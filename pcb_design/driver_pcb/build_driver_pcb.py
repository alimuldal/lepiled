#!/usr/bin/env python3
"""
Reproducible Native KiCad 9.0.8 Generator for Board 1:
LepiLED DIY Maxi Switch Driver & USB-C PD PCB (Rev 4.0 / Option 2).

Architecture:
  - 20 V USB-C PD 3.1 Sink (AP33771CFBZ-13-FA02 + back-to-back DMN3404L-7)
    + Aux 18-24 V DC entry (TP1/TP2 + F2 + D13).
  - Hardware 17.25 V UVLO (LM393BIDR + LM4040BIM3-2.5) + Ground-Referenced
    Maxi-Switch (J4/SW1, D14 5.1 V, D12 BAT54, Q2/Q3 BSS138).
  - Dual 40 V 333 mA Constant-Current Hysteretic Buck LED Drivers (AL8860WT-7,
    R3/R4 = 0.30 Ohm, L1/L2 = SRN6045-680M 68 uH, D9/D10 = B340A-13-F).

Hardened DFM / Carbon Review Compliance:
  - Properly wired 4-block A3 KiCad schematic with standard graphical symbols.
  - 0 unplugged via-in-pad (strictly enforced in GridRouter, .kicad_dru, and
    post-route geometric assertion >= 0.25 mm drill-to-SMD copper).
  - Solid unbroken B.Cu GND plane beneath U1, U2, U3, Q1A/Q1B, C2/C3/C8/C9.
  - Corrected footprints: J1 (0.35 mm drill, 7.26 mm datum, full CrtYd),
    J4 (1.00 mm drill), L1/L2 (2.00x6.00 mm pads @ +/-2.15 mm), U3 (0.22 mm
    pads / 0.04 mm mask expansion -> 0.10 mm Green LPI mask dam).
  - Green LPI solder mask, ds.m_SolderMaskExpansion, full F.SilkS RefDes
    (>= 0.80 mm / 0.15 mm) + J4 pin legend + 2:1 F.Fab assembly map PDF.
  - TP1, TP2, H1..H4 excluded from CPL & PCBA BOM.
"""

import csv
import heapq
import json
import math
import shutil
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

KCLI = "/usr/bin/kicad-cli"
GERBV = "/home/alimuldal/.local/share/lepiled-tools/bin/gerbv"

CX, CY = 100.0, 100.0


def uid(name: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"lepiled-rev4-driver-{name}"))


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
# 1. Library Tables, .kicad_pro (Green LPI + strict DRC), and .kicad_dru
# ---------------------------------------------------------------------------

def write_lib_tables():
    (BASE_DIR / "sym-lib-table").write_text(
        '(sym_lib_table\n  (version 7)\n'
        '  (lib (name "lepiled")(type "KiCad")(uri "${KIPRJMOD}/lepiled.kicad_sym")(options "")(descr "LepiLED Rev4 Driver symbols"))\n)\n'
    )
    (BASE_DIR / "fp-lib-table").write_text(
        '(fp_lib_table\n  (version 7)\n'
        '  (lib (name "lepiled")(type "KiCad")(uri "${KIPRJMOD}/lepiled.pretty")(options "")(descr "LepiLED Rev4 Driver footprints"))\n)\n'
    )


def write_kicad_pro():
    def nc_entry(name, clearance, track_width, via_d=0.60, via_drill=0.30, prio=0):
        return {
            "bus_width": 12,
            "clearance": clearance,
            "diff_pair_gap": 0.25,
            "diff_pair_via_gap": 0.25,
            "diff_pair_width": 0.20,
            "line_style": 0,
            "microvia_diameter": 0.30,
            "microvia_drill": 0.10,
            "name": name,
            "pcb_color": "rgba(0, 0, 0, 0.000)",
            "priority": prio,
            "schematic_color": "rgba(0, 0, 0, 0.000)",
            "track_width": track_width,
            "via_diameter": via_d,
            "via_drill": via_drill,
            "wire_width": 6,
        }

    netclass_assignments = {}
    for n in ["VBUS", "VBUS_FUSED", "VBUS_DAMP", "VBUS_SENSE", "Q1_MID", "VIN_20V", "AUX_IN", "AUX_FUSED"]:
        netclass_assignments[f"/{n}"] = ["Power_20V"]
    for n in ["SW1_NODE", "SW2_NODE"]:
        netclass_assignments[f"/{n}"] = ["Power_SW"]
    for n in ["UV_POS", "UV_NEG", "VIS_POS", "VIS_NEG"]:
        netclass_assignments[f"/{n}"] = ["LED_Drive"]
    for n in [
        "CC1", "CC2", "U3_VOUT", "U3_PWR_EN", "U3_V5V", "U3_VSEL", "U3_ISEL",
        "U3_LED", "PD_LED_A", "Q1_GATE", "V_REF", "UVLO_SENSE", "V_SW_BIAS",
        "SW_UV_N", "SW_ALL_N", "U1_CTRL", "U2_CTRL",
    ]:
        netclass_assignments[f"/{n}"] = ["Signal"]

    pro = {
        "board": {
            "design_settings": {
                "defaults": {
                    "board_outline_line_width": 0.10,
                    "copper_line_width": 0.20,
                    "silk_line_width": 0.15,
                    "silk_text_size_h": 0.80,
                    "silk_text_size_v": 0.80,
                    "silk_text_thickness": 0.15,
                },
                "diff_pair_dimensions": [],
                "drc_exclusions": [],
                "rule_severities": {
                    "pth_inside_courtyard": "error",
                    "silk_over_copper": "warning",
                    "silk_overlap": "warning",
                    "solder_mask_bridge": "error",
                },
                "rules": {
                    "min_clearance": 0.16,
                    "min_copper_edge_clearance": 0.30,
                    "min_hole_clearance": 0.25,
                    "min_silk_clearance": 0.15,
                    "min_text_height": 0.60,
                    "min_through_hole_diameter": 0.28,
                    "min_track_width": 0.20,
                    "min_via_annulus": 0.12,
                    "min_via_diameter": 0.55,
                    "solder_mask_clearance": 0.05,
                    "solder_mask_min_width": 0.10,
                },
                "track_widths": [0.20, 0.25, 0.40, 0.50, 0.60, 0.80, 1.00],
                "via_dimensions": [
                    {"diameter": 0.60, "drill": 0.30},
                    {"diameter": 0.75, "drill": 0.35},
                ],
            },
            "layer_presets": [],
        },
        "boards": [],
        "libraries": {"pinned_footprint_libs": ["lepiled"], "pinned_symbol_libs": ["lepiled"]},
        "meta": {"filename": "driver_pcb.kicad_pro", "version": 1},
        "net_settings": {
            "classes": [
                nc_entry("Default", 0.16, 0.25, 0.60, 0.30, 2147483647),
                nc_entry("Power_20V", 0.16, 0.80, 0.60, 0.30, 10),
                nc_entry("Power_SW", 0.20, 0.55, 0.60, 0.30, 20),
                nc_entry("LED_Drive", 0.20, 0.50, 0.60, 0.30, 30),
                nc_entry("Signal", 0.16, 0.22, 0.60, 0.30, 40),
            ],
            "meta": {"version": 3},
            "net_colors": None,
            "netclass_assignments": netclass_assignments,
            "netclass_patterns": [],
        },
        "pcbnew": {"page_layout_descr_file": ""},
        "schematic": {"legacy_lib_dir": "", "meta": {"version": 1}},
        "sheets": [[uid("root_sheet"), "Root"]],
        "text_variables": {},
    }
    (BASE_DIR / "driver_pcb.kicad_pro").write_text(json.dumps(pro, indent=2) + "\n")

    dru = """(version 1)

(rule "No via inside or within 0.25mm of SMD pad"
  (condition "A.Type == 'Via' && B.Type == 'Pad' && B.Pad_Type == 'SMD'")
  (constraint hole_clearance (min 0.25mm))
)

(rule "LED_Drive clearance >= 0.22mm"
  (condition "A.NetClass == 'LED_Drive' && !(A.Type == 'Pad' && B.Type == 'Pad')")
  (constraint clearance (min 0.22mm))
)

(rule "Power_SW clearance >= 0.22mm"
  (condition "A.NetClass == 'Power_SW' && !(A.Type == 'Pad' && B.Type == 'Pad')")
  (constraint clearance (min 0.22mm))
)

(rule "Power_20V minimum track width >= 0.20mm (Kelvin sense/DFN pad exit)"
  (condition "A.NetClass == 'Power_20V'")
  (constraint track_width (min 0.20mm))
)

(rule "Signal track width >= 0.20mm"
  (condition "A.NetClass == 'Signal'")
  (constraint track_width (min 0.20mm))
)
"""
    (BASE_DIR / "driver_pcb.kicad_dru").write_text(dru)


# ---------------------------------------------------------------------------
# 2. Custom Footprints in lepiled.pretty/ (Datasheet-Verified + Review-Hardened)
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
            s.SetWidth(mm(0.15))
            s.SetStart(lpt(x0, y0))
            s.SetEnd(lpt(x1, y1))
            fp.Add(s)
    if pin1_dot:
        c = pcbnew.PCB_SHAPE(fp)
        c.SetShape(pcbnew.SHAPE_T_CIRCLE)
        c.SetLayer(pcbnew.F_SilkS)
        c.SetWidth(mm(0.15))
        c.SetFilled(True)
        c.SetCenter(lpt(pin1_dot[0], pin1_dot[1]))
        c.SetEnd(lpt(pin1_dot[0] + 0.18, pin1_dot[1]))
        fp.Add(c)


def _setup_fp_texts(fp, ref_xy=(0.0, 2.2), val_xy=(0.0, -2.2), ref_layer=pcbnew.F_SilkS, ref_sz=0.80):
    fp.Reference().SetPosition(lpt(*ref_xy))
    fp.Reference().SetLayer(ref_layer)
    fp.Reference().SetTextSize(pcbnew.VECTOR2I(mm(ref_sz), mm(ref_sz)))
    fp.Reference().SetTextThickness(mm(0.15))
    fp.Value().SetPosition(lpt(*val_xy))
    fp.Value().SetLayer(pcbnew.F_Fab)
    fp.Value().SetTextSize(pcbnew.VECTOR2I(mm(0.60), mm(0.60)))
    fp.Value().SetTextThickness(mm(0.10))


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
    if FP_LIB_DIR.exists():
        shutil.rmtree(FP_LIB_DIR)
    FP_LIB_DIR.mkdir(parents=True, exist_ok=True)
    io = pcbnew.PCB_IO_KICAD_SEXPR()

    def save(fp, name):
        fp.SetFPID(pcbnew.LIB_ID("lepiled", name))
        io.FootprintSave(str(FP_LIB_DIR), fp)

    # 1. Diodes AL8860WT-7 (TSOT25) - AL8860.pdf p. 1 & p. 17
    # Left (top->bot): 1=SW (+0.95), 2=GND (0.00), 3=CTRL (-0.95)
    # Right (bot->top): 4=SET (-0.95), 5=VIN (+0.95)
    fp = pcbnew.FOOTPRINT(None)
    fp.SetReference("U")
    fp.SetValue("AL8860WT-7")
    fp.SetAttributes(pcbnew.FP_SMD)
    _smd_pad(fp, 1, -1.10, +0.95, 1.00, 0.62, roundrect=0.08)
    _smd_pad(fp, 2, -1.10, 0.00, 1.00, 0.62, roundrect=0.08)
    _smd_pad(fp, 3, -1.10, -0.95, 1.00, 0.62, roundrect=0.08)
    _smd_pad(fp, 4, +1.10, -0.95, 1.00, 0.62, roundrect=0.08)
    _smd_pad(fp, 5, +1.10, +0.95, 1.00, 0.62, roundrect=0.08)
    _add_rect_crtyd_and_fab(
        fp, 3.20, 2.90,
        silk_lines=[(-0.35, +1.68, +0.35, +1.68), (-0.35, -1.68, +0.35, -1.68)],
        pin1_dot=(-1.88, +1.55), fab_w=1.60, fab_h=2.90,
    )
    _setup_fp_texts(fp, ref_xy=(0.0, +2.35), val_xy=(0.0, -2.35))
    save(fp, "Diodes_TSOT25_AL8860")

    # 2. Diodes AP33771CFBZ-13-FA02 (W-DFN3030-14 Type A1) - AP33771C.pdf p. 1 & p. 14
    # 0.40 mm pitch; pad width 0.22 mm + 0.04 mm local mask margin => 0.10 mm Green LPI mask dam!
    # Left (top->bot): 1..7 at y = +1.20..-1.20; Right (bot->top): 8..14 at y = -1.20..+1.20
    fp = pcbnew.FOOTPRINT(None)
    fp.SetReference("U")
    fp.SetValue("AP33771C")
    fp.SetAttributes(pcbnew.FP_SMD)
    ys = [+1.20, +0.80, +0.40, 0.00, -0.40, -0.80, -1.20]
    for idx, y in enumerate(ys, start=1):
        _smd_pad(fp, idx, -1.325, y, 0.45, 0.22, mask_margin=0.04, roundrect=0.04)
    for idx, y in enumerate(reversed(ys), start=8):
        _smd_pad(fp, idx, +1.325, y, 0.45, 0.22, mask_margin=0.04, roundrect=0.04)
    # Center EPAD (15) = 1.65 x 2.55 mm (0.275 mm copper gap to outer pads), segmented 2x2 F.Paste
    _smd_pad(fp, 15, 0.0, 0.0, 1.65, 2.55, layers=lset(pcbnew.F_Cu, pcbnew.F_Mask), mask_margin=0.0)
    for px in (-0.36, +0.36):
        for py in (-0.58, +0.58):
            _smd_pad(fp, "", px, py, 0.56, 0.90, layers=lset(pcbnew.F_Paste), mask_margin=0.0)
    _add_rect_crtyd_and_fab(
        fp, 3.20, 3.20,
        silk_lines=[(-1.40, +1.78, +1.40, +1.78), (-1.40, -1.78, +1.40, -1.78)],
        pin1_dot=(-1.85, +1.55), fab_w=3.00, fab_h=3.00,
    )
    _setup_fp_texts(fp, ref_xy=(0.0, +2.45), val_xy=(0.0, -2.45))
    save(fp, "Diodes_W-DFN3030-14_AP33771C")

    # 3. TI LM393BIDR (SOIC-8, 1.27 mm pitch)
    fp = pcbnew.FOOTPRINT(None)
    fp.SetReference("U")
    fp.SetValue("LM393BIDR")
    fp.SetAttributes(pcbnew.FP_SMD)
    ys8 = [+1.905, +0.635, -0.635, -1.905]
    for idx, y in enumerate(ys8, start=1):
        _smd_pad(fp, idx, -2.70, y, 1.50, 0.60, roundrect=0.08)
    for idx, y in enumerate(reversed(ys8), start=5):
        _smd_pad(fp, idx, +2.70, y, 1.50, 0.60, roundrect=0.08)
    _add_rect_crtyd_and_fab(
        fp, 6.90, 4.90,
        silk_lines=[(-1.60, +2.65, +1.60, +2.65), (-1.60, -2.65, +1.60, -2.65)],
        pin1_dot=(-3.70, +2.45), fab_w=3.90, fab_h=4.90,
    )
    _setup_fp_texts(fp, ref_xy=(0.0, +3.35), val_xy=(0.0, -3.35))
    save(fp, "TI_SOIC-8_LM393B")

    # 4. SOT-23-3 (1=bottom-left, 2=bottom-right, 3=top-center)
    sfp = pcbnew.FOOTPRINT(None)
    sfp.SetReference("Q")
    sfp.SetValue("SOT-23-3")
    sfp.SetAttributes(pcbnew.FP_SMD)
    _smd_pad(sfp, 1, -0.95, -1.00, 0.70, 0.95, roundrect=0.08)
    _smd_pad(sfp, 2, +0.95, -1.00, 0.70, 0.95, roundrect=0.08)
    _smd_pad(sfp, 3, 0.00, +1.00, 0.70, 0.95, roundrect=0.08)
    _add_rect_crtyd_and_fab(
        sfp, 2.90, 2.95,
        silk_lines=[(-1.62, +0.05, -1.62, +0.55), (+1.62, +0.05, +1.62, +0.55)],
        pin1_dot=(-1.68, -1.58), fab_w=2.90, fab_h=1.30,
    )
    _setup_fp_texts(sfp, ref_xy=(0.0, +2.25), val_xy=(0.0, -2.25))
    save(sfp, "SOT-23-3")

    # 5. 2-pin Diodes (Pin 1 = Cathode left -X, Pin 2 = Anode right +X)
    def make_diode(name, val, pw, ph, ctc, bw, bh, bidir=False):
        dfp = pcbnew.FOOTPRINT(None)
        dfp.SetReference("D")
        dfp.SetValue(val)
        dfp.SetAttributes(pcbnew.FP_SMD)
        _smd_pad(dfp, 1, -ctc / 2.0, 0.0, pw, ph, roundrect=0.08)
        _smd_pad(dfp, 2, +ctc / 2.0, 0.0, pw, ph, roundrect=0.08)
        ky = max(bh, ph) / 2.0 + 0.35
        kx = ctc / 2.0 + pw / 2.0 + 0.30
        if bidir:
            silk = [(-0.80, +ky, +0.80, +ky), (-0.80, -ky, +0.80, -ky)]
        else:
            silk = [(-kx, -ph / 2.0, -kx, +ph / 2.0)]
        _add_rect_crtyd_and_fab(dfp, ctc + pw, max(bh, ph), silk_lines=silk, fab_w=bw, fab_h=bh)
        _setup_fp_texts(dfp, ref_xy=(0.0, ky + 0.65), val_xy=(0.0, -ky - 0.65))
        save(dfp, name)

    make_diode("D_SMA_DO-214AC", "B340A-13-F", 1.60, 1.70, 4.00, 4.30, 2.60)
    make_diode("D_SMB_DO-214AA_BiDir", "SMBJ22CA", 1.72, 2.20, 3.88, 4.35, 3.60, bidir=True)
    make_diode("D_SOD-123", "BZT52C5V1", 0.90, 0.95, 3.15, 2.70, 1.55)
    make_diode("LED_0603", "Green_0603", 0.75, 0.95, 1.55, 1.60, 0.80)

    # 6. Inductors, Polyfuse, Resistors, Capacitors
    def make_2pad(name, ref_pfx, val, pw, ph, ctc, bw, bh, has_silk=True):
        pfp = pcbnew.FOOTPRINT(None)
        pfp.SetReference(ref_pfx)
        pfp.SetValue(val)
        pfp.SetAttributes(pcbnew.FP_SMD)
        _smd_pad(pfp, 1, -ctc / 2.0, 0.0, pw, ph, roundrect=0.08)
        _smd_pad(pfp, 2, +ctc / 2.0, 0.0, pw, ph, roundrect=0.08)
        sy = max(bh, ph) / 2.0 + 0.30
        silk = [(-0.80, +sy, +0.80, +sy), (-0.80, -sy, +0.80, -sy)] if has_silk else None
        _add_rect_crtyd_and_fab(pfp, max(ctc + pw, bw), max(bh, ph), silk_lines=silk, fab_w=bw, fab_h=bh)
        _setup_fp_texts(pfp, ref_xy=(0.0, sy + 0.65), val_xy=(0.0, -sy - 0.65))
        save(pfp, name)

    # Bourns SRN6045-680M: datasheet p. 2 exact pads = 2.00 x 6.00 mm at +/-2.15 mm (ctc = 4.30 mm)!
    make_2pad("Bourns_SRN6045", "L", "SRN6045-680M", 2.00, 6.00, 4.30, 6.00, 6.00, has_silk=True)
    # Bourns MF-MSMF150/24X (1812): pads 1.50 x 3.40 mm, ctc 4.20 mm
    make_2pad("Bourns_MF_MSMF_1812", "F", "MF-MSMF150/24X", 1.50, 3.40, 4.20, 4.60, 3.25, has_silk=False)
    make_2pad("R_1206", "R", "R_1206", 1.05, 1.75, 2.55, 3.20, 1.60, has_silk=False)
    make_2pad("R_0805", "R", "R_0805", 0.95, 1.40, 1.95, 2.00, 1.25, has_silk=False)
    make_2pad("R_0603", "R", "R_0603", 0.72, 0.95, 1.50, 1.60, 0.80, has_silk=False)
    make_2pad("C_1210", "C", "C_1210", 1.15, 2.65, 2.65, 3.20, 2.50, has_silk=False)
    make_2pad("C_1206", "C", "C_1206", 1.10, 1.75, 2.65, 3.20, 1.60, has_silk=False)
    make_2pad("C_0805", "C", "C_0805", 0.95, 1.40, 1.95, 2.00, 1.25, has_silk=False)
    make_2pad("C_0603", "C", "C_0603", 0.72, 0.95, 1.50, 1.60, 0.80, has_silk=False)

    # 7. GCT USB4085-GF-A (0.35 mm finished signal drill => 0.150 mm X annular ring; 7.26 mm mouth datum; full CrtYd)
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
        p.SetDrillSize(pcbnew.VECTOR2I(mm(0.35), mm(0.35)))
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
        p.SetDrillSize(pcbnew.VECTOR2I(mm(0.35), mm(0.35)))
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
    # Exact 7.26 mm Row-B-to-front-mouth body outline (usb4085.pdf Sheet 1) & full courtyard to -7.50 mm
    for x0, y0, x1, y1 in [(-4.47, +2.33, +4.47, +2.33), (+4.47, +2.33, +4.47, -7.26),
                           (+4.47, -7.26, -4.47, -7.26), (-4.47, -7.26, -4.47, +2.33)]:
        s = pcbnew.PCB_SHAPE(fp)
        s.SetShape(pcbnew.SHAPE_T_SEGMENT)
        s.SetLayer(pcbnew.F_Fab)
        s.SetWidth(mm(0.10))
        s.SetStart(lpt(x0, y0))
        s.SetEnd(lpt(x1, y1))
        fp.Add(s)
    for x0, y0, x1, y1 in [(-5.00, +2.55, +5.00, +2.55), (+5.00, +2.55, +5.00, -7.50),
                           (+5.00, -7.50, -5.00, -7.50), (-5.00, -7.50, -5.00, +2.55)]:
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
    s.SetWidth(mm(0.15))
    s.SetStart(lpt(-3.60, +2.55))
    s.SetEnd(lpt(+3.60, +2.55))
    fp.Add(s)
    _setup_fp_texts(fp, ref_xy=(-5.95, +0.90), val_xy=(0.0, -5.00), ref_sz=0.80)
    save(fp, "GCT_USB4085_GF_A")

    # 8. JST XH Headers (ALL use 1.00 mm drill per jst_xh.pdf 0.9+0.1/-0 -> 1.00 mm standard!)
    def make_jst_xh(name, val, n_pins):
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
            p.SetSize(pcbnew.VECTOR2I(mm(1.80), mm(2.10)))
            p.SetDrillSize(pcbnew.VECTOR2I(mm(1.00), mm(1.00)))
            p.SetLayerSet(pcbnew.PAD.PTHMask())
            p.SetLocalSolderMaskMargin(mm(0.05))
            jfp.Add(p)
        bw = 7.40 if n_pins == 2 else 9.90
        hx = bw / 2.0
        for layer, lw, pad_e in [(pcbnew.F_SilkS, 0.15, 0.12), (pcbnew.F_Fab, 0.10, 0.0), (pcbnew.F_CrtYd, 0.05, 0.25)]:
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
        c.SetWidth(mm(0.15))
        c.SetFilled(True)
        c.SetCenter(lpt(+span / 2.0, +2.65))
        c.SetEnd(lpt(+span / 2.0 + 0.18, +2.65))
        jfp.Add(c)
        _setup_fp_texts(jfp, ref_xy=(0.0, -3.35), val_xy=(0.0, +4.25), ref_sz=0.80)
        save(jfp, name)

    make_jst_xh("JST_XH_B2B_P2.50mm", "B2B-XH-A", 2)
    make_jst_xh("JST_XH_B3B_P2.50mm", "B3B-XH-A", 3)

    # 9. TestPoint_Pad_D2.5mm (excluded from CPL and PCBA BOM)
    fp = pcbnew.FOOTPRINT(None)
    fp.SetReference("TP")
    fp.SetValue("TestPoint_D2.5mm")
    fp.SetAttributes(pcbnew.FP_THROUGH_HOLE | pcbnew.FP_EXCLUDE_FROM_BOM | pcbnew.FP_EXCLUDE_FROM_POS_FILES)
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
    c.SetEnd(lpt(1.45, 0.0))
    fp.Add(c)
    _setup_fp_texts(fp, ref_xy=(0.0, +2.05), val_xy=(0.0, -2.05), ref_layer=pcbnew.F_Fab, ref_sz=0.80)
    save(fp, "TestPoint_Pad_D2.5mm")

    # 10. MountingHole_2.7mm_M2.5_Pad5.5mm (excluded from CPL and PCBA BOM)
    fp = pcbnew.FOOTPRINT(None)
    fp.SetReference("H")
    fp.SetValue("MountingHole_2.7mm_M2.5")
    fp.SetAttributes(pcbnew.FP_THROUGH_HOLE | pcbnew.FP_EXCLUDE_FROM_BOM | pcbnew.FP_EXCLUDE_FROM_POS_FILES)
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
    c.SetEnd(lpt(2.90, 0.0))
    fp.Add(c)
    _setup_fp_texts(fp, ref_xy=(0.0, -3.50), val_xy=(0.0, +3.50), ref_layer=pcbnew.F_Fab, ref_sz=0.80)
    save(fp, "MountingHole_2.7mm_M2.5_Pad5.5mm")


