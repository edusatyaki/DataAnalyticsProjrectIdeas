# 08 · COVID-19 Analysis (Python)

**Module:** Python (pandas, matplotlib/seaborn/plotly)  **Dataset:** [Johns Hopkins CSSE COVID-19 time series](https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data/csse_covid_19_time_series) (CC BY 4.0, archived 10 Mar 2023)
**Column profile:** [DATA_PROFILE.md](DATA_PROFILE.md)

## Files in `data/`

| File | Rows | Id columns | Date columns |
|---|---|---|---|
| `time_series_covid19_confirmed_global.csv` | 289 | `Province/State, Country/Region, Lat, Long` | 1,143 daily (`1/22/20` … `3/9/23`) |
| `time_series_covid19_deaths_global.csv` | 289 | same | same |
| `time_series_covid19_recovered_global.csv` | 274 | same | same (**stops being updated in Aug 2021, and the last-day total is 0**) |
| `time_series_covid19_confirmed_US.csv` | 3,342 | `UID, iso2, iso3, code3, FIPS, Admin2 (county), Province_State, Country_Region, Lat, Long_, Combined_Key` | same |
| `time_series_covid19_deaths_US.csv` | 3,342 | same + `Population` | same |

## What the data check found

- **Wide format:** one column per day. You must `melt` it into long format (`country, date, value`).
- **Values are cumulative.** Daily new cases = `diff()`. Corrections in the source cause some negative diffs, so clip them to 0 or flag them.
- **Some countries are split into provinces:** China (34 rows), plus Australia, Canada, the UK and France with their territories. `groupby('Country/Region').sum()` first. `Province/State` is blank for 68% of rows (single-row countries).
- **Do not use the recovered data after mid-2021.** It drops to zero.
- No population in the global files. Merge one (e.g. World Bank, or JHU's `UID_ISO_FIPS_LookUp_Table.csv`) to get per-million rates. The US deaths file includes `Population` per county.
- Final totals (9 Mar 2023): **676.6 M confirmed, 6.88 M deaths globally**; US: 103.8 M confirmed, 1.12 M deaths.

## Step-by-step approach

1. **Load & reshape**
   ```python
   import pandas as pd
   def load(kind):
       df = pd.read_csv(f"data/time_series_covid19_{kind}_global.csv")
       df = df.drop(columns=["Lat", "Long"]).groupby("Country/Region").sum(numeric_only=True)
       long = df.T
       long.index = pd.to_datetime(long.index, format="%m/%d/%y")
       return long          # rows = date, columns = country, cumulative
   conf, deaths = load("confirmed"), load("deaths")
   new_cases = conf.diff().clip(lower=0)
   ```
2. **Features:**
   - Daily new cases and deaths, and their 7-day rolling averages
   - Case fatality rate = deaths / confirmed
   - Growth rate and doubling time
   - Cases per million after merging population
3. **Global picture:**
   - Cumulative and daily world totals
   - Identify the waves (original, Delta mid-2021, Omicron Jan 2022) with peak dates
4. **Country comparison:**
   - Top 10 countries by cases, deaths, deaths per million and CFR
   - A "days since 100th case" log-scale chart for 6–8 countries
5. **India deep-dive:** the April–May 2021 second wave, its peak day, and how CFR changed over time.
6. **US county view:** merge confirmed and deaths on `UID`; calculate deaths per 100k by state; plot a choropleth with plotly using `FIPS`.
7. **Statistics:**
   - Correlation of cases with deaths, lagged 14–21 days (`shift`)
   - Month-of-year seasonality
8. **Visual story:** 6–8 polished charts, including an animated plotly map of cases over time.
9. **Conclusions:** what the data can and can't say, given testing differences between countries.

## Deliverables

`covid_analysis.ipynb` (clean, with markdown explanations), an `outputs/` folder of charts, and a summary in the README.
