"""
Fix Change Failure Rate for Project 2 2026.
Current:  [2, 2, 2, 4, 1, 2, 2, 5, 2, 3, 2, 2] = 29 failures
Target:   [2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 2, 1] = 22 failures

Changes needed:
- Apr: 4→2 (remove 2)
- May: 1→2 (add 1)  
- Aug: 5→2 (remove 3)
- Oct: 3→1 (remove 2)
- Dec: 2→1 (remove 1)
"""
import pandas as pd
import numpy as np

print("Reading data_observations.csv...")
df = pd.read_csv('data_observations.csv', delimiter=';', dtype=str)
df['timestamp'] = pd.to_datetime(df['timestamp'])

# Get max ID for creating new records
max_id = df['id'].astype(int).max()

# Current vs Target failures per month
current = {1: 2, 2: 2, 3: 2, 4: 4, 5: 1, 6: 2, 7: 2, 8: 5, 9: 2, 10: 3, 11: 2, 12: 2}
target =  {1: 2, 2: 2, 3: 2, 4: 2, 5: 2, 6: 2, 7: 2, 8: 2, 9: 2, 10: 1, 11: 2, 12: 1}

changes = {m: target[m] - current[m] for m in range(1, 13)}
print("Changes needed per month:", {m: c for m, c in changes.items() if c != 0})

new_rows = []

for month in range(1, 13):
    change = changes[month]
    if change == 0:
        continue
    
    # Get failures for this month
    mask = (df['project_id'] == '2') & (df['timestamp'].dt.year == 2026) & \
           (df['timestamp'].dt.month == month) & (df['type'] == 'DEPLOYMENT_FAILURE')
    month_fails = df[mask]
    
    if change < 0:
        # REMOVE failures (and their linked FIX records)
        to_remove = abs(change)
        removed = 0
        for idx in month_fails.index:
            if removed >= to_remove:
                break
            fail_id = df.loc[idx, 'id']
            # Remove the failure
            df = df.drop(idx)
            # Remove linked FIX record
            fix_mask = (df['type'] == 'DEPLOYMENT_FAILURE_FIX') & (df['deployment_failure_id'] == fail_id)
            df = df[~fix_mask]
            removed += 1
        print(f"Month {month}: Removed {removed} failures (and their FIX records)")
    
    elif change > 0:
        # ADD failures (copy existing failure and create new FIX)
        to_add = change
        if len(month_fails) > 0:
            sample_fail = month_fails.iloc[0].copy()
            # Find its FIX record
            sample_fix = df[(df['type'] == 'DEPLOYMENT_FAILURE_FIX') & 
                           (df['deployment_failure_id'] == sample_fail['id'])]
            
            for i in range(to_add):
                max_id += 1
                new_fail = sample_fail.copy()
                new_fail['id'] = str(max_id)
                # Adjust timestamp slightly
                new_fail['timestamp'] = pd.Timestamp(2026, month, 15 + i, 10, 0, 0)
                new_rows.append(new_fail)
                
                if len(sample_fix) > 0:
                    max_id += 1
                    new_fix = sample_fix.iloc[0].copy()
                    new_fix['id'] = str(max_id)
                    new_fix['deployment_failure_id'] = new_fail['id']
                    new_fix['timestamp'] = pd.Timestamp(2026, month, 15 + i, 12, 0, 0)
                    new_rows.append(new_fix)
            
            print(f"Month {month}: Added {to_add} failures (with FIX records)")

# Add new rows
if new_rows:
    new_df = pd.DataFrame(new_rows)
    new_df['timestamp'] = new_df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
    df['timestamp'] = df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
    df = pd.concat([df, new_df], ignore_index=True)
else:
    df['timestamp'] = df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')

print(f"\nTotal rows after changes: {len(df)}")
df.to_csv('data_observations.csv', sep=';', index=False)
print("Saved data_observations.csv")

# Verify
print("\nVerification:")
df['timestamp'] = pd.to_datetime(df['timestamp'])
for month in range(1, 13):
    mask = (df['project_id'] == '2') & (df['timestamp'].dt.year == 2026) & \
           (df['timestamp'].dt.month == month) & (df['type'] == 'DEPLOYMENT_FAILURE')
    count = len(df[mask])
    print(f"  Month {month}: {count} failures (target: {target[month]})")
