# LepiLED DIY Maxi Switch — Electronics Architecture & Design Rationale

**Project:** LepiLED DIY Maxi Switch (Milestone M1)
**Target Application:** Fanless, UK-sourced (~£100 lamp-parts BOM) moth-trapping lamp with Brehm-inspired `4-UV / OFF / 8-ALL` Maxi-Switch functionality powered from standard `5 V` USB power banks.

---

## 1. Architecture Comparison: Off-the-Shelf Modules vs Custom PCB (`2× LM3410XMY`)

We evaluated three off-the-shelf (OTS) constant-current driver approaches against a custom 2-layer `36 × 46 mm` PCB hosting **2× TI `LM3410XMY/NOPB`** boost controllers:

| Criterion | Generic `XL6009` CC-CV Module | `Adafruit TPS61169` Breakout | `Led Senser V2 Rev.2` (commercial) | **Custom PCB (`2× TI LM3410XMY/NOPB`)** |
|---|---|---|---|---|
| **Topology & String Support** | Single bulky CC-CV module (~50×25 mm); single-channel only | Single boost (`1.8 A` typ / **`1.2 A` min** switch limit). At `4.5 V` droop, 4S UV needs `~1.6 A` peak (`> 1.2 A` limit); 8S is impossible | Single 8S boost (`35 V`, `3 A` in). UV-only requires bypassing 4 visible LEDs, restricting $V_{\text{in}} \le 9\text{ V}$ | **Dual independent 4S CCM boosts** (`U1`: 4S UV `~14.5 V`; `U2`: 4S Vis `~11.7 V`), well below `24 V` `Vsw_max` and `2.10 A` `Icl_min` |
| **UK Delivered Cost** | `~£3–£7 × 2` (plus hot-switch risk) | `~£9 × 2` (`£18`) + insufficient `Icl` margin | `€30–€50+` (`£35–£45+` delivered) — breaks £100 BOM | **`~£19–£24` total** (5× JLCPCB FR4 + 2× `LM3410XMY` + passives/USB-C/protection) |
| **Efficiency & Thermal** | `~78–82%` @ 5 V; bulky trimpot vibration drift | Trips current limit / thermal foldback above `~4 W` from 5 V | `~80–85%` @ 5 V (Brehm 2017: `13.4 W` input) | **`~88–89%` converter eff.** (`10.62 W` total USB input in `8-ALL`, `~5.5 W` in `4-UV`), MSOP-PowerPAD $R_{\theta JA}=53.7^\circ\text{C/W}$ |
| **Powerbank OCP Immunity** | Large `100–470 µF` electrolytic input caps trip USB OCP | Hits `1.2 A` switch limit on `5 V` cable droop | Requires `2.7–3.0 A` USB-A/C source | **Active soft-start (`Q1A/Q1B` + `Q3` `~4 ms` ramp)**: `IC=0` cold plug peak = **`2.15 A`** (`<< 3 A`); `2.05–2.12 A` steady `8-ALL` |
| **Maxi-Switch & Fault Safety** | High-current output switching risks hot-open destruction | Output hot-switch hazard | Bypass switch cannot safely open boost loop | **Logic-level `DIM` switching + `BZT52C18` OVP (`< 22.6 V` peak) + back-to-back PMOS `±16 V` cutoff (`TL431` OVP, `VIN_PROT < 6.11 V`)** |

---

## 2. Critical Datasheet-Driven Design Decisions

### 2.1 Package Thermal Catch: `LM3410XMY/NOPB` (MSOP-PowerPAD) vs `LM3410XMF` (SOT-23-5)
- `datasheets/lm3410.pdf` (SNVS541H, Sec. 6.3–6.4 p. 4 & Sec. 10.3.5 p. 40) specifies **`RθJA = 164.2 °C/W`** and an explicit **`400 mW` internal dissipation ceiling** for `SOT-23-5` (`DBV`), warning designers to switch to `WSON-6` or **`8-pin MSOP-PowerPAD (DGN)`** whenever internal loss exceeds `400 mW`.
- On Channel 1 (4S UV @ `339 mA`), worst-case `4.25 V` input droop with `Rds(on) = 0.33 Ω` produces `1.290 W` IC dissipation (`datasheet_spec` corner) — violating SOT-23-5 limits.
- Using **`LM3410XMY/NOPB`** (`DGN` MSOP-PowerPAD, **`RθJA = 53.7 °C/W`**, `RθJC(bot) = 6.8 °C/W`, `1=NC, 2=PGND, 3=VIN, 4=DIM, 5=FB, 6=AGND, 7=SW, 8=NC, DAP=GND`) with 4–6 thermal vias keeps $T_J = 124.3^\circ\text{C} \le 125^\circ\text{C}$ across all `10,935` datasheet corners down to `4.25 V` at $T_{\text{PCB}} \le 55^\circ\text{C}$ (and $108.4^\circ\text{C}$ / $114.7^\circ\text{C}$ at `4.50 V`).

