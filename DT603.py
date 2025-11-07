#!/usr/bin/env python3
"""
Accreditation Expiry Projection & Simple Predictive Analysis

Requirements:
    pip install pandas matplotlib numpy openpyxl
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime


INPUT_PATH = Path("data (6).xlsx") 
SHEET_NAME = "Export"

DATE_COL = "Accreditation expiry date"
TITLE_COL = "Accreditation title"
STATUS_COL = "Accreditation status"

MONTHS_AHEAD = 18  #projection

OUTPUT_DIR = Path("accreditation_outputs")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def main():
    #Load data
    df = pd.read_excel(INPUT_PATH, sheet_name=SHEET_NAME)
    df.columns = [str(c).strip() for c in df.columns]

    # Parse expiry date
    df[DATE_COL] = pd.to_datetime(df[DATE_COL], errors="coerce")
    df = df[~df[DATE_COL].isna()].copy()   # Keep valid dates only

    # add expiry month
    df["expiry_month"] = df[DATE_COL].dt.to_period("M")

    today = pd.Timestamp(datetime.today().date())
    future_months = pd.period_range(
        start=today.to_period("M"),
        end=(today + pd.DateOffset(months=MONTHS_AHEAD - 1)).to_period("M"),
        freq="M"
    )

    # count expiries per month
    monthly_counts = (
        df.groupby("expiry_month")
          .size()
          .reindex(future_months, fill_value=0)
          .rename("expiring_count")
          .to_frame()
    )

    monthly_counts.to_csv(OUTPUT_DIR / "monthly_expiring_totals.csv", index=True)

    # Breakdown by skill (accreditation) title
    monthly_by_title = (
        df.groupby(["expiry_month", TITLE_COL])
          .size()
          .unstack(TITLE_COL)
          .reindex(future_months, fill_value=0)
          .fillna(0)
    )

    monthly_by_title.to_csv(OUTPUT_DIR / "monthly_expiring_by_title.csv")

    # Identify PPST variations
    ppst_cols = [c for c in monthly_by_title.columns if "ppst" in str(c).lower()]

    if ppst_cols:
        ppst_monthly = monthly_by_title[ppst_cols].sum(axis=1).rename("PPST_expiring_count")
        ppst_monthly.to_csv(OUTPUT_DIR / "ppst_monthly_expiring.csv")
    else:
        ppst_monthly = None

    # visual 1 — Overall monthly expiries
    plt.figure()
    monthly_counts["expiring_count"].plot(kind="bar")
    plt.title(f"Accreditations Expiring per Month (Next {MONTHS_AHEAD} Months)")
    plt.xlabel("Month")
    plt.ylabel("Count")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "monthly_expiring_totals.png")
    plt.close()

    # visual 2 — PPST only
    if ppst_monthly is not None:
        plt.figure()
        ppst_monthly.plot(kind="bar")
        plt.title(f"PPST Accreditations Expiring per Month (Next {MONTHS_AHEAD} Months)")
        plt.xlabel("Month")
        plt.ylabel("Count")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.savefig(OUTPUT_DIR / "ppst_monthly_expiring.png")
        plt.close()

    # visual 3 — Top 5 skill by expiries
    top_titles = df[df["expiry_month"].isin(future_months)][TITLE_COL].value_counts().head(5).index.tolist()

    if top_titles:
        plt.figure()
        monthly_by_title[top_titles].plot(kind="bar")
        plt.title(f"Top 5 Accreditation Titles by Expiring Count (Next {MONTHS_AHEAD} Months)")
        plt.xlabel("Month")
        plt.ylabel("Count")
        plt.xticks(rotation=45, ha="right")
        plt.legend(title="Accreditation title")
        plt.tight_layout()
        plt.savefig(OUTPUT_DIR / "top_titles_monthly_expiring.png")
        plt.close()

    # SIMPLE LINEAR TREND
    hist = (
        df.groupby("expiry_month")
          .size()
          .rename("expiring_count")
          .to_frame()
          .sort_index()
    )

    full_idx = pd.period_range(start=hist.index.min(), end=hist.index.max(), freq="M")
    hist = hist.reindex(full_idx, fill_value=0)

    x = np.arange(len(hist))
    slope, intercept = np.polyfit(x, hist["expiring_count"].values, 1)

    extra_months = 6
    future_x = np.arange(len(hist), len(hist) + extra_months)
    future_y = slope * future_x + intercept
    future_y = np.maximum(0, future_y)

    forecast_idx = pd.period_range(start=hist.index[-1] + 1, periods=extra_months, freq="M")
    forecast_df = pd.DataFrame({"predicted_expiring_count": future_y.astype(int)}, index=forecast_idx)
    forecast_df.to_csv(OUTPUT_DIR / "simple_trend_forecast_beyond_known.csv")

    plt.figure()
    hist["expiring_count"].plot(label="Known monthly expiries")
    forecast_df["predicted_expiring_count"].plot(label="Forecast")
    plt.title("Simple Linear Trend Forecast of Monthly Expiries (Beyond Known Dates)")
    plt.xlabel("Month")
    plt.ylabel("Count")
    plt.xticks(rotation=45, ha="right")
    plt.legend()
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "simple_trend_forecast.png")
    plt.close()

    print("Analysis complete! :) ")
    print(f"Outputs saved to: {OUTPUT_DIR.resolve()}")


if __name__ == "__main__":
    main()
