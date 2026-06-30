import pandas as pd
import numpy as np
import datetime as dt
import re
from tqdm import tqdm
# from ollama import chat
import json
import yaml
from functools import lru_cache

from config import OPENAI_API_KEY
from openai import OpenAI

client = OpenAI(api_key=OPENAI_API_KEY)

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

    def price_unit_separation(self, df):
        if "price" in df.columns:
        # The expand=True argument turns the list of split values into separate columns.
            split_cols = df["price"].astype(str).str.split(n=1, expand=True)

            if split_cols.shape[1] == 2:
                df["price_value"] = split_cols[0]
                df["price_unit"] = split_cols[1]
            elif split_cols.shape[1] == 1:
                df["price_value"] = split_cols[0]
                df["price_unit"] = "N/A"

        df["price_value"] = pd.to_numeric(df["price_value"], errors="coerce")

        # Convert based on unit
        df['price_unit'] = df['price_unit'].str.lower()
        df.loc[df["price_unit"] == "tỷ", "price_value"] *= 1_000_000_000
        df.loc[df["price_unit"] == "triệu", "price_value"] *= 1_000_000

        return df

    def size_separation(self, df):
        if "size" in df.columns:
            df["size"] = (
                            df["size"]
                            .astype(str)
                            .str.replace(r"[\r\n\t]+", " ", regex=True)  # clean up line breaks
                            .str.replace(r"(\d)(?=[a-zA-Zm²M²])", r"\1 ", regex=True)  # ensure space before unit
                            .str.replace(r"\s+", " ", regex=True)
                            .str.strip()
                        )
            split_cols = df["size"].str.split(n=1, expand=True)

            if split_cols.shape[1] == 2:
                df["size_value"] = split_cols[0]
                df["size_unit"] = split_cols[1]
            elif split_cols.shape[1] == 1:
                df["size_value"] = split_cols[0]
                df["size_unit"] = "N/A"

        df["size_value"] = pd.to_numeric(df["size_value"], errors="coerce")

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

        # Lowercase all district names for comparison
        lower_districts = [d.lower() for d in districts]

        # Prepare a new column for results
        df["district"] = "N/A"

        # Loop through rows with tqdm progress bar
        pattern = "|".join(map(re.escape, [d.lower() for d in districts]))

        df["district"] = (
            df["address"]
            .astype(str)
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
                r'(\d+)\s*(pn|phòng ngủ|phòng ngu|phòng n\.gủ|phong ngu)',
            ],
            "bathroom": [
                r'(\d+)\s*(wc|toilet|phòng tắm|Phòng Tắm|phong tam)',
            ],
            "floor": [
                r'(\d+)\s*(tầng|lầu|Tầng|Lầu)',
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
        response = client.chat.completions.create(
            model="gpt-4o-mini",   # CHEAP & GOOD
            messages=[
                {"role": "system", "content": "You extract structured data and return JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0,
            max_tokens=200
        )

        return response.choices[0].message.content.strip()

    def _build_batch_prompt(self, descriptions, feature):
        return f"""
Extract number of {feature}s from Vietnamese real estate descriptions.

Aliases:
- bedroom: PN, phòng ngủ
- bathroom: WC, toilet, phòng tắm
- floor: tầng, lầu

Rules:
- Return only integers
- Missing = 0
- Output JSON: {{"0": n0, "1": n1, ...}}

Return JSON only.

Texts:
""" + "\n".join(
            f"[{i}] {desc}" for i, desc in enumerate(descriptions)
        )

    def _parse_llm_json(self, text, batch_size):
        try:
            match = re.search(r'\{.*\}', text, re.S)
            if not match:
                return [0] * batch_size

            data = json.loads(match.group())
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
        need_llm = df[feature].isna()
        df_llm = df[need_llm].copy()
        if df_llm.empty:
            df[feature] = df[feature].replace(["N/A", "n/a", "", None], np.nan).fillna(0).astype(int)
            return df

        # STEP 3: BATCH LLM (only if needed)
        if not df_llm.empty:
            results = {}

            for i in tqdm(
                range(0, len(df_llm), self.batch_size),
                desc=f"LLM extracting {feature}"
            ):
                batch = df_llm.iloc[i:i + self.batch_size]
                descriptions = batch["description"].tolist()
                indices = batch.index.tolist()

                values = self._llm_batch_extract(descriptions, feature)

                for idx, val in zip(indices, values):
                    results[idx] = val

            for idx, val in results.items():
                df.at[idx, feature] = val

        # STEP 4: FINAL NORMALIZATION (ONLY HERE)
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
        for i, row in df.iterrows():
            text = str(row['time_detail']).lower()
            scraped_on = row['scraped_on']
            num = row['number']

            if pd.isna(num) or pd.isna(scraped_on):
                continue

            if "ngày" in text:
                df.at[i, 'time_detailed_num'] = scraped_on - pd.Timedelta(days=num)
            elif "tuần" in text:
                df.at[i, 'time_detailed_num'] = scraped_on - pd.Timedelta(weeks=num)
            elif "tháng" in text:
                df.at[i, 'time_detailed_num'] = scraped_on - pd.Timedelta(days=num * 30)
            elif "năm" in text:
                df.at[i, 'time_detailed_num'] = scraped_on - pd.Timedelta(days=num * 365)
            # For giây/phút/giờ → same as scraped_on (already set)

        return df

    def modify_columns(self, df):
        if all(col in df.columns for col in ["price_value", "price_unit"]):
            df = df.drop(columns=["price"])

        if "time_detailed_num" in df.columns:  # ← typo fixed: “tine” → “time”
            df = df.drop(columns=["time_detail", "number"])

        df = df.drop(columns=[
            'bedroom_fast', 'bathroom_fast', 'floor_fast',
            'legality', 'direction', 'width', 'length'
        ], errors="ignore")

        df['website'] = 'Guland'

        return df

if __name__ == "__main__":
    input_file = "/home/anhtupham99/BDS-project/data/raw/detailed_guland.jsonl"
    output_file = "/home/anhtupham99/BDS-project/data/json_to_csv/detailed_guland_processed_1.csv"
    yml_district = "/home/anhtupham99/BDS-project/bds_crawling/locations.yml"

    extractor = DataPreprocessor(model="Mistral")
    df = extractor.load_data_jsonl(input_file)
    df = extractor.price_unit_separation(df)
    df = extractor.size_separation(df)
    df = extractor.extract_district_from_address(df, yml_district)
    df = extractor.extract_feature_numeric(df, "bedroom") # Use LLM
    df = extractor.extract_feature_numeric(df, "bathroom") # Use LLM
    df = extractor.extract_feature_numeric(df, "floor")    # Use LLM
    df = extractor.extract_time_detailed_num(df)
    df = extractor.modify_columns(df)
    extractor.save_data(df, output_file)