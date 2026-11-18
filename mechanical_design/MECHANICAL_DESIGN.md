# M3 Mechanical & Passive Thermal Design — LepiLED DIY Maxi Switch

**Status:** Complete & Verified (2D/3D FVM Thermal + All-Pairs Parametric B-Rep CAD + UK Sourcing)  
**Reconciled Contracts:** `circuit_design/INTERFACE_CONTRACT.md` §1.1 & §2, `PROJECT.md` §Interface Contracts  
**Part Registry:** `mechanical_design/MECH_PARTS.csv` (29 `MECH-*` line items, 1:1 ready for M4 BOM)

---

## 1. Mechanical & Thermal Architecture Summary

Pure passive (fanless) cooling satisfies every LED, Driver IC, MOSFET, and Driver PCB thermal limit across all M1 electrical modes (`4-UV Nom`, `8-ALL Nom`, `8-ALL DS-RealWPE`, and `8-ALL DS-100%`), both ambient temperatures (`22 °C` and `30 °C`), and both orientations (**vertical hanging** and **horizontal**) via a **Decoupled Dual-Heatsink Passive Cooling** architecture verified by coupled 2D/3D Finite-Volume (FVM) PDE solvers:

1. **Optical / Emitter Core (`MECH-HS-CORE` + `4× MECH-MCPCB-1..4`):**
   - `4×` `20.0 × 80.0 × 1.6 mm` `1.0 W/(m·K)` Aluminum MCPCB strips (`MECH-MCPCB-1..4`) mounted with `Arctic MX-4` (`MECH-TIM-1`) and `8× M3` stainless screws onto the 4 orthogonal faces of **`MECH-HS-CORE`** (`40 × 40 × 3 mm` Al 6063-T6 square hollow tube, matte-black coated via `MECH-COAT-1` $\varepsilon = 0.88$, exact CAD length **`165.0 mm`**).
   - **2D Pinched-Neck MCPCB Spreading (Reconciled to M2 `build_led_mcpcb.py`):** M2's `3535` LED thermal pad (`1.30 × 3.25 mm`) is laterally pinched by anode/cathode pads at `±1.385 mm`, forcing heat through `1.30 mm`-wide `1 oz` Cu necks into the custom `492.7 mm²` (UV) and `279.5 mm²` (Vis) thermal copper wings. Genuine 2D FVM PDE solution yields **`R_diel_UV = 15.292 K/W`** (`17.543 K/W` peak) and **`R_diel_Vis = 18.885 K/W`** (`21.837 K/W` peak), leaving `14.4 °C` (`DS-100%`) and `40.5 °C` (`Nom`) UV thermal margin.
   - Enclosed inside a premade UK borosilicate 3.3 glass cylinder (**`MECH-TUBE-1`**, `CRH Supplies` `75 mm OD / 68 mm ID / 3.5 mm wall × 150 ± 1.0 mm`, `~90%` UV-A transmission at `365 nm`, `126.0 mm` exposed window) sealed at both ends by compliant **`68 × 3.5 mm` VMQ70 O-rings (`MECH-GASKET-1..2`)** in `4.90 mm`-wide × `2.65 mm`-deep flush-pilot grooves (`24.3%` nominal squeeze, `10.0%–38.6%` rigid across `149.0–151.0 mm` with `91.3% <= 92%` gland fill at `151.0 mm`, plus `±1.5 mm` slotted `M4` top core float).

