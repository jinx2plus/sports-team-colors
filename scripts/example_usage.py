from sports_colors import mlb

def main():
    team = "LA Dodgers"
    colors = mlb.get_team_colors(team)
    
    print(f"--- {team} Color Scheme ---")
    for name, hex_code in colors.items():
        print(f"{name.capitalize()}: {hex_code}")

if __name__ == "__main__":
    main()
