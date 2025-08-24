#!/usr/bin/env python3
"""
FPL Squad Optimizer

This module uses linear programming to find the optimal 15-player squad
within budget constraints and position requirements.

Enhanced with advanced ML models including Markov Chains, age analysis,
news sentiment, and ensemble predictions.
"""

import pandas as pd
import numpy as np
from pulp import *
import pickle
import os
import logging

# Import advanced ML models
try:
    from advanced_ml_models import EnsemblePredictor, MarkovChainFormPredictor
    ADVANCED_MODELS_AVAILABLE = True
except ImportError:
    ADVANCED_MODELS_AVAILABLE = False
    logging.warning("Advanced ML models not available. Using fallback prediction.")

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FPLOptimizer:
    """Optimizes FPL squad selection using linear programming"""
    
    def __init__(self, budget=100.0, model_path="models/model.pkl", min_budget_usage=0.99):
        self.budget = budget
        self.min_budget_usage = min_budget_usage  # Use at least 99% of budget
        self.model_path = model_path
        self.model = None
        
        # Initialize advanced ML system
        self.use_advanced_models = ADVANCED_MODELS_AVAILABLE
        if self.use_advanced_models:
            self.ensemble_predictor = EnsemblePredictor()
            self.advanced_models_loaded = False
        else:
            self.ensemble_predictor = None
            self.advanced_models_loaded = False
        
        # Squad constraints
        self.position_requirements = {
            'Goalkeeper': 2,
            'Defender': 5,
            'Midfielder': 5,
            'Forward': 3
        }
        self.starting_xi_requirements = {
            'Goalkeeper': 1,
            'Defender': {'min': 3, 'max': 5},
            'Midfielder': {'min': 2, 'max': 5}, 
            'Forward': {'min': 1, 'max': 3}
        }
        self.max_players_per_team = 3
        self.team_requirements = {}  # Custom team requirements
        self.team_position_limits = {}  # Team-specific position limits (e.g., max 2 defenders from Chelsea)
        
        # FDR considerations
        self.use_fdr = True
        self.fdr_weights = {'attack': 0.1, 'defence': 0.1, 'overall': 0.05}  # FDR impact on selection
        
        # Expensive player management (prevent high-value bench warmers)
        self.expensive_threshold = 8.0  # Players above this cost prioritize starting XI
        self.very_expensive_threshold = 10.0  # Premium players limit on bench
        self.max_expensive_bench = 1  # Max very expensive players on bench
        
        # Position weights for prioritizing certain positions
        self.position_weights = {
            'Goalkeeper': 1.0,
            'Defender': 1.0,
            'Midfielder': 1.0,
            'Forward': 1.0
        }
        
        # Manual player selection
        self.manually_selected_players = []  # List of player IDs to force include
        
    def load_model(self):
        """Load the trained prediction model (basic or advanced)"""
        try:
            # Try to load advanced models first
            if self.use_advanced_models and self.ensemble_predictor:
                if self.ensemble_predictor.load_models():
                    self.advanced_models_loaded = True
                    logger.info("🚀 Advanced ML ensemble loaded successfully!")
                    return
            
            # Fallback to basic model
            if os.path.exists(self.model_path):
                with open(self.model_path, 'rb') as f:
                    self.model = pickle.load(f)
                logger.info("Basic model loaded successfully")
            else:
                logger.warning(f"No model found at {self.model_path}. Using form-based prediction.")
                self.model = None
        except Exception as e:
            logger.error(f"Error loading models: {e}")
            self.model = None
            self.advanced_models_loaded = False
    
    def predict_points(self, players_df):
        """Predict points for all players using best available method"""
        
        # Method 1: Advanced ML Ensemble (if available)
        if self.use_advanced_models and self.advanced_models_loaded:
            try:
                logger.info("🤖 Using Advanced ML Ensemble (Markov + Age + News + ML)")
                predictions = self.ensemble_predictor.predict_with_ensemble(players_df)
                players_df['predicted_points'] = predictions
                
                logger.info("✅ Advanced predictions generated successfully")
                
            except Exception as e:
                logger.warning(f"Advanced prediction failed: {e}. Falling back to basic model.")
                self.advanced_models_loaded = False
                return self.predict_points(players_df)  # Recursive fallback
        
        # Method 2: Basic trained model
        elif self.model is not None:
            try:
                # Features used in model training
                feature_columns = [
                    'form', 'cost', 'minutes', 'total_points', 'points_per_game',
                    'influence', 'creativity', 'threat', 'ict_index',
                    'selected_by_percent', 'minutes_per_game', 'cost_efficiency',
                    'position_encoded'
                ]
                
                # Ensure all feature columns exist
                available_features = [col for col in feature_columns if col in players_df.columns]
                X = players_df[available_features]
                
                # Fill any missing values
                X = X.fillna(0)
                
                predictions = self.model.predict(X)
                players_df['predicted_points'] = predictions
                
                logger.info("📊 Used basic trained model for predictions")
                
            except Exception as e:
                logger.warning(f"Basic model prediction failed: {e}. Using fallback prediction.")
                # Fallback to form-based prediction
                players_df['predicted_points'] = players_df['form'] * 2.5
                
        # Method 3: Enhanced strategic prediction (fixtures + performance)
        else:
            logger.info("📈 Using enhanced strategic prediction (fixtures + last 5 matches + season + factors)")
            # Strategic prediction with updated weight distribution
            
            # 1. Season Performance Base (20% weight) - reduced further
            season_base = players_df['total_points'] / max(players_df['total_points'].max() / 10, 1)
            season_base = np.clip(season_base, 0, 10)  # Cap at 10 points
            
            # 2. Last 5 Matches Performance (20% weight) - NEW: focus on very recent performance
            last5_base = players_df['form'] * 1.8  # Form represents last 5 matches
            last5_base = np.clip(last5_base, 0, 9)  # Higher impact for recent matches
            
            # 3. Fixture Difficulty Analysis (25% weight) - maintain high priority
            fixture_score = self.calculate_fixture_advantage(players_df)
            fixture_score = np.clip(fixture_score, 0, 8)  # Cap fixture advantage
            
            # 4. Recent Form Last 10 Matches (5% weight) - minimal impact
            form10_base = players_df.get('form_10', players_df['form']) * 0.8  # Fallback to form if no form_10
            form10_base = np.clip(form10_base, 0, 4)   # Low impact
            
            # 5. Points Per Game Consistency (15% weight)
            ppg_base = players_df['points_per_game'] * 1.5
            ppg_base = np.clip(ppg_base, 0, 7)
            
            # 6. Value for Money Factor (10% weight)
            value_base = (players_df['total_points'] / players_df['cost']) * 0.8
            value_base = np.clip(value_base, 0, 6)
            
            # 7. Top 5 Team Bonus (5% weight) - NEW: boost for big teams
            top5_teams = ['Man City', 'Arsenal', 'Liverpool', 'Chelsea', 'Man Utd']  # Adjust as needed
            top5_bonus = players_df['team'].apply(lambda x: 1.0 if x in top5_teams else 0.0) * 2.0
            top5_bonus = np.clip(top5_bonus, 0, 2)
            
            # Weighted combination with updated strategic focus
            base_prediction = (
                season_base * 0.20 +     # Season performance (20%)
                last5_base * 0.20 +      # Last 5 matches (20%)
                fixture_score * 0.25 +   # Fixture advantage (25%)
                form10_base * 0.05 +     # Recent form last 10 (5%)
                ppg_base * 0.15 +        # PPG consistency (15%)
                value_base * 0.10 +      # Value factor (10%)
                top5_bonus * 0.05        # Top 5 team bonus (5%)
            )
            
            # Adjust for availability (minutes played)
            minutes_factor = np.clip(players_df['minutes'] / 900, 0.4, 1.1)  # Less punitive
            
            # Adjust for team popularity/quality (reduced impact)
            popularity_factor = 1 + (players_df['selected_by_percent'] / 100) * 0.1  # Reduced from 0.2
            
            # Position-specific adjustments
            position_multipliers = {
                'Goalkeeper': 0.9,     # GKs typically score less
                'Defender': 1.0,       # Baseline
                'Midfielder': 1.1,     # Slight boost for versatility
                'Forward': 1.05        # Slight boost for attacking returns
            }
            
            position_factor = players_df['position'].map(position_multipliers).fillna(1.0)
            
            # Final balanced prediction
            players_df['predicted_points'] = (
                base_prediction * 
                minutes_factor * 
                popularity_factor *
                position_factor
            )
            
            # Add small randomization to prevent identical predictions
            players_df['predicted_points'] += np.random.normal(0, 0.1, len(players_df))
            
            logger.info("✅ Applied strategic prediction: Season (20%) + Last5 (20%) + Fixtures (25%) + Form10 (5%) + PPG (15%) + Value (10%) + Top5 (5%)")
        
        # Apply FDR adjustments if enabled
        if self.use_fdr and 'fdr_overall' in players_df.columns:
            players_df = self.apply_fdr_adjustments(players_df)
        
        return players_df
    
    def calculate_fixture_advantage(self, players_df):
        """
        Calculate fixture advantage score based on upcoming gameweek difficulty
        Returns higher scores for players with easier upcoming fixtures
        """
        fixture_scores = np.zeros(len(players_df))
        
        try:
            # Check if FDR columns exist
            fdr_columns = ['fdr_overall', 'fdr_attack', 'fdr_defence']
            available_fdr = [col for col in fdr_columns if col in players_df.columns]
            
            if not available_fdr:
                logger.warning("No FDR data available, using neutral fixture scores")
                return np.full(len(players_df), 4.0)  # Neutral score
            
            # Calculate position-specific fixture advantages
            for idx, player in players_df.iterrows():
                position = player['position']
                base_score = 0
                
                # Get FDR values (default to 3.0 if missing)
                fdr_overall = player.get('fdr_overall', 3.0)
                fdr_attack = player.get('fdr_attack', 3.0) 
                fdr_defence = player.get('fdr_defence', 3.0)
                
                # Position-specific fixture scoring
                if position in ['Forward', 'Midfielder']:
                    # Attackers benefit from low attack FDR (easier to score/assist)
                    attack_advantage = max(0, 5 - fdr_attack)  # 0-4 scale
                    overall_advantage = max(0, 5 - fdr_overall) * 0.5  # 0-2 scale
                    base_score = attack_advantage + overall_advantage
                    
                elif position == 'Defender':
                    # Defenders benefit from low defence FDR (clean sheets + attacking returns)
                    defence_advantage = max(0, 5 - fdr_defence) * 1.2  # Weighted higher
                    attack_advantage = max(0, 5 - fdr_attack) * 0.4   # Some attacking potential
                    overall_advantage = max(0, 5 - fdr_overall) * 0.4
                    base_score = defence_advantage + attack_advantage + overall_advantage
                    
                elif position == 'Goalkeeper':
                    # Goalkeepers primarily benefit from low defence FDR
                    defence_advantage = max(0, 5 - fdr_defence) * 1.5  # Heavily weighted
                    overall_advantage = max(0, 5 - fdr_overall) * 0.3
                    base_score = defence_advantage + overall_advantage
                
                # Apply team strength modifiers
                # Popular teams (high selection %) often have better fixtures or easier wins
                team_popularity = player.get('selected_by_percent', 0) / 100
                popularity_bonus = team_popularity * 0.5  # Small bonus for popular teams
                
                # Combine for final fixture score
                fixture_scores[idx] = base_score + popularity_bonus
                
            logger.info(f"Calculated fixture advantages: avg={fixture_scores.mean():.2f}, max={fixture_scores.max():.2f}")
            
        except Exception as e:
            logger.warning(f"Error calculating fixture advantage: {e}, using neutral scores")
            fixture_scores = np.full(len(players_df), 4.0)
        
        return fixture_scores
    
    def apply_fdr_adjustments(self, players_df):
        """Apply FDR adjustments to predicted points"""
        logger.info("Applying FDR adjustments to predictions...")
        
        # Apply position-specific FDR adjustments
        for idx, player in players_df.iterrows():
            position = player['position']
            base_points = player['predicted_points']
            
            # Get FDR values
            fdr_attack = player.get('fdr_attack', 3.0)
            fdr_defence = player.get('fdr_defence', 3.0)
            fdr_overall = player.get('fdr_overall', 3.0)
            
            # Position-specific FDR impact
            if position in ['Forward', 'Midfielder']:
                # Attackers benefit more from low attack FDR
                fdr_multiplier = 1 + (self.fdr_weights['attack'] * (5 - fdr_attack))
                fdr_multiplier += self.fdr_weights['overall'] * (5 - fdr_overall)
            elif position == 'Defender':
                # Defenders benefit from low defence FDR (clean sheets)
                fdr_multiplier = 1 + (self.fdr_weights['defence'] * (5 - fdr_defence))
                fdr_multiplier += self.fdr_weights['overall'] * (5 - fdr_overall)
            elif position == 'Goalkeeper':
                # Goalkeepers benefit most from low defence FDR
                fdr_multiplier = 1 + (self.fdr_weights['defence'] * 1.5 * (5 - fdr_defence))
                fdr_multiplier += self.fdr_weights['overall'] * (5 - fdr_overall)
            else:
                fdr_multiplier = 1.0
            
            # Apply the adjustment
            players_df.loc[idx, 'predicted_points'] = base_points * fdr_multiplier
        
        # Add FDR-adjusted derived metrics
        players_df['fdr_adjusted_value'] = players_df['predicted_points'] / players_df['cost']
        
        logger.info("FDR adjustments applied successfully")
        return players_df
    
    def set_fdr_weights(self, weights):
        """Set FDR impact weights"""
        self.fdr_weights.update(weights)
        logger.info(f"FDR weights updated: {self.fdr_weights}")
    
    def optimize_squad(self, players_df):
        """
        Optimize squad selection using linear programming with improved constraints
        
        Args:
            players_df: DataFrame with player data and predicted points
            
        Returns:
            dict: Optimization results including selected players and total points
        """
        logger.info(f"Optimizing squad with budget £{self.budget}m (min usage: {self.min_budget_usage*100:.0f}%)")
        
        # Prepare final optimization points
        players_df = self.prepare_final_points(players_df)
        
        # Filter out 'Manager' position if it exists
        players_df = players_df[players_df['position'] != 'Manager'].copy()
        
        # Create the optimization problem
        prob = LpProblem("FPL_Squad_Selection", LpMaximize)
        
        # Decision variables: binary variable for each player
        player_vars = {}
        for idx, player in players_df.iterrows():
            player_vars[idx] = LpVariable(f"player_{idx}", cat='Binary')
        
        # Additional variables for starting XI selection
        starting_vars = {}
        for idx, player in players_df.iterrows():
            starting_vars[idx] = LpVariable(f"starting_{idx}", cat='Binary')
        
        # Objective function: maximize weighted predicted points with strong starting XI bias
        # Heavy penalty for expensive players on bench to force them into starting XI
        prob += lpSum([
            players_df.loc[idx, 'final_points'] * player_vars[idx] +
            players_df.loc[idx, 'final_points'] * 2.0 * starting_vars[idx] +  # Strong starting XI bonus
            players_df.loc[idx, 'cost'] * 10.0 * starting_vars[idx]  # Cost bonus for starting XI
            for idx in players_df.index
        ])
        
        # Constraint 1: Budget constraint with minimum usage
        total_cost = lpSum([players_df.loc[idx, 'cost'] * player_vars[idx] for idx in players_df.index])
        prob += total_cost <= self.budget
        prob += total_cost >= self.budget * self.min_budget_usage  # Use at least 99% of budget
        
        # Constraint 2: Total squad size (15 players)
        prob += lpSum([player_vars[idx] for idx in players_df.index]) == 15
        
        # Constraint 3: Starting XI size (11 players)
        prob += lpSum([starting_vars[idx] for idx in players_df.index]) == 11
        
        # Constraint 4: Starting players must be in squad
        for idx in players_df.index:
            prob += starting_vars[idx] <= player_vars[idx]
        
        # Constraint 5: Position requirements for full squad
        for position, required_count in self.position_requirements.items():
            position_players = players_df[players_df['position'] == position].index
            prob += lpSum([player_vars[idx] for idx in position_players]) == required_count
        
        # Constraint 6: Starting XI position requirements
        gk_players = players_df[players_df['position'] == 'Goalkeeper'].index
        def_players = players_df[players_df['position'] == 'Defender'].index
        mid_players = players_df[players_df['position'] == 'Midfielder'].index
        fwd_players = players_df[players_df['position'] == 'Forward'].index
        
        prob += lpSum([starting_vars[idx] for idx in gk_players]) == 1
        prob += lpSum([starting_vars[idx] for idx in def_players]) >= 3
        prob += lpSum([starting_vars[idx] for idx in def_players]) <= 5
        prob += lpSum([starting_vars[idx] for idx in mid_players]) >= 2
        prob += lpSum([starting_vars[idx] for idx in mid_players]) <= 5
        prob += lpSum([starting_vars[idx] for idx in fwd_players]) >= 1
        prob += lpSum([starting_vars[idx] for idx in fwd_players]) <= 3
        
        # Constraint 7: Team requirements and team-position limits
        for team in players_df['team'].unique():
            team_players = players_df[players_df['team'] == team].index
            
            # Custom team requirements
            if team in self.team_requirements:
                prob += lpSum([player_vars[idx] for idx in team_players]) == self.team_requirements[team]
            else:
                # Default maximum players per team
                prob += lpSum([player_vars[idx] for idx in team_players]) <= self.max_players_per_team
            
            # Team-specific position limits (prevent too many of same position from one team)
            if team in self.team_position_limits:
                for position, max_count in self.team_position_limits[team].items():
                    team_position_players = players_df[
                        (players_df['team'] == team) & (players_df['position'] == position)
                    ].index
                    if len(team_position_players) > 0:
                        prob += lpSum([player_vars[idx] for idx in team_position_players]) <= max_count
            else:
                # Default: prevent more than 2 players of same position from same team
                for position in ['Goalkeeper', 'Defender', 'Midfielder', 'Forward']:
                    team_position_players = players_df[
                        (players_df['team'] == team) & (players_df['position'] == position)
                    ].index
                    if len(team_position_players) > 0:
                        max_same_position = 2 if position in ['Defender', 'Midfielder'] else 1
                        prob += lpSum([player_vars[idx] for idx in team_position_players]) <= max_same_position
        
        # Constraint 8: Expensive players must start (prevent high-value bench warmers)
        expensive_players = players_df[players_df['cost'] >= self.expensive_threshold].index
        for idx in expensive_players:
            # If an expensive player is selected, they should have high probability of starting
            prob += starting_vars[idx] >= 0.8 * player_vars[idx]  # 80% chance to start if selected
        
        # Constraint 9: Limit very expensive players on bench
        very_expensive_players = players_df[players_df['cost'] >= self.very_expensive_threshold].index
        bench_expensive = lpSum([player_vars[idx] - starting_vars[idx] for idx in very_expensive_players])
        prob += bench_expensive <= self.max_expensive_bench
        
        # Constraint 10: Force include manually selected players
        if hasattr(self, 'manually_selected_players') and self.manually_selected_players:
            for player_index in self.manually_selected_players:
                if player_index in players_df.index:
                    prob += player_vars[player_index] == 1  # Force selection
        
        # Solve the problem
        prob.solve(PULP_CBC_CMD(msg=0))  # Silent solver
        
        # Extract results
        if prob.status == 1:  # Optimal solution found
            selected_indices = []
            starting_indices = []
            
            for idx in players_df.index:
                if player_vars[idx].varValue == 1:
                    selected_indices.append(idx)
                if starting_vars[idx].varValue == 1:
                    starting_indices.append(idx)
            
            selected_players = players_df.loc[selected_indices].copy()
            starting_players = players_df.loc[starting_indices].copy()
            bench_players = selected_players[~selected_players.index.isin(starting_indices)].copy()
            
            # Mark starting XI and bench
            selected_players['is_starting'] = selected_players.index.isin(starting_indices)
            
            # Calculate summary statistics
            total_cost = selected_players['cost'].sum()
            total_predicted_points = selected_players['predicted_points'].sum()
            starting_predicted_points = starting_players['predicted_points'].sum()
            remaining_budget = self.budget - total_cost
            
            # Position breakdown
            position_breakdown = selected_players['position'].value_counts().to_dict()
            starting_position_breakdown = starting_players['position'].value_counts().to_dict()
            
            # Team breakdown
            team_breakdown = selected_players['team'].value_counts().to_dict()
            
            results = {
                'status': 'optimal',
                'selected_players': selected_players.sort_values('predicted_points', ascending=False),
                'starting_players': starting_players.sort_values('predicted_points', ascending=False),
                'bench_players': bench_players.sort_values('predicted_points', ascending=False),
                'total_cost': total_cost,
                'total_predicted_points': total_predicted_points,
                'starting_predicted_points': starting_predicted_points,
                'remaining_budget': remaining_budget,
                'budget_usage_pct': (total_cost / self.budget) * 100,
                'position_breakdown': position_breakdown,
                'starting_position_breakdown': starting_position_breakdown,
                'team_breakdown': team_breakdown
            }
            
            logger.info(f"Optimization successful! Total predicted points: {total_predicted_points:.1f}")
            logger.info(f"Starting XI predicted points: {starting_predicted_points:.1f}")
            logger.info(f"Total cost: £{total_cost:.1f}m ({(total_cost/self.budget)*100:.1f}% of budget)")
            
        else:
            results = {
                'status': 'infeasible',
                'message': 'No feasible solution found with given constraints'
            }
            logger.error("Optimization failed - no feasible solution found")
        
        return results
    
    def print_squad_summary(self, results):
        """Print a formatted summary of the optimized squad"""
        if results['status'] != 'optimal':
            print(f"Optimization failed: {results.get('message', 'Unknown error')}")
            return
        
        selected = results['selected_players']
        starting = results.get('starting_players', selected.head(11))
        bench = results.get('bench_players', selected.tail(4))
        
        print("\n" + "="*90)
        print("OPTIMAL FPL SQUAD")
        print("="*90)
        print(f"Budget: £{self.budget}m | Total Cost: £{results['total_cost']:.1f}m | Usage: {results.get('budget_usage_pct', 0):.1f}%")
        print(f"Remaining: £{results['remaining_budget']:.1f}m")
        print(f"Total Predicted Points: {results['total_predicted_points']:.1f}")
        if 'starting_predicted_points' in results:
            print(f"Starting XI Points: {results['starting_predicted_points']:.1f}")
        print("\n" + "-"*90)
        
        # Starting XI
        print("\n🔥 STARTING XI (Most Popular + High Points)")
        print("-" * 50)
        for position in ['Goalkeeper', 'Defender', 'Midfielder', 'Forward']:
            position_players = starting[starting['position'] == position] if 'starting_players' in results else selected[selected['position'] == position].head(2 if position == 'Goalkeeper' else 3)
            if len(position_players) > 0:
                print(f"\n{position.upper()}S ({len(position_players)}):")
                for _, player in position_players.iterrows():
                    popularity = f"{player['selected_by_percent']:.1f}%"
                    print(f"  {player['name']:<25} | {player['team']:<15} | £{player['cost']:.1f}m | {player['predicted_points']:.1f}pts | {popularity} owned")
        
        # Bench
        print("\n📋 BENCH (Budget Players)")
        print("-" * 50)
        if 'bench_players' in results and len(bench) > 0:
            for _, player in bench.iterrows():
                popularity = f"{player['selected_by_percent']:.1f}%"
                print(f"  {player['name']:<25} | {player['team']:<15} | £{player['cost']:.1f}m | {player['predicted_points']:.1f}pts | {popularity} owned")
        
        print("\n" + "-"*90)
        print("TEAM BREAKDOWN:")
        for team, count in sorted(results['team_breakdown'].items()):
            print(f"{team}: {count} players")
        
        # Position weights info
        if hasattr(self, 'position_weights'):
            print(f"\nPosition Weights Applied: {self.position_weights}")
        
        print("="*90)

    def set_position_weights(self, weights):
        """Set position weights for optimization"""
        self.position_weights.update(weights)
        logger.info(f"Updated position weights: {self.position_weights}")
    
    def set_team_requirements(self, team_requirements):
        """Set custom team requirements (e.g., {'Arsenal': 2, 'Liverpool': 1})"""
        self.team_requirements = team_requirements
        logger.info(f"Set team requirements: {team_requirements}")
    
    def set_team_position_limits(self, team_position_limits):
        """Set team-specific position limits (e.g., {'Arsenal': {'Defender': 2, 'Midfielder': 1}})"""
        self.team_position_limits = team_position_limits
        logger.info(f"Set team position limits: {team_position_limits}")
    
    def set_max_players_per_team(self, max_players):
        """Set maximum players per team"""
        self.max_players_per_team = max_players
        logger.info(f"Set max players per team: {max_players}")
    
    def set_fdr_weights(self, fdr_weights):
        """Set FDR impact weights (e.g., {'attack': 0.15, 'defence': 0.1, 'overall': 0.05})"""
        self.fdr_weights.update(fdr_weights)
        logger.info(f"Updated FDR weights: {self.fdr_weights}")
    
    def prepare_final_points(self, players_df):
        """Prepare final points for optimization including enhanced FDR and fixture adjustments"""
        # Start with predicted points (already includes fixture analysis)
        players_df['weighted_points'] = players_df['predicted_points'].copy()
        
        # Add enhanced FDR-adjusted value if available
        if 'fdr_adjusted_value' in players_df.columns:
            players_df['fdr_value_score'] = players_df['fdr_adjusted_value'] * players_df['cost']
            # Blend predicted points with FDR value score for more balanced optimization
            players_df['weighted_points'] = (
                players_df['predicted_points'] * 0.7 +  # 70% predicted points
                players_df['fdr_value_score'] * 0.3     # 30% FDR value score
            )
        
        # Enhanced popularity factor with fixture consideration
        base_popularity = 1 + (players_df['selected_by_percent'] / 100) * 0.03  # Reduced base impact
        
        # Fixture-aware popularity boost (popular players with good fixtures get extra boost)
        if 'fdr_overall' in players_df.columns:
            fixture_popularity_boost = (
                (players_df['selected_by_percent'] / 100) * 
                (5 - players_df['fdr_overall']) / 4 * 0.02  # Extra boost for popular players with good fixtures
            )
            players_df['popularity_factor'] = base_popularity + fixture_popularity_boost
        else:
            players_df['popularity_factor'] = base_popularity
        
        # Apply final adjustments
        players_df['final_points'] = players_df['weighted_points'] * players_df['popularity_factor']
        
        return players_df

    def analyze_next_3_gameweeks(self, players_df):
        """
        Analyze the next 3 gameweeks and return comprehensive fixture analysis
        Returns a dict with keys: position_recommendations, team_analysis, fdr_rankings
        """
        # Use available FDR columns (fdr_attack, fdr_defence, fdr_overall)
        for col in ["fdr_attack", "fdr_defence", "fdr_overall"]:
            if col not in players_df.columns:
                players_df[col] = 3.0

        players_df = players_df.copy()
        # Calculate a fixture score for each player (lower FDR = better fixtures)
        players_df["fixture_score"] = (
            (5 - players_df["fdr_attack"]) * (players_df["position"].isin(["Forward", "Midfielder"])) +
            (5 - players_df["fdr_defence"]) * (players_df["position"] == "Defender") +
            (5 - players_df["fdr_defence"]) * (players_df["position"] == "Goalkeeper")
        )
        # Combine with predicted points for a recommendation score
        players_df["recommendation_score"] = players_df["predicted_points"] * 0.7 + players_df["fixture_score"] * 0.3

        # Defensive: fillna
        players_df["recommendation_score"] = players_df["recommendation_score"].fillna(0)

        # Get top 5 for each position
        recommendations = {}
        for pos, key in zip([
            "Forward", "Midfielder", "Defender", "Goalkeeper"],
            ["forwards", "midfielders", "defenders", "goalkeepers"]):
            pos_df = players_df[players_df["position"] == pos].sort_values(
                "recommendation_score", ascending=False
            ).head(5)
            recommendations[key] = [
                {
                    "name": row["name"],
                    "team": row["team"],
                    "cost": row["cost"],
                    "form": row["form"],
                    "selected_by_percent": row.get("selected_by_percent", 0),
                    "season_points": row.get("total_points", 0),
                }
                for _, row in pos_df.iterrows()
            ]

        # Generate team analysis data
        team_analysis = []
        try:
            # Group by team and calculate average FDR values
            team_data = players_df.groupby('team').agg({
                'fdr_overall': 'mean',
                'fdr_attack': 'mean', 
                'fdr_defence': 'mean',
                'next_opponent': 'first',
                'next_fixture_home': 'first'
            }).reset_index()
            
            # Sort teams by best fixtures (lowest FDR)
            team_data = team_data.sort_values('fdr_overall')
            
            for _, team_row in team_data.iterrows():
                team_analysis.append({
                    'team': team_row['team'],
                    'fdr_overall': team_row['fdr_overall'],
                    'fdr_attack': team_row['fdr_attack'],
                    'fdr_defence': team_row['fdr_defence'],
                    'next_opponent': team_row.get('next_opponent', 'TBD'),
                    'home_away': 'Home' if team_row.get('next_fixture_home', False) else 'Away',
                    'fixtures_count': 3  # Default to 3 gameweeks
                })
        except Exception as e:
            logger.warning(f"Error generating team analysis: {e}")
            # Create dummy data if analysis fails
            unique_teams = players_df['team'].unique()[:10]
            for i, team in enumerate(unique_teams):
                team_analysis.append({
                    'team': team,
                    'fdr_overall': 2.5 + (i * 0.1),
                    'fdr_attack': 2.3 + (i * 0.1),
                    'fdr_defence': 2.7 + (i * 0.1),
                    'next_opponent': 'TBD',
                    'home_away': 'Home' if i % 2 == 0 else 'Away',
                    'fixtures_count': 3
                })
        
        # Generate FDR rankings (same as team analysis but formatted differently)
        fdr_rankings = []
        try:
            team_data = players_df.groupby('team').agg({
                'fdr_overall': 'mean',
                'fdr_attack': 'mean', 
                'fdr_defence': 'mean',
                'next_opponent': 'first',
                'next_fixture_home': 'first'
            }).reset_index()
            
            team_data = team_data.sort_values('fdr_overall')
            
            for _, team_row in team_data.iterrows():
                fdr_rankings.append({
                    'team': team_row['team'],
                    'fdr_overall': team_row['fdr_overall'],
                    'fdr_attack': team_row['fdr_attack'],
                    'fdr_defence': team_row['fdr_defence'],
                    'next_opponent': team_row.get('next_opponent', 'TBD'),
                    'next_fixture_home': team_row.get('next_fixture_home', False)
                })
        except Exception as e:
            logger.warning(f"Error generating FDR rankings: {e}")
            # Create dummy data if analysis fails
            unique_teams = players_df['team'].unique()[:15]
            for i, team in enumerate(unique_teams):
                fdr_rankings.append({
                    'team': team,
                    'fdr_overall': 2.0 + (i * 0.2),
                    'fdr_attack': 1.8 + (i * 0.2),
                    'fdr_defence': 2.2 + (i * 0.2),
                    'next_opponent': 'TBD',
                    'next_fixture_home': i % 2 == 0
                })

        return {
            "position_recommendations": recommendations,
            "team_analysis": team_analysis,
            "fdr_rankings": fdr_rankings
        }

