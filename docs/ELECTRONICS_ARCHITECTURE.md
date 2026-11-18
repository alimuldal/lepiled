# LepiLED DIY Maxi Switch — Electronics Architecture & Design Rationale

**Project:** LepiLED DIY Maxi Switch (Milestone M1)
**Target Application:** Fanless, UK-sourced (~£100 lamp-parts BOM) moth-trapping lamp with Brehm-inspired `4-UV / OFF / 8-ALL` Maxi-Switch functionality powered from standard `5 V` USB power banks.

---

## 1. Architecture Comparison: Off-the-Shelf Modules vs Custom PCB (`2× LM3410XMY`)

We evaluated three off-the-shelf (OTS) constant-current driver approaches against a custom 2-layer `36 × 46 mm` PCB hosting **2× TI `LM3410XMY/NOPB`** boost controllers:

| Criterion | Generic `XL6009` CC-CV Module | `Adafruit TPS61169` Breakout | `Led Senser V2 Rev.2` (commercial) | **Custom PCB (`2× TI LM3410XMY/NOPB`)** |
|---|---|---|---|---|
| **Topology & String Support** | Single bulky CC-CV module (~50×25 mm); single-channel only | Single boost (`1.8 A` typ / **`1.2 A` min** switch limit). At `4.5 V` droop, 4S UV needs `~1.6 A` peak (`> 1.2 A` limit); 8S is impossible | Single 8S boost (`35 V`, `3 A` in). UV-only requires bypassing 4 visible LEDs, restricting $V_{\text{in}} \le 9\text{ V}$ | **Dual independent 4S CCM boosts** (`U1`: 4S UV `~14.4 V`; `U2`: 4S Vis `~11.5 V`), well below `24 V` `Vsw_max` and `2.10 A` `Icl_min` |
| **UK Delivered Cost** | `~£3–£7 × 2` (plus hot-switch risk) | `~£9 × 2` (`£18`) + insufficient `Icl` margin | `€30–€50+` (`£35–£45+` delivered) — breaks £100 BOM | **`~£18–£22` total** (5× JLCPCB FR4 + 2× `LM3410XMY` + passives/USB-C/protection) |
| **Efficiency & Thermal** | `~78–82%` @ 5 V; bulky trimpot vibration drift | Trips current limit / thermal foldback above `~4 W` from 5 V | `~80–85%` @ 5 V (Brehm 2017: `13.4 W` input) | **`~88%` converter eff.** (`~10.3 W` total USB input in `8-ALL`, `~5.5 W` in `4-UV`), MSOP-PowerPAD $R_{\theta JA}=53.7^\circ\text{C/W}$ |
| **Powerbank OCP Immunity** | Large `100–470 µF` electrolytic input caps trip USB OCP | Hits `1.2 A` switch limit on `5 V` cable droop | Requires `2.7–3.0 A` USB-A/C source | **Low ceramic $C_{\text{in}}$ (`~24 µF` eff.) + `1.0 ms` Ch2 stagger (`R7/C6`)**; `~2.07 A` steady `8-ALL` fits standard `2.4 A / 3 A` banks |
| **Maxi-Switch Safety** | High-current output switching risks hot-open destruction | Output hot-switch hazard | Bypass switch cannot safely open boost loop | **Logic-level `DIM` switching (`BAV70LT1G` + `10 kΩ`) + TI Fig. 14 `20 V` Zener OVP**; zero hot-open hazard |

---

## 2. Critical Datasheet-Driven Design Decisions

### 2.1 Package Thermal Catch: `LM3410XMY/NOPB` (MSOP-PowerPAD) vs `LM3410XMF` (SOT-23-5)
- `datasheets/lm3410.pdf` (SNVS541H, Sec. 6.3–6.4 p. 4 & Sec. 10.3.5 p. 40) specifies **`RθJA = 164.2 °C/W`** and an explicit **`400 mW` internal dissipation ceiling** for `SOT-23-5` (`DBV`), warning designers to switch to `WSON-6` or **`8-pin MSOP-PowerPAD (DGN)`** whenever internal loss exceeds `400 mW` or total stage loss exceeds `750 mW`.
- On Channel 1 (4S UV @ `339 mA`), worst-case `4.5 V` input droop with hot `Rds(on) = 0.25–0.33 Ω` produces `~550–850 mW` IC dissipation — violating SOT-23-5 limits and risking `165 °C` thermal shutdown inside a sealed end cap.
- Switching to **`LM3410XMY/NOPB`** (`8-HVSSOP / MSOP-PowerPAD`, **`RθJA = 53.7 °C/W`**, `RθJC(bot) = 6.8 °C/W`, identical ~£2.35 UK unit cost) reduces $\Delta T_{JA}$ by **3.06×**, keeping worst-case junction temperature safely under `125 °C`.

