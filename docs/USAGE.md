# Sports Team Colors — Python usage and design rules

The root `data/*.json` catalog is authoritative. The library retains source team colors and constructs **derived chart colors** separately. Source values are not a guarantee of current official team brand standards; check source and season for identity-critical uses.

## Install and run

```bash
python -m pip install -e .
python -m pip install pytest
python -m pytest -q
```

```python
from sports_colors import get_palette, get_team_colors, audit_palette

original = get_team_colors('nba-lakers')
palette = get_palette('nba-lakers', chart_type='categorical', n_colors=3,
                      theme='light', accessibility='wcag-aa')
print(original)                 # Unchanged source values
print(palette.colors)           # Chart-specific render colors
print(palette.adjusted)         # Which selected display colors were altered
print(palette.contrast_ratios)  # Measured against palette.background
print(palette.warnings)         # Distinction and accessibility warnings
print(audit_palette(palette.colors, background=palette.background).passed)
```

Supported chart types:

- `categorical`: discrete series; team colors first, then generated derivatives if needed.
- `sequential`: one hue with ordered OKLCH lightness; ordered magnitude only. With `wcag-aa`, adjust the **entire** lightness ramp to keep relative luminance strictly monotonic while meeting contrast; never adjust magnitude bins independently.
- `diverging`: two distinguishable hues with neutral midpoint; **only** for signed values with a meaningful reference point. If the team palette is achromatic or lacks two distinct chromatic hues, generated fallback hues are used and marked as **non-official** in warnings.

Chart rendering snippets are in `examples/matplotlib_demo.py` and `examples/plotly_demo.py`; those plotting libraries are optional. `matplotlib_rc` returns an `rc_context` dictionary, and `plotly_layout` returns a figure layout dictionary.

## Accessibility and limitations

- Compare a visible mark with its **actual adjacent background**; 3:1 for essential non-text graphics, and 4.5:1 for ordinary text are useful WCAG AA checks. These do **not** certify WCAG compliance for a chart.
- OKLab pair distances and simulated protanopia/deuteranopia/tritanopia are **heuristics**. They cannot guarantee that every category is distinguishable. Test legends, labels, patterns and line styles with real charts.
- The adjustment logic preserves source hues approximately while changing OKLCH lightness and clipping to sRGB. Extra generated categorical hues are **not** official team colors.
- Chart colors may still be similar to each other even if each achieves 3:1 against the background; inspect `palette.warnings`.
- For crash severity, signal states, congestion risk or other **semantic safety encodings**, keep the project's standardized red/amber/green thresholds. Use team colors only for nonsemantic UI chrome and typography. Avoid assigning arbitrary team hues to risk categories.
- `preserve_brand=True` keeps the raw source colors in `palette.original_colors`; it does **not** prevent derived display colors from being adjusted for readability. `get_team_colors` always returns unmodified values.
- Logos are remote ESPN URLs, not bundled assets. Rights to logos/colors and any association with clubs are **not** granted by this repository.

## Data maintenance

`data/{mlb,nba,nfl,epl}.json` remains the source of truth. `setup.py` packages the same four JSON files into wheels. Do not directly edit the built-wheel copies. Recheck primary/secondary source links, dates and logos when teams rebrand. The CSV in `data/all_teams_colors.csv` and README tables should be regenerated when JSON changes. See `SOURCES.md` for existing references and verification caveats.
