# LepiLED DIY Maxi Switch — Electronics Architecture (Rev 4.8)

## 1. Overview

The lamp runs exclusively from a **20 V USB-C PD** power source (laptop charger or 20 V PD power bank) using a single 2-layer **ENIG** `driver_pcb` (`36 × 46 mm`) with **Full-SMD JLCPCB PCBA** (`48` machine-reflowed SMDs; only `J1..J4` THT hand-soldered at home), driving two independent 4-LED strings (`4× UV-A` and `4× Visible`) mounted on off-board 20 mm LED stars.

| Parameter | Value |
|---|---|
| **Power Input** | 20 V USB-C PD (`0.454 A` / `9.08 W` nominal in `8-ALL`; `0.581 A` worst-case corner) |
| **LED Drive Current** | `333 mA` nominal constant-current per 4S string (`AL8860WT-7` hysteretic buck) |
| **Driver PCB Loss & Efficiency** | **`0.512 W`** nominal PCB dissipation (`0.850 W` worst-case corner), **`94.1%`** system efficiency |
| **Hardware UVLO** | `17.48 V` ON / `16.66 V` OFF (`0.83 V` hysteresis; SPICE `17.65 / 16.53 V`, zero chatter across `0.30 Ω` source Z) |
| **Mode Switching** | Direct gold-contact `DPDT On-On-On` toggle (`OFF` / `4-UV` / `8-ALL`) |
| **Component Count** | `72` RefDes (`54` PCBA = `48` JLCPCB SMD + `4` THT `J1..J4` + `2` DNP `D13/D14`; `4` isolated NPTH `H1..H4`; `4` bare ENIG test pads `TP1..TP4`; `10` off-board) |

For the history of earlier revisions and review changes, see [DESIGN_DECISIONS.md](DESIGN_DECISIONS.md).

---

## 2. Four Functional Subsystems

### Block 1 — 20 V USB-C PD Sink & Input Protection
- **USB-C Receptacle (`J1`, `GCT USB4085-GF-A`):** Through-hole 16-pin receptacle (`Ø0.40 mm` signal drills, ENIG finish, full-connection GND pins `A1/A12/B1/B12` tied directly to `SH1/SH2`). Optional `24 V` bidirectional ESD diodes (`D13`, `D14` `ESD24V32D-C`, `25 pF`) sit on `CC1`/`CC2` as paste-free DNP footprints.
- **Overcurrent, Surge & Hot-Plug Damping (`F1`, `D11`, `R7`, `C10`, `C11`):**
  - `F1` (**`Littelfuse 046801.5NRHF`**, `1206` Slo-Blo SMD fuse, `1.5 A / 63 V DC`, **`50 A` interrupt rating**, `I²t = 0.288 A²s`, `R_cold = 0.044 Ω`, LCSC `C151143`) replaces the Rev 4.7 PTC polyfuse, providing high breaking capacity, zero elevated-temperature hold-current collapse, and **`107×` melting `I²t` margin** (`0.00270 A²s` during `85 °C` hot-plug).
  - `D11` (**`RUILON SMBJ22A`**, `22 V` unidirectional TVS, LCSC `C10214`, placed zero-stub inline directly after `F1`) clamps both positive inductive hot-plug surges (`V_BR = 24.4–26.9 V`, modeled with real `TBV1 = 9.6e-4 /°C` tempco) and negative transients (`-2.27 V` peak in SPICE).
  - `R7` (**`UNI-ROYAL 25121WF100KT4E`**, `1.0 Ω ±1%`, **`2512 1.0 W` pulse-rated**, LCSC `C11254`) in series with `C10` (`4.7 µF 50 V X7R 1206`) safely absorbs the `208.2 W` `3–5 µs` hot-plug damping pulse (vs `600 W` `2512` pulse limit; replaces the undersized `0805` resistor from Rev 4.7).
  - Total sink capacitance across `VIN_20V` is **`8.0 µF` nominal / `8.8 µF` max** (`C11 = C2 = C3 = 1.0 µF` `0805` + `C8/C9/C14 = 100 nF` + `C10 = 4.7 µF`), staying inside the USB Type-C `<= 10 µF` `cSnk` spec.
- **USB-C PD Sink Controller (`U3`, `WCH CH224A`, `ESSOP-10`, LCSC `C42459160`):**
  - Integrates internal `5.1 kΩ` dead-battery `R_d` pull-downs on `CC1`/`CC2` and `32 V`-tolerant `VHV`, `VBUS`, and `PG` pins (`1.0 mm` leaded pitch).
  - `Pin 8 (VBUS)` shorts directly to `Pin 1 (VHV)` / `VIN_20V`; `Pin 9 (CFG1)` is strapped via `R9 = 120 kΩ ±1%` to `GND` (single-resistor `20 V` mode).
  - Active-low `Pin 10 (PG)` drives red bench diagnostic LED `D12` (`KT-0603R`, `~1.6 mA` via `R13`/`R10 = 10 kΩ / 10 kΩ`) whenever `20 V` PD is active — visible directly on top of the lid-mounted PCB during bench testing.
- **Bench Test Pads (`TP1..TP4`):** Four `$0` bare `1.0 mm` ENIG SMD pads on `F.Cu` exposing `VIN_20V`, `V_REF`, `UVLO_OK`, and `GND` for effortless multimeter bring-up.

