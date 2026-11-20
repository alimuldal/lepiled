# LepiLED DIY Maxi Switch — PCB Design & Verification Summary (Rev 4.6)

Rev 4.6 uses **a single custom PCB (`driver_pcb`, unchanged electrically from Rev 4.5)**, authored natively in **KiCad 9.0.8** and verified with automated real-pin-type ERC, DRC (`--schematic-parity --severity-all`), zero-via-in-pad and unbroken-`B.Cu`-power-plane audits, Gerber/Excellon exports, and 3D raytraced renders. The legacy `led_mcpcb` strip board was retired in Rev 4.2 in favor of off-the-shelf pre-mounted `20 mm` Copper Direct-Thermal-Path (DTP) LED stars.

## 1. Board Overview & Verification Status

| Metric | `driver_pcb` (20 V USB-C PD Only + Dual Buck — SOLE Custom PCB) |
|---|---|
| **KiCad Project** | [driver_pcb.kicad_pro](driver_pcb/driver_pcb.kicad_pro) |
| **Generator Script** | [build_driver_pcb.py](driver_pcb/build_driver_pcb.py) |
| **Dimensions & Stackup** | `36.0 × 46.0 × 1.6 mm`, `R = 2.0 mm` corners, 2-layer FR4, 1 oz Cu, **Lead-Free HASL** (budget/1-off) or **ENIG** (optional upgrade), Green LPI / White silk |
| **Component Count** | `75` RefDes (`61` populated On-PCB = `57` SMD + `4` THT `J1..J4`; Hybrid PCBA splits this into `50` JLCPCB SMD + `11` DIY hand-solder; `4` isolated NPTH `H1..H4`; `10` Off-Board = `8×` `20 mm` Cu DTP stars + `SW1` + `SW1_BOOT`) |
| **KiCad ERC (`--severity-all`)** | **0 violations** (real pin types + `PWR_FLAG`s; [erc_report.rpt](driver_pcb/erc_report.rpt)) |
| **KiCad DRC (`--schematic-parity --severity-all`)** | **0 violations, 0 unconnected, 0 parity issues** ([drc_report.rpt](driver_pcb/drc_report.rpt)) |
| **Copper Integrity Audits** | **0 via-in-pad** (`48` vias / `143` SMD pads, `>= 0.25 mm`); **`0` non-GND `B.Cu` segments** inside buck power stage (`Y = [4.3, 16.5] mm`) |
| **Full Turnkey PCBA Outputs** | [driver_pcb_gerbers.zip](gerbers/driver_pcb/driver_pcb_gerbers.zip), [driver_pcb_cpl.csv](driver_pcb_cpl.csv) (`57` SMD-only), [driver_pcb_bom_pcba.csv](driver_pcb_bom_pcba.csv) (`61` On-PCB), [assembly_map.pdf](driver_pcb/renders/assembly_map.pdf) |
| **Hybrid Budget PCBA Outputs** *(derived 1:1 via [generate_hybrid_pcba.py](generate_hybrid_pcba.py))* | [driver_pcb_bom_pcba_hybrid.csv](driver_pcb_bom_pcba_hybrid.csv) (`50` SMD for JLCPCB), [driver_pcb_cpl_hybrid.csv](driver_pcb_cpl_hybrid.csv) (`50` placements), [driver_pcb_diy_hand_solder.csv](driver_pcb_diy_hand_solder.csv) (`4` THT + `7` chunky 2-pad SMDs) |

## 2. Layout, Silkscreen & JLCPCB Economic PCBA Highlights

