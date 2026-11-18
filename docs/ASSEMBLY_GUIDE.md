# LepiLED DIY Maxi Switch — Practical Assembly & Bring-Up Guide

This guide walks step-by-step through fabricating, soldering, bench-testing, and mechanically assembling the **LepiLED DIY Maxi Switch** (`8-ALL` / `OFF` / `4-UV` fanless moth lamp). Follow the sequence below carefully — **do not seal the electronics cavity before completing the 4-stage electrical bench bring-up.**

---

## Safety Warnings (Read First)

> **⚠️ 365 nm UV-A EYE & SKIN HAZARD (`Luminus_SST-10-UV_Datasheet.pdf` p. 14):**  
> `D1..D4` (`4× Luminus SST-10-UV-A130-G365-00`) emit ~2.5 W of intense `365–375 nm` UV-A radiation that appears dim to the human eye while causing acute corneal/retinal and skin injury. **Always wear certified EN 166 / EN 170 UV-blocking eyewear (`< 400 nm` cutoff)** whenever powering the LED strips during bench testing, shield exposed skin, and operate the finished lamp only with the borosilicate glass cylinder (`MECH-TUBE-1`) installed.

> **⚠️ ENCLOSED MOTH-TRAP VENTILATION (`thermal_summary.json`):**  
> Passive thermal verification assumes open-air natural convection up to `30 °C` ambient. Inside an unventilated, heat-trapping moth-trap funnel box exceeding `31 °C` internal air temperature, add trap ventilation if running worst-case `DS-100%` fault margins (`Nominal` operation holds cleanly up to `~40 °C`).

---

## 1. Al MCPCB LED Strip Assembly (`4× MECH-MCPCB-1..4`)

Each of the 4 aluminum strips (`20.0 × 80.0 × 1.6 mm`, `1.0 W/m·K` dielectric, `1 oz` `F.Cu` only) mounts one UV LED (`D_UV` at `y = +18.0 mm`) and one Visible LED (`D_VIS` at `y = -18.0 mm`):
- **Strips #1 & #2:** `D_UV` (`SST-10-UV-A130-G365-00`) + Royal Blue `D_VIS` (`Cree XPEBRY`, e.g., `00R02`)
- **Strip #3:** `D_UV` + Green `D_VIS` (`Cree XPEBGR`, e.g., `00F01`)
- **Strip #4:** `D_UV` + Cool White `D_VIS` (`Cree XPEBWT`, e.g., `00FE1`)

### ⚠️ CRITICAL POLARITY CALLOUT — OPPOSITE BOTTOM NOTCHES!
**Do NOT orient `SST-10-UV` and `XP-E2` the same way by their bottom thermal-pad notch!** Their package footprints have **opposite** polarity conventions (`pcb_design/led_mcpcb/build_led_mcpcb.py`, `datasheets/Luminus_SST-10-UV_Datasheet.pdf` p. 10, `datasheets/XLamp-XPE2.pdf` p. 38):
- **`D_UV` (`SST-10-UV-A130-G365-00`, upper pad):** Anode Left (`X = -1.385`), Cathode Right (`X = +1.385`), isolated center thermal pad (`1.30 × 3.25 mm`). The bottom thermal-pad notch faces **CATHODE (`+X` / `K-`)** — silkscreen reads `A+`, `K-`, Pin-1 dot, and **`BTM NOTCH=K`**.
- **`D_VIS` (`Cree XP-E2`, lower pad):** Anode Left (`X = -1.40`), Cathode Right (`X = +1.40`), isolated center thermal pad (`1.30 × 3.30 mm`). The bottom thermal-pad notch faces **ANODE (`-X` / `A+`)** — silkscreen reads `A+`, `K-`, Pin-1 dot, and **`BTM NOTCH=A`**.

