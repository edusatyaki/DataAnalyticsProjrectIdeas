# 10 · Loan Default Analysis

**Module:** Statistics and EDA (Python: pandas, seaborn, scipy, statsmodels)  **Dataset:** [Loan Default Prediction Dataset (Kaggle, nikhil1e9)](https://www.kaggle.com/datasets/nikhil1e9/loan-default)  **Column profile:** [DATA_PROFILE.md](DATA_PROFILE.md)

---

## 1. Project description

**Business context.** A lender is losing money on defaults (11.6% of loans). The credit-policy team wants to know which borrower and loan characteristics are associated with default, how strong each effect is, and how to segment applicants into risk tiers, using statistics rather than gut feel.

**Objective.** Run a full statistical EDA on 255k loans: describe the data, compare defaulters vs non-defaulters, test hypotheses with effect sizes, and turn the findings into a simple risk-segmentation rule and policy recommendations.

**Stakeholders.** Credit-risk / underwriting, pricing team, collections.

**Key questions**
1. What is the default rate, and how is the data distributed?
2. Which numeric features (age, income, interest rate…) differ between defaulters and non-defaulters, and by how much?
3. Which categorical features (employment, co-signer…) are associated with default?
4. Which combinations of factors identify high-risk borrowers?
5. What policy changes would reduce defaults?

## 2. Dataset

`Loan_default.csv`: 255,347 loans × 18 columns.

| Type | Columns |
|---|---|
| ID | `LoanID` |
| Numeric | `Age` (18–69), `Income` (15k–150k), `LoanAmount` (5k–250k), `CreditScore` (300–849), `MonthsEmployed` (0–119), `NumCreditLines` (1–4), `InterestRate` (2–25%), `LoanTerm` (12–60), `DTIRatio` (0.1–0.9) |
| Categorical | `Education` (4), `EmploymentType` (4), `MaritalStatus` (3), `HasMortgage`, `HasDependents`, `LoanPurpose` (5), `HasCoSigner` |
| Target | `Default` (0/1), **11.6% = 1** |

---

## 3. Data cleaning

| # | Check | Code | Finding |
|---|---|---|---|
| 1 | Shape and types | `df.info()` | 18 columns, correct types |
| 2 | Missing values | `df.isna().sum()` | **None** |
| 3 | Duplicates | `df.duplicated().sum()`, `df.LoanID.is_unique` | **None**; LoanID unique |
| 4 | Range checks | `df.describe()`: age 18–69, score 300–849, DTI 0.1–0.9 | All plausible |
| 5 | Outliers | IQR rule per numeric column | **None.** Every numeric column is near-uniform (skew ≈ 0) |
| 6 | Category values | `value_counts()` | Clean and balanced (each level ~20–33%) |
| 7 | Encode Yes/No | `map({'Yes':1,'No':0})` | For correlation and regression |
| 8 | Derived features | `AgeBand`, `IncomeQuartile`, `ScoreBand` (Poor <580, Fair 580–669, Good 670–739, Very good 740–799, Excellent 800+), `RateBand`, `TenureBand`, `LoanToIncome = LoanAmount/Income`, `EMI` | For segment analysis |
| 9 | Drop `LoanID` from the analysis | | |

**Insight from cleaning:** perfectly clean data with uniform distributions suggests the data is **synthetic**. Say so in the report.

---

## 4. Exploratory data analysis (EDA)

**Univariate**
- Target balance bar chart (11.6% default)
- Histograms/KDEs of numeric columns (flat shapes), count plots of categoricals
- Summary table: mean, median, std, skew, kurtosis

**Bivariate (feature vs Default)**
- Default rate by every categorical and every band (bar chart with the 11.6% baseline line)
- Box/violin plots of Age, Income, InterestRate, MonthsEmployed, LoanAmount split by Default
- Point-biserial correlations with Default; full correlation heat map

**Multivariate**
- Default-rate heat maps: AgeBand × RateBand, EmploymentType × HasCoSigner
- Pair plot on a 5k sample, coloured by Default
- Logistic regression (`statsmodels.Logit`) to read **odds ratios** with all features together

**Segmentation**
- Count the risk flags (age < 30, rate > 18%, income < 50k, employed < 24 months, no co-signer) → default rate by number of flags

---

## 5. Testing (hypothesis tests)

State H₀/H₁, use α = 0.05, and **report effect size**. With 255k rows almost everything is "significant".

| # | Hypothesis (H₀) | Test | Result | Effect size |
|---|---|---|---|---|
| 1 | Age is the same for defaulters and non-defaulters | Mann-Whitney U / Welch t | 36.6 vs 44.4 years, p ≈ 0 | **Cohen's d = −0.52 (medium)** |
| 2 | Interest rate is the same | Mann-Whitney | 15.9% vs 13.2% | d = +0.41 |
| 3 | Income is the same | Mann-Whitney | 71.8k vs 83.9k | d = −0.31 |
| 4 | Months employed is the same | Mann-Whitney | 50 vs 61 months | d = −0.30 |
| 5 | Loan amount is the same | Mann-Whitney | 144.5k vs 125.4k | d = +0.27 |
| 6 | Credit score is the same | Mann-Whitney | 559 vs 576 | d = −0.11 (small) |
| 7 | **Loan term** is the same | Mann-Whitney | 36.05 vs 36.02, **p = 0.78** | **None:** fail to reject |
| 8 | Default is independent of employment type | Chi-square | p ≈ 1e-114 | Cramér's V = 0.046 |
| 9 | Default is independent of co-signer | Chi-square / two-proportion z | 10.4% vs 12.9% | V = 0.039 |
| 10 | Default is independent of education / marital status / purpose | Chi-square | All significant | V = 0.02–0.03 (very weak) |
| 11 | Interest rate is equal across loan purposes | One-way ANOVA | 13.47%–13.53% by purpose, p = 0.55. **Fail to reject** | η² ≈ 0 |

Also give a 95% confidence interval for the default rate of each risk segment (`statsmodels.stats.proportion.proportion_confint`).

---

## 6. Observations (from this data)

1. **Default rate is 11.6%** (29.7k of 255k loans). The data is clean but near-uniform, so it's likely synthetic.
2. **Age is the strongest single driver:** default falls from **20.8% (18–25) to 16.1% (26–35), 10.8% (36–50) and 6.1% (51+)**.
3. **Interest rate:** 6.6% default at ≤ 8% → 9.3% (8–13%) → 12.3% (13–18%) → **17.0% above 18%**.
4. **Income:** the lowest quartile (< 49k) defaults at **17.4%**, vs about 9–10.5% for the other three.
5. **Job tenure:** < 12 months employed → **16.9%**; 6–10 years → 8.5%.
6. **Categoricals are weak:** unemployed 13.6% vs full-time 9.5%; no co-signer 12.9% vs 10.4%; dependents, mortgage, education and purpose shift default by only 1–2 points (Cramér's V < 0.05).
7. **No effect:** loan term (p = 0.78) and DTI ratio (d = 0.06) barely matter. Credit score matters less than expected (d = 0.11).
8. **Risk flags stack up:** with 0 flags, default is **4.5%**; 1 flag 7.7%; 2 flags 13.2%; 3 flags 22.9%; 4 flags 34.5%; **all 5 flags 52.9%**.
9. Young (< 30) **and** unemployed **and** rate > 18%: 4,391 loans with **33% default**.

## 7. Recommendations

1. **Adopt a flag-based risk tier now:** 0–1 flags = auto-approve; 2 = standard review; 3+ = manual underwriting or a co-signer requirement (default 23–53%).
2. **Young, short-tenure applicants:** require a co-signer or smaller first loans, then step up after good repayment history.
3. **Break the high-rate trap:** loans priced above 18% default at 17%, so the high rate may itself cause defaults. Review pricing; offer lower rates with collateral instead.
4. **Income-based limits:** cap loan amount at a multiple of income for the bottom income quartile.
5. **Don't over-weight credit score, term or DTI** in this portfolio; the evidence for them is weak.
6. **Next step:** build a predictive model (logistic regression / gradient boosting) on these features and validate on real, non-synthetic data before rollout.

## 8. Deliverables

`loan_default_eda.ipynb` (cleaning → EDA → tests table → segmentation) and a 1-page credit-policy recommendation.
