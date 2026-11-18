# LepiLED DIY Maxi Switch

A practical, DIY, **fanless (passive-cooled)** *"Maxi Switch"*-style moth-trapping lamp inspired by Gunnar Brehm's LepiLED ([Pensoft 2017 design paper](https://nl.pensoft.net/article/11887/element/2/12//)) and commercial Maxi Switch hardware, designed around UK off-the-shelf parts, reproducible open-source EDA/CAD/simulation toolchains, and a ~£100 lamp-parts budget.

---

## 1. Key Features & Verified Specifications

| Subsystem | Verified Specification | Source |
|---|---|---|
| **Optical Array (`360°`, 2 Tiers × 4 Faces)** | `4×` UV-A `365 nm` (`Luminus SST-10-UV-A130-G365-00`) + `2×` Royal Blue `455 nm` (`Cree XP-E2`) + `1×` Green `528 nm` (`Cree XP-E2`) + `1×` Cool White `6200 K` (`Cree XP-E2`) on `4×` `20 × 80 × 1.6 mm` `1.0 W/m·K` Al MCPCBs | `circuit_design/`, `pcb_design/led_mcpcb/` |
| **Maxi-Switch Modes (`SW1` SPDT On-Off-On)** | **`4-UV`** (`~5.54 W`, `~1.11 A @ 5.0 V`, halves battery draw for extended runtime) / **`OFF`** (`< 1 mA`) / **`8-ALL`** (`~10.74 W`, `2.07–2.15 A @ 5.0 V`, `+1.0 ms` staggered turn-on) via logic-level `DIM` diode-OR (`D12` `BAV70LT1G`) | `docs/ELECTRONICS_ARCHITECTURE.md` |
| **Constant-Current Boost Drivers** | Dual independent 4S CCM boosts (`2× TI LM3410XMY/NOPB`, MSOP-8-PowerPAD, `1.6 MHz`, `RθJA = 53.7 °C/W`), `339.3 mA` nominal per string (`0.56 Ω ±1%` sense), `~88–89%` efficiency, `BZT52C18` open-load OVP (`≤ 22.56 V < 24 V`) | `circuit_design/sim/` |
| **Input Protection & Soft-Start** | `MF-LSMF500/16X` polyfuse (`5.0 A` @ `23 °C`), back-to-back `DMG2305UX-7` (`-16 V` reverse-polarity block), `TL431AIDBZR` latched OVP (`[5.75, 6.14] V` trip up to `+16 V`), `~4 ms` soft-start (`≤ 2.51 A` cold inrush), `SMBJ5.0A` TVS | `circuit_design/sim/outputs/sim_summary.json` |
| **Power Entry Options** | **Option A (`M16_GLAND`, primary weatherproof):** `TP1`/`TP2` + `18 AWG ≤ 1.0 m` captive USB-A pigtail (`R_cable ≤ 0.048 Ω`, supply `≥ 4.85 V`, `≥ 3 A`). **Option B (`USB_C`):** `J1` `USB4085-GF-A` (`R_cable ≤ 0.018 Ω`, `≥ 4.90 V`, `≥ 3.5 A`, **requires `≥ 12.31 mm` / `13.0 mm` extended-barrel plug**) | `circuit_design/INTERFACE_CONTRACT.md`, `mechanical_design/MECHANICAL_DESIGN.md` |
| **PCBs (KiCad 9.0.8, 0 ERC / 0 DRC)** | **Board 1 (`driver_pcb`):** `36.0 × 46.0 mm`, 2-layer `1.6 mm` FR4, `61` On-PCB + `10` Off-Board (`71` RefDes, `36` nets). **Board 2 (`led_mcpcb`):** `20.0 × 80.0 mm`, 1-layer `F.Cu`-only Al MCPCB (`0` `B.Cu`, `0` PTH) | `pcb_design/PCB_SUMMARY.md` |
| **Glass Enclosure & Passive Heatsinks** | `CRH Supplies` borosilicate 3.3 cylinder (`75 mm OD / 68 mm ID / 3.5 mm wall × 150 mm`, `~90%` UV-A @ `365 nm`) sealed by `VMQ70` O-rings. Decoupled dual-heatsink spine: matte-black `40×40×3 × 165 mm` Al core (`ε = 0.88`) + `SK 578/50 SA` top + `6.0 mm` PETG/PA12 bulkhead + `0.5 mm` `TG-A6200` + `SK LED R 80 SA` (`Config A`) or `SK 578/50 SA` (`Config C`) bottom | `mechanical_design/MECHANICAL_DESIGN.md` |
| **Thermal & CAD Verification** | **`20 / 20`** baseline fanless thermal cases PASS (`Config A` worst `30 °C` Horiz `8-ALL DS-100%`: `T_j,UV = 85.6 °C < 100`, `T_pcb_top_avg = 53.7 °C ≤ 55`); `Config C` passes `16/20` (all `12/12` nominal `≤ 30 °C` + `4/4` `22 °C` DS). **`34/34`** parametric checks, **`0/612`** B-Rep overlaps, `84/84` insertion checks, support-free `FDM` & `SLS` end-caps (`≤ 0.022 mm² > 46°`) | `mechanical_design/thermal/thermal_summary.json`, `mechanical_design/cad/cad_verification.json` |

