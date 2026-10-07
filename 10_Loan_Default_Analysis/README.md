# 10 · Loan Default Analysis (Statistics & EDA)

**Module:** Statistics and EDA (Python: pandas, seaborn, scipy, statsmodels)  **Dataset:** [Loan Default Prediction Dataset (Kaggle, nikhil1e9)](https://www.kaggle.com/datasets/nikhil1e9/loan-default)
**Column profile:** [DATA_PROFILE.md](DATA_PROFILE.md)

## File in `data/`

`Loan_default.csv`: 255,347 loans × 18 columns. **No missing values, no duplicates.**

| Type | Columns |
|---|---|
| ID | `LoanID` |
| Numeric | `Age` (18–69), `Income` (15k–150k), `LoanAmount` (5k–250k), `CreditScore` (300–849), `MonthsEmployed` (0–119), `NumCreditLines` (1–4), `InterestRate` (2–25%), `LoanTerm` (12/24/36/48/60), `DTIRatio` (0.1–0.9) |
| Categorical | `Education` (4), `EmploymentType` (4), `MaritalStatus` (3), `HasMortgage`, `HasDependents`, `LoanPurpose` (5), `HasCoSigner` (Yes/No) |
| Target | `Default` (0/1). **Default rate = 11.6%** (imbalanced) |

## What the data check found

The data is clean but looks **synthetic**: numeric features are almost uniformly distributed and the signals are modest. Real effects are still there:

| Driver | Default rate |
|---|---|
| Age 18–25 → 51–69 | **20.8% → 6.1%** (strongest) |
| Unemployed vs full-time | 13.6% vs 9.5% |
| No co-signer vs co-signer | 12.9% vs 10.4% |
| Credit score bottom 20% vs top 20% | 13.2% vs 10.2% |
| Loan term | flat at ~11.6% (no effect) |

Correlation with `Default`: Age −0.17, InterestRate +0.13, Income −0.10, MonthsEmployed −0.10, LoanAmount +0.09, DTIRatio ≈ 0.

## Step-by-step approach

1. **Understand & audit:** shape, `info()`, `describe()`, nulls, duplicates, and target balance (bar chart of `Default`).
2. **Univariate EDA:**
   - Histograms and KDEs for numeric columns (note the flat, uniform shapes)
   - Box plots for outliers
   - Count plots for categoricals
   - Skewness and kurtosis
3. **Feature engineering:**
   - `Age band`, `Income band`, `Credit score band` (Poor < 580 / Fair / Good / Very good / Excellent ≥ 800)
   - `Loan-to-Income = LoanAmount / Income`
   - `EMI ≈ LoanAmount × r(1+r)^n / ((1+r)^n − 1)` with `r = InterestRate/1200` and `n = LoanTerm`
4. **Bivariate EDA (feature vs Default):**
   - Default rate by each categorical and each band (bar charts with the 11.6% baseline drawn as a line)
   - Box or violin plots of numeric features split by Default
   - Correlation heat map
5. **Hypothesis testing:** state H₀/H₁, α = 0.05, and report the effect size, not just the p-value. With 255k rows almost everything is "significant", so effect size is what matters.
   - **Chi-square test of independence** for each categorical vs Default, with **Cramér's V**
   - **Two-sample t-test / Mann-Whitney U** for Income, Age, CreditScore and InterestRate (defaulters vs non-defaulters), with Cohen's d
   - **ANOVA**: does InterestRate differ across LoanPurpose?
   - **Proportion z-test**: default rate with vs without a co-signer
   - Confidence intervals for the default rate of each segment
6. **Multivariate:**
   - Default-rate heat map of Age band × Employment type
   - Pair plot on a sample
   - Optional baseline logistic regression (`statsmodels`) to read odds ratios
7. **Risk segments:** combine the 3–4 strongest drivers into a simple rule-based score (Low / Medium / High risk) and show the default rate per segment.
8. **Report:** the top drivers ranked by effect size, the segments to avoid or price higher, and the data limitations (synthetic data, no time dimension).

## Deliverables

`loan_default_eda.ipynb` and a 1-page "Credit policy recommendations" summary.
