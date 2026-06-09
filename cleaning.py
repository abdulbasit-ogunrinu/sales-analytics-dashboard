import pandas as pd
import numpy as np

# Load Dataset
df = pd.read_excel("Product-Sales-Region.xlsx")

print("=" * 60)
print("PHASE 1 — DATA CLEANING & PREPROCESSING")
print("=" * 60)

# Initial inspection
print("\n[1] Shape:", df.shape)
print("\n[2] Data types:\n", df.dtypes)
print("\n[3] Missing values:\n", df.isnull().sum())
print("\n[4] Duplicates:", df.duplicated().sum())

# Handle missing values 
# Promotion: NaN means no promo applied — fill with "None"
df["Promotion"] = df["Promotion"].fillna("None")
print("\n[5] Promotion nulls after fill:", df["Promotion"].isnull().sum())

# Drop duplicate rows (if any) 
before = len(df)
df = df.drop_duplicates()
print(f"[6] Rows removed (duplicates): {before - len(df)}")

# Fix / confirm data types
date_cols = ["Date", "OrderDate", "DeliveryDate"]
for col in date_cols:
    df[col] = pd.to_datetime(df[col])

df["Returned"] = df["Returned"].astype(int)  # already int, but enforce

#  Feature engineering 
# Delivery lead time in days
df["DeliveryDays"] = (df["DeliveryDate"] - df["OrderDate"]).dt.days

# Revenue after discount (cross-check against TotalPrice)
df["CalcRevenue"] = df["Quantity"] * df["UnitPrice"] * (1 - df["Discount"])

# Date parts for time-series analysis
df["Year"]    = df["Date"].dt.year
df["Month"]   = df["Date"].dt.month
df["Quarter"] = df["Date"].dt.quarter
df["YearMonth"] = df["Date"].dt.to_period("M")

# Net revenue: exclude returned orders
df["NetRevenue"] = df["TotalPrice"] * (1 - df["Returned"])

# Profit proxy: revenue minus shipping cost
df["GrossProfit"] = df["NetRevenue"] - df["ShippingCost"]

# Discount bucket
def discount_bucket(d):
    if d == 0:      return "No Discount"
    elif d <= 0.05: return "Low (1–5%)"
    elif d <= 0.10: return "Mid (6–10%)"
    else:           return "High (11–15%)"

df["DiscountBucket"] = df["Discount"].apply(discount_bucket)

# Outlier check on numeric columns 
num_cols = ["Quantity", "UnitPrice", "TotalPrice", "ShippingCost", "DeliveryDays"]
print("\n[7] Numeric summary after cleaning:\n")
print(df[num_cols].describe().round(2))

# Flag any negative or zero TotalPrice rows
bad_price = df[df["TotalPrice"] <= 0]
print(f"\n[8] Rows with TotalPrice <= 0: {len(bad_price)}")

# Validate key categorical columns 
print("\n[9] Unique value counts:")
for col in ["Region", "Product", "CustomerType", "PaymentMethod",
            "Promotion", "StoreLocation", "Salesperson", "RegionManager"]:
    print(f"   {col}: {df[col].nunique()} → {df[col].unique().tolist()}")

# Save cleaned dataset
df.to_csv("cleaned_sales_data.csv", index=False)
print("\n[✓] Cleaned dataset saved to cleaned_sales_data.csv")
print(f"    Final shape: {df.shape}")