---

## 2. BOM Tier Summary (`bom/`)

Per **Requirement R4**, the external `5 V` USB power bank and 3D-printed end-caps (`MECH-CAP-BOT`, `MECH-CAP-TOP`) are excluded from the lamp-parts BOM.

| Build Tier | Bottom Heatsink (`MECH-HS-EXT-BOT`) | Per-Lamp Amortized (ex VAT / inc 20% VAT) | 1-Off UK DIY Outlay *(excl. shipping, ex / inc VAT)* | Intended Use |
|---|---|---|---|---|
| **Nominal-Mode Build (`Config C`)** | `Fischer SK 578/50 SA` (`R = 8.5 mm` hub holes) | **£109.39** / **£131.27** | **£161.04** / **£193.25** | Matches ~£100 R4 target; passes all `12/12` nominal cases (`≤ 30 °C`) + `4/4` `22 °C` DS fault cases |
| **Worst-Case Thermal Upgrade (`Config A`)** | `Fischer SK LED R 80 SA` (`R = 11.0 mm` hub holes) | **£128.11** / **£153.73** | **£179.76** / **£215.71** | Passes all `20/20` thermal cases including stacked `30 °C` Horizontal `DS-100%` fault corners |

See [`bom/BOM.md`](bom/BOM.md) for pack/MOQ breakdowns, UK shipping-threshold consolidation (`DigiKey £65`, `Farnell £40`, `RS £60`, `JLCPCB IOSS`), stocked Cree XP-E2 / Samsung MLCC equivalents, and [`bom/bom.csv`](bom/bom.csv) for machine-verified line items.

---

## 3. Repository Layout

```
lepiled/
├── README.md                        # Top-level overview, specs, layout, and verification commands
├── bom/
│   ├── bom.csv                      # Machine-readable UK BOM (71 RefDes + 2 PCB fab + 29 MECH-*)
│   ├── BOM.md                       # Tier comparison, MOQ/1-off breakdown, shipping & sourcing guide
│   └── verify_bom.py                # Stdlib verifier for 1:1 ID parity & deterministic arithmetic
├── circuit_design/
│   ├── COMPONENT_IDS.csv            # Canonical 71-RefDes electrical registry
│   ├── INTERFACE_CONTRACT.md        # M1<->M2<->M3 electrical, thermal & physical envelope contract
│   ├── generate_schematic.py        # Reproducible schemdraw schematic generator
│   ├── lepiled_schematic.cir        # Top-level circuit netlist
│   ├── schematic.{pdf,png,svg}      # Rendered full schematic diagram
│   └── sim/                         # ngspice netlists, models, SciPy corner/MC suite & outputs
├── datasheets/                      # Archived vendor PDFs + datasheets_summary.{json,md}
├── docs/
│   ├── ASSEMBLY_GUIDE.md            # Step-by-step SMD reflow, bring-up, metalwork & assembly guide
│   ├── BLOCKERS.md                  # External blockers (B1) and user-space toolchains (M1/B2/B3)
│   └── ELECTRONICS_ARCHITECTURE.md  # Driver trade-off & datasheet-driven rationale
├── mechanical_design/
│   ├── MECHANICAL_DESIGN.md         # Decoupled dual-heatsink & thermal/CAD engineering report
│   ├── CLEARANCE_VERIFICATION.md    # B-Rep all-pairs, insertion, O-ring & overhang audit
│   ├── MECH_PARTS.csv               # Canonical 29-part UK mechanical registry
│   ├── cad/                         # build123d params.py, generate_cad.py, render_cad.py, STEP/STL/PNGs
│   └── thermal/                     # 2D/3D FVM PDE thermal_analysis.py, CSV, JSON & plots
└── pcb_design/
    ├── PCB_SUMMARY.md               # Board stackups, ERC/DRC metrics & manufacturing manifest
    ├── driver_pcb_bom*.csv          # Full (71) & PCBA (61) BOMs + JLCPCB CPL (57 placed)
    ├── led_mcpcb_*.csv              # Al MCPCB strip BOM & CPL (D_UV, D_VIS)
    ├── driver_pcb/                  # KiCad 9 project, schematic, PCB, builder script, ERC/DRC, renders
    ├── led_mcpcb/                   # KiCad 9 1-layer Al MCPCB project, builder script, ERC/DRC, renders
    └── gerbers/                     # Ready-to-order Gerber & drill packages (.zip + individual layers)
```

---

## 4. Build & Assembly Quick Start

