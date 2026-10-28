# TreppenSchlepper Simulation Project

## What is TreppenSchlepper?

An open project to build a fully autonomous device that carries heavy cargo (and eventually persons) up and down stairs. Target price: **below €500**. The device climbs stairs step-by-step using a telescoping lift-and-slide mechanism. Reference blog: https://treppenschlepper.blogspot.com/

---

## Mechanical Design

### Components

| Part | Role |
|------|------|
| **FootPlate (FP)** | Base plate resting on the stair tread; attached to the lower end of ElevatorCylinder. Contains battery, MCU, and sensors. Rubber underside for grip. |
| **SlidingInnerShell (IS)** | Inner body that houses the ElevatorCylinder and carries the FootPlate via EC. Lifted together with OS in Phase 2, stays elevated at its original x-position during Phase 3, then retracted back into OS in Phase 4. Length = 25 cm (= OuterShell length, so IS fully retracts in Phase 4). Slightly smaller than OS in the y-axis so OS encloses IS when EC is fully retracted. Includes **guide rails** (one on each side) connecting IS to OS — these extend/retract in x-direction and carry z-direction loads (weight of IS + FP when HC is extended). |
| **ElevatorCylinder (EC)** | Vertical linear actuator between FootPlate (bottom) and IS ceiling (top); extends to lift IS+OS together upward while FootPlate stays anchored on the lower tread. In Phase 4, EC retracts first, pulling FP upward into IS (IS is held in place by HC + guide rails). Once EC is fully retracted, HC pulls IS+EC+FP horizontally back into OS. Stroke = rise height (18 cm for 18/27 stair). |
| **HorizontalCylinder (HC)** | Horizontal linear actuator between OuterShell and SlidingInnerShell; pushes OuterShell forward toward the upper step (bracing against static SlidingInnerShell); retracts in Phase 4 to pull SlidingInnerShell + EC + FootPlate back under OuterShell. Stroke = 25 cm = IS/OS length. Body rigidly attached to OS rear; rod tip attaches to IS ceiling at IS **rear face** via a small bracket. HC occupies the z-gap between IS ceiling and OS ceiling = H_OS − H_IS = 60 mm. Contracted (Phases 1, 2): body only (~120 mm) at OS rear, rod retracted, IS and OS share same x-position. Extended (Phase 3): rod spans from IS rear face to OS rear face (250 mm); body (120 mm) continues inside OS. The IS-HC bracket is present in all 4 phases, aligned with IS left (rear) face. |
| **Guide Rails (2x)** | Telescoping rails (one on each side) connecting IS and OS. Extend/retract in x-direction with HC stroke. Carry z-direction load — support IS + FP weight during Phase 4 EC retraction, preventing HC from bending. Ball-bearing drawer slides or similar. |
| **OuterShell (OS)** | Main body carrying the payload; moves vertically (via EC) and horizontally (via HC). Length = 25 cm (reduced from original 40 cm so the device fits on a 27 cm tread). |
| **Wheels (4x, 2 driven)** | Ø 70 mm, mounted on OuterShell. At least the 2 front wheels are motor-driven for positioning and alignment toward the upper step. 2 rear wheels are passive casters or fixed. If tread depth exceeds OS length, wheels drive OS forward to the next step. Steering (y-axis alignment) via differential speed of the two driven front wheels. Front axle 50 mm from OS front face; rear axle 200 mm from OS front (50 mm from back). Wheel axis height above OS lower edge = 0.8 × R = 28 mm, so the wheel protrudes 7 mm below OS bottom, creating a 7 mm clearance gap between OS/IS bottom and the tread surface when driving. |

### Key Structural Relationship

- ElevatorCylinder: vertical, between **FootPlate (bottom)** and **IS ceiling (top)** — EC is inside IS
- HorizontalCylinder: horizontal, body **rigidly attached to OS**, rod end attached to **IS ceiling top**; sits in the z-gap between IS ceiling and OS ceiling (60 mm gap = H_OS − H_IS)
- **Guide rails**: telescoping, one on each side between IS and OS, carry z-direction load (IS+FP weight) when HC is extended; prevent HC from bending under vertical load
- HC body is **rigidly attached to OS**
- OS is **slightly larger than IS in the y-axis** — OS encloses IS when EC is fully retracted
- **Phase 2**: EC lifts IS+OS together; only FP stays on the lower tread
- **Phase 3**: HC pushes OS forward; IS stays at its elevated x-position, held by EC+FP below; guide rails extend
- **Phase 4**: First, EC retracts pulling FP upward into IS (IS held in place by HC + guide rails). Then, HC retracts pulling IS+EC+FP back into OS (guide rails retract)
- OS length = IS length = HC stroke = 25 cm — this ensures IS can fully retract into OS

