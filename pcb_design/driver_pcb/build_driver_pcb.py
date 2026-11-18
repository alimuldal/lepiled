#!/usr/bin/env python3
"""
Reproducible KiCad 9 generator for Board 1: Driver & Protection PCB (pcb_design/driver_pcb/).
- 36.0 x 46.0 mm, 2-layer 1.6 mm FR4 (1 oz Cu), 2.0 mm corner radii.
- H1..H4 at (+/-14.0, +/-19.0) mm: 2.7 mm PTH drill, 5.5 mm pad tied to GND.
- 1:1 parity across ALL 71 RefDes (61 On-PCB + 10 Off-Board marked on_board=no, in_bom=yes, dnp=yes)
  and ALL 36 canonical nets from circuit_design/COMPONENT_IDS.csv & lepiled_schematic.cir.
- Full compliance with circuit_design/INTERFACE_CONTRACT.md Sec. 1.1-1.3.
"""

import csv
import heapq
import json
import math
import subprocess
import uuid
import zipfile
from pathlib import Path

import pcbnew

BASE_DIR = Path(__file__).resolve().parent
PCB_DESIGN_DIR = BASE_DIR.parent
REPO_ROOT = PCB_DESIGN_DIR.parent
COMPONENT_CSV = REPO_ROOT / "circuit_design" / "COMPONENT_IDS.csv"
GERBER_DIR = PCB_DESIGN_DIR / "gerbers" / "driver_pcb"
RENDER_DIR = BASE_DIR / "renders"
FP_LIB_DIR = BASE_DIR / "lepiled.pretty"

CX, CY = 100.0, 100.0


def uid(name: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"lepiled-driver-{name}"))


def mm(v: float) -> int:
    return pcbnew.FromMM(v)


def kpt(xm: float, ym: float) -> pcbnew.VECTOR2I:
    return pcbnew.VECTOR2I(mm(CX + xm), mm(CY - ym))


def lpt(xm: float, ym: float) -> pcbnew.VECTOR2I:
    return pcbnew.VECTOR2I(mm(xm), mm(-ym))


def lset(*layers) -> pcbnew.LSET:
    s = pcbnew.LSET()
    for lyr in layers:
        s.addLayer(lyr)
    return s


# ---------------------------------------------------------------------------
# 1. Library tables, .kicad_pro (with Netclasses), and .kicad_dru
# ---------------------------------------------------------------------------

def write_lib_tables():
    (BASE_DIR / "sym-lib-table").write_text(
        '(sym_lib_table\n  (version 7)\n'
        '  (lib (name "lepiled")(type "KiCad")(uri "${KIPRJMOD}/lepiled.kicad_sym")(options "")(descr "LepiLED Driver symbols"))\n)\n'
    )
    (BASE_DIR / "fp-lib-table").write_text(
        '(fp_lib_table\n  (version 7)\n'
        '  (lib (name "lepiled")(type "KiCad")(uri "${KIPRJMOD}/lepiled.pretty")(options "")(descr "LepiLED Driver footprints"))\n)\n'
    )


def write_kicad_pro():
    def nc_entry(name, clearance, track_width, via_d=0.6, via_drill=0.3, prio=0):
        return {
            "bus_width": 12,
            "clearance": clearance,
            "diff_pair_gap": 0.25,
            "diff_pair_via_gap": 0.25,
            "diff_pair_width": 0.2,
            "line_style": 0,
            "microvia_diameter": 0.3,
            "microvia_drill": 0.1,
            "name": name,
            "pcb_color": "rgba(0, 0, 0, 0.000)",
            "priority": prio,
            "schematic_color": "rgba(0, 0, 0, 0.000)",
            "track_width": track_width,
            "via_diameter": via_d,
            "via_drill": via_drill,
            "wire_width": 6,
        }

    netclass_assignments = {
        "VBUS": ["Power_5V"],
        "VBUS_FUSED": ["Power_5V"],
        "V_MID": ["Power_5V"],
        "VIN_PROT": ["Power_5V"],
        "SW1_NODE": ["Power_SW"],
        "SW2_NODE": ["Power_SW"],
        "VOUT1": ["Power_HV"],
        "VOUT2": ["Power_HV"],
        "UV_RET": ["Power_HV"],
        "VIS_RET": ["Power_HV"],
    }
    for sig in [
        "CC1", "CC2", "EN1_NET", "EN2_NET", "DIM2_NET", "SW_UV_EN",
        "Q1_GATE", "Q2_BASE", "Q3_BASE", "Q3_EMIT", "Q4_BASE",
        "OVP_SENSE", "OVP_K", "OVP_DRV", "OVP_DRV_GATE", "OVP_HYS",
        "FB1_NET", "FB2_NET",
    ]:
        netclass_assignments[sig] = ["Signal"]

    pro = {
        "board": {
            "design_settings": {
                "defaults": {
                    "board_outline_line_width": 0.1,
                    "copper_line_width": 0.2,
                    "silk_line_width": 0.12,
                    "silk_text_size_h": 0.7,
                    "silk_text_size_v": 0.7,
                    "silk_text_thickness": 0.12,
                },
                "diff_pair_dimensions": [],
                "drc_exclusions": [],
                "rules": {
                    "min_clearance": 0.18,
                    "min_copper_edge_clearance": 0.30,
                    "min_hole_clearance": 0.25,
                    "min_silk_clearance": 0.10,
                    "min_text_height": 0.50,
                    "min_through_hole_diameter": 0.28,
                    "min_track_width": 0.25,
                    "min_via_annulus": 0.12,
                    "min_via_diameter": 0.55,
                    "solder_mask_clearance": 0.05,
                },
                "track_widths": [0.25, 0.4, 0.5, 0.6, 1.0, 1.5],
                "via_dimensions": [
                    {"diameter": 0.6, "drill": 0.3},
                    {"diameter": 0.8, "drill": 0.4},
                ],
            },
            "layer_presets": [],
        },
        "boards": [],
        "libraries": {"pinned_footprint_libs": ["lepiled"], "pinned_symbol_libs": ["lepiled"]},
        "meta": {"filename": "driver_pcb.kicad_pro", "version": 1},
        "net_settings": {
            "classes": [
                nc_entry("Default", 0.20, 0.30, 0.60, 0.30, 2147483647),
                nc_entry("Power_5V", 0.20, 1.50, 0.80, 0.40, 10),
                nc_entry("Power_SW", 0.22, 1.00, 0.60, 0.30, 20),
                nc_entry("Power_HV", 0.25, 0.60, 0.80, 0.40, 30),
                nc_entry("Signal", 0.20, 0.25, 0.60, 0.30, 40),
            ],
            "meta": {"version": 3},
            "net_colors": None,
            "netclass_assignments": netclass_assignments,
            "netclass_patterns": [
                {"netclass": "Power_5V", "pattern": "VBUS*"},
                {"netclass": "Power_5V", "pattern": "V_MID"},
                {"netclass": "Power_5V", "pattern": "VIN_PROT"},
                {"netclass": "Power_SW", "pattern": "SW*_NODE"},
                {"netclass": "Power_HV", "pattern": "VOUT*"},
                {"netclass": "Power_HV", "pattern": "*_RET"},
                {"netclass": "Signal", "pattern": "EN*"},
                {"netclass": "Signal", "pattern": "DIM2_NET"},
                {"netclass": "Signal", "pattern": "SW_UV_EN"},
                {"netclass": "Signal", "pattern": "OVP_*"},
                {"netclass": "Signal", "pattern": "Q*_GATE"},
                {"netclass": "Signal", "pattern": "Q*_BASE"},
                {"netclass": "Signal", "pattern": "Q*_EMIT"},
                {"netclass": "Signal", "pattern": "FB*_NET"},
                {"netclass": "Signal", "pattern": "CC*"},
            ],
        },
        "pcbnew": {"page_layout_descr_file": ""},
        "schematic": {"legacy_lib_dir": "", "meta": {"version": 1}},
        "sheets": [[uid("root_sheet"), "Root"]],
        "text_variables": {},
    }
    (BASE_DIR / "driver_pcb.kicad_pro").write_text(json.dumps(pro, indent=2) + "\n")

    dru = """(version 1)

(rule "Power_SW clearance >= 0.25mm"
  (condition "A.NetClass == 'Power_SW' && !(A.Type == 'Pad' && B.Type == 'Pad')")
  (constraint clearance (min 0.25mm))
)

(rule "Power_HV clearance >= 0.25mm"
  (condition "A.NetClass == 'Power_HV'")
  (constraint clearance (min 0.25mm))
)

(rule "Signal track width >= 0.25mm"
  (condition "A.NetClass == 'Signal'")
  (constraint track_width (min 0.25mm))
)

(rule "Power_HV track width >= 0.60mm"
  (condition "A.NetClass == 'Power_HV'")
  (constraint track_width (min 0.60mm))
)

(rule "Power_SW pad-exit stub >= 0.35mm"
  (condition "A.NetClass == 'Power_SW'")
  (constraint track_width (min 0.35mm))
)

(rule "Power_SW trunk track width >= 1.00mm"
  (condition "A.NetClass == 'Power_SW' && !A.intersectsCourtyard('U1') && !A.intersectsCourtyard('U2')")
  (constraint track_width (min 1.00mm))
)

(rule "Power_5V pad-exit / sense tap >= 0.35mm"
  (condition "A.NetClass == 'Power_5V'")
  (constraint track_width (min 0.35mm))
)

(rule "Power_5V trunk track width >= 1.50mm"
  (condition "A.NetClass == 'Power_5V' && !A.insideArea('Sense_Tap_Area') && !A.intersectsCourtyard('J1') && !A.intersectsCourtyard('Q1A') && !A.intersectsCourtyard('Q1B') && !A.intersectsCourtyard('U1') && !A.intersectsCourtyard('U2')")
  (constraint track_width (min 1.50mm))
)
"""
    (BASE_DIR / "driver_pcb.kicad_dru").write_text(dru)


# ---------------------------------------------------------------------------
# 2. Custom Footprints in lepiled.pretty/
# ---------------------------------------------------------------------------

def _add_rect_crtyd_and_fab(fp, w, h, silk_lines=None, pin1_dot=None, fab_w=None, fab_h=None):
    fw = fab_w if fab_w is not None else w
    fh = fab_h if fab_h is not None else h
    for layer, lw, bw, bh in [
        (pcbnew.F_CrtYd, 0.05, w + 0.30, h + 0.30),
        (pcbnew.F_Fab, 0.10, fw, fh),
    ]:
        hx, hy = bw / 2.0, bh / 2.0
        for x0, y0, x1, y1 in [(-hx, hy, hx, hy), (hx, hy, hx, -hy), (hx, -hy, -hx, -hy), (-hx, -hy, -hx, hy)]:
            s = pcbnew.PCB_SHAPE(fp)
            s.SetShape(pcbnew.SHAPE_T_SEGMENT)
            s.SetLayer(layer)
            s.SetWidth(mm(lw))
            s.SetStart(lpt(x0, y0))
            s.SetEnd(lpt(x1, y1))
            fp.Add(s)
    if silk_lines:
        for x0, y0, x1, y1 in silk_lines:
            s = pcbnew.PCB_SHAPE(fp)
            s.SetShape(pcbnew.SHAPE_T_SEGMENT)
            s.SetLayer(pcbnew.F_SilkS)
            s.SetWidth(mm(0.12))
            s.SetStart(lpt(x0, y0))
            s.SetEnd(lpt(x1, y1))
            fp.Add(s)
    if pin1_dot:
        c = pcbnew.PCB_SHAPE(fp)
        c.SetShape(pcbnew.SHAPE_T_CIRCLE)
        c.SetLayer(pcbnew.F_SilkS)
        c.SetWidth(mm(0.12))
        c.SetFilled(True)
        c.SetCenter(lpt(pin1_dot[0], pin1_dot[1]))
        c.SetEnd(lpt(pin1_dot[0] + 0.18, pin1_dot[1]))
        fp.Add(c)


def _setup_fp_texts(fp, ref_xy=(0.0, 2.2), val_xy=(0.0, -2.2), ref_layer=pcbnew.F_SilkS, ref_sz=0.65):
    fp.Reference().SetPosition(lpt(*ref_xy))
    fp.Reference().SetLayer(ref_layer)
    fp.Reference().SetTextSize(pcbnew.VECTOR2I(mm(ref_sz), mm(ref_sz)))
    fp.Reference().SetTextThickness(mm(0.11))
    fp.Value().SetPosition(lpt(*val_xy))
    fp.Value().SetLayer(pcbnew.F_Fab)
    fp.Value().SetTextSize(pcbnew.VECTOR2I(mm(0.60), mm(0.60)))


def _smd_pad(fp, num, xm, ym, w, h, layers=None, mask_margin=0.05, roundrect=0.0):
    p = pcbnew.PAD(fp)
    p.SetNumber(str(num))
    p.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
    if roundrect > 0:
        p.SetShape(pcbnew.PAD_SHAPE_ROUNDRECT)
        p.SetRoundRectCornerRadius(mm(roundrect))
    else:
        p.SetShape(pcbnew.PAD_SHAPE_RECT)
    p.SetPosition(lpt(xm, ym))
    p.SetSize(pcbnew.VECTOR2I(mm(w), mm(h)))
    p.SetLayerSet(layers if layers is not None else lset(pcbnew.F_Cu, pcbnew.F_Mask, pcbnew.F_Paste))
    p.SetLocalSolderMaskMargin(mm(mask_margin))
    fp.Add(p)
    return p


