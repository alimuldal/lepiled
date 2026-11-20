# Interface Contract (Rev 4.8) — Electronics ↔ PCB & Mechanical / Thermal

**Canonical Registry:** [COMPONENT_IDS.csv](COMPONENT_IDS.csv) (**72 unique RefDes:** `54` PCBA = `48` JLCPCB SMD [20 Basic + 7 Extended] + `4` THT `J1..J4` + `2` DNP `D13/D14`; `4` Isolated NPTH `H1..H4`; `4` Bare ENIG Test Pads `TP1..TP4`; `10` Off-Board = `8×` `20 mm` LED stars + `SW1` + `SW1_BOOT`)
**Datasheet Source of Truth:** [datasheets_summary.json](../datasheets/datasheets_summary.json)
**Simulation Verification:** [sim_summary.json](sim/outputs/sim_summary.json)
**CAD Parameter SSOT:** [cad_params.json](../mechanical_design/cad/cad_params.json)

---

## 1. Electronics ↔ PCB Design & Manufacturing Contract

### 1.1 Physical Board Envelope & Mounting Holes
- **Single Custom PCB (`driver_pcb`):** **`36.0 mm × 46.0 mm`**, 2-layer `1.6 mm` FR4, `2.0 mm` corner radii, 1 oz Cu, **ENIG** finish, Green LPI (`min_solder_mask_bridge >= 0.10 mm`) / White silk.
  - SMD power/signal envelope: `<= 4.5 mm` (`L1`/`L2` `Sunlord SWPA6045S680MT` = `4.5 mm` max; `J1` `USB4085-GF-A` = `3.46 mm`).
  - Through-hole wire headers `J2..J4` (`JST B2B-XH-A` / `B3B-XH-A`, `1.00 mm` drills, mated via pre-crimped `22 AWG` JST-XH pigtails): `7.0 mm` unmated (`9.8 mm` mated).
  - **Mounting Holes (`H1..H4`):** `4× M2.5` **unplated isolated NPTH** (`Ø2.7 mm` drill, **`r = 2.80 mm` (`Ø5.60 mm`) `F.Cu` + `B.Cu` copper keepouts** verified directly on exported RS-274X Gerbers) at `(±14.0, ±19.0) mm`, bolting horizontally (**`F.Cu` SMD/JST-side UP!**) onto `MECH-LID-BOT`'s `4×` integral `M2.5` brass-insert standoffs via `4× M2.5 × 6 mm` **nylon** pan-head screws.
  - **Bench Test Pads (`TP1..TP4`):** Four bare `1.0 mm` ENIG `F.Cu` pads (`VIN_20V`, `V_REF`, `UVLO_OK`, `GND`) on top-facing `F.Cu` alongside `D12` for open-air bench bring-up.
- **Off-Board LEDs (`8×` `20 mm` Stars):** `4×` UV-A (`SST-10-UV`, `Z = 148.5 mm`) and `4×` Visible (`Cree XP-E2`, `Z = 114.5 mm`, **`34.0 mm` vertical pitch**; Royal Blue on opposite Faces 1 `+X` & 3 `-X`, Green on Face 2 `+Y`, Cool White on Face 4 `-Y`) edge-clamped onto bare mill-aluminum faces of `MECH-HS-CORE` at `R = 11.7 mm` (`23.4 mm` bolt pitch) using `16× M3 × 8 mm` pan screws + `16× M3` DIN 125 (`Ø7.0 mm`) nylon insulating washers.

### 1.2 Copper, Stackup & Layout Design Rules (`driver_pcb`)
- **Zero Unplugged Via-in-Pad:** Every via clears every SMD pad by `>= 0.25 mm` (`51` vias / `130` SMD pads, `0` violations). `U3` (`WCH CH224A` `ESSOP-10`) `2.10 × 3.30 mm` EPAD uses segmented paste and perimeter `0.30/0.60 mm` `GND` vias.
- **Unbroken `B.Cu` Ground Plane Under Power Stage:** Continuous solid `GND` plane beneath `U1`, `U2`, `D9`, `D10`, `L1`, `L2`, `R3`, `R4`, `C2`, `C3`, `C8`, `C9` (`0` non-GND segments inside `Y = [4.3, 16.5] mm`).
- **Trace Widths & High-$di/dt$ Loops (`20 V` Bus, `0.454 A` nom / `0.581 A` max):**
  - `VBUS`, `VIN_20V`: `>= 0.80 mm` (`1.00 mm` trunk). Zero-stub fly-by routing from `F1` (`1206`) directly across `D11` (`SMBJ22A`) into `R7` (`2512`) / `C10` (`1206`) / `C11`.
  - Buck hot loops (`C2/C8 -> R3 -> UV_POS`, `D9 -> VIN_20V`, `SW1_NODE -> L1` and Ch2 mirror): `>= 0.60 mm`, `< 10 mm` perimeter on `F.Cu`, with true Kelvin `VIN` and `SET` taps at `R3`/`R4`.
- **Footprint & PCBA Accuracy:**
  - `J1` (`GCT USB4085-GF-A`): `Ø0.40 mm` signal drills (`0.65 × 0.90 mm` oval pads), full-connection GND pins tied to `SH1/SH2`, `Y_mouth = -26.18 mm` (board coords).
  - `D13`/`D14` (`D_SOD-323_DNP`): paste-free DNP footprints (`0` apertures in `F_Paste.gbr`, `SetDNP(True)`).
  - `driver_pcb_cpl.csv` and `driver_pcb_cpl_hybrid.csv` contain **all `48` populated SMDs**; `driver_pcb_diy_hand_solder.csv` contains only `J1..J4` THT + `D13/D14` DNP; `H1..H4` and `TP1..TP4` are excluded from PCBA.

