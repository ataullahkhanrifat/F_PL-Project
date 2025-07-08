#!/usr/bin/env python3
"""
FPL Squad Optimizer

This module uses linear programming to find the optimal 15-player squad
within budget constraints and position requirements.
"""

import pandas as pd
import numpy as np
from pulp import *
import pickle
import os
import logging

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
        
    def load_model(self):
        """Load the trained prediction model"""
        try:
            if os.path.exists(self.model_path):
                with open(self.model_path, 'rb') as f:
                    self.model = pickle.load(f)
                logger.info("Model loaded successfully")
            else:
                logger.warning(f"Model not found at {self.model_path}. Using form as prediction.")
                self.model = None
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            self.model = None
    
    def predict_points(self, players_df):
        """Predict points for all players with FDR integration"""
        if self.model is not None:
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
                
                logger.info("Used trained model for predictions")
                
            except Exception as e:
                logger.warning(f"Model prediction failed: {e}. Using fallback prediction.")
                # Fallback to form-based prediction
                players_df['predicted_points'] = players_df['form'] * 2.5
        else:
            # Fallback prediction based on form and recent performance
            players_df['predicted_points'] = players_df['form'] * 2.5
        
        # Apply FDR adjustments if enabled
        if self.use_fdr and 'fdr_overall' in players_df.columns:
            players_df = self.apply_fdr_adjustments(players_df)
        
        return players_df
    
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
        """Prepare final points for optimization including FDR adjustments"""
        # Start with predicted points
        players_df['weighted_points'] = players_df['predicted_points'].copy()
        
        # Add FDR-adjusted value if available
        if 'fdr_adjusted_value' in players_df.columns:
            players_df['fdr_value_score'] = players_df['fdr_adjusted_value'] * players_df['cost']
            players_df['weighted_points'] = players_df['fdr_value_score']
        
        # Add popularity factor (slight boost for highly selected players)
        players_df['popularity_factor'] = 1 + (players_df['selected_by_percent'] / 100) * 0.05
        players_df['final_points'] = players_df['weighted_points'] * players_df['popularity_factor']
        
        return players_df

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
