"""
Generate 2026 simulated data for Project 2: "AI Adoption Gone Wrong"

Story:
- Q1: Honeymoon period - high AI acceptance, metrics look OK (similar to 2025 baseline)
- Q2: Problems start - high acceptance continues, rework increases, DORA metrics degrade
- Q3: Things get worse - sustained high acceptance, high rework, DORA metrics degrade more  
- Q4: Bad situation - team hasn't learned, productivity is clearly worse than 2025

Contrast with Project 1: 
- Project 1 learned to be selective (acceptance drops, rework drops, DORA improves)
- Project 2 keeps accepting blindly (acceptance stays high, rework high, DORA degrades)
"""

import csv
import random
from datetime import datetime, timedelta
from typing import List, Tuple

# Set seed for reproducibility
random.seed(2026)

# Configuration based on 2025 baseline (Project 1/2 are identical in 2025)
# 2025 baseline: ~103 deployments, ~8-9 deployments/month, ~26 failures (25% CFR), ~3000 commits

# Output file
OUTPUT_FILE = "project2_2026_data.csv"

# Starting ID (use a high range to avoid conflicts after appending)
START_ID = 200000

# 2025 baseline stats (derived from the existing data)
BASELINE_2025 = {
    'deployments_per_month': 8.5,
    'failure_rate': 0.25,  # ~25% CFR
    'commits_per_deployment': 30,  # roughly 3000 commits / 100 deployments
    'mttr_minutes': 600,  # ~10 hours average
    'lead_time_minutes': 4000,  # ~2.8 days (actual 2025 average: 3700-4300 minutes)
}

# Progressive degradation by quarter
# Key story: high AI acceptance → high rework → degraded DORA
DEGRADATION = {
    'Q1': {  # Honeymoon - similar to 2025, slightly optimistic
        'deployment_factor': 1.05,  # slightly more deployments (AI boosting velocity)
        'failure_rate': 0.24,  # similar to 2025 baseline
        'commits_factor': 1.15,  # more code (AI generating lots)
        'mttr_factor': 0.95,  # slightly faster recovery
        'lead_time_factor': 1.0,  # same as 2025 baseline (no improvement yet)
        'ai_acceptance_rate': 0.85,  # high acceptance (excited about AI)
        'ai_rework_rate': 0.12,  # low visible rework (problems hidden)
    },
    'Q2': {  # Problems emerge - technical debt starts to show
        'deployment_factor': 0.80,  # 20% fewer deployments (slowing down)
        'failure_rate': 0.36,  # failure rate increases significantly
        'commits_factor': 0.95,  # slightly fewer productive commits
        'mttr_factor': 1.5,  # 50% longer recovery (unfamiliar code)
        'lead_time_factor': 1.4,  # 40% longer lead time (more review/rework)
        'ai_acceptance_rate': 0.88,  # acceptance stays high
        'ai_rework_rate': 0.28,  # rework becoming visible
    },
    'Q3': {  # Getting worse - team doubles down on AI instead of fixing process
        'deployment_factor': 0.65,  # 35% fewer deployments
        'failure_rate': 0.44,  # high failure rate
        'commits_factor': 0.80,  # fewer commits, more fixing
        'mttr_factor': 2.0,  # 2x longer recovery
        'lead_time_factor': 1.8,  # 80% longer lead time
        'ai_acceptance_rate': 0.91,  # still high acceptance (not learning)
        'ai_rework_rate': 0.38,  # high rework rate
    },
    'Q4': {  # Bad situation persists - clear productivity decline
        'deployment_factor': 0.55,  # 45% fewer deployments
        'failure_rate': 0.50,  # 50% failure rate!
        'commits_factor': 0.70,  # significantly fewer commits
        'mttr_factor': 2.5,  # 2.5x longer recovery
        'lead_time_factor': 2.2,  # 2.2x longer lead time
        'ai_acceptance_rate': 0.92,  # still accepting blindly
        'ai_rework_rate': 0.45,  # very high rework
    },
}

