# LepiLED DIY Maxi Switch — Open Blockers & User Action Items

## Active Blockers

| ID | Status | Item | Impact | Action Required |
|---|---|---|---|---|
| **B1** | **Open (Low Impact)** | Original user research Google Sheet (`1VNcXHNNrZ-xlLQjyCB3U-OSda4Kfq_rMDRMXmeiYSrs`) requires Google sign-in | Cannot verify whether any specific off-the-shelf vendor links or notes from the user's earlier spreadsheet differ from the verified UK GBP BOM | Optional: export the spreadsheet as CSV/XLSX into `docs/` or share read-only link if you want any specific parts cross-checked |

## Resolved Blockers

| ID | Status | Resolution |
|---|---|---|
| **B2** | **Resolved** | System **KiCad 9.0.8** (`/usr/bin/kicad-cli` and `pcbnew`) installed and used to generate, ERC-check (`0` violations), DRC-check (`--schematic-parity --severity-all`, `0` violations, `0` unconnected, `0` parity), plot Gerbers/Excellon, and raytrace both `driver_pcb` and `led_mcpcb`. |
| **B3** | **Resolved** | `build123d` / `trimesh` / `ngspice` / `gerbv` toolchains verified operational; all 16 SPICE checks, 2,565 datasheet corners, 2,000 Monte Carlo trials, 20 thermal FVM cases, and 612 all-pairs CAD B-Rep checks executed and passing. |
| **B4** | **Resolved** | Legacy `5 V` boost efficiency, 4.39 W PCB heat, `SK LED R 80 SA` cost penalty, and `13 mm` extended-barrel USB-C plug limitation all eliminated by the Rev 4.0 Option 2 (`20 V` USB-C PD + dual `AL8860WT-7` buck + direct-mate `6.65 mm` USB-C tunnel + dual `SK 578/50 SA`) redesign. |