def create_footprints():
    FP_LIB_DIR.mkdir(parents=True, exist_ok=True)
    io = pcbnew.PCB_IO_KICAD_SEXPR()

    def save(fp, name):
        fp.SetFPID(pcbnew.LIB_ID("lepiled", name))
        io.FootprintSave(str(FP_LIB_DIR), fp)

    # 1. TI LM3410XMY/NOPB (DGN0008A HVSSOP-8-1EP) - lm3410.pdf pp. 50-51
    fp = pcbnew.FOOTPRINT(None)
    fp.SetReference("U")
    fp.SetValue("LM3410XMY")
    fp.SetAttributes(pcbnew.FP_SMD)
    y_rows = [+0.975, +0.325, -0.325, -0.975]
    for idx, y in enumerate(y_rows, start=1):
        _smd_pad(fp, idx, -2.20, y, 1.40, 0.42, roundrect=0.08)
    for idx, y in enumerate(reversed(y_rows), start=5):
        _smd_pad(fp, idx, +2.20, y, 1.40, 0.42, roundrect=0.08)
    _smd_pad(fp, 9, 0.0, 0.0, 2.00, 3.00, layers=lset(pcbnew.F_Cu), mask_margin=0.0)
    _smd_pad(fp, 9, 0.0, 0.0, 1.88, 2.00, layers=lset(pcbnew.F_Cu, pcbnew.F_Mask, pcbnew.F_Paste), mask_margin=0.0)
    _add_rect_crtyd_and_fab(
        fp, 5.80, 3.20,
        silk_lines=[(-1.35, +1.70, +1.35, +1.70), (-1.35, -1.70, +1.35, -1.70)],
        pin1_dot=(-1.65, +1.75), fab_w=3.00, fab_h=3.00,
    )
    _setup_fp_texts(fp, ref_xy=(-2.15, -2.15), val_xy=(0.0, +2.35))
    save(fp, "TI_LM3410XMY_DGN0008A")

    # 2. SOT-23-3 variants
    def make_sot23(name, val, pad_w, pad_h, x_bot, y_bot, y_top):
        sfp = pcbnew.FOOTPRINT(None)
        sfp.SetReference("Q")
        sfp.SetValue(val)
        sfp.SetAttributes(pcbnew.FP_SMD)
        _smd_pad(sfp, 1, -x_bot, y_bot, pad_w, pad_h, roundrect=0.08)
        _smd_pad(sfp, 2, +x_bot, y_bot, pad_w, pad_h, roundrect=0.08)
        _smd_pad(sfp, 3, 0.0, y_top, pad_w, pad_h, roundrect=0.08)
        # Keep silk outside pads cleanly
        _add_rect_crtyd_and_fab(
            sfp, 2.90, 2.95,
            silk_lines=[(-1.60, -0.15, -1.60, +0.55), (+1.60, -0.15, +1.60, +0.55)],
            pin1_dot=(-1.68, -1.45), fab_w=2.90, fab_h=1.30,
        )
        _setup_fp_texts(sfp, ref_xy=(0.0, +2.10), val_xy=(0.0, -2.10), ref_layer=pcbnew.F_Fab, ref_sz=0.60)
        save(sfp, name)

    make_sot23("TI_SOT-23-3_DBZ", "TL431AIDBZR", 0.60, 1.25, 0.95, -1.05, +1.05)
    make_sot23("Diodes_SOT-23-3_DMG2305UX", "DMG2305UX-7", 0.80, 0.90, 0.95, -1.00, +1.00)
    make_sot23("onsemi_SOT-23-3_Case318", "SOT-23-3", 0.56, 0.95, 0.95, -0.975, +0.975)

    # 3. 2-pin Diodes (Pin 1 = Cathode left -X, Pin 2 = Anode right +X)
    def make_diode(name, val, pw, ph, ctc, bw, bh, silk_bar=True, silk_u=False):
        dfp = pcbnew.FOOTPRINT(None)
        dfp.SetReference("D")
        dfp.SetValue(val)
        dfp.SetAttributes(pcbnew.FP_SMD)
        _smd_pad(dfp, 1, -ctc / 2.0, 0.0, pw, ph, roundrect=0.10)
        _smd_pad(dfp, 2, +ctc / 2.0, 0.0, pw, ph, roundrect=0.10)
        ky = max(bh, ph) / 2.0 + 0.35
        kx = ctc / 2.0 + pw / 2.0 + 0.28
        if silk_u:
            uy = ph / 2.0 + 0.25
            silk = [(-kx, -uy, -kx, +uy), (-kx, +uy, -0.75, +uy), (-kx, -uy, -0.75, -uy)]
        elif silk_bar:
            silk = [(-kx, -ph / 2.0, -kx, +ph / 2.0)]
        else:
            silk = None
        _add_rect_crtyd_and_fab(
            dfp, ctc + pw, max(bh, ph),
            silk_lines=silk,
            fab_w=bw, fab_h=bh,
        )
        _setup_fp_texts(dfp, ref_xy=(0.0, ky + 0.65), val_xy=(0.0, -ky - 0.65), ref_layer=pcbnew.F_Fab, ref_sz=0.65)
        save(dfp, name)

    make_diode("D_SMA_DO-214AC", "B340A-13-F", 1.60, 1.70, 4.00, 4.30, 2.60, silk_bar=True)
    make_diode("D_SMB_DO-214AA", "SMBJ5.0A-E3/5B", 1.72, 2.20, 3.88, 4.35, 3.60, silk_bar=True)
    make_diode("D_SOD-123", "BZT52C", 0.90, 0.95, 3.15, 2.70, 1.55, silk_bar=True, silk_u=True)

    # 4. Inductors, Polyfuse, Resistors, Capacitors
    def make_2pad(name, ref_pfx, val, pw, ph, ctc, bw, bh, ref_lyr=pcbnew.F_SilkS, has_silk=True, ref_center=False):
        pfp = pcbnew.FOOTPRINT(None)
        pfp.SetReference(ref_pfx)
        pfp.SetValue(val)
        pfp.SetAttributes(pcbnew.FP_SMD)
        _smd_pad(pfp, 1, -ctc / 2.0, 0.0, pw, ph, roundrect=0.08)
        _smd_pad(pfp, 2, +ctc / 2.0, 0.0, pw, ph, roundrect=0.08)
        sy = max(bh, ph) / 2.0 + 0.30
        _add_rect_crtyd_and_fab(
            pfp, max(ctc + pw, bw), max(bh, ph),
            silk_lines=[(-1.0, +sy, +1.0, +sy), (-1.0, -sy, +1.0, -sy)] if (ctc > 2.2 and has_silk) else None,
            fab_w=bw, fab_h=bh,
        )
        r_xy = (0.0, 0.0) if ref_center else (0.0, sy + 0.60)
        _setup_fp_texts(pfp, ref_xy=r_xy, val_xy=(0.0, -sy - 0.60), ref_layer=ref_lyr, ref_sz=0.65)
        save(pfp, name)

    make_2pad("Bourns_SRN6045", "L", "SRN6045-100M", 1.80, 5.00, 4.40, 6.00, 6.00, ref_lyr=pcbnew.F_Fab, has_silk=True)
    make_2pad("Bourns_MF_LSMF_2920", "F", "MF-LSMF500/16X", 2.00, 5.30, 6.60, 7.30, 5.10, ref_lyr=pcbnew.F_SilkS, has_silk=False, ref_center=True)
    make_2pad("R_1206", "R", "R_1206", 1.05, 1.80, 2.55, 3.20, 1.60, ref_lyr=pcbnew.F_Fab, has_silk=False)
    make_2pad("R_0805", "R", "R_0805", 0.95, 1.45, 1.95, 2.00, 1.25, ref_lyr=pcbnew.F_Fab, has_silk=False)
    make_2pad("R_0603", "R", "R_0603", 0.75, 1.00, 1.50, 1.55, 0.85, ref_lyr=pcbnew.F_Fab, has_silk=False)
    make_2pad("C_1206", "C", "C_1206", 1.15, 1.80, 2.65, 3.20, 1.60, ref_lyr=pcbnew.F_Fab, has_silk=False)
    make_2pad("C_1210", "C", "C_1210", 1.15, 2.70, 2.65, 3.20, 2.50, ref_lyr=pcbnew.F_Fab, has_silk=False)
    make_2pad("C_0603", "C", "C_0603", 0.80, 0.95, 1.60, 1.60, 0.80, ref_lyr=pcbnew.F_Fab, has_silk=False)

    # 5. GCT USB4085-GF-A (16 PTH + 4 oval slot TH shield tabs) - usb4085.pdf Sheets 1-2
    fp = pcbnew.FOOTPRINT(None)
    fp.SetReference("J")
    fp.SetValue("USB4085-GF-A")
    fp.SetAttributes(pcbnew.FP_THROUGH_HOLE)
    row_a = [("A1", -2.975), ("A4", -2.125), ("A5", -1.275), ("A6", -0.425),
             ("A7", +0.425), ("A8", +1.275), ("A9", +2.125), ("A12", +2.975)]
    row_b = [("B12", -2.975), ("B9", -2.125), ("B8", -1.275), ("B7", -0.425),
             ("B6", +0.425), ("B5", +1.275), ("B4", +2.125), ("B1", +2.975)]
    for pname, px in row_a:
        p = pcbnew.PAD(fp)
        p.SetNumber(pname)
        p.SetAttribute(pcbnew.PAD_ATTRIB_PTH)
        p.SetShape(pcbnew.PAD_SHAPE_OVAL)
        p.SetPosition(lpt(px, +1.35))
        p.SetSize(pcbnew.VECTOR2I(mm(0.65), mm(0.85)))
        p.SetDrillSize(pcbnew.VECTOR2I(mm(0.40), mm(0.40)))
        p.SetLayerSet(pcbnew.PAD.PTHMask())
        p.SetLocalSolderMaskMargin(mm(0.04))
        fp.Add(p)
    for pname, px in row_b:
        p = pcbnew.PAD(fp)
        p.SetNumber(pname)
        p.SetAttribute(pcbnew.PAD_ATTRIB_PTH)
        p.SetShape(pcbnew.PAD_SHAPE_OVAL)
        p.SetPosition(lpt(px, 0.00))
        p.SetSize(pcbnew.VECTOR2I(mm(0.65), mm(0.85)))
        p.SetDrillSize(pcbnew.VECTOR2I(mm(0.40), mm(0.40)))
        p.SetLayerSet(pcbnew.PAD.PTHMask())
        p.SetLocalSolderMaskMargin(mm(0.04))
        fp.Add(p)
    for sname, sx, sy, pw, ph, dw, dh in [
        ("SH1", -4.325, +0.37, 0.90, 2.40, 0.60, 2.10),
        ("SH2", +4.325, +0.37, 0.90, 2.40, 0.60, 2.10),
        ("SH3", -4.325, -3.01, 0.90, 1.70, 0.60, 1.40),
        ("SH4", +4.325, -3.01, 0.90, 1.70, 0.60, 1.40),
    ]:
        p = pcbnew.PAD(fp)
        p.SetNumber(sname)
        p.SetAttribute(pcbnew.PAD_ATTRIB_PTH)
        p.SetShape(pcbnew.PAD_SHAPE_OVAL)
        p.SetDrillShape(pcbnew.PAD_DRILL_SHAPE_OBLONG)
        p.SetPosition(lpt(sx, sy))
        p.SetSize(pcbnew.VECTOR2I(mm(pw), mm(ph)))
        p.SetDrillSize(pcbnew.VECTOR2I(mm(dw), mm(dh)))
        p.SetLayerSet(pcbnew.PAD.PTHMask())
        p.SetLocalSolderMaskMargin(mm(0.05))
        fp.Add(p)

    for x0, y0, x1, y1 in [(-4.47, +2.33, +4.47, +2.33), (+4.47, +2.33, +4.47, -6.84),
                           (+4.47, -6.84, -4.47, -6.84), (-4.47, -6.84, -4.47, +2.33)]:
        s = pcbnew.PCB_SHAPE(fp)
        s.SetShape(pcbnew.SHAPE_T_SEGMENT)
        s.SetLayer(pcbnew.F_Fab)
        s.SetWidth(mm(0.10))
        s.SetStart(lpt(x0, y0))
        s.SetEnd(lpt(x1, y1))
        fp.Add(s)
    for x0, y0, x1, y1 in [(-5.0, +2.55, +5.0, +2.55), (+5.0, +2.55, +5.0, -4.20),
                           (+5.0, -4.20, -5.0, -4.20), (-5.0, -4.20, -5.0, +2.55)]:
        s = pcbnew.PCB_SHAPE(fp)
        s.SetShape(pcbnew.SHAPE_T_SEGMENT)
        s.SetLayer(pcbnew.F_CrtYd)
        s.SetWidth(mm(0.05))
        s.SetStart(lpt(x0, y0))
        s.SetEnd(lpt(x1, y1))
        fp.Add(s)
    s = pcbnew.PCB_SHAPE(fp)
    s.SetShape(pcbnew.SHAPE_T_SEGMENT)
    s.SetLayer(pcbnew.F_SilkS)
    s.SetWidth(mm(0.12))
    s.SetStart(lpt(-3.6, +2.50))
    s.SetEnd(lpt(+3.6, +2.50))
    fp.Add(s)
    _setup_fp_texts(fp, ref_xy=(-5.65, +0.90), val_xy=(0.0, -4.50), ref_sz=0.70)
    save(fp, "GCT_USB4085_GF_A")

    # 6. JST XH Headers (B2B-XH-A 1.0mm drill, B3B-XH-A 0.9mm drill) - jst_xh.pdf pp. 2, 5
    def make_jst_xh(name, val, n_pins, drill_mm):
        jfp = pcbnew.FOOTPRINT(None)
        jfp.SetReference("J")
        jfp.SetValue(val)
        jfp.SetAttributes(pcbnew.FP_THROUGH_HOLE)
        pitch = 2.50
        span = (n_pins - 1) * pitch
        for i in range(n_pins):
            px = +span / 2.0 - i * pitch
            p = pcbnew.PAD(jfp)
            p.SetNumber(str(i + 1))
            p.SetAttribute(pcbnew.PAD_ATTRIB_PTH)
            p.SetShape(pcbnew.PAD_SHAPE_RECT if i == 0 else pcbnew.PAD_SHAPE_OVAL)
            p.SetPosition(lpt(px, 0.0))
            p.SetSize(pcbnew.VECTOR2I(mm(1.80), mm(2.00)))
            p.SetDrillSize(pcbnew.VECTOR2I(mm(drill_mm), mm(drill_mm)))
            p.SetLayerSet(pcbnew.PAD.PTHMask())
            p.SetLocalSolderMaskMargin(mm(0.05))
            jfp.Add(p)
        bw = (7.40 if n_pins == 2 else 9.90)
        hx = bw / 2.0
        for layer, lw, pad_e in [(pcbnew.F_SilkS, 0.12, 0.10), (pcbnew.F_Fab, 0.10, 0.0), (pcbnew.F_CrtYd, 0.05, 0.25)]:
            x0, x1, y0, y1 = -hx - pad_e, +hx + pad_e, -2.35 - pad_e, +3.40 + pad_e
            segs = [(x0, y1, x1, y1), (x1, y1, x1, y0), (x1, y0, x0, y0), (x0, y0, x0, y1)]
            if layer == pcbnew.F_SilkS:
                segs = [(x0, y1, x1, y1), (x1, y1, x1, y0), (x1, y0, +1.2, y0), (-1.2, y0, x0, y0), (x0, y0, x0, y1)]
            for ax, ay, bx, by in segs:
                s = pcbnew.PCB_SHAPE(jfp)
                s.SetShape(pcbnew.SHAPE_T_SEGMENT)
                s.SetLayer(layer)
                s.SetWidth(mm(lw))
                s.SetStart(lpt(ax, ay))
                s.SetEnd(lpt(bx, by))
                jfp.Add(s)
        c = pcbnew.PCB_SHAPE(jfp)
        c.SetShape(pcbnew.SHAPE_T_CIRCLE)
        c.SetLayer(pcbnew.F_SilkS)
        c.SetWidth(mm(0.12))
        c.SetFilled(True)
        c.SetCenter(lpt(+hx + 0.50, -1.50))
        c.SetEnd(lpt(+hx + 0.68, -1.50))
        jfp.Add(c)
        _setup_fp_texts(jfp, ref_xy=(0.0, -3.15), val_xy=(0.0, +4.10), ref_sz=0.70)
        save(jfp, name)

    make_jst_xh("JST_XH_B2B_P2.50mm", "B2B-XH-A", 2, 1.00)
    make_jst_xh("JST_XH_B3B_P2.50mm", "B3B-XH-A", 3, 0.90)

    # 7. TestPoint_Pad_D2.5mm
    fp = pcbnew.FOOTPRINT(None)
    fp.SetReference("TP")
    fp.SetValue("TestPoint_D2.5mm")
    fp.SetAttributes(pcbnew.FP_THROUGH_HOLE)
    p = pcbnew.PAD(fp)
    p.SetNumber("1")
    p.SetAttribute(pcbnew.PAD_ATTRIB_PTH)
    p.SetShape(pcbnew.PAD_SHAPE_CIRCLE)
    p.SetPosition(lpt(0.0, 0.0))
    p.SetSize(pcbnew.VECTOR2I(mm(2.50), mm(2.50)))
    p.SetDrillSize(pcbnew.VECTOR2I(mm(1.30), mm(1.30)))
    p.SetLayerSet(pcbnew.PAD.PTHMask())
    p.SetLocalSolderMaskMargin(mm(0.05))
    fp.Add(p)
    c = pcbnew.PCB_SHAPE(fp)
    c.SetShape(pcbnew.SHAPE_T_CIRCLE)
    c.SetLayer(pcbnew.F_CrtYd)
    c.SetWidth(mm(0.05))
    c.SetCenter(lpt(0.0, 0.0))
    c.SetEnd(lpt(1.40, 0.0))
    fp.Add(c)
    _setup_fp_texts(fp, ref_xy=(0.0, +1.95), val_xy=(0.0, -1.95), ref_sz=0.65)
    save(fp, "TestPoint_Pad_D2.5mm")

    # 8. MountingHole_2.7mm_M2.5_Pad5.5mm
    fp = pcbnew.FOOTPRINT(None)
    fp.SetReference("H")
    fp.SetValue("MountingHole_2.7mm_M2.5")
    fp.SetAttributes(pcbnew.FP_THROUGH_HOLE | pcbnew.FP_EXCLUDE_FROM_POS_FILES)
    p = pcbnew.PAD(fp)
    p.SetNumber("1")
    p.SetAttribute(pcbnew.PAD_ATTRIB_PTH)
    p.SetShape(pcbnew.PAD_SHAPE_CIRCLE)
    p.SetPosition(lpt(0.0, 0.0))
    p.SetSize(pcbnew.VECTOR2I(mm(5.50), mm(5.50)))
    p.SetDrillSize(pcbnew.VECTOR2I(mm(2.70), mm(2.70)))
    p.SetLayerSet(pcbnew.PAD.PTHMask())
    p.SetLocalSolderMaskMargin(mm(0.05))
    fp.Add(p)
    c = pcbnew.PCB_SHAPE(fp)
    c.SetShape(pcbnew.SHAPE_T_CIRCLE)
    c.SetLayer(pcbnew.F_CrtYd)
    c.SetWidth(mm(0.05))
    c.SetCenter(lpt(0.0, 0.0))
    c.SetEnd(lpt(2.85, 0.0))
    fp.Add(c)
    _setup_fp_texts(fp, ref_xy=(0.0, -3.40), val_xy=(0.0, +3.40), ref_layer=pcbnew.F_Fab, ref_sz=0.65)
    save(fp, "MountingHole_2.7mm_M2.5_Pad5.5mm")


