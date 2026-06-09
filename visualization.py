import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from matplotlib.gridspec import GridSpec

df = pd.read_csv("cleaned_sales_data.csv", parse_dates=["Date","OrderDate","DeliveryDate"])
df["YearMonth"] = pd.to_datetime(df["Date"]).dt.to_period("M")

# ── Palette ───────────────────────────────────────────────────────────────────
PALETTE = ["#534AB7", "#1D9E75", "#D85A30", "#BA7517", "#185FA5", "#D4537E", "#639922"]
sns.set_theme(style="whitegrid", font_scale=1.0)
plt.rcParams.update({"figure.facecolor": "white", "axes.facecolor": "white",
                     "font.family": "DejaVu Sans"})


# FIGURE 1 — Sales overview (2×2)
fig1, axes = plt.subplots(2, 2, figsize=(14, 10))
fig1.suptitle("Sales Overview", fontsize=16, fontweight="bold", y=1.01)

# 1a. Monthly revenue trend
monthly = (df.groupby("YearMonth")["TotalPrice"].sum()
             .reset_index().sort_values("YearMonth"))
monthly["YM_str"] = monthly["YearMonth"].astype(str)
ax = axes[0, 0]
ax.plot(monthly["YM_str"], monthly["TotalPrice"] / 1000, color=PALETTE[0],
        linewidth=2.5, marker="o", markersize=4)
ax.fill_between(monthly["YM_str"], monthly["TotalPrice"] / 1000, alpha=0.1,
                color=PALETTE[0])
ax.set_title("Monthly Revenue Trend", fontweight="bold")
ax.set_ylabel("Revenue ($K)")
ax.set_xlabel("")
tick_step = max(1, len(monthly) // 8)
ax.set_xticks(monthly["YM_str"].iloc[::tick_step])
ax.tick_params(axis="x", rotation=45)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}K"))

# 1b. Revenue by region (horizontal bar)
region_rev = (df.groupby("Region")["TotalPrice"].sum()
                .sort_values().reset_index())
ax = axes[0, 1]
bars = ax.barh(region_rev["Region"], region_rev["TotalPrice"] / 1000,
               color=PALETTE[:len(region_rev)])
ax.set_title("Revenue by Region", fontweight="bold")
ax.set_xlabel("Revenue ($K)")
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}K"))
for bar, val in zip(bars, region_rev["TotalPrice"]):
    ax.text(bar.get_width() + 5, bar.get_y() + bar.get_height() / 2,
            f"${val/1000:,.1f}K", va="center", fontsize=9)

# 1c. Revenue by product
prod_rev = (df.groupby("Product")["TotalPrice"].sum()
              .sort_values().reset_index())
ax = axes[1, 0]
bars = ax.barh(prod_rev["Product"], prod_rev["TotalPrice"] / 1000,
               color=PALETTE[:len(prod_rev)])
ax.set_title("Revenue by Product", fontweight="bold")
ax.set_xlabel("Revenue ($K)")
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}K"))
for bar, val in zip(bars, prod_rev["TotalPrice"]):
    ax.text(bar.get_width() + 2, bar.get_y() + bar.get_height() / 2,
            f"${val/1000:,.1f}K", va="center", fontsize=9)

# 1d. Quarterly revenue by year
df["YQ"] = df["Year"].astype(str) + " Q" + df["Quarter"].astype(str)
quarterly = (df.groupby(["Year","Quarter"])["TotalPrice"].sum()
               .reset_index().sort_values(["Year","Quarter"]))
quarterly["Label"] = quarterly["Year"].astype(str) + " Q" + quarterly["Quarter"].astype(str)
ax = axes[1, 1]
colors_q = [PALETTE[0] if y == 2023 else PALETTE[1] if y == 2024 else PALETTE[2]
            for y in quarterly["Year"]]
ax.bar(quarterly["Label"], quarterly["TotalPrice"] / 1000, color=colors_q, width=0.6)
ax.set_title("Quarterly Revenue by Year", fontweight="bold")
ax.set_ylabel("Revenue ($K)")
ax.tick_params(axis="x", rotation=45)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}K"))
from matplotlib.patches import Patch
ax.legend(handles=[Patch(color=PALETTE[0], label="2023"),
                   Patch(color=PALETTE[1], label="2024"),
                   Patch(color=PALETTE[2], label="2025")],
          loc="upper left", fontsize=9)

fig1.tight_layout()
fig1.savefig("fig1_sales_overview.png", dpi=150, bbox_inches="tight")
print("[✓] fig1_sales_overview.png saved")
plt.close()


