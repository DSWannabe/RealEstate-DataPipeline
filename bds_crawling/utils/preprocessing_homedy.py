import pandas as pd
import numpy as np
import datetime as dt
import re
from tqdm import tqdm
from ollama import chat
import json
import yaml
from functools import lru_cache

class DataPreprocessor:

    def __init__(self, model="Mistral", batch_size=10):
        self.model = model
        self.batch_size = batch_size

    def load_data_csv(self, input_file):
        df = pd.read_csv(input_file)
        return df

    def load_data_jsonl(self, input_file):
        df = pd.read_json(input_file, lines=True)
        return df

    def save_data(self, df, output_file):
        df.to_csv(output_file, index=False, encoding="utf-8")
        print(f"✅ File saved to: {output_file}")

    def price_preprocessing(self, df):
        # ensure price column exists and is string for regex ops
        if "price" not in df.columns:
            df["price"] = np.nan

        price_str = df["price"].astype(str)

        # detect price ranges like "1,4 - 1,6"
        price_range_pattern = r"\d+(?:,\d+)?\s*-\s*\d+(?:,\d+)?"
        mask_range = price_str.str.contains(price_range_pattern, na=False)

        # extract & average ranges
        nums = (
            price_str[mask_range]
            .str.findall(r"\d+(?:,\d+)?")
            .apply(lambda x: [float(n.replace(",", ".")) for n in x])
        )

        df.loc[mask_range, "price"] = nums.apply(
            lambda x: np.mean(x) if len(x) == 2 else np.nan
        )

        # handle single prices (e.g. "1,5")
        mask_single = price_str.str.match(r"^\d+,\d+$", na=False)
        df.loc[mask_single, "price"] = (
            price_str[mask_single]
            .str.replace(",", ".", regex=False)
            .astype(float)
        )

        # convert to numeric (final safety net)
        df["price"] = pd.to_numeric(df["price"], errors="coerce")

        # scale by unit
        df.loc[df["price_unit"] == "Tỷ", "price"] *= 1000000000
        df.loc[df["price_unit"] == "Triệu", "price"] *= 1000000

        return df


    """ Address preprocessing start """
    def load_districts(self, yaml_file):
        with open(yaml_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        # Your YAML format: TPHCM -> Quan_huyen -> [ "Quận 1", "Quận 2", ... ]
        districts = data.get("TPHCM", {}).get("Quan_huyen", [])
        return districts

    def extract_district_from_address(self, df, yaml_file):
        # Load district list from YAML
        districts = self.load_districts(yaml_file)

        # Prepare a new column for results
        df["district"] = "N/A"

        # Loop through rows with tqdm progress bar
        pattern = "|".join(re.escape(d.lower()) for d in districts)

        df["district"] = (
            df["address"]
            .str.lower()
            .str.extract(f"({pattern})", expand=False)
            .fillna("N/A")
        )
        return df
    """ Address preprocessing end """

    def fast_extract_numeric(self, text, feature):
        """
        Try regex-based extraction first.
        Returns int or None.
        """
        if not isinstance(text, str):
            return None

        text = text.lower()

        patterns = {
            "bedroom": [
                r'(\d+)\s*(pn|phòng ngủ|phòng ngu|phòng n\.gủ)',
            ],
            "bathroom": [
                r'(\d+)\s*(wc|toilet|phòng tắm)',
            ],
            "floor": [
                r'(\d+)\s*(tầng|lầu)',
            ]
        }

        for pattern in patterns.get(feature, []):
            m = re.search(pattern, text)
            if m:
                return int(m.group(1))

        return None

    # ===================== LLM CORE =====================
    @lru_cache(maxsize=50000)
    def _llm_cached(self, prompt):
        response = chat(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response["message"]["content"].strip()

    def _build_batch_prompt(self, descriptions, feature):
        return f"""
Extract number of {feature}s from Vietnamese real estate descriptions.

Aliases:
- bedroom: PN, phòng ngủ
- bathroom: WC, toilet, phòng tắm
- floor: tầng, lầu

Rules:
- Return only integers
- If missing, return 0

Return JSON only.

Descriptions:
""" + "\n".join(
            f"[{i}] {desc}" for i, desc in enumerate(descriptions)
        )

    def _parse_llm_json(self, text, batch_size):
        try:
            text = text.strip()
            text = re.search(r'\{.*\}', text, re.S)
            data = json.loads(text)
            return [int(data.get(str(i), 0)) for i in range(batch_size)]
        except Exception:
            return [0] * batch_size

    def _llm_batch_extract(self, descriptions, feature):
        prompt = self._build_batch_prompt(descriptions, feature)
        raw = self._llm_cached(prompt)
        return self._parse_llm_json(raw, len(descriptions))

    # ===================== MAIN FEATURE EXTRACTION =====================
    def extract_feature_numeric(self, df, feature):
        if feature not in df.columns:
            df[feature] = np.nan

        # STEP 1: FAST RULE-BASED
        df[f"{feature}_fast"] = df["description"].apply(
            lambda x: self.fast_extract_numeric(x, feature)
        )

        df.loc[df[feature].isna(), feature] = df[f"{feature}_fast"]

        # STEP 2: FIND ROWS NEEDING LLM
        # need_llm = df[feature].isna()
        # df_llm = df[need_llm].copy()

        # STEP 3: BATCH LLM (only if needed)
        # if not df_llm.empty:
        #     results = {}

        #     for i in tqdm(
        #         range(0, len(df_llm), self.batch_size),
        #         desc=f"LLM extracting {feature}"
        #     ):
        #         batch = df_llm.iloc[i:i + self.batch_size]
        #         descriptions = batch["description"].tolist()
        #         indices = batch.index.tolist()

        #         values = self._llm_batch_extract(descriptions, feature)

        #         for idx, val in zip(indices, values):
        #             results[idx] = val

        #     for idx, val in results.items():
        #         df.at[idx, feature] = val

        # STEP 4: FINAL NORMALIZATION
        df[feature] = (
            df[feature]
            .replace(["N/A", "n/a", "", None], np.nan)
            .fillna(0)
            .astype(int)
        )

        df = df.drop(columns=[f"{feature}_fast"])

        return df

    def extract_time_detailed_num(self, df):
        # Ensure 'scraped_on' is a datetime column
        df['scraped_on'] = pd.to_datetime(df['scraped_on'], errors='coerce')

        # Extract number from 'time_detail' (e.g., "3 ngày trước" → 3)
        df['number'] = df['time_detail'].str.extract(r'(\d+)').astype(float)

        # Default = scraped_on (for "giây", "phút", "giờ")
        df['time_detailed_num'] = df['scraped_on']

        # Apply time adjustments
        mask = df['time_detail'].str.contains("ngày", case=False, na=False)
        df.loc[mask, 'time_detailed_num'] -= pd.to_timedelta(df.loc[mask, 'number'], unit='D')

        mask = df['time_detail'].str.contains("tuần", case=False, na=False)
        df.loc[mask, 'time_detailed_num'] -= pd.to_timedelta(df.loc[mask, 'number'] * 7, unit='D')

        mask = df['time_detail'].str.contains("tháng", case=False, na=False)
        df.loc[mask, 'time_detailed_num'] -= pd.to_timedelta(df.loc[mask, 'number'] * 30, unit='D')

        mask = df['time_detail'].str.contains("năm", case=False, na=False)
        df.loc[mask, 'time_detailed_num'] -= pd.to_timedelta(df.loc[mask, 'number'] * 365, unit='D')

        return df

    def modify_columns(self, df):
        if all(col in df.columns for col in ["price_value", "price_unit"]):
            df = df.drop(columns=["price"])

        if "time_detailed_num" in df.columns:  # ← typo fixed: “tine” → “time”
            df = df.drop(columns=["time_detail", "number"])

        cols_to_drop = [
            'bedroom_fast', 'bathroom_fast', 'floor_fast',
            'legality', 'direction'
        ]

        df = df.drop(columns=[c for c in cols_to_drop if c in df.columns])

        df['website'] = 'Homedy'

        return df


if __name__ == "__main__":
    input_file = "/home/anhtupham99/BDS-project/data/raw/detailed_homedy.jsonl"
    output_file = "/home/anhtupham99/BDS-project/data/json_to_csv/detailed_homedy_processed_1.csv"
    yml_district = "/home/anhtupham99/BDS-project/bds_crawling/locations.yml"

    extractor = DataPreprocessor(model="Mistral")
    df = extractor.load_data_jsonl(input_file)
    df = extractor.price_preprocessing(df)
    df = extractor.extract_district_from_address(df, yml_district)
    df = extractor.extract_feature_numeric(df, "bedroom") # Use LLM
    df = extractor.extract_feature_numeric(df, "bathroom") # Use LLM
    df = extractor.extract_feature_numeric(df, "floor")    # Use LLM
    df = extractor.extract_time_detailed_num(df)
    df = extractor.modify_columns(df)
    extractor.save_data(df, output_file)