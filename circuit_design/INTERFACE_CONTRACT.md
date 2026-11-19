# Interface Contract (Rev 4.0 / Option 2) — Electronics ↔ PCB & Mechanical / Thermal

**Canonical Registry:** `circuit_design/COMPONENT_IDS.csv` (**72 unique RefDes:** 62 On-PCB, 10 Off-Board)
**Datasheet Source of Truth:** `datasheets/datasheets_summary.json`
**Simulation Verification:** `circuit_design/sim/outputs/sim_summary.json`

---

## 1. Electronics ↔ PCB Design & Manufacturing Contract

### 1.1 Physical Board Envelope & Mounting Holes
- **Board Dimensions:** **`36.0 mm × 46.0 mm`**, 2-layer `1.6 mm` FR4, `2.0 mm` corner radii (`diagonal = 58.4 mm`, preserving 100% compatibility with the `MECH-CAP-BOT` cavity and `MECH-ADAPT-BOT` pedestal).
- **Solder Mask & Finish:** **Green LPI** (`min_solder_mask_bridge >= 0.10 mm`, `solder_mask_expansion = 0.04–0.05 mm`) with Lead-Free HASL or ENIG.
- **Component Heights above PCB Top:**
  - SMD power/signal envelope: `<= 4.5 mm` (`L1`/`L2` `SRN6045-680M` = `4.5 mm` max; `J1` `USB4085-GF-A` = `3.46 mm`).
  - Through-hole wire headers `J2..J4` (`JST B2B-XH-A` / `B3B-XH-A`, **`1.00 mm` drill on all three**): `7.0 mm` unmated (`9.8 mm` mated).
- **Mounting Holes (`H1..H4`):** `4× M2.5` plated/GND-tied holes (`2.7 mm` drill, `5.5 mm` pad/nut keepout) centered at `(±14.0, ±19.0) mm`.

### 1.2 Copper, Stackup & Layout Design Rules (Option 2 + Carbon Review Hardening)
- **Copper Weight:** `1 oz` (`35 µm`) outer layers.
- **Zero Unplugged Via-in-Pad:** Every via MUST sit outside every SMD pad copper `+ 0.25 mm` solder-mask dam (`"pth_inside_courtyard": "error"` and `.kicad_dru` hole-to-SMD clearance `>= 0.25 mm`). `U3` (`W-DFN3030-14`) EPAD connects to `U3.5` (`GND`) on `F.Cu` and fans out outside the `3.0 × 3.0 mm` courtyard to `0.30/0.60 mm` `GND` vias.
- **Solid Unbroken `B.Cu` Ground Plane:** Keep `B.Cu` a continuous `GND` reference plane beneath `U1`, `U2`, `U3`, `Q1A/Q1B`, and `C2/C3/C8/C9`. Avoid slicing `B.Cu` under switching loops.
- **Trace Widths & Clearances (`20 V` Bus, `0.46 A` nom / `0.58 A` max):**
  - `VBUS`, `VBUS_FUSED`, `VBUS_SENSE`, `Q1_MID`, `VIN_20V`, `AUX_IN`, `AUX_FUSED`: **`>= 0.80 mm`** (`1.00 mm` trunk preferred; `0.35 mm` pad-exit allowed at `J1`/`U3`/`Q1A`/`Q1B`).
  - High-$di/dt$ buck loops (`C2/C8 -> R3 -> UV_POS`, `D9 -> VIN_20V`, `SW1_NODE -> L1` and Ch2 mirror): **`>= 0.60 mm`** (`0.35 mm` pad-exit at `TSOT25`), kept compact (`< 10 mm`).
  - `UV_POS`, `UV_NEG`, `VIS_POS`, `VIS_NEG` (`333 mA` DC): **`>= 0.50 mm`**, clearance **`>= 0.25 mm`**.
  - Signal nets (`CC1`, `CC2`, `U3_*`, `Q1_GATE`, `V_REF`, `UVLO_SENSE`, `V_SW_BIAS`, `SW_UV_N`, `SW_ALL_N`, `U1_CTRL`, `U2_CTRL`, `PD_LED_A`): **`>= 0.20 mm`** (`0.25 mm` default).
- **Kelvin Sense Routing:**
  - `U3.ISENP` (Pin 4) taps the upstream (`VBUS_FUSED`) pad of `R8` (`5 mΩ`); `U3.VCC` (Pin 3) taps the downstream (`VBUS_SENSE`) pad of `R8`.
  - `U1.SET` (Pin 4) taps the `UV_POS` pad of `R3` (`0.30 Ω`), `U1.VIN` (Pin 5) taps the `VIN_20V` pad of `R3`; same for `U2` / `R4`.
- **Footprint Accuracy (Per Review Findings):**
  - `J1` (`GCT USB4085-GF-A`): `0.35 mm` finished signal drill (`0.150 mm` X annular ring), `7.26 mm` Row-B-to-front-mouth datum (`Y_mouth = -25.76 mm`), full `F.CrtYd` over the shell.
  - `J4` (`JST B3B-XH-A`): **`1.00 mm`** drill (`1.80 × 2.10 mm` oval pads), silkscreen pin legend `1:UV 2:GND 3:ALL`.
  - `L1`/`L2` (`Bourns SRN6045-680M`): datasheet `2.00 × 6.00 mm` pads at `±2.15 mm`.
  - `U3` (`W-DFN3030-14`): `0.22 mm` pad width (`0.40 mm` pitch -> `0.18 mm` copper gap -> `>= 0.10 mm` Green LPI solder mask dam with `0.04 mm` local mask expansion).
  - Full `F.Silkscreen` RefDes on all populated parts (`>= 0.80 mm` height, `>= 0.15 mm` stroke, `>= 0.15 mm` mask clearance) + 2:1 `F.Fab` assembly map PDF.
  - `TP1`, `TP2`, `H1..H4` excluded from Pick-and-Place CPL and PCBA BOM.

