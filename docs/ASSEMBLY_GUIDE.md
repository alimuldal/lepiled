# LepiLED DIY Maxi Switch — Assembly & Bring-Up Guide

## 1. Pre-Assembly Safety & Ordering Checklist

- **UV-A Eye Safety:** Wear EN166 / ANSI Z87+ UV400 safety glasses whenever the `365 nm` UV LEDs (`D1..D4`) are powered. Never stare directly into the shroud.
- **No Live Hot-Plugging of LED Headers:** Always unplug USB-C power before mating or unmating `J2` (UV) or `J3` (Visible).
- **Driver PCB (`driver_pcb`):** Upload [driver_pcb_gerbers.zip](../pcb_design/gerbers/driver_pcb/driver_pcb_gerbers.zip) (`36 × 46 mm`, 2-layer `1.6 mm` FR4, 1 oz Cu, **Lead-Free HASL**, Green LPI / White silk, **Top Side** assembly, **Economic PCBA**, Qty `2`; select **"Remove order number"** to keep the back silkscreen clean) to JLCPCB:
  - **Hybrid 2-Reel Budget PCBA (recommended — 2 Extended reels = `$6` feeder fees):** Upload [driver_pcb_bom_pcba_hybrid.csv](../pcb_design/driver_pcb_bom_pcba_hybrid.csv) and [driver_pcb_cpl_hybrid.csv](../pcb_design/driver_pcb_cpl_hybrid.csv) (`40` SMDs assembled by JLCPCB), then hand-solder the `10` remaining parts (`J1..J4` THT + `F1`, `D11`, `L1`, `L2`, `R3`, `R4`) listed in [driver_pcb_diy_hand_solder.csv](../pcb_design/driver_pcb_diy_hand_solder.csv) using [assembly_map.pdf](../pcb_design/driver_pcb/renders/assembly_map.pdf). (`D13/D14` are optional DNP.)
  - **Placement Check:** Confirm the polarity and Pin-1 orientation of `D9/D10`, `D12`, `U1..U5`, `Q2/Q3`, and `D15/D16` in JLCPCB's 3D preview before checkout.
- **Acrylic Shroud (`MECH-TUBE-1`):** Order `Ø60.0 × 54.0 × 3.0 × 115 mm` (`±2.0 mm` tolerant) **clear unstabilized extruded PMMA (`Plexiglas XT`)**. Do not use UV-blocking cast `Plexiglas GS` or polycarbonate. Wet-sand a light `1.0 × 30°` outer bevel on both ends with 400-grit sandpaper for smooth O-ring entry.
  - **Chemical Warning:** Never clean PMMA with isopropyl alcohol (IPA) or seal with acetic-cure (vinegar-smelling) silicone. Clean with warm soapy water and seal exclusively with **neutral-cure oxime RTV silicone** (`MECH-SEAL-1`, e.g. Dow 7091 / Loctite SI 5980).
- **LED Stars:** Order `8×` pre-mounted `20 mm` Copper DTP star MCPCBs (`4× Luminus SST-10-UV 365 nm`, `2× Cree XP-E2 Royal Blue`, `1× Green`, `1× Cool White`) with electrically neutral thermal pads.
- **3D Printing (8 Support-Free Parts in Matte Black ASA + Signal-Orange Accent, `0.2 mm` layers, `4` perimeters, `25%` gyroid infill, `0` supports):**
  - [mech_cap_bot.step](../mechanical_design/cad/mech_cap_bot.step) — inverted (top rim flat on bed; optional `0.15 mm` fuzzy skin on the outer tapered wall with a keepout over the O-ring bore).
  - [mech_lid_bot.step](../mechanical_design/cad/mech_lid_bot.step) — upright (flat bottom face on bed).
  - [mech_cable_clamp.step](../mechanical_design/cad/mech_cable_clamp.step) — print `2×`, upright on flat bottom face.
  - [mech_core_anchor.step](../mechanical_design/cad/mech_core_anchor.step) — inverted on flat top face.
  - [mech_cap_top.step](../mechanical_design/cad/mech_cap_top.step) — upright (bottom rim on bed).
  - [mech_plug_top.step](../mechanical_design/cad/mech_plug_top.step) — inverted on flat finial face.
  - [mech_hang_bushing.step](../mechanical_design/cad/mech_hang_bushing.step) — print `2×` in Signal Orange, flat on outer flange.
  - [mech_drill_jig.step](../mechanical_design/cad/mech_drill_jig.step) — flat back plate on bed (PLA/PETG fine).

