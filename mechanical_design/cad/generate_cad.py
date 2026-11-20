#!/usr/bin/env python3
"""
Parametric 3D CAD Generator for LepiLED DIY Maxi Switch (Rev 4.2 — Lean 1-Off Hobby Build) using build123d.

Exports (100% support-free FDM PETG/ASA):
  - mech_lid_bot.step / .stl       (Flat Ø92 x 4 mm lid w/ 4x integral 11.5 mm PCB bosses & Ø2.45 mm locating pins)
  - mech_cap_bot.step / .stl       (Unified USB-C + Ø20.2 mm grommet flange + C&K 7211 alcove + 4x captive M3 nut slots)
  - mech_cap_top.step / .stl       (Glass seat + 41x41 mm protruding core aperture + silicone groove + 2x M3 lock holes)
  - mech_plug_top.step / .stl      (Weatherproof press-fit rain cap sealing open top of protruding 40x40x3 mm Al tube)
  - mech_plug_bot.step / .stl      (Internal 33.4x33.4x12 mm core plug w/ captive M3 nuts replacing Al bottom anchor)
  - mech_drill_jig.step / .stl     (Snap-on 40.6 mm U-channel drill guide for all 16x M3 holes of 20 mm Copper DTP stars)
  - lepiled_assembly.step          (Full multi-part B-Rep assembly incl. 8x 20 mm DTP stars, fasteners & grommet)
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


def build_lid_bot(p: LepiLEDParams) -> bd.Part:
    """
    Build MECH-LID-BOT: flat 3D-printed Ø92 x 4.0 mm bottom lid with:
      - 4x integral 11.5 mm tall Ø6.2 mm PCB standoff bosses topped with Ø2.45 x 2.0 mm locating pins
        (passes cleanly through Ø2.7 mm isolated NPTH H1..H4 -> ZERO brass inserts & ZERO M2.5 screws!)
      - 4x M3 flush DIN 7991 CSK clearance holes at R = 40.2 mm (mating into captive M3 nuts in cap_bot)
      - Prints flat on Z=0 bed with ZERO >46 deg overhang!
    """
    r_lid = p.lid_bot_od / 2.0
    part = bd.Cylinder(r_lid, p.lid_bot_thick, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    bot_edges = part.edges().filter_by(bd.GeomType.CIRCLE).sort_by(bd.Axis.Z)[:1]
    part = bd.chamfer(bot_edges, length=p.cap_chamfer)

    r_boss = p.pcb_boss_od / 2.0
    r_pin = p.pcb_loc_pin_dia / 2.0
    for sx in (-1.0, 1.0):
        for sy in (-1.0, 1.0):
            bx, by = sx * p.pcb_hole_x, sy * p.pcb_hole_y
            boss = bd.Cylinder(r_boss, p.pcb_boss_h, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((bx, by, p.z_lid_bot_end))
            collar = bd.Cone(r_boss + 1.0, r_boss, 1.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((bx, by, p.z_lid_bot_end))
            pin = bd.Cylinder(r_pin, p.pcb_loc_pin_h - 0.3, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((bx, by, p.z_pcb_bot))
            pin_tip = bd.Cone(r_pin, r_pin - 0.3, 0.3, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((bx, by, p.z_pcb_bot + p.pcb_loc_pin_h - 0.3))
            part = part.fuse(boss).fuse(collar).fuse(pin).fuse(pin_tip)

    for deg in (45.0, 135.0, 225.0, 315.0):
        rad = math.radians(deg)
        hx, hy = p.lid_bot_bolt_r * math.cos(rad), p.lid_bot_bolt_r * math.sin(rad)
        c_thru = bd.Cylinder(p.m3_clearance_dia / 2.0, p.lid_bot_thick + 1.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((hx, hy, -0.5))
        c_csk = bd.Cone(3.20, p.m3_clearance_dia / 2.0, 1.50, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((hx, hy, 0.0))
        part = part - c_thru - c_csk

    return part


def build_cap_bot(p: LepiLEDParams) -> bd.Part:
    """
    Build unified Rev 4.2 MECH-CAP-BOT:
      - Ø92 -> Ø84 mm outer envelope, Ø61 mm PCB cavity + 40.3 deg cone + 6 mm bulkhead
      - MECH-GASKET-3 (66x2.0 mm) optional V-roof groove
      - 4x radial side-entry captive M3 hex-nut pockets at R = 40.2 mm (ZERO brass heat-set inserts!)
      - 2x M3 CSK upward bulkhead bolt holes at (±9.0, 0.0) into 3D-printed MECH-PLUG-BOT
      - -Y side: Flat-faced Ø20.2 x 2.5 mm rubber membrane grommet flange + direct-mate USB-C tunnel
      - +X side: C&K 7211SYZBE gold DPDT switch alcove (15.0 x 13.5 mm + 47 deg roof) & Ø6.35 mm teardrop bore
      - Prints upright (+Z up) with < 1 mm^2 >46 deg overhang (100% support-free!).
    """
    r_bot = p.cap_bot_od / 2.0
    r_top = p.cap_top_od / 2.0
    z_base = p.z_lid_bot_end
    z_top = p.z_cap_bot_top
    z_taper_bot = p.z_glass_bot - 12.0
    z_taper_top = z_taper_bot + (r_bot - r_top)

    c_bot = bd.Cylinder(r_bot, z_taper_bot - z_base, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, z_base))
    c_step = bd.Cone(r_bot, r_top, z_taper_top - z_taper_bot, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, z_taper_bot))
    c_top = bd.Cylinder(r_top, z_top - z_taper_top, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, z_taper_top))
    part = c_bot.fuse(c_step).fuse(c_top)
    bottom_edges = part.edges().filter_by(bd.GeomType.CIRCLE).sort_by(bd.Axis.Z)[:1]
    top_edges = part.edges().filter_by(bd.GeomType.CIRCLE).sort_by(bd.Axis.Z)[-1:]
    part = bd.chamfer(bottom_edges + top_edges, length=p.cap_chamfer)

    # Internal PCB cavity: cylinder + 40.3 deg cone all the way to R=0.02 apex
    r_cav = p.cap_bot_cavity_dia / 2.0
    cav_cyl = bd.Cylinder(r_cav, p.cap_bot_cavity_full_h, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, z_base))
    cav_cone = bd.Cone(r_cav, 0.02, p.cap_bot_taper_h, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, z_base + p.cap_bot_cavity_full_h))
    part = part - cav_cyl.fuse(cav_cone)

    # Bottom O-ring groove (optional 66x2.0 mm O-ring or silicone bead, 45 deg V-roof)
    r_g3_in, r_g3_out = p.bot_oring_r_in, p.bot_oring_r_out
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

    # 4x M3 clearance bores + radial side-entry captive M3 hex-nut pockets (Z = 9.0 .. 11.7 mm, 47 deg pitched roof -> 0 overhang!)
    r_bolt = p.m3_clearance_dia / 2.0
    z_nut_bot = z_base + 5.0  # Z = 9.0 mm (2.95 mm above MECH-GASKET-3 roof!)
    nut_prof = _pitched_rect_profile(p.m3_nut_af, p.m3_nut_thick, 47.0)
    nut_len = (r_bot + 1.0) - (p.lid_bot_bolt_r - p.m3_nut_af / 2.0 - 0.4)  # radial slot from outer wall inward past nut center
    for deg in (45.0, 135.0, 225.0, 315.0):
        rad = math.radians(deg)
        ix, iy = p.lid_bot_bolt_r * math.cos(rad), p.lid_bot_bolt_r * math.sin(rad)
        # Vertical M3 clearance bore from Z_base up through nut slot + 1.5 mm bolt tip room (45 deg cone tip)
        h_tot_bolt = (z_nut_bot - z_base) + p.m3_nut_thick + 2.5
        hole = bd.Cylinder(r_bolt, h_tot_bolt, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((ix, iy, z_base))
        tip = bd.Cone(r_bolt, 0.02, r_bolt - 0.02, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((ix, iy, z_base + h_tot_bolt))
        part = part - hole.fuse(tip)
        # Radial side-entry captive M3 hex-nut slot opening outward at `deg`
        slot = bd.extrude(nut_prof, nut_len).rotate(bd.Axis.X, 90.0).rotate(bd.Axis.Z, 90.0)
        slot = slot.translate((p.lid_bot_bolt_r - p.m3_nut_af / 2.0 - 0.4, 0.0, z_nut_bot)).rotate(bd.Axis.Z, deg)
        part = part - slot

    # Glass socket (Z = 70.0 .. 82.0) + axial O-ring groove (MECH-GASKET-1: 68x3.5 mm)
    r_pilot = p.glass_pilot_od / 2.0
    glass_outer = bd.Cone(p.glass_skirt_id_bot / 2.0, p.glass_skirt_id_top / 2.0, p.glass_socket_depth, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    glass_inner = bd.Cylinder(r_pilot, p.glass_socket_depth, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    glass_slot = (glass_outer - glass_inner).translate((0, 0, p.z_glass_bot))

    g1_out = bd.Cylinder(p.glass_oring_od / 2.0, p.glass_oring_depth + 0.05, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    g1_in = bd.Cylinder(p.glass_oring_id / 2.0, p.glass_oring_depth + 0.05, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    g1 = (g1_out - g1_in).translate((0, 0, p.z_glass_bot - p.glass_oring_depth))
    part = part - glass_slot.fuse(g1)

    # Core socket (41.0 x 41.0 mm, Z = 70.0 .. 82.0) + 4x wire slots opening into cavity cone
    core_sock = bd.Box(p.core_pocket_w, p.core_pocket_w, p.glass_socket_depth,
                       align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, p.z_core_bot))
    part = part - core_sock

    slot_offset = p.core_pocket_w / 2.0 + p.core_wire_slot_d / 2.0 - 0.1
    z_slot_bot = p.z_cap_bot_cavity_taper_start + 5.0
    h_slot = z_top - z_slot_bot
    for angle in (0.0, 90.0, 180.0, 270.0):
        wslot = bd.Box(p.core_wire_slot_d + 0.2, p.core_wire_slot_w, h_slot,
                       align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((slot_offset, 0, z_slot_bot))
        wslot = wslot.rotate(bd.Axis.Z, angle)
        part = part - wslot

    # 2x M3 CSK upward bulkhead holes at (±9.0, 0.0) into 3D-printed MECH-PLUG-BOT (45 deg CSK seat -> 0 overhang!)
    z_csk_seat = p.z_cap_bot_bulkhead_start - 4.5
    for sx in (-1.0, 1.0):
        bx = sx * p.plug_bot_bolt_x
        c_clear = bd.Cylinder(3.4, 12.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((bx, 0.0, z_csk_seat - 12.0))
        c_seat = bd.Cone(3.4, r_bolt, 1.7, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((bx, 0.0, z_csk_seat))
        c_thru = bd.Cylinder(r_bolt, 12.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((bx, 0.0, z_csk_seat + 1.6))
        part = part - c_clear.fuse(c_seat).fuse(c_thru)

    # SW1 (C&K 7211SYZBE gold DPDT) toggle switch cutout (+X side, Y = 0, Z = 30.0 mm)
    sw_sf_face = _teardrop_profile_wire(p.sw1_spotface_dia / 2.0, 45.0)
    sw_sf = bd.extrude(sw_sf_face, 5.0).rotate(bd.Axis.X, 90.0).rotate(bd.Axis.Z, -90.0)
    sw_sf = sw_sf.translate((p.sw1_spotface_x + 5.0, 0.0, p.sw1_z))
    part = part - sw_sf

    x_sw_in = p.sw1_spotface_x - p.sw1_wall_thick
    sw_corridor_len = x_sw_in - 10.0
    sw_prof = _pitched_rect_profile(p.sw1_alcove_w, p.sw1_alcove_h, 47.0)
    sw_alc = bd.extrude(sw_prof, sw_corridor_len).rotate(bd.Axis.X, 90.0).rotate(bd.Axis.Z, -90.0)
    sw_alc = sw_alc.translate((x_sw_in, 0.0, p.sw1_z - p.sw1_alcove_h / 2.0))
    part = part - sw_alc

    sw_td_face = _teardrop_profile_wire(p.sw1_hole_dia / 2.0 + p.print_clearance * 0.5, 45.0)
    sw_hole = bd.extrude(sw_td_face, 8.0).rotate(bd.Axis.X, 90.0).rotate(bd.Axis.Z, -90.0)
    sw_hole = sw_hole.translate((x_sw_in + 5.0, 0.0, p.sw1_z))
    part = part - sw_hole

    # Unified USB-C Direct-Mate Entry + Off-the-Shelf Ø20.2 x 2.5 mm Rubber Grommet Seat (-Y side)
    z_usbc = p.z_usbc
    y_sf = p.grommet_outer_spotface_y
    y_panel_in = y_sf + p.grommet_panel_thick
    y_back_in = y_panel_in + p.grommet_back_relief_depth
    y_tunnel_in = -18.00

    g_sf_face = _teardrop_profile_wire(p.grommet_outer_spotface_dia / 2.0, 45.0)
    g_sf = bd.extrude(g_sf_face, 5.0).rotate(bd.Axis.X, 90.0).translate((0.0, y_sf, z_usbc))
    part = part - g_sf

    g_bore_face = _teardrop_profile_wire(p.grommet_bore_dia / 2.0, 45.0)
    g_bore = bd.extrude(g_bore_face, p.grommet_panel_thick + 1.0).rotate(bd.Axis.X, 90.0).translate((0.0, y_panel_in + 0.5, z_usbc))
    part = part - g_bore

    g_back_face = _teardrop_profile_wire(p.grommet_back_relief_dia / 2.0, 45.0)
    g_back = bd.extrude(g_back_face, p.grommet_back_relief_depth).rotate(bd.Axis.X, 90.0).translate((0.0, y_back_in, z_usbc))
    part = part - g_back

    overmold_len = abs((y_back_in - 0.5) - y_tunnel_in)
    overmold_prof = _pitched_rect_profile(p.usbc_overmold_w, p.usbc_overmold_h, 47.0)
    overmold = bd.extrude(overmold_prof, overmold_len).rotate(bd.Axis.X, 90.0)
    overmold = overmold.translate((0.0, y_tunnel_in, z_usbc - p.usbc_overmold_h / 2.0))
    part = part - overmold

    return part


def build_cap_top(p: LepiLEDParams) -> bd.Part:
    """
    Build Rev 4.2 MECH-CAP-TOP (prints 100% flat inverted, < 1 mm^2 >46 deg overhang):
      - Glass socket + MECH-GASKET-2 (68x3.5 mm) groove
      - 41.0 x 41.0 mm through-aperture for protruding bare 40x40x3 mm Al core + top 1.5 mm silicone-seal bevel
      - 2x radial M3 locking screw bores + counterbores at ±X, Z = 228.5 mm (teardrop flipped -Z for inverted printing!)
        tapping straight into the 3 mm walls of MECH-HS-CORE (ZERO top adapter disc, ZERO inserts!)
    """
    r_cap = p.cap_top_od / 2.0
    z_bot = p.z_cap_top_bot
    z_top = p.z_cap_top_top
    h_tot = z_top - z_bot

    part = bd.Cylinder(r_cap, h_tot, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, z_bot))
    part = bd.chamfer(part.edges().filter_by(bd.GeomType.CIRCLE), length=p.cap_chamfer)

    r_pilot = p.glass_pilot_od / 2.0
    glass_outer = bd.Cone(p.glass_skirt_id_top / 2.0, p.glass_skirt_id_bot / 2.0, p.glass_socket_depth, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    glass_inner = bd.Cylinder(r_pilot, p.glass_socket_depth, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    glass_slot = (glass_outer - glass_inner).translate((0, 0, z_bot))

    g2_out = bd.Cylinder(p.glass_oring_od / 2.0, p.glass_oring_depth + 0.05, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    g2_in = bd.Cylinder(p.glass_oring_id / 2.0, p.glass_oring_depth + 0.05, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    g2 = (g2_out - g2_in).translate((0, 0, p.z_glass_top - 0.05))
    part = part - glass_slot.fuse(g2)

    # Core aperture + 45-deg silicone bead groove around top face (prints directly on bed -> zero overhang!)
    core_thru = bd.Box(p.core_pocket_w, p.core_pocket_w, h_tot + 2.0,
                       align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, z_bot - 1.0))
    part = part - core_thru
    w_g = p.core_pocket_w + 2.0 * p.cap_top_seal_groove
    # 45 deg frustum cut at Z_top for neat silicone bead around protruding Al tube
    with bd.BuildSketch(bd.Plane.XY.offset(z_top)) as sk_top:
        bd.Rectangle(w_g, w_g)
    with bd.BuildSketch(bd.Plane.XY.offset(z_top - p.cap_top_seal_groove)) as sk_bot:
        bd.Rectangle(p.core_pocket_w, p.core_pocket_w)
    seal_chamfer = bd.loft([sk_bot.sketch, sk_top.sketch])
    part = part - seal_chamfer

    # 2x M3 radial locking holes on ±X at Z = 228.5 mm (apex points -Z because cap_top prints inverted on Z_top!)
    z_lock = z_top - p.cap_top_lock_z_from_top
    td_thru = _teardrop_profile_wire(p.m3_clearance_dia / 2.0, 45.0)
    td_cb = _teardrop_profile_wire(3.6, 45.0)  # clears Ø5.5-6.0 mm M3 SHCS/pan head + hex key
    for sx in (-1.0, 1.0):
        # Extrude along +X from core face to outer wall, rotating teardrop so apex points -Z!
        h_lock = bd.extrude(td_thru, 26.0).rotate(bd.Axis.X, -90.0).rotate(bd.Axis.Z, -90.0)
        h_cb = bd.extrude(td_cb, 18.0).rotate(bd.Axis.X, -90.0).rotate(bd.Axis.Z, -90.0)
        if sx > 0:
            h_lock = h_lock.translate((19.0, 0.0, z_lock))
            h_cb = h_cb.translate((27.0, 0.0, z_lock))
        else:
            h_lock = h_lock.rotate(bd.Axis.Z, 180.0).translate((-19.0, 0.0, z_lock))
            h_cb = h_cb.rotate(bd.Axis.Z, 180.0).translate((-27.0, 0.0, z_lock))
        part = part - h_lock - h_cb

    return part


def build_plug_top(p: LepiLEDParams) -> bd.Part:
    """
    Build MECH-PLUG-TOP: 3D-printed weatherproof press-fit rain cap sealing the open top of the protruding
    40 x 40 x 3 mm aluminum tube (prints flat upside-down on Z_plug_top_end with 0.00 mm^2 overhang!).
    """
    # Press-fit insert inside 34.0 mm bore (Z = 310.0 .. 320.0 mm) with 1.0 mm lead-in chamfer
    insert = bd.Box(p.plug_top_w, p.plug_top_w, p.plug_top_insert_h,
                    align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, p.z_core_top - p.plug_top_insert_h))
    insert = bd.fillet(insert.edges().filter_by(bd.Axis.Z), 1.5)
    # Rain-shedding top cap overlapping tube rim (Z = 320.0 .. 324.0 mm)
    cap = bd.Box(p.plug_top_cap_w, p.plug_top_cap_w, p.plug_top_cap_h,
                 align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, p.z_core_top))
    cap = bd.fillet(cap.edges().filter_by(bd.Axis.Z), 1.5)
    top_edges = cap.edges().filter_by_position(bd.Axis.Z, p.z_plug_top_end - 0.1, p.z_plug_top_end + 0.1)
    cap = bd.chamfer(top_edges, length=1.2)
    return insert.fuse(cap)


def build_plug_bot(p: LepiLEDParams) -> bd.Part:
    """
    Build MECH-PLUG-BOT: 3D-printed 33.4 x 33.4 x 12.0 mm internal bottom core plug (replaces aluminum anchor!):
      - 2x vertical M3 clearance bores + top-accessible captive M3 hex-nut pockets at (±9.0, 0) for M3x16 bulkhead bolts
      - 4x horizontal M3 self-tapping/clearance bores at Y = ±9.0, Z = 76.0 mm for flush M3x8 CSK core pins
      - Prints flat on Z = 70.0 mm with ZERO overhang!
    """
    plug = bd.Box(p.plug_bot_w, p.plug_bot_w, p.plug_bot_h,
                  align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, p.z_core_bot))
    plug = bd.fillet(plug.edges().filter_by(bd.Axis.Z), 1.5)

    r_bolt = p.m3_clearance_dia / 2.0
    # 2x vertical M3 bores + top-open captive M3 hex-nut recesses at (±9.0, 0)
    r_hex = p.m3_nut_af / math.sqrt(3.0)
    for sx in (-1.0, 1.0):
        bx = sx * p.plug_bot_bolt_x
        v_bore = bd.Cylinder(r_bolt, p.plug_bot_h + 1.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((bx, 0.0, p.z_core_bot - 0.5))
        with bd.BuildSketch(bd.Plane.XY.offset(p.z_core_bot + p.plug_bot_h - 4.0)) as sk_hex:
            bd.RegularPolygon(r_hex, 6)
        hex_pocket = bd.extrude(sk_hex.sketch, 4.5).translate((bx, 0.0, 0.0))
        plug = plug - v_bore - hex_pocket

    # 2x horizontal M3 through-bores at Y = ±9.0, Z = 76.0 mm (teardrop profile -> support-free!)
    td_pin = _teardrop_profile_wire(1.45, 45.0)  # Ø2.9 mm self-tapping pilot for M3x8 CSK pins from both ±X faces
    for sy in (-p.plug_bot_pin_y, p.plug_bot_pin_y):
        h_pin = bd.extrude(td_pin, p.plug_bot_w + 2.0).rotate(bd.Axis.X, 90.0).rotate(bd.Axis.Z, 90.0)
        h_pin = h_pin.translate((-p.plug_bot_w / 2.0 - 1.0, sy, p.z_core_bot + 6.0))
        plug = plug - h_pin

    return plug


def build_drill_jig(p: LepiLEDParams) -> bd.Part:
    """
    Build MECH-DRILL-JIG: bonus 3D-printed snap-on U-channel drilling template (fits 40.0 mm Al tube)
    that locates all 4 M3 holes per face for the two 20 mm Copper DTP stars (Z_star = ±18 mm, bolts ±9.5 mm)
    plus an end-stop shoulder referencing the bottom end of MECH-HS-CORE (Z_core_bot = 70.0 mm)!
    """
    wall = 3.0
    inner_w = p.core_w_nom + 0.6  # 40.6 mm slip fit
    outer_w = inner_w + 2.0 * wall
    jig_len = 115.0  # covers Z = 70.0 .. 185.0 mm (from bottom end-stop past top UV star screw at Z=172.5!)
    leg_h = 18.0     # clips 15 mm down both side walls of the 40x40 tube

    # Flat back plate (Y = -outer_w/2..+outer_w/2, X = 0..wall) + 2 side legs + bottom end-stop lip
    base = bd.Box(wall, outer_w, jig_len, align=(bd.Align.MIN, bd.Align.CENTER, bd.Align.MIN))
    leg_pos = bd.Box(leg_h, wall, jig_len, align=(bd.Align.MIN, bd.Align.MAX, bd.Align.MIN)).translate((0, outer_w / 2.0, 0))
    leg_neg = bd.Box(leg_h, wall, jig_len, align=(bd.Align.MIN, bd.Align.MIN, bd.Align.MIN)).translate((0, -outer_w / 2.0, 0))
    end_stop = bd.Box(12.0, outer_w, wall, align=(bd.Align.MIN, bd.Align.CENTER, bd.Align.MAX))  # Z = -3 .. 0 end stop
    jig = base.fuse(leg_pos).fuse(leg_neg).fuse(end_stop)

    # 4x Ø2.6 mm M3 tap-drill guide holes along centerline (Y=0) referenced from bottom of core (Z=0 in jig frame):
    # Vis star (Z_rel = 57.0 mm) -> 57.0 ± 9.5 = 47.5, 66.5 mm
    # UV star  (Z_rel = 93.0 mm) -> 93.0 ± 9.5 = 83.5, 102.5 mm
    for z_rel in (
        p.axial_vis_to_bot_mm - p.star_bolt_r,
        p.axial_vis_to_bot_mm + p.star_bolt_r,
        (p.z_led_uv - p.z_core_bot) - p.star_bolt_r,
        (p.z_led_uv - p.z_core_bot) + p.star_bolt_r,
    ):
        guide = bd.Cylinder(1.30, wall + 2.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER)).rotate(bd.Axis.Y, 90.0).translate((wall / 2.0, 0.0, z_rel))
        jig = jig - guide

    # Rotate flat onto XY bed (base plate down on Z=0, legs pointing +Z -> 0.00 mm^2 overhang!)
    jig = jig.rotate(bd.Axis.Y, -90.0).translate((0.0, 0.0, 0.0))
    # Shift so min Z = 0
    bb = jig.bounding_box()
    return jig.translate((0.0, 0.0, -bb.min.Z))


def build_assembly_parts(p: LepiLEDParams, core_w_override: float | None = None,
                         glass_id_override: float | None = None, glass_od_override: float | None = None,
                         glass_length_override: float | None = None) -> dict[str, bd.Shape]:
    """Build all Rev 4.2 physical assembly components (incl. 8x 20 mm Cu DTP stars, fasteners & grommet)."""
    core_w = core_w_override or p.core_w_nom
    g_id = glass_id_override or p.glass_id_nom
    g_od = glass_od_override or p.glass_od_nom
    g_len = glass_length_override or p.glass_length

    lid_bot = build_lid_bot(p)
    cap_bot = build_cap_bot(p)
    cap_top = build_cap_top(p)
    plug_top = build_plug_top(p)
    plug_bot = build_plug_bot(p)

    # Driver PCB (Rev 4.2: USB-C only, isolated NPTH H1..H4 dropped onto MECH-LID-BOT Ø2.45 mm locating pins!)
    pcb_board = bd.Box(p.pcb_w, p.pcb_l, p.pcb_thick, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    pcb_board = bd.fillet(pcb_board.edges().filter_by(bd.Axis.Z), p.pcb_corner_r).translate((0, 0, p.z_pcb_bot))
    for sx in (-1.0, 1.0):
        for sy in (-1.0, 1.0):
            npth = bd.Cylinder(p.pcb_hole_drill / 2.0, p.pcb_thick + 0.4, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((sx * p.pcb_hole_x, sy * p.pcb_hole_y, p.z_pcb_bot - 0.2))
            pcb_board = pcb_board - npth
    l1_smd = bd.Box(6.0, 6.0, 4.5, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((-13.4, 11.1, p.z_pcb_top))
    l2_smd = bd.Box(6.0, 6.0, 4.5, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((13.4, 11.1, p.z_pcb_top))
    j2_hdr = bd.Box(7.4, 5.8, p.pcb_jst_mated_h, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((-5.2, 19.2, p.z_pcb_top))
    j3_hdr = bd.Box(7.4, 5.8, p.pcb_jst_mated_h, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((5.2, 19.2, p.z_pcb_top))
    j4_hdr = bd.Box(9.9, 5.8, p.pcb_jst_mated_h, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((-1.4, -2.5, p.z_pcb_top))
    j1_usbc_outer = bd.Box(8.94, 9.17, 3.46, align=(bd.Align.CENTER, bd.Align.MIN, bd.Align.MIN)).translate((0.0, p.usbc_j1_front_y, p.z_pcb_top))
    j1_cavity = bd.Box(8.34, p.usbc_mating_depth_mm + 0.05, 2.56, align=(bd.Align.CENTER, bd.Align.MIN, bd.Align.CENTER)).translate((0.0, p.usbc_j1_front_y - 0.05, p.z_usbc))
    j1_usbc = j1_usbc_outer - j1_cavity
    j23_pins = bd.Box(15.0, 2.0, p.pcb_jst_pin_protrude, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)).translate((0.0, 19.2, p.z_pcb_bot))
    j4_pins = bd.Box(7.5, 2.0, p.pcb_jst_pin_protrude, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)).translate((-1.4, -2.5, p.z_pcb_bot))
    j1_pins = bd.Box(9.6, 5.7, p.pcb_jst_pin_protrude, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)).translate((0.0, -19.54, p.z_pcb_bot))
    pcb_assy = bd.Compound([pcb_board, l1_smd, l2_smd, j2_hdr, j3_hdr, j4_hdr, j1_usbc, j23_pins, j4_pins, j1_pins])

    # Central protruding bare aluminum core (40 x 40 x 3 mm, L = 250.0 mm stock cut!)
    core_out = bd.Box(core_w, core_w, p.core_length, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    core_in = bd.Box(core_w - 2.0 * p.core_wall, core_w - 2.0 * p.core_wall, p.core_length + 2.0,
                     align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, -1.0))
    hs_core = (core_out - core_in).translate((0, 0, p.z_core_bot))
    # Drilled Ø8.0 mm top hanging hole at Z = 302.0 mm (along X axis)
    hang_bore = bd.Cylinder(p.core_hang_hole_dia / 2.0, core_w + 2.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER)).rotate(bd.Axis.Y, 90.0).translate((0.0, 0.0, p.z_hang_hole))
    hs_core = hs_core - hang_bore
    # Bottom plug_bot M3 CSK side pin bores (Y = ±9.0, Z = 76.0 mm) + top cap_top M3 lock tapped bores (Y = 0, Z = 228.5 mm)
    for sy in (-p.plug_bot_pin_y, p.plug_bot_pin_y):
        b_pin = bd.Cylinder(1.70, core_w + 2.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER)).rotate(bd.Axis.Y, 90.0).translate((0.0, sy, p.z_core_bot + 6.0))
        hs_core = hs_core - b_pin
    z_top_lock = p.z_cap_top_top - p.cap_top_lock_z_from_top
    t_lock = bd.Cylinder(1.55, core_w + 2.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER)).rotate(bd.Axis.Y, 90.0).translate((0.0, 0.0, z_top_lock))
    hs_core = hs_core - t_lock

    # ALL Modeled M3 Fasteners & Captive M3 Nuts (single fastener size across entire lamp!)
    fasteners_list = []
    # 1. 4x M3x8 flush CSK bottom plug pins + 2x M3x16 CSK upward bulkhead bolts + 2x captive M3 nuts in plug_bot
    for sy in (-p.plug_bot_pin_y, p.plug_bot_pin_y):
        for sx in (-1.0, 1.0):
            x_face = sx * (core_w / 2.0 - 0.1)
            shank = bd.Cylinder(1.42, 7.5, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX if sx > 0 else bd.Align.MIN)).rotate(bd.Axis.Y, 90.0).translate((x_face, sy, p.z_core_bot + 6.0))
            fasteners_list.append(shank)
    z_csk_seat = p.z_cap_bot_bulkhead_start - 4.5
    for sx in (-1.0, 1.0):
        bx = sx * p.plug_bot_bolt_x
        b_shank = bd.Cylinder(1.45, 16.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((bx, 0.0, z_csk_seat + 0.1))
        b_head = bd.Cone(3.0, 1.45, 1.5, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((bx, 0.0, z_csk_seat + 0.1))
        fasteners_list.append(b_shank.fuse(b_head))
    # 2. 4x M3x10 DIN 7991 CSK lid bolts (R=40.2) + 4x captive M3 hex nuts in cap_bot slots (Z=9.1..11.5)
    for deg in (45.0, 135.0, 225.0, 315.0):
        rad = math.radians(deg)
        lx, ly = p.lid_bot_bolt_r * math.cos(rad), p.lid_bot_bolt_r * math.sin(rad)
        lb_head = bd.Cone(3.0, 1.48, 1.45, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((lx, ly, 0.05))
        lb_shank = bd.Cylinder(1.48, 11.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((lx, ly, 0.05))
        fasteners_list.append(lb_head.fuse(lb_shank))
    # 3. 2x M3x12 SHCS top cap locking screws on ±X at Z = 228.5 mm (head in counterbore X=27.2..30.2, shank into core wall)
    for sx in (-1.0, 1.0):
        if sx > 0:
            th = bd.Cylinder(2.75, 3.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).rotate(bd.Axis.Y, 90.0).translate((27.2, 0.0, z_top_lock))
            ts = bd.Cylinder(1.48, 10.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)).rotate(bd.Axis.Y, 90.0).translate((27.2, 0.0, z_top_lock))
        else:
            th = bd.Cylinder(2.75, 3.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)).rotate(bd.Axis.Y, 90.0).translate((-27.2, 0.0, z_top_lock))
            ts = bd.Cylinder(1.48, 10.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).rotate(bd.Axis.Y, 90.0).translate((-27.2, 0.0, z_top_lock))
        fasteners_list.append(th.fuse(ts))
    fasteners_m3 = bd.Compound(fasteners_list)

    # Borosilicate glass tube (MECH-TUBE-1)
    z_g_start = p.z_glass_bot - 0.5 * (g_len - p.glass_length)
    g_outer = bd.Cylinder(g_od / 2.0, g_len, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    g_inner = bd.Cylinder(g_id / 2.0, g_len + 2.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, -1.0))
    glass_tube = (g_outer - g_inner).translate((0, 0, z_g_start))

    # 8x Pre-mounted 20 mm Copper DTP LED stars (4x UV + 4x Vis) + 16x M3 screws w/ nylon washers
    star_items = []
    for angle in (0.0, 90.0, 180.0, 270.0):
        x0 = core_w / 2.0 + p.star_tim_thick
        for z_star, led_h in ((p.z_led_uv, p.led_uv_max_h), (p.z_led_vis, p.led_vis_max_h)):
            star_disc = bd.Cylinder(p.star_dia / 2.0, p.star_thick, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).rotate(bd.Axis.Y, 90.0).translate((x0, 0.0, z_star))
            led_pkg = bd.Box(led_h, 3.45, 3.45, align=(bd.Align.MIN, bd.Align.CENTER, bd.Align.CENTER)).translate((x0 + p.star_thick, 0.0, z_star))
            s_top = bd.Cylinder(3.5, p.m3_pan_plus_washer_h, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).rotate(bd.Axis.Y, 90.0).translate((x0 + p.star_thick, 0.0, z_star + p.star_bolt_r))
            s_bot = bd.Cylinder(3.5, p.m3_pan_plus_washer_h, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).rotate(bd.Axis.Y, 90.0).translate((x0 + p.star_thick, 0.0, z_star - p.star_bolt_r))
            star_items.append(bd.Compound([star_disc, led_pkg, s_top, s_bot]).rotate(bd.Axis.Z, angle))
    dtp_stars = bd.Compound(star_items)

    # SW1 (C&K 7211SYZBE gold DPDT) + C&K 759D02000 silicone boot (+X side)
    x_sw_in = p.sw1_spotface_x - p.sw1_wall_thick
    sw_body = bd.Box(p.sw1_body_depth, p.sw1_body_w_y, p.sw1_body_h_z, align=(bd.Align.MAX, bd.Align.CENTER, bd.Align.CENTER)).translate((x_sw_in, 0, p.sw1_z))
    sw_lugs = bd.Box(p.sw1_lugs_depth, 10.0, 8.5, align=(bd.Align.MAX, bd.Align.CENTER, bd.Align.CENTER)).translate((x_sw_in - p.sw1_body_depth, 0, p.sw1_z))
    sw_boot = bd.Cylinder(6.65, 16.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).rotate(bd.Axis.Y, 90.0).translate((p.sw1_spotface_x, 0, p.sw1_z))
    sw1_assy = bd.Compound([sw_body, sw_lugs, sw_boot])

    # Off-the-shelf 20 mm rubber membrane grommet
    y_sf = p.grommet_outer_spotface_y
    y_panel_in = y_sf + p.grommet_panel_thick
    g_outer_lip = bd.Cylinder(12.2, 2.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).rotate(bd.Axis.X, 90.0).translate((0.0, y_sf - 0.05, p.z_usbc))
    g_neck = bd.Cylinder(9.95, p.grommet_panel_thick + 0.1, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).rotate(bd.Axis.X, 90.0).translate((0.0, y_panel_in + 0.05, p.z_usbc))
    g_inner_lip = bd.Cylinder(11.5, 2.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).rotate(bd.Axis.X, 90.0).translate((0.0, y_panel_in + 2.05, p.z_usbc))
    g_cable_cut = bd.Box(12.8, 12.0, 7.2, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER)).translate((0.0, y_sf + 1.0, p.z_usbc))
    grommet_usbc = g_outer_lip.fuse(g_neck).fuse(g_inner_lip) - g_cable_cut

    # Standard 6.65 mm USB-C PD plug seated full 4.55 mm inside J1
    y_plug_tip = p.usbc_j1_front_y + p.usbc_mating_depth_mm
    y_overmold_front = y_plug_tip - p.usbc_specified_barrel_mm
    usbc_plug_shell = bd.Box(8.3, p.usbc_specified_barrel_mm + 0.01, 2.5, align=(bd.Align.CENTER, bd.Align.MAX, bd.Align.CENTER)).translate((0.0, y_plug_tip, p.z_usbc))
    usbc_plug_overmold = bd.Box(12.4, 26.0, 6.8, align=(bd.Align.CENTER, bd.Align.MAX, bd.Align.CENTER)).translate((0.0, y_overmold_front, p.z_usbc))
    usbc_plug_assy = usbc_plug_shell.fuse(usbc_plug_overmold)
    assert len(usbc_plug_assy.solids()) == 1

    return dict(
        lid_bot=lid_bot,
        cap_bot=cap_bot,
        cap_top=cap_top,
        plug_top=plug_top,
        plug_bot=plug_bot,
        pcb_assy=pcb_assy,
        hs_core=hs_core,
        fasteners_m3=fasteners_m3,
        glass_tube=glass_tube,
        dtp_stars=dtp_stars,
        sw1_assy=sw1_assy,
        grommet_usbc=grommet_usbc,
        usbc_plug_assy=usbc_plug_assy,
    )


def check_all_pairs_intersections(parts: dict[str, bd.Shape]) -> dict[str, dict]:
    names = list(parts.keys())
    results: dict[str, dict] = {}
    nonzero_pairs: dict[str, float] = {}
    total_pairs = 0
    for i in range(len(names)):
        na, sa = names[i], parts[names[i]]
        ba = sa.bounding_box()
        for j in range(i + 1, len(names)):
            nb, sb = names[j], parts[names[j]]
            bb = sb.bounding_box()
            total_pairs += 1
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
    mesh = trimesh.load(str(stl_path), force="mesh")
    up = np.array(print_up_axis, dtype=float)
    up = up / np.linalg.norm(up)
    z_proj = mesh.vertices @ up
    z_bed = float(np.min(z_proj))
    face_z_min = np.min(z_proj[mesh.faces], axis=1)
    off_bed = face_z_min > (z_bed + 0.05)

    dots = mesh.face_normals @ up
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
    mesh = trimesh.load(str(stl_path), force="mesh")
    tris = mesh.triangles
    z_lo = p.z_usbc - p.usbc_overmold_h / 2.0
    z_hi = p.z_usbc + p.usbc_overmold_h / 2.0 + 0.5 * p.usbc_overmold_w * math.tan(math.radians(47.0))
    tri_mask = (
        (tris[:, :, 0].max(axis=1) >= -15.0)
        & (tris[:, :, 0].min(axis=1) <= 15.0)
        & (tris[:, :, 1].min(axis=1) < 0.0)
        & (tris[:, :, 2].max(axis=1) >= p.bot_oring_roof_z_max)
    )
    tris_sub = tris[tri_mask]
    v0 = tris_sub[:, 0, :]
    e1 = tris_sub[:, 1, :] - v0
    e2 = tris_sub[:, 2, :] - v0
    det = e1[:, 0] * e2[:, 2] - e1[:, 2] * e2[:, 0]
    valid = np.abs(det) > 1e-12
    v0, e1, e2, inv_det = v0[valid], e1[valid], e2[valid], 1.0 / det[valid]

    hw = p.usbc_overmold_w / 2.0
    xs = np.arange(-14.0, 14.0 + 1e-9, 0.5)
    zs = np.arange(p.bot_oring_roof_z_max + 2.0, z_hi + 6.0, 0.5)
    gx, gz = np.meshgrid(xs, zs, indexing="ij")
    gx_flat, gz_flat = gx.ravel(), gz.ravel()

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
    in_tunnel = (np.abs(gx_flat) < hw - 0.1) & (gz_flat > z_lo + 0.1) & (gz_flat < tunnel_roof_z - 0.1)
    r_bore = p.grommet_bore_dia / 2.0
    dist_c = np.hypot(gx_flat, gz_flat - p.z_usbc)
    outside_grommet_bore = (dist_c > r_bore + 0.8) & (gz_flat < p.z_usbc + r_bore)

    min_wall_mm = float("inf")
    min_loc = None
    anomalies = 0
    slot_rays = 0
    wall_rays = 0

    for idx in range(len(gx_flat)):
        ys = np.sort(y_hits_all[idx, hits_mask[idx]])
        dedup: list[float] = []
        for yv in ys:
            if not dedup or abs(float(yv) - dedup[-1]) > 1e-4:
                dedup.append(float(yv))
        front_ys = [yv for yv in dedup if yv < 0.0]
        if in_tunnel[idx]:
            slot_rays += 1
            if len(front_ys) != 0:
                anomalies += 1
        elif outside_grommet_bore[idx]:
            wall_rays += 1
            if len(front_ys) < 2:
                anomalies += 1
                continue
            wt = front_ys[1] - front_ys[0]
            if wt < min_wall_mm:
                min_wall_mm = wt
                min_loc = (round(float(gx_flat[idx]), 2), round(float(gz_flat[idx]), 2))

    return {
        "stl_file": stl_path.name,
        "grid_rays_total": int(len(gx_flat)),
        "wall_rays_checked": wall_rays,
        "slot_rays_checked": slot_rays,
        "anomalies": anomalies,
        "min_flange_wall_mm": round(min_wall_mm, 4) if min_wall_mm < float("inf") else 0.0,
        "min_wall_xz_mm": min_loc,
        "min_required_mm": p.min_wall,
        "pass": anomalies == 0 and min_wall_mm >= p.min_wall - 0.02,
    }


def export_and_verify_stl(shape: bd.Shape, step_path: Path, stl_path: Path) -> dict:
    bd.export_step(shape, str(step_path))
    bd.export_stl(shape, str(stl_path), tolerance=0.01, angular_tolerance=0.03)
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
    x_sw_in = p.sw1_spotface_x - p.sw1_wall_thick
    sw_body = bd.Box(p.sw1_body_depth, p.sw1_body_w_y, p.sw1_body_h_z, align=(bd.Align.MAX, bd.Align.CENTER, bd.Align.CENTER))
    sw_lugs = bd.Box(p.sw1_lugs_depth, 10.0, 8.5, align=(bd.Align.MAX, bd.Align.CENTER, bd.Align.CENTER)).translate((-p.sw1_body_depth, 0.0, 0.0))
    sw_bush = bd.Cylinder(p.sw1_hole_dia / 2.0, 8.89, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).rotate(bd.Axis.Y, 90.0)
    sw_tool = bd.Compound([sw_body, sw_lugs, sw_bush])

    sw_waypoints = [(20.0, float(z)) for z in np.linspace(p.z_lid_bot_end, p.sw1_z, 12)] + [
        (float(x), p.sw1_z) for x in np.linspace(20.0, x_sw_in, 15)
    ]
    sw_max_vol = 0.0
    for xw, zw in sw_waypoints:
        inter = cap_bot & sw_tool.translate((xw, 0.0, zw))
        sw_max_vol = max(sw_max_vol, float(inter.volume) if inter is not None else 0.0)

    # M3x16 CSK bulkhead bolts straight +Z insertion
    z_csk_seat = p.z_cap_bot_bulkhead_start - 4.5
    bolt_tool = bd.Cylinder(1.45, 16.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).fuse(
        bd.Cone(3.0, 1.45, 1.5, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    )
    bolt_max_vol = 0.0
    for sx in (-1.0, 1.0):
        for zb in np.linspace(p.z_lid_bot_end, z_csk_seat + 0.1, 15):
            inter = cap_bot & bolt_tool.translate((sx * p.plug_bot_bolt_x, 0.0, float(zb)))
            bolt_max_vol = max(bolt_max_vol, float(inter.volume) if inter is not None else 0.0)

    # Standard USB-C plug straight +Y insertion
    y_plug_tip = p.usbc_j1_front_y + p.usbc_mating_depth_mm
    y_overmold_front = y_plug_tip - p.usbc_specified_barrel_mm
    plug_tool = bd.Box(8.3, p.usbc_specified_barrel_mm + 0.01, 2.5, align=(bd.Align.CENTER, bd.Align.MAX, bd.Align.CENTER)).fuse(
        bd.Box(12.4, 26.0, 6.8, align=(bd.Align.CENTER, bd.Align.MAX, bd.Align.CENTER)).translate((0.0, -p.usbc_specified_barrel_mm, 0.0))
    )
    usbc_max_vol = 0.0
    for yt in np.linspace(-55.0, y_plug_tip, 15):
        inter = cap_bot & plug_tool.translate((0.0, float(yt), p.z_usbc))
        usbc_max_vol = max(usbc_max_vol, float(inter.volume) if inter is not None else 0.0)

    return {
        "sw1_dpdt_insertion": {"waypoints_tested": len(sw_waypoints), "max_intersection_vol_mm3": round(sw_max_vol, 6), "pass": sw_max_vol < 1e-4},
        "m3x16_bolt_insertion": {"waypoints_tested": 30, "max_intersection_vol_mm3": round(bolt_max_vol, 6), "pass": bolt_max_vol < 1e-4},
        "usbc_plug_insertion": {"waypoints_tested": 15, "max_intersection_vol_mm3": round(usbc_max_vol, 6), "pass": usbc_max_vol < 1e-4},
        "all_zero": (sw_max_vol < 1e-4) and (bolt_max_vol < 1e-4) and (usbc_max_vol < 1e-4),
    }


def main() -> None:
    out_dir = Path(__file__).resolve().parent
    p_fdm = LepiLEDParams(process="FDM")
    (out_dir / "cad_params.json").write_text(json.dumps(p_fdm.to_dict(), indent=2))

    # Remove legacy SLS STEP/STL files if present (Rev 4.2 targets DIY FDM PETG/ASA)
    for legacy in ("mech_cap_bot_sls.step", "mech_cap_bot_sls.stl", "mech_cap_top_sls.step", "mech_cap_top_sls.stl"):
        lp = out_dir / legacy
        if lp.exists():
            lp.unlink()

    assy_nom = build_assembly_parts(p_fdm)
    drill_jig = build_drill_jig(p_fdm)

    # 1. Export all 6 3D-printable FDM STEP & STL files
    mesh_checks = {
        "mech_lid_bot": export_and_verify_stl(assy_nom["lid_bot"], out_dir / "mech_lid_bot.step", out_dir / "mech_lid_bot.stl"),
        "mech_cap_bot": export_and_verify_stl(assy_nom["cap_bot"], out_dir / "mech_cap_bot.step", out_dir / "mech_cap_bot.stl"),
        "mech_cap_top": export_and_verify_stl(assy_nom["cap_top"], out_dir / "mech_cap_top.step", out_dir / "mech_cap_top.stl"),
        "mech_plug_top": export_and_verify_stl(assy_nom["plug_top"], out_dir / "mech_plug_top.step", out_dir / "mech_plug_top.stl"),
        "mech_plug_bot": export_and_verify_stl(assy_nom["plug_bot"], out_dir / "mech_plug_bot.step", out_dir / "mech_plug_bot.stl"),
        "mech_drill_jig": export_and_verify_stl(drill_jig, out_dir / "mech_drill_jig.step", out_dir / "mech_drill_jig.stl"),
    }

    # 2. Export individual assembly STLs to gitignored parts_stl/ for PyVista rendering
    comp_dir = out_dir / "parts_stl"
    comp_dir.mkdir(exist_ok=True)
    for old_f in comp_dir.glob("*.stl"):
        old_f.unlink()
    for name, shp in assy_nom.items():
        if name in ("lid_bot", "cap_bot", "cap_top", "plug_top", "plug_bot"):
            (comp_dir / f"{name}.stl").write_bytes((out_dir / f"mech_{name}.stl").read_bytes())
        else:
            bd.export_stl(shp, str(comp_dir / f"{name}.stl"), tolerance=0.03, angular_tolerance=0.12)

    assy_compound = bd.Compound(list(assy_nom.values()))
    bd.export_step(assy_compound, str(out_dir / "lepiled_assembly.step"))

    # 3. Overhang audits (all 6 printed parts in actual build-plate orientations!)
    overhang_checks = {
        "mech_lid_bot": audit_stl_overhangs(out_dir / "mech_lid_bot.stl", (0.0, 0.0, 1.0)),
        "mech_cap_bot": audit_stl_overhangs(out_dir / "mech_cap_bot.stl", (0.0, 0.0, 1.0)),
        "mech_cap_top": audit_stl_overhangs(out_dir / "mech_cap_top.stl", (0.0, 0.0, -1.0)),
        "mech_plug_top": audit_stl_overhangs(out_dir / "mech_plug_top.stl", (0.0, 0.0, -1.0)),
        "mech_plug_bot": audit_stl_overhangs(out_dir / "mech_plug_bot.stl", (0.0, 0.0, 1.0)),
        "mech_drill_jig": audit_stl_overhangs(out_dir / "mech_drill_jig.stl", (0.0, 0.0, 1.0)),
    }

    # 4. USB-C & 20 mm grommet flange STL ray-cast
    usbc_bezel_raycast = verify_usbc_bezel_wall_stl(out_dir / "mech_cap_bot.stl", p_fdm)

    # 5. All-pairs B-Rep intersection verification (Nominal + Worst-Case 151 mm glass)
    wc_glass_len = p_fdm.glass_length + p_fdm.glass_length_tol
    inter_nom = check_all_pairs_intersections(assy_nom)
    assy_wc = build_assembly_parts(
        p_fdm, core_w_override=p_fdm.core_w_max, glass_id_override=p_fdm.glass_id_min,
        glass_od_override=p_fdm.glass_od_max, glass_length_override=wc_glass_len,
    )
    inter_wc = check_all_pairs_intersections(assy_wc)

    # 6. Kinematic insertion sweeps
    alcove_checks = check_alcove_insertion(assy_nom["cap_bot"], p_fdm)

    all_meshes_ok = all(m["is_watertight"] and m["is_winding_consistent"] and m["stl_volume_mm3"] > 0 for m in mesh_checks.values())
    all_overhangs_ok = all(o["pass"] for o in overhang_checks.values())
    all_brep_ok = inter_nom["all_zero"] and inter_wc["all_zero"]
    usbc_bezel_wall_ok = usbc_bezel_raycast["pass"]
    all_alcove_ok = alcove_checks["all_zero"]
    all_param_checks_ok = all(c["pass"] for c in p_fdm.verify_all().values())

    report = {
        "revision": "Rev 4.2 (Lean 1-Off Hobby Build: 20mm Copper DTP Stars + 85.5mm Protruding Bare Core + Printed Rain Plug + Captive M3 Nuts + Zero Inserts)",
        "params": p_fdm.to_dict(),
        "mesh_checks": mesh_checks,
        "overhang_checks": overhang_checks,
        "usbc_grommet_flange_raycast": usbc_bezel_raycast,
        "alcove_insertion_checks": alcove_checks,
        "brep_all_pairs_nominal": {k: v for k, v in inter_nom.items() if k != "pairs"},
        "brep_all_pairs_worst_case": {k: v for k, v in inter_wc.items() if k != "pairs"},
        "summary": {
            "all_param_checks_pass": all_param_checks_ok,
            "all_meshes_watertight_manifold": all_meshes_ok,
            "all_overhangs_le_46deg": all_overhangs_ok,
            "usbc_grommet_flange_raycast_ge_2_5mm": usbc_bezel_wall_ok,
            "alcove_kinematic_insertion_zero": all_alcove_ok,
            "nominal_all_pairs_zero": inter_nom["all_zero"],
            "worst_case_all_pairs_zero": inter_wc["all_zero"],
            "overall_pass": (
                all_param_checks_ok and all_meshes_ok and all_overhangs_ok
                and usbc_bezel_wall_ok and all_brep_ok and all_alcove_ok
            ),
        },
    }
    verif_path = out_dir / "cad_verification.json"
    verif_path.write_text(json.dumps(report, indent=2))

    print("=== Mesh Verification (6 FDM Printable Parts) ===")
    for name, m in mesh_checks.items():
        print(f"  {name:16s}: vol={m['stl_volume_mm3']:8.1f} mm^3 | tri={m['triangles']:6d} | wt={m['is_watertight']} | wind={m['is_winding_consistent']} | euler={m['euler_number']:3d}")
    print("=== Overhang Verification ===")
    for name, o in overhang_checks.items():
        print(f"  {name:16s}: >46deg faces={o['off_bed_overhang_gt46_faces']:4d}, area={o['off_bed_overhang_gt46_area_mm2']:6.3f} mm^2, max={o['max_off_bed_overhang_deg']:5.2f} deg | pass={o['pass']}")
    print("=== USB-C & 20 mm Grommet Flange STL Ray-Cast ===")
    print(f"  {usbc_bezel_raycast['stl_file']}: rays={usbc_bezel_raycast['grid_rays_total']}, anomalies={usbc_bezel_raycast['anomalies']}, min_wall={usbc_bezel_raycast['min_flange_wall_mm']:.4f} mm | pass={usbc_bezel_raycast['pass']}")
    print("=== Kinematic Alcove, Bolt & USB-C Insertion ===")
    for k in ("sw1_dpdt_insertion", "m3x16_bolt_insertion", "usbc_plug_insertion"):
        v = alcove_checks[k]
        print(f"  {k:22s}: waypoints={v['waypoints_tested']:2d}, max_vol={v['max_intersection_vol_mm3']:.6f} mm^3 | pass={v['pass']}")
    print("=== All-Pairs B-Rep Intersection (incl. 8x 20mm Cu DTP Stars + ALL M3 Fasteners + 151mm Glass WC) ===")
    for label, d in [("NOMINAL", inter_nom), ("WORST_CASE", inter_wc)]:
        print(f"  {label:10s}: {d['total_pairs_checked']} pairs, nonzero={d['nonzero_count']} {d['nonzero_pairs']}")

    if not report["summary"]["overall_pass"]:
        raise SystemExit(1)
    print(f"Wrote {verif_path} and all Rev 4.2 STEP/STL artifacts (ALL CHECKS PASS).")


if __name__ == "__main__":
    main()
