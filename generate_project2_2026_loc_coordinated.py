"""
Generate coordinated LINES_OF_CODE and LINES_OF_CODE_AI observations for Project 2 in 2026.

CRITICAL: LOC_AI must NEVER exceed LOC on any given day.

Approach: Generate LOC first, then LOC_AI as a percentage of it.

Story:
- H1 (Q1-Q2): High AI reliance - LOC_AI is ~80-85% of total LOC
- H2 (Q3-Q4): Team writes human code while deleting AI code
  - LOC remains positive (human contribution)
  - LOC_AI can be negative (net deletion of AI code)
"""

import csv
import random
from datetime import datetime, timedelta
from calendar import monthrange

random.seed(2026_04)  # New seed

OUTPUT_LOC_FILE = "project2_2026_loc_coordinated.csv"
OUTPUT_LOC_AI_FILE = "project2_2026_loc_ai_coordinated.csv"

# Starting IDs - high range to avoid conflicts
START_ID_LOC = 300000
START_ID_LOC_AI = 350000

# Monthly parameters
# ai_pct: what fraction of new LOC is AI-generated (can be negative for deletions)
# target_loc: target total LOC for the month
MONTHLY_PARAMS = {
    # H1: High AI reliance
    1: {'target_loc': 5500, 'ai_pct': 0.88},   # Jan: very high AI%
    2: {'target_loc': 4600, 'ai_pct': 0.75},   # Feb
    3: {'target_loc': 6400, 'ai_pct': 0.88},   # Mar
    4: {'target_loc': 5700, 'ai_pct': 0.84},   # Apr
    5: {'target_loc': 8600, 'ai_pct': 0.77},   # May
    6: {'target_loc': 7700, 'ai_pct': 0.71},   # Jun
    
    # H2: Human code compensates, AI deletions
    7: {'target_loc': 4000, 'ai_pct': 0.24},   # Jul
    8: {'target_loc': 3500, 'ai_pct': -0.14},  # Aug: negative = deleting AI code
    9: {'target_loc': 2100, 'ai_pct': 0.06},   # Sep
    10: {'target_loc': 3700, 'ai_pct': -0.13}, # Oct: negative
    11: {'target_loc': 3300, 'ai_pct': -0.05}, # Nov: negative
    12: {'target_loc': 3700, 'ai_pct': 0.24},  # Dec
}

def get_workdays_in_month(year, month):
    """Get all workdays (Mon-Fri) in a month."""
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

def generate_coordinated_observations(year):
    """Generate LOC and LOC_AI observations ensuring LOC_AI <= LOC per day."""
    loc_observations = []
    loc_ai_observations = []
    current_id_loc = START_ID_LOC
    current_id_loc_ai = START_ID_LOC_AI
    
    for month in range(1, 13):
        params = MONTHLY_PARAMS[month]
        target_loc = params['target_loc']
        ai_pct = params['ai_pct']
        
        workdays = get_workdays_in_month(year, month)
        num_workdays = len(workdays)
        
        # Distribute LOC across workdays
        loc_per_day = target_loc / num_workdays
        
        for day in workdays:
            # Generate day's total LOC (with variance)
            day_loc = max(10, int(random.gauss(loc_per_day, loc_per_day * 0.4)))
            
            # Calculate day's LOC_AI based on ai_pct
            if ai_pct >= 0:
                # Positive: AI contributes this fraction
                day_loc_ai = int(day_loc * ai_pct * random.uniform(0.8, 1.2))
                day_loc_ai = min(day_loc_ai, day_loc)  # Ensure LOC_AI <= LOC
            else:
                # Negative: AI code being deleted (independent of new LOC)
                # Scale by magnitude of ai_pct
                day_loc_ai = int(day_loc * ai_pct * random.uniform(0.8, 1.2))
            
            # Split into multiple observations per day (realistic granularity)
            num_obs = random.randint(25, 40)
            
            # Generate LOC observations
            remaining_loc = day_loc
            for i in range(num_obs):
                if i == num_obs - 1:
                    obs_loc = remaining_loc  # Last one gets remainder
                else:
                    obs_loc = int(random.gauss(day_loc / num_obs, day_loc / num_obs * 0.5))
                    obs_loc = max(-20, min(obs_loc, remaining_loc))
                    remaining_loc -= obs_loc
                
                entry_time = random_worktime(day)
                loc_observations.append({
                    'id': current_id_loc,
                    'project_id': 2,
                    'type': 'LINES_OF_CODE',
                    'timestamp': entry_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'value': obs_loc,
                    'commit_hash': '',
                    'deployment_id': '',
                    'deployment_failure_id': '',
                    'ai_rework_commit': ''
                })
                current_id_loc += 1
            
            # Generate LOC_AI observations
            remaining_loc_ai = day_loc_ai
            num_ai_obs = random.randint(15, 25)
            for i in range(num_ai_obs):
                if i == num_ai_obs - 1:
                    obs_loc_ai = remaining_loc_ai
                else:
                    obs_loc_ai = int(random.gauss(day_loc_ai / num_ai_obs, abs(day_loc_ai) / num_ai_obs * 0.5))
                    if day_loc_ai >= 0:
                        obs_loc_ai = max(-10, min(obs_loc_ai, remaining_loc_ai))
                    remaining_loc_ai -= obs_loc_ai
                
                entry_time = random_worktime(day)
                loc_ai_observations.append({
                    'id': current_id_loc_ai,
                    'project_id': 2,
                    'type': 'LINES_OF_CODE_AI',
                    'timestamp': entry_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'value': obs_loc_ai,
                    'commit_hash': '',
                    'deployment_id': '',
                    'deployment_failure_id': '',
                    'ai_rework_commit': ''
                })
                current_id_loc_ai += 1
    
    return loc_observations, loc_ai_observations

