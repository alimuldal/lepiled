# LepiLED DIY Maxi Switch — Mechanical Clearance & Verification Report (Rev 4.3)

All **46 parametric assertions** ([params.py](file:///home/alimuldal/src/lepiled/mechanical_design/cad/params.py)), **8 watertight support-free FDM STEP/STL exports** (`mech_base_ring`, `mech_lid_bot`, `mech_cap_bot`, `mech_cap_top`, `mech_plug_top`, `mech_rain_hat`, `mech_plug_bot`, `mech_drill_jig`), overhang audits, **3,363-ray `20 mm` grommet flange & USB-C tunnel STL ray-cast**, **60-waypoint kinematic insertion sweeps**, and **210 all-pairs B-Rep solid intersection checks** (`105` Nominal + `105` Worst-Case `151 mm` UVT PMMA shroud, including all `8×` `20 mm` Copper DTP stars, `MECH-BASE-RING`, `MECH-RAIN-HAT`, bottom-mounted `SW1`, all `M3` fasteners, `20 mm` rubber grommet, and standard `6.65 mm` USB-C plug) ([generate_cad.py](file:///home/alimuldal/src/lepiled/mechanical_design/cad/generate_cad.py)) pass with **0.000000 mm³** interference ([cad_verification.json](file:///home/alimuldal/src/lepiled/mechanical_design/cad/cad_verification.json)).

## Key Verified Clearances & Checks (Rev 4.3)

| Check | Measured Value | Requirement | Status |
|---|---:|---:|:---:|
| Driver PCB radial clearance / `MECH-LID-BOT` boss radial clearance | `2.099 / 3.799 mm` | `>= 1.0 / 2.0 mm` | PASS |
| Printed `Ø2.45 mm` PCB locating pin clearance inside `Ø2.7 mm` `H1..H4` | `0.250 mm` | `0.15 – 0.40 mm` | PASS |
| Open air below `driver_pcb` TH pins / headroom above JST-XH to `42.75°` cone | `16.20 / 7.822 mm` | `>= 3.0 / 5.0 mm` | PASS |
| Bottom-mounted `SW1` lugs below `driver_pcb` / clear of `J4` & `J2/J3` pins | `4.03 / 4.285 / 3.985 mm` | `>= 2.5 / 2.0 / 2.0 mm` | PASS |
| `SW1` silicone boot clearance above flat ground inside `MECH-BASE-RING` | `3.000 mm` (`18.85 mm` radial access) | `>= 3.0 / 10.0 mm` | PASS |
| `MECH-BASE-RING` `Ø6.4 mm` bolt counterbore inner / outer wall | `3.00 / 2.60 mm` | `>= 2.5 mm` | PASS |
| Contoured `MECH-CAP-BOT` mid-body shell / waist-to-wire-slot wall | `5.00 / 8.50 mm` | `>= 4.0 mm` | PASS |
| `20 mm` grommet panel thickness / wall above `G3` / back-lip above lid | `2.50 / 9.33 / 9.68 mm` | `>= 2.5 mm` | PASS |
| Standard `6.65 mm` USB-C plug exposed barrel at full `4.55 mm` mating | `2.100 mm` | `1.0 – 3.0 mm` | PASS |
| `20 mm` Cu DTP star UV-to-Vis gap / LED & M3 clearance to UVT PMMA ID (`68 mm`) | `16.00 / 9.96 / 9.15 mm` | `>= 10.0 / >= 1.0 mm` | PASS |
| `MECH-CAP-TOP` drip-brim radial overhang beyond `cap_bot` / `M3` lock above `G2` | `8.00 / 2.65 mm` | `>= 6.0 / >= 2.5 mm` | PASS |
| Protruding bare core length / `Ø8 mm` hang hole below `plug_top` & `rain_hat` collar | `85.50 / 4.00 / 12.55 mm` | `60–100 / >= 3.0 / >= 8.0 mm` | PASS |
| UVT PMMA axial O-ring squeeze (`149–151 mm`) & gland fill | `10.0% / 24.3% / 38.6%` (`91.3%` fill) | `10–45%`, `<= 92%` | PASS |
| FDM off-bed `>46°` overhang (`7` parts = `0.000 mm²`; `cap_bot` = `0.787 mm²`) | `0.000 – 0.787 mm²` | `< 1.0 mm²` | PASS |
| USB-C & `20 mm` grommet flange STL ray-cast (`3,363` rays) | `0` anomalies, `min_wall = 2.500 mm` | `>= 2.5 mm` | PASS |
| Kinematic insertion (`SW1` into `lid_bot`, `2× M3×16` CSK, USB-C plug) | `0.000000 mm³` (`60` waypoints) | `0.000 mm³` | PASS |
| All-pairs B-Rep interference (`NOM` + `WC`, incl. `base_ring`, `rain_hat`, `8×` stars) | `0 / 210` nonzero pairs (`105 + 105`) | `0` | PASS |
