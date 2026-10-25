"""
TreppenSchlepper — Config A vs Config B mass distribution comparison.

Config A (baseline): electronics/battery/motors in OuterShell
  OS = 15 kg, FP = 2 kg

Config B (heavy FP): electronics/battery/motors moved to FootPlate
  OS = 9 kg, FP = 8 kg  (6 kg shifted from OS to FP)

Question: which configuration spends less energy per full step cycle?

Phase 2 (EC lifts OS group up): lighter OS  → less energy in Config B
Phase 3 (HC pushes OS forward): lighter OS  → less HC force in Config B
Phase 4 (EC lifts FP group up): heavier FP → more energy in Config B

Usage:
    python compare_configs.py
"""

import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt    # noqa: E402
import numpy as np                 # noqa: E402

from sim.params import MassParams, SimParams   # noqa: E402
from sim.sim_2d import run_step_cycle          # noqa: E402

os.makedirs("results", exist_ok=True)

# ── Config A — electronics in OS (baseline) ───────────────────────────────────

params_A = SimParams(
    mass=MassParams(
        m_outer_shell=15.0,  # OS carries structure + electronics + motors
        m_payload=20.0,
        m_inner_shell=4.0,
        m_foot_plate=2.0,    # FP is bare plate
        m_elevator_cyl=3.0,
        m_hc=1.5,
    )
)

# ── Config B — electronics in FP (6 kg shifted) ───────────────────────────────

params_B = SimParams(
    mass=MassParams(
        m_outer_shell=9.0,   # OS: structure only, electronics moved out
        m_payload=20.0,
        m_inner_shell=4.0,
        m_foot_plate=8.0,    # FP: carries battery, controller, wheel motors
        m_elevator_cyl=3.0,
        m_hc=1.5,
    )
)

# ── Run both ──────────────────────────────────────────────────────────────────

cycle_A = run_step_cycle(params_A)
cycle_B = run_step_cycle(params_B)

pA2, pA3, pA4 = cycle_A.phase2, cycle_A.phase3, cycle_A.phase4
pB2, pB3, pB4 = cycle_B.phase2, cycle_B.phase3, cycle_B.phase4


# ── Print comparison ──────────────────────────────────────────────────────────

def _row(label, vA, vB, unit):
    diff = vB - vA
    sign = "+" if diff >= 0 else ""
    print(f"  {label:<32} {vA:8.2f}  {vB:8.2f}  {sign}{diff:+.2f} {unit}")


print()
print("=" * 70)
print("  TreppenSchlepper — Config A vs Config B")
print("  A: electronics in OS (OS=15 kg, FP=2 kg)")
print("  B: electronics in FP (OS= 9 kg, FP=8 kg)")
print("=" * 70)
print(f"  {'Metric':<32} {'Config A':>8}  {'Config B':>8}  {'B-A':>8}")
print("  " + "-" * 60)

print("  --- Moving masses ---")
_row("Ph2 OS-group mass (kg)", pA2.mass, pB2.mass, "kg")
_row("Ph3 OS-group mass (kg)", pA3.mass_os_group, pB3.mass_os_group, "kg")
_row("Ph4 FP-group mass (kg)", pA4.mass, pB4.mass, "kg")

print("  --- Phase 2 (EC elevation) ---")
_row("Ph2 peak force (N)", pA2.F_peak, pB2.F_peak, "N")
_row("Ph2 peak power (W)", pA2.P_peak, pB2.P_peak, "W")
_row("Ph2 energy (J)", pA2.E, pB2.E, "J")
_row("Ph2 duration (s)", pA2.duration, pB2.duration, "s")

print("  --- Phase 3 (HC advance) ---")
_row("Ph3 peak HC force (N)", pA3.F_peak, pB3.F_peak, "N")
_row("Ph3 energy (J)", pA3.E, pB3.E, "J")
_row("Ph3 min stability (cm)",
     pA3.min_stability_margin * 100,
     pB3.min_stability_margin * 100, "cm")

print("  --- Phase 4 (EC retraction) ---")
_row("Ph4 peak force (N)", pA4.F_peak, pB4.F_peak, "N")
_row("Ph4 peak power (W)", pA4.P_peak, pB4.P_peak, "W")
_row("Ph4 energy (J)", pA4.E, pB4.E, "J")

