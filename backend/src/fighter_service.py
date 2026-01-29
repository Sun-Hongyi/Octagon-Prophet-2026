# src/fighter_service.py
import json
import pandas as pd
from typing import Dict, List

class FighterService:
    """Fighter lookup service for YOUR UFC JSON data"""
    
    def __init__(self, json_path: str = 'fighter_database_your_model.json'):
        print("📊 Loading fighter database from your JSON...")
        
        # Load YOUR UFC JSON data
        with open(json_path, 'r') as f:
            fighters_dict = json.load(f)
        
        # Convert to the format your model expects
        self.fighters = self._create_fighter_dict(fighters_dict)
        print(f"✅ Loaded {len(self.fighters)} fighters from your JSON dataset")
    
    def _create_fighter_dict(self, fighters_dict: Dict) -> Dict:
        """Create fighter dictionary from your JSON"""
        fighters = {}
        
        # Convert from your JSON structure to what PredictorService expects
        for fighter_name, stats in fighters_dict.items():
            # Your JSON has: win_rate, total_fights, win_streak, avg_kd, etc.
            # Create a fighter entry
            fighters[fighter_name] = {
                'id': fighter_name,  # Use name as ID since JSON doesn't have IDs
                'name': fighter_name,
                'win_rate': stats.get('win_rate', 0.5),
                'total_fights': stats.get('total_fights', 0),
                'win_streak': stats.get('win_streak', 0),
                'avg_kd': stats.get('avg_kd', 0),
                'avg_strikes': stats.get('avg_strikes', 0),
                'avg_sub': stats.get('avg_sub', 0),
                'avg_td': stats.get('avg_td', 0)
            }
        
        return fighters
    
    def get_fighter(self, name: str) -> Dict:
        """Find fighter by name (case-insensitive)"""
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
            return exact_matches[0][1]
        
        # Handle partial matches
        if partial_matches:
            # If only one match, return it
            if len(partial_matches) == 1:
                return partial_matches[0][1]
            
            # If multiple matches, try to find best one
            for match_name, match_fighter in partial_matches:
                if match_name.lower().startswith(name_lower):
                    return match_fighter
            
            # Otherwise return first match
            return partial_matches[0][1]
        
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
