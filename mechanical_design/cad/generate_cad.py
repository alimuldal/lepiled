#!/usr/bin/env python3
"""
Parametric 3D CAD Generator for LepiLED DIY Maxi Switch using build123d.

Key features and automated verification gates:
  - Committed JLCPCB 36.0 x 46.0 x 1.6 mm driver_pcb mounted vertically on the +X core face.
  - Open meshed cooling chimney through 30 x 30 x 2.0 mm x 300.0 mm bare Al 6063-T6 core
    (4 plain Ø4.5 mm clearance holes total, zero aluminum tapping; LED stars bonded with 2-part thermal epoxy).
  - Compact tapered white bottom nosecone (Ø40 -> Ø71 x 34.0 mm) with screened chimney inlet,
    45-deg water-shedding top lip, and single M4 x 50 mm stainless cross-bolt.
  - Top-head electronics bay with bolt-compressed axial face O-ring (88 x 2.5 mm VMQ50),
    recessed draining -X switch cove (true round Ø6.5 mm bore), downward-draining -Y breather vent,
    compressing +Y split cable clamp (10.5 mm grommet chamber, 1.2 mm standoff, slotted pan-head bolts),
    flexible +Y eaves C-clip, 1.4 mm eaves drip kerf, and 0.6 mm translucent internal dimple over D12.
  - Exports 6 watertight, support-free FDM parts (STEP + STL), including pre-mirrored cable clamp pair.
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


SMD_PACKAGE_DIMS: dict[str, tuple[float, float, float]] = {
    "U1": (3.0, 2.8, 1.0), "U2": (3.0, 2.8, 1.0),
    "U3": (6.9, 4.9, 1.75),
    "U4": (6.9, 4.9, 1.75),
    "U5": (3.0, 2.5, 1.12),
    "Q2": (3.0, 2.5, 1.12), "Q3": (3.0, 2.5, 1.12),
    "F1": (3.4, 1.8, 0.85),
    "D9": (4.6, 2.8, 2.30), "D10": (4.6, 2.8, 2.30),
    "D11": (4.7, 3.8, 2.44),
    "D12": (1.7, 0.9, 0.80),
    "D15": (3.0, 2.5, 1.12), "D16": (3.0, 2.5, 1.12),
    "L1": (6.1, 6.1, 4.50), "L2": (6.1, 6.1, 4.50),
    "R3": (3.3, 1.7, 0.70), "R4": (3.3, 1.7, 0.70),
    "R7": (6.5, 3.3, 0.75),
    "R10": (2.1, 1.3, 0.65), "R13": (2.1, 1.3, 0.65), "R14": (2.1, 1.3, 0.65),
    "R22": (2.1, 1.3, 0.65), "R23": (2.1, 1.3, 0.65), "R24": (2.1, 1.3, 0.65),
    "C2": (2.1, 1.3, 1.40), "C3": (2.1, 1.3, 1.40), "C11": (2.1, 1.3, 1.40),
    "C10": (3.3, 1.7, 1.80),
}


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


def _teardrop_profile_wire(radius: float, angle_deg: float = 42.0) -> bd.Face:
    """Horizontal-hole teardrop Face in XY plane with +Y apex (roof <= angle_deg overhang)."""
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


def _pentagon_gable_sketch(plane: bd.Plane, half_w: float, z_bot: float, z_apex: float) -> bd.Sketch:
    """Horizontal-port pentagon with flat bottom and 45-deg roof."""
    z_sh = z_apex - half_w
    assert z_sh > z_bot + 0.5, f"Degenerate gable: z_sh={z_sh} <= z_bot={z_bot}"
    with bd.BuildSketch(plane) as sk:
        with bd.BuildLine():
            bd.Polyline([
                (-half_w, z_bot),
                (half_w, z_bot),
                (half_w, z_sh),
                (0.0, z_apex),
                (-half_w, z_sh),
                (-half_w, z_bot),
            ])
        bd.make_face()
    return sk.sketch


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


def build_cap_bot(p: LepiLEDParams) -> bd.Part:
    """
    MECH-CAP-BOT — Compact Tapered Funnel Nosecone with Open Screened Chimney Inlet (Z = 0.0 .. 34.0 mm):
      - 45-deg cone Ø40.0 -> Ø71.0 mm (Z = 0.0 .. 15.5) + Ø71.0 collar (15.5 .. 31.7) + 45-deg water-shedding top bevel (31.7 .. 34.0)
      - Open 22 x 22 mm (R3) screened chimney inlet at tip + 28.4 x 28.4 x 0.8 mm stainless mesh seat beneath Al core
      - Single M4 x 50 mm A2 stainless cross-bolt along ±X at Z = 12.5 mm inside recessed 45-deg-roofed flat spotfaces
    """
    r_tip = p.cap_bot_tip_od / 2.0      # 20.0
    r_col = p.cap_bot_collar_od / 2.0   # 35.5
    h_cone = p.cap_bot_cone_h           # 15.5
    z_top = p.z_cap_bot_top             # 34.0
    bevel_h = 2.3                       # 45-deg outward watershed bevel on top lip (Z = 31.7 .. 34.0 -> R = 35.5 -> 33.2)

    lower_cone = bd.Cone(r_tip, r_col, h_cone, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    mid_cyl = bd.Cylinder(r_col, (z_top - bevel_h) - h_cone, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, h_cone))
    top_bevel = bd.Cone(r_col, r_col - bevel_h, bevel_h, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, z_top - bevel_h))
    part = lower_cone.fuse(mid_cyl).fuse(top_bevel)

    # Annular shroud bore (Ø61.6 x Ø49.0 mm, Z = 18.3 .. 34.0 mm) + MECH-GASKET-1 (60 x 3.5 mm VMQ50)
    r_bore = p.glass_bore_id / 2.0      # 30.8
    r_hub = p.core_hub_od / 2.0         # 24.5
    z_bore_bot = p.z_glass_bot - 1.2    # 18.3
    shroud_annulus = (
        bd.Cylinder(r_bore, z_top - z_bore_bot + 0.5, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
        - bd.Cylinder(r_hub, z_top - z_bore_bot + 1.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, -0.2))
    ).translate((0, 0, z_bore_bot))
    g1 = _radial_bore_oring_cut(r_bore, p.glass_oring_groove_od / 2.0, p.z_glass_bot + 4.0, p.glass_oring_flat_w, ramp_dir=+1.0)
    mouth_lead = (
        bd.Cone(r_bore, r_bore + 0.7, 1.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX))
        - bd.Cylinder(r_hub + 0.5, 1.4, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)).translate((0, 0, 0.2))
    ).translate((0, 0, z_top + 0.1))
    part = part - shroud_annulus - g1 - mouth_lead

    # 31.1 x 31.1 mm core socket (Z = 6.0 .. 34.0 mm) + 0.8 mm mesh pocket (Z = 5.2 .. 6.0 mm) + 22 x 22 mm R3 open chimney inlet
    # + backed 1.8 x 2.5 mm rounded-square neutral-sealant V-groove at Z = 31.5 .. 34.0 mm sealing core socket from optical chamber!
    core_sock = bd.Box(p.core_pocket_w, p.core_pocket_w, z_top - p.z_core_bot + 1.0,
                       align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, p.z_core_bot))
    mesh_pkt = bd.Box(28.4, 28.4, 1.2, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, p.z_core_bot - 0.8))
    with bd.BuildSketch(bd.Plane.XY.offset(-1.0)) as sk_in:
        bd.RectangleRounded(p.cap_bot_inlet_w, p.cap_bot_inlet_w, radius=3.0)
    inlet_cut = bd.extrude(sk_in.sketch, p.z_core_bot + 2.0)
    w_bg = p.core_pocket_w + 2.0 * p.cap_bot_seal_groove  # 34.7 mm w/ R5.5 corners -> 2.24 mm corner hub wall, 0 overhang
    with bd.BuildSketch(bd.Plane.XY.offset(z_top - p.cap_bot_seal_depth)) as sk_bg0:
        bd.Rectangle(p.core_pocket_w, p.core_pocket_w)
    with bd.BuildSketch(bd.Plane.XY.offset(z_top + 0.05)) as sk_bg1:
        bd.RectangleRounded(w_bg, w_bg, radius=5.5)
    bot_seal_cut = bd.loft([sk_bg0.sketch, sk_bg1.sketch])
    part = part - core_sock - mesh_pkt - inlet_cut - bot_seal_cut

    # Single M4 x 50 mm A2 stainless cross-bolt along ±X at Z = 12.5 mm + 45-deg-roofed flat bearing spotfaces at |X| = 21.0 mm
    td_m4 = _teardrop_profile_wire(p.core_bolt_hole_dia / 2.0, 42.0)
    m4_bore = bd.extrude(td_m4, 76.0).rotate(bd.Axis.X, 90.0).rotate(bd.Axis.Z, 90.0).translate((-38.0, 0.0, p.z_bot_bolt))
    part = part - m4_bore

    for sx in (-1.0, 1.0):
        # 45-deg gable pocket on ±X from |X| = 21.0 outward (Z = 7.8 .. 18.0 mm -> stays strictly below z_bore_bot = 18.3!)
        pl_sf = bd.Plane(origin=(sx * 21.0, 0.0, 0.0), x_dir=(0.0, sx, 0.0), z_dir=(sx, 0.0, 0.0))
        sk_sf = _pentagon_gable_sketch(pl_sf, 4.6, p.z_bot_bolt - 4.7, p.z_bot_bolt + 5.6)
        sf_cut = bd.extrude(sk_sf, 18.0)
        part = part - sf_cut

    return part


def build_top_base(p: LepiLEDParams) -> bd.Part:
    """
    MECH-TOP-BASE — Top-Head Electronics Chassis (Z = 120.0 .. 220.5 mm, prints upright):
      - Lower Ø71.0 mm shroud collar (MECH-GASKET-2 + ±Y 9.0 x 7.5 mm JST-XH wire slots)
      - 45-deg flare Ø71.0 -> Ø94.0 mm (Z = 133.5 .. 145.0 mm; 3.0 mm solid bulkhead above shroud stop cone)
      - 26.0 mm side-port ring (Z = 145.0 .. 171.0 mm, OD Ø94.0, ID Ø78.0):
          * +Y flat boss: 45-deg gable USB-C port + 45-deg wedge pocket + 2x blind M3x5 inserts + internal zip-tie bridge
          * -X recessed 32 mm draining finger cove (18-deg sloped floor) + true round Ø6.50 mm SW1 bore + keyed anti-rotation pocket
          * -Y downward-draining 35-deg breather bore from flat dry-bay floor pocket (Ø9.5 x 0.8 mm) out 45-deg flare underside
          * 4x diagonal 45-deg-gusseted bolt ears (R = 51.0 mm) with flush 90-deg M3x12 CSK bores
      - Flat Z = 171.0 mm deck with bolt-compressed axial face O-ring groove (MECH-GASKET-3: 88 x 2.5 mm VMQ50)
        + 2.0 mm centering pilot lip
      - Continuous 2.0 mm thermal baffle on +X (X = 15.55 .. 17.55) + 2x beefy 9.0 mm-wide PCB stanchions at Y = ±14.0 mm
    """
    z_bot = p.z_top_base_bot            # 120.0
    z_fl_bot = p.top_base_flare_bot_z   # 133.5
    z_port_bot = p.z_top_base_port_bot  # 145.0
    z_deck = p.z_top_base_deck_top      # 171.0
    r_col = p.top_base_collar_od / 2.0  # 35.5
    r_port = p.top_base_port_od / 2.0   # 47.0
    r_port_in = p.top_base_port_id / 2.0  # 39.0
    r_deck = p.top_base_deck_od / 2.0   # 49.0

    # 1. Outer body: lower collar + 45-deg flare + side-port ring + 2.0 mm 45-deg top deck lip
    c_col = bd.Cylinder(r_col, z_fl_bot - z_bot, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, z_bot))
    c_flare = bd.Cone(r_col, r_port, z_port_bot - z_fl_bot, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, z_fl_bot))
    c_ring = bd.Cylinder(r_port, (z_deck - 2.0) - z_port_bot, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, z_port_bot))
    c_deck_lip = bd.Cone(r_port, r_deck, 2.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, z_deck - 2.0))
    part = c_col.fuse(c_flare).fuse(c_ring).fuse(c_deck_lip)

    # 2. +Y flat vertical clamp boss (X = ±18.5 mm, Y = 47.0 mm, Z = 145.0 .. 168.5 mm) w/ <=42.2-deg ramp tucked inside c_col
    with bd.BuildSketch(bd.Plane.XY.offset(z_port_bot - 21.0)) as sk_py0:
        bd.Rectangle(22.0, 2.0)
    with bd.BuildSketch(bd.Plane.XY.offset(z_port_bot)) as sk_py1:
        bd.Rectangle(37.0, 14.0)
    py_ramp = bd.loft([sk_py0.sketch.translate((0.0, 28.5, 0.0)), sk_py1.sketch.translate((0.0, r_port - 7.0, 0.0))])
    py_pad = bd.Box(37.0, 12.0, (z_deck - 2.5) - z_port_bot, align=(bd.Align.CENTER, bd.Align.MAX, bd.Align.MIN)).translate((0.0, r_port, z_port_bot))
    part = part.fuse(py_ramp).fuse(py_pad)

    # 3. 4x diagonal 43-deg-gusseted M3 CSK bolt ears at 45/135/225/315 deg (R = 51.0 mm, Z = 163.0 .. 171.0 mm)
    r_eb = p.top_base_ear_boss_r  # 5.5
    z_ear_bot = z_deck - p.top_base_ear_h  # 163.0
    for deg in (45.0, 135.0, 225.0, 315.0):
        # Capsule spanning Y = 40.5 .. 56.5 (center Y = 48.5, length = 16.0, width = 11.0 -> circle centered at 51.0!)
        with bd.BuildSketch(bd.Plane.XY.offset(z_ear_bot)) as sk_ear_top:
            bd.SlotOverall(16.0, 2.0 * r_eb, rotation=90.0)
        ear_top = bd.extrude(sk_ear_top.sketch.translate((0.0, 48.5, 0.0)), p.top_base_ear_h).rotate(bd.Axis.Z, deg - 90.0)
        with bd.BuildSketch(bd.Plane.XY.offset(z_ear_bot - 11.8)) as sk_ear_bot:
            bd.Circle(r_eb)
        with bd.BuildSketch(bd.Plane.XY.offset(z_ear_bot)) as sk_ear_mid:
            bd.SlotOverall(16.0, 2.0 * r_eb, rotation=90.0)
        ear_gusset = bd.loft([
            sk_ear_bot.sketch.translate((0.0, r_port - r_eb - 0.8, 0.0)),
            sk_ear_mid.sketch.translate((0.0, 48.5, 0.0)),
        ]).rotate(bd.Axis.Z, deg - 90.0)
        part = part.fuse(ear_top).fuse(ear_gusset)

    # 4. 2.0 mm-tall centering pilot rim on Z = 171.0 .. 173.0 mm (R = 39.0 .. 42.15 mm -> 0.35 mm slip fit in cap_top bore!)
    pilot = (
        bd.Cylinder(p.cap_top_bore_id / 2.0 - 0.35, 2.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
        - bd.Cylinder(r_port_in, 3.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, -0.5))
    ).translate((0.0, 0.0, z_deck))
    pilot_top_e = pilot.edges().filter_by(bd.GeomType.CIRCLE).filter_by_position(bd.Axis.Z, z_deck + 1.9, z_deck + 2.1)
    outer_p = [e for e in pilot_top_e if e.radius > 41.5]
    if outer_p:
        pilot = bd.chamfer(outer_p, length=0.6)
    part = part.fuse(pilot)

    # 5. Cut open interior dry bay inside side-port ring (Z = 145.0 .. 172.0 mm, R = 39.0 mm)
    bay_cav = bd.Cylinder(r_port_in, z_deck - z_port_bot + 3.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, z_port_bot))
    part = part - bay_cav

    # 5b. Internal -X reinforced switch-pocket boss backing the 5.5 mm recessed cove (X = -39.0 .. -33.5, Z = 145.0 .. 171.0)
    x_sw_face = -(r_port - p.sw1_recess_x)  # -41.5
    sw_inner_boss = bd.Box(7.0, 21.0, z_deck - z_port_bot, align=(bd.Align.MIN, bd.Align.CENTER, bd.Align.MIN)).translate((x_sw_face + p.sw1_wall_thick - 1.0, 0.0, z_port_bot))
    part = part.fuse(sw_inner_boss)

    # 5c. Internal +Y zip-tie cable strain-relief bridge (X = +10.5, Y = 34.5, Z = 145.0..154.0) with 45-deg gable slot
    zt_post = bd.Box(5.0, 6.0, 9.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((10.5, 34.5, z_port_bot))
    pl_zt = bd.Plane(origin=(7.5, 34.5, 0.0), x_dir=(0.0, 1.0, 0.0), z_dir=(1.0, 0.0, 0.0))
    sk_zt = _pentagon_gable_sketch(pl_zt, 2.0, z_port_bot + 1.5, z_port_bot + 6.5)
    zt_slot = bd.extrude(sk_zt, 6.0)
    part = part.fuse(zt_post) - zt_slot

    # 6. Solid 1.5 mm insulating barrier behind J1/J4 + captive 15.6 x 15.6 mm thermal-bridge chute behind U1/U2
    #    + 2x vertical PCB stanchions at Y = ±14.0 mm with side-entry captive M3 hex nut pockets (5.5 mm B.Cu->Al gap)
    x_core_wall = p.core_pocket_w / 2.0   # 15.55
    x_baf_out = x_core_wall + p.core_sleeve_wall  # 17.05
    z_cradle_top = p.z_pcb_top + 2.3      # 222.8 (11.1 mm below internal bell ceiling cone; houses 45-deg roofs)
    baffle = bd.Box(p.core_sleeve_wall + 1.0, 2.0 * (p.pcb_hole_y + 4.5), z_cradle_top - z_port_bot,
                    align=(bd.Align.MIN, bd.Align.CENTER, bd.Align.MIN)).translate((x_core_wall - 1.0, 0.0, z_port_bot))
    part = part.fuse(baffle)

    # Captive 15.6 x 15.6 mm thermal-bridge guide chute (X = 15.55 .. 19.50 -> 1.0 mm clearance behind B.Cu for silicone pad!)
    x_chute_out = p.pcb_x_bcu - 1.0       # 19.50
    z_win_bot = p.pcb_thermal_win_z_bot   # 199.0 (3.0 mm above J4 pins)
    z_win_sh = z_win_bot + p.pcb_thermal_win_h  # 214.4
    half_win = 0.5 * p.pcb_thermal_win_w  # 7.80
    # Bottom shelf (Z = 198.2 .. 199.0) + 45-deg underside ramp from X=17.05 (Z=195.75) to X=19.50 (Z=198.2) -> 0 overhang, clears J4 pins!
    chute_shelf = bd.Box(x_chute_out - x_core_wall, 19.0, 0.8, align=(bd.Align.MIN, bd.Align.CENTER, bd.Align.MAX)).translate((x_core_wall, 0.0, z_win_bot))
    ramp_dx = x_chute_out - x_baf_out  # 2.45
    with bd.BuildSketch(bd.Plane.XZ) as sk_cr:
        with bd.BuildLine():
            bd.Polyline([
                (x_baf_out - 0.5, z_win_bot - 0.8 - ramp_dx),
                (x_baf_out, z_win_bot - 0.8 - ramp_dx),
                (x_chute_out, z_win_bot - 0.8),
                (x_baf_out - 0.5, z_win_bot - 0.8),
                (x_baf_out - 0.5, z_win_bot - 0.8 - ramp_dx),
            ])
        bd.make_face()
    chute_ramp = bd.extrude(sk_cr.sketch, 9.5, both=True)
    part = part.fuse(chute_shelf).fuse(chute_ramp)

    # Left & right vertical chute rails (Y = ±7.80 .. ±9.50, Z = 198.2 .. 214.4 -> stops below J2/J3 pins!)
    for sy in (-1.0, 1.0):
        rail = bd.Box(x_chute_out - x_core_wall, 9.5 - half_win + 0.5, z_win_sh - (z_win_bot - 0.8),
                      align=(bd.Align.MIN, bd.Align.MIN if sy > 0 else bd.Align.MAX, bd.Align.MIN)).translate(
            (x_core_wall, sy * half_win, z_win_bot - 0.8)
        )
        part = part.fuse(rail)

    for sy in (-1.0, 1.0):
        hy = sy * p.pcb_hole_y  # ±14.0
        # 9.0 mm-wide stanchion body (X = 15.55 .. 19.90) + stepped 6.0 mm-wide front land (X = 19.90 .. 20.50)
        st_body = bd.Box((p.pcb_x_bcu - 0.6) - x_core_wall, p.pcb_standoff_body_od, z_cradle_top - z_port_bot,
                         align=(bd.Align.MIN, bd.Align.CENTER, bd.Align.MIN)).translate((x_core_wall, hy, z_port_bot))
        st_tip = bd.Box(1.0, p.pcb_standoff_tip_od, z_cradle_top - (p.z_pcb_bot - 1.5),
                        align=(bd.Align.MAX, bd.Align.CENTER, bd.Align.MIN)).translate((p.pcb_x_bcu, hy, p.z_pcb_bot - 1.5))
        with bd.BuildSketch(bd.Plane.XY.offset(p.z_pcb_bot - 2.5)) as sk_t0:
            bd.Rectangle(0.6, p.pcb_standoff_tip_od)
        with bd.BuildSketch(bd.Plane.XY.offset(p.z_pcb_bot - 1.5)) as sk_t1:
            bd.Rectangle(1.4, p.pcb_standoff_tip_od)
        st_tip_ramp = bd.loft([
            sk_t0.sketch.translate((p.pcb_x_bcu - 1.1, hy, 0.0)),
            sk_t1.sketch.translate((p.pcb_x_bcu - 0.7, hy, 0.0)),
        ])
        part = part.fuse(st_body).fuse(st_tip).fuse(st_tip_ramp)

    # Cut through-window in captive 15.6 x 15.6 mm thermal-bridge chute (45-deg gable roof -> 0 overhang!)
    pl_win = bd.Plane(origin=(x_core_wall - 1.0, 0.0, 0.0), x_dir=(0.0, 1.0, 0.0), z_dir=(1.0, 0.0, 0.0))
    sk_win = _pentagon_gable_sketch(pl_win, half_win, z_win_bot, z_win_sh + half_win)
    part = part - bd.extrude(sk_win, 6.0)

    # 7. Cut bolt-compressed axial face O-ring groove on flat Z = 171.0 mm deck (MECH-GASKET-3: 88 x 2.5 mm VMQ50)
    r_g3_in = p.top_oring_groove_r_in                          # 43.6
    r_g3_out = p.top_oring_groove_r_in + p.top_oring_groove_w  # 47.0
    g3_cut = (
        bd.Cylinder(r_g3_out, p.top_oring_groove_depth + 0.2, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX))
        - bd.Cylinder(r_g3_in, p.top_oring_groove_depth + 0.6, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)).translate((0, 0, 0.2))
    ).translate((0.0, 0.0, z_deck + 0.2))
    part = part - g3_cut

    # 8. Cut 4x side-entry captive M3 hex nut pockets (X = 16.55..19.15, 45-deg roof -> 0 overhang!) + Ø3.4 mm teardrop M3 bores
    td_ins = _teardrop_profile_wire(p.m3_insert_pilot_dia / 2.0, 42.0)  # Reused for +Y blind clamp inserts below
    td_m3 = _teardrop_profile_wire(p.m3_clearance_dia / 2.0, 42.0)
    x_nut_c = x_core_wall + 1.0 + 1.30  # 17.85 (slot X = 16.55 .. 19.15 -> 1.00 mm back wall, 1.35 mm front lip)
    for sy in (-1.0, 1.0):
        for sz in (-1.0, 1.0):
            hy = sy * p.pcb_hole_y
            hz = p.pcb_z_center + sz * p.pcb_hole_z
            # Side-entry nut slot from outer face |Y| = 18.6 inward to |Y| = 10.6 (8.0 mm deep, leaves 1.1 mm inner wall)
            pl_nut = bd.Plane(origin=(x_nut_c, sy * 18.6, 0.0), x_dir=(sy, 0.0, 0.0), z_dir=(0.0, -sy, 0.0))
            sk_nut = _pentagon_gable_sketch(pl_nut, 1.30, hz - 2.90, hz + 2.90 + 1.30)
            part = part - bd.extrude(sk_nut, 8.0)
            # Horizontal Ø3.4 mm M3 clearance bore from X = 20.7 inward to X = 16.05 (stops 0.50 mm before core wall!)
            m3_bore = bd.extrude(td_m3, p.pcb_x_bcu - 16.05 + 0.2).rotate(bd.Axis.X, 90.0).rotate(bd.Axis.Z, -90.0).translate((p.pcb_x_bcu + 0.2, hy, hz))
            part = part - m3_bore

    # 9. Cut 4x flush 90-deg M3x12 CSK bores through diagonal bolt ears (Z = 163.0 .. 171.0)
    for deg in (45.0, 135.0, 225.0, 315.0):
        rad = math.radians(deg)
        ex, ey = p.top_base_ear_r * math.cos(rad), p.top_base_ear_r * math.sin(rad)
        c_thru = bd.Cylinder(p.m3_clearance_dia / 2.0, p.top_base_ear_h + 2.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((ex, ey, z_ear_bot - 1.0))
        c_csk = bd.Cone(3.25, p.m3_clearance_dia / 2.0, 3.25 - p.m3_clearance_dia / 2.0,
                        align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((ex, ey, z_ear_bot - 0.05))
        part = part - c_thru - c_csk

    # 10. Cut +Y horizontal 45-deg gable USB-C cable port + 45-deg wedge seat + 2x blind M3x5.0 inserts
    z_pbot = 148.0
    z_papex = 165.0
    pl_in = bd.Plane(origin=(0.0, 37.5, 0.0), x_dir=(-1.0, 0.0, 0.0), z_dir=(0.0, 1.0, 0.0))
    sk_p_str = _pentagon_gable_sketch(pl_in, 0.5 * p.clamp_port_w, z_pbot, z_papex)
    port_straight = bd.extrude(sk_p_str, 7.6)  # Y = 37.5 .. 45.1
    pl_w0 = bd.Plane(origin=(0.0, 45.0, 0.0), x_dir=(-1.0, 0.0, 0.0), z_dir=(0.0, 1.0, 0.0))
    pl_w1 = bd.Plane(origin=(0.0, r_port + 0.1, 0.0), x_dir=(-1.0, 0.0, 0.0), z_dir=(0.0, 1.0, 0.0))
    sk_w0 = _pentagon_gable_sketch(pl_w0, 0.5 * p.clamp_port_w, z_pbot, z_papex)
    sk_w1 = _pentagon_gable_sketch(pl_w1, 0.5 * p.clamp_port_w + 2.1, z_pbot, z_papex)
    port_wedge = bd.loft([sk_w0, sk_w1])
    part = part - port_straight - port_wedge

    for sx in (-1.0, 1.0):
        cb_bore = bd.extrude(td_ins, p.m3_insert_blind_depth + 0.2).rotate(bd.Axis.X, 90.0).translate((sx * p.clamp_bolt_dx, r_port + 0.2, p.clamp_z))
        part = part - cb_bore

    # 11. Cut -X widened 32 mm, 18-deg outward-draining finger cove + true round Ø6.50 mm SW1 bore + keyed pocket!
    cove_w = p.sw1_cove_w  # 32.0 along ±Y
    z_cove_ceil = 162.5
    z_cove_fl_in = 147.2
    z_cove_fl_out = 144.8  # ~18-deg outward-downward drain slope across 7.5 mm!
    # Cut cove prism in XZ plane (X_local -> global X, Y_local -> global Z), extruded symmetrically along Y = [-16, +16]
    with bd.BuildSketch(bd.Plane.XZ) as sk_cove:
        with bd.BuildLine():
            bd.Polyline([
                (x_sw_face, z_cove_fl_in),
                (x_sw_face - 12.0, z_cove_fl_out - 1.5),
                (x_sw_face - 12.0, 169.5),
                (-r_port - 1.0, 169.5),
                (x_sw_face, z_cove_ceil),  # 42.8-deg sloped ceiling staying cleanly below Z = 171.0 deck!
                (x_sw_face, z_cove_fl_in),
            ])
        bd.make_face()
    cove_cut = bd.extrude(sk_cove.sketch, cove_w / 2.0, both=True)

    # True round Ø6.50 mm horizontal bore (360-deg flat sealing surface for C&K 759D02000 boot!)
    sw_bore = bd.Cylinder(p.sw1_hole_dia / 2.0, 12.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER)).rotate(bd.Axis.Y, 90.0).translate((x_sw_face + 2.0, 0.0, p.sw1_z))

    # Internal anti-rotation pocket + 45-deg roofed keyway slot on +Y edge of bushing bore (aligns C&K 7211 keyway)
    pl_sw = bd.Plane(origin=(x_sw_face + p.sw1_wall_thick, 0.0, 0.0), x_dir=(0.0, 1.0, 0.0), z_dir=(1.0, 0.0, 0.0))
    sw_hw = 0.5 * (p.sw1_body_w_y + 0.8)  # 6.75 mm along ±Y
    sw_z_bot = p.sw1_z - 0.5 * (p.sw1_body_h_z + 0.8)  # 149.385
    sw_z_apex = p.sw1_z + 0.5 * (p.sw1_body_h_z + 0.8) + sw_hw  # 168.365 < 171.0
    sk_sw_rec = _pentagon_gable_sketch(pl_sw, sw_hw, sw_z_bot, sw_z_apex)
    sw_recess = bd.extrude(sk_sw_rec, 8.0)
    pl_key = bd.Plane(origin=(x_sw_face - 0.5, 0.0, 0.0), x_dir=(0.0, 1.0, 0.0), z_dir=(1.0, 0.0, 0.0))
    sk_key = _pentagon_gable_sketch(pl_key, 0.8, p.sw1_z - 1.0, p.sw1_z + 1.6)
    sw_key = bd.extrude(sk_key, 3.5).translate((0.0, p.sw1_hole_dia / 2.0 + 0.2, 0.0))
    part = part - cove_cut - sw_bore - sw_recess - sw_key

    # 12. Cut -Y downward-draining 35-deg ePTFE breather bore from flat dry-bay floor pocket out 45-deg flare underside!
    #     Centered at (0, vent_floor_y=-33.8, Z=144.2); rotate(Axis.X, -35 deg) tilts -Z axis toward -Y (downward & outward),
    #     exiting cleanly through the sheltered 45-deg flare underside at (Y=-38.9, Z=136.9) with 35-deg max overhang (0 >46 deg)!
    vent_pkt = bd.Cylinder(p.vent_pocket_dia / 2.0, p.vent_pocket_depth + 0.5, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)).translate((0.0, p.vent_floor_y, z_port_bot + 0.5))
    vent_bore = (
        bd.Cylinder(p.vent_hole_dia / 2.0, 21.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX))
        .translate((0.0, 0.0, 3.0))
        .rotate(bd.Axis.X, -35.0)
        .translate((0.0, p.vent_floor_y, z_port_bot - p.vent_pocket_depth))
    )
    part = part - vent_pkt - vent_bore

    # 13. Cut lower annular shroud bore (Ø61.6 x Ø49.0 mm, Z = 120.0 .. 135.7) + 45-deg ceiling cone + MECH-GASKET-2
    r_bore = p.glass_bore_id / 2.0  # 30.8
    r_hub = p.core_hub_od / 2.0     # 24.5
    z_bore_top = p.z_glass_top + 1.2  # 135.7
    shroud_annulus = (
        bd.Cylinder(r_bore, z_bore_top - z_bot + 0.5, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
        - bd.Cylinder(r_hub, z_bore_top - z_bot + 1.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, -0.2))
    ).translate((0, 0, z_bot - 0.5))
    cone_h = r_bore - r_hub  # 6.3 mm -> ends at Z = 142.0 mm (3.0 mm solid bulkhead below Z = 145.0 bay floor)
    shroud_stop = (
        bd.Cone(r_bore, r_hub, cone_h, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
        - bd.Cylinder(r_hub, cone_h + 0.4, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, -0.2))
    ).translate((0, 0, z_bore_top))
    # G2 groove with small 0.6 mm retention flat above ramp so PMMA insertion never wedges O-ring!
    g2 = _radial_bore_oring_cut(r_bore, p.glass_oring_groove_od / 2.0, z_bot + 3.0, p.glass_oring_flat_w, ramp_dir=+1.0)
    mouth_lead = (
        bd.Cone(r_bore + 0.7, r_bore, 1.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
        - bd.Cylinder(r_hub + 0.5, 1.4, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, -0.2))
    ).translate((0, 0, z_bot - 0.1))
    part = part - shroud_annulus - shroud_stop - g2 - mouth_lead

    # 14. Cut central 31.1 x 31.1 mm core bore + 2x uncrossed ±Y 9.0 x 7.5 mm JST-XH wire slots!
    core_thru = bd.Box(p.core_pocket_w, p.core_pocket_w, z_cradle_top - z_bot + 4.0,
                       align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, z_bot - 1.0))
    part = part - core_thru
    y_slot_c = p.core_pocket_w / 2.0 + p.core_wire_slot_d / 2.0 - 0.1  # 19.20 mm
    for sy in (-1.0, 1.0):
        wslot = bd.Box(p.core_wire_slot_w, p.core_wire_slot_d + 0.2, (z_port_bot + 2.0) - (z_bot - 1.0),
                       align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0.0, sy * y_slot_c, z_bot - 1.0))
        part = part - wslot

    return part


def build_cap_top(p: LepiLEDParams) -> bd.Part:
    """
    MECH-CAP-TOP — White Umbrella Rain Bell (Z = 171.0 .. 257.0 mm, prints upright, zero roof or collar holes):
      - Ø118.0 mm eaves w/ support-free 1.4 mm underside drip kerf, 4x M3x5.0 inserts at R = 51.0 mm,
        compliant flexible +Y cable C-clip + zip-tie slot, and -X rain-hood visor brow w/ tactile 0/1/2 ribs
      - Straight Ø85.0 mm inner bore (>= 6.7 mm wire-bend space behind J2/J3) + 0.60 mm translucent internal dimple
        opposite D12 (red 20 V PD LED visible through white shell with zero exterior hole)
      - Unbroken 30.6-deg rain roof -> 10.0 mm vertical collar with 30-deg outward-chamfered top lip & backed
        2.5 x 3.0 mm neutral-sealant V-groove (zero unsealed collar screws)
    """
    z_bot = p.z_cap_top_bot                             # 171.0
    z_eaves_top = p.z_cap_top_eaves_top                 # 181.0
    z_tap_top = z_eaves_top + p.cap_top_eaves_taper_h   # 194.4
    z_roof_bot = p.cap_top_roof_bot_z                   # 232.0
    z_col_bot = p.z_cap_top_collar_bot                  # 247.0
    z_top = p.z_cap_top_top                             # 257.0
    r_eaves = p.cap_top_eaves_od / 2.0                  # 59.0
    r_bell = p.cap_top_bell_od / 2.0                    # 45.6
    r_bore = p.cap_top_bore_id / 2.0                    # 42.5

    c_eaves = bd.Cylinder(r_eaves, z_eaves_top - z_bot, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, z_bot))
    c_taper = bd.Cone(r_eaves, r_bell, z_tap_top - z_eaves_top, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, z_eaves_top))
    c_bell = bd.Cylinder(r_bell, z_roof_bot - z_tap_top, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, z_tap_top))

    with bd.BuildSketch(bd.Plane.XY.offset(z_roof_bot)) as sk_roof_bot:
        bd.Circle(r_bell)
    with bd.BuildSketch(bd.Plane.XY.offset(z_col_bot)) as sk_roof_top:
        bd.RectangleRounded(p.cap_top_collar_w, p.cap_top_collar_w, radius=p.cap_top_collar_r)
    c_roof = bd.loft([sk_roof_bot.sketch, sk_roof_top.sketch])

    # Vertical collar with 1.8 mm 30-deg outward watershed chamfer on top perimeter
    col_str_h = p.cap_top_collar_h - 1.5
    with bd.BuildSketch(bd.Plane.XY.offset(z_col_bot)) as sk_col:
        bd.RectangleRounded(p.cap_top_collar_w, p.cap_top_collar_w, radius=p.cap_top_collar_r)
    c_collar = bd.extrude(sk_col.sketch, col_str_h)
    with bd.BuildSketch(bd.Plane.XY.offset(z_col_bot + col_str_h)) as sk_ct0:
        bd.RectangleRounded(p.cap_top_collar_w, p.cap_top_collar_w, radius=p.cap_top_collar_r)
    with bd.BuildSketch(bd.Plane.XY.offset(z_top)) as sk_ct1:
        bd.RectangleRounded(p.cap_top_collar_w - 3.0, p.cap_top_collar_w - 3.0, radius=2.8)
    c_col_bev = bd.loft([sk_ct0.sketch, sk_ct1.sketch])

    part = c_eaves.fuse(c_taper).fuse(c_bell).fuse(c_roof).fuse(c_collar).fuse(c_col_bev)

    # +Y Compliant Flexible Snap-In Cable C-Clip (2.0 mm flexible jaw wall, 4.0 mm chamfered entry, tucked near eaves)
    y_clip = 60.5  # Protrudes only 5.5 mm past R = 59 eaves to Y = 64.5 mm
    with bd.BuildSketch(bd.Plane.XY.offset(z_bot)) as sk_clip:
        bd.RectangleRounded(18.0, 9.0, radius=4.2)
    clip_tab = bd.extrude(sk_clip.sketch, p.cap_top_eaves_h).translate((0.0, y_clip, 0.0))
    part = part.fuse(clip_tab)
    # Ø5.0 mm cable pocket + 4.0 mm lead-in slot on +X + flexing relief cutout creating a 2.0 mm spring jaw!
    clip_bore = bd.Cylinder(2.5, p.cap_top_eaves_h + 2.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((1.5, y_clip, z_bot - 1.0))
    clip_entry = bd.Box(9.0, 4.0, p.cap_top_eaves_h + 2.0, align=(bd.Align.MIN, bd.Align.CENTER, bd.Align.MIN)).translate((1.5, y_clip, z_bot - 1.0))
    # 2.0 x 3.8 mm zip-tie slot on -X side with 3.0 mm solid outer wall
    zip_slot = bd.Box(2.0, 3.8, p.cap_top_eaves_h + 2.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((-5.0, y_clip, z_bot - 1.0))
    part = part - clip_bore - clip_entry - zip_slot

    # -X Matching Contoured Rain-Hood Visor Brow (X = -63.5 mm, +4.5 mm past R = 59.0 eaves -> shelters SW1 boot)
    #    44.0 mm wide w/ R4.0 corners -> 36.0 x 10.0 mm flat vertical exterior face for debossed "OFF  UV  ALL" + tactile ribs!
    x_vis = p.cap_top_sw_visor_x  # 63.5
    vis_w = 44.0
    with bd.BuildSketch(bd.Plane.XY.offset(z_bot)) as sk_vis:
        bd.RectangleRounded(16.0, vis_w, radius=4.0)
    visor_base = bd.extrude(sk_vis.sketch, p.cap_top_eaves_h).translate((-(x_vis - 8.0), 0.0, 0.0))
    with bd.BuildSketch(bd.Plane.XY.offset(z_eaves_top)) as sk_vt0:
        bd.RectangleRounded(16.0, vis_w, radius=4.0)
    with bd.BuildSketch(bd.Plane.XY.offset(z_eaves_top + 6.5)) as sk_vt1:
        bd.RectangleRounded(6.0, vis_w - 13.0, radius=2.5)
    visor_taper = bd.loft([
        sk_vt0.sketch.translate((-(x_vis - 8.0), 0.0, 0.0)),
        sk_vt1.sketch.translate((-(x_vis - 14.5), 0.0, 0.0)),
    ])
    part = part.fuse(visor_base).fuse(visor_taper)

    # -X Debossed Switch Position Legend ("OFF   UV   ALL", reading left-to-right when facing -X: +Y=Left -> -Y=Right)
    #    0.6 mm deep bold sans-serif text (1.5 nozzle widths -> support-free FDM; easy to paint-fill for dark contrast)
    pl_txt = bd.Plane(origin=(-x_vis - 0.05, 0.0, z_bot + 6.6), x_dir=(0.0, -1.0, 0.0), z_dir=(-1.0, 0.0, 0.0))
    for x_loc, label in ((-11.8, "OFF"), (0.0, "UV"), (11.8, "ALL")):
        with bd.BuildSketch(pl_txt) as sk_lbl:
            with bd.Locations((x_loc, 0.0)):
                bd.Text(label, font_size=4.6, font="DejaVu Sans", font_style=bd.FontStyle.BOLD)
        part = part - bd.extrude(sk_lbl.sketch, -0.65)

    # -X Tactile 0 / 1 / 2 switch index ribs along lower visor lip directly beneath OFF / UV / ALL:
    #   +Y (Left) = OFF (0 ribs), Y = 0 (Center) = UV (1 rib), -Y (Right) = ALL (2 ribs at Y = -10.0 & -13.6 mm)
    for y_rib in (0.0, -10.0, -13.6):
        x_outer = -x_vis
        with bd.BuildSketch(bd.Plane.XZ) as sk_rib:
            with bd.BuildLine():
                bd.Polyline([
                    (x_outer + 2.0, z_bot),
                    (x_outer - 1.0, z_bot),
                    (x_outer - 1.0, z_bot + 2.2),
                    (x_outer + 2.0, z_bot + 5.2),  # 45-deg top bevel -> 0 overhang, clears debossed text above
                    (x_outer + 2.0, z_bot),
                ])
            bd.make_face()
        part = part.fuse(bd.extrude(sk_rib.sketch, 0.7, both=True).translate((0.0, y_rib, 0.0)))

    # Support-free 45-deg 1.4 x 1.4 mm underside drip kerf around eaves perimeter (R = 56.8 .. 58.2 mm)
    r_k0, r_k1 = 56.8, 58.2
    r_km = 0.5 * (r_k0 + r_k1)
    k_h = 0.7  # exact 45-deg V-groove (0 overhang!)
    # Revolve triangular V-groove in XZ plane around Z axis
    with bd.BuildSketch(bd.Plane.XZ) as sk_kerf:
        with bd.BuildLine():
            bd.Polyline([(r_k0, z_bot - 0.1), (r_k1, z_bot - 0.1), (r_km, z_bot + k_h), (r_k0, z_bot - 0.1)])
        bd.make_face()
    kerf_cut = bd.revolve(sk_kerf.sketch, axis=bd.Axis.Z, revolution_arc=360.0)
    part = part - kerf_cut

    # Straight Ø85.0 mm bore + 0.4 mm bed-side elephant-foot chamfer + <=44-deg Circle->Square internal ceiling loft
    bore_main = bd.Cylinder(r_bore, p.cap_top_ceil_cone_z - z_bot + 0.5, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, z_bot - 0.5))
    ef_chamfer = bd.Cone(r_bore + 0.6, r_bore, 0.6, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, z_bot - 0.05))
    z_ceil_top = p.cap_top_ceil_cone_z + (r_bore - 0.5 * p.core_pocket_w) + 1.0
    with bd.BuildSketch(bd.Plane.XY.offset(p.cap_top_ceil_cone_z)) as sk_cb:
        bd.Circle(r_bore)
    with bd.BuildSketch(bd.Plane.XY.offset(z_ceil_top)) as sk_ct:
        bd.Rectangle(p.core_pocket_w, p.core_pocket_w)
    ceil_loft = bd.loft([sk_cb.sketch, sk_ct.sketch])
    part = part - bore_main - ef_chamfer - ceil_loft

    # Translucent 0.60 mm internal dimple opposite D12 (red 20 V PD LED at Y = +16.0, Z = 190.9 mm -> angle 22.1 deg!)
    # Stops at R = r_bell - d12_skin_thick = 45.0 mm -> 0.60 mm unbroken white outer skin (zero waterproof breach!)
    ang_d12 = math.degrees(math.atan2(p.d12_local_bx, math.sqrt(r_bore ** 2 - p.d12_local_bx ** 2)))
    td_d12 = _teardrop_profile_wire(3.0, 42.0)
    r_d12_stop = r_bell - p.d12_skin_thick  # 45.0 mm
    d12_dimple = bd.extrude(td_d12, r_d12_stop - (r_bore - 2.0)).rotate(bd.Axis.X, 90.0).rotate(bd.Axis.Z, 90.0).translate((r_bore - 2.0, 0.0, p.z_d12)).rotate(bd.Axis.Z, ang_d12)
    part = part - d12_dimple

    # 4x blind M3x5.0 brass heat-set insert bores in eaves underside at R = 51.0 mm (45-deg cone tip -> 0 overhang)
    r_pil = p.m3_insert_pilot_dia / 2.0
    for deg in (45.0, 135.0, 225.0, 315.0):
        rad = math.radians(deg)
        ix, iy = p.top_base_ear_r * math.cos(rad), p.top_base_ear_r * math.sin(rad)
        ib_str = bd.Cylinder(r_pil, 5.8, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((ix, iy, z_bot - 0.2))
        ib_tip = bd.Cone(r_pil, 0.02, r_pil - 0.02, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((ix, iy, z_bot + 5.6))
        part = part - ib_str - ib_tip

    # 31.1 x 31.1 mm core aperture + backed 2.5 x 3.0 mm top neutral-sealant V-groove (ZERO side lock holes!)
    core_thru = bd.Box(p.core_pocket_w, p.core_pocket_w, (z_top - p.cap_top_ceil_cone_z) + 4.0,
                       align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, p.cap_top_ceil_cone_z - 1.0))
    part = part - core_thru
    w_g = p.core_pocket_w + 2.0 * p.cap_top_seal_groove  # 36.1 mm (inside 37.4 mm beveled top lip)
    with bd.BuildSketch(bd.Plane.XY.offset(z_top + 0.05)) as sk_top:
        bd.Rectangle(w_g, w_g)
    with bd.BuildSketch(bd.Plane.XY.offset(z_top - p.cap_top_seal_depth)) as sk_bot:
        bd.Rectangle(p.core_pocket_w, p.core_pocket_w)
    part = part - bd.loft([sk_bot.sketch, sk_top.sketch])

    return part


def build_cable_clamp_half(p: LepiLEDParams, side: float = 1.0) -> bd.Part:
    """
    MECH-CABLE-CLAMP — Fixed Compressing +Y Split Cable Clamp (one half; exported as pre-mirrored L+R pair):
      - 1.2 mm axial flange standoff (Y = 48.2 mm vs +Y boss Y = 47.0 mm) so 45-deg wedges actually drive radial squeeze
      - 5.5 x 3.4 mm horizontally slotted pan-head M3x14 bolt slots (no CSK kinematic locking!)
      - Full 10.5 mm-long Ø7.4 mm cylindrical grommet chamber compressing 10.0 mm slit Ø8 x Ø4 silicone sleeve
      - Outer face sits at Y = 54.2 mm (4.8 mm inside R = 59.0 mm eaves); top Z = 166.5 mm (4.5 mm below eaves)
    """
    r_port = p.top_base_port_od / 2.0  # 47.0
    y_face = r_port + p.clamp_standoff_y  # 48.2 (1.2 mm real axial travel!)
    z_c = p.clamp_z                    # 156.5
    z_pbot = 148.0 + 0.35              # 148.35
    z_papex = 165.0 - 0.50             # 164.50

    # Outer flange (35.0(X) x 20.0(Z) x 6.0(Y), Z = 146.5 .. 166.5 mm -> 4.5 mm below eaves!)
    with bd.BuildSketch(bd.Plane(origin=(0.0, y_face, z_c), x_dir=(-1.0, 0.0, 0.0), z_dir=(0.0, 1.0, 0.0))) as sk_fl:
        bd.RectangleRounded(35.0, 20.0, radius=4.0)
    flange = bd.extrude(sk_fl.sketch, p.clamp_flange_t)  # Y = 48.2 .. 54.2

    # 45-deg compressing wedges (Y = 45.2 .. 48.2 mm; contacts port wedge at Y=47.0 with 0.20 mm start -> 1.0 mm drive!)
    hw_in = 0.5 * p.clamp_port_w - 0.20  # 7.80 mm at Y = 45.2
    hw_out = hw_in + 3.0                 # 10.80 mm at Y = 48.2 (at Y=47.0 -> 9.60 vs port 10.0, closes cleanly under bolt!)
    pl_w0 = bd.Plane(origin=(0.0, 45.2, 0.0), x_dir=(-1.0, 0.0, 0.0), z_dir=(0.0, 1.0, 0.0))
    pl_w1 = bd.Plane(origin=(0.0, y_face, 0.0), x_dir=(-1.0, 0.0, 0.0), z_dir=(0.0, 1.0, 0.0))
    sk_w0 = _pentagon_gable_sketch(pl_w0, hw_in, z_pbot, z_papex)
    sk_w1 = _pentagon_gable_sketch(pl_w1, hw_out, z_pbot, z_papex)
    wedge = bd.loft([sk_w0, sk_w1])

    # Inner straight sleeve barrel (Y = 41.5 .. 45.2 mm) enclosing full 10.5 mm grommet chamber!
    pl_key = bd.Plane(origin=(0.0, 41.5, 0.0), x_dir=(-1.0, 0.0, 0.0), z_dir=(0.0, 1.0, 0.0))
    sk_key = _pentagon_gable_sketch(pl_key, hw_in, z_pbot, z_papex)
    key = bd.extrude(sk_key, 45.2 - 41.5)
    full = flange.fuse(wedge).fuse(key)

    # Central horizontal Ø4.6 mm cable bore + FULL 10.5 mm-long Ø7.4 mm cylindrical grommet chamber (Y = 42.5 .. 53.0 mm!)
    r_cab = p.clamp_cable_dia / 2.0 + 0.05  # 2.30
    r_grom = p.clamp_grommet_id / 2.0       # 3.70 (compresses Ø8.0 mm sleeve onto Ø4.0-4.5 mm cable!)
    dr = r_grom - r_cab                     # 1.40
    # Build along local +Z (z=0 corresponds to global y_face=48.2), then rotate -90 around X so +Z -> +Y!
    c_cable = bd.Cylinder(r_cab, 20.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER))
    # Grommet cylinder spans local z ∈ [-5.7, +4.8] (10.5 mm!) -> global Y ∈ [42.5, 53.0], leaving 1.2 mm exit retaining lip!
    z_g_start = -5.7
    c_g2 = bd.Cylinder(r_grom, p.clamp_grommet_len, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, z_g_start))
    # 45-deg chamfered transitions into cable bore (zero overhang when printed face-down on Y = 54.2!)
    c_g_in = bd.Cone(r_cab, r_grom, dr, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)).translate((0, 0, z_g_start))
    c_g_out = bd.Cone(r_grom, r_cab, dr, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, z_g_start + p.clamp_grommet_len))
    bore_assy = c_cable.fuse(c_g2).fuse(c_g_in).fuse(c_g_out).rotate(bd.Axis.X, -90.0).translate((0.0, y_face, z_c))
    full = full - bore_assy

    # 2x horizontally X-slotted 5.5 x 3.4 mm pan-head M3 clearance slots at X = ±13.0 mm (allows ±X wedge travel!)
    for sx in (-1.0, 1.0):
        with bd.BuildSketch(bd.Plane(origin=(sx * p.clamp_bolt_dx, y_face - 1.0, z_c), x_dir=(-1.0, 0.0, 0.0), z_dir=(0.0, 1.0, 0.0))) as sk_sl:
            bd.SlotOverall(5.5, p.m3_clearance_dia)
        full = full - bd.extrude(sk_sl.sketch, p.clamp_flange_t + 3.0)

    # Split halves with 0.25 mm nominal gap (closes smoothly as wedges engage!)
    gap = 0.25
    if side > 0:
        half_mask = bd.Box(44.0, 44.0, 44.0, align=(bd.Align.MIN, bd.Align.CENTER, bd.Align.CENTER)).translate((gap, y_face, z_c))
    else:
        half_mask = bd.Box(44.0, 44.0, 44.0, align=(bd.Align.MAX, bd.Align.CENTER, bd.Align.CENTER)).translate((-gap, y_face, z_c))
    return full & half_mask


def build_plug_top(p: LepiLEDParams) -> bd.Part:
    """
    MECH-PLUG-TOP — Open-Chimney Ventilated Rain Finial (Z = 285.0 .. 324.0 mm, prints inverted):
      - 4 corner legs slipping 21 mm inside 26 x 26 mm Al bore, cross-pinned by top M4 x 50 mm stainless hanging bolt
      - Perimeter mesh-clamping rim resting on top end of Al core at Z = 306.0 mm (holds 28 x 28 mm stainless mesh)
      - 4 generous 14.4 x 9.0 mm exhaust windows (5.18 cm^2 open area) under overhanging 38 x 38 mm 45-deg rain hood
    """
    z_top_core = p.z_core_top            # 306.0
    z_legs_bot = z_top_core - p.plug_top_insert_h  # 285.0
    z_vent_top = z_top_core + p.plug_top_vent_h    # 315.0
    z_end = p.z_plug_top_end             # 324.0
    w_leg = p.plug_top_leg_w             # 25.4
    post_w = 5.5                         # 4 corner posts -> 14.4 mm clear exhaust opening on every side!

    # 1. Overhanging 38 x 38 mm rain hood (Z = 315.0 .. 324.0 mm: 3.0 mm skirt + 6.0 mm 45-deg pitched roof)
    skirt_h = 3.0
    bevel_h = p.plug_top_hood_h - skirt_h  # 6.0 mm -> 38 -> 26 mm top flat
    with bd.BuildSketch(bd.Plane.XY.offset(z_vent_top)) as sk_hs:
        bd.RectangleRounded(p.plug_top_hood_w, p.plug_top_hood_w, radius=2.0)
    hood_skirt = bd.extrude(sk_hs.sketch, skirt_h)
    with bd.BuildSketch(bd.Plane.XY.offset(z_vent_top + skirt_h)) as sk_hb:
        bd.RectangleRounded(p.plug_top_hood_w, p.plug_top_hood_w, radius=2.0)
    with bd.BuildSketch(bd.Plane.XY.offset(z_end)) as sk_ht:
        bd.RectangleRounded(p.plug_top_hood_w - 2.0 * bevel_h, p.plug_top_hood_w - 2.0 * bevel_h, radius=1.5)
    hood_roof = bd.loft([sk_hb.sketch, sk_ht.sketch])
    part = hood_skirt.fuse(hood_roof)

    # 2. 4 continuous corner posts running from Z = 285.0 .. 315.5 mm (0 overhang when printed inverted!)
    off = 0.5 * (w_leg - post_w)  # 9.95 mm
    for sx in (-1.0, 1.0):
        for sy in (-1.0, 1.0):
            post = bd.Box(post_w, post_w, (z_vent_top + 0.5) - z_legs_bot,
                          align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((sx * off, sy * off, z_legs_bot))
            part = part.fuse(post)

    # 3. ±X internal pin webs (Z = 285.0 .. 296.0 mm) with 45-deg upper bevel (Z = 296.0 .. 303.2 mm -> 0 overhang inverted!)
    for sx in (-1.0, 1.0):
        xc = sx * (0.5 * w_leg - 1.4)
        pl_web = bd.Plane(origin=(xc - 1.4, 0.0, 0.0), x_dir=(0.0, 1.0, 0.0), z_dir=(1.0, 0.0, 0.0))
        # Pentagon in YZ plane: full width at Z = 285..296, tapering at 45-deg outward to corner posts from Z = 296..303.5!
        half_span = 0.5 * w_leg - 0.5
        inner_y = off - 0.5 * post_w  # 7.2 mm (inner edge of corner posts)
        with bd.BuildSketch(pl_web) as sk_w:
            with bd.BuildLine():
                bd.Polyline([
                    (-half_span, z_legs_bot),
                    (half_span, z_legs_bot),
                    (half_span, 303.2),
                    (inner_y, 303.2),
                    (0.0, 296.0),
                    (-inner_y, 303.2),
                    (-half_span, 303.2),
                    (-half_span, z_legs_bot),
                ])
            bd.make_face()
        part = part.fuse(bd.extrude(sk_w.sketch, 2.8))

    # 4. Top-of-core mesh-clamping step on 4 corners (Z = 306.0 .. 308.4 mm) -> traps 28 x 28 mm mesh with 0 overhang!
    for sx in (-1.0, 1.0):
        for sy in (-1.0, 1.0):
            with bd.BuildSketch(bd.Plane.XY.offset(z_top_core)) as sk_m0:
                bd.Rectangle(post_w + 2.4, post_w + 2.4)
            with bd.BuildSketch(bd.Plane.XY.offset(z_top_core + 2.4)) as sk_m1:
                bd.Rectangle(post_w, post_w)
            tab = bd.loft([
                sk_m0.sketch.translate((sx * (off + 1.2), sy * (off + 1.2), 0.0)),
                sk_m1.sketch.translate((sx * off, sy * off, 0.0)),
            ])
            part = part.fuse(tab)

    # Cut Ø4.6 mm M4 cross-bolt clearance bore on ±X at Z = 290.0 mm (teardrop apex pointing -Z for inverted printing!)
    td_m4_inv = _teardrop_profile_wire(p.core_bolt_hole_dia / 2.0 + 0.1, 42.0)
    m4_cut = bd.extrude(td_m4_inv, 36.0).rotate(bd.Axis.X, -90.0).rotate(bd.Axis.Z, -90.0).translate((-18.0, 0.0, p.z_hang_hole))
    part = part - m4_cut

    return part


def build_cord_spool(p: LepiLEDParams) -> bd.Part:
    """
    Symmetric 6.0 mm flanged M4 bail spool (2x printed flat alongside MECH-PLUG-TOP):
      - Ø4.4 mm slip bore over top M4 x 50 mm stainless cross-bolt outside ±X walls of 30 mm Al core
      - Ø7.2 mm smooth barrel (1.4 mm wall) spacing bent coat-hanger wire bail clear of anodized Al tube & 38 mm rain hood
      - Exact stack on M4 x 50 bolt: 30.0 Al + 2x6.0 spools + 2x0.8 M4 washers + 5.0 nyloc = 48.6 mm (0.000 mm^2 overhang)
    """
    with bd.BuildSketch(bd.Plane.XZ) as sk_sp:
        with bd.BuildLine():
            bd.Polyline([
                (2.20, 0.0),
                (5.10, 0.0),
                (5.10, 0.6),
                (3.60, 2.2),   # 43.15-deg taper -> 0.000 mm^2 >46 deg overhang upright or inverted
                (3.60, 3.8),   # 1.6 mm barrel groove floor for Ø2.0-2.5 mm wire bail eye (or 3 mm cord)
                (5.10, 5.4),   # 43.15-deg flare
                (5.10, 6.0),
                (2.20, 6.0),
                (2.20, 0.0),
            ])
        bd.make_face()
    return bd.revolve(sk_sp.sketch, axis=bd.Axis.Z, revolution_arc=360.0)


def build_drill_jig(p: LepiLEDParams) -> bd.Part:
    """
    MECH-DRILL-JIG — Compact 35 mm Dual-Datum Snap-On Center-Punch End-Cap Guide:
      - Tight 30.3 mm U-channel fits onto either end of 30 x 30 mm Al tube
      - Two Ø2.0 mm center-punch guide cones at 6.5 mm (bottom M4 bolt) & 16.0 mm (top M4 hanging bolt) from end stop
    """
    wall = 3.2
    inner_w = p.core_w_nom + 0.30  # Tight 30.3 mm fit
    outer_w = inner_w + 2.0 * wall
    jig_len = 32.0
    leg_h = 14.0

    base = bd.Box(wall, outer_w, jig_len, align=(bd.Align.MIN, bd.Align.CENTER, bd.Align.MIN))
    leg_pos = bd.Box(leg_h, wall, jig_len, align=(bd.Align.MIN, bd.Align.MAX, bd.Align.MIN)).translate((0, outer_w / 2.0, 0))
    leg_neg = bd.Box(leg_h, wall, jig_len, align=(bd.Align.MIN, bd.Align.MIN, bd.Align.MIN)).translate((0, -outer_w / 2.0, 0))
    end_stop = bd.Box(10.0, outer_w, wall, align=(bd.Align.MIN, bd.Align.CENTER, bd.Align.MAX))
    jig = base.fuse(leg_pos).fuse(leg_neg).fuse(end_stop)

    dg = p.drill_guide_from_core_bot_mm
    for z_rel in (dg["bottom_m4_bolt_from_bot_mm"], dg["top_m4_hang_bolt_from_top_mm"]):
        punch_hole = bd.Cylinder(1.1, wall + 2.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER)).rotate(bd.Axis.Y, 90.0).translate((wall / 2.0, 0.0, z_rel))
        punch_cone = bd.Cone(2.6, 1.1, 1.5, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).rotate(bd.Axis.Y, 90.0).translate((-0.05, 0.0, z_rel))
        jig = jig - punch_hole - punch_cone

    jig = jig.rotate(bd.Axis.Y, -90.0)
    bb = jig.bounding_box()
    return jig.translate((0.0, 0.0, -bb.min.Z))


def build_usbc_cable(p: LepiLEDParams) -> bd.Part:
    """
    Model BOTH internal curved Ø4.4 mm USB-C cable (from +X 90-deg plug -> +Y cable clamp)
    AND external gravity drip loop -> flexible +Y eaves C-clip -> upward routing!
    """
    r_cab = 2.2
    z_c = p.clamp_z  # 156.5

    # 1. Internal horizontal S-curve in Z = clamp_z plane from plug strain-relief tip (27.48, 13.6) -> clamp (0.0, 42.5)
    x0, y0 = p.x_j1_center, 0.5 * p.usbc_plug_90_w_y + p.usbc_strain_relief_h + 0.1  # (27.48, 13.7)
    x1, y1 = 0.0, 42.5
    dx, dy = x0 - x1, y1 - y0
    r_int = (dx ** 2 + dy ** 2) / (4.0 * dx)
    th_i = math.acos(1.0 - (0.5 * dx) / r_int)
    pi1_mid = (x0 - r_int * (1.0 - math.cos(0.5 * th_i)), y0 + r_int * math.sin(0.5 * th_i))
    pi_inf = (0.5 * (x0 + x1), 0.5 * (y0 + y1))
    pi2_mid = (x1 + r_int * (1.0 - math.cos(0.5 * th_i)), y1 - r_int * math.sin(0.5 * th_i))

    with bd.BuildLine(bd.Plane.XY.offset(z_c)) as l_int:
        bd.ThreePointArc((x0, y0), pi1_mid, pi_inf)
        bd.ThreePointArc(pi_inf, pi2_mid, (x1, y1))
    pl_int = bd.Plane(origin=(x0, y0, z_c), x_dir=(1.0, 0.0, 0.0), z_dir=(0.0, 1.0, 0.0))
    with bd.BuildSketch(pl_int) as sk_int:
        bd.Circle(r_cab)
    cab_int = bd.sweep(sk_int.sketch, path=l_int.wire())

    # 2. External drip loop & upward cable in YZ plane (starting at clamp outer face Y = 54.4)
    y_ex0 = 0.5 * p.top_base_port_od + p.clamp_standoff_y + p.clamp_flange_t + 0.2  # 54.4
    r1 = 6.0
    p1 = (y_ex0 + r1, z_c - r1)
    p1_mid = (y_ex0 + r1 * math.sqrt(0.5), z_c - r1 * (1.0 - math.sqrt(0.5)))

    z_loop = z_c - 14.0  # 142.5 (lowest centerline at 136.5 -> 20 mm drip loop below 156.5 clamp!)
    p2 = (y_ex0 + r1, z_loop)
    r2 = 6.0
    p2_mid = (y_ex0 + r1 + r2, z_loop - r2)
    p3 = (y_ex0 + r1 + 2.0 * r2, z_loop)  # (72.4, 142.5)

    # Smooth S-curve up into +Y eaves C-clip (X = 1.5, Y = 60.5, Z = 171 .. 181 mm) -> build in YZ at X = 0 then route cleanly
    y_clip = 60.5
    z_clip_bot = p.z_cap_top_bot        # 171.0
    z_clip_top = p.z_cap_top_eaves_top  # 181.0
    dy_s = p3[0] - y_clip
    dz_s = z_clip_bot - z_loop
    r_s = (dy_s ** 2 + dz_s ** 2) / (4.0 * dy_s)
    th_s = math.acos(1.0 - (0.5 * dy_s) / r_s)
    p3_mid = (p3[0] - r_s * (1.0 - math.cos(0.5 * th_s)), z_loop + r_s * math.sin(0.5 * th_s))
    p_inf = (0.5 * (p3[0] + y_clip), 0.5 * (z_loop + z_clip_bot))
    p4_mid = (y_clip + r_s * (1.0 - math.cos(0.5 * th_s)), z_clip_bot - r_s * math.sin(0.5 * th_s))
    p4 = (y_clip, z_clip_bot)
    p5 = (y_clip, z_clip_top)

    y_top, z_top = 28.0, 345.0
    dy_u = y_clip - y_top
    dz_u = z_top - z_clip_top
    r_u = (dy_u ** 2 + dz_u ** 2) / (4.0 * dy_u)
    th_u = math.acos(1.0 - (0.5 * dy_u) / r_u)
    p5_mid = (y_clip - r_u * (1.0 - math.cos(0.5 * th_u)), z_clip_top + r_u * math.sin(0.5 * th_u))
    p_uinf = (0.5 * (y_clip + y_top), 0.5 * (z_clip_top + z_top))
    p6_mid = (y_top + r_u * (1.0 - math.cos(0.5 * th_u)), z_top - r_u * math.sin(0.5 * th_u))
    p6 = (y_top, z_top)

    with bd.BuildLine(bd.Plane.XY) as l_ext:
        bd.ThreePointArc((y_ex0, z_c), p1_mid, p1)
        bd.Line(p1, p2)
        bd.ThreePointArc(p2, p2_mid, p3)
        bd.ThreePointArc(p3, p3_mid, p_inf)
        bd.ThreePointArc(p_inf, p4_mid, p4)
        bd.Line(p4, p5)
        bd.ThreePointArc(p5, p5_mid, p_uinf)
        bd.ThreePointArc(p_uinf, p6_mid, p6)
    prof_pl = bd.Plane(origin=(y_ex0, z_c, 0.0), x_dir=(0.0, 1.0, 0.0), z_dir=(1.0, 0.0, 0.0))
    with bd.BuildSketch(prof_pl) as sk_ext:
        bd.Circle(r_cab)
    cab_ext = bd.sweep(sk_ext.sketch, path=l_ext.wire()).rotate(bd.Axis.X, 90.0).rotate(bd.Axis.Z, 90.0).translate((1.5, 0.0, 0.0))

    # Straight section inside clamp bore (Y = 42.5 .. 54.4)
    cab_mid = bd.Cylinder(r_cab, y_ex0 - 42.5, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).rotate(bd.Axis.X, -90.0).translate((0.0, 42.5, z_c))
    return bd.Compound([cab_int, cab_mid, cab_ext])


def _load_populated_smd_solids(p: LepiLEDParams) -> list[bd.Shape]:
    """
    Read ALL 48 populated SMD centroids & KiCad rotations from committed driver_pcb.kicad_pcb,
    mapped into the +X vertical top-bay pose:
      Global X = p.pcb_x_fcu + bz  (F.Cu facing outward +X)
      Global Y = bx                (J2 at Y = -5.2, J3 at Y = +5.2, D12 at Y = +16.0)
      Global Z = p.pcb_z_center + by
    """
    pcb_path = Path(__file__).resolve().parents[2] / "pcb_design" / "driver_pcb" / "driver_pcb.kicad_pcb"
    txt = pcb_path.read_text(encoding="utf-8")
    exclude = {"H1", "H2", "H3", "H4", "TP1", "TP2", "TP3", "TP4", "J1", "J2", "J3", "J4", "D13", "D14"}
    solids: list[bd.Shape] = []
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
        box = bd.Box(hz, lx, wy, align=(bd.Align.MIN, bd.Align.CENTER, bd.Align.CENTER)).translate((p.pcb_x_fcu, bx, p.pcb_z_center + by))
        solids.append(box)
    assert len(solids) == 48, f"Expected 48 populated SMDs from driver_pcb.kicad_pcb, got {len(solids)}"
    return solids


def build_assembly_parts(p: LepiLEDParams, core_w_override: float | None = None,
                         glass_id_override: float | None = None, glass_od_override: float | None = None,
                         glass_length_override: float | None = None) -> dict[str, bd.Shape]:
    """Build complete physical assembly including 10 brass inserts, 10 M3 screws, 2 M4x50 SS bolts, 48 SMDs & USB-C cable."""
    core_w = core_w_override or p.core_w_nom
    g_id = glass_id_override or p.glass_id_nom
    g_od = glass_od_override or p.glass_od_nom
    g_len = glass_length_override or p.glass_length

    cap_bot = build_cap_bot(p)
    top_base = build_top_base(p)
    cap_top = build_cap_top(p)
    plug_top_finial = build_plug_top(p)
    spool_unit = build_cord_spool(p)
    x_sp_in = 0.5 * core_w + 0.05
    spool_pos = spool_unit.rotate(bd.Axis.Y, 90.0).translate((x_sp_in, 0.0, p.z_hang_hole))
    spool_neg = spool_unit.rotate(bd.Axis.Y, -90.0).translate((-x_sp_in, 0.0, p.z_hang_hole))
    plug_top = bd.Compound([plug_top_finial, spool_pos, spool_neg])
    clamp_pos = build_cable_clamp_half(p, side=+1.0)
    clamp_neg = build_cable_clamp_half(p, side=-1.0)
    cable_clamp = bd.Compound([clamp_pos, clamp_neg])
    usbc_cable = build_usbc_cable(p)

    # Committed Driver PCB (36.0 x 46.0 x 1.6 mm) stood vertically on +X face (B.Cu at X = 24.0, F.Cu at X = 25.6)
    pcb_board = bd.Box(p.pcb_thick, p.pcb_w, p.pcb_l, align=(bd.Align.MIN, bd.Align.CENTER, bd.Align.CENTER))
    pcb_board = bd.fillet(pcb_board.edges().filter_by(bd.Axis.X), p.pcb_corner_r).translate((p.pcb_x_bcu, 0.0, p.pcb_z_center))
    for sy in (-1.0, 1.0):
        for sz in (-1.0, 1.0):
            npth = bd.Cylinder(p.pcb_hole_drill / 2.0, p.pcb_thick + 0.6, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER)).rotate(bd.Axis.Y, 90.0).translate(
                (p.pcb_x_bcu + 0.5 * p.pcb_thick, sy * p.pcb_hole_y, p.pcb_z_center + sz * p.pcb_hole_z)
            )
            pcb_board = pcb_board - npth

    pcb_parts: list[bd.Shape] = [pcb_board, *_load_populated_smd_solids(p)]
    j2_hdr = bd.Box(p.pcb_jst_mated_h, 7.4, 5.8, align=(bd.Align.MIN, bd.Align.CENTER, bd.Align.CENTER)).translate((p.pcb_x_fcu, -5.2, p.pcb_z_center + 19.2))
    j3_hdr = bd.Box(p.pcb_jst_mated_h, 7.4, 5.8, align=(bd.Align.MIN, bd.Align.CENTER, bd.Align.CENTER)).translate((p.pcb_x_fcu, 5.2, p.pcb_z_center + 19.2))
    j4_hdr = bd.Box(p.pcb_jst_mated_h, 9.9, 5.8, align=(bd.Align.MIN, bd.Align.CENTER, bd.Align.CENTER)).translate((p.pcb_x_fcu, -1.4, p.pcb_z_center - 2.5))
    j1_outer = bd.Box(3.46, 8.94, 9.17, align=(bd.Align.MIN, bd.Align.CENTER, bd.Align.MIN)).translate((p.pcb_x_fcu, 0.0, p.z_j1_mouth))
    j1_cav = bd.Box(2.56, 8.34, p.usbc_mating_depth_mm + 0.05, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((p.x_j1_center, 0.0, p.z_j1_mouth - 0.05))
    j1_usbc = j1_outer - j1_cav
    j23_pins = bd.Box(p.pcb_jst_pin_protrude, 15.0, 2.0, align=(bd.Align.MAX, bd.Align.CENTER, bd.Align.CENTER)).translate((p.pcb_x_bcu, 0.0, p.pcb_z_center + 19.2))
    j4_pins = bd.Box(p.pcb_jst_pin_protrude, 7.5, 2.0, align=(bd.Align.MAX, bd.Align.CENTER, bd.Align.CENTER)).translate((p.pcb_x_bcu, -1.4, p.pcb_z_center - 2.5))
    j1_pins = bd.Box(p.pcb_jst_pin_protrude, 9.6, 5.7, align=(bd.Align.MAX, bd.Align.CENTER, bd.Align.CENTER)).translate((p.pcb_x_bcu, 0.0, p.pcb_z_center - 19.54))
    pcb_parts.extend([j2_hdr, j3_hdr, j4_hdr, j1_usbc, j23_pins, j4_pins, j1_pins])
    pcb_assy = bd.Compound(pcb_parts)

    # Central open-chimney 30 x 30 x 2.0 mm bare mill Al 6063-T6 core (only 4 plain Ø4.5 mm holes, zero tapping!)
    core_out = bd.Box(core_w, core_w, p.core_length, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    core_in = bd.Box(core_w - 2.0 * p.core_wall, core_w - 2.0 * p.core_wall, p.core_length + 2.0,
                     align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, -1.0))
    hs_core = (core_out - core_in).translate((0, 0, p.z_core_bot))
    bot_m4_bore = bd.Cylinder(p.core_bolt_hole_dia / 2.0, core_w + 2.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER)).rotate(bd.Axis.Y, 90.0).translate((0.0, 0.0, p.z_bot_bolt))
    top_m4_bore = bd.Cylinder(p.core_bolt_hole_dia / 2.0, core_w + 2.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER)).rotate(bd.Axis.Y, 90.0).translate((0.0, 0.0, p.z_hang_hole))
    hs_core = hs_core - bot_m4_bore - top_m4_bore

    # 6x identical M3 x 5.0 x 4.2 mm brass heat-set inserts (4x eaves + 2x blind +Y clamp; PCB uses 4x captive M3 hex nuts!)
    inserts_list: list[bd.Shape] = []
    # a) 4x eaves inserts in MECH-CAP-TOP at R = 51.0 mm
    for deg in (45.0, 135.0, 225.0, 315.0):
        rad = math.radians(deg)
        ix, iy = p.top_base_ear_r * math.cos(rad), p.top_base_ear_r * math.sin(rad)
        ins = (bd.Cylinder(1.98, 5.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
               - bd.Cylinder(1.52, 5.2, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, -0.1)))
        inserts_list.append(ins.translate((ix, iy, p.z_cap_top_bot + 0.05)))
    # b) 2x blind +Y cable-clamp inserts in MECH-TOP-BASE
    r_port = p.top_base_port_od / 2.0
    for sx in (-1.0, 1.0):
        ins = (bd.Cylinder(1.98, 5.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX))
               - bd.Cylinder(1.52, 5.2, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)).translate((0, 0, 0.1)))
        inserts_list.append(ins.rotate(bd.Axis.X, -90.0).translate((sx * p.clamp_bolt_dx, r_port - 0.05, p.clamp_z)))
    inserts_brass = bd.Compound(inserts_list)

    # All modeled fasteners: 10x M3 (4 eaves CSK + 2 clamp pan + 4 PCB pan + 4 captive M3 hex nuts) + 2x M4 x 50 mm SS bolts!
    fasteners_list: list[bd.Shape] = []
    # 1. 4x M3x12 CSK diagonal eaves bolts
    z_ear_bot = p.z_top_base_deck_top - p.top_base_ear_h
    for deg in (45.0, 135.0, 225.0, 315.0):
        rad = math.radians(deg)
        ex, ey = p.top_base_ear_r * math.cos(rad), p.top_base_ear_r * math.sin(rad)
        lb_head = bd.Cone(2.95, 1.48, 1.47, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((ex, ey, z_ear_bot + 0.05))
        lb_shank = bd.Cylinder(1.48, 10.5, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((ex, ey, z_ear_bot + 1.52))
        fasteners_list.append(lb_head.fuse(lb_shank))
    # 2. 2x M3x14 pan-head + flat washer +Y cable clamp bolts
    y_cl_out = r_port + p.clamp_standoff_y + p.clamp_flange_t  # 54.2
    for sx in (-1.0, 1.0):
        cx = sx * p.clamp_bolt_dx
        ch = bd.Cylinder(3.4, 2.2, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
        cs = bd.Cylinder(1.48, 12.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX))
        cbolt = ch.fuse(cs).rotate(bd.Axis.X, -90.0).translate((cx, y_cl_out + 0.05, p.clamp_z))
        fasteners_list.append(cbolt)
    # 3. 4x M3x8 pan-head + steel + 2x Ø7.0x0.8 nylon washers + captive DIN 934 M3 hex nuts securing vertical driver_pcb on +X
    x_nut_c = p.core_pocket_w / 2.0 + 1.0 + 1.30  # 17.85
    for sy in (-1.0, 1.0):
        for sz in (-1.0, 1.0):
            hy = sy * p.pcb_hole_y
            hz = p.pcb_z_center + sz * p.pcb_hole_z
            # Washer stack (2x0.8 nylon + 0.5 steel = 2.1 mm) + pan head (2.0 mm); shank extends 4.3 mm behind B.Cu (stops X=16.2!)
            pw = bd.Cylinder(3.50, 3.6, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
            ps = bd.Cylinder(1.48, 5.85, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX))
            pbolt = pw.fuse(ps).rotate(bd.Axis.Y, 90.0).translate((p.pcb_x_fcu + 0.05, hy, hz))
            # Captive DIN 934 M3 hex nut (5.50 mm AF vertical along Z, 6.35 mm AC along Y, 2.40 mm thick at X=17.85)
            with bd.BuildSketch(bd.Plane.YZ.offset(x_nut_c - 1.20)) as sk_hn:
                bd.RegularPolygon(radius=p.pcb_nut_af / (2.0 * math.cos(math.radians(30.0))), side_count=6, rotation=0.0)
            hex_nut = bd.extrude(sk_hn.sketch, p.pcb_nut_thick).translate((0.0, hy, hz))
            fasteners_list.append(pbolt.fuse(hex_nut))
    # 4. Bottom M4 x 50 mm A2 stainless cross-bolt + nyloc nut at Z = 12.5 mm inside MECH-CAP-BOT spotfaces (|X| = 21.0)
    b_sh = bd.Cylinder(1.98, 48.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER)).rotate(bd.Axis.Y, 90.0).translate((0.0, 0.0, p.z_bot_bolt))
    b_hd = bd.Cylinder(3.4, 3.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).rotate(bd.Axis.Y, 90.0).translate((21.05, 0.0, p.z_bot_bolt))
    b_nt = bd.Cylinder(3.4, 3.8, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)).rotate(bd.Axis.Y, 90.0).translate((-21.05, 0.0, p.z_bot_bolt))
    fasteners_list.append(b_sh.fuse(b_hd).fuse(b_nt))
    # 5. Top M4 x 50 mm A2 stainless hanging cross-bolt + 2x M4 DIN 125 washers + nyloc nut clamping 2x 6.0 mm cord spools
    x_w_in = x_sp_in + 6.05  # 21.10 mm nom / 21.30 mm WC (0.05 mm clear of spool outer face)
    t_sh = bd.Cylinder(1.98, 50.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)).rotate(bd.Axis.Y, 90.0).translate((x_w_in + 0.80, 0.0, p.z_hang_hole))
    t_w_pos = bd.Cylinder(4.50, 0.80, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).rotate(bd.Axis.Y, 90.0).translate((x_w_in, 0.0, p.z_hang_hole))
    t_hd = bd.Cylinder(3.60, 3.00, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).rotate(bd.Axis.Y, 90.0).translate((x_w_in + 0.80, 0.0, p.z_hang_hole))
    t_w_neg = bd.Cylinder(4.50, 0.80, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)).rotate(bd.Axis.Y, 90.0).translate((-x_w_in, 0.0, p.z_hang_hole))
    t_nt = bd.Cylinder(3.80, 5.00, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)).rotate(bd.Axis.Y, 90.0).translate((-(x_w_in + 0.80), 0.0, p.z_hang_hole))
    fasteners_list.append(t_sh.fuse(t_w_pos).fuse(t_hd).fuse(t_w_neg).fuse(t_nt))
    fasteners_m3 = bd.Compound(fasteners_list)

    # Clear Extruded XT PMMA Shroud (Ø60 x 54 x 3.0 x 115 mm)
    z_g_start = p.z_glass_bot - 0.5 * (g_len - p.glass_length)
    g_outer = bd.Cylinder(g_od / 2.0, g_len, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    g_inner = bd.Cylinder(g_id / 2.0, g_len + 2.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, -1.0))
    glass_tube = (g_outer - g_inner).translate((0, 0, z_g_start))

    # 8x Convoy 20 mm Cu DTP LED stars (flattened Compound so .volume > 0; bonded w/ thermal epoxy -> zero star screws!)
    star_items: list[bd.Shape] = []
    for angle in (0.0, 90.0, 180.0, 270.0):
        x0 = core_w / 2.0 + p.star_tim_thick
        for z_star, led_h in ((p.z_led_uv, p.led_uv_max_h), (p.z_led_vis, p.led_vis_max_h)):
            star_disc = bd.Cylinder(p.star_dia / 2.0, p.star_thick, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).rotate(bd.Axis.Y, 90.0).translate((x0, 0.0, z_star)).rotate(bd.Axis.Z, angle)
            led_pkg = bd.Box(led_h, 3.45, 3.45, align=(bd.Align.MIN, bd.Align.CENTER, bd.Align.CENTER)).translate((x0 + p.star_thick, 0.0, z_star)).rotate(bd.Axis.Z, angle)
            star_items.extend([star_disc, led_pkg])
    dtp_stars = bd.Compound(star_items)

    # Side-mounted SW1 + silicone boot recessed 5.5 mm in -X draining cove (sheltered inside -X rain visor)
    x_sw0 = -(r_port - p.sw1_recess_x)  # -41.5
    sw_body = bd.Box(p.sw1_body_d_x, p.sw1_body_w_y, p.sw1_body_h_z,
                     align=(bd.Align.MIN, bd.Align.CENTER, bd.Align.CENTER)).translate((x_sw0 + p.sw1_wall_thick + 0.05, 0.0, p.sw1_z))
    sw_lugs = bd.Box(p.sw1_lugs_d_x, 10.0, 8.5,
                     align=(bd.Align.MIN, bd.Align.CENTER, bd.Align.CENTER)).translate((x_sw0 + p.sw1_wall_thick + 0.05 + p.sw1_body_d_x, 0.0, p.sw1_z))
    sw_bush = bd.Cylinder(p.sw1_hole_dia / 2.0 - 0.12, p.sw1_wall_thick + 0.1,
                          align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).rotate(bd.Axis.Y, 90.0).translate((x_sw0, 0.0, p.sw1_z))
    sw_boot = bd.Cylinder(p.sw1_boot_od / 2.0, p.sw1_boot_protrude_x,
                          align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)).rotate(bd.Axis.Y, 90.0).translate((x_sw0 - 0.05, 0.0, p.sw1_z))
    sw1_assy = bd.Compound([sw_body, sw_lugs, sw_bush, sw_boot])

    # Realistic 18.0 mm commercial left/right 90-deg USB-C plug + 2.10 mm exposed tongue + 7.0 mm strain relief pointing +Y!
    z_plug_tip = p.z_j1_mouth + p.usbc_mating_depth_mm
    plug_barrel = bd.Box(2.5, 8.3, p.usbc_mating_depth_mm + p.usbc_exposed_tongue_mm,
                         align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)).translate((p.x_j1_center, 0.0, z_plug_tip))
    z_body_top = p.z_j1_mouth - p.usbc_exposed_tongue_mm
    plug_body = bd.Box(p.usbc_plug_90_thick_x, p.usbc_plug_90_w_y, p.usbc_plug_90_len - p.usbc_exposed_tongue_mm,
                       align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)).translate((p.x_j1_center, 0.0, z_body_top))
    plug_strain = bd.Cone(3.4, 2.3, p.usbc_strain_relief_h,
                          align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).rotate(bd.Axis.X, -90.0).translate((p.x_j1_center, 0.5 * p.usbc_plug_90_w_y, p.clamp_z))
    usbc_plug_assy = plug_barrel.fuse(plug_body).fuse(plug_strain)

    # Top bent steel coat-hanger wire bail (Ø2.3 mm wire, ~Ø8 mm closed eyes riding on both ±X flanged spools on M4 bolt)
    x_sp_c = x_sp_in + 3.0  # Spool groove center: 18.05 mm nom / 18.25 mm WC
    r_eye = 4.90
    r_wire = 1.15  # Ø2.3 mm steel coat-hanger wire (0.15 mm clear of Ø7.2 mm barrel, 0.35 mm clear of 43-deg cheeks)
    z_eye_top = p.z_hang_hole + r_eye  # 294.90 mm (meets top of 360-deg bent wire eyes seamlessly)
    eye_pos = bd.Torus(major_radius=r_eye, minor_radius=r_wire).rotate(bd.Axis.Y, 90.0).translate((x_sp_c, 0.0, p.z_hang_hole))
    eye_neg = bd.Torus(major_radius=r_eye, minor_radius=r_wire).rotate(bd.Axis.Y, 90.0).translate((-x_sp_c, 0.0, p.z_hang_hole))
    with bd.BuildLine(bd.Plane.XY) as l_cord:
        bd.ThreePointArc((-x_sp_c, z_eye_top), (-22.8, p.z_plug_top_end + 3.0), (-12.0, p.z_plug_top_end + 28.0))
        bd.ThreePointArc((-12.0, p.z_plug_top_end + 28.0), (0.0, p.z_plug_top_end + 35.0), (12.0, p.z_plug_top_end + 28.0))
        bd.ThreePointArc((12.0, p.z_plug_top_end + 28.0), (22.8, p.z_plug_top_end + 3.0), (x_sp_c, z_eye_top))
    cord_wire = l_cord.wire()
    pl_cord = bd.Plane(origin=cord_wire.position_at(0.0), z_dir=cord_wire.tangent_at(0.0))
    with bd.BuildSketch(pl_cord) as sk_cord:
        bd.Circle(r_wire)
    cord_arch = bd.sweep(sk_cord.sketch, path=cord_wire).rotate(bd.Axis.X, 90.0)
    hang_loop = cord_arch.fuse(eye_pos).fuse(eye_neg)

    # Captive 15 x 15 mm PCB->Al-core thermal bridge (2x 1.0 mm silicone pads + 15x15x0.5 mm brass shims in chute)
    x_tb_min = 0.5 * core_w + 0.05
    x_tb_max = p.pcb_x_bcu - 0.05
    thermal_bridge = bd.Box(
        x_tb_max - x_tb_min, 15.0, 15.0,
        align=(bd.Align.MIN, bd.Align.CENTER, bd.Align.MIN),
    ).translate((x_tb_min, 0.0, p.pcb_thermal_win_z_bot + 0.05))

    return dict(
        cap_bot=cap_bot,
        top_base=top_base,
        cap_top=cap_top,
        plug_top=plug_top,
        cable_clamp=cable_clamp,
        hang_loop=hang_loop,
        pcb_assy=pcb_assy,
        thermal_bridge=thermal_bridge,
        hs_core=hs_core,
        inserts_brass=inserts_brass,
        fasteners_m3=fasteners_m3,
        glass_tube=glass_tube,
        dtp_stars=dtp_stars,
        sw1_assy=sw1_assy,
        usbc_plug_assy=usbc_plug_assy,
        usbc_cable=usbc_cable,
    )


def _raycast_mesh_numpy(mesh: trimesh.Trimesh, origins: np.ndarray, dirs: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    tris = mesh.triangles
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
        f1, s1, u1 = f[m1], s[m1], u[m1]
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
    """Exterior-to-interior ray-cast breach checks on sealed umbrella bell roof, side wall (incl. D12 dimple), and blind clamp inserts."""
    results: dict[str, dict | bool] = {}

    # 1. MECH-CAP-TOP lofted rain roof & collar (zero top breaches)
    m_top = trimesh.load(str(out_dir / "mech_cap_top.stl"), force="mesh")
    origins, dirs = [], []
    for rad in np.linspace(20.6, 44.0, 12):
        for ang in np.linspace(0.0, 2.0 * math.pi, 36, endpoint=False):
            origins.append([rad * math.cos(ang), rad * math.sin(ang), p.z_cap_top_top + 10.0])
            dirs.append([0.0, 0.0, -1.0])
    locs, idx_ray = _raycast_mesh_numpy(m_top, np.array(origins), np.array(dirs))
    hit_by_ray: dict[int, float] = {}
    for pt_h, r_i in zip(locs, idx_ray):
        hit_by_ray[int(r_i)] = max(hit_by_ray.get(int(r_i), -999.0), float(pt_h[2]))
    breaches_top = sum(1 for i in range(len(origins)) if hit_by_ray.get(i, -999.0) <= p.cap_top_ceil_cone_z)
    results["cap_top_roof_raycast_zero_holes"] = {
        "rays_cast": len(origins),
        "roof_breaches": breaches_top,
        "pass": breaches_top == 0,
    }

    # 2. MECH-TOP-BASE +Y blind clamp insert walls at (±13.0, Z = clamp_z)
    m_tb = trimesh.load(str(out_dir / "mech_top_base.stl"), force="mesh")
    tb_orig = [[sx * p.clamp_bolt_dx, 30.0, p.clamp_z] for sx in (-1.0, 1.0)]
    tb_dirs = [[0.0, 1.0, 0.0], [0.0, 1.0, 0.0]]
    l_locs, l_idx = _raycast_mesh_numpy(m_tb, np.array(tb_orig), np.array(tb_dirs))
    tb_min_y: dict[int, float] = {}
    for pt_h, r_i in zip(l_locs, l_idx):
        tb_min_y[int(r_i)] = min(tb_min_y.get(int(r_i), 999.0), float(pt_h[1]))
    sealed_cnt = sum(1 for i in range(2) if tb_min_y.get(i, 999.0) < 39.5)
    results["top_base_blind_clamp_insert_seal"] = {
        "inserts_checked": 2,
        "sealed_walls_hit": sealed_cnt,
        "pass": sealed_cnt == 2,
    }

    # 3. MECH-CAP-TOP outer vertical bell wall (incl. Z = 190.9 mm D12 translucent dimple -> MUST remain watertight!)
    b_orig, b_dir = [], []
    z_samples = list(np.linspace(185.0, 228.0, 8)) + [p.z_d12]
    for zv in z_samples:
        for ang in np.linspace(0.0, 2.0 * math.pi, 36, endpoint=False):
            b_orig.append([60.0 * math.cos(ang), 60.0 * math.sin(ang), float(zv)])
            b_dir.append([-math.cos(ang), -math.sin(ang), 0.0])
    b_locs, b_idx = _raycast_mesh_numpy(m_top, np.array(b_orig), np.array(b_dir))
    max_r_hit: dict[int, float] = {}
    for pt_h, r_i in zip(b_locs, b_idx):
        rh = math.hypot(float(pt_h[0]), float(pt_h[1]))
        max_r_hit[int(r_i)] = max(max_r_hit.get(int(r_i), 0.0), rh)
    side_breaches = sum(1 for i in range(len(b_orig)) if max_r_hit.get(i, 0.0) <= p.cap_top_bore_id / 2.0 + 0.5)
    results["cap_top_bell_wall_zero_side_holes"] = {
        "rays_cast": len(b_orig),
        "wall_breaches": side_breaches,
        "pass": side_breaches == 0,
    }

    # 4. MECH-CAP-TOP upper chimney collar (Z = 247.5 .. 254.0 mm, zero side screw holes!)
    c_orig, c_dir = [], []
    for zv in (248.5, 250.5, 252.5):
        for ang in np.linspace(0.0, 2.0 * math.pi, 24, endpoint=False):
            c_orig.append([35.0 * math.cos(ang), 35.0 * math.sin(ang), float(zv)])
            c_dir.append([-math.cos(ang), -math.sin(ang), 0.0])
    c_locs, c_idx = _raycast_mesh_numpy(m_top, np.array(c_orig), np.array(c_dir))
    max_rc: dict[int, float] = {}
    for pt_h, r_i in zip(c_locs, c_idx):
        max_rc[int(r_i)] = max(max_rc.get(int(r_i), 0.0), max(abs(float(pt_h[0])), abs(float(pt_h[1]))))
    col_breaches = sum(1 for i in range(len(c_orig)) if max_rc.get(i, 0.0) <= 0.5 * p.core_pocket_w + 1.0)
    results["cap_top_collar_zero_side_holes"] = {
        "rays_cast": len(c_orig),
        "collar_breaches": col_breaches,
        "pass": col_breaches == 0,
    }

    # 5. Verify -Y breather vent is genuinely open (zero ray hits along 35-deg downward-outward bore axis!)
    v_dir = np.array([[0.0, -math.sin(math.radians(35.0)), -math.cos(math.radians(35.0))]])
    v_orig = np.array([[0.0, p.vent_floor_y, p.z_top_base_port_bot - p.vent_pocket_depth]]) - 1.5 * v_dir
    v_locs, _ = _raycast_mesh_numpy(m_tb, v_orig, v_dir)
    results["top_base_breather_vent_open_drain"] = {
        "axis_ray_hits": int(len(v_locs)),
        "pass": len(v_locs) == 0,
    }

    results["all_pass"] = all(v["pass"] for k, v in results.items() if isinstance(v, dict))
    return results


def check_fastener_seat_bearing(cap_bot: bd.Part, top_base: bd.Part, cap_top: bd.Part, p: LepiLEDParams) -> dict[str, dict | bool]:
    results: dict[str, dict | bool] = {}

    # 1. cap_bot M4 x 50 cross-bolt bearing faces at |X| = 21.0 mm (Z = 12.5 mm)
    ideal_m4 = math.pi * (4.0 ** 2 - 2.30 ** 2) * 2.0
    bot_ratios = []
    for sx in (-1.0, 1.0):
        ring = (
            bd.Cylinder(4.0, 2.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX))
            - bd.Cylinder(2.30, 2.2, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)).translate((0, 0, 0.1))
        ).rotate(bd.Axis.Y, 90.0 if sx > 0 else -90.0).translate((sx * 21.0, 0.0, p.z_bot_bolt))
        inter = cap_bot & ring
        bot_ratios.append((float(inter.volume) if inter is not None else 0.0) / ideal_m4)
    results["cap_bot_m4_bolt_seat_bearing"] = {"min_contact_ratio": round(min(bot_ratios), 4), "min_required": 0.90, "pass": min(bot_ratios) >= 0.90}

    # 2. top_base 4x M3x12 CSK diagonal bolt-ear seats at R = 51.0 mm
    ideal_m3 = math.pi * (2.75 ** 2 - 1.70 ** 2) * 2.0
    ear_ratios = []
    z_ear_bot = p.z_top_base_deck_top - p.top_base_ear_h
    for deg in (45.0, 135.0, 225.0, 315.0):
        rad = math.radians(deg)
        ex, ey = p.top_base_ear_r * math.cos(rad), p.top_base_ear_r * math.sin(rad)
        ring = (
            bd.Cylinder(2.75, 2.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
            - bd.Cylinder(1.70, 2.2, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)).translate((0, 0, -0.1))
        ).translate((ex, ey, z_ear_bot + 1.6))
        inter = top_base & ring
        ear_ratios.append((float(inter.volume) if inter is not None else 0.0) / ideal_m3)
    results["top_base_ear_bolt_seat_bearing"] = {"min_contact_ratio": round(min(ear_ratios), 4), "min_required": 0.90, "pass": min(ear_ratios) >= 0.90}

    # 3. Core socket 4-wall intactness check on cap_bot, top_base & cap_top
    bot_wall_ok, tb_wall_ok, top_wall_ok = True, True, True
    x_sock = p.core_pocket_w / 2.0 + 0.05
    for ang in (0.0, 90.0, 180.0, 270.0):
        probe_b = bd.Box(2.5, 16.0, 8.0, align=(bd.Align.MIN, bd.Align.CENTER, bd.Align.MIN)).translate((x_sock, 0.0, p.z_core_bot + 13.0)).rotate(bd.Axis.Z, ang)
        vb = float((cap_bot & probe_b).volume) if (cap_bot & probe_b) is not None else 0.0
        if vb < 0.70 * (2.5 * 16.0 * 8.0):
            bot_wall_ok = False
    for ang in (0.0, 180.0):
        probe_tb = bd.Box(2.5, 16.0, 8.0, align=(bd.Align.MIN, bd.Align.CENTER, bd.Align.MIN)).translate((x_sock, 0.0, p.z_top_base_bot + 4.0)).rotate(bd.Axis.Z, ang)
        vtb = float((top_base & probe_tb).volume) if (top_base & probe_tb) is not None else 0.0
        if vtb < 0.70 * (2.5 * 16.0 * 8.0):
            tb_wall_ok = False
    for sy in (-1.0, 1.0):
        for sx in (-1.0, 1.0):
            probe_tby = bd.Box(8.0, 2.5, 8.0, align=(bd.Align.CENTER, bd.Align.MIN if sy > 0 else bd.Align.MAX, bd.Align.MIN)).translate((sx * 9.5, sy * x_sock, p.z_top_base_bot + 4.0))
            vtby = float((top_base & probe_tby).volume) if (top_base & probe_tby) is not None else 0.0
            if vtby < 0.70 * (2.5 * 8.0 * 8.0):
                tb_wall_ok = False
    for ang in (0.0, 90.0, 180.0, 270.0):
        probe_t = bd.Box(2.5, 16.0, 6.0, align=(bd.Align.MIN, bd.Align.CENTER, bd.Align.MIN)).translate((x_sock, 0.0, p.z_cap_top_collar_bot + 1.0)).rotate(bd.Axis.Z, ang)
        vt = float((cap_top & probe_t).volume) if (cap_top & probe_t) is not None else 0.0
        if vt < 0.70 * (2.5 * 16.0 * 6.0):
            top_wall_ok = False
    results["core_sockets_4wall_intact"] = {
        "cap_bot_4wall_ok": bot_wall_ok,
        "top_base_4wall_ok": tb_wall_ok,
        "cap_top_4wall_ok": top_wall_ok,
        "pass": bot_wall_ok and tb_wall_ok and top_wall_ok,
    }
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
    max_area_mm2: float = 1.0,
    allowed_box: tuple[tuple[float, float, float], tuple[float, float, float]] | None = None,
    allowed_box_max_area_mm2: float = 0.0,
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

    total_bad_area = float(np.sum(areas[bad]))
    outside_bad_area = total_bad_area
    if allowed_box is not None and np.any(bad):
        lo, hi = np.array(allowed_box[0], dtype=float), np.array(allowed_box[1], dtype=float)
        c_bad = centers[bad]
        in_box = np.all((c_bad >= lo) & (c_bad <= hi), axis=1)
        in_box_area = float(np.sum(areas[bad][in_box]))
        outside_bad_area = float(np.sum(areas[bad][~in_box]))
        passed = (outside_bad_area <= max_area_mm2) and (in_box_area <= allowed_box_max_area_mm2)
    else:
        passed = total_bad_area <= max_area_mm2

    return {
        "stl_file": stl_path.name,
        "bed_z_proj_mm": round(z_bed, 3),
        "off_bed_overhang_gt46_faces": int(np.sum(bad)),
        "off_bed_overhang_gt46_area_mm2": round(total_bad_area, 3),
        "off_bed_overhang_gt46_outside_allowed_mm2": round(outside_bad_area, 3),
        "max_off_bed_overhang_deg": round(float(np.max(angles_deg)) if len(angles_deg) else 0.0, 2),
        "pass": passed,
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
    top_base = assy["top_base"]
    cap_top = assy["cap_top"]
    r_port = p.top_base_port_od / 2.0

    # 1. SW1 horizontal insertion from inside dry bay outward along -X into recessed pocket
    x_sw_face = -(r_port - p.sw1_recess_x)
    sw_body = bd.Box(p.sw1_body_d_x, p.sw1_body_w_y, p.sw1_body_h_z, align=(bd.Align.MIN, bd.Align.CENTER, bd.Align.CENTER))
    sw_lugs = bd.Box(p.sw1_lugs_d_x, 10.0, 8.5, align=(bd.Align.MIN, bd.Align.CENTER, bd.Align.CENTER)).translate((p.sw1_body_d_x, 0.0, 0.0))
    sw_bush = bd.Cylinder(p.sw1_hole_dia / 2.0 - 0.12, 8.89, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MAX)).rotate(bd.Axis.Y, 90.0)
    sw_tool = bd.Compound([sw_body, sw_lugs, sw_bush])
    sw_max_vol = 0.0
    for xw in np.linspace(-23.0, x_sw_face + p.sw1_wall_thick + 0.05, 15):
        inter = top_base & sw_tool.translate((float(xw), 0.0, p.sw1_z))
        sw_max_vol = max(sw_max_vol, float(inter.volume) if inter is not None else 0.0)

    # 2. One-stroke vertical umbrella closure sweep: MECH-CAP-TOP slides straight down over wired PCB + core + plug
    wired_chassis = bd.Compound([top_base, assy["pcb_assy"], assy["usbc_plug_assy"], assy["sw1_assy"], assy["hs_core"]])
    bell_max_vol = 0.0
    for dz in np.linspace(75.0, 0.0, 20):
        inter = wired_chassis & cap_top.translate((0.0, 0.0, float(dz)))
        bell_max_vol = max(bell_max_vol, float(inter.volume) if inter is not None else 0.0)

    # 3. Pre-crimped 2-pin JST-XH plug vertical sweep up through both ±Y wire channels
    jst_plug_tool = bd.Box(7.4, 5.75, 12.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER))
    y_slot_c = p.core_pocket_w / 2.0 + p.core_wire_slot_d / 2.0 - 0.1
    jst_max_vol = 0.0
    for sy in (-1.0, 1.0):
        for zj in np.linspace(p.z_top_base_bot - 5.0, p.z_top_base_port_bot + 10.0, 15):
            inter = top_base & jst_plug_tool.translate((0.0, sy * y_slot_c, float(zj)))
            jst_max_vol = max(jst_max_vol, float(inter.volume) if inter is not None else 0.0)

    # 4. Outward pass of straight charger-end USB-C plug (12.6 x 24.0 x 6.8 mm) through +Y gable port
    straight_plug_tool = bd.Box(12.6, 24.0, 6.8, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER))
    port_max_vol = 0.0
    for yp in np.linspace(r_port - 14.0, r_port + 14.0, 15):
        inter = top_base & straight_plug_tool.translate((0.0, float(yp), 153.0))
        port_max_vol = max(port_max_vol, float(inter.volume) if inter is not None else 0.0)

    # 5. Full 18 mm 90-deg USB-C plug vertical unmated->mated insertion into J1 (checks bay floor & baffle clearance!)
    plug_real = assy["usbc_plug_assy"]
    j1_mate_vol = 0.0
    for dz_p in np.linspace(-6.0, 0.0, 12):
        inter = top_base & plug_real.translate((0.0, 0.0, float(dz_p)))
        j1_mate_vol = max(j1_mate_vol, float(inter.volume) if inter is not None else 0.0)

    return {
        "sw1_side_ring_insertion": {"waypoints_tested": 15, "max_intersection_vol_mm3": round(sw_max_vol, 6), "pass": sw_max_vol < 1e-4},
        "cap_top_bell_straight_down_closure": {"waypoints_tested": 20, "max_intersection_vol_mm3": round(bell_max_vol, 6), "pass": bell_max_vol < 1e-4},
        "jst_xh_plug_wire_slot_sweep": {"waypoints_tested": 30, "max_intersection_vol_mm3": round(jst_max_vol, 6), "pass": jst_max_vol < 1e-4},
        "usbc_straight_plug_outward_port_pass": {"waypoints_tested": 15, "max_intersection_vol_mm3": round(port_max_vol, 6), "pass": port_max_vol < 1e-4},
        "usbc_18mm_90_plug_j1_mating_sweep": {"waypoints_tested": 12, "max_intersection_vol_mm3": round(j1_mate_vol, 6), "pass": j1_mate_vol < 1e-4},
        "all_zero": (sw_max_vol < 1e-4) and (bell_max_vol < 1e-4) and (jst_max_vol < 1e-4) and (port_max_vol < 1e-4) and (j1_mate_vol < 1e-4),
    }


def compute_mass_budget(mesh_checks: dict, assy_nom: dict[str, bd.Shape]) -> dict[str, float]:
    vol_printed_cm3 = (
        mesh_checks["mech_cap_bot"]["brep_volume_mm3"]
        + mesh_checks["mech_top_base"]["brep_volume_mm3"]
        + mesh_checks["mech_cap_top"]["brep_volume_mm3"]
        + mesh_checks["mech_plug_top"]["brep_volume_mm3"]
        + mesh_checks["mech_cable_clamp"]["brep_volume_mm3"]  # Already includes BOTH mirrored L+R halves!
    ) / 1000.0
    asa_fdm_g = vol_printed_cm3 * 1.07 * 0.62
    petg_fdm_g = vol_printed_cm3 * 1.27 * 0.62
    al_core_g = (float(assy_nom["hs_core"].volume) / 1000.0) * 2.70
    pmma_shroud_g = (float(assy_nom["glass_tube"].volume) / 1000.0) * 1.18
    elec_stars_hw_g = 94.0  # Reduced fastener count (10 M3 + 2 M4 SS + 10 inserts + PCB + 8 Cu stars + switch + mesh)

    return {
        "printed_lamp_volume_cm3": round(vol_printed_cm3, 1),
        "cap_bot_volume_cm3": round(mesh_checks["mech_cap_bot"]["brep_volume_mm3"] / 1000.0, 1),
        "top_base_volume_cm3": round(mesh_checks["mech_top_base"]["brep_volume_mm3"] / 1000.0, 1),
        "cap_top_volume_cm3": round(mesh_checks["mech_cap_top"]["brep_volume_mm3"] / 1000.0, 1),
        "asa_fdm_62pct_g": round(asa_fdm_g, 1),
        "petg_fdm_62pct_g": round(petg_fdm_g, 1),
        "al_core_2mm_g": round(al_core_g, 1),
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

    # Export pre-mirrored cable clamp pair (L + R halves laid flat on outer flange face, spaced 6 mm apart!)
    cl_pos = build_cable_clamp_half(p_fdm, side=+1.0).rotate(bd.Axis.X, -90.0)
    cl_neg = build_cable_clamp_half(p_fdm, side=-1.0).rotate(bd.Axis.X, -90.0)
    bb_p = cl_pos.bounding_box()
    bb_n = cl_neg.bounding_box()
    cl_pos_p = cl_pos.translate((-bb_p.min.X + 3.0, -0.5 * (bb_p.min.Y + bb_p.max.Y), -bb_p.min.Z))
    cl_neg_p = cl_neg.translate((-bb_n.max.X - 3.0, -0.5 * (bb_n.min.Y + bb_n.max.Y), -bb_n.min.Z))
    clamp_pair_print = bd.Compound([cl_pos_p, cl_neg_p])

    # Export ventilated finial + 2x 6.0 mm flanged M4 cord spools together flush on inverted print bed (Z = 324.0 mm)
    plug_finial_only = build_plug_top(p_fdm)
    spool_bed = build_cord_spool(p_fdm)
    plug_top_print = bd.Compound([
        plug_finial_only,
        spool_bed.translate((29.0, 0.0, p_fdm.z_plug_top_end - 6.0)),
        spool_bed.translate((-29.0, 0.0, p_fdm.z_plug_top_end - 6.0)),
    ])

    mesh_checks = {
        "mech_cap_bot": export_and_verify_stl(assy_nom["cap_bot"], out_dir / "mech_cap_bot.step", out_dir / "mech_cap_bot.stl"),
        "mech_top_base": export_and_verify_stl(assy_nom["top_base"], out_dir / "mech_top_base.step", out_dir / "mech_top_base.stl"),
        "mech_cap_top": export_and_verify_stl(assy_nom["cap_top"], out_dir / "mech_cap_top.step", out_dir / "mech_cap_top.stl"),
        "mech_plug_top": export_and_verify_stl(plug_top_print, out_dir / "mech_plug_top.step", out_dir / "mech_plug_top.stl"),
        "mech_cable_clamp": export_and_verify_stl(clamp_pair_print, out_dir / "mech_cable_clamp.step", out_dir / "mech_cable_clamp.stl"),
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

    # Note: top_base allows strictly the intentional 2.5 mm-deep round Ø6.50 mm SW1 boot-seal bore (12.48 mm^2);
    #       cap_top allows strictly the 0.6 mm-deep debossed "OFF UV ALL" legend on the -X visor face;
    #       everywhere else on all 6 parts must be <= 1.0 mm^2!
    x_sw0 = -(0.5 * p_fdm.top_base_port_od - p_fdm.sw1_recess_x)
    sw1_bore_box = (
        (x_sw0 - 0.2, -p_fdm.sw1_hole_dia / 2.0 - 0.2, p_fdm.sw1_z),
        (x_sw0 + p_fdm.sw1_wall_thick + 0.2, p_fdm.sw1_hole_dia / 2.0 + 0.2, p_fdm.sw1_z + p_fdm.sw1_hole_dia / 2.0 + 0.3),
    )
    visor_text_box = (
        (-p_fdm.cap_top_sw_visor_x - 0.2, -18.5, p_fdm.z_cap_top_bot + 3.5),
        (-p_fdm.cap_top_sw_visor_x + 1.0, 18.5, p_fdm.z_cap_top_eaves_top),
    )
    overhang_checks = {
        "mech_cap_bot": audit_stl_overhangs(out_dir / "mech_cap_bot.stl", (0.0, 0.0, 1.0)),
        "mech_top_base": audit_stl_overhangs(
            out_dir / "mech_top_base.stl", (0.0, 0.0, 1.0),
            max_area_mm2=1.0, allowed_box=sw1_bore_box, allowed_box_max_area_mm2=13.0,
        ),
        "mech_cap_top": audit_stl_overhangs(
            out_dir / "mech_cap_top.stl", (0.0, 0.0, 1.0),
            max_area_mm2=1.0, allowed_box=visor_text_box, allowed_box_max_area_mm2=25.0,
        ),
        "mech_plug_top": audit_stl_overhangs(out_dir / "mech_plug_top.stl", (0.0, 0.0, -1.0)),
        "mech_cable_clamp": audit_stl_overhangs(out_dir / "mech_cable_clamp.stl", (0.0, 0.0, 1.0)),
        "mech_drill_jig": audit_stl_overhangs(out_dir / "mech_drill_jig.stl", (0.0, 0.0, 1.0)),
    }

    breach_checks = check_shell_raycast_breaches(out_dir, p_fdm)
    seat_checks = check_fastener_seat_bearing(assy_nom["cap_bot"], assy_nom["top_base"], assy_nom["cap_top"], p_fdm)

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
        "revision": "Rev 6.0 (Open-Chimney Funnel Lantern: Screened 30x30x2 mm Al Chimney, Thermal-Epoxy Stars, +X Vertical PCB, Axial Bell O-Ring & Compressing Cable Clamp)",
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
            "brep_all_pairs_zero_interference": all_brep_ok,
            "kinematic_insertion_zero_interference": all_kinematic_ok,
            "overall_pass": (
                all_param_checks_ok and all_meshes_ok and all_overhangs_ok
                and all_breaches_ok and all_seats_ok and all_brep_ok and all_kinematic_ok
            ),
        },
    }
    (out_dir / "cad_verification.json").write_text(json.dumps(report, indent=2) + "\n")

    print("=== Rev 6.0 CAD Generation & Automated Verification ===")
    for k, m in mesh_checks.items():
        oh = overhang_checks[k]
        print(f"  {k:18s}: watertight={m['is_watertight']} vol={m['stl_volume_mm3']:9.1f}mm3 >46deg={oh['off_bed_overhang_gt46_area_mm2']:6.3f}mm2 (outside={oh['off_bed_overhang_gt46_outside_allowed_mm2']:5.3f}mm2, pass={oh['pass']})")
    print(f"  Ray-cast breaches : all_pass={breach_checks['all_pass']} | roof={breach_checks['cap_top_roof_raycast_zero_holes']['roof_breaches']} bell={breach_checks['cap_top_bell_wall_zero_side_holes']['wall_breaches']} collar={breach_checks['cap_top_collar_zero_side_holes']['collar_breaches']} clamp={breach_checks['top_base_blind_clamp_insert_seal']['sealed_walls_hit']}/2 vent_hits={breach_checks['top_base_breather_vent_open_drain']['axis_ray_hits']}")
    print(f"  Fastener seats    : all_pass={seat_checks['all_pass']}")
    print(f"  Kinematic sweeps  : all_zero={kinematic_checks['all_zero']}")
    for kk, kv in kinematic_checks.items():
        if isinstance(kv, dict) and not kv["pass"]:
            print(f"    [KIN FAIL] {kk}: {kv}")
    print(f"  B-Rep Nominal     : {inter_nom['nonzero_count']}/{inter_nom['total_pairs_checked']} nonzero {inter_nom['nonzero_pairs']}")
    print(f"  B-Rep Worst-Case  : {inter_wc['nonzero_count']}/{inter_wc['total_pairs_checked']} nonzero {inter_wc['nonzero_pairs']}")
    print(f"  Mass budget       : {mass_budget['total_fdm_asa_g']:.1f} g ASA / {mass_budget['total_fdm_petg_g']:.1f} g PETG (Al={mass_budget['al_core_2mm_g']:.1f}g, PMMA={mass_budget['uvt_pmma_shroud_g']:.1f}g, printed={mass_budget['petg_fdm_62pct_g']:.1f}g)")
    print(f"  OVERALL PASS      : {report['summary']['overall_pass']}")
    if not report["summary"]["overall_pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
