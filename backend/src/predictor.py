#This file holds all the prediction logic, and builds the prediction
import numpy as np
from typing import Dict, Tuple, Optional

class PredictorService:
    """Service for UFC fight predictions"""

    def __init__(self, model, scaler):
        self.model = model
        self.scaler = scaler

    def predict_from_stats(self, kd: float, strikes: float, takedowns: float) -> float:
        """
        Predict fight outcome from raw stats differences
        """
        # Features array 
        features = [[kd, strikes, takedowns, 0, 0, 0, 0]]
        
        # Scale features 
        scaled = self.scaler.transform(features)
        
        # Get probability 
        prob = self.model.predict_proba(scaled)[0, 1]
        
        return float(prob)

    def predict_from_fighters(self, red_stats: Dict, blue_stats: Dict) -> float:
        """
        Predict fight outcome from fighter stat dictionaries
        """
        # Calculate differences 
        kd_diff = red_stats.get('avg_kd', 0) - blue_stats.get('avg_kd', 0)
        strike_diff = red_stats.get('avg_strikes', 0) - blue_stats.get('avg_strikes', 0)
        td_diff = red_stats.get('avg_td', 0) - blue_stats.get('avg_td', 0)
        
        # Features array 
        features = [[kd_diff, strike_diff, td_diff, 0, 0, 0, 0]]
        
        # Scale and predict 
        scaled = self.scaler.transform(features)
        prob = self.model.predict_proba(scaled)[0, 1]
        
        return float(prob)

    def calculate_confidence(self, probability: float) -> str:
        """
        Determine confidence level based on probability
        """
        if abs(probability - 0.5) > 0.3:
            return "High"
        elif abs(probability - 0.5) > 0.15:
            return "Medium"
        else:
            return "Low"
    
    def format_prediction_response(
        self, 
        probability: float, 
        red_name: str, 
        blue_name: str,
        red_stats: Optional[Dict] = None,
        blue_stats: Optional[Dict] = None
    ) -> Dict:
        """
        Format prediction response with all details
        """
        # Basic response 
        response = {
            "fight": f"{red_name} vs {blue_name}",
            "red_win_probability": f"{probability:.1%}",
            "blue_win_probability": f"{(1-probability):.1%}",
            "predicted_winner": red_name if probability > 0.5 else blue_name,
            "confidence": self.calculate_confidence(probability),
        }
        
        # Add stats comparison if stats provided
        if red_stats and blue_stats:
            kd_diff = red_stats.get('avg_kd', 0) - blue_stats.get('avg_kd', 0)
            strike_diff = red_stats.get('avg_strikes', 0) - blue_stats.get('avg_strikes', 0)
            td_diff = red_stats.get('avg_td', 0) - blue_stats.get('avg_td', 0)
            
            response["stats_comparison"] = {
                "knockdown_advantage": f"{red_name} by {kd_diff:.1f}" if kd_diff > 0 else f"{blue_name} by {abs(kd_diff):.1f}",
                "striking_advantage": f"{red_name} by {strike_diff:.1f}" if strike_diff > 0 else f"{blue_name} by {abs(strike_diff):.1f}",
                "takedown_advantage": f"{red_name} by {td_diff:.1f}" if td_diff > 0 else f"{blue_name} by {abs(td_diff):.1f}",
            }
        
        return response
