# api.py - FINAL FIXED VERSION
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
    version="2.0",
    description="REBALANCED API for predicting UFC fights with fight stats emphasis"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load REBALANCED model
model = joblib.load('models/ufc_predictor.joblib')
predictor = PredictorService(model)

# Load REBALANCED fighter database
fighter_service = FighterService('fighter_database_REBALANCED.json')

@app.get("/")
def home():
    return {
        "message": "UFC Predictor API 🥊",
        "version": "2.0",
        "model_type": "REBALANCED - Fight Stats Emphasis",
        "feature_priority": "1. Fight Statistics, 2. Recent Form, 3. Career",
        "endpoints": {
            "GET /": "This page",
            "GET /predict": "Predict with raw features",
            "GET /predict-fight": "Predict with fighter names (red_name, blue_name)",
            "GET /search/{query}": "Search fighters by name",
            "GET /model-info": "Get REBALANCED model information"
        }
    }

@app.get("/model-info")
def model_info():
    """Get REBALANCED model information"""
    return {
        "model": "REBALANCED UFC Predictor v2.0",
        "emphasis": "Fight Statistics > Recent Form > Career",
        "key_features": [
            "Striking volume and accuracy",
            "Knockdown power", 
            "Takedown and grappling advantage",
            "Submission threat",
            "Recent win streak",
            "Career win rate (de-emphasized)",
            "Experience (de-emphasized)"
        ],
        "files_used": [
            "ufc_predictor.joblib",
            "fighter_database_REBALANCED.json"
        ]
    }

@app.get("/predict")
def predict(
    str_diff: float, kd_diff: float, td_diff: float, sub_diff: float,
    streak_diff: float, win_rate_diff: float, exp_diff: float
):
    """Predict using REBALANCED features (fight stats first!)"""
    try:
        # Create features with REBALANCED priority order
        features = pd.DataFrame([{
            'str_diff': str_diff,
            'kd_diff': kd_diff,
            'td_diff': td_diff,
            'sub_diff': sub_diff,
            'streak_diff': streak_diff,
            'win_rate_diff': win_rate_diff,
            'exp_diff': exp_diff
        }])
        
        probability = predictor.model.predict_proba(features)[0, 1]
        
        # Create a simple prediction result - MATCHES NEW PREDICTOR FORMAT
        prediction_result = {
            'probability_fighter1_wins': float(probability),
            'probability_fighter2_wins': float(1 - probability),
            'predicted_winner_id': 'fighter1' if probability > 0.5 else 'fighter2',  # FIXED: Use 'predicted_winner_id'
            'confidence': predictor.calculate_confidence(probability),
            'fighter1': 'Fighter 1',
            'fighter2': 'Fighter 2',
            'fight': 'Fighter 1 vs Fighter 2',
            'feature_impacts': {'fight_stats': 0, 'recent_form': 0, 'career': 0},
            'key_advantages': []
        }
        
        return predictor.format_prediction_response(prediction_result)
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Prediction failed: {str(e)}")

@app.get("/predict-fight")
def predict_fight(red_name: str, blue_name: str):
    """Predict fight outcome using fighter names (REBALANCED)"""
    try:
        # Get fighter stats from REBALANCED database
        red_stats = fighter_service.get_fighter(red_name)
        blue_stats = fighter_service.get_fighter(blue_name)
        
        # Use REBALANCED prediction - returns a dictionary
        prediction_result = predictor.predict_from_fighters(red_stats, blue_stats)
        
        # Add fighter names to the prediction result
        prediction_result['fighter1'] = red_name
        prediction_result['fighter2'] = blue_name
        prediction_result['fight'] = f"{red_name} vs {blue_name}"
        
        # Format the response
        response = predictor.format_prediction_response(prediction_result)
        
        return response
        
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

@app.get("/feature-importance")
def feature_importance():
    """Get REBALANCED feature importance"""
    importance = predictor.get_feature_importance()
    
    # Categorize for REBALANCED model
    categories = {
        'fight_stats': [],
        'recent_form': [],
        'career': []
    }
    
    for feat, imp in importance.items():
        if 'str' in feat.lower() or 'kd' in feat.lower() or 'td' in feat.lower() or 'sub' in feat.lower():
            categories['fight_stats'].append((feat, imp))
        elif 'streak' in feat.lower():
            categories['recent_form'].append((feat, imp))
        elif 'win_rate' in feat.lower() or 'exp' in feat.lower():
            categories['career'].append((feat, imp))
    
    return {
        "model": "REBALANCED",
        "total_features": len(importance),
        "categories": categories
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    