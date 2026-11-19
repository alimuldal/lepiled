# LepiLED DIY Maxi Switch — Master Bill of Materials (Rev 4.1)

Machine-verified master BOM in [bom.csv](file:///home/alimuldal/src/lepiled/bom/bom.csv), audited 1:1 against [COMPONENT_IDS.csv](file:///home/alimuldal/src/lepiled/circuit_design/COMPONENT_IDS.csv) (`75` RefDes), [driver_pcb_bom_pcba.csv](file:///home/alimuldal/src/lepiled/pcb_design/driver_pcb_bom_pcba.csv) (`61` populated PCBA parts), [led_mcpcb_bom.csv](file:///home/alimuldal/src/lepiled/pcb_design/led_mcpcb_bom.csv) (`4`-row color-split MCPCB LEDs), and [MECH_PARTS.csv](file:///home/alimuldal/src/lepiled/mechanical_design/MECH_PARTS.csv) (`27` mechanical IDs) via [verify_bom.py](file:///home/alimuldal/src/lepiled/bom/verify_bom.py).

## 1. Cost Summary (Lamp Parts Only, UK GBP)

Rev 4.1 combines the **Option 2 (`20 V` USB-C PD + dual `AL8860WT-7` buck)** electronics architecture (`0.55 W` nominal / `0.80 W` max PCB loss) with three user-approved simplifications (**S1-A** top-heatsink-only with zero CNC milling, **S2-A** USB-C only, and **S3** direct gold `DPDT On-On-On` switch) plus an off-the-shelf `£0.30` `20 mm` rubber membrane grommet. That brings the complete lamp-parts build **below `£100` ex-VAT** amortized (`£9.19` ex-VAT / `£11.03` inc-VAT lower than Rev 4.0, and `£13.87` ex-VAT lower in 1-off MOQ checkout cost).

| Domain | Amortized Per-Lamp (ex-VAT) | Amortized Per-Lamp (inc 20% VAT) | 1-Off MOQ Packs (ex-VAT) | 1-Off MOQ Packs (inc 20% VAT) |
|---|---:|---:|---:|---:|
| **Electrical (`75` RefDes: `61` PCBA + `10` Off-Board + `4` NPTH)** | £41.06 | £49.27 | £45.35 | £54.42 |
| **Harness (`2× XHP-2`, `1× XHP-3`, `10× SXH-001T-P0.6` crimps)** | £0.43 | £0.52 | £0.52 | £0.62 |
| **PCB Fabrication (`driver_pcb` 2L FR4 `ENIG`; `led_mcpcb` in Mechanical)** | £2.20 | £2.64 | £11.00 | £13.20 |
| **Mechanical (`S1-A` Top `SK 578/50 SA` Only, Zero CNC Milling, `27` IDs)** | £54.80 | £65.76 | £90.22 | £108.26 |
| **TOTAL Rev 4.1 Lamp Build (Lamp Parts Only)** | **£98.49** | **£118.19** | **£147.09** | **£176.51** |

> **Scope Notes:** 3D-printed enclosure parts (`MECH-LID-BOT`, `MECH-CAP-BOT`, `MECH-CAP-TOP`) are £0.00 (printed in-house in PETG/ASA FDM or PA12 SLS), and external USB-C PD power sources (laptop charger or `20 V` PD power bank) plus UK shipping are excluded from lamp-parts totals. `PCB-02` (`led_mcpcb`, `ENIG`) is cross-referenced at £0.00 to `MECH-08` (`£6.00` amort / `£7.50` 5-pc batch) to prevent double-counting.

## 2. Key Rev 4.1 BOM Changes vs Rev 4.0

- **Zero CNC Milling & Top-Heatsink-Only (`S1-A`, `-£11.71` ex-VAT amort / `-£19.56` 1-off):** Removed the bottom `Fischer SK 578/50 SA` heatsink, CNC-milled `MECH-ADAPT-BOT`, `TG-A6200` thermal gap pad, bottom `4× M3 × 14` hub bolts, and Kapton pocket lining; replaced with 3D-printed `MECH-LID-BOT` (`4×` integral `M2.5` bosses + nylon `M2.5 × 6` screws & `M2.5` inserts). Replaced CNC-machined top adapter/anchors with stock `Ø76.2 × 3.0 mm` Al disc (`MECH-ADAPT-TOP`) and stock `32 × 32 mm` Al square bar (`MECH-ANCHOR-TOP/BOT`).
- **USB-C PD Only & Reliability Hardening (`S2-A` + Adversarial Reviews):** Removed Aux `TP1/TP2`, `F2`, `Q1B`, Aux `B340A`, and `M16` cable gland. Upgraded `Q1` to a single `40 V` `DMN4035L-7`, `F1` to `33 V` `Bourns MF-MSMF110/33X`, `D11` to unidirectional `SMBJ22A-E3/52`, and added ESD clamps on `CC1`/`CC2` (`D13/D14` `CDSOD323-T24`) and `J4` (`D15/D16` `CDSOD323-T05`), `0.90 V` UVLO hysteresis resistors (`R17–R20`), `Q1` gate bleed (`R21`), and `100 nF + 6.8 Ω` damped output shunts (`C4/C5`, `R22/R23`). Upgraded both `driver_pcb` and `led_mcpcb` to **ENIG** finish.
- **Direct Gold Dry-Circuit Switch (`S3`):** Replaced silver-contact `100SP3T1B1M1QEH` + steering `BAT54` + `5.1 V` Zener bias with a gold-contact `C&K 7211SYZBE` `DPDT On-On-On` (`0.4 VA max @ 20 V`), wired directly to `J4`.
- **Active Stocked Cree `XP-E2` Bins:** Updated `D5/D6` (`XPEBRY-L1-0000-00S02`, Royal Blue Bin 38), `D7` (`XPEBGR-L1-0000-00K01`, Green Bin S3, +28% flux), and `D8` (`XPEBWT-L1-0000-00H51`, Cool White Bin R5) alongside `4× Luminus SST-10-UV-A130-G365-00` (`D1..D4`).
- **Dew Protection (`Option 3A`):** Added `£0.30` off-the-shelf `20 mm` rubber membrane grommet (`MECH-GROMMET-1`, Eaton `KT-M20` / RS `06664634`) and amortized share of acrylic conformal coating (`MG Chemicals 419D` in `MECH-MISC-1`).

## 3. Recommended External Power Accessories (Not in Lamp-Parts Total)

- **Garden / Bench Use:** Any standard `45–100 W` USB-C PD laptop charger (e.g., MacBook / ThinkPad / Dell / Anker USB-C PD brick) with a standard `60 W+` USB-C to USB-C cable (`6.65 mm` plug mates directly into `J1` through the `20 mm` slit rubber grommet).
- **Portable Field Use:** Any `20 V`-capable USB-C PD power bank (`>= 45 W` / `>= 65 W`, e.g., Anker / INIU / Baseus `20,000 mAh / 74 Wh` -> `~7.5 h` in `8-ALL` or `~14 h` in `4-UV`).

## 4. Verification Command

```bash
python3 bom/verify_bom.py
```
