# LepiLED DIY Maxi Switch — Mechanical & Thermal Design (Rev 4.8)

## 1. Enclosure & Cooling Architecture

The lamp is a serviceable, sealed, fanless lantern (`276.0 mm` tall, `~560 g` in FDM Black ASA or `~599 g` in FDM Black PETG) built around a single stock `200 mm` aluminum square tube core and eight support-free 3D-printed parts (PETG/ASA-agnostic `31.1 mm` core clearance, `0` supports). For the revision history behind these choices, see [DESIGN_DECISIONS.md](../docs/DESIGN_DECISIONS.md).

- **Chimney-Only Matte-Black Al Core & Staggered Internal Anchor (`MECH-HS-CORE`, `MECH-CORE-ANCHOR`):** A single `200.0 mm` length of `30 × 30 × 3.0 mm` 6063-T6 aluminum box section carries all eight `20 mm` LED stars edge-clamped at `R = 11.7 mm` (`34.0 mm` UV-to-Vis pitch, `16× M3 × 8 mm` pan screws + `Ø7.0 mm` DIN 125 nylon washers) and protrudes `58.5 mm` above `MECH-CAP-TOP` as a passive convection/radiation chimney. Spraying **only the top `58.5 mm` chimney** matte black (`ε = 0.88`) boosts thermal rejection while leaving the interior shroud section bare mill aluminum (`ε = 0.20` — zero UV paint outgassing and zero star-pad masking!). The core locks internally from the dry electronics bay via staggered `MECH-CORE-ANCHOR` (`2× M3 × 12 mm` vertical SHCS on `±Y` at `(0, ±6.5 mm)` + `2× M3 × 8 mm` flush CSK cross-pins on `±X` at `Z_rel = 13.0 mm` — orthogonal and `> 4.4 mm` vertically clear, leaving `MECH-CAP-BOT` 100% free of exterior side holes!).
- **Tapered Base & Serviceable PCB-Carrier Lid (`MECH-CAP-BOT`, `MECH-LID-BOT`, `MECH-CABLE-CLAMP`):** `MECH-CAP-BOT` (`Ø92.4 → Ø74.0 × 88.5 mm`) features a deepened `22.0 mm` protective skirt (recessing the real `18.6 mm` `SW1` toggle boot by `3.4 mm`), intact tactile `0 / 1 / 2` ribs at `Z = 13.0..19.5 mm` (above the `11.0 mm` `45°`-arch portals), and an unobstructed straight `Ø71.6 mm` internal bore. `MECH-LID-BOT` (`Ø85.6 × 7.5 mm`) carries four integral `M2.5` brass-insert PCB standoffs so `driver_pcb` mounts **SMD/JST-side UP** in open air on the bench (eliminating blind USB-C mating and spigot crush!), a cut `Ø9.5 × 0.8 mm` recessed interior pocket for `MECH-VENT-1`, `SW1`'s aligned `12.70(X) × 11.43(Y)` anti-rotation pocket, and a `45°` conical seat + **blind `M3 × 4.0` brass inserts (`1.50 mm` solid roof into dry bay)** driving radial compression in `MECH-CABLE-CLAMP` onto a slit silicone sleeve (`MECH-GROMMET-1`).
- **`PLEXIGLAS® XT Clear 0A070` Shroud & Radial O-Rings (`MECH-TUBE-1`, `MECH-GASKET-1..3`):** Röhm `PLEXIGLAS® XT Clear 0A070` (`29070`, `Ø60 × 54 × 3.0 × 115 mm`, `~80–85%` normal / `~79.8%` cone-integrated transmission at `365 nm`) seals radially into `Ø61.6 × 14.5 mm` sockets via `60 × 3.5 mm` soft VMQ50/60 O-rings (`11.4–31.4%` squeeze across `59.2–60.6 mm` ovality, `±2.0 mm` cut-length tolerant). `MECH-LID-BOT` seals radially via **`MECH-GASKET-3` (`68 × 2.5 mm` VMQ70**, `14.0%` squeeze).
- **Sealed Lofted Roof + Vertical Collar, Finial, Snap-Fit Bushings & DIY Wire Bail (`MECH-CAP-TOP`, `MECH-PLUG-TOP`, `MECH-HANG-BUSHING`):** `MECH-CAP-TOP` adds a **`9.5 mm` vertical `40.4 × 40.4 mm` (`R = 4`) chimney collar** above its unbroken `Ø84 mm` `24.6°` rain roof so `2× M3 × 10 mm` SHCS lock screws bear flat on solid `4.65 mm` walls `5.1 mm` above the internal cone and `1.16 mm` below the backed `OTTOSEAL® S 72 Clear` silicone groove (**0 roof holes**, ray-cast verified!). `MECH-PLUG-TOP` seals the chimney top, and 2 snap-fit Signal-Orange `MECH-HANG-BUSHING` halves (`Ø4.0 mm` pivot bore, `1.85 mm` reinforced sleeve wall, `0.30 mm` retention barbs) carry a removable **DIY C-clip wire hanging bail** bent from `~175 mm` of `Ø2.2–3.0 mm` coat-hanger wire (`38.7 mm` hook/carabiner clearance above the finial, `317.3 mm` height with bail deployed; converging shoulders pull both `8.65 mm` pivot pins inward under gravity load).