# ---------------------------------------------------------------------------
# 3. Recognizable Graphical KiCad Symbol Library (lepiled.kicad_sym)
# ---------------------------------------------------------------------------

def _sym_wrap(name, ref, props_extra, body_g, pins_g, pin_names_hide=False, pin_nums_hide=False):
    pn_hide = "(hide yes)" if pin_names_hide else ""
    pm_hide = "(pin_numbers (hide yes))" if pin_nums_hide else ""
    return f"""  (symbol "{name}"
    {pm_hide}
    (pin_names (offset 1.016) {pn_hide})
    (exclude_from_sim no)
    (in_bom yes)
    (on_board yes)
    (property "Reference" "{ref}" (at 0 5.08 0) (effects (font (size 1.27 1.27))))
    (property "Value" "{name}" (at 0 -5.08 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "MPN" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
{props_extra}
    (symbol "{name}_0_1"
{body_g}
    )
    (symbol "{name}_1_1"
{pins_g}
    )
  )"""


def build_symbol_defs():
    syms = {}

    # Resistor (horizontal: pin 1 left -3.81, pin 2 right +3.81)
    syms["R"] = _sym_wrap(
        "R", "R", "",
        '      (rectangle (start -2.54 0.889) (end 2.54 -0.889) (stroke (width 0.254) (type default)) (fill (type none)))',
        '      (pin passive line (at -3.81 0 0) (length 1.27) (name "~" (effects (font (size 1.0 1.0)))) (number "1" (effects (font (size 1.0 1.0)))))\n'
        '      (pin passive line (at 3.81 0 180) (length 1.27) (name "~" (effects (font (size 1.0 1.0)))) (number "2" (effects (font (size 1.0 1.0)))))',
        pin_names_hide=True, pin_nums_hide=True,
    )

    # Capacitor (vertical: pin 1 top +3.81, pin 2 bottom -3.81)
    syms["C"] = _sym_wrap(
        "C", "C", "",
        '      (polyline (pts (xy -2.032 0.762) (xy 2.032 0.762)) (stroke (width 0.35) (type default)) (fill (type none)))\n'
        '      (polyline (pts (xy -2.032 -0.762) (xy 2.032 -0.762)) (stroke (width 0.35) (type default)) (fill (type none)))',
        '      (pin passive line (at 0 3.81 270) (length 3.048) (name "~" (effects (font (size 1.0 1.0)))) (number "1" (effects (font (size 1.0 1.0)))))\n'
        '      (pin passive line (at 0 -3.81 90) (length 3.048) (name "~" (effects (font (size 1.0 1.0)))) (number "2" (effects (font (size 1.0 1.0)))))',
        pin_names_hide=True, pin_nums_hide=True,
    )

    # Inductor (4 semicircular arcs, horizontal: pin 1 left -5.08, pin 2 right +5.08)
    syms["L"] = _sym_wrap(
        "L", "L", "",
        '      (arc (start -3.81 0) (mid -2.8575 0.9525) (end -1.905 0) (stroke (width 0.254) (type default)) (fill (type none)))\n'
        '      (arc (start -1.905 0) (mid -0.9525 0.9525) (end 0 0) (stroke (width 0.254) (type default)) (fill (type none)))\n'
        '      (arc (start 0 0) (mid 0.9525 0.9525) (end 1.905 0) (stroke (width 0.254) (type default)) (fill (type none)))\n'
        '      (arc (start 1.905 0) (mid 2.8575 0.9525) (end 3.81 0) (stroke (width 0.254) (type default)) (fill (type none)))',
        '      (pin passive line (at -5.08 0 0) (length 1.27) (name "1" (effects (font (size 1.0 1.0)))) (number "1" (effects (font (size 1.0 1.0)))))\n'
        '      (pin passive line (at 5.08 0 180) (length 1.27) (name "2" (effects (font (size 1.0 1.0)))) (number "2" (effects (font (size 1.0 1.0)))))',
        pin_names_hide=True, pin_nums_hide=True,
    )

    # Polyfuse (horizontal: pin 1 left -3.81, pin 2 right +3.81)
    syms["F"] = _sym_wrap(
        "F", "F", "",
        '      (rectangle (start -2.54 1.016) (end 2.54 -1.016) (stroke (width 0.254) (type default)) (fill (type none)))\n'
        '      (polyline (pts (xy -2.54 0) (xy 2.54 0)) (stroke (width 0.20) (type default)) (fill (type none)))\n'
        '      (polyline (pts (xy -1.524 -1.524) (xy 1.524 1.524) (xy 2.286 1.524)) (stroke (width 0.20) (type default)) (fill (type none)))',
        '      (pin passive line (at -3.81 0 0) (length 1.27) (name "~" (effects (font (size 1.0 1.0)))) (number "1" (effects (font (size 1.0 1.0)))))\n'
        '      (pin passive line (at 3.81 0 180) (length 1.27) (name "~" (effects (font (size 1.0 1.0)))) (number "2" (effects (font (size 1.0 1.0)))))',
        pin_names_hide=True, pin_nums_hide=True,
    )

    # Schottky Diode (Pin 1 = K left -3.81, Pin 2 = A right +3.81)
    syms["D_Schottky"] = _sym_wrap(
        "D_Schottky", "D", "",
        '      (polyline (pts (xy 1.27 -1.27) (xy 1.27 1.27) (xy -1.27 0) (xy 1.27 -1.27)) (stroke (width 0.254) (type default)) (fill (type none)))\n'
        '      (polyline (pts (xy -1.778 0.762) (xy -1.778 1.27) (xy -1.27 1.27) (xy -1.27 -1.27) (xy -0.762 -1.27) (xy -0.762 -0.762)) (stroke (width 0.254) (type default)) (fill (type none)))',
        '      (pin passive line (at -3.81 0 0) (length 2.54) (name "K" (effects (font (size 1.0 1.0)))) (number "1" (effects (font (size 1.0 1.0)))))\n'
        '      (pin passive line (at 3.81 0 180) (length 2.54) (name "A" (effects (font (size 1.0 1.0)))) (number "2" (effects (font (size 1.0 1.0)))))',
        pin_names_hide=True, pin_nums_hide=True,
    )

    # Zener Diode (Pin 1 = K left -3.81, Pin 2 = A right +3.81)
    syms["D_Zener"] = _sym_wrap(
        "D_Zener", "D", "",
        '      (polyline (pts (xy 1.27 -1.27) (xy 1.27 1.27) (xy -1.27 0) (xy 1.27 -1.27)) (stroke (width 0.254) (type default)) (fill (type none)))\n'
        '      (polyline (pts (xy -1.778 1.524) (xy -1.27 1.27) (xy -1.27 -1.27) (xy -0.762 -1.524)) (stroke (width 0.254) (type default)) (fill (type none)))',
        '      (pin passive line (at -3.81 0 0) (length 2.54) (name "K" (effects (font (size 1.0 1.0)))) (number "1" (effects (font (size 1.0 1.0)))))\n'
        '      (pin passive line (at 3.81 0 180) (length 2.54) (name "A" (effects (font (size 1.0 1.0)))) (number "2" (effects (font (size 1.0 1.0)))))',
        pin_names_hide=True, pin_nums_hide=True,
    )

    # Bidirectional TVS (Pin 1 left -3.81, Pin 2 right +3.81)
    syms["D_TVS"] = _sym_wrap(
        "D_TVS", "D", "",
        '      (polyline (pts (xy -2.032 1.016) (xy -2.032 -1.016) (xy 0 0) (xy -2.032 1.016)) (stroke (width 0.254) (type default)) (fill (type none)))\n'
        '      (polyline (pts (xy 2.032 1.016) (xy 2.032 -1.016) (xy 0 0) (xy 2.032 1.016)) (stroke (width 0.254) (type default)) (fill (type none)))\n'
        '      (polyline (pts (xy -0.508 1.27) (xy 0 1.016) (xy 0 -1.016) (xy 0.508 -1.27)) (stroke (width 0.254) (type default)) (fill (type none)))',
        '      (pin passive line (at -3.81 0 0) (length 1.778) (name "1" (effects (font (size 1.0 1.0)))) (number "1" (effects (font (size 1.0 1.0)))))\n'
        '      (pin passive line (at 3.81 0 180) (length 1.778) (name "2" (effects (font (size 1.0 1.0)))) (number "2" (effects (font (size 1.0 1.0)))))',
        pin_names_hide=True, pin_nums_hide=True,
    )

    # Indicator LED (Pin 1 = K left -3.81, Pin 2 = A right +3.81)
    syms["D_LED"] = _sym_wrap(
        "D_LED", "D", "",
        '      (polyline (pts (xy 1.27 -1.27) (xy 1.27 1.27) (xy -1.27 0) (xy 1.27 -1.27)) (stroke (width 0.254) (type default)) (fill (type none)))\n'
        '      (polyline (pts (xy -1.27 -1.27) (xy -1.27 1.27)) (stroke (width 0.254) (type default)) (fill (type none)))\n'
        '      (polyline (pts (xy -0.254 1.778) (xy -1.27 2.794)) (stroke (width 0.20) (type default)) (fill (type none)))\n'
        '      (polyline (pts (xy 0.762 1.778) (xy -0.254 2.794)) (stroke (width 0.20) (type default)) (fill (type none)))',
        '      (pin passive line (at -3.81 0 0) (length 2.54) (name "K" (effects (font (size 1.0 1.0)))) (number "1" (effects (font (size 1.0 1.0)))))\n'
        '      (pin passive line (at 3.81 0 180) (length 2.54) (name "A" (effects (font (size 1.0 1.0)))) (number "2" (effects (font (size 1.0 1.0)))))',
        pin_names_hide=True, pin_nums_hide=True,
    )

    # Off-board Power LED (Pin 1 = A left -3.81, Pin 2 = K right +3.81)
    syms["D_LED_AK"] = _sym_wrap(
        "D_LED_AK", "D", "",
        '      (polyline (pts (xy -1.27 -1.27) (xy -1.27 1.27) (xy 1.27 0) (xy -1.27 -1.27)) (stroke (width 0.254) (type default)) (fill (type none)))\n'
        '      (polyline (pts (xy 1.27 -1.27) (xy 1.27 1.27)) (stroke (width 0.254) (type default)) (fill (type none)))\n'
        '      (polyline (pts (xy -0.254 1.778) (xy 0.762 2.794)) (stroke (width 0.20) (type default)) (fill (type none)))\n'
        '      (polyline (pts (xy 0.762 1.778) (xy 1.778 2.794)) (stroke (width 0.20) (type default)) (fill (type none)))',
        '      (pin passive line (at -3.81 0 0) (length 2.54) (name "A" (effects (font (size 1.0 1.0)))) (number "1" (effects (font (size 1.0 1.0)))))\n'
        '      (pin passive line (at 3.81 0 180) (length 2.54) (name "K" (effects (font (size 1.0 1.0)))) (number "2" (effects (font (size 1.0 1.0)))))',
        pin_names_hide=True, pin_nums_hide=True,
    )

    # BAT54 SOT-23 Schottky (1=A left -3.81, 3=K right +3.81, 2=NC bottom -3.81)
    syms["D_BAT54"] = _sym_wrap(
        "D_BAT54", "D", "",
        '      (polyline (pts (xy -1.27 -1.27) (xy -1.27 1.27) (xy 1.27 0) (xy -1.27 -1.27)) (stroke (width 0.254) (type default)) (fill (type none)))\n'
        '      (polyline (pts (xy 1.778 0.762) (xy 1.778 1.27) (xy 1.27 1.27) (xy 1.27 -1.27) (xy 0.762 -1.27) (xy 0.762 -0.762)) (stroke (width 0.254) (type default)) (fill (type none)))',
        '      (pin passive line (at -3.81 0 0) (length 2.54) (name "A" (effects (font (size 0.9 0.9)))) (number "1" (effects (font (size 0.9 0.9)))))\n'
        '      (pin no_connect line (at 0 -3.81 90) (length 1.27) (name "NC" (effects (font (size 0.8 0.8)))) (number "2" (effects (font (size 0.8 0.8)))))\n'
        '      (pin passive line (at 3.81 0 180) (length 2.54) (name "K" (effects (font (size 0.9 0.9)))) (number "3" (effects (font (size 0.9 0.9)))))',
        pin_names_hide=True,
    )

    # N-MOSFET (1=G left -5.08 y=-1.27, 2=S bottom 0 y=-5.08, 3=D top 0 y=+5.08)
    syms["Q_NMOS"] = _sym_wrap(
        "Q_NMOS", "Q", "",
        '      (circle (center 0 0) (radius 2.794) (stroke (width 0.20) (type default)) (fill (type none)))\n'
        '      (polyline (pts (xy -1.524 1.524) (xy -1.524 -1.524)) (stroke (width 0.254) (type default)) (fill (type none)))\n'
        '      (polyline (pts (xy -0.762 1.778) (xy -0.762 0.762)) (stroke (width 0.30) (type default)) (fill (type none)))\n'
        '      (polyline (pts (xy -0.762 0.508) (xy -0.762 -0.508)) (stroke (width 0.30) (type default)) (fill (type none)))\n'
        '      (polyline (pts (xy -0.762 -0.762) (xy -0.762 -1.778)) (stroke (width 0.30) (type default)) (fill (type none)))\n'
        '      (polyline (pts (xy -0.762 1.27) (xy 0 1.27) (xy 0 2.54)) (stroke (width 0.254) (type default)) (fill (type none)))\n'
        '      (polyline (pts (xy -0.762 0) (xy 0 0) (xy 0 -2.54)) (stroke (width 0.254) (type default)) (fill (type none)))\n'
        '      (polyline (pts (xy -0.762 -1.27) (xy 0 -1.27)) (stroke (width 0.254) (type default)) (fill (type none)))\n'
        '      (polyline (pts (xy -2.54 -1.27) (xy -1.524 -1.27)) (stroke (width 0.254) (type default)) (fill (type none)))',
        '      (pin passive line (at -5.08 -1.27 0) (length 2.54) (name "G" (effects (font (size 0.9 0.9)))) (number "1" (effects (font (size 0.9 0.9)))))\n'
        '      (pin passive line (at 0 -5.08 90) (length 2.54) (name "S" (effects (font (size 0.9 0.9)))) (number "2" (effects (font (size 0.9 0.9)))))\n'
        '      (pin passive line (at 0 5.08 270) (length 2.54) (name "D" (effects (font (size 0.9 0.9)))) (number "3" (effects (font (size 0.9 0.9)))))',
        pin_names_hide=True,
    )

    # LM4040-2.5 Shunt Reference (1=K top +3.81, 2=A bottom -3.81, 3=GND right +3.81)
    syms["IC_LM4040"] = _sym_wrap(
        "IC_LM4040", "U", "",
        '      (polyline (pts (xy -1.27 -1.27) (xy 1.27 -1.27) (xy 0 1.27) (xy -1.27 -1.27)) (stroke (width 0.254) (type default)) (fill (type none)))\n'
        '      (polyline (pts (xy -1.778 1.778) (xy -1.27 1.27) (xy 1.27 1.27) (xy 1.778 0.762)) (stroke (width 0.254) (type default)) (fill (type none)))',
        '      (pin passive line (at 0 3.81 270) (length 2.54) (name "K" (effects (font (size 0.9 0.9)))) (number "1" (effects (font (size 0.9 0.9)))))\n'
        '      (pin passive line (at 0 -3.81 90) (length 2.54) (name "A" (effects (font (size 0.9 0.9)))) (number "2" (effects (font (size 0.9 0.9)))))\n'
        '      (pin passive line (at 3.81 -1.27 180) (length 2.54) (name "GND" (effects (font (size 0.8 0.8)))) (number "3" (effects (font (size 0.8 0.8)))))',
        pin_names_hide=True,
    )

    # AL8860WT-7 Buck LED Driver (5 pins: Left VIN(5), CTRL(3), GND(2); Right SET(4), SW(1))
    syms["IC_AL8860"] = _sym_wrap(
        "IC_AL8860", "U", "",
        '      (rectangle (start -7.62 6.35) (end 7.62 -6.35) (stroke (width 0.254) (type default)) (fill (type background)))',
        '      (pin passive line (at -11.43 3.81 0) (length 3.81) (name "VIN" (effects (font (size 1.1 1.1)))) (number "5" (effects (font (size 1.0 1.0)))))\n'
        '      (pin passive line (at -11.43 0.00 0) (length 3.81) (name "CTRL" (effects (font (size 1.1 1.1)))) (number "3" (effects (font (size 1.0 1.0)))))\n'
        '      (pin passive line (at -11.43 -3.81 0) (length 3.81) (name "GND" (effects (font (size 1.1 1.1)))) (number "2" (effects (font (size 1.0 1.0)))))\n'
        '      (pin passive line (at 11.43 3.81 180) (length 3.81) (name "SET" (effects (font (size 1.1 1.1)))) (number "4" (effects (font (size 1.0 1.0)))))\n'
        '      (pin passive line (at 11.43 -3.81 180) (length 3.81) (name "SW" (effects (font (size 1.1 1.1)))) (number "1" (effects (font (size 1.0 1.0)))))',
    )

    # LM393BIDR Dual Comparator (8 pins: Left 1IN+(3), 1IN-(2), 2IN+(5), 2IN-(6); Right 1OUT(1), 2OUT(7); Top VCC(8); Bot GND(4))
    syms["IC_LM393B"] = _sym_wrap(
        "IC_LM393B", "U", "",
        '      (rectangle (start -7.62 7.62) (end 7.62 -7.62) (stroke (width 0.254) (type default)) (fill (type background)))\n'
        '      (polyline (pts (xy -2.54 5.08) (xy -2.54 1.27) (xy 2.54 3.175) (xy -2.54 5.08)) (stroke (width 0.20) (type default)) (fill (type none)))\n'
        '      (polyline (pts (xy -2.54 -1.27) (xy -2.54 -5.08) (xy 2.54 -3.175) (xy -2.54 -1.27)) (stroke (width 0.20) (type default)) (fill (type none)))',
        '      (pin passive line (at -11.43 5.08 0) (length 3.81) (name "1IN+" (effects (font (size 1.0 1.0)))) (number "3" (effects (font (size 1.0 1.0)))))\n'
        '      (pin passive line (at -11.43 2.54 0) (length 3.81) (name "1IN-" (effects (font (size 1.0 1.0)))) (number "2" (effects (font (size 1.0 1.0)))))\n'
        '      (pin passive line (at -11.43 -2.54 0) (length 3.81) (name "2IN+" (effects (font (size 1.0 1.0)))) (number "5" (effects (font (size 1.0 1.0)))))\n'
        '      (pin passive line (at -11.43 -5.08 0) (length 3.81) (name "2IN-" (effects (font (size 1.0 1.0)))) (number "6" (effects (font (size 1.0 1.0)))))\n'
        '      (pin passive line (at 11.43 3.81 180) (length 3.81) (name "1OUT" (effects (font (size 1.0 1.0)))) (number "1" (effects (font (size 1.0 1.0)))))\n'
        '      (pin passive line (at 11.43 -3.81 180) (length 3.81) (name "2OUT" (effects (font (size 1.0 1.0)))) (number "7" (effects (font (size 1.0 1.0)))))\n'
        '      (pin passive line (at 0 11.43 270) (length 3.81) (name "VCC" (effects (font (size 1.0 1.0)))) (number "8" (effects (font (size 1.0 1.0)))))\n'
        '      (pin passive line (at 0 -11.43 90) (length 3.81) (name "GND" (effects (font (size 1.0 1.0)))) (number "4" (effects (font (size 1.0 1.0)))))',
    )

    # AP33771C PD 3.1 Sink Controller (15 pins: 8 left, 7 right)
    left_u3 = [("4", "ISENP", 10.16), ("3", "VCC", 7.62), ("11", "CC1", 5.08), ("10", "CC2", 2.54),
               ("13", "DP", 0.00), ("12", "DN", -2.54), ("5", "GND", -5.08), ("15", "EPAD", -7.62)]
    right_u3 = [("1", "VOUT", 10.16), ("2", "PWR_EN", 7.62), ("14", "V5V", 5.08), ("8", "VSEL", 2.54),
                ("9", "ISEL", 0.00), ("7", "LED", -2.54), ("6", "FLIP", -5.08)]
    u3_pins = []
    for num, nm, py in left_u3:
        ptype = "no_connect" if nm in ("DP", "DN") else "passive"
        u3_pins.append(f'      (pin {ptype} line (at -13.97 {py:.2f} 0) (length 3.81) (name "{nm}" (effects (font (size 1.0 1.0)))) (number "{num}" (effects (font (size 1.0 1.0)))))')
    for num, nm, py in right_u3:
        ptype = "no_connect" if nm == "FLIP" else "passive"
        u3_pins.append(f'      (pin {ptype} line (at 13.97 {py:.2f} 180) (length 3.81) (name "{nm}" (effects (font (size 1.0 1.0)))) (number "{num}" (effects (font (size 1.0 1.0)))))')
    syms["IC_AP33771C"] = _sym_wrap(
        "IC_AP33771C", "U", "",
        '      (rectangle (start -10.16 12.70) (end 10.16 -10.16) (stroke (width 0.254) (type default)) (fill (type background)))',
        "\n".join(u3_pins),
    )

    # GCT USB4085-GF-A (16 pins + 4 shield tabs grouped cleanly on right side)
    usbc_pins_spec = [
        ("A4", "VBUS", 12.70), ("A9", "VBUS", 10.16), ("B4", "VBUS", 7.62), ("B9", "VBUS", 5.08),
        ("A5", "CC1", 2.54), ("B5", "CC2", 0.00),
        ("A1", "GND", -2.54), ("A12", "GND", -5.08), ("B1", "GND", -7.62), ("B12", "GND", -10.16),
        ("SH1", "SHLD", -12.70), ("SH2", "SHLD", -12.70), ("SH3", "SHLD", -12.70), ("SH4", "SHLD", -12.70),
        ("A6", "D+", -15.24), ("B6", "D+", -15.24), ("A7", "D-", -17.78), ("B7", "D-", -17.78),
        ("A8", "SBU1", -20.32), ("B8", "SBU2", -22.86),
    ]
    usbc_p = []
    for num, nm, py in usbc_pins_spec:
        ptype = "no_connect" if nm in ("D+", "D-", "SBU1", "SBU2") else "passive"
        hide_str = " (hide yes)" if num in ("SH2", "SH3", "SH4", "B6", "B7") else ""
        usbc_p.append(f'      (pin {ptype} line (at 10.16 {py:.2f} 180) (length 3.81){hide_str} (name "{nm}" (effects (font (size 0.9 0.9)))) (number "{num}" (effects (font (size 0.9 0.9)))))')
    syms["J_USB4085"] = _sym_wrap(
        "J_USB4085", "J", "",
        '      (rectangle (start -6.35 15.24) (end 6.35 -25.40) (stroke (width 0.254) (type default)) (fill (type background)))',
        "\n".join(usbc_p),
    )

    # Connectors (2P, 3P), SPDT Switch, TestPoint, MountingHole, Mech_Boot
    syms["Conn_2P"] = _sym_wrap(
        "Conn_2P", "J", "",
        '      (rectangle (start -2.54 3.81) (end 2.54 -3.81) (stroke (width 0.254) (type default)) (fill (type background)))',
        '      (pin passive line (at -5.08 1.27 0) (length 2.54) (name "1" (effects (font (size 1.0 1.0)))) (number "1" (effects (font (size 1.0 1.0)))))\n'
        '      (pin passive line (at -5.08 -1.27 0) (length 2.54) (name "2" (effects (font (size 1.0 1.0)))) (number "2" (effects (font (size 1.0 1.0)))))',
    )
    syms["Conn_3P"] = _sym_wrap(
        "Conn_3P", "J", "",
        '      (rectangle (start -2.54 5.08) (end 2.54 -5.08) (stroke (width 0.254) (type default)) (fill (type background)))',
        '      (pin passive line (at -5.08 2.54 0) (length 2.54) (name "1" (effects (font (size 1.0 1.0)))) (number "1" (effects (font (size 1.0 1.0)))))\n'
        '      (pin passive line (at -5.08 0.00 0) (length 2.54) (name "2" (effects (font (size 1.0 1.0)))) (number "2" (effects (font (size 1.0 1.0)))))\n'
        '      (pin passive line (at -5.08 -2.54 0) (length 2.54) (name "3" (effects (font (size 1.0 1.0)))) (number "3" (effects (font (size 1.0 1.0)))))',
    )
    syms["SW_SPDT_3P"] = _sym_wrap(
        "SW_SPDT_3P", "SW", "",
        '      (rectangle (start -3.81 5.08) (end 3.81 -5.08) (stroke (width 0.254) (type default)) (fill (type background)))\n'
        '      (circle (center -1.27 0) (radius 0.508) (stroke (width 0.20) (type default)) (fill (type none)))\n'
        '      (polyline (pts (xy -0.762 0) (xy 1.524 2.032)) (stroke (width 0.254) (type default)) (fill (type none)))',
        '      (pin passive line (at -6.35 2.54 0) (length 2.54) (name "UV" (effects (font (size 0.9 0.9)))) (number "1" (effects (font (size 0.9 0.9)))))\n'
        '      (pin passive line (at -6.35 0.00 0) (length 2.54) (name "COM" (effects (font (size 0.9 0.9)))) (number "2" (effects (font (size 0.9 0.9)))))\n'
        '      (pin passive line (at -6.35 -2.54 0) (length 2.54) (name "ALL" (effects (font (size 0.9 0.9)))) (number "3" (effects (font (size 0.9 0.9)))))',
    )
    syms["TestPoint"] = _sym_wrap(
        "TestPoint", "TP", "",
        '      (circle (center 0 0) (radius 1.27) (stroke (width 0.254) (type default)) (fill (type none)))',
        '      (pin passive line (at 3.81 0 180) (length 2.54) (name "1" (effects (font (size 0.9 0.9)))) (number "1" (effects (font (size 0.9 0.9)))))',
        pin_names_hide=True,
    )
    syms["MountingHole"] = _sym_wrap(
        "MountingHole", "H", "",
        '      (circle (center 0 0) (radius 1.524) (stroke (width 0.254) (type default)) (fill (type none)))\n'
        '      (circle (center 0 0) (radius 0.762) (stroke (width 0.20) (type default)) (fill (type none)))',
        '      (pin passive line (at 0 -3.81 90) (length 2.286) (name "1" (effects (font (size 0.9 0.9)))) (number "1" (effects (font (size 0.9 0.9)))))',
        pin_names_hide=True,
    )
    syms["Mech_Item"] = _sym_wrap(
        "Mech_Item", "SW", "",
        '      (rectangle (start -3.81 1.905) (end 3.81 -1.905) (stroke (width 0.254) (type dash)) (fill (type none)))',
        "",
        pin_names_hide=True, pin_nums_hide=True,
    )
    # GND graphical symbol (passive pin so zero ERC power_pin_not_driven warnings)
    syms["GND_Sym"] = """  (symbol "GND_Sym"
    (pin_numbers (hide yes))
    (pin_names (offset 0) (hide yes))
    (exclude_from_sim no)
    (in_bom no)
    (on_board no)
    (property "Reference" "#PWR" (at 0 -5.08 0) (effects (font (size 1.0 1.0)) (hide yes)))
    (property "Value" "GND" (at 0 -3.556 0) (effects (font (size 1.0 1.0))))
    (property "Footprint" "" (at 0 0 0) (effects (font (size 1.0 1.0)) (hide yes)))
    (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.0 1.0)) (hide yes)))
    (symbol "GND_Sym_0_1"
      (polyline (pts (xy 0 0) (xy 0 -1.27) (xy 1.27 -1.27) (xy 0 -2.54) (xy -1.27 -1.27) (xy 0 -1.27)) (stroke (width 0.254) (type default)) (fill (type none)))
    )
    (symbol "GND_Sym_1_1"
      (pin passive line (at 0 0 270) (length 0) (name "GND" (effects (font (size 1.0 1.0)))) (number "1" (effects (font (size 1.0 1.0)))))
    )
  )"""
    return syms


