import pandas as pd
import json
from collections import defaultdict

def build_fighter_db_for_REBALANCED_model():
    """Build fighter database with features YOUR REBALANCED model expects"""
    
    print("📊 Building database for REBALANCED 7-feature model...")
    
    # Load your fights CSV
    df = pd.read_csv('../data/data/Fights.csv')
    
    # Track fighter career - ADD MORE STATS
    fighters = defaultdict(lambda: {
        'total_fights': 0,
        'wins': 0,
        'losses': 0,
        'draws': 0,
        
        # FIGHT STATISTICS (MOST IMPORTANT)
        'kd_total': 0,
        'str_total': 0,
        'sub_total': 0,
        'td_total': 0,
        
        # NEW: Track for AVERAGES
        'kd_history': [],
        'str_history': [],
        'sub_history': [],
        'td_history': [],
        
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
        
        # Store individual fight stats for averaging
        fighters[f1]['kd_history'].append(row.get('KD_1', 0))
        fighters[f1]['str_history'].append(row.get('STR_1', 0))
        fighters[f1]['sub_history'].append(row.get('SUB_1', 0))
        fighters[f1]['td_history'].append(row.get('TD_1', 0))
        
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
        
        fighters[f2]['kd_history'].append(row.get('KD_2', 0))
        fighters[f2]['str_history'].append(row.get('STR_2', 0))
        fighters[f2]['sub_history'].append(row.get('SUB_2', 0))
        fighters[f2]['td_history'].append(row.get('TD_2', 0))
        
        fighters[f2]['fight_history'].append('W' if result == 'L' else 'L' if result == 'W' else 'D')
        
        if result == 'W':
            fighters[f2]['losses'] += 1
        elif result == 'L':
            fighters[f2]['wins'] += 1
        else:
            fighters[f2]['draws'] += 1
    
    # Calculate final stats - MATCH YOUR REBALANCED MODEL
    fighter_db = {}
    for name, stats in fighters.items():
        total = stats['total_fights']
        wins = stats['wins']
        
        # Calculate win streak (last 3 fights)
        recent = stats['fight_history'][-3:] if len(stats['fight_history']) >= 3 else stats['fight_history']
        win_streak = sum(1 for r in recent if r == 'W')
        
        # FIGHT STATISTICS (MOST IMPORTANT for rebalanced model)
        avg_strikes = stats['str_total'] / total if total > 0 else 0
        avg_knockdowns = stats['kd_total'] / total if total > 0 else 0
        avg_takedowns = stats['td_total'] / total if total > 0 else 0
        avg_submissions = stats['sub_total'] / total if total > 0 else 0
        
        # YOUR REBALANCED MODEL EXPECTS THESE EXACT KEYS:
        fighter_db[name] = {
            # FIGHT STATS (PRIORITY 1 - 60% weight)
            'avg_strikes': avg_strikes,
            'avg_knockdowns': avg_knockdowns,
            'avg_takedowns': avg_takedowns,
            'avg_submissions': avg_submissions,
            
            # RECENT FORM (PRIORITY 2 - 30% weight)
            'win_streak': win_streak,
            
            # CAREER (PRIORITY 3 - 10% weight)
            'win_rate': wins / total if total > 0 else 0.5,
            'total_fights': total,
            
            # Additional stats that might be useful
            'recent_avg_strikes': sum(stats['str_history'][-5:]) / min(5, len(stats['str_history'])) if stats['str_history'] else 0,
            'recent_avg_knockdowns': sum(stats['kd_history'][-5:]) / min(5, len(stats['kd_history'])) if stats['kd_history'] else 0,
            'finish_rate': (sum(1 for kd in stats['kd_history'] if kd > 0) + 
                           sum(1 for sub in stats['sub_history'] if sub > 0)) / total if total > 0 else 0
        }
    
    print(f"✅ Built REBALANCED database with {len(fighter_db)} fighters")
    print(f"🎯 Keys match predict_ufc_fight_REBALANCED() function requirements")
    
    # Verify keys match your model
    sample_fighter = next(iter(fighter_db.values()))
    print(f"📋 Sample fighter keys: {list(sample_fighter.keys())}")
    
    return fighter_db

# Build and save with REBALANCED name
FIGHTER_DB_REBALANCED = build_fighter_db_for_REBALANCED_model()
with open('fighter_database_REBALANCED.json', 'w') as f:
    json.dump(FIGHTER_DB_REBALANCED, f, indent=2)

print(f"\n💾 Saved to: fighter_database_REBALANCED.json")
