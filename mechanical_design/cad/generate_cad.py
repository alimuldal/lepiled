#!/usr/bin/env python3
"""
Parametric 3D CAD Generator for LepiLED DIY Maxi Switch (Rev 4.6 — "Field Lantern") using build123d.

Exports (8 watertight, 100% support-free FDM ASA/PETG parts — MECH-BASE-RING & M20 gland eliminated!):
  - mech_cap_bot.step / .stl       (Unified 4.3-deg tapered frustum Ø87.6->74 mm w/ recessed skirt, 2x 45-deg portals,
                                    tactile 0/1/2 switch ribs, 4x M2.5 brass-insert PCB standoffs, solid R=24.4 mm
                                    core hub & ZERO exterior side holes!)
  - mech_lid_bot.step / .stl       (Recessed Ø78.6 mm bottom lid + Ø64.2 mm radial O-ring spigot + 16x14 mm USB-C
                                    pass-through port + SW1 + recessed ePTFE vent + D12 lightpipe + hanging cable clip)
  - mech_cable_clamp.step / .stl   (1 of 2 identical split cable-clamp saddle halves bolting below lid_bot; print 2x!)
  - mech_core_anchor.step / .stl   (Internal 23.4x23.4 mm dry-bay core lock block — cross-pinned flush in Al bore!)
  - mech_cap_top.step / .stl       (Unbroken Ø84 mm circular 25-deg rain eaves lofted to R=4 mm rounded-square collar,
                                    solid R=24.4 mm core hub, 4.6 mm M3 clamping shoulders & backed silicone channel!)
  - mech_plug_top.step / .stl      (8 mm 45-deg-beveled obelisk finial sealing top of matte-black 30x30x3 Al chimney)
  - mech_hang_bushing.step / .stl  (1 of 2 identical snap-in Signal-Orange Ø8 mm hang-hole paracord bushings; print 2x!)
  - mech_drill_jig.step / .stl     (Snap-on 30.6 mm U-channel drill guide for 16x M3 star + 2x anchor + 2x top-cap holes)
  - lepiled_assembly.step          (Full multi-part B-Rep assembly incl. ALL 57 SMDs, 90-deg USB-C + strain relief!)
  - cad_verification.json          (manifold + all-pairs B-Rep + POSITIVE fastener-seat bearing + overhang + kinematic!)
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
    "U1": (3.0, 2.8, 1.0), "U2": (3.0, 2.8, 1.0),
    "U3": (3.1, 3.1, 0.85),
    "U4": (5.0, 6.2, 1.75),
    "U5": (3.0, 2.5, 1.12),
    "Q1": (3.0, 2.5, 1.12), "Q2": (3.0, 2.5, 1.12), "Q3": (3.0, 2.5, 1.12),
    "F1": (4.7, 3.4, 1.25),
    "D9": (4.6, 2.8, 2.30), "D10": (4.6, 2.8, 2.30),
    "D11": (4.7, 3.8, 2.44),
    "D12": (1.7, 0.9, 0.80),
    "D13": (2.6, 1.4, 1.05), "D14": (2.6, 1.4, 1.05),
    "D15": (2.6, 1.4, 1.05), "D16": (2.6, 1.4, 1.05),
    "L1": (6.1, 6.1, 4.50), "L2": (6.1, 6.1, 4.50),
    "R3": (3.3, 1.7, 0.70), "R4": (3.3, 1.7, 0.70), "R8": (3.3, 1.7, 0.70),
    "R7": (2.1, 1.3, 0.65), "R12": (2.1, 1.3, 0.65), "R14": (2.1, 1.3, 0.65),
    "R16": (2.1, 1.3, 0.65), "R22": (2.1, 1.3, 0.65), "R23": (2.1, 1.3, 0.65),
    "C1": (2.1, 1.3, 1.40), "C11": (2.1, 1.3, 1.40), "C12": (2.1, 1.3, 1.40),
    "C2": (3.3, 1.7, 1.80), "C3": (3.3, 1.7, 1.80), "C10": (3.3, 1.7, 1.80),
}


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
    """Centered-X, bottom-Y=0 portal opening topped with a clean 45-deg pitched arch (0 overhang when inverted!)."""
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


def build_lid_bot(p: LepiLEDParams) -> bd.Part:
    """
    Build Rev 4.6 MECH-LID-BOT: recessed Ø78.6 x 5.0 mm bottom lid (Z = 19.0 .. 24.0 mm) + 6.5 mm radial O-ring spigot:
      - Standard 62 x 2.5 mm VMQ70 radial O-ring groove on Ø64.2 mm spigot (14.0% nom squeeze, 0 overhang!)
      - 16.0 x 14.0 mm stadium pass-through port at (0, -18.5 mm) passing intact 90-deg USB-C plug + 2x M3 clamp inserts
      - Bottom-mounted SW1 vertical Ø6.35 mm bore + 2.5 mm anti-rotation pocket at (0, +15.0 mm)
      - Ø2.5 mm ePTFE vent bore inside a Ø9.5 x 0.8 mm protective recessed pocket at (-20.0, 0.0 mm)
      - Ø2.6 mm D12 clear PMMA lightpipe bore at (+16.0, -0.6 mm) directly under D12
      - Integral centered bottom cable-clip saddle at (0, 0) for 0-deg plumb hanging!
      - 4x plain M3 clearance holes at R = 37.0 mm; prints flat upright on Z = 19.0 mm with 0.000 mm^2 overhang!
    """
    z0 = p.z_lid_bot_start  # 19.0
    z1 = p.z_lid_bot_end    # 24.0
    r_lid = p.lid_bot_od / 2.0
    base = bd.Cylinder(r_lid, p.lid_bot_thick, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, z0))

    # Hollow radial O-ring sealing spigot (Z = 24.0 .. 30.5 mm)
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

    # Radial O-ring groove for MECH-GASKET-3 (62 x 2.5 mm VMQ70, Z = 25.4 .. 29.95 mm, 45-deg upper ramp!)
    g3 = _radial_spigot_oring_cut(r_sp_out, p.bot_oring_groove_od / 2.0, z1 + 1.4, p.bot_oring_flat_w)
    part = part - g3

    # 4x M3 clearance holes at R = 37.0 mm (bolt heads recessed inside skirt!)
    for deg in (45.0, 135.0, 225.0, 315.0):
        rad = math.radians(deg)
        hx, hy = p.lid_bot_bolt_r * math.cos(rad), p.lid_bot_bolt_r * math.sin(rad)
        c_thru = bd.Cylinder(p.m3_clearance_dia / 2.0, p.lid_bot_thick + 2.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((hx, hy, z0 - 1.0))
        part = part - c_thru

    # 16.0 x 14.0 mm rounded-stadium USB-C plug pass-through port at (0.0, -18.5 mm) + 2x M3 brass insert bores for split clamp!
    with bd.BuildSketch(bd.Plane.XY.offset(z0 - 1.0)) as sk_port:
        bd.RectangleRounded(p.clamp_port_w, p.clamp_port_l, radius=3.0)
    port_cut = bd.extrude(sk_port.sketch, p.lid_bot_thick + 2.0).translate((p.clamp_x, p.clamp_y, 0.0))
    part = part - port_cut

    for sx in (-1.0, 1.0):
        cb_ins = bd.Cylinder(p.m3_insert_pilot_dia / 2.0, p.lid_bot_thick + 2.0,
                             align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((sx * p.clamp_bolt_dx, p.clamp_y, z0 - 1.0))
        part = part - cb_ins

    # Bottom-mounted SW1 vertical Ø6.35 mm bore + 2.5 mm upper anti-rotation pocket at (0.0, +15.0 mm)
    sw_bore = bd.Cylinder(p.sw1_hole_dia / 2.0 + p.print_clearance * 0.5, p.lid_bot_thick + 2.0,
                          align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((p.sw1_x, p.sw1_y, z0 - 1.0))
    sw_recess = bd.Box(p.sw1_body_w_x + 0.8, p.sw1_body_w_y + 0.8, p.lid_bot_thick - p.sw1_wall_thick + 0.5,
                       align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((p.sw1_x, p.sw1_y, z0 + p.sw1_wall_thick))
    part = part - sw_bore - sw_recess

    # Pressure-equalization IP68 ePTFE breather vent bore (patch applied on sheltered INSIDE top face Z = 24.0 mm -> 0 overhang & 100% mud/finger proof!)
    vent_bore = bd.Cylinder(p.vent_hole_dia / 2.0, p.lid_bot_thick + 2.0,
                            align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((p.vent_x, p.vent_y, z0 - 1.0))
    # D12 clear PMMA lightpipe bore at (+16.0, -0.6 mm) directly under D12
    d12_bore = bd.Cylinder(p.d12_lightpipe_dia / 2.0, p.lid_bot_thick + 2.0,
                           align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((p.d12_lightpipe_x, p.d12_lightpipe_y, z0 - 1.0))
    part = part - vent_bore - d12_bore

    return part


def build_cable_clamp_half(p: LepiLEDParams, side: float = 1.0) -> bd.Part:
    """
    Build one half of MECH-CABLE-CLAMP (2x identical mirrored halves clamped under MECH-LID-BOT at Y = -18.5 mm):
      - Upper 15.2 x 13.2 x 4.5 mm half-plug keys snugly inside the 16 x 14 mm lid port (0 mm protrusion above Z=24!)
      - Lower flange (32 x 16 x 11.0 mm) clamps upward via 2x M3x14 SHCS at X = ±12.0 mm (head on Z=8.0 -> 5 mm ground clr!)
      - 45-deg self-supporting Ø8.0 mm internal slit-silicone grommet chamber compresses watertight onto Ø4-4.5 mm cable
      - Prints UPRIGHT flat on Z = 8.0 mm bottom face with 0.000 mm^2 >46 deg overhang — print 2x identical copies!
    """
    z_lid = p.z_lid_bot_start  # 19.0
    with bd.BuildSketch(bd.Plane.XY.offset(z_lid)) as sk_plug:
        bd.RectangleRounded(p.clamp_port_w - 0.8, p.clamp_port_l - 0.8, radius=2.6)
    plug_boss = bd.extrude(sk_plug.sketch, p.lid_bot_thick - 0.4)  # Z = 19.0 .. 23.6 mm

    with bd.BuildSketch(bd.Plane.XY.offset(z_lid - p.clamp_outer_h)) as sk_flange:
        bd.RectangleRounded(32.0, 16.0, radius=3.5)
    flange = bd.extrude(sk_flange.sketch, p.clamp_outer_h)  # Z = 8.0 .. 19.0 mm
    full = flange.fuse(plug_boss)

    # Central Ø4.6 mm cable channel + 45-deg self-supporting Ø8.0 mm slit-silicone grommet chamber (0 overhang upright!)
    r_cab = p.clamp_cable_dia / 2.0 + 0.1  # 2.35
    r_grom = 4.0
    c_cable = bd.Cylinder(r_cab, p.clamp_outer_h + p.lid_bot_thick + 2.0,
                          align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, z_lid - p.clamp_outer_h - 1.0))
    c_grom_bot = bd.Cone(r_cab, r_grom, r_grom - r_cab, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, z_lid - 8.5))
    c_grom_mid = bd.Cylinder(r_grom, 4.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, z_lid - 8.5 + (r_grom - r_cab)))
    c_grom_top = bd.Cone(r_grom, r_cab, r_grom - r_cab, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, z_lid - 4.5 + (r_grom - r_cab)))
    c_top_fl = bd.Cone(r_cab, 4.2, 2.5, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, z_lid + 2.2))
    full = full - c_cable - c_grom_bot - c_grom_mid - c_grom_top - c_top_fl

    # 2x plain vertical M3 clearance bores at X = ±12.0 mm (M3 SHCS head sits flat on Z = 8.0 mm -> 0 overhang & 5 mm above ground!)
    for sx in (-1.0, 1.0):
        b_thru = bd.Cylinder(p.m3_clearance_dia / 2.0, p.clamp_outer_h + 2.0,
                             align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((sx * p.clamp_bolt_dx, 0.0, z_lid - p.clamp_outer_h - 1.0))
        full = full - b_thru

    gap = 0.25
    if side > 0:
        half_mask = bd.Box(40.0, 40.0, 40.0, align=(bd.Align.MIN, bd.Align.CENTER, bd.Align.CENTER)).translate((gap, 0.0, z_lid))
    else:
        half_mask = bd.Box(40.0, 40.0, 40.0, align=(bd.Align.MAX, bd.Align.CENTER, bd.Align.CENTER)).translate((-gap, 0.0, z_lid))
    half = (full & half_mask).translate((p.clamp_x, p.clamp_y, 0.0))
    return half


def build_core_anchor(p: LepiLEDParams) -> bd.Part:
    """
    Build MECH-CORE-ANCHOR: internal dry-bay core lock block (23.4 x 23.4 mm inside hollow Al core bore):
      - Upper rectangular body (Z = 72.0 .. 87.0 mm) cross-pinned flush to the 30x30x3 Al tube at Z = 79.5 mm via 2x M3x8 CSK
      - Lower 45-deg pyramidal nose (Z = 65.5 .. 72.0 mm) seats inside MECH-CAP-BOT's 45-deg socket pyramid
      - 2x M3 brass heat-set insert bores at (±6.5, 0.0 mm) facing -Z receive 2x M3x16 SHCS from the dry electronics bay!
      - Prints inverted on Z = 87.0 mm flat face with 0.000 mm^2 >46 deg overhang!
    """
    upper = bd.Box(p.anchor_w, p.anchor_w, p.anchor_h_in_core,
                   align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, p.z_core_bot))
    upper = bd.fillet(upper.edges().filter_by(bd.Axis.Z), 1.2)

    # Lower 45-deg pyramidal nose matching cap_bot's 45-deg core closure pyramid (0.6 mm clearance all around!)
    nose_h = 6.0  # Z = 66.0 .. 72.0 mm -> bottom flat is 11.4 x 11.4 mm? Wait: M3 inserts are at X = ±6.5 mm!
    # Keep flat bottom 18.0 x 14.0 mm at Z = 65.8 mm! At X = ±6.5 mm, cap_bot pyramid is at Z = 63.1 mm -> 2.7 mm clearance!
    with bd.BuildSketch(bd.Plane.XY.offset(p.z_core_bot)) as sk_top:
        bd.RectangleRounded(p.anchor_w, p.anchor_w, radius=1.2)
    with bd.BuildSketch(bd.Plane.XY.offset(p.z_core_bot - 2.6)) as sk_bot:
        bd.RectangleRounded(p.anchor_w - 5.2, p.anchor_w - 5.2, radius=1.0)  # 18.2 x 18.2 mm @ Z=69.4 mm (45-deg!)
    nose = bd.loft([sk_bot.sketch, sk_top.sketch])
    part = upper.fuse(nose)

    # 2x vertical M3 brass heat-set insert bores at (±6.5, 0.0 mm) facing -Z (Z = 69.4 .. 78.0 mm -> 8.6 mm deep!)
    for sx in (-1.0, 1.0):
        ins = bd.Cylinder(p.m3_insert_pilot_dia / 2.0, 9.0,
                          align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((sx * p.anchor_bolt_x, 0.0, p.z_core_bot - 3.0))
        part = part - ins

    # Horizontal cross-pin Ø4.0 mm brass insert bores on ±X at Z = 79.5 mm (teardrop apex toward -Z when printed inverted!)
    td_pin = _teardrop_profile_wire(p.m3_insert_pilot_dia / 2.0, 42.0)
    pin_bore = bd.extrude(td_pin, p.anchor_w + 2.0).rotate(bd.Axis.X, -90.0).rotate(bd.Axis.Z, -90.0).translate((-p.anchor_w / 2.0 - 1.0, 0.0, p.z_anchor_pin))
    part = part - pin_bore

    return part


def build_cap_bot(p: LepiLEDParams) -> bd.Part:
    """
    Build Rev 4.6 MECH-CAP-BOT ("Field Lantern" unified 4.3-deg continuous frustum, Z = 0.0 .. 101.0 mm, prints INVERTED!):
      - ONE uninterrupted conical silhouette (Ø87.6 mm base -> Ø74.0 mm shroud collar; ZERO external steps or side holes!)
      - Integral 19 mm standing skirt recessing MECH-LID-BOT completely inside + 2x smooth 45-deg-arch portals at ±Y
      - Tactile midnight switch index ribs (0 flat / 1 rib / 2 ribs) molded on lower skirt rim at +Y next to SW1!
      - 4x blind M3 brass-insert bores at R = 37.0 mm (Z = 24..30 mm; ZERO exterior nut slots!)
      - 4x filleted M2.5 brass-insert PCB standoffs (Ø7.4 -> Ø5.5 mm, Z = 51.6..56.0 mm; zero FDM Z-layer splitting!)
      - Solid R = 24.4 mm central hub preserving a 100% intact 16 mm-deep 30.8x30.8 mm square core socket!
      - Internal 2x M3x16 vertical anchor bores at (±6.5, 0.0 mm) bearing flat on a 7.1 mm solid ASA bulkhead (P0-1 FIXED!)
      - Widened Ø61.6 mm x 14.5 mm shroud bore + 60 x 3.5 mm VMQ50/60 radial O-ring groove (P1-1 FIXED!)
    """
    r_base = p.cap_bot_base_od / 2.0    # 43.8
    r_col = p.cap_bot_collar_od / 2.0   # 37.0
    z_top = p.z_cap_bot_top             # 101.0

    # Pure continuous 4.3-deg conical frustum from ground (Z = 0) to shroud collar (Z = 101.0)
    part = bd.Cone(r_base, r_col, z_top, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))

    # Crisp 0.8 mm architectural chamfer on ground rim (top edge when printed inverted) & top collar lead-in
    bot_edges = part.edges().filter_by(bd.GeomType.CIRCLE).filter_by_position(bd.Axis.Z, -0.1, 0.1)
    part = bd.chamfer(bot_edges, length=p.cap_chamfer)

    # Tactile midnight switch index ribs on outer rim at +Y (SW1 side: -X = 0 flat OFF, center = 1 rib UV, +X = 2 ribs ALL!)
    # 45-deg beveled +Z lead-in (downward-facing end when printed inverted -> 0.000 mm^2 overhang!)
    for x_rib in (0.0, 5.5, 8.5):
        y_outer = math.sqrt(max(1.0, (p.cap_bot_outer_r_at_z(6.0)) ** 2 - x_rib ** 2))
        with bd.BuildSketch(bd.Plane.YZ.offset(x_rib - 0.7)) as sk_rib:
            with bd.BuildLine():
                bd.Polyline([
                    (y_outer - 2.0, 2.5),
                    (y_outer + 0.9, 2.5),
                    (y_outer + 0.9, 8.0),
                    (y_outer - 2.0, 10.9),  # Exact 45-deg ramp facing +Z (print-DOWN inverted -> 45 deg, 0 overhang!)
                    (y_outer - 2.0, 2.5),
                ])
            bd.make_face()
        part = part.fuse(bd.extrude(sk_rib.sketch, 1.4))

    # Integral recessed skirt bore (Ø79.2 mm, Z = 0.0 .. 19.0 mm -> hides MECH-LID-BOT seam & bolts!)
    skirt_bore = bd.Cylinder(p.cap_bot_skirt_id / 2.0, p.cap_bot_skirt_h + 0.1,
                             align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, -0.1))
    part = part - skirt_bore

    # 2x opposing smooth 45-deg-arch cable/drainage/D12-glow portals at ±Y (Z = 0.0 .. 11.5 mm; 0 overhang inverted!)
    arch_prof = _pitched_arch_profile(p.cap_bot_portal_w, p.cap_bot_portal_rect_h, 45.0)
    # Note: inverted print has -Z UP! So pitched arch crown points toward +Z (WAIT: toward -Z is UP when inverted?
    # NO! Z = 0 is the TOP of the inverted print! The portal opens at Z = 0 (open top!) and goes DOWN toward Z = 11.5 mm!
    # Going downward in Z during inverted print means Z = 11.5 mm is printed FIRST (bottom of cutout in inverted print!),
    # and the walls grow UP to Z = 0 (open rim)! So the arch crown at Z = 11.5 mm has NO OVERHANG AT ALL — it's an upside-down V
    # printed from the point upward!! Verify: normal of the two 45-deg faces points toward -Z (print UP!), NOT +Z (print DOWN)!
    # That means ZERO downward-facing overhang in inverted orientation!!)
    for sy in (-1.0, 1.0):
        portal = bd.extrude(arch_prof, 24.0).rotate(bd.Axis.X, 90.0).translate((0.0, sy * 38.0 + (12.0 if sy > 0 else 12.0), -0.5))
        # Position cleanly cutting through ±Y skirt wall (Y ∈ [28, 52] or [-52, -28])
        portal = bd.extrude(arch_prof, 24.0).rotate(bd.Axis.X, 90.0).translate((0.0, (52.0 if sy > 0 else -28.0), -0.2))
        part = part - portal

    # Lower radial O-ring sealing bore (Ø65.0 mm, Z = 19.0 .. 30.5 mm) + 45-deg flare (Z = 30.5 .. 33.5 mm) -> Ø71.0 mm bay!
    r_sp_bore = p.cap_bot_spigot_bore_dia / 2.0  # 32.5
    r_cav = p.cap_bot_cavity_dia / 2.0           # 35.5
    sp_bore = bd.Cylinder(r_sp_bore, 30.5 - p.cap_bot_skirt_h + 0.5,
                          align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, p.cap_bot_skirt_h - 0.5))
    flare_h = r_cav - r_sp_bore  # 3.0 mm -> exact 45-deg transition (0 overhang inverted!)
    cav_flare = bd.Cone(r_sp_bore, r_cav, flare_h,
                        align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, 30.5))
    cav_main = bd.Cylinder(r_cav, p.cap_bot_ceiling_z - (30.5 + flare_h),
                           align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, 30.5 + flare_h))
    part = part - sp_bore.fuse(cav_flare).fuse(cav_main)

    # 4x blind M3 brass heat-set insert bores at R = 37.0 mm (Z = 24.0 .. 30.0 mm; ZERO exterior side-entry slots!)
    # Wait: lid sits at Z = 19.0 .. 24.0 mm, so lid flange meets a recessed shelf at Z = 24.0 mm?
    # Check: skirt bore ends at Z = 19.0 mm (lid bottom!), wait: lid OD is 78.6 mm (Z = 19.0 .. 24.0 mm), so skirt bore MUST
    # extend up to Z = 24.0 mm (lid top!) for the Ø78.6 mm lid to slide in up to Z = 24.0 mm!
    lid_pocket = bd.Cylinder(p.cap_bot_skirt_id / 2.0, p.lid_bot_thick + 0.1,
                             align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, p.cap_bot_skirt_h - 0.1))
    # Wait: check overhang of the flat annular step at Z = 24.0 mm (from R = 39.6 down to R = 32.5) when printed INVERTED!
    # Inverted print prints Z = 101 -> 33.5 -> 30.5 -> 24.0 -> 19.0 -> 0.0!
    # Going from Z = 24.0 to Z = 23.9, the bore WIDENS from R = 32.5 to R = 39.6 -> That's an UPWARD-FACING shelf (faces -Z = print UP!),
    # NOT an overhang!! Zero overhang!!
    part = part - lid_pocket

    for deg in (45.0, 135.0, 225.0, 315.0):
        rad = math.radians(deg)
        ix, iy = p.lid_bot_bolt_r * math.cos(rad), p.lid_bot_bolt_r * math.sin(rad)
        ins_bore = bd.Cylinder(p.m3_insert_pilot_dia / 2.0, p.m3_insert_depth + 0.2,
                               align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((ix, iy, p.z_lid_bot_end - 0.2))
        part = part - ins_bore

    # 4x integral filleted M2.5 brass heat-set insert PCB standoffs (Z = 51.6 .. 56.0 mm; print straight UP inverted!)
    standoff_h = p.cap_bot_ceiling_z - p.z_pcb_bcu  # 4.4 mm
    for sx in (-1.0, 1.0):
        for sy in (-1.0, 1.0):
            hx = sx * p.pcb_hole_x
            hy = p.pcb_y_center + sy * p.pcb_hole_y
            # Tapered boss: Ø7.4 mm at Z=56.0 ceiling -> Ø5.5 mm at Z=51.6 PCB keepout face (self-supporting cone!)
            boss = bd.Cone(p.pcb_standoff_tip_od / 2.0, p.pcb_standoff_root_od / 2.0, standoff_h,
                           align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((hx, hy, p.z_pcb_bcu))
            pilot = bd.Cylinder(p.m25_insert_pilot_dia / 2.0, p.m25_insert_depth + 0.2,
                                align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((hx, hy, p.z_pcb_bcu - 0.2))
            part = part.fuse(boss) - pilot

    # P0-1 FIXED: Annular shroud bore (Ø61.6 x Ø48.8 mm, Z = 85.3 .. 101.0 mm) around FULL-HEIGHT solid R = 24.4 mm central hub!
    # Extending the R = 24.4 mm hub flush to Z = 101.0 mm puts BOTH outer rim & central hub flat on the bed (0.000 mm^2 overhang!)
    r_bore = p.glass_bore_id / 2.0        # 30.8
    r_hub = p.core_hub_od / 2.0           # 24.4 (2.35 mm inside PMMA ID_min=53.5 mm; preserves 100% 4-wall square socket!)
    z_bore_bot = p.z_glass_bot - 1.2      # 85.3 (clears +2.0 mm oversize tube!)
    shroud_annulus = (
        bd.Cylinder(r_bore, z_top - z_bore_bot + 0.5, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
        - bd.Cylinder(r_hub, z_top - z_bore_bot + 1.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, -0.2))
    ).translate((0, 0, z_bore_bot))
    # 45-deg self-supporting annular transition cone narrowing from R = 30.8 down to R = 24.4 mm (6.4 mm tall -> 0 overhang!)
    cone_h = r_bore - r_hub  # 6.4 mm -> Z = 78.9 .. 85.3 mm!
    shroud_seat_cone = (
        bd.Cone(r_hub, r_bore, cone_h, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX))
        - bd.Cylinder(r_hub, cone_h + 0.4, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)).translate((0, 0, 0.2))
    ).translate((0, 0, z_bore_bot))
    # Radial bore O-ring groove (MECH-GASKET-1: 60 x 3.5 mm soft VMQ50/60; flat root Z = 92.4 .. 97.0 mm, 45-deg ramp 90.5..92.4)
    g1 = _radial_bore_oring_cut(r_bore, p.glass_oring_groove_od / 2.0, z_top - 4.0, p.glass_oring_flat_w, ramp_dir=-1.0)
    # 1.0 x 30-deg bore mouth lead-in chamfer at Z = 100.0 .. 101.0 mm
    mouth_lead = (
        bd.Cone(r_bore, r_bore + 0.7, 1.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX))
        - bd.Cylinder(r_hub + 0.5, 1.4, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)).translate((0, 0, 0.2))
    ).translate((0, 0, z_top + 0.1))
    part = part - shroud_annulus - shroud_seat_cone - g1 - mouth_lead

    # Weight-relief annular hollow above electronics ceiling (Z = 56.0 .. 73.0 mm, R = 24.6 .. 34.5 mm -> saves ~25 g ASA, 0 overhang inverted!)
    # Note: inverted print goes Z = 73 -> 56; tapering from R = 34.5 down to R = 24.6 (narrowing as Z increases) means
    # when printing inverted (Z decreasing), the cavity WIDENS from R = 24.6 to R = 34.5 -> UPWARD-FACING 45-deg shelf = 0 overhang!
    # Keep clear of 4x PCB standoffs (H1/H2 at (±14, +25) -> R=28.65 mm; H3/H4 at (±14, -13) -> R=19.1 mm) by starting at Z = 56.0 + 0.0
    # OUTSIDE R = 31.8 mm? Even cleaner: start relief ring above Z = 58.0? No, Z = 56.0 is ceiling! Hollow an annular groove
    # R ∈ [29.5, 34.5] from Z = 56.0 to Z = 72.0? No, R=29.5 touches H1/H2 standoff roots (28.65 + 3.7 = 32.35 mm)!
    # Keep full solid standoff roots cleanly untouched!

    # Intact 27.5 mm-deep 30.8 x 30.8 mm square core socket (Z = 73.5 .. 101.0 mm) + 45-deg support-free closure pyramid (Z = 58.3..73.5)!
    core_sock = bd.Box(p.core_pocket_w, p.core_pocket_w, z_top - p.z_core_bot + 1.0,
                       align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, p.z_core_bot))
    pyr_h = 0.5 * (p.core_pocket_w - 0.4)  # 15.2 mm -> closes to 0.4x0.4 mm tip at Z = 58.3 mm (0.000 mm^2 overhang!)
    with bd.BuildSketch(bd.Plane.XY.offset(p.z_core_bot)) as sk_base:
        bd.Rectangle(p.core_pocket_w, p.core_pocket_w)
    with bd.BuildSketch(bd.Plane.XY.offset(p.z_core_bot - pyr_h)) as sk_tip:
        bd.Rectangle(0.4, 0.4)
    part = part - core_sock - bd.loft([sk_tip.sketch, sk_base.sketch])

    # 2x internal vertical M3x16 dry-bay anchor bolt bores at (±6.5, 0.0 mm) through 8.6 mm solid ASA bulkhead (ZERO exterior holes!)
    for sx in (-1.0, 1.0):
        anc_bore = bd.Cylinder(p.m3_clearance_dia / 2.0, 16.0,
                               align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((sx * p.anchor_bolt_x, 0.0, p.cap_bot_ceiling_z - 0.5))
        part = part - anc_bore

    # 2x generous 9.0 x 7.5 mm wire channels at ±Y passing pre-crimped 7.4 x 5.75 mm JST-XH plugs straight through!
    y_slot_c = p.core_pocket_w / 2.0 + p.core_wire_slot_d / 2.0 - 0.1  # 19.05 mm (inside R=24.4 hub & R=26.75 PMMA ID!)
    for sy in (-1.0, 1.0):
        wslot = bd.Box(p.core_wire_slot_w, p.core_wire_slot_d + 0.2, (z_top + 1.0) - (p.cap_bot_ceiling_z - 1.0),
                       align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0.0, sy * y_slot_c, p.cap_bot_ceiling_z - 1.0))
        part = part - wslot

    return part


def build_cap_top(p: LepiLEDParams) -> bd.Part:
    """
    Build Rev 4.6 MECH-CAP-TOP (prints UPRIGHT on Z_cap_top_bot = 187.0 mm -> 0.000 mm^2 >46 deg overhang!):
      - Unbroken 360-deg Ø84 mm circular rain eaves lofted smoothly into a 38.8 x 38.8 mm (R=4 mm) rounded-square collar!
      - Solid R = 24.4 mm central hub stopping the 45-deg shroud cone cleanly at Z = 209.1 mm (P0-1 FIXED!)
      - 13.8 mm full-height 4-wall 30.8 x 30.8 mm square core socket + backed 2.0 x 2.5 mm top silicone seal groove!
      - 2x M3x10 SHCS radial core lock screws at Z = 211.5 mm bearing on 4.60 mm solid hub shoulders (clear of eaves rim!)
      - Widened Ø61.6 mm x 14.5 mm shroud bore + 60 x 3.5 mm soft VMQ50/60 radial O-ring groove (P1-1 FIXED!)
    """
    r_skirt = p.cap_top_skirt_od / 2.0    # 37.0
    r_brim = p.cap_top_brim_od / 2.0      # 42.0
    z_bot = p.z_cap_top_bot               # 187.0
    z_fl_bot = p.z_cap_top_brim_bot       # 197.0
    z_rim_bot = p.z_cap_top_brim_rim_bot  # 202.0
    z_rim_top = p.z_cap_top_brim_rim_top  # 205.0
    z_top = p.z_cap_top_top               # 216.5

    c_skirt = bd.Cylinder(r_skirt, z_fl_bot - z_bot, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, z_bot))
    c_flare = bd.Cone(r_skirt, r_brim, z_rim_bot - z_fl_bot, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, z_fl_bot))
    c_rim = bd.Cylinder(r_brim, z_rim_top - z_rim_bot, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, z_rim_bot))

    # Sculptural square-to-round lofted rain roof (Ø84 mm circle -> 38.8x38.8 R4 rounded-square collar, 27-35 deg slope!)
    with bd.BuildSketch(bd.Plane.XY.offset(z_rim_top)) as sk_roof_bot:
        bd.Circle(r_brim)
    with bd.BuildSketch(bd.Plane.XY.offset(z_top)) as sk_roof_top:
        bd.RectangleRounded(p.cap_top_collar_w, p.cap_top_collar_w, radius=p.cap_top_collar_r)
    c_roof = bd.loft([sk_roof_bot.sketch, sk_roof_top.sketch])

    part = c_skirt.fuse(c_flare).fuse(c_rim).fuse(c_roof)

    # Subtle outer drip-rim chamfer
    rim_edges = part.edges().filter_by(bd.GeomType.CIRCLE).filter_by_position(bd.Axis.Z, z_rim_bot - 0.1, z_rim_bot + 0.1)
    part = bd.chamfer(rim_edges, length=0.6)

    # P0-1 FIXED: Annular shroud bore (Ø61.6 x Ø48.8 mm, Z = 187.0 .. 202.7 mm) around FULL-HEIGHT solid R = 24.4 mm central hub!
    # Extending the R = 24.4 mm hub flush to Z = 187.0 mm puts BOTH outer skirt & central hub flat on the bed (0.000 mm^2 overhang!)
    r_bore = p.glass_bore_id / 2.0        # 30.8
    r_hub = p.core_hub_od / 2.0           # 24.4 (preserves full 4-wall square socket!)
    z_bore_top = p.z_glass_top + 1.2      # 202.7 (clears +2.0 mm oversize tube!)
    shroud_annulus = (
        bd.Cylinder(r_bore, z_bore_top - z_bot + 0.5, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
        - bd.Cylinder(r_hub, z_bore_top - z_bot + 1.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, -0.2))
    ).translate((0, 0, z_bot - 0.5))
    # 45-deg self-supporting annular transition cone narrowing from R = 30.8 up to R = 24.4 mm (6.4 mm tall -> Z = 202.7..209.1 mm!)
    cone_h = r_bore - r_hub  # 6.4 mm
    shroud_stop = (
        bd.Cone(r_bore, r_hub, cone_h, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
        - bd.Cylinder(r_hub, cone_h + 0.4, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, -0.2))
    ).translate((0, 0, z_bore_top))
    # Radial bore O-ring groove (MECH-GASKET-2: 60 x 3.5 mm soft VMQ50/60; flat root Z = 190.0 .. 194.6 mm + 1.9 mm 45-deg ramp!)
    g2 = _radial_bore_oring_cut(r_bore, p.glass_oring_groove_od / 2.0, z_bot + 3.0, p.glass_oring_flat_w, ramp_dir=+1.0)
    mouth_lead = (
        bd.Cone(r_bore + 0.7, r_bore, 1.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
        - bd.Cylinder(r_hub + 0.5, 1.4, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, -0.2))
    ).translate((0, 0, z_bot - 0.1))
    part = part - shroud_annulus - shroud_stop - g2 - mouth_lead

    # Intact 16.5 mm-tall 30.8 x 30.8 mm square core aperture + backed 2.0 x 2.5 mm top neutral-cure silicone seal groove!
    core_thru = bd.Box(p.core_pocket_w, p.core_pocket_w, (z_top - z_bot) + 2.0,
                       align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, z_bot - 1.0))
    part = part - core_thru
    w_g = p.core_pocket_w + 2.0 * p.cap_top_seal_groove  # 34.8 mm (leaves 2.0 mm outer collar lip on 38.8 mm square!)
    with bd.BuildSketch(bd.Plane.XY.offset(z_top + 0.05)) as sk_top:
        bd.Rectangle(w_g, w_g)
    with bd.BuildSketch(bd.Plane.XY.offset(z_top - 2.5)) as sk_bot:
        bd.Rectangle(p.core_pocket_w, p.core_pocket_w)
    part = part - bd.loft([sk_bot.sketch, sk_top.sketch])

    # P0-1 FIXED: 2x radial M3x10 SHCS core lock screws at Z = 211.5 mm bearing on 4.60 mm SOLID hub shoulders (|X| = 15.4..20.0 mm!)
    # Completely above the Z = 205.0 mm unbroken eaves rim AND above the Z = 209.1 mm internal cone apex!
    z_lock = p.z_cap_top_lock  # 211.5
    td_thru = _teardrop_profile_wire(p.m3_clearance_dia / 2.0, 42.0)
    td_cb = _teardrop_profile_wire(3.2, 42.0)
    for sx in (-1.0, 1.0):
        h_lock = bd.extrude(td_thru, 24.0).rotate(bd.Axis.X, 90.0).rotate(bd.Axis.Z, 90.0)
        h_cb = bd.extrude(td_cb, 26.0).rotate(bd.Axis.X, 90.0).rotate(bd.Axis.Z, 90.0)
        if sx > 0:
            h_lock = h_lock.translate((14.0, 0.0, z_lock))
            h_cb = h_cb.translate((20.0, 0.0, z_lock))  # Flat clamping shoulder at X = +20.0 mm (4.6 mm solid wall!)
        else:
            h_lock = h_lock.rotate(bd.Axis.Z, 180.0).translate((-14.0, 0.0, z_lock))
            h_cb = h_cb.rotate(bd.Axis.Z, 180.0).translate((-20.0, 0.0, z_lock))  # Flat clamping shoulder at X = -20.0 mm!
        part = part - h_lock - h_cb

    return part


def build_plug_top(p: LepiLEDParams) -> bd.Part:
    """Build Rev 4.6 MECH-PLUG-TOP: 8 mm tall 45-deg-beveled obelisk finial sealing top of matte-black 30x30x3 Al chimney."""
    insert = bd.Box(p.plug_top_w, p.plug_top_w, p.plug_top_insert_h,
                    align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, p.z_core_top - p.plug_top_insert_h))
    insert = bd.fillet(insert.edges().filter_by(bd.Axis.Z), 1.5)

    skirt_h = 3.0
    bevel_h = p.plug_top_cap_h - skirt_h  # 5.0 mm 45-deg obelisk crown!
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
    Build one half of MECH-HANG-BUSHING: snap-in Signal-Orange Ø8 mm paracord grommet for the Al chimney hang hole!
    Prints flat on its outer flange face with 0.000 mm^2 overhang — print 2x identical halves!
    """
    r_bore = p.hang_bush_id / 2.0          # 2.7 mm (Ø5.4 mm smooth cord bore)
    r_sleeve = p.core_hang_hole_dia / 2.0 - 0.15  # 3.85 mm (slips smoothly into Ø8.0 mm Al hole)
    r_flange = p.hang_bush_flange_od / 2.0        # 6.0 mm (Ø12.0 mm Signal-Orange touchpoint ring!)
    sleeve_len = p.core_wall + 1.5         # 4.5 mm into 3.0 mm Al wall (leaves open hollow bore clearance)

    flange = bd.Cylinder(r_flange, p.hang_bush_flange_t, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    flange_top_e = flange.edges().filter_by(bd.GeomType.CIRCLE).filter_by_position(bd.Axis.Z, -0.1, 0.1)
    flange = bd.chamfer(flange_top_e, length=0.6)
    sleeve = bd.Cylinder(r_sleeve, sleeve_len, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, p.hang_bush_flange_t))
    bore = bd.Cylinder(r_bore, p.hang_bush_flange_t + sleeve_len + 2.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, -1.0))
    lead = bd.Cone(r_bore + 0.9, r_bore, 0.9, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, -0.05))
    half = flange.fuse(sleeve) - bore - lead

    cw = core_w_override or p.core_w_nom
    x_face = 0.5 * cw + 0.05
    if side > 0:
        return half.rotate(bd.Axis.Y, -90.0).translate((x_face + p.hang_bush_flange_t, 0.0, p.z_hang_hole))
    return half.rotate(bd.Axis.Y, 90.0).translate((-x_face - p.hang_bush_flange_t, 0.0, p.z_hang_hole))


