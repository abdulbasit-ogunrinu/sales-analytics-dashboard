import pandas as pd
import numpy as np
import sys

# Windows consoles default to cp1252 and raise UnicodeEncodeError on the
# box-drawing / arrow / en-dash characters used in the report below.
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

df = pd.read_csv("cleaned_sales_data.csv", parse_dates=["Date","OrderDate","DeliveryDate"])
df["YearMonth"] = pd.to_datetime(df["Date"]).dt.to_period("M")

print("=" * 60)
print("PHASE 2 — EXPLORATORY DATA ANALYSIS")
print("=" * 60)

# Overall KPIs 
total_orders   = len(df)
total_revenue  = df["TotalPrice"].sum()
net_revenue    = df["NetRevenue"].sum()
avg_order      = df["TotalPrice"].mean()
return_rate    = df["Returned"].mean() * 100
avg_delivery   = df["DeliveryDays"].mean()
total_shipping = df["ShippingCost"].sum()

print("\n── OVERALL KPIs ──")
print(f"  Total Orders       : {total_orders:,}")
print(f"  Gross Revenue      : ${total_revenue:,.2f}")
print(f"  Net Revenue        : ${net_revenue:,.2f}")
print(f"  Revenue Lost (RET) : ${total_revenue - net_revenue:,.2f}")
print(f"  Avg Order Value    : ${avg_order:,.2f}")
print(f"  Return Rate        : {return_rate:.1f}%")
print(f"  Avg Delivery Days  : {avg_delivery:.1f}")
print(f"  Total Shipping Cost: ${total_shipping:,.2f}")

# Revenue by Region
print("\n── REVENUE BY REGION ──")
region = (df.groupby("Region")
            .agg(Orders=("OrderID","count"),
                 GrossRevenue=("TotalPrice","sum"),
                 NetRevenue=("NetRevenue","sum"),
                 AvgOrderValue=("TotalPrice","mean"),
                 ReturnRate=("Returned","mean"))
            .sort_values("GrossRevenue", ascending=False))
region["ReturnRate"] = (region["ReturnRate"] * 100).round(1)
region["GrossRevenue"] = region["GrossRevenue"].round(2)
region["NetRevenue"]   = region["NetRevenue"].round(2)
region["AvgOrderValue"]= region["AvgOrderValue"].round(2)
print(region.to_string())

#  Revenue by Product 
print("\n── REVENUE BY PRODUCT ──")
product = (df.groupby("Product")
             .agg(Orders=("OrderID","count"),
                  GrossRevenue=("TotalPrice","sum"),
                  AvgUnitPrice=("UnitPrice","mean"),
                  AvgQty=("Quantity","mean"),
                  ReturnRate=("Returned","mean"))
             .sort_values("GrossRevenue", ascending=False))
product["ReturnRate"]   = (product["ReturnRate"] * 100).round(1)
product["GrossRevenue"] = product["GrossRevenue"].round(2)
product["AvgUnitPrice"] = product["AvgUnitPrice"].round(2)
product["AvgQty"]       = product["AvgQty"].round(2)
print(product.to_string())

# Monthly revenue trend 
print("\n── MONTHLY REVENUE (first 12 & last 6 rows) ──")
monthly = (df.groupby("YearMonth")["TotalPrice"].sum()
             .reset_index()
             .sort_values("YearMonth"))
monthly.columns = ["YearMonth", "Revenue"]
print(monthly.to_string(index=False))

# Customer type analysis 
print("\n── CUSTOMER TYPE ──")
cust = (df.groupby("CustomerType")
          .agg(Orders=("OrderID","count"),
               Revenue=("TotalPrice","sum"),
               AvgOrder=("TotalPrice","mean"),
               ReturnRate=("Returned","mean"))
          .round(2))
cust["ReturnRate"] = (cust["ReturnRate"] * 100).round(1)
print(cust.to_string())

# Promotion impact 
print("\n── PROMOTION IMPACT ──")
promo = (df.groupby("Promotion")
           .agg(Orders=("OrderID","count"),
                Revenue=("TotalPrice","sum"),
                AvgOrder=("TotalPrice","mean"),
                AvgDiscount=("Discount","mean"))
           .sort_values("Revenue", ascending=False)
           .round(2))
