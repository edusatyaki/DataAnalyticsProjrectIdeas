# 06 · Retail Store Analytics (SQL)

**Module:** SQL  **Dataset:** Retail Shop Case Study: the classic 3-table set listed on [Kaggle (amark720)](https://www.kaggle.com/datasets/amark720/retail-shop-case-study-dataset). The Kaggle page now returns *permission denied*, so these files come from a public mirror ([mrinalcs/sql-retail-data-analysis](https://github.com/mrinalcs/sql-retail-data-analysis)) with the same columns.
**Column profile:** [DATA_PROFILE.md](DATA_PROFILE.md)

## Files in `data/`

| Table | Rows | Columns |
|---|---|---|
| `Customer.csv` | 5,647 | `customer_Id` (PK), `DOB` (dd-mm-yyyy), `Gender` (M/F, 2 blank), `city_code` (1–10, 2 blank) |
| `Transactions.csv` | 23,053 | `transaction_id, cust_id, tran_date, prod_subcat_code, prod_cat_code, Qty, Rate, Tax, total_amt, Store_type` |
| `prod_cat_info.csv` | 23 | `prod_cat_code, prod_cat, prod_sub_cat_code, prod_subcat` |

**Relationships:** `Transactions.cust_id → Customer.customer_Id`; `Transactions.(prod_cat_code, prod_subcat_code) → prod_cat_info.(prod_cat_code, prod_sub_cat_code)`.

## What the data check found (these are the traps)

1. **Mixed date formats in `tran_date`:** 13,929 rows look like `28-02-2014` and 9,124 like `12/2/2014`. Both are day-first. Normalise them to DATE before any time analysis. The range is 25 Jan 2011 – 28 Feb 2014.
2. **Returns are negative rows.** 2,177 rows have `Qty < 0` with negative `Rate` and `total_amt`. A return reuses the original `transaction_id`, which is why only 20,878 of the 23,053 ids are unique. `transaction_id` is **not** a primary key.
3. **The product join needs two columns.** Subcategory codes repeat across categories (e.g. subcat 1 = *Women* under Clothing but *Mens* under Footwear and Bags). Join on both codes, or you'll multiply rows.
4. 13 exact duplicate rows in Transactions. Tax is 10.5% of `Qty × Rate`.

## Step-by-step approach

1. **Create the schema** (PostgreSQL or MySQL): load the CSVs into staging tables with `tran_date`/`DOB` as TEXT, then cast:
   ```sql
   -- PostgreSQL
   UPDATE transactions_stg SET tran_date = REPLACE(tran_date, '/', '-');
   CREATE TABLE transactions AS
   SELECT *, TO_DATE(tran_date, 'DD-MM-YYYY') AS tran_dt FROM transactions_stg;
   ```
   Add PK/FK constraints and an index on `cust_id`.
2. **Data-prep questions** (the classic case study):
   - Row count of each table; number of return transactions
   - Convert dates; find the time range covered (days, months, years)
   - Which category does subcategory "DIY" belong to?
3. **Analysis questions** (write one query each):
   - Most frequently used channel (`Store_type`)
   - Male vs female customer count
   - City with the most customers
   - Number of subcategories under Books
   - Maximum quantity ever ordered
   - Net revenue for Electronics + Books
   - Customers with more than 10 transactions (excluding returns)
   - Combined revenue from Electronics and Clothing at Flagship stores
   - Revenue from male customers in Electronics, by subcategory
   - % of sales and % of returns by subcategory (top 5 by sales)
   - Net revenue from customers aged 25–35 in the last 30 days of data, using `MAX(tran_dt)` as the reference date
   - Category with the highest value of returns in the last 3 months
   - Store type with the highest sales value and quantity
   - Categories whose average revenue is above the overall average
   - Average and total revenue by subcategory for the top 5 categories by quantity
4. **Advanced SQL to show off:**
   - `RANK()` customers by net spend within each city
   - Month-on-month revenue growth with `LAG()`
   - RFM segmentation: `NTILE(5)` on Recency, Frequency and Monetary
   - Return rate by category with `SUM(CASE WHEN Qty<0 …) / SUM(CASE WHEN Qty>0 …)`
   - A cohort table of first-purchase month × active months
5. **Write up:** for each query, give the business question, the SQL, the result and a one-line insight.

## Deliverables

`schema.sql`, `analysis.sql` (numbered questions), `README` with results and insights. Optional: a Power BI or Excel chart from the query outputs.