# ---------------------------------------------------------------------------
# 3. KiCad Symbol Library & 71-RefDes Schematic
# ---------------------------------------------------------------------------

def _sym_2pin(name, ref_pfx, shape_kind):
    if shape_kind == "R":
        body = '(rectangle (start -1.016 2.54) (end 1.016 -2.54) (stroke (width 0.254) (type default)) (fill (type none)))'
        p1, p2 = '(at 0 5.08 270)', '(at 0 -5.08 90)'
        n1, n2 = '"~"', '"~"'
    elif shape_kind == "C":
        body = (
            '(polyline (pts (xy -2.032 0.762) (xy 2.032 0.762)) (stroke (width 0.3048) (type default)) (fill (type none)))\n'
            '      (polyline (pts (xy -2.032 -0.762) (xy 2.032 -0.762)) (stroke (width 0.3048) (type default)) (fill (type none)))'
        )
        p1, p2 = '(at 0 3.81 270)', '(at 0 -3.81 90)'
        n1, n2 = '"~"', '"~"'
    elif shape_kind == "L":
        body = '(rectangle (start -1.016 2.54) (end 1.016 -2.54) (stroke (width 0.254) (type default)) (fill (type background)))'
        p1, p2 = '(at 0 5.08 270)', '(at 0 -5.08 90)'
        n1, n2 = '"1"', '"2"'
    elif shape_kind == "F":
        body = (
            '(rectangle (start -1.27 2.54) (end 1.27 -2.54) (stroke (width 0.254) (type default)) (fill (type none)))\n'
            '      (polyline (pts (xy 0 2.54) (xy 0 -2.54)) (stroke (width 0.2032) (type default)) (fill (type none)))'
        )
        p1, p2 = '(at 0 5.08 270)', '(at 0 -5.08 90)'
        n1, n2 = '"1"', '"2"'
    else:
        body = (
            '(polyline (pts (xy -1.27 -1.27) (xy -1.27 1.27)) (stroke (width 0.254) (type default)) (fill (type none)))\n'
            '      (polyline (pts (xy 1.27 -1.27) (xy 1.27 1.27) (xy -1.27 0) (xy 1.27 -1.27)) (stroke (width 0.254) (type default)) (fill (type none)))'
        )
        p1, p2 = '(at -3.81 0 0)', '(at 3.81 0 180)'
        n1, n2 = '"K"', '"A"'
    return f"""  (symbol "{name}"
    (pin_names (offset 1.016) (hide yes))
    (exclude_from_sim no)
    (in_bom yes)
    (on_board yes)
    (property "Reference" "{ref_pfx}" (at 2.54 1.27 0) (effects (font (size 1.27 1.27))))
    (property "Value" "{name}" (at 2.54 -1.27 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "MPN" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (symbol "{name}_0_1"
      {body}
    )
    (symbol "{name}_1_1"
      (pin passive line {p1} (length 2.54) (name {n1} (effects (font (size 1.0 1.0)))) (number "1" (effects (font (size 1.0 1.0)))))
      (pin passive line {p2} (length 2.54) (name {n2} (effects (font (size 1.0 1.0)))) (number "2" (effects (font (size 1.0 1.0)))))
    )
  )"""


def _sym_led_offboard():
    return """  (symbol "LED_OffBoard"
    (pin_names (offset 1.016) (hide yes))
    (exclude_from_sim no)
    (in_bom yes)
    (on_board no)
    (property "Reference" "D" (at 0 3.81 0) (effects (font (size 1.27 1.27))))
    (property "Value" "LED" (at 0 -3.81 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "MPN" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (symbol "LED_OffBoard_0_1"
      (polyline (pts (xy 1.27 -1.27) (xy 1.27 1.27)) (stroke (width 0.254) (type default)) (fill (type none)))
      (polyline (pts (xy -1.27 -1.27) (xy -1.27 1.27) (xy 1.27 0) (xy -1.27 -1.27)) (stroke (width 0.254) (type default)) (fill (type none)))
    )
    (symbol "LED_OffBoard_1_1"
      (pin passive line (at -3.81 0 0) (length 2.54) (name "A" (effects (font (size 1.0 1.0)))) (number "1" (effects (font (size 1.0 1.0)))))
      (pin passive line (at 3.81 0 180) (length 2.54) (name "K" (effects (font (size 1.0 1.0)))) (number "2" (effects (font (size 1.0 1.0)))))
    )
  )"""


def _sym_box(name, ref_pfx, w_half, h_half, pins_spec, on_board="yes"):
    pin_txt = "\n".join(
        f'      (pin passive line (at {x:.2f} {y:.2f} {ang}) (length 2.54) (name "{pn}" (effects (font (size 1.0 1.0)))) (number "{num}" (effects (font (size 1.0 1.0)))))'
        for num, pn, x, y, ang in pins_spec
    )
    return f"""  (symbol "{name}"
    (pin_names (offset 1.016))
    (exclude_from_sim no)
    (in_bom yes)
    (on_board {on_board})
    (property "Reference" "{ref_pfx}" (at 0 {h_half + 1.27:.2f} 0) (effects (font (size 1.27 1.27))))
    (property "Value" "{name}" (at 0 {-h_half - 1.27:.2f} 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "MPN" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (symbol "{name}_0_1"
      (rectangle (start {-w_half:.2f} {h_half:.2f}) (end {w_half:.2f} {-h_half:.2f}) (stroke (width 0.254) (type default)) (fill (type background)))
    )
    (symbol "{name}_1_1"
{pin_txt}
    )
  )"""


def build_symbol_defs():
    return [
        _sym_2pin("R_Generic", "R", "R"),
        _sym_2pin("C_Generic", "C", "C"),
        _sym_2pin("L_Generic", "L", "L"),
        _sym_2pin("F_Polyfuse", "F", "F"),
        _sym_2pin("Diode_K_A", "D", "D"),
        _sym_led_offboard(),
        _sym_box("LM3410XMY_DGN", "U", 6.35, 8.89, [
            ("1", "NC1", -8.89, 5.08, 0),
            ("2", "PGND", -8.89, 2.54, 0),
            ("3", "VIN", -8.89, 0.00, 0),
            ("4", "DIM", -8.89, -2.54, 0),
            ("9", "DAP", -8.89, -5.08, 0),
            ("8", "NC2", 8.89, 5.08, 180),
            ("7", "SW", 8.89, 2.54, 180),
            ("6", "AGND", 8.89, 0.00, 180),
            ("5", "FB", 8.89, -2.54, 180),
        ]),
        _sym_box("TL431AIDBZR", "U", 5.08, 5.08, [
            ("1", "K", -7.62, 2.54, 0),
            ("2", "REF", -7.62, 0.00, 0),
            ("3", "A", -7.62, -2.54, 0),
        ]),
        _sym_box("PMOS_DMG2305UX", "Q", 5.08, 5.08, [
            ("1", "G", -7.62, 0.00, 0),
            ("2", "S", 7.62, 2.54, 180),
            ("3", "D", 7.62, -2.54, 180),
        ]),
        _sym_box("BJT_SOT23", "Q", 5.08, 5.08, [
            ("1", "B", -7.62, 0.00, 0),
            ("3", "C", 7.62, 2.54, 180),
            ("2", "E", 7.62, -2.54, 180),
        ]),
        _sym_box("BAV70_CC", "D", 5.08, 5.08, [
            ("1", "A1", -7.62, 2.54, 0),
            ("2", "A2", -7.62, -2.54, 0),
            ("3", "K", 7.62, 0.00, 180),
        ]),
        _sym_box("BAW56_CA", "D", 5.08, 5.08, [
            ("3", "A", -7.62, 0.00, 0),
            ("1", "K1", 7.62, 2.54, 180),
            ("2", "K2", 7.62, -2.54, 180),
        ]),
        _sym_box("USB4085_GFA", "J", 7.62, 24.13, [
            ("A4", "VBUS_A4", 10.16, 20.32, 180),
            ("A9", "VBUS_A9", 10.16, 17.78, 180),
            ("B4", "VBUS_B4", 10.16, 15.24, 180),
            ("B9", "VBUS_B9", 10.16, 12.70, 180),
            ("A5", "CC1", 10.16, 10.16, 180),
            ("B5", "CC2", 10.16, 7.62, 180),
            ("A1", "GND_A1", 10.16, 5.08, 180),
            ("A12", "GND_A12", 10.16, 2.54, 180),
            ("B1", "GND_B1", 10.16, 0.00, 180),
            ("B12", "GND_B12", 10.16, -2.54, 180),
            ("SH1", "SH1", 10.16, -5.08, 180),
            ("SH2", "SH2", 10.16, -7.62, 180),
            ("SH3", "SH3", 10.16, -10.16, 180),
            ("SH4", "SH4", 10.16, -12.70, 180),
            ("A6", "Dp1", -10.16, 15.24, 0),
            ("A7", "Dn1", -10.16, 12.70, 0),
            ("A8", "SBU1", -10.16, 10.16, 0),
            ("B6", "Dp2", -10.16, 7.62, 0),
            ("B7", "Dn2", -10.16, 5.08, 0),
            ("B8", "SBU2", -10.16, 2.54, 0),
        ]),
        _sym_box("JST_B2B_XH", "J", 5.08, 3.81, [
            ("1", "P1", 7.62, 1.27, 180),
            ("2", "P2", 7.62, -1.27, 180),
        ]),
        _sym_box("JST_B3B_XH", "J", 5.08, 5.08, [
            ("1", "P1", 7.62, 2.54, 180),
            ("2", "P2", 7.62, 0.00, 180),
            ("3", "P3", 7.62, -2.54, 180),
        ]),
        _sym_box("SW_100SP3T", "SW", 5.08, 6.35, [
            ("1", "UV_EN", -7.62, 3.81, 0),
            ("2", "COM", -7.62, 1.27, 0),
            ("3", "ALL_EN", -7.62, -1.27, 0),
            ("4", "BUSH", -7.62, -3.81, 0),
        ], on_board="no"),
        _sym_box("Mech_1Pin", "SW", 3.81, 2.54, [
            ("1", "MECH", -6.35, 0.00, 0),
        ], on_board="no"),
        _sym_box("Pad_1Pin", "TP", 2.54, 2.54, [
            ("1", "P1", -5.08, 0.00, 0),
        ]),
    ]


def write_kicad_sym(syms):
    body = "\n".join(syms)
    txt = f'(kicad_symbol_lib\n  (version 20241209)\n  (generator "kicad_symbol_editor")\n  (generator_version "9.0")\n{body}\n)\n'
    (BASE_DIR / "lepiled.kicad_sym").write_text(txt)


def _rot_pt(lx, ly, deg):
    r = math.radians(deg)
    rx = lx * math.cos(r) - ly * math.sin(r)
    ry = lx * math.sin(r) + ly * math.cos(r)
    return round(rx, 2), round(-ry, 2)


