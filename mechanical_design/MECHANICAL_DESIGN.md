# LepiLED DIY Maxi Switch — Mechanical & Thermal Design

## 1. Enclosure & Cooling Architecture

The lamp is a sealed, fanless lantern (`266.5 mm` tall, `~521 g` in FDM Black ASA) built around a single stock aluminum square tube core and eight support-free 3D-printed parts. For the revision history behind these choices, see [DESIGN_DECISIONS.md](../docs/DESIGN_DECISIONS.md).

- **Aluminum Cooling Core & Internal Anchor (`MECH-HS-CORE`, `MECH-CORE-ANCHOR`):** A single `200 mm` length of `30 × 30 × 3.0 mm` 6063-T6 aluminum box section carries all eight `20 mm` Copper DTP LED stars (`16× M3 × 8 mm` pan screws with nylon insulating washers) and protrudes `63.0 mm` above the top cap as a passive convection/radiation chimney. Spraying the exterior matte black (with the eight star pads masked bare) boosts thermal radiation and keeps LED junctions cool in still air. The core seats flat onto a `5.5 mm` bulkhead inside the base and locks internally from the dry electronics bay via `MECH-CORE-ANCHOR` (`2× M3 × 12 mm` SHCS + `2× M3 × 8 mm` flush CSK cross-pins), leaving the lower housing wall completely unbroken.
- **Tapered Base & Recessed Bottom Lid (`MECH-CAP-BOT`, `MECH-LID-BOT`, `MECH-CABLE-CLAMP`):** A single `5.1°` matte-black ASA tapered base (`Ø88.4 → Ø74.0 × 80.0 mm`) recesses the flat bottom lid `17.5 mm` inside a protective skirt with two `45°`-arch cable/lightpipe portals and tactile `0 / 1 / 2` switch index ribs. The horizontal `driver_pcb` mounts SMD-side down onto four filleted standoffs with `M2.5` brass heat-set inserts. The lid carries the booted `DPDT` mode switch (`SW1`), a sheltered interior IP68 ePTFE breather vent (`MECH-VENT-1`), a `28.3 mm` side-visible acrylic lightpipe beneath `D12`, and a `16.0 × 14.0 mm` pass-through port with a 2-piece split clamp (`MECH-CABLE-CLAMP`) that captures a right-angle USB-C PD cable watertightly.
- **UV-Transmitting Acrylic Shroud & Radial O-Rings (`MECH-TUBE-1`, `MECH-GASKET-1..3`):** A clear unstabilized extruded PMMA (`Plexiglas XT`) cylinder (`Ø60 × 54 × 3.0 × 115 mm`, `85–92%` transmission at `365 nm`) seals into `Ø61.6 × 14.5 mm` top and bottom sockets via `60 × 3.5 mm` soft VMQ50/60 radial silicone O-rings (`11.4–31.4%` squeeze across tube ovality, `±2.0 mm` cut-length tolerant). The bottom lid seals radially with a `62 × 2.5 mm` VMQ70 silicone O-ring.
- **Lofted Rain Roof, Finial & Hang Bushing (`MECH-CAP-TOP`, `MECH-PLUG-TOP`, `MECH-HANG-BUSHING`):** The top cap lofts unbroken `Ø84 mm` circular `27°` rain eaves into a rounded-square collar clamped to the aluminum core with `2× M3 × 10 mm` SHCS and sealed with neutral-cure oxime silicone in a backed top groove. A press-fit beveled finial seals the open top of the square tube, and a 2-piece snap-in Signal-Orange bushing lines the `Ø8.0 mm` hanging hole.

### Mass Budget (From CAD B-Rep Volumes in [cad_verification.json](cad/cad_verification.json))

| Component | Mass (FDM Black ASA, 4 walls / 25% infill) | Mass (100% Solid ASA) |
|---|---:|---:|
| **3D-Printed Lamp Parts (`7` functional parts)** | `172.5 g` (`260.0 cm³`) | `278.2 g` |
| **Matte-Black Al 6063-T6 Core (`30 × 30 × 3.0 × 200 mm`)** | `173.8 g` | `173.8 g` |
| **Extruded XT PMMA Shroud (`Ø60 × 54 × 3.0 × 115 mm`)** | `72.9 g` | `72.9 g` |
| **`8×` Cu DTP Stars (`34 g`), Driver PCB, Switch, Inserts, O-Rings & Screws** | `102.0 g` | `102.0 g` |
| **Total Lamp Mass (Height)** | **`521.2 g` (`266.5 mm`)** | **`626.9 g`** |

