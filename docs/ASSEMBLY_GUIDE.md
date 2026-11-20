# LepiLED DIY Maxi Switch — Assembly, Commissioning & Bring-Up Guide (Rev 4.5)

## 1. Pre-Assembly Safety & Ordering Checklist

- **UV-A Eye Safety:** Wear EN166 / ANSI Z87+ UV400 safety glasses whenever `D1..D4` (`365 nm` Luminus `SST-10-UV`) are energized. Never stare directly into the shroud.
- **No Live Hot-Plugging of LED Headers:** Always unplug USB-C power before mating or unmating `J2` (UV) or `J3` (Visible).
- **Single Custom PCB (`driver_pcb` ONLY):** Upload [driver_pcb_gerbers.zip](file:///home/alimuldal/src/lepiled/pcb_design/gerbers/driver_pcb/driver_pcb_gerbers.zip) (`36 × 46 mm`, 2-layer `1.6 mm` FR4, 1 oz Cu, **ENIG**, Green LPI / White silk) to JLCPCB along with [driver_pcb_bom_pcba.csv](file:///home/alimuldal/src/lepiled/pcb_design/driver_pcb_bom_pcba.csv) and [driver_pcb_cpl.csv](file:///home/alimuldal/src/lepiled/pcb_design/driver_pcb_cpl.csv) (`57` SMD parts assembled via JLCPCB Economic PCBA; `J1..J4` THT hand-soldered on the bench using [assembly_map.pdf](file:///home/alimuldal/src/lepiled/pcb_design/driver_pcb/renders/assembly_map.pdf)).
- **Clear Unstabilized Extruded PMMA Shroud (`MECH-TUBE-1`):** Order `Ø60.0 × 54.0 × 3.0 mm × 115 mm` (`±2.0 mm` cut-length tolerant) **unstabilized clear extruded PMMA (`Plexiglas XT`)** tubing (`85–92%` @ `365 nm`). **Do NOT use UV-blocking standard cast `Plexiglas GS` or polycarbonate (PC)**. Quick arrival check: shine a `365 nm` torch through the tube wall onto white paper or a banknote—fluorescence should stay bright.
  - **Chemical Warning (PMMA):** Never clean PMMA with **isopropyl alcohol (IPA)** or seal with **acetic-cure (vinegar-smelling) silicone**—both cause environmental stress crazing in acrylic! Clean PMMA only with warm soapy water and seal joints exclusively with **neutral-cure oxime RTV silicone** (`MECH-SEAL-1`, e.g. Dow 7091 / Loctite SI 5980).
- **Pre-Mounted LEDs (`Zero Bare-SMD Reflow`):** Order `8×` pre-mounted **`20 mm` Copper DTP star MCPCBs** (`4× Luminus SST-10-UV 365 nm`, `2× Cree XP-E2 Royal Blue 455 nm`, `1× XP-E2 Green 528 nm`, `1× XP-E2 Cool White 6200–6500 K`) from Kaidomain/Convoy (or `LED-Tech.de`).
- **3D Printing (6 Support-Free FDM Parts in PETG or Black ASA, `0.2 mm` layers, `4` perimeters, `25%` gyroid infill, `0` supports — `MECH-PLUG-BOT` eliminated):**
  - [mech_base_ring.step](file:///home/alimuldal/src/lepiled/mechanical_design/cad/mech_base_ring.step) — inverted (`Z = 0` mating face on bed, `0.000 mm²` overhang).
  - [mech_lid_bot.step](file:///home/alimuldal/src/lepiled/mechanical_design/cad/mech_lid_bot.step) — upright (`Z = 0` flat bottom face on bed, `0.000 mm²` overhang).
  - [mech_cap_bot.step](file:///home/alimuldal/src/lepiled/mechanical_design/cad/mech_cap_bot.step) — **inverted** (`Z = 77.0 mm` top shroud rim flat on bed, `0.917 mm²` `>46°` overhang).
  - [mech_cap_top.step](file:///home/alimuldal/src/lepiled/mechanical_design/cad/mech_cap_top.step) — **upright** (`Z = 168.0 mm` bottom shroud rim flat on bed, `0.000 mm²` overhang).
  - [mech_plug_top.step](file:///home/alimuldal/src/lepiled/mechanical_design/cad/mech_plug_top.step) — inverted (flat top cap face on bed, `0.000 mm²` overhang).
  - [mech_drill_jig.step](file:///home/alimuldal/src/lepiled/mechanical_design/cad/mech_drill_jig.step) — flat back plate on bed (`0.000 mm²` overhang).

## 2. Step-by-Step Build Sequence

1. **Drill & Tap the Single Stock Aluminum Tube (`MECH-HS-CORE`, `30 × 30 × 3.0 mm × 200 mm`, Zero Sawing):**
   - Slip the 3D-printed snap-on drilling jig ([mech_drill_jig.step](file:///home/alimuldal/src/lepiled/mechanical_design/cad/mech_drill_jig.step)) over the bottom end of the `200 mm` tube (end-stop flush against the bottom end):
     - On all 4 faces, drill `4× Ø2.5 mm` pilot holes (`16` holes total: Vis star screws at `44.0 / 63.0 mm`, UV star screws at `76.0 / 95.0 mm` from the bottom end) and tap **`M3 × 0.5`** (`3 mm` wall gives `6` full threads).
     - On the two opposite `±X` faces only, use the jig's bottom and top guide holes (`6.0 mm` and `130.5 mm` from the bottom end) to drill `4× Ø2.5 mm` holes and tap **`M3 × 0.5`** for the `MECH-CAP-BOT` and `MECH-CAP-TOP` radial locking screws.
   - Drill `1× Ø8.0 mm` hanging hole straight across the protruding top (`16.0 mm` down from the top end, centered at `Y = 0`).
   - Deburr all edges and degrease the aluminum with warm soapy water (or IPA *before* bringing the PMMA tube anywhere near the bench). *(Optional: a light coat of matte-black high-temp spray paint on just the top `57 mm` protruding chimney drops LED temperatures by `~9 °C` for hot `30–35 °C` nights.)*
2. **Pre-Wire All `8×` `20 mm` Copper DTP Stars on the Bench (CRITICAL: BEFORE Mounting to the Core!):**
   - Lay all `8×` copper stars on a silicone mat or piece of wood—**never solder wires after bolting stars onto the aluminum core**, or the aluminum tube will sink heat out of the iron.
   - Use **`24 AWG` silicone-insulated wire (`HARN-03`)** for all inter-star jumpers inside the `365 nm` UV chamber (PVC embrittles under UV-A), feeding the two `HARN-01` pre-crimped 2-pin JST-XH pigtails:
     - **Ch1 UV String (`4× SST-10-UV`):** `HARN-01` 2-pin JST-XH (`Pin 1 Red -> D1+`, `D1- -> D2+`, `D2- -> D3+`, `D3- -> D4+`, `D4- -> Pin 2 Black`).
     - **Ch2 Vis String (`2× RB + 1× GR + 1× CW`):** Second `HARN-01` 2-pin JST-XH (`Pin 1 Red -> D5+`, `D5- -> D6+`, `D6- -> D7+`, `D7- -> D8+`, `D8- -> Pin 2 Black`).
   - Leave `~100 mm` tail length on the JST-XH pigtails; verify every star lights cleanly with a multimeter diode check before mounting.
3. **Bolt Stars to `MECH-HS-CORE` (`M3` + Mandatory Nylon Washers):**
   - Apply a thin, even layer of PC thermal paste (`MECH-TIM-1`, e.g. Arctic MX-4) under each `20 mm` Copper DTP star.
   - Bolt all 4 UV stars (top row, `85.5 mm` from core bottom) and all 4 Visible stars (bottom row, `53.5 mm` from core bottom) onto the 4 flat faces using **`16× M3 × 8 mm` pan-head screws WITH `16× M3` nylon insulating washers (`MECH-WASH-NYLON`) under every screw head**. Verify `> 10 MΩ` isolation between `+`/`-` leads and the aluminum core.
4. **Hand-Solder `J1..J4` on `driver_pcb` & Prepare `MECH-LID-BOT`:**
   - Hand-solder `J1` (`USB4085-GF-A`), `J2/J3` (`B2B-XH-A`), and `J4` (`B3B-XH-A`) onto the JLCPCB-assembled `driver_pcb` using [assembly_map.pdf](file:///home/alimuldal/src/lepiled/pcb_design/driver_pcb/renders/assembly_map.pdf).
   - Solder the pre-crimped `22 AWG` 3-pin JST-XH pigtail (`HARN-02`, leave `~60 mm` length) directly to the gold solder lugs of `SW1` (`C&K 7211SYZBE`, `DPDT On-On-On`):

| `C&K 7211SYZBE` Lug(s) | Wire Destination (`J4`) | Pos 1 (`OFF`) | Pos 2 (`4-UV`) | Pos 3 (`8-ALL`) |
|---|---|---|---|---|
| **Lugs `2 + 5` (tied together)** | **`J4.2` (`GND`)** | Common `GND` | Common `GND` | Common `GND` |
| **Lug `6`** | **`J4.1` (`SW_UV_IN`)** | Closed to `GND` (`U1` OFF) | Open (`U1` ON) | Open (`U1` ON) |
| **Lug `3`** | **`J4.3` (`SW_VIS_IN`)** | Closed to `GND` (`U2` OFF) | Closed to `GND` (`U2` OFF) | Open (`U2` ON) |
| **Lugs `1` and `4`** | **No Connect (leave bare)** | — | — | — |

   - Seat `SW1` into the anti-rotation pocket on `MECH-LID-BOT` (`X = 0, Y = +18.5 mm`) with the toggle pointing straight **downward**, and tighten `SW1_BOOT` (`C&K 759D02000`) from underneath.
   - Stick the **`Ø8 mm` IP68 ePTFE breather vent patch (`MECH-VENT-1`)** cleanly over the `Ø2.5 mm` vent bore (`X = -23.0, Y = 0.0 mm`) on the sheltered underside of `MECH-LID-BOT`.
   - Glue a short `~18 mm` stub of `Ø2.5 mm` clear PMMA rod (or clear transparent filament) into the `D12` lightpipe bore (`X = +16.0, Y = +1.4 mm`) using a tiny dab of neutral-cure oxime silicone (`MECH-SEAL-1`) flush with the bottom face.

## 3. Staged Bench Bring-Up (Standard USB-C PD Laptop Charger)

1. **Unplugged Shorts Check:** Confirm `VIN_20V` to `GND` `> 5 kΩ`, `VBUS` to `GND` `> 10 kΩ`, and `J2`/`J3` open.
2. **USB-C PD `20 V` Negotiation (`J2`/`J3` Unplugged, `SW1` = `OFF`):** Plug the `90°` USB-C PD cable (`HARN-04`) into a `45–100 W` USB-C PD laptop charger or `20 V` PD power bank and into `J1`. Confirm green LED **`D12`** shows **`4 s` breathing** (`20 V VOUT ON`; steady solid = source did not offer `20 V / 1 A`), `V(VIN_20V) = 20.0 V ± 1 V`, and `V(V_REF) = 2.500 V ± 0.01 V`.
3. **5 V UVLO Rejection Check:** Plug in a legacy `5 V` USB charger; confirm `V(U1_CTRL) < 50 mV` and `V(U2_CTRL) < 50 mV`.
4. **LED Load Test (Power Off Before Mating `J2`/`J3`; UV400 Glasses On!):** Mate `J2`, `J3`, and `J4`, reconnect the `20 V` PD charger, and check:
   - **`OFF`:** `I_in < 15 mA`, all 8 LEDs dark.
   - **`4-UV`:** `D1..D4` lit, `I_in ≈ 0.25 A @ 20 V` (`~5.0 W`), `V(R3) = 100 mV ± 6 mV`.
   - **`8-ALL`:** All 8 LEDs lit, `I_in ≈ 0.45–0.46 A @ 20 V` (`~9.1 W`), `V(R3) ≈ 100 mV`, `V(R4) ≈ 100 mV`.

## 4. Final Mechanical Assembly & Weatherproofing

1. **Direct Core Lock & Wire Routing (`MECH-CAP-BOT`, Zero `MECH-PLUG-BOT`):**
   - Pass the two pre-crimped 2-pin JST-XH plugs (`HARN-01`) straight down through the two generous `9.0 × 7.5 mm` `±Y` wire channels in `MECH-CAP-BOT` (no de-pinning needed!).
   - Slide the bottom `12 mm` of `MECH-HS-CORE` into `MECH-CAP-BOT`'s `30.8 × 30.8 mm` square collar and secure radially with **`2× M3 × 10 mm` SHCS screws** through the `±X` teardrop bores (`6 mm` below the shroud bore).
2. **Extruded XT PMMA Shroud, Radial O-Rings, Sloped Rain Roof & Top Plug:**
   - Lightly grease **`MECH-GASKET-1` and `MECH-GASKET-2` (`60 × 3.0 mm` VMQ70)** with silicone grease and seat them in the radial bore grooves of `MECH-CAP-BOT` and `MECH-CAP-TOP`.
   - Slide the clear extruded XT PMMA shroud (`MECH-TUBE-1`) straight down into `MECH-CAP-BOT` (`~30 N` smooth hand push), then slide `MECH-CAP-TOP` down over the protruding aluminum core and onto the top of the shroud.
   - Secure `MECH-CAP-TOP` with **`2× M3 × 10 mm` SHCS screws** through its sheltered `±X` teardrop bores into the tapped holes in `MECH-HS-CORE`.
   - Run a neat bead of **neutral-cure oxime RTV silicone (`MECH-SEAL-1`)** around the top core-exit chamfer groove on `MECH-CAP-TOP` and around the skirt of `MECH-PLUG-TOP` before pressing `MECH-PLUG-TOP` into the top end of the hollow `30 × 30` aluminum core. Clip any carabiner or tie paracord through the unobstructed `Ø8.0 mm` hanging hole.
3. **Horizontal `driver_pcb`, `M20` Split Cable Gland, Bottom Lid & Base Ring:**
   - Drop `4×` `M3` hex nuts into the `4×` side-entry captive nut slots around `MECH-CAP-BOT`'s lower flange.
   - Bolt `driver_pcb` horizontally **SMD/JST-side facing downward** onto the `4× Ø5.5 mm` standoffs inside `MECH-CAP-BOT` using **`4× M2.5 × 8 mm` pan-head screws** (`MECH-FAST-M25`). Mate `J2` (UV) and `J3` (Vis) directly into the downward-facing headers.
   - Thread the compact `90°` USB-C plug (`HARN-04`) through the open `M20` split cable gland body (`MECH-GLAND-1`) installed in `MECH-LID-BOT`, wrap the `Ø4–5 mm` split rubber seal around the round cable jacket, and tighten the dome nut watertight.
   - Plug the `90°` USB-C plug into `J1` and plug `SW1`'s `HARN-02` pigtail into `J4`.
   - Lightly grease **`MECH-GASKET-3` (`70 × 2.5 mm` VMQ70)** on `MECH-LID-BOT`'s radial spigot, slide `MECH-LID-BOT` straight into `MECH-CAP-BOT`, place `MECH-BASE-RING` underneath, and clamp both together with **`4× M3 × 16 mm` SHCS screws** through the base-ring counterbores. Route the captured USB-C cable out straight downward when hanging or out through one of `MECH-BASE-RING`'s four `24 × 9.5 mm` cutouts when standing upright.
