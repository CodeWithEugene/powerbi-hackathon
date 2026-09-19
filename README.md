# Angani Air: Turning Loyalty Data into Customer Growth

Moringa / Angani BI Hackathon — Case Study dated **19 September 2026**.

> **Core business question:** Did the 2018 Loyalty Program Promotion create valuable customer behaviour, and how should Angani Air improve its loyalty strategy?
>
> Management must answer: **Who should we target · What should we offer them · Where should we invest our loyalty budget?**

## 1. Business situation

Angani Air (AA), a growing African airline, ran a **Loyalty Program Promotion Feb–Apr 2018**. It generated many signups, but management does not know if it created *valuable* behaviour (repeat travel, spend, retention) or just cheap acquisition.

This team was hired as the **Business Intelligence & Customer Strategy team**. We are not asked to "build a dashboard" — we must deliver a **management decision-support solution**:

```
Understand Business → Define Decisions → Identify Questions →
Select KPIs → Storyboard → Build Dashboards
```

Investigation chain required by the brief:

```
Campaign → Loyalty Membership → Customer Characteristics →
Flight Behaviour → Customer Value
```

Move beyond "what happened" to **credible insights + actionable recommendations**.

## 2. Repo structure

```
"PowerBI Hackathon"/
├── 0.docs/                                         # Brief
│   └── Moringa Angani BI Hackathon Case Study.pdf
├── 1.data/                                         # Source data (from https://smplu.link/BIHACKATHON)
│   ├── Customer Loyalty History.csv                # 16,737 members, one row per member
│   ├── Customer Flight Activity.csv                # 392,936 rows, monthly grain, Jan 2017–Dec 2018
│   ├── Calendar.csv                                # 2,557 days, 2012-01-01 to 2018-12-31
│   └── Airline Loyalty Data Dictionary.csv         # Field definitions
├── README..md                                      # This file (note: double-dot typo, keep for compat)
├── CONTRIBUTING.md                                 # Team workflow + Power BI standards
├── SECURITY.md                                     # Data-privacy + secret hygiene
└── LICENSE.md                                      # Licence + dataset terms
```

> Dataset note from the brief: adapted from a public airline dataset. Company names and context modified for the hackathon. Educational use only.

## 3. Data at a glance

**Customer Loyalty History** (dimension, `Loyalty Number` PK):
`Country, Province, City, Postal Code, Gender, Education, Salary, Marital Status, Loyalty Card (Star > Nova > Aurora), CLV, Enrollment Type (Standard / 2018 Promotion), Enrollment Year/Month, Cancellation Year/Month`.

Profiled values:
- Enrollment: Standard 15,766 · 2018 Promotion **971** (Feb 295, Mar 330, Apr 346). Total 2018 enrolments: 3,010.
- Card: Star 7,637 · Nova 5,671 · Aurora 3,429.
- Geography: all Canada (Ontario 5,404, BC 4,409, Quebec 3,300, + 8 smaller provinces).
- Demographics: ~50/50 gender; Bachelor 10,475 dominant; Married 9,735 / Single 4,484 / Divorced 2,518.
- Cancellations: 2,067 members have a cancellation date.
- Data quirks: `Salary` missing in 4,238 rows, contains negatives/min –58k, max ~407k, median ~73k. `CLV` mean ~7,989, median ~5,780, max ~83k — right-skewed, segment before averaging.

**Customer Flight Activity** (fact, grain: member × year × month):
`Total Flights, Distance (km), Points Accumulated, Points Redeemed, Dollar Cost Points Redeemed (CDN)`.
Totals: ~508k flights; ~796.5M points accumulated vs ~12.3M redeemed (~2.2M CDN cost). 2017: 191,100 rows; 2018: 201,836 rows.

**Calendar**: date spine with `Start of Year / Quarter / Month`. Use for time intelligence; join Activity Year+Month to it.

**Suggested joins:** `History[Loyalty Number]` 1—* `Activity[Loyalty Number]`; `Activity[Year-Month]` *—1 `Calendar[Month start]`.

## 4. Decisions, questions, KPIs

Decisions to support: retain/grow high-value segments, fix or kill promotion-style acquisition, reallocate loyalty budget by card tier / region / cohort.

Starter questions:
- Did Promotion cohort fly more, spend more (CLV), retain better, redeem differently vs Standard 2018 cohort and pre-2018 cohorts?
- Which card tier / province / education / marital segment gives best flights-per-member, CLV, retention, redemption cost?
- Where is breakage (unredeemed points) vs liability (redemption CDN cost) concentrated?

Starter KPIs (always split by Enrollment Type + cohort):
Members, % Promotion mix, Total Flights, Flights/Member, Distance/Member, Avg CLV, Retention % (1 – cancelled), Churn %, Points Accumulated/Redeemed, Redemption rate, CDN cost per member, Breakage estimate.

## 5. Deliverable + judging

- **Tool:** final BI solution **must be Microsoft Power BI**. Excel / Python / SQL allowed for cleaning, exploration, accuracy checks.
- **Format:** interactive PBIX, **max 5 report pages** (tabs). More pages ≠ more marks.
- Must show: data prep, modelling, meaningful KPIs, analytical depth, visualisation, interactivity, storytelling, actionable insights.
- **Submit:** email PBIX to **bidasanalytics@gmail.com**.
- **AI policy:** ChatGPT / Copilot / Gemini permitted, but the team must understand, validate, and explain any AI-generated output.

Peer judging (each group leader scores via WhatsApp form, 1–10 each, 50 max):

| Criterion | What is judged |
|---|---|
| Business Understanding (10) | Real problem, domain/user context |
| Dashboard Design & Interactivity (10) | Clarity, layout, filters/drill-downs/hover |
| Storytelling & Narrative Flow (10) | Problem → insight → conclusion |
| Decision-Focused Insights (10) | Non-obvious, viewer knows what to do next |
| Final Presentation (10) | Clear, confident, ≤10 min |

Presentation: tell **What happened → Why it matters → What management should do next**. Not a page-by-page walkthrough. Max **10 minutes**, presented to peers as the AA Executive Committee.

## 6. Getting started

1. Read `0.docs/Moringa Angani BI Hackathon Case Study.pdf` and the Data Dictionary CSV.
2. Profile/clean with Python/SQL (handle blank Salary, negative salaries, blank cancellations, CLV outliers).
3. Model in Power BI per §3 joins; build a Calendar month key; write DAX measures (see `CONTRIBUTING.md` naming).
4. Storyboard ≤5 pages, e.g.: (1) Executive answer, (2) Campaign effectiveness, (3) Who is valuable, (4) Behaviour & points economics, (5) Recommendations & next investment.
5. Validate numbers against source CSVs before submitting PBIX.

See `CONTRIBUTING.md` for workflow and `SECURITY.md` before sharing data externally.
