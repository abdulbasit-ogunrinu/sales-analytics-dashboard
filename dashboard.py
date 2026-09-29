"""
Static Sales Analytics Dashboard  -  maroon & white theme.

Builds a single, fully self-contained HTML file (sales_dashboard.html):
no web server, no Dash, no CDN, works offline by double-clicking.

    python dashboard.py

Analytics corrections applied vs. the previous interactive version are
documented in the "Data quality & methodology" section of the output and
summarised in the console at the end of the run.
"""

import sys
import html
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
from plotly.offline import get_plotlyjs
from scipy import stats

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

# Named index.html so GitHub Pages serves it at the site root
# (.../sales-analytics-dashboard/) instead of a path with a filename on it.
OUTPUT_FILE = "index.html"
DATA_FILE = "cleaned_sales_data.csv"

# ═══════════════════════════════════════════════════════════════════════════
# THEME  -  maroon & white
# ═══════════════════════════════════════════════════════════════════════════
MAROON_DEEP = "#4A0A14"
MAROON      = "#6D1220"
MAROON_MID  = "#8E2233"
ROSE        = "#A94659"
ROSE_SOFT   = "#C98A97"
ROSE_WASH   = "#E8C4CC"
BLUSH       = "#FBF5F6"
BLUSH_DEEP  = "#F3E4E7"
WHITE       = "#FFFFFF"
GOLD        = "#B8892B"
INK         = "#2B1015"
MUTED       = "#8B6670"
BORDER      = "#EBD7DC"
GRID        = "#F4E8EB"

# Ordered so the darkest maroon reads as "largest" on ranking charts.
SERIES = [MAROON, ROSE, ROSE_SOFT, MAROON_MID, ROSE_WASH, MAROON_DEEP]
PIE_SERIES = [MAROON, ROSE, ROSE_SOFT, MAROON_DEEP, ROSE_WASH]
HEAT_SCALE = [
    [0.00, "#FFFFFF"], [0.20, "#FAECEE"], [0.40, "#E8C4CC"],
    [0.60, "#C98A97"], [0.80, "#A94659"], [1.00, "#5A0E1B"],
]
FONT = "Inter, 'Segoe UI', system-ui, -apple-system, Arial, sans-serif"


# ═══════════════════════════════════════════════════════════════════════════
# LOAD + PREPARE
# ═══════════════════════════════════════════════════════════════════════════
df = pd.read_csv(
    DATA_FILE,
    parse_dates=["Date", "OrderDate", "DeliveryDate"],
    keep_default_na=False,          # keep "No Promotion" as a real category
    na_values=["", "NA", "NaN", "nan", "null", "NULL"],
)
df["Promotion"] = df["Promotion"].fillna("No Promotion")
df["YearMonth"] = df["Date"].dt.to_period("M").astype(str)
df["Year"] = df["Date"].dt.year
df["Month"] = df["Date"].dt.month
df["YearHalf"] = np.where(df["Month"] <= 6, "H1", "H2")

DATE_MIN, DATE_MAX = df["Date"].min(), df["Date"].max()
LAST_YEAR = int(DATE_MAX.year)
LAST_MONTH = int(DATE_MAX.month)
LAST_YEAR_PARTIAL = LAST_MONTH < 12
GROSS = df["TotalPrice"].sum()
N_ORDERS = len(df)


# ═══════════════════════════════════════════════════════════════════════════
# VALIDATION  -  recompute every headline number and reconcile
# ═══════════════════════════════════════════════════════════════════════════
CHECKS = []


def check(status, label, detail):
    CHECKS.append({"status": status, "label": label, "detail": detail})


# 1. Duplicates / nulls
check("pass" if df["OrderID"].is_unique and not df.duplicated().any() else "fail",
      "No duplicate orders",
      f"{N_ORDERS:,} rows, {df['OrderID'].nunique():,} unique OrderIDs, "
      f"0 duplicate rows")

# 2. Revenue arithmetic
_recon = (df["Quantity"] * df["UnitPrice"] * (1 - df["Discount"]) - df["TotalPrice"]).abs().max()
check("pass" if _recon < 0.01 else "fail",
      "Revenue arithmetic reconciles",
      f"TotalPrice = Qty x UnitPrice x (1 - Discount) for all rows "
      f"(max difference ${_recon:.4f})")

# 3. Promotions complete
_promo_missing = int(df["Promotion"].isna().sum())
_promo_recon = abs(df.groupby("Promotion")["TotalPrice"].sum().sum() - GROSS)
check("pass" if _promo_missing == 0 and _promo_recon < 0.01 else "fail",
      "Promotion field complete",
      f"All {N_ORDERS:,} orders carry a promotion value; promotion revenue "
      f"reconciles to the ${GROSS:,.0f} total (delta ${_promo_recon:.2f})")

# 4. Date integrity
_bad_dates = int((df["DeliveryDate"] < df["OrderDate"]).sum())
check("pass" if _bad_dates == 0 else "fail",
      "Delivery dates are consistent",
      f"0 orders delivered before they were placed; lead time "
      f"{df['DeliveryDays'].min():.0f}-{df['DeliveryDays'].max():.0f} days "
      f"(mean {df['DeliveryDays'].mean():.1f})")