def get_quarter(month: int) -> str:
    """Get quarter string from month."""
    if month <= 3:
        return 'Q1'
    elif month <= 6:
        return 'Q2'
    elif month <= 9:
        return 'Q3'
    else:
        return 'Q4'

def get_workdays_in_month(year: int, month: int) -> List[datetime]:
    """Get list of workdays (Mon-Fri) in a month."""
    workdays = []
    if month == 12:
        next_month = datetime(year + 1, 1, 1)
    else:
        next_month = datetime(year, month + 1, 1)
    
    current = datetime(year, month, 1)
    while current < next_month:
        if current.weekday() < 5:  # Mon-Fri
            workdays.append(current)
        current += timedelta(days=1)
    return workdays

def random_worktime(base_date: datetime) -> datetime:
    """Generate random work time (8am-6pm)."""
    hour = random.randint(8, 17)
    minute = random.randint(0, 59)
    second = random.randint(0, 59)
    return base_date.replace(hour=hour, minute=minute, second=second)

def generate_deployments_and_related(year: int) -> Tuple[List[dict], int]:
    """Generate DEPLOYMENT, DEPLOYMENT_FAILURE, DEPLOYMENT_FAILURE_FIX, COMMIT observations."""
    observations = []
    current_id = START_ID
    deployment_id_start = 100000  # New ID range for Project 2's 2026 deployments
    
    for month in range(1, 13):
        quarter = get_quarter(month)
        params = DEGRADATION[quarter]
        workdays = get_workdays_in_month(year, month)
        
        # Calculate deployments for this month
        base_deployments = BASELINE_2025['deployments_per_month']
        num_deployments = max(3, int(base_deployments * params['deployment_factor'] + random.gauss(0, 1)))
        
        # Select deployment days
        deployment_days = sorted(random.sample(workdays, min(num_deployments, len(workdays))))
        
        for dep_day in deployment_days:
            dep_time = random_worktime(dep_day)
            deployment_id = deployment_id_start
            deployment_id_start += 1
            
            # DEPLOYMENT observation
            observations.append({
                'id': current_id,
                'project_id': 2,
                'type': 'DEPLOYMENT',
                'timestamp': dep_time.strftime('%Y-%m-%d %H:%M:%S'),
                'value': 1,
                'commit_hash': '',
                'deployment_id': '',
                'deployment_failure_id': '',
                'ai_rework_commit': ''
            })
            dep_obs_id = current_id
            current_id += 1
            
            # Generate commits for this deployment (before deployment time)
            base_commits = BASELINE_2025['commits_per_deployment']
            num_commits = max(10, int(base_commits * params['commits_factor'] + random.gauss(0, 5)))
            
            # Lead time: how far back commits happen before deployment
            # The "lead_time_factor" scales the AVERAGE distance back from deployment
            # To achieve target_avg lead time, commits should be centered around that point
            base_lead_time_minutes = BASELINE_2025['lead_time_minutes']  # 4000 min (~2.77 days)
            target_avg_lead_time = base_lead_time_minutes * params['lead_time_factor']
            
            # Add some variance to the target
            target_avg_lead_time = max(1440, target_avg_lead_time + random.gauss(0, 360))  # min 1 day
            
            for i in range(num_commits):
                # Each commit's lead time follows a distribution centered on target_avg
                # Use gaussian with stddev = 40% of mean for realistic spread
                commit_lead_time_minutes = max(60, random.gauss(target_avg_lead_time, target_avg_lead_time * 0.4))
                commit_time = dep_time - timedelta(minutes=commit_lead_time_minutes)
                
                # Determine if this is a rework commit (fixing AI code)
                is_rework = random.random() < params['ai_rework_rate'] * 0.3  # 30% of rework rate shows as distinct commits
                
                observations.append({
                    'id': current_id,
                    'project_id': 2,
                    'type': 'COMMIT',
                    'timestamp': commit_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'value': 1,
                    'commit_hash': f'p2c{current_id:05d}',
                    'deployment_id': dep_obs_id,
                    'deployment_failure_id': '',
                    'ai_rework_commit': '1' if is_rework else ''
                })
                current_id += 1
            
            # Check if deployment fails - use deterministic approach based on index
            # This ensures the failure rate targets are met more consistently
            deployment_index_in_quarter = sum(1 for o in observations if o['type'] == 'DEPLOYMENT' and 
                                              get_quarter(int(o['timestamp'].split('-')[1])) == quarter)
            
            # Calculate expected failures for this point
            expected_failures_so_far = deployment_index_in_quarter * params['failure_rate']
            actual_failures_so_far = sum(1 for o in observations if o['type'] == 'DEPLOYMENT_FAILURE' and 
                                         get_quarter(int(o['timestamp'].split('-')[1])) == quarter)
            
            # Fail if we're behind on the expected failure count (with some randomness)
            should_fail = (actual_failures_so_far < expected_failures_so_far - 0.5) or \
                         (random.random() < params['failure_rate'] and actual_failures_so_far < expected_failures_so_far + 1)
            
            if should_fail:
                # DEPLOYMENT_FAILURE
                failure_time = dep_time + timedelta(minutes=random.randint(5, 60))
                observations.append({
                    'id': current_id,
                    'project_id': 2,
                    'type': 'DEPLOYMENT_FAILURE',
                    'timestamp': failure_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'value': 1,
                    'commit_hash': '',
                    'deployment_id': dep_obs_id,
                    'deployment_failure_id': '',
                    'ai_rework_commit': ''
                })
                failure_obs_id = current_id
                current_id += 1
                
                # DEPLOYMENT_FAILURE_FIX
                base_mttr = BASELINE_2025['mttr_minutes']
                mttr = max(60, int(base_mttr * params['mttr_factor'] + random.gauss(0, 60)))
                fix_time = failure_time + timedelta(minutes=mttr)
                
                observations.append({
                    'id': current_id,
                    'project_id': 2,
                    'type': 'DEPLOYMENT_FAILURE_FIX',
                    'timestamp': fix_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'value': 1,
                    'commit_hash': '',
                    'deployment_id': '',
                    'deployment_failure_id': failure_obs_id,
                    'ai_rework_commit': ''
                })
                current_id += 1
    
    return observations, current_id

