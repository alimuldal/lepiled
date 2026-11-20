#!/usr/bin/env python3
"""Machine-verifiable audit script for bom/bom.csv (Rev 4.2 — Lean 1-Off Hobby Build)."""

from __future__ import annotations

import csv
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
BOM_CSV = REPO_ROOT / "bom" / "bom.csv"
COMP_IDS_CSV = REPO_ROOT / "circuit_design" / "COMPONENT_IDS.csv"
DRIVER_BOM_CSV = REPO_ROOT / "pcb_design" / "driver_pcb_bom.csv"
DRIVER_PCBA_CSV = REPO_ROOT / "pcb_design" / "driver_pcb_bom_pcba.csv"
MECH_PARTS_CSV = REPO_ROOT / "mechanical_design" / "MECH_PARTS.csv"

EXPECTED_COLUMNS = [
    "BOM_ID",
    "Domain",
    "Source_IDs",
    "RefDes_List",
    "Build_Tier",
    "Qty_Per_Lamp",
    "Category",
    "MPN_or_Part",
    "Specification",
    "Mounting_or_Package",
    "UK_Supplier",
    "Supplier_URL",
    "MOQ_Pack_Qty",
    "Packs_1Off",
    "Order_Qty_1Off",
    "Unit_Price_Amort_GBP_exVAT",
    "Pack_Price_1Off_GBP_exVAT",
    "Ext_Price_Amort_GBP_exVAT",
    "Ext_Price_1Off_GBP_exVAT",
    "Ext_Price_Amort_GBP_incVAT",
    "Ext_Price_1Off_GBP_incVAT",
    "Include_In_Total",
    "Notes",
]

Q2 = Decimal("0.01")
VAT_RATE = Decimal("1.20")


def round2(val: Decimal) -> Decimal:
    return val.quantize(Q2, rounding=ROUND_HALF_UP)


def load_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        raw_rows = list(csv.reader(f))
    if not raw_rows:
        raise ValueError(f"Empty CSV in {path}")
    header = raw_rows[0]
    rows: list[dict[str, str]] = []
    for line_no, raw in enumerate(raw_rows[1:], start=2):
        if len(raw) != len(header):
            raise ValueError(f"{path}:{line_no}: expected {len(header)} columns, got {len(raw)}")
        rows.append(dict(zip(header, raw)))
    return header, rows


