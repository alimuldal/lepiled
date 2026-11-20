# Interface Contract (Rev 4.3) — Electronics ↔ PCB & Mechanical / Thermal

**Canonical Registry:** [COMPONENT_IDS.csv](file:///home/alimuldal/src/lepiled/circuit_design/COMPONENT_IDS.csv) (**75 unique RefDes:** `61` Populated On-PCB = `57` SMD JLCPCB PCBA + `4` THT `J1..J4`; `4` Isolated NPTH `H1..H4`; `10` Off-Board = `8×` pre-mounted `20 mm` Copper DTP stars + `SW1` + `SW1_BOOT`)
**Datasheet Source of Truth:** [datasheets_summary.json](file:///home/alimuldal/src/lepiled/datasheets/datasheets_summary.json)
**Simulation Verification:** [sim_summary.json](file:///home/alimuldal/src/lepiled/circuit_design/sim/outputs/sim_summary.json)

---

## 1. Electronics ↔ PCB Design & Manufacturing Contract

### 1.1 Physical Board Envelope & Mounting Holes
- **Single Custom PCB (`driver_pcb` — `led_mcpcb` eliminated in Rev 4.2):** **`36.0 mm × 46.0 mm`**, 2-layer `1.6 mm` FR4, `2.0 mm` corner radii, 1 oz Cu, **ENIG** finish, Green LPI (`min_solder_mask_bridge >= 0.10 mm`) / White silk.
  - SMD power/signal envelope: `<= 4.5 mm` (`L1`/`L2` `SRN6045-680M` = `4.5 mm` max; `J1` `USB4085-GF-A` = `3.46 mm`).
  - Through-hole wire headers `J2..J4` (`JST B2B-XH-A` / `B3B-XH-A`, `1.00 mm` drills, mated via pre-crimped `22 AWG` JST-XH pigtails): `7.0 mm` unmated (`9.8 mm` mated).
  - **Mounting Holes (`H1..H4`):** `4× M2.5` **unplated isolated NPTH** (`Ø2.7 mm` drill, `Ø5.5 mm` copper keepout, no GND connection) at `(±14.0, ±19.0) mm`, dropping straight onto `MECH-LID-BOT`'s `4× Ø2.45 mm` 3D-printed locating pins (zero PCB screws, zero brass inserts).
- **Off-Board LEDs (`8×` `20 mm` Copper DTP Stars):** `4×` UV-A (`SST-10-UV`, `Z = 163.0 mm`) and `4×` Visible (`Cree XP-E2`, `Z = 127.0 mm`) bolted directly to the 4 faces of `MECH-HS-CORE` with `16× M3` screws + `16× M3` nylon insulating washers (electrically neutral thermal pads verified safe on shared Al core).

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

### 2.1 Thermal Dissipation Budget (Fanless Protruding Bare `250 mm` Al Core)
Nominal drive current = **`333 mA`** (`V_SENSE = 100 mV`, `R3 = R4 = 0.30 Ω ±1%`), supplied from **`20.0 V` USB-C PD** (`I_in = 0.455 A` nominal, `0.581 A` worst-case corner).

| Subsystem | `8-ALL` Electrical (W) | `8-ALL` Nominal Heat (W) | `8-ALL` Worst-Case Corner (W) | `4-UV` Nominal Heat (W) | Thermal Limit |
|---|---|---|---|---|---|
| **Ch1 UV Array (`4× SST-10-UV`, `D1..D4`)** | `4.74 W` | **`2.84 W`** (`40%` WPE bound; `2.42 W` typ) | `5.62 W` (`100%` heat bound) | **`2.84 W`** | $T_{j,\max} = 100^\circ\text{C}$ ($R_{\theta Js}=1.4^\circ\text{C/W}$) |
| **Ch2 Visible Array (`4× XP-E2`, `D5..D8`)** | `3.80 W` | **`2.28 W`** | `4.75 W` (`100%` heat bound) | `0.00 W` | $T_{j,\max} = 150^\circ\text{C}$ ($R_{\theta Js}=5.7\text{–}9.0^\circ\text{C/W}$) |
| **`U1` (`AL8860WT-7` Ch1 UV)** | `0.067 W` loss | **`0.067 W`** | **`0.115 W`** | `0.067 W` | $T_{j,\max} = 150^\circ\text{C}$ ($125^\circ\text{C}$ derated) |
| **`U2` (`AL8860WT-7` Ch2 Vis)** | `0.071 W` loss | **`0.071 W`** | **`0.115 W`** | `0.000 W` | $T_{j,\max} = 150^\circ\text{C}$ ($125^\circ\text{C}$ derated) |
| **`D9`/`D10` + `L1`/`L2` + `R3`/`R4`** | `0.206 W` | **`0.206 W`** | `0.307 W` | `0.095 W` | $T_{\max} = 125^\circ\text{C}$ |
| **`U3`/`U4`/`U5`/`Q1`/`F1`/Bias Overhead** | `0.206 W` | **`0.206 W`** | `0.260 W` | `0.158 W` | `F1` $I_{\text{hold}}(60^\circ\text{C})=0.73\text{ A}$ (`1.26×` margin) |
| **Driver PCB Total Loss** | **`0.550 W`** | **`0.550 W`** | **`0.797 W`** (`<= 0.85 W` bound) | **`0.320 W`** | **Passes `16/16` Real-WPE (`22–30 °C`) & `4/4` (`35 °C`) on sealed `MECH-LID-BOT` (`<= 75 °C` PETG)** |
| **Total Lamp Power (`20.0 V` PD)** | **`9.10 W`** (`0.455 A`) | **`5.12 W` LEDs + `0.55 W` PCB** | `10.37 W` LEDs + `0.80 W` PCB | **`2.84 W` LEDs + `0.32 W` PCB** | Overall electrical efficiency **`93.8%`** |

### 2.2 Mechanical Interface Datums (Synced with `mechanical_design/cad/params.py` Rev 4.3)
- **Bottom Lid, Screwless PCB Retention & Protective Base Ring:** `MECH-LID-BOT` (`Ø92 × 4.0 mm`) carries `4×` integral `18.0 mm` bosses topped with `Ø2.45 × 2.0 mm` printed locating pins (`Z_pcb_bot = 22.0 mm`, `Z_pcb_top = 23.6 mm`) passing directly into `driver_pcb`'s isolated NPTH `H1..H4` (zero PCB screws, zero brass inserts), giving `16.2 mm` open air below through-hole pins and `7.82 mm` vertical headroom above mated JST-XH plugs. `MECH-BASE-RING` (`Ø92 × 68 × 18 mm`, `4×` drainage cutouts) clamps underneath `MECH-LID-BOT` via the same `4× M3 × 16 mm` SHCS lid bolts.
- **Bottom-Mounted `C&K 7211SYZBE` Switch (`MECH-LID-BOT`):** Vertical `Ø6.35 mm` (`1/4-40`) bore + `1.5 mm` upper anti-rotation pocket (`2.50 mm` panel wall) at `(X = 0.0, Y = +8.5 mm)` pointing downward inside `MECH-BASE-RING`; solder lugs clear `driver_pcb` underside by `4.03 mm` and `J4`/`J2-J3` pins by `>= 3.98 mm`; `C&K 759D02000` silicone boot sits `3.0 mm` clear above flat ground. `MECH-CAP-BOT`'s `+X` wall is 100% solid and unbroken.
- **USB-C Direct-Mate Tunnel & `20 mm` Grommet Boss (`-Y` Wall):** `J1` front datum `Y = -25.76 mm`, centerline `Z = 25.48 mm`. Local `-Y` grommet boss blends cleanly from the lower flange into the contoured waist (`Ø92 -> Ø71 -> Ø65 -> Ø84 mm`), carrying a flat `Ø26.0 mm` spotface at `Y = -43.5 mm` with a **`Ø20.2 × 2.5 mm`** grommet bore and `Ø23.6 mm` back-lip groove (`2.10 mm` exposed plug barrel at full `4.55 mm` mating).
- **UVT PMMA Shroud, Protruding Bare Al Core & Dual Rain Roof:** Shatter-resistant UV-transmitting PMMA cylinder (`Ø75 × 69 × 3.0 mm × 150 mm`, `Z = 73.0–223.0 mm`) seals on `68 × 3.5 mm` VMQ70 O-rings. Single `250.0 mm` bare `40 × 40 × 3.0 mm` Al 6063 core (`Z = 73.0–323.0 mm`) seats on `MECH-PLUG-BOT`, passes through `MECH-CAP-TOP` (integral `Ø108 mm` drip-brim shielding `2× M3 × 12 mm` locking screws at `Z = 230.0 mm` + silicone groove), protrudes `85.5 mm`, carries a `Ø8.0 mm` hanging hole at `Z = 305.0 mm`, and is topped by `MECH-PLUG-TOP` (`Z = 327.0 mm`) plus detachable cord-retained `MECH-RAIN-HAT` (`Ø136 mm`, `Z = 329.55 mm`, `347.55 mm` total height from `Z = -18.0 mm` standing rim).
