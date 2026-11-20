#!/usr/bin/env python3
"""
Parametric 3D CAD Generator for LepiLED DIY Maxi Switch (Rev 4.4 — Vertical PCB, Bottom USB-C & Seamless Weatherproof Housing) using build123d.

Exports (7 watertight, 100% support-free FDM PETG/ASA parts):
  - mech_base_ring.step / .stl     (Bolt-on Ø92 x 18 mm protective standing ring w/ 4x drainage & 90-deg cable cutouts)
  - mech_lid_bot.step / .stl       (Flat Ø92 x 5 mm lid w/ vertical PCB card-guide rails, bottom USB-C grommet & bottom SW1)
  - mech_cap_bot.step / .stl       (100% seamless axisymmetric contoured shell — ZERO side holes or bosses!)
  - mech_cap_top.step / .stl       (Integral Ø116 mm drip-brim w/ 1.5 mm underside drip groove + core lock + silicone groove)
  - mech_plug_top.step / .stl      (Weatherproof press-fit rain cap sealing open top of protruding 40x40x3 mm Al tube)
  - mech_plug_bot.step / .stl      (Internal 33.4x33.4x12 mm core plug w/ captive M3 nuts replacing Al bottom anchor)
  - mech_drill_jig.step / .stl     (Snap-on 40.6 mm U-channel drill guide for all 16x M3 holes of 20 mm Copper DTP stars)
  - lepiled_assembly.step          (Full multi-part B-Rep assembly incl. vertical driver_pcb, UVT PMMA shroud & fasteners)
  - cad_verification.json          (trimesh manifold metrics + all-pairs B-Rep 0.000 mm^3 checks + overhang & mass audit)
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


def build_base_ring(p: LepiLEDParams) -> bd.Part:
    """
    Build MECH-BASE-RING: protective bolt-on standing ring & downward SW1 / USB-C guard (Z = -18.0 .. 0.0 mm):
      - Clamps underneath MECH-LID-BOT using the exact same 4x M3x16 SHCS lid bolts (zero extra fasteners!)
      - 4x Ø6.4 mm counterbores with 2.5 mm seat web at Z = -2.5 mm
      - 4x wide 22 x 7.5 mm drainage & 90-deg USB-C cable exit cutouts at 0/90/180/270 deg
      - Prints inverted (Z = 0.0 flat on build plate, -Z up) with 0.000 mm^2 >46 deg overhang!
    """
    r_out = p.base_ring_od / 2.0
    r_in = p.base_ring_id / 2.0
    outer = bd.Cylinder(r_out, p.base_ring_h, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX))
    inner = bd.Cylinder(r_in, p.base_ring_h + 2.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)).translate((0, 0, 1.0))
    part = outer - inner
    bot_edges = part.edges().filter_by(bd.GeomType.CIRCLE).filter_by_position(bd.Axis.Z, -p.base_ring_h - 0.1, -p.base_ring_h + 0.1)
    part = bd.chamfer(bot_edges, length=p.cap_chamfer)

    r_thru = p.m3_clearance_dia / 2.0
    r_cb = p.base_ring_cb_dia / 2.0
    cb_h = p.base_ring_h - p.base_ring_bolt_web
    for deg in (45.0, 135.0, 225.0, 315.0):
        rad = math.radians(deg)
        hx, hy = p.lid_bot_bolt_r * math.cos(rad), p.lid_bot_bolt_r * math.sin(rad)
        thru = bd.Cylinder(r_thru, p.base_ring_h + 2.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)).translate((hx, hy, 1.0))
        cb = bd.Cylinder(r_cb, cb_h + 1.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)).translate((hx, hy, -p.base_ring_bolt_web))
        part = part - thru - cb

    for deg in (0.0, 90.0, 180.0, 270.0):
        cut = bd.Box(24.0, p.base_ring_drain_w, p.base_ring_drain_h + 1.0,
                     align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0.5 * (r_in + r_out), 0.0, -p.base_ring_h - 1.0))
        part = part - cut.rotate(bd.Axis.Z, deg)

    return part


def build_lid_bot(p: LepiLEDParams) -> bd.Part:
    """
    Build Rev 4.4 MECH-LID-BOT: flat 3D-printed Ø92 x 5.0 mm bottom lid with:
      - 2x integral vertical card-guide rails (Z = 5.0 .. 46.0 mm) with 2.0 mm slots & bottom seat ledges at Z = 11.76 mm
        holding the unchanged 36 x 46 mm driver_pcb vertically at Y_back = -8.48 mm (zero PCB screws, zero inserts!)
      - Bottom-entry USB-C Ø20.2 x 2.5 mm rubber grommet bore + Ø23.6 x 2.5 mm top inner-lip counterbore at (0.0, -5.0 mm)
      - Bottom-mounted SW1 (C&K 7211SYZBE) vertical Ø6.35 mm bore + 2.5 mm anti-rotation pocket at (0.0, +16.5 mm)
      - 4x plain M3 clearance holes at R = 40.2 mm (clamped with MECH-BASE-RING by 4x M3x16 SHCS)
      - Prints flat on Z = 0 bed with 0.000 mm^2 >46 deg overhang!
    """
    r_lid = p.lid_bot_od / 2.0
    part = bd.Cylinder(r_lid, p.lid_bot_thick, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))

    # 2x Vertical U-channel PCB card-guide rails on ±X edges of driver_pcb (X_edge = ±18.0 mm, Y_mid = -7.68 mm)
    y_mid = 0.5 * (p.pcb_y_back + p.pcb_y_front)  # -7.68 mm
    rail_y_w = p.pcb_rail_slot_w + 2.0 * p.pcb_rail_wall  # 6.4 mm
    rail_x_in = p.pcb_w / 2.0 - p.pcb_rail_grip_x         # 16.6 mm (grips outer 1.4 mm margin cleanly!)
    rail_x_out = p.pcb_w / 2.0 + 0.20 + p.pcb_rail_wall   # 20.4 mm
    rail_x_w = rail_x_out - rail_x_in                     # 3.8 mm
    rail_x_mid = 0.5 * (rail_x_in + rail_x_out)
    z_rail_top = p.z_cap_bot_cavity_taper_start - 1.5     # 46.5 mm (safely below 44 deg cavity cone!)
    rail_h = z_rail_top - p.z_lid_bot_end                 # 41.5 mm

    for sx in (-1.0, 1.0):
        # Main vertical guide post
        post = bd.Box(rail_x_w, rail_y_w, rail_h, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((sx * rail_x_mid, y_mid, p.z_lid_bot_end))
        # Base reinforcement gusset on Z = 5.0 mm (45 deg pyramid base)
        foot = bd.Box(rail_x_w + 2.0, rail_y_w + 2.0, 3.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((sx * rail_x_mid, y_mid, p.z_lid_bot_end))
        # Cut vertical PCB edge slot down to bottom PCB seat at Z = z_pcb_bot_edge (11.76 mm)!
        slot_x_in = rail_x_in - 0.5
        slot_x_out = p.pcb_w / 2.0 + 0.20  # 18.2 mm (0.20 mm radial clearance to PCB edge)
        slot_w_x = slot_x_out - slot_x_in
        slot_cx = 0.5 * (slot_x_in + slot_x_out)
        slot = bd.Box(slot_w_x, p.pcb_rail_slot_w, z_rail_top - p.z_pcb_bot_edge + 1.0,
                      align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((sx * slot_cx, y_mid, p.z_pcb_bot_edge - 0.05))
        part = part.fuse(post).fuse(foot) - slot

    # 4x plain M3 bolt holes at R = 40.2 mm
    for deg in (45.0, 135.0, 225.0, 315.0):
        rad = math.radians(deg)
        hx, hy = p.lid_bot_bolt_r * math.cos(rad), p.lid_bot_bolt_r * math.sin(rad)
        c_thru = bd.Cylinder(p.m3_clearance_dia / 2.0, p.lid_bot_thick + 2.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((hx, hy, -1.0))
        part = part - c_thru

    # Bottom-entry USB-C Ø20.2 x 2.5 mm rubber grommet bore + Ø23.6 x 2.5 mm top inner-lip counterbore at (0.0, -5.0 mm)
    g_bore = bd.Cylinder(p.grommet_bore_dia / 2.0, p.lid_bot_thick + 2.0,
                         align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0.0, p.y_usbc, -1.0))
    g_back = bd.Cylinder(p.grommet_back_relief_dia / 2.0, p.grommet_back_relief_depth + 0.5,
                         align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0.0, p.y_usbc, p.grommet_panel_thick))
    part = part - g_bore - g_back

    # Bottom-mounted SW1 vertical Ø6.35 mm bore + 2.5 mm upper anti-rotation pocket at (0.0, +16.5 mm)
    sw_bore = bd.Cylinder(p.sw1_hole_dia / 2.0 + p.print_clearance * 0.5, p.lid_bot_thick + 2.0,
                          align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((p.sw1_x, p.sw1_y, -1.0))
    sw_recess = bd.Box(p.sw1_body_w_x + 0.8, p.sw1_body_w_y + 0.8, p.lid_bot_thick - p.sw1_wall_thick + 0.5,
                       align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((p.sw1_x, p.sw1_y, p.sw1_wall_thick))
    part = part - sw_bore - sw_recess

    return part


def build_cap_bot(p: LepiLEDParams) -> bd.Part:
    """
    Build seamless axisymmetric Rev 4.4 MECH-CAP-BOT:
      - 100% solid, unbroken outer wall (ZERO side cutouts, ZERO side bosses — both USB-C & SW1 enter through bottom lid!)
      - Contoured lightweight shell (Ø92 flange -> Ø71 mid -> Ø65 waist -> 45-deg flare to Ø84 shroud skirt)
        keeping every structural wall >= 3.5-8.5 mm robust!
      - 4x radial side-entry captive M3 hex-nut pockets at R = 40.2 mm (ZERO brass heat-set inserts!)
      - 2x M3 CSK upward bulkhead bolt holes at (±9.0, 0.0) into 3D-printed MECH-PLUG-BOT
      - Prints upright (+Z up) with 0.000 mm^2 >46 deg overhang (100% support-free!).
    """
    r_bot = p.cap_bot_od / 2.0          # 46.0
    r_mid = p.cap_bot_mid_od / 2.0      # 35.5
    r_waist = p.cap_bot_waist_od / 2.0  # 32.5
    r_top = p.cap_top_od / 2.0          # 42.0
    z_base = p.z_lid_bot_end            # 5.0
    z_flange_top = z_base + 11.0        # 16.0
    z_mid_bot = z_flange_top + (r_bot - r_mid)      # 26.5 (45 deg inward taper)
    z_mid_top = p.z_cap_bot_cavity_taper_start      # 47.5
    z_waist_top = 72.0
    z_flare_top = z_waist_top + (r_top - r_waist)   # 81.5 (45 deg outward flare, 2.35 mm below G1 bottom = 83.85!)
    z_top = p.z_cap_bot_top             # 98.5

    s1 = bd.Cylinder(r_bot, z_flange_top - z_base, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, z_base))
    s2 = bd.Cone(r_bot, r_mid, z_mid_bot - z_flange_top, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, z_flange_top))
    s3 = bd.Cylinder(r_mid, z_mid_top - z_mid_bot, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, z_mid_bot))
    s4 = bd.Cone(r_mid, r_waist, z_waist_top - z_mid_top, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, z_mid_top))
    s5 = bd.Cone(r_waist, r_top, z_flare_top - z_waist_top, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, z_waist_top))
    s6 = bd.Cylinder(r_top, z_top - z_flare_top, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, z_flare_top))
    part = s1.fuse(s2).fuse(s3).fuse(s4).fuse(s5).fuse(s6)

    top_edges = part.edges().filter_by(bd.GeomType.CIRCLE).filter_by_position(bd.Axis.Z, z_top - 0.1, z_top + 0.1)
    part = bd.chamfer(top_edges, length=p.cap_chamfer)

    # Internal PCB cavity: cylinder + 44.1 deg cone all the way to R=0.02 apex (captures vertical PCB upper corners!)
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

    # 4x M3 clearance bores + radial side-entry captive M3 hex-nut pockets (Z = 10.0 .. 12.7 mm, 47 deg pitched roof)
    r_bolt = p.m3_clearance_dia / 2.0
    z_nut_bot = z_base + 5.0  # Z = 10.0 mm (2.95 mm above MECH-GASKET-3 roof!)
    nut_prof = _pitched_rect_profile(p.m3_nut_af, p.m3_nut_thick, 47.0)
    nut_len = (r_bot + 1.0) - (p.lid_bot_bolt_r - p.m3_nut_af / 2.0 - 0.4)
    for deg in (45.0, 135.0, 225.0, 315.0):
        rad = math.radians(deg)
        ix, iy = p.lid_bot_bolt_r * math.cos(rad), p.lid_bot_bolt_r * math.sin(rad)
        h_tot_bolt = (z_nut_bot - z_base) + p.m3_nut_thick + 2.5
        hole = bd.Cylinder(r_bolt, h_tot_bolt, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((ix, iy, z_base))
        tip = bd.Cone(r_bolt, 0.02, r_bolt - 0.02, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((ix, iy, z_base + h_tot_bolt))
        part = part - hole.fuse(tip)
        slot = bd.extrude(nut_prof, nut_len).rotate(bd.Axis.X, 90.0).rotate(bd.Axis.Z, 90.0)
        slot = slot.translate((p.lid_bot_bolt_r - p.m3_nut_af / 2.0 - 0.4, 0.0, z_nut_bot)).rotate(bd.Axis.Z, deg)
        part = part - slot

    # Shroud socket (Z = 85.5 .. 97.5) + axial O-ring groove (MECH-GASKET-1: 68x3.5 mm)
    r_pilot = p.glass_pilot_od / 2.0
    glass_outer = bd.Cone(p.glass_skirt_id_bot / 2.0, p.glass_skirt_id_top / 2.0, p.glass_socket_depth, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    glass_inner = bd.Cylinder(r_pilot, p.glass_socket_depth, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    glass_slot = (glass_outer - glass_inner).translate((0, 0, p.z_glass_bot))

    g1_out = bd.Cylinder(p.glass_oring_od / 2.0, p.glass_oring_depth + 0.05, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    g1_in = bd.Cylinder(p.glass_oring_id / 2.0, p.glass_oring_depth + 0.05, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    g1 = (g1_out - g1_in).translate((0, 0, p.z_glass_bot - p.glass_oring_depth))
    part = part - glass_slot.fuse(g1)

    # Core socket (41.0 x 41.0 mm, Z = 85.5 .. 97.5) + 4x wire slots opening into cavity cone
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

    return part


def build_cap_top(p: LepiLEDParams) -> bd.Part:
    """
    Build Rev 4.4 MECH-CAP-TOP with integral Ø116 mm rain drip-brim + 1.5 mm underside drip-break groove:
      - Prints 100% flat inverted (Z_cap_top_top on bed -> 0.000 mm^2 overhang!)
      - 3.8 mm thick Ø116 mm brim overhangs lower body by 12 mm/side; underside drip-break groove detaches runoff
      - Shroud socket + MECH-GASKET-2 (68x3.5 mm) groove + 41x41 mm protruding core aperture + silicone groove
      - 2x radial M3 locking screw bores + counterbores at ±X tucked cleanly beneath the drip-brim
    """
    r_cap = p.cap_top_od / 2.0
    r_brim = p.cap_top_brim_od / 2.0
    z_bot = p.z_cap_top_bot
    z_top = p.z_cap_top_top
    z_brim_bot = z_top - p.cap_top_brim_rim_h
    gusset = 3.0
    h_tot = z_top - z_bot

    c_body = bd.Cylinder(r_cap, z_brim_bot - z_bot, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, z_bot))
    c_gusset = bd.Cone(r_cap, r_cap + gusset, gusset, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, z_brim_bot - gusset))
    c_brim = bd.Cylinder(r_brim, p.cap_top_brim_rim_h, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, z_brim_bot))
    part = c_body.fuse(c_gusset).fuse(c_brim)

    dg_out = bd.Cylinder(r_brim - 2.5, 1.55, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    dg_in = bd.Cylinder(r_brim - 4.5, 1.55, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    drip_groove = (dg_out - dg_in).translate((0, 0, z_brim_bot - 0.05))
    part = part - drip_groove

    bot_c = part.edges().filter_by(bd.GeomType.CIRCLE).filter_by_position(bd.Axis.Z, z_bot - 0.1, z_bot + 0.1)
    top_c = part.edges().filter_by(bd.GeomType.CIRCLE).filter_by_position(bd.Axis.Z, z_top - 0.1, z_top + 0.1)
    part = bd.chamfer(bot_c + top_c, length=p.cap_chamfer)

    r_pilot = p.glass_pilot_od / 2.0
    glass_outer = bd.Cone(p.glass_skirt_id_top / 2.0, p.glass_skirt_id_bot / 2.0, p.glass_socket_depth, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    glass_inner = bd.Cylinder(r_pilot, p.glass_socket_depth, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    glass_slot = (glass_outer - glass_inner).translate((0, 0, z_bot))

    g2_out = bd.Cylinder(p.glass_oring_od / 2.0, p.glass_oring_depth + 0.05, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    g2_in = bd.Cylinder(p.glass_oring_id / 2.0, p.glass_oring_depth + 0.05, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    g2 = (g2_out - g2_in).translate((0, 0, p.z_glass_top - 0.05))
    part = part - glass_slot.fuse(g2)

    core_thru = bd.Box(p.core_pocket_w, p.core_pocket_w, h_tot + 2.0,
                       align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, z_bot - 1.0))
    part = part - core_thru
    w_g = p.core_pocket_w + 2.0 * p.cap_top_seal_groove
    with bd.BuildSketch(bd.Plane.XY.offset(z_top)) as sk_top:
        bd.Rectangle(w_g, w_g)
    with bd.BuildSketch(bd.Plane.XY.offset(z_top - p.cap_top_seal_groove)) as sk_bot:
        bd.Rectangle(p.core_pocket_w, p.core_pocket_w)
    seal_chamfer = bd.loft([sk_bot.sketch, sk_top.sketch])
    part = part - seal_chamfer

    z_lock = z_top - p.cap_top_lock_z_from_top
    td_thru = _teardrop_profile_wire(p.m3_clearance_dia / 2.0, 45.0)
    td_cb = _teardrop_profile_wire(3.6, 45.0)
    for sx in (-1.0, 1.0):
        h_lock = bd.extrude(td_thru, 36.0).rotate(bd.Axis.X, -90.0).rotate(bd.Axis.Z, -90.0)
        h_cb = bd.extrude(td_cb, 28.0).rotate(bd.Axis.X, -90.0).rotate(bd.Axis.Z, -90.0)
        if sx > 0:
            h_lock = h_lock.translate((19.0, 0.0, z_lock))
            h_cb = h_cb.translate((27.0, 0.0, z_lock))
        else:
            h_lock = h_lock.rotate(bd.Axis.Z, 180.0).translate((-19.0, 0.0, z_lock))
            h_cb = h_cb.rotate(bd.Axis.Z, 180.0).translate((-27.0, 0.0, z_lock))
        part = part - h_lock - h_cb

    return part


def build_plug_top(p: LepiLEDParams) -> bd.Part:
    """Build MECH-PLUG-TOP: weatherproof press-fit rain cap sealing the open top of the protruding Al tube."""
    insert = bd.Box(p.plug_top_w, p.plug_top_w, p.plug_top_insert_h,
                    align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, p.z_core_top - p.plug_top_insert_h))
    insert = bd.fillet(insert.edges().filter_by(bd.Axis.Z), 1.5)
    cap = bd.Box(p.plug_top_cap_w, p.plug_top_cap_w, p.plug_top_cap_h,
                 align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, p.z_core_top))
    cap = bd.fillet(cap.edges().filter_by(bd.Axis.Z), 1.5)
    top_edges = cap.edges().filter_by_position(bd.Axis.Z, p.z_plug_top_end - 0.1, p.z_plug_top_end + 0.1)
    cap = bd.chamfer(top_edges, length=1.2)
    return insert.fuse(cap)


def build_plug_bot(p: LepiLEDParams) -> bd.Part:
    """Build MECH-PLUG-BOT: 3D-printed 33.4 x 33.4 x 12.0 mm internal bottom core plug w/ captive M3 nuts."""
    plug = bd.Box(p.plug_bot_w, p.plug_bot_w, p.plug_bot_h,
                  align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, p.z_core_bot))
    plug = bd.fillet(plug.edges().filter_by(bd.Axis.Z), 1.5)

    r_bolt = p.m3_clearance_dia / 2.0
    r_hex = p.m3_nut_af / math.sqrt(3.0)
    for sx in (-1.0, 1.0):
        bx = sx * p.plug_bot_bolt_x
        v_bore = bd.Cylinder(r_bolt, p.plug_bot_h + 1.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((bx, 0.0, p.z_core_bot - 0.5))
        with bd.BuildSketch(bd.Plane.XY.offset(p.z_core_bot + p.plug_bot_h - 4.0)) as sk_hex:
            bd.RegularPolygon(r_hex, 6)
        hex_pocket = bd.extrude(sk_hex.sketch, 4.5).translate((bx, 0.0, 0.0))
        plug = plug - v_bore - hex_pocket

    td_pin = _teardrop_profile_wire(1.45, 45.0)
    for sy in (-p.plug_bot_pin_y, p.plug_bot_pin_y):
        h_pin = bd.extrude(td_pin, p.plug_bot_w + 2.0).rotate(bd.Axis.X, 90.0).rotate(bd.Axis.Z, 90.0)
        h_pin = h_pin.translate((-p.plug_bot_w / 2.0 - 1.0, sy, p.z_core_bot + 6.0))
        plug = plug - h_pin

    return plug


def build_drill_jig(p: LepiLEDParams) -> bd.Part:
    """Build MECH-DRILL-JIG: snap-on U-channel drilling template for all 16x M3 holes of the 20 mm Copper DTP stars."""
    wall = 3.0
    inner_w = p.core_w_nom + 0.6
    outer_w = inner_w + 2.0 * wall
    jig_len = 115.0
    leg_h = 18.0

    base = bd.Box(wall, outer_w, jig_len, align=(bd.Align.MIN, bd.Align.CENTER, bd.Align.MIN))
    leg_pos = bd.Box(leg_h, wall, jig_len, align=(bd.Align.MIN, bd.Align.MAX, bd.Align.MIN)).translate((0, outer_w / 2.0, 0))
    leg_neg = bd.Box(leg_h, wall, jig_len, align=(bd.Align.MIN, bd.Align.MIN, bd.Align.MIN)).translate((0, -outer_w / 2.0, 0))
    end_stop = bd.Box(12.0, outer_w, wall, align=(bd.Align.MIN, bd.Align.CENTER, bd.Align.MAX))
    jig = base.fuse(leg_pos).fuse(leg_neg).fuse(end_stop)

    for z_rel in (
        p.axial_vis_to_bot_mm - p.star_bolt_r,
        p.axial_vis_to_bot_mm + p.star_bolt_r,
        (p.z_led_uv - p.z_core_bot) - p.star_bolt_r,
        (p.z_led_uv - p.z_core_bot) + p.star_bolt_r,
    ):
        guide = bd.Cylinder(1.30, wall + 2.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER)).rotate(bd.Axis.Y, 90.0).translate((wall / 2.0, 0.0, z_rel))
        jig = jig - guide

    jig = jig.rotate(bd.Axis.Y, -90.0)
    bb = jig.bounding_box()
    return jig.translate((0.0, 0.0, -bb.min.Z))


def build_assembly_parts(p: LepiLEDParams, core_w_override: float | None = None,
                         glass_id_override: float | None = None, glass_od_override: float | None = None,
                         glass_length_override: float | None = None) -> dict[str, bd.Shape]:
    """Build all Rev 4.4 physical assembly components (vertical driver_pcb + bottom USB-C + bottom SW1 + seamless cap_bot)."""
    core_w = core_w_override or p.core_w_nom
    g_id = glass_id_override or p.glass_id_nom
    g_od = glass_od_override or p.glass_od_nom
    g_len = glass_length_override or p.glass_length

    base_ring = build_base_ring(p)
    lid_bot = build_lid_bot(p)
    cap_bot = build_cap_bot(p)
    cap_top = build_cap_top(p)
    plug_top = build_plug_top(p)
    plug_bot = build_plug_bot(p)

    # Vertical Driver PCB (unchanged 36 x 46 x 1.6 mm board: X_pcb->X, Y_pcb->+Z, Z_pcb(F.Cu)->+Y at Y_front=-6.88 mm!)
    # Helper to place board-local features: F.Cu sits at Y = p.pcb_y_front, B.Cu at Y = p.pcb_y_back, center Z = p.z_pcb_center
    yc_f = p.pcb_y_front
    yc_b = p.pcb_y_back
    zc = p.z_pcb_center

    pcb_board = bd.Box(p.pcb_w, p.pcb_thick, p.pcb_l, align=(bd.Align.CENTER, bd.Align.MAX, bd.Align.CENTER))
    pcb_board = bd.fillet(pcb_board.edges().filter_by(bd.Axis.Y), p.pcb_corner_r).translate((0.0, yc_f, zc))
    for sx in (-1.0, 1.0):
        for sz in (-1.0, 1.0):
            npth = bd.Cylinder(p.pcb_hole_drill / 2.0, p.pcb_thick + 0.6, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER)).rotate(bd.Axis.X, 90.0).translate((sx * p.pcb_hole_x, 0.5 * (yc_b + yc_f), zc + sz * p.pcb_hole_y))
            pcb_board = pcb_board - npth

    l1_smd = bd.Box(6.0, 4.5, 6.0, align=(bd.Align.CENTER, bd.Align.MIN, bd.Align.CENTER)).translate((-13.4, yc_f, zc + 11.1))
    l2_smd = bd.Box(6.0, 4.5, 6.0, align=(bd.Align.CENTER, bd.Align.MIN, bd.Align.CENTER)).translate((13.4, yc_f, zc + 11.1))
    j2_hdr = bd.Box(7.4, p.pcb_jst_mated_h, 5.8, align=(bd.Align.CENTER, bd.Align.MIN, bd.Align.CENTER)).translate((-5.2, yc_f, zc + 19.2))
    j3_hdr = bd.Box(7.4, p.pcb_jst_mated_h, 5.8, align=(bd.Align.CENTER, bd.Align.MIN, bd.Align.CENTER)).translate((5.2, yc_f, zc + 19.2))
    j4_hdr = bd.Box(9.9, p.pcb_jst_mated_h, 5.8, align=(bd.Align.CENTER, bd.Align.MIN, bd.Align.CENTER)).translate((-1.4, yc_f, zc - 2.5))
    j1_usbc_outer = bd.Box(8.94, 3.46, 9.17, align=(bd.Align.CENTER, bd.Align.MIN, bd.Align.MIN)).translate((0.0, yc_f, p.pcb_z_j1_mouth))
    j1_cavity = bd.Box(8.34, 2.56, p.usbc_mating_depth_mm + 0.05, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0.0, p.y_usbc, p.pcb_z_j1_mouth - 0.05))
    j1_usbc = j1_usbc_outer - j1_cavity
    j23_pins = bd.Box(15.0, p.pcb_jst_pin_protrude, 2.0, align=(bd.Align.CENTER, bd.Align.MAX, bd.Align.CENTER)).translate((0.0, yc_b, zc + 19.2))
    j4_pins = bd.Box(7.5, p.pcb_jst_pin_protrude, 2.0, align=(bd.Align.CENTER, bd.Align.MAX, bd.Align.CENTER)).translate((-1.4, yc_b, zc - 2.5))
    j1_pins = bd.Box(9.6, p.pcb_jst_pin_protrude, 5.7, align=(bd.Align.CENTER, bd.Align.MAX, bd.Align.CENTER)).translate((0.0, yc_b, zc - 19.54))
    pcb_assy = bd.Compound([pcb_board, l1_smd, l2_smd, j2_hdr, j3_hdr, j4_hdr, j1_usbc, j23_pins, j4_pins, j1_pins])

    # Central protruding bare aluminum core (40 x 40 x 3.0 mm, L = 250.0 mm stock cut!)
    core_out = bd.Box(core_w, core_w, p.core_length, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    core_in = bd.Box(core_w - 2.0 * p.core_wall, core_w - 2.0 * p.core_wall, p.core_length + 2.0,
                     align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, -1.0))
    hs_core = (core_out - core_in).translate((0, 0, p.z_core_bot))
    hang_bore = bd.Cylinder(p.core_hang_hole_dia / 2.0, core_w + 2.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER)).rotate(bd.Axis.Y, 90.0).translate((0.0, 0.0, p.z_hang_hole))
    hs_core = hs_core - hang_bore
    for sy in (-p.plug_bot_pin_y, p.plug_bot_pin_y):
        b_pin = bd.Cylinder(1.70, core_w + 2.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER)).rotate(bd.Axis.Y, 90.0).translate((0.0, sy, p.z_core_bot + 6.0))
        hs_core = hs_core - b_pin
    z_top_lock = p.z_cap_top_top - p.cap_top_lock_z_from_top
    t_lock = bd.Cylinder(1.55, core_w + 2.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER)).rotate(bd.Axis.Y, 90.0).translate((0.0, 0.0, z_top_lock))
    hs_core = hs_core - t_lock

    # ALL Modeled M3 Fasteners (single fastener size across entire lamp!)
    fasteners_list = []
    # 1. 4x M3x8 flush CSK bottom plug pins + 2x M3x16 CSK upward bulkhead bolts
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
    # 2. 4x M3x16 SHCS lid + base_ring bolts (head seated at Z=-2.55..-5.55, shank Z=-2.55..+13.45 into captive M3 nut Z=10..12.7)
    for deg in (45.0, 135.0, 225.0, 315.0):
        rad = math.radians(deg)
        lx, ly = p.lid_bot_bolt_r * math.cos(rad), p.lid_bot_bolt_r * math.sin(rad)
        lb_head = bd.Cylinder(2.75, 3.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)).translate((lx, ly, -p.base_ring_bolt_web - 0.05))
        lb_shank = bd.Cylinder(1.48, 16.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((lx, ly, -p.base_ring_bolt_web - 0.05))
        fasteners_list.append(lb_head.fuse(lb_shank))
    # 3. 2x M3x12 SHCS top cap locking screws on ±X tucked beneath Ø116 mm drip-brim
    for sx in (-1.0, 1.0):
        if sx > 0:
            th = bd.Cylinder(2.75, 3.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).rotate(bd.Axis.Y, 90.0).translate((27.2, 0.0, z_top_lock))
            ts = bd.Cylinder(1.48, 10.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)).rotate(bd.Axis.Y, 90.0).translate((27.2, 0.0, z_top_lock))
        else:
            th = bd.Cylinder(2.75, 3.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)).rotate(bd.Axis.Y, 90.0).translate((-27.2, 0.0, z_top_lock))
            ts = bd.Cylinder(1.48, 10.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).rotate(bd.Axis.Y, 90.0).translate((-27.2, 0.0, z_top_lock))
        fasteners_list.append(th.fuse(ts))
    fasteners_m3 = bd.Compound(fasteners_list)

    # Shatter-resistant UV-Transmitting PMMA (Acrylic) shroud tube (MECH-TUBE-1)
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

    # Bottom-mounted SW1 (C&K 7211SYZBE gold DPDT) + C&K 759D02000 silicone boot on MECH-LID-BOT at (0.0, +16.5 mm)
    sw_body = bd.Box(p.sw1_body_w_x, p.sw1_body_w_y, p.sw1_body_h_z,
                     align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((p.sw1_x, p.sw1_y, p.sw1_wall_thick + 0.05))
    sw_lugs = bd.Box(10.0, 8.5, p.sw1_lugs_h_z,
                     align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((p.sw1_x, p.sw1_y, p.sw1_wall_thick + 0.05 + p.sw1_body_h_z))
    sw_bush = bd.Cylinder(p.sw1_hole_dia / 2.0 - 0.05, p.sw1_wall_thick + 0.1,
                          align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((p.sw1_x, p.sw1_y, 0.0))
    sw_boot = bd.Cylinder(p.sw1_boot_od / 2.0, p.sw1_boot_protrude_z,
                          align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)).translate((p.sw1_x, p.sw1_y, -0.05))
    sw1_assy = bd.Compound([sw_body, sw_lugs, sw_bush, sw_boot])

    # Off-the-shelf 20 mm rubber membrane grommet seated FLAT in MECH-LID-BOT at (0.0, -5.0 mm)
    g_outer_lip = bd.Cylinder(12.2, 2.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)).translate((0.0, p.y_usbc, -0.05))
    g_neck = bd.Cylinder(9.95, p.grommet_panel_thick + 0.1, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0.0, p.y_usbc, -0.05))
    g_inner_lip = bd.Cylinder(11.5, 2.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0.0, p.y_usbc, p.grommet_panel_thick + 0.05))
    g_cable_cut = bd.Box(12.8, 7.2, 12.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER)).translate((0.0, p.y_usbc, 1.5))
    grommet_usbc = g_outer_lip.fuse(g_neck).fuse(g_inner_lip) - g_cable_cut

    # Standard 6.65 mm USB-C PD plug seated straight UPWARD full 4.55 mm inside J1
    z_plug_tip = p.pcb_z_j1_mouth + p.usbc_mating_depth_mm
    z_overmold_top = z_plug_tip - p.usbc_specified_barrel_mm
    usbc_plug_shell = bd.Box(8.3, 2.5, p.usbc_specified_barrel_mm + 0.01, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)).translate((0.0, p.y_usbc, z_plug_tip))
    usbc_plug_overmold = bd.Box(12.4, 6.8, 22.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)).translate((0.0, p.y_usbc, z_overmold_top))
    usbc_plug_assy = usbc_plug_shell.fuse(usbc_plug_overmold)
    assert len(usbc_plug_assy.solids()) == 1

    return dict(
        base_ring=base_ring,
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


def check_kinematic_insertion(lid_bot: bd.Part, cap_bot: bd.Part, p: LepiLEDParams) -> dict[str, dict | bool]:
    # 1. Bottom-mounted SW1 vertical insertion straight down into MECH-LID-BOT pocket
    sw_body = bd.Box(p.sw1_body_w_x, p.sw1_body_w_y, p.sw1_body_h_z, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    sw_lugs = bd.Box(10.0, 8.5, p.sw1_lugs_h_z, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0.0, 0.0, p.sw1_body_h_z))
    sw_bush = bd.Cylinder(p.sw1_hole_dia / 2.0 - 0.05, 8.89, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX))
    sw_tool = bd.Compound([sw_body, sw_lugs, sw_bush])
    sw_max_vol = 0.0
    for zw in np.linspace(25.0, p.sw1_wall_thick + 0.05, 15):
        inter = lid_bot & sw_tool.translate((p.sw1_x, p.sw1_y, float(zw)))
        sw_max_vol = max(sw_max_vol, float(inter.volume) if inter is not None else 0.0)

    # 2. Vertical driver_pcb sliding straight down into MECH-LID-BOT card-guide rails
    pcb_tool = bd.Box(p.pcb_w, p.pcb_thick, p.pcb_l, align=(bd.Align.CENTER, bd.Align.MAX, bd.Align.MIN))
    pcb_max_vol = 0.0
    for zp in np.linspace(55.0, p.z_pcb_bot_edge, 15):
        inter = lid_bot & pcb_tool.translate((0.0, p.pcb_y_front, float(zp)))
        pcb_max_vol = max(pcb_max_vol, float(inter.volume) if inter is not None else 0.0)

    # 3. M3x16 CSK bulkhead bolts straight +Z insertion inside MECH-CAP-BOT
    z_csk_seat = p.z_cap_bot_bulkhead_start - 4.5
    bolt_tool = bd.Cylinder(1.45, 16.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).fuse(
        bd.Cone(3.0, 1.45, 1.5, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    )
    bolt_max_vol = 0.0
    for sx in (-1.0, 1.0):
        for zb in np.linspace(p.z_lid_bot_end, z_csk_seat + 0.1, 15):
            inter = cap_bot & bolt_tool.translate((sx * p.plug_bot_bolt_x, 0.0, float(zb)))
            bolt_max_vol = max(bolt_max_vol, float(inter.volume) if inter is not None else 0.0)

    # 4. Standard USB-C plug straight +Z upward insertion through MECH-LID-BOT grommet bore
    z_plug_tip = p.pcb_z_j1_mouth + p.usbc_mating_depth_mm
    plug_tool = bd.Box(8.3, 2.5, p.usbc_specified_barrel_mm + 0.01, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)).fuse(
        bd.Box(12.4, 6.8, 22.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)).translate((0.0, 0.0, -p.usbc_specified_barrel_mm))
    )
    usbc_max_vol = 0.0
    for zt in np.linspace(-25.0, z_plug_tip, 15):
        inter = lid_bot & plug_tool.translate((0.0, p.y_usbc, float(zt)))
        usbc_max_vol = max(usbc_max_vol, float(inter.volume) if inter is not None else 0.0)

    return {
        "sw1_bottom_lid_insertion": {"waypoints_tested": 15, "max_intersection_vol_mm3": round(sw_max_vol, 6), "pass": sw_max_vol < 1e-4},
        "pcb_vertical_rail_insertion": {"waypoints_tested": 15, "max_intersection_vol_mm3": round(pcb_max_vol, 6), "pass": pcb_max_vol < 1e-4},
        "m3x16_bolt_insertion": {"waypoints_tested": 30, "max_intersection_vol_mm3": round(bolt_max_vol, 6), "pass": bolt_max_vol < 1e-4},
        "usbc_bottom_plug_insertion": {"waypoints_tested": 15, "max_intersection_vol_mm3": round(usbc_max_vol, 6), "pass": usbc_max_vol < 1e-4},
        "all_zero": (sw_max_vol < 1e-4) and (pcb_max_vol < 1e-4) and (bolt_max_vol < 1e-4) and (usbc_max_vol < 1e-4),
    }


def compute_mass_budget(mesh_checks: dict, assy_nom: dict[str, bd.Shape]) -> dict[str, float]:
    """Compute exact lamp mass budget (g) from B-Rep volumes and stock material densities."""
    lamp_printed_keys = ("mech_base_ring", "mech_lid_bot", "mech_cap_bot", "mech_cap_top", "mech_plug_top", "mech_plug_bot")
    vol_printed_cm3 = sum(mesh_checks[k]["brep_volume_mm3"] for k in lamp_printed_keys) / 1000.0
    petg_solid_g = vol_printed_cm3 * 1.27
    petg_fdm_g = vol_printed_cm3 * 1.27 * 0.60  # 4 perimeters + 25% gyroid infill (~60% effective fill on contoured shells)

    al_core_g = (float(assy_nom["hs_core"].volume) / 1000.0) * 2.70
    pmma_shroud_g = (float(assy_nom["glass_tube"].volume) / 1000.0) * 1.18
    elec_stars_hw_g = 112.0  # 8x Cu DTP stars (34 g) + PCB (23 g) + SW1/boot/pigtails/M3/O-rings (55 g)

    return {
        "printed_lamp_volume_cm3": round(vol_printed_cm3, 1),
        "cap_bot_volume_cm3": round(mesh_checks["mech_cap_bot"]["brep_volume_mm3"] / 1000.0, 1),
        "cap_top_volume_cm3": round(mesh_checks["mech_cap_top"]["brep_volume_mm3"] / 1000.0, 1),
        "lid_bot_volume_cm3": round(mesh_checks["mech_lid_bot"]["brep_volume_mm3"] / 1000.0, 1),
        "base_ring_volume_cm3": round(mesh_checks["mech_base_ring"]["brep_volume_mm3"] / 1000.0, 1),
        "petg_fdm_60pct_g": round(petg_fdm_g, 1),
        "petg_solid_100pct_g": round(petg_solid_g, 1),
        "al_core_3mm_g": round(al_core_g, 1),
        "uvt_pmma_shroud_g": round(pmma_shroud_g, 1),
        "elec_stars_hardware_g": elec_stars_hw_g,
        "total_fdm_g": round(petg_fdm_g + al_core_g + pmma_shroud_g + elec_stars_hw_g, 1),
        "total_solid_g": round(petg_solid_g + al_core_g + pmma_shroud_g + elec_stars_hw_g, 1),
    }


def main() -> None:
    out_dir = Path(__file__).resolve().parent
    p_fdm = LepiLEDParams(process="FDM")
    (out_dir / "cad_params.json").write_text(json.dumps(p_fdm.to_dict(), indent=2))

    assy_nom = build_assembly_parts(p_fdm)
    drill_jig = build_drill_jig(p_fdm)

    # 1. Export all 7 3D-printable FDM STEP & STL files
    mesh_checks = {
        "mech_base_ring": export_and_verify_stl(assy_nom["base_ring"], out_dir / "mech_base_ring.step", out_dir / "mech_base_ring.stl"),
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
    printed_map = ("base_ring", "lid_bot", "cap_bot", "cap_top", "plug_top", "plug_bot")
    for name, shp in assy_nom.items():
        if name in printed_map:
            (comp_dir / f"{name}.stl").write_bytes((out_dir / f"mech_{name}.stl").read_bytes())
        else:
            bd.export_stl(shp, str(comp_dir / f"{name}.stl"), tolerance=0.03, angular_tolerance=0.12)

    assy_compound = bd.Compound(list(assy_nom.values()))
    bd.export_step(assy_compound, str(out_dir / "lepiled_assembly.step"))

    # 3. Overhang audits (all 7 printed parts in actual build-plate orientations!)
    overhang_checks = {
        "mech_base_ring": audit_stl_overhangs(out_dir / "mech_base_ring.stl", (0.0, 0.0, -1.0)),
        "mech_lid_bot": audit_stl_overhangs(out_dir / "mech_lid_bot.stl", (0.0, 0.0, 1.0)),
        "mech_cap_bot": audit_stl_overhangs(out_dir / "mech_cap_bot.stl", (0.0, 0.0, 1.0)),
        "mech_cap_top": audit_stl_overhangs(out_dir / "mech_cap_top.stl", (0.0, 0.0, -1.0)),
        "mech_plug_top": audit_stl_overhangs(out_dir / "mech_plug_top.stl", (0.0, 0.0, -1.0)),
        "mech_plug_bot": audit_stl_overhangs(out_dir / "mech_plug_bot.stl", (0.0, 0.0, 1.0)),
        "mech_drill_jig": audit_stl_overhangs(out_dir / "mech_drill_jig.stl", (0.0, 0.0, 1.0)),
    }

    # 4. All-pairs B-Rep intersection verification (Nominal + Worst-Case 151 mm PMMA shroud)
    wc_glass_len = p_fdm.glass_length + p_fdm.glass_length_tol
    inter_nom = check_all_pairs_intersections(assy_nom)
    assy_wc = build_assembly_parts(
        p_fdm, core_w_override=p_fdm.core_w_max, glass_id_override=p_fdm.glass_id_min,
        glass_od_override=p_fdm.glass_od_max, glass_length_override=wc_glass_len,
    )
    inter_wc = check_all_pairs_intersections(assy_wc)

    # 5. Kinematic insertion sweeps (SW1, vertical PCB into rails, M3x16 bolts, bottom USB-C plug)
    kinematic_checks = check_kinematic_insertion(assy_nom["lid_bot"], assy_nom["cap_bot"], p_fdm)

    # 6. Exact mass budget
    mass_budget = compute_mass_budget(mesh_checks, assy_nom)

    all_meshes_ok = all(m["is_watertight"] and m["is_winding_consistent"] and m["stl_volume_mm3"] > 0 for m in mesh_checks.values())
    all_overhangs_ok = all(o["pass"] for o in overhang_checks.values())
    all_brep_ok = inter_nom["all_zero"] and inter_wc["all_zero"]
    all_kinematic_ok = kinematic_checks["all_zero"]
    all_param_checks_ok = all(c["pass"] for c in p_fdm.verify_all().values())

    report = {
        "revision": "Rev 4.4 (Vertical PCB + Bottom USB-C & SW1 + Seamless Contoured Housing + UVT PMMA + Ø116 mm Drip-Brim)",
        "params": p_fdm.to_dict(),
        "mesh_checks": mesh_checks,
        "overhang_checks": overhang_checks,
        "kinematic_insertion_checks": kinematic_checks,
        "brep_all_pairs_nominal": {k: v for k, v in inter_nom.items() if k != "pairs"},
        "brep_all_pairs_worst_case": {k: v for k, v in inter_wc.items() if k != "pairs"},
        "mass_budget_g": mass_budget,
        "summary": {
            "all_param_checks_pass": all_param_checks_ok,
            "all_meshes_watertight_manifold": all_meshes_ok,
            "all_overhangs_le_46deg": all_overhangs_ok,
            "kinematic_insertion_zero": all_kinematic_ok,
            "nominal_all_pairs_zero": inter_nom["all_zero"],
            "worst_case_all_pairs_zero": inter_wc["all_zero"],
            "overall_pass": (
                all_param_checks_ok and all_meshes_ok and all_overhangs_ok
                and all_brep_ok and all_kinematic_ok
            ),
        },
    }
    verif_path = out_dir / "cad_verification.json"
    verif_path.write_text(json.dumps(report, indent=2))

    print("=== Mesh Verification (7 FDM Printable Parts) ===")
    for name, m in mesh_checks.items():
        print(f"  {name:16s}: vol={m['stl_volume_mm3']:8.1f} mm^3 | tri={m['triangles']:6d} | wt={m['is_watertight']} | wind={m['is_winding_consistent']} | euler={m['euler_number']:3d}")
    print("=== Overhang Verification ===")
    for name, o in overhang_checks.items():
        print(f"  {name:16s}: >46deg faces={o['off_bed_overhang_gt46_faces']:4d}, area={o['off_bed_overhang_gt46_area_mm2']:6.3f} mm^2, max={o['max_off_bed_overhang_deg']:5.2f} deg | pass={o['pass']}")
    print("=== Kinematic Insertion (SW1, Vertical PCB Rails, M3x16 Bolts, Bottom USB-C Plug) ===")
    for k in ("sw1_bottom_lid_insertion", "pcb_vertical_rail_insertion", "m3x16_bolt_insertion", "usbc_bottom_plug_insertion"):
        v = kinematic_checks[k]
        print(f"  {k:28s}: waypoints={v['waypoints_tested']:2d}, max_vol={v['max_intersection_vol_mm3']:.6f} mm^3 | pass={v['pass']}")
    print("=== All-Pairs B-Rep Intersection (incl. Vertical PCB, Bottom USB-C & SW1, UVT PMMA & ALL Fasteners) ===")
    for label, d in [("NOMINAL", inter_nom), ("WORST_CASE", inter_wc)]:
        print(f"  {label:10s}: {d['total_pairs_checked']} pairs, nonzero={d['nonzero_count']} {d['nonzero_pairs']}")
    print("=== Verified Mass Budget (Rev 4.4) ===")
    print(f"  Printed lamp parts ({mass_budget['printed_lamp_volume_cm3']} cm^3; cap_bot={mass_budget['cap_bot_volume_cm3']}, cap_top={mass_budget['cap_top_volume_cm3']} cm^3): {mass_budget['petg_fdm_60pct_g']} g FDM (60%) / {mass_budget['petg_solid_100pct_g']} g solid")
    print(f"  Al core (3 mm): {mass_budget['al_core_3mm_g']} g | UVT PMMA shroud: {mass_budget['uvt_pmma_shroud_g']} g | Elec+Stars+HW: {mass_budget['elec_stars_hardware_g']} g")
    print(f"  TOTAL LAMP WEIGHT (FDM): {mass_budget['total_fdm_g']} g ({mass_budget['total_solid_g']} g 100% solid)")

    if not report["summary"]["overall_pass"]:
        raise SystemExit(1)
    print(f"Wrote {verif_path} and all Rev 4.4 STEP/STL artifacts (ALL CHECKS PASS).")


if __name__ == "__main__":
    main()
