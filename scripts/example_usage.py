import json
import requests

def load_data_locally(league):
    """Load team data from a local JSON file."""
    try:
        with open(f'data/{league}.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Local file data/{league}.json not found.")
        return None

def load_data_from_github(league):
    """
    Load team data directly from the GitHub repository.
    This is useful for using the data in external projects without cloning the repo.
    """
    user = "jinx2plus"
    repo = "sports-team-colors"
    branch = "main"
    url = f"https://raw.githubusercontent.com/{user}/{repo}/{branch}/data/{league}.json"
    
    print(f"Fetching data from: {url}")
    try:
        response = requests.get(url)
        response.raise_for_status() # Check for HTTP errors
        return response.json()
    except Exception as e:
        print(f"Error fetching data from GitHub: {e}")
        return None

def main():
    league = "nba"
    
    # Example 1: Loading from GitHub (Recommended for external apps)
    print("--- Example 1: GitHub Import ---")
    teams = load_data_from_github(league)
    
    if teams:
        print(f"Successfully loaded {len(teams)} teams from GitHub.")
        # Accessing a specific team (e.g., LA Lakers)
        lakers = next((t for t in teams if t['id'] == 'nba-lakers'), None)
        if lakers:
            print(f"Team: {lakers['name']}")
            print(f"Primary Color: {lakers['colors']['primary']}")
            print(f"Logo URL: {lakers['logo_url']}")
    
    print("\n" + "="*40 + "\n")
    
    # Example 2: Loading Locally
    print("--- Example 2: Local Import ---")
    local_teams = load_data_locally(league)
    if local_teams:
        print(f"Successfully loaded {len(local_teams)} teams from local file.")

if __name__ == "__main__":
    # Note: You need the 'requests' library installed: pip install requests
    main()
