# LepiLED DIY Maxi Switch — Mechanical Clearance & Verification Report (Rev 4.0 / Option 2)

All 34 parametric assertions ([params.py](file:///home/alimuldal/src/lepiled/mechanical_design/cad/params.py)), 5 watertight STEP/STL exports, overhang audits, 5,913-ray USB-C tunnel ray-cast, 84-waypoint kinematic insertion sweeps, and **612 all-pairs B-Rep solid intersection checks** ([generate_cad.py](file:///home/alimuldal/src/lepiled/mechanical_design/cad/generate_cad.py)) pass with **0.000 mm³** interference ([cad_verification.json](file:///home/alimuldal/src/lepiled/mechanical_design/cad/cad_verification.json)).

## 1. Rev 4.0 Mechanical & Interface Updates

1. **Unified Dual `SK 578/50 SA` Heatsinks (`Ø60 × 50 mm` top & bottom):** Option 2's `0.50 W` nom / `0.82 W` max PCB loss allows identical `£5.88` `SK 578/50 SA` heatsinks top and bottom, reducing overall lamp height by `20.0 mm` (`330.0 mm` vs `350.0 mm`, excluding eye bolt) and standardizing both hub bolt circles to `4× M3` at `R = 8.5 mm`.
2. **Exact `J1` Front Datum (`Y = -25.76 mm`):** Corrected from `-25.34 mm` to GCT `USB4085-GF-A`'s exact datasheet datum (`Row-B -18.50 mm - 7.26 mm = -25.76 mm`).
3. **Deepened `MECH-ADAPT-BOT` Pin Relief Pockets (`2.5 mm`):** Increased from `1.8 mm` to `2.5 mm` under `J1/TP1/TP2`, `J2/J3`, and `J4` to clear untrimmed through-hole tails plus Kapton insulation (`5.5 mm` solid Al remains beneath the pockets).
4. **Direct-Mate `6.65 mm` Standard USB-C Tunnel (`mech_cap_bot_usbc`):** Replaced the extended-barrel bezel with a clean `13.6 × 7.8 mm` (+47° self-supporting pitched roof) recessed tunnel opening into the `Ø61.0 mm` cavity, allowing any standard `6.65 mm` USB-C PD laptop-charger or power-bank plug to seat full `4.55 mm` into `J1` (`2.10 mm` exposed barrel, `0.000 mm³` interference across `153` B-Rep pairs).
5. **Flat M2.5 Nylon PCB Washers (`MECH-FAST-2`):** Replaced nylon shoulder washers (which cannot fit `Ø2.7 mm` `H1..H4` holes) with flat M2.5 nylon washers (`Ø5.0 mm OD`).

## 2. Key Verified Clearances & Checks

| Check | Measured Value | Requirement | Status |
|---|---:|---:|:---:|
| Driver PCB radial clearance inside `Ø61 mm` cavity | `2.099 mm` | `>= 1.0 mm` | PASS |
| Driver PCB rim on `Ø59 mm` aluminum pedestal | `1.099 mm` | `>= 0.5 mm` | PASS |
| PCB vertical headroom above mated JST-XH (`J2..J4`) to cone | `6.775 mm` | `>= 5.0 mm` | PASS |
| Bottom relief pocket depth (`J1/TP1/TP2`, `J2/J3`, `J4`) | `2.500 mm` | `>= 2.5 mm` | PASS |
| USB-C tunnel above `MECH-ADAPT-BOT` pedestal / `MECH-GASKET-3` | `0.080 mm` / `3.030 mm` | `> 0.05` / `>= 2.5 mm` | PASS |
| Standard `6.65 mm` USB-C plug exposed barrel at full `4.55 mm` mating | `2.100 mm` | `1.0 – 3.0 mm` | PASS |
| `SW1` wall window / radial clearance to PCB / Z above SMD | `2.50` / `5.81` / `4.67 mm` | `2.0–3.5` / `>= 1.0` / `>= 2.0 mm` | PASS |
| Worst-case `Ø66.5 mm` glass ID clearance to core corner / LED / M3 | `4.612` / `9.110` / `8.500 mm` | `>= 1.0 mm` | PASS |
| Glass axial O-ring squeeze (`149–151 mm` glass) & gland fill | `10.0% / 24.3% / 38.6%` (`91.3%` fill) | `10–45%`, `<= 92%` | PASS |
| FDM off-bed `>46°` overhang (`cap_bot` / `cap_top` / `cap_bot_usbc`) | `0.02` / `0.01` / `0.62 mm²` | `< 1.0 mm²` | PASS |
| Kinematic insertion sweeps (`SW1`, `M16` nut, `2× M4x16` CSK) | `0.000000 mm³` (84 waypoints) | `0.000 mm³` | PASS |
| All-pairs B-Rep interference (`M16_NOM/WC`, `USBC_NOM/WC`) | `0 / 612` nonzero pairs | `0` | PASS |
