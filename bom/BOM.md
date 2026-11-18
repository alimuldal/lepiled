# LepiLED DIY Maxi Switch — Itemized UK Bill of Materials (`bom/BOM.md`)

**Machine-Readable Source:** [`bom/bom.csv`](bom.csv)  
**Verification Script:** `python3 -B bom/verify_bom.py` (1:1 verified against `circuit_design/COMPONENT_IDS.csv` [71 RefDes], `pcb_design/driver_pcb_bom.csv` [71 RefDes], `pcb_design/driver_pcb_bom_pcba.csv` [61 On-PCB], `pcb_design/led_mcpcb_bom.csv` [`D_UV`/`D_VIS`], and `mechanical_design/MECH_PARTS.csv` [29 `MECH-*` IDs])  
**Currency & Tax Basis:** GBP (`£`), UK VAT = **20%** (`1 USD ≈ £0.76 GBP` reference for JLCPCB, queried 2026-11-18).

---

## 1. Table A — Build Tier Cost Comparison (Per-Lamp Amortized)

Two passive bottom-heatsink configurations share identical electronics (`71` RefDes), PCBs (`driver_pcb` + `4× led_mcpcb`), optics, enclosure, and end-cap architecture, differing **only** in `MECH-HS-EXT-BOT`:

| Build Configuration | Bottom Radiator (`MECH-HS-EXT-BOT`) | Thermal Qualification | Electrical (71 RefDes) | `PCB-01` Driver FR4 | Mechanical (`29 MECH-*` incl. `4× Al MCPCB`) | **Total ex VAT** | **Total inc 20% VAT** *(invoice / row-sum)* |
|---|---|---|---:|---:|---:|---:|---:|
| **Nominal-Mode Build (`Config C`)** *(~£100 R4 Target)* | `Fischer SK 578/50 SA` (`£5.88` ex VAT, `R = 8.5 mm` bot hub holes) | **16 / 20 PASS** (all **12/12** nominal cases `≤ 30 °C` pass w/ `+9.29 °C` margin; `4/4` `22 °C` DS fault pass; fails only `30 °C` DS-RealWPE/100% on `T_pcb_top_avg`) | £41.36 | £1.52 | £66.51 | **£109.39** | **£131.27** *(£131.23)* |
| **Worst-Case Thermal Upgrade (`Config A`)** *(Recommended Full-Corner Margin)* | `Fischer SK LED R 80 SA` (`£24.60` ex VAT, `1.35 K/W`, `R = 11.0 mm` bot hub holes) | **20 / 20 PASS** (all nominal + stacked `30 °C` Horizontal `DS-100%` fault corners pass: `T_j,UV = 85.6 °C < 100`, `T_pcb_top_avg = 53.7 °C ≤ 55`) | £41.36 | £1.52 | £85.23 | **£128.11** | **£153.73** *(£153.69)* |

> **Zero Double-Counting Note:** `led_mcpcb` (`PCB-02`, `4×` `20 × 80 × 1.6 mm` 1-layer Al MCPCB strips) is already costed under `MECH-10` (`MECH-MCPCB-1..4`, `£6.00` ex VAT amortized / `£7.50` 5-pc batch). `PCB-02` is retained in `bom/bom.csv` for 100% M2 Gerber traceability with `Include_In_Total = No` and `£0.00` so Al MCPCB cost is never counted twice.  
> *(Note on 4p VAT delta: UK VAT at invoice level is `round(£109.39 × 1.20, 2) = £131.27` vs `£131.23` when summing individually rounded 2p `0603` resistor lines.)*

---

## 2. Table B — Per-Lamp Amortized Cost vs. 1-Off UK DIY Checkout Outlay

Because UK distributors enforce minimum pack quantities (`5-pc` JLCPCB boards, `10×` Cut-Tape `0603`/`0805` passives, full aerosol cans, full thermal pad sheets, and fastener/O-ring multi-packs), a first-time single-lamp builder pays more at checkout than the amortized single-lamp material cost (and keeps usable spares for repairs or a second lamp).

