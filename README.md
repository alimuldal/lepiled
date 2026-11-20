<div align="center">

# LepiLED DIY Maxi Switch

**Open-source, fanless DIY moth lamp — `20 V` USB-C PD + dual buck drivers + `20 mm` Copper DTP LED stars**

*4× 365 nm UV-A · 2× 455 nm Royal Blue · 1× 528 nm Green · 1× 6200 K Cool White*

![Revision](https://img.shields.io/badge/Revision-4.5-blue?style=flat-square)
![Input](https://img.shields.io/badge/Power-20V%20USB--C%20PD-blueviolet?style=flat-square)
![Weight](https://img.shields.io/badge/Weight-~603g%20FDM-teal?style=flat-square)
![Shroud](https://img.shields.io/badge/Shroud-Extruded%20XT%20PMMA-informational?style=flat-square)
![KiCad](https://img.shields.io/badge/KiCad%209-0%20ERC%20%7C%200%20DRC-success?style=flat-square)
![BOM](https://img.shields.io/badge/1--Off%20UK%20BOM-%C2%A3110.09%20ex--VAT-orange?style=flat-square)

[Lamp Assembly](#whole-lamp-assembly) · [Driver PCB](#driver-pcb) · [Circuit Schematic](#circuit-schematic) · [Differences from Brehm (2017)](#differences-from-brehm-2017) · [Verification](#verification-summary) · [Build & BOM](#build--repository-map)

</div>

---

An open-source DIY implementation of Gunnar Brehm's *LepiLED* moth lamp ([Brehm, 2017, *Nota Lepidopterologica* 40(1): 87–108](https://doi.org/10.3897/nl.40.11887)), engineered for a compact, rugged, weatherproof, portable single-unit hobby build running straight off any `45 W+` USB-C PD laptop charger or `20 V` USB-C PD power bank. **Rev 4.5** cuts mass by **`-269 g`** (`~603 g` FDM) and height by **`-82 mm`** (`277.0 mm` tall) compared to Rev 4.4 while resolving every mechanical and weatherproofing issue from the independent review: a **compact stock `200 mm` bare `30 × 30 × 3 mm` aluminum core** (`174 g`, retaining the full `3 mm` wall for `M3` star threads, protruding `56.8 mm` with an unobstructed `Ø8 mm` hanging hole), a **shatter-resistant clear unstabilized extruded PMMA (`Plexiglas XT`) shroud** (`Ø60 × 54 × 3.0 × 115 mm`, `73 g`, `±2.0 mm` cut-length tolerant on **radial bore O-rings**), a **`25°` sloped conical `Ø88 mm` rain roof**, a **horizontal `driver_pcb` bolted via `H1..H4`** inside a **100% seamless lower shell**, a **permanently captured bottom USB-C PD cable through an `M20` IP68 split cable gland** beside the **bottom-mounted booted toggle switch**, plus an **IP68 ePTFE breather vent** and **`D12` PD-status lightpipe** (`£110.09` ex-VAT / `£132.11` inc-VAT complete 1-off UK build including captured USB-C cable, UV silicone wire, split gland, breather vent & oxime silicone; `£103.14` ex-VAT / `£123.77` inc-VAT with workshop screws & PC paste).

## Whole Lamp Assembly

<table>
  <tr>
    <td align="center" width="50%">
      <a href="mechanical_design/cad/assembly_iso.png">
        <img src="mechanical_design/cad/assembly_iso.png" alt="LepiLED Rev 4.5 3D Isometric Assembly" height="460" />
      </a>
      <br />
      <sub><b>3D Assembly (277.0 mm tall; ~603 g FDM)</b> — Clear extruded XT PMMA shroud (Ø60×54×115 mm), bare stock 200 mm 30×30×3 mm Al core protruding 56.8 mm with unobstructed Ø8 mm hang hole &amp; rain plug, unbroken 25° sloped conical Ø88 mm rain roof, seamless lower body, and protective standing ring.</sub>
    </td>
    <td align="center" width="50%">
      <a href="mechanical_design/cad/assembly_section_yz.png">
        <img src="mechanical_design/cad/assembly_section_yz.png" alt="LepiLED Rev 4.5 YZ Cross-Section" height="460" />
      </a>
      <br />
      <sub><b>YZ Cross-Section</b> — Radial O-ring shroud &amp; bottom-lid seals, 8× 20 mm Copper DTP stars bolted with M3 + nylon washers, horizontal <code>driver_pcb</code> (all 57 SMDs modeled) on bulkhead standoffs, compact 90° USB-C plug into bottom M20 IP68 split cable gland, and downward-pointing booted DPDT switch inside the base ring.</sub>
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
      <sub><b>Driver PCB — Bottom</b><br/>Unbroken <code>B.Cu</code> power-stage GND plane, isolated <code>H1..H4</code> NPTH holes bolting onto bulkhead standoffs via 4× M2.5×8 screws, mirrored pinout legends, and Emperor-moth back silkscreen.</sub>
    </td>
  </tr>
</table>

## Circuit Schematic

<p align="center">
  <a href="circuit_design/schematic.pdf">
    <img src="circuit_design/schematic.png" alt="LepiLED Rev 4.5 Complete Circuit Schematic" width="100%" />
  </a>
  <br />
  <sub>Click the schematic to open the full vector <a href="circuit_design/schematic.pdf">schematic.pdf</a> (KiCad 9.0.8, 0 ERC violations, 75 unique RefDes).</sub>
</p>

## Differences from Brehm (2017)

Reference paper: **Brehm, G. (2017).** *A new LED lamp for the collection of nocturnal Lepidoptera and a spectral comparison of light-trapping lamps.* **Nota Lepidopterologica**, 40(1), 87–108. [doi:10.3897/nl.40.11887](https://doi.org/10.3897/nl.40.11887)

This DIY build retains the paper's 8-LED insect-tuned spectrum (`4× UV-A`, `2× Royal Blue`, `1× Green`, `1× Cool White` at two vertical levels) and UV-transmitting acrylic (`PMMA`) cylinder while making four practical departures from the 2017 prototype:

- **Fanless compact monolithic cooling & sloped rain roof:** Replaces the internal axial fan and gauze vents with a sealed clear extruded `XT PMMA` cylinder (`Ø60 × 54 × 3.0 × 115 mm`) on low-force radial bore O-rings (`~30 N` push, `±2.5 mm` cut-length tolerant), a single stock `200 mm` `30 × 30 × 3 mm` bare aluminum core protruding `56.8 mm` out the top (unobstructed `Ø8 mm` hanging hole + rain plug), a `25°` sloped conical `Ø88 mm` rain roof, and an adhesive IP68 ePTFE breather vent preventing rain-quench fogging.
- **`20 V` USB-C PD + dual buck drivers + captured bottom cable:** Replaces the `5–12 V` boost source with a `20 V` USB-C PD sink (`AP33771C`) and two `AL8860WT-7` constant-current buck drivers (`333 mA` per channel, `93.8%` efficiency), fed by a permanently captured `90°` USB-C PD cable sealed watertight through a bottom `M20` IP68 split cable gland.
- **Protected bottom-mounted dual-mode switch (`OFF / 4-UV / 8-ALL`):** Splits the 8 LEDs into independent 4S UV-A and 4S Visible strings controlled by a booted gold-contact `DPDT` toggle mounted underneath `MECH-LID-BOT` inside a drained standing ring (`MECH-BASE-RING`).
- **Zero bare-SMD soldering & 6 support-free 3D prints:** Uses off-the-shelf pre-mounted `20 mm` Copper DTP LED stars (`R_sub ≈ 0.5 K/W`, bolted with `M3` screws + nylon washers), JLCPCB-assemblable `driver_pcb`, pre-crimped `22 AWG` JST-XH pigtails (passing straight through `9.0 × 7.5 mm` wire channels without de-pinning), `24 AWG` UV-stable silicone inter-star wire, and 6 watertight support-free FDM parts (with `MECH-PLUG-BOT` eliminated).

## Verification Summary

| Domain | Verification Suite | Result | Report / Source |
|---|---|---|---|
| **Circuit & SPICE** | 6 `ngspice` benches + `2,565` datasheet corners + `2,000`-trial Monte Carlo | **15/15 PASS** (`0` corner fails, `100.0%` MC yield, `0` UVLO chatter) | [sim_summary.json](circuit_design/sim/outputs/sim_summary.json) |
| **Driver PCB** | KiCad 9.0.8 real-pin ERC + DRC (`--schematic-parity --severity-all`) + copper audits | **0 ERC, 0 DRC, 0 parity, 0 via-in-pad, 0 `B.Cu` power slots** | [driver_pcb.kicad_pcb](pcb_design/driver_pcb/driver_pcb.kicad_pcb) |
| **Thermal (Rev 4.5)** | Coupled network: XT PMMA (`Ø60×54`) + `56.8 mm` bare `30×30×3` core + Cu DTP stars | **`22 °C` UK Night `T_j,UV = 69.1 °C`, `T_pcb = 55.9 °C`; `30 °C` Horiz Nom `T_j,UV = 77.1 °C`, `T_pcb = 63.9 °C` (`<= 75 °C` PETG)** | [thermal_summary.json](mechanical_design/thermal/thermal_summary.json) |
| **Mechanical CAD** | `37` param checks + `6` watertight FDM STLs + `75` kinematic sweeps + `156` B-Rep pairs (incl. all `57` SMDs!) | **ALL PASS** (`0/156` collisions Nom/WC `±2 mm`, `0.000–0.917 mm²` `>46°` overhangs, **`~603 g` FDM**, **`277 mm` tall**) | [cad_verification.json](mechanical_design/cad/cad_verification.json) |
| **UK 1-Off BOM** | 1:1 RefDes (`75`) / PCBA (`61`) / Harness (`4`) / PCB (`1`) / Mech (`18`) parity | **PASS** (`£110.09` ex-VAT / `£132.11` inc-VAT complete 1-off incl. cable, seals & vent; `£103.14` ex-VAT w/ owned screws & paste) | [bom.csv](bom/bom.csv) |

<details>
<summary><b>More Visuals — Thermal Margins, SPICE Waveforms &amp; 3D-Printed Parts</b></summary>
<br />
<p align="center">
  <img src="mechanical_design/thermal/thermal_margins.png" alt="Rev 4.5 Steady-State Thermal Margins across 22-35 C" width="96%" />
  <br />
  <sub>Coupled steady-state junction and PCB temperatures across 22 °C, 30 °C, and 35 °C ambient with Ø60×54 mm XT PMMA shroud, bare 30×30×3 mm protruding Al core, and 20 mm Copper DTP stars.</sub>
</p>
<table>
  <tr>
    <td align="center" width="50%">
      <img src="circuit_design/sim/outputs/plot_nominal_modes.png" alt="SPICE Nominal Operating Modes" width="100%" />
      <br />
      <sub><b>SPICE Modes</b> — Clean transitions across OFF, 4-UV, and 8-ALL at 333 mA.</sub>
    </td>
    <td align="center" width="50%">
      <img src="mechanical_design/cad/cap_top_detail.png" alt="3D-Printed Top End Cap with 25-deg Sloped Rain Roof" width="100%" />
      <br />
      <sub><b>Support-Free Top Cap</b> — Unbroken 25° sloped conical Ø88 mm rain roof with radial bore O-ring seal and sheltered M3 core locking screws (0.000 mm² overhang upright).</sub>
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
| **3D Print & Mechanical** | [MECHANICAL_DESIGN.md](mechanical_design/MECHANICAL_DESIGN.md) · [CLEARANCE_VERIFICATION.md](mechanical_design/CLEARANCE_VERIFICATION.md) · [mech_base_ring.step](mechanical_design/cad/mech_base_ring.step) · [mech_lid_bot.step](mechanical_design/cad/mech_lid_bot.step) · [mech_cap_bot.step](mechanical_design/cad/mech_cap_bot.step) · [mech_cap_top.step](mechanical_design/cad/mech_cap_top.step) · [mech_plug_top.step](mechanical_design/cad/mech_plug_top.step) · [mech_drill_jig.step](mechanical_design/cad/mech_drill_jig.step) · [lepiled_assembly.step](mechanical_design/cad/lepiled_assembly.step) |
| **Datasheets & BOM** | [bom.csv](bom/bom.csv) · [MECH_PARTS.csv](mechanical_design/MECH_PARTS.csv) · [datasheets_summary.md](datasheets/datasheets_summary.md) |
