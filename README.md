<div align="center">

# LepiLED DIY Maxi Switch

**Open-source, fanless DIY moth lamp powered by 20 V USB-C PD**

*4× 365 nm UV-A · 2× 455 nm Royal Blue · 1× 528 nm Green · 1× 6200 K Cool White*

![Revision](https://img.shields.io/badge/Revision-4.7-blue?style=flat-square)
![Input](https://img.shields.io/badge/Power-20V%20USB--C%20PD-blueviolet?style=flat-square)
![Weight](https://img.shields.io/badge/Weight-~521g-teal?style=flat-square)
![Shroud](https://img.shields.io/badge/Shroud-UV--Transmitting%20PMMA-informational?style=flat-square)
![KiCad](https://img.shields.io/badge/KiCad%209-0%20ERC%20%7C%200%20DRC-success?style=flat-square)
![BOM](https://img.shields.io/badge/1--Off%20UK%20BOM-%C2%A3105%20ex--VAT-orange?style=flat-square)

[Features](#key-features) · [Assembly](#whole-lamp-assembly) · [Driver PCB](#driver-pcb) · [Schematic](#circuit-schematic) · [Differences from Brehm (2017)](#differences-from-brehm-2017) · [Verification](#verification-summary) · [Build & Docs](#build--documentation)

</div>

---

An open-source DIY implementation of Gunnar Brehm's *LepiLED* moth lamp ([Brehm, 2017, *Nota Lepidopterologica* 40(1): 87–108](https://doi.org/10.3897/nl.40.11887)), designed for a compact, weatherproof single-unit build running from any 45 W+ USB-C PD laptop charger or 20 V USB-C PD power bank.

## Key Features

- **Insect-tuned 8-LED spectrum with dual modes:** Four 365 nm UV-A emitters and four visible emitters (Royal Blue, Green, Cool White) arranged on two vertical tiers around a four-sided aluminum core, switched between `OFF`, `4-UV`, and `8-ALL` via a booted toggle recessed in the base.
- **High-efficiency 20 V USB-C PD power:** Negotiates 20 V over USB-C PD and drives each 4-LED string with an independent 333 mA constant-current buck converter (`~94%` efficiency, `~0.5 W` driver loss). Hardware undervoltage lockout keeps the LEDs off on legacy 5–15 V USB sources, and a side-visible red indicator confirms 20 V PD negotiation.
- **Fanless, weatherproof lantern enclosure:** Completely sealed against dew and rain with silicone O-rings, an interior waterproof breather vent, a sloped rain roof, and a permanently captured right-angle USB-C cable secured by a 2-piece split clamp. A matte-black aluminum cooling core doubles as the hanging point and keeps LED junctions cool in still night air (`~521 g`, `266.5 mm` tall).
- **Hobby-friendly build:** Uses a single custom 2-layer driver PCB (ready for budget JLCPCB assembly with only 2 extended parts), pre-mounted 20 mm copper LED stars (no bare-LED reflow soldering), pre-crimped wire harnesses, brass heat-set inserts, and 8 support-free 3D-printed ASA parts.

## Whole Lamp Assembly

<table>
  <tr>
    <td align="center" width="50%">
      <a href="mechanical_design/cad/assembly_iso.png">
        <img src="mechanical_design/cad/assembly_iso.png" alt="LepiLED 3D Isometric Assembly" height="460" />
      </a>
      <br />
      <sub><b>3D Assembly (266.5 mm tall, ~521 g)</b> — Tapered matte-black ASA base with recessed bottom lid and cable portals, clear UV-transmitting acrylic shroud over 8 copper LED stars, sloped rain roof, matte-black aluminum cooling chimney, finial cap, and orange hanging-hole bushing.</sub>
    </td>
    <td align="center" width="50%">
      <a href="mechanical_design/cad/assembly_section_yz.png">
        <img src="mechanical_design/cad/assembly_section_yz.png" alt="LepiLED YZ Cross-Section" height="460" />
      </a>
      <br />
      <sub><b>YZ Cross-Section</b> — Internal dry-bay core anchor, radial shroud and lid O-rings, horizontal driver PCB mounted on brass-insert standoffs, captured right-angle USB-C cable with split clamp, and recessed booted mode switch.</sub>
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
      <sub><b>Driver PCB — Top (36 × 46 mm, 2-layer FR4)</b><br/>20 V USB-C PD sink controller, hysteretic undervoltage lockout, and dual 333 mA constant-current buck drivers.</sub>
    </td>
    <td align="center" width="50%">
      <a href="pcb_design/driver_pcb/renders/render_bottom.png">
        <img src="pcb_design/driver_pcb/renders/render_bottom.png" alt="Driver PCB Bottom 3D Render" height="360" />
      </a>
      <br />
      <sub><b>Driver PCB — Bottom</b><br/>Solid ground plane under the switching stage, isolated mounting holes, connector pinout legends, and Emperor-moth silkscreen.</sub>
    </td>
  </tr>
</table>

## Circuit Schematic

<p align="center">
  <a href="circuit_design/schematic.pdf">
    <img src="circuit_design/schematic.png" alt="LepiLED Complete Circuit Schematic" width="100%" />
  </a>
  <br />
  <sub>Click to open the full vector <a href="circuit_design/schematic.pdf">schematic.pdf</a> (KiCad 9, 0 ERC violations).</sub>
</p>

## Differences from Brehm (2017)

Reference paper: **Brehm, G. (2017).** *A new LED lamp for the collection of nocturnal Lepidoptera and a spectral comparison of light-trapping lamps.* **Nota Lepidopterologica**, 40(1), 87–108. [doi:10.3897/nl.40.11887](https://doi.org/10.3897/nl.40.11887)

This build retains the paper's 8-LED spectrum (`4× UV-A`, `2× Royal Blue`, `1× Green`, `1× Cool White` on two tiers) and UV-transmitting acrylic shroud while making four practical changes for DIY builders:

- **Fanless passive cooling:** Replaces the internal cooling fan and mesh vents with a sealed acrylic cylinder and an exposed matte-black aluminum square tube core, paired with a sloped rain roof and an interior waterproof breather vent.
- **20 V USB-C PD buck electronics:** Replaces the low-voltage boost converter with a 20 V USB-C PD sink and two 333 mA buck drivers, running directly from standard USB-C PD chargers or power banks at ~94% efficiency.
- **Recessed dual-mode switch:** Splits the UV and visible LEDs onto independent channels selected via a weatherproof bottom-mounted toggle (`OFF / 4-UV / 8-ALL`), with tactile ribs on the base skirt and a status lightpipe for finding settings in the dark.
- **Accessible DIY construction:** Uses pre-mounted 20 mm copper LED stars, a single custom PCB designed for low-cost turnkey assembly, pre-crimped wire pigtails, and support-free 3D-printed parts.

## Verification Summary

| Domain | Scope | Result | Source |
|---|---|---|---|
| **Circuit & SPICE** | 6 `ngspice` benches, 2,565 datasheet corners, 2,000-trial Monte Carlo | **15/15 PASS** (0 corner failures, 100% MC yield, 94.2% efficiency) | [sim_summary.json](circuit_design/sim/outputs/sim_summary.json) |
| **Driver PCB** | KiCad 9 ERC, DRC with schematic parity, and copper/silkscreen checks | **0 ERC, 0 DRC, 0 parity issues, 0 via-in-pad** | [driver_pcb.kicad_pcb](pcb_design/driver_pcb/driver_pcb.kicad_pcb) |
| **Thermal** | Coupled steady-state thermal model in still air (`22–35 °C`) | **All modes PASS** (`T_j,UV = 55.8 °C` at `22 °C`; `63.0–71.6 °C` at `30 °C`) | [thermal_summary.json](mechanical_design/thermal/thermal_summary.json) |
| **Mechanical CAD** | Parameter checks, watertight STLs, overhang checks, kinematic & B-Rep collision checks | **All PASS** (0 collisions, 0 unsupported overhangs, `~521 g`, `266.5 mm` tall) | [cad_verification.json](mechanical_design/cad/cad_verification.json) |
| **Master BOM** | 1:1 parity across schematic, PCB, hybrid PCBA, harness, and mechanical parts | **PASS** (`£105.28` ex-VAT all new; `£93.43` ex-VAT using workshop screws/paste/paint) | [bom.csv](bom/bom.csv) |

<details>
<summary><b>Additional Visuals — Thermal Plot, SPICE Waveforms &amp; 3D-Printed Top Cap</b></summary>
<br />
<p align="center">
  <img src="mechanical_design/thermal/thermal_network_comparison.png" alt="Aluminum Core Surface Finish Thermal Comparison" width="96%" />
  <br />
  <sub>Steady-state UV junction temperatures at 30 °C still air (horizontal): spraying the aluminum core matte black (with LED mounting pads masked) lowers UV junction temperature by 13–16 °C compared to bare aluminum.</sub>
</p>
<table>
  <tr>
    <td align="center" width="50%">
      <img src="circuit_design/sim/outputs/plot_nominal_modes.png" alt="SPICE Nominal Operating Modes" width="100%" />
      <br />
      <sub><b>SPICE Modes</b> — Clean transitions across OFF, 4-UV, and 8-ALL at 333 mA per string.</sub>
    </td>
    <td align="center" width="50%">
      <img src="mechanical_design/cad/cap_top_detail.png" alt="3D-Printed Top End Cap" width="100%" />
      <br />
      <sub><b>Support-Free Top Cap</b> — Sloped circular rain eaves lofted to a rounded-square chimney collar with a silicone sealing groove.</sub>
    </td>
  </tr>
</table>
</details>

## Build & Documentation

| Area | Key Files |
|---|---|
| **Build Guides & BOM** | [ASSEMBLY_GUIDE.md](docs/ASSEMBLY_GUIDE.md) · [BOM.md](bom/BOM.md) · [BLOCKERS.md](docs/BLOCKERS.md) *(pre-order checklist)* · [DESIGN_DECISIONS.md](docs/DESIGN_DECISIONS.md) *(full revision history)* |
| **Electronics & SPICE** | [schematic.pdf](circuit_design/schematic.pdf) · [ELECTRONICS_ARCHITECTURE.md](docs/ELECTRONICS_ARCHITECTURE.md) · [COMPONENT_IDS.csv](circuit_design/COMPONENT_IDS.csv) · [INTERFACE_CONTRACT.md](circuit_design/INTERFACE_CONTRACT.md) · [run_simulations.py](circuit_design/sim/run_simulations.py) |
| **Driver PCB & PCBA** | [PCB_SUMMARY.md](pcb_design/PCB_SUMMARY.md) · [driver_pcb_gerbers.zip](pcb_design/gerbers/driver_pcb/driver_pcb_gerbers.zip) · [assembly_map.pdf](pcb_design/driver_pcb/renders/assembly_map.pdf) · Hybrid PCBA: [driver_pcb_bom_pcba_hybrid.csv](pcb_design/driver_pcb_bom_pcba_hybrid.csv) + [driver_pcb_cpl_hybrid.csv](pcb_design/driver_pcb_cpl_hybrid.csv) + [driver_pcb_diy_hand_solder.csv](pcb_design/driver_pcb_diy_hand_solder.csv) · Full BOM/CPL: [driver_pcb_bom_pcba.csv](pcb_design/driver_pcb_bom_pcba.csv) + [driver_pcb_cpl.csv](pcb_design/driver_pcb_cpl.csv) |
| **3D Print & Mechanical** | [MECHANICAL_DESIGN.md](mechanical_design/MECHANICAL_DESIGN.md) · [CLEARANCE_VERIFICATION.md](mechanical_design/CLEARANCE_VERIFICATION.md) · [mech_cap_bot.step](mechanical_design/cad/mech_cap_bot.step) · [mech_lid_bot.step](mechanical_design/cad/mech_lid_bot.step) · [mech_cable_clamp.step](mechanical_design/cad/mech_cable_clamp.step) · [mech_core_anchor.step](mechanical_design/cad/mech_core_anchor.step) · [mech_cap_top.step](mechanical_design/cad/mech_cap_top.step) · [mech_plug_top.step](mechanical_design/cad/mech_plug_top.step) · [mech_hang_bushing.step](mechanical_design/cad/mech_hang_bushing.step) · [mech_drill_jig.step](mechanical_design/cad/mech_drill_jig.step) · [lepiled_assembly.step](mechanical_design/cad/lepiled_assembly.step) |
| **Parts Data & Datasheets** | [bom.csv](bom/bom.csv) · [MECH_PARTS.csv](mechanical_design/MECH_PARTS.csv) · [datasheets_summary.md](datasheets/datasheets_summary.md) |