# FIGURE 2 — Returns & discount analysis
fig2, axes = plt.subplots(2, 2, figsize=(14, 10))
fig2.suptitle("Returns & Discount Analysis", fontsize=16, fontweight="bold")

# 2a. Return rate by product
ret_prod = (df.groupby("Product")["Returned"].mean().sort_values() * 100)
ax = axes[0, 0]
ax.barh(ret_prod.index, ret_prod.values, color=PALETTE[2])
ax.axvline(df["Returned"].mean() * 100, color="gray", linestyle="--",
           label=f"Avg {df['Returned'].mean()*100:.1f}%")
ax.set_title("Return Rate by Product", fontweight="bold")
ax.set_xlabel("Return Rate (%)")
ax.legend(fontsize=9)
for i, v in enumerate(ret_prod.values):
    ax.text(v + 0.3, i, f"{v:.1f}%", va="center", fontsize=9)

# 2b. Return rate by region
ret_reg = (df.groupby("Region")["Returned"].mean().sort_values() * 100)
ax = axes[0, 1]
ax.barh(ret_reg.index, ret_reg.values, color=PALETTE[3])
ax.axvline(df["Returned"].mean() * 100, color="gray", linestyle="--",
           label=f"Avg {df['Returned'].mean()*100:.1f}%")
ax.set_title("Return Rate by Region", fontweight="bold")
ax.set_xlabel("Return Rate (%)")
ax.legend(fontsize=9)
for i, v in enumerate(ret_reg.values):
    ax.text(v + 0.3, i, f"{v:.1f}%", va="center", fontsize=9)

# 2c. Promotion revenue comparison
promo_rev = (df.groupby("Promotion")["TotalPrice"].sum()
               .sort_values(ascending=False).reset_index())
ax = axes[1, 0]
bars = ax.bar(promo_rev["Promotion"], promo_rev["TotalPrice"] / 1000,
              color=PALETTE[:len(promo_rev)])
ax.set_title("Revenue by Promotion Code", fontweight="bold")
ax.set_ylabel("Revenue ($K)")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}K"))
for bar, val in zip(bars, promo_rev["TotalPrice"]):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 5,
            f"${val/1000:,.1f}K", ha="center", fontsize=9)

# 2d. Discount bucket vs avg order value
disc_aov = (df.groupby("DiscountBucket")["TotalPrice"].mean()
              .reindex(["No Discount","Low (1–5%)","Mid (6–10%)","High (11–15%)"]))
ax = axes[1, 1]
ax.bar(disc_aov.index, disc_aov.values, color=PALETTE[4])
ax.set_title("Avg Order Value by Discount Tier", fontweight="bold")
ax.set_ylabel("Avg Order Value ($)")
ax.tick_params(axis="x", rotation=20)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
for i, v in enumerate(disc_aov.values):
    ax.text(i, v + 10, f"${v:,.0f}", ha="center", fontsize=9)

fig2.tight_layout()
fig2.savefig("fig2_returns_discounts.png", dpi=150, bbox_inches="tight")
print("[✓] fig2_returns_discounts.png saved")
plt.close()


# FIGURE 3 — Salesperson & operations
fig3, axes = plt.subplots(2, 2, figsize=(14, 10))
fig3.suptitle("Salesperson & Operations", fontsize=16, fontweight="bold")

# 3a. Revenue per salesperson
sp = (df.groupby("Salesperson")["TotalPrice"].sum()
        .sort_values(ascending=False).reset_index())
ax = axes[0, 0]
bars = ax.bar(sp["Salesperson"], sp["TotalPrice"] / 1000,
              color=PALETTE[:len(sp)])
ax.set_title("Revenue by Salesperson", fontweight="bold")
ax.set_ylabel("Revenue ($K)")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}K"))
for bar, val in zip(bars, sp["TotalPrice"]):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 3,
            f"${val/1000:,.1f}K", ha="center", fontsize=9)

# 3b. Salesperson return rate
sp_ret = (df.groupby("Salesperson")["Returned"].mean().sort_values() * 100)
ax = axes[0, 1]
ax.barh(sp_ret.index, sp_ret.values, color=PALETTE[2])
ax.axvline(df["Returned"].mean() * 100, color="gray", linestyle="--",
           label=f"Avg {df['Returned'].mean()*100:.1f}%")
