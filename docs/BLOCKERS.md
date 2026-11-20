# LepiLED DIY Maxi Switch — Open Items & Build Notes (Rev 4.5)

All engineering blockers from Rev 1–4.4 and every P0/P1 finding from all three independent adversarial review campaigns (electrical/PCB, LED/MCPCB, and mechanical/weatherproofing) are resolved and verified in **Rev 4.5** (see [DESIGN_DECISIONS.md](DESIGN_DECISIONS.md)).

## Practical Pre-Order Build Notes (Non-Blocking)

| ID | Status | Item | Impact | Action Before Ordering |
|---|---|---|---|---|
| **N1** | **Routine Check** | JLCPCB / LCSC Economic PCBA live stock & order-number option for `driver_pcb` (`57` SMD assembled, `4` THT hand-soldered) | Occasional passive/IC reel stock fluctuations; factory order serial could otherwise stamp over `B.SilkS` | Upload [driver_pcb_bom_pcba.csv](../pcb_design/driver_pcb_bom_pcba.csv) and [driver_pcb_cpl.csv](../pcb_design/driver_pcb_cpl.csv) (`driver_pcb` is the sole custom PCB; `D12=C72043`, `R9=C23153`, `R11=C4260`, `R19=C23192` are JLCPCB Basic parts). Select **"Remove order number"** at checkout so JLCPCB leaves the Emperor-moth back silkscreen untouched, and hand-solder `J1..J4` THT from RS UK / Farnell UK. |
| **N2** | **Routine Check** | `8×` Pre-mounted `20 mm` Copper DTP LED stars & **unstabilized extruded `XT PMMA` shroud** (`MECH-TUBE-1`) | UV-A output depends on unstabilized acrylic; DTP safety requires electrically neutral thermal pads | Confirm vendor listings specify **electrically neutral thermal pads** on `20 mm` Copper DTP stars (mount with `16× M3` nylon insulating washers; check `pad-to-core = open`). Order **clear unstabilized extruded PMMA (`Plexiglas XT`, `Ø60 × 54 × 3.0 × 115 mm`)**—never UV-blocking cast `GS` or polycarbonate! Verify with a `365 nm` torch, never clean with IPA, and seal only with neutral-cure oxime silicone. |
| **N3** | **Deferred Choice** | 3D-print filament selection (`PETG` vs `Black ASA`) | Thermal design is verified safe for `75 °C` PETG (`T_pcb = 55.9 °C` @ `22 °C`, `63.9 °C` @ `30 °C` horiz nom); Black ASA adds `95 °C` HDT + UV-A stability | Print the 6 support-free parts in either PETG or Black ASA depending on workshop stock. |

## Resolved Engineering Blockers & Adversarial Review Campaigns

| ID | Status | Resolution |
|---|---|---|
| **B1** | **Resolved** | System **KiCad 9.0.8** generates, runs real-pin-type ERC (`0` violations) and DRC (`--schematic-parity --severity-all`, `0` violations, `0` unconnected, `0` parity), plots Gerbers/Excellon, and raytraces `driver_pcb` (`ENIG`, Emperor-moth `B.SilkS`). |
| **B2** | **Resolved** | Full automated verification toolchain (`ngspice`, `build123d`, `trimesh`, `pyvista`, `gerbv`, coupled thermal solver, BOM parity verifier) passes 100% on Rev 4.5 (`15/15` SPICE + `2,565` corners + `2,000` MC, `37/37` param + `6/6` watertight STLs + `75/75` kinematic + `156/156` B-Rep CAD incl. all `57` SMDs, `~603 g` FDM, `277 mm` tall, `£110.09` ex-VAT complete 1-off / `£103.14` net with workshop screws & paste). |
| **B3** | **Resolved** | Legacy `5 V` boost heat (`4.39 W`), bottom heatsink, CNC milling, custom `led_mcpcb` bare-SMD reflow, `MECH-PLUG-BOT`, and side housing penetrations eliminated across Rev 4.0–4.5. |
| **B4** | **Resolved** | All electrical review findings closed: `0.90 V` hysteretic `LM393B` UVLO, `40 V` `DMN4035L-7` + `33 V` `MF-MSMF110/33X` + unidirectional `SMBJ22A` + `CC1/CC2` & `J4` ESD diodes, `100 nF + 6.8 Ω` damped output shunts, gold `C&K 7211SYZBE` dry-circuit DPDT switch, isolated NPTH `H1..H4`, unbroken `B.Cu` power plane, and `Ø0.40 mm` `J1` drills. |
| **B5** | **Resolved** | All mechanical/weatherproofing review findings closed in Rev 4.5: downsized to `30 × 30 × 3 × 200 mm` bare core + `Ø60 × 54 × 115 mm` extruded `XT PMMA` (`-269 g`, `-82 mm`), horizontal `driver_pcb` bolted via `H1..H4` (`0` SMD collisions), radial bore/spigot O-rings (`±2.5 mm` cut-length tolerant), `9.0 × 7.5 mm` JST-XH wire channels, bottom `M20` IP68 split cable gland + captured `90°` USB-C PD cable, unbroken `25°` sloped conical rain roof, adhesive IP68 ePTFE breather vent, `D12` lightpipe, `24 AWG` UV silicone wire, and neutral-cure oxime silicone. |