| Cost Category / Pack-MOQ Driver | Amortized Unit Cost (ex VAT) | 1-Off DIY Checkout Outlay (ex VAT) | Pack / MOQ Reality & Spares Retained |
|---|---:|---:|---|
| **Active & Connector Semiconductors / Passives (`ELEC-01..37`)** | £41.36 | £43.66 | `10×` Cut-Tape packs on `R1..R2`, `R5..R20`, `C6..C12` add `+£2.30` ex VAT and leave `2–9×` spare passives per value |
| **Driver PCB Fab (`PCB-01`, `driver_pcb`)** | £1.52 | £7.60 | JLCPCB `5-pc` minimum (`£7.60` ex VAT incl. shipping share; `4` spare boards) |
| **Al MCPCB Fab (`MECH-10` / `MECH-MCPCB-1..4`)** | £6.00 | £7.50 | JLCPCB `5-pc` minimum (`£7.50` ex VAT; `4` used + `1` spare strip) |
| **Thermal Coating (`MECH-03` / `MECH-COAT-1`)** | £2.00 | £6.67 | Full `400 ml` VHT matte-black spray can (`£8.00` inc VAT) |
| **Glass & Cap VMQ70 O-Rings (`MECH-13`, `MECH-14`)** | £6.67 | £11.00 | Typically sold in `5-packs` (`68×3.5 mm` `£6.50` + `66×2.0 mm` `£4.50` ex VAT) |
| **IP68 M16 Cable Gland (`MECH-15` / `RS 669-4667`)** | £0.35 | £5.48 | Confirmed RS UK `06694667` sold only in **bag of 5** (`£5.48` ex VAT incl. locknuts) |
| **Hanging Hardware (`MECH-16` / `MECH-EYE-1`)** | £2.08 | £2.50 | `DIN 582` M6 lifting eye nut + `M6 × 75 mm` A2/A4 threaded stud (Accu UK) |
| **PCB Gap Pad (`MECH-18` / `RS 607-066`)** | £2.68 | £10.70 | Confirmed RS UK `0607066` sold as full `150 × 150 × 0.5 mm` `TG-A6200` sheet (yields ~12 pads) |
| **Fasteners & Heat-Set Inserts (`MECH-19..24`)** | £7.30 | £19.00 | Accu `10-packs` (`M2.5×6`, `M3×8`, `M3×14`, `M3×0.5`, `M4×16/40`) + CNC Kitchen `20–50 pk` `M3×5.7` inserts |
| **Kapton Tape, 22 AWG Silicone Wire & Nylon CSK Washers (`MECH-25`)** | £1.00 | £8.50 | Full roll Kapton + `22 AWG` wire reel/cut length + M4 nylon CSK washer pack |
| **All Other Single-Unit Mechanical Parts (`MECH-01,02,04,05,06..09,17`)** | £38.43 *(Nom)* / £57.15 *(Upg)* | £38.43 *(Nom)* / £57.15 *(Upg)* | Tube, core, top/bot heatsinks, Al plates/anchors, and `4 g` `Arctic MX-4` syringe (`1×` each) |
| **TOTAL — Nominal Build (`Config C`, excl. vendor shipping)** | **£109.39** *(£131.27 inc VAT)* | **£161.04** *(£193.25 inc VAT)* | Leaves `4×` spare FR4 PCBs, `1×` spare MCPCB, `4×` glands, `~11` pads of `TG-A6200`, spare passives/fasteners |
| **TOTAL — DS-100% Upgrade Build (`Config A`, excl. vendor shipping)** | **£128.11** *(£153.73 inc VAT)* | **£179.76** *(£215.71 inc VAT)* | Same spares plus `SK LED R 80 SA` (`£24.60` ex VAT) bottom heatsink |

---

## 3. Shipping, VAT & UK Order Consolidation Strategy

1. **DigiKey UK (`digikey.co.uk`) — `£65.00` Free-Shipping Threshold:**
   - Orders below `£65.00` incur a **`£22.00` delivery charge**. Always shop in GBP (`digikey.co.uk`) and select **UPS** (**DDP** — customs cleared cleanly; 20% UK VAT applies; avoid FedEx/DHL CPT).
   - A bare electrical order (`£43.66` ex VAT) is `£21.34` below `£65.00`. **Consolidation trick:** bundle `MECH-HS-EXT-TOP` (`SK 578/50 SA`, `£5.88`), a second `SK 578/50 SA` if building `Config C` (`£5.88`), spare `SST-10-UV` (`£4.32`) + `LM3410XMY` (`£2.35`), optional JST XH mating housings (`XHP-2`/`XHP-3`), and an equivalent DigiKey M16 gland / gap pad (`3M 5590H` / Bergquist `GP3000S30`) onto **one DigiKey UK cart** to clear `£65.00` and eliminate both DigiKey's `£22.00` and RS UK's `£9.50` small-order delivery fees.
2. **Mouser UK (`mouser.co.uk`) — `£65.00` Free-Shipping Threshold:**
   - Collects 20% UK VAT at checkout; useful alternate for `LM3410XMY/NOPB` (`£2.16`), `MF-LSMF500/16X` (`£0.98`), and `C&K 759D02000` (`£1.87`).
3. **RS Components UK (`uk.rs-online.com`) — `£60.00` ex VAT Private / `£50.00` Business (`£9.50` / `£8.50` below):**
   - Carries `RS 607-066` (`TG-A6200` `£10.70`) and `RS 669-4667` (`M16` 5-pack `£5.48`). Bundle with `22 AWG` silicone wire, Kapton tape, and/or USB cable / switch consumables if ordering from RS, or source `TG-A6200` / M16 gland on DigiKey/Farnell to avoid splitting orders.
4. **Farnell UK (`uk.farnell.com`) — `£40.00` ex VAT Free-Shipping Threshold (`£8.99` below £40):**
   - Stocks `JST SXH-001T-P0.6` loose crimps (`£0.0459`), Kapton tape, and active `Murata GRM188R71H104KA93D` (`£0.0146` 10+).
5. **JLCPCB (`jlcpcb.com`) — Global Standard Direct Line + IOSS 20% UK VAT:**
   - Upload **both** `pcb_design/gerbers/driver_pcb/driver_pcb_gerbers.zip` (2-layer FR4, `36 × 46 mm`) and `pcb_design/gerbers/led_mcpcb/led_mcpcb_gerbers.zip` (1-layer `1.0 W/m·K` Al MCPCB, `20 × 80 mm`, White LPI) in a **single combined order**.
   - Global Standard Direct Line shipping (`~£7.60–£8.00` for `< 0.5 kg`) splits across both PCB packs; JLCPCB collects **20% UK VAT at checkout** on `(PCB + Shipping)` via IOSS DDP for consignments `< £135`, avoiding Royal Mail `£8–£12` customs fees.
6. **CRH Supplies UK (`crhsupplies.com`) & Metals4U (`metals4u.co.uk`):**
   - Borosilicate 3.3 cylinder (`£12.50` inc VAT + `~£5–£7` UK glass courier) and cut-to-length `40 × 40 × 3 mm` Al 6063 box section (`£7.00` inc VAT + UK delivery).

---

## 4. Complete Itemized BOM

