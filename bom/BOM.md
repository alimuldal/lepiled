# LepiLED DIY Maxi Switch — Master Bill of Materials

The machine-verified master BOM lives in [bom.csv](bom.csv) and is audited 1:1 against [COMPONENT_IDS.csv](../circuit_design/COMPONENT_IDS.csv) (`72` RefDes and verified `Datasheet_Ref` files), [driver_pcb_bom_pcba.csv](../pcb_design/driver_pcb_bom_pcba.csv) (`54` On-PCB parts), the derived 2-Reel Hybrid HASL PCBA files ([driver_pcb_bom_pcba_hybrid.csv](../pcb_design/driver_pcb_bom_pcba_hybrid.csv), [driver_pcb_cpl_hybrid.csv](../pcb_design/driver_pcb_cpl_hybrid.csv), [driver_pcb_diy_hand_solder.csv](../pcb_design/driver_pcb_diy_hand_solder.csv)), and [MECH_PARTS.csv](../mechanical_design/MECH_PARTS.csv) (`20` mechanical IDs) via [verify_bom.py](verify_bom.py).

## 1. Single-Unit Cost Summary (UK GBP)

| Domain | 1-Off Parts (ex-VAT) | 1-Off Parts (inc 20% VAT) | Amortized Per-Lamp (ex-VAT) |
|---|---:|---:|---:|
| **Electrical (`72` RefDes incl. `8×` Convoy `20 mm` Cu DTP LED stars + Farnell UK DIY basket)** | £33.91 | £40.69 | £32.75 |
| **Harness (pre-crimped JST-XH pigtails, `2 m` `24 AWG` UV silicone wire, `2.0 m` `90°` USB-C PD cable)** | £10.00 | £12.00 | £8.25 |
| **PCB Fab (Lead-Free HASL) + 2-Reel Hybrid Economic PCBA (`driver_pcb`, `41` SMDs, 2-pc min)** | £15.00 | £18.00 | £7.50 |
| **Mechanical (XT PMMA, `30×30×2×300 mm` clear-anodized Al, epoxy, `80 ml` Soudal, O-rings, pad/shims, HW)** | £48.39 | £58.07 | £42.28 |
| **Total Parts-Only 1-Off (All Items Purchased New)** | **£107.30** | **£128.76** | **£90.78** (`£108.94` inc-VAT) |
| **Net Out-of-Pocket Parts-Only (Using Owned M3 HW & Thermal Pad/Shims)** | **£97.39** | **£116.87** | — |

### UK Delivery & Checkout Reality Breakdown

| Vendor | Contents | Est. UK Shipping / Fees (inc-VAT) |
|---|---|---:|
| **JLCPCB** | 3× bare + 2× 2-Reel Hybrid assembled Lead-Free HASL `driver_pcb` (`41` SMDs: `20` Basic + `U1/U2`, `U3`). Live verified UK-VAT DDP invoice total: **`£31.01`** (includes boards, SMDs, setup, Global Direct Line shipping, and 20% UK VAT — about `£9.50` above line-item PCB + JLC SMD sum) | Included in `£31.01` DDP (`~£9.50` over parts line) |
| **Convoylight.com** | `4× Luminus SST-10-UV 365 nm` + `2× Osram KB CSLNM1.14 455 nm` + `1× KP CSLNM1.F1 Green` + `1× KW CSLNM1.TG 6500 K` (all on `20 mm` Cu DTP stars) | £3 |
| **Farnell UK** | `SW1` (`C&K 7211SYZBE`), `SW1_BOOT` (`759D02000`), `4` THT (`J1..J4`) + `7` 2-pad SMDs (`F1`, `D11`, `L1/L2`, `R3/R4`, `R7`) — note Farnell applies a small-order handling fee below `£40` ex-VAT (`~£10–£12` inc-VAT unless combined with other parts or ordered via CPC / Mouser / RS) | £5–£12 |
| **eBay UK / Amazon UK / Plastics Supplier** | Pre-cut extruded clear XT PMMA (`Ø60×54×3 × 115 mm`), `30×30×2×300 mm` clear-anodized Al tube, thermal epoxy (`Arctic Alumina` / `MG 8329TFS`), `80 ml` `Soudal Fix ALL Crystal`, VMQ50 O-rings (`60×3.5`, `88×2.5`), silicone tubing, ePTFE vent, `2× DIN 912 M4×50` SS SHCS + `2×` washers + `2×` nylocs, `M3` nylon washers, JST pigtails, `2 m` silicone wire, `2.0 m` supple TPE/silicone left/right `90°` USB-C cable | £4–£10 |
| **Estimated Realistic All-In UK Delivered (All New)** | **Parts (£128.76 inc-VAT) + Shipping / DDP / Small-Order Fees** | **~£150–£163 inc-VAT** |
| **Estimated Realistic All-In UK Delivered (Owned M3 HW & Pad/Shims)** | **Parts (£116.87 inc-VAT) + Shipping / DDP / Small-Order Fees** | **~£138–£150 inc-VAT** |

