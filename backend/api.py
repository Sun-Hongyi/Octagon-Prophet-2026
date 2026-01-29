# api.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware  # ← ADD THIS
import joblib
import json
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.predictor import PredictorService
from src.fighter_service import FighterService

app = FastAPI(title="UFC Predictor API", version="1.0")

# CORS middleware - ALLOWS React to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Your React app URL
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Load model and setup services
print("🔧 Loading ML model...")
model = joblib.load('models/ufc_model.pkl')
scaler = joblib.load('models/ufc_scaler.pkl')
predictor = PredictorService(model, scaler)

print("📊 Loading fighter database...")
fighter_service = FighterService('fighter_database_detailed.json')

print("✅ UFC Predictor API ready!")

@app.get("/")
def home():
    return {
        "message": "UFC Predictor API 🥊",
        "version": "1.0",
        "endpoints": {
            "GET /": "This page",
            "GET /predict": "Predict with stats (kd, strikes, takedowns)",
            "GET /predict-fight": "Predict with fighter names (red_name, blue_name)",
            "GET /search/{query}": "Search fighters by name"
        }
    }

@app.get("/predict")
def predict(kd: float, strikes: float, takedowns: float):
    """Predict fight outcome using raw stats differences"""
    try:
        probability = predictor.predict_from_stats(kd, strikes, takedowns)
        return predictor.format_prediction_response(
            probability=probability,
            red_name="Red Fighter",
            blue_name="Blue Fighter"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Prediction failed: {str(e)}")

@app.get("/predict-fight")
def predict_fight(red_name: str, blue_name: str):
    """Predict fight outcome using fighter names"""
    try:
        # Get fighter stats
        red_stats = fighter_service.get_fighter(red_name)
        blue_stats = fighter_service.get_fighter(blue_name)
        
        # Make prediction
        probability = predictor.predict_from_fighters(red_stats, blue_stats)
        
        # Format response
        return predictor.format_prediction_response(
            probability=probability,
            red_name=red_name,
            blue_name=blue_name,
            red_stats=red_stats,
            blue_stats=blue_stats
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
    