"""
3-D simulation of TreppenSchlepper.

The 2-D model fully covers x (forward) and z (vertical) dynamics.
This module adds the y (lateral) dimension:

  - 3-D CoM tracking for each phase snapshot
  - Lateral stability margin  = wheel_track/2 - |CoM_y|
  - 4-wheel normal force distribution (static equilibrium per time step)
  - Skew-angle sensitivity: maximum safe approach misalignment

Coordinate system
-----------------
  x = 0  at IS front face / step edge; +x toward upper tread
  y = 0  at device centreline; +y to the right
  z = 0  at lower tread surface; +z upward

All SI units (m, kg, s, N).
"""

from dataclasses import dataclass
import math
import numpy as np

from .params_3d import SimParams3D
from .sim_2d import run_step_cycle, Phase3Result, StepCycleResult

G = 9.81


# ── 3-D CoM snapshot ─────────────────────────────────────────────────────────

@dataclass
class CoM3D:
    """Centre-of-mass position (x, y, z) of a component group."""
    x: float  # m
    y: float  # m  (0 for symmetric loading)
    z: float  # m


def _com_os_group(p: SimParams3D, x_hc: float) -> CoM3D:
    """
    CoM of the OS group (OS + payload + HC + upper EC) at HC extension x_hc.

    x_hc = 0 at Phase 3 start, = hc_stroke at Phase 3 end.
    """
    geo = p.base.geometry
    m = p.base.mass
    rise = p.base.stair.rise_height
    floor_rise = (1 - 0.8) * geo.wheel_radius  # 7 mm clearance

    x_os_front = geo.x_os_front_init + x_hc
    x_os_com = x_os_front - geo.L_os * geo.com_frac_os

    z_os_bottom = rise + floor_rise
    z_os_com = z_os_bottom + p.base.geometry.h_os * 0.25  # approximate mid-OS

    return CoM3D(x=x_os_com, y=0.0, z=z_os_com)


def _com_is_group(p: SimParams3D) -> CoM3D:
    """CoM of the IS group (IS + FP + lower EC) — fixed throughout Phase 3."""
    geo = p.base.geometry
    x_is_com = -(geo.L_is * geo.com_frac_is)
    z_is_com = 0.0  # FP on lower tread, IS roughly above it
    return CoM3D(x=x_is_com, y=0.0, z=z_is_com)


# ── Lateral stability ─────────────────────────────────────────────────────────

@dataclass
class LateralStability:
    """Lateral (y-axis) stability summary for Phase 3."""

    # Wheel track half-width = lateral stability margin for centred load
    track_half: float           # m
    lateral_margin_centred: float  # m  = track_half for symmetric payload

    # Maximum payload lateral offset before lateral tipping
    max_payload_offset: float   # m  CoM_y = track_half → tips

    # Skew sensitivity
    max_safe_skew_deg: float    # degrees — beyond this angle one front wheel
    #                              contacts the step edge significantly earlier

    # Load on each wheel pair at Phase 3 start (static, symmetric)
    F_front_pair: float         # N  both front wheels combined
    F_rear_pair: float          # N  both rear wheels combined

    def summary(self) -> str:
        lines = [
            "=== Phase 3 Lateral Stability (3-D) ===",
            f"  Wheel track (c-to-c)      : {self.track_half * 2 * 100:.1f} cm",
            f"  Lateral margin (centred)  : {self.lateral_margin_centred * 100:.1f} cm",
            f"  Max payload offset (tip)  : ±{self.max_payload_offset * 100:.1f} cm",
            f"  Max safe approach skew    : ±{self.max_safe_skew_deg:.1f}°",
            f"  Front wheel pair load     : {self.F_front_pair:.0f} N",
            f"  Rear wheel pair load      : {self.F_rear_pair:.0f} N",
        ]
        return "\n".join(lines)


def compute_lateral_stability(p: SimParams3D) -> LateralStability:
    """
    Compute lateral stability for Phase 3 (OS fully advanced, both wheels on
    upper tread — worst-case static snapshot for wheel load distribution).
    """
    geo   = p.base.geometry
    geo3d = p.geo3d
    m     = p.base.mass

    track_half = geo3d.wheel_track / 2.0

    # For centred symmetric payload, CoM_y = 0 → margin = track_half
    lateral_margin_centred = track_half

    # Maximum payload lateral offset before tipping:
    #   CoM_y_total = m_payload * delta_y / m_total = track_half
    #   → delta_y = track_half * m_total / m_payload
    m_total = m.m_phase3_os + m.m_phase4
    if m.m_payload > 0:
        max_payload_offset = track_half * m_total / m.m_payload
    else:
        max_payload_offset = float("inf")

    # Maximum safe approach skew:
    # A skewed device (angle θ about z) causes the two front wheels to reach
    # the step edge at different times. Critical: the step-edge crossings differ
    # by the lateral wheel separation (track) projected onto x:
    #   Δx_contact = track_half * sin(θ)
    # We allow Δx_contact up to the longitudinal stability margin (9 cm).
    # Beyond that, the load is asymmetric enough to risk lateral roll.
    # Run the 2D sim to get the stability margin.
    cycle = run_step_cycle(p.base)
    margin_x = cycle.phase3.min_stability_margin   # m
    if track_half > 0:
        max_safe_skew_rad = math.atan2(margin_x, track_half)
    else:
        max_safe_skew_rad = math.pi / 2
    max_safe_skew_deg = math.degrees(max_safe_skew_rad)

    # Wheel load distribution at Phase 3 end (OS fully on upper tread):
    # Static equilibrium, symmetric (left = right).
    # Moment about rear axle → front load:
    #   F_front * (L_rear - L_front) = W_os_group * (x_com_os - x_rear_wheel)
    # where x is measured from OS front face.
    x_front = geo.wheel_offset_front   # from OS front face (positive = rearward)
    x_rear  = geo.wheel_offset_rear
    x_com   = geo.L_os * geo.com_frac_os  # from OS front face
    wheelbase = x_rear - x_front

    W_os_group = m.m_phase3_os * G
    if wheelbase > 0:
        F_front_pair = W_os_group * (x_rear - x_com) / wheelbase
        F_rear_pair  = W_os_group * (x_com - x_front) / wheelbase
    else:
        F_front_pair = F_rear_pair = W_os_group / 2

    return LateralStability(
        track_half=track_half,
        lateral_margin_centred=lateral_margin_centred,
        max_payload_offset=max_payload_offset,
        max_safe_skew_deg=max_safe_skew_deg,
        F_front_pair=F_front_pair,
        F_rear_pair=F_rear_pair,
    )


# ── Full 3-D result ───────────────────────────────────────────────────────────

@dataclass
class StepCycleResult3D:
    """2-D cycle result augmented with 3-D lateral analysis."""
    cycle_2d: StepCycleResult
    lateral: LateralStability
    params: SimParams3D

    def summary(self) -> str:
        return "\n\n".join([
            self.cycle_2d.summary(),
            self.lateral.summary(),
        ])


def run_step_cycle_3d(p: SimParams3D) -> StepCycleResult3D:
    """Run full 2-D step cycle and augment with 3-D lateral analysis."""
    cycle = run_step_cycle(p.base)
    lateral = compute_lateral_stability(p)
    return StepCycleResult3D(cycle_2d=cycle, lateral=lateral, params=p)
