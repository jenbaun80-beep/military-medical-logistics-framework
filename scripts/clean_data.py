"""Clean a logistics CSV while preserving the source file."""

from argparse import ArgumentParser
from pathlib import Path
import csv

import numpy as np
import pandas as pd

REQUIRED_COLUMNS = {"source_record_id", "facility_code", "item_code", "quantity_on_hand", "snapshot_at"}
OPERATIONAL_COLUMNS = {"item_nsn", "category", "quantity_on_hand", "expiration_date"}


def clean_operational_logistics_data(raw_df: pd.DataFrame) -> pd.DataFrame:
    """Normalize and validate a raw operational logistics DataFrame."""
    missing = OPERATIONAL_COLUMNS - set(raw_df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")

    data = raw_df.copy()
    data["item_nsn"] = data["item_nsn"].astype(str).str.strip().str.replace("-", "", regex=False)
    data["quantity_on_hand"] = pd.to_numeric(
        data["quantity_on_hand"], errors="coerce"
    ).fillna(0)
    data = data[data["quantity_on_hand"] >= 0].copy()
    data["expiration_date"] = pd.to_datetime(data["expiration_date"], errors="coerce")
    data["category"] = data["category"].astype(str).str.title().str.strip()

    today = pd.Timestamp.now()
    data["days_to_expiration"] = (data["expiration_date"] - today).dt.days
    data["shelf_life_alert"] = data["days_to_expiration"].apply(
        lambda days: (
            "CRITICAL_EXPIRED"
            if days < 0
            else "EXPIRING_SOON"
            if days <= 90
            else "HEALTHY"
        )
    )
    return data


def run_demo() -> None:
    """Run the ANA 330 example against a deliberately messy feed."""
    raw_logistics_feed = pd.DataFrame(
        {
            "item_nsn": [
                " 6505-01-123-4567 ",
                "6505019876543",
                "6505-01-000-1111 ",
                "UNKNOWN",
            ],
            "category": [" PHARMACEUTICALS ", "surgical gear", " blood products ", "ppe"],
            "quantity_on_hand": [150, -10, np.nan, 500],
            "expiration_date": [
                "2026-09-01",
                "2027-12-31",
                "invalid_date_entry",
                "2026-05-15",
            ],
        }
    )

    print("--- RAW UNCLEANED LOGISTICS FEED ---")
    print(raw_logistics_feed)
    print("\n--- CLEANED & NORMALIZED DATASET (ANA 330) ---")
    cleaned_data = clean_operational_logistics_data(raw_logistics_feed)
    print(
        cleaned_data[
            [
                "item_nsn",
                "category",
                "quantity_on_hand",
                "expiration_date",
                "shelf_life_alert",
            ]
        ]
    )


def clean(input_path: Path, output_path: Path) -> int:
    with input_path.open(newline="", encoding="utf-8-sig") as source:
        reader = csv.DictReader(source)
        columns = set(reader.fieldnames or [])
        missing = REQUIRED_COLUMNS - columns
        if missing:
            raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", newline="", encoding="utf-8") as destination:
            writer = csv.DictWriter(destination, fieldnames=reader.fieldnames)
            writer.writeheader()
            written = 0
            for row in reader:
                row = {key: value.strip() for key, value in row.items()}
                if not row["source_record_id"] or not row["facility_code"] or not row["item_code"]:
                    continue
                row["quantity_on_hand"] = str(float(row["quantity_on_hand"]))
                writer.writerow(row)
                written += 1
    return written


def main() -> None:
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--demo", action="store_true", help="Run the ANA 330 example feed")
    args = parser.parse_args()

    if args.demo:
        run_demo()
        return
    if not args.input or not args.output:
        parser.error("--input and --output are required unless --demo is specified")
    print(f"Wrote {clean(args.input, args.output)} records to {args.output}")


if __name__ == "__main__":
    main()
