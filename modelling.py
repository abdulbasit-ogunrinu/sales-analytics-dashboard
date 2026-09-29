import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys
import warnings
warnings.filterwarnings("ignore")

# Windows consoles default to cp1252 and raise UnicodeEncodeError on the
# box-drawing / arrow characters used in the report below.
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import (classification_report, confusion_matrix,
                             roc_auc_score, roc_curve,
                             mean_absolute_error, mean_squared_error, r2_score)
from sklearn.ensemble import (RandomForestClassifier, GradientBoostingClassifier,
                              RandomForestRegressor, GradientBoostingRegressor)
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.tree import DecisionTreeClassifier
import matplotlib.ticker as mticker

df = pd.read_csv("cleaned_sales_data.csv", parse_dates=["Date","OrderDate","DeliveryDate"])
PALETTE = ["#6D1220", "#A94659", "#C98A97", "#8E2233", "#4A0A14"]

print("=" * 60)
print("PHASE 4 — PREDICTIVE MODELLING")
print("=" * 60)

# ══════════════════════════════════════════════════════════════════════════════
# MODEL A — Return Prediction (Classification)
# Target: Returned (0 or 1)
# ══════════════════════════════════════════════════════════════════════════════
print("\n── MODEL A: Return Prediction (Classification) ──")

# NOTE: the encoders must be fitted on the TRAIN split only. Fitting them on the
# full frame before the split leaks the held-out rows' category vocabulary into
# training (a "test-set-informed" fit), which inflates CV scores.
cat_cols = ["Region", "Product", "CustomerType", "PaymentMethod",
            "Promotion", "StoreLocation", "Salesperson", "DiscountBucket"]
num_cols = ["Quantity", "UnitPrice", "Discount", "ShippingCost", "DeliveryDays"]

enc_cols = [c + "_enc" for c in cat_cols]
feature_cols = enc_cols + num_cols

# Split first, on the raw frame, so the encoders can be fitted train-only.
X_raw = df[cat_cols + num_cols]
y = df["Returned"]
X_train_raw, X_test_raw, y_train, y_test = train_test_split(
    X_raw, y, test_size=0.2, random_state=42, stratify=y)

# Fit encoders on the training half only, then transform the test half with the
# same mapping. (A category absent from train maps to -1 rather than inventing
# a new code.)
X_train = X_train_raw.copy()
X_test = X_test_raw.copy()
for col in cat_cols:
    le = LabelEncoder()
    X_train[col + "_enc"] = le.fit_transform(X_train[col].astype(str))
    X_test[col + "_enc"] = pd.Series(
        le.transform(X_test[col].astype(str)),
        index=X_test.index, dtype=X_train[col + "_enc"].dtype)

X_train = X_train[feature_cols]
X_test = X_test[feature_cols]

scaler = StandardScaler()
X_train_s = scaler.fit_transform(X_train)
X_test_s  = scaler.transform(X_test)

# Fit multiple classifiers
models_cls = {
    "Logistic Regression": LogisticRegression(max_iter=500, random_state=42),
    "Decision Tree":       DecisionTreeClassifier(max_depth=6, random_state=42),
    "Random Forest":       RandomForestClassifier(n_estimators=100, random_state=42),
    "Gradient Boosting":   GradientBoostingClassifier(n_estimators=100, random_state=42),
}

cls_results = {}
baseline_acc = y_train.value_counts(normalize=True).max()
print(f"\n{'Model':<25} {'Accuracy':>10} {'AUC':>8} {'F1-Return':>12} {'CV AUC':>9}")
print("-" * 70)
print(f"{'[majority-class baseline]':<25} {baseline_acc:>10.4f} {0.5:>8.4f} {'-':>12} {'-':>9}")

cv = StratifiedKFold(5, shuffle=True, random_state=42)

