# LepiLED DIY Maxi Switch — Mechanical & Thermal Design (Rev 4.9)

## 1. Enclosure & Cooling Architecture

The lamp is a serviceable, sealed, fanless lantern (`277.0 mm` tall body / `318.3 mm` w/ wire bail, `~572 g` in FDM Black ASA or `~613 g` in FDM Black PETG) built around a single unpainted stock `200 mm` aluminum square tube core, eight support-free 3D-printed parts (PETG/ASA-agnostic `31.1 mm` core clearance, `0` supports), and **unified workshop `M3` CSK hardware** (one single thread size across all `14` brass inserts and `32` screws!). For the revision history behind these choices, see [DESIGN_DECISIONS.md](../docs/DESIGN_DECISIONS.md).

- **Unpainted Bare Mill Al Core & Staggered Internal Anchor (`MECH-HS-CORE`, `MECH-CORE-ANCHOR`):** A single `200.0 mm` length of `30 × 30 × 3.0 mm` 6063-T6 aluminum box section carries all eight Convoy `20 mm` Copper DTP LED stars edge-clamped at `R = 11.7 mm` (`34.0 mm` UV-to-Vis pitch, `16×` `M3 × 8 mm` CSK screw + `M3` steel flat washer + `Ø7.0 mm` DIN 125 nylon washer stack) and protrudes `58.5 mm` above `MECH-CAP-TOP` as a passive cooling chimney. Leaving the entire tube **unpainted bare mill aluminum (`ε = 0.20`)** eliminates paint cost, masking, and UV paint outgassing while passing **16/16 UK-night (`<= 22 °C`) Real-WPE**, **18/18 `15–30 °C` nominal (PETG)**, and **24/24 `15–30 °C` Real-WPE (ASA + commercial ICs)** thermal cases! The core locks internally from the dry electronics bay via staggered `MECH-CORE-ANCHOR` (`2× M3 × 12 mm` vertical flush CSK bolts on `±Y` at `(0, ±6.5 mm)` + `2× M3 × 8 mm` flush CSK cross-pins on `±X` at `Z_rel = 13.0 mm` — orthogonal and `> 4.4 mm` vertically clear, leaving `MECH-CAP-BOT` 100% free of exterior side holes!).
- **Tapered Base & Unified-`M3` Serviceable PCB-Carrier Lid (`MECH-CAP-BOT`, `MECH-LID-BOT`, `MECH-CABLE-CLAMP`):** `MECH-CAP-BOT` (`Ø94.4 → Ø74.0 × 89.5 mm`) features a deepened `22.0 mm` protective skirt (recessing the real `18.6 mm` `SW1` toggle boot by `3.4 mm`), intact tactile `0 / 1 / 2` ribs at `Z = 13.0..19.5 mm` (above the `11.0 mm` `45°`-arch portals), an unobstructed straight `Ø71.6 mm` internal bore, and `4×` `M3 × 5.0` lid brass inserts at `R = 40.0 mm` (`2.20 mm` inner bore wall + `5.20 mm` outer wall). `MECH-LID-BOT` (`Ø87.6 × 8.5 mm`) is thickened `+1.0 mm` so **all `14` inserts use identical standard `M3 × 5.0 × 4.2 mm` workshop inserts** (`4×` integral `Ø7.0 → Ø6.0 mm` `M3` PCB standoffs mounting `driver_pcb` **SMD/JST-side UP** in open air, `2×` **blind `M3 × 5.0` clamp inserts** retaining a `1.50 mm` solid roof into the dry bay!), `4×` flush `90°` CSK lid seats (`0.55 mm` unbroken outer rim), a cut `Ø9.5 × 0.8 mm` recessed interior pocket for `MECH-VENT-1`, `SW1`'s aligned `12.70(X) × 11.43(Y)` anti-rotation pocket, and a `45°` conical seat driving radial compression in `MECH-CABLE-CLAMP` (with flush `90°` CSK seats) onto a slit silicone sleeve (`MECH-GROMMET-1`).
- **Extruded Clear XT PMMA Shroud & Radial O-Rings (`MECH-TUBE-1`, `MECH-GASKET-1..3`):** Non-UV-blocked extruded clear XT PMMA (`Ø60 × 54 × 3.0 × 115 mm`, verified via 365 nm white-paper fluorescence bench check) seals radially into `Ø61.6 × 14.5 mm` sockets via `60 × 3.5 mm` soft VMQ50/60 O-rings (`11.4–31.4%` squeeze across `59.2–60.6 mm` ovality, `±2.0 mm` cut-length tolerant). `MECH-LID-BOT` seals radially via **`MECH-GASKET-3` (`68 × 2.5 mm` VMQ70**, `14.0%` squeeze).
- **Sealed Lofted Roof + Vertical Collar, Finial, Snap-Fit Bushings & DIY Wire Bail (`MECH-CAP-TOP`, `MECH-PLUG-TOP`, `MECH-HANG-BUSHING`):** `MECH-CAP-TOP` adds a **`9.5 mm` vertical `40.4 × 40.4 mm` (`R = 4`) chimney collar** above its unbroken `Ø84 mm` `24.6°` rain roof so `2× M3 × 10 mm` CSK lock screws (+ steel flat washers) bear flat on solid `4.65 mm` walls `5.1 mm` above the internal cone and `1.16 mm` below the backed `Soudal Fix ALL Crystal` sealant groove (**0 roof holes**, ray-cast verified!). `MECH-PLUG-TOP` seals the chimney top, and 2 snap-fit Signal-Orange `MECH-HANG-BUSHING` halves (`Ø4.0 mm` pivot bore, `1.85 mm` reinforced sleeve wall, `0.30 mm` retention barbs) carry a removable **DIY C-clip wire hanging bail** bent from `~175 mm` of `Ø2.2–3.0 mm` coat-hanger wire (`38.7 mm` hook/carabiner clearance above the finial, `318.3 mm` height with bail deployed; converging shoulders pull both `8.6 mm` pivot pins inward under gravity load).

