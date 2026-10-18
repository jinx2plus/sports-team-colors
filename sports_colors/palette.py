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
    distance_oklab,
    ensure_contrast,
    from_oklch,
    normalize_hex,
    relative_luminance,
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
    root = Path(__file__).resolve().parent.parent
    project_data = root / "data"
    bundled_data = Path(__file__).resolve().parent / "data"
    # The directory adjacent to a wheel's site-packages may contain unrelated
    # data/. Only prefer the checkout when its project files AND catalog exist.
    is_checkout = (root / "pyproject.toml").is_file() and (root / "setup.py").is_file()
    is_complete = all((project_data / f"{league}.json").is_file() for league in _LEAGUES)
    data_dir = project_data if is_checkout and is_complete else bundled_data
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


def _accessible_categorical(colors: list[str], background: str) -> tuple[list[str], int]:
    """Fix contrast while keeping categorical swatches perceptually distinct.

    WCAG correction can collapse distinct light source colors into identical
    gray shades. Prefer a different lightness of the same hue; synthesize hues
    only if that cannot produce a sufficiently different accessible color.
    """
    chosen: list[str] = []
    replacements = 0
    dark = relative_luminance(background) < 0.5
    for source in colors:
        candidate = ensure_contrast(source, background, 3.0)
        if candidate not in chosen and all(distance_oklab(candidate, prev) >= 0.07 for prev in chosen):
            chosen.append(candidate)
            continue
        l, c, h = to_oklch(source)
        alternatives: list[str] = []
        for delta in (-0.12, 0.12, -0.22, 0.22, -0.34, 0.34, -0.44, 0.44):
            alternate = from_oklch(max(0.06, min(0.95, l + delta)), c, h)
            alternatives.append(ensure_contrast(alternate, background, 3.0))
        for step in range(1, 101):
            hue = h + step * 2.399963229728653  # golden-angle hue offsets
            for lightness in ((0.72, 0.82, 0.63) if dark else (0.45, 0.37, 0.53)):
                alternate = from_oklch(lightness, max(c, 0.14), hue)
                alternatives.append(ensure_contrast(alternate, background, 3.0))
        match = next((value for value in alternatives
                      if value not in chosen
                      and all(distance_oklab(value, prev) >= 0.09 for prev in chosen)), None)
        if match is None:
            raise ValueError("Cannot generate distinguishable accessible categorical colors")
        chosen.append(match)
        replacements += 1
    return chosen, replacements


def _color_at_luminance(source: str, target: float, chroma_scale: float) -> str:
    """Find a display color with measured relative luminance near target."""
    _, chroma, hue = to_oklch(source)
    chroma *= chroma_scale
    lo, hi = 0.0, 1.0
    for _ in range(26):
        mid = (lo + hi) / 2
        if relative_luminance(from_oklch(mid, chroma, hue)) < target:
            lo = mid
        else:
            hi = mid
    candidates = (from_oklch(lo, chroma, hue), from_oklch(hi, chroma, hue))
    return min(candidates, key=lambda color: abs(relative_luminance(color) - target))


def _accessible_diverging(colors: list[str], *, dark: bool, background: str) -> list[str]:
    """Maintain magnitude order on both sides of the zero midpoint.

    Contrast targeting by each swatch's original OKLCH lightness could invert
    zero-adjacent bins. Instead set targets in measured sRGB luminance space,
    with the neutral midpoint and both end magnitudes ordered outward.
    """
    if len(colors) == 1:
        return [ensure_contrast(colors[0], background, 3.0)]
    background_y = relative_luminance(background)
    center_y = max(0.16, 3.0 * (background_y + 0.05) - 0.05 + 0.02) if dark else min(
        0.28, (background_y + 0.05) / 3.0 - 0.05 - 0.02)
    edge_y = 0.55 if dark else 0.055
    count = len(colors)
    positions = [abs(2 * i / (count - 1) - 1) for i in range(count)]
    targets = [center_y + (edge_y - center_y) * pos for pos in positions]
    for chroma_scale in (1.0, 0.85, 0.65, 0.45, 0.3):
        selected = [_color_at_luminance(src, y, chroma_scale) for src, y in zip(colors, targets)]
        values = [relative_luminance(c) for c in selected]
        contrast_ok = all(contrast_ratio(color, background) >= 3.0 for color in selected)
        ordered = True
        for i in range(count - 1):
            delta_strength = positions[i + 1] - positions[i]
            delta_y = values[i + 1] - values[i]
            if abs(delta_strength) < 1e-8:
                if abs(delta_y) >= 0.005:
                    ordered = False
                    break
            elif delta_strength * delta_y * (1 if dark else -1) <= 1e-6:
                ordered = False
                break
        if contrast_ok and ordered:
            return selected
    raise ValueError("Cannot construct an accessible diverging palette preserving magnitude order")


