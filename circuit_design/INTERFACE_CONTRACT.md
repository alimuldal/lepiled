# M1 Interface Contract — Electronics ↔ M2 (PCB) & M3 (Mechanical / Thermal)

**Canonical Registry:** `circuit_design/COMPONENT_IDS.csv` (62 unique RefDes: 52 On-PCB, 10 Off-Board)
**Datasheet Source of Truth:** `datasheets/datasheets_summary.json`
**Simulation Verification:** `circuit_design/sim/outputs/sim_summary.json`

---

## 1. M1 ↔ M2 (PCB Design & Manufacturing) Contract

### 1.1 Physical Board Envelope & Mounting Holes
- **Board Dimensions:** **`36.0 mm × 46.0 mm`**, 2-layer `1.6 mm` FR4, `2.0 mm` corner radii (`diagonal = 58.4 mm`, providing `4.8 mm` radial clearance inside `Ø 68 mm` borosilicate glass ID).
- **Component Heights above PCB Top:**
  - SMD power/signal envelope: `≤ 4.8 mm` (`L1`/`L2` `SRN6045-100M` = `4.5 mm` max; `J1` `USB4085-GF-A` = `3.46 mm`).
  - Through-hole wire headers `J2..J4` (`JST B2B-XH-A` / `B3B-XH-A`): `7.0 mm` unmated (`9.8 mm` mated) — locate `J2..J4` inside the end-cap central wiring pocket per M3 clearance.
- **Mounting Holes (`H1..H4`):** `4× M2.5` plated/GND-tied holes (`2.7 mm` drill, `5.5 mm` pad/nut keepout) centered at:
  - `H1`: `(-14.0, +19.0) mm`
  - `H2`: `(+14.0, +19.0) mm`
  - `H3`: `(-14.0, -19.0) mm`
  - `H4`: `(+14.0, -19.0) mm`
  *(Origin at board center.)*

### 1.2 Copper, Stackup & Layout Design Rules
- **Copper Weight:** `1 oz` (`35 µm`) outer layers minimum (`2 oz` optional).
- **Power & Loop Trace Widths:**
  - `VBUS`, `VBUS_FUSED`, `V_MID`, `VIN_PROT` (`2.1 A` nom, `2.4 A` droop): **`≥ 1.2 mm`** (`47 mil`).
  - High-$di/dt$ switching loops (`C2/C3 -> L1/L2 -> U1/U2.SW -> PGND`, `D9/D10 -> C4/C5 -> PGND`): **`≥ 1.0 mm`**, kept **`< 8 mm`** total loop length.
  - `VOUT1`, `VOUT2` (`~339 mA`): `≥ 0.6 mm`.
  - Signal nets (`EN1_NET`, `EN2_NET`, `DIM2_NET`, `Q1_GATE`, `Q2_BASE`, `Q3_BASE`, `CC1`, `CC2`): `≥ 0.25 mm` (`10 mil`).
- **Kelvin Feedback & Star-Ground Routing (`FB1_NET`, `FB2_NET`, `PGND`, `AGND`):**
  - Per `datasheets/lm3410.pdf` p. 3 (`DGN` 8-pin MSOP-PowerPAD): `1=NC, 2=PGND, 3=VIN, 4=DIM, 5=FB, 6=AGND, 7=SW, 8=NC, DAP=GND`.
  - Route `U1.5` (`FB`) directly to `R8` / `D13` anode (`FB1_NET`). Route `R3` (`0.56 Ω`) ground return directly to `U1.6` (`AGND`) and tie `AGND` (Pin 6) + `PGND` (Pin 2) cleanly at the `DAP` thermal pad (never share `C2/C4` high-$di/dt$ switching return copper with `R3`!). Same for `U2` / `R9` / `D14` / `R4`.
- **`SW` Switch-Node Copper Keepout & Clearance:**
  - Keep `SW1_NODE` and `SW2_NODE` (`U1.7`, `U2.7`) compact (`< 15 mm²`) and **clear bottom-layer `GND` copper directly beneath `SW1_NODE` and `SW2_NODE`**.
  - Maintain **`≥ 0.25 mm` (`10 mil`)** clearance around `VOUT1`, `VOUT2`, `SW1_NODE`, and `SW2_NODE` (`~16–23 V`).
- **Thermal Vias & Copper Pours:**
  - Place **4–6× `0.30 mm` drill / `0.60 mm` pad thermal vias** directly under each `LM3410XMY/NOPB` (`DGN` `DAP`) stitched to a continuous bottom `GND` thermal plane.
  - Provide **`≥ 1.0 cm²` copper pour** on the cathode pads of `D9` and `D10` (`B340A-13-F`, `SMA`) and generous `Drain`/`Source` copper pads on `Q1A` and `Q1B` (`DMG2305UX-7`).