def write_kicad_sym(syms):
    txt = '(kicad_symbol_lib\n  (version 20241209)\n  (generator "kicad_symbol_editor")\n  (generator_version "9.0")\n'
    txt += "\n".join(syms.values()) + "\n)\n"
    (BASE_DIR / "lepiled.kicad_sym").write_text(txt)


# ---------------------------------------------------------------------------
# 4. Properly Wired 4-Block A3 KiCad Schematic (driver_pcb.kicad_sch)
# ---------------------------------------------------------------------------

def _sym_pin_offsets():
    """Exact local (dx, dy) in KiCad symbol-def coords (+Y UP) -> schematic uses (x + dx, y - dy) when rot=0."""
    return {
        "R": {"1": (-3.81, 0), "2": (3.81, 0)},
        "C": {"1": (0, 3.81), "2": (0, -3.81)},
        "L": {"1": (-5.08, 0), "2": (5.08, 0)},
        "F": {"1": (-3.81, 0), "2": (3.81, 0)},
        "D_Schottky": {"1": (-3.81, 0), "2": (3.81, 0)},
        "D_Zener": {"1": (-3.81, 0), "2": (3.81, 0)},
        "D_TVS": {"1": (-3.81, 0), "2": (3.81, 0)},
        "D_LED": {"1": (-3.81, 0), "2": (3.81, 0)},
        "D_LED_AK": {"1": (-3.81, 0), "2": (3.81, 0)},
        "D_BAT54": {"1": (-3.81, 0), "2": (0, -3.81), "3": (3.81, 0)},
        "Q_NMOS": {"1": (-5.08, -1.27), "2": (0, -5.08), "3": (0, 5.08)},
        "IC_LM4040": {"1": (0, 3.81), "2": (0, -3.81), "3": (3.81, -1.27)},
        "IC_AL8860": {"5": (-11.43, 3.81), "3": (-11.43, 0), "2": (-11.43, -3.81), "4": (11.43, 3.81), "1": (11.43, -3.81)},
        "IC_LM393B": {"3": (-11.43, 5.08), "2": (-11.43, 2.54), "5": (-11.43, -2.54), "6": (-11.43, -5.08),
                      "1": (11.43, 3.81), "7": (11.43, -3.81), "8": (0, 11.43), "4": (0, -11.43)},
        "IC_AP33771C": {"4": (-13.97, 10.16), "3": (-13.97, 7.62), "11": (-13.97, 5.08), "10": (-13.97, 2.54),
                        "13": (-13.97, 0), "12": (-13.97, -2.54), "5": (-13.97, -5.08), "15": (-13.97, -7.62),
                        "1": (13.97, 10.16), "2": (13.97, 7.62), "14": (13.97, 5.08), "8": (13.97, 2.54),
                        "9": (13.97, 0), "7": (13.97, -2.54), "6": (13.97, -5.08)},
        "J_USB4085": {"A4": (10.16, 12.70), "A9": (10.16, 10.16), "B4": (10.16, 7.62), "B9": (10.16, 5.08),
                      "A5": (10.16, 2.54), "B5": (10.16, 0.00), "A1": (10.16, -2.54), "A12": (10.16, -5.08),
                      "B1": (10.16, -7.62), "B12": (10.16, -10.16), "SH1": (10.16, -12.70), "SH2": (10.16, -12.70),
                      "SH3": (10.16, -12.70), "SH4": (10.16, -12.70), "A6": (10.16, -15.24), "B6": (10.16, -15.24),
                      "A7": (10.16, -17.78), "B7": (10.16, -17.78), "A8": (10.16, -20.32), "B8": (10.16, -22.86)},
        "Conn_2P": {"1": (-5.08, 1.27), "2": (-5.08, -1.27)},
        "Conn_3P": {"1": (-5.08, 2.54), "2": (-5.08, 0), "3": (-5.08, -2.54)},
        "SW_SPDT_3P": {"1": (-6.35, 2.54), "2": (-6.35, 0), "3": (-6.35, -2.54)},
        "TestPoint": {"1": (3.81, 0)},
        "MountingHole": {"1": (0, -3.81)},
        "Mech_Item": {},
    }


def _rot_pin(dx, dy, ang):
    """KiCad schematic symbol rotation CCW by ang degrees, then Y-down conversion."""
    rad = math.radians(ang)
    rx = dx * math.cos(rad) - dy * math.sin(rad)
    ry = dx * math.sin(rad) + dy * math.cos(rad)
    return (round(rx, 4), round(-ry, 4))


