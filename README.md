# Sales Analytics Dashboard

An explanation of `sales_dashboard.html` — a single-file report of 1,500 sales orders covering
**1 January 2023 to 30 June 2025**.

The dashboard exists to answer a narrow question honestly: *what do these numbers actually
show?* Every figure on it reconciles exactly to the source data, and every figure that could
be mistaken for a finding carries an explanation of why it isn't one.

---

## What the file is

`sales_dashboard.html` is one self-contained file, about 4.2 MB. The charting library is
embedded inside it, so there is no server, no internet connection, and no companion asset to
lose. Double-click the file and it opens in any browser.

To rebuild it after changing the data:

```bash
python cleaning.py        # Product-Sales-Region.xlsx -> cleaned_sales_data.csv
python dashboard.py       # cleaned_sales_data.csv   -> sales_dashboard.html
```

`cleaning.py` must run first, because `dashboard.py` reads the CSV it produces. The original
spreadsheet is never modified.

---

## How the page is laid out

Reading top to bottom, the page has four parts:

1. **Header** — the reporting period and four scale figures.
2. **Six KPI cards** — the headline numbers, each with a qualifier underneath.
3. **Performance** — ten charts covering volume, geography, product, time, returns, payment,
   promotions, operations and people.
4. **Notes & methodology** — three explanations of misleading numbers, seven data-integrity
   checks, and a footer defining every term used.

The layout reflows to two columns below 1150 px and to a single column below 720 px, with no
horizontal scrolling at any width.

---

## Header

The header states the reporting period and the four dimensions the whole dashboard is sliced
by:

| Dimension | Count |
|---|---|
| Regions | 5 |
| Products | 7 |
| Salespeople | 6 |
| Months | 30 |

Thirty is the exact number of months between the first and last order, with **no gaps** — the
monthly series is continuous, so the trend chart has nothing interpolated or missing.

---

## The six KPI cards

These are the numbers a reader should leave with. Each one carries a second line that qualifies
it, because on its own each figure is open to a wrong reading.

**Gross revenue — $4,379,992**
Sub: 1,500 orders · 747 days
The sum of `TotalPrice` across all orders. This is revenue *before* returns are deducted.

**Net revenue — $3,269,903**
Sub: $1,110,090 lost to returns
Gross less the full value of every returned order. The gap between the two cards — **$1.11M,
or 25.3% of gross** — is the single largest number on the dashboard and is easy to overlook
because it is only ever presented as a difference.

**Average order value — $2,920**
Sub: median $2,175 · skewed by large orders
The mean order is **$745 larger than the median**, which means the distribution has a long
right tail: a small number of large orders pull the average up. Anywhere this dashboard shows
revenue, the average order value is available on hover so that order count and basket size
can be told apart.

**Return rate — 24.8%**
Sub: 372 of 1,500 orders
Roughly one order in four comes back. The per-product breakdown of this number is the subject
of one of the three explanations below, and is *not* a ranking.

**Average order count — 50.0**
Sub: orders per month, all 5 regions
Volume, deliberately shown next to the revenue cards so revenue differences are not
automatically read as performance differences.

**Discount given — $347,901**
Sub: 7.3% average discount rate
The total value of discounts handed out, computed as `Quantity × UnitPrice × Discount`.
Note that 7.3% is the average across *all* orders including undiscounted ones.

---

## Performance — the ten charts

### 1. Monthly revenue trend

Thirty consecutive months, plotted as a line with a dotted mean line at **$146,000**.

The series runs between **$78,446** and **$208,549**, with a standard deviation of **$23,791**
— about 16% of the mean. The shape is a flat band with noise, not a trend and not a cycle.
The chart title says "no seasonality" because a regression against month index returns an
R² of 0.001, meaning the passage of time explains essentially none of the variation.

**What it tells you:** trading volume has been stable for two and a half years. There is no
growth story and no decline story here.

### 2. Revenue by region

Horizontal bars, smallest to largest, with values labelled on the bars.

| Region | Revenue | Share | Orders |
|---|---|---|---|
| North | $967,958 | 22.1% | 309 |
| East | $883,634 | 20.2% | 311 |
| West | $853,479 | 19.5% | 284 |
| Central | $847,154 | 19.3% | 301 |
| South | $827,768 | 18.9% | 295 |

