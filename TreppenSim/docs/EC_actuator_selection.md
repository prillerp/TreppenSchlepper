I need an actuator for linear movements, stroke around 180mm, speed min 30mm/s, force max 700 N. Could be electric linear motor, or hydraulic, but needs to be light (less weight) and needs to be mounted on a mobile platform, thus max. 24VDC power supply. Please provide a table with at least 5 suggested makes, together with their main specs and price (lot size 1)

Copilot, 2026-07-20:
# Linear Actuator Recommendations (24 VDC Mobile Platform)

## Requirements

- Stroke: ~180 mm (200 mm standard stroke acceptable)
- Speed: ≥ 30 mm/s
- Force: up to 700 N
- Power supply: 24 VDC maximum
- Low weight preferred for mobile platform installation

## Technology Recommendation

For a mobile 24 VDC platform, an **electromechanical linear actuator** is generally preferable to a hydraulic solution. Hydraulic systems require additional components such as a pump, reservoir, valves, and hoses, significantly increasing overall system mass and complexity.

---

## Recommended Actuators

| Manufacturer | Series / Model | Voltage | Stroke (Suitable Option) | Max Force | Speed | Weight | Approx. Price (Qty 1) | Comments |
|-------------|----------------|----------|-------------------------|-----------|--------|--------|----------------------|----------|
| TiMOTION | TA2 Series | 24 VDC | 180–200 mm configurable | 750 N | up to 51 mm/s | ~1.2 kg | €120–180 | Compact, IP66, good OEM choice |
| Progressive Automations | PA-04 | 24 VDC | 203 mm (8 in) | 445–1780 N versions | High-speed versions >30 mm/s | ~2 kg | US$157–200 | IP66, readily available |
| FIRGELLI | Premium / Classic Rod | 24 VDC option | 203 mm (8 in) | 667 N (150 lb) | ~7.6 mm/s (standard version) | ~1.5 kg | US$130–155 | Lightweight, but standard speed below target |
| Thomson | Electrak HD 24-B017 | 24 VDC | 200 mm configurable | 1700 N | 58 mm/s under load | ~3–4 kg | €600–900 | Industrial-grade, robust, over-specified for 700 N |
| TiMOTION | TA2 Fast Version (F/G/K gearing) | 24 VDC | 200 mm | 750 N | 33–51 mm/s | ~1.2 kg | €150–220 | Excellent balance of weight, speed and force |
| Generic Industrial Actuator | 24 V / 750 N / 200 mm | 24 VDC | 200 mm | 750 N | Typically 30–50 mm/s | 1.2–1.5 kg | US$65–110 | Lowest cost, limited documentation |

---

## Best Matches for the Requirements

### 1. TiMOTION TA2

**Why:**

- Closest overall fit to the requirements
- Lightweight (~1.2 kg)
- 24 VDC operation
- Configurable stroke lengths
- Available in versions providing approximately 750 N and 33–51 mm/s
- Suitable for compact mobile equipment

### 2. Progressive Automations PA-04 High-Speed

**Why:**

- Good availability
- Competitive pricing
- IP66 environmental protection
- Well suited for mobile and industrial applications

### 3. Thomson Electrak HD24-B017

**Why:**

- Premium industrial solution
- Excellent environmental resistance
- High reliability and long service life
- Heavier and more expensive than required for a 700 N application

---

## Power Requirement Estimate

Given:

- Force = 700 N
- Speed = 30 mm/s = 0.03 m/s

Mechanical power:

**P = F × v = 700 × 0.03 = 21 W**

Assuming approximately 70% actuator efficiency:

**Electrical input power ≈ 30 W**

At 24 VDC:

**Current ≈ 1.3 A**

Therefore, all recommended actuators can be powered comfortably from a typical 24 V battery-based mobile platform.

---

## Final Recommendation

### Preferred Choice: TiMOTION TA2

The TiMOTION TA2 is the strongest candidate because it provides the best balance of:

- Low weight
- Compact dimensions
- 24 VDC operation
- Adequate force (~750 N)
- Sufficient speed (33–51 mm/s)
- Flexible stroke configurations around 180–200 mm

### Alternatives

1. Progressive Automations PA-04 High-Speed
2. Thomson Electrak HD24-B017 (for harsh environments and premium durability)

