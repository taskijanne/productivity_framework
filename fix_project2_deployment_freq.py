"""
Fix Deployment Frequency for Project 2 2026.
Target: 10,10,9,8,7,6,5,5,4,3,5,3 (decline with realistic variability)

This is tricky because deployments have linked commits, failures, and fixes.
Strategy:
- To ADD deployments: Create new deployment rows with new IDs
- To REMOVE deployments: Remove deployments that have NO linked failures (safest)
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

print("Reading data_observations.csv...")
df = pd.read_csv('data_observations.csv', delimiter=';', dtype=str)
df['timestamp'] = pd.to_datetime(df['timestamp'])

# Current vs Target deployments per month
current = {1: 9, 2: 8, 3: 9, 4: 7, 5: 5, 6: 6, 7: 5, 8: 7, 9: 5, 10: 4, 11: 5, 12: 3}
target =  {1: 10, 2: 10, 3: 9, 4: 8, 5: 7, 6: 6, 7: 5, 8: 5, 9: 4, 10: 3, 11: 5, 12: 3}

# Calculate changes needed
changes = {m: target[m] - current[m] for m in range(1, 13)}
print("Changes needed per month:", changes)

# Get max ID to create new unique IDs
max_id = df['id'].astype(int).max()
print(f"Current max ID: {max_id}")

# Filter to Project 2, 2026 deployments
mask_p2_2026_dep = (df['project_id'] == '2') & (df['timestamp'].dt.year == 2026) & (df['type'] == 'DEPLOYMENT')

# Get all deployment_failure_ids that are linked (these deployments have failures)
failures = df[(df['project_id'] == '2') & (df['type'] == 'DEPLOYMENT_FAILURE')]
deployments_with_failures = set(failures['deployment_id'].dropna().astype(str).values)
print(f"Deployments with failures (cannot remove): {len(deployments_with_failures)}")

new_rows = []

for month in range(1, 13):
    change = changes[month]
    month_mask = mask_p2_2026_dep & (df['timestamp'].dt.month == month)
    month_deps = df.loc[month_mask]
    
    if change > 0:
        # ADD deployments
        # Copy existing deployments and modify timestamp/id
        sample_dep = month_deps.iloc[0] if len(month_deps) > 0 else None
        if sample_dep is not None:
            for i in range(change):
                max_id += 1
                new_row = sample_dep.copy()
                new_row['id'] = str(max_id)
                # Spread timestamps throughout the month
                day = 5 + i * 7  # days 5, 12, 19, etc.
                new_row['timestamp'] = datetime(2026, month, min(day, 28), 14, 0, 0)
                new_rows.append(new_row)
            print(f"Month {month}: Added {change} deployments")
    
    elif change < 0:
        # REMOVE deployments (only those without failures)
        to_remove = abs(change)
        removed = 0
        for idx in month_deps.index:
            dep_id = df.loc[idx, 'id']
            if dep_id not in deployments_with_failures and removed < to_remove:
                df = df.drop(idx)
                # Also remove any commits linked to this deployment
                df = df[df['deployment_id'] != dep_id]
                removed += 1
        print(f"Month {month}: Removed {removed} deployments (target: {to_remove})")

# Add new rows
if new_rows:
    new_df = pd.DataFrame(new_rows)
    new_df['timestamp'] = new_df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
    df['timestamp'] = df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
    df = pd.concat([df, new_df], ignore_index=True)
else:
    df['timestamp'] = df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')

# Save
print(f"\nTotal rows after changes: {len(df)}")
df.to_csv('data_observations.csv', sep=';', index=False)
print("Saved data_observations.csv")
