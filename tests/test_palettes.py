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


@pytest.mark.parametrize("theme", ["light", "dark"])
def test_accessible_sequential_is_monotonic_for_every_team(theme):
    """Contrast correction must not invert magnitude bins or collapse swatches."""
    from sports_colors.color_math import relative_luminance

    direction = 1 if theme == "dark" else -1
    for team in all_teams():
        for count in (5, 10, 20):
            p = get_palette(team["id"], chart_type="sequential", theme=theme,
                            n_colors=count, accessibility="wcag-aa")
            luminances = [relative_luminance(color) for color in p.colors]
            assert all(contrast_ratio(color, p.background) >= 3.0 for color in p.colors), team["id"]
            assert all((b-a) * direction > 1e-6 for a, b in zip(luminances, luminances[1:])), (team["id"], theme, p.colors)


def test_accessible_sequential_reports_color_adjustments():
    p = get_palette("mlb-diamondbacks", chart_type="sequential", theme="dark", n_colors=10)
    assert any(p.adjusted)


@pytest.mark.parametrize("team", ["nba-nets", "epl-fulham"])
@pytest.mark.parametrize("theme", ["light", "dark"])
@pytest.mark.parametrize("accessibility", ["none", "wcag-aa"])
def test_neutral_team_diverging_has_distinct_opposing_hues(team, theme, accessibility):
    from sports_colors.color_math import distance_oklab

    p = get_palette(team, chart_type="diverging", n_colors=5,
                    theme=theme, accessibility=accessibility)
    assert distance_oklab(p.colors[0], p.colors[-1]) > 0.1
    assert len(set(p.colors)) == 5
    assert any("synthesized" in warning for warning in p.warnings)


def test_installed_package_does_not_use_unrelated_site_packages_data(tmp_path, monkeypatch):
    """An unrelated sibling /data must not shadow packaged sports_colors/data."""
    import json
    import sports_colors.palette as palette_module

    site = tmp_path / "site-packages"
    sibling = site / "data"
    bundled = site / "sports_colors" / "data"
    sibling.mkdir(parents=True)
    bundled.mkdir(parents=True)
    for league in ("mlb", "nba", "nfl", "epl"):
        base = {"name": "Fixture", "num_id": 1, "logo_url": "https://example.com/image.png",
                "colors": {"primary": "#000000", "secondary": "#FFFFFF",
                           "tertiary": "#777777", "quaternary": "#EE9900"}}
        bundled_team = dict(base, id=f"{league}-from-wheel")
        wrong_team = dict(base, id=f"{league}-from-unrelated-data")
        (bundled / f"{league}.json").write_text(json.dumps([bundled_team]), encoding="utf-8")
        (sibling / f"{league}.json").write_text(json.dumps([wrong_team]), encoding="utf-8")
    palette_module.all_teams.cache_clear()
    try:
        with monkeypatch.context() as m:
            m.setattr(palette_module, "__file__", str(site / "sports_colors" / "palette.py"))
            found = palette_module.all_teams()
            assert {x["id"] for x in found} == {f"{league}-from-wheel" for league in ("mlb", "nba", "nfl", "epl")}
    finally:
        palette_module.all_teams.cache_clear()


@pytest.mark.parametrize("theme", ["light", "dark"])
@pytest.mark.parametrize("count", [5, 9, 20])
def test_diverging_preserves_magnitude_order_with_accessibility(theme, count):
    """Each side must encode increasing distance from zero with ordered luminance."""
    from sports_colors.color_math import relative_luminance

    direction = 1 if theme == "dark" else -1
    for team in all_teams():
        p = get_palette(team["id"], chart_type="diverging", theme=theme,
                        n_colors=count, accessibility="wcag-aa")
        lum = [relative_luminance(c) for c in p.colors]
        strengths = [abs(2 * i / (count-1) - 1) for i in range(count)]
        assert all(contrast_ratio(c, p.background) >= 3.0 for c in p.colors), team["id"]
        for i in range(count-1):
            delta_strength = strengths[i + 1] - strengths[i]
            delta_y = lum[i + 1] - lum[i]
            if abs(delta_strength) < 1e-8:
                assert abs(delta_y) < 0.005
            else:
                assert delta_strength * delta_y * direction > 1e-6, (team["id"], theme, count, p.colors)


@pytest.mark.parametrize("theme", ["light", "dark"])
@pytest.mark.parametrize("count", [4, 10, 20])
def test_categorical_retains_distinct_swatches_after_contrast(theme, count):
    from sports_colors.color_math import distance_oklab

    for team in all_teams():
        p = get_palette(team["id"], chart_type="categorical", theme=theme,
                        n_colors=count, accessibility="wcag-aa")
        assert len(p.colors) == len(set(p.colors)), (team["id"], theme, count)
        assert all(contrast_ratio(c, p.background) >= 3.0 for c in p.colors), team["id"]
        assert all(distance_oklab(a, b) >= 0.065 for i, a in enumerate(p.colors)
                   for b in p.colors[i+1:]), team["id"]


def test_yankees_duplicate_contrast_correction_is_replaced():
    p = get_palette("mlb-yankees", n_colors=4, accessibility="wcag-aa")
    assert len(set(p.colors)) == 4
    assert any("contrast-colliding category colors" in message for message in p.warnings)
    assert p.original_colors[0] == "#FFFFFF"
    assert p.original_colors[2] == "#E1E1E1"
