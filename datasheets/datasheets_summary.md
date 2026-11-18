# Extracted Datasheet Specifications Summary

All electrical, thermal, and mechanical parameters below are extracted directly from the verified vendor PDF datasheets archived in `datasheets/` (single source of truth paired with `datasheets/datasheets_summary.json`).

---

## 1. Archived Vendor Datasheets (`datasheets/*.pdf`)

| Filename | Component / Series | Revision | Pages | Size |
|---|---|---|---|---|
| `Luminus_SST-10-UV_Datasheet.pdf` | Luminus `SST-10-UV` (365 nm UV-A) | PDS-002674 Rev 05 (2023-03-21) | 15 | 1.5 MB |
| `CUN66A1B_200324_R14.0.pdf` | Seoul Viosys `CUN66A1B` (Brehm 2017 baseline) | Rev 14.0 (2020-03-24) | 21 | 865 KB |
| `XLamp-XPE2.pdf` | Cree LED `XLamp XP-E2` (Blue, Green, Cool White) | CLD-DS56 Rev 25B (2026) | 49 | 3.0 MB |
| `lm3410.pdf` | TI `LM3410 / LM3410-Q1` Boost CC Driver | SNVS541H (Aug 2016) | 57 | 1.4 MB |
| `ds13005.pdf` | Diodes Inc `B340A-13-F` 40 V 3 A Schottky | DS13005 Rev. 9-2 | 3 | 124 KB |
| `srn6045.pdf` | Bourns `SRN6045` Semi-Shielded Power Inductors | Rev. 01/20 | 3 | 455 KB |
| `CRL.pdf` | Bourns `CRL1206` Low-Value Sense Resistors | Rev. 03/05/25 | 4 | 533 KB |
| `dcrcwe3.pdf` | Vishay `D/CRCW e3` Thick-Film Chip Resistors | Doc 20035 (2026-04-14) | 13 | 147 KB |
| `smbj.pdf` | Vishay `SMBJ5.0A` 600 W TVS Diode | Doc 88392 (2024-01-09) | 6 | 127 KB |
| `usb4085.pdf` | GCT `USB4085-GF-A` USB-C Receptacle | Rev B PCN (2023-02-28) | 3 | 197 KB |
| `DMG2305UX.pdf` | Diodes Inc `DMG2305UX-7` P-MOSFET | DS36196 Rev. 8-2 (Jul 2021) | 6 | 411 KB |
| `BZT52C.pdf` | Diodes Inc `BZT52C5V6` / `BZT52C20` Zener Diodes | DS18004 Rev. 38-2 (Oct 2017) | 5 | 386 KB |
| `BAV70_onsemi.pdf` | onsemi `BAV70LT1G` Common-Cathode Dual Diode | Rev. BAV70LT1/D | 7 | 239 KB |
| `BAW56_onsemi.pdf` | onsemi `BAW56L` Common-Anode Dual Diode (reference/pinout check) | Rev. BAW56LT1/D | 8 | 239 KB |
| `MF-LSMF.pdf` | Bourns `MF-LSMF300/24X` 2920 24 V 3.0 A PTC Fuse | Current Rev. | 6 | 1.4 MB |
| `MF-MSMF.pdf` | Bourns `MF-MSMF` 1812 PTC Series (reference check) | Current Rev. | 16 | 1.3 MB |

> **Notes on Verified Datasheet Corrections:**
> 1. **`F1` PTC Fuse (`MF-LSMF300/24X` vs `MF-MSMF300/24X`):** Inspection of `MF-MSMF.pdf` shows `MF-MSMF300/24X` does not exist (`MF-MSMF` only offers `300/6X` at 6 V or `260/16X` at 16 V). `MF-LSMF.pdf` provides **`MF-LSMF300/24X`** (`2920`, `24 V`, `3.0 A` hold / `5.2 A` trip), matching the exact required voltage/current rating.
> 2. **`D12` Diode-OR (`BAV70LT1G` vs `BAW56`):** Inspection of `BAW56_onsemi.pdf` p. 1 confirms `BAW56` is **Common Anode** (incompatible with positive-OR steering of `SW1` -> `EN1`), whereas `BAV70_onsemi.pdf` p. 1 confirms **`BAV70LT1G`** (`BAV70,215`) is the pin-compatible SOT-23-3 **Common Cathode** dual switching diode (`100 V`, `200 mA`).

