# LepiLED DIY Maxi Switch — Open Items & Build Notes (Rev 4.3)

All engineering blockers from Rev 1–4.2 and every actionable finding from both independent adversarial review rounds (Rev 4.1 electrical/mechanical review, Rev 4.2 LED + single-unit cost-down review) plus Rev 4.3 field-robustness/weatherproofing upgrades are resolved and verified in **Rev 4.3** (see [DESIGN_DECISIONS.md](file:///home/alimuldal/src/lepiled/docs/DESIGN_DECISIONS.md)).

## Practical Pre-Order Build Notes (Non-Blocking)

| ID | Status | Item | Impact | Action Before Ordering |
|---|---|---|---|---|
| **N1** | **Routine Check** | JLCPCB / LCSC Economic PCBA live stock for `driver_pcb` (`57` SMD assembled, `4` THT hand-soldered) | Occasional passive/IC reel stock fluctuations at time of order | Upload [driver_pcb_bom_pcba.csv](file:///home/alimuldal/src/lepiled/pcb_design/driver_pcb_bom_pcba.csv) and [driver_pcb_cpl.csv](file:///home/alimuldal/src/lepiled/pcb_design/driver_pcb_cpl.csv) (`driver_pcb` is the sole custom PCB; `D12=C72043`, `R9=C23153`, `R11=C4260`, `R19=C23192` are JLCPCB Basic parts). Hand-solder `J1..J4` THT from RS UK / Farnell UK to avoid THT assembly surcharges. |
| **N2** | **Routine Check** | `8×` Pre-mounted `20 mm` Copper DTP LED stars & **UVT PMMA acrylic shroud** (`MECH-TUBE-1`) | Avoids custom MCPCB fabrication, bare-SMD reflow, and glass breakage; UV performance depends on choosing UV-transmitting acrylic | Confirm vendor listings specify **electrically neutral thermal pads** on `20 mm` Copper DTP stars (mount with `16× M3` nylon insulating washers; check `pad-to-core = open`), and order **UV-transmitting / unstabilized cast PMMA** (`Ø75 × 69 × 3.0 mm`, never polycarbonate!). |
| **N3** | **Optional** | Original user research Google Sheet (`1VNcXHNNrZ-xlLQjyCB3U-OSda4Kfq_rMDRMXmeiYSrs`) requires Google sign-in | Cannot cross-check whether any earlier personal notes differ from the verified UK GBP BOM | Optional: export as CSV/XLSX into `docs/` if any specific supplier notes need comparison. |

## Resolved Engineering Blockers & Adversarial Review Campaigns

| ID | Status | Resolution |
|---|---|---|
| **B2** | **Resolved** | System **KiCad 9.0.8** generates, runs real-pin-type ERC (`0` violations) and DRC (`--schematic-parity --severity-all`, `0` violations, `0` unconnected, `0` parity), plots Gerbers/Excellon, and raytraces `driver_pcb` (`ENIG`). |
| **B3** | **Resolved** | Full automated verification toolchain (`ngspice`, `build123d`, `trimesh`, `pyvista`, `gerbv`, 2D/3D FVM thermal solver, BOM parity verifier) passes 100% on Rev 4.3 (`15/15` SPICE + `2,565` corners + `2,000` MC, `16/16` Real-WPE `22–30 °C` + `4/4` `35 °C` thermal incl. UVT PMMA & rain-hat derating, `46/46` param + `210/210` B-Rep CAD, `£91.35` ex-VAT 1-off / `£84.80` net with owned M3 + thermal paste). |
| **B4** | **Resolved** | Legacy `5 V` boost heat (`4.39 W`), bottom heatsink, CNC milling overhead, and extended-barrel USB-C limitation eliminated across Rev 4.0 -> Rev 4.3 (`20 V` USB-C PD only, dual `AL8860` buck, single bare protruding `250 mm` Al core, zero CNC milling, `20 mm` rubber grommet + conformal coat). |
| **B5** | **Resolved** | All Rev 4.1 Carbon + Opus 5.5 adversarial findings closed: `0.90 V` hysteretic `LM393B` UVLO, `40 V` `DMN4035L-7` + `33 V` `MF-MSMF110/33X` + unidirectional `SMBJ22A` + `CC1/CC2` & `J4` ESD diodes, `100 nF + 6.8 Ω` damped output shunts, gold `C&K 7211SYZBE` dry-circuit DPDT switch, isolated NPTH `H1..H4`, unbroken `B.Cu` power plane, `Ø0.40 mm` `J1` drills, and active Cree `XP-E2` bins. |
| **B6** | **Resolved** | Rev 4.2 + Rev 4.3 hobby buildability, robustness, waterproofing & weight upgrades implemented and verified: `8×` pre-mounted `20 mm` Copper DTP stars (`MECH-DRILL-JIG` included), shatter-resistant UVT PMMA shroud (`120 g`), bare `250 mm × 3 mm` protruding Al core, bottom-mounted `SW1` inside bolt-on `MECH-BASE-RING`, integral `Ø108 mm` `MECH-CAP-TOP` drip-brim + detachable pack-flat `MECH-RAIN-HAT`, contoured `MECH-CAP-BOT` (`~892 g` FDM total), zero brass inserts, single `M3` hardware, and JLCPCB Basic PCBA. |
