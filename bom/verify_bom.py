#!/usr/bin/env python3
"""Machine-verifiable audit script for bom/bom.csv against M1, M2, and M3 registries."""

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
LED_MCPCB_BOM_CSV = REPO_ROOT / "pcb_design" / "led_mcpcb_bom.csv"
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
            raise ValueError(
                f"{path}:{line_no}: expected {len(header)} columns, got {len(raw)}"
            )
        rows.append(dict(zip(header, raw)))
    return header, rows


def main() -> int:
    errors: list[str] = []

    def fail(msg: str) -> None:
        errors.append(msg)

    # 1. Load all files
    bom_cols, bom_rows = load_csv(BOM_CSV)
    if bom_cols != EXPECTED_COLUMNS:
        fail(f"bom.csv columns mismatch: got {bom_cols}, expected {EXPECTED_COLUMNS}")

    _, comp_rows = load_csv(COMP_IDS_CSV)
    _, drv_rows = load_csv(DRIVER_BOM_CSV)
    _, pcba_rows = load_csv(DRIVER_PCBA_CSV)
    _, mcpcb_rows = load_csv(LED_MCPCB_BOM_CSV)
    _, mech_rows = load_csv(MECH_PARTS_CSV)

    # 2. Check BOM_ID uniqueness, Build_Tier, Include_In_Total
    seen_bom_ids: set[str] = set()
    for idx, row in enumerate(bom_rows, start=2):
        bid = row["BOM_ID"].strip()
        if not bid:
            fail(f"Row {idx}: empty BOM_ID")
        elif bid in seen_bom_ids:
            fail(f"Row {idx}: duplicate BOM_ID {bid}")
        seen_bom_ids.add(bid)

        if row["Build_Tier"] != "CORE":
            fail(f"{bid}: expected Build_Tier='CORE' (unified Rev 4.0 Dual SK 578/50 SA baseline), got {row['Build_Tier']!r}")
        if row["Include_In_Total"] not in {"Yes", "No"}:
            fail(f"{bid}: invalid Include_In_Total {row['Include_In_Total']!r}")

    # 3. Electrical 72-RefDes 1:1 parity
    comp_by_ref = {r["RefDes"].strip(): r for r in comp_rows}
    drv_by_ref = {r["Designator"].strip(): r for r in drv_rows}
    pcba_refs = {r["Designator"].strip() for r in pcba_rows}

    if len(comp_rows) != 72:
        fail(f"COMPONENT_IDS.csv expected 72 rows, got {len(comp_rows)}")
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
                    fail(
                        f"{bid} ({ref}): MPN mismatch: bom={row['MPN_or_Part']!r} vs comp={expected_mpn!r}"
                    )
        bom_elec_refs.extend(refs)

    if len(bom_elec_refs) != len(set(bom_elec_refs)):
        fail("Duplicate RefDes across Electrical BOM rows")
    if set(bom_elec_refs) != set(comp_by_ref):
        missing = sorted(set(comp_by_ref) - set(bom_elec_refs))
        extra = sorted(set(bom_elec_refs) - set(comp_by_ref))
        fail(f"Electrical RefDes set mismatch: missing={missing}, extra={extra}")

    # Verify PCBA 56-part populated subset (62 On-PCB minus 6 PCB features TP1/TP2/H1..H4) and Off-Board 10-part subset
    off_board_expected = {"D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8", "SW1", "SW1_BOOT"}
    pcb_features = {"TP1", "TP2", "H1", "H2", "H3", "H4"}
    on_pcb_from_comp = {
        r["RefDes"].strip() for r in comp_rows if r["Mounting"].strip() == "On-PCB"
    }
    if (on_pcb_from_comp - pcb_features) != pcba_refs or len(pcba_refs) != 56:
        fail(f"Populated On-PCB 56-RefDes subset does not match driver_pcb_bom_pcba.csv (got {len(pcba_refs)})")
    if set(comp_by_ref) - on_pcb_from_comp != off_board_expected:
        fail("Off-board RefDes subset mismatch")

    # Verify led_mcpcb_bom.csv (D_UV = 4, D_VIS = 4)
    mcpcb_by_des = {r["Designator"].strip(): r for r in mcpcb_rows}
    if set(mcpcb_by_des) != {"D_UV", "D_VIS"}:
        fail(f"led_mcpcb_bom.csv expected D_UV/D_VIS, got {set(mcpcb_by_des)}")
    if int(mcpcb_by_des["D_UV"]["Qty_Per_Lamp_4x"]) != 4:
        fail("led_mcpcb_bom.csv D_UV Qty_Per_Lamp_4x != 4")
    if int(mcpcb_by_des["D_VIS"]["Qty_Per_Lamp_4x"]) != 4:
        fail("led_mcpcb_bom.csv D_VIS Qty_Per_Lamp_4x != 4")

    # Check TP1/TP2 and H1..H4 are zero-cost excluded PCB features
    for ref_group in ({"TP1", "TP2"}, {"H1", "H2", "H3", "H4"}):
        matched = [
            r
            for r in bom_elec_rows
            if set(x.strip() for x in r["RefDes_List"].split(";")) == ref_group
        ]
        if len(matched) != 1:
            fail(f"Expected single BOM row for PCB feature {sorted(ref_group)}")
        elif matched[0]["Include_In_Total"] != "No" or Decimal(matched[0]["Ext_Price_Amort_GBP_exVAT"]) != 0:
            fail(f"PCB feature {sorted(ref_group)} must have Include_In_Total=No and £0.00")

    # 4. PCB Fabrication rows & Zero Double-Counting Guard
    pcb_rows = {r["BOM_ID"]: r for r in bom_rows if r["Domain"] == "PCB_Fab"}
    if set(pcb_rows) != {"PCB-01", "PCB-02"}:
        fail(f"Expected PCB-01 and PCB-02 in PCB_Fab domain, got {set(pcb_rows)}")
    if pcb_rows["PCB-01"]["Source_IDs"] != "driver_pcb" or pcb_rows["PCB-01"]["Include_In_Total"] != "Yes":
        fail("PCB-01 must represent driver_pcb with Include_In_Total=Yes")
    pcb02 = pcb_rows["PCB-02"]
    if (
        pcb02["Source_IDs"] != "led_mcpcb"
        or pcb02["Include_In_Total"] != "No"
        or int(pcb02["Qty_Per_Lamp"]) != 4
        or Decimal(pcb02["Ext_Price_Amort_GBP_exVAT"]) != 0
        or Decimal(pcb02["Ext_Price_1Off_GBP_exVAT"]) != 0
        or "MECH-10" not in pcb02["Notes"]
        or "MECH-MCPCB-1..4" not in pcb02["Notes"]
    ):
        fail("PCB-02 must cross-reference MECH-10 (MECH-MCPCB-1..4) with Include_In_Total=No and £0.00")

    # 5. Mechanical 29-Part 1:1 Parity
    mech_by_id = {r["Part_ID"].strip(): r for r in mech_rows}
    if len(mech_by_id) != 29:
        fail(f"MECH_PARTS.csv expected 29 rows, got {len(mech_by_id)}")

    bom_mech_primary = [r for r in bom_rows if r["Domain"] == "Mechanical"]
    bom_harn_rows = [r for r in bom_rows if r["Domain"] == "Harness"]
    if len(bom_harn_rows) != 3:
        fail(f"Expected 3 Harness rows (XHP-2, XHP-3, SXH-001T-P0.6), got {len(bom_harn_rows)}")

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
            fail(
                f"{bid}: Ext_Price_Amort={row['Ext_Price_Amort_GBP_exVAT']} != MECH_PARTS sum={expected_amort}"
            )
        if set(ids) & {"MECH-CAP-BOT", "MECH-CAP-TOP"}:
            if row["Include_In_Total"] != "No" or Decimal(row["Ext_Price_Amort_GBP_exVAT"]) != 0:
                fail(f"{bid}: R4 3D-printed cap must be Include_In_Total=No and £0.00")

    if len(bom_mech_ids) != len(set(bom_mech_ids)):
        fail("Duplicate mechanical Source_IDs in BOM")
    if set(bom_mech_ids) != set(mech_by_id):
        missing = sorted(set(mech_by_id) - set(bom_mech_ids))
        extra = sorted(set(bom_mech_ids) - set(mech_by_id))
        fail(f"Mechanical Part_ID mismatch: missing={missing}, extra={extra}")

    # 6. Exact deterministic arithmetic, MOQ, and supplier URL checks on every row
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
                fail(f"{bid}: Ext_Price_1Off_GBP_exVAT ({ext_1off}) < Ext_Price_Amort_GBP_exVAT ({ext_amort})")
            if moq <= 0 or order_qty % moq != 0:
                fail(f"{bid}: Order_Qty_1Off ({order_qty}) not a multiple of MOQ ({moq})")
            sup = row["UK_Supplier"].strip()
            url = row["Supplier_URL"].strip()
            if not sup or sup.startswith("N/A"):
                fail(f"{bid}: missing UK_Supplier ({sup!r})")
            if not url.startswith("https://"):
                fail(f"{bid}: Supplier_URL must start with https:// (got {url!r})")
        else:
            if any(x != Decimal("0.00") for x in (unit_amort, pack_1off, ext_amort, ext_1off, ext_amort_vat, ext_1off_vat)):
                fail(f"{bid}: Include_In_Total=No row has non-zero pricing")

    if errors:
        print("BOM VERIFICATION FAILED:", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 1

    # 7. Compute and print exact verified totals
    def summarize(tiers: set[str], domain_filter: str | None = None) -> tuple[Decimal, Decimal, Decimal, Decimal]:
        rows = [
            r
            for r in bom_rows
            if r["Include_In_Total"] == "Yes"
            and r["Build_Tier"] in tiers
            and (domain_filter is None or r["Domain"] == domain_filter)
        ]
        a_ex = sum((Decimal(r["Ext_Price_Amort_GBP_exVAT"]) for r in rows), Decimal("0.00"))
        o_ex = sum((Decimal(r["Ext_Price_1Off_GBP_exVAT"]) for r in rows), Decimal("0.00"))
        a_vat_rows = sum((Decimal(r["Ext_Price_Amort_GBP_incVAT"]) for r in rows), Decimal("0.00"))
        o_vat_rows = sum((Decimal(r["Ext_Price_1Off_GBP_incVAT"]) for r in rows), Decimal("0.00"))
        return a_ex, o_ex, a_vat_rows, o_vat_rows

    elec_a_ex, elec_o_ex, elec_a_vr, elec_o_vr = summarize({"CORE"}, "Electrical")
    harn_a_ex, harn_o_ex, harn_a_vr, harn_o_vr = summarize({"CORE"}, "Harness")
    pcb_a_ex, pcb_o_ex, pcb_a_vr, pcb_o_vr = summarize({"CORE"}, "PCB_Fab")
    mech_a_ex, mech_o_ex, mech_a_vr, mech_o_vr = summarize({"CORE"}, "Mechanical")
    tot_a_ex, tot_o_ex, tot_a_vr, tot_o_vr = summarize({"CORE"})

    print("PASS: bom/bom.csv verified 1:1 across Rev 4.0 Option 2 (72 RefDes, 56 PCBA, 3 Harness, 2 PCB fab, 29 MECH-* IDs)")
    print(f"  Electrical (72 RefDes):        Amort = £{elec_a_ex:.2f} ex VAT (inv incVAT £{round2(elec_a_ex * VAT_RATE):.2f}) | 1-Off = £{elec_o_ex:.2f} ex VAT (inv incVAT £{round2(elec_o_ex * VAT_RATE):.2f})")
    print(f"  Harness (JST-XH plugs/crimps): Amort = £{harn_a_ex:.2f} ex VAT (inv incVAT £{round2(harn_a_ex * VAT_RATE):.2f}) | 1-Off = £{harn_o_ex:.2f} ex VAT (inv incVAT £{round2(harn_o_ex * VAT_RATE):.2f})")
    print(f"  PCB Fab (PCB-01; PCB-02=£0):   Amort = £{pcb_a_ex:.2f} ex VAT (inv incVAT £{round2(pcb_a_ex * VAT_RATE):.2f}) | 1-Off = £{pcb_o_ex:.2f} ex VAT (inv incVAT £{round2(pcb_o_ex * VAT_RATE):.2f})")
    print(f"  Mechanical (Dual SK 578/50):   Amort = £{mech_a_ex:.2f} ex VAT (inv incVAT £{round2(mech_a_ex * VAT_RATE):.2f}) | 1-Off = £{mech_o_ex:.2f} ex VAT (inv incVAT £{round2(mech_o_ex * VAT_RATE):.2f})")
    print(f"  TOTAL Rev 4.0 Lamp Build:      Amort = £{tot_a_ex:.2f} ex VAT (inv incVAT £{round2(tot_a_ex * VAT_RATE):.2f}; row incVAT £{tot_a_vr:.2f}) | 1-Off = £{tot_o_ex:.2f} ex VAT (inv incVAT £{round2(tot_o_ex * VAT_RATE):.2f}; row incVAT £{tot_o_vr:.2f})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
