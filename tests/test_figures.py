"""Tests for figure generation and the main rendering orchestrator."""

from __future__ import annotations

import os
from pathlib import Path

from thunderball.figures import (
    plot_convoy_screen,
    plot_drift_geometry,
    plot_ndl_curve,
    plot_submersible_range,
    plot_transmission_loss,
    render_all_figures,
)

PROJECT_ROOT = Path(__file__).resolve().parent


def test_plot_ndl_curve_writes_png(tmp_path) -> None:
    out = tmp_path / "figures"
    path = plot_ndl_curve(figures_out=str(out))
    assert os.path.exists(path)
    assert path.endswith(".png")
    assert os.path.getsize(path) > 0


def test_plot_convoy_screen_writes_png(tmp_path) -> None:
    out = tmp_path / "figures"
    path = plot_convoy_screen((0.0, 45.0, 90.0, 180.0), 30.0, figures_out=str(out))
    assert os.path.exists(path)
    assert os.path.getsize(path) > 0


def test_plot_submersible_range_writes_png(tmp_path) -> None:
    out = tmp_path / "figures"
    path = plot_submersible_range(400.0, 0.035, 2.0, figures_out=str(out))
    assert os.path.exists(path)
    assert os.path.getsize(path) > 0


def test_plot_transmission_loss_writes_png(tmp_path) -> None:
    out = tmp_path / "figures"
    path = plot_transmission_loss(f_khz=10.0, figures_out=str(out))
    assert os.path.exists(path)
    assert os.path.getsize(path) > 0


def test_plot_drift_geometry_writes_png(tmp_path) -> None:
    out = tmp_path / "figures"
    path = plot_drift_geometry(
        set_deg=90.0, drift_knots=0.8, duration_h=0.41, figures_out=str(out)
    )
    assert os.path.exists(path)
    assert os.path.getsize(path) > 0


def test_render_all_figures_returns_five_paths(tmp_path) -> None:
    paths = render_all_figures(figures_out=str(tmp_path / "figures"))
    assert len(paths) == 5
    for path in paths:
        assert os.path.exists(path)


def test_convoy_screen_figure_depends_on_the_bearings_it_is_given(tmp_path) -> None:
    """Regression: the polar plot once sampled coverage_fraction() one bearing
    at a time, which is constant for any single escort — so the rendered image
    was identical for every screen. Different screens must render differently.
    """
    dense = plot_convoy_screen(
        (0.0, 45.0, 90.0, 135.0, 180.0, 225.0, 270.0, 315.0),
        30.0,
        figures_out=str(tmp_path / "dense"),
    )
    sparse = plot_convoy_screen(
        (0.0, 180.0), 30.0, figures_out=str(tmp_path / "sparse")
    )
    assert Path(dense).read_bytes() != Path(sparse).read_bytes()


def test_drift_geometry_duration_defaults_to_the_domain_bottom_time(
    tmp_path,
) -> None:
    """The default duration must come from the dive math, not a literal — and
    it must be the *planned* bottom time the team actually flies, min(air,
    NDL), not the longer air-budget limit decompression pre-empts."""
    from thunderball.dive_planner import bottom_time_from_air, plan_dive
    from thunderball.figures import FLAGSHIP_DIVE, _flagship_bottom_hours

    capacity_l, fill_bar, sac_lmin, depth_m = FLAGSHIP_DIVE
    plan = plan_dive(
        depth_m=depth_m,
        cylinder_capacity_l=capacity_l,
        fill_pressure_bar=fill_bar,
        sac_rate_lmin=sac_lmin,
    )
    expected = plan.bottom_minutes / 60.0
    assert _flagship_bottom_hours() == expected
    # Decompression binds first here, so the air budget is strictly longer:
    # the two durations are distinguishable and the default is the right one.
    air_hours = bottom_time_from_air(capacity_l * fill_bar, sac_lmin, depth_m) / 60.0
    assert air_hours > expected
    assert 0.1 < expected < 0.3
    # The default path and the explicit path render the same figure.
    default = plot_drift_geometry(figures_out=str(tmp_path / "default"))
    explicit = plot_drift_geometry(
        duration_h=expected, figures_out=str(tmp_path / "explicit")
    )
    assert Path(default).read_bytes() == Path(explicit).read_bytes()
