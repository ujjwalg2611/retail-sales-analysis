import sqlite3, json
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, seaborn as sns

raw = pd.read_csv("data/raw_retail_sales.csv")
log = {"raw_rows": len(raw)}

# ---------- 1. DATA QUALITY AUDIT ----------
log["duplicate_rows"] = int(raw.duplicated().sum())
log["missing_region"] = int(raw["region"].isna().sum())
log["missing_quantity"] = int(raw["quantity"].isna().sum())
log["negative_prices"] = int((raw["unit_price"] < 0).sum())
log["inconsistent_category_case"] = int((raw["category"] != raw["category"].str.title()).sum())

# ---------- 2. CLEANING ----------
df = raw.drop_duplicates().copy()
df["category"] = df["category"].str.title().replace({"Home & Kitchen": "Home & Kitchen"})
df = df.dropna(subset=["quantity"])                       # cannot compute revenue
df["region"] = df["region"].fillna("Unknown")
df = df[df["unit_price"] > 0]                             # invalid prices
# outliers: flag prices > 3x the product's median
med = df.groupby("product")["unit_price"].transform("median")
log["price_outliers_removed"] = int((df["unit_price"] > 3 * med).sum())
df = df[df["unit_price"] <= 3 * med]
df["quantity"] = df["quantity"].astype(int)
df["order_date"] = pd.to_datetime(df["order_date"])
df["revenue"] = (df["quantity"] * df["unit_price"]).round(2)
df["month"] = df["order_date"].dt.to_period("M").astype(str)
log["clean_rows"] = len(df)
log["rows_removed_total"] = log["raw_rows"] - log["clean_rows"]

# ---------- 3. SQL ANALYSIS (SQLite) ----------
con = sqlite3.connect("data/retail.db")
df.assign(order_date=df["order_date"].dt.strftime("%Y-%m-%d")).to_sql("sales", con, if_exists="replace", index=False)
q = lambda s: pd.read_sql(s, con)
monthly = q("SELECT month, ROUND(SUM(revenue),2) AS revenue, COUNT(*) AS orders FROM sales GROUP BY month ORDER BY month")
by_cat = q("SELECT category, ROUND(SUM(revenue),2) AS revenue, ROUND(100.0*SUM(revenue)/(SELECT SUM(revenue) FROM sales),1) AS share_pct FROM sales GROUP BY category ORDER BY revenue DESC")
by_region = q("SELECT region, ROUND(SUM(revenue),2) AS revenue FROM sales GROUP BY region ORDER BY revenue DESC")
top_products = q("SELECT product, category, ROUND(SUM(revenue),2) AS revenue FROM sales GROUP BY product, category ORDER BY revenue DESC LIMIT 5")
aov = q("SELECT ROUND(AVG(revenue),2) AS aov FROM sales")["aov"][0]
q4 = monthly[monthly.month >= "2024-10"]["revenue"].sum() / monthly["revenue"].sum() * 100

# anomaly detection: monthly z-score
z = (monthly["revenue"] - monthly["revenue"].mean()) / monthly["revenue"].std()
monthly["z"] = z.round(2)

log.update(total_revenue=float(df["revenue"].sum()), aov=float(aov), q4_share_pct=round(float(q4),1),
           top_category=by_cat.iloc[0].to_dict(), top_product=top_products.iloc[0].to_dict(),
           top_region=by_region.iloc[0].to_dict(),
           peak_month=monthly.loc[monthly.revenue.idxmax(), "month"],
           lowest_month=monthly.loc[monthly.revenue.idxmin(), "month"],
           months_abs_z_gt_1=monthly[monthly.z.abs() > 1]["month"].tolist())

# ---------- 4. VISUALS ----------
sns.set_theme(style="whitegrid")
fig, ax = plt.subplots(figsize=(9,4.5)); sns.lineplot(data=monthly, x="month", y="revenue", marker="o", ax=ax)
ax.set_title("Monthly Revenue (2024, synthetic data)"); ax.tick_params(axis="x", rotation=45); plt.tight_layout(); plt.savefig("charts/monthly_revenue.png", dpi=150); plt.close()
fig, ax = plt.subplots(figsize=(7,4.5)); sns.barplot(data=by_cat, x="category", y="revenue", ax=ax)
ax.set_title("Revenue by Category"); plt.tight_layout(); plt.savefig("charts/revenue_by_category.png", dpi=150); plt.close()
fig, ax = plt.subplots(figsize=(6,4.5)); sns.barplot(data=by_region, x="region", y="revenue", ax=ax)
ax.set_title("Revenue by Region"); plt.tight_layout(); plt.savefig("charts/revenue_by_region.png", dpi=150); plt.close()
pv = df.pivot_table(index="category", columns="month", values="revenue", aggfunc="sum")
fig, ax = plt.subplots(figsize=(11,3.8)); sns.heatmap(pv/1000, cmap="YlGnBu", ax=ax, cbar_kws={"label":"Revenue (thousands)"})
ax.set_title("Category x Month Revenue Heatmap"); plt.tight_layout(); plt.savefig("charts/category_month_heatmap.png", dpi=150); plt.close()

df.to_csv("data/clean_retail_sales.csv", index=False)
json.dump(log, open("results.json","w"), indent=2, default=str)
print(json.dumps(log, indent=2, default=str)); print(by_cat); print(monthly)
