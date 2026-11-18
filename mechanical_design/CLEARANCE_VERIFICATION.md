# M3 Dimensional Clearance, Tolerance & CAD Verification Report

**Sources of Truth:** `mechanical_design/cad/params.py`, `mechanical_design/cad/cad_params.json`, `mechanical_design/cad/cad_verification.json`, `circuit_design/INTERFACE_CONTRACT.md`  
**CAD Generator:** `build123d==0.13.0` (`cadquery-ocp-novtk==8.0.1.1.0`), verified via `trimesh==5.2.1` + all-pairs B-Rep solid intersection (`&`) + STL overhang/ray-cast audits.

---

## 1. Global Coordinate System & Axial Z-Stack (`0.0` to `386.7 mm`)

- **Origin `(0, 0, 0)`**: Center of bottom resting face of `MECH-HS-EXT-BOT`.
- **`+Z`**: Vertically upward along lamp centerline toward `MECH-CAP-TOP` and `MECH-EYE-1`.
- **`+X, +Y`**: Normal to the 4 flat faces of `MECH-HS-CORE` (`40.0 × 40.0 mm`).

| Z Range (mm) | Component / Feature | Key Dimensional & Thermal Role |
|---|---|---|
| `0.0 – 70.0` | `MECH-HS-EXT-BOT` (`Fischer SK LED R 80 SA`, `Ø 80.0 × 70.0 mm`) | Flat base at `Z = 0.0`; `Ø 34 mm` core + `22` radial fins (`1.35 K/W` catalog) |
| `70.0 – 78.0` | `MECH-ADAPT-BOT` (`Ø 90.0 × 3.0 mm` + `Ø 59.0 × 5.0 mm` pedestal) | Bolted to `SK LED R 80 SA` (`4× M3×14 CSK` at `R = 11.0 mm`); Kapton-lined `1.8 mm` pockets for `J2/J3` (`(0, +19.2)`), `J4` (`(-1.4, -2.5)`), & `J1/TP1/TP2` (`(0, -19.5)`, `21.0 × 7.0 mm`); `4× M2.5` tapped holes |
| `78.0 – 78.5` | `MECH-TIM-PCB` (`0.5 mm` `TG-A6200` `6.2 W/m·K` gap pad) | Electrically isolates & thermally couples PCB `B.Cu` plane (`10.94 cm²` active area after `J1/TP1/TP2/J2..J4/H1..H4` cutouts) |
| `78.5 – 80.1` | Driver PCB (`36.0 × 46.0 × 1.6 mm` FR4, `2.0 mm` corner radii) | `H1..H4` at `(±14.0, ±19.0)`; `1.8 mm` TH pins (`J1` `SH3/SH4` at `Y=-22.36`, `TP1/TP2`, `J2..J4`) sit inside `2.3 mm` combined relief (`0.64 mm` `-Y` pocket margin) |
| `80.1 – 84.9` | Driver PCB SMD envelope (`≤ 4.8 mm`; `L1/L2` at `(-13.80/+5.20, +11.80)`) | `J1` (`USB4085-GF-A`, `Y ∈ [-25.34, -16.17]` w/ carved `4.55 mm` pocket `Y ∈ [-25.34, -20.79]`) mid-plane at `Z = 81.98 mm` |
| `80.1 – 89.9` | Mated `J2..J4` wire headers (`9.8 mm` max height) | Clears `40.3°` conical cavity ceiling at `R = 23.82 mm` (`Z = 96.68 mm`) by `6.78 mm` |
| `73.0 – 144.0` | `MECH-CAP-BOT` (`Ø 92.0 mm` base -> `45°` step -> `Ø 84.0 mm` skirt) | Clamped to `MECH-ADAPT-BOT` via `4× M3×8` at `R = 40.2 mm` (`45°`) + `MECH-GASKET-3` (`66×2.0 mm`); unobstructed `SW1` (`X=16.0..42.5`) & `M16` (`Y=-40.5..-16.0`) entry corridors; Option B `USB_C` recessed stop at `Y = -33.10 mm` + `2.600 mm` bezel wall (`Y_in = -30.50 mm`, requires `≥ 12.31 mm` [`13.0 mm` nom] extended-barrel USB-C cable) |
| `126.0 – 132.0` | PETG/PA12 Thermal Bulkhead (`6.0 mm` min center thickness) | Decouples `MECH-HS-CORE` (`Z ≥ 132.0`) from PCB cavity (`R_bulkhead = 11.20 K/W`); `2× M4×16` DIN 7991 CSK bolts + `M4` nylon CSK washers (`c_clear = 12.0 mm`) at `(±9.0, 0.0)` |
| `132.0 – 144.0` | Bottom Glass & Core Socket (`12.0 mm` deep) | `MECH-GASKET-1` (`68×3.5 mm` VMQ70) in `R=33.20..38.10 × 2.65 mm` groove (`Z = 129.35..132.0`); `MECH-ANCHOR-BOT` cross-pinned at `Z = 138.0` |
| `132.0 – 282.0` | `MECH-TUBE-1` (`75/68/3.5 × 150.0 ± 1.0 mm` Borosilicate 3.3) | Exposed window `Z = 144.0 – 270.0 mm` (`126.0 mm`) |
| `132.0 – 297.0` | `MECH-HS-CORE` (`40 × 40 × 3 mm` Al 6063, **`L = 165.0 mm`**) | Passes through `MECH-CAP-TOP` aperture, `0.5 mm` proud of flat plastic top (`296.5 mm`) via `4×` `0.5 mm` spacers |
| `167.0 – 247.0` | `4× MECH-MCPCB-1..4` (`20.0 × 80.0 × 1.6 mm` Al MCPCB) | Centered in glass window (`Z = 207.0` mid); Vis at `Z = 189.0`, UV at `Z = 225.0`, wire pads at `y = -26.0` |
| `270.0 – 296.5` | `MECH-CAP-TOP` (`Ø 84.0 mm` OD, `26.5 mm` tall, 100% flat top) | `12.0 mm` glass socket + `MECH-GASKET-2` (`68×3.5 mm`, `2.65 mm` deep); `3.10 mm` solid plastic above groove (`euler = 0, genus = 1`); `4× 0.5 mm` shims (`MECH-FAST-3W`) |
| `283.0 – 297.0` | `MECH-ANCHOR-TOP` (`33.2 × 33.2 × 14.0 mm` Al 6061 block) | Drilled `Ø 6.0 mm` center + `2× M4×40` flush CSK cross-pins at `(0, ±9.0, 290.0)` in `±1.5 mm` core slots |
| `297.0 – 300.0` | `MECH-ADAPT-TOP` (`Ø 76.0 × 3.0 mm` Al 6061 disc) | Direct metal-to-metal TIM contact to `MECH-HS-CORE`; bolts `MECH-CAP-TOP` at `R = 34.0 mm` (`4× M3×8`) |
| `300.0 – 350.0` | `MECH-HS-EXT-TOP` (`Fischer SK 578/50 SA`, `Ø 60.0 × 50.0 mm`) | Bolted to `MECH-ADAPT-TOP` (`4× M3×8 CSK` at `R = 8.5 mm`) + center `Ø 6.5 mm` bore |
| `284.0 – 386.7` | `MECH-EYE-1` (`M6 × 75 mm` stainless eye bolt) | Clamps `MECH-HS-EXT-TOP` + `MECH-ADAPT-TOP` directly to `MECH-ANCHOR-TOP` |