### Mass Budget (From CAD B-Rep Volumes in [cad_verification.json](cad/cad_verification.json))

| Component | FDM Black ASA (4 walls / 25% infill) | FDM Black PETG (4 walls / 25% infill) |
|---|---:|---:|
| **3D-Printed Lamp Parts (`7` functional parts, `315.7 cm³`)** | `209.4 g` | `248.6 g` |
| **Chimney-Black Al 6063-T6 Core (`30 × 30 × 3.0 × 200 mm`)** | `173.8 g` | `173.8 g` |
| **`PLEXIGLAS XT 0A070` Shroud (`Ø60 × 54 × 3.0 × 115 mm`)** | `72.9 g` | `72.9 g` |
| **`8×` LED Stars, Driver PCB, Switch, 14 Brass Inserts, O-Rings & Screws** | `104.0 g` | `104.0 g` |
| **Total Lamp Mass (`276.0 × Ø92.4 mm`)** | **`560.1 g`** | **`599.2 g`** |

## 2. SSOT-Coupled Thermal Verification ([thermal_summary.json](thermal/thermal_summary.json))

Solved with [thermal_analysis.py](thermal/thermal_analysis.py) reading geometry directly from [cad_params.json](cad/cad_params.json) (`58.5 mm` chimney, `F_amb = 0.881` eave-shaded view factor, `86.0 mm` shroud window, `5.5 mm` bulkhead) and PCB/LED power directly from [sim_summary.json](../circuit_design/sim/outputs/sim_summary.json) (`P_PCB = 0.324 W` 4-UV / `0.512 W` 8-ALL nom / `0.850 W` worst-case) with **`~14%` interior optical Fresnel/end-cap re-absorption** (`+0.48 W` in `8-ALL`). Checked simultaneously against UV `100 °C`, PMMA `75 °C`, commercial IC bay air `70 °C` (`U4`/`U5`), and PETG `75 °C` (`ASA = 95 °C`):

