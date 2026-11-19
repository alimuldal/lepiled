# LepiLED DIY Maxi Switch (Rev 4.0 / Option 2)

Open-source, fanless DIY implementation of Gunnar Brehm's *LepiLED Maxi Switch* moth lamp (`4× 365 nm UV-A + 2× 455 nm Royal Blue + 1× 528 nm Green + 1× 6200 K Cool White`), redesigned around **20 V USB-C PD + dual constant-current buck LED drivers** (`94.3%` system efficiency, `0.50 W` nominal PCB dissipation, direct compatibility with standard USB-C PD laptop chargers and 20 V power banks).

## Architecture Highlights (Rev 4.0 / Option 2)

- **Power Input & Protection:** Standalone `Diodes AP33771C` USB-C PD 3.1 sink negotiates `20 V / 1.0 A` over a standard `GCT USB4085-GF-A` port (`J1`), protected by a `Bourns MF-MSMF150/24X` PTC polyfuse (`F1`), bidirectional `SMBJ22CA` TVS (`D11`), consolidated `6.7 µF` RC hot-plug damper (`C1 + C10/R7 + C11`, clamping `85 °C / 1.0 µH` hot-plug transients to `26.65 V`), and back-to-back `DMN3404L` load-switch MOSFETs (`Q1A/Q1B`). Optional `18–24 V` Aux DC input (`TP1/TP2`) passes through `F2` + `B340A` (`D13`) with zero back-feed to `J1` (`0.000 mV`).
- **Dual Buck LED Drivers (`333 mA`):** Two `Diodes AL8860WT-7` hysteretic buck drivers (`U1`, `U2`) with `0.30 Ω` sense resistors (`R3/R4`) and `68 µH` shielded inductors (`L1/L2`) regulate the 4S UV-A string (`J2`) and 4S Visible string (`J3`) at `330–336 mA` (`5.4%–7.3%` ripple, `2.47×` `I_sat` margin).
- **Hardware UVLO & Ground-Referenced Maxi-Switch:** Dual `TI LM393B` comparator (`U4`) + `LM4040-2.5` reference (`U5`) cleanly disables both drivers below `17.25 V` (rejecting `5 V / 9 V / 12 V / 15 V` non-20V USB chargers). Ground-referenced `SW1` (`4-UV / OFF / 8-ALL`) drives `BSS138` active-low pull-downs (`Q2/Q3`) with `BAT54` Schottky steering (`D12`, `> 638 mV` gate margin).
- **Fanless Dual-Heatsink Enclosure:** Borosilicate 3.3 tube (`75/68/3.5 × 150 mm`), matte-black `40 × 40 × 3 mm` Al core carrying `4×` 1-layer Al MCPCB strips, `6.0 mm` thermal isolation bulkhead, and identical `£5.88` `Fischer SK 578/50 SA` radial heatsinks top and bottom (`330 mm` tall, passing **20/20** thermal FVM cases up to `30 °C` horizontal `DS-100%`). Direct-mate `mech_cap_bot_usbc` accepts standard `6.65 mm` USB-C PD laptop-charger plugs directly.

## Verification Summary

| Domain | Verification Suite | Result | Key Artifact |
|---|---|---|---|
| **Circuit & SPICE** | `ngspice` 6 testbenches + `2,565` datasheet corners + `2,000`-trial Monte Carlo | **16/16 PASS** (`0` corner fails, `100.0%` MC yield) | [sim_summary.json](file:///home/alimuldal/src/lepiled/circuit_design/sim/outputs/sim_summary.json) |
| **Driver PCB (KiCad 9.0.8)** | Native ERC + DRC (`--schematic-parity --severity-all`) + zero-via-in-pad audit | **0 ERC, 0 DRC, 0 unconnected, 0 parity, 0 via-in-pad** | [driver_pcb.kicad_pcb](file:///home/alimuldal/src/lepiled/pcb_design/driver_pcb/driver_pcb.kicad_pcb) |
| **LED MCPCB (KiCad 9.0.8)** | Native ERC + DRC (`--schematic-parity --severity-all`) + 1L Al `.gbrjob` | **0 ERC, 0 DRC, 0 unconnected, 0 parity** | [led_mcpcb.kicad_pcb](file:///home/alimuldal/src/lepiled/pcb_design/led_mcpcb/led_mcpcb.kicad_pcb) |
| **Thermal (2D/3D FVM)** | Coupled 2D MCPCB + 3D Driver PCB + Dual `SK 578/50 SA` network | **20/20 PASS** (`T_j,UV <= 83.5 °C`, `T_PCB <= 45.5 °C` @ `30 °C` DS-100%) | [thermal_summary.json](file:///home/alimuldal/src/lepiled/mechanical_design/thermal/thermal_summary.json) |
| **Mechanical CAD** | 34 param checks + 5 watertight STLs + 5,913-ray USB-C check + 612 B-Rep pairs | **ALL PASS** (`0/612` collisions, `0.000 mm³` kinematic sweeps) | [cad_verification.json](file:///home/alimuldal/src/lepiled/mechanical_design/cad/cad_verification.json) |
| **UK GBP BOM** | 1:1 RefDes/PCBA/Harness/Mechanical parity + penny arithmetic | **PASS** (`£107.68` ex-VAT / `£129.22` inc-VAT amort) | [bom.csv](file:///home/alimuldal/src/lepiled/bom/bom.csv) |

## Repository Structure

- **Circuit & Simulation:** [schematic.pdf](file:///home/alimuldal/src/lepiled/circuit_design/schematic.pdf), [COMPONENT_IDS.csv](file:///home/alimuldal/src/lepiled/circuit_design/COMPONENT_IDS.csv), [INTERFACE_CONTRACT.md](file:///home/alimuldal/src/lepiled/circuit_design/INTERFACE_CONTRACT.md), [ELECTRONICS_ARCHITECTURE.md](file:///home/alimuldal/src/lepiled/docs/ELECTRONICS_ARCHITECTURE.md), [run_simulations.py](file:///home/alimuldal/src/lepiled/circuit_design/sim/run_simulations.py)
- **KiCad PCBs & Gerbers:** [PCB_SUMMARY.md](file:///home/alimuldal/src/lepiled/pcb_design/PCB_SUMMARY.md), [driver_pcb_gerbers.zip](file:///home/alimuldal/src/lepiled/pcb_design/gerbers/driver_pcb/driver_pcb_gerbers.zip), [led_mcpcb_gerbers.zip](file:///home/alimuldal/src/lepiled/pcb_design/gerbers/led_mcpcb/led_mcpcb_gerbers.zip)
- **Mechanical & Thermal:** [MECHANICAL_DESIGN.md](file:///home/alimuldal/src/lepiled/mechanical_design/MECHANICAL_DESIGN.md), [CLEARANCE_VERIFICATION.md](file:///home/alimuldal/src/lepiled/mechanical_design/CLEARANCE_VERIFICATION.md), [MECH_PARTS.csv](file:///home/alimuldal/src/lepiled/mechanical_design/MECH_PARTS.csv)
- **BOM & Build Docs:** [BOM.md](file:///home/alimuldal/src/lepiled/bom/BOM.md), [ASSEMBLY_GUIDE.md](file:///home/alimuldal/src/lepiled/docs/ASSEMBLY_GUIDE.md), [BLOCKERS.md](file:///home/alimuldal/src/lepiled/docs/BLOCKERS.md)
