# Interface Contract (Rev 4.9) — Electronics ↔ PCB & Mechanical / Thermal

**Canonical Registry:** [COMPONENT_IDS.csv](COMPONENT_IDS.csv) (**72 unique RefDes:** `54` PCBA = `41` JLCPCB SMD [20 Basic + 2 Extended] + `11` DIY [`4` THT `J1..J4` + `7` chunky 2-pad SMDs] + `2` DNP `D13/D14`; `4` Isolated `M3` NPTH `H1..H4`; `4` Bare HASL Test Pads `TP1..TP4`; `10` Off-Board = `8×` Convoy `20 mm` Cu DTP LED stars + `SW1` + `SW1_BOOT`)
**Datasheet Source of Truth:** [datasheets_summary.json](../datasheets/datasheets_summary.json)
**Simulation Verification:** [sim_summary.json](sim/outputs/sim_summary.json)
**CAD Parameter SSOT:** [cad_params.json](../mechanical_design/cad/cad_params.json)

---

## 1. Electronics ↔ PCB Design & Manufacturing Contract

### 1.1 Physical Board Envelope & Unified `M3` Mounting Holes
- **Single Custom PCB (`driver_pcb`):** **`36.0 mm × 46.0 mm`**, 2-layer `1.6 mm` FR4, `2.0 mm` corner radii, 1 oz Cu, **Lead-Free HASL** finish, Green LPI (`min_solder_mask_bridge >= 0.10 mm`) / White silk.
  - SMD power/signal envelope: `<= 4.5 mm` (`L1`/`L2` `Bourns SRN6045-680M` = `4.5 mm` max; `J1` `USB4085-GF-A` = `3.46 mm`).
  - Through-hole wire headers `J2..J4` (`JST B2B-XH-A` / `B3B-XH-A`, `1.00 mm` drills, mated via pre-crimped `22 AWG` JST-XH pigtails): `7.0 mm` unmated (`9.8 mm` mated).
  - **Unified `M3` Mounting Holes (`H1..H4`):** `4× M3` **unplated isolated NPTH** (`Ø3.2 mm` drill, **`r = 3.10 mm` (`Ø6.20 mm`) `F.Cu` + `B.Cu` copper keepouts** verified directly on exported RS-274X Gerbers: `F_Cu >= 3.609 mm`, `B_Cu >= 3.085 mm`) at `(±14.0, ±19.0) mm`, bolting horizontally (**`F.Cu` SMD/JST-side UP!**) onto `MECH-LID-BOT`'s `4×` integral `M3 × 5.0` brass-insert standoffs (`Ø7.0 → Ø6.0 mm`) via `4×` `M3 × 8 mm` CSK screw + `M3` steel flat washer + `Ø7.0 × 0.8 mm` DIN 125 nylon insulating washer.
  - **Bench Test Pads (`TP1..TP4`):** Four bare `1.0 mm` HASL `F.Cu` pads (`VIN_20V`, `V_REF`, `UVLO_OK`, `GND`) on top-facing `F.Cu` alongside `D12` for open-air bench bring-up.
- **Off-Board LEDs (`8×` Convoy `20 mm` Cu DTP Stars):** `4×` UV-A (`Luminus SST-10-UV`, `Z = 149.5 mm`) and `4×` Visible (`ams OSRAM CSLNM1`, `Z = 115.5 mm`, **`34.0 mm` vertical pitch**; Royal Blue `KB CSLNM1.14` on opposite Faces 1 `+X` & 3 `-X`, Pure Green `KP CSLNM1.F1` on Face 2 `+Y`, Cool White `KW CSLNM1.TG` on Face 4 `-Y`) edge-clamped onto bare mill-aluminum faces of `MECH-HS-CORE` at `R = 11.7 mm` (`23.4 mm` bolt pitch) using `16×` `M3 × 8 mm` CSK screws + `M3` steel flat washers + `Ø7.0 mm` DIN 125 nylon insulating washers.

