#!/usr/bin/env python3
"""
FPL Data Fetcher with FDR Integration

This module fetches Fantasy Premier League data from the official API,
processes it with Fixture Difficulty Ratings (FDR), and saves it for further analysis.
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
    """Fetches and processes FPL data from the official API with FDR integration"""
    
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
                try:
                    kickoff = datetime.fromisoformat(fixture['kickoff_time'].replace('Z', '+00:00'))
                    if kickoff > current_time:
                        return fixture['event']
                except:
                    continue
        
        # If no upcoming fixtures found, find the latest finished gameweek
        latest_gw = 1
        for fixture in fixtures_data:
            if fixture['finished'] is True and fixture['event']:
                latest_gw = max(latest_gw, fixture['event'])
        
        return latest_gw + 1  # Next gameweek
    
    def process_players_data(self, raw_data, fixtures_data=None, upcoming_gameweeks=5):
        """Process player data into a clean DataFrame with FDR integration"""
        logger.info("Processing player data...")
        
        players = raw_data['elements']
        teams = {team['id']: team['name'] for team in raw_data['teams']}
        positions = {pos['id']: pos['singular_name'] for pos in raw_data['element_types']}
        
        # Calculate FDR from fixtures if available
        team_fdr_data = {}
        if fixtures_data:
            team_fdr_data = self.calculate_team_fdr_from_fixtures(
                fixtures_data, raw_data['teams'], upcoming_gameweeks
            )
        
        # Create team strength lookup for fallback FDR
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
        
        # Extract relevant player features
        processed_players = []
        
        for player in players:
            team_id = player['team']
            
            # Get FDR data for this player's team
            if team_id in team_fdr_data:
                fdr_data = team_fdr_data[team_id]
                fdr_attack = fdr_data['fdr_attack_avg']
                fdr_defence = fdr_data['fdr_defence_avg']
                fdr_overall = fdr_data['fdr_overall_avg']
                fixtures_count = fdr_data['fixtures_count']
                upcoming_fixtures = fdr_data['upcoming_fixtures']
            else:
                # Fallback to basic FDR calculation from team strength
                team_data = team_strength[team_id]
                avg_attack = (team_data['strength_attack_home'] + team_data['strength_attack_away']) / 2
                avg_defence = (team_data['strength_defence_home'] + team_data['strength_defence_away']) / 2
                avg_overall = (team_data['strength_overall_home'] + team_data['strength_overall_away']) / 2
                
                fdr_attack = max(1, min(5, 6 - (avg_attack / 300)))
                fdr_defence = max(1, min(5, 6 - (avg_defence / 300)))
                fdr_overall = max(1, min(5, 6 - (avg_overall / 300)))
                fixtures_count = 0
                upcoming_fixtures = []
            
            processed_player = {
                'id': player['id'],
                'name': f"{player['first_name']} {player['second_name']}",
                'web_name': player['web_name'],
                'team': teams[team_id],
                'team_id': team_id,
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
                'value_form': float(player['value_form']) if player['value_form'] else 0.0,
                'value_season': float(player['value_season']) if player['value_season'] else 0.0,
                'transfers_in': player['transfers_in'],
                'transfers_out': player['transfers_out'],
                'transfers_in_event': player['transfers_in_event'],
                'transfers_out_event': player['transfers_out_event'],
                # FDR (Fixture Difficulty Rating) data
                'fdr_attack': round(fdr_attack, 2),
                'fdr_defence': round(fdr_defence, 2),
                'fdr_overall': round(fdr_overall, 2),
                'fixtures_count': fixtures_count,
                # Team strength data for reference
                'team_strength_attack': (team_strength[team_id]['strength_attack_home'] + 
                                       team_strength[team_id]['strength_attack_away']) / 2,
                'team_strength_defence': (team_strength[team_id]['strength_defence_home'] + 
                                        team_strength[team_id]['strength_defence_away']) / 2,
                # Upcoming fixtures summary
                'next_opponent': upcoming_fixtures[0]['opponent'] if upcoming_fixtures else 'TBD',
                'next_fixture_home': upcoming_fixtures[0]['is_home'] if upcoming_fixtures else None,
                'next_fixture_fdr': upcoming_fixtures[0]['fdr_overall'] if upcoming_fixtures else 3.0
            }
            processed_players.append(processed_player)
        
        df = pd.DataFrame(processed_players)
        
        # Add derived features
        df['minutes_per_game'] = df['minutes'] / max(1, len(raw_data['events']))
        df['cost_efficiency'] = df['total_points'] / df['cost']
        df['form_per_cost'] = df['form'] / df['cost']
        
        # FDR-adjusted metrics (lower FDR = easier fixtures = better value)
        df['fdr_adjusted_form'] = df['form'] * (6 - df['fdr_overall']) / 5  # Boost form for easier fixtures
        df['fdr_value_score'] = (df['total_points'] / df['cost']) * (6 - df['fdr_overall']) / 5
        
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
    
    def run(self, upcoming_gameweeks=5):
        """Run the complete data fetching and processing pipeline"""
        try:
            # Fetch raw data
            raw_data = self.fetch_data()
            
            # Fetch fixtures data
            try:
                fixtures_data = self.fetch_fixtures()
                logger.info("Successfully fetched fixtures data")
            except Exception as e:
                logger.warning(f"Could not fetch fixtures data: {e}")
                fixtures_data = None
            
            # Validate season data
            season_info = self.validate_season_data(raw_data)
            logger.info(f"Season data validation: {season_info}")
            
            # Process player data with FDR integration
            players_df = self.process_players_data(raw_data, fixtures_data, upcoming_gameweeks)
            
            # Add data validation information
            players_df, season_info = self.add_data_validation_info(players_df, season_info)
            
            # Save processed data
            self.save_processed_data(players_df)
            
            logger.info("Data fetching and processing completed successfully!")
            return players_df
            
        except Exception as e:
            logger.error(f"Error in data pipeline: {e}")
            raise

    def validate_season_data(self, raw_data):
        """Validate if the data is from current season and check for known transfers"""
        current_year = datetime.now().year
        current_month = datetime.now().month
        
        # FPL season typically runs Aug-May
        if current_month >= 8:
            expected_season = f"{current_year}-{current_year+1}"
        else:
            expected_season = f"{current_year-1}-{current_year}"
        
        # Check events to determine season
        events = raw_data.get('events', [])
        season_info = {
            'is_current_season': True,  # Default assumption
            'season_identifier': expected_season,
            'data_freshness': 'unknown',
            'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'warnings': []
        }
        
        # Check if we're in off-season (June-July) and data might be stale
        if current_month in [6, 7]:
            season_info['warnings'].append({
                'type': 'off_season',
                'message': f"⚠️ Off-season period detected. Data may be from {current_year-1}-{current_year} season.",
                'severity': 'medium'
            })
        
        # Check for potential transfer issues by looking for known cases
        self.check_known_transfers(raw_data, season_info)
        
        # Note: Relegation checking removed - current dataset contains only Premier League teams
        
        return season_info
    
    # Note: check_relegated_teams function removed - current dataset contains only Premier League teams
    
    def check_known_transfers(self, raw_data, season_info):
        """Check for known real-world transfers that might not be reflected"""
        # Known high-profile transfers for 2025 (as examples)
        known_transfers = [
            {
                'player_name': 'Trent Alexander-Arnold',
                'old_team': 'Liverpool',
                'new_team': 'Real Madrid',
                'transfer_date': '2025-01-01',  # Example date
                'status': 'confirmed'
            },
            # Add more known transfers here as they happen
        ]
        
        players = raw_data.get('elements', [])
        teams = {team['id']: team['name'] for team in raw_data.get('teams', [])}
        
        for transfer in known_transfers:
            # Find the player in current data
            for player in players:
                full_name = f"{player.get('first_name', '')} {player.get('second_name', '')}"
                if transfer['player_name'].lower() in full_name.lower():
                    current_team = teams.get(player.get('team'), 'Unknown')
                    
                    if current_team == transfer['old_team']:
                        season_info['warnings'].append({
                            'type': 'transfer_not_updated',
                            'message': f"🚨 {transfer['player_name']} may have transferred from {transfer['old_team']} to {transfer['new_team']} but is still listed as {current_team} player.",
                            'severity': 'high',
                            'player_id': player.get('id'),
                            'affected_optimization': True
                        })
                    break
    
    def add_data_validation_info(self, df, season_info):
        """Add validation information to the dataframe"""
        # Add validation flags to dataframe
        df['data_validation_warnings'] = 0
        df['transfer_risk'] = 'low'
        
        # Mark players with transfer warnings
        for warning in season_info['warnings']:
            if warning['type'] == 'transfer_not_updated' and 'player_id' in warning:
                player_mask = df['id'] == warning['player_id']
                df.loc[player_mask, 'data_validation_warnings'] = 1
                df.loc[player_mask, 'transfer_risk'] = 'high'
            
            # Mark players from relegated teams
            elif warning['type'] == 'relegated_team_present' and 'team_id' in warning:
                team_mask = df['team_id'] == warning['team_id']
                df.loc[team_mask, 'data_validation_warnings'] = 1
                df.loc[team_mask, 'transfer_risk'] = 'high'
        
        return df, season_info

def main():
    """Main function to run the data fetcher"""
    fetcher = FPLDataFetcher()
    players_df = fetcher.run(upcoming_gameweeks=5)
    
    # Display summary with FDR information
    print("\n" + "="*60)
    print("FPL DATA SUMMARY WITH FDR INTEGRATION")
    print("="*60)
    print(f"Total players: {len(players_df)}")
    print(f"Positions: {players_df['position'].value_counts().to_dict()}")
    print(f"Average cost: £{players_df['cost'].mean():.1f}m")
    print(f"Top scorer: {players_df.loc[players_df['total_points'].idxmax(), 'name']} ({players_df['total_points'].max()} pts)")
    
    # FDR Summary
    print("\nFDR ANALYSIS:")
    print(f"Average FDR (Attack): {players_df['fdr_attack'].mean():.2f}")
    print(f"Average FDR (Defence): {players_df['fdr_defence'].mean():.2f}")
    print(f"Average FDR (Overall): {players_df['fdr_overall'].mean():.2f}")
    
    # Best FDR teams
    team_fdr = players_df.groupby('team')[['fdr_attack', 'fdr_defence', 'fdr_overall']].mean().round(2)
    print("\nEASIEST FIXTURES (Next 5 GWs):")
    best_attack_fixtures = team_fdr.nsmallest(3, 'fdr_attack')
    best_defence_fixtures = team_fdr.nsmallest(3, 'fdr_defence')
    
    print("Attack (best for forwards/midfielders):")
    for team, row in best_attack_fixtures.iterrows():
        print(f"  {team}: {row['fdr_attack']}")
    
    print("Defence (best for defenders/goalkeepers):")
    for team, row in best_defence_fixtures.iterrows():
        print(f"  {team}: {row['fdr_defence']}")
    
    print("="*60)

if __name__ == "__main__":
    main()
