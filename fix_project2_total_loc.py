"""
Fix Project 2 Total LOC data for 2026.
Target: 
- 2026 total LOC should be higher than 2025 (~70,000-75,000 vs 64,500)
- Monthly LOC should be relatively stable or slightly increasing (AI generates more code)
- No dramatic drops in later months

Strategy:
- Adjust existing LINES_OF_CODE values to achieve target
- Then regenerate LINES_OF_CODE_AI to maintain 60%->75% ratio
"""

import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Target monthly LOC for 2026 (should be ~10-15% higher than 2025 average of 5375)
# Story: AI helps produce more code, especially mid-year when they're going "all in"
TARGET_MONTHLY_LOC = {
    '01': 5800,   # Slightly above 2025 baseline
    '02': 6100,   # Ramping up
    '03': 6400,   # AI adoption increasing
    '04': 6800,   # Strong AI usage
    '05': 7200,   # Peak productivity (before problems surface)
    '06': 7000,   # Still high
    '07': 6600,   # Slight decline as issues emerge
    '08': 6200,   # More issues, but still producing
    '09': 5900,   # Declining
    '10': 5600,   # Further decline
    '11': 5400,   # Struggling
    '12': 5200,   # Year end - still producing but at lower rate
}
# Total: ~74,200 (15% more than 2025's 64,500)

# AI LOC percentages (from previous fix)
TARGET_AI_PERCENTAGES = {
    '01': 0.60, '02': 0.61, '03': 0.63, '04': 0.65,
    '05': 0.67, '06': 0.69, '07': 0.70, '08': 0.71,
    '09': 0.72, '10': 0.73, '11': 0.74, '12': 0.75,
}

