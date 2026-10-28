# TreppenSchlepper Simulation Project

## What is TreppenSchlepper?

An open project to build a fully autonomous device that carries heavy cargo (and eventually persons) up and down stairs. Target price: below €2,000. The device climbs stairs step-by-step using a telescoping lift-and-slide mechanism. Reference blog: https://treppenschlepper.blogspot.com/ (PDF: `C:\Users\prillerp\TreppenSchlepper\TreppenSchlepper.pdf`)

---

## Mechanical Design

### Components

| Part | Role |
|------|------|
| **FootPlate** | Base plate resting on the stair tread; attached to the bottom of SlidingInnerShell |
| **SlidingInnerShell (IS)** | Inner body carrying the FootPlate; lifted together with OS in Phase 2, stays elevated at its original x-position during Phase 3, then retracted back into OS in Phase 4. Length = 25 cm (= OuterShell length, so IS fully retracts in Phase 4). Slightly smaller than OS in the y-axis so OS encloses IS when EC is fully retracted. |
| **ElevatorCylinder (EC)** | Vertical linear actuator between FootPlate (bottom) and IS ceiling (top); extends to lift IS+OS together upward while FootPlate stays anchored on the lower tread. Retracts in Phase 4 to lower IS back to OS floor height. Stroke = rise height (18 cm for 18/27 stair). |
| **HorizontalCylinder (HC)** | Horizontal linear actuator between OuterShell and SlidingInnerShell; pushes OuterShell forward toward the upper step (bracing against static SlidingInnerShell); retracts to pull SlidingInnerShell + FootPlate back under OuterShell. Stroke = 25 cm = IS/OS length. Body rigidly attached to OS rear; rod tip attaches to IS ceiling at IS **rear face** via a small bracket. HC occupies the z-gap between IS ceiling and OS ceiling = H_OS − H_IS = 60 mm. Contracted (Phases 1, 2, 4): body only (~120 mm) at OS rear, rod retracted, IS and OS share same x-position. Extended (Phase 3): rod spans from IS rear face to OS rear face (250 mm); body (120 mm) continues inside OS. The IS-HC bracket is present in all 4 phases, aligned with IS left (rear) face. |
| **OuterShell (OS)** | Main body carrying the payload; moves vertically (via EC) and horizontally (via HC). Length = 25 cm (reduced from original 40 cm so the device fits on a 27 cm tread). |
| **Wheels (4x)** | Ø 70 mm, mounted on OuterShell; flat-surface travel and positioning; differential steering via opposite rotation on one axle. Front axle 50 mm from OS front face; rear axle 200 mm from OS front (50 mm from back). Wheel axis height above OS lower edge = 0.8 × R = 28 mm, so the wheel protrudes 7 mm below OS bottom, creating a 7 mm clearance gap between OS/IS bottom and the tread surface when driving. |

### Key Structural Relationship

- ElevatorCylinder: vertical, between **FootPlate (bottom)** and **IS ceiling (top)** — EC is inside IS
- HorizontalCylinder: horizontal, body **rigidly attached to OS**, rod end attached to **IS ceiling top**; sits in the z-gap between IS ceiling and OS ceiling (60 mm gap = H_OS − H_IS)
- HC body is **rigidly attached to OS**
- OS is **slightly larger than IS in the y-axis** — OS encloses IS when EC is fully retracted
- **Phase 2**: EC lifts IS+OS together; only FP stays on the lower tread
- **Phase 3**: HC pushes OS forward; IS stays at its elevated x-position, held by EC+FP below
- **Phase 4**: HC retracts pulling IS back into OS (x); EC retracts lowering IS to OS floor height
- OS length = IS length = HC stroke = 25 cm — this ensures IS can fully retract into OS

### Sizing Constraint

OS length must be ≤ tread depth (27 cm). At 25 cm there is 2 cm margin. HC stroke = OS length so the rear of OS clears the step edge at end of Phase 3 and IS can fully retract in Phase 4.

### Mass Distribution — Config B (selected)

Electronics, battery, and wheel motors are located in the **FootPlate**, not the OuterShell. This keeps OS structurally light and concentrates heavy components in FP.

