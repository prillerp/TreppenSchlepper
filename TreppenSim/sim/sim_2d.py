"""
2-D (x-z plane) simulation of TreppenSchlepper - Phase 3.

Phase 3: HorizontalCylinder extends, pushing OuterShell forward over the
upper step while SlidingInnerShell + FootPlate remain anchored on the lower
tread.

Coordinate system
-----------------
  x=0  : step edge (front face of IS, front of lower tread)
  z=0  : lower tread surface
  +x   : toward upper tread
  +z   : upward

State at start of Phase 3
--------------------------
  IS front at x=0, IS back at x=-L_is   (fixed throughout Phase 3)
  OS front at x=x_os_front_init          (default 0, flush with step edge)
  OS bottom at z=rise_height             (after Phase 2 elevation)
  HC extension = 0

Tipping analysis
----------------
The EC (vertical actuator) is locked at full extension during Phase 3 and
acts as a rigid strut between IS and OS in the z-direction.  The HC
provides only horizontal force.  We track:

  x_com_total   - x-position of the entire device CoM
  M_tip         - gravitational tipping moment of OS group about the
                  step edge (x=0), positive = nose-heavy (clockwise)
  stability_margin - distance from combined CoM to the active support edge:
                     before wheel contact: support edge = IS front = 0
                     after  wheel contact: support edge = x of front wheel

All SI units (m, kg, s, N, W, J).
"""

from dataclasses import dataclass
from typing import Optional

import numpy as np

from .params import SimParams
from .motion import trapezoid_profile
from .sim_1d import PhaseResult

G = 9.81  # m/s²


# ── Phase 3 result ───────────────────────────────────────────────────────────

@dataclass
class Phase3Result:
    """Full output of the Phase 3 (HC advance) simulation."""
    label: str
    mass_os_group: float  # kg - moving mass (OS + payload + upper EC)
    mass_is_group: float  # kg - anchored mass (IS + FP + lower EC)
    displacement: float   # m  - HC stroke

    t: np.ndarray      # s
    x_hc: np.ndarray   # m    HC extension
    xdot: np.ndarray   # m/s
    xddot: np.ndarray  # m/s^2
    F_hc: np.ndarray   # N    HC force (positive = pushing OS forward)
    P: np.ndarray      # W    instantaneous HC power
    E: float           # J    total HC energy for Phase 3

    # Geometry time series
    x_os_front: np.ndarray      # m  x of OS front face
    x_os_back: np.ndarray       # m  x of OS back face
    x_com_os: np.ndarray        # m  x of OS+payload CoM
    x_com_is: float             # m  x of IS CoM (fixed, negative)
    x_com_total: np.ndarray     # m  x of combined device CoM
    x_front_wheel: np.ndarray   # m  x of front wheel axis
    x_rear_wheel: np.ndarray    # m  x of rear wheel axis
    wheel_contact: np.ndarray   # bool: front wheel axis past step edge

    # Stability
    M_tip: np.ndarray             # N·m tipping moment about step edge
    stability_margin: np.ndarray  # m  + = stable, - = tips if HC released

    @property
    def duration(self) -> float:
        return float(self.t[-1])

    @property
    def F_peak(self) -> float:
        return float(np.max(np.abs(self.F_hc)))

    @property
    def P_peak(self) -> float:
        return float(np.max(self.P))

    @property
    def wheel_contact_time(self) -> Optional[float]:
        idx = int(np.argmax(self.wheel_contact))
        return float(self.t[idx]) if self.wheel_contact[idx] else None

    @property
    def min_stability_margin(self) -> float:
        return float(np.min(self.stability_margin))

    @property
    def M_tip_peak(self) -> float:
        return float(np.max(self.M_tip))

    def summary(self) -> str:
        wct = self.wheel_contact_time
        wct_str = f"{wct:.3f} s" if wct is not None else "never"
        lines = [
            f"=== {self.label} ===",
            f"  OS group mass (moving) : {self.mass_os_group:.2f} kg",
            f"  IS group mass (fixed)  : {self.mass_is_group:.2f} kg",
            f"  HC stroke              : {self.displacement * 100:.1f} cm",
            f"  Duration               : {self.duration:.3f} s",
            f"  Peak HC force          : {self.F_peak:.1f} N",
            f"  Peak HC power          : {self.P_peak:.1f} W",
            f"  HC energy              : {self.E:.2f} J",
            f"  Wheel contact at       : {wct_str}",
            f"  Min stability margin   : "
            f"{self.min_stability_margin * 100:.1f} cm",
            f"  Peak tipping moment    : {self.M_tip_peak:.1f} N*m",
        ]
        return "\n".join(lines)


# ── Simulation ─────────────────────────────────────────────────────────────

