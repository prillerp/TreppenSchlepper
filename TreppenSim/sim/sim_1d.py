"""
1-D (vertical, z-axis) simulation of the TreppenSchlepper ElevatorCylinder.

Two scenarios are covered:

  Phase2Result  — ELEVATION
      IS + OuterShell + payload + upper-EC lifted together from lower tread
      level to upper tread level (displacement = rise_height).
      FootPlate is the fixed anchor (EC sits between FP and IS ceiling).

  Phase4Result  — RETRACTION  (lifting the FootPlate assembly)
      FootPlate + SlidingInnerShell + lower-EC lifted from lower tread level
      to upper tread level (displacement = rise_height).
      OuterShell is the fixed anchor (sitting on upper tread via wheels).

Both use position-controlled simulation:
  - A trapezoidal velocity profile z(t) is prescribed.
  - The required actuator force is back-calculated from the equation of motion:
        F_act(t) = m * (z̈(t) + g) + c * ż(t)
  - Power:   P(t)  = F_act(t) * ż(t)
  - Energy:  E     = ∫ P dt   (trapezoidal integration)

All SI units (m, kg, s, N, W, J).
"""

from dataclasses import dataclass
import numpy as np
from .params import SimParams
from .motion import trapezoid_profile


G = 9.81  # m/s²


@dataclass
class PhaseResult:
    label: str             # human-readable name
    mass: float            # kg  — moving mass
    displacement: float    # m   — travel distance

    t:      np.ndarray     # s
    z:      np.ndarray     # m   — position of moving body
    zdot:   np.ndarray     # m/s
    zddot:  np.ndarray     # m/s²
    F_act:  np.ndarray     # N   — required actuator force
    P:      np.ndarray     # W   — instantaneous power
    E:      float          # J   — total energy per stroke

    @property
    def duration(self) -> float:
        return float(self.t[-1])

    @property
    def F_peak(self) -> float:
        return float(np.max(self.F_act))

    @property
    def F_static(self) -> float:
        """Minimum force just to hold the mass against gravity (no motion)."""
        return self.mass * G

    @property
    def P_peak(self) -> float:
        return float(np.max(self.P))

    def summary(self) -> str:
        lines = [
            f"=== {self.label} ===",
            f"  Moving mass        : {self.mass:.2f} kg",
            f"  Displacement       : {self.displacement * 100:.1f} cm",
            f"  Duration           : {self.duration:.3f} s",
            f"  Static hold force  : {self.F_static:.1f} N",
            f"  Peak actuator force: {self.F_peak:.1f} N",
            f"  Peak power         : {self.P_peak:.1f} W",
            f"  Energy per stroke  : {self.E:.2f} J",
        ]
        return "\n".join(lines)


def simulate_phase(
    label: str,
    mass: float,
    params: SimParams,
) -> PhaseResult:
    """
    Simulate one vertical lift stroke.

    Args:
        label:   descriptive name for plots / reports
        mass:    moving mass in kg
        params:  full SimParams (stair geometry + actuator profile)

    Returns:
        PhaseResult with trajectories and derived quantities
    """
    rise = params.stair.rise_height
    act = params.actuator

    t, z, zdot, zddot = trapezoid_profile(
        displacement=rise,
        v_max=act.v_max,
        a_max=act.a_max,
        dt=params.dt,
    )

    # Equation of motion (Coulomb + viscous friction):
    #   F_act = m*(zddot + g) + F_c*sign(zdot) + c*zdot
    F_act = (
        mass * (zddot + G)
        + act.F_coulomb * np.sign(zdot)
        + act.damping * zdot
    )

    P = F_act * zdot
    _integrate = getattr(np, "trapezoid", None) or np.trapz
    E = float(_integrate(P, t))

    return PhaseResult(
        label=label,
        mass=mass,
        displacement=rise,
        t=t, z=z, zdot=zdot, zddot=zddot,
        F_act=F_act, P=P, E=E,
    )


def run_all(params: SimParams) -> tuple[PhaseResult, PhaseResult]:
    """Run Phase 2 (Elevation) and Phase 4 (Retraction)."""
    from dataclasses import replace

    phase2 = simulate_phase(
        label="Phase 2 — Elevation (IS + OS + payload)",
        mass=params.mass.m_phase2,
        params=params,
    )

    # Phase 4 may use a faster actuator profile (actuator_p4).
    p4_params = (
        replace(params, actuator=params.actuator_p4)
        if params.actuator_p4 is not None
        else params
    )
    phase4 = simulate_phase(
        label="Phase 4 — Retraction (FootPlate + InnerShell)",
        mass=params.mass.m_phase4,
        params=p4_params,
    )
    return phase2, phase4
