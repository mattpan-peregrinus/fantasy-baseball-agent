import pandas as pd
from config import ALL_CATEGORIES
from utils.data_helpers import extract_player_stats
from analysis.team_analysis import analyze_team

def waiver_recommendations(league, my_team):
    """Find valuable players on the waiver wire"""
    print("\n--- WAIVER WIRE RECOMMENDATIONS ---")
    
    # Get team weaknesses
    strengths, weaknesses = analyze_team(league, my_team)

    # Get free agents (this can take some time)
    print("\nSearching free agents...")
    free_agents = league.free_agents(size=100)  # Get top 100 free agents
    
    # Create a DataFrame for free agents
    fa_stats = []
    for player in free_agents:
        player_data = extract_player_stats(player, ALL_CATEGORIES)
        if player_data:  # Only add if we have stats
            fa_stats.append(player_data)
    
    # Convert to DataFrame
    fa_df = pd.DataFrame(fa_stats)
    
    # Filter out injured players
    active_fa = fa_df[fa_df['injuryStatus'].isin(['ACTIVE', 'NA', 'PROBABLE', 'QUESTIONABLE'])]
    
    # Find players who help in weak categories
    recommendations = []
    
    for weakness in weaknesses:
        print(f"\nTop free agents for {weakness}:")
        
        if weakness in ['ERA', 'WHIP']:  # Lower is better
            top_players = active_fa.sort_values(by=weakness, ascending=True).head(5)
        else:  # Higher is better
            top_players = active_fa.sort_values(by=weakness, ascending=False).head(5)
        
        for _, player in top_players.iterrows():
            print(f"- {player['name']} ({player['position']}, {player['team']}): {player[weakness]}")
            recommendations.append((player['name'], player['position'], weakness))
    
    print("\nSummary of Recommendations:")
    for name, pos, cat in set(recommendations):
        print(f"Add {name} ({pos}) to improve {cat}")