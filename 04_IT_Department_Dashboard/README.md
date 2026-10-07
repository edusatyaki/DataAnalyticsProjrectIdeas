# 04 · IT Department Spend Dashboard (Power BI)

**Module:** Power BI  **Dataset:** [Microsoft IT Spend Analysis sample](https://github.com/microsoft/powerbi-desktop-samples/blob/main/powerbi-service-samples/IT%20Spend%20Analysis%20Sample-no-PV.xlsx), data © obviEnce (attribution required, see below)
**Column profile:** [DATA_PROFILE.md](DATA_PROFILE.md)

## Files in `data/`

The original `.xlsx` keeps all its data **inside the Power Pivot model**. Its only visible sheet is a licence note, so opening it in Excel shows nothing. The model's 8 tables are exported here as CSVs, which form a ready-made **star schema**:

| Table | Rows | Key | Columns |
|---|---|---|---|
| **`Fact.csv`** | 166,216 | (fact) | `Date, Value, Department, Cost Element ID, Country/Region ID, Business Area ID, IT Sub Area ID, Scenario ID` |
| `Date.csv` | 48 | `Date` | `Year, Period, Month` (2011–2014, month-start dates) |
| `Department.csv` | 471 | `Department` | `VP` (63 VPs) |
| `Cost_Element.csv` | 253 | `Cost Element ID` | `Cost element name, Cost Element Group` (7), `Cost Element Sub Group` (25) |
| `Country_Region.csv` | 52 | `Country/Region ID` | `Country/Region, Sales Region` (6) |
| `Business_Area.csv` | 7 | `Business Area ID` | `Business Area` |
| `IT_Area.csv` | 40 | `IT Sub Area ID` | `IT Area` (5), `IT Sub Area` |
| `Scenario.csv` | 5 | `Scenario ID` | `Actual, Plan, LE1, LE2, LE3` (LE = Latest Estimate) |

`IT_Spend_Analysis_Sample.xlsx` is the untouched original. In Power BI Desktop you can also import it directly with *File → Import → Power Query, Power Pivot, Power View*.

## What the data check found

- Every fact row falls in **2014** (12 months), even though the Date table covers 2011–2014.
- `Value` ranges from −68.9M to +58.2M. Negatives are credits or reversals, so keep them in the sums.
- **Scenario is the key idea.** Each cost line appears once per scenario (Actual / Plan / LE1–3). Never sum `Value` without a Scenario filter, or you'll count spend several times over.
- IDs were exported as decimals (`5.0`). Set them to Whole Number in Power Query so the relationships match.

## Step-by-step approach

1. **Load** all 8 CSVs. In Power Query, set ID columns to Whole Number and `Date` to Date.
2. **Model view:** create 7 one-to-many relationships from the dimension tables to `Fact`, with single-direction filtering. Mark `Date` as the date table.
3. **DAX measures:**
   ```DAX
   Actual   = CALCULATE(SUM(Fact[Value]), Scenario[Scenario] = "Actual")
   Plan     = CALCULATE(SUM(Fact[Value]), Scenario[Scenario] = "Plan")
   Variance = [Actual] - [Plan]
   Var %    = DIVIDE([Variance], [Plan])
   Actual YTD = TOTALYTD([Actual], 'Date'[Date])
   Latest Estimate = CALCULATE(SUM(Fact[Value]), Scenario[Scenario] = "LE3")
   ```
4. **Page 1 – Overview:** KPI cards (Actual, Plan, Variance, Var %), a monthly Actual vs Plan line chart, and a variance waterfall by IT Area.
5. **Page 2 – Where the money goes:** a treemap of Cost Element Group › Sub Group, a filled map by Country/Region, and a bar chart by Business Area.
6. **Page 3 – Accountability:** a matrix of VP › Department with Actual, Plan and Var %. Use conditional formatting to turn overspend red, and add a Top-N filter for the 10 departments with the biggest overspend.
7. **Page 4 – Forecast accuracy:** compare LE1 → LE2 → LE3 → Actual to see whether estimates improved over the year.
8. **Interactivity:** slicers for Region, IT Area and Business Area, plus a drill-through from IT Area to a department detail page and tooltips showing Var %.
9. **Insights:** answer "Is IT over budget, where, and who owns it?"

## KPIs

Total Actual · Plan · Variance & Var % · YTD spend · overspending departments · spend by IT Area/Region · forecast error by LE

## Attribution (required by the data owner)

> This workbook and related data is provided by Obvience (www.obvience.com). Any visualization pages must carry the notice: **obviEnce ©**.

## Deliverables

`IT_Spend_Dashboard.pbix` (3–4 pages) and screenshots in the README.
