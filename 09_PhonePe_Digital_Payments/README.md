# 09 · PhonePe Digital Payments Analysis (Python)

**Module:** Python  **Dataset:** [PhonePe Pulse](https://github.com/PhonePe/pulse), official aggregate data (CDLA-Permissive-2.0), **2018 Q1 – 2026 Q2**, 36 states/UTs, ~780 districts
**Column profile:** [DATA_PROFILE.md](DATA_PROFILE.md)

## How the data was prepared

Pulse publishes ~11,000 small JSON files (`data/<aggregated|map|top>/<transaction|user|merchant>/…/state/<state>/<year>/<quarter>.json`). [`scripts/flatten_pulse.py`](scripts/flatten_pulse.py) turns the state-level files into 9 tidy CSVs. Re-run it to refresh:

```bash
git clone --depth 1 https://github.com/PhonePe/pulse.git
python scripts/flatten_pulse.py pulse/data data
```

Writing your own JSON → DataFrame extraction is part of the classic version of this project. Use the script as a reference answer, not a shortcut.

## Files in `data/`

| File | Rows | Grain | Columns |
|---|---|---|---|
| `aggregated_transaction.csv` | 3,671 | state × quarter × type | `state, year, quarter, transaction_type` (P2P / Retail / Utility), `count` |
| `aggregated_user.csv` | 1,224 | state × quarter | `registered_count` (users) |
| `aggregated_merchant.csv` | 1,178 | state × quarter | `registered_count` (merchants) |
| `map_transaction.csv` | 26,616 | district × quarter | `district, count, amount` (₹) |
| `map_user.csv` | 26,622 | district × quarter | `district, registered_count` |
| `map_merchant.csv` | 24,737 | district × quarter | `district, registered_count` |
| `top_transaction.csv` | 10,200 | top-10 districts per state-quarter | `entity, count` |
| `top_user.csv` / `top_merchant.csv` | 10,200 / 9,732 | top-10 districts | `entity, registered_count` |

## What the data check found (the schema has changed)

- **The current Pulse schema has no `amount` at state level.** `aggregated_transaction` gives **counts only**, split into P2P / Retail / Utility (older tutorials show categories like "Recharge & bill payments" with amounts). **Rupee value is only in `map_transaction`**, so sum districts to get state or India totals.
- **App opens and device brands (`usersByDevice`) are no longer published.** Those classic "brand share" charts can't be built from current data, which is the "demographic data may need a separate source" note in the bootcamp sheet.
- 2026 has only Q1–Q2. Use full years (2018–2025) for year-on-year comparisons.
- State names are slugs (`andaman-&-nicobar-islands`, `uttar-pradesh`). Map them to proper names, and to the state names in an India GeoJSON for choropleths. District names end in " district".
- Merchant data starts later than user data for some states (fewer rows).

## Step-by-step approach

1. **Extraction (if building it yourself):** walk the folders with `os.walk`/`pathlib`, `json.load` each file, append to lists and build DataFrames. Compare with the provided CSVs.
2. **Clean:** a state-name mapping dict, a `period = pd.PeriodIndex(year=…, quarter=…, freq='Q')` column, and a check for duplicates and missing quarters.
3. **Optional SQL step** (the classic project uses MySQL/PostgreSQL): load the CSVs into tables with `SQLAlchemy` / `to_sql` and run the aggregations in SQL.
4. **Analysis questions:**
   - India's total transaction value and count per quarter (sum of `map_transaction`), and its CAGR from 2018 to 2025
   - Mix of P2P vs Retail vs Utility counts, and how it shifted over time
   - Top 10 states and districts by value; fastest-growing states (YoY %)
   - Average transaction value (`amount / count`) by state: where are payments larger?
   - Users per state against value per user (an engagement proxy)
   - Merchant growth vs user growth: where is merchant acceptance lagging?
   - The COVID-19 effect: compare 2020 Q2 with the trend
5. **Visuals:**
   - A plotly **India choropleth** (state GeoJSON) with a year/quarter slider
   - Treemap of district value
   - Line charts of growth
   - Stacked area of the transaction-type mix
6. **Dashboard (optional):** a Streamlit app with Year, Quarter, State and Metric selectors and a map. This is the standard deliverable for this project.
7. **Insights:** 6–8 findings for a PhonePe business team, such as where to focus merchant onboarding.

## Deliverables

`phonepe_analysis.ipynb`, an optional `app.py` (Streamlit), and charts plus insights in the README.
