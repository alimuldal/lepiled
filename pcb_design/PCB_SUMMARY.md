# LepiLED DIY Maxi Switch — PCB Design & Verification Summary (Rev 4.7)

Rev 4.7 uses **a single custom PCB (`driver_pcb`, `36 × 46 mm` — mechanically identical to Rev 4.6)**, redesigned around the locally stocked **`WCH CH224A` (`C42459160`, `1.0 mm` leaded `ESSOP-10`)** USB-C PD sink controller and **100% live-verified JLCPCB Basic passives/semiconductors**, authored natively in **KiCad 9.0.8** and verified with automated real-pin-type ERC, DRC (`--schematic-parity --severity-all`), zero-via-in-pad and unbroken-`B.Cu`-power-plane audits, Gerber/Excellon exports, and 3D raytraced renders. The legacy `led_mcpcb` strip board was retired in Rev 4.2 in favor of off-the-shelf pre-mounted `20 mm` Copper Direct-Thermal-Path (DTP) LED stars.

## 1. Board Overview & Verification Status

| Metric | `driver_pcb` (20 V USB-C PD `CH224A` + Dual Buck — SOLE Custom PCB) |
|---|---|
| **KiCad Project** | [driver_pcb.kicad_pro](driver_pcb/driver_pcb.kicad_pro) |
| **Generator Script** | [build_driver_pcb.py](driver_pcb/build_driver_pcb.py) |
| **Dimensions & Stackup** | `36.0 × 46.0 × 1.6 mm`, `R = 2.0 mm` corners, 2-layer FR4, 1 oz Cu, **Lead-Free HASL** (budget default; `1.0 mm` leaded `ESSOP-10`, zero fine-pitch DFN) or **ENIG** (optional), Green LPI / White silk |
| **Component Count** | `67` RefDes (`53` populated On-PCB = `49` SMD + `4` THT `J1..J4`; Hybrid PCBA splits this into `41` JLCPCB SMD [**ONLY 2 Extended reels: `U1/U2` + `U3`**] + `10` DIY hand-solder + `2` optional DNP `D13/D14`; `4` isolated NPTH `H1..H4`; `10` Off-Board = `8×` `20 mm` Cu DTP stars + `SW1` + `SW1_BOOT`) |
| **KiCad ERC (`--severity-all`)** | **0 violations** (real pin types + `PWR_FLAG`s; [erc_report.rpt](driver_pcb/erc_report.rpt)) |
| **KiCad DRC (`--schematic-parity --severity-all`)** | **0 violations, 0 unconnected, 0 parity issues** ([drc_report.rpt](driver_pcb/drc_report.rpt)) |
| **Copper Integrity Audits** | **0 via-in-pad** (`52` vias / `124` SMD pads, `>= 0.25 mm`); **`0` non-GND `B.Cu` segments** inside buck power stage (`Y = [4.3, 16.5] mm`) |
| **Full Turnkey PCBA Outputs** | [driver_pcb_gerbers.zip](gerbers/driver_pcb/driver_pcb_gerbers.zip), [driver_pcb_cpl.csv](driver_pcb_cpl.csv) (`49` SMD-only), [driver_pcb_bom_pcba.csv](driver_pcb_bom_pcba.csv) (`53` On-PCB), [assembly_map.pdf](driver_pcb/renders/assembly_map.pdf) |
| **Hybrid 2-Reel Budget PCBA Outputs** *(derived 1:1 via [generate_hybrid_pcba.py](generate_hybrid_pcba.py))* | [driver_pcb_bom_pcba_hybrid.csv](driver_pcb_bom_pcba_hybrid.csv) (`41` SMD for JLCPCB, **2 Extended reels = `$6` feeder fees**), [driver_pcb_cpl_hybrid.csv](driver_pcb_cpl_hybrid.csv) (`41` placements), [driver_pcb_diy_hand_solder.csv](driver_pcb_diy_hand_solder.csv) (`4` THT + `6` chunky 2-pad SMDs + `2` optional DNP notes) |

