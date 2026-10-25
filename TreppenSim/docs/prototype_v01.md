# TreppenSchlepper — Plywood Prototype Build Plan v0.1

> **Goal:** Validate the stair-climbing mechanism with real hardware.
> Proof-of-concept, not final product. 5–10 kg payload. Plywood structure.
>
> **Tools available:** Standard workbench, drill press, jigsaw/circular saw,
> hand tools, screwdrivers, soldering iron. **3D printer** for non-metallic parts.
>
> **Budget target:** < €800 (reduced BOM for proof-of-concept).

---

## 1. Prototype Scope

### What this prototype validates
- Phase 2 elevation (EC lifts IS+OS)
- Phase 3 horizontal advance (HC pushes OS forward)
- Phase 4 retraction (EC+HC retract, FP rises)
- Basic stability on a single step
- Actuator force/speed under real-world friction

### What this prototype does NOT validate
- Autonomous navigation (manual control only)
- Multi-step continuous climbing (one step at a time)
- Full payload (20+ kg) — structural limits of plywood
- Weatherproofing, safety systems

---

## 2. Structural Design — Plywood Construction

All structural parts from **12 mm birch plywood** (strong, affordable, easy to cut/drill).
Use **wood screws + wood glue** for permanent joints, **M5 bolts + T-nuts** for
adjustable/removable connections.

### 2.1 OuterShell (OS)

Open-top box, 250 × 400 × 140 mm (L × W × H).

```
           250 mm
    ┌──────────────────┐
    │                  │  140 mm
    │    (open top)    │
    └──────────────────┘
           400 mm wide (into page)
```

**Cut list (12 mm plywood):**

| Part       | Dimensions (mm)  | Qty | Notes |
|------------|------------------|-----|-------|
| OS bottom  | 250 × 400        | 1   | Floor plate |
| OS front   | 400 × 140        | 1   | Front wall |
| OS back    | 400 × 140        | 1   | Rear wall |
| OS side L  | 226 × 140        | 1   | Left side (inside front+back) |
| OS side R  | 226 × 140        | 1   | Right side |

- Inside clear width: 400 − 2×12 = 376 mm
- Inside clear length: 250 − 2×12 = 226 mm
- Assemble with glue + 4 mm wood screws (pre-drill to prevent splitting)
- Drill holes for wheel motor mounts (see §4)
- Drill slot for HC rod passage through OS back wall (12 × 30 mm slot)
- Weight estimate: ~1.5 kg (plywood density ~680 kg/m³)

### 2.2 SlidingInnerShell (IS)

Open-top tray that slides inside OS. Must clear OS inner walls.

**Inside OS clear dimensions:** 226 × 376 mm
**IS outer dimensions:** 220 × 370 × 80 mm (6 mm clearance total, 3 mm per side)

| Part       | Dimensions (mm)  | Qty | Notes |
|------------|------------------|-----|-------|
| IS bottom  | 220 × 370        | 1   | Floor plate |
| IS front   | 370 × 80         | 1   | Front wall |
| IS back    | 370 × 80         | 1   | Rear wall |
| IS side L  | 196 × 80         | 1   | Left side |
| IS side R  | 196 × 80         | 1   | Right side |

- IS slides on UHMWPE tape (adhesive-backed, applied to IS outer faces and OS inner faces)
- Weight estimate: ~0.8 kg
- Drill holes in IS ceiling area for EC top mount and HC rod attachment

### 2.3 FootPlate (FP)

Simple flat plate with anti-slip rubber on bottom.

| Part       | Dimensions (mm)  | Qty | Notes |
|------------|------------------|-----|-------|
| FP base    | 220 × 370        | 1   | 12 mm plywood |
| Rubber sheet | 220 × 370      | 1   | 3 mm anti-slip rubber, glued |

- Weight estimate: ~0.7 kg (plywood) + 0.2 kg (rubber)
- For prototype: battery and MCU can sit on top of FP, strapped down
- Drill centre hole for EC rod passage (Ø 20 mm)
- Weight target with electronics: ~3 kg (vs 8 kg production — lighter for plywood strength)

### 2.4 IS-to-OS Sliding Guide

Instead of expensive IGUS rails, use **UHMWPE adhesive tape** on contact surfaces.

- Apply 25 mm wide UHMWPE tape strips to:
  - IS outer side faces (both sides, full length)
  - OS inner side faces (both sides, full length)
  - IS bottom outer face (full width, 2 strips)
  - OS bottom inner face (full width, 2 strips)
