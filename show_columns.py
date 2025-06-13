#!/usr/bin/env python3
"""
Display FPL dataset columns in a nice table format
"""

import pandas as pd

def display_columns():
    # Load the data
    df = pd.read_csv('data/processed/fpl_players_latest.csv')
    
    print("╔══════════════════════════════════════════════════════════════════════════════════════╗")
    print("║                                  FPL DATASET COLUMNS                                ║")
    print("╠══════════════════════════════════════════════════════════════════════════════════════╣")
    print(f"║ Total Columns: {len(df.columns):<15} Total Players: {len(df):<25} ║")
    print("╚══════════════════════════════════════════════════════════════════════════════════════╝")
    print()
    
    # Column descriptions
    descriptions = {
        'id': 'Player unique identifier',
        'name': 'Full player name',
        'web_name': 'Display name on FPL website',
        'team': 'Team name (e.g., Arsenal, Liverpool)',
        'team_id': 'Team unique identifier',
        'position': 'Player position (GK, DEF, MID, FWD)',
        'cost': 'Player cost in millions (£)',
        'total_points': 'Total season points',
        'form': 'Recent form (last 5 games average)',
        'points_per_game': 'Average points per game',
        'minutes': 'Total minutes played',
        'goals_scored': 'Total goals scored',
        'assists': 'Total assists',
        'clean_sheets': 'Total clean sheets (GK/DEF)',
        'goals_conceded': 'Total goals conceded (GK/DEF)',
        'own_goals': 'Total own goals',
        'penalties_saved': 'Total penalties saved (GK)',
        'penalties_missed': 'Total penalties missed',
        'yellow_cards': 'Total yellow cards',
        'red_cards': 'Total red cards',
        'saves': 'Total saves (GK)',
        'bonus': 'Total bonus points',
        'bps': 'Bonus Points System score',
        'influence': 'FPL Influence metric',
        'creativity': 'FPL Creativity metric',
        'threat': 'FPL Threat metric',
        'ict_index': 'Combined ICT Index (Influence+Creativity+Threat)',
        'selected_by_percent': 'Ownership percentage (how many managers have player)',
        'value_form': 'Value based on recent form',
        'value_season': 'Value based on season performance',
        'transfers_in': 'Total transfers in (season)',
        'transfers_out': 'Total transfers out (season)',
        'transfers_in_event': 'Transfers in this gameweek',
        'transfers_out_event': 'Transfers out this gameweek',
        'fdr_attack': '🌟 Fixture Difficulty Rating - Attack (1=easy, 5=hard)',
        'fdr_defence': '🌟 Fixture Difficulty Rating - Defence (1=easy, 5=hard)',
        'fdr_overall': '🌟 Fixture Difficulty Rating - Overall (1=easy, 5=hard)',
        'team_strength_attack': 'Team attack strength (raw FPL data)',
        'team_strength_defence': 'Team defence strength (raw FPL data)',
        'minutes_per_game': '📊 Calculated: Average minutes per game',
        'cost_efficiency': '📊 Calculated: Total points ÷ Cost',
        'form_per_cost': '📊 Calculated: Form ÷ Cost',
        'position_encoded': '📊 Calculated: Position as number (1=GK, 2=DEF, etc)'
    }
    
    print("┌────┬─────────────────────────┬────────────────────────────────────────────────────────┐")
    print("│ #  │ Column Name             │ Description                                            │")
    print("├────┼─────────────────────────┼────────────────────────────────────────────────────────┤")
    
    for i, col in enumerate(df.columns, 1):
        desc = descriptions.get(col, 'No description')
        print(f"│ {i:2d} │ {col:<23} │ {desc:<54} │")
    
    print("└────┴─────────────────────────┴────────────────────────────────────────────────────────┘")
    print()
    print("🌟 = New FDR features added")
    print("📊 = Calculated/derived features")
    print()
    
    # Show some sample data
    print("📈 SAMPLE DATA (First 3 players):")
    print("=" * 80)
    sample_cols = ['name', 'team', 'position', 'cost', 'total_points', 'form', 'fdr_overall']
    print(df[sample_cols].head(3).to_string(index=False))
    print()

if __name__ == "__main__":
    display_columns()
