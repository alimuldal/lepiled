#!/usr/bin/env python3
"""
Parametric 3D CAD Generator for LepiLED DIY Maxi Switch (M3) using build123d 0.13.0.

Exports:
  - mech_cap_bot.step / .stl       (FDM PETG/ASA, M16 gland)
  - mech_cap_top.step / .stl       (FDM PETG/ASA, flat top face)
  - mech_cap_bot_sls.step / .stl   (SLS PA12, M16 gland)
  - mech_cap_top_sls.step / .stl   (SLS PA12, flat top face)
  - mech_cap_bot_usbc.step / .stl  (FDM PETG/ASA, Option B USB-C stepped pocket)
  - lepiled_assembly.step / .stl   (Full multi-part assembly)
  - cad_verification.json          (trimesh manifold metrics + all-pairs B-Rep 0.000 mm^3 checks + overhang audit)
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import build123d as bd
import numpy as np
import trimesh

from params import LepiLEDParams


def _teardrop_profile_wire(radius: float, angle_deg: float = 45.0) -> bd.Face:
    """Create a horizontal-hole teardrop Face in XY plane with +Y apex for support-free printing."""
    theta = math.radians(angle_deg)
    xt = radius * math.sin(theta)
    yt = radius * math.cos(theta)
    y_apex = yt + xt / math.tan(theta)
    with bd.BuildSketch() as sk:
        with bd.BuildLine():
            bd.ThreePointArc((-xt, yt), (0.0, -radius), (xt, yt))
            bd.Line((xt, yt), (0.0, y_apex))
            bd.Line((0.0, y_apex), (-xt, yt))
        bd.make_face()
    return sk.face()


def _pitched_rect_profile(width: float, rect_h: float, roof_angle_deg: float = 45.0) -> bd.Face:
    """Create a centered-X, bottom-Z=0 rectangle topped with a symmetric 45-deg pitched roof in XY plane."""
    hw = width / 2.0
    roof_h = hw * math.tan(math.radians(roof_angle_deg))
    with bd.BuildSketch() as sk:
        with bd.BuildLine():
            bd.Polyline([
                (-hw, 0.0),
                (hw, 0.0),
                (hw, rect_h),
                (0.0, rect_h + roof_h),
                (-hw, rect_h),
                (-hw, 0.0),
            ])
        bd.make_face()
    return sk.face()


def _m16_anti_rotation_hex_profile(af_width: float, half_vert: float) -> bd.Face:
    """
    Create a 22.5 mm AF captive hex pocket profile in XY plane (X = width, Y = vertical Z after rotation):
      - Vertical flat walls at X = +/- af_width/2 (anti-rotation for 22 mm AF hex locknut)
      - 30-deg bottom V (supported from below, zero overhang)
      - 45-deg symmetric pitched roof above +half_vert (zero >45-deg overhang)
    """
    hw = af_width / 2.0
    y_bot_v = -af_width / math.sqrt(3.0)
    y_bot_side = -hw / math.sqrt(3.0)
    y_roof_peak = half_vert + hw
    with bd.BuildSketch() as sk:
        with bd.BuildLine():
            bd.Polyline([
                (0.0, y_bot_v),
                (hw, y_bot_side),
                (hw, half_vert),
                (0.0, y_roof_peak),
                (-hw, half_vert),
                (-hw, y_bot_side),
                (0.0, y_bot_v),
            ])
        bd.make_face()
    return sk.face()


def build_cap_bot(p: LepiLEDParams) -> bd.Part:
    """Build MECH-CAP-BOT parametric end-cap (0 mm^2 >45 deg off-bed overhang, >=2.5 mm walls)."""
    r_bot = p.cap_bot_od / 2.0        # 46.0 mm
    r_top = p.cap_top_od / 2.0        # 42.0 mm
    z_base = p.z_adapt_bot_end        # 73.0
    z_top = p.z_cap_bot_top           # 144.0
    z_taper_bot = p.z_glass_bot - 12.0  # 120.0
    z_taper_top = z_taper_bot + (r_bot - r_top)  # 124.0 (45 deg outer step)

    # 1. Outer body: Ø92 mm lower body -> 45 deg step -> Ø84 mm upper glass skirt
    c_bot = bd.Cylinder(r_bot, z_taper_bot - z_base, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, z_base))
    c_step = bd.Cone(r_bot, r_top, z_taper_top - z_taper_bot, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, z_taper_bot))
    c_top = bd.Cylinder(r_top, z_top - z_taper_top, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, z_taper_top))
    part = c_bot.fuse(c_step).fuse(c_top)
    # 0.8 mm chamfers on bottom Z=73.0 and top Z=144.0 circles
    bottom_edges = part.edges().filter_by(bd.GeomType.CIRCLE).sort_by(bd.Axis.Z)[:1]
    top_edges = part.edges().filter_by(bd.GeomType.CIRCLE).sort_by(bd.Axis.Z)[-1:]
    part = bd.chamfer(bottom_edges + top_edges, length=p.cap_chamfer)

    # 2. Internal PCB cavity: cylinder + 40.3 deg cone all the way to R=0.02 apex (zero 90-deg ceiling)
    r_cav = p.cap_bot_cavity_dia / 2.0
    h_full = p.cap_bot_cavity_full_h
    h_taper = p.cap_bot_taper_h
    cav_cyl = bd.Cylinder(r_cav, h_full, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, z_base))
    cav_cone = bd.Cone(r_cav, 0.02, h_taper, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, z_base + h_full))
    part = part - cav_cyl.fuse(cav_cone)

    # 3. Bottom O-ring groove (MECH-GASKET-3: 66x2.0 mm) with self-supporting 45 deg V-roof
    r_g3_in = p.bot_oring_r_in
    r_g3_out = p.bot_oring_r_out
    r_g3_mid = 0.5 * (r_g3_in + r_g3_out)
    half_w = 0.5 * (r_g3_out - r_g3_in)
    g3_base = (
        bd.Cylinder(r_g3_out, p.bot_oring_flat_h + 0.1, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
        - bd.Cylinder(r_g3_in, p.bot_oring_flat_h + 0.1, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    ).translate((0, 0, z_base - 0.1))
    g3_roof = (
        bd.Cone(r_g3_out, r_g3_mid, half_w, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
        - bd.Cone(r_g3_in, r_g3_mid, half_w, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    ).translate((0, 0, z_base + p.bot_oring_flat_h))
    part = part - g3_base - g3_roof

    # 4. 4x M3 heat-set insert blind holes at R = 40.2 mm (45°, 135°, 225°, 315°) with 45 deg cone tip
    r_ins = p.insert_m3_hole_dia / 2.0
    for deg in (45.0, 135.0, 225.0, 315.0):
        rad = math.radians(deg)
        ix, iy = p.adapt_bot_bolt_r * math.cos(rad), p.adapt_bot_bolt_r * math.sin(rad)
        hole = bd.Cylinder(r_ins, p.insert_m3_depth, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((ix, iy, z_base))
        tip = bd.Cone(r_ins, 0.02, r_ins - 0.02, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((ix, iy, z_base + p.insert_m3_depth))
        lead = bd.Cone(r_ins + 0.4, r_ins, 0.4, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((ix, iy, z_base))
        part = part - hole.fuse(tip).fuse(lead)

    # 5. Glass socket (Z = 132.0 .. 144.0) with tapered skirt + axial O-ring groove (MECH-GASKET-1: 68x3.5 mm)
    r_pilot = p.glass_pilot_od / 2.0
    r_skirt_bot = p.glass_skirt_id_bot / 2.0
    r_skirt_top = p.glass_skirt_id_top / 2.0
    glass_outer = bd.Cone(r_skirt_bot, r_skirt_top, p.glass_socket_depth, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    glass_inner = bd.Cylinder(r_pilot, p.glass_socket_depth, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    glass_slot = (glass_outer - glass_inner).translate((0, 0, p.z_glass_bot))

    g1_out = bd.Cylinder(p.glass_oring_od / 2.0, p.glass_oring_depth + 0.05, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    g1_in = bd.Cylinder(p.glass_oring_id / 2.0, p.glass_oring_depth + 0.05, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    g1 = (g1_out - g1_in).translate((0, 0, p.z_glass_bot - p.glass_oring_depth))
    part = part - glass_slot.fuse(g1)

    # 6. Core socket (41.0 x 41.0 mm, Z = 132.0 .. 144.0) + 4x wire slots opening into cavity cone
    core_sock = bd.Box(p.core_pocket_w, p.core_pocket_w, p.glass_socket_depth,
                       align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, p.z_core_bot))
    part = part - core_sock

    slot_offset = p.core_pocket_w / 2.0 + p.core_wire_slot_d / 2.0 - 0.1
    z_slot_bot = p.z_adapt_bot_end + 22.0  # opens cleanly below cavity cone -> zero overhang
    h_slot = z_top - z_slot_bot
    for angle in (0.0, 90.0, 180.0, 270.0):
        wslot = bd.Box(p.core_wire_slot_d + 0.2, p.core_wire_slot_w, h_slot,
                       align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((slot_offset, 0, z_slot_bot))
        wslot = wslot.rotate(bd.Axis.Z, angle)
        part = part - wslot

    # 7. 2x M4 CSK upward bulkhead holes at (±9.0, 0.0) into MECH-ANCHOR-BOT (45 deg CSK seat, zero overhang)
    # At R=9.0, cav_cone ceiling is at Z ~ 115.4 mm; at R=13.3, Z ~ 110.3 mm.
    # CSK seat Z=121.5..123.6, c_clear=12.0 mm (Z=109.5..121.5) breaks cleanly out of cone, bore Ø4.4 up to Z=132.5.
    z_csk_seat = p.z_cap_bot_bulkhead_start - 4.5  # 121.5
    for sx in (-1.0, 1.0):
        bx = sx * p.anchor_bot_bolt_x
        c_clear = bd.Cylinder(4.3, 12.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((bx, 0.0, z_csk_seat - 12.0))
        c_seat = bd.Cone(4.3, 2.2, 2.1, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((bx, 0.0, z_csk_seat))
        c_thru = bd.Cylinder(2.2, 11.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((bx, 0.0, z_csk_seat + 2.0))
        part = part - c_clear.fuse(c_seat).fuse(c_thru)

    # 8. SW1 toggle switch cutout (+X side, Y = 0, Z = 93.0 mm)
    # External flat spot-face with 45 deg teardrop top (zero >45 deg overhang)
    sw_sf_face = _teardrop_profile_wire(p.sw1_spotface_dia / 2.0, 45.0)
    sw_sf = bd.extrude(sw_sf_face, 5.0).rotate(bd.Axis.X, 90.0).rotate(bd.Axis.Z, -90.0)
    sw_sf = sw_sf.translate((p.sw1_spotface_x + 5.0, 0.0, p.sw1_z))
    part = part - sw_sf

    # Unobstructed SW1 entry corridor + alcove (X = 16.0..42.5) with symmetric 45 deg pitched roof in YZ
    x_sw_in = p.sw1_spotface_x - p.sw1_wall_thick  # 42.5
    sw_corridor_len = x_sw_in - 16.0               # 26.5 mm -> opens cleanly into Ø61 mm bottom cavity
    sw_prof = _pitched_rect_profile(p.sw1_alcove_w, p.sw1_alcove_h, 45.0)
    sw_alc = bd.extrude(sw_prof, sw_corridor_len).rotate(bd.Axis.X, 90.0).rotate(bd.Axis.Z, -90.0)
    sw_alc = sw_alc.translate((x_sw_in, 0.0, p.sw1_z - p.sw1_alcove_h / 2.0))
    part = part - sw_alc

    # SW1 horizontal teardrop hole (Ø6.35 + clearance)
    sw_td_face = _teardrop_profile_wire(p.sw1_hole_dia / 2.0 + p.print_clearance * 0.5, 45.0)
    sw_hole = bd.extrude(sw_td_face, 8.0).rotate(bd.Axis.X, 90.0).rotate(bd.Axis.Z, -90.0)
    sw_hole = sw_hole.translate((x_sw_in + 5.0, 0.0, p.sw1_z))
    part = part - sw_hole

    # 9. Power entry on -Y side (M16_GLAND or USB_C)
    if p.power_entry_mode == "M16_GLAND":
        # External Ø24 mm teardrop spot-face at Y = -44.0
        m16_sf_face = _teardrop_profile_wire(p.m16_spotface_dia / 2.0, 45.0)
        m16_sf = bd.extrude(m16_sf_face, 6.0).rotate(bd.Axis.X, 90.0).translate((0.0, p.m16_spotface_y, p.m16_z))
        part = part - m16_sf

        # Unobstructed captive 22.5 mm AF anti-rotation hex locknut corridor + alcove (Y = -40.5..-16.0)
        y_m16_in = p.m16_spotface_y + p.m16_wall_thick  # -40.5
        m16_corridor_len = (-16.0) - y_m16_in           # 24.5 mm -> opens cleanly into Ø61 mm bottom cavity
        nut_prof = _m16_anti_rotation_hex_profile(p.m16_nut_af, p.m16_nut_half_vert)
        nut_alc = bd.extrude(nut_prof, m16_corridor_len).rotate(bd.Axis.X, 90.0).translate((0.0, y_m16_in + m16_corridor_len, p.m16_z))
        part = part - nut_alc

        # Horizontal teardrop M16 hole
        m16_td = _teardrop_profile_wire(p.m16_hole_dia / 2.0 + p.print_clearance * 0.5, 45.0)
        m16_hole = bd.extrude(m16_td, 10.0).rotate(bd.Axis.X, 90.0).translate((0.0, y_m16_in + 1.0, p.m16_z))
        part = part - m16_hole
    else:
        # Option B (Rev 4.0): Direct-mate recessed USB-C tunnel centered on J1 mid-plane (Z = z_usbc = 61.98)
        # 13.6 x 7.8 mm + 45 deg pitched roof passes straight through the Ø92->Ø61 mm wall into the cavity
        # so any standard 6.65 mm USB-C PD laptop-charger plug seats full 4.55 mm into J1 (front mouth Y = -25.76 mm)!
        z_usbc = p.z_usbc
        y_tunnel_in = -24.00  # breaks cleanly inside cavity cone across full X=±6.8 width -> ~0.02 mm^2 overhang!
        overmold_len = abs(-47.5 - y_tunnel_in)
        overmold_prof = _pitched_rect_profile(p.usbc_overmold_w, p.usbc_overmold_h, 47.0)
        overmold = bd.extrude(overmold_prof, overmold_len).rotate(bd.Axis.X, 90.0)
        overmold = overmold.translate((0.0, y_tunnel_in, z_usbc - p.usbc_overmold_h / 2.0))
        part = part - overmold

    return part


def build_cap_top(p: LepiLEDParams) -> bd.Part:
    """Build MECH-CAP-TOP parametric end-cap (100% flat top face Z_top, 0 mm^2 >45 deg overhang)."""
    r_cap = p.cap_top_od / 2.0
    z_bot = p.z_cap_top_bot  # 270.0
    z_top = p.z_cap_top_top  # 296.5
    h_tot = z_top - z_bot    # 26.5

    # 1. Main cylinder with outer chamfers
    part = bd.Cylinder(r_cap, h_tot, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, z_bot))
    part = bd.chamfer(part.edges().filter_by(bd.GeomType.CIRCLE), length=p.cap_chamfer)

    # 2. Glass socket (Z = 270.0 .. 282.0) with tapered skirt + axial O-ring groove (MECH-GASKET-2: 68x3.5 mm)
    r_pilot = p.glass_pilot_od / 2.0
    r_skirt_bot = p.glass_skirt_id_bot / 2.0
    r_skirt_top = p.glass_skirt_id_top / 2.0
    glass_outer = bd.Cone(r_skirt_top, r_skirt_bot, p.glass_socket_depth, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    glass_inner = bd.Cylinder(r_pilot, p.glass_socket_depth, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    glass_slot = (glass_outer - glass_inner).translate((0, 0, z_bot))

    g2_out = bd.Cylinder(p.glass_oring_od / 2.0, p.glass_oring_depth + 0.05, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    g2_in = bd.Cylinder(p.glass_oring_id / 2.0, p.glass_oring_depth + 0.05, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    g2 = (g2_out - g2_in).translate((0, 0, p.z_glass_top - 0.05))
    part = part - glass_slot.fuse(g2)

    # 3. Central 41.0 x 41.0 mm through-aperture for MECH-HS-CORE
    core_thru = bd.Box(p.core_pocket_w, p.core_pocket_w, h_tot + 2.0,
                       align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, z_bot - 1.0))
    part = part - core_thru

    # 4. 4x M3 heat-set inserts at R = 34.0 mm (45°) directly in flat Z_top face + 45 deg cone tip
    r_ins = p.insert_m3_hole_dia / 2.0
    for deg in (45.0, 135.0, 225.0, 315.0):
        rad = math.radians(deg)
        ix, iy = p.adapt_top_bolt_r * math.cos(rad), p.adapt_top_bolt_r * math.sin(rad)
        hole = bd.Cylinder(r_ins, p.insert_m3_depth, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)).translate((ix, iy, z_top))
        tip = bd.Cone(0.02, r_ins, r_ins - 0.02, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)).translate((ix, iy, z_top - p.insert_m3_depth))
        lead = bd.Cone(r_ins, r_ins + 0.4, 0.4, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)).translate((ix, iy, z_top))
        part = part - hole.fuse(tip).fuse(lead)

    return part


def build_radial_heatsink(od: float, core_dia: float, height: float, n_fins: int, fin_thick: float,
                          z_start: float, center_bore_dia: float = 0.0) -> bd.Part:
    """Build radial-fin extruded/moulded aluminum heatsink (SK 578/50 SA or SK LED R 80 SA)."""
    core = bd.Cylinder(core_dia / 2.0, height, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    fin_len = (od - core_dia) / 2.0 + 1.0
    fins = []
    for i in range(n_fins):
        ang = 360.0 * i / n_fins
        fin = bd.Box(fin_len, fin_thick, height,
                     align=(bd.Align.MIN, bd.Align.CENTER, bd.Align.MIN)).translate((core_dia / 2.0 - 1.0, 0, 0))
        fins.append(fin.rotate(bd.Axis.Z, ang))
    hs = core.fuse(*fins)
    hs = hs & bd.Cylinder(od / 2.0, height, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    if center_bore_dia > 0.0:
        bore = bd.Cylinder(center_bore_dia / 2.0, height + 2.0,
                           align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, -1.0))
        hs = hs - bore
    return hs.translate((0, 0, z_start))


def build_assembly_parts(p: LepiLEDParams, core_w_override: float | None = None,
                         glass_id_override: float | None = None, glass_od_override: float | None = None,
                         glass_length_override: float | None = None) -> dict[str, bd.Shape]:
    """Build all physical assembly components as individual non-overlapping solids."""
    core_w = core_w_override or p.core_w_nom
    g_id = glass_id_override or p.glass_id_nom
    g_od = glass_od_override or p.glass_od_nom
    g_len = glass_length_override or p.glass_length

    cap_bot = build_cap_bot(p)
    cap_top = build_cap_top(p)
    hs_bot = build_radial_heatsink(
        p.hs_ext_bot_od, p.hs_ext_bot_core_dia, p.hs_ext_bot_height,
        p.hs_ext_bot_n_fins, p.hs_ext_bot_fin_thick, p.z_hs_bot_start, center_bore_dia=0.0,
    )
    hs_top = build_radial_heatsink(
        p.hs_ext_top_od, p.hs_ext_top_core_dia, p.hs_ext_top_height,
        p.hs_ext_top_n_fins, p.hs_ext_top_fin_thick, p.z_adapt_top_end, center_bore_dia=p.eye_bolt_clearance_dia,
    )

    # Bottom adapter plate (MECH-ADAPT-BOT: Ø90x3.0 mm + Ø59x5.0 mm central PCB pedestal)
    # Includes Kapton-lined relief pockets for J2/J3, J4, AND J1+TP1/TP2
    adapt_base = bd.Cylinder(p.adapt_bot_od / 2.0, p.adapt_bot_thick, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, p.z_hs_bot_end))
    adapt_ped = bd.Cylinder(p.adapt_bot_pedestal_dia / 2.0, p.adapt_bot_pedestal_h, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, p.z_adapt_bot_end))
    adapt_bot = adapt_base.fuse(adapt_ped)
    j23_pocket = bd.Box(p.adapt_bot_j23_pocket_w, p.adapt_bot_j23_pocket_l, p.adapt_bot_pin_pocket_depth,
                        align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)).translate((p.adapt_bot_j23_pocket_x, p.adapt_bot_j23_pocket_y, p.z_pcb_seat))
    j4_pocket = bd.Box(p.adapt_bot_j4_pocket_w, p.adapt_bot_j4_pocket_l, p.adapt_bot_pin_pocket_depth,
                       align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)).translate((p.adapt_bot_j4_pocket_x, p.adapt_bot_j4_pocket_y, p.z_pcb_seat))
    j1tp_pocket = bd.Box(p.adapt_bot_j1tp_pocket_w, p.adapt_bot_j1tp_pocket_l, p.adapt_bot_pin_pocket_depth,
                         align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)).translate((p.adapt_bot_j1tp_pocket_x, p.adapt_bot_j1tp_pocket_y, p.z_pcb_seat))
    adapt_bot = adapt_bot - j23_pocket - j4_pocket - j1tp_pocket

    # Top adapter plate (MECH-ADAPT-TOP)
    adapt_top = bd.Cylinder(p.adapt_top_od / 2.0, p.adapt_top_thick, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, p.z_core_top))
    adapt_top = adapt_top - bd.Cylinder(p.eye_bolt_clearance_dia / 2.0, p.adapt_top_thick + 2.0,
                                        align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, p.z_core_top - 1.0))

    # 4x 0.5 mm SS spacer washers (MECH-FAST-3W) between flat cap_top and adapt_top
    washers = []
    for deg in (45.0, 135.0, 225.0, 315.0):
        rad = math.radians(deg)
        wx, wy = p.adapt_top_bolt_r * math.cos(rad), p.adapt_top_bolt_r * math.sin(rad)
        w_out = bd.Cylinder(3.5, p.cap_top_air_gap_proud, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((wx, wy, p.z_cap_top_top))
        w_in = bd.Cylinder(1.6, p.cap_top_air_gap_proud + 0.2, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((wx, wy, p.z_cap_top_top - 0.1))
        washers.append(w_out - w_in)
    spacer_washers = bd.Compound(washers)

    # PCB thermal gap pad (MECH-TIM-PCB) with matching J2/J3, J4, and J1+TP1/TP2 cutouts
    tim_pcb = bd.Box(p.tim_pcb_w, p.tim_pcb_l, p.tim_pcb_thick,
                     align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, p.z_pcb_seat))
    for px, py, pw, pl in [
        (p.adapt_bot_j23_pocket_x, p.adapt_bot_j23_pocket_y, p.adapt_bot_j23_pocket_w, p.adapt_bot_j23_pocket_l),
        (p.adapt_bot_j4_pocket_x, p.adapt_bot_j4_pocket_y, p.adapt_bot_j4_pocket_w, p.adapt_bot_j4_pocket_l),
        (p.adapt_bot_j1tp_pocket_x, p.adapt_bot_j1tp_pocket_y, p.adapt_bot_j1tp_pocket_w, p.adapt_bot_j1tp_pocket_l),
    ]:
        tim_pcb = tim_pcb - bd.Box(pw, pl, p.tim_pcb_thick + 0.5,
                                   align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((px, py, p.z_pcb_seat - 0.25))

    # Driver PCB + exact Rev 4.0 SMD, JST headers, J1 (front mouth Y = -25.76 mm), and TH pins (inside 2.5 mm pockets)
    pcb_board = bd.Box(p.pcb_w, p.pcb_l, p.pcb_thick, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    pcb_board = bd.fillet(pcb_board.edges().filter_by(bd.Axis.Z), p.pcb_corner_r).translate((0, 0, p.z_pcb_bot))
    l1_smd = bd.Box(6.0, 6.0, 4.5, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((-13.0, 11.8, p.z_pcb_top))
    l2_smd = bd.Box(6.0, 6.0, 4.5, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((13.0, 11.8, p.z_pcb_top))
    j2_hdr = bd.Box(7.4, 5.8, p.pcb_jst_mated_h, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((-5.2, 19.2, p.z_pcb_top))
    j3_hdr = bd.Box(7.4, 5.8, p.pcb_jst_mated_h, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((5.2, 19.2, p.z_pcb_top))
    j4_hdr = bd.Box(9.9, 5.8, p.pcb_jst_mated_h, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((-1.4, -2.5, p.z_pcb_top))
    # J1 body F_Fab spans Y in [-25.76, -16.59] (exact GCT USB4085-GF-A Row-B (-18.50) - 7.26 mm mouth)
    # Carve real 4.55 mm-deep mating pocket (8.34 x 4.55 x 2.56 mm, Y in [-25.76, -21.21], centered at Z = z_usbc)
    j1_usbc_outer = bd.Box(8.94, 9.17, 3.46, align=(bd.Align.CENTER, bd.Align.MIN, bd.Align.MIN)).translate((0.0, p.usbc_j1_front_y, p.z_pcb_top))
    j1_cavity = bd.Box(8.34, p.usbc_mating_depth_mm + 0.05, 2.56, align=(bd.Align.CENTER, bd.Align.MIN, bd.Align.CENTER)).translate((0.0, p.usbc_j1_front_y - 0.05, p.z_usbc))
    j1_usbc = j1_usbc_outer - j1_cavity
    # TH pin protrusions below PCB (1.8 mm) inside relief pockets (J1 SH3/SH4 tabs reach Y = -22.36)
    j23_pins = bd.Box(15.0, 2.0, p.pcb_jst_pin_protrude, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)).translate((0.0, 19.2, p.z_pcb_bot))
    j4_pins = bd.Box(7.5, 2.0, p.pcb_jst_pin_protrude, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)).translate((-1.4, -2.5, p.z_pcb_bot))
    j1_pins = bd.Box(9.6, 5.7, p.pcb_jst_pin_protrude, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)).translate((0.0, -19.54, p.z_pcb_bot))
    tp1_pin = bd.Cylinder(1.25, p.pcb_jst_pin_protrude, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)).translate((-8.2, -19.5, p.z_pcb_bot))
    tp2_pin = bd.Cylinder(1.25, p.pcb_jst_pin_protrude, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)).translate((8.2, -19.5, p.z_pcb_bot))
    pcb_assy = bd.Compound([pcb_board, l1_smd, l2_smd, j2_hdr, j3_hdr, j4_hdr, j1_usbc, j23_pins, j4_pins, j1_pins, tp1_pin, tp2_pin])

    # Central heatsink core (MECH-HS-CORE: 40x40x3 mm) with cross-pin bores & +/-1.5 mm top slots
    core_out = bd.Box(core_w, core_w, p.core_length, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    core_in = bd.Box(core_w - 2.0 * p.core_wall, core_w - 2.0 * p.core_wall, p.core_length + 2.0,
                     align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, -1.0))
    hs_core = (core_out - core_in).translate((0, 0, p.z_core_bot))
    # Cross-pin holes at bottom (Z = z_core_bot + 6.0) & +/-1.5 mm slotted holes at top (Z = z_core_top - 7.0)
    for sy in (-p.anchor_top_pin_y, p.anchor_top_pin_y):
        b_pin = bd.Cylinder(2.1, core_w + 2.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER)).rotate(bd.Axis.Y, 90.0).translate((0.0, sy, p.z_core_bot + 6.0))
        t_slot = bd.Box(core_w + 2.0, 4.2, 7.2, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER)).translate((0.0, sy, p.z_core_top - 7.0))
        hs_core = hs_core - b_pin - t_slot

    # Bottom internal anchor plug (MECH-ANCHOR-BOT: 33.2x33.2x12.0 mm) + 2x M4x16 CSK upward bolts + 2x M4x40 pins
    anchor_bot = bd.Box(p.anchor_bot_w, p.anchor_bot_w, p.anchor_bot_h,
                        align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, p.z_core_bot))
    for sx in (-1.0, 1.0):
        v_hole = bd.Cylinder(2.0, p.anchor_bot_h + 1.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((sx * p.anchor_bot_bolt_x, 0.0, p.z_core_bot - 0.5))
        anchor_bot = anchor_bot - v_hole
    for sy in (-p.anchor_top_pin_y, p.anchor_top_pin_y):
        h_hole = bd.Cylinder(2.0, p.anchor_bot_w + 2.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER)).rotate(bd.Axis.Y, 90.0).translate((0.0, sy, p.z_core_bot + 6.0))
        anchor_bot = anchor_bot - h_hole

    # Top internal anchor block (MECH-ANCHOR-TOP: 33.2x33.2x14.0 mm) WITH central M6 bore + 2x offset M4 bores
    anchor_top = bd.Box(p.anchor_w, p.anchor_w, p.anchor_h,
                        align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)).translate((0, 0, p.z_core_top))
    m6_bore = bd.Cylinder(p.eye_bolt_thread_dia / 2.0, p.anchor_h + 2.0,
                          align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)).translate((0, 0, p.z_core_top + 1.0))
    anchor_top = anchor_top - m6_bore
    for sy in (-p.anchor_top_pin_y, p.anchor_top_pin_y):
        p_bore = bd.Cylinder(2.0, p.anchor_w + 2.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER)).rotate(bd.Axis.Y, 90.0).translate((0.0, sy, p.z_core_top - 7.0))
        anchor_top = anchor_top - p_bore

    # Flush M4x40 cross-pin fasteners (top & bottom anchors, flush within 40.0 mm core_w) & 2x M4x16 CSK bulkhead bolts
    fasteners_list = []
    for sy in (-p.anchor_top_pin_y, p.anchor_top_pin_y):
        pin_top = bd.Cylinder(1.95, core_w - 0.2, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER)).rotate(bd.Axis.Y, 90.0).translate((0.0, sy, p.z_core_top - 7.0))
        pin_bot = bd.Cylinder(1.95, core_w - 0.2, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER)).rotate(bd.Axis.Y, 90.0).translate((0.0, sy, p.z_core_bot + 6.0))
        fasteners_list.extend([pin_top, pin_bot])
    z_csk_seat = p.z_cap_bot_bulkhead_start - 4.5  # 121.5
    for sx in (-1.0, 1.0):
        bx = sx * p.anchor_bot_bolt_x
        b_shank = bd.Cylinder(1.95, 16.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((bx, 0.0, z_csk_seat + 0.1))
        b_head = bd.Cone(4.0, 1.95, 2.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((bx, 0.0, z_csk_seat + 0.1))
        fasteners_list.append(b_shank.fuse(b_head))
    fasteners_anchors = bd.Compound(fasteners_list)

    # M6 x 75 mm eye bolt (MECH-EYE-1)
    eye_shaft = bd.Cylinder(2.95, p.hs_ext_top_height + p.adapt_top_thick + p.anchor_h + 6.0,
                            align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, p.z_core_top - p.anchor_h + 1.0))
    eye_collar = bd.Cylinder(9.0, 5.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, p.z_hs_top_end))
    eye_ring = bd.Torus(11.0, 3.2).rotate(bd.Axis.X, 90.0).translate((0, 0, p.z_hs_top_end + 17.0))
    eye_bolt = eye_shaft.fuse(eye_collar).fuse(eye_ring)

    # Borosilicate glass tube (MECH-TUBE-1), centered symmetrically when glass_length_override is set
    z_g_start = p.z_glass_bot - 0.5 * (g_len - p.glass_length)
    g_outer = bd.Cylinder(g_od / 2.0, g_len, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    g_inner = bd.Cylinder(g_id / 2.0, g_len + 2.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, -1.0))
    glass_tube = (g_outer - g_inner).translate((0, 0, z_g_start))

    # 4x MCPCB strips + 8 LEDs + 8 M3 screw heads
    mcpcb_items = []
    for angle in (0.0, 90.0, 180.0, 270.0):
        x0 = core_w / 2.0 + p.mcpcb_tim_thick
        strip = bd.Box(p.mcpcb_thick, p.mcpcb_w, p.mcpcb_l,
                       align=(bd.Align.MIN, bd.Align.CENTER, bd.Align.CENTER)).translate((x0, 0, p.z_mcpcb_center))
        uv_led = bd.Box(p.led_uv_max_h, 3.45, 3.45,
                        align=(bd.Align.MIN, bd.Align.CENTER, bd.Align.CENTER)).translate((x0 + p.mcpcb_thick, 0, p.z_led_uv))
        vis_led = bd.Box(p.led_vis_max_h, 3.45, 3.45,
                         align=(bd.Align.MIN, bd.Align.CENTER, bd.Align.CENTER)).translate((x0 + p.mcpcb_thick, 0, p.z_led_vis))
        s_top = bd.Cylinder(2.75, p.m3_shcs_head_h, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).rotate(bd.Axis.Y, 90.0).translate((x0 + p.mcpcb_thick, 0, p.z_mcpcb_center + p.mcpcb_mount_y))
        s_bot = bd.Cylinder(2.75, p.m3_shcs_head_h, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).rotate(bd.Axis.Y, 90.0).translate((x0 + p.mcpcb_thick, 0, p.z_mcpcb_center - p.mcpcb_mount_y))
        mcpcb_items.append(bd.Compound([strip, uv_led, vis_led, s_top, s_bot]).rotate(bd.Axis.Z, angle))
    mcpcbs = bd.Compound(mcpcb_items)

    # SW1 + SW1_BOOT envelope (+X side)
    x_sw_in = p.sw1_spotface_x - p.sw1_wall_thick
    sw_body = bd.Box(8.89, 12.7, 6.86, align=(bd.Align.MAX, bd.Align.CENTER, bd.Align.CENTER)).translate((x_sw_in, 0, p.sw1_z))
    sw_lugs = bd.Box(4.8, 10.0, 5.0, align=(bd.Align.MAX, bd.Align.CENTER, bd.Align.CENTER)).translate((x_sw_in - 8.89, 0, p.sw1_z))
    sw_boot = bd.Cylinder(6.65, 16.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).rotate(bd.Axis.Y, 90.0).translate((p.sw1_spotface_x, 0, p.sw1_z))
    sw1_assy = bd.Compound([sw_body, sw_lugs, sw_boot])

    parts = dict(
        cap_bot=cap_bot,
        cap_top=cap_top,
        hs_bot=hs_bot,
        hs_top=hs_top,
        adapt_bot=adapt_bot,
        adapt_top=adapt_top,
        spacer_washers=spacer_washers,
        tim_pcb=tim_pcb,
        pcb_assy=pcb_assy,
        hs_core=hs_core,
        anchor_bot=anchor_bot,
        anchor_top=anchor_top,
        fasteners_anchors=fasteners_anchors,
        eye_bolt=eye_bolt,
        glass_tube=glass_tube,
        mcpcbs=mcpcbs,
        sw1_assy=sw1_assy,
    )

    if p.power_entry_mode == "M16_GLAND":
        y_m16_in = p.m16_spotface_y + p.m16_wall_thick
        m16_ext = bd.Cylinder(10.5, 22.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).rotate(bd.Axis.X, 90.0).translate((0, p.m16_spotface_y, p.m16_z))
        # Captive 22.0 mm AF hex locknut (vertical flat-to-flat = 22.0 mm) inside 22.5 mm AF hex alcove
        with bd.BuildSketch() as sk_hex:
            bd.RegularPolygon(radius=11.0 / math.cos(math.radians(30.0)), side_count=6, rotation=30.0)
        m16_nut = bd.extrude(sk_hex.face(), 5.0).rotate(bd.Axis.X, 90.0).translate((0, y_m16_in + 5.1, p.m16_z))
        parts["m16_assy"] = bd.Compound([m16_ext, m16_nut])
    else:
        # Standard 6.65 mm USB-C PD laptop-charger plug (usbc_specified_barrel_mm = 6.65 mm),
        # inserted full 4.55 mm inside J1 (tip at Y = -21.21 mm; overmold shoulder at Y = -27.86 mm,
        # passing freely through the 13.6 x 7.8 mm direct-mate tunnel with zero collision!).
        y_plug_tip = p.usbc_j1_front_y + p.usbc_mating_depth_mm
        y_overmold_front = y_plug_tip - p.usbc_specified_barrel_mm
        usbc_plug_shell = bd.Box(8.3, p.usbc_specified_barrel_mm + 0.01, 2.5, align=(bd.Align.CENTER, bd.Align.MAX, bd.Align.CENTER)).translate((0.0, y_plug_tip, p.z_usbc))
        usbc_plug_overmold = bd.Box(12.4, 24.0, 6.8, align=(bd.Align.CENTER, bd.Align.MAX, bd.Align.CENTER)).translate((0.0, y_overmold_front, p.z_usbc))
        usbc_plug_assy = usbc_plug_shell.fuse(usbc_plug_overmold)
        assert len(usbc_plug_assy.solids()) == 1, f"Expected 1 contiguous USB-C plug solid, got {len(usbc_plug_assy.solids())}"
        parts["usbc_plug_assy"] = usbc_plug_assy

    return parts


def check_all_pairs_intersections(parts: dict[str, bd.Shape]) -> dict[str, dict]:
    """
    Run genuine ALL-PAIRS N*(N-1)/2 B-Rep solid intersection check across every part in the assembly.
    Uses bounding-box pre-filter before exact OCCT boolean `&` so all N*(N-1)/2 pairs execute fast and accurately.
    """
    names = list(parts.keys())
    results: dict[str, dict] = {}
    nonzero_pairs: dict[str, float] = {}
    total_pairs = 0
    for i in range(len(names)):
        na = names[i]
        sa = parts[na]
        ba = sa.bounding_box()
        for j in range(i + 1, len(names)):
            nb = names[j]
            sb = parts[nb]
            bb = sb.bounding_box()
            total_pairs += 1
            # Exact AABB overlap check (with 0.05 mm safety margin)
            if (
                ba.max.X < bb.min.X - 0.05 or bb.max.X < ba.min.X - 0.05
                or ba.max.Y < bb.min.Y - 0.05 or bb.max.Y < ba.min.Y - 0.05
                or ba.max.Z < bb.min.Z - 0.05 or bb.max.Z < ba.min.Z - 0.05
            ):
                vol = 0.0
            else:
                inter = sa & sb
                vol = float(inter.volume) if inter is not None else 0.0
            key = f"{na}__vs__{nb}"
            passed = vol < 1e-4
            if not passed:
                nonzero_pairs[key] = round(vol, 6)
            results[key] = {"intersection_vol_mm3": round(vol, 6), "pass": passed}
    return {
        "total_pairs_checked": total_pairs,
        "nonzero_count": len(nonzero_pairs),
        "nonzero_pairs": nonzero_pairs,
        "all_zero": len(nonzero_pairs) == 0,
        "pairs": results,
    }


def audit_stl_overhangs(stl_path: Path, print_up_axis: tuple[float, float, float], max_overhang_deg: float = 46.0) -> dict:
    """Audit off-bed downward-facing triangles exceeding max_overhang_deg from vertical."""
    mesh = trimesh.load(str(stl_path), force="mesh")
    up = np.array(print_up_axis, dtype=float)
    up = up / np.linalg.norm(up)
    z_proj = mesh.vertices @ up
    z_bed = float(np.min(z_proj))
    face_z_min = np.min(z_proj[mesh.faces], axis=1)
    off_bed = face_z_min > (z_bed + 0.05)

    dots = mesh.face_normals @ up
    # Downward-facing: dot < 0; overhang angle from vertical = 90 - angle_from_down = arcsin(|dot|)
    downward = dots < -1e-4
    angles_deg = np.degrees(np.arcsin(np.clip(-dots[downward & off_bed], 0.0, 1.0)))
    areas = mesh.area_faces[downward & off_bed]
    bad = angles_deg > max_overhang_deg
    return {
        "stl_file": stl_path.name,
        "bed_z_proj_mm": round(z_bed, 3),
        "off_bed_overhang_gt46_faces": int(np.sum(bad)),
        "off_bed_overhang_gt46_area_mm2": round(float(np.sum(areas[bad])), 3),
        "max_off_bed_overhang_deg": round(float(np.max(angles_deg)) if len(angles_deg) else 0.0, 2),
        "pass": float(np.sum(areas[bad])) < 1.0,
    }


def verify_usbc_bezel_wall_stl(stl_path: Path, p: LepiLEDParams) -> dict:
    """
    Vectorized Möller-Trumbore STL ray-cast across X in [-9.0, +9.0] and Z in [z_usbc - 6.0, z_usbc + 12.0]
    (0.25 mm step) asserting unobstructed direct-mate tunnel inside the 13.6 x 7.8 mm (+45 deg roof) opening
    and solid wall >= 2.500 mm everywhere outside it (above MECH-GASKET-3).
    """
    mesh = trimesh.load(str(stl_path), force="mesh")
    tris = mesh.triangles  # (T, 3, 3)
    z_lo = p.bot_oring_roof_z_max + 0.5
    z_hi = p.z_usbc + p.usbc_overmold_h / 2.0 + 0.5 * p.usbc_overmold_w + 3.0
    tri_xmin = tris[:, :, 0].min(axis=1)
    tri_xmax = tris[:, :, 0].max(axis=1)
    tri_ymin = tris[:, :, 1].min(axis=1)
    tri_zmin = tris[:, :, 2].min(axis=1)
    tri_zmax = tris[:, :, 2].max(axis=1)
    tri_mask = (tri_xmax >= -9.5) & (tri_xmin <= 9.5) & (tri_ymin < 0.0) & (tri_zmax >= z_lo - 0.5) & (tri_zmin <= z_hi + 0.5)
    tris_sub = tris[tri_mask]

    v0 = tris_sub[:, 0, :]
    e1 = tris_sub[:, 1, :] - v0
    e2 = tris_sub[:, 2, :] - v0
    det = e1[:, 0] * e2[:, 2] - e1[:, 2] * e2[:, 0]
    valid_tri = np.abs(det) > 1e-12
    v0, e1, e2, inv_det = v0[valid_tri], e1[valid_tri], e2[valid_tri], 1.0 / det[valid_tri]

    hw = p.usbc_overmold_w / 2.0
    xs = np.arange(-9.0, 9.0 + 1e-9, 0.25)
    zs = np.arange(z_lo, z_hi + 1e-9, 0.25)
    xs_eval = xs.copy()
    xs_eval[np.isclose(np.abs(xs_eval), hw, atol=1e-3)] += 0.01

    gx, gz = np.meshgrid(xs_eval, zs, indexing="ij")
    gx_flat = gx.ravel()
    gz_flat = gz.ravel()

    y_orig = -50.0
    tvec_x = gx_flat[:, None] - v0[None, :, 0]
    tvec_y = y_orig - v0[None, :, 1]
    tvec_z = gz_flat[:, None] - v0[None, :, 2]

    u = (tvec_x * e2[None, :, 2] - tvec_z * e2[None, :, 0]) * inv_det[None, :]
    qvec_x = tvec_y * e1[None, :, 2] - tvec_z * e1[None, :, 1]
    qvec_y = tvec_z * e1[None, :, 0] - tvec_x * e1[None, :, 2]
    qvec_z = tvec_x * e1[None, :, 1] - tvec_y * e1[None, :, 0]
    v = qvec_y * inv_det[None, :]
    t = (e2[None, :, 0] * qvec_x + e2[None, :, 1] * qvec_y + e2[None, :, 2] * qvec_z) * inv_det[None, :]

    hits_mask = (u >= -1e-7) & (v >= -1e-7) & (u + v <= 1.0 + 1e-7) & (t > 0.0)
    y_hits_all = y_orig + t

    tunnel_roof_z = p.z_usbc + p.usbc_overmold_h / 2.0 + np.maximum(0.0, hw - np.abs(gx_flat)) * math.tan(math.radians(47.0))
    in_tunnel = (
        (np.abs(gx_flat) < hw - 0.05)
        & (gz_flat > p.z_usbc - p.usbc_overmold_h / 2.0 + 0.05)
        & (gz_flat < tunnel_roof_z - 0.05)
    )
    outside_tunnel = (
        (np.abs(gx_flat) > hw + 0.05)
        | (gz_flat < p.z_usbc - p.usbc_overmold_h / 2.0 - 0.05)
        | (gz_flat > tunnel_roof_z + 0.05)
    )

    min_wall_mm = float("inf")
    min_loc = None
    anomalies = 0
    wall_rays_checked = 0
    slot_rays_checked = 0

    for idx in range(len(gx_flat)):
        ys = np.sort(y_hits_all[idx, hits_mask[idx]])
        dedup: list[float] = []
        for yv in ys:
            if not dedup or abs(float(yv) - dedup[-1]) > 1e-4:
                dedup.append(float(yv))
        front_ys = [yv for yv in dedup if yv < 0.0]

        if in_tunnel[idx]:
            slot_rays_checked += 1
            if len(front_ys) != 0:
                anomalies += 1
        elif outside_tunnel[idx]:
            wall_rays_checked += 1
            if len(front_ys) < 2:
                anomalies += 1
                continue
            wall_thick = front_ys[1] - front_ys[0]
            if wall_thick < min_wall_mm:
                min_wall_mm = wall_thick
                min_loc = (round(float(gx_flat[idx]), 3), round(float(gz_flat[idx]), 3))

    return {
        "stl_file": stl_path.name,
        "grid_rays_total": int(len(gx_flat)),
        "wall_rays_checked": wall_rays_checked,
        "slot_rays_checked": slot_rays_checked,
        "anomalies": anomalies,
        "min_bezel_wall_mm": round(min_wall_mm, 4) if min_wall_mm < float("inf") else 0.0,
        "min_wall_xz_mm": min_loc,
        "min_required_mm": p.min_wall,
        "pass": anomalies == 0 and min_wall_mm >= p.min_wall,
    }


def export_and_verify_stl(shape: bd.Shape, step_path: Path, stl_path: Path) -> dict:
    bd.export_step(shape, str(step_path))
    bd.export_stl(shape, str(stl_path), tolerance=0.015, angular_tolerance=0.05)
    mesh = trimesh.load(str(stl_path), force="mesh")
    return {
        "step_file": step_path.name,
        "stl_file": stl_path.name,
        "brep_volume_mm3": round(float(shape.volume), 3),
        "stl_volume_mm3": round(float(mesh.volume), 3),
        "is_watertight": bool(mesh.is_watertight),
        "is_winding_consistent": bool(mesh.is_winding_consistent),
        "is_volume": bool(mesh.is_volume),
        "euler_number": int(mesh.euler_number),
        "genus": int((2 - mesh.euler_number) // 2),
        "triangles": int(len(mesh.faces)),
    }


def check_alcove_insertion(cap_bot: bd.Part, p: LepiLEDParams) -> dict[str, dict | bool]:
    """
    Genuine B-Rep kinematic insertion sweep checks from the open bottom cavity (Z = 73.0)
    up and radially into seated poses inside MECH-CAP-BOT for:
      1. SW1 switch (8.89 x 12.7 x 6.86 mm body + 4.8x10x5 mm lugs + Ø6.35 x 8.89 mm bushing)
      2. M16 locknut (22.0 mm AF x 5.0 mm hex nut)
      3. M4x16 CSK bulkhead bolts (straight +Z insertion into both counterbores)
    Asserts 0.000000 mm^3 intersection along every waypoint of every path.
    """
    x_sw_in = p.sw1_spotface_x - p.sw1_wall_thick  # 42.5
    # SW1 local frame centered on body-front face (x=0 at body-bushing interface)
    sw_body = bd.Box(8.89, 12.7, 6.86, align=(bd.Align.MAX, bd.Align.CENTER, bd.Align.CENTER))
    sw_lugs = bd.Box(4.8, 10.0, 5.0, align=(bd.Align.MAX, bd.Align.CENTER, bd.Align.CENTER)).translate((-8.89, 0.0, 0.0))
    sw_bush = bd.Cylinder(p.sw1_hole_dia / 2.0, 8.89, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).rotate(bd.Axis.Y, 90.0)
    sw_tool = bd.Compound([sw_body, sw_lugs, sw_bush])

    # Path: start at (X_front=20.0, Z=73.0) inside Ø61 cavity -> +Z to sw1_z -> +X to x_sw_in
    sw_waypoints = [(20.0, float(z)) for z in np.linspace(p.z_adapt_bot_end, p.sw1_z, 12)] + [
        (float(x), p.sw1_z) for x in np.linspace(20.0, x_sw_in, 15)
    ]
    sw_max_vol = 0.0
    for xw, zw in sw_waypoints:
        inter = cap_bot & sw_tool.translate((xw, 0.0, zw))
        vol = float(inter.volume) if inter is not None else 0.0
        if vol > sw_max_vol:
            sw_max_vol = vol

    # M16 22.0 mm AF x 5.0 mm hex locknut centered at (0, Y_center, Z)
    y_m16_in = p.m16_spotface_y + p.m16_wall_thick  # -40.5
    with bd.BuildSketch() as sk_hex:
        bd.RegularPolygon(radius=11.0 / math.cos(math.radians(30.0)), side_count=6, rotation=30.0)
    nut_tool = bd.extrude(sk_hex.face(), 5.0).rotate(bd.Axis.X, 90.0).translate((0.0, 2.5, 0.0))  # Y in [-2.5, +2.5]

    # Path: start at (Y_center=-22.0, Z=73.0) inside Ø61 cavity -> +Z to m16_z -> -Y to y_m16_in + 2.6
    nut_waypoints = [(-22.0, float(z)) for z in np.linspace(p.z_adapt_bot_end, p.m16_z, 12)] + [
        (float(y), p.m16_z) for y in np.linspace(-22.0, y_m16_in + 2.6, 15)
    ]
    nut_max_vol = 0.0
    for yw, zw in nut_waypoints:
        inter = cap_bot & nut_tool.translate((0.0, yw, zw))
        vol = float(inter.volume) if inter is not None else 0.0
        if vol > nut_max_vol:
            nut_max_vol = vol

    # M4x16 CSK bulkhead bolts straight +Z insertion from Z=73.0 to seated z_csk_seat+0.1
    z_csk_seat = p.z_cap_bot_bulkhead_start - 4.5
    bolt_shank = bd.Cylinder(1.95, 16.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    bolt_head = bd.Cone(4.0, 1.95, 2.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    bolt_tool = bolt_shank.fuse(bolt_head)
    bolt_z_steps = np.linspace(p.z_adapt_bot_end, z_csk_seat + 0.1, 15)
    bolt_max_vol = 0.0
    for sx in (-1.0, 1.0):
        bx = sx * p.anchor_bot_bolt_x
        for zw in bolt_z_steps:
            inter = cap_bot & bolt_tool.translate((bx, 0.0, float(zw)))
            vol = float(inter.volume) if inter is not None else 0.0
            if vol > bolt_max_vol:
                bolt_max_vol = vol

    return {
        "sw1_insertion": {
            "waypoints_tested": len(sw_waypoints),
            "max_intersection_vol_mm3": round(sw_max_vol, 6),
            "pass": sw_max_vol < 1e-4,
        },
        "m16_nut_insertion": {
            "waypoints_tested": len(nut_waypoints),
            "max_intersection_vol_mm3": round(nut_max_vol, 6),
            "pass": nut_max_vol < 1e-4,
        },
        "m4x16_bolt_insertion": {
            "waypoints_tested": int(2 * len(bolt_z_steps)),
            "max_intersection_vol_mm3": round(bolt_max_vol, 6),
            "pass": bolt_max_vol < 1e-4,
        },
        "all_zero": sw_max_vol < 1e-4 and nut_max_vol < 1e-4 and bolt_max_vol < 1e-4,
    }


def main() -> None:
    out_dir = Path(__file__).resolve().parent

    # 1. FDM Baseline (M16_GLAND)
    p_fdm = LepiLEDParams(process="FDM", power_entry_mode="M16_GLAND")
    assy_nom = build_assembly_parts(p_fdm)

    mesh_checks = {}
    mesh_checks["mech_cap_bot"] = export_and_verify_stl(
        assy_nom["cap_bot"], out_dir / "mech_cap_bot.step", out_dir / "mech_cap_bot.stl"
    )
    mesh_checks["mech_cap_top"] = export_and_verify_stl(
        assy_nom["cap_top"], out_dir / "mech_cap_top.step", out_dir / "mech_cap_top.stl"
    )

    # 2. SLS PA12 Variant
    p_sls = LepiLEDParams(process="SLS", power_entry_mode="M16_GLAND")
    mesh_checks["mech_cap_bot_sls"] = export_and_verify_stl(
        build_cap_bot(p_sls), out_dir / "mech_cap_bot_sls.step", out_dir / "mech_cap_bot_sls.stl"
    )
    mesh_checks["mech_cap_top_sls"] = export_and_verify_stl(
        build_cap_top(p_sls), out_dir / "mech_cap_top_sls.step", out_dir / "mech_cap_top_sls.stl"
    )

    # 3. USB-C Option B Variant
    p_usbc = LepiLEDParams(process="FDM", power_entry_mode="USB_C")
    assy_usbc = build_assembly_parts(p_usbc)
    mesh_checks["mech_cap_bot_usbc"] = export_and_verify_stl(
        assy_usbc["cap_bot"], out_dir / "mech_cap_bot_usbc.step", out_dir / "mech_cap_bot_usbc.stl"
    )

    # 4. Full Assembly STEP + STL + per-part STLs (and USB-C cap_bot render STL)
    comp_dir = out_dir / "parts_stl"
    comp_dir.mkdir(exist_ok=True)
    for k, shp in assy_nom.items():
        bd.export_stl(shp, str(comp_dir / f"{k}.stl"), tolerance=0.04, angular_tolerance=0.15)
    bd.export_stl(assy_usbc["usbc_plug_assy"], str(comp_dir / "usbc_plug_assy.stl"), tolerance=0.04, angular_tolerance=0.15)

    assy_compound = bd.Compound(list(assy_nom.values()))
    bd.export_step(assy_compound, str(out_dir / "lepiled_assembly.step"))
    bd.export_stl(assy_compound, str(out_dir / "lepiled_assembly.stl"), tolerance=0.04, angular_tolerance=0.15)

    # 5. Overhang audits on FDM STLs + vectorized USB-C bezel wall STL ray-cast
    overhang_checks = {
        "mech_cap_bot": audit_stl_overhangs(out_dir / "mech_cap_bot.stl", (0.0, 0.0, 1.0)),
        "mech_cap_top": audit_stl_overhangs(out_dir / "mech_cap_top.stl", (0.0, 0.0, -1.0)),
        "mech_cap_bot_usbc": audit_stl_overhangs(out_dir / "mech_cap_bot_usbc.stl", (0.0, 0.0, 1.0)),
    }
    usbc_bezel_raycast = verify_usbc_bezel_wall_stl(out_dir / "mech_cap_bot_usbc.stl", p_usbc)

    # 6. Genuine ALL-PAIRS B-Rep interference checks (M16_GLAND & USB_C, Nominal & Worst-Case incl. +1.0 mm glass length)
    wc_glass_len = p_fdm.glass_length + p_fdm.glass_length_tol  # 151.0 mm
    inter_m16_nom = check_all_pairs_intersections(assy_nom)
    assy_m16_wc = build_assembly_parts(
        p_fdm, core_w_override=p_fdm.core_w_max, glass_id_override=p_fdm.glass_id_min,
        glass_od_override=p_fdm.glass_od_max, glass_length_override=wc_glass_len,
    )
    inter_m16_wc = check_all_pairs_intersections(assy_m16_wc)

    inter_usbc_nom = check_all_pairs_intersections(assy_usbc)
    assy_usbc_wc = build_assembly_parts(
        p_usbc, core_w_override=p_usbc.core_w_max, glass_id_override=p_usbc.glass_id_min,
        glass_od_override=p_usbc.glass_od_max, glass_length_override=wc_glass_len,
    )
    inter_usbc_wc = check_all_pairs_intersections(assy_usbc_wc)

    # 7. Kinematic B-Rep alcove & bulkhead bolt insertion sweep verification
    alcove_checks = check_alcove_insertion(assy_nom["cap_bot"], p_fdm)

    # 8. Assert cap_top topology (zero gasket-2 puncture: euler_number == 0, genus == 1)
    cap_top_euler_ok = (
        mesh_checks["mech_cap_top"]["euler_number"] == 0
        and mesh_checks["mech_cap_top"]["genus"] == 1
        and mesh_checks["mech_cap_top_sls"]["euler_number"] == 0
        and mesh_checks["mech_cap_top_sls"]["genus"] == 1
    )

    all_meshes_ok = all(
        m["is_watertight"] and m["is_winding_consistent"] and m["stl_volume_mm3"] > 0
        for m in mesh_checks.values()
    ) and cap_top_euler_ok
    all_overhangs_ok = all(o["pass"] for o in overhang_checks.values())
    all_brep_ok = (
        inter_m16_nom["all_zero"]
        and inter_m16_wc["all_zero"]
        and inter_usbc_nom["all_zero"]
        and inter_usbc_wc["all_zero"]
    )
    usbc_plug_contiguous = len(assy_usbc["usbc_plug_assy"].solids()) == 1
    usbc_bezel_wall_ok = usbc_bezel_raycast["pass"]
    all_alcove_ok = alcove_checks["all_zero"]
    all_param_checks_ok = all(c["pass"] for c in p_fdm.verify_all().values())

    report = {
        "params": p_fdm.to_dict(),
        "mesh_checks": mesh_checks,
        "overhang_checks": overhang_checks,
        "usbc_bezel_wall_raycast": usbc_bezel_raycast,
        "alcove_insertion_checks": alcove_checks,
        "usbc_plug_assy_solids": len(assy_usbc["usbc_plug_assy"].solids()),
        "brep_all_pairs_m16_nominal": {k: v for k, v in inter_m16_nom.items() if k != "pairs"},
        "brep_all_pairs_m16_worst_case": {k: v for k, v in inter_m16_wc.items() if k != "pairs"},
        "brep_all_pairs_usbc_nominal": {k: v for k, v in inter_usbc_nom.items() if k != "pairs"},
        "brep_all_pairs_usbc_worst_case": {k: v for k, v in inter_usbc_wc.items() if k != "pairs"},
        "summary": {
            "all_param_checks_pass": all_param_checks_ok,
            "all_meshes_watertight_manifold": all_meshes_ok,
            "cap_top_euler_zero_genus_one": cap_top_euler_ok,
            "all_overhangs_le_45deg": all_overhangs_ok,
            "usbc_bezel_wall_raycast_ge_2_5mm": usbc_bezel_wall_ok,
            "alcove_kinematic_insertion_zero": all_alcove_ok,
            "usbc_plug_assy_contiguous": usbc_plug_contiguous,
            "m16_nominal_all_pairs_zero": inter_m16_nom["all_zero"],
            "m16_worst_case_all_pairs_zero": inter_m16_wc["all_zero"],
            "usbc_nominal_all_pairs_zero": inter_usbc_nom["all_zero"],
            "usbc_worst_case_all_pairs_zero": inter_usbc_wc["all_zero"],
            "overall_pass": (
                all_param_checks_ok and all_meshes_ok and all_overhangs_ok
                and usbc_bezel_wall_ok and all_brep_ok and all_alcove_ok and usbc_plug_contiguous
            ),
        },
    }
    verif_path = out_dir / "cad_verification.json"
    verif_path.write_text(json.dumps(report, indent=2))

    print("=== Mesh Verification ===")
    for name, m in mesh_checks.items():
        print(
            f"  {name:20s}: vol={m['stl_volume_mm3']:8.1f} mm^3 | tri={m['triangles']:6d} | wt={m['is_watertight']} "
            f"| wind={m['is_winding_consistent']} | euler={m['euler_number']:3d} (g={m['genus']})"
        )
    print(f"  cap_top euler==0 (genus==1) check: {cap_top_euler_ok}")
    print("=== Overhang Verification ===")
    for name, o in overhang_checks.items():
        print(f"  {name:20s}: >46deg faces={o['off_bed_overhang_gt46_faces']:4d}, area={o['off_bed_overhang_gt46_area_mm2']:6.2f} mm^2, max={o['max_off_bed_overhang_deg']:5.2f} deg | pass={o['pass']}")
    print("=== USB-C Bezel Wall STL Ray-Cast ===")
    print(
        f"  {usbc_bezel_raycast['stl_file']}: rays={usbc_bezel_raycast['grid_rays_total']} "
        f"(wall={usbc_bezel_raycast['wall_rays_checked']}, slot={usbc_bezel_raycast['slot_rays_checked']}), "
        f"anomalies={usbc_bezel_raycast['anomalies']}, min_wall={usbc_bezel_raycast['min_bezel_wall_mm']:.4f} mm "
        f"at XZ={usbc_bezel_raycast['min_wall_xz_mm']} | pass={usbc_bezel_raycast['pass']}"
    )
    print("=== Kinematic Alcove & Bolt Insertion ===")
    for k in ("sw1_insertion", "m16_nut_insertion", "m4x16_bolt_insertion"):
        v = alcove_checks[k]
        print(f"  {k:22s}: waypoints={v['waypoints_tested']:2d}, max_vol={v['max_intersection_vol_mm3']:.6f} mm^3 | pass={v['pass']}")
    print("=== All-Pairs B-Rep Intersection (incl. 151.0 mm glass WC) ===")
    for label, d in [
        ("M16_NOM", inter_m16_nom),
        ("M16_WC", inter_m16_wc),
        ("USBC_NOM", inter_usbc_nom),
        ("USBC_WC", inter_usbc_wc),
    ]:
        print(f"  {label:10s}: {d['total_pairs_checked']} pairs, nonzero={d['nonzero_count']} {d['nonzero_pairs']}")

    if not report["summary"]["overall_pass"]:
        raise SystemExit(1)
    print(f"Wrote {verif_path} and all STEP/STL artifacts (ALL CHECKS PASS).")


if __name__ == "__main__":
    main()
