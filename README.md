# Military Medical Logistics Framework

A starting point for modeling, acquiring, and cleaning logistics data that supports military medical operations.

## Repository layout

- `docs/` - architecture and design notes
- `schema/` - SQL definitions for the logistics data model
- `scripts/` - data acquisition and cleaning utilities
- `notebooks/` - exploratory analysis notebooks

## Getting started

1. Review `docs/architecture_notes.txt`.
2. Apply `schema/01_create_logistics_tables.sql` to a PostgreSQL database.
3. Acquire a CSV with `python scripts/data_acquisition.py https://example.invalid/logistics.csv` and clean it with `python scripts/clean_data.py --input data/raw/logistics.csv --output data/processed/logistics_clean.csv`.

The scripts use standard-library Python only. They expect CSV input and preserve the source data by writing cleaned output to a separate path.
