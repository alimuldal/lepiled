#!/usr/bin/env python3
"""
Reproducible KiCad 9 generator for Board 2: Aluminum MCPCB Dual-LED Strip (MECH-MCPCB-1..4).
- 20.0 x 80.0 mm, 1.0 mm corner radii, 1.6 mm 1-layer Al MCPCB (1.0 W/m*K, 1 oz F.Cu ONLY).
- Zero B.Cu, zero vias, zero PTH holes.
- MH1, MH2 at (0, +32.0) and (0, -32.0) mm: 3.2 mm NPTH, 6.0 mm head keepout.
- D_UV (Luminus SST-10-UV-A130) at (0, +18.0) mm; D_VIS (Cree XP-E2) at (0, -18.0) mm.
- Opposite bottom thermal-pad notch polarity cues documented on F.Silkscreen.
- Custom-polygon electrically isolated thermal center pad copper pours with strict SMD mask openings.
- 4 wire solder pads (UV+, VIS+, VIS-, UV-) at y = -26.0 mm clear of MH2 keepout.
"""

import csv
import json
import math
import os
import shutil
import subprocess
import uuid
import zipfile
from pathlib import Path

import pcbnew

BASE_DIR = Path(__file__).resolve().parent
PCB_DESIGN_DIR = BASE_DIR.parent
GERBER_DIR = PCB_DESIGN_DIR / "gerbers" / "led_mcpcb"
RENDER_DIR = BASE_DIR / "renders"
FP_LIB_DIR = BASE_DIR / "lepiled_mcpcb.pretty"

# Board coordinates: center at (100.0, 100.0) in KiCad sheet space.
# Math coords (x_m, y_m) with +Y UP map to KiCad (100.0 + x_m, 100.0 - y_m).
CX, CY = 100.0, 100.0


def uid(name: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"lepiled-mcpcb-{name}"))


def mm(val: float) -> int:
    return pcbnew.FromMM(val)


def kpt(xm: float, ym: float) -> pcbnew.VECTOR2I:
    return pcbnew.VECTOR2I(mm(CX + xm), mm(CY - ym))


def lpt(xm: float, ym: float) -> pcbnew.VECTOR2I:
    """Footprint-local point (math coords +Y up -> KiCad +Y down)."""
    return pcbnew.VECTOR2I(mm(xm), mm(-ym))


def lset(*layers) -> pcbnew.LSET:
    s = pcbnew.LSET()
    for lyr in layers:
        s.addLayer(lyr)
    return s


def polygon_area(pts_xy):
    area = 0.0
    n = len(pts_xy)
    for i in range(n):
        x1, y1 = pts_xy[i]
        x2, y2 = pts_xy[(i + 1) % n]
        area += x1 * y2 - x2 * y1
    return abs(area) * 0.5