def main():
    conn = sqlite3.connect('productivity_framework.db')
    cursor = conn.cursor()
    
    # Step 1: Get current LOC data structure
    query = '''
    SELECT strftime('%m', timestamp) as month, 
           SUM(value) as current_loc,
           COUNT(*) as entries,
           MIN(timestamp) as min_ts,
           MAX(timestamp) as max_ts
    FROM observations 
    WHERE project_id = 2 AND timestamp >= '2026-01-01' 
    AND type = 'LINES_OF_CODE'
    GROUP BY month
    ORDER BY month
    '''
    df = pd.read_sql_query(query, conn)
    print("=== Current Total LOC by Month ===")
    print(df.to_string())
    print(f"Current 2026 Total: {df['current_loc'].sum():.0f}")
    
    # Step 2: Calculate scaling factors
    df['target_loc'] = df['month'].map(TARGET_MONTHLY_LOC)
    df['scale_factor'] = df['target_loc'] / df['current_loc']
    
    print("\n=== Target LOC and Scale Factors ===")
    print(df[['month', 'current_loc', 'target_loc', 'scale_factor']].to_string())
    print(f"Target 2026 Total: {df['target_loc'].sum():.0f}")
    
    # Step 3: Update LINES_OF_CODE values by scaling
    for _, row in df.iterrows():
        month = row['month']
        scale = row['scale_factor']
        
        # Update all LOC entries for this month
        cursor.execute('''
            UPDATE observations 
            SET value = ROUND(value * ?, 0)
            WHERE project_id = 2 
            AND strftime('%m', timestamp) = ?
            AND timestamp >= '2026-01-01'
            AND type = 'LINES_OF_CODE'
        ''', (scale, month))
        
    print(f"\n=== Updated LINES_OF_CODE entries ===")
    
    # Step 4: Delete and regenerate LINES_OF_CODE_AI to maintain target percentages
    cursor.execute('''
        DELETE FROM observations 
        WHERE project_id = 2 
        AND timestamp >= '2026-01-01' 
        AND type = 'LINES_OF_CODE_AI'
    ''')
    print(f"Deleted existing LINES_OF_CODE_AI entries")
    
    # Get new LOC totals after scaling
    query_new = '''
    SELECT strftime('%m', timestamp) as month, 
           SUM(value) as total_loc,
           MIN(timestamp) as min_ts,
           MAX(timestamp) as max_ts
    FROM observations 
    WHERE project_id = 2 AND timestamp >= '2026-01-01' 
    AND type = 'LINES_OF_CODE'
    GROUP BY month
    ORDER BY month
    '''
    df_new = pd.read_sql_query(query_new, conn)
    
    # Step 5: Generate new AI LOC entries
    new_entries = []
    
    for _, row in df_new.iterrows():
        month = row['month']
        total_loc = row['total_loc']
        target_ai_pct = TARGET_AI_PERCENTAGES[month]
        target_ai_loc = int(total_loc * target_ai_pct)
        
        min_ts = datetime.strptime(row['min_ts'], '%Y-%m-%d %H:%M:%S')
        max_ts = datetime.strptime(row['max_ts'], '%Y-%m-%d %H:%M:%S')
        
        # Create entries
        num_entries = random.randint(420, 480)
        remaining = target_ai_loc
        values = []
        
        for i in range(num_entries - 1):
            if remaining <= 0:
                values.append(random.randint(5, 15))
            else:
                avg_needed = remaining / (num_entries - i)
                val = max(1, int(avg_needed + random.gauss(0, avg_needed * 0.3)))
                val = min(val, remaining, 50)
                values.append(val)
                remaining -= val
        
        if remaining > 0:
            values.append(remaining)
        else:
            values.append(random.randint(5, 15))
        
        time_range = (max_ts - min_ts).total_seconds()
        
        for val in values:
            random_seconds = random.random() * time_range
            ts = min_ts + timedelta(seconds=random_seconds)
            ts_str = ts.strftime('%Y-%m-%d %H:%M:%S')
            new_entries.append((2, 'LINES_OF_CODE_AI', ts_str, float(val), None, None, None, None))
    
    cursor.executemany('''
        INSERT INTO observations (project_id, type, timestamp, value, commit_hash, deployment_id, deployment_failure_id, ai_rework_commit)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', new_entries)
    
    print(f"Inserted {len(new_entries)} new LINES_OF_CODE_AI entries")
    
    # Step 6: Verify results
    query_verify = '''
    SELECT 
        l.month,
        l.total_loc,
        a.ai_loc,
        ROUND(a.ai_loc * 100.0 / l.total_loc, 1) as ai_pct
    FROM (
        SELECT strftime('%m', timestamp) as month, SUM(value) as total_loc
        FROM observations 
        WHERE project_id = 2 AND timestamp >= '2026-01-01' AND type = 'LINES_OF_CODE'
        GROUP BY month
    ) l
    JOIN (
        SELECT strftime('%m', timestamp) as month, SUM(value) as ai_loc
        FROM observations 
        WHERE project_id = 2 AND timestamp >= '2026-01-01' AND type = 'LINES_OF_CODE_AI'
        GROUP BY month
    ) a ON l.month = a.month
    ORDER BY l.month
    '''
    df_verify = pd.read_sql_query(query_verify, conn)
    
    print("\n=== Final Verification ===")
    print(df_verify.to_string())
    print(f"\n2026 Total LOC: {df_verify['total_loc'].sum():.0f}")
    print(f"2026 Total AI LOC: {df_verify['ai_loc'].sum():.0f}")
    
    # Compare with 2025
    query_2025 = '''
    SELECT SUM(value) as total FROM observations 
    WHERE project_id = 2 AND timestamp >= '2025-01-01' AND timestamp < '2026-01-01' 
    AND type = 'LINES_OF_CODE'
    '''
    df_2025 = pd.read_sql_query(query_2025, conn)
    print(f"2025 Total LOC: {df_2025['total'].iloc[0]:.0f}")
    
    conn.commit()
    conn.close()
    print("\n=== Done! ===")

if __name__ == '__main__':
    main()
