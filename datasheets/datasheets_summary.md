# Datasheets & Parameter Summary (Rev 4.9 — Value-Engineered 2-Reel Hybrid & Unified M3)

Canonical structured machine-readable parameters live in [datasheets_summary.json](datasheets_summary.json).

## Key Verified Part Ratings (Rev 4.9)

| RefDes | Part (MPN) | Package / Finish | Key Verified Ratings | Sourcing |
|---|---|---|---|---|
| `U1, U2` | `Diodes AL8860WT-7` | `TSOT25` | `4.5–40 V`, `1.0 A`, `100 mV` sense, `1 MHz` max, `RthJA = 147 °C/W` | JLCPCB Ext 1/2 (`C125330`) |
| `U3` | `WCH CH224A` | `ESSOP-10` (`1.0 mm` leaded) | `32 V` abs max `VHV/VBUS/PG`, `CFG1 = 120 kΩ` → `20 V` PD, internal `5.1 kΩ` Rd | JLCPCB Ext 2/2 (`C42459160`) |
| `U4` | `onsemi LM393DR2G` | `SOIC-8` | `2–36 V`, `0..+70 °C` commercial (`LM2903DR2G` `C57474` industrial alt), `2.5 mA` max | JLCPCB Basic (`C7955`) |
| `U5` | `Changjing CJ431` | `SOT-23-3` | `2.500 V ±0.5%`, `-25..+85 °C` (`1=REF, 2=K, 3=A`); damped with `R24 = 10 Ω` + `C16 = 100 nF` | JLCPCB Basic (`C3113`) |
| `F1` | `Littelfuse 046801.5NRHF` | `1206` Slo-Blo | `1.5 A`, `63 V DC`, **`50 A` interrupt**, `I²t = 0.288 A²s`, `R_cold = 0.044 Ω` | Farnell UK DIY 2-pad SMD |
| `D11` | `Littelfuse SMBJ22A` | `DO-214AA (SMB)` | `22 V` Vrwm, `24.4–26.9 V` Vbr (`TBV1 = 9.6e-4 /°C`), `600 W` uni-dir | Farnell UK DIY 2-pad SMD |
| `L1, L2` | `Bourns SRN6045-680M` | `6.0 × 6.0 × 4.5 mm` | `68 µH ±20%`, `Isat = 1.0 A`, `Irms = 0.90 A`, `DCR_max = 0.351 Ω` | Farnell UK DIY 2-pad SMD |
| `R3, R4` | `Bourns CRL1206-FW-R300ELF` | `1206` | `0.30 Ω ±1%`, `0.50 W` (`15×` derated @ `33 mW`) | Farnell UK DIY 2-pad SMD |
| `R7` | `Vishay CRCW25121R00FKEG` | `2512` | `1.0 Ω ±1%`, **`1.0 W`**, **`600 W` `5–10 µs` pulse limit** | Farnell UK DIY 2-pad SMD |
| `R24, C16` | `10.0 Ω 0805` + `100 nF 0603` | `0805` / `0603` | Damped `V_REF` ESD bypass (`Q <= 1` `TL431`-stable; `τ = 1.0 ms < 3.0 ms`) | JLCPCB Basic (`C17415`/`C14663`) |
| `D1..D4` | `Luminus SST-10-UV 365 nm` | `20 mm` Cu DTP Star | `365 nm`, `3.60 V` typ, `RthJS = 1.4 K/W`, `Tj_max = 100 °C`, isolated pad | Convoylight.com (1 order!) |
| `D5, D6` | `Osram KB CSLNM1.14 455 nm` | `20 mm` Cu DTP Star | `450 nm` peak / `455 nm` dom, `2.85 V` @ `333 mA`, `RthJS = 4.1–4.9 K/W`, isolated pad | Convoylight.com (Faces 1 & 3) |
| `D7` | `Osram KP CSLNM1.F1 Green` | `20 mm` Cu DTP Star | `515–565 nm` phosphor green, `2.85 V` @ `333 mA`, `RthJS = 4.1–4.9 K/W`, isolated pad | Convoylight.com (Face 2) |
| `D8` | `Osram KW CSLNM1.TG 6500 K` | `20 mm` Cu DTP Star | `6500 K` Cool White, `2.85 V` @ `333 mA`, `RthJS = 4.1–4.9 K/W`, isolated pad | Convoylight.com (Face 4) |
| `SW1 + Boot` | `C&K 7211SYZBE` + `759D02000` | `1/4-40` Panel | Gold dry-circuit `0.4 VA max`, `12.70(X)×11.43(Y)` body, `18.6 mm` booted protrusion | Farnell UK |
| `MECH-TUBE-1` | Extruded `XT PMMA` `Ø60×54×3` | `115 mm` cut | `~80–85%` @ `365 nm`; verify w/ white-paper fluorescence bench check; no IPA | eBay UK / Amari Plastics |
| `MECH-SEAL-1` | `Soudal Fix ALL Crystal` | `290 ml` | Solvent-free SMX hybrid MS-polymer; plastic-to-Al seals only (Screwfix `51412`) | Screwfix / Toolstation UK |
