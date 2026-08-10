"""Summarize cleaned logistics quantities with descriptive statistics."""

from argparse import ArgumentParser
import csv
import json
from pathlib import Path
from statistics import mean, median, pstdev

REQUIRED_COLUMNS = {"facility_code", "item_code", "quantity_on_hand"}


def summarize(values: list[float]) -> dict[str, float | int]:
    """Return descriptive statistics for a non-empty sequence of quantities."""
    return {
        "count": len(values),
        "mean": mean(values),
        "median": median(values),
        "minimum": min(values),
        "maximum": max(values),
        "population_stddev": pstdev(values),
    }


def analyze(input_path: Path) -> dict:
    """Analyze quantity-on-hand values from a cleaned logistics CSV."""
    overall: list[float] = []
    by_facility: dict[str, list[float]] = {}
    by_item: dict[str, list[float]] = {}

    with input_path.open(newline="", encoding="utf-8-sig") as source:
        reader = csv.DictReader(source)
        columns = set(reader.fieldnames or [])
        missing = REQUIRED_COLUMNS - columns
        if missing:
            raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")

        for row_number, row in enumerate(reader, start=2):
            try:
                quantity = float(row["quantity_on_hand"])
            except (TypeError, ValueError) as error:
                raise ValueError(f"Invalid quantity on row {row_number}") from error

            facility = row["facility_code"].strip()
            item = row["item_code"].strip()
            overall.append(quantity)
            by_facility.setdefault(facility, []).append(quantity)
            by_item.setdefault(item, []).append(quantity)

    return {
        "source": str(input_path),
        "overall": summarize(overall) if overall else {},
        "by_facility": {key: summarize(values) for key, values in sorted(by_facility.items())},
        "by_item": {key: summarize(values) for key, values in sorted(by_item.items())},
    }


def run_mth330_statistical_module() -> dict:
    """Run MTH 330 hypothesis testing, SPC, and seven-day forecasting."""
    try:
        import numpy as np
        import pandas as pd
        import scipy.stats as stats
        from statsmodels.tsa.holtwinters import ExponentialSmoothing
    except ImportError as error:
        raise RuntimeError(
            "MTH 330 analysis requires pandas, numpy, scipy, and statsmodels"
        ) from error

    np.random.seed(42)
    dates = pd.date_range(start="2026-07-01", periods=30, freq="D")
    base_demand = 120 + np.sin(np.linspace(0, 4 * np.pi, 30)) * 15
    demand_data = base_demand + np.random.normal(loc=0, scale=5, size=30)
    demand_data[19] = 180
    df = pd.DataFrame({"date": dates, "daily_consumption": demand_data})

    consumption = df["daily_consumption"]
    mean_val = consumption.mean()
    std_val = consumption.std()
    shapiro_stat, shapiro_p = stats.shapiro(consumption)

    baseline_target = 115.0
    t_stat, p_val = stats.ttest_1samp(
        consumption, popmean=baseline_target, alternative="greater"
    )

    ucl = mean_val + (3 * std_val)
    lcl = max(0, mean_val - (3 * std_val))
    anomalies = df[df["daily_consumption"] > ucl]

    model = ExponentialSmoothing(consumption, trend="add", seasonal=None).fit()
    forecast = model.forecast(7)

    report = {
        "descriptive": {
            "mean": float(mean_val),
            "standard_deviation": float(std_val),
            "shapiro_w": float(shapiro_stat),
            "shapiro_p_value": float(shapiro_p),
        },
        "hypothesis_test": {
            "baseline_target": baseline_target,
            "t_statistic": float(t_stat),
            "p_value": float(p_val),
            "reject_null_at_005": bool(p_val < 0.05),
        },
        "spc": {
            "upper_control_limit": float(ucl),
            "lower_control_limit": float(lcl),
            "anomaly_count": len(anomalies),
            "anomaly_dates": anomalies["date"].dt.strftime("%Y-%m-%d").tolist(),
        },
        "seven_day_forecast": [float(value) for value in forecast],
    }

    print("--- MTH 330 Statistical Analysis ---")
    print(f"Mean Daily Consumption: {mean_val:.2f} units")
    print(f"Standard Deviation: {std_val:.2f}")
    print(f"Shapiro-Wilk: W={shapiro_stat:.4f}, p-value={shapiro_p:.4f}")
    print(f"One-sample t-test: t={t_stat:.4f}, p-value={p_val:.4f}")
    print(f"SPC limits: LCL={lcl:.2f}, UCL={ucl:.2f}")
    print(f"Detected anomalies: {len(anomalies)}")
    for index, value in enumerate(forecast, start=1):
        print(f"Day +{index} Forecasted Demand: {value:.2f} units")
    return report


def main() -> None:
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path)
    parser.add_argument("--output", type=Path, help="Optional JSON report path")
    parser.add_argument(
        "--mth330",
        action="store_true",
        help="Run hypothesis testing, SPC, and demand forecasting",
    )
    args = parser.parse_args()

    if args.mth330:
        report = run_mth330_statistical_module()
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
            print(f"Wrote statistical report to {args.output}")
        return

    if not args.input:
        parser.error("--input is required unless --mth330 is specified")
    report = analyze(args.input)
    rendered = json.dumps(report, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
        print(f"Wrote statistical report to {args.output}")
    else:
        print(rendered)


if __name__ == "__main__":
    main()
