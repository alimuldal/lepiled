# LepiLED DIY Maxi Switch — Verified Datasheet Summary (Rev 4.8)

All electrical, thermal, and mechanical parameters below are verified against manufacturer datasheets and mirrored in machine-readable form in [datasheets_summary.json](datasheets_summary.json). Every `Datasheet_Ref` in `circuit_design/COMPONENT_IDS.csv` resolves to an archived PDF or this verified summary JSON.

## 1. Power Input, USB-C PD 3.2 (`20 V`) & Input Protection

| Part / MPN | Manufacturer | Package | Key Datasheet Specifications | Reference |
|---|---|---|---|---|
| **`CH224A`** (`U3`, LCSC `C42459160`) | WCH | ESSOP-10 (`1.0 mm` leaded pitch, `2.10 × 3.30 mm` EPAD) | Standalone `20 V` USB-C PD3.2 sink; `VHV`/`VBUS`/`PG <= 32 V`; internal `5.1 kΩ` dead-battery `CC` `Rd`; `VBUS` Pin 8 shorted to `VHV`/`VIN_20V`; `CFG1 = R9 = 120 kΩ` single-resistor `20 V` strap (disables `28 V` EPR). | [datasheets_summary.json](datasheets_summary.json) |
| **`USB4085-GF-A`** (`J1`) | GCT | 16-pin TH USB-C | `5.0 A` VBUS, `6.25 A` GND, `48 V` max, `20,000` cycles, `0.40 mm` PCB signal drills (`0.65 × 0.90 mm` oval pads; **ENIG** board finish avoids HASL hole plugging), `7.26 mm` Row-B-to-front-mouth datum. | [usb4085.pdf](usb4085.pdf) |
| **`046801.5NRHF`** (`F1`, LCSC `C151143`) | Littelfuse | 1206 SMD (Slo-Blo thin-film) | `1.5 A` rated, `63 V DC`, **`50 A` DC interrupting rating**, `I²t = 0.288 A²s` (`144×` margin over hot-plug transient `~0.002 A²s`), `R_cold = 0.044 Ω` typ (`15 mW` @ `0.58 A`), zero PTC thermal hold-current collapse. | [datasheets_summary.json](datasheets_summary.json) |
| **`SMBJ22A`** (`D11`, LCSC `C10214`) | RUILON (SMBJ series) | DO-214AA (SMB), Unidirectional | `V_RWM = 22.0 V`, `V_BR = 24.4–26.9 V @ 1 mA` (`TC ≈ +0.096 %/°C`), `V_C = 35.5 V @ 16.9 A`, `600 W` peak pulse, forward diode clamps negative inductive surges. | [smbj.pdf](smbj.pdf) |
| **`25121WF100KT4E`** (`R7`, LCSC `C11254`) | UNI-ROYAL | 2512 SMD (`1.0 W`) | `1.0 Ω ±1%`, `1.0 W` steady-state (`8×` resistive film area vs `0805`; safely survives `206–362 W` `3–5 µs` USB-C hot-plug RC damper pulse with `C10 = 4.7 µF`). | [datasheets_summary.json](datasheets_summary.json) |
| **`ESD24V32D-C`** (`D13`, `D14`, DNP, `C5224353`) | Leiditech | SOD-323, Bidirectional | `24 V` `V_RWM`, `25 pF`, `320 W`. Marked **DNP** (excluded from paste & PCBA; USB-C plug is sealed inside housing and `CH224A` has internal ESD). | [datasheets_summary.json](datasheets_summary.json) |
| **`BAV99`** (`D15`, `D16`, LCSC `C2500`) | Nexperia | SOT-23-3 | Dual series switching/ESD clamp (`70 V`, `200 mA`, `< 1.5 pF`) clamping `J4` switch lines to `GND` and `/V_REF` (backed by damped `R24 = 10 Ω` + `C16 = 100 nF`). | [datasheets_summary.json](datasheets_summary.json) |

## 2. Constant-Current Buck LED Drivers (`333 mA` Nominal per String)

| Part / MPN | Manufacturer | Package | Key Datasheet Specifications | Reference |
|---|---|---|---|---|
| **`AL8860WT-7`** (`U1`, `U2`, LCSC `C125330`) | Diodes Inc. | TSOT25 (`0.95 mm` pitch, `0.68 mm` pads) | `4.5–40 V` (`42 V` abs max) hysteretic buck LED driver; `1.0 A` max (TSOT25); `V_SENSE = 100 mV ±4%` (`±20%` hyst); `V_EN(OFF) = 0.20 V`, `V_EN(ON) = 0.25 V`; `t_SS = 1.5 ms/nF`; `t_ON >= 500 ns`, `f_SW <= 1.0 MHz`; inherent open/short-LED protection; `R_θJA = 147 °C/W`, `T_Jmax = 150 °C`. | [AL8860.pdf](AL8860.pdf) |
| **`SWPA6045S680MT`** (`L1`, `L2`, LCSC `C53663`) | Sunlord | `6.0×6.0×4.5 mm` SMD | `68 µH ±20%`, `I_sat = 1.10 A` (`2.7×` margin vs `0.407 A` peak), `I_rms = 0.95 A`, `DCR_max = 0.376 Ω` (`0.29 Ω` typ), shielded ferrite drum, machine-reflowed by JLCPCB. | [datasheets_summary.json](datasheets_summary.json) |
| **`SS34`** (`D9`, `D10`, LCSC `C8678`) | MDD | SMA (DO-214AC) | `40 V`, `3.0 A` avg, `80 A` surge, `V_F ≈ 0.35 V` at `0.33 A`, `T_Jmax = 125 °C`. | [datasheets_summary.json](datasheets_summary.json) |
| **`1206W4F300LT5E`** (`R3`, `R4`, LCSC `C59882`) | UNI-ROYAL | 1206 SMD | `0.30 Ω ±1%`, `0.25 W @ 70 °C` (`7.5×` margin over `33 mW`). Sets `I_LED = 0.100 / 0.30 = 333.3 mA`. | [datasheets_summary.json](datasheets_summary.json) |