The top-to-bottom gap is **$140,190, or 3.2 percentage points** — a spread of 17% between
best and worst. Order counts are near-identical (284–311), so revenue tracks order volume
almost exactly. This is the closest thing the dataset has to a real ranking, and even here the
gap is modest.

### 3. Revenue by product

Bars show revenue; hovering reveals average order value and order count for each product.

| Product | Revenue | Share | Avg order | Orders |
|---|---|---|---|---|
| Tablet | $684,539 | 15.6% | $2,852 | 240 |
| Laptop | $684,417 | 15.6% | $3,028 | 226 |
| Printer | $684,387 | 15.6% | $3,244 | 211 |
| Monitor | $651,629 | 14.9% | $3,074 | 212 |
| Chair | $622,589 | 14.2% | $2,979 | 209 |
| Desk | $555,267 | 12.7% | $2,682 | 207 |
| Phone | $497,163 | 11.4% | $2,550 | 195 |

**The top three are separated by $152 — a rounding error.** Tablet, Laptop and Printer are the
same product commercially speaking. At the other end, Desk and Phone earn less, but they also
sold 12 and 22 fewer orders. Average order value rises as revenue falls, so the lower-revenue
products are not worse products, just cheaper ones sold slightly less often.

### 4. Revenue by year

| Year | Revenue | Note |
|---|---|---|
| 2023 | $1,697,870 | full year |
| 2024 | $1,771,955 | full year |
| 2025 | $910,168 | **January–June only** |

The 2025 bar is coloured differently and annotated "H1 only". On the raw totals it looks like
a **49% collapse**.

It is not. Comparing the same six months:

- **Jan–Jun 2025: $910,168**
- **Jan–Jun 2024: $911,988**
- **Change: −0.2% — flat**

Annualised, 2025 is running at **$1,820,335** against 2024's **$1,771,955**, which is **+2.7%**.
The company is slightly ahead of last year, not collapsing. The chart title carries the H1-to-H1
figure for this reason, and an explanation sits directly beneath the chart.

### 5. Return rate by product

Bars are coloured against the 24.8% overall average, which is drawn as a dashed line.

| Product | Return rate | vs average |
|---|---|---|
| Chair | 28.2% | +3.4 |
| Laptop | 27.4% | +2.6 |
| Monitor | 26.4% | +1.6 |
| Tablet | 24.2% | −0.6 |
| Phone | 23.1% | −1.7 |
| Printer | 22.3% | −2.5 |
| Desk | 21.7% | −3.1 |

The full spread is **6.5 percentage points**, and every product has roughly 214 orders.

**This is the chart most likely to be misread.** Chair's bar is visibly longest, which invites
the conclusion that Chair is a problem product. A chi-square test gives **p = 0.60** — and a
p-value near 1 means the spread is entirely consistent with chance. Under the usual 0.05
threshold, a difference this size would be extraordinary. With ~214 orders per product, random
variation alone produces a spread of this width.

The same test on region (p = 0.75) and salesperson (p = 0.57) gives the same answer, and a
model trained to predict returns performs no better than chance.

**Read this as one band, not a ranking.** A full explanation sits beneath the chart.

### 6. Revenue by payment method

A donut of the five methods, with percentages labelled outside the ring.

| Method | Revenue | Share |
|---|---|---|
| Online | $971,115 | 22.2% |
| Cash | $950,388 | 21.7% |
| Credit Card | $866,483 | 19.8% |
| Gift Card | $821,585 | 18.8% |
| Debit Card | $770,421 | 17.6% |

The spread from first to last is **4.6 points**. No method dominates. Online and cash are
statistically indistinguishable from each other, as are gift card and debit card.

### 7. Revenue by promotion

Four bars, with average discount and order count on hover.

| Promotion | Revenue | Share | Avg discount | Orders | Undiscounted |
|---|---|---|---|---|---|
| FREESHIP | $1,238,077 | 28.3% | 6.9% | 419 | 126 |
| WINTER15 | $1,078,012 | 24.6% | 7.3% | 373 | 98 |
| No Promotion | $1,074,247 | 24.5% | — | 370 | 90 |
| SAVE10 | $989,657 | 22.6% | 7.6% | 338 | 83 |

