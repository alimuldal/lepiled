# LepiLED DIY Maxi Switch — Mechanical Clearance & Verification Report

All `57` parametric assertions ([params.py](cad/params.py)), `6` print-ready (`Z = 0`, `+Z` up) watertight support-free FDM STEP/STL exports (`mech_cap_bot`, `mech_top_base`, `mech_cap_top`, pre-flipped `mech_plug_top` + breakaway-tabbed bail spools, pre-mirrored L+R `mech_cable_clamp`, and ASA-tolerant `mech_drill_jig`), overhang audits (`0.000–0.005 mm²` `>46°` across all geometry outside the intentional `2.5 mm`-deep round `Ø6.50 mm` `SW1` boot-seal bore and `0.50 mm` debossed visor legend), `7` ray-cast wall-integrity, bulkhead, and dimple gates, `3` fastener-seat bearing and intact 4-wall core-socket checks, `124`-waypoint kinematic insertion sweeps (`SW1` horizontal, `MECH-CAP-TOP` straight down over wired PCB and core, pre-crimped JST-XH plugs up through `±Y` slots, intact straight USB-C plug outward through `+Y` `45°`-gable port, `24.4 mm` StarTech `90°` USB-C plug mating vertically into `J1`, and all `4×` `M3 × 12` CSK bolts ascending from below through open outward radial U-slot diagonal ear tunnels), and `240` all-pairs B-Rep solid intersection checks (`120` Nominal + `120` Worst-Case `30.4 mm` Al core, `Ø60.6 mm` oval & `+2.0 mm` XT PMMA shroud, including bent wire hanging bail, `2.0 m` drip-loop `Ø2.8 mm` TPE USB-C cable, all `6` `M3 × 5.0 × 4.2 mm` brass inserts, all `4` captive DIN 934 `M3` hex nuts, the `15 × 15 mm` silicone-pad/brass-shim PCB thermal bridge, all `10` `M3` screws with exact washer stacks, both `DIN 912 M4 × 50 mm` A2 stainless SHCS cross-bolts + captive hex nyloc nut, all `48` populated SMDs from `driver_pcb.kicad_pcb`, `8` epoxy-bonded `20 mm` copper DTP stars, `SW1` with silicone boot, and the measured `24.4 mm` (`22.3 + 2.1 mm`) StarTech `90°` USB-C plug + `14.4 × Ø5.0 mm` strain relief) ([generate_cad.py](cad/generate_cad.py)) pass with `0.000000 mm³` interference ([cad_verification.json](cad/cad_verification.json)).

## Verified Clearances & Automated Gates

