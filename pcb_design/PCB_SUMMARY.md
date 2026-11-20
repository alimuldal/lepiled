# LepiLED DIY Maxi Switch — PCB Design & Verification Summary (Rev 4.2)

Rev 4.2 uses **a single custom PCB (`driver_pcb`)**, authored natively in **KiCad 9.0.8** and verified with automated real-pin-type ERC, DRC (`--schematic-parity --severity-all`), zero-via-in-pad and unbroken-`B.Cu`-power-plane audits, Gerber/Excellon exports, and 3D raytraced renders. The legacy `led_mcpcb` strip board was retired in Rev 4.2 in favor of off-the-shelf pre-mounted `20 mm` Copper Direct-Thermal-Path (DTP) LED stars.

## 1. Board Overview & Verification Status

| Metric | `driver_pcb` (20 V USB-C PD Only + Dual Buck — SOLE Custom PCB) |
|---|---|
| **KiCad Project** | [driver_pcb.kicad_pro](file:///home/alimuldal/src/lepiled/pcb_design/driver_pcb/driver_pcb.kicad_pro) |
| **Generator Script** | [build_driver_pcb.py](file:///home/alimuldal/src/lepiled/pcb_design/driver_pcb/build_driver_pcb.py) |
| **Dimensions & Stackup** | `36.0 × 46.0 × 1.6 mm`, `R = 2.0 mm` corners, 2-layer FR4, 1 oz Cu, **ENIG**, Green LPI / White silk |
| **Component Count** | `75` RefDes (`61` populated On-PCB = `57` SMD assembled by JLCPCB + `4` THT `J1..J4` hand-soldered; `4` isolated NPTH `H1..H4`; `10` Off-Board = `8×` `20 mm` Cu DTP stars + `SW1` + `SW1_BOOT`) |
| **KiCad ERC (`--severity-all`)** | **0 violations** (real pin types + `PWR_FLAG`s; [erc_report.rpt](file:///home/alimuldal/src/lepiled/pcb_design/driver_pcb/erc_report.rpt)) |
| **KiCad DRC (`--schematic-parity --severity-all`)** | **0 violations, 0 unconnected, 0 parity issues** ([drc_report.rpt](file:///home/alimuldal/src/lepiled/pcb_design/driver_pcb/drc_report.rpt)) |
| **Copper Integrity Audits** | **0 via-in-pad** (`48` vias / `143` SMD pads, `>= 0.25 mm`); **`0` non-GND `B.Cu` segments** inside buck power stage (`Y = [4.3, 16.5] mm`) |
| **Gerber & PCBA Outputs** | [driver_pcb_gerbers.zip](file:///home/alimuldal/src/lepiled/pcb_design/gerbers/driver_pcb/driver_pcb_gerbers.zip), [driver_pcb_cpl.csv](file:///home/alimuldal/src/lepiled/pcb_design/driver_pcb_cpl.csv) (`57` SMD-only), [driver_pcb_bom_pcba.csv](file:///home/alimuldal/src/lepiled/pcb_design/driver_pcb_bom_pcba.csv) (`61` w/ JLCPCB Basic LCSC#s), [assembly_map.pdf](file:///home/alimuldal/src/lepiled/pcb_design/driver_pcb/renders/assembly_map.pdf) |

## 2. Layout & JLCPCB Economic PCBA Highlights

- **Tool-Free Isolated Mounting:** `H1..H4` at `(±14.0, ±19.0 mm)` are unplated isolated NPTH (`Ø2.7 mm` drill, `Ø5.5 mm` copper keepout) that drop directly onto `MECH-LID-BOT`'s four integral `Ø2.45 mm` 3D-printed locating pins (zero PCB screws, zero brass inserts).
- **JLCPCB Basic-Part Optimization:** Standard `0603`/`0805`/`1206` passives and green `0603` status LED `D12` (`C72043`, `R9=C23153`, `R11=C4260`, `R19=C23192`, etc.) map directly to JLCPCB Basic LCSC reels to minimize Economic PCBA feeder fees; `J1..J4` THT are excluded from `driver_pcb_cpl.csv` for easy bench hand-soldering.
- **High-Speed Power Stage & Footprints:** Unbroken `B.Cu` `GND` plane beneath `U1/U2/D9/D10/L1/L2/R3/R4/C2/C3/C8/C9`; `< 10 mm` `F.Cu` switching loops; Kelvin `VIN`+`SET` taps at `R3`/`R4` (`0.30 Ω`) and `R8` (`5 mΩ`); zero-stub `F1 -> D11 (SMBJ22A)` fly-by; `J1` `Ø0.40 mm` signal drills; `U3` `1.80 × 2.70 mm` EPAD with `64.4%` segmented paste; `F1` Style-2 `1812` land pattern; mirrored `B.SilkS` pinout legends (`1:UV+ 2:UV-`, `1:VIS+ 2:VIS-`, `1:UV 2:GND 3:VIS`).

## 3. Visual Inspection Outputs

- **Native KiCad Schematic:** [schematic.pdf](file:///home/alimuldal/src/lepiled/circuit_design/schematic.pdf) / [schematic.png](file:///home/alimuldal/src/lepiled/circuit_design/schematic.png)
- **Driver PCB 3D Renders & Fab Map:** [render_top.png](file:///home/alimuldal/src/lepiled/pcb_design/driver_pcb/renders/render_top.png), [render_bottom.png](file:///home/alimuldal/src/lepiled/pcb_design/driver_pcb/renders/render_bottom.png), [assembly_map.pdf](file:///home/alimuldal/src/lepiled/pcb_design/driver_pcb/renders/assembly_map.pdf)