### Mass Budget (From CAD B-Rep Volumes in [cad_verification.json](cad/cad_verification.json))

| Component | FDM Black ASA (4 walls / 25% infill) | FDM Black PETG (4 walls / 25% infill) |
|---|---:|---:|
| **3D-Printed Lamp Parts (`7` functional parts, `332.8 cm³`)** | `220.8 g` | `262.1 g` |
| **Unpainted Bare Mill Al 6063-T6 Core (`30 × 30 × 3.0 × 200 mm`)** | `173.8 g` | `173.8 g` |
| **Extruded Clear XT PMMA Shroud (`Ø60 × 54 × 3.0 × 115 mm`)** | `72.9 g` | `72.9 g` |
| **`8×` Convoy Cu Stars, Driver PCB, Switch, 14 `M3` Inserts, O-Rings & Screws** | `104.0 g` | `104.0 g` |
| **Total Lamp Mass (`277.0 × Ø94.4 mm`)** | **`571.5 g`** | **`612.7 g`** |

## 2. SSOT-Coupled Thermal Verification ([thermal_summary.json](thermal/thermal_summary.json))

Solved with [thermal_analysis.py](thermal/thermal_analysis.py) reading geometry directly from [cad_params.json](cad/cad_params.json) (`58.5 mm` unpainted bare Al chimney `ε = 0.20`, `F_amb = 0.881` eave-shaded view factor, `86.0 mm` shroud window, `5.5 mm` bulkhead) and PCB/LED power directly from [sim_summary.json](../circuit_design/sim/outputs/sim_summary.json) (`P_PCB = 0.321 W` 4-UV / `0.508 W` 8-ALL nom / `0.842 W` worst-case; `ams OSRAM CSLNM1` `R_thJS = 4.9 K/W` max) with **`~14%` interior optical Fresnel/end-cap re-absorption**. Checked simultaneously against UV `100 °C`, PMMA `75 °C`, commercial IC bay air `70 °C` (`U4`/`U5`), and PETG `75 °C` (`ASA = 95 °C`):

