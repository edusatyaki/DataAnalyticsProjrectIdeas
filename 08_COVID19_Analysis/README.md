# 08 · COVID-19 Analysis

**Module:** Python (pandas, matplotlib/seaborn, plotly)  **Dataset:** [Johns Hopkins CSSE COVID-19 time series](https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data/csse_covid_19_time_series) (CC BY 4.0, final update 10 Mar 2023)  **Column profile:** [DATA_PROFILE.md](DATA_PROFILE.md)

---

## 1. Project description

**Business context.** A public-health research team wants a retrospective of the pandemic: how it spread, when the waves peaked, which countries were hit hardest, how deadly it was in different places, and what India's experience looked like. The work must handle real-world messy time-series data.

**Objective.** Reshape wide cumulative time series into tidy data, engineer epidemiological metrics, and build a visual, statistically supported story in a Jupyter notebook.

**Stakeholders.** Public-health analysts, policy makers, journalists.

**Key questions**
1. How many cases and deaths were recorded globally, and when did the waves peak?
2. Which countries had the most cases, deaths and highest fatality rates?
3. How did India's waves compare (Delta vs Omicron)?
4. How long after cases do deaths follow?
5. Which US states had the highest death rates per 100k?

## 2. Dataset

| File | Rows | Id columns | Date columns |
|---|---|---|---|
| `time_series_covid19_confirmed_global.csv` | 289 | `Province/State, Country/Region, Lat, Long` | 1,143 daily (`1/22/20` … `3/9/23`) |
| `time_series_covid19_deaths_global.csv` | 289 | same | same |
| `time_series_covid19_recovered_global.csv` | 274 | same | same (**abandoned after 4 Aug 2021**) |
| `time_series_covid19_confirmed_US.csv` | 3,342 | `UID, iso2, iso3, code3, FIPS, Admin2, Province_State, Country_Region, Lat, Long_, Combined_Key` | same |
| `time_series_covid19_deaths_US.csv` | 3,342 | same + `Population` | same |

---

## 3. Data cleaning

```python
import pandas as pd, numpy as np

def load(kind):
    df = pd.read_csv(f"data/time_series_covid19_{kind}_global.csv")
    df = (df.drop(columns=["Province/State", "Lat", "Long"])
            .groupby("Country/Region").sum(numeric_only=True))      # 1. merge provinces into countries
    long = df.T                                                       # 2. wide -> dates as rows
    long.index = pd.to_datetime(long.index, format="%m/%d/%y")         # 3. parse "1/22/20"
    return long

conf, deaths = load("confirmed"), load("deaths")
new_cases  = conf.diff().clip(lower=0)                                 # 4. cumulative -> daily, clip corrections
new_deaths = deaths.diff().clip(lower=0)
tidy = (conf.stack().rename("confirmed").to_frame()                    # 5. tidy long table for plotting/merging
          .join(deaths.stack().rename("deaths")).reset_index()
          .rename(columns={"level_0": "date", "Country/Region": "country"}))
```