### 1.3 RefDes Parity Rule (On-PCB vs Off-Board)
- **62 On-PCB parts:** `U1..U5`, `Q1A..Q1B`, `Q2..Q3`, `F1..F2`, `D9..D15`, `L1..L2`, `R1..R17`, `C1..C15`, `J1..J4`, `TP1..TP2`, `H1..H4`.
- **10 Off-Board parts:** `D1..D4` (via `J2`), `D5..D8` (via `J3`), `SW1` (via `J4`), `SW1_BOOT`.

---

## 2. Electronics ↔ Mechanical & Thermal Contract

### 2.1 Thermal Dissipation Budget (Fanless Sizing — Option 2)
Nominal steady-state drive current = **`333 mA`** (`V_SENSE = 100 mV`, `R3 = R4 = 0.30 Ω ±1%`).
Input supply: **`20.0 V` USB-C PD** (`>= 45 W` laptop charger or `20 V` PD power bank, `I_in = 0.45–0.46 A` nominal, `<= 0.58 A` worst-case corner) OR raw **`18–24 V` DC** on `TP1`/`TP2`.

| Subsystem | `8-ALL` Electrical (W) | `8-ALL` Nominal Heat (W) | `8-ALL` Worst-Case Corner (W) | `4-UV` Nominal Heat (W) | Thermal Limit |
|---|---|---|---|---|---|
| **Ch1 UV Array (`4× SST-10-UV`, `D1..D4`)** | `4.78 W` | **`2.90 W`** (`WPE >= 40%` bound; `2.49 W` typ) | `5.65 W` (`100%` heat bound) | **`2.90 W`** | $T_{j,\max} = 100^\circ\text{C}$ ($R_{\theta Js}=1.4^\circ\text{C/W}$) |
| **Ch2 Visible Array (`4× XP-E2`, `D5..D8`)** | `3.82 W` | **`2.26 W`** | `4.75 W` (`100%` heat bound) | `0.00 W` | $T_{j,\max} = 150^\circ\text{C}$ ($R_{\theta Js}=5.7\text{–}9.0^\circ\text{C/W}$) |
| **`U1` (`AL8860WT-7` Ch1 UV)** | `0.062 W` loss | **`0.062 W`** | **`0.115 W`** | `0.062 W` | $T_{j,\max} = 150^\circ\text{C}$ ($R_{\theta JA}=147^\circ\text{C/W}$, $\Delta T_J \le 17^\circ\text{C}$) |
| **`U2` (`AL8860WT-7` Ch2 Vis)** | `0.065 W` loss | **`0.065 W`** | **`0.115 W`** | `0.000 W` | $T_{j,\max} = 150^\circ\text{C}$ ($R_{\theta JA}=147^\circ\text{C/W}$, $\Delta T_J \le 17^\circ\text{C}$) |
| **`D9`/`D10` + `L1`/`L2` + `R3`/`R4`** | `0.220 W` | **`0.220 W`** | `0.330 W` | `0.110 W` | $T_{\max} = 125^\circ\text{C}$ |
| **`U3`/`U4`/`U5`/`Q1`/`F1`/Bias Overhead** | `0.153 W` | **`0.153 W`** | `0.260 W` | `0.140 W` | `F1` $I_{\text{hold}}(60^\circ\text{C})=1.00\text{ A}$ (`1.72×` margin) |
| **Driver PCB Total Loss** | **`0.500 W`** | **`0.50 W`** | **`0.82 W`** (`<= 0.85 W` design bound) | **`0.31 W`** | **Passes 20/20 thermal cases on `£5.88` `SK 578/50 SA` bottom heatsink!** |
| **Total Lamp Power (`20.0 V` PD)** | **`9.05 W`** (`0.453 A`) | **`5.16 W` LEDs + `0.50 W` PCB** | `10.40 W` LEDs + `0.82 W` PCB | **`2.90 W` LEDs + `0.31 W` PCB** | Overall electrical efficiency **`~94.3%`** |

### 2.2 Mechanical Compatibility & Enclosure Updates
- **Bottom Heatsink Cost Reduction:** Because Option 2 cuts Driver PCB worst-case heat by **more than `5×`** (`4.39 W -> 0.82 W`), the affordable **`£5.88` `Fischer SK 578/50 SA`** (`Ø60 × 50 mm`, identical to the top heatsink!) now passes **20/20** thermal cases including `30 °C` ambient stacked worst-case, completely eliminating the `£24.60` `SK LED R 80 SA` upgrade heatsink!
- **USB-C Direct-Mate Recess:** `j1_front_y = -25.76 mm` (`7.26 mm` Row-B datum); `mech_cap_bot_usbc.stl` bezel overmold recess is deepened so standard **`6.65 mm`** USB-C laptop-charger and power-bank plugs mate directly with positive margin (no extended-barrel cable required!).
- **PCB Relief Pockets:** Deepened from `1.8 mm` to **`2.5 mm`** in `MECH-ADAPT-BOT` for generous JST/USB-C through-hole pin clearance over the Kapton liner.
- **Ground-Referenced Switch (`SW1` / `J4`):** Common terminal (`J4.2`) is `GND`, eliminating any live supply voltage at the external toggle switch.
