# tests/test_fighter_service.py
import sys
import os
import json
import tempfile
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.fighter_service import FighterService

def test_fighter_service():
    """Test fighter database service"""
    # Create a temporary test database
    test_db = {
        "Conor McGregor": {"avg_kd": 1.2, "avg_strikes": 45},
        "Khabib Nurmagomedov": {"avg_kd": 0.3, "avg_strikes": 22}
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(test_db, f)
        temp_path = f.name
    
    try:
        service = FighterService(temp_path)
        
        # Test exact match
        stats = service.get_fighter("Conor McGregor")
        assert stats["avg_kd"] == 1.2
        
        # Test case-insensitive
        stats = service.get_fighter("conor mcgregor")
        assert stats["avg_kd"] == 1.2
        
        # Test search
        results = service.search_fighters("Conor", limit=5)
        assert len(results) == 1
        assert results[0]["name"] == "Conor McGregor"
        
        # Test fighter count
        assert service.get_fighter_count() == 2
        
    finally:
        os.unlink(temp_path)
