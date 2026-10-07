"""Reproduce the numbers quoted in every project's Observations section.

Run from anywhere:  python tools/reference_findings.py  (needs pandas, scipy, scikit-learn)
These are reference answers for instructors. Students should derive them on their own first.
"""
import warnings
import numpy as np
import pandas as pd
from scipy import stats

warnings.filterwarnings("ignore")
from pathlib import Path
R = str(Path(__file__).resolve().parent.parent) + "/"
pd.set_option("display.width", 220)


def h(t):
    print(f"\n######## {t}")


# 01 Air quality
h("01 AIR")
a = pd.read_csv(R + "01_National_Air_Quality/data/city_day.csv", parse_dates=["Date"])
a["Year"] = a.Date.dt.year
print("avg AQI by city top/bottom:", a.groupby("City").AQI.mean().sort_values().round(0).to_dict())
print("AQI by year:", a.groupby("Year").AQI.mean().round(0).to_dict())
print("AQI by month:", a.groupby(a.Date.dt.month).AQI.mean().round(0).to_dict())
print("AQI>500 rows:", (a.AQI > 500).sum())
bad = a.AQI_Bucket.isin(["Poor", "Very Poor", "Severe"])
print("pct poor+ days by city:", (bad[a.AQI.notna()].groupby(a.City).mean() * 100).round(0).sort_values().to_dict())
lock = lambda y: a[(a.Date >= f"{y}-03-25") & (a.Date <= f"{y}-05-31")].groupby("City")[["PM2.5", "NO2", "AQI"]].mean()
l19, l20 = lock(2019), lock(2020)
ch = ((l20 / l19 - 1) * 100).round(0)
print("lockdown change median %:", ch.median().to_dict())
print("lockdown overall:", ((lock(2020).mean() / lock(2019).mean() - 1) * 100).round(1).to_dict())
print("corr with AQI:", a[["PM2.5", "PM10", "NO2", "CO", "SO2", "O3", "NOx", "NH3"]].corrwith(a.AQI).round(2).to_dict())
w = a[a.Date.dt.month.isin([11, 12, 1])].AQI.dropna(); m = a[a.Date.dt.month.isin([7, 8, 9])].AQI.dropna()
print("winter vs monsoon AQI:", w.mean().round(0), m.mean().round(0), stats.mannwhitneyu(w, m).pvalue)

# 02 Healthcare
h("02 HEALTH")
d = pd.read_csv(R + "02_US_Healthcare/data/healthcare_dataset.csv", parse_dates=["Date of Admission", "Discharge Date"]).drop_duplicates()
d["LOS"] = (d["Discharge Date"] - d["Date of Admission"]).dt.days
print("rows after dedup", len(d), "LOS", d.LOS.describe().round(1).to_dict())
dd = d[d["Billing Amount"] >= 0]
print("total bill", dd["Billing Amount"].sum().round(0), "avg", dd["Billing Amount"].mean().round(0))
for c in ["Medical Condition", "Insurance Provider", "Admission Type", "Medication"]:
    print(c, dd.groupby(c)["Billing Amount"].agg(["size", "mean"]).round(0).to_dict("index"))
print("LOS by type", d.groupby("Admission Type").LOS.mean().round(2).to_dict())
print("tests by cond", pd.crosstab(d["Medical Condition"], d["Test Results"], normalize="index").round(3).to_dict("index"))
print("anova bill~cond p", stats.f_oneway(*[g["Billing Amount"] for _, g in dd.groupby("Medical Condition")]).pvalue)
ct = pd.crosstab(d["Medical Condition"], d["Test Results"]); print("chi2 cond x test p", stats.chi2_contingency(ct)[1])
print("age by cond", d.groupby("Medical Condition").Age.mean().round(1).to_dict())
print("adm by year", d["Date of Admission"].dt.year.value_counts().sort_index().to_dict())
print("corr age bill", d.Age.corr(d["Billing Amount"]).round(3))

