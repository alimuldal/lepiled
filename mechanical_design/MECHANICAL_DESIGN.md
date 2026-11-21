# LepiLED DIY Maxi Switch — Mechanical & Thermal Design

## 1. Enclosure & Open-Chimney Cooling Architecture

The lamp is a fanless lantern (`324.0 mm` body height, `~609 g` White ASA or `~657 g` White PETG) built around an open, stainless-mesh-screened `30 × 30 × 2.0 × 300.0 mm` clear-anodized aluminum square tube cooling chimney (`ε_IR ≈ 0.82`), six support-free 3D-printed parts, an extruded clear XT PMMA shroud, epoxy-bonded Copper DTP LED stars (zero aluminum tapping), a captive `15 × 15 mm` silicone-pad/brass-shim PCB thermal bridge, `6` `M3` brass inserts + `4` captive `M3` hex nuts + `10` `M3` screws, and two `M4 × 50 mm` A2 stainless cross-bolts. For design history and revision rationale, see [DESIGN_DECISIONS.md](../docs/DESIGN_DECISIONS.md).

- **Open-Chimney Tapered Bottom Nosecone (`MECH-CAP-BOT`, `Z = 0.0..34.0 mm`):** `45°` tapered frustum (`Ø40.0 → Ø71.0 mm` over `15.5 mm`, `4.01 mm` core-socket corner wall, `2.80 mm` wall behind `MECH-GASKET-1` `60 × 3.5 mm` VMQ50 O-ring) topped by a `45°` outward watershed lip bevel. Features a `22 × 22 mm` (`R3`, `4.76 cm²`) open chimney air inlet with a recessed `28.4 × 28.4 × 0.8 mm` pocket clamping a `304` stainless `1 mm` insect mesh square beneath the aluminum core end, locked by a single `M4 × 50 mm` A2 stainless cross-bolt at `Z = 12.5 mm` (`Z_rel = 6.5 mm`, outside the sealed optical chamber), and a backed `1.8 × 2.5 mm` rounded-square neutral-sealant V-groove (`2.24 mm` corner hub wall) on top of the `Ø49 mm` central hub (`Z = 31.5..34.0 mm`) sealing the core socket from the optical chamber before PMMA installation. Prints upright with `0.000 mm²` overhang.
- **Top Electronics Chassis (`MECH-TOP-BASE`, `Z = 120.0..222.8 mm`):** Upper `Ø71.0 mm` shroud socket (`MECH-GASKET-2` + uncrossed `±Y` `9.0 × 7.5 mm` JST-XH wire channels) flaring at `45°` to a `26.0 mm` tall `Ø94.0 mm` side-port ring (`Ø78.0 mm` interior dry bay) housing:
  - **`+X` Vertical PCB Cradle, Captive `M3` Hex Nuts & `15.6 × 15.6 mm` Thermal-Bridge Chute:** Solid `1.5 mm` insulating barrier (`X = 15.55..17.05 mm`) shielding `J1`/`J4` pins, two `9.0 mm`-wide vertical stanchions (`Y = ±14.0 mm`) with `45°`-roofed side-entry pockets holding `4×` DIN 934 `M3` hex nuts (`1.00 mm` back wall, `1.35 mm` front lip, `6.0 mm` stepped front pads inside `H1..H4`'s `Ø6.2 mm` keepouts), and a closed-perimeter `15.6 × 15.6 mm` captive chute (`Z = 199.0..214.4 mm` + `45°` gable roof, zero overhang) directly behind `U1/U2` (`B.Cu` at `X = 20.5 mm`, `5.5 mm` nom / `5.3 mm` WC gap to anodized Al core) holding two `1.0 mm` dielectric silicone pads sandwiching `15 × 15 × 0.5 mm` brass shims. `J1` sits at deck level (`Z_mouth = 171.32 mm`, `26.32 mm` above the `Z = 145.0 mm` bay floor) with its wide slot along `±Y` so a standard left/right `90°` USB-C cable (`<= 18.0 mm` plug) mates in open air (`2.68 mm` clear of baffle) and curves smoothly to `+Y`.
  - **`+Y` Compressing Split Cable Clamp (`MECH-CABLE-CLAMP`):** `45°`-gable port passing an intact straight charger-end USB-C plug outward during assembly, with an internal dry-bay zip-tie strain-relief post and a pre-mirrored L+R `45°`-wedge split clamp (`1.2 mm` axial flange standoff so wedges drive real radial compression, `5.5 × 3.4 mm` X-slotted `M3 × 14` pan-head bolt slots into blind `M3 × 5.0` inserts with `4.03 mm` solid dry-bay wall, and a full `10.5 mm × Ø7.4 mm` chamber compressing a `10 mm` slit `Ø8 × Ø4 mm` silicone sleeve with a thin neutral sealant bead on the flange face). Sits `4.8 mm` inside the `Ø118 mm` eaves and `4.5 mm` below the eaves underside.
  - **`-X` Recessed Draining `SW1` Cove (`C&K 7211SYZBE` + `759D02000` Boot):** `5.5 mm` recessed `32.0 mm`-wide alcove (`X = -41.5 mm`, `18°` outward-sloping draining floor, `42.8°` ceiling) with a true round `Ø6.50 mm` circular bore (360° flat boot seal), bushing keyway notch, and internal anti-rotation pocket (`8.33 mm` rear lug clearance to worst-case Al core), keeping the boot `3.4–5.3 mm` inside `MECH-CAP-TOP`'s `-X` visor brow (`X = -63.5 mm`).
  - **`-Y` Downward-Draining Breather Vent (`MECH-VENT-1`):** `Ø9.5 × 0.8 mm` flat horizontal pocket on the dry-bay floor (`Y = -33.8 mm`) over a `35°` downward-outward `Ø3.5 mm` bore exiting the `45°` underside flare (`Y = -38.9, Z = 136.9 mm`) so water drains by gravity.
  - **Axial Face O-Ring Deck & `4×` Gusseted Bolt Ears (`R = 51.0 mm`):** Flat `Z = 171.0 mm` deck carrying a `3.4 × 1.88 mm` axial face groove (`MECH-GASKET-3`, `88 × 2.5 mm` VMQ50, `24.8%` squeeze, `76.8%` fill) and a `2.0 mm` centering pilot lip, surrounded by `4×` `43°`-gusseted flush `M3 × 12` CSK ears (`2.25 mm` solid rim around CSK).
- **Top Weatherproof Rain Bell (`MECH-CAP-TOP`, `Z = 171.0..257.0 mm`):** Overhanging `Ø118.0 mm` circular rain eaves with a `1.4 mm` support-free `45°` underside drip kerf, flexible `2.0 mm`-wall `+Y` snap-in cable C-clip + zip-tie slot, and `-X` rain visor brow with `0.6 mm`-deep debossed `OFF / UV / ALL` labels and `0 / 1 / 2` tactile ribs; straight `Ø85.0 mm` bore (`10.18 mm` wire-bend space behind `J2`/`J3`) with a `0.60 mm` unbroken translucent internal dimple opposite `D12` (`Y = +16.0, Z = 190.9 mm`); unbroken `30.6°` lofted rain roof (`0` roof holes, `0` bell side holes, `0` collar side holes); and `10.0 mm` vertical `40.4 × 40.4 mm` collar with `30°`-chamfered top lip and backed `2.5 × 3.0 mm` neutral-sealant V-groove.
- **Open-Chimney Clear-Anodized Al Core & Ventilated Rain Finial (`MECH-HS-CORE`, `MECH-PLUG-TOP`):** Standard `300.0 mm` length of `30 × 30 × 2.0 mm` clear/silver-anodized 6063-T6 tube (`181 g`, `26 × 26 mm` open bore, `49.0 mm` external protrusion above collar, `ε_IR ≈ 0.82`). `MECH-PLUG-TOP` drops 4 corner legs `21 mm` into the bore, clamps the upper `28 × 28 mm` stainless mesh square onto the tube rim, opens `4× 14.4 × 9.0 mm` exhaust ports (`5.18 cm²`) under an overhanging `38 × 38 mm` `45°` rain hood, and prints alongside `2×` symmetric `6.0 mm` flanged `M4` bail spools (`Ø10.2 mm` flanges, `Ø7.2 mm` barrel, `Ø4.4 mm` bore) clamped outside the `±X` aluminum tube walls by the top `M4 × 50 mm` A2 stainless cross-bolt + `M4` washers + nyloc nut (`48.6 mm` total stack) to carry a bent `~2.0–2.5 mm` steel coat-hanger wire hanging bail (`~Ø8 mm` closed eyes riding cleanly on the spools over the stainless bolt).

### Mass Budget (From CAD B-Rep Volumes in [cad_verification.json](cad/cad_verification.json))

| Component | FDM White ASA (4 walls / 25% infill) | FDM White PETG (4 walls / 25% infill) |
|---|---:|---:|
| **3D-Printed Lamp Parts (`5` functional parts, `~393 cm³`)** | `~261 g` | `~309 g` |
| **Clear-Anodized Al 6063-T6 Core (`30 × 30 × 2.0 × 300 mm`)** | `181.1 g` | `181.1 g` |
| **Extruded Clear XT PMMA Shroud (`Ø60 × 54 × 3.0 × 115 mm`)** | `72.9 g` | `72.9 g` |
| **`8×` Convoy Cu Stars, Driver PCB, Bridge, Switch, M3/M4 HW, Mesh & O-Rings** | `94.0 g` | `94.0 g` |
| **Total Lamp Mass (`324.0 mm` body; Tip `Ø40 × 34.0 mm`, Eaves `Ø118 mm`)** | **`~609 g`** | **`~657 g`** |

## 2. Coupled 8-Node Thermal Verification ([thermal_summary.json](thermal/thermal_summary.json))

Solved with [thermal_analysis.py](thermal/thermal_analysis.py) reading geometry from [cad_params.json](cad/cad_params.json) (`30 × 30 × 2.0 × 300 mm` clear-anodized Al `ε = 0.82`, open `26 × 26 mm` screened chimney with conservative mesh/turn loss `K = 8.0`, captive `15 × 15 mm` silicone-pad/brass-shim PCB bridge `R = 8.5 K/W`, realistic vertical `F.Cu` convection + inner bell radiation, `25%`-infill wall conduction, `+2 K` chimney plume preheating) and electrical losses from [sim_summary.json](../circuit_design/sim/outputs/sim_summary.json) (`P_PCB = 0.321 W` 4-UV / `0.508 W` 8-ALL nom / `0.842 W` worst-case; `14%` interior optical re-absorption). Checked against UV `100 °C`, PMMA `75 °C`, commercial `LM393` `T_PCB <= 70 °C`, and polymer HDT on **all core-contacting plastic nodes** (`T_plastic_max <= 70 °C` PETG / `95 °C` ASA):

| Ambient & Orientation | Mode | `T_core,Vis` (°C) | `T_j,UV` (°C) (`<=100`) | `T_shroud` (°C) (`<=75`) | `T_bay` (°C) | `T_PCB` (°C) (`<=70`) | `Q_bore` (W) | Status (PETG / ASA) |
|---|---|---:|---:|---:|---:|---:|---:|:---:|
| `15 °C` Vertical | `8-ALL Nom (40% UV)` | `42.2` | `43.0` | `26.6` | `26.4` | `36.6` | `1.84` | **PASS / PASS** |
| `22 °C` Vertical *(UK Night)* | `4-UV Nom (40% UV)` | `37.4` | `39.5` | `28.8` | `28.9` | `35.3` | `0.94` | **PASS / PASS** |
| `22 °C` Vertical *(UK Night)* | `8-ALL Nom (40% UV)` | `48.8` | `49.6` | `33.5` | `33.2` | `43.2` | `1.79` | **PASS / PASS** |
| `22 °C` Vertical *(UK Night)* | `8-ALL DS-RealWPE` | `55.4` | `56.5` | `36.1` | `36.2` | `49.8` | `2.35` | **PASS / PASS** |
| `30 °C` Vertical *(Warm Night)* | `4-UV Nom (40% UV)` | `45.1` | `47.2` | `36.7` | `36.7` | `43.0` | `0.90` | **PASS / PASS** |
| `30 °C` Vertical *(Warm Night)* | `8-ALL Nom (40% UV)` | `56.3` | `57.2` | `41.3` | `41.0` | `50.7` | `1.73` | **PASS / PASS** |
| `30 °C` Vertical *(Warm Night)* | `8-ALL DS-RealWPE` | `62.9` | `64.0` | `43.9` | `43.9` | `57.2` | `2.28` | **PASS / PASS** |
| `35 °C` Vertical *(Heatwave)* | `8-ALL Nom (40% UV)` | `61.0` | `61.9` | `46.3` | `45.8` | `55.4` | `1.69` | **PASS / PASS** |
| `35 °C` Vertical *(Heatwave)* | `8-ALL DS-RealWPE` | `67.6` | `68.6` | `48.9` | `48.7` | `61.8` | `2.23` | **PASS / PASS** |

All `8/8` vertical UK-night (`<= 22 °C`), `12/12` vertical `15–30 °C`, and `16/16` vertical `15–35 °C` Real-WPE cases pass **both PETG (`<= 70 °C`) and ASA (`<= 95 °C`)** alongside all LED, PMMA, and `LM393` (`T_PCB <= 57.2 °C` at `30 °C` WC / `61.8 °C` at `35 °C` WC) limits.

### Thermal Configuration Comparison (`30 °C` Vertical Still Air, `8-ALL Nom / DS-RealWPE`)

| Core & PCB Thermal Configuration | `T_j,UV` (Nom / DS-RealWPE) | `T_core,Vis` (Nom / DS-RealWPE) | `T_PCB` (Nom / DS-RealWPE) |
|---|---:|---:|---:|
| **Primary: Open Chimney + Anodized Al (`ε=0.82`) + PCB Thermal Bridge** | **`57.2 / 64.0 °C`** | **`56.3 / 62.9 °C`** | **`50.7 / 57.2 °C`** |
| **Open Chimney + Anodized Al (`ε=0.82`), No PCB Bridge** | `57.0 / 63.7 °C` | `56.2 / 62.6 °C` | `53.8 / 63.8 °C` |
| **Open Chimney + Bare Mill Al (`ε=0.10`), No PCB Bridge** | `63.3 / 71.3 °C` | `62.5 / 70.2 °C` | `56.4 / 66.8 °C` |
| **Closed Bore + Bare Mill Al (`ε=0.10`), No PCB Bridge** | `79.8 / 92.0 °C` | `79.3 / 91.3 °C` | `64.3 / 76.4 °C` |

## 3. CAD Files & Renders

- **Parametric Generator & Audit:** [params.py](cad/params.py), [cad_params.json](cad/cad_params.json), [generate_cad.py](cad/generate_cad.py), [cad_verification.json](cad/cad_verification.json)
- **6 Support-Free 3D-Printable Parts:** [mech_cap_bot.step](cad/mech_cap_bot.step), [mech_top_base.step](cad/mech_top_base.step), [mech_cable_clamp.step](cad/mech_cable_clamp.step) *(pre-mirrored L+R pair)*, [mech_cap_top.step](cad/mech_cap_top.step), [mech_plug_top.step](cad/mech_plug_top.step), [mech_drill_jig.step](cad/mech_drill_jig.step), [lepiled_assembly.step](cad/lepiled_assembly.step)
- **Renders & Thermal Plots:** [assembly_iso.png](cad/assembly_iso.png), [assembly_section_xz.png](cad/assembly_section_xz.png), [assembly_section_yz.png](cad/assembly_section_yz.png), [cap_bot_detail.png](cad/cap_bot_detail.png), [top_base_detail.png](cad/top_base_detail.png), [cap_top_detail.png](cad/cap_top_detail.png), [thermal_margins.png](thermal/thermal_margins.png), [thermal_ambient_sweep.png](thermal/thermal_ambient_sweep.png), [thermal_network_comparison.png](thermal/thermal_network_comparison.png)
