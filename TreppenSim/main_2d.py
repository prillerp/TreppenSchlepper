"""
TreppenSchlepper — 2-D (x-z) simulation entry point.

Runs the full step cycle (Phase 2 elevation + Phase 3 HC advance +
Phase 4 retraction) and saves three figures to results/:

  sim_2d_phase3.png    — Phase 3 HC kinematics and forces (4 panels)
  sim_2d_stability.png — CoM tracking and tipping moment (2 panels)
  sim_2d_cycle.png     — Full step cycle energy and duration breakdown

Usage:
    python main_2d.py
"""

import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.gridspec as gridspec  # noqa: E402
import matplotlib.patches as mpatches  # noqa: E402
import matplotlib.pyplot as plt        # noqa: E402
import numpy as np                     # noqa: E402

from sim.params import SimParams       # noqa: E402
from sim.sim_2d import run_step_cycle  # noqa: E402


# ── Parameters & run ─────────────────────────────────────────────────────────

params = SimParams()  # all defaults — see sim/params.py for values

cycle = run_step_cycle(params)
p2, p3, p4 = cycle.phase2, cycle.phase3, cycle.phase4

print()
print(p2.summary())
print()
print(p3.summary())
print()
print(p4.summary())
print()
print(cycle.summary())

os.makedirs("results", exist_ok=True)


# ── Shared helpers ────────────────────────────────────────────────────────────

def _fmt(ax, xlabel, ylabel, title, legend=True):
    ax.set_xlabel(xlabel, fontsize=9)
    ax.set_ylabel(ylabel, fontsize=9)
    ax.set_title(title, fontsize=10, fontweight="bold")
    if legend:
        handles, _ = ax.get_legend_handles_labels()
        if handles:
            ax.legend(fontsize=7.5)
    ax.grid(True, alpha=0.3)
    ax.tick_params(labelsize=8)


def _vline(ax, x, label, color="gray", ls="--"):
    ax.axvline(x, color=color, ls=ls, lw=1.0, label=label)


# ── Figure 1 — Phase 3 kinematics & forces (4 panels) ────────────────────────

C3 = "#2ca02c"

fig1 = plt.figure(figsize=(12, 9))
fig1.suptitle(
    "TreppenSchlepper — Phase 3 (HC Advance)\n"
    f"HC stroke = {params.hc.stroke * 100:.0f} cm  |  "
    f"v_max = {params.hc.v_max * 100:.0f} cm/s  |  "
    f"OS group = {p3.mass_os_group:.1f} kg",
    fontsize=12, fontweight="bold",
)

gs1 = gridspec.GridSpec(2, 2, figure=fig1, hspace=0.42, wspace=0.32)
ax_x = fig1.add_subplot(gs1[0, 0])
ax_v = fig1.add_subplot(gs1[0, 1])
ax_f = fig1.add_subplot(gs1[1, 0])
ax_p = fig1.add_subplot(gs1[1, 1])

ax_x.plot(p3.t, p3.x_hc * 100, color=C3, lw=2, label="HC extension")
ax_x.axhline(
    params.hc.stroke * 100, color="gray", ls=":", lw=1,
    label=f"target {params.hc.stroke * 100:.0f} cm",
)

ax_v.plot(p3.t, p3.xdot * 100, color=C3, lw=2)

ax_f.plot(p3.t, p3.F_hc, color=C3, lw=2)
i_pk = int(np.argmax(np.abs(p3.F_hc)))
ax_f.annotate(
    f"peak {p3.F_peak:.0f} N",
    xy=(p3.t[i_pk], p3.F_hc[i_pk]),
    xytext=(
        p3.t[i_pk] + p3.duration * 0.05,
        p3.F_hc[i_pk] * 1.05,
    ),
    fontsize=8, color=C3,
    arrowprops=dict(arrowstyle="->", color=C3, lw=0.8),
)

ax_p.plot(p3.t, p3.P, color=C3, lw=2)

