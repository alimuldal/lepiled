# LepiLED DIY Maxi Switch — Electronics Architecture (Rev 4.1)

## 1. Architectural Evolution: `20 V` USB-C PD Only + Dual Constant-Current Buck
Building on the Rev 4.0 shift from `5 V` boost to `20 V` USB-C PD + dual `AL8860WT-7` constant-current bucks, **Rev 4.1** hardens every safety, ESD, UVLO hysteresis, and derating margin surfaced by two independent adversarial reviews while removing the unused Auxiliary DC path and steering-FET switch overhead.

| Metric | Legacy Rev 3 (`5 V` Boost) | Rev 4.0 (Dual-Input Buck) | **Rev 4.1 (USB-C Only, Hardened)** |
|---|---|---|---|
| Input Architecture | `5 V` USB-C (`2.15–3.24 A`) | `20 V` USB-C PD + Aux `TP1/TP2` | **`20 V` USB-C PD Only (`0.455 A` nom / `0.581 A` max)** |
| Driver PCB Loss (nom / worst) | `1.60 W` / `4.39 W` | `0.50 W` / `0.82 W` | **`0.550 W` / `0.797 W`** (`93.8%` sys eff) |
| Load Switch & Input Protection | `30 V` FET / discrete OVP | `2× 30 V DMN3404L` + `24 V` PTC + `SMBJ22CA` | **Single `40 V DMN4035L-7` + `33 V MF-MSMF110/33X` + Uni `SMBJ22A` + `CC1/CC2` ESD** |
| Hardware UVLO | None (fixed `5 V`) | `17.25 V` comparator (`0 V` hyst) | **`0.90 V` hysteretic `LM393B` (`V_ON = 17.54 V`, `V_OFF = 16.64 V`, `0` chatter)** |
| Mode Switch (`SW1`) | Silver SP3T + high-side | Silver SP3T + `BAT54`/`BSS138` bias | **Gold `C&K 7211SYZBE` DPDT On-On-On wired direct to `J4` + `5 V` ESD** |
| Bottom Heatsink Required | `£24.60` `SK LED R 80 SA` | `£5.88` `SK 578/50 SA` | **None (`MECH-LID-BOT` sealed plastic lid; passes 20/20 `22–30 °C` & 5/5 `35 °C`)** |

---

## 2. Four Functional Subsystems (`75` Unique RefDes in `COMPONENT_IDS.csv`)

### Block 1 — USB-C PD 3.1 `20 V / 1.0 A` Sink & Input Protection
- **USB-C Receptacle (`J1`, `GCT USB4085-GF-A`):** `R1, R2 = 5.1 kΩ ±1%` provide dead-battery `CC1`/`CC2` `R_d` pull-downs (`AP33771C` Fig. 1). Dedicated `24 V` unidirectional ESD diodes (`D13`, `D14` `Bourns CDSOD323-T24`, `3 pF`, `±15 kV` IEC 61000-4-2) protect `CC1`/`CC2` even against an adjacent-pin `20 V` `VBUS` short.
- **Overcurrent, Surge & Hot-Plug Protection (`F1`, `D11`, `C1`, `R7`, `C10`):**
  - `F1` (`Bourns MF-MSMF110/33X`, `33 V`, `1.10 A` hold / `0.73 A @ 60 °C`) gives `1.65×` voltage derating on `20 V` (`1.50×` at `22 V` TVS `V_RWM`) and `1.26×` hold margin above the `0.581 A` worst-case input current.
  - `D11` (`Vishay SMBJ22A-E3/52`, `22 V` **unidirectional** TVS, zero-stub fly-by immediately downstream of `F1`) clamps both positive hot-plug surges (`V_BR = 24.4–26.9 V`) and negative cable-inductance transients (`-2.26 V` peak in SPICE).
  - Consolidated `6.7 µF` (`<= 10 µF` USB-C PD spec) Middlebrook RC damper (`C1 = 1.0 µF`, `C10 = 4.7 µF` in series with `R7 = 1.0 Ω`, plus `C11 = 1.0 µF` on `U3.VCC`) holds `85 °C / 1.0 µH / -35%` derated hot-plug transients to **`26.02 V`** (`<< 31 V` `AP33771C` and `<< 40 V` `Q1` abs max).
