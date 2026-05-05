# Sports Team Colors

A data-driven project providing comprehensive color schemes (up to 4 colors per team) and high-quality logos for NBA, NFL, MLB, and EPL teams.

## Data Structure

Each league has its own JSON file in the `data/` directory. Teams now feature a full color palette:

```json
{
    "id": "mlb-dodgers",
    "num_id": 114,
    "name": "Los Angeles Dodgers",
    "logo_url": "https://a.espncdn.com/i/teamlogos/mlb/500/lad.png",
    "colors": {
        "primary": "#005A9C",
        "secondary": "#EF3E42",
        "tertiary": "#FFFFFF",
        "quaternary": "#A1AAAD"
    }
}
```

## Visual Reference (Sample)

### Color Palette Preview
![Team Palettes](palette_preview.png)

### MLB
| Team | Logo | Primary | Secondary | Tertiary | Quaternary |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **LA Dodgers** | <img src="https://a.espncdn.com/i/teamlogos/mlb/500/lad.png" width="40"> | ![#005A9C](https://placehold.co/15x15/005A9C/005A9C.png) #005A9C | ![#EF3E42](https://placehold.co/15x15/EF3E42/EF3E42.png) #EF3E42 | ![#FFFFFF](https://placehold.co/15x15/FFFFFF/FFFFFF.png) #FFFFFF | ![#A1AAAD](https://placehold.co/15x15/A1AAAD/A1AAAD.png) #A1AAAD |
| **NY Yankees** | <img src="https://a.espncdn.com/i/teamlogos/mlb/500/nyy.png" width="40"> | ![#003087](https://placehold.co/15x15/003087/003087.png) #003087 | ![#E1E1E1](https://placehold.co/15x15/E1E1E1/E1E1E1.png) #E1E1E1 | ![#FFFFFF](https://placehold.co/15x15/FFFFFF/FFFFFF.png) #FFFFFF | ![#000000](https://placehold.co/15x15/000000/000000.png) #000000 |

### NBA
| Team | Logo | Primary | Secondary | Tertiary | Quaternary |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **LA Lakers** | <img src="https://a.espncdn.com/i/teamlogos/nba/500/lal.png" width="40"> | ![#552583](https://placehold.co/15x15/552583/552583.png) #552583 | ![#FDB927](https://placehold.co/15x15/FDB927/FDB927.png) #FDB927 | ![#000000](https://placehold.co/15x15/000000/000000.png) #000000 | ![#FFFFFF](https://placehold.co/15x15/FFFFFF/FFFFFF.png) #FFFFFF |
| **GS Warriors** | <img src="https://a.espncdn.com/i/teamlogos/nba/500/gsw.png" width="40"> | ![#1D428A](https://placehold.co/15x15/1D428A/1D428A.png) #1D428A | ![#FFC72C](https://placehold.co/15x15/FFC72C/FFC72C.png) #FFC72C | ![#FFFFFF](https://placehold.co/15x15/FFFFFF/FFFFFF.png) #FFFFFF | ![#26282A](https://placehold.co/15x15/26282A/26282A.png) #26282A |

## Full Dataset
Check the `data/` folder for the full list of 112 teams across 4 leagues.
