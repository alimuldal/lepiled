# LepiLED DIY Maxi Switch — PCB Design & Manufacturing Summary (Milestone M2)

**Toolchain:** User-space KiCad `9.0.8` (`kicad-cli`, Python `pcbnew 9.0.8`) and `gerbv 2.10.0` (provisioned via `/home/alimuldal/.local/share/lepiled-tools/bin/`; see `docs/BLOCKERS.md` Sec. 3).  
**Reproducible Generators:**
- Board 1 (Driver & Protection PCB): `pcb_design/driver_pcb/build_driver_pcb.py`
- Board 2 (Aluminum MCPCB Dual-LED Strip, `MECH-MCPCB-1..4`): `pcb_design/led_mcpcb/build_led_mcpcb.py`

---

## 1. Board Stackups & Fabrication Parameters (JLCPCB / PCBWay)

| Parameter | Board 1 — Driver & Protection PCB (`driver_pcb`) | Board 2 — Dual-LED Al MCPCB Strip (`led_mcpcb`, qty 4×) |
|---|---|---|
| **Outline & Corners** | `36.0 × 46.0 mm`, `2.0 mm` corner radii | `20.0 × 80.0 mm`, `1.0 mm` corner radii |
| **Layers & Substrate** | **2-layer** `1.6 mm` FR4 (`Tg130–140`) | **1-layer** `1.6 mm` Aluminum MCPCB (`1.0 W/m·K` dielectric) |
| **Copper Weight** | `1 oz` (`35 µm`) outer (`F.Cu` + `B.Cu`) | **`1 oz` (`35 µm`) `F.Cu` ONLY** (zero `B.Cu`, zero vias, zero PTH) |
| **Solder Mask / Silk** | Green (or matte black) LPI + White silkscreen | **White** LPI (`F.Mask` only) + **Black** silkscreen (`F.Silkscreen`) |
| **Surface Finish** | ENIG or Lead-Free HASL | Lead-Free HASL or ENIG |
| **Mounting Holes** | `H1..H4` at `(±14.0, ±19.0) mm`: `2.7 mm` PTH / `5.5 mm` pad (`GND`) | `MH1, MH2` at `(0.0, ±32.0) mm`: `3.2 mm` NPTH / `6.0 mm` head keepout |
| **Min Track / Space / Via** | `0.25 mm` / `0.20 mm` (`0.25 mm` HV/SW) / `0.30 mm` drill (`0.60 mm` pad) | `0.48 mm` / `0.25 mm` / **none (0 vias, 0 PTH)** |

---

## 2. ERC, DRC & Schematic-to-PCB Parity Verification

Both boards pass KiCad 9.0.8 ERC (`--severity-all --exit-code-violations`) and DRC (`--schematic-parity --severity-all --exit-code-violations`) with **zero unresolved errors, zero warnings, zero unconnected items, and zero schematic parity issues**:

| Board | ERC Violations | DRC Violations | Unconnected Items | Schematic Parity Issues | Report Paths |
|---|---|---|---|---|---|
| **Board 1 (`driver_pcb`)** | **0** | **0** | **0** | **0** | `pcb_design/driver_pcb/erc_report.{json,rpt}`, `drc_report.{json,rpt}` |
| **Board 2 (`led_mcpcb`)** | **0** | **0** | **0** | **0** | `pcb_design/led_mcpcb/erc_report.{json,rpt}`, `drc_report.{json,rpt}` |