wct = p3.wheel_contact_time
if wct is not None:
    for ax in (ax_x, ax_v, ax_f, ax_p):
        _vline(ax, wct, f"wheel @{wct:.2f}s", color="orange")

_fmt(ax_x, "Time (s)", "HC extension (cm)", "HC Extension x_hc(t)")
_fmt(ax_v, "Time (s)", "Velocity (cm/s)", "HC Velocity x'(t)")
_fmt(ax_f, "Time (s)", "Force (N)", "HC Force F(t)")
_fmt(ax_p, "Time (s)", "Power (W)", "HC Power P(t)")

summary1 = (
    f"Peak force: {p3.F_peak:.0f} N  |  "
    f"Peak power: {p3.P_peak:.1f} W  |  "
    f"Energy: {p3.E:.2f} J  |  "
    f"Duration: {p3.duration:.2f} s"
)
fig1.text(
    0.5, 0.01, summary1, ha="center", va="bottom", fontsize=9,
    bbox=dict(boxstyle="round,pad=0.4", fc="lightyellow", ec="gray", lw=0.8),
)

out1 = os.path.join("results", "sim_2d_phase3.png")
fig1.savefig(out1, dpi=150, bbox_inches="tight")
plt.close(fig1)
print(f"Plot saved -> {out1}")


# ── Figure 2 — Stability analysis (2 panels) ──────────────────────────────────

geo = params.geometry
tread_cm = params.stair.tread_depth * 100

fig2, (ax_com, ax_tip) = plt.subplots(1, 2, figsize=(12, 5))
fig2.suptitle(
    "TreppenSchlepper — Phase 3 Stability Analysis\n"
    f"L_os = {geo.L_os * 100:.0f} cm  |  L_is = {geo.L_is * 100:.0f} cm  |  "
    f"wheel r = {geo.wheel_radius * 100:.0f} cm  "
    f"(front offset {geo.wheel_offset_front * 100:.0f} cm)",
    fontsize=12, fontweight="bold",
)

# Panel A — x positions
ax_com.plot(
    p3.t, p3.x_os_front * 100, color="#1f77b4", lw=2, label="OS front",
)
ax_com.plot(
    p3.t, p3.x_os_back * 100, color="#1f77b4", lw=1.5, ls="--",
    label="OS back",
)
ax_com.plot(
    p3.t, p3.x_front_wheel * 100, color="darkorange", lw=1.5, ls="-.",
    label="front wheel axis",
)
ax_com.plot(
    p3.t, p3.x_rear_wheel * 100, color="peru", lw=1.5, ls=":",
    label="rear wheel axis",
)
ax_com.plot(
    p3.t, p3.x_com_os * 100, color="#ff7f0e", lw=2, label="OS+payload CoM",
)
ax_com.plot(
    p3.t, p3.x_com_total * 100, color="#d62728", lw=2, label="Combined CoM",
)
ax_com.axhline(0, color="k", lw=1.2, label="Step edge (x=0)")
ax_com.axhline(
    tread_cm, color="gray", ls=":", lw=1, label=f"Tread end ({tread_cm:.0f} cm)",
)
ax_com.fill_between(
    p3.t, 0, tread_cm,
    color="lightblue", alpha=0.15, label="Upper tread zone",
)
if wct is not None:
    _vline(ax_com, wct, f"wheel @{wct:.2f}s", color="orange")
_fmt(ax_com, "Time (s)", "x position (cm)", "Positions during Phase 3")