### 2.2 Inductor Evaluation: `Bourns SRN6045-100M` vs `SRN6045-6R8Y`
In `datasheets/srn6045.pdf`, sub-10 µH parts carry **`Y` (±30%)** tolerance (`SRN6045-6R8Y` drops to `4.76 µH` minimum), whereas `SRN6045-100M` (`10 µH`) carries **`M` (±20%)** (`8.0 µH` minimum, $I_{\text{sat}} = 3.0\text{ A}$, $I_{\text{rms}} = 2.5\text{ A}$, $DCR_{\max} = 58.6\text{ m}\Omega$). Exhaustive corner sweeps across `Vin ∈ [4.5, 5.5] V`, `L` full tolerance, `Vf` across `-10 °C..+85 °C`, and `fsw ∈ [1.2, 2.0] MHz` confirm `SRN6045-100M` delivers superior margin against `LM3410`'s `2.10 A` minimum switch current limit (`Icl_min`):
- **Datasheet corners (`VFB ±6.3%`, `Rsense ±1%`):** `SRN6045-100M` `I_L,pk,max = 1.679 A` (`+0.421 A` margin vs `2.10 A`), vs `1.770 A` (`+0.330 A`) for `6R8Y`.
- **Extreme out-of-spec corners (`VFB ±15%`, `Rsense ±5%`):** `SRN6045-100M` `I_L,pk,max = 1.924 A` (**`+0.176 A` margin**), vs `1.991 A` (`+0.109 A`) for `6R8Y`.
- **Zero DCM corners (`0 / 6,561` per channel/scenario)** and `41%` lower ripple current (`~0.31 A` vs `~0.52 A` worst case).
Accordingly, **`Bourns SRN6045-100M`** is selected for `L1` and `L2`.

### 2.3 Sense Resistor (`R3`, `R4`) & Catch Diode (`D9`, `D10`)
- **`R3`, `R4` = `Bourns CRL1206-FW-R560ELF` (`0.56 Ω ±1%`, `0.50 W`, `1206`):** Verified stocked value in `datasheets/CRL.pdf`, yielding $I_{\text{LED,nom}} = 0.190 / 0.56 = \mathbf{339.3\text{ mA}}$ ($P = 64.5\text{ mW}$, `7.7×` derated below `0.50 W`).
- **`D9`, `D10` = `Diodes Inc B340A-13-F` (`40 V`, `3.0 A`, `SMA`, `ds13005.pdf`):** `0.38 V` typ at `1 A`, `0.50 V` max at `3 A`, `RθJA = 50 °C/W`, `225k+` stock at DigiKey UK (`~£0.40`).

### 2.4 Power Input, Protection & USB Powerbank OCP Immunity
1. **USB-C & Optional Gland Entry (`J1`, `R1`, `R2`, `TP1`, `TP2`):** `GCT USB4085-GF-A` (`5.0 A` VBUS, `6.25 A` GND) with dedicated `5.1 kΩ ±1%` `Rd` pulldowns (`Vishay CRCW08055K10FKEA`) on `CC1` (`R1`) and `CC2` (`R2`). Parallel through-hole solder pads (`TP1` = `VBUS`, `TP2` = `GND`) allow builders using a captive USB cable through an **M16 IP68 nylon gland** to omit `J1/R1/R2` without modifying the PCB.
2. **Over-Current, ESD & Reverse Polarity (`F1`, `D11`, `Q1`, `D15`, `R10`):**
   - `F1` = **`Bourns MF-LSMF300/24X`** (`2920`, `24 V`, `3.0 A` hold / `5.2 A` trip, `datasheets/MF-LSMF.pdf`; corrects the nonexistent `MF-MSMF300/24X` part number cited in early notes).
   - `D11` = `Vishay SMBJ5.0A-E3/5B` (`600 W` TVS, `6.40–7.07 V` breakdown) clamps ESD spikes and crowds `F1` on >7 V fault inputs.
   - `Q1` = `Diodes Inc DMG2305UX-7` (`-20 V`, `-5.0 A`, `40 mΩ` typ P-MOSFET) + `D15` (`BZT52C5V6-7-F`) + `R10` (`100 kΩ`) provides low-loss (`~0.17 W`) reverse-polarity blocking.
3. **Powerbank OCP Immunity (`C1..C3`, `R7`, `C6`):**
   - Total ceramic input capacitance is `3 × 10 µF` (`Murata GRM31CR71E106KA12L`, `25 V`, `X7R`, `1206`, `~24 µF` effective at 5 V) + `2 × 100 nF`, keeping hot-plug charge impulse to `~120 µC` (`~4 µs`), well below USB powerbank OCP blanking (`0.5–5 ms`).
   - Output caps `C4..C5` use **`Samsung CL32B106KBJNFNE` (`10 µF`, `50 V`, `X7R`, `1210`)** (`~7.5 µF` effective at `16 V`), avoiding the severe DC-bias collapse of smaller `25 V` `1206` MLCCs.
   - `R7` (`10 kΩ`) + `C6` (`100 nF`) provides a `τ = 1.0 ms` soft-enable stagger on `U2.DIM` so Ch2 starts ~`0.47 ms` after Ch1 in `8-ALL` mode.

