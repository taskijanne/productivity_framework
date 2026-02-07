"""
Script to summarize data from data_observations.csv
Groups by project_id, observation type, and month, showing count, mean, min, max, stdev
"""

import pandas as pd
import numpy as np

# Read the CSV file (semicolon-delimited)
df = pd.read_csv('data_observations.csv', delimiter=';')

# Parse timestamp and extract year-month
df['timestamp'] = pd.to_datetime(df['timestamp'])
df['year_month'] = df['timestamp'].dt.to_period('M')

# Group by project_id, type, and month, calculate statistics on the 'value' column
summary = df.groupby(['project_id', 'type', 'year_month'])['value'].agg([
    ('count', 'count'),
    ('mean', 'mean'),
    ('min', 'min'),
    ('max', 'max'),
    ('stdev', lambda x: x.std() if len(x) > 1 else 0)
]).reset_index()

# Sort by project_id, type, and year_month
summary = summary.sort_values(['project_id', 'type', 'year_month'])

# Print header
print("=" * 110)
print("DATA OBSERVATIONS SUMMARY")
print("Grouped by Project ID, Observation Type, and Month")
print("=" * 110)

current_project = None
current_type = None

for _, row in summary.iterrows():
    # Print project header when project changes
    if current_project != row['project_id']:
        current_project = row['project_id']
        current_type = None
        print(f"\n{'═' * 110}")
        print(f"PROJECT {int(current_project)}")
        print(f"{'═' * 110}")
    
    # Print type header when type changes
    if current_type != row['type']:
        current_type = row['type']
        print(f"\n  {current_type}")
        print(f"  {'─' * 106}")
        print(f"  {'Month':<12} {'Count':>10} {'Mean':>12} {'Min':>12} {'Max':>12} {'Stdev':>12}")
        print(f"  {'─' * 12} {'─' * 10} {'─' * 12} {'─' * 12} {'─' * 12} {'─' * 12}")
    
    # Format the values
    month = str(row['year_month'])
    count = int(row['count'])
    mean_val = f"{row['mean']:.4f}" if pd.notna(row['mean']) else "N/A"
    min_val = f"{row['min']:.4f}" if pd.notna(row['min']) else "N/A"
    max_val = f"{row['max']:.4f}" if pd.notna(row['max']) else "N/A"
    stdev_val = f"{row['stdev']:.4f}" if pd.notna(row['stdev']) else "N/A"
    
    print(f"  {month:<12} {count:>10} {mean_val:>12} {min_val:>12} {max_val:>12} {stdev_val:>12}")

# Print totals
print(f"\n{'=' * 110}")
print("OVERALL TOTALS")
print(f"{'=' * 110}")

totals = df.groupby('project_id').size().reset_index(name='total_observations')
for _, row in totals.iterrows():
    print(f"Project {int(row['project_id'])}: {row['total_observations']:,} observations")

print(f"\nGrand Total: {len(df):,} observations")
print(f"Date Range: {df['timestamp'].min()} to {df['timestamp'].max()}")
print("=" * 110)
