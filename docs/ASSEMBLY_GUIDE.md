# LepiLED DIY Maxi Switch — Assembly, Commissioning & Bring-Up Guide (Rev 4.6 — "Field Lantern")

## 1. Pre-Assembly Safety & Ordering Checklist

- **UV-A Eye Safety:** Wear EN166 / ANSI Z87+ UV400 safety glasses whenever `D1..D4` (`365 nm` Luminus `SST-10-UV`) are energized. Never stare directly into the shroud.
- **No Live Hot-Plugging of LED Headers:** Always unplug USB-C power before mating or unmating `J2` (UV) or `J3` (Visible).
- **Single Custom PCB (`driver_pcb` ONLY):** Upload [driver_pcb_gerbers.zip](../pcb_design/gerbers/driver_pcb/driver_pcb_gerbers.zip) (`36 × 46 mm`, 2-layer `1.6 mm` FR4, 1 oz Cu, **ENIG**, Green LPI / White silk) to JLCPCB along with [driver_pcb_bom_pcba.csv](../pcb_design/driver_pcb_bom_pcba.csv) and [driver_pcb_cpl.csv](../pcb_design/driver_pcb_cpl.csv) (`57` SMD parts assembled via JLCPCB Economic PCBA; select **"Remove order number"** so the Emperor-moth back silkscreen stays clean; hand-solder `J1..J4` THT using [assembly_map.pdf](../pcb_design/driver_pcb/renders/assembly_map.pdf)).
- **Clear Unstabilized Extruded PMMA Shroud (`MECH-TUBE-1`):** Order `Ø60.0 × 54.0 × 3.0 mm × 115 mm` (`±2.0 mm` cut-length tolerant) **unstabilized clear extruded PMMA (`Plexiglas XT`)** tubing (`85–92%` @ `365 nm`). **Do NOT use UV-blocking standard cast `Plexiglas GS` or polycarbonate (PC).** Wet-sand a light `1.0 × 30°` outer bevel on both tube ends with 400-grit sandpaper for smooth O-ring insertion.
  - **Chemical Warning (PMMA):** Never clean PMMA with **isopropyl alcohol (IPA)** or seal with **acetic-cure (vinegar-smelling) silicone**—both cause stress crazing in acrylic! Clean PMMA only with warm soapy water and seal exclusively with **neutral-cure oxime RTV silicone** (`MECH-SEAL-1`, e.g. Dow 7091 / Loctite SI 5980).
- **Pre-Mounted LEDs (`Zero Bare-SMD Reflow`):** Order `8×` pre-mounted **`20 mm` Copper DTP star MCPCBs** (`4× Luminus SST-10-UV 365 nm`, `2× Cree XP-E2 Royal Blue 455 nm`, `1× XP-E2 Green 528 nm`, `1× XP-E2 Cool White 6200–6500 K`) from Kaidomain/Convoy.
- **3D Printing (8 Support-Free FDM Parts in Matte Black ASA + Signal-Orange Accent, `0.2 mm` layers, `4` perimeters, `25%` gyroid infill, `0` supports):**
  - *Recommended CMF:* Print all structural shells in **Matte Black ASA** (`HDT 95 °C`, UV-A immune). Optional slicer **fuzzy skin (`0.15 mm` depth / `0.30 mm` spacing)** on the exterior tapered wall of `MECH-CAP-BOT` (with a cylindrical keepout over the O-ring bore) produces a rugged bead-blasted grip texture.
  - [mech_cap_bot.step](../mechanical_design/cad/mech_cap_bot.step) — **inverted** (`Z = 101.0 mm` top rim flat on bed, `0.160 mm²` `>46°` overhang).
  - [mech_lid_bot.step](../mechanical_design/cad/mech_lid_bot.step) — **upright** (`Z = 19.0 mm` flat bottom face on bed, `0.000 mm²` overhang).
  - [mech_cable_clamp.step](../mechanical_design/cad/mech_cable_clamp.step) — **print `2×`**, upright on flat bottom face (`0.000 mm²` overhang).
  - [mech_core_anchor.step](../mechanical_design/cad/mech_core_anchor.step) — **inverted** on flat top face (`0.000 mm²` overhang).
  - [mech_cap_top.step](../mechanical_design/cad/mech_cap_top.step) — **upright** (`Z = 187.0 mm` bottom rim flat on bed, `0.000 mm²` overhang).
  - [mech_plug_top.step](../mechanical_design/cad/mech_plug_top.step) — **inverted** on flat top finial face (`0.000 mm²` overhang).
  - [mech_hang_bushing.step](../mechanical_design/cad/mech_hang_bushing.step) — **print `2×` in Signal Orange (`RAL 2009`)**, flat on outer flange face (`0.000 mm²` overhang).
  - [mech_drill_jig.step](../mechanical_design/cad/mech_drill_jig.step) — flat back plate on bed (`0.000 mm²` overhang; PLA/PETG fine).