- **PD Sink Controller & Load Switch (`U3`, `Q1`):**
  - `U3` (`Diodes AP33771CFBZ-13-FA02`): `R9 = 39.0 kΩ ±1%` (`VSEL`) requests `20 V`; `R10 = 82.0 kΩ ±1%` (`ISEL`) requests `>= 1.0 A` (`1.1 A` hardware OCP across the Kelvin-routed `R8 = 5 mΩ` `WSL12065L000FEA` shunt); `R12 = 200 Ω` (`0805`) limits `VOUT` active discharge; `R13 = 1.0 kΩ` drives green status LED **`D12`** (`4 s` breathing = `20 V VOUT ON`, steady = PDO mismatch); `DP`/`DN` remain open (`no_connect`) to avoid outdoor moisture false trips.
  - `Q1` (single `40 V` `Diodes DMN4035L-7`, `52 mΩ max @ 4.5 V`, `SOT-23-3`) is slew-rate limited via `R11 = 6.2 kΩ` + `C13 = 47 nF` to `GND` (holding `VOUT` turn-on inrush to **`0.582 A < 1.0 A`**) with `R21 = 1.0 MΩ` bleed to `GND` guaranteeing an OFF default when unpowered.

### Block 2 — Hysteretic Hardware UVLO & Direct Gold `DPDT` Maxi-Switch
- **Hysteretic `LM393B` UVLO (`U4`, `U5`, `R14–R20`, `Q2`, `Q3`):**
  - Because `AP33771C` falls back to `5/9/12/15 V` on non-20V USB chargers, `U5` (`LM4040BIM3-2.5/NOPB`, `2.500 V ±0.2%`, biased by `R14 = 10 kΩ`) and `U4` (`TI LM393BIDR`) supervise `VIN_20V`.
  - `U4A` monitors `VIN_20V` through `R15 = 59.0 kΩ` / `R16 = 10.0 kΩ` / `C15 = 100 nF` (`fc = 186 Hz`), with `R17 = 100 kΩ` / `R18 = 100 kΩ` forming a `0 V / 10 V` midpoint on `UVLO_OK` (keeping `U4B IN-` safely inside the `LM393B` common-mode range) and **`R19 = 510 kΩ`** providing **`0.90 V` positive-feedback hysteresis**: **`V_ON = 17.54 V`**, **`V_OFF = 16.64 V`** (Monte Carlo `V_ON ∈ [17.21, 17.84] V`, `V_OFF ∈ [16.33, 16.92] V`). Verified in SPICE across a `0.30 Ω` source ramp with **zero chatter**.
  - `U4B` inverts `UVLO_OK` to `UVLO_FAULT` (pulled up to `2.500 V` `V_REF` via `R20 = 47.0 kΩ`), driving `Q2` and `Q3` (`BSS138`) to clamp `U1_CTRL` and `U2_CTRL` to **`0.027 mV`** (`<< 200 mV` disable threshold) whenever `VIN_20V` is below UVLO (`5/9/12/15/15.75 V` sources yield `I_LED = 0.000 mA`).
- **Direct Gold Dry-Circuit Maxi-Switch (`SW1`, `SW1_BOOT`, `J4`, `R5`, `R6`, `D15`, `D16`):**
  - `SW1` (`C&K 7211SYZBE`, gold-plated `0.4 VA max @ 20 V` `DPDT On-On-On`, sealed with `C&K 759D02000` silicone boot) wires directly to `J4` (`J4.2 = GND` tied to common lugs `2+5`; `J4.1 = SW_UV_IN` to lug `6`; `J4.3 = SW_VIS_IN` to lug `3`; lugs `1/4` NC).
  - `D15`/`D16` (`Bourns CDSOD323-T05`, `5.0 V` ESD diodes) and `R5`/`R6` (`1.0 kΩ`) protect `U1_CTRL` and `U2_CTRL` against ESD at the external switch harness while maintaining `V(U_CTRL) <= 50 mV` (`< 200 mV` OFF threshold) whenever a pole closes to `GND`.
  - **Positions:** Pos 1 (`OFF`) grounds both `J4.1` and `J4.3`; Pos 2 (`4-UV`) releases `J4.1` (`U1` ON) while grounding `J4.3` (`U2` OFF); Pos 3 (`8-ALL`) releases both (`U1` and `U2` ON).