def make_rect_poly(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def add_poly_to_custom_pad(pad: pcbnew.PAD, pts_xy):
    poly = pcbnew.SHAPE_POLY_SET()
    poly.NewOutline()
    for x, y in pts_xy:
        poly.Append(lpt(x, y))
    pad.AddPrimitivePoly(pcbnew.F_Cu, poly, 0, True)


def build_uv_thermal_poly():
    """Contiguous H-shaped isolated thermal copper pour around D_UV at (0, +18.0), local coords."""
    # D_UV is at (0, +18.0). Local (0,0) = (0, +18.0) on board.
    # MH1 is at local (0, +14.0). Board top is local +22.0, bottom is -58.0.
    # Upper wing: y in [+2.3, +21.3], x in [-9.2, +9.2], notched around MH1 (0, +14.0) R=3.5mm
    #Wait: keep a clean polygonal cutout around MH1!
    pts = []
    # Start at center neck bottom-left (-0.65, -1.65), go down to lower wing
    # Lower wing: y in [-17.0, -2.35], x in [-7.2, +7.2]
    pts.extend([
        (-0.65, -2.35),
        (-7.20, -2.35),
        (-7.20, -17.00),
        (+7.20, -17.00),
        (+7.20, -2.35),
        (+0.65, -2.35),
        # Pass through center thermal neck (x in [-0.65, +0.65], y in [-2.35, +2.35])
        (+0.65, +2.35),
        (+9.20, +2.35),
        (+9.20, +20.60),
        (+8.40, +21.30),
        (+4.10, +21.30),
        (+4.10, +17.50),
    ])
    # Carve MH1 at (0, +14.0) with R=4.10 mm (>= 4.0 mm screw-head & dielectric clearance!)
    pts.pop()  # remove (+4.10, +17.5)
    for deg in range(0, -181, -15):
        rad = math.radians(deg)
        pts.append((4.10 * math.cos(rad), 14.0 + 4.10 * math.sin(rad)))
    pts.extend([
        (-4.10, +21.30),
        (-8.40, +21.30),
        (-9.20, +20.60),
        (-9.20, +2.35),
        (-0.65, +2.35),
    ])
    return pts


def build_vis_thermal_poly():
    """Contiguous isolated thermal copper pour around D_VIS at (0, -18.0), local coords."""
    # D_VIS is at (0, -18.0). Local y=+17.5 is board y=-0.5. Local y=-5.0 is board y=-23.0.
    # D_VIS pads: Anode (-1.40, 0) 0.50x3.30, Thermal (0,0) 1.30x3.30, Cathode (+1.40, 0) 0.50x3.30.
    # VIS+/VIS- traces exit downward from y = -1.65 to (-2.25, -8.0).
    # So thermal copper covers:
    # - Top wing: x in [-7.2, +7.2], y in [+2.35, +17.2]
    # - Left wing: x in [-7.2, -2.35], y in [-4.5, +2.35] (slanted clear of VIS+ trace at x=-2.65 below y=-1.65 -> keep x <= -3.35 for y < -1.0)
    # Wait: keep it super clean and symmetric above y = +2.35 plus side ears down to y = -4.2 at x in [3.4, 7.2] & [-7.2, -3.4]!
    pts = [
        (-0.65, -1.65),
        (+0.65, -1.65),
        (+0.65, +2.35),
        (+2.30, +2.35),
        (+2.30, -1.65),
        (+3.40, -1.65),
        (+3.40, -3.60),
        (+7.20, -3.60),
        (+7.20, +17.20),
        (-7.20, +17.20),
        (-7.20, -3.60),
        (-3.40, -3.60),
        (-3.40, -1.65),
        (-2.30, -1.65),
        (-2.30, +2.35),
        (-0.65, +2.35),
    ]
    return pts


def create_footprints():
    FP_LIB_DIR.mkdir(parents=True, exist_ok=True)
    io = pcbnew.PCB_IO_KICAD_SEXPR()

    # 1. LED_Luminus_SST-10-UV_A130
    fp_uv = pcbnew.FOOTPRINT(None)
    fp_uv.SetReference("D_UV")
    fp_uv.SetValue("SST-10-UV-A130-G365-00")
    fp_uv.SetFPID(pcbnew.LIB_ID("lepiled_mcpcb", "LED_Luminus_SST-10-UV_A130"))
    fp_uv.SetAttributes(pcbnew.FP_SMD)

    # Pad 1: Anode (-1.385, 0), 0.48 x 3.25 mm
    p1 = pcbnew.PAD(fp_uv)
    p1.SetNumber("1")
    p1.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
    p1.SetShape(pcbnew.PAD_SHAPE_RECT)
    p1.SetPosition(lpt(-1.385, 0.0))
    p1.SetSize(pcbnew.VECTOR2I(mm(0.48), mm(3.25)))
    p1.SetLayerSet(lset(pcbnew.F_Cu, pcbnew.F_Mask, pcbnew.F_Paste))
    p1.SetLocalSolderMaskMargin(mm(0.05))
    fp_uv.Add(p1)

    # Pad 2: Cathode (+1.385, 0), 0.48 x 3.25 mm
    p2 = pcbnew.PAD(fp_uv)
    p2.SetNumber("2")
    p2.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
    p2.SetShape(pcbnew.PAD_SHAPE_RECT)
    p2.SetPosition(lpt(+1.385, 0.0))
    p2.SetSize(pcbnew.VECTOR2I(mm(0.48), mm(3.25)))
    p2.SetLayerSet(lset(pcbnew.F_Cu, pcbnew.F_Mask, pcbnew.F_Paste))
    p2.SetLocalSolderMaskMargin(mm(0.05))
    fp_uv.Add(p2)

    # Pad 3 (SMD opening strictly 1.30 x 3.25 mm; F.Paste segmented below per Luminus p. 10)
    p3_smd = pcbnew.PAD(fp_uv)
    p3_smd.SetNumber("3")
    p3_smd.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
    p3_smd.SetShape(pcbnew.PAD_SHAPE_RECT)
    p3_smd.SetPosition(lpt(0.0, 0.0))
    p3_smd.SetSize(pcbnew.VECTOR2I(mm(1.30), mm(3.25)))
    p3_smd.SetLayerSet(lset(pcbnew.F_Cu, pcbnew.F_Mask))
    p3_smd.SetLocalSolderMaskMargin(mm(0.0))
    fp_uv.Add(p3_smd)

    # Segmented F.Paste on D_UV thermal pad: 3 x (1.15 x 0.75 mm) = 61.2% coverage
    for py_off in (-1.00, 0.00, +1.00):
        pp = pcbnew.PAD(fp_uv)
        pp.SetNumber("")
        pp.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
        pp.SetShape(pcbnew.PAD_SHAPE_RECT)
        pp.SetPosition(lpt(0.0, py_off))
        pp.SetSize(pcbnew.VECTOR2I(mm(1.15), mm(0.75)))
        pp.SetLayerSet(lset(pcbnew.F_Paste))
        fp_uv.Add(pp)

    # Pad 3 (Custom thermal heat-spreading copper pour, F.Cu ONLY -> SMD-masked outside 1.30x3.25!)
    p3_wing = pcbnew.PAD(fp_uv)
    p3_wing.SetNumber("3")
    p3_wing.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
    p3_wing.SetShape(pcbnew.PAD_SHAPE_CUSTOM)
    p3_wing.SetPosition(lpt(0.0, 0.0))
    p3_wing.SetSize(pcbnew.VECTOR2I(mm(1.20), mm(3.00)))
    p3_wing.SetAnchorPadShape(pcbnew.F_Cu, pcbnew.PAD_SHAPE_RECT)
    uv_poly = build_uv_thermal_poly()
    add_poly_to_custom_pad(p3_wing, uv_poly)
    p3_wing.SetLayerSet(lset(pcbnew.F_Cu))
    fp_uv.Add(p3_wing)

    # Silkscreen outline & polarity cues (outside 3.45x3.45 body and pads!)
    # Body is [-1.725, +1.725] x [-1.725, +1.725]
    for x0, y0, x1, y1 in [
        (-2.10, +2.05, +2.10, +2.05),
        (-2.10, -2.05, +2.10, -2.05),
        (-2.10, -2.05, -2.10, +2.05),
        (+2.10, -2.05, +2.10, +2.05),
    ]:
        seg = pcbnew.PCB_SHAPE(fp_uv)
        seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
        seg.SetLayer(pcbnew.F_SilkS)
        seg.SetWidth(mm(0.15))
        seg.SetStart(lpt(x0, y0))
        seg.SetEnd(lpt(x1, y1))
        fp_uv.Add(seg)

    # Anode pin-1 dot on left (-X)
    dot = pcbnew.PCB_SHAPE(fp_uv)
    dot.SetShape(pcbnew.SHAPE_T_CIRCLE)
    dot.SetLayer(pcbnew.F_SilkS)
    dot.SetWidth(mm(0.15))
    dot.SetFilled(True)
    dot.SetCenter(lpt(-2.55, +1.20))
    dot.SetEnd(lpt(-2.30, +1.20))
    fp_uv.Add(dot)

    # Courtyard
    for x0, y0, x1, y1 in [
        (-2.30, +2.25, +2.30, +2.25),
        (-2.30, -2.25, +2.30, -2.25),
        (-2.30, -2.25, -2.30, +2.25),
        (+2.30, -2.25, +2.30, +2.25),
    ]:
        seg = pcbnew.PCB_SHAPE(fp_uv)
        seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
        seg.SetLayer(pcbnew.F_CrtYd)
        seg.SetWidth(mm(0.05))
        seg.SetStart(lpt(x0, y0))
        seg.SetEnd(lpt(x1, y1))
        fp_uv.Add(seg)

    # Fab outline & polarity notch cue on F.Fab (semicircle notch facing Cathode +X)
    for x0, y0, x1, y1 in [
        (-1.725, +1.725, +1.725, +1.725),
        (-1.725, -1.725, +1.725, -1.725),
        (-1.725, -1.725, -1.725, +1.725),
        (+1.725, -1.725, +1.725, +1.725),
    ]:
        seg = pcbnew.PCB_SHAPE(fp_uv)
        seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
        seg.SetLayer(pcbnew.F_Fab)
        seg.SetWidth(mm(0.10))
        seg.SetStart(lpt(x0, y0))
        seg.SetEnd(lpt(x1, y1))
        fp_uv.Add(seg)

    # Text labels on SilkS (clear of pads)
    fp_uv.Reference().SetPosition(lpt(0.0, +3.10))
    fp_uv.Reference().SetTextSize(pcbnew.VECTOR2I(mm(1.0), mm(1.0)))
    fp_uv.Reference().SetTextThickness(mm(0.15))
    fp_uv.Value().SetPosition(lpt(0.0, -3.20))
    fp_uv.Value().SetLayer(pcbnew.F_Fab)
    fp_uv.Value().SetTextSize(pcbnew.VECTOR2I(mm(0.8), mm(0.8)))

    for txt_str, tx, ty in [("A+", -3.30, 0.0), ("K-", +3.30, 0.0), ("BTM NOTCH=K", 0.0, -3.10)]:
        t = pcbnew.PCB_TEXT(fp_uv)
        t.SetText(txt_str)
        t.SetLayer(pcbnew.F_SilkS)
        t.SetPosition(lpt(tx, ty))
        t.SetTextSize(pcbnew.VECTOR2I(mm(0.85), mm(0.85)))
        t.SetTextThickness(mm(0.15))
        fp_uv.Add(t)

    io.FootprintSave(str(FP_LIB_DIR), fp_uv)

    # 2. LED_Cree_XP-E2
    fp_vis = pcbnew.FOOTPRINT(None)
    fp_vis.SetReference("D_VIS")
    fp_vis.SetValue("XP-E2")
    fp_vis.SetFPID(pcbnew.LIB_ID("lepiled_mcpcb", "LED_Cree_XP-E2"))
    fp_vis.SetAttributes(pcbnew.FP_SMD)

    p1 = pcbnew.PAD(fp_vis)
    p1.SetNumber("1")
    p1.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
    p1.SetShape(pcbnew.PAD_SHAPE_RECT)
    p1.SetPosition(lpt(-1.40, 0.0))
    p1.SetSize(pcbnew.VECTOR2I(mm(0.50), mm(3.30)))
    p1.SetLayerSet(lset(pcbnew.F_Cu, pcbnew.F_Mask))
    p1.SetLocalSolderMaskMargin(mm(0.05))
    fp_vis.Add(p1)

    p2 = pcbnew.PAD(fp_vis)
    p2.SetNumber("2")
    p2.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
    p2.SetShape(pcbnew.PAD_SHAPE_RECT)
    p2.SetPosition(lpt(+1.40, 0.0))
    p2.SetSize(pcbnew.VECTOR2I(mm(0.50), mm(3.30)))
    p2.SetLayerSet(lset(pcbnew.F_Cu, pcbnew.F_Mask))
    p2.SetLocalSolderMaskMargin(mm(0.05))
    fp_vis.Add(p2)

    # Segmented electrode F.Paste on D_VIS A/K pads: 5 x (0.48 x 0.44 mm) = 64.0% coverage (Cree p. 39, fixes Opus B-L6)
    for px_el in (-1.40, +1.40):
        for py_el in (-1.30, -0.65, 0.00, +0.65, +1.30):
            ppe = pcbnew.PAD(fp_vis)
            ppe.SetNumber("")
            ppe.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
            ppe.SetShape(pcbnew.PAD_SHAPE_RECT)
            ppe.SetPosition(lpt(px_el, py_el))
            ppe.SetSize(pcbnew.VECTOR2I(mm(0.48), mm(0.44)))
            ppe.SetLayerSet(lset(pcbnew.F_Paste))
            fp_vis.Add(ppe)

    p3_smd = pcbnew.PAD(fp_vis)
    p3_smd.SetNumber("3")
    p3_smd.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
    p3_smd.SetShape(pcbnew.PAD_SHAPE_RECT)
    p3_smd.SetPosition(lpt(0.0, 0.0))
    p3_smd.SetSize(pcbnew.VECTOR2I(mm(1.30), mm(3.30)))
    p3_smd.SetLayerSet(lset(pcbnew.F_Cu, pcbnew.F_Mask))
    p3_smd.SetLocalSolderMaskMargin(mm(0.0))
    fp_vis.Add(p3_smd)

    # Segmented windowpane F.Paste on D_VIS thermal pad: 2x3 x (0.50 x 0.90 mm) = 62.9% coverage (Cree p. 39)
    for px_off in (-0.34, +0.34):
        for py_off in (-1.05, 0.00, +1.05):
            pp = pcbnew.PAD(fp_vis)
            pp.SetNumber("")
            pp.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
            pp.SetShape(pcbnew.PAD_SHAPE_RECT)
            pp.SetPosition(lpt(px_off, py_off))
            pp.SetSize(pcbnew.VECTOR2I(mm(0.50), mm(0.90)))
            pp.SetLayerSet(lset(pcbnew.F_Paste))
            fp_vis.Add(pp)

    p3_wing = pcbnew.PAD(fp_vis)
    p3_wing.SetNumber("3")
    p3_wing.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
    p3_wing.SetShape(pcbnew.PAD_SHAPE_CUSTOM)
    p3_wing.SetPosition(lpt(0.0, 0.0))
    p3_wing.SetSize(pcbnew.VECTOR2I(mm(1.20), mm(3.00)))
    p3_wing.SetAnchorPadShape(pcbnew.F_Cu, pcbnew.PAD_SHAPE_RECT)
    vis_poly = build_vis_thermal_poly()
    add_poly_to_custom_pad(p3_wing, vis_poly)
    p3_wing.SetLayerSet(lset(pcbnew.F_Cu))
    fp_vis.Add(p3_wing)

    for x0, y0, x1, y1 in [
        (-2.10, +2.05, +2.10, +2.05),
        (-2.10, -2.05, +2.10, -2.05),
        (-2.10, -2.05, -2.10, +2.05),
        (+2.10, -2.05, +2.10, +2.05),
    ]:
        seg = pcbnew.PCB_SHAPE(fp_vis)
        seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
        seg.SetLayer(pcbnew.F_SilkS)
        seg.SetWidth(mm(0.15))
        seg.SetStart(lpt(x0, y0))
        seg.SetEnd(lpt(x1, y1))
        fp_vis.Add(seg)

    dot = pcbnew.PCB_SHAPE(fp_vis)
    dot.SetShape(pcbnew.SHAPE_T_CIRCLE)
    dot.SetLayer(pcbnew.F_SilkS)
    dot.SetWidth(mm(0.15))
    dot.SetFilled(True)
    dot.SetCenter(lpt(-2.55, +1.20))
    dot.SetEnd(lpt(-2.30, +1.20))
    fp_vis.Add(dot)

    for x0, y0, x1, y1 in [
        (-2.30, +2.25, +2.30, +2.25),
        (-2.30, -2.25, +2.30, -2.25),
        (-2.30, -2.25, -2.30, +2.25),
        (+2.30, -2.25, +2.30, +2.25),
    ]:
        seg = pcbnew.PCB_SHAPE(fp_vis)
        seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
        seg.SetLayer(pcbnew.F_CrtYd)
        seg.SetWidth(mm(0.05))
        seg.SetStart(lpt(x0, y0))
        seg.SetEnd(lpt(x1, y1))
        fp_vis.Add(seg)

    for x0, y0, x1, y1 in [
        (-1.725, +1.725, +1.725, +1.725),
        (-1.725, -1.725, +1.725, -1.725),
        (-1.725, -1.725, -1.725, +1.725),
        (+1.725, -1.725, +1.725, +1.725),
    ]:
        seg = pcbnew.PCB_SHAPE(fp_vis)
        seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
        seg.SetLayer(pcbnew.F_Fab)
        seg.SetWidth(mm(0.10))
        seg.SetStart(lpt(x0, y0))
        seg.SetEnd(lpt(x1, y1))
        fp_vis.Add(seg)

    fp_vis.Reference().SetPosition(lpt(0.0, +3.10))
    fp_vis.Reference().SetTextSize(pcbnew.VECTOR2I(mm(1.0), mm(1.0)))
    fp_vis.Reference().SetTextThickness(mm(0.15))
    fp_vis.Value().SetPosition(lpt(0.0, +4.40))
    fp_vis.Value().SetLayer(pcbnew.F_Fab)
    fp_vis.Value().SetTextSize(pcbnew.VECTOR2I(mm(0.8), mm(0.8)))

    for txt_str, tx, ty in [("A+", -3.30, 0.0), ("K-", +3.30, 0.0), ("BTM NOTCH=A", 0.0, +4.40)]:
        t = pcbnew.PCB_TEXT(fp_vis)
        t.SetText(txt_str)
        t.SetLayer(pcbnew.F_SilkS)
        t.SetPosition(lpt(tx, ty))
        t.SetTextSize(pcbnew.VECTOR2I(mm(0.85), mm(0.85)))
        t.SetTextThickness(mm(0.15))
        fp_vis.Add(t)

    io.FootprintSave(str(FP_LIB_DIR), fp_vis)

    # 3. Wire Solder Pad 2.5 x 3.5 mm (SMD, with F.CrtYd per DFM review)
    fp_pad = pcbnew.FOOTPRINT(None)
    fp_pad.SetReference("J_PAD")
    fp_pad.SetValue("WirePad_2.5x3.5mm")
    fp_pad.SetFPID(pcbnew.LIB_ID("lepiled_mcpcb", "WirePad_2.5x3.5mm"))
    fp_pad.SetAttributes(pcbnew.FP_SMD | pcbnew.FP_EXCLUDE_FROM_BOM | pcbnew.FP_EXCLUDE_FROM_POS_FILES)

    pw = pcbnew.PAD(fp_pad)
    pw.SetNumber("1")
    pw.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
    pw.SetShape(pcbnew.PAD_SHAPE_ROUNDRECT)
    pw.SetRoundRectCornerRadius(mm(0.30))
    pw.SetPosition(lpt(0.0, 0.0))
    pw.SetSize(pcbnew.VECTOR2I(mm(2.50), mm(3.50)))
    pw.SetLayerSet(lset(pcbnew.F_Cu, pcbnew.F_Mask))
    pw.SetLocalSolderMaskMargin(mm(0.05))
    fp_pad.Add(pw)

    for x0, y0, x1, y1 in [(-1.45, +1.95, +1.45, +1.95), (+1.45, +1.95, +1.45, -1.95),
                           (+1.45, -1.95, -1.45, -1.95), (-1.45, -1.95, -1.45, +1.95)]:
        seg = pcbnew.PCB_SHAPE(fp_pad)
        seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
        seg.SetLayer(pcbnew.F_CrtYd)
        seg.SetWidth(mm(0.05))
        seg.SetStart(lpt(x0, y0))
        seg.SetEnd(lpt(x1, y1))
        fp_pad.Add(seg)

    fp_pad.Reference().SetPosition(lpt(0.0, +2.60))
    fp_pad.Reference().SetLayer(pcbnew.F_Fab)
    fp_pad.Reference().SetTextSize(pcbnew.VECTOR2I(mm(0.85), mm(0.85)))
    fp_pad.Reference().SetTextThickness(mm(0.14))
    fp_pad.Value().SetPosition(lpt(0.0, -2.60))
    fp_pad.Value().SetLayer(pcbnew.F_Fab)
    fp_pad.Value().SetTextSize(pcbnew.VECTOR2I(mm(0.7), mm(0.7)))
    io.FootprintSave(str(FP_LIB_DIR), fp_pad)

    # 4. Mounting Hole M3 NPTH 3.2 mm drill, 6.0 mm keepout
    fp_mh = pcbnew.FOOTPRINT(None)
    fp_mh.SetReference("MH")
    fp_mh.SetValue("MountingHole_3.2mm_M3_NPTH")
    fp_mh.SetFPID(pcbnew.LIB_ID("lepiled_mcpcb", "MountingHole_3.2mm_M3_NPTH"))
    fp_mh.SetAttributes(pcbnew.FP_EXCLUDE_FROM_BOM | pcbnew.FP_EXCLUDE_FROM_POS_FILES | pcbnew.FP_BOARD_ONLY)

    pmh = pcbnew.PAD(fp_mh)
    pmh.SetNumber("")
    pmh.SetAttribute(pcbnew.PAD_ATTRIB_NPTH)
    pmh.SetShape(pcbnew.PAD_SHAPE_CIRCLE)
    pmh.SetPosition(lpt(0.0, 0.0))
    pmh.SetSize(pcbnew.VECTOR2I(mm(3.20), mm(3.20)))
    pmh.SetDrillSize(pcbnew.VECTOR2I(mm(3.20), mm(3.20)))
    pmh.SetLayerSet(lset(pcbnew.F_Mask))
    pmh.SetLocalSolderMaskMargin(mm(1.40))  # 3.20 + 2*1.40 = 6.00 mm mask keepout
    fp_mh.Add(pmh)

    # 6.0 mm head keepout ring on F.SilkS & F.CrtYd (outside 6.0 mm mask opening)
    for layer, rad, lw in [(pcbnew.F_SilkS, 3.25, 0.15), (pcbnew.F_CrtYd, 3.30, 0.05)]:
        c = pcbnew.PCB_SHAPE(fp_mh)
        c.SetShape(pcbnew.SHAPE_T_CIRCLE)
        c.SetLayer(layer)
        c.SetWidth(mm(lw))
        c.SetFilled(False)
        c.SetCenter(lpt(0.0, 0.0))
        c.SetEnd(lpt(rad, 0.0))
        fp_mh.Add(c)

    fp_mh.Reference().SetPosition(lpt(0.0, +4.10))
    fp_mh.Reference().SetLayer(pcbnew.F_Fab)
    fp_mh.Reference().SetTextSize(pcbnew.VECTOR2I(mm(0.85), mm(0.85)))
    fp_mh.Reference().SetTextThickness(mm(0.14))
    fp_mh.Value().SetPosition(lpt(0.0, -4.10))
    fp_mh.Value().SetLayer(pcbnew.F_Fab)
    fp_mh.Value().SetTextSize(pcbnew.VECTOR2I(mm(0.7), mm(0.7)))
    io.FootprintSave(str(FP_LIB_DIR), fp_mh)

    return polygon_area(uv_poly), polygon_area(vis_poly)


def write_lib_tables():
    sym_table = """(sym_lib_table
  (version 7)
  (lib (name "lepiled_mcpcb")(type "KiCad")(uri "${KIPRJMOD}/lepiled_mcpcb.kicad_sym")(options "")(descr "LepiLED MCPCB custom symbols"))
)
"""
    fp_table = """(fp_lib_table
  (version 7)
  (lib (name "lepiled_mcpcb")(type "KiCad")(uri "${KIPRJMOD}/lepiled_mcpcb.pretty")(options "")(descr "LepiLED MCPCB custom footprints"))
)
"""
    (BASE_DIR / "sym-lib-table").write_text(sym_table)
    (BASE_DIR / "fp-lib-table").write_text(fp_table)


def write_kicad_pro():
    pro = {
        "board": {
            "design_settings": {
                "defaults": {
                    "board_outline_line_width": 0.1,
                    "copper_line_width": 0.2,
                    "silk_line_width": 0.15,
                    "silk_text_size_h": 0.85,
                    "silk_text_size_v": 0.85,
                    "silk_text_thickness": 0.15,
                },
                "diff_pair_dimensions": [],
                "drc_exclusions": [],
                "rules": {
                    "min_clearance": 0.25,
                    "min_copper_edge_clearance": 0.5,
                    "min_hole_clearance": 0.5,
                    "min_silk_clearance": 0.15,
                    "min_text_height": 0.7,
                    "min_track_width": 0.45,
                    "solder_mask_clearance": 0.05,
                },
                "track_widths": [0.8, 1.0],
                "via_dimensions": [],
            },
            "layer_presets": [],
        },
        "boards": [],
        "libraries": {
            "pinned_footprint_libs": ["lepiled_mcpcb"],
            "pinned_symbol_libs": ["lepiled_mcpcb"],
        },
        "meta": {"filename": "led_mcpcb.kicad_pro", "version": 1},
        "net_settings": {
            "classes": [
                {
                    "bus_width": 12,
                    "clearance": 0.25,
                    "diff_pair_gap": 0.25,
                    "diff_pair_via_gap": 0.25,
                    "diff_pair_width": 0.2,
                    "line_style": 0,
                    "microvia_diameter": 0.3,
                    "microvia_drill": 0.1,
                    "name": "Default",
                    "pcb_color": "rgba(0, 0, 0, 0.000)",
                    "priority": 2147483647,
                    "schematic_color": "rgba(0, 0, 0, 0.000)",
                    "track_width": 0.8,
                    "via_diameter": 0.6,
                    "via_drill": 0.3,
                    "wire_width": 6,
                }
            ],
            "meta": {"version": 3},
            "net_colors": None,
            "netclass_assignments": None,
            "netclass_patterns": [],
        },
        "pcbnew": {"page_layout_descr_file": ""},
        "schematic": {
            "legacy_lib_dir": "",
            "meta": {"version": 1},
        },
        "sheets": [[uid("root_sheet"), "Root"]],
        "text_variables": {},
    }
    (BASE_DIR / "led_mcpcb.kicad_pro").write_text(json.dumps(pro, indent=2) + "\n")


def write_kicad_sym():
    sym = """(kicad_symbol_lib
  (version 20241209)
  (generator "kicad_symbol_editor")
  (generator_version "9.0")
  (symbol "LED_ThermalPad"
    (pin_names (offset 1.016))
    (exclude_from_sim no)
    (in_bom yes)
    (on_board yes)
    (property "Reference" "D" (at 0 3.81 0) (effects (font (size 1.27 1.27))))
    (property "Value" "LED" (at 0 -5.08 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "MPN" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (symbol "LED_ThermalPad_0_1"
      (polyline (pts (xy -1.27 -1.27) (xy -1.27 1.27)) (stroke (width 0.254) (type default)) (fill (type none)))
      (polyline (pts (xy -1.27 0) (xy 1.27 0)) (stroke (width 0) (type default)) (fill (type none)))
      (polyline (pts (xy 1.27 -1.27) (xy 1.27 1.27) (xy -1.27 0) (xy 1.27 -1.27)) (stroke (width 0.254) (type default)) (fill (type none)))
    )
    (symbol "LED_ThermalPad_1_1"
      (pin passive line (at -3.81 0 0) (length 2.54) (name "A" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))
      (pin passive line (at 3.81 0 180) (length 2.54) (name "K" (effects (font (size 1.27 1.27)))) (number "2" (effects (font (size 1.27 1.27)))))
      (pin passive line (at 0 -5.08 90) (length 2.54) (name "TH" (effects (font (size 1.0 1.0)))) (number "3" (effects (font (size 1.0 1.0)))))
    )
  )
  (symbol "SolderPad_1P"
    (pin_names (offset 1.016))
    (exclude_from_sim no)
    (in_bom no)
    (on_board yes)
    (property "Reference" "J" (at 0 2.54 0) (effects (font (size 1.27 1.27))))
    (property "Value" "SolderPad" (at 0 -2.54 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "lepiled_mcpcb:WirePad_2.5x3.5mm" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (symbol "SolderPad_1P_0_1"
      (rectangle (start -1.27 1.27) (end 1.27 -1.27) (stroke (width 0.254) (type default)) (fill (type none)))
    )
    (symbol "SolderPad_1P_1_1"
      (pin passive line (at 3.81 0 180) (length 2.54) (name "P1" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))
    )
  )
  (symbol "MountingHole_NPTH"
    (pin_names (offset 1.016))
    (exclude_from_sim yes)
    (in_bom no)
    (on_board yes)
    (property "Reference" "MH" (at 0 2.54 0) (effects (font (size 1.27 1.27))))
    (property "Value" "M3_NPTH" (at 0 -2.54 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "lepiled_mcpcb:MountingHole_3.2mm_M3_NPTH" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (symbol "MountingHole_NPTH_0_1"
      (circle (center 0 0) (radius 1.27) (stroke (width 0.254) (type default)) (fill (type none)))
    )
  )
)
"""
    (BASE_DIR / "lepiled_mcpcb.kicad_sym").write_text(sym)


def write_kicad_sch():
    root_uuid = uid("root_sheet")
    # Grid: 1.27 mm multiples! Use 2.54 mm steps cleanly.
    # LED_ThermalPad:
    #   Pin 1 (A) at local (-3.81, 0) -> schematic (x - 3.81, y)
    #   Pin 2 (K) at local (+3.81, 0) -> schematic (x + 3.81, y)
    #   Pin 3 (THERM) at local (0, -3.81) -> schematic (x, y + 3.81) because Y-down!
    # SolderPad_1P:
    #   Pin 1 at local (+3.81, 0) -> at angle 0: (x + 3.81, y); at angle 180: (x - 3.81, y).
    duv_x, duv_y = 101.60, 63.50
    dvis_x, dvis_y = 101.60, 101.60

    j_uv_p_x, j_uv_p_y = 63.50, 63.50     # pin 1 at 67.31, 63.50
    j_uv_n_x, j_uv_n_y = 139.70, 63.50    # angle 180 -> pin 1 at 135.89, 63.50
    j_vis_p_x, j_vis_p_y = 63.50, 101.60  # pin 1 at 67.31, 101.60
    j_vis_n_x, j_vis_n_y = 139.70, 101.60 # angle 180 -> pin 1 at 135.89, 101.60

    mh1_x, mh1_y = 63.50, 139.70
    mh2_x, mh2_y = 88.90, 139.70

    def sym_inst(ref, lib_id, val, fp, mpn, ds, x, y, angle, pins, in_bom="yes"):
        s_uid = uid(f"sym_{ref}")
        pin_lines = "\n".join(f'    (pin "{p}" (uuid "{uid(f"pin_{ref}_{p}")}"))' for p in pins)
        val_y = y + 8.89 if "LED_ThermalPad" in lib_id else y + 5.08
        return f"""  (symbol
    (lib_id "{lib_id}")
    (at {x:.2f} {y:.2f} {angle})
    (unit 1)
    (exclude_from_sim no)
    (in_bom {in_bom})
    (on_board yes)
    (dnp no)
    (uuid "{s_uid}")
    (property "Reference" "{ref}" (at {x:.2f} {y - 5.08:.2f} 0) (effects (font (size 1.27 1.27))))
    (property "Value" "{val}" (at {x:.2f} {val_y:.2f} 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "{fp}" (at {x:.2f} {y:.2f} 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Datasheet" "{ds}" (at {x:.2f} {y:.2f} 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "MPN" "{mpn}" (at {x:.2f} {y:.2f} 0) (effects (font (size 1.27 1.27)) (hide yes)))
{pin_lines}
    (instances
      (project "led_mcpcb"
        (path "/{root_uuid}"
          (reference "{ref}")
          (unit 1)
        )
      )
    )
  )"""

    def wire(x1, y1, x2, y2, name):
        return f'  (wire (pts (xy {x1:.2f} {y1:.2f}) (xy {x2:.2f} {y2:.2f})) (stroke (width 0) (type default)) (uuid "{uid(name)}"))'

    def label(txt, x, y, ang=0):
        return f'  (label "{txt}" (at {x:.2f} {y:.2f} {ang}) (effects (font (size 1.27 1.27)) (justify left bottom)) (uuid "{uid(f"lbl_{txt}_{x}_{y}")}"))'

    def nc(x, y, name):
        return f'  (no_connect (at {x:.2f} {y:.2f}) (uuid "{uid(name)}"))'

    sch = f"""(kicad_sch
  (version 20250114)
  (generator "eeschema")
  (generator_version "9.0")
  (uuid "{root_uuid}")
  (paper "A4")
  (title_block
    (title "LepiLED Dual-LED Aluminum MCPCB Strip (MECH-MCPCB-1..4)")
    (date "2026-11-18")
    (rev "1.0")
    (comment 1 "1-Layer Al MCPCB 20x80 mm, 1.6 mm, 1.0 W/m*K, 1 oz F.Cu ONLY")
    (comment 2 "D_UV: SST-10-UV (btm notch=K); D_VIS: XP-E2 (btm notch=A)")
  )
  (lib_symbols
    (symbol "lepiled_mcpcb:LED_ThermalPad"
      (pin_names (offset 1.016))
      (exclude_from_sim no)
      (in_bom yes)
      (on_board yes)
      (property "Reference" "D" (at 0 3.81 0) (effects (font (size 1.27 1.27))))
      (property "Value" "LED" (at 0 -5.08 0) (effects (font (size 1.27 1.27))))
      (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
      (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
      (property "MPN" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
      (symbol "LED_ThermalPad_0_1"
        (polyline (pts (xy -1.27 -1.27) (xy -1.27 1.27)) (stroke (width 0.254) (type default)) (fill (type none)))
        (polyline (pts (xy -1.27 0) (xy 1.27 0)) (stroke (width 0) (type default)) (fill (type none)))
        (polyline (pts (xy 1.27 -1.27) (xy 1.27 1.27) (xy -1.27 0) (xy 1.27 -1.27)) (stroke (width 0.254) (type default)) (fill (type none)))
      )
      (symbol "LED_ThermalPad_1_1"
        (pin passive line (at -3.81 0 0) (length 2.54) (name "A" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))
        (pin passive line (at 3.81 0 180) (length 2.54) (name "K" (effects (font (size 1.27 1.27)))) (number "2" (effects (font (size 1.27 1.27)))))
        (pin passive line (at 0 -5.08 90) (length 2.54) (name "TH" (effects (font (size 1.0 1.0)))) (number "3" (effects (font (size 1.0 1.0)))))
      )
    )
    (symbol "lepiled_mcpcb:SolderPad_1P"
      (pin_names (offset 1.016))
      (exclude_from_sim no)
      (in_bom no)
      (on_board yes)
      (property "Reference" "J" (at 0 2.54 0) (effects (font (size 1.27 1.27))))
      (property "Value" "SolderPad" (at 0 -2.54 0) (effects (font (size 1.27 1.27))))
      (property "Footprint" "lepiled_mcpcb:WirePad_2.5x3.5mm" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
      (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
      (symbol "SolderPad_1P_0_1"
        (rectangle (start -1.27 1.27) (end 1.27 -1.27) (stroke (width 0.254) (type default)) (fill (type none)))
      )
      (symbol "SolderPad_1P_1_1"
        (pin passive line (at 3.81 0 180) (length 2.54) (name "P1" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))
      )
    )
    (symbol "lepiled_mcpcb:MountingHole_NPTH"
      (pin_names (offset 1.016))
      (exclude_from_sim yes)
      (in_bom no)
      (on_board yes)
      (property "Reference" "MH" (at 0 2.54 0) (effects (font (size 1.27 1.27))))
      (property "Value" "M3_NPTH" (at 0 -2.54 0) (effects (font (size 1.27 1.27))))
      (property "Footprint" "lepiled_mcpcb:MountingHole_3.2mm_M3_NPTH" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
      (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
      (symbol "MountingHole_NPTH_0_1"
        (circle (center 0 0) (radius 1.27) (stroke (width 0.254) (type default)) (fill (type none)))
      )
    )
  )
{sym_inst("D_UV", "lepiled_mcpcb:LED_ThermalPad", "SST-10-UV-A130-G365-00", "lepiled_mcpcb:LED_Luminus_SST-10-UV_A130", "SST-10-UV-A130-G365-00", "datasheets/Luminus_SST-10-UV_Datasheet.pdf", duv_x, duv_y, 0, ["1", "2", "3"], "yes")}
{sym_inst("D_VIS", "lepiled_mcpcb:LED_ThermalPad", "Cree XP-E2 (RB/GR/CW)", "lepiled_mcpcb:LED_Cree_XP-E2", "XPEBRY/XPEBGR/XPEBWT", "datasheets/XLamp-XPE2.pdf", dvis_x, dvis_y, 0, ["1", "2", "3"], "yes")}
{sym_inst("J_UV_P", "lepiled_mcpcb:SolderPad_1P", "UV+", "lepiled_mcpcb:WirePad_2.5x3.5mm", "", "", j_uv_p_x, j_uv_p_y, 0, ["1"], "no")}
{sym_inst("J_UV_N", "lepiled_mcpcb:SolderPad_1P", "UV-", "lepiled_mcpcb:WirePad_2.5x3.5mm", "", "", j_uv_n_x, j_uv_n_y, 180, ["1"], "no")}
{sym_inst("J_VIS_P", "lepiled_mcpcb:SolderPad_1P", "VIS+", "lepiled_mcpcb:WirePad_2.5x3.5mm", "", "", j_vis_p_x, j_vis_p_y, 0, ["1"], "no")}
{sym_inst("J_VIS_N", "lepiled_mcpcb:SolderPad_1P", "VIS-", "lepiled_mcpcb:WirePad_2.5x3.5mm", "", "", j_vis_n_x, j_vis_n_y, 180, ["1"], "no")}
{sym_inst("MH1", "lepiled_mcpcb:MountingHole_NPTH", "M3_NPTH", "lepiled_mcpcb:MountingHole_3.2mm_M3_NPTH", "", "", mh1_x, mh1_y, 0, [], "no")}
{sym_inst("MH2", "lepiled_mcpcb:MountingHole_NPTH", "M3_NPTH", "lepiled_mcpcb:MountingHole_3.2mm_M3_NPTH", "", "", mh2_x, mh2_y, 0, [], "no")}
{wire(j_uv_p_x + 3.81, j_uv_p_y, duv_x - 3.81, duv_y, "w_uvp")}
{wire(duv_x + 3.81, duv_y, j_uv_n_x - 3.81, j_uv_n_y, "w_uvn")}
{wire(j_vis_p_x + 3.81, j_vis_p_y, dvis_x - 3.81, dvis_y, "w_visp")}
{wire(dvis_x + 3.81, dvis_y, j_vis_n_x - 3.81, j_vis_n_y, "w_visn")}
{label("UV_P", 81.28, 63.50)}
{label("UV_N", 121.92, 63.50)}
{label("VIS_P", 81.28, 101.60)}
{label("VIS_N", 121.92, 101.60)}
{nc(duv_x, duv_y + 5.08, "nc_duv_therm")}
{nc(dvis_x, dvis_y + 5.08, "nc_dvis_therm")}
  (text "Note: D_UV (SST-10-UV) bottom notch faces CATHODE; D_VIS (Cree XP-E2) bottom notch faces ANODE." (at 50.80 124.46 0) (effects (font (size 1.5 1.5)) (justify left bottom)) (uuid "{uid("note_pol")}"))
  (sheet_instances
    (path "/" (page "1"))
  )
)
"""
    (BASE_DIR / "led_mcpcb.kicad_sch").write_text(sch)


def add_rounded_rect_edge_cuts(board: pcbnew.BOARD, w: float, h: float, r: float):
    hw, hh = w / 2.0, h / 2.0
    # 4 straight segments + 4 quarter-circle arcs
    segs = [
        ((-hw + r, +hh), (+hw - r, +hh)),
        ((+hw, +hh - r), (+hw, -hh + r)),
        ((+hw - r, -hh), (-hw + r, -hh)),
        ((-hw, -hh + r), (-hw, +hh - r)),
    ]
    for (x0, y0), (x1, y1) in segs:
        s = pcbnew.PCB_SHAPE(board)
        s.SetShape(pcbnew.SHAPE_T_SEGMENT)
        s.SetLayer(pcbnew.Edge_Cuts)
        s.SetWidth(mm(0.10))
        s.SetStart(kpt(x0, y0))
        s.SetEnd(kpt(x1, y1))
        board.Add(s)

    # Corner arcs: center, start, mid, end (in math coords)
    s2 = r / math.sqrt(2.0)
    corners = [
        ((+hw - r, +hh - r), (+hw - r, +hh), (+hw - r + s2, +hh - r + s2), (+hw, +hh - r)),  # TR
        ((+hw - r, -hh + r), (+hw, -hh + r), (+hw - r + s2, -hh + r - s2), (+hw - r, -hh)),  # BR
        ((-hw + r, -hh + r), (-hw + r, -hh), (-hw + r - s2, -hh + r - s2), (-hw, -hh + r)),  # BL
        ((-hw + r, +hh - r), (-hw, +hh - r), (-hw + r - s2, +hh - r + s2), (-hw + r, +hh)),  # TL
    ]
    for c, st, mid, en in corners:
        a = pcbnew.PCB_SHAPE(board)
        a.SetShape(pcbnew.SHAPE_T_ARC)
        a.SetLayer(pcbnew.Edge_Cuts)
        a.SetWidth(mm(0.10))
        a.SetArcGeometry(kpt(*st), kpt(*mid), kpt(*en))
        board.Add(a)


def add_track(board: pcbnew.BOARD, pts_xy, width_mm: float, net):
    for (x0, y0), (x1, y1) in zip(pts_xy, pts_xy[1:]):
        trk = pcbnew.PCB_TRACK(board)
        trk.SetLayer(pcbnew.F_Cu)
        trk.SetWidth(mm(width_mm))
        trk.SetStart(kpt(x0, y0))
        trk.SetEnd(kpt(x1, y1))
        trk.SetNet(net)
        board.Add(trk)


def build_board(uv_area: float, vis_area: float):
    pcb_path = BASE_DIR / "led_mcpcb.kicad_pcb"
    board = pcbnew.NewBoard(str(pcb_path))
    board.SetCopperLayerCount(1)

    # Disable B.Cu, B.Mask, B.Silkscreen, B.Paste, B.Adhesive, B.Courtyard, B.Fab for strict 1-layer Al MCPCB
    enabled = pcbnew.LSET()
    for lyr in [
        pcbnew.F_Cu, pcbnew.F_Mask, pcbnew.F_SilkS, pcbnew.F_Paste,
        pcbnew.Edge_Cuts, pcbnew.Margin, pcbnew.F_CrtYd, pcbnew.F_Fab,
        pcbnew.Dwgs_User, pcbnew.Cmts_User,
    ]:
        enabled.addLayer(lyr)
    board.SetEnabledLayers(enabled)

    ds = board.GetDesignSettings()
    ds.m_TrackMinWidth = mm(0.45)
    ds.m_MinClearance = mm(0.25)
    ds.m_CopperEdgeClearance = mm(0.50)
    ds.m_HoleClearance = mm(0.50)
    ds.m_SilkClearance = mm(0.15)
    ds.m_SolderMaskExpansion = mm(0.05)
    ds.SetAuxOrigin(kpt(0.0, 0.0))

    add_rounded_rect_edge_cuts(board, 20.0, 80.0, 1.0)

    # Create nets matching schematic
    nets = {}
    for nname in [
        "/UV_P", "/UV_N", "/VIS_P", "/VIS_N",
        "unconnected-(D_UV-TH-Pad3)", "unconnected-(D_VIS-TH-Pad3)",
    ]:
        n = pcbnew.NETINFO_ITEM(board, nname)
        board.Add(n)
        nets[nname] = n

    io = pcbnew.PCB_IO_KICAD_SEXPR()
    root_uuid = uid("root_sheet")

    def place_fp(fp_name, ref, val, xm, ym, pad_nets=None, attrs=None):
        fp = io.FootprintLoad(str(FP_LIB_DIR), fp_name)
        fp.SetFPID(pcbnew.LIB_ID("lepiled_mcpcb", fp_name))
        fp.SetReference(ref)
        fp.SetValue(val)
        fp.SetPosition(kpt(xm, ym))
        fp.SetPath(pcbnew.KIID_PATH(f"/{root_uuid}/{uid(f'sym_{ref}')}"))
        if attrs is not None:
            fp.SetAttributes(attrs)
        if pad_nets:
            for pad in fp.Pads():
                pnum = pad.GetNumber()
                if pnum in pad_nets:
                    pad.SetNet(nets[pad_nets[pnum]])
        board.Add(fp)
        return fp

    place_fp("LED_Luminus_SST-10-UV_A130", "D_UV", "SST-10-UV-A130-G365-00", 0.0, +18.0,
             {"1": "/UV_P", "2": "/UV_N", "3": "unconnected-(D_UV-TH-Pad3)"}, pcbnew.FP_SMD)
    place_fp("LED_Cree_XP-E2", "D_VIS", "Cree XP-E2 (RB/GR/CW)", 0.0, -18.0,
             {"1": "/VIS_P", "2": "/VIS_N", "3": "unconnected-(D_VIS-TH-Pad3)"}, pcbnew.FP_SMD)

    pad_attrs = pcbnew.FP_SMD | pcbnew.FP_EXCLUDE_FROM_BOM | pcbnew.FP_EXCLUDE_FROM_POS_FILES
    # Shifted +2.0 mm north to Y=-24.0 mm -> 3.50 mm clearance to grounded MH2 M3 screw head (Carbon B-7 / Opus B-L17)
    place_fp("WirePad_2.5x3.5mm", "J_UV_P", "UV+", -6.75, -24.0, {"1": "/UV_P"}, pad_attrs)
    place_fp("WirePad_2.5x3.5mm", "J_VIS_P", "VIS+", -2.25, -24.0, {"1": "/VIS_P"}, pad_attrs)
    place_fp("WirePad_2.5x3.5mm", "J_VIS_N", "VIS-", +2.25, -24.0, {"1": "/VIS_N"}, pad_attrs)
    place_fp("WirePad_2.5x3.5mm", "J_UV_N", "UV-", +6.75, -24.0, {"1": "/UV_N"}, pad_attrs)

    mh_attrs = pcbnew.FP_EXCLUDE_FROM_BOM | pcbnew.FP_EXCLUDE_FROM_POS_FILES | pcbnew.FP_BOARD_ONLY
    place_fp("MountingHole_3.2mm_M3_NPTH", "MH1", "M3_NPTH", 0.0, +32.0, None, mh_attrs)
    place_fp("MountingHole_3.2mm_M3_NPTH", "MH2", "M3_NPTH", 0.0, -32.0, None, mh_attrs)

    # Planar F.Cu traces (0.48 mm exit from D_UV pads -> 0.80 mm trunk, 0.50 mm from D_VIS -> 0.80 mm)
    add_track(board, [(-1.385, +18.0), (-1.90, +18.0)], 0.48, nets["/UV_P"])
    add_track(board, [(-1.90, +18.0), (-8.30, +18.0), (-8.30, -22.5), (-6.75, -24.0)], 0.80, nets["/UV_P"])
    add_track(board, [(+1.385, +18.0), (+1.90, +18.0)], 0.48, nets["/UV_N"])
    add_track(board, [(+1.90, +18.0), (+8.30, +18.0), (+8.30, -22.5), (+6.75, -24.0)], 0.80, nets["/UV_N"])
    add_track(board, [(-1.400, -18.0), (-1.400, -20.0)], 0.50, nets["/VIS_P"])
    add_track(board, [(-1.400, -20.0), (-1.400, -21.8), (-2.25, -24.0)], 0.80, nets["/VIS_P"])
    add_track(board, [(+1.400, -18.0), (+1.400, -20.0)], 0.50, nets["/VIS_N"])
    add_track(board, [(+1.400, -20.0), (+1.400, -21.8), (+2.25, -24.0)], 0.80, nets["/VIS_N"])

    # Board-level Silkscreen labels for solder pads & strip ID (clear of pads & MH2 ring r=3.3mm -> y=-28.7)
    for txt_str, xm, ym in [
        ("UV+", -6.75, -27.2),
        ("VIS+", -2.25, -27.2),
        ("VIS-", +2.25, -27.2),
        ("UV-", +6.75, -27.2),
        ("LEPILED MCPCB R4.1", 0.0, -37.2),
    ]:
        t = pcbnew.PCB_TEXT(board)
        t.SetText(txt_str)
        t.SetLayer(pcbnew.F_SilkS)
        t.SetPosition(kpt(xm, ym))
        t.SetTextSize(pcbnew.VECTOR2I(mm(0.85), mm(0.85)))
        t.SetTextThickness(mm(0.15))
        board.Add(t)

    pcbnew.SaveBoard(str(pcb_path), board)
    print(f"Saved {pcb_path} | D_UV therm pour = {uv_area:.1f} mm^2, D_VIS therm pour = {vis_area:.1f} mm^2")


def run_verification_and_exports():
    kcli = "/usr/bin/kicad-cli"
    gerbv = "/home/alimuldal/.local/share/lepiled-tools/bin/gerbv"

    sch_path = BASE_DIR / "led_mcpcb.kicad_sch"
    pcb_path = BASE_DIR / "led_mcpcb.kicad_pcb"

    GERBER_DIR.mkdir(parents=True, exist_ok=True)
    RENDER_DIR.mkdir(parents=True, exist_ok=True)

    # 1. ERC (both JSON and report)
    for fmt, ext in [("json", "json"), ("report", "rpt")]:
        subprocess.run(
            [kcli, "sch", "erc", "--format", fmt, "--severity-all", "--exit-code-violations",
             "-o", str(BASE_DIR / f"erc_report.{ext}"), str(sch_path)],
            check=True,
        )

    # 2. DRC (both JSON and report)
    for fmt, ext in [("json", "json"), ("report", "rpt")]:
        subprocess.run(
            [kcli, "pcb", "drc", "--format", fmt, "--schematic-parity", "--severity-all", "--exit-code-violations",
             "-o", str(BASE_DIR / f"drc_report.{ext}"), str(pcb_path)],
            check=True,
        )

    # 3. Export 1-Layer Gerbers (F.Cu, F.Mask, F.SilkS, F.Paste, Edge.Cuts ONLY)
    for old_f in GERBER_DIR.glob("*"):
        if old_f.is_file():
            old_f.unlink()
    subprocess.run(
        [kcli, "pcb", "export", "gerbers", "--no-protel-ext", "--use-drill-file-origin",
         "-o", str(GERBER_DIR) + "/",
         "-l", "F.Cu,F.Mask,F.SilkS,F.Paste,Edge.Cuts", str(pcb_path)],
        check=True,
    )
    subprocess.run(
        [kcli, "pcb", "export", "drill", "--format", "excellon", "--drill-origin", "plot",
         "--excellon-units", "mm", "--excellon-separate-th",
         "--generate-map", "--map-format", "pdf", "--generate-report",
         "-o", str(GERBER_DIR) + "/", str(pcb_path)],
        check=True,
    )

    # Verify 0 PTH holes in drill report and remove empty KiCad PTH stub files
    drill_rpt = (GERBER_DIR / "led_mcpcb-drill.rpt").read_text()
    assert "Total plated holes count 0" in drill_rpt, f"Unexpected PTH holes in 1-layer MCPCB:\n{drill_rpt}"
    for stub in ["led_mcpcb-PTH.drl", "led_mcpcb-PTH-drl_map.pdf"]:
        p_stub = GERBER_DIR / stub
        if p_stub.exists():
            p_stub.unlink()

    # Verify NO B_Cu or PTH files exist
    for bad in GERBER_DIR.glob("*"):
        assert "B_Cu" not in bad.name and "B_Mask" not in bad.name and "PTH.drl" not in bad.name.replace("NPTH.drl", ""), \
            f"Unexpected back/PTH file in 1-layer MCPCB gerbers: {bad.name}"

    # Patch led_mcpcb-job.gbrjob to strict 1-layer Aluminum MCPCB spec (1.0 W/m*K, ENIG finish, Rev 4.1)
    gbrjob_path = GERBER_DIR / "led_mcpcb-job.gbrjob"
    if gbrjob_path.exists():
        job = json.loads(gbrjob_path.read_text())
        job.setdefault("Header", {}).setdefault("GenerationSoftware", {})
        job.setdefault("GeneralSpecs", {})["LayerNumber"] = 1
        job["GeneralSpecs"]["BoardThickness"] = 1.6
        job["GeneralSpecs"]["Finish"] = "ENIG"
        job["GeneralSpecs"]["ProjectId"] = {"Name": "led_mcpcb", "GUID": uid("led_mcpcb_proj"), "Revision": "4.1"}
        job["MaterialStackup"] = [
            {"Type": "Legend", "Name": "Top Silk Screen", "Color": "Black"},
            {"Type": "SolderPaste", "Name": "Top Solder Paste"},
            {"Type": "SolderMask", "Thickness": 0.02, "Name": "Top Solder Mask", "Color": "White"},
            {"Type": "Copper", "Thickness": 0.035, "Name": "F.Cu"},
            {"Type": "Dielectric", "Thickness": 0.10, "Material": "Thermal Dielectric (1.0 W/m*K)", "Name": "Thermal Dielectric"},
            {"Type": "Dielectric", "Thickness": 1.445, "Material": "Aluminum 5052/6061 Base", "Name": "Aluminum Core"},
        ]
        gbrjob_path.write_text(json.dumps(job, indent=2) + "\n")

    zip_path = GERBER_DIR / "led_mcpcb_gerbers.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in sorted(GERBER_DIR.iterdir()):
            if f.name.endswith((".gbr", ".drl", ".gbrjob")):
                zf.write(f, f.name)

    # 4. CPL & Color-Split BOM (JLCPCB format, opposite-notch tape rotation documented per Opus B-M11/B-L15)
    raw_pos = RENDER_DIR / "_raw_pos.csv"
    subprocess.run(
        [kcli, "pcb", "export", "pos", "--format", "csv", "--units", "mm",
         "--use-drill-file-origin", "--exclude-dnp", "--exclude-fp-th",
         "-o", str(raw_pos), str(pcb_path)],
        check=True,
    )
    with raw_pos.open() as f_in, (PCB_DESIGN_DIR / "led_mcpcb_cpl.csv").open("w", newline="") as f_out:
        reader = csv.DictReader(f_in)
        writer = csv.writer(f_out)
        writer.writerow(["Designator", "Mid X", "Mid Y", "Layer", "Rotation", "Polarity_Note"])
        for row in reader:
            ref = row["Ref"]
            rot = float(row["Rot"])
            # D_UV (SST-10-UV: notch=K) vs D_VIS (XP-E2: notch=A) have opposite tape orientation -> +180 deg offset on D_VIS
            if ref == "D_VIS":
                rot = (rot + 180.0) % 360.0
                pnote = "Cree XP-E2 BTM NOTCH=A (+180 deg tape offset vs SST-10-UV; verify on preview)"
            else:
                pnote = "Luminus SST-10-UV BTM NOTCH=K (verify on preview)"
            writer.writerow([
                ref, f"{float(row['PosX']):.3f}", f"{float(row['PosY']):.3f}",
                "Top" if row["Side"].lower() == "top" else "Bottom",
                f"{rot:.1f}", pnote,
            ])
    raw_pos.unlink()

    with (PCB_DESIGN_DIR / "led_mcpcb_bom.csv").open("w", newline="") as f_out:
        writer = csv.writer(f_out)
        writer.writerow(["Variant_Strip", "Comment", "Designator", "Footprint", "MPN", "Qty_Per_Strip", "Qty_Per_Lamp_4x", "Notes"])
        writer.writerow([
            "ALL (Strips 1-4)", "365nm UV LED 3535", "D_UV", "LED_Luminus_SST-10-UV_A130",
            "Luminus SST-10-UV-A130-G365-00", 1, 4, "D1..D4 on MECH-MCPCB-1..4; bottom thermal pad notch = Cathode"
        ])
        writer.writerow([
            "Strips 1 & 2 (RB)", "455nm Royal Blue LED 3535", "D_VIS", "LED_Cree_XP-E2",
            "Cree XPEBRY-L1-0000-00S02", 1, 2, "D5..D6 on MECH-MCPCB-1..2 (active Cree bin 38); bottom notch = Anode"
        ])
        writer.writerow([
            "Strip 3 (GR)", "528nm Green LED 3535", "D_VIS", "LED_Cree_XP-E2",
            "Cree XPEBGR-L1-0000-00K01", 1, 1, "D7 on MECH-MCPCB-3 (active Cree bin S3, +28% flux); bottom notch = Anode"
        ])
        writer.writerow([
            "Strip 4 (CW)", "6200K Cool White LED 3535", "D_VIS", "LED_Cree_XP-E2",
            "Cree XPEBWT-L1-0000-00H51", 1, 1, "D8 on MECH-MCPCB-4 (active Cree bin R5); bottom notch = Anode"
        ])

    # 5. Schematic PDF, SVG, 3D Top Render, Gerbv Top PNG
    subprocess.run([kcli, "sch", "export", "pdf", "-o", str(RENDER_DIR / "schematic.pdf"), str(sch_path)], check=True)
    subprocess.run(
        [kcli, "pcb", "export", "svg", "-o", str(RENDER_DIR / "board.svg"),
         "-l", "F.Cu,F.SilkS,Edge.Cuts", "--mode-single", "--fit-page-to-board", "--exclude-drawing-sheet", str(pcb_path)],
        check=True,
    )
    subprocess.run(
        [kcli, "pcb", "render", "--side", "top", "-w", "1000", "-h", "1600", "--quality", "high",
         "-o", str(RENDER_DIR / "render_top.png"), str(pcb_path)],
        check=True,
    )
    gbr_files = [
        str(GERBER_DIR / "led_mcpcb-F_Cu.gbr"),
        str(GERBER_DIR / "led_mcpcb-F_Mask.gbr"),
        str(GERBER_DIR / "led_mcpcb-F_Silkscreen.gbr"),
        str(GERBER_DIR / "led_mcpcb-Edge_Cuts.gbr"),
        str(GERBER_DIR / "led_mcpcb-NPTH.drl"),
    ]
    subprocess.run(
        [gerbv, "-x", "png", "-D", "300", "-o", str(RENDER_DIR / "gerbv_top.png")] + gbr_files,
        check=True,
    )
    print("Board 2 verification & exports completed cleanly.")


def main():
    write_lib_tables()
    write_kicad_pro()
    write_kicad_sym()
    uv_area, vis_area = create_footprints()
    write_kicad_sch()
    build_board(uv_area, vis_area)
    run_verification_and_exports()


if __name__ == "__main__":
    main()
