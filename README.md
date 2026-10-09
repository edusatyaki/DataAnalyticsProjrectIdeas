# Data Analytics Project Ideas: 13 Bootcamp Projects, Data Included

Thirteen portfolio projects across **Excel → Power BI → SQL → Python → Statistics & EDA → Generative AI**. Every project folder has:

- `data/`: the dataset, already downloaded (no Kaggle login needed)
- `DATA_PROFILE.md`: **every column of every file** with its type, missing %, unique count and min/max or top values
- `README.md`: a complete project guide in 8 sections:

| # | Section | What it contains |
|---|---|---|
| 1 | **Project description** | Business context, objective, stakeholders, key questions |
| 2 | **Dataset** | Files, grain, columns |
| 3 | **Data cleaning** | Every issue found in the real data and the exact fix (Excel / Power Query / DAX / SQL / pandas) |
| 4 | **EDA** | Univariate → bivariate → multivariate → time analysis, plus the dashboard layout |
| 5 | **Testing** | (A) data-validation tests with pass conditions, (B) hypothesis tests with H₀, method and the **actual result** |
| 6 | **Observations** | 7–9 findings with real numbers computed from this data |
| 7 | **Recommendations** | Actions backed by the observations |
| 8 | **Deliverables** | What to submit |

Every number in the Observations and Testing sections was computed from the files in this repo. Reproduce them with `python tools/reference_findings.py` (instructor answer key; students should derive them on their own first).

| # | Project | Module | Dataset | Size | Data notes |
|---|---|---|---|---|---|
| 01 | [National Air Quality](01_National_Air_Quality/) | Excel | Air Quality in India, 2015–16 (CPCB/Kaggle) | 6.3k city-days, 10 cities (+ hourly) | 8–73% missing per pollutant; Mumbai has no AQI; 109 AQI > 500, half from an Ahmedabad CO sensor error |
| 02 | [US Healthcare](02_US_Healthcare/) | Excel | Healthcare Dataset (Kaggle) | 55.5k admissions | **Synthetic**; 534 duplicates; 108 negative bills |
| 03 | [India CPI Inflation](03_India_CPI_Inflation/) | Excel | MoSPI CPI via IndiaInflation.com | 2013–Aug 2026 national; 2025+ state/category/item | **Base 2024 = 100**; first line is a comment |
| 04 | [IT Department Dashboard](04_IT_Department_Dashboard/) | Power BI | Microsoft IT Spend sample (obviEnce) | 166k fact rows, 7 dims | Exported from the hidden Power Pivot model; filter by Scenario |
| 05 | [E-commerce Orders](05_Ecommerce_Orders_PowerBI/) | Power BI | Olist (uses data in 07) | 100k orders | Stand-in for the Bangalore mobile-accessories file |
| 06 | [Retail Store](06_Retail_Store_SQL/) | SQL | Retail Shop Case Study (3 tables) | 23k transactions | Mixed date formats; returns = negative rows; 2-column join |
| 07 | [E-commerce Business](07_Ecommerce_Business_SQL/) | SQL | Olist Brazilian E-commerce (9 tables) | 100k orders | `customer_unique_id` ≠ `customer_id`; fan-out joins |
| 08 | [COVID-19 Analysis](08_COVID19_Analysis/) | Python | Johns Hopkins CSSE time series | 1,143 days × 289 regions (+ US counties) | Wide & cumulative; recovered stops in Aug 2021 |
| 09 | [PhonePe Digital Payments](09_PhonePe_Digital_Payments/) | Python | PhonePe Pulse (official) | 2018 Q1–2026 Q2, 780 districts | JSON flattened to 9 CSVs; ₹ amount only at district level |
| 10 | [Loan Default Analysis](10_Loan_Default_Analysis/) | Stats & EDA | Loan Default Prediction (Kaggle) | 255k loans | Clean but near-synthetic; 11.6% default |
| 11 | [Pro Kabaddi League](11_Pro_Kabaddi_League/) | Stats & EDA | kabaddiPy (S1–S10) | 1,064 matches + player stats | Kaggle file was broken, so rebuilt from kabaddiPy |
| 12 | [Superstore Sales](12_Superstore_Sales/) | Stats & EDA | Tableau Sample Superstore | 9,994 order lines | cp1252 encoding; discount kills profit |
| 13 | [Credit Risk Modelling](13_Credit_Risk_Modelling/) | Generative AI | Credit Risk Dataset (Kaggle) | 32.6k loans | 21.8% default; leakage via grade/rate; ML + LLM layer |

## Run it in the cloud (GitHub Codespaces)

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/edusatyaki/DataAnalyticsProjrectIdeas?quickstart=1)

Click the badge. Nothing to install on your laptop. The first build takes about 5 minutes; later starts are quick. You get:

