"""Run after: pip install -e . plotly; python examples/plotly_demo.py"""

import plotly.graph_objects as go

from sports_colors import get_palette, plotly_layout

palette = get_palette("epl-arsenal", chart_type="categorical", n_colors=3)
fig = go.Figure()
for name, value, color in zip(["A", "B", "C"], [5, 7, 3], palette.colors):
    fig.add_bar(name=name, x=[name], y=[value], marker_color=color)
fig.update_layout(**plotly_layout(palette), title="Sports team colors — Plotly demo")
fig.write_html("team_colors_plotly.html")
print("Warnings:", *palette.warnings, sep="\n - ")
