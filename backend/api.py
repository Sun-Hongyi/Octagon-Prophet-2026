# api.py - CLEAN VERSION (NO DEBUG)
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware  
import joblib
import warnings
import pandas as pd
import sys
import os

# Suppress scikit-learn version warnings
from sklearn.exceptions import InconsistentVersionWarning
warnings.filterwarnings("ignore", category=InconsistentVersionWarning)

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.predictor import PredictorService
from src.fighter_service import FighterService

app = FastAPI(
    title="UFC Predictor API", 
    version="1.0",
    description="API for predicting UFC fights"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load model
model = joblib.load('models/ufc_predictor.joblib')
predictor = PredictorService(model)

# Load fighter database
fighter_service = FighterService('fighter_database_your_model.json')

@app.get("/")
def home():
    return {
        "message": "UFC Predictor API 🥊",
        "version": "1.0",
        "endpoints": {
            "GET /": "This page",
            "GET /predict": "Predict with raw features",
            "GET /predict-fight": "Predict with fighter names (red_name, blue_name)",
            "GET /search/{query}": "Search fighters by name"
        }
    }

@app.get("/predict")
def predict(kd_diff: float, str_diff: float, sub_diff: float, td_diff: float, 
            win_rate_diff: float, exp_diff: float, streak_diff: float):
    """Predict using all 7 features"""
    try:
        features = pd.DataFrame([{
            'kd_diff': kd_diff,
            'str_diff': str_diff,
            'sub_diff': sub_diff,
            'td_diff': td_diff,
            'win_rate_diff': win_rate_diff,
            'exp_diff': exp_diff,
            'streak_diff': streak_diff
        }])
        
        probability = predictor.model.predict_proba(features)[0, 1]
        
        return predictor.format_prediction_response(
            probability=probability,
            fighter1_name="Fighter 1",
            fighter2_name="Fighter 2"
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Prediction failed: {str(e)}")

@app.get("/predict-fight")
def predict_fight(red_name: str, blue_name: str):
    """Predict fight outcome using fighter names"""
    try:
        red_stats = fighter_service.get_fighter(red_name)
        blue_stats = fighter_service.get_fighter(blue_name)
        
        probability = predictor.predict_from_fighters(red_stats, blue_stats)
        
        return predictor.format_prediction_response(
            probability=probability,
            fighter1_name=red_name,
            fighter2_name=blue_name,
            fighter1_stats=red_stats,
            fighter2_stats=blue_stats
        )
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/search/{query}")
def search_fighters(query: str, limit: int = 10):
    """Search for fighters by name"""
    if len(query) < 2:
        raise HTTPException(
            status_code=400, 
            detail="Search query must be at least 2 characters"
        )
    
    results = fighter_service.search_fighters(query, limit)
    return {
        "query": query,
        "count": len(results),
        "fighters": results
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    