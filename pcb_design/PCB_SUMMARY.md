# LepiLED DIY Maxi Switch — Driver PCB Summary (Rev 4.9)

The lamp uses a single custom 2-layer **Lead-Free HASL** PCB (`driver_pcb`, `36.0 × 46.0 mm`), authored in **KiCad 10** and verified with automated ERC, DRC (`--refill-zones --schematic-parity --severity-all`), post-export RS-274X Gerber audits, PCBA CSV parity checks, and 3D raytraced renders. The LEDs mount off-board on standard pre-mounted `20 mm` Copper DTP LED stars.

## 1. Board Specifications & Verification

| Metric | `driver_pcb` (Rev 4.9) |
|---|---|
| **KiCad Project & Generator** | [driver_pcb.kicad_pro](driver_pcb/driver_pcb.kicad_pro) · [build_driver_pcb.py](driver_pcb/build_driver_pcb.py) |
| **Dimensions & Stackup** | `36.0 × 46.0 × 1.6 mm`, `R = 2.0 mm` corners, 2-layer FR4, 1 oz Cu, **Lead-Free HASL** finish (JLCPCB `$2` promo tier), Green LPI / White silk |
| **Component Count** | `72` RefDes (`54` PCBA = `41` JLCPCB SMD + `11` DIY [`4` THT `J1..J4` + `7` chunky 2-pad SMDs] + `2` DNP `D13/D14`; `4` isolated `M3` NPTH `H1..H4`; `4` bare HASL bench test pads `TP1..TP4`; `10` Off-Board) |
| **KiCad ERC (`--severity-all`)** | **0 violations** ([erc_report.rpt](driver_pcb/erc_report.rpt)) |
| **KiCad DRC (`--refill-zones --schematic-parity --severity-all`)** | **0 violations, 0 unconnected, 0 schematic parity issues** ([drc_report.rpt](driver_pcb/drc_report.rpt)) |
| **Copper, Gerber & Silkscreen Audits** | **0 via-in-pad** (`51` vias / `130` SMD pads, `>= 0.25 mm`); **`0` non-GND `B.Cu` segments** under buck power stage (`Y = [4.3, 16.5] mm`); **Gerber-verified `0` copper inside `r = 2.95 mm` of `M3` `H1..H4` NPTH** (`F_Cu >= 3.609 mm > Ø7` nylon washer!, `B_Cu >= 3.085 mm`); **`0` solder paste on DNP `D13`/`D14`**; **`58/58` `F.SilkS` RefDes** |
| **2-Reel Hybrid HASL PCBA** *(derived via [generate_hybrid_pcba.py](generate_hybrid_pcba.py))* | [driver_pcb_gerbers.zip](gerbers/driver_pcb/driver_pcb_gerbers.zip), [driver_pcb_bom_pcba_hybrid.csv](driver_pcb_bom_pcba_hybrid.csv) (**`41` SMDs** assembled by JLCPCB: `20` Basic + **ONLY `2` Extended reels**), [driver_pcb_cpl_hybrid.csv](driver_pcb_cpl_hybrid.csv) (`41` placements), [driver_pcb_diy_hand_solder.csv](driver_pcb_diy_hand_solder.csv) (`11` DIY parts: `4` THT `J1..J4` + `7` chunky 2-pad SMDs `F1`, `D11`, `L1/L2`, `R3/R4`, `R7`, + `2` DNP) |
| **Canonical Full On-PCB Outputs** | [driver_pcb_bom_pcba.csv](driver_pcb_bom_pcba.csv) (`54` On-PCB), [driver_pcb_cpl.csv](driver_pcb_cpl.csv) (`48` SMD), [assembly_map.pdf](driver_pcb/renders/assembly_map.pdf) (`5:1` fit-to-board) |

## 2. Layout & PCBA Highlights (Rev 4.9)

