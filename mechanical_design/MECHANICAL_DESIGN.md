# LepiLED DIY Maxi Switch — Mechanical & Thermal Design (Rev 4.4 — Vertical PCB, Bottom USB-C & Seamless Weatherproof Housing)

## 1. Architecture Summary

Rev 4.4 delivers a completely seamless, weatherproof, portable hobby enclosure built around the unchanged `driver_pcb`, `8×` pre-mounted `20 mm` Copper DTP LED stars, and `250 mm` bare `40 × 40 × 3.0 mm` Al 6063 core:

- **Vertical `driver_pcb` + Bottom-Entry USB-C Power (`0` Side Holes, `0°` Cable Tilt):** Stands the unchanged `36 × 46 mm` `driver_pcb` vertically inside `2×` integral card-guide rails on `MECH-LID-BOT` (`Y_front = -6.88 mm`, `J2/J3` at the top right under the core wire slots, upper corners captured `1.21 mm` beneath the `42.75°` cavity cone for rock-solid axial plug support). `J1` USB-C points straight downward through the `20 mm` rubber membrane grommet seated flat in `MECH-LID-BOT` (`X = 0, Y = -5.0 mm`), eliminating side cable tilt when hanging and removing **every** side penetration from `MECH-CAP-BOT`.
- **Bottom-Mounted Toggle Switch (`SW1`) + Bolt-On Protective Base Stand Ring (`MECH-BASE-RING`):** Mounts `C&K 7211SYZBE` + `759D02000` silicone boot vertically beside the USB-C grommet on `MECH-LID-BOT` (`X = 0, Y = +16.5 mm`, `3.99 mm` solid lid web from the grommet and `7.87 mm` clear of `J4`). A bolt-on support-free standing ring (`MECH-BASE-RING`, `Ø92 × 68 × 18 mm`, `4×` wide `22 × 7.5 mm` drainage/90°-cable cutouts) clamps with the exact same `4× M3 × 16 mm` SHCS lid bolts, shielding the silicone switch boot by `3.0 mm` above flat ground.
- **Shatter-Resistant UV-Transmitting PMMA Shroud (`MECH-TUBE-1`):** `120 g` UV-transmitting cast PMMA cylinder (`Ø75.0 × 69.0 × 3.0 mm × 150 mm`, `85–92%` @ `365 nm`) on standard `68 × 3.5 mm` VMQ70 silicone O-rings (`-143 g` and shatter-resistant vs borosilicate; never substitute polycarbonate).
- **Integral `Ø116 mm` Drip-Brim on `MECH-CAP-TOP` (Unobstructed Hanging Hole):** `3.8 mm` thick flange with a `1.5 mm` deep underside drip-break groove (`0.000 mm²` overhang inverted) overhanging the entire lower housing by `12 mm` per side while tucking the `2× M3` core locking screws directly underneath and leaving the `85.5 mm` bare Al core and `Ø8.0 mm` hanging hole 100% open.
- **100% Seamless Axisymmetric `MECH-CAP-BOT` (`3 mm` Al Core Retained):** Smooth contoured shell (`Ø92 → Ø71 → Ø65 → Ø84 mm`, `237.0 cm³`, `0.178 mm²` `>46°` overhang, all walls `>= 3.5–8.5 mm` robust) paired with the full `3.0 mm` Al tube wall for 6-thread `M3` engagement.

### Verified Mass Budget (From B-Rep Volumes in [cad_verification.json](file:///home/alimuldal/src/lepiled/mechanical_design/cad/cad_verification.json))

| Component | Rev 4.2 (FDM 60%) | Rev 4.4 (FDM 60% — 4 walls / 25% infill) | Rev 4.4 (100% Solid PETG) |
|---|---:|---:|---:|
| **3D-Printed Lamp Parts (`6` lamp parts incl. `base_ring` & `Ø116 mm` brim)** | `~365 g` (`479 cm³`) | **`340.6 g`** (`447.0 cm³`) | `567.7 g` |
| **Bare Al 6063 Core (`250 mm`, `40 × 40 × 3.0 mm`)** | `298.5 g` | **`298.5 g`** | `298.5 g` |
| **Transparent Shroud (`Ø75 × 150 mm`)** | `263.0 g` (borosilicate) | **`120.1 g`** (UVT PMMA `3.0 mm`) | `120.1 g` |
| **`8×` Cu DTP Stars (`34 g`), Driver PCB, Switch, Wires, M3 & Seals** | `112.0 g` | **`112.0 g`** | `112.0 g` |
| **TOTAL LAMP WEIGHT** | **`~1,039 g`** | **`871.2 g`** (`~168 g` lighter than Rev 4.2!) | `1,098.3 g` |

## 2. Coupled Thermal Verification ([thermal_summary.json](file:///home/alimuldal/src/lepiled/mechanical_design/thermal/thermal_summary.json))

