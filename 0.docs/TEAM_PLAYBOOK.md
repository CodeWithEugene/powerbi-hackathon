# Angani Air BI Hackathon — Team Playbook

**Read this once, start to finish (10 minutes). Then go to your role in Section 8.**

This document holds everything: what the challenge asks, what the data contains, how we cleaned it and why, what we found, what we are building in Power BI, the DAX, the five-page storyboard, who does what in the 120 minutes, the 10-minute pitch, and the answers to the questions we will be asked.

---

## 1. The challenge in one paragraph

Angani Air ran a Loyalty Program Promotion from **February to April 2018**. It produced many signups. Management does not know whether those signups became valuable customers (repeat flying, spend, retention) or were just cheap acquisition. We are hired as the Business Intelligence and Customer Strategy team. The deliverable is a **Power BI file (PBIX), maximum 5 report pages**, emailed to `bidasanalytics@gmail.com`, plus a **10-minute presentation** to the other teams acting as the Angani Air Executive Committee.

The core question: **"Did the 2018 Loyalty Program Promotion create valuable customer behaviour, and how should Angani Air improve its loyalty strategy?"**

Management wants three answers: **Who should we target · What should we offer them · Where should we invest the loyalty budget.**

The brief is explicit that we are **not** being asked to "build a dashboard". The expected method is: Understand Business → Define Decisions → Identify Questions → Select KPIs → Storyboard → Build. The investigation chain is Campaign → Loyalty Membership → Customer Characteristics → Flight Behaviour → Customer Value.

### How we are judged

Peer scoring. Each group leader scores every other team 1 to 10 on five criteria, 50 points maximum.

| Criterion | What is judged | How we score high |
|---|---|---|
| Business Understanding | Real problem, domain and user context | Open with the decision, not the data. Frame every page as Who/What/Where. |
| Dashboard Design & Interactivity | Clear layout, filters, drill-downs, hover | Two colours, insight-sentence titles, synced slicers, one drill-through, tooltip pages. |
| Storytelling & Narrative Flow | Problem → insight → conclusion | Page 1 is the answer. Pages 2 to 4 are the evidence. Page 5 is the action. |
| Decision-Focused Insights | Non-obvious, viewer knows what to do next | Our four findings (Section 5) are things the other teams will not find. |
| Final Presentation | Clear, confident, within 10 minutes | Scripted, rehearsed three times, 8 minutes, no page walkthrough. |

The presentation must follow **What happened → Why it matters → What management should do next**.

---

## 2. The data

Three CSV files in `1.data/raw/`, plus a data dictionary. Generated files go to `1.data/cleaned/`.

### Customer Loyalty History (dimension, 16,737 rows, one per member)

Key: `Loyalty Number`. Columns: Country (always Canada), Province, City, Postal Code, Gender, Education, Salary, Marital Status, Loyalty Card (Star, Nova, Aurora), CLV, Enrollment Type (Standard or 2018 Promotion), Enrollment Year and Month, Cancellation Year and Month (blank if still a member).

What we profiled:

| Field | Finding |
|---|---|
| Enrollment Type | Standard 15,766 · **2018 Promotion 971** (Feb 295, Mar 330, Apr 346) |
| Enrolled in 2018 | 3,010 total = 971 promotion + 2,039 standard |
| Loyalty Card | Star 7,637 · Nova 5,671 · Aurora 3,429 |
| Province | Ontario 5,404 · BC 4,409 · Quebec 3,300 · eight smaller provinces |
| Cancelled | 2,067 members have a cancellation date |
| Salary | 4,238 blank (every one of them has Education = College, so it is a systematic gap, not random). 20 negative values. Median about 73k. |
| CLV | Mean 7,989, median 5,780, max 83k. Heavily right-skewed. **CLV has a correlation of -0.005 with actual flights flown in 2017 to 2018.** It is described as "total invoice value for all flights ever booked", so for a member who joined in 2018 it cannot describe 2018 behaviour. We treat it as a legacy label, not a value measure. |

### Customer Flight Activity (fact, 392,936 rows)

Grain: one row per member per year per month, Jan 2017 to Dec 2018. Columns: Total Flights, Distance (km), Points Accumulated, Points Redeemed, Dollar Cost Points Redeemed (CDN).

Totals: about 508k flights, 796.5M points earned, 12.3M points redeemed, CDN 2.21M redemption cost. Every Loyalty Number in this file exists in the History file.