def write_kicad_sch(syms, comp_rows):
    root_uuid = uid("root_sheet")
    sym_pins = {
        "R_Generic": {"1": (0, 5.08), "2": (0, -5.08)},
        "C_Generic": {"1": (0, 3.81), "2": (0, -3.81)},
        "L_Generic": {"1": (0, 5.08), "2": (0, -5.08)},
        "F_Polyfuse": {"1": (0, 5.08), "2": (0, -5.08)},
        "Diode_K_A": {"1": (-3.81, 0), "2": (3.81, 0)},
        "LED_OffBoard": {"1": (-3.81, 0), "2": (3.81, 0)},
        "LM3410XMY_DGN": {
            "1": (-8.89, 5.08), "2": (-8.89, 2.54), "3": (-8.89, 0.00),
            "4": (-8.89, -2.54), "9": (-8.89, -5.08),
            "8": (8.89, 5.08), "7": (8.89, 2.54), "6": (8.89, 0.00), "5": (8.89, -2.54),
        },
        "TL431AIDBZR": {"1": (-7.62, 2.54), "2": (-7.62, 0.00), "3": (-7.62, -2.54)},
        "PMOS_DMG2305UX": {"1": (-7.62, 0.00), "2": (7.62, 2.54), "3": (7.62, -2.54)},
        "BJT_SOT23": {"1": (-7.62, 0.00), "3": (7.62, 2.54), "2": (7.62, -2.54)},
        "BAV70_CC": {"1": (-7.62, 2.54), "2": (-7.62, -2.54), "3": (7.62, 0.00)},
        "BAW56_CA": {"3": (-7.62, 0.00), "1": (7.62, 2.54), "2": (7.62, -2.54)},
        "USB4085_GFA": {
            "A4": (10.16, 20.32), "A9": (10.16, 17.78), "B4": (10.16, 15.24), "B9": (10.16, 12.70),
            "A5": (10.16, 10.16), "B5": (10.16, 7.62),
            "A1": (10.16, 5.08), "A12": (10.16, 2.54), "B1": (10.16, 0.00), "B12": (10.16, -2.54),
            "SH1": (10.16, -5.08), "SH2": (10.16, -7.62), "SH3": (10.16, -10.16), "SH4": (10.16, -12.70),
            "A6": (-10.16, 15.24), "A7": (-10.16, 12.70), "A8": (-10.16, 10.16),
            "B6": (-10.16, 7.62), "B7": (-10.16, 5.08), "B8": (-10.16, 2.54),
        },
        "JST_B2B_XH": {"1": (7.62, 1.27), "2": (7.62, -1.27)},
        "JST_B3B_XH": {"1": (7.62, 2.54), "2": (7.62, 0.00), "3": (7.62, -2.54)},
        "SW_100SP3T": {"1": (-7.62, 3.81), "2": (-7.62, 1.27), "3": (-7.62, -1.27), "4": (-7.62, -3.81)},
        "Mech_1Pin": {"1": (-6.35, 0.00)},
        "Pad_1Pin": {"1": (-5.08, 0.00)},
    }

    specs = {
        "J1": ("USB4085_GFA", "lepiled:GCT_USB4085_GF_A", 45.72, 60.96, 0, {
            "A4": "VBUS", "A9": "VBUS", "B4": "VBUS", "B9": "VBUS",
            "A5": "CC1", "B5": "CC2",
            "A1": "GND", "A12": "GND", "B1": "GND", "B12": "GND",
            "SH1": "GND", "SH2": "GND", "SH3": "GND", "SH4": "GND",
            "A6": None, "A7": None, "A8": None, "B6": None, "B7": None, "B8": None,
        }),
        "TP1": ("Pad_1Pin", "lepiled:TestPoint_Pad_D2.5mm", 86.36, 35.56, 0, {"1": "VBUS"}),
        "TP2": ("Pad_1Pin", "lepiled:TestPoint_Pad_D2.5mm", 86.36, 45.72, 0, {"1": "GND"}),
        "R1": ("R_Generic", "lepiled:R_0805", 86.36, 60.96, 0, {"1": "CC1", "2": "GND"}),
        "R2": ("R_Generic", "lepiled:R_0805", 101.60, 60.96, 0, {"1": "CC2", "2": "GND"}),
        "C12": ("C_Generic", "lepiled:C_0603", 116.84, 60.96, 0, {"1": "VBUS", "2": "GND"}),

        "F1": ("F_Polyfuse", "lepiled:Bourns_MF_LSMF_2920", 142.24, 40.64, 90, {"1": "VBUS", "2": "VBUS_FUSED"}),
        "Q1A": ("PMOS_DMG2305UX", "lepiled:Diodes_SOT-23-3_DMG2305UX", 172.72, 40.64, 0, {"3": "VBUS_FUSED", "2": "V_MID", "1": "Q1_GATE"}),
        "Q1B": ("PMOS_DMG2305UX", "lepiled:Diodes_SOT-23-3_DMG2305UX", 205.74, 40.64, 0, {"2": "V_MID", "3": "VIN_PROT", "1": "Q1_GATE"}),
        "D11": ("Diode_K_A", "lepiled:D_SMB_DO-214AA", 236.22, 40.64, 270, {"1": "VIN_PROT", "2": "GND"}),
        "D15": ("Diode_K_A", "lepiled:D_SOD-123", 187.96, 58.42, 270, {"1": "V_MID", "2": "Q1_GATE"}),
        "R10": ("R_Generic", "lepiled:R_0603", 142.24, 66.04, 0, {"1": "V_MID", "2": "Q1_GATE"}),
        "R11": ("R_Generic", "lepiled:R_0603", 160.02, 66.04, 0, {"1": "Q3_EMIT", "2": "GND"}),
        "R12": ("R_Generic", "lepiled:R_0603", 142.24, 86.36, 0, {"1": "V_MID", "2": "OVP_SENSE"}),
        "R13": ("R_Generic", "lepiled:R_0603", 160.02, 86.36, 0, {"1": "OVP_SENSE", "2": "GND"}),
        "R14": ("R_Generic", "lepiled:R_0603", 177.80, 86.36, 0, {"1": "V_MID", "2": "Q3_BASE"}),
        "C11": ("C_Generic", "lepiled:C_0603", 195.58, 86.36, 0, {"1": "Q3_BASE", "2": "GND"}),
        "R15": ("R_Generic", "lepiled:R_0603", 213.36, 86.36, 0, {"1": "V_MID", "2": "Q2_BASE"}),
        "R16": ("R_Generic", "lepiled:R_0603", 231.14, 86.36, 0, {"1": "Q2_BASE", "2": "OVP_K"}),
        "U3": ("TL431AIDBZR", "lepiled:TI_SOT-23-3_DBZ", 147.32, 111.76, 0, {"1": "OVP_K", "2": "OVP_SENSE", "3": "GND"}),
        "Q2": ("BJT_SOT23", "lepiled:onsemi_SOT-23-3_Case318", 175.26, 111.76, 0, {"1": "Q2_BASE", "2": "V_MID", "3": "OVP_DRV"}),
        "D16": ("BAW56_CA", "lepiled:onsemi_SOT-23-3_Case318", 205.74, 111.76, 0, {"3": "OVP_DRV", "1": "OVP_DRV_GATE", "2": "OVP_HYS"}),
        "R18": ("R_Generic", "lepiled:R_0603", 236.22, 111.76, 0, {"1": "OVP_DRV_GATE", "2": "Q1_GATE"}),
        "R19": ("R_Generic", "lepiled:R_0603", 254.00, 111.76, 0, {"1": "OVP_HYS", "2": "OVP_SENSE"}),
        "R17": ("R_Generic", "lepiled:R_0603", 142.24, 134.62, 0, {"1": "OVP_DRV", "2": "Q4_BASE"}),
        "R20": ("R_Generic", "lepiled:R_0603", 160.02, 134.62, 0, {"1": "Q4_BASE", "2": "GND"}),
        "Q4": ("BJT_SOT23", "lepiled:onsemi_SOT-23-3_Case318", 187.96, 134.62, 0, {"1": "Q4_BASE", "2": "GND", "3": "Q3_BASE"}),
        "Q3": ("BJT_SOT23", "lepiled:onsemi_SOT-23-3_Case318", 220.98, 134.62, 0, {"1": "Q3_BASE", "2": "Q3_EMIT", "3": "Q1_GATE"}),

        "C1": ("C_Generic", "lepiled:C_1206", 40.64, 116.84, 0, {"1": "VIN_PROT", "2": "GND"}),
        "C2": ("C_Generic", "lepiled:C_1206", 58.42, 116.84, 0, {"1": "VIN_PROT", "2": "GND"}),
        "C3": ("C_Generic", "lepiled:C_1206", 76.20, 116.84, 0, {"1": "VIN_PROT", "2": "GND"}),
        "C7": ("C_Generic", "lepiled:C_0603", 93.98, 116.84, 0, {"1": "VIN_PROT", "2": "GND"}),
        "C8": ("C_Generic", "lepiled:C_0603", 111.76, 116.84, 0, {"1": "VIN_PROT", "2": "GND"}),
        "H1": ("Pad_1Pin", "lepiled:MountingHole_2.7mm_M2.5_Pad5.5mm", 45.72, 142.24, 0, {"1": "GND"}),
        "H2": ("Pad_1Pin", "lepiled:MountingHole_2.7mm_M2.5_Pad5.5mm", 66.04, 142.24, 0, {"1": "GND"}),
        "H3": ("Pad_1Pin", "lepiled:MountingHole_2.7mm_M2.5_Pad5.5mm", 86.36, 142.24, 0, {"1": "GND"}),
        "H4": ("Pad_1Pin", "lepiled:MountingHole_2.7mm_M2.5_Pad5.5mm", 106.68, 142.24, 0, {"1": "GND"}),

        "J4": ("JST_B3B_XH", "lepiled:JST_XH_B3B_P2.50mm", 45.72, 177.80, 0, {"1": "SW_UV_EN", "2": "VIN_PROT", "3": "EN2_NET"}),
        "SW1": ("SW_100SP3T", "", 83.82, 177.80, 0, {"1": "SW_UV_EN", "2": "VIN_PROT", "3": "EN2_NET", "4": "SW1_MECH"}),
        "SW1_BOOT": ("Mech_1Pin", "", 116.84, 181.61, 0, {"1": "SW1_MECH"}),
        "D12": ("BAV70_CC", "lepiled:onsemi_SOT-23-3_Case318", 147.32, 177.80, 0, {"1": "SW_UV_EN", "2": "EN2_NET", "3": "EN1_NET"}),
        "R5": ("R_Generic", "lepiled:R_0603", 177.80, 177.80, 0, {"1": "EN1_NET", "2": "GND"}),
        "R6": ("R_Generic", "lepiled:R_0603", 195.58, 177.80, 0, {"1": "EN2_NET", "2": "GND"}),
        "R7": ("R_Generic", "lepiled:R_0603", 213.36, 177.80, 0, {"1": "EN2_NET", "2": "DIM2_NET"}),
        "C6": ("C_Generic", "lepiled:C_0603", 231.14, 177.80, 0, {"1": "DIM2_NET", "2": "GND"}),

        "U1": ("LM3410XMY_DGN", "lepiled:TI_LM3410XMY_DGN0008A", 309.88, 53.34, 0, {
            "1": None, "2": "GND", "3": "VIN_PROT", "4": "EN1_NET", "9": "GND",
            "8": None, "7": "SW1_NODE", "6": "GND", "5": "FB1_NET",
        }),
        "L1": ("L_Generic", "lepiled:Bourns_SRN6045", 342.90, 35.56, 90, {"1": "VIN_PROT", "2": "SW1_NODE"}),
        "D9": ("Diode_K_A", "lepiled:D_SMA_DO-214AC", 365.76, 35.56, 180, {"2": "SW1_NODE", "1": "VOUT1"}),
        "C4": ("C_Generic", "lepiled:C_1210", 386.08, 43.18, 0, {"1": "VOUT1", "2": "GND"}),
        "C9": ("C_Generic", "lepiled:C_0603", 398.78, 43.18, 0, {"1": "VOUT1", "2": "GND"}),
        "D13": ("Diode_K_A", "lepiled:D_SOD-123", 347.98, 60.96, 270, {"1": "VOUT1", "2": "FB1_NET"}),
        "R8": ("R_Generic", "lepiled:R_0603", 365.76, 60.96, 0, {"1": "FB1_NET", "2": "UV_RET"}),
        "R3": ("R_Generic", "lepiled:R_1206", 386.08, 60.96, 0, {"1": "UV_RET", "2": "GND"}),
        "J2": ("JST_B2B_XH", "lepiled:JST_XH_B2B_P2.50mm", 309.88, 86.36, 0, {"1": "VOUT1", "2": "UV_RET"}),
        "D1": ("LED_OffBoard", "", 342.90, 86.36, 0, {"1": "VOUT1", "2": "UV_N1"}),
        "D2": ("LED_OffBoard", "", 358.14, 86.36, 0, {"1": "UV_N1", "2": "UV_N2"}),
        "D3": ("LED_OffBoard", "", 373.38, 86.36, 0, {"1": "UV_N2", "2": "UV_N3"}),
        "D4": ("LED_OffBoard", "", 388.62, 86.36, 0, {"1": "UV_N3", "2": "UV_RET"}),

        "U2": ("LM3410XMY_DGN", "lepiled:TI_LM3410XMY_DGN0008A", 309.88, 134.62, 0, {
            "1": None, "2": "GND", "3": "VIN_PROT", "4": "DIM2_NET", "9": "GND",
            "8": None, "7": "SW2_NODE", "6": "GND", "5": "FB2_NET",
        }),
        "L2": ("L_Generic", "lepiled:Bourns_SRN6045", 342.90, 116.84, 90, {"1": "VIN_PROT", "2": "SW2_NODE"}),
        "D10": ("Diode_K_A", "lepiled:D_SMA_DO-214AC", 365.76, 116.84, 180, {"2": "SW2_NODE", "1": "VOUT2"}),
        "C5": ("C_Generic", "lepiled:C_1210", 386.08, 124.46, 0, {"1": "VOUT2", "2": "GND"}),
        "C10": ("C_Generic", "lepiled:C_0603", 398.78, 124.46, 0, {"1": "VOUT2", "2": "GND"}),
        "D14": ("Diode_K_A", "lepiled:D_SOD-123", 347.98, 142.24, 270, {"1": "VOUT2", "2": "FB2_NET"}),
        "R9": ("R_Generic", "lepiled:R_0603", 365.76, 142.24, 0, {"1": "FB2_NET", "2": "VIS_RET"}),
        "R4": ("R_Generic", "lepiled:R_1206", 386.08, 142.24, 0, {"1": "VIS_RET", "2": "GND"}),
        "J3": ("JST_B2B_XH", "lepiled:JST_XH_B2B_P2.50mm", 309.88, 167.64, 0, {"1": "VOUT2", "2": "VIS_RET"}),
        "D5": ("LED_OffBoard", "", 342.90, 167.64, 0, {"1": "VOUT2", "2": "VIS_N1"}),
        "D6": ("LED_OffBoard", "", 358.14, 167.64, 0, {"1": "VIS_N1", "2": "VIS_N2"}),
        "D7": ("LED_OffBoard", "", 373.38, 167.64, 0, {"1": "VIS_N2", "2": "VIS_N3"}),
        "D8": ("LED_OffBoard", "", 388.62, 167.64, 0, {"1": "VIS_N3", "2": "VIS_RET"}),
    }

    assert set(specs.keys()) == set(comp_rows.keys())

    sym_blocks, label_blocks, nc_blocks = [], [], []
    for ref, (sym_name, fp_name, sx, sy, ang, pin_map) in specs.items():
        row = comp_rows[ref]
        is_off = (row["Mounting"] == "Off-Board")
        on_board = "no" if is_off else "yes"
        dnp = "yes" if is_off else "no"
        val = row["Value_Rating"].split(";")[0].strip()
        pin_lines = "\n".join(f'    (pin "{pnum}" (uuid "{uid(f"pin_{ref}_{pnum}")}"))' for pnum in pin_map)
        sym_blocks.append(f"""  (symbol
    (lib_id "lepiled:{sym_name}")
    (at {sx:.2f} {sy:.2f} {ang})
    (unit 1)
    (exclude_from_sim no)
    (in_bom yes)
    (on_board {on_board})
    (dnp {dnp})
    (uuid "{uid(f'sym_{ref}')}")
    (property "Reference" "{ref}" (at {sx:.2f} {sy - 5.08:.2f} 0) (effects (font (size 1.1 1.1))))
    (property "Value" "{val}" (at {sx:.2f} {sy + 5.08:.2f} 0) (effects (font (size 0.9 0.9))))
    (property "Footprint" "{fp_name}" (at {sx:.2f} {sy:.2f} 0) (effects (font (size 1.0 1.0)) (hide yes)))
    (property "Datasheet" "{row['Datasheet_Ref']}" (at {sx:.2f} {sy:.2f} 0) (effects (font (size 1.0 1.0)) (hide yes)))
    (property "MPN" "{row['MPN']}" (at {sx:.2f} {sy:.2f} 0) (effects (font (size 1.0 1.0)) (hide yes)))
{pin_lines}
    (instances
      (project "driver_pcb"
        (path "/{root_uuid}"
          (reference "{ref}")
          (unit 1)
        )
      )
    )
  )""")

        for pnum, net in pin_map.items():
            dx, dy = _rot_pt(*sym_pins[sym_name][pnum], ang)
            px, py = round(sx + dx, 2), round(sy + dy, 2)
            if net is None:
                nc_blocks.append(f'  (no_connect (at {px:.2f} {py:.2f}) (uuid "{uid(f"nc_{ref}_{pnum}")}"))')
            else:
                lbl_ang = (0 if dx > 0 else 180) if abs(dx) >= abs(dy) else (270 if dy > 0 else 90)
                label_blocks.append(
                    f'  (global_label "{net}" (shape bidirectional) (at {px:.2f} {py:.2f} {lbl_ang}) '
                    f'(fields_autoplaced yes) (effects (font (size 1.0 1.0)) (justify left)) '
                    f'(uuid "{uid(f"glbl_{ref}_{pnum}_{net}")}"))'
                )

    lib_sym_txt = "\n".join(s.replace('(symbol "', '(symbol "lepiled:', 1) for s in syms)
    sch = f"""(kicad_sch
  (version 20250114)
  (generator "eeschema")
  (generator_version "9.0")
  (uuid "{root_uuid}")
  (paper "A3")
  (title_block
    (title "LepiLED DIY Maxi Switch - Driver & Protection PCB (71 RefDes, 36 Nets)")
    (date "2026-11-18")
    (rev "1.0")
    (comment 1 "36.0 x 46.0 mm 2-Layer FR4 (1 oz Cu) | Dual LM3410XMY 339mA Boost + OVP/RPP/Soft-Start")
    (comment 2 "1:1 parity with circuit_design/COMPONENT_IDS.csv (61 On-PCB + 10 Off-Board DNP)")
  )
  (lib_symbols
{lib_sym_txt}
  )
{chr(10).join(sym_blocks)}
{chr(10).join(label_blocks)}
{chr(10).join(nc_blocks)}
  (sheet_instances
    (path "/" (page "1"))
  )
)
"""
    (BASE_DIR / "driver_pcb.kicad_sch").write_text(sch)
    return specs


