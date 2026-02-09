"""Full metrics comparison between Project 1 and Project 2 for 2026"""
import sqlite3
import pandas as pd

conn = sqlite3.connect('productivity_framework.db')

print('='*70)
print('PROJECT 2 vs PROJECT 1 - 2026 METRICS COMPARISON')
print('='*70)

def query(sql):
    return pd.read_sql_query(sql, conn)

# 1. Deployment Frequency
print('\n1. DEPLOYMENT FREQUENCY')
for pid in [1, 2]:
    deps = query(f"""
        SELECT strftime('%m', timestamp) as month, COUNT(*) as cnt
        FROM observations 
        WHERE project_id={pid} AND type='DEPLOYMENT' AND strftime('%Y', timestamp)='2026'
        GROUP BY month ORDER BY month
    """)
    print(f"   P{pid}: {list(deps['cnt'])} = {deps['cnt'].sum()} total, {deps['cnt'].mean():.1f}/mo")

# 2. Change Failure Rate
print('\n2. CHANGE FAILURE RATE')
for pid in [1, 2]:
    deps = query(f"SELECT COUNT(*) as c FROM observations WHERE project_id={pid} AND type='DEPLOYMENT' AND strftime('%Y', timestamp)='2026'")['c'][0]
    fails = query(f"SELECT COUNT(*) as c FROM observations WHERE project_id={pid} AND type='DEPLOYMENT_FAILURE' AND strftime('%Y', timestamp)='2026'")['c'][0]
    print(f"   P{pid}: {fails}/{deps} = {fails/deps*100:.1f}%")

# 3. Lead Time for Changes - calculated from COMMIT timestamps linked to deployments
print('\n3. LEAD TIME FOR CHANGES (hours) - see API for calculated values')
print("   (Calculated dynamically from commit->deployment linkage)")

# 4. MTTR (avg minutes) - calculated from DEPLOYMENT_FAILURE_FIX value field
print('\n4. MEAN TIME TO RECOVER (minutes)')
for pid in [1, 2]:
    # The value field stores recovery time in minutes
    result = query(f"""
        SELECT AVG(CAST(value AS FLOAT)) as avg_min
        FROM observations 
        WHERE project_id={pid} AND type='DEPLOYMENT_FAILURE_FIX' AND strftime('%Y', timestamp)='2026'
    """)
    mttr = result['avg_min'][0]
    if mttr and mttr > 1:
        print(f"   P{pid}: {mttr:.0f} min")
    else:
        # Count fixes and calculate from failure-to-fix timestamps
        fixes = query(f"""
            SELECT COUNT(*) as c FROM observations 
            WHERE project_id={pid} AND type='DEPLOYMENT_FAILURE_FIX' AND strftime('%Y', timestamp)='2026'
        """)['c'][0]
        print(f"   P{pid}: {fixes} fixes (see API for calculated MTTR)")

# 5. AI Acceptance Rate (value = 1.0 for accepted, 0.0 for rejected)
print('\n5. AI ACCEPTANCE RATE')
for pid in [1, 2]:
    accepted = query(f"SELECT COUNT(*) as c FROM observations WHERE project_id={pid} AND type='AI_SUGGESTION_RESULT' AND strftime('%Y', timestamp)='2026' AND CAST(value AS FLOAT)=1.0")['c'][0]
    rejected = query(f"SELECT COUNT(*) as c FROM observations WHERE project_id={pid} AND type='AI_SUGGESTION_RESULT' AND strftime('%Y', timestamp)='2026' AND CAST(value AS FLOAT)=0.0")['c'][0]
    total = accepted + rejected
    if total > 0:
        print(f"   P{pid}: {accepted}/{total} = {accepted/total*100:.1f}%")
    else:
        print(f"   P{pid}: No AI_SUGGESTION_RESULT data")

# 6. AI Rework Rate (commits with ai_rework_commit set)
print('\n6. AI REWORK RATE')
for pid in [1, 2]:
    # All commits that are AI-assisted (have value containing 'AI' or ai_rework_commit indicates origin)
    ai_commits = query(f"SELECT COUNT(*) as c FROM observations WHERE project_id={pid} AND type='COMMIT' AND strftime('%Y', timestamp)='2026'")['c'][0]
    reworks = query(f"SELECT COUNT(*) as c FROM observations WHERE project_id={pid} AND type='COMMIT' AND strftime('%Y', timestamp)='2026' AND ai_rework_commit IS NOT NULL")['c'][0]
    if ai_commits > 0:
        print(f"   P{pid}: {reworks} rework commits / {ai_commits} total commits = {reworks/ai_commits*100:.1f}%")
    else:
        print(f"   P{pid}: No commit data")

# 7. Lines of Code
print('\n7. LINES OF CODE (AI %)')
for pid in [1, 2]:
    total_loc = query(f"SELECT SUM(CAST(value AS INT)) as total FROM observations WHERE project_id={pid} AND type='LINES_OF_CODE' AND strftime('%Y', timestamp)='2026'")['total'][0]
    ai_loc = query(f"SELECT SUM(CAST(value AS INT)) as total FROM observations WHERE project_id={pid} AND type='LINES_OF_CODE_AI' AND strftime('%Y', timestamp)='2026'")['total'][0]
    print(f"   P{pid}: {ai_loc/1000:.0f}k/{total_loc/1000:.0f}k = {ai_loc/total_loc*100:.0f}% AI")

# 8. Developer Satisfaction
print('\n8. DEVELOPER SATISFACTION')
for pid in [1, 2]:
    sat = query(f"""
        SELECT strftime('%m', timestamp) as month, AVG(CAST(value AS FLOAT)) as avg_sat
        FROM observations 
        WHERE project_id={pid} AND type='SATISFACTION' AND strftime('%Y', timestamp)='2026'
        GROUP BY month ORDER BY month
    """)
    print(f"   P{pid}: {[round(x,1) for x in sat['avg_sat']]} avg={sat['avg_sat'].mean():.1f}")

print('\n' + '='*70)
print('SUMMARY: Project 1 = Happy Case | Project 2 = Unhappy Case')
print('='*70)
conn.close()
