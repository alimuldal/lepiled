# LepiLED DIY Maxi Switch — Mechanical & Thermal Design (Rev 4.5 — Compact, Horizontal PCB, Radial O-Rings & Weatherproof Split Gland)

## 1. Architecture Summary

Rev 4.5 addresses every P0/P1 finding from the independent Rev 4.4 mechanical critical review ([mech_review_carbon.md](file:///home/alimuldal/.gemini/antigravity-cli/brain/c78b6e5e-2450-404f-9915-887b1c7650b6/mech_review_carbon.md) & [mech_review_opus.md](file:///home/alimuldal/.gemini/antigravity-cli/brain/c78b6e5e-2450-404f-9915-887b1c7650b6/mech_review_opus.md)), cutting lamp mass by **`-268.6 g`** (`602.6 g` FDM) and total height by **`-81.5 mm`** (`277.0 mm`):

- **Compact `30 × 30 × 3.0 mm × 200 mm` Bare Al Core (`174 g`) & Clear Extruded `XT PMMA` Shroud (`73 g`):** Retains the robust `3.0 mm` Al wall for full 6-turn `M3` star threads (`16× M3 × 8 mm` pan screws + nylon washers) while shrinking the shroud to `Ø60 × 54 × 3.0 × 115 mm` clear unstabilized extruded PMMA (`Plexiglas XT`, `85–92%` @ `365 nm`). `MECH-PLUG-BOT` is eliminated completely—the core locks directly into `MECH-CAP-BOT`'s `12 mm` square collar below the shroud seal via `2× M3 × 10 mm` radial SHCS screws, with `2× 9.0 × 7.5 mm` wire channels passing pre-crimped 2-pin JST-XH plugs straight through without de-pinning.
- **Low-Force Radial Bore/Spigot O-Ring Seals (`±2.5 mm` Cut-Length Tolerant):** Replaces the Rev 4.4 axial face seals (`700–2,000 N` preload) with self-supporting `45°`-ramped radial O-ring grooves: `MECH-GASKET-1/2` (`60 × 3.0 mm` VMQ70 on `Ø60 mm` PMMA OD, `20.0%` nom / `13.3–26.7%` squeeze, `~30 N` hand push) and `MECH-GASKET-3` (`70 × 2.5 mm` VMQ70 on `MECH-LID-BOT`'s `7 mm` spigot, `14.0%` squeeze).
- **Horizontal `driver_pcb` + Bottom `M20` Split Waterproof Cable Gland + Bottom `SW1`:** Unchanged `36 × 46 mm` `driver_pcb` bolts horizontally (SMD/JST side **down** for easy field access) onto `4× Ø5.5 mm` bulkhead standoffs inside seamless `MECH-CAP-BOT` via `H1..H4` (`4× M2.5 × 8 mm` screws; verified against **all 57 SMDs** parsed from [driver_pcb_cpl.csv](file:///home/alimuldal/src/lepiled/pcb_design/driver_pcb_cpl.csv)). A permanently captured `90°` USB-C PD cable exits straight down through an `M20` IP68 split cable gland (`MECH-GLAND-1`, clears intact USB-C plug and seals watertight around the round jacket) beside bottom-mounted `SW1` (`C&K 7211SYZBE` + `759D02000` boot), shielded inside `MECH-BASE-RING` (`Ø94.4 × 71.6 × 20 mm`). `MECH-LID-BOT` also integrates an adhesive `Ø8 mm` IP68 ePTFE breather vent (`MECH-VENT-1`) and a `Ø2.5 mm` clear `D12` PD-status lightpipe.
- **Unbroken `25°` Sloped Conical Rain Roof (`MECH-CAP-TOP`):** `Ø88 mm` sloped roof (`0.000 mm²` overhang upright) sheds rain off the core exit immediately (zero water pooling) with `2× M3 × 10 mm` radial locking screws tucked cleanly beneath the rim and `56.8 mm` of protruding Al core + unobstructed `Ø8 mm` hanging hole above.

### Verified Mass Budget (From B-Rep Volumes in [cad_verification.json](file:///home/alimuldal/src/lepiled/mechanical_design/cad/cad_verification.json))

| Component | Rev 4.4 (FDM 60%) | Rev 4.5 (FDM 60% — 4 walls / 25% infill) | Rev 4.5 (100% Solid PETG) |
|---|---:|---:|---:|
| **3D-Printed Lamp Parts (`5` lamp parts — `MECH-PLUG-BOT` deleted)** | `340.6 g` (`447.0 cm³`) | **`240.8 g`** (`316.0 cm³`) | `401.3 g` |
| **Bare Al 6063-T6 Core (`30×30×3 × 200 mm` vs `40×40×3 × 250 mm`)** | `298.5 g` | **`173.9 g`** | `173.9 g` |
| **Transparent Shroud (`Ø60×54×115 mm` XT PMMA vs `Ø75×69×150 mm`)** | `120.1 g` | **`72.9 g`** | `72.9 g` |
| **`8×` Cu DTP Stars (`34 g`), PCB, SW1, M20 Split Gland, O-Rings & Screws** | `112.0 g` | **`115.0 g`** | `115.0 g` |
| **TOTAL LAMP WEIGHT (HEIGHT)** | **`871.2 g` (`358.5 mm`)** | **`602.6 g` (`277.0 mm` — `-269 g`, `-82 mm`!)** | `763.1 g` |

## 2. Coupled Thermal Verification ([thermal_summary.json](file:///home/alimuldal/src/lepiled/mechanical_design/thermal/thermal_summary.json))

Executed via [thermal_analysis.py](file:///home/alimuldal/src/lepiled/mechanical_design/thermal/thermal_analysis.py) modeling `20 mm` Copper DTP stars (`R_sub = 0.50 K/W`, `R_tim = 0.30 K/W`), the **`56.8 mm` bare mill-finish (`ε = 0.20`) protruding `30 × 30 × 3 mm` core**, `Ø60 × 54 × 3.0 mm` **XT PMMA shroud** (`k = 0.19 W/(m·K)`, `ε = 0.93`), and sealed bottom electronics bay (`75 °C` conservative PETG limit; `95 °C` if printed in ASA):

| Ambient & Case | Mode | `T_core` (°C) | `T_j,UV` (°C) (`<=100`) | `T_shroud` (°C) (`<=75`) | `T_PCB` (°C) (`<=75` PETG) | Status |
|---|---|---:|---:|---:|---:|:---:|
| `22 °C` Vertical (UK Night) | `4-UV Nom` | `49.7` | `51.3` | `29.7` | `42.0` | PASS |
| `22 °C` Vertical (UK Night) | `8-ALL Nom (40%UV)` | `67.5` | `69.1` | `35.2` | `55.9` | PASS |
| `22 °C` Horizontal | `8-ALL DS-RealWPE` | `79.8` | `81.9` | `39.4` | `67.4` | PASS |
| `30 °C` Vertical | `8-ALL Nom (40%UV)` | `75.1` | `76.7` | `42.9` | `63.7` | PASS |
| `30 °C` Horizontal | `8-ALL Nom (40%UV)` | `75.5` | `77.1` | `43.7` | `63.9` | PASS |
| `30 °C` Vertical | `8-ALL DS-RealWPE` | `86.2` | `88.3` | `46.4` | `74.7` | PASS |
| `35 °C` Horizontal | `8-ALL Nom (40%UV)` | `80.0` | `81.7` | `48.5` | `68.7` | PASS |
| *Optional Matte-Black Top (`30 °C` Horiz)* | *`8-ALL Nom / DS-RealWPE`* | *`~66 / 77`* | *`~68 / 79`* | *`~41 / 45`* | *`~58 / 68`* | *PASS* |

**Thermal Takeaway:** On typical `15–22 °C` UK nights, the compact bare `30 × 30 × 3 mm` core runs at `69.1 °C` UV junction (`31 °C` below the `100 °C` `SST-10-UV` limit) and `55.9 °C` PCB (`19 °C` below PETG's `75 °C` softening limit), and stays safe for PETG in nominal operation all the way up to `35 °C` horizontal (`T_PCB = 68.7 °C`). For sustained hot-climate (`30–35 °C`) worst-case operation, either printing in Black ASA (`95 °C` HDT) or spraying just the `56.8 mm` protruding core top matte-black (`ε = 0.88`) adds another `~9–10 °C` of thermal headroom.

## 3. CAD Artifacts & Plots

- **Parameters & Generator:** [params.py](file:///home/alimuldal/src/lepiled/mechanical_design/cad/params.py), [generate_cad.py](file:///home/alimuldal/src/lepiled/mechanical_design/cad/generate_cad.py), [cad_verification.json](file:///home/alimuldal/src/lepiled/mechanical_design/cad/cad_verification.json)
- **6 Support-Free 3D-Printable Parts (FDM PETG/ASA):** [mech_base_ring.step](file:///home/alimuldal/src/lepiled/mechanical_design/cad/mech_base_ring.step), [mech_lid_bot.step](file:///home/alimuldal/src/lepiled/mechanical_design/cad/mech_lid_bot.step), [mech_cap_bot.step](file:///home/alimuldal/src/lepiled/mechanical_design/cad/mech_cap_bot.step), [mech_cap_top.step](file:///home/alimuldal/src/lepiled/mechanical_design/cad/mech_cap_top.step), [mech_plug_top.step](file:///home/alimuldal/src/lepiled/mechanical_design/cad/mech_plug_top.step), [mech_drill_jig.step](file:///home/alimuldal/src/lepiled/mechanical_design/cad/mech_drill_jig.step), [lepiled_assembly.step](file:///home/alimuldal/src/lepiled/mechanical_design/cad/lepiled_assembly.step)
- **CAD Renders & Thermal Plots:** [assembly_iso.png](file:///home/alimuldal/src/lepiled/mechanical_design/cad/assembly_iso.png), [assembly_section_xz.png](file:///home/alimuldal/src/lepiled/mechanical_design/cad/assembly_section_xz.png), [assembly_section_yz.png](file:///home/alimuldal/src/lepiled/mechanical_design/cad/assembly_section_yz.png), [lid_bot_detail.png](file:///home/alimuldal/src/lepiled/mechanical_design/cad/lid_bot_detail.png), [cap_bot_detail.png](file:///home/alimuldal/src/lepiled/mechanical_design/cad/cap_bot_detail.png), [cap_top_detail.png](file:///home/alimuldal/src/lepiled/mechanical_design/cad/cap_top_detail.png), [thermal_margins.png](file:///home/alimuldal/src/lepiled/mechanical_design/thermal/thermal_margins.png), [thermal_ambient_sweep.png](file:///home/alimuldal/src/lepiled/mechanical_design/thermal/thermal_ambient_sweep.png), [thermal_network_comparison.png](file:///home/alimuldal/src/lepiled/mechanical_design/thermal/thermal_network_comparison.png)
