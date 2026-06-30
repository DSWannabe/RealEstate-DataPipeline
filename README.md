# RealEstate-DataPipeline (RE-Project)

An end-to-end data engineering pipeline that scrapes Vietnamese real estate listings, lands them in a PostgreSQL data lake, and transforms them into a star-schema data warehouse for downstream price prediction modeling.

## Overview

This project automates the full lifecycle of real estate data — from raw web scraping to an analytics-ready warehouse:

1. **Scrape** listings from Guland, Homedy, and Thuviennhadat using Scrapy, BeautifulSoup, and Playwright
2. **Land** raw JSON/JSONL data into a PostgreSQL data lake via Peewee ORM
3. **Transform** raw listings into a clean, normalized star schema
4. **Load** into a data warehouse (`fact_listing` + dimension tables) ready for analysis or ML feature engineering

Built as a personal project to practice real-world data engineering: multi-source scraping, schema design, ETL, and pipeline structure.

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌────────────────┐     ┌──────────────────┐
│   Scrapers   │ --> │  Data Lake   │ --> │  ETL / Clean   │ --> │  Data Warehouse   │
│  (Scrapy/    │     │ (PostgreSQL  │     │  & Transform   │     │  (Star Schema)    │
│  Playwright) │     │  via Peewee) │     │                │     │                   │
└─────────────┘     └──────────────┘     └────────────────┘     └──────────────────┘
   Guland,              raw listing           text norm,           fact_listing +
   Homedy,               JSON tables           field mapping,       dim_address,
   Thuviennhadat                               dedup                dim_date,
                                                                     dim_direction,
                                                                     dim_legality,
                                                                     dim_property_type
```

## Tech Stack

- **Scraping:** Scrapy, BeautifulSoup, Playwright
- **Storage:** PostgreSQL
- **ORM:** Peewee
- **Language:** Python 3.11

## Project Structure

```
bds_crawling/              # Scrapy project: spiders + scraping utilities
├── spiders/                 # One spider per source site (Guland, Homedy, Thuviennhadat)
├── utils/                   # Preprocessing & JSON-to-CSV conversion helpers
├── items.py, pipelines.py, settings.py

database/
├── datalake/
│   ├── create/               # Data lake table definitions (raw listing tables)
│   └── etl/                  # ETL logic: services per source, schema, normalization
└── datawarehouse/
    └── create/                # Star schema: fact_listing + dimension tables

requirements.txt
scrapy.cfg
```

## Data Model

The warehouse uses a star schema centered on `fact_listing`, with the following dimensions:

- `dim_address` — location hierarchy (city/district/ward)
- `dim_date` — listing date breakdown
- `dim_direction` — house-facing direction
- `dim_legality` — legal status (pink book / red book / etc.)
- `dim_property_type` — property category (apartment, house, land, etc.)

[Optional: embed an ER diagram image here, e.g. `![Schema](docs/schema.png)`]

## Setup

```bash
# Clone the repo
git clone https://github.com/DSWannabe/RealEstate-DataPipeline.git
cd RealEstate-DataPipeline

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp bds_crawling/utils/.env.example bds_crawling/utils/.env
# then fill in your PostgreSQL credentials and any API keys
```

## Usage

```bash
# Run a spider (example: Guland)
scrapy crawl guland

# Run ETL to transform raw data into the warehouse
python database/datalake/etl/run_etl.py
```

[Adjust the above commands to match your actual entry points/CLI.]

## Status / Roadmap

- [x] Scraping pipeline for Guland, Homedy, Thuviennhadat
- [x] Data lake ingestion (raw listing tables)
- [x] ETL transform & normalization logic
- [ ] Warehouse load step (`load.py`) — in progress
- [ ] Price prediction model on top of warehouse data

## Notes

This is an active learning project — feedback and suggestions welcome.