- **USB-C & Protection Placement (`J1`, `R1`, `R2`, `C12`, `D11`, `TP1`, `TP2`):**
  - Place `C12` (`100 nF 25 V`) directly at `J1` `VBUS` pin; place `R1` (`5.1 kΩ`) and `R2` (`5.1 kΩ`) adjacent to `J1` `A5` (`CC1`) and `B5` (`CC2`) with individual traces to `GND`.
  - Place `D11` (`SMBJ5.0A`) **downstream** of `Q1B` on `VIN_PROT` (never upstream on `VBUS_FUSED`).
  - Place `TP1` (`VBUS`) and `TP2` (`GND`) `2.5 mm` pad / `1.3 mm` drill TH pads near `J1` for optional captive USB cable entry via an M16 gland.

### 1.3 RefDes Parity Rule (On-PCB vs Off-Board)
- `circuit_design/COMPONENT_IDS.csv` defines **62 RefDes**:
  - **52 On-PCB parts:** `U1..U2`, `Q1A..Q1B`, `Q2..Q3`, `F1`, `D9..D15`, `L1..L2`, `R1..R14`, `C1..C12`, `J1..J4`, `TP1..TP2`, `H1..H4`.
  - **10 Off-Board parts:** `D1..D4` (via `J2`), `D5..D8` (via `J3`), `SW1` (via `J4`), and `SW1_BOOT` (weatherproof silicone boot mounted on `SW1`).
- M2 KiCad schematic MUST match these exact 62 RefDes 1:1 (marking off-board parts as DNP-on-driver-PCB or placing `D1..D8` on the Al MCPCB board).

---

## 2. M1 ↔ M3 (Mechanical & Thermal) Contract

### 2.1 Thermal Dissipation Budget (Fanless Sizing)
Nominal steady-state drive current = **`339.3 mA`** (`V_FB = 0.190 V`, `R3 = R4 = 0.56 Ω ±1%`).
Nominal USB input scenario: `V_USB = 5.0 V` through `20 AWG 1 m` cable + `J1` + `F1` + `Q1A/Q1B` (`R_path = 0.19 Ω` typ -> `V_IC = 4.605 V`, `I_in = 2.08 A` analytic / `2.10 A` ngspice).
Worst-case datasheet corners combine `sim_summary.json` `datasheet_spec` (`V_IC = 4.5 V`, `Rds = 0.33 Ω`, `V_FB = 202 mV`, `R_sense = 0.554 Ω`) and `4.75 V` max-R droop (`I_in = 2.40 A`).

