# LepiLED DIY Maxi Switch — Master Bill of Materials (Rev 4.2 — 1-Off Hobby Build)

Machine-verified master BOM in [bom.csv](file:///home/alimuldal/src/lepiled/bom/bom.csv), audited 1:1 against [COMPONENT_IDS.csv](file:///home/alimuldal/src/lepiled/circuit_design/COMPONENT_IDS.csv) (`75` RefDes), [driver_pcb_bom_pcba.csv](file:///home/alimuldal/src/lepiled/pcb_design/driver_pcb_bom_pcba.csv) (`61` populated PCBA parts), and [MECH_PARTS.csv](file:///home/alimuldal/src/lepiled/mechanical_design/MECH_PARTS.csv) (`14` mechanical IDs) via [verify_bom.py](file:///home/alimuldal/src/lepiled/bom/verify_bom.py).

## 1. Single-Unit Hobby Cost Summary (UK GBP)

Rev 4.2 optimizes directly for **true 1-off hobby checkout cost** and ease of assembly—eliminating the second custom PCB (`led_mcpcb`), bare-SMD LED reflow (and unbudgeted stencil/paste/hotplate tooling), the separate top heatsink, all aluminum anchors/adapter discs, brass heat-set inserts, spray paint, and multi-pack seal waste:

| Domain | 1-Off Hobby Checkout (ex-VAT) | 1-Off Hobby Checkout (inc 20% VAT) | Amortized Per-Lamp (ex-VAT) |
|---|---:|---:|---:|
| **Electrical (`75` RefDes incl. `8×` `20 mm` Copper DTP LED stars)** | £42.72 | £51.26 | £41.00 |
| **Harness (Pre-crimped `22 AWG` JST-XH 2P & 3P pigtails — no crimper)** | £2.50 | £3.00 | £0.75 |
| **PCB Fab + JLCPCB Economic PCBA (`driver_pcb` ONLY, 2-pc min)** | £20.00 | £24.00 | £10.00 |
| **Mechanical (Single `250 mm` bare Al tube, glass, seals, M3 + nylon washers)** | £28.02 | £33.62 | £28.02 |
| **TOTAL Rev 4.2 1-Off Build (All Items Purchased New)** | **£93.24** | **£111.89** | **£79.77** |
| **NET 1-Off Out-of-Pocket (Using Owned Workshop `M3` Screws/Nuts & PC Paste)** | **£86.89** | **£104.27** | — |

> **Scope Notes:** All 6 3D-printed parts (`MECH-LID-BOT`, `MECH-CAP-BOT`, `MECH-CAP-TOP`, `MECH-PLUG-TOP`, `MECH-PLUG-BOT`, `MECH-DRILL-JIG`) are printed in-house (`£0.00`, support-free FDM PETG/ASA). External USB-C PD power sources (laptop charger or `20 V` PD power bank) and courier delivery fees are excluded.

## 2. Key Rev 4.2 Cost & Buildability Wins vs Rev 4.1

- **Pre-Mounted `20 mm` Copper DTP Stars (`ELEC-08..11`):** `4× Luminus SST-10-UV 365 nm` + `2× Cree XP-E2 Royal Blue` + `1× Green` + `1× Cool White` pre-reflowed onto `20 mm` Copper DTP boards (`£23.40` ex-VAT / `£28.08` inc-VAT from Kaidomain/Convoy, vs `£35.82` bare LEDs + `led_mcpcb` + `£25–70` unbudgeted stencil/paste/hotplate). Cuts substrate thermal resistance `~24×` (`15.3–18.9 K/W → 0.50 K/W`).
- **Single Stock Metal Part (`MECH-HS-CORE`):** One off-the-shelf `250 mm` cut of bare `40 × 40 × 3 mm` Al 6063 box section (`£6.67` ex-VAT) protrudes `85.5 mm` above `MECH-CAP-TOP` with a drilled `Ø8 mm` hanging hole and 3D-printed press-fit rain plug (`MECH-PLUG-TOP`). Eliminates `SK 578/50 SA`, Al top disc, both Al anchors, `M6` eye bolt, `M4` pins, shims, and spray paint (`-£62.20` ex-VAT 1-off mechanical cost vs Rev 4.1!).
- **Single `M3` Fastener Size & Zero Brass Inserts:** Captive `M3` hex-nut pockets in `MECH-CAP-BOT` and `MECH-PLUG-BOT` plus printed `Ø2.45 mm` PCB locating pins on `MECH-LID-BOT` eliminate all `M2.5` hardware, `M4` bolts, and CNC Kitchen inserts. Only `16× M3` nylon washers (`£1.50` 25-pk) are added to insulate the star mounting screw heads.
- **JLCPCB Economic PCBA + UK Consolidation:** `driver_pcb_bom_pcba.csv` uses JLCPCB Basic LCSC codes for standard passives and LEDs (`D12`, `R1/2/5/6/7/9/10/11/12/13/14/16/17/18/19/20/21/22/23`, `C1–C15`), and the few through-hole parts (`J1..J4`, `SW1`, `SW1_BOOT`) are consolidated onto Farnell UK / RS UK to avoid DigiKey UK's `£22` `< £65` shipping fee.
- **Pre-Crimped `22 AWG` JST-XH Pigtails (`HARN-01..02`):** Eliminates the need for a JST micro-crimper while keeping `J2/J3/J4` unplug-friendly for bench testing.

## 3. Verification Command

```bash
python3 bom/verify_bom.py
```