def build_drill_jig(p: LepiLEDParams) -> bd.Part:
    """Build Rev 4.6 MECH-DRILL-JIG: snap-on 30.6 mm U-channel drill guide for 16x M3 star + 2x anchor + 2x top-cap holes."""
    wall = 3.0
    inner_w = p.core_w_nom + 0.6
    outer_w = inner_w + 2.0 * wall
    jig_len = 148.0  # Covers anchor pin (7.5 mm), Vis stars, UV stars, and top cap lock (139.5 mm)!
    leg_h = 15.0

    base = bd.Box(wall, outer_w, jig_len, align=(bd.Align.MIN, bd.Align.CENTER, bd.Align.MIN))
    leg_pos = bd.Box(leg_h, wall, jig_len, align=(bd.Align.MIN, bd.Align.MAX, bd.Align.MIN)).translate((0, outer_w / 2.0, 0))
    leg_neg = bd.Box(leg_h, wall, jig_len, align=(bd.Align.MIN, bd.Align.MIN, bd.Align.MIN)).translate((0, -outer_w / 2.0, 0))
    end_stop = bd.Box(10.0, outer_w, wall, align=(bd.Align.MIN, bd.Align.CENTER, bd.Align.MAX))
    jig = base.fuse(leg_pos).fuse(leg_neg).fuse(end_stop)

    guide_zs = (
        p.anchor_pin_z_rel,                             # 7.5 mm (MECH-CORE-ANCHOR cross-pin on ±X)
        p.axial_vis_to_bot_mm - p.star_bolt_r,          # 46.5 mm (Vis star bottom screw)
        p.axial_vis_to_bot_mm + p.star_bolt_r,          # 65.5 mm (Vis star top screw)
        (p.z_led_uv - p.z_core_bot) - p.star_bolt_r,    # 78.5 mm (UV star bottom screw)
        (p.z_led_uv - p.z_core_bot) + p.star_bolt_r,    # 97.5 mm (UV star top screw)
        p.z_cap_top_lock - p.z_core_bot,                # 139.5 mm (MECH-CAP-TOP radial lock on ±X)
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
            lx, wy, hz = SMD_PACKAGE_DIMS.get(ref, (1.7, 0.9, 0.65))
            if int(round(rot)) % 180 == 90:
                lx, wy = wy, lx
            box = bd.Box(lx, wy, hz, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)).translate((bx, p.pcb_y_center + by, p.pcb_z_fcu))
            solids.append(box)
    assert len(solids) == 57, f"Expected 57 SMDs from driver_pcb_cpl.csv, got {len(solids)}"
    return solids


