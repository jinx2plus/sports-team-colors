"""Team palette lookup, accessible role selection and chart-specific variants."""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from .accessibility import audit_palette
from .color_math import (
    best_text_color,
    contrast_ratio,
    ensure_contrast,
    from_oklch,
    normalize_hex,
    to_oklch,
)

_LEAGUES = ("mlb", "nba", "nfl", "epl")
_ROLES = ("primary", "secondary", "tertiary", "quaternary")


@dataclass(frozen=True)
class Palette:
    team_id: str
    team_name: str
    chart_type: str
    theme: str
    colors: tuple[str, ...]
    original_colors: tuple[str, ...]
    background: str
    foreground: str
    warnings: tuple[str, ...]
    contrast_ratios: tuple[float, ...]
    adjusted: tuple[bool, ...]


@lru_cache(maxsize=1)
def all_teams() -> tuple[dict, ...]:
    """The root /data is authoritative in a checkout; bundled data works in a wheel."""
    project_data = Path(__file__).resolve().parent.parent / "data"
    bundled_data = Path(__file__).resolve().parent / "data"
    data_dir = project_data if project_data.is_dir() else bundled_data
    teams: list[dict] = []
    for league in _LEAGUES:
        with (data_dir / f"{league}.json").open(encoding="utf-8") as fh:
            league_teams = json.load(fh)
        for team in league_teams:
            if not isinstance(team.get("colors"), dict) or any(role not in team["colors"] for role in _ROLES):
                raise ValueError(f"Invalid palette schema: {team!r}")
            teams.append(team)
    ids = [team["id"] for team in teams]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate team IDs in catalog")
    return tuple(teams)


def get_team(team: str) -> dict:
    key = team.strip().casefold()
    if not key:
        raise ValueError("Team name/id must not be empty")
    matches = [t for t in all_teams() if key in (t["id"].casefold(), t["name"].casefold())]
    if len(matches) != 1:
        raise ValueError(f"Expected one matching team for {team!r}; found {len(matches)}. Use the league-prefixed ID.")
    return matches[0]


def get_team_colors(team: str) -> dict[str, str]:
    """Get original colors without any chart-specific adjustments."""
    return {role: normalize_hex(value) for role, value in get_team(team)["colors"].items()}


def _distinct(values: tuple[str, ...]) -> list[str]:
    return list(dict.fromkeys(values))


def _categorical(sources: tuple[str, ...], count: int) -> list[str]:
    colors = _distinct(sources)
    if count <= len(colors):
        return colors[:count]
    # Additional hues are derivatives, not verified official team brand colors.
    i = 0
    while len(colors) < count:
        base = sources[i % len(sources)]
        l, c, h = to_oklch(base)
        hue_offset = (i // len(sources) + 1) * math.radians(48) * (1 if i % 2 else -1)
        new = from_oklch(min(0.75, max(0.33, l)), max(c, 0.10), h + hue_offset)
        if new not in colors:
            colors.append(new)
        i += 1
        if i > count * 20:
            raise ValueError("Cannot generate enough distinct colors")
    return colors


def _sequential(sources: tuple[str, ...], count: int, *, dark: bool) -> list[str]:
    if count == 1:
        return [sources[0]]
    _, chroma, hue = to_oklch(sources[0])
    start, end = ((0.48, 0.88) if dark else (0.64, 0.25))
    return [from_oklch(start + (end - start) * i / (count - 1), chroma, hue) for i in range(count)]


def _diverging(sources: tuple[str, ...], count: int, *, dark: bool) -> list[str]:
    if count == 1:
        return ["#999999"]
    # Preserve two team hues where available. A neutral middle denotes zero.
    _, c1, h1 = to_oklch(sources[0])
    second = sources[1] if len(sources) > 1 else sources[0]
    _, c2, h2 = to_oklch(second)
    end_l, center_l = ((0.76, 0.42) if dark else (0.39, 0.72))
    result: list[str] = []
    for i in range(count):
        pos = i / (count - 1) * 2 - 1
        strength = abs(pos)
        hue, chroma = (h1, c1) if pos < 0 else (h2, c2)
        result.append(from_oklch(center_l + (end_l - center_l) * strength, chroma * strength, hue))
    return result


def get_palette(
    team: str,
    *,
    chart_type: str = "categorical",
    n_colors: int = 4,
    theme: str = "light",
    accessibility: str = "wcag-aa",
    preserve_brand: bool = True,
) -> Palette:
    """Build chart colors with source provenance and deterministic accessibility warnings.

    preserve_brand keeps the official/source HEX values in original_colors; when
    accessibility is enabled, display colors may be adjusted. Use the exact
    original values via get_team_colors for identity-critical artwork.
    """
    if chart_type not in ("categorical", "sequential", "diverging"):
        raise ValueError("chart_type must be categorical, sequential, or diverging")
    if theme not in ("light", "dark"):
        raise ValueError("theme must be light or dark")
    if accessibility not in ("wcag-aa", "none"):
        raise ValueError("accessibility must be wcag-aa or none")
    if isinstance(n_colors, bool) or not isinstance(n_colors, int) or not (1 <= n_colors <= 20):
        raise ValueError("n_colors must be an integer between 1 and 20")
    entry = get_team(team)
    sources = tuple(get_team_colors(team)[role] for role in _ROLES)
    dark = theme == "dark"
    background = "#101820" if dark else "#FFFFFF"
    if chart_type == "categorical":
        colors = _categorical(sources, n_colors)
    elif chart_type == "sequential":
        colors = _sequential(sources, n_colors, dark=dark)
    else:
        colors = _diverging(sources, n_colors, dark=dark)
    original_display = list(colors)
    if accessibility == "wcag-aa":
        colors = [ensure_contrast(c, background, 3.0) for c in colors]
    ratios = tuple(round(contrast_ratio(c, background), 3) for c in colors)
    adjusted = tuple(a != b for a, b in zip(original_display, colors))
    warnings: list[str] = []
    if any(adjusted):
        warnings.append("Display colors adjusted toward >=3:1 contrast against the supplied background; source HEX values are unchanged.")
    if n_colors > len(_distinct(sources)) and chart_type == "categorical":
        warnings.append("Additional category colors are generated variations, not official team colors.")
    report = audit_palette(colors, background=background)
    warnings.extend(f"{issue.code}: {issue.message} ({', '.join(issue.colors)})" for issue in report.issues)
    if chart_type == "diverging":
        warnings.append("Diverging palettes are for signed deviations around a meaningful zero; verify color-to-semantics mapping.")
    if not preserve_brand:
        warnings.append("preserve_brand=False is deprecated as a no-op; source colors are always retained for provenance.")
    return Palette(entry["id"], entry["name"], chart_type, theme, tuple(colors), sources, background,
                   best_text_color(background), tuple(dict.fromkeys(warnings)), ratios, adjusted)
