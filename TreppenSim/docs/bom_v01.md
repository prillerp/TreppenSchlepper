# TreppenSchlepper — Bill of Materials v0.3

> **Config B** selected 2026-07-16: battery, MCU, and wheel motors located in
> FootPlate (not OuterShell). This keeps the OS light (9 kg structural only)
> and concentrates the heavy electronics in the FP, which is lifted only in
> Phase 4 (lighter payload for the dominant Phase 2 lift).
>
> Simulation basis: 2-D sim, 18/27 stair, 20 kg payload, `sim/params.py` defaults.
>
> **v0.3 corrections (2026-07-19):**
> - EC candidate replaced: LINAK LA12 is wrong (max stroke 130 mm < 180 mm required;
>   max speed 5–6 mm/s vs 30 mm/s minimum). New candidate: electric-linear-actuators.com
>   Mini Industrial A-series, 30 mm/s / 500 N / 180 mm stroke.
> - Battery energy corrected: 5 Ah × 24 V = 120 Wh (was incorrectly stated as 432 Wh).
>   Usable step count revised accordingly.
> - OS dimension clarified: H_OS = 140 mm (shell alone); total device height with EC
>   extended ≈ 500 mm.
> - Simulation values updated to current model (EC peak Ph2 = 390.8 N, total E = 104.7 J).
> - Phase 2 moving mass corrected to include IS (4 kg): 36.0 kg total.

---

## Actuators

