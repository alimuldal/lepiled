# LepiLED DIY Maxi Switch — Mechanical Clearance & Verification Report (Rev 4.6)

All **38 parametric assertions** ([params.py](cad/params.py)), **8 watertight support-free FDM STEP/STL exports** (`mech_cap_bot`, `mech_lid_bot`, `mech_cable_clamp`, `mech_core_anchor`, `mech_cap_top`, `mech_plug_top`, `mech_hang_bushing`, `mech_drill_jig` — `MECH-BASE-RING` and `M20` gland eliminated), overhang audits, **4 positive fastener-seat bearing & intact 4-wall core-socket regression gates** (P0-1 guard), **84-waypoint kinematic insertion sweeps** (`SW1`, horizontal `driver_pcb` with all `57` SMDs, `7.4 × 5.75 mm` pre-crimped JST-XH plug through both `±Y` wire slots, and the **actual `13.2 × 11.5 mm` `90°` USB-C L-plug** straight through the `16.0 × 14.0 mm` lid port), and **210 all-pairs B-Rep solid intersection checks** (`105` Nominal + `105` Worst-Case `Ø60.6 mm` oval & `+2.0 mm` XT PMMA shroud, including all `57` SMDs, `90°` USB-C plug + `7.0 mm` molded strain-relief boot, 2-piece split clamp, dry-bay core anchor, Signal-Orange hang bushings, `D12` lightpipe, `SW1`, `8×` Copper DTP stars, and all `M3`/`M2.5` fasteners) ([generate_cad.py](cad/generate_cad.py)) pass with **0.000000 mm³** interference ([cad_verification.json](cad/cad_verification.json)).

## Key Verified Clearances & Checks (Rev 4.6)

| Check | Measured Value | Requirement | Status |
|---|---:|---:|:---:|
| Horizontal `driver_pcb` corners / `90°` USB-C plug radial clearance inside `Ø71.0 mm` bay | `2.115 / 1.670 mm` | `>= 1.5 / 1.2 mm` | PASS |
| `driver_pcb` `B.Cu` TH pins to ceiling / SMDs above `SW1` lugs / mated JST above lid | `2.60 / 11.23 / 16.20 mm` | `>= 2.0 / 8.0 / 14.0 mm` | PASS |
| `90°` USB-C `7.0 mm` molded strain-relief boot bottom above `MECH-LID-BOT` top (`Z=24`) | `8.420 mm` (`15.4 mm` to plug) | `>= 6.0 mm` | PASS |
| Split cable clamp port & `M3` bolts inside `Ø56.2 mm` spigot ID / gap to `SW1` | `1.375 / 4.049 / 20.785 mm` | `>= 1.0 / 2.5 / 14.0 mm` | PASS |
| `SW1` boot & `MECH-CABLE-CLAMP` ground clearance inside `19 mm` recessed skirt | `4.000 / 8.000 mm` (`5.0` w/ bolt) | `>= 3.0 / 5.0 mm` | PASS |
| `MECH-CAP-BOT` lid insert inner/outer walls / min skirt wall / bay wall / O-ring wall | `2.30 / 3.26 / 2.85 / 4.71 / 4.30 mm` | `>= 2.2–3.5 mm` | PASS |
| Solid `R = 24.4 mm` central core hub clearance to PMMA ID (`53.5`) / corner wall | `2.350 / 2.621 mm` (`9.0 mm` flat) | `>= 2.0 / 2.5 mm` | PASS |
| **P0-1 Guard:** Fastener-seat bearing (`cap_bot` anchor / `cap_top` lock / `lid_bot` bolts) | `100.0% / 94.6% / 100.0%` | `>= 80–90%` | PASS |
| **P0-1 Guard:** Intact 4-wall `30.8 × 30.8 mm` square core sockets (`cap_bot` & `cap_top`) | `True / True` | `True` | PASS |
| `20 mm` Cu DTP star UV-to-Vis gap / core, LED & M3 clearance to XT PMMA ID (`53.5 mm`) | `12.00 / 5.25 / 7.71 / 4.74 mm` | `>= 10.0 / >= 3.0 mm` | PASS |
| Shroud radial O-rings (`60 × 3.5 mm` VMQ50/60 on real `59.2–60.6 mm` oval XT PMMA) | `11.4% / 22.9% / 31.4%` (`69.7%` fill) | `10–33%`, `<= 85%` | PASS |
| Short-tube (`113.0 mm`, `-2.0 mm`) gravity-drop margin above `MECH-GASKET-2` flat root | `2.900 mm` | `>= 2.0 mm` | PASS |
| Bottom lid radial spigot O-ring (`62 × 2.5 mm` VMQ70 on `Ø64.2 mm` spigot) | `14.0%` (`59.5%` fill) | `10–22%`, `<= 85%` | PASS |
| Protruding matte-black core / hang hole below finial / lofted roof slope | `57.0 / 2.00 mm` / `27.0°–35.3°` | `55–85 / >= 2.0 mm` / `>= 20°` | PASS |
| FDM off-bed `>46°` overhang (`7` parts = `0.000 mm²`; `cap_bot` = `0.160 mm²`) | `0.000 – 0.160 mm²` | `< 1.0 mm²` | PASS |
| Kinematic insertion (`SW1`, PCB w/ 57 SMDs, JST wire slots, **actual `90°` USB-C L-plug**) | `0.000000 mm³` (`84` waypoints) | `0.000 mm³` | PASS |
| All-pairs B-Rep interference (`NOM` + `WC 60.6 mm oval & +2 mm`, incl. all `57` SMDs & strain relief) | `0 / 210` nonzero pairs (`105 + 105`) | `0` | PASS |
