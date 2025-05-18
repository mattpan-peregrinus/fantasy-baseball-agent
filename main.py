from espn_api.baseball import League
from config import LEAGUE_ID, YEAR, ESPN_S2, SWID, TEAM_ID
from analysis.team_analysis import analyze_team
from analysis.waiver_wire import waiver_recommendations
from analysis.trades import trade_recommendations

def main():
    print("ESPN Fantasy Baseball Analyzer")
    print("Connecting to ESPN Fantasy API...")
    
    try:
        league = League(league_id=LEAGUE_ID, year=YEAR, espn_s2=ESPN_S2, swid=SWID)
        print(f"Connected successfully to: {league.settings.name}")
        
        my_team = league.teams[TEAM_ID-1]  
        print(f"Analyzing team: {my_team.team_name}")
        
        # Main menu
        while True:
            print("\nWhat would you like to do?")
            print("1. Analyze my team strengths/weaknesses")
            print("2. Get waiver wire recommendations")
            print("3. Find trade targets")
            print("4. Exit")
            
            choice = input("Enter your choice (1-4): ")
            
            if choice == '1':
                analyze_team(league, my_team)
            elif choice == '2':
                waiver_recommendations(league, my_team)
            elif choice == '3':
                trade_recommendations(league, my_team)
            elif choice == '4':
                print("Goodbye, may you not be the Rockies!")
                break
            else:
                print("Invalid choice, please try again.")
                
    except Exception as e:
        print(f"Error: {e}")
        print("Please check your credentials and internet connection.")

if __name__ == "__main__":
    main()