---

## 2. LED Emitters (`D1..D8`)

| Parameter | `SST-10-UV-A130-G365-00` (4× UV) | `CUN66A1B` (Baseline Ref.) | `XPEBRY-L1-0000-00R02` (2× Blue) | `XPEBGR-L1-0000-00E01` (1× Green) | `XPEBWT-L1-0000-00F51` (1× CW) |
|---|---|---|---|---|---|
| **PDF Citation** | `Luminus_SST-10-UV_Datasheet.pdf` pp. 1–6, 10 | `CUN66A1B_200324_R14.0.pdf` pp. 3–9 | `XLamp-XPE2.pdf` pp. 3–4, 38–43 | `XLamp-XPE2.pdf` pp. 3–4, 11 | `XLamp-XPE2.pdf` pp. 3–4, 43 |
| **Wavelength / CCT** | `365–375 nm` (`370 nm` typ) | `360–370 nm` (`367 nm` typ) | `450–460 nm` (`455 nm` typ) | `520–535 nm` (`528 nm` typ) | `6200 K` typ |
| **$V_f$ @ 350 mA, 25 °C** | `~3.60 V` typ (`2.7–3.9 V`, *p. 6*) | `~3.50 V` typ (*p. 4*) | `2.93 V` typ / `3.40 V` max (*p. 4*) | `2.70 V` typ / `3.25 V` max (*p. 4*) | `~2.93 V` typ / `3.19 V` max (`2.84/3.10 V` @ 85 °C, *p. 4*) |
| **$V_f$ @ 500 mA, 25 °C** | `2.8` min / `3.7` typ / `4.0` max (*p. 5*) | `3.4 / 3.6 / 3.8 V` (*p. 3, 9*) | — | — | — |
| **$V_f$ Tempco** | `-2.67 mV/°C` (*p. 6*) | `-2.67 mV/°C` (*p. 7*) | `-1.5 mV/°C` (*p. 3*) | `-1.2 mV/°C` (*p. 3*) | `-1.5 mV/°C` (*p. 3*) |
| **$I_{f,\max}$ (CW)** | `1.0 A` (`365 nm`, *p. 4*) | `0.7 A` (*p. 3*) | `1.2 A` (*p. 3*) | `1.5 A` (*p. 3*) | `1.5 A` (*p. 3*) |
| **$T_{j,\max}$** | **`100 °C`** (*p. 4*) | `90 °C` (*p. 3*) | **`150 °C`** (*p. 4*) | **`150 °C`** (*p. 4*) | **`150 °C`** (*p. 4*) |
| **$R_{\theta J-s}$** | **`1.4 °C/W`** (*p. 1*) | `3.8 °C/W` (*p. 3*) | `5.7 °C/W` (*p. 3*) | `9.0 °C/W` (*p. 3*) | `5.8 °C/W` (*p. 3*) |
| **Pad Compatibility** | `A130`: `3.25×3.25 mm` (XP-compatible, *p. 10*) | Z5 `3535` | `3.30×3.30 mm` XP (*pp. 38–39*) | `3.30×3.30 mm` XP (*pp. 38–39*) | `3.30×3.30 mm` XP (*pp. 38–39*) |

---

## 3. Boost Constant-Current Driver (`U1`, `U2` = `TI LM3410XMY/NOPB`)

