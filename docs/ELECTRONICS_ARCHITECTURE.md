# LepiLED DIY Maxi Switch — Electronics Architecture (Rev 4.7)

## 1. Overview

The lamp runs exclusively from a **20 V USB-C PD** power source (laptop charger or 20 V PD power bank) using a single 2-layer `driver_pcb` (`36 × 46 mm`) driving two independent 4-LED strings (`4× UV-A` and `4× Visible`) mounted on off-board 20 mm Copper Direct-Thermal-Path (DTP) stars.

| Parameter | Value |
|---|---|
| **Power Input** | 20 V USB-C PD (`0.453 A` / `9.07 W` nominal in `8-ALL`; `0.586 A` worst-case corner) |
| **LED Drive Current** | `333 mA` nominal constant-current per 4S string (`AL8860WT-7` hysteretic buck) |
| **Driver PCB Loss & Efficiency** | `0.501 W` nominal PCB dissipation, **`94.2%`** system efficiency |
| **Hardware UVLO** | `17.48 V` ON / `16.66 V` OFF (`0.83 V` hysteresis, zero chatter across `0.30 Ω` cable impedance) |
| **Mode Switching** | Direct gold-contact `DPDT On-On-On` toggle (`OFF` / `4-UV` / `8-ALL`) |
| **Component Count** | `66` RefDes (`52` populated On-PCB, `4` isolated NPTH mounting holes, `10` off-board) |

For the history of earlier revisions and review changes, see [DESIGN_DECISIONS.md](DESIGN_DECISIONS.md).

---

## 2. Four Functional Subsystems

### Block 1 — 20 V USB-C PD Sink & Input Protection
- **USB-C Receptacle (`J1`, `GCT USB4085-GF-A`):** Through-hole 16-pin receptacle (`Ø0.40 mm` signal drills). Optional `24 V` bidirectional ESD diodes (`D13`, `D14` `ESD24V32D-C`, `25 pF`) are provided on `CC1`/`CC2` and left unpopulated (DNP) in the 2-reel Hybrid PCBA profile.
- **Overcurrent, Surge & Hot-Plug Damping (`F1`, `D11`, `R7`, `C10`, `C11`):**
  - `F1` (`Bourns MF-MSMF110/33X`, `33 V`, `40 A I_max`, `1.10 A` hold / `0.73 A @ 60 °C`) provides input overcurrent protection with `1.65×` voltage derating.
  - `D11` (`Vishay SMBJ22A-E3/52`, `22 V` unidirectional TVS placed inline directly after `F1`) clamps both positive inductive hot-plug surges (`V_BR = 24.4–26.9 V`) and negative transients (`-2.26 V` peak in SPICE).
  - Total sink capacitance across `VIN_20V` is **`8.0 µF` nominal / `8.8 µF` max** (`C11 = C2 = C3 = 1.0 µF` `0805` + `C8/C9/C14 = 100 nF` + `C10 = 4.7 µF` in series with `R7 = 1.0 Ω`), staying within the USB Type-C `<= 10 µF` sink limit (`cSnk`) with a well-damped `N = 1.42` RC ratio. At `85 °C` worst-case `21 V` hot-plug (`1.0 µH` cable), peak bus voltage is `26.60 V` (`< 32 V` `CH224A` max) and peak surge current through `F1` is `28.85 A` (`< 40 A` `I_max`).
- **USB-C PD Sink Controller (`U3`, `WCH CH224A`, `ESSOP-10`):**
  - Integrates internal `5.1 kΩ` dead-battery `R_d` pull-downs on `CC1`/`CC2` and `32 V`-tolerant `VHV`, `VBUS`, and `PG` pins (`1.0 mm` leaded pitch).
  - `Pin 8 (VBUS)` shorts directly to `Pin 1 (VHV)` / `VIN_20V` per the `CH224A` datasheet.
  - `Pin 9 (CFG1)` is strapped to `GND` through `R9 = 120 kΩ ±1%` (single-resistor `20 V` mode, which disables `28 V` EPR decoding on `CFG2`/`CFG3`).
  - Active-low `Pin 10 (PG)` sinks `~1.6 mA` through red status LED `D12` (`KT-0603R`) and the `R13`/`R10` (`10 kΩ` / `10 kΩ`) divider whenever `20 V` PD is negotiated.

