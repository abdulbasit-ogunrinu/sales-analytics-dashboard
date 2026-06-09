import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash
from dash import dcc, html, Input, Output
import warnings; warnings.filterwarnings("ignore")

# Load data
df = pd.read_csv("cleaned_sales_data.csv", parse_dates=["Date","OrderDate","DeliveryDate"])
df["YearMonth"] = df["Date"].dt.to_period("M").astype(str)

# Blue + white dashboard theme
BLUE = "#0B5FFF"
NAVY = "#083B86"
SKY = "#38BDF8"
CYAN = "#06B6D4"
TEAL = "#14B8A6"
GOLD = "#F59E0B"
RED = "#EF4444"
INK = "#0F172A"
MUTED = "#64748B"
BORDER = "#D8E7FF"
PANEL = "#FFFFFF"
BG = "#F4F9FF"
PALETTE = [BLUE, SKY, CYAN, TEAL, NAVY, GOLD]

CARD_STYLE = {
    "background":"rgba(255,255,255,0.96)",
    "border":"1px solid #D8E7FF",
    "borderRadius":"8px",
    "padding":"10px",
    "boxShadow":"0 14px 35px rgba(37,99,235,0.10)",
}

BASE_LAYOUT = dict(
    plot_bgcolor="white",
    paper_bgcolor="white",
    font=dict(family="Inter, Arial, sans-serif", size=11, color=INK),
    margin=dict(l=12, r=12, t=48, b=12),
    height=275,
    colorway=PALETTE,
)

GRID_STYLE = {
    "display":"grid",
    "gap":"16px",
    "marginBottom":"16px",
}

FILTER_BOX = {
    "background":"rgba(255,255,255,0.86)",
    "border":"1px solid rgba(216,231,255,0.95)",
    "borderRadius":"8px",
    "padding":"10px 12px",
    "boxShadow":"0 10px 24px rgba(15,23,42,0.06)",
}

DROPDOWN_STYLE = {"width":"170px", "fontSize":"13px"}


def filter_df(region, product, customer, year):
    d = df.copy()
    if region   != "ALL": d = d[d["Region"]      == region]
    if product  != "ALL": d = d[d["Product"]      == product]
    if customer != "ALL": d = d[d["CustomerType"] == customer]
    if year     != 0:     d = d[d["Year"]         == year]
    return d


def kpi_card(label, value, color=BLUE):
    return html.Div(style={
        "position":"relative",
        "overflow":"hidden",
        "background":"linear-gradient(145deg, #FFFFFF 0%, #F8FBFF 62%, #EAF4FF 100%)",
        "border":"1px solid #D8E7FF",
        "borderRadius":"8px",
        "padding":"16px 16px 14px",
        "boxShadow":"0 14px 30px rgba(37,99,235,0.10)",
    }, children=[
        html.Div(style={
            "position":"absolute", "right":"-24px", "top":"-24px",
            "width":"82px", "height":"82px", "borderRadius":"50%",
            "border":f"18px solid {color}", "opacity":"0.10",
        }),
        html.Div(style={
            "width":"34px", "height":"4px", "borderRadius":"99px",
            "background":color, "marginBottom":"10px",
        }),
        html.P(label, style={"margin":"0 0 6px", "fontSize":"11px",
                              "color":MUTED, "fontWeight":"700", "textTransform":"uppercase"}),
        html.P(value, style={"margin":"0", "fontSize":"22px",
                              "fontWeight":"800", "color":INK, "letterSpacing":"0"}),
    ])


def chart_card(graph_id):
    return html.Div(style=CARD_STYLE, children=[dcc.Graph(id=graph_id, config={"displayModeBar":False})])


def hero_metric(label, value, color):
    return html.Div(style={
        "background":"rgba(255,255,255,0.16)",
        "border":"1px solid rgba(255,255,255,0.28)",
        "borderRadius":"8px",
        "padding":"12px 14px",
        "minWidth":"132px",
    }, children=[
        html.P(label, style={"margin":"0 0 4px", "fontSize":"11px", "fontWeight":"700", "color":"#DCEBFF", "textTransform":"uppercase"}),
        html.P(value, style={"margin":"0", "fontSize":"18px", "fontWeight":"800", "color":"white"}),
        html.Div(style={"height":"3px", "width":"42px", "background":color, "borderRadius":"99px", "marginTop":"10px"}),
    ])


# App
app = dash.Dash(__name__, title="Sales Analytics Dashboard")