This chart is arithmetically correct and the four bars are a legitimate split of revenue.

**But it cannot tell you which campaign worked**, for two reasons:

- The code does not reliably record the discount given. `SAVE10` averages **7.6%** rather than
  10%, and 83 of its orders received nothing at all. `WINTER15` averages 7.3% with 98 at zero.
  `FREESHIP`, which should concern shipping rather than price, still carries a **6.9% price
  discount**.
- **307 of the 1,130 promoted orders were undiscounted entirely** — 27% of them.

So "FREESHIP is the biggest campaign" is a statement about how the codes are assigned, not
about discount effectiveness. An explanation sits beneath the chart.

*This bar set was previously missing the 24.5% "No Promotion" block entirely — see the
corrections section.*

### 8. Average delivery time by region

| Region | Average days |
|---|---|
| Central | 5.9 |
| South | 5.9 |
| East | 6.0 |
| West | 6.0 |
| North | 6.4 |

The entire spread is **0.5 days**. Every order in the dataset was delivered between 2 and 10
days after being placed, and no region delivers materially faster or slower than any other.
This is a flat chart by design — it exists to rule out delivery time as an explanation for the
regional revenue differences in chart 2.

### 9. Revenue by salesperson

| Salesperson | Revenue | Share | Avg order | Orders |
|---|---|---|---|---|
| Bob | $796,781 | 18.2% | $3,279 | 243 |
| Alice | $786,166 | 17.9% | $3,035 | 259 |
| Frank | $714,642 | 16.3% | $2,941 | 243 |
| Carlos | $707,167 | 16.1% | $2,619 | 270 |
| Eva | $698,670 | 16.0% | $2,960 | 236 |
| Diana | $676,568 | 15.4% | $2,717 | 249 |

The spread is **2.7 points** across six people, and order counts are within 236–270 of each
other. Bob's lead over Diana is $120,212, or 17.8%.

The chart title reads "spread is volume, not skill" because the order counts are close and the
revenue differences track them. Notably, **Carlos sold the most orders (270) but ranks fourth
on revenue** — his average order value is the lowest of the six. Revenue rank is not a
performance ranking.

### 10. Revenue heatmap — region × product

A 5 × 7 grid; every cell is labelled with its revenue figure. Cells range from **$68,566** to
**$172,222**.

This chart exists as a reconciliation test as much as an analytical one. All **35 cells** sum
to **$4,379,992** — the gross revenue total, to the cent. If any region or product were
dropped, double-counted or mislabelled anywhere in the pipeline, this grid would not balance.

Darkest cells cluster in North, consistent with that region leading chart 2. Nothing in the grid
contradicts the other charts.

---

## Notes & methodology

This section exists because three numbers on the dashboard look like findings and are not.

### The three explanations

Each of the following sits **directly beneath the chart it qualifies**, so the caveat can never
be separated from the number:

1. **Return rate by product** — the 6.5-point spread is noise (p = 0.60), not a ranking.
2. **Revenue by year** — 2025 is six months of data, not a 49% collapse.
3. **Revenue by promotion** — the codes don't record the discounts, so the bars can't rank
   campaigns.

The full reasoning for each is in the chart sections above.

### Data integrity — 7 of 7 checks passed

A collapsible block confirms the arithmetic underneath the dashboard:

| Check | Result |
|---|---|
| No duplicate orders | 1,500 rows, 1,500 unique `OrderID`, 0 duplicates |
| Revenue arithmetic reconciles | `TotalPrice = Qty × UnitPrice × (1 − Discount)` for every row, max difference $0.00 |
| Promotion field complete | All 1,500 orders carry a promotion value; promotion revenue reconciles to the total |
| Delivery dates are consistent | 0 orders delivered before they were placed; lead time 2–10 days, mean 6.0 |
| Monthly series has no gaps | 30 consecutive months, Jan 2023 to Jun 2025 |
| Every breakdown sums back to the total | Region, product, customer, payment, promotion, salesperson and year all reconcile |
| Category revenue is broadly volume-comparable | Order counts spread 195–240 (product) and 284–311 (region) |

**These checks and the three explanations are testing different things.** All seven checks pass,
which means every number on the page is internally correct. The explanations cover a different
question: whether a correct number represents a real pattern. A figure can be exactly right and
still be meaningless — the 2025 bar is arithmetically flawless and tells you nothing about
performance.

