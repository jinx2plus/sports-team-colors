"""Matplotlib and Plotly adapters; plotting libraries remain optional."""

from __future__ import annotations

from .palette import Palette


def matplotlib_rc(palette: Palette) -> dict:
    """Pass to plt.rc_context(matplotlib_rc(palette)) without changing global defaults."""
    return {
        "axes.prop_cycle": __import__("cycler").cycler(color=list(palette.colors)),
        "axes.facecolor": palette.background,
        "figure.facecolor": palette.background,
        "savefig.facecolor": palette.background,
        "axes.labelcolor": palette.foreground,
        "text.color": palette.foreground,
        "xtick.color": palette.foreground,
        "ytick.color": palette.foreground,
    }


def plotly_layout(palette: Palette) -> dict:
    """Pass as fig.update_layout(**plotly_layout(palette))."""
    return {
        "colorway": list(palette.colors),
        "paper_bgcolor": palette.background,
        "plot_bgcolor": palette.background,
        "font": {"color": palette.foreground},
        "xaxis": {"gridcolor": "#CBD5E1" if palette.theme == "light" else "#384658"},
        "yaxis": {"gridcolor": "#CBD5E1" if palette.theme == "light" else "#384658"},
    }
