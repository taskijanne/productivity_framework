"""
Script to adjust Change Failure Rate (CFR) for 2025 data.
Goal: CFR between 15-30%, lower in summer (Jun-Aug), higher in Nov-Dec.
Applies same changes to both Project 1 and Project 2.
"""

import pandas as pd
from datetime import datetime, timedelta

# Read the CSV
df = pd.read_csv('data_observations.csv', delimiter=';')

print("Original row count:", len(df))

# ============================================================================
# PART 1: IDENTIFY FAILURES TO REMOVE
# ============================================================================
# Remove failures from: Feb (1), Jun (1), Jul (3), Aug (1), Sep (1), Oct (2)

# Project 1 failure IDs to remove (last failures in each month)
p1_failures_to_remove = [
    4997,   # Feb - last of 3
    5004,   # Jun - last of 2
    5006, 5007, 5008,  # Jul - last 3 of 4
    5010,   # Aug - last of 2
    5014,   # Sep - last of 3
    5018, 5019,  # Oct - last 2 of 4
]

# Project 2 failure IDs to remove (equivalent failures)
p2_failures_to_remove = [
    60765,  # Feb
    60772,  # Jun
    60774, 60775, 60776,  # Jul
    60778,  # Aug
    60781,  # Sep
    60784, 60785,  # Oct
]

# Find corresponding FIX IDs for Project 1
p1_fix_to_remove = []
for fail_id in p1_failures_to_remove:
    fix_rows = df[(df['type'] == 'DEPLOYMENT_FAILURE_FIX') & (df['deployment_failure_id'] == fail_id)]
    p1_fix_to_remove.extend(fix_rows['id'].tolist())

# Find corresponding FIX IDs for Project 2
p2_fix_to_remove = []
for fail_id in p2_failures_to_remove:
    fix_rows = df[(df['type'] == 'DEPLOYMENT_FAILURE_FIX') & (df['deployment_failure_id'] == fail_id)]
    p2_fix_to_remove.extend(fix_rows['id'].tolist())

print("\nProject 1 failures to remove:", p1_failures_to_remove)
print("Project 1 fixes to remove:", p1_fix_to_remove)
print("Project 2 failures to remove:", p2_failures_to_remove)
print("Project 2 fixes to remove:", p2_fix_to_remove)

# Remove these rows
all_ids_to_remove = p1_failures_to_remove + p1_fix_to_remove + p2_failures_to_remove + p2_fix_to_remove
df = df[~df['id'].isin(all_ids_to_remove)]

print("\nAfter removing failures, row count:", len(df))

# ============================================================================
# PART 2: ADD NEW FAILURES FOR NOV AND DEC
# ============================================================================
# Nov: currently 2, need 3 -> add 1
# Dec: currently 1, need 2 -> add 1

# Get max ID for new records
max_id = df['id'].max()
print("\nMax ID before adding:", max_id)

new_rows = []

# --- PROJECT 1 ---
# Nov: Add failure for deployment 88 (2025-11-03 14:30:00) - first available without failure
# Failure occurs ~30 min after deployment, fix ~10 hours later
new_rows.append({
    'id': max_id + 1,
    'project_id': 1,
    'timestamp': '2025-11-03 15:02:00',
    'type': 'DEPLOYMENT_FAILURE',
    'value': None,
    'developer_id': None,
    'commit_hash': None,
    'deployment_id': 88,
    'deployment_failure_id': None
})
new_rows.append({
    'id': max_id + 2,
    'project_id': 1,
    'timestamp': '2025-11-04 01:15:00',
    'type': 'DEPLOYMENT_FAILURE_FIX',
    'value': None,
    'developer_id': None,
    'commit_hash': None,
    'deployment_id': None,
    'deployment_failure_id': max_id + 1
})

# Dec: Add failure for deployment 98 (2025-12-08 13:50:00)
new_rows.append({
    'id': max_id + 3,
    'project_id': 1,
    'timestamp': '2025-12-08 14:25:00',
    'type': 'DEPLOYMENT_FAILURE',
    'value': None,
    'developer_id': None,
    'commit_hash': None,
    'deployment_id': 98,
    'deployment_failure_id': None
})
new_rows.append({
    'id': max_id + 4,
    'project_id': 1,
    'timestamp': '2025-12-09 00:40:00',
    'type': 'DEPLOYMENT_FAILURE_FIX',
    'value': None,
    'developer_id': None,
    'commit_hash': None,
    'deployment_id': None,
    'deployment_failure_id': max_id + 3
})

# --- PROJECT 2 ---
# Nov: Add failure for deployment 55870 (2025-11-03 14:30:00)
new_rows.append({
    'id': max_id + 5,
    'project_id': 2,
    'timestamp': '2025-11-03 15:02:00',
    'type': 'DEPLOYMENT_FAILURE',
    'value': None,
    'developer_id': None,
    'commit_hash': None,
    'deployment_id': 55870,
    'deployment_failure_id': None
})
new_rows.append({
    'id': max_id + 6,
    'project_id': 2,
    'timestamp': '2025-11-04 01:15:00',
    'type': 'DEPLOYMENT_FAILURE_FIX',
    'value': None,
    'developer_id': None,
    'commit_hash': None,
    'deployment_id': None,
    'deployment_failure_id': max_id + 5
})

# Dec: Add failure for deployment 55880 (2025-12-08 13:50:00)
new_rows.append({
    'id': max_id + 7,
    'project_id': 2,
    'timestamp': '2025-12-08 14:25:00',
    'type': 'DEPLOYMENT_FAILURE',
    'value': None,
    'developer_id': None,
    'commit_hash': None,
    'deployment_id': 55880,
    'deployment_failure_id': None
})
new_rows.append({
    'id': max_id + 8,
    'project_id': 2,
    'timestamp': '2025-12-09 00:40:00',
    'type': 'DEPLOYMENT_FAILURE_FIX',
    'value': None,
    'developer_id': None,
    'commit_hash': None,
    'deployment_id': None,
    'deployment_failure_id': max_id + 7
})

# Add new rows to dataframe
new_df = pd.DataFrame(new_rows)
df = pd.concat([df, new_df], ignore_index=True)

print("After adding new failures, row count:", len(df))

# ============================================================================
# PART 3: VERIFY THE CHANGES
# ============================================================================
print("\n" + "="*60)
print("VERIFICATION - NEW CFR BY MONTH")
print("="*60)

for project_id in [1, 2]:
    print(f"\n--- PROJECT {project_id} ---")
    p_2025 = df[(df['project_id'] == project_id) & (df['timestamp'].str.startswith('2025'))]
    dep = p_2025[p_2025['type'] == 'DEPLOYMENT'].copy()
    dep_fail = p_2025[p_2025['type'] == 'DEPLOYMENT_FAILURE'].copy()
    dep['month'] = pd.to_datetime(dep['timestamp']).dt.to_period('M')
    
    print("Month      Deps  Fails  CFR%")
    print("-" * 35)
    
    for month in sorted(dep['month'].unique()):
        month_deps = dep[dep['month'] == month]
        dep_ids = month_deps['id'].tolist()
        failures_count = dep_fail[dep_fail['deployment_id'].isin(dep_ids)].shape[0]
        total_deps = month_deps.shape[0]
        rate = failures_count / total_deps * 100 if total_deps > 0 else 0
        print(f"{str(month):<10} {total_deps:<5} {failures_count:<6} {rate:.1f}%")

# ============================================================================
# PART 4: SAVE THE MODIFIED DATA
# ============================================================================
df.to_csv('data_observations.csv', sep=';', index=False)
print("\n✓ Changes saved to data_observations.csv")
