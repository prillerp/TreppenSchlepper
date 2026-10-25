"""
3-D geometry parameters for TreppenSchlepper.

Extends sim/params.py with the y-axis (lateral/width) dimensions that
are absent from the 2-D model.  All lengths in metres.

Coordinate system (shared with sim_3d.py and draw_3d.py):
  x  — forward, 0 at IS front face (step edge), +x toward upper tread
  y  — lateral, 0 at device centreline, +y to the right
  z  — vertical, 0 at lower tread surface, +z upward
"""

from dataclasses import dataclass, field
from .params import SimParams


@dataclass
class Geometry3DParams:
    """Width (y-axis) dimensions of all parts and the stair environment."""

    # ── Device cross-section (y-axis) ────────────────────────────────────────
    W_os: float = 0.400     # m  OuterShell width
    W_is: float = 0.370     # m  IS width  (slightly narrower so OS encloses IS)
    W_fp: float = 0.400     # m  FootPlate width  (same as OS)
    W_ec: float = 0.040     # m  ElevatorCylinder square cross-section
    W_hc: float = 0.040     # m  HorizontalCylinder square cross-section

    # ── Wheel geometry (y-axis) ───────────────────────────────────────────────
    wheel_width: float = 0.050          # m  tyre width
    wheel_track: float = 0.340          # m  centre-to-centre lateral distance
    #                                       (left axle at y = -track/2, right at +track/2)

    # ── Stair environment ─────────────────────────────────────────────────────
    W_stair: float = 1.000  # m  clear stair width (reference; device is 0.4 m wide)

    # ── Payload box (for visualisation) ──────────────────────────────────────
    H_payload: float = 0.060    # m  payload box height above OS top
    W_payload_margin: float = 0.020  # m  inset from OS sides

    @property
    def W_payload(self) -> float:
        return self.W_os - 2 * self.W_payload_margin

    @property
    def lateral_clearance(self) -> float:
        """Half-gap between device and stair wall on each side."""
        return (self.W_stair - self.W_os) / 2


@dataclass
class SimParams3D:
    """Full parameter set for the 3-D simulation."""
    base: SimParams = field(default_factory=SimParams)
    geo3d: Geometry3DParams = field(default_factory=Geometry3DParams)
