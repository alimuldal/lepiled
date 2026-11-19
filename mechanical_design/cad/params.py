#!/usr/bin/env python3
"""
Single Source of Truth for LepiLED DIY Maxi Switch (Rev 4.1 — S1-A / S2-A / S3) Mechanical & CAD Parameters.

Rev 4.1 Major Simplifications & Adversarial Review Fixes:
  - S1-A: Eliminated bottom SK 578/50 SA heatsink, CNC-milled MECH-ADAPT-BOT pedestal, TG-A6200 gap pad,
    bottom 4x M3x14 hub bolts, and Kapton pocket lining. Replaced with flat 3D-printed MECH-LID-BOT
    featuring 4x integral 11.5 mm M2.5 PCB standoff bosses (zero CNC milling across the entire lamp!).
  - S2-A: Unified USB-C PD ONLY entry (removed M16_GLAND & TP1/TP2 Aux inputs).
  - 3A:   Flat-faced Ø20.2 x 2.5 mm rubber membrane grommet flange (fits off-the-shelf £0.30 20 mm
    grommet, e.g. RS/Eaton KT-M20 / SES 20 mm DG) + open direct-mate USB-C tunnel into J1.
  - S3:   C&K 7211SYZBE gold DPDT toggle switch (12.7 x 11.43 x 10.67 mm body, 1/4-40 bushing) alcove.
  - B-H3: MECH-ANCHOR-TOP (32x32x14 mm stock Al bar) recessed 0.50 mm below core top with tight Ø4.2 mm
    round top cross-pin bores so eye-bolt torque preloads MECH-HS-CORE tightly against MECH-ADAPT-TOP.
  - Zero milling: MECH-ADAPT-TOP = stock Ø76.2 mm (3") x 3.0 mm Al disc; MECH-ANCHOR-TOP/BOT = stock
    32 x 32 mm Al square bar (saw-cut & drill/tap only).

All coordinates are in millimeters (mm) using a right-handed global frame:
  - Origin (0, 0, 0): Center of the bottom resting face of MECH-LID-BOT.
  - +Z: Vertically upward along the lamp centerline toward MECH-CAP-TOP and MECH-EYE-1.
  - +X, +Y: Normal to the 4 flat faces of the 40x40x3 mm MECH-HS-CORE tube.
"""

from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Literal


