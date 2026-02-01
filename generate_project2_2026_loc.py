"""
Generate LINES_OF_CODE observations for Project 2 in 2026.

Story:
- H1 (Q1-Q2): High AI reliance - LOC_AI is ~85-90% of total LOC
- H2 (Q3-Q4): Team realizes problems, writes more human code, AI contribution drops

Existing LOC_AI data for Project 2 2026:
- Q1: 13906 LOC_AI
- Q2: 16847 LOC_AI  
- Q3: 592 LOC_AI (near zero - lots of deletions)
- Q4: 253 LOC_AI (near zero)

We need to generate LOC such that:
- H1: LOC ≈ LOC_AI / 0.85 (AI is ~85% of total)
- H2: LOC includes significant human-written code to compensate for AI deletions
"""

import csv
import random
from datetime import datetime, timedelta

random.seed(2026_02)  # Different seed to avoid correlation

OUTPUT_FILE = "project2_2026_loc.csv"

# Starting ID - use high range to avoid conflicts
START_ID = 300000

# Target values based on existing LOC_AI and desired AI%
# Q1-Q2: AI is ~85% of total, so LOC = LOC_AI / 0.85
# Q3-Q4: Human code compensates, AI% drops to ~10-20%

MONTHLY_TARGETS = {
    # H1: High AI reliance (LOC close to LOC_AI, AI ~85%)
    1: {'loc_ai': 4838, 'target_ai_pct': 0.88},   # Jan: very high AI%
    2: {'loc_ai': 3454, 'target_ai_pct': 0.85},   # Feb
    3: {'loc_ai': 5614, 'target_ai_pct': 0.82},   # Mar: starting to see issues
    4: {'loc_ai': 4805, 'target_ai_pct': 0.80},   # Apr
    5: {'loc_ai': 6596, 'target_ai_pct': 0.78},   # May
    6: {'loc_ai': 5446, 'target_ai_pct': 0.75},   # Jun: problems visible
    
    # H2: Team compensates with human code (AI% drops significantly)
    # LOC_AI is near zero, but team still produces LOC through human effort
    7: {'loc_ai': 966, 'target_ai_pct': 0.25},    # Jul: human code takes over
    8: {'loc_ai': -496, 'target_ai_pct': 0.0},    # Aug: negative AI, all human
    9: {'loc_ai': 122, 'target_ai_pct': 0.05},    # Sep
    10: {'loc_ai': -472, 'target_ai_pct': 0.0},   # Oct: negative AI, all human
    11: {'loc_ai': -161, 'target_ai_pct': 0.0},   # Nov: negative AI
    12: {'loc_ai': 886, 'target_ai_pct': 0.20},   # Dec: slight recovery
}

# 2025 baseline: ~5000-6000 LOC/month
BASELINE_LOC_PER_MONTH = 5500

def get_workdays_in_month(year, month):
    """Get all workdays (Mon-Fri) in a month."""
    from calendar import monthrange
    _, num_days = monthrange(year, month)
    workdays = []
    for day in range(1, num_days + 1):
        dt = datetime(year, month, day)
        if dt.weekday() < 5:  # Mon-Fri
            workdays.append(dt)
    return workdays

def random_worktime(day):
    """Generate a random work timestamp on a given day."""
    hour = random.randint(8, 17)
    minute = random.randint(0, 59)
    second = random.randint(0, 59)
    return day.replace(hour=hour, minute=minute, second=second)

def generate_loc_observations(year):
    """Generate LINES_OF_CODE observations for each month."""
    observations = []
    current_id = START_ID
    
    for month in range(1, 13):
        targets = MONTHLY_TARGETS[month]
        loc_ai = targets['loc_ai']
        ai_pct = targets['target_ai_pct']
        
        # Calculate target LOC
        if ai_pct > 0 and loc_ai > 0:
            # LOC = LOC_AI / AI_PCT
            target_loc = int(loc_ai / ai_pct)
        else:
            # For months with zero/negative AI, use baseline with some reduction
            # (productivity is down in H2 due to fixing issues)
            if month >= 7:
                # H2: reduced productivity but human code compensates
                target_loc = int(BASELINE_LOC_PER_MONTH * 0.7)  # 70% of baseline
            else:
                target_loc = BASELINE_LOC_PER_MONTH
        
        # Add some variance
        target_loc = max(2000, int(target_loc + random.gauss(0, 500)))
        
        workdays = get_workdays_in_month(year, month)
        
        # Distribute LOC across workdays
        # Similar pattern to Project 1: many small observations
        num_obs = random.randint(650, 750)  # Similar to P1's ~700-750 obs/month
        
        # Calculate per-observation average
        avg_per_obs = target_loc / num_obs
        
        for _ in range(num_obs):
            day = random.choice(workdays)
            entry_time = random_worktime(day)
            
            # Individual LOC values with variance
            # Can be negative (deletions) but mostly positive
            value = int(random.gauss(avg_per_obs, abs(avg_per_obs) * 0.8))
            
            observations.append({
                'id': current_id,
                'project_id': 2,
                'type': 'LINES_OF_CODE',
                'timestamp': entry_time.strftime('%Y-%m-%d %H:%M:%S'),
                'value': value,
                'commit_hash': '',
                'deployment_id': '',
                'deployment_failure_id': '',
                'ai_rework_commit': ''
            })
            current_id += 1
    
    return observations

def main():
    print("Generating Project 2 2026 LINES_OF_CODE data")
    print("=" * 60)
    
    observations = generate_loc_observations(2026)
    
    # Sort by timestamp
    observations.sort(key=lambda x: x['timestamp'])
    
    print(f"Generated {len(observations)} observations")
    
    # Write to CSV (no header - will be appended)
    fieldnames = ['id', 'project_id', 'type', 'timestamp', 'value', 
                  'commit_hash', 'deployment_id', 'deployment_failure_id', 'ai_rework_commit']
    
    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=';')
        for obs in observations:
            writer.writerow(obs)
    
    print(f"Written to {OUTPUT_FILE}")
    
    # Print summary
    print("\nMonthly summary:")
    for month in range(1, 13):
        month_obs = [o for o in observations 
                    if o['timestamp'].startswith(f'2026-{month:02d}')]
        total = sum(int(o['value']) for o in month_obs)
        ai_data = MONTHLY_TARGETS[month]
        actual_ai_pct = (ai_data['loc_ai'] / total * 100) if total > 0 else 0
        quarter = f"Q{(month-1)//3 + 1}"
        print(f"{quarter} 2026-{month:02d}: LOC={total:6d}, LOC_AI={ai_data['loc_ai']:6d}, AI%={actual_ai_pct:5.1f}%")

if __name__ == '__main__':
    main()
