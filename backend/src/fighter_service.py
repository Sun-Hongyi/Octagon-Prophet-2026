# src/fighter_service.py
import json
import pandas as pd
from typing import Dict, List

class FighterService:
    """Fighter lookup service for REBALANCED UFC JSON data"""
    
    def __init__(self, json_path: str = 'fighter_database_REBALANCED.json'):
        print("📊 Loading REBALANCED fighter database from JSON...")
        
        # Load REBALANCED UFC JSON data
        with open(json_path, 'r') as f:
            fighters_dict = json.load(f)
        
        # Convert to the format your REBALANCED model expects
        self.fighters = self._create_fighter_dict(fighters_dict)
        print(f"✅ Loaded {len(self.fighters)} fighters from REBALANCED JSON dataset")
        print(f"🎯 Model type: REBALANCED (fight stats emphasis)")
    
    def _create_fighter_dict(self, fighters_dict: Dict) -> Dict:
        """Create fighter dictionary from REBALANCED JSON"""
        fighters = {}
        
        # Convert from REBALANCED JSON structure to what PredictorService expects
        for fighter_name, stats in fighters_dict.items():
            # REBALANCED JSON has: avg_strikes, avg_knockdowns, avg_takedowns, avg_submissions
            # Create a fighter entry for REBALANCED model
            fighters[fighter_name] = {
                'id': fighter_name,  # Use name as ID
                'name': fighter_name,
                
                # FIGHT STATISTICS (MOST IMPORTANT - PRIORITY 1)
                'avg_strikes': stats.get('avg_strikes', 0),
                'avg_knockdowns': stats.get('avg_knockdowns', 0),
                'avg_takedowns': stats.get('avg_takedowns', 0),
                'avg_submissions': stats.get('avg_submissions', 0),
                
                # RECENT FORM (PRIORITY 2)
                'win_streak': stats.get('win_streak', 0),
                
                # CAREER STATS (LEAST IMPORTANT - PRIORITY 3)
                'win_rate': stats.get('win_rate', 0.5),
                'total_fights': stats.get('total_fights', 0),
                
                # Additional metrics from new JSON
                'recent_avg_strikes': stats.get('recent_avg_strikes', 0),
                'recent_avg_knockdowns': stats.get('recent_avg_knockdowns', 0),
                'finish_rate': stats.get('finish_rate', 0)
            }
        
        # Print sample fighter to verify
        sample_name = list(fighters.keys())[0]
        print(f"📋 Sample fighter ({sample_name}):")
        print(f"   • Fight Stats: {fighters[sample_name]['avg_strikes']:.1f} strikes, "
              f"{fighters[sample_name]['avg_knockdowns']:.1f} KDs")
        print(f"   • Recent: {fighters[sample_name]['win_streak']}-fight streak")
        print(f"   • Career: {fighters[sample_name]['win_rate']*100:.1f}% win rate")
        
        return fighters
    
    def get_fighter(self, name: str) -> Dict:
        """Find fighter by name (case-insensitive) - UPDATED for rebalanced"""
        name_lower = name.strip().lower()
        
        exact_matches = []
        partial_matches = []
        
        # Search through all fighters
        for fighter_name, fighter in self.fighters.items():
            fighter_lower = fighter_name.lower()
            
            # Check for exact match
            if fighter_lower == name_lower:
                exact_matches.append((fighter_name, fighter))
            
            # Check for partial match
            elif name_lower in fighter_lower:
                partial_matches.append((fighter_name, fighter))
        
        # Return exact match if found
        if exact_matches:
            fighter = exact_matches[0][1]
            print(f"🔍 Found: {fighter['name']} "
                  f"({fighter['avg_strikes']:.1f} avg strikes, "
                  f"{fighter['win_rate']*100:.1f}% win rate)")
            return fighter
        
        # Handle partial matches
        if partial_matches:
            # If only one match, return it
            if len(partial_matches) == 1:
                fighter = partial_matches[0][1]
                print(f"🔍 Found (partial): {fighter['name']}")
                return fighter
            
            # If multiple matches, try to find best one
            for match_name, match_fighter in partial_matches:
                if match_name.lower().startswith(name_lower):
                    print(f"🔍 Found (best match): {match_fighter['name']}")
                    return match_fighter
            
            # Otherwise return first match
            fighter = partial_matches[0][1]
            print(f"🔍 Found (first match): {fighter['name']}")
            return fighter
        
        # No matches found - show suggestions
        suggestions = []
        for fighter_name in self.fighters.keys():
            if name_lower in fighter_name.lower():
                suggestions.append(fighter_name)
        
        if suggestions:
            raise ValueError(f"Did you mean: {', '.join(suggestions[:3])}?")
        
        raise ValueError(f"Fighter '{name}' not found. Try: {list(self.fighters.keys())[:5]}")
    
    def search_fighters(self, query: str, limit: int = 10) -> List[Dict]:
        """Search fighters by name"""
        if len(query) < 2:
            return []
        
        query_lower = query.lower()
        results = []
        
        for fighter_name, fighter in self.fighters.items():
            if query_lower in fighter_name.lower():
                results.append(fighter)
                if len(results) >= limit:
                    break
        
        return results
    
    def get_fighter_stats_for_model(self, name: str) -> Dict:
        """Get fighter stats in EXACT format required by REBALANCED model"""
        fighter = self.get_fighter(name)
        
        # Return in EXACT format that predict_ufc_fight_REBALANCED() expects
        return {
            'avg_strikes': fighter['avg_strikes'],
            'avg_knockdowns': fighter['avg_knockdowns'],
            'avg_takedowns': fighter['avg_takedowns'],
            'avg_submissions': fighter['avg_submissions'],
            'win_streak': fighter['win_streak'],
            'win_rate': fighter['win_rate'],
            'total_fights': fighter['total_fights']
        }
