# 01 · National Air Quality Analysis

**Module:** Excel  **Dataset:** [Air Quality Data in India 2015–2020](https://www.kaggle.com/datasets/rohanrao/air-quality-data-in-india) (CPCB data, compiled on Kaggle)  **Column profile:** [DATA_PROFILE.md](DATA_PROFILE.md)

---

## 1. Project description

**Business context.** India has many of the world's most polluted cities. A state environment board wants to know which cities need action first, when pollution peaks, which pollutants drive the Air Quality Index (AQI), and whether reduced activity (the 2020 lockdown) actually cleans the air.

**Objective.** Build an Excel workbook that cleans 5 years of daily readings for 26 cities, analyses them and presents an interactive dashboard with evidence-based recommendations.

**Stakeholders.** Pollution control board, city administrations, public-health officials.

**Key questions**
1. Which cities have the worst air, both on average and by number of "Poor or worse" days?
2. Is air quality improving year over year?
3. Which months and seasons are worst, and how big is the seasonal swing?
4. Which pollutants move most closely with AQI?
5. How much did pollution fall during the 2020 lockdown compared with the same period in 2019?
6. How reliable is the data (coverage by city and pollutant)?

## 2. Dataset

| File | Rows | Grain | Use it for |
|---|---|---|---|
| `city_day.csv` | 29,531 | city × day | **Main file.** 26 cities, 1 Jan 2015 – 1 Jul 2020 |
| `station_day.csv` | 108,035 | station × day | Station-level drill-down (110 stations) |
| `stations.csv` | 230 | station | Lookup: StationId → name, city, state, status |
| `city_hour.csv.gz` | 707,875 | city × hour | Hour-of-day patterns (Power Query or Python) |
| `station_hour.csv.gz` | 2.59 M | station × hour | Too big for Excel (> 1,048,576 rows). Python only |

**Columns (city_day):** `City`, `Date`, 12 pollutants (`PM2.5, PM10, NO, NO2, NOx, NH3, CO, SO2, O3, Benzene, Toluene, Xylene`), `AQI`, `AQI_Bucket` (Good / Satisfactory / Moderate / Poor / Very Poor / Severe).

---

## 3. Data cleaning

| # | Step | How (Excel) | What you'll find |
|---|---|---|---|
| 1 | Import properly | Data → From Text/CSV → **Transform Data** (Power Query). Set `Date` = Date and pollutants = Decimal Number | Text dates convert cleanly (ISO format) |
| 2 | Check duplicates | Power Query → select City + Date → Keep Duplicates | **0 duplicates** |
| 3 | Measure missing values | `=COUNTBLANK(C:C)/COUNTA(A:A)` per column, plus a City × Year pivot of `COUNT(AQI)` | Xylene 61%, PM10 38%, NH3 35%, AQI 16% blank. Many cities only start in 2017–2019 |
| 4 | Decide the missing-value rule | **Don't fill pollutants with 0.** Leave them blank (pivot averages ignore blanks). Drop rows with blank AQI only for AQI analysis | Write the rule in an "Assumptions" sheet |
| 5 | Find impossible values | Filter `AQI > 500` (the official scale tops out at 500) | **543 rows**, of which **412 are Ahmedabad** |
| 6 | Investigate the outlier city | Pivot: average CO by City | **Ahmedabad's CO averages 22 mg/m³ against a median of 0.9 for the other cities.** This is a sensor or unit error that inflates its AQI |
| 7 | Treat outliers | Add `AQI_clean = MIN(AQI, 500)` and a flag column `Ahmedabad_CO_issue`. Report Ahmedabad separately, or exclude it from the city ranking | Document it. Don't delete silently |
| 8 | Add derived columns | `Year = YEAR(Date)`, `Month = TEXT(Date,"mmm")`, `Season` with `IFS` (Winter Dec–Feb, Summer Mar–May, Monsoon Jun–Sep, Post-monsoon Oct–Nov), `Is_Poor = OR(bucket="Poor","Very Poor","Severe")` | |
| 9 | Add state | `XLOOKUP` StationId → State from `stations.csv` (station_day only) | |
| 10 | Load to the Data Model | Close & Load To → PivotTable + "Add to Data Model" | Faster pivots |

---

## 4. Exploratory data analysis (EDA)

**Univariate**
- Distribution of AQI (histogram via Insert → Statistic Chart): right-skewed, with a long tail of extreme days
- `AQI_Bucket` frequency (column chart)
- Descriptive statistics per pollutant (Data Analysis ToolPak → Descriptive Statistics): mean, median, standard deviation, max

**Bivariate**
- Average AQI by City (sorted bar chart): the ranking of the worst cities
- % of Poor-or-worse days by City (100% stacked bar)
- Average AQI by Year (line): the trend
- Average AQI by Month (line or column): the seasonal cycle
- Scatter of PM2.5 vs AQI and PM10 vs AQI, with trendlines and R²

**Multivariate**
- **City × Month heat map** (pivot plus conditional formatting colour scale): shows the North Indian winter spike
- City × Year pivot of average AQI: who improved and who got worse
- Correlation matrix of all pollutants with AQI (ToolPak → Correlation)

**Event analysis**
- Lockdown window, 25 Mar – 31 May: average PM2.5, NO2 and AQI per city in 2020 against the same window in 2019, as a % change table plus a clustered bar chart

**Dashboard sheet**
- Slicers: City, Year, Season
- KPI cards: average AQI, % severe days, worst month, cleanest city, data coverage %
- Charts: monthly trend line, city ranking bar, heat map, lockdown comparison

---

## 5. Testing

**A. Data-validation tests**

| Test | Formula / method | Pass condition |
|---|---|---|
| Row count after import | `=ROWS()` | 29,531 |
| No duplicate City + Date | `=COUNTIFS(City,A2,Date,B2)>1` | 0 |
| AQI matches its bucket | Pivot of MIN/MAX AQI per bucket | Good ≤ 50, Satisfactory 51–100, Moderate 101–200, Poor 201–300, Very Poor 301–400, Severe > 400 |
| Pivot total = raw total | `SUM` of the pivot vs `SUM` of the raw column | Equal |
| Dashboard slicer check | Pick one city and recompute its average AQI with `AVERAGEIFS` | Equal |

**B. Statistical tests** (ToolPak: t-Test Two-Sample Unequal Variances)

| Hypothesis | Test | Result |
|---|---|---|
| H₀: winter (Nov–Jan) AQI = monsoon (Jul–Sep) AQI | Two-sample t-test / Mann-Whitney | Winter 233 vs monsoon 114, p < 0.001. **Reject H₀** |
| H₀: lockdown 2020 PM2.5 = same window in 2019 | Paired t-test across cities | Median city change −38%. **Reject H₀** |
| H₀: PM2.5 is unrelated to AQI | Correlation (r) with a t-test on r | r = 0.66 (PM10 r = 0.80, CO r = 0.68) |

---

## 6. Observations (from this data)

1. **Worst cities by average AQI:** Delhi 259, Patna 241, Gurugram 225, Lucknow 218. Ahmedabad shows 452, but that comes from its faulty CO readings, so treat it as a data issue, not a ranking.
2. **Share of Poor-or-worse days:** Delhi 65%, Patna 54%, Gurugram 52%, Lucknow 49%. Aizawl, Shillong, Thiruvananthapuram, Ernakulam and Coimbatore had **0%**.
3. **Steady improvement:** average AQI fell from 212 (2015) to 197 (2016), 181 (2017), 157 (2019) and 114 (H1 2020). Part of this comes from cleaner southern and north-eastern cities joining the dataset later, so check the same trend city by city.
4. **Strong seasonality:** November (242) and January (232) are the worst months; July (112) is the cleanest. Winter AQI is **about 2× monsoon AQI**.
5. **Drivers:** PM10 (r = 0.80), CO (0.68) and PM2.5 (0.66) track AQI most closely. O₃ (0.20) and NH₃ (0.25) barely do.
6. **Lockdown effect:** across all cities, 25 Mar – 31 May 2020 had **PM2.5 −44%, NO₂ −46% and AQI −44%** compared with 2019. NO₂ (mainly from traffic) fell the most.
7. **Data gaps:** PM10 and NH₃ are missing for over a third of days, so city averages for them are less reliable.

## 7. Recommendations

1. **Prioritise the Indo-Gangetic cities** (Delhi, Patna, Gurugram, Lucknow) for winter action plans that start in **October**, before the November peak.
2. **Target traffic and combustion:** the lockdown showed a 40–46% fall when vehicles stopped. This supports congestion pricing, EV push and cleaner-fuel mandates.
3. **Control dust (PM10),** the strongest AQI driver: construction-site rules and road sweeping.
4. **Audit Ahmedabad's monitoring stations.** Implausible CO values distort public reporting.
5. **Improve sensor coverage** for PM10 and NH₃. Set a target of ≥ 90% data completeness per station.
6. Issue **seasonal public-health advisories** (Nov–Jan) in the worst cities.

## 8. Deliverables

`AirQuality_Analysis.xlsx` with sheets **Raw → Clean → Assumptions → Pivots → Tests → Dashboard → Insights**, plus a one-page PDF summary.
