# LepiLED DIY Maxi Switch — Assembly & Bring-Up Guide

## 1. Pre-Assembly Safety & Ordering Checklist

- **UV-A Eye Safety:** Wear EN166 / ANSI Z87+ UV400 safety glasses whenever the `365 nm` UV LEDs (`D1..D4`) are powered. Do not look directly into the shroud.
- **No Live Hot-Plugging of LED Headers:** Unplug USB-C power before mating or unmating `J2` (UV) or `J3` (Visible).
- **Driver PCB (`driver_pcb`, 2-Reel Hybrid Lead-Free HASL PCBA):** Upload [driver_pcb_gerbers.zip](../pcb_design/gerbers/driver_pcb/driver_pcb_gerbers.zip) (`36 × 46 mm`, 2-layer `1.6 mm` FR4, 1 oz Cu, Lead-Free HASL, Green LPI / White silk, Top Side Economic PCBA, Qty `2`; select "Remove order number" for a clean back silkscreen) together with [driver_pcb_bom_pcba_hybrid.csv](../pcb_design/driver_pcb_bom_pcba_hybrid.csv) and [driver_pcb_cpl_hybrid.csv](../pcb_design/driver_pcb_cpl_hybrid.csv) to JLCPCB:
  - JLCPCB populates `41` SMDs (`20` Basic + `2` Extended reels: `U1/U2 = AL8860WT-7` and `U3 = WCH CH224A`).
  - Hand-solder the `11` DIY parts in [driver_pcb_diy_hand_solder.csv](../pcb_design/driver_pcb_diy_hand_solder.csv) (ordered in one Farnell UK basket alongside `SW1` and `SW1_BOOT`): `4` THT connectors (`J1..J4`) and `7` 2-pad SMDs (`F1` `1206` Littelfuse `046801.5NRHF`, `D11` `SMB` `SMBJ22A` with cathode band toward `VIN_20V`, `L1/L2` `6045` Bourns `SRN6045-680M`, `R3/R4` `1206` Bourns `0.30 Ω`, `R7` `2512` Vishay `1.0 Ω 1 W`) using [assembly_map.pdf](../pcb_design/driver_pcb/renders/assembly_map.pdf). `D13/D14` are paste-free DNP.
  - **Placement Check:** Confirm Pin-1 orientation of `D9/D10`, `D12`, `U1..U5`, `Q2/Q3`, and `D15/D16` in JLCPCB's 3D preview before checkout.
- **UV-Transmitting Extruded XT PMMA Shroud (`MECH-TUBE-1`):** Order `Ø60.0 × 54.0 × 3.0 mm` non-UV-blocked extruded clear XT PMMA (Röhm `0A070` / Perspex XT / Altuglas XT), ideally pre-cut to `115 mm` (`±2.0 mm` tolerant) to avoid home hacksaw stress cracking. Do not substitute UV-blocking acrylic or polycarbonate.
  - **Split-Beam `365 nm` Verification Test:** Hold white printer paper `20 cm` behind the tube and shine a `365 nm` UV LED so half the beam passes through the tube wall and half passes through open air onto the paper. Non-UV-blocked XT PMMA shows little or no brightness step across the tube edge; UV-blocking acrylic casts a distinct dark shadow on the tube half.
  - **Edge Bevel & Cleaning:** Wet-sand a light `1.0 × 30°` outer bevel on both ends with 400-grit sandpaper for smooth O-ring entry. Do not clean PMMA with isopropyl alcohol (IPA) or apply sealant to the PMMA; wash with warm soapy water.
