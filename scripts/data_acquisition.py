"""Acquire and validate medical logistics telemetry and source files."""

from argparse import ArgumentParser
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen

logging.basicConfig(
    filename="data_ingestion.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] Governance Audit: %(message)s",
)


def ingest_supply_telemetry(payload_json: str) -> dict:
    """Validate a telemetry payload before downstream ETL storage."""
    try:
        data = json.loads(payload_json)
        required_keys = ["unit_id", "item_nsn", "quantity", "timestamp"]
        for key in required_keys:
            if key not in data:
                raise ValueError(f"Missing mandatory telemetry field: {key}")

        logging.info(
            "Successfully ingested telemetry from Unit %s for NSN %s",
            data["unit_id"],
            data["item_nsn"],
        )
        return {"status": "SUCCESS", "record": data}
    except (TypeError, ValueError, json.JSONDecodeError) as error:
        logging.error("Ingestion payload rejected: %s", error)
        return {"status": "REJECTED", "error": str(error)}


def acquire(url: str, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with urlopen(url, timeout=30) as response:
        output.write_bytes(response.read())


def main() -> None:
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("url", nargs="?", help="HTTP(S) URL for the source CSV")
    parser.add_argument("--output", type=Path, default=Path("data/raw/logistics.csv"))
    args = parser.parse_args()

    if not args.url:
        parser.error("a source URL is required")
    acquire(args.url, args.output)
    print(f"Wrote {args.output}")


def run_sample() -> None:
    """Run the sample telemetry payload from the project brief."""
    sample_payload = json.dumps(
        {
            "unit_id": "MED-REQ-03",
            "item_nsn": "6505011234567",
            "quantity": 150,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    )
    response = ingest_supply_telemetry(sample_payload)
    print("Ingestion Result:", response)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        run_sample()
    else:
        main()
