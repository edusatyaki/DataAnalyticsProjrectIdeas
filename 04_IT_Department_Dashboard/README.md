# 04 · IT Department Spend Dashboard

**Module:** Power BI  **Dataset:** [Microsoft IT Spend Analysis sample](https://github.com/microsoft/powerbi-desktop-samples/blob/main/powerbi-service-samples/IT%20Spend%20Analysis%20Sample-no-PV.xlsx), data © obviEnce  **Column profile:** [DATA_PROFILE.md](DATA_PROFILE.md)

---

## 1. Project description

**Business context.** The CIO of a global company must explain the year's IT spending to the CFO: did IT stay within its plan, which areas overspent, who is accountable, and how good were the mid-year forecasts? Spending is tracked against a **Plan** and three **Latest Estimates (LE1–LE3)** made during the year.

**Objective.** Build a multi-page Power BI report on a star-schema model that compares Actual vs Plan, drills from IT Area down to VP and department, and measures forecast accuracy.

**Stakeholders.** CIO, CFO / finance controllers, VPs who own cost centres.

**Key questions**
1. What is total actual IT spend against plan? What are the variance and variance %?
2. Which IT areas, business areas, regions and cost groups overspent?
3. In which months did the overspend happen?
4. Which VPs and departments are over or under budget?
5. Did the forecasts (LE1 → LE3) get closer to the actual?

## 2. Dataset: a star schema (8 CSVs exported from the workbook's Power Pivot model)

| Table | Rows | Key | Columns |
|---|---|---|---|
| **`Fact.csv`** | 166,216 | (fact) | `Date, Value, Department, Cost Element ID, Country/Region ID, Business Area ID, IT Sub Area ID, Scenario ID` |
| `Date.csv` | 48 | `Date` | `Year, Period, Month` (2011–2014) |
| `Department.csv` | 471 | `Department` | `VP` (63 VPs) |
| `Cost_Element.csv` | 253 | `Cost Element ID` | `Cost element name, Cost Element Group` (7), `Cost Element Sub Group` (25) |
| `Country_Region.csv` | 52 | `Country/Region ID` | `Country/Region, Sales Region` (6) |
| `Business_Area.csv` | 7 | `Business Area ID` | `Business Area` |
| `IT_Area.csv` | 40 | `IT Sub Area ID` | `IT Area` (5), `IT Sub Area` |
| `Scenario.csv` | 5 | `Scenario ID` | Actual, Plan, LE1, LE2, LE3 |

`IT_Spend_Analysis_Sample.xlsx` is the untouched original (its data is in Power Pivot, so it looks empty in plain Excel).

---

## 3. Data cleaning (Power Query)

| # | Step | Why |
|---|---|---|
| 1 | Load all 8 CSVs; **promote headers** | |
| 2 | Change every `… ID` column and `Department` to **Whole Number** | They were exported as `5.0`; relationships fail on text or decimal mismatches |
| 3 | `Date` → Date type in both Fact and Date | |
| 4 | Check for orphan keys: merge Fact with each dimension (Left Anti join) | **0 orphans.** Every fact row matches a dimension |
| 5 | Check duplicate keys in dimensions (Group By key → count > 1) | Dimension keys must be unique for 1:* relationships |
| 6 | Note that **all facts fall in 2014** although `Date` covers 2011–2014 | Filter the report to 2014, or keep the Date table but show 2014 only |
| 7 | Keep negative `Value`s | Credits and reversals are real accounting entries. Don't delete them |
| 8 | Rename columns to business-friendly names; hide the ID columns in Report view | Clean field list |
| 9 | Add a `Month Name` sort-by-`Period` in Date | Months sort Jan → Dec, not alphabetically |

**Model view.** Create 7 one-to-many, single-direction relationships from each dimension to `Fact`. Mark `Date` as the date table.

---

## 4. Analysis (EDA in Power BI)

**DAX measures**
```DAX
Actual          = CALCULATE(SUM(Fact[Value]), Scenario[Scenario] = "Actual")
Plan            = CALCULATE(SUM(Fact[Value]), Scenario[Scenario] = "Plan")
Variance        = [Actual] - [Plan]
Variance %      = DIVIDE([Variance], [Plan])
Actual YTD      = TOTALYTD([Actual], 'Date'[Date])
Plan YTD        = TOTALYTD([Plan], 'Date'[Date])
LE1             = CALCULATE(SUM(Fact[Value]), Scenario[Scenario] = "LE1")
LE3             = CALCULATE(SUM(Fact[Value]), Scenario[Scenario] = "LE3")
LE3 Error %     = DIVIDE([LE3] - [Actual], [Actual])
Over Plan Flag  = IF([Variance] > 0, "Over", "Under")
```

**Page 1 – Executive overview:** KPI cards (Actual, Plan, Variance, Var %); monthly Actual vs Plan line; **waterfall** of variance by IT Area.
**Page 2 – Where the money goes:** treemap of Cost Element Group › Sub Group; map by Country; bar by Business Area; decomposition tree (Variance → IT Area → Sub Area → Cost Element).
**Page 3 – Accountability:** matrix VP › Department with Actual, Plan, Var %, conditional formatting (red = over), Top-N filter.
**Page 4 – Forecast accuracy:** clustered column of LE1, LE2, LE3, Plan vs Actual; error % per LE.
**Interactivity:** slicers (Region, IT Area, Business Area, Month), drill-through IT Area → detail page, tooltips with Var %, bookmarks for "Overspend story".

---

## 5. Testing

**A. Model and measure validation**

| Test | How | Pass condition |
|---|---|---|
| Totals reconcile | Card `[Actual]` vs `SUM` of Value where Scenario ID = 1 in Power Query | Equal (**858.4 M**) |
| Scenarios are never mixed | Table visual with no Scenario filter: `SUM(Value)` ≈ 4.2 B is a **wrong** number | Every measure filters Scenario |
| Relationships work | Slice by IT Area; the total of rows equals the grand total | Equal |
| No blank dimension members | A visual by each dimension shows no "(Blank)" | No blanks |
| Time intelligence | `Actual YTD` in December = full-year Actual | Equal |
| Cross-check in Excel | Pivot the CSVs and compare 3 numbers | Match |

**B. Analytical checks**
- Is the variance concentrated? A Pareto of variance by IT Sub Area shows what % of overspend comes from the top 3 sub-areas.
- Forecast-accuracy test: compare the absolute error of LE1 vs LE3. The later estimate should be smaller.

---

## 6. Observations (from this data)

1. **IT overspent:** Actual **$858.4 M** vs Plan **$811.0 M**, a variance of **+$47.4 M (+5.8%)**.
2. **One area causes all of it:** **Infrastructure** spent $249.9 M against $168.9 M planned (**+$81.1 M, +48%**). Every other IT area came in **under** plan: Functional −$24.5 M (−8.4%), BU Support −$6.5 M, Governance −$1.8 M, Enablement −$0.8 M.
3. **The same story by business area:** Infrastructure +$78.5 M (+44%). R&D (−8.5%), BU (−7.0%) and Office & Admin (−4.9%) were under.
4. **Year-end spike:** January was **27% under** plan, but **December was +$29.3 M (+45%) over**. A classic "use it or lose it" year-end spend. May (+12.7%), September (+11.3%) and November (+15.1%) were also over.
5. **By region:** the USA (+$43 M, +6.3%) and Europe (+$7.1 M, +6.8%) were over; Latin America (−13%) and Canada (−13%) were under. Africa & Asia has $0.2 M of actuals with **no plan at all**.
6. **Forecasting improved:** LE1 was 5.7% below the final actual (as bad as the Plan at −5.5%); **LE2 was within 0.1%** and LE3 within 1.0%. Mid-year re-forecasting worked.
7. **Accountability:** 25 of the 58 VPs finished over plan. One VP (Jim Wheeler) shows **−$85.9 M actual** against $36.7 M planned: large credits or reallocations that need explaining.
8. **Data oddities:** the *Administrative* cost group has a −$84 M plan but no actuals, and a few VPs have actuals with no plan. Flag these for finance.

## 7. Recommendations

1. **Run an Infrastructure spend review:** find which sub-areas and cost elements drove the +48%, and either re-baseline the plan (if growth was intended) or add approval gates.
2. **Stop the December rush:** quarterly budget release and approval for spend over a threshold in Q4.
3. **Make LE2 the official forecast checkpoint.** It was within 0.1% of the outcome.
4. **Fix planning gaps:** every cost centre with actuals (Africa & Asia, VPs with no plan) must have a plan line.
5. **Reconcile the large credits** (the −$85.9 M VP line, the Administrative plan) with finance before the report goes to the CFO.
6. **Reinvest under-spend:** the Functional (−$24.5 M) and BU Support (−$6.5 M) IT areas under-spent by ~$31 M, which could fund part of the Infrastructure need without raising the total.

## 8. Deliverables

`IT_Spend_Dashboard.pbix` (4 pages) with screenshots in the README, and a 1-page CFO brief. **Required attribution on report pages:** "Data provided by obviEnce (www.obvience.com). obviEnce ©".