### 1.2 Copper, Stackup & Layout Design Rules (`driver_pcb`)
- **Zero Unplugged Via-in-Pad:** Every via clears every SMD pad by `>= 0.25 mm` (`51` vias / `130` SMD pads, `0` violations). `U3` (`WCH CH224A` `ESSOP-10`) `2.10 × 3.30 mm` EPAD uses segmented paste and perimeter `0.30/0.60 mm` `GND` vias.
- **Unbroken `B.Cu` Ground Plane Under Power Stage:** Continuous solid `GND` plane beneath `U1`, `U2`, `D9`, `D10`, `L1`, `L2`, `R3`, `R4`, `C2`, `C3`, `C8`, `C9` (`0` non-GND segments inside `Y = [4.3, 16.5] mm`).
- **Trace Widths & High-$di/dt$ Loops (`20 V` Bus, `0.453 A` nom / `0.573 A` max):**
  - `VBUS`, `VIN_20V`: `>= 0.80 mm` (`1.00 mm` trunk). Zero-stub fly-by routing from `F1` (`1206`) directly across `D11` (`SMBJ22A`) into `R7` (`2512`) / `C10` (`1206`) / `C11`.
  - Buck hot loops (`C2/C8 -> R3 -> UV_POS`, `D9 -> VIN_20V`, `SW1_NODE -> L1` and Ch2 mirror): `>= 0.60 mm`, `< 10 mm` perimeter on `F.Cu`, with true Kelvin `VIN` and `SET` taps at `R3`/`R4`.
- **Footprint & PCBA Accuracy:**
  - `J1` (`GCT USB4085-GF-A`): `Ø0.40 mm` signal drills (`0.65 × 0.90 mm` oval pads), full-connection GND pins tied to `SH1/SH2`, `Y_mouth = -26.18 mm` (board coords).
  - `D13`/`D14` (`D_SOD-323_DNP`): paste-free DNP footprints (`0` apertures in `F_Paste.gbr`, `SetDNP(True)`).
  - `driver_pcb_bom_pcba_hybrid.csv` and `driver_pcb_cpl_hybrid.csv` contain **`41` JLCPCB SMDs** (`20` Basic + `2` Extended); `driver_pcb_diy_hand_solder.csv` contains `11` DIY Farnell UK parts (`J1..J4` THT + `F1`, `D11`, `L1/L2`, `R3/R4`, `R7`) + `D13/D14` DNP; `H1..H4` and `TP1..TP4` are excluded from PCBA.

---

## 2. Electronics ↔ Mechanical & Thermal Contract

### 2.1 Thermal Dissipation Budget (SSOT-Coupled to `sim_summary.json` & `cad_params.json`)
Nominal drive current = **`333 mA`** (`R3 = R4 = 0.30 Ω ±1%`), supplied from **`20.0 V` USB-C PD** (`I_in = 0.453 A` / `9.06 W` nominal; `0.573 A` worst-case corner; **`94.1%`** system efficiency).

| Subsystem | `8-ALL` Electrical (W) | `8-ALL` Nom Heat (`40%` UV WPE) | `8-ALL` Worst-Case (`DS-RealWPE`) | `4-UV` Nom Heat | Thermal Limit |
|---|---|---|---|---|---|
| **Ch1 UV Array (`4× SST-10-UV`, `D1..D4`)** | `4.736 W` | **`2.842 W`** | `3.650 W` | **`2.842 W`** | $T_{j,\max} = 100^\circ\text{C}$ ($R_{\theta Js}=1.4^\circ\text{C/W}$) |
| **Ch2 Visible Array (`4× OSRAM CSLNM1`, `D5..D8`)** | `3.784 W` | **`2.270 W`** | `2.950 W` | `0.000 W` | $T_{j,\max} = 150^\circ\text{C}$ ($R_{\theta Js}=4.1\text{–}4.9^\circ\text{C/W}$) |
| **Interior Optical Re-Absorption (`~14%`)** | — | **`0.477 W`** | `0.450 W` | **`0.265 W`** | Split 50% core / 50% XT PMMA wall |
| **`U1`/`U2` (`AL8860WT-7`) + Buck Passives** | `0.352 W` | **`0.352 W`** | `0.582 W` | `0.165 W` | $T_{j,\max} = 125^\circ\text{C}$ derated |
| **`U3`/`U4`/`U5`/`F1`/`D12`/Quiescent Overhead** | `0.156 W` | **`0.156 W`** | `0.260 W` | `0.156 W` | `U4/U5` commercial `0..+70 °C` bay air |
| **Driver PCB Total Loss (`sim_summary.json`)** | **`0.508 W`** | **`0.508 W`** | **`0.842 W`** | **`0.321 W`** | Unpainted Al: `T_bay = 51.0 / 58.8 / 67.5 °C <= 70 °C`; `T_pcb = 57.8 / 65.6 / 78.9 °C` (`<=75 °C` PETG nom & `22 °C` WC; `<=95 °C` ASA) |

