# LepiLED DIY Maxi Switch — Mechanical & Thermal Design (Rev 4.6 — "Field Lantern")

## 1. Architecture Summary

Rev 4.6 resolves every P0/P1 mechanical, sealing, and thermal defect uncovered in the fourth independent adversarial review while introducing a unified "Field Lantern" industrial-design silhouette (`~577 g` FDM Black ASA, `281.5 mm` tall):

- **Intact Solid `R = 24.4 mm` (`Ø48.8 mm`) Central Core Hubs & Internal Dry-Bay Core Anchor (P0-1 Fixed):** In both `MECH-CAP-BOT` and `MECH-CAP-TOP`, the `45°` internal shroud transition cone terminates onto a full-height solid `R = 24.4 mm` hub (`2.62 mm` corner wall / `9.0 mm` flat wall around the `30.8 × 30.8 mm` square core socket, `0.000 mm²` overhang). `MECH-CAP-BOT` locks the `30 × 30 × 3 × 200 mm` Al core **internally from the dry electronics bay** via `2× M3 × 16 mm` SHCS bearing flat on an `8.6 mm` solid ASA bulkhead into `MECH-CORE-ANCHOR` (cross-pinned flush inside the Al bore by `2× M3 × 8 mm` CSK screws)—leaving **zero exterior side holes or rain-ingress paths on `MECH-CAP-BOT`**. `MECH-CAP-TOP` clamps via `2× M3 × 10 mm` SHCS bearing on solid `4.60 mm` hub shoulders well clear of the unbroken `Ø84 mm` eaves rim, backed by a solid-floor `2.0 × 2.5 mm` top neutral-cure oxime silicone seal channel.
- **Coaxial 3D-Printed 2-Piece Split Cable Clamp (P0-2 Fixed, `-£3.33`):** Eliminates the colliding/non-passing `M20` cable gland. `MECH-LID-BOT` features a `16.0 × 14.0 mm` rounded-stadium pass-through port (passing an intact `13.2 × 11.5 mm` `90°` USB-C L-plug cleanly) clamped from below by `2×` identical `MECH-CABLE-CLAMP` halves (`2× M3 × 14 mm` SHCS) compressing a slit silicone grommet onto the `Ø4.0–4.5 mm` cable jacket. Zero protrusion above `MECH-LID-BOT` (`Z = 24.0 mm`) gives **`15.4 mm` vertical bend room below the `90°` plug body** (`8.42 mm` clear below a modeled `7.0 mm` molded strain-relief boot!) and `5.0 mm` ground clearance.
- **Unified `4.3°` Tapered Frustum Base & Lofted Square-to-Round Rain Roof:** Eliminates `MECH-BASE-RING` completely—`MECH-CAP-BOT` is one continuous matte-black ASA tapered frustum (`Ø88.4 mm` ground rim → `Ø74.0 mm` shroud collar, `4.3°` taper) recessing `MECH-LID-BOT` (`Ø79.4 mm`) `19.0 mm` inside with two smooth `45°`-arch cable/D12-glow portals and tactile `0 / 1 / 2` midnight switch index ribs. `MECH-CAP-TOP` lofts its unbroken `Ø84 mm` circular rain eaves smoothly into an `R = 4.0 mm` `38.8 × 38.8 mm` rounded-square chimney collar, topped by an `8.0 mm` `45°`-beveled obelisk finial (`MECH-PLUG-TOP`) and a 2-half Signal-Orange snap-in `Ø8 mm` paracord bushing (`MECH-HANG-BUSHING`).
- **Ovality-Tolerant Radial O-Rings, Brass Heat-Set Inserts, Interior ePTFE Vent & Side-Visible `D12`:** Widened shroud bores (`Ø61.6 mm × 14.5 mm` deep) with **`60 × 3.5 mm` soft VMQ50/60** radial O-rings hold `11.4–31.4%` squeeze (`22.9%` nom) across real `59.2–60.6 mm` extruded `Plexiglas XT` ovality with `+2.9 mm` short-tube gravity-drop margin. `4× M2.5 × 4.0 × 3.5 mm` brass heat-set inserts inside filleted `Ø7.4 → Ø5.5 mm` PCB standoffs and `10× M3 × 5.0 × 4.2 mm` brass inserts eliminate FDM Z-layer splitting and exterior hex-nut slots. `MECH-VENT-1` moves to the sheltered **inside top face** of `MECH-LID-BOT` (mud/finger proof), and the `D12` PMMA lightpipe lengthens to **`29.8 mm`** (`1.4 mm` below `D12`, `45°` beveled side-visible tip).

### Verified Mass Budget (From B-Rep Volumes in [cad_verification.json](cad/cad_verification.json))

| Component | Rev 4.5 (FDM PETG) | Rev 4.6 (FDM Black ASA — 4 walls / 25% infill) | Rev 4.6 (100% Solid ASA) |
|---|---:|---:|---:|
| **3D-Printed Lamp Parts (`7` lamp parts — `MECH-BASE-RING` deleted)** | `240.8 g` (`316.0 cm³` PETG) | **`228.3 g`** (`344.1 cm³` Black ASA) | `368.2 g` |
| **Matte-Black Al 6063-T6 Core (`30 × 30 × 3.0 × 200 mm`)** | `173.9 g` | **`173.8 g`** | `173.8 g` |
| **Transparent Shroud (`Ø60 × 54 × 3.0 × 115 mm` Extruded XT PMMA)** | `72.9 g` | **`72.9 g`** | `72.9 g` |
| **`8×` Cu DTP Stars (`34 g`), PCB, SW1, Brass Inserts, O-Rings & Screws** | `115.0 g` *(w/ M20 gland)* | **`102.0 g`** *(M20 gland removed)* | `102.0 g` |
| **TOTAL LAMP WEIGHT (HEIGHT)** | `602.6 g` (`277.0 mm`) | **`577.0 g` (`281.5 mm` — `-25.6 g` vs 4.5, `-294 g` vs 4.4)** | `716.9 g` |

