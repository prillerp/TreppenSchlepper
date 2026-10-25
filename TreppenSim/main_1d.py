"""
TreppenSchlepper — 1-D vertical simulation entry point.

Runs Phase 2 (Elevation) and Phase 4 (Retraction), prints a summary,
and saves plots to results/.

Usage:
    python main_1d.py

Override parameters by editing the SimParams construction below.
"""

import matplotlib
matplotlib.use("Agg")  # headless backend — no display required
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
import os

from sim.params import SimParams, StairParams, MassParams, ActuatorParams
from sim.sim_1d import run_all, PhaseResult


# ── Parameters ────────────────────────────────────────────────────────────────

params = SimParams(
    stair=StairParams(
        rise_height=0.18,  # m  — 18 cm (typical 18/27 stair)
        tread_depth=0.27,  # m
    ),
    mass=MassParams(
        m_outer_shell=9.0,      # kg  Config B — structure only
        m_payload=20.0,         # kg  design-point cargo load
        m_inner_shell=4.0,      # kg
        m_foot_plate=8.0,       # kg  Config B — incl. battery, MCU, sensors
        m_elevator_cyl=3.0,     # kg  (split equally upper/lower)
        m_hc=1.5,               # kg  HC body rides up with OS in Phase 2
        ec_upper_fraction=0.5,
    ),
    actuator=ActuatorParams(
        v_max=0.03,         # m/s   30 mm/s — TiMOTION TA2 PWM-limited speed
        a_max=0.10,         # m/s²  max acceleration
        F_coulomb=30.0,     # N     Coulomb friction (lead-screw)
        damping=80.0,       # N·s/m viscous term
    ),
    dt=0.001,  # s
)


# ── Run simulation ─────────────────────────────────────────────────────────────

phase2, phase4 = run_all(params)

print()
print(phase2.summary())
print()
print(phase4.summary())
print()
print(f"Total energy both strokes : {phase2.E + phase4.E:.2f} J")
print(
    f"Total duration both strokes: "
    f"{phase2.duration + phase4.duration:.3f} s"
)


# ── Plot helpers ───────────────────────────────────────────────────────────────

os.makedirs("results", exist_ok=True)


def _fmt(ax, xlabel, ylabel, title):
    ax.set_xlabel(xlabel, fontsize=9)
    ax.set_ylabel(ylabel, fontsize=9)
    ax.set_title(title, fontsize=10, fontweight="bold")
    handles, _ = ax.get_legend_handles_labels()
    if handles:
        ax.legend(fontsize=7.5)
    ax.grid(True, alpha=0.3)
    ax.tick_params(labelsize=8)


def plot_phase(result: PhaseResult, color: str, out_path: str) -> None:
    """4-panel plot for a single phase: position, velocity, force, power."""
    rise_cm = result.displacement * 100
    fig = plt.figure(figsize=(12, 9))
    fig.suptitle(
        f"TreppenSchlepper — 1-D Vertical Simulation\n"
        f"{result.label}\n"
        f"Rise = {rise_cm:.0f} cm  |  "
        f"Mass = {result.mass:.1f} kg  |  "
        f"v_max = {params.actuator.v_max * 100:.0f} cm/s",
        fontsize=12,
        fontweight="bold",
    )

    gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.42, wspace=0.32)
    ax_z = fig.add_subplot(gs[0, 0])
    ax_v = fig.add_subplot(gs[0, 1])
    ax_f = fig.add_subplot(gs[1, 0])
    ax_p = fig.add_subplot(gs[1, 1])

    lw = 2.0
    ax_z.plot(result.t, result.z * 100, color=color, lw=lw)
    ax_v.plot(result.t, result.zdot * 100, color=color, lw=lw)
    ax_f.plot(result.t, result.F_act, color=color, lw=lw)
    ax_p.plot(result.t, result.P, color=color, lw=lw)

    ax_z.axhline(
        rise_cm, color="gray", ls=":", lw=1,
        label=f"target {rise_cm:.0f} cm",
    )
    ax_f.axhline(
        result.F_static, color=color, ls=":", lw=1, alpha=0.6,
        label=f"static hold {result.F_static:.0f} N",
    )

    i_pk = int(np.argmax(result.F_act))
    ax_f.annotate(
        f"peak {result.F_peak:.0f} N",
        xy=(result.t[i_pk], result.F_act[i_pk]),
        xytext=(
            result.t[i_pk] + result.duration * 0.05,
            result.F_act[i_pk] * 1.02,
        ),
        fontsize=8,
        color=color,
        arrowprops=dict(arrowstyle="->", color=color, lw=0.8),
    )

    _fmt(ax_z, "Time (s)", "Position (cm)", "Position z(t)")
    _fmt(ax_v, "Time (s)", "Velocity (cm/s)", "Velocity ż(t)")
    _fmt(ax_f, "Time (s)", "Force (N)", "Actuator Force F(t)")
    _fmt(ax_p, "Time (s)", "Power (W)", "Actuator Power P(t)")

    summary = (
        f"Mass: {result.mass:.1f} kg  |  "
        f"Peak force: {result.F_peak:.0f} N  |  "
        f"Peak power: {result.P_peak:.1f} W  |  "
        f"Energy: {result.E:.2f} J  |  "
        f"Duration: {result.duration:.2f} s"
    )
    fig.text(
        0.5, 0.01, summary, ha="center", va="bottom", fontsize=9,
        bbox=dict(
            boxstyle="round,pad=0.4", fc="lightyellow", ec="gray", lw=0.8
        ),
    )

    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Plot saved to {out_path}")


