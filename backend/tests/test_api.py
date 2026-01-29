from fastapi.testclient import TestClient
import sys
import os

# Add backend to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from api import app

client = TestClient(app)

def test_home_endpoint():
    """Test the root endpoint returns API info"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "UFC Predictor" in data["message"]
    assert "endpoints" in data

def test_predict_endpoint_valid():
    """Test prediction with valid stats"""
    response = client.get("/predict?kd=2&strikes=35&takedowns=1")
    assert response.status_code == 200
    data = response.json()
    assert "red_win_probability" in data
    assert "predicted_winner" in data
    assert "confidence" in data
    # Probability should be between 0 and 1
    assert "0%" in data["red_win_probability"] or "100%" in data["red_win_probability"]

def test_predict_endpoint_missing_params():
    """Test prediction with missing parameters"""
    response = client.get("/predict?kd=2")  # Missing strikes and takedowns
    assert response.status_code == 422  # FastAPI validation error

def test_search_fighters():
    """Test fighter search endpoint"""
    response = client.get("/search/conor")
    assert response.status_code == 200
    data = response.json()
    assert "query" in data
    assert "fighters" in data
    assert isinstance(data["fighters"], list)

def test_search_fighters_short_query():
    """Test search with query too short"""
    response = client.get("/search/a")  # Too short (needs 2 chars)
    assert response.status_code == 400