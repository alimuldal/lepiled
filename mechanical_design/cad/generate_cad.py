#!/usr/bin/env python3
"""
Parametric 3D CAD Generator for LepiLED DIY Maxi Switch (Rev 4.5 — Compact, Horizontal PCB, Radial O-Rings & Weatherproof Split Gland) using build123d.

Exports (6 watertight, 100% support-free FDM PETG/ASA parts — MECH-PLUG-BOT eliminated!):
  - mech_base_ring.step / .stl     (Bolt-on Ø92 x 20 mm protective standing ring w/ 4x wide cable & drainage cutouts)
  - mech_lid_bot.step / .stl       (Flat Ø92 x 5 mm lid + 7 mm radial O-ring spigot + SW1 + M20 split gland + ePTFE vent + D12 lightpipe)
  - mech_cap_bot.step / .stl       (100% seamless shell w/ 4x horizontal PCB standoffs, 9x7.5 mm JST wire slots, radial O-ring & 2x M3 core lock)
  - mech_cap_top.step / .stl       (15-deg sloped conical Ø88 mm rain roof + radial O-ring + internal core silicone seal + 2x M3 lock)
  - mech_plug_top.step / .stl      (Weatherproof press-fit rain cap sealing open top of protruding 30x30x3 mm Al tube)
  - mech_drill_jig.step / .stl     (Snap-on 30.6 mm U-channel drill guide for all 16x M3 star holes + 4x cap-lock holes)
  - lepiled_assembly.step          (Full multi-part B-Rep assembly incl. ALL 57 SMDs from driver_pcb_cpl.csv!)
  - cad_verification.json          (trimesh manifold metrics + all-pairs B-Rep 0.000 mm^3 checks + overhang & mass audit)
"""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import build123d as bd
import numpy as np
import trimesh

from params import LepiLEDParams


# Accurate SMD package 3D bounding boxes (length_x, width_y, height_z) in mm for ALL 57 SMDs in driver_pcb_cpl.csv
SMD_PACKAGE_DIMS: dict[str, tuple[float, float, float]] = {
    "U1": (3.0, 2.8, 1.0), "U2": (3.0, 2.8, 1.0),          # TSOT25 AL8860WT-7
    "U3": (3.1, 3.1, 0.85),                                 # W-DFN3030-14 AP33771C
    "U4": (5.0, 6.2, 1.75),                                 # SOIC-8 LM393B
    "U5": (3.0, 2.5, 1.12),                                 # SOT-23-3 LM4040
    "Q1": (3.0, 2.5, 1.12), "Q2": (3.0, 2.5, 1.12), "Q3": (3.0, 2.5, 1.12),  # SOT-23-3
    "F1": (4.7, 3.4, 1.25),                                 # 1812 PTC F1
    "D9": (4.6, 2.8, 2.30), "D10": (4.6, 2.8, 2.30),        # SMA B340A
    "D11": (4.7, 3.8, 2.44),                                # SMB SMBJ22A
    "D12": (1.7, 0.9, 0.80),                                # 0603 Green LED
    "D13": (2.6, 1.4, 1.05), "D14": (2.6, 1.4, 1.05),       # SOD-323 ESD
    "D15": (2.6, 1.4, 1.05), "D16": (2.6, 1.4, 1.05),       # SOD-323 ESD
    "L1": (6.1, 6.1, 4.50), "L2": (6.1, 6.1, 4.50),         # SRN6045-680M
    "R3": (3.3, 1.7, 0.70), "R4": (3.3, 1.7, 0.70), "R8": (3.3, 1.7, 0.70),  # 1206
    "R7": (2.1, 1.3, 0.65), "R12": (2.1, 1.3, 0.65), "R14": (2.1, 1.3, 0.65),
    "R16": (2.1, 1.3, 0.65), "R22": (2.1, 1.3, 0.65), "R23": (2.1, 1.3, 0.65),  # 0805
    "C1": (2.1, 1.3, 1.40), "C11": (2.1, 1.3, 1.40), "C12": (2.1, 1.3, 1.40),   # 0805 MLCC
    "C2": (3.3, 1.7, 1.80), "C3": (3.3, 1.7, 1.80), "C10": (3.3, 1.7, 1.80),    # 1206 MLCC
}


def _teardrop_profile_wire(radius: float, angle_deg: float = 42.0) -> bd.Face:
    """Create a horizontal-hole teardrop Face in XY plane with +Y apex (both arc & roof <= angle_deg overhang!)."""
    # Arc stops at (90 - angle_deg) from +Y so circular overhang <= angle_deg; straight roof slopes at angle_deg!
    theta_arc = math.radians(90.0 - angle_deg)
    xt = radius * math.sin(theta_arc)
    yt = radius * math.cos(theta_arc)
    y_apex = yt + xt / math.tan(math.radians(angle_deg))
    with bd.BuildSketch() as sk:
        with bd.BuildLine():
            bd.ThreePointArc((-xt, yt), (0.0, -radius), (xt, yt))
            bd.Line((xt, yt), (0.0, y_apex))
            bd.Line((0.0, y_apex), (-xt, yt))
        bd.make_face()
    return sk.face()


def _pitched_rect_profile(width: float, rect_h: float, roof_angle_deg: float = 45.0) -> bd.Face:
    """Create a centered-X, bottom-Y=0 rectangle topped with a symmetric pitched roof in XY plane."""
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


def _radial_bore_oring_cut(r_bore: float, r_groove: float, z_flat: float, flat_w: float, ramp_dir: float) -> bd.Part:
    """
    Create a 45-deg self-supporting annular radial O-ring groove cut into an internal bore wall.
    ramp_dir = +1.0 puts the 45-deg ramp above z_flat + flat_w (upright print);
    ramp_dir = -1.0 puts the 45-deg ramp below z_flat - flat_w (inverted print).
    """
    dr = r_groove - r_bore
    if ramp_dir > 0:
        c_main = (
            bd.Cylinder(r_groove, flat_w, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
            - bd.Cylinder(r_bore - 0.2, flat_w, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
        ).translate((0.0, 0.0, z_flat))
        c_ramp = (
            bd.Cone(r_groove, r_bore, dr, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
            - bd.Cylinder(r_bore - 0.2, dr, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
        ).translate((0.0, 0.0, z_flat + flat_w))
    else:
        c_main = (
            bd.Cylinder(r_groove, flat_w, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX))
            - bd.Cylinder(r_bore - 0.2, flat_w, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX))
        ).translate((0.0, 0.0, z_flat))
        c_ramp = (
            bd.Cone(r_bore, r_groove, dr, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX))
            - bd.Cylinder(r_bore - 0.2, dr, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX))
        ).translate((0.0, 0.0, z_flat - flat_w))
    return c_main.fuse(c_ramp)