| Ambient & Orientation | Mode | `T_core` (°C) | `T_j,UV` (°C) (`<=100`) | `T_j,Vis` (°C) (`<=150`) | `T_shroud` (°C) (`<=75`) | `T_bay` (°C) (`<=70`) | `T_PCB` (°C) (`<=75` PETG / `<=95` ASA) | Status |
|---|---|---:|---:|---:|---:|---:|---:|:---:|
| `15 °C` Vertical | `8-ALL Nom (40% UV)` | `60.4` | `62.0` | `64.1` | `29.3` | `44.1` | `51.0` | **PASS** |
| `22 °C` Vertical *(UK Night)* | `4-UV Nom (40% UV)` | `49.5` | `51.1` | `48.9` | `30.2` | `39.4` | `43.7` | **PASS** |
| `22 °C` Vertical *(UK Night)* | `8-ALL Nom (40% UV)` | `67.1` | `68.7` | `70.8` | `36.1` | `51.0` | `57.8` | **PASS** |
| `22 °C` Vertical *(UK Night)* | `8-ALL DS-RealWPE` | `78.1` | `80.2` | `83.1` | `39.5` | `59.7` | `71.1` | **PASS** |
| `30 °C` Vertical *(Warm Night)* | `8-ALL Nom (40% UV)` | `74.7` | `76.3` | `78.5` | `43.8` | `58.8` | `65.6` | **PASS** |
| `30 °C` Vertical *(Warm Night)* | `8-ALL DS-RealWPE` | `85.7` | `87.8` | `90.6` | `47.2` | `67.5` | `78.9` *(ASA PASS)* | ASA PASS / PETG >75 |
| `30 °C` Horizontal | `8-ALL Nom (40% UV)` | `75.1` | `76.7` | `78.8` | `44.5` | `59.0` | `65.8` | **PASS** |
| `35 °C` Vertical *(Heatwave)* | `8-ALL Nom (40% UV)` | `79.5` | `81.1` | `83.2` | `48.6` | `63.6` | `70.5` | **PASS** |

**`16/16` UK-night (`<= 22 °C` Real-WPE, PETG + commercial ICs), `18/18` `15–30 °C` nominal (PETG), and `24/24` `15–30 °C` Real-WPE (ASA + commercial ICs) PASS all thermal limits on unpainted bare aluminum!**

### Surface-Finish Emissivity Comparison (`30 °C` Vertical Hanging Still Air, `8-ALL Nom / DS-RealWPE`)

| Al Core Finish | `T_j,UV` (Nom / DS-RealWPE) | `T_bay` (Nom / DS-RealWPE) | `T_PCB` (Nom / DS-RealWPE) |
|---|---:|---:|---:|
| **Config 0 (Rev 4.9 Standard): Unpainted Bare Mill Al (`ε = 0.20`)** | **`76.3 / 87.8 °C`** | **`58.8 / 67.5 °C`** | **`65.6 / 78.9 °C`** *(Nom PETG / WC ASA)* |
| **Config 1 (Optional): Chimney-Only Matte-Black (`58.5 mm`)** | `69.1 / 78.8 °C` | `54.9 / 62.7 °C` | `61.7 / 74.1 °C` *(PETG PASS)* |
| **Config 2: Full-Core Matte-Black Spray (pads masked)** | `64.9 / 73.6 °C` | `52.5 / 59.8 °C` | `59.4 / 71.1 °C` *(PETG PASS)* |
| **Config 3: Benchmark External `SK 578/50 SA` Heatsink** | `55.2 / 60.9 °C` | `47.4 / 53.1 °C` | `54.3 / 64.4 °C` *(PETG PASS)* |

## 3. CAD Files & Renders

- **Parametric Generator & Audit:** [params.py](cad/params.py), [cad_params.json](cad/cad_params.json), [generate_cad.py](cad/generate_cad.py), [cad_verification.json](cad/cad_verification.json)
- **8 Support-Free 3D-Printable Parts:** [mech_cap_bot.step](cad/mech_cap_bot.step), [mech_lid_bot.step](cad/mech_lid_bot.step), [mech_cable_clamp.step](cad/mech_cable_clamp.step) (`2×`), [mech_core_anchor.step](cad/mech_core_anchor.step), [mech_cap_top.step](cad/mech_cap_top.step), [mech_plug_top.step](cad/mech_plug_top.step), [mech_hang_bushing.step](cad/mech_hang_bushing.step) (`2×`), [mech_drill_jig.step](cad/mech_drill_jig.step), [lepiled_assembly.step](cad/lepiled_assembly.step)
- **Renders & Thermal Plots:** [assembly_iso.png](cad/assembly_iso.png), [assembly_section_xz.png](cad/assembly_section_xz.png), [assembly_section_yz.png](cad/assembly_section_yz.png), [lid_bot_detail.png](cad/lid_bot_detail.png), [cap_bot_detail.png](cad/cap_bot_detail.png), [cap_top_detail.png](cad/cap_top_detail.png), [thermal_margins.png](thermal/thermal_margins.png), [thermal_ambient_sweep.png](thermal/thermal_ambient_sweep.png), [thermal_network_comparison.png](thermal/thermal_network_comparison.png)