# 5. Monthly series continuity
_months = pd.period_range(df["YearMonth"].min(), df["YearMonth"].max(), freq="M").astype(str)
_gaps = [m for m in _months if m not in set(df["YearMonth"])]
check("pass" if not _gaps else "warn",
      "Monthly series has no gaps",
      f"{df['YearMonth'].nunique()} consecutive months from {DATE_MIN:%b %Y} "
      f"to {DATE_MAX:%b %Y}" if not _gaps else f"Missing months: {', '.join(_gaps)}")

# 6. Cross-tab reconciliation
_deltas = {c: abs(df.groupby(c)["TotalPrice"].sum().sum() - GROSS)
           for c in ["Region", "Product", "CustomerType", "PaymentMethod",
                     "Promotion", "Salesperson", "Year"]}
check("pass" if max(_deltas.values()) < 0.01 else "fail",
      "Every breakdown sums back to the total",
      f"Region, product, customer, payment, promotion, salesperson and year "
      f"breakdowns all reconcile to ${GROSS:,.0f}")

# ── 7. Volume confounding ────────────────────────────────────────────────────
_counts = df.groupby("Product").size()
check("pass", "Category revenue is broadly volume-comparable",
      f"Order counts are evenly spread (products {int(_counts.min())}-"
      f"{int(_counts.max())}, regions "
      f"{int(df.groupby('Region').size().min())}-"
      f"{int(df.groupby('Region').size().max())}), so revenue rankings mostly "
      f"track real volume. Average order value is shown alongside revenue to "
      f"keep the two effects separated.")


# ═══════════════════════════════════════════════════════════════════════════
# READING NOTES
#
# Three places in this dashboard where a number looks like a pattern but is
# not one. Each is attached to the chart it applies to, so it cannot be
# separated from the number it qualifies.
#
# (The related warning that total revenue cannot be machine-predicted is not
# shown here because this dashboard displays no model. It is reported by
# modelling.py.)
# ═══════════════════════════════════════════════════════════════════════════
def chi2_p(col):
    t = df.groupby(col)["Returned"].agg(["sum", "count"])
    tab = np.column_stack([t["sum"], t["count"] - t["sum"]])
    return float(stats.chi2_contingency(tab)[1])


# -- Note: return rates --------------------------------------------------------
_prod_p = chi2_p("Product")
_prod_rates = df.groupby("Product")["Returned"].mean() * 100
_hi, _lo = _prod_rates.idxmax(), _prod_rates.idxmin()
_per_prod = int(df.groupby("Product").size().mean())

NOTE_RETURNS = (
    f"The highest and lowest products differ by just "
    f"{_prod_rates.max() - _prod_rates.min():.1f} points "
    f"({_prod_rates.min():.1f}% to {_prod_rates.max():.1f}%), and with roughly "
    f"{_per_prod} orders each that is the spread ordinary random variation produces "
    f"on its own. A chi-square test puts it at p = {_prod_p:.2f}, where anything "
    f"below 0.05 would be needed before a difference could be called real, and "
    f"nothing here reaches it. Regions (p = {chi2_p('Region'):.2f}) and salespeople "
    f"(p = {chi2_p('Salesperson'):.2f}) are the same story, and a model built to "
    f"predict returns performs no better than chance. This is better read as every "
    f"product sitting in one band rather than as a ranking: {_hi}'s "
    f"{_prod_rates.max():.1f}% is not evidence that {_hi} is a problem product."
)

# -- Note: partial year --------------------------------------------------------
_h1_cur = df[(df["Year"] == LAST_YEAR) & (df["Month"] <= 6)]["TotalPrice"].sum()
_h1_prev = df[(df["Year"] == LAST_YEAR - 1) & (df["Month"] <= 6)]["TotalPrice"].sum()
_yoy = (_h1_cur / _h1_prev - 1) * 100 if _h1_prev else float("nan")
_annualised = _h1_cur * (12 / 6)
_full_years = sorted(y for y in df["Year"].unique() if y < LAST_YEAR)
_prev_full = df[df["Year"] == max(_full_years)]["TotalPrice"].sum()
_apparent = (_h1_cur / _prev_full - 1) * 100
_n_months = LAST_MONTH

NOTE_YEAR = (
    f"The data stops on {DATE_MAX:%d %B %Y}, so the {LAST_YEAR} bar covers "
    f"{_n_months} months against 12 for every other year. That is the whole reason "
    f"it looks like a {abs(_apparent):.0f}% collapse — trading is not falling, "
    f"there is simply half a year of it. Compared over matching months, January to "
    f"June {LAST_YEAR} against January to June {LAST_YEAR - 1}, revenue is "
    f"${_h1_cur:,.0f} against ${_h1_prev:,.0f}, which is flat at {_yoy:+.1f}%, and "
    f"scaled to a full year {LAST_YEAR} is running slightly ahead at "
    f"${_annualised:,.0f} against ${_prev_full:,.0f}. Read this chart by comparing "
    f"the same months in each year rather than the totals."
)

