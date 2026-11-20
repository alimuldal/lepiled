#!/usr/bin/env python3
"""
Parametric 3D CAD Generator for LepiLED DIY Maxi Switch (Rev 4.8 — "Field Lantern") using build123d.

Rev 4.8 Highlights & Automated Regression Gates:
  - Exports 8 watertight, 100% support-free PETG/ASA-agnostic FDM parts (STEP + STL).
  - Lid-mounted horizontal driver_pcb (SMD/JST-side UP!) on 4x M2.5 brass-insert standoffs
    inside an unobstructed Ø71.6 mm bore — open-air USB-C & JST mating, zero blind reach!
  - MECH-CAP-TOP adds a 9.5 mm vertical collar above the 25-deg lofted roof (0 roof holes!).
  - MECH-CORE-ANCHOR staggers vertical ±Y bolts & horizontal ±X cross-pins (0 insert clash!).
  - MECH-CABLE-CLAMP uses blind M3 inserts (1.8 mm solid roof) + 45-deg conical radial squeeze.
  - Hard automated gates:
      1. Watertight manifold + Euler/winding check on all 8 STLs
      2. Overhang <= 46 deg check in real build-plate print orientations
      3. Positive fastener-seat bearing & 4-wall intact core-socket check
      4. Exterior-to-interior ray-cast breach check on sealed shells (cap_top, cap_bot, lid_bot)
      5. All-pairs B-Rep intersection check (Nominal + Worst-Case) INCLUDING all 14 modeled brass
         inserts, exact full-length BOM screws, realistic 15 mm 90-deg USB-C plug + strain relief,
         and all 48 populated SMDs read directly from driver_pcb.kicad_pcb (zero rotation offsets!)
      6. Kinematic insertion sweeps (SW1, ENTIRE lid+PCB+mated-90-deg-USB-C plug straight up, JST slots!)
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from pathlib import Path

import build123d as bd
import numpy as np
import trimesh

from params import LepiLEDParams


# Accurate SMD package 3D bounding boxes (length_x, width_y, height_z) in mm for Rev 4.8 populated SMDs
SMD_PACKAGE_DIMS: dict[str, tuple[float, float, float]] = {
    "U1": (3.0, 2.8, 1.0), "U2": (3.0, 2.8, 1.0),
    "U3": (6.9, 4.9, 1.75),
    "U4": (6.9, 4.9, 1.75),
    "U5": (3.0, 2.5, 1.12),
    "Q2": (3.0, 2.5, 1.12), "Q3": (3.0, 2.5, 1.12),
    "F1": (3.4, 1.8, 0.85),        # Rev 4.8: Littelfuse 046801.5NRHF 1206 Slo-Blo fuse
    "D9": (4.6, 2.8, 2.30), "D10": (4.6, 2.8, 2.30),
    "D11": (4.7, 3.8, 2.44),
    "D12": (1.7, 0.9, 0.80),
    "D15": (3.0, 2.5, 1.12), "D16": (3.0, 2.5, 1.12),
    "L1": (6.1, 6.1, 4.50), "L2": (6.1, 6.1, 4.50),
    "R3": (3.3, 1.7, 0.70), "R4": (3.3, 1.7, 0.70),
    "R7": (6.5, 3.3, 0.75),        # Rev 4.8: UNI-ROYAL 2512 1.0 W pulse damper resistor!
    "R10": (2.1, 1.3, 0.65), "R13": (2.1, 1.3, 0.65), "R14": (2.1, 1.3, 0.65),
    "R22": (2.1, 1.3, 0.65), "R23": (2.1, 1.3, 0.65), "R24": (2.1, 1.3, 0.65),
    "C2": (2.1, 1.3, 1.40), "C3": (2.1, 1.3, 1.40), "C11": (2.1, 1.3, 1.40),
    "C10": (3.3, 1.7, 1.80),
}


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


def _teardrop_profile_wire(radius: float, angle_deg: float = 42.0) -> bd.Face:
    """Create a horizontal-hole teardrop Face in XY plane with +Y apex (both arc & roof <= angle_deg overhang!)."""
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


def _pitched_arch_profile(width: float, rect_h: float, roof_angle_deg: float = 45.0) -> bd.Face:
    """Centered-X, bottom-Y=0 portal opening topped with a clean 45-deg pitched arch (0 overhang inverted!)."""
    hw = width / 2.0
    roof_h = hw * math.tan(math.radians(roof_angle_deg))
    with bd.BuildSketch() as sk:
        with bd.BuildLine():
            bd.Polyline([
                (-hw, 0.0), (hw, 0.0), (hw, rect_h),
                (0.0, rect_h + roof_h), (-hw, rect_h), (-hw, 0.0),
            ])
        bd.make_face()
    return sk.face()


def _radial_bore_oring_cut(r_bore: float, r_groove: float, z_flat: float, flat_w: float, ramp_dir: float) -> bd.Part:
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


def build_lid_bot(p: LepiLEDParams) -> bd.Part:
    """
    Build Rev 4.8 MECH-LID-BOT (Z = 22.0 .. 29.0 mm + 7.0 mm spigot + 4x integral M2.5 PCB standoffs!):
      - 7.0 mm thick recessed Ø85.6 mm floor allowing BLIND 5.2 mm M3 clamp inserts (1.8 mm solid dry-bay roof!)
      - Ø70.8 mm radial O-ring spigot (68 x 2.5 mm VMQ70) w/ 4x integral M2.5 brass-insert PCB standoffs rising
        to Z = 45.5 mm so driver_pcb mounts SMD/JST-Side UP in open air on the bench!
      - 16.5 x 14.5 mm stadium USB-C port at (0, -20.5) w/ 45-deg lower conical seat driving radial clamp squeeze!
      - SW1 Ø6.35 mm bore + 12.70(X)x11.43(Y) anti-rotation pocket at (0, +15.0 mm) aligned with toggle throw!
      - Ø2.5 mm breather vent bore + ACTUALLY CUT Ø9.5 x 0.8 mm recessed protective pocket on sheltered INSIDE face!
      - ZERO D12 lightpipe hole (D12 is visible directly on top of PCB during bench testing; one fewer leak path!)
      - Prints flat upright on Z = 22.0 mm with 0.000 mm^2 >46 deg overhang!
    """
    z0 = p.z_lid_bot_start    # 22.0
    z1 = p.z_lid_bot_end      # 29.0
    r_lid = p.lid_bot_od / 2.0
    base = bd.Cylinder(r_lid, p.lid_bot_thick, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, z0))

    # Hollow radial O-ring sealing spigot (Z = 29.0 .. 36.0 mm)
    r_sp_out = p.lid_spigot_od / 2.0
    r_sp_in = p.lid_spigot_id / 2.0
    spigot = (
        bd.Cylinder(r_sp_out, p.lid_spigot_h, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
        - bd.Cylinder(r_sp_in, p.lid_spigot_h + 1.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    ).translate((0.0, 0.0, z1))
    part = base.fuse(spigot)

    # Top lead-in chamfer on spigot for smooth O-ring assembly
    sp_top = part.edges().filter_by(bd.GeomType.CIRCLE).filter_by_position(bd.Axis.Z, z1 + p.lid_spigot_h - 0.1, z1 + p.lid_spigot_h + 0.1)
    outer_sp_top = [e for e in sp_top if e.radius > r_sp_out - 0.5]
    if outer_sp_top:
        part = bd.chamfer(outer_sp_top, length=0.6)

    # 4x integral M2.5 brass-insert PCB standoffs rising UP from Z=29.0 to Z=45.5 mm (0 overhang upright!)
    # H1/H2 at (±14.0, +26.0, R=29.53) buttress cleanly into the inner spigot wall while staying inside groove root R=33.65!
    st_h = p.pcb_z_bcu - z1  # 16.5 mm
    r_st_body = p.pcb_standoff_body_od / 2.0  # 3.20 mm (1.55 mm wall around Ø3.3 mm M2.5 insert!)
    r_st_tip = p.pcb_standoff_tip_od / 2.0    # 2.75 mm (matches Ø5.5 mm H1..H4 copper keepout!)
    taper_h = 1.5
    inner_clip = bd.Cylinder(p.bot_oring_groove_od / 2.0 - 0.5, st_h + 2.0,
                             align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0.0, 0.0, z1 - 0.5))
    for sx in (-1.0, 1.0):
        for sy in (-1.0, 1.0):
            hx = sx * p.pcb_hole_x
            hy = p.pcb_y_center + sy * p.pcb_hole_y
            st_lower = bd.Cylinder(r_st_body, st_h - taper_h, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((hx, hy, z1))
            st_upper = bd.Cone(r_st_body, r_st_tip, taper_h, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((hx, hy, p.pcb_z_bcu - taper_h))
            # Clip outer perimeter strictly inside O-ring groove root R=33.15 so spigot O-ring groove is 100% untouched!
            st_full = st_lower.fuse(st_upper) & inner_clip
            part = part.fuse(st_full)

    # Cut radial O-ring groove AFTER standoffs so groove is mathematically exact (MECH-GASKET-3: 68 x 2.5 mm VMQ70)
    g3 = _radial_spigot_oring_cut(r_sp_out, p.bot_oring_groove_od / 2.0, z1 + 1.4, p.bot_oring_flat_w)
    part = part - g3

    # Cut 4x blind M3x5.0 brass heat-set insert pilot bores in standoff tops (Z = 40.5 .. 46.5 mm — unified M3!)
    for sx in (-1.0, 1.0):
        for sy in (-1.0, 1.0):
            hx = sx * p.pcb_hole_x
            hy = p.pcb_y_center + sy * p.pcb_hole_y
            pilot = bd.Cylinder(p.m3_insert_pilot_dia / 2.0, p.m3_insert_depth + 0.2,
                                align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)).translate((hx, hy, p.pcb_z_bcu + 0.2))
            part = part - pilot

    # 4x M3 flush 90-deg countersunk lid mounting holes at R = 40.2 mm (exact 45-deg upright -> 0 overhang!)
    for deg in (45.0, 135.0, 225.0, 315.0):
        rad = math.radians(deg)
        hx, hy = p.lid_bot_bolt_r * math.cos(rad), p.lid_bot_bolt_r * math.sin(rad)
        c_thru = bd.Cylinder(p.m3_clearance_dia / 2.0, p.lid_bot_thick + 2.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((hx, hy, z0 - 1.0))
        c_csk = bd.Cone(3.25, p.m3_clearance_dia / 2.0, 3.25 - p.m3_clearance_dia / 2.0,
                        align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((hx, hy, z0 - 0.05))
        part = part - c_thru - c_csk

    # 16.5 x 14.5 mm stadium USB-C plug pass-through port + 45-deg lower conical radial-compression seat (Z = 22.0..25.0)!
    # Note: wider at Z=22.0 (bottom) tapering inward to Z=25.0 -> 45-deg overhang upright? Check:
    # Upright prints Z=22 -> 25 -> 29! As Z increases, the hole NARROWS inward by 3.0 mm at 45 deg = EXACT 45-deg roof = 0 overhang!
    with bd.BuildSketch(bd.Plane.XY.offset(z0 - 0.5)) as sk_port_top:
        bd.RectangleRounded(p.clamp_port_w, p.clamp_port_l, radius=3.0)
    port_straight = bd.extrude(sk_port_top.sketch, p.lid_bot_thick + 1.5).translate((p.clamp_x, p.clamp_y, 0.0))

    cone_h = 3.0
    with bd.BuildSketch(bd.Plane.XY.offset(z0 - 0.1)) as sk_cone_bot:
        bd.RectangleRounded(p.clamp_port_w + 2.0 * cone_h, p.clamp_port_l + 2.0 * cone_h, radius=4.0)
    with bd.BuildSketch(bd.Plane.XY.offset(z0 + cone_h)) as sk_cone_top:
        bd.RectangleRounded(p.clamp_port_w, p.clamp_port_l, radius=3.0)
    port_cone = bd.loft([sk_cone_bot.sketch, sk_cone_top.sketch]).translate((p.clamp_x, p.clamp_y, 0.0))
    part = part - port_straight - port_cone

    # P0-5 FIXED: 2x BLIND std workshop M3x5.0 brass heat-set insert pockets in 8.5 mm lid (Z = 22.0 .. 29.0 mm -> 1.5 mm SOLID ROOF!)
    # 5.1 mm straight Ø4.0 mm pilot bore + matched 45-deg cone (r=2.0 -> 0.10 over 1.90 mm -> watertight & 0.06 mm^2 tip!)
    r_pil = p.m3_insert_pilot_dia / 2.0  # 2.0 mm
    for sx in (-1.0, 1.0):
        cb_straight = bd.Cylinder(r_pil, 5.2,
                                  align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((sx * p.clamp_bolt_dx, p.clamp_y, z0 - 0.1))
        cb_cone = bd.Cone(r_pil, 0.10, r_pil - 0.10,
                          align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((sx * p.clamp_bolt_dx, p.clamp_y, z0 + 5.1))
        part = part - cb_straight.fuse(cb_cone)

    # Bottom-mounted SW1 vertical Ø6.35 mm bore + 4.5 mm upper anti-rotation pocket (12.70(X) x 11.43(Y) aligned w/ throw!)
    sw_bore = bd.Cylinder(p.sw1_hole_dia / 2.0 + p.print_clearance * 0.5, p.lid_bot_thick + 2.0,
                          align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((p.sw1_x, p.sw1_y, z0 - 1.0))
    sw_recess = bd.Box(p.sw1_body_w_x + 0.8, p.sw1_body_w_y + 0.8, p.lid_bot_thick - p.sw1_wall_thick + 0.5,
                       align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((p.sw1_x, p.sw1_y, z0 + p.sw1_wall_thick))
    part = part - sw_bore - sw_recess

    # Pressure-equalization IP68 ePTFE breather vent bore + ACTUALLY CUT Ø9.5 x 0.8 mm recessed pocket on sheltered INSIDE face!
    vent_bore = bd.Cylinder(p.vent_hole_dia / 2.0, p.lid_bot_thick + 2.0,
                            align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((p.vent_x, p.vent_y, z0 - 1.0))
    vent_pocket = bd.Cylinder(p.vent_pocket_dia / 2.0, p.vent_pocket_depth + 0.2,
                              align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)).translate((p.vent_x, p.vent_y, z1 + 0.2))
    part = part - vent_bore - vent_pocket

    return part


def build_cable_clamp_half(p: LepiLEDParams, side: float = 1.0) -> bd.Part:
    """
    Build one half of Rev 4.8 MECH-CABLE-CLAMP (2x identical mirrored halves bolting into BLIND M3 inserts):
      - Matching 45-deg external conical wedge engages MECH-LID-BOT's tapered port seat, converting vertical
        M3x12 bolt force into genuine RADIAL inward clamping compression around a slit silicone cable sleeve!
      - 0 mm protrusion above lid top (Z=29.0 mm); prints UPRIGHT flat on Z=13.0 mm with 0.000 mm^2 overhang!
    """
    z_lid = p.z_lid_bot_start  # 22.0
    cone_h = 3.0
    # Upper straight key + 45-deg tapered wedge matching MECH-LID-BOT conical seat (0.4 mm slip clearance)
    with bd.BuildSketch(bd.Plane.XY.offset(z_lid + cone_h)) as sk_plug_top:
        bd.RectangleRounded(p.clamp_port_w - 1.0, p.clamp_port_l - 1.0, radius=2.6)
    plug_upper = bd.extrude(sk_plug_top.sketch, p.lid_bot_thick - cone_h - 0.5)  # Z = 25.0 .. 28.5 mm

    with bd.BuildSketch(bd.Plane.XY.offset(z_lid)) as sk_wedge_bot:
        bd.RectangleRounded(p.clamp_port_w + 2.0 * cone_h - 1.0, p.clamp_port_l + 2.0 * cone_h - 1.0, radius=3.6)
    with bd.BuildSketch(bd.Plane.XY.offset(z_lid + cone_h)) as sk_wedge_top:
        bd.RectangleRounded(p.clamp_port_w - 1.0, p.clamp_port_l - 1.0, radius=2.6)
    plug_wedge = bd.loft([sk_wedge_bot.sketch, sk_wedge_top.sketch])

    with bd.BuildSketch(bd.Plane.XY.offset(z_lid - p.clamp_outer_h)) as sk_flange:
        bd.RectangleRounded(34.0, 20.0, radius=4.0)
    flange = bd.extrude(sk_flange.sketch, p.clamp_outer_h)  # Z = 13.0 .. 22.0 mm
    full = flange.fuse(plug_wedge).fuse(plug_upper)

    # Central Ø4.6 mm cable bore + 45-deg self-supporting Ø8.0 mm slit-silicone sleeve chamber (0 overhang upright!)
    r_cab = p.clamp_cable_dia / 2.0 + 0.1  # 2.35
    r_grom = 4.0
    c_cable = bd.Cylinder(r_cab, p.clamp_outer_h + p.lid_bot_thick + 2.0,
                          align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, z_lid - p.clamp_outer_h - 1.0))
    c_grom_bot = bd.Cone(r_cab, r_grom, r_grom - r_cab, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, z_lid - 7.0))
    c_grom_mid = bd.Cylinder(r_grom, 3.4, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, z_lid - 7.0 + (r_grom - r_cab)))
    c_grom_top = bd.Cone(r_grom, r_cab, r_grom - r_cab, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, z_lid - 3.6 + (r_grom - r_cab)))
    c_top_fl = bd.Cone(r_cab, 4.2, 2.5, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, z_lid + p.lid_bot_thick - 2.9))
    full = full - c_cable - c_grom_bot - c_grom_mid - c_grom_top - c_top_fl

    # 2x flush 90-deg countersunk M3 clearance bores at X = ±13.0 mm (M3x12 CSK sits flush at Z=13.0 -> 13.0 mm ground clr!)
    for sx in (-1.0, 1.0):
        b_thru = bd.Cylinder(p.m3_clearance_dia / 2.0, p.clamp_outer_h + 2.0,
                             align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((sx * p.clamp_bolt_dx, 0.0, z_lid - p.clamp_outer_h - 1.0))
        b_csk = bd.Cone(3.25, p.m3_clearance_dia / 2.0, 3.25 - p.m3_clearance_dia / 2.0,
                        align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((sx * p.clamp_bolt_dx, 0.0, z_lid - p.clamp_outer_h - 0.05))
        full = full - b_thru - b_csk

    gap = 0.30
    if side > 0:
        half_mask = bd.Box(44.0, 44.0, 44.0, align=(bd.Align.MIN, bd.Align.CENTER, bd.Align.CENTER)).translate((gap, 0.0, z_lid))
    else:
        half_mask = bd.Box(44.0, 44.0, 44.0, align=(bd.Align.MAX, bd.Align.CENTER, bd.Align.CENTER)).translate((-gap, 0.0, z_lid))
    return (full & half_mask).translate((p.clamp_x, p.clamp_y, 0.0))


def build_core_anchor(p: LepiLEDParams) -> bd.Part:
    """
    Build Rev 4.8 MECH-CORE-ANCHOR (P0-2 FIXED — 90-deg orthogonal + 4.4 mm vertical stagger -> ZERO clash!):
      - 23.4 x 23.4 x 19.0 mm internal core lock block seating flat at Z = 68.0 mm
      - 2x vertical M3 brass insert bores on ±Y at (0.0, ±6.5 mm, Z = 68.0 .. 75.5 mm)
      - 2x horizontal cross-pin M3 brass insert bores on ±X at Z = 81.0 mm (Z_rel = 13.0 mm)
      - Prints inverted on flat top face Z = 87.0 mm with 0.000 mm^2 >46 deg overhang!
    """
    part = bd.Box(p.anchor_w, p.anchor_w, p.anchor_h_in_core,
                  align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, p.z_core_bot))
    part = bd.fillet(part.edges().filter_by(bd.Axis.Z), 1.2)

    # 2x vertical M3 brass heat-set insert bores on ±Y at (0.0, ±6.5 mm) facing -Z (Z = 68.0 .. 75.0 mm)
    # Top with 45-deg self-supporting cone so inverted print (Z decreasing) has 0.000 mm^2 overhang!
    for sy in (-1.0, 1.0):
        ins = bd.Cylinder(p.m3_insert_pilot_dia / 2.0, 6.2,
                          align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0.0, sy * p.anchor_bolt_y, p.z_core_bot - 0.2))
        ins_cone = bd.Cone(p.m3_insert_pilot_dia / 2.0, 0.3, 1.7,
                           align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0.0, sy * p.anchor_bolt_y, p.z_core_bot + 6.0))
        part = part - ins - ins_cone

    # Horizontal cross-pin Ø4.0 mm brass insert bores on ±X at Z = 81.0 mm (teardrop apex toward -Z when printed inverted!)
    td_pin = _teardrop_profile_wire(p.m3_insert_pilot_dia / 2.0, 42.0)
    pin_bore = bd.extrude(td_pin, p.anchor_w + 2.0).rotate(bd.Axis.X, -90.0).rotate(bd.Axis.Z, -90.0).translate((-p.anchor_w / 2.0 - 1.0, 0.0, p.z_anchor_pin))
    part = part - pin_bore

    return part


def build_cap_bot(p: LepiLEDParams) -> bd.Part:
    """
    Build Rev 4.8 MECH-CAP-BOT (prints INVERTED on Z = 88.5 mm with 0 unsupported exterior overhang!):
      - Cylindrical Ø92.4 mm base (Z = 0..36 mm) transitioning smoothly via 9.8-deg frustum to Ø74.0 mm collar (Z = 88.5)
      - Deepened 22.0 mm integral skirt recessing MECH-LID-BOT + REAL 18.6 mm SW1 boot (3.4 mm clear!)
      - Intact tactile 0/1/2 switch index ribs at Z = 13.0..19.5 mm (ABOVE the 11 mm +Y portal arch!)
      - Unobstructed straight Ø71.6 mm bore from lid spigot to Z = 62.5 mm ceiling (effortless lid+PCB insertion!)
      - 2x internal vertical M3x12 anchor bores on ±Y at (0.0, ±6.5 mm) through 5.5 mm bulkhead (ZERO side holes!)
      - PETG/ASA-agnostic 31.1 x 31.1 mm core socket inside solid R = 24.5 mm central hub + 60x3.5 VMQ50 O-ring
    """
    r_base = p.cap_bot_base_od / 2.0    # 46.2
    r_col = p.cap_bot_collar_od / 2.0   # 37.0
    z_tap = p.cap_bot_taper_start_z     # 36.0
    z_top = p.z_cap_bot_top             # 88.5

    lower_cyl = bd.Cylinder(r_base, z_tap, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    upper_cone = bd.Cone(r_base, r_col, z_top - z_tap, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, z_tap))
    part = lower_cyl.fuse(upper_cone)

    bot_edges = part.edges().filter_by(bd.GeomType.CIRCLE).filter_by_position(bd.Axis.Z, -0.1, 0.1)
    part = bd.chamfer(bot_edges, length=p.cap_chamfer)

    # Tactile midnight switch index ribs on outer +Y wall at Z = 13.0 .. 19.5 mm (100% ABOVE 11 mm portal arch!)
    for x_rib in (0.0, 5.5, 8.5):
        y_outer = math.sqrt(max(1.0, r_base ** 2 - x_rib ** 2))
        with bd.BuildSketch(bd.Plane.YZ.offset(x_rib - 0.7)) as sk_rib:
            with bd.BuildLine():
                bd.Polyline([
                    (y_outer - 2.0, 13.0),
                    (y_outer + 0.9, 13.0),
                    (y_outer + 0.9, 18.0),
                    (y_outer - 2.0, 20.9),  # Exact 45-deg ramp facing +Z (print-DOWN inverted -> 0 overhang!)
                    (y_outer - 2.0, 13.0),
                ])
            bd.make_face()
        part = part.fuse(bd.extrude(sk_rib.sketch, 1.4))

    # Integral recessed skirt + lid pocket (Ø86.2 mm, Z = 0.0 .. 29.0 mm -> upward-facing shelf when printed inverted!)
    skirt_and_lid = bd.Cylinder(p.cap_bot_skirt_id / 2.0, p.z_lid_bot_end + 0.1,
                                align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, -0.1))
    part = part - skirt_and_lid

    # 2x opposing smooth 45-deg-arch cable/drainage portals at ±Y (Z = 0.0 .. 11.0 mm; 0 overhang inverted!)
    arch_prof = _pitched_arch_profile(p.cap_bot_portal_w, p.cap_bot_portal_rect_h, 45.0)
    for sy in (-1.0, 1.0):
        portal = bd.extrude(arch_prof, 24.0).rotate(bd.Axis.X, 90.0).translate((0.0, (54.0 if sy > 0 else -30.0), -0.2))
        part = part - portal

    # Straight unobstructed Ø71.6 mm bore from Z = 29.0 mm all the way to Z = 62.5 mm ceiling!
    r_cav = p.cap_bot_cavity_dia / 2.0  # 35.8
    cav_main = bd.Cylinder(r_cav, p.cap_bot_ceiling_z - p.z_lid_bot_end + 0.5,
                           align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, p.z_lid_bot_end - 0.5))
    part = part - cav_main

    # 4x blind M3 brass heat-set insert bores at R = 40.2 mm (Z = 29.0 .. 35.0 mm; 45-deg cone tip -> 0 overhang!)
    for deg in (45.0, 135.0, 225.0, 315.0):
        rad = math.radians(deg)
        ix, iy = p.lid_bot_bolt_r * math.cos(rad), p.lid_bot_bolt_r * math.sin(rad)
        ins_bore = bd.Cylinder(p.m3_insert_pilot_dia / 2.0, p.m3_insert_depth + 0.2,
                               align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((ix, iy, p.z_lid_bot_end - 0.2))
        part = part - ins_bore

    # Annular shroud bore (Ø61.6 x Ø49.0 mm, Z = 72.8 .. 88.5 mm) around FULL-HEIGHT solid R = 24.5 mm central hub!
    r_bore = p.glass_bore_id / 2.0  # 30.8
    r_hub = p.core_hub_od / 2.0     # 24.5
    z_bore_bot = p.z_glass_bot - 1.2  # 72.8
    shroud_annulus = (
        bd.Cylinder(r_bore, z_top - z_bore_bot + 0.5, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
        - bd.Cylinder(r_hub, z_top - z_bore_bot + 1.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, -0.2))
    ).translate((0, 0, z_bore_bot))
    cone_h = r_bore - r_hub  # 6.3 mm -> Z = 66.5 .. 72.8 mm (4.0 mm above Z=62.5 ceiling!)
    shroud_seat_cone = (
        bd.Cone(r_hub, r_bore, cone_h, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX))
        - bd.Cylinder(r_hub, cone_h + 0.4, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)).translate((0, 0, 0.2))
    ).translate((0, 0, z_bore_bot))
    g1 = _radial_bore_oring_cut(r_bore, p.glass_oring_groove_od / 2.0, z_top - 4.0, p.glass_oring_flat_w, ramp_dir=-1.0)
    mouth_lead = (
        bd.Cone(r_bore, r_bore + 0.7, 1.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX))
        - bd.Cylinder(r_hub + 0.5, 1.4, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)).translate((0, 0, 0.2))
    ).translate((0, 0, z_top + 0.1))
    part = part - shroud_annulus - shroud_seat_cone - g1 - mouth_lead

    # Intact 20.5 mm-deep PETG/ASA-agnostic 31.1 x 31.1 mm square core socket (Z = 68.0 .. 88.5 mm)
    core_sock = bd.Box(p.core_pocket_w, p.core_pocket_w, z_top - p.z_core_bot + 1.0,
                       align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, p.z_core_bot))
    part = part - core_sock

    # P0-2 FIXED: 2x internal vertical flush M3x12 CSK dry-bay anchor bores on ±Y at (0.0, ±6.5 mm) through 5.5 mm bulkhead!
    for sy in (-1.0, 1.0):
        anc_bore = bd.Cylinder(p.m3_clearance_dia / 2.0, p.bulkhead_thick + 2.0,
                               align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0.0, sy * p.anchor_bolt_y, p.cap_bot_ceiling_z - 0.5))
        anc_csk = bd.Cone(3.25, p.m3_clearance_dia / 2.0, 3.25 - p.m3_clearance_dia / 2.0,
                          align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0.0, sy * p.anchor_bolt_y, p.cap_bot_ceiling_z - 0.05))
        part = part - anc_bore - anc_csk

    # 2x generous 9.0 x 7.5 mm wire channels at ±Y passing pre-crimped 7.4 x 5.75 mm JST-XH plugs straight through!
    y_slot_c = p.core_pocket_w / 2.0 + p.core_wire_slot_d / 2.0 - 0.1  # 19.20 mm
    for sy in (-1.0, 1.0):
        wslot = bd.Box(p.core_wire_slot_w, p.core_wire_slot_d + 0.2, (z_top + 1.0) - (p.cap_bot_ceiling_z - 1.0),
                       align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0.0, sy * y_slot_c, p.cap_bot_ceiling_z - 1.0))
        part = part - wslot

    return part


def build_cap_top(p: LepiLEDParams) -> bd.Part:
    """
    Build Rev 4.8 MECH-CAP-TOP (P0-1 FIXED — ZERO roof holes, ZERO silicone-groove breach, 0.000 mm^2 overhang!):
      - Unbroken Ø84 mm circular rain eaves lofted smoothly into a 40.4 x 40.4 mm (R=4 mm) vertical chimney collar!
      - 9.5 mm vertical collar (Z = 200.0 .. 209.5 mm) gives 4.65 mm SOLID flat clamping walls for 2x M3x10 SHCS
        at Z = 203.3 mm — 5.0 mm ABOVE internal shroud cone apex (196.5 mm) and 1.25 mm BELOW top silicone groove!
    """
    r_skirt = p.cap_top_skirt_od / 2.0    # 37.0
    r_brim = p.cap_top_brim_od / 2.0      # 42.0
    z_bot = p.z_cap_top_bot               # 174.5
    z_fl_bot = p.z_cap_top_brim_bot       # 182.5
    z_rim_bot = p.z_cap_top_brim_rim_bot  # 187.5
    z_rim_top = p.z_cap_top_brim_rim_top  # 190.0
    z_col_bot = p.z_cap_top_collar_bot    # 200.0
    z_top = p.z_cap_top_top               # 209.5

    c_skirt = bd.Cylinder(r_skirt, z_fl_bot - z_bot, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, z_bot))
    c_flare = bd.Cone(r_skirt, r_brim, z_rim_bot - z_fl_bot, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, z_fl_bot))
    c_rim = bd.Cylinder(r_brim, z_rim_top - z_rim_bot, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, z_rim_bot))

    with bd.BuildSketch(bd.Plane.XY.offset(z_rim_top)) as sk_roof_bot:
        bd.Circle(r_brim)
    with bd.BuildSketch(bd.Plane.XY.offset(z_col_bot)) as sk_roof_top:
        bd.RectangleRounded(p.cap_top_collar_w, p.cap_top_collar_w, radius=p.cap_top_collar_r)
    c_roof = bd.loft([sk_roof_bot.sketch, sk_roof_top.sketch])

    # 9.5 mm solid vertical rounded-square chimney collar above the rain roof!
    with bd.BuildSketch(bd.Plane.XY.offset(z_col_bot)) as sk_col:
        bd.RectangleRounded(p.cap_top_collar_w, p.cap_top_collar_w, radius=p.cap_top_collar_r)
    c_collar = bd.extrude(sk_col.sketch, p.cap_top_collar_h)

    part = c_skirt.fuse(c_flare).fuse(c_rim).fuse(c_roof).fuse(c_collar)

    rim_edges = part.edges().filter_by(bd.GeomType.CIRCLE).filter_by_position(bd.Axis.Z, z_rim_bot - 0.1, z_rim_bot + 0.1)
    part = bd.chamfer(rim_edges, length=0.6)

    # Annular shroud bore (Ø61.6 x Ø49.0 mm) around FULL-HEIGHT solid R = 24.5 mm central hub!
    r_bore = p.glass_bore_id / 2.0  # 30.8
    r_hub = p.core_hub_od / 2.0     # 24.5
    z_bore_top = p.z_glass_top + 1.2  # 190.2
    shroud_annulus = (
        bd.Cylinder(r_bore, z_bore_top - z_bot + 0.5, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
        - bd.Cylinder(r_hub, z_bore_top - z_bot + 1.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, -0.2))
    ).translate((0, 0, z_bot - 0.5))
    cone_h = r_bore - r_hub  # 6.3 mm -> ends at Z = 196.5 mm (5.0+ mm BELOW lock bore bottom!)
    shroud_stop = (
        bd.Cone(r_bore, r_hub, cone_h, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
        - bd.Cylinder(r_hub, cone_h + 0.4, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, -0.2))
    ).translate((0, 0, z_bore_top))
    g2 = _radial_bore_oring_cut(r_bore, p.glass_oring_groove_od / 2.0, z_bot + 3.0, p.glass_oring_flat_w, ramp_dir=+1.0)
    mouth_lead = (
        bd.Cone(r_bore + 0.7, r_bore, 1.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
        - bd.Cylinder(r_hub + 0.5, 1.4, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, -0.2))
    ).translate((0, 0, z_bot - 0.1))
    part = part - shroud_annulus - shroud_stop - g2 - mouth_lead

    # Intact PETG/ASA-agnostic 31.1 x 31.1 mm core aperture + backed 2.0 x 2.5 mm top PMMA-safe silicone channel!
    core_thru = bd.Box(p.core_pocket_w, p.core_pocket_w, (z_top - z_bot) + 2.0,
                       align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, z_bot - 1.0))
    part = part - core_thru
    w_g = p.core_pocket_w + 2.0 * p.cap_top_seal_groove  # 35.1 mm (2.65 mm outer rim on 40.4 mm collar!)
    with bd.BuildSketch(bd.Plane.XY.offset(z_top + 0.05)) as sk_top:
        bd.Rectangle(w_g, w_g)
    with bd.BuildSketch(bd.Plane.XY.offset(z_top - p.cap_top_seal_depth)) as sk_bot:
        bd.Rectangle(p.core_pocket_w, p.core_pocket_w)
    part = part - bd.loft([sk_bot.sketch, sk_top.sketch])

    # P0-1 FIXED: 2x plain teardrop M3x10 SHCS bores on ±X at Z = 203.3 mm bearing flat on |X| = 20.2 mm collar walls!
    # ZERO deep Ø6.4 mm counterbore eating into roof or silicone channel!
    z_lock = p.z_cap_top_lock  # 203.3
    td_thru = _teardrop_profile_wire(p.m3_clearance_dia / 2.0, 42.0)
    for sx in (-1.0, 1.0):
        h_lock = bd.extrude(td_thru, 24.0).rotate(bd.Axis.X, 90.0).rotate(bd.Axis.Z, 90.0)
        if sx > 0:
            h_lock = h_lock.translate((14.0, 0.0, z_lock))
        else:
            h_lock = h_lock.rotate(bd.Axis.Z, 180.0).translate((-14.0, 0.0, z_lock))
        part = part - h_lock

    return part


def build_plug_top(p: LepiLEDParams) -> bd.Part:
    """Build Rev 4.8 MECH-PLUG-TOP: 8 mm tall 45-deg-beveled obelisk finial sealing top of Al chimney."""
    insert = bd.Box(p.plug_top_w, p.plug_top_w, p.plug_top_insert_h,
                    align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, p.z_core_top - p.plug_top_insert_h))
    insert = bd.fillet(insert.edges().filter_by(bd.Axis.Z), 1.5)

    skirt_h = 3.0
    bevel_h = p.plug_top_cap_h - skirt_h
    cap_base = bd.Box(p.plug_top_cap_w, p.plug_top_cap_w, skirt_h,
                      align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, p.z_core_top))
    cap_base = bd.fillet(cap_base.edges().filter_by(bd.Axis.Z), 1.5)

    with bd.BuildSketch(bd.Plane.XY.offset(p.z_core_top + skirt_h)) as sk_b:
        bd.RectangleRounded(p.plug_top_cap_w, p.plug_top_cap_w, radius=1.5)
    with bd.BuildSketch(bd.Plane.XY.offset(p.z_plug_top_end)) as sk_t:
        bd.RectangleRounded(p.plug_top_cap_w - 2.0 * bevel_h, p.plug_top_cap_w - 2.0 * bevel_h, radius=1.2)
    crown = bd.loft([sk_b.sketch, sk_t.sketch])

    return insert.fuse(cap_base).fuse(crown)


def build_hang_bushing_half(p: LepiLEDParams, side: float = 1.0, core_w_override: float | None = None) -> bd.Part:
    """
    Build one half of Rev 4.8 MECH-HANG-BUSHING: Signal-Orange Ø8 mm paracord grommet w/ 45-deg snap-retention barb!
    Prints flat on its outer flange face with 0.000 mm^2 overhang — print 2x identical halves!
    """
    r_bore = p.hang_bush_id / 2.0                  # 2.70 mm
    r_sleeve = p.core_hang_hole_dia / 2.0 - 0.15   # 3.85 mm (slips into Ø8.0 mm Al hole)
    r_barb = p.core_hang_hole_dia / 2.0 + 0.15     # 4.15 mm (0.30 mm radial snap barb locks behind 3.0 mm Al wall!)
    r_flange = p.hang_bush_flange_od / 2.0         # 6.00 mm
    sleeve_len = p.core_wall + 1.8                 # 4.8 mm

    flange = bd.Cylinder(r_flange, p.hang_bush_flange_t, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    flange_top_e = flange.edges().filter_by(bd.GeomType.CIRCLE).filter_by_position(bd.Axis.Z, -0.1, 0.1)
    flange = bd.chamfer(flange_top_e, length=0.6)
    sleeve = bd.Cylinder(r_sleeve, sleeve_len, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, p.hang_bush_flange_t))
    # Self-supporting 45-deg snap barb ridge right behind the 3.0 mm Al tube wall (0 overhang upright!)
    z_barb = p.hang_bush_flange_t + p.core_wall + 0.15
    barb_in = bd.Cone(r_sleeve, r_barb, 0.40, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, z_barb))
    barb_out = bd.Cone(r_barb, r_sleeve, 0.90, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, z_barb + 0.40))
    # 2x axial flex relief slots on sleeve tip so barb snaps smoothly into Ø8.0 mm hole
    slot = bd.Box(1.2, 2.0 * r_barb + 1.0, 2.4, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, z_barb - 0.6))
    bore = bd.Cylinder(r_bore, p.hang_bush_flange_t + sleeve_len + 2.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, -1.0))
    lead = bd.Cone(r_bore + 0.9, r_bore, 0.9, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, -0.05))
    half = flange.fuse(sleeve).fuse(barb_in).fuse(barb_out) - bore - lead - slot

    cw = core_w_override or p.core_w_nom
    x_face = 0.5 * cw + 0.05
    if side > 0:
        return half.rotate(bd.Axis.Y, -90.0).translate((x_face + p.hang_bush_flange_t, 0.0, p.z_hang_hole))
    return half.rotate(bd.Axis.Y, 90.0).translate((-x_face - p.hang_bush_flange_t, 0.0, p.z_hang_hole))


def build_hang_bail(p: LepiLEDParams) -> bd.Part:
    """
    Build Rev 4.8 DIY C-shaped wire hanging bail (bent from ~175 mm of Ø2.2-3.0 mm coat-hanger wire; £0 BOM):
      - Two coaxial inward pivot pins enter the ±X Signal-Orange bushings (Ø4.0 mm bore) to |X| = 8.0 mm
        (8.65 mm engagement past outer flange; 4.7 mm below MECH-PLUG-TOP insert!).
      - Converging upper shoulders (~22 deg inward) self-center carabiners/hooks at X = 0 AND pull the two
        pivot pins INWARD into the aluminum core under gravity load (impossible to splay open!).
      - 38.7 mm clear hanging gap above MECH-PLUG-TOP finial; springs open slightly by hand to remove/pack.
    """
    x_tip = p.bail_pin_tip_x             # 8.0
    x_leg = p.bail_half_w                # 22.0
    z_piv = p.z_hang_hole                # 252.0
    z_leg = z_piv + p.bail_leg_h         # 282.0
    x_crn = p.bail_crown_half_w + 1.0    # 8.5 (crown corner before R=8.0 fillet -> smooth ~17 mm rounded top!)
    z_top = p.z_bail_top_center          # 316.0

    # Build 100% G1-tangent symmetric centerline in XY (Y -> global Z after +90 deg X rotation)
    r_elb = 3.5
    r_sh = 7.0
    r_crn = 8.0

    # Shoulder unit vector from (-x_leg, z_leg) -> (-x_crn, z_top)
    dx_s = x_leg - x_crn   # 13.5
    dz_s = z_top - z_leg   # 34.0
    l_s = math.hypot(dx_s, dz_s)
    ux_s, uz_s = dx_s / l_s, dz_s / l_s
    alpha = math.atan2(dx_s, dz_s)  # ~21.66 deg from vertical
    t_sh = r_sh * math.tan(0.5 * alpha)
    t_crn = r_crn * math.tan(0.5 * (0.5 * math.pi - alpha))

    # Left half tangent points (right half is exact X-mirror!)
    p0 = (-x_tip, z_piv)
    p1_in = (-(x_leg - r_elb), z_piv)
    p1_mid = (-(x_leg - r_elb * (1.0 - math.sqrt(0.5))), z_piv + r_elb * (1.0 - math.sqrt(0.5)))
    p1_out = (-x_leg, z_piv + r_elb)

    p2_in = (-x_leg, z_leg - t_sh)
    p2_out = (-x_leg + t_sh * ux_s, z_leg + t_sh * uz_s)
    # Arc midpoint for left shoulder (center is at (-x_leg + r_sh, z_leg - t_sh))
    c2x, c2z = -x_leg + r_sh, z_leg - t_sh
    a2_mid = math.pi - 0.5 * alpha
    p2_mid = (c2x + r_sh * math.cos(a2_mid), c2z + r_sh * math.sin(a2_mid))

    p3_in = (-x_crn - t_crn * ux_s, z_top - t_crn * uz_s)
    p3_out = (-x_crn + t_crn, z_top)
    # Arc midpoint for left crown (center is at (-x_crn + t_crn, z_top - r_crn))
    c3x, c3z = -x_crn + t_crn, z_top - r_crn
    a3_mid = 0.5 * math.pi + 0.5 * (0.5 * math.pi - alpha)
    p3_mid = (c3x + r_crn * math.cos(a3_mid), c3z + r_crn * math.sin(a3_mid))

    def mir(pt: tuple[float, float]) -> tuple[float, float]:
        return (-pt[0], pt[1])

    with bd.BuildLine(bd.Plane.XY) as path_line:
        bd.Line(p0, p1_in)
        bd.ThreePointArc(p1_in, p1_mid, p1_out)
        bd.Line(p1_out, p2_in)
        bd.ThreePointArc(p2_in, p2_mid, p2_out)
        bd.Line(p2_out, p3_in)
        bd.ThreePointArc(p3_in, p3_mid, p3_out)
        bd.Line(p3_out, mir(p3_out))
        bd.ThreePointArc(mir(p3_out), mir(p3_mid), mir(p3_in))
        bd.Line(mir(p3_in), mir(p2_out))
        bd.ThreePointArc(mir(p2_out), mir(p2_mid), mir(p2_in))
        bd.Line(mir(p2_in), mir(p1_out))
        bd.ThreePointArc(mir(p1_out), mir(p1_mid), mir(p1_in))
        bd.Line(mir(p1_in), mir(p0))

    wire_path = path_line.wire()
    # Sweep Ø2.6 mm circular cross-section perpendicular to start tangent (-X at p0)
    prof_plane = bd.Plane(origin=(p0[0], p0[1], 0.0), x_dir=(0.0, 1.0, 0.0), z_dir=(-1.0, 0.0, 0.0))
    with bd.BuildSketch(prof_plane) as sk_wire:
        bd.Circle(p.bail_wire_dia / 2.0)
    bail_xy = bd.sweep(sk_wire.sketch, path=wire_path)
    return bail_xy.rotate(bd.Axis.X, 90.0)


def build_drill_jig(p: LepiLEDParams) -> bd.Part:
    """Build Rev 4.8 MECH-DRILL-JIG: snap-on 30.6 mm U-channel drill guide matching cad_params.json 1:1."""
    wall = 3.0
    inner_w = p.core_w_nom + 0.6
    outer_w = inner_w + 2.0 * wall
    dg = p.drill_guide_from_core_bot_mm
    jig_len = math.ceil(dg["cap_top_lock_x_faces"] + 8.0)  # Covers anchor pin, all 4 star rows, and top-cap lock!
    leg_h = 15.0

    base = bd.Box(wall, outer_w, jig_len, align=(bd.Align.MIN, bd.Align.CENTER, bd.Align.MIN))
    leg_pos = bd.Box(leg_h, wall, jig_len, align=(bd.Align.MIN, bd.Align.MAX, bd.Align.MIN)).translate((0, outer_w / 2.0, 0))
    leg_neg = bd.Box(leg_h, wall, jig_len, align=(bd.Align.MIN, bd.Align.MIN, bd.Align.MIN)).translate((0, -outer_w / 2.0, 0))
    end_stop = bd.Box(10.0, outer_w, wall, align=(bd.Align.MIN, bd.Align.CENTER, bd.Align.MAX))
    jig = base.fuse(leg_pos).fuse(leg_neg).fuse(end_stop)

    guide_zs = (
        dg["anchor_cross_pin_x_faces"],
        dg["vis_star_bot_bolt_all_4_faces"],
        dg["vis_star_top_bolt_all_4_faces"],
        dg["uv_star_bot_bolt_all_4_faces"],
        dg["uv_star_top_bolt_all_4_faces"],
        dg["cap_top_lock_x_faces"],
    )
    for z_rel in guide_zs:
        guide = bd.Cylinder(1.30, wall + 2.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER)).rotate(bd.Axis.Y, 90.0).translate((wall / 2.0, 0.0, z_rel))
        jig = jig - guide

    jig = jig.rotate(bd.Axis.Y, -90.0)
    bb = jig.bounding_box()
    return jig.translate((0.0, 0.0, -bb.min.Z))


def _load_populated_smd_solids(p: LepiLEDParams) -> list[bd.Shape]:
    """Read ALL 48 populated SMD centroids & TRUE KiCad rotations directly from driver_pcb.kicad_pcb (no JLCPCB offset corruption!)."""
    pcb_path = Path(__file__).resolve().parents[2] / "pcb_design" / "driver_pcb" / "driver_pcb.kicad_pcb"
    txt = pcb_path.read_text(encoding="utf-8")
    # Parse (footprint "..." ... (at X Y [ROT]) ... (property "Reference" "REF" ...)) blocks cleanly
    # Aux origin in build_driver_pcb.py is (100.0, 100.0) with global board Y = 100.0 - kicad_Y
    exclude = {"H1", "H2", "H3", "H4", "TP1", "TP2", "TP3", "TP4", "J1", "J2", "J3", "J4", "D13", "D14"}
    solids: list[bd.Shape] = []
    # Split on top-level footprint blocks
    for blk in txt.split("\n\t(footprint ")[1:]:
        m_ref = re.search(r'\(property\s+"Reference"\s+"([^"]+)"', blk)
        m_at = re.search(r'\(at\s+([-+]?\d+(?:\.\d+)?)\s+([-+]?\d+(?:\.\d+)?)(?:\s+([-+]?\d+(?:\.\d+)?))?\)', blk)
        if not m_ref or not m_at:
            continue
        ref = m_ref.group(1).strip()
        if ref in exclude:
            continue
        bx = float(m_at.group(1)) - 100.0
        by = 100.0 - float(m_at.group(2))
        rot = float(m_at.group(3)) if m_at.group(3) else 0.0
        lx, wy, hz = SMD_PACKAGE_DIMS.get(ref, (1.7, 0.9, 0.65))
        if int(round(rot)) % 180 == 90:
            lx, wy = wy, lx
        # Rev 4.8: SMD/JST-Side UP on F.Cu (Z = p.pcb_z_fcu .. p.pcb_z_fcu + hz)!
        box = bd.Box(lx, wy, hz, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((bx, p.pcb_y_center + by, p.pcb_z_fcu))
        solids.append(box)
    assert len(solids) == 48, f"Expected 48 populated SMDs from driver_pcb.kicad_pcb, got {len(solids)}"
    return solids


def build_assembly_parts(p: LepiLEDParams, core_w_override: float | None = None,
                         glass_id_override: float | None = None, glass_od_override: float | None = None,
                         glass_length_override: float | None = None) -> dict[str, bd.Shape]:
    """Build all Rev 4.8 physical assembly components incl. ALL 14 brass inserts & exact-length BOM screws!"""
    core_w = core_w_override or p.core_w_nom
    g_id = glass_id_override or p.glass_id_nom
    g_od = glass_od_override or p.glass_od_nom
    g_len = glass_length_override or p.glass_length

    lid_bot = build_lid_bot(p)
    cap_bot = build_cap_bot(p)
    cap_top = build_cap_top(p)
    plug_top = build_plug_top(p)
    core_anchor = build_core_anchor(p)
    clamp_pos = build_cable_clamp_half(p, side=+1.0)
    clamp_neg = build_cable_clamp_half(p, side=-1.0)
    cable_clamp = bd.Compound([clamp_pos, clamp_neg])
    hang_bushing = bd.Compound([build_hang_bushing_half(p, side=+1.0, core_w_override=core_w), build_hang_bushing_half(p, side=-1.0, core_w_override=core_w)])
    hang_bail = build_hang_bail(p)

    # Serviceable Lid-Mounted Driver PCB (B.Cu DOWN at Z=45.5 mm, F.Cu SMD/JST UP at Z=47.1 mm, Y_ctr = +7.0 mm!)
    pcb_board = bd.Box(p.pcb_w, p.pcb_l, p.pcb_thick, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    pcb_board = bd.fillet(pcb_board.edges().filter_by(bd.Axis.Z), p.pcb_corner_r).translate((0.0, p.pcb_y_center, p.pcb_z_bcu))
    for sx in (-1.0, 1.0):
        for sy in (-1.0, 1.0):
            npth = bd.Cylinder(p.pcb_hole_drill / 2.0, p.pcb_thick + 0.6, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER)).translate(
                (sx * p.pcb_hole_x, p.pcb_y_center + sy * p.pcb_hole_y, p.pcb_z_bcu + 0.5 * p.pcb_thick)
            )
            pcb_board = pcb_board - npth

    pcb_parts: list[bd.Shape] = [pcb_board, *_load_populated_smd_solids(p)]
    j2_hdr = bd.Box(7.4, 5.8, p.pcb_jst_mated_h, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((-5.2, p.pcb_y_center + 19.2, p.pcb_z_fcu))
    j3_hdr = bd.Box(7.4, 5.8, p.pcb_jst_mated_h, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((5.2, p.pcb_y_center + 19.2, p.pcb_z_fcu))
    j4_hdr = bd.Box(9.9, 5.8, p.pcb_jst_mated_h, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((-1.4, p.pcb_y_center - 2.5, p.pcb_z_fcu))
    j1_outer = bd.Box(8.94, 9.17, 3.46, align=(bd.Align.CENTER, bd.Align.MIN, bd.Align.MIN)).translate((0.0, p.y_j1_mouth, p.pcb_z_fcu))
    j1_cav = bd.Box(8.34, p.usbc_mating_depth_mm + 0.05, 2.56, align=(bd.Align.CENTER, bd.Align.MIN, bd.Align.CENTER)).translate((0.0, p.y_j1_mouth - 0.05, p.z_j1_center))
    j1_usbc = j1_outer - j1_cav
    j23_pins = bd.Box(15.0, 2.0, p.pcb_jst_pin_protrude, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)).translate((0.0, p.pcb_y_center + 19.2, p.pcb_z_bcu))
    j4_pins = bd.Box(7.5, 2.0, p.pcb_jst_pin_protrude, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)).translate((-1.4, p.pcb_y_center - 2.5, p.pcb_z_bcu))
    j1_pins = bd.Box(9.6, 5.7, p.pcb_jst_pin_protrude, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)).translate((0.0, p.pcb_y_center - 19.54, p.pcb_z_bcu))
    pcb_parts.extend([j2_hdr, j3_hdr, j4_hdr, j1_usbc, j23_pins, j4_pins, j1_pins])
    pcb_assy = bd.Compound(pcb_parts)

    # Central protruding 30 x 30 x 3.0 mm Al 6063-T6 core (L = 200.0 mm; chimney-only matte black!)
    core_out = bd.Box(core_w, core_w, p.core_length, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    core_in = bd.Box(core_w - 2.0 * p.core_wall, core_w - 2.0 * p.core_wall, p.core_length + 2.0,
                     align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, -1.0))
    hs_core = (core_out - core_in).translate((0, 0, p.z_core_bot))
    hang_bore = bd.Cylinder(p.core_hang_hole_dia / 2.0, core_w + 2.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER)).rotate(bd.Axis.Y, 90.0).translate((0.0, 0.0, p.z_hang_hole))
    anchor_pin_bore = bd.Cylinder(1.75, core_w + 2.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER)).rotate(bd.Axis.Y, 90.0).translate((0.0, 0.0, p.z_anchor_pin))
    for sx in (-1.0, 1.0):
        csk = bd.Cone(1.7, 3.2, 1.5, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).rotate(bd.Axis.Y, 90.0 if sx > 0 else -90.0).translate((sx * (0.5 * core_w - 1.45), 0.0, p.z_anchor_pin))
        hs_core = hs_core - csk
    top_lock_bore = bd.Cylinder(1.55, core_w + 2.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER)).rotate(bd.Axis.Y, 90.0).translate((0.0, 0.0, p.z_cap_top_lock))
    hs_core = hs_core - hang_bore - anchor_pin_bore - top_lock_bore

    # ALL 14 Modeled Brass Heat-Set Inserts — ALL IDENTICAL STANDARD WORKSHOP M3 x 5.0 x 4.2 mm!
    inserts_list = []
    # a) 4x M3x5 lid inserts inside cap_bot at R=40.2 mm
    for deg in (45.0, 135.0, 225.0, 315.0):
        rad = math.radians(deg)
        ix, iy = p.lid_bot_bolt_r * math.cos(rad), p.lid_bot_bolt_r * math.sin(rad)
        ins = (bd.Cylinder(1.98, 5.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
               - bd.Cylinder(1.52, 5.2, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, -0.1)))
        inserts_list.append(ins.translate((ix, iy, p.z_lid_bot_end + 0.05)))
    # b) 2x M3x5.0 blind cable-clamp inserts inside 8.5 mm MECH-LID-BOT (Z = 22.05 .. 27.05 mm; 3.45 mm below dry bay!)
    for sx in (-1.0, 1.0):
        ins = (bd.Cylinder(1.98, 5.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
               - bd.Cylinder(1.52, 5.2, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, -0.1)))
        inserts_list.append(ins.translate((sx * p.clamp_bolt_dx, p.clamp_y, p.z_lid_bot_start + 0.05)))
    # c) 2x M3x5 vertical core-anchor inserts on ±Y at (0, ±6.5 mm)
    for sy in (-1.0, 1.0):
        ins = (bd.Cylinder(1.98, 5.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
               - bd.Cylinder(1.52, 5.2, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, -0.1)))
        inserts_list.append(ins.translate((0.0, sy * p.anchor_bolt_y, p.z_core_bot + 0.05)))
    # d) 2x M3x5 horizontal cross-pin inserts on ±X inside core_anchor
    for sx in (-1.0, 1.0):
        ins = (bd.Cylinder(1.98, 5.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX))
               - bd.Cylinder(1.52, 5.2, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)).translate((0, 0, 0.1)))
        inserts_list.append(ins.rotate(bd.Axis.Y, 90.0 if sx > 0 else -90.0).translate((sx * (p.anchor_w / 2.0 - 0.05), 0.0, p.z_anchor_pin)))
    # e) 4x M3x5.0 unified PCB standoff inserts in MECH-LID-BOT standoff tops (Z = 41.45 .. 46.45 mm!)
    for sx in (-1.0, 1.0):
        for sy in (-1.0, 1.0):
            hx = sx * p.pcb_hole_x
            hy = p.pcb_y_center + sy * p.pcb_hole_y
            ins = (bd.Cylinder(1.98, 5.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX))
                   - bd.Cylinder(1.52, 5.2, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)).translate((0, 0, 0.1)))
            inserts_list.append(ins.translate((hx, hy, p.pcb_z_bcu - 0.05)))
    inserts_brass = bd.Compound(inserts_list)

    # ALL Exact Full-Length Modeled Workshop M3 CSK Fasteners (unified M3 across the ENTIRE lamp!)
    fasteners_list = []
    # 1. 4x M3x12 CSK flush recessed lid bolts (full 12.0 mm OAL: 1.5 mm CSK head + 10.5 mm shank -> 3.5 mm into M3x5 insert!)
    for deg in (45.0, 135.0, 225.0, 315.0):
        rad = math.radians(deg)
        lx, ly = p.lid_bot_bolt_r * math.cos(rad), p.lid_bot_bolt_r * math.sin(rad)
        lb_head = bd.Cone(2.95, 1.48, 1.47, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((lx, ly, p.z_lid_bot_start + 0.05))
        lb_shank = bd.Cylinder(1.48, 10.5, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((lx, ly, p.z_lid_bot_start + 1.52))
        fasteners_list.append(lb_head.fuse(lb_shank))
    # 2. 2x M3x12 CSK flush split cable clamp bolts (full 12.0 mm OAL: sits flush at Z=13.0 -> tip at Z=25.0 inside M3x5 blind insert!)
    for sx in (-1.0, 1.0):
        cx, cy = sx * p.clamp_bolt_dx, p.clamp_y
        ch = bd.Cone(2.95, 1.48, 1.47, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((cx, cy, p.z_lid_bot_start - p.clamp_outer_h + 0.05))
        cs = bd.Cylinder(1.48, 10.5, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((cx, cy, p.z_lid_bot_start - p.clamp_outer_h + 1.52))
        fasteners_list.append(ch.fuse(cs))
    # 3. 2x M3x12 CSK flush internal dry-bay core anchor bolts on ±Y at (0, ±6.5 mm; full 12.0 mm OAL!)
    for sy in (-1.0, 1.0):
        ay = sy * p.anchor_bolt_y
        ah = bd.Cone(2.95, 1.48, 1.47, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0.0, ay, p.cap_bot_ceiling_z + 0.05))
        ash = bd.Cylinder(1.48, 10.5, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0.0, ay, p.cap_bot_ceiling_z + 1.52))
        fasteners_list.append(ah.fuse(ash))
    # 4. 2x FULL-LENGTH M3x8 CSK flush cross-pin screws (exact 8.0 mm!) on ±X
    for sx in (-1.0, 1.0):
        rot_y = 90.0 if sx > 0 else -90.0
        ps = bd.Cylinder(1.48, 8.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)).rotate(bd.Axis.Y, rot_y).translate((sx * (0.5 * core_w - 0.1), 0.0, p.z_anchor_pin))
        fasteners_list.append(ps)
    # 5. 2x FULL-LENGTH M3x10 CSK + M3 steel flat washer radial top-cap lock screws bearing on |X| = 20.2 mm collar walls!
    x_collar = p.cap_top_collar_w / 2.0 + 0.05  # 20.25
    for sx in (-1.0, 1.0):
        if sx > 0:
            th = bd.Cylinder(3.0, 2.2, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).rotate(bd.Axis.Y, 90.0).translate((x_collar, 0.0, p.z_cap_top_lock))
            ts = bd.Cylinder(1.48, 9.5, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)).rotate(bd.Axis.Y, 90.0).translate((x_collar, 0.0, p.z_cap_top_lock))
        else:
            th = bd.Cylinder(3.0, 2.2, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)).rotate(bd.Axis.Y, 90.0).translate((-x_collar, 0.0, p.z_cap_top_lock))
            ts = bd.Cylinder(1.48, 9.5, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).rotate(bd.Axis.Y, 90.0).translate((-x_collar, 0.0, p.z_cap_top_lock))
        fasteners_list.append(th.fuse(ts))
    # 6. 4x M3x8 CSK + M3 steel washer + Ø7.0x0.8 mm M3 nylon insulating washer securing driver_pcb into M3x5 lid inserts!
    for sx in (-1.0, 1.0):
        for sy in (-1.0, 1.0):
            hx = sx * p.pcb_hole_x
            hy = p.pcb_y_center + sy * p.pcb_hole_y
            # 0.8 mm nylon washer + 0.5 mm steel washer + 1.5 mm CSK head = 2.8 mm stack above F.Cu; 6.2 mm shank below!
            pw = bd.Cylinder(3.50, 2.8, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((hx, hy, p.pcb_z_fcu + 0.05))
            ps = bd.Cylinder(1.48, 6.2, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)).translate((hx, hy, p.pcb_z_fcu + 0.05))
            fasteners_list.append(pw.fuse(ps))
    fasteners_m3 = bd.Compound(fasteners_list)

    # Clear PLEXIGLAS XT 0A070 shroud (Ø60 x 54 x 3.0 x 115 mm)
    z_g_start = p.z_glass_bot - 0.5 * (g_len - p.glass_length)
    g_outer = bd.Cylinder(g_od / 2.0, g_len, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    g_inner = bd.Cylinder(g_id / 2.0, g_len + 2.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, -1.0))
    glass_tube = (g_outer - g_inner).translate((0, 0, z_g_start))

    # 8x Pre-mounted 20 mm LED stars + 16x M3 pan screws w/ Ø7.0 mm nylon washers edge-clamping at R = 11.7 mm!
    star_items = []
    for angle in (0.0, 90.0, 180.0, 270.0):
        x0 = core_w / 2.0 + p.star_tim_thick
        for z_star, led_h in ((p.z_led_uv, p.led_uv_max_h), (p.z_led_vis, p.led_vis_max_h)):
            star_disc = bd.Cylinder(p.star_dia / 2.0, p.star_thick, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).rotate(bd.Axis.Y, 90.0).translate((x0, 0.0, z_star))
            led_pkg = bd.Box(led_h, 3.45, 3.45, align=(bd.Align.MIN, bd.Align.CENTER, bd.Align.CENTER)).translate((x0 + p.star_thick, 0.0, z_star))
            s_top = bd.Cylinder(p.star_washer_od / 2.0, p.m3_pan_plus_washer_h, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).rotate(bd.Axis.Y, 90.0).translate((x0 + p.star_thick, 0.0, z_star + p.star_bolt_r))
            s_bot = bd.Cylinder(p.star_washer_od / 2.0, p.m3_pan_plus_washer_h, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).rotate(bd.Axis.Y, 90.0).translate((x0 + p.star_thick, 0.0, z_star - p.star_bolt_r))
            star_items.append(bd.Compound([star_disc, led_pkg, s_top, s_bot]).rotate(bd.Axis.Z, angle))
    dtp_stars = bd.Compound(star_items)

    # Bottom-mounted SW1 (C&K 7211SYZBE) + REAL 18.6 mm silicone boot on MECH-LID-BOT at (0.0, +15.0 mm)
    z_sw0 = p.z_lid_bot_start
    sw_body = bd.Box(p.sw1_body_w_x, p.sw1_body_w_y, p.sw1_body_h_z,
                     align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((p.sw1_x, p.sw1_y, z_sw0 + p.sw1_wall_thick + 0.05))
    sw_lugs = bd.Box(10.0, 8.5, p.sw1_lugs_h_z,
                     align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((p.sw1_x, p.sw1_y, z_sw0 + p.sw1_wall_thick + 0.05 + p.sw1_body_h_z))
    sw_bush = bd.Cylinder(p.sw1_hole_dia / 2.0 - 0.05, p.sw1_wall_thick + 0.1,
                          align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((p.sw1_x, p.sw1_y, z_sw0))
    sw_boot = bd.Cylinder(p.sw1_boot_od / 2.0, p.sw1_boot_protrude_z,
                          align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)).translate((p.sw1_x, p.sw1_y, z_sw0 - 0.05))
    sw1_assy = bd.Compound([sw_body, sw_lugs, sw_bush, sw_boot])

    # Realistic 15.0 mm 90-deg-down USB-C PD plug + 7.0 mm strain relief mated into TOP-mounted J1!
    y_plug_tip = p.y_j1_mouth + p.usbc_mating_depth_mm
    plug_barrel = bd.Box(8.3, p.usbc_mating_depth_mm + 1.5, 2.5, align=(bd.Align.CENTER, bd.Align.MAX, bd.Align.CENTER)).translate((0.0, y_plug_tip, p.z_j1_center))
    plug_body = bd.Box(p.usbc_plug_90_w, p.usbc_plug_90_len - 1.5, p.usbc_plug_90_h,
                       align=(bd.Align.CENTER, bd.Align.MAX, bd.Align.MAX)).translate((0.0, p.y_j1_mouth - 1.5, p.z_j1_center + 3.0))
    y_plug_ctr = p.y_j1_mouth - 1.5 - 0.5 * (p.usbc_plug_90_len - 1.5)
    z_plug_bot = p.z_j1_center + 3.0 - p.usbc_plug_90_h
    plug_strain = bd.Cone(2.6, 3.6, p.usbc_strain_relief_h, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)).translate((0.0, y_plug_ctr, z_plug_bot))
    usbc_plug_assy = plug_barrel.fuse(plug_body).fuse(plug_strain)

    return dict(
        lid_bot=lid_bot,
        cap_bot=cap_bot,
        cap_top=cap_top,
        plug_top=plug_top,
        core_anchor=core_anchor,
        cable_clamp=cable_clamp,
        hang_bushing=hang_bushing,
        hang_bail=hang_bail,
        pcb_assy=pcb_assy,
        hs_core=hs_core,
        inserts_brass=inserts_brass,
        fasteners_m3=fasteners_m3,
        glass_tube=glass_tube,
        dtp_stars=dtp_stars,
        sw1_assy=sw1_assy,
        usbc_plug_assy=usbc_plug_assy,
    )


def _raycast_mesh_numpy(mesh: trimesh.Trimesh, origins: np.ndarray, dirs: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Dependency-free vectorized Moller-Trumbore ray-triangle intersection on an STL mesh."""
    tris = mesh.triangles  # (T, 3, 3)
    v0 = tris[:, 0, :]
    e1 = tris[:, 1, :] - v0
    e2 = tris[:, 2, :] - v0
    eps = 1e-9
    hit_locs: list[np.ndarray] = []
    hit_idx: list[int] = []
    for i, (orig, d) in enumerate(zip(origins, dirs)):
        h = np.cross(d, e2)
        a = np.einsum("ij,ij->i", e1, h)
        valid = np.abs(a) > eps
        if not np.any(valid):
            continue
        f = 1.0 / a[valid]
        s = orig - v0[valid]
        u = f * np.einsum("ij,ij->i", s, h[valid])
        m1 = (u >= -1e-6) & (u <= 1.0 + 1e-6)
        if not np.any(m1):
            continue
        idx_v = np.nonzero(valid)[0][m1]
        f1 = f[m1]
        s1 = s[m1]
        u1 = u[m1]
        q = np.cross(s1, e1[idx_v])
        v = f1 * np.einsum("ij,j->i", q, d)
        m2 = (v >= -1e-6) & (u1 + v <= 1.0 + 1e-6)
        if not np.any(m2):
            continue
        t = f1[m2] * np.einsum("ij,ij->i", e2[idx_v[m2]], q[m2])
        m3 = t > 1e-6
        for tv in t[m3]:
            hit_locs.append(orig + tv * d)
            hit_idx.append(i)
    if not hit_locs:
        return np.zeros((0, 3)), np.zeros((0,), dtype=int)
    return np.asarray(hit_locs), np.asarray(hit_idx, dtype=int)