def simulate_phase3(params: SimParams) -> Phase3Result:
    """
    Simulate Phase 3: HC extends, pushing OS forward over the upper step.

    Motion: trapezoidal velocity profile (same generator as Phase 2).
    Force:  F_hc = m_os * x_ddot + c_hc * x_dot  (no gravity on horizontal)
    """
    geo = params.geometry
    hc = params.hc
    m = params.mass

    m_os_group = m.m_phase3_os   # OS + payload + upper EC + HC
    m_is_group = m.m_phase4      # IS + FP + lower EC (anchored)

    # kinematics
    t, x_hc, xdot, xddot = trapezoid_profile(
        displacement=hc.stroke,
        v_max=hc.v_max,
        a_max=hc.a_max,
        dt=params.dt,
    )

    # HC force (Coulomb + viscous friction, no gravity on horizontal axis)
    F_hc = (
        m_os_group * xddot
        + hc.F_coulomb * np.sign(xdot)
        + hc.damping * xdot
    )
    P = F_hc * xdot
    _integrate = getattr(np, "trapezoid", None) or np.trapz
    E = float(_integrate(P, t))

    # geometry
    x_os_front = geo.x_os_front_init + x_hc
    x_os_back = x_os_front - geo.L_os

    # CoM of OS group (weighted offset from OS front face toward rear).
    # HC body at OS rear: CoM at ~76% of L_os from front (120 mm body).
    # Upper EC is inside IS (rigid strut), not part of OS group.
    hc_com_frac = 1.0 - 0.06 / geo.L_os  # body centre 60 mm from rear
    os_com_offset = geo.L_os * (
        m.m_outer_shell * geo.com_frac_os
        + m.m_payload * geo.com_frac_payload
        + m.m_hc * hc_com_frac
    ) / m_os_group
    x_com_os = x_os_front - os_com_offset

    x_com_is = -(geo.L_is * geo.com_frac_is)  # fixed, negative x

    x_com_total = (
        m_os_group * x_com_os + m_is_group * x_com_is
    ) / (m_os_group + m_is_group)

    # Front wheel axis x-position (moves with OS)
    x_front_wheel = x_os_front - geo.wheel_offset_front
    x_rear_wheel = x_os_front - geo.wheel_offset_rear

    # Front wheel contacts upper tread when its axis clears the step edge
    # (wheel centre past x=0 → wheel can roll on upper tread surface).
    wheel_contact = x_front_wheel >= 0.0

    # Tipping pivot:
    # Before wheel contact: IS front (x=0) is the only support edge.
    # After  wheel contact: front wheel axis is the new (forward) support edge.
    support_edge = np.where(wheel_contact, x_front_wheel, 0.0)
    stability_margin = support_edge - x_com_total

    # Tipping moment of OS group about step edge (x=0);
    # positive = nose-heavy = EC must resist rotation
    M_tip = m_os_group * G * x_com_os

    return Phase3Result(
        label="Phase 3 - HC Advance (OuterShell to upper step)",
        mass_os_group=m_os_group,
        mass_is_group=m_is_group,
        displacement=hc.stroke,
        t=t, x_hc=x_hc, xdot=xdot, xddot=xddot,
        F_hc=F_hc, P=P, E=E,
        x_os_front=x_os_front, x_os_back=x_os_back,
        x_com_os=x_com_os, x_com_is=x_com_is,
        x_com_total=x_com_total,
        x_front_wheel=x_front_wheel, x_rear_wheel=x_rear_wheel,
        wheel_contact=wheel_contact,
        M_tip=M_tip,
        stability_margin=stability_margin,
    )


# ── Full step cycle ───────────────────────────────────────────────────────────

@dataclass
class StepCycleResult:
    """Combined results for one complete step cycle (phases 2 + 3 + 4)."""
    phase2: PhaseResult
    phase3: Phase3Result
    phase4: PhaseResult

    @property
    def total_energy(self) -> float:
        return self.phase2.E + self.phase3.E + self.phase4.E

    @property
    def total_duration(self) -> float:
        return (
            self.phase2.duration
            + self.phase3.duration
            + self.phase4.duration
        )

    def summary(self) -> str:
        e2, e3, e4 = self.phase2.E, self.phase3.E, self.phase4.E
        d2 = self.phase2.duration
        d3 = self.phase3.duration
        d4 = self.phase4.duration
        lines = [
            "=== Full Step Cycle ===",
            f"  Phase 2 - Elevation  : {e2:6.2f} J  {d2:.2f} s",
            f"  Phase 3 - HC Advance : {e3:6.2f} J  {d3:.2f} s",
            f"  Phase 4 - Retraction : {e4:6.2f} J  {d4:.2f} s",
            "  " + "-" * 35,
            f"  Total energy         : {self.total_energy:6.2f} J",
            f"  Total duration       : {self.total_duration:.2f} s",
        ]
        return "\n".join(lines)


def run_step_cycle(params: SimParams) -> StepCycleResult:
    """Run all three active phases and return combined results."""
    from .sim_1d import run_all as run_1d
    phase2, phase4 = run_1d(params)
    phase3 = simulate_phase3(params)
    return StepCycleResult(phase2=phase2, phase3=phase3, phase4=phase4)
