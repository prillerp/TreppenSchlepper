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
    lower part moves with FootPlate assembly (Phase 4a).
    ec_upper_fraction controls that split (default 0.5).
    """
    # Config B: battery/MCU/sensors in FootPlate; wheel motors on OS.
    m_outer_shell: float = 5.0     # kg  structure + wheels + 2 motors
    m_payload: float = 3.0         # kg  PoC payload
    m_inner_shell: float = 3.0     # kg  structure + guide rails
    m_foot_plate: float = 5.0      # kg  plate + battery + MCU + sensors
    m_elevator_cyl: float = 3.0    # kg  ElevatorCylinder total
    m_hc: float = 1.5              # kg  HorizontalCylinder (rack + motor)
    ec_upper_fraction: float = 0.5

    @property
    def m_ec_upper(self) -> float:
        return self.m_elevator_cyl * self.ec_upper_fraction

    @property
    def m_ec_lower(self) -> float:
        return self.m_elevator_cyl * (1.0 - self.ec_upper_fraction)

    @property
    def m_phase2(self) -> float:
        """Moving mass Ph2: IS+OS+payload+upper EC+HC."""
        return (
            self.m_outer_shell + self.m_payload
            + self.m_inner_shell + self.m_ec_upper + self.m_hc
        )

    @property
    def m_phase3_os(self) -> float:
        """Moving mass Ph3 (OS group): OS + payload + HC."""
        return self.m_outer_shell + self.m_payload + self.m_hc

    @property
    def m_phase4_ec(self) -> float:
        """Phase 4a vertical mass: only FP + lower EC (IS held by HC+rails)."""
        return self.m_foot_plate + self.m_ec_lower

    @property
    def m_phase4_hc(self) -> float:
        """Phase 4b horizontal mass: IS + full EC + FP."""
        return (
            self.m_inner_shell + self.m_elevator_cyl + self.m_foot_plate
        )

    @property
    def m_phase4(self) -> float:
        """Backward-compat alias for Phase 4a EC retraction mass."""
        return self.m_phase4_ec


@dataclass
class ActuatorParams:
    """
    ElevatorCylinder motion profile (trapezoidal velocity).

    Friction model: F_friction = F_coulomb*sign(v) + damping*v
    Lead-screw actuator: Coulomb-dominated.
    """
    v_max: float = 0.03       # m/s  30 mm/s
    a_max: float = 0.10       # m/s²
    F_coulomb: float = 30.0   # N
    damping: float = 80.0     # N·s/m


@dataclass
class GeometryParams:
    """
    Side-view (x-z) dimensions of the device.

    x=0: step edge (IS front face), +x toward upper tread.
    z=0: lower tread surface, +z upward.
    """
    L_os: float = 0.25
    L_is: float = 0.25
    h_os: float = 0.50
    com_frac_os: float = 0.50
    com_frac_payload: float = 0.50
    com_frac_is: float = 0.50
    x_os_front_init: float = 0.0
    wheel_radius: float = 0.035
    wheel_offset_front: float = 0.05
    wheel_offset_rear: float = 0.20


@dataclass
class HCActuatorParams:
    """
    HorizontalCylinder (Phase 3 advance / Phase 4b retraction) profile.

    Realistic target: 100 mm/s with DC motor + rack-and-pinion.
    Friction: 5 N Coulomb + 20 N·s/m viscous.
    """
    v_max: float = 0.10       # m/s  100 mm/s (achievable with rack+pinion)
    a_max: float = 0.50       # m/s²
    F_coulomb: float = 5.0    # N
    damping: float = 20.0     # N·s/m
    stroke: float = 0.25      # m  = L_os


@dataclass
class SimParams:
    stair: StairParams = field(default_factory=StairParams)
    mass: MassParams = field(default_factory=MassParams)
    actuator: ActuatorParams = field(default_factory=ActuatorParams)
    geometry: GeometryParams = field(default_factory=GeometryParams)
    hc: HCActuatorParams = field(default_factory=HCActuatorParams)
    # Phase 4a EC retraction — no PWM limit, natural actuator speed.
    actuator_p4: Optional[ActuatorParams] = field(
        default_factory=lambda: ActuatorParams(
            v_max=0.044, a_max=0.10,
            F_coulomb=30.0, damping=80.0
        )
    )
    dt: float = 0.001  # s
