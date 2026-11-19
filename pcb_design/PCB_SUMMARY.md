# LepiLED DIY Maxi Switch — PCB Design & Verification Summary (Rev 4.0 / Option 2)

Both custom PCBs are authored natively in **KiCad 9.0.8** and verified with automated KiCad ERC, DRC (`--schematic-parity --severity-all`), zero-via-in-pad geometric audits, Gerber/Excellon exports, and 3D raytraced renders.

## 1. Board Overview & Verification Status

| Metric | Board 1: `driver_pcb` (20 V PD + Dual Buck) | Board 2: `led_mcpcb` (LED Strip, 4× per lamp) |
|---|---|---|
| **KiCad Project** | [driver_pcb.kicad_pro](file:///home/alimuldal/src/lepiled/pcb_design/driver_pcb/driver_pcb.kicad_pro) | [led_mcpcb.kicad_pro](file:///home/alimuldal/src/lepiled/pcb_design/led_mcpcb/led_mcpcb.kicad_pro) |
| **Generator Script** | [build_driver_pcb.py](file:///home/alimuldal/src/lepiled/pcb_design/driver_pcb/build_driver_pcb.py) | [build_led_mcpcb.py](file:///home/alimuldal/src/lepiled/pcb_design/led_mcpcb/build_led_mcpcb.py) |
| **Dimensions & Stackup** | `36.0 × 46.0 × 1.6 mm`, `R = 2.0 mm` corners, 2-layer FR4, 1 oz Cu, Green LPI / White silk | `20.0 × 80.0 × 1.6 mm`, `R = 1.5 mm` corners, **1-layer Aluminum MCPCB** (`LayerNumber: 1`), 1 oz Cu, 1.0 W/(m·K), White / Black silk |
| **Component Count** | 72 RefDes in schematic (62 On-PCB = 56 populated PCBA + 6 PCB features `TP1/TP2/H1..H4`; 10 Off-Board) | 2 SMD LEDs (`D_UV`, `D_VIS`) + 4 solder pads + 2× `Ø3.2 mm` NPTH (`MH1`, `MH2`) |
| **KiCad ERC (`--severity-all`)** | **0 violations** ([erc_report.rpt](file:///home/alimuldal/src/lepiled/pcb_design/driver_pcb/erc_report.rpt)) | **0 violations** ([erc_report.rpt](file:///home/alimuldal/src/lepiled/pcb_design/led_mcpcb/erc_report.rpt)) |
| **KiCad DRC (`--schematic-parity --severity-all`)** | **0 violations, 0 unconnected, 0 parity issues** ([drc_report.rpt](file:///home/alimuldal/src/lepiled/pcb_design/driver_pcb/drc_report.rpt)) | **0 violations, 0 unconnected, 0 parity issues** ([drc_report.rpt](file:///home/alimuldal/src/lepiled/pcb_design/led_mcpcb/drc_report.rpt)) |
| **Via-in-Pad Audit** | **0 via-in-pad** across all 60 vias and 135 SMD pads (all drill clearances `>= 0.25 mm`) | N/A (1-layer Al MCPCB, 0 vias) |
| **Gerber Archive** | [driver_pcb_gerbers.zip](file:///home/alimuldal/src/lepiled/pcb_design/gerbers/driver_pcb/driver_pcb_gerbers.zip) | [led_mcpcb_gerbers.zip](file:///home/alimuldal/src/lepiled/pcb_design/gerbers/led_mcpcb/led_mcpcb_gerbers.zip) |
| **PCBA / Assembly Outputs** | [driver_pcb_cpl.csv](file:///home/alimuldal/src/lepiled/pcb_design/driver_pcb_cpl.csv) (56 parts), [driver_pcb_bom_pcba.csv](file:///home/alimuldal/src/lepiled/pcb_design/driver_pcb_bom_pcba.csv), [assembly_map.pdf](file:///home/alimuldal/src/lepiled/pcb_design/driver_pcb/renders/assembly_map.pdf) | [led_mcpcb_cpl.csv](file:///home/alimuldal/src/lepiled/pcb_design/led_mcpcb_cpl.csv), [led_mcpcb_bom.csv](file:///home/alimuldal/src/lepiled/pcb_design/led_mcpcb_bom.csv) |

## 2. Board 1 (`driver_pcb`) Architecture & Layout Highlights

- **Fixed Mechanical Datums Preserved 1:1:** `H1..H4` at `(±14.0, ±19.0 mm)` (`Ø2.7 mm` drill / `Ø5.5 mm` pad, flat M2.5 nylon washers), `J1` (`GCT USB4085-GF-A`) at `(0.0, -18.50 mm)` (front mouth datum `Y = -25.76 mm`), `TP1/TP2` at `(±8.20, -19.50 mm)`, `J2/J3` (`JST B2B-XH-A`, `1.00 mm` drills) at `(±5.20, +19.20 mm)`, and `J4` (`JST B3B-XH-A`, `1.00 mm` drills) at `(-1.40, -2.50 mm)`.
- **Power & Thermal Layout:** Unbroken `B.Cu` `GND` plane across the entire board with 60 vias (all strictly outside SMD pads and IC courtyards). Dedicated short `SW1_NODE`/`SW2_NODE` loops (`0.55 mm`) tightly couple `U1`/`L1`/`D9` and `U2`/`L2`/`D10`; Kelvin sense taps connect `R8` (`5 mΩ`) cleanly to `U3.ISENP` and `U3.VCC`, and `R3`/`R4` (`0.30 Ω`) to `U1.SET`/`U2.SET`.
- **Assembly & Inspection Readiness:** `U3` (`W-DFN3030-14`) uses a segmented 2×2 thermal-pad solder paste stencil (`60%` coverage) with external top/bottom `GND` vias. Verified `F.SilkS` and mirrored `B.SilkS` pinout legends (`1:UV+ 2:UV-`, `1:VIS+ 2:VIS-`, `1:UV 2:GND 3:ALL`) match square Pin 1 pads exactly. `TP1`, `TP2`, and `H1..H4` are excluded from the pick-and-place CPL and PCBA BOM.

## 3. Board 2 (`led_mcpcb`) Architecture & Layout Highlights

- **Strict 1-Layer Aluminum MCPCB:** `led_mcpcb-job.gbrjob` specifies `LayerNumber: 1` (single `F.Cu` copper layer on `1.6 mm` aluminum core with `100 µm` `1.0 W/(m·K)` dielectric).
- **Reflow & Clearance Safeguards:** Segmented `F.Paste` stencils on both LED thermal pads (`D_UV`: 3× `1.15 × 0.75 mm` = `61.2%`; `D_VIS`: 2×3 `0.50 × 0.90 mm` = `62.9%`) prevent tombstoning and solder floating. `MH1` copper pullback (`R = 4.10 mm` around `Ø3.2 mm` NPTH) maintains `> 1.35 mm` creepage from `M3` DIN 912 SHCS heads (`Ø5.5 mm`). Distinct polarity legends (`BTM NOTCH = K` for `SST-10-UV`; `BTM NOTCH = A` for Cree `XP-E2`) prevent inverted hand reflow.

## 4. Visual Inspection Outputs

- **Native KiCad Schematic:** [schematic.pdf](file:///home/alimuldal/src/lepiled/circuit_design/schematic.pdf) / [schematic.png](file:///home/alimuldal/src/lepiled/circuit_design/schematic.png)
- **Driver PCB 3D Renders:** [render_top.png](file:///home/alimuldal/src/lepiled/pcb_design/driver_pcb/renders/render_top.png), [render_bottom.png](file:///home/alimuldal/src/lepiled/pcb_design/driver_pcb/renders/render_bottom.png), [assembly_map.pdf](file:///home/alimuldal/src/lepiled/pcb_design/driver_pcb/renders/assembly_map.pdf)
- **LED MCPCB 3D Render & Schematic:** [render_top.png](file:///home/alimuldal/src/lepiled/pcb_design/led_mcpcb/renders/render_top.png), [schematic.pdf](file:///home/alimuldal/src/lepiled/pcb_design/led_mcpcb/renders/schematic.pdf)
