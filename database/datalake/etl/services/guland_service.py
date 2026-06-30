import json
from itertools import islice
from tqdm import tqdm
from schema import db, Guland


class GulandImportService:
    @staticmethod
    def read_jsonl(file_path: str, batch_size=1000):
        with open(file_path, "r", encoding="utf-8") as f:
            while True:
                lines = list(islice(f, batch_size))
                if not lines:
                    break

                rows = [json.loads(line) for line in lines]

                with db.atomic():
                    (
                        Guland
                        .insert_many(rows)
                        .on_conflict_ignore()   # Skip duplicate post_id if unique
                        .execute()
                    )