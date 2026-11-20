# LepiLED DIY Maxi Switch — Pre-Order & Build Checklist (Rev 4.7)

All automated electrical, PCB, thermal, CAD, and BOM verification gates pass with zero open blockers. For the complete history of resolved engineering findings across earlier revisions, see [DESIGN_DECISIONS.md](DESIGN_DECISIONS.md).

## Routine Pre-Order Checks

| Item | What to Check Before Ordering |
|---|---|
| **1. JLCPCB Hybrid PCBA (`driver_pcb`)** | Upload [driver_pcb_gerbers.zip](../pcb_design/gerbers/driver_pcb/driver_pcb_gerbers.zip), [driver_pcb_bom_pcba_hybrid.csv](../pcb_design/driver_pcb_bom_pcba_hybrid.csv), and [driver_pcb_cpl_hybrid.csv](../pcb_design/driver_pcb_cpl_hybrid.csv) (`40` SMDs, **only 2 Extended reels**: `U1/U2` `C125330` and `U3` `C42459160`, Lead-Free HASL, Top-Side Economic PCBA). Select **"Remove order number"** so the Emperor-moth back silkscreen stays clean, verify polarized part orientation in JLCPCB's 3D viewer, and order the `10` bench hand-solder parts ([driver_pcb_diy_hand_solder.csv](../pcb_design/driver_pcb_diy_hand_solder.csv)) from RS UK / Farnell UK. *(For sub-zero or `> 30 °C` ambient builds, `LM2903DR2G` `C57474` is a drop-in `-40..+105 °C` substitute for Basic `LM393DR2G` `C7955`.)* |
| **2. LED Stars & Acrylic Shroud** | Confirm the `8×` `20 mm` Copper DTP LED stars have **electrically neutral thermal pads** and install them with `M3` nylon insulating washers. Order **clear unstabilized extruded PMMA (`Plexiglas XT`, `Ø60 × 54 × 3.0 × 115 mm`)**—never UV-blocking cast `GS` or polycarbonate. Never clean PMMA with IPA or seal with acetic-cure silicone. |
| **3. Filament & Matte-Black Core Paint** | Print all structural shells in **Matte Black ASA** (`HDT 95 °C`, UV-A resistant; Signal-Orange ASA/PETG for the hang bushing). Mask the `8× Ø20 mm` LED star pads bare before spraying the `30 × 30 × 3.0 × 200 mm` aluminum core matte black. |
