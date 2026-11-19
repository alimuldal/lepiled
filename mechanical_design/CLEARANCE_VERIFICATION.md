# LepiLED DIY Maxi Switch — Mechanical Clearance & Verification Report (Rev 4.1)

All **35 parametric assertions** ([params.py](file:///home/alimuldal/src/lepiled/mechanical_design/cad/params.py)), **6 watertight STEP/STL exports** (`mech_lid_bot`, `mech_cap_bot`, `mech_cap_top` in FDM and SLS), support-free overhang audits, **3,249-ray `20 mm` grommet flange & USB-C tunnel STL ray-cast**, **72-waypoint kinematic insertion sweeps**, and **272 all-pairs B-Rep solid intersection checks** (`136` Nominal + `136` Worst-Case, including all 24 modeled fasteners, `20 mm` rubber grommet, and standard `6.65 mm` USB-C plug) ([generate_cad.py](file:///home/alimuldal/src/lepiled/mechanical_design/cad/generate_cad.py)) pass with **0.000000 mm³** interference ([cad_verification.json](file:///home/alimuldal/src/lepiled/mechanical_design/cad/cad_verification.json)).

## 1. Rev 4.1 Mechanical & Interface Updates

1. **Top-Heatsink-Only & Zero CNC Milling (`S1-A`):** Replaced bottom `SK 578/50 SA`, CNC-milled `MECH-ADAPT-BOT`, and gap pad with 3D-printed `MECH-LID-BOT` (`Ø92 × 4.0 mm` + `4×` integral `11.5 mm` `M2.5` PCB bosses), shortening overall lamp height by `42.0 mm` (`288.0 mm` vs `330.0 mm`, excluding `M6` eye bolt). Switched `MECH-ADAPT-TOP` to stock `Ø76.2 × 3.0 mm` Al disc and `MECH-ANCHOR-TOP/BOT` to stock `32 × 32 mm` Al square bar (`1.0 mm/side` slip fit inside the `34 × 34 mm` core bore).
2. **Top Butt-Joint Preload (`Opus B-H3` Fix):** `MECH-ANCHOR-TOP` is recessed `0.50 mm` below `MECH-HS-CORE` top (`Z = 235.0 mm`) and pinned with tight `Ø4.2 mm` round bores, guaranteeing positive eye-bolt thermal preload into `MECH-ADAPT-TOP`.
3. **Unified USB-C Entry with `20 mm` Rubber Membrane Grommet (`Option 3A` + `S2-A`):** Removed the obsolete M16 gland cap variant. `MECH-CAP-BOT` carries a flat `Ø26.0 mm` outer spotface (`Y = -43.5 mm`), `Ø20.2 × 2.5 mm` panel bore, and `Ø23.6 × 2.5 mm` internal back-lip relief groove for a standard off-the-shelf `20 mm` rubber membrane grommet (`MECH-GROMMET-1`) ahead of the direct-mate `13.6 × 7.8 mm` USB-C tunnel (`J1` datum `Y = -25.76 mm`).
4. **Gold `DPDT On-On-On` Switch Alcove (`S3`):** Widened `+X` switch alcove to `15.0 × 13.5 mm` at `Z = 30.0 mm` (`2.50 mm` wall window) to house the `12.7 × 11.43 × 10.67 mm` `C&K 7211SYZBE` body and solder lugs cleanly above `driver_pcb`.
5. **Isolated Nylon PCB Mounting (`Option 2A`):** `driver_pcb` mounts to `MECH-LID-BOT` bosses via `4×` nylon `M2.5 × 6 mm` screws into `M2.5 × 4.0 mm` brass heat-set inserts through isolated unplated `H1..H4` (`Ø2.7 mm`).

## 2. Key Verified Clearances & Checks

| Check | Measured Value | Requirement | Status |
|---|---:|---:|:---:|
| Driver PCB radial clearance inside `Ø61 mm` cavity | `2.099 mm` | `>= 1.0 mm` | PASS |
| `MECH-LID-BOT` boss radial clearance to cavity wall | `3.799 mm` | `>= 2.0 mm` | PASS |
| Open air below `driver_pcb` through-hole pins | `9.700 mm` | `>= 3.0 mm` | PASS |
| PCB vertical headroom above mated JST-XH (`J2..J4`) to cone | `8.979 mm` | `>= 5.0 mm` | PASS |
| `20 mm` grommet panel thickness (`Ø20.2 mm` bore) | `2.500 mm` | `2.0 – 3.2 mm` | PASS |
| Grommet bore wall above `MECH-GASKET-3` / back-lip above lid | `2.830 / 3.180 mm` | `>= 2.5 mm` | PASS |
| USB-C tunnel wall above `MECH-GASKET-3` / below `MECH-GASKET-1` | `9.030 / 37.178 mm` | `>= 2.5 mm` | PASS |
| Standard `6.65 mm` USB-C plug exposed barrel at full `4.55 mm` mating | `2.100 mm` | `1.0 – 3.0 mm` | PASS |
| `C&K 7211` wall window / radial to PCB / Z above SMD | `2.50 / 4.53 / 2.385 mm` | `2.0–3.5 / >= 1.0 / >= 2.0 mm` | PASS |
| `MECH-ANCHOR-TOP` preload recess / stock bar slip fit | `0.500 / 1.000 mm` | `0.3–1.0 / >= 0.3 mm` | PASS |
| Worst-case `Ø66.5 mm` glass ID clearance to core / LED / M3 | `4.612 / 9.110 / 8.500 mm` | `>= 1.0 mm` | PASS |
| Glass axial O-ring squeeze (`149–151 mm` glass) & gland fill | `10.0% / 24.3% / 38.6%` (`91.3%` fill) | `10–45%`, `<= 92%` | PASS |
| FDM off-bed `>46°` overhang (`lid_bot` / `cap_bot` / `cap_top`) | `0.000 / 0.243 / 0.005 mm²` | `< 1.0 mm²` | PASS |
| USB-C & `20 mm` grommet flange STL ray-cast (`3,249` rays) | `0` anomalies, `min_wall = 2.500 mm` | `>= 2.5 mm` | PASS |
| Kinematic insertion (`C&K 7211`, `2× M4×16` CSK, USB-C plug) | `0.000000 mm³` (`72` waypoints) | `0.000 mm³` | PASS |
| All-pairs B-Rep interference (`NOM` + `WC`, incl. `24` fasteners) | `0 / 272` nonzero pairs (`136 + 136`) | `0` | PASS |
