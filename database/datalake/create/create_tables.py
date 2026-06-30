from database.db import db
from listings.guland import GulandListing
from listings.homedy import HomedyListing
from listings.thuviennhadat import ThuvienListing
from listings.base_listing import BaseListing

def create_tables():
    with db:
        db.create_tables(
            [
                GulandListing,
                HomedyListing,
                BaseListing,
                ThuvienListing
            ],
            safe=True
        )

if __name__ == "__main__":
    create_tables()
