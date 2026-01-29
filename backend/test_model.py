#Checks if model works

import joblib
import numpy as np

print("🧪 Testing if model loads...")

try:
    # Load your models
    model = joblib.load('models/ufc_model_20260129_095125.pkl')
    scaler = joblib.load('models/ufc_scaler_20260129_095125.pkl')
    
    print("✅ Models loaded successfully!")
    
    # Test prediction
    test_features = [[2, 35, 1, 0.15, 0.1, 0.25, 0]]  # Example fight
    scaled_features = scaler.transform(test_features)
    probability = model.predict_proba(scaled_features)[0, 1]
    
    print(f"🎯 Test prediction: {probability:.1%} chance Red wins")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("Make sure models are in backend/models/ folder!")