| # | Part | Key Spec | Sim value | Candidate product | Notes |
|---|------|----------|-----------|-------------------|-------|
| 1 | **ElevatorCylinder (EC)** | Stroke 180 mm, Ph2 peak 389 N, Ph4 peak 191 N, min speed 30 mm/s | v_max=30 mm/s (speed-limited by controller; natural speed at 389 N ≈ 44 mm/s), a_max=100 mm/s², F_c=30 N | [TiMOTION TA2, 24 V, 180 mm stroke, code A (1000 N rated), no built-in feedback](https://www.timotion.com/en/products/linear-actuators/ta2-series) | ACME lead-screw, self-locking. **1000 N rated** → 611 N margin over 389 N peak. Natural speed ~44 mm/s at 389 N; PWM-limited to 30 mm/s. IP66D. Weight ~1.2 kg. Retracted length 285 mm (no feedback) — fits in ~320 mm device height with ~35 mm margin. Order without built-in feedback; use external AS5600 encoder (item 23). EU stock at LinearDirect.eu. ~~LINAK LA12 rejected~~: max stroke 130 mm, max speed 5–6 mm/s. ~~Mini Industrial A superseded~~: 500 N limit restricts max payload to 31 kg. |
| 2 | **HorizontalCylinder (HC)** | Stroke 250 mm, peak 49 N, speed 350 mm/s, mass ~1.5 kg | v_max=350 mm/s, a_max=1200 mm/s², F_c=5 N | Rack-and-pinion or toothed-belt linear drive (custom) | Standard rod actuators top out ~180 mm/s under load. HC body is rigidly attached to OS and lifted with it in Phase 2. Slower alternative (≤180 mm/s) accepted at cost of longer Phase 3. |

---

## Structural

| # | Part | Dimensions | Mass | Material (suggested) |
|---|------|-----------|------|----------------------|
| 3 | **OuterShell (OS)** | L=250 mm, W=400 mm, **H_OS=140 mm** (shell alone; total device height with EC extended ≈ 500 mm) | **9 kg** (structure only) | Welded aluminium box section; no onboard electronics |
| 4 | **SlidingInnerShell (IS)** | L=250 mm (= OS length), W=370 mm, H=80 mm | 4 kg | Aluminium profile, slides inside OS on low-friction guides |
| 5 | **FootPlate (FP)** | ~250 × 400 mm | **8 kg** (plate + battery + MCU + sensors) | Steel base plate with rubber anti-slip underside; housings for electronics bolted on top |

---

## Wheels & Drive

| # | Part | Spec | Qty | Location | Notes |
|---|------|------|-----|----------|-------|
| 6 | **Drive wheel** | Ø 70 mm, rubber tyre | 4 | Mounted on OS | Front axle 50 mm from OS front; rear axle 200 mm from OS front (50 mm from back) |
| 7 | **Wheel motor** | DC gear motor, 24 V, ~100 RPM | 4 | **Mounted on OS** | Differential steering via opposite rotation on same axle. Motors are on OS (move with it); power/signal cables must flex during Phase 3 horizontal travel. Estimated torque requirement: ~0.25 N·m per motor (F_total ≈ 0.1 × 29 kg × 9.81 = 28 N → 7 N/wheel × 35 mm radius). Pololu 25D at 100 RPM (~0.3–0.6 N·m) likely adequate — confirm with drive test. |

> **Wiring note:** wheel motors live on OS but battery/MCU live in FP. Flex cables
> or a small drag-chain must accommodate ~250 mm of horizontal OS travel in Phase 3
> and ~180 mm of vertical travel in Phase 2.

---

## Electronics & Power (all in FootPlate)

| # | Part | Spec | Notes |
|---|------|------|-------|
| 8 | **Battery** | 24 V LiFePO4, capacity TBD | One step cycle ≈ 105 J = 0.029 Wh. A **5 Ah pack = 120 Wh** → ~4 100 steps theoretical at 100% efficiency. Real usable capacity depends on staircase length, depth-of-discharge limit, and drivetrain efficiency (assume 60% → ~2 500 steps per charge). For a 20-step staircase that is ~125 round trips. |
| 9 | **Motor driver** | 4-channel DC driver, 24 V | Drives 4 wheel motors. Mounted in FP; output cables run to OS wheels. |
| 10 | **Actuator driver** | 2-channel linear actuator driver | Drives EC and HC. |
| 11 | **Main MCU** | Cortex-M or Raspberry Pi class | Path planning, sensor fusion, safety monitor. In FP. |
| 12 | **Bluetooth module** | BLE 5.x | Smartphone app + wrist-button command interface. |

---

## Sensors (planned)

| # | Part | Purpose | Accuracy target | Location |
|---|------|---------|-----------------|----------|
| 13 | **Distance / ToF sensor** | Stair geometry detection | ±2 mm within 1 m | OS front |
| 14 | **IMU (6-DOF)** | Tilt / orientation monitoring | <0.5° | FP (fixed to stair during climb) |
| 15 | **Load cell** | Payload overload detection | ±5% | OS (at payload interface) |
| 16 | **Battery monitor** | SoC + temperature | ±2% SoC | FP |
| 17 | **Wheel encoders** | Speed feedback, slip detection | Quadrature, >100 CPR | OS (at each wheel motor) |
| 18 | **EC position sensor** | EC stroke feedback | ±1 mm | EC body |
| 19 | **HC position sensor** | HC stroke feedback | ±1 mm | HC body |

---

## Summary of Simulation-Derived Specs (Config B, 18/27 stair, 20 kg payload)

| Parameter | Value |
|-----------|-------|
| Ph2 moving mass (IS + OS + payload + upper EC + HC) | 36.0 kg |
| Ph4 moving mass (IS + FP + lower EC) | 13.5 kg |
| EC peak force Phase 2 | **389 N** |
| HC peak force Phase 3 | 48.6 N |
| HC energy Phase 3 | 2.8 J |
| EC peak force Phase 4 | **167 N** |
| **Total energy per step** | **102.0 J** |
| **Total time per step** (Ph2 30 mm/s, Ph4 44 mm/s) | **11.84 s** |
| Phase 3 min stability margin | +9.3 cm (stable throughout) |
| Phase 3 wheel contact time | 0.29 s after start |
| **Max safe payload (1000 N TA2)** | **~82 kg** (984 N at 80 kg ✓; 1083 N at 90 kg ✗) |

> **EC speed:** `sim/params.py` updated to v_max = 0.030 m/s. All sim values above are at
> the realistic 30 mm/s spec of the Mini Industrial A candidate.

---

## Config A vs Config B Decision

| Criterion | Config A (OS-heavy) | Config B (FP-heavy) | Winner |
|-----------|--------------------|--------------------|--------|
| Total energy per step | 104.7 J | 104.7 J | Tie |
| EC force Ph2 (dominant phase) | 411 N | **391 N** | **B** |
| EC force Ph4 | 130 N | 193 N | A |
| EC size required | Sized for 411 N | Sized for **391 N** | **B** |
| Phase 3 stability margin | ~8.3 cm | **9.0 cm** | **B** |
| Wiring complexity | Simple (all on OS) | Flex cables needed | A |

**Decision: Config B.** Smaller and cheaper EC, better stability margin. Wiring
flex cables are a known engineering problem with standard solutions.

---

## Cost Estimate — Lot Size 1 (Single Prototype)

> Prices are indicative retail/distributor prices in EUR as of mid-2026.
> Items marked **[ASSUMED]** have no confirmed specification yet.
> Target total device cost: **< €2 000**.

### Actuators

| # | Part | Candidate | Unit price | Qty | Line total | Notes |
|---|------|-----------|-----------|-----|-----------|-------|
| 1 | ElevatorCylinder (EC) | TiMOTION TA2, 24 V, 180 mm stroke, code A (1000 N rated), no built-in feedback | €150 | 1 | **€150** | **[ASSUMED]** EU stock at LinearDirect.eu or direct from TiMOTION Europe. Request quote confirming: 24 V, 180 mm stroke, code A, no feedback, clevis both ends. IP66D. Weight ~1.2 kg. **1000 N rating → max payload ~82 kg** (person transport enabled). ~~Mini Industrial A superseded~~: 500 N limited max payload to 31 kg. ~~LINAK LA12 rejected~~. |
| 2 | HorizontalCylinder (HC) drive | Rack-and-pinion kit + DC motor + gearbox | €120 | 1 | **€120** | **[ASSUMED]** No confirmed product yet. Estimate: 25 cm aluminium rack (~€20) + pinion + 24 V DC motor with gearbox (~€60) + mounting hardware (~€40). |

### Structural

| # | Part | Supplier type | Unit price | Qty | Line total | Notes |
|---|------|--------------|-----------|-----|-----------|-------|
| 3 | OuterShell (OS) | Custom fab (aluminium box section, welded) | €350 | 1 | **€350** | **[ASSUMED]** Prototype one-off fabrication at local metalwork shop. Includes material (6061-T6 aluminium sheet) and welding labour. Could be reduced with laser-cut + bent sheet design. |
| 4 | SlidingInnerShell (IS) | Aluminium extrusion + machining | €150 | 1 | **€150** | **[ASSUMED]** Standard 80/20-style extrusion cut to 250 mm, plus sliding guide rails (IGUS or similar). |
| 5 | FootPlate (FP) | Steel plate + rubber sheet | €40 | 1 | **€40** | 6 mm steel plate 250×400 mm (~€15 material) + anti-slip rubber sheet + laser cutting. |

### Wheels & Drive

| # | Part | Candidate | Unit price | Qty | Line total | Notes |
|---|------|-----------|-----------|-----|-----------|-------|
| 6 | Drive wheel (Ø 70 mm) | Pololu 70×8 mm or similar rubber wheel | €8 | 4 | **€32** | Standard hobby/robotics wheel. |
| 7 | Wheel motor | Pololu 25D metal gearmotor, 24 V, ~100 RPM | €35 | 4 | **€140** | **[ASSUMED]** Torque requirement estimated at ~0.25 N·m per motor — within 25D spec. Confirm with drive test. |
| 8 | Wheel axle / mounting hardware | Pololu motor bracket + shaft collar | €8 | 4 | **€32** | |

### Electronics & Power

| # | Part | Candidate | Unit price | Qty | Line total | Notes |
|---|------|-----------|-----------|-----|-----------|-------|
| 9 | Battery | 24 V / 5 Ah LiFePO4 pack | €90 | 1 | **€90** | **[ASSUMED]** 5 Ah × 24 V = **120 Wh**; one step ≈ 0.029 Wh → ~4 100 steps theoretical (assume ~2 500 usable at 60% efficiency). Increase to 10 Ah for longer staircases. |
| 10 | Motor driver | Cytron MDD10A (2×10 A dual channel) × 2 | €30 | 2 | **€60** | Two boards for 4 motors (each board drives 2 motors). |
| 11 | Actuator driver | IBT-2 H-bridge 43 A or similar, × 2 | €12 | 2 | **€24** | One per actuator (EC, HC). |
| 12 | Main MCU | Raspberry Pi 4 (2 GB) | €55 | 1 | **€55** | **[ASSUMED]** RPi gives Linux + Python for rapid prototyping. Could be replaced with STM32 board for production. |
| 13 | Bluetooth module | HC-05 or integrated in RPi | €5 | 1 | **€5** | RPi 4 has onboard BT; separate module only if MCU is swapped. |
| 14 | Flex cable / drag-chain | IGUS micro energy chain + 6-core flex cable | €35 | 1 | **€35** | **[ASSUMED]** To carry power + signal from FP to OS across 250 mm horizontal + 180 mm vertical travel. |
| 15 | Wiring, connectors, PCB | — | €40 | 1 | **€40** | **[ASSUMED]** Prototype wiring loom, JST connectors, prototype PCB. |
| 16 | Power supply (bench, development only) | 24 V / 5 A bench PSU | €40 | 1 | **€40** | Development/test use; not part of deployed device. |

### Sensors

| # | Part | Candidate | Unit price | Qty | Line total | Notes |
|---|------|-----------|-----------|-----|-----------|-------|
| 17 | Distance / ToF sensor | VL53L1X (ST) breakout board | €12 | 2 | **€24** | Two units for redundancy / wider FOV. ±4 mm to 4 m range. |
| 18 | IMU (6-DOF) | MPU-6050 breakout | €6 | 1 | **€6** | Mounted in FP. |
| 19 | Load cell + amplifier | 50 kg load cell + HX711 | €10 | 1 | **€10** | **[ASSUMED]** Single-point load cell at payload interface. |
| 20 | Battery monitor | INA226 breakout (voltage + current) | €5 | 1 | **€5** | |
| 21 | Wheel encoders | Magnetic encoder integrated in Pololu motors | €0 | 4 | **€0** | Included with motor selection above. |
| 22 | EC position sensor | Built-in potentiometer or Hall sensor (order with EC) | €0 | 1 | **€0** | Confirm feedback option when ordering from electric-linear-actuators.com. |
| 23 | HC position sensor | Magnetic linear encoder (e.g. AS5600 + strip) | €8 | 1 | **€8** | **[ASSUMED]** 12-bit magnetic encoder on HC rack. |

### Fasteners, Misc.

| # | Part | Unit price | Qty | Line total | Notes |
|---|------|-----------|-----|-----------|-------|
| 24 | M3/M4/M5 fastener assortment | €15 | 1 | **€15** | |
| 25 | IGUS iglide sliding guides (IS in OS) | €20 | 1 | **€20** | **[ASSUMED]** Low-friction polymer guide pads for IS sliding in OS. |
| 26 | Miscellaneous (adhesive, paint, cable ties…) | €20 | 1 | **€20** | |

---

### Cost Summary

| Category | Subtotal |
|----------|---------|
| Actuators | €270 |
| Structural | €540 |
| Wheels & Drive | €204 |
| Electronics & Power (excl. bench PSU) | €309 |
| Sensors | €53 |
| Fasteners & Misc. | €55 |
| **Total (prototype, excl. bench PSU)** | **€1 431** |
| Budget headroom to €2 000 target | **€569** |

> The single largest cost driver is the **OuterShell fabrication (€350)**. A laser-cut
> and folded sheet-metal design (instead of welded box section) could reduce this to
> ~€150–200 at prototype quantities.
>
> EC upgraded from Mini Industrial A (~€50) to TiMOTION TA2 (~€150): +€100 cost,
> but max payload increases from 31 kg to **~82 kg**, enabling person transport.
> ~~LINAK LA12 rejected~~ (€180, wrong specs). ~~Mini Industrial A superseded~~ (€50, 500 N limit).
