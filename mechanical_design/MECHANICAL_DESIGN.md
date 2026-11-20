# LepiLED DIY Maxi Switch — Mechanical & Thermal Design (Rev 4.2 — Lean 1-Off Hobby Build)

## 1. Architecture Summary (Single Stock Aluminum Tube + `20 mm` Copper DTP Stars)

Rev 4.2 strips the mechanical stack down to **one single stock metal part**—a `250.0 mm` length of bare mill-finish `40 × 40 × 3 mm` Al 6063 box section (`MECH-HS-CORE`, zero sawing, zero spray paint, zero CNC milling)—paired with a `75/68/3.5 × 150 mm` borosilicate 3.3 cylinder (`MECH-TUBE-1`) and `8×` off-the-shelf pre-mounted **`20 mm` Copper Direct-Thermal-Path (DTP) LED stars** (`4×` UV at `Z = 163.0 mm`, `4×` Vis at `Z = 127.0 mm`).

- **Monolithic Protruding Core & Hanging Point:** `MECH-HS-CORE` protrudes **`85.5 mm`** above `MECH-CAP-TOP` (`324.0 mm` total height to top of rain cap), eliminating the separate `SK 578/50 SA` heatsink, aluminum adapter disc, internal aluminum anchors, `M6` eye bolt, shims, and bolted thermal joint. A drilled **`Ø8.0 mm` hanging hole** (`Z = 302.0 mm`) gives a direct metal-to-metal carabiner/cord attachment, while a 3D-printed press-fit rain plug (`MECH-PLUG-TOP`, sealed with silicone) weatherproofs the open tube end.
- **Zero Brass Heat-Set Inserts & Single `M3` Fastener Size:**
  - `MECH-CAP-BOT` uses `4×` side-entry **captive `M3` hex-nut pockets** for `MECH-LID-BOT` and a `6.0 mm` thermal isolation bulkhead (`R_bulkhead = 11.20 K/W`).
  - `MECH-LID-BOT` carries `4×` integral `11.5 mm` bosses topped with **`Ø2.45 × 2.0 mm` printed locating pins** passing straight into `driver_pcb`'s isolated NPTH `H1..H4` (zero PCB screws, zero `M2.5` inserts).
  - `MECH-PLUG-BOT` (3D-printed internal plug w/ captive `M3` nuts) replaces the aluminum bottom anchor; `MECH-CAP-TOP` locks onto the protruding tube via `2× M3 × 12 mm` horizontal screws + a `1.5 mm` top silicone-seal chamfer groove.
  - `MECH-DRILL-JIG` clips onto the bottom of `MECH-HS-CORE` to guide all `16× M3` star mounting holes (`M3` nylon insulating washers under all 16 screw heads).

## 2. Coupled Thermal Verification ([thermal_summary.json](file:///home/alimuldal/src/lepiled/mechanical_design/thermal/thermal_summary.json))

