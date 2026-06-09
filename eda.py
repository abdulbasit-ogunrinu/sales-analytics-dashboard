import pandas as pd
import numpy as np

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