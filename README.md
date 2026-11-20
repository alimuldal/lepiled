<div align="center">

# LepiLED DIY Maxi Switch

**Open-source, fanless DIY moth lamp powered by 20 V USB-C PD**

*4× 365 nm UV-A · 2× 455 nm Royal Blue · 1× Pure Green · 1× 6500 K Cool White*

![Revision](https://img.shields.io/badge/Revision-4.9-blue?style=flat-square)
![Input](https://img.shields.io/badge/Power-20V%20USB--C%20PD-blueviolet?style=flat-square)
![Weight](https://img.shields.io/badge/Weight-~572g%20ASA%20%7C%20~613g%20PETG-teal?style=flat-square)
![Shroud](https://img.shields.io/badge/Shroud-Extruded%20XT%20PMMA-informational?style=flat-square)
![KiCad](https://img.shields.io/badge/KiCad%2010-0%20ERC%20%7C%200%20DRC%20%7C%20HASL-success?style=flat-square)
![BOM](https://img.shields.io/badge/1--Off%20UK%20Parts-%C2%A3101%20ex--VAT%20(%C2%A387%20Net)-orange?style=flat-square)

[Features](#key-features) · [Assembly](#whole-lamp-assembly) · [Driver PCB](#driver-pcb) · [Schematic](#circuit-schematic) · [Differences from Brehm (2017)](#differences-from-brehm-2017) · [Verification](#verification-summary) · [Build & Docs](#build--documentation)

</div>

---

An open-source DIY implementation of Gunnar Brehm's *LepiLED* moth lamp ([Brehm, 2017, *Nota Lepidopterologica* 40(1): 87–108](https://doi.org/10.3897/nl.40.11887)), value-engineered for an affordable (`~£121–£125` inc-VAT UK delivered using standard workshop `M3` hardware & thermal paste), weatherproof single-unit hobby build running from any 45 W+ USB-C PD laptop charger or 20 V USB-C PD power bank.

## Key Features

- **Insect-tuned 8-LED spectrum from ONE vendor (`Convoylight.com`):** Four `Luminus SST-10-UV 365 nm` UV-A emitters and four `ams OSRAM CSLNM1` visible emitters (`2× KB CSLNM1.14` 455 nm Royal Blue on opposite `±X` faces, `1× KP CSLNM1.F1` Pure Green, `1× KW CSLNM1.TG` 6500 K Cool White) all pre-mounted on `20 mm` Copper DTP stars with electrically neutral thermal pads, switched between `OFF`, `4-UV`, and `8-ALL` via a recessed gold-contact booted toggle (`C&K 7211SYZBE`).
- **Value-engineered 2-Reel Hybrid Lead-Free HASL PCBA (`~£15 ex-VAT`):** Single 2-layer `driver_pcb` (`36 × 46 mm`) where JLCPCB machine-reflows **`41` SMDs** (`20` Basic + **only `2` Extended reels**: `U1/U2` `AL8860WT-7` & `U3` `WCH CH224A`), leaving only `4` THT connectors (`J1..J4`) and `7` chunky 2-pad SMDs (`F1` `1206` Littelfuse `046801.5NRHF` `1.5 A / 63 V` Slo-Blo, `D11` `SMB` `SMBJ22A`, `L1/L2` `6045` `Bourns SRN6045-680M`, `R3/R4` `1206` `0.30 Ω`, `R7` `2512 1 W` pulse damper) consolidated in ONE Farnell UK order alongside `SW1`. Achieves `94.1%` efficiency (`0.508 W` PCB loss), `0.83 V` hysteretic UVLO (`LM393` + `TL431` with damped `R24/C16` ESD bypass), bare HASL bench test pads (`TP1..TP4`), and diagnostic LED `D12`.
- **Serviceable, weatherproof fanless lantern with unified `M3` CSK hardware:** `driver_pcb` mounts **SMD/JST-side UP** on four integral `M3` brass-insert standoffs rising from `MECH-LID-BOT` (`8.5 mm` thick), allowing open-air USB-C/JST mating and bench testing before sliding straight up into the `Ø71.6 mm` dry bay in one stroke. The **entire lamp** uses **one single thread size (`M3`)**: `14×` identical standard `M3 × 5.0 × 4.2 mm` brass inserts, `32×` workshop `M3` countersunk (`CSK`) screws (with `90°` flush countersinks on lid/clamp/anchor and steel + `Ø7.0 mm` DIN 125 nylon washer stacks on the stars & PCB), unpainted bare mill aluminum core (`£0` paint, zero UV outgassing), radial silicone O-rings, interior recessed IP68 ePTFE breather vent, blind-bolted conical split cable clamp, unbroken rain eaves + `9.5 mm` vertical collar (`0` roof holes), local click-and-collect `Soudal Fix ALL Crystal` (`£0` ship), and a removable DIY coat-hanger wire hanging bail (`277.0 mm` body / `318.3 mm` w/ bail, `~572 g` ASA / `~613 g` PETG).
- **Workshop-friendly & mistake-proofed:** Prints support-free on standard workshop **PETG or ASA** printers (`31.1 mm` core clearance, `0` supports), uses pre-crimped JST-XH pigtails, and enforces full SSOT cross-domain verification via `python3 verify_all.py --check`.

## Whole Lamp Assembly

<table>
  <tr>
    <td align="center" width="50%">
      <a href="mechanical_design/cad/assembly_iso.png">
        <img src="mechanical_design/cad/assembly_iso.png" alt="LepiLED 3D Isometric Assembly" height="460" />
      </a>
      <br />
      <sub><b>3D Assembly (277.0 mm body / 318.3 mm w/ wire bail; ~572 g ASA / ~613 g PETG)</b> — Tapered PETG/ASA base (Ø94.4 mm) with 22 mm protective skirt, extruded clear XT PMMA shroud over 8 Convoy Cu DTP stars, sloped rain roof + 9.5 mm vertical collar (0 roof holes), unpainted bare mill Al core, finial cap, snap-fit orange pivot bushings, and removable DIY coat-hanger C-clip wire bail.</sub>
    </td>
    <td align="center" width="50%">
      <a href="mechanical_design/cad/assembly_section_yz.png">
        <img src="mechanical_design/cad/assembly_section_yz.png" alt="LepiLED YZ Cross-Section" height="460" />
      </a>
      <br />
      <sub><b>YZ Cross-Section</b> — Staggered internal core anchor (±Y flush M3 CSK bolts / ±X CSK cross-pins), radial shroud &amp; lid O-rings, serviceable lid-mounted PCB (SMD-side UP on M3 standoffs), 15 mm 90° USB-C plug + blind-bolted conical split clamp (flush M3 CSK), and recessed real 18.6 mm SW1 toggle boot.</sub>
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
      <sub><b>Driver PCB — Top (36 × 46 mm, 2-layer FR4, Lead-Free HASL)</b><br/>2-Reel Hybrid JLCPCB PCBA (41 SMDs: 20 Basic + U1/U2, U3) + 11 Farnell UK DIY parts (4 THT headers + 7 chunky 2-pad SMDs: F1, D11, L1/L2, R3/R4, R7) + TP1..TP4 bench pads.</sub>
    </td>
    <td align="center" width="50%">
      <a href="pcb_design/driver_pcb/renders/render_bottom.png">
        <img src="pcb_design/driver_pcb/renders/render_bottom.png" alt="Driver PCB Bottom 3D Render" height="360" />
      </a>
      <br />
      <sub><b>Driver PCB — Bottom</b><br/>Solid ground plane under the switching stage, Gerber-verified Ø6.2 mm M3 NPTH copper keepouts around H1..H4 (F.Cu &gt;= 3.61 mm clearing Ø7 nylon washers!), connector pinout legends, and Emperor-moth silkscreen.</sub>
    </td>
  </tr>
</table>

## Circuit Schematic

<p align="center">
  <a href="circuit_design/schematic.pdf">
    <img src="circuit_design/schematic.png" alt="LepiLED Complete Circuit Schematic" width="100%" />
  </a>
  <br />
  <sub>Click to open the full vector <a href="circuit_design/schematic.pdf">schematic.pdf</a> (KiCad 10, 0 ERC violations).</sub>
</p>

## Differences from Brehm (2017)

Reference paper: **Brehm, G. (2017).** *A new LED lamp for the collection of nocturnal Lepidoptera and a spectral comparison of light-trapping lamps.* **Nota Lepidopterologica**, 40(1), 87–108. [doi:10.3897/nl.40.11887](https://doi.org/10.3897/nl.40.11887)

This build retains the paper's 8-LED spectrum (`4× UV-A`, `2× Royal Blue`, `1× Green`, `1× Cool White` on two tiers) and UV-transmitting extruded clear XT PMMA shroud while making four practical changes for DIY builders:

- **Fanless passive cooling:** Replaces the internal cooling fan and mesh vents with a sealed acrylic cylinder and an exposed unpainted bare mill aluminum square tube core (`58.5 mm` protruding chimney), paired with a sloped rain roof and an interior recessed IP68 ePTFE breather vent.
- **20 V USB-C PD buck electronics:** Replaces the low-voltage boost converter with a `CH224A` 20 V USB-C PD sink and two `AL8860WT-7` `333 mA` buck drivers (`94.1%` efficiency, `0.508 W` driver loss).
- **Recessed dual-mode switch:** Splits UV and visible LEDs onto independent channels selected via a weatherproof bottom-mounted gold-contact toggle (`OFF / 4-UV / 8-ALL`) with tactile `0 / 1 / 2` ribs on the base skirt.
- **Value-engineered DIY construction:** Uses single-vendor `Convoylight.com` `20 mm` Copper DTP LED stars, a Lead-Free HASL 2-Reel Hybrid PCB (`41` machine-reflowed SMDs + `11` chunky hand-soldered parts), unified workshop `M3` CSK fasteners & `M3×5.0` brass inserts, pre-crimped JST-XH wire pigtails, open-air lid-mounted PCB serviceability, and support-free PETG/ASA 3D-printed parts.

## Verification Summary

Run `python3 verify_all.py --check` at any time to verify all gates, SHA-256 freshness hashes, and doc parity:

| Domain | Scope | Result | Source |
|---|---|---|---|
| **Circuit & SPICE** | 6 `libngspice` benches (real TVS `TBV1`, `F1` `I²t`, `2512 R7` pulse), 2,565 corners, 2,000-trial MC | **16/16 PASS** (`0` corner failures, `100%` MC yield, `94.1%` eff, `107×` `F1` `I²t` margin) | [sim_summary.json](circuit_design/sim/outputs/sim_summary.json) |
| **Driver PCB & Gerbers** | KiCad 10 ERC, DRC (`--refill-zones --schematic-parity --severity-all`), RS-274X Gerber M3 NPTH/DNP audit | **0 ERC, 0 DRC, 0 parity, 0 via-in-pad, 0 M3 NPTH copper (`F_Cu >= 3.61 mm`) / 0 DNP paste** | [driver_pcb.kicad_pcb](pcb_design/driver_pcb/driver_pcb.kicad_pcb) |
| **Thermal (SSOT-Coupled)** | Unpainted bare mill Al core (`ε=0.20`, `58.5 mm` chimney, `F_amb=0.881`, `14%` optical re-abs., Osram `CSLNM1`) | **16/16 UK-Night (`<=22 °C` Real-WPE PETG) · 18/18 `15–30 °C` Nom (PETG) · 24/24 `15–30 °C` Real-WPE (ASA+Comm IC)** | [thermal_summary.json](mechanical_design/thermal/thermal_summary.json) |
| **Mechanical CAD** | 49 param checks, 8 watertight STLs, overhangs, **3 ray-cast breach gates**, 80 kinematic & 240 B-Rep pairs (incl. DIY wire bail, 14 unified `M3×5` inserts & 32 `M3` CSK screws) | **All PASS** (`0` collisions, `0` roof/wall breaches, `0` unsupported overhangs, `277.0 mm` body) | [cad_verification.json](mechanical_design/cad/cad_verification.json) |
| **Master BOM & Docs** | 1:1 parity across `72` RefDes, `54` PCBA (`41` JLC + `11` DIY + `2` DNP), `20` `MECH-*`, all `Datasheet_Ref` files, SSOT drill coordinates | **PASS** (`£100.60` ex-VAT / `£120.72` inc-VAT all-new; **`£87.02` ex-VAT / `£104.42` inc-VAT net w/ owned M3/paste**; **`~£121–£125` est. UK delivered!**) | [bom.csv](bom/bom.csv) |

<details>
<summary><b>Additional Visuals — Thermal Plot, SPICE Waveforms &amp; Sealed Top Cap</b></summary>
<br />
<p align="center">
  <img src="mechanical_design/thermal/thermal_network_comparison.png" alt="Aluminum Core Surface Finish Thermal Comparison" width="96%" />
  <br />
  <sub>Steady-state UV junction temperatures at 30 °C vertical hanging still air (with F_amb=0.881 rain-eave shading &amp; 14% optical re-absorption): unpainted bare mill Al (Config 0, Rev 4.9 standard) keeps T_j,UV = 76.3 °C nominal (87.8 °C worst-case) with zero paint cost or UV outgassing; optional chimney-only matte-black spray (Config 1) offers an extra 7–9 °C margin for 30 °C tropical PETG builds.</sub>
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
      <sub><b>Sealed Top Cap (0 Roof Holes)</b> — Unbroken Ø84 mm circular rain eaves lofted to a 9.5 mm vertical rounded-square chimney collar with backed Soudal Fix ALL Crystal sealant channel.</sub>
    </td>
  </tr>
</table>
</details>

## Build & Documentation

| Area | Key Files |
|---|---|
| **Build Guides & Process** | [ASSEMBLY_GUIDE.md](docs/ASSEMBLY_GUIDE.md) · [BOM.md](bom/BOM.md) · [BLOCKERS.md](docs/BLOCKERS.md) *(pre-order checklist)* · [CHANGE_CHECKLIST.md](docs/CHANGE_CHECKLIST.md) *(SSOT & mistake-proofing)* · [DESIGN_DECISIONS.md](docs/DESIGN_DECISIONS.md) · [verify_all.py](verify_all.py) |
| **Electronics & SPICE** | [schematic.pdf](circuit_design/schematic.pdf) · [ELECTRONICS_ARCHITECTURE.md](docs/ELECTRONICS_ARCHITECTURE.md) · [COMPONENT_IDS.csv](circuit_design/COMPONENT_IDS.csv) · [INTERFACE_CONTRACT.md](circuit_design/INTERFACE_CONTRACT.md) · [run_simulations.py](circuit_design/sim/run_simulations.py) |
| **Driver PCB & PCBA** | [PCB_SUMMARY.md](pcb_design/PCB_SUMMARY.md) · [driver_pcb_gerbers.zip](pcb_design/gerbers/driver_pcb/driver_pcb_gerbers.zip) · [assembly_map.pdf](pcb_design/driver_pcb/renders/assembly_map.pdf) · 2-Reel Hybrid HASL PCBA: [driver_pcb_bom_pcba_hybrid.csv](pcb_design/driver_pcb_bom_pcba_hybrid.csv) + [driver_pcb_cpl_hybrid.csv](pcb_design/driver_pcb_cpl_hybrid.csv) + [driver_pcb_diy_hand_solder.csv](pcb_design/driver_pcb_diy_hand_solder.csv) |
| **3D Print & Mechanical** | [MECHANICAL_DESIGN.md](mechanical_design/MECHANICAL_DESIGN.md) · [CLEARANCE_VERIFICATION.md](mechanical_design/CLEARANCE_VERIFICATION.md) · [mech_cap_bot.step](mechanical_design/cad/mech_cap_bot.step) · [mech_lid_bot.step](mechanical_design/cad/mech_lid_bot.step) · [mech_cable_clamp.step](mechanical_design/cad/mech_cable_clamp.step) · [mech_core_anchor.step](mechanical_design/cad/mech_core_anchor.step) · [mech_cap_top.step](mechanical_design/cad/mech_cap_top.step) · [mech_plug_top.step](mechanical_design/cad/mech_plug_top.step) · [mech_hang_bushing.step](mechanical_design/cad/mech_hang_bushing.step) · [mech_drill_jig.step](mechanical_design/cad/mech_drill_jig.step) · [lepiled_assembly.step](mechanical_design/cad/lepiled_assembly.step) |
| **Parts Data & Datasheets** | [bom.csv](bom/bom.csv) · [MECH_PARTS.csv](mechanical_design/MECH_PARTS.csv) · [datasheets_summary.md](datasheets/datasheets_summary.md) |