- **Isolated Horizontal Enclosure Mounting:** `H1..H4` at `(±14.0, ±19.0 mm)` are unplated isolated NPTH (`Ø2.7 mm` drill, `Ø5.5 mm` copper keepout) bolting horizontally (SMD/JST side down for easy field access) onto `MECH-CAP-BOT`'s four filleted `M2.5` brass heat-set insert standoffs via `4× M2.5 × 6 mm` pan-head screws. All `57` SMD 3D bodies from [driver_pcb_cpl.csv](driver_pcb_cpl.csv) are verified `0.000 mm³` collision-free in CAD.
- **JLCPCB Full vs. Hybrid Economic PCBA (Zero-Divergence Pipeline):** [build_driver_pcb.py](driver_pcb/build_driver_pcb.py) exports the canonical full [driver_pcb_bom_pcba.csv](driver_pcb_bom_pcba.csv) and [driver_pcb_cpl.csv](driver_pcb_cpl.csv) using verified JLCPCB Basic LCSC codes (leaving unverified/stock-varying Extended codes blank so JLCPCB matches by exact MPN/Comment without silent mis-population). [generate_hybrid_pcba.py](generate_hybrid_pcba.py) programmatically derives the budget Hybrid set (checked byte-for-byte by [verify_bom.py](../bom/verify_bom.py)):
  - Offloads `5` chunky 2-pad Extended reels (`F1` `1812`, `D11` `SMB`, `L1/L2` `6×6 mm`, `R3/R4` `1206`, `R8` `1206`) to [driver_pcb_diy_hand_solder.csv](driver_pcb_diy_hand_solder.csv) (`-$15` in feeder fees) while JLCPCB still places `U3` (`W-DFN3030-14`), `U1/U2` (`TSOT25`), all `SOT-23`/`SOD-323` devices, and all `0603`/`0805`/`1206` passives.
  - Applies two verified JLCPCB Basic drop-in swaps (`-$6` in feeder fees): `U4` `LM393BIDR` → `onsemi LM393DR2G` (`C7955`, identical SOIC-8 pinout, `0..70 °C` grade, worst-case UVLO `17.03–18.06 V / 16.15–17.13 V` PASS) and `D9/D10` `B340A-13-F` → `MDD SS34` (`C8678`, identical `3 A / 40 V` SMA Schottky). `R15` remains `59.0 kΩ` to keep worst-case UVLO thresholds strictly clear of `15 V + 5%` (`15.75 V`) and `20 V - 5%` (`19.0 V`).
  - Choosing **Lead-Free HASL** instead of ENIG saves a further `~£13` at JLCPCB checkout (fine for `0.4 mm` DFN when JLCPCB reflows `U3` with a stencil).
- **Back Silkscreen & Moth Graphic:** Features `LEPILED REV4.5 20V-PD`, mirrored `B.SilkS` pinout legends (`1:UV+ 2:UV-`, `1:VIS+ 2:VIS-`, `1:UV 2:GND 3:VIS`), and a centered Emperor-moth (*Saturnia pavonia*) graphic (with `JLCJLCJLCJLC` removed — select *"Remove order number"* at JLCPCB checkout to keep the back clean).
- **High-Speed Power Stage & Footprints:** Unbroken `B.Cu` `GND` plane beneath `U1/U2/D9/D10/L1/L2/R3/R4/C2/C3/C8/C9`; `< 10 mm` `F.Cu` switching loops; Kelvin `VIN`+`SET` taps at `R3`/`R4` (`0.30 Ω`) and `R8` (`5 mΩ`); zero-stub `F1 -> D11 (SMBJ22A)` fly-by; `J1` `Ø0.40 mm` signal drills; `U3` `1.80 × 2.70 mm` EPAD with `64.4%` segmented paste; `F1` Style-2 `1812` land pattern.

## 3. Visual Inspection Outputs

- **Native KiCad Schematic:** [schematic.pdf](../circuit_design/schematic.pdf) / [schematic.png](../circuit_design/schematic.png)
- **Driver PCB 3D Renders & Fab Map:** [render_top.png](driver_pcb/renders/render_top.png), [render_bottom.png](driver_pcb/renders/render_bottom.png), [assembly_map.pdf](driver_pcb/renders/assembly_map.pdf)
