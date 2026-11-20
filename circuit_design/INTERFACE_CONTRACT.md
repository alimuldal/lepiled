# Interface Contract (Rev 4.6) — Electronics ↔ PCB & Mechanical / Thermal

**Canonical Registry:** [COMPONENT_IDS.csv](COMPONENT_IDS.csv) (**75 unique RefDes:** `61` Populated On-PCB = `57` SMD JLCPCB PCBA + `4` THT `J1..J4`; `4` Isolated NPTH `H1..H4`; `10` Off-Board = `8×` pre-mounted `20 mm` Copper DTP stars + `SW1` + `SW1_BOOT`)
**Datasheet Source of Truth:** [datasheets_summary.json](../datasheets/datasheets_summary.json)
**Simulation Verification:** [sim_summary.json](sim/outputs/sim_summary.json)

---

## 1. Electronics ↔ PCB Design & Manufacturing Contract

### 1.1 Physical Board Envelope & Mounting Holes
- **Single Custom PCB (`driver_pcb` — `led_mcpcb` eliminated in Rev 4.2):** **`36.0 mm × 46.0 mm`**, 2-layer `1.6 mm` FR4, `2.0 mm` corner radii, 1 oz Cu, **ENIG** finish, Green LPI (`min_solder_mask_bridge >= 0.10 mm`) / White silk.
  - SMD power/signal envelope: `<= 4.5 mm` (`L1`/`L2` `SRN6045-680M` = `4.5 mm` max; `J1` `USB4085-GF-A` = `3.46 mm`).
  - Through-hole wire headers `J2..J4` (`JST B2B-XH-A` / `B3B-XH-A`, `1.00 mm` drills, mated via pre-crimped `22 AWG` JST-XH pigtails): `7.0 mm` unmated (`9.8 mm` mated).
  - **Mounting Holes (`H1..H4`):** `4× M2.5` **unplated isolated NPTH** (`Ø2.7 mm` drill, `Ø5.5 mm` copper keepout, no GND connection) at `(±14.0, ±19.0) mm`, bolting horizontally (SMD-side down) onto `MECH-CAP-BOT`'s `4×` filleted `Ø7.4 → Ø5.5 mm` standoffs fitted with `M2.5 × 4.0 × 3.5 mm` brass heat-set inserts via `4× M2.5 × 6 mm` pan-head screws (`100%` clear of all `57` SMDs).
- **Off-Board LEDs (`8×` `20 mm` Copper DTP Stars):** `4×` UV-A (`SST-10-UV`, `Z = 139.0 mm`) and `4×` Visible (`Cree XP-E2`, `Z = 107.0 mm`, `32 mm` pitch) bolted directly to the 4 masked bare-aluminum pads on the matte-black `30 × 30 × 3.0 mm` `MECH-HS-CORE` with `16× M3 × 8 mm` pan screws + `16× M3` nylon insulating washers (electrically neutral thermal pads verified safe on shared Al core).

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

### 2.1 Thermal Dissipation Budget (Fanless Protruding Matte-Black `200 mm` `30 × 30 × 3` Al Core)
Nominal drive current = **`333 mA`** (`V_SENSE = 100 mV`, `R3 = R4 = 0.30 Ω ±1%`), supplied from **`20.0 V` USB-C PD** (`I_in = 0.455 A` nominal, `0.581 A` worst-case corner).

| Subsystem | `8-ALL` Electrical (W) | `8-ALL` Nominal Heat (W) | `8-ALL` Worst-Case Corner (W) | `4-UV` Nominal Heat (W) | Thermal Limit |
|---|---|---|---|---|---|
| **Ch1 UV Array (`4× SST-10-UV`, `D1..D4`)** | `4.74 W` | **`2.84 W`** (`40%` WPE bound; `2.42 W` typ) | `5.62 W` (`100%` heat bound) | **`2.84 W`** | $T_{j,\max} = 100^\circ\text{C}$ ($R_{\theta Js}=1.4^\circ\text{C/W}$) |
| **Ch2 Visible Array (`4× XP-E2`, `D5..D8`)** | `3.80 W` | **`2.28 W`** | `4.75 W` (`100%` heat bound) | `0.00 W` | $T_{j,\max} = 150^\circ\text{C}$ ($R_{\theta Js}=5.7\text{–}9.0^\circ\text{C/W}$) |
| **`U1` (`AL8860WT-7` Ch1 UV)** | `0.067 W` loss | **`0.067 W`** | **`0.115 W`** | `0.067 W` | $T_{j,\max} = 150^\circ\text{C}$ ($125^\circ\text{C}$ derated) |
| **`U2` (`AL8860WT-7` Ch2 Vis)** | `0.071 W` loss | **`0.071 W`** | **`0.115 W`** | `0.000 W` | $T_{j,\max} = 150^\circ\text{C}$ ($125^\circ\text{C}$ derated) |
| **`D9`/`D10` + `L1`/`L2` + `R3`/`R4`** | `0.206 W` | **`0.206 W`** | `0.307 W` | `0.095 W` | $T_{\max} = 125^\circ\text{C}$ |
| **`U3`/`U4`/`U5`/`Q1`/`F1`/Bias Overhead** | `0.206 W` | **`0.206 W`** | `0.260 W` | `0.158 W` | `F1` $I_{\text{hold}}(60^\circ\text{C})=0.73\text{ A}$ (`1.26×` margin) |
| **Driver PCB Total Loss** | **`0.550 W`** | **`0.550 W`** | **`0.797 W`** (`<= 0.85 W` bound) | **`0.320 W`** | **`T_pcb = 52.8 °C` (`22 °C` UK) / `60.3 °C` (`30 °C` Horiz Nom) / `70.4 °C` (`30 °C` DS-RealWPE) `<= 75 °C` (`95 °C` ASA)** |
| **Total Lamp Power (`20.0 V` PD)** | **`9.10 W`** (`0.455 A`) | **`5.12 W` LEDs + `0.55 W` PCB** | `10.37 W` LEDs + `0.80 W` PCB | **`2.84 W` LEDs + `0.32 W` PCB** | Overall electrical efficiency **`93.8%`** |