Executed via [thermal_analysis.py](file:///home/alimuldal/src/lepiled/mechanical_design/thermal/thermal_analysis.py) modeling `20 mm` Copper DTP stars (`R_sub = 0.50 K/W`, `R_tim = 0.30 K/W`), the `85.5 mm` bare mill-finish (`ε = 0.20`) protruding core, **UVT PMMA `3.0 mm` shroud** (`k = 0.19 W/(m·K)`, `ε = 0.93`), and sealed plastic bottom chamber (`75 °C` PETG limit):

| Ambient & Case | Mode | `T_core` (°C) | `T_j,UV` (°C) (`<=100`) | `T_shroud` (°C) (`<=75`) | `T_PCB` (°C) (`<=75`) | Status |
|---|---|---:|---:|---:|---:|:---:|
| `22 °C` Vertical (UK Night) | `4-UV Nom` | `40.0` | `41.6` | `26.9` | `39.8` | PASS |
| `22 °C` Vertical (UK Night) | `8-ALL Nom (40%UV)` | `51.6` | `53.2` | `30.4` | `52.2` | PASS |
| `22 °C` Horizontal | `8-ALL DS-RealWPE` | `59.4` | `61.5` | `33.0` | `62.3` | PASS |
| `22 °C` Horizontal | `8-ALL DS-100%` (0% optical) | `75.7` | `79.0` | `38.3` | `73.1` | PASS |
| `30 °C` Horizontal | `8-ALL Nom (40%UV)` | `59.3` | `60.9` | `38.6` | `60.0` | PASS |
| `30 °C` Horizontal | `8-ALL DS-RealWPE` | `66.9` | `69.0` | `40.8` | `69.9` | PASS |
| `35 °C` Horizontal | `8-ALL Nom (40%UV)` | `64.0` | `65.6` | `43.5` | `64.8` | PASS |
| `35 °C` Horizontal | `8-ALL DS-RealWPE` | `71.5` | `73.6` | `45.7` | `74.7` | PASS |

**Thermal Takeaway:** Switching from `3.5 mm` borosilicate (`k = 1.14`) to `3.0 mm` UVT PMMA (`k = 0.19`) raises `T_j,UV` by just **`+0.28 °C`** (`60.88` vs `60.60 °C` at `30 °C` horiz), and the acrylic shroud stays cool at **`30–46 °C`** across all realistic night conditions (`> 30 °C` below PMMA continuous-service limits). Leaving the entire `85.5 mm` bare core open above the `Ø116 mm` brim avoids any convection derating.

## 3. CAD Artifacts & Plots

- **Parameters & Generator:** [params.py](file:///home/alimuldal/src/lepiled/mechanical_design/cad/params.py), [generate_cad.py](file:///home/alimuldal/src/lepiled/mechanical_design/cad/generate_cad.py), [cad_verification.json](file:///home/alimuldal/src/lepiled/mechanical_design/cad/cad_verification.json)
- **7 Support-Free 3D-Printable Parts (FDM PETG/ASA):** [mech_base_ring.step](file:///home/alimuldal/src/lepiled/mechanical_design/cad/mech_base_ring.step), [mech_lid_bot.step](file:///home/alimuldal/src/lepiled/mechanical_design/cad/mech_lid_bot.step), [mech_cap_bot.step](file:///home/alimuldal/src/lepiled/mechanical_design/cad/mech_cap_bot.step), [mech_cap_top.step](file:///home/alimuldal/src/lepiled/mechanical_design/cad/mech_cap_top.step), [mech_plug_top.step](file:///home/alimuldal/src/lepiled/mechanical_design/cad/mech_plug_top.step), [mech_plug_bot.step](file:///home/alimuldal/src/lepiled/mechanical_design/cad/mech_plug_bot.step), [mech_drill_jig.step](file:///home/alimuldal/src/lepiled/mechanical_design/cad/mech_drill_jig.step), [lepiled_assembly.step](file:///home/alimuldal/src/lepiled/mechanical_design/cad/lepiled_assembly.step)
- **CAD Renders & Thermal Plots:** [assembly_iso.png](file:///home/alimuldal/src/lepiled/mechanical_design/cad/assembly_iso.png), [assembly_section_xz.png](file:///home/alimuldal/src/lepiled/mechanical_design/cad/assembly_section_xz.png), [assembly_section_yz.png](file:///home/alimuldal/src/lepiled/mechanical_design/cad/assembly_section_yz.png), [lid_bot_detail.png](file:///home/alimuldal/src/lepiled/mechanical_design/cad/lid_bot_detail.png), [cap_bot_detail.png](file:///home/alimuldal/src/lepiled/mechanical_design/cad/cap_bot_detail.png), [cap_top_detail.png](file:///home/alimuldal/src/lepiled/mechanical_design/cad/cap_top_detail.png), [thermal_margins.png](file:///home/alimuldal/src/lepiled/mechanical_design/thermal/thermal_margins.png), [thermal_ambient_sweep.png](file:///home/alimuldal/src/lepiled/mechanical_design/thermal/thermal_ambient_sweep.png), [thermal_network_comparison.png](file:///home/alimuldal/src/lepiled/mechanical_design/thermal/thermal_network_comparison.png)