## 2. Step-by-Step Build Sequence

1. **Drill, Tap & Matte-Black Spray the Single Stock Aluminum Tube (`MECH-HS-CORE`, `30 × 30 × 3.0 × 200 mm`):**
   - Slip the snap-on drilling jig ([mech_drill_jig.step](../mechanical_design/cad/mech_drill_jig.step)) over the bottom end of the `200 mm` tube (end-stop flush against bottom):
     - On all 4 faces, drill `4× Ø2.5 mm` pilot holes (`16` total: Vis stars at `46.5 / 65.5 mm`, UV stars at `78.5 / 97.5 mm` from bottom) and tap **`M3 × 0.5`** (`3 mm` wall gives `6` full threads).
     - On the two opposite `±X` faces only, use the top guide (`139.5 mm`) to drill `Ø2.5 mm` and tap **`M3 × 0.5`** (`MECH-CAP-TOP` radial lock), and use the bottom guide (`7.5 mm`) to drill **`Ø3.4 mm` clearance + `90°` countersink** for the `2× M3 × 8 mm` CSK flush anchor cross-pins!
   - Drill `1× Ø8.0 mm` hanging hole across `±X` (`16.0 mm` down from the top end, centered at `Y = 0`).
   - Degrease the aluminum tube thoroughly, mask the `8× Ø20 mm` LED star pads with `20 mm` masking tape circles (plus plug the `M3` threads with scrap screws), and apply **2 light coats of matte-black high-temp spray paint (`MECH-PAINT-1`)** across the entire exterior (both the protruding chimney and the chamber faces between stars). Peel the 8 circular masks once dry — this drops LED junction temperatures by **`13.1–16.4 °C`** in still air (`8.5–10.4 °C` if you only spray the exposed `57 mm` top chimney).
2. **Press Brass Heat-Set Inserts (Soldering Iron @ `220–240 °C`):**
   - **`MECH-CAP-BOT`:** Press `4× M3 × 5.0 × 4.2 mm` inserts into the recessed lid shelf (`R = 36.8 mm`) and `4× M2.5 × 4.0 × 3.5 mm` inserts into the `4×` filleted PCB standoffs.
   - **`MECH-LID-BOT`:** Press `2× M3 × 5.0 × 4.2 mm` inserts into the split cable clamp bores (`X = ±12.0, Y = -18.5 mm`).
   - **`MECH-CORE-ANCHOR`:** Press `4× M3 × 5.0 × 4.2 mm` inserts (`2×` vertical bottom bores at `X = ±6.5 mm`, `2×` horizontal cross-pin bores on `±X`).
3. **Pre-Wire All `8×` `20 mm` Copper DTP Stars on the Bench (CRITICAL: BEFORE Bolting to the Core!):**
   - Solder all inter-star jumpers on a silicone/wood mat using **`24 AWG` UV-stable silicone wire (`HARN-03`)**, feeding the two `HARN-01` pre-crimped 2-pin JST-XH pigtails (leave **`125 mm`** tail length so `J2/J3` plug in comfortably!):
     - **Ch1 UV String (`4× SST-10-UV`):** `Pin 1 Red -> D1+ -> ... -> D4- -> Pin 2 Black`.
     - **Ch2 Vis String (`2× RB + 1× GR + 1× CW`):** `Pin 1 Red -> D5+ -> ... -> D8- -> Pin 2 Black`.
   - Apply a thin layer of PC thermal paste (`MECH-TIM-1`) under each star and bolt onto the `8×` masked bare-aluminum pads using **`16× M3 × 8 mm` pan screws WITH `16× M3` nylon insulating washers (`MECH-WASH-NYLON`)**. Verify `> 10 MΩ` isolation to the core.