# 03 CPI
h("03 CPI")
n = pd.read_csv(R + "03_India_CPI_Inflation/data/cpi-national.csv", skiprows=1)
n["d"] = pd.to_datetime(dict(year=n.year, month=n.month, day=1))
print("avg inflation by year", n.groupby("year").combined_inflation.mean().round(2).to_dict())
print("months >6% by year", n.assign(o=n.combined_inflation > 6).groupby("year").o.sum().to_dict())
print("peak", n.loc[n.combined_inflation.idxmax(), ["d", "combined_inflation"]].tolist(), "low", n.loc[n.combined_inflation.idxmin(), ["d", "combined_inflation"]].tolist())
print("latest", n.iloc[-1].to_dict())
print("rural-urban mean gap", (n.rural_inflation - n.urban_inflation).mean().round(2))
c = pd.read_csv(R + "03_India_CPI_Inflation/data/cpi-categories.csv", skiprows=1)
lc = c[(c.year == 2026) & (c.month == 8) & (c.sector == "Combined")].sort_values("inflation_rate")
print("cat latest", lc.set_index("category").inflation_rate.to_dict())
s = pd.read_csv(R + "03_India_CPI_Inflation/data/cpi-states.csv", skiprows=1)
ls = s[(s.year == 2026) & (s.month == 8) & (s.sector == "Combined")].sort_values("inflation_rate")
print("states latest low", ls.head(5).set_index("state").inflation_rate.to_dict(), "high", ls.tail(5).set_index("state").inflation_rate.to_dict(), "n>6", (ls.inflation_rate > 6).sum())
it = pd.read_csv(R + "03_India_CPI_Inflation/data/cpi-items.csv", skiprows=1)
li = it[(it.year == 2026) & (it.month == 8)].sort_values("inflation_rate")
print("items low", li.head(5).set_index("item").inflation_rate.to_dict(), "high", li.tail(5).set_index("item").inflation_rate.to_dict())
print("corr rural/urban", n.rural_inflation.corr(n.urban_inflation).round(3))

# 04 IT spend
h("04 IT")
D = R + "04_IT_Department_Dashboard/data/"
f = pd.read_csv(D + "Fact.csv")
sc = pd.read_csv(D + "Scenario.csv"); ia = pd.read_csv(D + "IT_Area.csv"); ce = pd.read_csv(D + "Cost_Element.csv")
cr = pd.read_csv(D + "Country_Region.csv"); ba = pd.read_csv(D + "Business_Area.csv"); dep = pd.read_csv(D + "Department.csv")
f = f.merge(sc, on="Scenario ID").merge(ia, on="IT Sub Area ID").merge(ce, on="Cost Element ID").merge(cr, on="Country/Region ID").merge(ba, on="Business Area ID").merge(dep, on="Department", how="left")
print("orphans", f.isna().sum().to_dict())
tot = f.groupby("Scenario").Value.sum()
print("by scenario", (tot / 1e6).round(1).to_dict())
def av(col):
    p = f[f.Scenario.isin(["Actual", "Plan"])].pivot_table(index=col, columns="Scenario", values="Value", aggfunc="sum")
    p["var"] = p.Actual - p.Plan; p["var%"] = (p["var"] / p.Plan * 100).round(1)
    return (p.assign(Actual=p.Actual / 1e6, Plan=p.Plan / 1e6, var=p["var"] / 1e6).round(1).sort_values("var"))
for col in ["IT Area", "Business Area", "Sales Region", "Cost Element Group", "Date"]:
    print(col, av(col).to_dict("index"))
v = av("VP"); print("VP over", v.tail(5).to_dict("index")); print("VP under", v.head(3).to_dict("index"))
print("n VPs over plan", (v["var"] > 0).sum(), "of", len(v))
le = f.groupby("Scenario").Value.sum()
print("LE err vs actual %", ((le / le["Actual"] - 1) * 100).round(1).to_dict())