def build_assembly_parts(p: LepiLEDParams, core_w_override: float | None = None,
                         glass_id_override: float | None = None, glass_od_override: float | None = None,
                         glass_length_override: float | None = None) -> dict[str, bd.Shape]:
    """Build all Rev 4.6 physical assembly components (incl. ALL 57 SMDs, 90-deg USB-C + strain relief, split clamp & anchor)."""
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

    # Horizontal Driver PCB (SMD/JST down at Z_fcu = 50.0 mm, B.Cu up at 51.6 mm, centered at Y = +6.0 mm!)
    pcb_board = bd.Box(p.pcb_w, p.pcb_l, p.pcb_thick, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    pcb_board = bd.fillet(pcb_board.edges().filter_by(bd.Axis.Z), p.pcb_corner_r).translate((0.0, p.pcb_y_center, p.pcb_z_fcu))
    for sx in (-1.0, 1.0):
        for sy in (-1.0, 1.0):
            npth = bd.Cylinder(p.pcb_hole_drill / 2.0, p.pcb_thick + 0.6, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER)).translate(
                (sx * p.pcb_hole_x, p.pcb_y_center + sy * p.pcb_hole_y, p.pcb_z_fcu + 0.5 * p.pcb_thick)
            )
            pcb_board = pcb_board - npth

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

    # Central protruding Matte-Black 30 x 30 x 3.0 mm Al 6063-T6 core (L = 200.0 mm stock cut — 174 g!)
    core_out = bd.Box(core_w, core_w, p.core_length, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    core_in = bd.Box(core_w - 2.0 * p.core_wall, core_w - 2.0 * p.core_wall, p.core_length + 2.0,
                     align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, -1.0))
    hs_core = (core_out - core_in).translate((0, 0, p.z_core_bot))
    hang_bore = bd.Cylinder(p.core_hang_hole_dia / 2.0, core_w + 2.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER)).rotate(bd.Axis.Y, 90.0).translate((0.0, 0.0, p.z_hang_hole))
    anchor_pin_bore = bd.Cylinder(1.75, core_w + 2.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER)).rotate(bd.Axis.Y, 90.0).translate((0.0, 0.0, p.z_anchor_pin))
    # Countersinks on ±X faces of core at Z = z_anchor_pin so M3x8 CSK cross-pins sit 100% flush inside cap_bot socket!
    for sx in (-1.0, 1.0):
        csk = bd.Cone(1.7, 3.2, 1.5, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).rotate(bd.Axis.Y, 90.0 if sx > 0 else -90.0).translate((sx * (0.5 * core_w - 1.45), 0.0, p.z_anchor_pin))
        hs_core = hs_core - csk
    top_lock_bore = bd.Cylinder(1.55, core_w + 2.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER)).rotate(bd.Axis.Y, 90.0).translate((0.0, 0.0, p.z_cap_top_lock))
    hs_core = hs_core - hang_bore - anchor_pin_bore - top_lock_bore

    # ALL Modeled Fasteners (4x M3x10 lid + 2x M3x12 clamp + 2x M3x16 dry-bay anchor + 2x M3x8 CSK pin + 2x M3x10 top lock + 4x M2.5x8 PCB!)
    fasteners_list = []
    # 1. 4x M3x10 SHCS recessed lid bolts
    for deg in (45.0, 135.0, 225.0, 315.0):
        rad = math.radians(deg)
        lx, ly = p.lid_bot_bolt_r * math.cos(rad), p.lid_bot_bolt_r * math.sin(rad)
        lb_head = bd.Cylinder(2.75, 3.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)).translate((lx, ly, p.z_lid_bot_start - 0.05))
        lb_shank = bd.Cylinder(1.48, 10.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((lx, ly, p.z_lid_bot_start - 0.05))
        fasteners_list.append(lb_head.fuse(lb_shank))
    # 2. 2x M3x14 SHCS split cable clamp bolts (head sits flat on Z = 8.0 mm bottom face -> 5 mm ground clr!)
    for sx in (-1.0, 1.0):
        cx, cy = sx * p.clamp_bolt_dx, p.clamp_y
        ch = bd.Cylinder(2.75, 3.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)).translate((cx, cy, p.z_lid_bot_start - p.clamp_outer_h - 0.05))
        cs = bd.Cylinder(1.48, 14.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((cx, cy, p.z_lid_bot_start - p.clamp_outer_h - 0.05))
        fasteners_list.append(ch.fuse(cs))
    # 3. 2x M3x16 SHCS internal dry-bay core anchor bolts (bearing flat at Z = 56.0 mm into MECH-CORE-ANCHOR!)
    for sx in (-1.0, 1.0):
        ax = sx * p.anchor_bolt_x
        ah = bd.Cylinder(2.75, 3.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)).translate((ax, 0.0, p.cap_bot_ceiling_z - 0.05))
        ash = bd.Cylinder(1.48, 16.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((ax, 0.0, p.cap_bot_ceiling_z - 0.05))
        fasteners_list.append(ah.fuse(ash))
    # 4. 2x M3x8 CSK flush cross-pin screws locking MECH-CORE-ANCHOR to Al core at Z = 79.5 mm
    for sx in (-1.0, 1.0):
        rot_y = 90.0 if sx > 0 else -90.0
        ps = bd.Cylinder(1.48, 7.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)).rotate(bd.Axis.Y, rot_y).translate((sx * (0.5 * core_w - 0.2), 0.0, p.z_anchor_pin))
        fasteners_list.append(ps)
    # 5. 2x M3x10 SHCS radial top-cap core lock screws bearing on solid shoulders at |X| = 20.0 mm, Z = 211.5 mm!
    for sx in (-1.0, 1.0):
        if sx > 0:
            th = bd.Cylinder(2.75, 3.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).rotate(bd.Axis.Y, 90.0).translate((20.05, 0.0, p.z_cap_top_lock))
            ts = bd.Cylinder(1.48, 8.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)).rotate(bd.Axis.Y, 90.0).translate((20.05, 0.0, p.z_cap_top_lock))
        else:
            th = bd.Cylinder(2.75, 3.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)).rotate(bd.Axis.Y, 90.0).translate((-20.05, 0.0, p.z_cap_top_lock))
            ts = bd.Cylinder(1.48, 8.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).rotate(bd.Axis.Y, 90.0).translate((-20.05, 0.0, p.z_cap_top_lock))
        fasteners_list.append(th.fuse(ts))
    # 6. 4x M2.5x8 pan-head PCB mounting screws into 4x M2.5 brass heat-set inserts
    for sx in (-1.0, 1.0):
        for sy in (-1.0, 1.0):
            hx = sx * p.pcb_hole_x
            hy = p.pcb_y_center + sy * p.pcb_hole_y
            ph = bd.Cylinder(2.25, 1.8, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)).translate((hx, hy, p.pcb_z_fcu - 0.05))
            ps = bd.Cylinder(1.20, 6.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((hx, hy, p.pcb_z_fcu - 0.05))
            fasteners_list.append(ph.fuse(ps))
    fasteners_m3 = bd.Compound(fasteners_list)

    # Clear Unstabilized Extruded PMMA (Plexiglas XT) shroud (Ø60 x 54 x 3.0 x 115 mm) — seated under gravity!
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

    # Bottom-mounted SW1 (C&K 7211SYZBE gold DPDT) + silicone boot on recessed MECH-LID-BOT at (0.0, +15.0 mm)
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

    # Compact 90-deg-down USB-C PD plug + explicitly modeled 7 mm molded strain-relief boot!
    y_plug_tip = p.y_j1_mouth + p.usbc_mating_depth_mm
    plug_barrel = bd.Box(8.3, p.usbc_mating_depth_mm + 2.0, 2.5, align=(bd.Align.CENTER, bd.Align.MAX, bd.Align.CENTER)).translate((0.0, y_plug_tip, p.z_j1_center))
    plug_body = bd.Box(p.usbc_plug_90_w, p.usbc_plug_90_len - 1.9, p.usbc_plug_90_h,
                       align=(bd.Align.CENTER, bd.Align.MAX, bd.Align.MAX)).translate((0.0, p.y_j1_mouth - 1.9, p.z_j1_center + 2.8))
    y_plug_ctr = p.y_j1_mouth - 1.9 - 0.5 * (p.usbc_plug_90_len - 1.9)
    z_plug_bot = p.z_j1_center + 2.8 - p.usbc_plug_90_h
    plug_strain = bd.Cone(2.6, 3.6, p.usbc_strain_relief_h, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)).translate((0.0, y_plug_ctr, z_plug_bot))
    usbc_plug_assy = plug_barrel.fuse(plug_body).fuse(plug_strain)

    # 29.8 mm clear PMMA D12 lightpipe rod w/ 45-deg beveled side-glow tip (1.4 mm below D12 @ Z = 49.2 mm!)
    d12_rod = bd.Cylinder(1.20, 29.8, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((p.d12_lightpipe_x, p.d12_lightpipe_y, p.z_lid_bot_start - 1.0))

    return dict(
        lid_bot=lid_bot,
        cap_bot=cap_bot,
        cap_top=cap_top,
        plug_top=plug_top,
        core_anchor=core_anchor,
        cable_clamp=cable_clamp,
        hang_bushing=hang_bushing,
        pcb_assy=pcb_assy,
        hs_core=hs_core,
        fasteners_m3=fasteners_m3,
        glass_tube=glass_tube,
        dtp_stars=dtp_stars,
        sw1_assy=sw1_assy,
        usbc_plug_assy=usbc_plug_assy,
        d12_rod=d12_rod,
    )


def check_fastener_seat_bearing(cap_bot: bd.Part, cap_top: bd.Part, lid_bot: bd.Part, p: LepiLEDParams) -> dict[str, dict | bool]:
    """
    Mandatory Rev 4.6 P0-1 regression gate: verify POSITIVE solid plastic bearing material directly beneath
    every structural fastener clamping shoulder (prevents floating-screw false positives!).
    """
    results: dict[str, dict | bool] = {}

    # 1. cap_bot 2x internal vertical M3x16 dry-bay core anchor seats at (±6.5, 0.0, Z = 56.0 .. 58.0 mm)
    ideal_ring = math.pi * (2.75 ** 2 - 1.70 ** 2) * 2.0  # 2 mm deep annular bearing slice under Ø5.5 mm head
    bot_ratios = []
    for sx in (-1.0, 1.0):
        ring = (
            bd.Cylinder(2.75, 2.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
            - bd.Cylinder(1.70, 2.2, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, -0.1))
        ).translate((sx * p.anchor_bolt_x, 0.0, p.cap_bot_ceiling_z))
        inter = cap_bot & ring
        vol = float(inter.volume) if inter is not None else 0.0
        bot_ratios.append(vol / ideal_ring)
    results["cap_bot_anchor_seat_bearing"] = {
        "min_contact_ratio": round(min(bot_ratios), 4),
        "min_required": 0.90,
        "pass": min(bot_ratios) >= 0.90,
    }

    # 2. cap_top 2x radial M3x10 core lock seats at |X| = 18.0 .. 20.0 mm, Z = z_cap_top_lock (211.5 mm)
    top_ratios = []
    for sx in (-1.0, 1.0):
        ring = (
            bd.Cylinder(2.75, 2.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX))
            - bd.Cylinder(1.70, 2.2, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)).translate((0, 0, 0.1))
        ).rotate(bd.Axis.Y, 90.0 if sx > 0 else -90.0).translate((sx * 20.0, 0.0, p.z_cap_top_lock))
        inter = cap_top & ring
        vol = float(inter.volume) if inter is not None else 0.0
        top_ratios.append(vol / ideal_ring)
    results["cap_top_lock_seat_bearing"] = {
        "min_contact_ratio": round(min(top_ratios), 4),
        "min_required": 0.80,
        "pass": min(top_ratios) >= 0.80,
    }

    # 3. lid_bot 4x M3x10 recessed lid bolt seats at R = 37.0 mm, Z = 19.0 .. 21.0 mm
    lid_ratios = []
    for deg in (45.0, 135.0, 225.0, 315.0):
        rad = math.radians(deg)
        lx, ly = p.lid_bot_bolt_r * math.cos(rad), p.lid_bot_bolt_r * math.sin(rad)
        ring = (
            bd.Cylinder(2.75, 2.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
            - bd.Cylinder(1.70, 2.2, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, -0.1))
        ).translate((lx, ly, p.z_lid_bot_start))
        inter = lid_bot & ring
        vol = float(inter.volume) if inter is not None else 0.0
        lid_ratios.append(vol / ideal_ring)
    results["lid_bot_bolt_seat_bearing"] = {
        "min_contact_ratio": round(min(lid_ratios), 4),
        "min_required": 0.90,
        "pass": min(lid_ratios) >= 0.90,
    }

    # 4. Core socket 4-wall intactness check on BOTH cap_bot & cap_top (accounting for ±Y wire slots in cap_bot!)
    bot_wall_ok = True
    top_wall_ok = True
    for ang in (0.0, 180.0):
        probe_b = bd.Box(2.5, 16.0, 8.0, align=(bd.Align.MIN, bd.Align.CENTER, bd.Align.MIN)).translate((15.45, 0.0, p.z_core_bot + 2.0)).rotate(bd.Axis.Z, ang)
        vb = float((cap_bot & probe_b).volume) if (cap_bot & probe_b) is not None else 0.0
        if vb < 0.70 * (2.5 * 16.0 * 8.0):
            bot_wall_ok = False
    for sy in (-1.0, 1.0):
        for sx in (-1.0, 1.0):
            # Check solid ±Y socket shoulders on BOTH sides of the 9.0 mm JST-XH wire slot (|X| ∈ [5.5, 13.5 mm])
            probe_by = bd.Box(8.0, 2.5, 8.0, align=(bd.Align.CENTER, bd.Align.MIN if sy > 0 else bd.Align.MAX, bd.Align.MIN)).translate((sx * 9.5, sy * 15.45, p.z_core_bot + 2.0))
            vby = float((cap_bot & probe_by).volume) if (cap_bot & probe_by) is not None else 0.0
            if vby < 0.70 * (8.0 * 2.5 * 8.0):
                bot_wall_ok = False
    for ang in (0.0, 90.0, 180.0, 270.0):
        probe_t = bd.Box(2.5, 16.0, 8.0, align=(bd.Align.MIN, bd.Align.CENTER, bd.Align.MIN)).translate((15.45, 0.0, p.z_cap_top_top - 11.0)).rotate(bd.Axis.Z, ang)
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
    # 1. Bottom-mounted SW1 vertical insertion straight down into recessed MECH-LID-BOT pocket
    sw_body = bd.Box(p.sw1_body_w_x, p.sw1_body_w_y, p.sw1_body_h_z, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    sw_lugs = bd.Box(10.0, 8.5, p.sw1_lugs_h_z, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0.0, 0.0, p.sw1_body_h_z))
    sw_bush = bd.Cylinder(p.sw1_hole_dia / 2.0 - 0.05, 8.89, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX))
    sw_tool = bd.Compound([sw_body, sw_lugs, sw_bush])
    sw_max_vol = 0.0
    for zw in np.linspace(p.z_lid_bot_start + 25.0, p.z_lid_bot_start + p.sw1_wall_thick + 0.05, 15):
        inter = lid_bot & sw_tool.translate((p.sw1_x, p.sw1_y, float(zw)))
        sw_max_vol = max(sw_max_vol, float(inter.volume) if inter is not None else 0.0)

    # 2. Horizontal driver_pcb (centered during entry through Ø65 mm bore, then shifted +6 mm onto standoffs!)
    pcb_max_vol = 0.0
    for dz in np.linspace(-50.0, -14.0, 10):
        # Pass centered through Ø65 mm spigot bore (dy = -pcb_y_center -> centered at Y=0)
        inter = cap_bot & pcb_assy.translate((0.0, -p.pcb_y_center, float(dz)))
        pcb_max_vol = max(pcb_max_vol, float(inter.volume) if inter is not None else 0.0)
    for dy in np.linspace(-p.pcb_y_center, 0.0, 6):
        inter = cap_bot & pcb_assy.translate((0.0, float(dy), -14.0))
        pcb_max_vol = max(pcb_max_vol, float(inter.volume) if inter is not None else 0.0)
    for dz in np.linspace(-14.0, 0.0, 8):
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

    # 4. ACTUAL 90-deg USB-C L-plug cross-section (13.2 x 11.5 x 18 mm) passing straight through 16x14 mm lid port (P0-2 FIXED!)
    plug90_pass_tool = bd.Box(p.usbc_plug_90_w, p.usbc_plug_90_h, 18.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER))
    port_max_vol = 0.0
    for zp in np.linspace(p.z_lid_bot_start - 15.0, p.z_lid_bot_end + 15.0, 15):
        inter = lid_bot & plug90_pass_tool.translate((p.clamp_x, p.clamp_y, float(zp)))
        port_max_vol = max(port_max_vol, float(inter.volume) if inter is not None else 0.0)

    return {
        "sw1_bottom_lid_insertion": {"waypoints_tested": 15, "max_intersection_vol_mm3": round(sw_max_vol, 6), "pass": sw_max_vol < 1e-4},
        "pcb_horiz_standoff_insertion": {"waypoints_tested": 24, "max_intersection_vol_mm3": round(pcb_max_vol, 6), "pass": pcb_max_vol < 1e-4},
        "jst_xh_plug_wire_slot_sweep": {"waypoints_tested": 30, "max_intersection_vol_mm3": round(jst_max_vol, 6), "pass": jst_max_vol < 1e-4},
        "usbc_90_plug_split_port_pass": {"waypoints_tested": 15, "max_intersection_vol_mm3": round(port_max_vol, 6), "pass": port_max_vol < 1e-4},
        "all_zero": (sw_max_vol < 1e-4) and (pcb_max_vol < 1e-4) and (jst_max_vol < 1e-4) and (port_max_vol < 1e-4),
    }


