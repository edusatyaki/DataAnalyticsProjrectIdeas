# 03 · India CPI Inflation Analysis (Excel)

**Module:** Excel  **Dataset:** CPI series from MoSPI, via [IndiaInflation.com](https://indiainflation.com/data) (credit IndiaInflation.com when you use it). Official source: [data.gov.in CPI catalog](https://www.data.gov.in/catalog/all-india-consumer-price-index-ruralurban-0).
**Column profile:** [DATA_PROFILE.md](DATA_PROFILE.md)

> Each CSV starts with a one-line `# source …` comment. In Excel, delete row 1. In Power Query, use "Remove Top Rows = 1". In pandas, use `pd.read_csv(f, skiprows=1)`.

## Files in `data/`

| File | Rows | Coverage | Columns |
|---|---|---|---|
| `cpi-national.csv` | 164 | **Jan 2013 – Aug 2026**, monthly | `year, month, combined_index, rural_index, urban_index, combined_inflation, rural_inflation, urban_inflation` |
| `cpi-categories.csv` | 720 | Jan 2025 – Aug 2026 | `category` (12 divisions), `year, month, sector` (Combined/Rural/Urban), `index_value, inflation_rate` |
| `cpi-states.csv` | 2,140 | Jan 2025 – Aug 2026 | `state` (36 states/UTs), `year, month, sector, index_value, inflation_rate` |
| `cpi-items.csv` | 7,160 | Jan 2025 – Aug 2026 | full hierarchy `category › sub_group › class › sub_class › item` (358 items), `code, year, month, index_value, inflation_rate` |

## What the data check found

- **Base year is 2024 = 100** (the new MoSPI series). The national file links back to 2013, so its index runs from 55 to 109. Don't mix it with an old base-2012 series without rebasing. This is the "check base years" warning from the bootcamp sheet.
- **Year-on-year inflation needs the same month last year.** The national file has no rate for 2013 (first 12 rows). The category and item files have no rate for 2025, because the new base-2024 classification has no earlier year, so 60% of their `inflation_rate` is blank. The state file already supplies 2025 rates (only 4.5% blank).
- Category, state and item data only start in 2025, so long-term trends come from the national file only.
- Item-level inflation ranges from −53% to +161% (vegetables swing hard). Use the median or weights, not a simple average.

## Step-by-step approach

1. **Import** each file with Power Query, remove the comment row and build a real date: `=DATE(year, month, 1)`.
2. **Recompute inflation yourself** to show you understand it: `YoY % = (Index_t / Index_{t−12} − 1) × 100` with `XLOOKUP` or `OFFSET`. Match it against the supplied column.
3. **National trend (2013–2026):**
   - Line chart of Combined, Rural and Urban inflation
   - Mark the RBI tolerance band (2%–6%) as two flat series
   - Count the months above 6% each year with `COUNTIFS`
   - Find the peak month and the lowest month
4. **Rural vs urban gap:** add `rural_inflation − urban_inflation` and chart it. When does rural inflation lead?
5. **Category drivers (2026):** latest-month inflation by category (sorted bar). Which division is pushing headline inflation up?
6. **State comparison:** latest-month inflation by state (ranked bar or filled map), and the states above 6%.
7. **Item drill-down:** top 10 and bottom 10 items by YoY inflation in the latest month, using pivot plus `SORTBY`. Add a food-only view.
8. **Dashboard:** slicers for Sector, Category and State. Show KPI cards for latest headline inflation, months above 6% and the top inflating category.
9. **Insights:** connect findings to real events, such as 2013 food inflation, the 2020 pandemic supply shock and 2022 commodity prices.

## Deliverables

`CPI_Inflation_Analysis.xlsx` and a short memo: "What drove inflation in the latest 12 months?"