## 2. Step-by-Step Build Sequence

1. **Drill, Tap & Matte-Black Spray the Aluminum Core (`MECH-HS-CORE`, `30 × 30 × 3.0 × 200 mm`):**
   - Slip [mech_drill_jig.step](../mechanical_design/cad/mech_drill_jig.step) flush over the bottom end of the tube:
     - On all 4 faces, drill `4× Ø2.5 mm` pilot holes (`16` total: `46.5`, `65.5`, `78.5`, `97.5 mm` from bottom) and tap `M3 × 0.5`.
     - On two opposite `±X` faces only, drill `Ø2.5 mm` and tap `M3 × 0.5` at the top guide (`139.5 mm`), and drill `Ø3.4 mm` clearance + `90°` countersink at the bottom guide (`7.5 mm`) for the flush anchor cross-pins.
   - Drill `1× Ø8.0 mm` hanging hole across `±X`, centered `16.0 mm` down from the top end.
   - Degrease the tube, mask the `8× Ø20 mm` star pads with tape circles (and plug the `M3` holes with scrap screws), apply 2 light coats of matte-black high-temp spray paint (`MECH-PAINT-1`), and peel the masks once dry.
2. **Press Brass Heat-Set Inserts (Soldering Iron @ `220–240 °C`):**
   - `MECH-CAP-BOT`: `4× M3` inserts into the recessed lid shelf and `4× M2.5` inserts into the four PCB standoffs.
   - `MECH-LID-BOT`: `2× M3` inserts into the split cable clamp bores.
   - `MECH-CORE-ANCHOR`: `4× M3` inserts (`2×` vertical bottom bores, `2×` horizontal cross-pin bores).
3. **Pre-Wire the `8×` Copper Stars on the Bench (Before Bolting to the Core):**
   - Solder all inter-star jumpers on a silicone/wood mat with `24 AWG` UV-stable silicone wire (`HARN-03`), terminating each 4S string onto a `HARN-01` pre-crimped 2-pin JST-XH pigtail (leave `125 mm` tails):
     - **Ch1 UV (`4× SST-10-UV`):** `Pin 1 Red → D1+ → ... → D4- → Pin 2 Black`.
     - **Ch2 Vis (`2× RB + 1× GR + 1× CW`):** `Pin 1 Red → D5+ → ... → D8- → Pin 2 Black`.
   - Apply a thin layer of thermal paste (`MECH-TIM-1`) under each star and bolt onto the `8×` masked pads with `16× M3 × 8 mm` pan screws and `16× M3` nylon insulating washers (`MECH-WASH-NYLON`). Verify `> 10 MΩ` isolation to the core.
4. **Finish `driver_pcb` & Populate `MECH-LID-BOT`:**
   - Hand-solder `J1..J4` (and `F1`, `D11`, `L1`, `L2`, `R3`, `R4` in Hybrid mode) onto `driver_pcb`.
   - Cut the `HARN-02` 3-pin JST-XH pigtail to `115 mm` and solder to `SW1` (`C&K 7211SYZBE`):