### Sizing Constraint

OS length must be ≤ tread depth (27 cm). At 25 cm there is 2 cm margin. HC stroke = OS length so the rear of OS clears the step edge at end of Phase 3 and IS can fully retract in Phase 4.

### Mass Distribution — Config B (selected)

Electronics, battery, and sensors are located in the **FootPlate**, not the OuterShell. Wheel motors remain on OS (they must move with the wheels). This keeps OS light and concentrates heavy electronics in FP.

| Group | Config B |
|-------|----------|
| OuterShell (structure + wheels + 2 motors) | **5 kg** |
| SlidingInnerShell (structure + guide rails) | **3 kg** |
| FootPlate (plate + battery + MCU + sensors) | **5 kg** |

**Why Config B:** Lighter OS means lower EC peak force in Phase 2 and better Phase 3 stability margin. Downside: flex cables needed between FP electronics and OS-mounted wheel motors (~250 mm horizontal + ~180 mm vertical travel).

**Wiring note:** Wheel motors sit on OS but are powered from FP. Flex cables or a drag-chain must accommodate Phase 2 vertical travel (180 mm) and Phase 3 horizontal travel (250 mm).

---

## Operation Phases (per step)

### Phase 1 — Position in front of step
Two driven front wheels position the OuterShell in front of the step. Steering is achieved by differential rotation of the two front wheel motors. If the tread depth is larger than OS length, wheels drive forward to reach the next step edge. Y-axis alignment to the step is required. Fully wheel-driven, no actuators involved.

### Phase 2 — Elevation
ElevatorCylinder extends (between FP and IS ceiling), lifting **IS+OS+payload** upward by rise_height. FootPlate remains stationary on the lower tread as the anchor/reaction point. IS and OS move as one unit.

### Phase 3 — Slide OuterShell forward
HorizontalCylinder pushes OuterShell horizontally toward the upper step. IS stays at its elevated position (held in x by EC+FP below), acting as the HC reaction point. Guide rails extend as OS moves forward relative to IS. **Balance-critical phase**: center of mass shifts forward; tipping risk until front wheel axis crosses the step edge. Stability margin is **independent of rise height** — it depends only on OS/IS geometry, wheel offsets, and mass distribution.

### Phase 4 — Retract FootPlate
**Sequential, not simultaneous:**
1. **EC retracts first:** pulls FP upward into IS. IS remains in place, held by HC + guide rails which carry the z-direction load. Only FP + lower EC mass moves vertically.
2. **HC retracts next:** once EC is fully retracted, HC pulls IS + EC + FP horizontally back into OS. Guide rails retract. Device is now fully on the upper step, ready for the next cycle.

---

## Stair Geometry

Standard formula: `1 × tread_depth + 2 × rise_height = 63 cm` (human step length)

Most common stair — **18/27**:
- Rise height: **18 cm**
- Tread depth: **27 cm**

A library of stair types is simulated via `sweep_rise.py` (rise 14–22 cm, see Simulation Results below).

---

## Forces / Physics to Model

- Gravity (on OuterShell + payload, and on SlidingInnerShell/FootPlate)
- ElevatorCylinder force (vertical, lifts IS+OS relative to FootPlate)
- HorizontalCylinder force (horizontal, moves OuterShell relative to SlidingInnerShell)
- Guide rail z-load (supports IS+FP weight when HC is extended in Phase 4)
- Wheel traction (horizontal drive on flat surface)
- Friction — modelled as **Coulomb + viscous**: `F_friction = F_c·sign(v) + c·v`. Pure viscous-only is wrong for lead-screw actuators; Coulomb dominates.
- Contact/collision (FootPlate and wheels vs. stair surfaces)
- Tipping moment (especially phase 3 — overhang of OuterShell before wheel contact)

---

## Simulation Roadmap

