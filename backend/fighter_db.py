import pandas as pd
import json
from collections import defaultdict

def build_fighter_db_for_your_model():
    """Build fighter database with features YOUR model expects"""
    
    print("📊 Building database for YOUR 7-feature model...")
    
    # Load your fights CSV
    df = pd.read_csv('../data/data/Fights.csv')
    
    # Track fighter career
    fighters = defaultdict(lambda: {
        'total_fights': 0,
        'wins': 0,
        'losses': 0,
        'draws': 0,
        'kd_total': 0,
        'str_total': 0,
        'sub_total': 0,  # NEW: submissions
        'td_total': 0,
        'fight_history': []  # Track recent fights for streak
    })
    
    # Process each fight
    for idx, row in df.iterrows():
        f1 = row['Fighter_1']
        f2 = row['Fighter_2']
        result = row['Result_1']  # 'W', 'L', or 'D'
        
        # Update fighter 1
        fighters[f1]['total_fights'] += 1
        fighters[f1]['kd_total'] += row.get('KD_1', 0)
        fighters[f1]['str_total'] += row.get('STR_1', 0)
        fighters[f1]['sub_total'] += row.get('SUB_1', 0)
        fighters[f1]['td_total'] += row.get('TD_1', 0)
        fighters[f1]['fight_history'].append(result)
        
        if result == 'W':
            fighters[f1]['wins'] += 1
        elif result == 'L':
            fighters[f1]['losses'] += 1
        else:
            fighters[f1]['draws'] += 1
        
        # Update fighter 2  
        fighters[f2]['total_fights'] += 1
        fighters[f2]['kd_total'] += row.get('KD_2', 0)
        fighters[f2]['str_total'] += row.get('STR_2', 0)
        fighters[f2]['sub_total'] += row.get('SUB_2', 0)
        fighters[f2]['td_total'] += row.get('TD_2', 0)
        fighters[f2]['fight_history'].append('W' if result == 'L' else 'L' if result == 'W' else 'D')
        
        if result == 'W':
            fighters[f2]['losses'] += 1
        elif result == 'L':
            fighters[f2]['wins'] += 1
        else:
            fighters[f2]['draws'] += 1
    
    # Calculate final stats
    fighter_db = {}
    for name, stats in fighters.items():
        total = stats['total_fights']
        wins = stats['wins']
        
        # Calculate win streak (last 3 fights)
        recent = stats['fight_history'][-3:] if len(stats['fight_history']) >= 3 else stats['fight_history']
        win_streak = sum(1 for r in recent if r == 'W')
        
        fighter_db[name] = {
            'win_rate': wins / total if total > 0 else 0.5,
            'total_fights': total,
            'win_streak': win_streak,
            'avg_kd': stats['kd_total'] / total if total > 0 else 0,
            'avg_strikes': stats['str_total'] / total if total > 0 else 0,
            'avg_sub': stats['sub_total'] / total if total > 0 else 0,  # NEW
            'avg_td': stats['td_total'] / total if total > 0 else 0
        }
    
    print(f"✅ Built database with {len(fighter_db)} fighters")
    return fighter_db

# Build and save
FIGHTER_DB = build_fighter_db_for_your_model()
with open('fighter_database_your_model.json', 'w') as f:
    json.dump(FIGHTER_DB, f, indent=2)
