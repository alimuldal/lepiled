# LepiLED DIY Maxi Switch — Verified Datasheet Summary (Rev 4.5)

All electrical, thermal, and mechanical parameters below are extracted from manufacturer datasheets archived in `datasheets/` and mirrored in machine-readable form in [datasheets_summary.json](datasheets_summary.json).

## 1. Power Input, USB-C PD 3.1 (`20 V / 1.0 A`) & Protection

| Part / MPN | Manufacturer | Package | Key Datasheet Specifications | Local PDF |
|---|---|---|---|---|
| **`AP33771CFBZ-13-FA02`** (`U3`) | Diodes Inc. | W-DFN3030-14 (Type A1, `0.40 mm` pitch) | USB-C PD 3.1 sink controller; `V_CC` `3.3–31 V` (`34 V` abs max); `V_VOUT`/`V_ISENP` `31 V` abs max; `R_VSEL = 39.0 kΩ 1%` -> `20 V`; `R_ISEL = 82.0 kΩ 1%` -> `1.0 A` / `1.1 A` OCP; `R_SENSE = 5 mΩ`; `R_OUT = 200 Ω` discharge limit; `LED` pin `4 s` breathing = `VOUT ON`, steady = PDO mismatch; `1.80 × 2.70 mm` EPAD; `R_θJA = 50.04 °C/W`. | [AP33771C.pdf](AP33771C.pdf) |
| **`DMN4035L-7`** (`Q1`) | Diodes Inc. | SOT-23-3 (`1=G, 2=S, 3=D`) | `40 V` N-MOSFET (`2×` rating on `20 V` rail); `V_GSS = ±20 V`; `V_GS(th) = 1.0–2.5 V`; `R_DS(on) <= 52 mΩ @ 4.5 V`, `<= 42 mΩ @ 10 V`; `I_D = 4.6 A`. Single high-side USB-C load switch slew-controlled via `R11 = 6.2 kΩ`, `C13 = 47 nF`, `R21 = 1.0 MΩ` (`0.582 A` peak inrush). | [DMN4035L.pdf](DMN4035L.pdf) |
| **`USB4085-GF-A`** (`J1`) | GCT | 16-pin TH USB-C | `5.0 A` VBUS, `6.25 A` GND, `48 V` max, `20,000` cycles, `0.40 mm` PCB signal drills (`0.65 × 0.90 mm` oval pads), `7.26 mm` Row-B-to-front-mouth datum. | [usb4085.pdf](usb4085.pdf) |
| **`MF-MSMF110/33X`** (`F1`) | Bourns | 1812 SMD (Style-2 land) | `33 V` max (`1.65×` derating on `20 V`), `40 A` interrupt, `I_hold = 1.10 A @ 23 °C` (`0.73 A @ 60 °C`, `1.26×` margin over `0.581 A` WC), `I_trip = 2.2 A`. | [MF-MSMF.pdf](MF-MSMF.pdf) |
| **`SMBJ22A-E3/52`** (`D11`) | Vishay | DO-214AA (SMB), Unidirectional | `V_RWM = 22.0 V`, `V_BR = 24.4–26.9 V @ 1 mA`, `V_C = 35.5 V @ 16.9 A`, `600 W` peak pulse, forward diode clamps negative inductive surges. | [smbj.pdf](smbj.pdf) |
| **`WSL12065L000FEA`** (`R8`) | Vishay Dale | 1206 SMD | `5.0 mΩ ±1%`, `0.50 W`, metal strip shunt for `AP33771C` Kelvin `ISENP`/`VCC` OCP sensing. | [WSL.pdf](WSL.pdf) |
| **`CDSOD323-T24` / `-T05`** (`D13–D16`) | Bourns | SOD-323, Unidirectional | `±15 kV` air / `±8 kV` contact IEC 61000-4-2 ESD clamps (`3 pF` typ): `24 V` `V_RWM` on `CC1`/`CC2` (`D13`/`D14`, `VBUS`-short tolerant); `5.0 V` `V_RWM` on `J4` switch lines (`D15`/`D16`). | [datasheets_summary.json](datasheets_summary.json) |

## 2. Constant-Current Buck LED Drivers (`333 mA` Nominal per String)

| Part / MPN | Manufacturer | Package | Key Datasheet Specifications | Local PDF |
|---|---|---|---|---|
| **`AL8860WT-7`** (`U1`, `U2`) | Diodes Inc. | TSOT25 (`0.95 mm` pitch, `0.68 mm` pads) | `4.5–40 V` (`42 V` abs max) hysteretic buck LED driver; `1.0 A` max (TSOT25); `V_SENSE = 100 mV ±4%` (`±20%` hyst); `V_EN(OFF) = 0.20 V`, `V_EN(ON) = 0.25 V`; `t_SS = 1.5 ms/nF`; `t_ON >= 500 ns`, `f_SW <= 1.0 MHz`; inherent open/short-LED protection; `R_θJA = 147 °C/W`, `T_Jmax = 150 °C`. | [AL8860.pdf](AL8860.pdf) |
| **`SRN6045-680M`** (`L1`, `L2`) | Bourns | `6.0×6.0×4.5 mm` SMD | `68 µH ±20%`, `I_sat = 1.00 A` (`2.46×` margin vs `0.407 A` peak), `I_rms = 0.90 A`, `DCR_max = 0.351 Ω` (`0.29 Ω` typ), recommended pads `2.00 × 6.00 mm` at `±2.15 mm`. | [srn6045.pdf](srn6045.pdf) |
| **`B340A-13-F`** (`D9`, `D10`) | Diodes Inc. | SMA (DO-214AC) | `40 V`, `3.0 A` avg, `100 A` surge, `V_F ≈ 0.34–0.38 V` at `0.33 A`, `T_Jmax = 125 °C`, `R_θJA = 50 °C/W`. | [ds13005.pdf](ds13005.pdf) |
| **`CRL1206-FW-R300ELF`** (`R3`, `R4`) | Bourns | 1206 SMD | `0.30 Ω ±1%`, `0.50 W @ 70 °C`, `±200 ppm/°C`. Sets `I_LED = 0.100 / 0.30 = 333.3 mA` (`33 mW`). | [CRL.pdf](CRL.pdf) |

