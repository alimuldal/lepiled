# Interface Contract (Rev 4.1) — Electronics ↔ PCB & Mechanical / Thermal

**Canonical Registry:** [COMPONENT_IDS.csv](file:///home/alimuldal/src/lepiled/circuit_design/COMPONENT_IDS.csv) (**75 unique RefDes:** `61` Populated On-PCB = `57` SMD + `4` THT `J1..J4`; `4` Isolated NPTH `H1..H4`; `10` Off-Board)
**Datasheet Source of Truth:** [datasheets_summary.json](file:///home/alimuldal/src/lepiled/datasheets/datasheets_summary.json)
**Simulation Verification:** [sim_summary.json](file:///home/alimuldal/src/lepiled/circuit_design/sim/outputs/sim_summary.json)

---

## 1. Electronics ↔ PCB Design & Manufacturing Contract

### 1.1 Physical Board Envelopes & Mounting Holes
- **Board 1 (`driver_pcb`):** **`36.0 mm × 46.0 mm`**, 2-layer `1.6 mm` FR4, `2.0 mm` corner radii, 1 oz Cu, **ENIG** finish, Green LPI (`min_solder_mask_bridge >= 0.10 mm`) / White silk.
  - SMD power/signal envelope: `<= 4.5 mm` (`L1`/`L2` `SRN6045-680M` = `4.5 mm` max; `J1` `USB4085-GF-A` = `3.46 mm`).
  - Through-hole wire headers `J2..J4` (`JST B2B-XH-A` / `B3B-XH-A`, `1.00 mm` drills): `7.0 mm` unmated (`9.8 mm` mated).
  - **Mounting Holes (`H1..H4`):** `4× M2.5` **unplated isolated NPTH** (`Ø2.7 mm` drill, `Ø5.5 mm` copper keepout, no GND connection) at `(±14.0, ±19.0) mm`, fastened with nylon `M2.5 × 6 mm` screws into `MECH-LID-BOT` bosses.
- **Board 2 (`led_mcpcb`, `4×` per lamp):** **`20.0 mm × 80.0 mm`**, 1-layer `1.6 mm` Aluminum MCPCB (`1.0 W/m·K`, `100 µm` dielectric), 1 oz Cu, **ENIG** finish, White / Black silk.
  - `D_UV` at `(0, +18.0 mm)`, `D_VIS` at `(0, -18.0 mm)`, `MH1`/`MH2` `Ø3.2 mm` NPTH at `(0, ±32.0 mm)`, wire solder pads shifted north to **`Y = -24.0 mm`** (`>= 6.0 mm` clear of `MH2` `M3` SHCS head).

### 1.2 Copper, Stackup & Layout Design Rules (`driver_pcb`)
- **Zero Unplugged Via-in-Pad:** Every via sits outside every SMD pad copper `+ 0.25 mm` solder-mask dam (`48` vias / `143` SMD pads, `0` violations). `U3` (`W-DFN3030-14`) `1.80 × 2.70 mm` EPAD uses `2×2` segmented paste (`64.4%`) and fans out externally to `0.30/0.60 mm` `GND` vias.
- **Unbroken `B.Cu` Ground Plane Under Power Stage:** `B.Cu` forms a continuous solid `GND` plane beneath `U1`, `U2`, `D9`, `D10`, `L1`, `L2`, `R3`, `R4`, `C2`, `C3`, `C8`, `C9` (`0` non-GND segments inside `Y = [4.3, 16.5] mm`). `U1_CTRL` and `U2_CTRL` route cleanly on `F.Cu` through the `D9`/`D10` inter-pad gaps.
- **Trace Widths & High-$di/dt$ Loops (`20 V` Bus, `0.455 A` nom / `0.581 A` max):**
  - `VBUS`, `VBUS_FUSED`, `VBUS_SENSE`, `VIN_20V`: **`>= 0.80 mm`** (`1.00 mm` trunk). Zero-stub fly-by routing from `F1` directly across `D11` (`SMBJ22A`) into `C1`/`R7`/`C10`.
  - Buck hot loops (`C2/C8 -> R3 -> UV_POS`, `D9 -> VIN_20V`, `SW1_NODE -> L1` and Ch2 mirror): **`>= 0.60 mm`**, `< 10 mm` perimeter on `F.Cu`.
  - Kelvin sense routing: `U3.ISENP`/`U3.VCC` tap `R8` (`5 mΩ`) upstream/downstream pads; `U1.VIN`/`U1.SET` and `U2.VIN`/`U2.SET` tap `R3`/`R4` (`0.30 Ω`) pads directly with isolated sense traces.
- **Footprint & PCBA Accuracy:**
  - `J1` (`GCT USB4085-GF-A`): **`Ø0.40 mm`** signal drills (`0.65 × 0.90 mm` oval pads, `>= 0.125 mm` annular ring), `Y_mouth = -25.76 mm`.
  - `U1`/`U2` (`TSOT25`): `0.68 mm` nominal pad width (`0.27 mm` copper gap).
  - `F1` (`Bourns MF-MSMF110/33X`): `1812` Style-2 datasheet land pattern (`3.15 × 1.78 mm` pads at `±1.725 mm`).
  - `driver_pcb_cpl.csv` contains **only the 57 SMD parts**; `J1..J4` THT are listed in `driver_pcb_bom_pcba.csv` (`61` rows with LCSC part numbers); `H1..H4` are excluded from both.

### 1.3 RefDes Parity Rule (On-PCB vs Off-Board)
- **65 On-PCB RefDes:** `61` populated (`U1..U5`, `Q1..Q3`, `F1`, `D9..D16`, `L1..L2`, `R1..R23`, `C1..C15`, `J1..J4`) + `4` unplated NPTH (`H1..H4`).
- **10 Off-Board RefDes:** `D1..D4` (via `J2`), `D5..D8` (via `J3`), `SW1` (`C&K 7211SYZBE`, via `J4`), `SW1_BOOT` (`C&K 759D02000`).

---

## 2. Electronics ↔ Mechanical & Thermal Contract

### 2.1 Thermal Dissipation Budget (Fanless `S1-A` Top-Heatsink-Only Sizing)
Nominal drive current = **`333 mA`** (`V_SENSE = 100 mV`, `R3 = R4 = 0.30 Ω ±1%`), supplied from **`20.0 V` USB-C PD** (`I_in = 0.455 A` nominal, `0.581 A` worst-case corner).

| Subsystem | `8-ALL` Electrical (W) | `8-ALL` Nominal Heat (W) | `8-ALL` Worst-Case Corner (W) | `4-UV` Nominal Heat (W) | Thermal Limit |
|---|---|---|---|---|---|
| **Ch1 UV Array (`4× SST-10-UV`, `D1..D4`)** | `4.74 W` | **`2.84 W`** (`40%` WPE bound; `2.42 W` typ) | `5.62 W` (`100%` heat bound) | **`2.84 W`** | $T_{j,\max} = 100^\circ\text{C}$ ($R_{\theta Js}=1.4^\circ\text{C/W}$) |
| **Ch2 Visible Array (`4× XP-E2`, `D5..D8`)** | `3.80 W` | **`2.28 W`** | `4.75 W` (`100%` heat bound) | `0.00 W` | $T_{j,\max} = 150^\circ\text{C}$ ($R_{\theta Js}=5.7\text{–}9.0^\circ\text{C/W}$) |
| **`U1` (`AL8860WT-7` Ch1 UV)** | `0.067 W` loss | **`0.067 W`** | **`0.115 W`** | `0.067 W` | $T_{j,\max} = 150^\circ\text{C}$ ($125^\circ\text{C}$ derated) |
| **`U2` (`AL8860WT-7` Ch2 Vis)** | `0.071 W` loss | **`0.071 W`** | **`0.115 W`** | `0.000 W` | $T_{j,\max} = 150^\circ\text{C}$ ($125^\circ\text{C}$ derated) |
| **`D9`/`D10` + `L1`/`L2` + `R3`/`R4`** | `0.206 W` | **`0.206 W`** | `0.307 W` | `0.095 W` | $T_{\max} = 125^\circ\text{C}$ |
| **`U3`/`U4`/`U5`/`Q1`/`F1`/Bias Overhead** | `0.206 W` | **`0.206 W`** | `0.260 W` | `0.158 W` | `F1` $I_{\text{hold}}(60^\circ\text{C})=0.73\text{ A}$ (`1.26×` margin) |
| **Driver PCB Total Loss** | **`0.550 W`** | **`0.550 W`** | **`0.797 W`** (`<= 0.85 W` bound) | **`0.320 W`** | **Passes 20/20 (`22–30 °C`) & 5/5 (`35 °C`) on sealed `MECH-LID-BOT` (`<= 75 °C` PETG)** |
| **Total Lamp Power (`20.0 V` PD)** | **`9.10 W`** (`0.455 A`) | **`5.12 W` LEDs + `0.55 W` PCB** | `10.37 W` LEDs + `0.80 W` PCB | **`2.84 W` LEDs + `0.32 W` PCB** | Overall electrical efficiency **`93.8%`** |

### 2.2 Mechanical Interface Datums (Synced with `mechanical_design/cad/params.py`)
- **Bottom Lid & PCB Elevation (`S1-A`):** `MECH-LID-BOT` (`Ø92 × 4.0 mm`) carries `4×` integral `11.5 mm` bosses (`Z_pcb_bot = 15.5 mm`, `Z_pcb_top = 17.1 mm`), giving `9.7 mm` open air below through-hole pins (`0` Kapton lining or gap pad needed) and `8.98 mm` vertical headroom above mated JST-XH plugs.
- **USB-C Direct-Mate Tunnel & `20 mm` Grommet Flange:** `J1` front datum `Y = -25.76 mm`, centerline `Z = 18.98 mm`. Outer `-Y` wall carries a flat `Ø26.0 mm` spotface at `Y = -43.5 mm` with a **`Ø20.2 × 2.5 mm`** grommet bore and `Ø23.6 mm` back-lip groove accepting a standard `20 mm` rubber membrane grommet around any `6.65 mm` USB-C cable (`2.10 mm` exposed plug barrel at full `4.55 mm` mating).
- **`C&K 7211SYZBE` Switch Alcove (`+X` Wall):** `Ø6.35 mm` (`1/4-40`) bushing bore at `Z = 30.0 mm` (`2.50 mm` panel thickness), `15.0 × 13.5 mm` internal alcove clearing the `12.7 × 11.43 × 10.67 mm` DPDT body (`4.53 mm` radial clearance to PCB, `2.39 mm` vertical clearance above SMD envelope).
- **Top Butt-Joint Preload (`Opus B-H3` Fix):** `MECH-ANCHOR-TOP` (`32 × 32 × 14.0 mm` stock Al bar) sits recessed **`0.50 mm`** below the top end face of `MECH-HS-CORE` via tight `Ø4.2 mm` round cross-pin bores, ensuring `MECH-EYE-1` torque always preloads the core against `MECH-ADAPT-TOP` (`Ø76.2 × 3.0 mm` stock Al disc) and `MECH-HS-EXT-TOP` (`SK 578/50 SA`).
