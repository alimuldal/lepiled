# LepiLED DIY Maxi Switch — Master Bill of Materials (Rev 4.8)

The machine-verified master BOM lives in [bom.csv](bom.csv) and is audited 1:1 against [COMPONENT_IDS.csv](../circuit_design/COMPONENT_IDS.csv) (`72` RefDes + every `Datasheet_Ref` verified on disk), [driver_pcb_bom_pcba.csv](../pcb_design/driver_pcb_bom_pcba.csv) (`54` On-PCB parts), the derived Full-SMD ENIG PCBA files ([driver_pcb_bom_pcba_hybrid.csv](../pcb_design/driver_pcb_bom_pcba_hybrid.csv), [driver_pcb_cpl_hybrid.csv](../pcb_design/driver_pcb_cpl_hybrid.csv), [driver_pcb_diy_hand_solder.csv](../pcb_design/driver_pcb_diy_hand_solder.csv)), and [MECH_PARTS.csv](../mechanical_design/MECH_PARTS.csv) (`23` mechanical IDs) via [verify_bom.py](verify_bom.py).

## 1. Low-Hassle Full-SMD ENIG Single-Unit Cost Summary (UK GBP)

| Domain | 1-Off Parts (ex-VAT) | 1-Off Parts (inc 20% VAT) | Amortized Per-Lamp (ex-VAT) |
|---|---:|---:|---:|
| **Electrical (`72` RefDes incl. `8×` `20 mm` LED stars from Kaidomain + LED-TECH.DE)** | £43.41 | £52.09 | £42.25 |
| **Harness (pre-crimped JST-XH pigtails, `24 AWG` UV silicone wire, `90°` USB-C PD cable)** | £8.34 | £10.01 | £6.59 |
| **PCB Fab (ENIG) + Full-SMD Economic PCBA (`driver_pcb`, `48` SMDs [7 Ext reels], 2-pc min)** | £38.65 | £46.38 | £19.33 |
| **Mechanical (`0A070` PMMA, `OTTOSEAL S 72 Clear`, `200 mm` Al core, O-rings, sleeve, vent, inserts, hardware)** | £57.78 | £69.34 | £53.20 |
| **Total Parts-Only 1-Off (All Items Purchased New)** | **£148.18** | **£177.82** | **£121.37** (`£145.64` inc-VAT) |
| **Net Parts-Only 1-Off (Using Owned M3 Screws, Thermal Paste & Matte-Black Spray)** | **£133.43** | **£160.12** | — |

### Estimated Multi-Vendor UK Delivery Breakdown (Single-Lamp Order)

Hobby single-unit builds span multiple specialist vendors; estimated UK delivery charges are shown separately below so there are no checkout surprises:

| Vendor | Contents | Est. UK Shipping (inc-VAT) |
|---|---|---:|
| **JLCPCB** | 5× bare ENIG `driver_pcb` + 2× Full-SMD assembled (`48` SMDs) | £9–£12 |
| **Farnell UK / RS UK** | `SW1` (`C&K 7211SYZBE`), `SW1_BOOT`, `J1..J4` THT, `MECH-VENT-1` | £0–£6 *(free over threshold / RS)* |
| **Kaidomain** | `4× Luminus SST-10-UV 365 nm` + `1× Cree XP-E2 Cool White` (`20 mm` Cu DTP) | £4 |
| **LED-TECH.DE** | `2× Cree XP-E2 Royal Blue 455 nm` + `1× Cree XP-E2 Green 528 nm` (`20 mm` Star) | £11–£14 |
| **Amari Plastics / Acrylglas-Shop** | `PLEXIGLAS® XT Clear 0A070 (29070)` `Ø60 × 54 × 3.0 × 115 mm` tube | £8–£12 |
| **Metals4U UK / eBay UK** | `30 × 30 × 3.0 × 200 mm` 6063-T6 Al box section | £5 |
| **Sealants Online UK** | `OTTOSEAL® S 72 Clear` (`310 ml` PMMA-safe neutral-alkoxy RTV) | £6 |
| **Simply Bearings / Accu / Amazon UK** | VMQ O-rings (`60×3.5`, `68×2.5`), silicone tubing, brass inserts, nylon screws/washers, pigtails, USB-C cable | £5–£8 |
| **Estimated Total UK Delivery** | **8 Vendor Shipments** | **£48–£67** |
| **Estimated All-In UK Delivered Single Lamp (All New)** | **Parts (£177.82 inc-VAT) + Shipping** | **~£226–£245 inc-VAT** |
| **Estimated All-In UK Delivered (Owned M3 / Paste / Spray)** | **Parts (£160.12 inc-VAT) + Shipping** | **~£208–£227 inc-VAT** |

