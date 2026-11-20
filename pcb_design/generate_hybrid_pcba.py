#!/usr/bin/env python3
"""Programmatically derive Hybrid JLCPCB Economic PCBA files from the canonical full BOM & CPL.

Single source of truth:
  - pcb_design/driver_pcb_bom_pcba.csv (61 populated On-PCB parts: 57 SMD + 4 THT)
  - pcb_design/driver_pcb_cpl.csv      (57 SMD placements)

Derived outputs (never hand-edit; verified 1:1 by bom/verify_bom.py):
  - pcb_design/driver_pcb_bom_pcba_hybrid.csv  (50 SMD parts assembled by JLCPCB; 0 THT, 0 chunky 2-pad offloads)
  - pcb_design/driver_pcb_cpl_hybrid.csv       (50 SMD placements matching the hybrid BOM 1:1)
  - pcb_design/driver_pcb_diy_hand_solder.csv  (11 bench hand-solder parts: 4 THT + 7 chunky 2-pad Extended SMDs)

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
#    Eliminates 5 Extended feeder reels ($15 / ~£12) while keeping all fine-pitch ICs,
#    SOT-23, SOD-323, and 0603/0805/1206 passives assembled by JLCPCB.
HYBRID_DIY_OFFLOAD: dict[str, str] = {
    "F1": "1812 2-pad PPTC fuse (Extended reel offload; easy hand-solder)",
    "D11": "DO-214AA (SMB) 2-pad TVS diode (Extended reel offload; easy hand-solder)",
    "L1": "6.0x6.0 mm 2-pad power inductor (Extended reel offload; easy hand-solder)",
    "L2": "6.0x6.0 mm 2-pad power inductor (Extended reel offload; easy hand-solder)",
    "R3": "1206 2-pad 0.30R shunt (Extended reel offload; easy hand-solder)",
    "R4": "1206 2-pad 0.30R shunt (Extended reel offload; easy hand-solder)",
    "R8": "1206 2-pad 5mR shunt (Extended reel offload; easy hand-solder)",
}

# 2. Electrically verified JLCPCB Basic part substitutions applied ONLY in the Hybrid PCBA BOM.
#    - U4: onsemi LM393DR2G (C7955, Basic, SOIC-8, 2-36 V, 0..70 C commercial).
#      Worst-case UVLO corners with R15=59.0k (+/-1% R, +/-0.85% LM4040, +/-9 mV Vio):
#      V_ON = [17.03, 18.06] V, V_OFF = [16.15, 17.13] V, hyst >= 0.85 V (100% PASS).
#    - D9, D10: MDD SS34 (C8678, Basic, SMA DO-214AC, 3 A / 40 V Schottky catch diode).
#    Note: R15 is intentionally kept at 59.0k (56k drops WC V_OFF to 15.49 V < 15.75 V PD max;
#    62k pushes WC V_ON to 18.85 V > 18.5 V).
HYBRID_BASIC_SWAPS: dict[str, dict[str, str]] = {
    "U4": {
        "Comment": "LM393DR2G",
        "LCSC Part #": "C7955",
        "MPN": "onsemi LM393DR2G",
        "Hybrid_Note": "JLCPCB Basic drop-in for LM393BIDR (identical SOIC-8; 0..70 C grade; WC UVLO 17.03-18.06/16.15-17.13 V)",
    },
    "D9": {
        "Comment": "SS34",
        "LCSC Part #": "C8678",
        "MPN": "MDD SS34",
        "Hybrid_Note": "JLCPCB Basic 3A/40V SMA Schottky drop-in for B340A-13-F",
    },
    "D10": {
        "Comment": "SS34",
        "LCSC Part #": "C8678",
        "MPN": "MDD SS34",
        "Hybrid_Note": "JLCPCB Basic 3A/40V SMA Schottky drop-in for B340A-13-F",
    },
}

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
    unknown_offloads = set(HYBRID_DIY_OFFLOAD) - full_refs
    unknown_swaps = set(HYBRID_BASIC_SWAPS) - full_refs
    overlap = set(HYBRID_DIY_OFFLOAD) & set(HYBRID_BASIC_SWAPS)
    if unknown_offloads:
        raise ValueError(f"HYBRID_DIY_OFFLOAD references unknown Designators: {sorted(unknown_offloads)}")
    if unknown_swaps:
        raise ValueError(f"HYBRID_BASIC_SWAPS references unknown Designators: {sorted(unknown_swaps)}")
    if overlap:
        raise ValueError(f"Designators present in both offload and swap maps: {sorted(overlap)}")

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
        "basic_swaps": len(HYBRID_BASIC_SWAPS),
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
        f"{stats['hybrid_pcba_rows']} JLCPCB Hybrid SMD ({stats['basic_swaps']} Basic swaps) + "
        f"{stats['diy_hand_solder_rows']} DIY hand-solder ({stats['smd_offloads']} offloaded chunky SMDs + "
        f"{stats['diy_hand_solder_rows'] - stats['smd_offloads']} THT)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
