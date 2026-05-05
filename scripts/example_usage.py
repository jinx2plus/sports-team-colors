import json
import requests

# List of all leagues in this repository
LEAGUES = ["mlb", "nba", "nfl", "epl"]

def get_team_by_id(team_id, use_github=True):
    """
    Find a specific team's data across all leagues.
    team_id: e.g., 'nba-lakers', 'mlb-dodgers', 'epl-liverpool'
    """
    for league in LEAGUES:
        if use_github:
            data = load_data_from_github(league)
        else:
            data = load_data_locally(league)
            
        if data:
            team = next((t for t in data if t['id'] == team_id), None)
            if team:
                return team
    return None

def load_data_locally(league):
    try:
        with open(f'data/{league}.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return None

def load_data_from_github(league):
    user = "jinx2plus"
    repo = "sports-team-colors"
    branch = "main"
    url = f"https://raw.githubusercontent.com/{user}/{repo}/{branch}/data/{league}.json"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception:
        return None

def main():
    # Example: Look up specific teams regardless of which league they are in
    target_teams = ["nba-lakers", "mlb-yankees", "epl-liverpool", "nfl-chiefs"]
    
    print(f"--- Searching for {len(target_teams)} teams ---")
    
    for tid in target_teams:
        team = get_team_by_id(tid, use_github=True)
        if team:
            print(f"Found: {team['name']}")
            print(f"  Colors: {list(team['colors'].values())}")
            print(f"  Logo: {team['logo_url']}")
        else:
            print(f"Could not find team: {tid}")

if __name__ == "__main__":
    # pip install requests
    main()
