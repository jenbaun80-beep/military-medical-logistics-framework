"""Clean a logistics CSV while preserving the source file."""

from argparse import ArgumentParser
from pathlib import Path
import csv

REQUIRED_COLUMNS = {"source_record_id", "facility_code", "item_code", "quantity_on_hand", "snapshot_at"}


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
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(f"Wrote {clean(args.input, args.output)} records to {args.output}")


if __name__ == "__main__":
    main()