### Footer

The footer defines each term used anywhere on the page, and gives two specific cautions:

- **2025 covers January–June only** and must be compared with 2024 over the same months, never
  against a full-year total.
- **Revenue breakdowns are raw sums, not per-order values.** Average order value is on hover
  so order count and basket size can be separated.

It also explains how to read a p-value, since the return-rate explanation depends on it.

---

## What the dashboard actually shows

Taken as a whole, the picture is one of a **stable, evenly-distributed business**:

- Revenue is flat across two and a half years, with no trend and no seasonality.
- Regions, products, payment methods and salespeople are all within a few percentage points
  of each other. There is no standout winner anywhere.
- Order volume is the main driver of revenue differences, not pricing or performance.
- **One quarter of all orders is returned**, costing $1.11M — the most actionable number on
  the page, and the one with no explanation attached because it is a straightforward count.
- Delivery is uniform everywhere and rules out logistics as a factor.

The three apparent findings — the return-rate spread, the 2025 collapse and the promotion
ranking — are all artefacts of how the data is cut. That is the main thing this dashboard is
for.

---

## Data behind the dashboard

Source: `Product-Sales-Region.xlsx` — 1,500 orders, 19 columns, unmodified.

`cleaning.py` validates the data, fills the 370 missing promotion codes, and adds nine derived
columns (`DeliveryDays`, `Year`, `Month`, `Quarter`, `YearMonth`, `NetRevenue`,
`GrossProfit`, `DiscountBucket`, and `CalcRevenue` for auditing). Output: 1,500 rows × 28
columns.

**Metric definitions**

- **Gross revenue** — sum of `TotalPrice`.
- **Net revenue** — gross less the full value of returned orders.
- **Return rate** — share of orders flagged `Returned`. Because `OrderID` is unique, this is
  both the line rate and the order rate.
- **Average order value** — mean `TotalPrice` per order.
- **Average delivery** — mean days from `OrderDate` to `DeliveryDate`.

`Product-Sales-Region.xlsx` is read-only and never written to.

---

## Corrections applied

The most consequential change, because it silently removed a quarter of the data from one of
the charts:

**24.5% of revenue was invisible in the promotion breakdown.** `cleaning.py` filled missing
promotions with the literal string `"None"`:

```python
df["Promotion"] = df["Promotion"].fillna("None")   # wrong
```

pandas' `read_csv` treats `"None"` as a null value, so the sentinel was parsed straight back
to `NaN` on every read. **370 orders worth $1,074,247 disappeared from every
`groupby("Promotion")`** — including the $1,074,247 "No Promotion" bar now visible in chart 7.
Nothing raised an error; the number was simply wrong. The fix is `"No Promotion"`, which is
not in pandas' default null list and survives the round-trip. `cleaning.py` now re-reads its own
output and asserts that the promotion breakdown reconciles, so this cannot regress quietly.

**Other corrections**

- **2025 was charted as a full year**, showing a 49% decline. It is now labelled H1, compared
  like-for-like, and explained on the chart.
- **Return rates were presented as a ranking** despite a p-value of 0.60. The chart title,
  colour coding and note now state the spread is not significant.
- **Revenue was shown without average order value**, so volume differences read as
  performance. Average order value is now on hover for every revenue chart.
- **Explanation text was being parsed as HTML**, truncating any sentence containing `p < 0.05`.
  All generated text is now escaped.

---

## Files

| File | Role |
|---|---|
| `sales_dashboard.html` | **The dashboard.** Generated, self-contained, ~4.2 MB |
| `dashboard.py` | Builds it. Reads `cleaned_sales_data.csv` |
| `cleaning.py` | Validates and cleans the spreadsheet → `cleaned_sales_data.csv` |
| `cleaned_sales_data.csv` | Generated. 1,500 rows × 28 columns |
| `Product-Sales-Region.xlsx` | Source data. Never modified |
| `eda.py` | Optional: console exploratory analysis |
| `visualization.py` | Optional: `fig1`–`fig5` |
| `modelling.py` | Optional: `fig6`–`fig8` |

The three optional scripts are independent of each other and of the dashboard. They read the
same cleaned CSV and are not required to view or rebuild the dashboard.