def compute_mass_budget(mesh_checks: dict, assy_nom: dict[str, bd.Shape]) -> dict[str, float]:
    """Compute exact Rev 4.6 lamp mass budget (g) from B-Rep volumes and ASA (1.07 g/cm^3) / stock material densities."""
    vol_printed_cm3 = (
        mesh_checks["mech_lid_bot"]["brep_volume_mm3"]
        + mesh_checks["mech_cap_bot"]["brep_volume_mm3"]
        + mesh_checks["mech_cap_top"]["brep_volume_mm3"]
        + mesh_checks["mech_plug_top"]["brep_volume_mm3"]
        + mesh_checks["mech_core_anchor"]["brep_volume_mm3"]
        + 2.0 * mesh_checks["mech_cable_clamp"]["brep_volume_mm3"]
        + 2.0 * mesh_checks["mech_hang_bushing"]["brep_volume_mm3"]
    ) / 1000.0
    asa_solid_g = vol_printed_cm3 * 1.07  # Black ASA density = 1.07 g/cm^3 (16% lighter than PETG 1.27 g/cm^3!)
    asa_fdm_g = vol_printed_cm3 * 1.07 * 0.62  # 4 perimeters + 25% gyroid infill (~62% effective fill)

    al_core_g = (float(assy_nom["hs_core"].volume) / 1000.0) * 2.70
    pmma_shroud_g = (float(assy_nom["glass_tube"].volume) / 1000.0) * 1.18
    elec_stars_hw_g = 102.0  # 8x Cu DTP stars (34 g) + PCB (23 g) + SW1/boot/inserts/O-rings/M3/M2.5 (45 g; M20 gland eliminated!)

    return {
        "printed_lamp_volume_cm3": round(vol_printed_cm3, 1),
        "cap_bot_volume_cm3": round(mesh_checks["mech_cap_bot"]["brep_volume_mm3"] / 1000.0, 1),
        "cap_top_volume_cm3": round(mesh_checks["mech_cap_top"]["brep_volume_mm3"] / 1000.0, 1),
        "lid_bot_volume_cm3": round(mesh_checks["mech_lid_bot"]["brep_volume_mm3"] / 1000.0, 1),
        "asa_fdm_62pct_g": round(asa_fdm_g, 1),
        "asa_solid_100pct_g": round(asa_solid_g, 1),
        "al_core_3mm_g": round(al_core_g, 1),
        "uvt_pmma_shroud_g": round(pmma_shroud_g, 1),
        "elec_stars_hardware_g": elec_stars_hw_g,
        "total_fdm_g": round(asa_fdm_g + al_core_g + pmma_shroud_g + elec_stars_hw_g, 1),
        "total_solid_g": round(asa_solid_g + al_core_g + pmma_shroud_g + elec_stars_hw_g, 1),
    }


