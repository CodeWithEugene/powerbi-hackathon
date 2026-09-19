"""
Control-total checks for the cleaned data. Run after clean_data.py and again
after loading into Power BI (compare the cards with what this prints).

    python3 2.models/validate.py
Exits non-zero if any total is off.
"""
from pathlib import Path
import sys
import pandas as pd

CLEAN = Path(__file__).resolve().parents[1] / "1.data" / "cleaned"

EXPECTED = {
    "members": 16_737,
    "promo_members": 971,
    "std2018_members": 2_039,
    "cancelled": 2_067,
    "total_flights": 508_808,
    "flights_2017": 223_262,
    "flights_2018": 285_546,
    "points_earned": 796_548_992.5,
    "points_redeemed": 12_300_572,
    "redemption_cost_cdn": 2_214_454,
    "promo_flights_2018": 44_877,
    "std2018_flights_2018": 17_165,
}


def main() -> int:
    cu = pd.read_csv(CLEAN / "clean_customers.csv")
    ac = pd.read_csv(CLEAN / "clean_activity.csv")
    m = ac.merge(cu[["Loyalty Number", "Cohort"]], on="Loyalty Number")
    a18 = m[m.Year == 2018]
    actual = {
        "members": len(cu),
        "promo_members": (cu.Cohort == "2018 Promotion").sum(),
        "std2018_members": (cu.Cohort == "2018 Standard").sum(),
        "cancelled": (cu.Status == "Cancelled").sum(),
        "total_flights": ac["Total Flights"].sum(),
        "flights_2017": ac[ac.Year == 2017]["Total Flights"].sum(),
        "flights_2018": a18["Total Flights"].sum(),
        "points_earned": ac["Points Accumulated"].sum(),
        "points_redeemed": ac["Points Redeemed"].sum(),
        "redemption_cost_cdn": ac["Dollar Cost Points Redeemed"].sum(),
        "promo_flights_2018": a18[a18.Cohort == "2018 Promotion"]["Total Flights"].sum(),
        "std2018_flights_2018": a18[a18.Cohort == "2018 Standard"]["Total Flights"].sum(),
    }
    ok = True
    for k, exp in EXPECTED.items():
        got = actual[k]
        flag = "OK " if abs(float(got) - float(exp)) < 0.5 else "FAIL"
        ok &= flag == "OK "
        print(f"{flag} {k:<22} expected {exp:>16,}  got {got:>16,}")
    # grain check: one row per member x month
    dups = ac.duplicated(["Loyalty Number", "Year", "Month"]).sum()
    print(f"{'OK ' if dups == 0 else 'FAIL'} {'unique member x month':<22} duplicates = {dups}")
    ok &= dups == 0
    # every activity member exists in customers
    orphans = (~ac["Loyalty Number"].isin(cu["Loyalty Number"])).sum()
    print(f"{'OK ' if orphans == 0 else 'FAIL'} {'no orphan members':<22} orphans = {orphans}")
    ok &= orphans == 0
    print("\nALL CHECKS PASSED" if ok else "\nCHECKS FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
