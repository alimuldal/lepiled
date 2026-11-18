# Extracted Datasheet Specifications Summary

All electrical, thermal, and mechanical parameters below are extracted directly from the verified vendor PDF datasheets archived in `datasheets/` (single source of truth paired with `datasheets/datasheets_summary.json`).

---

## 1. Archived Vendor Datasheets (`datasheets/*.pdf`)

| Filename | Component / Series | Revision | Pages | Size |
|---|---|---|---|---|
| `Luminus_SST-10-UV_Datasheet.pdf` | Luminus `SST-10-UV` (365 nm UV-A) | PDS-002674 Rev 05 (2023-03-21) | 15 | 1.5 MB |
| `CUN66A1B_200324_R14.0.pdf` | Seoul Viosys `CUN66A1B` (Brehm 2017 baseline) | Rev 14.0 (2020-03-24) | 21 | 865 KB |
| `XLamp-XPE2.pdf` | Cree LED `XLamp XP-E2` (Royal Blue, Green, Cool White) | CLD-DS56 Rev 25B (2026) | 49 | 3.0 MB |
| `lm3410.pdf` | TI `LM3410 / LM3410-Q1` Boost CC Driver | SNVS541H (Aug 2016) | 57 | 1.4 MB |
| `ds13005.pdf` | Diodes Inc `B340A-13-F` 40 V 3 A Schottky | DS13005 Rev. 9-2 | 3 | 124 KB |
| `srn6045.pdf` | Bourns `SRN6045` Semi-Shielded Power Inductors | Rev. 01/20 | 3 | 455 KB |
| `CRL.pdf` | Bourns `CRL1206` Low-Value Sense Resistors | Rev. 03/05/25 | 4 | 533 KB |
| `dcrcwe3.pdf` | Vishay `D/CRCW e3` Thick-Film Chip Resistors | Doc 20035 (2026-04-14) | 13 | 147 KB |
| `smbj.pdf` | Vishay `SMBJ5.0A` 600 W TVS Diode | Doc 88392 (2024-01-09) | 6 | 127 KB |
| `usb4085.pdf` | GCT `USB4085-GF-A` USB-C Receptacle | Rev B PCN (2023-02-28) | 3 | 197 KB |
| `DMG2305UX.pdf` | Diodes Inc `DMG2305UX-7` P-MOSFET | DS36196 Rev. 8-2 (Jul 2021) | 6 | 411 KB |
| `mmbt3904lt1-d.pdf` | onsemi `MMBT3904LT1G` NPN General-Purpose Transistor | Rev. 15 (Sept 2026) | 11 | 310 KB |
| `mmbt3906lt1-d.pdf` | onsemi `MMBT3906LT1G` PNP General-Purpose Transistor | Rev. 15 (Sept 2026) | 11 | 319 KB |
| `tl431.pdf` | TI `TL431AIDBZR` Precision Programmable Shunt Reference | SLVS543S (May 2024) | 85 | 2.9 MB |
| `BZT52C.pdf` | Diodes Inc `BZT52C5V6` / `BZT52C18` Zener Diodes | DS18004 Rev. 38-2 (Oct 2017) | 5 | 386 KB |
| `BAV70_onsemi.pdf` | onsemi `BAV70LT1G` Common-Cathode Dual Diode (`D12`) | Rev. BAV70LT1/D | 7 | 239 KB |
| `BAW56_onsemi.pdf` | onsemi `BAW56LT1G` Common-Anode Dual Diode (`D16`) | Rev. BAW56LT1/D | 8 | 239 KB |
| `MF-LSMF.pdf` | Bourns `MF-LSMF500/16X` 2920 16 V 5.0 A PTC Fuse | Current Rev. | 11 | 1.4 MB |
| `MF-MSMF.pdf` | Bourns `MF-MSMF` 1812 PTC Series (reference check) | Current Rev. | 16 | 1.3 MB |
| `jst_xh.pdf` | JST `XH` Series Headers (`B2B-XH-A`, `B3B-XH-A`) | Current Rev. | 9 | 172 KB |