def check_shell_raycast_breaches(out_dir: Path, p: LepiLEDParams) -> dict[str, dict | bool]:
    """
    NEW Rev 4.8 Section 9 Mandatory Gate: Exterior-to-Interior Ray-Cast Wall-Breach Detector!
    Catches unintended through-holes in sealed rain roofs, bulkheads, and blind insert roofs
    (would have immediately caught both Rev 4.6's MECH-CAP-TOP roof holes AND open clamp bores!).
    """
    results: dict[str, dict | bool] = {}

    # 1. MECH-CAP-TOP lofted rain roof (R ∈ [20.6, 40.5 mm], all 360 deg): vertical rays from Z=top+10 downward
    #    MUST hit solid plastic ABOVE the shroud bore top (z_glass_top + 1.5)!
    m_top = trimesh.load(str(out_dir / "mech_cap_top.stl"), force="mesh")
    origins, dirs = [], []
    for rad in np.linspace(20.6, 40.5, 12):
        for ang in np.linspace(0.0, 2.0 * math.pi, 36, endpoint=False):
            origins.append([rad * math.cos(ang), rad * math.sin(ang), p.z_cap_top_top + 10.0])
            dirs.append([0.0, 0.0, -1.0])
    locs, idx_ray = _raycast_mesh_numpy(m_top, np.array(origins), np.array(dirs))
    hit_by_ray: dict[int, float] = {}
    for pt_h, r_i in zip(locs, idx_ray):
        hit_by_ray[int(r_i)] = max(hit_by_ray.get(int(r_i), -999.0), float(pt_h[2]))
    breaches_top = sum(1 for i in range(len(origins)) if hit_by_ray.get(i, -999.0) <= p.z_glass_top + 1.5)
    results["cap_top_roof_raycast_zero_holes"] = {
        "rays_cast": len(origins),
        "roof_breaches": breaches_top,
        "pass": breaches_top == 0,
    }

    # 2. MECH-LID-BOT blind clamp insert roofs at (±13.0, -20.5 mm): vertical rays through BOTH blind insert
    #    centers MUST hit solid plastic roof (proving ZERO open through-hole into dry bay!)
    m_lid = trimesh.load(str(out_dir / "mech_lid_bot.stl"), force="mesh")
    lid_origins = [[sx * p.clamp_bolt_dx, p.clamp_y, p.z_lid_bot_end + 5.0] for sx in (-1.0, 1.0)]
    lid_dirs = [[0.0, 0.0, -1.0], [0.0, 0.0, -1.0]]
    l_locs, l_idx = _raycast_mesh_numpy(m_lid, np.array(lid_origins), np.array(lid_dirs))
    lid_hits = {int(r_i) for r_i in l_idx}
    results["lid_bot_blind_clamp_insert_seal"] = {
        "inserts_checked": 2,
        "sealed_roofs_hit": len(lid_hits),
        "pass": len(lid_hits) == 2,
    }

    # 3. MECH-CAP-BOT outer electronics-bay frustum wall (Z ∈ [30.5, 61.5 mm], all 360 deg):
    #    radial inward rays MUST hit solid wall before entering Ø71.6 mm dry bay (ZERO side-hole leaks!)
    m_bot = trimesh.load(str(out_dir / "mech_cap_bot.stl"), force="mesh")
    b_orig, b_dir = [], []
    for zv in np.linspace(30.5, 61.5, 8):
        for ang in np.linspace(0.0, 2.0 * math.pi, 36, endpoint=False):
            b_orig.append([55.0 * math.cos(ang), 55.0 * math.sin(ang), float(zv)])
            b_dir.append([-math.cos(ang), -math.sin(ang), 0.0])
    b_locs, b_idx = _raycast_mesh_numpy(m_bot, np.array(b_orig), np.array(b_dir))
    max_r_hit: dict[int, float] = {}
    for pt_h, r_i in zip(b_locs, b_idx):
        rh = math.hypot(float(pt_h[0]), float(pt_h[1]))
        max_r_hit[int(r_i)] = max(max_r_hit.get(int(r_i), 0.0), rh)
    side_breaches = sum(1 for i in range(len(b_orig)) if max_r_hit.get(i, 0.0) <= p.cap_bot_cavity_dia / 2.0 + 0.5)
    results["cap_bot_dry_bay_wall_zero_side_holes"] = {
        "rays_cast": len(b_orig),
        "wall_breaches": side_breaches,
        "pass": side_breaches == 0,
    }

    results["all_pass"] = all(v["pass"] for k, v in results.items() if isinstance(v, dict))
    return results


