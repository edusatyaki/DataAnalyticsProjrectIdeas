# 05 · E-commerce Orders Dashboard

**Module:** Power BI  **Dataset:** [Olist Brazilian E-commerce](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) (CC BY-NC-SA 4.0)

> **Data lives in [`../07_Ecommerce_Business_SQL/data/`](../07_Ecommerce_Business_SQL/data/)** (shared with project 07); column profile in [its DATA_PROFILE.md](../07_Ecommerce_Business_SQL/DATA_PROFILE.md).
> ⚠️ The bootcamp brief describes a **2023 Bangalore mobile-accessories company**. Olist is a stand-in with the same kind of order data. The method below works for either.

---

## 1. Project description

**Business context.** An online marketplace's leadership team wants one interactive report showing sales performance, customer behaviour, payment preferences, delivery performance and seller quality. They suspect late deliveries are hurting customer satisfaction.

**Objective.** Model ~100k orders across 8 related tables in Power BI, build DAX KPIs and deliver a 4-page report that management can slice by time, region and category.

**Stakeholders.** CEO and category managers, operations / logistics, customer-experience team, seller-success team.

**Key questions**
1. How are revenue, orders and AOV trending? Is the business growing?
2. Which categories and states generate the most revenue?
3. How do customers pay, and how many come back?
4. How fast are deliveries, how often are they late, and does lateness hurt reviews?
5. How concentrated is revenue among sellers?

## 2. Dataset

| Table | Rows | Key | Role |
|---|---|---|---|
| `olist_orders_dataset` | 99,441 | `order_id` | Order header: status + 5 timestamps |
| `olist_order_items_dataset` | 112,650 | `order_id + order_item_id` | **Main fact**: `price`, `freight_value`, `product_id`, `seller_id` |
| `olist_order_payments_dataset` | 103,886 | `order_id + payment_sequential` | Payment type, installments, value |
| `olist_order_reviews_dataset` | 99,225 | `review_id` | `review_score` 1–5 |
| `olist_customers_dataset` | 99,441 | `customer_id` | City/state; `customer_unique_id` = the real person |
| `olist_products_dataset` | 32,951 | `product_id` | Category (Portuguese), size/weight |
| `olist_sellers_dataset` | 3,095 | `seller_id` | Seller city/state |
| `product_category_name_translation` | 71 | `product_category_name` | Portuguese → English |
| `olist_geolocation_dataset.csv.gz` | 1.0 M | zip prefix | Optional, for maps (unzip first) |

---

## 3. Data cleaning (Power Query)

| # | Step | Detail |
|---|---|---|
| 1 | Types | All `*_timestamp` / `*_date` → Date/Time; `price`, `freight_value`, `payment_value` → Fixed Decimal |
| 2 | English categories | Merge `products` with `translation` (Left Outer) → `category_en`; replace nulls with **"unknown"** (610 products have no category) |
| 3 | Fix misspelt columns | Rename `product_name_lenght` → `product_name_length` (and the description column) |
| 4 | Delivery columns (orders) | `Delivery Days = Duration.Days(delivered − purchase)`; `Late Flag = delivered date > estimated date`; `Is Delivered = status = "delivered"` |
| 5 | Keep all 8 statuses | Needed for cancellation rate. Delivery measures use delivered orders only (3% of orders have no delivery date) |
| 6 | Reviews: one per order | Group by `order_id` → average `review_score` (a few orders have 2–3 reviews) |
| 7 | Payments: order level | Group by `order_id` → total `payment_value`, max `installments`, first `payment_type`. Avoids 1:many fan-out |
| 8 | Geolocation (optional) | Remove the **261,831 duplicate rows**; group by zip prefix → average lat/lng |
| 9 | Calendar table | DAX: `Calendar = CALENDAR(DATE(2016,9,1), DATE(2018,10,31))` + Year, Month, MonthName, YearMonth |
| 10 | Trim edge months | Sep–Dec 2016 and Sep–Oct 2018 have only a handful of orders; set a report-level filter of **Jan 2017 – Aug 2018** for trends |

**Model.** Star schema. `order_items` (fact) → `products`, `sellers`, `orders` (M:1); `orders` → `customers`, `Calendar`; the order-level payment and review tables → `orders` (1:1).

---

## 4. Analysis (EDA in Power BI)