| `SW1` Lug(s) | `J4` Pin | Pos 1 (`OFF`) | Pos 2 (`4-UV`) | Pos 3 (`8-ALL`) |
|---|---|---|---|---|
| **Lugs `2 + 5` (tied)** | **`J4.2` (`GND`)** | Common `GND` | Common `GND` | Common `GND` |
| **Lug `6`** | **`J4.1` (`SW_UV_IN`)** | Closed to `GND` (`U1` OFF) | Open (`U1` ON) | Open (`U1` ON) |
| **Lug `3`** | **`J4.3` (`SW_VIS_IN`)** | Closed to `GND` (`U2` OFF) | Closed to `GND` (`U2` OFF) | Open (`U2` ON) |
| **Lugs `1` and `4`** | **No Connect** | — | — | — |

   - Seat `SW1` into `MECH-LID-BOT` (oriented so pulling toward the smooth `0`-rib outer rim = `OFF`) and tighten `SW1_BOOT` from underneath.
   - Stick the `Ø8 mm` ePTFE breather vent patch (`MECH-VENT-1`) over the `Ø2.5 mm` vent hole on the sheltered **inside top face** of `MECH-LID-BOT`.
   - Cut a `28.3 ± 0.3 mm` piece of `Ø2.5 mm` clear PMMA rod (or clear filament), sand a `45°` bevel on the bottom tip aimed toward the side portal, and seal it into the `D12` lightpipe bore (`1.0 mm` protrusion below the lid) with a dab of neutral-cure oxime silicone.

## 3. Staged Bench Bring-Up

1. **Unplugged Shorts Check:** Confirm `VIN_20V` to `GND` `> 5 kΩ`, `VBUS` to `GND` `> 10 kΩ`, and `J2`/`J3` open.
2. **20 V PD Negotiation (`J2`/`J3` Unplugged, `SW1` = `OFF`):** Plug the `90°` USB-C PD cable (`HARN-04`) into a `45–100 W` USB-C PD charger and `J1`. Confirm red status LED `D12` lights, `V(VIN_20V) = 20.0 V ± 1 V`, and `V(V_REF) = 2.500 V ± 0.03 V`.
3. **5 V UVLO Rejection Check:** Plug into a legacy `5 V` USB port; confirm `V(U1_CTRL) < 50 mV` and `V(U2_CTRL) < 50 mV`.
4. **LED Load Test (Power Off Before Mating `J2`/`J3`; Wear UV400 Glasses):** Mate `J2`, `J3`, and `J4`, reconnect `20 V` PD, and verify `OFF` (`< 15 mA`), `4-UV` (`~0.25 A`, `V(R3) = 100 mV ± 6 mV`), and `8-ALL` (`~0.453 A`, `V(R3) ≈ V(R4) ≈ 100 mV`).

## 4. Final Mechanical Assembly & Sealing

1. **Lock Core to Base:** Slide `MECH-CORE-ANCHOR` into the bottom of `MECH-HS-CORE` and secure flush with `2× M3 × 8 mm` CSK screws. Pass both 2-pin JST-XH plugs (`HARN-01`) down through the `±Y` wire channels in `MECH-CAP-BOT`, seat the core fully into its square socket, and fasten `2× M3 × 12 mm` SHCS upward through the bulkhead into `MECH-CORE-ANCHOR` before installing the PCB.
2. **Shroud, Roof, Finial & Hang Bushing:** Lightly grease `MECH-GASKET-1/2` (`60 × 3.5 mm` VMQ50/60) with silicone grease and seat them in `MECH-CAP-BOT` and `MECH-CAP-TOP`. Slide the beveled PMMA tube into the base, slide the top cap over the core onto the tube, and fasten `2× M3 × 10 mm` SHCS into the top-cap shoulders with a dab of oxime silicone under the heads. Fill the top core-exit groove and finial skirt with neutral-cure oxime silicone, press `MECH-PLUG-TOP` flush, and snap both Signal-Orange `MECH-HANG-BUSHING` halves into the `Ø8.0 mm` hole.
3. **Install PCB, Cable Clamp & Bottom Lid:** Mate `J2` and `J3`, then bolt `driver_pcb` (SMD/JST-side down) onto the four `M2.5` brass-insert standoffs with `4× M2.5 × 6 mm` pan screws. Pass the intact `90°` USB-C plug up through the lid port and mate it into `J1`, and plug `SW1` (`HARN-02`) into `J4`. Wrap a thin slit silicone sleeve (or bead of oxime silicone) around the cable jacket, clamp both `MECH-CABLE-CLAMP` halves into the lid port with `2× M3 × 12 mm` SHCS, grease `MECH-GASKET-3` (`62 × 2.5 mm` VMQ70), press `MECH-LID-BOT` into the recessed base skirt, and fasten with `4× M3 × 10 mm` SHCS.