# 05/07 Olist
h("07 OLIST")
O = R + "07_Ecommerce_Business_SQL/data/"
o = pd.read_csv(O + "olist_orders_dataset.csv", parse_dates=["order_purchase_timestamp", "order_delivered_customer_date", "order_estimated_delivery_date"])
it = pd.read_csv(O + "olist_order_items_dataset.csv"); pay = pd.read_csv(O + "olist_order_payments_dataset.csv")
rv = pd.read_csv(O + "olist_order_reviews_dataset.csv"); cu = pd.read_csv(O + "olist_customers_dataset.csv")
pr = pd.read_csv(O + "olist_products_dataset.csv"); tr = pd.read_csv(O + "product_category_name_translation.csv")
pr = pr.merge(tr, on="product_category_name", how="left")
rev = it.price.sum(); print("revenue", round(rev / 1e6, 2), "freight", round(it.freight_value.sum() / 1e6, 2), "orders", o.order_id.nunique())
ordv = it.groupby("order_id").price.sum(); print("AOV", round(ordv.mean(), 1), "median", ordv.median())
ou = o.merge(cu, on="customer_id")
cnt = ou.groupby("customer_unique_id").order_id.nunique(); print("repeat rate %", round((cnt > 1).mean() * 100, 2))
x = it.merge(pr, on="product_id")
print("top cats", (x.groupby("product_category_name_english").price.sum() / 1e3).sort_values(ascending=False).head(8).round(0).to_dict())
print("state rev share", (it.merge(o, on="order_id").merge(cu, on="customer_id").groupby("customer_state").price.sum() / rev * 100).sort_values(ascending=False).head(5).round(1).to_dict())
print("pay type", (pay.payment_type.value_counts(normalize=True) * 100).round(1).to_dict(), "avg inst cc", pay[pay.payment_type == "credit_card"].payment_installments.mean().round(1))
dl = o[o.order_status == "delivered"].dropna(subset=["order_delivered_customer_date"]).copy()
dl["days"] = (dl.order_delivered_customer_date - dl.order_purchase_timestamp).dt.days
dl["late"] = dl.order_delivered_customer_date.dt.normalize() > dl.order_estimated_delivery_date
print("deliv days mean/median", dl.days.mean().round(1), dl.days.median(), "late %", round(dl.late.mean() * 100, 1))
r1 = rv.drop_duplicates("order_id").merge(dl, on="order_id")
print("review late vs ontime", r1.groupby("late").review_score.mean().round(2).to_dict(), "pct 1-2 star", r1.groupby("late").review_score.apply(lambda s: (s <= 2).mean() * 100).round(1).to_dict())
print("ttest", stats.ttest_ind(r1[r1.late].review_score, r1[~r1.late].review_score, equal_var=False).pvalue)
print("avg review", rv.review_score.mean().round(2), "dist", (rv.review_score.value_counts(normalize=True).sort_index() * 100).round(1).to_dict())
lst = dl.merge(cu, on="customer_id").groupby("customer_state").agg(days=("days", "mean"), late=("late", "mean"), n=("order_id", "size"))
print("state deliv", lst.sort_values("days").round(2).iloc[[0, 1, 2, -3, -2, -1]].to_dict("index"))
m = o.set_index("order_purchase_timestamp").resample("ME").order_id.count(); print("monthly orders", m["2017-01":"2018-08"].to_dict())
sel = it.groupby("seller_id").price.sum().sort_values(ascending=False); print("top10% sellers share", round(sel.head(int(len(sel) * .1)).sum() / sel.sum() * 100, 1))
print("cancel %", round(o.order_status.isin(["canceled", "unavailable"]).mean() * 100, 2))
print("yoy Jan-Aug", it.merge(o, on="order_id").assign(y=lambda t: t.order_purchase_timestamp.dt.year, mo=lambda t: t.order_purchase_timestamp.dt.month).query("mo<=8").groupby("y").price.sum().round(0).to_dict())