| Subsystem | `8-ALL` Electrical (W) | `8-ALL` Nominal Heat (W) | `8-ALL` Worst-Case Datasheet Bound (W) | `4-UV` Nominal Heat (W) | Thermal Limit ($T_{j,\max}$ / $T_{\text{amb}}$) |
|---|---|---|---|---|---|
| **Each UV LED (`D1..D4`, `SST-10-UV`)** | `1.22 W` (`3.59 V × 0.339 A`) | **`0.74 W`** (`WPE ≥ 40%`) | `1.22 W` (`100%` heat bound) | **`0.74 W`** | **$T_{j,\max} = 100^\circ\text{C}$** ($R_{\theta J-s} = 1.4^\circ\text{C/W}$) |
| **Ch1 UV Array Total (`4× UV`)** | `4.87 W` | **`2.96 W`** | `4.87 W` | **`2.96 W`** | Target $T_{j,\text{UV}} \le 80^\circ\text{C}$ @ $30^\circ\text{C}$ amb |
| **Visible Blue (`D5, D6`, `XPEBRY-00S02`)** | `0.99 W` ea | `0.50 W` ea | `0.99 W` ea | `0.00 W` | $T_{j,\max} = 150^\circ\text{C}$ ($R_{\theta J-s} = 5.7^\circ\text{C/W}$) |
| **Visible Green (`D7`, `XPEBGR-00K01`)** | `0.92 W` | `0.66 W` | `0.92 W` | `0.00 W` | $T_{j,\max} = 150^\circ\text{C}$ ($R_{\theta J-s} = 9.0^\circ\text{C/W}$) |
| **Visible Cool White (`D8`, `XPEBWT-00H51`)** | `0.99 W` | `0.64 W` | `0.99 W` | `0.00 W` | $T_{j,\max} = 150^\circ\text{C}$ ($R_{\theta J-s} = 5.8^\circ\text{C/W}$) |
| **Ch2 Visible Array Total (`4× Vis`)** | `3.89 W` | **`2.30 W`** | `3.89 W` | `0.00 W` | Target $T_{j,\text{Vis}} \le 85^\circ\text{C}$ @ $30^\circ\text{C}$ amb |
| **`U1` (`LM3410XMY` Ch1 UV)** | `0.385 W` loss | **`0.385 W`** | **`0.994 W`** (`datasheet_spec`) | **`0.385 W`** | **$T_{j,\max} = 125^\circ\text{C}$** ($R_{\theta JA} = 53.7^\circ\text{C/W}$) |
| **`U2` (`LM3410XMY` Ch2 Vis)** | `0.246 W` loss | **`0.246 W`** | **`0.675 W`** (`datasheet_spec`) | `0.00 W` | **$T_{j,\max} = 125^\circ\text{C}$** ($R_{\theta JA} = 53.7^\circ\text{C/W}$) |
| **`D9` / `D10` (`B340A-13-F`)** | `0.129 W` ea | **`0.258 W`** tot | `0.364 W` tot (`0.182 W` ea) | `0.129 W` (`D9`) | $T_{j,\max} = 125^\circ\text{C}$ ($R_{\theta JA} = 50^\circ\text{C/W}$) |
| **`L1` / `L2` (`SRN6045-100M`)** | `0.065 W` / `0.041 W` | **`0.106 W`** tot | `0.218 W` tot | `0.065 W` (`L1`) | $T_{\max} = 125^\circ\text{C}$ |
| **`F1 + Q1A/Q1B + R3/R4` Passives** | `0.561 W` tot | **`0.561 W`** | **`0.958 W`** (`4.75 V` max-R droop) | `0.190 W` | `F1` $I_{\text{hold}}(55^\circ\text{C})=2.82\text{ A}$ |
| **Driver PCB Total Loss** | **`1.556 W`** | **`1.56 W`** | **`3.21 W`** (`0.994+0.675+0.364+0.218+0.958`) | **`0.77 W`** | **Keep PCB ambient $\le 55^\circ\text{C}$** |
| **Total Lamp + Cable USB Power (`5.0 V`)** | **`10.71 W`** (`~2.08–2.10 A`) | **`5.26 W` hs + `1.56 W` PCB** | `8.77 W` + `3.21 W` PCB | **`2.96 W` hs + `0.77 W` PCB** | `U1` $T_j \le 108.4^\circ\text{C}$ (DS @ `55 °C`) |

> **USB Source & Cable Contract (`8-ALL` Mode):** Specify **`20 AWG ≤ 1.5 m`** USB power cable (`R_cable ≤ 0.06 Ω`) and **`≥ 4.75 V`** USB power-bank output for `8-ALL` mode (`I_in = 2.40 A max`, safely below `MF-LSMF400/16X` `I_hold = 2.82 A @ 55 °C` and `2.64 A @ 60 °C`).

### 2.2 LED Array Geometry & Wiring Constraints
- **Emitter Mounting:** `4×` custom JLCPCB `1.0 W/m·K` Aluminum MCPCB dual-LED strips (`MECH-MCPCB-1..4`, ~`20 × 80 mm` each, or `8×` 20 mm Cu DTP star fallback) mounted on the 4 faces of a central aluminum heatsink core (`90°` azimuth spacing, 2 vertical tiers: 4× UV + 4× Visible, `360°` emission).
- **Wiring:** Two independent 2-wire series loops using `22 AWG` silicone-insulated wire (`≥ 105 °C` rated) routed cleanly through heatsink channels/end-cap pass-throughs back to `J2` (`UV+`, `UV-`) and `J3` (`VIS+`, `VIS-`).

### 2.3 Panel Cutouts & User Interface Dimensions
- **`SW1` (`E-Switch 100SP3T1B1M1QEH`) + `SW1_BOOT` (`C&K 759D02000`):**
  - **Cutout:** **`Ø 6.35 mm`** (`1/4"`) circular hole (`1/4-40` threaded bushing, `2.0–3.5 mm` max panel wall thickness for boot nut engagement).
  - Connected to PCB header `J4` via 3× `24 AWG` wires (`UV_EN`, `5V_COM`, `ALL_EN`).
- **Power Entry (`J1` USB-C vs M16 Captive Cable Gland):**
  - *Option A (Captive Weatherproof Cable — recommended for outdoor moth trapping):* **`M16 × 1.5`** circular cutout (**`Ø 16.2 mm`**) for IP68 nylon cable gland clamping a `≤ 1.5 m` `20 AWG` USB cable soldered to `TP1`/`TP2`.
  - *Option B (Direct PCB USB-C Receptacle):* Recessed **`9.3 × 3.6 mm`** slot (centered on `J1` `USB4085-GF-A` mid-plane) with external silicone dust/rain plug.
