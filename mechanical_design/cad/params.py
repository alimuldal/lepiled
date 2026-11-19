#!/usr/bin/env python3
"""
Single Source of Truth for LepiLED DIY Maxi Switch (M3) Mechanical & CAD Parameters.

All coordinates are in millimeters (mm) using a right-handed global frame:
  - Origin (0, 0, 0): Center of the bottom resting face of MECH-HS-EXT-BOT.
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
    # Build configuration flags
    process: Literal["FDM", "SLS"] = "FDM"
    power_entry_mode: Literal["M16_GLAND", "USB_C"] = "M16_GLAND"

    # External top heatsink (Fischer Elektronik SK 578/50 SA, Ø60 x 50 mm)
    hs_ext_top_od: float = 60.0
    hs_ext_top_core_dia: float = 24.0
    hs_ext_top_height: float = 50.0
    hs_ext_top_n_fins: int = 22
    hs_ext_top_fin_thick: float = 1.4
    hs_ext_top_hub_bolt_r: float = 8.5  # 4x M3 into solid Ø24 mm hub

    # External bottom heatsink (Fischer Elektronik SK 578/50 SA, Ø60 x 50 mm — identical to top heatsink!)
    # Option 2 (20 V USB-C PD + dual AL8860 buck) cuts PCB heat to 0.50 W nom / 0.82 W worst-case,
    # eliminating the £24.60 SK LED R 80 SA upgrade while passing 20/20 thermal cases with wide margin.
    hs_ext_bot_od: float = 60.0
    hs_ext_bot_core_dia: float = 24.0
    hs_ext_bot_height: float = 50.0
    hs_ext_bot_n_fins: int = 22
    hs_ext_bot_fin_thick: float = 1.4
    hs_ext_bot_hub_bolt_r: float = 8.5   # 4x M3 into solid Ø24 mm base core (matches top heatsink!)

    # Bottom adapter/spreader plate (MECH-ADAPT-BOT: Al 6061 Ø90 x 3.0 mm + Ø59 x 5.0 mm central PCB pedestal)
    adapt_bot_od: float = 90.0
    adapt_bot_thick: float = 3.0
    adapt_bot_pedestal_dia: float = 59.0
    adapt_bot_pedestal_h: float = 5.0
    adapt_bot_bolt_r: float = 40.2  # 4x M3 at 45° outside Ø80 mm heatsink
    # Exact M2 Driver PCB relief pockets (build_driver_pcb.py):
    # J2 (-5.2, +19.2) & J3 (+5.2, +19.2)
    adapt_bot_j23_pocket_x: float = 0.0
    adapt_bot_j23_pocket_y: float = 19.2
    adapt_bot_j23_pocket_w: float = 20.0
    adapt_bot_j23_pocket_l: float = 6.5
    # J4 (-1.4, -2.5)
    adapt_bot_j4_pocket_x: float = -1.4
    adapt_bot_j4_pocket_y: float = -2.5
    adapt_bot_j4_pocket_w: float = 11.0
    adapt_bot_j4_pocket_l: float = 5.5
    # J1 (0.0, -18.50) & TP1/TP2 (±8.2, -19.5), clear of H3/H4 5.5 mm keepouts at (±14.0, -19.0)
    # Widened -Y to Y in [-23.0, -16.0] for 0.64 mm SH3/SH4 tab margin; deepened to 2.5 mm for untrimmed TH pins + Kapton!
    adapt_bot_j1tp_pocket_x: float = 0.0
    adapt_bot_j1tp_pocket_y: float = -19.5
    adapt_bot_j1tp_pocket_w: float = 21.0
    adapt_bot_j1tp_pocket_l: float = 7.0
    adapt_bot_pin_pocket_depth: float = 2.5

    # Top adapter plate (MECH-ADAPT-TOP: Al 6061 Ø76 x 3.0 mm)
    adapt_top_od: float = 76.0
    adapt_top_thick: float = 3.0
    adapt_top_bolt_r: float = 34.0  # 4x M3 at 45° outside Ø60 mm heatsink & core corners

    # PCB thermal gap pad (MECH-TIM-PCB: TGlobal TG-A6200-150-0.5, 0.5 mm, 6.2 W/mK)
    tim_pcb_thick: float = 0.5
    tim_pcb_w: float = 34.0
    tim_pcb_l: float = 44.0

    # Driver PCB (M2 Interface Contract §1.1 & build_driver_pcb.py)
    pcb_w: float = 36.0
    pcb_l: float = 46.0
    pcb_thick: float = 1.6
    pcb_corner_r: float = 2.0
    pcb_smd_max_h: float = 4.8       # L1/L2 SRN6045 = 4.5 mm
    pcb_jst_mated_h: float = 9.8     # J2..J4 JST XH mated
    pcb_jst_pin_protrude: float = 1.8
    pcb_hole_x: float = 14.0         # H1..H4 at (±14.0, ±19.0)
    pcb_hole_y: float = 19.0
    pcb_hole_drill: float = 2.7
    pcb_hole_keepout: float = 5.5

    # End-cap shared & bottom flange envelopes
    cap_bot_od: float = 92.0
    cap_top_od: float = 84.0
    cap_chamfer: float = 0.8
    min_wall: float = 2.5

    # Bottom end-cap internal cavity & bulkhead (40.3 deg cone to apex for 0 mm^2 >46 deg STL overhang)
    cap_bot_cavity_dia: float = 61.0
    cap_bot_cavity_full_h: float = 17.0   # Z = 73.0 -> 90.0 (14.4 mm above 80.1 PCB top)
    cap_bot_taper_h: float = 36.0         # Z = 90.0 -> 126.0 (40.3 deg inward taper all the way to apex)
    bulkhead_thick: float = 6.0           # Z = 126.0 -> 132.0 (>= 5.0 mm thermal isolation)

    # Bottom cap-to-plate O-ring (MECH-GASKET-3: 66x2.0 mm VMQ70, self-supporting 45° V-roof groove)
    bot_oring_r_in: float = 33.0
    bot_oring_r_out: float = 35.5
    bot_oring_flat_h: float = 0.80        # vertical wall before 45° V-roof apex (+1.25 mm -> Z_base + 2.05 mm)

    # Side cutouts in MECH-CAP-BOT (Z adjusted -20.0 mm for 50 mm SK 578/50 SA bottom heatsink!)
    # M16x1.5 gland (-Y side) with 22.5 mm AF anti-rotation hex pocket + 45° symmetric pitched roof
    m16_z: float = 74.5
    m16_hole_dia: float = 16.2
    m16_spotface_dia: float = 24.0
    m16_spotface_y: float = -44.0
    m16_wall_thick: float = 3.5
    m16_nut_af: float = 22.5              # captive anti-rotation flat-to-flat for 22 mm AF M16 locknut
    m16_nut_depth: float = 5.5
    m16_nut_half_vert: float = 6.5        # vertical flat height +/-6.5 mm around m16_z (corner dia = 25.98 mm)

    # USB-C direct-mate recessed tunnel (-Y side, when power_entry_mode == "USB_C")
    # Open 13.6 x 7.8 mm overmold tunnel passes straight through the Ø92->Ø61 mm cap wall into the cavity
    # so standard 6.65 mm USB-C PD laptop-charger plugs mate directly into J1 (front mouth Y = -25.76 mm)!
    usbc_bezel_w: float = 9.5
    usbc_bezel_h: float = 3.8
    usbc_overmold_w: float = 13.6
    usbc_overmold_h: float = 7.8
    usbc_z_offset_from_pcb_top: float = 1.88
    usbc_j1_front_y: float = -25.76       # GCT USB4085-GF-A exact datum: Row-B (-18.50) - 7.26 mm mouth
    usbc_mating_depth_mm: float = 4.55
    usbc_specified_barrel_mm: float = 6.65  # Standard USB-IF Type-C plug barrel (no exotic extended cable needed!)

    # SW1 toggle switch (+X side, horizontal along Y)
    sw1_z: float = 73.0
    sw1_hole_dia: float = 6.35
    sw1_spotface_dia: float = 15.0
    sw1_spotface_x: float = 45.0
    sw1_wall_thick: float = 2.5           # inside 2.0-3.5 mm SW1_BOOT window
    sw1_alcove_w: float = 15.0            # along Y
    sw1_alcove_h: float = 10.0            # along Z

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
    # Groove R_in=33.20 mm (flush w/ pilot) .. R_out=38.10 mm (width 4.90 mm), depth 2.65 mm:
    # 24.3% squeeze nom, 10.0%-38.6% rigid across 149-151 mm (91.3% <= 92% gland fill at 151 mm)
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

    # Bottom internal anchor block (MECH-ANCHOR-BOT) bolted from open PCB cavity via 2x M4 CSK
    anchor_bot_w: float = 33.2
    anchor_bot_h: float = 12.0
    anchor_bot_bolt_x: float = 9.0        # 2x M4 CSK at (±9.0, 0.0)

    # Top end-cap flange (MECH-CAP-TOP) — flat top face + 4x 0.5 mm SS spacer washers (MECH-FAST-3W)
    # 14.5 mm gives >= 3.10 mm solid plastic between M3 insert cone tips and MECH-GASKET-2 roof
    cap_top_flange_thick: float = 14.5
    cap_top_air_gap_proud: float = 0.5    # core protrudes 0.5 mm above flat cap_top via 0.5 mm M3 spacers

    # Top internal anchor block (MECH-ANCHOR-TOP) & M6 eye bolt (MECH-EYE-1)
    anchor_w: float = 33.2
    anchor_h: float = 14.0
    anchor_top_pin_y: float = 9.0         # 2x M4x40 flush CSK at (0, ±9.0) clear of central M6
    eye_bolt_thread_dia: float = 6.0
    eye_bolt_clearance_dia: float = 6.5

    # LED Al MCPCB strips (MECH-MCPCB-1..4: 20x80x1.6 mm)
    mcpcb_w: float = 20.0
    mcpcb_l: float = 80.0
    mcpcb_thick: float = 1.6
    mcpcb_tim_thick: float = 0.15
    mcpcb_uv_y: float = 18.0
    mcpcb_vis_y: float = -18.0
    mcpcb_pad_y: float = -26.0            # synced to led_mcpcb.kicad_pcb
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

    # Derived global Z coordinates
    @property
    def z_hs_bot_start(self) -> float:
        return 0.0

    @property
    def z_hs_bot_end(self) -> float:
        return self.hs_ext_bot_height  # 70.0

    @property
    def z_adapt_bot_end(self) -> float:
        return self.z_hs_bot_end + self.adapt_bot_thick  # 73.0

    @property
    def z_pcb_seat(self) -> float:
        return self.z_adapt_bot_end + self.adapt_bot_pedestal_h  # 78.0

    @property
    def z_pcb_bot(self) -> float:
        return self.z_pcb_seat + self.tim_pcb_thick  # 78.5

    @property
    def z_pcb_top(self) -> float:
        return self.z_pcb_bot + self.pcb_thick  # 80.1

    @property
    def z_usbc(self) -> float:
        return self.z_pcb_top + self.usbc_z_offset_from_pcb_top  # 81.98

    @property
    def z_cap_bot_cavity_taper_start(self) -> float:
        return self.z_adapt_bot_end + self.cap_bot_cavity_full_h  # 90.0

    @property
    def z_cap_bot_bulkhead_start(self) -> float:
        return self.z_cap_bot_cavity_taper_start + self.cap_bot_taper_h  # 126.0

    @property
    def z_glass_bot(self) -> float:
        return self.z_cap_bot_bulkhead_start + self.bulkhead_thick  # 132.0

    @property
    def z_core_bot(self) -> float:
        return self.z_glass_bot  # 132.0

    @property
    def z_cap_bot_top(self) -> float:
        return self.z_glass_bot + self.glass_socket_depth  # 144.0

    @property
    def z_glass_top(self) -> float:
        return self.z_glass_bot + self.glass_length  # 282.0

    @property
    def z_cap_top_bot(self) -> float:
        return self.z_glass_top - self.glass_socket_depth  # 270.0

    @property
    def z_cap_top_top(self) -> float:
        return self.z_glass_top + self.cap_top_flange_thick  # 296.5

    @property
    def z_core_top(self) -> float:
        return self.z_cap_top_top + self.cap_top_air_gap_proud  # 297.0

    @property
    def core_length(self) -> float:
        return self.z_core_top - self.z_core_bot  # 165.0

    @property
    def exposed_glass_window(self) -> float:
        return self.z_cap_top_bot - self.z_cap_bot_top  # 126.0

    @property
    def z_mcpcb_center(self) -> float:
        return 0.5 * (self.z_glass_bot + self.z_glass_top)  # 207.0

    @property
    def z_led_uv(self) -> float:
        return self.z_mcpcb_center + self.mcpcb_uv_y  # 225.0

    @property
    def z_led_vis(self) -> float:
        return self.z_mcpcb_center + self.mcpcb_vis_y  # 189.0

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
        return self.z_core_top + self.adapt_top_thick  # 300.0

    @property
    def z_hs_top_end(self) -> float:
        return self.z_adapt_top_end + self.hs_ext_top_height  # 350.0

    @property
    def bot_oring_roof_z_max(self) -> float:
        half_w = 0.5 * (self.bot_oring_r_out - self.bot_oring_r_in)
        return self.z_adapt_bot_end + self.bot_oring_flat_h + half_w  # 73.0 + 0.8 + 1.25 = 75.05

    @property
    def m16_roof_z_max(self) -> float:
        # True B-Rep peak of 45° pitched roof over 22.5 mm AF hex pocket
        return self.m16_z + self.m16_nut_half_vert + 0.5 * self.m16_nut_af  # 94.5 + 6.5 + 11.25 = 112.25

    def verify_all(self) -> dict[str, dict[str, float | bool]]:
        """Run deterministic geometric & clearance assertions."""
        checks: dict[str, dict[str, float | bool]] = {}

        # 1. PCB radial clearance inside bottom cavity & pedestal
        pcb_corner_r = math.hypot(self.pcb_w / 2.0 - self.pcb_corner_r,
                                  self.pcb_l / 2.0 - self.pcb_corner_r) + self.pcb_corner_r
        pcb_rad_clr = self.cap_bot_cavity_dia / 2.0 - pcb_corner_r
        pedestal_rad_clr = self.adapt_bot_pedestal_dia / 2.0 - pcb_corner_r
        checks["pcb_radial_clearance_mm"] = {"value": round(pcb_rad_clr, 3), "min": 1.0, "pass": pcb_rad_clr >= 1.0}
        checks["pcb_on_pedestal_rim_mm"] = {"value": round(pedestal_rad_clr, 3), "min": 0.5, "pass": pedestal_rad_clr >= 0.5}

        # 2. Vertical clearance above PCB top to 45 deg conical ceiling at J2/J3 outer radius
        r_jst_outer = math.hypot(5.2 + 3.7, 19.2 + 2.9)  # 23.82 mm
        z_cone_at_jst = self.z_cap_bot_cavity_taper_start + (self.cap_bot_cavity_dia / 2.0 - r_jst_outer)
        jst_vert_clr = z_cone_at_jst - (self.z_pcb_top + self.pcb_jst_mated_h)
        pcb_edge_clr = self.z_cap_bot_cavity_taper_start - self.z_pcb_top
        checks["pcb_cavity_edge_headroom_mm"] = {"value": round(pcb_edge_clr, 3), "min": 8.0, "pass": pcb_edge_clr >= 8.0}
        checks["pcb_jst_cone_headroom_mm"] = {"value": round(jst_vert_clr, 3), "min": 5.0, "pass": jst_vert_clr >= 5.0}

        # 3. Bulkhead thermal isolation thickness
        checks["bulkhead_thickness_mm"] = {"value": self.bulkhead_thick, "min": 5.0, "pass": self.bulkhead_thick >= 5.0}

        # 4. M16 gland locknut clearance to MECH-GASKET-3, PCB edge, and MECH-GASKET-1
        m16_nut_z_bot = self.m16_z - self.m16_nut_af / math.sqrt(3.0)  # bottom hex vertex
        m16_inner_wall_y = self.m16_spotface_y + self.m16_wall_thick  # -40.5
        m16_nut_inner_y = m16_inner_wall_y + self.m16_nut_depth       # -35.0
        m16_pcb_gap = (-self.pcb_l / 2.0) - m16_nut_inner_y           # 12.0
        g1_z_bot = self.z_glass_bot - self.glass_oring_depth          # 129.35
        checks["m16_above_gasket3_mm"] = {"value": round(m16_nut_z_bot - self.bot_oring_roof_z_max, 3), "min": 2.5, "pass": (m16_nut_z_bot - self.bot_oring_roof_z_max) >= 2.5}
        checks["m16_nut_to_pcb_y_mm"] = {"value": round(m16_pcb_gap, 3), "min": 3.0, "pass": m16_pcb_gap >= 3.0}
        checks["m16_roof_below_gasket1_mm"] = {"value": round(g1_z_bot - self.m16_roof_z_max, 3), "min": 2.5, "pass": (g1_z_bot - self.m16_roof_z_max) >= 2.5}

        # 5. USB-C direct-mate recessed tunnel clearance above Z_base, MECH-ADAPT-BOT pedestal, and MECH-GASKET-3
        usbc_overmold_z_bot = self.z_usbc - self.usbc_overmold_h / 2.0
        usbc_overmold_roof_z = self.z_usbc + self.usbc_overmold_h / 2.0 + 0.5 * self.usbc_overmold_w
        j1_front_y = self.usbc_j1_front_y  # -25.76 mm exact GCT USB4085-GF-A Row-B (-18.50) - 7.26 mm datum
        # Standard 6.65 mm USB-C plug seats 4.55 mm into J1; overmold stops cleanly at Y = -27.86 mm inside open cavity
        usbc_overmold_face_y = j1_front_y + self.usbc_mating_depth_mm - self.usbc_specified_barrel_mm
        usbc_barrel_exposed_mm = abs(usbc_overmold_face_y - j1_front_y)
        checks["usbc_above_base_mm"] = {"value": round(usbc_overmold_z_bot - self.z_adapt_bot_end, 3), "min": 2.5, "pass": (usbc_overmold_z_bot - self.z_adapt_bot_end) >= 2.5}
        checks["usbc_above_pedestal_mm"] = {"value": round(usbc_overmold_z_bot - self.z_pcb_seat, 3), "min": 0.05, "pass": usbc_overmold_z_bot > self.z_pcb_seat}
        checks["usbc_above_gasket3_mm"] = {"value": round(usbc_overmold_z_bot - self.bot_oring_roof_z_max, 3), "min": 2.5, "pass": (usbc_overmold_z_bot - self.bot_oring_roof_z_max) >= 2.5}
        checks["usbc_roof_below_gasket1_mm"] = {"value": round(g1_z_bot - usbc_overmold_roof_z, 3), "min": 2.5, "pass": (g1_z_bot - usbc_overmold_roof_z) >= 2.5}
        checks["usbc_direct_mate_barrel_exposed_mm"] = {"value": round(usbc_barrel_exposed_mm, 3), "min": 1.0, "max": 3.0, "pass": 1.0 <= usbc_barrel_exposed_mm <= 3.0}
        checks["usbc_pocket_depth_mm"] = {"value": round(self.adapt_bot_pin_pocket_depth, 3), "min": 2.5, "pass": self.adapt_bot_pin_pocket_depth >= 2.5}

        # 6. SW1 clearance to PCB and SMD envelope
        sw1_inner_x = self.sw1_spotface_x - self.sw1_wall_thick       # 42.5
        sw1_back_x = sw1_inner_x - (8.89 + 4.8 + 5.0)                 # 23.81
        sw1_pcb_x_gap = sw1_back_x - (self.pcb_w / 2.0)               # 5.81
        sw1_bot_z = self.sw1_z - 6.86 / 2.0                           # 89.57
        sw1_smd_z_gap = sw1_bot_z - (self.z_pcb_top + self.pcb_smd_max_h)
        checks["sw1_wall_window_mm"] = {"value": self.sw1_wall_thick, "min": 2.0, "max": 3.5, "pass": 2.0 <= self.sw1_wall_thick <= 3.5}
        checks["sw1_radial_to_pcb_mm"] = {"value": round(sw1_pcb_x_gap, 3), "min": 1.0, "pass": sw1_pcb_x_gap >= 1.0}
        checks["sw1_z_above_smd_mm"] = {"value": round(sw1_smd_z_gap, 3), "min": 2.0, "pass": sw1_smd_z_gap >= 2.0}

        # 7. Radial clearances inside worst-case borosilicate glass tube (ID_min = 66.5 mm)
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

        # 8. Minimum structural wall thicknesses (>= 2.5 mm everywhere, incl. chamfers & lead-in cones!)
        r_ins = self.insert_m3_hole_dia / 2.0
        bot_cav_to_g3_wall = self.bot_oring_r_in - self.cap_bot_cavity_dia / 2.0
        bot_g3_to_insert_wall = (self.adapt_bot_bolt_r - r_ins) - self.bot_oring_r_out
        bot_insert_outer_wall = (self.cap_bot_od / 2.0 - self.cap_chamfer) - (self.adapt_bot_bolt_r + r_ins + 0.4)
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
            "z_hs_bot_end": self.z_hs_bot_end,
            "z_adapt_bot_end": self.z_adapt_bot_end,
            "z_pcb_seat": self.z_pcb_seat,
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
            "m16_roof_z_max": self.m16_roof_z_max,
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