### Calendar (2,557 rows)

Daily date spine from 2012 to 2018 with Start of Year, Start of Quarter, Start of Month. We only need 2017 to 2018.

---

## 3. Data cleaning — what we did and why

All cleaning was done in Python (pandas). Source files in `1.data/raw/` were never modified. Outputs are written to `1.data/cleaned/`. The brief allows Python for cleaning; the final visuals must be Power BI.

| Issue found | What we did | Why |
|---|---|---|
| **1,922 exact duplicate rows** in Activity (identical in every column) | Removed | A duplicated row double-counts flights and points. Most were all-zero rows, but 7,490 flights were in duplicated rows. |
| **1,949 further rows sharing the same member + year + month but with different values** | Summed to one row per member per month | These look like split bookings within a month (one row for 1 flight of 667 km, another for 1 flight of 2,499 km). The dictionary defines the grain as member × period, so we aggregate to it. This lets Power BI relationships work cleanly. |
| 20 negative salaries | Set to blank | A negative annual income is a data error. Blanking rather than deleting keeps the member. |
| 4,238 blank salaries, all College | Kept, added a `Salary Missing` flag | Deleting 25% of members would bias everything. We do not use Salary in any headline number. |
| CLV skew and zero correlation with behaviour | Kept, added a `CLV Band`; we report median, not mean, and we say so | Averaging a skewed field misleads. More importantly we measure value from observed flights and points instead. |
| No cohort field | Added `Cohort`: "2018 Promotion", "2018 Standard", "Pre-2018 Standard" | The brief and CONTRIBUTING.md require the promotion to be compared with a like-for-like baseline, which is people who joined in the same year without the promotion. |
| No status field | Added `Status` (Active / Cancelled) and `Tenure Months` | Needed for churn and retention. Tenure is enrolment to cancellation, or to Dec 2018 if still active. |
| Activity rows exist for months before a member enrolled (14,765 rows for 2018 joiners, 1,317 of them with flights) | Kept, added `Post Enrollment` flag and `Months Since Enrollment` | People flew before joining the programme. That is real. We flag it so post-enrolment behaviour can be isolated. |
| Country column is constant | Dropped | Adds nothing. |
| No promo window marker on dates | Added `Promo Period` to Calendar: 2017 Baseline / Pre-promo (Jan 18) / Promo (Feb–Apr 18) / Post-promo (May–Dec 18) | Lets us shade the campaign window and compare periods with one slicer. |

### Output files

| File | Use |
|---|---|
| `1.data/cleaned/clean_customers.csv` | Dimension table. 16,737 rows. |
| `1.data/cleaned/clean_activity.csv` | Fact table. 389,065 rows after cleaning. |
| `1.data/cleaned/clean_calendar.csv` | Date dimension, 2017 to 2018 daily. |
| `1.data/cleaned/AnganiAir_Model.xlsx` | The same three tables as sheets, for uploading to Power BI Service in a browser if no Windows machine is available. |
| `1.data/cleaned/clean_flat_activity_customers.csv` | Everything joined into one flat table. Last-resort fallback that needs no relationships. |

### Control totals after cleaning (every Power BI card must match these)

| Measure | Value |
|---|---|
| Members | 16,737 |
| 2018 Promotion members | 971 |
| 2018 Standard members | 2,039 |
| Cancelled members | 2,067 |
| Total Flights | 508,808 |
| Flights 2017 | 223,262 |
| Flights 2018 | 285,546 |
| Points Earned | 796,548,992 |
| Points Redeemed | 12,300,572 |
| Redemption cost CDN | 2,214,454 |

### Reproducing the cleaning and the analysis

The full pipeline lives in `2.models/` as three Python scripts. Run them from the repo root, in this order. They need `pandas` and `openpyxl`.

```bash
python3 2.models/clean_data.py
```
Reads the three source CSVs, applies every rule in the table above, and writes the five files listed in "Output files". Prints the row counts at each step (392,936 → 391,014 after exact dedupe → 389,065 at member × month grain) and the control totals.

```bash
python3 2.models/validate.py
```
Checks the cleaned files against the control totals below, confirms the fact table is unique on member × month, and confirms every activity member exists in the customer table. Exits non-zero on any failure. **Run it before loading into Power BI, then compare the Power BI cards with what it prints.**

