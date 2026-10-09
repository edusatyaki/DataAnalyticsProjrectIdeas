# 01 · National Air Quality: Task List

Work through the tasks in order and tick each box as you finish. **Check** values let you confirm your answer: if yours is different, fix the step before moving on. The full project guide is in [README.md](README.md), and every column is described in [DATA_PROFILE.md](DATA_PROFILE.md).

| Part | Tool | Data folder | Period |
|---|---|---|---|
| **A** (core, required) | Google Sheets | `data/Google Sheets Datasheets/` | 2015–2016, 10 cities |
| **B** (extension) | Excel | `data/Excel Dataset/` | 2015 – Jul 2020, 26 cities |

---

## Part A · Google Sheets (2015–2016)

### A1. Set up the workbook

- [ ] **A1.1** Create one Google Sheets workbook named `AirQuality_2015_16`.
- [ ] **A1.2** Import the four files with File → Import → Upload → *Insert new sheet(s)*. Name the tabs `city_day`, `station_day`, `stations`, `delhi_hour`.
- [ ] **A1.3** Freeze the header row on every tab (View → Freeze → 1 row).
- [ ] **A1.4** Add a `Notes` tab and record the source, the period and today's date.

**Check:** `city_day` has **6,279** data rows, `station_day` 17,182, `stations` 29, `delhi_hour` 17,543.

### A2. Audit the data

- [ ] **A2.1** Count rows per city: `=QUERY(city_day!A:P,"select A, count(B) group by A")`.
- [ ] **A2.2** Find the first and last date per city with `MINIFS` / `MAXIFS`. Which three cities start late?
- [ ] **A2.3** Check for duplicate City + Date pairs with a helper column `=COUNTIFS(A:A,A2,B:B,B2)` and count values above 1.
- [ ] **A2.4** Measure the % missing for every pollutant column: `=COUNTBLANK(C2:C6280)/ROWS(C2:C6280)`.
- [ ] **A2.5** Count the AQI values above 500: `=COUNTIF(O:O,">500")`. Then break them down by city.
- [ ] **A2.6** Compare the average CO by city. Which city looks wrong?

**Check:** 0 duplicates · **1,879** blank AQI (30%) · PM10 73% missing · **109** rows with AQI > 500, of which **51** are Ahmedabad · Ahmedabad CO averages **14.0** · Mumbai has no AQI at all · Gurugram, Patna and Visakhapatnam start late.

### A3. Clean and add columns (on `city_day`)

- [ ] **A3.1** Add `Year` with `=ARRAYFORMULA(IF(B2:B="",,YEAR(B2:B)))`.
- [ ] **A3.2** Add `Month` (number) and `MonthName` (`=TEXT(B2,"mmm")`).
- [ ] **A3.3** Add `Season` with `IFS`: Winter = Dec–Feb, Summer = Mar–May, Monsoon = Jun–Sep, Post-monsoon = Oct–Nov.
- [ ] **A3.4** Add `AQI_clean` = `MIN(AQI,500)`, leaving it blank when AQI is blank.
- [ ] **A3.5** Add `Is_Poor` = TRUE when the bucket is Poor, Very Poor or Severe.
- [ ] **A3.6** Add a flag `Ahmedabad_CO_issue` = TRUE for Ahmedabad rows.
- [ ] **A3.7** On the `Notes` tab, write your rules: blanks stay blank (never 0), AQI capped at 500, Ahmedabad reported separately, Mumbai excluded from AQI charts.
- [ ] **A3.8** On `station_day`, add `State` with `=XLOOKUP(A2,stations!A:A,stations!D:D)`.

**Check:** average AQI = **203.5** · average AQI_clean = **200.2** · median AQI = 159.

### A4. Analyse with pivot tables

Build each one with Insert → Pivot table on a new tab.

- [ ] **A4.1** Average AQI by city, sorted from highest to lowest.
- [ ] **A4.2** % of Poor-or-worse days by city (average of `Is_Poor`).
- [ ] **A4.3** Average AQI by year, then a City × Year pivot.
- [ ] **A4.4** Average AQI by month and by season.
- [ ] **A4.5** Count of days by `AQI_Bucket`.
- [ ] **A4.6** Average AQI by state, using `station_day` and its `State` column.
- [ ] **A4.7** The worst two Delhi stations by average AQI.

**Check:** Delhi **299**, Patna 272, Gurugram 227 (Ahmedabad 311 is flagged) · cleanest city Visakhapatnam 104 · Delhi 81% Poor-or-worse days · 2015 = 212, 2016 = 197 · worst month January (290), best August (145) · Winter 271, Monsoon 150 · Moderate is the most common bucket (1,796 days) · worst Delhi stations: Sirifort 423, Anand Vihar 419.

### A5. Visualise

- [ ] **A5.1** Bar chart: average AQI by city, with Ahmedabad shown in a different colour.
- [ ] **A5.2** Line chart: average AQI by month (Jan–Dec).
- [ ] **A5.3** Heat map: a City × Month pivot coloured with conditional formatting (Format → Conditional formatting → Colour scale).
- [ ] **A5.4** Column chart: number of days in each AQI bucket, in order Good → Severe.
- [ ] **A5.5** Scatter chart: PM10 against AQI, with a trendline and R².
- [ ] **A5.6** Line chart: Delhi's daily AQI from 15 Oct to 30 Nov 2016.
- [ ] **A5.7** Line chart: Delhi's average PM2.5 by hour of day (a pivot on `delhi_hour`, after adding an `Hour` column with `=HOUR(B2)`).
- [ ] **A5.8** Line chart: hourly PM2.5 on Diwali night, 30 Oct 6 pm – 31 Oct 6 am 2016.

