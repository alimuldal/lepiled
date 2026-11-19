# LepiLED DIY Maxi Switch — Open Items & Build Notes (Rev 4.1)

All engineering blockers from Rev 1–4.0 and every actionable finding from the two independent fresh-eyes adversarial reviews (Carbon and Opus 5.5) are resolved and verified in **Rev 4.1** (see [DESIGN_DECISIONS.md](file:///home/alimuldal/src/lepiled/docs/DESIGN_DECISIONS.md)).

## Practical Pre-Order Build Notes (Non-Blocking)

| ID | Status | Item | Impact | Action Before Ordering |
|---|---|---|---|---|
| **N1** | **Routine Check** | JLCPCB / LCSC PCBA live stock for `driver_pcb` (`61` parts) | Occasional passive/IC reel stock fluctuations at time of order | Upload [driver_pcb_bom_pcba.csv](file:///home/alimuldal/src/lepiled/pcb_design/driver_pcb_bom_pcba.csv) and [driver_pcb_cpl.csv](file:///home/alimuldal/src/lepiled/pcb_design/driver_pcb_cpl.csv) (`57` SMD-only); substitute pin-compatible 0603/0805 passives if needed and plan to hand-solder the `4` THT connectors (`J1..J4`) to avoid THT assembly fees. |
| **N2** | **Routine Check** | `led_mcpcb` mixed visible LED assembly (`4×` strips) | Each lamp uses `2×` Royal Blue (`00S02`), `1×` Green (`00K01`), and `1×` Cool White (`00H51`) alongside `4×` UV-A (`SST-10-UV`) | Order bare **1-layer Al ENIG** strips from JLCPCB and hand-reflow the 8 LEDs on a hotplate/skillet per [led_mcpcb_bom.csv](file:///home/alimuldal/src/lepiled/pcb_design/led_mcpcb_bom.csv), double-checking the opposite bottom-pad notches (`D_UV`: notch = K; `D_VIS`: notch = A). |
| **N3** | **Optional** | Original user research Google Sheet (`1VNcXHNNrZ-xlLQjyCB3U-OSda4Kfq_rMDRMXmeiYSrs`) requires Google sign-in | Cannot cross-check whether any earlier personal notes differ from the verified UK GBP BOM | Optional: export as CSV/XLSX into `docs/` if any specific supplier notes need comparison. |

## Resolved Engineering Blockers & Adversarial Review Campaigns

| ID | Status | Resolution |
|---|---|---|
| **B2** | **Resolved** | System **KiCad 9.0.8** generates, runs real-pin-type ERC (`0` violations) and DRC (`--schematic-parity --severity-all`, `0` violations, `0` unconnected, `0` parity), plots Gerbers/Excellon, and raytraces both `driver_pcb` (`ENIG`) and `led_mcpcb` (`ENIG`). |
| **B3** | **Resolved** | Full automated verification toolchain (`ngspice`, `build123d`, `trimesh`, `pyvista`, `gerbv`, 2D/3D FVM thermal solver, BOM parity verifier) passes 100% on Rev 4.1 (`15/15` SPICE + `2,565` corners + `2,000` MC, `20/20` + `35 °C` `5/5` thermal, `35/35` param + `272/272` B-Rep CAD, `£98.49` ex-VAT BOM). |
| **B4** | **Resolved** | Legacy `5 V` boost heat (`4.39 W`), bottom heatsink & CNC milling overhead, and extended-barrel USB-C limitation eliminated across Rev 4.0 -> Rev 4.1 (`20 V` USB-C PD only, dual `AL8860` buck, top-heatsink-only `S1-A`, zero CNC milling, `£0.30` `20 mm` rubber grommet + conformal coat). |
| **B5** | **Resolved** | All Carbon and Opus 5.5 adversarial review findings closed in Rev 4.1: `0.90 V` hysteretic `LM393B` UVLO (zero chatter), `40 V` `DMN4035L-7` + `33 V` `MF-MSMF110/33X` + unidirectional `SMBJ22A` + `CC1/CC2` & `J4` ESD diodes, `100 nF + 6.8 Ω` damped output shunts, gold `C&K 7211SYZBE` dry-circuit DPDT switch, isolated NPTH `H1..H4` + nylon `M2.5`, unbroken `B.Cu` power plane, `Ø0.40 mm` `J1` drills, `Y = -24.0 mm` MCPCB pads, active Cree `XP-E2` bins, and `0.50 mm` top anchor preload recess (`Opus B-H3`). |
