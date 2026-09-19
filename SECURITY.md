# Security Policy — Angani Air BI Hackathon

Low-risk hackathon project, but the dataset is member-level. Treat it as personal data.

## 1. Data handling

- Source: `1.data/` from `https://smplu.link/BIHACKATHON`. Educational / hackathon use only (see `LICENSE.md`).
- `Customer Loyalty History.csv` contains quasi-identifiers: `Loyalty Number`, `Postal Code`, `City/Province`, demographics, `Salary`, `CLV`. **Do not attempt re-identification. Do not join with external data to identify individuals.**
- Share only aggregates outside the team. Never email or post row-level exports containing `Loyalty Number` + `Postal Code`. The final PBIX submission to `bidasanalytics@gmail.com` should avoid member-level tables unless needed — prefer aggregated visuals.
- Keep raw data in `1.data/`; do not upload it to public repos, gists, or AI tools that retain training data without consent.

## 2. PBIX / credential hygiene

- Remove embedded database credentials, API keys, and personal OneDrive/SharePoint paths before sharing the PBIX.
- Don't commit secrets, `.env` files, or access tokens. If one is committed accidentally, rotate it and notify the lead immediately.
- Before submitting, use Power BI's data-source settings to verify no private local paths leak in queries.

## 3. AI use

AI assistants are permitted by the brief, but: don't paste row-level PII into public prompts beyond what the task needs, and always validate AI-generated DAX, measures, and insights against source totals. The team must be able to explain every AI-assisted output during presentation.

## 4. Reporting an issue

For a suspected leak, exposed secret, or privacy concern in this repo: tell the team lead directly, remove the exposure, and rotate any affected credential. There is no separate security contact for this hackathon repo.
