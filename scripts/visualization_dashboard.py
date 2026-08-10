"""Streamlit dashboard for cleaned medical logistics inventory data."""

from pathlib import Path

import pandas as pd
import streamlit as st

DEFAULT_INPUT = Path("data/processed/logistics_clean.csv")
REQUIRED_COLUMNS = {"facility_code", "item_code", "quantity_on_hand"}
COMMAND_DASHBOARD_OUTPUT = Path("docs/command_dashboard_sample.png")

st.set_page_config(
    page_title="Medical Logistics Monitor",
    page_icon=":material/local_shipping:",
    layout="wide",
)


@st.cache_data(ttl="15m")
def load_data(input_path: str) -> pd.DataFrame:
    """Load and type the cleaned logistics CSV."""
    data = pd.read_csv(input_path)
    missing = REQUIRED_COLUMNS - set(data.columns)
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")
    data["quantity_on_hand"] = pd.to_numeric(data["quantity_on_hand"], errors="coerce")
    data = data.dropna(subset=["quantity_on_hand"]).copy()
    for column in ("facility_code", "item_code"):
        data[column] = data[column].astype(str).str.strip()
    return data


def generate_command_dashboard(output_path: Path = COMMAND_DASHBOARD_OUTPUT) -> Path:
    """Generate the ANA 230 executive command dashboard PNG."""
    try:
        import matplotlib.pyplot as plt
        import numpy as np
        import seaborn as sns
    except ImportError as error:
        raise RuntimeError(
            "Command dashboard generation requires matplotlib, numpy, and seaborn"
        ) from error

    sns.set_theme(style="darkgrid")
    figure, axes = plt.subplots(2, 2, figsize=(14, 10))
    figure.suptitle(
        "NIWC Medical Logistics Operational Command Dashboard (ANA 230)",
        fontsize=16,
        fontweight="bold",
    )

    np.random.seed(42)
    dates = pd.date_range(start="2026-07-01", periods=30, freq="D")
    demand = 120 + np.sin(np.linspace(0, 4 * np.pi, 30)) * 15
    demand += np.random.normal(0, 5, 30)
    demand[19] = 180
    trend_data = pd.DataFrame({"Date": dates, "Consumption": demand})

    axes[0, 0].plot(
        trend_data["Date"],
        trend_data["Consumption"],
        color="#1f77b4",
        linewidth=2,
        marker="o",
        markersize=4,
    )
    axes[0, 0].set_title("30-Day Daily Supply Consumption Trend", fontweight="bold")
    axes[0, 0].set_ylabel("Units Consumed")
    axes[0, 0].tick_params(axis="x", rotation=45)

    mean_value = trend_data["Consumption"].mean()
    upper_control_limit = mean_value + (3 * trend_data["Consumption"].std())
    axes[0, 1].plot(
        trend_data["Date"], trend_data["Consumption"], color="#2ca02c", label="Daily Burn"
    )
    axes[0, 1].axhline(
        upper_control_limit,
        color="red",
        linestyle="--",
        linewidth=1.5,
        label=f"Upper Control Limit (3-Sigma: {upper_control_limit:.1f})",
    )
    axes[0, 1].axhline(
        mean_value,
        color="black",
        linestyle=":",
        label=f"Mean ({mean_value:.1f})",
    )
    axes[0, 1].scatter(
        trend_data["Date"].iloc[19],
        trend_data["Consumption"].iloc[19],
        color="red",
        s=100,
        zorder=5,
        label="Surge Anomaly Detected",
    )
    axes[0, 1].set_title("Operational Anomaly Detection (SPC Bounds)", fontweight="bold")
    axes[0, 1].legend(loc="upper left", fontsize=8)
    axes[0, 1].tick_params(axis="x", rotation=45)

    categories = [
        "Pharmaceuticals",
        "Surgical Gear",
        "Blood Products",
        "PPE/Sanitation",
        "Trauma Kits",
    ]
    stock_levels = [450, 280, 120, 890, 310]
    axes[1, 0].barh(
        categories,
        stock_levels,
        color=["#1f77b4", "#aec7e8", "#ff7f0e", "#2ca02c", "#d62728"],
    )
    axes[1, 0].set_title("Current Stock Levels by Item Category", fontweight="bold")
    axes[1, 0].set_xlabel("Quantity on Hand")

    forecast_days = [f"Day +{index}" for index in range(1, 8)]
    forecast_values = [125, 128, 131, 130, 127, 124, 122]
    safety_stock = 115
    axes[1, 1].plot(
        forecast_days,
        forecast_values,
        color="#9467bd",
        marker="s",
        linewidth=2,
        label="Forecast Demand",
    )
    axes[1, 1].axhline(
        safety_stock,
        color="orange",
        linestyle="--",
        label="Safety Baseline Threshold",
    )
    axes[1, 1].set_title("7-Day Predictive Consumption Forecast", fontweight="bold")
    axes[1, 1].set_ylabel("Projected Units")
    axes[1, 1].legend(loc="lower left", fontsize=8)

    figure.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output_path, dpi=300)
    plt.close(figure)
    return output_path