def check_fastener_seat_bearing(cap_bot: bd.Part, cap_top: bd.Part, lid_bot: bd.Part, p: LepiLEDParams) -> dict[str, dict | bool]:
    results: dict[str, dict | bool] = {}
    ideal_ring = math.pi * (2.75 ** 2 - 1.70 ** 2) * 2.0

    # 1. cap_bot 2x internal vertical M3x12 CSK anchor seats behind 1.55 mm CSK cone on ±Y at (0, ±6.5 mm)
    bot_ratios = []
    for sy in (-1.0, 1.0):
        ring = (
            bd.Cylinder(2.75, 2.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
            - bd.Cylinder(1.70, 2.2, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, -0.1))
        ).translate((0.0, sy * p.anchor_bolt_y, p.cap_bot_ceiling_z + 1.6))
        inter = cap_bot & ring
        bot_ratios.append((float(inter.volume) if inter is not None else 0.0) / ideal_ring)
    results["cap_bot_anchor_seat_bearing"] = {"min_contact_ratio": round(min(bot_ratios), 4), "min_required": 0.90, "pass": min(bot_ratios) >= 0.90}

    # 2. cap_top 2x radial M3x10 lock seats on flat vertical collar faces |X| = 20.2 mm
    top_ratios = []
    x_col = p.cap_top_collar_w / 2.0
    for sx in (-1.0, 1.0):
        ring = (
            bd.Cylinder(2.75, 2.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX))
            - bd.Cylinder(1.70, 2.2, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)).translate((0, 0, 0.1))
        ).rotate(bd.Axis.Y, 90.0 if sx > 0 else -90.0).translate((sx * x_col, 0.0, p.z_cap_top_lock))
        inter = cap_top & ring
        top_ratios.append((float(inter.volume) if inter is not None else 0.0) / ideal_ring)
    results["cap_top_lock_seat_bearing"] = {"min_contact_ratio": round(min(top_ratios), 4), "min_required": 0.85, "pass": min(top_ratios) >= 0.85}

    # 3. lid_bot 4x M3x12 CSK recessed lid bolt seats behind 1.55 mm CSK cone at R = 40.2 mm
    lid_ratios = []
    for deg in (45.0, 135.0, 225.0, 315.0):
        rad = math.radians(deg)
        lx, ly = p.lid_bot_bolt_r * math.cos(rad), p.lid_bot_bolt_r * math.sin(rad)
        ring = (
            bd.Cylinder(2.75, 2.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
            - bd.Cylinder(1.70, 2.2, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, -0.1))
        ).translate((lx, ly, p.z_lid_bot_start + 1.6))
        inter = lid_bot & ring
        lid_ratios.append((float(inter.volume) if inter is not None else 0.0) / ideal_ring)
    results["lid_bot_bolt_seat_bearing"] = {"min_contact_ratio": round(min(lid_ratios), 4), "min_required": 0.90, "pass": min(lid_ratios) >= 0.90}

    # 4. Core socket 4-wall intactness check on BOTH cap_bot & cap_top
    bot_wall_ok, top_wall_ok = True, True
    x_sock = p.core_pocket_w / 2.0 + 0.05
    for ang in (0.0, 180.0):
        probe_b = bd.Box(2.5, 16.0, 8.0, align=(bd.Align.MIN, bd.Align.CENTER, bd.Align.MIN)).translate((x_sock, 0.0, p.z_core_bot + 2.0)).rotate(bd.Axis.Z, ang)
        vb = float((cap_bot & probe_b).volume) if (cap_bot & probe_b) is not None else 0.0
        if vb < 0.70 * (2.5 * 16.0 * 8.0):
            bot_wall_ok = False
    for sy in (-1.0, 1.0):
        for sx in (-1.0, 1.0):
            probe_by = bd.Box(8.0, 2.5, 8.0, align=(bd.Align.CENTER, bd.Align.MIN if sy > 0 else bd.Align.MAX, bd.Align.MIN)).translate((sx * 9.5, sy * x_sock, p.z_core_bot + 2.0))
            vby = float((cap_bot & probe_by).volume) if (cap_bot & probe_by) is not None else 0.0
            if vby < 0.70 * (8.0 * 2.5 * 8.0):
                bot_wall_ok = False
    for ang in (0.0, 90.0, 180.0, 270.0):
        probe_t = bd.Box(2.5, 16.0, 8.0, align=(bd.Align.MIN, bd.Align.CENTER, bd.Align.MIN)).translate((x_sock, 0.0, p.z_cap_top_collar_bot - 2.0)).rotate(bd.Axis.Z, ang)
        vt = float((cap_top & probe_t).volume) if (cap_top & probe_t) is not None else 0.0
        if vt < 0.70 * (2.5 * 16.0 * 8.0):
            top_wall_ok = False
    results["core_sockets_4wall_intact"] = {"cap_bot_4wall_ok": bot_wall_ok, "cap_top_4wall_ok": top_wall_ok, "pass": bot_wall_ok and top_wall_ok}
    results["all_pass"] = all(v["pass"] for k, v in results.items() if isinstance(v, dict))
    return results


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


