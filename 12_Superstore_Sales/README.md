# 12 · Superstore Sales Analysis

**Module:** Statistics and EDA (Python)  **Dataset:** Tableau "Sample – Superstore", US orders 2014–2017 (copy from [Kaggle vivek468](https://www.kaggle.com/datasets/vivek468/superstore-dataset-final); official source: [Tableau sample data](https://public.tableau.com/app/learn/sample-data))  **Column profile:** [DATA_PROFILE.md](DATA_PROFILE.md)

---

## 1. Project description

**Business context.** A US office-supplies and furniture retailer is growing sales but its profit margin is thin (12.5%). Leadership wants to know which products, regions and customers are profitable, whether discounting is destroying profit, and what to change.

**Objective.** Run a full statistical EDA on 9,994 order lines: clean, explore, test hypotheses about discount, region and segment effects, and recommend profit-improving actions.

**Stakeholders.** CEO/CFO, category managers, regional sales managers, pricing team.

**Key questions**
1. How have sales and profit trended over 2014–2017?
2. Which categories and sub-categories make or lose money?
3. Which regions and states are unprofitable, and why?
4. How does discount affect profit?
5. Is profit concentrated in a few customers?
6. Is there seasonality?

## 2. Dataset

`Sample_Superstore.csv`: 9,994 order lines × 21 columns. No missing values.

| Group | Columns |
|---|---|
| Order | `Row ID, Order ID` (5,009 orders), `Order Date, Ship Date` (m/d/yyyy text), `Ship Mode` (4) |
| Customer | `Customer ID, Customer Name` (793), `Segment` (Consumer / Corporate / Home Office) |
| Geography | `Country` (US), `City` (531), `State` (49), `Postal Code`, `Region` (West / East / Central / South) |
| Product | `Product ID` (1,862), `Category` (3), `Sub-Category` (17), `Product Name` |
| Measures | `Sales, Quantity, Discount` (0–0.8), `Profit` (−6,600 to +8,400) |

---

## 3. Data cleaning

| # | Step | Code | Finding |
|---|---|---|---|
| 1 | Read with the right encoding | `pd.read_csv(path, encoding="cp1252")` | UTF-8 fails (Windows-1252 bytes). Don't use `comment="#"`: product names contain `#` |
| 2 | Parse dates | `pd.to_datetime(df["Order Date"], format="%m/%d/%Y")` | 3 Jan 2014 – 30 Dec 2017 |
| 3 | Missing / duplicates | `isna().sum()`, `duplicated().sum()` | 0 / 0 |
| 4 | Validate logic | `Ship Date ≥ Order Date`; `0 ≤ Discount ≤ 0.8`; `Quantity > 0` | All pass |
| 5 | Drop constant columns | `Country` (only "United States"), `Row ID` | |
| 6 | Check IDs | `Product ID` → 1,862 ids but 1,848 names | Group by ID, not by name |
| 7 | Derived columns | `Year, Month, Quarter, Weekday`, `Ship Days`, `Profit Margin = Profit/Sales`, `Discount Band` (0 / ≤ 20% / 20–40% / > 40%), `Is Loss = Profit < 0` | |
| 8 | Outliers | IQR flags 11.7% of lines on Sales and 18.8% on Profit | **Keep them.** Big orders and big losses are real business events. Analyse them separately |
| 9 | Postal codes | Read as string (`dtype={"Postal Code": str}`) to keep leading zeros | |

---

## 4. Exploratory data analysis (EDA)

**Univariate:** distributions of Sales and Profit (right-skewed with fat tails, so use a log scale for Sales); Discount value counts; KPI summary (sales, profit, margin, orders, AOV).
**Bivariate:**
- Sales, profit and margin by Category and Sub-Category (sorted bars; highlight the losses)
- By Region, State (choropleth), Segment and Ship Mode
- Discount vs Profit scatter + regression line; average profit by discount band
- Ship Mode vs Ship Days

**Multivariate:**
- Region × Category profit heat map
- Sub-Category × Discount Band average-profit heat map
- Average discount by Region alongside profit (explains Central)

**Time:** yearly sales and profit; monthly seasonality (share of annual sales by month); rolling 3-month trend.
**Customers:** Pareto curve of profit by customer; number of loss-making customers; RFM segments.

---

## 5. Testing

**A. Data-validation tests**

| Test | Pass condition |
|---|---|
| Rows = 9,994, orders = 5,009, customers = 793 | Equal |
| Totals reconcile: Sales = 2,297,201, Profit = 286,397 | Equal |
| No negative quantity or sales; discount within [0, 0.8] | 0 violations |
| `Ship Date ≥ Order Date` | 0 violations |

**B. Statistical tests**

| # | Hypothesis (H₀) | Test | Result |
|---|---|---|---|
| 1 | Discount and profit are uncorrelated | Pearson & Spearman | Pearson r = −0.22, **Spearman ρ = −0.54**; discount vs margin r = **−0.86**. **Reject** |
| 2 | Profit of discounted lines = non-discounted lines | Welch t-test | p ≈ 4e-55. **Reject**: discounted lines earn much less |
| 3 | Profit margin is the same in all 4 regions | Kruskal-Wallis (non-normal) + Dunn/Tukey post-hoc | p ≈ 4e-51. **Reject**: Central is worst |
| 4 | Ship mode is independent of segment | Chi-square | p ≈ 9e-5. Weak but significant association |
| 5 | 95% confidence interval for average order value | t-interval | **$458.6 (95% CI $432–$485)** |
| 6 | Sales are normally distributed | Shapiro / Q-Q | Strongly non-normal, which justifies the non-parametric tests |

---

## 6. Observations (from this data)

1. **Overall:** $2.30 M sales, **$286k profit, 12.5% margin**. Sales grew from $484k (2014) to $733k (2017) and profit from $50k to $93k. 2015 sales dipped slightly.
2. **Furniture barely earns:** a **2.5% margin** ($18k profit on $742k sales) vs Technology 17.4% and Office Supplies 17.0%.
3. **Loss-making sub-categories:** **Tables −$17.7k (−8.6% margin)**, Bookcases −$3.5k, Supplies −$1.2k. Machines are barely positive (1.8%). The stars are Copiers ($55.6k, 37% margin), Phones ($44.5k) and Accessories ($41.9k).
4. **Discounting destroys profit:** lines discounted ≥ 30% are **13.9% of lines but lose $135k** in total. Average profit per line goes from +$67 at 0% to **−$311 at 50%**.
5. **Regions:** West has a 14.9% margin, East 13.5%, South 11.9%, **Central only 7.9%**. Central also has the **highest average discount (24%)** vs West 11%.
6. **States:** **Texas −$25.7k** (average discount 37%), Ohio −$17.0k, Pennsylvania −$15.6k, Illinois −$12.6k. California (+$76k) and New York (+$74k) carry the profit.
7. **Customers:** the top 20% of customers produce **81% of profit** (but only 48% of sales). **155 customers are net loss-making.**
8. **Seasonality:** November (15.3%), December (14.2%) and September (13.4%) together are ~43% of annual sales; February is the weakest (2.6%).
9. **Segments and ship modes** have similar margins (11.5%–14%). They aren't the main lever.

## 7. Recommendations

1. **Cap discounts at 20%.** Above 20%, average profit turns negative. Require manager approval for anything higher, especially in Texas, Ohio, Pennsylvania and Illinois.
2. **Fix or drop Tables and Bookcases:** renegotiate supplier costs, raise prices, or bundle them with profitable chairs and furnishings.
3. **Central-region pricing review:** bring its 24% average discount in line with the West (11%). Closing that gap is the biggest single margin lever in the region.
4. **Grow the winners:** promote Copiers, Phones, Accessories and Paper (high margin) in campaigns and cross-sells.
5. **Customer strategy:** protect the top 20% (81% of profit) with account management; review pricing for the 155 loss-making customers.
6. **Plan inventory and staff for Sep–Dec,** which holds ~43% of annual sales.

## 8. Deliverables

`superstore_eda.ipynb` (cleaning → EDA → tests → insights) and a 1-page executive summary with these recommendations.
