def get_league_averages(league, categories):
    """Calculate league average stats for each category"""
    
    all_stats = {cat: [] for cat in categories}
    
    # Collect stats from all teams
    for team in league.teams:
        for player in team.roster:
            if not hasattr(player, 'stats') or not player.stats:
                continue
                
            stats = player.stats.get('2025_projected', None)
            if not stats:
                stats = player.stats.get('2025_season', {})
                
            for cat in categories:
                if cat in stats:
                    all_stats[cat].append(stats[cat])
    
    # Calculate averages
    league_avgs = {}
    for cat in categories:
        if all_stats[cat]:
            league_avgs[cat] = sum(all_stats[cat]) / len(all_stats[cat])
        else:
            league_avgs[cat] = 0
    
    return league_avgs

def extract_player_stats(player, categories):
    """Extract stats for a single player into a dictionary"""
    if not hasattr(player, 'stats') or not player.stats:
        return None
        
    # Get season stats (current season)
    stats = player.stats.get('2025_projected', None)  # Use projected stats
    if not stats:
        stats = player.stats.get('2025_season', {})   # Fallback to season stats
    
    # Skip players with no stats
    if not stats:
        return None
        
    # Extract relevant stats
    player_data = {
        'id': player.playerId if hasattr(player, 'playerId') else 0,
        'name': player.name,
        'position': player.position,
        'team': player.proTeam,
        'injured': player.injured,
        'injuryStatus': player.injuryStatus if hasattr(player, 'injuryStatus') else 'NA'
    }
    
    # Add each stat category
    for cat in categories:
        player_data[cat] = stats.get(cat, 0)
    
    # Add AB/PA/IP if available (needed for rate stats)
    for stat in ['AB', 'PA', 'IP']:
        if stat in stats:
            player_data[stat] = stats.get(stat, 0)
    
    return player_data