| Group | Config A | Config B | Shift |
|-------|----------|----------|-------|
| OuterShell | 15 kg (structure + electronics) | **9 kg** (structure only) | −6 kg |
| FootPlate | 2 kg (bare plate) | **8 kg** (plate + battery + MCU + sensors) | +6 kg |

**Why Config B:** Total energy per step is identical (physics is symmetric — you lift the same total mass through the same height regardless of which phase). The advantage is actuator sizing: Phase 2 EC peak force drops from 411 N to 351 N, allowing a smaller/cheaper cylinder. Phase 3 stability margin also improves slightly (+0.7 cm). Downside: flex cables needed between FP electronics and OS-mounted wheel motors (~250 mm horizontal + ~180 mm vertical travel).

**Wiring note:** Wheel motors sit on OS but are powered from FP. Flex cables or a drag-chain must accommodate Phase 2 vertical travel (180 mm) and Phase 3 horizontal travel (250 mm).

---

## Operation Phases (per step)

### Phase 1 — Position in front of step
All four wheels drive the OuterShell into position. Turning is achieved by differential rotation of wheels on the same axle (tank-style steering). Fully wheel-driven, no actuators involved.

### Phase 2 — Elevation
ElevatorCylinder extends (between FP and IS ceiling), lifting **IS+OS+payload** upward by rise_height. FootPlate remains stationary on the lower tread as the anchor/reaction point. IS and OS move as one unit.

### Phase 3 — Slide OuterShell forward
HorizontalCylinder pushes OuterShell horizontally toward the upper step. IS stays at its elevated position (held in x by EC+FP below), acting as the HC reaction point. **Balance-critical phase**: center of mass shifts forward; tipping risk until front wheel axis crosses the step edge (at ~0.29 s into Phase 3 for default params). Minimum stability margin is +9.0 cm (stable throughout for default params). Stability margin is **independent of rise height** — it depends only on OS/IS geometry, wheel offsets, and mass distribution.

### Phase 4 — Retract FootPlate
FootPlate is lifted (freed from lower tread). HorizontalCylinder retracts, pulling SlidingInnerShell + FootPlate back inside OuterShell. Simultaneously, ElevatorCylinder retracts to lower IS/FP to OS floor height. Device is now fully on the upper step, ready for the next cycle.

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
    sim_2d.py         — Phase 3 (HC advance) + StepCycleResult combining all phases
  docs/
    phases_diagram.txt — ASCII side-view of all 4 phases (with HC in all phases, to-scale)
    bom_v01.md         — Bill of Materials v0.3 (Config B)
    prototype_v01.md   — Plywood prototype build plan (5–10 kg PoC)
  firmware/
    manual_control/    — Arduino Mega manual-button control sketch
  results/            — saved PNG plots
