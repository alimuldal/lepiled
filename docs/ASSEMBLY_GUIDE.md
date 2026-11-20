# LepiLED DIY Maxi Switch — Assembly, Commissioning & Bring-Up Guide (Rev 4.4)

## 1. Pre-Assembly Safety & Ordering Checklist

- **UV-A Eye Safety:** Wear EN166 / ANSI Z87+ UV400 safety glasses whenever `D1..D4` (`365 nm` Luminus `SST-10-UV`) are energized. Never stare directly into the shroud.
- **No Live Hot-Plugging of LED Headers:** Always unplug USB-C power before mating or unmating `J2` (UV) or `J3` (Visible).
- **Single Custom PCB (`driver_pcb` ONLY):** Upload [driver_pcb_gerbers.zip](file:///home/alimuldal/src/lepiled/pcb_design/gerbers/driver_pcb/driver_pcb_gerbers.zip) (`36 × 46 mm`, 2-layer `1.6 mm` FR4, 1 oz Cu, **ENIG**, Green LPI / White silk) to JLCPCB along with [driver_pcb_bom_pcba.csv](file:///home/alimuldal/src/lepiled/pcb_design/driver_pcb_bom_pcba.csv) and [driver_pcb_cpl.csv](file:///home/alimuldal/src/lepiled/pcb_design/driver_pcb_cpl.csv) (`57` SMD parts assembled via JLCPCB Economic PCBA; `J1..J4` THT hand-soldered on the bench using [assembly_map.pdf](file:///home/alimuldal/src/lepiled/pcb_design/driver_pcb/renders/assembly_map.pdf)).
- **UV-Transmitting PMMA Shroud (`MECH-TUBE-1`):** Order `Ø75.0 × 69.0 × 3.0 mm × 150 mm` **UV-transmitting / unstabilized cast PMMA (acrylic)** tubing (`85–92%` @ `365 nm`). **Do NOT use polycarbonate** (blocks `> 98%` of `365 nm` UV-A). Quick arrival sanity check: shine a `365 nm` torch through the tube wall onto white paper or a banknote—fluorescence should stay bright.
- **Pre-Mounted LEDs (`Zero Bare-SMD Reflow`):** Order `8×` pre-mounted **`20 mm` Copper DTP star MCPCBs** (`4× Luminus SST-10-UV 365 nm`, `2× Cree XP-E2 Royal Blue 455 nm`, `1× XP-E2 Green 528 nm`, `1× XP-E2 Cool White 6200–6500 K`) from Kaidomain/Convoy (or EU specialist `LED-Tech.de`).
- **3D Printing (7 Support-Free FDM Parts in PETG or ASA, `0.2 mm` layers, `4` perimeters, `25%` gyroid infill, `0` supports):**
  - [mech_base_ring.step](file:///home/alimuldal/src/lepiled/mechanical_design/cad/mech_base_ring.step) — inverted (`Z = 0` mating face on bed, `0.000 mm²` overhang).
  - [mech_lid_bot.step](file:///home/alimuldal/src/lepiled/mechanical_design/cad/mech_lid_bot.step) — upright (`Z = 0` flat bottom face on bed, `0.000 mm²` overhang).
  - [mech_cap_bot.step](file:///home/alimuldal/src/lepiled/mechanical_design/cad/mech_cap_bot.step) — upright (flat bottom face on bed, `0.178 mm²` overhang, seamless outer cylinder).
  - [mech_cap_top.step](file:///home/alimuldal/src/lepiled/mechanical_design/cad/mech_cap_top.step) — inverted (flat `Ø116 mm` drip-brim face on bed, `0.000 mm²` overhang).
  - [mech_plug_top.step](file:///home/alimuldal/src/lepiled/mechanical_design/cad/mech_plug_top.step) — inverted (flat cap face on bed, `0.000 mm²` overhang).
  - [mech_plug_bot.step](file:///home/alimuldal/src/lepiled/mechanical_design/cad/mech_plug_bot.step) — upright (flat bottom face on bed, `0.000 mm²` overhang).
  - [mech_drill_jig.step](file:///home/alimuldal/src/lepiled/mechanical_design/cad/mech_drill_jig.step) — flat back plate on bed (`0.000 mm²` overhang).

## 2. Step-by-Step Build Sequence

1. **Drill & Tap the Single Stock Aluminum Tube (`MECH-HS-CORE`, `40 × 40 × 3.0 mm × 250 mm`, Zero Sawing/Painting):**
   - Slip the 3D-printed snap-on drilling jig ([mech_drill_jig.step](file:///home/alimuldal/src/lepiled/mechanical_design/cad/mech_drill_jig.step)) over the bottom end of the `250 mm` tube (end-stop flush against the tube end) and drill `4× Ø2.5 mm` pilot holes on each of the 4 faces (`16` holes total: Vis star screws at `47.5 / 66.5 mm`, UV star screws at `83.5 / 102.5 mm` from the bottom end). Tap all `16` holes **`M3 × 0.5`** (`3 mm` wall gives `6` full threads).
   - Drill `1× Ø8.0 mm` hanging hole straight across the protruding top (`18 mm` down from the top end, centered at `Y = 0`).
   - Drill `2× Ø2.5 mm` holes and tap **`M3 × 0.5`** on opposite `±X` faces at `157.0 mm` from the bottom end (`Z = 230.0 mm`, for the `2× M3 × 12 mm` `MECH-CAP-TOP` locking screws tucked neatly beneath the drip-brim).
   - Drill `4× Ø3.4 mm` clearance holes with a light `90°` flush countersink on the `±X` faces at `6.0 mm` from the bottom end, `Y = ±9.0 mm` (for the `4× M3 × 8 mm` flush CSK screws pinning `MECH-PLUG-BOT`).
   - Deburr all edges and clean the 4 star mounting spots with IPA. (No spray paint needed!)
2. **Pre-Wire All `8×` `20 mm` Copper DTP Stars on the Bench (CRITICAL: BEFORE Mounting to the Core!):**
   - Lay all `8×` copper stars on a silicone mat or piece of wood—**never solder wires after bolting stars onto the aluminum core**, or the `250 mm` aluminum tube will sink heat out of the soldering iron tip.
   - Pre-tin the `+` and `-` pads on each star, then solder `22 AWG` jumper wires to form two 4-in-series harnesses:
     - **Ch1 UV String (`4× SST-10-UV`):** `HARN-01` 2-pin JST-XH pigtail (`Pin 1 Red -> D1+`, `D1- -> D2+`, `D2- -> D3+`, `D3- -> D4+`, `D4- -> Pin 2 Black`).
     - **Ch2 Vis String (`2× RB + 1× GR + 1× CW`):** Second `HARN-01` 2-pin JST-XH pigtail (`Pin 1 Red -> D5+`, `D5- -> D6+`, `D6- -> D7+`, `D7- -> D8+`, `D8- -> Pin 2 Black`).
   - Leave `~100 mm` tail length on the JST-XH pigtails to drop cleanly through the bottom core wire slots into `J2` and `J3`. Verify every star lights cleanly with a multimeter diode check before mounting.
3. **Bolt Stars to `MECH-HS-CORE` (`M3` + Mandatory Nylon Washers):**
   - Apply a thin, even layer of PC thermal paste (`MECH-TIM-1`, e.g. Arctic MX-4) under each `20 mm` Copper DTP star.
   - Bolt all 4 UV stars (top row, `93 mm` from core bottom) and all 4 Visible stars (bottom row, `57 mm` from core bottom) onto the 4 faces using **`16× M3 × 6–8 mm` screws WITH `16× M3` nylon insulating washers (`MECH-WASH-NYLON`) under every screw head**. Verify `> 10 MΩ` isolation between `+`/`-` leads and the aluminum core with a multimeter.
4. **Hand-Solder `J1..J4` on `driver_pcb` & Mount `SW1` on `MECH-LID-BOT`:**
   - Hand-solder the 4 through-hole connectors (`J1` `USB4085-GF-A`, `J2/J3` `B2B-XH-A`, `J4` `B3B-XH-A`) onto the JLCPCB-assembled `driver_pcb` using [assembly_map.pdf](file:///home/alimuldal/src/lepiled/pcb_design/driver_pcb/renders/assembly_map.pdf).
   - Solder the pre-crimped `22 AWG` 3-pin JST-XH pigtail (`HARN-02`, leave `~60 mm` wire length) directly to the gold solder lugs of `SW1` (`C&K 7211SYZBE`, `DPDT On-On-On`), bending the insulated wires sideways clear of `driver_pcb`:

| `C&K 7211SYZBE` Lug(s) | Wire Destination (`J4`) | Pos 1 (`OFF`) | Pos 2 (`4-UV`) | Pos 3 (`8-ALL`) |
|---|---|---|---|---|
| **Lugs `2 + 5` (tied together)** | **`J4.2` (`GND`)** | Common `GND` | Common `GND` | Common `GND` |
| **Lug `6`** | **`J4.1` (`SW_UV_IN`)** | Closed to `GND` (`U1` OFF) | Open (`U1` ON) | Open (`U1` ON) |
| **Lug `3`** | **`J4.3` (`SW_VIS_IN`)** | Closed to `GND` (`U2` OFF) | Closed to `GND` (`U2` OFF) | Open (`U2` ON) |
| **Lugs `1` and `4`** | **No Connect (leave bare)** | — | — | — |

   - Verify continuity in all three switch positions, seat `SW1` into the anti-rotation pocket on top of `MECH-LID-BOT` (`X = 0, Y = +16.5 mm`) with the toggle pointing straight **downward**, and tighten `SW1_BOOT` (`C&K 759D02000`) from underneath.

## 3. Staged Bench Bring-Up (Standard USB-C PD Laptop Charger)

1. **Unplugged Shorts Check:** Confirm `VIN_20V` to `GND` `> 5 kΩ`, `VBUS` to `GND` `> 10 kΩ`, and `J2`/`J3` open.
2. **USB-C PD `20 V` Negotiation (`J2`/`J3` Unplugged, `SW1` = `OFF`):** Plug a `45–100 W` USB-C PD laptop charger or `20 V` PD power bank into `J1`. Confirm green LED **`D12`** shows **`4 s` breathing** (`20 V VOUT ON`; steady solid = source did not offer `20 V / 1 A`), `V(VIN_20V) = 20.0 V ± 1 V`, and `V(V_REF) = 2.500 V ± 0.01 V`.
3. **5 V UVLO Rejection Check:** Plug in a legacy `5 V` USB charger; confirm `V(U1_CTRL) < 50 mV` and `V(U2_CTRL) < 50 mV`.
4. **LED Load Test (Power Off Before Mating `J2`/`J3`; UV400 Glasses On!):** Mate `J2`, `J3`, and `J4`, reconnect the `20 V` PD charger, and check:
   - **`OFF`:** `I_in < 15 mA`, all 8 LEDs dark.
   - **`4-UV`:** `D1..D4` lit, `I_in ≈ 0.25 A @ 20 V` (`~5.0 W`), `V(R3) = 100 mV ± 6 mV`.
   - **`8-ALL`:** All 8 LEDs lit, `I_in ≈ 0.45–0.46 A @ 20 V` (`~9.1 W`), `V(R3) ≈ 100 mV`, `V(R4) ≈ 100 mV`.

## 4. Final Mechanical Assembly & Weatherproofing

1. **Bottom Core Plug & Bulkhead:** Drop `2×` `M3` hex nuts into the top pockets of `MECH-PLUG-BOT`, slide it flush into the bottom end of `MECH-HS-CORE`, and pin it with `4× M3 × 8 mm` flush CSK screws on the `±X` walls. Route the `J2`/`J3` JST-XH pigtails down the outside corners of the core through the `MECH-CAP-BOT` wire slots, seat the core in the square socket, and bolt it down from inside the bottom cavity with `2× M3 × 16 mm` CSK screws.
2. **UVT PMMA Shroud, Top Cap & Rain Plug:**
   - Seat `MECH-GASKET-1` (`68 × 3.5 mm`) in `MECH-CAP-BOT`, lower the UVT PMMA acrylic tube (`MECH-TUBE-1`) onto it, seat `MECH-GASKET-2` in `MECH-CAP-TOP`, and slide `MECH-CAP-TOP` down over the protruding aluminum core until both O-rings compress snugly.
   - Thread `2× M3 × 12 mm` SHCS screws through the `±X` locking bores tucked beneath `MECH-CAP-TOP`'s `Ø116 mm` drip-brim into the tapped holes in `MECH-HS-CORE`. Run a neat bead of clear silicone sealant into the top square chamfer groove where the aluminum tube exits `MECH-CAP-TOP`.
   - Smear a thin ring of silicone sealant around the skirt of `MECH-PLUG-TOP` and press it firmly into the top end of the hollow `40 × 40` aluminum tube to weatherproof the bore. Clip any carabiner or tie paracord straight through the unobstructed `Ø8.0 mm` hanging hole below the cap.
3. **Vertical `driver_pcb`, Bottom Lid, Protective Base Ring & Bottom `20 mm` USB-C Grommet:**
   - Drop `4×` `M3` hex nuts into the `4×` side-entry captive nut slots around the lower flange of `MECH-CAP-BOT`.
   - Slide `driver_pcb` straight down into the two vertical card-guide rails on `MECH-LID-BOT` (`J1` USB-C pointing straight downward over the `Ø20.2 mm` grommet bore, `J2/J3` at the top, component side facing `+Y` toward `SW1`) until the bottom edge seats firmly on the rail ledges.
   - Plug `J2`, `J3`, and `J4` into `driver_pcb`, slide `MECH-LID-BOT` straight up into `MECH-CAP-BOT` (the `42.75°` upper cavity cone captures the top corners of `driver_pcb` to absorb upward USB-C insertion force), seat `MECH-BASE-RING` flush beneath `MECH-LID-BOT`, and clamp both together with `4× M3 × 16 mm` SHCS screws through the base-ring counterbores.
   - Slit the `20 mm` rubber membrane grommet (`MECH-GROMMET-1`) radially from edge to center, plug your USB-C PD cable straight upward into `J1`, wrap the grommet snugly around the cable jacket behind the plug, and snap it into the `Ø20.2 × 2.5 mm` bore in `MECH-LID-BOT`. *(When hanging, the cable exits straight down with zero lamp tilt; to stand the lamp flat while powered, use a low-profile 90° USB-C cable routed out through one of `MECH-BASE-RING`'s four `22 × 7.5 mm` bottom cutouts.)*
