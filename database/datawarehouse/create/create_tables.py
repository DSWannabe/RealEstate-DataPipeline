from database.datawarehouse.create.db import db
from datawarehouse.create import dim_address
from datawarehouse.create import dim_date
from datawarehouse.create import dim_property
from datawarehouse.create import dim_direction
from datawarehouse.create import dim_legality
from datawarehouse.create import fact

def create_tables():
    with db:
        db.create_tables(
            [
                dim_property,
                dim_address,
                dim_direction,
                dim_date,
                dim_legality,
                fact
            ],
            safe=True
        )

if __name__ == "__main__":
    create_tables()