### Reflow & Series Harness Procedure
1. **ESD & Handling:** Wear a grounded ESD wrist strap (`SST-10-UV` is `6000 V` HBM Class 2). Pick emitters by their ceramic substrate edges with plastic/reverse-action tweezers — **never touch or squeeze the silicone/quartz primary optic domes**.
2. **Hotplate Preheat & Reflow:** `1.6 mm` aluminum sinks heat rapidly; a regular soldering iron cannot wet the center thermal pad. Apply thin SAC305 solder paste (via stencil or fine syringe), place LEDs matching `A+`/`K-` and `BTM NOTCH=K` / `BTM NOTCH=A`, preheat the Al strip on a PCB hotplate to `~150–170 °C`, then ramp to `~240–245 °C` (or assist briefly with hot air) until each LED self-centers cleanly without bridging the `~0.22 mm` under-package solder-bridge gap (`0.495 mm` `D_UV` / `0.500 mm` `D_VIS` copper pad-to-thermal-pad gap on `led_mcpcb`).
3. **Strip Continuity & Isolation Test:** Using a multimeter in diode mode (or a current-limited `10 mA` bench PSU), verify each LED illuminates faintly (`~2.4–3.2 V`) with correct polarity and check **infinite resistance (`> 10 MΩ`)** from every solder pad to the bare aluminum backplate/edges.
4. **4-Strip Series Wiring:** Solder `22 AWG` silicone-insulated wire (`≥ 105 °C`) to the `y = -26.0 mm` pads (left-to-right: `UV+`, `VIS+`, `VIS-`, `UV-`) to form two independent 4-LED series loops:
   - **Ch1 UV loop (`J2`):** `J2.1 (VOUT1)` → `Strip1 UV+` → `Strip1 UV-` → `Strip2 UV+` → ... → `Strip4 UV-` → `J2.2 (UV_RET)`
   - **Ch2 Vis loop (`J3`):** `J3.1 (VOUT2)` → `Strip1 VIS+` → `Strip1 VIS-` → `Strip2 VIS+` → ... → `Strip4 VIS-` → `J3.2 (VIS_RET)`
   - Leave ~`120–150 mm` service slack to reach the bottom PCB cavity via the `4×` `6.0 × 3.5 mm` wire exit channels built into `MECH-CAP-BOT`'s core socket (`±X / ±Y`), terminating in `JST XHP-2` housings (or verify exact polarity against `driver_pcb` `B.Silkscreen` `"2:UV-  1:UV+"` and `"2:VIS-  1:VIS+"`).

---

## 2. Driver PCB (`driver_pcb`) Assembly & 4-Stage Bench Bring-Up

### 2.1 SMD & Through-Hole Soldering
1. **SMD Reflow (`U1..U3`, `Q1A..Q4`, `F1`, `D9..D16`, `L1..L2`, `R1..R20`, `C1..C12`):**
   - Reflow top-side (`F.Cu`) SMDs with solder paste on hotplate/oven.
   - **Verify pinouts & polarity:**
     - `U1`, `U2` (`LM3410XMY/NOPB`): Pin 1 dot on `F.Silkscreen`; ensure the central exposed `DAP` solders cleanly to the `6×` thermal vias.
     - `D13..D15` (`SOD-123`): `F.Silkscreen` U-bracket marks **Pad 1 (Cathode)**.
     - `D9`, `D10` (`SMA`) & `D11` (`SMB`): `F.Silkscreen` bar marks **Cathode**.
     - `U3` (`TL431AIDBZR` `1=K, 2=REF, 3=A`), `Q1A/Q1B` (`DMG2305UX-7` `1=G, 2=S, 3=D`), `Q2..Q4` (`1=B, 2=E, 3=C`), `D12` (`BAV70LT1G` CC), `D16` (`BAW56LT1G` CA).
2. **Through-Hole Connectors (`J1..J4`) & `TP1`/`TP2` Preparation:**
   - Solder `J1` (`GCT USB4085-GF-A` 16+4 TH; inspect closely under magnification for solder bridges across the `0.65 × 0.85 mm` oval signal pins), `J2`, `J3` (`B2B-XH-A`), and `J4` (`B3B-XH-A`).
   - **Option A (`M16_GLAND` baseline) — defer permanent `TP1`/`TP2` soldering until Section 5 Step 3:** Leave `TP1` (`F.Silkscreen` `"TP1:5V"`, `(-8.2, -19.5)`) and `TP2` (`F.Silkscreen` `"TP2:GND"`, `(+8.2, -19.5)`) unpopulated for now. Neither the USB-A plug nor the assembled `driver_pcb` can pass through `MECH-GLAND-1`, so the captive `18 AWG ≤ 1.0 m` pigtail must be threaded through the gland into `MECH-CAP-BOT` **before** soldering to `TP1`/`TP2` in Section 5 Step 3. *(If you temporarily solder test leads or a pigtail to `TP1`/`TP2` during Stage 2–4 bench testing, unsolder them cleanly and clear the `1.3 mm` plated holes before Section 5 Step 3.)*
   - **⚠️ CRITICAL PROTRUSION LIMIT:** Trim all TH component pins (`J1..J4`) — and `TP1`/`TP2` wire tails once soldered in Section 5 Step 3 — on `B.Cu` strictly **`≤ 1.8 mm`** (target `1.0–1.5 mm`) so they stay completely recessed inside the `1.8 mm` Kapton-lined `MECH-ADAPT-BOT` relief pockets + `0.5 mm` `TG-A6200` pad window (`2.3 mm` total depth) and never puncture or short `+5 V` to aluminum.