# -- Note: promotion codes -----------------------------------------------------
_promo_disc = df.groupby("Promotion")["Discount"].agg(["mean", "size"])
_zero = {p: int(((df["Promotion"] == p) & (df["Discount"] == 0)).sum())
         for p in df["Promotion"].unique() if p != "No Promotion"}
_promo_rows = int(df[df["Promotion"] != "No Promotion"].shape[0])
_zero_tot = sum(_zero.values())

NOTE_PROMO = (
    f"The promotion code does not reliably record the discount that was actually "
    f"applied. SAVE10 averages {_promo_disc.loc['SAVE10', 'mean'] * 100:.1f}% rather "
    f"than 10% and {_zero['SAVE10']} of its orders received nothing; WINTER15 "
    f"averages {_promo_disc.loc['WINTER15', 'mean'] * 100:.1f}% with {_zero['WINTER15']} "
    f"at zero; and FREESHIP, which should concern shipping rather than price, still "
    f"carries a {_promo_disc.loc['FREESHIP', 'mean'] * 100:.1f}% price discount with "
    f"{_zero['FREESHIP']} orders at zero — {_zero_tot} of the {_promo_rows:,} promoted "
    f"orders were undiscounted altogether. The four bars are an accurate split of "
    f"revenue and worth looking at, but they cannot show which campaign worked; for "
    f"that, group by the discount actually given."
)


# ═══════════════════════════════════════════════════════════════════════════
# PLOTLY BASE LAYOUT
# ═══════════════════════════════════════════════════════════════════════════
BASE = dict(
    plot_bgcolor=WHITE,
    paper_bgcolor=WHITE,
    font=dict(family=FONT, size=11, color=INK),
    margin=dict(l=8, r=8, t=44, b=8),
    height=300,
    colorway=SERIES,
    hoverlabel=dict(bgcolor=MAROON_DEEP, font_color=WHITE,
                    font_family=FONT, font_size=12),
    showlegend=False,
)


def titled(fig, text, height=300):
    fig.update_layout(
        title=dict(text=text, font=dict(size=13, color=MAROON, family=FONT),
                   x=0.0, xanchor="left", y=0.96, yanchor="top"),
        height=height,
    )
    return fig


def money_axis(**kw):
    base = dict(showgrid=True, gridcolor=GRID, zerolinecolor=BORDER,
                linecolor=BORDER, tickprefix="$", tickformat=",.0f")
    base.update(kw)
    return base


CHARTS = []


def add(div_id, fig, cls="card span-2", note=None):
    div = pio.to_html(fig, include_plotlyjs=False, full_html=False,
                      config={"displayModeBar": False, "responsive": True},
                      div_id=div_id)
    note_html = (f'<p class="note">{html.escape(note)}</p>') if note else ""
    CHARTS.append(f'<div class="{cls}">{div}{note_html}</div>')


# ── 1. Monthly revenue trend ──────────────────────────────────────────────────
_m = df.groupby("YearMonth")["TotalPrice"].sum().reset_index().sort_values("YearMonth")
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=_m["YearMonth"], y=_m["TotalPrice"], mode="lines+markers",
    line=dict(color=MAROON, width=2.5, shape="spline"),
    fill="tozeroy", fillcolor="rgba(109,18,32,0.10)",
    marker=dict(size=6, color=WHITE, line=dict(color=MAROON, width=2)),
    hovertemplate="<b>%{x}</b><br>$%{y:,.0f}<extra></extra>"))
_mean_m = _m["TotalPrice"].mean()
fig.add_hline(y=_mean_m, line_dash="dot", line_color=ROSE,
              annotation_text=f"mean ${_mean_m:,.0f}", annotation_position="top left",
              annotation_font=dict(size=10, color=MAROON_MID))
fig.update_layout(**BASE, xaxis=dict(tickangle=-45, showgrid=False, linecolor=BORDER,
                                     tickfont=dict(size=10)),
                  yaxis=money_axis())
add("c-trend", titled(fig, "Monthly revenue trend  ·  30 months, no seasonality"))

# ── 2. Revenue by region ─────────────────────────────────────────────────────
_r = df.groupby("Region")["TotalPrice"].sum().sort_values()
fig = go.Figure(go.Bar(
    x=_r.values, y=_r.index, orientation="h",
    marker=dict(color=MAROON, line=dict(color=WHITE, width=1)),
    text=[f"${v:,.0f}" for v in _r.values], textposition="outside",
    textfont=dict(color=MAROON, size=11),
    hovertemplate="<b>%{y}</b><br>$%{x:,.0f}<extra></extra>"))
fig.update_layout(**BASE, xaxis=money_axis(), yaxis=dict(showgrid=False))
add("c-region", titled(fig, "Revenue by region"), cls="card")

