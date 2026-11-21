# LepiLED DIY Maxi Switch — Mechanical Clearance & Verification Report

All `50` parametric assertions ([params.py](cad/params.py)), `6` watertight support-free FDM STEP/STL exports (`mech_cap_bot`, `mech_top_base`, `mech_cap_top`, `mech_plug_top`, pre-mirrored L+R `mech_cable_clamp`, and `mech_drill_jig`), overhang audits (`0.000–0.005 mm²` `>46°` across all geometry outside the intentional `2.5 mm`-deep round `Ø6.50 mm` `SW1` boot-seal bore), `5` ray-cast wall-integrity and vent-openness gates, `3` fastener-seat bearing and intact 4-wall core-socket checks, `92`-waypoint kinematic insertion sweeps (`SW1` horizontal, `MECH-CAP-TOP` straight down over wired PCB and core, pre-crimped JST-XH plugs up through `±Y` slots, intact straight USB-C plug outward through `+Y` `45°`-gable port, and `18.0 mm` `90°` USB-C plug mating vertically into `J1`), and `240` all-pairs B-Rep solid intersection checks (`120` Nominal + `120` Worst-Case `30.4 mm` Al core, `Ø60.6 mm` oval & `+2.0 mm` XT PMMA shroud, including paracord hanging loop, `2.0 m` drip-loop USB-C cable, all `6` `M3 × 5.0 × 4.2 mm` brass inserts, all `4` captive DIN 934 `M3` hex nuts, the `15 × 15 mm` silicone-pad/brass-shim PCB thermal bridge, all `10` `M3` screws, both `M4 × 50 mm` A2 stainless cross-bolts, all `48` populated SMDs from `driver_pcb.kicad_pcb`, `8` epoxy-bonded `20 mm` copper DTP stars, `SW1` with silicone boot, and the `18.0 mm` `90°` USB-C plug + `7.0 mm` strain relief) ([generate_cad.py](cad/generate_cad.py)) pass with `0.000000 mm³` interference ([cad_verification.json](cad/cad_verification.json)).

## Verified Clearances & Automated Gates

