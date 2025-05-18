def get_league_averages(league, categories):
    """Calculate league average stats for each category
    
    Returns the average stats across all teams in the league, 
    calculated as the mean of each team's average per active/starting player.
    """
    # Initialize stats collection by team
    team_stats = {team.team_name: {cat: [] for cat in categories} for team in league.teams}
    
    # Track active players per team
    active_player_counts = {team.team_name: 0 for team in league.teams}
    
    # Collect stats from all teams
    print("Calculating league averages...")
    for team in league.teams:
        print(f"Processing team: {team.team_name}")
        team_name = team.team_name
        
        for player in team.roster:
            # Skip players with no stats
            if not hasattr(player, 'stats') or not player.stats:
                continue
                
            # Extract player stats
            player_stats = extract_player_stats_from_espn(player, categories)
            if not player_stats:
                continue
                
            # Add each category to team collection
            for cat in categories:
                if cat in player_stats and player_stats[cat] is not None:
                    team_stats[team_name][cat].append(player_stats[cat])
            
            # Count this player as active
            active_player_counts[team_name] += 1
    
    # Calculate team averages first, then league average
    league_avgs = {}
    for cat in categories:
        team_avgs = []
        
        for team_name, stats in team_stats.items():
            if stats[cat] and active_player_counts[team_name] > 0:
                # For each team, calculate the average stat per active player
                team_avg = sum(stats[cat]) / active_player_counts[team_name]
                team_avgs.append(team_avg)
        
        # League average is the average of team averages
        if team_avgs:
            league_avgs[cat] = sum(team_avgs) / len(team_avgs)
        else:
            league_avgs[cat] = 0
    
    return league_avgs

def extract_player_stats_from_espn(player, categories):
    # Skip players with no stats attribute
    if not hasattr(player, 'stats') or not player.stats:
        return None
    
    # Initialize stats dictionary
    player_stats = {}
    
    # Season stats appear to be in player.stats[0]
    if 0 in player.stats and 'breakdown' in player.stats[0]:
        breakdown = player.stats[0]['breakdown']
        
        # Handle case where breakdown is empty 
        if not breakdown:
            # Try to get projected breakdown instead
            if 'projected_breakdown' in player.stats[0]:
                breakdown = player.stats[0]['projected_breakdown']
            else:
                return None 
        
        # Map stats directly from breakdown
        for cat in categories:
            if cat in breakdown:
                player_stats[cat] = breakdown[cat]
            # Special case for common stat aliases
            elif cat == 'AVG' and 'AVG' not in breakdown and 'OBP' in breakdown and 'SLG' in breakdown:
                # Approximate AVG from OBP if missing
                player_stats[cat] = breakdown['OBP'] * 0.8  
    
        # Add AB/PA/IP if available (needed for rate stats)
        if 'AB' in breakdown:
            player_stats['AB'] = breakdown['AB']
        if 'PA' in breakdown:
            player_stats['PA'] = breakdown['PA']
        # For pitchers, innings pitched might be stored as OUTS/3
        if 'IP' not in breakdown and 'OUTS' in breakdown:
            player_stats['IP'] = breakdown['OUTS'] / 3
        elif 'IP' in breakdown:
            player_stats['IP'] = breakdown['IP']
    
    return player_stats

def extract_player_stats(player, categories):
    """Extract stats for a single player into a dictionary format for analysis"""
    if not hasattr(player, 'stats') or not player.stats:
        return None
        
    # Get stats from ESPN format
    stats = extract_player_stats_from_espn(player, categories)
    if not stats:
        return None
    
    # Add player metadata
    player_data = {
        'id': getattr(player, 'playerId', 0),
        'name': getattr(player, 'name', 'Unknown'),
        'position': getattr(player, 'position', 'Unknown'),
        'team': getattr(player, 'proTeam', 'Unknown'),
        'injured': getattr(player, 'injured', False),
        'injuryStatus': getattr(player, 'injuryStatus', 'NA'),
        'lineupSlot': getattr(player, 'lineupSlot', 'Unknown')
    }
    
    # Add stats to player data
    for cat in categories:
        if cat in stats:
            player_data[cat] = stats[cat]
        else:
            player_data[cat] = 0
    
    # Add AB/PA/IP for rate stat calculations
    for stat in ['AB', 'PA', 'IP']:
        if stat in stats:
            player_data[stat] = stats[stat]
    
    return player_data