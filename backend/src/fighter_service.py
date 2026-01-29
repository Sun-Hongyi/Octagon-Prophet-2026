#Searches for the data of the specific fighters that are going to fight
import json
from typing import Dict, List, Optional

class FighterService:
    """Service for managing fighter statistics database"""
    
    def __init__(self, db_path: str = 'fighter_database.json'):
        """
        Initialize with path to fighter database JSON file
        
        Args:
            db_path: Path to fighter database JSON file
        """
        try:
            with open(db_path, 'r') as f:
                self.fighters = json.load(f)
            print(f"✅ Loaded {len(self.fighters)} fighters from {db_path}")
        except FileNotFoundError:
            print(f"❌ Fighter database not found: {db_path}")
            self.fighters = {}
        except json.JSONDecodeError:
            print(f"❌ Invalid JSON in fighter database: {db_path}")
            self.fighters = {}
    
    def get_fighter(self, name: str) -> Dict:
        """
        Get fighter statistics by name (case-insensitive search)
        
        Args:
            name: Fighter name to search for
            
        Returns:
            Dictionary containing fighter statistics
            
        Raises:
            ValueError: If fighter not found
        """
        # 1. Exact match
        if name in self.fighters:
            return self.fighters[name]
        
        # 2. Case-insensitive exact match
        for fighter_name in self.fighters.keys():
            if fighter_name.lower() == name.lower():
                return self.fighters[fighter_name]
        
        # 3. Partial match (if user types "Conor" instead of "Conor McGregor")
        matches = []
        for fighter_name in self.fighters.keys():
            if name.lower() in fighter_name.lower():
                matches.append(fighter_name)
        
        if len(matches) == 1:
            return self.fighters[matches[0]]
        elif len(matches) > 1:
            # Return the first match with a warning
            print(f"⚠️ Multiple fighters found for '{name}': {matches}")
            return self.fighters[matches[0]]
        
        # 4. Not found
        raise ValueError(f"Fighter not found: '{name}'. Try a different spelling.")
    
    def search_fighters(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Search for fighters by name with pagination
        
        Args:
            query: Search string
            limit: Maximum number of results to return
            
        Returns:
            List of fighter dictionaries with name and stats
        """
        if not query or len(query) < 2:
            return []
        
        query = query.lower()
        results = []
        
        for fighter_name, stats in self.fighters.items():
            if query in fighter_name.lower():
                # Create result with name included
                result = {"name": fighter_name}
                result.update(stats)  # Add all stats
                results.append(result)
                
                if len(results) >= limit:
                    break
        
        # Sort by name length (closest matches first)
        results.sort(key=lambda x: len(x["name"]))
        
        return results
    
    def get_fighter_count(self) -> int:
        """Get total number of fighters in database"""
        return len(self.fighters)
    
    def get_top_strikers(self, limit: int = 10) -> List[Dict]:
        """Get fighters with highest average strikes"""
        fighters_list = [
            {"name": name, **stats} 
            for name, stats in self.fighters.items()
        ]
        fighters_list.sort(
            key=lambda x: x.get("avg_strikes", 0), 
            reverse=True
        )
        return fighters_list[:limit]
    
    def get_top_grapplers(self, limit: int = 10) -> List[Dict]:
        """Get fighters with highest average takedowns"""
        fighters_list = [
            {"name": name, **stats} 
            for name, stats in self.fighters.items()
        ]
        fighters_list.sort(
            key=lambda x: x.get("avg_td", 0), 
            reverse=True
        )
        return fighters_list[:limit]