| # | Issue | Treatment |
|---|---|---|
| 1 | Wide format (1 column per day) | `melt` / transpose to long |
| 2 | Values are **cumulative** | `diff()` for daily new values |
| 3 | Negative daily values (data corrections) | `clip(lower=0)`; count and report them |
| 4 | Countries split into provinces (China 34 rows, UK, France, Canada, Australia…) | `groupby('Country/Region').sum()` |
| 5 | `Province/State` 68% blank | Expected: single-row countries |
| 6 | **Recovered** stops being reported in Aug 2021 (last-day total = 0) | Don't use it after mid-2021, and don't compute "active cases" |
| 7 | Non-country rows: `Diamond Princess`, `MS Zaandam`, `Summer Olympics 2020`, `Winter Olympics 2022`, `Antarctica` | Drop for country analysis |
| 8 | No population in the global files | Merge [UID_ISO_FIPS_LookUp_Table.csv](https://github.com/CSSEGISandData/COVID-19/blob/master/csse_covid_19_data/UID_ISO_FIPS_LookUp_Table.csv) for per-million rates |
| 9 | US files: 115 rows with `Population = 0` ("Unassigned", "Out of …", cruise ships) | Exclude them from per-capita rates |
| 11 | Deaths > confirmed on some dates (North Korea, Sudan, UK) | Reporting errors; flag them and exclude those country-days from CFR |
| 10 | Day-of-week reporting artefacts (weekend dips) | Use 7-day rolling averages |

---

## 4. Exploratory data analysis (EDA)

**Feature engineering:** daily new cases and deaths, 7-day rolling averages, CFR = deaths / confirmed, cases and deaths per million, growth rate, doubling time, days since the 100th case.

**Global**
- Cumulative and daily (7-day average) world cases and deaths; annotate the wave peaks
- Year-by-year totals (2020, 2021, 2022, early 2023)

**Countries**
- Top 10 by cases, deaths, deaths per million and CFR (bar charts)
- "Days since 100th case" log-scale trajectories for 6–8 countries
- Choropleth of cases per million (plotly), with an animated version over time

**India deep-dive**
- Daily cases and deaths; the Delta (2021) vs Omicron (2022) peak comparison; CFR over time

**US**
- Merge confirmed and deaths on `UID`; deaths per 100k by state; county choropleth using `FIPS`

**Relationships**
- Cross-correlation of daily cases vs daily deaths shifted 0–35 days
- Month-of-year seasonality heat map

---

## 5. Testing

**A. Data-validation tests** (write them as `assert` statements in the notebook)

```python
assert conf.index.is_monotonic_increasing and conf.index.is_unique
assert (conf.diff().dropna() < 0).sum().sum() < 0.01 * conf.size     # corrections are rare
assert conf.iloc[-1].sum() == 676_570_149                             # matches the raw file's last column
bad = (deaths > conf).any()
print(bad[bad].index.tolist())   # deaths > cases: North Korea, Sudan, UK (reporting errors) -> investigate
assert new_cases.sum().sum() + conf.iloc[0].sum() >= conf.iloc[-1].sum()   # clipping only adds
```

**B. Statistical tests**

| Hypothesis | Method | Result |
|---|---|---|
| H₀: daily deaths don't follow daily cases | Lagged Pearson correlation (0–35 days) | Correlation peaks at a **0–7 day lag** (r ≈ 0.26 globally). Weak, because Omicron's huge case counts had low fatality |
| H₀: CFR is the same in 2020 and 2022 | Two-proportion z-test on deaths/cases per year | 2020 CFR ≈ 2.3% vs 2022 ≈ 0.3%. **Reject H₀** |
| H₀: per-capita death rates are equal across US states | Kruskal-Wallis on county rates grouped by state | p ≈ 3e-215; state rates range from 61 to 455 per 100k. **Reject H₀** |
| Trend significance | Mann-Kendall test or a regression slope on 7-day averages around each peak | Quantifies rise and fall rates |

---

## 6. Observations (from this data)

1. **Totals (9 Mar 2023):** **676.6 M confirmed cases and 6.88 M deaths** worldwide. Overall CFR **1.02%**.
2. **Waves:** cases peaked on **24 Jan 2022 (Omicron) at about 3.4 M new cases a day** (7-day average); deaths peaked earlier, on **26 Jan 2021 at about 14,900 a day**. The deadliest wave was not the largest one.
3. **By year:** 83.8 M cases and 1.9 M deaths in 2020; cumulative 288.7 M and 5.47 M by end-2021; 660.5 M and 6.69 M by end-2022. **2022 had the most cases but far fewer deaths per case.**
4. **Most cases:** US 103.8 M, India 44.7 M, France 39.9 M, Germany 38.2 M, Brazil 37.1 M.
5. **Most deaths:** US 1.12 M, Brazil 699k, India 531k, Russia 388k, Mexico 333k.
6. **Fatality varies widely** (countries with > 1 M cases): Peru **4.9%**, Mexico 4.5%, Ecuador 3.4% vs Singapore **0.08%**, South Korea 0.11%, New Zealand 0.11%. Testing levels, age structure and health systems all matter.
7. **India:** the Delta wave peaked on **8 May 2021 at about 391k cases a day** (7-day average). The Omicron wave peaked on 25 Jan 2022 at about 312k a day but with far fewer deaths. Final: 44.7 M cases, 531k deaths.
8. **US states:** the highest deaths per 100k are Arizona (455), Oklahoma (454), Mississippi (449), West Virginia (444); Hawaii is lowest among states at 130.
9. **The recovered series is unusable after 4 Aug 2021,** so "active cases" can't be computed reliably.

## 7. Recommendations

1. **Measure severity, not only cases:** dashboards should lead with deaths, hospitalisations and CFR. Case counts were a poor guide to burden in 2022.
2. **Early-warning capacity:** deaths followed cases within about 1–3 weeks. Health systems need surge plans triggered by case growth.
3. **Learn from low-CFR countries** (South Korea, Singapore, NZ): early testing, contact tracing and protection of the elderly.
4. **Target high-burden US states** for public-health investment (vaccination outreach, chronic-disease management).
5. **Data governance:** keep consistent definitions (don't abandon series like "recovered") and publish population denominators with the data.

## 8. Deliverables

`covid_analysis.ipynb` (markdown narrative + asserts + charts), an `outputs/` folder of PNG/HTML charts, and a README summary with the key charts.
