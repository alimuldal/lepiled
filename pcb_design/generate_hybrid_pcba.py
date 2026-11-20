#!/usr/bin/env python3
"""Programmatically derive JLCPCB 2-Reel Hybrid Lead-Free HASL PCBA files from canonical full BOM & CPL.

Rev 4.9 (Budget 2-Extended-Reel Hybrid PCBA — Only 2 Extended Reels = $6 Feeder Fees!):
  Single source of truth:
    - pcb_design/driver_pcb_bom_pcba.csv (54 On-PCB rows: 48 populated SMD + 2 optional DNP + 4 THT)
    - pcb_design/driver_pcb_cpl.csv      (48 populated SMD placements; DNP D13/D14 excluded)

  Derived outputs (never hand-edit; verified 1:1 by bom/verify_bom.py & verify_all.py):
    - pcb_design/driver_pcb_bom_pcba_hybrid.csv  (41 SMD parts assembled by JLCPCB: 20 Basic + ONLY 2 Extended reels U1/U2 & U3!)
    - pcb_design/driver_pcb_cpl_hybrid.csv       (41 SMD placements matching the JLCPCB upload BOM 1:1)
    - pcb_design/driver_pcb_diy_hand_solder.csv  (4 THT J1..J4 + 7 chunky 2-pad SMDs F1/D11/L1/L2/R3/R4/R7 from Farnell UK + 2 DNP)

Usage:
  python3 pcb_design/generate_hybrid_pcba.py          # regenerate all 3 derived CSVs
  python3 pcb_design/generate_hybrid_pcba.py --check  # exit 1 if any derived CSV is stale/divergent
"""

from __future__ import annotations

import argparse
import csv
import io
from pathlib import Path
import sys

PCB_DESIGN_DIR = Path(__file__).resolve().parent
FULL_BOM_PATH = PCB_DESIGN_DIR / "driver_pcb_bom_pcba.csv"
FULL_CPL_PATH = PCB_DESIGN_DIR / "driver_pcb_cpl.csv"

HYBRID_BOM_PATH = PCB_DESIGN_DIR / "driver_pcb_bom_pcba_hybrid.csv"
HYBRID_CPL_PATH = PCB_DESIGN_DIR / "driver_pcb_cpl_hybrid.csv"
DIY_BOM_PATH = PCB_DESIGN_DIR / "driver_pcb_diy_hand_solder.csv"

# 1. Rev 4.9 2-Extended-Reel Hybrid PCBA: Offload ONLY the 7 chunky 2-pad Extended SMDs
#    (1206, 2512, SMB, 6x6 mm) to bench hand-soldering alongside J1..J4 THT — all consolidated
#    in ONE Farnell UK order with SW1/SW1_BOOT, cutting $15 in JLCPCB Extended feeder fees!
HYBRID_DIY_OFFLOAD: dict[str, str] = {
    "F1": "Chunky 1206 2-pad Slo-Blo fuse (saves $3 JLCPCB Ext fee; consolidated on Farnell UK)",
    "D11": "Chunky DO-214AA SMB 2-pad TVS diode (saves $3 JLCPCB Ext fee; consolidated on Farnell UK)",
    "L1": "Chunky 6.0x6.0 mm 2-pad inductor (saves $3 JLCPCB Ext fee w/ L2; consolidated on Farnell UK)",
    "L2": "Chunky 6.0x6.0 mm 2-pad inductor (saves $3 JLCPCB Ext fee w/ L1; consolidated on Farnell UK)",
    "R3": "Chunky 1206 2-pad 0.30 Ohm shunt (saves $3 JLCPCB Ext fee w/ R4; consolidated on Farnell UK)",
    "R4": "Chunky 1206 2-pad 0.30 Ohm shunt (saves $3 JLCPCB Ext fee w/ R3; consolidated on Farnell UK)",
    "R7": "Chunky 2512 1 W 2-pad pulse damper resistor (saves $3 JLCPCB Ext fee; consolidated on Farnell UK)",
}

