"""
TreppenSchlepper — Energy and duration sweep over payload mass.

Fixed stair: 18/27 (rise = 18 cm, tread = 27 cm).
Payload range: 0 … 100 kg in 10 kg steps.

Results are plotted vs payload mass and saved to results/sweep_payload.png.

Usage:
    uv run python sweep_payload.py
"""

import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt         # noqa: E402
import matplotlib.patches as mpatches  # noqa: E402
import numpy as np                      # noqa: E402

from sim.params import SimParams        # noqa: E402
from sim.sim_2d import run_step_cycle   # noqa: E402

os.makedirs("results", exist_ok=True)

# ── Sweep configuration ───────────────────────────────────────────────────────

PAYLOAD_KG = sorted(set(list(range(0, 35, 5)) + [3]))  # 0,3,5,10,…30 kg
DESIGN_POINT = 3.0                     # kg — PoC payload, highlighted in plots
EC_RATED_N   = 500.0                   # candidate EC actuator rated force
EC_MAX_PAYLOAD_KG = (EC_RATED_N - 141) / 9.9  # ~36 kg at 500 N

# ── Run sweep ─────────────────────────────────────────────────────────────────

results = []

for pl in PAYLOAD_KG:
    p = SimParams()
    p.mass.m_payload = float(pl)

    cycle = run_step_cycle(p)
    ph2, ph3 = cycle.phase2, cycle.phase3
    ph4a, ph4b = cycle.phase4a, cycle.phase4b

    results.append(dict(
        payload    = pl,
        e2         = ph2.E,
        e3         = ph3.E,
        e4a        = ph4a.E,
        e4b        = ph4b.E,
        e_total    = cycle.total_energy,
        d2         = ph2.duration,
        d3         = ph3.duration,
        d4a        = ph4a.duration,
        d4b        = ph4b.duration,
        d_total    = cycle.total_duration,
        f_peak_ec2 = ph2.F_peak,
        f_peak_ec4 = ph4a.F_peak,
        f_peak_hc  = ph3.F_peak,
        f_peak_hc4 = ph4b.F_peak,
        stab_min   = ph3.min_stability_margin * 100,  # cm
        m_phase2   = ph2.mass,
        m_phase3   = ph3.mass_os_group,
    ))

    print(
        f"payload={pl:3d} kg  E={cycle.total_energy:6.1f} J  "
        f"t={cycle.total_duration:.2f} s  "
        f"EC_peak={ph2.F_peak:.0f} N  stab={ph3.min_stability_margin*100:.1f} cm"
    )

# Arrays
pl_arr   = np.array([r["payload"]    for r in results])
e2_arr   = np.array([r["e2"]         for r in results])
e3_arr   = np.array([r["e3"]         for r in results])
e4a_arr  = np.array([r["e4a"]        for r in results])
e4b_arr  = np.array([r["e4b"]        for r in results])
etot_arr = np.array([r["e_total"]    for r in results])
d2_arr   = np.array([r["d2"]         for r in results])
d3_arr   = np.array([r["d3"]         for r in results])
d4a_arr  = np.array([r["d4a"]        for r in results])
d4b_arr  = np.array([r["d4b"]        for r in results])
dtot_arr = np.array([r["d_total"]    for r in results])
fec2_arr = np.array([r["f_peak_ec2"] for r in results])
fec4_arr = np.array([r["f_peak_ec4"] for r in results])
fhc_arr  = np.array([r["f_peak_hc"]  for r in results])
stab_arr = np.array([r["stab_min"]   for r in results])

# ── Plot ──────────────────────────────────────────────────────────────────────

C2   = "#1f77b4"
C3   = "#2ca02c"
C4   = "#d62728"
CTOT = "#333333"

fig, axes = plt.subplots(2, 3, figsize=(16, 10))
fig.suptitle(
    "TreppenSchlepper — Parameter Sweep over Payload Mass\n"
    "Fixed stair 18/27  |  rise = 18 cm  |  Config B  |  PoC design 3 kg",
    fontsize=13, fontweight="bold",
)

DP_KW  = dict(color="goldenrod", lw=1.5, ls="--", alpha=0.8)   # design-point line
EC_KW  = dict(color="gray",      lw=1.2, ls=":",  alpha=0.8)   # EC rated limit


def _base(ax, ylabel, title):
    ax.set_xlabel("Payload mass (kg)", fontsize=9)
    ax.set_ylabel(ylabel, fontsize=9)
    ax.set_title(title, fontsize=10, fontweight="bold")
    ax.set_xticks(PAYLOAD_KG)
    ax.set_xticklabels([str(p) for p in PAYLOAD_KG], fontsize=8)
    ax.grid(True, alpha=0.3)
    ax.tick_params(labelsize=8)
    ax.axvline(DESIGN_POINT, **DP_KW, label=f"Design point ({DESIGN_POINT:.0f} kg)")


# ── Panel 1 — Energy per phase ────────────────────────────────────────────────

ax = axes[0, 0]
ax.plot(pl_arr, e2_arr,   "o-", color=C2,   lw=2, label="Phase 2 (EC lift)")
ax.plot(pl_arr, e3_arr,   "s-", color=C3,   lw=2, label="Phase 3 (HC advance)")
ax.plot(pl_arr, e4a_arr,  "^-", color=C4,   lw=2, label="Phase 4a (EC retract)")
ax.plot(pl_arr, e4b_arr,  "v-", color="#ff7f0e", lw=2, label="Phase 4b (HC retract)")
ax.plot(pl_arr, etot_arr, "D-", color=CTOT, lw=2.5, label="Total")
_base(ax, "Energy (J)", "Energy per Phase vs Payload")
ax.legend(fontsize=7.5)