for name, model in models_cls.items():
    X_tr = X_train_s if name == "Logistic Regression" else X_train.values
    X_te = X_test_s  if name == "Logistic Regression" else X_test.values
    model.fit(X_tr, y_train)
    preds  = model.predict(X_te)
    proba  = model.predict_proba(X_te)[:, 1]
    acc    = (preds == y_test).mean()
    auc    = roc_auc_score(y_test, proba)
    report = classification_report(y_test, preds, output_dict=True)
    f1_ret = report["1"]["f1-score"]
    # Cross-validated AUC on the training data only, so the best-model pick is
    # not made on the same split the headline score is reported from.
    cv_auc = cross_val_score(
        type(model)(**model.get_params()), X_tr, y_train, cv=cv,
        scoring="roc_auc").mean()
    cls_results[name] = {"model": model, "acc": acc, "auc": auc,
                          "preds": preds, "proba": proba, "f1": f1_ret,
                          "cv_auc": cv_auc, "X_te": X_te}
    print(f"{name:<25} {acc:>10.4f} {auc:>8.4f} {f1_ret:>12.4f} {cv_auc:>9.4f}")

# Best model, chosen by CV AUC rather than test AUC
best_name = max(cls_results, key=lambda k: cls_results[k]["cv_auc"])
best = cls_results[best_name]
print(f"\n[Best] {best_name}  (CV AUC = {best['cv_auc']:.4f}, test AUC = {best['auc']:.4f})")

if best["cv_auc"] < 0.55:
    print("\n" + "!" * 70)
    print("!! NO PREDICTIVE SIGNAL. Every model's cross-validated AUC is within")
    print("!! chance of 0.50, so the ranking above is noise. The models cannot")
    print("!! tell you which orders will be returned, and accuracy is simply the")
    print("!! majority-class rate. Do not use these predictions operationally.")
    print("!" * 70)

print("\nClassification Report (Best Model):")
X_te_best = best["X_te"]
print(classification_report(y_test, best["preds"], target_names=["Not Returned","Returned"]))

# Feature importance (Random Forest)
rf = cls_results["Random Forest"]["model"]
importances = pd.Series(rf.feature_importances_, index=feature_cols)
importances = importances.sort_values(ascending=False).head(10)
print("\nTop 10 Feature Importances (Random Forest):")
print(importances.to_string())

# ── Save classification plots ─────────────────────────────────────────────────
fig, axes = plt.subplots(1, 3, figsize=(16, 5))
fig.suptitle("Return Prediction — Model Evaluation", fontsize=14, fontweight="bold")

# Confusion matrix
cm = confusion_matrix(y_test, best["preds"])
import seaborn as sns
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", ax=axes[0],
            xticklabels=["Not Ret.","Returned"], yticklabels=["Not Ret.","Returned"])
axes[0].set_title(f"Confusion Matrix\n({best_name})", fontweight="bold")
axes[0].set_ylabel("Actual"); axes[0].set_xlabel("Predicted")

# ROC curves
for name, res in cls_results.items():
    fpr, tpr, _ = roc_curve(y_test, res["proba"])
    axes[1].plot(fpr, tpr, label=f"{name} ({res['auc']:.3f})")
axes[1].plot([0,1],[0,1],"k--", linewidth=1)
axes[1].set_title("ROC Curves (All Models)", fontweight="bold")
axes[1].set_xlabel("False Positive Rate"); axes[1].set_ylabel("True Positive Rate")
axes[1].legend(fontsize=8)

# Feature importance bar
importances.sort_values().plot(kind="barh", ax=axes[2], color=PALETTE[0])
axes[2].set_title("Feature Importance\n(Random Forest)", fontweight="bold")
axes[2].set_xlabel("Importance Score")

fig.tight_layout()
fig.savefig("fig6_classification.png", dpi=150, bbox_inches="tight")
print("\n[✓] fig6_classification.png saved")
plt.close()

# ══════════════════════════════════════════════════════════════════════════════
# MODEL B — Revenue Prediction (Regression)
# Target: TotalPrice
# ══════════════════════════════════════════════════════════════════════════════
print("\n── MODEL B: Revenue Prediction (Regression) ──")
print("   NOTE: TotalPrice = Quantity x UnitPrice x (1 - Discount) exactly, and")
print("   all three are supplied as features. This is an identity, not a")
print("   prediction problem - a near-perfect score is arithmetic, not skill.")

reg_cat = [c + "_enc" for c in cat_cols]
reg_num = ["Quantity", "UnitPrice", "Discount", "ShippingCost"]
reg_features = reg_cat + reg_num