Extracted from `datasheets/lm3410.pdf` (`SNVS541H`, Sec. 6.1–6.5 pp. 4–5, Fig. 6 p. 6, Table 25 p. 39, Sec. 10.3.5 p. 40):
- **Package & Thermal:** `8-HVSSOP / MSOP-PowerPAD` (`DGN`), **$R_{\theta JA} = 53.7\text{ °C/W}$**, $R_{\theta JC(\text{bot})} = 6.8\text{ °C/W}$ (replaces `SOT-23-5 DBV` which has $R_{\theta JA} = 164.2\text{ °C/W}$ and an explicit `400 mW` internal dissipation ceiling in Sec. 6.3 p. 4).
- **Recommended Operating Ratings:** $V_{\text{in}} \in [2.7, 5.5]\text{ V}$ (`7.0 V` abs max); $V_{\text{SW}} \in [3.0, 24.0]\text{ V}$ (`26.5 V` abs max); $T_J \in [-40, +125]\text{ °C}$ (`150 °C` abs max, `165 °C` thermal shutdown).
- **Feedback Reference $V_{FB}$:** **`178 mV` min / `190 mV` typ / `202 mV` max** ($\pm 6.3\%$ over $-40\dots 125^\circ\text{C}$), $I_{FB} = 0.1\,\mu\text{A}$ typ (`1 µA` max).
- **Switching Frequency $f_{SW}$ (`LM3410X`):** **`1200 kHz` min / `1600 kHz` typ / `2000 kHz` max**.
- **Switch Current Limit $I_{CL}$:** **`2.1 A` min / `2.8 A` typ**.
- **Duty Cycle Limits:** $D_{\max} = 88\%$ min / `92%` typ; $D_{\min} = 5\%$ typ.
- **Switch $R_{DS(\text{on})}$:** `170 mΩ` typ ($25^\circ\text{C}$) / `250 mΩ` typ ($125^\circ\text{C}$, Fig. 6) / **`330 mΩ` max**.
- **Switching Times (Table 25 p. 39):** $t_r \approx 6\text{–}10\text{ ns}$ (`8 ns` nom), $t_f \approx 5\text{–}8\text{ ns}$ (`6.5 ns` nom).
- **DIM Control:** $V_{\text{DIM\_L}} \le 0.4\text{ V}$ (shutdown, $I_Q = 80\text{ nA}$ typ), $V_{\text{DIM\_H}} \ge 1.8\text{ V}$ (enable, max $V_{\text{in}} + 0.3\text{ V}$, **do not float**); $I_{\text{DIM}} = 100\text{ nA}$; $I_Q$ switching `7 mA` typ / `11 mA` max.

---

## 4. Power Magnetics, Diodes, Passives & Protection

