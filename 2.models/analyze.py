"""
Analysis that produced every number in 0.docs/TEAM_PLAYBOOK.md section 5.
Reads the cleaned files, prints the findings. Nothing is written.

    python3 2.models/analyze.py

Method: the 2018 Promotion cohort is compared with the like-for-like baseline
(2018 Standard joiners), never with the legacy base alone. Value is measured
from observed behaviour (flights, distance, points), not CLV, because CLV has
~zero correlation with flying.
"""
from pathlib import Path
import pandas as pd

pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 30)
CLEAN = Path(__file__).resolve().parents[1] / "1.data" / "cleaned"
CDN_PER_POINT = 0.18


def section(title):
    print(f"\n{'=' * 8} {title} {'=' * 8}")


def main():
    cu = pd.read_csv(CLEAN / "clean_customers.csv")
    ac = pd.read_csv(CLEAN / "clean_activity.csv")
    m = ac.merge(cu, on="Loyalty Number", how="left")
    cu["Cancelled"] = cu.Status == "Cancelled"
    m["Cancelled"] = m.Status == "Cancelled"

    section("FINDING 1: flights per member by cohort, 2018")
    a18 = m[m.Year == 2018]
    g = a18.groupby("Cohort").agg(members=("Loyalty Number", "nunique"), flights=("Total Flights", "sum"),
                                  earned=("Points Accumulated", "sum"), redeemed=("Points Redeemed", "sum"),
                                  km=("Distance", "sum"))
    g["flights/member"] = g.flights / g.members
    g["earn pts/km"] = g.earned / g.km
    g["redemption %"] = 100 * g.redeemed / g.earned
    g["unredeemed CDN/member"] = (g.earned - g.redeemed) * CDN_PER_POINT / g.members
    print(g.round(2))

    f17, f18 = m[m.Year == 2017]["Total Flights"].sum(), a18["Total Flights"].sum()
    print(f"\nflights 2017 {f17:,} -> 2018 {f18:,}  growth {f18-f17:,} ({100*(f18-f17)/f17:.1f}%)")
    for c in ["2018 Promotion", "2018 Standard"]:
        print(f"  {c}: {100*g.loc[c,'flights']/(f18-f17):.1f}% of growth")
    pre = m[m.Cohort == "Pre-2018 Standard"]
    p17, p18 = pre[pre.Year == 2017]["Total Flights"].sum(), pre[pre.Year == 2018]["Total Flights"].sum()
    print(f"  legacy base organic growth: {100*(p18-p17)/p17:.1f}%")

    post = a18[(a18.Month >= 5) & (a18["Enrollment Year"] == 2018)]
    pm = post.groupby(["Cohort", "Loyalty Number"])["Total Flights"].sum().reset_index()
    print("\nMay-Dec flights per member distribution (shows it is the whole cohort, not outliers):")
    print(pm.groupby("Cohort")["Total Flights"].describe().round(1))
    print("% with >=1 flight May-Dec:", (pm.groupby("Cohort")["Total Flights"].apply(lambda s: 100 * (s > 0).mean())).round(1).to_dict())

    section("FINDING 3: the 8-month cliff")
    t = a18[a18["Enrollment Year"] == 2018].groupby(["Cohort", "Month"]).agg(f=("Total Flights", "sum"), n=("Loyalty Number", "nunique"))
    print("monthly flights per member, 2018 joiners:")
    print((t.f / t.n).unstack(0).round(2))
    c18 = cu[(cu["Cancellation Year"] == 2018) & (cu["Enrollment Year"] == 2018)]
    print("\n2018 cancellations by month, 2018 joiners:")
    print(pd.crosstab(c18["Cancellation Month"].astype(int), c18.Cohort))
    print("\nchurn % by cohort:", (100 * cu.groupby("Cohort").Cancelled.mean()).round(1).to_dict())
    print("median tenure at cancellation (months):", cu[cu.Cancelled & (cu["Enrollment Year"] == 2018)].groupby("Cohort")["Tenure Months"].median().to_dict())
    pc = a18[a18.Cohort == "2018 Promotion"].groupby(["Cancelled", "Loyalty Number"])["Total Flights"].sum().reset_index()
    print("promo 2018 flights/member, cancelled vs retained:", pc.groupby("Cancelled")["Total Flights"].mean().round(1).to_dict())

    section("FINDING 4: demographics are flat")
    for seg in ["Loyalty Card", "Province", "Education", "Marital Status", "Gender"]:
        s = m.groupby(seg).agg(members=("Loyalty Number", "nunique"), flights=("Total Flights", "sum"),
                               cost=("Dollar Cost Points Redeemed", "sum"))
        s["flights/member 17-18"] = (s.flights / s.members).round(1)
        s["CDN cost/member"] = (s.cost / s.members).round(0)
        s["churn %"] = (100 * cu.groupby(seg).Cancelled.mean()).round(1)
        s["median CLV"] = cu.groupby(seg).CLV.median().round(0)
        print(f"\n{seg}:")
        print(s.drop(columns=["flights", "cost"]).sort_values("flights/member 17-18", ascending=False))
    mem = m.groupby("Loyalty Number").agg(flights=("Total Flights", "sum"), km=("Distance", "sum"),
                                          redeemed=("Points Redeemed", "sum"), earned=("Points Accumulated", "sum"))
    mem = mem.join(cu.set_index("Loyalty Number"))
    print(f"\ncorr(CLV, flights) = {mem.CLV.corr(mem.flights):.3f}   corr(Salary, flights) = {mem['Salary Clean'].corr(mem.flights):.3f}")
    ms = mem.sort_values("flights", ascending=False)
    cum = ms.flights.cumsum() / ms.flights.sum()
    print(f"top 20% of members = {100*cum.iloc[int(len(ms)*.2)]:.1f}% of flights; top 50% = {100*cum.iloc[int(len(ms)*.5)]:.1f}%")

    section("FINDING 5: redemption is retention")
    mem["redeemer"] = mem.redeemed > 0
    print("churn % redeemers vs non-redeemers:", (100 * mem.groupby("redeemer").Cancelled.mean()).round(1).to_dict())
    print("flights 17-18 redeemers vs non:", mem.groupby("redeemer").flights.mean().round(1).to_dict())
    print("% ever redeemed by cohort:", (100 * mem.groupby("Cohort").redeemer.mean()).round(1).to_dict())
    print("churn % by cohort x redeemer:")
    print((100 * mem.pivot_table(index="Cohort", columns="redeemer", values="Cancelled", aggfunc="mean")).round(1))
    earned, red, cost = ac["Points Accumulated"].sum(), ac["Points Redeemed"].sum(), ac["Dollar Cost Points Redeemed"].sum()
    print(f"\nprogramme redemption rate {100*red/earned:.2f}%   CDN per point {cost/red:.3f}   "
          f"unredeemed {earned-red:,.0f} pts = CDN {(earned-red)*cost/red/1e6:.1f}M")


if __name__ == "__main__":
    main()
