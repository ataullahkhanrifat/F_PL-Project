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
        self.fixtures_url = "https://fantasy.premierleague.com/api/fixtures/"
        self.raw_data_dir = "data/raw"
        self.processed_data_dir = "data/processed"
        
        # Ensure directories exist
        os.makedirs(self.raw_data_dir, exist_ok=True)
        os.makedirs(self.processed_data_dir, exist_ok=True)
        
        # Cache for team strength data
        self.team_strength_cache = {}
        self.current_gameweek = None
    
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
    
    def fetch_fixtures(self):
        """Fetch fixtures data from FPL API"""
        try:
            logger.info("Fetching fixtures from FPL API...")
            response = requests.get(self.fixtures_url)
            response.raise_for_status()
            
            fixtures_data = response.json()
            
            # Save fixtures data with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"fpl_fixtures_{timestamp}.json"
            filepath = os.path.join(self.raw_data_dir, filename)
            
            with open(filepath, 'w') as f:
                json.dump(fixtures_data, f, indent=2)
            
            # Also save as latest
            latest_filepath = os.path.join(self.raw_data_dir, "fpl_fixtures_latest.json")
            with open(latest_filepath, 'w') as f:
                json.dump(fixtures_data, f, indent=2)
            
            logger.info(f"Fixtures data saved to {filepath}")
            return fixtures_data
            
        except requests.RequestException as e:
            logger.error(f"Error fetching fixtures: {e}")
            raise
    
    def calculate_team_fdr_from_fixtures(self, fixtures_data, teams_data, upcoming_gameweeks=5):
        """Calculate FDR for each team based on upcoming fixtures"""
        logger.info(f"Calculating FDR for next {upcoming_gameweeks} gameweeks...")
        
        # Get current gameweek
        current_gw = self.get_current_gameweek(fixtures_data)
        if current_gw is None:
            logger.warning("Could not determine current gameweek, using gameweek 1")
            current_gw = 1
        
        # Create team strength lookup
        team_strength = {}
        for team in teams_data:
            team_strength[team['id']] = {
                'name': team['name'],
                'code': team['code'],
                'strength': team.get('strength', 1000),  # Overall team strength
                'strength_overall_home': team.get('strength_overall_home', 1000),
                'strength_overall_away': team.get('strength_overall_away', 1000),
                'strength_attack_home': team.get('strength_attack_home', 1000),
                'strength_attack_away': team.get('strength_attack_away', 1000),
                'strength_defence_home': team.get('strength_defence_home', 1000),
                'strength_defence_away': team.get('strength_defence_away', 1000)
            }
        
        # Calculate FDR for each team
        team_fdr = {}
        
        for team_id in team_strength.keys():
            upcoming_fixtures = []
            
            # Get upcoming fixtures for this team
            for fixture in fixtures_data:
                if (fixture['event'] and 
                    fixture['event'] >= current_gw and 
                    fixture['event'] < current_gw + upcoming_gameweeks):
                    
                    if fixture['team_h'] == team_id:
                        # Home fixture
                        opponent_id = fixture['team_a']
                        is_home = True
                    elif fixture['team_a'] == team_id:
                        # Away fixture
                        opponent_id = fixture['team_h']
                        is_home = False
                    else:
                        continue
                    
                    if opponent_id in team_strength:
                        opponent = team_strength[opponent_id]
                        
                        # Calculate FDR based on opponent strength
                        if is_home:
                            # When playing at home, opponent's away strength determines difficulty
                            attack_difficulty = self.strength_to_fdr(opponent['strength_attack_away'])
                            defence_difficulty = self.strength_to_fdr(opponent['strength_defence_away'])
                            overall_difficulty = self.strength_to_fdr(opponent['strength_overall_away'])
                        else:
                            # When playing away, opponent's home strength determines difficulty
                            attack_difficulty = self.strength_to_fdr(opponent['strength_attack_home'])
                            defence_difficulty = self.strength_to_fdr(opponent['strength_defence_home'])
                            overall_difficulty = self.strength_to_fdr(opponent['strength_overall_home'])
                        
                        upcoming_fixtures.append({
                            'gameweek': fixture['event'],
                            'opponent': opponent['name'],
                            'is_home': is_home,
                            'fdr_attack': attack_difficulty,
                            'fdr_defence': defence_difficulty,
                            'fdr_overall': overall_difficulty
                        })
            
            # Calculate average FDR for the team
            if upcoming_fixtures:
                avg_fdr_attack = sum(f['fdr_attack'] for f in upcoming_fixtures) / len(upcoming_fixtures)
                avg_fdr_defence = sum(f['fdr_defence'] for f in upcoming_fixtures) / len(upcoming_fixtures)
                avg_fdr_overall = sum(f['fdr_overall'] for f in upcoming_fixtures) / len(upcoming_fixtures)
                
                team_fdr[team_id] = {
                    'fdr_attack_avg': round(avg_fdr_attack, 2),
                    'fdr_defence_avg': round(avg_fdr_defence, 2),
                    'fdr_overall_avg': round(avg_fdr_overall, 2),
                    'fixtures_count': len(upcoming_fixtures),
                    'upcoming_fixtures': upcoming_fixtures[:upcoming_gameweeks]  # Limit to requested gameweeks
                }
            else:
                # No fixtures found, use neutral FDR
                team_fdr[team_id] = {
                    'fdr_attack_avg': 3.0,
                    'fdr_defence_avg': 3.0,
                    'fdr_overall_avg': 3.0,
                    'fixtures_count': 0,
                    'upcoming_fixtures': []
                }
        
        return team_fdr
    
    def strength_to_fdr(self, strength):
        """Convert team strength to FDR scale (1-5)"""
        # FPL strength values are typically 1000-1500
        # Higher strength = stronger team = higher difficulty for opponents
        # Convert to 1-5 scale where 5 = most difficult
        
        if strength >= 1400:
            return 5  # Very difficult
        elif strength >= 1300:
            return 4  # Difficult  
        elif strength >= 1200:
            return 3  # Average
        elif strength >= 1100:
            return 2  # Easy
        else:
            return 1  # Very easy
    
    def get_current_gameweek(self, fixtures_data):
        """Determine current gameweek from fixtures"""
        current_time = datetime.now()
        
        for fixture in fixtures_data:
            if fixture['finished'] is False and fixture['kickoff_time']:
                kickoff = datetime.fromisoformat(fixture['kickoff_time'].replace('Z', '+00:00'))
                if kickoff > current_time:
                    return fixture['event']
        
        # If no upcoming fixtures found, find the latest finished gameweek
        latest_gw = 1
        for fixture in fixtures_data:
            if fixture['finished'] is True and fixture['event']:
                latest_gw = max(latest_gw, fixture['event'])
        
        return latest_gw + 1  # Next gameweek
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
