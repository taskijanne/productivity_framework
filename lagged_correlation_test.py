"""
Lagged Correlation Analysis - Test Script
Tests the concept of lagged correlation between AI metrics and productivity (CPS)

Uses the existing metrics_calculator to get proper metrics.
"""

import numpy as np
from scipy import stats
from datetime import datetime
import sys
sys.path.insert(0, 'c:/Users/janne/productivity_framework')

from services.metrics_calculator import calculate_metric
from models.enums import MetricType

# Calculate monthly metrics for Project 1, 2026
months = []
for m in range(1, 13):
    # Create month boundaries
    start = f"2026-{m:02d}-01 00:00:00"
    if m == 12:
        end = "2026-12-31 23:59:59"
    else:
        end = f"2026-{m+1:02d}-01 00:00:00"
    
    # Calculate each metric for this month using the API's calculator
    lt = calculate_metric(MetricType.LEAD_TIME_FOR_CHANGES.value, start, end, 1, "productivity_framework.db")
    df_metric = calculate_metric(MetricType.DEPLOYMENT_FREQUENCY.value, start, end, 1, "productivity_framework.db")
    cfr = calculate_metric(MetricType.CHANGE_FAILURE_RATE.value, start, end, 1, "productivity_framework.db")
    mttr = calculate_metric(MetricType.MEAN_TIME_TO_RECOVER.value, start, end, 1, "productivity_framework.db")
    loc_ai = calculate_metric(MetricType.LINES_OF_CODE_AI_PER_DAY.value, start, end, 1, "productivity_framework.db")
    accept = calculate_metric(MetricType.AI_ACCEPTANCE_RATE.value, start, end, 1, "productivity_framework.db")
    rework = calculate_metric(MetricType.AI_REWORK_RATE.value, start, end, 1, "productivity_framework.db")
    
    months.append({
        'month': m,
        'lead_time': lt.get('mean_value', 0),
        'df': df_metric.get('mean_value', 0),
        'cfr': cfr.get('mean_value', 0),
        'mttr': mttr.get('mean_value', 0),
        'loc_ai': loc_ai.get('mean_value', 0),
        'accept_rate': accept.get('mean_value', 0) * 100,  # as percentage
        'rework_rate': rework.get('mean_value', 0) * 100,  # as percentage
    })

# Calculate simple CPS (z-scored, inverted where needed)
import pandas as pd
monthly = pd.DataFrame(months)

def zscore(series):
    std = series.std()
    if std == 0:
        return pd.Series([0] * len(series))
    return (series - series.mean()) / std

# Z-scores (inverted for metrics where lower is better)
monthly['z_lead_time'] = -zscore(monthly['lead_time'])  # Inverted
monthly['z_df'] = zscore(monthly['df'])
monthly['z_cfr'] = -zscore(monthly['cfr'])  # Inverted  
monthly['z_mttr'] = -zscore(monthly['mttr'])  # Inverted

# Simple CPS = sum of z-scores (equal weights)
monthly['cps'] = monthly['z_lead_time'] + monthly['z_df'] + monthly['z_cfr'] + monthly['z_mttr']

print("=" * 80)
print("MONTHLY DATA (2026 Project 1)")
print("=" * 80)
print(f"{'Mon':>3} {'LOC_AI':>8} {'Accept%':>8} {'Rework%':>8} {'LeadTime':>9} {'DF':>5} {'CFR':>5} {'MTTR':>7} {'CPS':>8}")
print("-" * 80)
for _, row in monthly.iterrows():
    print(f"{int(row['month']):>3} {row['loc_ai']:>8.0f} {row['accept_rate']:>8.1f} {row['rework_rate']:>8.1f} {row['lead_time']:>9.0f} {row['df']:>5.2f} {row['cfr']:>5.2f} {row['mttr']:>7.1f} {row['cps']:>8.2f}")

# ============================================================================
# LAGGED CORRELATION ANALYSIS
# ============================================================================