Executed via [thermal_analysis.py](file:///home/alimuldal/src/lepiled/mechanical_design/thermal/thermal_analysis.py) modeling `20 mm` Copper DTP stars (`R_sub = 0.50 K/W`, `R_tim = 0.30 K/W` vs legacy `15.29–18.89 K/W` `1.0 W/m·K` MCPCB), the `85.5 mm` bare mill-finish (`ε = 0.20`) protruding core (Churchill-Chu convection + radiation, `r_int_top = 0.0 K/W`), borosilicate glass path, and sealed plastic bottom chamber (`75 °C` PETG limit):

| Ambient & Orientation | Mode | `Q_PCB` (W) | `T_core` (°C) | `T_j,UV` (°C) (`<=100`) | `T_j,Vis` (°C) (`<=150`) | `T_PCB` (°C) (`<=75`) | Status |
|---|---|---:|---:|---:|---:|---:|:---:|
| `22 °C` Vertical (UK Night) | `4-UV Nom` | `0.320` | `39.7` | `41.4` | `39.4` | `39.6` | PASS |
| `22 °C` Vertical (UK Night) | `8-ALL Nom (40%UV)` | `0.550` | `51.3` | `53.0` | `58.1` | `52.1` | PASS |
| `22 °C` Horizontal | `8-ALL DS-RealWPE` | `0.797` | `58.8` | `60.9` | `67.5` | `61.8` | PASS |
| `22 °C` Horizontal | `8-ALL DS-100%` (0% optical) | `0.797` | `75.2` | `78.4` | `87.1` | `72.7` | PASS |
| `30 °C` Horizontal | `4-UV Nom` | `0.320` | `47.2` | `48.8` | `46.8` | `47.2` | PASS |
| `30 °C` Horizontal | `8-ALL Nom (40%UV)` | `0.550` | `58.7` | `60.3` | `65.4` | `59.7` | PASS |
| `30 °C` Horizontal | `8-ALL DS-RealWPE` | `0.797` | `66.2` | `68.3` | `75.0` | `69.5` | PASS |
| `35 °C` Horizontal | `8-ALL Nom (40%UV)` | `0.550` | `63.4` | `65.0` | `70.1` | `64.5` | PASS |
| `35 °C` Horizontal | `8-ALL DS-RealWPE` | `0.797` | `70.8` | `72.9` | `79.6` | `74.2` | PASS |

**Result:** **10/10 PASS at `22 °C`**, **16/16 Real-WPE modes PASS across `22–30 °C`**, and **4/4 Real-WPE modes PASS at `35 °C` horizontal** (`~39–47 °C` UV junction margin at nominal, `~32 °C` margin under stacked datasheet worst-case tolerances). *(Only the artificial `0%-optical-efficiency` bound at `30–35 °C` reaches `80–85 °C` PCB vs `75 °C` PETG / `95 °C` ASA while keeping `T_j,UV <= 90.2 °C < 100 °C`.)*

## 3. CAD Artifacts & Plots

- **Parameters & Generator:** [params.py](file:///home/alimuldal/src/lepiled/mechanical_design/cad/params.py), [generate_cad.py](file:///home/alimuldal/src/lepiled/mechanical_design/cad/generate_cad.py), [cad_verification.json](file:///home/alimuldal/src/lepiled/mechanical_design/cad/cad_verification.json)
- **6 Support-Free 3D-Printable Parts (FDM PETG/ASA):** [mech_lid_bot.step](file:///home/alimuldal/src/lepiled/mechanical_design/cad/mech_lid_bot.step), [mech_cap_bot.step](file:///home/alimuldal/src/lepiled/mechanical_design/cad/mech_cap_bot.step), [mech_cap_top.step](file:///home/alimuldal/src/lepiled/mechanical_design/cad/mech_cap_top.step), [mech_plug_top.step](file:///home/alimuldal/src/lepiled/mechanical_design/cad/mech_plug_top.step), [mech_plug_bot.step](file:///home/alimuldal/src/lepiled/mechanical_design/cad/mech_plug_bot.step), [mech_drill_jig.step](file:///home/alimuldal/src/lepiled/mechanical_design/cad/mech_drill_jig.step), [lepiled_assembly.step](file:///home/alimuldal/src/lepiled/mechanical_design/cad/lepiled_assembly.step)
- **CAD Renders & Thermal Plots:** [assembly_iso.png](file:///home/alimuldal/src/lepiled/mechanical_design/cad/assembly_iso.png), [assembly_section_xz.png](file:///home/alimuldal/src/lepiled/mechanical_design/cad/assembly_section_xz.png), [assembly_section_yz.png](file:///home/alimuldal/src/lepiled/mechanical_design/cad/assembly_section_yz.png), [lid_bot_detail.png](file:///home/alimuldal/src/lepiled/mechanical_design/cad/lid_bot_detail.png), [cap_bot_detail.png](file:///home/alimuldal/src/lepiled/mechanical_design/cad/cap_bot_detail.png), [cap_top_detail.png](file:///home/alimuldal/src/lepiled/mechanical_design/cad/cap_top_detail.png), [thermal_margins.png](file:///home/alimuldal/src/lepiled/mechanical_design/thermal/thermal_margins.png), [thermal_ambient_sweep.png](file:///home/alimuldal/src/lepiled/mechanical_design/thermal/thermal_ambient_sweep.png), [thermal_network_comparison.png](file:///home/alimuldal/src/lepiled/mechanical_design/thermal/thermal_network_comparison.png)
