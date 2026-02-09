"""
Fix Project 2 AI LOC data for 2026.
Target: AI LOC should go from 60% in January to 75% in December (steady increase).

Strategy:
- Keep existing LINES_OF_CODE entries (total LOC)
- Delete existing LINES_OF_CODE_AI entries
- Regenerate AI LOC entries to achieve target percentages
"""

import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Target AI LOC percentages by month (60% -> 75%)
TARGET_AI_PERCENTAGES = {
    '01': 0.60,
    '02': 0.61,
    '03': 0.63,
    '04': 0.65,
    '05': 0.67,
    '06': 0.69,
    '07': 0.70,
    '08': 0.71,
    '09': 0.72,
    '10': 0.73,
    '11': 0.74,
    '12': 0.75,
}

def main():
    conn = sqlite3.connect('productivity_framework.db')
    cursor = conn.cursor()
    
    # Step 1: Get existing LINES_OF_CODE totals per month
    query = '''
    SELECT strftime('%m', timestamp) as month, 
           SUM(value) as total_loc,
           COUNT(*) as entries,
           MIN(timestamp) as min_ts,
           MAX(timestamp) as max_ts
    FROM observations 
    WHERE project_id = 2 AND timestamp >= '2026-01-01' 
    AND type = 'LINES_OF_CODE'
    GROUP BY month
    ORDER BY month
    '''
    df_loc = pd.read_sql_query(query, conn)
    print("=== Current Total LOC by Month ===")
    print(df_loc.to_string())
    
    # Step 2: Calculate target AI LOC per month
    df_loc['target_ai_pct'] = df_loc['month'].map(TARGET_AI_PERCENTAGES)
    df_loc['target_ai_loc'] = (df_loc['total_loc'] * df_loc['target_ai_pct']).round().astype(int)
    
    print("\n=== Target AI LOC by Month ===")
    print(df_loc[['month', 'total_loc', 'target_ai_pct', 'target_ai_loc']].to_string())
    
    # Step 3: Delete existing LINES_OF_CODE_AI entries for Project 2 in 2026
    cursor.execute('''
        DELETE FROM observations 
        WHERE project_id = 2 
        AND timestamp >= '2026-01-01' 
        AND type = 'LINES_OF_CODE_AI'
    ''')
    deleted = cursor.rowcount
    print(f"\n=== Deleted {deleted} existing LINES_OF_CODE_AI entries ===")
    
    # Step 4: Generate new AI LOC entries
    # We'll create entries distributed throughout each month
    new_entries = []
    
    for _, row in df_loc.iterrows():
        month = row['month']
        target_ai_loc = row['target_ai_loc']
        min_ts = datetime.strptime(row['min_ts'], '%Y-%m-%d %H:%M:%S')
        max_ts = datetime.strptime(row['max_ts'], '%Y-%m-%d %H:%M:%S')
        
        # Create ~400-500 entries per month (similar to original)
        num_entries = random.randint(420, 480)
        
        # Generate random values that sum to target
        # Use positive values only (5-25 lines per entry typical)
        remaining = target_ai_loc
        values = []
        
        for i in range(num_entries - 1):
            if remaining <= 0:
                values.append(random.randint(5, 15))  # Still add some entries
            else:
                # Average needed per remaining entry
                avg_needed = remaining / (num_entries - i)
                # Add some variance
                val = max(1, int(avg_needed + random.gauss(0, avg_needed * 0.3)))
                val = min(val, remaining, 50)  # Cap at 50 lines per entry
                values.append(val)
                remaining -= val
        
        # Last entry gets the remainder (or a reasonable value)
        if remaining > 0:
            values.append(remaining)
        else:
            values.append(random.randint(5, 15))
        
        # Generate timestamps distributed throughout the month
        time_range = (max_ts - min_ts).total_seconds()
        
        for val in values:
            # Random timestamp within the month
            random_seconds = random.random() * time_range
            ts = min_ts + timedelta(seconds=random_seconds)
            ts_str = ts.strftime('%Y-%m-%d %H:%M:%S')
            
            new_entries.append((2, 'LINES_OF_CODE_AI', ts_str, float(val), None, None, None, None))
    
    # Step 5: Insert new entries
    cursor.executemany('''
        INSERT INTO observations (project_id, type, timestamp, value, commit_hash, deployment_id, deployment_failure_id, ai_rework_commit)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', new_entries)
    
    print(f"\n=== Inserted {len(new_entries)} new LINES_OF_CODE_AI entries ===")
    
    # Step 6: Verify results
    query_verify = '''
    SELECT strftime('%m', timestamp) as month, 
           SUM(value) as ai_loc,
           COUNT(*) as entries
    FROM observations 
    WHERE project_id = 2 AND timestamp >= '2026-01-01' 
    AND type = 'LINES_OF_CODE_AI'
    GROUP BY month
    ORDER BY month
    '''
    df_verify = pd.read_sql_query(query_verify, conn)
    
    # Join with total LOC to calculate actual percentage
    df_result = df_loc[['month', 'total_loc', 'target_ai_pct']].merge(df_verify, on='month')
    df_result['actual_ai_pct'] = df_result['ai_loc'] / df_result['total_loc']
    
    print("\n=== Verification: Actual AI LOC Percentages ===")
    print(df_result.to_string())
    
    conn.commit()
    conn.close()
    print("\n=== Done! ===")

if __name__ == '__main__':
    main()