- **Sealant (`MECH-SEAL-1`):** `Soudal Fix ALL Crystal` (`80 ml` hand-squeeze tube), a solvent-free SMX hybrid MS-polymer. Degrease aluminum mating zones with IPA (well away from the PMMA tube) and lightly scuff mating plastic before applying to the bottom nosecone hub V-groove, top collar V-groove, and cable clamp flange face; cure `24 h` in open air.
- **LED Stars (`D1..D8`, `Convoylight.com`):** Order `4× Luminus SST-10-UV 365 nm`, `2× Osram KB CSLNM1.14` (`455 nm` Royal Blue), `1× Osram KP CSLNM1.F1` (Pure Green), and `1× Osram KW CSLNM1.TG` (`6500 K` Cool White), all on `20 mm` Copper DTP stars. Verify electrically neutral thermal pads with a multimeter before mounting.
- **3D Printing (6 Support-Free Parts in White PETG or White ASA, `0.2 mm` layers, `4` perimeters, `25%` gyroid infill, `0` supports; enable scarf seams and lightly wet-sand O-ring grooves with 400-grit; avoid plain PLA):**
  - [mech_cap_bot.step](../mechanical_design/cad/mech_cap_bot.step) — upright (`Ø40 mm` flat tip on bed).
  - [mech_top_base.step](../mechanical_design/cad/mech_top_base.step) — upright (lower `Ø71 mm` collar rim on bed).
  - [mech_cap_top.step](../mechanical_design/cad/mech_cap_top.step) — upright (`Ø118 mm` eaves flat on bed).
  - [mech_plug_top.step](../mechanical_design/cad/mech_plug_top.step) — inverted (flat `26 × 26 mm` rain-hood top on bed).
  - [mech_cable_clamp.step](../mechanical_design/cad/mech_cable_clamp.step) — prints as a pre-mirrored L+R matched pair on one build plate (flat outer flange on bed).
  - [mech_drill_jig.step](../mechanical_design/cad/mech_drill_jig.step) — `35 mm` end-cap guide, flat back plate on bed (PETG or PLA).

## 2. Step-by-Step Build Sequence

### Step 1 — Drill `4` Plain `Ø4.5 mm` Holes in the `300.0 mm` Clear-Anodized Aluminum Core (`MECH-HS-CORE`)
All coordinates match [cad_params.json](../mechanical_design/cad/cad_params.json) (`drill_guide_from_core_bot_mm`) and [mech_drill_jig.step](../mechanical_design/cad/mech_drill_jig.step) on the `300.0 mm` `30 × 30 × 2.0 mm` clear/silver-anodized Al 6063-T6 tube (or bare mill tube painted matte white or matte black for `ε_IR ≈ 0.82`). No aluminum tapping is required:

| Feature | Faces | Distance from End (mm) | Operation |
|---|---|---:|---|
| Bottom nosecone cross-bolt (`M4 × 50 mm` SS) | `±X` (`2` faces) | **`6.5 mm`** from bottom end | Center-punch with `MECH-DRILL-JIG`, drill `Ø4.5 mm` plain clearance, deburr |
| Visible LED star centers (`D5..D8`, epoxy reference) | All `4` faces | **`54.0 mm`** from bottom end | Pencil alignment mark only (do not drill) |
| UV LED star centers (`D1..D4`, epoxy reference) | All `4` faces | **`88.0 mm`** from bottom end | Pencil alignment mark only (do not drill) |
| Top hanging & finial cross-bolt (`M4 × 50 mm` SS) | `±X` (`2` faces) | **`16.0 mm`** from top end (`284.0 mm` from bottom) | Flip `MECH-DRILL-JIG` onto top end, center-punch, drill `Ø4.5 mm` plain clearance, deburr |

### Step 2 — Press `6×` `M3 × 5.0` Brass Inserts & Seat `4×` Captive `M3` Hex Nuts
- **Brass Heat-Set Inserts (`6×` identical `M3 × 5.0 × 4.2 mm`, `220–240 °C` iron):**
  - **`MECH-CAP-TOP` (`4×`):** Underside of the `Ø118 mm` rain eaves at `R = 51.0 mm` (`45°/135°/225°/315°`).
  - **`MECH-TOP-BASE` (`2×`):** Horizontally into the blind `+Y` cable-clamp pockets (`X = ±13.0 mm`, `4.0 mm` solid dry-bay wall behind them).
- **Captive `M3` Hex Nuts (`4×` standard DIN 934):** Drop `4×` `M3` hex nuts horizontally into the side-entry pockets on the outer edges of `MECH-TOP-BASE`'s two `+X` PCB stanchions (`Y = ±14.0 mm`, `Z = 178.5` and `216.5 mm`) with flat sides horizontal (`5.5 mm` AF vertical).

