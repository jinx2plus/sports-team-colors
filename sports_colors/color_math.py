"""Dependency-free sRGB/OKLab conversion and WCAG contrast helpers."""

from __future__ import annotations

import math
import re

_HEX_PATTERN = re.compile(r"^#[0-9a-fA-F]{6}$")


def normalize_hex(value: str) -> str:
    if not isinstance(value, str) or not _HEX_PATTERN.fullmatch(value):
        raise ValueError(f"Expected #RRGGBB color, got {value!r}")
    return value.upper()


def hex_to_rgb(value: str) -> tuple[float, float, float]:
    value = normalize_hex(value)
    return tuple(int(value[i : i + 2], 16) / 255 for i in (1, 3, 5))


def rgb_to_hex(rgb: tuple[float, float, float]) -> str:
    return "#" + "".join(f"{round(max(0.0, min(1.0, c)) * 255):02X}" for c in rgb)


def _linear(v: float) -> float:
    return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4


def _srgb(v: float) -> float:
    v = max(0.0, min(1.0, v))
    return v * 12.92 if v <= 0.0031308 else 1.055 * v ** (1 / 2.4) - 0.055


def relative_luminance(color: str) -> float:
    r, g, b = (_linear(x) for x in hex_to_rgb(color))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(foreground: str, background: str) -> float:
    a, b = relative_luminance(foreground), relative_luminance(background)
    return (max(a, b) + 0.05) / (min(a, b) + 0.05)


def to_oklab(color: str) -> tuple[float, float, float]:
    r, g, b = (_linear(c) for c in hex_to_rgb(color))
    l = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b
    m = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b
    s = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b
    l, m, s = l ** (1 / 3), m ** (1 / 3), s ** (1 / 3)
    return (
        0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s,
        1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s,
        0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s,
    )


def to_oklch(color: str) -> tuple[float, float, float]:
    l, a, b = to_oklab(color)
    return l, math.hypot(a, b), math.atan2(b, a)


def from_oklch(lightness: float, chroma: float, hue_radians: float) -> str:
    """Convert OKLCH to clipped sRGB; not a perceptual gamut mapping algorithm."""
    l = max(0.0, min(1.0, lightness))
    a, b = chroma * math.cos(hue_radians), chroma * math.sin(hue_radians)
    ll = (l + 0.3963377774 * a + 0.2158037573 * b) ** 3
    mm = (l - 0.1055613458 * a - 0.0638541728 * b) ** 3
    ss = (l - 0.0894841775 * a - 1.2914855480 * b) ** 3
    r = 4.0767416621 * ll - 3.3077115913 * mm + 0.2309699292 * ss
    g = -1.2684380046 * ll + 2.6097574011 * mm - 0.3413193965 * ss
    bb = -0.0041960863 * ll - 0.7034186147 * mm + 1.7076147010 * ss
    return rgb_to_hex((_srgb(r), _srgb(g), _srgb(bb)))


def distance_oklab(a: str, b: str) -> float:
    p, q = to_oklab(a), to_oklab(b)
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(p, q)))


def ensure_contrast(color: str, background: str, minimum: float = 3.0) -> str:
    """Adjust OKLCH lightness, preserving original hue as far as sRGB permits."""
    color, background = normalize_hex(color), normalize_hex(background)
    if contrast_ratio(color, background) + 1e-9 >= minimum:
        return color
    l, c, h = to_oklch(color)
    direction = -1 if relative_luminance(background) >= 0.5 else 1
    for step in range(1, 101):
        candidate = from_oklch(l + direction * step / 100, c, h)
        if contrast_ratio(candidate, background) + 1e-9 >= minimum:
            return candidate
    return "#000000" if contrast_ratio("#000000", background) >= minimum else "#FFFFFF"


def best_text_color(background: str) -> str:
    return max(("#151515", "#FFFFFF"), key=lambda c: contrast_ratio(c, background))