# 2. Optional ESD diodes left DNP (unpopulated and excluded from F_Paste.gbr)
HYBRID_DNP_EXCLUDE: dict[str, str] = {
    "D13": "Optional CC1 24 V ESD diode (DNP; excluded from paste & PCBA; pads remain available)",
    "D14": "Optional CC2 24 V ESD diode (DNP; excluded from paste & PCBA; pads remain available)",
}

# 3. Basic swaps map (empty in Rev 4.9; all 20 Basic + 2 Extended LCSC codes are canonical).
HYBRID_BASIC_SWAPS: dict[str, dict[str, str]] = {}

HYBRID_BOM_COLS = ["Comment", "Designator", "Footprint", "LCSC Part #", "MPN", "Hybrid_Note"]
DIY_BOM_COLS = ["Comment", "Designator", "Footprint", "MPN", "Assembly_Method", "DIY_Reason"]


def _read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.reader(f))
    if not rows:
        raise ValueError(f"Empty CSV: {path}")
    header = rows[0]
    return header, [dict(zip(header, r)) for r in rows[1:]]


def _render_csv(header: list[str], rows: list[list[str]]) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf, lineterminator="\n")
    writer.writerow(header)
    writer.writerows(rows)
    return buf.getvalue()


def derive_hybrid_tables(
    full_bom_path: Path = FULL_BOM_PATH,
    full_cpl_path: Path = FULL_CPL_PATH,
) -> tuple[str, str, str, dict[str, int]]:
    """Deterministically derive (pcba_bom_csv, pcba_cpl_csv, diy_bom_csv, stats)."""
    _, full_bom = _read_csv(full_bom_path)
    cpl_header, full_cpl = _read_csv(full_cpl_path)

    full_refs = {r["Designator"].strip() for r in full_bom}
    for name, mapping in [
        ("HYBRID_DIY_OFFLOAD", HYBRID_DIY_OFFLOAD),
        ("HYBRID_DNP_EXCLUDE", HYBRID_DNP_EXCLUDE),
        ("HYBRID_BASIC_SWAPS", HYBRID_BASIC_SWAPS),
    ]:
        unknown = set(mapping) - full_refs
        if unknown:
            raise ValueError(f"{name} references unknown Designators: {sorted(unknown)}")
    if (set(HYBRID_DIY_OFFLOAD) & set(HYBRID_DNP_EXCLUDE)) or (
        (set(HYBRID_DIY_OFFLOAD) | set(HYBRID_DNP_EXCLUDE)) & set(HYBRID_BASIC_SWAPS)
    ):
        raise ValueError("Overlapping Designators across offload/DNP/swap maps")

    hybrid_bom_rows: list[list[str]] = []
    diy_bom_rows: list[list[str]] = []
    hybrid_refs: set[str] = set()

    for row in full_bom:
        ref = row["Designator"].strip()
        method = row["Assembly_Method"].strip()

        if "THT" in method:
            diy_bom_rows.append([
                row["Comment"],
                ref,
                row["Footprint"],
                row["MPN"],
                method,
                "Through-hole connector (Farnell UK; hand-soldered alongside 7 chunky 2-pad SMDs)",
            ])
        elif ref in HYBRID_DIY_OFFLOAD:
            diy_bom_rows.append([
                row["Comment"],
                ref,
                row["Footprint"],
                row["MPN"],
                "SMD Hand-Solder (Chunky 2-Pad DIY Offload)",
                HYBRID_DIY_OFFLOAD[ref],
            ])
        elif ref in HYBRID_DNP_EXCLUDE or "DNP" in method:
            diy_bom_rows.append([
                row["Comment"],
                ref,
                row["Footprint"],
                row["MPN"],
                "Optional DNP (Excluded from Paste & PCBA)",
                HYBRID_DNP_EXCLUDE.get(ref, "Optional DNP"),
            ])
        else:
            swap = HYBRID_BASIC_SWAPS.get(ref)
            comment = swap["Comment"] if swap else row["Comment"]
            lcsc = swap["LCSC Part #"] if swap else row["LCSC Part #"]
            mpn = swap["MPN"] if swap else row["MPN"]
            note = swap["Hybrid_Note"] if swap else ""
            if not lcsc:
                raise ValueError(f"Missing LCSC Part # for JLCPCB-assembled SMD {ref} ({mpn})")
            hybrid_bom_rows.append([comment, ref, row["Footprint"], lcsc, mpn, note])
            hybrid_refs.add(ref)

    hybrid_cpl_rows: list[list[str]] = []
    cpl_seen: set[str] = set()
    for row in full_cpl:
        ref = row["Designator"].strip()
        if ref in hybrid_refs:
            hybrid_cpl_rows.append([row[c] for c in cpl_header])
            cpl_seen.add(ref)

    if cpl_seen != hybrid_refs:
        missing = sorted(hybrid_refs - cpl_seen)
        extra = sorted(cpl_seen - hybrid_refs)
        raise ValueError(f"PCBA CPL/BOM Designator mismatch: missing={missing}, extra={extra}")

    stats = {
        "full_bom_rows": len(full_bom),
        "full_cpl_rows": len(full_cpl),
        "hybrid_pcba_rows": len(hybrid_bom_rows),
        "hybrid_cpl_rows": len(hybrid_cpl_rows),
        "diy_hand_solder_rows": len(diy_bom_rows),
        "dnp_rows": len(HYBRID_DNP_EXCLUDE),
        "smd_offloads": len(HYBRID_DIY_OFFLOAD),
    }

    return (
        _render_csv(HYBRID_BOM_COLS, hybrid_bom_rows),
        _render_csv(cpl_header, hybrid_cpl_rows),
        _render_csv(DIY_BOM_COLS, diy_bom_rows),
        stats,
    )