app.layout = html.Div(style={
    "fontFamily":"Inter, Arial, sans-serif",
    "backgroundColor":BG,
    "backgroundImage":"linear-gradient(rgba(11,95,255,0.05) 1px, transparent 1px), linear-gradient(90deg, rgba(11,95,255,0.05) 1px, transparent 1px)",
    "backgroundSize":"34px 34px",
    "minHeight":"100vh",
    "padding":"24px 32px",
}, children=[

    html.Div(style={
        "position":"relative",
        "overflow":"hidden",
        "borderRadius":"8px",
        "padding":"28px 30px",
        "marginBottom":"22px",
        "color":"white",
        "background":"linear-gradient(135deg, #083B86 0%, #0B5FFF 55%, #38BDF8 100%)",
        "boxShadow":"0 24px 55px rgba(11,95,255,0.24)",
    }, children=[
        html.Div(style={
            "position":"absolute", "inset":"0",
            "backgroundImage":"repeating-linear-gradient(135deg, rgba(255,255,255,0.12) 0px, rgba(255,255,255,0.12) 1px, transparent 1px, transparent 18px)",
        }),
        html.Div(style={"position":"relative", "display":"flex", "justifyContent":"space-between", "gap":"24px", "alignItems":"center", "flexWrap":"wrap"}, children=[
            html.Div(children=[
                html.P("Sales Performance Command Center", style={"margin":"0 0 6px", "fontSize":"12px", "fontWeight":"800", "letterSpacing":"0.08em", "textTransform":"uppercase", "color":"#DCEBFF"}),
                html.H1("Sales Analytics Dashboard", style={"margin":"0", "fontSize":"34px", "fontWeight":"850", "color":"white", "letterSpacing":"0"}),
                html.P("Product | Region | Customer | Operational Signals | 2023-2025",
                       style={"margin":"8px 0 0", "color":"#EAF4FF", "fontSize":"14px", "fontWeight":"500"}),
            ]),
            html.Div(style={"display":"flex", "gap":"12px", "flexWrap":"wrap"}, children=[
                hero_metric("Revenue", f"${df['TotalPrice'].sum():,.0f}", SKY),
                hero_metric("Orders", f"{len(df):,}", TEAL),
                hero_metric("Regions", f"{df['Region'].nunique():,}", GOLD),
            ]),
        ]),
    ]),

    html.Div(style={"display":"flex", "gap":"14px", "marginBottom":"20px", "flexWrap":"wrap"}, children=[
        html.Div(style=FILTER_BOX, children=[
            html.Label("Region", style={"fontSize":"12px", "color":NAVY, "display":"block", "marginBottom":"6px", "fontWeight":"700"}),
            dcc.Dropdown(id="f-region",
                options=[{"label":"All Regions", "value":"ALL"}]+
                        [{"label":r, "value":r} for r in sorted(df["Region"].unique())],
                value="ALL", clearable=False, style=DROPDOWN_STYLE),
        ]),
        html.Div(style=FILTER_BOX, children=[
            html.Label("Product", style={"fontSize":"12px", "color":NAVY, "display":"block", "marginBottom":"6px", "fontWeight":"700"}),
            dcc.Dropdown(id="f-product",
                options=[{"label":"All Products", "value":"ALL"}]+
                        [{"label":p, "value":p} for p in sorted(df["Product"].unique())],
                value="ALL", clearable=False, style=DROPDOWN_STYLE),
        ]),
        html.Div(style=FILTER_BOX, children=[
            html.Label("Customer Type", style={"fontSize":"12px", "color":NAVY, "display":"block", "marginBottom":"6px", "fontWeight":"700"}),
            dcc.Dropdown(id="f-customer",
                options=[{"label":"All", "value":"ALL"}]+
                        [{"label":c, "value":c} for c in sorted(df["CustomerType"].unique())],
                value="ALL", clearable=False, style=DROPDOWN_STYLE),
        ]),
        html.Div(style=FILTER_BOX, children=[
            html.Label("Year", style={"fontSize":"12px", "color":NAVY, "display":"block", "marginBottom":"6px", "fontWeight":"700"}),
            dcc.Dropdown(id="f-year",
                options=[{"label":"All Years", "value":0}]+
                        [{"label":str(y), "value":y} for y in sorted(df["Year"].unique())],
                value=0, clearable=False, style={"width":"140px", "fontSize":"13px"}),
        ]),
    ]),

    html.Div(id="kpi-row", style={
        "display":"grid", "gridTemplateColumns":"repeat(auto-fit, minmax(155px, 1fr))",
        "gap":"14px", "marginBottom":"18px",
    }),

    html.Div(style={**GRID_STYLE, "gridTemplateColumns":"minmax(0, 2fr) minmax(280px, 1fr)"}, children=[
        chart_card("ch-monthly"),
        chart_card("ch-region"),
    ]),

    html.Div(style={**GRID_STYLE, "gridTemplateColumns":"repeat(auto-fit, minmax(280px, 1fr))"}, children=[
        chart_card("ch-product"),
        chart_card("ch-salesperson"),
        chart_card("ch-returns"),
    ]),

    html.Div(style={**GRID_STYLE, "gridTemplateColumns":"repeat(auto-fit, minmax(280px, 1fr))"}, children=[
        chart_card("ch-payment"),
        chart_card("ch-promo"),
        chart_card("ch-delivery"),
    ]),

    html.Div(style={**CARD_STYLE, "marginBottom":"16px"}, children=[dcc.Graph(id="ch-heatmap", config={"displayModeBar":False})]),
])