## 2. Coupled Thermal Verification ([thermal_summary.json](thermal/thermal_summary.json))

Solved with [thermal_analysis.py](thermal/thermal_analysis.py) for `20 mm` Copper DTP stars (`R_sub = 0.50 K/W`, `R_tim = 0.30 K/W`), the matte-black sprayed `30 × 30 × 3 mm` aluminum core (`ε = 0.88`, `63.0 mm` exposed chimney), `Ø60 × 54 × 3.0 mm` XT PMMA shroud (`ε = 0.93`), and Black ASA enclosure (`HDT 95 °C`, checked against a conservative `75 °C` PCB limit):

| Ambient & Orientation | Mode | `T_core` (°C) | `T_j,UV` (°C) (`<=100`) | `T_shroud` (°C) (`<=75`) | `T_PCB` (°C) (`<=75`) | Status |
|---|---|---:|---:|---:|---:|:---:|
| `22 °C` Vertical | `4-UV Nom` | `41.3` | `43.0` | `29.8` | `39.9` | PASS |
| `22 °C` Vertical | `8-ALL Nom (40% UV)` | `54.2` | `55.8` | `35.4` | `52.8` | PASS |
| `22 °C` Horizontal | `8-ALL DS-RealWPE` | `62.5` | `64.6` | `39.7` | `63.0` | PASS |
| `30 °C` Vertical | `8-ALL Nom (40% UV)` | `61.4` | `63.0` | `43.1` | `60.4` | PASS |
| `30 °C` Horizontal | `8-ALL Nom (40% UV)` | `61.4` | `63.0` | `43.8` | `60.3` | PASS |
| `30 °C` Horizontal | `8-ALL DS-RealWPE` | `69.5` | `71.6` | `47.4` | `70.4` | PASS |
| `35 °C` Horizontal | `8-ALL Nom (40% UV)` | `65.8` | `67.4` | `48.6` | `65.0` | PASS |
| `35 °C` Horizontal | `8-ALL DS-RealWPE` | `73.8` | `75.9` | `52.2` | `75.0` | PASS |

### Effect of Matte-Black Core Finish (`30 °C` Horizontal Still Air, `8-ALL Nom / DS-RealWPE`)

| Al Core Finish | `T_j,UV` (Nom / DS-RealWPE) | Drop vs Bare Al | `T_PCB` (Nom / DS-RealWPE) |
|---|---:|---:|---:|
| **Bare Mill Aluminum (`ε = 0.20`)** | `78.3 / 90.5 °C` | `0.0 / 0.0 °C` | `64.9 / 76.1 °C` *(over limit)* |
| **Chimney-Only Matte-Black Spray (`top 57 mm`, `ε = 0.88`)** | `69.8 / 80.1 °C` | `-8.5 / -10.4 °C` | `61.3 / 71.7 °C` *(PASS)* |
| **Full-Core Matte-Black Spray (`star pads masked`, `ε = 0.88`)** | **`65.2 / 74.1 °C`** | **`-13.1 / -16.4 °C`** | **`58.5 / 68.3 °C`** *(PASS)* |

## 3. CAD Files & Renders

- **Parametric Generator & Audit:** [params.py](cad/params.py), [generate_cad.py](cad/generate_cad.py), [cad_verification.json](cad/cad_verification.json)
- **8 Support-Free 3D-Printable Parts:** [mech_cap_bot.step](cad/mech_cap_bot.step), [mech_lid_bot.step](cad/mech_lid_bot.step), [mech_cable_clamp.step](cad/mech_cable_clamp.step) (`2×`), [mech_core_anchor.step](cad/mech_core_anchor.step), [mech_cap_top.step](cad/mech_cap_top.step), [mech_plug_top.step](cad/mech_plug_top.step), [mech_hang_bushing.step](cad/mech_hang_bushing.step) (`2×`), [mech_drill_jig.step](cad/mech_drill_jig.step), [lepiled_assembly.step](cad/lepiled_assembly.step)
- **Renders & Thermal Plots:** [assembly_iso.png](cad/assembly_iso.png), [assembly_section_xz.png](cad/assembly_section_xz.png), [assembly_section_yz.png](cad/assembly_section_yz.png), [lid_bot_detail.png](cad/lid_bot_detail.png), [cap_bot_detail.png](cad/cap_bot_detail.png), [cap_top_detail.png](cad/cap_top_detail.png), [thermal_margins.png](thermal/thermal_margins.png), [thermal_ambient_sweep.png](thermal/thermal_ambient_sweep.png), [thermal_network_comparison.png](thermal/thermal_network_comparison.png)
