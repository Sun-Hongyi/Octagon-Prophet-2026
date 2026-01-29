import pandas as pd
import json
import os

# Load your fights data
print("📂 Loading fight data...")
fights_path = '../data/raw_total_fight_data.csv'
if not os.path.exists(fights_path):
    print(f"❌ File not found: {fights_path}")
    exit()

fights = pd.read_csv(fights_path, sep=';')
print(f"✅ Loaded {len(fights)} fights")

# Function to extract number from "X of Y" format
def extract_number(val, position=0):
    """Extract first number from 'X of Y' format"""
    try:
        if pd.isna(val):
            return 0
        # Handle cases like "41 of 103", "2", "0"
        if ' of ' in str(val):
            return float(str(val).split(' of ')[position])
        else:
            return float(val)
    except:
        return 0

# Dictionary to store all fighter stats
fighter_stats = {}

print("🔢 Processing fights...")
for idx, row in fights.iterrows():
    if idx % 500 == 0:
        print(f"  Processed {idx}/{len(fights)} fights...")
    
    red_name = str(row['R_fighter']).strip()
    blue_name = str(row['B_fighter']).strip()
    
    # Extract ALL stats properly
    # Knockdowns (direct numbers)
    red_kd = float(row['R_KD']) if not pd.isna(row['R_KD']) else 0
    blue_kd = float(row['B_KD']) if not pd.isna(row['B_KD']) else 0
    
    # Takedowns (from "X of Y" format)
    red_td_landed = extract_number(row['R_TD'], 0)
    blue_td_landed = extract_number(row['B_TD'], 0)
    
    # Significant strikes (from "X of Y" format)
    red_strikes = extract_number(row['R_SIG_STR.'], 0)
    blue_strikes = extract_number(row['B_SIG_STR.'], 0)
    
    # Add to fighter stats
    for name, kd, td, strikes in [
        (red_name, red_kd, red_td_landed, red_strikes),
        (blue_name, blue_kd, blue_td_landed, blue_strikes)
    ]:
        if name not in fighter_stats:
            fighter_stats[name] = {
                "kd": [],      # Knockdowns
                "td": [],      # Takedowns landed
                "strikes": [], # Significant strikes landed
                "fights": 0    # Number of fights
            }
        
        fighter_stats[name]["kd"].append(kd)
        fighter_stats[name]["td"].append(td)
        fighter_stats[name]["strikes"].append(strikes)
        fighter_stats[name]["fights"] += 1

print(f"📊 Collected stats for {len(fighter_stats)} fighters")

# Calculate averages
fighter_averages = {}
print("📈 Calculating averages...")
for name, stats in fighter_stats.items():
    num_fights = stats["fights"]
    if num_fights > 0:
        fighter_averages[name] = {
            "avg_kd": sum(stats["kd"]) / num_fights,
            "avg_td": sum(stats["td"]) / num_fights,
            "avg_strikes": sum(stats["strikes"]) / num_fights,
            "total_fights": num_fights,
            "total_kd": sum(stats["kd"]),
            "total_td": sum(stats["td"]),
            "total_strikes": sum(stats["strikes"])
        }
    else:
        fighter_averages[name] = {
            "avg_kd": 0,
            "avg_td": 0,
            "avg_strikes": 0,
            "total_fights": 0,
            "total_kd": 0,
            "total_td": 0,
            "total_strikes": 0
        }

# Save to JSON
output_path = 'fighter_database_detailed.json'
with open(output_path, 'w') as f:
    json.dump(fighter_averages, f, indent=2)

print(f"✅ Saved detailed database with {len(fighter_averages)} fighters to {output_path}")

# Show sample
print("\n📋 Sample fighters:")
sample_fighters = list(fighter_averages.keys())[:5]
for name in sample_fighters:
    stats = fighter_averages[name]
    print(f"  {name}:")
    print(f"    Fights: {stats['total_fights']}")
    print(f"    Avg KD: {stats['avg_kd']:.2f}")
    print(f"    Avg TD: {stats['avg_td']:.2f}")
    print(f"    Avg Strikes: {stats['avg_strikes']:.1f}")