def generate() -> dict[str, int]:
    hybrid_bom_txt, hybrid_cpl_txt, diy_bom_txt, stats = derive_hybrid_tables()
    HYBRID_BOM_PATH.write_text(hybrid_bom_txt, encoding="utf-8", newline="")
    HYBRID_CPL_PATH.write_text(hybrid_cpl_txt, encoding="utf-8", newline="")
    DIY_BOM_PATH.write_text(diy_bom_txt, encoding="utf-8", newline="")
    return stats


def check() -> list[str]:
    hybrid_bom_txt, hybrid_cpl_txt, diy_bom_txt, _ = derive_hybrid_tables()
    errors: list[str] = []
    for path, expected in [
        (HYBRID_BOM_PATH, hybrid_bom_txt),
        (HYBRID_CPL_PATH, hybrid_cpl_txt),
        (DIY_BOM_PATH, diy_bom_txt),
    ]:
        if not path.exists():
            errors.append(f"Missing derived file: {path.name} (run python3 pcb_design/generate_hybrid_pcba.py)")
        elif path.read_text(encoding="utf-8").replace("\r\n", "\n") != expected:
            errors.append(
                f"Stale/divergent derived file: {path.name} does not match canonical "
                f"driver_pcb_bom_pcba.csv + driver_pcb_cpl.csv (run python3 pcb_design/generate_hybrid_pcba.py)"
            )
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate or verify JLCPCB 2-Reel Hybrid HASL PCBA files.")
    parser.add_argument("--check", action="store_true", help="Verify derived CSVs match canonical full BOM/CPL without writing.")
    args = parser.parse_args()

    if args.check:
        errs = check()
        if errs:
            for e in errs:
                print(f"ERROR: {e}", file=sys.stderr)
            return 1
        print("PASS: JLCPCB 2-Reel Hybrid PCBA CSVs match canonical driver_pcb_bom_pcba.csv + driver_pcb_cpl.csv 1:1.")
        return 0

    stats = generate()
    print(
        f"Generated Rev 4.9 2-Reel Hybrid PCBA outputs from {stats['full_bom_rows']} canonical PCBA rows "
        f"({stats['full_cpl_rows']} SMD CPL): "
        f"{stats['hybrid_pcba_rows']} JLCPCB SMD (20 Basic + ONLY 2 Extended reels!) + "
        f"{stats['diy_hand_solder_rows'] - stats['dnp_rows']} DIY ({stats['diy_hand_solder_rows'] - stats['dnp_rows'] - stats['smd_offloads']} THT + {stats['smd_offloads']} chunky 2-pad SMDs) + {stats['dnp_rows']} DNP."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
