# LepiLED DIY Maxi Switch — Master Bill of Materials (Rev 4.9)

The machine-verified master BOM lives in [bom.csv](bom.csv) and is audited 1:1 against [COMPONENT_IDS.csv](../circuit_design/COMPONENT_IDS.csv) (`72` RefDes + every `Datasheet_Ref` verified on disk), [driver_pcb_bom_pcba.csv](../pcb_design/driver_pcb_bom_pcba.csv) (`54` On-PCB parts), the derived 2-Reel Hybrid HASL PCBA files ([driver_pcb_bom_pcba_hybrid.csv](../pcb_design/driver_pcb_bom_pcba_hybrid.csv), [driver_pcb_cpl_hybrid.csv](../pcb_design/driver_pcb_cpl_hybrid.csv), [driver_pcb_diy_hand_solder.csv](../pcb_design/driver_pcb_diy_hand_solder.csv)), and [MECH_PARTS.csv](../mechanical_design/MECH_PARTS.csv) (`20` mechanical IDs) via [verify_bom.py](verify_bom.py).

## 1. Value-Engineered Single-Unit Cost Summary (UK GBP)

| Domain | 1-Off Parts (ex-VAT) | 1-Off Parts (inc 20% VAT) | Amortized Per-Lamp (ex-VAT) |
|---|---:|---:|---:|
| **Electrical (`72` RefDes incl. `8×` Convoy `20 mm` Cu DTP LED stars + Farnell UK DIY basket)** | £33.90 | £40.68 | £32.74 |
| **Harness (pre-crimped JST-XH pigtails, `24 AWG` UV silicone wire, `90°` USB-C PD cable)** | £8.34 | £10.01 | £6.59 |
| **PCB Fab (Lead-Free HASL) + 2-Reel Hybrid Economic PCBA (`driver_pcb`, `41` SMDs, 2-pc min)** | £15.00 | £18.00 | £7.50 |
| **Mechanical (XT PMMA, `Soudal Fix ALL Crystal`, unpainted bare Al core, O-rings, sleeve, vent, unified `M3`)** | £43.36 | £52.03 | £40.25 |
| **Total Parts-Only 1-Off (All Items Purchased New)** | **£100.60** | **£120.72** | **£87.08** (`£104.50` inc-VAT) |
| **Net Out-of-Pocket Parts-Only (Using Owned M3 CSK Screws/Washers, M3 Brass Inserts & Thermal Paste)** | **£87.02** | **£104.42** | — |

### Consolidated UK Delivery Breakdown (Single-Lamp Order — 4 Shipments + Local Click & Collect)

Rev 4.9 consolidates procurement from 8 specialist orders down to **4 shipped baskets + £0 local click & collect**, slashing UK postage by `> 65%`:

| Vendor | Contents | Est. UK Shipping (inc-VAT) |
|---|---|---:|
| **JLCPCB** | 5× bare Lead-Free HASL `driver_pcb` + 2× 2-Reel Hybrid assembled (`41` SMDs: `20` Basic + `U1/U2`, `U3`) | £9–£11 |
| **Convoylight.com** *(1-vendor LEDs)* | `4× Luminus SST-10-UV 365 nm` + `2× Osram KB CSLNM1.14 455 nm` + `1× KP CSLNM1.F1 Green` + `1× KW CSLNM1.TG 6500 K` (all on `20 mm` Cu DTP stars) | £3 |
| **Farnell UK** *(1-basket DIY)* | `SW1` (`C&K 7211SYZBE`), `SW1_BOOT` (`759D02000`), `4` THT (`J1..J4`) + `7` chunky 2-pad SMDs (`F1`, `D11`, `L1/L2`, `R3/R4`, `R7`) | £4.74 *(£3.95 ex-VAT)* |
| **Screwfix UK** *(Click & Collect)* | `Soudal Fix ALL Crystal` (`290 ml`, SKU `51412`, £7.69 inc-VAT; or Toolstation `61251` £7.99) | £0 |
| **eBay UK / Amazon UK** *(Free Post)* | Extruded clear XT PMMA tube (`Ø60×54×3`), `30×30×3×200 mm` bare Al core, VMQ O-rings (`60×3.5`, `68×2.5`), silicone tubing, ePTFE vent, `25`-pack `M3` nylon washers, JST pigtails, `24 AWG` silicone wire, `90°` USB-C cable | £0–£2 |
| **Estimated Total UK Delivery** | **4 Shipped Baskets + Click & Collect** | **£17–£21** |
| **Estimated All-In UK Delivered (All New)** | **Parts (£120.72 inc-VAT) + Shipping** | **~£138–£142 inc-VAT** |
| **Estimated All-In UK Delivered (Owned M3 CSK / Inserts / Paste)** | **Parts (£104.42 inc-VAT) + Shipping** | **~£121–£125 inc-VAT** |

