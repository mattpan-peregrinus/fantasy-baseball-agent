# ESPN Fantasy Baseball Agent
An advanced command-line tool to improve your ESPN fantasy baseball team and avoid becoming the Colorado Rockies of your league.

## 📊 Features
- **Team Analysis**: Evaluate your team's strengths and weaknesses based on category performance
- **Waiver Wire Recommendations**: Find free agents who can address your team's weaknesses
- **Trade Recommendations**: Identify players on other teams who could help your weak categories
- **Detailed Roster Breakdown**: View your team's composition by position
- **Smart Stat Processing**: Properly differentiates between pitchers and position players
- **Injury Awareness**: Shows injury status for all players

## 🚀 Prerequisites
- Python 3.7 or higher
- ESPN Fantasy Baseball league (Rotisserie scoring format)
- League credentials 

## 📥 Installation
1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/fantasy-baseball-analyzer.git

3. Install the required packages:
   ```bash
   pip install espn-api pandas numpy

5. Configure your league settings:
   - Open config.py and add your league ID, ESPN_S2 cookie, SWID cookie, and team ID.
   - Verify the scoring categories match your league's settings.

## 🔑 Getting ESPN API Credentials
For private leagues, you'll need your ESPN_S2 and SWID cookies:

1. Log in to your ESPN Fantasy account
2. Open browser developer tools (F12 in most browsers)
3. Go to Storage/Application tab and find Cookies
4. Look for the ESPN_S2 and SWID cookies
5. Copy these values to your config.py file


## 📋 How It Works
### Team Analysis
- Calculates both team totals and per-active-player averages
- Compares your team's per-active-player stats to league-wide averages
- Identifies categories where your team excels or lags behind

### Waiver Wire Recommendations
- Identifies players available on your waiver wire
- Uses stat-based filtering to ensure pitchers are recommended for pitching stats, and position players for batting stats
- Shows players who can help in your weakest categories

### Trade Analysis
- Searches all teams in your league for potential trade targets
- Suggests players from your roster who you could offer in trades
- Organizes recommendations by team to help plan effective trades

## 🛠️ Troubleshooting
If you encounter issues:

- Verify your league credentials in config.py
- Check your internet connection
- Make sure you're using the correct team ID (1-based index)
- If seeing position players recommended for pitching stats (or vice versa), check that BATTING_CATEGORIES and PITCHING_CATEGORIES are correctly defined in config.py

## 📝 Notes
- The analyzer uses the espn-api package, which interacts with ESPN's undocumented API
- API responses may change without notice; if you encounter issues, check for updates to this tool
- Player statistics update based on ESPN's data refresh schedule

## 🙏 Acknowledgments
This tool uses the [espn-api](https://github.com/cwendt94/espn-api) package for ESPN Fantasy API integration.