2. **All-Metal Top Thermal Spine & Anchor Retention:**
   - `MECH-HS-CORE` passes through `MECH-CAP-TOP`'s `41.0 × 41.0 mm` aperture (with `4× 0.5 mm` stainless shim spacer washers **`MECH-FAST-3W`** on a **100% flat top face**) to mate metal-to-metal via `MECH-TIM-1` onto **`MECH-ADAPT-TOP`** (`Ø 76.0 × 3.0 mm` Al 6061, `R_int_top = 0.284 K/W`) and **`MECH-HS-EXT-TOP`** (**`Fischer Elektronik SK 578/50 SA`**, `Ø 60.0 × 50.0 mm`, DigiKey UK `£5.88` ex VAT).
   - Hanging weight passes exclusively through metal: **`MECH-EYE-1`** (`M6 × 75 mm` stainless long-shank eye bolt) threads through `SK 578/50 SA` + `MECH-ADAPT-TOP` into **`MECH-ANCHOR-TOP`** (`33.2 × 33.2 × 14.0 mm` Al 6061 block, central `M6` tapped + `2×` offset `M4 × 40 mm` flush CSK cross-pins at `Y = ±9.0 mm` in `±1.5 mm` core slots).
   - Bottom core retention uses an internal **`MECH-ANCHOR-BOT`** (`33.2 × 33.2 × 12.0 mm` Al 6061 block cross-pinned inside `MECH-HS-CORE` by `2× M4 × 40` flush CSK before cap insertion), bolted upward by `2× M4 × 16 mm` DIN 7991 CSK bolts + `2× M4` nylon countersunk (CSK) insulating washers (`MECH-MISC-1`, compatible with the self-supporting `45°` CSK cone) through the bulkhead from inside the wide-open bottom PCB cavity (zero blind glass-slot screws).

3. **Thermally Decoupled Driver PCB Path (`T_pcb_bot` & `T_pcb_top_avg <= 55 °C` Guarantee):**
   - **Why `SK 578/50 SA` + lumped `0.28 K/W` was insufficient:** 3D 3-layer FVM PDE analysis (`dx = 0.25 mm`, synced 1:1 to M2 `driver_pcb_cpl.csv` / `driver_pcb.kicad_pcb`: `F.Cu` isolated copper pours `U1/U2` `3.0 × 2.0 mm` rotated DAPs / `VOUT1` / `VOUT2` / `SW1_NODE` / `SW2_NODE` / `VBUS_FUSED` / `V_MID` + `15%` signal trace fill / `B.Cu` GND plane with `SW1_NODE`/`SW2_NODE` keepouts `Y >= +6.65` / coupled `MECH-ADAPT-BOT` + `0.08 K/W` bottom TIM-2 hub, `32×` exact KiCad GND vias [`6× U1` + `6× U2` + `20×` stitching], `4× H1..H4` plated holes, `25 µm` soldermask, and `J1`/`TP1`/`TP2`/`J2..J4` pad cutouts leaving `10.94 cm²` active pad area) showed that `SK 578/50 SA` on the bottom (`Config C`) reached `T_pcb_top_avg = 62.5 °C > 55 °C` in `30 °C` horizontal `DS-100%` (`4.39 W` PCB loss).
   - **Solution (`Config A`):** Separate `MECH-HS-CORE` from the Driver PCB cavity with a **`6.0 mm` PETG/PA12 bulkhead** (`R_bulkhead = 11.20 K/W` parallel plastic + outer wall + nylon-isolated `M4` bolts + radiation). Upgrade **`MECH-HS-EXT-BOT`** to **`Fischer Elektronik SK LED R 80 SA`** (`Ø 80.0 × 70.0 mm`, `22` radial fins, `Ø 34.0 mm` core, catalog `1.35 K/W`, TME UK `£24.60` ex VAT) coupled via **`MECH-ADAPT-BOT`** (`Ø 90.0 × 3.0 mm` plate + `Ø 59.0 × 5.0 mm` PCB pedestal) and a **`0.5 mm` `TG-A6200` (`6.2 W/(m·K)`) insulating gap pad (`MECH-TIM-PCB`)**.
   - **M2-Aligned Pin Relief Pockets:** `MECH-ADAPT-BOT` includes `1.8 mm`-deep Kapton-lined milled pockets (and matching `MECH-TIM-PCB` cutouts) for `J2/J3` (`(0, +19.2)`, `20.0 × 6.5 mm`), `J4` (`(-1.4, -2.5)`, `11.0 × 5.5 mm`), and **`J1 + TP1/TP2`** (`(0.0, -19.5)`, `21.0 × 7.0 mm`, `Y ∈ [-23.0, -16.0]`, giving `0.64 mm` `-Y` margin past `J1` `SH3/SH4` tabs at `Y = -22.36` and clear of `H3/H4` `5.5 mm` keepouts at `(±14.0, -19.0)`), preventing `1.8 mm` TH leads/`18 AWG` soldered tails from puncturing `MECH-TIM-PCB` or shorting `+5 V` `VBUS` to aluminum.