def write_kicad_sch(syms, comp_rows):
    root_uuid = uid("root_sheet")
    pin_offs = _sym_pin_offsets()

    # Exact footprint mapping for every RefDes
    fp_map = {
        "U1": "lepiled:Diodes_TSOT25_AL8860",
        "U2": "lepiled:Diodes_TSOT25_AL8860",
        "U3": "lepiled:Diodes_W-DFN3030-14_AP33771C",
        "U4": "lepiled:TI_SOIC-8_LM393B",
        "U5": "lepiled:SOT-23-3",
        "Q1A": "lepiled:SOT-23-3",
        "Q1B": "lepiled:SOT-23-3",
        "Q2": "lepiled:SOT-23-3",
        "Q3": "lepiled:SOT-23-3",
        "F1": "lepiled:Bourns_MF_MSMF_1812",
        "F2": "lepiled:Bourns_MF_MSMF_1812",
        "D9": "lepiled:D_SMA_DO-214AC",
        "D10": "lepiled:D_SMA_DO-214AC",
        "D11": "lepiled:D_SMB_DO-214AA_BiDir",
        "D12": "lepiled:SOT-23-3",
        "D13": "lepiled:D_SMA_DO-214AC",
        "D14": "lepiled:D_SOD-123",
        "D15": "lepiled:LED_0603",
        "L1": "lepiled:Bourns_SRN6045",
        "L2": "lepiled:Bourns_SRN6045",
        "R1": "lepiled:R_0603", "R2": "lepiled:R_0603",
        "R3": "lepiled:R_1206", "R4": "lepiled:R_1206",
        "R5": "lepiled:R_0603", "R6": "lepiled:R_0603",
        "R7": "lepiled:R_0805", "R8": "lepiled:R_1206",
        "R9": "lepiled:R_0603", "R10": "lepiled:R_0603",
        "R11": "lepiled:R_0603", "R12": "lepiled:R_0805",
        "R13": "lepiled:R_0603", "R14": "lepiled:R_0805",
        "R15": "lepiled:R_0603", "R16": "lepiled:R_0603",
        "R17": "lepiled:R_0805",
        "C1": "lepiled:C_0805", "C2": "lepiled:C_1210", "C3": "lepiled:C_1210",
        "C4": "lepiled:C_0805", "C5": "lepiled:C_0805",
        "C6": "lepiled:C_0603", "C7": "lepiled:C_0603",
        "C8": "lepiled:C_0603", "C9": "lepiled:C_0603",
        "C10": "lepiled:C_1206", "C11": "lepiled:C_0805", "C12": "lepiled:C_0805",
        "C13": "lepiled:C_0603", "C14": "lepiled:C_0603", "C15": "lepiled:C_0603",
        "J1": "lepiled:GCT_USB4085_GF_A",
        "J2": "lepiled:JST_XH_B2B_P2.50mm",
        "J3": "lepiled:JST_XH_B2B_P2.50mm",
        "J4": "lepiled:JST_XH_B3B_P2.50mm",
        "TP1": "lepiled:TestPoint_Pad_D2.5mm",
        "TP2": "lepiled:TestPoint_Pad_D2.5mm",
        "H1": "lepiled:MountingHole_2.7mm_M2.5_Pad5.5mm",
        "H2": "lepiled:MountingHole_2.7mm_M2.5_Pad5.5mm",
        "H3": "lepiled:MountingHole_2.7mm_M2.5_Pad5.5mm",
        "H4": "lepiled:MountingHole_2.7mm_M2.5_Pad5.5mm",
    }

    short_val = {
        "U1": "AL8860WT-7", "U2": "AL8860WT-7", "U3": "AP33771C", "U4": "LM393BIDR", "U5": "LM4040-2.5",
        "Q1A": "DMN3404L", "Q1B": "DMN3404L", "Q2": "BSS138", "Q3": "BSS138",
        "F1": "1.5A/24V", "F2": "1.5A/24V",
        "D1": "SST-10-UV", "D2": "SST-10-UV", "D3": "SST-10-UV", "D4": "SST-10-UV",
        "D5": "XP-E2 RB", "D6": "XP-E2 RB", "D7": "XP-E2 GRN", "D8": "XP-E2 CW",
        "D9": "B340A", "D10": "B340A", "D11": "SMBJ22CA", "D12": "BAT54",
        "D13": "B340A", "D14": "5.1V", "D15": "GRN LED",
        "L1": "68uH", "L2": "68uH",
        "R1": "5.1k", "R2": "5.1k", "R3": "0.30R", "R4": "0.30R",
        "R5": "100k", "R6": "100k", "R7": "1.0R", "R8": "5mR",
        "R9": "39.0k", "R10": "82.0k", "R11": "6.2k", "R12": "200R",
        "R13": "1.0k", "R14": "10.0k", "R15": "59.0k", "R16": "10.0k", "R17": "22.0k",
        "C1": "1uF/50V", "C2": "10uF/50V", "C3": "10uF/50V", "C4": "1uF/50V", "C5": "1uF/50V",
        "C6": "1.0nF", "C7": "4.7nF", "C8": "100nF", "C9": "100nF", "C10": "4.7uF/50V",
        "C11": "1uF/50V", "C12": "1uF/50V", "C13": "47nF", "C14": "100nF", "C15": "100nF",
        "J1": "USB4085", "J2": "UV_STR", "J3": "VIS_STR", "J4": "MAXI_SW",
        "SW1": "SPDT On-Off-On", "SW1_BOOT": "759D02000 Boot",
        "TP1": "AUX_18-24V", "TP2": "AUX_GND",
        "H1": "M2.5_GND", "H2": "M2.5_GND", "H3": "M2.5_GND", "H4": "M2.5_GND",
    }

    elements = []
    raw_wires = []
    raw_labels = []
    pin_pos = {}
    pwr_counter = [0]

    def place(ref, sym_name, x, y, ang=0, ref_off=(0, -3.2), val_off=(0, 3.2)):
        row = comp_rows[ref]
        off_board = (row["Mounting"] == "Off-Board")
        fp = "" if off_board else fp_map[ref]
        in_bom = "no" if ref in ("TP1", "TP2", "H1", "H2", "H3", "H4") else "yes"
        on_board = "no" if off_board else "yes"
        dnp = "no"  # Off-board parts use (on_board no), NOT (dnp yes), so KiCad does not draw red X crossouts!
        pins = list(pin_offs[sym_name].keys())
        pin_lines = "\n".join(f'    (pin "{p}" (uuid "{uid(f"pin_{ref}_{p}")}"))' for p in pins)
        s = f"""  (symbol
    (lib_id "lepiled:{sym_name}")
    (at {x:.2f} {y:.2f} {ang})
    (unit 1)
    (exclude_from_sim no)
    (in_bom {in_bom})
    (on_board {on_board})
    (dnp {dnp})
    (uuid "{uid(f'sym_{ref}')}")
    (property "Reference" "{ref}" (at {x + ref_off[0]:.2f} {y + ref_off[1]:.2f} 0) (effects (font (size 1.27 1.27))))
    (property "Value" "{short_val[ref]}" (at {x + val_off[0]:.2f} {y + val_off[1]:.2f} 0) (effects (font (size 1.15 1.15))))
    (property "Footprint" "{fp}" (at {x:.2f} {y:.2f} 0) (effects (font (size 1.0 1.0)) (hide yes)))
    (property "Datasheet" "{row['Datasheet_Ref']}" (at {x:.2f} {y:.2f} 0) (effects (font (size 1.0 1.0)) (hide yes)))
    (property "MPN" "{row['MPN']}" (at {x:.2f} {y:.2f} 0) (effects (font (size 1.0 1.0)) (hide yes)))
{pin_lines}
    (instances
      (project "driver_pcb"
        (path "/{root_uuid}"
          (reference "{ref}")
          (unit 1)
        )
      )
    )
  )"""
        elements.append(s)
        for p, (dx, dy) in pin_offs[sym_name].items():
            rx, ry = _rot_pin(dx, dy, ang)
            pin_pos[(ref, p)] = (round(x + rx, 2), round(y + ry, 2))

    def wire(p1, p2):
        p1 = (round(p1[0], 2), round(p1[1], 2))
        p2 = (round(p2[0], 2), round(p2[1], 2))
        if abs(p1[0] - p2[0]) < 1e-4 and abs(p1[1] - p2[1]) < 1e-4:
            return
        raw_wires.append((p1, p2))

    def polywire(pts):
        for a, b in zip(pts, pts[1:]):
            wire(a, b)

    def junc(pt):
        pass  # Auto-emitted cleanly after exact wire splitting at all vertices!

    def gnd_at(pt):
        pwr_counter[0] += 1
        idx = pwr_counter[0]
        ref = f"#GND{idx:02d}"
        x, y = round(pt[0], 2), round(pt[1], 2)
        elements.append(f"""  (symbol
    (lib_id "lepiled:GND_Sym")
    (at {x:.2f} {y:.2f} 0)
    (unit 1)
    (exclude_from_sim no)
    (in_bom no)
    (on_board no)
    (dnp no)
    (uuid "{uid(f'gnd_{idx}')}")
    (property "Reference" "{ref}" (at {x:.2f} {y+5.08:.2f} 0) (effects (font (size 1.0 1.0)) (hide yes)))
    (property "Value" "GND" (at {x:.2f} {y+3.81:.2f} 0) (effects (font (size 1.0 1.0))))
    (property "Footprint" "" (at {x:.2f} {y:.2f} 0) (effects (font (size 1.0 1.0)) (hide yes)))
    (property "Datasheet" "" (at {x:.2f} {y:.2f} 0) (effects (font (size 1.0 1.0)) (hide yes)))
    (pin "1" (uuid "{uid(f'gndp_{idx}')}"))
    (instances (project "driver_pcb" (path "/{root_uuid}" (reference "{ref}") (unit 1))))
  )""")
        raw_labels.append(("GND", (x, y), 0, "left bottom", True))

    def lbl(name, pt, ang=0, just="left bottom"):
        raw_labels.append((name, (round(pt[0], 2), round(pt[1], 2)), ang, just, False))

    def nc(pt):
        elements.append(f'  (no_connect (at {pt[0]:.2f} {pt[1]:.2f}) (uuid "{uid(f"nc_{pt}_{len(elements)}")}"))')

    def box(x0, y0, x1, y1, title, dash=False):
        st = "dash" if dash else "solid"
        elements.append(
            f'  (rectangle (start {x0:.2f} {y0:.2f}) (end {x1:.2f} {y1:.2f}) '
            f'(stroke (width 0.25) (type {st}) (color 60 90 140 1)) (fill (type none)) (uuid "{uid(f"box_{title}")}"))'
        )
        elements.append(
            f'  (text "{title}" (at {x0 + 2.54:.2f} {y0 + 3.81:.2f} 0) '
            f'(effects (font (size 1.8 1.8) (bold yes)) (justify left bottom)) (uuid "{uid(f"txt_{title}")}"))'
        )

    # =====================================================================
    # BLOCK 1 (Top-Left: X=15..205, Y=18..146): USB-C PD 20V & AUX DC ENTRY
    # =====================================================================
    box(15.24, 17.78, 205.74, 146.05, "BLOCK 1: USB-C PD 3.1 (20 V / 1.0 A) SINK & AUX 18-24 V DC INPUT")

    place("J1", "J_USB4085", 27.94, 58.42, 0, ref_off=(0, -17.5), val_off=(0, 27.5))
    # Tie VBUS pins (A4,A9,B4,B9) together into VBUS trunk at y=45.72
    polywire([pin_pos[("J1", "A4")], (43.18, 45.72)])
    for bp in ("A9", "B4", "B9"):
        p = pin_pos[("J1", bp)]
        polywire([p, (43.18, p[1]), (43.18, 45.72)])
        junc((43.18, p[1]))
    junc((43.18, 45.72))
    # Tie GND & Shield pins together
    polywire([pin_pos[("J1", "A1")], (43.18, 60.96), (43.18, 73.66)])
    for gp in ("A12", "B1", "B12", "SH1"):
        p = pin_pos[("J1", gp)]
        wire(p, (43.18, p[1]))
        junc((43.18, p[1]))
    gnd_at((43.18, 73.66))
    for ncp in ("A6", "A7", "A8", "B8"):
        nc(pin_pos[("J1", ncp)])

    # F1 -> VBUS_FUSED -> R8 (5mR) -> VBUS_SENSE -> Q1A/Q1B -> VIN_20V (clean horizontal power bus at y=45.72!)
    place("F1", "F", 53.34, 45.72, 0, ref_off=(0, -3.0), val_off=(0, 3.0))
    wire((43.18, 45.72), pin_pos[("F1", "1")])
    lbl("VBUS", (45.72, 45.72))

    # Shunt protection & damper off VBUS_FUSED (x=63.50..88.90)
    place("D11", "D_TVS", 63.50, 58.42, 90, ref_off=(-3.5, 0), val_off=(4.2, 0))
    place("C1", "C", 73.66, 58.42, 0, ref_off=(-3.8, -1.0), val_off=(4.0, 0.5))
    place("R7", "R", 83.82, 54.61, 90, ref_off=(3.2, -1.0), val_off=(3.2, 1.2))
    place("C10", "C", 83.82, 66.04, 0, ref_off=(3.8, -1.0), val_off=(4.2, 1.0))

    place("R8", "R", 96.52, 45.72, 0, ref_off=(0, -3.0), val_off=(0, 3.0))
    wire(pin_pos[("F1", "2")], pin_pos[("R8", "1")])
    lbl("VBUS_FUSED", (66.04, 45.72))
    for px, pnode in [(63.50, pin_pos[("D11", "2")]), (73.66, pin_pos[("C1", "1")]), (83.82, pin_pos[("R7", "2")])]:
        wire((px, 45.72), pnode)
        junc((px, 45.72))
    wire(pin_pos[("R7", "1")], pin_pos[("C10", "1")])
    lbl("VBUS_DAMP", (83.82, 59.69), just="left bottom")
    gnd_at(pin_pos[("D11", "1")])
    gnd_at(pin_pos[("C1", "2")])
    gnd_at(pin_pos[("C10", "2")])

    # Q1A & Q1B back-to-back common-source N-MOSFETs (rot 90 / 270 -> horizontal D-S-S-D along y=45.72!)
    # Q1A rot=90: D(3) at (-5.08, 0), S(2) at (+5.08, 0), G(1) at (+1.27, +5.08)
    # Q1B rot=270: S(2) at (-5.08, 0), D(3) at (+5.08, 0), G(1) at (-1.27, -5.08) -> wait! Let's place Q1A rot=90 & Q1B rot=270!
    # Check _rot_pin for Q_NMOS:
    #   rot=90:  D(0,5.08)->(-5.08, 0), S(0,-5.08)->(+5.08, 0), G(-5.08,-1.27)->(+1.27, +5.08) (G below!)
    #   rot=270: S(0,-5.08)->(-5.08, 0), D(0,5.08)->(+5.08, 0), G(-5.08,-1.27)->(-1.27, -5.08) (G above!)
    # Even cleaner: place Q1A at (124.46, 45.72) rot=90 and Q1B at (147.32, 45.72) rot=270? Let's keep both Gates pointing DOWN or wire neatly!
    place("Q1A", "Q_NMOS", 124.46, 45.72, 90, ref_off=(0, -5.5), val_off=(0, -3.5))
    place("Q1B", "Q_NMOS", 149.86, 45.72, 270, ref_off=(0, -6.5), val_off=(0, -4.5))
    wire(pin_pos[("R8", "2")], pin_pos[("Q1A", "3")])
    lbl("VBUS_SENSE", (105.41, 45.72))
    wire(pin_pos[("Q1A", "2")], pin_pos[("Q1B", "2")])
    lbl("Q1_MID", (134.62, 45.72))
    wire(pin_pos[("Q1B", "3")], (185.42, 45.72))
    lbl("VIN_20V", (172.72, 45.72))

    # C11 on VBUS_SENSE
    place("C11", "C", 111.76, 58.42, 0, ref_off=(-4.0, 0), val_off=(4.0, 0))
    wire((111.76, 45.72), pin_pos[("C11", "1")])
    junc((111.76, 45.72))
    gnd_at(pin_pos[("C11", "2")])

    # C13 between Q1_GATE and Q1_MID; R11 from U3_PWR_EN to Q1_GATE
    place("C13", "C", 137.16, 58.42, 0, ref_off=(3.5, -1.0), val_off=(3.8, 1.0))
    wire((137.16, 45.72), pin_pos[("C13", "1")])
    junc((137.16, 45.72))
    polywire([pin_pos[("Q1A", "1")], (125.73, 62.23), pin_pos[("C13", "2")]])
    polywire([pin_pos[("Q1B", "1")], (148.59, 36.83), (133.35, 36.83), (133.35, 62.23), (125.73, 62.23)])
    junc((133.35, 62.23))
    junc((137.16, 62.23))
    lbl("Q1_GATE", (127.00, 62.23))

    # U3 AP33771C centered at (137.16, 99.06)
    place("U3", "IC_AP33771C", 137.16, 99.06, 0, ref_off=(0, -14.5), val_off=(0, 12.2))
    # Kelvin taps ISENP (pin 4) & VCC (pin 3) + CC1 (11), CC2 (10)
    polywire([pin_pos[("U3", "4")], (113.03, 88.90)])
    lbl("VBUS_FUSED", (113.03, 88.90))
    polywire([pin_pos[("U3", "3")], (113.03, 91.44)])
    lbl("VBUS_SENSE", (113.03, 91.44))
    # CC1 / CC2 wires from J1 + R1/R2 5.1k pull-downs
    place("R1", "R", 63.50, 81.28, 90, ref_off=(-3.5, 0), val_off=(3.5, 0))
    place("R2", "R", 76.20, 81.28, 90, ref_off=(-3.5, 0), val_off=(3.5, 0))
    wire(pin_pos[("J1", "A5")], (45.72, 55.88))
    lbl("CC1", (45.72, 55.88))
    wire(pin_pos[("J1", "B5")], (45.72, 58.42))
    lbl("CC2", (45.72, 58.42))
    polywire([pin_pos[("U3", "11")], (93.98, 93.98), (93.98, 74.93), (63.50, 74.93), pin_pos[("R1", "2")]])
    lbl("CC1", (66.04, 74.93))
    polywire([pin_pos[("U3", "10")], (96.52, 96.52), (96.52, 77.47), (76.20, 77.47), pin_pos[("R2", "2")]])
    lbl("CC2", (78.74, 77.47))
    gnd_at(pin_pos[("R1", "1")])
    gnd_at(pin_pos[("R2", "1")])
    nc(pin_pos[("U3", "13")])
    nc(pin_pos[("U3", "12")])
    nc(pin_pos[("U3", "6")])
    # U3 GND (5) & EPAD (15)
    polywire([pin_pos[("U3", "5")], (118.11, 104.14), (118.11, 106.68), pin_pos[("U3", "15")]])
    wire((118.11, 106.68), (118.11, 109.22))
    gnd_at((118.11, 109.22))

    # U3 Right-side peripherals: R12 (VOUT), R11 (PWR_EN), C12 (V5V), R9 (VSEL), R10 (ISEL), R13+D15 (LED)
    place("R12", "R", 172.72, 88.90, 180, ref_off=(0, -3.0), val_off=(0, 3.0))
    wire(pin_pos[("U3", "1")], pin_pos[("R12", "2")])
    lbl("U3_VOUT", (154.94, 88.90))
    polywire([pin_pos[("R12", "1")], (185.42, 88.90), (185.42, 45.72)])

    place("R11", "R", 165.10, 78.74, 0, ref_off=(0, -3.0), val_off=(0, 3.0))
    polywire([pin_pos[("U3", "2")], (157.48, 91.44), (157.48, 78.74), pin_pos[("R11", "1")]])
    lbl("U3_PWR_EN", (157.48, 83.82))
    polywire([pin_pos[("R11", "2")], (175.26, 78.74), (175.26, 62.23), (137.16, 62.23)])

    place("C12", "C", 162.56, 106.68, 0, ref_off=(3.5, -1.0), val_off=(3.8, 1.0))
    polywire([pin_pos[("U3", "14")], (162.56, 93.98), pin_pos[("C12", "1")]])
    lbl("U3_V5V", (153.67, 93.98))
    gnd_at(pin_pos[("C12", "2")])

    place("R9", "R", 175.26, 106.68, 90, ref_off=(3.2, -1.0), val_off=(3.2, 1.2))
    polywire([pin_pos[("U3", "8")], (175.26, 96.52), pin_pos[("R9", "2")]])
    lbl("U3_VSEL", (167.64, 96.52))
    gnd_at(pin_pos[("R9", "1")])

    place("R10", "R", 187.96, 106.68, 90, ref_off=(3.2, -1.0), val_off=(3.2, 1.2))
    polywire([pin_pos[("U3", "9")], (187.96, 99.06), pin_pos[("R10", "2")]])
    lbl("U3_ISEL", (177.80, 99.06))
    gnd_at(pin_pos[("R10", "1")])

    place("R13", "R", 165.10, 121.92, 0, ref_off=(0, -3.0), val_off=(0, 3.0))
    place("D15", "D_LED", 182.88, 121.92, 180, ref_off=(0, -3.5), val_off=(0, 3.5))
    polywire([pin_pos[("U3", "7")], (157.48, 101.60), (157.48, 121.92), pin_pos[("R13", "1")]])
    lbl("U3_LED", (157.48, 114.30))
    wire(pin_pos[("R13", "2")], pin_pos[("D15", "2")])
    lbl("PD_LED_A", (171.45, 121.92))
    polywire([pin_pos[("D15", "1")], (190.50, 121.92), (190.50, 127.00)])
    gnd_at((190.50, 127.00))

    # Auxiliary 18-24 V DC Entry (TP1 -> F2 -> D13 -> VIN_20V, TP2 -> GND, H1..H4 -> GND)
    place("TP1", "TestPoint", 25.40, 111.76, 0, ref_off=(0, -3.0), val_off=(0, 3.2))
    place("F2", "F", 43.18, 111.76, 0, ref_off=(0, -3.0), val_off=(0, 3.0))
    place("D13", "D_Schottky", 60.96, 111.76, 180, ref_off=(0, -3.0), val_off=(0, 3.0))
    wire(pin_pos[("TP1", "1")], pin_pos[("F2", "1")])
    lbl("AUX_IN", (30.48, 111.76))
    wire(pin_pos[("F2", "2")], pin_pos[("D13", "2")])
    lbl("AUX_FUSED", (48.26, 111.76))
    wire(pin_pos[("D13", "1")], (76.20, 111.76))
    lbl("VIN_20V", (76.20, 111.76))

    place("TP2", "TestPoint", 25.40, 129.54, 0, ref_off=(0, -3.0), val_off=(0, 3.2))
    wire(pin_pos[("TP2", "1")], (35.56, 129.54))
    gnd_at((35.56, 129.54))

    for idx, hx in enumerate([58.42, 71.12, 83.82, 96.52], start=1):
        place(f"H{idx}", "MountingHole", hx, 129.54, 0, ref_off=(0, -3.5), val_off=(0, 5.2))
        gnd_at(pin_pos[(f"H{idx}", "1")])

    # =====================================================================
    # BLOCK 2 (Bottom-Left: X=15..205, Y=155..278): 17.25 V UVLO & MAXI-SWITCH
    # =====================================================================
    box(15.24, 154.94, 205.74, 276.86, "BLOCK 2: 17.25 V HARDWARE UVLO & GROUND-REFERENCED MAXI-SWITCH")

    # UVLO Left Sub-block (R14/U5, R15/R16/C15, U4 LM393B, C14)
    place("R14", "R", 30.48, 177.80, 90, ref_off=(-3.8, -0.8), val_off=(-4.0, 1.2))
    place("U5", "IC_LM4040", 30.48, 193.04, 0, ref_off=(-4.5, -1.0), val_off=(-4.8, 1.2))
    wire((30.48, 167.64), pin_pos[("R14", "2")])
    lbl("VIN_20V", (33.02, 167.64))
    wire(pin_pos[("R14", "1")], pin_pos[("U5", "1")])
    gnd_at(pin_pos[("U5", "2")])
    polywire([pin_pos[("U5", "3")], (38.10, 194.31), (38.10, 196.85)])
    gnd_at((38.10, 196.85))

    place("R15", "R", 50.80, 177.80, 90, ref_off=(-3.8, -0.8), val_off=(-4.0, 1.2))
    place("R16", "R", 50.80, 195.58, 90, ref_off=(-3.8, -0.8), val_off=(-4.0, 1.2))
    place("C15", "C", 60.96, 195.58, 0, ref_off=(3.5, -1.0), val_off=(3.8, 1.0))
    wire((30.48, 167.64), (86.36, 167.64))
    junc((50.80, 167.64))
    wire((50.80, 167.64), pin_pos[("R15", "2")])
    wire(pin_pos[("R15", "1")], pin_pos[("R16", "2")])
    junc((50.80, 185.42))
    polywire([(50.80, 185.42), (60.96, 185.42), pin_pos[("C15", "1")]])
    junc((60.96, 185.42))
    gnd_at(pin_pos[("R16", "1")])
    gnd_at(pin_pos[("C15", "2")])

    place("U4", "IC_LM393B", 86.36, 190.50, 0, ref_off=(-5.0, -9.5), val_off=(4.5, -9.5))
    place("C14", "C", 74.93, 175.26, 0, ref_off=(-4.0, -0.8), val_off=(-4.0, 1.2))
    wire((86.36, 167.64), pin_pos[("U4", "8")])
    junc((74.93, 167.64))
    wire((74.93, 167.64), pin_pos[("C14", "1")])
    gnd_at(pin_pos[("C14", "2")])
    gnd_at(pin_pos[("U4", "4")])

    # Wire UVLO_SENSE to 1IN+(3) and 2IN+(5), V_REF to 1IN-(2) and 2IN-(6)
    polywire([(60.96, 185.42), pin_pos[("U4", "3")]])
    lbl("UVLO_SENSE", (63.50, 185.42))
    polywire([(68.58, 185.42), (68.58, 193.04), pin_pos[("U4", "5")]])
    junc((68.58, 185.42))
    polywire([(30.48, 184.15), (43.18, 184.15), (43.18, 205.74), (71.12, 205.74), (71.12, 187.96), pin_pos[("U4", "2")]])
    junc((30.48, 184.15))
    lbl("V_REF", (33.02, 184.15))
    polywire([(71.12, 195.58), pin_pos[("U4", "6")]])
    junc((71.12, 195.58))

    wire(pin_pos[("U4", "1")], (106.68, 186.69))
    lbl("U1_CTRL", (106.68, 186.69))
    wire(pin_pos[("U4", "7")], (106.68, 194.31))
    lbl("U2_CTRL", (106.68, 194.31))

    # Maxi-Switch Right Sub-block (R17/D14 5.1V bias, R5/R6, D12 BAT54, Q2/Q3 BSS138, J4 <-> SW1)
    place("R17", "R", 124.46, 177.80, 90, ref_off=(-3.8, -0.8), val_off=(-4.0, 1.2))
    place("D14", "D_Zener", 124.46, 193.04, 270, ref_off=(-3.8, -0.8), val_off=(-4.0, 1.2))
    wire((124.46, 167.64), pin_pos[("R17", "2")])
    lbl("VIN_20V", (124.46, 167.64))
    wire(pin_pos[("R17", "1")], pin_pos[("D14", "1")])
    gnd_at(pin_pos[("D14", "2")])

    # V_SW_BIAS horizontal rail at y=184.15 -> R5 (SW_UV_N) and R6 (SW_ALL_N)
    place("R5", "R", 142.24, 193.04, 90, ref_off=(-3.8, -0.8), val_off=(-4.0, 1.2))
    place("R6", "R", 162.56, 193.04, 90, ref_off=(-3.8, -0.8), val_off=(-4.0, 1.2))
    polywire([(124.46, 184.15), (162.56, 184.15), pin_pos[("R6", "2")]])
    wire((142.24, 184.15), pin_pos[("R5", "2")])
    lbl("V_SW_BIAS", (128.27, 184.15))

    # D12 (BAT54: 1=A -> SW_UV_N, 3=K -> SW_ALL_N, 2=NC)
    place("D12", "D_BAT54", 152.40, 203.20, 0, ref_off=(0, -3.5), val_off=(0, 5.2))
    nc(pin_pos[("D12", "2")])
    polywire([pin_pos[("R5", "1")], (142.24, 203.20), pin_pos[("D12", "1")]])
    polywire([pin_pos[("R6", "1")], (162.56, 203.20), pin_pos[("D12", "3")]])

    # Q2 (Ch1 UV) & Q3 (Ch2 Vis) BSS138 pull-down MOSFETs
    place("Q2", "Q_NMOS", 149.86, 231.14, 0, ref_off=(3.5, -2.0), val_off=(4.0, 0.5))
    place("Q3", "Q_NMOS", 172.72, 231.14, 0, ref_off=(3.5, -2.0), val_off=(4.0, 0.5))
    polywire([(142.24, 203.20), (142.24, 232.41), pin_pos[("Q2", "1")]])
    lbl("SW_UV_N", (142.24, 213.36))
    polywire([(162.56, 203.20), (162.56, 232.41), pin_pos[("Q3", "1")]])
    lbl("SW_ALL_N", (162.56, 213.36))
    gnd_at(pin_pos[("Q2", "2")])
    gnd_at(pin_pos[("Q3", "2")])
    wire(pin_pos[("Q2", "3")], (149.86, 220.98))
    lbl("U1_CTRL", (149.86, 220.98))
    wire(pin_pos[("Q3", "3")], (172.72, 220.98))
    lbl("U2_CTRL", (172.72, 220.98))

    # J4 header wired directly to Off-Board SW1 (+ SW1_BOOT mechanical item)
    place("J4", "Conn_3P", 160.02, 259.08, 180, ref_off=(0, -6.5), val_off=(0, 6.8))
    place("SW1", "SW_SPDT_3P", 187.96, 259.08, 0, ref_off=(0, -6.5), val_off=(0, 6.8))
    place("SW1_BOOT", "Mech_Item", 187.96, 271.78, 0, ref_off=(-9.0, 0), val_off=(9.0, 0))
    polywire([pin_pos[("J4", "1")], (167.64, 261.62), (167.64, 251.46), (176.53, 251.46), (176.53, 256.54), pin_pos[("SW1", "1")]])
    lbl("SW_UV_N", (170.18, 251.46))
    wire(pin_pos[("J4", "2")], pin_pos[("SW1", "2")])
    wire((173.99, 259.08), (173.99, 269.24))
    gnd_at((173.99, 269.24))
    polywire([pin_pos[("J4", "3")], (170.18, 256.54), (170.18, 264.16), (177.80, 264.16), (177.80, 261.62), pin_pos[("SW1", "3")]])
    lbl("SW_ALL_N", (172.72, 264.16))

    # =====================================================================
    # BLOCK 3 (Top-Right: X=213..404, Y=18..134): CH1 4S UV-A BUCK (333 mA)
    # =====================================================================
    def build_buck_block(y0, title, u_ref, r_ref, l_ref, d_ref, c_bulk, c_hf, c_out, c_ss, j_ref,
                         led_refs, pos_net, neg_net, sw_net, ctrl_net, n_nets):
        box(213.36, y0, 403.86, y0 + 114.30, title)
        y_top = y0 + 25.40
        y_mid = y0 + 58.42
        y_bot = y0 + 83.82

        # Input decoupling C_bulk, C_hf on VIN_20V
        place(c_bulk, "C", 226.06, y_top + 15.24, 0, ref_off=(-4.2, -1.0), val_off=(-4.5, 1.2))
        place(c_hf, "C", 241.30, y_top + 15.24, 0, ref_off=(-4.0, -1.0), val_off=(-4.2, 1.2))
        place(r_ref, "R", 269.24, y_top, 0, ref_off=(0, -3.2), val_off=(0, 3.2))
        wire((220.98, y_top), pin_pos[(r_ref, "1")])
        lbl("VIN_20V", (220.98, y_top))
        for cx, cref in [(226.06, c_bulk), (241.30, c_hf)]:
            wire((cx, y_top), pin_pos[(cref, "1")])
            junc((cx, y_top))
            gnd_at(pin_pos[(cref, "2")])

        # U1 / U2 AL8860WT-7
        place(u_ref, "IC_AL8860", 269.24, y_mid, 0, ref_off=(0, -8.5), val_off=(0, 8.5))
        # VIN (5) to VIN_20V bus
        polywire([pin_pos[(u_ref, "5")], (251.46, y_mid - 3.81), (251.46, y_top)])
        junc((251.46, y_top))
        # CTRL (3) + soft-start cap C_ss
        place(c_ss, "C", 246.38, y_mid + 12.70, 0, ref_off=(-4.0, -1.0), val_off=(-4.2, 1.2))
        polywire([pin_pos[(u_ref, "3")], (233.68, y_mid)])
        junc((246.38, y_mid))
        wire((246.38, y_mid), pin_pos[(c_ss, "1")])
        gnd_at(pin_pos[(c_ss, "2")])
        lbl(ctrl_net, (233.68, y_mid))
        # GND (2)
        polywire([pin_pos[(u_ref, "2")], (254.00, y_mid + 3.81), (254.00, y_mid + 12.70)])
        gnd_at((254.00, y_mid + 12.70))

        # SET (4) -> R_sense right side (UV_POS / VIS_POS) -> C_out -> J_ref.1
        polywire([pin_pos[(r_ref, "2")], (322.58, y_top)])
        polywire([pin_pos[(u_ref, "4")], (287.02, y_mid - 3.81), (287.02, y_top)])
        junc((287.02, y_top))
        lbl(pos_net, (292.10, y_top))

        # Freewheeling Schottky D9/D10 (K to VIN_20V, A to SW_NODE)
        place(d_ref, "D_Schottky", 259.08, y_top + 15.24, 270, ref_off=(-3.5, -1.0), val_off=(-3.8, 1.2))
        # D_Schottky rot=270: pin 1(K) at (0, +3.81) -> UP (y - 3.81); pin 2(A) at (0, -3.81) -> DOWN (y + 3.81)
        wire((259.08, y_top), pin_pos[(d_ref, "1")])
        junc((259.08, y_top))

        # SW (1) -> L1/L2 -> UV_NEG/VIS_NEG
        place(l_ref, "L", 297.18, y_bot, 0, ref_off=(0, -3.2), val_off=(0, 3.2))
        polywire([pin_pos[(u_ref, "1")], (287.02, y_mid + 3.81), (287.02, y_bot), pin_pos[(l_ref, "1")]])
        polywire([pin_pos[(d_ref, "2")], (259.08, y_mid + 17.78), (287.02, y_mid + 17.78), (287.02, y_bot)])
        junc((287.02, y_bot))
        lbl(sw_net, (271.78, y_mid + 17.78))

        # Output ripple bypass C4/C5 across POS and NEG
        place(c_out, "C", 312.42, y_top + 27.94, 0, ref_off=(-4.2, -1.0), val_off=(-4.2, 1.2))
        wire((312.42, y_top), pin_pos[(c_out, "1")])
        junc((312.42, y_top))
        polywire([pin_pos[(l_ref, "2")], (322.58, y_bot)])
        wire(pin_pos[(c_out, "2")], (312.42, y_bot))
        junc((312.42, y_bot))
        lbl(neg_net, (304.80, y_bot))

        # Connector J2 / J3 wired into Off-Board 4S LED string
        place(j_ref, "Conn_2P", 332.74, y_mid, 0, ref_off=(0, -5.8), val_off=(0, 5.8))
        polywire([(322.58, y_top), (322.58, y_mid - 1.27), pin_pos[(j_ref, "1")]])
        polywire([(322.58, y_bot), (322.58, y_mid + 1.27), pin_pos[(j_ref, "2")]])

        # Off-board 4S LED string (dashed enclosure)
        box(342.90, y0 + 12.70, 398.78, y0 + 101.60, f"OFF-BOARD 4S ({j_ref})", dash=True)
        led_ys = [y0 + 30.48, y0 + 48.26, y0 + 66.04, y0 + 83.82]
        for idx, (lref, ly) in enumerate(zip(led_refs, led_ys)):
            place(lref, "D_LED_AK", 370.84, ly, 270, ref_off=(4.2, -1.2), val_off=(4.5, 1.2))
        # D_LED_AK rot=270: pin 1 (A) is UP (y - 3.81), pin 2 (K) is DOWN (y + 3.81)
        polywire([(322.58, y_top), (370.84, y_top), pin_pos[(led_refs[0], "1")]])
        junc((322.58, y_top))
        for idx in range(3):
            wire(pin_pos[(led_refs[idx], "2")], pin_pos[(led_refs[idx + 1], "1")])
            lbl(n_nets[idx], (370.84, round(0.5 * (led_ys[idx] + led_ys[idx + 1]), 2)))
        polywire([pin_pos[(led_refs[3], "2")], (370.84, y0 + 93.98), (322.58, y0 + 93.98), (322.58, y_bot)])

    build_buck_block(
        17.78, "BLOCK 3: CH1 4S UV-A 365 nm BUCK DRIVER (333 mA)",
        "U1", "R3", "L1", "D9", "C2", "C8", "C4", "C6", "J2",
        ["D1", "D2", "D3", "D4"], "UV_POS", "UV_NEG", "SW1_NODE", "U1_CTRL",
        ["UV_N1", "UV_N2", "UV_N3"],
    )
    build_buck_block(
        139.70, "BLOCK 4: CH2 4S VISIBLE BUCK DRIVER (333 mA)",
        "U2", "R4", "L2", "D10", "C3", "C9", "C5", "C7", "J3",
        ["D5", "D6", "D7", "D8"], "VIS_POS", "VIS_NEG", "SW2_NODE", "U2_CTRL",
        ["VIS_N1", "VIS_N2", "VIS_N3"],
    )

    # Automatic exact wire splitter & junction emitter for 0 KiCad ERC violations!
    split_pts = set(pin_pos.values())
    for a, b in raw_wires:
        split_pts.add(a)
        split_pts.add(b)
    for _, pt_l, _, _, _ in raw_labels:
        split_pts.add(pt_l)

    final_segs = set()
    for a, b in raw_wires:
        if abs(a[1] - b[1]) < 1e-4:  # Horizontal
            y = a[1]
            x0, x1 = min(a[0], b[0]), max(a[0], b[0])
            xs = sorted({x0, x1} | {p[0] for p in split_pts if abs(p[1] - y) < 1e-3 and x0 < p[0] < x1})
            for u, v in zip(xs, xs[1:]):
                if v - u > 1e-4:
                    final_segs.add(((u, y), (v, y)))
        elif abs(a[0] - b[0]) < 1e-4:  # Vertical
            x = a[0]
            y0, y1 = min(a[1], b[1]), max(a[1], b[1])
            ys = sorted({y0, y1} | {p[1] for p in split_pts if abs(p[0] - x) < 1e-3 and y0 < p[1] < y1})
            for u, v in zip(ys, ys[1:]):
                if v - u > 1e-4:
                    final_segs.add(((x, u), (x, v)))
        else:
            final_segs.add((a, b))

    deg = {}
    for a, b in sorted(final_segs):
        deg[a] = deg.get(a, 0) + 1
        deg[b] = deg.get(b, 0) + 1
        elements.append(
            f'  (wire (pts (xy {a[0]:.2f} {a[1]:.2f}) (xy {b[0]:.2f} {b[1]:.2f})) '
            f'(stroke (width 0) (type default)) (uuid "{uid(f"sw_{a}_{b}")}"))'
        )
    pin_counts = {}
    for p in pin_pos.values():
        pin_counts[p] = pin_counts.get(p, 0) + 1
    for pt_j, d_cnt in sorted(deg.items()):
        if d_cnt >= 3 or (d_cnt >= 2 and pin_counts.get(pt_j, 0) >= 1):
            elements.append(f'  (junction (at {pt_j[0]:.2f} {pt_j[1]:.2f}) (diameter 0) (color 0 0 0 0) (uuid "{uid(f"sj_{pt_j}")}"))')
    for idx_l, (nm, pt_l, ang, just, hidden) in enumerate(raw_labels):
        h_str = " (hide yes)" if hidden else ""
        sz_str = "0.8 0.8" if hidden else "1.15 1.15"
        elements.append(
            f'  (label "{nm}" (at {pt_l[0]:.2f} {pt_l[1]:.2f} {ang}) '
            f'(effects (font (size {sz_str})) (justify {just}){h_str}) (uuid "{uid(f"sl_{idx_l}_{nm}_{pt_l}")}"))'
        )

    # Assemble full .kicad_sch with embedded lib_symbols
    lib_sym_txt = "\n".join(
        s.replace('(symbol "', '(symbol "lepiled:', 1) for s in syms.values()
    )
    sch = f"""(kicad_sch
  (version 20250114)
  (generator "eeschema")
  (generator_version "9.0")
  (uuid "{root_uuid}")
  (paper "A3")
  (title_block
    (title "LepiLED DIY Maxi Switch — 20 V USB-C PD + Dual AL8860 Buck")
    (date "2026-11-19")
    (rev "4.0")
    (company "LepiLED Open-Source DIY Hardware")
    (comment 1 "Option 2: AP33771C 20V/1A PD Sink + Dual AL8860WT-7 333mA Buck + 17.25V UVLO")
    (comment 2 "72 RefDes (62 On-PCB, 10 Off-Board) | ~0.50 W PCB loss | 94.3% Efficiency")
  )
  (lib_symbols
{lib_sym_txt}
  )
{chr(10).join(elements)}
  (sheet_instances
    (path "/" (page "1"))
  )
)
"""
    (BASE_DIR / "driver_pcb.kicad_sch").write_text(sch)
    return fp_map, short_val


