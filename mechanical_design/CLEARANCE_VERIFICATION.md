# LepiLED DIY Maxi Switch — Mechanical Clearance & Verification Report (Rev 4.5)

All **37 parametric assertions** ([params.py](cad/params.py)), **6 watertight support-free FDM STEP/STL exports** (`mech_base_ring`, `mech_lid_bot`, `mech_cap_bot`, `mech_cap_top`, `mech_plug_top`, `mech_drill_jig` — `MECH-PLUG-BOT` eliminated), overhang audits, **75-waypoint kinematic insertion sweeps** (`SW1`, horizontal `driver_pcb` with all `57` SMDs onto standoffs, `7.4 × 5.75 mm` pre-crimped JST-XH plug straight through both `±Y` wire channels, intact `12.4 × 6.8 mm` USB-C plug straight through the `M20` split gland bore), and **156 all-pairs B-Rep solid intersection checks** (`78` Nominal + `78` Worst-Case `+2.0 mm` XT PMMA shroud, including **all `57` SMDs parsed from `driver_pcb_cpl.csv`**, `90°` USB-C plug, `M20` split gland, `SW1`, `8×` `20 mm` Copper DTP stars, and all `M3`/`M2.5` fasteners) ([generate_cad.py](cad/generate_cad.py)) pass with **0.000000 mm³** interference ([cad_verification.json](cad/cad_verification.json)).

## Key Verified Clearances & Checks (Rev 4.5)

| Check | Measured Value | Requirement | Status |
|---|---:|---:|:---:|
| Horizontal `driver_pcb` corners / `90°` USB-C plug radial clearance inside `Ø74.4 mm` cavity | `1.353 / 5.740 mm` | `>= 1.0 / 4.0 mm` | PASS |
| `driver_pcb` `B.Cu` TH pins to `43.6°` shroud-cone apex / flat bulkhead ceiling | `1.690 / 4.600 mm` | `>= 1.5 / 4.0 mm` | PASS |
| `driver_pcb` downward SMDs above `SW1` lugs / mated `J2..J4` above `MECH-LID-BOT` | `7.230 / 12.200 mm` | `>= 5.0 / 10.0 mm` | PASS |
| `M20` split cable gland locknut inside spigot / edge-to-edge gap to `SW1` | `0.750 / 18.035 mm` | `>= 0.5 / 10.0 mm` | PASS |
| `SW1` boot & `M20` split gland clearance above flat ground inside `MECH-BASE-RING` | `5.000 / 3.500 mm` | `>= 3.0 / 2.5 mm` | PASS |
| `MECH-BASE-RING` `Ø6.2 mm` bolt counterbore inner / outer walls | `2.600 / 2.600 mm` | `>= 2.5 mm` | PASS |
| `MECH-CAP-BOT` cavity-to-bolt / outer-bolt / mid-shell / O-ring outer walls | `2.60 / 3.20 / 3.80 / 3.60 mm` | `>= 2.5–3.2 mm` | PASS |
| `MECH-LID-BOT` spigot radial O-ring groove wall / `MECH-CAP-TOP` collar corner wall | `2.550 / 3.521 mm` | `>= 2.5 / 3.0 mm` | PASS |
| `20 mm` Cu DTP star UV-to-Vis gap / core, LED & M3 clearance to XT PMMA ID (`53.5 mm`) | `12.00 / 5.25 / 7.71 / 4.74 mm` | `>= 10.0 / >= 3.0 mm` | PASS |
| Wire channels (`±Y`) passing `7.4 × 5.75 mm` JST-XH plug / inside PMMA ID | `9.0 × 7.5 mm` (`3.41 mm` inside ID) | `>= 8.5 × 7.0 / >= 2.5 mm` | PASS |
| Shroud radial bore O-rings (`60 × 3.0 mm` VMQ70 on `Ø60 ±0.4 mm` OD) squeeze & fill | `13.3% / 20.0% / 26.7%` (`68.5%` fill) | `10–32%`, `<= 85%` | PASS |
| Bottom lid radial spigot O-ring (`70 × 2.5 mm` VMQ70) squeeze & fill | `14.0%` (`59.5%` fill) | `10–22%`, `<= 85%` | PASS |
| Protruding bare core length / `Ø8 mm` hang hole below `MECH-PLUG-TOP` / `25°` roof | `56.78 / 2.00 mm` / `25.0°` | `55–85 / >= 2.0 mm` / `>= 10°` | PASS |
| FDM off-bed `>46°` overhang (`5` parts = `0.000 mm²`; `cap_bot` = `0.917 mm²`) | `0.000 – 0.917 mm²` | `< 1.0 mm²` | PASS |
| Kinematic insertion (`SW1`, horizontal PCB w/ 57 SMDs, JST-XH wire slots, M20 gland) | `0.000000 mm³` (`75` waypoints) | `0.000 mm³` | PASS |
| All-pairs B-Rep interference (`NOM` + `WC +2 mm`, incl. all `57` SMDs & all fasteners) | `0 / 156` nonzero pairs (`78 + 78`) | `0` | PASS |
