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
| **LA Dodgers** | <img src="https://a.espncdn.com/i/teamlogos/mlb/500/lad.png" width="40"> | ![#005A9C](https://placehold.co/15x15/005A9C/005A9C.png) #005A9C | ![#FFFFFF](https://placehold.co/15x15/FFFFFF/FFFFFF.png) #FFFFFF | ![#EF3E42](https://placehold.co/15x15/EF3E42/EF3E42.png) #EF3E42 | ![#A1AAAD](https://placehold.co/15x15/A1AAAD/A1AAAD.png) #A1AAAD |

### NBA
| Team | Logo | Primary | Secondary | Tertiary | Quaternary |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Phila. 76ers** | <img src="https://a.espncdn.com/i/teamlogos/nba/500/phi.png" width="40"> | ![#006BB6](https://placehold.co/15x15/006BB6/006BB6.png) #006BB6 | ![#ED174C](https://placehold.co/15x15/ED174C/ED174C.png) #ED174C | ![#002B5C](https://placehold.co/15x15/002B5C/002B5C.png) #002B5C | ![#C4CED4](https://placehold.co/15x15/C4CED4/C4CED4.png) #C4CED4 |
| **Houston Rockets** | <img src="https://a.espncdn.com/i/teamlogos/nba/500/hou.png" width="40"> | ![#CE1141](https://placehold.co/15x15/CE1141/CE1141.png) #CE1141 | ![#000000](https://placehold.co/15x15/000000/000000.png) #000000 | ![#C4CED4](https://placehold.co/15x15/C4CED4/C4CED4.png) #C4CED4 | ![#FFFFFF](https://placehold.co/15x15/FFFFFF/FFFFFF.png) #FFFFFF |

### EPL
| Team | Logo | Primary | Secondary | Tertiary | Quaternary |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Liverpool** | <img src="https://a.espncdn.com/i/teamlogos/soccer/500/364.png" width="40"> | ![#C8102E](https://placehold.co/15x15/C8102E/C8102E.png) #C8102E | ![#00B2A9](https://placehold.co/15x15/00B2A9/00B2A9.png) #00B2A9 | ![#F6EB61](https://placehold.co/15x15/F6EB61/F6EB61.png) #F6EB61 | ![#000000](https://placehold.co/15x15/000000/000000.png) #000000 |

## Full Dataset
Check the `data/` folder for the full list of 112 teams across 4 leagues.