> **Scope:** The 8 3D-printed parts are printed on a workshop printer (`£0.00`, Black PETG or ASA + Signal-Orange accent). Workshop tools/PPE/consumables (UV400 glasses, filament, O-ring grease) and external 20 V USB-C PD power sources (laptop charger or 20 V PD power bank) are excluded per project scope. Note that the JLCPCB 2-pc minimum, `310 ml` `OTTOSEAL S 72`, and fastener multi-packs make a **2nd lamp** cost only ~£80–£95 incremental!

## 2. Key Ordering Notes

- **Driver PCB Full-SMD ENIG PCBA (`PCB-01` — Low-Hassle Path):** Upload [driver_pcb_gerbers.zip](../pcb_design/gerbers/driver_pcb/driver_pcb_gerbers.zip), [driver_pcb_bom_pcba_hybrid.csv](../pcb_design/driver_pcb_bom_pcba_hybrid.csv), and [driver_pcb_cpl_hybrid.csv](../pcb_design/driver_pcb_cpl_hybrid.csv) to JLCPCB (**ENIG**, Top-Side Economic PCBA, Qty `2`). JLCPCB machine-reflows **all `48` SMDs** (`20` Basic + `7` Extended reels: `U1/U2`, `U3`, `F1`, `D11`, `L1/L2`, `R3/R4`, `R7`). Only the **`4` through-hole connectors (`J1..J4`)** in [driver_pcb_diy_hand_solder.csv](../pcb_design/driver_pcb_diy_hand_solder.csv) are hand-soldered at home (`D13/D14` are left DNP with zero solder paste).
- **UV-Transmitting Plexiglass Shroud (`MECH-TUBE-1`, `Ø60 × 54 × 3.0 × 115 mm`):** Specifically order **Röhm `PLEXIGLAS® XT Clear 0A070` (`29070`)** (`~80–85%` normal / `~79.8%` cone-integrated transmission at `365 nm`) from Amari Plastics UK or Acrylglas-Shop. Do **not** substitute UV-blocking cast `GS` or polycarbonate. Verify 365 nm transmission on arrival with the quick white-paper fluorescence bench check in [ASSEMBLY_GUIDE.md](../docs/ASSEMBLY_GUIDE.md). Never clean PMMA with IPA!
- **PMMA-Safe Sealant (`MECH-SEAL-1`):** Use **`OTTOSEAL® S 72 Clear`** (Röhm-certified non-crazing neutral-alkoxy silicone for PLEXIGLAS XT) and observe a mandatory **48-hour open-air cure** before closing the shroud/lid.
- **Pre-Mounted `20 mm` LED Stars (`D1..D8`):** `4× Luminus SST-10-UV 365 nm` + `1× Cree XP-E2 Cool White` from **Kaidomain** (`20 mm` Cu DTP), plus `2× Cree XP-E2 Royal Blue 455 nm` (`LT-2231`) + `1× Cree XP-E2 Green 528 nm` (`LT-2228`) from **LED-TECH.DE**. Mount Royal Blue on **opposite Faces 1 (`+X`) and 3 (`-X`)** with `16× M3 × 8 mm` pan screws and `16× M3` DIN 125 nylon washers edge-clamping at `R = 11.7 mm`.
- **Aluminum Core (`MECH-HS-CORE`) & Chimney-Only Matte-Black Spray (`MECH-PAINT-1`):** `200.0 mm` length of `30 × 30 × 3.0 mm` 6063-T6 square tube. Spray **only the top `58.5 mm` protruding chimney** matte black — leave the interior shroud section bare mill aluminum (zero UV paint outgassing and zero star-pad masking!).
- **Seals & Hardware:** `2×` `60 × 3.5 mm` soft VMQ50/60 shroud O-rings, `1×` **`68 × 2.5 mm` VMQ70** lid O-ring, `10 mm` slit silicone tubing sleeve (`MECH-GROMMET-1`, `Ø8 × Ø4 mm`), `Ø8 mm` adhesive IP68 ePTFE vent patch, `8× M3×5×4.2` + `2× M3×4×4.2` short blind brass inserts, `4× M2.5×4×3.5` brass inserts, `4× M2.5 × 6 mm` **nylon** pan screws, and `28× M3` machine screws (`16× M3×8` pan, `2× M3×8` CSK, `2× M3×10` SHCS, `8× M3×12` SHCS).

## 3. Verification

```bash
python3 bom/verify_bom.py
```