def _accessible_sequential(sources: tuple[str, ...], count: int, *, dark: bool, background: str) -> list[str]:
    """Constrain the *whole* ordered ramp, not individual swatches.

    Per-swatch contrast fixes can pull the first two bins past one another.
    Shift the OKLCH lightness domain together until all swatches meet contrast
    while their measured sRGB relative luminance is strictly monotonic.
    """
    if count == 1:
        return [ensure_contrast(sources[0], background, 3.0)]
    _, chroma, hue = to_oklch(sources[0])
    initial_start, initial_end = ((0.48, 0.88) if dark else (0.64, 0.25))
    direction = 1 if dark else -1
    for chroma_scale in (1.0, 0.85, 0.65, 0.4, 0.2, 0.0):
        for step in range(95):
            shift = direction * step / 200
            start = initial_start + shift
            end = max(0.02, min(0.98, initial_end + shift))
            if not 0.02 <= start <= 0.98 or (end - start) * direction < 0.12:
                break
            colors = [from_oklch(start + (end - start) * i / (count - 1),
                                  chroma * chroma_scale, hue) for i in range(count)]
            values = [relative_luminance(c) for c in colors]
            if (all(contrast_ratio(c, background) >= 3.0 for c in colors)
                    and all((values[i+1] - values[i]) * direction > 1e-6
                            for i in range(count - 1))):
                return colors
    raise ValueError("Cannot construct a monotonic, >=3:1 sequential palette for this team")


def _diverging(sources: tuple[str, ...], count: int, *, dark: bool) -> tuple[list[str], bool]:
    """Distinct opposing hues are essential to encode signed values.

    Prefer substantially different chromatic team colors; otherwise synthesize
    a complementary hue, or use a blue/orange pair for entirely neutral teams.
    The returned boolean notes that non-brand fallback hues were necessary.
    """
    if count == 1:
        return ["#999999"], False
    chromatic = [(c, h) for source in sources for _, c, h in [to_oklch(source)] if c >= 0.04]
    fallback = False
    if not chromatic:
        _, c1, h1 = to_oklch("#4477AA")
        _, c2, h2 = to_oklch("#CC6633")
        fallback = True
    else:
        c1, h1 = chromatic[0]
        alternatives = sorted(chromatic[1:],
                              key=lambda item: abs(math.atan2(math.sin(item[1] - h1),
                                                             math.cos(item[1] - h1))), reverse=True)
        if alternatives and abs(math.atan2(math.sin(alternatives[0][1] - h1),
                                           math.cos(alternatives[0][1] - h1))) >= math.pi / 3:
            c2, h2 = alternatives[0]
        else:
            c2, h2 = max(0.12, c1), h1 + math.pi
            fallback = True
    end_l, center_l = ((0.76, 0.42) if dark else (0.39, 0.72))
    result: list[str] = []
    for i in range(count):
        pos = i / (count - 1) * 2 - 1
        strength = abs(pos)
        hue, chroma = (h1, c1) if pos < 0 else (h2, c2)
        result.append(from_oklch(center_l + (end_l - center_l) * strength, chroma * strength, hue))
    return result, fallback


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
    fallback_diverging_hues = False
    if chart_type == "categorical":
        colors = _categorical(sources, n_colors)
    elif chart_type == "sequential":
        colors = _sequential(sources, n_colors, dark=dark)
    else:
        colors, fallback_diverging_hues = _diverging(sources, n_colors, dark=dark)
    original_display = list(colors)
    categorical_replacements = 0
    if accessibility == "wcag-aa":
        if chart_type == "sequential":
            colors = _accessible_sequential(sources, n_colors, dark=dark, background=background)
        elif chart_type == "diverging":
            colors = _accessible_diverging(colors, dark=dark, background=background)
        else:
            colors, categorical_replacements = _accessible_categorical(colors, background)
    ratios = tuple(round(contrast_ratio(c, background), 3) for c in colors)
    adjusted = tuple(a != b for a, b in zip(original_display, colors))
    warnings: list[str] = []
    if any(adjusted):
        warnings.append("Display colors adjusted toward >=3:1 contrast against the supplied background; source HEX values are unchanged.")
    if n_colors > len(_distinct(sources)) and chart_type == "categorical":
        warnings.append("Additional category colors are generated variations, not official team colors.")
    if categorical_replacements:
        warnings.append(f"Replaced {categorical_replacements} contrast-colliding category colors with distinct display variations; generated colors are not official team colors.")
    report = audit_palette(colors, background=background)
    warnings.extend(f"{issue.code}: {issue.message} ({', '.join(issue.colors)})" for issue in report.issues)
    if chart_type == "diverging":
        warnings.append("Diverging palettes are for signed deviations around a meaningful zero; verify color-to-semantics mapping.")
        if fallback_diverging_hues:
            warnings.append("Insufficient distinguishable team hues: synthesized diverging colors are not official team colors.")
    if not preserve_brand:
        warnings.append("preserve_brand=False is deprecated as a no-op; source colors are always retained for provenance.")
    return Palette(entry["id"], entry["name"], chart_type, theme, tuple(colors), sources, background,
                   best_text_color(background), tuple(dict.fromkeys(warnings)), ratios, adjusted)
