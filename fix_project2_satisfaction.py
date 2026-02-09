"""
Fix Project 2 Satisfaction data for 2026.
Target trajectory (honeymoon then cliff):
- Q1 (Jan-Mar): Very High (~8.5-9.0) - "AI is amazing!"
- Q2 (Apr-Jun): Still Good (~7.5-8.0) - Issues are "growing pains"
- Q3 (Jul-Sep): Drops (~6.5-7.0) - Frustration sets in
- Q4 (Oct-Dec): Crashes (~5.0-6.5) - Burnout
"""

import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Target satisfaction averages by month
TARGET_SATISFACTION = {
    '01': 8.6,   # Q1 - Very high
    '02': 8.8,   # Q1 - Peak excitement
    '03': 8.5,   # Q1 - Still very high
    '04': 8.0,   # Q2 - Good
    '05': 7.7,   # Q2 - Starting to notice issues
    '06': 7.4,   # Q2 - "Growing pains"
    '07': 7.0,   # Q3 - Drop begins
    '08': 6.7,   # Q3 - Frustration
    '09': 6.5,   # Q3 - More frustration
    '10': 6.0,   # Q4 - Crash begins
    '11': 5.5,   # Q4 - Low morale
    '12': 5.2,   # Q4 - Burnout
}

def main():
    conn = sqlite3.connect('productivity_framework.db')
    cursor = conn.cursor()
    
    # Step 1: Get current satisfaction data structure
    query = '''
    SELECT strftime('%m', timestamp) as month, 
           COUNT(*) as entries,
           AVG(value) as current_avg,
           MIN(timestamp) as min_ts,
           MAX(timestamp) as max_ts
    FROM observations 
    WHERE project_id = 2 AND timestamp >= '2026-01-01' 
    AND type = 'SATISFACTION'
    GROUP BY month
    ORDER BY month
    '''
    df = pd.read_sql_query(query, conn)
    print("=== Current Satisfaction by Month ===")
    print(df[['month', 'entries', 'current_avg']].to_string())
    
    # Step 2: Delete existing satisfaction entries for Project 2 in 2026
    cursor.execute('''
        DELETE FROM observations 
        WHERE project_id = 2 
        AND timestamp >= '2026-01-01' 
        AND type = 'SATISFACTION'
    ''')
    deleted = cursor.rowcount
    print(f"\nDeleted {deleted} existing SATISFACTION entries")
    
    # Step 3: Generate new satisfaction entries
    # 10 entries per month (same as original), with values around target
    new_entries = []
    
    for _, row in df.iterrows():
        month = row['month']
        target_avg = TARGET_SATISFACTION[month]
        num_entries = int(row['entries'])  # Keep same count
        
        min_ts = datetime.strptime(row['min_ts'], '%Y-%m-%d %H:%M:%S')
        max_ts = datetime.strptime(row['max_ts'], '%Y-%m-%d %H:%M:%S')
        
        # Generate values around target (satisfaction is 1-10 scale)
        # Use normal distribution with small std dev
        values = []
        for _ in range(num_entries):
            val = random.gauss(target_avg, 0.5)  # std dev of 0.5
            val = max(1.0, min(10.0, round(val, 2)))  # Clamp to 1-10
            values.append(val)
        
        # Adjust to hit target average more precisely
        current_avg = sum(values) / len(values)
        adjustment = target_avg - current_avg
        values = [max(1.0, min(10.0, round(v + adjustment, 2))) for v in values]
        
        # Generate timestamps
        time_range = (max_ts - min_ts).total_seconds()
        
        for val in values:
            random_seconds = random.random() * time_range
            ts = min_ts + timedelta(seconds=random_seconds)
            ts_str = ts.strftime('%Y-%m-%d %H:%M:%S')
            new_entries.append((2, 'SATISFACTION', ts_str, val, None, None, None, None))
    
    # Step 4: Insert new entries
    cursor.executemany('''
        INSERT INTO observations (project_id, type, timestamp, value, commit_hash, deployment_id, deployment_failure_id, ai_rework_commit)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', new_entries)
    
    print(f"Inserted {len(new_entries)} new SATISFACTION entries")
    
    # Step 5: Verify results
    query_verify = '''
    SELECT strftime('%m', timestamp) as month, 
           COUNT(*) as entries,
           ROUND(AVG(value), 2) as avg_satisfaction,
           ROUND(MIN(value), 2) as min_val,
           ROUND(MAX(value), 2) as max_val
    FROM observations 
    WHERE project_id = 2 AND timestamp >= '2026-01-01' 
    AND type = 'SATISFACTION'
    GROUP BY month
    ORDER BY month
    '''
    df_verify = pd.read_sql_query(query_verify, conn)
    
    print("\n=== New Satisfaction by Month ===")
    print(df_verify.to_string())
    
    # Show trajectory
    print("\n=== Satisfaction Trajectory ===")
    for _, row in df_verify.iterrows():
        month_name = datetime(2026, int(row['month']), 1).strftime('%b')
        avg = row['avg_satisfaction']
        bar = '█' * int(avg)
        print(f"{month_name}: {avg:.1f} {bar}")
    
    conn.commit()
    conn.close()
    print("\n=== Done! ===")

if __name__ == '__main__':
    main()
