"""
Trapezoidal velocity profile generator.

Produces a position-controlled trajectory for a given displacement:
  - Phase A: constant acceleration from 0 to v_peak
  - Phase B: cruise at v_peak  (may be zero if displacement is too short)
  - Phase C: constant deceleration from v_peak to 0

Returns arrays of (t, z, zdot, zddot) sampled at dt intervals.
The back-calculated actuator force for a mass m with damping c is:
    F_act = m * (zddot + g) + c * zdot
"""

import numpy as np


def trapezoid_profile(
    displacement: float,
    v_max: float,
    a_max: float,
    dt: float = 0.001,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Args:
        displacement: total distance to travel (m), must be > 0
        v_max:        maximum speed (m/s)
        a_max:        acceleration magnitude (m/s²)
        dt:           time step (s)

    Returns:
        t, z, zdot, zddot  — all 1-D numpy arrays of equal length
    """
    if displacement <= 0:
        raise ValueError("displacement must be positive")

    t_acc = v_max / a_max
    d_acc = 0.5 * a_max * t_acc ** 2  # distance covered during one ramp

    if 2.0 * d_acc >= displacement:
        # Triangle profile: no cruise phase, peak speed is lower than v_max
        t_acc = np.sqrt(displacement / a_max)
        t_cruise = 0.0
        v_peak = a_max * t_acc
    else:
        d_cruise = displacement - 2.0 * d_acc
        t_cruise = d_cruise / v_max
        v_peak = v_max

    t_total = 2.0 * t_acc + t_cruise
    t = np.arange(0.0, t_total + dt * 0.5, dt)  # include endpoint

    z     = np.zeros_like(t)
    zdot  = np.zeros_like(t)
    zddot = np.zeros_like(t)

    d_acc_actual = 0.5 * a_max * t_acc ** 2

    for i, ti in enumerate(t):
        if ti <= t_acc:
            # Acceleration ramp
            zddot[i] = a_max
            zdot[i]  = a_max * ti
            z[i]     = 0.5 * a_max * ti ** 2
        elif ti <= t_acc + t_cruise:
            # Cruise
            dt_c = ti - t_acc
            zddot[i] = 0.0
            zdot[i]  = v_peak
            z[i]     = d_acc_actual + v_peak * dt_c
        else:
            # Deceleration ramp
            dt_d = ti - t_acc - t_cruise
            zddot[i] = -a_max
            zdot[i]  = max(0.0, v_peak - a_max * dt_d)
            z[i]     = d_acc_actual + v_peak * t_cruise + v_peak * dt_d - 0.5 * a_max * dt_d ** 2

    # Clamp numerical overshoot
    z = np.clip(z, 0.0, displacement)

    return t, z, zdot, zddot
