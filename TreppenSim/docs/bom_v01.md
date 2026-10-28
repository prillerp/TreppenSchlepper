# TreppenSchlepper — Bill of Materials v1.0

> **Config B, 12 V system, plywood PoC prototype**
>
> Simulation basis: 2-D sim, 18/27 stair, **3 kg PoC payload**, `sim/params.py` defaults.
>
> Target budget: **< €500** (single-unit prototype)
>
> All prices are indicative retail prices (AliExpress / Amazon EU / HobbyKing)
> as of 2026-10. Prices include shipping where noted; VAT may apply.
>
> **Key design decisions for PoC:**
> - **12 V system** (was 24 V) — simpler battery, cheaper actuators, safer for prototype
> - **Plywood structure** (was aluminium) — standard tools, no metalwork shop needed
> - **2 driven front wheels** (was 4) — simpler wiring, sufficient for flat-surface positioning
> - **EC actuator 300 N rated** (was 1000 N TA2) — right-sized for 3 kg PoC (171 N peak)
> - **DIY rack-and-pinion HC** — no off-the-shelf actuator does 250 mm at 100 mm/s cheaply

---

## 1. Actuators

| # | Part | Spec | Candidate | Price | Qty | Total | Notes |
|---|------|------|-----------|-------|-----|-------|-------|
| 1 | **ElevatorCylinder (EC)** | 12 V, 200 mm stroke, 300 N, 35 mm/s | AliExpress generic lead-screw actuator ([example](https://www.aliexpress.com/item/32809655815.html)) | €25 | 1 | **€25** | Lead-screw = self-locking (holds load without power). 200 mm stroke gives 20 mm margin over 180 mm rise. Peak force at 3 kg = 171 N → 43% margin. Max payload ~16 kg. Swap for stronger actuator for heavy loads. |
| 2 | **HC motor** | 12 V, ~130 RPM, encoder, metal gearbox | JGA25-370 gear motor with Hall encoder ([AliExpress](https://www.aliexpress.us/item/3256805466278047.html)) | €9 | 1 | **€9** | 130 RPM × M1/20T pinion (∅20 mm) = 136 mm/s no-load. Under 12.5 N load: ~100 mm/s. 6 mm D-shaft. |
| 3 | **HC rack** | Module 1, steel, 250 mm | M1 steel gear rack, 10×10 mm ([AliExpress](https://www.aliexpress.us/w/wholesale-rack-pinion-gear.html)) | €8 | 1 | **€8** | 45# carbon steel. Cut from 500 mm if needed. Mount to IS ceiling with M3 screws. |
| 4 | **HC pinion** | Module 1, 20 teeth, 6 mm bore | M1 spur gear 20T ([AliExpress](https://www.aliexpress.com/w/wholesale-gear-and-pinion.html)) | €3 | 1 | **€3** | Press-fit or grub screw on motor shaft. PD = 20 mm. |

**Actuators subtotal: €45**

---

## 2. Guide Rails

| # | Part | Spec | Candidate | Price | Qty | Total | Notes |
|---|------|------|-----------|-------|-----|-------|-------|
| 5 | **Telescoping drawer slides** | 250 mm, full extension, ball bearing, ≥30 kg pair | Standard furniture drawer slides ([Amazon](https://www.amazon.com/telescoping-drawer-slides/s?k=telescoping+drawer+slides)) | €10 | 1 pair | **€10** | Carry IS z-load during Phase 4a (~30 N). Mount between IS and OS side walls. |

---

## 3. Wheels & Drive

| # | Part | Spec | Candidate | Price | Qty | Total | Notes |
|---|------|------|-----------|-------|-----|-------|-------|
| 6 | **Driven wheel** | ∅70 mm, rubber, 6 mm bore | Robot wheel 70×20 mm ([AliExpress](https://www.aliexpress.com/w/wholesale-wheels-for-robot.html)) | €3 | 2 | **€6** | Front axle, 50 mm from OS front face. |
| 7 | **Passive wheel (caster)** | ∅70 mm or similar swivel caster | Small swivel caster | €4 | 2 | **€8** | Rear position. Free-spinning, allow steering. |
| 8 | **Wheel motor (driven)** | 12 V, 60 RPM, encoder, metal gearbox | JGA25-370 gear motor with Hall encoder ([AliExpress](https://www.aliexpress.us/item/3256805324414758.html)) | €9 | 2 | **€18** | 60 RPM × ∅70 mm wheel = 220 mm/s ≈ 0.8 km/h. Torque: ~0.5 N·m (>> 0.12 N·m needed). Encoder for closed-loop speed control. |
| 9 | **Motor-to-wheel coupling** | 6 mm bore, hub adapter | Wheel hub + grub screw | €2 | 2 | **€4** | 3D-printed or aluminium hex hub. |

**Wheels & Drive subtotal: €36**

---

## 4. Electronics & Power

| # | Part | Spec | Candidate | Price | Qty | Total | Notes |
|---|------|------|-----------|-------|-----|-------|-------|
| 10 | **Main MCU** | ATmega2560, 54 I/O, 16 analog | Arduino Mega 2560 R3 clone (CH340) ([Amazon](https://www.amazon.com/arduino-mega-2560-r3/s?k=arduino+mega+2560+r3)) | €18 | 1 | **€18** | Sufficient I/O for all motors, sensors, encoders. Manual-button control for PoC; upgrade to Raspberry Pi for autonomous operation later. |
| 11 | **EC motor driver** | H-bridge, 12 V, ≥10 A | BTS7960 43A module ([AliExpress](https://www.aliexpress.us/w/wholesale-bts7960-43a-motor-driver.html)) | €2 | 1 | **€2** | PWM speed control + direction. EC motor draws ~3 A at 171 N load. |
| 12 | **HC motor driver** | H-bridge, 12 V, ≥5 A | BTS7960 43A module | €2 | 1 | **€2** | Same module type as EC driver. |
| 13 | **Wheel motor driver** | Dual H-bridge, 12 V, ≥2 A/ch | L298N module ([AliExpress](https://www.aliexpress.com/w/wholesale-l298n.html)) | €3 | 1 | **€3** | Drives both wheel motors (dual channel). PWM speed + direction per wheel for differential steering. |
| 14 | **Battery** | 3S 11.1 V LiPo, 5000 mAh, ≥25 C | Turnigy Rapid 5000 mAh 3S ([HobbyKing](https://hobbyking.com/batteries-chargers/batteries/3s-lipo-batteries.html)) | €28 | 1 | **€28** | 55 Wh capacity. One step ≈ 51.5 J ≈ 0.014 Wh → ~3 900 steps theoretical. At 60% efficiency → ~2 300 steps. Weight ~380 g. XT60 connector. |
| 15 | **LiPo charger** | Balance charger, 2S–3S | B3 Pro compact charger | €12 | 1 | **€12** | Plugs into mains. Charges 3S in ~2 h. |
| 16 | **Power distribution** | Fuse + switch + XT60 | Inline fuse holder + toggle switch | €5 | 1 | **€5** | 15 A fuse for short-circuit protection. |
| 17 | **Wiring & connectors** | Silicone wire 14/22 AWG, JST, XT60 | Assorted kit | €12 | 1 | **€12** | 14 AWG for power, 22 AWG for signal. |
| 18 | **Flex cable (FP↔OS)** | Multi-core flex, ≥6 conductors | Ribbon cable or flex harness | €5 | 1 | **€5** | Must accommodate 250 mm horizontal + 180 mm vertical travel. Loop with strain relief. |

**Electronics & Power subtotal: €87**

---

## 5. Sensors

| # | Part | Spec | Candidate | Price | Qty | Total | Notes |
|---|------|------|-----------|-------|-----|-------|-------|
| 19 | **ToF distance sensor** | Range 50 mm–1.2 m, I²C | VL53L0X breakout ([AliExpress](https://www.aliexpress.us/w/wholesale-vl53l0x.html)) | €1.50 | 2 | **€3** | Front-facing on OS. Stair edge detection + positioning. |
| 20 | **IMU (6-DOF)** | Accel + gyro, I²C | MPU-6050 GY-521 breakout | €1.50 | 1 | **€1.50** | Mounted on FP. Tilt/orientation monitoring. |
| 21 | **Load cell + amplifier** | 20 kg, 24-bit ADC | HX711 + 20 kg load cell kit ([AliExpress](https://www.aliexpress.us/item/2255800297354620.html)) | €3 | 1 | **€3** | Payload overload detection. Mount between OS and payload platform. |
| 22 | **EC position sensor** | 12-bit magnetic rotary encoder | AS5600 module + diametric magnet | €2.50 | 1 | **€2.50** | Mount magnet on EC lead screw or motor shaft. I²C. ±0.1° = sub-mm stroke resolution. |
| 23 | **Battery monitor** | Voltage + current, I²C | INA226 breakout | €2 | 1 | **€2** | SoC estimation. Mount inline with battery. |

**Sensors subtotal: €12**

---

## 6. Structure (Plywood Prototype)

| # | Part | Spec | Candidate | Price | Qty | Total | Notes |
|---|------|------|-----------|-------|-----|-------|-------|
| 24 | **Plywood sheet (OS + IS)** | 12 mm birch plywood, ~600×400 mm | Hardware store | €12 | 1 | **€12** | Cut to size for OS box (250×250×140 mm) and IS tray (250×230×80 mm). |
| 25 | **Plywood sheet (FP)** | 6 mm plywood, ~300×250 mm | Hardware store | €5 | 1 | **€5** | FootPlate base. Add rubber sheet on bottom for grip. |
| 26 | **Rubber anti-slip sheet** | 2 mm, ~300×250 mm | Hardware store | €4 | 1 | **€4** | Glue to FP underside. Prevents slip on stair tread. |
| 27 | **3D printed parts** | Motor mounts, wheel hubs, HC bracket, sensor mounts | PLA/PETG filament (~100 g) | €5 | 1 | **€5** | Design parametrically; print on FDM printer. |
| 28 | **Wood screws + fasteners** | M3/M4 assortment + wood screws | Assorted kit | €10 | 1 | **€10** | |
| 29 | **Wood glue + misc** | PVA glue, sandpaper, paint/varnish | Hardware store | €5 | 1 | **€5** | |

**Structure subtotal: €41**

---

## Cost Summary

| Category | Subtotal |
|----------|---------|
| Actuators (EC + HC mechanism) | €45 |
| Guide rails | €10 |
| Wheels & drive | €36 |
| Electronics & power | €87 |
| Sensors | €12 |
| Structure (plywood) | €41 |
| **Total (PoC prototype)** | **€231** |
| **Budget headroom to €500** | **€269** |

> **€231 total** — well under the €500 target. The headroom covers:
> - Shipping costs from multiple suppliers (~€20–40)
> - Unexpected replacements or upgrades (~€30)
> - Tools or consumables not listed (~€20)
> - Optional upgrades (stronger EC for heavier loads, Raspberry Pi for autonomy)

---

## Sourcing Strategy

| Source | Items | Lead time | Notes |
|--------|-------|-----------|-------|
| **AliExpress** | EC actuator, HC motor+rack+pinion, sensors, motor drivers, wheels | 2–4 weeks | Cheapest. Order early. Check seller ratings (>95%). |
| **Amazon EU** | Arduino Mega, L298N, drawer slides, fasteners | 1–3 days | Fast delivery. Slightly higher prices. |
| **HobbyKing** | LiPo battery | 1–2 weeks | EU warehouse for faster shipping. |
| **Local hardware store** | Plywood, rubber sheet, wood screws, glue, sandpaper | Same day | |
| **3D print service / own printer** | Motor mounts, brackets, wheel hubs | 1–3 days | PLA or PETG. |

---

## Upgrade Path (beyond PoC)

| Upgrade | What changes | Added cost | Enables |
|---------|-------------|-----------|---------|
| **Heavier payload** | Replace EC actuator with 750 N or 1000 N model | +€25–125 | 30–80 kg cargo |
| **Autonomous operation** | Add Raspberry Pi 4 + camera | +€60–80 | Path planning, stair detection |
| **Aluminium structure** | Replace plywood OS/IS/FP with sheet aluminium | +€150–300 | Durability, weather resistance |
| **24 V system** | Replace battery + actuator + drivers | +€50–100 | Higher efficiency, faster motors |

---

## Simulation-Derived Specs (Config B, 18/27 stair, 3 kg PoC payload)

| Parameter | Value |
|-----------|-------|
| Ph2 moving mass (IS + OS + payload + upper EC + HC) | 14.0 kg |
| Ph3 moving mass (OS + payload + HC) | 9.5 kg |
| Ph4a moving mass (FP + lower EC) | 6.5 kg |
| Ph4b moving mass (IS + EC + FP) | 11.0 kg |
| EC peak force Phase 2 | **171 N** (57% of 300 N rated) |
| HC peak force Phase 3 | 11.8 N |
| EC peak force Phase 4a | **98 N** |
| HC peak force Phase 4b | 12.5 N |
| **Total energy per step** | **51.5 J** |
| **Total time per step** | **16.2 s** |
| Phase 3 min stability margin | +10.1 cm (stable) |
| Phase 3 wheel contact time | 0.60 s after start |
| EC actuator max payload | ~16 kg (at 300 N rated) |
