#!/usr/bin/env python3
"""
Advanced ML Models for FPL Player Performance Prediction

This module implements multiple sophisticated models including:
1. Markov Chain for form transitions
2. Deep Learning with age/injury factors
3. News sentiment analysis
4. Ensemble methods combining multiple approaches
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_absolute_error, mean_squared_error
import joblib
import requests
import re
from datetime import datetime, timedelta
import logging
from textblob import TextBlob
import warnings
warnings.filterwarnings('ignore')

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MarkovChainFormPredictor:
    """
    Markov Chain model for predicting player form transitions
    Analyzes historical form patterns to predict future performance states
    """
    
    def __init__(self):
        self.transition_matrix = {}
        self.form_states = ['Poor', 'Below Average', 'Average', 'Good', 'Excellent']
        self.state_ranges = {
            'Poor': (0, 2),
            'Below Average': (2, 4), 
            'Average': (4, 6),
            'Good': (6, 8),
            'Excellent': (8, 12)
        }
    
    def categorize_form(self, points):
        """Convert numerical points to form state"""
        for state, (min_val, max_val) in self.state_ranges.items():
            if min_val <= points < max_val:
                return state
        return 'Excellent' if points >= 8 else 'Poor'
    
    def build_transition_matrix(self, historical_data):
        """
        Build transition probability matrix from historical gameweek data
        Args:
            historical_data: DataFrame with columns ['player_id', 'gameweek', 'points']
        """
        logger.info("Building Markov Chain transition matrix...")
        
        # Initialize transition counts
        transitions = {}
        for state1 in self.form_states:
            transitions[state1] = {state2: 0 for state2 in self.form_states}
        
        # Count transitions for each player
        for player_id in historical_data['player_id'].unique():
            player_data = historical_data[historical_data['player_id'] == player_id].sort_values('gameweek')
            
            if len(player_data) < 2:
                continue
                
            # Convert points to form states
            form_sequence = [self.categorize_form(points) for points in player_data['points']]
            
            # Count state transitions
            for i in range(len(form_sequence) - 1):
                current_state = form_sequence[i]
                next_state = form_sequence[i + 1]
                transitions[current_state][next_state] += 1
        
        # Convert counts to probabilities
        self.transition_matrix = {}
        for state1 in self.form_states:
            total_transitions = sum(transitions[state1].values())
            if total_transitions > 0:
                self.transition_matrix[state1] = {
                    state2: count / total_transitions 
                    for state2, count in transitions[state1].items()
                }
            else:
                # Uniform distribution if no data
                self.transition_matrix[state1] = {
                    state2: 1/len(self.form_states) for state2 in self.form_states
                }
        
        logger.info("Markov Chain transition matrix built successfully")
    
    def predict_next_form(self, current_form_points, steps=1):
        """
        Predict player's form state for next gameweek(s)
        Args:
            current_form_points: Current form score
            steps: Number of steps ahead to predict
        Returns:
            Expected points for next gameweek
        """
        current_state = self.categorize_form(current_form_points)
        
        # Get transition probabilities
        state_probs = {state: 0.0 for state in self.form_states}
        state_probs[current_state] = 1.0
        
        # Apply transition matrix for 'steps' iterations
        for _ in range(steps):
            new_probs = {state: 0.0 for state in self.form_states}
            for state1, prob1 in state_probs.items():
                for state2, transition_prob in self.transition_matrix[state1].items():
                    new_probs[state2] += prob1 * transition_prob
            state_probs = new_probs
        
        # Calculate expected points
        expected_points = 0
        for state, prob in state_probs.items():
            min_points, max_points = self.state_ranges[state]
            avg_points = (min_points + max_points) / 2
            expected_points += prob * avg_points
        
        return expected_points

class PlayerAgeInjuryAnalyzer:
    """
    Analyzes age and injury impact on player performance
    """
    
    def __init__(self):
        self.age_performance_curve = {}
        self.injury_impact_factors = {}
    
    def calculate_age_factor(self, age, position):
        """
        Calculate age-based performance multiplier
        Different positions have different age curves
        """
        age_curves = {
            'Goalkeeper': {
                'peak_age': 30,
                'decline_start': 35,
                'steep_decline': 38
            },
            'Defender': {
                'peak_age': 28,
                'decline_start': 32,
                'steep_decline': 35
            },
            'Midfielder': {
                'peak_age': 26,
                'decline_start': 30,
                'steep_decline': 34
            },
            'Forward': {
                'peak_age': 27,
                'decline_start': 31,
                'steep_decline': 34
            }
        }
        
        curve = age_curves.get(position, age_curves['Midfielder'])
        
        if age <= curve['peak_age']:
            # Linear increase to peak
            return 0.8 + (0.2 * age / curve['peak_age'])
        elif age <= curve['decline_start']:
            # Peak performance
            return 1.0
        elif age <= curve['steep_decline']:
            # Gradual decline
            decline_years = age - curve['decline_start']
            decline_rate = 0.05  # 5% per year
            return 1.0 - (decline_rate * decline_years)
        else:
            # Steep decline
            return max(0.6, 1.0 - 0.1 * (age - curve['steep_decline']))
    
    def analyze_injury_history(self, player_data):
        """
        Analyze player's injury history and current status
        Returns injury risk factor (0-1, where 1 = no risk)
        """
        # This would ideally fetch from injury databases
        # For now, use minutes played as proxy
        recent_minutes = player_data.get('minutes', 0)
        total_possible = 90 * 10  # Assume 10 games played so far
        
        availability_rate = recent_minutes / total_possible if total_possible > 0 else 0
        
        # Players with low minutes might be injured or out of favor
        if availability_rate < 0.3:
            return 0.6  # High injury/unavailability risk
        elif availability_rate < 0.6:
            return 0.8  # Moderate risk
        else:
            return 1.0  # Low risk

class NewsAnalyzer:
    """
    Analyzes recent news and social media sentiment about players
    """
    
    def __init__(self):
        self.news_sources = [
            'https://www.skysports.com/premier-league/news',
            'https://www.bbc.com/sport/football/premier-league',
            'https://www.premierleague.com/news'
        ]
    
    def search_player_news(self, player_name, team_name, days_back=7):
        """
        Search for recent news about a specific player
        Returns sentiment score (-1 to 1)
        """
        try:
            # This is a simplified version - would need proper news API integration
            # For now, return neutral sentiment
            
            # Simulate news search and sentiment analysis
            search_terms = [player_name, f"{player_name} injury", f"{player_name} form"]
            
            # Mock sentiment based on player name (for demo)
            # In real implementation, would use News API + sentiment analysis
            sentiment_scores = []
            
            for term in search_terms:
                # Simulate sentiment analysis
                mock_sentiment = self._mock_sentiment_analysis(player_name, team_name)
                sentiment_scores.append(mock_sentiment)
            
            return np.mean(sentiment_scores)
            
        except Exception as e:
            logger.warning(f"News analysis failed for {player_name}: {e}")
            return 0.0  # Neutral sentiment if analysis fails
    
    def _mock_sentiment_analysis(self, player_name, team_name):
        """
        Mock sentiment analysis - replace with real news API integration
        """
        # Simulate different scenarios
        risk_keywords = ['injury', 'doubt', 'suspended', 'dropped']
        positive_keywords = ['scoring', 'excellent', 'form', 'starting']
        
        # Random sentiment for demo (replace with real analysis)
        base_sentiment = np.random.normal(0, 0.3)
        return np.clip(base_sentiment, -1, 1)

class EnsemblePredictor:
    """
    Combines multiple prediction models for improved accuracy
    """
    
    def __init__(self):
        self.models = {}
        self.weights = {}
        self.scaler = StandardScaler()
        self.markov_model = MarkovChainFormPredictor()
        self.age_analyzer = PlayerAgeInjuryAnalyzer()
        self.news_analyzer = NewsAnalyzer()
    
    def prepare_advanced_features(self, players_df):
        """
        Create advanced features for ML models
        """
        logger.info("Preparing advanced features...")
        
        # Basic features
        features_df = players_df.copy()
        
        # Age-related features
        current_year = datetime.now().year
        features_df['age'] = features_df.get('age', 25)  # Default age if not available
        
        # Calculate age factors
        features_df['age_factor'] = features_df.apply(
            lambda row: self.age_analyzer.calculate_age_factor(row['age'], row['position']), 
            axis=1
        )
        
        # Injury risk analysis
        features_df['injury_risk_factor'] = features_df.apply(
            lambda row: self.age_analyzer.analyze_injury_history(row), 
            axis=1
        )
        
        # Form consistency (variance in recent form)
        features_df['form_consistency'] = 1 / (1 + features_df['form'].std()) if len(features_df) > 1 else 1
        
        # Value metrics
        features_df['cost_efficiency'] = features_df['total_points'] / features_df['cost']
        features_df['form_per_cost'] = features_df['form'] / features_df['cost']
        
        # Position encoding
        le = LabelEncoder()
        features_df['position_encoded'] = le.fit_transform(features_df['position'])
        
        # Team strength (based on average team performance)
        team_strength = features_df.groupby('team')['total_points'].mean()
        features_df['team_strength'] = features_df['team'].map(team_strength)
        
        # Recent transfer activity
        features_df['transfer_momentum'] = (
            features_df['transfers_in_event'] - features_df['transfers_out_event']
        )
        
        # News sentiment (simplified for now)
        features_df['news_sentiment'] = features_df.apply(
            lambda row: self.news_analyzer.search_player_news(row['name'], row['team']),
            axis=1
        )
        
        return features_df
    
    def train_ensemble_models(self, training_data):
        """
        Train multiple ML models and determine optimal weights
        """
        logger.info("Training ensemble models...")
        
        # Prepare features
        X = training_data[[
            'form', 'cost', 'minutes', 'total_points', 'points_per_game',
            'influence', 'creativity', 'threat', 'ict_index',
            'selected_by_percent', 'age_factor', 'injury_risk_factor',
            'cost_efficiency', 'form_per_cost', 'position_encoded',
            'team_strength', 'transfer_momentum', 'news_sentiment'
        ]].fillna(0)
        
        # Target variable (next gameweek points)
        y = training_data['next_gw_points'].fillna(training_data['form'])
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42
        )
        
        # Train multiple models
        self.models['random_forest'] = RandomForestRegressor(
            n_estimators=200, max_depth=15, random_state=42
        )
        self.models['gradient_boost'] = GradientBoostingRegressor(
            n_estimators=200, max_depth=8, learning_rate=0.1, random_state=42
        )
        
        # Train models and calculate weights based on performance
        model_scores = {}
        
        for name, model in self.models.items():
            # Train model
            model.fit(X_train, y_train)
            
            # Evaluate performance
            y_pred = model.predict(X_test)
            mae = mean_absolute_error(y_test, y_pred)
            cv_scores = cross_val_score(model, X_scaled, y, cv=5, scoring='neg_mean_absolute_error')
            
            model_scores[name] = -np.mean(cv_scores)
            logger.info(f"{name} - MAE: {mae:.3f}, CV Score: {-np.mean(cv_scores):.3f}")
        
        # Calculate ensemble weights (inverse of error)
        total_inverse_error = sum(1/score for score in model_scores.values())
        self.weights = {
            name: (1/score) / total_inverse_error 
            for name, score in model_scores.items()
        }
        
        logger.info(f"Ensemble weights: {self.weights}")
    
    def predict_with_ensemble(self, players_df):
        """
        Make predictions using ensemble of models + Markov Chain
        """
        # Prepare features
        features_df = self.prepare_advanced_features(players_df)
        
        X = features_df[[
            'form', 'cost', 'minutes', 'total_points', 'points_per_game',
            'influence', 'creativity', 'threat', 'ict_index',
            'selected_by_percent', 'age_factor', 'injury_risk_factor',
            'cost_efficiency', 'form_per_cost', 'position_encoded',
            'team_strength', 'transfer_momentum', 'news_sentiment'
        ]].fillna(0)
        
        # Scale features
        X_scaled = self.scaler.transform(X)
        
        # Get predictions from each model
        ensemble_predictions = np.zeros(len(players_df))
        
        for name, model in self.models.items():
            predictions = model.predict(X_scaled)
            ensemble_predictions += self.weights[name] * predictions
        
        # Add Markov Chain predictions
        markov_predictions = []
        for _, player in features_df.iterrows():
            markov_pred = self.markov_model.predict_next_form(player['form'])
            markov_predictions.append(markov_pred)
        
        markov_predictions = np.array(markov_predictions)
        
        # Combine ensemble + Markov Chain (70% ensemble, 30% Markov)
        final_predictions = 0.7 * ensemble_predictions + 0.3 * markov_predictions
        
        # Apply age and injury factors
        final_predictions *= features_df['age_factor'] * features_df['injury_risk_factor']
        
        # Apply news sentiment adjustment
        sentiment_multiplier = 1 + (features_df['news_sentiment'] * 0.1)  # ±10% based on news
        final_predictions *= sentiment_multiplier
        
        return final_predictions
    
    def save_models(self, save_path="models/"):
        """Save trained models"""
        import os
        os.makedirs(save_path, exist_ok=True)
        
        # Save ensemble models
        for name, model in self.models.items():
            joblib.dump(model, f"{save_path}ensemble_{name}.pkl")
        
        # Save other components
        joblib.dump(self.scaler, f"{save_path}scaler.pkl")
        joblib.dump(self.weights, f"{save_path}ensemble_weights.pkl")
        joblib.dump(self.markov_model, f"{save_path}markov_model.pkl")
        
        logger.info(f"Models saved to {save_path}")
    
    def load_models(self, load_path="models/"):
        """Load trained models"""
        try:
            # Load ensemble models
            self.models['random_forest'] = joblib.load(f"{load_path}ensemble_random_forest.pkl")
            self.models['gradient_boost'] = joblib.load(f"{load_path}ensemble_gradient_boost.pkl")
            
            # Load other components
            self.scaler = joblib.load(f"{load_path}scaler.pkl")
            self.weights = joblib.load(f"{load_path}ensemble_weights.pkl")
            self.markov_model = joblib.load(f"{load_path}markov_model.pkl")
            
            logger.info("Advanced models loaded successfully")
            return True
            
        except Exception as e:
            logger.warning(f"Could not load advanced models: {e}")
            return False

def create_sample_training_data():
    """
    Create sample training data for model development
    This would be replaced with actual historical FPL data
    """
    np.random.seed(42)
    
    # Generate sample data for 100 players over 20 gameweeks
    players = []
    for player_id in range(1, 101):
        for gw in range(1, 21):
            # Simulate player performance with various factors
            base_form = np.random.normal(5, 2)
            age_effect = np.random.normal(0, 0.5)
            injury_effect = np.random.choice([0, -2, -4], p=[0.8, 0.15, 0.05])
            
            points = max(0, base_form + age_effect + injury_effect + np.random.normal(0, 1))
            
            players.append({
                'player_id': player_id,
                'gameweek': gw,
                'points': points,
                'form': base_form,
                'age': np.random.randint(18, 38),
                'position': np.random.choice(['Goalkeeper', 'Defender', 'Midfielder', 'Forward']),
                'cost': np.random.uniform(4.0, 12.0),
                'minutes': np.random.randint(0, 90),
                'total_points': points * gw,
                'points_per_game': points,
                'influence': np.random.uniform(0, 100),
                'creativity': np.random.uniform(0, 100),
                'threat': np.random.uniform(0, 100),
                'ict_index': np.random.uniform(0, 20),
                'selected_by_percent': np.random.uniform(0, 50),
                'team': f"Team_{np.random.randint(1, 21)}",
                'name': f"Player_{player_id}",
                'transfers_in_event': np.random.randint(0, 1000),
                'transfers_out_event': np.random.randint(0, 1000),
                'next_gw_points': max(0, points + np.random.normal(0, 2))  # Target variable
            })
    
    return pd.DataFrame(players)

def main():
    """Test the advanced ML system"""
    logger.info("Testing Advanced ML System...")
    
    # Create sample data
    training_data = create_sample_training_data()
    
    # Initialize ensemble predictor
    predictor = EnsemblePredictor()
    
    # Build Markov Chain from historical data
    predictor.markov_model.build_transition_matrix(
        training_data[['player_id', 'gameweek', 'points']]
    )
    
    # Prepare training data with advanced features
    enhanced_data = predictor.prepare_advanced_features(training_data)
    
    # Train ensemble models
    predictor.train_ensemble_models(enhanced_data)
    
    # Test predictions on recent data
    current_gw_data = enhanced_data[enhanced_data['gameweek'] == 20]
    predictions = predictor.predict_with_ensemble(current_gw_data)
    
    logger.info(f"Generated {len(predictions)} predictions")
    logger.info(f"Prediction range: {predictions.min():.2f} - {predictions.max():.2f}")
    
    # Save models
    predictor.save_models()
    
    return predictor

if __name__ == "__main__":
    main()