# ── Panel 2 — Duration per phase ─────────────────────────────────────────────

ax = axes[0, 1]
ax.plot(pl_arr, d2_arr,   "o-", color=C2,   lw=2, label="Phase 2 (EC lift)")
ax.plot(pl_arr, d3_arr,   "s-", color=C3,   lw=2, label="Phase 3 (HC advance)")
ax.plot(pl_arr, d4a_arr,  "^-", color=C4,   lw=2, label="Phase 4a (EC retract)")
ax.plot(pl_arr, d4b_arr,  "v-", color="#ff7f0e", lw=2, label="Phase 4b (HC retract)")
ax.plot(pl_arr, dtot_arr, "D-", color=CTOT, lw=2.5, label="Total")
_base(ax, "Duration (s)", "Duration per Phase vs Payload")
ax.legend(fontsize=7.5)

# ── Panel 3 — Stacked energy bar ─────────────────────────────────────────────

C4B = "#ff7f0e"
ax = axes[0, 2]
w = 3.5
ax.bar(pl_arr, e2_arr,              width=w, color=C2, label="Ph2", edgecolor="k", lw=0.5)
ax.bar(pl_arr, e3_arr, bottom=e2_arr,           width=w, color=C3, label="Ph3", edgecolor="k", lw=0.5)
ax.bar(pl_arr, e4a_arr, bottom=e2_arr + e3_arr, width=w, color=C4, label="Ph4a", edgecolor="k", lw=0.5)
ax.bar(pl_arr, e4b_arr, bottom=e2_arr + e3_arr + e4a_arr, width=w, color=C4B, label="Ph4b", edgecolor="k", lw=0.5)
for x, e in zip(pl_arr, etot_arr):
    ax.text(x, e + 0.5, f"{e:.0f}", ha="center", va="bottom", fontsize=7)
_base(ax, "Energy (J)", "Stacked Energy per Step")
ax.legend(fontsize=7.5)

# ── Panel 4 — Peak actuator forces ───────────────────────────────────────────

ax = axes[1, 0]
ax.plot(pl_arr, fec2_arr, "o-", color=C2, lw=2, label="EC peak — Phase 2")
ax.plot(pl_arr, fec4_arr, "^-", color=C4, lw=2, label="EC peak — Phase 4a")
ax.plot(pl_arr, fhc_arr,  "s-", color=C3, lw=2, label="HC peak — Phase 3")
ax.axhline(EC_RATED_N, **EC_KW,
           label=f"EC actuator rated ({EC_RATED_N:.0f} N)")
if EC_MAX_PAYLOAD_KG <= pl_arr[-1]:
    ax.axvline(EC_MAX_PAYLOAD_KG, color="red", lw=1.5, ls="-.",
               label=f"Max safe payload ({EC_MAX_PAYLOAD_KG:.0f} kg)")
    ax.annotate(
        f"Max payload\n~{EC_MAX_PAYLOAD_KG:.0f} kg",
        xy=(EC_MAX_PAYLOAD_KG, EC_RATED_N),
        xytext=(EC_MAX_PAYLOAD_KG - 8, EC_RATED_N + 40),
        fontsize=8, color="red",
        arrowprops=dict(arrowstyle="->", color="red", lw=1.2),
    )
_base(ax, "Peak force (N)", "Peak Actuator Forces vs Payload")
ax.legend(fontsize=7.5)

# ── Panel 5 — Phase 3 stability margin ───────────────────────────────────────

ax = axes[1, 1]
ax.plot(pl_arr, stab_arr, "o-", color="#9467bd", lw=2, label="Min stability margin")
ax.axhline(0, color="red", lw=1.5, ls="--", label="Tip-over threshold")
ax.fill_between(pl_arr, stab_arr, 0,
                where=stab_arr >= 0, alpha=0.15, color="#9467bd", label="Stable")
ax.fill_between(pl_arr, stab_arr, 0,
                where=stab_arr <  0, alpha=0.25, color="red",     label="Tipping")
_base(ax, "Min stability margin (cm)", "Phase 3 Stability vs Payload")
ax.legend(fontsize=7.5)

# ── Panel 6 — Summary table ───────────────────────────────────────────────────

ax = axes[1, 2]
ax.axis("off")

col_labels = ["Payload\n(kg)", "E_total\n(J)", "t_total\n(s)",
              "EC_peak\n(N)", "HC_peak\n(N)", "Stab.\n(cm)"]
table_data = [
    [
        f"{r['payload']}",
        f"{r['e_total']:.1f}",
        f"{r['d_total']:.2f}",
        f"{r['f_peak_ec2']:.0f}",
        f"{r['f_peak_hc']:.0f}",
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
tbl.scale(1.1, 1.4)

# highlight design point row
for row_idx, r in enumerate(results):
    bg = "#fff8cc" if r["payload"] == DESIGN_POINT else "white"
    for col_idx in range(len(col_labels)):
        tbl[(row_idx + 1, col_idx)].set_facecolor(bg)
    # highlight EC over-limit rows
    if r["f_peak_ec2"] > EC_RATED_N:
        tbl[(row_idx + 1, 3)].set_facecolor("#ffe0e0")

ax.set_title("Simulation Results Table\n(yellow = design point)",
             fontsize=10, fontweight="bold")

# ── Save ──────────────────────────────────────────────────────────────────────

plt.tight_layout(rect=[0, 0, 1, 0.94])
out = os.path.join("results", "sweep_payload.png")
fig.savefig(out, dpi=150, bbox_inches="tight")
plt.close(fig)
print(f"\nSweep plot saved -> {out}")