```

### Key parameter classes (`sim/params.py`)

| Class | Controls |
|-------|---------|
| `StairParams` | rise_height, tread_depth |
| `MassParams` | component masses; computes m_phase2 (includes m_hc), m_phase4 |
| `ActuatorParams` | EC profile: v_max, a_max, F_coulomb, damping |
| `GeometryParams` | L_os, L_is, h_os, CoM fractions, wheel geometry |
| `HCActuatorParams` | HC profile: v_max, a_max, F_coulomb, damping, stroke |
| `SimParams` | aggregates all above; `actuator_p4` allows different EC speed for Phase 4 |

---

## Current Default Parameters (Config B, 18/27 stair, 20 kg payload)

### Masses
| Component | Mass | Location |
|-----------|------|----------|
| OuterShell | 9 kg | OS (structure only) |
| Payload (design point) | 20 kg | OS |
| HorizontalCylinder | 1.5 kg | OS (rides up with OS in Phase 2) |
| SlidingInnerShell | 4 kg | IS |
| FootPlate | 8 kg | FP (incl. battery, MCU, sensors) |
| ElevatorCylinder (total) | 3 kg | split 50/50 OS/IS |
| **Phase 2 moving mass** (IS + OS + payload + upper EC + HC) | **36.0 kg** | IS now lifts with OS |
| **Phase 3 moving mass** (OS + payload + HC only — IS stationary) | **30.5 kg** | EC is a rigid strut inside IS |
| **Phase 4 moving mass** (IS + FP + lower EC) | **13.5 kg** | |

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
| Phase 2 (EC up) | **30 mm/s** | 100 mm/s² | **~6.3 s** | 30 N | 80 N·s/m |
| Phase 3 (HC fwd) | 350 mm/s | 1200 mm/s² | ~1.0 s | 5 N | 20 N·s/m |
| Phase 4 (EC retract) | **44 mm/s** | 100 mm/s² | **~4.5 s** | 30 N | 80 N·s/m |

### Simulation Results (Config B, 18/27, 20 kg payload)

| Metric | Value |
|--------|-------|
| EC peak force (Phase 2) | **389 N** |
| HC peak force (Phase 3) | 48.6 N |
| HC energy (Phase 3) | 2.8 J |
| Min stability margin (Phase 3) | +9.3 cm (stable) |
| Wheel contact time (Phase 3) | 0.29 s after start |
| EC peak force (Phase 4) | **167 N** |
| **Total energy per step** | **102.0 J** |
| **Total duration per step** | **11.84 s** |

Phase 2 EC runs at 30 mm/s (PWM-limited). Phase 4 EC runs at 44 mm/s (natural TA2 speed, no PWM limit — gravity-assisted retraction with lighter load). Phase 4 duration increased from the erroneous ~1 s to realistic ~4.5 s; total step time 11.84 s. Peak force is set by m × a_max + Coulomb friction, not by speed.

### Rise Height Sweep (14–22 cm, `sweep_rise.py`)

Stair formula: tread = 63 − 2 × rise. OS length = 25 cm → **rise ≤ 19 cm** is the fit constraint (tread ≥ OS). Steeper stairs are simulated with tread clamped to 25 cm.

| Rise (cm) | Tread (cm) | E_total (J) | t_total (s) | EC peak (N) | Stability (cm) |
| --------- | ---------- | ----------- | ----------- | ----------- | -------------- |
| 14 | 35 | 79.9 | 9.60 | 389 | 9.3 |
| 15 | 33 | 85.5 | 10.16 | 389 | 9.3 |
| 16 | 31 | 91.0 | 10.71 | 389 | 9.3 |
| 17 | 29 | 96.5 | 11.28 | 389 | 9.3 |
| **18** | **27** | **102.0** | **11.84** | **389** | **9.3** |
| 19 | 25 | 107.5 | 12.40 | 389 | 9.3 |
| 20 | 25\* | 113.0 | 12.96 | 389 | 9.3 |
| 21 | 25\* | 118.6 | 13.52 | 389 | 9.3 |
| 22 | 25\* | 124.1 | 14.08 | 389 | 9.3 |

\* tread clamped to OS length — device barely fits.

**Key findings from sweep (EC at 30 mm/s):**

- **EC peak force is constant** (389 N) across all rise heights. Peak occurs during acceleration; set by m × a_max + Coulomb friction, independent of stroke or speed.
- **Stability margin is constant** (9.3 cm) across all rise heights. Phase 3 geometry is independent of rise.
- **Energy scales linearly** at ~5.5 J per cm of rise (Phase 2 + 4 dominate; Phase 3 contributes a fixed ~2.8 J).
- **Duration scales linearly** at ~0.56 s per cm of rise (Phase 2 at 30 mm/s + Phase 4 at 44 mm/s).
- TiMOTION TA2 (1000 N rated) has 611 N margin over 389 N peak across the entire range — well within spec.

### Payload Mass Sweep (0–100 kg, `sweep_payload.py`)

Fixed stair 18/27. All other parameters at Config B defaults.

| Payload (kg) | E_total (J) | t_total (s) | EC peak (N) | HC peak (N) | Stability (cm) |
| ------------ | ----------- | ----------- | ----------- | ----------- | -------------- |
| 0 | 66.7 | 11.84 | 191 | 25 | 10.7 |
| 10 | 84.3 | 11.84 | 290 | 37 | 9.8 |
| **20** | **102.0** | **11.84** | **389** | **49** | **9.3** |
| 30 | 119.7 | 11.84 | 488 | 61 | 8.9 |
| 40 | 137.3 | 11.84 | 587 | 73 | 8.7 |
| 50 | 155.0 | 11.84 | 687 | 85 | 8.5 |
| 60 | 172.6 | 11.84 | 786 | 97 | 8.4 |
| 70 | 190.3 | 11.84 | 885 | 109 | 8.3 |
| 80 | 208.0 | 11.84 | 984 | 121 | 8.2 |
| 90 | 225.6 | 11.84 | 1083 | 133 | 8.2 |
| 100 | 243.3 | 11.84 | 1182 | 145 | 8.1 |

**Key findings from sweep (EC at 30 mm/s):**

- **Duration is constant** (11.84 s) regardless of payload. Velocity-governed trapezoidal profile; only force and energy change.
- **Energy scales linearly** at ~1.77 J/kg — exactly m·g·h = 1 kg × 9.81 m/s² × 0.18 m = 1.77 J/kg. Physics confirmed.
- **EC peak force scales linearly** at ~9.9 N/kg. TiMOTION TA2 (1000 N rated) → maximum safe payload **~82 kg** ((1000 − 191) / 9.9 ≈ 82 kg) — person transport range enabled. (At 80 kg: 984 N ✓; at 90 kg: 1083 N ✗.)
- **Stability margin decreases slightly** with payload: 10.7 cm (empty) → 8.1 cm (100 kg). Still well positive throughout.
- **HC peak force scales linearly** at ~1.0 N/kg.

---

## Actuator Research Findings

### ElevatorCylinder (EC)
- **Candidate:** TiMOTION TA2, 24 V, 180 mm stroke, code A (1000 N rated), no built-in feedback, IP66D
- ACME lead-screw, self-locking (holds load without power); weight ~1.2 kg
- Natural speed at 389 N load ≈ **44 mm/s**; PWM speed controller limits to 30 mm/s for predictable motion
- Friction: predominantly Coulomb (~30 N), small viscous term (same model as before)
- **Config B impact at 20 kg payload:** Phase 2 peak force 389 N; Phase 4 peak force 167 N — 611 N margin under 1000 N rated
- **Maximum safe payload: ~82 kg** (EC limit: (1000 − 191) / 9.9 N/kg ≈ 82 kg) — person transport range enabled
- EU stock at LinearDirect.eu; contact TiMOTION Europe for quote (estimate €120–180)
- Retracted length for 180 mm stroke: 285 mm (no feedback) — fits device height of ~320 mm with ~35 mm margin
- Order without built-in feedback; use AS5600 external encoder for EC position (already in sensor BOM, item 23)
- ~~LINAK LA12 rejected~~: max stroke 130 mm (need 180 mm), max speed 5–6 mm/s (need 30 mm/s)
- ~~Mini Industrial A superseded~~: 500 N rating limited max payload to 31 kg; person transport not possible

### HorizontalCylinder (HC)

- HC body is rigidly mounted to OS — its mass (1.5 kg) is included in the Phase 2 moving mass
- HC mounts in the z-gap between IS ceiling and OS ceiling (60 mm gap); body length ~120 mm (contracted), full extended span = 250 mm stroke
- **350 mm/s cannot be achieved by a standard rod actuator** (commercial max ~180 mm/s under load)
- Required mechanism: **rack-and-pinion or toothed-belt linear drive**
- Alternatively: accept slower Phase 3 (~2 s) with a fast rod actuator
- Candidate for slower option: D-Series high-speed actuator (electric-linear-actuators.com), ~200 mm/s / 100 N

### Friction Model
- Real lead-screw actuators are dominated by **Coulomb (constant) friction**, not viscous
- Correct model: `F_friction = F_c·sign(v) + c·v`
- Viscous-only model (old) underestimated friction ~3×
- EC: F_c = 30 N (≈11% of 300 N rated) — typical for well-lubricated lead screw
- HC: F_c = 5 N — lower, assumes ball-screw or rack mechanism

### Config A vs Config B — Mass Distribution Decision

- Total energy per step is **identical** regardless of whether electronics are in OS or FP (97.7 J either way) — this is a conservation-of-energy identity, not a coincidence
- Config B (FP-heavy) was chosen for: smaller EC peak force in Phase 2, better Phase 3 stability margin (+9.0 cm vs Config A). Exact Config A comparison needs re-running with corrected model.
- Tradeoff: flex cables / drag-chain needed between FP electronics and OS wheel motors
- See `compare_configs.py` for the full comparison

---

## Bill of Materials

See `docs/bom_v01.md` for the current BOM (v0.2, Config B) with candidate products.

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
