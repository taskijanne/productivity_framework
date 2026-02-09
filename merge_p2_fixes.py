"""
Merge Project 2 fixes from special backup into virgin data_observations.csv.
Preserves original row order and only changes Project 2 rows.
Uses vectorized operations for speed.
"""
import pandas as pd

print('Reading files...')
# Read virgin (from git checkout)
virgin = pd.read_csv('data_observations.csv', delimiter=';', dtype=str)
# Read fixed version with P2 changes
fixed = pd.read_csv('data_observations_with_p2_fixes.csv', delimiter=';', dtype=str)

print(f'Virgin rows: {len(virgin)}')
print(f'Fixed rows: {len(fixed)}')

# Strategy: Keep virgin structure, but for rows where id matches a P2 id in fixed,
# update all columns except id

# Get the set of P2 ids from fixed
fixed_p2 = fixed[fixed['project_id'] == '2'].copy()
p2_ids = set(fixed_p2['id'].values)
print(f'Project 2 rows to replace: {len(p2_ids)}')

# Create lookup from id to index in fixed_p2
fixed_p2 = fixed_p2.set_index('id')

# Find which rows in virgin need updating (P2 rows)
mask = virgin['id'].isin(p2_ids)
print(f'Rows to update in virgin: {mask.sum()}')

# For P2 rows, update values from fixed_p2
# Get the ids that need updating
ids_to_update = virgin.loc[mask, 'id'].values

# Update each column (except id) using loc with the fixed values
cols = [c for c in virgin.columns if c != 'id']
for col in cols:
    # Map: for each id in ids_to_update, get the value from fixed_p2
    new_values = [fixed_p2.loc[id_val, col] for id_val in ids_to_update]
    virgin.loc[mask, col] = new_values

print('Replacement complete')

# Save
virgin.to_csv('data_observations.csv', sep=';', index=False)
print('Saved data_observations.csv')