def _radial_spigot_oring_cut(r_spigot: float, r_groove: float, z_flat: float, flat_w: float) -> bd.Part:
    """Create a 45-deg self-supporting external radial O-ring groove cut into a vertical spigot (upright print)."""
    dr = r_spigot - r_groove
    c_main = (
        bd.Cylinder(r_spigot + 0.5, flat_w, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
        - bd.Cylinder(r_groove, flat_w, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    ).translate((0.0, 0.0, z_flat))
    c_ramp = (
        bd.Cylinder(r_spigot + 0.5, dr, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
        - bd.Cone(r_groove, r_spigot, dr, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    ).translate((0.0, 0.0, z_flat + flat_w))
    return c_main.fuse(c_ramp)


def build_base_ring(p: LepiLEDParams) -> bd.Part:
    """
    Build MECH-BASE-RING: bolt-on Ø92 x 20 mm protective standing ring & switch/cable-gland guard (Z = -20.0 .. 0.0 mm):
      - Clamps underneath MECH-LID-BOT using the exact same 4x M3x16 SHCS lid bolts
      - Shields both C&K 759D02000 silicone boot (5 mm clearance) and M20 split cable gland nut (3.5 mm clearance)
      - 4x wide 24 x 9.5 mm drainage & captured USB-C cable exit cutouts at 0/90/180/270 deg
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
    Build Rev 4.5 MECH-LID-BOT: flat Ø92 x 5.0 mm bottom lid + 7.0 mm radial O-ring spigot (MECH-GASKET-3):
      - Standard 70 x 2.5 mm VMQ70 radial O-ring groove on spigot (14% squeeze, 45-deg upper ramp -> 0 overhang!)
      - Bottom M20 IP68 split waterproof cable gland bore (Ø20.4 mm) at (0.0, -18.5 mm)
      - Bottom-mounted SW1 (C&K 7211SYZBE) vertical Ø6.35 mm bore + 2.5 mm anti-rotation pocket at (0.0, +18.5 mm)
      - Ø2.5 mm pressure-equalization vent port at (-23.0, 0.0 mm) for adhesive Ø8 mm IP68 ePTFE breather patch
      - Ø2.6 mm clear PMMA/filament D12 PD-status lightpipe bore at (+16.0, +1.4 mm) aligned straight under D12!
      - 4x plain M3 clearance holes at R = 41.5 mm; prints flat upright on Z = 0 with 0.000 mm^2 >46 deg overhang!
    """
    r_lid = p.lid_bot_od / 2.0
    base = bd.Cylinder(r_lid, p.lid_bot_thick, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))

    # Hollow radial O-ring sealing spigot (Z = 5.0 .. 12.0 mm)
    r_sp_out = p.lid_spigot_od / 2.0
    r_sp_in = p.lid_spigot_id / 2.0
    spigot = (
        bd.Cylinder(r_sp_out, p.lid_spigot_h, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
        - bd.Cylinder(r_sp_in, p.lid_spigot_h + 1.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    ).translate((0.0, 0.0, p.z_lid_bot_end))
    part = base.fuse(spigot)

    # Top lead-in chamfer on spigot for smooth O-ring assembly
    sp_top = part.edges().filter_by(bd.GeomType.CIRCLE).filter_by_position(bd.Axis.Z, p.z_lid_bot_end + p.lid_spigot_h - 0.1, p.z_lid_bot_end + p.lid_spigot_h + 0.1)
    outer_sp_top = [e for e in sp_top if e.radius > r_sp_out - 0.5]
    if outer_sp_top:
        part = bd.chamfer(outer_sp_top, length=0.6)

    # Radial O-ring groove for MECH-GASKET-3 (70 x 2.5 mm VMQ70, Z = 6.5 .. 11.05 mm, 45-deg upper ramp!)
    g3 = _radial_spigot_oring_cut(r_sp_out, p.bot_oring_groove_od / 2.0, p.z_lid_bot_end + 1.5, p.bot_oring_flat_w)
    part = part - g3

    # 4x plain M3 bolt holes at R = 41.5 mm
    for deg in (45.0, 135.0, 225.0, 315.0):
        rad = math.radians(deg)
        hx, hy = p.lid_bot_bolt_r * math.cos(rad), p.lid_bot_bolt_r * math.sin(rad)
        c_thru = bd.Cylinder(p.m3_clearance_dia / 2.0, p.lid_bot_thick + 2.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((hx, hy, -1.0))
        part = part - c_thru

    # M20 split waterproof cable gland bore at (0.0, -18.5 mm)
    gland_bore = bd.Cylinder(p.gland_bore_dia / 2.0, p.lid_bot_thick + 2.0,
                             align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((p.gland_x, p.gland_y, -1.0))
    part = part - gland_bore

    # Bottom-mounted SW1 vertical Ø6.35 mm bore + 2.5 mm upper anti-rotation pocket at (0.0, +18.5 mm)
    sw_bore = bd.Cylinder(p.sw1_hole_dia / 2.0 + p.print_clearance * 0.5, p.lid_bot_thick + 2.0,
                          align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((p.sw1_x, p.sw1_y, -1.0))
    sw_recess = bd.Box(p.sw1_body_w_x + 0.8, p.sw1_body_w_y + 0.8, p.lid_bot_thick - p.sw1_wall_thick + 0.5,
                       align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((p.sw1_x, p.sw1_y, p.sw1_wall_thick))
    part = part - sw_bore - sw_recess

    # Pressure-equalization IP68 ePTFE breather vent hole + D12 clear lightpipe hole
    vent_bore = bd.Cylinder(p.vent_hole_dia / 2.0, p.lid_bot_thick + 2.0,
                            align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((p.vent_x, p.vent_y, -1.0))
    d12_bore = bd.Cylinder(p.d12_lightpipe_dia / 2.0, p.lid_bot_thick + 2.0,
                           align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((p.d12_lightpipe_x, p.d12_lightpipe_y, -1.0))
    part = part - vent_bore - d12_bore

    return part


def build_cap_bot(p: LepiLEDParams) -> bd.Part:
    """
    Build seamless Rev 4.5 MECH-CAP-BOT (prints INVERTED on Z_cap_bot_top = 72.0 mm -> 0.000 mm^2 >46 deg overhang!):
      - 100% seamless outer shell (Ø72 collar -> 45-deg -> Ø82 mid bay -> 45-deg -> Ø92 flange)
      - 4x integral Ø5.5 mm bulkhead standoffs growing straight up during inverted print (H1..H4 + 4x M2.5x8 screws)
      - Direct 12 mm core socket (30.8 x 30.8 mm, Z=48..60 mm) w/ 45-deg support-free closure pyramid & 2x M3x10 radial lock screws
        6 mm BELOW the shroud seal (MECH-PLUG-BOT completely eliminated!)
      - 2x generous 9.0 x 7.5 mm wire channels at ±Y passing pre-crimped 2-pin JST-XH plugs straight through!
      - Radial bore O-ring groove (MECH-GASKET-1: 60 x 3.0 mm VMQ70) on Ø60.8 mm shroud bore (20% nom squeeze)
      - 4x captive M3 hex-nut pockets w/ 47-deg print-up roofs & snap-in retention detents at R = 41.5 mm!
    """
    r_bot = p.cap_bot_od / 2.0          # 46.0
    r_mid = p.cap_bot_mid_od / 2.0      # 41.0
    r_col = p.cap_bot_collar_od / 2.0   # 36.0
    z_base = p.z_lid_bot_end            # 5.0
    z_flange_top = 15.0
    z_mid_bot = z_flange_top + (r_bot - r_mid)      # 20.0 (45-deg taper)
    z_mid_top = 45.0
    z_col_bot = z_mid_top + (r_mid - r_col)         # 50.0 (45-deg taper)
    z_top = p.z_cap_bot_top                         # 72.0

    # Outer axisymmetric contoured shell (going from Z=72 down to Z=5, radius only expands at <= 45 deg!)
    s1 = bd.Cylinder(r_bot, z_flange_top - z_base, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, z_base))
    s2 = bd.Cone(r_bot, r_mid, z_mid_bot - z_flange_top, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, z_flange_top))
    s3 = bd.Cylinder(r_mid, z_mid_top - z_mid_bot, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, z_mid_bot))
    s4 = bd.Cone(r_mid, r_col, z_col_bot - z_mid_top, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, z_mid_top))
    s5 = bd.Cylinder(r_col, z_top - z_col_bot, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, z_col_bot))
    part = s1.fuse(s2).fuse(s3).fuse(s4).fuse(s5)

    # Bottom outer edge chamfer (top edge when printed inverted!)
    bot_edges = part.edges().filter_by(bd.GeomType.CIRCLE).filter_by_position(bd.Axis.Z, z_base - 0.1, z_base + 0.1)
    part = bd.chamfer(bot_edges, length=p.cap_chamfer)

    # Electronics bay cavity (Ø74.4 mm, Z = 5.0 .. 35.0 mm — flat floor at Z=35.0 faces UP when printed inverted!)
    r_cav = p.cap_bot_cavity_dia / 2.0
    cav = bd.Cylinder(r_cav, p.cap_bot_ceiling_z - z_base + 0.1, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, z_base - 0.1))
    part = part - cav

    # 4x integral Ø5.5 mm PCB standoffs hanging down from Z = 35.0 to B.Cu = 28.6 mm (print straight UP inverted!)
    standoff_h = p.cap_bot_ceiling_z - p.z_pcb_bcu  # 6.4 mm
    for sx in (-1.0, 1.0):
        for sy in (-1.0, 1.0):
            hx = sx * p.pcb_hole_x
            hy = p.pcb_y_center + sy * p.pcb_hole_y
            boss = bd.Cylinder(p.pcb_standoff_od / 2.0, standoff_h + 1.0,
                               align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((hx, hy, p.z_pcb_bcu))
            pilot = bd.Cylinder(p.pcb_standoff_pilot_dia / 2.0, standoff_h + 2.0,
                                align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((hx, hy, p.z_pcb_bcu - 0.1))
            part = part.fuse(boss) - pilot

    # 4x M3 clearance bores + radial side-entry captive M3 hex-nut pockets (47-deg print-up roofs toward -Z!)
    r_bolt = p.m3_clearance_dia / 2.0
    z_nut_top = z_base + 9.2   # Z = 14.2 mm (flat seat closer to bed when inverted!)
    nut_prof = _pitched_rect_profile(p.m3_nut_af, p.m3_nut_thick, 47.0)
    nut_len = (r_bot + 1.0) - (p.lid_bot_bolt_r - p.m3_nut_af / 2.0 - 0.4)
    for deg in (45.0, 135.0, 225.0, 315.0):
        rad = math.radians(deg)
        ix, iy = p.lid_bot_bolt_r * math.cos(rad), p.lid_bot_bolt_r * math.sin(rad)
        hole = bd.Cylinder(r_bolt, 12.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((ix, iy, z_base - 0.1))
        part = part - hole
        # Extrude along +X, rotate so pitched roof points in -Z (print-up when inverted!)
        slot = bd.extrude(nut_prof, nut_len).rotate(bd.Axis.X, -90.0).rotate(bd.Axis.Z, 90.0)
        slot = slot.translate((p.lid_bot_bolt_r - p.m3_nut_af / 2.0 - 0.4, 0.0, z_nut_top)).rotate(bd.Axis.Z, deg)
        part = part - slot

    # Shroud bore (Ø60.8 mm, Z = 62.3 .. 75.5 mm -> clears +2.0 mm oversize tube!) + 45-deg cone to R=0.2 mm apex (0 overhang!)
    r_bore = p.glass_bore_id / 2.0
    z_bore_bot = p.z_glass_bot - 1.2
    shroud_bore = bd.Cylinder(r_bore, z_top - z_bore_bot + 0.5,
                              align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, z_bore_bot))
    r_cone_bot = 0.2
    cone_h = (r_bore - r_cone_bot) * 1.05  # 31.71 mm -> 43.6-deg self-supporting cone closing at Z = 32.09 mm!
    shroud_seat_cone = bd.Cone(r_cone_bot, r_bore, cone_h, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)).translate((0, 0, z_bore_bot))
    g1 = _radial_bore_oring_cut(r_bore, p.glass_oring_groove_od / 2.0, z_top - 3.5, p.glass_oring_flat_w, ramp_dir=-1.0)
    part = part - shroud_bore - shroud_seat_cone - g1

    # Direct square core socket (30.8 x 30.8 mm, Z = 51.5 .. 75.5 mm) + 45-deg corner closure pyramid (0.000 mm^2 overhang!)
    core_sock = bd.Box(p.core_pocket_w, p.core_pocket_w, z_top - p.z_core_bot + 1.0,
                       align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, p.z_core_bot))
    pyr_h = 0.5 * p.core_pocket_w - 0.2
    with bd.BuildSketch(bd.Plane.XY.offset(p.z_core_bot)) as sk_base:
        bd.Rectangle(p.core_pocket_w, p.core_pocket_w)
    with bd.BuildSketch(bd.Plane.XY.offset(p.z_core_bot - pyr_h)) as sk_tip:
        bd.Rectangle(0.4, 0.4)
    part = part - core_sock - bd.loft([sk_tip.sketch, sk_base.sketch])

    # 2x generous 9.0 x 7.5 mm wire channels at ±Y passing pre-crimped 7.4 x 5.75 mm JST-XH plugs straight through!
    y_slot_c = p.core_pocket_w / 2.0 + p.core_wire_slot_d / 2.0 - 0.1  # 19.05 mm (inside R=26.5 PMMA ID!)
    for sy in (-1.0, 1.0):
        wslot = bd.Box(p.core_wire_slot_w, p.core_wire_slot_d + 0.2, (p.z_glass_bot + 2.0) - (p.cap_bot_ceiling_z - 1.0),
                       align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0.0, sy * y_slot_c, p.cap_bot_ceiling_z - 1.0))
        part = part - wslot

    # 2x radial M3x10 SHCS core locking screw teardrop bores + counterbores on ±X at Z = 57.5 mm (6 mm BELOW shroud!)
    td_thru = _teardrop_profile_wire(p.m3_clearance_dia / 2.0, 42.0)
    td_cb = _teardrop_profile_wire(3.3, 42.0)
    for sx in (-1.0, 1.0):
        # Extrude along +Z -> rotate(X,-90) maps +Z->+Y, +Y->-Z -> rotate(Z,-90) maps +Y->+X, +Y_apex->-Z (print-up inverted!)
        h_lock = bd.extrude(td_thru, 30.0).rotate(bd.Axis.X, -90.0).rotate(bd.Axis.Z, -90.0)
        h_cb = bd.extrude(td_cb, 20.0).rotate(bd.Axis.X, -90.0).rotate(bd.Axis.Z, -90.0)
        if sx > 0:
            h_lock = h_lock.translate((14.0, 0.0, p.cap_bot_lock_z))
            h_cb = h_cb.translate((22.0, 0.0, p.cap_bot_lock_z))
        else:
            h_lock = h_lock.rotate(bd.Axis.Z, 180.0).translate((-14.0, 0.0, p.cap_bot_lock_z))
            h_cb = h_cb.rotate(bd.Axis.Z, 180.0).translate((-22.0, 0.0, p.cap_bot_lock_z))
        part = part - h_lock - h_cb

    return part


def build_cap_top(p: LepiLEDParams) -> bd.Part:
    """
    Build Rev 4.5 MECH-CAP-TOP (prints UPRIGHT on Z_cap_top_bot = 163.0 mm -> 0.000 mm^2 >46 deg overhang!):
      - 15-deg sloped conical Ø88 mm rain-shedding roof (ZERO flat water-pooling saucer!)
      - 45-deg self-supporting underside flare from Ø72 mm shroud skirt to Ø88 mm drip-brim (+14 mm past shroud)
      - Radial bore O-ring groove (MECH-GASKET-2: 60 x 3.0 mm VMQ70) on Ø60.8 mm shroud bore (20% nom squeeze)
      - Internal neutral-cure silicone core seal groove BELOW the 2x M3x10 radial locking screws!
    """
    r_skirt = p.cap_top_skirt_od / 2.0    # 36.0
    r_brim = p.cap_top_brim_od / 2.0      # 44.0
    r_col = p.cap_top_collar_od / 2.0     # 25.3
    z_bot = p.z_cap_top_bot               # 163.0
    z_fl_bot = p.z_cap_top_brim_bot       # 171.0
    z_rim_bot = p.z_cap_top_brim_rim_bot  # 179.0
    z_rim_top = p.z_cap_top_brim_rim_top  # 181.5
    z_top = p.z_cap_top_top               # 186.511

    c_skirt = bd.Cylinder(r_skirt, z_fl_bot - z_bot, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, z_bot))
    c_flare = bd.Cone(r_skirt, r_brim, z_rim_bot - z_fl_bot, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, z_fl_bot))
    c_rim = bd.Cylinder(r_brim, z_rim_top - z_rim_bot, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, z_rim_bot))
    c_roof = bd.Cone(r_brim, r_col, z_top - z_rim_top, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, z_rim_top))
    part = c_skirt.fuse(c_flare).fuse(c_rim).fuse(c_roof)

    # Subtle outer rim chamfer
    rim_edges = part.edges().filter_by(bd.GeomType.CIRCLE).filter_by_position(bd.Axis.Z, z_rim_bot - 0.1, z_rim_bot + 0.1)
    part = bd.chamfer(rim_edges, length=0.6)

    # Shroud bore (Ø60.8 mm, Z = 163.0 .. 176.2 mm -> clears +2.0 mm oversize tube!) + 45-deg cone all the way to R=15.0 mm (0 overhang!)
    r_bore = p.glass_bore_id / 2.0
    z_bore_top = p.z_glass_top + 1.2
    shroud_bore = bd.Cylinder(r_bore, z_bore_top - z_bot + 0.5,
                              align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, z_bot - 0.5))
    r_cone_top = 15.0
    cone_h = r_bore - r_cone_top  # 15.4 mm -> exact 45-deg self-supporting cone entering square core aperture!
    shroud_stop = bd.Cone(r_bore, r_cone_top, cone_h, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, z_bore_top))
    g2 = _radial_bore_oring_cut(r_bore, p.glass_oring_groove_od / 2.0, z_bot + 3.5, p.glass_oring_flat_w, ramp_dir=+1.0)
    part = part - shroud_bore - shroud_stop - g2

    # Protruding 30.8 x 30.8 mm square core aperture + top weather-fillet chamfer groove
    core_thru = bd.Box(p.core_pocket_w, p.core_pocket_w, (z_top - z_bot) + 2.0,
                       align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, z_bot - 1.0))
    part = part - core_thru
    w_g = p.core_pocket_w + 2.0 * p.cap_top_seal_groove
    with bd.BuildSketch(bd.Plane.XY.offset(z_top + 0.05)) as sk_top:
        bd.Rectangle(w_g, w_g)
    with bd.BuildSketch(bd.Plane.XY.offset(z_top - p.cap_top_seal_groove)) as sk_bot:
        bd.Rectangle(p.core_pocket_w, p.core_pocket_w)
    part = part - bd.loft([sk_bot.sketch, sk_top.sketch])

    # 2x radial M3x10 SHCS core locking screw teardrop bores + counterbores on ±X at Z = 185.0 mm (+Z apex upright!)
    z_lock = p.z_cap_top_lock
    td_thru = _teardrop_profile_wire(p.m3_clearance_dia / 2.0, 42.0)
    td_cb = _teardrop_profile_wire(3.3, 42.0)
    for sx in (-1.0, 1.0):
        h_lock = bd.extrude(td_thru, 34.0).rotate(bd.Axis.X, 90.0).rotate(bd.Axis.Z, 90.0)
        h_cb = bd.extrude(td_cb, 26.0).rotate(bd.Axis.X, 90.0).rotate(bd.Axis.Z, 90.0)
        if sx > 0:
            h_lock = h_lock.translate((14.0, 0.0, z_lock))
            h_cb = h_cb.translate((22.0, 0.0, z_lock))
        else:
            h_lock = h_lock.rotate(bd.Axis.Z, 180.0).translate((-14.0, 0.0, z_lock))
            h_cb = h_cb.rotate(bd.Axis.Z, 180.0).translate((-22.0, 0.0, z_lock))
        part = part - h_lock - h_cb

    return part