def audit_stl_overhangs(
    stl_path: Path,
    print_up_axis: tuple[float, float, float],
    max_overhang_deg: float = 46.0,
    allowed_bridge_z: float | None = None,
    allowed_bridge_xy: float | None = None,
) -> dict:
    mesh = trimesh.load(str(stl_path), force="mesh")
    up = np.array(print_up_axis, dtype=float)
    up = up / np.linalg.norm(up)
    z_proj = mesh.vertices @ up
    z_bed = float(np.min(z_proj))
    face_z_min = np.min(z_proj[mesh.faces], axis=1)
    off_bed = face_z_min > (z_bed + 0.05)

    dots = mesh.face_normals @ up
    downward = dots < -1e-4
    sel = downward & off_bed
    angles_deg = np.degrees(np.arcsin(np.clip(-dots[sel], 0.0, 1.0)))
    areas = mesh.area_faces[sel]
    centers = mesh.triangles_center[sel]
    bad = angles_deg > max_overhang_deg

    bridge_area = 0.0
    in_bridge = np.zeros_like(bad, dtype=bool)
    if allowed_bridge_z is not None and allowed_bridge_xy is not None:
        in_bridge = (
            bad
            & (np.abs(centers[:, 2] - allowed_bridge_z) < 0.25)
            & (np.abs(centers[:, 0]) <= allowed_bridge_xy)
            & (np.abs(centers[:, 1]) <= allowed_bridge_xy)
        )
        bridge_area = float(np.sum(areas[in_bridge]))
        bad = bad & (~in_bridge)

    non_bridge_angles = angles_deg[~in_bridge] if len(angles_deg) else np.array([])
    return {
        "stl_file": stl_path.name,
        "bed_z_proj_mm": round(z_bed, 3),
        "off_bed_overhang_gt46_faces": int(np.sum(bad)),
        "off_bed_overhang_gt46_area_mm2": round(float(np.sum(areas[bad])), 3),
        "intentional_hidden_bridge_area_mm2": round(bridge_area, 3),
        "max_off_bed_overhang_deg": round(float(np.max(non_bridge_angles)) if len(non_bridge_angles) else 0.0, 2),
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


def check_kinematic_insertion(assy: dict[str, bd.Shape], p: LepiLEDParams) -> dict[str, dict | bool]:
    lid_bot = assy["lid_bot"]
    cap_bot = assy["cap_bot"]
    # 1. SW1 vertical insertion into MECH-LID-BOT
    sw_body = bd.Box(p.sw1_body_w_x, p.sw1_body_w_y, p.sw1_body_h_z, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    sw_lugs = bd.Box(10.0, 8.5, p.sw1_lugs_h_z, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0.0, 0.0, p.sw1_body_h_z))
    sw_bush = bd.Cylinder(p.sw1_hole_dia / 2.0 - 0.05, 8.89, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX))
    sw_tool = bd.Compound([sw_body, sw_lugs, sw_bush])
    sw_max_vol = 0.0
    for zw in np.linspace(p.z_lid_bot_start + 25.0, p.z_lid_bot_start + p.sw1_wall_thick + 0.05, 15):
        inter = lid_bot & sw_tool.translate((p.sw1_x, p.sw1_y, float(zw)))
        sw_max_vol = max(sw_max_vol, float(inter.volume) if inter is not None else 0.0)

    # 2. Rev 4.8 Serviceable Assembly Sweep: ENTIRE pre-wired sub-assembly (MECH-LID-BOT + driver_pcb w/ 48 SMDs +
    #    mated 15 mm 90-deg USB-C plug + strain relief + SW1!) slides STRAIGHT UP into MECH-CAP-BOT in ONE vertical stroke!
    lid_subassy = bd.Compound([lid_bot, assy["pcb_assy"], assy["usbc_plug_assy"], assy["sw1_assy"]])
    sub_max_vol = 0.0
    for dz in np.linspace(-55.0, 0.0, 20):
        inter = cap_bot & lid_subassy.translate((0.0, 0.0, float(dz)))
        sub_max_vol = max(sub_max_vol, float(inter.volume) if inter is not None else 0.0)

    # 3. Pre-crimped 2-pin JST-XH plug (7.4 x 5.75 x 12 mm) straight vertical sweep through both ±Y wire channels!
    jst_plug_tool = bd.Box(7.4, 5.75, 12.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER))
    y_slot_c = p.core_pocket_w / 2.0 + p.core_wire_slot_d / 2.0 - 0.1
    jst_max_vol = 0.0
    for sy in (-1.0, 1.0):
        for zj in np.linspace(p.cap_bot_ceiling_z - 5.0, p.z_glass_bot + 10.0, 15):
            inter = cap_bot & jst_plug_tool.translate((0.0, sy * y_slot_c, float(zj)))
            jst_max_vol = max(jst_max_vol, float(inter.volume) if inter is not None else 0.0)

    # 4. ACTUAL 15 mm 90-deg USB-C L-plug passing straight through 16.5 x 14.5 mm lid port!
    plug90_pass_tool = bd.Box(p.usbc_plug_90_w, p.usbc_plug_90_h, 18.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER))
    port_max_vol = 0.0
    for zp in np.linspace(p.z_lid_bot_start - 15.0, p.z_lid_bot_end + 15.0, 15):
        inter = lid_bot & plug90_pass_tool.translate((p.clamp_x, p.clamp_y, float(zp)))
        port_max_vol = max(port_max_vol, float(inter.volume) if inter is not None else 0.0)

    return {
        "sw1_bottom_lid_insertion": {"waypoints_tested": 15, "max_intersection_vol_mm3": round(sw_max_vol, 6), "pass": sw_max_vol < 1e-4},
        "lid_pcb_usbc_straight_up_insertion": {"waypoints_tested": 20, "max_intersection_vol_mm3": round(sub_max_vol, 6), "pass": sub_max_vol < 1e-4},
        "jst_xh_plug_wire_slot_sweep": {"waypoints_tested": 30, "max_intersection_vol_mm3": round(jst_max_vol, 6), "pass": jst_max_vol < 1e-4},
        "usbc_90_plug_split_port_pass": {"waypoints_tested": 15, "max_intersection_vol_mm3": round(port_max_vol, 6), "pass": port_max_vol < 1e-4},
        "all_zero": (sw_max_vol < 1e-4) and (sub_max_vol < 1e-4) and (jst_max_vol < 1e-4) and (port_max_vol < 1e-4),
    }


