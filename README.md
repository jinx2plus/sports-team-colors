# Sports Team Colors

A data-driven project providing official color schemes (Hex) and logos for NBA, NFL, MLB, and EPL teams.

## Data Structure

Each league has its own JSON file in the `data/` directory.

```json
{
    "id": "mlb-dodgers",
    "num_id": 114,
    "name": "Los Angeles Dodgers",
    "logo_url": "https://a.espncdn.com/i/teamlogos/mlb/500/lad.png",
    "colors": {
        "primary": "#005A9C",
        "secondary": "#FFFFFF",
        "accent": "#A5ACAF"
    }
}
```

## Visual Reference

### MLB
| Team | Logo | Primary | Secondary |
| :--- | :---: | :---: | :---: |
| **LA Dodgers** | <img src="https://a.espncdn.com/i/teamlogos/mlb/500/lad.png" width="40"> | ![#005A9C](https://placehold.co/15x15/005A9C/005A9C.png) #005A9C | ![#FFFFFF](https://placehold.co/15x15/FFFFFF/FFFFFF.png) #FFFFFF |
| **NY Yankees** | <img src="https://a.espncdn.com/i/teamlogos/mlb/500/nyy.png" width="40"> | ![#003087](https://placehold.co/15x15/003087/003087.png) #003087 | ![#E6E6E6](https://placehold.co/15x15/E6E6E6/E6E6E6.png) #E6E6E6 |

### NBA
| Team | Logo | Primary | Secondary |
| :--- | :---: | :---: | :---: |
| **LA Lakers** | <img src="https://a.espncdn.com/i/teamlogos/nba/500/lal.png" width="40"> | ![#552583](https://placehold.co/15x15/552583/552583.png) #552583 | ![#FDB927](https://placehold.co/15x15/FDB927/FDB927.png) #FDB927 |
| **GS Warriors** | <img src="https://a.espncdn.com/i/teamlogos/nba/500/gsw.png" width="40"> | ![#1D428A](https://placehold.co/15x15/1D428A/1D428A.png) #1D428A | ![#FFC72C](https://placehold.co/15x15/FFC72C/FFC72C.png) #FFC72C |

## Usage (Python)

```python
import json

# Load MLB colors from JSON
with open('data/mlb.json', 'r') as f:
    mlb_teams = json.load(f)

# Find LA Dodgers by ID
dodgers = next(team for team in mlb_teams if team['id'] == 'mlb-dodgers')
print(f"Name: {dodgers['name']}")
print(f"Logo: {dodgers['logo_url']}")
print(f"Colors: {dodgers['colors']}")
```