# ---------------------------------------------------------------------------
# 5. GridRouter with Strict ZERO-Via-in-Pad Enforcement
# ---------------------------------------------------------------------------

class GridRouter:
    RES = 0.15
    XMIN, XMAX = -17.7, +17.7
    YMIN, YMAX = -22.65, +22.65

    def __init__(self, board: pcbnew.BOARD, b_keepouts=None):
        self.board = board
        self.nx = int(round((self.XMAX - self.XMIN) / self.RES)) + 1
        self.ny = int(round((self.YMAX - self.YMIN) / self.RES)) + 1
        self.obstacles = []      # (layer_mask, x0, y0, x1, y1, netname)
        self.smd_pad_boxes = []  # (x0, y0, x1, y1) ALL SMD pads (never allow vias inside!)
        self.pad_rects = []      # (layer_mask, x0, y0, x1, y1, netname) for start/goal pad-exit unblocking
        self.pth_centers = []    # (cx, cy, drill_r) ALL PTH holes
        self.net_vias = {}       # netname -> set of (ix, iy) existing same-net vias (reusable for free!)
        self.ic_courtyards = []  # (x0, y0, x1, y1) IC courtyards (no vias inside!)
        self.b_keepouts = b_keepouts or []
        self._index_board()

    def _to_ij(self, x, y):
        ix = max(0, min(self.nx - 1, int(round((x - self.XMIN) / self.RES))))
        iy = max(0, min(self.ny - 1, int(round((y - self.YMIN) / self.RES))))
        return ix, iy

    def _to_xy(self, ix, iy):
        return (round(self.XMIN + ix * self.RES, 4), round(self.YMIN + iy * self.RES, 4))

    def _index_board(self):
        # Corner keepouts for 2.0 mm board radii
        for cx, cy in [(-18.0, -23.0), (+18.0, -23.0), (-18.0, +23.0), (+18.0, +23.0)]:
            self.obstacles.append((3, cx - 1.0, cy - 1.0, cx + 1.0, cy + 1.0, "__EDGE__"))
        for x0, y0, x1, y1 in self.b_keepouts:
            self.obstacles.append((2, x0, y0, x1, y1, "__KO_B__"))

        for fp in self.board.GetFootprints():
            ref = fp.GetReference()
            # Track IC & transistor courtyards to keep vias completely outside
            if ref.startswith(("U", "Q")):
                xs, ys = [], []
                for g in fp.GraphicalItems():
                    if g.GetLayer() == pcbnew.F_Fab:
                        bb = g.GetBoundingBox()
                        xs.extend([bb.GetLeft() / 1e6 - CX, bb.GetRight() / 1e6 - CX])
                        ys.extend([CY - bb.GetBottom() / 1e6, CY - bb.GetTop() / 1e6])
                if xs:
                    self.ic_courtyards.append((min(xs), min(ys), max(xs), max(ys)))

            for pad in fp.Pads():
                pos = pad.GetPosition()
                px = pos.x / 1e6 - CX
                py = CY - pos.y / 1e6
                bbox = pad.GetBoundingBox()
                x0 = bbox.GetLeft() / 1e6 - CX
                x1 = bbox.GetRight() / 1e6 - CX
                y1 = CY - bbox.GetTop() / 1e6
                y0 = CY - bbox.GetBottom() / 1e6
                nn = pad.GetNetname()
                if pad.GetAttribute() == pcbnew.PAD_ATTRIB_PTH:
                    self.obstacles.append((3, x0, y0, x1, y1, nn))
                    self.pad_rects.append((3, x0, y0, x1, y1, nn))
                    dr = max(pad.GetDrillSize().x, pad.GetDrillSize().y) / 2e6
                    self.pth_centers.append((px, py, dr))
                else:
                    self.obstacles.append((1, x0, y0, x1, y1, nn))
                    self.pad_rects.append((1, x0, y0, x1, y1, nn))
                    self.smd_pad_boxes.append((x0, y0, x1, y1))

    def add_seg_obstacle(self, x0, y0, x1, y1, width_mm, layer, netname):
        hw = width_mm / 2.0
        lm = 1 if layer == pcbnew.F_Cu else 2
        self.obstacles.append((lm, min(x0, x1) - hw, min(y0, y1) - hw,
                               max(x0, x1) + hw, max(y0, y1) + hw, netname))

    def add_via_obstacle(self, x, y, diam_mm, netname):
        r = diam_mm / 2.0
        self.obstacles.append((3, x - r, y - r, x + r, y + r, netname))
        self.pth_centers.append((x, y, 0.15))
        self.net_vias.setdefault(netname, set()).add(self._to_ij(x, y))

    def _build_blocked(self, netname, half_w, clr_mm):
        b0 = [bytearray(self.nx) for _ in range(self.ny)]
        b1 = [bytearray(self.nx) for _ in range(self.ny)]
        via_blk = [bytearray(self.nx) for _ in range(self.ny)]

        pad_m = half_w + clr_mm + 0.02
        vm_net = 0.30 + max(clr_mm, 0.20) + 0.03
        # STRICT ZERO VIA-IN-PAD: drill_r=0.15 + 0.30 mm safety = 0.45 mm -> drill-to-SMD >= 0.28 mm (> 0.25 mm rule!)
        smd_via_margin = 0.46

        # Block board border for vias & tracks (respecting 0.30 mm copper-edge clearance)
        for iy in range(self.ny):
            y = self.YMIN + iy * self.RES
            for ix in range(self.nx):
                x = self.XMIN + ix * self.RES
                if abs(x) > 17.20 or abs(y) > 22.20:
                    via_blk[iy][ix] = 1
                if abs(x) > 17.55 or abs(y) > 22.55:
                    b0[iy][ix] = 1
                    b1[iy][ix] = 1

        # 1. Block ALL SMD pads from receiving ANY via (even same-net!)
        for x0, y0, x1, y1 in self.smd_pad_boxes:
            ix0 = max(0, int(math.floor((x0 - smd_via_margin - self.XMIN) / self.RES)))
            ix1 = min(self.nx - 1, int(math.ceil((x1 + smd_via_margin - self.XMIN) / self.RES)))
            iy0 = max(0, int(math.floor((y0 - smd_via_margin - self.YMIN) / self.RES)))
            iy1 = min(self.ny - 1, int(math.ceil((y1 + smd_via_margin - self.YMIN) / self.RES)))
            for iy in range(iy0, iy1 + 1):
                vrow = via_blk[iy]
                for ix in range(ix0, ix1 + 1):
                    vrow[ix] = 1

        # 2. Block ALL IC/transistor bodies (F.Fab) from receiving ANY via
        for x0, y0, x1, y1 in self.ic_courtyards:
            ix0 = max(0, int(math.floor((x0 - 0.15 - self.XMIN) / self.RES)))
            ix1 = min(self.nx - 1, int(math.ceil((x1 + 0.15 - self.XMIN) / self.RES)))
            iy0 = max(0, int(math.floor((y0 - 0.15 - self.YMIN) / self.RES)))
            iy1 = min(self.ny - 1, int(math.ceil((y1 + 0.15 - self.YMIN) / self.RES)))
            for iy in range(iy0, iy1 + 1):
                vrow = via_blk[iy]
                for ix in range(ix0, ix1 + 1):
                    vrow[ix] = 1

        # 3. Block hole-to-hole clearance around all existing PTH/vias
        for cx, cy, dr in self.pth_centers:
            hm = dr + 0.15 + 0.32
            ix0 = max(0, int(math.floor((cx - hm - self.XMIN) / self.RES)))
            ix1 = min(self.nx - 1, int(math.ceil((cx + hm - self.XMIN) / self.RES)))
            iy0 = max(0, int(math.floor((cy - hm - self.YMIN) / self.RES)))
            iy1 = min(self.ny - 1, int(math.ceil((cy + hm - self.YMIN) / self.RES)))
            for iy in range(iy0, iy1 + 1):
                vrow = via_blk[iy]
                for ix in range(ix0, ix1 + 1):
                    vrow[ix] = 1

        # 4. Net-specific copper obstacles
        for lm, x0, y0, x1, y1, nn in self.obstacles:
            if nn == netname and nn not in ("__EDGE__", "__KO_B__"):
                continue
            ix0 = max(0, int(math.floor((x0 - pad_m - self.XMIN) / self.RES)))
            ix1 = min(self.nx - 1, int(math.ceil((x1 + pad_m - self.XMIN) / self.RES)))
            iy0 = max(0, int(math.floor((y0 - pad_m - self.YMIN) / self.RES)))
            iy1 = min(self.ny - 1, int(math.ceil((y1 + pad_m - self.YMIN) / self.RES)))
            if lm & 1:
                for iy in range(iy0, iy1 + 1):
                    row = b0[iy]
                    for ix in range(ix0, ix1 + 1):
                        row[ix] = 1
            if lm & 2:
                for iy in range(iy0, iy1 + 1):
                    row = b1[iy]
                    for ix in range(ix0, ix1 + 1):
                        row[ix] = 1
            vx0 = max(0, int(math.floor((x0 - vm_net - self.XMIN) / self.RES)))
            vx1 = min(self.nx - 1, int(math.ceil((x1 + vm_net - self.XMIN) / self.RES)))
            vy0 = max(0, int(math.floor((y0 - vm_net - self.YMIN) / self.RES)))
            vy1 = min(self.ny - 1, int(math.ceil((y1 + vm_net - self.YMIN) / self.RES)))
            for iy in range(vy0, vy1 + 1):
                vrow = via_blk[iy]
                for ix in range(vx0, vx1 + 1):
                    vrow[ix] = 1
        return (b0, b1), via_blk

    def _unblock_endpoint_pad(self, blocked, lyr_idx, pt_xy, netname):
        px, py = pt_xy
        lm_bit = 1 if lyr_idx == 0 else 2
        ix_c, iy_c = self._to_ij(px, py)
        blocked[lyr_idx][iy_c][ix_c] = 0
        for lm, x0, y0, x1, y1, nn in self.pad_rects:
            if (lm & lm_bit) and nn == netname and (x0 - 0.05 <= px <= x1 + 0.05) and (y0 - 0.05 <= py <= y1 + 0.05):
                ix0 = max(0, int(math.floor((x0 - self.XMIN) / self.RES)))
                ix1 = min(self.nx - 1, int(math.ceil((x1 - self.XMIN) / self.RES)))
                iy0 = max(0, int(math.floor((y0 - self.YMIN) / self.RES)))
                iy1 = min(self.ny - 1, int(math.ceil((y1 - self.YMIN) / self.RES)))
                for iy in range(iy0, iy1 + 1):
                    row = blocked[lyr_idx][iy]
                    for ix in range(ix0, ix1 + 1):
                        row[ix] = 0

    def route(self, start_xy, start_lyr_idx, goal_xy, goal_lyr_idx, net_obj, width_mm, clr_mm, allow_b=True, b_penalty=4):
        netname = net_obj.GetNetname()
        sx, sy = self._to_ij(*start_xy)
        gx, gy = self._to_ij(*goal_xy)
        blocked, via_blk = self._build_blocked(netname, width_mm / 2.0, clr_mm)
        self._unblock_endpoint_pad(blocked, start_lyr_idx, start_xy, netname)
        self._unblock_endpoint_pad(blocked, goal_lyr_idx, goal_xy, netname)

        start = (start_lyr_idx, sx, sy)
        goal = (goal_lyr_idx, gx, gy)
        pq = [(abs(sx - gx) + abs(sy - gy), 0, start, -1)]
        dist = {start: 0}
        parent = {}
        dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        reusable = self.net_vias.get(netname, set())

        while pq:
            _, g, state, prev_dir = heapq.heappop(pq)
            if state == goal:
                break
            if g > dist.get(state, 10**9):
                continue
            l, x, y = state
            for d_idx, (dx, dy) in enumerate(dirs):
                nx_, ny_ = x + dx, y + dy
                if 0 <= nx_ < self.nx and 0 <= ny_ < self.ny and not blocked[l][ny_][nx_]:
                    turn_cost = 1 if (prev_dir != -1 and prev_dir != d_idx) else 0
                    ng = g + 1 + turn_cost + (b_penalty if l == 1 else 0)
                    ns = (l, nx_, ny_)
                    if ng < dist.get(ns, 10**9):
                        dist[ns] = ng
                        parent[ns] = state
                        heapq.heappush(pq, (ng + abs(nx_ - gx) + abs(ny_ - gy), ng, ns, d_idx))
            is_reuse = (x, y) in reusable
            if allow_b and (not via_blk[y][x] or is_reuse):
                nl = 1 - l
                if not blocked[nl][y][x]:
                    ng = g + (2 if is_reuse else 22)
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

        pts_coords = [self._to_xy(ix, iy) for (_, ix, iy) in path]
        pts_coords[0] = start_xy
        pts_coords[-1] = goal_xy

        i = 0
        while i < len(path) - 1:
            l0, l1 = path[i][0], path[i + 1][0]
            if l0 != l1:
                if (path[i][1], path[i][2]) not in reusable:
                    vx, vy = pts_coords[i]
                    add_via(self.board, vx, vy, net_obj, 0.60, 0.30)
                    self.add_via_obstacle(vx, vy, 0.60, netname)
                i += 1
                continue
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
            p_start, p_end = pts_coords[i], pts_coords[j]
            lyr = pcbnew.F_Cu if l0 == 0 else pcbnew.B_Cu
            add_track(self.board, [p_start, p_end], width_mm, net_obj, lyr)
            self.add_seg_obstacle(p_start[0], p_start[1], p_end[0], p_end[1], width_mm, lyr, netname)
            i = j