```bash
python3 2.models/analyze.py
```
Reproduces every number in Section 5: cohort comparison, share of growth, the monthly cliff, cancellations by month, flat demographics, correlation of CLV with flights, and the redeemer versus non-redeemer churn split. Writes nothing.

If anyone asks "how did you get that number", the answer is one of these three files.

---

## 4. How we analysed it — the logic

The brief says compare the promotion to a baseline. The honest baseline is **people who joined in 2018 without the promotion** (2,039 members). They joined in the same year, face the same programme, the same routes, the same economy. The only difference is the offer. Comparing promo members with the whole legacy base would be unfair because legacy members have years of tenure.

We asked five questions, in the order of the brief's chain:

1. **Campaign → Membership.** How many joined, and did they stay? (Members, churn, tenure at cancellation.)
2. **Membership → Characteristics.** Are promo members a different kind of person? (Card, province, education, marital status mix by cohort.)
3. **Characteristics → Behaviour.** Do any characteristics predict flying? (Flights per member by every segment.)
4. **Behaviour → Value.** How much did each cohort fly and earn, and what did it cost? (Flights per member, distance, points earned, redeemed, redemption cost, earn rate.)
5. **Retention drivers.** What separates members who stay from members who leave? (Churn by redemption behaviour, by cohort.)

Value is measured from **observed behaviour** (flights, distance, points), not from CLV, because CLV does not correlate with any of it.

---

## 5. What we found

### Finding 1 — The promotion created the most valuable flyers the programme has

| Metric (2018) | 2018 Promotion | 2018 Standard | Pre-2018 Standard |
|---|---|---|---|
| Members | 971 (5.8% of base) | 2,039 | 13,727 |
| Flights in 2018 | 44,877 | 17,165 | 223,504 |
| **Flights per member** | **46.2** | 8.4 | 16.3 |
| Km per member (May–Dec) | 65,981 | 11,270 | |
| Members with at least one flight May–Dec | 94.9% | 82.9% | |

2018 flights grew by 62,284 over 2017 (+27.9%). The promo cohort alone accounts for **72%** of that growth. The 2018 standard cohort accounts for 28%. The legacy base grew only 2.3% on its own.

This is not a few outliers. Among promo members, May to December flights have a median of 44, an interquartile range of 32 to 58, and a minimum of 0. The whole cohort flies heavily.

### Finding 2 — The mechanic was a 50% points bonus, and it is expensive

| | 2018 Promotion | 2018 Standard | Legacy |
|---|---|---|---|
| Points earned per km | **1.50** | 1.00 | 1.00 |
| Redemption rate (redeemed ÷ earned) | **0.37%** | 1.75% | 1.74% |
| Unredeemed points value per member (at CDN 0.18 per point) | **CDN 18,665** | CDN 2,870 | |

CDN 0.18 per point is the observed ratio of redemption cost to points redeemed across the whole dataset. Promo members earned 101M points in 2018 and redeemed 375k. They are sitting on about CDN 18M of unredeemed value.

### Finding 3 — Then we lost 1 in 8 of them, all at the same moment

| | 2018 Promotion | 2018 Standard |
|---|---|---|
| Churn within 2018 | **11.8%** (115 of 971) | 2.2% (44 of 2,039) |
| Median tenure at cancellation | **8 months** | 8 months |

Promo flights per member per month: 6.4 in May, 8.4 in June, 8.7 in July, 7.7 in August, then **2.8 in September**, 2.7 in October, 2.4 in November. Engagement fell about 70% in one month.

Promo cancellations by month: 1 in March, 3 in April, 2 in May, 0 in June, 0 in July, 4 in August, 1 in September, then **30 in October, 31 in November, 43 in December**.

Reading: a time-boxed bonus (roughly six months from the Feb to Apr joins) ended around September, flying collapsed, and cancellations followed a month or two later. The members who cancelled were not low-value. They flew **40 flights each** in 2018 versus 47 for those who stayed.

### Finding 4 — Demographics predict nothing

Flights per member over 2017 to 2018, by segment:

| Segment | Range across all values |
|---|---|
| Loyalty Card | Aurora 30.6 · Nova 30.5 · Star 30.3 |
| Province (11) | 27.6 (PEI, 66 members) to 33.6 (Yukon, 110 members); the big provinces all 30.3 to 30.7 |
| Education (5) | 30.3 to 31.0 |
| Marital Status | 30.1 to 30.6 |
| Gender | 30.2 to 30.6 |

