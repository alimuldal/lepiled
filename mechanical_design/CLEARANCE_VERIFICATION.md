# LepiLED DIY Maxi Switch — Mechanical Clearance & Verification Report (Rev 4.4)

All **41 parametric assertions** ([params.py](file:///home/alimuldal/src/lepiled/mechanical_design/cad/params.py)), **7 watertight support-free FDM STEP/STL exports** (`mech_base_ring`, `mech_lid_bot`, `mech_cap_bot`, `mech_cap_top`, `mech_plug_top`, `mech_plug_bot`, `mech_drill_jig`), overhang audits, **75-waypoint kinematic insertion sweeps** (`SW1`, vertical `driver_pcb` sliding into rails, `2× M3×16` CSK bolts, bottom USB-C plug), and **182 all-pairs B-Rep solid intersection checks** (`91` Nominal + `91` Worst-Case `151 mm` UVT PMMA shroud, including vertical `driver_pcb`, `8×` `20 mm` Copper DTP stars, `MECH-BASE-RING`, bottom-mounted `SW1` & `20 mm` USB-C grommet, standard `6.65 mm` USB-C plug, and all `M3` fasteners) ([generate_cad.py](file:///home/alimuldal/src/lepiled/mechanical_design/cad/generate_cad.py)) pass with **0.000000 mm³** interference ([cad_verification.json](file:///home/alimuldal/src/lepiled/mechanical_design/cad/cad_verification.json)).

## Key Verified Clearances & Checks (Rev 4.4)

| Check | Measured Value | Requirement | Status |
|---|---:|---:|:---:|
| Vertical `driver_pcb` corner / card-guide rail radial clearance inside `Ø61 mm` cavity | `10.603 / 7.380 mm` | `>= 5.0 / 3.0 mm` | PASS |
| Vertical `driver_pcb` upper corners to `42.75°` cone (axial plug stop) / `J2/J3` headroom | `1.212 / 13.505 mm` | `0.5–3.0 / >= 5.0 mm` | PASS |
| Bottom USB-C `20 mm` grommet panel thickness / overmold clearance above lid top | `2.50 / 1.90 mm` | `2.0–3.2 / >= 1.0 mm` | PASS |
| Standard `6.65 mm` USB-C plug exposed barrel at full `4.55 mm` upward mating | `2.100 mm` | `1.0 – 3.0 mm` | PASS |
| Bottom lid web between USB-C grommet and `SW1` pocket / outer lip-to-boot gap | `3.985 / 2.650 mm` | `>= 3.0 / 2.0 mm` | PASS |
| Bottom-mounted `SW1` clearance to mated `J4` header / radial clearance inside cavity | `7.865 / 7.395 mm` | `>= 5.0 / 5.0 mm` | PASS |
| `SW1` silicone boot clearance above flat ground inside `MECH-BASE-RING` | `3.000 mm` (`10.85 mm` radial access) | `>= 3.0 / 10.0 mm` | PASS |
| `MECH-BASE-RING` `Ø6.4 mm` bolt counterbore inner / outer wall | `3.00 / 2.60 mm` | `>= 2.5 mm` | PASS |
| Seamless `MECH-CAP-BOT` mid-body shell / waist-to-wire-slot wall | `5.00 / 8.50 mm` | `>= 4.0 mm` | PASS |
| `20 mm` Cu DTP star UV-to-Vis gap / LED & M3 clearance to UVT PMMA ID (`68 mm`) | `16.00 / 9.96 / 9.15 mm` | `>= 10.0 / >= 1.0 mm` | PASS |
| `MECH-CAP-TOP` `Ø116 mm` drip-brim radial overhang past base / `M3` lock above `G2` | `12.00 / 2.65 mm` | `>= 10.0 / >= 2.5 mm` | PASS |
| Protruding bare core length / `Ø8 mm` hang hole clearance below `MECH-PLUG-TOP` | `85.50 / 4.00 mm` | `60–100 / >= 3.0 mm` | PASS |
| UVT PMMA axial O-ring squeeze (`149–151 mm`) & gland fill | `10.0% / 24.3% / 38.6%` (`91.3%` fill) | `10–45%`, `<= 92%` | PASS |
| FDM off-bed `>46°` overhang (`6` parts = `0.000 mm²`; `cap_bot` = `0.178 mm²`) | `0.000 – 0.178 mm²` | `< 1.0 mm²` | PASS |
| Kinematic insertion (`SW1`, vertical `driver_pcb` rails, `2× M3×16` CSK, USB-C plug) | `0.000000 mm³` (`75` waypoints) | `0.000 mm³` | PASS |
| All-pairs B-Rep interference (`NOM` + `WC`, incl. vertical PCB, `base_ring`, `8×` stars) | `0 / 182` nonzero pairs (`91 + 91`) | `0` | PASS |