def generate_ai_suggestions(year: int, start_id: int) -> Tuple[List[dict], int]:
    """Generate AI_SUGGESTION_RESULT observations (acceptance rate tracking)."""
    observations = []
    current_id = start_id
    
    # Generate ~50-80 AI suggestions per workday
    for month in range(1, 13):
        quarter = get_quarter(month)
        params = DEGRADATION[quarter]
        workdays = get_workdays_in_month(year, month)
        
        for day in workdays:
            # Number of AI suggestions per day (5 developers, ~10-16 suggestions each)
            num_suggestions = random.randint(50, 80)
            
            for _ in range(num_suggestions):
                suggestion_time = random_worktime(day)
                
                # Value: 1 = accepted, 0 = rejected
                accepted = 1 if random.random() < params['ai_acceptance_rate'] else 0
                
                observations.append({
                    'id': current_id,
                    'project_id': 2,
                    'type': 'AI_SUGGESTION_RESULT',
                    'timestamp': suggestion_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'value': accepted,
                    'commit_hash': '',
                    'deployment_id': '',
                    'deployment_failure_id': '',
                    'ai_rework_commit': ''
                })
                current_id += 1
    
    return observations, current_id

def generate_lines_of_code_ai(year: int, start_id: int) -> Tuple[List[dict], int]:
    """Generate LINES_OF_CODE_AI observations."""
    observations = []
    current_id = start_id
    
    # Generate ~10-20 LINES_OF_CODE_AI entries per workday
    for month in range(1, 13):
        quarter = get_quarter(month)
        params = DEGRADATION[quarter]
        workdays = get_workdays_in_month(year, month)
        
        for day in workdays:
            num_entries = random.randint(10, 20)
            
            for _ in range(num_entries):
                entry_time = random_worktime(day)
                
                # Lines of AI code - can be positive or negative (deletions)
                # High acceptance = more AI lines initially
                # But much of it gets deleted/rewritten later
                base_lines = random.randint(-50, 80)
                
                # Later quarters: more deletions of AI code
                if quarter in ['Q3', 'Q4']:
                    base_lines = random.randint(-60, 60)  # More variance, more deletions
                
                observations.append({
                    'id': current_id,
                    'project_id': 2,
                    'type': 'LINES_OF_CODE_AI',
                    'timestamp': entry_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'value': base_lines,
                    'commit_hash': '',
                    'deployment_id': '',
                    'deployment_failure_id': '',
                    'ai_rework_commit': ''
                })
                current_id += 1
    
    return observations, current_id

