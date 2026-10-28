# TreppenSchlepper — Plywood Prototype Build Plan v1.0

> **Goal:** Validate the stair-climbing mechanism with real hardware.
> Proof-of-concept, not final product. **3 kg payload**. Plywood structure.
>
> **Tools available:** Standard workbench, drill press, jigsaw/circular saw,
> hand tools, screwdrivers, soldering iron. **3D printer** for non-metallic parts.
>
> **Budget target:** < €500 (BOM total: ~€231, see `docs/bom_v01.md`)
>
> **System voltage:** 12 V DC (3S LiPo battery)

---

## 1. Prototype Scope

### What this prototype validates
- Phase 2 elevation (EC lifts IS+OS)
- Phase 3 horizontal advance (HC pushes OS forward via rack-and-pinion)
- Phase 4a EC retraction (pulls FP up into IS; IS held by guide rails + HC)
- Phase 4b HC retraction (pulls IS+EC+FP back into OS)
- Basic stability on a single step
- Actuator force/speed under real-world friction
- Guide rail function (carry z-load during Phase 4a)

### What this prototype does NOT validate
- Autonomous navigation (manual control only)
- Multi-step continuous climbing (one step at a time)
- Heavy payload (>10 kg) — structural limits of plywood
- Weatherproofing, safety systems

---

## 2. Structural Design — Plywood Construction

All structural parts from **12 mm birch plywood** (strong, affordable, easy to cut/drill).
Use **wood screws + wood glue** for permanent joints, **M4 bolts** for adjustable
connections.

### 2.1 OuterShell (OS)

Open-top box, 250 × 250 × 140 mm (L × W × H).

```
           250 mm
    ┌──────────────────┐
    │                  │  140 mm
    │    (open top)    │
    └──────────────────┘
           250 mm wide (into page)
```

**Cut list (12 mm plywood):**

| Part       | Dimensions (mm)  | Qty | Notes |
|------------|------------------|-----|-------|
| OS bottom  | 250 × 250        | 1   | Floor plate |
| OS front   | 250 × 140        | 1   | Front wall |
| OS back    | 250 × 140        | 1   | Rear wall |
| OS side L  | 226 × 140        | 1   | Left side (inside front+back) |
| OS side R  | 226 × 140        | 1   | Right side |

- Inside clear width: 250 − 2×12 = 226 mm
- Inside clear length: 250 − 2×12 = 226 mm
- Assemble with glue + 4 mm wood screws (pre-drill to prevent splitting)
- Mount guide rail (drawer slide) to each inside side wall
- Drill holes for wheel motor mounts through front wall (see §4)
- Drill slot for HC rack passage through OS back wall
- Weight estimate: ~1.2 kg (plywood density ~680 kg/m³)

### 2.2 SlidingInnerShell (IS)

Tray that slides inside OS on guide rails (drawer slides).

**IS outer dimensions:** 220 × 230 × 80 mm (clearance for drawer slide mechanism)

| Part       | Dimensions (mm)  | Qty | Notes |
|------------|------------------|-----|-------|
| IS bottom  | 220 × 230        | 1   | Floor plate |
| IS front   | 230 × 80         | 1   | Front wall |
| IS back    | 230 × 80         | 1   | Rear wall |
| IS side L  | 196 × 80         | 1   | Left side |
| IS side R  | 196 × 80         | 1   | Right side |

- IS rides on guide rails (one drawer slide on each side)
- Weight estimate: ~0.7 kg
- Add cross-beam between IS side walls at centre for EC top mount
- Mount HC rack to IS ceiling (top of side walls)

### 2.3 FootPlate (FP)

Simple flat plate with anti-slip rubber on bottom.

| Part       | Dimensions (mm)  | Qty | Notes |
|------------|------------------|-----|-------|
| FP base    | 220 × 230        | 1   | 6 mm plywood |
| Rubber sheet | 220 × 230      | 1   | 2 mm anti-slip rubber, glued |

- Weight estimate: ~0.4 kg (plywood) + 0.15 kg (rubber)
- Battery and MCU sit on top of FP, strapped down
- Drill centre hole for EC rod passage (Ø 20 mm)
- Weight target with electronics: ~3 kg (lighter than production 5 kg)

### 2.4 Guide Rails (IS-to-OS)

**250 mm full-extension ball-bearing drawer slides, 1 pair.**

- Mount the fixed (outer) part to OS side walls
- Mount the moving (inner) part to IS side walls
- These carry IS+FP z-load during Phase 4a (when EC retracts and IS hangs from HC+rails)
- Z-load: ~11 kg × 9.81 = ~108 N over 2 slides → ~54 N each (well within 15 kg/slide rating)
- x-direction: low friction, allows IS to slide 250 mm in/out of OS

