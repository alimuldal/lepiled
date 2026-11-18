# M1 Interface Contract — Electronics ↔ M2 (PCB) & M3 (Mechanical / Thermal)

**Canonical Registry:** `circuit_design/COMPONENT_IDS.csv` (52 unique RefDes)
**Datasheet Source of Truth:** `datasheets/datasheets_summary.json`
**Simulation Verification:** `circuit_design/sim/outputs/sim_summary.json`

---

## 1. M1 ↔ M2 (PCB Design & Manufacturing) Contract

### 1.1 Physical Board Envelope & Mounting Holes
- **Board Dimensions:** **`36.0 mm × 46.0 mm`**, 2-layer `1.6 mm` FR4, `2.0 mm` corner radii (`diagonal = 58.4 mm`, providing `4.8 mm` radial clearance inside `Ø 68 mm` borosilicate glass ID).
- **Max Component Height:** `≤ 4.8 mm` above PCB top (`L1`/`L2` `SRN6045-100M` = `4.5 mm` max; `J1` `USB4085-GF-A` = `3.46 mm`).
- **Mounting Holes (`H1..H4`):** `4× M2.5` plated/GND-tied holes (`2.7 mm` drill, `5.5 mm` pad/nut keepout) centered at:
  - `H1`: `(-14.0, +19.0) mm`
  - `H2`: `(+14.0, +19.0) mm`
  - `H3`: `(-14.0, -19.0) mm`
  - `H4`: `(+14.0, -19.0) mm`
  *(Origin at board center.)*

### 1.2 Copper, Stackup & Layout Design Rules
- **Copper Weight:** `1 oz` (`35 µm`) outer layers minimum (`2 oz` optional).
- **Power & Loop Trace Widths:**
  - `VBUS`, `VBUS_FUSED`, `VIN_PROT` (`2.1 A` RMS nominal, `~2.6 A` droop): **`≥ 1.2 mm`** (`47 mil`).
  - High-$di/dt$ switching loops (`C2/C3 -> L1/L2 -> U1/U2.SW -> PGND`, `D9/D10 -> C4/C5 -> PGND`): **`≥ 1.0 mm`**, kept **`< 8 mm`** total loop length.
  - `VOUT1`, `VOUT2` (`~339 mA`): `≥ 0.6 mm`.
  - Signal nets (`EN1_NET`, `EN2_NET`, `DIM2_NET`, `CC1`, `CC2`): `≥ 0.25 mm` (`10 mil`).
- **Kelvin Feedback Routing (`FB1_NET`, `FB2_NET`):**
  - Route `U1.5` (`FB`) directly to `R8` / `D13` anode pad (`FB1_NET`), and connect `R3` (`0.56 Ω`) ground return cleanly to `U1` `AGND`/`PGND` (`>= 0.25 mm`) without sharing high-current switching return copper. Same for `U2` / `R9` / `D14` / `R4`.
- **`SW` Switch-Node Copper Keepout & Clearance:**
  - Keep the `SW1_NODE` and `SW2_NODE` copper islands (`U1.7`, `U2.7`) compact (`< 15 mm²`) and **keep bottom-layer `GND` copper pour cleared directly beneath `SW1_NODE` and `SW2_NODE`** to minimize parasitic switching capacitance and EMI.
  - Maintain **`≥ 0.25 mm` (`10 mil`)** clearance around `VOUT1`, `VOUT2`, `SW1_NODE`, and `SW2_NODE` (~16–23 V boost/OVP nodes).
- **Thermal Vias & Copper Pours:**
  - Place **4–6× `0.30 mm` drill / `0.60 mm` pad thermal vias** directly under each `LM3410XMY/NOPB` (`HVSSOP-8` `DAP` exposed pad) stitched to a continuous bottom `GND` thermal plane.
  - Provide **`≥ 1.0 cm²` copper pour** on the cathode pads of `D9` and `D10` (`B340A-13-F`, `SMA`, `RθJA = 50 °C/W`).
