# LepiLED DIY Maxi Switch — Master Bill of Materials (Rev 4.0 / Option 2)

Machine-verified master BOM in [bom.csv](file:///home/alimuldal/src/lepiled/bom/bom.csv), audited 1:1 against [COMPONENT_IDS.csv](file:///home/alimuldal/src/lepiled/circuit_design/COMPONENT_IDS.csv) (72 RefDes), [driver_pcb_bom_pcba.csv](file:///home/alimuldal/src/lepiled/pcb_design/driver_pcb_bom_pcba.csv) (56 populated PCBA parts), [led_mcpcb_bom.csv](file:///home/alimuldal/src/lepiled/pcb_design/led_mcpcb_bom.csv) (4× MCPCB LEDs), and [MECH_PARTS.csv](file:///home/alimuldal/src/lepiled/mechanical_design/MECH_PARTS.csv) (29 mechanical parts) via [verify_bom.py](file:///home/alimuldal/src/lepiled/bom/verify_bom.py).

## 1. Cost Summary (Lamp Parts Only, UK GBP)

Pivoting to **Option 2 (`20 V` USB-C PD + dual `AL8860WT-7` buck drivers)** cuts driver PCB heat dissipation from `1.60 W` nom / `4.39 W` max down to **`0.50 W` nom / `0.82 W` max** (`94.3%` system efficiency). That allows a matching `£5.88` **`Fischer SK 578/50 SA`** bottom heatsink to pass **20/20** thermal cases (eliminating the `£24.60` `SK LED R 80 SA` upgrade) and saves **`£21.30` ex-VAT (`£25.56` inc-VAT)** while adding JST-XH mating harness plugs and crimps.

| Domain | Amortized Per-Lamp (ex-VAT) | Amortized Per-Lamp (inc 20% VAT) | 1-Off MOQ Packs (ex-VAT) | 1-Off MOQ Packs (inc 20% VAT) |
|---|---:|---:|---:|---:|
| **Electrical (72 RefDes: 56 PCBA + 10 Off-Board + 6 PCB features)** | £39.22 | £47.06 | £43.06 | £51.67 |
| **Harness (`2× XHP-2`, `1× XHP-3`, `10× SXH-001T-P0.6` crimps)** | £0.43 | £0.52 | £0.52 | £0.62 |
| **PCB Fabrication (`driver_pcb` 2L FR4; `led_mcpcb` in Mechanical)** | £1.52 | £1.82 | £7.60 | £9.12 |
| **Mechanical (Unified Dual `SK 578/50 SA`, Borosilicate, Core, Hardware)** | £66.51 | £79.81 | £109.78 | £131.74 |
| **TOTAL Rev 4.0 Lamp Build (Lamp Parts Only)** | **£107.68** | **£129.22** | **£160.96** | **£193.15** |

> **Scope Notes:** Per project rules, 3D-printed end caps (`MECH-CAP-BOT`, `MECH-CAP-TOP`) are £0.00 (printed in-house on user's FDM/SLS printers), and external power sources (laptop USB-C PD charger, 20 V PD power bank, or 18–24 V battery) plus UK shipping are excluded from lamp-parts totals. `PCB-02` (`led_mcpcb`) is cross-referenced at £0.00 to `MECH-10` (`£6.00` amort / `£7.50` 5-pc batch) to prevent double-counting.

## 2. Key Option 2 Updates vs Legacy 5 V Boost Build

- **Driver & PD Silicone (`ELEC-01..07`):** Dual `Diodes AL8860WT-7` (`£0.55` ea) replace dual `LM3410XMY` (`£2.35` ea); `Diodes AP33771CFBZ-13-FA02` negotiates `20 V / 1.0 A` USB-C PD; `TI LM393BIDR` + `LM4040BIM3-2.5/NOPB` implement the `17.25 V` hardware UVLO; `2× DMN3404L-7` back-to-back N-MOSFETs block Aux DC back-feed; `2× Bourns MF-MSMF150/24X` (`1812`) protect USB-C and Aux DC entries.
- **Stocked LED MPNs (`ELEC-08..11`):** Updated to actively stocked DigiKey UK Cree `XP-E2` bins (`XPEBRY-L1-0000-00R02`, `XPEBGR-L1-0000-00F01`, `XPEBWT-L1-0000-00F51`) alongside `4× Luminus SST-10-UV-A130-G365-00`.
- **Consolidated Passives & Mating Harness (`ELEC-32`, `HARN-01..03`):** `C1, C4, C5, C11, C12` consolidated onto a single 10-pack of `1.0 µF 50 V X7R 0805` (`GRM21BR71H105KA12L`); `JST XHP-2`, `XHP-3`, and `SXH-001T-P0.6` crimp contacts explicitly included.
- **Mechanical Cost & Fastener Fixes (`MECH-05`, `MECH-20`):** Unified `2× Fischer SK 578/50 SA` (`£5.88` ea) for top and bottom heatsinks; `MECH-FAST-2` corrected to flat M2.5 nylon washers (`Ø5.0 mm OD`) matching the `Ø2.7 mm` `H1..H4` mounting holes.

## 3. Recommended External Power Accessories (Not in Lamp-Parts Total)

- **Bench Validation:** Any standard `45–100 W` USB-C PD laptop charger (e.g., MacBook / ThinkPad / Dell / Anker USB-C PD brick) with a standard `60 W+` USB-C to USB-C cable (`6.65 mm` plug mates directly into `mech_cap_bot_usbc`).
- **Field Use:** Any `20 V`-capable USB-C PD power bank (`>= 45 W` / `>= 65 W`, e.g., Anker / INIU / Baseus `20,000 mAh / 74 Wh` -> `~7.5 h` in 8-ALL or `~14 h` in 4-UV) OR any `5S–6S` Li-ion / `18–20 V` power-tool battery pack wired into `TP1/TP2` through the `MECH-GLAND-1` M16 IP68 gland.

## 4. Verification Command

```bash
python3 bom/verify_bom.py
```
