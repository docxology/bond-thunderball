"""Figure generation for the DISCO VOLANTE manuscript.

Renders deterministic, publication-style figures for the three domain
concepts into ``output/figures/``:

* :func:`plot_ndl_curve` — no-decompression limit vs. depth (dive planning).
* :func:`plot_convoy_screen` — polar escort-screen coverage (convoy integrity).
* :func:`plot_submersible_range` — range vs. speed trade-off (logistics).

The single orchestrator :func:`render_all_figures` produces all three and
returns their paths. All curves are evaluated deterministically from the
domain math; there is no randomness.
"""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

from .convoy_integrity import coverage_fraction
from .dive_planner import BuhlmannModel, compute_ndl
from .submersible_logistics import range_nm

__all__ = [
    "plot_convoy_screen",
    "plot_ndl_curve",
    "plot_submersible_range",
    "render_all_figures",
]

#: Output directory for figures, relative to the package root.
FIGURES_OUT = "output/figures"


def _out_path(figures_out: str, name: str) -> str:
    import os

    os.makedirs(figures_out, exist_ok=True)
    return os.path.join(figures_out, name)


def plot_ndl_curve(
    model: BuhlmannModel | None = None, figures_out: str = FIGURES_OUT
) -> str:
    """Render the no-decompression limit curve over plausible dive depths."""
    model = model or BuhlmannModel()
    depths = np.linspace(8.0, 45.0, 100)
    ndls = np.array([compute_ndl(float(d), model=model) for d in depths])

    fig, ax = plt.subplots(figsize=(6.2, 4.2))
    ax.plot(depths, ndls, color="#0f766e", linewidth=2.0)
    ax.set_xlabel("Depth (m)")
    ax.set_ylabel("No-decompression limit (min)")
    ax.set_title("Bühlmann ZH-L16A no-decompression limit")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    path = _out_path(figures_out, "ndl_curve.png")
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def plot_convoy_screen(
    bearings: tuple[float, ...],
    half_angle_deg: float = 30.0,
    figures_out: str = FIGURES_OUT,
) -> str:
    """Render a polar escort-screen coverage plot for a set of bearing angles."""
    fig, ax = plt.subplots(figsize=(5.0, 5.0), subplot_kw={"projection": "polar"})
    theta = np.deg2rad(np.linspace(0.0, 360.0, 360))
    radii = np.array(
        [
            coverage_fraction((float(t),), half_angle_deg)
            for t in np.linspace(0, 360, 360)
        ]
    )
    ax.plot(theta, radii, color="#b45309", linewidth=2.0)
    ax.fill(theta, radii, color="#b45309", alpha=0.25)
    ax.set_theta_zero_location("N")  # type: ignore[attr-defined]
    ax.set_theta_direction(-1)  # type: ignore[attr-defined]
    ax.set_title(f"Escort screen coverage (half-angle {half_angle_deg:.0f}°)")
    fig.tight_layout()
    path = _out_path(figures_out, "convoy_screen.png")
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def plot_submersible_range(
    energy_kwh: float,
    drag_coeff: float,
    hotel_kw: float,
    figures_out: str = FIGURES_OUT,
) -> str:
    """Render the submersible range-vs-speed curve and its optimum marker."""
    speeds = np.linspace(1.0, 30.0, 200)
    ranges = np.array(
        [range_nm(energy_kwh, float(v), drag_coeff, hotel_kw) for v in speeds]
    )
    best_i = int(np.argmax(ranges))

    fig, ax = plt.subplots(figsize=(6.2, 4.2))
    ax.plot(speeds, ranges, color="#1e40af", linewidth=2.0)
    ax.plot(
        speeds[best_i],
        ranges[best_i],
        "o",
        color="#dc2626",
        label=f"optimal range {ranges[best_i]:.1f} nm",
    )
    ax.set_xlabel("Speed (knots)")
    ax.set_ylabel("Range (nm)")
    ax.set_title("Submersible range vs. speed (cubic drag + hotel load)")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    path = _out_path(figures_out, "submersible_range.png")
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def render_all_figures(
    bearings: tuple[float, ...] = (0.0, 45.0, 90.0, 135.0, 180.0, 225.0, 270.0, 315.0),
    half_angle_deg: float = 30.0,
    energy_kwh: float = 400.0,
    drag_coeff: float = 0.035,
    hotel_kw: float = 2.0,
    figures_out: str = FIGURES_OUT,
) -> list[str]:
    """Render every concept figure and return the list of written paths."""
    paths = [
        plot_ndl_curve(figures_out=figures_out),
        plot_convoy_screen(bearings, half_angle_deg, figures_out=figures_out),
        plot_submersible_range(
            energy_kwh, drag_coeff, hotel_kw, figures_out=figures_out
        ),
    ]
    return paths