# Panel B — stability margin and tipping moment
ax_tip2 = ax_tip.twinx()
ax_tip.plot(
    p3.t, p3.stability_margin * 100, color="#2ca02c", lw=2,
    label="Stability margin (cm)",
)
ax_tip.axhline(0, color="red", lw=1, ls="--")
ax_tip.fill_between(
    p3.t, p3.stability_margin * 100, 0,
    where=p3.stability_margin >= 0, alpha=0.15, color="#2ca02c",
    label="Stable region",
)
ax_tip.fill_between(
    p3.t, p3.stability_margin * 100, 0,
    where=p3.stability_margin < 0, alpha=0.25, color="red",
    label="Tipping risk",
)
ax_tip2.plot(
    p3.t, p3.M_tip, color="#9467bd", lw=1.5, ls="-.",
    label="Tipping moment (N*m)",
)
ax_tip2.set_ylabel("Tipping moment (N*m)", fontsize=9, color="#9467bd")
ax_tip2.tick_params(labelsize=8, colors="#9467bd")
if wct is not None:
    _vline(ax_tip, wct, f"wheel @{wct:.2f}s", color="orange")
_fmt(
    ax_tip, "Time (s)", "Stability margin (cm)",
    "Stability Margin & Tipping Moment",
)
lines_a, labels_a = ax_tip.get_legend_handles_labels()
lines_b, labels_b = ax_tip2.get_legend_handles_labels()
ax_tip.legend(lines_a + lines_b, labels_a + labels_b, fontsize=7.5)

plt.tight_layout(rect=[0, 0, 1, 0.93])
out2 = os.path.join("results", "sim_2d_stability.png")
fig2.savefig(out2, dpi=150, bbox_inches="tight")
plt.close(fig2)
print(f"Plot saved -> {out2}")


# ── Figure 3 — Full cycle energy & duration breakdown ─────────────────────────

fig3, (ax_e, ax_d) = plt.subplots(1, 2, figsize=(10, 5))
fig3.suptitle(
    "TreppenSchlepper — Full Step Cycle Summary\n"
    f"18/27 stair  |  payload {params.mass.m_payload:.0f} kg  |  "
    f"total {cycle.total_energy:.1f} J  in  {cycle.total_duration:.1f} s",
    fontsize=12, fontweight="bold",
)

phases = ["Phase 2\nElevation", "Phase 3\nHC Advance", "Phase 4\nRetraction"]
energies = [p2.E, p3.E, p4.E]
durations = [p2.duration, p3.duration, p4.duration]
colors = ["#1f77b4", "#2ca02c", "#d62728"]

bars_e = ax_e.bar(
    phases, energies, color=colors, edgecolor="k", lw=0.8, width=0.5,
)
for bar, val in zip(bars_e, energies):
    ax_e.text(
        bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.3,
        f"{val:.2f} J", ha="center", va="bottom", fontsize=9, fontweight="bold",
    )
ax_e.set_ylabel("Energy (J)", fontsize=10)
ax_e.set_title("Energy per Phase", fontsize=11, fontweight="bold")
ax_e.set_ylim(0, max(energies) * 1.25)
ax_e.grid(axis="y", alpha=0.3)
ax_e.tick_params(labelsize=9)
ax_e.legend(
    handles=[mpatches.Patch(
        color="lightyellow", ec="gray",
        label=f"Total: {cycle.total_energy:.2f} J",
    )],
    fontsize=9,
)

bars_d = ax_d.bar(
    phases, durations, color=colors, edgecolor="k", lw=0.8, width=0.5,
)
for bar, val in zip(bars_d, durations):
    ax_d.text(
        bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.05,
        f"{val:.2f} s", ha="center", va="bottom", fontsize=9, fontweight="bold",
    )
ax_d.set_ylabel("Duration (s)", fontsize=10)
ax_d.set_title("Duration per Phase", fontsize=11, fontweight="bold")
ax_d.set_ylim(0, max(durations) * 1.25)
ax_d.grid(axis="y", alpha=0.3)
ax_d.tick_params(labelsize=9)
ax_d.legend(
    handles=[mpatches.Patch(
        color="lightyellow", ec="gray",
        label=f"Total: {cycle.total_duration:.2f} s",
    )],
    fontsize=9,
)

plt.tight_layout(rect=[0, 0, 1, 0.90])
out3 = os.path.join("results", "sim_2d_cycle.png")
fig3.savefig(out3, dpi=150, bbox_inches="tight")
plt.close(fig3)
print(f"Plot saved -> {out3}")