**Check:** Delhi's highest AQI is **716** on 7 Nov 2016 · hourly PM2.5 is highest at midnight (152) and lowest at 4–5 pm (93) · Diwali night rises from 172 (6 pm) to **759** (3 am).

### A6. Test

- [ ] **A6.1** Bucket check: MIN and MAX AQI per bucket must match the official bands (Good ≤ 50 … Severe > 400).
- [ ] **A6.2** Total check: the sum of a pivot's day counts equals the number of non-blank AQI rows (4,400).
- [ ] **A6.3** Correlation: `=CORREL()` of PM2.5 with AQI and of PM10 with AQI. Use `FILTER` to drop blank pairs.
- [ ] **A6.4** Winter vs monsoon: `=T.TEST(winter_range, monsoon_range, 2, 3)`.
- [ ] **A6.5** Delhi smog: average PM2.5 for 1–10 Nov 2016 against 1–10 Nov 2015 with `AVERAGEIFS`.

**Check:** r(PM2.5) = **0.76**, r(PM10) = **0.88** · winter vs monsoon p < 0.001 · Delhi PM2.5 **446 vs 239** (+87%) · Delhi Severe days 85 in 2016 vs 33 in 2015.

### A7. Dashboard

- [ ] **A7.1** Create a `Dashboard` tab with KPI cards: average AQI, % Poor-or-worse days, worst city, cleanest city, worst month.
- [ ] **A7.2** Place the charts from A5 on it.
- [ ] **A7.3** Add slicers (Data → Add a slicer) for City, Year and Season, and connect them to the pivots.
- [ ] **A7.4** Test the slicers: choose Delhi and confirm the KPI card matches `=AVERAGEIFS(AQI, City, "Delhi")`.

### A8. Insights

- [ ] **A8.1** On an `Insights` tab, write 6–8 findings, each with a number from your pivots.
- [ ] **A8.2** Write 4–6 recommendations, each linked to a finding.
- [ ] **A8.3** Share the workbook as "Anyone with the link can view" and paste the link in your submission.

---

## Part B · Excel (full 2015 – Jul 2020)

Start this part after Part A. `station_hour.csv.gz` has 2.59 million rows, which is more than Excel can hold, so leave it out (or use it in Python).

### B1. Load

- [ ] **B1.1** Load `city_day.csv`, `station_day.csv` and `stations.csv` with Data → From Text/CSV → **Transform Data** (Power Query). Set `Date` to Date and the pollutants to Decimal Number.
- [ ] **B1.2** Unzip `city_hour.csv.gz` with 7-Zip and load it to the **Data Model only** (Close & Load To → Only Create Connection + Add to Data Model).
- [ ] **B1.3** In Power Query, add the Year, Month, Season, AQI_clean and Is_Poor columns again.

**Check:** `city_day` has **29,531** rows and 26 cities · 4,681 blank AQI · `station_day` 108,035 rows and 110 stations.

### B2. Audit at full scale

- [ ] **B2.1** City × Year pivot of `COUNT(AQI)`: which cities only join in 2017–2019?
- [ ] **B2.2** AQI > 500 by city.
- [ ] **B2.3** Average CO for Ahmedabad against the other cities.

**Check:** **543** rows with AQI > 500, of which **412** are Ahmedabad · Ahmedabad CO averages **22.2**.

### B3. Six-year trend

- [ ] **B3.1** Average AQI by year, 2015–2020, as a line chart.
- [ ] **B3.2** The same for Delhi alone. Does the city-level trend match the all-city trend?
- [ ] **B3.3** Write one sentence on why the all-city average can fall partly because cleaner cities join later.

**Check:** all cities 212 → 197 → 181 → 183 → 157 → 114 · Delhi 297 → 301 → 257 → 249 → 232 → 182.

### B4. 2020 lockdown

- [ ] **B4.1** Average PM2.5, NO2 and AQI for 25 Mar – 31 May in 2020 against the same window in 2019, across all rows.
- [ ] **B4.2** The same comparison per city, as a % change table and a clustered bar chart.
- [ ] **B4.3** Paired t-test on city-level PM2.5 (2019 vs 2020) with the Analysis ToolPak.

**Check:** PM2.5 **−44%**, NO2 **−44%**, AQI **−43%** · Delhi PM2.5 −44%, NO2 −55% · paired p < 0.001 across the 19 cities with both years.

### B5. Compare with Part A

- [ ] **B5.1** Does the 2015–16 ranking of the worst cities still hold for 2015–2020?
- [ ] **B5.2** Which month is worst in each period? (Part A: January. Full data: November.)
- [ ] **B5.3** Write a short note on how using only 2 years changes the conclusions.

### B6. Dashboard

- [ ] **B6.1** PivotCharts with slicers for City, Year and Season, plus a timeline on Date.
- [ ] **B6.2** Add the lockdown chart and the six-year trend line.

---

## Submission checklist

- [ ] Google Sheets link (Part A), shared as view-only
- [ ] `AirQuality_Analysis.xlsx` (Part B) with sheets **Raw → Clean → Assumptions → Pivots → Tests → Dashboard → Insights**
- [ ] A one-page PDF summary: 3 key findings, 3 recommendations and one dashboard screenshot
- [ ] Every Check value above matches your workbook, or you've explained why it differs
