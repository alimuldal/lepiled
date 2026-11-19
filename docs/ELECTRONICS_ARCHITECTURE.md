# LepiLED DIY Maxi Switch — Electronics Architecture (Rev 4.0 / Option 2)

## 1. Architectural Decision: Why `20 V` USB-C PD + Dual Constant-Current Buck
Following independent circuit and PCB reviews of the initial `5 V` boost architecture, the design pivoted to **Option 2: `20 V` USB-C PD 3.1 sink (`AP33771CFBZ-13-FA02`) feeding dual `40 V` constant-current hysteretic buck LED drivers (`AL8860WT-7`)**.

| Metric | Old Rev 3 (`5 V` Dual `LM3410` Boost) | New Rev 4.0 (`20 V` PD Dual `AL8860` Buck) |
|---|---|---|
| Input Current (`8-ALL`, nominal) | `2.15 A` (`3.24 A` worst-case droop) | **`0.46 A`** (`0.58 A` worst-case corner) |
| Driver PCB Power Loss (nominal / worst) | `1.60 W` / `4.39 W` | **`0.50 W`** / **`0.82 W`** (`5.3×` lower!) |
| Overall System Efficiency | `~81%` | **`~94.3%`** |
| Open-LED & Short-LED Protection | External Zener OVP (`D13/D14`) + `FB` risk | **Inherent inside `AL8860WT-7`** |
| USB-C Cable & Laptop Charger Support | Required `<= 0.4 m 18 AWG` cable (`5 V 3.5 A`) | **Any `45 W+` USB-C PD laptop charger / `20 V` PD bank + standard `1–3 m` cable** |
| External Bottom Heatsink Required | `£24.60` `SK LED R 80 SA` (`Ø80×70 mm`) | **`£5.88` `SK 578/50 SA` (`Ø60×50 mm`) — passes 20/20 thermal cases!** |
| Active Protection / OVP Complexity | 19-part discrete `TL431` + 3-BJT latch | **Integrated `AP33771C` PD + 5-part `LM393B`/`LM4040` `17.25 V` UVLO** |

---

## 2. Four Functional Subsystems (72 Unique RefDes in `COMPONENT_IDS.csv`)

### Block 1 — USB-C PD 3.1 `20 V / 1.0 A` Sink & Auxiliary `18–24 V` DC Entry
- **USB-C Receptacle (`J1`, `GCT USB4085-GF-A`):** `R1, R2 = 5.1 kΩ ±1%` provide dead-battery `CC1`/`CC2` `R_d` pull-downs (`AP33771C` Fig. 1).
- **Overcurrent & Hot-Plug Protection (`F1`, `D11`, `C1`, `R7`, `C10`):**
  - `F1` (`Bourns MF-MSMF150/24X`, `24 V`, `1.50 A` hold / `1.00 A @ 60 °C`) gives `>= 1.72×` hold margin above the `0.58 A` worst-case input current.
  - `D11` (`Vishay SMBJ22CA-E3/52`, `22 V` bidirectional TVS, `V_BR = 24.4–26.9 V`) pairs with an overdamped Middlebrook RC damper (`C1 = 1.0 µF`, `C10 = 4.7 µF` in series with `R7 = 1.0 Ω`, plus `C11 = 1.0 µF` on `U3.VCC`, totaling `6.7 µF <= 10 µF` USB-C PD limit). Even under a `21 V`, `1.0 µH` inductive hot-plug at `85 °C` with `-35%` DC-bias-derated ceramics, `V_VBUS_FUSED` peaks at **`26.65 V`** (`< 30 V` `DMN3404L` and `< 31 V` `AP33771C` abs max).
- **PD Sink Controller (`U3`, `Diodes AP33771CFBZ-13-FA02`):**
  - `R9 = 39.0 kΩ ±1%` (`VSEL`) requests a `20 V` PDO (`AP33771C` Table 2).
  - `R10 = 82.0 kΩ ±1%` (`ISEL`) requests `>= 1.0 A` and sets hardware OCP at `1.1 A` across the `R8 = 5 mΩ` Kelvin shunt (`ISENP` upstream, `VCC` downstream).
  - `Q1A, Q1B` (`DMN3404L-7`, `30 V`, `<= 82 mΩ @ 3 V` / `<= 42 mΩ @ 4.5 V`) wired back-to-back common-source provide soft turn-on (`R11 = 6.2 kΩ`, `C13 = 47 nF`) and block reverse current if `TP1` is powered while `J1` is unplugged (`< 0.001 mV` leakage).
  - `R12 = 200 Ω` (`0805`) limits `U3.VOUT` discharge current; `R13 = 1.0 kΩ` drives the Green status LED `D15`. `DP`/`DN` are left open (`no_connect`) per Table 1 to waive moisture-detection false trips outdoors.
