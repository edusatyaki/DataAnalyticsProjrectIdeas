# 13 · Credit Risk Modelling (Generative AI)

**Module:** Generative AI (Python + scikit-learn + an LLM API)  **Dataset:** [Credit Risk Dataset (Kaggle, laotse)](https://www.kaggle.com/datasets/laotse/credit-risk-dataset)
**Column profile:** [DATA_PROFILE.md](DATA_PROFILE.md)

## File in `data/`

`credit_risk_dataset.csv`: 32,581 loans × 12 columns

| Column | Meaning | Notes |
|---|---|---|
| `person_age` | Age | **5 rows over 100 (max 144)**: errors |
| `person_income` | Annual income | 4k – 6M, heavily skewed |
| `person_home_ownership` | RENT / MORTGAGE / OWN / OTHER | |
| `person_emp_length` | Years employed | **2.7% missing**; 2 rows over 60 (max 123) |
| `loan_intent` | EDUCATION / MEDICAL / VENTURE / PERSONAL / DEBTCONSOLIDATION / HOMEIMPROVEMENT | |
| `loan_grade` | A–G | Lender's risk grade |
| `loan_amnt` | Loan amount | 500 – 35,000 |
| `loan_int_rate` | Interest rate | **9.6% missing** |
| `loan_status` | **Target**: 1 = default | **Default rate 21.8%** |
| `loan_percent_income` | loan / income | |
| `cb_person_default_on_file` | Past default (Y/N) | |
| `cb_person_cred_hist_length` | Credit history (years) | |

165 exact duplicate rows.

## What the data check found

- **Strong, realistic signal** (unlike project 10): default rate by grade is A 10% → B 16% → C 21% → **D 59% → E 64% → F 71% → G 98%**. By home ownership, RENT 32% vs OWN 7.5%.
- **Leakage warning:** `loan_grade` and `loan_int_rate` are the lender's own risk assessments. Build models with and without them and explain the difference.
- Impute `loan_int_rate` within each `loan_grade` (rates are set by grade). Impute `person_emp_length` with the median.

## Step-by-step approach

### Part A: classic credit-risk model

1. **Clean:**
   - Drop duplicates
   - Remove or cap ages over 100 and employment over 60 years
   - Impute missing values as described above
   - Log-transform income
2. **EDA:** default rate by each feature and a correlation heat map. Also calculate **WoE/IV** (Weight of Evidence / Information Value), the standard credit-scoring way to rank features.
3. **Split:** stratified train/test at 80/20 and **fit preprocessing on train only** (`ColumnTransformer`: one-hot categoricals, scale numerics).
4. **Models:** Logistic Regression (the interpretable baseline), Random Forest and XGBoost/LightGBM. Handle the 22% class imbalance with `class_weight` or SMOTE.
5. **Evaluate:**
   - ROC-AUC, PR-AUC, KS statistic, the confusion matrix and recall on defaulters
   - Pick a probability threshold using a cost matrix (a missed default costs far more than a rejected good customer)
6. **Explain:** feature importance, **SHAP** values (global + one per applicant), and logistic-regression odds ratios.
7. **Scorecard (optional):** convert log-odds to a 300–900 points scale (PDO method) and cut it into risk bands.

### Part B: the Generative AI layer (what makes this a GenAI project)

8. **LLM explanation of each decision:** send the applicant's features, predicted PD and top SHAP factors to an LLM (Claude or another) with a strict prompt. It should return a plain-language explanation plus an *adverse-action* style reason list. The model decides; the LLM only explains. Never let the LLM change the score.
9. **Natural-language Q&A over the portfolio:** let a user ask "What's the default rate for renters under 25 with education loans?" The LLM writes a pandas/SQL query (tool use), the code runs it, and the LLM summarises the result.
10. **Auto-generated credit memo:** for a given applicant, produce a one-page memo covering a profile summary, risk score, key risks, mitigants and a recommendation, using a fixed template.
11. **Guardrails & evaluation:**
    - No protected attributes (age!) in explanations used for decisions; discuss fairness across `person_age` bands
    - Check that LLM outputs only cite factors that actually came from SHAP
    - Log prompts and responses
12. **App:** a Streamlit app with an applicant form → PD + risk band → SHAP chart → LLM explanation → downloadable memo.

## Deliverables

`credit_risk_model.ipynb`, `app.py` (Streamlit + LLM), `prompts/` (versioned prompt templates), and a README covering model metrics, a demo GIF, limitations and fairness notes.