### 2.2 Inductor Evaluation: `Bourns SRN6045-100M` vs `SRN6045-6R8Y`
In `datasheets/srn6045.pdf`, `SRN6045-100M` (`10 µH ±20%`, `8.0 µH` min, $I_{\text{sat}} = 3.0\text{ A}$, $I_{\text{rms}} = 2.5\text{ A}$, $DCR_{\max} = 58.6\text{ m}\Omega$) provides superior margin against `LM3410`'s `2.10 A` minimum switch current limit (`Icl_min`):
- **Datasheet corners (`V_IC >= 4.25 V`, `VFB ±6.3%`, `Rsense ±1%`):** `I_L,pk,max = 1.872 A` (`+0.228 A` margin vs `2.10 A`), `0 / 10,935` DCM corners.
- **Extreme OOS corners (`V_IC >= 4.50 V`, `VFB ±15%`, `Rsense ±5%`):** `I_L,pk,max = 2.005 A` (`+0.096 A` margin vs `2.10 A`).

### 2.3 Sense Resistor (`R3`, `R4`) & Catch Diode (`D9`, `D10`)
- **`R3`, `R4` = `Bourns CRL1206-FW-R560ELF` (`0.56 Ω ±1%`, `0.50 W`, `1206`):** $I_{\text{LED,nom}} = 0.190 / 0.56 = \mathbf{339.3\text{ mA}}$ ($P = 64.5\text{ mW}$, `7.7×` derated below `0.50 W`).
- **`D9`, `D10` = `Diodes Inc B340A-13-F` (`40 V`, `3.0 A`, `SMA`, `ds13005.pdf`):** `0.38 V` typ at `1 A`, `0.50 V` max at `3 A`, `RθJA = 50 °C/W`.

### 2.4 Power Input, `±16 V` Precision `TL431` Fault Cutoff, Hold Margin & Cold Hot-Plug Soft-Start
1. **USB-C & Optional Gland Entry (`J1`, `R1`, `R2`, `C12`, `TP1`, `TP2`):** `GCT USB4085-GF-A` (`VBUS A4/B4/A9/B9` `5.0 A`, `GND A1/B1/A12/B12/SH` `6.25 A`) with `100 nF 25 V` ESD cap `C12` and dedicated `5.1 kΩ ±1%` `Rd` pulldowns (`Vishay CRCW08055K10FKEA`, `0.125 W` std / `0.25 W` ext) on `CC1` (`R1`) and `CC2` (`R2`), plus `TP1`/`TP2` TH pads for the recommended captive `18 AWG ≤ 1.0 m` USB cable through an **M16 IP68 gland**.
2. **Upgraded Polyfuse (`F1` = `Bourns MF-LSMF500/16X`):** `2920`, `16 V max` (covers `±16 V` faults), `40 A Imax`, `5.0 A` hold @ `23 °C`, **`3.75 A @ 50 °C`**, **`3.525 A @ 55 °C`**, **`3.30 A @ 60 °C`**, `R_1max = 25 mΩ` (`MF-LSMF.pdf` pp. 2–3). Under full stacked `datasheet_spec` worst-case USB droop (`4.85 V` `18 AWG ≤ 1.0 m` captive `I_in = 3.110 A` or `4.90 V` `18 AWG ≤ 0.8 m` USB-C `I_in = 3.237 A`), `F1` maintains positive hold margin at `55 °C` and `60 °C`.
3. **Back-to-Back P-MOSFET Reverse-Polarity, `TL431` Precision OVP Cutoff & Soft-Start (`Q1A`, `Q1B`, `U3`, `Q2..Q4`, `D15`, `D16`, `D11`, `R10..R20`, `C11`):**
   - `Q1A` (`DMG2305UX-7`, `D=VBUS_FUSED`, `S=V_MID`) blocks `-12 V / -16 V` reverse polarity (`-16.1 pA` reverse current, `VIN_PROT ≈ -22 µV`; `D11` `SMBJ5.0A` sits **downstream** on `VIN_PROT`).
   - `U3` (`TI TL431AIDBZR`, `2.495 V ±1%`, `tl431.pdf`) + `R12/R13` (`13.7 kΩ / 10.0 kΩ ±1%`) + `Q2` (`MMBT3906LT1G`) + `D16` (`BAW56LT1G` Common Anode) + `Q4` (`MMBT3904LT1G` latch clamp) + `R19` (`27 kΩ` hysteresis) sets a tight OVP threshold in **`[5.75 V, 6.14 V]`** — holding ON at `5.5 V @ 85 °C` (`0` false trips) while cutting off strictly below `D11` `Vbr_min = 6.40 V`. Verified across `6.0..16.0 V` in `ngspice` (`max(P(D11)) = 25.4 µW << 50 mW`, `VIN_PROT_pk <= 6.11 V < 7.0 V`, every resistor `<= 28.8 mW << 50 mW` at `+16.0 V`).
   - `D15` (`BZT52C5V6-7-F`, `Q1_GATE -> V_MID`) clamps `Q1A/Q1B` `|VGS| <= 6.0 V < ±8.0 V` abs max even during `200 ns` `+5.5 -> +16.0 V` live steps (`VIN_PROT_pk = 5.18 V`, `Vgs_min = -4.74 V`).
   - `Q3` (`MMBT3904LT1G`) + `R11` (`1.5 kΩ`) + `R14` (`220 kΩ`) + `C11` (`100 nF`) slews `Q1_GATE` smoothly over `~4 ms` on cold `0 -> 5 V` hot-plug (`IC=0` everywhere), limiting peak inrush to **`2.15 A`** (`I_L1/I_L2 <= 1.34 A << 3.0 A` `I_sat`).
   - `C4..C5` use `Samsung CL32B106KBJNFNE` (`10 µF, 50 V, X7R, 1210`, `~7.5 µF` eff. at `16 V`).

