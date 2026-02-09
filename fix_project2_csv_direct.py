"""
Fix Project 2 2026 data directly in CSV to tell the 'unhappy case' story.
Team goes all-in on AI and never pulls back.

Fixes applied:
1. AI LOC %: 60% → 75% (keeps climbing, never moderates)
2. Total LOC: ~74k total (higher than 2025's 64k)
3. Satisfaction: 8.6 → 5.2 (honeymoon then cliff)

This script modifies the CSV directly without breaking ID linkages.
"""

import pandas as pd
import numpy as np
from datetime import datetime

# Read CSV
print("Reading data_observations.csv...")
df = pd.read_csv('data_observations.csv', delimiter=';')
print(f"Total rows: {len(df)}")

# Filter to Project 2, 2026 only
df['timestamp'] = pd.to_datetime(df['timestamp'])
mask_p2_2026 = (df['project_id'] == 2) & (df['timestamp'].dt.year == 2026)
print(f"Project 2 2026 rows: {mask_p2_2026.sum()}")

# ============================================
# FIX 0: Fix negative AI LOC values (data corruption from previous run)
# ============================================
print("\n=== FIX 0: Negative AI LOC ===")
ai_loc_mask_neg = mask_p2_2026 & (df['type'] == 'LINES_OF_CODE_AI') & (df['value'] < 0)
neg_count = ai_loc_mask_neg.sum()
print(f"Found {neg_count} negative AI LOC values")
if neg_count > 0:
    df.loc[ai_loc_mask_neg, 'value'] = df.loc[ai_loc_mask_neg, 'value'].abs()
    print(f"Converted to positive values")

# ============================================
# FIX 1: Total LOC (~74k with proper curve) - DO THIS FIRST
# ============================================
print("\n=== FIX 1: Total LOC ===")

loc_mask = mask_p2_2026 & (df['type'] == 'LINES_OF_CODE')
ai_loc_mask = mask_p2_2026 & (df['type'] == 'LINES_OF_CODE_AI')

# Current totals
current_loc = df.loc[loc_mask, 'value'].sum()
current_ai_loc = df.loc[ai_loc_mask, 'value'].sum()
print(f"Current Total LOC: {current_loc:.0f}")
print(f"Current AI LOC: {current_ai_loc:.0f}")
print(f"Current AI %: {current_ai_loc/current_loc*100:.1f}%")

# Target: ~74k total, with monthly distribution:
# Q1: Ramp up (5-6k/month)
# Q2: Peak (7-8k/month) 
# Q3: Decline starts (6-7k/month)
# Q4: Decline continues (4-5k/month)
target_monthly_loc = {
    1: 5500, 2: 5800, 3: 6200, 4: 7000,
    5: 7500, 6: 7800, 7: 6800, 8: 6400,
    9: 6000, 10: 5500, 11: 4800, 12: 4700
}
# Total: 74,000

for month in range(1, 13):
    month_mask = mask_p2_2026 & (df['timestamp'].dt.month == month)
    month_loc_mask = month_mask & (df['type'] == 'LINES_OF_CODE')
    
    current_month_loc = df.loc[month_loc_mask, 'value'].sum()
    if current_month_loc > 0:
        scale_factor = target_monthly_loc[month] / current_month_loc
        df.loc[month_loc_mask, 'value'] = df.loc[month_loc_mask, 'value'] * scale_factor

# Verify total LOC
new_loc = df.loc[loc_mask, 'value'].sum()
print(f"New Total LOC: {new_loc:.0f}")

# ============================================
# FIX 2: AI LOC % (60% → 75%) - DO THIS AFTER Total LOC is set
# ============================================
print("\n=== FIX 2: AI LOC % ===")

# Target: 60% in Jan → 75% in Dec
# Monthly AI ratio targets
monthly_ai_ratio = {
    1: 0.60, 2: 0.62, 3: 0.64, 4: 0.66,
    5: 0.68, 6: 0.70, 7: 0.71, 8: 0.72,
    9: 0.73, 10: 0.74, 11: 0.74, 12: 0.75
}

# For each month, adjust AI LOC values to hit target ratio BASED ON NEW TOTAL LOC
for month in range(1, 13):
    month_mask = mask_p2_2026 & (df['timestamp'].dt.month == month)
    month_loc_mask = month_mask & (df['type'] == 'LINES_OF_CODE')
    month_ai_mask = month_mask & (df['type'] == 'LINES_OF_CODE_AI')
    
    # Use the already-scaled total LOC
    month_loc = df.loc[month_loc_mask, 'value'].sum()
    month_ai = df.loc[month_ai_mask, 'value'].sum()
    
    if month_loc > 0 and month_ai_mask.sum() > 0:
        target_ai = month_loc * monthly_ai_ratio[month]
        scale_factor = target_ai / month_ai if month_ai > 0 else 1
        df.loc[month_ai_mask, 'value'] = df.loc[month_ai_mask, 'value'] * scale_factor
        print(f"Month {month}: LOC={month_loc:.0f}, AI target={target_ai:.0f} ({monthly_ai_ratio[month]*100:.0f}%)")

