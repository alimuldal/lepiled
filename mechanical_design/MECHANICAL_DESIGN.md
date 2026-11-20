# LepiLED DIY Maxi Switch — Mechanical & Thermal Design (Rev 4.6 — "Field Lantern")

## 1. Architecture Summary

Rev 4.6 resolves every P0/P1 mechanical, sealing, and thermal defect uncovered in the fourth independent adversarial review while introducing a compact "Field Lantern" industrial-design silhouette (`~521 g` FDM Black ASA, `266.5 mm` tall):

- **Intact Solid `R = 24.4 mm` (`Ø48.8 mm`) Central Core Hubs & Internal Dry-Bay Core Anchor (P0-1 Fixed):** In both `MECH-CAP-BOT` and `MECH-CAP-TOP`, the `45°` internal shroud transition cone terminates onto a full-height solid `R = 24.4 mm` hub (`2.62 mm` corner wall / `9.0 mm` flat wall around the `30.8 × 30.8 mm` square core socket, `0.000 mm²` unsupported overhang). `MECH-CAP-BOT` seats the `30 × 30 × 3 × 200 mm` Al core flat onto a **`5.5 mm` solid ASA bulkhead** (printing inverted with one hidden `30.8 mm` internal orthogonal bridge inside the socket to save `21 mm` height and `56 g` of dead plastic) and locks it **internally from the dry electronics bay** via `2× M3 × 12 mm` SHCS into `MECH-CORE-ANCHOR` (cross-pinned flush inside the Al bore by `2× M3 × 8 mm` CSK screws)—leaving **zero exterior side holes or rain-ingress paths on `MECH-CAP-BOT`**. `MECH-CAP-TOP` clamps via `2× M3 × 10 mm` SHCS bearing on solid `4.60 mm` hub shoulders well clear of the unbroken `Ø84 mm` eaves rim, backed by a solid-floor `2.0 × 2.5 mm` top neutral-cure oxime silicone seal channel.
- **Coaxial 3D-Printed 2-Piece Split Cable Clamp (P0-2 Fixed, `-£3.33`):** Eliminates the colliding/non-passing `M20` cable gland. `MECH-LID-BOT` features a `16.0 × 14.0 mm` rounded-stadium pass-through port (passing an intact `13.2 × 11.5 mm` `90°` USB-C L-plug cleanly) clamped from below by `2×` identical `MECH-CABLE-CLAMP` halves (`2× M3 × 12 mm` SHCS) compressing a slit silicone grommet onto the `Ø4.0–4.5 mm` cable jacket. Zero protrusion above `MECH-LID-BOT` (`Z = 22.5 mm`) gives **`13.9 mm` vertical bend room below the `90°` plug body** (`6.92 mm` clear below a modeled `7.0 mm` molded strain-relief boot!) and `5.0 mm` ground clearance.
- **Compact `5.1°` Tapered Frustum Base & Lofted Square-to-Round Rain Roof:** Eliminates `MECH-BASE-RING` completely—`MECH-CAP-BOT` is one continuous matte-black ASA tapered frustum (`Ø88.4 mm` ground rim → `Ø74.0 mm` shroud collar, `80.0 mm` tall, `5.1°` taper) recessing `MECH-LID-BOT` (`Ø79.4 mm`) `17.5 mm` inside with two smooth `45°`-arch cable/D12-glow portals and tactile `0 / 1 / 2` midnight switch index ribs. `MECH-CAP-TOP` lofts its unbroken `Ø84 mm` circular rain eaves smoothly into an `R = 4.0 mm` `38.8 × 38.8 mm` rounded-square chimney collar, topped by an `8.0 mm` `45°`-beveled obelisk finial (`MECH-PLUG-TOP`) and a 2-half Signal-Orange snap-in `Ø8 mm` paracord bushing (`MECH-HANG-BUSHING`).
- **Ovality-Tolerant Radial O-Rings, Brass Heat-Set Inserts, Interior ePTFE Vent & Side-Visible `D12`:** Widened shroud bores (`Ø61.6 mm × 14.5 mm` deep) with **`60 × 3.5 mm` soft VMQ50/60** radial O-rings hold `11.4–31.4%` squeeze (`22.9%` nom) across real `59.2–60.6 mm` extruded `Plexiglas XT` ovality with `+2.9 mm` short-tube gravity-drop margin. `4× M2.5 × 4.0 × 3.5 mm` brass heat-set inserts inside filleted `Ø7.4 → Ø5.5 mm` PCB standoffs and `10× M3 × 5.0 × 4.2 mm` brass inserts eliminate FDM Z-layer splitting and exterior hex-nut slots. `MECH-VENT-1` sits on the sheltered **inside top face** of `MECH-LID-BOT` (mud/finger proof), and the `D12` PMMA lightpipe is **`28.3 mm`** long (`1.4 mm` below `D12`, `45°` beveled side-visible tip).