| Check | Measured Value | Requirement | Status |
|---|---:|---:|:---:|
| Bottom nosecone height / tip OD / cone slope / visible LED from tip | `34.0 / Ø40.0 mm` / `44.45°` / `60.0 mm` | `<= 35 / 42 mm` / `<= 46°` / `<= 65 mm` | **PASS** |
| Nosecone core-socket corner wall / bottom hub V-groove corner wall / collar O-ring outer wall | `2.914 / 2.242 / 2.800 mm` | `>= 2.5 / 2.0 / 2.5 mm` | **PASS** |
| Open chimney inlet area (`22 × 22 mm`, `R3`) / bottom `M4` Al edge distance | `4.76 cm²` / `4.250 mm` | `>= 4.0 cm²` / `>= 4.0 mm` | **PASS** |
| Optional bottom mesh pocket (`28.0 × 28.0 × 1.0 mm`, `R4.5`): min landing shelf / WC flat core seat at `Z = 5.0 mm` | `3.000 / 0.450 mm` (`2.44 mm` corners) | `>= 2.5 / >= 0.40 mm` | **PASS** |
| Vertical `driver_pcb` (`+X` face) radial clr in `Ø85.0 mm` bell (`F.Cu` / `L1,L2` / JST wire bend) | `13.686 / 10.805 / 9.784 mm` | `>= 8.0 / 6.0 / 6.5 mm` | **PASS** |
| Vertical `driver_pcb` `B.Cu` TH pins air gap / captive M3 nut walls (`back / front`) / `M3×8` screw tip clr | `2.050 / 1.000 / 1.650 / 0.850 mm` | `>= 1.2 / 0.8 / 1.2 / 0.5 mm` | **PASS** |
| Captive `15.6 × 15.6 mm` thermal-bridge gap (`WC / nom`) / `90°` USB-C plug to baffle clearance | `5.700 (5.900 nom) / 3.080 mm` | `4.5–6.0 / >= 1.5 mm` | **PASS** |
| Mated `J2/J3` & PCB top edge below `MECH-CAP-TOP` internal `Circle→Square` ceiling loft | `4.096 / 7.886 mm` | `>= 4.0 / 6.0 mm` | **PASS** |
| `24.4 mm` StarTech `90°` USB-C plug above bay floor / clamp standoff travel / grommet fill (`Ø7.4×10.2 mm`) | `6.220 / 1.200 mm` / `80.2%` | `>= 6.0 / 1.0 mm` / `<= 85%` | **PASS** |
| Blind `+Y` clamp insert wall (`7.0 mm` bore) / `M3×12` closed bottom clr / inside eaves / below eaves | `3.000 / 1.500 / 4.800 / 4.500 mm` | `>= 2.5 / 0.8 / 3.5 / 4.0 mm` | **PASS** |
| `SW1` lugs clr to worst-case Al core / boot inside `-X` rain visor / cove boot top clr / ring Z wall | `8.330 / 3.400 / 1.200 / 3.285 mm` | `>= 7.0 / 2.5 / 1.0 / 3.0 mm` | **PASS** |
| `4×` eaves `M3×5.0` insert walls (`to G3 groove / outer` at `R=51.0 mm`) & ear CSK outer rim | `1.900 / 6.000 / 2.250 mm` | `>= 1.8 / 4.0 / 2.0 mm` | **PASS** |
| Ray-Cast Gate: `MECH-CAP-TOP` lofted rain roof (`432` rays) | `0 breaches` | `0` | **PASS** |
| Ray-Cast Gate: `MECH-CAP-TOP` outer bell wall (`324` rays) & `D12` normal dimple skin at `Z = 195.2 mm` | `0 breaches` / `0.900 mm` | `0` / `0.80–1.15 mm` | **PASS** |
| Ray-Cast Gate: `MECH-CAP-TOP` upper chimney collar zero side holes (`72` rays) | `0 breaches` | `0` | **PASS** |
| Ray-Cast Gate: `MECH-TOP-BASE` blind `+Y` `M3×5.0` clamp insert dry-bay seal (`2` inserts) | `2 / 2 sealed` | `2 / 2` | **PASS** |
| Ray-Cast Gate: `MECH-TOP-BASE` `-Y` `35°` downward breather bore through-drain check | `0 axis ray hits` | `0` (open) | **PASS** |
| Ray-Cast Gate: `MECH-CAP-BOT` solid waterproof bulkhead above `±X` `M4` SHCS / captive-hex pockets | `2.150 mm` | `>= 1.80 mm` | **PASS** |
| Fastener-seat bearing (`cap_bot` `M4` SHCS & captive hex pockets / `top_base` `4×` ear `M3` CSK) | `94.4% / 100.0%` | `>= 90.0%` | **PASS** |
| Intact 4-wall `31.1 × 31.1 mm` core sockets (`cap_bot` / `top_base` / `cap_top`) | `True / True / True` | `True` | **PASS** |
| Core hub corner wall / `MECH-CAP-TOP` vertical collar wall | `2.509 / 4.650 mm` | `>= 2.2 / 4.0 mm` | **PASS** |
| Core corner / UV LED / `±Y` wire-slot radial clr to XT PMMA ID (`53.5 mm` min) | `5.254 / 7.870 / 4.246 mm` | `>= 5.0 / 7.0 / 2.5 mm` | **PASS** |
| Epoxy-bonded `Ø20 mm` stars: UV-to-Vis edge gap / UV below top rim / Vis above bot rim | `14.0 / 16.0 / 16.0 mm` | `>= 10.0 / 12.0 / 12.0 mm` | **PASS** |
| Shroud radial O-rings (`BS229` `59.92 × 3.53 mm` VMQ 70A on `59.2–60.6 mm` oval PMMA) & short-tube margin | `12.2–32.0%` (`70.9%` fill) / `2.90 mm` | `10–33%`, `<= 85%`, `>= 2.0 mm` | **PASS** |
| Top rain-bell bolt-compressed axial face O-ring (`BS153` `88.57 × 2.62 mm` VMQ 70A, `3.60 × 2.20 mm` groove) | `16.0%` (`68.1%` fill) | `15–30%`, `<= 85%` | **PASS** |
| Chimney protrusion / rain roof slope / finial exhaust area & hood overhang / top `M4` Al edge | `48.0 mm` / `45.0°` / `5.18 cm²` / `6.0 mm` / `13.75 mm` | `45–75 mm` / `>= 24°` / `>= 4.5 cm²` / `>= 5.0 mm` / `>= 10.0 mm` | **PASS** |
| FDM `>46°` overhang (`4` parts = `0.000 mm²`; outside intentional `SW1` bore & visor legend = `<= 0.005 mm²`) | `0.000–0.005 mm²` outside `SW1` bore (`12.5 mm²`) & `0.5 mm` debossed legend | `<= 1.0 mm²` outside allowed features | **PASS** |
| Kinematic insertion (`SW1`, bell down, `±Y` JST slots, `+Y` straight plug, `90°` plug→`J1`, `4×` ear CSK bolts) | `0.000000 mm³` (`124` waypoints) | `0.000 mm³` | **PASS** |
| All-pairs B-Rep (`NOM` + `WC`, incl. wire bail, cable, 6 inserts, 4 M3 hex nuts, thermal bridge, screws, 48 SMDs & USB-C) | `0 / 240` nonzero pairs (`120 + 120`) | `0` | **PASS** |