# 06 Retail
h("06 RETAIL")
P = R + "06_Retail_Store_SQL/data/"
t = pd.read_csv(P + "Transactions.csv"); c6 = pd.read_csv(P + "Customer.csv"); pc = pd.read_csv(P + "prod_cat_info.csv")
t["dt"] = pd.to_datetime(t.tran_date.str.replace("/", "-"), format="%d-%m-%Y")
t = t.merge(pc, left_on=["prod_cat_code", "prod_subcat_code"], right_on=["prod_cat_code", "prod_sub_cat_code"]).merge(c6, left_on="cust_id", right_on="customer_Id", how="left")
print("rows", len(t), "net rev", round(t.total_amt.sum() / 1e6, 2), "gross", round(t[t.Qty > 0].total_amt.sum() / 1e6, 2), "returns", round(t[t.Qty < 0].total_amt.sum() / 1e6, 2))
print("channel", t.groupby("Store_type").total_amt.agg(["size", "sum"]).round(0).to_dict("index"))
print("cat", (t.groupby("prod_cat").total_amt.sum() / 1e6).round(2).sort_values().to_dict())
print("return rate by cat %", (t[t.Qty < 0].groupby("prod_cat").size() / t[t.Qty > 0].groupby("prod_cat").size() * 100).round(1).to_dict())
print("gender cust", c6.Gender.value_counts().to_dict(), "top city", c6.city_code.value_counts().head(3).to_dict())
print("gender rev", (t.groupby("Gender").total_amt.sum() / 1e6).round(2).to_dict())
print("yearly", (t.groupby(t.dt.dt.year).total_amt.sum() / 1e6).round(2).to_dict())
print("subcat top", (t.groupby(["prod_cat", "prod_subcat"]).total_amt.sum() / 1e6).sort_values(ascending=False).head(5).round(2).to_dict())
ct = t[t.Qty > 0].groupby("cust_id").transaction_id.nunique(); print(">10 tx customers", (ct > 10).sum())
dob = pd.to_datetime(c6.DOB, format="%d-%m-%Y"); print("age at max date", ((t.dt.max() - dob).dt.days / 365.25).describe().round(1).to_dict())
print("chi2 store x cat p", stats.chi2_contingency(pd.crosstab(t.Store_type, t.prod_cat))[1])
print("dupes", t.duplicated(subset=["transaction_id", "cust_id", "tran_date", "Qty", "total_amt"]).sum())

# 08 COVID
h("08 COVID")
def load(k):
    df = pd.read_csv(R + f"08_COVID19_Analysis/data/time_series_covid19_{k}_global.csv").drop(columns=["Lat", "Long"]).groupby("Country/Region").sum(numeric_only=True).T
    df.index = pd.to_datetime(df.index, format="%m/%d/%y"); return df
cf, de = load("confirmed"), load("deaths")
w = cf.sum(1); wd = de.sum(1); nw = w.diff().clip(lower=0)
print("final", w.iloc[-1], wd.iloc[-1], "CFR", round(wd.iloc[-1] / w.iloc[-1] * 100, 2))
print("peak daily world 7d", nw.rolling(7).mean().idxmax(), round(nw.rolling(7).mean().max()))
dw = wd.diff().clip(lower=0).rolling(7).mean(); print("peak deaths 7d", dw.idxmax(), round(dw.max()))
print("top cases", (cf.iloc[-1].sort_values(ascending=False).head(8) / 1e6).round(1).to_dict())
print("top deaths", (de.iloc[-1].sort_values(ascending=False).head(8) / 1e3).round(0).to_dict())
cfr = (de.iloc[-1] / cf.iloc[-1] * 100)[cf.iloc[-1] > 1e6].sort_values(); print("CFR hi", cfr.tail(5).round(2).to_dict(), "lo", cfr.head(5).round(2).to_dict())
ind = cf["India"].diff().clip(lower=0).rolling(7).mean(); print("India peak", ind.idxmax(), round(ind.max()), "final", cf["India"].iloc[-1], de["India"].iloc[-1])
inds = ind.copy(); print("India 2022 peak", inds["2022"].idxmax(), round(inds["2022"].max()))
yr = w.resample("YE").last().diff(); print("cases by year", w.resample("YE").last().to_dict())
print("deaths by year", wd.resample("YE").last().to_dict())
nd = wd.diff().clip(lower=0); best = max(range(0, 36, 7), key=lambda L: nw.corr(nd.shift(-L))); print("best lag", best, {L: round(nw.corr(nd.shift(-L)), 3) for L in range(0, 36, 7)})
us = pd.read_csv(R + "08_COVID19_Analysis/data/time_series_covid19_deaths_US.csv")
st = us.groupby("Province_State").agg(pop=("Population", "sum"), d=(us.columns[-1], "sum")); st = st[st["pop"] > 0]; st["per100k"] = st.d / st["pop"] * 1e5
print("US per100k hi", st.per100k.sort_values().tail(4).round(0).to_dict(), "lo", st.per100k.sort_values().head(4).round(0).to_dict())