# ---------------------------------------------------------------------------
# 4. Grid-Verified 2-Layer Router & PCB Builder
# ---------------------------------------------------------------------------

class GridRouter:
    """0.125 mm grid 2-layer A* router preventing any short, crossing, or clearance violation."""
    RES = 0.125  # mm per cell
    XMIN, XMAX = -17.5, +17.5
    YMIN, YMAX = -22.5, +22.5

    def __init__(self, board: pcbnew.BOARD, keepout_boxes_b):
        self.board = board
        self.nx = int(round((self.XMAX - self.XMIN) / self.RES)) + 1
        self.ny = int(round((self.YMAX - self.YMIN) / self.RES)) + 1
        # Stored obstacles: list of (layer_mask, x0, y0, x1, y1, netname)
        # layer_mask: 1=F.Cu, 2=B.Cu, 3=Both
        self.obstacles = []
        # Round-rect board corners keepout
        for sx in (-1, 1):
            for sy in (-1, 1):
                cx, cy = sx * 16.0, sy * 21.0
                for ix in range(self.nx):
                    x = self.XMIN + ix * self.RES
                    if (sx > 0 and x > cx) or (sx < 0 and x < cx):
                        for iy in range(self.ny):
                            y = self.YMIN + iy * self.RES
                            if (sy > 0 and y > cy) or (sy < 0 and y < cy):
                                if math.hypot(x - cx, y - cy) > 1.60:
                                    self.obstacles.append((3, x - 0.07, y - 0.07, x + 0.07, y + 0.07, "__EDGE__"))
        for (x0, y0, x1, y1) in keepout_boxes_b:
            self.obstacles.append((2, x0, y0, x1, y1, "__KO_B__"))
        self._register_board_items()

    def _to_ij(self, xm, ym):
        ix = max(0, min(self.nx - 1, int(round((xm - self.XMIN) / self.RES))))
        iy = max(0, min(self.ny - 1, int(round((ym - self.YMIN) / self.RES))))
        return ix, iy

    def _to_xy(self, ix, iy):
        return round(self.XMIN + ix * self.RES, 4), round(self.YMIN + iy * self.RES, 4)

    def _register_board_items(self):
        for fp in self.board.GetFootprints():
            for pad in fp.Pads():
                bb = pad.GetBoundingBox()
                x0 = bb.GetLeft() / 1e6 - CX
                x1 = bb.GetRight() / 1e6 - CX
                y1 = CY - bb.GetTop() / 1e6
                y0 = CY - bb.GetBottom() / 1e6
                nn = pad.GetNetname() or "__NC__"
                lmask = 3 if pad.GetAttribute() in (pcbnew.PAD_ATTRIB_PTH, pcbnew.PAD_ATTRIB_NPTH) else 1
                self.obstacles.append((lmask, x0, y0, x1, y1, nn))
        for trk in self.board.GetTracks():
            if isinstance(trk, pcbnew.PCB_VIA):
                vx, vy = trk.GetPosition().x / 1e6 - CX, CY - trk.GetPosition().y / 1e6
                r = trk.GetWidth(pcbnew.F_Cu) / 2e6
                self.obstacles.append((3, vx - r, vy - r, vx + r, vy + r, trk.GetNetname()))
            else:
                p0, p1 = trk.GetStart(), trk.GetEnd()
                x0, y0 = p0.x / 1e6 - CX, CY - p0.y / 1e6
                x1, y1 = p1.x / 1e6 - CX, CY - p1.y / 1e6
                hw = trk.GetWidth() / 2e6
                lm = 1 if trk.GetLayer() == pcbnew.F_Cu else 2
                self.obstacles.append((lm, min(x0, x1) - hw, min(y0, y1) - hw, max(x0, x1) + hw, max(y0, y1) + hw, trk.GetNetname()))

    def add_seg_obstacle(self, x0, y0, x1, y1, w, lyr, netname):
        hw = w / 2.0
        lm = 1 if lyr == pcbnew.F_Cu else 2
        self.obstacles.append((lm, min(x0, x1) - hw, min(y0, y1) - hw, max(x0, x1) + hw, max(y0, y1) + hw, netname))

    def add_via_obstacle(self, x, y, diam, netname):
        r = diam / 2.0
        self.obstacles.append((3, x - r, y - r, x + r, y + r, netname))

    def _build_blocked(self, netname, half_w, clr, allow_via_margin=0.45):
        # Returns blocked[layer_idx][ix][iy] where layer_idx 0=F.Cu, 1=B.Cu
        pad_m = half_w + clr + 0.08
        b0 = [bytearray(self.ny) for _ in range(self.nx)]
        b1 = [bytearray(self.ny) for _ in range(self.nx)]
        via_blk = [bytearray(self.ny) for _ in range(self.nx)]
        vm = 0.30 + clr + 0.08
        # Enforce copper_edge_clearance (0.30 mm) + half_w around board perimeter
        edge_x = 18.0 - 0.34 - half_w
        edge_y = 23.0 - 0.34 - half_w
        via_edge_x = 18.0 - 0.34 - 0.30
        via_edge_y = 23.0 - 0.34 - 0.30
        for ix in range(self.nx):
            x = self.XMIN + ix * self.RES
            for iy in range(self.ny):
                y = self.YMIN + iy * self.RES
                if abs(x) > edge_x or abs(y) > edge_y:
                    b0[ix][iy] = 1
                    b1[ix][iy] = 1
                if abs(x) > via_edge_x or abs(y) > via_edge_y:
                    via_blk[ix][iy] = 1

        # Block ALL existing vias & PTH holes in via_blk regardless of net (prevents hole_to_hole / co-located)
        hole_m = 0.30 + 0.30 + 0.32
        for fp in self.board.GetFootprints():
            for pad in fp.Pads():
                if pad.GetAttribute() in (pcbnew.PAD_ATTRIB_PTH, pcbnew.PAD_ATTRIB_NPTH):
                    px = pad.GetPosition().x / 1e6 - CX
                    py = CY - pad.GetPosition().y / 1e6
                    pr = max(pad.GetDrillSize().x, pad.GetDrillSize().y) / 2e6
                    hm = 0.15 + pr + 0.30
                    vx0 = max(0, int(math.floor((px - hm - self.XMIN) / self.RES)))
                    vx1 = min(self.nx - 1, int(math.ceil((px + hm - self.XMIN) / self.RES)))
                    vy0 = max(0, int(math.floor((py - hm - self.YMIN) / self.RES)))
                    vy1 = min(self.ny - 1, int(math.ceil((py + hm - self.YMIN) / self.RES)))
                    for ix in range(vx0, vx1 + 1):
                        vrow = via_blk[ix]
                        for iy in range(vy0, vy1 + 1):
                            vrow[iy] = 1
        for trk in self.board.GetTracks():
            if isinstance(trk, pcbnew.PCB_VIA):
                vx = trk.GetPosition().x / 1e6 - CX
                vy = CY - trk.GetPosition().y / 1e6
                vx0 = max(0, int(math.floor((vx - hole_m - self.XMIN) / self.RES)))
                vx1 = min(self.nx - 1, int(math.ceil((vx + hole_m - self.XMIN) / self.RES)))
                vy0 = max(0, int(math.floor((vy - hole_m - self.YMIN) / self.RES)))
                vy1 = min(self.ny - 1, int(math.ceil((vy + hole_m - self.YMIN) / self.RES)))
                for ix in range(vx0, vx1 + 1):
                    vrow = via_blk[ix]
                    for iy in range(vy0, vy1 + 1):
                        vrow[iy] = 1

        for lm, x0, y0, x1, y1, nn in self.obstacles:
            if nn == "__EDGE__" or nn == "__KO_B__":
                pass
            elif nn == netname:
                continue
            ix0 = max(0, int(math.floor((x0 - pad_m - self.XMIN) / self.RES)))
            ix1 = min(self.nx - 1, int(math.ceil((x1 + pad_m - self.XMIN) / self.RES)))
            iy0 = max(0, int(math.floor((y0 - pad_m - self.YMIN) / self.RES)))
            iy1 = min(self.ny - 1, int(math.ceil((y1 + pad_m - self.YMIN) / self.RES)))
            if lm & 1:
                for ix in range(ix0, ix1 + 1):
                    row = b0[ix]
                    for iy in range(iy0, iy1 + 1):
                        row[iy] = 1
            if lm & 2:
                for ix in range(ix0, ix1 + 1):
                    row = b1[ix]
                    for iy in range(iy0, iy1 + 1):
                        row[iy] = 1
            vx0 = max(0, int(math.floor((x0 - vm - self.XMIN) / self.RES)))
            vx1 = min(self.nx - 1, int(math.ceil((x1 + vm - self.XMIN) / self.RES)))
            vy0 = max(0, int(math.floor((y0 - vm - self.YMIN) / self.RES)))
            vy1 = min(self.ny - 1, int(math.ceil((y1 + vm - self.YMIN) / self.RES)))
            for ix in range(vx0, vx1 + 1):
                vrow = via_blk[ix]
                for iy in range(vy0, vy1 + 1):
                    vrow[iy] = 1
        return (b0, b1), via_blk

    def route(self, start_xy, start_lyr_idx, goal_xy, goal_lyr_idx, net_obj, width_mm, clr_mm, allow_b=True):
        netname = net_obj.GetNetname()
        sx, sy = self._to_ij(*start_xy)
        gx, gy = self._to_ij(*goal_xy)
        blocked, via_blk = self._build_blocked(netname, width_mm / 2.0, clr_mm)
        # Only ensure exact start and goal cells are open
        blocked[start_lyr_idx][sx][sy] = 0
        blocked[goal_lyr_idx][gx][gy] = 0

        start = (start_lyr_idx, sx, sy)
        goal = (goal_lyr_idx, gx, gy)
        pq = [(abs(sx - gx) + abs(sy - gy), 0, start, -1)]
        dist = {start: 0}
        parent = {}

        dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        while pq:
            _, g, state, prev_dir = heapq.heappop(pq)
            if state == goal:
                break
            if g > dist.get(state, 10**9):
                continue
            l, x, y = state
            for d_idx, (dx, dy) in enumerate(dirs):
                nx_, ny_ = x + dx, y + dy
                if 0 <= nx_ < self.nx and 0 <= ny_ < self.ny and not blocked[l][nx_][ny_]:
                    # Slight preference for B.Cu only when needed, small turn penalty
                    turn_cost = 1 if (prev_dir != -1 and prev_dir != d_idx) else 0
                    ng = g + 1 + turn_cost + (1 if l == 1 else 0)
                    ns = (l, nx_, ny_)
                    if ng < dist.get(ns, 10**9):
                        dist[ns] = ng
                        parent[ns] = state
                        heapq.heappush(pq, (ng + abs(nx_ - gx) + abs(ny_ - gy), ng, ns, d_idx))
            if allow_b and not via_blk[x][y]:
                nl = 1 - l
                if not blocked[nl][x][y]:
                    ng = g + 18
                    ns = (nl, x, y)
                    if ng < dist.get(ns, 10**9):
                        dist[ns] = ng
                        parent[ns] = state
                        heapq.heappush(pq, (ng + abs(x - gx) + abs(y - gy), ng, ns, -1))

        if goal not in parent and goal != start:
            raise RuntimeError(f"Router failed for net {netname}: {start_xy} (L{start_lyr_idx}) -> {goal_xy} (L{goal_lyr_idx})")

        path = [goal]
        cur = goal
        while cur != start:
            cur = parent[cur]
            path.append(cur)
        path.reverse()

        # Convert path to exact KiCad segments & vias, snapping endpoints to exact start_xy/goal_xy
        pts_coords = [self._to_xy(ix, iy) for (_, ix, iy) in path]
        pts_coords[0] = start_xy
        pts_coords[-1] = goal_xy

        # Group consecutive points on same layer into collinear segments
        i = 0
        while i < len(path) - 1:
            l0 = path[i][0]
            l1 = path[i + 1][0]
            if l0 != l1:
                vx, vy = pts_coords[i]
                add_via(self.board, vx, vy, net_obj, 0.60, 0.30)
                self.add_via_obstacle(vx, vy, 0.60, netname)
                i += 1
                continue
            # Extend straight run on same layer
            j = i + 1
            dx0 = round(pts_coords[j][0] - pts_coords[i][0], 4)
            dy0 = round(pts_coords[j][1] - pts_coords[i][1], 4)
            while j + 1 < len(path) and path[j + 1][0] == l0:
                dx1 = round(pts_coords[j + 1][0] - pts_coords[j][0], 4)
                dy1 = round(pts_coords[j + 1][1] - pts_coords[j][1], 4)
                if (dx0 == 0 and dx1 == 0) or (dy0 == 0 and dy1 == 0):
                    j += 1
                else:
                    break
            p_start = pts_coords[i]
            p_end = pts_coords[j]
            lyr = pcbnew.F_Cu if l0 == 0 else pcbnew.B_Cu
            add_track(self.board, [p_start, p_end], width_mm, net_obj, lyr)
            self.add_seg_obstacle(p_start[0], p_start[1], p_end[0], p_end[1], width_mm, lyr, netname)
            i = j