## 2. Coupled Thermal Verification ([thermal_summary.json](thermal/thermal_summary.json))

Executed via [thermal_analysis.py](thermal/thermal_analysis.py) modeling `20 mm` Copper DTP stars (`R_sub = 0.50 K/W`, `R_tim = 0.30 K/W`), the **`57.0 mm` protruding `30 × 30 × 3 mm` Al core sprayed matte black** (`ε = 0.88`, star pads masked), `Ø60 × 54 × 3.0 mm` **XT PMMA shroud** (`k = 0.19 W/(m·K)`, `ε = 0.93`, opaque in thermal IR `8–14 µm`), and Black ASA housing (`HDT 95 °C`; checked against the conservative `75 °C` PCB limit):

| Ambient & Case | Mode | `T_core` (°C) | `T_j,UV` (°C) (`<=100`) | `T_shroud` (°C) (`<=75`) | `T_PCB` (°C) (`<=75` / `95` ASA) | Status |
|---|---|---:|---:|---:|---:|:---:|
| `22 °C` Vertical (UK Night) | `4-UV Nom` | `42.6` | `44.3` | `30.3` | `38.8` | PASS |
| `22 °C` Vertical (UK Night) | `8-ALL Nom (40%UV)` | `56.3` | `57.9` | `36.3` | `50.9` | PASS |
| `22 °C` Horizontal | `8-ALL DS-RealWPE` | `65.2` | `67.3` | `41.0` | `60.9` | PASS |
| `30 °C` Vertical | `8-ALL Nom (40%UV)` | `63.4` | `65.0` | `44.0` | `58.5` | PASS |
| `30 °C` Horizontal | `8-ALL Nom (40%UV)` | `63.5` | `65.2` | `44.7` | `58.5` | PASS |
| `30 °C` Horizontal | `8-ALL DS-RealWPE` | `72.0` | `74.1` | `48.6` | `68.3` | PASS |
| `35 °C` Horizontal | `8-ALL Nom (40%UV)` | `67.9` | `69.6` | `49.6` | `63.3` | PASS |
| `35 °C` Horizontal | `8-ALL DS-RealWPE` | `76.3` | `78.4` | `53.4` | `73.0` | PASS |

### Surface-Finish Emissivity Comparison (`30 °C` Horizontal Still Air, `8-ALL Nom / DS-RealWPE`)

| Al Core Finish | `T_j,UV` Nom / DS-RealWPE | Delta vs Bare Al | `T_PCB` Nom / DS-RealWPE | Why It Works |
|---|---:|---:|---:|---|
| **Bare Mill Al (`ε = 0.20` everywhere)** | `78.3 / 90.5 °C` | `0.0 / 0.0 °C` | `64.9 / 76.1 °C` *(FAIL)* | Weak IR radiation (`~1.4 W/(m²·K)`) vs convection (`~6.5 W/(m²·K)`) |
| **Chimney-Only Matte-Black Spray (`top 57 mm` `ε = 0.88`, inner `0.20`)** | `69.8 / 80.1 °C` | **`-8.5 / -10.4 °C`** | `61.3 / 71.7 °C` *(PASS)* | Boosts top chimney IR radiation `4.4×` (`~6.2 W/(m²·K)`) |
| **Rev 4.6 Standard: Full-Core Matte-Black Spray (`star pads masked`, `ε = 0.88`)** | **`65.2 / 74.1 °C`** | **`-13.1 / -16.4 °C`** | **`58.5 / 68.3 °C` *(PASS)*** | Boosts BOTH top chimney radiation AND internal IR coupling to PMMA (`ε = 0.93`) |

## 3. CAD Artifacts & Plots

- **Parameters & Generator:** [params.py](cad/params.py), [generate_cad.py](cad/generate_cad.py), [cad_verification.json](cad/cad_verification.json)
- **8 Support-Free 3D-Printable Parts (FDM Black ASA + Signal-Orange Accent):** [mech_cap_bot.step](cad/mech_cap_bot.step), [mech_lid_bot.step](cad/mech_lid_bot.step), [mech_cable_clamp.step](cad/mech_cable_clamp.step) (`print 2×`), [mech_core_anchor.step](cad/mech_core_anchor.step), [mech_cap_top.step](cad/mech_cap_top.step), [mech_plug_top.step](cad/mech_plug_top.step), [mech_hang_bushing.step](cad/mech_hang_bushing.step) (`print 2×`), [mech_drill_jig.step](cad/mech_drill_jig.step), [lepiled_assembly.step](cad/lepiled_assembly.step)
- **CAD Renders & Thermal Plots:** [assembly_iso.png](cad/assembly_iso.png), [assembly_section_xz.png](cad/assembly_section_xz.png), [assembly_section_yz.png](cad/assembly_section_yz.png), [lid_bot_detail.png](cad/lid_bot_detail.png), [cap_bot_detail.png](cad/cap_bot_detail.png), [cap_top_detail.png](cad/cap_top_detail.png), [thermal_margins.png](thermal/thermal_margins.png), [thermal_ambient_sweep.png](thermal/thermal_ambient_sweep.png), [thermal_network_comparison.png](thermal/thermal_network_comparison.png)
