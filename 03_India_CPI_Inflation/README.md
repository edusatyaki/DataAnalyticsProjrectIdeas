# 03 · India CPI Inflation Analysis

**Module:** Excel  **Dataset:** CPI from MoSPI via [IndiaInflation.com](https://indiainflation.com/data) (credit IndiaInflation.com). Official source: [data.gov.in](https://www.data.gov.in/catalog/all-india-consumer-price-index-ruralurban-0).  **Column profile:** [DATA_PROFILE.md](DATA_PROFILE.md)

---

## 1. Project description

**Business context.** Inflation drives RBI interest-rate decisions, wage negotiations and household budgets. The RBI targets 4% CPI inflation with a tolerance band of 2%–6%. A research desk wants an Excel tool that tracks inflation since 2013, explains what drives it today (categories and items) and shows where it is highest (states).

**Objective.** Build a clean CPI workbook, recompute inflation from index values, and present a dashboard and memo answering "what is driving inflation now?".

**Stakeholders.** Economists, policy analysts, finance teams and anyone pricing contracts.

**Key questions**
1. How has headline inflation moved since 2014? Which periods breached the 6% upper band?
2. Does rural inflation differ from urban?
3. Which categories and items are driving the latest inflation?
4. Which states have the highest and lowest inflation?
5. How volatile are food items compared with other items?

## 2. Dataset

| File | Rows | Coverage | Columns |
|---|---|---|---|
| `cpi-national.csv` | 164 | **Jan 2013 – Aug 2026** | `year, month, combined_index, rural_index, urban_index, combined_inflation, rural_inflation, urban_inflation` |
| `cpi-categories.csv` | 720 | Jan 2025 – Aug 2026 | `category` (12 divisions), `year, month, sector` (Combined/Rural/Urban), `index_value, inflation_rate` |
| `cpi-states.csv` | 2,140 | Jan 2025 – Aug 2026 | `state` (36), `year, month, sector, index_value, inflation_rate` |
| `cpi-items.csv` | 7,160 | Jan 2025 – Aug 2026 | hierarchy `category › sub_group › class › sub_class › item` (358 items), `code, year, month, index_value, inflation_rate` |

**Key definition.** Inflation (YoY %) = (Index this month ÷ Index same month last year − 1) × 100. The index base is **2024 = 100**.

---

## 3. Data cleaning

| # | Step | How (Excel / Power Query) | Notes |
|---|---|---|---|
| 1 | Remove the comment line | Power Query → Remove Top Rows = 1 → Use First Row as Headers | Every file starts with `# source…` |
| 2 | Build a real date | `=DATE(year, month, 1)`, formatted `mmm-yy` | Needed for charts and lookups |
| 3 | Fix data types | Index and inflation = Decimal, year and month = Whole Number | |
| 4 | Understand the blanks | Filter blank `inflation_rate` | National: 2013 has none (no 2012 base). Categories and items: all of 2025 is blank (new base-2024 classification). These are **structural blanks, not errors**, so don't fill them |
| 5 | Check the base year | Average index for 2024 should be ≈ 100 | Confirms base 2024 = 100. Never mix with an old base-2012 series without rebasing |
| 6 | Shorten long category names | Lookup table, e.g. "Personal care, social protection and misc." → "Personal care & misc." | Readable charts |
| 7 | Clean state names | Trim; "NCT of Delhi" → "Delhi" | Needed for map charts |
| 8 | Recompute inflation | `=(C14/C2-1)*100`, or `XLOOKUP` of the same month last year | Compare with the given column. Differences should be tiny (rounding) |
| 9 | Helper flags | `Above_6 = inflation>6`, `Below_2 = inflation<2` | For counting band breaches |

---

## 4. Exploratory data analysis (EDA)

**Trend (national, 2014–2026)**
- Line chart of Combined, Rural and Urban inflation with the **2% and 6% band lines**
- Annual average inflation (pivot by year), months above 6% each year (`COUNTIFS`)
- Peak and lowest months (`MAXIFS`/`MINIFS` + `XLOOKUP` for the date)

**Rural vs urban**
- Gap series `rural − urban` (column chart); correlation between the two

**Category drivers (latest month)**
- Sorted bar of category inflation (Combined sector)

**State comparison**
- Ranked bar or filled map of state inflation; count of states above 6%

**Item drill-down**
- Top 10 and bottom 10 items by YoY (`SORTBY` + `TAKE`)
- Food-only view; volatility = standard deviation of monthly inflation per item

**Dashboard**
- Slicers: Sector, Category, State, Month
- KPI cards: latest headline, rural, urban, months above 6% in the last 24, top category

---

## 5. Testing

**A. Data-validation tests**

| Test | Pass condition |
|---|---|
| Recomputed YoY = supplied YoY | Difference only from rounding, for all rows |
| 164 national months, no gaps | Distinct dates = 164, consecutive |
| 12 categories × 3 sectors × 20 months | 720 rows |
| State rows per month | Combined + Rural + Urban per state. A few UTs lack a series, so explain the 2,140 vs 2,160 gap |

**B. Statistical tests**

| Hypothesis | Test | Result |
|---|---|---|
| H₀: rural inflation = urban inflation (2014–2026) | Paired t-test on monthly pairs | Mean gap +0.14 pp, p = 0.09. **Fail to reject:** no real rural–urban difference |
| H₀: rural and urban inflation are unrelated | `CORREL` | r = 0.86. They move together strongly |
| H₀: average inflation 2020–22 = 2017–19 | Two-sample t-test on monthly values | ~6.2% vs ~3.7%. **Reject H₀** (the pandemic and commodity shock) |
| H₀: food items are as volatile as non-food items | Levene test on each item's month-to-month std of inflation (2026) | Median std 1.49 pp for food vs 0.47 pp for non-food, p ≈ 5e-9. **Reject:** food is ~3× more volatile |

---

## 6. Observations (from this data)

1. **Long-term picture:** annual average inflation was 6.7% (2014), 3.3% (2017), **6.6% (2020)**, **6.7% (2022)** and 5.0% (2024), then fell to **2.2% in 2025**.
2. **Band breaches:** months above 6% clustered in **2014 (8 months), 2020 (10) and 2022 (10)**, with **none** in 2025–2026.
3. **Extremes:** the peak was **8.6% (Jan 2014)**; the low was **0.04% (Oct 2025)**, below the RBI's 2% floor.
4. **Latest (Aug 2026):** headline **4.82%**, rural 5.23%, urban 4.31%. Back near the 4% target after the 2025 dip.
5. **Rural and urban move together** (r = 0.86); on average rural runs only 0.14 pp higher.
6. **Category drivers (Aug 2026):** *Personal care & misc.* **15.2%** (gold and silver prices), Restaurants 8.4%, Food & beverages 5.7%. The lowest are Health 1.3% and Recreation 1.7%.
7. **Items:** Silver jewellery **+107%**, Ginger +74%, Onion +48%, Garlic +44% and Gold jewellery +36% at the top; Tomato **−31%**, Coconut oil −30% and Potato −13% at the bottom.
8. **States (Aug 2026):** highest are Telangana 6.3%, Dadra-Daman 6.2%, Tamil Nadu 5.9%; lowest are Mizoram 2.4%, Delhi 2.6%, Meghalaya 2.7%. **Only 2 states are above 6%.**

## 7. Recommendations

1. **Report core inflation** (excluding food, fuel and gold) alongside headline. Gold and silver alone push "Personal care & misc." to 15%.
2. **Food supply management:** onion, garlic and ginger spikes call for buffer stocks and better cold-chain and storage to smooth seasonal swings.
3. **Policy read:** headline at 4.8% is inside the band but rising from a 2025 low, so the data argues for **holding rates rather than cutting**.
4. **State focus:** Telangana and Tamil Nadu (~6%) need local supply checks on the items driving them.
5. **Businesses:** use **~5% as the planning inflation** for 2026–27 contracts, with escalation clauses for precious-metal and food-linked inputs.

## 8. Deliverables

`CPI_Inflation_Analysis.xlsx` (Raw → Clean → Calc → Pivots → Tests → Dashboard) and a 1-page memo, "What drove inflation in the last 12 months?".
