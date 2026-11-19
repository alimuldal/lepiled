# LepiLED DIY Maxi Switch — Verified Datasheet Summary (Rev 4.0 / Option 2)

All electrical, thermal, and mechanical parameters below are extracted directly from the manufacturer PDFs archived in `datasheets/` and mirrored in machine-readable form in `datasheets/datasheets_summary.json`.

## 1. Power Input & USB-C PD 3.1 Negotiation (`20 V / 1.0 A`)

| Part / MPN | Manufacturer | Package | Key Datasheet Specifications | Local PDF |
|---|---|---|---|---|
| **`AP33771CFBZ-13-FA02`** (`U3`) | Diodes Inc. | W-DFN3030-14 (Type A1, `0.40 mm` pitch) | USB-C PD 3.1 EPR/SPR sink controller; `V_CC` `3.3–31 V` (`34 V` abs max); `V_VOUT`/`V_ISENP` `31 V` abs max; `R_VSEL = 39.0 kΩ 1%` -> `20 V` (Table 2); `R_ISEL = 82.0 kΩ 1%` -> `1.0 A` / `1.1 A` OCP; `R_SENSE = 5 mΩ`; `R_OUT = 200 Ω` discharge limit; `I_VCC = 3.3 mA` typ (`6 mA` max); `R_θJA = 50.04 °C/W`. | `datasheets/AP33771C.pdf` |
| **`DMN3404L-7`** (`Q1A`, `Q1B`) | Diodes Inc. | SOT-23-3 (`1=G, 2=S, 3=D`) | `30 V` logic-level N-MOSFET; `V_GSS = ±20 V`; `V_GS(th) = 1.0–2.0 V`; `R_DS(on) <= 82 mΩ @ V_GS = 3.0 V` (`95 mΩ @ 85 °C`), `<= 42 mΩ @ 4.5 V`; `I_D = 4.8 A`. Back-to-back common-source blocks reverse current from `TP1` to `J1`. | `datasheets/DMN3404L.pdf` |
| **`USB4085-GF-A`** (`J1`) | GCT | 16-pin TH/SMT hybrid USB-C | `5.0 A` VBUS, `6.25 A` GND, `48 V` max, `20,000` cycles, `0.35 mm` signal drill, `7.26 mm` Row-B-to-front-mouth datum. | `datasheets/usb4085.pdf` |
| **`MF-MSMF150/24X`** (`F1`, `F2`) | Bourns | 1812 SMD | `24 V` max, `20 A` interrupt, `I_hold = 1.50 A @ 23 °C`, `1.13 A @ 50 °C`, `1.00 A @ 60 °C`, `I_trip = 3.0 A`, `R_1max = 120 mΩ`. | `datasheets/MF-MSMF.pdf` |
| **`SMBJ22CA-E3/52`** (`D11`) | Vishay | DO-214AA (SMB), Bidirectional | `V_RWM = 22.0 V`, `V_BR = 24.4–26.9 V @ 1 mA`, `V_C = 35.5 V @ 16.9 A`, `600 W` peak pulse, `I_D <= 1 µA`. | `datasheets/smbj.pdf` |

## 2. Constant-Current Buck LED Drivers (`333 mA` Nominal per String)

| Part / MPN | Manufacturer | Package | Key Datasheet Specifications | Local PDF |
|---|---|---|---|---|
| **`AL8860WT-7`** (`U1`, `U2`) | Diodes Inc. | TSOT25 (`0.95 mm` pitch, no EPAD) | `4.5–40 V` (`42 V` abs max) hysteretic buck LED driver; `1.0 A` max (TSOT25); `V_SENSE = 100 mV ±4%` (`96–104 mV`), `±20%` hysteresis; `R_SW = 0.20 Ω` typ (`0.30 Ω` app nom); `V_EN(OFF) = 0.20 V`, `V_EN(ON) = 0.25 V`; `t_SS = 1.5 ms/nF`; `t_ON_rec >= 500 ns`, `f_SW <= 1.0 MHz`; inherent open-LED and short-LED protection; `R_θJA = 147 °C/W`, `T_Jmax = 150 °C`. | `datasheets/AL8860.pdf` |
| **`SRN6045-680M`** (`L1`, `L2`) | Bourns | `6.0×6.0×4.5 mm` SMD | `68 µH ±20%` (`54.4–81.6 µH`), `I_sat = 1.00 A` (`2.27×` margin vs `0.44 A` peak), `I_rms = 0.90 A`, `DCR_max = 0.351 Ω` (`0.29 Ω` typ), recommended pads `2.00 × 6.00 mm` at `±2.15 mm`. | `datasheets/srn6045.pdf` |
| **`B340A-13-F`** (`D9`, `D10`, `D13`) | Diodes Inc. | SMA (DO-214AC) | `40 V`, `3.0 A` avg, `100 A` surge, `V_F ≈ 0.34–0.38 V` at `0.33–1.0 A` (`0.50 V` max @ `3 A`), `T_Jmax = 125 °C`, `R_θJA = 50 °C/W`. Reused for Ch1/Ch2 freewheeling + Aux DC blocking. | `datasheets/ds13005.pdf` |
| **`CRL1206-FW-R300ELF`** (`R3`, `R4`) | Bourns | 1206 SMD | `0.30 Ω ±1%`, `0.50 W @ 70 °C`, `±200 ppm/°C`. Sets `I_LED = 0.100 / 0.30 = 333.3 mA` (`P = 33 mW`). | `datasheets/CRL.pdf` |