def add_rounded_rect_edge_cuts(board: pcbnew.BOARD, w: float, h: float, r: float):
    hw, hh = w / 2.0, h / 2.0
    for (x0, y0), (x1, y1) in [
        ((-hw + r, +hh), (+hw - r, +hh)),
        ((+hw, +hh - r), (+hw, -hh + r)),
        ((+hw - r, -hh), (-hw + r, -hh)),
        ((-hw, -hh + r), (-hw, +hh - r)),
    ]:
        s = pcbnew.PCB_SHAPE(board)
        s.SetShape(pcbnew.SHAPE_T_SEGMENT)
        s.SetLayer(pcbnew.Edge_Cuts)
        s.SetWidth(mm(0.10))
        s.SetStart(kpt(x0, y0))
        s.SetEnd(kpt(x1, y1))
        board.Add(s)
    s2 = r / math.sqrt(2.0)
    for st, mid, en in [
        ((+hw - r, +hh), (+hw - r + s2, +hh - r + s2), (+hw, +hh - r)),
        ((+hw, -hh + r), (+hw - r + s2, -hh + r - s2), (+hw - r, -hh)),
        ((-hw + r, -hh), (-hw + r - s2, -hh + r - s2), (-hw, -hh + r)),
        ((-hw, +hh - r), (-hw + r - s2, +hh - r + s2), (-hw + r, +hh)),
    ]:
        a = pcbnew.PCB_SHAPE(board)
        a.SetShape(pcbnew.SHAPE_T_ARC)
        a.SetLayer(pcbnew.Edge_Cuts)
        a.SetWidth(mm(0.10))
        a.SetArcGeometry(kpt(*st), kpt(*mid), kpt(*en))
        board.Add(a)


def add_track(board, pts_xy, width_mm, net, layer=pcbnew.F_Cu):
    for (x0, y0), (x1, y1) in zip(pts_xy, pts_xy[1:]):
        if abs(x0 - x1) < 1e-5 and abs(y0 - y1) < 1e-5:
            continue
        t = pcbnew.PCB_TRACK(board)
        t.SetLayer(layer)
        t.SetWidth(mm(width_mm))
        t.SetStart(kpt(x0, y0))
        t.SetEnd(kpt(x1, y1))
        t.SetNet(net)
        board.Add(t)


def add_via(board, xm, ym, net, diam_mm=0.60, drill_mm=0.30):
    v = pcbnew.PCB_VIA(board)
    v.SetPosition(kpt(xm, ym))
    v.SetWidth(mm(diam_mm))
    v.SetDrill(mm(drill_mm))
    v.SetViaType(pcbnew.VIATYPE_THROUGH)
    v.SetNet(net)
    board.Add(v)
    return v


def add_zone(board, pts_xy, layer, net, priority=0, min_thickness=0.20, clearance=0.20,
             thermal_gap=0.25, thermal_bridge=0.35, solid_pads=False):
    z = pcbnew.ZONE(board)
    z.SetLayer(layer)
    z.SetNet(net)
    z.SetAssignedPriority(priority)
    z.SetMinThickness(mm(min_thickness))
    z.SetLocalClearance(mm(clearance))
    z.SetThermalReliefGap(mm(thermal_gap))
    z.SetThermalReliefSpokeWidth(mm(thermal_bridge))
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL if solid_pads else pcbnew.ZONE_CONNECTION_THERMAL)
    ol = z.Outline()
    ol.NewOutline()
    for x, y in pts_xy:
        ol.Append(kpt(x, y))
    board.Add(z)
    return z


def add_rule_keepout(board, pts_xy, layer=pcbnew.B_Cu):
    z = pcbnew.ZONE(board)
    z.SetLayer(layer)
    z.SetIsRuleArea(True)
    z.SetDoNotAllowCopperPour(True)
    z.SetDoNotAllowTracks(True)
    z.SetDoNotAllowVias(True)
    z.SetDoNotAllowPads(True)
    ol = z.Outline()
    ol.NewOutline()
    for x, y in pts_xy:
        ol.Append(kpt(x, y))
    board.Add(z)
    return z


def get_pad_pos(fp, pad_num):
    for p in fp.Pads():
        if p.GetNumber() == str(pad_num):
            pos = p.GetPosition()
            return (pos.x / 1e6 - CX, CY - pos.y / 1e6)
    raise KeyError(f"Pad {pad_num} not found in {fp.GetReference()}")


