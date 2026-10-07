# 07 · E-commerce Business Analysis (SQL)

**Module:** SQL  **Dataset:** [Olist Brazilian E-commerce](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce): ~100k real, anonymised orders from Sep 2016 to Oct 2018 (licence CC BY-NC-SA 4.0). Project 05 uses the same data.
**Column profile:** [DATA_PROFILE.md](DATA_PROFILE.md)

## Schema

```
customers (customer_id PK, customer_unique_id, zip, city, state)
   │1
   │n
orders (order_id PK, customer_id FK, order_status, purchase_ts, approved_at,
   │    delivered_carrier_date, delivered_customer_date, estimated_delivery_date)
   ├──< order_items (order_id, order_item_id, product_id FK, seller_id FK, shipping_limit_date, price, freight_value)
   ├──< order_payments (order_id, payment_sequential, payment_type, payment_installments, payment_value)
   └──< order_reviews (review_id, order_id, review_score, comment_title, comment_message, created, answered)
products (product_id PK, product_category_name, …dimensions)  ──  category_translation (pt → en)
sellers (seller_id PK, zip, city, state)
geolocation (zip_prefix, lat, lng, city, state)   -- not unique per zip!
```

## What the data check found

- **`customer_id` ≠ customer.** Every order gets a new `customer_id` (99,441 of them), but there are only 96,096 `customer_unique_id`s. Use `customer_unique_id` for repeat-customer analysis. Most customers buy only once.
- **An order can have many items, payments and reviews.** Joining items and payments directly multiplies rows. Aggregate each to the order level in a CTE first.
- `order_status`: 96,478 delivered; the rest are shipped, canceled, unavailable, invoiced, processing, created or approved. Delivery timestamps are NULL for undelivered orders (3% missing).
- Product category is missing for 610 products (1.9%). Two column names are misspelt in the source: `product_name_lenght` and `product_description_lenght`.
- Reviews: 88% have no title and 59% no message (they're in Portuguese). Some `review_id`s repeat across orders.
- **Geolocation has 261,831 exact duplicates** and several points per zip. Use `AVG(lat), AVG(lng) … GROUP BY zip` before joining. The geolocation file is gzipped. Load it with `\copy … FROM PROGRAM 'gunzip -c …'` or unzip it first.

## Step-by-step approach

1. **Load:** create 9 tables with proper types (TIMESTAMP, NUMERIC(10,2)), primary keys and foreign keys. Add indexes on `order_items(order_id)`, `orders(customer_id)` and `order_items(product_id)`.
2. **Sanity checks:**
   - Row counts per table
   - Orders with no items
   - `SUM(payment_value)` vs `SUM(price + freight_value)` per order (they should roughly match)
3. **Sales:**
   - Monthly revenue, orders and AOV, with MoM growth using `LAG()`
   - Revenue by category (English names) and the top 10 categories by revenue and by units
   - Revenue by customer state; seller state → customer state flows
4. **Customers:**
   - New vs returning customers per month (first order with `MIN() OVER (PARTITION BY customer_unique_id)`)
   - Repeat-purchase rate
   - RFM segments with `NTILE`
   - Monthly retention cohorts (first-order month × months since)
5. **Payments:**
   - Share of orders by payment type
   - Average installments by price band
   - Orders paid with more than one method
6. **Delivery & satisfaction:**
   - Average delivery days and % late by state
   - Average review score for late vs on-time orders (late orders score far lower)
   - Correlation between freight share and review score
7. **Sellers:**
   - Top sellers by revenue (`DENSE_RANK`)
   - Seller revenue concentration: what share comes from the top 10% of sellers?
   - Sellers with an average review below 3 and more than 50 orders
8. **Reusable objects:** create `VIEW order_summary` (one row per order with revenue, payment, review and delivery metrics), plus one stored function, e.g. `seller_scorecard(seller_id)`.
9. **Write up:** each query with its business question, SQL, a result snippet and an insight. End with 5 recommendations.

## Deliverables

`01_schema.sql`, `02_load.sql`, `03_analysis.sql`, `README` with insights. Optionally connect Power BI to the views (see project 05).