Every segment is flat at about 30 flights. Churn ranges only 11.8% to 13.1% across card tiers. Redemption cost per member is CDN 127 to 138 everywhere. CLV correlates -0.005 with flights, and Salary correlates -0.007. **Targeting by who people are will not find value. Targeting by what they do will.** The promo cohort has the same card, province, education, and marital mix as everyone else; what makes them different is the offer they got.

### Finding 5 — Redemption is the retention lever

| | Churn |
|---|---|
| Members who have redeemed at least once | **4.9%** |
| Members who have never redeemed | **40.8%** |

Across the whole base, 98.5% of points are never redeemed. 784M unredeemed points sit on the books, about CDN 141M at observed value. Only 35% of 2018 standard joiners and 52% of promo joiners have ever redeemed, against 75% of legacy members. Redeemers also fly twice as much (36 flights vs 18).

Causality caveat we state openly: heavy flyers redeem more and also churn less, so redemption is partly a marker of engagement. But redemption is the one lever the airline controls directly, so it is the right intervention point.

### Finding 6 — Value is spread, not concentrated

The top 20% of members account for only 34% of flights; the top 50% for 72%. There is no small elite to protect. Retention has to work at the cohort level.

---

## 6. The answer we give management

**"The promotion built our best flyers. Then we let 12% of them walk because the offer had a cliff and nobody redeemed."**

| Question | Answer |
|---|---|
| **Who** should we target | The 856 retained promo members and every 2018 joiner who has never redeemed (about 65% of the standard cohort). Stop demographic targeting; it is flat. |
| **What** should we offer | (1) A first-redemption nudge inside 90 days, because redeemers churn 5% vs 41%. (2) Re-run the promotion but taper the earn bonus from 1.5× to 1.25× to 1.0× over months 6 to 12 instead of ending it. (3) A win-back offer to the 115 cancelled promo members, who flew 40 flights each. |
| **Where** should the budget go | Away from acquisition by demographic segment. Into months 6 to 9 of the member lifecycle and into redemption incentives. Spend flat across provinces because none outperforms. |

Expected effect, stated as estimates: halving promo churn keeps about 55 members × 46 flights, roughly 2,500 flights a year from a 971-person cohort. Lifting 2018 standard redemption from 35% to legacy levels of 75% would move most of them from the 41% churn group to the 5% group.

---

## 7. What we build in Power BI

### Model (star schema)

- `clean_customers` (dimension) one-to-many `clean_activity` (fact) on `Loyalty Number`.
- `clean_calendar` (dimension) one-to-many `clean_activity` on `Date` to `Month Start`. Mark `clean_calendar` as the date table. Single-direction filters only.
- Hide `Loyalty Number`, `Year`, `Month`, `Postal Code`, `City` from report view. No member-level tables in the report (see SECURITY.md).
- Theme: two colours. Promo cohort in one strong colour, everything else grey. Nothing else.

### DAX measures (paste as-is)