### 2.2 4-Stage Bench Bring-Up (Before Mounting to Heatsink)
1. **Stage 1 — Cold Shorts Check (unpowered):**
   - Measure resistance across `VBUS–GND` (`> 10 kΩ`), `VIN_PROT–GND`, `VOUT1–GND`, and `VOUT2–GND` to rule out solder bridges before applying power.
2. **Stage 2 — Input Protection, Reverse Polarity & Precision OVP (`J2..J4` unplugged, current-limited PSU `100 mA`):**
   - Power bench bring-up via `J1` (USB-C) on the standard PCBA build, or via temporary bench test leads clipped/tacked to `TP1`/`TP2` if `J1` is unpopulated (remove/unsolder any temporary `TP1`/`TP2` leads before Section 5 gland threading). Apply `5.00 V`: confirm `V_MID ≈ 5.00 V`, `VIN_PROT ≈ 4.98–5.00 V`, and `Q1_GATE ≈ 0 V` (`|VGS| ≈ 5 V`).
   - *(Optional)* Apply `-5 V` / `-12 V` reverse polarity at `100 mA` limit: verify `VIN_PROT ≈ 0 V` (`Q1A` blocks completely).
   - Sweep input upward from `5.0 V` to `6.5 V`: verify `U3` (`TL431`) + `Q2`/`Q4` trips and **latches OFF** cleanly inside **`[5.75 V, 6.14 V]`** (`VIN_PROT` drops to `0 V` and remains latched OFF until input voltage drops below `~5.34–5.66 V`).