def main():
    print("Generating Project 2 2026 data: 'AI Adoption Gone Wrong' story")
    print("=" * 60)
    
    all_observations = []
    
    # Generate deployments, failures, fixes, and commits
    print("Generating deployments, commits, failures, and fixes...")
    dep_obs, next_id = generate_deployments_and_related(2026)
    all_observations.extend(dep_obs)
    print(f"  Generated {len(dep_obs)} deployment-related observations")
    
    # Generate AI suggestion results
    print("Generating AI suggestion results...")
    ai_obs, next_id = generate_ai_suggestions(2026, next_id)
    all_observations.extend(ai_obs)
    print(f"  Generated {len(ai_obs)} AI suggestion observations")
    
    # Generate lines of code AI
    print("Generating lines of code AI...")
    loc_obs, next_id = generate_lines_of_code_ai(2026, next_id)
    all_observations.extend(loc_obs)
    print(f"  Generated {len(loc_obs)} LINES_OF_CODE_AI observations")
    
    # Sort by timestamp
    all_observations.sort(key=lambda x: x['timestamp'])
    
    # Write to CSV
    print(f"\nWriting {len(all_observations)} observations to {OUTPUT_FILE}...")
    fieldnames = ['id', 'project_id', 'type', 'timestamp', 'value', 
                  'commit_hash', 'deployment_id', 'deployment_failure_id', 'ai_rework_commit']
    
    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=';')
        # No header - will be appended to existing file
        for obs in all_observations:
            writer.writerow(obs)
    
    print(f"\nDone! Generated data saved to {OUTPUT_FILE}")
    print("\nSummary statistics:")
    
    # Count by type
    type_counts = {}
    for obs in all_observations:
        t = obs['type']
        type_counts[t] = type_counts.get(t, 0) + 1
    
    for t, count in sorted(type_counts.items()):
        print(f"  {t}: {count}")
    
    # Count failures by quarter
    print("\nDeployment failures by quarter:")
    for q in ['Q1', 'Q2', 'Q3', 'Q4']:
        failures = sum(1 for obs in all_observations 
                      if obs['type'] == 'DEPLOYMENT_FAILURE' and 
                      get_quarter(int(obs['timestamp'].split('-')[1])) == q)
        deploys = sum(1 for obs in all_observations 
                     if obs['type'] == 'DEPLOYMENT' and 
                     get_quarter(int(obs['timestamp'].split('-')[1])) == q)
        rate = failures / deploys if deploys > 0 else 0
        print(f"  {q}: {failures}/{deploys} = {rate:.1%} CFR")
    
    print("\n" + "=" * 60)
    print("To append this data to data_observations.csv, run:")
    print(f'  type {OUTPUT_FILE} >> data_observations.csv')
    print("\nThen re-run data_ingestor.py to reload the database.")

if __name__ == '__main__':
    main()