- Coefficient of friction: ~0.15 (UHMWPE on plywood)
- Cost: ~€8 for a roll of UHMWPE tape

---

## 3. Actuator Integration

### 3.1 ElevatorCylinder (EC)

**TiMOTION TA2, 24 V, 180 mm stroke, 1000 N rated**

Mounting:
- **Bottom mount (FP):** Clevis pin through FP base plate. Drill 2 × Ø8 mm holes
  in FP, 60 mm apart (centred). Use M8 bolt as clevis pin. Reinforce FP locally
  with a 3 mm steel plate (100 × 100 mm) epoxied + screwed under the plywood.
- **Top mount (IS ceiling):** Same clevis arrangement through IS ceiling
  (top edges of IS side walls, with a plywood cross-beam between them).
  IS cross-beam: 370 × 60 × 12 mm plywood, screwed between IS side walls at
  the centre point (110 mm from each end).
- EC retracted length: 285 mm. IS height (80 mm) + FP thickness (12 mm) +
  rubber (3 mm) = 95 mm. Available space for EC = 95 mm (inside IS).
  **Problem:** EC retracted length (285 mm) >> IS internal height (56 mm).

**Critical dimension issue:** The EC retracted length (285 mm) does not fit
inside the 80 mm tall IS. The EC must extend BELOW the FP or ABOVE the IS ceiling.

**Solution:** EC mounts vertically BETWEEN FP bottom and IS cross-beam top,
passing THROUGH the FP plate and IS bottom. The EC body sits exposed between
FP and IS, enclosed by the space between them when extended.

```
  Phase 1 (retracted):        Phase 2 (extended):
  ┌─────IS──────┐             ┌─────IS──────┐
  │  ┌──EC──┐   │                            
  │  │      │   │             │  ┌──EC──┐   │
  │  │      │   │             │  │      │   │
  ├──┤      ├───┤             │  │      │   │
  │FP│      │   │             │  │      │   │
  └──┤      ├───┘             │  │      │   │
     │      │                 │  │      │   │
     └──────┘                 ├──┤      ├───┤
     ▓▓▓▓▓▓▓▓ ← step         │FP│      │   │
                              └──┤      ├───┘
                                 └──────┘
                              ▓▓▓▓▓▓▓▓ ← step
```

EC mounting revised:
- EC bottom end: bolted to a 3 mm steel bracket on FP underside
- EC top end: bolted to IS cross-beam (between IS side walls)
- EC passes through holes in both FP top plate and IS bottom plate
- When retracted: EC spans from FP bottom to IS top (~285 mm = FP_thick + gap + IS_height)
- When extended: gap increases by 180 mm (rise height)

Implication for device height: retracted height ≈ 285 mm (EC) + 140 mm (OS above IS) = 425 mm.

### 3.2 HorizontalCylinder (HC) — Simplified for Prototype

For the prototype, **abandon the 350 mm/s target**. Use a standard linear actuator
at ~100–180 mm/s. Phase 3 will take ~2–3 s instead of ~1 s. Acceptable for PoC.

**Candidate:** Generic 24 V mini linear actuator, 250 mm stroke, 100 N rated,
~150 mm/s. Available on Amazon/AliExpress for ~€30–50.

Alternative (cheaper, simpler): **Threaded rod + DC motor + 3D-printed nut housing.**
- M8 threaded rod (8 mm lead, 1.25 mm pitch)
- 24V DC motor with coupling
- 3D-printed split nut housing with anti-backlash spring
- Speed: depends on motor RPM. At 200 RPM: 200 × 1.25 mm/rev = 250 mm/min = 4.2 mm/s (too slow!)
- Better: M8×8 lead screw (trapezoidal, 8 mm lead): 200 RPM × 8 mm/rev = 1600 mm/min = 27 mm/s
- With a faster motor (1000 RPM): 133 mm/s — usable

**Recommended for prototype:** Buy a 250 mm stroke mini linear actuator (~€40).
Mount body to OS back wall (outside), rod tip to IS back wall (through OS slot).

Mounting:
- OS back wall: drill 4 × M4 holes for actuator bracket (3D-printed)
- IS back wall: drill 2 × M4 holes for rod clevis
- Slot in OS back wall: 12 × 30 mm for rod passage

### 3.3 Actuator Summary (Prototype)

| Actuator | Product | Est. price | Speed | Force |
|----------|---------|-----------|-------|-------|
| EC | TiMOTION TA2, 180 mm, 1000 N | €150 | 30–44 mm/s | 389 N peak |
| HC | Mini linear actuator, 250 mm, 100 N | €40 | ~150 mm/s | 49 N peak |