---

## 3. Actuator Integration

### 3.1 ElevatorCylinder (EC)

**12 V lead-screw linear actuator, 200 mm stroke, 300 N rated, ~35 mm/s**

The EC retracted length (~180 mm for a 200 mm stroke cheap actuator) does not fit
inside the 80 mm tall IS. The EC must extend between FP and IS, passing through
both plates.

```
  Phase 1 (retracted):        Phase 2 (extended):
  ┌─────IS──────┐             ┌─────IS──────┐
  │  ┌──EC──┐   │
  │  │      │   │             │  ┌──EC──┐   │
  ├──┤      ├───┤             │  │      │   │
  │FP│      │   │             │  │      │   │
  └──┤      ├───┘             │  │      │   │
     └──────┘                 ├──┤      ├───┤
     ▓▓▓▓▓▓▓▓ ← step         │FP│      │   │
                              └──┤      ├───┘
                                 └──────┘
                              ▓▓▓▓▓▓▓▓ ← step
```

Mounting:
- **Bottom mount (FP):** Clevis bracket on FP underside. M6 bolt as clevis pin.
  Reinforce FP locally with a 3D-printed load spreader plate.
- **Top mount (IS ceiling):** Clevis bracket on IS cross-beam (plywood bar
  between IS side walls, 230 × 50 × 12 mm, at centre).
- EC passes through holes in both FP top plate and IS bottom plate.

### 3.2 HorizontalCylinder (HC) — DIY Rack-and-Pinion

**JGA25-370 motor (12 V, 130 RPM) + M1 steel rack (250 mm) + M1/20T pinion**

The motor+pinion assembly mounts to OS (rigidly). The rack mounts to IS ceiling.
When the motor turns, the pinion drives along the rack, pushing OS forward
(or pulling IS back).

```
  OS ceiling (top view):
  ┌──────────────────────────────┐
  │  [Motor+Pinion] ←OS mount   │
  │       ↓ mesh                │
  │  ═══════════════ ←rack on IS│
  │                              │
  └──────────────────────────────┘
```

Mounting:
- **Motor mount:** 3D-printed bracket, M3 screws to OS ceiling/back wall.
  Motor sits in the 60 mm z-gap between IS ceiling and OS ceiling.
- **Rack:** M3 screws along IS ceiling top surface. Rack teeth face downward.
- **Pinion:** Press-fit or grub screw on motor 6 mm D-shaft.
  PD = 20 mm → centre-to-centre = 10 mm from rack pitch line.

Speed check: 130 RPM × π × 20 mm / 60 = 136 mm/s no-load → ~100 mm/s under load.

### 3.3 Actuator Summary (Prototype)

| Actuator | Product | Price | Speed | Peak force (3 kg) |
|----------|---------|-------|-------|-------------------|
| EC | 12 V lead-screw, 200 mm, 300 N | ~€25 | ~35 mm/s | 171 N |
| HC | JGA25-370 + M1 rack-and-pinion | ~€20 | ~100 mm/s | 12.5 N |

---

## 4. Wheels & Drive

### 4.1 Wheels
- 2 × Ø70 mm rubber **driven wheels** (front axle, 50 mm from OS front)
- 2 × Ø70 mm (or similar) **passive casters** (rear, 200 mm from OS front)

### 4.2 Motors
**2 × JGA25-370 DC gear motor, 12 V, 60 RPM, with Hall encoder**

Speed: 60 RPM × π × 70 mm / 60 = 220 mm/s ≈ 0.8 km/h
Rolling resistance force: ~0.02 × 18 kg × 9.81 = 3.5 N total → 1.75 N/wheel
Torque per wheel: 1.75 N × 0.035 m = 0.06 N·m — well within 0.5 N·m motor stall torque.

Differential steering: run left wheel faster than right (or vice versa) to turn.
Encoder feedback enables closed-loop speed matching.

### 4.3 Wheel Mounting (3D Printed)

Each front motor bracket:
- Bolts through OS front wall or side wall with M4 bolts
- Motor press-fits into bracket cavity
- Wheel hub adaptor couples 6 mm D-shaft to wheel bore

Rear casters: standard small furniture casters, screw-mount to OS bottom.

### 4.4 Wheel positions

```
OS side view:
┌────────────────────────────┐
│  ○ caster       ○ driven   │  ← wheels protrude 7 mm below OS bottom
│  200 mm         50 mm      │     (from OS front face)
└────────────────────────────┘
      250 mm
```

