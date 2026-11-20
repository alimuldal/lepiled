<div align="center">

# LepiLED DIY Maxi Switch

**Open-source, fanless DIY moth lamp — `20 V` USB-C PD + dual buck drivers + `20 mm` Copper DTP LED stars**

*4× 365 nm UV-A · 2× 455 nm Royal Blue · 1× 528 nm Green · 1× 6200 K Cool White*

![Revision](https://img.shields.io/badge/Revision-4.2-blue?style=flat-square)
![Input](https://img.shields.io/badge/Power-20V%20USB--C%20PD-blueviolet?style=flat-square)
![Efficiency](https://img.shields.io/badge/Efficiency-93.8%25-brightgreen?style=flat-square)
![Machining](https://img.shields.io/badge/Metal%20Parts-1%20Stock%20Al%20Tube-teal?style=flat-square)
![KiCad](https://img.shields.io/badge/KiCad%209-0%20ERC%20%7C%200%20DRC-success?style=flat-square)
![BOM](https://img.shields.io/badge/1--Off%20UK%20BOM-%C2%A393.24%20ex--VAT-orange?style=flat-square)

[Lamp Assembly](#whole-lamp-assembly) · [Driver PCB](#driver-pcb) · [Circuit Schematic](#circuit-schematic) · [Differences from Brehm (2017)](#differences-from-brehm-2017) · [Verification](#verification-summary) · [Build & BOM](#build--repository-map)

</div>

---

An open-source DIY implementation of Gunnar Brehm's *LepiLED* moth lamp ([Brehm, 2017, *Nota Lepidopterologica* 40(1): 87–108](https://doi.org/10.3897/nl.40.11887)), engineered for a single-unit hobby build straight off any `45 W+` USB-C PD laptop charger or `20 V` USB-C PD power bank. Rev 4.2 uses **pre-mounted `20 mm` Copper DTP LED stars** (eliminating bare-LED reflow and the second custom PCB), a **single stock `250 mm` length of bare `40 × 40 × 3 mm` aluminum tube** protruding out the top as a monolithic fanless heatsink and hanging point, **zero brass heat-set inserts**, and a single JLCPCB-assemblable `driver_pcb`—bringing the complete **1-off UK build down to `£93.24` ex-VAT (`£111.89` inc-VAT; `£104.27` inc-VAT with workshop `M3` hardware & PC thermal paste)**.

## Whole Lamp Assembly

<table>
  <tr>
    <td align="center" width="50%">
      <a href="mechanical_design/cad/assembly_iso.png">
        <img src="mechanical_design/cad/assembly_iso.png" alt="LepiLED Rev 4.2 3D Isometric Assembly" height="460" />
      </a>
      <br />
      <sub><b>3D Assembly (324 mm tall)</b> — Borosilicate 3.3 cylinder, bare stock 250 mm 40×40×3 mm Al core protruding 85.5 mm out the top (drilled Ø8 mm hanging hole + printed rain plug), 8× 20 mm Copper DTP LED stars, 20 mm USB-C rubber grommet, and booted DPDT toggle.</sub>
    </td>
    <td align="center" width="50%">
      <a href="mechanical_design/cad/assembly_section_yz.png">
        <img src="mechanical_design/cad/assembly_section_yz.png" alt="LepiLED Rev 4.2 YZ Cross-Section" height="460" />
      </a>
      <br />
      <sub><b>YZ Cross-Section</b> — Press-fit rain plug & Ø8 mm hanging hole, 6.0 mm thermal bulkhead, printed bottom core plug, integral bottom-lid PCB locating pins (zero inserts), and direct-mate USB-C tunnel.</sub>
    </td>
  </tr>
</table>

## Driver PCB

<table>
  <tr>
    <td align="center" width="50%">
      <a href="pcb_design/driver_pcb/renders/render_top.png">
        <img src="pcb_design/driver_pcb/renders/render_top.png" alt="Driver PCB Top 3D Render" height="360" />
      </a>
      <br />
      <sub><b>Driver PCB — Top (36 × 46 mm, 2L FR4 ENIG, JLCPCB Basic-Optimized PCBA)</b><br/>AP33771C 20 V PD sink, 40 V DMN4035L load switch, hysteretic LM393B UVLO, dual AL8860WT-7 333 mA bucks.</sub>
    </td>
    <td align="center" width="50%">
      <a href="pcb_design/driver_pcb/renders/render_bottom.png">
        <img src="pcb_design/driver_pcb/renders/render_bottom.png" alt="Driver PCB Bottom 3D Render" height="360" />
      </a>
      <br />
      <sub><b>Driver PCB — Bottom</b><br/>Unbroken <code>B.Cu</code> power-stage GND plane, isolated NPTH holes dropping onto printed bottom-lid locating pins, mirrored pinout legends.</sub>
    </td>
  </tr>
</table>

## Circuit Schematic

<p align="center">
  <a href="circuit_design/schematic.pdf">
    <img src="circuit_design/schematic.png" alt="LepiLED Rev 4.2 Complete Circuit Schematic" width="100%" />
  </a>
  <br />
  <sub>Click the schematic to open the full vector <a href="circuit_design/schematic.pdf">schematic.pdf</a> (KiCad 9.0.8, 0 ERC violations, 75 unique RefDes).</sub>
</p>

## Differences from Brehm (2017)

Reference paper: **Brehm, G. (2017).** *A new LED lamp for the collection of nocturnal Lepidoptera and a spectral comparison of light-trapping lamps.* **Nota Lepidopterologica**, 40(1), 87–108. [doi:10.3897/nl.40.11887](https://doi.org/10.3897/nl.40.11887)

This DIY build retains the paper's 8-LED insect-tuned spectrum (`4× UV-A`, `2× Royal Blue`, `1× Green`, `1× Cool White` at two vertical levels) while making four practical departures from the 2017 prototype:

- **Fanless monolithic cooling:** Replaces the internal axial fan and gauze vents with a sealed borosilicate 3.3 cylinder and a single stock `250 mm` `40 × 40 × 3 mm` bare aluminum tube protruding `85.5 mm` out the top (capped by a 3D-printed rain plug with a drilled `Ø8 mm` hanging hole).
- **`20 V` USB-C PD + dual buck drivers:** Replaces the `5–12 V` boost constant-current source with a `20 V` USB-C PD sink (`AP33771C`) and two `AL8860WT-7` constant-current buck drivers (`333 mA` per channel, `93.8%` efficiency), running straight off standard laptop chargers or `20 V` PD power banks.
- **Dual-mode switching (`OFF / 4-UV / 8-ALL`):** Splits the 8 LEDs into independent 4S UV-A and 4S Visible strings controlled by a sealed gold-contact `DPDT` toggle (matching Brehm's later *Maxi Switch* functionality, vs. single-mode operation in the 2017 prototype).
- **Zero bare-SMD soldering & single-fastener DIY build:** Uses off-the-shelf pre-mounted `20 mm` Copper DTP LED stars (`R_sub ≈ 0.5 K/W`), JLCPCB-assemblable `driver_pcb`, pre-crimped `22 AWG` JST-XH pigtails, support-free 3D-printed caps/plugs/drill-jig with captive `M3` hex-nut pockets, and `M3` as the sole fastener size across the entire lamp.

## Verification Summary

| Domain | Verification Suite | Result | Report / Source |
|---|---|---|---|
| **Circuit & SPICE** | 6 `ngspice` benches + `2,565` datasheet corners + `2,000`-trial Monte Carlo | **15/15 PASS** (`0` corner fails, `100.0%` MC yield, `0` UVLO chatter) | [sim_summary.json](circuit_design/sim/outputs/sim_summary.json) |
| **Driver PCB** | KiCad 9.0.8 real-pin ERC + DRC (`--schematic-parity --severity-all`) + copper audits | **0 ERC, 0 DRC, 0 parity, 0 via-in-pad, 0 `B.Cu` power slots** | [driver_pcb.kicad_pcb](pcb_design/driver_pcb/driver_pcb.kicad_pcb) |
| **Thermal (Rev 4.2)** | Coupled network: `85.5 mm` bare Al tube + `20 mm` Cu DTP stars + sealed lid (`75 °C` PETG) | **16/16 Real-WPE PASS** (`22–30 °C`) + **4/4 Real-WPE PASS** (`35 °C`) + **10/10** (`22 °C`) | [thermal_summary.json](mechanical_design/thermal/thermal_summary.json) |
| **Mechanical CAD** | `36` param checks + `6` watertight FDM STLs + `3,249`-ray flange check + `156` B-Rep pairs | **ALL PASS** (`0/156` collisions Nom/WC, `0.000–0.387 mm²` `>46°` overhangs) | [cad_verification.json](mechanical_design/cad/cad_verification.json) |
| **UK 1-Off BOM** | 1:1 RefDes (`75`) / PCBA (`61`) / Pigtails (`2`) / PCB (`1`) / Mech (`14`) parity | **PASS** (`£93.24` ex-VAT / `£111.89` inc-VAT 1-off; `£104.27` w/ owned M3 & paste) | [bom.csv](bom/bom.csv) |

<details>
<summary><b>More Visuals — Thermal Margins, SPICE Waveforms &amp; 3D-Printed Parts</b></summary>
<br />
<p align="center">
  <img src="mechanical_design/thermal/thermal_margins.png" alt="Rev 4.2 Steady-State Thermal Margins across 22-35 C" width="96%" />
  <br />
  <sub>Coupled steady-state junction and PCB temperatures across 22 °C, 30 °C, and 35 °C ambient on the bare protruding Al core + 20 mm Copper DTP stars.</sub>
</p>
<table>
  <tr>
    <td align="center" width="50%">
      <img src="circuit_design/sim/outputs/plot_nominal_modes.png" alt="SPICE Nominal Operating Modes" width="100%" />
      <br />
      <sub><b>SPICE Modes</b> — Clean transitions across OFF, 4-UV, and 8-ALL at 333 mA.</sub>
    </td>
    <td align="center" width="50%">
      <img src="mechanical_design/cad/cap_bot_detail.png" alt="3D-Printed Bottom End Cap Detail" width="100%" />
      <br />
      <sub><b>Support-Free Bottom Cap</b> — Captive M3 nut slots, 20 mm rubber grommet flange &amp; DPDT switch alcove.</sub>
    </td>
  </tr>
</table>
</details>

## Build & Repository Map

| Area | Key Files |
|---|---|
| **Start Here** | [ASSEMBLY_GUIDE.md](docs/ASSEMBLY_GUIDE.md) · [BOM.md](bom/BOM.md) · [DESIGN_DECISIONS.md](docs/DESIGN_DECISIONS.md) · [BLOCKERS.md](docs/BLOCKERS.md) |
| **Electronics & SPICE** | [schematic.pdf](circuit_design/schematic.pdf) · [ELECTRONICS_ARCHITECTURE.md](docs/ELECTRONICS_ARCHITECTURE.md) · [COMPONENT_IDS.csv](circuit_design/COMPONENT_IDS.csv) · [INTERFACE_CONTRACT.md](circuit_design/INTERFACE_CONTRACT.md) · [run_simulations.py](circuit_design/sim/run_simulations.py) |
| **Driver PCB & PCBA** | [PCB_SUMMARY.md](pcb_design/PCB_SUMMARY.md) · [driver_pcb_gerbers.zip](pcb_design/gerbers/driver_pcb/driver_pcb_gerbers.zip) · [assembly_map.pdf](pcb_design/driver_pcb/renders/assembly_map.pdf) · [driver_pcb_bom_pcba.csv](pcb_design/driver_pcb_bom_pcba.csv) · [driver_pcb_cpl.csv](pcb_design/driver_pcb_cpl.csv) |
| **3D Print & Mechanical** | [MECHANICAL_DESIGN.md](mechanical_design/MECHANICAL_DESIGN.md) · [CLEARANCE_VERIFICATION.md](mechanical_design/CLEARANCE_VERIFICATION.md) · [mech_lid_bot.step](mechanical_design/cad/mech_lid_bot.step) · [mech_cap_bot.step](mechanical_design/cad/mech_cap_bot.step) · [mech_cap_top.step](mechanical_design/cad/mech_cap_top.step) · [mech_plug_top.step](mechanical_design/cad/mech_plug_top.step) · [mech_plug_bot.step](mechanical_design/cad/mech_plug_bot.step) · [mech_drill_jig.step](mechanical_design/cad/mech_drill_jig.step) · [lepiled_assembly.step](mechanical_design/cad/lepiled_assembly.step) |
| **Datasheets & BOM** | [bom.csv](bom/bom.csv) · [MECH_PARTS.csv](mechanical_design/MECH_PARTS.csv) · [datasheets_summary.md](datasheets/datasheets_summary.md) |
