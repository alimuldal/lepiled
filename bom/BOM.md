# LepiLED DIY Maxi Switch — Master Bill of Materials (Rev 4.7 — `CH224A` 2-Reel Hybrid PCBA)

Machine-verified master BOM in [bom.csv](bom.csv), audited 1:1 against [COMPONENT_IDS.csv](../circuit_design/COMPONENT_IDS.csv) (`67` RefDes), [driver_pcb_bom_pcba.csv](../pcb_design/driver_pcb_bom_pcba.csv) (`53` populated PCBA parts), the programmatically derived 2-Extended-reel Hybrid PCBA files ([driver_pcb_bom_pcba_hybrid.csv](../pcb_design/driver_pcb_bom_pcba_hybrid.csv), [driver_pcb_cpl_hybrid.csv](../pcb_design/driver_pcb_cpl_hybrid.csv), [driver_pcb_diy_hand_solder.csv](../pcb_design/driver_pcb_diy_hand_solder.csv)), and [MECH_PARTS.csv](../mechanical_design/MECH_PARTS.csv) (`22` mechanical IDs) via [verify_bom.py](verify_bom.py).

## 1. Single-Unit Hobby Cost Summary (UK GBP)

Rev 4.7 switches `driver_pcb` to the locally stocked `WCH CH224A` (`C42459160`, `1.0 mm` leaded `ESSOP-10`) and 100% live-verified JLCPCB Basic passives/semiconductors (`TL431`, `LM393DR2G`, `2N7002`, `SS34`, `KT-0603R`, `BAV99`), dropping Hybrid PCBA to **only `2` Extended reels (`$6` feeder fees)** and Lead-Free HASL (`-£9.57` ex-VAT vs Rev 4.6):

| Domain | 1-Off Hobby Checkout (ex-VAT) | 1-Off Hobby Checkout (inc 20% VAT) | Amortized Per-Lamp (ex-VAT) |
|---|---:|---:|---:|
| **Electrical (`67` RefDes incl. `8×` `20 mm` Copper DTP LED stars)** | £38.15 | £45.78 | £36.95 |
| **Harness (JST-XH 2P/3P pigtails + `24 AWG` UV silicone wire + captured `90°` USB-C PD cable)** | £8.34 | £10.01 | £6.59 |
| **PCB Fab + 2-Reel Hybrid Economic PCBA (`driver_pcb` ONLY, Lead-Free HASL, 2-pc min)** | £15.00 | £18.00 | £7.50 |
| **Mechanical (`200 mm` `30×30×3` Al core, `Ø60×54` XT PMMA, 3 radial O-rings, ePTFE vent, oxime silicone, matte-black spray, brass inserts, screws)** | £43.93 | £52.72 | £43.10 |
| **TOTAL Rev 4.7 1-Off Build (All Items Purchased New)** | **£105.42** | **£126.50** | **£94.14** |
| **NET 1-Off Out-of-Pocket (Using Owned Workshop Screws, PC Paste & Matte-Black Spray)** | **£93.57** | **£112.28** | — |

> **Scope Notes:** All 8 3D-printed parts (`MECH-CAP-BOT`, `MECH-LID-BOT`, `MECH-CABLE-CLAMP` `2×`, `MECH-CORE-ANCHOR`, `MECH-CAP-TOP`, `MECH-PLUG-TOP`, `MECH-HANG-BUSHING` `2×`, `MECH-DRILL-JIG`) are printed in-house (`£0.00`, support-free FDM Black ASA + Signal-Orange accent). External USB-C PD power sources (laptop charger or `20 V` PD power bank) are excluded.

## 2. Key Ordering Notes (Rev 4.6)

- **Toggle Switch (`SW1`, `C&K 7211SYZBE` + `759D02000` Boot):** Retained intentionally after verifying UK distributor stock. Cheaper `~£2.50–£3.50` panel-mount `DPDT On-On-On` switches on Farnell UK (e.g. Multicomp Pro `1MD6T1B5M1QE`, Farnell `1550185`) use **silver contacts** (which oxidize in damp woodland air on `~30 µA` dry-circuit `AL8860 CTRL` lines), while the `£4.27` gold variant (`1MD6T2B4M7RE`, Farnell `1550145`) has an unthreaded bushing that cannot take a waterproof `1/4-40` sealing boot. *(Multicomp Pro `E4`, Farnell `2113266` at `£1.69` ex-VAT, is a drop-in UK boot alternative to `759D02000`.)*
- **Clear Unstabilized Extruded PMMA Tube (`MECH-TUBE-1` — `Ø60 × 54 × 3.0 mm × 115 mm`):** Order **clear unstabilized extruded PMMA (`Plexiglas XT`)** (`85–92%` @ `365 nm`, `~£15` inc-VAT realistic UK 1-off delivered from Clear Plastic Tube UK / Simply Plastics UK). **Do NOT substitute UV-blocking cast `Plexiglas GS` or polycarbonate (PC).** Never clean with IPA or seal with acetic-cure silicone.
- **Pre-Mounted `20 mm` Copper DTP Stars (`ELEC-08..11`):** `4× Luminus SST-10-UV 365 nm` + `2× Cree XP-E2 Royal Blue` + `1× Green` + `1× Cool White` (`£23.40` ex-VAT from Kaidomain/Convoy). Mount with `16× M3 × 8 mm` pan screws (black-oxide recommended visually) + `16× M3` nylon insulating washers (`MECH-WASH-NYLON`) and wire with `24 AWG` silicone wire (`HARN-03`).
- **Single Stock Metal Part (`MECH-HS-CORE`) + Matte-Black Spray (`MECH-PAINT-1`):** `200.0 mm` stock cut of bare `30 × 30 × 3.0 mm` Al 6063-T6 box section (`174 g`, `£6.25` ex-VAT delivered on eBay UK / Metals4U) sprayed with matte-black stove/caliper paint (`ε = 0.88`, masking the `8× Ø20 mm` star pads with tape) — drops LED junction temps by **`13.1–16.4 °C`** without paying for custom anodizing.
- **Weatherproofing Kit (`MECH-GASKET-1..3`, `MECH-VENT-1`, `MECH-SEAL-1`):** `2×` **`60 × 3.5 mm` soft VMQ50/60** radial shroud O-rings (ovality-safe for extruded XT PMMA), `1×` **`62 × 2.5 mm` VMQ70** radial lid O-ring, `Ø8 mm` adhesive IP68 ePTFE breather vent patch (applied inside the dry bay on top of `MECH-LID-BOT`), and **neutral-cure oxime** RTV silicone (never acetic-cure).
- **Brass Heat-Set Inserts & Fasteners (`MECH-INS-M3/M25`, `MECH-FAST-M3/M25`):** `10× M3 × 5.0 × 4.2 mm` inserts (`4×` lid, `2×` cable clamp, `4×` core anchor) + `4× M2.5 × 4.0 × 3.5 mm` inserts (`4×` PCB standoffs); `16× M3×8` pan (stars), `2× M3×8` CSK (anchor pin), `6× M3×10` SHCS (`2×` top lock + `4×` lid), `4× M3×12` SHCS (`2×` split cable clamp + `2×` dry-bay anchor), and `4× M2.5×6` pan (`driver_pcb`).

## 3. Verification Command

```bash
python3 bom/verify_bom.py
```
