# 05 · E-commerce Orders Dashboard (Power BI)

**Module:** Power BI  **Dataset:** [Olist Brazilian E-commerce](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) (CC BY-NC-SA 4.0)

> **Data lives in [`../07_Ecommerce_Business_SQL/data/`](../07_Ecommerce_Business_SQL/data/)** so the ~120 MB isn't stored twice. See that folder's [DATA_PROFILE.md](../07_Ecommerce_Business_SQL/DATA_PROFILE.md) for every column.
>
> ⚠️ The bootcamp brief describes a **2023 Bangalore mobile-accessories company**. Olist is a stand-in with the same kind of order data. Get the exact file from Coding Ninjas if you can. The steps below work for either.

## Tables you need (Olist)

| Table | Rows | Key | Role |
|---|---|---|---|
| `olist_orders_dataset` | 99,441 | `order_id` | Fact header: status + 5 timestamps |
| `olist_order_items_dataset` | 112,650 | `order_id + order_item_id` | **Main fact**: `price`, `freight_value`, `product_id`, `seller_id` |
| `olist_order_payments_dataset` | 103,886 | `order_id + payment_sequential` | Payment type, installments, value |
| `olist_order_reviews_dataset` | 99,225 | `review_id` | `review_score` 1–5 |
| `olist_customers_dataset` | 99,441 | `customer_id` | City/state. Use `customer_unique_id` to count real customers (96,096) |
| `olist_products_dataset` | 32,951 | `product_id` | Category (in Portuguese), size/weight |
| `olist_sellers_dataset` | 3,095 | `seller_id` | Seller city/state |
| `product_category_name_translation` | 71 | `product_category_name` | Portuguese → English |
| `olist_geolocation_dataset.csv.gz` | 1.0 M | zip prefix | Optional, for maps. 261k duplicate rows, so average lat/lng per zip first |

## Step-by-step approach

1. **Power Query:**
   - Parse all timestamps as Date/Time
   - Merge the translation table into products (`category_en`), and replace a null category with "unknown"
   - Keep all 8 order statuses (you need `canceled`/`unavailable` for cancellation rate), but use only `delivered` orders in delivery-time measures
   - Add `Delivery Days = order_delivered_customer_date − order_purchase_timestamp` and `Late Flag = delivered > estimated`
2. **Model:** a star schema with `order_items` as the fact table. Relate it to orders (M:1), products, sellers and customers (through orders). Payments and reviews relate to orders by `order_id`, which is 1:many, so aggregate them first or use bridge measures. Build a **Calendar table** with `CALENDAR(MIN, MAX)` on purchase date.
3. **DAX measures:**
   ```DAX
   Revenue        = SUM(order_items[price])
   Freight        = SUM(order_items[freight_value])
   Orders         = DISTINCTCOUNT(orders[order_id])
   AOV            = DIVIDE([Revenue], [Orders])
   Customers      = DISTINCTCOUNT(customers[customer_unique_id])
   Repeat Rate    = DIVIDE(COUNTROWS(FILTER(VALUES(customers[customer_unique_id]), CALCULATE([Orders]) > 1)), [Customers])
   Avg Delivery Days = AVERAGE(orders[Delivery Days])
   Late %         = DIVIDE(CALCULATE([Orders], orders[Late Flag] = TRUE()), [Orders])
   Avg Review     = AVERAGE(reviews[review_score])
   Revenue MoM %  = DIVIDE([Revenue] - CALCULATE([Revenue], DATEADD('Calendar'[Date], -1, MONTH)), CALCULATE([Revenue], DATEADD('Calendar'[Date], -1, MONTH)))
   ```
4. **Page 1 – Sales overview:** KPI cards, a monthly revenue and orders trend (the data runs Sep 2016 – Oct 2018; filter to Jan 2017 – Aug 2018 because the edge months have only a handful of orders), revenue by category (top 10), and a revenue map by state.
5. **Page 2 – Customers & payments:** payment-type donut, an installments distribution, new vs repeat customers, and the top cities.
6. **Page 3 – Operations:** average delivery days and Late % by state, then late delivery against review score. This is the key story: late orders get much worse reviews.
7. **Page 4 – Sellers:** top sellers by revenue, seller count by state, and a revenue vs average review scatter.
8. Add slicers (Date, State, Category), drill-through to a category page, and bookmarks for a guided story.

## Deliverables

`Ecommerce_Dashboard.pbix` (3–4 pages), screenshots, and 5 business recommendations.