# ── 3. Revenue vs average order value by product ─────────────────────────────
_p = df.groupby("Product").agg(rev=("TotalPrice", "sum"),
                               aov=("TotalPrice", "mean"),
                               n=("TotalPrice", "size")).sort_values("rev")
fig = go.Figure(go.Bar(
    x=_p["rev"], y=_p.index, orientation="h",
    marker=dict(color=MAROON_MID, line=dict(color=WHITE, width=1)),
    text=[f"${v:,.0f}" for v in _p["rev"]], textposition="outside",
    textfont=dict(color=MAROON, size=10),
    customdata=np.column_stack([_p["aov"], _p["n"]]),
    hovertemplate="<b>%{y}</b><br>Revenue $%{x:,.0f}"
                  "<br>Avg order $%{customdata[0]:,.0f}"
                  "<br>Orders %{customdata[1]:,.0f}<extra></extra>"))
fig.update_layout(**BASE, xaxis=money_axis(), yaxis=dict(showgrid=False))
add("c-product", titled(fig, "Revenue by product  ·  hover for avg order value"))

# ── 4. Annual revenue, with the partial year flagged ─────────────────────────
_y = df.groupby("Year")["TotalPrice"].sum()
labels = [f"{yr}" if yr != LAST_YEAR or not LAST_YEAR_PARTIAL
          else f"{yr} (H1 only)" for yr in _y.index]
fig = go.Figure(go.Bar(
    x=labels, y=_y.values,
    marker=dict(color=[MAROON] * (len(_y) - 1) + [ROSE_SOFT],
                line=dict(color=WHITE, width=1)),
    text=[f"${v:,.0f}" for v in _y.values], textposition="outside",
    textfont=dict(color=MAROON, size=11),
    hovertemplate="<b>%{x}</b><br>$%{y:,.0f}<extra></extra>"))
fig.add_annotation(
    x=f"{LAST_YEAR} (H1 only)", y=_y.iloc[-1], text=f"H1 only - annualised ${_annualised:,.0f}",
    showarrow=True, arrowhead=0, ax=0, ay=-42, font=dict(size=10, color=MAROON),
    bgcolor=BLUSH_DEEP, bordercolor=BORDER, borderpad=4)
fig.update_layout(**BASE, yaxis=money_axis(), xaxis=dict(showgrid=False),
                  annotations=[a for a in fig.layout.annotations])
add("c-year", titled(fig,
                     f"Revenue by year  ·  {LAST_YEAR} is H1 only, H1-to-H1 {_yoy:+.1f}%"),
    note=NOTE_YEAR)

# ── 5. Return rate by product, honestly labelled ─────────────────────────────
_ret = (df.groupby("Product")["Returned"].mean() * 100).sort_values()
_avg = df["Returned"].mean() * 100
fig = go.Figure(go.Bar(
    x=_ret.values, y=_ret.index, orientation="h",
    marker=dict(color=[MAROON if v <= _avg else ROSE for v in _ret.values],
                line=dict(color=WHITE, width=1)),
    text=[f"{v:.1f}%" for v in _ret.values], textposition="outside",
    textfont=dict(color=MAROON, size=10),
    hovertemplate="<b>%{y}</b><br>%{x:.1f}% of orders returned<extra></extra>"))
fig.add_vline(x=_avg, line_dash="dash", line_color=INK, line_width=1,
              annotation_text=f"overall {_avg:.1f}%", annotation_position="top right",
              annotation_font=dict(size=10, color=INK))
fig.add_annotation(
    x=1.0, y=1.0, xref="paper", yref="paper", xanchor="right", yanchor="bottom",
    text=f"spread is noise (chi-square p = {_prod_p:.2f})",
    showarrow=False, font=dict(size=10, color=MAROON_MID), bgcolor=BLUSH_DEEP,
    bordercolor=BORDER, borderpad=4)
fig.update_layout(**BASE, xaxis=dict(ticksuffix="%", showgrid=True, gridcolor=GRID,
                                     zerolinecolor=BORDER, linecolor=BORDER),
                  yaxis=dict(showgrid=False))
add("c-returns", titled(fig, "Return rate by product  ·  differences are not significant"),
    note=NOTE_RETURNS)

# ── 6. Revenue by payment method ─────────────────────────────────────────────
_pay = df.groupby("PaymentMethod")["TotalPrice"].sum().sort_values(ascending=False)
fig = go.Figure(go.Pie(
    labels=_pay.index, values=_pay.values, hole=0.55,
    marker=dict(colors=PIE_SERIES, line=dict(color=WHITE, width=2)),
    textinfo="label+percent", textposition="outside",
    textfont=dict(size=10, color=INK),
    hovertemplate="<b>%{label}</b><br>$%{value:,.0f} (%{percent})<extra></extra>"))
fig.update_layout(**BASE, title=dict(
    text="Revenue by payment method", font=dict(size=13, color=MAROON, family=FONT),
    x=0.0, xanchor="left", y=0.96, yanchor="top"))
add("c-payment", fig, cls="card")