### 2.5 `4-UV / OFF / 8-ALL` Maxi-Switch Logic & TI Fig. 14 `BZT52C18` OVP
- **Mode Switch (`SW1` + `SW1_BOOT`):** `E-Switch 100SP3T1B1M1QEH` (`SPDT On-Off-On`, `Ø 6.35 mm` cutout) + `C&K 759D02000` full silicone boot, wired via `J4` (`JST B3B-XH-A`, `datasheets/jst_xh.pdf`).
- **Diode-OR Steering (`D12` = `onsemi BAV70LT1G`, Common-Cathode):** `R5`/`R6` (`10 kΩ`) pull `DIM` pins cleanly to `0 V` in `OFF` mode; `R7` (`10 kΩ`) + `C6` (`100 nF`) gives `1.0 ms` Ch2 turn-on stagger and `2.0 ms` (`R6+R7`) turn-off discharge (`DIM2_NET = 0.22 V < 0.4 V` by `9.5 ms`, `I_L2_avg = -12 µA`, `4-UV` backfeed `= 35 nA`).
- **Open-Load OVP (`D13`, `D14` = `Diodes Inc BZT52C18-7-F`, `R8`, `R9` = `100 Ω`):** Wired per **TI `lm3410.pdf` Fig. 14 (p. 15)**. `BZT52C18` (`16.8–19.1 V`, `Zzt <= 45 Ω`) replaces `BZT52C20`: at `-10 °C` max `Vf` (`~16.4 V`), Zener leakage is negligible (`< 100 µA`), while worst-case open-load (`19.1 V` Zener, `45 Ω`, `5.5 V` in, `8 µH`, `1.2 MHz`, `+15% VFB`) clamps `VOUT1_pk = 22.36 V` and `VSW_pk = 22.56 V` (**`< 24.0 V` recommended max**!).

### 2.6 Active Emitter Selection (`8× 3535 SMD` on `4×` Al MCPCB Strips)
- `4× Luminus SST-10-UV-A130-G365-00` (365 nm, `A130` `3.25×3.25 mm` pad)
- `2× Cree XPEBRY-L1-0000-00S02` (Royal Blue, `450–460 nm`, `XLamp-XPE2.pdf` p. 10)
- `1× Cree XPEBGR-L1-0000-00K01` (Green, `520–535 nm`, `XLamp-XPE2.pdf` p. 11)
- `1× Cree XPEBWT-L1-0000-00H51` (Cool White, `6200 K`, `XLamp-XPE2.pdf` p. 5)
- Mounted on **4× Custom JLCPCB `1.0 W/m·K` Al MCPCB dual-LED strips** (`MECH-MCPCB-1..4`), with 20 mm Cu DTP stars as electrical-equivalent fallback.

---

## 3. Reproducing the M1 Environment & Simulations

User-space tools outside `/home/alimuldal/src/lepiled`:
- **`ngspice 45.2+ds-1`:** `/home/alimuldal/.local/share/lepiled-tools/bin/ngspice`
- **Python `3.14.4` venv:** `/home/alimuldal/.local/share/lepiled-venv` (`numpy`, `scipy`, `matplotlib`, `schemdraw`, `cairosvg`)

```bash
/home/alimuldal/.local/share/lepiled-venv/bin/python circuit_design/generate_schematic.py
/home/alimuldal/.local/share/lepiled-venv/bin/python circuit_design/sim/run_simulations.py
```