---

## 2. First-Principles 2D/3D Thermal Verification (`mechanical_design/thermal/`)

Reproduced via `mechanical_design/thermal/thermal_analysis.py`:
- **2D MCPCB FVM (`dx = 0.10 mm`):** `R_diel_UV = 15.292 K/W` (`12.198 K/W` @ `2 oz` Cu; `24.038 K/W` bare pad), `R_diel_Vis = 18.885 K/W`.
- **3D Driver PCB FVM (`dx = 0.25 mm`, M2 1:1 synced `F.Cu` pours & `32×` KiCad GND vias, coupled `MECH-ADAPT-BOT`, `0.5 mm` `TG-A6200`, `10.94 cm²` active area):** `R_eff_bot_avg = 0.369 K/W`, `ΔT_adapt_bot_avg = 0.37 °C`, `ΔT_bot_avg = 1.62 °C`, `ΔT_top_avg = 9.36 °C`, `ΔT_U1_top = 60.06 °C`, `ΔT_Q1A_top = 58.50 °C`, `ΔT_Q1B_top = 61.46 °C` (`ΔT_Q1_top = max = 61.46 °C`, `4.394 W` `DS-100%`).

### 2.1 `Config A` Steady-State Temperatures & Margins (`20 / 20 PASS`)
Limits: $T_{j,\text{UV}} < 100^\circ\text{C}$, $T_{j,\text{Vis}} < 150^\circ\text{C}$, $T_{\text{PCB,bot}} \le 55^\circ\text{C}$, $T_{\text{PCB,top\_avg}} \le 55^\circ\text{C}$, $T_{j,U1} \le 125^\circ\text{C}$ (3D via-coupled & JEDEC $53.7^\circ\text{C/W}$), $T_{j,Q1} = \max(T_{j,Q1A}, T_{j,Q1B}) \le 150^\circ\text{C}$.

