"""Contrast and approximate color-vision-deficiency audits for charts."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations

from .color_math import (
    _linear,
    _srgb,
    best_text_color,
    contrast_ratio,
    distance_oklab,
    hex_to_rgb,
    normalize_hex,
    rgb_to_hex,
)

# Approximate full-severity Machado-style transforms on *linear* RGB.
# Simulations help flag potential problems; they are not diagnostic or a WCAG test.
_MATRICES = {
    "protanopia": ((0.152286, 1.052583, -0.204868), (0.114503, 0.786281, 0.099216), (-0.003882, -0.048116, 1.051998)),
    "deuteranopia": ((0.367322, 0.860646, -0.227968), (0.280085, 0.672501, 0.047413), (-0.011820, 0.042940, 0.968881)),
    "tritanopia": ((1.255528, -0.076749, -0.178779), (-0.078411, 0.930809, 0.147602), (0.004733, 0.691367, 0.303900)),
}


@dataclass(frozen=True)
class AuditIssue:
    code: str
    colors: tuple[str, ...]
    message: str
    severity: str = "warning"


@dataclass(frozen=True)
class AuditReport:
    colors: tuple[str, ...]
    background: str
    issues: tuple[AuditIssue, ...]
    text_color: str

    @property
    def passed(self) -> bool:
        return not any(i.severity == "error" for i in self.issues)


def simulate_cvd(color: str, condition: str = "deuteranopia") -> str:
    if condition not in _MATRICES:
        raise ValueError(f"Unknown CVD condition: {condition!r}")
    values = tuple(_linear(v) for v in hex_to_rgb(color))
    transformed = [sum(x * y for x, y in zip(row, values)) for row in _MATRICES[condition]]
    return rgb_to_hex(tuple(_srgb(v) for v in transformed))


def audit_palette(
    colors: list[str] | tuple[str, ...],
    *,
    background: str = "#FFFFFF",
    graphics_min: float = 3.0,
    pair_min_distance: float = 0.08,
    check_cvd: bool = True,
) -> AuditReport:
    """Audit graphical marks against their supplied adjacent background.

    Graphical contrast only applies to marks necessary to interpret content;
    audit is intentionally conservative and can emit warnings on decoration.
    Pairwise OKLab distance is a heuristic, not a WCAG pass/fail criterion.
    """
    bg = normalize_hex(background)
    palette = tuple(normalize_hex(c) for c in colors)
    issues: list[AuditIssue] = []
    for color in palette:
        ratio = contrast_ratio(color, bg)
        if ratio < graphics_min:
            issues.append(AuditIssue("graphics_contrast", (color,), f"Contrast {ratio:.2f}:1 < {graphics_min:.1f}:1", "error"))
    for i, j in combinations(range(len(palette)), 2):
        first, second = palette[i], palette[j]
        if first == second:
            issues.append(AuditIssue("duplicate", (first, second), "Identical palette entries", "error"))
            continue
        if distance_oklab(first, second) < pair_min_distance:
            issues.append(AuditIssue("similar_colors", (first, second), "Low perceptual distance (OKLab heuristic)"))
        if check_cvd:
            for condition in ("protanopia", "deuteranopia", "tritanopia"):
                if distance_oklab(simulate_cvd(first, condition), simulate_cvd(second, condition)) < pair_min_distance:
                    issues.append(AuditIssue("cvd_similarity", (first, second), f"May be difficult to distinguish under {condition}"))
    return AuditReport(palette, bg, tuple(issues), best_text_color(bg))