- **Python 3.12** with everything in [`requirements.txt`](requirements.txt): pandas, seaborn, plotly, scipy, statsmodels, scikit-learn, xgboost, shap, streamlit, JupyterLab, duckdb, the Anthropic SDK
- **PostgreSQL 16** for the SQL projects (06–07), already running. Type `psql` in the terminal to connect (database `analytics`, user/password `analyst`). Load CSVs with `\copy`. The SQLTools sidebar is already connected.
- **Forwarded ports:** Streamlit on 8501, JupyterLab on 8888 (`jupyter lab --ip 0.0.0.0 --no-browser`)
- **Project 13 (LLM):** add `ANTHROPIC_API_KEY` as a [Codespaces secret](https://github.com/settings/codespaces). The Codespace asks for it when you create it.

Excel and Power BI (01–05) still need the desktop apps. Download the `data/` folder for those, or do the cleaning in pandas first.

Working locally instead: `python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`.

## Suggested order

Do them in module order. Each one reuses skills from the one before:

1. **Excel (01–03):** cleaning in Power Query, pivots, lookups, dashboards
2. **Power BI (04–05):** star schema, relationships, DAX, multi-page reports
3. **SQL (06–07):** joins, CTEs, window functions, cohorts/RFM
4. **Python (08–09):** pandas reshaping, time series, JSON, maps, Streamlit
5. **Stats & EDA (10–12):** distributions, hypothesis tests, effect sizes, storytelling
6. **GenAI (13):** ML model + LLM explanations and Q&A

## The same 8 steps for every project

1. **Frame the questions.** Write 6–10 business questions before touching the data.
2. **Read `DATA_PROFILE.md`.** Know the grain (what one row is), keys, data types and missing %.
3. **Audit.** Look for duplicates, impossible values, mixed formats and how the tables join (check for row fan-out).
4. **Clean and document every decision**, e.g. "dropped 534 duplicates", "capped AQI at 500".
5. **Feature engineering:** dates → year/month/quarter, bands, ratios, flags.
6. **Analyse.** Answer each question with a number and a chart.
7. **Present.** Build a dashboard or notebook with a clear story, not a chart dump.
8. **Recommend.** Write 3–5 actions, each backed by a number. Add limitations.

**Portfolio README template for each project:** Problem → Data → Approach → Key insights (with numbers) → Dashboard screenshots → Recommendations → Tools used.

## Repository notes

- **Compressed files:** `olist_geolocation_dataset.csv.gz` (07) is gzipped to stay under GitHub's 100 MB file limit. pandas reads them directly; on Windows, unzip with 7-Zip for Excel.
- **Regenerate the profiles:** `python tools/profile_datasets.py` (needs pandas).
- **Rebuild prepared data:** `09_.../scripts/flatten_pulse.py` (PhonePe JSON → CSV) and `11_.../scripts/build_matches.py` (kabaddiPy JSON → CSV).
- **Exact bootcamp files:** the source sheet says none of these links is confirmed as the exact Coding Ninjas file. They are public equivalents with the same structure and purpose. Project 05 in particular is a stand-in.

## Sources & licences

| Dataset | Source | Licence / terms |
|---|---|---|
| Air Quality India | [Kaggle – rohanrao](https://www.kaggle.com/datasets/rohanrao/air-quality-data-in-india) (CPCB) | See Kaggle page |
| Healthcare | [Kaggle – prasad22](https://www.kaggle.com/datasets/prasad22/healthcare-dataset) | See Kaggle page |
| CPI India | [IndiaInflation.com](https://indiainflation.com/data) (MoSPI), [data.gov.in](https://www.data.gov.in/catalog/all-india-consumer-price-index-ruralurban-0) | Credit IndiaInflation.com |
| IT Spend | [Microsoft Power BI samples](https://github.com/microsoft/powerbi-desktop-samples) | Data © obviEnce, attribution required |
| Olist | [Kaggle – olistbr](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) | CC BY-NC-SA 4.0 |
| Retail Shop Case Study | [Kaggle – amark720](https://www.kaggle.com/datasets/amark720/retail-shop-case-study-dataset), mirror [mrinalcs](https://github.com/mrinalcs/sql-retail-data-analysis) | See source |
| COVID-19 | [JHU CSSE](https://github.com/CSSEGISandData/COVID-19) | CC BY 4.0 |
| PhonePe Pulse | [PhonePe/pulse](https://github.com/PhonePe/pulse) | CDLA-Permissive-2.0 |
| Loan Default | [Kaggle – nikhil1e9](https://www.kaggle.com/datasets/nikhil1e9/loan-default) | See Kaggle page |
| Pro Kabaddi | [kabaddiPy](https://github.com/kabaddiPy/kabaddiPy) | See repo |
| Superstore | [Tableau sample data](https://public.tableau.com/app/learn/sample-data), copy via [Kaggle – vivek468](https://www.kaggle.com/datasets/vivek468/superstore-dataset-final) | Tableau sample |
| Credit Risk | [Kaggle – laotse](https://www.kaggle.com/datasets/laotse/credit-risk-dataset) | See Kaggle page |

The datasets are redistributed here for teaching. All rights stay with the original owners.

— Satyaki Das