# ── Per-phase plots ────────────────────────────────────────────────────────────

plot_phase(
    phase2,
    color="#1f77b4",
    out_path=os.path.join("results", "sim_1d_phase2.png"),
)
plot_phase(
    phase4,
    color="#d62728",
    out_path=os.path.join("results", "sim_1d_phase4.png"),
)


# ── Combined comparison plot ───────────────────────────────────────────────────

COLORS = {"phase2": "#1f77b4", "phase4": "#d62728"}

fig = plt.figure(figsize=(12, 9))
fig.suptitle(
    "TreppenSchlepper — 1-D Vertical Simulation (Phase 2 vs Phase 4)\n"
    f"Rise = {params.stair.rise_height * 100:.0f} cm  |  "
    f"Payload = {params.mass.m_payload:.0f} kg  |  "
    f"v_max = {params.actuator.v_max * 100:.0f} cm/s",
    fontsize=12,
    fontweight="bold",
)

gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.42, wspace=0.32)
ax_z = fig.add_subplot(gs[0, 0])
ax_v = fig.add_subplot(gs[0, 1])
ax_f = fig.add_subplot(gs[1, 0])
ax_p = fig.add_subplot(gs[1, 1])

for result, key in ((phase2, "phase2"), (phase4, "phase4")):
    c = COLORS[key]
    ls = "-" if key == "phase2" else "--"
    lbl = result.label.split("(")[0].strip()
    ax_z.plot(result.t, result.z * 100, color=c, lw=2, ls=ls, label=lbl)
    ax_v.plot(result.t, result.zdot * 100, color=c, lw=2, ls=ls, label=lbl)
    ax_f.plot(result.t, result.F_act, color=c, lw=2, ls=ls, label=lbl)
    ax_p.plot(result.t, result.P, color=c, lw=2, ls=ls, label=lbl)

ax_z.axhline(
    params.stair.rise_height * 100, color="gray", ls=":", lw=1,
    label=f"target {params.stair.rise_height * 100:.0f} cm",
)
ax_f.axhline(
    phase2.F_static, color=COLORS["phase2"], ls=":", lw=1, alpha=0.6,
    label=f"static Ph2 ({phase2.F_static:.0f} N)",
)
ax_f.axhline(
    phase4.F_static, color=COLORS["phase4"], ls=":", lw=1, alpha=0.6,
    label=f"static Ph4 ({phase4.F_static:.0f} N)",
)

_fmt(ax_z, "Time (s)", "Position (cm)", "Position z(t)")
_fmt(ax_v, "Time (s)", "Velocity (cm/s)", "Velocity ż(t)")
_fmt(ax_f, "Time (s)", "Force (N)", "Actuator Force F(t)")
_fmt(ax_p, "Time (s)", "Power (W)", "Actuator Power P(t)")

energy_text = (
    f"Phase 2: {phase2.E:.2f} J ({phase2.duration:.2f} s)  |  "
    f"Phase 4: {phase4.E:.2f} J ({phase4.duration:.2f} s)  |  "
    f"Total: {phase2.E + phase4.E:.2f} J"
)
fig.text(
    0.5, 0.01, energy_text, ha="center", va="bottom", fontsize=9,
    bbox=dict(
        boxstyle="round,pad=0.4", fc="lightyellow", ec="gray", lw=0.8
    ),
)

out_combined = os.path.join("results", "sim_1d_combined.png")
fig.savefig(out_combined, dpi=150, bbox_inches="tight")
plt.close(fig)
print(f"Plot saved to {out_combined}")