4. **Hand-Solder `J1..J4` on `driver_pcb` & Populate `MECH-LID-BOT`:**
   - Hand-solder `J1` (`USB4085-GF-A`), `J2/J3` (`B2B-XH-A`), and `J4` (`B3B-XH-A`) onto `driver_pcb`.
   - Cut the pre-crimped `22 AWG` 3-pin JST-XH pigtail (`HARN-02`) to **`115 mm`** (gives plenty of slack to open the recessed lid and plug `J4`!) and solder directly to `SW1` (`C&K 7211SYZBE`):

| `C&K 7211SYZBE` Lug(s) | Wire Destination (`J4`) | Pos 1 (`OFF`) | Pos 2 (`4-UV`) | Pos 3 (`8-ALL`) |
|---|---|---|---|---|
| **Lugs `2 + 5` (tied together)** | **`J4.2` (`GND`)** | Common `GND` | Common `GND` | Common `GND` |
| **Lug `6`** | **`J4.1` (`SW_UV_IN`)** | Closed to `GND` (`U1` OFF) | Open (`U1` ON) | Open (`U1` ON) |
| **Lug `3`** | **`J4.3` (`SW_VIS_IN`)** | Closed to `GND` (`U2` OFF) | Closed to `GND` (`U2` OFF) | Open (`U2` ON) |
| **Lugs `1` and `4`** | **No Connect (leave bare)** | — | — | — |

   - Seat `SW1` into `MECH-LID-BOT` (`X = 0, Y = +15.0 mm`, oriented so pulling toward the smooth `0`-rib outer rim = **`OFF`**) and tighten `SW1_BOOT` (`C&K 759D02000`) from underneath.
   - Stick the **`Ø8 mm` IP68 ePTFE breather vent patch (`MECH-VENT-1`)** cleanly over the `Ø2.5 mm` vent bore (`X = -20.0, Y = 0.0 mm`) on the sheltered **INSIDE top face (`Z = 24.0 mm`)** of `MECH-LID-BOT` where mud and fingers can never disturb it.
   - Cut a **`29.8 ± 0.3 mm`** length of `Ø2.5 mm` clear PMMA rod (or clear filament), sand a **`45°` bevel** on its bottom tip aimed outward toward the side portal, and seal it into the `D12` lightpipe bore (`X = +16.0, Y = -0.6 mm`, protruding `1.0 mm` below `MECH-LID-BOT`) with a tiny dab of neutral-cure oxime silicone (`MECH-SEAL-1`).

## 3. Staged Bench Bring-Up (Standard USB-C PD Laptop Charger)

1. **Unplugged Shorts Check:** Confirm `VIN_20V` to `GND` `> 5 kΩ`, `VBUS` to `GND` `> 10 kΩ`, and `J2`/`J3` open.
2. **USB-C PD `20 V` Negotiation (`J2`/`J3` Unplugged, `SW1` = `OFF`):** Plug the `90°` USB-C PD cable (`HARN-04`) into a `45–100 W` USB-C PD charger and into `J1`. Confirm green LED **`D12`** shows **`4 s` breathing** (`20 V VOUT ON`; steady solid = source did not offer `20 V / 1 A`), `V(VIN_20V) = 20.0 V ± 1 V`, and `V(V_REF) = 2.500 V ± 0.01 V`.
3. **5 V UVLO Rejection Check:** Plug in a legacy `5 V` USB charger; confirm `V(U1_CTRL) < 50 mV` and `V(U2_CTRL) < 50 mV`.
4. **LED Load Test (Power Off Before Mating `J2`/`J3`; UV400 Glasses On!):** Mate `J2`, `J3`, and `J4`, reconnect `20 V` PD, and verify `OFF` (`< 15 mA`), `4-UV` (`~0.25 A`, `V(R3) = 100 mV ± 6 mV`), and `8-ALL` (`~0.455 A`, `V(R3) ≈ V(R4) ≈ 100 mV`).

