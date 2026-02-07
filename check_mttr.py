import pandas as pd

df = pd.read_csv('data_observations.csv', delimiter=';')
p1_2025 = df[(df['project_id'] == 1) & (df['timestamp'].str.startswith('2025'))]

dep_fail = p1_2025[p1_2025['type'] == 'DEPLOYMENT_FAILURE'].copy()
dep_fix = p1_2025[p1_2025['type'] == 'DEPLOYMENT_FAILURE_FIX'].copy()

print('=== MAY, JUNE, AUGUST FAILURE/FIX PAIRS (Project 1) ===')
print()

for month_name, month_num in [('May', 5), ('June', 6), ('August', 8)]:
    print(f'--- {month_name} ---')
    month_fixes = dep_fix[pd.to_datetime(dep_fix['timestamp']).dt.month == month_num]
    for _, fix in month_fixes.iterrows():
        fail_id = fix['deployment_failure_id']
        fail_match = dep_fail[dep_fail['id'] == fail_id]
        if not fail_match.empty:
            fail_row = fail_match.iloc[0]
            fail_time = pd.to_datetime(fail_row['timestamp'])
            fix_time = pd.to_datetime(fix['timestamp'])
            minutes = (fix_time - fail_time).total_seconds() / 60
            print(f"  Failure ID {int(fail_id)}: {fail_row['timestamp']}")
            print(f"  Fix ID {int(fix['id'])}: {fix['timestamp']}")
            print(f"  MTTR: {minutes:.0f} min = {minutes/60:.1f} hrs")
            print()