# Use the same random_state so the numeric and categorical halves stay row-aligned.
idx = np.arange(len(df))
idx_tr, idx_te = train_test_split(idx, test_size=0.2, random_state=42)
X_tr_r = df.loc[idx_tr, reg_num].copy()
X_te_r = df.loc[idx_te, reg_num].copy()
y_tr_r = df.loc[idx_tr, "TotalPrice"]
y_te_r = df.loc[idx_te, "TotalPrice"]

# Fit the categorical encoders on the training half only (no test-set leakage).
for col in cat_cols:
    le = LabelEncoder()
    X_tr_r[col + "_enc"] = le.fit_transform(df.loc[idx_tr, col].astype(str))
    X_te_r[col + "_enc"] = le.transform(df.loc[idx_te, col].astype(str))

X_tr_r = X_tr_r[reg_features]
X_te_r = X_te_r[reg_features]

scaler_r = StandardScaler()
X_tr_rs = scaler_r.fit_transform(X_tr_r)
X_te_rs  = scaler_r.transform(X_te_r)

# Regressor classes only. (An earlier draft built this dict with
# *Classifier estimators for a regression target, then immediately overwrote it
# with the regressors below - the classifier dict was dead code that could only
# ever raise if it were ever used.)
models_reg = {
    "Linear Regression": LinearRegression(),
    "Random Forest":     RandomForestRegressor(n_estimators=100, random_state=42),
    "Gradient Boosting": GradientBoostingRegressor(n_estimators=100, random_state=42),
}

print(f"\n{'Model':<25} {'MAE':>10} {'RMSE':>10} {'R²':>8}")
print("-" * 58)

reg_results = {}
for name, model in models_reg.items():
    X_tr_use = X_tr_rs if name == "Linear Regression" else X_tr_r.values
    X_te_use = X_te_rs if name == "Linear Regression" else X_te_r.values
    model.fit(X_tr_use, y_tr_r)
    preds = model.predict(X_te_use)
    mae   = mean_absolute_error(y_te_r, preds)
    rmse  = np.sqrt(mean_squared_error(y_te_r, preds))
    r2    = r2_score(y_te_r, preds)
    reg_results[name] = {"model": model, "preds": preds, "mae": mae, "rmse": rmse, "r2": r2}
    print(f"{name:<25} {mae:>10.2f} {rmse:>10.2f} {r2:>8.4f}")

best_reg_name = max(reg_results, key=lambda k: reg_results[k]["r2"])
best_reg = reg_results[best_reg_name]
print(f"\n[Best] {best_reg_name}  (R² = {best_reg['r2']:.4f})")

# Feature importance for best regressor (RF or GB)
if hasattr(reg_results[best_reg_name]["model"], "feature_importances_"):
    reg_imp = pd.Series(
        reg_results[best_reg_name]["model"].feature_importances_,
        index=reg_features).sort_values(ascending=False).head(10)
    print("\nTop 10 Revenue Drivers:")
    print(reg_imp.to_string())

# ── Save regression plots ──────────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(12, 5))
fig.suptitle("Revenue Prediction — Model Evaluation", fontsize=14, fontweight="bold")

# Actual vs predicted
axes[0].scatter(y_te_r, best_reg["preds"], alpha=0.3, color=PALETTE[0], s=20)
lims = [min(y_te_r.min(), best_reg["preds"].min()),
        max(y_te_r.max(), best_reg["preds"].max())]
axes[0].plot(lims, lims, "r--", linewidth=1.5, label="Perfect fit")
axes[0].set_title(f"Actual vs Predicted\n({best_reg_name})", fontweight="bold")
axes[0].set_xlabel("Actual Revenue ($)"); axes[0].set_ylabel("Predicted Revenue ($)")
axes[0].xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
axes[0].yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
axes[0].legend()

# Feature importance
if hasattr(reg_results[best_reg_name]["model"], "feature_importances_"):
    reg_imp.sort_values().plot(kind="barh", ax=axes[1], color=PALETTE[1])
    axes[1].set_title("Revenue Feature Importance", fontweight="bold")
    axes[1].set_xlabel("Importance Score")

fig.tight_layout()
fig.savefig("fig7_regression.png", dpi=150, bbox_inches="tight")
print("\n[✓] fig7_regression.png saved")
plt.close()


