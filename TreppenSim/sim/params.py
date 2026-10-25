from dataclasses import dataclass, field
from typing import Optional


@dataclass
class StairParams:
    """Geometry of a single stair step."""
    rise_height: float = 0.18  # m  (typical 18 cm)
    tread_depth: float = 0.27  # m  (typical 27 cm)


@dataclass
class MassParams:
    """
    Component masses (kg).

    ElevatorCylinder split: upper part moves with OuterShell (Phase 2),
    lower part moves with FootPlate assembly (Phase 4).
    ec_upper_fraction controls that split (default 0.5).
    """
    # Config B: battery/MCU/motors in FootPlate (lighter OS, heavier FP).
    # 6 kg shifted from OS to FP vs Config A (OS=15, FP=2).
    m_outer_shell: float = 9.0     # kg  structural body (structure only)
    m_payload: float = 20.0        # kg  cargo (design point)
    m_inner_shell: float = 4.0     # kg  SlidingInnerShell
    m_foot_plate: float = 8.0      # kg  FootPlate + battery + MCU + sensors
    m_elevator_cyl: float = 3.0    # kg  ElevatorCylinder total
    # HC body is rigidly attached to OS and rides up with it in Phase 2.
    m_hc: float = 1.5              # kg  HorizontalCylinder (rack + motor)
    ec_upper_fraction: float = 0.5  # fraction of EC mass with OuterShell

    @property
    def m_ec_upper(self) -> float:
        return self.m_elevator_cyl * self.ec_upper_fraction

    @property
    def m_ec_lower(self) -> float:
        return self.m_elevator_cyl * (1.0 - self.ec_upper_fraction)

    @property
    def m_phase2(self) -> float:
        """Moving mass Ph2: IS+OS+payload+upper EC+HC (IS and OS lift together)."""
        return (
            self.m_outer_shell + self.m_payload
            + self.m_inner_shell + self.m_ec_upper + self.m_hc
        )

    @property
    def m_phase3_os(self) -> float:
        """Moving mass Ph3 (OS group): OuterShell + payload + HC.
        IS is stationary (held by EC+FP); EC is a rigid strut inside IS."""
        return self.m_outer_shell + self.m_payload + self.m_hc

    @property
    def m_phase4(self) -> float:
        """Moving mass Ph4: FootPlate + InnerShell + lower EC."""
        return self.m_foot_plate + self.m_inner_shell + self.m_ec_lower


@dataclass
class ActuatorParams:
    """
    ElevatorCylinder motion profile (trapezoidal velocity).

    Friction model: F_friction = F_coulomb*sign(v) + damping*v
    TiMOTION TA2 (ACME screw): Coulomb-dominated.
    At v=0.03 m/s: 30 + 80*0.03 = 32.4 N ≈ 3% of 1000 N rated.
    Natural speed at 389 N ≈ 44 mm/s; PWM-limited to 30 mm/s.
    """
    v_max: float = 0.03    # m/s  30 mm/s PWM-limited (TA2 natural ~44 mm/s)
    a_max: float = 0.10       # m/s²  max acceleration / deceleration
    F_coulomb: float = 30.0   # N     constant Coulomb (dry) friction
    damping: float = 80.0     # N·s/m speed-proportional viscous term


@dataclass
class GeometryParams:
    """
    Side-view (x-z) dimensions of the device.

    x=0: step edge (IS front face), +x toward upper tread.
    z=0: lower tread surface, +z upward.
    """
    # Shells — sized to fit on a 27 cm tread
    L_os: float = 0.25          # m  OuterShell length
    L_is: float = 0.25          # m  IS length (= L_os for full retraction)
    h_os: float = 0.50          # m  device height (EC extended)
    # CoM fractions along length: 0 = front face, 1 = rear face
    com_frac_os: float = 0.50
    com_frac_payload: float = 0.50
    com_frac_is: float = 0.50
    # OS front x at start of Phase 3 (0 = flush with step edge)
    x_os_front_init: float = 0.0
    # Wheel geometry — 70 mm diameter, two axles
    wheel_radius: float = 0.035       # m  (70 mm diameter)
    wheel_offset_front: float = 0.05  # m  front axle from OS front face
    wheel_offset_rear: float = 0.20   # m  rear axle (5 cm from OS back)


@dataclass
class HCActuatorParams:
    """
    HorizontalCylinder (Phase 3 / Phase 4 retraction) profile.

    Tuned for ~1 s / 25 cm stroke (rack-and-pinion or belt drive required
    at this speed — standard rod actuators top out at ~180 mm/s).
    Friction: 5 N Coulomb + 20 N·s/m viscous → ~12 N at 350 mm/s.
    """
    v_max: float = 0.35       # m/s
    a_max: float = 1.2        # m/s²
    F_coulomb: float = 5.0    # N     Coulomb friction (ball-screw / rack)
    damping: float = 20.0     # N·s/m
    stroke: float = 0.25      # m  = L_os


@dataclass
class SimParams:
    stair: StairParams = field(default_factory=StairParams)
    mass: MassParams = field(default_factory=MassParams)
    actuator: ActuatorParams = field(default_factory=ActuatorParams)
    geometry: GeometryParams = field(default_factory=GeometryParams)
    hc: HCActuatorParams = field(default_factory=HCActuatorParams)
    # Phase 4 EC retraction — no PWM speed limit (gravity-assisted lowering).
    # TA2 natural speed ~44 mm/s; same a_max as Phase 2 (same motor).
    actuator_p4: Optional[ActuatorParams] = field(
        default_factory=lambda: ActuatorParams(
            v_max=0.044, a_max=0.10, F_coulomb=30.0, damping=80.0
        )
    )
    dt: float = 0.001  # s