def render_dashboard(data: pd.DataFrame, source: str) -> None:
    """Render the filtered inventory dashboard."""
    st.title("Medical logistics monitor")
    st.caption(f"Source: {source}")

    with st.sidebar:
        st.header("Filters")
        facilities = st.multiselect(
            "Facilities",
            options=sorted(data["facility_code"].unique()),
            default=sorted(data["facility_code"].unique()),
        )
        items = st.multiselect(
            "Supply items",
            options=sorted(data["item_code"].unique()),
            default=sorted(data["item_code"].unique()),
        )
        if st.button("Generate command dashboard"):
            try:
                output_path = generate_command_dashboard()
                st.success(f"Saved {output_path}")
            except RuntimeError as error:
                st.error(str(error))

    filtered = data[
        data["facility_code"].isin(facilities) & data["item_code"].isin(items)
    ]

    with st.container(horizontal=True):
        st.metric("Records", f"{len(filtered):,}", border=True)
        st.metric("Quantity on hand", f"{filtered['quantity_on_hand'].sum():,.0f}", border=True)
        st.metric("Facilities", f"{filtered['facility_code'].nunique():,}", border=True)
        st.metric("Supply items", f"{filtered['item_code'].nunique():,}", border=True)

    if filtered.empty:
        st.warning("No records match the selected filters.")
        return

    facility_totals = (
        filtered.groupby("facility_code", as_index=False)["quantity_on_hand"]
        .sum()
        .sort_values("quantity_on_hand", ascending=False)
    )
    item_totals = (
        filtered.groupby("item_code", as_index=False)["quantity_on_hand"]
        .sum()
        .sort_values("quantity_on_hand", ascending=False)
    )

    chart_left, chart_right = st.columns(2)
    with chart_left:
        with st.container(border=True):
            st.subheader("Quantity by facility")
            st.bar_chart(facility_totals, x="facility_code", y="quantity_on_hand")
    with chart_right:
        with st.container(border=True):
            st.subheader("Quantity by supply item")
            st.bar_chart(item_totals, x="item_code", y="quantity_on_hand")

    with st.container(border=True):
        st.subheader("Filtered inventory records")
        st.dataframe(filtered, hide_index=True, width="stretch")


def main() -> None:
    with st.sidebar:
        input_path = st.text_input("CSV path", value=str(DEFAULT_INPUT))

    path = Path(input_path)
    if not path.exists():
        st.title("Medical logistics monitor")
        st.info(f"Add a cleaned CSV at `{path}` or enter another path in the sidebar.")
        st.code(
            "python scripts/clean_data.py "
            "--input data/raw/logistics.csv "
            "--output data/processed/logistics_clean.csv"
        )
        return

    try:
        data = load_data(str(path))
    except (OSError, ValueError, pd.errors.ParserError) as error:
        st.error(f"Could not load logistics data: {error}")
        return

    render_dashboard(data, str(path))


if __name__ == "__main__":
    main()
