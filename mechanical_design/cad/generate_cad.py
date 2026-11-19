#!/usr/bin/env python3
"""
Parametric 3D CAD Generator for LepiLED DIY Maxi Switch (Rev 4.1 — S1-A / S2-A / S3) using build123d.

Exports:
  - mech_lid_bot.step / .stl       (FDM PETG/ASA, flat bottom lid w/ 4x integral 11.5 mm M2.5 PCB bosses)
  - mech_lid_bot_sls.step / .stl   (SLS PA12, flat bottom lid)
  - mech_cap_bot.step / .stl       (FDM PETG/ASA, unified USB-C + Ø20.2 mm rubber grommet flange + C&K 7211 DPDT)
  - mech_cap_bot_sls.step / .stl   (SLS PA12, unified bottom cap)
  - mech_cap_top.step / .stl       (FDM PETG/ASA, flat top face)
  - mech_cap_top_sls.step / .stl   (SLS PA12, flat top face)
  - lepiled_assembly.step / .stl   (Full multi-part assembly incl. all fasteners & grommet)
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
      - 4x integral 11.5 mm tall Ø6.2 mm M2.5 PCB standoff bosses at H1..H4 (±14.0, ±19.0)
      - 4x M3 flush countersunk clearance holes at R = 40.2 mm (45°, 135°, 225°, 315°)
      - Prints flat on Z=0 bed with ZERO >46° overhang and zero CNC milling!
    """
    r_lid = p.lid_bot_od / 2.0
    part = bd.Cylinder(r_lid, p.lid_bot_thick, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    bot_edges = part.edges().filter_by(bd.GeomType.CIRCLE).sort_by(bd.Axis.Z)[:1]
    part = bd.chamfer(bot_edges, length=p.cap_chamfer)

    # 4x integral M2.5 PCB mounting bosses (Z = 4.0 .. 15.5 mm) with Ø3.5 x 4.5 mm M2.5 insert bores
    r_boss = p.pcb_boss_od / 2.0
    r_ins = p.pcb_boss_insert_dia / 2.0
    for sx in (-1.0, 1.0):
        for sy in (-1.0, 1.0):
            bx, by = sx * p.pcb_hole_x, sy * p.pcb_hole_y
            boss = bd.Cylinder(r_boss, p.pcb_boss_h, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((bx, by, p.z_lid_bot_end))
            # Small 1.0 mm 45-deg fillet/collar at base of boss for bending stiffness
            collar = bd.Cone(r_boss + 1.0, r_boss, 1.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((bx, by, p.z_lid_bot_end))
            part = part.fuse(boss).fuse(collar)
            ins_hole = bd.Cylinder(r_ins, p.pcb_boss_insert_depth, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)).translate((bx, by, p.z_pcb_bot + 0.05))
            part = part - ins_hole

    # 4x M3 flush DIN 7991 CSK clearance holes at R = 40.2 mm (zero overhang on Z=0 bed!)
    for deg in (45.0, 135.0, 225.0, 315.0):
        rad = math.radians(deg)
        hx, hy = p.lid_bot_bolt_r * math.cos(rad), p.lid_bot_bolt_r * math.sin(rad)
        c_thru = bd.Cylinder(1.70, p.lid_bot_thick + 1.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((hx, hy, -0.5))
        # M3 DIN 7991 CSK head Ø6.0 mm, 90° -> cone from R=3.20 at Z=0.0 to R=1.70 at Z=1.50 (45° = support-free!)
        c_csk = bd.Cone(3.20, 1.70, 1.50, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((hx, hy, 0.0))
        part = part - c_thru - c_csk

    return part


def build_cap_bot(p: LepiLEDParams) -> bd.Part:
    """
    Build unified Rev 4.1 MECH-CAP-BOT:
      - Ø92 -> Ø84 mm outer envelope, Ø61 mm PCB cavity + 40.3° cone + 6 mm bulkhead
      - MECH-GASKET-3 (66x2.0 mm) V-roof groove + 4x M3 heat-set inserts at R = 40.2 mm
      - -Y side: Flat-faced Ø20.2 x 2.5 mm rubber membrane grommet flange (3A) + Ø23.6 mm back lip relief
        + 13.6 x 7.8 mm (+47° roof) direct-mate USB-C tunnel into J1 (Y = -25.76 mm)
      - +X side: C&K 7211SYZBE gold DPDT switch alcove (15.0 x 13.5 mm + 45° roof) & Ø6.35 mm teardrop bore
      - Prints upright (+Z up) with < 1 mm^2 >46° overhang (100% support-free!).
    """
    r_bot = p.cap_bot_od / 2.0        # 46.0 mm
    r_top = p.cap_top_od / 2.0        # 42.0 mm
    z_base = p.z_lid_bot_end          # 4.0
    z_top = p.z_cap_bot_top           # 82.0
    z_taper_bot = p.z_glass_bot - 12.0  # 58.0
    z_taper_top = z_taper_bot + (r_bot - r_top)  # 62.0 (45 deg outer step)

    # 1. Outer body: Ø92 mm lower body -> 45 deg step -> Ø84 mm upper glass skirt
    c_bot = bd.Cylinder(r_bot, z_taper_bot - z_base, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, z_base))
    c_step = bd.Cone(r_bot, r_top, z_taper_top - z_taper_bot, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, z_taper_bot))
    c_top = bd.Cylinder(r_top, z_top - z_taper_top, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, z_taper_top))
    part = c_bot.fuse(c_step).fuse(c_top)
    bottom_edges = part.edges().filter_by(bd.GeomType.CIRCLE).sort_by(bd.Axis.Z)[:1]
    top_edges = part.edges().filter_by(bd.GeomType.CIRCLE).sort_by(bd.Axis.Z)[-1:]
    part = bd.chamfer(bottom_edges + top_edges, length=p.cap_chamfer)

    # 2. Internal PCB cavity: cylinder + 40.3 deg cone all the way to R=0.02 apex
    r_cav = p.cap_bot_cavity_dia / 2.0
    cav_cyl = bd.Cylinder(r_cav, p.cap_bot_cavity_full_h, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, z_base))
    cav_cone = bd.Cone(r_cav, 0.02, p.cap_bot_taper_h, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, z_base + p.cap_bot_cavity_full_h))
    part = part - cav_cyl.fuse(cav_cone)

    # 3. Bottom O-ring groove (MECH-GASKET-3: 66x2.0 mm) with self-supporting 45 deg V-roof
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

    # 4. 4x M3 heat-set insert blind holes at R = 40.2 mm (45°, 135°, 225°, 315°) with 45 deg cone tip
    r_ins = p.insert_m3_hole_dia / 2.0
    for deg in (45.0, 135.0, 225.0, 315.0):
        rad = math.radians(deg)
        ix, iy = p.lid_bot_bolt_r * math.cos(rad), p.lid_bot_bolt_r * math.sin(rad)
        hole = bd.Cylinder(r_ins, p.insert_m3_depth, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((ix, iy, z_base))
        tip = bd.Cone(r_ins, 0.02, r_ins - 0.02, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((ix, iy, z_base + p.insert_m3_depth))
        lead = bd.Cone(r_ins + 0.4, r_ins, 0.4, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((ix, iy, z_base))
        part = part - hole.fuse(tip).fuse(lead)

    # 5. Glass socket (Z = 70.0 .. 82.0) with tapered skirt + axial O-ring groove (MECH-GASKET-1: 68x3.5 mm)
    r_pilot = p.glass_pilot_od / 2.0
    glass_outer = bd.Cone(p.glass_skirt_id_bot / 2.0, p.glass_skirt_id_top / 2.0, p.glass_socket_depth, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    glass_inner = bd.Cylinder(r_pilot, p.glass_socket_depth, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    glass_slot = (glass_outer - glass_inner).translate((0, 0, p.z_glass_bot))

    g1_out = bd.Cylinder(p.glass_oring_od / 2.0, p.glass_oring_depth + 0.05, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    g1_in = bd.Cylinder(p.glass_oring_id / 2.0, p.glass_oring_depth + 0.05, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    g1 = (g1_out - g1_in).translate((0, 0, p.z_glass_bot - p.glass_oring_depth))
    part = part - glass_slot.fuse(g1)

    # 6. Core socket (41.0 x 41.0 mm, Z = 70.0 .. 82.0) + 4x wire slots opening cleanly into cavity cone
    core_sock = bd.Box(p.core_pocket_w, p.core_pocket_w, p.glass_socket_depth,
                       align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, p.z_core_bot))
    part = part - core_sock

    slot_offset = p.core_pocket_w / 2.0 + p.core_wire_slot_d / 2.0 - 0.1
    z_slot_bot = p.z_cap_bot_cavity_taper_start + 5.0  # opens cleanly below cavity cone -> zero overhang
    h_slot = z_top - z_slot_bot
    for angle in (0.0, 90.0, 180.0, 270.0):
        wslot = bd.Box(p.core_wire_slot_d + 0.2, p.core_wire_slot_w, h_slot,
                       align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((slot_offset, 0, z_slot_bot))
        wslot = wslot.rotate(bd.Axis.Z, angle)
        part = part - wslot

    # 7. 2x M4 CSK upward bulkhead holes at (±9.0, 0.0) into MECH-ANCHOR-BOT (45 deg CSK seat, zero overhang)
    z_csk_seat = p.z_cap_bot_bulkhead_start - 4.5
    for sx in (-1.0, 1.0):
        bx = sx * p.anchor_bot_bolt_x
        c_clear = bd.Cylinder(4.3, 12.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((bx, 0.0, z_csk_seat - 12.0))
        c_seat = bd.Cone(4.3, 2.2, 2.1, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((bx, 0.0, z_csk_seat))
        c_thru = bd.Cylinder(2.2, 11.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((bx, 0.0, z_csk_seat + 2.0))
        part = part - c_clear.fuse(c_seat).fuse(c_thru)

    # 8. SW1 (C&K 7211SYZBE gold DPDT) toggle switch cutout (+X side, Y = 0, Z = 30.0 mm)
    sw_sf_face = _teardrop_profile_wire(p.sw1_spotface_dia / 2.0, 45.0)
    sw_sf = bd.extrude(sw_sf_face, 5.0).rotate(bd.Axis.X, 90.0).rotate(bd.Axis.Z, -90.0)
    sw_sf = sw_sf.translate((p.sw1_spotface_x + 5.0, 0.0, p.sw1_z))
    part = part - sw_sf

    x_sw_in = p.sw1_spotface_x - p.sw1_wall_thick  # 42.5
    sw_corridor_len = x_sw_in - 10.0               # breaks cleanly into Ø61 mm bottom cavity cone!
    sw_prof = _pitched_rect_profile(p.sw1_alcove_w, p.sw1_alcove_h, 47.0)
    sw_alc = bd.extrude(sw_prof, sw_corridor_len).rotate(bd.Axis.X, 90.0).rotate(bd.Axis.Z, -90.0)
    sw_alc = sw_alc.translate((x_sw_in, 0.0, p.sw1_z - p.sw1_alcove_h / 2.0))
    part = part - sw_alc

    sw_td_face = _teardrop_profile_wire(p.sw1_hole_dia / 2.0 + p.print_clearance * 0.5, 45.0)
    sw_hole = bd.extrude(sw_td_face, 8.0).rotate(bd.Axis.X, 90.0).rotate(bd.Axis.Z, -90.0)
    sw_hole = sw_hole.translate((x_sw_in + 5.0, 0.0, p.sw1_z))
    part = part - sw_hole

    # 9. Unified USB-C Direct-Mate Entry + Off-the-Shelf Ø20.2 x 2.5 mm Rubber Grommet Seat (-Y side, Option 3A!)
    z_usbc = p.z_usbc
    y_sf = p.grommet_outer_spotface_y                                   # -43.5
    y_panel_in = y_sf + p.grommet_panel_thick                           # -41.0
    y_back_in = y_panel_in + p.grommet_back_relief_depth                # -38.5
    y_tunnel_in = -18.00  # breaks cleanly inside cavity cone across full X=±6.8 width -> ~0 mm^2 overhang!

    # 9a. Flat outer Ø26.0 mm 45-deg teardrop spotface (Y = -48.5 .. -43.5) so rubber grommet flange seats flat!
    g_sf_face = _teardrop_profile_wire(p.grommet_outer_spotface_dia / 2.0, 45.0)
    g_sf = bd.extrude(g_sf_face, 5.0).rotate(bd.Axis.X, 90.0).translate((0.0, y_sf, z_usbc))
    part = part - g_sf

    # 9b. Ø20.2 mm 45-deg teardrop grommet bore through the 2.5 mm panel flange (Y = -44.5 .. -40.5)
    g_bore_face = _teardrop_profile_wire(p.grommet_bore_dia / 2.0, 45.0)
    g_bore = bd.extrude(g_bore_face, p.grommet_panel_thick + 1.0).rotate(bd.Axis.X, 90.0).translate((0.0, y_panel_in + 0.5, z_usbc))
    part = part - g_bore

    # 9c. Ø23.6 mm 45-deg teardrop back-lip relief groove (Y = -41.0 .. -38.5) so grommet snaps in mechanically!
    g_back_face = _teardrop_profile_wire(p.grommet_back_relief_dia / 2.0, 45.0)
    g_back = bd.extrude(g_back_face, p.grommet_back_relief_depth).rotate(bd.Axis.X, 90.0).translate((0.0, y_back_in, z_usbc))
    part = part - g_back

    # 9d. Open 13.6 x 7.8 mm (+47 deg roof) direct-mate USB-C guide tunnel (Y = -39.0 .. -24.0) straight to J1!
    overmold_len = abs((y_back_in - 0.5) - y_tunnel_in)
    overmold_prof = _pitched_rect_profile(p.usbc_overmold_w, p.usbc_overmold_h, 47.0)
    overmold = bd.extrude(overmold_prof, overmold_len).rotate(bd.Axis.X, 90.0)
    overmold = overmold.translate((0.0, y_tunnel_in, z_usbc - p.usbc_overmold_h / 2.0))
    part = part - overmold

    return part


def build_cap_top(p: LepiLEDParams) -> bd.Part:
    """Build MECH-CAP-TOP parametric end-cap (100% flat top face Z_top, <1 mm^2 >46 deg overhang)."""
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

    core_thru = bd.Box(p.core_pocket_w, p.core_pocket_w, h_tot + 2.0,
                       align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, z_bot - 1.0))
    part = part - core_thru

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
                          z_start: float, center_bore_dia: float = 0.0, hub_bolt_r: float = 8.5) -> bd.Part:
    """Build radial-fin extruded aluminum heatsink (Fischer SK 578/50 SA) with Ø6.5 center bore & 4x M3 hub holes."""
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
    # 4x M3 tapped blind holes at R = 8.5 mm in bottom face of hub (depth 8.0 mm for 4x M3x8 CSK bolts)
    for deg in (45.0, 135.0, 225.0, 315.0):
        rad = math.radians(deg)
        hx, hy = hub_bolt_r * math.cos(rad), hub_bolt_r * math.sin(rad)
        h_tap = bd.Cylinder(1.55, 8.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((hx, hy, -0.1))
        hs = hs - h_tap
    return hs.translate((0, 0, z_start))


def build_assembly_parts(p: LepiLEDParams, core_w_override: float | None = None,
                         glass_id_override: float | None = None, glass_od_override: float | None = None,
                         glass_length_override: float | None = None) -> dict[str, bd.Shape]:
    """Build all Rev 4.1 physical assembly components (including all fasteners & rubber grommet) as non-overlapping solids."""
    core_w = core_w_override or p.core_w_nom
    g_id = glass_id_override or p.glass_id_nom
    g_od = glass_od_override or p.glass_od_nom
    g_len = glass_length_override or p.glass_length

    lid_bot = build_lid_bot(p)
    cap_bot = build_cap_bot(p)
    cap_top = build_cap_top(p)
    hs_top = build_radial_heatsink(
        p.hs_ext_top_od, p.hs_ext_top_core_dia, p.hs_ext_top_height,
        p.hs_ext_top_n_fins, p.hs_ext_top_fin_thick, p.z_adapt_top_end,
        center_bore_dia=p.eye_bolt_clearance_dia, hub_bolt_r=p.hs_ext_top_hub_bolt_r,
    )

    # Top adapter plate (MECH-ADAPT-TOP: off-the-shelf Ø76.2 x 3.0 mm Al disc) with M6 center, 4x R8.5 CSK, 4x R34 M3 holes
    adapt_top = bd.Cylinder(p.adapt_top_od / 2.0, p.adapt_top_thick, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, p.z_core_top))
    adapt_top = adapt_top - bd.Cylinder(p.eye_bolt_clearance_dia / 2.0, p.adapt_top_thick + 2.0,
                                        align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, p.z_core_top - 1.0))
    for deg in (45.0, 135.0, 225.0, 315.0):
        rad = math.radians(deg)
        # 4x M3 CSK hub bolts at R = 8.5 mm (CSK flush in bottom face Z = z_core_top)
        hx, hy = p.hs_ext_top_hub_bolt_r * math.cos(rad), p.hs_ext_top_hub_bolt_r * math.sin(rad)
        h_thru = bd.Cylinder(1.70, p.adapt_top_thick + 1.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((hx, hy, p.z_core_top - 0.5))
        h_csk = bd.Cone(3.20, 1.70, 1.50, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((hx, hy, p.z_core_top))
        adapt_top = adapt_top - h_thru - h_csk
        # 4x M3 clamp bolts at R = 34.0 mm
        cx, cy = p.adapt_top_bolt_r * math.cos(rad), p.adapt_top_bolt_r * math.sin(rad)
        c_thru = bd.Cylinder(1.70, p.adapt_top_thick + 1.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((cx, cy, p.z_core_top - 0.5))
        adapt_top = adapt_top - c_thru

    # 4x 0.5 mm SS spacer washers (MECH-FAST-3W) between flat cap_top and adapt_top
    washers = []
    for deg in (45.0, 135.0, 225.0, 315.0):
        rad = math.radians(deg)
        wx, wy = p.adapt_top_bolt_r * math.cos(rad), p.adapt_top_bolt_r * math.sin(rad)
        w_out = bd.Cylinder(3.5, p.cap_top_air_gap_proud, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((wx, wy, p.z_cap_top_top))
        w_in = bd.Cylinder(1.6, p.cap_top_air_gap_proud + 0.2, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((wx, wy, p.z_cap_top_top - 0.1))
        washers.append(w_out - w_in)
    spacer_washers = bd.Compound(washers)

    # Driver PCB (Rev 4.1: USB-C only, NO Aux TP1/TP2, isolated NPTH H1..H4 Ø2.7 mm drills!)
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
    # TH pin protrusions below PCB (1.8 mm — floating in 11.5 mm open air gap above MECH-LID-BOT!)
    j23_pins = bd.Box(15.0, 2.0, p.pcb_jst_pin_protrude, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)).translate((0.0, 19.2, p.z_pcb_bot))
    j4_pins = bd.Box(7.5, 2.0, p.pcb_jst_pin_protrude, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)).translate((-1.4, -2.5, p.z_pcb_bot))
    j1_pins = bd.Box(9.6, 5.7, p.pcb_jst_pin_protrude, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)).translate((0.0, -19.54, p.z_pcb_bot))
    pcb_assy = bd.Compound([pcb_board, l1_smd, l2_smd, j2_hdr, j3_hdr, j4_hdr, j1_usbc, j23_pins, j4_pins, j1_pins])

    # Central heatsink core (MECH-HS-CORE: 40x40x3 mm) with TIGHT Ø4.2 mm round top & bottom cross-pin bores (Opus B-H3!)
    core_out = bd.Box(core_w, core_w, p.core_length, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    core_in = bd.Box(core_w - 2.0 * p.core_wall, core_w - 2.0 * p.core_wall, p.core_length + 2.0,
                     align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, -1.0))
    hs_core = (core_out - core_in).translate((0, 0, p.z_core_bot))
    z_top_pin = p.z_core_top - p.anchor_top_recess - p.anchor_h / 2.0  # z_core_top - 7.50 mm!
    for sy in (-p.anchor_top_pin_y, p.anchor_top_pin_y):
        b_pin = bd.Cylinder(2.1, core_w + 2.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER)).rotate(bd.Axis.Y, 90.0).translate((0.0, sy, p.z_core_bot + 6.0))
        t_pin = bd.Cylinder(2.1, core_w + 2.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER)).rotate(bd.Axis.Y, 90.0).translate((0.0, sy, z_top_pin))
        hs_core = hs_core - b_pin - t_pin

    # Bottom internal anchor plug (MECH-ANCHOR-BOT: stock 32x32x12 mm Al bar — ZERO milling!)
    anchor_bot = bd.Box(p.anchor_bot_w, p.anchor_bot_w, p.anchor_bot_h,
                        align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, p.z_core_bot))
    for sx in (-1.0, 1.0):
        v_hole = bd.Cylinder(2.0, p.anchor_bot_h + 1.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((sx * p.anchor_bot_bolt_x, 0.0, p.z_core_bot - 0.5))
        anchor_bot = anchor_bot - v_hole
    for sy in (-p.anchor_top_pin_y, p.anchor_top_pin_y):
        h_hole = bd.Cylinder(2.0, p.anchor_bot_w + 2.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER)).rotate(bd.Axis.Y, 90.0).translate((0.0, sy, p.z_core_bot + 6.0))
        anchor_bot = anchor_bot - h_hole

    # Top internal anchor block (MECH-ANCHOR-TOP: stock 32x32x14 mm Al bar, recessed 0.50 mm for B-H3 preload!)
    z_anchor_top_face = p.z_core_top - p.anchor_top_recess
    anchor_top = bd.Box(p.anchor_w, p.anchor_w, p.anchor_h,
                        align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)).translate((0, 0, z_anchor_top_face))
    m6_bore = bd.Cylinder(p.eye_bolt_thread_dia / 2.0, p.anchor_h + 2.0,
                          align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)).translate((0, 0, z_anchor_top_face + 1.0))
    anchor_top = anchor_top - m6_bore
    for sy in (-p.anchor_top_pin_y, p.anchor_top_pin_y):
        p_bore = bd.Cylinder(2.0, p.anchor_w + 2.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER)).rotate(bd.Axis.Y, 90.0).translate((0.0, sy, z_top_pin))
        anchor_top = anchor_top - p_bore

    # ALL Modeled Fasteners (Carbon C-4 / Opus C-M4: verified 0.000000 mm^3 B-Rep interference!)
    fasteners_list = []
    # 1. 4x M4x40 flush cross-pins + 2x M4x16 CSK bottom bulkhead bolts
    for sy in (-p.anchor_top_pin_y, p.anchor_top_pin_y):
        pin_top = bd.Cylinder(1.95, core_w - 0.2, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER)).rotate(bd.Axis.Y, 90.0).translate((0.0, sy, z_top_pin))
        pin_bot = bd.Cylinder(1.95, core_w - 0.2, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER)).rotate(bd.Axis.Y, 90.0).translate((0.0, sy, p.z_core_bot + 6.0))
        fasteners_list.extend([pin_top, pin_bot])
    z_csk_seat = p.z_cap_bot_bulkhead_start - 4.5
    for sx in (-1.0, 1.0):
        bx = sx * p.anchor_bot_bolt_x
        b_shank = bd.Cylinder(1.95, 16.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((bx, 0.0, z_csk_seat + 0.1))
        b_head = bd.Cone(4.0, 1.95, 2.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((bx, 0.0, z_csk_seat + 0.1))
        fasteners_list.append(b_shank.fuse(b_head))
    # 2. 4x Nylon M2.5 x 6 mm PCB screws through NPTH H1..H4 into MECH-LID-BOT bosses
    for sx in (-1.0, 1.0):
        for sy in (-1.0, 1.0):
            bx, by = sx * p.pcb_hole_x, sy * p.pcb_hole_y
            s_head = bd.Cylinder(2.25, 2.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((bx, by, p.z_pcb_top + 0.02))
            s_shank = bd.Cylinder(1.22, 5.8, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)).translate((bx, by, p.z_pcb_top + 0.02))
            fasteners_list.append(s_head.fuse(s_shank))
    # 3. 4x M3x8 DIN 7991 CSK lid bolts (R=40.2) + 4x M3x8 top cap SHCS (R=34.0) + 4x M3x8 CSK hub bolts (R=8.5)
    for deg in (45.0, 135.0, 225.0, 315.0):
        rad = math.radians(deg)
        # Bottom lid CSK M3x8 (flush Z=0.05..8.05)
        lx, ly = p.lid_bot_bolt_r * math.cos(rad), p.lid_bot_bolt_r * math.sin(rad)
        lb_head = bd.Cone(3.0, 1.48, 1.45, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((lx, ly, 0.05))
        lb_shank = bd.Cylinder(1.48, 8.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((lx, ly, 0.05))
        fasteners_list.append(lb_head.fuse(lb_shank))
        # Top cap SHCS M3x8 (at R=34.0, head above adapt_top)
        tx, ty = p.adapt_top_bolt_r * math.cos(rad), p.adapt_top_bolt_r * math.sin(rad)
        tb_head = bd.Cylinder(2.75, 3.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((tx, ty, p.z_adapt_top_end + 0.02))
        tb_shank = bd.Cylinder(1.48, 8.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)).translate((tx, ty, p.z_adapt_top_end + 0.02))
        fasteners_list.append(tb_head.fuse(tb_shank))
        # Top heatsink hub CSK M3x8 (at R=8.5, CSK flush in bottom of adapt_top -> into SK 578/50 SA hub!)
        hx, hy = p.hs_ext_top_hub_bolt_r * math.cos(rad), p.hs_ext_top_hub_bolt_r * math.sin(rad)
        hb_head = bd.Cone(3.0, 1.48, 1.45, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((hx, hy, p.z_core_top + 0.05))
        hb_shank = bd.Cylinder(1.48, 8.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((hx, hy, p.z_core_top + 0.05))
        fasteners_list.append(hb_head.fuse(hb_shank))
    fasteners_anchors = bd.Compound(fasteners_list)

    # M6 x 75 mm eye bolt (MECH-EYE-1) engaging recessed MECH-ANCHOR-TOP
    eye_shaft = bd.Cylinder(2.95, p.hs_ext_top_height + p.adapt_top_thick + p.anchor_top_recess + p.anchor_h + 5.0,
                            align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, z_anchor_top_face - p.anchor_h + 1.0))
    eye_collar = bd.Cylinder(9.0, 5.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, p.z_hs_top_end))
    eye_ring = bd.Torus(11.0, 3.2).rotate(bd.Axis.X, 90.0).translate((0, 0, p.z_hs_top_end + 17.0))
    eye_bolt = eye_shaft.fuse(eye_collar).fuse(eye_ring)

    # Borosilicate glass tube (MECH-TUBE-1)
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

    # SW1 (C&K 7211SYZBE gold DPDT) + C&K 759D02000 silicone boot envelope (+X side)
    x_sw_in = p.sw1_spotface_x - p.sw1_wall_thick
    sw_body = bd.Box(p.sw1_body_depth, p.sw1_body_w_y, p.sw1_body_h_z, align=(bd.Align.MAX, bd.Align.CENTER, bd.Align.CENTER)).translate((x_sw_in, 0, p.sw1_z))
    sw_lugs = bd.Box(p.sw1_lugs_depth, 10.0, 8.5, align=(bd.Align.MAX, bd.Align.CENTER, bd.Align.CENTER)).translate((x_sw_in - p.sw1_body_depth, 0, p.sw1_z))
    sw_boot = bd.Cylinder(6.65, 16.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).rotate(bd.Axis.Y, 90.0).translate((p.sw1_spotface_x, 0, p.sw1_z))
    sw1_assy = bd.Compound([sw_body, sw_lugs, sw_boot])

    # Off-the-shelf 20 mm rubber membrane grommet (snapped into Ø20.2 x 2.5 mm flange at Y = -43.5 .. -41.0!)
    y_sf = p.grommet_outer_spotface_y
    y_panel_in = y_sf + p.grommet_panel_thick
    g_outer_lip = bd.Cylinder(12.2, 2.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).rotate(bd.Axis.X, 90.0).translate((0.0, y_sf - 0.05, p.z_usbc))
    g_neck = bd.Cylinder(9.95, p.grommet_panel_thick + 0.1, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).rotate(bd.Axis.X, 90.0).translate((0.0, y_panel_in + 0.05, p.z_usbc))
    g_inner_lip = bd.Cylinder(11.5, 2.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).rotate(bd.Axis.X, 90.0).translate((0.0, y_panel_in + 2.05, p.z_usbc))
    g_cable_cut = bd.Box(12.8, 12.0, 7.2, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER)).translate((0.0, y_sf + 1.0, p.z_usbc))
    grommet_usbc = g_outer_lip.fuse(g_neck).fuse(g_inner_lip) - g_cable_cut

    # Standard 6.65 mm USB-C PD laptop-charger / power-bank plug seated full 4.55 mm inside J1
    y_plug_tip = p.usbc_j1_front_y + p.usbc_mating_depth_mm
    y_overmold_front = y_plug_tip - p.usbc_specified_barrel_mm
    usbc_plug_shell = bd.Box(8.3, p.usbc_specified_barrel_mm + 0.01, 2.5, align=(bd.Align.CENTER, bd.Align.MAX, bd.Align.CENTER)).translate((0.0, y_plug_tip, p.z_usbc))
    usbc_plug_overmold = bd.Box(12.4, 26.0, 6.8, align=(bd.Align.CENTER, bd.Align.MAX, bd.Align.CENTER)).translate((0.0, y_overmold_front, p.z_usbc))
    usbc_plug_assy = usbc_plug_shell.fuse(usbc_plug_overmold)
    assert len(usbc_plug_assy.solids()) == 1, f"Expected 1 contiguous USB-C plug solid, got {len(usbc_plug_assy.solids())}"

    return dict(
        lid_bot=lid_bot,
        cap_bot=cap_bot,
        cap_top=cap_top,
        hs_top=hs_top,
        adapt_top=adapt_top,
        spacer_washers=spacer_washers,
        pcb_assy=pcb_assy,
        hs_core=hs_core,
        anchor_bot=anchor_bot,
        anchor_top=anchor_top,
        fasteners_anchors=fasteners_anchors,
        eye_bolt=eye_bolt,
        glass_tube=glass_tube,
        mcpcbs=mcpcbs,
        sw1_assy=sw1_assy,
        grommet_usbc=grommet_usbc,
        usbc_plug_assy=usbc_plug_assy,
    )


def check_all_pairs_intersections(parts: dict[str, bd.Shape]) -> dict[str, dict]:
    """Run genuine ALL-PAIRS N*(N-1)/2 B-Rep solid intersection check across every part in the assembly."""
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
    """Audit off-bed downward-facing triangles exceeding max_overhang_deg from vertical."""
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
    """
    Vectorized Möller-Trumbore STL ray-cast across the USB-C tunnel & Ø20.2 mm grommet flange asserting
    unobstructed direct-mate opening inside the 13.6 x 7.8 mm (+47° roof) USB-C tunnel and >= 2.50 mm
    flange/wall thickness everywhere outside the grommet aperture (above MECH-GASKET-3).
    """
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
    in_tunnel = (
        (np.abs(gx_flat) < hw - 0.1)
        & (gz_flat > z_lo + 0.1)
        & (gz_flat < tunnel_roof_z - 0.1)
    )
    # Check solid grommet flange ring (outside Ø20.2 teardrop bore, inside Ø26 spotface)
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
    """
    Genuine B-Rep kinematic insertion sweep checks from the open bottom cavity (Z = 4.0) into seated poses:
      1. SW1 C&K 7211SYZBE DPDT switch (10.67 x 12.7 x 11.43 mm body + lugs + Ø6.35 bushing)
      2. M4x16 CSK bulkhead bolts (straight +Z insertion into both counterbores)
      3. Standard USB-C plug straight +Y insertion through Ø20.2 grommet bore & 13.6x7.8 tunnel into J1
    """
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
        vol = float(inter.volume) if inter is not None else 0.0
        sw_max_vol = max(sw_max_vol, vol)

    # M4x16 CSK bulkhead bolts straight +Z insertion
    z_csk_seat = p.z_cap_bot_bulkhead_start - 4.5
    bolt_tool = bd.Cylinder(1.95, 16.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).fuse(
        bd.Cone(4.0, 1.95, 2.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    )
    bolt_z_steps = np.linspace(p.z_lid_bot_end, z_csk_seat + 0.1, 15)
    bolt_max_vol = 0.0
    for sx in (-1.0, 1.0):
        bx = sx * p.anchor_bot_bolt_x
        for zw in bolt_z_steps:
            inter = cap_bot & bolt_tool.translate((bx, 0.0, float(zw)))
            vol = float(inter.volume) if inter is not None else 0.0
            bolt_max_vol = max(bolt_max_vol, vol)

    # USB-C plug straight +Y insertion from Y_tip = -50.0 to seated Y_tip = -21.21
    y_plug_tip_seated = p.usbc_j1_front_y + p.usbc_mating_depth_mm
    usbc_tool = bd.Box(8.3, p.usbc_specified_barrel_mm + 0.01, 2.5, align=(bd.Align.CENTER, bd.Align.MAX, bd.Align.CENTER)).fuse(
        bd.Box(12.4, 26.0, 6.8, align=(bd.Align.CENTER, bd.Align.MAX, bd.Align.CENTER)).translate((0.0, -p.usbc_specified_barrel_mm, 0.0))
    )
    usbc_y_steps = np.linspace(-50.0, y_plug_tip_seated, 15)
    usbc_max_vol = 0.0
    for yw in usbc_y_steps:
        inter = cap_bot & usbc_tool.translate((0.0, float(yw), p.z_usbc))
        vol = float(inter.volume) if inter is not None else 0.0
        usbc_max_vol = max(usbc_max_vol, vol)

    return {
        "sw1_dpdt_insertion": {"waypoints_tested": len(sw_waypoints), "max_intersection_vol_mm3": round(sw_max_vol, 6), "pass": sw_max_vol < 1e-4},
        "m4x16_bolt_insertion": {"waypoints_tested": int(2 * len(bolt_z_steps)), "max_intersection_vol_mm3": round(bolt_max_vol, 6), "pass": bolt_max_vol < 1e-4},
        "usbc_plug_insertion": {"waypoints_tested": len(usbc_y_steps), "max_intersection_vol_mm3": round(usbc_max_vol, 6), "pass": usbc_max_vol < 1e-4},
        "all_zero": sw_max_vol < 1e-4 and bolt_max_vol < 1e-4 and usbc_max_vol < 1e-4,
    }


def main() -> None:
    out_dir = Path(__file__).resolve().parent

    # Clean up obsolete Rev 4.0 dual-variant files
    for stale in ("mech_cap_bot_usbc.step", "mech_cap_bot_usbc.stl", "cap_bot_usbc_detail.png"):
        p_stale = out_dir / stale
        if p_stale.exists():
            p_stale.unlink()

    # 1. FDM Baseline (Unified Rev 4.1 S1-A / S2-A / S3)
    p_fdm = LepiLEDParams(process="FDM")
    assy_nom = build_assembly_parts(p_fdm)

    mesh_checks = {}
    mesh_checks["mech_lid_bot"] = export_and_verify_stl(
        assy_nom["lid_bot"], out_dir / "mech_lid_bot.step", out_dir / "mech_lid_bot.stl"
    )
    mesh_checks["mech_cap_bot"] = export_and_verify_stl(
        assy_nom["cap_bot"], out_dir / "mech_cap_bot.step", out_dir / "mech_cap_bot.stl"
    )
    mesh_checks["mech_cap_top"] = export_and_verify_stl(
        assy_nom["cap_top"], out_dir / "mech_cap_top.step", out_dir / "mech_cap_top.stl"
    )

    # 2. SLS PA12 Variants
    p_sls = LepiLEDParams(process="SLS")
    mesh_checks["mech_lid_bot_sls"] = export_and_verify_stl(
        build_lid_bot(p_sls), out_dir / "mech_lid_bot_sls.step", out_dir / "mech_lid_bot_sls.stl"
    )
    mesh_checks["mech_cap_bot_sls"] = export_and_verify_stl(
        build_cap_bot(p_sls), out_dir / "mech_cap_bot_sls.step", out_dir / "mech_cap_bot_sls.stl"
    )
    mesh_checks["mech_cap_top_sls"] = export_and_verify_stl(
        build_cap_top(p_sls), out_dir / "mech_cap_top_sls.step", out_dir / "mech_cap_top_sls.stl"
    )

    # 3. Full Assembly STEP + STL + clean per-part STLs
    comp_dir = out_dir / "parts_stl"
    if comp_dir.exists():
        for old_stl in comp_dir.glob("*.stl"):
            old_stl.unlink()
    comp_dir.mkdir(exist_ok=True)
    for k, shp in assy_nom.items():
        bd.export_stl(shp, str(comp_dir / f"{k}.stl"), tolerance=0.04, angular_tolerance=0.15)

    assy_compound = bd.Compound(list(assy_nom.values()))
    bd.export_step(assy_compound, str(out_dir / "lepiled_assembly.step"))
    bd.export_stl(assy_compound, str(out_dir / "lepiled_assembly.stl"), tolerance=0.04, angular_tolerance=0.15)

    # 4. Overhang audits on ALL 3 FDM printed STLs + USB-C grommet flange STL ray-cast
    overhang_checks = {
        "mech_lid_bot": audit_stl_overhangs(out_dir / "mech_lid_bot.stl", (0.0, 0.0, 1.0)),
        "mech_cap_bot": audit_stl_overhangs(out_dir / "mech_cap_bot.stl", (0.0, 0.0, 1.0)),
        "mech_cap_top": audit_stl_overhangs(out_dir / "mech_cap_top.stl", (0.0, 0.0, -1.0)),
    }
    usbc_bezel_raycast = verify_usbc_bezel_wall_stl(out_dir / "mech_cap_bot.stl", p_fdm)

    # 5. Genuine ALL-PAIRS B-Rep interference checks (Nominal & Worst-Case incl. +1.0 mm glass length + all fasteners!)
    wc_glass_len = p_fdm.glass_length + p_fdm.glass_length_tol
    inter_nom = check_all_pairs_intersections(assy_nom)
    assy_wc = build_assembly_parts(
        p_fdm, core_w_override=p_fdm.core_w_max, glass_id_override=p_fdm.glass_id_min,
        glass_od_override=p_fdm.glass_od_max, glass_length_override=wc_glass_len,
    )
    inter_wc = check_all_pairs_intersections(assy_wc)

    # 6. Kinematic B-Rep alcove, bolt & USB-C plug insertion sweep verification
    alcove_checks = check_alcove_insertion(assy_nom["cap_bot"], p_fdm)

    # 7. Assert cap_top topology (zero gasket-2 puncture: euler_number == 0, genus == 1)
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
    all_brep_ok = inter_nom["all_zero"] and inter_wc["all_zero"]
    usbc_plug_contiguous = len(assy_nom["usbc_plug_assy"].solids()) == 1
    usbc_bezel_wall_ok = usbc_bezel_raycast["pass"]
    all_alcove_ok = alcove_checks["all_zero"]
    all_param_checks_ok = all(c["pass"] for c in p_fdm.verify_all().values())

    report = {
        "revision": "Rev 4.1 (S1-A Top-Heatsink-Only + Zero CNC Milling + S2-A USB-C Only + 3A 20mm Grommet + S3 Gold DPDT + B-H3 Preload)",
        "params": p_fdm.to_dict(),
        "mesh_checks": mesh_checks,
        "overhang_checks": overhang_checks,
        "usbc_grommet_flange_raycast": usbc_bezel_raycast,
        "alcove_insertion_checks": alcove_checks,
        "usbc_plug_assy_solids": len(assy_nom["usbc_plug_assy"].solids()),
        "brep_all_pairs_nominal": {k: v for k, v in inter_nom.items() if k != "pairs"},
        "brep_all_pairs_worst_case": {k: v for k, v in inter_wc.items() if k != "pairs"},
        "summary": {
            "all_param_checks_pass": all_param_checks_ok,
            "all_meshes_watertight_manifold": all_meshes_ok,
            "cap_top_euler_zero_genus_one": cap_top_euler_ok,
            "all_overhangs_le_46deg": all_overhangs_ok,
            "usbc_grommet_flange_raycast_ge_2_5mm": usbc_bezel_wall_ok,
            "alcove_kinematic_insertion_zero": all_alcove_ok,
            "usbc_plug_assy_contiguous": usbc_plug_contiguous,
            "nominal_all_pairs_zero": inter_nom["all_zero"],
            "worst_case_all_pairs_zero": inter_wc["all_zero"],
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
    print("=== USB-C & 20 mm Grommet Flange STL Ray-Cast ===")
    print(
        f"  {usbc_bezel_raycast['stl_file']}: rays={usbc_bezel_raycast['grid_rays_total']} "
        f"(wall={usbc_bezel_raycast['wall_rays_checked']}, slot={usbc_bezel_raycast['slot_rays_checked']}), "
        f"anomalies={usbc_bezel_raycast['anomalies']}, min_wall={usbc_bezel_raycast['min_flange_wall_mm']:.4f} mm "
        f"at XZ={usbc_bezel_raycast['min_wall_xz_mm']} | pass={usbc_bezel_raycast['pass']}"
    )
    print("=== Kinematic Alcove, Bolt & USB-C Insertion ===")
    for k in ("sw1_dpdt_insertion", "m4x16_bolt_insertion", "usbc_plug_insertion"):
        v = alcove_checks[k]
        print(f"  {k:22s}: waypoints={v['waypoints_tested']:2d}, max_vol={v['max_intersection_vol_mm3']:.6f} mm^3 | pass={v['pass']}")
    print("=== All-Pairs B-Rep Intersection (incl. ALL fasteners + 151.0 mm glass WC) ===")
    for label, d in [("NOMINAL", inter_nom), ("WORST_CASE", inter_wc)]:
        print(f"  {label:10s}: {d['total_pairs_checked']} pairs, nonzero={d['nonzero_count']} {d['nonzero_pairs']}")

    if not report["summary"]["overall_pass"]:
        raise SystemExit(1)
    print(f"Wrote {verif_path} and all STEP/STL artifacts (ALL CHECKS PASS).")


if __name__ == "__main__":
    main()