**DAX measures**
```DAX
Revenue           = SUM(order_items[price])
Freight           = SUM(order_items[freight_value])
Orders            = DISTINCTCOUNT(orders[order_id])
AOV               = DIVIDE([Revenue], [Orders])
Customers         = DISTINCTCOUNT(customers[customer_unique_id])
Repeat Customers  = COUNTROWS(FILTER(VALUES(customers[customer_unique_id]), CALCULATE([Orders]) > 1))
Repeat Rate       = DIVIDE([Repeat Customers], [Customers])
Avg Delivery Days = CALCULATE(AVERAGE(orders[Delivery Days]), orders[Is Delivered] = TRUE())
Late %            = DIVIDE(CALCULATE([Orders], orders[Late Flag] = TRUE()), CALCULATE([Orders], orders[Is Delivered] = TRUE()))
Avg Review        = AVERAGE(reviews_order[review_score])
Cancel %          = DIVIDE(CALCULATE([Orders], orders[order_status] IN {"canceled","unavailable"}), [Orders])
Revenue PM        = CALCULATE([Revenue], DATEADD('Calendar'[Date], -1, MONTH))
Revenue MoM %     = DIVIDE([Revenue] - [Revenue PM], [Revenue PM])
```

| Page | Visuals |
|---|---|
| **1. Sales overview** | KPI cards (Revenue, Orders, AOV, Customers); monthly revenue + orders combo chart; top-10 categories bar; revenue by state (filled map) |
| **2. Customers & payments** | Payment-type donut; installments histogram; new vs repeat customers; top cities table |
| **3. Delivery & satisfaction** | Avg delivery days and Late % by state (map + bar); **review score: late vs on-time** (clustered bar); review-score distribution |
| **4. Sellers** | Top sellers by revenue; seller count by state; revenue vs average review scatter; Pareto line of seller revenue |

**Interactivity:** slicers (Date range, State, Category, Payment type), drill-through to Category and Seller pages, tooltips, and a "Late delivery story" bookmark.

---

## 5. Testing

**A. Report validation**

| Test | Pass condition |
|---|---|
| Revenue card = `SUM(price)` in Power Query | **13.59 M** BRL |
| Orders card = distinct `order_id` in orders | **99,441** |
| No fan-out: Revenue is unchanged when a Payment slicer is added to the page | Totals stay consistent |
| Category totals add up to the grand total (including "unknown") | Equal |
| Late % only counts delivered orders | Denominator = 96,470 delivered orders with dates |
| Spot-check 3 orders end to end (items, payment, review) against the raw CSV | Match |

**B. Analytical tests** (Python or Excel ToolPak alongside the report)

| Hypothesis | Result |
|---|---|
| H₀: review score is the same for late and on-time deliveries | **2.27 vs 4.29**, Welch t-test p ≈ 0. **Reject H₀** |
| H₀: delivery time is the same across states | SP 8.3 days vs RR 29 days. Large differences (ANOVA) |

---

## 6. Observations (from this data)

1. **Size:** **R$13.6 M revenue** (+R$2.25 M freight) from 99,441 orders; **AOV R$138**, median R$87 (a few big orders pull the mean up).
2. **Strong growth:** monthly orders grew from 800 (Jan 2017) to about 6,500–7,200 a month in 2018. Jan–Aug revenue rose **2.4× from 2017 to 2018**. **Black Friday (Nov 2017) was the top month** with 7,544 orders.
3. **Top categories:** health & beauty (R$1.26 M), watches & gifts (R$1.21 M), bed-bath-table (R$1.04 M), sports & leisure (R$0.99 M), computer accessories (R$0.91 M).
4. **Geography is concentrated:** São Paulo alone is **38%** of revenue; SP + RJ + MG = **63%**.
5. **Payments:** credit card **74%** of payment records (average 3.5 installments), boleto 19%, voucher 5.6%.
6. **Almost no repeat customers:** only **3.1%** of real customers ordered more than once.
7. **Delivery:** average 12.1 days (median 10); **6.8% arrive late**. SP gets orders in 8 days; the northern states (AM, AP, RR) wait 26–29 days.
8. **Late deliveries hurt reviews:** average review **2.27 for late vs 4.29 for on-time**; **62% of late orders get 1–2 stars** vs 9% of on-time ones.
9. **Seller concentration:** the **top 10% of sellers earn 67.5%** of revenue. Cancellations are low (1.2%).

## 7. Recommendations

1. **Fix late deliveries first.** It's the biggest lever on satisfaction. Pad delivery estimates for the northern and north-eastern states, and penalise or reward sellers on on-time dispatch.
2. **Build retention:** with 3% repeat customers, launch post-purchase email, loyalty points and a second-order coupon. Even reaching 6% repeat would add significant revenue.
3. **Plan for Black Friday:** stock, logistics capacity and support staffing for November.
4. **Grow outside SP:** targeted marketing and regional warehouses in RJ, MG and the South to cut delivery days and diversify revenue.
5. **Protect key sellers:** a seller-success programme for the top 10% (who make 2/3 of revenue), plus quality monitoring for low-review sellers.
6. **Promote installments** on high-ticket categories (watches, computers), since card buyers already use about 3.5 installments.

## 8. Deliverables

`Ecommerce_Dashboard.pbix` (4 pages), screenshots in the README, and 5 business recommendations.
