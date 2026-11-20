# LepiLED DIY Maxi Switch — Assembly & Bring-Up Guide (Rev 4.8)

## 1. Pre-Assembly Safety & Ordering Checklist

- **UV-A Eye Safety:** Wear EN166 / ANSI Z87+ UV400 safety glasses whenever the `365 nm` UV LEDs (`D1..D4`) are powered. Never stare directly into the shroud.
- **No Live Hot-Plugging of LED Headers:** Always unplug USB-C power before mating or unmating `J2` (UV) or `J3` (Visible).
- **Driver PCB (`driver_pcb` — Low-Hassle Full-SMD ENIG PCBA):** Upload [driver_pcb_gerbers.zip](../pcb_design/gerbers/driver_pcb/driver_pcb_gerbers.zip) (`36 × 46 mm`, 2-layer `1.6 mm` FR4, 1 oz Cu, **ENIG**, Green LPI / White silk, **Top Side** assembly, **Economic PCBA**, Qty `2`; select **"Remove order number"** for a clean back silkscreen) together with [driver_pcb_bom_pcba_hybrid.csv](../pcb_design/driver_pcb_bom_pcba_hybrid.csv) and [driver_pcb_cpl_hybrid.csv](../pcb_design/driver_pcb_cpl_hybrid.csv) to JLCPCB:
  - JLCPCB machine-reflows **all `48` SMDs** (`20` Basic + `7` Extended reels: `U1/U2`, `U3`, `F1`, `D11`, `L1/L2`, `R3/R4`, `R7`) — **zero home SMD soldering!**
  - Hand-solder only the **`4` through-hole connectors (`J1..J4`)** in [driver_pcb_diy_hand_solder.csv](../pcb_design/driver_pcb_diy_hand_solder.csv) using [assembly_map.pdf](../pcb_design/driver_pcb/renders/assembly_map.pdf). (`D13/D14` are paste-free DNP.)
  - **Placement Check:** Confirm Pin-1 orientation of `D9/D10`, `D11`, `D12`, `U1..U5`, `Q2/Q3`, and `D15/D16` in JLCPCB's 3D preview before checkout.
- **UV-Transmitting Plexiglass Shroud (`MECH-TUBE-1`):** Order `Ø60.0 × 54.0 × 3.0 × 115 mm` (`±2.0 mm` tolerant) **Röhm `PLEXIGLAS® XT Clear 0A070` (`29070`)** from Amari Plastics UK or Acrylglas-Shop (`~80–85%` normal transmission at `365 nm`). Do **not** substitute UV-blocking cast `GS` or polycarbonate.
  - **365 nm Bench Verification Test:** Before cutting or sealing, hold a piece of bright white printer paper (containing optical brighteners) behind the tube and shine a `365 nm` UV torch or one powered `SST-10-UV` star through it. Genuine `0A070` transmits strongly so the paper fluoresces bright blue-violet right through the wall; UV-blocking PMMA/PC casts a dark shadow on the paper.
  - **Edge Bevel & Chemical Warning:** Wet-sand a light `1.0 × 30°` outer bevel on both ends with 400-grit sandpaper for smooth O-ring entry. **Never clean PMMA with isopropyl alcohol (IPA)** or seal with acetic-cure silicone. Wash only with warm soapy water and seal exclusively with **`OTTOSEAL® S 72 Clear`** (`MECH-SEAL-1`, Röhm-certified PMMA-safe neutral-alkoxy silicone) with a **mandatory 48-hour open-air cure** before closing the shroud/lid!
- **LED Stars (`D1..D8`):** Order `4× Luminus SST-10-UV 365 nm` + `1× Cree XP-E2 Cool White` (`20 mm` Cu DTP) from Kaidomain, and `2× Cree XP-E2 Royal Blue 455 nm` (`LT-2231`) + `1× Cree XP-E2 Green 528 nm` (`LT-2228`) (`20 mm` Star) from LED-TECH.DE. Verify electrically neutral thermal pads with a multimeter before assembly.
- **3D Printing (8 Support-Free Parts in Black PETG or ASA + Signal-Orange Accent, `0.2 mm` layers, `4` perimeters, `25%` gyroid infill, `0` supports; avoid plain PLA):**
  - [mech_cap_bot.step](../mechanical_design/cad/mech_cap_bot.step) — inverted (top rim flat on bed).
  - [mech_lid_bot.step](../mechanical_design/cad/mech_lid_bot.step) — upright (flat bottom face on bed).
  - [mech_cable_clamp.step](../mechanical_design/cad/mech_cable_clamp.step) — print `2×`, upright on flat bottom face.
  - [mech_core_anchor.step](../mechanical_design/cad/mech_core_anchor.step) — inverted on flat top face.
  - [mech_cap_top.step](../mechanical_design/cad/mech_cap_top.step) — upright (bottom rim on bed).
  - [mech_plug_top.step](../mechanical_design/cad/mech_plug_top.step) — inverted on flat finial face.
  - [mech_hang_bushing.step](../mechanical_design/cad/mech_hang_bushing.step) — print `2×` in Signal Orange, flat on outer flange.
  - [mech_drill_jig.step](../mechanical_design/cad/mech_drill_jig.step) — flat back plate on bed (PETG/PLA fine).