- **Auxiliary `18–24 V` DC Input (`TP1`, `TP2`, `F2`, `D13`):** Accepts a captive M16 gland `20 V` PD trigger pigtail, `18–24 V` tool battery, or bench supply via `F2` (`MF-MSMF150/24X`) and `D13` (`B340A-13-F`, blocks `-40 V` reverse polarity and `J1` back-feed; `-30 V` fault keeps `VIN_20V = -0.094 V` well inside `-0.3 V` IC abs max).

### Block 2 — Hardware `17.25 V` UVLO & Ground-Referenced Maxi-Switch
- Because `AP33771C` has `V_VSELMIN = 5 V` and falls back to `5/9/12/15 V` on non-20 V sources, `U5` (`LM4040BIM3-2.5/NOPB`, `2.500 V ±0.2%`, biased by `R14 = 10 kΩ`) and `U4` (`LM393BIDR` dual open-collector comparator) monitor `VIN_20V` via `R15 = 59.0 kΩ` / `R16 = 10.0 kΩ` / `C15 = 100 nF` (`V_TH = 17.25 V`, Monte Carlo `[17.02, 17.47] V`).
- Below `17.25 V`, `U4.1OUT` and `U4.2OUT` directly sink `U1_CTRL` and `U2_CTRL` to **`0.15 mV`** (`<< 200 mV` `AL8860` disable threshold), cleanly locking out `5/9/12/15/15.75 V` sources (`I_LED = 0.000 mA`) and enabling smoothly above `17.5 V` (`18.5–24 V`).
- **Ground-Referenced Maxi-Switch (`J4`, `SW1`, `D14`, `R17`, `R5`, `R6`, `D12`, `Q2`, `Q3`):**
  - `SW1` common pin (`J4.2`) is `GND` (touch-safe, zero live rail at the exterior toggle!).
  - `R17 (22 kΩ)` + `D14 (BZT52C5V1, 5.1 V)` generate `V_SW_BIAS = 5.1 V`, pulling `Q2`/`Q3` (`BSS138`) gates high through `R5 = R6 = 100 kΩ` so both drivers default **OFF** when `SW1` is centered.
  - **`4-UV` (`J4.1 = GND`):** `Q2` turns OFF -> `U1_CTRL` floats high (`U1` ON); `Q3` stays ON -> `U2` OFF.
  - **`8-ALL` (`J4.3 = GND`):** `Q3` turns OFF (`U2` ON), and `D12` (`BAT54-7-F`, `V_F = 162 mV @ 51 µA << 800 mV` `BSS138` `V_GS(th)_min`) pulls `Q2.G` low -> `Q2` turns OFF (`U1` ON).

### Blocks 3 & 4 — Dual `AL8860WT-7` Constant-Current Buck LED Drivers (`333 mA`)
- **Topology (`U1`/`U2` `AL8860WT-7`, `TSOT25`):** High-side current sense `R3 = R4 = 0.30 Ω ±1%` (`Bourns CRL1206-FW-R300ELF`, `33 mW`) sets `I_LED = 0.100 V / 0.30 Ω = 333.3 mA`.
- **Inductors & Freewheeling Diodes:** `L1 = L2 = 68 µH ±20%` (`Bourns SRN6045-680M`, `I_sat = 1.00 A` vs `0.408 A` peak -> `2.45×` saturation margin) + `D9 = D10 = B340A-13-F` (`40 V 3 A` SMA Schottky). Switching frequency is `~433 kHz` (Ch1 UV, `t_ON = 1.70 µs`) and `~540 kHz` (Ch2 Vis, `t_ON = 1.10 µs`), well inside `t_ON >= 500 ns` and `f_SW <= 1.0 MHz`.
- **Staggered Soft-Start & Quiet LED Harness:** `C6 = 1.0 nF` (`1.5 ms`) on `U1.CTRL` and `C7 = 4.7 nF` (`7.0 ms`) on `U2.CTRL` stagger turn-on; `C4 = C5 = 1.0 µF 50 V X7R` directly across `J2`/`J3` attenuate off-board LED ripple to `5.35%` pp (`±2.7%`, UV) and `7.31%` pp (`±3.7%`, Vis).
- **Inherent Fault Protection:** Verified in `ngspice` — open-LED halts `SW` at `V_SW <= 20.62 V` (`<< 42 V` abs max) with `I_UV = 0 mA`; shorted-LED regulates inductor current at `338.4 mA` (`419 mA` peak) with zero thermal runaway.

---

## 3. Verification Summary (`circuit_design/sim/outputs/sim_summary.json`)
- **6/6 `ngspice` Nominal & Fault Benches:** **PASS** (`16/16` assertions passing).
- **Datasheet Corner Sweep (`18.5–24.0 V`, `-10..+55 °C`, all tolerances):** **`2565 / 2565 PASS`** (`P_PCB_max = 0.819 W`, `I_in_max = 0.578 A`, `T_jmax = 71.9 °C`).
- **Full-Parameter Monte Carlo (`N = 2000`):** **`2000 / 2000 (100.0%) PASS`** (`I_UV = 329.9 ± 4.5 mA`, `P_PCB = 0.520 W` mean / `0.574 W` max, `V_UVLO ∈ [17.015, 17.470] V`).