### Blocks 3 & 4 — Dual `AL8860WT-7` Constant-Current Buck LED Drivers (`333 mA`)
- **Topology (`U1`/`U2` `AL8860WT-7`, `TSOT25`):** High-side current sense `R3 = R4 = 0.30 Ω ±1%` (`Bourns CRL1206-FW-R300ELF`, `33 mW`, dedicated Kelvin `VIN` + `SET` traces) sets `I_LED = 0.100 V / 0.30 Ω = 333.3 mA`. Local `4.7 µF` `1206` X7R bulk capacitors (`C2`, `C3` — total `VOUT` capacitance `<= 10 µF` USB-C PD limit) + `100 nF` HF bypass (`C8`, `C9`) sit directly across `VIN–GND`.
- **Inductors & Freewheeling Diodes:** `L1 = L2 = 68 µH ±20%` (`Bourns SRN6045-680M`, `I_sat = 1.00 A` vs `0.407 A` peak -> `2.46×` saturation margin) + `D9 = D10 = B340A-13-F` (`40 V 3 A` SMA Schottky). Switching frequency is `~385 kHz` (Ch1 UV) and `~482 kHz` (Ch2 Vis), with `t_ON >= 1.0 µs` (`>= 500 ns` min) and `f_SW <= 683 kHz` (`<= 1.0 MHz` max) across all corners.
- **Staggered Soft-Start & Damped Output Shunts:** `C6 = 1.0 nF` (`1.5 ms`) and `C7 = 4.7 nF` (`7.0 ms`) stagger channel turn-on. Across `J2` and `J3`, `C4/R22` and `C5/R23` (`100 nF + 6.8 Ω`) attenuate harness EMI while limiting accidental open-LED live-mate surge currents to **`0.532 A`** (UV, `<= 1.0 A` max) and **`0.922 A`** (Vis, `<= 1.2 A` max).
- **Inherent Fault Protection:** Verified in `ngspice` — open-LED halts `SW` (`I_UV = 0 mA`); shorted-LED regulates inductor current at `338.7 mA` (`419 mA` peak) with zero thermal runaway.

---

## 3. Verification Summary ([sim_summary.json](file:///home/alimuldal/src/lepiled/circuit_design/sim/outputs/sim_summary.json))
- **6/6 `ngspice` Nominal & Fault Benches:** **15/15 assertions PASS** (nominal `I_UV = 329.9 mA`, `I_VIS = 336.2 mA`, `V_REF = 2.508 V`, `0` UVLO chatter on `0.30 Ω` ramp, `85 °C` hot-plug `26.02 V`, `Q1` inrush `0.582 A`, negative transient `-2.26 V`, open-LED live-mate `0.532 A / 0.922 A`, short-LED `338.7 mA`).
- **Datasheet Corner Sweep (`18.5–24.0 V`, `-10..+55 °C`, all tolerances):** **`2,565 / 2,565 PASS`** (`P_PCB_max = 0.797 W`, `I_in_max = 0.581 A`, `T_jmax = 69.8 °C`).
- **Full-Parameter Monte Carlo (`N = 2,000`):** **`2,000 / 2,000 (100.0%) PASS`** (`I_UV = 329.9 ± 4.5 mA`, `I_VIS = 331.9 ± 4.5 mA`, `P_PCB = 0.561 W` mean / `0.618 W` max, `V_ON = 17.54 ± 0.08 V`, `V_OFF = 16.64 ± 0.08 V`, `V_HYST = 0.902 ± 0.007 V`).