### 2.2 Mechanical Interface Datums (Synced with `mechanical_design/cad/params.py` Rev 4.6)
- **Horizontal `driver_pcb`, Compact Tapered Base & Recessed Bottom Lid:** Unchanged `36 × 46 × 1.6 mm` `driver_pcb` mounts horizontally (`F.Cu` SMD/JST side facing **down** at `Z = 47.0 mm`, centered at `Y = +6.0 mm`) onto `4×` filleted `M2.5` brass-insert standoffs inside `MECH-CAP-BOT` via `H1..H4` + `4× M2.5 × 6 mm` screws (`2.12 mm` radial clearance inside `Ø71.0 mm` bay; `9.73 mm` above `SW1` lugs; `14.7 mm` below mated `J2..J4` to `MECH-LID-BOT`). `MECH-CAP-BOT` is one compact `5.1°` matte-black ASA frustum (`Ø88.4 → Ø74.0 mm`, `Z = 0..80.0 mm`) recessing `MECH-LID-BOT` (`Ø79.4 × 5.0 mm`, `Z = 17.5..22.5 mm`) `17.5 mm` inside its standing skirt (`MECH-BASE-RING` deleted), sealed radially via `MECH-GASKET-3` (`62 × 2.5 mm` VMQ70 on a `6.5 mm` spigot, `14.0%` squeeze) and fastened by `4× M3 × 10 mm` SHCS into `4× M3` brass inserts.
- **Coaxial Split Cable Clamp, Bottom `SW1`, Interior ePTFE Vent & Side-Visible `D12` Lightpipe:** Compact `90°`-down USB-C PD plug (`<= 13 mm` past `J1` mouth at `Y = -20.18 mm, Z = 45.12 mm`, plus `7.0 mm` molded strain relief) passes intact through `MECH-LID-BOT`'s `16.0 × 14.0 mm` rounded-stadium port (`(0.0, -18.5 mm)`) and is clamped from below by `2×` identical 3D-printed `MECH-CABLE-CLAMP` halves (`2× M3 × 12 mm` SHCS, `0 mm` internal protrusion → `6.92 mm` vertical air gap below strain relief, `5.0 mm` ground clearance). `C&K 7211SYZBE` + `759D02000` boot mounts downward at `(0.0, +15.0 mm)` (`20.8 mm` gap from clamp port, `2.5 mm` above ground). `MECH-LID-BOT` also carries a `Ø2.5 mm` vent bore (`(-20.0, 0.0 mm)`) covered on the sheltered **inside top face** by `MECH-VENT-1` and a `28.3 mm` clear `D12` lightpipe (`(+16.0, -0.6 mm)`) terminating `1.4 mm` below `D12` with a `45°` side-visible beveled tip.
- **Extruded `XT PMMA` Shroud, Matte-Black `30 × 30 × 3` Core & Lofted Rain Roof:** Clear unstabilized extruded `XT PMMA` cylinder (`Ø60 × 54 × 3.0 × 115 mm`, `Z = 65.5–180.5 mm`, `±2.0 mm` cut-length & `59.2–60.6 mm` ovality tolerant) seals radially on `60 × 3.5 mm` soft VMQ50/60 bore O-rings (`22.9%` nom squeeze, `14.5 mm` sockets). Single `200.0 mm` matte-black sprayed `30 × 30 × 3.0 mm` Al 6063-T6 core (`Z = 58.5–258.5 mm`, `174 g`) seats flat on a `5.5 mm` bulkhead inside solid `R = 24.4 mm` hubs in both caps, locks internally from the dry bay via `2× M3 × 12 mm` SHCS into `MECH-CORE-ANCHOR` (**zero exterior holes on `MECH-CAP-BOT`**) with `2× 9.0 × 7.5 mm` `±Y` wire channels, passes through `MECH-CAP-TOP` (unbroken `Ø84 mm` eaves lofted to `R = 4 mm` `38.8 × 38.8 mm` collar + `2× M3 × 10 mm` solid-shoulder lock screws at `Z = 190.5 mm` + backed `2.0 × 2.5 mm` neutral-cure oxime silicone channel), protrudes `63.0 mm` with Signal-Orange bushed `Ø8.0 mm` hang hole (`Z = 242.5 mm`), and is topped by an `8.0 mm` chamfered finial `MECH-PLUG-TOP` (**`266.5 mm` total height**).
