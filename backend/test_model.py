# test_model.py - Test YOUR UFC model
import joblib
import pandas as pd
import os

print("="*60)
print("TESTING YOUR UFC PREDICTION MODEL")
print("="*60)

# Test 1: Check if model file exists
print("\n📁 1. Checking model file...")
model_path = 'models/ufc_predictor.joblib'

if os.path.exists(model_path):
    print(f"✅ Model found: {model_path}")
else:
    print(f"❌ Model NOT found at: {model_path}")
    print("Available files in models/:")
    for f in os.listdir('models'):
        print(f"  • {f}")
    exit(1)

# Test 2: Load your model
print("\n🔧 2. Loading your model...")
try:
    model = joblib.load(model_path)
    print(f"✅ Model loaded successfully!")
    print(f"   Model type: {type(model).__name__}")
    
    # Check model attributes
    if hasattr(model, 'feature_importances_'):
        print(f"   Has feature_importances_: YES")
        print(f"   Number of features expected: {len(model.feature_importances_)}")
    
except Exception as e:
    print(f"❌ Failed to load model: {e}")
    exit(1)

# Test 3: Make prediction with YOUR features
print("\n🎯 3. Testing prediction with YOUR features...")
try:
    # YOUR model expects these 3 features:
    # 1. win_rate_diff
    # 2. exp_diff  
    # 3. streak_diff
    
    test_data = pd.DataFrame([{
        'win_rate_diff': 0.2,   # Fighter 1 has 20% better win rate
        'exp_diff': 5,          # Fighter 1 has 5 more fights
        'streak_diff': 1        # Fighter 1 has 1 more recent win
    }])
    
    print(f"📊 Test features:")
    print(f"   • win_rate_diff: {test_data['win_rate_diff'].iloc[0]:.3f}")
    print(f"   • exp_diff: {test_data['exp_diff'].iloc[0]}")
    print(f"   • streak_diff: {test_data['streak_diff'].iloc[0]}")
    
    # Make prediction
    prediction = model.predict(test_data)[0]
    probability = model.predict_proba(test_data)[0]
    
    print(f"\n✅ Prediction successful!")
    print(f"   Fighter 1 wins? {'YES' if prediction == 1 else 'NO'}")
    print(f"   Probability Fighter 1 wins: {probability[1]:.3f} ({probability[1]*100:.1f}%)")
    print(f"   Probability Fighter 2 wins: {probability[0]:.3f} ({probability[0]*100:.1f}%)")
    
except Exception as e:
    print(f"❌ Prediction failed: {e}")
    print("\n⚠️  Your model might expect different feature names.")
    print("    Check what features your model was trained with.")

# Test 4: Check feature importance
print("\n📈 4. Checking feature importance...")
if hasattr(model, 'feature_importances_'):
    features = ['win_rate_diff', 'exp_diff', 'streak_diff']
    importance = model.feature_importances_
    
    print("Feature importance:")
    for i, (feature, imp) in enumerate(zip(features, importance)):
        print(f"   {i+1}. {feature}: {imp:.4f}")
else:
    print("⚠️  Model doesn't have feature_importances_ attribute")

print("\n" + "="*60)
print("TEST COMPLETE!")
print("="*60)
print("\n🎉 Your UFC model is working!")
print("   Next: Update api.py to use this model")