---

## 5. Electronics — Minimal Prototype

Manual control via 8 wired buttons. No autonomous operation.
All powered from **3S 11.1 V LiPo** (55 Wh).

### 5.1 Power
- **3S 11.1 V 5000 mAh LiPo** battery on FP
- **Buck converter** 12 V→5 V for Arduino + sensors
- 15 A inline fuse + toggle switch for power distribution
- For bench testing: can also use a 12 V bench PSU (tethered)

### 5.2 Control
- **Arduino Mega 2560** clone as MCU (~€18)
- **2 × BTS7960** H-bridge modules (~€2 each) — EC motor, HC motor
- **1 × L298N** dual H-bridge (~€3) — left + right wheel motors
- **8 wired control buttons:**
  - EC UP / EC DOWN
  - HC EXTEND / HC RETRACT
  - WHEELS FORWARD / WHEELS BACKWARD
  - STEER LEFT / STEER RIGHT
- **Emergency stop** (mushroom button, NC contact)

### 5.3 Sensors (Prototype Minimum)
- **4 × limit switches** (EC top, EC bottom, HC extended, HC retracted) — €4
- **1 × MPU6050 IMU** for tilt monitoring — €1.50
- No encoders, no ToF, no load cell for first prototype

### 5.4 Wiring

```
12V LiPo ──┬── BTS7960 #1 ── EC motor (2 wires)
            ├── BTS7960 #2 ── HC motor (2 wires)
            ├── L298N ─────── Wheel L + R (4 wires)
            └── Buck 5V ──── Arduino + sensors

Arduino ──┬── BTS7960 #1: EN, RPWM, LPWM (3 pins)
          ├── BTS7960 #2: EN, RPWM, LPWM (3 pins)
          ├── L298N: IN1-IN4, ENA, ENB (6 pins)
          ├── 4 × limit switches (4 digital inputs)
          ├── MPU6050 (I2C: SDA=20, SCL=21)
          └── 8 × control buttons + E-stop (9 digital inputs)
```

**Flex cable note:** Battery and MCU are on FP, but wheel motors and HC motor
are on OS. A flex cable harness (~6+ conductors) must loop between FP and OS
with enough slack for 250 mm horizontal + 180 mm vertical travel.

---

## 6. Assembly Sequence

### Phase A — Structure (Day 1–2)

1. **Cut plywood** per cut lists (§2.1–2.3). Label all parts.
2. **Assemble OS box:** Glue + screw front, back, sides to bottom plate.
   Let glue cure 4+ hours.
3. **Assemble IS tray:** Same procedure.
4. **Mount guide rails:** Screw drawer slide outer rail to each OS side wall.
   Screw inner rail to each IS side wall. Test: IS should slide smoothly
   in and out of OS with light push.
5. **Cut FP plate** (6 mm plywood). Glue rubber sheet to bottom.
   Drill EC passage hole (Ø20 mm centre).
6. **Add IS cross-beam** for EC top mount (230 × 50 × 12 mm plywood bar
   between IS side walls at midpoint).

### Phase B — Actuators (Day 3–4)

7. **Mount EC:** Attach bottom clevis to FP. Attach top clevis to IS cross-beam.
   Verify: EC extends 180 mm (rise height), lifting IS+OS from FP.
8. **Mount HC rack** to IS ceiling (M3 screws along IS side wall tops).
   3D-print motor bracket, mount motor+pinion to OS.
   Verify: motor drives OS 250 mm forward relative to IS.
9. **Test actuators individually:** Connect each to 12 V supply. Verify
   direction, speed, and full stroke.

### Phase C — Wheels & Drive (Day 4–5)

10. **3D-print motor brackets** (2 pcs) and wheel hub adaptors (2 pcs).
11. **Mount driven motors** to OS front (through brackets + M4 bolts).
12. **Mount rear casters** to OS bottom.
13. **Attach driven wheels.** Verify OS rolls freely on flat surface.
14. **Test wheel drive:** Connect motors to L298N. Verify forward, backward,
    left turn, right turn.

### Phase D — Electronics (Day 5–6)

15. **Wire motor drivers** per schematic (§5.4).
16. **Flash Arduino** with `firmware/manual_control/manual_control.ino`.
17. **Wire control buttons** (8 buttons + E-stop) to Arduino.
18. **Mount limit switches** on EC and HC end-of-travel positions.
19. **Strap battery to FP.** Wire power distribution (fuse + switch).
20. **Test all functions** individually: EC up/down, HC extend/retract,
    wheels forward/backward, steer left/right.