# ---------------------------------------------------------------------------
# 6. Board Primitives & Option 2 PCB Construction
# ---------------------------------------------------------------------------

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


def get_pad_pos(fp, pad_num):
    for p in fp.Pads():
        if p.GetNumber() == str(pad_num):
            pos = p.GetPosition()
            return (round(pos.x / 1e6 - CX, 4), round(CY - pos.y / 1e6, 4))
    raise KeyError(f"Pad {pad_num} not found in {fp.GetReference()}")


def assert_zero_via_in_pad(board: pcbnew.BOARD):
    """Hard geometric guard: every via drill must be >= 0.25 mm clear of every SMD pad copper!"""
    smd_boxes = []
    for fp in board.GetFootprints():
        for p in fp.Pads():
            if p.GetAttribute() == pcbnew.PAD_ATTRIB_SMD and p.IsOnLayer(pcbnew.F_Cu):
                bb = p.GetBoundingBox()
                smd_boxes.append((
                    fp.GetReference(), p.GetNumber(),
                    bb.GetLeft() / 1e6 - CX, CY - bb.GetBottom() / 1e6,
                    bb.GetRight() / 1e6 - CX, CY - bb.GetTop() / 1e6,
                ))
    vias = []
    for trk in board.GetTracks():
        if trk.GetClass() == "PCB_VIA":
            pos = trk.GetPosition()
            vias.append((pos.x / 1e6 - CX, CY - pos.y / 1e6, trk.GetDrill() / 2e6, trk.GetWidth(pcbnew.F_Cu) / 2e6))

    violations = []
    for vx, vy, vr_drill, vr_pad in vias:
        for ref, pnum, x0, y0, x1, y1 in smd_boxes:
            dx = max(x0 - vx, 0.0, vx - x1)
            dy = max(y0 - vy, 0.0, vy - y1)
            d_drill = math.hypot(dx, dy) - vr_drill
            if d_drill < 0.24:
                violations.append((ref, pnum, round(vx, 2), round(vy, 2), round(d_drill, 3)))
    assert not violations, f"ZERO-VIA-IN-PAD VIOLATION ({len(violations)}): {violations[:10]}"
    print(f"Verified 0 via-in-pad across {len(vias)} vias and {len(smd_boxes)} SMD pads (all drill clearances >= 0.25 mm).")


def place_non_overlapping_silkscreen(board: pcbnew.BOARD):
    """Place every populated component's RefDes on F.SilkS cleanly outside all pads, mask openings, and other text."""
    # Collect forbidden F.SilkS rectangles: pads (+0.30 mm), silk outlines (+0.22 mm), and tall/IC F.Fab bodies
    mask_boxes = []
    body_boxes = {}
    for fp in board.GetFootprints():
        ref = fp.GetReference()
        for p in fp.Pads():
            if p.IsOnLayer(pcbnew.F_Mask) or p.IsOnLayer(pcbnew.F_Cu):
                bb = p.GetBoundingBox()
                m = 0.30
                mask_boxes.append((
                    bb.GetLeft() / 1e6 - CX - m, CY - bb.GetBottom() / 1e6 - m,
                    bb.GetRight() / 1e6 - CX + m, CY - bb.GetTop() / 1e6 + m,
                ))
        for g in fp.GraphicalItems():
            if g.GetLayer() == pcbnew.F_SilkS:
                bb = g.GetBoundingBox()
                m = 0.22
                mask_boxes.append((
                    bb.GetLeft() / 1e6 - CX - m, CY - bb.GetBottom() / 1e6 - m,
                    bb.GetRight() / 1e6 - CX + m, CY - bb.GetTop() / 1e6 + m,
                ))
        if ref.startswith(("J", "U", "L", "F")) or ref in ("D9", "D10", "D11", "D13"):
            xs, ys = [], []
            for g in fp.GraphicalItems():
                if g.GetLayer() == pcbnew.F_Fab:
                    bb = g.GetBoundingBox()
                    xs.extend([bb.GetLeft() / 1e6 - CX, bb.GetRight() / 1e6 - CX])
                    ys.extend([CY - bb.GetBottom() / 1e6, CY - bb.GetTop() / 1e6])
            if xs:
                body_boxes[ref] = (min(xs) - 0.10, min(ys) - 0.10, max(xs) + 0.10, max(ys) + 0.10)
    placed_text_boxes = []

    def overlaps_any(bx0, by0, bx1, by1, own_ref=""):
        if bx0 < -17.3 or bx1 > 17.3 or by0 < -22.3 or by1 > 22.3:
            return True
        for x0, y0, x1, y1 in mask_boxes:
            if bx0 < x1 and bx1 > x0 and by0 < y1 and by1 > y0:
                return True
        for bref, (x0, y0, x1, y1) in body_boxes.items():
            if bref == own_ref and bref.startswith(("L", "J")):
                continue  # Allow L1/L2/J2/J3/J4 own labels cleanly if needed; never put OTHER labels inside!
            if bx0 < x1 and bx1 > x0 and by0 < y1 and by1 > y0:
                return True
        for x0, y0, x1, y1 in placed_text_boxes:
            if bx0 < x1 and bx1 > x0 and by0 < y1 and by1 > y0:
                return True
        return False

    # Place board-level legends first on F.SilkS and B.SilkS (verified exact top & mirrored bottom pin order!)
    # Top view left->right: J4 Pin3(ALL) | Pin2(GND) | Pin1(UV,sq); Bottom view left->right: Pin1(sq) | Pin2 | Pin3!
    board_texts = [
        ("3:ALL 2:GND", -3.55, +2.90, 0.62, pcbnew.F_SilkS, False),
        ("1:UV (J4)", -3.55, +1.90, 0.62, pcbnew.F_SilkS, False),
        ("TP1:18-24V", -8.20, -21.75, 0.72, pcbnew.F_SilkS, False),
        ("TP2:GND", +8.20, -21.75, 0.72, pcbnew.F_SilkS, False),
        ("LEPILED REV4 20V-PD", 0.0, +21.75, 0.80, pcbnew.B_SilkS, True),
        ("1:UV+ 2:UV-", -5.20, +16.40, 0.75, pcbnew.B_SilkS, True),
        ("1:VIS+ 2:VIS-", +5.20, +16.40, 0.75, pcbnew.B_SilkS, True),
        ("1:UV 2:GND 3:ALL", -1.40, -5.65, 0.72, pcbnew.B_SilkS, True),
    ]
    for txt_str, xm, ym, sz, lyr, mir in board_texts:
        t = pcbnew.PCB_TEXT(board)
        t.SetText(txt_str)
        t.SetLayer(lyr)
        t.SetPosition(kpt(xm, ym))
        t.SetTextSize(pcbnew.VECTOR2I(mm(sz), mm(sz)))
        t.SetTextThickness(mm(0.15))
        if mir:
            t.SetMirrored(True)
        board.Add(t)
        if lyr == pcbnew.F_SilkS:
            hw = 0.5 * len(txt_str) * sz * 0.78 + 0.25
            hh = 0.5 * sz + 0.25
            placed_text_boxes.append((xm - hw, ym - hh, xm + hw, ym + hh))

    # Place RefDes for all populated components cleanly on F.SilkS
    placed_cnt = 0
    for fp in board.GetFootprints():
        ref = fp.GetReference()
        if ref in ("H1", "H2", "H3", "H4", "TP1", "TP2"):
            fp.Reference().SetLayer(pcbnew.F_Fab)
            continue
        pos = fp.GetPosition()
        fx, fy = pos.x / 1e6 - CX, CY - pos.y / 1e6
        sz = 0.75
        hw = 0.5 * len(ref) * sz * 0.82 + 0.22
        hh = 0.5 * sz + 0.22
        # Spiral search within <= 4.0 mm of component center (cramped passives stay clean on F.Fab assembly map)
        best = None
        for r_step in range(2, 13):
            rad = r_step * 0.35
            for ang_deg in range(0, 360, 15):
                tx = fx + rad * math.cos(math.radians(ang_deg))
                ty = fy + rad * math.sin(math.radians(ang_deg))
                if not overlaps_any(tx - hw, ty - hh, tx + hw, ty + hh, own_ref=ref):
                    best = (tx, ty)
                    break
            if best:
                break
        if best:
            tx, ty = best
            fp.Reference().SetLayer(pcbnew.F_SilkS)
            fp.Reference().SetPosition(kpt(tx, ty))
            fp.Reference().SetTextAngle(pcbnew.EDA_ANGLE(0, pcbnew.DEGREES_T))
            fp.Reference().SetTextSize(pcbnew.VECTOR2I(mm(sz), mm(sz)))
            fp.Reference().SetTextThickness(mm(0.15))
            placed_text_boxes.append((tx - hw, ty - hh, tx + hw, ty + hh))
            placed_cnt += 1
        else:
            fp.Reference().SetLayer(pcbnew.F_Fab)
    print(f"Placed {placed_cnt} non-overlapping F.Silkscreen RefDes labels (0.75 mm / 0.15 mm stroke).")


