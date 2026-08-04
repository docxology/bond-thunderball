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