# 09 PhonePe
h("09 PHONEPE")
Q = R + "09_PhonePe_Digital_Payments/data/"
mt = pd.read_csv(Q + "map_transaction.csv"); at = pd.read_csv(Q + "aggregated_transaction.csv"); au = pd.read_csv(Q + "aggregated_user.csv"); am = pd.read_csv(Q + "aggregated_merchant.csv"); mm = pd.read_csv(Q + "map_merchant.csv")
y = mt.groupby("year")[["count", "amount"]].sum(); y["atv"] = y.amount / y["count"]
print("yearly value Lcr, count bn, ATV", (y.amount / 1e12).round(1).to_dict(), (y["count"] / 1e9).round(1).to_dict(), y.atv.round(0).to_dict())
print("CAGR value 18-25", round(((y.amount[2025] / y.amount[2018]) ** (1 / 7) - 1) * 100, 1), "count", round(((y["count"][2025] / y["count"][2018]) ** (1 / 7) - 1) * 100, 1))
mix = at.groupby(["year", "transaction_type"])["count"].sum().unstack(); print("mix %", (mix.div(mix.sum(1), axis=0) * 100).round(1).to_dict("index"))
s25 = mt[mt.year == 2025].groupby("state")[["amount", "count"]].sum(); s25["atv"] = s25.amount / s25["count"]
print("top states 2025 value share", (s25.amount / s25.amount.sum() * 100).sort_values(ascending=False).head(6).round(1).to_dict())
print("ATV hi", s25.atv.sort_values().tail(4).round(0).to_dict(), "lo", s25.atv.sort_values().head(4).round(0).to_dict())
d25 = mt[mt.year == 2025].groupby(["state", "district"]).amount.sum().sort_values(ascending=False); print("top districts", (d25.head(6) / 1e12).round(2).to_dict(), "top10 share", round(d25.head(10).sum() / d25.sum() * 100, 1), "n", len(d25))
g = mt[mt.year.isin([2024, 2025])].groupby(["state", "year"]).amount.sum().unstack(); g["yoy"] = (g[2025] / g[2024] - 1) * 100
print("yoy fast", g.yoy.sort_values().tail(5).round(1).to_dict(), "slow", g.yoy.sort_values().head(5).round(1).to_dict())
lu = au[(au.year == 2026) & (au.quarter == 2)].registered_count.sum(); lm = am[(am.year == 2026) & (am.quarter == 2)].registered_count.sum(); print("users latest", lu, "merchants", lm)
q = mt.groupby(["year", "quarter"]).amount.sum(); print("2019q4..2020q3", (q.loc[[(2019, 4), (2020, 1), (2020, 2), (2020, 3)]] / 1e12).round(2).to_dict())
uq = au[(au.year == 2025) & (au.quarter == 4)].set_index("state").registered_count; mq = am[(am.year == 2025) & (am.quarter == 4)].set_index("state").registered_count
r = (uq / mq).sort_values(); print("users per merchant hi", r.tail(4).round(0).to_dict(), "lo", r.head(4).round(0).to_dict(), "india", round(uq.sum() / mq.sum(), 1))
print("Q seasonality avg share", (mt[mt.year.between(2021, 2025)].groupby(["year", "quarter"]).amount.sum().groupby(level=0).transform(lambda s: s / s.sum()).groupby(level=1).mean() * 100).round(1).to_dict())