> **Notes on Verified Datasheet Corrections:**
> 1. **`F1` PTC Fuse (`MF-LSMF500/16X`):** Upgraded to **`MF-LSMF500/16X`** (`MF-LSMF.pdf` pp. 2–3: `16 V`, `5.0 A` hold @ `23 °C`, `3.75 A @ 50 °C`, `3.525 A @ 55 °C`, `3.30 A @ 60 °C`, `10.0 A` trip, `R_1max = 25 mΩ`) so `I_in` maintains positive `60 °C` hold margin even under full stacked `datasheet_spec` USB droop (`3.11–3.24 A < 3.30 A`) while covering `±16 V` fault inputs.
> 2. **Active Cree `XP-E2` Order Codes (`XLamp-XPE2.pdf` Rev 25B):** `XPEBRY-L1-0000-00S02` (Royal Blue, p. 10), `XPEBGR-L1-0000-00K01` (Green, p. 11), and `XPEBWT-L1-0000-00H51` (Cool White, p. 5) are all verified active "Order Codes Suggested for New Designs".
> 3. **`D12` Diode-OR (`BAV70LT1G` vs `BAW56`):** `BAV70_onsemi.pdf` p. 1 confirms **`BAV70LT1G`** is **Common Cathode** (`BAW56` is Common Anode).

---

## 2. LED Emitters (`D1..D8`)

| Parameter | `SST-10-UV-A130-G365-00` (4× UV) | `CUN66A1B` (Baseline Ref.) | `XPEBRY-L1-0000-00S02` (2× Blue) | `XPEBGR-L1-0000-00K01` (1× Green) | `XPEBWT-L1-0000-00H51` (1× CW) |
|---|---|---|---|---|---|
| **PDF Citation** | `Luminus_SST-10-UV_Datasheet.pdf` pp. 1–6, 10 | `CUN66A1B_200324_R14.0.pdf` pp. 3–9 | `XLamp-XPE2.pdf` pp. 3–4, 10 | `XLamp-XPE2.pdf` pp. 3–4, 11 | `XLamp-XPE2.pdf` pp. 3–4, 5 |
| **Wavelength / CCT** | `365–375 nm` (`370 nm` typ) | `360–370 nm` (`367 nm` typ) | `450–460 nm` (`D3–D4`, `455 nm` typ) | `520–535 nm` (`G2–G4`, `528 nm` typ) | `6200 K` typ (`Kit 51`) |
| **$V_f$ @ 350 mA, 25 °C** | `~3.60 V` typ (`2.7–3.9 V`, *p. 6*) | `~3.50 V` typ (*p. 4*) | `2.93 V` typ / `3.40 V` max (*p. 4*) | `2.70 V` typ / `3.25 V` max (*p. 4*) | `~2.93 V` typ / `3.19 V` max (`2.84/3.10 V` @ 85 °C, *p. 4*) |
| **$V_f$ @ 500 mA, 25 °C** | `2.8` min / `3.7` typ / `4.0` max (*p. 5*) | `3.4 / 3.6 / 3.8 V` (*p. 3, 9*) | — | — | — |
| **$V_f$ Tempco** | `-2.67 mV/°C` (*p. 6*) | `-2.67 mV/°C` (*p. 7*) | `-1.5 mV/°C` (*p. 3*) | `-1.2 mV/°C` (*p. 3*) | `-1.5 mV/°C` (*p. 3*) |
| **$I_{f,\max}$ (CW)** | `1.0 A` (`365 nm`, *p. 4*) | `0.7 A` (*p. 3*) | `1.2 A` (*p. 3*) | `1.5 A` (*p. 3*) | `1.5 A` (*p. 3*) |
| **$T_{j,\max}$** | **`100 °C`** (*p. 4*) | `90 °C` (*p. 3*) | **`150 °C`** (*p. 4*) | **`150 °C`** (*p. 4*) | **`150 °C`** (*p. 4*) |
| **$R_{\theta J-s}$** | **`1.4 °C/W`** (*p. 1*) | `3.8 °C/W` (*p. 3*) | `5.7 °C/W` (*p. 3*) | `9.0 °C/W` (*p. 3*) | `5.8 °C/W` (*p. 3*) |
| **Pad Compatibility** | `A130`: `3.25×3.25 mm` (XP-compatible, *p. 10*) | Z5 `3535` | `3.30×3.30 mm` XP (*pp. 38–39*) | `3.30×3.30 mm` XP (*pp. 38–39*) | `3.30×3.30 mm` XP (*pp. 38–39*) |

