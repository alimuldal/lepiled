# LepiLED DIY Maxi Switch — Master Bill of Materials (Rev 4.7)

The machine-verified master BOM lives in [bom.csv](bom.csv) and is audited 1:1 against [COMPONENT_IDS.csv](../circuit_design/COMPONENT_IDS.csv) (`66` RefDes), [driver_pcb_bom_pcba.csv](../pcb_design/driver_pcb_bom_pcba.csv) (`52` On-PCB parts), the derived 2-Extended-reel Hybrid PCBA files ([driver_pcb_bom_pcba_hybrid.csv](../pcb_design/driver_pcb_bom_pcba_hybrid.csv), [driver_pcb_cpl_hybrid.csv](../pcb_design/driver_pcb_cpl_hybrid.csv), [driver_pcb_diy_hand_solder.csv](../pcb_design/driver_pcb_diy_hand_solder.csv)), and [MECH_PARTS.csv](../mechanical_design/MECH_PARTS.csv) (`22` mechanical IDs) via [verify_bom.py](verify_bom.py).

## 1. Single-Unit Hobby Cost Summary (UK GBP)

| Domain | 1-Off Checkout (ex-VAT) | 1-Off Checkout (inc 20% VAT) | Amortized Per-Lamp (ex-VAT) |
|---|---:|---:|---:|
| **Electrical (`66` RefDes incl. `8×` `20 mm` Copper DTP LED stars)** | £38.01 | £45.61 | £36.74 |
| **Harness (pre-crimped JST-XH pigtails, `24 AWG` UV silicone wire, `90°` USB-C PD cable)** | £8.34 | £10.01 | £6.59 |
| **PCB Fab + 2-Reel Hybrid Economic PCBA (`driver_pcb`, Lead-Free HASL, 2-pc min)** | £15.00 | £18.00 | £7.50 |
| **Mechanical (`200 mm` Al core, `Ø60×54` XT PMMA tube, O-rings, ePTFE vent, oxime silicone, matte-black paint, brass inserts, screws)** | £43.93 | £52.72 | £43.10 |
| **Total 1-Off Build (All Items Purchased New)** | **£105.28** | **£126.34** | **£93.93** |
| **Net 1-Off Out-of-Pocket (Using Owned Screws, Thermal Paste & Matte-Black Spray)** | **£93.43** | **£112.12** | — |

> **Scope:** The 8 3D-printed parts are printed in-house (`£0.00`, Black ASA + Signal-Orange accent). External USB-C PD power sources (laptop charger or 20 V PD power bank) are excluded.

## 2. Key Ordering Notes

- **Driver PCB Hybrid PCBA (`PCB-01`):** Upload [driver_pcb_gerbers.zip](../pcb_design/gerbers/driver_pcb/driver_pcb_gerbers.zip), [driver_pcb_bom_pcba_hybrid.csv](../pcb_design/driver_pcb_bom_pcba_hybrid.csv), and [driver_pcb_cpl_hybrid.csv](../pcb_design/driver_pcb_cpl_hybrid.csv) to JLCPCB (`40` SMDs assembled, only 2 Extended reels: `U1/U2` `C125330` and `U3` `C42459160`). Hand-solder the `10` bulky parts (`J1..J4` THT + `F1`, `D11`, `L1`, `L2`, `R3`, `R4`) from RS UK / Farnell UK listed in [driver_pcb_diy_hand_solder.csv](../pcb_design/driver_pcb_diy_hand_solder.csv). *(Optional industrial upgrade for sub-zero or `> 30 °C` ambient builds: swap `U4` from Basic `LM393DR2G` `C7955` to `LM2903DR2G` `C57474`.)*
- **Toggle Switch (`SW1`, `C&K 7211SYZBE` + `759D02000` Boot):** Uses gold dry-circuit contacts (`0.4 VA max`) and a threaded `1/4-40` bushing for the waterproof silicone boot. Do not substitute silver-contact switches, which oxidize outdoors on microamp logic signals. *(Multicomp Pro `E4`, Farnell `2113266`, is a compatible boot alternative.)*
- **UV-Transmitting Acrylic Tube (`MECH-TUBE-1`, `Ø60 × 54 × 3.0 × 115 mm`):** Order **clear unstabilized extruded PMMA (`Plexiglas XT`)** (`85–92%` @ `365 nm`). Do not substitute UV-blocking cast `Plexiglas GS` or polycarbonate. Never clean with IPA or seal with acetic-cure silicone.
- **Pre-Mounted `20 mm` Copper DTP Stars (`D1..D8`):** `4× Luminus SST-10-UV 365 nm` + `2× Cree XP-E2 Royal Blue` + `1× Green` + `1× Cool White` with electrically neutral thermal pads. Mount with `16× M3 × 8 mm` pan screws and `16× M3` nylon insulating washers, wired with `24 AWG` silicone wire (`HARN-03`).
- **Aluminum Core (`MECH-HS-CORE`) & Matte-Black Spray (`MECH-PAINT-1`):** `200.0 mm` length of `30 × 30 × 3.0 mm` 6063-T6 square tube sprayed matte black (masking the `8× Ø20 mm` star pads bare).
- **Seals & Hardware:** `2×` `60 × 3.5 mm` soft VMQ50/60 shroud O-rings, `1×` `62 × 2.5 mm` VMQ70 lid O-ring, `Ø8 mm` adhesive IP68 ePTFE vent patch, neutral-cure oxime RTV silicone, `10× M3` + `4× M2.5` brass heat-set inserts, and standard `M3`/`M2.5` machine screws.

## 3. Verification

```bash
python3 bom/verify_bom.py
```
