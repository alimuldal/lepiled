# LepiLED DIY Maxi Switch — Master Bill of Materials (Rev 4.3 — Field-Robust 1-Off Hobby Build)

Machine-verified master BOM in [bom.csv](file:///home/alimuldal/src/lepiled/bom/bom.csv), audited 1:1 against [COMPONENT_IDS.csv](file:///home/alimuldal/src/lepiled/circuit_design/COMPONENT_IDS.csv) (`75` RefDes), [driver_pcb_bom_pcba.csv](file:///home/alimuldal/src/lepiled/pcb_design/driver_pcb_bom_pcba.csv) (`61` populated PCBA parts), and [MECH_PARTS.csv](file:///home/alimuldal/src/lepiled/mechanical_design/MECH_PARTS.csv) (`15` mechanical IDs) via [verify_bom.py](file:///home/alimuldal/src/lepiled/bom/verify_bom.py).

## 1. Single-Unit Hobby Cost Summary (UK GBP)

Rev 4.3 keeps every Rev 4.2 cost/buildability win (pre-mounted `20 mm` Copper DTP stars, single custom `driver_pcb`, single bare protruding `250 mm` Al core, zero brass inserts, single `M3` fastener size) while replacing brittle borosilicate glass with a **shatter-resistant UV-transmitting PMMA acrylic tube** (`-£2.09` ex-VAT, `-143 g`) and adding 3D-printed weatherproofing (`MECH-BASE-RING` switch guard and an integral `Ø116 mm` shroud drip-brim with drip-break groove):

| Domain | 1-Off Hobby Checkout (ex-VAT) | 1-Off Hobby Checkout (inc 20% VAT) | Amortized Per-Lamp (ex-VAT) |
|---|---:|---:|---:|
| **Electrical (`75` RefDes incl. `8×` `20 mm` Copper DTP LED stars)** | £42.72 | £51.26 | £41.00 |
| **Harness (Pre-crimped `22 AWG` JST-XH 2P & 3P pigtails — no crimper)** | £2.50 | £3.00 | £0.75 |
| **PCB Fab + JLCPCB Economic PCBA (`driver_pcb` ONLY, 2-pc min)** | £20.00 | £24.00 | £10.00 |
| **Mechanical (`250 mm` bare `3 mm` Al tube, UVT PMMA shroud, seals, M3 + nylon washers)** | £26.13 | £31.36 | £26.13 |
| **TOTAL Rev 4.3 1-Off Build (All Items Purchased New)** | **£91.35** | **£109.62** | **£77.88** |
| **NET 1-Off Out-of-Pocket (Using Owned Workshop `M3` Screws/Nuts & PC Paste)** | **£84.80** | **£101.76** | — |

> **Scope Notes:** All 7 3D-printed parts (`MECH-BASE-RING`, `MECH-LID-BOT`, `MECH-CAP-BOT`, `MECH-CAP-TOP`, `MECH-PLUG-TOP`, `MECH-PLUG-BOT`, `MECH-DRILL-JIG`) are printed in-house (`£0.00`, support-free FDM PETG/ASA). External USB-C PD power sources (laptop charger or `20 V` PD power bank) and courier delivery fees are excluded.

## 2. Key Ordering Notes (Rev 4.3)

- **UV-Transmitting PMMA Tube (`MECH-TUBE-1` — `Ø75 × 69 × 3.0 mm × 150 mm`):** Order **UV-transmitting / unstabilized cast PMMA** (e.g. Plexiglas GS 2458 / Perspex UVT, `85–92%` @ `365 nm`, `~£10` inc-VAT from Simply Plastics / Direct Plastics UK). **Do NOT substitute polycarbonate (PC)**, which blocks `> 98%` of `365 nm` UV-A.
- **Pre-Mounted `20 mm` Copper DTP Stars (`ELEC-08..11`):** `4× Luminus SST-10-UV 365 nm` + `2× Cree XP-E2 Royal Blue` + `1× Green` + `1× Cool White` (`£23.40` ex-VAT from Kaidomain/Convoy). Confirm electrically neutral thermal pads and mount with all `16× M3` nylon insulating washers (`MECH-WASH-NYLON`).
- **Single Stock Metal Part (`MECH-HS-CORE`):** `250.0 mm` stock cut of bare `40 × 40 × 3.0 mm` Al 6063 box section (`£6.67` ex-VAT; `3.0 mm` wall retained for full `M3` thread engagement).
- **Single `M3` Fastener Size (`MECH-FAST-M3`):** `20× M3×8` (`16×` stars + `4×` bottom plug pins), `2× M3×12` (`cap_top` lock), `6× M3×16` (`2×` bulkhead CSK + `4×` base-ring/lid SHCS), plus `6× M3` hex nuts (`4×` captive in `cap_bot` + `2×` in `plug_bot`).
- **JLCPCB Economic PCBA + UK Consolidation:** `driver_pcb` is the sole custom PCB (`57` SMD JLCPCB Basic-optimized; `J1..J4`, `SW1`, `SW1_BOOT` consolidated on Farnell UK / RS UK to avoid DigiKey UK's `£22` `< £65` shipping fee).

## 3. Verification Command

```bash
python3 bom/verify_bom.py
```