### Block 2 — Hysteretic Hardware UVLO & Mode Switch Interface
- **Hysteretic UVLO (`U4`, `U5`, `R14–R21`, `C14`, `C15`, `Q2`, `Q3`):**
  - Keeps both LED drivers off whenever a charger falls back to `5 / 9 / 12 / 15 V`.
  - `U5` (`Hottech TL431`, `2.500 V ±1%`, biased via `R14 = 10 kΩ`) provides the reference rail (`V_REF`) for both comparator stages and the switch ESD clamps.
  - `U4A` (`onsemi LM393DR2G`, `SOIC-8` Basic) compares `VIN_20V` through `R15 = 30.0 kΩ`, `R16 = 5.1 kΩ`, and `C15 = 100 nF`, with `R17/R18 = 100 kΩ/100 kΩ` setting a `0 V / 10 V` midpoint on `UVLO_OK` and `R19 = 270 kΩ` providing **`0.83 V` positive-feedback hysteresis** (`V_ON = 17.48 V`, `V_OFF = 16.66 V`). *(For sustained sub-zero or `> 30 °C` sealed-bay operation, `onsemi LM2903DR2G` `C57474` is a drop-in `-40..+105 °C` replacement for `U4`.)*
  - `U4B` inverts `UVLO_OK` to `UVLO_FAULT`, pulled up via the `R20 = 56.0 kΩ` / `R21 = 100 kΩ` divider (`3.21 V` at `5 V`, `<= 15.36 V` during `85 °C` hot-plug) to drive `Q2`/`Q3` (`2N7002`), clamping `U1_CTRL` and `U2_CTRL` to `< 0.1 mV` below UVLO.
- **Direct Gold Dry-Circuit Mode Switch (`SW1`, `SW1_BOOT`, `J4`, `R5`, `R6`, `D15`, `D16`):**
  - `SW1` (`C&K 7211SYZBE`, gold-contact `DPDT On-On-On` with `759D02000` silicone boot) wires directly to `J4` (`J4.2 = GND`, `J4.1 = SW_UV_IN`, `J4.3 = SW_VIS_IN`).
  - Dual series ESD clamps `D15`/`D16` (`Nexperia BAV99`, clamping to `GND` and `V_REF`) and `R5`/`R6` (`1.0 kΩ`) protect both `AL8860` `CTRL` inputs while pulling a grounded channel cleanly below the `200 mV` shutdown threshold.
  - **Positions:** `OFF` grounds both channels; `4-UV` releases `U1` while grounding `U2`; `8-ALL` releases both.

### Blocks 3 & 4 — Dual `AL8860WT-7` Constant-Current Buck Drivers (`333 mA`)
- **Current Regulation:** High-side sense resistors `R3 = R4 = 0.30 Ω ±1%` (`Bourns CRL1206-FW-R300ELF`, Kelvin-sensed to `VIN` and `SET`) regulate `I_LED = 0.100 V / 0.30 Ω = 333.3 mA`. Each buck has local `1.0 µF` (`C2`/`C3`) + `100 nF` (`C8`/`C9`) input decoupling, a `68 µH` shielded inductor (`L1`/`L2`, `SRN6045-680M`, `1.0 A I_sat`), and a `40 V 3 A` Schottky catch diode (`D9`/`D10`, `MDD SS34`).
- **Staggered Soft-Start & Damped Output Shunts:** `C6 = 1.0 nF` (`1.5 ms`) and `C7 = 4.7 nF` (`7.0 ms`) stagger channel turn-on. Across `J2` and `J3`, `100 nF` + `10.0 Ω` (`C4/R22`, `C5/R23`) damp harness EMI while limiting accidental open-LED live-reconnect peaks to `0.419 A` (UV) and `0.700 A` (Vis).
- **Fault Handling:** Open-LED operation safely halts switching (`0 mA`), and a shorted LED string stays current-regulated at `339 mA` (`420 mA` peak).

---

## 3. Verification Summary ([sim_summary.json](../circuit_design/sim/outputs/sim_summary.json))

- **6 `ngspice` Benches:** **15/15 checks PASS** — nominal `I_UV = 331.4 mA`, `I_VIS = 337.3 mA`, `VIN_pp = 111.6 mV`, `V_REF = 2.509 V`; zero UVLO chatter across a `0.30 Ω` ramp; `85 °C` `21 V` hot-plug `V_pk = 26.60 V`, `F1_pk = 28.85 A`, `V_GS_pk = 15.36 V`; cold `5 V` attach `8.92 A`; negative transient `-2.26 V`; open-LED live-reconnect `0.419 A / 0.700 A`; shorted-LED `339.4 mA`.
- **Datasheet Corner Sweep (`18.5–21.5 V`, `-10..+55 °C`, all tolerances):** **`2,565 / 2,565 PASS`** (`P_PCB_max = 0.892 W`, `I_in_max = 0.586 A`, `T_j,max = 69.8 °C`).
- **Full-Parameter Monte Carlo (`N = 2,000`):** **`2,000 / 2,000 (100.0%) PASS`** (`I_UV = 329.9 ± 4.5 mA`, `I_VIS = 331.9 ± 4.5 mA`, `P_PCB = 0.511 W` mean, `94.4%` mean efficiency, `V_ON ∈ [17.09, 17.86] V`, `V_OFF ∈ [16.29, 17.01] V`).