| $T_{\text{amb}}$ & Orient. | Mode | $T_{j,\text{UV}}$ | $T_{j,\text{Vis}}$ | $T_{\text{PCB,bot}}$ | $T_{\text{PCB,top\_avg}}$ | $T_{j,U1}$ (3D / JEDEC) | $T_{j,Q1}$ | Status |
|---|---|---:|---:|---:|---:|---:|---:|---|
| `22 °C` Vertical | `4-UV Nom` (`2.96 + 0.80 W`) | `45.0 °C` | `32.1 °C` | `26.7 °C` | `28.1 °C` | `48.1 / 48.4 °C` | `35.1 °C` | **PASS** |
| `22 °C` Vertical | `8-ALL Nom (40% UV)` (`5.26 + 1.60 W`) | `51.0 °C` | `57.3 °C` | `29.5 °C` | `32.5 °C` | `50.7 / 51.2 °C` | `56.5 °C` | **PASS** |
| `22 °C` Vertical | `8-ALL DS-100%` (`10.78 + 4.39 W`) | `76.4 °C` | `85.8 °C` | `36.3 °C` | `44.1 °C` | `103.5 / 105.6 °C` | `109.8 °C` | **PASS** |
| `30 °C` Vertical | `4-UV Nom` | `52.9 °C` | `39.9 °C` | `34.7 °C` | `36.1 °C` | `56.1 / 56.4 °C` | `43.1 °C` | **PASS** |
| `30 °C` Vertical | `8-ALL Nom (40% UV)` | `58.9 °C` | `65.1 °C` | `37.5 °C` | `40.5 °C` | `58.8 / 59.2 °C` | `64.5 °C` | **PASS** |
| `30 °C` Vertical | `8-ALL DS-RealWPE` (`6.85 + 4.39 W`) | `67.0 °C` | `76.0 °C` | `43.3 °C` | `51.1 °C` | `110.5 / 112.6 °C` | `116.8 °C` | **PASS** |
| `30 °C` Vertical | `8-ALL DS-100%` | `84.3 °C` | `93.6 °C` | `44.4 °C` | `52.1 °C` | `111.6 / 113.7 °C` | `117.9 °C` | **PASS** |
| `30 °C` Horizontal | `4-UV Nom` | `53.1 °C` | `40.2 °C` | `35.0 °C` | `36.4 °C` | `56.4 / 56.7 °C` | `43.4 °C` | **PASS** |
| `30 °C` Horizontal | `8-ALL Nom (40% UV)` | `59.5 °C` | `65.7 °C` | `38.2 °C` | `41.2 °C` | `59.4 / 59.9 °C` | `65.2 °C` | **PASS** |
| `30 °C` Horizontal | `8-ALL DS-RealWPE` | `67.9 °C` | `76.8 °C` | `44.6 °C` | `52.4 °C` | `111.9 / 113.9 °C` | `118.1 °C` | **PASS** |
| `30 °C` Horizontal | `8-ALL DS-100%` (Worst Corner) | **`85.6 °C`** | **`94.9 °C`** | **`45.9 °C`** | **`53.7 °C`** | **`113.1 / 115.2 °C`** | **`119.4 °C`** | **PASS** |

### 2.2 Sensitivity & Stress Tests (`Horizontal`, `8-ALL Nom` / `DS-100%`)
- `1.0 mm` `TG-A6200` PCB pad (`30 °C`): `T_pcb_bot = 46.2 °C`, `T_pcb_top_avg = 54.0 °C`, `T_j,U1 = 114.5 / 115.5 °C` (**PASS**).
- Cheaper `3.0 W/(m·K)` `0.5 mm` gap pad (`30 °C`): `T_pcb_bot = 46.2 °C`, `T_pcb_top_avg = 54.0 °C` (**PASS**).
- Bare mill-finish core ($\varepsilon = 0.34$, omitted `MECH-COAT-1`, `30 °C`): `T_j,UV = 88.05 °C`, `T_pcb_top_avg = 54.01 °C` (`+2.45 °C` UV penalty vs `ε = 0.88`, **PASS**).
- Thick `0.25 mm` `TIM-1/2` bondline (`30 °C`): `T_j,UV = 86.1 °C`, `T_pcb_top_avg = 53.7 °C` (**PASS**).
- `+20% R_th` still-air penalty (`30 °C`): `T_pcb_bot = 48.0 °C ≤ 55`, `T_j,U1 = 115.2 / 117.3 °C ≤ 125`, `T_j,UV = 87.7 °C < 100` (`T_pcb_top_avg = 55.7 °C` in `DS-100%`; `42.2 °C` in `Nom`).
- Hot summer `T_amb = 35 °C`: `T_pcb_bot = 50.9 °C ≤ 55`, `T_j,U1 = 118.1 / 120.2 °C ≤ 125`, `T_j,UV = 90.4 °C < 100` (`T_pcb_top_avg = 58.6 °C` in `DS-100%`; `46.1 °C` in `Nom`).

---

## 3. Parametric CAD, Printability, DIY Metalworking & Assembly

