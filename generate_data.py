"""Generate a SYNTHETIC retail transactions dataset with realistic data-quality issues.
Synthetic = not real company data. Seeded for reproducibility."""
import numpy as np, pandas as pd

rng = np.random.default_rng(42)
N = 12000
products = {
    "Electronics": [("Headphones", 1800), ("Smart Speaker", 3500), ("Power Bank", 1200), ("Webcam", 2400)],
    "Clothing": [("T-Shirt", 600), ("Jeans", 1800), ("Jacket", 3200), ("Sneakers", 2800)],
    "Home & Kitchen": [("Mixer Grinder", 3000), ("Cookware Set", 2500), ("Bedsheet", 900), ("Lamp", 700)],
    "Grocery": [("Rice 5kg", 450), ("Olive Oil", 650), ("Tea Pack", 300), ("Snack Box", 250)],
}
regions = ["North", "South", "East", "West"]
rows = []
dates = pd.date_range("2024-01-01", "2024-12-31")
for i in range(N):
    cat = rng.choice(list(products), p=[0.25, 0.30, 0.25, 0.20])
    name, price = products[cat][rng.integers(0, 4)]
    qty = int(rng.integers(1, 6))
    rows.append({
        "order_id": f"ORD{100000+i}", "order_date": rng.choice(dates),
        "category": cat, "product": name, "region": rng.choice(regions),
        "quantity": qty, "unit_price": round(price * rng.uniform(0.9, 1.1), 2),
        "customer_id": f"C{rng.integers(1, 3001):04d}",
    })
df = pd.DataFrame(rows)
df["order_date"] = pd.to_datetime(df["order_date"]).dt.strftime("%Y-%m-%d")

# --- inject data-quality issues ---
dup = df.sample(240, random_state=1); df = pd.concat([df, dup], ignore_index=True)       # duplicate rows
df.loc[df.sample(300, random_state=2).index, "region"] = np.nan                           # missing region
df.loc[df.sample(150, random_state=3).index, "quantity"] = np.nan                         # missing quantity
df.loc[df.sample(60, random_state=4).index, "unit_price"] = -df["unit_price"].abs()       # negative prices
df.loc[df.sample(25, random_state=5).index, "unit_price"] *= 40                           # price outliers
df.loc[df.sample(200, random_state=6).index, "category"] = df["category"].str.lower()     # inconsistent casing
df = df.sample(frac=1, random_state=7).reset_index(drop=True)
df.to_csv("data/raw_retail_sales.csv", index=False)
print("raw rows:", len(df))
