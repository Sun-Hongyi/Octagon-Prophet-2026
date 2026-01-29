# src/predictor.py - CLEAN VERSION (NO DEBUG)
import numpy as np
import pandas as pd
from typing import Dict, Optional

class PredictorService:
    """UFC fight prediction service for your 7-feature model"""
    
    def __init__(self, model):
        self.model = model
    
    def predict_from_fighters(self, fighter1_stats: Dict, fighter2_stats: Dict) -> float:
        """
        Predict fight outcome from fighter stats
        
        Args:
            fighter1_stats: Dictionary with Fighter 1 stats
            fighter2_stats: Dictionary with Fighter 2 stats
            
        Returns:
            Probability that Fighter 1 wins (0.0 to 1.0)
        """
        # Calculate all 7 feature differences
        kd_diff = fighter1_stats.get('avg_kd', 0) - fighter2_stats.get('avg_kd', 0)
        str_diff = fighter1_stats.get('avg_strikes', 0) - fighter2_stats.get('avg_strikes', 0)
        sub_diff = fighter1_stats.get('avg_sub', 0) - fighter2_stats.get('avg_sub', 0)
        td_diff = fighter1_stats.get('avg_td', 0) - fighter2_stats.get('avg_td', 0)
        win_rate_diff = fighter1_stats.get('win_rate', 0.5) - fighter2_stats.get('win_rate', 0.5)
        exp_diff = fighter1_stats.get('total_fights', 0) - fighter2_stats.get('total_fights', 0)
        streak_diff = fighter1_stats.get('win_streak', 0) - fighter2_stats.get('win_streak', 0)
        
        # Create DataFrame with ALL 7 features
        features = pd.DataFrame([{
            'kd_diff': kd_diff,
            'str_diff': str_diff,
            'sub_diff': sub_diff,
            'td_diff': td_diff,
            'win_rate_diff': win_rate_diff,
            'exp_diff': exp_diff,
            'streak_diff': streak_diff
        }])
        
        # Make sure we have all expected columns
        if hasattr(self.model, 'feature_names_in_'):
            expected_columns = list(self.model.feature_names_in_)
        else:
            # Default to the 7 features
            expected_columns = ['kd_diff', 'str_diff', 'sub_diff', 'td_diff', 
                              'win_rate_diff', 'exp_diff', 'streak_diff']
        
        # Fill any missing columns with 0
        for col in expected_columns:
            if col not in features.columns:
                features[col] = 0
        
        # Reorder columns to match training
        features = features[expected_columns]
        
        # Predict
        probability = self.model.predict_proba(features)[0, 1]
        
        return float(probability)
    
    def predict_from_names(self, fighter1_name: str, fighter2_name: str, 
                          fighter_service) -> float:
        """
        Convenience method: Predict using fighter names
        """
        fighter1_stats = fighter_service.get_fighter(fighter1_name)
        fighter2_stats = fighter_service.get_fighter(fighter2_name)
        
        return self.predict_from_fighters(fighter1_stats, fighter2_stats)
    
    def calculate_confidence(self, probability: float) -> str:
        """
        Determine confidence level based on probability
        """
        if probability > 0.8 or probability < 0.2:
            return "Very High"
        elif probability > 0.7 or probability < 0.3:
            return "High"
        elif probability > 0.6 or probability < 0.4:
            return "Medium"
        else:
            return "Low (Close Fight)"
    
    def format_prediction_response(
        self, 
        probability: float, 
        fighter1_name: str, 
        fighter2_name: str,
        fighter1_stats: Optional[Dict] = None,
        fighter2_stats: Optional[Dict] = None
    ) -> Dict:
        """
        Format prediction response for frontend
        """
        predicted_winner = fighter1_name if probability > 0.5 else fighter2_name
        winner_probability = probability if probability > 0.5 else 1 - probability
        
        response = {
            "fight": f"{fighter1_name} vs {fighter2_name}",
            "prediction": predicted_winner,
            "confidence": self.calculate_confidence(probability),
            "probabilities": {
                fighter1_name: f"{probability:.1%}",
                fighter2_name: f"{(1-probability):.1%}"
            },
            "winner_probability": f"{winner_probability:.1%}",
            "is_close_fight": (0.4 <= probability <= 0.6)
        }
        
        if fighter1_stats and fighter2_stats:
            response["advantages"] = {
                "knockdowns": f"{fighter1_name} by {fighter1_stats.get('avg_kd', 0) - fighter2_stats.get('avg_kd', 0):.2f} avg",
                "strikes": f"{fighter1_name} by {fighter1_stats.get('avg_strikes', 0) - fighter2_stats.get('avg_strikes', 0):.1f} avg",
                "submissions": f"{fighter1_name} by {fighter1_stats.get('avg_sub', 0) - fighter2_stats.get('avg_sub', 0):.2f} avg",
                "takedowns": f"{fighter1_name} by {fighter1_stats.get('avg_td', 0) - fighter2_stats.get('avg_td', 0):.2f} avg",
                "win_rate": f"{fighter1_name} by {fighter1_stats.get('win_rate', 0.5) - fighter2_stats.get('win_rate', 0.5):.3f}",
                "experience": f"{fighter1_name} by {fighter1_stats.get('total_fights', 0) - fighter2_stats.get('total_fights', 0)} fights",
                "recent_form": f"{fighter1_name} by {fighter1_stats.get('win_streak', 0) - fighter2_stats.get('win_streak', 0)} wins"
            }
        
        return response
    
    def get_feature_importance(self) -> Dict:
        """Get feature importance from your model"""
        if hasattr(self.model, 'feature_importances_'):
            importance = self.model.feature_importances_
            
            if hasattr(self.model, 'feature_names_in_'):
                features = list(self.model.feature_names_in_)
            else:
                features = ['kd_diff', 'str_diff', 'sub_diff', 'td_diff', 
                           'win_rate_diff', 'exp_diff', 'streak_diff']
            
            return {
                features[i]: float(importance[i])
                for i in range(min(len(features), len(importance)))
            }
        return {}
    