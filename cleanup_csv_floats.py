"""
Clean up CSV file by removing .0 float suffixes from integer columns.
This fixes the data ingestion errors.
"""

import pandas as pd
import numpy as np

print("Reading data_observations.csv...")
# Read all columns as strings to preserve formatting
df = pd.read_csv('data_observations.csv', delimiter=';', dtype=str)
print(f"Total rows: {len(df)}")

# Columns that should be integers (but may have .0 due to NaN handling)
int_columns = ['id', 'project_id', 'deployment_id', 'deployment_failure_id', 'developer_id', 'ai_rework_commit']

for col in int_columns:
    if col in df.columns:
        # Remove trailing .0 suffix if present (e.g., "60761.0" -> "60761")
        def clean_float_str(x):
            if pd.isna(x) or x == '' or x == 'nan':
                return ''
            s = str(x)
            if s.endswith('.0'):
                return s[:-2]
            return s
        df[col] = df[col].apply(clean_float_str)

# Also ensure value column doesn't have unnecessary decimals for integer values
# But keep decimals for satisfaction scores

# Save back
print("Saving cleaned CSV...")
df.to_csv('data_observations.csv', sep=';', index=False)
print("Done!")

# Verify
print("\nVerification:")
df2 = pd.read_csv('data_observations.csv', delimiter=';', dtype=str)
fixes = df2[df2['type'] == 'DEPLOYMENT_FAILURE_FIX'].head(3)
print(fixes[['id', 'deployment_failure_id']].to_string())
