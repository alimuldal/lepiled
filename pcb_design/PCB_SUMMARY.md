# LepiLED DIY Maxi Switch — Driver PCB Summary (Rev 4.8)

The lamp uses a single custom 2-layer **ENIG** PCB (`driver_pcb`, `36.0 × 46.0 mm`), authored in **KiCad 10** and verified with automated ERC, DRC (`--refill-zones --schematic-parity --severity-all`), post-export RS-274X Gerber audits, PCBA CSV parity checks, and 3D raytraced renders. The LEDs mount off-board on standard pre-mounted `20 mm` LED stars.

## 1. Board Specifications & Verification

| Metric | `driver_pcb` (Rev 4.8) |
|---|---|
| **KiCad Project & Generator** | [driver_pcb.kicad_pro](driver_pcb/driver_pcb.kicad_pro) · [build_driver_pcb.py](driver_pcb/build_driver_pcb.py) |
| **Dimensions & Stackup** | `36.0 × 46.0 × 1.6 mm`, `R = 2.0 mm` corners, 2-layer FR4, 1 oz Cu, **ENIG** finish (flat gold pads for `U3` `ESSOP-10`, `J1` `0.40 mm` drills & `TP1..TP4`), Green LPI / White silk |
| **Component Count** | `72` RefDes (`54` PCBA = `48` JLCPCB SMD + `4` THT `J1..J4` + `2` DNP `D13/D14`; `4` isolated NPTH `H1..H4`; `4` bare ENIG bench test pads `TP1..TP4`; `10` Off-Board) |
| **KiCad ERC (`--severity-all`)** | **0 violations** ([erc_report.rpt](driver_pcb/erc_report.rpt)) |
| **KiCad DRC (`--refill-zones --schematic-parity --severity-all`)** | **0 violations, 0 unconnected, 0 schematic parity issues** ([drc_report.rpt](driver_pcb/drc_report.rpt)) |
| **Copper, Gerber & Silkscreen Audits** | **0 via-in-pad** (`51` vias / `130` SMD pads, `>= 0.25 mm`); **`0` non-GND `B.Cu` segments** under buck power stage (`Y = [4.3, 16.5] mm`); **Gerber-verified `0` copper inside `r = 2.70 mm` of `H1..H4` NPTH** (`F_Cu >= 3.61 mm`, `B_Cu >= 2.79 mm`); **`0` solder paste on DNP `D13`/`D14`**; **`58/58` `F.SilkS` RefDes** |
| **Low-Hassle Full-SMD ENIG PCBA** *(derived via [generate_hybrid_pcba.py](generate_hybrid_pcba.py))* | [driver_pcb_gerbers.zip](gerbers/driver_pcb/driver_pcb_gerbers.zip), [driver_pcb_bom_pcba_hybrid.csv](driver_pcb_bom_pcba_hybrid.csv) (**ALL `48` SMDs** assembled by JLCPCB: `20` Basic + `7` Extended reels), [driver_pcb_cpl_hybrid.csv](driver_pcb_cpl_hybrid.csv) (`48` placements), [driver_pcb_diy_hand_solder.csv](driver_pcb_diy_hand_solder.csv) (**ONLY `4` THT connectors `J1..J4`** + `2` DNP) |
| **Canonical Full On-PCB Outputs** | [driver_pcb_bom_pcba.csv](driver_pcb_bom_pcba.csv) (`54` On-PCB), [driver_pcb_cpl.csv](driver_pcb_cpl.csv) (`48` SMD), [assembly_map.pdf](driver_pcb/renders/assembly_map.pdf) (`5:1` fit-to-board) |

## 2. Layout & PCBA Highlights (Rev 4.8)

- **Zero Home SMD Soldering (Full-SMD ENIG PCBA):** JLCPCB machine-reflows all `48` populated SMDs using live-verified LCSC stock: `20` Basic reels (`U4 = LM393DR2G C7955`, `U5 = TL431 C181103`, `Q2/Q3 = 2N7002 C8545`, `D9/D10 = SS34 C8678`, `D12 = KT-0603R C2286`, `D15/D16 = BAV99 C2500`, `R24 = 10.0 Ω C17415`, `C16 = 100 nF C14663`, and all other Basic passives) + `7` Extended reels (`U1/U2 = AL8860WT-7 C125330`, `U3 = CH224A C42459160`, `F1 = Littelfuse 046801.5NRHF C151143`, `D11 = RUILON SMBJ22A C10214`, `L1/L2 = Sunlord SWPA6045S680MT C53663`, `R3/R4 = 1206W4F300LT5E C59882`, `R7 = 25121WF100KT4E C11254`). Only `J1..J4` THT are hand-soldered at home; optional `D13/D14` use paste-free DNP footprints (`D_SOD-323_DNP`) and are excluded from PCBA.
- **Hardened Copper Keepouts & Thermal Reliefs:** Circular `r = 2.80 mm` (`Ø5.60 mm`) `F.Cu` + `B.Cu` `PCB_RULE_AREA` keepouts around `H1..H4` NPTH guarantee `>= 2.78 mm` bare fiberglass around the `M2.5` nylon mounting screws (post-verified directly on exported RS-274X Gerbers). `J1` GND pins (`A1/A12/B1/B12`) use full zone connections tied directly to shield tabs `SH1/SH2` (eliminating `starved_thermal` warnings).
- **Power-Stage & Bring-Up Polish:** Unbroken `B.Cu` GND plane under `U1/U2/D9/D10/L1/L2/R3/R4/C2/C3/C8/C9`; tighter `C8`/`C9` placement right beside `U1.5`/`U2.5`; Kelvin `VIN` and `SET` sense traces at `R3`/`R4`; zero-stub `F1 → D11` TVS routing; `Ø0.40 mm` signal drills on `J1`; `2.10 × 3.30 mm` `U3` EPAD with segmented paste and perimeter thermal vias; and four `$0` bare ENIG `1.0 mm` bench test pads (`TP1..TP4`: `VIN_20V`, `V_REF`, `UVLO_OK`, `GND`).
- **Back Silkscreen:** Includes `LEPILED REV4.8 20V-PD`, mirrored connector pinout legends (`1:UV+ 2:UV-`, `1:VIS+ 2:VIS-`, `1:UV 2:GND 3:VIS`), and an Emperor-moth (*Saturnia pavonia*) graphic. Select *"Remove order number"* at JLCPCB checkout.

## 3. Visual Outputs

- **Schematic:** [schematic.pdf](../circuit_design/schematic.pdf) · [schematic.png](../circuit_design/schematic.png)
- **PCB Renders & Assembly Map:** [render_top.png](driver_pcb/renders/render_top.png) · [render_bottom.png](driver_pcb/renders/render_bottom.png) · [gerbv_top.png](driver_pcb/renders/gerbv_top.png) · [gerbv_bottom.png](driver_pcb/renders/gerbv_bottom.png) · [assembly_map.pdf](driver_pcb/renders/assembly_map.pdf)
