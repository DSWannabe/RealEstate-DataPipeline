from peewee import PostgresqlDatabase

db = PostgresqlDatabase(
    "bds_datalake",
    user="postgres",
    password="B@dmeetsevil1999xx",
    host="172.20.238.231",
    port=5432
)
