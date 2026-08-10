# Military Medical Logistics Framework

A starting point for modeling, acquiring, and cleaning logistics data that supports military medical operations.

## Repository layout

- `docs/` - architecture and design notes
- `schema/` - SQL definitions for the logistics data model
- `scripts/` - data acquisition, cleaning, analysis, and visualization utilities
- `notebooks/` - exploratory analysis notebooks

## Getting started

1. Review `docs/architecture_notes.txt`.
2. Apply `schema/01_create_logistics_tables.sql` to a MySQL database.
3. Acquire a CSV with `python scripts/data_acquisition.py https://example.invalid/logistics.csv` and clean it with `python scripts/clean_data.py --input data/raw/logistics.csv --output data/processed/logistics_clean.csv`.

The acquisition script uses the Python standard library. The cleaning, statistical, and visualization modules use the packages listed in `requirements.txt`.

## Data Preparation & Normalization Pipeline (ANA 330)

The data preparation module, `scripts/clean_data.py`, processes raw telemetry and inventory feeds through an automated normalization pipeline:

- **Identifier Normalization:** Strips whitespace and formatting artifacts from 13-digit National Stock Numbers (NSNs).
- **Data Integrity and Imputation:** Handles missing or null stock levels and removes corrupted negative quantity entries.
- **Date Parsing and Shelf-Life Rules:** Standardizes heterogeneous date formats and calculates dynamic operational risk flags: `CRITICAL_EXPIRED`, `EXPIRING_SOON`, and `HEALTHY`.

The reusable `clean_operational_logistics_data()` function also returns `days_to_expiration` for downstream analysis.

Run the included ANA 330 mock-feed demonstration with:

```powershell
python scripts/clean_data.py --demo
```

## Applied Statistical Analysis (MTH 330)

The dedicated `scripts/statistical_analysis.py` module demonstrates applied quantitative analysis for medical supply logistics:

- **Hypothesis Testing:** One-sample t-testing evaluates daily medical supply burn rates against operational baseline targets at $\alpha = 0.05$.
- **Statistical Process Control (SPC):** 3-sigma upper and lower control limits detect supply surges and other anomalies.
- **Time-Series Forecasting:** Holt-Winters exponential smoothing projects seven-day future supply requirements.

Install the analysis dependencies and run the demonstration with:

```powershell
pip install -r requirements.txt
python scripts/statistical_analysis.py --mth330
streamlit run scripts/visualization_dashboard.py
```

The dashboard sidebar can also generate the ANA 230 executive command graphic with four panels: 30-day consumption, SPC anomaly bounds, category stock levels, and a seven-day demand projection. The PNG is saved to `docs/command_dashboard_sample.png`.

## Executive Command Dashboard (ANA 230)

The framework includes an automated visual telemetry engine in `scripts/visualization_dashboard.py`. It translates operational statistical anomalies, medical-category stock distribution, and seven-day predictive demand into an executive command dashboard.

## Project Visualization & Dashboard
![Mock Supply Stock Visualization](docs/mock_supply_stock.png)

## Dataset & Raw Logs
You can inspect the raw and cleaned data files used in this project:
- [View Raw Supply Data (CSV)](data/mock_supply_raw.csv)
- [View Cleaned Audit-Ready Data (CSV)](data/mock_supply_cleaned.csv)
