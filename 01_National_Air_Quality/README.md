# 01 · National Air Quality Analysis

**Module:** Excel  **Dataset:** [Air Quality Data in India](https://www.kaggle.com/datasets/rohanrao/air-quality-data-in-india) (CPCB data, compiled on Kaggle), trimmed to **2015–2016**  **Column profile:** [DATA_PROFILE.md](DATA_PROFILE.md)

---

## 1. Project description

**Business context.** India has many of the world's most polluted cities. A state environment board wants to know which cities need action first, when pollution peaks, which pollutants drive the Air Quality Index (AQI), and what happens during extreme pollution episodes such as Delhi's November 2016 smog.

**Objective.** Build an Excel workbook that cleans 2 years (2015–2016) of daily readings for 10 cities, analyses them and presents an interactive dashboard with evidence-based recommendations.

**Stakeholders.** Pollution control board, city administrations, public-health officials.

**Key questions**
1. Which cities have the worst air, both on average and by number of "Poor or worse" days?
2. Did air quality change from 2015 to 2016, city by city?
3. Which months and seasons are worst, and how big is the seasonal swing?
4. Which pollutants move most closely with AQI?
5. How bad was Delhi's November 2016 smog compared with the same days in 2015?
6. How reliable is the data (coverage by city and pollutant)?

## 2. Dataset

| File | Rows | Grain | Use it for |
|---|---|---|---|
| `city_day.csv` | 6,279 | city × day | **Main file.** 10 cities, 1 Jan 2015 – 31 Dec 2016 |
| `station_day.csv` | 17,182 | station × day | Station-level drill-down (29 stations) |
| `stations.csv` | 29 | station | Lookup: StationId → name, city, state, status |
| `city_hour.csv` | 150,634 | city × hour | Hour-of-day patterns |

**Google Sheets:** all four files fit in one workbook as four tabs (about 2.8 million cells against the 10 million limit), which leaves room for the derived columns in step 8. Import each with File → Import → Upload → *Insert new sheet(s)*.

**Columns (city_day):** `City`, `Date`, 12 pollutants (`PM2.5, PM10, NO, NO2, NOx, NH3, CO, SO2, O3, Benzene, Toluene, Xylene`), `AQI`, `AQI_Bucket` (Good / Satisfactory / Moderate / Poor / Very Poor / Severe).

---

## 3. Data cleaning

| # | Step | How (Excel) | What you'll find |
|---|---|---|---|
| 1 | Import properly | Excel: Data → From Text/CSV → **Transform Data** (Power Query). Set `Date` = Date and pollutants = Decimal Number. Sheets: File → Import, one tab per file | Text dates convert cleanly (ISO format) |
| 2 | Check duplicates | Power Query → select City + Date → Keep Duplicates | **0 duplicates** |
| 3 | Measure missing values | `=COUNTBLANK(C:C)/COUNTA(A:A)` per column, plus a City × Year pivot of `COUNT(AQI)` | PM10 73%, NH3 60%, Xylene 59%, AQI 30% blank. **Mumbai has no AQI at all** (no PM, NO₂, SO₂ or O₃ sensors). Gurugram, Patna and Visakhapatnam start late (AQI from Jan 2016, Oct 2015 and Jul 2016) |
| 4 | Decide the missing-value rule | **Don't fill pollutants with 0.** Leave them blank (pivot averages ignore blanks). Drop rows with blank AQI only for AQI analysis | Write the rule in an "Assumptions" sheet |
| 5 | Find impossible values | Filter `AQI > 500` (the official scale tops out at 500) | **109 rows**: Ahmedabad 51, Delhi 23, Patna 15, Lucknow 12. The highest is Ahmedabad at **1,842** |
| 6 | Investigate the outlier city | Pivot: average CO by City | **Ahmedabad's CO averages 14 mg/m³ against a median of 1.7 for the other cities.** This is a sensor or unit error that inflates its AQI. Delhi's > 500 days are real (Nov 2016 smog) |
| 7 | Treat outliers | Add `AQI_clean = MIN(AQI, 500)` and a flag column `Ahmedabad_CO_issue`. Report Ahmedabad separately, or exclude it from the city ranking. Exclude Mumbai from every AQI chart | Document it. Don't delete silently |
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
- City × Year pivot of average AQI (2015 vs 2016): who improved and who got worse
- Correlation matrix of all pollutants with AQI (ToolPak → Correlation)

**Event analysis**
- Delhi smog, 1–10 Nov: average PM2.5, PM10 and AQI in 2016 against the same window in 2015, as a % change table plus a daily line chart (Diwali fell on 30 Oct 2016)
- Hour of day (`city_hour.csv`): average PM2.5 by hour, to show the night-time build-up

**Dashboard sheet**
- Slicers: City, Year, Season
- KPI cards: average AQI, % severe days, worst month, cleanest city, data coverage %
- Charts: monthly trend line, city ranking bar, heat map, Delhi Nov 2016 episode

---

## 5. Testing

**A. Data-validation tests**

| Test | Formula / method | Pass condition |
|---|---|---|
| Row count after import | `=ROWS()` | 6,279 |
| No duplicate City + Date | `=COUNTIFS(City,A2,Date,B2)>1` | 0 |
| AQI matches its bucket | Pivot of MIN/MAX AQI per bucket | Good ≤ 50, Satisfactory 51–100, Moderate 101–200, Poor 201–300, Very Poor 301–400, Severe > 400 |
| Pivot total = raw total | `SUM` of the pivot vs `SUM` of the raw column | Equal |
| Dashboard slicer check | Pick one city and recompute its average AQI with `AVERAGEIFS` | Equal |

**B. Statistical tests** (ToolPak: t-Test Two-Sample Unequal Variances)

| Hypothesis | Test | Result |
|---|---|---|
| H₀: winter (Nov–Jan) AQI = monsoon (Jul–Sep) AQI | Two-sample t-test / Mann-Whitney | Winter 266 vs monsoon 147, p < 0.001. **Reject H₀** |
| H₀: average AQI in 2015 = 2016 (same city) | Paired t-test across the 7 cities with both years | Patna −28%, Lucknow +20%, others within ±13%; p = 0.45. **Fail to reject H₀**: no overall change in 2 years |
| H₀: PM2.5 is unrelated to AQI | Correlation (r) with a t-test on r | r = 0.76 (PM10 r = 0.88). **Reject H₀** |

---

## 6. Observations (from this data)

1. **Worst cities by average AQI:** Delhi 299, Patna 272, Gurugram 227, Lucknow 224. Ahmedabad shows 311, but that comes from its faulty CO readings, so treat it as a data issue, not a ranking. Visakhapatnam (104) and Bengaluru (109) are the cleanest.
2. **Share of Poor-or-worse days:** Delhi 81%, Patna 62%, Gurugram 54%, Lucknow 46%. Chennai 13%, Hyderabad 11%, Bengaluru 5%, Visakhapatnam 0%.
3. **No real trend in two years:** average AQI was 212 in 2015 and 197 in 2016, but the cities differ: Patna improved 28% while Lucknow got 20% worse. The paired test finds no significant change, and the all-city average shifts partly because Gurugram and Visakhapatnam join only in 2016.
4. **Strong seasonality:** January (290) and February (275) are the worst months, then November (261) and December (258). August (145) is the cleanest. Winter AQI is **about 1.8× monsoon AQI**.
5. **Drivers:** PM10 (r = 0.88) and PM2.5 (0.76) track AQI most closely. NH₃ (0.16) and Benzene (0.09) barely do. CO's 0.45 falls to 0.22 once Ahmedabad is removed, which is more evidence of its bad CO sensor.
6. **Delhi's November 2016 smog:** over 1–10 Nov, PM2.5 averaged **446 against 239** on the same days of 2015 (+87%), and AQI averaged 571. Delhi had **85 Severe days in 2016 against 33 in 2015**.
7. **Night-time build-up:** hourly PM2.5 peaks around 10 pm – midnight (about 105) and is lowest around 5 pm (about 69), as the cooler night air traps pollution near the ground.
8. **Data gaps:** PM10 is missing on 73% of days and NH₃ on 60%, and Mumbai cannot be ranked at all, so coverage must be reported next to every city average.

## 7. Recommendations

1. **Prioritise the Indo-Gangetic cities** (Delhi, Patna, Gurugram, Lucknow) for winter action plans that start in **October**, before the November–January peak.
2. **Prepare an emergency plan for Delhi in late October:** firecracker and crop-burning controls plus construction bans, triggered by forecasts, to avoid a repeat of November 2016.
3. **Control dust (PM10 and PM2.5),** the strongest AQI drivers: construction-site rules and road sweeping.
4. **Audit Ahmedabad's monitoring stations.** Implausible CO values distort public reporting.
5. **Install full sensor sets in Mumbai** and improve PM10 and NH₃ coverage everywhere. Set a target of ≥ 90% data completeness per station.
6. Issue **seasonal and night-time public-health advisories** (Nov–Feb, evenings) in the worst cities.

## 8. Deliverables

`AirQuality_Analysis.xlsx` with sheets **Raw → Clean → Assumptions → Pivots → Tests → Dashboard → Insights**, plus a one-page PDF summary.