1. **Order Components & PCBs:** Follow [`bom/BOM.md`](bom/BOM.md) (`Option A` `M16_GLAND` recommended; bundle `pcb_design/gerbers/driver_pcb/driver_pcb_gerbers.zip` and `pcb_design/gerbers/led_mcpcb/led_mcpcb_gerbers.zip` on JLCPCB).
2. **3D-Print End-Caps:** Print `mechanical_design/cad/mech_cap_bot.stl` (or `mech_cap_bot_usbc.stl` for Option B) upright and `mech_cap_top.stl` inverted in **`PETG` or `ASA`** (support-free; **do not use PLA**), or order `*_sls.stl` in `PA12`.
3. **Assemble & Bring Up:** Follow [`docs/ASSEMBLY_GUIDE.md`](docs/ASSEMBLY_GUIDE.md) closely — paying special attention to:
   - **Opposite LED thermal-pad notches:** `SST-10-UV` (`BTM NOTCH=K`) vs `Cree XP-E2` (`BTM NOTCH=A`).
   - **Option B (`USB_C`) extended-barrel cable:** `mech_cap_bot_usbc` requires a `≥ 12.31 mm` (`13.0 mm`) extended-tip USB-C plug (`R_cable ≤ 0.018 Ω`).
   - **`365 nm` UV-A safety:** Wear `EN 166 / EN 170` `< 400 nm` UV-blocking glasses whenever testing emitters.

---

## 5. Reproducible Verification Commands

All tools run in user-space without `sudo` (paths documented in [`docs/BLOCKERS.md`](docs/BLOCKERS.md)). Run from `/home/alimuldal/src/lepiled`:

```bash
# 1. BOM 1:1 Parity & Arithmetic Verification (M4)
python3 -B bom/verify_bom.py

# 2. Schematic & Circuit Simulation Suite (M1: ngspice 45.2 + SciPy corners/MC)
/home/alimuldal/.local/share/lepiled-venv/bin/python circuit_design/generate_schematic.py
/home/alimuldal/.local/share/lepiled-venv/bin/python circuit_design/sim/run_simulations.py
/home/alimuldal/.local/share/lepiled-tools/bin/ngspice -b circuit_design/sim/netlists/lepiled_nominal.cir

# 3. KiCad 9.0.8 ERC & DRC Live Verification (M2: 0 violations, read-only into /tmp)
/home/alimuldal/.local/share/lepiled-tools/bin/kicad-cli sch erc --format json --severity-all --exit-code-violations -o /tmp/erc_driver.json pcb_design/driver_pcb/driver_pcb.kicad_sch
/home/alimuldal/.local/share/lepiled-tools/bin/kicad-cli pcb drc --format json --schematic-parity --severity-all --exit-code-violations -o /tmp/drc_driver.json pcb_design/driver_pcb/driver_pcb.kicad_pcb
/home/alimuldal/.local/share/lepiled-tools/bin/kicad-cli sch erc --format json --severity-all --exit-code-violations -o /tmp/erc_mcpcb.json pcb_design/led_mcpcb/led_mcpcb.kicad_sch
/home/alimuldal/.local/share/lepiled-tools/bin/kicad-cli pcb drc --format json --schematic-parity --severity-all --exit-code-violations -o /tmp/drc_mcpcb.json pcb_design/led_mcpcb/led_mcpcb.kicad_pcb
# Full PCB/Gerber/BOM/CPL rebuild:
/home/alimuldal/.local/share/lepiled-tools/bin/kicad-python pcb_design/driver_pcb/build_driver_pcb.py
/home/alimuldal/.local/share/lepiled-tools/bin/kicad-python pcb_design/led_mcpcb/build_led_mcpcb.py

# 4. 2D/3D Thermal FVM & Parametric B-Rep CAD Verification (M3)
/home/alimuldal/.local/share/lepiled-cad-venv/bin/python mechanical_design/thermal/thermal_analysis.py
/home/alimuldal/.local/share/lepiled-cad-venv/bin/python mechanical_design/cad/params.py
/home/alimuldal/.local/share/lepiled-cad-venv/bin/python mechanical_design/cad/generate_cad.py
xvfb-run -a /home/alimuldal/.local/share/lepiled-cad-venv/bin/python mechanical_design/cad/render_cad.py
```

---

## 6. External Blockers Summary

- **`B1` (Hard External Blocker):** The reference Google Sheet (`https://docs.google.com/spreadsheets/d/1VNcXHNNrZ-xlLQjyCB3U-OSda4Kfq_rMDRMXmeiYSrs/edit?usp=sharing`) is login-gated (`HTTP 401` / `302` redirect). All parts, ratings, and UK pricing were independently verified from primary vendor PDF datasheets and live UK distributor catalogs.
- **`M1`, `B2/M2`, `B3/M3` (Resolved in User-Space):** `ngspice 45.2`, `KiCad 9.0.8`, `gerbv 2.10.0`, `lepiled-venv`, and `lepiled-cad-venv` (`build123d 0.13.0`) are provisioned in user-space with zero blocking impact. Full details in [`docs/BLOCKERS.md`](docs/BLOCKERS.md).
