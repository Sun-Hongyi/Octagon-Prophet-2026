# tests/test_predictor.py
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

import numpy as np
from src.predictor import PredictorService

# Mock model and scaler for testing
class MockModel:
    def predict_proba(self, X):
        # Always predict 75% for Red
        return np.array([[0.25, 0.75]])

class MockScaler:
    def transform(self, X):
        return X

def test_predictor_service():
    """Test the predictor service"""
    model = MockModel()
    scaler = MockScaler()
    predictor = PredictorService(model, scaler)
    
    # Test prediction
    prob = predictor.predict_from_stats(kd=2, strikes=35, takedowns=1)
    assert 0 <= prob <= 1
    assert abs(prob - 0.75) < 0.01  # Should match mock
    
    # Test confidence calculation
    assert predictor.calculate_confidence(0.9) == "High"
    assert predictor.calculate_confidence(0.65) == "Medium"
    assert predictor.calculate_confidence(0.51) == "Low"