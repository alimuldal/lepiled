# LepiLED DIY Maxi Switch — Mechanical Clearance & Verification Report (Rev 4.2)

All **36 parametric assertions** ([params.py](file:///home/alimuldal/src/lepiled/mechanical_design/cad/params.py)), **6 watertight support-free FDM STEP/STL exports** (`mech_lid_bot`, `mech_cap_bot`, `mech_cap_top`, `mech_plug_top`, `mech_plug_bot`, `mech_drill_jig`), overhang audits, **3,249-ray `20 mm` grommet flange & USB-C tunnel STL ray-cast**, **72-waypoint kinematic insertion sweeps**, and **156 all-pairs B-Rep solid intersection checks** (`78` Nominal + `78` Worst-Case `151 mm` glass, including all `8×` `20 mm` Copper DTP stars, all `M3` fasteners, `20 mm` rubber grommet, and standard `6.65 mm` USB-C plug) ([generate_cad.py](file:///home/alimuldal/src/lepiled/mechanical_design/cad/generate_cad.py)) pass with **0.000000 mm³** interference ([cad_verification.json](file:///home/alimuldal/src/lepiled/mechanical_design/cad/cad_verification.json)).

## Key Verified Clearances & Checks (Rev 4.2)

| Check | Measured Value | Requirement | Status |
|---|---:|---:|:---:|
| Driver PCB radial clearance / `MECH-LID-BOT` boss radial clearance | `2.099 / 3.799 mm` | `>= 1.0 / 2.0 mm` | PASS |
| Printed `Ø2.45 mm` PCB locating pin clearance inside `Ø2.7 mm` `H1..H4` | `0.250 mm` | `0.15 – 0.40 mm` | PASS |
| Open air below `driver_pcb` through-hole pins / headroom above JST-XH | `9.700 / 8.979 mm` | `>= 3.0 / 5.0 mm` | PASS |
| Captive `M3` hex-nut pocket wall above `MECH-GASKET-3` | `2.950 mm` | `>= 2.5 mm` | PASS |
| `20 mm` grommet panel thickness / wall above `G3` / back-lip above lid | `2.50 / 2.83 / 3.18 mm` | `>= 2.5 mm` | PASS |
| Standard `6.65 mm` USB-C plug exposed barrel at full `4.55 mm` mating | `2.100 mm` | `1.0 – 3.0 mm` | PASS |
| `C&K 7211` wall window / radial to PCB / Z above SMD | `2.50 / 4.53 / 2.385 mm` | `2.0–3.5 / >= 1.0 / >= 2.0 mm` | PASS |
| `20 mm` Cu DTP star UV-to-Vis vertical gap / radial LED & M3 clearance to glass ID | `16.00 / 9.21 / 8.40 mm` | `>= 10.0 / >= 1.0 mm` | PASS |
| `MECH-CAP-TOP` horizontal `M3` lock bore wall above `MECH-GASKET-2` | `4.150 mm` | `>= 2.5 mm` | PASS |
| Protruding bare core length / `Ø8 mm` hang hole clearance below `MECH-PLUG-TOP` | `85.50 / 4.00 mm` | `60–100 / >= 3.0 mm` | PASS |
| Glass axial O-ring squeeze (`149–151 mm` glass) & gland fill | `10.0% / 24.3% / 38.6%` (`91.3%` fill) | `10–45%`, `<= 92%` | PASS |
| FDM off-bed `>46°` overhang (`lid_bot`/`cap_bot`/`cap_top`/`plug_top`/`plug_bot`/`jig`) | `0.00 / 0.39 / 0.00 / 0.00 / 0.00 / 0.00 mm²` | `< 1.0 mm²` | PASS |
| USB-C & `20 mm` grommet flange STL ray-cast (`3,249` rays) | `0` anomalies, `min_wall = 2.500 mm` | `>= 2.5 mm` | PASS |
| Kinematic insertion (`C&K 7211`, `2× M3×16` CSK, USB-C plug) | `0.000000 mm³` (`72` waypoints) | `0.000 mm³` | PASS |
| All-pairs B-Rep interference (`NOM` + `WC`, incl. `8×` Cu stars & all `M3` bolts) | `0 / 156` nonzero pairs (`78 + 78`) | `0` | PASS |