- **USB-C & Optional Gland Pads (`J1`, `R1`, `R2`, `TP1`, `TP2`):**
  - Place `R1` (`5.1 kΩ`) and `R2` (`5.1 kΩ`) directly adjacent to `J1` pins `A5` (`CC1`) and `B5` (`CC2`) with individual traces to `GND` (never short `CC1` and `CC2`).
  - Place `TP1` (`VBUS`) and `TP2` (`GND`) `2.5 mm` pad / `1.3 mm` drill TH solder pads near `J1` for builders using an optional captive USB cable through an M16 gland.

### 1.3 RefDes Parity Rule (On-PCB vs Off-Board)
- `circuit_design/COMPONENT_IDS.csv` defines **52 RefDes**:
  - **43 On-PCB parts** (`U1..U2`, `Q1`, `F1`, `D9..D15`, `L1..L2`, `R1..R10`, `C1..C10`, `J1..J4`, `TP1..TP2`, `H1..H4`).
  - **9 Off-Board parts**: `D1..D4` (terminated on `J2`), `D5..D8` (terminated on `J3`), and `SW1` (terminated on `J4`).
- M2 KiCad schematic MUST instantiate all 52 RefDes (marking `D1..D8` and `SW1` with off-board/DNP-on-driver-PCB attributes or placing `D1..D8` on a separate Al MCPCB sheet/board) so `pcb_design/`, `circuit_design/`, and `bom/` maintain exact 1:1 RefDes parity.

---

## 2. M1 ↔ M3 (Mechanical & Thermal) Contract

### 2.1 Thermal Dissipation Budget (Fanless Sizing)
Nominal steady-state drive current = **`339.3 mA`** (`V_FB = 0.190 V`, `R3 = R4 = 0.56 Ω ±1%`).
Conservative LED heat dissipation assumes WPE ≈ `40%` for UV (`SST-10-UV`, datasheet typ `48%` -> `~0.64 W` heat, conservative `0.74 W`) and `28–58%` across XP-E2 colors (`~0.50–0.69 W` heat, conservative `~2.30 W` total Vis). A `100%`-electrical upper bound is also given for worst-case passive heatsink margin checks.