### 71-RefDes & 36-Net Canonical Parity (`circuit_design/COMPONENT_IDS.csv` & `lepiled_schematic.cir`)
- **Board 1 Schematic (`driver_pcb.kicad_sch`):** Contains all **71 RefDes** (`61` On-PCB + `10` Off-Board `D1..D4`, `D5..D8`, `SW1`, `SW1_BOOT` marked `(on_board no) (in_bom yes) (dnp yes)` and wired cleanly to `J2`, `J3`, `J4`, and `SW1_MECH`) and all **36 canonical nets** (`CC1`, `CC2`, `DIM2_NET`, `EN1_NET`, `EN2_NET`, `FB1_NET`, `FB2_NET`, `GND`, `OVP_DRV`, `OVP_DRV_GATE`, `OVP_HYS`, `OVP_K`, `OVP_SENSE`, `Q1_GATE`, `Q2_BASE`, `Q3_BASE`, `Q3_EMIT`, `Q4_BASE`, `SW1_MECH`, `SW1_NODE`, `SW2_NODE`, `SW_UV_EN`, `UV_N1..N3`, `UV_RET`, `VBUS`, `VBUS_FUSED`, `VIN_PROT`, `VIS_N1..N3`, `VIS_RET`, `VOUT1`, `VOUT2`, `V_MID`).
- **Board 1 Layout (`driver_pcb.kicad_pcb`):** Places exact **61 On-PCB RefDes** across all **29 On-PCB nets** with verified pinouts (`U3` TL431AIDBZR `1=K, 2=REF, 3=A`; `D16` BAW56LT1G `1=K1, 2=K2, 3=A`; `D12` BAV70LT1G `1=A1, 2=A2, 3=K`; `Q1A/Q1B` DMG2305UX-7 `1=G, 2=S, 3=D`; `Q2/Q3/Q4` `1=B, 2=E, 3=C`; `U1/U2` LM3410XMY `1=NC, 2=PGND, 3=VIN, 4=DIM, 5=FB, 6=AGND, 7=SW, 8=NC, 9(DAP)=GND`; `J1` USB4085-GF-A 16+4 TH with `0.65 × 0.85 mm` oval signal pads giving `0.125 mm` X-ring and `0.200 mm` clearance per `usb4085.pdf`; `J2/J3` `1.0 mm` drill; `J4` `0.9 mm` drill).
- **Silkscreen Polarity & BOM Export Note:** `D13..D15` (`D_SOD-123`) carry `F.Silkscreen` cathode U-brackets around Pad 1 (Cathode); `J2`/`J3` bottom-side `B.Silkscreen` (`mirrored=True`) reads `"2:UV-  1:UV+"` and `"2:VIS-  1:VIS+"` aligned directly under Pad 2 (left, round) and Pad 1 (right, square) in bottom view, clear of `B.Cu` traces/pads. Note that `kicad-cli sch export bom` in KiCad 9 emits a benign annotation warning and appends `?` to canonical non-numeric-suffix RefDes (`Q1A`, `Q1B`, `SW1_BOOT`, `D_UV`, `D_VIS`); therefore `pcb_design/*_bom*.csv` are deterministically generated from `COMPONENT_IDS.csv` in `build_*.py` with exact 1:1 RefDes parity.

---

## 3. `INTERFACE_CONTRACT.md` Sec. 1.2 Measured Compliance Metrics (Board 1)

