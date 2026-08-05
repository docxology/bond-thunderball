"""Figure generation for the DISCO VOLANTE manuscript.

Renders deterministic, publication-style figures for the six domain
concepts into ``output/figures/``:

* :func:`plot_ndl_curve` — no-decompression limit vs. depth (dive planning).
* :func:`plot_convoy_screen` — polar escort-screen coverage (convoy integrity).
* :func:`plot_submersible_range` — range vs. speed trade-off (logistics).
* :func:`plot_transmission_loss` — passive-sonar transmission loss vs. range.
* :func:`plot_drift_geometry` — set-and-drift dead-reckoning geometry.

The single orchestrator :func:`render_all_figures` produces all five and
returns their paths. All curves are evaluated deterministically from the
domain math; there is no randomness.
"""

from __future__ import annotations

import os

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

from .convoy_integrity import coverage_fraction, is_bearing_covered
from .current_navigation import drift_vector
from .dive_planner import BuhlmannModel, bottom_time_from_air, compute_ndl
from .sonar_detection import transmission_loss
from .submersible_logistics import range_nm

__all__ = [
    "plot_convoy_screen",
    "plot_drift_geometry",
    "plot_ndl_curve",
    "plot_submersible_range",
    "plot_transmission_loss",
    "render_all_figures",
]

#: Output directory for figures, relative to the package root.
FIGURES_OUT = "output/figures"

#: Flagship recovery-dive parameters used for figure defaults (cylinder litres,
#: fill bar, SAC L/min, working depth m). Mirrors ``manuscript/config.yaml``.
FLAGSHIP_DIVE = (12.0, 207.0, 20.0, 40.0)


def _out_path(figures_out: str, name: str) -> str:
    os.makedirs(figures_out, exist_ok=True)
    return os.path.join(figures_out, name)


def _flagship_bottom_hours() -> float:
    """Gas-limited bottom time (hours) of the flagship recovery profile."""
    capacity_l, fill_bar, sac_lmin, depth_m = FLAGSHIP_DIVE
    return bottom_time_from_air(capacity_l * fill_bar, sac_lmin, depth_m) / 60.0


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
    """Render a polar escort-screen coverage rosette for a set of bearings.

    Each of 360 sample bearings is tested against the *actual* screen with
    :func:`~thunderball.convoy_integrity.is_bearing_covered`, so the filled
    lobes are the sectors these escorts really watch and the notches are the
    real uncovered gaps. Escort bearings are marked on the rim.
    """
    fig, ax = plt.subplots(figsize=(5.0, 5.0), subplot_kw={"projection": "polar"})
    samples = np.linspace(0.0, 360.0, 360, endpoint=False)
    radii = np.array(
        [
            1.0 if is_bearing_covered(float(t), bearings, half_angle_deg) else 0.0
            for t in samples
        ]
    )
    # Close the ring: repeat the first sample at 360 deg so the filled lobe has
    # no cosmetic notch at the 0/360 seam.
    samples = np.append(samples, 360.0)
    radii = np.append(radii, radii[0])
    theta = np.deg2rad(samples)
    coverage = coverage_fraction(bearings, half_angle_deg)
    ax.fill_between(theta, 0.0, radii, color="#b45309", alpha=0.30, step="mid")
    ax.plot(theta, radii, color="#b45309", linewidth=1.6, drawstyle="steps-mid")
    ax.plot(
        np.deg2rad(np.asarray(bearings, dtype=float)),
        np.ones(len(bearings)),
        "o",
        color="#1e3a8a",
        markersize=5.0,
        label="escorts",
    )
    ax.set_ylim(0.0, 1.15)
    ax.set_yticks([])
    ax.set_theta_zero_location("N")  # type: ignore[attr-defined]
    ax.set_theta_direction(-1)  # type: ignore[attr-defined]
    ax.set_title(
        f"Escort screen coverage: {coverage * 100:.0f}% of the perimeter\n"
        f"({len(bearings)} escorts, half-angle {half_angle_deg:.0f}°)"
    )
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


def plot_transmission_loss(
    f_khz: float = 10.0,
    sl_db: float = 150.0,
    nl_db: float = 75.0,
    di_db: float = 15.0,
    dt_db: float = 10.0,
    figures_out: str = FIGURES_OUT,
) -> str:
    """Render passive-sonar transmission loss vs. range with the detection
    threshold marked (the crossing is the detection range)."""
    ranges = np.linspace(1.0, 60.0, 200)
    tls = np.array([transmission_loss(float(r), f_khz) for r in ranges])
    budget = sl_db - (nl_db - di_db) - dt_db

    fig, ax = plt.subplots(figsize=(6.2, 4.2))
    ax.plot(ranges, tls, color="#7c3aed", linewidth=2.0)
    ax.axhline(budget, color="#dc2626", linestyle="--", linewidth=1.4)
    ax.text(2.0, budget + 2.0, f"detection budget {budget:.0f} dB", color="#dc2626")
    ax.set_xlabel("Range (nm)")
    ax.set_ylabel("Transmission loss (dB)")
    ax.set_title(f"Passive-sonar transmission loss at {f_khz:.1f} kHz (Thorp)")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    path = _out_path(figures_out, "transmission_loss.png")
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def plot_drift_geometry(
    set_deg: float = 90.0,
    drift_knots: float = 0.8,
    duration_h: float | None = None,
    figures_out: str = FIGURES_OUT,
) -> str:
    """Render the set-and-drift geometry over the dive's bottom time.

    ``duration_h`` defaults to the gas-limited bottom time of the flagship
    recovery profile, computed from the domain core rather than pinned to a
    literal, so the figure moves when the dive parameters move.
    """
    if duration_h is None:
        duration_h = _flagship_bottom_hours()
    cur_e, cur_n = drift_vector(set_deg, drift_knots)
    arrow_e = cur_e * duration_h
    arrow_n = cur_n * duration_h
    drift = float(np.hypot(arrow_e, arrow_n))

    fig, ax = plt.subplots(figsize=(5.6, 5.6))
    ax.arrow(
        0.0,
        0.0,
        arrow_e,
        arrow_n,
        head_width=0.06,
        head_length=0.06,
        fc="#0f766e",
        ec="#0f766e",
    )
    ax.set_xlim(-0.5, 0.5)
    ax.set_ylim(-0.5, 0.5)
    ax.set_aspect("equal")
    ax.set_xlabel("East (nm)")
    ax.set_ylabel("North (nm)")
    ax.set_title(
        f"Set-and-drift over {duration_h:.2f} h (drift {drift:.2f} nm, "
        f"set {set_deg:.0f}°)"
    )
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    path = _out_path(figures_out, "drift_geometry.png")
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def render_all_figures(
    bearings: tuple[float, ...] = (0.0, 45.0, 90.0, 135.0, 180.0, 225.0, 270.0, 315.0),
    half_angle_deg: float = 30.0,
    energy_kwh: float = 400.0,
    drag_coeff: float = 0.035,
    hotel_kw: float = 2.0,
    f_khz: float = 10.0,
    figures_out: str = FIGURES_OUT,
) -> list[str]:
    """Render every concept figure and return the list of written paths."""
    paths = [
        plot_ndl_curve(figures_out=figures_out),
        plot_convoy_screen(bearings, half_angle_deg, figures_out=figures_out),
        plot_submersible_range(
            energy_kwh, drag_coeff, hotel_kw, figures_out=figures_out
        ),
        plot_transmission_loss(f_khz=f_khz, figures_out=figures_out),
        plot_drift_geometry(figures_out=figures_out),
    ]
    return paths