def main() -> int:
    errors: list[str] = []

    def fail(msg: str) -> None:
        errors.append(msg)

    bom_cols, bom_rows = load_csv(BOM_CSV)
    if bom_cols != EXPECTED_COLUMNS:
        fail(f"bom.csv columns mismatch: got {bom_cols}, expected {EXPECTED_COLUMNS}")

    _, comp_rows = load_csv(COMP_IDS_CSV)
    _, drv_rows = load_csv(DRIVER_BOM_CSV)
    _, pcba_rows = load_csv(DRIVER_PCBA_CSV)
    _, mech_rows = load_csv(MECH_PARTS_CSV)

    seen_bom_ids: set[str] = set()
    for idx, row in enumerate(bom_rows, start=2):
        bid = row["BOM_ID"].strip()
        if not bid:
            fail(f"Row {idx}: empty BOM_ID")
        elif bid in seen_bom_ids:
            fail(f"Row {idx}: duplicate BOM_ID {bid}")
        seen_bom_ids.add(bid)

        if row["Build_Tier"] != "CORE":
            fail(f"{bid}: expected Build_Tier='CORE', got {row['Build_Tier']!r}")
        if row["Include_In_Total"] not in {"Yes", "No"}:
            fail(f"{bid}: invalid Include_In_Total {row['Include_In_Total']!r}")

    # 1. Electrical 75-RefDes 1:1 parity
    comp_by_ref = {r["RefDes"].strip(): r for r in comp_rows}
    drv_by_ref = {r["Designator"].strip(): r for r in drv_rows}
    pcba_refs = {r["Designator"].strip() for r in pcba_rows}

    if len(comp_rows) != 75:
        fail(f"COMPONENT_IDS.csv expected 75 rows, got {len(comp_rows)}")
    if set(comp_by_ref) != set(drv_by_ref):
        fail("COMPONENT_IDS.csv vs driver_pcb_bom.csv RefDes mismatch")

    bom_elec_rows = [r for r in bom_rows if r["Domain"] == "Electrical"]
    bom_elec_refs: list[str] = []
    for row in bom_elec_rows:
        bid = row["BOM_ID"]
        refs = [x.strip() for x in row["RefDes_List"].split(";") if x.strip()]
        src_refs = [x.strip() for x in row["Source_IDs"].split(";") if x.strip()]
        if refs != src_refs:
            fail(f"{bid}: Source_IDs {src_refs} != RefDes_List {refs}")
        qty = int(row["Qty_Per_Lamp"])
        if qty != len(refs):
            fail(f"{bid}: Qty_Per_Lamp={qty} != len(RefDes_List)={len(refs)}")
        for ref in refs:
            if ref not in comp_by_ref:
                fail(f"{bid}: unknown RefDes {ref}")
            else:
                expected_mpn = comp_by_ref[ref]["MPN"].strip()
                if row["MPN_or_Part"].strip() != expected_mpn:
                    fail(f"{bid} ({ref}): MPN mismatch: bom={row['MPN_or_Part']!r} vs comp={expected_mpn!r}")
        bom_elec_refs.extend(refs)

    if len(bom_elec_refs) != len(set(bom_elec_refs)):
        fail("Duplicate RefDes across Electrical BOM rows")
    if set(bom_elec_refs) != set(comp_by_ref):
        fail(f"Electrical RefDes set mismatch: missing={sorted(set(comp_by_ref) - set(bom_elec_refs))}")

    off_board_expected = {"D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8", "SW1", "SW1_BOOT"}
    pcb_features = {"H1", "H2", "H3", "H4"}
    on_pcb_from_comp = {r["RefDes"].strip() for r in comp_rows if r["Mounting"].strip() == "On-PCB"}
    if (on_pcb_from_comp - pcb_features) != pcba_refs or len(pcba_refs) != 61:
        fail(f"Populated On-PCB 61-RefDes subset mismatch (got {len(pcba_refs)})")
    if set(comp_by_ref) - on_pcb_from_comp != off_board_expected:
        fail("Off-board RefDes subset mismatch")

    matched_h = [r for r in bom_elec_rows if set(x.strip() for x in r["RefDes_List"].split(";")) == pcb_features]
    if len(matched_h) != 1 or matched_h[0]["Include_In_Total"] != "No" or Decimal(matched_h[0]["Ext_Price_Amort_GBP_exVAT"]) != 0:
        fail("PCB feature H1..H4 must have single BOM row with Include_In_Total=No and £0.00")

    # 2. Single custom PCB (driver_pcb ONLY — led_mcpcb eliminated in Rev 4.2!)
    pcb_rows = {r["BOM_ID"]: r for r in bom_rows if r["Domain"] == "PCB_Fab"}
    if set(pcb_rows) != {"PCB-01"}:
        fail(f"Expected only PCB-01 (driver_pcb) in PCB_Fab domain, got {set(pcb_rows)}")
    if pcb_rows["PCB-01"]["Source_IDs"] != "driver_pcb" or pcb_rows["PCB-01"]["Include_In_Total"] != "Yes":
        fail("PCB-01 must represent driver_pcb with Include_In_Total=Yes")

    # 3. Harness (2 pre-crimped JST-XH pigtail rows)
    bom_harn_rows = [r for r in bom_rows if r["Domain"] == "Harness"]
    if len(bom_harn_rows) != 2:
        fail(f"Expected 2 Harness rows (2P & 3P pre-crimped JST-XH pigtails), got {len(bom_harn_rows)}")

    # 4. Mechanical 16-Part 1:1 Parity (Rev 4.3)
    mech_by_id = {r["Part_ID"].strip(): r for r in mech_rows}
    if len(mech_by_id) != 16:
        fail(f"MECH_PARTS.csv expected 16 rows, got {len(mech_by_id)}")

    bom_mech_primary = [r for r in bom_rows if r["Domain"] == "Mechanical"]
    printed_ids = {"MECH-BASE-RING", "MECH-LID-BOT", "MECH-CAP-BOT", "MECH-CAP-TOP", "MECH-PLUG-TOP", "MECH-RAIN-HAT", "MECH-PLUG-BOT", "MECH-DRILL-JIG"}
    bom_mech_ids: list[str] = []
    for row in bom_mech_primary:
        bid = row["BOM_ID"]
        ids = [x.strip() for x in row["Source_IDs"].split(";") if x.strip()]
        bom_mech_ids.extend(ids)
        missing_ids = [i for i in ids if i not in mech_by_id]
        if missing_ids:
            fail(f"{bid}: unknown mechanical Source_IDs {missing_ids}")
            continue
        expected_qty = sum(int(mech_by_id[i]["Qty"]) for i in ids)
        if int(row["Qty_Per_Lamp"]) != expected_qty:
            fail(f"{bid}: Qty_Per_Lamp={row['Qty_Per_Lamp']} != MECH_PARTS sum={expected_qty}")
        expected_amort = sum(Decimal(mech_by_id[i]["Ext_Price_GBP_exVAT"]) for i in ids)
        if Decimal(row["Ext_Price_Amort_GBP_exVAT"]) != expected_amort:
            fail(f"{bid}: Ext_Price_Amort={row['Ext_Price_Amort_GBP_exVAT']} != MECH_PARTS sum={expected_amort}")
        if set(ids) & printed_ids:
            if row["Include_In_Total"] != "No" or Decimal(row["Ext_Price_Amort_GBP_exVAT"]) != 0:
                fail(f"{bid}: 3D-printed part must be Include_In_Total=No and £0.00")

    if len(bom_mech_ids) != len(set(bom_mech_ids)):
        fail("Duplicate mechanical Source_IDs in BOM")
    if set(bom_mech_ids) != set(mech_by_id):
        fail(f"Mechanical Part_ID mismatch: missing={sorted(set(mech_by_id) - set(bom_mech_ids))}")

    # 5. Exact penny arithmetic & supplier checks
    for row in bom_rows:
        bid = row["BOM_ID"]
        qty = int(row["Qty_Per_Lamp"])
        moq = int(row["MOQ_Pack_Qty"])
        packs = int(row["Packs_1Off"])
        order_qty = int(row["Order_Qty_1Off"])

        unit_amort = Decimal(row["Unit_Price_Amort_GBP_exVAT"])
        pack_1off = Decimal(row["Pack_Price_1Off_GBP_exVAT"])
        ext_amort = Decimal(row["Ext_Price_Amort_GBP_exVAT"])
        ext_1off = Decimal(row["Ext_Price_1Off_GBP_exVAT"])
        ext_amort_vat = Decimal(row["Ext_Price_Amort_GBP_incVAT"])
        ext_1off_vat = Decimal(row["Ext_Price_1Off_GBP_incVAT"])

        if order_qty != packs * moq:
            fail(f"{bid}: Order_Qty_1Off ({order_qty}) != Packs_1Off*MOQ ({packs}*{moq})")
        if round2(Decimal(qty) * unit_amort) != ext_amort:
            fail(f"{bid}: round({qty} * {unit_amort}, 2) != {ext_amort}")
        if round2(Decimal(packs) * pack_1off) != ext_1off:
            fail(f"{bid}: round({packs} * {pack_1off}, 2) != {ext_1off}")
        if round2(ext_amort * VAT_RATE) != ext_amort_vat:
            fail(f"{bid}: round({ext_amort} * 1.20, 2) != {ext_amort_vat}")
        if round2(ext_1off * VAT_RATE) != ext_1off_vat:
            fail(f"{bid}: round({ext_1off} * 1.20, 2) != {ext_1off_vat}")

        if row["Include_In_Total"] == "Yes":
            if order_qty < qty:
                fail(f"{bid}: Order_Qty_1Off ({order_qty}) < Qty_Per_Lamp ({qty})")
            if ext_1off < ext_amort:
                fail(f"{bid}: Ext_Price_1Off ({ext_1off}) < Ext_Price_Amort ({ext_amort})")
            if not row["Supplier_URL"].strip().startswith("https://"):
                fail(f"{bid}: Supplier_URL must start with https://")
        else:
            if any(x != Decimal("0.00") for x in (unit_amort, pack_1off, ext_amort, ext_1off, ext_amort_vat, ext_1off_vat)):
                fail(f"{bid}: Include_In_Total=No row has non-zero pricing")

    if errors:
        print("BOM VERIFICATION FAILED:", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 1

    def summarize(domain_filter: str | None = None) -> tuple[Decimal, Decimal]:
        rows = [
            r for r in bom_rows
            if r["Include_In_Total"] == "Yes"
            and (domain_filter is None or r["Domain"] == domain_filter)
        ]
        a_ex = sum((Decimal(r["Ext_Price_Amort_GBP_exVAT"]) for r in rows), Decimal("0.00"))
        o_ex = sum((Decimal(r["Ext_Price_1Off_GBP_exVAT"]) for r in rows), Decimal("0.00"))
        return a_ex, o_ex

    elec_a, elec_o = summarize("Electrical")
    harn_a, harn_o = summarize("Harness")
    pcb_a, pcb_o = summarize("PCB_Fab")
    mech_a, mech_o = summarize("Mechanical")
    tot_a, tot_o = summarize()

    # Also compute "Workshop Owned" 1-off total (excluding M3 hardware + PC thermal paste already on hand)
    owned_ex = sum(
        Decimal(r["Ext_Price_1Off_GBP_exVAT"])
        for r in bom_rows
        if r["Source_IDs"] in {"MECH-TIM-1", "MECH-FAST-M3"}
    )
    net_o = tot_o - owned_ex

    print("PASS: bom/bom.csv verified 1:1 across Rev 4.3 (75 RefDes, 61 PCBA, 2 Harness pigtails, 1 custom PCB, 16 MECH-* IDs)")
    print(f"  Electrical (75 RefDes incl. 8x Cu DTP stars): 1-Off = £{elec_o:.2f} ex VAT (£{round2(elec_o * VAT_RATE):.2f} inc VAT) | Amort = £{elec_a:.2f} ex VAT")
    print(f"  Harness (Pre-crimped 22 AWG JST-XH pigtails): 1-Off = £{harn_o:.2f} ex VAT (£{round2(harn_o * VAT_RATE):.2f} inc VAT) | Amort = £{harn_a:.2f} ex VAT")
    print(f"  PCB Fab + Economic PCBA (driver_pcb ONLY):    1-Off = £{pcb_o:.2f} ex VAT (£{round2(pcb_o * VAT_RATE):.2f} inc VAT) | Amort = £{pcb_a:.2f} ex VAT")
    print(f"  Mechanical (UVT PMMA + Bare Core, 16 IDs):    1-Off = £{mech_o:.2f} ex VAT (£{round2(mech_o * VAT_RATE):.2f} inc VAT) | Amort = £{mech_a:.2f} ex VAT")
    print(f"  TOTAL Rev 4.3 1-Off Build (All Purchased):    1-Off = £{tot_o:.2f} ex VAT (£{round2(tot_o * VAT_RATE):.2f} inc VAT) | Amort = £{tot_a:.2f} ex VAT (£{round2(tot_a * VAT_RATE):.2f} inc VAT)")
    print(f"  NET 1-Off Spend (Using Owned M3 + PC Paste):  1-Off = £{net_o:.2f} ex VAT (£{round2(net_o * VAT_RATE):.2f} inc VAT)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