---

## 4. Wheels & Drive

### 4.1 Wheels
- 4 × Ø70 mm rubber wheels (Pololu or similar hobby wheels)
- Front axle: 50 mm from OS front face
- Rear axle: 200 mm from OS front face (50 mm from back)

### 4.2 Motors
For the prototype at 5–10 kg payload, lower-cost motors suffice.
Total device weight (no payload): ~8 kg. With 10 kg payload: 18 kg.
Rolling resistance force: ~0.02 × 18 × 9.81 = 3.5 N total → 0.9 N per wheel.
Torque per wheel: 0.9 N × 0.035 m = 0.03 N·m — very low.

**Candidate:** JGA25-370 DC gear motor, 12V (run at 12V from buck converter off 24V battery),
~200 RPM, 0.3 N·m stall torque. ~€8 each.

Alternatively: Pololu micro metal gearmotor (cheaper, smaller, adequate for PoC).

### 4.3 Wheel Mounting (3D Printed)

3D-print motor brackets that attach motors to OS side walls.

Each bracket:
- Clamps to OS side wall with M4 bolts (through-holes in plywood)
- Motor press-fits or screw-mounts into bracket
- Wheel hub adaptor (3D-printed or use Pololu hub)

**Files to design:** `motor_bracket_front.stl`, `motor_bracket_rear.stl`

### 4.4 Wheel positions

```
OS side view:
┌────────────────────────────┐
│     ○ rear        ○ front  │  ← wheels protrude 7mm below OS bottom
│     200mm         50mm     │     (from OS front face)
└────────────────────────────┘
      250 mm
```

---

## 5. Electronics — Minimal Prototype

For proof-of-concept, simplify dramatically. Manual control via wired buttons
or simple RC transmitter. No autonomous operation.

### 5.1 Power
- 24 V supply: Use **bench power supply** (24V / 5A) for initial testing.
  Tethered operation — no onboard battery needed for first tests.
- Later: 3S2P 18650 pack (11.1 V) + boost converter to 24 V,
  or 6S LiFePO4 pack (19.2 V nominal, close enough for 24 V actuators).

### 5.2 Control
- **Arduino Mega** or **ESP32** as MCU (€10–15)
- 2 × **BTS7960 H-bridge** modules (€8 each) — one for EC, one for HC
- 2 × **L298N dual H-bridge** modules (€5 each) — for 4 wheel motors
  (L298N handles ~2A per channel, adequate for low-torque wheel motors)
- **Wired control box** with 6 buttons:
  - EC UP / EC DOWN
  - HC EXTEND / HC RETRACT
  - WHEELS FORWARD / WHEELS BACKWARD
- **Emergency stop** button (cuts power to all motors)

### 5.3 Sensors (Prototype Minimum)
- **2 × limit switches** on EC (top and bottom of travel) — €2
- **2 × limit switches** on HC (extended and retracted) — €2
- **1 × IMU (MPU6050)** for tilt monitoring — €4
- No encoders, no ToF, no load cell for first prototype

### 5.4 Wiring

```
24V PSU ──┬── BTS7960 #1 ── EC motor (2 wires)
          ├── BTS7960 #2 ── HC motor (2 wires)
          ├── L298N #1 ──── Wheel motor FL + FR (4 wires)
          ├── L298N #2 ──── Wheel motor RL + RR (4 wires)
          └── Buck 5V ──── Arduino + sensors

Arduino ──┬── BTS7960 #1: EN, RPWM, LPWM (3 pins)
          ├── BTS7960 #2: EN, RPWM, LPWM (3 pins)
          ├── L298N #1: IN1-IN4, ENA, ENB (6 pins)
          ├── L298N #2: IN1-IN4, ENA, ENB (6 pins)
          ├── 4 × limit switches (4 digital inputs)
          ├── MPU6050 (I2C: SDA, SCL)
          └── 6 × control buttons (6 digital inputs)
```

---

## 6. Bill of Materials — Prototype