def main():
    print("Generating coordinated LOC and LOC_AI for Project 2 2026")
    print("=" * 60)
    
    loc_obs, loc_ai_obs = generate_coordinated_observations(2026)
    
    # Sort by timestamp
    loc_obs.sort(key=lambda x: x['timestamp'])
    loc_ai_obs.sort(key=lambda x: x['timestamp'])
    
    print(f"Generated {len(loc_obs)} LOC observations")
    print(f"Generated {len(loc_ai_obs)} LOC_AI observations")
    
    # Write to CSV files
    fieldnames = ['id', 'project_id', 'type', 'timestamp', 'value', 
                  'commit_hash', 'deployment_id', 'deployment_failure_id', 'ai_rework_commit']
    
    with open(OUTPUT_LOC_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=';')
        for obs in loc_obs:
            writer.writerow(obs)
    
    with open(OUTPUT_LOC_AI_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=';')
        for obs in loc_ai_obs:
            writer.writerow(obs)
    
    print(f"\nWritten to {OUTPUT_LOC_FILE} and {OUTPUT_LOC_AI_FILE}")
    
    # Verify no daily violations
    print("\nVerifying daily totals (LOC_AI should never exceed LOC when both positive):")
    from collections import defaultdict
    daily_loc = defaultdict(int)
    daily_loc_ai = defaultdict(int)
    
    for obs in loc_obs:
        day = obs['timestamp'][:10]
        daily_loc[day] += obs['value']
    
    for obs in loc_ai_obs:
        day = obs['timestamp'][:10]
        daily_loc_ai[day] += obs['value']
    
    violations = 0
    for day in sorted(daily_loc.keys()):
        loc = daily_loc[day]
        loc_ai = daily_loc_ai[day]
        if loc > 0 and loc_ai > loc:
            violations += 1
            if violations <= 5:
                print(f"  VIOLATION: {day}: LOC={loc}, LOC_AI={loc_ai}")
    
    if violations == 0:
        print("  No violations found!")
    else:
        print(f"  Found {violations} violations")
    
    # Monthly summary
    print("\nMonthly summary:")
    for month in range(1, 13):
        month_str = f'2026-{month:02d}'
        loc = sum(obs['value'] for obs in loc_obs if obs['timestamp'].startswith(month_str))
        loc_ai = sum(obs['value'] for obs in loc_ai_obs if obs['timestamp'].startswith(month_str))
        ai_pct = (loc_ai / loc * 100) if loc > 0 else 0
        print(f"  {month_str}: LOC={loc:6d}, LOC_AI={loc_ai:6d}, AI%={ai_pct:6.1f}%")

if __name__ == '__main__':
    main()
