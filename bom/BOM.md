# LepiLED DIY Maxi Switch — Master Bill of Materials (Rev 4.5 — Compact Weatherproof 1-Off Hobby Build)

Machine-verified master BOM in [bom.csv](file:///home/alimuldal/src/lepiled/bom/bom.csv), audited 1:1 against [COMPONENT_IDS.csv](file:///home/alimuldal/src/lepiled/circuit_design/COMPONENT_IDS.csv) (`75` RefDes), [driver_pcb_bom_pcba.csv](file:///home/alimuldal/src/lepiled/pcb_design/driver_pcb_bom_pcba.csv) (`61` populated PCBA parts), and [MECH_PARTS.csv](file:///home/alimuldal/src/lepiled/mechanical_design/MECH_PARTS.csv) (`18` mechanical IDs) via [verify_bom.py](file:///home/alimuldal/src/lepiled/bom/verify_bom.py).

## 1. Single-Unit Hobby Cost Summary (UK GBP)

Rev 4.5 budgets every real weatherproofing and harness item honestly for a single-unit UK build (including realistic delivered XT PMMA pricing, the permanently captured `90°` USB-C PD cable, `M20` IP68 split cable gland, `MECH-GASKET-3` lid O-ring, IP68 ePTFE breather vent, neutral-cure oxime silicone sealant, and `24 AWG` UV-stable silicone inter-star wire):

| Domain | 1-Off Hobby Checkout (ex-VAT) | 1-Off Hobby Checkout (inc 20% VAT) | Amortized Per-Lamp (ex-VAT) |
|---|---:|---:|---:|
| **Electrical (`75` RefDes incl. `8×` `20 mm` Copper DTP LED stars)** | £42.72 | £51.26 | £41.00 |
| **Harness (JST-XH 2P/3P pigtails + `24 AWG` UV silicone wire + captured `90°` USB-C PD cable)** | £8.34 | £10.01 | £6.59 |
| **PCB Fab + JLCPCB Economic PCBA (`driver_pcb` ONLY, 2-pc min)** | £20.00 | £24.00 | £10.00 |
| **Mechanical (`200 mm` bare `30×30×3` Al core, `Ø60×54` XT PMMA, 3 radial O-rings, M20 split gland, ePTFE vent, oxime silicone, fasteners)** | £39.03 | £46.84 | £39.03 |
| **TOTAL Rev 4.5 1-Off Build (All Items Purchased New)** | **£110.09** | **£132.11** | **£96.62** |
| **NET 1-Off Out-of-Pocket (Using Owned Workshop `M3`/`M2.5` Screws & PC Paste)** | **£103.14** | **£123.77** | — |

> **Scope Notes:** All 6 3D-printed parts (`MECH-BASE-RING`, `MECH-LID-BOT`, `MECH-CAP-BOT`, `MECH-CAP-TOP`, `MECH-PLUG-TOP`, `MECH-DRILL-JIG`) are printed in-house (`£0.00`, support-free FDM PETG or Black ASA; `MECH-PLUG-BOT` eliminated). External USB-C PD power sources (laptop charger or `20 V` PD power bank) are excluded.

## 2. Key Ordering Notes (Rev 4.5)

- **Clear Unstabilized Extruded PMMA Tube (`MECH-TUBE-1` — `Ø60 × 54 × 3.0 mm × 115 mm`):** Order **clear unstabilized extruded PMMA (`Plexiglas XT`)** (`85–92%` @ `365 nm`, `~£15` inc-VAT realistic UK 1-off delivered from Clear Plastic Tube UK / Simply Plastics UK). **Do NOT substitute standard UV-blocking cast `Plexiglas GS` or polycarbonate (PC).** Never clean with IPA or seal with acetic-cure silicone.
- **Pre-Mounted `20 mm` Copper DTP Stars (`ELEC-08..11`):** `4× Luminus SST-10-UV 365 nm` + `2× Cree XP-E2 Royal Blue` + `1× Green` + `1× Cool White` (`£23.40` ex-VAT from Kaidomain/Convoy). Mount with `16× M3 × 8 mm` pan screws + `16× M3` nylon insulating washers (`MECH-WASH-NYLON`) and wire with `24 AWG` silicone wire (`HARN-03`).
- **Single Stock Metal Part (`MECH-HS-CORE`):** `200.0 mm` stock cut of bare `30 × 30 × 3.0 mm` Al 6063-T6 box section (`174 g`, `£6.25` ex-VAT delivered on eBay UK / Metals4U; retains full `3.0 mm` wall for 6-turn `M3` threads).
- **Weatherproofing Kit (`MECH-GASKET-1..3`, `MECH-GLAND-1`, `MECH-VENT-1`, `MECH-SEAL-1`):** `2×` `60 × 3.0 mm` VMQ70 radial shroud O-rings, `1×` `70 × 2.5 mm` VMQ70 radial lid O-ring, `M20` IP68 split waterproof cable gland (`Ø4–5 mm` split seal around captured `90°` USB-C PD cable `HARN-04`), `Ø8 mm` adhesive IP68 ePTFE breather vent patch, and **neutral-cure oxime** RTV silicone (never acetic-cure).
- **Fasteners (`MECH-FAST-M3`, `MECH-FAST-M25`):** `16× M3×8` pan (stars), `4× M3×10` SHCS (`cap_bot`/`cap_top` core locks), `4× M3×16` SHCS + `4× M3` hex nuts (`lid`/`base_ring`), plus `4× M2.5×8` pan (horizontal `driver_pcb`).

## 3. Verification Command

```bash
python3 bom/verify_bom.py
```
