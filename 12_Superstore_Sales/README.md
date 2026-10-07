# 12 · Superstore Sales Analysis (Statistics & EDA)

**Module:** Statistics and EDA (Python)  **Dataset:** Tableau "Sample – Superstore" (US orders 2014–2017). This copy is from [Kaggle (vivek468)](https://www.kaggle.com/datasets/vivek468/superstore-dataset-final). The official download is on the [Tableau sample-data page](https://public.tableau.com/app/learn/sample-data).
**Column profile:** [DATA_PROFILE.md](DATA_PROFILE.md)

## File in `data/`

`Sample_Superstore.csv`: 9,994 order lines × 21 columns. **No missing values.** Total sales are $2.30 M and total profit $286k.

| Group | Columns |
|---|---|
| Order | `Row ID, Order ID` (5,009 orders), `Order Date, Ship Date` (m/d/yyyy text), `Ship Mode` (4) |
| Customer | `Customer ID, Customer Name` (793), `Segment` (Consumer/Corporate/Home Office) |
| Geography | `Country` (US only), `City` (531), `State` (49), `Postal Code`, `Region` (West/East/Central/South) |
| Product | `Product ID` (1,862), `Category` (3), `Sub-Category` (17), `Product Name` |
| Measures | `Sales, Quantity, Discount` (0–0.8), `Profit` (−6,600 to +8,400) |

## What the data check found

- **Encoding is Windows-1252**, not UTF-8: `pd.read_csv(..., encoding="cp1252")` or `"latin-1"`.
- Product names contain `#` and commas, so don't use `comment="#"`.
- Dates are text in m/d/yyyy format: `pd.to_datetime(df["Order Date"], format="%m/%d/%Y")`.
- `Product ID` is not unique to one product name (1,862 ids vs 1,848 names). Group by ID.
- **Discount destroys profit:** average profit per line is +$67 at 0% discount, +$25 at 20%, and **−$46 to −$311 at 30%–50%**. This is the headline story.

## Step-by-step approach

1. **Load & prep:**
   - Parse dates; add `Year, Month, Quarter, Weekday`
   - `Ship Days = Ship Date − Order Date`
   - `Profit Margin = Profit / Sales`
   - `Discount band` (0, 0–20%, 20–40%, 40%+)
2. **Univariate:**
   - Distributions of Sales and Profit (heavily right-skewed with fat tails, so try a log scale)
   - Outlier detection with IQR and z-score; list the top 10 loss-making lines
3. **Bivariate / multivariate:**
   - Sales, profit and margin by Category and Sub-Category: Tables, Bookcases and Supplies lose money
   - Region × Category profit heat map; state-level profit map (plotly choropleth)
   - Discount vs Profit scatter with a regression line, plus profit by discount band
   - Segment and Ship Mode comparisons
4. **Time series:**
   - Monthly sales and profit trend; YoY growth
   - Seasonality: September, November and December are the peak months
   - Rolling 3-month average
5. **Statistical tests:**
   - **Pearson/Spearman correlation**: Discount vs Profit, and Sales vs Profit
   - **ANOVA / Kruskal-Wallis**: does profit margin differ by Region? Follow up with Tukey HSD
   - **Chi-square**: Ship Mode vs Segment independence
   - **t-test**: profit of discounted vs non-discounted lines
   - Confidence interval for average order value
6. **Customer view:** Pareto analysis (do 20% of customers bring 80% of profit?), RFM segments, and top customers.
7. **Recommendations:** a discount cap, which sub-categories to fix or drop, and which regions to invest in. Back each with a number.

## Deliverables

`superstore_eda.ipynb` and an executive summary with 5 recommendations.