## 3. Hardware `17.25 V` UVLO & Ground-Referenced Maxi-Switch

| Part / MPN | Manufacturer | Package | Key Datasheet Specifications | Local PDF |
|---|---|---|---|---|
| **`LM393BIDR`** (`U4`) | Texas Instruments | SOIC-8 | Dual open-collector comparator; `V_CC = 2–36 V` (`38 V` abs max); `V_IO <= 4 mV`; `I_Q = 0.6 mA` typ (`1.7 mA` max); `V_OL < 20 mV @ 100 µA << 200 mV` `AL8860` disable threshold. | `datasheets/LM393B.pdf` |
| **`LM4040BIM3-2.5/NOPB`** (`U5`) | Texas Instruments | SOT-23-3 (DBZ) | `2.500 V ±0.2%` (`±0.5%` over temp) micropower shunt reference; `I_RMIN = 45 µA` typ (`65 µA` max), `I_RMAX = 15 mA`. Biased via `R14 = 10 kΩ` (`250 µA @ 5 V`, `1.75 mA @ 20 V`). | `datasheets/LM4040.pdf` |
| **`BSS138`** (`Q2`, `Q3`) | onsemi | SOT-23-3 (`1=G, 2=S, 3=D`) | `50 V` N-MOSFET; `V_GS(th) = 0.8–1.5 V` (`-2 mV/°C`); `R_DS(on) <= 6.0 Ω @ 4.5 V`. | `datasheets/BSS138.pdf` |
| **`BAT54-7-F`** (`D12`) | Diodes Inc. | SOT-23-3 (`1=A, 2=NC, 3=K`) | `30 V`, `200 mA` Schottky; `V_F <= 240 mV @ 0.1 mA` (`> 500 mV` margin below `BSS138` `V_GS(th)_min`). | `datasheets/BAT54.pdf` |
| **`BZT52C5V1-7-F`** (`D14`) | Diodes Inc. | SOD-123 | `5.1 V` Zener (`4.8–5.4 V`), `500 mW`, clamps `V_SW_BIAS` for `Q2`/`Q3` gates. | `datasheets/BZT52C.pdf` |

## 4. Off-Board LEDs (Stocked UK Distributor Bins) & Interconnects

| Part / MPN | Manufacturer | Key Datasheet Specifications | Local PDF |
|---|---|---|---|
| **`SST-10-UV-A130-G365-00`** (`D1..D4`) | Luminus | 365–375 nm UV-A; `V_F = 3.60 V` typ (`2.7–3.9 V`) @ `350 mA`; `I_Fmax = 1.0 A`; `T_Jmax = 100 °C`; `R_θJs = 1.4 °C/W`; `WPE ≈ 48%`. | `datasheets/Luminus_SST-10-UV_Datasheet.pdf` |
| **`XPEBRY-L1-0000-00R02`** (`D5`, `D6`) | Cree LED | Royal Blue 450–460 nm (Bin 37, `625 mW` min @ `350 mA`); `V_F = 2.93 V` typ (`2.6–3.4 V`); `R_θJs = 5.7 °C/W`; `V_Rmax = 1.0 V`. | `datasheets/XLamp-XPE2.pdf` |
| **`XPEBGR-L1-0000-00F01`** (`D7`) | Cree LED | Green 520–535 nm (Bin R3, `122 lm` min @ `350 mA`); `V_F = 2.70 V` typ (`2.5–3.25 V`, legacy `3.6 V`); `R_θJs = 9.0 °C/W`; `V_Rmax = 1.0 V`. | `datasheets/XLamp-XPE2.pdf` |
| **`XPEBWT-L1-0000-00F51`** (`D8`) | Cree LED | Cool White 6200 K (Bin R3, `122 lm` min @ `85 °C`); `V_F = 2.93 V` @ `25 °C`; `R_θJs = 5.8 °C/W`; `V_Rmax = 1.0 V`. | `datasheets/XLamp-XPE2.pdf` |
| **`B2B-XH-A` / `B3B-XH-A`** (`J2..J4`) | JST | `2.50 mm` pitch, `3 A`, `250 V`, `1.00 mm` PCB drill for all 2-pin and 3-pin headers. | `datasheets/jst_xh.pdf` |
