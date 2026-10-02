"""Builds dashboard.html (self-contained, no external libraries) from the cleaned data."""
import json, pandas as pd
df = pd.read_csv("data/clean_retail_sales.csv")
agg = (df.groupby(["month","category","region","product"])
         .agg(revenue=("revenue","sum"), orders=("order_id","count")).reset_index())
agg["revenue"] = agg["revenue"].round(2)
dq = json.load(open("results.json"))
data = {"rows": agg.to_dict("records"),
        "dq": {k: dq[k] for k in ["raw_rows","clean_rows","rows_removed_total","duplicate_rows","missing_region",
               "missing_quantity","negative_prices","inconsistent_category_case","price_outliers_removed"]}}
html = open("dashboard_template.html").read().replace("__DATA__", json.dumps(data, separators=(",",":")))
open("dashboard.html","w").write(html)
print("dashboard.html", len(html)//1024, "KB")
