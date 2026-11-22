# Interface Contract — Electronics ↔ PCB & Mechanical / Thermal

**Canonical Registry:** [COMPONENT_IDS.csv](COMPONENT_IDS.csv) (`72` RefDes: `54` PCBA = `41` JLCPCB SMD [20 Basic + 2 Extended] + `11` DIY [`4` THT `J1..J4` + `7` 2-pad SMDs] + `2` DNP `D13/D14`; `4` Isolated `M3` NPTH `H1..H4`; `4` Bare HASL Test Pads `TP1..TP4`; `10` Off-Board = `8×` Convoy `20 mm` Cu DTP LED stars + `SW1` + `SW1_BOOT`)
**Datasheet Source of Truth:** [datasheets_summary.json](../datasheets/datasheets_summary.json)
**Simulation Verification:** [sim_summary.json](sim/outputs/sim_summary.json)
**CAD Parameter SSOT:** [cad_params.json](../mechanical_design/cad/cad_params.json)

---

## 1. Electronics ↔ PCB Design & Manufacturing Contract

### 1.1 Physical Board Envelope & `M3` Mounting Holes
- **Single Custom PCB (`driver_pcb`):** `36.0 mm × 46.0 mm`, 2-layer `1.6 mm` FR4, `2.0 mm` corner radii, 1 oz Cu, Lead-Free HASL finish, Green LPI (`min_solder_mask_bridge >= 0.10 mm`) / White silk.
  - SMD power/signal envelope: `<= 4.5 mm` (`L1`/`L2` `Bourns SRN6045-680M` = `4.5 mm` max; `J1` `USB4085-GF-A` = `3.46 mm`).
  - Through-hole wire headers `J2..J4` (`JST B2B-XH-A` / `B3B-XH-A`, `1.00 mm` drills): `7.0 mm` unmated (`9.8 mm` mated). `HARN-01` pigtails are kept strictly inside the dark top bay and spliced to `HARN-03` `24 AWG` UV-stable silicone risers.
  - **Mounting Holes (`H1..H4`):** `4× M3` unplated isolated NPTH (`Ø3.2 mm` drill, `r = 3.10 mm` [`Ø6.20 mm`] `F.Cu` + `B.Cu` copper keepouts verified on exported RS-274X Gerbers: `F_Cu >= 3.609 mm`, `B_Cu >= 3.085 mm`) at `(±14.0, ±19.0) mm`, mounting vertically (`F.Cu` facing `+X`) onto `MECH-TOP-BASE`'s `4×` captive DIN 934 `M3` hex nuts via `4×` `M3 × 8 mm` pan-head screw + `M3` steel flat washer + `3×` stacked `Ø7.0 × 0.8 mm` DIN 125 nylon insulating washers.
  - **Bench Test Pads (`TP1..TP4`) & `D12`:** Four bare `1.0 mm` HASL `F.Cu` pads (`VIN_20V`, `V_REF`, `UVLO_OK`, `GND`) on outward-facing `+X` `F.Cu` alongside red `20 V` PD LED `D12` (also visible through `MECH-CAP-TOP`'s `0.90 mm` outer-taper-contoured translucent internal dimple).
- **Off-Board LEDs (`8×` Convoy `20 mm` Cu DTP Stars):** `4×` UV-A (`Luminus SST-10-UV`, `Z = 94.0 mm`) and `4×` Visible (`ams OSRAM CSLNM1`, `Z = 60.0 mm`, `34.0 mm` vertical pitch; Royal Blue `KB CSLNM1.14` on opposite Faces 1 `+X` & 3 `-X`, Pure Green `KP CSLNM1.F1` on Face 2 `+Y`, Cool White `KW CSLNM1.TG` on Face 4 `-Y`) bonded onto abraded bare-aluminum landing pads on the bare mill-finish `MECH-HS-CORE` with electrically insulating 2-part thermally conductive epoxy (`MECH-TIM-1`, zero core holes in the optical zone).

### 1.2 Copper, Stackup & Layout Design Rules (`driver_pcb`)
- **Zero Unplugged Via-in-Pad:** Every via clears every SMD pad by `>= 0.25 mm` (`51` vias / `130` SMD pads, `0` violations). `U3` (`WCH CH224A` `ESSOP-10`) `2.10 × 3.30 mm` EPAD uses segmented paste and perimeter `0.30/0.60 mm` `GND` vias.
- **Unbroken `B.Cu` Ground Plane Under Power Stage:** Continuous solid `GND` plane beneath `U1`, `U2`, `D9`, `D10`, `L1`, `L2`, `R3`, `R4`, `C2`, `C3`, `C8`, `C9` (`0` non-GND segments inside `Y = [4.3, 16.5] mm`).
- **Trace Widths & High-$di/dt$ Loops (`20 V` Bus, `0.453 A` nom / `0.573 A` max):**
  - `VBUS`, `VIN_20V`: `>= 0.80 mm` (`1.00 mm` trunk). Zero-stub fly-by routing from `F1` (`1206`) directly across `D11` (`SMBJ22A`) into `R7` (`2512`) / `C10` (`1206`) / `C11`.
  - Buck hot loops (`C2/C8 -> R3 -> UV_POS`, `D9 -> VIN_20V`, `SW1_NODE -> L1` and Ch2 mirror): `>= 0.60 mm`, `< 10 mm` perimeter on `F.Cu`, with Kelvin `VIN` and `SET` taps at `R3`/`R4`.
- **Footprint & PCBA Accuracy:**
  - `J1` (`GCT USB4085-GF-A`): `Ø0.40 mm` signal drills (`0.65 × 0.90 mm` oval pads), full-connection GND pins tied to `SH1/SH2`, `Y_mouth = -26.18 mm` (board coords).
  - `D13`/`D14` (`D_SOD-323_DNP`): paste-free DNP footprints (`0` apertures in `F_Paste.gbr`, `SetDNP(True)`).
  - `driver_pcb_bom_pcba_hybrid.csv` and `driver_pcb_cpl_hybrid.csv` contain `41` JLCPCB SMDs (`20` Basic + `2` Extended); `driver_pcb_diy_hand_solder.csv` contains `11` DIY Farnell UK parts (`J1..J4` THT + `F1`, `D11`, `L1/L2`, `R3/R4`, `R7`) + `D13/D14` DNP; `H1..H4` and `TP1..TP4` are excluded from PCBA.

---

## 2. Electronics ↔ Mechanical & Thermal Contract

### 2.1 Thermal Dissipation Budget (SSOT-Coupled to `sim_summary.json` & `cad_params.json`)
Nominal drive current = `333 mA` (`R3 = R4 = 0.30 Ω ±1%`), supplied from `20.0 V` USB-C PD (`I_in = 0.453 A` / `9.06 W` nominal; `0.573 A` worst-case corner; `94.1%` system efficiency).

| Subsystem | `8-ALL` Electrical (W) | `8-ALL` Nom Heat (`40%` UV WPE) | `8-ALL` Worst-Case (`DS-RealWPE`) | `4-UV` Nom Heat | Thermal Limit |
|---|---|---|---|---|---|
| **Ch1 UV Array (`4× SST-10-UV`, `D1..D4`)** | `4.736 W` | `2.842 W` | `3.698 W` | `2.842 W` | $T_{j,\max} = 100^\circ\text{C}$ ($R_{\theta Js}=1.4^\circ\text{C/W}$) |
| **Ch2 Visible Array (`4× OSRAM CSLNM1`, `D5..D8`)** | `3.784 W` | `2.270 W` | `3.279 W` | `0.000 W` | $T_{j,\max} = 150^\circ\text{C}$ ($R_{\theta Js}=4.1\text{–}4.9^\circ\text{C/W}$) |
| **Spectral Optical Re-Absorption (`15.3%` UV / `3.5%` Vis)** | — | `0.343 W` | `0.336 W` | `0.290 W` | `11.3%` UV / `1.3%` Vis in PMMA wall; remainder on core/sockets |
| **`U1`/`U2` (`AL8860WT-7`) + Buck Passives** | `0.352 W` | `0.352 W` | `0.583 W` | `0.165 W` | $T_{j,\max} = 125^\circ\text{C}$ derated |
| **`U3`/`U4`/`U5`/`F1`/`D12`/Quiescent Overhead** | `0.156 W` | `0.156 W` | `0.259 W` | `0.156 W` | `U4` (`LM393DR2G`) commercial `0..+70 °C` rating |
| **Driver PCB Total Loss (`sim_summary.json`)** | `0.508 W` | `0.508 W` | `0.842 W` | `0.321 W` | Bare mill Al (`K_eff=9.3`) + epoxied `16 K/W` bridge: `T_pcb / T_j,U4 = 48.9 / 47.5 °C` (`22 °C` nom), `66.0 / 65.3 °C` (`30 °C` WC); `66.3 / 67.0 °C <= 70 °C` (`35 °C` WC w/ optional upper-tube matte paint) |

### 2.2 Mechanical Interface Datums (Synced with `mechanical_design/cad/cad_params.json`)
- **Vertical `+X` Top-Bay `driver_pcb` & Captive Thermal Bridge:** `36 × 46 × 1.6 mm` `driver_pcb` mounts vertically on `MECH-TOP-BASE` (`B.Cu` at `X = 20.9 mm`, `F.Cu` facing `+X` at `X = 22.5 mm`, `Z = 174.5..220.5 mm`, `5.9 mm` nom / `5.7 mm` WC gap to the aluminum core) via `4×` captive DIN 934 `M3` hex nuts inside `MECH-CAP-TOP`'s straight `Ø85.0 mm` bore (`9.78 mm` wire-bend space behind `J2`/`J3`). A solid `1.5 mm` plastic barrier shields `J1`/`J4` TH pins (`2.05 mm` air clearance), while a closed-perimeter `15.6 × 15.6 mm` captive chute (`Z = 199.0..214.4 mm`) behind the pin-free `U1/U2` copper zone clamps a doubly insulated `1.0 mm` silicone-pad + `15 × 15 × 0.5 mm` brass-shim thermal bridge against the aluminum core. `J1` sits at deck level (`Z_mouth = 171.32 mm`, `X_ctr = +24.38 mm`, wide slot along `±Y`) with `26.32 mm` headroom to the bay floor (`Z = 145.0 mm`), mating a standard left/right `90°` USB-C plug (`<= 18.0 mm` protrusion) curving horizontally to `+Y`.
- **Top Side-Port Ring (`MECH-TOP-BASE`) & Rain Bell (`MECH-CAP-TOP`):** `MECH-TOP-BASE` (`Z = 120.0..224.8 mm`) carries `SW1` recessed `5.5 mm` in a `32 mm` outward-draining `-X` cove (`X = -41.5 mm, Z = 154.2 mm`, round `Ø6.50 mm` bore, `8.33 mm` lug-to-core clearance, `3.4–5.3 mm` inside the `-X` visor), the compressing `+Y` `MECH-CABLE-CLAMP` (`1.2 mm` standoff, X-slotted `M3 × 12` pan-head bolts into `7.0 mm` blind `M3 × 5.0` inserts, `10.2 × Ø9.0 mm` grommet bore at `77.5%` silicone fill, internal zip-tie post), and the `-Y` downward-draining breather vent (`Ø9.5 × 0.8 mm` flat bay-floor pocket at `Y = -33.8 mm` over a `35°` bore), all under `MECH-CAP-TOP`'s `Ø118 mm` rain eaves (with monolithic `1.4 mm` drip kerf, flexible `+Y` C-clip, `-X` visor + `0/1/2` ribs, and `0.90 mm` outer-taper-contoured `D12` dimple). `MECH-CAP-TOP` seals axially on `MECH-GASKET-3` (`88 × 2.5 mm` VMQ50 in a `2.00 mm` quantized `Z = 171.0 mm` deck groove), fastens via `4×` diagonal open-slot gusseted flush `M3 × 12` CSK ears (`R = 51.0 mm`), and seals to the aluminum chimney via a top `2.5 × 3.0 mm` rounded-corner neutral-sealant V-groove (zero collar side holes).
- **Open-Chimney Nosecone, Bare Mill-Finish Al Core & Ventilated Finial:** `MECH-CAP-BOT` (`Ø40 → Ø71 × 34.0 mm`, unobstructed `22 × 22 mm` `R3` chimney inlet) locks `MECH-HS-CORE` (`30 × 30 × 2.0 × 300.0 mm` bare mill-finish Al `ε = 0.10`, `Z = 5.0..305.0 mm`, `26 × 26 mm` open chimney) via a single bottom `DIN 912 M4 × 50 mm` A2 stainless SHCS cross-bolt + captive `-X` hex nyloc nut (`Z = 11.5 mm`, `6.5 mm` from core bottom) and seals the core socket from the LED optical chamber via a top `1.8 × 2.5 mm` rounded-square hub sealant V-groove (`Z = 31.5..34.0 mm`). `MECH-PLUG-TOP` (`Z = 281.5..323.0 mm`, `4×` unobstructed exhaust ports under `38 × 38 mm` hood + `2× 6.0 mm` flanged bail spools) pins via the second `DIN 912 M4 × 50 mm` stainless cross-bolt (`Z = 289.0 mm`, `16.0 mm` from core top), which carries a bent steel coat-hanger wire hanging bail. Extruded clear XT PMMA shroud (`Ø60 × 54 × 3.0 × 115 mm`, `Z = 19.5..134.5 mm`, `86.0 mm` exposed window) seals on `60 × 3.5 mm` VMQ50/60 radial O-rings. Total body height: `323.0 mm`.