| # | Part | Qty | Unit € | Total € | Source |
|---|------|-----|--------|---------|--------|
| **Structural** | | | | | |
| 1 | Birch plywood 12mm, 600×400 sheet | 2 | 8 | 16 | Hardware store |
| 2 | UHMWPE adhesive tape 25mm × 5m | 1 | 8 | 8 | Amazon |
| 3 | Anti-slip rubber sheet 3mm, 300×400 | 1 | 5 | 5 | Amazon |
| 4 | Steel reinforcement plate 3mm, 100×100 | 2 | 3 | 6 | Hardware store |
| 5 | 3D printer filament (PETG, ~200g) | 1 | 8 | 8 | — |
| **Actuators** | | | | | |
| 6 | TiMOTION TA2, 24V, 180mm, 1000N | 1 | 150 | 150 | LinearDirect.eu |
| 7 | Mini linear actuator, 24V, 250mm, 100N | 1 | 40 | 40 | Amazon/AliExpress |
| **Wheels & Drive** | | | | | |
| 8 | Ø70mm rubber wheel | 4 | 5 | 20 | Amazon |
| 9 | JGA25-370 DC gear motor 12V 200RPM | 4 | 8 | 32 | Amazon |
| 10 | Wheel hub adaptor (3D printed) | 4 | 0 | 0 | — |
| **Electronics** | | | | | |
| 11 | Arduino Mega 2560 (clone) | 1 | 12 | 12 | Amazon |
| 12 | BTS7960 H-bridge module | 2 | 8 | 16 | Amazon |
| 13 | L298N dual H-bridge module | 2 | 5 | 10 | Amazon |
| 14 | Buck converter 24V→5V | 1 | 4 | 4 | Amazon |
| 15 | Limit switches (micro) | 4 | 1 | 4 | Amazon |
| 16 | MPU6050 breakout | 1 | 4 | 4 | Amazon |
| 17 | Push buttons (panel mount) | 7 | 1 | 7 | Amazon |
| 18 | Emergency stop button (mushroom, NC) | 1 | 5 | 5 | Amazon |
| 19 | Wire assortment (silicone, 18-22 AWG) | 1 | 12 | 12 | Amazon |
| 20 | Connectors (XT60, JST, screw terminals) | 1 | 10 | 10 | Amazon |
| **Fasteners** | | | | | |
| 21 | Wood screws 4×30mm (box 100) | 1 | 5 | 5 | Hardware store |
| 22 | M4×20 bolts + nuts (20 pcs) | 1 | 4 | 4 | Hardware store |
| 23 | M5×30 bolts + T-nuts (10 pcs) | 1 | 5 | 5 | Hardware store |
| 24 | M8×60 bolt (EC clevis pin) | 2 | 1 | 2 | Hardware store |
| 25 | Misc (cable ties, heat shrink, tape) | 1 | 8 | 8 | — |
| **Power (bench testing)** | | | | | |
| 26 | 24V / 5A bench power supply | 1 | 35 | 35 | Amazon |
| | | | | | |
| | **TOTAL** | | | **€448** | |

**Budget headroom to €800 target: €352** (for replacement parts, upgrades, 2nd HC attempt).

---

## 7. Assembly Sequence

### Phase A — Structure (Day 1–2)

1. **Cut plywood** per cut lists (§2.1–2.3). Label all parts.
2. **Assemble OS box:** Glue + screw front, back, sides to bottom plate.
   Let glue cure 4+ hours.
3. **Assemble IS tray:** Same procedure. Verify IS slides into OS with
   ~3 mm clearance per side.
4. **Apply UHMWPE tape** to IS outer faces and OS inner faces.
   Test sliding friction — IS should slide smoothly with light push.
5. **Cut FP plate.** Glue rubber sheet to bottom. Drill EC passage hole (Ø20mm centre).
6. **Add IS cross-beam** for EC top mount (§3.1).

### Phase B — Actuators (Day 3–4)

7. **Mount EC:** Attach bottom clevis to FP (with steel reinforcement plate).
   Attach top clevis to IS cross-beam. Verify stroke: EC should lift IS+OS
   by 180 mm from FP surface.
8. **Mount HC:** Attach body bracket to OS back wall. Attach rod to IS back wall.
   Verify stroke: HC should push OS 250 mm forward relative to IS.
9. **Test actuators manually:** Connect each to bench PSU (24V). Verify direction,
   speed, and full stroke. Measure actual speed with stopwatch.

### Phase C — Wheels & Drive (Day 4–5)

10. **3D-print motor brackets** (4 pcs) and wheel hub adaptors (4 pcs).
11. **Mount motors** to OS side walls using brackets + M4 bolts.
12. **Attach wheels.** Verify OS rolls freely on flat surface.
13. **Test wheel drive:** Connect motors to bench PSU via L298N. Verify
    forward/backward, left/right turns.

### Phase D — Electronics (Day 5–6)

