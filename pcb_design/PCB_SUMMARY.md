# LepiLED DIY Maxi Switch — PCB Design & Verification Summary (Rev 4.1)

Both custom PCBs are authored natively in **KiCad 9.0.8** and verified with automated KiCad ERC (using real pin electrical types + explicit `PWR_FLAG`s), DRC (`--schematic-parity --severity-all`), zero-via-in-pad and unbroken-`B.Cu`-power-plane audits, Gerber/Excellon exports, and 3D raytraced renders.

## 1. Board Overview & Verification Status

| Metric | Board 1: `driver_pcb` (20 V PD Only + Dual Buck) | Board 2: `led_mcpcb` (LED Strip, 4× per lamp) |
|---|---|---|
| **KiCad Project** | [driver_pcb.kicad_pro](file:///home/alimuldal/src/lepiled/pcb_design/driver_pcb/driver_pcb.kicad_pro) | [led_mcpcb.kicad_pro](file:///home/alimuldal/src/lepiled/pcb_design/led_mcpcb/led_mcpcb.kicad_pro) |
| **Generator Script** | [build_driver_pcb.py](file:///home/alimuldal/src/lepiled/pcb_design/driver_pcb/build_driver_pcb.py) | [build_led_mcpcb.py](file:///home/alimuldal/src/lepiled/pcb_design/led_mcpcb/build_led_mcpcb.py) |
| **Dimensions & Stackup** | `36.0 × 46.0 × 1.6 mm`, `R = 2.0 mm` corners, 2-layer FR4, 1 oz Cu, **ENIG**, Green LPI / White silk | `20.0 × 80.0 × 1.6 mm`, `R = 1.5 mm` corners, **1-layer Aluminum MCPCB** (`LayerNumber: 1`), 1 oz Cu, `1.0 W/(m·K)`, **ENIG**, White / Black silk |
| **Component Count** | `75` RefDes (`61` populated On-PCB = `57` SMD + `4` THT `J1..J4`; `4` isolated NPTH `H1..H4`; `10` Off-Board) | `2` SMD LEDs (`D_UV`, `D_VIS`) + `4` solder pads (`Y = -24.0 mm`) + `2× Ø3.2 mm` NPTH (`MH1`, `MH2`) |
| **KiCad ERC (`--severity-all`)** | **0 violations** (real pin types + `PWR_FLAG`s; [erc_report.rpt](file:///home/alimuldal/src/lepiled/pcb_design/driver_pcb/erc_report.rpt)) | **0 violations** ([erc_report.rpt](file:///home/alimuldal/src/lepiled/pcb_design/led_mcpcb/erc_report.rpt)) |
| **KiCad DRC (`--schematic-parity --severity-all`)** | **0 violations, 0 unconnected, 0 parity issues** ([drc_report.rpt](file:///home/alimuldal/src/lepiled/pcb_design/driver_pcb/drc_report.rpt)) | **0 violations, 0 unconnected, 0 parity issues** ([drc_report.rpt](file:///home/alimuldal/src/lepiled/pcb_design/led_mcpcb/drc_report.rpt)) |
| **Via-in-Pad & Ground Plane Audit** | **0 via-in-pad** across all `48` vias and `143` SMD pads (`>= 0.25 mm`); **`0` non-GND `B.Cu` segments** inside power stage (`Y = [4.3, 16.5] mm`) | N/A (1-layer Al MCPCB, `0` vias) |
| **Gerber Archive** | [driver_pcb_gerbers.zip](file:///home/alimuldal/src/lepiled/pcb_design/gerbers/driver_pcb/driver_pcb_gerbers.zip) | [led_mcpcb_gerbers.zip](file:///home/alimuldal/src/lepiled/pcb_design/gerbers/led_mcpcb/led_mcpcb_gerbers.zip) |
| **PCBA / Assembly Outputs** | [driver_pcb_cpl.csv](file:///home/alimuldal/src/lepiled/pcb_design/driver_pcb_cpl.csv) (`57` SMD-only), [driver_pcb_bom_pcba.csv](file:///home/alimuldal/src/lepiled/pcb_design/driver_pcb_bom_pcba.csv) (`61` w/ LCSC#), [assembly_map.pdf](file:///home/alimuldal/src/lepiled/pcb_design/driver_pcb/renders/assembly_map.pdf) | [led_mcpcb_cpl.csv](file:///home/alimuldal/src/lepiled/pcb_design/led_mcpcb_cpl.csv) (`+180°` opposite notch), [led_mcpcb_bom.csv](file:///home/alimuldal/src/lepiled/pcb_design/led_mcpcb_bom.csv) (4-row color-split) |

## 2. Board 1 (`driver_pcb`) Rev 4.1 Hardening Highlights

- **Mechanical Datums & Isolated Mounting (`Option 2A`):** `H1..H4` at `(±14.0, ±19.0 mm)` are **unplated isolated NPTH** (`Ø2.7 mm` drill, `Ø5.5 mm` copper keepout) secured with nylon `M2.5 × 6 mm` screws into `MECH-LID-BOT` bosses. `J1` (`GCT USB4085-GF-A`) sits at `(0.0, -18.50 mm)` (`Y_mouth = -25.76 mm`), `J2/J3` at `(±5.20, +19.20 mm)`, and `J4` at `(-1.40, -2.50 mm)`. `TP1/TP2`, `F2`, `Q1B`, and Aux `B340A` are removed (`S2-A`).
- **Footprint & DFM Fixes:** `J1` signal drills widened to **`Ø0.40 mm`** (`0.65 × 0.90 mm` oval pads) for standard fabrication tolerances; `U3` (`W-DFN3030-14`) EPAD widened to datasheet `1.80 × 2.70 mm` with `2×2` segmented paste (`64.4%`); `U1/U2` (`TSOT25`) pads sized to `0.68 mm` nominal; `F1` (`MF-MSMF110/33X`) uses datasheet `1812` Style-2 land pattern; board upgraded to **ENIG** finish for `0.40 mm`-pitch `W-DFN` coplanarity.
- **High-Speed Power Stage & Kelvin Routing:** Unbroken `B.Cu` `GND` plane beneath the entire buck stage (`0` non-GND segments inside `Y = [4.3, 16.5] mm`), with `U1_CTRL`/`U2_CTRL` routed on `F.Cu` through `D9`/`D10` pad gaps. Compact `< 10 mm` `F.Cu` switching loops couple `U1/D9/L1/C2/C8` and `U2/D10/L2/C3/C9`; dedicated Kelvin `VIN` and `SET` sense traces tap `R3`/`R4` (`0.30 Ω`) pads directly; zero-stub fly-by routing feeds `F1 -> D11 (SMBJ22A) -> C1/R7/C10 -> R8 (5 mΩ Kelvin) -> Q1 (40 V DMN4035L-7)`.
- **PCBA-Ready Outputs:** `driver_pcb_cpl.csv` exports **strictly the 57 SMD placements**; `driver_pcb_bom_pcba.csv` lists all `61` populated parts with verified LCSC part numbers; `F.SilkS` and mirrored `B.SilkS` pinout legends (`1:UV+ 2:UV-`, `1:VIS+ 2:VIS-`, `1:UV 2:GND 3:VIS`) match square Pin 1 pads alongside [assembly_map.pdf](file:///home/alimuldal/src/lepiled/pcb_design/driver_pcb/renders/assembly_map.pdf).

## 3. Board 2 (`led_mcpcb`) Rev 4.1 Hardening Highlights

- **Strict 1-Layer Aluminum MCPCB (`ENIG`):** `led_mcpcb-job.gbrjob` specifies `LayerNumber: 1` (single `F.Cu` copper layer on `1.6 mm` aluminum core with `100 µm` `1.0 W/(m·K)` dielectric and **ENIG** finish).
- **Wire-Pad Clearance & Reflow Safeguards:** Wire solder pads shifted north from `Y = -28.0 mm` to **`Y = -24.0 mm`** (`>= 6.0 mm` from `MH2` `M3` SHCS head, `>= 2.0 mm` below `D_VIS`). Segmented `F.Paste` stencils (`D_UV`: `61.2%`; `D_VIS`: `64.0%`) prevent LED float/tombstoning. Distinct polarity legends (`BTM NOTCH = K` for `SST-10-UV`; `BTM NOTCH = A` for Cree `XP-E2`) and `+180°` relative CPL orientation prevent inverted reflow. [led_mcpcb_bom.csv](file:///home/alimuldal/src/lepiled/pcb_design/led_mcpcb_bom.csv) splits the 4 strips cleanly across the active Cree `XP-E2` bins (`2× 00S02`, `1× 00K01`, `1× 00H51`).

## 4. Visual Inspection Outputs

- **Native KiCad Schematic:** [schematic.pdf](file:///home/alimuldal/src/lepiled/circuit_design/schematic.pdf) / [schematic.png](file:///home/alimuldal/src/lepiled/circuit_design/schematic.png)
- **Driver PCB 3D Renders & Fab Map:** [render_top.png](file:///home/alimuldal/src/lepiled/pcb_design/driver_pcb/renders/render_top.png), [render_bottom.png](file:///home/alimuldal/src/lepiled/pcb_design/driver_pcb/renders/render_bottom.png), [assembly_map.pdf](file:///home/alimuldal/src/lepiled/pcb_design/driver_pcb/renders/assembly_map.pdf)
- **LED MCPCB 3D Render & Schematic:** [render_top.png](file:///home/alimuldal/src/lepiled/pcb_design/led_mcpcb/renders/render_top.png), [schematic.pdf](file:///home/alimuldal/src/lepiled/pcb_design/led_mcpcb/renders/schematic.pdf)
