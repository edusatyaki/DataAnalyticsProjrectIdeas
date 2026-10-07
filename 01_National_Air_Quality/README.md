# 01 · National Air Quality Analysis (Excel)

**Module:** Excel  **Dataset:** [Air Quality Data in India 2015–2020](https://www.kaggle.com/datasets/rohanrao/air-quality-data-in-india) (CPCB data, compiled on Kaggle)
**Column profile:** [DATA_PROFILE.md](DATA_PROFILE.md)

## Files in `data/`

| File | Rows | Grain | Use it for |
|---|---|---|---|
| `city_day.csv` | 29,531 | 1 row = city × day | **Main file for Excel.** 26 cities, Jan 2015 – Jul 2020 |
| `station_day.csv` | 108,035 | station × day | Station-level drill-down (110 stations) |
| `stations.csv` | 230 | station | Lookup: StationId → name, city, state, Active/Inactive |
| `city_hour.csv.gz` | 707,875 | city × hour | Too big for comfortable Excel. Use Power Query or Python |
| `station_hour.csv.gz` | 2.59 M | station × hour | Exceeds Excel's 1,048,576-row limit. Python only |

> `.csv.gz` files are compressed to stay under GitHub's file-size limit. Unzip with 7-Zip, or let pandas read them directly: `pd.read_csv("city_hour.csv.gz")`.

## Columns (city_day)

`City`, `Date`, 12 pollutants (`PM2.5, PM10, NO, NO2, NOx, NH3, CO, SO2, O3, Benzene, Toluene, Xylene`), `AQI`, `AQI_Bucket`
(Good / Satisfactory / Moderate / Poor / Very Poor / Severe).

## What the data check found

- **Missing values are heavy and uneven:** Xylene 61%, PM10 38%, NH3 35%, AQI 16%. Many cities only started reporting in 2017–2019, so a city's average depends on which years it has data for.
- **AQI is blank on 16% of rows.** Where AQI is missing, the bucket is missing too.
- **Extreme values:** AQI goes up to 2,049 (the scale tops out at 500) and PM10 is capped at exactly 1000.0. Treat these as sensor caps or errors, not as real readings.
- `Date` is ISO text (`2015-01-01`), so Excel converts it to a date cleanly.
- The data ends 1 Jul 2020. The March–May 2020 lockdown makes a natural "before/after" story.

## Step-by-step approach

1. **Import with Power Query** (Data → From Text/CSV) instead of opening the CSV directly. Set `Date` to Date and the pollutant columns to Decimal. Add `Year`, `Month`, `MonthName`, `Season` columns (Winter = Dec–Feb, Summer = Mar–May, Monsoon = Jun–Sep, Post-monsoon = Oct–Nov).
2. **Data-quality sheet:** use `COUNTBLANK` per pollutant and a City × Year pivot of `COUNT(AQI)` to show coverage. Decide your rule: drop rows where AQI is blank for AQI analysis; keep blanks (don't fill with 0) for pollutants.
3. **Merge in the station lookup** (optional): `XLOOKUP` StationId → State in `station_day` to add a state-level view.
4. **Cap outliers:** add a helper column `AQI_clean = MIN(AQI, 500)` and flag rows with `AQI > 500`.
5. **Core pivots:**
   - Average AQI by City (ranked): which cities are worst?
   - Average AQI by Year: is air getting better?
   - Month × City heat map (conditional formatting): the winter spike in North India
   - AQI_Bucket count by City (100% stacked bar): share of "Poor or worse" days
   - PM2.5 vs PM10 vs NO2 by season
6. **Lockdown analysis:** compare average PM2.5, NO2 and AQI for Mar 25 – May 31 in 2020 against the same window in 2019 for each city. Calculate the percentage change.
7. **Correlation:** run `CORREL` (or Data Analysis ToolPak → Correlation) between pollutants and AQI. PM2.5 and PM10 should be the strongest drivers.
8. **Dashboard sheet:** add slicers for City, Year and Season, with KPI cards for average AQI, % severe days, worst month and cleanest city. Show a line chart (monthly AQI trend), a bar chart (city ranking) and the heat map.
9. **Insights sheet:** write 5–7 numbered findings, each with the number that backs it.

## KPIs to show

Average AQI · % days Poor/Very Poor/Severe · worst city · worst month · PM2.5 lockdown drop % · data-coverage %

## Deliverables

`AirQuality_Analysis.xlsx` (Raw → Clean → Pivots → Dashboard → Insights sheets) and a one-page summary.

## Stretch

Rank cities by "number of days above the WHO PM2.5 guideline (15 µg/m³)". Rebuild the dashboard on `station_day` with a State slicer.