1. **1D (z-axis):** estimate actuator requirements, power, timing, energy storage ✅ done
2. **2D (x, z):** add horizontal motion; Phase 3 HC advance, stability/tipping analysis ✅ done
3. **Rise sweep:** energy, duration, forces and stability over 14–22 cm rise range ✅ done
4. **Payload sweep:** energy, duration, forces and stability over 0–100 kg payload ✅ done
5. **3D:** full environment model with stair geometry, complete functional simulation

---

## Simulation Code Structure

```
TreppenSim/
  main_1d.py          — 1-D entry point (Phase 2 + 4 vertical only)
  main_2d.py          — 2-D entry point (full step cycle, all plots)
  sweep_rise.py       — sweeps rise 14–22 cm; plots energy, duration, forces, stability
  sweep_payload.py    — sweeps payload 0–100 kg; plots energy, duration, forces, stability
  draw_phases.py      — generates results/phases_drawing.png (2-D scale drawing, all 4 phases)
  compare_configs.py  — A vs B mass distribution comparison
  sim/
    params.py         — all parameter dataclasses (single source of truth)
    motion.py         — trapezoidal velocity profile generator
    sim_1d.py         — Phase 2 (elevation) and Phase 4 (EC retraction) simulation
    sim_2d.py         — Phase 3 (HC advance) + Phase 4b (HC retraction) + StepCycleResult
  docs/
    phases_diagram.txt — ASCII side-view of all 4 phases (with HC in all phases, to-scale)
    bom_v01.md         — Bill of Materials (Config B)
    prototype_v01.md   — Plywood prototype build plan
  firmware/
    manual_control/    — Arduino Mega manual-button control sketch
  results/            — saved PNG plots
```

### Key parameter classes (`sim/params.py`)

| Class | Controls |
|-------|---------|
| `StairParams` | rise_height, tread_depth |
| `MassParams` | component masses; computes m_phase2, m_phase3_os, m_phase4_ec (FP+lower EC), m_phase4_hc (IS+EC+FP) |
| `ActuatorParams` | EC profile: v_max, a_max, F_coulomb, damping |
| `GeometryParams` | L_os, L_is, h_os, CoM fractions, wheel geometry |
| `HCActuatorParams` | HC profile: v_max, a_max, F_coulomb, damping, stroke |
| `SimParams` | aggregates all above; `actuator_p4` allows different EC speed for Phase 4 |

---

## Current Default Parameters (Config B, 18/27 stair, 3 kg PoC payload)

### Masses
| Component | Mass | Location |
|-----------|------|----------|
| OuterShell (structure + wheels + 2 motors) | 5 kg | OS |
| Payload (PoC) | 3 kg | OS |
| HorizontalCylinder | 1.5 kg | OS (rides up with OS in Phase 2) |
| SlidingInnerShell (structure + guide rails) | 3 kg | IS |
| FootPlate (plate + battery + MCU + sensors) | 5 kg | FP |
| ElevatorCylinder (total) | 3 kg | split 50/50 OS/IS |
| **Phase 2 moving mass** (IS + OS + payload + upper EC + HC) | **14.0 kg** | IS lifts with OS |
| **Phase 3 moving mass** (OS + payload + HC only — IS stationary) | **9.5 kg** | EC is a rigid strut inside IS |
| **Phase 4a moving mass** (FP + lower EC — vertical EC retraction) | **6.5 kg** | IS held by HC + guide rails |
| **Phase 4b moving mass** (IS + EC + FP — horizontal HC retraction) | **11.0 kg** | |

### Geometry
| Parameter | Value |
|-----------|-------|
| OS length | 25 cm |
| IS length | 25 cm |
| Device height (EC extended) | 50 cm |
| Wheel diameter | 70 mm |
| Wheel axis height above OS lower edge | 28 mm (= 0.8 × R_WHEEL); wheel protrudes 7 mm below OS bottom |
| Tread clearance when driving | 7 mm (= 0.2 × R_WHEEL) between OS/IS bottom and floor |
| Front wheel axis from OS front | 50 mm |
| Rear wheel axis from OS front | 200 mm (50 mm from back) |

### Actuator Profiles
| Phase | v_max | a_max | Duration | F_coulomb | damping |
|-------|-------|-------|----------|-----------|---------|
| Phase 2 (EC up) | 30 mm/s | 100 mm/s² | ~6.3 s | 30 N | 80 N·s/m |
| Phase 3 (HC fwd) | 100 mm/s | 500 mm/s² | ~2.7 s | 5 N | 20 N·s/m |
| Phase 4a (EC retract) | 44 mm/s | 100 mm/s² | ~4.3 s | 30 N | 80 N·s/m |
| Phase 4b (HC retract) | 100 mm/s | 500 mm/s² | ~2.7 s | 5 N | 20 N·s/m |

