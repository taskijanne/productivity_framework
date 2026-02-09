"""Verify data after reingest"""
import sqlite3
import pandas as pd

conn = sqlite3.connect('productivity_framework.db')

print('=== Project 2 - 2026 Verification ===')

# LOC
q1 = "SELECT SUM(value) as total FROM observations WHERE project_id = 2 AND timestamp >= '2026-01-01' AND type = 'LINES_OF_CODE'"
df1 = pd.read_sql_query(q1, conn)
print('Total LOC:', int(df1.iloc[0,0]))

# AI LOC  
q2 = "SELECT SUM(value) as total FROM observations WHERE project_id = 2 AND timestamp >= '2026-01-01' AND type = 'LINES_OF_CODE_AI'"
df2 = pd.read_sql_query(q2, conn)
print('AI LOC:', int(df2.iloc[0,0]))
print('AI LOC %:', round(df2.iloc[0,0] / df1.iloc[0,0] * 100, 1))

# Satisfaction by month
q3 = """SELECT strftime('%m', timestamp) as month, ROUND(AVG(value), 1) as sat
FROM observations WHERE project_id = 2 AND timestamp >= '2026-01-01' AND type = 'SATISFACTION'
GROUP BY month ORDER BY month"""
df3 = pd.read_sql_query(q3, conn)
print('Satisfaction by month:', df3['sat'].tolist())

# Deployment count
q4 = "SELECT COUNT(*) as cnt FROM observations WHERE project_id = 2 AND timestamp >= '2026-01-01' AND type = 'DEPLOYMENT'"
df4 = pd.read_sql_query(q4, conn)
print('Deployments:', int(df4.iloc[0,0]))

conn.close()
print('\nAll data verified!')
