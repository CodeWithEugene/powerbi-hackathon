"""
Angani Air BI Hackathon - data cleaning pipeline.

Reads the three source CSVs in 1.data/raw/ (never modified) and writes the
Power BI-ready star schema:

    1.data/cleaned/clean_customers.csv                 dimension, one row per member
    1.data/cleaned/clean_activity.csv                  fact, one row per member x month
    1.data/cleaned/clean_calendar.csv                  date dimension, 2017-2018 daily
    1.data/cleaned/AnganiAir_Model.xlsx                same three tables, for Power BI Service upload
    1.data/cleaned/clean_flat_activity_customers.csv   single flat table fallback

Run from the repo root:  python3 2.models/clean_data.py
Every cleaning decision is explained in 0.docs/TEAM_PLAYBOOK.md section 3.
"""
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "1.data" / "raw"
CLEAN = ROOT / "1.data" / "cleaned"
CDN_PER_POINT = 0.18  # observed: total redemption cost / total points redeemed


def load_sources():
    h = pd.read_csv(RAW / "Customer Loyalty History.csv")
    a = pd.read_csv(RAW / "Customer Flight Activity.csv")
    c = pd.read_csv(RAW / "Calendar.csv")
    # BOM / stray whitespace in headers
    for df in (h, a, c):
        df.columns = [col.strip().lstrip("﻿") for col in df.columns]
    return h, a, c


def build_customers(h: pd.DataFrame) -> pd.DataFrame:
    d = h.copy()

    # Cohort: promo must be compared with a like-for-like baseline (2018 standard joiners)
    d["Cohort"] = np.where(
        d["Enrollment Type"] == "2018 Promotion", "2018 Promotion",
        np.where(d["Enrollment Year"] == 2018, "2018 Standard", "Pre-2018 Standard"),
    )
    d["Status"] = np.where(d["Cancellation Year"].notna(), "Cancelled", "Active")

    d["Enrollment Date"] = pd.to_datetime(
        dict(year=d["Enrollment Year"], month=d["Enrollment Month"], day=1))
    d["Cancellation Date"] = pd.to_datetime(
        dict(year=d["Cancellation Year"], month=d["Cancellation Month"], day=1), errors="coerce")

    # Tenure: enrolment -> cancellation, or -> Dec 2018 (end of data) if still active
    end_year = np.where(d["Cancellation Date"].notna(), d["Cancellation Date"].dt.year, 2018)
    end_month = np.where(d["Cancellation Date"].notna(), d["Cancellation Date"].dt.month, 12)
    d["Tenure Months"] = ((end_year - d["Enrollment Date"].dt.year) * 12
                          + (end_month - d["Enrollment Date"].dt.month)).astype(int)

    # Salary: 20 negatives are errors -> null. 4,238 blanks (all College) kept and flagged.
    d["Salary Clean"] = d["Salary"].where(d["Salary"] >= 0, np.nan)
    d["Salary Missing"] = d["Salary Clean"].isna()

    # CLV is right-skewed; band it and report medians, never rely on the mean
    d["CLV Band"] = pd.cut(d["CLV"], [0, 4000, 6000, 10000, 20000, 1e9],
                           labels=["<4k", "4-6k", "6-10k", "10-20k", "20k+"])
    d["Card Rank"] = d["Loyalty Card"].map({"Aurora": 1, "Nova": 2, "Star": 3})

    return d.drop(columns=["Country"])  # constant (Canada)


def build_activity(a: pd.DataFrame, customers: pd.DataFrame) -> pd.DataFrame:
    n0 = len(a)
    f = a.drop_duplicates()                       # 1. exact duplicate rows
    n1 = len(f)
    f = f.groupby(["Loyalty Number", "Year", "Month"], as_index=False).sum()  # 2. split rows -> member x month
    n2 = len(f)
    print(f"activity: {n0:,} rows -> {n1:,} after exact dedupe (-{n0-n1:,}) "
          f"-> {n2:,} at member x month grain (-{n1-n2:,} split rows summed)")

    f["Month Start"] = pd.to_datetime(dict(year=f["Year"], month=f["Month"], day=1))
    f = f.merge(customers[["Loyalty Number", "Enrollment Date"]], on="Loyalty Number", how="left")
    f["Post Enrollment"] = f["Month Start"] >= f["Enrollment Date"]
    f["Months Since Enrollment"] = ((f["Month Start"].dt.year - f["Enrollment Date"].dt.year) * 12
                                    + (f["Month Start"].dt.month - f["Enrollment Date"].dt.month))
    return f.drop(columns=["Enrollment Date"])


def build_calendar(c: pd.DataFrame) -> pd.DataFrame:
    cal = c.copy()
    cal["Date"] = pd.to_datetime(cal["Date"])
    cal = cal[cal["Date"].dt.year >= 2017].copy()   # activity only covers 2017-2018
    cal["Year"] = cal["Date"].dt.year
    cal["Month"] = cal["Date"].dt.month
    cal["Month Name"] = cal["Date"].dt.strftime("%b")
    cal["Quarter"] = "Q" + cal["Date"].dt.quarter.astype(str)
    cal["Year-Month"] = cal["Date"].dt.strftime("%Y-%m")
    is18 = cal["Year"] == 2018
    cal["Promo Period"] = np.select(
        [is18 & cal["Month"].between(2, 4), is18 & (cal["Month"] >= 5), is18],
        ["Promo (Feb-Apr 18)", "Post-promo (May-Dec 18)", "Pre-promo (Jan 18)"],
        default="2017 Baseline",
    )
    return cal


def build_flat(activity, customers, calendar) -> pd.DataFrame:
    months = calendar.drop_duplicates("Start of Month")[["Start of Month", "Promo Period", "Quarter", "Month Name"]].copy()
    months["Start of Month"] = pd.to_datetime(months["Start of Month"])
    flat = (activity
            .merge(customers.drop(columns=["Postal Code", "City"]), on="Loyalty Number", how="left")  # no quasi-identifiers
            .merge(months, left_on="Month Start", right_on="Start of Month", how="left")
            .drop(columns=["Start of Month"]))
    return flat


def main():
    h, a, c = load_sources()
    customers = build_customers(h)
    activity = build_activity(a, customers)
    calendar = build_calendar(c)

    customers.to_csv(CLEAN / "clean_customers.csv", index=False)
    activity.to_csv(CLEAN / "clean_activity.csv", index=False)
    calendar.to_csv(CLEAN / "clean_calendar.csv", index=False)
    with pd.ExcelWriter(CLEAN / "AnganiAir_Model.xlsx", engine="openpyxl") as w:
        customers.to_excel(w, sheet_name="Customers", index=False)
        activity.to_excel(w, sheet_name="Activity", index=False)
        calendar.to_excel(w, sheet_name="Calendar", index=False)
    build_flat(activity, customers, calendar).to_csv(CLEAN / "clean_flat_activity_customers.csv", index=False)

    print(f"customers: {len(customers):,}  promo: {(customers.Cohort=='2018 Promotion').sum():,}  "
          f"std2018: {(customers.Cohort=='2018 Standard').sum():,}  cancelled: {(customers.Status=='Cancelled').sum():,}")
    print(f"flights: {activity['Total Flights'].sum():,}  points earned: {activity['Points Accumulated'].sum():,.0f}  "
          f"redeemed: {activity['Points Redeemed'].sum():,}  CDN: {activity['Dollar Cost Points Redeemed'].sum():,}")
    print("wrote 5 files to 1.data/cleaned/")


if __name__ == "__main__":
    main()