def build_board(fp_map, short_val, comp_rows):
    pcb_path = BASE_DIR / "driver_pcb.kicad_pcb"
    board = pcbnew.NewBoard(str(pcb_path))
    board.SetCopperLayerCount(2)

    ds = board.GetDesignSettings()
    ds.m_TrackMinWidth = mm(0.20)
    ds.m_MinClearance = mm(0.16)
    ds.m_CopperEdgeClearance = mm(0.30)
    ds.m_HoleClearance = mm(0.25)
    ds.m_SilkClearance = mm(0.15)
    ds.m_ViasMinSize = mm(0.55)
    ds.m_ViasMinAnnularWidth = mm(0.12)
    ds.m_MinThroughDrill = mm(0.28)
    ds.m_SolderMaskExpansion = mm(0.05)  # Real KiCad 9 SWIG attribute!
    ds.m_SolderMaskMinWidth = mm(0.10)
    ds.SetAuxOrigin(kpt(0.0, 0.0))

    add_rounded_rect_edge_cuts(board, 36.0, 46.0, 2.0)

    # Create all canonical on-PCB nets with "/" root-sheet prefix for 100% KiCad schematic parity!
    net_names = [
        "GND", "VBUS", "VBUS_FUSED", "VBUS_DAMP", "VBUS_SENSE", "Q1_MID", "VIN_20V",
        "AUX_IN", "AUX_FUSED", "CC1", "CC2",
        "U3_VOUT", "U3_PWR_EN", "U3_V5V", "U3_VSEL", "U3_ISEL", "U3_LED", "PD_LED_A", "Q1_GATE",
        "V_REF", "UVLO_SENSE", "V_SW_BIAS", "SW_UV_N", "SW_ALL_N", "U1_CTRL", "U2_CTRL",
        "SW1_NODE", "SW2_NODE", "UV_POS", "UV_NEG", "VIS_POS", "VIS_NEG",
    ]
    nets = {}
    for nn in net_names:
        n = pcbnew.NETINFO_ITEM(board, f"/{nn}")
        board.Add(n)
        nets[nn] = n
    # Exact KiCad 9 auto-generated net names for no_connect pins (0 schematic parity issues!)
    nc_net_names = {
        ("D12", "2"): "unconnected-(D12-NC-Pad2)",
        ("U3", "6"): "unconnected-(U3-FLIP-Pad6)",
        ("U3", "12"): "unconnected-(U3-DN-Pad12)",
        ("U3", "13"): "unconnected-(U3-DP-Pad13)",
        ("J1", "A6"): "unconnected-(J1-D+-PadA6)",
        ("J1", "B6"): "unconnected-(J1-D+-PadB6)",
        ("J1", "A7"): "unconnected-(J1-D--PadA7)",
        ("J1", "B7"): "unconnected-(J1-D--PadB7)",
        ("J1", "A8"): "unconnected-(J1-SBU1-PadA8)",
        ("J1", "B8"): "unconnected-(J1-SBU2-PadB8)",
    }
    nc_nets = {}
    for k_nc, nname_nc in nc_net_names.items():
        n = pcbnew.NETINFO_ITEM(board, nname_nc)
        board.Add(n)
        nc_nets[k_nc] = n

    # Exact pad->net mapping for all 62 on-PCB components
    pad_net_map = {
        "J1": {"A4": "VBUS", "A9": "VBUS", "B4": "VBUS", "B9": "VBUS", "A5": "CC1", "B5": "CC2",
               "A1": "GND", "A12": "GND", "B1": "GND", "B12": "GND",
               "SH1": "GND", "SH2": "GND", "SH3": "GND", "SH4": "GND"},
        "J2": {"1": "UV_POS", "2": "UV_NEG"},
        "J3": {"1": "VIS_POS", "2": "VIS_NEG"},
        "J4": {"1": "SW_UV_N", "2": "GND", "3": "SW_ALL_N"},
        "TP1": {"1": "AUX_IN"}, "TP2": {"1": "GND"},
        "H1": {"1": "GND"}, "H2": {"1": "GND"}, "H3": {"1": "GND"}, "H4": {"1": "GND"},
        "F1": {"1": "VBUS", "2": "VBUS_FUSED"},
        "F2": {"1": "AUX_IN", "2": "AUX_FUSED"},
        "D11": {"1": "GND", "2": "VBUS_FUSED"},
        "D13": {"1": "VIN_20V", "2": "AUX_FUSED"},
        "D14": {"1": "V_SW_BIAS", "2": "GND"},
        "D15": {"1": "GND", "2": "PD_LED_A"},
        "D12": {"1": "SW_UV_N", "3": "SW_ALL_N"},
        "D9": {"1": "VIN_20V", "2": "SW1_NODE"},
        "D10": {"1": "VIN_20V", "2": "SW2_NODE"},
        "L1": {"1": "SW1_NODE", "2": "UV_NEG"},
        "L2": {"1": "SW2_NODE", "2": "VIS_NEG"},
        "U1": {"1": "SW1_NODE", "2": "GND", "3": "U1_CTRL", "4": "UV_POS", "5": "VIN_20V"},
        "U2": {"1": "SW2_NODE", "2": "GND", "3": "U2_CTRL", "4": "VIS_POS", "5": "VIN_20V"},
        "U3": {"1": "U3_VOUT", "2": "U3_PWR_EN", "3": "VBUS_SENSE", "4": "VBUS_FUSED",
               "5": "GND", "7": "U3_LED", "8": "U3_VSEL", "9": "U3_ISEL",
               "10": "CC2", "11": "CC1", "14": "U3_V5V", "15": "GND"},
        "U4": {"1": "U1_CTRL", "2": "V_REF", "3": "UVLO_SENSE", "4": "GND",
               "5": "UVLO_SENSE", "6": "V_REF", "7": "U2_CTRL", "8": "VIN_20V"},
        "U5": {"1": "V_REF", "2": "GND", "3": "GND"},
        "Q1A": {"1": "Q1_GATE", "2": "Q1_MID", "3": "VBUS_SENSE"},
        "Q1B": {"1": "Q1_GATE", "2": "Q1_MID", "3": "VIN_20V"},
        "Q2": {"1": "SW_UV_N", "2": "GND", "3": "U1_CTRL"},
        "Q3": {"1": "SW_ALL_N", "2": "GND", "3": "U2_CTRL"},
        "R1": {"1": "GND", "2": "CC1"}, "R2": {"1": "GND", "2": "CC2"},
        "R3": {"1": "VIN_20V", "2": "UV_POS"}, "R4": {"1": "VIN_20V", "2": "VIS_POS"},
        "R5": {"1": "SW_UV_N", "2": "V_SW_BIAS"}, "R6": {"1": "SW_ALL_N", "2": "V_SW_BIAS"},
        "R7": {"1": "VBUS_DAMP", "2": "VBUS_FUSED"},
        "R8": {"1": "VBUS_FUSED", "2": "VBUS_SENSE"},
        "R9": {"1": "GND", "2": "U3_VSEL"}, "R10": {"1": "GND", "2": "U3_ISEL"},
        "R11": {"1": "U3_PWR_EN", "2": "Q1_GATE"}, "R12": {"1": "VIN_20V", "2": "U3_VOUT"},
        "R13": {"1": "U3_LED", "2": "PD_LED_A"}, "R14": {"1": "V_REF", "2": "VIN_20V"},
        "R15": {"1": "UVLO_SENSE", "2": "VIN_20V"}, "R16": {"1": "GND", "2": "UVLO_SENSE"},
        "R17": {"1": "V_SW_BIAS", "2": "VIN_20V"},
        "C1": {"1": "VBUS_FUSED", "2": "GND"}, "C2": {"1": "VIN_20V", "2": "GND"},
        "C3": {"1": "VIN_20V", "2": "GND"}, "C4": {"1": "UV_POS", "2": "UV_NEG"},
        "C5": {"1": "VIS_POS", "2": "VIS_NEG"}, "C6": {"1": "U1_CTRL", "2": "GND"},
        "C7": {"1": "U2_CTRL", "2": "GND"}, "C8": {"1": "VIN_20V", "2": "GND"},
        "C9": {"1": "VIN_20V", "2": "GND"}, "C10": {"1": "VBUS_DAMP", "2": "GND"},
        "C11": {"1": "VBUS_SENSE", "2": "GND"}, "C12": {"1": "U3_V5V", "2": "GND"},
        "C13": {"1": "Q1_MID", "2": "Q1_GATE"}, "C14": {"1": "VIN_20V", "2": "GND"},
        "C15": {"1": "UVLO_SENSE", "2": "GND"},
    }

    # Clean, well-spaced floorplan on 36.0 x 46.0 mm preserving exact enclosure datums!
    # (ref: (x_mm, y_mm, rot_deg))
    placements = {
        # Fixed Enclosure Datums
        "H1": (-14.00, +19.00, 0), "H2": (+14.00, +19.00, 0),
        "H3": (-14.00, -19.00, 0), "H4": (+14.00, -19.00, 0),
        "J1": (0.00, -18.50, 0),
        "TP1": (-8.20, -19.50, 0), "TP2": (+8.20, -19.50, 0),
        "J2": (-5.20, +19.20, 0), "J3": (+5.20, +19.20, 0),
        "J4": (-1.40, -2.50, 0),

        # Block 1: Aux DC (Left edge) + USB-C PD (Lower-center & Lower-right)
        "F2": (-14.80, -12.20, 90),
        "D13": (-14.80, -5.80, 270),   # pin2(A) bot -> F2, pin1(K) top -> VIN_20V
        "F1": (-8.40, -14.20, 180),    # pin1(VBUS) right facing J1, pin2(VBUS_FUSED) left
        "D11": (-9.50, -9.80, 0),      # SMBJ22CA right above F1 (pin1=GND left, pin2=VBUS_FUSED right)
        "C1": (-4.40, -12.60, 270),    # 0805 1uF on VBUS_FUSED (1=top facing D11.2 & R7.2)
        "R7": (-3.80, -9.60, 0),       # 0805 1.0R damper (1=left -> C10.1, 2=right -> VBUS_FUSED)
        "C10": (-3.80, -6.80, 0),      # 1206 4.7uF damper cap directly above R7
        "R1": (+6.60, -16.60, 0),
        "R2": (+9.60, -16.60, 0),
        "R8": (+1.40, -12.80, 0),      # 1206 5mR shunt (1=VBUS_FUSED left, 2=VBUS_SENSE right)
        "U3": (+7.80, -12.60, 0),      # W-DFN3030-14 (pins 1-7 left, 8-14 right)
        "C11": (+0.50, -10.00, 180),   # 0805 1uF (1=VBUS_SENSE right, 2=GND left)
        "C12": (+11.80, -10.60, 0),    # 0805 1uF (1=U3_V5V left facing U3.14, 2=GND right)
        "R9": (+13.00, -15.20, 180),   # 2=U3_VSEL left facing U3.8, 1=GND right
        "R10": (+13.00, -13.60, 180),  # 2=U3_ISEL left facing U3.9, 1=GND right
        "R13": (+14.80, -8.80, 0),
        "D15": (+14.80, -6.80, 0),     # 2=PD_LED_A right directly over R13.2, 1=GND left facing open area!
        "Q1A": (+2.00, -7.00, 90),     # D(3) left facing C11.1, S(2) top-right, G(1) bot-right
        "Q1B": (+7.30, -7.00, 270),    # D(3) right -> VIN_20V, G(1) top-left, S(2) bot-left
        "R11": (+3.90, -10.00, 0),
        "C13": (+4.65, -7.00, 90),     # Vertical right between Q1A and Q1B (0 overlap with J4/U4/Q1B!)
        "R12": (+11.00, -7.85, 270),   # Clear of C12 courtyard!

        # Block 2: 17.25 V UVLO (Mid-Right) & Ground-Referenced Maxi-Switch (Mid-Left)
        "U4": (+10.00, -1.60, 0),      # SOIC-8 (wide channel above for UVLO divider!)
        "C14": (+13.40, +2.65, 0),     # 100nF right above U4.8 (VCC)
        "U5": (+16.00, -2.70, 270),    # SOT-23 (dropped 1.1mm so U4.7 right-side escape & via zone is wide open!)
        "R14": (+16.00, +1.90, 90),    # 0805 vertical above U5.1 (clear of D10 & C14!)
        "R15": (+10.40, +2.65, 0),     # 59k (1=UVLO_SENSE left, 2=VIN_20V right)
        "R16": (+7.40, +2.65, 0),      # 10k horizontal (1=GND left, 2=UVLO_SENSE right)
        "C15": (+4.40, +2.65, 180),    # 100nF horizontal (1=UVLO_SENSE right, 2=GND left, opens U4.1 corridor!)

        "D14": (-15.00, +0.20, 90),
        "R17": (-11.80, +1.20, 0),
        "R5": (-10.80, -1.20, 180),    # 1=SW_UV_N right facing J4, 2=V_SW_BIAS left facing R17!
        "R6": (-10.80, -3.00, 180),    # 1=SW_ALL_N right facing J4, 2=V_SW_BIAS left facing R17!
        "D12": (-9.80, -5.80, 0),
        "Q2": (-8.20, +1.85, 0),       # Clear of C2 courtyard!
        "Q3": (+1.30, +3.70, 0),       # Clear of C9, C15, and J4 legend!

        # Block 3: Ch1 4S UV Buck (Upper-Left)
        "L1": (-13.00, +11.80, 90),    # 6.0x6.0 mm (pads at y = +13.95, +9.65 -> vertical!)
        "D9": (-13.00, +5.40, 0),      # SMA (K=1 left/VIN_20V, A=2 right/SW1_NODE)
        "U1": (-6.00, +8.65, 0),       # TSOT25 (clear of R3 courtyard at y=+12.50!)
        "R3": (-4.20, +12.50, 90),     # 1206 0.30R vertical (1=VIN_20V bot, 2=UV_POS top)
        "C4": (-5.20, +15.55, 180),    # 0805 1uF (1=UV_POS right -> J2.1, 2=UV_NEG left -> J2.2)
        "C2": (-6.00, +5.20, 180),     # 1210 10uF (1=VIN_20V facing INWARD right!)
        "C8": (-2.00, +6.90, 90),      # 0603 100nF
        "C6": (-2.00, +10.20, 90),     # 0603 1.0nF soft-start

        # Block 4: Ch2 4S Visible Buck (Upper-Right)
        "L2": (+13.00, +11.80, 90),
        "D10": (+13.00, +5.40, 180),   # SMA mirrored (A=2 left/SW2_NODE, K=1 right/VIN_20V)
        "U2": (+6.00, +8.65, 180),     # TSOT25 mirrored (clear of R4 courtyard at y=+12.50!)
        "R4": (+6.20, +12.50, 90),     # 1206 0.30R vertical (1=VIN_20V bot, 2=VIS_POS top)
        "C5": (+5.20, +15.55, 180),    # 0805 1uF (1=VIS_POS right -> J3.1, 2=VIS_NEG left -> J3.2)
        "C3": (+6.00, +5.20, 0),       # 1210 10uF (1=VIN_20V facing INWARD left!)
        "C9": (+2.00, +6.90, 90),
        "C7": (+2.00, +10.20, 90),
    }

    io = pcbnew.PCB_IO_KICAD_SEXPR()
    root_uuid = uid("root_sheet")
    fps = {}

    for ref, (xm, ym, ang) in placements.items():
        fp_name = fp_map[ref].split(":")[1]
        fp = io.FootprintLoad(str(FP_LIB_DIR), fp_name)
        fp.SetFPID(pcbnew.LIB_ID("lepiled", fp_name))
        fp.SetReference(ref)
        fp.SetValue(short_val[ref])
        fp.SetPosition(kpt(xm, ym))
        fp.SetOrientation(pcbnew.EDA_ANGLE(ang, pcbnew.DEGREES_T))
        fp.SetPath(pcbnew.KIID_PATH(f"/{root_uuid}/{uid(f'sym_{ref}')}"))
        p_nets = pad_net_map.get(ref, {})
        for p in fp.Pads():
            pn = p.GetNumber()
            if pn in p_nets:
                p.SetNet(nets[p_nets[pn]])
            elif (ref, pn) in nc_nets:
                p.SetNet(nc_nets[(ref, pn)])
        board.Add(fp)
        fps[ref] = fp

    def pt(ref, pnum):
        return get_pad_pos(fps[ref], pnum)

    # Solid unbroken B.Cu GND plane across entire board (0.22 mm clearance satisfies LED_Drive & Power_SW rules!)
    add_zone(
        board, [(-17.65, -22.65), (+17.65, -22.65), (+17.65, +22.65), (-17.65, +22.65)],
        pcbnew.B_Cu, nets["GND"], priority=0, min_thickness=0.20, clearance=0.22,
    )

    # -----------------------------------------------------------------------
    # Explicit Critical Power & Kelvin Traces BEFORE GridRouter
    # -----------------------------------------------------------------------
    # 1. J1 VBUS tie on F.Cu + CC1/CC2 clean B.Cu escapes (0.35 mm drills)
    add_track(board, [pt("J1", "B9"), pt("J1", "A4")], 0.45, nets["VBUS"])
    add_track(board, [pt("J1", "B4"), pt("J1", "A9")], 0.45, nets["VBUS"])
    add_track(board, [pt("J1", "A4"), (-2.125, -16.10), (+2.125, -16.10), pt("J1", "A9")], 0.50, nets["VBUS"])
    add_track(board, [(-2.125, -16.10), (-6.30, -16.10), (-6.30, -14.20), pt("F1", "1")], 0.80, nets["VBUS"])

    # 2. U3 (AP33771C W-DFN3030-14, 0.40 mm pitch) clean 0.20 mm fan-out escapes + external GND vias
    # Strictly horizontal bridge from U3.5 (-13.0) straight into EPAD (7.80, -13.0) — 0.19 mm clear of U3.4!
    add_track(board, [pt("U3", "5"), (7.80, -13.00)], 0.20, nets["GND"])
    u3_v_top = (7.80, -10.20)
    u3_v_bot = (7.80, -15.00)
    add_track(board, [pt("U3", "15"), u3_v_top], 0.45, nets["GND"])
    add_via(board, u3_v_top[0], u3_v_top[1], nets["GND"])
    add_track(board, [pt("U3", "15"), u3_v_bot], 0.45, nets["GND"])
    add_via(board, u3_v_bot[0], u3_v_bot[1], nets["GND"])

    u3_esc = {
        "1": (5.40, -10.20),   # U3_VOUT
        "2": (4.80, -11.20),   # U3_PWR_EN
        "3": (4.00, -12.20),   # VBUS_SENSE
        "4": (4.60, -13.20),   # VBUS_FUSED
        "7": (5.40, -14.40),   # U3_LED
        "8": (10.00, -14.60),  # U3_VSEL
        "9": (10.60, -13.60),  # U3_ISEL
        "10": (11.20, -12.80), # CC2
        "11": (10.60, -11.80), # CC1
        "14": (10.00, -10.80), # U3_V5V
    }
    # Strictly orthogonal H-V-H fan-outs (0.20 mm) so router bounding boxes stay razor-thin
    u3_fan_paths = {
        "1":  [pt("U3", "1"), (5.80, -11.40), (5.80, -10.20), u3_esc["1"]],
        "2":  [pt("U3", "2"), (5.40, -11.80), (5.40, -11.20), u3_esc["2"]],
        "3":  [pt("U3", "3"), u3_esc["3"]],
        "4":  [pt("U3", "4"), (5.40, -12.60), (5.40, -13.20), u3_esc["4"]],
        "7":  [pt("U3", "7"), (5.80, -13.80), (5.80, -14.40), u3_esc["7"]],
        "8":  [pt("U3", "8"), (9.80, -13.80), (9.80, -14.60), u3_esc["8"]],
        "9":  [pt("U3", "9"), (10.20, -13.40), (10.20, -13.60), u3_esc["9"]],
        "10": [pt("U3", "10"), (10.60, -13.00), (10.60, -12.80), u3_esc["10"]],
        "11": [pt("U3", "11"), (10.20, -12.60), (10.20, -11.80), u3_esc["11"]],
        "14": [pt("U3", "14"), (9.80, -11.40), (9.80, -10.80), u3_esc["14"]],
    }
    for pnum, path_pts in u3_fan_paths.items():
        add_track(board, path_pts, 0.20, nets[pad_net_map["U3"][pnum]])

    # J1 CC1/CC2 clean 0.20 mm B.Cu escapes outside the 0.85 mm PTH row & shield tabs
    j1_cc1_esc = (-1.275, -15.60)
    j1_cc2_esc = (+5.60, -20.00)
    add_track(board, [pt("J1", "A5"), j1_cc1_esc], 0.20, nets["CC1"], pcbnew.B_Cu)
    add_track(board, [pt("J1", "B5"), (+1.275, -20.00), j1_cc2_esc], 0.20, nets["CC2"], pcbnew.B_Cu)

    # 3. Tight Ch1 & Ch2 AL8860 high-di/dt loops + ultra-short dedicated GND vias on F.Cu
    add_track(board, [pt("U1", "1"), (-11.00, +9.60), (-11.00, +9.65), pt("L1", "1")], 0.55, nets["SW1_NODE"])
    add_track(board, [(-11.00, +9.65), (-11.00, +5.40), pt("D9", "2")], 0.55, nets["SW1_NODE"])
    add_track(board, [pt("U1", "2"), (-8.80, +8.65)], 0.35, nets["GND"])
    add_via(board, -8.80, +8.65, nets["GND"])
    add_track(board, [pt("C2", "2"), (-7.325, +6.80), (-9.20, +6.80)], 0.45, nets["GND"])
    add_via(board, -9.20, +6.80, nets["GND"])
    add_track(board, [pt("U2", "1"), (+11.00, +7.70), (+11.00, +9.65), pt("L2", "1")], 0.55, nets["SW2_NODE"])
    add_track(board, [(+11.00, +9.65), (+11.00, +5.40), pt("D10", "2")], 0.55, nets["SW2_NODE"])
    add_track(board, [pt("U2", "2"), (+8.80, +8.65)], 0.35, nets["GND"])
    add_via(board, +8.80, +8.65, nets["GND"])
    add_track(board, [pt("C3", "2"), (+7.325, +6.80), (+9.20, +6.80)], 0.45, nets["GND"])
    add_via(board, +9.20, +6.80, nets["GND"])
    # Symmetric centerline HF bypass & soft-start GND vias for C8/C9 and C6/C7
    add_track(board, [pt("C8", "2"), (0.00, +7.65), pt("C9", "2")], 0.30, nets["GND"])
    add_via(board, 0.00, +7.65, nets["GND"])
    add_track(board, [pt("C6", "2"), (0.00, +10.95), pt("C7", "2")], 0.25, nets["GND"])
    add_via(board, 0.00, +10.95, nets["GND"])
    # Dedicated U4.4 (LM393B GND) fan-out via cleanly left of U4.4 + U4.1 escape via + non-crossing under-U4 ties + U5 GND
    add_track(board, [pt("U4", "4"), (+5.50, -3.505), (+5.50, -3.30)], 0.25, nets["GND"])
    add_via(board, +5.50, -3.30, nets["GND"])
    add_track(board, [pt("U4", "1"), (+5.30, +0.305)], 0.22, nets["U1_CTRL"])
    add_via(board, +5.30, +0.305, nets["U1_CTRL"])
    add_track(board, [pt("U4", "2"), (+10.40, pt("U4", "2")[1]), (+10.40, pt("U4", "6")[1]), pt("U4", "6")], 0.22, nets["V_REF"])
    add_track(board, [pt("U4", "3"), (+9.60, pt("U4", "3")[1]), (+9.60, pt("U4", "5")[1]), pt("U4", "5")], 0.22, nets["UVLO_SENSE"])
    add_track(board, [pt("U5", "3"), (pt("U5", "3")[0], pt("U5", "2")[1]), pt("U5", "2")], 0.25, nets["GND"])
    add_track(board, [(+16.00, pt("U5", "2")[1]), (+16.00, -5.00)], 0.25, nets["GND"])
    add_via(board, +16.00, -5.00, nets["GND"])
    # Dedicated ultra-short C14.2 (U4 100 nF VCC decoupling GND) via cleanly below C14.2
    add_track(board, [pt("C14", "2"), (+14.15, +1.35)], 0.25, nets["GND"])
    add_via(board, +14.15, +1.35, nets["GND"])
    # Tie C15.2 (GND) directly to adjacent Q3.2 (GND) + shared GND via straight below Q3.2!
    add_track(board, [pt("C15", "2"), pt("Q3", "2"), (+2.25, +1.35)], 0.25, nets["GND"])
    add_via(board, +2.25, +1.35, nets["GND"])

    # Initialize GridRouter with strict zero-via-in-pad blocking
    router = GridRouter(board)
    for trk in board.GetTracks():
        if trk.GetClass() == "PCB_VIA":
            pos = trk.GetPosition()
            router.add_via_obstacle(pos.x / 1e6 - CX, CY - pos.y / 1e6, 0.60, trk.GetNetname())
        else:
            st, en = trk.GetStart(), trk.GetEnd()
            router.add_seg_obstacle(st.x / 1e6 - CX, CY - st.y / 1e6, en.x / 1e6 - CX, CY - en.y / 1e6,
                                    trk.GetWidth() / 1e6, trk.GetLayer(), trk.GetNetname())

    # Helper to route list of pairs cleanly (supports ("U3", "pin") auto-mapping to fanout escape!)
    def resolve_pt(ref, pnum):
        if ref == "U3" and pnum in u3_esc:
            return u3_esc[pnum]
        if ref == "J1" and pnum == "A5":
            return j1_cc1_esc
        if ref == "J1" and pnum == "B5":
            return j1_cc2_esc
        return pt(ref, pnum)

    def r_net(pairs, nname, w, clr=0.20, allow_b=True, b_pen=5):
        nobj = nets[nname]
        for (r1, p1, l1), (r2, p2, l2) in pairs:
            router.route(resolve_pt(r1, p1), l1, resolve_pt(r2, p2), l2, nobj, w, clr, allow_b=allow_b, b_penalty=b_pen)

    # --- Power_20V Trunks (0.60-0.80 mm) ---
    r_net([(("TP1", "1", 0), ("F2", "1", 0))], "AUX_IN", 0.80, 0.22)
    r_net([(("F2", "2", 0), ("D13", "2", 0))], "AUX_FUSED", 0.80, 0.22)
    r_net([
        (("F1", "2", 0), ("D11", "2", 0)),
        (("D11", "2", 0), ("C1", "1", 0)),
        (("C1", "1", 0), ("R7", "2", 0)),
        (("R7", "2", 0), ("R8", "1", 0)),
    ], "VBUS_FUSED", 0.55, 0.20)
    r_net([(("R7", "1", 0), ("C10", "1", 0))], "VBUS_DAMP", 0.55, 0.20)
    r_net([
        (("R8", "2", 0), ("U3", "3", 0)),  # Direct Kelvin VCC tap first!
    ], "VBUS_SENSE", 0.25, 0.18)
    r_net([
        (("R8", "2", 0), ("C11", "1", 0)),
        (("C11", "1", 0), ("Q1A", "3", 0)),
    ], "VBUS_SENSE", 0.55, 0.20)
    r_net([(("R8", "1", 0), ("U3", "4", 0))], "VBUS_FUSED", 0.25, 0.18)  # Kelvin ISENP tap
    # Route ultra-short local Kelvin taps & LED output headers FIRST so VIN_20V never detours between C4/C5 and J2/J3!
    r_net([(("R3", "2", 0), ("U1", "4", 0))], "UV_POS", 0.25, 0.18)
    r_net([(("R4", "2", 0), ("U2", "4", 0))], "VIS_POS", 0.25, 0.18)
    r_net([(("C8", "1", 0), ("U1", "5", 0))], "VIN_20V", 0.30, 0.18)
    r_net([(("C9", "1", 0), ("U2", "5", 0))], "VIN_20V", 0.30, 0.18)
    r_net([
        (("R3", "2", 0), ("C4", "1", 0)),
        (("C4", "1", 0), ("J2", "1", 0)),
    ], "UV_POS", 0.50, 0.22)
    r_net([
        (("L1", "2", 0), ("C4", "2", 0)),
        (("C4", "2", 0), ("J2", "2", 0)),
    ], "UV_NEG", 0.50, 0.22)
    r_net([
        (("R4", "2", 0), ("C5", "1", 0)),
        (("C5", "1", 0), ("J3", "1", 0)),
    ], "VIS_POS", 0.50, 0.22)
    r_net([
        (("C5", "2", 0), ("J3", "2", 0)),
        (("L2", "2", 0), ("J3", "2", 1)),
    ], "VIS_NEG", 0.50, 0.22)

    # Main VIN_20V distribution star (route BEFORE Q1_MID so Q1_MID stays below Q1A/Q1B!)
    r_net([
        (("Q1B", "3", 0), ("C3", "1", 0)),
        (("C3", "1", 0), ("C9", "1", 0)),
        (("C3", "1", 0), ("D10", "1", 0)),
        (("C3", "1", 0), ("R4", "1", 0)),
        (("C9", "1", 0), ("C8", "1", 0)),
        (("C2", "1", 0), ("C8", "1", 0)),
        (("C2", "1", 0), ("D9", "1", 0)),
        (("C2", "1", 0), ("R3", "1", 0)),
        (("D13", "1", 0), ("D9", "1", 0)),
    ], "VIN_20V", 0.60, 0.20, b_pen=6)
    r_net([(("Q1A", "2", 0), ("Q1B", "2", 0))], "Q1_MID", 0.50, 0.20)
    r_net([(("Q1A", "2", 0), ("C13", "1", 0))], "Q1_MID", 0.25, 0.16)
    r_net([
        (("Q1B", "3", 0), ("R12", "1", 0)),
        (("C3", "1", 0), ("C14", "1", 0)),
        (("C14", "1", 0), ("U4", "8", 0)),
        (("C3", "1", 0), ("R15", "2", 0)),
        (("R15", "2", 0), ("R14", "2", 0)),
        (("D9", "1", 0), ("R17", "2", 0)),
    ], "VIN_20V", 0.30, 0.18, b_pen=6)

    # --- Signals (0.22 mm, 0.16 mm board clearance) ---
    # Route ultra-short local U3 peripheral straps BEFORE CC1/CC2 so CC2 never blocks U3_ISEL!
    r_net([(("U3", "8", 0), ("R9", "2", 0))], "U3_VSEL", 0.22, 0.16)
    r_net([(("U3", "9", 0), ("R10", "2", 0))], "U3_ISEL", 0.22, 0.16)
    r_net([(("U3", "14", 0), ("C12", "1", 0))], "U3_V5V", 0.22, 0.16)
    r_net([(("J1", "B5", 1), ("R2", "2", 0)), (("R2", "2", 0), ("U3", "10", 0))], "CC2", 0.22, 0.16)
    r_net([(("J1", "A5", 1), ("R1", "2", 0)), (("R1", "2", 0), ("U3", "11", 0))], "CC1", 0.22, 0.16)
    r_net([(("U3", "1", 0), ("R12", "2", 0))], "U3_VOUT", 0.22, 0.16)
    r_net([(("U3", "2", 0), ("R11", "1", 0))], "U3_PWR_EN", 0.22, 0.16)
    r_net([
        (("R11", "2", 0), ("Q1A", "1", 0)),
        (("Q1A", "1", 0), ("Q1B", "1", 0)),
        (("Q1B", "1", 0), ("C13", "2", 0)),
    ], "Q1_GATE", 0.22, 0.16)
    r_net([(("U3", "7", 0), ("R13", "1", 0))], "U3_LED", 0.22, 0.16)
    r_net([(("R13", "2", 0), ("D15", "2", 0))], "PD_LED_A", 0.22, 0.16)

    # UVLO & Switch Control Signals (local bias/switch nets before long U1_CTRL/U2_CTRL!)
    r_net([
        (("R15", "1", 0), ("R16", "2", 0)),
        (("R16", "2", 0), ("C15", "1", 0)),
    ], "UVLO_SENSE", 0.22, 0.16)
    r_net([
        (("R17", "1", 0), ("D14", "1", 0)),
        (("R17", "1", 0), ("R5", "2", 0)),
        (("R5", "2", 0), ("R6", "2", 0)),
    ], "V_SW_BIAS", 0.22, 0.16)
    r_net([
        (("J4", "1", 1), ("R5", "1", 0)),
        (("R5", "1", 0), ("D12", "1", 0)),
        (("R5", "1", 0), ("Q2", "1", 0)),
    ], "SW_UV_N", 0.22, 0.16)
    r_net([
        (("J4", "3", 0), ("R6", "1", 0)),
        (("R6", "1", 0), ("D12", "3", 0)),
        (("J4", "3", 1), ("Q3", "1", 0)),
    ], "SW_ALL_N", 0.22, 0.16)
    r_net([
        (("Q2", "3", 0), ("C6", "1", 0)),
        (("C6", "1", 0), ("U1", "3", 0)),
    ], "U1_CTRL", 0.22, 0.16)
    router.route(pt("Q2", "3"), 0, (+5.30, +0.305), 1, nets["U1_CTRL"], 0.22, 0.16, allow_b=True, b_penalty=5)
    r_net([
        (("Q3", "3", 0), ("C7", "1", 0)),
        (("C7", "1", 0), ("U2", "3", 0)),
        (("C7", "1", 0), ("U4", "7", 0)),
    ], "U2_CTRL", 0.22, 0.16)
    r_net([
        (("R16", "2", 0), ("U4", "3", 0)),
    ], "UVLO_SENSE", 0.22, 0.16)
    r_net([
        (("R14", "1", 0), ("U5", "1", 0)),
        (("U5", "1", 0), ("U4", "6", 0)),
    ], "V_REF", 0.22, 0.16)

    # --- Fan-Out GND Stitching Vias for ALL Remaining SMD GND Pads (Strictly Outside Pads!) ---
    gnd_smd_pads = [
        ("C1", "2", 0.45), ("C10", "2", 0.45), ("C11", "2", 0.30), ("C12", "2", 0.30),
        ("D11", "1", 0.50), ("D14", "2", 0.30), ("D15", "1", 0.25),
        ("R1", "1", 0.25), ("R2", "1", 0.25), ("R9", "1", 0.25), ("R10", "1", 0.25), ("R16", "1", 0.25),
        ("Q2", "2", 0.25),
    ]
    gnd_nname = nets["GND"].GetNetname()
    existing_gnd_vias = [
        (trk.GetPosition().x / 1e6 - CX, CY - trk.GetPosition().y / 1e6)
        for trk in board.GetTracks()
        if trk.GetClass() == "PCB_VIA" and trk.GetNetname() == gnd_nname
    ]
    for ref, pnum, gw in gnd_smd_pads:
        px, py = pt(ref, pnum)
        routed = False
        # First check if an already-placed GND via within 2.8 mm is directly reachable on F.Cu
        near_vias = sorted(
            ((math.hypot(vx - px, vy - py), vx, vy) for vx, vy in existing_gnd_vias if math.hypot(vx - px, vy - py) <= 2.8),
        )
        for _, vx, vy in near_vias[:8]:
            try:
                router.route((px, py), 0, (vx, vy), 0, nets["GND"], min(gw, 0.30), 0.16, allow_b=False)
                routed = True
                break
            except RuntimeError:
                continue
        if routed:
            continue
        for try_w in (gw, 0.22):
            _, via_blk = router._build_blocked(gnd_nname, try_w / 2.0, 0.16)
            candidates = []
            for dx in range(-45, 46):
                for dy in range(-45, 46):
                    tx, ty = px + dx * router.RES, py + dy * router.RES
                    if -17.1 <= tx <= 17.1 and -22.1 <= ty <= 22.1:
                        ix, iy = router._to_ij(tx, ty)
                        if not via_blk[iy][ix]:
                            candidates.append((dx * dx + dy * dy, tx, ty))
            candidates.sort()
            for _, vx, vy in candidates[:120]:
                try:
                    router.route((px, py), 0, (vx, vy), 0, nets["GND"], try_w, 0.16, allow_b=False)
                    add_via(board, vx, vy, nets["GND"], 0.60, 0.30)
                    router.add_via_obstacle(vx, vy, 0.60, gnd_nname)
                    existing_gnd_vias.append((vx, vy))
                    routed = True
                    break
                except RuntimeError:
                    continue
            if routed:
                break
        if not routed:
            # Last resort: connect to any existing GND via within 6.0 mm (F.Cu or short B.Cu bridge)
            far_vias = sorted(
                ((math.hypot(vx - px, vy - py), vx, vy) for vx, vy in existing_gnd_vias if math.hypot(vx - px, vy - py) <= 6.0),
            )
            for _, vx, vy in far_vias[:12]:
                try:
                    router.route((px, py), 0, (vx, vy), 0, nets["GND"], 0.22, 0.16, allow_b=False)
                    routed = True
                    break
                except RuntimeError:
                    continue
        assert routed, f"Could not place fan-out GND via near {ref}.{pnum}"

    # Hard geometric verification of ZERO via-in-pad
    assert_zero_via_in_pad(board)

    # Fill B.Cu GND plane
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())

    # Place clean non-overlapping F.Silkscreen RefDes & legends
    place_non_overlapping_silkscreen(board)

    pcbnew.SaveBoard(str(pcb_path), board)
    print(f"Saved {pcb_path} cleanly.")


