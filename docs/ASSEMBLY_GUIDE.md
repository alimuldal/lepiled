# LepiLED DIY Maxi Switch — Assembly, Commissioning & Bring-Up Guide (Rev 4.1)

## 1. Pre-Assembly Safety & Ordering Checklist

- **UV-A Eye Safety:** Wear EN166 / ANSI Z87+ UV400 safety glasses whenever `D1..D4` (`365 nm` Luminus `SST-10-UV`) are energized. Never stare directly into the glass tube.
- **No Live Hot-Plugging of LED Headers:** Always disconnect USB-C power before mating or unmating `J2` (UV) or `J3` (Visible). Although `C4/R22` and `C5/R23` (`100 nF + 6.8 Ω`) limit accidental live-mate surges (`<= 0.53 A` UV / `<= 0.92 A` Vis), live connection of LED loads on hysteretic buck drivers is poor practice and should be avoided.
- **PCB Ordering:**
  - **Board 1 (`driver_pcb`):** Upload [driver_pcb_gerbers.zip](file:///home/alimuldal/src/lepiled/pcb_design/gerbers/driver_pcb/driver_pcb_gerbers.zip) (`36 × 46 mm`, 2-layer `1.6 mm` FR4, 1 oz Cu, **ENIG** finish, Green LPI / White silk) to JLCPCB or PCBWay. For SMT assembly, upload [driver_pcb_cpl.csv](file:///home/alimuldal/src/lepiled/pcb_design/driver_pcb_cpl.csv) (**57 SMD parts only**; `J1..J4` THT and `H1..H4` NPTH excluded) and [driver_pcb_bom_pcba.csv](file:///home/alimuldal/src/lepiled/pcb_design/driver_pcb_bom_pcba.csv) (61 populated parts including `J1..J4` LCSC part numbers). Keep [assembly_map.pdf](file:///home/alimuldal/src/lepiled/pcb_design/driver_pcb/renders/assembly_map.pdf) handy during bench inspection and hand-soldering of `J1..J4`.
  - **Board 2 (`led_mcpcb`):** Upload [led_mcpcb_gerbers.zip](file:///home/alimuldal/src/lepiled/pcb_design/gerbers/led_mcpcb/led_mcpcb_gerbers.zip) (`20 × 80 mm`, **1-layer `1.6 mm` Aluminum MCPCB**, `1.0 W/(m·K)` dielectric, 1 oz Cu, **ENIG** finish, White / Black silk). Note the 4 strips use mixed visible LEDs per [led_mcpcb_bom.csv](file:///home/alimuldal/src/lepiled/pcb_design/led_mcpcb_bom.csv): `2×` Royal Blue (`XPEBRY-L1-0000-00S02`), `1×` Green (`XPEBGR-L1-0000-00K01`), and `1×` Cool White (`XPEBWT-L1-0000-00H51`), plus `4×` UV-A (`SST-10-UV-A130-G365-00`).
- **3D Printing Enclosure Parts (Support-Free):** Print all three parts in **PETG or ASA** FDM (`0.2 mm` layers, `0` supports required) or PA12 SLS (`*_sls.step`):
  - [mech_lid_bot.step](file:///home/alimuldal/src/lepiled/mechanical_design/cad/mech_lid_bot.step) — flat bottom face on bed (`0.00 mm²` `>46°` overhang).
  - [mech_cap_bot.step](file:///home/alimuldal/src/lepiled/mechanical_design/cad/mech_cap_bot.step) — flat bottom face on bed (`0.24 mm²` `>46°` overhang).
  - [mech_cap_top.step](file:///home/alimuldal/src/lepiled/mechanical_design/cad/mech_cap_top.step) — inverted, flat top face on bed (`0.01 mm²` `>46°` overhang).
- **Zero-CNC Metalwork:** All metal parts use off-the-shelf UK bar/disc stock (`MECH-HS-CORE` `40 × 40 × 3 mm` box cut to `165.0 mm`, `MECH-ADAPT-TOP` stock `Ø76.2 × 3.0 mm` Al disc, `MECH-ANCHOR-TOP/BOT` stock `32 × 32 mm` Al square bar cut to `14.0 mm` / `12.0 mm`) requiring only simple drill-press and hand-tap operations.

## 2. Step-by-Step Build Sequence

1. **Reflow `led_mcpcb` Strips (`4×`):**
   - Apply solder paste using the segmented thermal-pad stencil apertures (`61.2%` on `D_UV`, `64.0%` on `D_VIS`).
   - **CRITICAL POLARITY CHECK:** `D_UV` (`SST-10-UV`) has **`BTM NOTCH = CATHODE (K)`**; `D_VIS` (Cree `XP-E2`) has **`BTM NOTCH = ANODE (A)`** — opposite bottom-pad notches (`180°` relative orientation in [led_mcpcb_cpl.csv](file:///home/alimuldal/src/lepiled/pcb_design/led_mcpcb_cpl.csv)). Verify every LED with a multimeter diode test (`~3.3–3.6 V` UV, `~2.6–3.0 V` Vis) after reflow.
2. **Drill, Tap & Coat Metal Parts (Zero CNC Milling):**
   - Cut `MECH-HS-CORE` (`40 × 40 × 3 mm` Al 6063) to `165.0 mm` with square, flat top end face. Drill tight **`Ø4.2 mm` round cross-pin bores** (`82°`/`90°` flush countersunk on outside for `M4 × 40` DIN 7991 CSK) for both top and bottom anchors — do NOT slot the top pin bores. Position the top anchor pin centerlines so the top face of `MECH-ANCHOR-TOP` sits **`0.50 mm` recessed below** the top end face of `MECH-HS-CORE` (this guarantees eye-bolt torque preloads the core cleanly against `MECH-ADAPT-TOP`).
   - Mask the 4 LED mounting stripes and the top end face of `MECH-HS-CORE`, then spray matte-black high-emissivity paint (`MECH-COAT-1`).
   - Drill and tap `MECH-HS-EXT-TOP` (`Fischer SK 578/50 SA`): `Ø6.5 mm` center through-bore + `4× M3` tapped holes at `R = 8.5 mm`.
   - Drill `MECH-ADAPT-TOP` (stock `Ø76.2 × 3.0 mm` Al disc): `Ø6.5 mm` center hole, `4× M3` CSK at `R = 8.5 mm` (flush on bottom core-mating face), and `4× Ø3.4 mm` clearance holes at `R = 34.0 mm`.
   - Drill/tap `MECH-ANCHOR-TOP` (`32 × 32 × 14.0 mm` stock bar): `M6 × 1.0` center through-tap + `2× Ø4.2 mm` cross-pin bores (`Y = ±9.0 mm`, `Z = 7.0 mm` from anchor bottom). Drill/tap `MECH-ANCHOR-BOT` (`32 × 32 × 12.0 mm` stock bar): `2× M4` vertical tapped holes (`X = ±9.0 mm`) + `2× Ø4.2 mm` cross-pin bores (`Y = ±9.0 mm`).
3. **Mount MCPCBs & Wire Series Strings:**
   - Apply thin `Arctic MX-4` (`MECH-TIM-1`) under each strip and bolt all 4 strips to `MECH-HS-CORE` with `8× M3 × 8 mm` DIN 912 SHCS (`MECH-FAST-1`).
   - Solder `22 AWG` silicone wire to the `Y = -24.0 mm` pads (**exit wires sideways/outward around the `M3` screw keepout**, never straight down over `MH2`), daisy-chaining the 4 UV pads (`UV+ -> D1 -> D2 -> D3 -> D4 -> UV-`) and 4 Vis pads (`VIS+ -> D5 -> D6 -> D7 -> D8 -> VIS-`).
   - Route the two pairs through the bottom core wire slots and bulkhead pass-throughs, crimp `JST SXH-001T-P0.6` contacts into `2× JST XHP-2` plugs (`HARN-01`), and verify `Pin 1 = +` (`UV+`/`VIS+`), `Pin 2 = -` (`UV-`/`VIS-`) against the `B.SilkS` labels on `driver_pcb`.
4. **Install Heat-Set Inserts & Wire `SW1` (`C&K 7211SYZBE` DPDT On-On-On):**
   - Press `4× M2.5 × 4.0 mm` brass heat-set inserts (`MECH-FAST-2`) into the `4×` integral PCB bosses on `MECH-LID-BOT`, plus `8× M3 × 5.7 mm` inserts (`MECH-FAST-3`) into `MECH-CAP-BOT` (`4×` at `R = 40.2 mm`) and `MECH-CAP-TOP` (`4×` at `R = 34.0 mm`).
   - Solder a 3-wire `22 AWG` harness (`HARN-02`, `JST XHP-3` plug) to the gold solder lugs of `SW1` (`C&K 7211SYZBE`, `DPDT On-On-On`) as shown below (numbering per C&K 7000-series datasheet, looking at the lug side with keyway/flat oriented consistently):

| `C&K 7211SYZBE` Lug(s) | Wire Destination (`J4`) | Pos 1 (`OFF`) | Pos 2 (`4-UV`) | Pos 3 (`8-ALL`) |
|---|---|---|---|---|
| **Lugs `2 + 5` (tied together)** | **`J4.2` (`GND`)** | Common `GND` | Common `GND` | Common `GND` |
| **Lug `6`** | **`J4.1` (`SW_UV_IN`)** | Closed to `GND` (`U1` OFF) | Open (`U1` ON) | Open (`U1` ON) |
| **Lug `3`** | **`J4.3` (`SW_VIS_IN`)** | Closed to `GND` (`U2` OFF) | Closed to `GND` (`U2` OFF) | Open (`U2` ON) |
| **Lugs `1` and `4`** | **No Connect (leave bare)** | — | — | — |

   - Verify continuity across the `JST XHP-3` plug in all three toggle positions with a multimeter before mounting `SW1` + `SW1_BOOT` (`759D02000`) through the `+X` wall of `MECH-CAP-BOT`.
5. **Conformal Coating & Driver PCB Mounting (`MECH-LID-BOT`):**
   - After hand-soldering `J1..J4` and completing the bench bring-up below (Section 3), mask the interiors of `J1`, `J2`, `J3`, and `J4` with masking tape or mating dummy plugs, then apply a thin coat of **acrylic conformal coating** (e.g. MG Chemicals `419D`, `MECH-MISC-1`) over both sides of `driver_pcb` to protect the `0.40 mm`-pitch `AP33771C` and `AL8860` circuitry against light field dew. Allow full cure before closing the enclosure.
   - Mount `driver_pcb` onto the `4×` `11.5 mm` bosses of `MECH-LID-BOT` using **`4×` Nylon `M2.5 × 6 mm` pan-head screws** (`MECH-FAST-2`) through the isolated unplated `H1..H4` holes (`Ø2.7 mm`).

## 3. Staged Bench Bring-Up (Standard USB-C PD Laptop Charger)

Perform all electrical checks on the bench **before** applying conformal coating or sealing the enclosure:

1. **Unplugged Shorts Check:** Measure resistance between `VIN_20V` and `GND` (`> 5 kΩ`), `VBUS` and `GND` (`> 10 kΩ`), and across `J2`/`J3` (open).
2. **USB-C PD 20 V Negotiation (No LEDs Connected, `SW1` = `OFF`):** Plug a standard `45–100 W` USB-C PD laptop charger or `20 V` PD power bank into `J1`.
   - Confirm green status LED **`D12`** shows **`4 s` breathing** (`AP33771C` `VOUT = ON` at negotiated `20 V`; a **steady solid** `D12` indicates a PDO mismatch where the source did not offer `20 V / >= 1.0 A`).
   - Confirm `V(VBUS) = 20.0 V ± 1 V`, `V(VIN_20V) = 20.0 V ± 1 V`, `V(V_REF) = 2.500 V ± 0.01 V`, and `V(UVLO_FAULT) < 50 mV`.
3. **5 V UVLO Rejection Check:** Unplug the `20 V` charger and plug in a legacy `5 V`-only USB charger. Confirm `V(UVLO_FAULT) ≈ 2.50 V`, `V(U1_CTRL) < 50 mV`, `V(U2_CTRL) < 50 mV`, and both LED channels remain completely disabled.
4. **LED Load Test (Power Off Before Mating `J2`/`J3`; UV400 Glasses On!):**
   - Disconnect USB-C power, mate `J2` (UV), `J3` (Vis), and `J4` (`SW1`), then plug in the `20 V` PD charger and test all three `SW1` positions:
   - **`OFF` (Pos 1):** `I_in < 15 mA`, all 8 LEDs dark.
   - **`4-UV` (Pos 2):** `D1..D4` lit cleanly, `I_in ≈ 0.25 A @ 20 V` (`~5.0 W`), `V(R3) = 100 mV ± 6 mV` (`I_UV ≈ 333 mA`).
   - **`8-ALL` (Pos 3):** All 8 LEDs lit, `I_in ≈ 0.45–0.46 A @ 20 V` (`~9.1 W`), `V(R3) ≈ 100 mV`, `V(R4) ≈ 100 mV`.

## 4. Final Enclosure Assembly & Dew-Sealing

1. **Core & Bottom Bulkhead:** Pin `MECH-ANCHOR-BOT` and `MECH-ANCHOR-TOP` (`0.50 mm` top recess) into `MECH-HS-CORE` with `4× M4 × 40 mm` flush CSK bolts (`MECH-FAST-5`). Bolt the core down to `MECH-CAP-BOT` from inside the open bottom cavity using `2× M4 × 16 mm` CSK bolts with `M4` nylon CSK insulating washers (`MECH-MISC-1`).
2. **Glass Tube, Top Cap & Top Heatsink Preload:**
   - Seat `MECH-GASKET-1` (`68 × 3.5 mm` VMQ70) in `MECH-CAP-BOT`, lower `MECH-TUBE-1` borosilicate tube into place, seat `MECH-GASKET-2` in `MECH-CAP-TOP`, and place `4× 0.5 mm` SS shim washers (`MECH-FAST-3W`) on top of `MECH-CAP-TOP`.
   - Apply thin `Arctic MX-4` (`MECH-TIM-1`) to the top end face of `MECH-HS-CORE` and to both sides of `MECH-ADAPT-TOP`. Bolt `MECH-ADAPT-TOP` to `MECH-HS-EXT-TOP` (`4× M3 × 8 mm` CSK, `MECH-FAST-4`), place the assembly onto `MECH-CAP-TOP`, and fasten `4× M3 × 8 mm` SHCS (`MECH-FAST-3`) through `MECH-ADAPT-TOP` into `MECH-CAP-TOP`.
   - Thread `MECH-EYE-1` (`M6 × 75 mm` stainless eye bolt + washer) down through `MECH-HS-EXT-TOP` and `MECH-ADAPT-TOP` into the recessed `MECH-ANCHOR-TOP` and torque snug. Because `MECH-ANCHOR-TOP` is recessed `0.50 mm` below the core end face and pinned through tight `Ø4.2 mm` round bores, eye-bolt tension pulls `MECH-HS-CORE` firmly into full contact with `MECH-ADAPT-TOP`.
3. **Bottom Lid & `20 mm` Rubber Membrane Grommet:**
   - Seat `MECH-GASKET-3` (`66 × 2.0 mm` VMQ70) in the bottom groove of `MECH-CAP-BOT`.
   - Plug in `J2`, `J3`, and `J4` on the conformally coated `driver_pcb`, align `J1` with the `-Y` USB-C tunnel, and fasten `MECH-LID-BOT` flush to `MECH-CAP-BOT` with `4× M3 × 8 mm` DIN 7991 CSK bolts (`MECH-FAST-3`).
   - Make a single clean radial slit from the outer edge to the center pinhole of the off-the-shelf `20 mm` rubber membrane grommet (`MECH-GROMMET-1`, e.g. Eaton `KT-M20` / RS `06664634`). Plug your standard USB-C PD cable into `J1`, wrap the slit grommet snugly around the cable jacket behind the plug overmold, and press the grommet groove into the `Ø20.2 × 2.5 mm` flat flange of `MECH-CAP-BOT`.