print("  --- Full cycle ---")
_row("Total energy (J)", cycle_A.total_energy, cycle_B.total_energy, "J")
_row("Total duration (s)", cycle_A.total_duration, cycle_B.total_duration, "s")

print("  " + "-" * 60)
winner = "A (OS-heavy)" if cycle_A.total_energy < cycle_B.total_energy \
    else "B (FP-heavy)"
diff_J = abs(cycle_B.total_energy - cycle_A.total_energy)
diff_pct = diff_J / cycle_A.total_energy * 100
print(f"  Lower energy: Config {winner}  |  diff = {diff_J:.1f} J "
      f"({diff_pct:.1f}%)")
print("=" * 70)
print()


# ── Plot ──────────────────────────────────────────────────────────────────────

phases = ["Ph2\nElevation", "Ph3\nHC Advance", "Ph4\nRetraction", "TOTAL"]
eA = [pA2.E, pA3.E, pA4.E, cycle_A.total_energy]
eB = [pB2.E, pB3.E, pB4.E, cycle_B.total_energy]

x = np.arange(len(phases))
width = 0.35

fig, (ax_e, ax_f) = plt.subplots(1, 2, figsize=(12, 5))
fig.suptitle(
    "TreppenSchlepper — Config A (OS-heavy) vs Config B (FP-heavy)\n"
    "A: OS=15 kg, FP=2 kg   |   B: OS=9 kg, FP=8 kg   (6 kg shifted)",
    fontsize=12, fontweight="bold",
)

bars_A = ax_e.bar(x - width / 2, eA, width, label="Config A (OS-heavy)",
                  color="#1f77b4", edgecolor="k", lw=0.8)
bars_B = ax_e.bar(x + width / 2, eB, width, label="Config B (FP-heavy)",
                  color="#d62728", edgecolor="k", lw=0.8)
for bar, val in zip(bars_A, eA):
    ax_e.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
              f"{val:.1f}", ha="center", va="bottom", fontsize=8)
for bar, val in zip(bars_B, eB):
    ax_e.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
              f"{val:.1f}", ha="center", va="bottom", fontsize=8)
ax_e.set_xticks(x)
ax_e.set_xticklabels(phases, fontsize=9)
ax_e.set_ylabel("Energy (J)", fontsize=10)
ax_e.set_title("Energy per Phase", fontsize=11, fontweight="bold")
ax_e.legend(fontsize=9)
ax_e.grid(axis="y", alpha=0.3)
ax_e.tick_params(labelsize=8)

# Force comparison
forces_lbl = ["Ph2 peak\nforce (N)", "Ph3 peak\nforce (N)", "Ph4 peak\nforce (N)"]
fA = [pA2.F_peak, pA3.F_peak, pA4.F_peak]
fB = [pB2.F_peak, pB3.F_peak, pB4.F_peak]
xf = np.arange(len(forces_lbl))

bfA = ax_f.bar(xf - width / 2, fA, width, label="Config A",
               color="#1f77b4", edgecolor="k", lw=0.8)
bfB = ax_f.bar(xf + width / 2, fB, width, label="Config B",
               color="#d62728", edgecolor="k", lw=0.8)
for bar, val in zip(bfA, fA):
    ax_f.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
              f"{val:.0f}", ha="center", va="bottom", fontsize=8)
for bar, val in zip(bfB, fB):
    ax_f.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
              f"{val:.0f}", ha="center", va="bottom", fontsize=8)
ax_f.set_xticks(xf)
ax_f.set_xticklabels(forces_lbl, fontsize=9)
ax_f.set_ylabel("Force (N)", fontsize=10)
ax_f.set_title("Peak Actuator Force per Phase", fontsize=11, fontweight="bold")
ax_f.legend(fontsize=9)
ax_f.grid(axis="y", alpha=0.3)
ax_f.tick_params(labelsize=8)

plt.tight_layout(rect=[0, 0, 1, 0.90])
out = os.path.join("results", "compare_configs.png")
fig.savefig(out, dpi=150, bbox_inches="tight")
plt.close(fig)
print(f"Plot saved -> {out}")