| Subsystem | Mode: `8-ALL` Electrical (W) | Mode: `8-ALL` Conservative Heat (W) | Mode: `8-ALL` 100%-Heat Bound (W) | Mode: `4-UV` Conservative Heat (W) | Thermal Limit ($T_{j,\max}$ / $T_{\text{case}}$) |
|---|---|---|---|---|---|
| **Each UV LED (`D1..D4`, `SST-10-UV`)** | `1.22 W` (`3.59 V × 0.339 A`) | **`0.74 W`** | `1.22 W` | **`0.74 W`** | **$T_{j,\max} = 100^\circ\text{C}$** ($R_{\theta J-s} = 1.4^\circ\text{C/W}$) |
| **Ch1 UV Array Total (`4× UV`)** | `4.87 W` | **`2.96 W`** | `4.87 W` | **`2.96 W`** | Target $T_{j,\text{UV}} \le 80^\circ\text{C}$ @ $30^\circ\text{C}$ amb |
| **Visible Blue (`D5, D6`, `XPEBRY`)** | `0.99 W` ea | `0.50 W` ea | `0.99 W` ea | `0.00 W` | $T_{j,\max} = 150^\circ\text{C}$ ($R_{\theta J-s} = 5.7^\circ\text{C/W}$) |
| **Visible Green (`D7`, `XPEBGR`)** | `0.91 W` | `0.66 W` | `0.91 W` | `0.00 W` | $T_{j,\max} = 150^\circ\text{C}$ ($R_{\theta J-s} = 9.0^\circ\text{C/W}$) |
| **Visible Cool White (`D8`, `XPEBWT`)** | `0.99 W` | `0.64 W` | `0.99 W` | `0.00 W` | $T_{j,\max} = 150^\circ\text{C}$ ($R_{\theta J-s} = 5.8^\circ\text{C/W}$) |
| **Ch2 Visible Array Total (`4× Vis`)** | `3.88 W` | **`2.30 W`** | `3.88 W` | `0.00 W` | Target $T_{j,\text{Vis}} \le 85^\circ\text{C}$ @ $30^\circ\text{C}$ amb |
| **`U1` (`LM3410XMY` Ch1 UV)** | `0.36 W` loss | **`0.36 W`** (`0.65 W` max droop) | `0.65 W` | **`0.36 W`** | **$T_{j,\max} = 125^\circ\text{C}$** ($R_{\theta JA} = 53.7^\circ\text{C/W}$) |
| **`U2` (`LM3410XMY` Ch2 Vis)** | `0.24 W` loss | **`0.24 W`** (`0.42 W` max droop) | `0.42 W` | `0.00 W` | **$T_{j,\max} = 125^\circ\text{C}$** ($R_{\theta JA} = 53.7^\circ\text{C/W}$) |
| **`D9` / `D10` (`B340A-13-F`)** | `0.12 W` ea | **`0.12 W`** ea | `0.15 W` ea | `0.12 W` (`D9`) | $T_{j,\max} = 125^\circ\text{C}$ ($R_{\theta JA} = 50^\circ\text{C/W}$) |
| **`L1` / `L2` (`SRN6045-100M`)** | `0.06 W` / `0.04 W` | **`0.10 W`** tot | `0.16 W` tot | `0.06 W` (`L1`) | $T_{\max} = 125^\circ\text{C}$ |
| **`F1 + Q1 + R3/R4` Passives** | `~0.35 W` tot | **`~0.35 W`** | `~0.45 W` | `~0.14 W` | — |
| **Driver PCB Total Loss** | `1.29 W` | **`1.29 W`** | `1.83 W` | **`0.68 W`** | Keep PCB ambient $\le 60^\circ\text{C}$ |
| **Total Lamp Power (`5 V` USB In)** | **`10.04 W`** (`~2.07 A`) | **`5.26 W` heatsink + `1.29 W` PCB** | `8.75 W` + `1.83 W` | **`2.96 W` hs + `0.68 W` PCB** | — |

### 2.2 LED Array Geometry & Wiring Constraints
- **Emitter Mounting:** `4×` custom JLCPCB `1.0 W/m·K` Aluminum MCPCB dual-LED strips (`MECH-MCPCB-1..4`, ~`20 × 80 mm` each, or `8×` 20 mm Cu DTP star fallback) mounted on the 4 faces of a central aluminum heatsink core (`90°` azimuth spacing, 2 vertical tiers: 4× UV + 4× Visible, `360°` emission).
- **Wiring:** Two independent 2-wire series loops using `22 AWG` silicone-insulated wire (`≥ 105 °C` rated) routed cleanly through heatsink channels/end-cap pass-throughs back to `J2` (`UV+`, `UV-`) and `J3` (`VIS+`, `VIS-`).

### 2.3 Panel Cutouts & User Interface Dimensions
- **`SW1` (`E-Switch 100SP3T1B1M1QEH` + `C&K 759D02000` boot):**
  - **Cutout:** **`Ø 6.35 mm`** (`1/4"`) circular hole (`1/4-40` threaded bushing, flat/anti-rotation key optional, `2.0–3.5 mm` max panel wall thickness for boot nut engagement).
  - Connected to PCB header `J4` via 3× `24 AWG` wires (`UV_EN`, `5V_COM`, `ALL_EN`).
- **Power Entry (`J1` USB-C vs M16 Captive Cable Gland):**
  - *Option A (Captive Weatherproof Cable — recommended for outdoor moth trapping):* **`M16 × 1.5`** circular cutout (**`Ø 16.2 mm`**) for IP68 nylon cable gland clamping a `2 m` heavy-duty USB cable soldered directly to `TP1`/`TP2`.
  - *Option B (Direct PCB USB-C Receptacle):* Recessed **`9.3 × 3.6 mm`** slot (centered on `J1` `USB4085-GF-A` mid-plane) with external silicone dust/rain plug.