---

## 2. Electronics ↔ Mechanical & Thermal Contract

### 2.1 Thermal Dissipation Budget (SSOT-Coupled to `sim_summary.json` & `cad_params.json`)
Nominal drive current = **`333 mA`** (`R3 = R4 = 0.30 Ω ±1%`), supplied from **`20.0 V` USB-C PD** (`I_in = 0.454 A` / `9.08 W` nominal; `0.581 A` worst-case corner; **`94.1%`** system efficiency).

| Subsystem | `8-ALL` Electrical (W) | `8-ALL` Nom Heat (`40%` UV WPE) | `8-ALL` Worst-Case (`DS-RealWPE`) | `4-UV` Nom Heat | Thermal Limit |
|---|---|---|---|---|---|
| **Ch1 UV Array (`4× SST-10-UV`, `D1..D4`)** | `4.736 W` | **`2.842 W`** | `3.650 W` | **`2.842 W`** | $T_{j,\max} = 100^\circ\text{C}$ ($R_{\theta Js}=1.4^\circ\text{C/W}$) |
| **Ch2 Visible Array (`4× XP-E2`, `D5..D8`)** | `3.801 W` | **`2.281 W`** | `2.950 W` | `0.000 W` | $T_{j,\max} = 150^\circ\text{C}$ ($R_{\theta Js}=5.7\text{–}9.0^\circ\text{C/W}$) |
| **Interior Optical Re-Absorption (`~14%`)** | — | **`0.478 W`** | `0.450 W` | **`0.265 W`** | Split 50% core / 50% `0A070` PMMA wall |
| **`U1`/`U2` (`AL8860WT-7`) + Buck Passives** | `0.356 W` | **`0.356 W`** | `0.590 W` | `0.168 W` | $T_{j,\max} = 125^\circ\text{C}$ derated |
| **`U3`/`U4`/`U5`/`F1`/`D12`/Quiescent Overhead** | `0.156 W` | **`0.156 W`** | `0.260 W` | `0.156 W` | `U4/U5` commercial `0..+70 °C` bay air |
| **Driver PCB Total Loss (`sim_summary.json`)** | **`0.512 W`** | **`0.512 W`** | **`0.850 W`** | **`0.324 W`** | `T_bay = 47.3 / 54.9 / 62.8 °C <= 70 °C`; `T_pcb = 54.2 / 61.8 / 74.2 °C <= 75 °C` PETG (`95 °C` ASA) |

### 2.2 Mechanical Interface Datums (Synced with `mechanical_design/cad/cad_params.json` Rev 4.8)
- **Serviceable Lid-Mounted `driver_pcb` (`F.Cu` SMD/JST-Side UP!):** `36 × 46 × 1.6 mm` `driver_pcb` bolts onto `4×` integral `M2.5` brass-insert standoffs rising UP from `MECH-LID-BOT` (`B.Cu` at `Z = 45.5 mm`, `F.Cu` at `Z = 47.1 mm`, `Y_ctr = +7.3 mm`) inside an unobstructed straight **`Ø71.6 mm`** bore in `MECH-CAP-BOT` (`Z = 0..88.5 mm`, `Ø92.4 → Ø74.0 mm`). `J1` (`Y_mouth = -18.88 mm, Z_ctr = 48.98 mm`) mates in **open air on the bench** to a realistic **`15.0 mm`** `90°`-down USB-C PD plug + `7.0 mm` strain relief before sliding the entire lid+PCB+plug straight up in one vertical stroke (`0.000 mm³` kinematic clearance!).
- **Recessed Lid, Blind Conical Cable Clamp, Real `18.6 mm` `SW1` Boot & Cut Vent Pocket:** `MECH-LID-BOT` (`Ø85.6 × 7.5 mm`, `Z = 22.0..29.5 mm`) sits inside a deepened `22.0 mm` skirt (shielding real `18.6 mm` `SW1` boot by `3.4 mm` with intact `0/1/2` ribs at `Z = 13.0..19.5 mm`), seals radially via **`MECH-GASKET-3` (`68 × 2.5 mm` VMQ70)**, and clamps the USB-C cable via `2×` conical-wedge `MECH-CABLE-CLAMP` halves compressing `MECH-GROMMET-1` radially using **`2× M3×12` SHCS into blind `M3×4` inserts (`1.50 mm` solid roof into dry bay)**. `MECH-VENT-1` seats inside a cut `Ø9.5 × 0.8 mm` recessed pocket on the inside lid face (`(-21.5, 0.0 mm)`).
- **Staggered Core Anchor, `0A070` PMMA Shroud & Sealed Lofted Collar:** `MECH-HS-CORE` (`30 × 30 × 3.0 × 200.0 mm`, `Z = 68.0..268.0 mm`, **top `58.5 mm` chimney ONLY matte black**) locks internally via staggered `MECH-CORE-ANCHOR` (`±Y` vertical `M3×12` bolts at `(0, ±6.5 mm)` + `±X` flush `M3×8` CSK cross-pins at `Z_rel = 13.0 mm`). `PLEXIGLAS® XT Clear 0A070` shroud (`Ø60 × 54 × 3.0 × 115 mm`, `Z = 74.0..189.0 mm`) seals on `60 × 3.5 mm` VMQ50/60 radial O-rings. `MECH-CAP-TOP` adds a **`9.5 mm` vertical `40.4 × 40.4 mm` collar** above the `24.6°` rain roof (`Z = 200.0..209.5 mm`) so `2× M3×10` lock screws bear flat on `4.65 mm` vertical walls (`5.1 mm` above internal cone, `1.16 mm` below `OTTOSEAL S 72` top groove — **zero roof holes!**). Total height: **`276.0 mm`**.
