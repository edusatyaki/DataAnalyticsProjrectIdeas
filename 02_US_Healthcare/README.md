# 02 · US Healthcare Analysis

**Module:** Excel  **Dataset:** [Healthcare Dataset (Kaggle, prasad22)](https://www.kaggle.com/datasets/prasad22/healthcare-dataset)  **Column profile:** [DATA_PROFILE.md](DATA_PROFILE.md)

> ⚠️ **This dataset is synthetic.** Values are randomly generated, so almost every group looks the same. That is itself the lesson: an analyst must say "no meaningful difference" when the data shows none, instead of inventing a story.

---

## 1. Project description

**Business context.** A US hospital network wants a single view of its admissions: who is admitted, for what, for how long, how much is billed, and to which insurers. Management wants to know where revenue comes from and whether any condition, insurer or admission type costs more.

**Objective.** Clean 55,500 admission records, build KPIs and an interactive Excel dashboard, and test whether the apparent differences between groups are real.

**Stakeholders.** Hospital operations, finance (billing), insurance-relations team.

**Key questions**
1. What are admission volume, total billing, average bill and average length of stay (LOS)?
2. How do bill and LOS vary by medical condition, admission type, insurer and age group?
3. Which insurers bring the most revenue?
4. Are test results related to condition or medication?
5. Are there trends or seasonality in admissions?

## 2. Dataset

`healthcare_dataset.csv`: 55,500 rows × 15 columns, 1 row = 1 admission, May 2019 – May 2024.

| Column | Notes |
|---|---|
| `Name` | Random casing (`DAvId muNoZ`) |
| `Age` | 13–89 |
| `Gender`, `Blood Type` | 2 and 8 categories |
| `Medical Condition` | Arthritis, Asthma, Cancer, Diabetes, Hypertension, Obesity |
| `Date of Admission`, `Discharge Date` | ISO text dates |
| `Doctor`, `Hospital` | ~40k unique values each, so useless for grouping |
| `Insurance Provider` | Aetna, Blue Cross, Cigna, Medicare, UnitedHealthcare |
| `Billing Amount` | −2,008 to 52,764 |
| `Room Number` | 101–500 |
| `Admission Type` | Elective / Urgent / Emergency |
| `Medication` | Aspirin, Ibuprofen, Lipitor, Paracetamol, Penicillin |
| `Test Results` | Normal / Abnormal / Inconclusive |

---

## 3. Data cleaning

| # | Step | How (Excel) | Result |
|---|---|---|---|
| 1 | Import | Power Query; set the two date columns to Date and `Billing Amount` to Decimal | |
| 2 | Fix name casing | Power Query → Transform → Format → **Capitalize Each Word** (or `=PROPER()`) | `David Munoz` |
| 3 | Remove exact duplicates | Home → Remove Rows → Remove Duplicates (all columns) | **534 removed → 54,966 rows** |
| 4 | Negative bills | Filter `Billing Amount < 0` → add a flag column `Is_Refund` | **108 rows.** Exclude them from averages; keep them in a "Refunds" note |
| 5 | Round money | `=ROUND(Billing,2)` | |
| 6 | Length of stay | `LOS = Discharge Date − Date of Admission` | 1–30 days, mean 15.5 |
| 7 | Validate dates | Check that `Discharge ≥ Admission` | 0 violations |
| 8 | Age groups | `=IFS(Age<18,"<18",Age<=30,"18-30",Age<=45,"31-45",Age<=60,"46-60",Age<=75,"61-75",TRUE,"75+")` | |
| 9 | Date parts | `Year`, `Month`, `Quarter`, `YearMonth` | 2019 and 2024 are partial years |
| 10 | Bill band | <10k / 10–25k / 25–40k / 40k+ | |
| 11 | Drop analysis-useless columns from pivots | Doctor, Hospital, Room Number (keep them in the data) | |

---

## 4. Exploratory data analysis (EDA)

**Univariate**
- Histograms of Age, Billing Amount and LOS. All three are **flat (uniform)**, the fingerprint of synthetic data.
- Count of admissions by Condition, Admission Type, Insurer, Medication and Test Result. Each splits almost evenly.

**Bivariate**
- Average bill by Condition / Insurer / Admission Type / Medication (bar charts; zoom the axis to see how tiny the gaps are)
- Average LOS by Admission Type
- Test Results by Condition (100% stacked bar)
- Age vs Billing scatter (r ≈ 0)

**Time**
- Monthly admissions trend (line). Mark 2019 and 2024 as partial years.
- Revenue by Year × Insurer (clustered column)

**Multivariate**
- Condition × Age-group heat map of admission counts
- Condition × Insurer pivot of average bill

**Dashboard**
- Slicers: Year, Condition, Insurer, Gender, Admission Type
- KPI cards: Admissions, Revenue, Average bill, Average LOS, % Emergency, % Abnormal
- Charts: monthly trend, revenue by insurer, condition mix, test-result mix

---

## 5. Testing

**A. Data-validation tests**

| Test | Pass condition |
|---|---|
| Row count after dedup | 54,966 |
| `COUNTIFS` of duplicates on all columns | 0 |
| No Discharge before Admission | 0 rows |
| Pivot revenue = `SUMIFS` on the clean table | Equal |
| Every category value is valid (pivot of distinct values) | 6 conditions, 5 insurers, 3 admission types |

**B. Statistical tests** (ToolPak: ANOVA Single Factor, t-Test; Chi-square with `CHISQ.TEST`)

| Hypothesis | Test | Result |
|---|---|---|
| H₀: average bill is the same across the 6 conditions | One-way ANOVA | p ≈ 0.047, but the gap is only $25,206 (Cancer) to $25,859 (Obesity), about 2.5%. Statistically borderline, **practically irrelevant** |
| H₀: test result is independent of condition | Chi-square (`CHISQ.TEST`) | p = 0.21. **Fail to reject:** no relationship |
| H₀: LOS is the same for Emergency vs Elective | t-test | 15.58 vs 15.51 days. No difference |
| H₀: Age and bill are uncorrelated | `CORREL` | r = −0.003. No relationship |

**Teaching point:** with 55k rows even tiny gaps can become "significant". Always report the size of the difference, not only the p-value.

---

## 6. Observations (from this data)

1. **Volume and revenue:** 54,966 admissions after cleaning; **$1.40 billion billed**; average bill **$25,595**; average stay **15.5 days**.
2. **Every group is almost identical:** average bill by condition ranges only $25.2k–$25.9k; by insurer $25.5k–$25.7k; by admission type $25.6k–$25.7k.
3. **Balanced mix:** each condition is about 16.6% of admissions, each insurer about 20%, each admission type about 33%.
4. **Test results** are about one-third Normal / Abnormal / Inconclusive for every condition (chi-square p = 0.21).
5. **Volume trend:** about 11k admissions in each full year (2020–2023), with no growth and no seasonality.
6. **Data quality:** 534 duplicate rows (1%) and 108 negative bills. Name casing and hospital names ("LLC Smith") show the data is generated.
7. Average patient age is about 51.5 in every condition, which is medically unrealistic (asthma usually skews younger). This is more evidence that the data is synthetic.

## 7. Recommendations

1. **Fix data capture first:** dedupe at source, block negative bills unless they are coded as refunds, and standardise names.
2. **Don't make pricing or insurer decisions from this data.** No group differs by more than ~2.5%.
3. **Add the fields that would make the analysis actionable:** diagnosis codes (ICD), procedure codes, readmission flag, cost (not only billing), payer-paid amount and real hospital IDs.
4. **Monitor capacity:** about 11k admissions a year with a stable 15.5-day stay gives a predictable bed-day demand (~470 beds occupied on average) for planning.
5. **Reuse the dashboard** as a template. It will become insightful once it's connected to real data.

## 8. Deliverables

`Healthcare_Analysis.xlsx` (Raw → Clean → Pivots → Tests → Dashboard → Insights) and a short note on synthetic-data limitations.