| Requirement (`INTERFACE_CONTRACT.md` Sec. 1.2) | Target / Limit | Measured on `driver_pcb.kicad_pcb` | Status |
|---|---|---|---|
| **KiCad Netclasses (`driver_pcb.kicad_pro` + `.kicad_dru`)** | `Power_5V ≥1.5 mm`, `Power_SW ≥1.0 mm / ≥0.25 mm clr`, `Power_HV ≥0.6 mm / ≥0.25 mm clr`, `Signal ≥0.25 mm / ≥0.20 mm clr` | Enforced in `.kicad_dru` (`>= 0.35 mm` fallback rules ordered first so `Power_5V ≥1.50 mm` outside `Sense_Tap_Area`/pad-exit courtyards and `Power_SW ≥1.00 mm` outside `U1`/`U2` courtyards execute cleanly; `Power_HV ≥0.60 mm`; `Signal ≥0.25 mm`; verified live via `/tmp` `0.35 mm` injection DRC test). `0` overlap between `>= 1.50 mm` `Power_5V` trunks and `Sense_Tap_Area`. Exposed neckdowns: `0.36 mm` stub on `SW1/SW2` (`0.312 mm` exposed), **`~0.42 mm` (`0.152 mm²`)** on `VIN_PROT` `U1.3/U2.3`, `~0.42–0.57 mm` on `J1` dual `VBUS` pins; `0` single-via `3.24 A` bottlenecks (`VBUS`/`VBUS_FUSED`/`VIN_PROT` & `Q1A.2->Q1B.2` `V_MID` routed `100%` on `F.Cu` with `0` power vias) | PASS |
| **`VOUT1` (`D9` cathode) thermal copper pour** | `≥ 100.0 mm²` (`1.0 cm²`) | **`130.25 mm²`** (`1.30 cm²` on `F.Cu`) | PASS |
| **`VOUT2` (`D10` cathode) thermal copper pour** | `≥ 100.0 mm²` (`1.0 cm²`) | **`131.50 mm²`** (`1.32 cm²` on `F.Cu`) | PASS |
| **`SW1_NODE` / `SW2_NODE` total copper area (union of pads + tracks + zones)** | `< 15.0 mm²` | **`13.53 mm²`** (`13.5345 mm²` `SHAPE_POLY_SET` union) for `SW1_NODE`, **`13.53 mm²`** (`13.5345 mm²`) for `SW2_NODE` (`SRN6045` `1.80×5.00 mm` + `B340A` `1.60×1.70 mm` + `U1.7`/`U2.7` + `1.00 mm` bridge; zero extra zone) | PASS |
| **`B.Cu` keepout directly under `SW1_NODE`/`SW2_NODE`** | Explicit `RULE_AREA` disallowing `B.Cu` copper/tracks/vias | 4 explicit `B.Cu` `RULE_AREA` zones covering 100% of `SW1_NODE` & `SW2_NODE` pads/tracks + margin; **`0.000000 mm²`** `B.Cu` copper overlap verified via both `pcbnew` `SHAPE_POLY_SET` and raw `driver_pcb-B_Cu.gbr` | PASS |
| **High-$di/dt$ switching loop perimeters (closed Euclidean pad-center)** | HF Input `< 8.0 mm`; HF Output minimized for `SMA` + `0603` + `MSOP-8` | Ch1 HF input (`C7-U1.3-U1.2-C7`): **`5.877 mm`**; Ch2 HF input (`C8-U2.3-U2.2-C8`): **`5.877 mm`**; Ch1/Ch2 bulk input (`C2/C3`): **`12.133 mm`**; Ch1 HF output (`U1.7-D9-C9-DAP-U1.7`): **`16.945 mm`**; Ch2 HF output (`U2.7-D10-C10-DAP-U2.7`): **`16.945 mm`**; Ch1/Ch2 bulk output (`C4/C5`): **`25.668 / 25.508 mm`**; open SW path (`U1.7->D9.2->L1.2` / `U2.7->D10.2->L2.2`): **`5.296 mm`** | PASS |
| **Kelvin `FB` & `AGND`/`PGND` star** | `U1.5->R8/D13`, `R3.2->U1.6->DAP` isolated from `C2/C4` `PGND` | Dedicated Kelvin traces (`R3.2->U1.DAP/U1.6`, `R4.2->U2.DAP/U2.6`) separated from `C7/C2/C9/C4` & `C8/C3/C10/C5` `PGND` switching return vias | PASS |
| **`U1`/`U2` `DAP` thermal vias** | `4–6×` `0.30/0.60 mm` vias to `B.Cu` `GND` | **`6×`** `0.30 mm` drill / `0.60 mm` pad vias strictly inside `U1.DAP` and **`6×`** strictly inside `U2.DAP` (inside both `3.00×2.00 mm` copper and `2.00×1.88 mm` mask/paste bounds) | PASS |
| **`Q1A`/`Q1B` pours & protection placement** | Generous `VBUS_FUSED`/`V_MID` pours; `C12/R1/R2` at `J1`; `D11` downstream on `VIN_PROT`; `TP1/TP2` `2.5/1.3 mm` near `J1` | All verified on `driver_pcb.kicad_pcb` (`VBUS_FUSED = 25.69 mm²`, `V_MID = 6.26 mm²` continuous `F.Cu` `Q1A.2->Q1B.2` pour, `TP1` at `(-8.2, -19.5)`, `TP2` at `(+8.2, -19.5)`) | PASS |

---

## 4. Board 2 (`led_mcpcb`, `MECH-MCPCB-1..4`) Compliance Summary

