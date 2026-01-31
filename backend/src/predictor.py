# src/predictor.py - FIXED VERSION
import numpy as np
import pandas as pd
from typing import Dict, Optional, List

class PredictorService:
    """UFC fight prediction service for REBALANCED 7+ feature model"""
    
    def __init__(self, model):
        self.model = model
        print("🎯 REBALANCED Predictor Service initialized")
        print("   • Emphasis: FIGHT STATISTICS > Recent Form > Career")
    
    def predict_from_fighters(self, fighter1_stats: Dict, fighter2_stats: Dict) -> Dict:
        """
        Predict fight outcome from REBALANCED fighter stats
        
        Args:
            fighter1_stats: Dictionary with Fighter 1 REBALANCED stats
            fighter2_stats: Dictionary with Fighter 2 REBALANCED stats
            
        Returns:
            Dictionary with prediction results
        """
        # Calculate ALL feature differences for REBALANCED model
        features_dict = {}
        
        # 1. FIGHT STATISTICS FEATURES (MOST IMPORTANT)
        # Striking features
        str_diff = fighter1_stats.get('avg_strikes', 0) - fighter2_stats.get('avg_strikes', 0)
        features_dict['str_diff'] = str_diff
        features_dict['str_ratio'] = fighter1_stats.get('avg_strikes', 0.1) / (fighter2_stats.get('avg_strikes', 0.1) + 0.1)
        features_dict['str_dominance'] = 1 if str_diff > 0 else 0
        
        # Enhanced striking (weighted)
        features_dict['striking_volume_advantage'] = str_diff * 1.5
        features_dict['striking_dominance'] = features_dict['str_dominance'] * 2
        
        # Knockdown features
        kd_diff = fighter1_stats.get('avg_knockdowns', 0) - fighter2_stats.get('avg_knockdowns', 0)
        features_dict['kd_diff'] = kd_diff
        features_dict['kd_ratio'] = fighter1_stats.get('avg_knockdowns', 0.1) / (fighter2_stats.get('avg_knockdowns', 0.1) + 0.1)
        features_dict['kd_dominance'] = 1 if kd_diff > 0 else 0
        features_dict['knockdown_power'] = kd_diff * 2  # Double weight
        
        # Takedown features
        td_diff = fighter1_stats.get('avg_takedowns', 0) - fighter2_stats.get('avg_takedowns', 0)
        features_dict['td_diff'] = td_diff
        features_dict['td_ratio'] = fighter1_stats.get('avg_takedowns', 0.1) / (fighter2_stats.get('avg_takedowns', 0.1) + 0.1)
        features_dict['td_dominance'] = 1 if td_diff > 0 else 0
        
        # Submission features
        sub_diff = fighter1_stats.get('avg_submissions', 0) - fighter2_stats.get('avg_submissions', 0)
        features_dict['sub_diff'] = sub_diff
        features_dict['sub_ratio'] = fighter1_stats.get('avg_submissions', 0.1) / (fighter2_stats.get('avg_submissions', 0.1) + 0.1)
        features_dict['sub_dominance'] = 1 if sub_diff > 0 else 0
        features_dict['submission_threat'] = sub_diff * 1.8  # Higher weight
        
        # 2. RECENT FORM FEATURES
        streak_diff = fighter1_stats.get('win_streak', 0) - fighter2_stats.get('win_streak', 0)
        features_dict['streak_diff'] = streak_diff
        
        # 3. CAREER FEATURES (LEAST IMPORTANT)
        win_rate_diff = fighter1_stats.get('win_rate', 0.5) - fighter2_stats.get('win_rate', 0.5)
        features_dict['win_rate_diff'] = win_rate_diff
        exp_diff = fighter1_stats.get('total_fights', 0) - fighter2_stats.get('total_fights', 0)
        features_dict['exp_diff'] = exp_diff
        
        # Create DataFrame
        features_df = pd.DataFrame([features_dict])
        
        # Ensure all expected columns exist
        if hasattr(self.model, 'feature_names_in_'):
            expected_columns = list(self.model.feature_names_in_)
        else:
            # Default columns from REBALANCED model
            expected_columns = [
                'str_diff', 'str_ratio', 'str_dominance', 'striking_volume_advantage', 'striking_dominance',
                'kd_diff', 'kd_ratio', 'kd_dominance', 'knockdown_power',
                'td_diff', 'td_ratio', 'td_dominance',
                'sub_diff', 'sub_ratio', 'sub_dominance', 'submission_threat',
                'streak_diff', 'win_rate_diff', 'exp_diff'
            ]
        
        # Fill missing columns with 0
        for col in expected_columns:
            if col not in features_df.columns:
                features_df[col] = 0
        
        # Reorder columns
        features_df = features_df[expected_columns]
        
        # Predict
        probability = self.model.predict_proba(features_df)[0, 1]
        
        # Calculate impact by category
        fight_stat_impact = sum(abs(features_dict.get(col, 0)) for col in 
                               ['str_diff', 'kd_diff', 'td_diff', 'sub_diff'])
        recent_impact = abs(streak_diff)
        career_impact = abs(win_rate_diff) + abs(exp_diff)
        total_impact = fight_stat_impact + recent_impact + career_impact
        
        # Identify key advantages
        key_advantages = []
        if abs(str_diff) > 10:
            key_advantages.append(f"{'Fighter 1' if str_diff > 0 else 'Fighter 2'} has striking advantage")
        if abs(kd_diff) > 0.5:
            key_advantages.append(f"{'Fighter 1' if kd_diff > 0 else 'Fighter 2'} has knockdown power")
        if abs(td_diff) > 1:
            key_advantages.append(f"{'Fighter 1' if td_diff > 0 else 'Fighter 2'} has grappling advantage")
        if abs(streak_diff) >= 2:
            key_advantages.append(f"{'Fighter 1' if streak_diff > 0 else 'Fighter 2'} has momentum")
        
        return {
            'probability_fighter1_wins': float(probability),
            'probability_fighter2_wins': float(1 - probability),
            'predicted_winner_id': 'fighter1' if probability > 0.5 else 'fighter2',  # CHANGED: Use ID instead of name
            'confidence': self.calculate_confidence(probability),
            'feature_impacts': {
                'fight_stats': fight_stat_impact / total_impact if total_impact > 0 else 0,
                'recent_form': recent_impact / total_impact if total_impact > 0 else 0,
                'career': career_impact / total_impact if total_impact > 0 else 0
            },
            'key_advantages': key_advantages if key_advantages else ["Evenly matched fight"],
            'detailed_features': features_dict
        }
    
    def predict_from_names(self, fighter1_name: str, fighter2_name: str, 
                          fighter_service) -> Dict:
        """
        Predict using fighter names with REBALANCED service
        """
        # Get stats in REBALANCED format
        fighter1_stats = fighter_service.get_fighter_stats_for_model(fighter1_name)
        fighter2_stats = fighter_service.get_fighter_stats_for_model(fighter2_name)
        
        result = self.predict_from_fighters(fighter1_stats, fighter2_stats)
        
        # Add fighter names to result
        result['fighter1'] = fighter1_name
        result['fighter2'] = fighter2_name
        result['fight'] = f"{fighter1_name} vs {fighter2_name}"
        
        return result
    
    def calculate_confidence(self, probability: float) -> str:
        """
        Determine confidence level based on probability
        """
        prob = max(probability, 1 - probability)  # Winner's probability
        
        if prob > 0.85:
            return "Very High"
        elif prob > 0.75:
            return "High"
        elif prob > 0.65:
            return "Medium"
        elif prob > 0.55:
            return "Low"
        else:
            return "Very Low (Toss-up)"
    
    def format_prediction_response(self, prediction_result: Dict) -> Dict:
        """
        Format REBALANCED prediction response for frontend
        """
        fighter1 = prediction_result.get('fighter1', 'Fighter 1')
        fighter2 = prediction_result.get('fighter2', 'Fighter 2')
        prob1 = prediction_result['probability_fighter1_wins']
        prob2 = prediction_result['probability_fighter2_wins']
        
        # Determine actual winner name (FIXED)
        winner_id = prediction_result.get('predicted_winner_id', 'fighter1')
        predicted_winner = fighter1 if winner_id == 'fighter1' else fighter2
        
        response = {
            "fight": prediction_result.get('fight', f"{fighter1} vs {fighter2}"),
            "prediction": predicted_winner,  # FIXED: Now shows actual fighter name
            "confidence": prediction_result['confidence'],
            "probabilities": {
                fighter1: f"{prob1:.1%}",
                fighter2: f"{prob2:.1%}"
            },
            "winner_probability": f"{max(prob1, prob2):.1%}",
            "is_close_fight": (0.45 <= prob1 <= 0.55),
            "model_type": "REBALANCED (Fight Stats Emphasis)",
            "feature_importance": {
                "Fight Statistics": f"{prediction_result['feature_impacts']['fight_stats']:.1%}",
                "Recent Form": f"{prediction_result['feature_impacts']['recent_form']:.1%}",
                "Career Stats": f"{prediction_result['feature_impacts']['career']:.1%}"
            },
            "key_factors": prediction_result['key_advantages']
        }
        
        return response
    
    def get_feature_importance(self) -> Dict:
        """Get feature importance from REBALANCED model"""
        if hasattr(self.model, 'feature_importances_'):
            importance = self.model.feature_importances_
            
            if hasattr(self.model, 'feature_names_in_'):
                features = list(self.model.feature_names_in_)
            else:
                features = [
                    'str_diff', 'kd_diff', 'td_diff', 'sub_diff',
                    'streak_diff', 'win_rate_diff', 'exp_diff'
                ]
            
            # Categorize features
            importance_dict = {}
            for i, feat in enumerate(features):
                category = self._categorize_feature(feat)
                importance_dict[feat] = {
                    'importance': float(importance[i]),
                    'category': category
                }
            
            return importance_dict
        return {}
    
    def _categorize_feature(self, feature_name: str) -> str:
        """Categorize feature for REBALANCED model"""
        feat_lower = feature_name.lower()
        
        if any(x in feat_lower for x in ['str', 'striking', 'kd', 'knockdown', 'td', 'takedown', 'sub', 'submission']):
            return 'FIGHT_STATS'
        elif 'streak' in feat_lower:
            return 'RECENT_FORM'
        elif any(x in feat_lower for x in ['win_rate', 'exp']):
            return 'CAREER'
        else:
            return 'OTHER'
    
    def get_model_info(self) -> Dict:
        """Get REBALANCED model information"""
        return {
            "model_type": "REBALANCED Random Forest",
            "emphasis": "FIGHT STATISTICS > Recent Form > Career",
            "key_features": "Striking volume, Knockdowns, Takedowns, Submissions",
            "training_data": "UFC fights 1994-2025",
            "accuracy": "Optimized for fight stat prediction"
        }
    