---

## 2. Deterministic Clearance, Wall-Thickness & Tolerance Audit (`params.py`)

All 34 parametric assertions in `mechanical_design/cad/params.py` pass:

| Check Name | Measured Value | Requirement | Status |
|---|---|---|---|
| `pcb_radial_clearance_mm` | **`2.099 mm`** | `≥ 1.0 mm` | PASS |
| `pcb_on_pedestal_rim_mm` | **`1.099 mm`** | `≥ 0.5 mm` | PASS |
| `pcb_cavity_edge_headroom_mm` | **`9.900 mm`** | `≥ 8.0 mm` | PASS |
| `pcb_jst_cone_headroom_mm` | **`6.775 mm`** | `≥ 5.0 mm` | PASS |
| `bulkhead_thickness_mm` | **`6.000 mm`** | `≥ 5.0 mm` | PASS |
| `m16_above_gasket3_mm` | **`6.460 mm`** | `≥ 2.5 mm` | PASS |
| `m16_nut_to_pcb_y_mm` | **`12.000 mm`** | `≥ 3.0 mm` | PASS |
| `m16_roof_below_gasket1_mm` | **`17.100 mm`** | `≥ 2.5 mm` | PASS |
| `usbc_above_base_mm` | **`4.730 mm`** | `≥ 2.5 mm` | PASS |
| `usbc_above_gasket3_mm` | **`2.680 mm`** | `≥ 2.5 mm` | PASS |
| `usbc_roof_below_gasket1_mm` | **`36.120 mm`** | `≥ 2.5 mm` | PASS |
| `usbc_bezel_wall_thick_mm` | **`2.600 mm`** | `≥ 2.5 mm` | PASS |
| `usbc_min_extended_barrel_mm` | **`12.310 mm`** | `≤ 13.0 mm` (mandatory extended-barrel Option B cable) | PASS |
| `usbc_extended_barrel_margin_mm` | **`0.690 mm`** | `≥ 0.25 mm` | PASS |
| `sw1_wall_window_mm` | **`2.500 mm`** | `2.0 – 3.5 mm` (`SW1_BOOT`) | PASS |
| `sw1_radial_to_pcb_mm` | **`5.810 mm`** | `≥ 1.0 mm` | PASS |
| `sw1_z_above_smd_mm` | **`4.670 mm`** | `≥ 2.0 mm` | PASS |
| `pilot_to_glass_id_min_mm` | **`0.050 mm`** | `> 0.02 mm` | PASS |
| `skirt_to_glass_od_max_mm` | **`0.400 mm`** | `≥ 0.2 mm` | PASS |
| `core_corner_to_glass_id_min_mm` | **`4.612 mm`** | `≥ 1.0 mm` | PASS |
| `led_vis_to_glass_id_min_mm` | **`9.110 mm`** | `≥ 1.0 mm` | PASS |
| `m3_head_to_glass_id_min_mm` | **`8.500 mm`** | `≥ 1.0 mm` | PASS |
| `bot_cav_to_gasket3_wall_mm` | **`2.500 mm`** | `≥ 2.5 mm` | PASS |
| `bot_gasket3_to_insert_wall_mm` | **`2.650 mm`** | `≥ 2.5 mm` | PASS |
| `bot_insert_to_chamfer_wall_mm` | **`2.550 mm`** | `≥ 2.5 mm` | PASS |
| `glass_skirt_min_wall_mm` | **`3.600 mm`** | `≥ 2.5 mm` | PASS |
| `pilot_corner_min_wall_mm` | **`4.209 mm`** | `≥ 2.5 mm` | PASS |
| `top_insert_to_core_wall_mm` | **`2.959 mm`** | `≥ 2.5 mm` | PASS |
| `top_insert_to_chamfer_wall_mm` | **`4.750 mm`** | `≥ 2.5 mm` | PASS |
| `top_insert_above_gasket2_mm` | **`3.100 mm`** | `≥ 2.5 mm` | PASS |
| `glass_oring_squeeze_min_pct` (`149 mm` rigid) | **`10.0 %`** | `≥ 10.0 %` | PASS |
| `glass_oring_squeeze_nom_pct` (`150 mm`) | **`24.3 %`** | `20.0 – 35.0 %` | PASS |
| `glass_oring_squeeze_max_pct` (`151 mm` rigid) | **`38.6 %`** | `≤ 45.0 %` | PASS |
| `gland_fill_at_151` | **`0.9133`** (`91.3%`) | `≤ 0.92` | PASS |