### 4.1 Electrical & UI Components (`71` RefDes in `39` Grouped Rows)

> **Al MCPCB Cross-Reference:** `D1..D4` (`ELEC-07`) map to `D_UV` and `D5..D8` (`ELEC-08..10`) map to `D_VIS` across the `4×` `led_mcpcb` strips (`MECH-MCPCB-1..4`). All other `61` `On-PCB` RefDes (`ELEC-01..06`, `11..35`, `38..39`) mount on `driver_pcb`, and `SW1`/`SW1_BOOT` (`ELEC-36..37`) are off-board panel-mounted in `MECH-CAP-BOT`.

| BOM_ID | RefDes (`COMPONENT_IDS.csv`) | Qty | Canonical MPN | Specification | UK Supplier | MOQ / Order Qty | Unit Amort £ (ex VAT) | Ext Amort £ (ex VAT) | Ext 1-Off £ (ex VAT) | Ext Amort £ (inc VAT) | Notes / Stocked Equivalent |
|---|---|---:|---|---|---|---|---:|---:|---:|---:|---|
| `ELEC-01` | `U1;U2` | 2 | `TI LM3410XMY/NOPB` | Boost CC IC, 1.6 MHz, MSOP-8-1EP | DigiKey UK | 1 / 2 | 2.350 | 4.70 | 4.70 | 5.64 | [Link](https://www.digikey.co.uk/en/products/result?keywords=LM3410XMY%2FNOPB); Mouser £2.16 |
| `ELEC-02` | `U3` | 1 | `TI TL431AIDBZR` | 2.495 V ±1% shunt ref, SOT-23-3 | DigiKey UK | 1 / 1 | 0.220 | 0.22 | 0.22 | 0.26 | [Link](https://www.digikey.co.uk/en/products/detail/texas-instruments/TL431AIDBZR/377309) |
| `ELEC-03` | `Q1A;Q1B` | 2 | `Diodes DMG2305UX-7` | -20 V / -4.2 A P-MOSFET, SOT-23-3 | DigiKey UK | 1 / 2 | 0.280 | 0.56 | 0.56 | 0.67 | [Link](https://www.digikey.co.uk/en/products/detail/diodes-incorporated/DMG2305UX-7/4514550) |
| `ELEC-04` | `Q2` | 1 | `onsemi MMBT3906LT1G` | -40 V / -200 mA PNP, SOT-23-3 | DigiKey UK | 1 / 1 | 0.110 | 0.11 | 0.11 | 0.13 | [Link](https://www.digikey.co.uk/en/products/detail/onsemi/MMBT3906LT1G/1479904) |
| `ELEC-05` | `Q3;Q4` | 2 | `onsemi MMBT3904LT1G` | 40 V / 200 mA NPN, SOT-23-3 | DigiKey UK | 1 / 2 | 0.110 | 0.22 | 0.22 | 0.26 | [Link](https://www.digikey.co.uk/en/products/detail/onsemi/MMBT3904LT1G/1479836) |
| `ELEC-06` | `F1` | 1 | `Bourns MF-LSMF500/16X` | 16 V / 5.0 A hold polyfuse, 2920 | DigiKey UK | 1 / 1 | 1.460 | 1.46 | 1.46 | 1.75 | [Link](https://www.digikey.co.uk/en/products/detail/bourns-inc/MF-LSMF500-16X-2/3858713); Mouser £0.98 |
| `ELEC-07` | `D1;D2;D3;D4` | 4 | `Luminus SST-10-UV-A130-G365-00` | 365 nm UV-A 3535 LED (`D_UV`) | DigiKey UK | 1 / 4 | 4.320 | 17.28 | 17.28 | 20.74 | [Link](https://www.digikey.co.uk/en/products/detail/luminus-devices-inc/SST-10-UV-A130-G365-00/10260429); **`BTM NOTCH=K`** |
| `ELEC-08` | `D5;D6` | 2 | `Cree XPEBRY-L1-0000-00S02` | 455 nm Royal Blue 3535 LED (`D_VIS`) | DigiKey UK | 1 / 2 | 1.400 | 2.80 | 2.80 | 3.36 | [Link](https://www.digikey.com/en/products/detail/cree-led/XPEBRY-L1-0000-00R02/5277158); use stocked `00R02`; **`BTM NOTCH=A`** |
| `ELEC-09` | `D7` | 1 | `Cree XPEBGR-L1-0000-00K01` | 528 nm Green 3535 LED (`D_VIS`) | DigiKey UK | 1 / 1 | 1.160 | 1.16 | 1.16 | 1.39 | [Link](https://www.digikey.com/en/products/detail/cree-led/XPEBGR-L1-0000-00F01/5277178); use stocked `00F01`; **`BTM NOTCH=A`** |
| `ELEC-10` | `D8` | 1 | `Cree XPEBWT-L1-0000-00H51` | 6200 K Cool White 3535 LED (`D_VIS`) | DigiKey UK | 1 / 1 | 0.870 | 0.87 | 0.87 | 1.04 | [Link](https://www.digikey.com/en/products/detail/cree-led/XPEBWT-L1-0000-00FE1/5859345); use stocked `00FE1`; **`BTM NOTCH=A`** |
| `ELEC-11` | `D9;D10` | 2 | `Diodes B340A-13-F` | 40 V / 3.0 A Schottky, SMA | DigiKey UK | 1 / 2 | 0.400 | 0.80 | 0.80 | 0.96 | [Link](https://www.digikey.co.uk/en/products/detail/diodes-incorporated/B340A-13-F/718228) |
| `ELEC-12` | `D11` | 1 | `Vishay SMBJ5.0A-E3/5B` | 5.0 V Vrwm / 600 W TVS, SMB | DigiKey UK | 1 / 1 | 0.420 | 0.42 | 0.42 | 0.50 | [Link](https://www.digikey.co.uk/en/products/detail/vishay-general-semiconductor-diodes-division/SMBJ5-0A-E3-5B/1236254) |
| `ELEC-13` | `D12` | 1 | `onsemi BAV70LT1G` | 100 V CC dual diode, SOT-23-3 | DigiKey UK | 1 / 1 | 0.090 | 0.09 | 0.09 | 0.11 | [Link](https://www.digikey.co.uk/en/products/result?keywords=BAV70LT1G) |
| `ELEC-14` | `D13;D14` | 2 | `Diodes BZT52C18-7-F` | 18 V / 500 mW OVP Zener, SOD-123 | DigiKey UK | 1 / 2 | 0.160 | 0.32 | 0.32 | 0.38 | [Link](https://www.digikey.co.uk/en/products/detail/diodes-incorporated/BZT52C18-7-F/717900) |
| `ELEC-15` | `D15` | 1 | `Diodes BZT52C5V6-7-F` | 5.6 V / 500 mW VGS Zener, SOD-123 | DigiKey UK | 1 / 1 | 0.160 | 0.16 | 0.16 | 0.19 | [Link](https://www.digikey.co.uk/en/products/detail/diodes-incorporated/BZT52C5V6-7-F/717937) |
| `ELEC-16` | `D16` | 1 | `onsemi BAW56LT1G` | 70 V CA dual diode, SOT-23-3 | DigiKey UK | 1 / 1 | 0.090 | 0.09 | 0.09 | 0.11 | [Link](https://www.digikey.co.uk/en/products/detail/onsemi/BAW56LT1G/1479901) |
| `ELEC-17` | `L1;L2` | 2 | `Bourns SRN6045-100M` | 10 µH ±20%, Isat=3.0 A, 6×6×4.5 | DigiKey UK | 1 / 2 | 0.320 | 0.64 | 0.64 | 0.77 | [Link](https://www.digikey.co.uk/en/products/detail/bourns-inc/SRN6045-100M/3807218) |
| `ELEC-18` | `R1;R2` | 2 | `Vishay CRCW08055K10FKEA` | 5.1 kΩ ±1%, 0805 | DigiKey UK | 10 / 10 | 0.030 | 0.06 | 0.30 | 0.07 | [Link](https://www.digikey.co.uk/en/products/result?keywords=CRCW08055K10FKEA) |
| `ELEC-19` | `R3;R4` | 2 | `Bourns CRL1206-FW-R560ELF` | 0.56 Ω ±1%, 0.50 W, 1206 | DigiKey UK | 1 / 2 | 0.160 | 0.32 | 0.32 | 0.38 | [Link](https://www.digikey.com/en/products/detail/bourns-inc/CRL1206-FW-R560ELF/13531393) |
| `ELEC-20` | `R5;R6;R7;R10;R13;R15;R17` | 7 | `Vishay CRCW060310K0FKEA` | 10 kΩ ±1%, 0.1 W, 0603 | DigiKey UK | 10 / 10 | 0.024 | 0.17 | 0.24 | 0.20 | [Link](https://www.digikey.co.uk/en/products/result?keywords=CRCW060310K0FKEA) |
| `ELEC-21` | `R8;R9` | 2 | `Vishay CRCW0603100RFKEA` | 100 Ω ±1%, 0.1 W, 0603 | DigiKey UK | 10 / 10 | 0.024 | 0.05 | 0.24 | 0.06 | [Link](https://www.digikey.co.uk/en/products/result?keywords=CRCW0603100RFKEA) |
| `ELEC-22` | `R11` | 1 | `Vishay CRCW06031K50FKEA` | 1.5 kΩ ±1%, 0.1 W, 0603 | DigiKey UK | 10 / 10 | 0.024 | 0.02 | 0.24 | 0.02 | [Link](https://www.digikey.co.uk/en/products/result?keywords=CRCW06031K50FKEA) |
| `ELEC-23` | `R12` | 1 | `Vishay CRCW060313K7FKEA` | 13.7 kΩ ±1%, 0.1 W, 0603 | DigiKey UK | 10 / 10 | 0.024 | 0.02 | 0.24 | 0.02 | [Link](https://www.digikey.co.uk/en/products/result?keywords=CRCW060313K7FKEA) |
| `ELEC-24` | `R14` | 1 | `Vishay CRCW0603220KFKEA` | 220 kΩ ±1%, 0.1 W, 0603 | DigiKey UK | 10 / 10 | 0.024 | 0.02 | 0.24 | 0.02 | [Link](https://www.digikey.co.uk/en/products/result?keywords=CRCW0603220KFKEA) |
| `ELEC-25` | `R16` | 1 | `Vishay CRCW06035K60FKEA` | 5.6 kΩ ±1%, 0.1 W, 0603 | DigiKey UK | 10 / 10 | 0.024 | 0.02 | 0.24 | 0.02 | [Link](https://www.digikey.co.uk/en/products/result?keywords=CRCW06035K60FKEA) |
| `ELEC-26` | `R18` | 1 | `Vishay CRCW0603220RFKEA` | 220 Ω ±1%, 0.1 W, 0603 | DigiKey UK | 10 / 10 | 0.024 | 0.02 | 0.24 | 0.02 | [Link](https://www.digikey.co.uk/en/products/result?keywords=CRCW0603220RFKEA) |
| `ELEC-27` | `R19` | 1 | `Vishay CRCW060368K0FKEA` | 68.0 kΩ ±1%, 0.1 W, 0603 | DigiKey UK | 10 / 10 | 0.024 | 0.02 | 0.24 | 0.02 | [Link](https://www.digikey.co.uk/en/products/result?keywords=CRCW060368K0FKEA) |
| `ELEC-28` | `R20` | 1 | `Vishay CRCW0603100KFKEA` | 100 kΩ ±1%, 0.1 W, 0603 | DigiKey UK | 10 / 10 | 0.024 | 0.02 | 0.24 | 0.02 | [Link](https://www.digikey.co.uk/en/products/result?keywords=CRCW0603100KFKEA) |
| `ELEC-29` | `C1;C2;C3` | 3 | `Murata GRM31CR71E106KA12L` | 10 µF ±10% 25 V X7R, 1206 | DigiKey UK | 1 / 3 | 0.260 | 0.78 | 0.78 | 0.94 | [Link](https://www.digikey.com/en/products/detail/murata-electronics/GRM31CR71E106KA12L/3836109) |
| `ELEC-30` | `C4;C5` | 2 | `Samsung CL32B106KBJNFNE` | 10 µF ±10% 50 V X7R, 1210 | DigiKey UK | 1 / 2 | 0.520 | 1.04 | 1.04 | 1.25 | [Link](https://www.digikey.com/en/products/detail/samsung-electro-mechanics/CL32B106KBJNNNE/3889156); `-FNE` OOS → use stocked `CL32B106KBJNNNE` |
| `ELEC-31` | `C6;C7;C8;C11;C12` | 5 | `Murata GRM188R71E104KA01D` | 100 nF ±10% 25 V X7R, 0603 | DigiKey UK | 10 / 10 | 0.020 | 0.10 | 0.20 | 0.12 | [Link](https://www.digikey.co.uk/en/products/result?keywords=GRM188R71E104KA01D); 50 V `GRM188R71H104KA93D` also fits |
| `ELEC-32` | `C9;C10` | 2 | `Murata GRM188R71H104KA93D` | 100 nF ±10% 50 V X7R, 0603 | DigiKey UK | 10 / 10 | 0.020 | 0.04 | 0.20 | 0.05 | [Link](https://www.digikey.co.uk/en/products/detail/murata-electronics/GRM188R71H104KA93D/4844391); Farnell 10+ £0.0146 |
| `ELEC-33` | `J1` | 1 | `GCT USB4085-GF-A` | 5.0 A VBUS 16-pin TH USB-C | DigiKey UK | 1 / 1 | 0.680 | 0.68 | 0.68 | 0.82 | [Link](https://www.digikey.co.uk/en/products/detail/gct/USB4085-GF-A/9863435) |
| `ELEC-34` | `J2;J3` | 2 | `JST B2B-XH-A` | 2-pin 2.50 mm TH header, 3 A | DigiKey UK | 1 / 2 | 0.070 | 0.14 | 0.14 | 0.17 | [Link](https://www.digikey.co.uk/en/products/detail/jst-sales-america-inc/B2B-XH-A/608775) |
| `ELEC-35` | `J4` | 1 | `JST B3B-XH-A` | 3-pin 2.50 mm TH header, 3 A | DigiKey UK | 1 / 1 | 0.100 | 0.10 | 0.10 | 0.12 | [Link](https://www.digikey.co.uk/en/products/detail/jst-sales-america-inc/B3B-XH-A/608777) |
| `ELEC-36` | `SW1` | 1 | `E-Switch 100SP3T1B1M1QEH` | SPDT On-Off-On toggle, 5 A, 1/4-40 | DigiKey UK | 1 / 1 | 3.980 | 3.98 | 3.98 | 4.78 | [Link](https://www.digikey.co.uk/en/products/detail/e-switch/100SP3T1B1M1QEH/378893) |
| `ELEC-37` | `SW1_BOOT` | 1 | `C&K 759D02000` | Waterproof silicone boot, 1/4-40 | DigiKey UK | 1 / 1 | 1.860 | 1.86 | 1.86 | 2.23 | [Link](https://www.digikey.co.uk/en/products/detail/c-k/759D02000/1007062); Mouser £1.87 |
| `ELEC-38` | `TP1;TP2` | 2 | `Custom TH Pad` | 2.5 mm pad / 1.3 mm drill TH | PCB Feature | 1 / 2 | 0.000 | 0.00 | 0.00 | 0.00 | Integrated on `driver_pcb` (`Include_In_Total=No`) |
| `ELEC-39` | `H1;H2;H3;H4` | 4 | `M2.5 Mounting Hole` | 2.7 mm drill / 5.5 mm pad GND | PCB Feature | 1 / 4 | 0.000 | 0.00 | 0.00 | 0.00 | Integrated on `driver_pcb` (`Include_In_Total=No`) |
| **Subtotal** | **71 RefDes** | **71** | — | — | — | — | — | **£41.36** | **£43.66** | **£49.59** *(inv £49.63)* | **1-Off inc VAT = £52.39 (inv) / £52.40 (row)** |

### 4.2 PCB Fabrication Packages (`2` Gerber Sets)

| BOM_ID | Source | Qty | Description | UK Supplier | MOQ / Order Qty | Unit Amort £ (ex VAT) | Ext Amort £ (ex VAT) | Ext 1-Off £ (ex VAT) | Ext Amort £ (inc VAT) | Notes |
|---|---|---:|---|---|---|---:|---:|---:|---:|---|
| `PCB-01` | `driver_pcb` | 1 | Custom 2-layer FR4 `36.0 × 46.0 mm`, `1.6 mm`, `1 oz` | [JLCPCB](https://jlcpcb.com/) | 5 / 5 | 1.520 | 1.52 | 7.60 | 1.82 | `1/5` of `£7.60` batch w/ Global Direct ship share (1-off inc VAT `£9.12`) |
| `PCB-02` | `led_mcpcb` | 4 | Custom 1-layer Al MCPCB `20.0 × 80.0 mm`, `1.0 W/m·K` | [JLCPCB](https://jlcpcb.com/) | 5 / 5 | 0.000 | 0.00 | 0.00 | 0.00 | **Excluded (`Include_In_Total=No`); costed in `MECH-10` (`MECH-MCPCB-1..4`)** |

### 4.3 Mechanical, Thermal & Enclosure Parts (`29 MECH-*` IDs + `NOMINAL_ALT`)

| BOM_ID | Source_IDs | Tier | Qty | Part / MPN | UK Supplier | MOQ / Order Qty | Unit Amort £ (ex VAT) | Ext Amort £ (ex VAT) | Ext 1-Off £ (ex VAT) | Ext Amort £ (inc VAT) | Notes |
|---|---|---|---:|---|---|---|---:|---:|---:|---:|---|
| `MECH-01` | `MECH-TUBE-1` | `CORE` | 1 | CRH Supplies 75/68/3.5 × 150 mm Borosilicate 3.3 | [CRH Supplies UK](https://www.crhsupplies.com/) | 1 / 1 | 10.420 | 10.42 | 10.42 | 12.50 | ~90% UV-A @ 365 nm; ±1.0 mm length; +UK glass courier |
| `MECH-02` | `MECH-HS-CORE` | `CORE` | 1 | 6063-T6 Al Box Tube `40×40×3 × 165.0 mm` | [Metals4U](https://www.metals4u.co.uk/aluminium-40mm-x-40mm-x-3mm-box-section) | 1 / 1 | 5.830 | 5.83 | 5.83 | 7.00 | Cut-to-length UK stock |
| `MECH-03` | `MECH-COAT-1` | `CORE` | 1 | Matte-Black High-Emissivity Enamel (`ε = 0.88`) | [Halfords](https://www.halfords.com/) / Toolstation | 1 / 1 | 2.000 | 2.00 | 6.67 | 2.40 | 1/4 share vs full `400 ml` spray can (`£8.00` inc VAT) |
| `MECH-04` | `MECH-HS-EXT-TOP` | `CORE` | 1 | `Fischer SK 578/50 SA` (`Ø60 × 50 mm`) | [DigiKey UK](https://www.digikey.co.uk/en/products/detail/fischer-elektronik/SK-578-50-SA/3229101) | 1 / 1 | 5.880 | 5.88 | 5.88 | 7.06 | Drill `Ø6.5` center + `4× M3` @ `R=8.5 mm` |
| `MECH-05A` | `MECH-HS-EXT-BOT` | `UPGRADE_ONLY` | 1 | `Fischer SK LED R 80 SA` (`Ø80 × 70 mm`, `1.35 K/W`) | [TME UK](https://www.tme.eu/gb/details/sk_led_r_80_sa/heatsinks/fischer-elektronik/sk-led-r-80-sa/) | 1 / 1 | 24.600 | 24.60 | 24.60 | 29.52 | **Config A** (`20/20` thermal pass); drill `4× M3` @ `R=11.0 mm` |
| `MECH-05C` | `MECH-HS-EXT-BOT-NOM` | `NOMINAL_ALT` | 1 | `Fischer SK 578/50 SA` (`Ø60 × 50 mm`) | [DigiKey UK](https://www.digikey.co.uk/en/products/detail/fischer-elektronik/SK-578-50-SA/3229101) | 1 / 1 | 5.880 | 5.88 | 5.88 | 7.06 | **Config C** nominal-only alt; drill `MECH-ADAPT-BOT` @ `R=8.5 mm` |
| `MECH-06` | `MECH-ADAPT-TOP` | `CORE` | 1 | Al 6061-T6 Disc `Ø76 × 3.0 mm` | [eBay UK](https://www.ebay.co.uk/) / Al Online | 1 / 1 | 1.670 | 1.67 | 1.67 | 2.00 | Bridges core + `MECH-CAP-TOP` to `SK 578/50 SA` |
| `MECH-07` | `MECH-ADAPT-BOT` | `CORE` | 1 | Al 6061-T6 `Ø90×3` + `Ø59×5 mm` Pedestal | [eBay UK](https://www.ebay.co.uk/) / Al Online | 1 / 1 | 2.500 | 2.50 | 2.50 | 3.00 | `1.8 mm` Kapton pockets; no-mill `3+2+3 mm` stack alt `<0.03 K/W` |
| `MECH-08` | `MECH-ANCHOR-BOT` | `CORE` | 1 | Al 6061-T6 Block `33.2 × 33.2 × 12.0 mm` | [eBay UK](https://www.ebay.co.uk/) / Al Online | 1 / 1 | 1.250 | 1.25 | 1.25 | 1.50 | Cross-pinned inside core; `2× M4` vertical tapped |
| `MECH-09` | `MECH-ANCHOR-TOP` | `CORE` | 1 | Al 6061-T6 Block `33.2 × 33.2 × 14.0 mm` | [eBay UK](https://www.ebay.co.uk/) / Al Online | 1 / 1 | 1.250 | 1.25 | 1.25 | 1.50 | `M6` tapped + `2× M4` cross-pins; 100% metal load path |
| `MECH-10` | `MECH-MCPCB-1..4` | `CORE` | 4 | Custom JLCPCB `20×80×1.6 mm` Al MCPCB (`led_mcpcb`) | [JLCPCB](https://jlcpcb.com/) | 5 / 5 | 1.500 | 6.00 | 7.50 | 7.20 | `5-pc` min (`£7.50` ex VAT = 4 used + 1 spare); mounts `D1..D8` |
| `MECH-11` | `MECH-CAP-BOT` | `CORE` | 1 | 3D-Printed Bottom End Cap (`mech_cap_bot*.step/.stl`) | [DIY / JLC3DP](https://jlc3dp.com/) | 1 / 1 | 0.000 | 0.00 | 0.00 | 0.00 | **Excluded per R4** (`PETG/ASA` FDM or `PA12` SLS) |
| `MECH-12` | `MECH-CAP-TOP` | `CORE` | 1 | 3D-Printed Top End Cap (`mech_cap_top*.step/.stl`) | [DIY / JLC3DP](https://jlc3dp.com/) | 1 / 1 | 0.000 | 0.00 | 0.00 | 0.00 | **Excluded per R4** (`PETG/ASA` FDM or `PA12` SLS) |
| `MECH-13` | `MECH-GASKET-1;2` | `CORE` | 2 | Silicone VMQ70 O-Ring `68 mm ID × 3.5 mm CS` | [Polymax UK](https://www.polymax.co.uk/o-rings/) / Simply Bearings | 5 / 5 | 2.500 | 5.00 | 6.50 | 6.00 | Glass end seals; `BS231` (`66.27×3.53 mm` VMQ70) fits as OTS alt |
| `MECH-14` | `MECH-GASKET-3` | `CORE` | 1 | Silicone VMQ70 O-Ring `66 mm ID × 2.0 mm CS` | [Polymax UK](https://www.polymax.co.uk/o-rings/) / Simply Bearings | 5 / 5 | 1.670 | 1.67 | 4.50 | 2.00 | Bottom PCB cavity V-roof seal |
| `MECH-15` | `MECH-GLAND-1` | `CORE` | 1 | M16×1.5 Black Nylon IP68 Gland + Locknut | [RS UK 669-4667](https://uk.rs-online.com/web/p/cable-glands/06694667) | 5 / 5 | 0.350 | 0.35 | 5.48 | 0.42 | Verified RS UK bag of 5 (`£5.48` ex VAT); Option A baseline |
| `MECH-16` | `MECH-EYE-1` | `CORE` | 1 | M6 × 75 mm Stainless Eye Bolt + Washer | [Accu UK](https://www.accu.co.uk/) | 1 / 1 | 2.080 | 2.08 | 2.50 | 2.50 | Accu UK alt: `DIN 582 M6` eye nut + `M6 × 75 mm` stud |
| `MECH-17` | `MECH-TIM-1` | `CORE` | 1 | `Arctic MX-4` Thermal Compound (`4 g` syringe) | [Scan UK](https://www.scan.co.uk/) / Overclockers | 1 / 1 | 3.750 | 3.75 | 3.75 | 4.50 | Scan `£3.32` / OCUK `£4.16` ex VAT; covers all joints |
| `MECH-18` | `MECH-TIM-PCB` | `CORE` | 1 | `TGlobal TG-A6200-150-0.5` (`6.2 W/m·K`, cut `34×44`) | [RS UK 607-066](https://uk.rs-online.com/web/p/thermal-pads/0607066) | 1 / 1 | 2.680 | 2.68 | 10.70 | 3.22 | 1/4 share vs full `150×150 mm` RS UK sheet (`£10.70` ex VAT) |
| `MECH-19` | `MECH-FAST-1` | `CORE` | 8 | `M3 × 8 mm` A2 DIN 912 SHCS + M3 Nuts/Washers | [Accu UK](https://www.accu.co.uk/) | 10 / 10 | 0.150 | 1.20 | 2.00 | 1.44 | Secures `MECH-MCPCB-1..4` (`Ø5.5 < 6.0 mm` keepout) |
| `MECH-20` | `MECH-FAST-2` | `CORE` | 4 | `M2.5 × 6 mm` A2 SHCS + Nylon Shoulder Washers | [Accu UK](https://www.accu.co.uk/) | 10 / 10 | 0.250 | 1.00 | 3.00 | 1.20 | **`6 mm` mandatory** (`0.0 mm` fin protrusion) |
| `MECH-21` | `MECH-FAST-3` | `CORE` | 8 | `M3 × 8 mm` A2 SHCS + `M3×5.7 mm` Brass Inserts | [Accu UK](https://www.accu.co.uk/) / CNC Kitchen | 20 / 20 | 0.250 | 2.00 | 6.50 | 2.40 | **`8 mm` mandatory** (`1.7–2.2 mm` blind-hole clearance) |
| `MECH-22` | `MECH-FAST-3W` | `CORE` | 4 | `M3 × 0.5 mm` A2 DIN 988 Shim Washers | [Accu UK](https://www.accu.co.uk/) | 10 / 10 | 0.100 | 0.40 | 1.50 | 0.48 | Creates `0.5 mm` air gap on flat `MECH-CAP-TOP` |
| `MECH-23` | `MECH-FAST-4` | `CORE` | 8 | `4× M3×14` + `4× M3×8` DIN 7991 CSK A2 | [Accu UK](https://www.accu.co.uk/) | 10 / 10 | 0.150 | 1.20 | 2.50 | 1.44 | Flush CSK heads for `MECH-ADAPT-BOT` / `TOP` |
| `MECH-24` | `MECH-FAST-5` | `CORE` | 6 | `2× M4×16` + `4× M4×40` DIN 7991 CSK A2 | [Accu UK](https://www.accu.co.uk/) | 10 / 10 | 0.250 | 1.50 | 3.50 | 1.80 | Bulkhead tension bolts + top/bot anchor cross-pins |
| `MECH-25` | `MECH-MISC-1` | `CORE` | 1 | Kapton Tape + `2× M4` Nylon CSK Washers + `22 AWG` Wire | [Farnell UK](https://uk.farnell.com/) / eBay UK | 1 / 1 | 1.000 | 1.00 | 8.50 | 1.20 | Pocket insulation + thermal bulkhead isolation + LED wire |

---

## 5. Optional / Uncatalogued Harness & Power Cable Accessories

These mating cable-side items are required during wiring (unless soldering leads directly) and are documented here rather than in `bom.csv` so `bom.csv` maintains exact 1:1 ID parity with `COMPONENT_IDS.csv` (`71`) and `MECH_PARTS.csv` (`29`):

| Accessory | Mates With | Qty | Typical UK Supplier & Est. Cost (ex VAT) | Notes |
|---|---|---:|---|---|
| **JST `XHP-2`** 2-pin housing | `J2`, `J3` (`B2B-XH-A`) | 2 | DigiKey UK (`~£0.07/ea`) | Or pre-crimped JST-XH 2-pin `22 AWG` pigtails |
| **JST `XHP-3`** 3-pin housing | `J4` (`B3B-XH-A`) | 1 | DigiKey UK (`~£0.07/ea`) | Or pre-crimped JST-XH 3-pin `24 AWG` pigtail |
| **JST `SXH-001T-P0.6`** crimp contacts | `XHP-2`, `XHP-3` | 7 | Farnell UK (`£0.0459/ea`, loose cut-strip; DigiKey is 8k reel) | Requires JST/Engineer PA-09 crimp tool |
| **Option A Power Cable (`M16_GLAND`)** | `TP1`/`TP2` + `MECH-GLAND-1` | 1 | `18 AWG ≤ 1.0 m` heavy-duty USB-A pigtail (`~£2–£4`) | Outer jacket `4–8 mm` for M16 IP68 seal; `R_cable ≤ 0.048 Ω @ 55 °C` |
| **Option B Power Cable (`USB_C`)** | `J1` (`USB4085-GF-A`) | 1 | **Extended-barrel USB-C (`≥ 12.31 mm` / `13.0 mm` tip)** (`~£5–£9`) | **`mech_cap_bot_usbc` stop is at `Y = -33.10 mm`: standard `6.65 mm` plugs CANNOT mate!** Must also satisfy `R_cable ≤ 0.018 Ω` (`18 AWG ≤ 0.4 m` or `16 AWG ≤ 0.65 m`) |

---

## 6. UK Stocking & Sourcing Notes

1. **Cree XP-E2 Stocked Bin Equivalents (`ELEC-08..10`):** The exact bin suffixes in `COMPONENT_IDS.csv` (`XPEBRY-L1-0000-00S02`, `XPEBGR-L1-0000-00K01`, `XPEBWT-L1-0000-00H51`) are factory lead-time on UK distributors; identical-package/optical-class **in-stock UK Cut-Tape** replacements in the same `XLamp-XPE2.pdf` family are **`XPEBRY-L1-0000-00R02`** (`£1.40`), **`XPEBGR-L1-0000-00F01`** (`£1.16`), and **`XPEBWT-L1-0000-00FE1`** (`£0.87`).
2. **Output MLCC `C4`/`C5` (`ELEC-30`):** `Samsung CL32B106KBJNFNE` is out of stock under `-FNE`; **`CL32B106KBJNNNE`** is the exact `10 µF 50 V X7R 1210` in-stock Samsung replacement (`780,000+` units in stock at DigiKey UK, `£0.52`).
3. **`100 nF 0603` MLCC (`ELEC-31..32`):** `Murata GRM188R71E104KA01D` (`25 V`) can be unified with `GRM188R71H104KA93D` (`50 V`, used on `C9/C10`, active and stocked at `£0.0146–£0.020/ea` in `10+` breaks).
4. **O-Rings (`MECH-13`, `MECH-14`):** `Simply Bearings` stocks `68 × 3.0` and `66 × 1.5` online rather than `68 × 3.5` / `66 × 2.0`; order exact VMQ70 sizes from UK seal specialists (`Polymax UK`, `M Barnwell`), or use standard off-the-shelf **`BS231` (`66.27 × 3.53 mm` VMQ70)** as a drop-in axial face-seal substitute for `68 × 3.5 mm`.
5. **Hanging Eye Bolt (`MECH-16`):** Accu UK does not stock a monolithic `M6 × 75 mm` long-shank eye bolt; order a **`DIN 582 M6` A4 lifting eye nut + `M6 × 75 mm` A2/A4 threaded stud** (with threadlocker) from Accu UK (`~£2.50` ex VAT).
6. **`Fischer SK 578/50 SA` (`MECH-04` / `MECH-05C`):** DigiKey UK Marketplace (`5496-SK57850SA-ND`, part ID `3229101`) pricing fluctuates dynamically with FX/stock (`~£5.88–£12.00` ex VAT).

---

## 7. Requirement R4 Exclusions

Per **Requirement R4**, the following are **excluded** from the ~£100 lamp-parts BOM (`£0.00` / `Include_In_Total = No`):
- **External `5 V` USB Power Bank** (must deliver **`≥ 4.85 V` @ `≥ 3 A`** continuous for Option A, or `≥ 4.90 V` @ `≥ 3.5 A` for Option B; `10.74 W` in `8-ALL` vs `5.54 W` in `4-UV`).
- **3D-Printed End-Caps & Filament/Sintering Consumables** (`MECH-CAP-BOT`, `MECH-CAP-TOP` in `PETG`/`ASA` FDM or `PA12` SLS).