### Verified Mass Budget (From B-Rep Volumes in [cad_verification.json](cad/cad_verification.json))

| Component | Rev 4.5 (FDM PETG) | Rev 4.6 Compact (FDM Black ASA — 4 walls / 25% infill) | Rev 4.6 (100% Solid ASA) |
|---|---:|---:|---:|
| **3D-Printed Lamp Parts (`7` lamp parts — `MECH-BASE-RING` deleted)** | `240.8 g` (`316.0 cm³` PETG) | **`172.5 g`** (`260.0 cm³` Black ASA; `cap_bot = 138.7 cm³`) | `278.2 g` |
| **Matte-Black Al 6063-T6 Core (`30 × 30 × 3.0 × 200 mm`)** | `173.9 g` | **`173.8 g`** | `173.8 g` |
| **Transparent Shroud (`Ø60 × 54 × 3.0 × 115 mm` Extruded XT PMMA)** | `72.9 g` | **`72.9 g`** | `72.9 g` |
| **`8×` Cu DTP Stars (`34 g`), PCB, SW1, Brass Inserts, O-Rings & Screws** | `115.0 g` *(w/ M20 gland)* | **`102.0 g`** *(M20 gland removed)* | `102.0 g` |
| **TOTAL LAMP WEIGHT (HEIGHT)** | `602.6 g` (`277.0 mm`) | **`521.2 g` (`266.5 mm` — `-81.4 g` vs 4.5, `-350 g` vs 4.4)** | `626.9 g` |

## 2. Coupled Thermal Verification ([thermal_summary.json](thermal/thermal_summary.json))

Executed via [thermal_analysis.py](thermal/thermal_analysis.py) modeling `20 mm` Copper DTP stars (`R_sub = 0.50 K/W`, `R_tim = 0.30 K/W`), the **`63.0 mm` protruding `30 × 30 × 3 mm` Al core sprayed matte black** (`ε = 0.88`, star pads masked), `Ø60 × 54 × 3.0 mm` **XT PMMA shroud** (`k = 0.19 W/(m·K)`, `ε = 0.93`, opaque in thermal IR `8–14 µm`), and Black ASA housing (`HDT 95 °C`; checked against the conservative `75 °C` PCB limit):

| Ambient & Case | Mode | `T_core` (°C) | `T_j,UV` (°C) (`<=100`) | `T_shroud` (°C) (`<=75`) | `T_PCB` (°C) (`<=75` / `95` ASA) | Status |
|---|---|---:|---:|---:|---:|:---:|
| `22 °C` Vertical (UK Night) | `4-UV Nom` | `41.3` | `43.0` | `29.8` | `39.9` | PASS |
| `22 °C` Vertical (UK Night) | `8-ALL Nom (40%UV)` | `54.2` | `55.8` | `35.4` | `52.8` | PASS |
| `22 °C` Horizontal | `8-ALL DS-RealWPE` | `62.5` | `64.6` | `39.7` | `63.0` | PASS |
| `30 °C` Vertical | `8-ALL Nom (40%UV)` | `61.4` | `63.0` | `43.1` | `60.4` | PASS |
| `30 °C` Horizontal | `8-ALL Nom (40%UV)` | `61.4` | `63.0` | `43.8` | `60.3` | PASS |
| `30 °C` Horizontal | `8-ALL DS-RealWPE` | `69.5` | `71.6` | `47.4` | `70.4` | PASS |
| `35 °C` Horizontal | `8-ALL Nom (40%UV)` | `65.8` | `67.4` | `48.6` | `65.0` | PASS |
| `35 °C` Horizontal | `8-ALL DS-RealWPE` | `73.8` | `75.9` | `52.2` | `75.0` | PASS |

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