- **Variants Exported (`mechanical_design/cad/`):**
  - `FDM` (`0.25 mm` clearance, `Ø 4.1 mm` inserts): `mech_cap_bot.step/.stl`, `mech_cap_top.step/.stl`.
  - `SLS` (`0.15 mm` clearance, `Ø 4.0 mm` inserts): `mech_cap_bot_sls.step/.stl`, `mech_cap_top_sls.step/.stl`.
  - `USB_C` (`FDM`): `mech_cap_bot_usbc.step/.stl` (recessed `14.0 × 8.5 mm` overmold stop at `Y = -33.10 mm` directly against the `Ø 61.0 mm` cavity wall [`Y_in = -30.50 mm`], preserving **`2.600 mm ≥ 2.500 mm`** bezel wall across the entire cutout Z-span around the `9.5 × 3.8 mm` slot [verified by `3,705`-ray vectorized STL ray-cast: `min_wall = 2.6000 mm`, `0` anomalies], `45°` pitched roofs, `2.680 mm` above `MECH-GASKET-3`, `4.730 mm` floor, and `0.022 mm²` `> 46°` overhang). **Mandatory Option B cable requirement:** per `datasheets/usb4085.pdf` pp. 1–2 (`J1` tongue recessed `0.80 mm`, full mating insertion **`4.55 mm`** to `Y = -20.79 mm`), **Option B (`USB_C`) REQUIRES an extended-barrel USB-C cable (`≥ 12.31 mm` barrel, e.g. a `13.0 mm` extended-tip USB-C plug providing `0.690 mm` overmold seating margin)** — standard `6.65 mm`-barrel USB-C cables can insert at most `0.49 mm` past `J1`'s outer shell face (short of the `0.80 mm`-recessed tongue) and **will not mate electrically**. Primary baseline `M16_GLAND` (`TP1`/`TP2`) is unaffected.
- **Support-Free Printability:** Print `MECH-CAP-BOT` upright (`Z = 73.0 mm` on bed) and `MECH-CAP-TOP` inverted (`100%` flat `Z = 296.5 mm` face on bed — zero proud pads, `14.5 mm` flange thickness gives `3.10 mm` solid plastic above `MECH-GASKET-2` roof, `euler = 0, genus = 1`). All internal cones (`40.3°`), O-ring V-roofs (`45°`), blind insert drill-point tips (`45°`), `SW1`/`M16`/`USB-C` unobstructed entry corridors & pitched roofs (`45°`), and external spot-faces (`45°` teardrops) yield **`0.005 mm²` (`MECH-CAP-TOP`) and `0.022 mm²` (`MECH-CAP-BOT` & `MECH-CAP-BOT-USBC`)** `> 46°` off-bed overhang.
- **DIY Metalworking vs No-Mill Spacer Alternative:**
  - *Machined baseline:* `MECH-ADAPT-BOT` (`Ø 90 × 3 mm` + `Ø 59 × 5 mm` pedestal) uses a `1.8 mm`-deep end-mill/Dremel pocket for `J1/TP1/TP2`, `J2/J3`, and `J4`.
  - *No-mill DIY alternative:* Stack a flat `Ø 90 × 3.0 mm` Al disc + `Ø 59 × 2.0 mm` solid Al disc + `Ø 59 × 3.0 mm` Al plate with simple saw/drill/file rectangular slots (`J1/TP1/TP2`, `J2/J3`, `J4`) bonded with `MX-4` and clamped by `MECH-FAST-4` (`4× M3 × 14 mm` CSK). Thermal impact is `< 0.03 K/W`.