def analyze_lagged_correlation(predictor_name, predictor_values, cps_values, max_lag=4):
    """Analyze correlation at different lags."""
    print(f"\n{'=' * 70}")
    print(f"LAGGED CORRELATION: {predictor_name} vs CPS")
    print("=" * 70)
    print(f"\nLag 0: {predictor_name}(month) correlated with CPS(same month)")
    print(f"Lag 1: {predictor_name}(month) correlated with CPS(month + 1)")
    print(f"Lag 2: {predictor_name}(month) correlated with CPS(month + 2)")
    print("etc.\n")
    
    print(f"{'Lag':>4} {'Correlation':>12} {'R²':>8} {'p-value':>10} {'n':>4} {'Interpretation':>25}")
    print("-" * 70)
    
    best_lag = 0
    best_r2 = 0
    
    for lag in range(0, max_lag + 1):
        if lag == 0:
            x = predictor_values
            y = cps_values
        else:
            x = predictor_values[:-lag]  # Earlier months
            y = cps_values[lag:]         # Later months
        
        n = len(x)
        if n < 3:
            print(f"{lag:>4} {'N/A':>12} {'N/A':>8} {'N/A':>10} {n:>4} {'Insufficient data':>25}")
            continue
        
        # Check for zero variance
        if np.std(x) == 0 or np.std(y) == 0:
            print(f"{lag:>4} {'N/A':>12} {'N/A':>8} {'N/A':>10} {n:>4} {'Zero variance':>25}")
            continue
        
        corr, p_val = stats.pearsonr(x, y)
        r2 = corr ** 2
        
        if r2 > best_r2:
            best_r2 = r2
            best_lag = lag
        
        # Interpretation
        if abs(corr) > 0.7:
            strength = "Strong"
        elif abs(corr) > 0.4:
            strength = "Moderate"
        else:
            strength = "Weak"
        
        direction = "positive" if corr > 0 else "negative"
        sig = "*" if p_val < 0.05 else ""
        
        print(f"{lag:>4} {corr:>12.3f} {r2:>8.3f} {p_val:>10.4f} {n:>4} {strength + ' ' + direction + sig:>25}")
    
    print(f"\n* = statistically significant (p < 0.05)")
    print(f">>> Best lag: {best_lag} months (R² = {best_r2:.3f})")
    
    return best_lag, best_r2

# Get arrays
loc_ai = monthly['loc_ai'].values
accept_rate = monthly['accept_rate'].values
rework_rate = monthly['rework_rate'].values
cps = monthly['cps'].values

# Analyze each AI metric
analyze_lagged_correlation("LOC_AI", loc_ai, cps)
analyze_lagged_correlation("ACCEPT_RATE", accept_rate, cps)
analyze_lagged_correlation("REWORK_RATE", rework_rate, cps)

# ============================================================================
# RATE OF CHANGE ANALYSIS
# ============================================================================
print("\n" + "=" * 70)
print("RATE OF CHANGE ANALYSIS: ΔLOC_AI vs CPS")
print("=" * 70)
print("\nΔLOC_AI = change in LOC_AI from previous month")
print("Does the RATE of change in AI usage predict productivity?\n")

monthly['delta_loc_ai'] = monthly['loc_ai'].diff()

# Skip first row (no delta)
delta = monthly['delta_loc_ai'].values[1:]
cps_for_delta = cps[1:]

if np.std(delta) > 0 and np.std(cps_for_delta) > 0:
    corr, p_val = stats.pearsonr(delta, cps_for_delta)
    r2 = corr ** 2
    
    print(f"Correlation: {corr:.3f}")
    print(f"R²: {r2:.3f}")
    print(f"p-value: {p_val:.4f}")
    print(f"n: {len(delta)}")
    
    if corr > 0:
        print("\nInterpretation: When LOC_AI is INCREASING, CPS tends to be higher")
    else:
        print("\nInterpretation: When LOC_AI is DECREASING, CPS tends to be higher")
else:
    print("Cannot compute - zero variance in data")