- **1-Layer Strictly Enforced:** `pcb_design/gerbers/led_mcpcb/` contains ONLY `F_Cu`, `F_Mask`, `F_Paste`, `F_Silkscreen`, `Edge_Cuts`, `NPTH.drl` (`2× 3.20 mm` holes at `(0, ±32.0)`), `drill.rpt` (`Total plated holes count 0`), and `.gbrjob`. **Zero `B_Cu`, zero `B_Mask`, zero `PTH` drill files.** *(Note: `led_mcpcb-job.gbrjob` contains KiCad 9's default 2-layer/`FR4` stackup boilerplate because KiCad clamps `SetCopperLayerCount()` internally to 2; fabrication houses should build to the 1-layer `1.0 W/m·K` Al MCPCB Gerber set.)*
- **LED Placement & Opposite Notch Cues:**
  - `D_UV` (`Luminus SST-10-UV-A130-G365-00`) at `(0, +18.0) mm`: Anode left (`-1.385`), Cathode right (`+1.385`), exposed thermal pad SMD-masked strictly to `1.30 × 3.25 mm`, electrically isolated thermal copper wing **`492.5 mm²`**, silkscreen marked `A+`, `K-`, and `BTM NOTCH=K`.
  - `D_VIS` (`Cree XP-E2`: 2× RB, 1× GR, 1× CW across 4 strips) at `(0, -18.0) mm`: Anode left (`-1.40`), Cathode right (`+1.40`), exposed thermal pad SMD-masked strictly to `1.30 × 3.30 mm`, electrically isolated thermal copper wing **`279.1 mm²`**, silkscreen marked `A+`, `K-`, and `BTM NOTCH=A`.
- **Wire Solder Pads:** `UV+`, `VIS+`, `VIS-`, `UV-` (`2.5 × 3.5 mm` SMD pads) at `(-6.75, -26.0)`, `(-2.25, -26.0)`, `(+2.25, -26.0)`, `(+6.75, -26.0) mm` (`≥ 1.37 mm` clear outside `MH2` `Ø 6.0 mm` keepout).

---

## 5. Manufacturing Output Manifest

### Gerber & Drill Packages
- **Board 1 (`pcb_design/gerbers/driver_pcb/`):** `driver_pcb_gerbers.zip` containing `driver_pcb-F_Cu.gbr`, `driver_pcb-B_Cu.gbr`, `driver_pcb-F_Mask.gbr`, `driver_pcb-B_Mask.gbr`, `driver_pcb-F_Silkscreen.gbr`, `driver_pcb-B_Silkscreen.gbr`, `driver_pcb-F_Paste.gbr`, `driver_pcb-Edge_Cuts.gbr`, `driver_pcb-PTH.drl`, `driver_pcb-NPTH.drl`, `driver_pcb-job.gbrjob` (plus drill maps & `driver_pcb-drill.rpt`).
- **Board 2 (`pcb_design/gerbers/led_mcpcb/`):** `led_mcpcb_gerbers.zip` containing `led_mcpcb-F_Cu.gbr`, `led_mcpcb-F_Mask.gbr`, `led_mcpcb-F_Silkscreen.gbr`, `led_mcpcb-F_Paste.gbr`, `led_mcpcb-Edge_Cuts.gbr`, `led_mcpcb-NPTH.drl`, `led_mcpcb-job.gbrjob` (plus `NPTH-drl_map.pdf` & `led_mcpcb-drill.rpt`).

### Pick-and-Place CPL & BOMs (`pcb_design/`)
- `pcb_design/driver_pcb_cpl.csv` — 57 placed On-PCB parts (`61` minus `4×` `H1..H4` mounting holes) in JLCPCB format (`Designator,Mid X,Mid Y,Layer,Rotation`).
- `pcb_design/driver_pcb_bom.csv` — Complete 71-RefDes BOM matching `circuit_design/COMPONENT_IDS.csv` 1:1 with `Mounting` and `DNP` flags (`61` `On-PCB` + `10` `Off-Board`).
- `pcb_design/driver_pcb_bom_pcba.csv` — 61 On-PCB parts only (`DNP=No`) for PCB assembly.
- `pcb_design/led_mcpcb_cpl.csv` — `D_UV` `(0.000, 18.000)` & `D_VIS` `(0.000, -18.000)`.
- `pcb_design/led_mcpcb_bom.csv` — `D_UV` & `D_VIS` per-strip and 4× lamp quantities.

### Visual Verification Renders
- Board 1 (`pcb_design/driver_pcb/renders/`): `schematic.pdf`, `board.svg`, `render_top.png`, `render_bottom.png`, `gerbv_top.png`, `gerbv_bottom.png`.
- Board 2 (`pcb_design/led_mcpcb/renders/`): `schematic.pdf`, `board.svg`, `render_top.png`, `gerbv_top.png`.

---

## 6. M2 ↔ M3 Mechanical Cross-Check Notes (For M3/M4/M5)
- **Primary Baseline (`M16_GLAND` via `TP1`/`TP2`):** `J1` remains at `(0.0, -18.50) mm` (`2.34 mm` overhang past `y = -23.00 mm` PCB edge), compatible with `mechanical_design/cad/mech_cap_bot.stl` and `adapt_bot.stl` (`0` collisions, `≥ 5.16 mm` radial / `≥ 7.98 mm` vertical margins).
- **Option B (`USB_C`, `mech_cap_bot_usbc.stl`) Plug-Reach Caveat:** Challenger 2 STL ray-casting noted that `mech_cap_bot_usbc` places the external USB-C cable overmold stop at `Y = -33.50 mm` (`8.16 mm` from `J1` front face at `Y = -25.34 mm`), whereas a standard USB-C plug barrel is `6.65 mm` long per `datasheets/usb4085.pdf` p. 2 (`1.51 mm` short of contact). M3/M4/M5 should recess the `mech_cap_bot_usbc` bezel overmold pocket inward by `≥ 4.5 mm` (to `Y ≈ -28.0 mm`) or specify an extended-barrel USB-C cable for Option B.
