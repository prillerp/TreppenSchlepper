"""
TreppenSchlepper — Energy and duration sweep over stair rise heights.

Stair formula (human step length = 63 cm):  tread = 63 - 2 × rise
Rise range: 14 cm … 22 cm  (typical European range)

For each rise height the full 2-D step cycle (Phase 2 + 3 + 4) is run.
Results are plotted vs rise height and saved to results/sweep_rise.png.

Note: OS length = 25 cm must fit on the tread (tread ≥ 25 cm → rise ≤ 19 cm).
Steps steeper than that are flagged but still simulated for completeness.

Usage:
    uv run python sweep_rise.py
"""

import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt      # noqa: E402
import matplotlib.patches as mpatches  # noqa: E402
import numpy as np                   # noqa: E402

from sim.params import (             # noqa: E402
    SimParams, StairParams, ActuatorParams, HCActuatorParams,
)
from sim.sim_2d import run_step_cycle  # noqa: E402

os.makedirs("results", exist_ok=True)

# ── Sweep configuration ───────────────────────────────────────────────────────

RISE_CM = list(range(14, 23))          # 14, 15, …, 22  cm
L_OS_CM = 25.0                         # OS length constraint
OS_MAX_RISE_CM = (63 - L_OS_CM) / 2   # = 19 cm: tread = L_OS at this point

# ── Run sweep ─────────────────────────────────────────────────────────────────

results = []

for rise_cm in RISE_CM:
    rise   = rise_cm / 100.0
    tread  = (63.0 - 2.0 * rise_cm) / 100.0   # stair formula in metres
    tread  = max(tread, L_OS_CM / 100.0)       # clamp to at least OS length

    p = SimParams()
    p.stair.rise_height = rise
    p.stair.tread_depth = tread
    # HC stroke stays 25 cm (= OS length) regardless of rise
    p.hc.stroke = L_OS_CM / 100.0

    cycle = run_step_cycle(p)
    ph2, ph3, ph4 = cycle.phase2, cycle.phase3, cycle.phase4

    results.append(dict(
        rise_cm   = rise_cm,
        tread_cm  = tread * 100,
        e2        = ph2.E,
        e3        = ph3.E,
        e4        = ph4.E,
        e_total   = cycle.total_energy,
        d2        = ph2.duration,
        d3        = ph3.duration,
        d4        = ph4.duration,
        d_total   = cycle.total_duration,
        f_peak_ec = ph2.F_peak,
        f_peak_ec4= ph4.F_peak,
        f_peak_hc = ph3.F_peak,
        stab_min  = ph3.min_stability_margin * 100,   # cm
        wct       = ph3.wheel_contact_time,
    ))

    print(
        f"rise={rise_cm:2d} cm  tread={tread*100:.0f} cm  "
        f"E={cycle.total_energy:6.1f} J  t={cycle.total_duration:.2f} s  "
        f"EC_peak={ph2.F_peak:.0f} N  stab={ph3.min_stability_margin*100:.1f} cm"
    )

# Unpack to arrays for plotting
rise_arr    = np.array([r["rise_cm"]   for r in results])
tread_arr   = np.array([r["tread_cm"]  for r in results])
e2_arr      = np.array([r["e2"]        for r in results])
e3_arr      = np.array([r["e3"]        for r in results])
e4_arr      = np.array([r["e4"]        for r in results])
etot_arr    = np.array([r["e_total"]   for r in results])
d2_arr      = np.array([r["d2"]        for r in results])
d3_arr      = np.array([r["d3"]        for r in results])
d4_arr      = np.array([r["d4"]        for r in results])
dtot_arr    = np.array([r["d_total"]   for r in results])
fec_arr     = np.array([r["f_peak_ec"] for r in results])
fec4_arr    = np.array([r["f_peak_ec4"]for r in results])
fhc_arr     = np.array([r["f_peak_hc"] for r in results])
stab_arr    = np.array([r["stab_min"]  for r in results])

# ── Plot ──────────────────────────────────────────────────────────────────────

C2 = "#1f77b4"   # Phase 2 — blue
C3 = "#2ca02c"   # Phase 3 — green
C4 = "#d62728"   # Phase 4 — red
CTOT = "#333333" # total — dark

fig, axes = plt.subplots(2, 3, figsize=(16, 10))
fig.suptitle(
    "TreppenSchlepper — Parameter Sweep over Stair Rise Heights\n"
    "Stair formula: tread = 63 − 2×rise  |  OS length = 25 cm  |  "
    "Payload = 20 kg  |  Config B",
    fontsize=13, fontweight="bold",
)

SHADE_KW  = dict(color="#ffcccc", alpha=0.35, zorder=0)    # constraint violation zone
VLINE_KW  = dict(color="red", lw=1.2, ls="--", alpha=0.7)


def _base(ax, ylabel, title):
    ax.set_xlabel("Rise height (cm)", fontsize=9)
    ax.set_ylabel(ylabel, fontsize=9)
    ax.set_title(title, fontsize=10, fontweight="bold")
    ax.set_xticks(RISE_CM)
    ax.set_xticklabels([str(r) for r in RISE_CM], fontsize=8)
    ax.grid(True, alpha=0.3)
    ax.tick_params(labelsize=8)
    # shade region where tread < OS length (tight fit)
    ax.axvspan(OS_MAX_RISE_CM, max(RISE_CM) + 0.5, **SHADE_KW)
    ax.axvline(OS_MAX_RISE_CM, **VLINE_KW)