### Simulation Results (Config B, 18/27, 3 kg PoC payload)

| Metric | Value |
|--------|-------|
| EC peak force (Phase 2) | **171 N** |
| HC peak force (Phase 3) | 11.8 N |
| HC energy (Phase 3) | 1.7 J |
| Min stability margin (Phase 3) | +10.1 cm (stable) |
| Wheel contact time (Phase 3) | 0.60 s after start |
| EC peak force (Phase 4a) | **98 N** |
| HC peak force (Phase 4b) | 12.5 N |
| **Total energy per step** | **51.5 J** |
| **Total duration per step** | **16.23 s** |

Phase 2 EC at 30 mm/s, Phase 4a EC at 44 mm/s (natural speed). HC at 100 mm/s (realistic rack-and-pinion). Phase 4 is sequential: EC retracts first (4.5 s), then HC retracts (2.7 s).

### Rise Height Sweep (14–22 cm, `sweep_rise.py`)

Stair formula: tread = 63 − 2 × rise. OS length = 25 cm → **rise ≤ 19 cm** is the fit constraint (tread ≥ OS). Steeper stairs are simulated with tread clamped to 25 cm.

| Rise (cm) | Tread (cm) | E_total (J) | t_total (s) | EC peak (N) | Stability (cm) |
| --------- | ---------- | ----------- | ----------- | ----------- | -------------- |
| 14 | 35 | 40.8 | 14.0 | 171 | 10.1 |
| 15 | 33 | 43.5 | 14.6 | 171 | 10.1 |
| 16 | 31 | 46.2 | 15.1 | 171 | 10.1 |
| 17 | 29 | 48.8 | 15.7 | 171 | 10.1 |
| **18** | **27** | **51.5** | **16.2** | **171** | **10.1** |
| 19 | 25 | 54.2 | 16.8 | 171 | 10.1 |
| 20 | 25\* | 56.8 | 17.4 | 171 | 10.1 |
| 21 | 25\* | 59.5 | 17.9 | 171 | 10.1 |
| 22 | 25\* | 62.2 | 18.5 | 171 | 10.1 |

\* tread clamped to OS length — device barely fits.

**Key findings from sweep:**

- **EC peak force is constant** (171 N) across all rise heights — set by m × a_max + Coulomb friction.
- **Stability margin is constant** (10.1 cm) — Phase 3 geometry is independent of rise.
- **Energy scales linearly** at ~2.7 J per cm of rise.
- **Duration scales linearly** at ~0.56 s per cm of rise.

### Payload Sweep (0–30 kg, `sweep_payload.py`)

Fixed stair 18/27. All other parameters at Config B defaults.

| Payload (kg) | E_total (J) | t_total (s) | EC peak (N) | HC peak (N) | Stability (cm) |
| ------------ | ----------- | ----------- | ----------- | ----------- | -------------- |
| 0 | 46.2 | 16.23 | 141 | 10 | 10.8 |
| **3** | **51.5** | **16.23** | **171** | **12** | **10.1** |
| 5 | 55.0 | 16.23 | 191 | 13 | 9.8 |
| 10 | 63.9 | 16.23 | 241 | 15 | 9.3 |
| 15 | 72.7 | 16.23 | 290 | 18 | 9.0 |
| 20 | 81.5 | 16.23 | 340 | 20 | 8.8 |
| 25 | 90.4 | 16.23 | 389 | 23 | 8.6 |
| 30 | 99.2 | 16.23 | 439 | 25 | 8.5 |

**Key findings:**

- **Duration is constant** (16.23 s) regardless of payload — velocity-governed.
- **Energy scales linearly** at ~1.77 J/kg (= m·g·h for 18 cm rise).
- **EC peak force scales linearly** at ~9.9 N/kg. A 250 N actuator covers up to ~11 kg; a 500 N actuator covers up to ~36 kg.
- **Stability margin: 10.1 cm** at 3 kg PoC — very stable throughout.

---

## Actuator Research Findings

