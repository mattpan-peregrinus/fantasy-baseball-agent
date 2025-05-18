import pandas as pd
from config import ALL_CATEGORIES, BATTING_CATEGORIES, PITCHING_CATEGORIES
from utils.data_helpers import extract_player_stats
from analysis.team_analysis import analyze_team

def waiver_recommendations(league, my_team):
    """Find valuable players on the waiver wire"""
    print("\n--- WAIVER WIRE RECOMMENDATIONS ---")
    
    # Get team weaknesses
    strengths, weaknesses = analyze_team(league, my_team)
    
    if not weaknesses:
        print("\nYour team has no clear weaknesses to address.")
        print("Would you like to see top available players in all categories? (y/n)")
        response = input("> ").lower()
        if response == 'y':
            weaknesses = ALL_CATEGORIES
        else:
            return

    # Get free agents
    print("\nSearching free agents...")
    free_agents = league.free_agents(size=100)  # Top 100 free agents
    print(f"Found {len(free_agents)} free agents. Analyzing stats...")
 
    fa_stats = []
    for player in free_agents:
        player_data = extract_player_stats(player, ALL_CATEGORIES)
        if player_data:  
            fa_stats.append(player_data)
    if not fa_stats:
        print("No usable stats found for free agents.")
        return
    fa_df = pd.DataFrame(fa_stats)
    
    # Filter out injured players (with option to include)
    include_injured = input("Include injured players? (y/n): ").lower() == 'y'
    if not include_injured:
        if 'injuryStatus' in fa_df.columns:
            active_fa = fa_df[fa_df['injuryStatus'].isin(['ACTIVE', 'NA', 'PROBABLE', 'QUESTIONABLE'])]
        else:
            active_fa = fa_df[~fa_df['injured']]
            
        if active_fa.empty:
            print("No active players found. Showing all players including injured.")
            active_fa = fa_df
    else:
        active_fa = fa_df
    
    print(f"Analyzing {len(active_fa)} available players...")
    
    # Find players who help in weak categories
    recommendations = []
    
    for weakness in weaknesses:
        print(f"\nTop free agents for {weakness}:")
        
        # Skip processing if category not in DataFrame
        if weakness not in active_fa.columns:
            print(f"  No data available for {weakness}")
            continue
            
        if weakness in PITCHING_CATEGORIES:
            # For pitching categories
            valid_players = active_fa[active_fa[weakness].notna()]
            
            if weakness in ['ERA', 'WHIP']:
                # For ERA/WHIP: 
                # 1. Exclude zeros (likely position players)
                # 2. Include reasonable ranges for these stats
                filtered_players = valid_players[(valid_players[weakness] > 0) & 
                                               (valid_players[weakness] < 10)] 
            
            elif weakness in ['W', 'SV', 'K']:
                # For W/SV/K:
                # Include only players with non-zero values (actual pitchers)
                filtered_players = valid_players[valid_players[weakness] > 0]
            
            else:
                filtered_players = valid_players
            
            if filtered_players.empty:
                print(f"  No players found with valid {weakness} stats")
                continue
            
            if weakness in ['ERA', 'WHIP']:
                top_players = filtered_players.sort_values(by=weakness, ascending=True).head(5)
            else:
                top_players = filtered_players.sort_values(by=weakness, ascending=False).head(5)
            
        else: 
            # For batting categories
            valid_players = active_fa[active_fa[weakness].notna()]
            
            if valid_players.empty:
                print(f"  No players found with valid {weakness} stats")
                continue
                
            top_players = valid_players.sort_values(by=weakness, ascending=False).head(5)
        
        # Display and record recommendations
        for _, player in top_players.iterrows():
            status = f" [INJURED: {player['injuryStatus']}]" if player.get('injured', False) else ""
            
            # Format the value based on category type
            if weakness in ['ERA', 'WHIP', 'AVG', 'OBP']:
                formatted_value = f"{player[weakness]:.3f}"
            else:
                formatted_value = f"{player[weakness]:.0f}"
                
            print(f"- {player['name']} ({player['position']}, {player['team']}): {formatted_value}{status}")
            recommendations.append((player['name'], player['position'], weakness, player[weakness]))
            
    # Recommended pickups
    if recommendations:
        print("\nRecommended Pickups:")
        
        player_recommendations = {}
        for name, pos, cat, value in recommendations:
            if name not in player_recommendations:
                player_recommendations[name] = {"position": pos, "helps_with": []}
            
            if cat in ['ERA', 'WHIP', 'AVG', 'OBP']:
                formatted_value = f"{value:.3f}"
            else:
                formatted_value = f"{value:.0f}"
                
            player_recommendations[name]["helps_with"].append(f"{cat}: {formatted_value}")
        
        for name, details in player_recommendations.items():
            helps_with = ", ".join(details["helps_with"])
            print(f"* {name} ({details['position']}) - Helps with: {helps_with}")
    else:
        print("\nNo suitable recommendations found. Try including injured players or checking more categories.")