---

## 3. Boost Constant-Current Driver (`U1`, `U2` = `TI LM3410XMY/NOPB`)

Extracted from `datasheets/lm3410.pdf` (`SNVS541H`, Sec. 5 p. 3, Sec. 6.1–6.5 pp. 4–5, Fig. 6 p. 6, Table 25 p. 37, Sec. 10.3.5 p. 40):
- **Package & DGN Pinout (Sec. 5 p. 3):** `8-HVSSOP / MSOP-PowerPAD` (`DGN`): `1=NC`, `2=PGND`, `3=VIN`, `4=DIM`, `5=FB`, `6=AGND`, `7=SW`, `8=NC`, `DAP=GND` (connect `DAP` to `PGND` + `AGND` on top layer with 4–6 thermal vias to bottom `GND`).
- **Thermal:** **$R_{\theta JA} = 53.7\text{ °C/W}$**, $R_{\theta JC(\text{bot})} = 6.8\text{ °C/W}$ (mandatory over `SOT-23-5 DBV` `164.2 °C/W` / `400 mW` limit).
- **Recommended Operating Ratings:** $V_{\text{in}} \in [2.7, 5.5]\text{ V}$ (`7.0 V` abs max); $V_{\text{SW}} \in [3.0, 24.0]\text{ V}$ (`26.5 V` abs max); $T_J \in [-40, +125]\text{ °C}$ (`150 °C` abs max, `165 °C` thermal shutdown).
- **Feedback Reference $V_{FB}$:** **`178 mV` min / `190 mV` typ / `202 mV` max** ($\pm 6.3\%$), $I_{FB} = 0.1\,\mu\text{A}$ typ (`1 µA` max).
- **Switching Frequency $f_{SW}$ (`LM3410X`):** **`1200 kHz` min / `1600 kHz` typ / `2000 kHz` max**.
- **Switch Current Limit $I_{CL}$:** **`2.1 A` min / `2.8 A` typ**; Duty Limits: $D_{\max} = 88\%$ min / `92%` typ, $D_{\min} = 5\%$ typ.
- **Switch $R_{DS(\text{on})}$:** `170 mΩ` typ ($25^\circ\text{C}$) / `250 mΩ` typ ($125^\circ\text{C}$, Fig. 6) / **`330 mΩ` max**.
- **Switching Times (Table 25 p. 37):** $t_r \approx 6\text{–}10\text{ ns}$ (`8 ns` nom), $t_f \approx 5\text{–}8\text{ ns}$ (`6.5 ns` nom).
- **DIM Control:** $V_{\text{DIM\_L}} \le 0.4\text{ V}$ (shutdown, $I_Q = 80\text{ nA}$ typ), $V_{\text{DIM\_H}} \ge 1.8\text{ V}$ (enable, max $V_{\text{in}} + 0.3\text{ V}$, **do not float**); $I_{\text{DIM}} = 100\text{ nA}$; $I_Q$ switching `7 mA` typ / `11 mA` max.

---

## 4. Power Magnetics, Diodes, Passives & Protection