promo["AvgDiscount"] = (promo["AvgDiscount"] * 100).round(1)
print(promo.to_string())

# Payment method 
print("\n── PAYMENT METHOD ──")
pay = (df.groupby("PaymentMethod")
         .agg(Orders=("OrderID","count"),
              Revenue=("TotalPrice","sum"),
              AvgOrder=("TotalPrice","mean"))
         .sort_values("Revenue", ascending=False)
         .round(2))
print(pay.to_string())

# Salesperson performance 
print("\n── SALESPERSON PERFORMANCE ──")
sales = (df.groupby("Salesperson")
           .agg(Orders=("OrderID","count"),
                Revenue=("TotalPrice","sum"),
                AvgDeal=("TotalPrice","mean"),
                ReturnRate=("Returned","mean"),
                AvgDelivery=("DeliveryDays","mean"))
           .sort_values("Revenue", ascending=False)
           .round(2))
sales["ReturnRate"] = (sales["ReturnRate"] * 100).round(1)
print(sales.to_string())

# Region manager effectiveness 
print("\n── REGION MANAGER ──")
mgr = (df.groupby("RegionManager")
         .agg(Orders=("OrderID","count"),
              Revenue=("TotalPrice","sum"),
              ReturnRate=("Returned","mean"),
              AvgShipping=("ShippingCost","mean"))
         .sort_values("Revenue", ascending=False)
         .round(2))
mgr["ReturnRate"] = (mgr["ReturnRate"] * 100).round(1)
print(mgr.to_string())

# Delivery days by region 
print("\n── DELIVERY DAYS BY REGION ──")
deliv = (df.groupby("Region")["DeliveryDays"]
           .agg(["mean","median","min","max"])
           .round(1))
print(deliv.to_string())

# Correlation matrix (numeric) 
print("\n── CORRELATION MATRIX ──")
corr_cols = ["Quantity","UnitPrice","Discount","TotalPrice","ShippingCost",
             "DeliveryDays","Returned"]
print(df[corr_cols].corr().round(3).to_string())

print("\n[✓] EDA complete.")

# ── Caveats that matter when reading the tables above ────────────────────────
print("\n" + "=" * 60)
print("CAVEATS — read before quoting any of the above")
print("=" * 60)

last_year = int(df["Date"].max().year)
last_month = int(df["Date"].max().month)
h1_cur = df[(df["Year"] == last_year) & (df["Month"] <= 6)]["TotalPrice"].sum()
h1_prev = df[(df["Year"] == last_year - 1) & (df["Month"] <= 6)]["TotalPrice"].sum()
prev_full = df[df["Year"] == last_year - 1]["TotalPrice"].sum()
print(f"\n1. {last_year} is a PARTIAL YEAR (ends month {last_month}).")
print(f"   Raw totals make it look like a {(h1_cur / prev_full - 1) * 100:.0f}% decline,")
print(f"   but H1-to-H1 is {(h1_cur / h1_prev - 1) * 100:+.1f}% and annualised")
print(f"   {last_year} is ${h1_cur * 2:,.0f} vs ${prev_full:,.0f} for {last_year - 1}.")
print("   Compare H1-to-H1 only.")

# Return-rate significance
from scipy import stats


def chi2_p(col):
    t = df.groupby(col)["Returned"].agg(["sum", "count"])
    tab = np.column_stack([t["sum"], t["count"] - t["sum"]])
    return float(stats.chi2_contingency(tab)[1])


print("\n2. Return-rate differences are NOT statistically significant:")
for c in ["Product", "Region", "CustomerType", "Salesperson"]:
    r = df.groupby(c)["Returned"].mean() * 100
    p = chi2_p(c)
    print(f"   {c:13} {r.min():.1f}%-{r.max():.1f}%  p = {p:.2f}  "
          f"{'significant' if p < 0.05 else '-> noise'}")

print("\n3. Revenue columns are raw sums, not per-order values. Order counts are")
print("   fairly even, so rankings mostly track volume — use AvgOrderValue to")
print("   separate basket size from order count.")

print("\n4. Promotion codes do not encode the discount actually granted, so the")
print("   promotion table cannot be used to judge promo effectiveness.")
print("   'No Promotion' orders are included (an earlier version silently lost them).")