```dax
Total Flights = SUM(clean_activity[Total Flights])
Total Distance km = SUM(clean_activity[Distance])
Points Earned = SUM(clean_activity[Points Accumulated])
Points Redeemed = SUM(clean_activity[Points Redeemed])
Redemption Cost CDN = SUM(clean_activity[Dollar Cost Points Redeemed])
Members = DISTINCTCOUNT(clean_customers[Loyalty Number])
Active Members = CALCULATE([Members], clean_customers[Status] = "Active")
Cancelled Members = CALCULATE([Members], clean_customers[Status] = "Cancelled")
Churn % = DIVIDE([Cancelled Members], [Members])
Retention % = 1 - [Churn %]
Flying Members = DISTINCTCOUNT(clean_activity[Loyalty Number])
Flights per Member = DIVIDE([Total Flights], [Flying Members])
Distance per Member = DIVIDE([Total Distance km], [Flying Members])
Redemption Rate % = DIVIDE([Points Redeemed], [Points Earned])
Unredeemed Points = [Points Earned] - [Points Redeemed]
CDN per Point = DIVIDE([Redemption Cost CDN], [Points Redeemed])
Unredeemed Liability CDN = [Unredeemed Points] * 0.18
Liability per Member CDN = DIVIDE([Unredeemed Liability CDN], [Flying Members])
Cost per Member CDN = DIVIDE([Redemption Cost CDN], [Flying Members])
Earn Rate pts per km = DIVIDE([Points Earned], [Total Distance km])
Avg CLV = AVERAGE(clean_customers[CLV])
Median CLV = MEDIAN(clean_customers[CLV])
Promo Members % = DIVIDE(CALCULATE([Members], clean_customers[Cohort] = "2018 Promotion"), [Members])

Flights PY = CALCULATE([Total Flights], SAMEPERIODLASTYEAR(clean_calendar[Date]))
Flights YoY % = DIVIDE([Total Flights] - [Flights PY], [Flights PY])
Flights Growth Abs = [Total Flights] - [Flights PY]
Share of Growth % =
    DIVIDE([Flights Growth Abs],
           CALCULATE([Flights Growth Abs], REMOVEFILTERS(clean_customers)))

Redeemers =
    CALCULATE(DISTINCTCOUNT(clean_activity[Loyalty Number]), clean_activity[Points Redeemed] > 0)
Redeemer % = DIVIDE([Redeemers], [Flying Members])
Churn % Redeemers =
    VAR r = CALCULATETABLE(VALUES(clean_activity[Loyalty Number]), clean_activity[Points Redeemed] > 0)
    RETURN DIVIDE(CALCULATE([Cancelled Members], r), CALCULATE([Members], r))
Churn % Non-Redeemers =
    VAR r = CALCULATETABLE(VALUES(clean_activity[Loyalty Number]), clean_activity[Points Redeemed] > 0)
    RETURN DIVIDE(CALCULATE([Cancelled Members], EXCEPT(VALUES(clean_customers[Loyalty Number]), r)),
                  CALCULATE([Members], EXCEPT(VALUES(clean_customers[Loyalty Number]), r)))

Flights per Member Post-Enrol =
    CALCULATE([Flights per Member], clean_activity[Post Enrollment] = TRUE())
Avg Tenure Months = AVERAGE(clean_customers[Tenure Months])
```

Validation after pasting: `Total Flights` card shows 508,808. Filter Cohort to "2018 Promotion": flights 44,877, `Flights per Member` 46.2, `Redemption Rate %` 0.37%, `Churn %` 11.8%. Filter to "2018 Standard": flights 17,165, 8.4 per member, 1.75%, 2.2%. If any of these is off, stop and fix the model before building visuals.

### The five pages

Every visual title is a sentence stating the insight, not a label. Slicers for Cohort, Loyalty Card, Province on every page, synced.

**Page 1 — Executive answer.** Title: *"The promo built our best flyers. Then we lost 12% of them in one quarter."*
- Five KPI cards: Flights YoY +27.9% · Promo share of growth 72% · Promo flights per member 46 vs 8 · Promo churn 11.8% vs 2.2% · Unredeemed points CDN 141M.
- One line chart: monthly total flights, 2017 vs 2018, promo window Feb to Apr shaded.
- Three tiles: Who / What / Where, one sentence each, linking to Page 5.
- Footnote: "Cleaned in Python: duplicates removed, member × month grain. All figures reconcile to source."

**Page 2 — Campaign effectiveness.** Title: *"Like-for-like, promo members flew 5.5× more than standard 2018 joiners."*
- Clustered bars by cohort: Flights per Member, Distance per Member, Redemption Rate, Churn %.
- Line: monthly flights per member, Promo vs 2018 Standard, Jan to Dec 2018. This shows the September cliff.
- Column chart: cancellations by month × cohort. This shows the Oct to Dec spike.
- Small table: earn rate 1.5 vs 1.0 points per km.
- Tooltip page: member counts and enrolment month.

**Page 3 — Who is valuable.** Title: *"It isn't demographics. Behaviour predicts value; segments don't."*
- Four small bar charts, Flights per Member by Card, Province, Education, Marital Status, all on a **fixed y-axis 0 to 40** so the flatness is visible.
- Scatter: CLV vs Total Flights, with note "r ≈ 0. CLV is legacy invoice history, not 2017 to 2018 behaviour."
- Two-bar chart: Churn % Redeemers 4.9% vs Churn % Non-Redeemers 40.8%. This is the page's punchline.
- Decomposition tree: Churn % → Redeemer flag → Cohort → Card.