def _legend_constraint(ax):
    ax.legend(
        handles=ax.get_legend_handles_labels()[0] + [
            mpatches.Patch(color="#ffcccc", alpha=0.6,
                           label=f"tread < OS ({L_OS_CM:.0f} cm)"),
        ],
        fontsize=7.5,
    )


# ── Panel 1 — Energy per phase (lines) ───────────────────────────────────────

ax = axes[0, 0]
ax.plot(rise_arr, e2_arr, "o-", color=C2,   lw=2, label="Phase 2 (EC lift)")
ax.plot(rise_arr, e3_arr, "s-", color=C3,   lw=2, label="Phase 3 (HC advance)")
ax.plot(rise_arr, e4_arr, "^-", color=C4,   lw=2, label="Phase 4 (EC retract)")
ax.plot(rise_arr, etot_arr, "D-", color=CTOT, lw=2.5, label="Total")
_base(ax, "Energy (J)", "Energy per Phase vs Rise Height")
_legend_constraint(ax)

# ── Panel 2 — Duration per phase (lines) ─────────────────────────────────────

ax = axes[0, 1]
ax.plot(rise_arr, d2_arr, "o-", color=C2,   lw=2, label="Phase 2 (EC lift)")
ax.plot(rise_arr, d3_arr, "s-", color=C3,   lw=2, label="Phase 3 (HC advance)")
ax.plot(rise_arr, d4_arr, "^-", color=C4,   lw=2, label="Phase 4 (EC retract)")
ax.plot(rise_arr, dtot_arr, "D-", color=CTOT, lw=2.5, label="Total")
_base(ax, "Duration (s)", "Duration per Phase vs Rise Height")
_legend_constraint(ax)

# ── Panel 3 — Stacked energy bar chart ───────────────────────────────────────

ax = axes[0, 2]
w = 0.6
ax.bar(rise_arr, e2_arr,              width=w, color=C2, label="Phase 2 (EC lift)",     edgecolor="k", lw=0.5)
ax.bar(rise_arr, e3_arr, bottom=e2_arr,          width=w, color=C3, label="Phase 3 (HC)",         edgecolor="k", lw=0.5)
ax.bar(rise_arr, e4_arr, bottom=e2_arr + e3_arr, width=w, color=C4, label="Phase 4 (EC retract)", edgecolor="k", lw=0.5)
for x, e in zip(rise_arr, etot_arr):
    ax.text(x, e + 0.5, f"{e:.0f}", ha="center", va="bottom", fontsize=7)
_base(ax, "Energy (J)", "Stacked Energy per Step")
_legend_constraint(ax)

# ── Panel 4 — Peak actuator forces ───────────────────────────────────────────

ax = axes[1, 0]
ax.plot(rise_arr, fec_arr,  "o-", color=C2, lw=2, label="EC peak force — Phase 2")
ax.plot(rise_arr, fec4_arr, "^-", color=C4, lw=2, label="EC peak force — Phase 4")
ax.plot(rise_arr, fhc_arr,  "s-", color=C3, lw=2, label="HC peak force — Phase 3")
ax.axhline(1000, color="gray", ls=":", lw=1.2, label="TiMOTION TA2 rated (1000 N)")
ax.axhline(100, color="#888888", ls="-.", lw=1, label="HC candidate limit (100 N)")
_base(ax, "Peak force (N)", "Peak Actuator Forces vs Rise Height")
_legend_constraint(ax)

# ── Panel 5 — Phase 3 stability margin ───────────────────────────────────────

ax = axes[1, 1]
ax.plot(rise_arr, stab_arr, "o-", color="#9467bd", lw=2, label="Min stability margin")
ax.axhline(0, color="red", lw=1.5, ls="--", label="Tip-over threshold")
ax.fill_between(rise_arr, stab_arr, 0,
                where=stab_arr >= 0, alpha=0.15, color="#9467bd", label="Stable")
ax.fill_between(rise_arr, stab_arr, 0,
                where=stab_arr <  0, alpha=0.25, color="red",     label="Tipping")
_base(ax, "Min stability margin (cm)", "Phase 3 Stability vs Rise Height")
_legend_constraint(ax)

# ── Panel 6 — Summary table ───────────────────────────────────────────────────

ax = axes[1, 2]
ax.axis("off")

col_labels = ["Rise\n(cm)", "Tread\n(cm)", "E_total\n(J)", "t_total\n(s)",
              "EC_peak\n(N)", "Stab.\n(cm)"]
table_data = [
    [
        f"{r['rise_cm']}",
        f"{r['tread_cm']:.0f}",
        f"{r['e_total']:.1f}",
        f"{r['d_total']:.2f}",
        f"{r['f_peak_ec']:.0f}",
        f"{r['stab_min']:.1f}",
    ]
    for r in results
]

tbl = ax.table(
    cellText=table_data,
    colLabels=col_labels,
    loc="center",
    cellLoc="center",
)
tbl.auto_set_font_size(False)
tbl.set_fontsize(8)
tbl.scale(1.15, 1.45)

# highlight rows where tread < OS (tight / overstepped)
for row_idx, r in enumerate(results):
    bg = "#ffe0e0" if r["tread_cm"] < L_OS_CM else "white"
    for col_idx in range(len(col_labels)):
        tbl[(row_idx + 1, col_idx)].set_facecolor(bg)

ax.set_title("Simulation Results Table\n(red = tread < OS length)",
             fontsize=10, fontweight="bold")

# ── Save ──────────────────────────────────────────────────────────────────────

plt.tight_layout(rect=[0, 0, 1, 0.94])
out = os.path.join("results", "sweep_rise.png")
fig.savefig(out, dpi=150, bbox_inches="tight")
plt.close(fig)
print(f"\nSweep plot saved -> {out}")
