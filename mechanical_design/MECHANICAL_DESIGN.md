# LepiLED DIY Maxi Switch — Mechanical & Thermal Design (Rev 4.1)

## 1. Architecture Summary (`S1-A`: Zero CNC Milling, Top-Heatsink-Only)

The Rev 4.1 fanless enclosure pairs a `75/68/3.5 × 150 mm` borosilicate 3.3 glass cylinder (`MECH-TUBE-1`) with a `40 × 40 × 3 × 165.0 mm` matte-black-coated aluminum 6063 core (`MECH-HS-CORE`) carrying four `20 × 80 × 1.6 mm` aluminum MCPCB LED strips (`MECH-MCPCB-1..4`, 1 UV + 1 Vis LED per face). A `6.0 mm` thermally isolating bulkhead (`R_bulkhead = 11.20 K/W`) separates the LED column from the bottom electronics chamber.

Because the `20 V` dual-buck driver dissipates only **`0.55 W` nominal (`0.80 W` worst-case)**, Rev 4.1 adopts **`S1-A` (Top-Heatsink-Only + Sealed Plastic Lid)** — eliminating the bottom external heatsink, CNC-milled adapter pedestal, thermal gap pad, Kapton liner, and bottom hub bolts, reducing overall height by `42.0 mm` to **`288.0 mm`** (excluding `M6` eye bolt) and removing **100% of CNC milling** across the entire lamp:

- **Top Heatsink & Zero-CNC Metalwork:** A single **`Fischer Elektronik SK 578/50 SA`** (`Ø60 × 50 mm`, `£5.88`) rejects LED heat upward through an off-the-shelf **`Ø76.2 mm` (3") × `3.0 mm` Al disc** (`MECH-ADAPT-TOP`). Both top and bottom core anchors (`MECH-ANCHOR-TOP/BOT`) are simple cut-and-drilled lengths of stock **`32 × 32 mm` Al square bar**.
- **Positive Butt-Joint Thermal Preload (`Opus B-H3` Fix):** `MECH-ANCHOR-TOP` is pinned via tight **`Ø4.2 mm` round** cross-pin bores (replacing slotted holes) and recessed **`0.50 mm`** below the top end face of `MECH-HS-CORE`. Tightening `MECH-EYE-1` (`M6 × 75 mm` stainless eye bolt) puts 100% metal-to-metal hanging tension on the anchor while actively clamping `MECH-HS-CORE` tightly against `MECH-ADAPT-TOP`.
- **3D-Printed Bottom Lid & Unified USB-C Dew Seal (`Option 3A`):** `MECH-LID-BOT` (`Ø92 × 4.0 mm` flat lid + `4×` integral `11.5 mm` `M2.5` bosses) carries `driver_pcb` on nylon `M2.5 × 6 mm` screws (`Option 2A`) with `9.7 mm` open air under through-hole tails. `MECH-CAP-BOT` features a single unified `-Y` direct-mate USB-C tunnel fronted by a flat **`Ø20.2 × 2.5 mm` panel flange** (`Ø23.6 mm` back-lip groove) accepting a `£0.30` off-the-shelf **`20 mm` rubber membrane grommet** (`MECH-GROMMET-1`, radially slit around any standard `6.65 mm` USB-C cable), backed by acrylic conformal coating on `driver_pcb`.
- **Switch Alcove (`S3`):** The `+X` wall of `MECH-CAP-BOT` is sized for the gold-contact `C&K 7211SYZBE` `DPDT On-On-On` toggle switch (`12.7 × 11.43 × 10.67 mm` body, `1/4-40` bushing + `759D02000` silicone boot).

## 2. Coupled 2D/3D FVM Thermal Verification (`20/20` @ `22–30 °C`, `5/5` @ `35 °C`)

Executed via [thermal_analysis.py](file:///home/alimuldal/src/lepiled/mechanical_design/thermal/thermal_analysis.py) using 2D FVM MCPCB copper-spreading PDEs (`R_diel_UV = 15.29 K/W`, `R_diel_Vis = 18.89 K/W`), a 3D Driver PCB conduction/air-cavity model (`R_eff_bot_pcb = 10.0 K/W` sealed plastic cavity), and top `SK 578/50 SA` radiation/convection correlations synced to Rev 4.1's `0.550 W` nominal / `0.797 W` max PCB loss ([thermal_summary.json](file:///home/alimuldal/src/lepiled/mechanical_design/thermal/thermal_summary.json)), evaluated against a conservative **`75 °C` PETG** PCB/cavity limit (`95 °C` ASA).

| Ambient & Orientation | Mode | `Q_PCB` (W) | `T_j,UV` (°C) (`<=100`) | `T_j,Vis` (°C) (`<=150`) | `T_PCB,top` (°C) (`<=75`) | `T_j,U1` JEDEC (°C) (`<=125`) | Status |
|---|---|---:|---:|---:|---:|---:|:---:|
| `22 °C` Vertical | `4-UV Nom` | `0.320` | `45.3` | `33.0` | `35.4` | `44.7` | PASS |
| `22 °C` Vertical | `8-ALL Nom (40%UV)` | `0.550` | `52.0` | `58.9` | `44.8` | `54.1` | PASS |
| `30 °C` Horizontal | `4-UV Nom` | `0.320` | `53.4` | `41.1` | `43.5` | `52.8` | PASS |
| `30 °C` Horizontal | `8-ALL Nom (40%UV)` | `0.550` | `60.4` | `67.2` | `53.0` | `62.4` | PASS |
| `30 °C` Horizontal | `8-ALL DS-RealWPE` | `0.797` | `68.3` | `77.2` | `60.9` | `76.0` | PASS |
| `30 °C` Horizontal | `8-ALL DS-100%` (0% optical) | `0.797` | `86.2` | `95.5` | `67.3` | `82.4` | PASS |
| `35 °C` Horizontal | `8-ALL Nom (40%UV)` | `0.550` | `65.3` | `72.1` | `57.9` | `67.2` | PASS |
| `35 °C` Horizontal | `8-ALL DS-100%` (0% optical) | `0.797` | `90.9` | `100.3` | `72.1` | `87.2` | PASS |

**Result:** **Rev 4.1 `S1-A` passes 20/20 cases across `22–30 °C`**, **5/5 cases at `35 °C` horizontal** (even under artificial 0%-WPE loading), and **4/4 realistic-WPE modes at `40 °C` horizontal** (`T_j,UV <= 77.9 °C`, `T_PCB <= 70.6 °C`; only artificial 0%-WPE at `40 °C` reaches `77.0 °C` vs `75 °C` PETG / `95 °C` ASA).

## 3. CAD Artifacts & Plots

- **Parameters & Generator:** [params.py](file:///home/alimuldal/src/lepiled/mechanical_design/cad/params.py), [generate_cad.py](file:///home/alimuldal/src/lepiled/mechanical_design/cad/generate_cad.py), [cad_verification.json](file:///home/alimuldal/src/lepiled/mechanical_design/cad/cad_verification.json)
- **3D Printable Parts (Support-Free FDM & SLS):** [mech_lid_bot.step](file:///home/alimuldal/src/lepiled/mechanical_design/cad/mech_lid_bot.step), [mech_cap_bot.step](file:///home/alimuldal/src/lepiled/mechanical_design/cad/mech_cap_bot.step), [mech_cap_top.step](file:///home/alimuldal/src/lepiled/mechanical_design/cad/mech_cap_top.step), [lepiled_assembly.step](file:///home/alimuldal/src/lepiled/mechanical_design/cad/lepiled_assembly.step)
- **CAD Renders & Thermal Plots:** [assembly_iso.png](file:///home/alimuldal/src/lepiled/mechanical_design/cad/assembly_iso.png), [assembly_section_xz.png](file:///home/alimuldal/src/lepiled/mechanical_design/cad/assembly_section_xz.png), [assembly_section_yz.png](file:///home/alimuldal/src/lepiled/mechanical_design/cad/assembly_section_yz.png), [lid_bot_detail.png](file:///home/alimuldal/src/lepiled/mechanical_design/cad/lid_bot_detail.png), [cap_bot_detail.png](file:///home/alimuldal/src/lepiled/mechanical_design/cad/cap_bot_detail.png), [cap_top_detail.png](file:///home/alimuldal/src/lepiled/mechanical_design/cad/cap_top_detail.png), [thermal_margins.png](file:///home/alimuldal/src/lepiled/mechanical_design/thermal/thermal_margins.png), [thermal_ambient_sweep.png](file:///home/alimuldal/src/lepiled/mechanical_design/thermal/thermal_ambient_sweep.png), [thermal_network_comparison.png](file:///home/alimuldal/src/lepiled/mechanical_design/thermal/thermal_network_comparison.png)