| Check | Measured Value | Requirement | Status |
|---|---:|---:|:---:|
| Bottom nosecone height / tip OD / cone slope / visible LED from tip | `34.0 / Ø40.0 mm` / `45.0°` / `60.0 mm` | `<= 35 / 42 mm` / `<= 46°` / `<= 65 mm` | **PASS** |
| Nosecone core-socket corner wall (`Z = 6 mm`) / shroud collar O-ring outer wall | `4.009 / 2.800 mm` | `>= 2.5 / 2.5 mm` | **PASS** |
| Open chimney inlet area (`22 × 22 mm`, `R3`) / bottom `M4` Al edge distance | `4.76 cm²` / `4.250 mm` | `>= 4.0 cm²` / `>= 4.0 mm` | **PASS** |
| Vertical `driver_pcb` (`+X` face) radial clr in `Ø85.0 mm` bell (`F.Cu` / `L1,L2` / JST wire bend) | `13.997 / 11.145 / 10.179 mm` | `>= 8.0 / 6.0 / 6.5 mm` | **PASS** |
| Vertical `driver_pcb` `B.Cu` TH pins air gap to `1.5 mm` baffle / captive M3 nut walls (`back / front`) | `1.650 / 1.000 / 1.350 mm` | `>= 1.2 / 0.8 / 1.2 mm` | **PASS** |
| Captive `15.6 × 15.6 mm` thermal-bridge gap (`WC / nom`) / `90°` USB-C plug to baffle clearance | `5.300 (5.500 nom) / 2.680 mm` | `4.5–6.0 / >= 1.5 mm` | **PASS** |
| Mated `J2/J3` & PCB top edge below `MECH-CAP-TOP` internal `Circle→Square` ceiling loft | `8.782 / 12.497 mm` | `>= 4.0 / 6.0 mm` | **PASS** |
| `18.0 mm` `90°` USB-C plug above bay floor / clamp axial standoff travel / grommet chamber | `8.320 / 1.200 / 10.50 mm` | `>= 6.0 / 1.0 / 10.0 mm` | **PASS** |
| Blind `+Y` `M3×5.0` clamp insert dry-bay wall / clamp inside `Ø118 mm` eaves / top below eaves | `4.030 / 4.800 / 4.500 mm` | `>= 2.5 / 3.5 / 4.0 mm` | **PASS** |
| `SW1` lugs clr to worst-case Al core / boot inside `-X` rain visor (`18.6 mm` max) / ring Z wall | `8.330 / 3.400 / 4.785 mm` | `>= 7.0 / 2.5 / 3.0 mm` | **PASS** |
| `4×` eaves `M3×5.0` insert walls (`to G3 groove / outer` at `R=51.0 mm`) & ear CSK outer rim | `2.000 / 6.000 / 2.250 mm` | `>= 1.8 / 4.0 / 2.0 mm` | **PASS** |
| Ray-Cast Gate: `MECH-CAP-TOP` lofted rain roof (`432` rays) | `0 breaches` | `0` | **PASS** |
| Ray-Cast Gate: `MECH-CAP-TOP` outer vertical bell wall incl. `D12` `0.60 mm` dimple (`324` rays) | `0 breaches` | `0` | **PASS** |
| Ray-Cast Gate: `MECH-CAP-TOP` upper chimney collar zero side holes (`72` rays) | `0 breaches` | `0` | **PASS** |
| Ray-Cast Gate: `MECH-TOP-BASE` blind `+Y` `M3×5.0` clamp insert dry-bay seal (`2` inserts) | `2 / 2 sealed` | `2 / 2` | **PASS** |
| Ray-Cast Gate: `MECH-TOP-BASE` `-Y` `35°` downward breather bore through-drain check | `0 axis ray hits` | `0` (open) | **PASS** |
| Fastener-seat bearing (`cap_bot` `M4` cross-bolt spotfaces / `top_base` `4×` ear `M3` CSK) | `96.4% / 100.0%` | `>= 90.0%` | **PASS** |
| Intact 4-wall `31.1 × 31.1 mm` core sockets (`cap_bot` / `top_base` / `cap_top`) | `True / True / True` | `True` | **PASS** |
| Core hub corner wall / `MECH-CAP-TOP` vertical collar wall | `2.509 / 4.650 mm` | `>= 2.2 / 4.0 mm` | **PASS** |
| Core corner / UV LED / `±Y` wire-slot radial clr to XT PMMA ID (`53.5 mm` min) | `5.254 / 7.870 / 3.265 mm` | `>= 5.0 / 7.0 / 2.5 mm` | **PASS** |
| Epoxy-bonded `Ø20 mm` stars: UV-to-Vis edge gap / UV below top rim / Vis above bot rim | `14.0 / 16.0 / 16.0 mm` | `>= 10.0 / 12.0 / 12.0 mm` | **PASS** |
| Shroud radial O-rings (`60 × 3.5 mm` VMQ50/60 on `59.2–60.6 mm` oval PMMA) & short-tube margin | `11.4–31.4%` (`69.7%` fill) / `2.90 mm` | `10–33%`, `<= 85%`, `>= 2.0 mm` | **PASS** |
| Top rain-bell bolt-compressed axial face O-ring (`88 × 2.5 mm` VMQ50 on `Z = 171 mm` deck) | `24.8%` (`76.8%` fill) | `18–30%`, `<= 85%` | **PASS** |
| Chimney protrusion / rain roof slope / finial exhaust area & hood overhang / top `M4` Al edge | `49.0 mm` / `30.6°` / `5.18 cm²` / `6.0 mm` / `13.75 mm` | `45–75 mm` / `>= 24°` / `>= 4.5 cm²` / `>= 5.0 mm` / `>= 10.0 mm` | **PASS** |
| FDM `>46°` overhang (`4` parts = `0.000 mm²`; `cap_top` = `0.005 mm²`; `top_base` outside `SW1` bore = `0.000 mm²`) | `0.000–0.005 mm²` (`12.407 mm²` on round `Ø6.50 mm` `SW1` bore arc) | `<= 1.0 mm²` outside `SW1` bore | **PASS** |
| Kinematic insertion (`SW1`, bell down, `±Y` JST slots, `+Y` straight plug, `18 mm` `90°` plug→`J1`) | `0.000000 mm³` (`92` waypoints) | `0.000 mm³` | **PASS** |
| All-pairs B-Rep (`NOM` + `WC`, incl. paracord, cable, 6 inserts, 4 M3 hex nuts, thermal bridge, screws, 48 SMDs & USB-C) | `0 / 240` nonzero pairs (`120 + 120`) | `0` | **PASS** |