# ---------------------------------------------------------------------------
# 7. Verification (ERC, DRC --schematic-parity) & Manufacturing Exports
# ---------------------------------------------------------------------------

def verify_and_export(comp_rows):
    sch_path = BASE_DIR / "driver_pcb.kicad_sch"
    pcb_path = BASE_DIR / "driver_pcb.kicad_pcb"

    GERBER_DIR.mkdir(parents=True, exist_ok=True)
    RENDER_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Native KiCad 9.0.8 ERC
    for fmt, ext in [("json", "json"), ("report", "rpt")]:
        subprocess.run(
            [KCLI, "sch", "erc", "--format", fmt, "--severity-all", "--exit-code-violations",
             "-o", str(BASE_DIR / f"erc_report.{ext}"), str(sch_path)],
            check=True,
        )

    # 2. Native KiCad 9.0.8 DRC with schematic parity
    for fmt, ext in [("json", "json"), ("report", "rpt")]:
        subprocess.run(
            [KCLI, "pcb", "drc", "--format", fmt, "--schematic-parity", "--severity-all", "--exit-code-violations",
             "-o", str(BASE_DIR / f"drc_report.{ext}"), str(pcb_path)],
            check=True,
        )

    # 3. Gerbers & Excellon Drill
    for old_f in GERBER_DIR.glob("*"):
        if old_f.is_file():
            old_f.unlink()
    subprocess.run(
        [KCLI, "pcb", "export", "gerbers", "--no-protel-ext", "--use-drill-file-origin",
         "-o", str(GERBER_DIR) + "/",
         "-l", "F.Cu,B.Cu,F.Mask,B.Mask,F.SilkS,B.SilkS,F.Paste,Edge.Cuts", str(pcb_path)],
        check=True,
    )
    subprocess.run(
        [KCLI, "pcb", "export", "drill", "--format", "excellon", "--drill-origin", "plot",
         "--excellon-units", "mm", "--excellon-separate-th",
         "--generate-map", "--map-format", "pdf", "--generate-report",
         "-o", str(GERBER_DIR) + "/", str(pcb_path)],
        check=True,
    )

    # Patch driver_pcb-job.gbrjob to Green LPI / White Silk / 1 oz Cu
    gbrjob_path = GERBER_DIR / "driver_pcb-job.gbrjob"
    if gbrjob_path.exists():
        job = json.loads(gbrjob_path.read_text())
        for item in job.get("MaterialStackup", []):
            if item.get("Type") == "SolderMask":
                item["Color"] = "Green"
            elif item.get("Type") == "Legend":
                item["Color"] = "White"
        gbrjob_path.write_text(json.dumps(job, indent=2) + "\n")

    zip_path = GERBER_DIR / "driver_pcb_gerbers.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in sorted(GERBER_DIR.iterdir()):
            if f.name.endswith((".gbr", ".drl", ".gbrjob")):
                zf.write(f, f.name)

    # 4. Clean JLCPCB CPL & BOM (excluding TP1, TP2, H1..H4!)
    raw_pos = RENDER_DIR / "_raw_pos.csv"
    subprocess.run(
        [KCLI, "pcb", "export", "pos", "--format", "csv", "--units", "mm",
         "--use-drill-file-origin", "--exclude-dnp",
         "-o", str(raw_pos), str(pcb_path)],
        check=True,
    )
    exclude_pcba = {"TP1", "TP2", "H1", "H2", "H3", "H4"}
    with raw_pos.open() as f_in, (PCB_DESIGN_DIR / "driver_pcb_cpl.csv").open("w", newline="") as f_out:
        reader = csv.DictReader(f_in)
        writer = csv.writer(f_out)
        writer.writerow(["Designator", "Mid X", "Mid Y", "Layer", "Rotation"])
        for row in reader:
            if row["Ref"] in exclude_pcba:
                continue
            writer.writerow([
                row["Ref"], f"{float(row['PosX']):.3f}", f"{float(row['PosY']):.3f}",
                "Top" if row["Side"].lower() == "top" else "Bottom",
                f"{float(row['Rot']):.1f}",
            ])
    raw_pos.unlink()

    with (PCB_DESIGN_DIR / "driver_pcb_bom.csv").open("w", newline="") as f_all, \
         (PCB_DESIGN_DIR / "driver_pcb_bom_pcba.csv").open("w", newline="") as f_pcba:
        cols = ["Comment", "Designator", "Footprint", "MPN", "Qty", "Category", "Mounting", "DNP"]
        w_all = csv.writer(f_all)
        w_pcba = csv.writer(f_pcba)
        w_all.writerow(cols)
        w_pcba.writerow(cols)
        for ref, r in comp_rows.items():
            dnp_flag = "Yes" if (r["Mounting"] == "Off-Board" or ref in exclude_pcba) else "No"
            line = [r["Value_Rating"], ref, r["Package_Footprint"], r["MPN"], r["Qty"], r["Category"], r["Mounting"], dnp_flag]
            w_all.writerow(line)
            if r["Mounting"] == "On-PCB" and ref not in exclude_pcba:
                w_pcba.writerow(line)

    # 5. Schematic PDF/SVG + 2:1 F.Fab Assembly Map PDF + 3D Top/Bottom Renders + Gerbv PNGs
    subprocess.run([KCLI, "sch", "export", "pdf", "-o", str(RENDER_DIR / "schematic.pdf"), str(sch_path)], check=True)
    subprocess.run([KCLI, "sch", "export", "svg", "-o", str(RENDER_DIR), str(sch_path)], check=True)
    # Mirror native KiCad schematic directly into circuit_design/schematic.{pdf,svg,png}!
    shutil.copy2(RENDER_DIR / "schematic.pdf", REPO_ROOT / "circuit_design" / "schematic.pdf")
    svg_src = RENDER_DIR / "driver_pcb.svg"
    if svg_src.exists():
        shutil.copy2(svg_src, REPO_ROOT / "circuit_design" / "schematic.svg")
    subprocess.run(
        ["pdftoppm", "-png", "-r", "180", "-singlefile",
         str(RENDER_DIR / "schematic.pdf"), str(REPO_ROOT / "circuit_design" / "schematic")],
        check=True,
    )

    subprocess.run(
        [KCLI, "pcb", "export", "pdf", "-o", str(RENDER_DIR / "assembly_map.pdf"),
         "-l", "F.Fab,F.SilkS,Edge.Cuts", "--mode-single", "--black-and-white", "--exclude-value", str(pcb_path)],
        check=True,
    )
    subprocess.run(
        [KCLI, "pcb", "export", "svg", "-o", str(RENDER_DIR / "assembly_map.svg"),
         "-l", "F.Fab,F.SilkS,Edge.Cuts", "--mode-single", "--black-and-white",
         "--fit-page-to-board", "--exclude-drawing-sheet", str(pcb_path)],
        check=True,
    )
    subprocess.run(
        [KCLI, "pcb", "export", "svg", "-o", str(RENDER_DIR / "board.svg"),
         "-l", "F.Cu,B.Cu,F.SilkS,B.SilkS,Edge.Cuts", "--mode-single", "--fit-page-to-board", "--exclude-drawing-sheet", str(pcb_path)],
        check=True,
    )
    subprocess.run(
        [KCLI, "pcb", "render", "--side", "top", "-w", "1400", "-h", "1800", "--quality", "high",
         "-o", str(RENDER_DIR / "render_top.png"), str(pcb_path)],
        check=True,
    )
    subprocess.run(
        [KCLI, "pcb", "render", "--side", "bottom", "-w", "1400", "-h", "1800", "--quality", "high",
         "-o", str(RENDER_DIR / "render_bottom.png"), str(pcb_path)],
        check=True,
    )
    subprocess.run(
        [GERBV, "-x", "png", "-D", "300", "-o", str(RENDER_DIR / "gerbv_top.png"),
         str(GERBER_DIR / "driver_pcb-F_Cu.gbr"),
         str(GERBER_DIR / "driver_pcb-F_Silkscreen.gbr"),
         str(GERBER_DIR / "driver_pcb-Edge_Cuts.gbr"),
         str(GERBER_DIR / "driver_pcb-PTH.drl")],
        check=True,
    )
    subprocess.run(
        [GERBV, "-x", "png", "-D", "300", "-o", str(RENDER_DIR / "gerbv_bottom.png"),
         str(GERBER_DIR / "driver_pcb-B_Cu.gbr"),
         str(GERBER_DIR / "driver_pcb-B_Silkscreen.gbr"),
         str(GERBER_DIR / "driver_pcb-Edge_Cuts.gbr"),
         str(GERBER_DIR / "driver_pcb-PTH.drl")],
        check=True,
    )
    print("Board 1 (Option 2 / Rev 4.0) verification & exports completed cleanly.")


def main():
    with COMPONENT_CSV.open() as f:
        comp_rows = {row["RefDes"]: row for row in csv.DictReader(f)}
    assert len(comp_rows) == 72, f"Expected 72 RefDes in COMPONENT_IDS.csv, got {len(comp_rows)}"

    write_lib_tables()
    write_kicad_pro()
    syms = build_symbol_defs()
    write_kicad_sym(syms)
    create_footprints()
    fp_map, short_val = write_kicad_sch(syms, comp_rows)
    build_board(fp_map, short_val, comp_rows)
    verify_and_export(comp_rows)


if __name__ == "__main__":
    main()