def compute_mass_budget(mesh_checks: dict, assy_nom: dict[str, bd.Shape]) -> dict[str, float]:
    vol_printed_cm3 = (
        mesh_checks["mech_lid_bot"]["brep_volume_mm3"]
        + mesh_checks["mech_cap_bot"]["brep_volume_mm3"]
        + mesh_checks["mech_cap_top"]["brep_volume_mm3"]
        + mesh_checks["mech_plug_top"]["brep_volume_mm3"]
        + mesh_checks["mech_core_anchor"]["brep_volume_mm3"]
        + 2.0 * mesh_checks["mech_cable_clamp"]["brep_volume_mm3"]
        + 2.0 * mesh_checks["mech_hang_bushing"]["brep_volume_mm3"]
    ) / 1000.0
    asa_fdm_g = vol_printed_cm3 * 1.07 * 0.62
    petg_fdm_g = vol_printed_cm3 * 1.27 * 0.62
    al_core_g = (float(assy_nom["hs_core"].volume) / 1000.0) * 2.70
    pmma_shroud_g = (float(assy_nom["glass_tube"].volume) / 1000.0) * 1.18
    elec_stars_hw_g = 104.0

    return {
        "printed_lamp_volume_cm3": round(vol_printed_cm3, 1),
        "cap_bot_volume_cm3": round(mesh_checks["mech_cap_bot"]["brep_volume_mm3"] / 1000.0, 1),
        "cap_top_volume_cm3": round(mesh_checks["mech_cap_top"]["brep_volume_mm3"] / 1000.0, 1),
        "lid_bot_volume_cm3": round(mesh_checks["mech_lid_bot"]["brep_volume_mm3"] / 1000.0, 1),
        "asa_fdm_62pct_g": round(asa_fdm_g, 1),
        "petg_fdm_62pct_g": round(petg_fdm_g, 1),
        "al_core_3mm_g": round(al_core_g, 1),
        "uvt_pmma_shroud_g": round(pmma_shroud_g, 1),
        "elec_stars_hardware_g": elec_stars_hw_g,
        "total_fdm_asa_g": round(asa_fdm_g + al_core_g + pmma_shroud_g + elec_stars_hw_g, 1),
        "total_fdm_petg_g": round(petg_fdm_g + al_core_g + pmma_shroud_g + elec_stars_hw_g, 1),
    }