---

## TreppenSchlepper ElevatorCylinder Analysis — Claude Code, 2026-07-20

### EC Requirements (from simulation)

| Parameter | Requirement | Source |
|-----------|-------------|--------|
| Stroke | exactly 180 mm | rise height of 18/27 stair |
| Min speed under load | 30 mm/s | hardware candidate spec |
| Peak force (Ph2, 20 kg payload) | 389 N | `sweep_payload.py` |
| Rated force (safety margin) | ≥ 500 N | 1.28× over peak at design point |
| Voltage | 24 V DC | mobile platform battery |
| Self-locking | required | must hold load without power |
| Position feedback | preferred | stroke control |

### Candidate Comparison

| | LINAK LA12 | Mini Industrial A | **TiMOTION TA2** |
|---|---|---|---|
| Status | **❌ Rejected** | Current BOM | **⬆ Recommended upgrade** |
| Max rated force | 750 N | 500 N | **750–1000 N** (speed-code dependent) |
| Max safe payload (EC limit) | — | ~31 kg | **~56 kg (750 N) / ~82 kg (1000 N)** |
| Speed at ~389 N load | 5–6 mm/s ❌ | 30 mm/s ✓ | **~44 mm/s ✓** (1000 N code A); 33–51 mm/s (fast codes) |
| Stroke range | max 130 mm ❌ | custom ✓ | 20–1000 mm ✓ |
| Voltage | 24 V ✓ | 24 V ✓ | 12/24/36/48 V ✓ |
| Self-locking | lead screw ✓ | lead screw ✓ | ACME screw ✓ |
| IP rating | IP54 | unknown | **IP66D ✓** |
| Position feedback | optional | "confirm when ordering" | **POT / Reed / Hall ✓** |
| Retracted length (180 mm stroke) | — | ~120 mm body | **285 mm (no FB) / 315 mm (with FB)** |
| Weight | — | unknown | **~1.2 kg** |
| EU availability | EU stock | ships from HK (3–7 d) | **EU stock (LinearDirect.eu)** |
| Price (lot 1, est.) | €180 | ~€50 [ASSUMED] | **~€120–180 [ASSUMED]** |
| Certification | — | none stated | **IEC60601-1, EMC** |

### Why TA2 is the Better Choice

**Force margin / payload capacity is the decisive factor.** The project goal explicitly includes *"eventually persons"*. A person transport load of 60–80 kg exceeds the Mini Industrial A's 500 N limit at 31 kg payload. The TA2:
- At 750 N (fast speed codes): max payload ≈ **56 kg** — useful cargo range
- At 1000 N (slow code A): max payload ≈ **82 kg** — enables person transport

At 30 mm/s (speed-limited by controller), simulation results are unchanged. The TA2 naturally runs at ~44 mm/s at 389 N (code A), so a PWM controller limits it to 30 mm/s for predictable motion.

Additional confirmed advantages over Mini Industrial A: IP66D (vs. unknown), feedback (confirmed vs. "contact vendor"), EU stock (vs. HK shipping), certified quality (IEC60601-1 vs. none).

### Geometric Constraint — Retracted Length

> ⚠ **Verify before ordering with feedback option.**
>
> EC retracted length = stroke + 105 mm (no feedback) = **285 mm**
> EC retracted length = stroke + 135 mm (with Hall/POT) = **315 mm**
>
> Device retracted height (EC at bottom) ≈ 320 mm (= 500 mm − 180 mm stroke).
> No-feedback variant (285 mm) fits with ~35 mm margin. With-feedback variant (315 mm) leaves only ~5 mm — likely too tight once mounting brackets are added. **Order the no-feedback variant and use an external Hall/encoder strip for position sensing** (e.g. the AS5600 magnetic encoder already in the sensor BOM).

### Recommended Order Specification

- **Model:** TiMOTION TA2, 24 V DC, code A (slow/high-force, 1000 N rated)
- **Stroke:** 180 mm
- **Feedback:** none built-in (use external sensor)
- **Voltage:** 24 V DC
- **Mounting:** clevis both ends
- **Contact:** TiMOTION Europe (timotion.com/en/products) or LinearDirect.eu (timotion specialist since 2006)
- **Action needed:** Request quote; confirm retracted body length for 180 mm stroke without feedback.