## 3. Hysteretic Hardware UVLO & Direct Gold Dry-Circuit Switch

| Part / MPN | Manufacturer | Package | Key Datasheet Specifications | Reference |
|---|---|---|---|---|
| **`LM393DR2G`** (`U4`, LCSC `C7955`) | onsemi | SOIC-8 | Dual open-collector comparator; `V_CC = 2–36 V`; **`0..+70 °C`** commercial grade (adequate for UK open-air nocturnal use; drop-in `-40..+125 °C` alt `LM2903DR2G C57474`); `I_CC = 1.0 mA` typ / `2.5 mA` max. Configured with `R15–R21` for `0.83 V` hysteresis (`V_ON = 17.48 V`, `V_OFF = 16.66 V`). | [datasheets_summary.json](datasheets_summary.json) |
| **`TL431`** (`U5`, LCSC `C181103`) | Hottech | SOT-23-3 (`1=REF, 2=K, 3=A`) | `2.500 V ±1%` shunt reference; **`0..+70 °C`** commercial grade; `I_KA = 1–100 mA` (`1.41 mA @ 16.6 V`, `1.75 mA @ 20 V` via `R14 = 10 kΩ`). Damped ESD bypass `R24 = 10 Ω` + `C16 = 100 nF` keeps loop unconditionally stable (`Q <= 1`). | [datasheets_summary.json](datasheets_summary.json) |
| **`2N7002`** (`Q2`, `Q3`, LCSC `C8545`) | Changjing | SOT-23-3 (`1=G, 2=S, 3=D`) | `60 V` N-MOSFET; `V_GS(th) = 1.0–2.5 V`; `R_DS(on) <= 7.5 Ω`. Clamps `U1_CTRL`/`U2_CTRL` LOW via `R20 = 56 kΩ / R21 = 100 kΩ` divider (`V_GS = 3.21–11.54 V`). | [datasheets_summary.json](datasheets_summary.json) |
| **`7211SYZBE` + `759D02000`** (`SW1`, `SW1_BOOT`) | C&K | Panel `1/4-40` bushing (`12.70×11.43×10.67 mm`) | Gold-plated dry-circuit `DPDT On-On-On` toggle (`0.4 VA max @ 20 V AC/DC`, `8.89 mm` `Y` bushing + `10.67 mm` `S` bat → `18.6 mm` total booted protrusion below `2.5–3.0 mm` lid floor). | [datasheets_summary.json](datasheets_summary.json) |

## 4. Off-Board LEDs (`20 mm` Stars) & Interconnects

| Part / MPN | Manufacturer | Key Datasheet Specifications (Electrically Neutral Thermal Pads) | Reference |
|---|---|---|---|
| **`SST-10-UV-A130` 365 nm** (`D1..D4`, Faces 1–4) | Luminus (20 mm Cu DTP star) | 365–375 nm UV-A; `V_F = 3.60 V` typ (`2.7–3.9 V`) @ `350 mA`; `I_Fmax = 1.0 A`; `T_Jmax = 100 °C`; `R_θJs = 1.4 °C/W`; `WPE ≈ 48%`. | [Luminus_SST-10-UV_Datasheet.pdf](Luminus_SST-10-UV_Datasheet.pdf) |
| **`XP-E2` Royal Blue 455 nm** (`D5` Face 1, `D6` Face 3 — **opposite faces**) | Cree LED (20 mm star) | Royal Blue 450–460 nm; `V_F = 2.93 V` typ (`2.6–3.4 V`) @ `350 mA`; `I_Fmax = 1.2 A`; `R_θJs = 5.7 °C/W`. | [XLamp-XPE2.pdf](XLamp-XPE2.pdf) |
| **`XP-E2` Green 528 nm** (`D7` Face 2) | Cree LED (20 mm star) | Green 520–535 nm; `V_F = 2.70 V` typ (`2.5–3.25 V`) @ `350 mA`; `I_Fmax = 1.5 A`; `R_θJs = 9.0 °C/W`. | [XLamp-XPE2.pdf](XLamp-XPE2.pdf) |
| **`XP-E2` Cool White 6200–6500 K** (`D8` Face 4) | Cree LED (20 mm Cu DTP star) | Cool White 6200–6500 K; `V_F = 2.93 V` @ `25 °C`; `I_Fmax = 1.5 A`; `R_θJs = 5.8 °C/W`. | [XLamp-XPE2.pdf](XLamp-XPE2.pdf) |
| **`B2B-XH-A` / `B3B-XH-A`** (`J2..J4`) | JST | `2.50 mm` pitch, `3 A`, `250 V`, `1.00 mm` PCB drill (THT hand-soldered). | [jst_xh.pdf](jst_xh.pdf) |
| **`UNI-ROYAL 0603WAF` / `0805W8F`** (`R5..R24`) | UNI-ROYAL | Thick-film chip resistors (`±1%`, `0.1 W` 0603 / `0.125 W` 0805; JLCPCB Basic). | [dcrcwe3.pdf](dcrcwe3.pdf) |