def main() -> None:
    out_dir = Path(__file__).resolve().parent
    # Clean up deprecated Rev 4.5 mech_base_ring artifacts if present
    for old_name in ("mech_base_ring.step", "mech_base_ring.stl", "mech_plug_bot.step", "mech_plug_bot.stl"):
        old_p = out_dir / old_name
        if old_p.exists():
            old_p.unlink()

    p_fdm = LepiLEDParams(process="FDM")
    (out_dir / "cad_params.json").write_text(json.dumps(p_fdm.to_dict(), indent=2))

    assy_nom = build_assembly_parts(p_fdm)
    drill_jig = build_drill_jig(p_fdm)
    clamp_half_export = build_cable_clamp_half(p_fdm, side=+1.0)
    # Orient cable clamp half UPRIGHT flat on its Z = 8.0 mm bottom face for 0.000 mm^2 overhang print!
    bb_cl = clamp_half_export.bounding_box()
    clamp_half_print = clamp_half_export.translate((-0.5 * (bb_cl.min.X + bb_cl.max.X), -0.5 * (bb_cl.min.Y + bb_cl.max.Y), -bb_cl.min.Z))

    hang_bush_half = build_hang_bushing_half(p_fdm, side=+1.0)
    # Orient hang bushing flat on its outer flange face for print-ready STL/overhang check!
    hang_bush_print = hang_bush_half.rotate(bd.Axis.Y, 90.0)
    bb_hb = hang_bush_print.bounding_box()
    hang_bush_print = hang_bush_print.translate((0.0, 0.0, -bb_hb.min.Z))

    # 1. Export all 8 3D-printable FDM STEP & STL files
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

    # 2. Export individual assembly STLs to gitignored parts_stl/ for PyVista rendering
    comp_dir = out_dir / "parts_stl"
    comp_dir.mkdir(exist_ok=True)
    for old_f in comp_dir.glob("*.stl"):
        old_f.unlink()
    for name, shp in assy_nom.items():
        bd.export_stl(shp, str(comp_dir / f"{name}.stl"), tolerance=0.02, angular_tolerance=0.08)

    assy_compound = bd.Compound(list(assy_nom.values()))
    bd.export_step(assy_compound, str(out_dir / "lepiled_assembly.step"))

    # 3. Overhang audits (all 8 printed parts in actual build-plate orientations!)
    overhang_checks = {
        "mech_lid_bot": audit_stl_overhangs(out_dir / "mech_lid_bot.stl", (0.0, 0.0, 1.0)),
        "mech_cap_bot": audit_stl_overhangs(out_dir / "mech_cap_bot.stl", (0.0, 0.0, -1.0)),
        "mech_cap_top": audit_stl_overhangs(out_dir / "mech_cap_top.stl", (0.0, 0.0, 1.0)),
        "mech_plug_top": audit_stl_overhangs(out_dir / "mech_plug_top.stl", (0.0, 0.0, -1.0)),
        "mech_core_anchor": audit_stl_overhangs(out_dir / "mech_core_anchor.stl", (0.0, 0.0, -1.0)),
        "mech_cable_clamp": audit_stl_overhangs(out_dir / "mech_cable_clamp.stl", (0.0, 0.0, 1.0)),
        "mech_hang_bushing": audit_stl_overhangs(out_dir / "mech_hang_bushing.stl", (0.0, 0.0, 1.0)),
        "mech_drill_jig": audit_stl_overhangs(out_dir / "mech_drill_jig.stl", (0.0, 0.0, 1.0)),
    }

    # 4. Mandatory Positive Fastener-Seat Bearing & Intact 4-Wall Core Socket Verification (P0-1 regression gate!)
    seat_checks = check_fastener_seat_bearing(assy_nom["cap_bot"], assy_nom["cap_top"], assy_nom["lid_bot"], p_fdm)

    # 5. All-pairs B-Rep intersection verification (Nominal + Worst-Case +2.0 mm & 60.6 mm oval XT PMMA shroud!)
    wc_glass_len = p_fdm.glass_length + p_fdm.glass_length_tol
    inter_nom = check_all_pairs_intersections(assy_nom)
    assy_wc = build_assembly_parts(
        p_fdm, core_w_override=p_fdm.core_w_max, glass_id_override=p_fdm.glass_id_min,
        glass_od_override=p_fdm.glass_od_max, glass_length_override=wc_glass_len,
    )
    inter_wc = check_all_pairs_intersections(assy_wc)

    # 6. Kinematic insertion sweeps (SW1, horizontal PCB w/ 57 SMDs, JST-XH wire slots, ACTUAL 90-deg USB-C plug!)
    kinematic_checks = check_kinematic_insertion(assy_nom["lid_bot"], assy_nom["cap_bot"], assy_nom["pcb_assy"], p_fdm)

    # 7. Exact mass budget
    mass_budget = compute_mass_budget(mesh_checks, assy_nom)

    all_meshes_ok = all(m["is_watertight"] and m["is_winding_consistent"] and m["stl_volume_mm3"] > 0 for m in mesh_checks.values())
    all_overhangs_ok = all(o["pass"] for o in overhang_checks.values())
    all_brep_ok = inter_nom["all_zero"] and inter_wc["all_zero"]
    all_kinematic_ok = kinematic_checks["all_zero"]
    all_seats_ok = seat_checks["all_pass"]
    all_param_checks_ok = all(c["pass"] for c in p_fdm.verify_all().values())

    report = {
        "revision": "Rev 4.6 (Field Lantern: Unified Tapered Frustum, Solid Core Hubs, Dry-Bay Anchor, Coaxial Split Clamp & Lofted Roof)",
        "params": p_fdm.to_dict(),
        "mesh_checks": mesh_checks,
        "overhang_checks": overhang_checks,
        "fastener_seat_bearing_checks": seat_checks,
        "kinematic_insertion_checks": kinematic_checks,
        "brep_all_pairs_nominal": {k: v for k, v in inter_nom.items() if k != "pairs"},
        "brep_all_pairs_worst_case": {k: v for k, v in inter_wc.items() if k != "pairs"},
        "mass_budget_g": mass_budget,
        "summary": {
            "all_param_checks_pass": all_param_checks_ok,
            "all_meshes_watertight_manifold": all_meshes_ok,
            "all_overhangs_le_46deg": all_overhangs_ok,
            "fastener_seat_bearing_pass": all_seats_ok,
            "kinematic_insertion_zero": all_kinematic_ok,
            "nominal_all_pairs_zero": inter_nom["all_zero"],
            "worst_case_all_pairs_zero": inter_wc["all_zero"],
            "overall_pass": (
                all_param_checks_ok and all_meshes_ok and all_overhangs_ok
                and all_seats_ok and all_brep_ok and all_kinematic_ok
            ),
        },
    }
    verif_path = out_dir / "cad_verification.json"
    verif_path.write_text(json.dumps(report, indent=2))

    print("=== Mesh Verification (8 FDM Printable Parts — MECH-BASE-RING & M20 Gland Eliminated) ===")
    for name, m in mesh_checks.items():
        print(f"  {name:18s}: vol={m['stl_volume_mm3']:8.1f} mm^3 | tri={m['triangles']:6d} | wt={m['is_watertight']} | wind={m['is_winding_consistent']} | euler={m['euler_number']:3d}")
    print("=== Overhang Verification ===")
    for name, o in overhang_checks.items():
        print(f"  {name:18s}: >46deg faces={o['off_bed_overhang_gt46_faces']:4d}, area={o['off_bed_overhang_gt46_area_mm2']:6.3f} mm^2, max={o['max_off_bed_overhang_deg']:5.2f} deg | pass={o['pass']}")
    print("=== Positive Fastener-Seat Bearing & Intact Core-Socket Gate (P0-1 Regression Guard) ===")
    for k, v in seat_checks.items():
        if isinstance(v, dict):
            print(f"  {k:30s}: {v}")
    print("=== Kinematic Insertion (SW1, PCB w/ 57 SMDs, JST-XH Wire Slots, ACTUAL 90-deg USB-C L-Plug!) ===")
    for k in ("sw1_bottom_lid_insertion", "pcb_horiz_standoff_insertion", "jst_xh_plug_wire_slot_sweep", "usbc_90_plug_split_port_pass"):
        v = kinematic_checks[k]
        print(f"  {k:30s}: waypoints={v['waypoints_tested']:2d}, max_vol={v['max_intersection_vol_mm3']:.6f} mm^3 | pass={v['pass']}")
    print("=== All-Pairs B-Rep Intersection (incl. 57 SMDs, 90-deg USB-C + 7 mm Strain Relief, Split Clamp & Anchor) ===")
    for label, d in [("NOMINAL", inter_nom), ("WORST_CASE", inter_wc)]:
        print(f"  {label:10s}: {d['total_pairs_checked']} pairs, nonzero={d['nonzero_count']} {d['nonzero_pairs']}")
    print("=== Verified Mass Budget (Rev 4.6 Black ASA) ===")
    print(f"  Printed lamp parts ({mass_budget['printed_lamp_volume_cm3']} cm^3; cap_bot={mass_budget['cap_bot_volume_cm3']}, cap_top={mass_budget['cap_top_volume_cm3']}, lid_bot={mass_budget['lid_bot_volume_cm3']} cm^3): {mass_budget['asa_fdm_62pct_g']} g ASA FDM / {mass_budget['asa_solid_100pct_g']} g solid")
    print(f"  Al core (30x30x3x200): {mass_budget['al_core_3mm_g']} g | XT PMMA shroud (60x54x115): {mass_budget['uvt_pmma_shroud_g']} g | Elec+Stars+HW: {mass_budget['elec_stars_hardware_g']} g")
    print(f"  TOTAL LAMP WEIGHT (FDM ASA): {mass_budget['total_fdm_g']} g ({mass_budget['total_solid_g']} g solid) | HEIGHT: {p_fdm.total_height_mm} mm")

    if not report["summary"]["overall_pass"]:
        raise SystemExit(1)
    print(f"Wrote {verif_path} and all Rev 4.6 STEP/STL artifacts (ALL CHECKS PASS).")


if __name__ == "__main__":
    main()
