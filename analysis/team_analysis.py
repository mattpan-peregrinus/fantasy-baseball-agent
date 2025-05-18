import pandas as pd
import numpy as np
from config import ALL_CATEGORIES
from utils.data_helpers import get_league_averages, extract_player_stats

def analyze_team(league, my_team):
    """Analyze team strengths and weaknesses by category"""
    print("\n--- TEAM ANALYSIS ---")
    players = my_team.roster
    player_stats = []
    
    # Extract player stats
    for player in players:
        player_data = extract_player_stats(player, ALL_CATEGORIES)
        if player_data:  
            player_stats.append(player_data)

    if not player_stats:
        print(f"\nTeam: {my_team.team_name}")
        print("\nNo player statistics available. Check API connection and data.")
        return [], []
    
    df = pd.DataFrame(player_stats)
    
    # Get league averages 
    league_stats = get_league_averages(league, ALL_CATEGORIES)
    
    # Count active vs. total players 
    active_players = 0
    if 'lineupSlot' in df.columns:
        active_players = df[~df['lineupSlot'].isin(['BE', 'IL'])].shape[0]
    else:
        active_players = len(df)
    
    total_players = len(df)
    
    # Calculate different versions of team stats
    team_totals = {}
    team_all_avgs = {}    # Average per roster spot
    team_active_avgs = {} # Average per active player
    
    # Batting Average - weighted by AB
    if 'AB' in df.columns and df['AB'].sum() > 0:
        team_all_avgs['AVG'] = (df['AVG'] * df['AB']).sum() / df['AB'].sum()
    else:
        team_all_avgs['AVG'] = df['AVG'].mean() if 'AVG' in df.columns else 0
    
    team_active_avgs['AVG'] = team_all_avgs['AVG'] 
    
    # On-base Percentage - weighted by PA
    if 'PA' in df.columns and df['PA'].sum() > 0:
        team_all_avgs['OBP'] = (df['OBP'] * df['PA']).sum() / df['PA'].sum()
    else:
        team_all_avgs['OBP'] = df['OBP'].mean() if 'OBP' in df.columns else 0
    
    team_active_avgs['OBP'] = team_all_avgs['OBP']  
    
    # ERA - weighted by IP
    if 'IP' in df.columns and df['IP'].sum() > 0:
        team_all_avgs['ERA'] = (df['ERA'] * df['IP']).sum() / df['IP'].sum()
    else:
        team_all_avgs['ERA'] = df['ERA'].mean() if 'ERA' in df.columns else 0
    
    team_active_avgs['ERA'] = team_all_avgs['ERA'] 
    
    # WHIP - weighted by IP
    if 'IP' in df.columns and df['IP'].sum() > 0:
        team_all_avgs['WHIP'] = (df['WHIP'] * df['IP']).sum() / df['IP'].sum()
    else:
        team_all_avgs['WHIP'] = df['WHIP'].mean() if 'WHIP' in df.columns else 0
    
    team_active_avgs['WHIP'] = team_all_avgs['WHIP']  
    
    # Counting stats - calculate different versions
    for stat in ['R', 'HR', 'RBI', 'SB', 'W', 'SV', 'K']:
        if stat in df.columns:
            team_totals[stat] = df[stat].sum()
            team_all_avgs[stat] = team_totals[stat] / total_players
            team_active_avgs[stat] = team_totals[stat] / active_players if active_players > 0 else 0
        else:
            team_totals[stat] = 0
            team_all_avgs[stat] = 0
            team_active_avgs[stat] = 0
    
    # Compare to league averages - use active player averages 
    # (assuming league_stats is calculated the same way)
    strengths = []
    weaknesses = []
    
    # Choose which team stats to compare with the league
    team_stats_to_compare = team_active_avgs
    
    for cat in ALL_CATEGORIES:
        if cat not in team_stats_to_compare or cat not in league_stats:
            continue
            
        if league_stats[cat] == 0:
            continue
            
        if cat in ['ERA', 'WHIP']:  
            if team_stats_to_compare[cat] < league_stats[cat] * 0.9:
                strengths.append(cat)
            elif team_stats_to_compare[cat] > league_stats[cat] * 1.1:
                weaknesses.append(cat)
        else: 
            if team_stats_to_compare[cat] > league_stats[cat] * 1.1:
                strengths.append(cat)
            elif team_stats_to_compare[cat] < league_stats[cat] * 0.9:
                weaknesses.append(cat)
    
    # Display team stats with multiple metrics
    print(f"\nTeam: {my_team.team_name}")
    print(f"Roster: {total_players} total players, {active_players} active players")
    
    print("\nTeam Statistics:")
    for cat in ALL_CATEGORIES:
        if cat in ['R', 'HR', 'RBI', 'SB', 'W', 'SV', 'K']:
            if cat in team_totals and cat in team_active_avgs and cat in league_stats:
                print(f"{cat}: {team_totals[cat]:.0f} total, {team_active_avgs[cat]:.3f} per active (League Avg: {league_stats[cat]:.3f})")
        else:
            if cat in team_active_avgs and cat in league_stats:
                print(f"{cat}: {team_active_avgs[cat]:.3f} (League Avg: {league_stats[cat]:.3f})")
    
    print("\nTeam Strengths:", ', '.join(strengths) if strengths else "None identified")
    print("Team Weaknesses:", ', '.join(weaknesses) if weaknesses else "None identified")
    
    # Positional analysis
    print("\nPositional Breakdown:")
    try:
        if 'position' in df.columns:
            position_groups = df.groupby('position')
            for position, group in position_groups:
                print(f"\n{position}:")
                for _, player in group.iterrows():
                    status = f" [INJURED: {player['injuryStatus']}]" if player['injured'] else ""
                    lineup = f" (BENCH)" if player.get('lineupSlot') in ['BE', 'IL'] else ""
                    print(f"- {player['name']} ({player['team']}){status}{lineup}")
        else:
            print("\nRoster Players:")
            for _, player in df.iterrows():
                status = f" [INJURED: {player['injuryStatus']}]" if player['injured'] else ""
                lineup = f" (BENCH)" if player.get('lineupSlot') in ['BE', 'IL'] else ""
                print(f"- {player['name']} ({player['team']}){status}{lineup}")
    except Exception as e:
        print(f"Error during positional breakdown: {e}")
        print("Check the 'position' field in your player data")

    return strengths, weaknesses