# 10 Loan
h("10 LOAN")
l = pd.read_csv(R + "10_Loan_Default_Analysis/data/Loan_default.csv")
for c in ["Education", "EmploymentType", "MaritalStatus", "HasMortgage", "HasDependents", "LoanPurpose", "HasCoSigner"]:
    ct = pd.crosstab(l[c], l.Default); chi2, p, _, _ = stats.chi2_contingency(ct); V = np.sqrt(chi2 / len(l) / (min(ct.shape) - 1))
    print(c, l.groupby(c).Default.mean().round(3).to_dict(), "p", f"{p:.1e}", "V", round(V, 3))
for c in ["Age", "Income", "LoanAmount", "CreditScore", "MonthsEmployed", "InterestRate", "DTIRatio", "NumCreditLines", "LoanTerm"]:
    a1, a0 = l[l.Default == 1][c], l[l.Default == 0][c]; dd_ = (a1.mean() - a0.mean()) / l[c].std()
    print(c, round(a0.mean(), 2), round(a1.mean(), 2), "d", round(dd_, 3), "p", f"{stats.mannwhitneyu(a1, a0).pvalue:.1e}")
l["ir"] = pd.cut(l.InterestRate, [0, 8, 13, 18, 25]); print("ir bands", l.groupby("ir", observed=True).Default.mean().round(3).to_dict())
l["inc"] = pd.qcut(l.Income, 4); print("income q", l.groupby("inc", observed=True).Default.mean().round(3).to_dict())
l["me"] = pd.cut(l.MonthsEmployed, [-1, 12, 36, 72, 120]); print("months emp", l.groupby("me", observed=True).Default.mean().round(3).to_dict())
yng = (l.Age < 30) & (l.InterestRate > 18) & (l.EmploymentType == "Unemployed"); print("young+highrate+unemp", yng.sum(), l[yng].Default.mean().round(3))
score = (l.Age < 30).astype(int) + (l.InterestRate > 18).astype(int) + (l.Income < 50000).astype(int) + (l.MonthsEmployed < 24).astype(int) + (l.HasCoSigner == "No").astype(int)
print("risk score", l.groupby(score).Default.agg(["size", "mean"]).round(3).to_dict("index"))
print("skew", l[["Income", "LoanAmount", "CreditScore"]].skew().round(3).to_dict())

# 11 Kabaddi
h("11 KABADDI")
K = R + "11_Pro_Kabaddi_League/data/"
k = pd.read_csv(K + "pkl_matches_s1_s10.csv")
fix = {"Dabang Delhi": "Dabang Delhi K.C.", "U.P. Yoddhas": "U.P. Yoddha"}
k[["team_1", "team_2", "winner"]] = k[["team_1", "team_2", "winner"]].replace(fix)
k["total"] = k.score_1 + k.score_2
print("pts per match by season", k.groupby("season").total.mean().round(1).to_dict())
print("margin by season", k.groupby("season").margin.mean().round(1).to_dict(), "close<=3 %", round((k.margin <= 3).mean() * 100, 1))
print("ties by season", k.groupby("season").winner.apply(lambda s: (s == "Tie").mean() * 100).round(1).to_dict())
print("finals", k[k.stage == "Final"][["season", "team_1", "score_1", "team_2", "score_2", "winner"]].to_string())
lt = pd.concat([k.rename(columns={"team_1": "team", "score_1": "pf", "score_2": "pa"}).assign(res=lambda x: np.where(x.winner == x.team, "W", np.where(x.winner == "Tie", "T", "L"))),
                k.rename(columns={"team_2": "team", "score_2": "pf", "score_1": "pa"}).assign(res=lambda x: np.where(x.winner == x.team, "W", np.where(x.winner == "Tie", "T", "L")))])[["season", "team", "pf", "pa", "res"]]