- **Value-Engineered 2-Reel Hybrid Lead-Free HASL PCBA (`£31.01` live-verified JLCPCB UK-VAT DDP invoice for 3 bare + 2 assembled boards!):** JLCPCB machine-reflows all `41` fine-pitch and `0603`/`0805`/`SOT-23`/`SOIC-8` SMDs using **`20` live-verified Basic reels** (`U4 = LM393DR2G C7955`, `U5 = Changjing CJ431 C3113`, `Q2/Q3 = 2N7002 C8545`, `D9/D10 = SS34 C8678`, `D12 = KT-0603R C2286`, `D15/D16 = BAV99 C2500`, `R19 = 220 kΩ C22961`, `R24 = 10.0 Ω C17415`, `C16 = 100 nF C14663`, and all Basic passives) + **ONLY `2` Extended reels** (`U1/U2 = AL8860WT-7 C125330` and `U3 = CH224A C42459160` — just `$6` in extended fees!). All `41` CPL rotations (including `U3 = 270°`) are live-verified against JLCPCB's 3D placement viewer, and `driver_pcb_bom_pcba_hybrid.csv` uses JLCPCB's native `JLCPCB Part #` header for zero-click matching. The `7` large, easy-to-hand-solder 2-pad SMDs (`F1` `1206` Littelfuse `046801.5NRHF`, `D11` `SMB` Littelfuse `SMBJ22A`, `L1/L2` `6045` Bourns `SRN6045-680M`, `R3/R4` `1206` Bourns `CRL1206-FW-R300ELF`, `R7` `2512` Vishay `CRCW25121R00FKEG`) plus the `4` THT headers (`J1..J4`) are consolidated into ONE Farnell UK order alongside `SW1` and `SW1_BOOT`. Optional `D13/D14` use paste-free DNP footprints (`D_SOD-323_DNP`) and are excluded from PCBA.
- **Unified `M3` NPTH Mounting Holes & Hardened Keepouts:** `H1..H4` are upgraded to **`M3` (`Ø3.20 mm` drill)** with circular `r = 3.10 mm` (`Ø6.20 mm`) `F.Cu` + `B.Cu` `PCB_RULE_AREA` keepouts — Gerber-verified `>= 3.609 mm` on `F.Cu` (clearing the entire `Ø7.0 mm` `M3` nylon insulating washer with zero copper contact!) and `>= 3.085 mm` on `B.Cu`. `J1` GND pins (`A1/A12/B1/B12`) use full zone connections tied directly to shield tabs `SH1/SH2`.
- **Power-Stage & Bring-Up Polish:** Unbroken `B.Cu` GND plane under `U1/U2/D9/D10/L1/L2/R3/R4/C2/C3/C8/C9`; tighter `C8`/`C9` placement right beside `U1.5`/`U2.5`; Kelvin `VIN` and `SET` sense traces at `R3`/`R4`; zero-stub `F1 → D11` TVS routing; `Ø0.40 mm` signal drills on `J1`; `2.10 × 3.30 mm` `U3` EPAD with segmented paste and perimeter thermal vias; and four `$0` bare HASL `1.0 mm` bench test pads (`TP1..TP4`: `VIN_20V`, `V_REF`, `UVLO_OK`, `GND`).
- **Back Silkscreen:** Includes `LEPILED REV4.9 20V-PD`, mirrored connector pinout legends (`1:UV+ 2:UV-`, `1:VIS+ 2:VIS-`, `1:UV 2:GND 3:VIS`), and an Emperor-moth (*Saturnia pavonia*) graphic. Select *"Remove order number"* at JLCPCB checkout.

## 3. Visual Outputs

- **Schematic:** [schematic.pdf](../circuit_design/schematic.pdf) · [schematic.png](../circuit_design/schematic.png)
- **PCB Renders & Assembly Map:** [render_top.png](driver_pcb/renders/render_top.png) · [render_bottom.png](driver_pcb/renders/render_bottom.png) · [gerbv_top.png](driver_pcb/renders/gerbv_top.png) · [gerbv_bottom.png](driver_pcb/renders/gerbv_bottom.png) · [assembly_map.pdf](driver_pcb/renders/assembly_map.pdf)