# MODEL C — Monthly Revenue Forecast (Time Series)
print("\n── MODEL C: Monthly Revenue Forecast (Time Series) ──")

monthly = (df.groupby(pd.Grouper(key="Date", freq="ME"))["TotalPrice"].sum()
             .reset_index().rename(columns={"Date":"ds","TotalPrice":"y"}))

# Simple approach: rolling 3-month avg + linear trend extrapolation
monthly["RollingAvg3"] = monthly["y"].rolling(3).mean()

# Linear trend
x = np.arange(len(monthly))
coeffs = np.polyfit(x, monthly["y"], 1)
trend_line = np.poly1d(coeffs)

# Forecast next 6 months
n_forecast = 6
future_x = np.arange(len(monthly), len(monthly) + n_forecast)
forecast_vals = trend_line(future_x)

last_date = monthly["ds"].iloc[-1]
future_dates = pd.date_range(start=last_date + pd.DateOffset(months=1),
                              periods=n_forecast, freq="ME")

# Honest uncertainty band. The previous version drew a fixed "±12% confidence
# band" that was a hard-coded constant with no statistical basis. Replace it
# with a proper prediction interval from the trend fit's residuals.
resid = monthly["y"] - trend_line(x)
sigma = float(np.sqrt((resid ** 2).sum() / max(1, len(x) - 2)))
# 95% interval on a mean response, widened by the leverage term.
t_crit = 1.96
leverage = 1 + (1 / len(x)) + ((future_x - x.mean()) ** 2 / ((x - x.mean()) ** 2).sum())
band = t_crit * sigma * np.sqrt(leverage)

# Is there a trend at all?
slope_p = float(np.corrcoef(x, monthly["y"])[0, 1])
r2_trend = float(np.corrcoef(x, monthly["y"])[0, 1] ** 2)

print(f"\nActual period : {monthly['ds'].iloc[0].strftime('%b %Y')} – {last_date.strftime('%b %Y')}")
print(f"Forecast period: {future_dates[0].strftime('%b %Y')} – {future_dates[-1].strftime('%b %Y')}")
print(f"\nTrend: slope ${coeffs[0]:,.0f}/month, r = {slope_p:+.3f} (R² = {r2_trend:.3f})")
print(f"Residual sigma: ${sigma:,.0f}   95% half-width: ${band.mean():,.0f} "
      f"({band.mean() / forecast_vals.mean() * 100:.0f}% of the forecast)")

if r2_trend < 0.15:
    print("\n" + "!" * 70)
    print("!! NO USABLE TREND. The monthly series is essentially flat")
    print(f"!! (R² = {r2_trend:.3f}), and month-to-month noise is larger than the")
    print("!! fitted trend. Treat the numbers below as a flat baseline around the")
    print("!! historical average, not as a forecast with a direction.")
    print("!" * 70)

print("\nForecasted monthly revenue (95% prediction interval):")
for d, v, bw in zip(future_dates, forecast_vals, band):
    print(f"  {d.strftime('%b %Y')}: ${v:,.0f}  +/- ${bw:,.0f}")

fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(monthly["ds"], monthly["y"] / 1000, label="Actual", color=PALETTE[0],
        linewidth=2, marker="o", markersize=4)
ax.plot(monthly["ds"], trend_line(x) / 1000, label="Linear Trend",
        color=PALETTE[2], linestyle="--", linewidth=1.5)
ax.plot(future_dates, forecast_vals / 1000, label="6-Month Forecast",
        color=PALETTE[1], linestyle="--", marker="s", markersize=6, linewidth=2)
ax.fill_between(future_dates, (forecast_vals - band) / 1000,
                (forecast_vals + band) / 1000, alpha=0.15, color=PALETTE[1],
                label="95% Prediction Interval")
ax.axvline(last_date, color="gray", linestyle=":", linewidth=1, alpha=0.7)
ax.set_title("Monthly Revenue — Actual + 6-Month Forecast", fontsize=13, fontweight="bold")
ax.set_ylabel("Revenue ($K)")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}K"))
ax.legend()
fig.tight_layout()
fig.savefig("fig8_forecast.png", dpi=150, bbox_inches="tight")
print("\n[✓] fig8_forecast.png saved")
plt.close()

print("\n[✓] Phase 4 complete — all models trained and plots saved.")