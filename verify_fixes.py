"""Quick verification of data fixes"""
import sqlite3
import pandas as pd

conn = sqlite3.connect('productivity_framework.db')

# 1. Verify MTTR still works
print('=== MTTR Verification ===')
q = '''SELECT 
    strftime('%Y', f.timestamp) as year, f.project_id,
    COUNT(*) as failures,
    ROUND(AVG((julianday(fx.timestamp) - julianday(f.timestamp)) * 24 * 60), 1) as avg_mttr_min
FROM observations f
JOIN observations fx ON f.id = fx.deployment_failure_id
WHERE f.type = 'DEPLOYMENT_FAILURE' AND fx.type = 'DEPLOYMENT_FAILURE_FIX'
GROUP BY year, f.project_id'''
print(pd.read_sql_query(q, conn).to_string())

# 2. Verify Project 2 2026 LOC
print('\n=== Project 2 2026 LOC ===')
q = '''SELECT 
    (SELECT SUM(value) FROM observations WHERE project_id=2 AND strftime('%Y',timestamp)='2026' AND type='LINES_OF_CODE_AI') as ai_loc,
    (SELECT SUM(value) FROM observations WHERE project_id=2 AND strftime('%Y',timestamp)='2026' AND type='LINES_OF_CODE') as total_loc'''
df = pd.read_sql_query(q, conn)
print(f"AI LOC: {df['ai_loc'][0]:.0f}, Total LOC: {df['total_loc'][0]:.0f}, Ratio: {df['ai_loc'][0]/df['total_loc'][0]*100:.1f}%")

# 3. Verify Satisfaction trajectory
print('\n=== Project 2 2026 Satisfaction ===')
q = '''SELECT strftime('%m', timestamp) as month, ROUND(AVG(value), 2) as avg_sat
FROM observations 
WHERE project_id = 2 AND strftime('%Y', timestamp) = '2026' AND type = 'SATISFACTION'
GROUP BY month ORDER BY month'''
print(pd.read_sql_query(q, conn).to_string())

conn.close()
print('\n✓ All verifications complete!')