ts = lt.groupby("team").agg(m=("res", "size"), win=("res", lambda s: (s == "W").mean() * 100), pf=("pf", "mean"), pa=("pa", "mean")).round(1).sort_values("win")
print("all-time win %", ts.to_dict("index"))
sw = lt.groupby(["team", "season"]).res.apply(lambda s: (s == "W").mean() * 100).unstack().std(1).round(1); print("consistency std", sw.sort_values().to_dict())
early, late = k[k.season <= 4].total, k[k.season >= 5].total; print("early vs late total", early.mean().round(1), late.mean().round(1), stats.ttest_ind(early, late, equal_var=False).pvalue)
print("normality total shapiro p", stats.shapiro(k.total.sample(500, random_state=0)).pvalue, "skew", k.total.skew().round(2))
pm = pd.read_csv(K + "pkl_player_match_points.csv")
tp = pm.groupby(["player_id", "player_name"]).points.sum().sort_values(ascending=False); print("top players all-time", tp.head(8).to_dict())
print("super10 count", (pm.points >= 10).sum(), "top super10", pm[pm.points >= 10].groupby("player_name").size().sort_values(ascending=False).head(5).to_dict())
tm = pm.groupby(["season", "game_id", "team"]).points.apply(lambda s: s.nlargest(2).sum() / s.sum() if s.sum() else np.nan); print("top2 share mean", round(tm.mean() * 100, 1))
ag = pd.read_csv(K + "PKL_AggregatedTeamStats.csv"); print("agg cols", [c for c in ag.columns if not c.endswith("_rank")][:60])

# 12 Superstore
h("12 SUPERSTORE")
s = pd.read_csv(R + "12_Superstore_Sales/data/Sample_Superstore.csv", encoding="cp1252", parse_dates=["Order Date", "Ship Date"])
print("sales/profit/margin", round(s.Sales.sum()), round(s.Profit.sum()), round(s.Profit.sum() / s.Sales.sum() * 100, 1))
print("yearly", s.groupby(s["Order Date"].dt.year)[["Sales", "Profit"]].sum().round(0).to_dict("index"))
for c in ["Category", "Region", "Segment", "Ship Mode"]:
    g = s.groupby(c)[["Sales", "Profit"]].sum(); g["m"] = g.Profit / g.Sales * 100; print(c, g.round(1).to_dict("index"))
g = s.groupby("Sub-Category")[["Sales", "Profit"]].sum(); g["m"] = g.Profit / g.Sales * 100; print("subcat", g.sort_values("Profit").round(1).to_dict("index"))
st = s.groupby("State").Profit.sum().sort_values(); print("state worst", st.head(5).round(0).to_dict(), "best", st.tail(5).round(0).to_dict())
print("disc>=0.3 share lines", round((s.Discount >= .3).mean() * 100, 1), "their profit", round(s[s.Discount >= .3].Profit.sum()))
print("corr disc profit pearson/spearman", s.Discount.corr(s.Profit).round(3), s.Discount.corr(s.Profit, method="spearman").round(3), "disc margin", s.Discount.corr(s.Profit / s.Sales).round(3))
print("ttest disc vs none", stats.ttest_ind(s[s.Discount > 0].Profit, s[s.Discount == 0].Profit, equal_var=False).pvalue)
s["mg"] = s.Profit / s.Sales; print("kruskal margin region", stats.kruskal(*[g.mg for _, g in s.groupby("Region")]).pvalue)
print("chi2 ship x segment", stats.chi2_contingency(pd.crosstab(s["Ship Mode"], s.Segment))[1])
cp = s.groupby("Customer ID").Profit.sum().sort_values(ascending=False); print("top20% cust profit share", round(cp.head(int(len(cp) * .2)).sum() / cp.sum() * 100, 1), "loss customers", (cp < 0).sum())
cs = s.groupby("Customer ID").Sales.sum().sort_values(ascending=False); print("top20% cust sales share", round(cs.head(int(len(cs) * .2)).sum() / cs.sum() * 100, 1))
print("ship days", (s["Ship Date"] - s["Order Date"]).dt.days.groupby(s["Ship Mode"]).mean().round(1).to_dict())
print("region disc", s.groupby("Region").Discount.mean().round(3).to_dict())
tx = s[(s.State == "Texas")]; print("Texas avg disc", tx.Discount.mean().round(2))
mo = s.groupby(s["Order Date"].dt.month).Sales.sum(); print("month share %", (mo / mo.sum() * 100).round(1).to_dict())
ov = s.groupby("Order ID").Sales.sum(); ci = stats.t.interval(.95, len(ov) - 1, ov.mean(), stats.sem(ov)); print("AOV", round(ov.mean(), 1), [round(x, 1) for x in ci])