3. **Stage 3 — Open-Load OVP Clamp (`J4` connected to `SW1`, `J2`/`J3` unplugged, `100 mA` PSU limit):**
   - Briefly toggle `SW1` to `4-UV` for 1–2 seconds with `J2` open: verify `D13` (`BZT52C18`) clamps `VOUT1` cleanly at **`~18–21 V`** (well below `LM3410`'s `24 V` limit). Return `SW1` to `OFF`.
4. **Stage 4 — Full 4-UV & 8-ALL Load Test (`J2` + `J3` connected to the 4× Al MCPCBs, `3.5 A` PSU limit, UV-A goggles ON!):**
   - **`OFF` (center):** `I_in < 1 mA`.
   - **`4-UV`:** Only `D1..D4` (`365 nm`) glow dimly violet; measure `V_R3 ≈ 190 mV` across `R3 = 0.56 Ω` (`I_LED1 ≈ 339 mA ± 7%`), `VOUT1 ≈ 14.4–14.8 V`, `I_in ≈ 1.11–1.20 A` @ `5.0 V`.
   - **`8-ALL`:** Both `D1..D4` and `D5..D8` (`2×` Blue, `1×` Green, `1×` Cool White) illuminate (`U2` staggered `+1.0 ms`); verify `V_R3 ≈ 190 mV`, `V_R4 ≈ 190 mV`, `VOUT2 ≈ 11.5–11.7 V`, `I_in ≈ 2.07–2.15 A` @ `5.0 V`.

---

## 3. Metalwork Preparation, Thermal Pads, Kapton & Fastener Rules

1. **Machining & Coating `MECH-HS-CORE` (`40 × 40 × 3 × 165.0 mm` Al 6063-T6):**
   - Drill `2× Ø 4.2 mm` bottom `M4` cross-pin through-holes (`6.0 mm` from the bottom tube end at `Y = ±9.0`, i.e., `Z = 138.0`), file `2× ±1.5 mm` slotted `M4` top cross-pin holes (`7.0 mm` from the top tube end at `Y = ±9.0`, i.e., `Z = 290.0`; `4.2 mm` wide × `7.2 mm` tall), and **`90°`-countersink both ends on all four entry/exit faces to `Ø 8.2 mm` outer width** (`~2.0 mm` deep into the `3.0 mm` Al wall, matching along the full `7.2 mm` vertical slot length at top) so the `Ø 8.0 × 2.3 mm` DIN 7991 `M4 × 40 mm` CSK heads (`MECH-FAST-5`) sit flush-or-subflush (`≤ 40.0 mm` overall core width) and clear `MECH-CAP-BOT` / `MECH-CAP-TOP` (`41.0 × 41.0 mm` sockets) with `0.000000 mm³` collision. Also drill/tap `8× M3` MCPCB mounting holes on the 4 faces (`(0, ±32.0) mm` relative to each strip center). *(Do **NOT** drill or file `4×` wire exit slots into `MECH-HS-CORE` — the `4×` `6.0 × 3.5 mm` wire exit channels, `Z = 95.0..144.0`, are already 3D-printed into `MECH-CAP-BOT`'s core socket.)*
   - Mask the `4×` `20 × 80 mm` MCPCB contact zones and top/bottom mating end faces, then coat the core exterior with matte-black high-emissivity VHT enamel (`MECH-COAT-1`, `ε = 0.88`, saving `-2.45 °C` on UV junction temperature).
2. **External Heatsinks (`MECH-HS-EXT-TOP` & `MECH-HS-EXT-BOT`):**
   - **`MECH-HS-EXT-TOP` (`SK 578/50 SA`):** Drill `Ø 6.5 mm` center through-bore for `MECH-EYE-1` and tap `4× M3` hub holes on **`R = 8.5 mm`** (`Ø 24 mm` solid hub).
   - **`MECH-HS-EXT-BOT` — Config A vs Config C Bolt Circle & `0°/90°/180°/270°` Hub Clocking:**
     - **Mandatory `0°/90°/180°/270°` hub clocking (BOTH Config A and Config C):** Drill/tap the `4× M3` hub holes in `MECH-HS-EXT-BOT` and matching `4× M3 × 14 mm` DIN 7991 CSK (`MECH-FAST-4`) holes in `MECH-ADAPT-BOT` at **`0°/90°/180°/270°`** (aligned to `±X`/`±Y`) — **do NOT clock hub holes at `45°/135°/225°/315°`**, because at `R = 8.5 mm` (`Config C`) the `225°` bolt at `(-6.01, -6.01)` hits the `J4` pocket (`6.44 mm³`) and overlaps the `J4` TH pins (`VIN_PROT` `+5 V`), and even at `R = 11.0 mm` (`Config A`) the `225°` bolt grazes the `J4` pocket corner.
     - **Config A (`SK LED R 80 SA`, `DS-100%` upgrade):** Drill/tap `4× M3` hub holes at **`R = 11.0 mm`** (`Ø 34 mm` core, clocked `0°/90°/180°/270°` for `0.000000 mm³` overlap with all pockets and `driver_pcb`). Because `SK LED R 80 SA` has `22` fins (`16.3636°` pitch, `90° / 16.3636° = 5.5` pitches per quadrant), centering all four `45°/135°/225°/315°` diagonals in fin valleys simultaneously is geometrically impossible; instead, use **symmetric indexing (`rot = 0°` paired with `0°/90°/180°/270°` hub holes)** so all four `45°` corners sit symmetrically `4.09°` off a fin center (`12.27°` from the opposite fin). **Before Step 1**, file or mill **`2.6 mm` radial fin-tip clearance notches** (`R_tip ≤ 37.45 mm`, e.g., `37.40 mm`, inward from the `40.0 mm` outer radius) at all four `45°/135°/225°/315°` corner positions — running at least `~12–15 mm` down from `Z = 70 mm` for ball-end `2.5 mm` Allen key access (or full-height `70 mm` along the interfered fin tips for a straight `2.5 mm` hex driver) — so the `Ø 5.5 mm` `MECH-FAST-3` SHCS heads at `R = 40.2 mm` and the hex driver clear with `0.000000 mm³` collision in Section 5 Step 4.
     - **Config C (`SK 578/50 SA` nominal-only):** Drill/tap `4× M3` hub holes at **`R = 8.5 mm`** (`Ø 24 mm` hub, clocked `0°/90°/180°/270°` — **ensure `MECH-ADAPT-BOT` hub CSK holes match `R = 8.5 mm` at `0°/90°/180°/270°` instead of `R = 11.0 mm`**). At `R = 8.5 mm` and `0°/90°/180°/270°`, `driver_pcb` / `J4` TH pin interference is `0.000000 mm³`, **however** the `180°` bolt head (`Ø 6.0 mm`) at `(-8.5, 0)` trims `~1.4 mm` (`1.78 mm³`) into the `-X` wall edge of the `1.8 mm`-deep `J4` pocket (`X ∈ [-6.9, +4.1]`): ensure this `180°` CSK head sits flush-or-subflush (`Z ≤ 78.0 mm`) and is **completely covered by Kapton tape** inside the `J4` pocket before Step 4 (`driver_pcb` installation).
3. **`MECH-ADAPT-BOT` Relief Pockets (Machined or No-Mill Stacked Plate):**
   - Either machine `1.8 mm`-deep pockets into the `Ø 59 × 5 mm` pedestal (`MECH-ADAPT-BOT`), OR use the **no-mill DIY alternative** (`< 0.03 K/W` difference): stack a flat `Ø 90 × 3.0 mm` disc + `Ø 59 × 2.0 mm` solid disc + `Ø 59 × 3.0 mm` plate with sawed/filed rectangular windows, bonded with `Arctic MX-4` and clamped by `MECH-FAST-4` (`4× M3 × 14 mm` CSK clocked at `0°/90°/180°/270°`).
   - **Exact pocket centers & sizes (`dx × dy × 1.8 mm` deep):**
     - `J2/J3`: center `(0.0, +19.2) mm`, size `20.0 × 6.5 mm`
     - `J4`: center `(-1.4, -2.5) mm`, size `11.0 × 5.5 mm`
     - `J1 + TP1/TP2`: center `(0.0, -19.5) mm`, size `21.0 × 7.0 mm` (`Y ∈ [-23.0, -16.0]`, clear of `H3/H4` `5.5 mm` keepouts at `(±14.0, -19.0)`)
   - **Kapton Lining (`MECH-MISC-1`):** Line the floor and walls of all three `1.8 mm` pockets completely with polyimide (Kapton) tape (`≥ 0.05 mm`) — and on Config C (`R = 8.5 mm`), ensure the Kapton lining completely covers the `180°` `MECH-FAST-4` CSK head edge (`X = -5.5 mm`) encroaching into the `-X` wall of the `J4` pocket.
4. **Cut `TG-A6200` Gap Pad (`MECH-TIM-PCB`):**
   - Cut a `34.0 × 44.0 mm` rectangle from the `0.5 mm` `TG-A6200` sheet (`RS 607-066`) and carefully cut out the exact `J2/J3`, `J4`, and `J1+TP1/TP2` windows plus `4× Ø 3.0 mm` corner holes for `H1..H4` (leaving `10.94 cm²` active thermal transfer area).
5. **⚠️ CRITICAL FASTENER LENGTH & INSULATION RULES:**
   - **`MECH-FAST-2` (`4× M2.5 × 6 mm` SHCS + nylon shoulder washers):** `6 mm` length is **mandatory** (gives `0.0 mm` screw protrusion into heatsink fins); nylon shoulder washers electrically isolate `H1..H4` and prevent board warp.
   - **`MECH-FAST-3` (`8× M3 × 8 mm` SHCS):** `8 mm` length is **mandatory** for `1.7–2.2 mm` blind-hole clearance in the `6.7 mm` deep `M3 × 5.7 mm` insert bores (`10 mm` bolts would bottom out).
   - **`MECH-FAST-3W` (`4× M3 × 0.5 mm` DIN 988 shim washers):** Place between flat `MECH-CAP-TOP` and `MECH-ADAPT-TOP` so the `0.5 mm` proud `MECH-HS-CORE` mates metal-to-metal with `MX-4` while leaving a `0.5 mm` thermal air gap over plastic.
   - **`MECH-FAST-5` + `MECH-MISC-1` (`2× M4 × 16 mm` CSK + `2× M4` nylon CSK washers):** Use the **`45°` nylon CSK insulating washers** under the upward bulkhead bolt heads to thermally decouple `MECH-HS-CORE` from the bottom PCB cavity.
   - **`MECH-FAST-1` (`8× M3 × 8 mm` SHCS):** Tighten gently and evenly onto thin `Arctic MX-4` (`MECH-TIM-1`) so the `1.6 mm` Al MCPCB strips do not bow.

---

## 4. 3D-Printed End-Caps (`PETG`/`ASA` FDM or `PA12` SLS) & Inserts

- **Files (`mechanical_design/cad/`):**
  - **FDM (`0.25 mm` clearance, `Ø 4.1 mm` insert bores):** `mech_cap_bot.stl` (Option A M16), `mech_cap_bot_usbc.stl` (Option B USB-C), `mech_cap_top.stl`. **Use `PETG` or `ASA` (`0.2 mm` layers, `4–5` perimeters, `25–40%` gyroid infill). Do NOT use PLA** (`T_g ~55–60 °C` softens near summer cavity/bulkhead temperatures).
  - **SLS (`0.15 mm` clearance, `Ø 4.0 mm` insert bores):** `mech_cap_bot_sls.stl`, `mech_cap_top_sls.stl` (`PA12` nylon, e.g., JLC3DP).
- **100% Support-Free Print Orientation:**
  - Print `MECH-CAP-BOT` / `MECH-CAP-BOT-USBC` **upright** (`Z = 73.0 mm` base on build plate; `0.022 mm²` `> 46°` overhang).
  - Print `MECH-CAP-TOP` **inverted** (`100%` flat `Z = 296.5 mm` top face on build plate; `0.005 mm²` `> 46°` overhang).
- **Heat-Set Inserts:** Using a soldering iron (`~220–240 °C` for PETG, `~260 °C` for PA12/ASA), press `4× M3 × 5.7 mm` CNC Kitchen brass inserts flush into `MECH-CAP-BOT` (`R = 40.2 mm`) and `4×` into `MECH-CAP-TOP` (`R = 34.0 mm`).

---

## 5. Final Mechanical Integration, O-Rings & Power Entry

1. **Bottom Heatsink & Adapter:** *(Config A `SK LED R 80 SA` only: confirm the `4×` `2.6 mm` radial fin-tip clearance notches at `45°/135°/225°/315°` are already filed/milled per Section 3.2 before assembly.)* Apply a thin film of `Arctic MX-4` (`MECH-TIM-1`) between `MECH-ADAPT-BOT` and `MECH-HS-EXT-BOT` (clocked `0°/90°/180°/270°` per Section 3.2, never `45°`), bolt flush-or-subflush (`Z ≤ 78.0 mm`) with `4× M3 × 14 mm` DIN 7991 CSK (`MECH-FAST-4`), and apply Kapton tape inside the 3 relief pockets (on Config C `R = 8.5 mm`, completely covering the `180°` CSK head edge inside the `-X` wall of the `J4` pocket).
2. **Core Spine & MCPCBs:** Cross-pin `MECH-ANCHOR-BOT` inside `MECH-HS-CORE` (`2× M4 × 40 mm` DIN 7991 CSK seated flush-or-subflush in the `90°`-countersunk bottom holes at `6.0 mm` from bottom end / `Z = 138.0`, `≤ 40.0 mm` overall core width), slide `MECH-HS-CORE` into `MECH-CAP-BOT`, and bolt upward from the open bottom cavity with `2× M4 × 16 mm` CSK + `2× M4` nylon CSK washers (`MECH-FAST-5` / `MECH-MISC-1`). Apply thin `MX-4` under `4× MECH-MCPCB-1..4`, secure with `8× M3 × 8 mm` SHCS (`MECH-FAST-1`), and feed the LED harness down through the `4×` pre-printed `6.0 × 3.5 mm` wire exit channels in `MECH-CAP-BOT`'s core socket into the open bottom cavity.
3. **Panel Switch & Power Entry (`MECH-CAP-BOT`):**
   - **`SW1` / `SW1_BOOT` (`+X` side):** Solder `3× 24 AWG` leads (`J4.1 = UV_EN`, `J4.2 = VIN_PROT`, `J4.3 = ALL_EN`) to `SW1`, insert `SW1` from inside the `26.5 mm` corridor through the `Ø 6.35 mm` hole, and thread `SW1_BOOT` (`759D02000`) externally onto the `1/4-40` bushing.
   - **Option A (`M16_GLAND` — Recommended Weatherproof Baseline, `mech_cap_bot.stl`):** Drop the `22 mm AF` M16 nylon locknut into the internal `22.5 mm AF` anti-rotation hex alcove. Feed the stripped and tinned free end of the `18 AWG ≤ 1.0 m` captive USB-A pigtail (`4–8 mm` jacket; if a test pigtail was temporarily soldered to `TP1`/`TP2` during Section 2.2 bring-up, unsolder it first) from **outside** through `MECH-GLAND-1` and the captive `22 mm AF` locknut into `MECH-CAP-BOT`'s open bottom cavity, leaving ~`80–100 mm` internal service slack. Tighten `MECH-GLAND-1` externally onto the cable jacket, and **then** solder `+5 V` → `TP1` (`"TP1:5V"`) and `GND` → `TP2` (`"TP2:GND"`) on `driver_pcb` inside the open cavity — trim `B.Cu` wire tails strictly **`≤ 1.8 mm`** and verify clean clearance inside the `MECH-ADAPT-BOT` relief pocket before seating `driver_pcb` and bolting `MECH-CAP-BOT` onto `MECH-ADAPT-BOT`.
   - **Option B (`USB_C` — Removable Cable, `mech_cap_bot_usbc.stl`):**
     > **⚠️ MANDATORY EXTENDED-BARREL USB-C CABLE (`MECHANICAL_DESIGN.md` §3):**  
     > The final CAD bezel places the `14.0 × 8.5 mm` overmold stop at `Y = -33.10 mm` (`2.600 mm` bezel wall), while `J1`'s front face sits at `Y = -25.34 mm` (requiring `4.55 mm` insertion to `Y = -20.79 mm`). **Option B strictly requires an extended-barrel USB-C cable (`≥ 12.31 mm` barrel, e.g., a `13.0 mm` extended-tip plug)** — standard `6.65 mm` USB-C plugs cannot reach `J1`'s recessed tongue! In addition, the USB-C cable round-trip resistance must satisfy **`R_cable ≤ 0.018 Ω`** (`18 AWG ≤ 0.4 m` or `16 AWG ≤ 0.65 m`).
4. **Driver PCB & Cavity Seal:** Lay the notched `0.5 mm` `TG-A6200` pad on `MECH-ADAPT-BOT`, seat `driver_pcb` (confirming `J1..J4` and `TP1`/`TP2` `B.Cu` tails `≤ 1.8 mm` fit cleanly inside the Kapton-lined pockets), and secure with `4× M2.5 × 6 mm` SHCS + nylon shoulder washers (`MECH-FAST-2`). Plug `J2`, `J3`, and `J4` (double-check `J2`/`J3` polarity!). Lightly coat `MECH-GASKET-3` (`66 × 2.0 mm` VMQ70) with **silicone grease** (never petroleum grease), seat in the bottom V-roof groove, and bolt `MECH-CAP-BOT` to `MECH-ADAPT-BOT` (`4× M3 × 8 mm` SHCS, `MECH-FAST-3` at `R = 40.2 mm`, tightening from below with a `2.5 mm` ball-end/straight hex driver through the pre-notched `2.6 mm` radial fin-tip reliefs on Config A or unobstructed outer rim on Config C).
5. **Top Anchor Cross-Pinning, Glass Tube & Top Cap:** First insert `MECH-ANCHOR-TOP` (`33.2 × 33.2 × 14.0 mm`, central `M6` bore vertical) into the top bore of `MECH-HS-CORE` (`Z = 283.0..297.0`) and cross-pin it with `2× M4 × 40 mm` DIN 7991 CSK bolts (`MECH-FAST-5`) seated flush-or-subflush inside the `90°`-countersunk `±1.5 mm` slotted top core holes (`7.0 mm` from top end, `Y = ±9.0`, `Z = 290.0`, keeping the `39.8 mm` pins flush within the `40.0 mm` core width — cross-pinning **must** occur before installing `MECH-CAP-TOP`, whose solid `Ø 84.0 mm` wall otherwise blocks `Z = 290.0`). Next, lightly silicone-grease `MECH-GASKET-1` and `MECH-GASKET-2` (`68 × 3.5 mm` VMQ70, or `BS231` alt). Seat `MECH-GASKET-1` in `MECH-CAP-BOT`'s glass groove, lower `MECH-TUBE-1` (`75/68/3.5 × 150 mm` borosilicate) into `MECH-CAP-BOT`'s socket, seat `MECH-GASKET-2` into `MECH-CAP-TOP`'s groove, and slide `MECH-CAP-TOP` down over `MECH-HS-CORE` (the `41.0 × 41.0 mm` through-aperture clears the flush cross-pins) onto the top of `MECH-TUBE-1`.
6. **Top Heatsink Subassembly, Adapter Clamp & Hanging Eye:** First apply a thin film of `MX-4` (`MECH-TIM-1`) between `MECH-ADAPT-TOP` and `MECH-HS-EXT-TOP` (`SK 578/50 SA`, keeping the `Ø 6.5 mm` center bore clear) and bolt `MECH-ADAPT-TOP` upward into `SK 578/50 SA`'s tapped `Ø 24 mm` hub using `4× M3 × 8 mm` DIN 7991 CSK bolts (`MECH-FAST-4` at `R = 8.5 mm`, tightening heads completely flush on the `Z = 297.0` underside — this **must** occur before bolting `MECH-ADAPT-TOP` to `MECH-CAP-TOP`, which otherwise seals off the `R = 8.5 mm` CSK entry against `MECH-HS-CORE` and `MECH-ANCHOR-TOP`). Next, place the `4× M3 × 0.5 mm` DIN 988 SS spacer washers (`MECH-FAST-3W`) over `MECH-CAP-TOP`'s `R = 34.0 mm` heat-set inserts, apply thin `MX-4` to `MECH-HS-CORE`'s `0.5 mm`-proud top face (or the matching center zone of `MECH-ADAPT-TOP`), seat the joined `MECH-ADAPT-TOP + SK 578/50 SA` subassembly onto `MECH-HS-CORE` and `MECH-FAST-3W`, and bolt `MECH-ADAPT-TOP` down into `MECH-CAP-TOP` using `4× M3 × 8 mm` SHCS (`MECH-FAST-3` at `R = 34.0 mm`, `4.0 mm` radially clear outside `SK 578/50 SA`'s `Ø 60 mm` rim). Finally, thread `MECH-EYE-1` (`M6 × 75 mm` eye bolt + washer, or `DIN 582 M6` eye nut + `M6 × 75 mm` stud, with medium threadlocker) down through `SK 578/50 SA` and `MECH-ADAPT-TOP` into `MECH-ANCHOR-TOP`'s central `M6 × 1.0` tapped hole.

---

## 6. Powering the Lamp in the Field (USB Powerbank Requirements)

- **Minimum Supply Spec (`INTERFACE_CONTRACT.md` §2.1):**
  - **Option A (`M16_GLAND`, `18 AWG ≤ 1.0 m`, `R_cable ≤ 0.048 Ω`):** Regulated `5.0 V` powerbank maintaining **`≥ 4.85 V` under `3.2 A` peak / `2.15 A` nominal load**, rated **`≥ 3.0 A` continuous at `5 V`** (QC 3.0 / USB-C PD `5 V 3 A` bank). Standard `2.0 A` / `2.1 A` powerbanks will trip overcurrent protection or sag below `4.85 V` in `8-ALL` mode.
  - **Option B (`USB_C`, `R_cable ≤ 0.018 Ω`):** Regulated `5.0 V` bank maintaining **`≥ 4.90 V`**, rated **`≥ 3.5 A`**.
- **Runtime Comparison:**
  - **`8-ALL` mode:** `~10.74 W` (`~2.15 A @ 5.0 V`) — full `365 nm` UV + Royal Blue + Green + Cool White attraction spectrum.
  - **`4-UV` mode:** `~5.54 W` (`~1.11 A @ 5.0 V`) — cuts powerbank draw nearly in half (`~2×` battery runtime) while keeping full `365 nm` UV coverage.