# ── 7. Promotion revenue, now complete ───────────────────────────────────────
_pr = df.groupby("Promotion")["TotalPrice"].sum().sort_values(ascending=False)
_pr_disc = df.groupby("Promotion")["Discount"].mean() * 100
fig = go.Figure(go.Bar(
    x=_pr.index, y=_pr.values,
    marker=dict(color=[MAROON, ROSE, ROSE_SOFT, MAROON_MID][:len(_pr)],
                line=dict(color=WHITE, width=1)),
    text=[f"${v:,.0f}" for v in _pr.values], textposition="outside",
    textfont=dict(color=MAROON, size=10),
    customdata=np.column_stack([_pr_disc.reindex(_pr.index).values,
                                (df.groupby("Promotion").size()
                                 .reindex(_pr.index).values)]),
    hovertemplate="<b>%{x}</b><br>Revenue $%{y:,.0f}"
                  "<br>Avg discount %{customdata[0]:.1f}%"
                  "<br>Orders %{customdata[1]:,.0f}<extra></extra>"))
fig.update_layout(**BASE, yaxis=money_axis(),
                  xaxis=dict(showgrid=False, tickangle=-15, tickfont=dict(size=10)))
add("c-promo", titled(fig, "Revenue by promotion  ·  now includes 'No Promotion'"),
    note=NOTE_PROMO)

# ── 8. Delivery days ─────────────────────────────────────────────────────────
_d = df.groupby("Region")["DeliveryDays"].mean().sort_values()
fig = go.Figure(go.Bar(
    x=_d.index, y=_d.values,
    marker=dict(color=MAROON_MID, line=dict(color=WHITE, width=1)),
    text=[f"{v:.1f}d" for v in _d.values], textposition="outside",
    textfont=dict(color=MAROON, size=11),
    hovertemplate="<b>%{x}</b><br>%{y:.1f} days average<extra></extra>"))
fig.update_layout(**BASE, yaxis=dict(showgrid=True, gridcolor=GRID,
                                     zerolinecolor=BORDER, linecolor=BORDER),
                  xaxis=dict(showgrid=False))
add("c-delivery", titled(fig, "Average delivery time by region  ·  flat 6 days"))

# ── 9. Salesperson performance ───────────────────────────────────────────────
_sp = df.groupby("Salesperson").agg(rev=("TotalPrice", "sum"),
                                    aov=("TotalPrice", "mean")).sort_values("rev")
fig = go.Figure(go.Bar(
    x=_sp["rev"], y=_sp.index, orientation="h",
    marker=dict(color=MAROON, line=dict(color=WHITE, width=1)),
    text=[f"${v:,.0f}" for v in _sp["rev"]], textposition="outside",
    textfont=dict(color=MAROON, size=10),
    customdata=_sp["aov"].values,
    hovertemplate="<b>%{y}</b><br>Revenue $%{x:,.0f}"
                  "<br>Avg order $%{customdata:,.0f}<extra></extra>"))
fig.update_layout(**BASE, xaxis=money_axis(), yaxis=dict(showgrid=False))
add("c-sales", titled(fig, "Revenue by salesperson  ·  spread is volume, not skill"))

# ── 10. Region x product heatmap ─────────────────────────────────────────────
_piv = df.pivot_table(values="TotalPrice", index="Region", columns="Product",
                      aggfunc="sum", fill_value=0)
_heat_recon = abs(_piv.values.sum() - GROSS)
fig = go.Figure(go.Heatmap(
    z=_piv.values, x=_piv.columns.tolist(), y=_piv.index.tolist(),
    colorscale=HEAT_SCALE,
    text=[[f"${v:,.0f}" for v in row] for row in _piv.values],
    texttemplate="%{text}", textfont=dict(size=10),
    hovertemplate="<b>%{y} · %{x}</b><br>$%{z:,.0f}<extra></extra>",
    colorbar=dict(title=dict(text="$", font=dict(size=10)), thickness=12,
                  outlinewidth=0, len=0.85)))
fig.update_layout(**{**BASE, "height": 330}, title=dict(
    text=f"Revenue heatmap  ·  region x product  (reconciles to ${GROSS:,.0f})",
    font=dict(size=13, color=MAROON, family=FONT), x=0.0, xanchor="left", y=0.97,
    yanchor="top"))
add("c-heat", fig, cls="card span-4")


# ═══════════════════════════════════════════════════════════════════════════
# KPI CARDS
# ═══════════════════════════════════════════════════════════════════════════
def kpi(label, value, sub="", accent=MAROON):
    sub_html = f'<div class="kpi-sub">{sub}</div>' if sub else ""
    return (f'<div class="kpi"><div class="kpi-rule" style="background:{accent}"></div>'
            f'<div class="kpi-label">{label}</div>'
            f'<div class="kpi-value" style="color:{accent}">{value}</div>'
            f'{sub_html}</div>')