## 2. Layout, Silkscreen & JLCPCB Economic PCBA Highlights

- **Isolated Horizontal Enclosure Mounting:** `H1..H4` at `(±14.0, ±19.0 mm)` are unplated isolated NPTH (`Ø2.7 mm` drill, `Ø5.5 mm` copper keepout) bolting horizontally (SMD/JST side down for easy field access) onto `MECH-CAP-BOT`'s four filleted `M2.5` brass heat-set insert standoffs via `4× M2.5 × 6 mm` pan-head screws. All `49` SMD 3D bodies from [driver_pcb_cpl.csv](driver_pcb_cpl.csv) are verified `0.000 mm³` collision-free in CAD.
- **JLCPCB 2-Extended-Reel Hybrid Economic PCBA (Zero-Divergence Pipeline):** [build_driver_pcb.py](driver_pcb/build_driver_pcb.py) exports canonical [driver_pcb_bom_pcba.csv](driver_pcb_bom_pcba.csv) and [driver_pcb_cpl.csv](driver_pcb_cpl.csv) with 100% live-verified in-stock LCSC codes (`U3=CH224A C42459160`, `U4=LM393DR2G C7955`, `U5=TL431 C181103`, `Q2/Q3=2N7002 C8545`, `D9/D10=SS34 C8678`, `D12=KT-0603R C2286` night-vision red, `D15/D16=BAV99 C2500`, Basic `30k/5.1k/270k` UVLO, Basic `10 Ω` snubbers). [generate_hybrid_pcba.py](generate_hybrid_pcba.py) programmatically derives the 2-reel Hybrid set (checked byte-for-byte by [verify_bom.py](../bom/verify_bom.py)):
  - Offloads `4` chunky 2-pad Extended reels (`F1` `1812`, `D11` `SMB`, `L1/L2` `6×6 mm`, `R3/R4` `1206` — `R8` shunt eliminated!) to [driver_pcb_diy_hand_solder.csv](driver_pcb_diy_hand_solder.csv) and leaves optional `D13/D14` (`CC1/CC2` ESD) DNP since the `90°` USB-C plug stays captured inside the sealed lantern and `CH224A` includes internal ESD protection.
  - Result: **Only `2` Extended reels (`U1/U2` `C125330` + `U3` `C42459160` = `$6` feeder fees)**, **Lead-Free HASL** finish, zero `0.4 mm` leadless DFN, and zero out-of-stock parts.
- **Back Silkscreen & Moth Graphic:** Features `LEPILED REV4.5 20V-PD`, mirrored `B.SilkS` pinout legends (`1:UV+ 2:UV-`, `1:VIS+ 2:VIS-`, `1:UV 2:GND 3:VIS`), and a centered Emperor-moth (*Saturnia pavonia*) graphic (select *"Remove order number"* at JLCPCB checkout to keep the back clean).
- **High-Speed Power Stage & Footprints:** Unbroken `B.Cu` `GND` plane beneath `U1/U2/D9/D10/L1/L2/R3/R4/C2/C3/C8/C9`; `< 10 mm` `F.Cu` switching loops; Kelvin `VIN`+`SET` taps at `R3`/`R4` (`0.30 Ω`); zero-stub `F1 -> D11 (SMBJ22A)` fly-by; `J1` `Ø0.40 mm` signal drills; `U3` `WCH ESSOP-10` `1.0 mm` leaded pitch with `2.10 × 3.30 mm` EPAD (`60%` segmented paste); `F1` Style-2 `1812` land pattern.

## 3. Visual Inspection Outputs

- **Native KiCad Schematic:** [schematic.pdf](../circuit_design/schematic.pdf) / [schematic.png](../circuit_design/schematic.png)
- **Driver PCB 3D Renders & Fab Map:** [render_top.png](driver_pcb/renders/render_top.png), [render_bottom.png](driver_pcb/renders/render_bottom.png), [assembly_map.pdf](driver_pcb/renders/assembly_map.pdf)
