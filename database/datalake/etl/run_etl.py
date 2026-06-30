from schema import db, Homedy, Guland, Thuviennhadat
from services.guland_service import GulandImportService
from services.homedy_service import HomedyImportService
from services.thuvien_service import ThuviennhadatImportService

def main():
    db.connect()
    db.create_tables([Homedy, Guland, Thuviennhadat], safe=True)

    # Read raw Jsonl
    GulandImportService.read_jsonl(
        "/home/anhtupham99/BDS-project/data/raw/detailed_guland.jsonl"
    )
    HomedyImportService.read_jsonl(
        "/home/anhtupham99/BDS-project/data/raw/detailed_homedy.jsonl"
    )
    ThuviennhadatImportService.read_jsonl(
        "/home/anhtupham99/BDS-project/data/raw/detailed_thuviennhadat.jsonl"
    )

    db.close()

if __name__ == "__main__":
    main()