def main() -> None:
    out_dir = Path(__file__).resolve().parent
    pcb_path = out_dir.parents[1] / "pcb_design" / "driver_pcb" / "driver_pcb.kicad_pcb"

    p_fdm = LepiLEDParams(process="FDM")
    (out_dir / "cad_params.json").write_text(json.dumps(p_fdm.to_dict(), indent=2) + "\n")

    assy_nom = build_assembly_parts(p_fdm)
    drill_jig = build_drill_jig(p_fdm)
    clamp_half_export = build_cable_clamp_half(p_fdm, side=+1.0)
    bb_cl = clamp_half_export.bounding_box()
    clamp_half_print = clamp_half_export.translate((-0.5 * (bb_cl.min.X + bb_cl.max.X), -0.5 * (bb_cl.min.Y + bb_cl.max.Y), -bb_cl.min.Z))

    hang_bush_half = build_hang_bushing_half(p_fdm, side=+1.0)
    hang_bush_print = hang_bush_half.rotate(bd.Axis.Y, 90.0)
    bb_hb = hang_bush_print.bounding_box()
    hang_bush_print = hang_bush_print.translate((0.0, 0.0, -bb_hb.min.Z))

    mesh_checks = {
        "mech_lid_bot": export_and_verify_stl(assy_nom["lid_bot"], out_dir / "mech_lid_bot.step", out_dir / "mech_lid_bot.stl"),
        "mech_cap_bot": export_and_verify_stl(assy_nom["cap_bot"], out_dir / "mech_cap_bot.step", out_dir / "mech_cap_bot.stl"),
        "mech_cap_top": export_and_verify_stl(assy_nom["cap_top"], out_dir / "mech_cap_top.step", out_dir / "mech_cap_top.stl"),
        "mech_plug_top": export_and_verify_stl(assy_nom["plug_top"], out_dir / "mech_plug_top.step", out_dir / "mech_plug_top.stl"),
        "mech_core_anchor": export_and_verify_stl(assy_nom["core_anchor"], out_dir / "mech_core_anchor.step", out_dir / "mech_core_anchor.stl"),
        "mech_cable_clamp": export_and_verify_stl(clamp_half_print, out_dir / "mech_cable_clamp.step", out_dir / "mech_cable_clamp.stl"),
        "mech_hang_bushing": export_and_verify_stl(hang_bush_print, out_dir / "mech_hang_bushing.step", out_dir / "mech_hang_bushing.stl"),
        "mech_drill_jig": export_and_verify_stl(drill_jig, out_dir / "mech_drill_jig.step", out_dir / "mech_drill_jig.stl"),
    }

    comp_dir = out_dir / "parts_stl"
    comp_dir.mkdir(exist_ok=True)
    for old_f in comp_dir.glob("*.stl"):
        old_f.unlink()
    for name, shp in assy_nom.items():
        bd.export_stl(shp, str(comp_dir / f"{name}.stl"), tolerance=0.02, angular_tolerance=0.08)

    assy_compound = bd.Compound(list(assy_nom.values()))
    bd.export_step(assy_compound, str(out_dir / "lepiled_assembly.step"))

    overhang_checks = {
        "mech_lid_bot": audit_stl_overhangs(out_dir / "mech_lid_bot.stl", (0.0, 0.0, 1.0)),
        "mech_cap_bot": audit_stl_overhangs(out_dir / "mech_cap_bot.stl", (0.0, 0.0, -1.0), allowed_bridge_z=p_fdm.z_core_bot, allowed_bridge_xy=0.5 * p_fdm.core_pocket_w + 0.2),
        "mech_cap_top": audit_stl_overhangs(out_dir / "mech_cap_top.stl", (0.0, 0.0, 1.0)),
        "mech_plug_top": audit_stl_overhangs(out_dir / "mech_plug_top.stl", (0.0, 0.0, -1.0)),
        "mech_core_anchor": audit_stl_overhangs(out_dir / "mech_core_anchor.stl", (0.0, 0.0, -1.0)),
        "mech_cable_clamp": audit_stl_overhangs(out_dir / "mech_cable_clamp.stl", (0.0, 0.0, 1.0)),
        "mech_hang_bushing": audit_stl_overhangs(out_dir / "mech_hang_bushing.stl", (0.0, 0.0, 1.0)),
        "mech_drill_jig": audit_stl_overhangs(out_dir / "mech_drill_jig.stl", (0.0, 0.0, 1.0)),
    }

    breach_checks = check_shell_raycast_breaches(out_dir, p_fdm)
    seat_checks = check_fastener_seat_bearing(assy_nom["cap_bot"], assy_nom["cap_top"], assy_nom["lid_bot"], p_fdm)

    wc_glass_len = p_fdm.glass_length + p_fdm.glass_length_tol
    inter_nom = check_all_pairs_intersections(assy_nom)
    assy_wc = build_assembly_parts(
        p_fdm, core_w_override=p_fdm.core_w_max, glass_id_override=p_fdm.glass_id_min,
        glass_od_override=p_fdm.glass_od_max, glass_length_override=wc_glass_len,
    )
    inter_wc = check_all_pairs_intersections(assy_wc)
    kinematic_checks = check_kinematic_insertion(assy_nom, p_fdm)
    mass_budget = compute_mass_budget(mesh_checks, assy_nom)

    all_meshes_ok = all(m["is_watertight"] and m["is_winding_consistent"] and m["stl_volume_mm3"] > 0 for m in mesh_checks.values())
    all_overhangs_ok = all(o["pass"] for o in overhang_checks.values())
    all_breaches_ok = breach_checks["all_pass"]
    all_brep_ok = inter_nom["all_zero"] and inter_wc["all_zero"]
    all_kinematic_ok = kinematic_checks["all_zero"]
    all_seats_ok = seat_checks["all_pass"]
    all_param_checks_ok = all(c["pass"] for c in p_fdm.verify_all().values())

    report = {
        "revision": "Rev 4.8 (Field Lantern: Serviceable Lid-Mounted PCB, Sealed Lofted Collar, Staggered Anchor, Blind Conical Clamp & PETG/ASA Tolerance)",
        "input_hashes": {
            "params.py": _sha256_file(out_dir / "params.py"),
            "driver_pcb.kicad_pcb": _sha256_file(pcb_path),
        },
        "params": p_fdm.to_dict(),
        "mesh_checks": mesh_checks,
        "overhang_checks": overhang_checks,
        "raycast_breach_checks": breach_checks,
        "fastener_seat_bearing_checks": seat_checks,
        "kinematic_insertion_checks": kinematic_checks,
        "brep_all_pairs_nominal": {k: v for k, v in inter_nom.items() if k != "pairs"},
        "brep_all_pairs_worst_case": {k: v for k, v in inter_wc.items() if k != "pairs"},
        "mass_budget_g": mass_budget,
        "summary": {
            "all_param_checks_pass": all_param_checks_ok,
            "all_meshes_watertight_manifold": all_meshes_ok,
            "all_overhangs_le_46deg": all_overhangs_ok,
            "raycast_breach_checks_pass": all_breaches_ok,
            "fastener_seat_bearing_pass": all_seats_ok,
            "kinematic_insertion_zero": all_kinematic_ok,
            "nominal_all_pairs_zero": inter_nom["all_zero"],
            "worst_case_all_pairs_zero": inter_wc["all_zero"],
            "overall_pass": (
                all_param_checks_ok and all_meshes_ok and all_overhangs_ok
                and all_breaches_ok and all_seats_ok and all_brep_ok and all_kinematic_ok
            ),
        },
    }
    verif_path = out_dir / "cad_verification.json"
    verif_path.write_text(json.dumps(report, indent=2) + "\n")

    print("=== Mesh Verification (8 PETG/ASA-Agnostic FDM Parts) ===")
    for name, m in mesh_checks.items():
        print(f"  {name:18s}: vol={m['stl_volume_mm3']:8.1f} mm^3 | tri={m['triangles']:6d} | wt={m['is_watertight']} | wind={m['is_winding_consistent']} | euler={m['euler_number']:3d}")
    print("=== Overhang Verification ===")
    for name, o in overhang_checks.items():
        print(f"  {name:18s}: >46deg faces={o['off_bed_overhang_gt46_faces']:4d}, area={o['off_bed_overhang_gt46_area_mm2']:6.3f} mm^2, max={o['max_off_bed_overhang_deg']:5.2f} deg | pass={o['pass']}")
    print("=== Exterior-to-Interior Ray-Cast Wall-Breach Gate (NEW Rev 4.8!) ===")
    for k, v in breach_checks.items():
        if isinstance(v, dict):
            print(f"  {k:38s}: {v}")
    print("=== Positive Fastener-Seat Bearing & Intact Core-Socket Gate ===")
    for k, v in seat_checks.items():
        if isinstance(v, dict):
            print(f"  {k:38s}: {v}")
    print("=== Kinematic Insertion (SW1, ENTIRE Lid+PCB+15mm USB-C Straight Up, JST Slots) ===")
    for k in ("sw1_bottom_lid_insertion", "lid_pcb_usbc_straight_up_insertion", "jst_xh_plug_wire_slot_sweep", "usbc_90_plug_split_port_pass"):
        v = kinematic_checks[k]
        print(f"  {k:38s}: waypoints={v['waypoints_tested']:2d}, max_vol={v['max_intersection_vol_mm3']:.6f} mm^3 | pass={v['pass']}")
    print("=== All-Pairs B-Rep Intersection (incl. 14 Brass Inserts, Full-Length Screws, 48 SMDs & 15mm USB-C!) ===")
    for label, d in [("NOMINAL", inter_nom), ("WORST_CASE", inter_wc)]:
        print(f"  {label:10s}: {d['total_pairs_checked']} pairs, nonzero={d['nonzero_count']} {d['nonzero_pairs']}")
    print(f"=== Mass Budget: {mass_budget['total_fdm_petg_g']} g PETG / {mass_budget['total_fdm_asa_g']} g ASA | Height: {p_fdm.total_height_mm} mm | Chimney: {p_fdm.core_protrusion_mm} mm ===")
    if not all_param_checks_ok:
        for k, v in p_fdm.verify_all().items():
            if not v["pass"]:
                print(f"  PARAM FAIL: {k}: {v}")
    if not report["summary"]["overall_pass"]:
        raise SystemExit(1)
    print(f"Wrote {verif_path} and all Rev 4.8 STEP/STL artifacts (ALL CHECKS PASS).")


if __name__ == "__main__":
    main()