### Phase E — Integration Test (Day 7)

21. **Build a test step:** One step from scrap wood, 18 cm rise × 27 cm tread.
22. **Manual step-climb sequence:**
    a. Drive up to step edge (wheels forward).
    b. EC extend (Phase 2) — verify IS+OS lift together, FP stays on lower tread.
    c. HC extend (Phase 3) — verify OS slides forward, front wheels reach upper tread.
    d. EC retract (Phase 4a) — verify FP lifts toward IS (guide rails hold IS).
    e. HC retract (Phase 4b) — verify IS+EC+FP slide back into OS.
23. **Add 3 kg payload** (books on OS). Repeat step 22.
24. **Observe and record:**
    - Plywood flex (structural adequacy)
    - Guide rail smoothness (sliding friction)
    - Actuator speed under load vs simulation prediction
    - Stability during Phase 3 (any visible tipping tendency)
    - FP grip on step surface

---

## 7. 3D-Printed Parts List

Design in FreeCAD or Fusion 360. Print in PETG (stronger than PLA, heat-resistant).

| Part | Qty | Est. print time | Notes |
|------|-----|-----------------|-------|
| Front wheel motor bracket | 2 | 2 h each | Bolts through OS front wall |
| Wheel hub adaptor | 2 | 30 min each | 6 mm D-shaft to wheel bore |
| HC motor bracket | 1 | 2 h | Mounts motor+pinion to OS ceiling area |
| EC clevis bracket (top) | 1 | 1 h | Connects EC to IS cross-beam |
| EC clevis bracket (bottom) | 1 | 1 h | Connects EC to FP |
| Control box enclosure | 1 | 3 h | Houses Arduino + buttons |
| Cable guide / strain relief | 2 | 30 min each | Routes flex cable between FP and OS |
| **Total** | **10** | **~13 h** | ~100 g PETG |

---

## 8. Test Step Construction

Build a single test step from construction lumber or scrap plywood.

```
        ┌─────────────┐
        │  upper tread │ 27 cm deep
        │  (400mm wide)│
  18cm  │             ┌┘
  rise  │             │
        │ lower tread │ 50 cm deep (approach + landing)
        └─────────────┘
```

Materials:
- 2 × 18 mm plywood or OSB sheets, ~400 × 400 mm
- 2 × construction timber 45×90 mm, 400 mm long (risers)
- Wood screws

Cost: ~€15 from scrap/offcuts, or ~€25 new.

---

## 9. Firmware

Minimal Arduino sketch for manual 8-button control. No autonomous operation.

**Key safety features in firmware:**
- Limit switch check: stops actuator at end of travel
- IMU tilt check: cuts all motors if tilt > 15°
- Emergency stop: NC contact, cuts all motor outputs
- Differential steering: left/right buttons slow inner wheel for arc turns;
  without forward/backward, steer buttons pivot in place

Firmware file: `firmware/manual_control/manual_control.ino` (v0.2)

---

## 10. Risk Register

| Risk | Impact | Mitigation |
|------|--------|------------|
| Plywood too flexible under load | Mechanism binds | Add aluminium angle reinforcement to OS corners (~€10) |
| IS slides rough on guide rails | Phase 3/4 stall | Lubricate rails; check alignment; shim if needed |
| EC retracted length > IS height | Cannot assemble | EC mounts externally between FP and IS (see §3.1) |
| HC pinion skips on rack | Lost position | Add spring-loaded pressure on pinion; use steel rack (not plastic) |
| Wheel motors too weak on carpet | Can't position | Test on hard floor only; add weight to FP for traction |
| FP doesn't grip step surface | Slips during Phase 2 | Add higher-friction rubber; add rubber feet/bumps |
| Flex cable snags | Wire break during phase transitions | Route through cable guide with strain relief loop |
| Guide rails bind when loaded | Phase 4a fails | Check rail alignment carefully; ensure rails are parallel |

---

## 11. Success Criteria

**Minimum viable prototype (MVP):**
- [ ] Device climbs one 18/27 step under manual control, no payload
- [ ] Device climbs one 18/27 step with 3 kg payload
- [ ] Phase 3 stability: no tipping observed
- [ ] Phase 4a: FP successfully lifts into IS (guide rails hold)
- [ ] All phases complete in < 30 s total (manual control)

**Stretch goals:**
- [ ] Climb with 5 kg payload
- [ ] Semi-automated sequence (Arduino runs Phase 2→3→4a→4b on single button press)
- [ ] Climb 2 consecutive steps
- [ ] Measured EC force / speed vs simulation comparison
