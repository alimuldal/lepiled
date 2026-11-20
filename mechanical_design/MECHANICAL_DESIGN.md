# LepiLED DIY Maxi Switch — Mechanical & Thermal Design (Rev 4.3 — Field-Robust, Lightweight & Weatherproofed)

## 1. Architecture Summary

Rev 4.3 builds on Rev 4.2's lean hobby architecture (single `250 mm` bare `40 × 40 × 3.0 mm` Al 6063 core, `8×` pre-mounted `20 mm` Copper DTP LED stars, zero brass heat-set inserts, single `M3` fastener size) with four targeted field-robustness, weatherproofing, and portability upgrades:

- **Shatter-Resistant UV-Transmitting PMMA (Acrylic) Shroud (`MECH-TUBE-1`):** Replaces the brittle `263 g` borosilicate tube with a **`120 g` UV-transmitting cast PMMA cylinder** (`Ø75.0 × 69.0 × 3.0 mm × 150 mm`, `85–92%` @ `365 nm` — matching the commercial *LepiLED Maxi* material). Drops `143 g`, eliminates glass breakage in a rucksack, and saves `£2.09` ex-VAT while retaining standard `68 × 3.5 mm` VMQ70 silicone O-rings (`MECH-GASKET-1..2`). *(Never substitute polycarbonate, which blocks `> 98%` of `365 nm` UV-A.)*
- **Bottom-Mounted Toggle Switch (`SW1`) + Protective Base Stand Ring (`MECH-BASE-RING`):** Relocates `C&K 7211SYZBE` + `759D02000` silicone boot from the exposed `+X` wall to the protected underside of `MECH-LID-BOT` (`X = 0, Y = +8.5 mm`, `4.03 mm` cleanly below `driver_pcb` and clear of all TH pins). `MECH-CAP-BOT`'s `+X` wall is now 100% solid and unbroken. A bolt-on support-free standing ring (`MECH-BASE-RING`, `Ø92 × 68 × 18 mm`, `4×` wide drainage cutouts) clamps with the **exact same `4× M3 × 16 mm` SHCS lid bolts**, shielding the silicone switch boot by `3.0 mm` so the lamp stands safely upright.
- **Dual-Layer Rain Roof System:**
  1. **Integral `Ø108 mm` Drip-Brim on `MECH-CAP-TOP`:** `3.5 mm` thick flange (`0.00 mm²` overhang when printed inverted) overhanging the entire lower housing and `-Y` USB-C grommet while shielding the `2× M3` core locking screws directly underneath and leaving `100%` of the `85.5 mm` bare Al core open to natural convection.
  2. **Detachable Pack-Flat Rain Umbrella (`MECH-RAIN-HAT`):** `Ø136 × 7.5 mm` umbrella disc (`5.0 mm` downward drip lip, `0.00 mm²` overhang inverted) that slips onto `MECH-PLUG-TOP` and is automatically retained by the hanging cord passing through `2× Ø6.0 mm` holes (`12.55 mm` above the `Ø8 mm` hanging hole). Pops off in seconds to pack flat.
- **Contoured Lightweight `MECH-CAP-BOT` Shell (Robust `3 mm` Al Core Retained):** Shapes excess solid bulk out of `MECH-CAP-BOT` (`336.7 cm³ -> 228.4 cm³`, `-32%`) while keeping every structural wall `>= 3.5–8.5 mm` thick and retaining the full `3.0 mm` Al tube wall for 6-thread `M3` engagement.

### Verified Mass Budget (From B-Rep Volumes in [cad_verification.json](file:///home/alimuldal/src/lepiled/mechanical_design/cad/cad_verification.json))