## 4. Final Mechanical Assembly & Weatherproofing

1. **Internal Dry-Bay Core Lock (`MECH-CORE-ANCHOR` → `MECH-CAP-BOT`, Zero Exterior Holes!):**
   - Slide `MECH-CORE-ANCHOR` into the bottom of `MECH-HS-CORE` and secure flush with **`2× M3 × 8 mm` CSK screws** through the countersunk `±X` holes (`7.5 mm` from bottom).
   - Pass the two pre-crimped 2-pin JST-XH plugs (`HARN-01`) straight down through the two `9.0 × 7.5 mm` `±Y` wire channels in `MECH-CAP-BOT`.
   - Seat `MECH-HS-CORE` fully into `MECH-CAP-BOT`'s intact `30.8 × 30.8 mm` square socket, reach into the open bottom bay *before* installing `driver_pcb`, and tighten **`2× M3 × 16 mm` SHCS** straight upward at `(±6.5, 0.0 mm)` through the solid `8.6 mm` bulkhead into `MECH-CORE-ANCHOR`.
2. **Shroud, Ovality-Safe O-Rings, Lofted Roof, Finial & Signal-Orange Hang Bushing:**
   - Lightly grease **`MECH-GASKET-1/2` (`60 × 3.5 mm` soft VMQ50/60)** with silicone grease and seat them in `MECH-CAP-BOT` and `MECH-CAP-TOP`.
   - Slide the beveled extruded `XT PMMA` shroud (`MECH-TUBE-1`) down into `MECH-CAP-BOT`, then slide `MECH-CAP-TOP` down over the matte-black core onto the shroud.
   - Tighten **`2× M3 × 10 mm` SHCS** (with small silicone sealing washers or a dab of oxime silicone under the heads) into the `±X` top-cap shoulders (`4.6 mm` solid ASA) and tapped core holes.
   - Fill the backed `2.0 × 2.5 mm` top core-exit channel on `MECH-CAP-TOP` and the skirt of `MECH-PLUG-TOP` with **neutral-cure oxime RTV silicone (`MECH-SEAL-1`)**, press `MECH-PLUG-TOP` flush onto the top of the core, and snap both **Signal-Orange `MECH-HANG-BUSHING` halves** into the `Ø8.0 mm` hang hole.
3. **Horizontal `driver_pcb`, Split Cable Clamp & Recessed Bottom Lid:**
   - Plug `J2` (UV) and `J3` (Vis) into `driver_pcb` *before* fastening the board, then bolt `driver_pcb` horizontally (SMD/JST-side down) onto the `4× M2.5` brass heat-set insert standoffs inside `MECH-CAP-BOT` using **`4× M2.5 × 6 mm` pan screws**.
   - Pass the intact `90°` USB-C plug (`HARN-04`) straight up through the `16.0 × 14.0 mm` stadium port in `MECH-LID-BOT` and plug it firmly into `J1`. Mate `SW1`'s `115 mm` `HARN-02` pigtail into `J4`.
   - Wrap a short slit silicone sleeve (or neat bead of neutral-cure oxime silicone) around the `Ø4.0–4.5 mm` USB-C cable jacket, sandwich both **`MECH-CABLE-CLAMP`** halves around it into the lid port, and tighten **`2× M3 × 14 mm` SHCS** upward into `MECH-LID-BOT`'s brass inserts.
   - Lightly grease **`MECH-GASKET-3` (`62 × 2.5 mm` VMQ70)** on `MECH-LID-BOT`'s spigot, slide `MECH-LID-BOT` straight up into `MECH-CAP-BOT`'s recessed skirt, and fasten with **`4× M3 × 10 mm` SHCS** into the `4× M3` brass inserts. Route the cable out through either smooth `45°`-arch portal when standing upright, or hang dead plumb from the Signal-Orange bushed hang hole!