| Ambient & Orientation | Mode | `T_core` (°C) | `T_j,UV` (°C) (`<=100`) | `T_shroud` (°C) (`<=75`) | `T_bay` (°C) (`<=70`) | `T_PCB` (°C) (`<=75` PETG) | Status |
|---|---|---:|---:|---:|---:|---:|:---:|
| `15 °C` Vertical | `8-ALL Nom (40% UV)` | `53.8` | `55.4` | `27.3` | `40.6` | `47.5` | **PASS** |
| `22 °C` Vertical *(UK Night)* | `4-UV Nom (40% UV)` | `45.1` | `46.7` | `28.9` | `37.0` | `41.4` | **PASS** |
| `22 °C` Vertical *(UK Night)* | `8-ALL Nom (40% UV)` | `60.2` | `61.8` | `34.0` | `47.3` | `54.2` | **PASS** |
| `22 °C` Vertical *(UK Night)* | `8-ALL DS-RealWPE` | `69.6` | `71.7` | `36.9` | `55.2` | `66.7` | **PASS** |
| `30 °C` Vertical *(Warm Night)* | `8-ALL Nom (40% UV)` | `67.5` | `69.2` | `41.6` | `54.9` | `61.8` | **PASS** |
| `30 °C` Vertical *(Warm Night)* | `8-ALL DS-RealWPE` | `76.7` | `78.8` | `44.4` | `62.8` | `74.2` | **PASS** |
| `30 °C` Horizontal | `8-ALL DS-RealWPE` | `77.1` | `79.2` | `45.1` | `62.9` | `74.4` | **PASS** |
| `35 °C` Vertical *(Heatwave)* | `8-ALL Nom (40% UV)` | `72.1` | `73.7` | `46.4` | `59.7` | `66.6` | **PASS** |
| `35 °C` Vertical *(Heatwave)* | `8-ALL DS-RealWPE` | `81.2` | `83.3` | `49.2` | `67.5` | `79.0` *(ASA OK)* | PETG >75 |

**`24 / 24` realistic cases across `15–30 °C` PASS all limits simultaneously (even for PETG + commercial `0..+70 °C` `U4`/`U5`)!**

### Surface-Finish Emissivity Comparison (`30 °C` Vertical Hanging Still Air, `8-ALL Nom / DS-RealWPE`)

| Al Core Finish | `T_j,UV` (Nom / DS-RealWPE) | `T_bay` (Nom / DS-RealWPE) | `T_PCB` (Nom / DS-RealWPE) |
|---|---:|---:|---:|
| **Config 0 (Rev 4.8 Standard): Chimney-Only Black (`58.5 mm`)** | **`69.2 / 78.8 °C`** | **`54.9 / 62.8 °C`** | **`61.8 / 74.2 °C`** *(PASS)* |
| **Config 1: Full-Core Matte-Black Spray (pads masked)** | `65.0 / 73.6 °C` | `52.6 / 59.8 °C` | `59.5 / 71.3 °C` *(PASS)* |
| **Config 2: Unpainted Bare Mill Al Core (`ε = 0.20`)** | `76.4 / 87.8 °C` | `58.8 / 67.6 °C` | `65.8 / 79.1 °C` *(PETG >75)* |
| **Config 3: Benchmark External `SK 578/50 SA` Heatsink** | `55.2 / 60.9 °C` | `47.5 / 53.1 °C` | `54.4 / 64.6 °C` *(PASS)* |

## 3. CAD Files & Renders

- **Parametric Generator & Audit:** [params.py](cad/params.py), [cad_params.json](cad/cad_params.json), [generate_cad.py](cad/generate_cad.py), [cad_verification.json](cad/cad_verification.json)
- **8 Support-Free 3D-Printable Parts:** [mech_cap_bot.step](cad/mech_cap_bot.step), [mech_lid_bot.step](cad/mech_lid_bot.step), [mech_cable_clamp.step](cad/mech_cable_clamp.step) (`2×`), [mech_core_anchor.step](cad/mech_core_anchor.step), [mech_cap_top.step](cad/mech_cap_top.step), [mech_plug_top.step](cad/mech_plug_top.step), [mech_hang_bushing.step](cad/mech_hang_bushing.step) (`2×`), [mech_drill_jig.step](cad/mech_drill_jig.step), [lepiled_assembly.step](cad/lepiled_assembly.step)
- **Renders & Thermal Plots:** [assembly_iso.png](cad/assembly_iso.png), [assembly_section_xz.png](cad/assembly_section_xz.png), [assembly_section_yz.png](cad/assembly_section_yz.png), [lid_bot_detail.png](cad/lid_bot_detail.png), [cap_bot_detail.png](cad/cap_bot_detail.png), [cap_top_detail.png](cad/cap_top_detail.png), [thermal_margins.png](thermal/thermal_margins.png), [thermal_ambient_sweep.png](thermal/thermal_ambient_sweep.png), [thermal_network_comparison.png](thermal/thermal_network_comparison.png)