def build_board(specs, comp_rows):
    pcb_path = BASE_DIR / "driver_pcb.kicad_pcb"
    board = pcbnew.NewBoard(str(pcb_path))
    board.SetCopperLayerCount(2)

    ds = board.GetDesignSettings()
    ds.m_TrackMinWidth = mm(0.25)
    ds.m_MinClearance = mm(0.18)
    ds.m_CopperEdgeClearance = mm(0.30)
    ds.m_HoleClearance = mm(0.25)
    ds.m_SilkClearance = mm(0.10)
    ds.m_ViasMinSize = mm(0.55)
    ds.m_ViasMinAnnularWidth = mm(0.12)
    ds.m_MinThroughDrill = mm(0.28)
    ds.m_SolderMaskMargin = mm(0.05)
    ds.SetAuxOrigin(kpt(0.0, 0.0))

    add_rounded_rect_edge_cuts(board, 36.0, 46.0, 2.0)

    on_pcb_nets = {
        "CC1", "CC2", "DIM2_NET", "EN1_NET", "EN2_NET", "FB1_NET", "FB2_NET", "GND",
        "OVP_DRV", "OVP_DRV_GATE", "OVP_HYS", "OVP_K", "OVP_SENSE",
        "Q1_GATE", "Q2_BASE", "Q3_BASE", "Q3_EMIT", "Q4_BASE",
        "SW1_NODE", "SW2_NODE", "SW_UV_EN", "UV_RET", "VBUS", "VBUS_FUSED",
        "VIN_PROT", "VIS_RET", "VOUT1", "VOUT2", "V_MID",
    }
    nets = {}
    for nn in sorted(on_pcb_nets):
        ni = pcbnew.NETINFO_ITEM(board, nn)
        board.Add(ni)
        nets[nn] = ni

    # Verified zero-courtyard-overlap placement (all 61 On-PCB RefDes)
    placement = {
        "H1": (-14.0, +19.0, 0),
        "H2": (+14.0, +19.0, 0),
        "H3": (-14.0, -19.0, 0),
        "H4": (+14.0, -19.0, 0),

        # Input USB-C, Test Pads, CC1/CC2, ESD
        "J1": (0.0, -18.50, 0),
        "TP1": (-8.2, -19.5, 0),
        "TP2": (+8.2, -19.5, 0),
        "C12": (-5.4, -13.2, 0),
        "R1": (-1.6, -13.2, 180),
        "R2": (+1.6, -13.2, 180),

        # Input Protection (F1, Q1A, Q1B, D15, D11, C1)
        "F1": (-12.8, -13.2, 180),
        "Q1A": (-14.2, -7.8, 90),
        "Q1B": (-10.2, -5.8, 270),
        "D15": (-14.6, -4.6, 180),
        "D11": (-14.6, -1.6, 180),
        "C1": (-9.2, -2.0, 0),

        # OVP / Soft-Start Cluster (3 clean non-overlapping columns on Lower-Right)
        "R12": (+6.4, -15.2, 0),
        "R13": (+6.4, -13.2, 180),
        "C11": (+6.4, -11.2, 180),
        "R14": (+6.4, -9.2, 0),
        "Q3": (+6.4, -6.2, 0),
        "R11": (+6.4, -3.2, 180),

        "R19": (+10.6, -15.2, 0),
        "U3": (+10.6, -12.2, 0),
        "R18": (+10.6, -9.4, 0),
        "R10": (+10.6, -7.4, 0),
        "Q4": (+10.6, -4.4, 0),

        "R16": (+15.0, -15.0, 180),
        "R15": (+15.0, -13.0, 0),
        "Q2": (+15.0, -10.2, 0),
        "D16": (+15.0, -6.4, 0),
        "R17": (+15.0, -3.4, 0),
        "R20": (+15.0, -1.4, 0),

        # Maxi-Switch & Headers (Center)
        "J4": (-1.4, -2.5, 0),
        "D12": (+1.4, -7.8, 0),
        "R5": (-3.4, -7.2, 0),
        "R6": (-3.4, -9.2, 0),
        "R7": (+1.2, -10.8, 0),
        "C6": (+3.6, -10.8, 270),

        # Channel 1: UV Boost (Left)
        "U1": (-10.0, +5.4, 90),
        "C7": (-10.0, +1.45, 180),
        "C2": (-13.6, +5.4, 90),
        "L1": (-13.8, +11.8, 0),
        "D9": (-7.6, +10.3, 180),
        "C9": (-7.0, +6.5, 270),
        "C4": (-4.8, +13.7, 0),
        "R8": (-4.8, +5.2, 90),
        "R3": (-2.4, +5.2, 270),
        "D13": (-2.0, +9.6, 270),
        "J2": (-5.2, +19.2, 180),

        # Channel 2: Vis Boost (Right)
        "U2": (+9.0, +5.4, 90),
        "C8": (+9.0, +1.45, 180),
        "C3": (+5.4, +5.4, 90),
        "L2": (+5.2, +11.8, 0),
        "D10": (+11.4, +10.3, 180),
        "C10": (+12.0, +6.5, 270),
        "C5": (+13.8, +13.7, 0),
        "R9": (+14.2, +5.2, 90),
        "R4": (+16.4, +5.2, 270),
        "D14": (+16.4, +9.6, 270),
        "J3": (+5.2, +19.2, 180),
    }
    assert len(placement) == 61

    io = pcbnew.PCB_IO_KICAD_SEXPR()
    root_uuid = uid("root_sheet")
    fps = {}

    for ref, (xm, ym, rot) in placement.items():
        sym_name, fp_full, _, _, _, pin_map = specs[ref]
        fp_name = fp_full.split(":", 1)[1]
        fp = io.FootprintLoad(str(FP_LIB_DIR), fp_name)
        fp.SetFPID(pcbnew.LIB_ID("lepiled", fp_name))
        fp.SetReference(ref)
        fp.SetValue(comp_rows[ref]["Value_Rating"].split(";")[0].strip())
        fp.SetPosition(kpt(xm, ym))
        fp.SetOrientationDegrees(rot)
        fp.SetPath(pcbnew.KIID_PATH(f"/{root_uuid}/{uid(f'sym_{ref}')}"))
        for pad in fp.Pads():
            pnum = pad.GetNumber()
            netname = pin_map.get(pnum)
            if netname is not None:
                pad.SetNet(nets[netname])
        board.Add(fp)
        fps[ref] = fp

    # Assign NC pins matching KiCad schematic net names
    nc_pin_names = {
        ("U1", "1"): "NC1", ("U1", "8"): "NC2",
        ("U2", "1"): "NC1", ("U2", "8"): "NC2",
        ("J1", "A6"): "Dp1", ("J1", "A7"): "Dn1", ("J1", "A8"): "SBU1",
        ("J1", "B6"): "Dp2", ("J1", "B7"): "Dn2", ("J1", "B8"): "SBU2",
    }
    for (ref, pnum), pname in nc_pin_names.items():
        nn = f"unconnected-({ref}-{pname}-Pad{pnum})"
        ni = pcbnew.NETINFO_ITEM(board, nn)
        board.Add(ni)
        for pad in fps[ref].Pads():
            if pad.GetNumber() == pnum:
                pad.SetNet(ni)

    # RefDes positions are already cleanly centered/placed in create_footprints()

    def pt(ref, pnum):
        return get_pad_pos(fps[ref], pnum)

    # -----------------------------------------------------------------------
    # Thermal Vias strictly INSIDE U1 & U2 DAP (6x 0.30/0.60 mm each -> B.Cu GND plane)
    # -----------------------------------------------------------------------
    for u_ref in ("U1", "U2"):
        ux, uy = placement[u_ref][:2]
        for dx, dy in [(-0.65, +0.50), (0.0, +0.50), (+0.65, +0.50), (-0.65, -0.50), (0.0, -0.50), (+0.65, -0.50)]:
            add_via(board, ux + dx, uy + dy, nets["GND"], 0.60, 0.30)

    # -----------------------------------------------------------------------
    # Copper Pours & B.Cu Keepouts (SW1_NODE, SW2_NODE)
    # -----------------------------------------------------------------------
    z_vout1 = add_zone(
        board,
        [(-17.5, +14.9), (-11.2, +14.9), (-8.2, +12.2), (-6.8, +8.4), (-0.5, +8.4), (-0.5, +22.5), (-17.5, +22.5)],
        pcbnew.F_Cu, nets["VOUT1"], priority=3, min_thickness=0.25, clearance=0.25, solid_pads=True
    )
    z_vout2 = add_zone(
        board,
        [(+0.5, +14.9), (+7.8, +14.9), (+11.0, +12.2), (+12.2, +8.4), (+17.5, +8.4), (+17.5, +22.5), (+0.5, +22.5)],
        pcbnew.F_Cu, nets["VOUT2"], priority=3, min_thickness=0.25, clearance=0.25, solid_pads=True
    )
    # Q1A/Q1B Drain/Source pours (F.Cu high-current continuous copper)
    add_zone(board, [(-17.0, -14.8), (-13.6, -14.8), (-13.6, -7.0), (-17.0, -7.0)],
             pcbnew.F_Cu, nets["VBUS_FUSED"], priority=2, min_thickness=0.25, clearance=0.20, solid_pads=True)
    add_zone(board, [(-13.8, -7.6), (-10.6, -7.6), (-10.6, -5.6), (-13.8, -5.6)],
             pcbnew.F_Cu, nets["V_MID"], priority=2, min_thickness=0.25, clearance=0.20, solid_pads=True)

    # Named Sense_Tap_Area (non-restrictive rule area) scoping low-current OVP/SS sense branches
    # Keep Q1A.2->Q1B.2 1.50mm V_MID trunk (x<=-10.45) and Q1B.3 VIN_PROT (x<=-8.45, y>=-6.55) strictly OUTSIDE!
    for sbox in [
        [(+4.5, -17.5), (+17.6, -17.5), (+17.6, -5.0), (+4.5, -5.0)],
        [(-16.0, -5.8), (-12.0, -5.8), (-12.0, -3.6), (-16.0, -3.6)],
        [(-8.7, -7.6), (+4.6, -7.6), (+4.6, -5.2), (-8.3, -5.2), (-8.3, -6.9), (-8.7, -6.9)],
    ]:
        sz = pcbnew.ZONE(board)
        sz.SetLayerSet(lset(pcbnew.F_Cu, pcbnew.B_Cu))
        sz.SetIsRuleArea(True)
        sz.SetZoneName("Sense_Tap_Area")
        sz.SetDoNotAllowCopperPour(False)
        sz.SetDoNotAllowTracks(False)
        sz.SetDoNotAllowVias(False)
        sz.SetDoNotAllowPads(False)
        ol = sz.Outline()
        ol.NewOutline()
        for x, y in sbox:
            ol.Append(kpt(x, y))
        board.Add(sz)

    # B.Cu Keepouts covering 100% of SW1_NODE & SW2_NODE copper + margin (leaving U1/U2 DAP clear!)
    ko_boxes = [
        (-12.90, +8.80, -8.25, +14.70),
        (-11.15, +6.65, -9.60, +9.00),
        (+6.10, +8.80, +10.75, +14.70),
        (+7.85, +6.65, +9.40, +9.00),
    ]
    for (x0, y0, x1, y1) in ko_boxes:
        add_rule_keepout(board, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], pcbnew.B_Cu)

    # Continuous B.Cu GND thermal plane (clearance 0.26mm >= Power_HV/Power_SW 0.25mm!)
    add_zone(
        board,
        [(-17.6, -22.6), (+17.6, -22.6), (+17.6, +22.6), (-17.6, +22.6)],
        pcbnew.B_Cu, nets["GND"], priority=0, min_thickness=0.20, clearance=0.26, solid_pads=True
    )

    # -----------------------------------------------------------------------
    # Explicit Short Critical Trunks (Power_SW, Power_HV, Power_5V, Kelvin FB/AGND)
    # -----------------------------------------------------------------------
    # 1. SW1_NODE / SW2_NODE: <= 0.80 mm exit stub (0.36 mm) inside U1/U2 courtyard -> 1.00 mm bridge
    add_track(board, [pt("U1", "7"), (-10.325, +9.10)], 0.36, nets["SW1_NODE"])
    add_track(board, [(-10.325, +9.10), (-10.325, +10.30)], 1.00, nets["SW1_NODE"])
    add_track(board, [(-10.325, +10.30), pt("D9", "2")], 1.00, nets["SW1_NODE"])
    add_track(board, [(-10.325, +10.30), (-11.60, +10.30)], 1.00, nets["SW1_NODE"])

    add_track(board, [pt("U2", "7"), (+8.675, +9.10)], 0.36, nets["SW2_NODE"])
    add_track(board, [(+8.675, +9.10), (+8.675, +10.30)], 1.00, nets["SW2_NODE"])
    add_track(board, [(+8.675, +10.30), pt("D10", "2")], 1.00, nets["SW2_NODE"])
    add_track(board, [(+8.675, +10.30), (+7.40, +10.30)], 1.00, nets["SW2_NODE"])

    # 2. Kelvin FB1_NET / FB2_NET & Kelvin AGND Star (R3.2 -> U1.6 -> DAP, R4.2 -> U2.6 -> DAP)
    add_track(board, [pt("U1", "6"), (-9.675, +5.40)], 0.36, nets["GND"])
    add_track(board, [pt("U1", "2"), (-10.325, +5.40)], 0.36, nets["GND"])
    add_track(board, [(-8.80, +4.40), (-8.20, +4.40), (-7.60, +3.40), (-2.40, +3.40), pt("R3", "2")], 0.45, nets["GND"])
    add_track(board, [pt("U1", "5"), (-8.35, +7.60)], 0.25, nets["FB1_NET"])
    add_via(board, -8.35, +7.60, nets["FB1_NET"], 0.60, 0.30)
    add_track(board, [(-8.35, +7.60), (-8.35, +4.45), (-5.90, +4.45)], 0.25, nets["FB1_NET"], pcbnew.B_Cu)
    add_via(board, -5.90, +4.45, nets["FB1_NET"], 0.60, 0.30)
    add_track(board, [(-5.90, +4.45), pt("R8", "1")], 0.25, nets["FB1_NET"])

    add_track(board, [pt("U2", "6"), (+9.325, +5.40)], 0.36, nets["GND"])
    add_track(board, [pt("U2", "2"), (+8.675, +5.40)], 0.36, nets["GND"])
    add_track(board, [(+10.20, +4.40), (+10.80, +4.40), (+11.40, +3.40), (+16.40, +3.40), pt("R4", "2")], 0.45, nets["GND"])
    add_track(board, [pt("U2", "5"), (+10.65, +7.60)], 0.25, nets["FB2_NET"])
    add_via(board, +10.65, +7.60, nets["FB2_NET"], 0.60, 0.30)
    add_track(board, [(+10.65, +7.60), (+10.65, +4.45), (+13.10, +4.45)], 0.25, nets["FB2_NET"], pcbnew.B_Cu)
    add_via(board, +13.10, +4.45, nets["FB2_NET"], 0.60, 0.30)
    add_track(board, [(+13.10, +4.45), pt("R9", "1")], 0.25, nets["FB2_NET"])

    # 3. UV_RET / VIS_RET taps (R3.1->R8.2, R4.1->R9.2)
    add_track(board, [pt("R3", "1"), (-4.80, +6.475), pt("R8", "2")], 0.60, nets["UV_RET"])
    add_track(board, [pt("R4", "1"), (+14.20, +6.475), pt("R9", "2")], 0.60, nets["VIS_RET"])

    # 4. U1/U2 VIN_PROT (<= 0.80mm stub inside courtyard into 1.50mm trunk at C7.1/C8.1), direct PGND->C7.2/C8.2 + vias, & DIM (pin 4)
    add_track(board, [pt("U1", "3"), (-9.675, +2.40), (-9.20, +1.45)], 0.36, nets["VIN_PROT"])
    add_track(board, [(-9.20, +1.45), (-9.05, +1.00), (-9.05, 0.00)], 1.50, nets["VIN_PROT"])
    add_track(board, [pt("U1", "2"), (-10.325, +2.10), pt("C7", "2")], 0.36, nets["GND"])
    add_track(board, [pt("C7", "2"), (-12.00, +1.85)], 0.60, nets["GND"])
    add_via(board, -12.00, +1.85, nets["GND"], 0.60, 0.30)
    u1_v4 = (-7.60, +2.45)
    add_track(board, [pt("U1", "4"), (-8.30, +2.475), u1_v4], 0.30, nets["EN1_NET"])

    add_track(board, [pt("U2", "3"), (+9.325, +2.40), (+9.80, +1.45)], 0.36, nets["VIN_PROT"])
    add_track(board, [(+9.80, +1.45), (+9.95, +1.00), (+9.95, 0.00)], 1.50, nets["VIN_PROT"])
    add_track(board, [pt("U2", "2"), (+8.675, +2.10), pt("C8", "2")], 0.36, nets["GND"])
    add_track(board, [pt("C8", "2"), (+7.10, +1.85)], 0.60, nets["GND"])
    add_via(board, +7.10, +1.85, nets["GND"], 0.60, 0.30)
    u2_v4 = (+11.40, +2.45)
    add_track(board, [pt("U2", "4"), (+10.70, +2.475), u2_v4], 0.30, nets["DIM2_NET"])

    # 5. J1 VBUS F.Cu continuous 1.50 mm trunk (<= 0.8mm pad escapes inside J1 courtyard) + CC1/CC2 B.Cu escapes
    add_track(board, [pt("J1", "B9"), pt("J1", "A4")], 0.50, nets["VBUS"])
    add_track(board, [pt("J1", "B4"), pt("J1", "A9")], 0.50, nets["VBUS"])
    add_track(board, [pt("J1", "A4"), (-2.125, -15.60)], 0.50, nets["VBUS"])
    add_track(board, [pt("J1", "A9"), (+2.125, -15.60)], 0.50, nets["VBUS"])
    add_track(board, [(+2.125, -15.60), (-2.125, -15.60), (-6.20, -15.60), pt("C12", "1")], 1.50, nets["VBUS"])

    # CC1 & CC2 route directly on B.Cu from J1 PTH pins -> never interrupt F.Cu VBUS trunk!
    add_track(board, [pt("J1", "A5"), (-0.625, -14.20)], 0.25, nets["CC1"], pcbnew.B_Cu)
    add_via(board, -0.625, -14.20, nets["CC1"], 0.60, 0.30)
    add_track(board, [(-0.625, -14.20), pt("R1", "1")], 0.25, nets["CC1"], pcbnew.F_Cu)

    add_track(board, [pt("J1", "B5"), (+1.275, -20.00), (+5.40, -20.00), (+5.40, -16.40), (+4.20, -16.40)], 0.25, nets["CC2"], pcbnew.B_Cu)
    add_via(board, +4.20, -16.40, nets["CC2"], 0.60, 0.30)
    add_track(board, [(+4.20, -16.40), (+4.20, -14.30), (+3.60, -14.30), (+3.60, -13.20), pt("R2", "1")], 0.25, nets["CC2"], pcbnew.F_Cu)

    # 6. Q1A/Q1B continuous F.Cu 1.50 mm power path (zero series vias!)
    # Q1A.3 -> F1.2 via VBUS_FUSED pour + 1.50 mm trunk
    add_track(board, [pt("Q1A", "3"), (-15.20, -10.50), pt("F1", "2")], 1.50, nets["VBUS_FUSED"])
    # Q1A.2 -> Q1B.2 via V_MID pour + 1.50 mm trunk
    add_track(board, [pt("Q1A", "2"), (-13.20, -6.75), (-11.20, -6.75), pt("Q1B", "2")], 1.50, nets["V_MID"])
    # Q1B.3 -> C1.1 -> D11.1 via 1.50 mm F.Cu trunk
    add_track(board, [pt("Q1B", "3"), (-9.60, -5.80), (-9.60, -3.30), (-10.525, -3.30), pt("C1", "1")], 1.50, nets["VIN_PROT"])
    add_track(board, [pt("C1", "1"), pt("D11", "1")], 1.50, nets["VIN_PROT"])
    add_track(board, [pt("C1", "1"), (-10.525, 0.00), (-9.05, 0.00)], 1.50, nets["VIN_PROT"])
    add_track(board, [(-10.525, 0.00), (-13.60, 0.00), pt("C2", "1"), (-16.00, +4.075), pt("L1", "1")], 1.50, nets["VIN_PROT"])
    add_track(board, [(-9.05, 0.00), (+5.40, 0.00), pt("C3", "1")], 1.50, nets["VIN_PROT"])
    add_track(board, [pt("J4", "2"), (-1.40, 0.00)], 1.50, nets["VIN_PROT"])
    add_track(board, [pt("C3", "1"), (+3.00, +4.075), pt("L2", "1")], 1.50, nets["VIN_PROT"])
    add_track(board, [(+5.40, 0.00), (+9.95, 0.00)], 1.50, nets["VIN_PROT"])

    # Explicit C1.2 & shared C6.2/C11.2/R13.2 GND vias before GridRouter
    add_track(board, [pt("D12", "2"), (+2.35, -9.80), (+0.45, -9.80), pt("R7", "1")], 0.25, nets["EN2_NET"])
    add_track(board, [pt("R7", "1"), (-4.15, -10.80), pt("R6", "1")], 0.25, nets["EN2_NET"])
    add_track(board, [pt("C1", "2"), (-7.4, -2.00)], 1.00, nets["GND"])
    add_via(board, -7.4, -2.00, nets["GND"], 0.60, 0.30)
    add_track(board, [pt("C6", "2"), (+4.4, -11.55), (+4.4, -12.2)], 0.35, nets["GND"])
    add_track(board, [pt("C11", "2"), (+4.4, -11.2), (+4.4, -12.2)], 0.35, nets["GND"])
    add_track(board, [pt("R13", "2"), (+4.4, -13.2), (+4.4, -12.2)], 0.35, nets["GND"])
    add_via(board, +4.4, -12.2, nets["GND"], 0.60, 0.30)

    # -----------------------------------------------------------------------
    # GridRouter for All Remaining Connections (Zero Crossings / Zero Shorts)
    # -----------------------------------------------------------------------
    router = GridRouter(board, ko_boxes)

    # Power_HV (VOUT1, VOUT2, UV_RET, VIS_RET: >= 0.60 mm, >= 0.25 mm clearance)
    router.route(pt("D9", "1"), 0, pt("C4", "1"), 0, nets["VOUT1"], 1.00, 0.25, allow_b=False)
    router.route(pt("D9", "1"), 0, pt("C9", "1"), 0, nets["VOUT1"], 1.00, 0.25, allow_b=False)
    router.route(pt("C4", "1"), 0, pt("J2", "1"), 0, nets["VOUT1"], 1.00, 0.25, allow_b=False)
    router.route(pt("D9", "1"), 0, pt("D13", "1"), 0, nets["VOUT1"], 0.60, 0.25, allow_b=False)
    router.route(pt("J2", "2"), 1, pt("R3", "1"), 0, nets["UV_RET"], 0.60, 0.25)

    router.route(pt("D10", "1"), 0, pt("C5", "1"), 0, nets["VOUT2"], 1.00, 0.25, allow_b=False)
    router.route(pt("D10", "1"), 0, pt("C10", "1"), 0, nets["VOUT2"], 1.00, 0.25, allow_b=False)
    router.route(pt("C5", "1"), 0, pt("J3", "1"), 0, nets["VOUT2"], 1.00, 0.25, allow_b=False)
    router.route(pt("D10", "1"), 0, pt("D14", "1"), 0, nets["VOUT2"], 0.60, 0.25, allow_b=False)
    # Keep J3.2 B.Cu exit clear of "2:VIS- 1:VIS+" bottom silkscreen
    add_track(board, [pt("J3", "2"), (+9.60, +19.20), (+9.60, +15.50)], 0.60, nets["VIS_RET"], pcbnew.B_Cu)
    router.add_seg_obstacle(+6.45, +19.20, +9.60, +19.20, 0.60, pcbnew.B_Cu, "VIS_RET")
    router.add_seg_obstacle(+9.60, +19.20, +9.60, +15.50, 0.60, pcbnew.B_Cu, "VIS_RET")
    router.route((+9.60, +15.50), 1, pt("R4", "1"), 0, nets["VIS_RET"], 0.60, 0.25)

    router.route((-5.90, +4.45), 1, pt("D13", "2"), 0, nets["FB1_NET"], 0.25, 0.20)
    router.route((+13.10, +4.45), 1, pt("D14", "2"), 0, nets["FB2_NET"], 0.25, 0.20)

    # Power_5V trunks (1.50 mm on F.Cu)
    router.route(pt("C12", "1"), 0, pt("TP1", "1"), 0, nets["VBUS"], 1.50, 0.20, allow_b=False)
    router.route(pt("TP1", "1"), 0, pt("F1", "1"), 0, nets["VBUS"], 1.50, 0.20, allow_b=False)

    # Protection & OVP/SS signals (route Q1_GATE around Q1A/Q1B before V_MID sense taps!)
    router.route(pt("Q1A", "1"), 0, pt("D15", "2"), 0, nets["Q1_GATE"], 0.25, 0.20)
    router.route(pt("Q1A", "1"), 0, pt("Q1B", "1"), 0, nets["Q1_GATE"], 0.25, 0.20)

    # V_MID sense taps (D15.1 & OVP/SS cluster inside Sense_Tap_Area)
    router.route(pt("Q1A", "2"), 0, pt("D15", "1"), 0, nets["V_MID"], 0.40, 0.20)
    # Route local OVP_SENSE R12.2->R13.1 & Q3_BASE first
    router.route(pt("R12", "2"), 0, pt("R13", "1"), 0, nets["OVP_SENSE"], 0.25, 0.20, allow_b=False)
    router.route(pt("R14", "2"), 0, pt("C11", "1"), 0, nets["Q3_BASE"], 0.25, 0.20)
    router.route(pt("C11", "1"), 0, pt("Q3", "1"), 0, nets["Q3_BASE"], 0.25, 0.20)
    router.route(pt("Q3", "1"), 0, pt("Q4", "3"), 0, nets["Q3_BASE"], 0.25, 0.20)
    router.route(pt("Q3", "2"), 0, pt("R11", "1"), 0, nets["Q3_EMIT"], 0.25, 0.20)
    # V_MID sense feed to R12.1 (jumps cleanly on B.Cu under Sense_Tap_Area)
    router.route(pt("Q1B", "2"), 0, pt("R12", "1"), 0, nets["V_MID"], 0.40, 0.20)
    router.route(pt("R12", "1"), 0, pt("R14", "1"), 0, nets["V_MID"], 0.35, 0.20)
    router.route(pt("R14", "1"), 0, pt("R10", "1"), 0, nets["V_MID"], 0.35, 0.20)
    router.route(pt("R10", "1"), 0, pt("R15", "1"), 0, nets["V_MID"], 0.35, 0.20)
    router.route(pt("R15", "1"), 0, pt("Q2", "2"), 0, nets["V_MID"], 0.35, 0.20)

    # Signals (>= 0.25 mm) — route D12.3 (EN1_NET) before D12.1/D12.2 so D12.3 isn't boxed in
    router.route(pt("D12", "3"), 0, pt("R5", "1"), 0, nets["EN1_NET"], 0.25, 0.20)
    router.route(pt("R5", "1"), 0, u1_v4, 0, nets["EN1_NET"], 0.25, 0.20)
    router.route(pt("J4", "1"), 0, pt("D12", "1"), 0, nets["SW_UV_EN"], 0.25, 0.20)
    router.route(pt("J4", "3"), 0, pt("D12", "2"), 0, nets["EN2_NET"], 0.25, 0.20)
    router.route(pt("R7", "2"), 0, pt("C6", "1"), 0, nets["DIM2_NET"], 0.25, 0.20)
    router.route(pt("C6", "1"), 0, u2_v4, 0, nets["DIM2_NET"], 0.25, 0.20)

    # Remaining Q1_GATE & OVP/SS signals
    router.route(pt("Q1B", "1"), 0, pt("Q3", "3"), 0, nets["Q1_GATE"], 0.25, 0.20)
    router.route(pt("Q3", "3"), 0, pt("R10", "2"), 0, nets["Q1_GATE"], 0.25, 0.20)
    router.route(pt("R10", "2"), 0, pt("R18", "2"), 0, nets["Q1_GATE"], 0.25, 0.20)

    router.route(pt("R13", "1"), 0, pt("U3", "2"), 0, nets["OVP_SENSE"], 0.25, 0.20)
    router.route(pt("U3", "2"), 0, pt("R19", "2"), 0, nets["OVP_SENSE"], 0.25, 0.20)
    router.route(pt("U3", "1"), 0, pt("R16", "2"), 0, nets["OVP_K"], 0.25, 0.20)
    router.route(pt("R16", "1"), 0, pt("R15", "2"), 0, nets["Q2_BASE"], 0.25, 0.20)
    router.route(pt("R15", "2"), 0, pt("Q2", "1"), 0, nets["Q2_BASE"], 0.25, 0.20)
    router.route(pt("Q2", "3"), 0, pt("D16", "3"), 0, nets["OVP_DRV"], 0.25, 0.20)
    router.route(pt("D16", "3"), 0, pt("R17", "1"), 0, nets["OVP_DRV"], 0.25, 0.20)
    router.route(pt("D16", "1"), 0, pt("R18", "1"), 0, nets["OVP_DRV_GATE"], 0.25, 0.20)
    router.route(pt("D16", "2"), 0, pt("R19", "1"), 0, nets["OVP_HYS"], 0.25, 0.20)
    router.route(pt("R17", "2"), 0, pt("R20", "1"), 0, nets["Q4_BASE"], 0.25, 0.20)
    router.route(pt("R17", "2"), 0, pt("Q4", "1"), 0, nets["Q4_BASE"], 0.25, 0.20)

    # GND stitching for all SMD GND pads -> B.Cu GND plane (route cleanly to a nearby free B.Cu via)
    gnd_pads = [
        ("C12", "2", 0.50), ("R1", "2", 0.35), ("R2", "2", 0.35),
        ("D11", "2", 1.00),
        ("C2", "2", 1.00), ("C4", "2", 1.00), ("C9", "2", 0.80),
        ("C3", "2", 1.00), ("C5", "2", 1.00), ("C10", "2", 0.80),
        ("U3", "3", 0.35), ("R11", "2", 0.35),
        ("Q4", "2", 0.35), ("R20", "2", 0.35), ("R5", "2", 0.35), ("R6", "2", 0.35),
    ]
    for ref, pnum, gw in gnd_pads:
        px, py = pt(ref, pnum)
        _, via_blk = router._build_blocked("GND", gw / 2.0, 0.22)
        candidates = []
        for dx in range(-48, 49):
            for dy in range(-48, 49):
                tx, ty = px + dx * router.RES, py + dy * router.RES
                if -17.0 <= tx <= 17.0 and -22.0 <= ty <= 22.0:
                    ix, iy = router._to_ij(tx, ty)
                    if not via_blk[ix][iy]:
                        candidates.append((dx * dx + dy * dy, tx, ty))
        candidates.sort()
        routed = False
        for _, vx, vy in candidates[:150]:
            try:
                router.route((px, py), 0, (vx, vy), 0, nets["GND"], gw, 0.20, allow_b=True)
                add_via(board, vx, vy, nets["GND"], 0.60, 0.30)
                router.add_via_obstacle(vx, vy, 0.60, "GND")
                routed = True
                break
            except RuntimeError:
                continue
        assert routed, f"Could not route GND via near {ref}.{pnum}"

    # Fill all copper zones
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())

    # Add board-level silkscreen labels clear of pads & mask openings
    # Bottom view (+X is LEFT, -X is RIGHT): J2.2(UV-) at x=-3.95 (left), J2.1(UV+) at x=-6.45 (right)
    # J3.2(VIS-) at x=+6.45 (left), J3.1(VIS+) at x=+3.95 (right)
    for txt_str, xm, ym, lyr in [
        ("LEPILED DRIVER v1.0", 0.0, +21.5, pcbnew.B_SilkS),
        ("2:UV-  1:UV+", -5.2, +16.7, pcbnew.B_SilkS),
        ("2:VIS-  1:VIS+", +5.2, +16.7, pcbnew.B_SilkS),
        ("TP1:5V", -8.2, -21.6, pcbnew.F_SilkS),
        ("TP2:GND", +8.2, -21.6, pcbnew.F_SilkS),
    ]:
        t = pcbnew.PCB_TEXT(board)
        t.SetText(txt_str)
        t.SetLayer(lyr)
        t.SetPosition(kpt(xm, ym))
        t.SetTextSize(pcbnew.VECTOR2I(mm(0.62), mm(0.62)))
        t.SetTextThickness(mm(0.11))
        if lyr == pcbnew.B_SilkS:
            t.SetMirrored(True)
        board.Add(t)

    pcbnew.SaveBoard(str(pcb_path), board)

    def filled_area_mm2(zone: pcbnew.ZONE) -> float:
        return zone.GetFilledPolysList(pcbnew.F_Cu).Area() / 1e12

    metrics = {
        "vout1_pour_mm2": round(filled_area_mm2(z_vout1), 2),
        "vout2_pour_mm2": round(filled_area_mm2(z_vout2), 2),
    }
    print("Board 1 saved:", pcb_path, "| Pour metrics:", metrics)
    return metrics


