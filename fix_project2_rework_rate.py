"""
Fix AI Rework Rate for Project 2 2026.
Target: Steady climb from 5% → 40% (tech debt accumulating from over-trusting AI)
"""
import pandas as pd
import numpy as np

print("Reading data_observations.csv...")
df = pd.read_csv('data_observations.csv', delimiter=';', dtype=str)
df['timestamp'] = pd.to_datetime(df['timestamp'])

# Filter to Project 2, 2026, COMMIT type
mask = (df['project_id'] == '2') & (df['timestamp'].dt.year == 2026) & (df['type'] == 'COMMIT')
print(f"Project 2 2026 COMMIT rows: {mask.sum()}")

# Target rework percentages by month (steady climb 5% → 40%)
target_rework_pct = {
    1: 0.05, 2: 0.07, 3: 0.10, 4: 0.14,
    5: 0.18, 6: 0.22, 7: 0.26, 8: 0.30,
    9: 0.33, 10: 0.35, 11: 0.38, 12: 0.40
}

# For each month, set the appropriate number of commits to have ai_rework_commit=1
for month in range(1, 13):
    month_mask = mask & (df['timestamp'].dt.month == month)
    month_commits = df.loc[month_mask].index.tolist()
    total = len(month_commits)
    
    if total > 0:
        target_rework = int(total * target_rework_pct[month])
        
        # First, reset all to 0
        df.loc[month_mask, 'ai_rework_commit'] = ''
        
        # Then, randomly select commits to mark as rework
        np.random.seed(42 + month)  # Reproducible
        rework_indices = np.random.choice(month_commits, size=target_rework, replace=False)
        df.loc[rework_indices, 'ai_rework_commit'] = '1'
        
        actual_rework = (df.loc[month_mask, 'ai_rework_commit'] == '1').sum()
        print(f"Month {month:2d}: {total:3d} commits, target {target_rework_pct[month]*100:.0f}% = {target_rework}, actual = {actual_rework}")

# Convert timestamp back to string
df['timestamp'] = df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')

# Save
print("\nSaving...")
df.to_csv('data_observations.csv', sep=';', index=False)
print("Done! Now merge P2 changes back to virgin file.")