def build_plug_top(p: LepiLEDParams) -> bd.Part:
    """Build MECH-PLUG-TOP: weatherproof press-fit rain cap sealing the open top of the protruding 30x30x3 mm Al tube."""
    insert = bd.Box(p.plug_top_w, p.plug_top_w, p.plug_top_insert_h,
                    align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, p.z_core_top - p.plug_top_insert_h))
    insert = bd.fillet(insert.edges().filter_by(bd.Axis.Z), 1.5)
    cap = bd.Box(p.plug_top_cap_w, p.plug_top_cap_w, p.plug_top_cap_h,
                 align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, p.z_core_top))
    cap = bd.fillet(cap.edges().filter_by(bd.Axis.Z), 1.5)
    top_edges = cap.edges().filter_by_position(bd.Axis.Z, p.z_plug_top_end - 0.1, p.z_plug_top_end + 0.1)
    cap = bd.chamfer(top_edges, length=1.2)
    return insert.fuse(cap)


def build_drill_jig(p: LepiLEDParams) -> bd.Part:
    """Build MECH-DRILL-JIG: snap-on 30.6 mm U-channel drill template for all 16x M3 star holes + cap_bot/cap_top locks."""
    wall = 3.0
    inner_w = p.core_w_nom + 0.6
    outer_w = inner_w + 2.0 * wall
    jig_len = 142.0  # Covers bottom lock (6 mm), Vis stars, UV stars, and top cap lock (134 mm)!
    leg_h = 15.0

    base = bd.Box(wall, outer_w, jig_len, align=(bd.Align.MIN, bd.Align.CENTER, bd.Align.MIN))
    leg_pos = bd.Box(leg_h, wall, jig_len, align=(bd.Align.MIN, bd.Align.MAX, bd.Align.MIN)).translate((0, outer_w / 2.0, 0))
    leg_neg = bd.Box(leg_h, wall, jig_len, align=(bd.Align.MIN, bd.Align.MIN, bd.Align.MIN)).translate((0, -outer_w / 2.0, 0))
    end_stop = bd.Box(10.0, outer_w, wall, align=(bd.Align.MIN, bd.Align.CENTER, bd.Align.MAX))
    jig = base.fuse(leg_pos).fuse(leg_neg).fuse(end_stop)

    # All Ø2.5 mm M3 tap-drill pilot guides along centerline (Y=0) referenced from bottom end of 200 mm core!
    guide_zs = (
        p.cap_bot_lock_z - p.z_core_bot,                # 6.0 mm (MECH-CAP-BOT radial lock on ±X)
        p.axial_vis_to_bot_mm - p.star_bolt_r,          # 44.0 mm (Vis star bottom screw)
        p.axial_vis_to_bot_mm + p.star_bolt_r,          # 63.0 mm (Vis star top screw)
        (p.z_led_uv - p.z_core_bot) - p.star_bolt_r,    # 76.0 mm (UV star bottom screw)
        (p.z_led_uv - p.z_core_bot) + p.star_bolt_r,    # 95.0 mm (UV star top screw)
        p.z_cap_top_lock - p.z_core_bot,                # 134.0 mm (MECH-CAP-TOP radial lock on ±X)
    )
    for z_rel in guide_zs:
        guide = bd.Cylinder(1.30, wall + 2.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER)).rotate(bd.Axis.Y, 90.0).translate((wall / 2.0, 0.0, z_rel))
        jig = jig - guide

    jig = jig.rotate(bd.Axis.Y, -90.0)
    bb = jig.bounding_box()
    return jig.translate((0.0, 0.0, -bb.min.Z))