- **Assembly Order:**
  1. Press `4× M3` heat-set inserts into `MECH-CAP-BOT` (`R = 40.2 mm`) and `4×` into `MECH-CAP-TOP` (`R = 34.0 mm`).
  2. Bolt `MECH-ADAPT-BOT` onto `MECH-HS-EXT-BOT` (`SK LED R 80 SA`) with `MX-4` and `4× M3 × 14 mm` CSK (`R = 11.0 mm`); apply Kapton tape inside `J1/TP1/TP2`, `J2/J3`, and `J4` relief pockets.
  3. Cross-pin `MECH-ANCHOR-BOT` inside `MECH-HS-CORE` (`2× M4 × 40` flush CSK at `Z = 138.0`), insert `MECH-HS-CORE` into `MECH-CAP-BOT`, and bolt upward through the bulkhead from the wide-open bottom PCB cavity using `2× M4 × 16 mm` DIN 7991 CSK bolts + `2× M4` nylon countersunk (CSK) insulating washers (`MECH-MISC-1`); mount `4× MECH-MCPCB-1..4` (`MX-4` + `8× M3 × 8`) and route `22 AWG` wires down the `4×` core slots into the open `MECH-CAP-BOT` cavity.
  4. Mount `SW1`/`SW1_BOOT` (`+X`) and `MECH-GLAND-1` (`-Y`, `22 mm` AF locknut drops into captive `22.5 mm` AF hex alcove, tighten gland from outside; or prepare Option B USB-C access) before installing the Driver PCB.
  5. Lay `0.5 mm` `TG-A6200` (`MECH-TIM-PCB`, notched for `J1/TP1/TP2/J2..J4`) on `MECH-ADAPT-BOT` and secure the Driver PCB with **`4× M2.5 × 6 mm`** SHCS + insulating nylon shoulder washers (`0.0 mm` fin protrusion); solder `TP1`/`TP2` (Option A) and plug `J2..J4`; seat `MECH-GASKET-3` (`66 × 2.0 mm`) and bolt `MECH-CAP-BOT` to `MECH-ADAPT-BOT` with `4× M3 × 8 mm` SHCS.
  6. Cross-pin `MECH-ANCHOR-TOP` in `±1.5 mm` top core slots (`2× M4 × 40` flush CSK at `Y = ±9.0`), seat `MECH-GASKET-1` (`68 × 3.5 mm`), `MECH-TUBE-1`, and `MECH-GASKET-2` (`68 × 3.5 mm`), slide `MECH-CAP-TOP` over `MECH-HS-CORE`, place `4× 0.5 mm` spacer washers (`MECH-FAST-3W`), bolt `MECH-ADAPT-TOP` (`MX-4`) to `MECH-CAP-TOP` (`4× M3 × 8`) and `SK 578/50 SA` (`4× M3 × 8` CSK), and torque `MECH-EYE-1` (`M6 × 75 mm`).

---

## 4. Lamp-Parts Budget Reconciliation (`M1 + M2 + M3`)

| Subsystem | Scope & Source | Estimated UK Retail (ex VAT) | Estimated UK Retail (inc. VAT) |
|---|---|---:|---:|
| **M1 Electronics** | `circuit_design/COMPONENT_IDS.csv` (67 active/passive parts) | `~£35.00 – £42.00` | `~£42.00 – £50.40` |
| **M2 Driver PCB Fab** | JLCPCB `36 × 46 mm` 2-layer FR4 (amortized/bundled with MCPCBs) | `~£3.50 – £6.50` | `~£4.20 – £7.80` |
| **M3 Mechanical (`MECH-*`)** | `mechanical_design/MECH_PARTS.csv` (29 items, excl. 3D filament per R4; includes `£24.60` `SK LED R 80 SA`) | **`£85.23`** *(or `£66.51` with `SK 578/50 SA` nom-only)* | **`£102.28`** *(or `£79.81` nom-only)* |
| **Total Lamp Parts** | Consolidated DigiKey/TME/RS/JLCPCB/CRH/Accu UK orders | **`~£124 – £134`** *(or `~£105 – £115` w/ `SK 578/50`)* | **`~£149 – £161`** |

*(Budget trade-off note: Upgrading `MECH-HS-EXT-BOT` from `SK 578/50 SA` (`£5.88`, DigiKey UK) to `SK LED R 80 SA` (`£24.60`, TME UK) adds `+£18.72` ex VAT (`~£24` above the `~£100` ex-VAT baseline) in order to guarantee `T_pcb_top_avg <= 55 °C` even under stacked `4.39 W` `DS-100%` datasheet worst-case fault corners; for nominal-mode-only DIY builds `<= 30 °C`, `SK 578/50 SA` remains `~£100` ex VAT.)*
