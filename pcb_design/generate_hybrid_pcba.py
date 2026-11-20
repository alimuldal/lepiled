#!/usr/bin/env python3
"""Programmatically derive Hybrid JLCPCB Economic PCBA files from the canonical full BOM & CPL.

Rev 4.7 (CH224A + 2-Extended-Reel Budget PCBA):
  Single source of truth:
    - pcb_design/driver_pcb_bom_pcba.csv (52 populated On-PCB parts: 48 SMD + 4 THT)
    - pcb_design/driver_pcb_cpl.csv      (48 SMD placements)

  Derived outputs (never hand-edit; verified 1:1 by bom/verify_bom.py):
    - pcb_design/driver_pcb_bom_pcba_hybrid.csv  (40 SMD parts assembled by JLCPCB; ONLY 2 Extended reels: U1/U2 + U3!)
    - pcb_design/driver_pcb_cpl_hybrid.csv       (40 SMD placements matching the hybrid BOM 1:1)
    - pcb_design/driver_pcb_diy_hand_solder.csv  (10 bench hand-solder parts: 4 THT + 6 chunky 2-pad SMDs; plus 2 optional DNP notes)

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

# 1. Chunky 2-pad Extended SMDs offloaded from JLCPCB PCBA to DIY bench hand-soldering.
#    Eliminates 4 Extended feeder reels ($12) while keeping all fine-pitch ICs, SOT-23,
#    and 0603/0805/1206 passives assembled by JLCPCB.
HYBRID_DIY_OFFLOAD: dict[str, str] = {
    "F1": "1812 2-pad PPTC fuse (Extended reel offload; easy hand-solder)",
    "D11": "DO-214AA (SMB) 2-pad TVS diode (Extended reel offload; easy hand-solder)",
    "L1": "6.0x6.0 mm 2-pad power inductor (Extended reel offload; easy hand-solder)",
    "L2": "6.0x6.0 mm 2-pad power inductor (Extended reel offload; easy hand-solder)",
    "R3": "1206 2-pad 0.30R shunt (Extended reel offload; easy hand-solder)",
    "R4": "1206 2-pad 0.30R shunt (Extended reel offload; easy hand-solder)",
}

# 2. Optional ESD diodes left DNP (unpopulated) in the 2-Extended-reel Hybrid BOM.
#    Because the 90-deg USB-C cable is permanently captured inside the sealed ASA base
#    and CH224A includes internal ESD protection, leaving D13/D14 unpopulated saves $3
#    and brings the entire Hybrid PCBA down to ONLY 2 Extended reels (U1/U2 + U3).
HYBRID_DNP_EXCLUDE: dict[str, str] = {
    "D13": "Optional CC1 24 V ESD diode (left DNP in 2-reel Hybrid PCBA; pads remain available)",
    "D14": "Optional CC2 24 V ESD diode (left DNP in 2-reel Hybrid PCBA; pads remain available)",
}

# 3. Basic swaps map (empty in Rev 4.7 because Basic parts U4/U5/Q2/Q3/D9/D10/D12/D15/D16
#    and all passives are already canonical in driver_pcb_bom_pcba.csv).
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
    """Deterministically derive (hybrid_bom_csv, hybrid_cpl_csv, diy_bom_csv, stats)."""
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
                "Through-hole connector (hand-soldered in both Full and Hybrid builds)",
            ])
        elif ref in HYBRID_DIY_OFFLOAD:
            diy_bom_rows.append([
                row["Comment"],
                ref,
                row["Footprint"],
                row["MPN"],
                "SMD Hand-Solder (DIY Hybrid Offload)",
                HYBRID_DIY_OFFLOAD[ref],
            ])
        elif ref in HYBRID_DNP_EXCLUDE:
            diy_bom_rows.append([
                row["Comment"],
                ref,
                row["Footprint"],
                row["MPN"],
                "Optional DNP (Omit in 2-Reel Hybrid)",
                HYBRID_DNP_EXCLUDE[ref],
            ])
        else:
            swap = HYBRID_BASIC_SWAPS.get(ref)
            comment = swap["Comment"] if swap else row["Comment"]
            lcsc = swap["LCSC Part #"] if swap else row["LCSC Part #"]
            mpn = swap["MPN"] if swap else row["MPN"]
            note = swap["Hybrid_Note"] if swap else ""
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
        raise ValueError(f"Hybrid CPL/BOM Designator mismatch: missing={missing}, extra={extra}")

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
    parser = argparse.ArgumentParser(description="Generate or verify Hybrid JLCPCB Economic PCBA files.")
    parser.add_argument("--check", action="store_true", help="Verify derived CSVs match canonical full BOM/CPL without writing.")
    args = parser.parse_args()

    if args.check:
        errs = check()
        if errs:
            for e in errs:
                print(f"ERROR: {e}", file=sys.stderr)
            return 1
        print("PASS: Hybrid PCBA CSVs match canonical driver_pcb_bom_pcba.csv + driver_pcb_cpl.csv 1:1.")
        return 0

    stats = generate()
    print(
        f"Generated Hybrid PCBA outputs from {stats['full_bom_rows']} canonical PCBA rows "
        f"({stats['full_cpl_rows']} SMD CPL): "
        f"{stats['hybrid_pcba_rows']} JLCPCB Hybrid SMD (ONLY 2 Extended reels: U1/U2 + U3!) + "
        f"{stats['diy_hand_solder_rows'] - stats['dnp_rows']} DIY hand-solder "
        f"({stats['smd_offloads']} offloaded chunky SMDs + 4 THT) + {stats['dnp_rows']} optional DNP."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