| RefDes | MPN | Key Datasheet Specs & Citations |
|---|---|---|
| `D9`, `D10` | `Diodes Inc B340A-13-F` | `ds13005.pdf` pp. 1–2: `SMA`, $V_{RRM}=40\text{ V}$, $I_{F(AV)}=3.0\text{ A}$, $I_{FSM}=100\text{ A}$, $V_F = 0.38\text{ V}$ @ 1 A / `0.43 V` @ 2 A / `0.46 V` typ (`0.50 V` max) @ 3 A ($25^\circ\text{C}$), $I_R \le 0.5\text{ mA}$ @ 40 V ($25^\circ\text{C}$), $T_{j,\max}=125^\circ\text{C}$, $R_{\theta JA}=50^\circ\text{C/W}$, $R_{\theta JT}=10^\circ\text{C/W}$. |
| `L1`, `L2` | `Bourns SRN6045-100M` | `srn6045.pdf` p. 1: $10\text{ }\mu\text{H} \pm 20\%$ (`8.0 µH` min), $I_{\text{rms}} = 2.5\text{ A}$, $I_{\text{sat}} = 3.0\text{ A}$, $DCR_{\max} = 58.6\text{ m}\Omega$, SRF `15 MHz` typ, `-40 to +125 °C`. *(Selected over `SRN6045-6R8Y` `±30%` for superior `ICL` corner margin.)* |
| `R3`, `R4` | `Bourns CRL1206-FW-R560ELF` | `CRL.pdf` p. 1: `0.56 Ω ±1%`, `0.50 W @ 70 °C`, `±200 ppm/°C`, `-55 to +155 °C`, `1206` ($I_{\text{LED,typ}} = 339.3\text{ mA}$, $P = 64.5\text{ mW}$). |
| `R1`, `R2` | `Vishay CRCW08055K10FKEA` | `dcrcwe3.pdf` p. 1: `5.1 kΩ ±1%`, `0.25 W @ 70 °C`, `±100 ppm/K`, `0805`. |
| `J1` | `GCT USB4085-GF-A` | `usb4085.pdf` pp. 1–2: `VBUS 5.0 A`, `GND 6.25 A`, `48 V`, `40 mΩ` init, `20,000` cycles, `-40 to +85 °C`. |
| `F1` | `Bourns MF-LSMF300/24X` | `MF-LSMF.pdf` pp. 1–2: `2920`, `24 V`, `40 A`, $I_{\text{hold}}=3.0\text{ A}$ @ $23^\circ\text{C}$ (`2.15 A` @ $60^\circ\text{C}$), $I_{\text{trip}}=5.2\text{ A}$, $R_{\min}=15\text{ m}\Omega$, $R_{1\max}=75\text{ m}\Omega$. |
| `D11` | `Vishay SMBJ5.0A-E3/5B` | `smbj.pdf` pp. 1–2: `SMB`, $V_{RWM}=5.0\text{ V}$, $V_{BR}=6.40\text{–}7.07\text{ V}$ @ 10 mA, $V_C = 9.2\text{ V}$ @ `65.2 A`, `600 W`, $I_D \le 800\text{ }\mu\text{A}$ @ 5.0 V. |
| `Q1` | `Diodes Inc DMG2305UX-7` | `DMG2305UX.pdf` pp. 1–2: `SOT-23-3`, $BV_{DSS}=-20\text{ V}$, $I_D = -5.0\text{ A}$, $V_{GS(\text{th})} = -0.5\text{ to }-0.9\text{ V}$, $R_{DS(\text{on})} = 40\text{ m}\Omega$ typ / `52 mΩ` max @ $-4.5\text{ V}$, $R_{\theta JA} = 90^\circ\text{C/W}$. |
| `D12` | `onsemi BAV70LT1G` | `BAV70_onsemi.pdf` pp. 1–2: `SOT-23-3` Common Cathode, `100 V`, `200 mA`, $V_F \le 715\text{ mV}$ @ 1 mA, $I_R \le 1\text{ }\mu\text{A}$ @ 100 V ($25^\circ\text{C}$). |
| `D13`, `D14` | `Diodes Inc BZT52C20-7-F` | `BZT52C.pdf` pp. 1–2: `SOD-123`, $V_Z = 18.8\text{–}21.2\text{ V}$ (`20.0 V` nom @ 5 mA), $I_R \le 0.1\text{ }\mu\text{A}$ @ 14 V, `500 mW @ 75 °C`. |
| `D15` | `Diodes Inc BZT52C5V6-7-F` | `BZT52C.pdf` pp. 1–2: `SOD-123`, $V_Z = 5.2\text{–}6.0\text{ V}$ (`5.6 V` nom @ 5 mA), `500 mW @ 75 °C`. |
| `C1..C3` | `Murata GRM31CR71E106KA12L` | `10 µF ±10%, 25 V, X7R, 1206` (`~8.0 µF` effective at 5 V DC bias). |
| `C4..C5` | `Samsung CL32B106KBJNFNE` | `10 µF ±10%, 50 V, X7R, 1210` (`~7.5 µF` effective at 16 V DC bias). |
| `SW1` | `E-Switch 100SP3T1B1M1QEH` + `C&K 759D02000` | `SPDT On-Off-On`, `5 A`, `1/4-40` bushing, `Ø 6.35 mm` cutout, full silicone boot (`10.41 mm` actuator). |