**Page 4 — Points economics.** Title: *"98.5% of points are never redeemed. Promo members are banking CDN 18.7k each."*
- Waterfall by cohort: Points Earned → Redeemed → Unredeemed.
- Bar: Liability per Member by cohort.
- Line: cumulative unredeemed points, 2017 to 2018.
- Cards: Redemption Rate 1.54%, CDN per Point 0.18.
- Drill-through from any cohort to a month-grain detail page (aggregated, no Loyalty Numbers shown).

**Page 5 — Decisions.** Title: *"Who · What · Where"*
- Three columns, one per question. Each recommendation as a card with **Owner · Action · Expected effect · Evidence page**.
- A "Re-run the promotion in 2019" box with the redesign: tapered bonus, redemption milestone at 90 days, target year-one churn ≤ 5%.
- A small "What we would measure next" box: month-6 to month-9 engagement, first-redemption rate, win-back conversion.

### Windows constraint

Power BI Desktop runs only on Windows. The PBIX must be produced there. Options in order:
1. A teammate with a Windows laptop owns the PBIX. Best.
2. No Windows: upload `1.data/cleaned/AnganiAir_Model.xlsx` to Power BI Service (Get data → Files). Open the semantic model, choose Edit data model, create the two relationships and paste the measures. Build the report in the browser.
3. If web modelling is unavailable: upload `clean_flat_activity_customers.csv` as a single table. Relationships are not needed. Most measures above work; drop the time-intelligence ones and use Year columns directly.

---

## 8. Three people, 120 minutes

**Minute 0 to 2, before anything else:** who has Windows? That person is A.

| Role | Owns | 0–20 | 20–70 | 70–100 | 100–120 |
|---|---|---|---|---|---|
| **A · Builder** | The PBIX, alone | Load the three clean CSVs, relationships, mark date table, paste all DAX, check the validation numbers in Section 7 | Build Pages 1, 2, 4 | Build Pages 3, 5, drill-through, synced slicers | Freeze at 105. Save. Export PDF backup. Email PBIX to bidasanalytics@gmail.com |
| **B · Designer / Analyst** | Look, titles, correctness | Set the two-colour theme. Wireframe the five pages on paper from Section 7 | Sit with A. Write every visual title as an insight sentence. Check every number against Section 3 control totals | Tooltip pages, formatting, alignment. Test hover and drill on every visual | Second pair of eyes on all five pages. Delete any visual that does not carry an insight |
| **C · Lead / Storyteller** | The ten minutes and the score | Send the WhatsApp number to organisers. Turn Section 9 into speaker notes | Write the Page 5 recommendation cards (owner, action, effect). Prepare the Section 10 answers | Rehearse alone with a timer, twice, target 8:00 | One full run with A and B on the real PBIX. Confirm roles: B clicks, C talks, A takes questions |

Rules:
- Nobody except A opens the PBIX. B and C review from PDF exports.
- No sixth page. No new visual after minute 100.
- Any number on a slide that does not match Section 3 or Section 5 gets removed, not argued about.

---

## 9. The ten-minute pitch

C speaks. B drives the screen. A stands by for questions. Target 8:00, leaving 2:00.

**0:00 – 0:45 Hook (Page 1 on screen).**
"In 2018 Angani Air flew 62,000 more flights than in 2017, up 28%. Seventy-two percent of that growth came from 971 people, six percent of the programme, recruited in one three-month promotion. Then, between October and December, 104 of them cancelled. We know why, and we know how to stop it."

**0:45 – 3:00 What happened (Pages 1, 2).**
Promo members fly 46 times a year. Standard joiners from the same year fly 8. The mechanic was a 50% points bonus: 1.5 points per kilometre instead of 1. Show the monthly line: engagement at 8 flights a month all summer, then 2.8 in September. Show the cancellation columns: 4 in August, then 30, 31, 43. Median tenure at cancellation is exactly 8 months. "The offer ended, the flying stopped, and a month later they left. And the people who left were flying 40 times a year."

**3:00 – 5:30 Why it matters (Pages 3, 4).**
Two things the numbers say that nobody expects. First, demographics tell you nothing. Show the four flat bar charts. Every card tier, province, education level, marital status flies about 30 times over two years. CLV has zero correlation with flying. "If you are allocating loyalty budget by segment, you are guessing." Second, redemption is the retention lever. Show the two bars: 5% churn among redeemers, 41% among members who never redeemed. Then Page 4: promo members banked CDN 18,700 of points each and redeemed almost none. Across the programme 98.5% of points are never used, about CDN 141 million. "That is either a liability on your balance sheet or proof that members do not value the currency. Either way it is a problem you can fix."

