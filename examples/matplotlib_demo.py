"""Run after: pip install -e . matplotlib; python examples/matplotlib_demo.py"""

import matplotlib.pyplot as plt

from sports_colors import get_palette, matplotlib_rc

palette = get_palette("nba-lakers", chart_type="categorical", n_colors=3)
with plt.rc_context(matplotlib_rc(palette)):
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(["Before", "Pilot", "After"], [12, 8, 5], color=palette.colors)
    ax.set_ylabel("Mean delay (seconds)")
    ax.set_title(f"Example chart — {palette.team_name} inspired")
    fig.tight_layout()
    fig.savefig("team_colors_matplotlib.png", dpi=180)
    plt.close(fig)
print("Warnings:", *palette.warnings, sep="\n - ")