### Block 2 — Hysteretic Hardware UVLO, Damped `V_REF` ESD Sink & Mode Switch
- **Hysteretic UVLO (`U4`, `U5`, `R14–R21`, `R24`, `C14–C16`, `Q2`, `Q3`):**
  - Keeps both LED drivers off whenever a charger falls back to `5 / 9 / 12 / 15 V`.
  - `U5` (`Hottech TL431`, `2.500 V ±1%`, `0..+70 °C` commercial rating, biased via `R14 = 10 kΩ`) provides `V_REF`.
  - **Damped ESD Bypass (`R24 = 10.0 Ω` `0805` Basic `C17415` + `C16 = 100 nF` `0603` Basic `C14663`):** Absorbs positive ESD pulses shunted by `D15`/`D16` right at `V_REF` while keeping `Q <= 1` critical damping (guaranteed unconditional `TL431` loop stability outside Curve A's oscillation region) AND keeping `τ_VREF = 1.0 ms < 3.0 ms = τ_UVLO_SENSE` (zero startup false-trigger!).
  - `U4A` (`onsemi LM393DR2G`, `SOIC-8` Basic, `0..+70 °C`; drop-in industrial alt `LM2903DR2G` `C57474`) compares `VIN_20V` via `R15 = 30.0 kΩ`, `R16 = 5.1 kΩ`, `C15 = 100 nF`, `R17/R18 = 100 kΩ/100 kΩ`, and `R19 = 270 kΩ` (`V_ON = 17.48 V`, `V_OFF = 16.66 V`, `0.83 V` hysteresis).
  - `U4B` inverts `UVLO_OK` to `UVLO_FAULT` (`R20 = 56.0 kΩ` / `R21 = 100 kΩ` divider: `3.21 V` at `5 V`, `<= 15.39 V` during `85 °C` hot-plug) driving `Q2`/`Q3` (`2N7002`) to clamp `U1_CTRL`/`U2_CTRL` below `0.1 mV` under UVLO.
- **Direct Gold Dry-Circuit Mode Switch (`SW1`, `SW1_BOOT`, `J4`, `R5`, `R6`, `D15`, `D16`):**
  - `SW1` (`C&K 7211SYZBE` gold `DPDT On-On-On` + `759D02000` silicone boot) wires directly to `J4` (`1:SW_UV_IN`, `2:GND`, `3:SW_VIS_IN`), protected by `D15`/`D16` (`BAV99`) and `R5`/`R6` (`1.0 kΩ`).

### Blocks 3 & 4 — Dual `AL8860WT-7` Constant-Current Buck Drivers (`333 mA`)
- **Current Regulation:** High-side sense resistors `R3 = R4 = 0.30 Ω ±1%` (**`UNI-ROYAL 1206W4F300LT5E`**, `0.25 W`, `7.5×` derated at `33 mW`, LCSC `C59882`, Kelvin-sensed to `VIN` and `SET`) regulate `I_LED = 333.3 mA`. Each buck has local `1.0 µF` (`C2`/`C3`) + tucked `100 nF` (`C8`/`C9`) input decoupling, a `68 µH` shielded inductor (`L1`/`L2`, **`Sunlord SWPA6045S680MT`**, `I_sat = 1.1 A`, `I_rms = 0.95 A`, `DCR_max = 0.376 Ω`, LCSC `C53663`), and a `40 V 3 A` Schottky catch diode (`D9`/`D10`, `MDD SS34`).
- **Staggered Soft-Start & Damped Output Shunts:** `C6 = 1.0 nF` (`1.5 ms`) and `C7 = 4.7 nF` (`7.0 ms`) stagger turn-on. `C4/R22` and `C5/R23` (`100 nF + 10.0 Ω`) damp harness EMI while limiting accidental open-LED live-reconnect peaks to `0.418 A` (UV) and `0.698 A` (Vis).
- **Balanced 360° Visible LED Perimeter Order (Ch2):** `J3.1 → D5 (Royal Blue, Face 1 +X) → D7 (Green, Face 2 +Y) → D6 (Royal Blue, Face 3 -X) → D8 (Cool White, Face 4 -Y) → J3.2`, placing the two Royal Blue emitters on opposite faces.

---

## 3. Verification Summary ([sim_summary.json](../circuit_design/sim/outputs/sim_summary.json))

- **6 `ngspice` Benches (`libngspice.so.0`):** **16/16 checks PASS** — nominal `I_UV = 330.2 mA`, `I_VIS = 335.9 mA`, `VIN_pp = 118.8 mV`, `V_REF = 2.509 V`; zero UVLO chatter across a `0.30 Ω` ramp (`17.65 V / 16.53 V`, `V_OK_min_post = 8.07 V`); `85 °C` `21 V` hot-plug (with real TVS `TBV1`) `V_pk = 26.67 V`, `F1_pk = 29.02 A (< 50 A)`, `I²t = 0.00270 A²s (107× margin)`, `R7_pk = 208.2 W (< 600 W 2512)`, `V_GS_pk = 15.39 V`; cold `21 V` hot-plug `40.43 A (< 50 A)`; `5 V` attach `9.45 A`; negative transient `-2.27 V`; open-LED live-reconnect `0.418 A / 0.698 A`; shorted-LED `339.4 mA`.
- **Datasheet Corner Sweep (`18.5–21.5 V`, `-10..+55 °C`, `T_bay = T_amb + 15 °C`, all tolerances & overheads):** **`2,565 / 2,565 PASS`** (`P_PCB_max = 0.850 W`, `I_in_max = 0.581 A`, `T_j,max = 84.8 °C`).
- **Full-Parameter Monte Carlo (`N = 2,000`):** **`2,000 / 2,000 (100.0%) PASS`** (`I_UV = 329.9 ± 4.5 mA`, `I_VIS = 332.0 ± 4.6 mA`, `P_PCB = 0.535 W` mean, `94.1%` mean efficiency, `V_ON ∈ [17.15, 17.88] V`, `V_OFF ∈ [16.34, 17.03] V`).