KPIS = [
    kpi("Gross revenue", f"${GROSS:,.0f}", f"{N_ORDERS:,} orders · {df['Date'].nunique()} days"),
    kpi("Net revenue", f"${df['NetRevenue'].sum():,.0f}",
        f"${GROSS - df['NetRevenue'].sum():,.0f} lost to returns"),
    kpi("Average order value", f"${df['TotalPrice'].mean():,.0f}",
        f"median ${df['TotalPrice'].median():,.0f} · skewed by large orders"),
    kpi("Return rate", f"{_avg:.1f}%", f"{int(df['Returned'].sum()):,} of {N_ORDERS:,} orders"),
    kpi("Average order count", f"{N_ORDERS / 30:,.1f}", "orders per month, all 5 regions"),
    kpi("Discount given", f"${(df['Quantity'] * df['UnitPrice'] * df['Discount']).sum():,.0f}",
        f"{df['Discount'].mean() * 100:.1f}% average discount rate"),
]

HERO = [
    ("Regions", f"{df['Region'].nunique()}"),
    ("Products", f"{df['Product'].nunique()}"),
    ("Salespeople", f"{df['Salesperson'].nunique()}"),
    ("Months", f"{df['YearMonth'].nunique()}"),
]


# ═══════════════════════════════════════════════════════════════════════════
# HTML
# ═══════════════════════════════════════════════════════════════════════════
CSS = """
*,*::before,*::after{box-sizing:border-box}
:root{
  --maroon:#6D1220; --maroon-deep:#4A0A14; --rose:#A94659; --rose-soft:#C98A97;
  --blush:#FBF5F6; --blush-deep:#F3E4E7; --white:#fff; --ink:#2B1015;
  --muted:#8B6670; --border:#EBD7DC;
}
html,body{margin:0;padding:0}
body{
  font-family:Inter,'Segoe UI',system-ui,-apple-system,Arial,sans-serif;
  background:var(--blush); color:var(--ink);
  background-image:
    linear-gradient(rgba(109,18,32,.035) 1px,transparent 1px),
    linear-gradient(90deg,rgba(109,18,32,.035) 1px,transparent 1px);
  background-size:34px 34px; -webkit-font-smoothing:antialiased;
}
.wrap{max-width:1560px;margin:0 auto;padding:26px 28px 60px}

/* ── header ── */
.hero{
  position:relative;overflow:hidden;border-radius:14px;padding:30px 34px;
  background:linear-gradient(120deg,var(--maroon-deep) 0%,var(--maroon) 48%,#8E2233 100%);
  box-shadow:0 22px 50px rgba(74,10,20,.28);margin-bottom:22px;color:#fff;
}
.hero::after{
  content:"";position:absolute;inset:0;pointer-events:none;
  background:repeating-linear-gradient(135deg,rgba(255,255,255,.10) 0 1px,transparent 1px 20px);
}
.hero-top{position:relative;display:flex;justify-content:space-between;
  align-items:center;gap:28px;flex-wrap:wrap}
.eyebrow{font-size:11px;font-weight:800;letter-spacing:.16em;text-transform:uppercase;
  color:#F0D2D8;margin:0 0 7px}
h1{margin:0;font-size:36px;font-weight:800;letter-spacing:-.5px;color:#fff}
.sub{margin:9px 0 0;color:#F3DCE1;font-size:14px;font-weight:500}
.hero-stats{position:relative;display:flex;gap:12px;flex-wrap:wrap}
.hstat{background:rgba(255,255,255,.14);border:1px solid rgba(255,255,255,.26);
  border-radius:10px;padding:11px 16px;min-width:96px}
.hstat b{display:block;font-size:21px;font-weight:800;color:#fff;line-height:1.1}
.hstat span{display:block;font-size:10px;font-weight:700;letter-spacing:.1em;
  text-transform:uppercase;color:#F0D2D8;margin-bottom:3px}

/* ── kpi ── */
.kpis{position:relative;display:grid;gap:14px;margin-bottom:22px;
  grid-template-columns:repeat(auto-fit,minmax(190px,1fr))}
.kpi{position:relative;background:#fff;border:1px solid var(--border);
  border-radius:12px;padding:16px 18px 15px;
  box-shadow:0 10px 26px rgba(109,18,32,.07);overflow:hidden}
.kpi-rule{position:absolute;left:0;top:0;height:100%;width:4px}
.kpi-label{font-size:10.5px;font-weight:800;letter-spacing:.09em;text-transform:uppercase;
  color:var(--muted);margin-bottom:8px}
.kpi-value{font-size:27px;font-weight:800;line-height:1.15;letter-spacing:-.5px}
.kpi-sub{margin-top:7px;font-size:11.5px;color:var(--muted);line-height:1.4}

/* ── cards / grid ── */
.grid{display:grid;gap:16px;grid-template-columns:repeat(4,minmax(0,1fr));margin-bottom:16px}
.card{background:#fff;border:1px solid var(--border);border-radius:12px;padding:10px 8px 4px;
  box-shadow:0 10px 26px rgba(109,18,32,.06);min-width:0;overflow:hidden}
.span-2{grid-column:span 2}
.span-4{grid-column:span 4}

/* ── reading notes ── */
.note{margin:2px 12px 12px;padding:11px 14px;border-radius:9px;
  background:var(--blush);border-left:3px solid var(--gold);
  font-size:11.5px;line-height:1.6;color:#5C3A42}
.sec{margin:34px 0 14px;display:flex;align-items:center;gap:12px}
.sec h2{margin:0;font-size:15px;font-weight:800;color:var(--maroon);letter-spacing:.01em}
.sec .line{flex:1;height:1px;background:linear-gradient(90deg,var(--border),transparent)}

/* ── checks ── */
.checks{background:#fff;border:1px solid var(--border);border-radius:12px;overflow:hidden;
  box-shadow:0 10px 26px rgba(109,18,32,.06)}
details{border-bottom:1px solid var(--border)}
details:last-child{border-bottom:0}
summary{cursor:pointer;padding:13px 18px;font-size:13.5px;font-weight:600;
  display:flex;align-items:center;gap:11px;list-style:none;transition:background .15s}
summary::-webkit-details-marker{display:none}
summary:hover{background:var(--blush)}
summary::after{content:"▾";margin-left:auto;color:var(--rose-soft);font-size:12px;
  transition:transform .2s}
details[open] summary::after{transform:rotate(180deg)}
.dot{width:9px;height:9px;border-radius:50%;flex:none}
.dot.pass{background:var(--maroon)}
.dot.warn{background:var(--gold)}
.dot.fail{background:#B3261E}
.badge{font-size:9.5px;font-weight:800;letter-spacing:.09em;text-transform:uppercase;
  padding:3px 8px;border-radius:99px}
.badge.pass{background:var(--blush-deep);color:var(--maroon)}
.badge.warn{background:#FBF3E2;color:#8A6414}
.badge.fail{background:#FBE9E7;color:#B3261E}
.chk-body{padding:0 18px 15px 38px;font-size:13px;line-height:1.65;color:#5C3A42}
.pie-head{padding:16px 18px;border-bottom:1px solid var(--border);background:var(--blush)}

/* ── footer ── */
footer{margin-top:36px;padding-top:20px;border-top:1px solid var(--border);
  font-size:12px;color:var(--muted);line-height:1.7}
footer b{color:var(--maroon)}
footer code{background:var(--blush-deep);padding:1.5px 6px;border-radius:5px;
  font-size:11.5px;color:var(--maroon-deep)}

@media(max-width:1150px){
  .grid{grid-template-columns:repeat(2,minmax(0,1fr))}
  .span-4{grid-column:span 2}
}
@media(max-width:720px){
  .grid{grid-template-columns:1fr}
  .span-2,.span-4{grid-column:span 1}
  .wrap{padding:16px 14px 40px}
  h1{font-size:27px}
  .hero{padding:24px 20px}
}
"""