| Component | Rev 4.2 (FDM 60%) | Rev 4.3 (FDM 60% — 4 walls / 25% infill) | Rev 4.3 (100% Solid PETG) |
|---|---:|---:|---:|
| **3D-Printed Lamp Parts (`7` parts incl. `base_ring` & `rain_hat`)** | `~365 g` (`479 cm³`) | **`361.1 g`** (`473.9 cm³`; `327.2 g` w/o rain hat) | `601.9 g` |
| **Bare Al 6063 Core (`250 mm`, `40 × 40 × 3.0 mm`)** | `298.5 g` | **`298.5 g`** | `298.5 g` |
| **Transparent Shroud (`Ø75 × 150 mm`)** | `263.0 g` (borosilicate) | **`120.1 g`** (UVT PMMA `3.0 mm`) | `120.1 g` |
| **`8×` Cu DTP Stars (`34 g`), Driver PCB, Switch, Wires, M3 & Seals** | `112.0 g` | **`112.0 g`** | `112.0 g` |
| **TOTAL LAMP WEIGHT** | **`~1,039 g`** | **`891.7 g`** w/ rain hat (**`857.8 g`** w/o hat) | `1,132.5 g` |

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
| `30 °C` Horiz **w/ `MECH-RAIN-HAT`** (`+10%` top conv derating) | `8-ALL Nom / DS-RealWPE` | `60.2 / 68.1` | **`61.9 / 70.2`** | **`38.9 / 41.2`** | **`60.6 / 70.7`** | **PASS** |
| `35 °C` Horizontal | `8-ALL Nom (40%UV)` | `64.0` | `65.6` | `43.5` | `64.8` | PASS |
| `35 °C` Horizontal | `8-ALL DS-RealWPE` | `71.5` | `73.6` | `45.7` | `74.7` | PASS |

**Thermal Takeaway:** Switching from `3.5 mm` borosilicate (`k = 1.14`) to `3.0 mm` UVT PMMA (`k = 0.19`) raises `T_j,UV` by just **`+0.28 °C`** (`60.88` vs `60.60 °C` at `30 °C` horiz), and the acrylic shroud stays cool at **`30–46 °C`** across all realistic night conditions (`> 30 °C` below PMMA continuous-service limits). Even with a conservative `+10%` convection penalty for the detachable `MECH-RAIN-HAT`, all realistic modes pass with **`~30–38 °C` UV junction margin**.

## 3. CAD Artifacts & Plots

- **Parameters & Generator:** [params.py](file:///home/alimuldal/src/lepiled/mechanical_design/cad/params.py), [generate_cad.py](file:///home/alimuldal/src/lepiled/mechanical_design/cad/generate_cad.py), [cad_verification.json](file:///home/alimuldal/src/lepiled/mechanical_design/cad/cad_verification.json)
- **8 Support-Free 3D-Printable Parts (FDM PETG/ASA):** [mech_base_ring.step](file:///home/alimuldal/src/lepiled/mechanical_design/cad/mech_base_ring.step), [mech_lid_bot.step](file:///home/alimuldal/src/lepiled/mechanical_design/cad/mech_lid_bot.step), [mech_cap_bot.step](file:///home/alimuldal/src/lepiled/mechanical_design/cad/mech_cap_bot.step), [mech_cap_top.step](file:///home/alimuldal/src/lepiled/mechanical_design/cad/mech_cap_top.step), [mech_plug_top.step](file:///home/alimuldal/src/lepiled/mechanical_design/cad/mech_plug_top.step), [mech_rain_hat.step](file:///home/alimuldal/src/lepiled/mechanical_design/cad/mech_rain_hat.step), [mech_plug_bot.step](file:///home/alimuldal/src/lepiled/mechanical_design/cad/mech_plug_bot.step), [mech_drill_jig.step](file:///home/alimuldal/src/lepiled/mechanical_design/cad/mech_drill_jig.step), [lepiled_assembly.step](file:///home/alimuldal/src/lepiled/mechanical_design/cad/lepiled_assembly.step)
- **CAD Renders & Thermal Plots:** [assembly_iso.png](file:///home/alimuldal/src/lepiled/mechanical_design/cad/assembly_iso.png), [assembly_section_xz.png](file:///home/alimuldal/src/lepiled/mechanical_design/cad/assembly_section_xz.png), [assembly_section_yz.png](file:///home/alimuldal/src/lepiled/mechanical_design/cad/assembly_section_yz.png), [lid_bot_detail.png](file:///home/alimuldal/src/lepiled/mechanical_design/cad/lid_bot_detail.png), [cap_bot_detail.png](file:///home/alimuldal/src/lepiled/mechanical_design/cad/cap_bot_detail.png), [cap_top_detail.png](file:///home/alimuldal/src/lepiled/mechanical_design/cad/cap_top_detail.png), [thermal_margins.png](file:///home/alimuldal/src/lepiled/mechanical_design/thermal/thermal_margins.png), [thermal_ambient_sweep.png](file:///home/alimuldal/src/lepiled/mechanical_design/thermal/thermal_ambient_sweep.png), [thermal_network_comparison.png](file:///home/alimuldal/src/lepiled/mechanical_design/thermal/thermal_network_comparison.png)
