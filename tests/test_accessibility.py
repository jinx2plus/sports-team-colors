import pytest

from sports_colors import audit_palette, contrast_ratio, ensure_contrast, simulate_cvd
from sports_colors.color_math import normalize_hex


def test_wcag_contrast_reference_black_and_white():
    assert contrast_ratio("#000000", "#FFFFFF") == pytest.approx(21.0)
    assert contrast_ratio("#FFFFFF", "#FFFFFF") == pytest.approx(1.0)


def test_ensure_contrast_modifies_low_contrast_and_preserves_high_contrast():
    assert ensure_contrast("#552583", "#FFFFFF") == "#552583"
    modified = ensure_contrast("#FDB927", "#FFFFFF")
    assert modified != "#FDB927"
    assert contrast_ratio(modified, "#FFFFFF") >= 3.0
    assert contrast_ratio(ensure_contrast("#000000", "#101820"), "#101820") >= 3.0


def test_identical_color_audit_is_error():
    report = audit_palette(["#000000", "#000000"], check_cvd=False)
    assert not report.passed
    assert any(issue.code == "duplicate" for issue in report.issues)


def test_low_contrast_audit_is_error():
    report = audit_palette(["#FFFFFF", "#002D62"], background="#FFFFFF")
    assert not report.passed
    assert any(issue.code == "graphics_contrast" for issue in report.issues)


def test_cvd_output_and_validation():
    assert normalize_hex(simulate_cvd("#CE1141", "deuteranopia")).startswith("#")
    with pytest.raises(ValueError):
        simulate_cvd("#FF0000", "unknown")
    with pytest.raises(ValueError):
        normalize_hex("red")


def test_text_background_note():
    report = audit_palette(["#000000"], background="#FFFFFF")
    assert report.passed
    assert contrast_ratio(report.text_color, report.background) >= 4.5