### ElevatorCylinder (EC)
- **Selected:** AliExpress generic lead-screw actuator, 12 V, 200 mm stroke, 300 N rated, ~35 mm/s, ~€25
- Lead-screw = self-locking (holds load without power) — safety-critical requirement met
- Peak force at 3 kg PoC: 171 N → 43% margin under 300 N rating
- Max payload at 300 N: ~16 kg. Upgrade to 750 N or 1000 N actuator for heavier loads.
- 200 mm stroke gives 20 mm margin over 180 mm rise height
- ~~TiMOTION TA2 superseded~~: 1000 N / €150 — massively oversized for 3 kg PoC

### HorizontalCylinder (HC)
- **Selected:** DIY rack-and-pinion — JGA25-370 motor (12 V, 130 RPM, encoder) + M1 steel rack (250 mm) + M1/20T pinion
- HC body rigidly mounted to OS — its mass (1.5 kg) is in Phase 2 moving mass
- HC mounts in the z-gap between IS ceiling and OS ceiling (60 mm gap)
- Stroke = 250 mm; force requirement ~12 N at 3 kg payload
- Speed: 130 RPM × 20 mm PD × π / 60 = ~136 mm/s no-load; ~100 mm/s under 12 N load
- Total HC mechanism cost: ~€20 (motor €9 + rack €8 + pinion €3)
- No off-the-shelf actuator does 250 mm at 100 mm/s at this price

### Guide Rails
- **Selected:** 250 mm full-extension ball-bearing drawer slides, 1 pair, ~€10
- Carry z-load: weight of IS + FP + EC ≈ 11 kg × 9.81 = ~108 N over 2 rails (~54 N each)
- Standard slides rated 15–25 kg each — more than adequate
- Low friction in x-direction, high stiffness in z-direction

### Wheel Motors (2× driven front)
- **Selected:** JGA25-370, 12 V, 60 RPM, Hall encoder, ~€9 each
- 60 RPM × 70 mm wheel × π / 60 = 220 mm/s ≈ 0.8 km/h
- Torque: ~0.5 N·m (>> 0.12 N·m needed for flat-surface drive)
- Differential steering via opposite wheel speeds for y-axis alignment

### Friction Model
- Real lead-screw actuators are dominated by **Coulomb (constant) friction**, not viscous
- Correct model: `F_friction = F_c·sign(v) + c·v`
- EC: F_c = 30 N — typical for lead screw
- HC: F_c = 5 N — lower, rack-and-pinion mechanism

---

## Bill of Materials

See `docs/bom_v01.md` for the current BOM v1.0 (Config B, 12 V, plywood PoC, **€231 total**).

---

## System Architecture

```
UI         │ MobileUI                      │ Dev & Dbg UI
App        │ Env.ID │ Localization │ Path Planning │ System Control │ Energy Mgmt
Middleware │ GPS │ Resource Mgmt │ Low-Level Services │ Safety │ Connectivity
HW         │ Battery │ Power Control │ Motors │ System Sensors │ Environment Sensors
```

### Control Algorithm (4 functions)

1. **Environment Identification** — detect stair geometry, steps, obstacles, persons
2. **Localization/Positioning** — own position relative to stair; ~1 cm for path planning, ~1 mm near step contact
3. **Path Planning** — fully dynamic; compute safe envelopes; refuse to start if no safe path exists
4. **Steering/Control** — follow path within safe envelopes; failsafe to stable static position at any moment

### Sensor Requirements

- Environment: ±2 mm within 1 m; ±1 cm beyond
- Position + orientation (detect tilt/skew)
- Payload weight (overload detection)
- Battery state (charge + temperature)
- Motor state (temperature, torque, wheel speed — detect slip and overload)

---

## Project Goals for this Simulation

1. Verify mechanical designs against tipping-over risk on various stair types
2. Calculate energy, forces, and torques to specify actuator and motor components
3. Provide a virtual environment for developing and testing the control algorithm

---

## License

**MIT License** — see `LICENSE` in the repository root.

- Anyone may use, modify, and distribute the software, designs, and documentation — including for commercial purposes.
- No warranty of any kind is given. The authors cannot guarantee correctness or freedom from third-party rights.
- Attribution required: any use or derivative work must include the original copyright notice and mention Peter Priller as the original author.

---

## Python

Always use `uv` instead of `pip` to run Python scripts (`uv run python ...`).