@dataclass(frozen=True)
class LepiLEDParams:
    # Build configuration flags (Rev 4.1: unified USB-C PD only!)
    process: Literal["FDM", "SLS"] = "FDM"

    # External top heatsink (Fischer Elektronik SK 578/50 SA, Ø60 x 50 mm — SOLE external heatsink!)
    hs_ext_top_od: float = 60.0
    hs_ext_top_core_dia: float = 24.0
    hs_ext_top_height: float = 50.0
    hs_ext_top_n_fins: int = 22
    hs_ext_top_fin_thick: float = 1.4
    hs_ext_top_hub_bolt_r: float = 8.5  # 4x M3 CSK into solid Ø24 mm hub

    # Flat 3D-printed bottom lid (MECH-LID-BOT: Ø92 x 4.0 mm + 4x integral 11.5 mm M2.5 PCB bosses)
    lid_bot_od: float = 92.0
    lid_bot_thick: float = 4.0
    lid_bot_bolt_r: float = 40.2        # 4x M3 at 45° outside MECH-GASKET-3
    pcb_boss_h: float = 11.5            # Elevates PCB to Z=15.5 mm -> Z_USBC=18.98 mm (clears Ø20.2 grommet + O-ring!)
    pcb_boss_od: float = 6.2            # Ø6.2 mm standoff boss (3.8 mm radial clearance inside Ø61 mm cavity)
    pcb_boss_insert_dia: float = 3.5    # M2.5 x 4.0 mm brass heat-set insert bore
    pcb_boss_insert_depth: float = 4.5

    # Top adapter plate (MECH-ADAPT-TOP: off-the-shelf 3" / Ø76.2 x 3.0 mm Al 6061-T6 disc)
    adapt_top_od: float = 76.2
    adapt_top_thick: float = 3.0
    adapt_top_bolt_r: float = 34.0      # 4x M3 at 45° outside Ø60 mm heatsink & core corners

    # Driver PCB (Rev 4.1 build_driver_pcb.py — isolated NPTH H1..H4, USB-C only, no Aux TP1/TP2)
    pcb_w: float = 36.0
    pcb_l: float = 46.0
    pcb_thick: float = 1.6
    pcb_corner_r: float = 2.0
    pcb_smd_max_h: float = 4.8          # L1/L2 SRN6045 = 4.5 mm
    pcb_jst_mated_h: float = 9.8        # J2..J4 JST XH mated
    pcb_jst_pin_protrude: float = 1.8   # 9.7 mm air clearance above lid top!
    pcb_hole_x: float = 14.0            # H1..H4 isolated NPTH at (±14.0, ±19.0)
    pcb_hole_y: float = 19.0
    pcb_hole_drill: float = 2.7
    pcb_hole_keepout: float = 5.5

    # End-cap shared & bottom flange envelopes
    cap_bot_od: float = 92.0
    cap_top_od: float = 84.0
    cap_chamfer: float = 0.8
    min_wall: float = 2.5

    # Bottom end-cap internal cavity & bulkhead (40.3 deg cone to apex for <1 mm^2 >46 deg STL overhang)
    cap_bot_cavity_dia: float = 61.0
    cap_bot_cavity_full_h: float = 24.0   # Z = 4.0 -> 28.0 (10.9 mm above Z_pcb_top = 17.1 mm!)
    cap_bot_taper_h: float = 36.0         # Z = 28.0 -> 64.0 (40.3 deg inward taper all the way to apex)
    bulkhead_thick: float = 6.0           # Z = 64.0 -> 70.0 (>= 5.0 mm thermal isolation)

    # Bottom lid-to-cap O-ring (MECH-GASKET-3: 66x2.0 mm VMQ70, self-supporting 45° V-roof groove)
    bot_oring_r_in: float = 33.0
    bot_oring_r_out: float = 35.5
    bot_oring_flat_h: float = 0.80        # vertical wall before 45° V-roof apex (+1.25 mm -> Z_base + 2.05 mm)

    # Unified USB-C direct-mate entry + off-the-shelf Ø20.2 mm rubber membrane grommet flange (-Y side, 3A!)
    usbc_overmold_w: float = 13.6
    usbc_overmold_h: float = 7.8
    usbc_z_offset_from_pcb_top: float = 1.88
    usbc_j1_front_y: float = -25.76       # GCT USB4085-GF-A exact datum: Row-B (-18.50) - 7.26 mm mouth
    usbc_mating_depth_mm: float = 4.55
    usbc_specified_barrel_mm: float = 6.65  # Standard USB-IF Type-C plug barrel
    grommet_outer_spotface_y: float = -43.5  # Flat vertical face for 20 mm rubber grommet outer lip
    grommet_outer_spotface_dia: float = 26.0 # Flat face clears Ø25 mm outer flange of 20 mm rubber grommet
    grommet_panel_thick: float = 2.5         # 2.5 mm panel flange thickness (fits 2.0-3.2 mm M20/20 mm grommets!)
    grommet_bore_dia: float = 20.2           # Fits off-the-shelf 20 mm rubber membrane grommet (e.g. Eaton KT-M20 / SES 20 mm)
    grommet_back_relief_dia: float = 23.6    # Back groove clearance for snapped-in rubber grommet inner lip
    grommet_back_relief_depth: float = 2.5   # Y = -41.0 .. -38.5 (completely outside MECH-GASKET-3 R=35.5 mm!)

    # SW1 toggle switch (+X side, C&K 7211SYZBE gold DPDT On-On-On: 12.7 x 11.43 x 10.67 mm body, 1/4-40 bushing!)
    sw1_z: float = 30.0
    sw1_hole_dia: float = 6.35
    sw1_spotface_dia: float = 15.0
    sw1_spotface_x: float = 45.0
    sw1_wall_thick: float = 2.5           # inside 2.0-3.5 mm C&K 759D02000 boot window
    sw1_body_depth: float = 10.67         # C&K 7211 DPDT body depth behind bushing
    sw1_body_w_y: float = 12.70           # C&K 7211 DPDT body width along Y
    sw1_body_h_z: float = 11.43           # C&K 7211 DPDT body height along Z (across dual poles)
    sw1_lugs_depth: float = 4.80
    sw1_alcove_w: float = 15.0            # along Y
    sw1_alcove_h: float = 13.5            # along Z (clears 11.43 mm DPDT body with >1 mm per side)

    # Borosilicate glass tube (MECH-TUBE-1: CRH Supplies 75/68/3.5 x 150 +/- 1.0 mm)
    glass_od_nom: float = 75.0
    glass_id_nom: float = 68.0
    glass_od_max: float = 76.0
    glass_id_min: float = 66.5
    glass_length: float = 150.0
    glass_length_tol: float = 1.0
    glass_socket_depth: float = 12.0
    glass_pilot_od: float = 66.4
    glass_skirt_id_top: float = 76.8
    glass_skirt_id_bot: float = 76.2

    # Glass axial face-seal O-ring (MECH-GASKET-1..2: 68x3.5 mm VMQ70)
    glass_oring_id: float = 66.4
    glass_oring_od: float = 76.2
    glass_oring_cs: float = 3.5
    glass_oring_depth: float = 2.65

    # Central heatsink core (MECH-HS-CORE: 40x40x3 mm Al 6063)
    core_w_nom: float = 40.0
    core_w_max: float = 40.5
    core_wall: float = 3.0
    core_bore_nom: float = 34.0
    core_pocket_w: float = 41.0
    core_wire_slot_w: float = 6.0
    core_wire_slot_d: float = 3.5

    # Bottom internal anchor block (MECH-ANCHOR-BOT: stock 32x32 mm Al square bar, 12 mm long — ZERO milling!)
    anchor_bot_w: float = 32.0
    anchor_bot_h: float = 12.0
    anchor_bot_bolt_x: float = 9.0        # 2x M4 CSK at (±9.0, 0.0)

    # Top end-cap flange (MECH-CAP-TOP) — flat top face + 4x 0.5 mm SS spacer washers (MECH-FAST-3W)
    cap_top_flange_thick: float = 14.5
    cap_top_air_gap_proud: float = 0.5    # core protrudes 0.5 mm above flat cap_top via 0.5 mm M3 spacers

    # Top internal anchor block (MECH-ANCHOR-TOP: stock 32x32 mm Al square bar, 14 mm long, 0.50 mm preload recess!)
    anchor_w: float = 32.0
    anchor_h: float = 14.0
    anchor_top_recess: float = 0.50       # Fixes Opus B-H3: anchor sits 0.50 mm below core top -> eye-bolt preloads core!
    anchor_top_pin_y: float = 9.0         # 2x M4x40 flush CSK through tight Ø4.2 mm round bores (no vertical slots!)
    eye_bolt_thread_dia: float = 6.0
    eye_bolt_clearance_dia: float = 6.5

    # LED Al MCPCB strips (MECH-MCPCB-1..4: 20x80x1.6 mm, Rev 4.1 pads shifted +2 mm north to -24.0 mm)
    mcpcb_w: float = 20.0
    mcpcb_l: float = 80.0
    mcpcb_thick: float = 1.6
    mcpcb_tim_thick: float = 0.15
    mcpcb_uv_y: float = 18.0
    mcpcb_vis_y: float = -18.0
    mcpcb_pad_y: float = -24.0            # synced to Rev 4.1 led_mcpcb.kicad_pcb!
    mcpcb_mount_y: float = 32.0
    led_uv_max_h: float = 2.08            # SST-10-UV 1.98 +/- 0.10 mm
    led_vis_max_h: float = 2.39           # XP-E2 2.26 +/- 0.13 mm
    m3_shcs_head_h: float = 3.00          # DIN 912 M3 head

    @property
    def print_clearance(self) -> float:
        return 0.25 if self.process == "FDM" else 0.15

    @property
    def insert_m3_hole_dia(self) -> float:
        return 4.1 if self.process == "FDM" else 4.0

    @property
    def insert_m3_depth(self) -> float:
        return 6.7

    # Derived global Z coordinates (Origin Z=0.0 = bottom resting face of MECH-LID-BOT)
    @property
    def z_lid_bot_start(self) -> float:
        return 0.0

    @property
    def z_lid_bot_end(self) -> float:
        return self.lid_bot_thick  # 4.0

    @property
    def z_pcb_bot(self) -> float:
        return self.z_lid_bot_end + self.pcb_boss_h  # 15.5

    @property
    def z_pcb_top(self) -> float:
        return self.z_pcb_bot + self.pcb_thick  # 17.1

    @property
    def z_usbc(self) -> float:
        return self.z_pcb_top + self.usbc_z_offset_from_pcb_top  # 18.98

    @property
    def z_cap_bot_cavity_taper_start(self) -> float:
        return self.z_lid_bot_end + self.cap_bot_cavity_full_h  # 28.0

    @property
    def z_cap_bot_bulkhead_start(self) -> float:
        return self.z_cap_bot_cavity_taper_start + self.cap_bot_taper_h  # 64.0

    @property
    def z_glass_bot(self) -> float:
        return self.z_cap_bot_bulkhead_start + self.bulkhead_thick  # 70.0

    @property
    def z_core_bot(self) -> float:
        return self.z_glass_bot  # 70.0

    @property
    def z_cap_bot_top(self) -> float:
        return self.z_glass_bot + self.glass_socket_depth  # 82.0

    @property
    def z_glass_top(self) -> float:
        return self.z_glass_bot + self.glass_length  # 220.0

    @property
    def z_cap_top_bot(self) -> float:
        return self.z_glass_top - self.glass_socket_depth  # 208.0

    @property
    def z_cap_top_top(self) -> float:
        return self.z_glass_top + self.cap_top_flange_thick  # 234.5

    @property
    def z_core_top(self) -> float:
        return self.z_cap_top_top + self.cap_top_air_gap_proud  # 235.0

    @property
    def core_length(self) -> float:
        return self.z_core_top - self.z_core_bot  # 165.0

    @property
    def exposed_glass_window(self) -> float:
        return self.z_cap_top_bot - self.z_cap_bot_top  # 126.0

    @property
    def z_mcpcb_center(self) -> float:
        return 0.5 * (self.z_glass_bot + self.z_glass_top)  # 145.0

    @property
    def z_led_uv(self) -> float:
        return self.z_mcpcb_center + self.mcpcb_uv_y  # 163.0

    @property
    def z_led_vis(self) -> float:
        return self.z_mcpcb_center + self.mcpcb_vis_y  # 127.0

    @property
    def axial_uv_to_top_mm(self) -> float:
        return self.z_core_top - self.z_led_uv  # 72.0

    @property
    def axial_uv_to_vis_mm(self) -> float:
        return self.z_led_uv - self.z_led_vis  # 36.0

    @property
    def axial_vis_to_bot_mm(self) -> float:
        return self.z_led_vis - self.z_core_bot  # 57.0

    @property
    def z_adapt_top_end(self) -> float:
        return self.z_core_top + self.adapt_top_thick  # 238.0

    @property
    def z_hs_top_end(self) -> float:
        return self.z_adapt_top_end + self.hs_ext_top_height  # 288.0

    @property
    def bot_oring_roof_z_max(self) -> float:
        half_w = 0.5 * (self.bot_oring_r_out - self.bot_oring_r_in)
        return self.z_lid_bot_end + self.bot_oring_flat_h + half_w  # 4.0 + 0.8 + 1.25 = 6.05

    def verify_all(self) -> dict[str, dict[str, float | bool]]:
        """Run deterministic geometric & clearance assertions."""
        checks: dict[str, dict[str, float | bool]] = {}

        # 1. PCB & Boss radial clearance inside bottom cavity + TH pin vertical air clearance
        pcb_corner_r = math.hypot(self.pcb_w / 2.0 - self.pcb_corner_r,
                                  self.pcb_l / 2.0 - self.pcb_corner_r) + self.pcb_corner_r
        pcb_rad_clr = self.cap_bot_cavity_dia / 2.0 - pcb_corner_r
        boss_outer_r = math.hypot(self.pcb_hole_x, self.pcb_hole_y) + self.pcb_boss_od / 2.0
        boss_rad_clr = self.cap_bot_cavity_dia / 2.0 - boss_outer_r
        pin_air_clr = self.pcb_boss_h - self.pcb_jst_pin_protrude
        checks["pcb_radial_clearance_mm"] = {"value": round(pcb_rad_clr, 3), "min": 1.0, "pass": pcb_rad_clr >= 1.0}
        checks["boss_radial_clearance_mm"] = {"value": round(boss_rad_clr, 3), "min": 2.0, "pass": boss_rad_clr >= 2.0}
        checks["th_pin_under_pcb_air_mm"] = {"value": round(pin_air_clr, 3), "min": 3.0, "pass": pin_air_clr >= 3.0}

        # 2. Vertical clearance above PCB top to 40.3 deg conical ceiling at J2/J3 outer radius
        r_jst_outer = math.hypot(5.2 + 3.7, 19.2 + 2.9)  # 23.82 mm
        cone_slope = self.cap_bot_taper_h / (self.cap_bot_cavity_dia / 2.0)
        z_cone_at_jst = self.z_cap_bot_cavity_taper_start + cone_slope * (self.cap_bot_cavity_dia / 2.0 - r_jst_outer)
        jst_vert_clr = z_cone_at_jst - (self.z_pcb_top + self.pcb_jst_mated_h)
        pcb_edge_clr = self.z_cap_bot_cavity_taper_start - self.z_pcb_top
        checks["pcb_cavity_edge_headroom_mm"] = {"value": round(pcb_edge_clr, 3), "min": 8.0, "pass": pcb_edge_clr >= 8.0}
        checks["pcb_jst_cone_headroom_mm"] = {"value": round(jst_vert_clr, 3), "min": 5.0, "pass": jst_vert_clr >= 5.0}

        # 3. Bulkhead thermal isolation thickness
        checks["bulkhead_thickness_mm"] = {"value": self.bulkhead_thick, "min": 5.0, "pass": self.bulkhead_thick >= 5.0}

        # 4. USB-C direct-mate tunnel + Ø20.2 mm rubber grommet flange clearances (Option 3A)
        g1_z_bot = self.z_glass_bot - self.glass_oring_depth
        grommet_bore_z_bot = self.z_usbc - self.grommet_bore_dia / 2.0
        grommet_back_z_bot = self.z_usbc - self.grommet_back_relief_dia / 2.0
        grommet_back_y_in = self.grommet_outer_spotface_y + self.grommet_panel_thick + self.grommet_back_relief_depth  # -38.5
        grommet_to_g3_radial = abs(grommet_back_y_in) - self.bot_oring_r_out  # 38.5 - 35.5 = 3.0 mm
        usbc_overmold_z_bot = self.z_usbc - self.usbc_overmold_h / 2.0
        usbc_overmold_roof_z = self.z_usbc + self.usbc_overmold_h / 2.0 + 0.5 * self.usbc_overmold_w * math.tan(math.radians(47.0))
        usbc_overmold_face_y = self.usbc_j1_front_y + self.usbc_mating_depth_mm - self.usbc_specified_barrel_mm
        usbc_barrel_exposed_mm = abs(usbc_overmold_face_y - self.usbc_j1_front_y)
        checks["grommet_panel_thick_mm"] = {"value": self.grommet_panel_thick, "min": 2.0, "max": 3.2, "pass": 2.0 <= self.grommet_panel_thick <= 3.2}
        checks["grommet_bore_above_gasket3_mm"] = {"value": round(grommet_bore_z_bot - self.bot_oring_roof_z_max, 3), "min": 2.5, "pass": (grommet_bore_z_bot - self.bot_oring_roof_z_max) >= 2.5}
        checks["grommet_back_above_lid_mm"] = {"value": round(grommet_back_z_bot - self.z_lid_bot_end, 3), "min": 2.5, "pass": (grommet_back_z_bot - self.z_lid_bot_end) >= 2.5}
        checks["grommet_back_to_gasket3_r_mm"] = {"value": round(grommet_to_g3_radial, 3), "min": 2.5, "pass": grommet_to_g3_radial >= 2.5}
        checks["usbc_tunnel_above_gasket3_mm"] = {"value": round(usbc_overmold_z_bot - self.bot_oring_roof_z_max, 3), "min": 2.5, "pass": (usbc_overmold_z_bot - self.bot_oring_roof_z_max) >= 2.5}
        checks["usbc_roof_below_gasket1_mm"] = {"value": round(g1_z_bot - usbc_overmold_roof_z, 3), "min": 2.5, "pass": (g1_z_bot - usbc_overmold_roof_z) >= 2.5}
        checks["usbc_direct_mate_barrel_mm"] = {"value": round(usbc_barrel_exposed_mm, 3), "min": 1.0, "max": 3.0, "pass": 1.0 <= usbc_barrel_exposed_mm <= 3.0}

        # 5. SW1 (C&K 7211SYZBE DPDT) clearance to PCB and SMD envelope
        sw1_inner_x = self.sw1_spotface_x - self.sw1_wall_thick       # 42.5
        sw1_back_x = sw1_inner_x - (self.sw1_body_depth + self.sw1_lugs_depth + 4.5)  # 22.53
        sw1_pcb_x_gap = sw1_back_x - (self.pcb_w / 2.0)               # 4.53
        sw1_bot_z = self.sw1_z - self.sw1_body_h_z / 2.0              # 24.285
        sw1_smd_z_gap = sw1_bot_z - (self.z_pcb_top + self.pcb_smd_max_h)
        checks["sw1_wall_window_mm"] = {"value": self.sw1_wall_thick, "min": 2.0, "max": 3.5, "pass": 2.0 <= self.sw1_wall_thick <= 3.5}
        checks["sw1_radial_to_pcb_mm"] = {"value": round(sw1_pcb_x_gap, 3), "min": 1.0, "pass": sw1_pcb_x_gap >= 1.0}
        checks["sw1_z_above_smd_mm"] = {"value": round(sw1_smd_z_gap, 3), "min": 2.0, "pass": sw1_smd_z_gap >= 2.0}

        # 6. Radial clearances inside worst-case borosilicate glass tube (ID_min = 66.5 mm)
        r_glass_min = self.glass_id_min / 2.0
        r_pilot = self.glass_pilot_od / 2.0
        r_core_max_corner = math.hypot(self.core_w_max / 2.0, self.core_w_max / 2.0)
        r_led_vis_max = self.core_w_nom / 2.0 + self.mcpcb_tim_thick + self.mcpcb_thick + self.led_vis_max_h
        r_m3_head_max = self.core_w_nom / 2.0 + self.mcpcb_tim_thick + self.mcpcb_thick + self.m3_shcs_head_h
        checks["pilot_to_glass_id_min_mm"] = {"value": round(r_glass_min - r_pilot, 3), "min": 0.02, "pass": r_glass_min > r_pilot}
        checks["skirt_to_glass_od_max_mm"] = {"value": round(self.glass_skirt_id_top / 2.0 - self.glass_od_max / 2.0, 3), "min": 0.2, "pass": self.glass_skirt_id_top > self.glass_od_max}
        checks["core_corner_to_glass_id_min_mm"] = {"value": round(r_glass_min - r_core_max_corner, 3), "min": 1.0, "pass": r_glass_min - r_core_max_corner >= 1.0}
        checks["led_vis_to_glass_id_min_mm"] = {"value": round(r_glass_min - r_led_vis_max, 3), "min": 1.0, "pass": r_glass_min - r_led_vis_max >= 1.0}
        checks["m3_head_to_glass_id_min_mm"] = {"value": round(r_glass_min - r_m3_head_max, 3), "min": 1.0, "pass": r_glass_min - r_m3_head_max >= 1.0}

        # 7. Minimum structural wall thicknesses (>= 2.5 mm everywhere, incl. chamfers & lead-in cones!)
        r_ins = self.insert_m3_hole_dia / 2.0
        bot_cav_to_g3_wall = self.bot_oring_r_in - self.cap_bot_cavity_dia / 2.0
        bot_g3_to_insert_wall = (self.lid_bot_bolt_r - r_ins) - self.bot_oring_r_out
        bot_insert_outer_wall = (self.cap_bot_od / 2.0 - self.cap_chamfer) - (self.lid_bot_bolt_r + r_ins + 0.4)
        skirt_wall = self.cap_top_od / 2.0 - self.glass_skirt_id_top / 2.0
        pilot_corner_wall = self.glass_pilot_od / 2.0 - math.hypot(self.core_pocket_w / 2.0, self.core_pocket_w / 2.0)
        top_insert_core_wall = (self.adapt_top_bolt_r - r_ins) - math.hypot(self.core_pocket_w / 2.0, self.core_pocket_w / 2.0)
        top_insert_outer_wall = (self.cap_top_od / 2.0 - self.cap_chamfer) - (self.adapt_top_bolt_r + r_ins + 0.4)
        top_insert_tip_z = self.z_cap_top_top - self.insert_m3_depth - r_ins
        g2_roof_z = self.z_glass_top + self.glass_oring_depth
        top_insert_above_g2 = top_insert_tip_z - g2_roof_z
        checks["bot_cav_to_gasket3_wall_mm"] = {"value": round(bot_cav_to_g3_wall, 3), "min": self.min_wall, "pass": bot_cav_to_g3_wall >= self.min_wall}
        checks["bot_gasket3_to_insert_wall_mm"] = {"value": round(bot_g3_to_insert_wall, 3), "min": self.min_wall, "pass": bot_g3_to_insert_wall >= self.min_wall}
        checks["bot_insert_to_chamfer_wall_mm"] = {"value": round(bot_insert_outer_wall, 3), "min": self.min_wall, "pass": bot_insert_outer_wall >= self.min_wall}
        checks["glass_skirt_min_wall_mm"] = {"value": round(skirt_wall, 3), "min": self.min_wall, "pass": skirt_wall >= self.min_wall}
        checks["pilot_corner_min_wall_mm"] = {"value": round(pilot_corner_wall, 3), "min": self.min_wall, "pass": pilot_corner_wall >= self.min_wall}
        checks["top_insert_to_core_wall_mm"] = {"value": round(top_insert_core_wall, 3), "min": self.min_wall, "pass": top_insert_core_wall >= self.min_wall}
        checks["top_insert_to_chamfer_wall_mm"] = {"value": round(top_insert_outer_wall, 3), "min": self.min_wall, "pass": top_insert_outer_wall >= self.min_wall}
        checks["top_insert_above_gasket2_mm"] = {"value": round(top_insert_above_g2, 3), "min": 2.5, "pass": top_insert_above_g2 >= 2.5}

        # 8. Top butt-joint preload recess (Opus B-H3 fix) + stock 32 mm bar bore clearance
        checks["anchor_top_preload_recess_mm"] = {"value": self.anchor_top_recess, "min": 0.3, "max": 1.0, "pass": 0.3 <= self.anchor_top_recess <= 1.0}
        checks["anchor_stock_bar_clearance_mm"] = {"value": round(0.5 * (self.core_bore_nom - self.anchor_w), 3), "min": 0.3, "pass": (self.core_bore_nom - self.anchor_w) >= 0.6}

        # 9. Glass length tolerance O-ring squeeze & gland fill (149.0 .. 151.0 mm)
        squeeze_nom = (self.glass_oring_cs - self.glass_oring_depth) / self.glass_oring_cs
        squeeze_min = (self.glass_oring_cs - (self.glass_oring_depth + 0.5 * self.glass_length_tol)) / self.glass_oring_cs
        squeeze_max = (self.glass_oring_cs - (self.glass_oring_depth - 0.5 * self.glass_length_tol)) / self.glass_oring_cs
        groove_w = 0.5 * (self.glass_oring_od - self.glass_oring_id)
        oring_area = math.pi * (0.5 * self.glass_oring_cs) ** 2
        gland_h_at_151 = self.glass_oring_depth - 0.5 * self.glass_length_tol
        gland_fill_at_151 = oring_area / (groove_w * gland_h_at_151)
        checks["glass_oring_squeeze_min_pct"] = {"value": round(100.0 * squeeze_min, 1), "min": 10.0, "pass": squeeze_min >= 0.10}
        checks["glass_oring_squeeze_nom_pct"] = {"value": round(100.0 * squeeze_nom, 1), "min": 20.0, "max": 35.0, "pass": 0.20 <= squeeze_nom <= 0.35}
        checks["glass_oring_squeeze_max_pct"] = {"value": round(100.0 * squeeze_max, 1), "max": 45.0, "pass": squeeze_max <= 0.45}
        checks["gland_fill_at_151"] = {"value": round(gland_fill_at_151, 4), "max": 0.92, "pass": gland_fill_at_151 <= 0.92}

        return checks

    def to_dict(self) -> dict:
        d = asdict(self)
        d["derived"] = {
            "z_lid_bot_end": self.z_lid_bot_end,
            "z_pcb_bot": self.z_pcb_bot,
            "z_pcb_top": self.z_pcb_top,
            "z_usbc": self.z_usbc,
            "z_cap_bot_cavity_taper_start": self.z_cap_bot_cavity_taper_start,
            "z_cap_bot_bulkhead_start": self.z_cap_bot_bulkhead_start,
            "z_glass_bot": self.z_glass_bot,
            "z_core_bot": self.z_core_bot,
            "z_cap_bot_top": self.z_cap_bot_top,
            "z_glass_top": self.z_glass_top,
            "z_cap_top_bot": self.z_cap_top_bot,
            "z_cap_top_top": self.z_cap_top_top,
            "z_core_top": self.z_core_top,
            "core_length_mm": self.core_length,
            "exposed_glass_window_mm": self.exposed_glass_window,
            "z_mcpcb_center": self.z_mcpcb_center,
            "z_led_uv": self.z_led_uv,
            "z_led_vis": self.z_led_vis,
            "axial_uv_to_top_mm": self.axial_uv_to_top_mm,
            "axial_uv_to_vis_mm": self.axial_uv_to_vis_mm,
            "axial_vis_to_bot_mm": self.axial_vis_to_bot_mm,
            "z_adapt_top_end": self.z_adapt_top_end,
            "z_hs_top_end": self.z_hs_top_end,
            "bot_oring_roof_z_max": self.bot_oring_roof_z_max,
        }
        d["checks"] = self.verify_all()
        return d


if __name__ == "__main__":
    p = LepiLEDParams()
    out_path = Path(__file__).with_name("cad_params.json")
    data = p.to_dict()
    out_path.write_text(json.dumps(data, indent=2))
    print(f"Wrote {out_path}")
    all_pass = True
    for name, c in data["checks"].items():
        status = "PASS" if c["pass"] else "FAIL"
        print(f"  [{status}] {name:34s}: {c}")
        if not c["pass"]:
            all_pass = False
    if not all_pass:
        raise SystemExit(1)
