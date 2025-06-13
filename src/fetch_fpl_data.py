#!/usr/bin/env python3
"""
FPL Data Fetcher

This module fetches Fantasy Premier League data from the official API,
processes it, and saves it for further analysis.
"""

import requests
import json
import pandas as pd
import os
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FPLDataFetcher:
    """Fetches and processes FPL data from the official API"""
    
    def __init__(self):
        self.base_url = "https://fantasy.premierleague.com/api/bootstrap-static/"
        self.raw_data_dir = "data/raw"
        self.processed_data_dir = "data/processed"
        
        # Ensure directories exist
        os.makedirs(self.raw_data_dir, exist_ok=True)
        os.makedirs(self.processed_data_dir, exist_ok=True)
    
    def fetch_data(self):
        """Fetch raw data from FPL API"""
        try:
            logger.info("Fetching data from FPL API...")
            response = requests.get(self.base_url)
            response.raise_for_status()
            
            data = response.json()
            
            # Save raw data with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"fpl_data_{timestamp}.json"
            filepath = os.path.join(self.raw_data_dir, filename)
            
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            
            # Also save as latest
            latest_filepath = os.path.join(self.raw_data_dir, "fpl_data_latest.json")
            with open(latest_filepath, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Raw data saved to {filepath}")
            return data
            
        except requests.RequestException as e:
            logger.error(f"Error fetching data: {e}")
            raise
    
    def process_players_data(self, raw_data):
        """Process player data into a clean DataFrame"""
        logger.info("Processing player data...")
        
        players = raw_data['elements']
        teams = {team['id']: team['name'] for team in raw_data['teams']}
        positions = {pos['id']: pos['singular_name'] for pos in raw_data['element_types']}
        
        # Create team strength lookup
        team_strength = {}
        for team in raw_data['teams']:
            team_strength[team['id']] = {
                'strength_overall_home': team['strength_overall_home'],
                'strength_overall_away': team['strength_overall_away'],
                'strength_attack_home': team['strength_attack_home'],
                'strength_attack_away': team['strength_attack_away'],
                'strength_defence_home': team['strength_defence_home'],
                'strength_defence_away': team['strength_defence_away']
            }
        
        # Create team strength mapping for FDR calculations
        team_strength = {}
        for team in raw_data['teams']:
            team_strength[team['id']] = {
                'name': team['name'],
                'strength_overall_home': team['strength_overall_home'],
                'strength_overall_away': team['strength_overall_away'],
                'strength_attack_home': team['strength_attack_home'],
                'strength_attack_away': team['strength_attack_away'],
                'strength_defence_home': team['strength_defence_home'],
                'strength_defence_away': team['strength_defence_away']
            }
        
        # Calculate FDR (Fixture Difficulty Rating) based on team strengths
        def calculate_fdr(team_id):
            """Calculate Fixture Difficulty Rating for a team"""
            team_data = team_strength[team_id]
            
            # Normalize strength values (higher strength = easier fixtures for that team)
            # FDR should be inverse - higher FDR = more difficult
            avg_attack = (team_data['strength_attack_home'] + team_data['strength_attack_away']) / 2
            avg_defence = (team_data['strength_defence_home'] + team_data['strength_defence_away']) / 2
            avg_overall = (team_data['strength_overall_home'] + team_data['strength_overall_away']) / 2
            
            # Convert to FDR scale (1-5, where 5 is most difficult)
            # Lower team strength = higher FDR (more difficult for opponents)
            fdr_attack = max(1, min(5, 6 - (avg_attack / 300)))  # Scale to 1-5
            fdr_defence = max(1, min(5, 6 - (avg_defence / 300)))
            fdr_overall = max(1, min(5, 6 - (avg_overall / 300)))
            
            return {
                'fdr_attack': round(fdr_attack, 2),
                'fdr_defence': round(fdr_defence, 2), 
                'fdr_overall': round(fdr_overall, 2)
            }
        
        # Extract relevant player features
        processed_players = []
        
        for player in players:
            team_fdr = calculate_fdr(player['team'])
            
            processed_player = {
                'id': player['id'],
                'name': f"{player['first_name']} {player['second_name']}",
                'web_name': player['web_name'],
                'team': teams[player['team']],
                'team_id': player['team'],
                'position': positions[player['element_type']],
                'cost': player['now_cost'] / 10.0,  # Convert to actual price
                'total_points': player['total_points'],
                'form': float(player['form']) if player['form'] else 0.0,
                'points_per_game': float(player['points_per_game']) if player['points_per_game'] else 0.0,
                'minutes': player['minutes'],
                'goals_scored': player['goals_scored'],
                'assists': player['assists'],
                'clean_sheets': player['clean_sheets'],
                'goals_conceded': player['goals_conceded'],
                'own_goals': player['own_goals'],
                'penalties_saved': player['penalties_saved'],
                'penalties_missed': player['penalties_missed'],
                'yellow_cards': player['yellow_cards'],
                'red_cards': player['red_cards'],
                'saves': player['saves'],
                'bonus': player['bonus'],
                'bps': player['bps'],
                'influence': float(player['influence']) if player['influence'] else 0.0,
                'creativity': float(player['creativity']) if player['creativity'] else 0.0,
                'threat': float(player['threat']) if player['threat'] else 0.0,
                'ict_index': float(player['ict_index']) if player['ict_index'] else 0.0,
                'selected_by_percent': float(player['selected_by_percent']),
                'cost': player['now_cost'] / 10.0,  # Convert to actual price
                'total_points': player['total_points'],
                'form': float(player['form']) if player['form'] else 0.0,
                'points_per_game': float(player['points_per_game']) if player['points_per_game'] else 0.0,
                'minutes': player['minutes'],
                'goals_scored': player['goals_scored'],
                'assists': player['assists'],
                'clean_sheets': player['clean_sheets'],
                'goals_conceded': player['goals_conceded'],
                'own_goals': player['own_goals'],
                'penalties_saved': player['penalties_saved'],
                'penalties_missed': player['penalties_missed'],
                'yellow_cards': player['yellow_cards'],
                'red_cards': player['red_cards'],
                'saves': player['saves'],
                'bonus': player['bonus'],
                'bps': player['bps'],
                'influence': float(player['influence']) if player['influence'] else 0.0,
                'creativity': float(player['creativity']) if player['creativity'] else 0.0,
                'threat': float(player['threat']) if player['threat'] else 0.0,
                'ict_index': float(player['ict_index']) if player['ict_index'] else 0.0,
                'selected_by_percent': float(player['selected_by_percent']),
                'value_form': float(player['value_form']) if player['value_form'] else 0.0,
                'value_season': float(player['value_season']) if player['value_season'] else 0.0,
                'transfers_in': player['transfers_in'],
                'transfers_out': player['transfers_out'],
                'transfers_in_event': player['transfers_in_event'],
                'transfers_out_event': player['transfers_out_event'],
                # FDR (Fixture Difficulty Rating) data
                'fdr_attack': team_fdr['fdr_attack'],
                'fdr_defence': team_fdr['fdr_defence'],
                'fdr_overall': team_fdr['fdr_overall'],
                # Team strength data for reference
                'team_strength_attack': (team_strength[player['team']]['strength_attack_home'] + 
                                       team_strength[player['team']]['strength_attack_away']) / 2,
                'team_strength_defence': (team_strength[player['team']]['strength_defence_home'] + 
                                        team_strength[player['team']]['strength_defence_away']) / 2
            }
            processed_players.append(processed_player)
        
        df = pd.DataFrame(processed_players)
        
        # Add derived features
        df['minutes_per_game'] = df['minutes'] / max(1, len(raw_data['events']))
        df['cost_efficiency'] = df['total_points'] / df['cost']
        df['form_per_cost'] = df['form'] / df['cost']
        
        # Position encoding for modeling
        position_mapping = {'Goalkeeper': 1, 'Defender': 2, 'Midfielder': 3, 'Forward': 4}
        df['position_encoded'] = df['position'].map(position_mapping)
        
        return df
    
    def save_processed_data(self, df):
        """Save processed data to CSV"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"fpl_players_{timestamp}.csv"
        filepath = os.path.join(self.processed_data_dir, filename)
        
        df.to_csv(filepath, index=False)
        
        # Also save as latest
        latest_filepath = os.path.join(self.processed_data_dir, "fpl_players_latest.csv")
        df.to_csv(latest_filepath, index=False)
        
        logger.info(f"Processed data saved to {filepath}")
        logger.info(f"Data shape: {df.shape}")
        logger.info(f"Columns: {list(df.columns)}")
        
        return filepath
    
    def run(self):
        """Run the complete data fetching and processing pipeline"""
        try:
            # Fetch raw data
            raw_data = self.fetch_data()
            
            # Process player data
            players_df = self.process_players_data(raw_data)
            
            # Save processed data
            self.save_processed_data(players_df)
            
            logger.info("Data fetching and processing completed successfully!")
            return players_df
            
        except Exception as e:
            logger.error(f"Error in data pipeline: {e}")
            raise

def main():
    """Main function to run the data fetcher"""
    fetcher = FPLDataFetcher()
    players_df = fetcher.run()
    
    # Display summary
    print("\n" + "="*50)
    print("FPL DATA SUMMARY")
    print("="*50)
    print(f"Total players: {len(players_df)}")
    print(f"Positions: {players_df['position'].value_counts().to_dict()}")
    print(f"Average cost: £{players_df['cost'].mean():.1f}m")
    print(f"Top scorer: {players_df.loc[players_df['total_points'].idxmax(), 'name']} ({players_df['total_points'].max()} pts)")
    print("="*50)

if __name__ == "__main__":
    main()
