import pandas as pd
from config import ALL_CATEGORIES
from utils.data_helpers import extract_player_stats
from analysis.team_analysis import analyze_team

def trade_recommendations(league, my_team):
    """Find potential trade targets based on team needs"""
    print("\n--- TRADE RECOMMENDATIONS ---")
    
    # Get team strengths and weaknesses
    strengths, weaknesses = analyze_team(league, my_team)
    
    # Get my team players for potential trades
    my_players = []
    for player in my_team.roster:
        player_data = extract_player_stats(player, ALL_CATEGORIES)
        if player_data:  # Only add if we have stats
            my_players.append(player_data)
    
    my_df = pd.DataFrame(my_players)
    
    # Find trade targets on other teams
    all_targets = []
    
    for team in league.teams:
        # Skip my team
        if team.team_id == my_team.team_id:
            continue
            
        print(f"\nAnalyzing {team.team_name}...")
        
        # Find players who help in our weak categories
        team_players = []
        for player in team.roster:
            player_data = extract_player_stats(player, ALL_CATEGORIES)
            if player_data:  # Only add if we have stats
                player_data['fantasy_team'] = team.team_name
                player_data['owner'] = team.owner
                team_players.append(player_data)
        
        # Add to overall targets list
        all_targets.extend(team_players)
    
    targets_df = pd.DataFrame(all_targets)
    
    # For each weakness, find top trade targets
    trade_options = []
    
    for weakness in weaknesses:
        print(f"\nTop trade targets for {weakness}:")
        
        if weakness in ['ERA', 'WHIP']:  # Lower is better
            top_targets = targets_df.sort_values(by=weakness, ascending=True).head(3)
        else:  # Higher is better
            top_targets = targets_df.sort_values(by=weakness, ascending=False).head(3)
            
        # Find players from my team who are strong in areas I can afford to lose
        if strengths:
            trade_strength = strengths[0]  # Use first strength as trade chip
            
            if trade_strength in ['ERA', 'WHIP']:  # Lower is better
                my_trade_chips = my_df.sort_values(by=trade_strength, ascending=True).head(3)
            else:  # Higher is better
                my_trade_chips = my_df.sort_values(by=trade_strength, ascending=False).head(3)
        else:
            # If no clear strengths, use players who don't help with weaknesses
            my_trade_chips = my_df.sort_values(by=weakness, ascending=True).head(3) if weakness not in ['ERA', 'WHIP'] else \
                             my_df.sort_values(by=weakness, ascending=False).head(3)
                
        # Display trade possibilities
        for _, target in top_targets.iterrows():
            print(f"\n- Target: {target['name']} ({target['position']}, {target['team']})")
            print(f"  Owner: {target['owner']} ({target['fantasy_team']})")
            print(f"  {weakness} value: {target[weakness]}")
            
            print("  Possible trade chips:")
            for _, chip in my_trade_chips.iterrows():
                print(f"  - {chip['name']} ({chip['position']}, {chip['team']})")
                
            # Add to trade options
            trade_options.append({
                'target': target['name'],
                'target_team': target['fantasy_team'],
                'target_owner': target['owner'],
                'target_position': target['position'],
                'improves': weakness,
                'trade_chips': [chip['name'] for _, chip in my_trade_chips.iterrows()]
            })