14. **Wire motor drivers** per schematic (§5.4).
15. **Flash Arduino** with basic manual-control firmware.
16. **Wire control buttons** and emergency stop.
17. **Mount limit switches** on EC and HC end-of-travel positions.
18. **Test all functions** individually: EC up/down, HC extend/retract,
    wheels forward/backward.

### Phase E — Integration Test (Day 7)

19. **Build a test step:** One step from scrap wood, 18 cm rise × 27 cm tread.
20. **Manual step-climb sequence:**
    a. Drive up to step edge (wheels).
    b. EC extend (Phase 2) — verify IS+OS lift together.
    c. HC extend (Phase 3) — verify OS slides forward, front wheels reach upper tread.
    d. EC+HC retract (Phase 4) — verify FP lifts from lower tread.
21. **Add 5 kg payload** (bag of sand/books on OS). Repeat step 20.
22. **Add 10 kg payload.** Repeat step 20. Check for:
    - Plywood flex/creak (structural adequacy)
    - Sliding friction (IS in OS)
    - Actuator speed under load
    - Stability during Phase 3

---

## 8. 3D-Printed Parts List

Design in FreeCAD or Fusion 360. Print in PETG (stronger than PLA, heat-resistant).

| Part | Qty | Est. print time | Notes |
|------|-----|-----------------|-------|
| Motor bracket (front) | 2 | 2h each | Clamps to OS side wall |
| Motor bracket (rear) | 2 | 2h each | Same design, different bolt hole spacing |
| Wheel hub adaptor | 4 | 30min each | Couples motor shaft to wheel bore |
| HC body bracket | 1 | 3h | Mounts HC actuator to OS back wall |
| HC rod clevis | 1 | 1h | Connects HC rod to IS back wall |
| Control box enclosure | 1 | 4h | Houses Arduino + buttons |
| EC clevis reinforcement | 2 | 1h each | Distributes load at EC mount points |
| **Total** | **13** | **~18h** | ~200g PETG |

---

## 9. Test Step Construction

Build a single test step from construction lumber or scrap plywood.

```
        ┌─────────────┐
        │  upper tread │ 27 cm deep
        │  (500mm wide)│
  18cm  │             ┌┘
  rise  │             │
        │ lower tread │ 50 cm deep (approach + landing)
        └─────────────┘
```

Materials:
- 2 × 18mm plywood or OSB sheets, ~500 × 500 mm
- 2 × construction timber 45×90mm, 500 mm long (risers)
- Wood screws

Cost: ~€15 from scrap/offcuts, or ~€25 new.

---

## 10. Firmware — Manual Control Sketch

Minimal Arduino sketch for manual button control. No autonomous operation.
Each button directly drives the corresponding motor(s).

**Key safety features in firmware:**
- Limit switch interrupt: stops actuator immediately at end of travel
- IMU tilt check: cuts all motors if tilt > 15° (emergency)
- Emergency stop: hardware NC relay, cuts power bus
- Soft current limit on H-bridges (set via PWM duty cycle limit)

Firmware file: `firmware/manual_control/manual_control.ino`

---

## 11. Risk Register

| Risk | Impact | Mitigation |
|------|--------|------------|
| Plywood too flexible under 10 kg | Mechanism binds | Add aluminium angle reinforcement to OS corners (€10) |
| IS slides too rough | Phase 3/4 stall | More UHMWPE tape; add wax; widen clearance |
| EC doesn't fit vertically | Cannot assemble | Mount EC partially external (see §3.1 revised layout) |
| HC too slow (~150 mm/s) | Phase 3 takes 2 s | Acceptable for PoC; upgrade to rack-and-pinion later |
| Wheel motors too weak on carpet | Can't position | Test on hard floor only; add weight to FP for traction |
| FP doesn't grip step surface | Slips during Phase 2 | Add higher-friction rubber; add suction cups |
| Wires snag during Phase 3 | Motor stall / wire break | Route cables through 3D-printed cable guide with strain relief |

---

## 12. Success Criteria

**Minimum viable prototype (MVP):**
- [ ] Device climbs one 18/27 step under manual control, no payload
- [ ] Device climbs one 18/27 step with 5 kg payload
- [ ] Phase 3 stability: no tipping observed
- [ ] All 4 phases complete in < 30 s total (manual control)

**Stretch goals:**
- [ ] Climb with 10 kg payload
- [ ] Semi-automated sequence (Arduino runs Phase 2→3→4 on single button press)
- [ ] Climb 2 consecutive steps
- [ ] Measured EC force vs simulation comparison