## 2. Step-by-Step Build Sequence

### Step 1 — Drill, Tap & Chimney-Only Spray the Aluminum Core (`MECH-HS-CORE`)
All drill coordinates below match [cad_params.json](../mechanical_design/cad/cad_params.json) (`drill_guide_from_core_bot_mm`) and [mech_drill_jig.step](../mechanical_design/cad/mech_drill_jig.step) 1:1, measured from the **bottom end** of the `200.0 mm` `30 × 30 × 3.0 mm` Al 6063-T6 tube:

| Feature | Faces | Distance from Core Bottom (mm) | Drill / Operation |
|---|---|---:|---|
| `MECH-CORE-ANCHOR` flush cross-pins (`2× M3×8` CSK) | `±X` only (`2` faces) | **`13.0 mm`** | Drill `Ø3.4 mm` clearance + `90°` countersink flush |
| Visible star bottom edge-clamp bolt (`4× M3×8` pan) | All `4` faces | **`34.8 mm`** | Drill `Ø2.5 mm`, tap `M3 × 0.5` *(star center `46.5 mm`)* |
| Visible star top edge-clamp bolt (`4× M3×8` pan) | All `4` faces | **`58.2 mm`** | Drill `Ø2.5 mm`, tap `M3 × 0.5` |
| UV star bottom edge-clamp bolt (`4× M3×8` pan) | All `4` faces | **`68.8 mm`** | Drill `Ø2.5 mm`, tap `M3 × 0.5` *(star center `80.5 mm`)* |
| UV star top edge-clamp bolt (`4× M3×8` pan) | All `4` faces | **`92.2 mm`** | Drill `Ø2.5 mm`, tap `M3 × 0.5` |
| `MECH-CAP-TOP` vertical collar lock (`2× M3×10` SHCS) | `±X` only (`2` faces) | **`135.3 mm`** | Drill `Ø2.5 mm`, tap `M3 × 0.5` |
| Paracord hanging hole (`MECH-HANG-BUSHING`) | `±X` only (`2` faces) | **`184.0 mm`** *(`16.0 mm` from top)* | Drill `Ø8.0 mm` through both `±X` walls; deburr |

- **Chimney-Only Matte-Black Spray (`MECH-PAINT-1`):** Mask the lower `141.5 mm` of the tube (leaving **only the top `58.5 mm` protruding chimney** exposed), degrease the chimney, and apply 2 light coats of matte-black high-temp spray paint. Leaving the interior shroud section bare mill aluminum eliminates UV paint outgassing inside the PMMA shroud AND eliminates star-pad masking!

### Step 2 — Press Brass Heat-Set Inserts (`220–240 °C` Soldering Iron)
- **`MECH-CAP-BOT`:** `4× M3 × 5.0 × 4.2 mm` inserts into the recessed lid shelf at `R = 40.2 mm`.
- **`MECH-LID-BOT`:** `4× M2.5 × 4.0 × 3.5 mm` inserts into the tops of the 4 integral PCB standoffs + **`2× M3 × 4.0 × 4.2 mm` short inserts** into the **blind** cable-clamp pockets on the underside (stops cleanly against the `1.5 mm` solid roof into the dry bay!).
- **`MECH-CORE-ANCHOR`:** `4× M3 × 5.0 × 4.2 mm` inserts (`2×` vertical `±Y` bottom bores + `2×` horizontal `±X` cross-pin bores — orthogonal and staggered `> 4.4 mm`, zero collision).

### Step 3 — Pre-Wire & Edge-Clamp the `8×` LED Stars (4-Face Map)
Solder all inter-star jumpers on a silicone/wood mat **before** bolting to the core using `24 AWG` UV-stable silicone wire (`HARN-03`), terminating each 4S string onto a `HARN-01` pre-crimped 2-pin JST-XH pigtail (`125 mm` tails). Place the two Royal Blue emitters on **opposite faces (`+X` and `-X`)** for balanced 360° attraction:

| Core Face | Upper Tier (`Z_core = 80.5 mm`, Ch1 `J2`) | Lower Tier (`Z_core = 46.5 mm`, Ch2 `J3`) | Perimeter Series Wiring Order |
|---|---|---|---|
| **Face 1 (`+X`)** | `D1` — `SST-10-UV 365 nm` | `D5` — `XP-E2 Royal Blue 455 nm` | `J2.1 (+) → D1 → D2 → D3 → D4 → J2.2 (-)` |
| **Face 2 (`+Y`)** | `D2` — `SST-10-UV 365 nm` | `D7` — `XP-E2 Green 528 nm` | `J3.1 (+) → D5 (RB) → D7 (GR) → D6 (RB) → D8 (CW) → J3.2 (-)` |
| **Face 3 (`-X`)** | `D3` — `SST-10-UV 365 nm` | `D6` — `XP-E2 Royal Blue 455 nm` | *(Royal Blue opposite on Faces 1 & 3)* |
| **Face 4 (`-Y`)** | `D4` — `SST-10-UV 365 nm` | `D8` — `XP-E2 Cool White 6200 K` | *(Green opposite Cool White on Faces 2 & 4)* |

- Apply a thin layer of thermal paste (`MECH-TIM-1`) under each `20 mm` star and edge-clamp at `R = 11.7 mm` (`23.4 mm` bolt pitch) using `16× M3 × 8 mm` pan screws and `16× M3` DIN 125 (`Ø7.0 mm`) nylon insulating washers (`1.80 mm` positive rim bite; screw shank clears every round `Ø20.0 mm` star). Verify `> 10 MΩ` isolation from every solder pad to the Al core.

### Step 4 — Finish `driver_pcb` & Assemble the Open-Air Lid Sub-Assembly (`MECH-LID-BOT`)
1. Hand-solder only `J1` (`GCT USB4085-GF-A`), `J2`, `J3`, and `J4` onto `driver_pcb`.
2. Cut the `HARN-02` 3-pin JST-XH pigtail to `75 mm` and solder to `SW1` (`C&K 7211SYZBE`):

| `SW1` Lug(s) | `J4` Pin | Pos 1 (`OFF`) | Pos 2 (`4-UV`) | Pos 3 (`8-ALL`) |
|---|---|---|---|---|
| **Lugs `2 + 5` (tied)** | **`J4.2` (`GND`)** | Common `GND` | Common `GND` | Common `GND` |
| **Lug `6`** | **`J4.1` (`SW_UV_IN`)** | Closed to `GND` (`U1` OFF) | Open (`U1` ON) | Open (`U1` ON) |
| **Lug `3`** | **`J4.3` (`SW_VIS_IN`)** | Closed to `GND` (`U2` OFF) | Closed to `GND` (`U2` OFF) | Open (`U2` ON) |
| **Lugs `1` and `4`** | **No Connect** | — | — | — |

3. Seat `SW1` into `MECH-LID-BOT`'s `12.70(X) × 11.43(Y)` anti-rotation pocket (throw along X; pull toward the `0`-rib outer edge = `OFF`) and tighten `SW1_BOOT` underneath.
4. Press the `Ø8 mm` adhesive IP68 ePTFE breather vent patch (`MECH-VENT-1`) squarely into the cut `Ø9.5 × 0.8 mm` recessed pocket on the **inside top face** of `MECH-LID-BOT`.
5. Pass the intact `90°` USB-C PD plug (`HARN-04`) up through `MECH-LID-BOT`'s `16.5 × 14.5 mm` stadium port.
6. Bolt `driver_pcb` (**`F.Cu` SMD/JST-side UP!**) onto `MECH-LID-BOT`'s four `M2.5` brass-insert standoffs using **`4× M2.5 × 6 mm` nylon pan-head screws** (`MECH-FAST-M25`). Mate `J1` (90° USB-C plug) and `J4` (`SW1` pigtail) right on the bench in completely open air!

## 3. Staged Open-Air Bench Bring-Up (Using `TP1..TP4` & `D12`)

With `driver_pcb` mounted face-up on `MECH-LID-BOT` and `J2`/`J3` unplugged, every probe point (`TP1..TP4`) and red status LED `D12` are right in front of you:

1. **Unplugged Shorts Check:** Confirm `TP1` (`VIN_20V`) to `TP4` (`GND`) `> 5 kΩ`, `VBUS` to `GND` `> 10 kΩ`, and `J2`/`J3` open.
2. **20 V PD Negotiation (`J2`/`J3` Unplugged, `SW1` = `OFF`):** Plug `HARN-04` into a `45–100 W` USB-C PD charger. Confirm red LED `D12` lights cleanly on top of the PCB, `V(TP1) = 20.0 V ± 1.0 V`, `V(TP2, V_REF) = 2.500 V ± 0.03 V`, and `V(TP3, UVLO_OK) ≈ 10.0 V`.
3. **5 V UVLO Rejection Check:** Plug into a legacy `5 V` USB port; confirm `V(TP3) < 0.2 V` and `V(U1_CTRL) < 50 mV`, `V(U2_CTRL) < 50 mV`.
4. **LED Load Test (Power Off Before Mating `J2`/`J3`; Wear UV400 Glasses):** Mate `J2` and `J3` downward onto the top-facing headers, reconnect `20 V` PD, and verify `OFF` (`< 15 mA`), `4-UV` (`~0.25 A`, `V(R3) = 100 mV ± 6 mV`), and `8-ALL` (`~0.454 A`, `V(R3) ≈ V(R4) ≈ 100 mV`).

## 4. Final Mechanical Assembly & Weatherproof Sealing

1. **Lock Core to Base:** Slide `MECH-CORE-ANCHOR` into the bottom of `MECH-HS-CORE` and secure flush on `±X` with `2× M3 × 8 mm` CSK screws (`13.0 mm` from core bottom). Pass both 2-pin JST-XH plugs (`HARN-01`) straight down through the `±Y` wire channels in `MECH-CAP-BOT`, seat the core fully into its `31.1 × 31.1 mm` socket, and fasten `2× M3 × 12 mm` SHCS upward through the bulkhead on `±Y` `(0, ±6.5 mm)` into `MECH-CORE-ANCHOR`.
2. **Shroud, Roof, Finial, Hang Bushings & DIY Wire Bail:** Seat `MECH-GASKET-1/2` (`60 × 3.5 mm` VMQ50/60, lightly lubricated) in `MECH-CAP-BOT` and `MECH-CAP-TOP`. Slide the beveled `0A070` PMMA tube into the base, slide `MECH-CAP-TOP` over the chimney onto the tube, and fasten `2× M3 × 10 mm` SHCS into the vertical `40.4 × 40.4 mm` collar walls (`135.3 mm` from core bottom). Fill the top silicone groove and `MECH-PLUG-TOP` skirt with **`OTTOSEAL® S 72 Clear`**, press `MECH-PLUG-TOP` flush, and snap both Signal-Orange `MECH-HANG-BUSHING` halves (`Ø4.0 mm` pivot bore) into the `Ø8.0 mm` hanging hole (`184.0 mm` from core bottom). **Allow `OTTOSEAL S 72` to cure open-air for 48 hours before sealing the bottom lid!**
   - **DIY C-Clip Wire Hanging Bail (Workshop Coat Hanger, `£0`):** Cut a **`~175 mm`** straight section of stiff **`Ø2.2–3.0 mm`** steel wire (e.g., standard metal coat hanger or `2.5–3.0 mm` welding/fencing rod) and bend symmetrically with pliers into a tapered lantern bail matching [assembly_section_xz.png](../mechanical_design/cad/assembly_section_xz.png): **`44 mm`** outer width across vertical `30 mm` side legs, **`8.5 mm`** inward-pointing horizontal pivot pins (ending `16 mm` apart inside the Al core bore), and shoulders converging at `~22°` to a rounded **`~17 mm`** top hanging crown (`39 mm` clear above the finial — fits any carabiner, S-hook, or branch). The converging shoulders self-center the hook and actively pull both pivot pins **inward** under weight so the clip cannot splay open; spring the legs apart slightly by hand to pop the bail in or out for packing.
3. **Final Lid Insertion & Conical Cable Clamp:** Cut a `10 mm` length of `MECH-GROMMET-1` (`Ø8 × Ø4 mm` silicone tubing), slit it lengthwise, wrap it around the USB-C cable jacket, and bolt both `MECH-CABLE-CLAMP` conical halves underneath `MECH-LID-BOT` using `2× M3 × 12 mm` SHCS into the blind `M3×4` inserts (the 45° conical seat compresses the silicone sleeve radially onto the cable). Mate `J2` and `J3` onto the top-facing `driver_pcb` headers, seat `MECH-GASKET-3` (`68 × 2.5 mm` VMQ70) on the lid spigot, slide the entire lid + PCB + mated USB-C assembly **straight up** into `MECH-CAP-BOT`'s `Ø71.6 mm` bore in one smooth stroke, and fasten with `4× M3 × 12 mm` SHCS.