def _load_all_57_smd_solids(p: LepiLEDParams) -> list[bd.Shape]:
    """Load ALL 57 SMD positions from pcb_design/driver_pcb_cpl.csv and build accurate downward-facing 3D boxes."""
    cpl_path = Path(__file__).resolve().parents[2] / "pcb_design" / "driver_pcb_cpl.csv"
    solids: list[bd.Shape] = []
    with cpl_path.open("r", encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            ref = row["Designator"].strip()
            bx = float(row["Mid X"])
            by = float(row["Mid Y"])
            rot = float(row["Rotation"])
            # Default 0603 dimensions for unlisted resistors/capacitors
            lx, wy, hz = SMD_PACKAGE_DIMS.get(ref, (1.7, 0.9, 0.65))
            if int(round(rot)) % 180 == 90:
                lx, wy = wy, lx
            # Horizontal PCB SMD-down: X_global = X_board, Y_global = pcb_y_center + Y_board, Z downward from pcb_z_fcu
            box = bd.Box(lx, wy, hz, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)).translate((bx, p.pcb_y_center + by, p.pcb_z_fcu))
            solids.append(box)
    assert len(solids) == 57, f"Expected 57 SMDs from driver_pcb_cpl.csv, got {len(solids)}"
    return solids


def build_assembly_parts(p: LepiLEDParams, core_w_override: float | None = None,
                         glass_id_override: float | None = None, glass_od_override: float | None = None,
                         glass_length_override: float | None = None) -> dict[str, bd.Shape]:
    """Build all Rev 4.5 physical assembly components (incl. ALL 57 SMDs, 90-deg USB-C plug, M20 split gland, SW1)."""
    core_w = core_w_override or p.core_w_nom
    g_id = glass_id_override or p.glass_id_nom
    g_od = glass_od_override or p.glass_od_nom
    g_len = glass_length_override or p.glass_length

    base_ring = build_base_ring(p)
    lid_bot = build_lid_bot(p)
    cap_bot = build_cap_bot(p)
    cap_top = build_cap_top(p)
    plug_top = build_plug_top(p)

    # Horizontal Driver PCB (SMD/JST side DOWN at Z_fcu = 27.0 mm, B.Cu UP at Z = 28.6 mm, centered at Y = +8.0 mm!)
    pcb_board = bd.Box(p.pcb_w, p.pcb_l, p.pcb_thick, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    pcb_board = bd.fillet(pcb_board.edges().filter_by(bd.Axis.Z), p.pcb_corner_r).translate((0.0, p.pcb_y_center, p.pcb_z_fcu))
    for sx in (-1.0, 1.0):
        for sy in (-1.0, 1.0):
            npth = bd.Cylinder(p.pcb_hole_drill / 2.0, p.pcb_thick + 0.6, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER)).translate(
                (sx * p.pcb_hole_x, p.pcb_y_center + sy * p.pcb_hole_y, p.pcb_z_fcu + 0.5 * p.pcb_thick)
            )
            pcb_board = pcb_board - npth

    # All 57 SMDs parsed directly from driver_pcb_cpl.csv + THT J1..J4 + B.Cu TH pin protrusions!
    pcb_parts: list[bd.Shape] = [pcb_board, *_load_all_57_smd_solids(p)]
    j2_hdr = bd.Box(7.4, 5.8, p.pcb_jst_mated_h, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)).translate((-5.2, p.pcb_y_center + 19.2, p.pcb_z_fcu))
    j3_hdr = bd.Box(7.4, 5.8, p.pcb_jst_mated_h, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)).translate((5.2, p.pcb_y_center + 19.2, p.pcb_z_fcu))
    j4_hdr = bd.Box(9.9, 5.8, p.pcb_jst_mated_h, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)).translate((-1.4, p.pcb_y_center - 2.5, p.pcb_z_fcu))
    j1_outer = bd.Box(8.94, 9.17, 3.46, align=(bd.Align.CENTER, bd.Align.MIN, bd.Align.MAX)).translate((0.0, p.y_j1_mouth, p.pcb_z_fcu))
    j1_cav = bd.Box(8.34, p.usbc_mating_depth_mm + 0.05, 2.56, align=(bd.Align.CENTER, bd.Align.MIN, bd.Align.CENTER)).translate((0.0, p.y_j1_mouth - 0.05, p.z_j1_center))
    j1_usbc = j1_outer - j1_cav
    j23_pins = bd.Box(15.0, 2.0, p.pcb_jst_pin_protrude, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0.0, p.pcb_y_center + 19.2, p.z_pcb_bcu))
    j4_pins = bd.Box(7.5, 2.0, p.pcb_jst_pin_protrude, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((-1.4, p.pcb_y_center - 2.5, p.z_pcb_bcu))
    j1_pins = bd.Box(9.6, 5.7, p.pcb_jst_pin_protrude, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0.0, p.pcb_y_center - 19.54, p.z_pcb_bcu))
    pcb_parts.extend([j2_hdr, j3_hdr, j4_hdr, j1_usbc, j23_pins, j4_pins, j1_pins])
    pcb_assy = bd.Compound(pcb_parts)

    # Central protruding bare Al core (30 x 30 x 3.0 mm, L = 200.0 mm stock cut — 175 g!)
    core_out = bd.Box(core_w, core_w, p.core_length, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    core_in = bd.Box(core_w - 2.0 * p.core_wall, core_w - 2.0 * p.core_wall, p.core_length + 2.0,
                     align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, -1.0))
    hs_core = (core_out - core_in).translate((0, 0, p.z_core_bot))
    hang_bore = bd.Cylinder(p.core_hang_hole_dia / 2.0, core_w + 2.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER)).rotate(bd.Axis.Y, 90.0).translate((0.0, 0.0, p.z_hang_hole))
    bot_lock_bore = bd.Cylinder(1.55, core_w + 2.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER)).rotate(bd.Axis.Y, 90.0).translate((0.0, 0.0, p.cap_bot_lock_z))
    top_lock_bore = bd.Cylinder(1.55, core_w + 2.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER)).rotate(bd.Axis.Y, 90.0).translate((0.0, 0.0, p.z_cap_top_lock))
    hs_core = hs_core - hang_bore - bot_lock_bore - top_lock_bore

    # ALL Modeled Fasteners (4x M3x16 lid/ring + 4x M3x10 core locks + 4x M2.5x8 horizontal PCB screws!)
    fasteners_list = []
    # 1. 4x M3x16 SHCS lid + base_ring bolts
    for deg in (45.0, 135.0, 225.0, 315.0):
        rad = math.radians(deg)
        lx, ly = p.lid_bot_bolt_r * math.cos(rad), p.lid_bot_bolt_r * math.sin(rad)
        lb_head = bd.Cylinder(2.75, 3.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)).translate((lx, ly, -p.base_ring_bolt_web - 0.05))
        lb_shank = bd.Cylinder(1.48, 16.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((lx, ly, -p.base_ring_bolt_web - 0.05))
        fasteners_list.append(lb_head.fuse(lb_shank))
    # 2. 4x M3x10 SHCS radial core locking screws (2x cap_bot at Z=54, 2x cap_top at Z=182)
    for z_lk in (p.cap_bot_lock_z, p.z_cap_top_lock):
        for sx in (-1.0, 1.0):
            if sx > 0:
                th = bd.Cylinder(2.75, 3.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).rotate(bd.Axis.Y, 90.0).translate((22.2, 0.0, z_lk))
                ts = bd.Cylinder(1.48, 10.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)).rotate(bd.Axis.Y, 90.0).translate((22.2, 0.0, z_lk))
            else:
                th = bd.Cylinder(2.75, 3.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)).rotate(bd.Axis.Y, 90.0).translate((-22.2, 0.0, z_lk))
                ts = bd.Cylinder(1.48, 10.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).rotate(bd.Axis.Y, 90.0).translate((-22.2, 0.0, z_lk))
            fasteners_list.append(th.fuse(ts))
    # 3. 4x M2.5x8 pan-head PCB mounting screws upward through H1..H4 into bulkhead standoffs
    for sx in (-1.0, 1.0):
        for sy in (-1.0, 1.0):
            hx = sx * p.pcb_hole_x
            hy = p.pcb_y_center + sy * p.pcb_hole_y
            ph = bd.Cylinder(2.25, 1.8, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)).translate((hx, hy, p.pcb_z_fcu - 0.05))
            ps = bd.Cylinder(1.05, 7.5, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((hx, hy, p.pcb_z_fcu - 0.05))
            fasteners_list.append(ph.fuse(ps))
    fasteners_m3 = bd.Compound(fasteners_list)

    # Shatter-resistant Clear Unstabilized Extruded PMMA (Plexiglas XT) shroud (Ø60 x 54 x 3.0 x 115 mm)
    z_g_start = p.z_glass_bot - 0.5 * (g_len - p.glass_length)
    g_outer = bd.Cylinder(g_od / 2.0, g_len, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    g_inner = bd.Cylinder(g_id / 2.0, g_len + 2.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, -1.0))
    glass_tube = (g_outer - g_inner).translate((0, 0, z_g_start))

    # 8x Pre-mounted 20 mm Copper DTP LED stars (4x UV + 4x Vis) + 16x M3 pan screws w/ nylon washers
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

    # Bottom-mounted SW1 (C&K 7211SYZBE gold DPDT) + C&K 759D02000 silicone boot on MECH-LID-BOT at (0.0, +18.5 mm)
    sw_body = bd.Box(p.sw1_body_w_x, p.sw1_body_w_y, p.sw1_body_h_z,
                     align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((p.sw1_x, p.sw1_y, p.sw1_wall_thick + 0.05))
    sw_lugs = bd.Box(10.0, 8.5, p.sw1_lugs_h_z,
                     align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((p.sw1_x, p.sw1_y, p.sw1_wall_thick + 0.05 + p.sw1_body_h_z))
    sw_bush = bd.Cylinder(p.sw1_hole_dia / 2.0 - 0.05, p.sw1_wall_thick + 0.1,
                          align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((p.sw1_x, p.sw1_y, 0.0))
    sw_boot = bd.Cylinder(p.sw1_boot_od / 2.0, p.sw1_boot_protrude_z,
                          align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)).translate((p.sw1_x, p.sw1_y, -0.05))
    sw1_assy = bd.Compound([sw_body, sw_lugs, sw_bush, sw_boot])

    # M20 IP68 split waterproof cable gland seated in MECH-LID-BOT at (0.0, -18.5 mm)
    gl_outer = bd.Cylinder(p.gland_nut_od / 2.0, p.gland_outer_h, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)).translate((p.gland_x, p.gland_y, -0.05))
    gl_neck = bd.Cylinder(p.gland_bore_dia / 2.0 - 0.15, p.lid_bot_thick + 0.1, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((p.gland_x, p.gland_y, -0.05))
    gl_inner = bd.Cylinder(p.gland_nut_od / 2.0, p.gland_inner_h, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((p.gland_x, p.gland_y, p.z_lid_bot_end + 0.05))
    gland_usbc = gl_outer.fuse(gl_neck).fuse(gl_inner)

    # Compact 90-deg-down USB-C PD plug mated full 4.55 mm inside horizontal J1 (cable exits downward to M20 split gland!)
    y_plug_tip = p.y_j1_mouth + p.usbc_mating_depth_mm
    plug_barrel = bd.Box(8.3, p.usbc_mating_depth_mm + 2.0, 2.5, align=(bd.Align.CENTER, bd.Align.MAX, bd.Align.CENTER)).translate((0.0, y_plug_tip, p.z_j1_center))
    plug_body = bd.Box(p.usbc_plug_90_w, p.usbc_plug_90_len - 1.9, p.usbc_plug_90_h,
                       align=(bd.Align.CENTER, bd.Align.MAX, bd.Align.MAX)).translate((0.0, p.y_j1_mouth - 1.9, p.z_j1_center + 2.8))
    usbc_plug_assy = plug_barrel.fuse(plug_body)

    return dict(
        base_ring=base_ring,
        lid_bot=lid_bot,
        cap_bot=cap_bot,
        cap_top=cap_top,
        plug_top=plug_top,
        pcb_assy=pcb_assy,
        hs_core=hs_core,
        fasteners_m3=fasteners_m3,
        glass_tube=glass_tube,
        dtp_stars=dtp_stars,
        sw1_assy=sw1_assy,
        gland_usbc=gland_usbc,
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


def check_kinematic_insertion(lid_bot: bd.Part, cap_bot: bd.Part, pcb_assy: bd.Shape, p: LepiLEDParams) -> dict[str, dict | bool]:
    # 1. Bottom-mounted SW1 vertical insertion straight down into MECH-LID-BOT pocket
    sw_body = bd.Box(p.sw1_body_w_x, p.sw1_body_w_y, p.sw1_body_h_z, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    sw_lugs = bd.Box(10.0, 8.5, p.sw1_lugs_h_z, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0.0, 0.0, p.sw1_body_h_z))
    sw_bush = bd.Cylinder(p.sw1_hole_dia / 2.0 - 0.05, 8.89, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX))
    sw_tool = bd.Compound([sw_body, sw_lugs, sw_bush])
    sw_max_vol = 0.0
    for zw in np.linspace(25.0, p.sw1_wall_thick + 0.05, 15):
        inter = lid_bot & sw_tool.translate((p.sw1_x, p.sw1_y, float(zw)))
        sw_max_vol = max(sw_max_vol, float(inter.volume) if inter is not None else 0.0)

    # 2. Horizontal driver_pcb (all 57 SMDs + J1..J4) straight +Z insertion into MECH-CAP-BOT onto bulkhead standoffs
    pcb_max_vol = 0.0
    for dz in np.linspace(-30.0, 0.0, 15):
        inter = cap_bot & pcb_assy.translate((0.0, 0.0, float(dz)))
        pcb_max_vol = max(pcb_max_vol, float(inter.volume) if inter is not None else 0.0)

    # 3. Pre-crimped 2-pin JST-XH plug (7.4 x 5.75 x 12 mm) straight vertical sweep through both ±Y wire channels!
    jst_plug_tool = bd.Box(7.4, 5.75, 12.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER))
    y_slot_c = p.core_pocket_w / 2.0 + p.core_wire_slot_d / 2.0 - 0.1
    jst_max_vol = 0.0
    for sy in (-1.0, 1.0):
        for zj in np.linspace(p.cap_bot_ceiling_z - 5.0, p.z_glass_bot + 10.0, 15):
            inter = cap_bot & jst_plug_tool.translate((0.0, sy * y_slot_c, float(zj)))
            jst_max_vol = max(jst_max_vol, float(inter.volume) if inter is not None else 0.0)

    # 4. Intact USB-C plug overmold (12.4 x 6.8 x 22 mm) passing straight through M20 split cable gland bore in MECH-LID-BOT!
    plug_pass_tool = bd.Box(12.4, 6.8, 22.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER))
    gland_max_vol = 0.0
    for zp in np.linspace(-20.0, 20.0, 15):
        inter = lid_bot & plug_pass_tool.translate((p.gland_x, p.gland_y, float(zp)))
        gland_max_vol = max(gland_max_vol, float(inter.volume) if inter is not None else 0.0)

    return {
        "sw1_bottom_lid_insertion": {"waypoints_tested": 15, "max_intersection_vol_mm3": round(sw_max_vol, 6), "pass": sw_max_vol < 1e-4},
        "pcb_horiz_standoff_insertion": {"waypoints_tested": 15, "max_intersection_vol_mm3": round(pcb_max_vol, 6), "pass": pcb_max_vol < 1e-4},
        "jst_xh_plug_wire_slot_sweep": {"waypoints_tested": 30, "max_intersection_vol_mm3": round(jst_max_vol, 6), "pass": jst_max_vol < 1e-4},
        "usbc_plug_m20_gland_pass": {"waypoints_tested": 15, "max_intersection_vol_mm3": round(gland_max_vol, 6), "pass": gland_max_vol < 1e-4},
        "all_zero": (sw_max_vol < 1e-4) and (pcb_max_vol < 1e-4) and (jst_max_vol < 1e-4) and (gland_max_vol < 1e-4),
    }


def compute_mass_budget(mesh_checks: dict, assy_nom: dict[str, bd.Shape]) -> dict[str, float]:
    """Compute exact lamp mass budget (g) from B-Rep volumes and stock material densities."""
    lamp_printed_keys = ("mech_base_ring", "mech_lid_bot", "mech_cap_bot", "mech_cap_top", "mech_plug_top")
    vol_printed_cm3 = sum(mesh_checks[k]["brep_volume_mm3"] for k in lamp_printed_keys) / 1000.0
    petg_solid_g = vol_printed_cm3 * 1.27
    petg_fdm_g = vol_printed_cm3 * 1.27 * 0.60  # 4 perimeters + 25% gyroid infill (~60% effective fill)

    al_core_g = (float(assy_nom["hs_core"].volume) / 1000.0) * 2.70
    pmma_shroud_g = (float(assy_nom["glass_tube"].volume) / 1000.0) * 1.18
    elec_stars_hw_g = 115.0  # 8x Cu DTP stars (34 g) + PCB (23 g) + SW1/boot/M20 split gland/O-rings/M3/M2.5 (58 g)

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
    # Clean up deprecated Rev 4.4 mech_plug_bot artifacts if present
    for old_name in ("mech_plug_bot.step", "mech_plug_bot.stl"):
        old_p = out_dir / old_name
        if old_p.exists():
            old_p.unlink()

    p_fdm = LepiLEDParams(process="FDM")
    (out_dir / "cad_params.json").write_text(json.dumps(p_fdm.to_dict(), indent=2))

    assy_nom = build_assembly_parts(p_fdm)
    drill_jig = build_drill_jig(p_fdm)

    # 1. Export all 6 3D-printable FDM STEP & STL files
    mesh_checks = {
        "mech_base_ring": export_and_verify_stl(assy_nom["base_ring"], out_dir / "mech_base_ring.step", out_dir / "mech_base_ring.stl"),
        "mech_lid_bot": export_and_verify_stl(assy_nom["lid_bot"], out_dir / "mech_lid_bot.step", out_dir / "mech_lid_bot.stl"),
        "mech_cap_bot": export_and_verify_stl(assy_nom["cap_bot"], out_dir / "mech_cap_bot.step", out_dir / "mech_cap_bot.stl"),
        "mech_cap_top": export_and_verify_stl(assy_nom["cap_top"], out_dir / "mech_cap_top.step", out_dir / "mech_cap_top.stl"),
        "mech_plug_top": export_and_verify_stl(assy_nom["plug_top"], out_dir / "mech_plug_top.step", out_dir / "mech_plug_top.stl"),
        "mech_drill_jig": export_and_verify_stl(drill_jig, out_dir / "mech_drill_jig.step", out_dir / "mech_drill_jig.stl"),
    }

    # 2. Export individual assembly STLs to gitignored parts_stl/ for PyVista rendering
    comp_dir = out_dir / "parts_stl"
    comp_dir.mkdir(exist_ok=True)
    for old_f in comp_dir.glob("*.stl"):
        old_f.unlink()
    printed_map = ("base_ring", "lid_bot", "cap_bot", "cap_top", "plug_top")
    for name, shp in assy_nom.items():
        if name in printed_map:
            (comp_dir / f"{name}.stl").write_bytes((out_dir / f"mech_{name}.stl").read_bytes())
        else:
            bd.export_stl(shp, str(comp_dir / f"{name}.stl"), tolerance=0.03, angular_tolerance=0.12)

    assy_compound = bd.Compound(list(assy_nom.values()))
    bd.export_step(assy_compound, str(out_dir / "lepiled_assembly.step"))

    # 3. Overhang audits (all 6 printed parts in actual build-plate orientations!)
    overhang_checks = {
        "mech_base_ring": audit_stl_overhangs(out_dir / "mech_base_ring.stl", (0.0, 0.0, -1.0)),
        "mech_lid_bot": audit_stl_overhangs(out_dir / "mech_lid_bot.stl", (0.0, 0.0, 1.0)),
        "mech_cap_bot": audit_stl_overhangs(out_dir / "mech_cap_bot.stl", (0.0, 0.0, -1.0)),
        "mech_cap_top": audit_stl_overhangs(out_dir / "mech_cap_top.stl", (0.0, 0.0, 1.0)),
        "mech_plug_top": audit_stl_overhangs(out_dir / "mech_plug_top.stl", (0.0, 0.0, -1.0)),
        "mech_drill_jig": audit_stl_overhangs(out_dir / "mech_drill_jig.stl", (0.0, 0.0, 1.0)),
    }

    # 4. All-pairs B-Rep intersection verification (Nominal + Worst-Case +2.0 mm XT PMMA shroud!)
    wc_glass_len = p_fdm.glass_length + p_fdm.glass_length_tol
    inter_nom = check_all_pairs_intersections(assy_nom)
    assy_wc = build_assembly_parts(
        p_fdm, core_w_override=p_fdm.core_w_max, glass_id_override=p_fdm.glass_id_min,
        glass_od_override=p_fdm.glass_od_max, glass_length_override=wc_glass_len,
    )
    inter_wc = check_all_pairs_intersections(assy_wc)

    # 5. Kinematic insertion sweeps (SW1, horizontal PCB w/ all 57 SMDs, JST-XH plug through wire slots, USB-C plug through M20 gland)
    kinematic_checks = check_kinematic_insertion(assy_nom["lid_bot"], assy_nom["cap_bot"], assy_nom["pcb_assy"], p_fdm)

    # 6. Exact mass budget
    mass_budget = compute_mass_budget(mesh_checks, assy_nom)

    all_meshes_ok = all(m["is_watertight"] and m["is_winding_consistent"] and m["stl_volume_mm3"] > 0 for m in mesh_checks.values())
    all_overhangs_ok = all(o["pass"] for o in overhang_checks.values())
    all_brep_ok = inter_nom["all_zero"] and inter_wc["all_zero"]
    all_kinematic_ok = kinematic_checks["all_zero"]
    all_param_checks_ok = all(c["pass"] for c in p_fdm.verify_all().values())

    report = {
        "revision": "Rev 4.5 (Compact 30x30x3 Core + XT PMMA + Horizontal PCB + Radial O-Rings + M20 Split Gland + 15-deg Rain Roof)",
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

    print("=== Mesh Verification (6 FDM Printable Parts — MECH-PLUG-BOT Eliminated) ===")
    for name, m in mesh_checks.items():
        print(f"  {name:16s}: vol={m['stl_volume_mm3']:8.1f} mm^3 | tri={m['triangles']:6d} | wt={m['is_watertight']} | wind={m['is_winding_consistent']} | euler={m['euler_number']:3d}")
    print("=== Overhang Verification ===")
    for name, o in overhang_checks.items():
        print(f"  {name:16s}: >46deg faces={o['off_bed_overhang_gt46_faces']:4d}, area={o['off_bed_overhang_gt46_area_mm2']:6.3f} mm^2, max={o['max_off_bed_overhang_deg']:5.2f} deg | pass={o['pass']}")
    print("=== Kinematic Insertion (SW1, Horizontal PCB w/ 57 SMDs, JST-XH Wire Slots, M20 Split Gland) ===")
    for k in ("sw1_bottom_lid_insertion", "pcb_horiz_standoff_insertion", "jst_xh_plug_wire_slot_sweep", "usbc_plug_m20_gland_pass"):
        v = kinematic_checks[k]
        print(f"  {k:30s}: waypoints={v['waypoints_tested']:2d}, max_vol={v['max_intersection_vol_mm3']:.6f} mm^3 | pass={v['pass']}")
    print("=== All-Pairs B-Rep Intersection (incl. ALL 57 SMDs, 90-deg USB-C, M20 Gland, SW1 & ALL Fasteners) ===")
    for label, d in [("NOMINAL", inter_nom), ("WORST_CASE", inter_wc)]:
        print(f"  {label:10s}: {d['total_pairs_checked']} pairs, nonzero={d['nonzero_count']} {d['nonzero_pairs']}")
    print("=== Verified Mass Budget (Rev 4.5) ===")
    print(f"  Printed lamp parts ({mass_budget['printed_lamp_volume_cm3']} cm^3; cap_bot={mass_budget['cap_bot_volume_cm3']}, cap_top={mass_budget['cap_top_volume_cm3']} cm^3): {mass_budget['petg_fdm_60pct_g']} g FDM (60%) / {mass_budget['petg_solid_100pct_g']} g solid")
    print(f"  Al core (30x30x3x200): {mass_budget['al_core_3mm_g']} g | XT PMMA shroud (60x54x115): {mass_budget['uvt_pmma_shroud_g']} g | Elec+Stars+HW: {mass_budget['elec_stars_hardware_g']} g")
    print(f"  TOTAL LAMP WEIGHT (FDM): {mass_budget['total_fdm_g']} g ({mass_budget['total_solid_g']} g 100% solid) | HEIGHT: {p_fdm.total_height_mm} mm")

    if not report["summary"]["overall_pass"]:
        raise SystemExit(1)
    print(f"Wrote {verif_path} and all Rev 4.5 STEP/STL artifacts (ALL CHECKS PASS).")


if __name__ == "__main__":
    main()