# 13 Credit risk
h("13 CREDIT")
c = pd.read_csv(R + "13_Credit_Risk_Modelling/data/credit_risk_dataset.csv").drop_duplicates()
c = c[(c.person_age <= 100) & ((c.person_emp_length <= 60) | c.person_emp_length.isna())]
print("rows", len(c), "default", round(c.loan_status.mean() * 100, 1))
for col in ["loan_intent", "person_home_ownership", "cb_person_default_on_file", "loan_grade"]:
    print(col, c.groupby(col).loan_status.mean().round(3).to_dict())
c["lpi"] = pd.cut(c.loan_percent_income, [0, .1, .2, .3, .4, 1]); print("lpi", c.groupby("lpi", observed=True).loan_status.mean().round(3).to_dict())
c["inc"] = pd.qcut(c.person_income, 5); print("income q", c.groupby("inc", observed=True).loan_status.mean().round(3).to_dict())
print("int rate by grade", c.groupby("loan_grade").loan_int_rate.agg(["mean", "min", "max"]).round(1).to_dict("index"))
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score, average_precision_score
c["loan_int_rate"] = c.groupby("loan_grade").loan_int_rate.transform(lambda s: s.fillna(s.median()))
c["person_emp_length"] = c.person_emp_length.fillna(c.person_emp_length.median())
c["log_inc"] = np.log(c.person_income)
cat = ["person_home_ownership", "loan_intent", "loan_grade", "cb_person_default_on_file"]
num = ["person_age", "log_inc", "person_emp_length", "loan_amnt", "loan_int_rate", "loan_percent_income", "cb_person_cred_hist_length"]
X, yv = c[cat + num], c.loan_status
Xtr, Xte, ytr, yte = train_test_split(X, yv, test_size=.2, stratify=yv, random_state=42)
def fit(cats, nums, model):
    pre = ColumnTransformer([("c", OneHotEncoder(handle_unknown="ignore"), cats), ("n", StandardScaler(), nums)])
    p = Pipeline([("p", pre), ("m", model)]).fit(Xtr[cats + nums], ytr); pr_ = p.predict_proba(Xte[cats + nums])[:, 1]
    from sklearn.metrics import roc_curve
    fpr, tpr, _ = roc_curve(yte, pr_)
    return round(roc_auc_score(yte, pr_), 3), round(average_precision_score(yte, pr_), 3), round(max(tpr - fpr), 3)
print("LR full", fit(cat, num, LogisticRegression(max_iter=2000, class_weight="balanced")))
print("GBM full", fit(cat, num, HistGradientBoostingClassifier(random_state=0)))
c2 = [x for x in cat if x != "loan_grade"]; n2 = [x for x in num if x != "loan_int_rate"]
print("LR no grade/rate", fit(c2, n2, LogisticRegression(max_iter=2000, class_weight="balanced")))
print("GBM no grade/rate", fit(c2, n2, HistGradientBoostingClassifier(random_state=0)))
c["ab"] = pd.cut(c.person_age, [19, 25, 35, 50, 100]); print("age bands", c.groupby("ab", observed=True).loan_status.mean().round(3).to_dict())
