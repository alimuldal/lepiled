# LepiLED DIY Maxi Switch — Mechanical & Thermal Design (Rev 4.0 / Option 2)

## 1. Architecture Summary

The Rev 4.0 fanless enclosure pairs a `75/68/3.5 × 150 mm` borosilicate 3.3 glass cylinder (`MECH-TUBE-1`) with a `40 × 40 × 3 × 165.0 mm` matte-black-coated aluminum 6063 core (`MECH-HS-CORE`) carrying four `20 × 80 × 1.6 mm` aluminum MCPCB LED strips (`MECH-MCPCB-1..4`, 1 UV + 1 Vis LED per face). A `6.0 mm` thermally isolating bulkhead (`R_bulkhead = 11.20 K/W`) separates the LED column from the bottom electronics chamber, while identical `Ø60 × 50 mm` black-anodized **`Fischer Elektronik SK 578/50 SA`** radial heatsinks (`MECH-HS-EXT-TOP` and `MECH-HS-EXT-BOT`, `£5.88` each) reject LED heat upward and Driver PCB heat downward. Overall height is `330.0 mm` (excluding M6 hanging eye bolt).

- **Power Entry Options:** Two drop-in 3D-printable bottom end-caps are provided (support-free FDM PETG/ASA or SLS PA12):
  - **Option A (`mech_cap_bot.step/.stl`):** Weatherproof `M16 × 1.5` IP68 cable gland (`MECH-GLAND-1`) with captive anti-rotation hex pocket, wired to `TP1/TP2` for captive `18–24 V` battery or sealed PD-trigger pigtails.
  - **Option B (`mech_cap_bot_usbc.step/.stl`):** Direct-mate `13.6 × 7.8 mm` recessed USB-C tunnel aligned to `J1` (`Y = -25.76 mm`), allowing any standard `6.65 mm` USB-C PD laptop-charger or power-bank plug to mate directly without extended-barrel cables.
- **Hanging Load Path:** 100% metal-to-metal load path from `MECH-EYE-1` (`M6 × 75 mm` stainless eye bolt) through `MECH-HS-EXT-TOP` and `MECH-ADAPT-TOP` into the cross-pinned `MECH-ANCHOR-TOP` inside `MECH-HS-CORE` (zero tensile load on 3D-printed plastic).

## 2. Coupled 2D/3D FVM Thermal Verification (`20/20 PASS`)

Executed via [thermal_analysis.py](file:///home/alimuldal/src/lepiled/mechanical_design/thermal/thermal_analysis.py) using genuine 2D FVM MCPCB copper-spreading PDEs (`R_diel_UV = 15.29 K/W`, `R_diel_Vis = 18.89 K/W`) and a 3D 3-layer FVM Driver PCB + `0.5 mm TG-A6200` (`6.2 W/m·K`) + `MECH-ADAPT-BOT` (`2.5 mm` relief pockets) solver synced to Option 2's `0.500 W` nominal / `0.819 W` worst-case PCB loss ([thermal_summary.json](file:///home/alimuldal/src/lepiled/mechanical_design/thermal/thermal_summary.json)).

| Ambient & Orientation | Mode | `Q_PCB` (W) | `T_j,UV` (°C) (`<=100`) | `T_j,Vis` (°C) (`<=150`) | `T_PCB,bot` (°C) (`<=55`) | `T_PCB,top` (°C) (`<=55`) | `T_j,U1` JEDEC (°C) (`<=125`) | Status |
|---|---|---:|---:|---:|---:|---:|---:|:---:|
| `22 °C` Vertical | `4-UV Nom` | `0.295` | `44.3` | `31.9` | `27.3` | `28.1` | `37.1` | PASS |
| `22 °C` Vertical | `8-ALL Nom (40%UV)` | `0.500` | `50.4` | `57.0` | `30.1` | `31.4` | `40.5` | PASS |
| `30 °C` Horizontal | `4-UV Nom` | `0.295` | `52.4` | `40.0` | `35.4` | `36.2` | `45.3` | PASS |
| `30 °C` Horizontal | `8-ALL Nom (40%UV)` | `0.500` | `58.8` | `65.4` | `38.5` | `39.8` | `48.9` | PASS |
| `30 °C` Horizontal | `8-ALL DS-RealWPE` | `0.819` | `66.2` | `74.9` | `40.9` | `43.0` | `57.8` | PASS |
| `30 °C` Horizontal | `8-ALL DS-100%` (0% optical) | `0.819` | `83.5` | `92.5` | `43.4` | `45.5` | `60.3` | PASS |

**Result:** **Config C (Decoupled Dual `SK 578/50 SA`) passes 20/20 steady-state cases** with `>= 16.5 °C` UV junction margin, `>= 9.5 °C` PCB temperature margin, and `>= 64.7 °C` `AL8860` IC junction margin even in stagnant `30 °C` horizontal air under 0%-optical-efficiency `DS-100%` loading.

## 3. CAD Artifacts & Plots

- **Parameters & Generator:** [params.py](file:///home/alimuldal/src/lepiled/mechanical_design/cad/params.py), [generate_cad.py](file:///home/alimuldal/src/lepiled/mechanical_design/cad/generate_cad.py), [cad_verification.json](file:///home/alimuldal/src/lepiled/mechanical_design/cad/cad_verification.json)
- **3D Printable End-Caps:** [mech_cap_bot.step](file:///home/alimuldal/src/lepiled/mechanical_design/cad/mech_cap_bot.step), [mech_cap_bot_usbc.step](file:///home/alimuldal/src/lepiled/mechanical_design/cad/mech_cap_bot_usbc.step), [mech_cap_top.step](file:///home/alimuldal/src/lepiled/mechanical_design/cad/mech_cap_top.step), [lepiled_assembly.step](file:///home/alimuldal/src/lepiled/mechanical_design/cad/lepiled_assembly.step)
- **Thermal Plots & Renders:** [thermal_margins.png](file:///home/alimuldal/src/lepiled/mechanical_design/thermal/thermal_margins.png), [thermal_ambient_sweep.png](file:///home/alimuldal/src/lepiled/mechanical_design/thermal/thermal_ambient_sweep.png), [thermal_network_comparison.png](file:///home/alimuldal/src/lepiled/mechanical_design/thermal/thermal_network_comparison.png), [render_section.png](file:///home/alimuldal/src/lepiled/mechanical_design/cad/render_section.png)