| RefDes | MPN | Key Datasheet Specs & Citations |
|---|---|---|
| `D9`, `D10` | `Diodes Inc B340A-13-F` | `ds13005.pdf` pp. 1–2: `SMA`, $V_{RRM}=40\text{ V}$, $I_{F(AV)}=3.0\text{ A}$, $I_{FSM}=100\text{ A}$, $V_F = 0.38\text{ V}$ @ 1 A / `0.43 V` @ 2 A / `0.46 V` typ (`0.50 V` max) @ 3 A ($25^\circ\text{C}$), $I_R \le 0.5\text{ mA}$ @ 40 V ($25^\circ\text{C}$), $T_{j,\max}=125^\circ\text{C}$, $R_{\theta JA}=50^\circ\text{C/W}$, $R_{\theta JT}=10^\circ\text{C/W}$. |
| `L1`, `L2` | `Bourns SRN6045-100M` | `srn6045.pdf` p. 1: $10\text{ }\mu\text{H} \pm 20\%$ (`8.0 µH` min), $I_{\text{rms}} = 2.5\text{ A}$, $I_{\text{sat}} = 3.0\text{ A}$, $DCR_{\max} = 58.6\text{ m}\Omega$, SRF `15 MHz` typ, `-40 to +125 °C`. |
| `R3`, `R4` | `Bourns CRL1206-FW-R560ELF` | `CRL.pdf` p. 1: `0.56 Ω ±1%`, `0.50 W @ 70 °C`, `±200 ppm/°C`, `-55 to +155 °C`, `1206` ($I_{\text{LED,typ}} = 339.3\text{ mA}$, $P = 64.5\text{ mW}$). |
| `R1`, `R2` | `Vishay CRCW08055K10FKEA` | `dcrcwe3.pdf` p. 1: `5.1 kΩ ±1%`, `0805`, `0.125 W` Standard ($\le 1\%$ drift) / `0.25 W` Extended ($\le 2\%$ drift) @ `70 °C`, `±100 ppm/K`. |
| `R5..R20` | `Vishay CRCW0603*FKEA` | `dcrcwe3.pdf` p. 1: `0603 ±1%`, `0.10 W` Standard / `0.125 W` Extended @ `70 °C`, `±100 ppm/K`. |
| `J1` | `GCT USB4085-GF-A` | `usb4085.pdf` pp. 1–2: `VBUS (A4/B4/A9/B9) 5.0 A`, `GND (A1/B1/A12/B12/SH) 6.25 A`, `CC1 (A5)`, `CC2 (B5)`, `48 V`, `40 mΩ` init, `20,000` cycles, `-40 to +85 °C`. |
| `J2..J4` | `JST B2B-XH-A` / `B3B-XH-A` | `jst_xh.pdf` pp. 1–2, 5: `2.50 mm` pitch, `3 A AC/DC (AWG #22)`, `250 V`, `-25..+85 °C`, `10 mΩ` init, `7.0 mm` unmated (`9.8 mm` mated) height. |
| `F1` | `Bourns MF-LSMF500/16X` | `MF-LSMF.pdf` pp. 2–3: `2920`, `16 V`, `40 A`, $I_{\text{hold}}=5.0\text{ A}$ @ $23^\circ\text{C}$ (`3.75 A` @ $50^\circ\text{C}$, `3.525 A` @ $55^\circ\text{C}$, `3.30 A` @ $60^\circ\text{C}$), $I_{\text{trip}}=10.0\text{ A}$, $R_{\min}=5\text{ m}\Omega$, $R_{1\max}=25\text{ m}\Omega$. |
| `D11` | `Vishay SMBJ5.0A-E3/5B` | `smbj.pdf` pp. 1–2: `SMB`, $V_{RWM}=5.0\text{ V}$, $V_{BR}=6.40\text{–}7.07\text{ V}$ @ 10 mA, $V_C = 9.2\text{ V}$ @ `65.2 A`, `600 W`, $I_D \le 800\text{ }\mu\text{A}$ @ 5.0 V (downstream on `VIN_PROT`). |
| `Q1A`, `Q1B` | `Diodes Inc DMG2305UX-7` | `DMG2305UX.pdf` pp. 1–2: `SOT-23-3` (`1=G, 2=S, 3=D`), $BV_{DSS}=-20\text{ V}$, $V_{GSS}=\pm 8\text{ V}$, $I_D = -4.2\text{ A}$ steady @ `25 °C` (`-3.3 A` @ `70 °C`; `-5.0 A` is `t<10 s`), $V_{GS(\text{th})} = -0.5\text{ to }-0.9\text{ V}$, $R_{DS(\text{on})} = 40\text{ m}\Omega$ typ / `52 mΩ` max @ $-4.5\text{ V}$, $R_{\theta JA} = 90^\circ\text{C/W}$. |
| `U3` | `TI TL431AIDBZR` | `tl431.pdf` pp. 4–5, 10: `SOT-23-3 DBZ` (`1=K, 2=REF, 3=A`), $V_{\text{ref}} = 2.495\text{ V} \pm 1\%$ ($2.470\text{–}2.520\text{ V}$ @ `25 °C`, $V_{I(\text{dev})} \le 34\text{ mV}$ over `-40..85 °C`), $I_{\text{ref}} \le 4\text{ }\mu\text{A}$, $I_{\min} \le 0.7\text{ mA}$, $V_{KA} \le 36\text{ V}$, $R_{\theta JA}=206^\circ\text{C/W}$. |
| `Q2` | `onsemi MMBT3906LT1G` | `mmbt3906lt1-d.pdf` pp. 1–2: `SOT-23-3` (`1=B, 2=E, 3=C`), $V_{CEO}=-40\text{ V}$, $I_C=-200\text{ mA}$, $h_{FE}\ge 80$ @ 1 mA (`100–300` @ 10 mA), $V_{CE(\text{sat})}\ge -0.25\text{ V}$ @ 10 mA. |
| `Q3`, `Q4` | `onsemi MMBT3904LT1G` | `mmbt3904lt1-d.pdf` pp. 1–2, 7: `SOT-23-3` (`1=B, 2=E, 3=C`), $V_{CEO}=40\text{ V}$, $V_{CBO}=60\text{ V}$, $V_{EBO}=6.0\text{ V}$, $I_C=200\text{ mA}$, $h_{FE}\ge 70$ @ 1 mA (`100–300` @ 10 mA), $V_{CE(\text{sat})}\le 0.2\text{ V}$ @ 10 mA. |
| `D12` | `onsemi BAV70LT1G` | `BAV70_onsemi.pdf` pp. 1–2: `SOT-23-3` Common Cathode, `100 V`, `200 mA`, $V_F \le 715\text{ mV}$ @ 1 mA, $I_R \le 1\text{ }\mu\text{A}$ @ 100 V ($25^\circ\text{C}$). |
| `D16` | `onsemi BAW56LT1G` | `BAW56_onsemi.pdf` pp. 1–2: `SOT-23-3` Common Anode (`3=A, 1=K1, 2=K2`), `70 V`, `200 mA`, $V_F \le 715\text{ mV}$ @ 1 mA. |
| `D13`, `D14` | `Diodes Inc BZT52C18-7-F` | `BZT52C.pdf` p. 2: `SOD-123`, $V_Z = 16.8\text{–}19.1\text{ V}$ (`18.0 V` nom @ 5 mA), $Z_{ZT}\le 45\text{ }\Omega$, $I_R \le 0.1\text{ }\mu\text{A}$ @ 12.6 V, `500 mW @ 75 °C`. |
| `D15` | `Diodes Inc BZT52C5V6-7-F` | `BZT52C.pdf` p. 2: `SOD-123`, $V_Z = 5.2\text{–}6.0\text{ V}$ (`5.6 V` nom @ 5 mA), $Z_{ZT}\le 40\text{ }\Omega$, `500 mW @ 75 °C` (`Q1A/Q1B` $V_{GS}$ gate-source clamp). |
| `C1..C3` | `Murata GRM31CR71E106KA12L` | `10 µF ±10%, 25 V, X7R, 1206` (`~8.0 µF` effective at 5 V DC bias). |
| `C4..C5` | `Samsung CL32B106KBJNFNE` | `10 µF ±10%, 50 V, X7R, 1210` (`~7.5 µF` effective at 16 V DC bias). |
| `C6..C8, C11..C12` | `Murata GRM188R71E104KA01D` | `100 nF ±10%, 25 V, X7R, 0603` (stagger, `VIN_PROT` bypass, soft-start, `VBUS` ESD bypass). |
| `C9..C10` | `Murata GRM188R71H104KA93D` | `100 nF ±10%, 50 V, X7R, 0603` (`VOUT1`/`VOUT2` HF output bypass). |
| `SW1` | `E-Switch 100SP3T1B1M1QEH` | `SPDT On-Off-On`, `5 A`, `1/4-40` bushing, `Ø 6.35 mm` panel cutout, `10.41 mm` actuator. |
| `SW1_BOOT` | `C&K 759D02000` | Full silicone waterproof toggle boot (`1/4-40` thread, mates to `SW1`). |
