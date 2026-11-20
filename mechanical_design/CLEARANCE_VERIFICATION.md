# LepiLED DIY Maxi Switch — Mechanical Clearance & Verification Report (Rev 4.9)

All **49 parametric assertions** ([params.py](cad/params.py)), **8 watertight support-free PETG/ASA-agnostic FDM STEP/STL exports** (`mech_cap_bot`, `mech_lid_bot`, `mech_cable_clamp`, `mech_core_anchor`, `mech_cap_top`, `mech_plug_top`, `mech_hang_bushing`, `mech_drill_jig`), overhang audits, **3 exterior-to-interior ray-cast wall-breach gates** (`MECH-CAP-TOP` rain roof `0/432`, `MECH-LID-BOT` blind `M3 × 5.0` clamp inserts `2/2`, `MECH-CAP-BOT` dry-bay wall `0/288`), **4 positive fastener-seat bearing & intact 4-wall core-socket checks**, **80-waypoint kinematic insertion sweeps** (`SW1`, **ENTIRE lid + PCB + 48 SMDs + mated 15 mm 90° USB-C plug straight up in one stroke**, pre-crimped JST-XH plugs through `±Y` slots, and intact `90°` USB-C plug through the `16.5 × 14.5 mm` lid port), and **240 all-pairs B-Rep solid intersection checks** (`120` Nominal + `120` Worst-Case `Ø60.6 mm` oval & `+2.0 mm` XT PMMA shroud, explicitly modeling the **DIY C-clip wire hanging bail, all `14` identical `M3 × 5.0 × 4.2 mm` brass inserts, all `32` exact full-length workshop `M3` CSK screws + steel/nylon washers, all `48` populated SMDs read directly from `driver_pcb.kicad_pcb`, and the realistic `15.0 mm` `90°` USB-C plug + `7.0 mm` strain relief**) ([generate_cad.py](cad/generate_cad.py)) pass with **`0.000000 mm³`** interference ([cad_verification.json](cad/cad_verification.json)).

## Key Verified Clearances & Regression Gates (Rev 4.9)

| Check | Measured Value | Requirement | Status |
|---|---:|---:|:---:|
| Serviceable lid-mounted `driver_pcb` / `15.0 mm` `90°` USB-C plug radial clr inside `Ø71.6 mm` bore | `1.290 / 1.283 mm` | `>= 1.2 / 0.8 mm` | **PASS** |
| Mated JST-XH top below flush CSK anchor ceiling / `B.Cu` TH pins above `SW1` lugs | `5.600 / 4.730 mm` | `>= 2.0 / 3.0 mm` | **PASS** |
| `15.0 mm` `90°` USB-C plug above spigot top / `7.0 mm` strain relief above lid top & inside spigot | `3.980 / 3.980 / 0.670 mm` | `>= 3.5 / 3.5 / 0.5 mm` | **PASS** |
| Blind `M3×5.0` clamp insert solid roof (`8.5 mm` lid) / clamp-to-`SW1` gap | `1.500 / 22.535 mm` | `>= 1.5 / 18.0 mm` | **PASS** |
| `4×` lid `M3×5.0` insert inner wall (`R=40.0 mm`) / flush `90°` CSK outer lid rim (`Ø87.6 mm`) | `2.200 / 0.550 mm` | `>= 2.2 / 0.3 mm` | **PASS** |
| Real `18.6 mm` `SW1` boot & flush-CSK `MECH-CABLE-CLAMP` recessed inside `22.0 mm` skirt | `3.400 / 13.000 mm` | `>= 2.5 / 5.0 mm` | **PASS** |
| **Ray-Cast Gate:** `MECH-CAP-TOP` lofted rain roof (`432` rays) — zero roof holes | `0 breaches` | `0` | **PASS** |
| **Ray-Cast Gate:** `MECH-LID-BOT` blind `M3×5.0` clamp insert dry-bay roof seal (`2` inserts) | `2 / 2 sealed` | `2 / 2` | **PASS** |
| **Ray-Cast Gate:** `MECH-CAP-BOT` outer dry-bay wall (`288` radial rays) — zero side holes | `0 breaches` | `0` | **PASS** |
| `MECH-CAP-TOP` vertical collar wall / lock screw above internal cone / below sealant groove | `4.650 / 5.100 / 1.159 mm` | `>= 4.0 / 3.0 / 1.0 mm` | **PASS** |
| Fastener-seat bearing (`cap_bot` flush CSK anchor / `cap_top` collar lock / `lid_bot` flush CSK) | `100.0% / 94.6% / 100.0%` | `>= 85–90%` | **PASS** |
| Intact 4-wall `31.1 × 31.1 mm` PETG/ASA-agnostic core sockets (`cap_bot` & `cap_top`) | `True / True` | `True` | **PASS** |
| Round `Ø20.0 mm` star edge-clamping (`R=11.7 mm`): shank edge clr / `Ø7` washer bite / UV-Vis washer gap | `0.200 / 1.800 / 3.600 mm` | `>= 0.15 / 1.5 / 3.0 mm` | **PASS** |
| Core corner / LED / `M3` CSK+washer / wire-slot radial clr to XT PMMA ID (`53.5 mm` min) | `5.25 / 7.71 / 6.39 / 3.27 mm` | `>= 2.5–5.0 mm` | **PASS** |
| Shroud radial O-rings (`60 × 3.5 mm` VMQ50/60 on `59.2–60.6 mm` oval PMMA) & short-tube margin | `11.4–31.4%` (`69.7%` fill) / `2.90 mm` | `10–33%`, `<= 85%`, `>= 2.0 mm` | **PASS** |
| Bottom lid radial spigot O-ring (`68 × 2.5 mm` VMQ70 on `Ø70.8 mm` spigot) | `14.0%` (`59.5%` fill) | `10–22%`, `<= 85%` | **PASS** |
| Chimney protrusion / hang hole below finial / lofted roof slope | `58.5 / 2.00 mm` / `24.6°` | `55–85 / >= 2.0 mm` / `>= 20°` | **PASS** |
| DIY C-clip wire bail (`Ø2.6 mm`): pin-in-bushing clr / engagement / leg-to-flange / hook clr | `0.70 / 8.60 / 3.85 / 38.7 mm` | `>= 0.5 / 7.0 / 2.5 / 30.0 mm` | **PASS** |
| FDM unsupported `>46°` overhang (`7` parts = `0.000 mm²`; `lid_bot` blind cone tip = `0.063 mm²`) | `<= 0.063 mm²` | `< 1.0 mm²` | **PASS** |
| Kinematic insertion (`SW1`, **ENTIRE Lid+PCB+15mm USB-C Straight Up**, JST slots, port pass) | `0.000000 mm³` (`80` waypoints) | `0.000 mm³` | **PASS** |
| All-pairs B-Rep (`NOM` + `WC`, incl. **wire bail, 14 `M3×5` inserts, 32 `M3` CSK screws, 48 SMDs & 15 mm USB-C**) | **`0 / 240` nonzero pairs** (`120 + 120`) | `0` | **PASS** |