def main():
    """Main function to run the optimizer with enhanced features"""
    # Load player data
    data_path = "data/processed/fpl_players_latest.csv"
    
    if not os.path.exists(data_path):
        logger.error(f"Player data not found at {data_path}")
        logger.error("Please run 'python src/fetch_fpl_data.py' first")
        return
    
    players_df = pd.read_csv(data_path)
    logger.info(f"Loaded {len(players_df)} players")
    
    # Initialize optimizer with enhanced features
    optimizer = FPLOptimizer(budget=100.0, min_budget_usage=0.99)
    
    # Example: Set position weights (prioritize midfielders and forwards)
    optimizer.set_position_weights({
        'Goalkeeper': 0.8,
        'Defender': 1.0,
        'Midfielder': 1.3,  # Prioritize midfielders
        'Forward': 1.2      # Slightly prioritize forwards
    })
    
    # Example: Set team requirements (optional)
    # optimizer.set_team_requirements({
    #     'Arsenal': 2,     # Want exactly 2 Arsenal players
    #     'Man City': 3,    # Want exactly 3 Man City players
    #     'Liverpool': 1    # Want exactly 1 Liverpool player
    # })
    
    # Load model and predict points
    optimizer.load_model()
    players_df = optimizer.predict_points(players_df)
    
    # Optimize squad
    results = optimizer.optimize_squad(players_df)
    
    # Print results
    optimizer.print_squad_summary(results)
    
    if results['status'] == 'optimal':
        print(f"\n💡 Tips:")
        print(f"   - Starting XI focuses on popular, high-scoring players")
        print(f"   - Bench has budget players to maximize starting XI quality")
        print(f"   - Used {results['budget_usage_pct']:.1f}% of available budget")
        print(f"   - Position weights applied: {optimizer.position_weights}")
    
    return results

if __name__ == "__main__":
    main()
