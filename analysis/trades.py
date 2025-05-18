import pandas as pd
from config import ALL_CATEGORIES, BATTING_CATEGORIES, PITCHING_CATEGORIES
from utils.data_helpers import extract_player_stats
from analysis.team_analysis import analyze_team

def trade_recommendations(league, my_team):
    """Find potential trade targets based on team needs"""
    print("\n--- TRADE RECOMMENDATIONS ---")
    
    # Get team strengths and weaknesses
    strengths, weaknesses = analyze_team(league, my_team)
    
    if not weaknesses:
        print("\nYour team doesn't have clear weaknesses to address via trades.")
        print("Would you like to search for top players in all categories? (y/n)")
        response = input("> ").lower()
        if response == 'y':
            weaknesses = ALL_CATEGORIES
        else:
            return
    
    # Get my team players for potential trades
    my_players = []
    for player in my_team.roster:
        player_data = extract_player_stats(player, ALL_CATEGORIES)
        if player_data:  
            my_players.append(player_data)
    
    if not my_players:
        print("No usable player data found for your team.")
        return
        
    my_df = pd.DataFrame(my_players)
    
    # Find trade targets on other teams
    all_targets = []
    
    for team in league.teams:
        if team.team_id == my_team.team_id:
            continue
        print(f"\nAnalyzing {team.team_name}...")
        
        # Find players who help in my weak categories
        team_players = []
        for player in team.roster:
            player_data = extract_player_stats(player, ALL_CATEGORIES)
            if player_data:  
                player_data['fantasy_team'] = team.team_name
                player_data['owner'] = getattr(team, 'owner', 'Unknown')
                team_players.append(player_data)
        
        if not team_players:
            print(f"  No usable player data found for {team.team_name}")
            continue
    
        all_targets.extend(team_players)
    
    if not all_targets:
        print("\nNo viable trade targets found. Check data availability.")
        return
        
    targets_df = pd.DataFrame(all_targets)
    
    # For each weakness, find top trade targets
    trade_options = []
    
    for weakness in weaknesses:
        print(f"\nTop trade targets for {weakness}:")
        
        if weakness not in targets_df.columns:
            print(f"  No data available for {weakness}")
            continue
            
        if weakness in PITCHING_CATEGORIES:
            # For pitching stats, identify pitchers using stat values
            valid_players = targets_df[targets_df[weakness].notna()]
            
            if weakness in ['ERA', 'WHIP']:
                # For ERA/WHIP: Filter reasonable values
                filtered_targets = valid_players[(valid_players[weakness] > 0) & 
                                              (valid_players[weakness] < 10)]
                
                # Sort ascending (lower is better)
                top_targets = filtered_targets.sort_values(by=weakness, ascending=True).head(3)
            
            elif weakness in ['W', 'SV', 'K']:
                # For W/SV/K: Filter non-zero values
                filtered_targets = valid_players[valid_players[weakness] > 0]
                
                # Sort descending (higher is better)
                top_targets = filtered_targets.sort_values(by=weakness, ascending=False).head(3)
            
            else:
                top_targets = valid_players.sort_values(by=weakness, ascending=False).head(3)
        
        else:  # Batting categories or others
            valid_players = targets_df[targets_df[weakness].notna()]
            
            # Higher is better for batting stats
            top_targets = valid_players.sort_values(by=weakness, ascending=False).head(3)
        
        if top_targets.empty:
            print(f"  No suitable trade targets found for {weakness}")
            continue
            
        # Find players from my team who are strong in areas I can afford to lose
        if strengths:
            # Use first strength as trade chip
            trade_strength = strengths[0]
            
            # Skip if the trade strength isn't in my team's data
            if trade_strength not in my_df.columns:
                print(f"  No data available for {trade_strength} in your roster")
                continue
                
            # Filter and sort my players
            valid_chips = my_df[my_df[trade_strength].notna()]
            
            if valid_chips.empty:
                print(f"  No valid trade chips found with {trade_strength} stats")
                continue
                
            if trade_strength in ['ERA', 'WHIP']: 
                my_trade_chips = valid_chips.sort_values(by=trade_strength, ascending=True).head(3)
            else:  
                my_trade_chips = valid_chips.sort_values(by=trade_strength, ascending=False).head(3)
        else:
            # If no clear strengths, use players who don't help with weaknesses
            if weakness not in my_df.columns:
                print(f"  No data available for {weakness} in your roster")
                continue
                
            valid_chips = my_df[my_df[weakness].notna()]
            
            if valid_chips.empty:
                print(f"  No valid trade chips found with {weakness} stats")
                continue
                
            if weakness in ['ERA', 'WHIP']: 
                # For ERA/WHIP, higher values are worse, so use those as trade chips
                my_trade_chips = valid_chips.sort_values(by=weakness, ascending=False).head(3)
            else:
                # For other stats, lower values are worse
                my_trade_chips = valid_chips.sort_values(by=weakness, ascending=True).head(3)
                
        # Display trade possibilities
        for _, target in top_targets.iterrows():
            # Format the value based on category type
            if weakness in ['ERA', 'WHIP', 'AVG', 'OBP']:
                stat_value = f"{target[weakness]:.3f}"
            else:
                stat_value = f"{target[weakness]:.0f}"
                
            print(f"\n- Target: {target['name']} ({target['position']}, {target['team']})")
            print(f"  Owner: {target['owner']} ({target['fantasy_team']})")
            print(f"  {weakness} value: {stat_value}")
            
            print("  Possible trade chips:")
            for _, chip in my_trade_chips.iterrows():
                status = f" [INJURED: {chip['injuryStatus']}]" if chip.get('injured', False) else ""
                print(f"  - {chip['name']} ({chip['position']}, {chip['team']}){status}")
                
            # Add to trade options
            trade_options.append({
                'target': target['name'],
                'target_team': target['fantasy_team'],
                'target_owner': target['owner'],
                'target_position': target['position'],
                'target_value': target[weakness],
                'improves': weakness,
                'trade_chips': [chip['name'] for _, chip in my_trade_chips.iterrows()]
            })
    
    # Summary of trade recommendations        
    if trade_options:
        print("\nSummary of Recommended Trades:")
        
        # Group recommendations by target team
        team_recommendations = {}
        for trade in trade_options:
            team = trade['target_team']
            if team not in team_recommendations:
                team_recommendations[team] = []
            team_recommendations[team].append(trade)
        
        # Display by team
        for team, trades in team_recommendations.items():
            print(f"\n{team} - Owner: {trades[0]['target_owner']}")
            
            for trade in trades:
                # Format the stat value
                if trade['improves'] in ['ERA', 'WHIP', 'AVG', 'OBP']:
                    stat_value = f"{trade['target_value']:.3f}"
                else:
                    stat_value = f"{trade['target_value']:.0f}"
                    
                print(f"  * Target: {trade['target']} ({trade['target_position']}) - {trade['improves']}: {stat_value}")
                print(f"    Offer: {', '.join(trade['trade_chips'])}")
    else:
        print("\nNo viable trade options were found.")