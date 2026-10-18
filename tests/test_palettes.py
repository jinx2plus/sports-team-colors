import pytest

from sports_colors import all_teams, contrast_ratio, get_palette, get_team_colors
from sports_colors.color_math import from_oklch, to_oklch


def test_catalog_has_expected_teams_and_valid_hex():
    teams = all_teams()
    assert len(teams) == 112
    assert len({team["id"] for team in teams}) == 112
    for team in teams:
        assert set(team["colors"]) == {"primary", "secondary", "tertiary", "quaternary"}
        assert all(value.startswith("#") and len(value) == 7 for value in team["colors"].values())


def test_raw_colors_are_unchanged():
    original = get_team_colors("nba-lakers")
    palette = get_palette("nba-lakers", n_colors=4)
    assert tuple(original.values()) == palette.original_colors
    assert original["primary"] == "#552583"
    assert palette.team_id == "nba-lakers"


@pytest.mark.parametrize("theme", ["light", "dark"])
@pytest.mark.parametrize("chart_type", ["categorical", "sequential", "diverging"])
def test_accessible_chart_palette(theme, chart_type):
    p = get_palette("nba-lakers", theme=theme, chart_type=chart_type, n_colors=6)
    assert len(p.colors) == 6
    assert all(contrast_ratio(color, p.background) >= 3.0 - 1e-7 for color in p.colors)
    assert all(color.startswith("#") and len(color) == 7 for color in p.colors)


def test_disable_adjustment_warns_about_low_contrast():
    p = get_palette("nba-lakers", n_colors=3, accessibility="none")
    assert p.colors[1] == "#FDB927"
    assert any("graphics_contrast" in warning for warning in p.warnings)


def test_readme_dodgers_order_matches_data():
    assert get_team_colors("mlb-dodgers")["secondary"] == "#FFFFFF"
    assert get_team_colors("mlb-dodgers")["tertiary"] == "#EF3E42"


def test_validation_and_ambiguous_names():
    for kwargs in ({"n_colors": 0}, {"chart_type": "unknown"}, {"theme": "sepia"}, {"accessibility": "AAA"}):
        with pytest.raises(ValueError):
            get_palette("nba-lakers", **kwargs)
    with pytest.raises(ValueError):
        get_palette("nonexistent team")


def test_oklch_roundtrip_approximate():
    for color in ("#005A9C", "#552583", "#7A263A", "#FFFFFF", "#000000"):
        l, c, h = to_oklch(color)
        reconstructed = from_oklch(l, c, h)
        assert all(abs(int(reconstructed[i:i + 2], 16) - int(color[i:i + 2], 16)) <= 2 for i in (1, 3, 5))
