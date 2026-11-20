# LepiLED DIY Maxi Switch — Driver PCB Summary (Rev 4.7)

The lamp uses a single custom 2-layer PCB (`driver_pcb`, `36.0 × 46.0 mm`), authored in **KiCad 9.0.8** and verified with automated ERC, DRC (`--schematic-parity --severity-all`), copper integrity audits, Gerber/Excellon exports, and 3D raytraced renders. The LEDs mount off-board on standard pre-mounted `20 mm` Copper DTP stars.

## 1. Board Specifications & Verification

| Metric | `driver_pcb` |
|---|---|
| **KiCad Project & Generator** | [driver_pcb.kicad_pro](driver_pcb/driver_pcb.kicad_pro) · [build_driver_pcb.py](driver_pcb/build_driver_pcb.py) |
| **Dimensions & Stackup** | `36.0 × 46.0 × 1.6 mm`, `R = 2.0 mm` corners, 2-layer FR4, 1 oz Cu, **Lead-Free HASL** (budget default; `1.0 mm` leaded `ESSOP-10`, no fine-pitch DFN) or optional ENIG, Green LPI / White silk |
| **Component Count** | `66` RefDes (`52` On-PCB = `48` SMD + `4` THT `J1..J4`; `4` isolated NPTH `H1..H4`; `10` Off-Board = `8×` `20 mm` Cu DTP stars + `SW1` + `SW1_BOOT`) |
| **KiCad ERC (`--severity-all`)** | **0 violations** ([erc_report.rpt](driver_pcb/erc_report.rpt)) |
| **KiCad DRC (`--schematic-parity --severity-all`)** | **0 violations, 0 unconnected, 0 parity issues** ([drc_report.rpt](driver_pcb/drc_report.rpt)) |
| **Copper & Silkscreen Audits** | **0 via-in-pad** (`53` vias / `122` SMD pads, `>= 0.25 mm`); **`0` non-GND `B.Cu` segments** under the buck power stage (`Y = [4.3, 16.5] mm`); **`52/52` `F.SilkS` RefDes** |
| **Hybrid 2-Reel Budget PCBA (Recommended)** *(derived via [generate_hybrid_pcba.py](generate_hybrid_pcba.py))* | [driver_pcb_gerbers.zip](gerbers/driver_pcb/driver_pcb_gerbers.zip), [driver_pcb_bom_pcba_hybrid.csv](driver_pcb_bom_pcba_hybrid.csv) (`40` SMD, **2 Extended reels = `$6` feeder fees**), [driver_pcb_cpl_hybrid.csv](driver_pcb_cpl_hybrid.csv) (`40` placements), [driver_pcb_diy_hand_solder.csv](driver_pcb_diy_hand_solder.csv) (`4` THT + `6` chunky 2-pad SMDs + `2` optional DNP) |
| **Canonical Full On-PCB Outputs** | [driver_pcb_bom_pcba.csv](driver_pcb_bom_pcba.csv) (`52` On-PCB), [driver_pcb_cpl.csv](driver_pcb_cpl.csv) (`48` SMD), [assembly_map.pdf](driver_pcb/renders/assembly_map.pdf) (`5:1` fit-to-board) |

## 2. Layout & PCBA Notes

- **2-Extended-Reel Hybrid PCBA:** All `40` JLCPCB-assembled SMDs use live-verified in-stock LCSC parts, with only **2 Extended reels** (`U1/U2` `AL8860WT-7` `C125330` and `U3` `WCH CH224A` `C42459160`) and `20` JLCPCB Basic reels (`U4 = LM393DR2G C7955` [`0..+70 °C`; drop-in industrial `-40..+105 °C` option: `LM2903DR2G C57474`], `U5 = TL431 C181103`, `Q2/Q3 = 2N7002 C8545`, `D9/D10 = SS34 C8678`, `D12 = KT-0603R C2286`, `D15/D16 = BAV99 C2500`, and all Basic passives). Six large 2-pad SMDs (`F1`, `D11`, `L1`, `L2`, `R3`, `R4`) are offloaded to bench hand-soldering alongside `J1..J4` THT, and optional `D13/D14` (`CC1/CC2` ESD) are left DNP.
- **Power-Stage & Enclosure Layout:** Unbroken `B.Cu` ground plane under `U1/U2/D9/D10/L1/L2/R3/R4/C2/C3/C8/C9`; `< 10 mm` `F.Cu` buck switching loops; Kelvin `VIN` and `SET` sense traces at `R3`/`R4`; zero-stub `F1 → D11` TVS placement; `Ø0.40 mm` signal drills on `J1`; `2.10 × 3.30 mm` `U3` thermal pad with segmented paste; and isolated unplated `H1..H4` (`Ø2.7 mm` NPTH) mounting holes. All `48` SMD 3D bodies clear the enclosure with `0.000 mm³` interference.
- **Back Silkscreen:** Includes `LEPILED REV4.7 20V-PD`, mirrored connector pinout legends (`1:UV+ 2:UV-`, `1:VIS+ 2:VIS-`, `1:UV 2:GND 3:VIS`), and an Emperor-moth (*Saturnia pavonia*) graphic. Select *"Remove order number"* at JLCPCB checkout to keep the back clean.

## 3. Visual Outputs

- **Schematic:** [schematic.pdf](../circuit_design/schematic.pdf) · [schematic.png](../circuit_design/schematic.png)
- **PCB Renders & Assembly Map:** [render_top.png](driver_pcb/renders/render_top.png) · [render_bottom.png](driver_pcb/renders/render_bottom.png) · [assembly_map.pdf](driver_pcb/renders/assembly_map.pdf)
