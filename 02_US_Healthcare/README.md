# 02 · US Healthcare Analysis (Excel)

**Module:** Excel  **Dataset:** [Healthcare Dataset (Kaggle, prasad22)](https://www.kaggle.com/datasets/prasad22/healthcare-dataset)
**Column profile:** [DATA_PROFILE.md](DATA_PROFILE.md)

> ⚠️ This dataset is **synthetic**: the values are randomly generated, not real hospital records. Distributions are close to uniform, so expect small differences between groups. Say this in your report. Good analysts don't over-claim.

## File in `data/`

`healthcare_dataset.csv`: 55,500 rows × 15 columns, 1 row = 1 admission (May 2019 – May 2024)

| Column | Notes |
|---|---|
| `Name` | Random casing (`DAvId muNoZ`). Fix with `PROPER()` |
| `Age` | 13–89 |
| `Gender` | Male / Female |
| `Blood Type` | 8 types |
| `Medical Condition` | Arthritis, Diabetes, Hypertension, Obesity, Cancer, Asthma |
| `Date of Admission`, `Discharge Date` | ISO text dates |
| `Doctor`, `Hospital` | ~40k unique values each, so not useful for grouping. Hospital names are fake company names |
| `Insurance Provider` | Cigna, Medicare, UnitedHealthcare, Blue Cross, Aetna |
| `Billing Amount` | −2,008 to 52,764. **108 negative values** |
| `Room Number` | 101–500 |
| `Admission Type` | Elective / Urgent / Emergency |
| `Medication` | Lipitor, Ibuprofen, Aspirin, Paracetamol, Penicillin |
| `Test Results` | Normal / Abnormal / Inconclusive |

## What the data check found

- **534 exact duplicate rows.** Remove them (Data → Remove Duplicates) and note the count.
- **108 negative bills.** Decide whether they are refunds or errors. Exclude them from averages and say so.
- Names have mixed case. Billing has long decimals, so round to 2 places.

## Step-by-step approach

1. **Clean (Power Query or helper columns):** `PROPER(Name)`, remove duplicates, round `Billing Amount`, flag `Billing < 0`.
2. **Derived columns:**
   - `Length of Stay = Discharge Date − Date of Admission` (days)
   - `Age Group` with `IFS`/`XLOOKUP` bands: <18, 18–30, 31–45, 46–60, 61–75, 75+
   - `Admission Year`, `Admission Month`, `Quarter`
   - `Bill Band`: <10k, 10–25k, 25–40k, 40k+
3. **Descriptive pivots:**
   - Admissions by Medical Condition and by Admission Type
   - Average bill and average length of stay by Condition, by Insurance Provider, and by Admission Type
   - Condition × Age Group counts (heat map)
   - Test Results by Condition and by Medication (100% stacked)
   - Monthly admissions trend (line), checking for seasonality
4. **Revenue view:** total billing by Insurance Provider and Year, with each provider's share of the total.
5. **What-if:** use a scenario or data table: "If Emergency admissions grow 10%, how does revenue change?"
6. **Dashboard:** slicers for Year, Condition, Insurance and Gender. KPI cards for total admissions, total billing, average bill, average stay and % abnormal results.
7. **Insights:** because the data is synthetic, state findings as "no meaningful difference between X and Y" when the gaps are under ~2%.

## KPIs

Admissions · Revenue · Average bill · Average length of stay · % Emergency · % Abnormal tests · Revenue by insurer

## Deliverables

`Healthcare_Analysis.xlsx` with Clean data, Pivots, Dashboard and Insights sheets.