**5:30 – 8:00 What to do (Page 5).**
Who: retained promo members and every 2018 joiner who has never redeemed. What: force a first redemption inside 90 days; re-run the promotion with a tapered bonus instead of a cliff; win back the 115 cancelled high flyers. Where: shift budget from segment acquisition to months 6 to 9 of the member lifecycle and to redemption incentives, flat across regions. Close: "Run the promotion again. It works. But taper the bonus and make them redeem once. That turns cheap acquisition into retained high-value flyers."

**8:00 – 8:45 Method.**
"We removed 1,922 duplicate rows and aggregated to member-month grain. We compared the promotion with people who joined in 2018 without it, not with the legacy base. Every number reconciles to the source files. We did not use CLV as a value measure because it does not correlate with behaviour, and we can show you that."

**8:45 – 10:00 Questions.**

Do not: walk through pages, read visual titles aloud, explain what a slicer does, apologise for the data.

---

## 10. Questions we will get, and the answers

| Question | Answer |
|---|---|
| "46 flights a year? Really?" | It is the whole cohort, not outliers. Median 44, interquartile range 32 to 58. 95% of promo members flew at least once after April. |
| "Is that fair? Legacy members fly 16." | That is why we compare with 2018 standard joiners at 8.4, not with legacy. Same year, same programme, different offer. |
| "Why do you say CLV is useless?" | Not useless, wrong tool. It is lifetime invoice history. For someone who joined in March 2018 it cannot describe their 2018 flying. Its correlation with flights is -0.005. We measure value from flights, distance, and points. |
| "Where does CDN 0.18 per point come from?" | Total redemption cost 2.21M divided by total points redeemed 12.3M, across the whole dataset. |
| "Is the 141M liability real?" | It is the unredeemed balance at the observed redemption value. Whether it is booked as liability depends on accounting policy and expiry rules we do not have. Either it is a cost waiting to happen or a currency members ignore. |
| "Does redemption cause retention, or do engaged people just redeem?" | Both are true and we say so. But redemption is the lever the airline controls. A first-redemption nudge is cheap to test. |
| "How do you know the bonus ended in September?" | We infer it. Earn rate is 1.5 all year, but flights per member drop 70% in September and cancellations spike from October, with median tenure 8 months. That pattern is a time-boxed incentive ending. Management can confirm the actual terms. |
| "What about the 4,238 missing salaries?" | All of them are College-educated members, so it is a systematic gap. We kept the members and did not use salary in any headline figure. |
| "Why did you drop 1,922 rows?" | They were exact duplicates. Keeping them double-counts 7,490 flights. |

---

## 11. Things we say out loud so nobody can catch us

- CLV and Salary have quality problems; we do not lean on them.
- The bonus end date is inferred from behaviour, not from the data dictionary.
- Redemption and retention are correlated; we present redemption as an intervention point, not a proven cause.
- The dataset is adapted from a public airline dataset and all members are in Canada; we do not pretend otherwise.
- We used AI to help with analysis and DAX, and every number here has been reproduced from the source CSVs.

---

## 12. Files

| Path | What |
|---|---|
| `0.docs/Moringa Angani BI Hackathon Case Study.pdf` | The brief |
| `0.docs/TEAM_PLAYBOOK.md` | This document |
| `2.models/clean_data.py` | Cleaning pipeline: source CSVs → clean_*.csv, xlsx, flat table |
| `2.models/validate.py` | Control-total checks on the cleaned files; run before and after loading into Power BI |
| `2.models/analyze.py` | Reproduces every finding in Section 5 |
| `1.data/raw/Customer Loyalty History.csv`, `Customer Flight Activity.csv`, `Calendar.csv` | Source, do not edit |
| `1.data/cleaned/clean_customers.csv`, `clean_activity.csv`, `clean_calendar.csv` | Load these into Power BI |
| `1.data/cleaned/AnganiAir_Model.xlsx` | Browser-upload fallback |
| `1.data/cleaned/clean_flat_activity_customers.csv` | Single-table fallback |
| `CONTRIBUTING.md`, `SECURITY.md` | Team standards; no member-level data leaves the team |