### Step 3 — Bond & Pre-Wire the `8×` Convoy Cu DTP LED Stars (4-Face Map)
1. Abrade only the 8 circular `Ø20 mm` star landing zones on the anodized or painted aluminum tube (`54.0 mm` and `88.0 mm` from bottom) down to clean bare aluminum with 240-grit sandpaper (leaving the surrounding anodized/painted finish intact for high IR emissivity), and degrease both aluminum and copper star backs with IPA or acetone.
2. Mix 2-part thermally conductive epoxy (`MECH-TIM-1`, `Arctic Alumina` or `MG Chemicals 8329TFS`) thinly and bond each `20 mm` star dead-flat onto its face with **solder pads oriented horizontally (3 and 9 o'clock)** around the perimeter. Clamp gently with spring clamps or rubber bands while curing and verify `> 10 MΩ` isolation from every solder pad to the aluminum core. *(Optional: while epoxy is mixed, dab a paper-thin smear between your stacked `15 × 15 × 0.5 mm` brass shims for Step 4 so they cure into one solid `3.5–4.0 mm` block.)*
3. Solder all inter-star jumpers and the long risers using **`24 AWG` UV-stable silicone wire (`HARN-03`)** (`240–260 mm` risers extending cleanly up into the dark top bay — do not expose PVC pigtail wire inside the `365 nm` UV chamber). Trim `HARN-01` 2-pin JST-XH pigtails to `~50 mm` and heatshrink-splice them to the silicone risers inside the top bay:

| Core Face | Upper Tier (`88.0 mm` from bot, Ch1 `J2`) | Lower Tier (`54.0 mm` from bot, Ch2 `J3`) | Uncrossed Perimeter Series Wiring Order |
|---|---|---|---|
| **Face 1 (`+X`)** | `D1` — `SST-10-UV 365 nm` | `D5` — `Osram KB CSLNM1.14 455 nm` | **Ch1 UV (`-Y` slot → `J2` at `Y = -5.2`):** `J2.1 (+) → D4 (-Y) → D3 (-X) → D2 (+Y) → D1 (+X) → J2.2 (-)` |
| **Face 2 (`+Y`)** | `D2` — `SST-10-UV 365 nm` | `D7` — `Osram KP CSLNM1.F1 Green` | **Ch2 Vis (`+Y` slot → `J3` at `Y = +5.2`):** `J3.1 (+) → D7 (+Y) → D5 (+X) → D8 (-Y) → D6 (-X) → J3.2 (-)` |
| **Face 3 (`-X`)** | `D3` — `SST-10-UV 365 nm` | `D6` — `Osram KB CSLNM1.14 455 nm` | *(Royal Blue opposite on Faces 1 & 3)* |
| **Face 4 (`-Y`)** | `D4` — `SST-10-UV 365 nm` | `D8` — `Osram KW CSLNM1.TG 6500 K` | *(Green opposite Cool White on Faces 2 & 4)* |

### Step 4 — Hand-Solder the `11` DIY PCB Parts & Assemble `MECH-TOP-BASE`
1. Using [assembly_map.pdf](../pcb_design/driver_pcb/renders/assembly_map.pdf) and [driver_pcb_diy_hand_solder.csv](../pcb_design/driver_pcb_diy_hand_solder.csv), solder the `7` 2-pad SMDs first (`R3`, `R4`, `F1`, `R7`, `D11` with cathode bar toward `VIN_20V`, `L1`, `L2`), then the `3` JST-XH headers (`J2`, `J3`, `J4`), and finally `J1` (`GCT USB4085-GF-A`).
2. **`J1` Micro-THT Soldering & Mandatory Pre-Power Short Gate:** Because `USB4085`'s `1.60 mm` signal pins sit flush inside the `1.60 mm` HASL board's `Ø0.40 mm` barrels (`0.20 mm` pad gap):
   - Hold the bare board to a light before inserting `J1` to confirm all 16 signal barrels are open (clear any HASL skin with flux + braid).
   - Seat `J1` dead-flush on `F.Cu`, tack the 4 outer shield tabs first, apply generous tacky no-clean flux on `B.Cu`, dwell `3–4 s` per pin at `350 °C` with a fine bevel/chisel tip so solder wicks into every barrel, clean with IPA, and inspect at `10×` magnification.
   - **Multimeter Check Before Power:** Verify `TP1` (`VIN_20V`) / `F1` (`VBUS`) to `U3.4` (`CC1`), `U3.5` (`CC2`), and `GND` all read `> 100 kΩ` while gently flexing a USB-C plug.
3. Clean the `Ø6.50 mm` circular `SW1` mounting hole in `MECH-TOP-BASE`'s `-X` cove with a `6.5 mm` (`1/4"`) twist drill by hand so the sealing face is flat and round. Trim `HARN-02` (`3`-pin JST-XH) to `~150 mm` (routing cleanly around the `-Y` side of the core to `J4`), solder to `SW1` (`C&K 7211SYZBE`), and insulate lugs with heatshrink:

| `SW1` Lug(s) | `J4` Pin | Pos 1 (`OFF`, toward `-Y`, 0 ribs) | Pos 2 (`4-UV`, center, 1 rib) | Pos 3 (`8-ALL`, toward `+Y`, 2 ribs) |
|---|---|---|---|---|
| **Lugs `2 + 5` (tied)** | **`J4.2` (`GND`)** | Common `GND` | Common `GND` | Common `GND` |
| **Lug `6`** | **`J4.1` (`SW_UV_IN`)** | Closed to `GND` (`U1` OFF) | Open (`U1` ON) | Open (`U1` ON) |
| **Lug `3`** | **`J4.3` (`SW_VIS_IN`)** | Closed to `GND` (`U2` OFF) | Closed to `GND` (`U2` OFF) | Open (`U2` ON) |
| **Lugs `1` and `4`** | **No Connect** | — | — | — |

4. Seat `SW1` into `MECH-TOP-BASE`'s keyed `-X` pocket with **Lugs `1,4` facing `-Y` (bushing keyway slot facing `+Y`)** so throwing the toggle toward `-Y` = `OFF` (0 ribs), center = `4-UV` (1 rib), and `+Y` = `8-ALL` (2 ribs). Tighten `SW1_BOOT` firmly against the flat face inside the `32 mm` draining cove.
5. Press the `Ø8 mm` adhesive IP68 ePTFE breather vent patch (`MECH-VENT-1`) squarely into the flat horizontal `Ø9.5 × 0.8 mm` pocket on the `-Y` dry-bay floor (over the `35°` downward-draining `Ø3.5 mm` bore).
6. **Outward Cable Threading & Open-Air PCB Mounting (Test Before Installing Thermal Bridge):** Feed the **straight charger-end plug** of the `2.0 m` standard left/right `90°` USB-C PD cable (`HARN-04`) **outward** from inside `MECH-TOP-BASE` through the `+Y` gable port until the `90°` plug rests inside the bay. Fasten a small cable tie around the cable onto the internal `+Y` strain-relief post (leaving slack to reach `J1`). Mount `driver_pcb` vertically on the `+X` stanchions (`F.Cu` facing `+X`, `J1` at deck level) into the `4×` captive `M3` hex nuts using `4×` `M3 × 8 mm` pan-head screws + `1×` `M3` steel flat washer + **`2×` stacked `0.8 mm` `M3` nylon insulating washers** (`MECH-WASH-NYLON`, `2.1 mm` washer stack so the screw threads fully through the hex nut without touching the core wall). Mate the `90°` USB-C plug straight up into `J1` (cable exiting horizontally along `+Y`) and mate `J4` (`SW1`).

## 3. Staged Open-Air Bench Bring-Up (`TP1..TP4` & `D12`)

With `driver_pcb` mounted on `MECH-TOP-BASE` (before installing `MECH-CAP-TOP`) and `J2`/`J3` unplugged, `TP1..TP4` and `D12` are exposed on `+X` `F.Cu`:

1. **Unplugged Shorts Check:** Confirm `TP1` (`VIN_20V`) to `TP4` (`GND`) `> 5 kΩ`, `VBUS` to `GND` `> 10 kΩ`, and `J2`/`J3` open.
2. **20 V PD Negotiation (`J2`/`J3` Unplugged, `SW1` = `OFF`):** Plug `HARN-04` into a `45–100 W` USB-C PD charger. Confirm red LED `D12` illuminates, `V(TP1) = 20.0 V ± 1.0 V`, `V(TP2, V_REF) = 2.500 V ± 0.03 V`, and `V(TP3, UVLO_OK) ≈ 10.0 V`.
3. **5 V UVLO Rejection Check:** Plug into a legacy `5 V` USB port; confirm `V(TP3) < 0.2 V` and `V(U1_CTRL) < 50 mV`, `V(U2_CTRL) < 50 mV`.
4. **LED Load Test (Power Off Before Mating `J2`/`J3`; Wear UV400 Glasses):** Mate `J2` and `J3` temporarily, reconnect `20 V` PD, and verify `OFF` (`< 15 mA`), `4-UV` (`~0.25 A`, `V(R3) = 100 mV ± 6 mV`), and `8-ALL` (`~0.453 A`, `V(R3) ≈ V(R4) ≈ 100 mV`). Unplug power and unmate `J2`/`J3` for mechanical assembly.

## 4. Final Mechanical Assembly & Sealing

1. **Bottom Nosecone, Stainless Mesh, `M4 × 50 mm` Cross-Bolt & Hub Seal (`MECH-CAP-BOT`):** Cut two `28 × 28 mm` squares of `304` stainless insect mesh (`MECH-MESH-1`). Drop one square into the `Z = 5.2 mm` mesh pocket at the bottom of `MECH-CAP-BOT`'s core socket, slide the `300.0 mm` aluminum core straight down on top of it (clamping the mesh mechanically), align the `6.5 mm` `Ø4.5 mm` holes, and secure with one `M4 × 50 mm` A2 stainless cross-bolt + washers + M4 nyloc nut inside the `±X` recessed spotfaces. **Before installing the XT PMMA tube**, degrease the aluminum tube at `Z = 34.0 mm` and fill `MECH-CAP-BOT`'s top `1.8 × 2.5 mm` rounded-square hub V-groove cleanly with `Soudal Fix ALL Crystal` (`MECH-SEAL-1`) so the `0.55 mm` core-socket gap and `M4` bolt holes are sealed off from the LED optical chamber; let cure before sliding the PMMA tube on.
2. **Slide Shroud & `MECH-TOP-BASE` Over Core & Seat Captive `15 × 15 mm` PCB Thermal Bridge:** Seat lightly silicone-greased `MECH-GASKET-1/2` (`60 × 3.5 mm` VMQ50/60) in `MECH-CAP-BOT` and `MECH-TOP-BASE`. Slide the beveled `115 mm` XT PMMA tube into `MECH-CAP-BOT`. Feed the UV (`-Y`) and Visible (`+Y`) silicone risers straight up through `MECH-TOP-BASE`'s uncrossed `±Y` `9.0 × 7.5 mm` channels while sliding `MECH-TOP-BASE` down the core onto the PMMA tube. Remove the 4 PCB screws temporarily, place the captive **`15 × 15 mm` thermal bridge stack** (`MECH-TIM-PAD`: one `1.0 mm` dielectric silicone pad against the anodized Al core + `15 × 15 × 0.5 mm` brass shims/pads totaling `~5.8–6.0 mm` uncompressed + one `1.0 mm` dielectric silicone pad on the `B.Cu` side) squarely inside the `15.6 × 15.6 mm` chute behind `U1/U2`, then re-fasten `driver_pcb` (`4× M3 × 8` + steel + `2×` nylon washers) so the pads compress gently across the `5.5 mm` gap without flexing the board. Splice/mate `J2` (`Y = -5.2`) and `J3` (`Y = +5.2`) cleanly inside the top bay.
3. **Compressing `+Y` Split Cable Clamp (`MECH-CABLE-CLAMP`):** Cut a `10 mm` length of `MECH-GROMMET-1` (`Ø8 × Ø4 mm` silicone tubing), slit it lengthwise at a slight angle, and wrap it around the USB-C cable jacket. Apply a thin continuous bead of `Soudal Fix ALL Crystal` (`MECH-SEAL-1`, `80 ml` tube) around the `+Y` boss face and silicone sleeve slit, seat both pre-mirrored L+R `MECH-CABLE-CLAMP` wedge halves around the sleeve, and tighten `2× M3 × 14 mm` pan-head screws + steel flat washers in the `5.5 × 3.4 mm` X-slotted flange until the wedges compress the silicone sleeve evenly.
4. **Top Rain Bell (`MECH-CAP-TOP`) & Axial Face O-Ring:** Seat `MECH-GASKET-3` (`88 × 2.5 mm` soft VMQ50) in the flat `Z = 171.0 mm` deck groove of `MECH-TOP-BASE`. Slide `MECH-CAP-TOP` straight down over the aluminum chimney and wired PCB (aligning the `+Y` cable C-clip above the clamp, `-X` visor above `SW1`, and `0.6 mm` internal dimple opposite `D12`) and fasten `4× M3 × 12 mm` CSK screws upward through the diagonal gusseted ears into the eaves inserts.
5. **Collar Seal, Ventilated Rain Finial (`MECH-PLUG-TOP`), Hanging Bolt & Drip Loop:** Degrease the aluminum chimney at the top collar, fill `MECH-CAP-TOP`'s top `2.5 × 3.0 mm` V-groove with `Soudal Fix ALL Crystal` (keep off the PMMA shroud), and cure `24 h` in open air. Lay the second `28 × 28 mm` stainless mesh square across the top rim of the aluminum chimney, insert `MECH-PLUG-TOP`'s 4 corner legs into the `26 × 26 mm` bore, and pin it with the second `M4 × 50 mm` A2 stainless cross-bolt + washers + M4 nyloc nut at `16.0 mm` from the core top. Tie a `3 mm` paracord hanging loop (or clip a stainless shackle/carabiner) directly onto the top `M4` stainless bolt. Form a `~20 mm` downward drip loop out of the `+Y` clamp and snap the USB-C cable into the flexible `+Y` eaves C-clip (optional mini zip-tie through the adjacent slot) to route the `2.0 m` lead upward clear of a catching funnel.
