"""Sports team inspired, chart-aware color palettes."""

from .accessibility import AuditIssue, AuditReport, audit_palette, simulate_cvd
from .color_math import contrast_ratio, ensure_contrast
from .palette import Palette, all_teams, get_palette, get_team, get_team_colors
from .themes import matplotlib_rc, plotly_layout

__all__ = [
    "AuditIssue", "AuditReport", "Palette", "all_teams", "audit_palette",
    "contrast_ratio", "ensure_contrast", "get_palette", "get_team", "get_team_colors",
    "matplotlib_rc", "plotly_layout", "simulate_cvd",
]
