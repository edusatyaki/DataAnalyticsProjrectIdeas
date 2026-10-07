# 06 · Retail Store Analytics

**Module:** SQL  **Dataset:** Retail Shop Case Study, the classic 3-table set ([Kaggle amark720](https://www.kaggle.com/datasets/amark720/retail-shop-case-study-dataset); that page now returns *permission denied*, so the files come from the public mirror [mrinalcs/sql-retail-data-analysis](https://github.com/mrinalcs/sql-retail-data-analysis))  **Column profile:** [DATA_PROFILE.md](DATA_PROFILE.md)

---

## 1. Project description

**Business context.** A multi-channel retailer (Flagship stores, MBR outlets, TeleShop, e-Shop) sells clothing, footwear, electronics, books, bags and home goods. Management wants SQL-based answers on who buys, what sells, which channel performs best and how much is lost to returns, to plan inventory and marketing.

**Objective.** Load 3 related tables into a relational database, clean them in SQL, and answer ~20 business questions with progressively advanced SQL (joins, CTEs, window functions, RFM).

**Stakeholders.** Retail head, category managers, channel managers, marketing.

**Key questions**
1. What are gross sales, returns and net revenue? How is revenue trending by year?
2. Which channel, category and subcategory earn the most?
3. Who are the customers (gender, age, city), and who are the most valuable?
4. Where are return rates highest?
5. Which customer segments (RFM) should marketing target?

## 2. Dataset

| Table | Rows | Columns |
|---|---|---|
| `Customer.csv` | 5,647 | `customer_Id` (PK), `DOB` (dd-mm-yyyy), `Gender` (M/F, 2 blank), `city_code` (1–10, 2 blank) |
| `Transactions.csv` | 23,053 | `transaction_id, cust_id, tran_date, prod_subcat_code, prod_cat_code, Qty, Rate, Tax, total_amt, Store_type` |
| `prod_cat_info.csv` | 23 | `prod_cat_code, prod_cat, prod_sub_cat_code, prod_subcat` |

**Joins:** `Transactions.cust_id → Customer.customer_Id`; `Transactions.(prod_cat_code, prod_subcat_code) → prod_cat_info.(prod_cat_code, prod_sub_cat_code)`. **Both columns are needed.**

---

## 3. Data cleaning (SQL, PostgreSQL syntax)

```sql
-- 1. Stage raw data as TEXT so nothing fails on load
CREATE TABLE transactions_stg (transaction_id TEXT, cust_id TEXT, tran_date TEXT, prod_subcat_code TEXT,
  prod_cat_code TEXT, qty TEXT, rate TEXT, tax TEXT, total_amt TEXT, store_type TEXT);
\copy transactions_stg FROM 'Transactions.csv' CSV HEADER

-- 2. Mixed date formats: 13,929 rows 'dd-mm-yyyy' + 9,124 rows 'd/m/yyyy' (both day-first)
-- 3. Cast types into the clean table
CREATE TABLE transactions AS
SELECT DISTINCT                                    -- 4. drops the 13 exact duplicate rows
       transaction_id::BIGINT, cust_id::INT,
       TO_DATE(REPLACE(tran_date, '/', '-'), 'DD-MM-YYYY') AS tran_date,
       prod_subcat_code::INT, prod_cat_code::INT, qty::INT, rate::NUMERIC, tax::NUMERIC,
       total_amt::NUMERIC, store_type,
       (qty::INT < 0) AS is_return                  -- 5. returns are negative rows
FROM transactions_stg;

-- 6. Customer: convert DOB, keep NULL gender/city (only 2 each), add age at the data's end date
CREATE TABLE customer AS
SELECT customer_id::INT, TO_DATE(dob,'DD-MM-YYYY') AS dob, NULLIF(gender,'') AS gender, NULLIF(city_code,'')::INT AS city_code
FROM customer_stg;

-- 7. Keys & indexes (transaction_id is NOT unique: a return reuses the sale's id)
ALTER TABLE customer ADD PRIMARY KEY (customer_id);
ALTER TABLE prod_cat_info ADD PRIMARY KEY (prod_cat_code, prod_sub_cat_code);
ALTER TABLE transactions ADD FOREIGN KEY (cust_id) REFERENCES customer(customer_id);
CREATE INDEX ON transactions (cust_id);
```

| # | Cleaning check | Finding |
|---|---|---|
| 1 | Date formats | 2 formats, both day-first. Range **25 Jan 2011 – 28 Feb 2014** (2014 has only 2 months) |
| 2 | Duplicates | 13 exact duplicate rows removed |
| 3 | Returns | 2,177 negative-qty rows. 2,175 `transaction_id`s appear twice (sale + return) |
| 4 | Tax rule | `tax = 10.5% × qty × rate` holds for every row, a nice integrity check |
| 5 | Nulls | Gender 2, city_code 2. Keep them; label as 'Unknown' in reports |
| 6 | Join check | The two-column join returns exactly 23,053 rows (a one-column join multiplies rows) |

---

## 4. Analysis (EDA with SQL)

**Data-prep questions**
1. Rows in each table; number of return transactions
2. Time range covered in days, months and years
3. Which category does "DIY" belong to?

**Business questions**
4. Most used channel (`Store_type`)
5. Male vs female customer count; city with the most customers
6. Subcategories under Books; maximum quantity ever ordered
7. Net revenue from Electronics + Books
8. Customers with more than 10 (non-return) transactions
9. Electronics + Clothing revenue at Flagship stores
10. Revenue from male customers in Electronics, by subcategory
11. % of sales and % of returns by subcategory, top 5 by sales
12. Net revenue from customers aged 25–35 in the last 30 days of data (`MAX(tran_date)` as "today")
13. Category with the highest return value in the last 3 months
14. Store type with the highest sales value and quantity
15. Categories with average revenue above the overall average
16. Average and total revenue by subcategory for the top 5 categories by quantity

**Advanced SQL**
- `RANK() OVER (PARTITION BY city_code ORDER BY net_spend DESC)`: top customers per city
- `LAG()`: month-on-month revenue growth
- **RFM:** `NTILE(5)` on recency, frequency and monetary → segments (Champions, Loyal, At-risk, Lost)
- Return rate by category: `SUM(CASE WHEN qty<0 THEN 1 END)::numeric / SUM(CASE WHEN qty>0 THEN 1 END)`
- Cohort: first-purchase month × months active

---

## 5. Testing

**A. SQL / data tests** (write each one as a query that must return 0 rows or the expected number)

| Test | Query idea | Expected |
|---|---|---|
| Row count | `SELECT COUNT(*) FROM transactions` | 23,040 after dedup |
| Orphan customers | `LEFT JOIN customer … WHERE c.customer_id IS NULL` | 0 |
| Orphan products | two-column `LEFT JOIN prod_cat_info … IS NULL` | 0 (and the join keeps 23,053 rows; a one-column join explodes to 57,166) |
| Tax integrity | `WHERE ABS(tax - 0.105*qty*rate) > 0.01` | 0 rows |
| Amount integrity | `WHERE ABS(ABS(total_amt) - (ABS(qty*rate) + tax)) > 0.01` (returns store total as −(qty×rate + tax)) | 0 rows |
| Every return has a sale | return ids without a positive row with the same id | **2** orphan returns. Report them |
| Net = gross + returns | reconcile the three sums | Equal |

**B. Statistical tests** (export query results to Excel/Python)

| Hypothesis | Result |
|---|---|
| H₀: category mix is independent of store type (chi-square on the Store × Category counts) | p = 0.90. **Fail to reject:** every channel sells the same mix |
| H₀: average purchase value of male = female customers (Welch t-test) | ₹2,604 vs ₹2,613 per transaction, p = 0.75. **Fail to reject:** spend per purchase is the same |

---

## 6. Observations (from this data)

1. **Revenue:** gross sales **₹54.5 M**, returns **−₹5.9 M (10.8% of gross)**, **net ₹48.6 M**.
2. **Trend:** net revenue was flat at ₹14.7 M (2011), ₹15.9 M (2012) and ₹15.7 M (2013). No growth. 2014 has only Jan–Feb.
3. **Channel:** **e-Shop is the biggest channel by far**: 9,311 transactions and ₹19.8 M, about 2× each of Flagship (₹9.7 M), MBR (₹9.7 M) and TeleShop (₹9.4 M).
4. **Categories:** **Books lead** (₹12.8 M), then Electronics ₹10.7 M and Home & kitchen ₹8.4 M. Bags are last (₹4.1 M).
5. **Top subcategories:** Electronics–Mobiles (₹2.25 M), Books–Fiction (₹2.23 M), Books–Children (₹2.21 M), Home–Tools and Footwear–Kids (₹2.15 M each).
6. **Returns** are about 10–11% of sales in every category (Bags 11.7% highest, Electronics 9.2% lowest).
7. **Customers:** 5,647 customers (2,892 M / 2,753 F) spread evenly across 10 cities (city 3 has the most, 595). They're young: age 21–44 at the end of the data (median 33).
8. **Low loyalty:** only **6 customers** made more than 10 purchase transactions.
9. Store type and category are independent (chi-square p = 0.90). Every channel sells the same mix.

## 7. Recommendations

1. **Invest in e-Shop.** It does as much business as the three physical channels together. Prioritise app/web UX, delivery and digital marketing.
2. **Reduce the 11% return rate,** starting with Bags and Footwear: better size guides, product photos and quality checks. Every 1 pp is about ₹0.5 M.
3. **Restart growth:** revenue has been flat for 3 years. Run category promotions in Books and Electronics (the top earners) and cross-sell Mobiles accessories.
4. **Loyalty programme:** very few repeat-heavy customers. Use the RFM segments for targeted offers to "At-risk" and "Loyal" groups.
5. **Differentiate channels:** since every channel sells the same mix, give Flagship stores an experience role (premium electronics, demos) and keep TeleShop for convenience categories.
6. **Target the 25–35 age group,** the core of the customer base, in campaigns.

## 8. Deliverables

`01_schema.sql`, `02_clean.sql`, `03_tests.sql`, `04_analysis.sql` (numbered questions with comments), and a README with the results table and insights.
