# 13 · Credit Risk Modelling with Generative AI

**Module:** Generative AI (Python, scikit-learn, SHAP, an LLM API, Streamlit)  **Dataset:** [Credit Risk Dataset (Kaggle, laotse)](https://www.kaggle.com/datasets/laotse/credit-risk-dataset)  **Column profile:** [DATA_PROFILE.md](DATA_PROFILE.md)

---

## 1. Project description

**Business context.** A lender wants to automate first-level credit decisions. It needs (a) an accurate, explainable **probability-of-default (PD) model**, and (b) a **GenAI layer** that turns each model decision into a clear explanation and a credit memo for loan officers, and that lets managers query the portfolio in plain English. The model must stay the decision-maker; the LLM only explains and summarises.

**Objective.** Clean the data, analyse default drivers, train and validate PD models (handling leakage and class imbalance), explain them with SHAP, then build an LLM-powered app that generates applicant explanations, credit memos and natural-language portfolio answers, with guardrails.

**Stakeholders.** Credit-risk team, loan officers, compliance / model-risk management, applicants (adverse-action notices).

**Key questions**
1. Which borrower and loan features drive default?
2. How accurate is a PD model, with and without the lender's own grade and rate?
3. Which applicants should be approved, reviewed or declined (threshold and cost)?
4. How can an LLM explain decisions faithfully and safely?

## 2. Dataset

`credit_risk_dataset.csv`: 32,581 loans × 12 columns.

| Column | Meaning | Notes |
|---|---|---|
| `person_age` | Age | 5 rows over 100 (max 144) |
| `person_income` | Annual income | 4k – 6M, heavily skewed |
| `person_home_ownership` | RENT / MORTGAGE / OWN / OTHER | |
| `person_emp_length` | Years employed | 2.7% missing; 2 rows over 60 |
| `loan_intent` | EDUCATION / MEDICAL / VENTURE / PERSONAL / DEBTCONSOLIDATION / HOMEIMPROVEMENT | |
| `loan_grade` | A–G (lender's risk grade) | **Leakage risk** |
| `loan_amnt` | Loan amount | 500 – 35,000 |
| `loan_int_rate` | Interest rate | 9.6% missing; set by grade (**leakage risk**) |
| `loan_status` | **Target**: 1 = default | 21.8% |
| `loan_percent_income` | Loan ÷ income | |
| `cb_person_default_on_file` | Past default Y/N | |
| `cb_person_cred_hist_length` | Credit history (years) | |

---

## 3. Data cleaning

| # | Step | Code idea | Result |
|---|---|---|---|
| 1 | Remove exact duplicates | `df.drop_duplicates()` | −165 rows |
| 2 | Remove impossible ages / employment | `age ≤ 100`, `emp_length ≤ 60` | −7 rows → **32,409 rows** |
| 3 | Impute `loan_int_rate` **within grade** | `groupby('loan_grade').transform(lambda s: s.fillna(s.median()))` | Rates are priced by grade |
| 4 | Impute `person_emp_length` | Median, plus a `emp_missing` flag | |
| 5 | Transform skewed income | `log_income = np.log(person_income)` | |
| 6 | Encode | One-hot for home ownership, intent and default-on-file; ordinal for grade (only in the "with grade" model) | |
| 7 | Split **before** fitting anything | `train_test_split(stratify=y, test_size=0.2, random_state=42)` | No leakage from imputation or scaling |
| 8 | Pipeline | `ColumnTransformer` + model in one `Pipeline` | Same transforms in training and in the app |
| 9 | Data checks | Interest rate ranges overlap across grades C–E (min 6.0%) | Flag as a data-quality note |

---

## 4. Exploratory data analysis (EDA)

- Target balance (21.9% default) and its implication: use stratification and class weights, and judge models by PR-AUC/recall, not accuracy
- **Default rate by** grade, home ownership, intent, past default, income quintile, loan-to-income band, age band (bar charts with a baseline line)
- Box plots of income, loan amount, rate and loan-to-income by status
- Correlation heat map; **WoE / Information Value** table to rank features the way credit scorecards do
- Interest-rate distribution by grade (shows why grade and rate are near-duplicates of the lender's judgement)

---

## 5. Modelling & testing

### A. Models

| Model | Features | ROC-AUC | PR-AUC | KS |
|---|---|---|---|---|
| Logistic Regression (balanced) | all incl. grade & rate | 0.876 | 0.710 | 0.61 |
| Gradient Boosting (HistGB) | all incl. grade & rate | **0.948** | **0.906** | **0.76** |
| Logistic Regression | **without** grade & rate | 0.818 | 0.630 | 0.49 |
| Gradient Boosting | **without** grade & rate | 0.904 | 0.821 | 0.65 |

*(80/20 stratified split, random_state = 42. Reproduce these and add cross-validation.)*

**Leakage discussion:** grade and rate add ~4–6 AUC points but are the lender's own risk view. Use the "without" model if the goal is to *replace* manual grading, or "with" if grading already happens upstream. Document the choice.

### B. Model testing checklist

| Test | Method | Pass condition |
|---|---|---|
| Generalisation | 5-fold stratified CV | AUC std < 0.01 |
| Overfitting | Train vs test AUC gap | < 0.03 |
| Calibration | Reliability curve, Brier score | Predicted PD ≈ observed default per decile |
| Threshold | Cost matrix (e.g. missed default = 5× a rejected good loan) | Choose the threshold that minimises expected cost; report recall and precision there |
| Stability | PSI of score distribution between train and test | PSI < 0.1 |
| Fairness | Approval rate and default rate by age band; equal-opportunity gap | Gap documented; no protected attributes in explanations |
| Explainability | SHAP global + local; sign checks (higher loan-to-income → higher PD) | Directions make business sense |

### C. Generative AI layer and its tests

1. **Applicant explanation.** Prompt = applicant features + PD + risk band + top-5 SHAP factors (name, value, direction). The LLM returns a plain-language explanation and 3–4 adverse-action reasons. **The LLM never sees or changes the decision logic.**
2. **Credit memo.** A fixed template: profile summary → PD and band → key risks → mitigants → recommendation (from the rule, not the LLM).
3. **Portfolio Q&A (tool use).** The user asks, "Default rate for renters with debt-consolidation loans?" The LLM calls a `query_portfolio(filters)` tool → pandas runs it → the LLM summarises the returned numbers.
4. **GenAI tests:**
   - *Faithfulness:* every factor the LLM mentions must be in the SHAP top-5 list (automated string check over 100 sampled applicants).
   - *Number accuracy:* the PD and amounts in the text must equal the model output (regex check).
   - *No protected attributes:* age must not appear as a reason (blocklist check).
   - *Consistency:* the same input gives the same reasons (temperature 0); log prompts and responses.
   - *Q&A accuracy:* compare 20 answers against hand-written pandas results.

---

## 6. Observations (from this data)

1. **After cleaning:** 32,409 loans, **21.9% default**.
2. **Lender grade is extremely predictive:** default rises from A 10% → B 16% → C 21% → **D 59% → E 65% → F 71% → G 98%**. There's a cliff between C and D.
3. **Affordability is the strongest borrower-side signal:** loan-to-income ≤ 10% → 12% default; 20–30% → 22%; **30–40% → 69%; above 40% → 74%**.
4. **Income:** the bottom income quintile (≤ $35k) defaults at **43%**, the top quintile at 9%.
5. **Housing:** renters 31.6% and "other" 31.1% vs mortgage 12.6% and **owners 7.5%**.
6. **History:** applicants with a previous default default at **37.9%** vs 18.4% without.
7. **Purpose:** debt consolidation (28.7%), medical (26.8%) and home improvement (26.2%) are riskiest; venture (14.9%) and education (17.3%) are safest.
8. **Age is not a driver** (21–26% across bands). That's good for fairness, since age can be excluded without hurting accuracy.
9. **Models:** gradient boosting reaches **AUC 0.95** (0.90 without grade and rate) and clearly beats logistic regression. Grade and rate add ~4–6 AUC points.

## 7. Recommendations

1. **Hard affordability rule:** refer or decline when loan-to-income > 30% (default jumps from 22% to 69%+), whatever the other factors.
2. **Use the gradient-boosting PD model** for approve / review / decline bands, with the threshold set from a cost matrix, not 0.5.
3. **Re-examine grades D–G:** with 59–98% default, these loans are rarely profitable even at high rates. Tighten eligibility or require collateral.
4. **Price for housing and history:** renters and prior defaulters need a risk premium or smaller limits; owners can get faster approvals.
5. **Deploy the LLM as an explainer only,** with faithfulness and protected-attribute checks in CI. Loan officers get memos in seconds and applicants get clear adverse-action reasons.
6. **Model governance:** monitor PSI monthly, recalibrate quarterly, and keep a fairness report by age band.

## 8. Deliverables

`credit_risk_model.ipynb` (cleaning → EDA → models → tests), `app.py` (Streamlit: applicant form → PD → SHAP chart → LLM explanation → downloadable memo), `prompts/` (versioned templates), `tests/` (faithfulness and number checks), and a README with metrics, a demo GIF, limitations and fairness notes.