> **Scope:** The 6 3D-printed parts are printed in White PETG or White ASA on a workshop printer (`~350–400 g` filament; excluded from parts total). The hanging loop is bent from salvaged `~2.0–2.5 mm` steel coat-hanger wire (unpriced in BOM). Basic workshop tools (soldering iron, `Ø4.5 mm` drill bit, center punch, pliers, UV400 safety glasses) and external 20 V USB-C PD power sources are excluded. No aluminum tap set, caulking gun, or second accent filament spool is needed. Because JLCPCB supplies 2 assembled boards and several consumables have surplus, a second lamp costs `~£60–£70` incremental.

## 2. Ordering Notes

- **Driver PCB 2-Reel Hybrid Lead-Free HASL PCBA (`PCB-01`):** Upload [driver_pcb_gerbers.zip](../pcb_design/gerbers/driver_pcb/driver_pcb_gerbers.zip), [driver_pcb_bom_pcba_hybrid.csv](../pcb_design/driver_pcb_bom_pcba_hybrid.csv), and [driver_pcb_cpl_hybrid.csv](../pcb_design/driver_pcb_cpl_hybrid.csv) to JLCPCB (Lead-Free HASL, Top-Side Economic PCBA, Qty `2`). JLCPCB populates `41` SMDs (`20` Basic + `2` Extended reels: `U1/U2 = AL8860WT-7 C125330` and `U3 = CH224A C42459160`). The `11` hand-soldered parts (`4` THT `J1..J4` + `7` 2-pad SMDs `F1`, `D11`, `L1/L2`, `R3/R4`, `R7`) in [driver_pcb_diy_hand_solder.csv](../pcb_design/driver_pcb_diy_hand_solder.csv) order in the same Farnell UK basket as `SW1` and `SW1_BOOT`. `D13/D14` are left DNP with zero solder paste.
- **LED Stars (`D1..D8`, `Convoylight.com`):** `4× Luminus SST-10-UV 365 nm`, `2× Osram KB CSLNM1.14` (`455 nm` Royal Blue), `1× Osram KP CSLNM1.F1` (Phosphor Pure Green, `520–555 nm`), and `1× Osram KW CSLNM1.TG` (`6500 K` Cool White), all on `20 mm` Copper DTP stars with electrically neutral thermal pads (`R_thJS <= 4.9 K/W`).
- **UV-Transmitting Extruded XT PMMA Shroud (`MECH-TUBE-1`, `Ø60 × 54 × 3.0 × 115 mm`):** Order from a UK technical plastics supplier specifying non-UV-blocked extruded XT PMMA (Röhm `PLEXIGLAS XT 0A070` / Perspex XT / Altuglas XT), ideally pre-cut to `115 mm` (`±2.0 mm` tolerant). Verify `365 nm` transmission with the split-beam side-by-side white-paper test in [ASSEMBLY_GUIDE.md](../docs/ASSEMBLY_GUIDE.md). Do not clean PMMA with IPA.
- **2-Part Thermally Conductive Epoxy (`MECH-TIM-1`):** `Arctic Alumina Thermal Adhesive` (`5 g`) or `MG Chemicals 8329TFS` (`~1.4–1.8 W/(m·K)`, electrically insulating, `6–10 MPa` shear). Permanently bonds all 8 LED stars to the aluminum core without drilling or tapping any holes inside the optical chamber.
- **Neutral Sealant (`MECH-SEAL-1`):** `Soudal Fix ALL Crystal` **`80 ml` hand-squeeze tube** (`~£4.99` inc-VAT, no caulking gun needed) — solvent-free SMX hybrid MS-polymer, non-acetic and copper-safe. Apply to the bottom nosecone hub V-groove (before sliding the PMMA tube on), the top collar V-groove, and the `+Y` cable clamp flange/sleeve seam (keep off the PMMA tube) and cure `24 h`.
- **Open-Chimney Clear-Anodized Aluminum Core (`MECH-HS-CORE`):** Standard `300.0 mm` length of **`30 × 30 × 2.0 mm`** clear/silver-anodized 6063-T6 square box section (`26 × 26 mm` unobstructed open bore, `ε_IR ≈ 0.82`, `181 g`; alternatively a bare mill tube coated in matte-white or matte-black paint with the 8 star landing circles abraded bare).
- **PCB Thermal Bridge (`MECH-TIM-PAD`):** Captive `15 × 15 mm` stack of `1.0 mm` electrically insulating silicone thermal gap pads (one against `B.Cu`, one against the anodized Al core) sandwiching `15 × 15 × 0.5 mm` brass shims (or stacked silicone pads to `~5.8–6.0 mm` uncompressed) inside `MECH-TOP-BASE`'s `15.6 × 15.6 mm` chute behind `U1/U2`.
- **Top Rain-Bell Axial Face O-Ring (`MECH-GASKET-3`):** `88 mm ID × 2.5 mm CS` soft Silicone VMQ50 O-ring compressed axially (`20.0%` squeeze, `72.2%` fill) in `MECH-TOP-BASE`'s flat `Z = 171.0 mm` deck groove (`2.00 mm` layer-quantized depth).
- **Standard `2.0 m` Left/Right `90°` USB-C PD Cable (`HARN-04`):** Standard `60–100 W` USB-C to USB-C PD cable with a **left/right** `90°` plug (`<= 18.0 mm` protrusion below receptacle mouth, `Ø4.0–4.5 mm` supple TPE or silicone round jacket rather than a stiff armored braided sheath so it forms the tight internal horizontal S-curve comfortably). `2.0 m` length lets the power bank sit safely in a drybag on the ground under a tripod or branch.
- **Fasteners (`MECH-INS-M3`, `MECH-FAST-M3`, `MECH-FAST-M4`, `MECH-WASH-NYLON`):** `6×` `M3 × 5.0 × 4.2 mm` brass inserts (`4×` eaves + `2×` blind clamp), `4×` DIN 934 `M3` hex nuts (captive PCB stanchion pockets), `10×` `M3` screws (`4× M3×12` CSK eaves, `4× M3×8` pan-head PCB, `2× M3×12` pan-head cable clamp + steel flat washers), `12×` `M3` DIN 125 `0.8 mm` nylon insulating washers (`3×` stacked per PCB screw on `H1..H4`, from one 25-pack), and `2×` `DIN 912 M4 × 50 mm` A2 stainless SHCS + `2×` M4 washers (top bolt) + `2×` M4 nyloc nuts (bottom nut locks inside the captive `-X` hex-nut pocket; top bolt carries an unpriced bent steel coat-hanger wire hanging bail on the two `6.0 mm` spools printed with `MECH-PLUG-TOP`).

## 3. Verification

```bash
python3 bom/verify_bom.py
```