ax.set_title("Return Rate by Salesperson", fontweight="bold")
ax.set_xlabel("Return Rate (%)")
ax.legend(fontsize=9)
for i, v in enumerate(sp_ret.values):
    ax.text(v + 0.3, i, f"{v:.1f}%", va="center", fontsize=9)

# 3c. Avg delivery days by region
deliv = (df.groupby("Region")["DeliveryDays"].mean().sort_values())
ax = axes[1, 0]
ax.barh(deliv.index, deliv.values, color=PALETTE[1])
ax.set_title("Avg Delivery Days by Region", fontweight="bold")
ax.set_xlabel("Days")
for i, v in enumerate(deliv.values):
    ax.text(v + 0.05, i, f"{v:.1f}d", va="center", fontsize=9)

# 3d. Payment method revenue split (pie)
pay = df.groupby("PaymentMethod")["TotalPrice"].sum()
ax = axes[1, 1]
wedges, texts, autotexts = ax.pie(
    pay.values, labels=pay.index, autopct="%1.1f%%",
    colors=PALETTE[:len(pay)], startangle=90,
    pctdistance=0.75, wedgeprops={"linewidth": 0.5, "edgecolor": "white"})
for at in autotexts:
    at.set_fontsize(9)
ax.set_title("Revenue by Payment Method", fontweight="bold")

fig3.tight_layout()
fig3.savefig("fig3_salesperson_ops.png", dpi=150, bbox_inches="tight")
print("[✓] fig3_salesperson_ops.png saved")
plt.close()


# FIGURE 4 — Heatmaps & correlation
fig4, axes = plt.subplots(1, 2, figsize=(14, 5))
fig4.suptitle("Product–Region Heatmaps", fontsize=16, fontweight="bold")

# 4a. Revenue heatmap: region × product
pivot_rev = df.pivot_table(values="TotalPrice", index="Region",
                           columns="Product", aggfunc="sum") / 1000
ax = axes[0]
sns.heatmap(pivot_rev, annot=True, fmt=".0f", cmap="YlOrRd",
            linewidths=0.5, ax=ax, cbar_kws={"label": "Revenue ($K)"})
ax.set_title("Revenue ($K): Region × Product", fontweight="bold")
ax.set_xlabel(""); ax.set_ylabel("")

# 4b. Return rate heatmap: region × product
pivot_ret = df.pivot_table(values="Returned", index="Region",
                           columns="Product", aggfunc="mean") * 100
ax = axes[1]
sns.heatmap(pivot_ret, annot=True, fmt=".1f", cmap="RdYlGn_r",
            linewidths=0.5, ax=ax, cbar_kws={"label": "Return Rate (%)"})
ax.set_title("Return Rate (%): Region × Product", fontweight="bold")
ax.set_xlabel(""); ax.set_ylabel("")

fig4.tight_layout()
fig4.savefig("fig4_heatmaps.png", dpi=150, bbox_inches="tight")
print("[✓] fig4_heatmaps.png saved")
plt.close()


# FIGURE 5 — Customer segment & correlation
fig5, axes = plt.subplots(1, 2, figsize=(14, 5))
fig5.suptitle("Customer Segments & Numeric Correlation", fontsize=16, fontweight="bold")

# 5a. Stacked bar: customer type revenue by product
cust_prod = df.pivot_table(values="TotalPrice", index="Product",
                           columns="CustomerType", aggfunc="sum") / 1000
cust_prod = cust_prod.sort_values(cust_prod.columns[0], ascending=False)
ax = axes[0]
cust_prod.plot(kind="bar", ax=ax, color=[PALETTE[0], PALETTE[1]],
               width=0.6, edgecolor="white")
ax.set_title("Revenue by Product & Customer Type", fontweight="bold")
ax.set_ylabel("Revenue ($K)")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}K"))
ax.tick_params(axis="x", rotation=30)
ax.legend(title="Customer Type")

# 5b. Correlation heatmap
corr_cols = ["Quantity","UnitPrice","Discount","TotalPrice",
             "ShippingCost","DeliveryDays","Returned"]
corr = df[corr_cols].corr()
ax = axes[1]
mask = np.triu(np.ones_like(corr, dtype=bool))
sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", center=0,
            mask=mask, linewidths=0.5, ax=ax,
            cbar_kws={"shrink": 0.8})
ax.set_title("Numeric Correlation Matrix", fontweight="bold")

fig5.tight_layout()
fig5.savefig("fig5_customer_correlation.png", dpi=150, bbox_inches="tight")
print("[✓] fig5_customer_correlation.png saved")
plt.close()

print("\n[✓] All 5 visualisation figures saved.")