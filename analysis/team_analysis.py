import pandas as pd
from config import ALL_CATEGORIES
from utils.data_helpers import get_league_averages, extract_player_stats

def analyze_team(league, my_team):
    """Analyze team strengths and weaknesses by category"""
    print("\n--- TEAM ANALYSIS ---")
    
    # Get all rostered players on your team
    players = my_team.roster
    
    # Create DataFrame for analysis
    player_stats = []
    
    # Extract player stats
    for player in players:
        player_data = extract_player_stats(player, ALL_CATEGORIES)
        if player_data:  # Only add if we have stats
            player_stats.append(player_data)
    
    # Convert to DataFrame
    df = pd.DataFrame(player_stats)
    
    # Get league averages
    league_stats = get_league_averages(league, ALL_CATEGORIES)
    
    # Calculate team totals
    team_totals = df.sum(numeric_only=True)
    team_avgs = {
        'AVG': sum(df['AVG'] * df['AB']) / df['AB'].sum() if 'AB' in df and df['AB'].sum() > 0 else 0,
        'OBP': sum(df['OBP'] * df['PA']) / df['PA'].sum() if 'PA' in df and df['PA'].sum() > 0 else 0,
        'ERA': sum(df['ERA'] * df['IP']) / df['IP'].sum() if 'IP' in df and df['IP'].sum() > 0 else 0,
        'WHIP': sum(df['WHIP'] * df['IP']) / df['IP'].sum() if 'IP' in df and df['IP'].sum() > 0 else 0
    }
    for stat in ['R', 'HR', 'RBI', 'SB', 'W', 'SV', 'K']:
        team_avgs[stat] = team_totals.get(stat, 0)
    
    # Compare to league averages
    strengths = []
    weaknesses = []
    
    for cat in ALL_CATEGORIES:
        if cat in ['ERA', 'WHIP']:  # Lower is better
            if team_avgs[cat] < league_stats[cat] * 0.9:
                strengths.append(cat)
            elif team_avgs[cat] > league_stats[cat] * 1.1:
                weaknesses.append(cat)
        else:  # Higher is better
            if team_avgs[cat] > league_stats[cat] * 1.1:
                strengths.append(cat)
            elif team_avgs[cat] < league_stats[cat] * 0.9:
                weaknesses.append(cat)
    
    # Display team stats
    print(f"\nTeam: {my_team.team_name}")
    print("\nTeam Statistics:")
    for cat in ALL_CATEGORIES:
        print(f"{cat}: {team_avgs[cat]:.3f} (League Avg: {league_stats[cat]:.3f})")
    
    print("\nTeam Strengths:", ', '.join(strengths))
    print("Team Weaknesses:", ', '.join(weaknesses))
    
    # Positional analysis
    print("\nPositional Breakdown:")
    position_groups = df.groupby('position')
    for position, group in position_groups:
        print(f"\n{position}:")
        for _, player in group.iterrows():
            print(f"- {player['name']} ({player['team']})")

    return strengths, weaknesses