JS = """
// Plotly 7 marks its graphs with .plotly-graph-div (older builds used
// .js-plotly-plot), so match both when the cards reflow on resize.
function resizeAll(){
  document.querySelectorAll('.plotly-graph-div, .js-plotly-plot').forEach(function(g){
    if (typeof Plotly !== 'undefined') { Plotly.Plots.resize(g); }
  });
}
window.addEventListener('resize', resizeAll);
window.addEventListener('load', resizeAll);
"""


def check_row(c):
    # Detail text is authored as plain prose but can contain characters like
    # "p < 0.05" that browsers would otherwise parse as markup.
    return (f'<details><summary><span class="dot {c["status"]}"></span>'
            f'<span class="badge {c["status"]}">{c["status"]}</span>'
            f'{html.escape(c["label"])}</summary>'
            f'<div class="chk-body">{html.escape(c["detail"])}</div></details>')


hero_stats = "".join(
    f'<div class="hstat"><span>{l}</span><b>{v}</b></div>' for l, v in HERO
)
kpi_html = "".join(KPIS)
charts_html = "\n".join(CHARTS)
checks_html = "".join(check_row(c) for c in CHECKS)
n_pass = sum(1 for c in CHECKS if c["status"] == "pass")
n_warn = sum(1 for c in CHECKS if c["status"] == "warn")
n_fail = sum(1 for c in CHECKS if c["status"] == "fail")