# Verify
final_loc = df.loc[loc_mask, 'value'].sum()
final_ai_loc = df.loc[ai_loc_mask, 'value'].sum()
print(f"Final Total LOC: {final_loc:.0f}")
print(f"Final AI LOC: {final_ai_loc:.0f}")
print(f"Final AI %: {final_ai_loc/final_loc*100:.1f}%")

# ============================================
# FIX 3: Satisfaction (honeymoon then cliff)
# ============================================
print("\n=== FIX 3: Satisfaction ===")

# Target pattern: 8.6 → 5.2 (honeymoon then cliff)
# Q1: 8.5-8.8 (honeymoon - AI is exciting!)
# Q2: 7.4-8.0 (starting to notice problems)
# Q3: 6.5-7.0 (frustration growing)
# Q4: 5.2-6.0 (cliff - burnout, tech debt, chaos)

# Note: Type is 'SATISFACTION' not 'DEVELOPER_SATISFACTION'
sat_mask = mask_p2_2026 & (df['type'] == 'SATISFACTION')

# Define target by month
target_sat = {
    1: 8.6, 2: 8.7, 3: 8.5,      # Q1: honeymoon
    4: 8.0, 5: 7.6, 6: 7.4,      # Q2: starting to notice
    7: 7.0, 8: 6.7, 9: 6.5,      # Q3: frustration
    10: 6.0, 11: 5.5, 12: 5.2    # Q4: cliff
}

for month in range(1, 13):
    month_sat_mask = mask_p2_2026 & (df['type'] == 'SATISFACTION') & (df['timestamp'].dt.month == month)
    if month_sat_mask.sum() > 0:
        # Add some noise around target
        base = target_sat[month]
        noise = np.random.uniform(-0.15, 0.15, size=month_sat_mask.sum())
        df.loc[month_sat_mask, 'value'] = base + noise

# Verify
for q, months in [(1, [1,2,3]), (2, [4,5,6]), (3, [7,8,9]), (4, [10,11,12])]:
    q_mask = sat_mask & df['timestamp'].dt.month.isin(months)
    avg = df.loc[q_mask, 'value'].mean()
    print(f"Q{q} Satisfaction avg: {avg:.2f}")

# ============================================
# Round values and save
# ============================================
print("\n=== Saving CSV ===")

# Round LOC values to integers
df.loc[df['type'].isin(['LINES_OF_CODE', 'LINES_OF_CODE_AI']), 'value'] = \
    df.loc[df['type'].isin(['LINES_OF_CODE', 'LINES_OF_CODE_AI']), 'value'].round(0)

# Round satisfaction to 1 decimal
df.loc[df['type'] == 'SATISFACTION', 'value'] = \
    df.loc[df['type'] == 'SATISFACTION', 'value'].round(1)

# Convert timestamp back to string format
df['timestamp'] = df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')

# Save
df.to_csv('data_observations.csv', sep=';', index=False)
print("Saved data_observations.csv")

# ============================================
# Final verification
# ============================================
print("\n=== Final Verification ===")
df2 = pd.read_csv('data_observations.csv', delimiter=';')
df2['timestamp'] = pd.to_datetime(df2['timestamp'])
p2_2026 = (df2['project_id'] == 2) & (df2['timestamp'].dt.year == 2026)

loc_total = df2.loc[p2_2026 & (df2['type'] == 'LINES_OF_CODE'), 'value'].sum()
ai_total = df2.loc[p2_2026 & (df2['type'] == 'LINES_OF_CODE_AI'), 'value'].sum()
sat_jan = df2.loc[p2_2026 & (df2['type'] == 'SATISFACTION') & (df2['timestamp'].dt.month == 1), 'value'].mean()
sat_dec = df2.loc[p2_2026 & (df2['type'] == 'SATISFACTION') & (df2['timestamp'].dt.month == 12), 'value'].mean()

print(f"Total LOC: {loc_total:.0f} (target: ~74k)")
print(f"AI LOC: {ai_total:.0f}")
print(f"AI %: {ai_total/loc_total*100:.1f}% (target: ~67% blended)")
print(f"Satisfaction Jan: {sat_jan:.1f} (target: 8.6)")
print(f"Satisfaction Dec: {sat_dec:.1f} (target: 5.2)")
print("\nDone! Now run: python init_database.py && python data_ingestor.py")