@app.callback(
    Output("kpi-row", "children"),
    Output("ch-monthly", "figure"),
    Output("ch-region", "figure"),
    Output("ch-product", "figure"),
    Output("ch-salesperson", "figure"),
    Output("ch-returns", "figure"),
    Output("ch-payment", "figure"),
    Output("ch-promo", "figure"),
    Output("ch-delivery", "figure"),
    Output("ch-heatmap", "figure"),
    Input("f-region", "value"),
    Input("f-product", "value"),
    Input("f-customer", "value"),
    Input("f-year", "value"),
)
def update(region, product, customer, year):
    d = filter_df(region, product, customer, year)
    if len(d) == 0:
        empty = go.Figure()
        empty.update_layout(**BASE_LAYOUT)
        return [], *[empty]*9

    kpis = [
        kpi_card("Total Orders",    f"{len(d):,}",                         BLUE),
        kpi_card("Gross Revenue",   f"${d['TotalPrice'].sum():,.0f}",       SKY),
        kpi_card("Net Revenue",     f"${d['NetRevenue'].sum():,.0f}",       CYAN),
        kpi_card("Avg Order Value", f"${d['TotalPrice'].mean():,.0f}",      TEAL),
        kpi_card("Return Rate",     f"{d['Returned'].mean()*100:.1f}%",     RED),
        kpi_card("Avg Delivery",    f"{d['DeliveryDays'].mean():.1f} days", GOLD),
    ]

    m = d.groupby("YearMonth")["TotalPrice"].sum().reset_index().sort_values("YearMonth")
    f_m = go.Figure()
    f_m.add_trace(go.Scatter(x=m["YearMonth"], y=m["TotalPrice"],
        mode="lines+markers", fill="tozeroy",
        line=dict(color=BLUE, width=3, shape="spline"), fillcolor="rgba(11,95,255,0.12)",
        marker=dict(size=7, color="white", line=dict(color=BLUE, width=2)),
        hovertemplate="<b>%{x}</b><br>$%{y:,.0f}<extra></extra>"))
    f_m.update_layout(**BASE_LAYOUT,
        title=dict(text="Monthly Revenue Trend", font=dict(size=13, color=INK)),
        xaxis=dict(tickangle=45, showgrid=False, linecolor=BORDER),
        yaxis=dict(tickprefix="$", showgrid=True, gridcolor="#EAF4FF", zerolinecolor=BORDER))

    reg = d.groupby("Region")["TotalPrice"].sum().sort_values()
    f_r = go.Figure(go.Bar(x=reg.values, y=reg.index, orientation="h",
        marker_color=PALETTE[:len(reg)], marker_line=dict(color="white", width=1),
        text=[f"${v:,.0f}" for v in reg.values], textposition="outside",
        hovertemplate="<b>%{y}</b><br>$%{x:,.0f}<extra></extra>"))
    f_r.update_layout(**BASE_LAYOUT,
        title=dict(text="Revenue by Region", font=dict(size=13, color=INK)),
        xaxis=dict(tickprefix="$", showgrid=True, gridcolor="#EAF4FF", zerolinecolor=BORDER),
        yaxis=dict(showgrid=False))

    prod = d.groupby("Product")["TotalPrice"].sum().sort_values()
    f_p = go.Figure(go.Bar(x=prod.values, y=prod.index, orientation="h",
        marker_color=PALETTE[:len(prod)], marker_line=dict(color="white", width=1),
        text=[f"${v:,.0f}" for v in prod.values], textposition="outside",
        hovertemplate="<b>%{y}</b><br>$%{x:,.0f}<extra></extra>"))
    f_p.update_layout(**BASE_LAYOUT,
        title=dict(text="Revenue by Product", font=dict(size=13, color=INK)),
        xaxis=dict(tickprefix="$", showgrid=True, gridcolor="#EAF4FF", zerolinecolor=BORDER),
        yaxis=dict(showgrid=False))

    sp = d.groupby("Salesperson")["TotalPrice"].sum().sort_values(ascending=False)
    f_sp = go.Figure(go.Bar(x=sp.index, y=sp.values,
        marker_color=PALETTE[:len(sp)], marker_line=dict(color="white", width=1),
        hovertemplate="<b>%{x}</b><br>$%{y:,.0f}<extra></extra>"))
    f_sp.update_layout(**BASE_LAYOUT,
        title=dict(text="Revenue by Salesperson", font=dict(size=13, color=INK)),
        yaxis=dict(tickprefix="$", showgrid=True, gridcolor="#EAF4FF", zerolinecolor=BORDER),
        xaxis=dict(showgrid=False))

    ret = (d.groupby("Product")["Returned"].mean()*100).sort_values()
    avg_r = d["Returned"].mean()*100
    f_ret = go.Figure()
    f_ret.add_trace(go.Bar(x=ret.values, y=ret.index, orientation="h",
        marker_color=[RED if v > avg_r else TEAL for v in ret.values],
        marker_line=dict(color="white", width=1),
        text=[f"{v:.1f}%" for v in ret.values], textposition="outside",
        hovertemplate="<b>%{y}</b><br>%{x:.1f}%<extra></extra>"))
    f_ret.add_vline(x=avg_r, line_dash="dash", line_color=NAVY,
                    annotation_text=f"Avg {avg_r:.1f}%", annotation_position="top right")
    f_ret.update_layout(**BASE_LAYOUT,
        title=dict(text="Return Rate by Product", font=dict(size=13, color=INK)),
        xaxis=dict(ticksuffix="%", showgrid=True, gridcolor="#EAF4FF", zerolinecolor=BORDER),
        yaxis=dict(showgrid=False))

    pay = d.groupby("PaymentMethod")["TotalPrice"].sum()
    f_pay = go.Figure(go.Pie(labels=pay.index, values=pay.values, hole=0.52,
        marker=dict(colors=PALETTE[:len(pay)], line=dict(color="white", width=2)),
        textinfo="label+percent",
        hovertemplate="<b>%{label}</b><br>$%{value:,.0f} (%{percent})<extra></extra>"))
    f_pay.update_layout(**BASE_LAYOUT,
        title=dict(text="Revenue by Payment Method", font=dict(size=13, color=INK)),
        showlegend=False)

    promo = d.groupby("Promotion")["TotalPrice"].sum().sort_values(ascending=False)
    f_promo = go.Figure(go.Bar(x=promo.index, y=promo.values,
        marker_color=PALETTE[:len(promo)], marker_line=dict(color="white", width=1),
        hovertemplate="<b>%{x}</b><br>$%{y:,.0f}<extra></extra>"))
    f_promo.update_layout(**BASE_LAYOUT,
        title=dict(text="Revenue by Promotion", font=dict(size=13, color=INK)),
        yaxis=dict(tickprefix="$", showgrid=True, gridcolor="#EAF4FF", zerolinecolor=BORDER),
        xaxis=dict(showgrid=False))

    deliv = d.groupby("Region")["DeliveryDays"].mean().sort_values()
    f_del = go.Figure(go.Bar(x=deliv.index, y=deliv.values,
        marker_color=PALETTE[:len(deliv)], marker_line=dict(color="white", width=1),
        text=[f"{v:.1f}d" for v in deliv.values], textposition="outside",
        hovertemplate="<b>%{x}</b><br>%{y:.1f} days<extra></extra>"))
    f_del.update_layout(**BASE_LAYOUT,
        title=dict(text="Avg Delivery Days by Region", font=dict(size=13, color=INK)),
        yaxis=dict(showgrid=True, gridcolor="#EAF4FF", zerolinecolor=BORDER),
        xaxis=dict(showgrid=False))

    pivot = d.pivot_table(values="TotalPrice", index="Region",
                          columns="Product", aggfunc="sum", fill_value=0)
    f_heat = go.Figure(go.Heatmap(
        z=pivot.values, x=pivot.columns.tolist(), y=pivot.index.tolist(),
        colorscale=[[0, "#EFF6FF"], [0.28, "#BFDBFE"], [0.55, "#60A5FA"], [0.78, "#2563EB"], [1, "#083B86"]],
        text=[[f"${v:,.0f}" for v in row] for row in pivot.values],
        texttemplate="%{text}", textfont={"size":11, "color":INK},
        hovertemplate="<b>%{y} x %{x}</b><br>$%{z:,.0f}<extra></extra>"))
    f_heat.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        font=dict(family="Inter, Arial, sans-serif", size=11, color=INK),
        margin=dict(l=12, r=12, t=48, b=12), height=330,
        title=dict(text="Revenue Heatmap: Region x Product", font=dict(size=13, color=INK)))

    return kpis, f_m, f_r, f_p, f_sp, f_ret, f_pay, f_promo, f_del, f_heat


if __name__ == "__main__":
    print("Dashboard running at: http://127.0.0.1:8050")
    app.run(debug=False, port=8050)