> **Scope:** The 8 3D-printed parts are printed on a workshop printer (`£0.00`, Black PETG or ASA + Signal-Orange accent). Workshop tools/PPE/consumables (UV400 glasses, filament, O-ring grease, coat-hanger wire bail) and external 20 V USB-C PD power sources are excluded per project scope. Because JLCPCB supplies 2 assembled boards and the sealant/washers/pigtails have surplus, building a **2nd lamp** costs only `~£55–£65` incremental!

## 2. Key Ordering Notes

- **Driver PCB 2-Reel Hybrid Lead-Free HASL PCBA (`PCB-01`):** Upload [driver_pcb_gerbers.zip](../pcb_design/gerbers/driver_pcb/driver_pcb_gerbers.zip), [driver_pcb_bom_pcba_hybrid.csv](../pcb_design/driver_pcb_bom_pcba_hybrid.csv), and [driver_pcb_cpl_hybrid.csv](../pcb_design/driver_pcb_cpl_hybrid.csv) to JLCPCB (**Lead-Free HASL**, Top-Side Economic PCBA, Qty `2`). JLCPCB machine-reflows **`41` SMDs** (`20` Basic + **ONLY `2` Extended reels**: `U1/U2 = AL8860WT-7 C125330` and `U3 = CH224A C42459160`). All **`11` hand-soldered parts** (`4` THT `J1..J4` + `7` chunky 2-pad SMDs `F1`, `D11`, `L1/L2`, `R3/R4`, `R7`) in [driver_pcb_diy_hand_solder.csv](../pcb_design/driver_pcb_diy_hand_solder.csv) order together in **ONE Farnell UK basket** alongside `SW1` and `SW1_BOOT`! (`D13/D14` are left DNP with zero solder paste.)
- **All 8 LEDs on `20 mm` Cu DTP Stars from ONE Vendor (`Convoylight.com`):** `4× Luminus SST-10-UV 365 nm`, `2× Osram KB CSLNM1.14` (`455 nm` Royal Blue), `1× Osram KP CSLNM1.F1` (Phosphor Pure Green, `520–555 nm`), and `1× Osram KW CSLNM1.TG` (`6500 K` Cool White) — every die has an electrically isolated neutral thermal pad (`R_thJS <= 4.9 K/W`) on a `20 mm` direct-thermal-path copper star. Mount Royal Blue on **opposite Faces 1 (`+X`) and 3 (`-X`)**.
- **UV-Transmitting Extruded XT PMMA Shroud (`MECH-TUBE-1`, `Ø60 × 54 × 3.0 × 115 mm`):** Order a short `250–300 mm` length of **extruded clear XT PMMA** (non-UV-blocked; Röhm `0A070` / Perspex XT / Altuglas XT) on eBay UK free-post and cut cleanly to `115 mm` (`±2.0 mm` tolerant) in the workshop. Verify `365 nm` transmission on arrival with the white-paper fluorescence bench check in [ASSEMBLY_GUIDE.md](../docs/ASSEMBLY_GUIDE.md). Never clean PMMA with IPA!
- **Local Click-and-Collect Neutral Sealant (`MECH-SEAL-1`):** **`Soudal Fix ALL Crystal`** (`290 ml`, Screwfix `51412`, `£7.69` inc-VAT, `£0` shipping) — solvent-free SMX hybrid MS-polymer, non-acetic and copper-safe. Apply **only** to plastic-to-aluminum joints (top collar groove and `MECH-PLUG-TOP` finial; never onto the PMMA tube) and allow `24 h` open-air cure.
- **Unpainted Bare Mill Aluminum Core (`MECH-HS-CORE`):** `200.0 mm` length of `30 × 30 × 3.0 mm` 6063-T6 square box section left **completely unpainted** (`ε = 0.20`, £0 paint, zero UV outgassing, zero masking).
- **Unified Workshop `M3` Hardware (`MECH-INS-M3`, `MECH-FAST-M3`, `MECH-WASH-NYLON`):** The entire lamp uses **ONE single thread size (`M3`)**: `14×` identical standard `M3 × 5.0 × 4.2 mm` brass heat-set inserts, `32×` workshop `M3` countersunk (`CSK`) screws (`22× M3×8`, `2× M3×10`, `8× M3×12`) + `20×` owned `M3` steel flat washers, and `20×` `M3` DIN 125 nylon insulating washers (`Ø7.0 × 0.8 mm`, all from ONE `25`-pack — `16×` for the 8 LED stars + `4×` isolating the PCB screws at `H1..H4`!).

## 3. Verification

```bash
python3 bom/verify_bom.py
```
