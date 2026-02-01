"""
Generate SATISFACTION observations for Project 2 in 2026.

Pattern: Bi-weekly surveys from 5 developers (same as 2025 and Project 1)

Story for Project 2:
- Initial spike: Excitement about AI tools (similar to Project 1)
- Gradual decline: Frustration as AI code causes problems
- Curve similar to Project 1, but different underlying reasons:
  - Project 1: Disciplined team, slightly bored not writing code
  - Project 2: Frustrated team, dealing with AI-caused problems

2025 baseline: ~7.5-8.4
Project 1 2026: 8.1 → 7.0 (decline due to less creative work)
Project 2 2026: Should follow similar pattern, maybe slightly lower in H2
"""

import csv
import random
from datetime import datetime, timedelta
from calendar import monthrange

random.seed(2026_03)  # Different seed

OUTPUT_FILE = "project2_2026_satisfaction.csv"
START_ID = 400000  # High range to avoid conflicts

# 5 developers
NUM_DEVELOPERS = 5

# Monthly satisfaction targets (similar curve to Project 1)
# Start high (excitement), decline (frustration with AI problems)
MONTHLY_SATISFACTION = {
    1: {'mean': 8.2, 'std': 0.5},   # Jan: Initial excitement about AI
    2: {'mean': 8.3, 'std': 0.5},   # Feb: Peak excitement
    3: {'mean': 8.0, 'std': 0.5},   # Mar: Still optimistic
    4: {'mean': 7.8, 'std': 0.6},   # Apr: Starting to notice issues
    5: {'mean': 7.5, 'std': 0.6},   # May: Problems emerging
    6: {'mean': 7.2, 'std': 0.6},   # Jun: Frustration building
    7: {'mean': 7.0, 'std': 0.7},   # Jul: Dealing with AI debt
    8: {'mean': 6.8, 'std': 0.7},   # Aug: Low point
    9: {'mean': 6.6, 'std': 0.7},   # Sep: Continued frustration
    10: {'mean': 6.5, 'std': 0.7},  # Oct: Morale low
    11: {'mean': 6.6, 'std': 0.7},  # Nov: Slight stabilization
    12: {'mean': 6.5, 'std': 0.7},  # Dec: Still struggling
}

def get_survey_days(year, month):
    """Get bi-weekly survey days (1st and 3rd Monday of month)."""
    survey_days = []
    _, num_days = monthrange(year, month)
    
    monday_count = 0
    for day in range(1, num_days + 1):
        dt = datetime(year, month, day)
        if dt.weekday() == 0:  # Monday
            monday_count += 1
            if monday_count in [1, 3]:  # 1st and 3rd Monday
                survey_days.append(dt)
    
    # Some months might only have 2 survey days, some might have 3
    return survey_days

def generate_satisfaction_observations(year):
    """Generate satisfaction observations for the year."""
    observations = []
    current_id = START_ID
    
    for month in range(1, 13):
        survey_days = get_survey_days(year, month)
        params = MONTHLY_SATISFACTION[month]
        
        for survey_day in survey_days:
            # All 5 developers submit on survey day
            for dev in range(NUM_DEVELOPERS):
                # Generate satisfaction score
                score = random.gauss(params['mean'], params['std'])
                # Clamp to reasonable range (1-10)
                score = max(1.0, min(10.0, score))
                score = round(score, 1)
                
                # Random time during work hours
                hour = random.randint(9, 16)
                minute = random.randint(0, 59)
                timestamp = survey_day.replace(hour=hour, minute=minute, second=0)
                
                observations.append({
                    'id': current_id,
                    'project_id': 2,
                    'type': 'SATISFACTION',
                    'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                    'value': score,
                    'commit_hash': '',
                    'deployment_id': '',
                    'deployment_failure_id': '',
                    'ai_rework_commit': ''
                })
                current_id += 1
    
    return observations

def main():
    print("Generating Project 2 2026 SATISFACTION data")
    print("=" * 60)
    
    observations = generate_satisfaction_observations(2026)
    
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
                    if o['timestamp'].startswith('2026-%02d' % month)]
        if month_obs:
            scores = [float(o['value']) for o in month_obs]
            avg = sum(scores) / len(scores)
            print('2026-%02d: %2d obs, avg=%.2f (target=%.1f)' % (month, len(month_obs), avg, MONTHLY_SATISFACTION[month]['mean']))

if __name__ == '__main__':
    main()