## 3. Hysteretic Hardware UVLO & Direct Gold Dry-Circuit Switch

| Part / MPN | Manufacturer | Package | Key Datasheet Specifications | Local PDF |
|---|---|---|---|---|
| **`LM393BIDR`** (`U4`) | Texas Instruments | SOIC-8 | Dual open-collector comparator; `V_CC = 2–36 V` (`38 V` abs max); `V_IO <= 4 mV`; `I_Q = 0.6 mA` typ. Configured with `R15–R20` for `0.90 V` hysteresis (`V_ON = 17.54 V`, `V_OFF = 16.64 V`) + `U4B` inverter driving `Q2`/`Q3`. | [LM393B.pdf](LM393B.pdf) |
| **`LM4040BIM3-2.5/NOPB`** (`U5`) | Texas Instruments | SOT-23-3 (DBZ) | `2.500 V ±0.2%` (`±0.85%` over temp) micropower shunt reference; `I_RMIN = 65 µA` max, `I_RMAX = 15 mA`. Biased via `R14 = 10 kΩ` (`250 µA @ 5 V`, `1.75 mA @ 20 V`). | [LM4040.pdf](LM4040.pdf) |
| **`BSS138`** (`Q2`, `Q3`) | onsemi | SOT-23-3 (`1=G, 2=S, 3=D`) | `50 V` N-MOSFET; `V_GS(th) = 0.8–1.5 V`; `R_DS(on) <= 6.0 Ω @ 4.5 V`. Clamps `U1_CTRL`/`U2_CTRL` to `< 0.1 mV` when `UVLO_FAULT` is HIGH (`2.50 V`). | [BSS138.pdf](BSS138.pdf) |
| **`7211SYZBE` + `759D02000`** (`SW1`, `SW1_BOOT`) | C&K | Panel `1/4-40` bushing (`12.7×11.43×10.67 mm`) | Gold-plated dry-circuit `DPDT On-On-On` toggle (`0.4 VA max @ 20 V AC/DC`, solder lugs) + full silicone waterproof boot; wired directly to `J4` without intermediate bias/steering FETs. | [datasheets_summary.json](datasheets_summary.json) |

## 4. Off-Board LEDs (Pre-Mounted `20 mm` Copper DTP Stars) & Interconnects

| Part / MPN | Manufacturer | Key Datasheet Specifications (Electrically Neutral Thermal Pads) | Local PDF |
|---|---|---|---|
| **`SST-10-UV-A130` 365 nm** (`D1..D4`, `20 mm` Cu DTP star) | Luminus | 365–375 nm UV-A; `V_F = 3.60 V` typ (`2.7–3.9 V`) @ `350 mA`; `I_Fmax = 1.0 A`; `T_Jmax = 100 °C`; `R_θJs = 1.4 °C/W`; `WPE ≈ 48%`; electrically neutral thermal pad (`R_sub ≈ 0.5 K/W` on Cu DTP). | [Luminus_SST-10-UV_Datasheet.pdf](Luminus_SST-10-UV_Datasheet.pdf) |
| **`XP-E2` Royal Blue 455 nm** (`D5`, `D6`, `20 mm` Cu DTP star) | Cree LED | Royal Blue 450–460 nm; `V_F = 2.93 V` typ (`2.6–3.4 V`) @ `350 mA`; `I_Fmax = 1.2 A`; `R_θJs = 5.7 °C/W`; electrically neutral thermal pad. | [XLamp-XPE2.pdf](XLamp-XPE2.pdf) |
| **`XP-E2` Green 528 nm** (`D7`, `20 mm` Cu DTP star) | Cree LED | Green 520–535 nm; `V_F = 2.70 V` typ (`2.5–3.25 V`) @ `350 mA`; `I_Fmax = 1.5 A`; `R_θJs = 9.0 °C/W`; electrically neutral thermal pad. | [XLamp-XPE2.pdf](XLamp-XPE2.pdf) |
| **`XP-E2` Cool White 6200–6500 K** (`D8`, `20 mm` Cu DTP star) | Cree LED | Cool White 6200–6500 K; `V_F = 2.93 V` @ `25 °C`; `I_Fmax = 1.5 A`; `R_θJs = 5.8 °C/W`; electrically neutral thermal pad. | [XLamp-XPE2.pdf](XLamp-XPE2.pdf) |
| **`B2B-XH-A` / `B3B-XH-A`** (`J2..J4`) | JST | `2.50 mm` pitch, `3 A`, `250 V`, `1.00 mm` PCB drill for all 2-pin and 3-pin headers. | [jst_xh.pdf](jst_xh.pdf) |
| **`CRCW0603` / `0805`** (`R1–R23` std) | Vishay | Thick-film chip resistors (`±1%`, `0.1 W` 0603 / `0.125 W` 0805). | [dcrcwe3.pdf](dcrcwe3.pdf) |