---

## 3. All-Pairs B-Rep Interference & Kinematic Insertion Verification

Executed via `build123d` solid boolean intersection (`&`) across **all `N*(N-1)/2 = 153` unordered pairs** of all `18` physical assembly solids (including `anchor_bot`, `anchor_top`, `eye_bolt`, `fasteners_anchors`, `spacer_washers`, `J1`/`TP1`/`TP2`/`J2..J4` TH pins, `sw1_assy`, `m16_assy` / single-solid fused `13.0 mm` extended-barrel `usbc_plug_assy` inserted `4.55 mm` into `J1`'s carved pocket with `0.0 mm` shell-to-overmold gap; Option B `USB_C` requires `≥ 12.31 mm` extended-barrel USB-C cable per `datasheets/usb4085.pdf` pp. 1–2, whereas primary baseline `M16_GLAND` via `TP1`/`TP2` is unaffected) across **both** `M16_GLAND` and `USB_C` modes at **both**:
- **Nominal:** `glass_ID = 68.0 mm`, `glass_OD = 75.0 mm`, `glass_length = 150.0 mm`, `core_W = 40.0 mm`
- **Worst-Case Tolerance Corner:** `glass_ID = 66.5 mm`, `glass_OD = 76.0 mm`, `glass_length = 151.0 mm`, `core_W = 40.5 mm`

| Configuration | Total Pairs Checked | Non-Zero Overlaps (`> 1e-4 mm³`) | Max Intersection Volume (`mm³`) | Result |
|---|---:|---:|---:|---|
| `M16_GLAND` Nominal | `153` | `0` | `0.000000` | **PASS** |
| `M16_GLAND` Worst-Case Corner (`151.0 mm` glass) | `153` | `0` | `0.000000` | **PASS** |
| `USB_C` Nominal | `153` | `0` | `0.000000` | **PASS** |
| `USB_C` Worst-Case Corner (`151.0 mm` glass) | `153` | `0` | `0.000000` | **PASS** |

### 3.1 Kinematic B-Rep Alcove & Bulkhead Bolt Insertion Sweeps (`check_alcove_insertion`)

| Insertion Sweep Path (from `Z = 73.0 mm` bottom opening to seated pose) | Waypoints | Max Intersection (`mm³`) | Result |
|---|---:|---:|---|
| `sw1_insertion` (`8.89×12.7×6.86` body + lugs + `Ø6.35×8.89` bushing) | `27` | `0.000000` | **PASS** |
| `m16_nut_insertion` (`22.0 mm AF × 5.0 mm` hex locknut) | `27` | `0.000000` | **PASS** |
| `m4x16_bolt_insertion` (`2× M4×16` DIN 7991 CSK straight `+Z` sweep) | `30` | `0.000000` | **PASS** |

---

## 4. Exported STL Manifold & Overhang Audit (`trimesh 5.2.1`)

| Exported Model | B-Rep Vol (`mm³`) | STL Vol (`mm³`) | Watertight / Winding | Euler χ (Genus $g$) | Triangles | Off-Bed `> 46°` Area (`mm²`) |
|---|---:|---:|---|---|---:|---:|
| `mech_cap_bot.stl` (FDM, M16) | `306,918.9` | `306,902.4` | `True` / `True` | `-14` (`g = 8`) | `43,950` | `0.022` (**PASS**) |
| `mech_cap_top.stl` (FDM, Flat) | `85,236.7` | `85,234.7` | `True` / `True` | `0` (`g = 1`) | `25,132` | `0.005` (**PASS**) |
| `mech_cap_bot_sls.stl` (SLS PA12) | `306,951.0` | `306,934.5` | `True` / `True` | `-14` (`g = 8`) | `43,950` | — |
| `mech_cap_top_sls.stl` (SLS PA12) | `85,256.4` | `85,254.4` | `True` / `True` | `0` (`g = 1`) | `25,132` | — |
| `mech_cap_bot_usbc.stl` (FDM, USB-C) | `313,905.9` | `313,889.6` | `True` / `True` | `-14` (`g = 8`) | `42,500` | `0.022` (**PASS**) |

- **Vectorized USB-C Bezel Wall STL Ray-Cast (`mech_cap_bot_usbc.stl`):** `3,705` rays scanned across `X ∈ [-7.0, +7.0]` × `Z ∈ [77.5, 93.5]` (`0.25 mm` step; `2,789` wall rays, `916` through-slot rays) → **`0` anomalies**, **`min_bezel_wall_mm = 2.6000 mm ≥ 2.500 mm`** (at `(X=0.0, Z=88.75)`).

---

## 5. Visual Inspection Sign-Off (`render_cad.py`)

All 6 offscreen PyVista renders (`assembly_iso.png`, `assembly_section_xz.png`, `assembly_section_yz.png`, `cap_bot_detail.png`, `cap_top_detail.png`, `cap_bot_usbc_detail.png`) were directly inspected:
- **`assembly_iso.png`**: Clear title framing above `MECH-EYE-1`, clean `SK LED R 80 SA` bottom radiator, stepped `Ø 92/84 mm` `MECH-CAP-BOT`, `SW1` + `M16` cutouts, borosilicate window, `MECH-CAP-TOP`, and `SK 578/50 SA`.
- **`assembly_section_xz.png` & `assembly_section_yz.png`**: Verify `40.3°` conical PCB cavity roof, `J1/TP1/TP2` + `J2/J3` + `J4` pin relief pockets in `MECH-ADAPT-BOT` & `MECH-TIM-PCB`, `2× M4×16` bulkhead bolts into `MECH-ANCHOR-BOT`, captive `22.5 mm` AF `M16` hex alcove, `45°` `SW1` roof, and `MECH-EYE-1` threading cleanly through `MECH-ANCHOR-TOP` with offset `M4×40` cross-pins.
- **`cap_bot_detail.png`, `cap_top_detail.png`, `cap_bot_usbc_detail.png`**: Verify flat `MECH-CAP-TOP` print bed face, `45°` V-roof `MECH-GASKET-3`, `45°` teardrop spot-faces, and intact `9.5 × 3.8 mm` USB-C bezel + `45°` pitched overmold roof.