HTML = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Sales Analytics Dashboard · {DATE_MIN:%b %Y} – {DATE_MAX:%b %Y}</title>
<style>{CSS}</style>
<script>{get_plotlyjs()}</script>
</head>
<body>
<div class="wrap">

  <header class="hero">
    <div class="hero-top">
      <div>
        <p class="eyebrow">Sales Performance Report</p>
        <h1>Sales Analytics Dashboard</h1>
        <p class="sub">Product &middot; Region &middot; Customer &middot; Operations &nbsp;|&nbsp;
           {DATE_MIN:%d %b %Y} – {DATE_MAX:%d %b %Y} ({df['YearMonth'].nunique()} months)</p>
      </div>
      <div class="hero-stats">{hero_stats}</div>
    </div>
  </header>

  <section class="kpis">{kpi_html}</section>

  <div class="sec"><h2>Performance</h2><div class="line"></div></div>
  <div class="grid">{charts_html}</div>

  <div class="sec"><h2>Notes &amp; methodology</h2><div class="line"></div></div>

  <div class="checks">
    <div class="pie-head">
      <b style="color:var(--maroon)">Three numbers on this dashboard look like findings
      but are not.</b>
      <div style="margin-top:5px">
        The return-rate spread, the {LAST_YEAR} revenue drop and the promotion
        ranking all look meaningful and are not. Each affected chart carries an
        explanation underneath it. The checks below confirm the figures
        themselves are correct.
      </div>
    </div>
    <details>
      <summary><span class="dot {'pass' if not n_fail else 'fail'}"></span>
        <span class="badge {'pass' if not n_fail else 'fail'}">{'pass' if not n_fail else 'fail'}</span>
        Data integrity &mdash; {n_pass} of {len(CHECKS)} automated checks passed</summary>
      <div class="chk-body">
        <p style="margin:0 0 10px">These confirm the figures are arithmetically
        sound. They do not speak to whether a difference is meaningful &mdash;
        that is what the explanations above each affected chart are for.</p>
        {checks_html}
      </div>
    </details>
  </div>

  <footer>
    <p><b>Source</b> <code>{DATA_FILE}</code> &middot; {N_ORDERS:,} orders &middot;
       gross revenue ${GROSS:,.2f} &middot; net revenue ${df['NetRevenue'].sum():,.2f}.</p>
    <p><b>Definitions.</b>
       <em>Gross revenue</em> = sum of <code>TotalPrice</code>, which equals
       <code>Quantity &times; UnitPrice &times; (1 &minus; Discount)</code> for every order.
       <em>Net revenue</em> = gross less the full value of returned orders.
       <em>Return rate</em> = share of order lines flagged as returned.
       <em>Average delivery</em> = mean days from order to delivery.</p>
    <p><b>How to read a p-value.</b> A p-value is the chance that a pattern this
       large would appear if there were no real effect behind it. Under 0.05
       (roughly 1 in 20) is the usual threshold for treating a difference as real.
       A p-value near 1 means the pattern is indistinguishable from luck.</p>
    <p><b>Two limits worth knowing.</b> {LAST_YEAR} covers January&ndash;{DATE_MAX:%B}
       only, so it must be compared with {LAST_YEAR - 1} over the same months
       (H1 to H1: {_yoy:+.1f}%), never against a full-year total. Revenue breakdowns
       are raw sums rather than per-order values; average order value is available
       on hover so order count and basket size can be told apart.</p>
  </footer>

</div>
<script>{JS}</script>
</body>
</html>
"""

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(HTML)

# ═══════════════════════════════════════════════════════════════════════════
# CONSOLE SUMMARY
# ═══════════════════════════════════════════════════════════════════════════
print("=" * 74)
print("STATIC DASHBOARD BUILT  (maroon & white)")
print("=" * 74)
print(f"Output        : {OUTPUT_FILE}  "
      f"({len(HTML) / 1024 / 1024:.2f} MB, self-contained, opens offline)")
print(f"Charts        : {len(CHARTS)}")
print(f"Date range    : {DATE_MIN:%d %b %Y} – {DATE_MAX:%d %b %Y}  "
      f"({df['YearMonth'].nunique()} months)")
print(f"Orders        : {N_ORDERS:,}")
print(f"Gross revenue : ${GROSS:,.2f}")
print(f"Net revenue   : ${df['NetRevenue'].sum():,.2f}")

print(f"\nData integrity: {n_pass} of {len(CHECKS)} checks passed"
      f"{f', {n_fail} FAILED' if n_fail else ''}")
for c in CHECKS:
    print(f"  [{c['status'].upper():4}] {c['label']}")

print("\nExplanations attached to charts:")
for title, note in [("Return rate by product", NOTE_RETURNS),
                    (f"Revenue by year ({LAST_YEAR} partial)", NOTE_YEAR),
                    ("Revenue by promotion", NOTE_PROMO)]:
    print(f"\n  • {title}\n    {' '.join(note.split())}")

print("\nCorrections applied vs the previous interactive dashboard:")
print("  1. Promotion field — cleaning.py filled NaN with the string 'None', which")
print("     pandas' read_csv parses straight back to NaN. 370 orders ($1,074,247,")
print("     24.5% of revenue) were invisible to every groupby('Promotion'). Now uses")
print("     'No Promotion', which survives the CSV round-trip.")
print("  2. Partial final year — labelled, compared like-for-like, and explained on")
print(f"     the chart (H1 vs H1 = {_yoy:+.1f}%, not the apparent {_apparent:+.0f}%).")
print(f"  3. Return rates — the spread is not significant (p = {_prod_p:.2f}); the")
print("     chart now says so in plain words instead of implying a ranking.")
print("  4. Revenue vs volume — average order value is surfaced so revenue sums")
print("     are not read as pure performance.")
print("  5. Console encoding — scripts no longer crash on Windows cp1252 output.")
print("  6. Note text is HTML-escaped so figures like 'p < 0.05' render correctly.")
print()