### 2.5 `4-UV / OFF / 8-ALL` Maxi-Switch Logic & TI Fig. 14 OVP Topology
- **Mode Switch (`SW1`):** `E-Switch 100SP3T1B1M1QEH` (`SPDT On-Off-On`, `5 A`, `1/4-40` bushing, `Ø 6.35 mm` panel cutout) paired with **`C&K 759D02000`** full silicone boot (replacing OOS `RS PRO 734-7233`), wired via `J4` (`B3B-XH-A`).
- **Diode-OR Steering (`D12` = `onsemi BAV70LT1G`, Common-Cathode):** `J4.1` (`4-UV`) and `J4.3` (`8-ALL`) feed the two anodes of `D12`, whose common cathode drives `EN1_NET` (`U1.DIM`), while `R5`/`R6` (`10 kΩ`) cleanly pull `EN1_NET`/`EN2_NET` to `0 V` in center `OFF` mode (`lm3410.pdf` prohibits floating `DIM`). *(Design check note: `BAV70LT1G` is verified **Common Cathode** per `datasheets/BAV70_onsemi.pdf`, correcting an earlier explorer note that mistakenly cited `BAW56`, which is Common Anode per `datasheets/BAW56_onsemi.pdf`.)*
- **Disabled-Channel Backfeed Immunity:** In `4-UV` mode, `U2` is shut down (`I_Q = 80 nA`), leaving `VOUT2` at `~4.8 V` via `L2 + D10`. Across 4 series `XP-E2` LEDs (`~10 V` turn-on knee), leakage is `< 50 nA` (zero visible glow).
- **Open-Load OVP (`D13`, `D14` = `BZT52C20-7-F`, `R8`, `R9` = `100 Ω`):** Wired strictly per **TI `lm3410.pdf` Figure 14 (p. 15)**: Zener `D13`/`D14` connects directly from `VOUT` to `FB_NET`, and `R8`/`R9` (`100 Ω`) sits **between `FB_NET` and `UV_RET`/`VIS_RET`** (above `R3`/`R4`). Normal `I_FB` (`0.1 µA`) causes only `10 µV` drop across `100 Ω`, while an open LED forces `~1.9–12 mA` through `D13 + R8`, cleanly clamping `VOUT` around `20.2–23.1 V < 24 V` max without exceeding `D13` (`500 mW`) or `U1` limits.

### 2.6 Emitter Mounting Trade-Off: Blank 20 mm Stars vs Custom JLCPCB Al MCPCB
- **Selected Emitters (`8× 3535 SMD`):** `4× Luminus SST-10-UV-A130-G365-00` (active, `A130` `3.25×3.25 mm` pad matching Cree XP-E2!) + `2× Cree XPEBRY-L1-0000-00R02` (Royal Blue) + `1× XPEBGR-L1-0000-00E01` (Green) + `1× XPEBWT-L1-0000-00F51` (Cool White).
- **Carrier Board Trade-Off:**
  - *8× Blank 20 mm Cu DTP Stars:* Lowest per-die $R_{\theta,\text{board}}$ (`~0.4 °C/W`), but requires mounting 8 discrete stars (16 screws/thermal pads) and hand-soldering 16 inter-star flying jumpers around a 4-sided core inside a `68 mm ID` tube (~£10–£14 UK delivered).
  - *4× Custom JLCPCB `1.0 W/m·K` Al MCPCB Dual-LED Strips (`~20 × 80 mm` panelized on `100 × 100 mm`):* Costs `~£12–£20` delivered to UK (5 panels = spares), gives larger heat-spreading area (`~1.5–2.5 °C/W` effective, $\Delta T_{J\text{-sink}} \approx 3.5^\circ\text{C}$ for `SST-10-UV` at `0.7 W` heat), reduces assembly to **4 strips / 8 screws**, and eliminates inter-LED jumper clutter.
  - **Decision:** Use **4× Custom JLCPCB `1.0 W/m·K` Al MCPCB dual-LED strips** (`MECH-MCPCB-1..4`), each carrying `1× UV` (`D1..D4`) + `1× Visible` (`D5..D8`), with standard 20 mm Cu DTP stars documented as an electrical-equivalent fallback.

---

## 3. Reproducing the M1 Environment & Simulations

Tools are provisioned strictly in user-space **outside** `/home/alimuldal/src/lepiled`:
- **`ngspice 45.2+ds-1`:** `/home/alimuldal/.local/share/lepiled-tools/bin/ngspice`
- **Python `3.14.4` venv:** `/home/alimuldal/.local/share/lepiled-venv` (`numpy`, `scipy`, `matplotlib`, `schemdraw`, `cairosvg`)

To regenerate the schematic and run the full dual-engine simulation suite from `/home/alimuldal/src/lepiled`:
```bash
/home/alimuldal/.local/share/lepiled-venv/bin/python circuit_design/generate_schematic.py
/home/alimuldal/.local/share/lepiled-venv/bin/python circuit_design/sim/run_simulations.py
```
