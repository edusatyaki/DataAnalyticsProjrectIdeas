# 09 · PhonePe Digital Payments Analysis

**Module:** Python (pandas, plotly, optional SQL + Streamlit)  **Dataset:** [PhonePe Pulse](https://github.com/PhonePe/pulse), official aggregates (CDLA-Permissive-2.0), **2018 Q1 – 2026 Q2**, 36 states/UTs, ~780 districts  **Column profile:** [DATA_PROFILE.md](DATA_PROFILE.md)

---

## 1. Project description

**Business context.** PhonePe is one of India's largest UPI apps. Its strategy team wants to understand how digital payments have grown, where (states and districts) the value is concentrated, how usage is shifting between person-to-person (P2P) and merchant payments, and where merchant acceptance lags user adoption. That tells it where to focus merchant onboarding and marketing.

**Objective.** Extract and transform PhonePe Pulse JSON into tidy tables, analyse growth and geography, and deliver an interactive geo-dashboard (plotly / Streamlit) with insights.

**Stakeholders.** Strategy, merchant-acquisition and regional marketing teams.

**Key questions**
1. How fast have transaction value and count grown? What is the CAGR?
2. How has the mix shifted between P2P, Retail (merchant) and Utility payments?
3. Which states and districts dominate? Which are growing fastest?
4. How does average transaction value (ATV) differ by state, and how is it trending?
5. Where are users high but merchants low (onboarding opportunity)?
6. What was the COVID-19 effect, and is there quarterly seasonality?

## 2. Dataset

The raw source is ~11,000 JSON files. [`scripts/flatten_pulse.py`](scripts/flatten_pulse.py) converts them into 9 CSVs. Re-run it to refresh:

```bash
git clone --depth 1 https://github.com/PhonePe/pulse.git
python scripts/flatten_pulse.py pulse/data data
```

| File | Rows | Grain | Columns |
|---|---|---|---|
| `aggregated_transaction.csv` | 3,671 | state × quarter × type | `state, year, quarter, transaction_type` (P2P / Retail / Utility), `count` |
| `aggregated_user.csv` | 1,224 | state × quarter | `registered_count` |
| `aggregated_merchant.csv` | 1,178 | state × quarter | `registered_count` |
| `map_transaction.csv` | 26,616 | district × quarter | `district, count, amount` (₹) |
| `map_user.csv` | 26,622 | district × quarter | `registered_count` |
| `map_merchant.csv` | 24,737 | district × quarter | `registered_count` |
| `top_transaction.csv` | 10,200 | top-10 districts per state-quarter | `entity, count` |
| `top_user.csv` / `top_merchant.csv` | 10,200 / 9,732 | top-10 districts | `entity, registered_count` |

---

## 3. Data cleaning

| # | Step | Code idea |
|---|---|---|
| 1 | **Extraction** (if building it yourself): walk the folders and `json.load` each file into rows | `for f in Path(...).rglob("*.json")` → dict → `pd.DataFrame` |
| 2 | Handle schema drift: the current schema **has no `amount` in aggregated/top files** and no app opens or device brands | Take ₹ value from `map_transaction`; drop all-empty columns |
| 3 | State names are slugs (`andaman-&-nicobar-islands`) | `.str.replace('-', ' ').str.title()` + a mapping to GeoJSON names (e.g. "Delhi" → "NCT of Delhi") |
| 4 | District names end in " district" | `.str.replace(' district', '').str.title()` |
| 5 | Build a period | `pd.PeriodIndex(year=df.year, quarter=df.quarter, freq='Q')` |
| 6 | Partial year | 2026 has only Q1–Q2. Use full years (2018–2025) for YoY and CAGR |
| 7 | Merchant series starts late for 3 states (2019) | Note it; compare from 2019 |
| 8 | Duplicates and gaps | `df.duplicated(['state','year','quarter','district']).sum()` and missing-quarter check per state |
| 9 | Units | `amount` is in ₹ → convert to **₹ lakh crore** (÷ 1e12) for readability |
| 10 | Derived metrics | `ATV = amount / count`; `users_per_merchant`; YoY % by state |

**Optional SQL layer:** `df.to_sql()` into MySQL/PostgreSQL (`agg_trans`, `map_trans`, `agg_user`…) and run the aggregations in SQL. This is a common bootcamp requirement.

---

## 4. Exploratory data analysis (EDA)

**Growth**
- Yearly and quarterly value and count (line, log scale); CAGR 2018–2025; ATV trend

**Mix**
- Stacked 100% area chart of P2P / Retail / Utility share of transaction count by year

**Geography**
- **India choropleth** (plotly + state GeoJSON) of value, with a year/quarter slider
- Top 10 states and districts (bar); district treemap; top-10-district concentration
- YoY growth by state 2024 → 2025 (diverging bar)
- ATV by state (where are payments larger?)

**Users vs merchants**
- Registered users and merchants over time; users per merchant by state (high = under-served merchants)

**Events and seasonality**
- 2020 Q1–Q3 (COVID lockdown) vs trend; average share of annual value by quarter

**Dashboard (Streamlit)**
- Sidebar: Year, Quarter, Metric (value/count/users), State
- Main: KPI tiles, choropleth, top-10 tables, trend chart

---

## 5. Testing

**A. Data-validation tests**

| Test | Pass condition |
|---|---|
| Re-running the flattener gives the same row counts | 3,671 / 26,616 / … |
| District sum = state total, using counts (`map_transaction` grouped by state vs `aggregated_transaction` summed over types) | **Exactly equal for all 1,224 state-quarters** |
| No negative counts or amounts | 0 rows |
| Every state has every quarter from its first appearance | No gaps |
| GeoJSON state names all match after mapping | 0 unmatched |

**B. Statistical tests**

| Hypothesis | Method | Result |
|---|---|---|
| H₀: growth rates are equal in North-Eastern vs large states | t-test / Mann-Whitney on 2025 YoY % | 8 NE states 24–43% vs a median of 18.7% for the rest, Mann-Whitney p ≈ 1e-5. **Reject H₀** |
| H₀: no quarterly seasonality | ANOVA of quarter share (2021–2025) | Q4 ≈ 28.6% vs Q1 ≈ 21.6% of annual value, p ≈ 1e-5 (trend growth also contributes, so de-trend for a stricter test) |
| H₀: ATV is unrelated to users per merchant | Spearman correlation across states (2025) | ρ = 0.26, p = 0.13. **No significant relationship** |
| Trend | Log-linear regression of value on time → implied growth rate | Compare with CAGR |

---

## 6. Observations (from this data)

1. **Explosive growth:** transaction value rose from **₹1.6 lakh crore (2018) to ₹155.4 lakh crore (2025)**, a **~92% CAGR**. Count grew from 1.1 bn to **128.5 bn** (~97% CAGR). H1 2026 alone is ₹88.9 lakh crore.
2. **Smaller tickets, more everyday use:** ATV peaked at **₹1,827 (2020)** and fell to **₹1,209 (2025)**. UPI moved from occasional transfers to daily small purchases.
3. **Merchant payments took over:** Retail's share of transactions rose from **49% (2018) to 62% (2025)** and 63% in 2026, while P2P fell from 47% to 32%. Utility peaked at 15% in 2021 (lockdown bill payments) and is now 6%.
4. **Top states (2025 value):** Maharashtra 11.7%, Karnataka 11.6%, Telangana 10.9%, Andhra Pradesh 9.8%, Uttar Pradesh 8.7%. The southern states are over-represented relative to population.
5. **District concentration:** **Bengaluru Urban alone did ₹7.9 lakh crore** in 2025, more than double the next district (Pune ₹3.6). The top 10 of 783 districts = **18%** of value.
6. **Fastest growth is in the North-East:** 2025 YoY was Meghalaya +43%, Manipur +40%, Lakshadweep +35%, Assam +31%. The slowest were Rajasthan +13%, Tamil Nadu +16%, Puducherry +14%.
7. **Scale:** about **712 M registered users** and **51 M merchants** (Q2 2026), roughly **14 users per merchant** nationally. Ladakh (88), Lakshadweep (47) and Meghalaya (45) are merchant-starved; Delhi and UP (11) are dense.
8. **COVID effect:** value was flat between Q1 2020 (₹2.70 lakh crore) and Q2 2020 (₹2.65), then jumped **+48% in Q3 2020**. The pandemic accelerated digital adoption.
9. **Seasonality:** Q4 carries ~28.6% of annual value vs Q1 ~21.6%. Festive season and growth momentum both contribute.

## 7. Recommendations

1. **Merchant onboarding where users per merchant is high:** Ladakh, the North-East and the island UTs, where users outnumber merchants 45–88 to 1.
2. **Ride the North-East growth** with regional-language marketing and offline-merchant QR drives. These are the fastest-growing markets.
3. **Defend the south and the metros:** Bengaluru, Pune and Hyderabad are concentrated, high-value markets, so invest in merchant tools (credit, lending, analytics).
4. **Monetise everyday payments:** falling ATV and a rising Retail share support small-ticket merchant products (soundbox, credit on UPI, BNPL).
5. **Plan for Q4 peaks:** scale infrastructure and offers for festive quarters.
6. **Fill the data gaps:** demographic and device data are no longer published, so partner with surveys or internal data for user-level insights.

## 8. Deliverables

`phonepe_analysis.ipynb`, optional `app.py` (Streamlit) and SQL scripts, choropleth screenshots and an insights README.