# ---------------------------------------------------------------------------
# 5. ERC, DRC, Gerbers, Drill, CPL, BOM & Renders
# ---------------------------------------------------------------------------

def verify_and_export(comp_rows):
    tbin = Path("/home/alimuldal/.local/share/lepiled-tools/bin")
    kcli = str(tbin / "kicad-cli")
    gerbv = str(tbin / "gerbv")

    sch_path = BASE_DIR / "driver_pcb.kicad_sch"
    pcb_path = BASE_DIR / "driver_pcb.kicad_pcb"

    GERBER_DIR.mkdir(parents=True, exist_ok=True)
    RENDER_DIR.mkdir(parents=True, exist_ok=True)

    for fmt, ext in [("json", "json"), ("report", "rpt")]:
        subprocess.run(
            [kcli, "sch", "erc", "--format", fmt, "--severity-all", "--exit-code-violations",
             "-o", str(BASE_DIR / f"erc_report.{ext}"), str(sch_path)],
            check=True,
        )

    for fmt, ext in [("json", "json"), ("report", "rpt")]:
        subprocess.run(
            [kcli, "pcb", "drc", "--format", fmt, "--schematic-parity", "--severity-all", "--exit-code-violations",
             "-o", str(BASE_DIR / f"drc_report.{ext}"), str(pcb_path)],
            check=True,
        )

    for old_f in GERBER_DIR.glob("*"):
        if old_f.is_file():
            old_f.unlink()
    subprocess.run(
        [kcli, "pcb", "export", "gerbers", "--no-protel-ext", "--use-drill-file-origin",
         "-o", str(GERBER_DIR) + "/",
         "-l", "F.Cu,B.Cu,F.Mask,B.Mask,F.SilkS,B.SilkS,F.Paste,Edge.Cuts", str(pcb_path)],
        check=True,
    )
    subprocess.run(
        [kcli, "pcb", "export", "drill", "--format", "excellon", "--drill-origin", "plot",
         "--excellon-units", "mm", "--excellon-separate-th",
         "--generate-map", "--map-format", "pdf", "--generate-report",
         "-o", str(GERBER_DIR) + "/", str(pcb_path)],
        check=True,
    )

    zip_path = GERBER_DIR / "driver_pcb_gerbers.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in sorted(GERBER_DIR.iterdir()):
            if f.name.endswith((".gbr", ".drl", ".gbrjob")):
                zf.write(f, f.name)

    raw_pos = RENDER_DIR / "_raw_pos.csv"
    subprocess.run(
        [kcli, "pcb", "export", "pos", "--format", "csv", "--units", "mm",
         "--use-drill-file-origin", "--exclude-dnp",
         "-o", str(raw_pos), str(pcb_path)],
        check=True,
    )
    with raw_pos.open() as f_in, (PCB_DESIGN_DIR / "driver_pcb_cpl.csv").open("w", newline="") as f_out:
        reader = csv.DictReader(f_in)
        writer = csv.writer(f_out)
        writer.writerow(["Designator", "Mid X", "Mid Y", "Layer", "Rotation"])
        for row in reader:
            writer.writerow([
                row["Ref"], f"{float(row['PosX']):.3f}", f"{float(row['PosY']):.3f}",
                "Top" if row["Side"].lower() == "top" else "Bottom",
                f"{float(row['Rot']):.1f}",
            ])
    raw_pos.unlink()

    with (PCB_DESIGN_DIR / "driver_pcb_bom.csv").open("w", newline="") as f_all, \
         (PCB_DESIGN_DIR / "driver_pcb_bom_pcba.csv").open("w", newline="") as f_pcba:
        cols = ["Designator", "Qty", "Category", "MPN", "Comment", "Footprint", "Mounting", "DNP"]
        w_all = csv.writer(f_all)
        w_pcba = csv.writer(f_pcba)
        w_all.writerow(cols)
        w_pcba.writerow(cols)
        for ref, r in comp_rows.items():
            dnp_flag = "Yes" if r["Mounting"] == "Off-Board" else "No"
            line = [ref, r["Qty"], r["Category"], r["MPN"], r["Value_Rating"], r["Package_Footprint"], r["Mounting"], dnp_flag]
            w_all.writerow(line)
            if r["Mounting"] == "On-PCB":
                w_pcba.writerow(line)

    subprocess.run([kcli, "sch", "export", "pdf", "-o", str(RENDER_DIR / "schematic.pdf"), str(sch_path)], check=True)
    subprocess.run(
        [kcli, "pcb", "export", "svg", "-o", str(RENDER_DIR / "board.svg"),
         "-l", "F.Cu,B.Cu,F.SilkS,B.SilkS,Edge.Cuts", "--mode-single", "--fit-page-to-board", "--exclude-drawing-sheet", str(pcb_path)],
        check=True,
    )
    subprocess.run(
        [kcli, "pcb", "render", "--side", "top", "-w", "1400", "-h", "1800", "--quality", "high",
         "-o", str(RENDER_DIR / "render_top.png"), str(pcb_path)],
        check=True,
    )
    subprocess.run(
        [kcli, "pcb", "render", "--side", "bottom", "-w", "1400", "-h", "1800", "--quality", "high",
         "-o", str(RENDER_DIR / "render_bottom.png"), str(pcb_path)],
        check=True,
    )
    subprocess.run(
        [gerbv, "-x", "png", "-D", "300", "-o", str(RENDER_DIR / "gerbv_top.png"),
         str(GERBER_DIR / "driver_pcb-F_Cu.gbr"),
         str(GERBER_DIR / "driver_pcb-F_Silkscreen.gbr"),
         str(GERBER_DIR / "driver_pcb-Edge_Cuts.gbr"),
         str(GERBER_DIR / "driver_pcb-PTH.drl")],
        check=True,
    )
    subprocess.run(
        [gerbv, "-x", "png", "-D", "300", "-o", str(RENDER_DIR / "gerbv_bottom.png"),
         str(GERBER_DIR / "driver_pcb-B_Cu.gbr"),
         str(GERBER_DIR / "driver_pcb-B_Silkscreen.gbr"),
         str(GERBER_DIR / "driver_pcb-Edge_Cuts.gbr"),
         str(GERBER_DIR / "driver_pcb-PTH.drl")],
        check=True,
    )
    print("Board 1 verification & exports completed cleanly.")


def main():
    with COMPONENT_CSV.open() as f:
        comp_rows = {row["RefDes"]: row for row in csv.DictReader(f)}
    assert len(comp_rows) == 71

    write_lib_tables()
    write_kicad_pro()
    syms = build_symbol_defs()
    write_kicad_sym(syms)
    create_footprints()
    specs = write_kicad_sch(syms, comp_rows)
    metrics = build_board(specs, comp_rows)
    verify_and_export(comp_rows)


if __name__ == "__main__":
    main()
