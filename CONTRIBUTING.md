# Contributing — Angani Air BI Hackathon

## 1. Roles

Appoint: **lead** (owns WhatsApp scoring number + timekeeping), **data prep** (Python/SQL cleaning), **modeller** (Power BI relationships + DAX), **designer** (layout/interactivity), **storyteller** (narrative + presentation). Small teams double up, but one person owns validation.

## 2. Workflow

1. **Understand → Decide → Question → KPI → Storyboard → Build.** No PBIX work before the storyboard is agreed.
2. Keep source CSVs in `1.data/` immutable. Put cleaned outputs / scripts alongside with a clear name (e.g. `1.data/clean_*.csv`); never overwrite sources.
3. PBIX is binary — avoid parallel edits. One editor at a time; export a `.pbit` / PDF snapshot when handing over so others can review without locking the file.
4. Every measure needs a source check: DAX total must reconcile to a Python/SQL control total (flights ~508k, members 16,737, promo cohort 971) before it ships.

## 3. Power BI standards

- **Model:** star schema. `Customer Loyalty History` = dimension, `Customer Flight Activity` = fact, `Calendar` = date dimension. No bidirectional filters unless justified; hide key columns from report view.
- **Measures:** `Total ` / `Avg ` / `% ` prefixes, e.g. `Total Flights`, `Flights per Member`, `Avg CLV`, `Retention %`, `CDN Cost per Member`. No implicit measures; format currency/percent at the measure level.
- **Cohorts:** always provide slicers for `Enrollment Type`, `Enrollment Year-Month`, `Loyalty Card`, `Province`. Promotion impact must be shown vs a like-for-like baseline (Standard 2018 enrolments), never in isolation.
- **Design:** ≤5 pages, one message per page, executive answer first. Every visual needs a title that states the insight, filters and drill-through must aid understanding, test hover/tooltips and mobile layout.

## 4. Definition of done (maps to judging)

- [ ] Business Understanding: decisions Who/What/Where are explicitly answered.
- [ ] Design & Interactivity: filters, drill-downs, tooltips work; no dead visuals.
- [ ] Storytelling: pages flow problem → insight → conclusion.
- [ ] Decision insights: each recommendation names owner, action, expected effect — no "interesting chart" without a next step.
- [ ] Presentation: ≤10 min rehearsal done, speaker notes follow What → So what → Now what.
- [ ] Validation: AI-generated DAX/copy reviewed, understood, and explainable by the team (required by the brief).

## 5. What not to do

- Don't add a 6th page. Don't commit credentials, connection strings, or personal exports.
- Don't publish member-level data with `Loyalty Number` + `Postal Code` outside the team (see `SECURITY.md`).
- Don't present raw averages over CLV/Salary without noting skew and missing values.