### 2.2 Mechanical Interface Datums (Synced with `mechanical_design/cad/cad_params.json` Rev 4.9)
- **Serviceable Lid-Mounted `driver_pcb` (`F.Cu` SMD/JST-Side UP!):** `36 × 46 × 1.6 mm` `driver_pcb` bolts onto `4×` integral `M3 × 5.0` brass-insert standoffs rising UP from `MECH-LID-BOT` (`B.Cu` at `Z = 46.5 mm`, `F.Cu` at `Z = 48.1 mm`, `Y_ctr = +7.3 mm`) inside an unobstructed straight **`Ø71.6 mm`** bore in `MECH-CAP-BOT` (`Z = 0..89.5 mm`, `Ø94.4 → Ø74.0 mm`). `J1` (`Y_mouth = -18.88 mm, Z_ctr = 49.98 mm`) mates in **open air on the bench** to a realistic **`15.0 mm`** `90°`-down USB-C PD plug + `7.0 mm` strain relief before sliding the entire lid+PCB+plug straight up in one vertical stroke (`0.000 mm³` kinematic clearance!).
- **Recessed `8.5 mm` Lid, Blind Conical Cable Clamp, Real `18.6 mm` `SW1` Boot & Cut Vent Pocket:** `MECH-LID-BOT` (`Ø87.6 × 8.5 mm`, `Z = 22.0..30.5 mm`, flush `90°` CSK seats at `R = 40.0 mm`) sits inside a deepened `22.0 mm` skirt (shielding real `18.6 mm` `SW1` boot by `3.4 mm` with intact `0/1/2` ribs at `Z = 13.0..19.5 mm`), seals radially via **`MECH-GASKET-3` (`68 × 2.5 mm` VMQ70)**, and clamps the USB-C cable via `2×` flush-CSK conical-wedge `MECH-CABLE-CLAMP` halves compressing `MECH-GROMMET-1` radially using **`2× M3×12` CSK screws into blind standard `M3×5.0` inserts (`1.50 mm` solid roof into dry bay)**. `MECH-VENT-1` seats inside a cut `Ø9.5 × 0.8 mm` recessed pocket on the inside lid face (`(-21.5, 0.0 mm)`).
- **Staggered Core Anchor, XT PMMA Shroud & Sealed Lofted Collar:** `MECH-HS-CORE` (`30 × 30 × 3.0 × 200.0 mm`, `Z = 69.0..269.0 mm`, **unpainted bare mill aluminum**) locks internally via staggered `MECH-CORE-ANCHOR` (`±Y` vertical flush `M3×12` CSK bolts at `(0, ±6.5 mm)` + `±X` flush `M3×8` CSK cross-pins at `Z_rel = 13.0 mm`). Extruded clear XT PMMA shroud (`Ø60 × 54 × 3.0 × 115 mm`, `Z = 75.0..190.0 mm`) seals on `60 × 3.5 mm` VMQ50/60 radial O-rings. `MECH-CAP-TOP` adds a **`9.5 mm` vertical `40.4 × 40.4 mm` collar** above the `24.6°` rain roof (`Z = 201.0..210.5 mm`) so `2× M3×10` CSK lock screws (+ steel washers) bear flat on `4.65 mm` vertical walls (`5.1 mm` above internal cone, `1.16 mm` below `Soudal Fix ALL Crystal` top groove — **zero roof holes!**). Total height: **`277.0 mm` body / `318.3 mm` w/ wire bail**.
