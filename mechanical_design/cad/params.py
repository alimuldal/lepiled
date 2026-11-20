#!/usr/bin/env python3
"""
Single Source of Truth for LepiLED DIY Maxi Switch (Rev 4.4 — Vertical PCB, Bottom USB-C & Seamless Weatherproof Housing).

Rev 4.4 Key Architecture (Zero Side Penetrations + Unobstructed Hanging + UVT PMMA Shroud):
  1. Vertical Driver PCB + Bottom-Entry USB-C Power (Zero Side Holes, Zero Cable Hang-Tilt):
     - Stands the unchanged Rev 4.2/4.3 `driver_pcb` (36 x 46 mm) vertically at Y_back = -8.48 mm inside
       two integral card-guide rails on MECH-LID-BOT, with its upper corners captured beneath the 44 deg
       cavity cone for rock-solid axial plug support (0 PCB screws, 0 brass inserts, £0 BOM delta).
     - J1 USB-C points straight down through the existing 20 mm rubber membrane grommet (MECH-GROMMET-1)
       seated directly in MECH-LID-BOT at (0.0, -5.0 mm), eliminating cable tilt when hanging and removing
       every side penetration from MECH-CAP-BOT (100% seamless unbroken outer wall!).
  2. Bottom-Mounted Toggle Switch (SW1) + Bolt-On Protective Base Stand Ring (MECH-BASE-RING):
     - C&K 7211SYZBE + C&K 759D02000 silicone boot mounts vertically beside the USB-C grommet on MECH-LID-BOT
       at (0.0, +16.5 mm), shielded inside MECH-BASE-RING (Ø92 x 68 x 18 mm, 4x wide drainage/cable cutouts).
  3. Shatter-Resistant UV-Transmitting PMMA Shroud + Integral Ø116 mm Drip-Brim:
     - 120 g UVT PMMA cylinder (Ø75 x 69 x 3.0 x 150 mm, 85-92% @ 365 nm) on 68 x 3.5 mm VMQ70 O-rings.
     - Single 250 mm bare 40 x 40 x 3.0 mm Al 6063 core protruding 85.5 mm above MECH-CAP-TOP (Ø116 mm
       drip-brim w/ 1.5 mm underside drip-break groove), unobstructed Ø8 mm hang hole & silicone-sealed rain plug.

All coordinates are in millimeters (mm) using a right-handed global frame:
  - Origin (0, 0, 0): Bottom face of MECH-LID-BOT (MECH-BASE-RING extends downward to Z = -18.0 mm).
  - +Z: Vertically upward along the lamp centerline toward MECH-CAP-TOP and MECH-PLUG-TOP.
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
    process: Literal["FDM", "SLS"] = "FDM"

    # Protective bolt-on standing ring / switch guard (MECH-BASE-RING: Z = -18.0 .. 0.0 mm, clamps w/ same 4x M3x16)
    base_ring_od: float = 92.0
    base_ring_id: float = 68.0          # Open Ø68 mm finger & USB-C access around bottom SW1 + grommet
    base_ring_h: float = 18.0           # Shields 15.0 mm C&K 759D02000 silicone boot by 3.0 mm above flat ground
    base_ring_bolt_web: float = 2.5     # 2.5 mm seat web -> M3x16 SHCS engages full captive M3 nut in cap_bot!
    base_ring_cb_dia: float = 6.4       # Clears Ø5.5 mm M3 SHCS head + 2.5 mm hex key (2.60 mm outer wall!)
    base_ring_drain_w: float = 22.0     # 4x wide drainage / 90-deg USB-C cable exit cutouts at 0/90/180/270 deg
    base_ring_drain_h: float = 7.5

    # Flat 3D-printed bottom lid (MECH-LID-BOT: Ø92 x 5.0 mm + vertical PCB card-guide rails + bottom USB-C & SW1)
    lid_bot_od: float = 92.0
    lid_bot_thick: float = 5.0          # 2.5 mm grommet panel web + 2.5 mm upper inner-lip counterbore (0 overhang!)
    lid_bot_bolt_r: float = 40.2        # 4x M3 at 45° outside MECH-GASKET-3 into captive M3 hex nuts

    # Captive M3 hex-nut pocket geometry (DIN 934 M3 nut: 5.5 mm AF, 2.4 mm thick -> 5.8 x 2.7 mm pocket)
    m3_nut_af: float = 5.8
    m3_nut_thick: float = 2.7
    m3_clearance_dia: float = 3.4

    # Driver PCB mounted VERTICALLY (unchanged 36.0 x 46.0 x 1.6 mm board; J1 points straight down, J2/J3 at top!)
    pcb_w: float = 36.0                 # Along global X (±18.0 mm)
    pcb_l: float = 46.0                 # Along global Z (vertical!)
    pcb_thick: float = 1.6              # Along global Y
    pcb_corner_r: float = 2.0
    pcb_smd_max_h: float = 4.8          # L1/L2 SRN6045 = 4.5 mm
    pcb_jst_mated_h: float = 9.8        # J2..J4 JST XH mated toward +Y
    pcb_jst_pin_protrude: float = 1.8   # TH pins protruding toward -Y
    pcb_hole_x: float = 14.0
    pcb_hole_y: float = 19.0
    pcb_hole_drill: float = 2.7
    pcb_hole_keepout: float = 5.5
    pcb_y_front: float = -6.88          # F.Cu face (SMD/JST side facing +Y) -> J1 USB-C centerline Y = -5.00 mm!
    pcb_z_j1_mouth: float = 9.0         # J1 mouth 4.0 mm above lid top -> 1.90 mm clearance above lid for plug overmold!
    pcb_rail_slot_w: float = 2.0        # Vertical card-guide slot gripping 1.6 mm FR4 (0.20 mm clearance/side)
    pcb_rail_grip_x: float = 1.4        # Grips outer 1.4 mm board margin (clears L1/L2 & all copper by >= 0.4 mm!)
    pcb_rail_wall: float = 2.2          # Sturdy 2.2 mm rail walls on MECH-LID-BOT

    # Seamless contoured bottom end-cap outer envelopes (ZERO side cutouts, ZERO side boss!)
    cap_bot_od: float = 92.0            # Lower bolt/gasket flange (Z = 5.0 .. 16.0 mm)
    cap_bot_mid_od: float = 71.0        # Smooth cylindrical body (5.0 mm robust wall around Ø61 mm cavity!)
    cap_bot_waist_od: float = 65.0      # Tapered upper waist (>= 8.5 mm robust wall around wire slots & cone!)
    cap_top_od: float = 84.0            # Upper shroud socket skirt OD (3.5 mm skirt wall)
    cap_top_brim_od: float = 116.0      # Integral Ø116 mm rain drip-brim flange (+12 mm/side past base; 0 deg overhang!)
    cap_top_brim_rim_h: float = 3.8     # Sturdy 3.8 mm brim flange w/ 1.5 mm underside drip-break groove + 3.0 mm gusset
    cap_chamfer: float = 0.8
    min_wall: float = 2.5

    # Bottom end-cap internal cavity & bulkhead (42.7 deg cone to apex -> support-free!)
    cap_bot_cavity_dia: float = 61.0
    cap_bot_cavity_full_h: float = 42.5   # Z = 5.0 -> 47.5 (clears vertical 46 mm PCB + rails!)
    cap_bot_taper_h: float = 33.0         # Z = 47.5 -> 80.5 (atan(30.5/33.0) = 42.75 deg <= 45 deg!)
    bulkhead_thick: float = 6.0           # Z = 80.5 -> 86.5

    # Bottom lid-to-cap O-ring groove (MECH-GASKET-3: 66x2.0 mm VMQ70, optional single O-ring or silicone bead)
    bot_oring_r_in: float = 33.0
    bot_oring_r_out: float = 35.5
    bot_oring_flat_h: float = 0.80

    # Bottom-entry USB-C direct-mate + Ø20.2 x 2.5 mm rubber membrane grommet seated flat in MECH-LID-BOT!
    usbc_overmold_w: float = 13.6
    usbc_overmold_h: float = 7.8
    usbc_z_offset_from_pcb_top: float = 1.88
    usbc_j1_overhang_mm: float = 2.76     # J1 mouth extends 2.76 mm past -23.0 mm PCB bottom edge (Y_pcb = -25.76)
    usbc_mating_depth_mm: float = 4.55
    usbc_specified_barrel_mm: float = 6.65
    grommet_panel_thick: float = 2.5
    grommet_bore_dia: float = 20.2
    grommet_back_relief_dia: float = 23.6
    grommet_back_relief_depth: float = 2.5

    # Bottom-mounted SW1 toggle switch (C&K 7211SYZBE on MECH-LID-BOT at X=0, Y=+16.5 mm, beside USB-C grommet!)
    sw1_x: float = 0.0
    sw1_y: float = 16.5                   # Cleanly separated from USB-C grommet (Y=-5.0) and vertical PCB (Y_front=-6.88)
    sw1_hole_dia: float = 6.35            # 1/4-40 UNS bushing bore
    sw1_wall_thick: float = 2.5           # 2.5 mm upper anti-rotation pocket in 5.0 mm lid -> full boot thread engagement
    sw1_body_w_x: float = 12.70           # C&K 7211SYZBE body width (across poles)
    sw1_body_w_y: float = 11.43           # C&K 7211SYZBE body thickness (along throw)
    sw1_body_h_z: float = 10.67           # Body height upward into cavity
    sw1_lugs_h_z: float = 4.80            # Solder lugs upward into cavity (Z = 2.5 .. 18.0 mm)
    sw1_boot_protrude_z: float = 15.0     # C&K 759D02000 silicone boot downward below Z = 0 (3.0 mm inside 18 mm base ring!)
    sw1_boot_od: float = 13.3

    # Shatter-resistant UV-Transmitting PMMA (Acrylic) shroud (MECH-TUBE-1: 75 mm OD x 3.0 mm wall = 69 mm ID x 150 mm)
    glass_od_nom: float = 75.0
    glass_id_nom: float = 69.0
    glass_od_max: float = 75.6
    glass_id_min: float = 68.0
    glass_length: float = 150.0
    glass_length_tol: float = 1.0
    glass_socket_depth: float = 12.0
    glass_pilot_od: float = 66.8
    glass_skirt_id_top: float = 77.0
    glass_skirt_id_bot: float = 76.6

    # Shroud axial face-seal O-ring (MECH-GASKET-1..2: standard 68x3.5 mm VMQ70 silicone O-ring pair)
    glass_oring_id: float = 66.8
    glass_oring_od: float = 76.6
    glass_oring_cs: float = 3.5
    glass_oring_depth: float = 2.65

    # Central protruding bare Al core (MECH-HS-CORE: stock 250.0 mm cut of 40x40x3.0 mm Al 6063 — kept 3 mm robust!)
    core_w_nom: float = 40.0
    core_w_max: float = 40.5
    core_wall: float = 3.0
    core_bore_nom: float = 34.0
    core_length: float = 250.0
    core_pocket_w: float = 41.0
    core_wire_slot_w: float = 6.0
    core_wire_slot_d: float = 3.5
    core_hang_hole_dia: float = 8.0
    core_hang_hole_from_top: float = 18.0

    # 3D-printed bottom internal core plug (MECH-PLUG-BOT: 33.4x33.4x12.0 mm w/ captive M3 nuts)
    plug_bot_w: float = 33.4
    plug_bot_h: float = 12.0
    plug_bot_bolt_x: float = 9.0
    plug_bot_pin_y: float = 9.0

    # Top end-cap (MECH-CAP-TOP) — slides over protruding core, locks with 2x M3x12 screws into core walls
    cap_top_flange_thick: float = 14.5
    cap_top_lock_z_from_top: float = 7.5  # 2x M3 locking screws 2.65 mm above G2, tucked cleanly below Ø116 mm brim!
    cap_top_seal_groove: float = 1.5

    # 3D-printed top weatherproof rain plug (MECH-PLUG-TOP: caps open top of protruding 40x40x3 mm hollow tube)
    plug_top_w: float = 33.5
    plug_top_insert_h: float = 10.0
    plug_top_cap_w: float = 40.4
    plug_top_cap_h: float = 4.0

    # 8x Off-the-shelf pre-mounted 20 mm Copper DTP LED stars (4x UV + 4x Vis; ZERO custom led_mcpcb!)
    star_dia: float = 20.0
    star_thick: float = 1.50
    star_tim_thick: float = 0.15
    star_uv_z_offset: float = 18.0
    star_vis_z_offset: float = -18.0
    star_bolt_r: float = 9.5
    led_uv_max_h: float = 2.08
    led_vis_max_h: float = 2.39
    m3_pan_plus_washer_h: float = 3.20

    @property
    def print_clearance(self) -> float:
        return 0.25 if self.process == "FDM" else 0.15

    # Derived global coordinates (vertical PCB)
    @property
    def z_base_ring_bot(self) -> float:
        return -self.base_ring_h  # -18.0

    @property
    def z_lid_bot_start(self) -> float:
        return 0.0

    @property
    def z_lid_bot_end(self) -> float:
        return self.lid_bot_thick  # 5.0

    @property
    def pcb_y_back(self) -> float:
        return self.pcb_y_front - self.pcb_thick  # -8.48

    @property
    def y_usbc(self) -> float:
        return self.pcb_y_front + self.usbc_z_offset_from_pcb_top  # -5.00

    @property
    def z_pcb_bot_edge(self) -> float:
        return self.pcb_z_j1_mouth + self.usbc_j1_overhang_mm  # 11.76

    @property
    def z_pcb_center(self) -> float:
        return self.z_pcb_bot_edge + 0.5 * self.pcb_l  # 34.76

    @property
    def z_pcb_top_edge(self) -> float:
        return self.z_pcb_bot_edge + self.pcb_l  # 57.76

    @property
    def z_cap_bot_cavity_taper_start(self) -> float:
        return self.z_lid_bot_end + self.cap_bot_cavity_full_h  # 48.0

    @property
    def z_cap_bot_bulkhead_start(self) -> float:
        return self.z_cap_bot_cavity_taper_start + self.cap_bot_taper_h  # 79.5

    @property
    def z_glass_bot(self) -> float:
        return self.z_cap_bot_bulkhead_start + self.bulkhead_thick  # 85.5

    @property
    def z_core_bot(self) -> float:
        return self.z_glass_bot  # 85.5

    @property
    def z_cap_bot_top(self) -> float:
        return self.z_glass_bot + self.glass_socket_depth  # 97.5

    @property
    def z_glass_top(self) -> float:
        return self.z_glass_bot + self.glass_length  # 235.5

    @property
    def z_cap_top_bot(self) -> float:
        return self.z_glass_top - self.glass_socket_depth  # 223.5

    @property
    def z_cap_top_top(self) -> float:
        return self.z_glass_top + self.cap_top_flange_thick  # 250.0

    @property
    def z_core_top(self) -> float:
        return self.z_core_bot + self.core_length  # 335.5

    @property
    def core_protrusion_mm(self) -> float:
        return self.z_core_top - self.z_cap_top_top  # 85.5

    @property
    def z_hang_hole(self) -> float:
        return self.z_core_top - self.core_hang_hole_from_top  # 317.5

    @property
    def z_plug_top_end(self) -> float:
        return self.z_core_top + self.plug_top_cap_h  # 339.5

    @property
    def total_height_mm(self) -> float:
        return self.z_plug_top_end - self.z_base_ring_bot  # 357.5

    @property
    def exposed_glass_window(self) -> float:
        return self.z_cap_top_bot - self.z_cap_bot_top  # 126.0

    @property
    def z_optical_center(self) -> float:
        return 0.5 * (self.z_glass_bot + self.z_glass_top)  # 160.5

    @property
    def z_led_uv(self) -> float:
        return self.z_optical_center + self.star_uv_z_offset  # 178.5

    @property
    def z_led_vis(self) -> float:
        return self.z_optical_center + self.star_vis_z_offset  # 142.5

    @property
    def axial_uv_to_top_mm(self) -> float:
        return self.z_cap_top_top - self.z_led_uv  # 71.5

    @property
    def axial_uv_to_vis_mm(self) -> float:
        return self.z_led_uv - self.z_led_vis  # 36.0

    @property
    def axial_vis_to_bot_mm(self) -> float:
        return self.z_led_vis - self.z_core_bot  # 57.0

    @property
    def bot_oring_roof_z_max(self) -> float:
        half_w = 0.5 * (self.bot_oring_r_out - self.bot_oring_r_in)
        return self.z_lid_bot_end + self.bot_oring_flat_h + half_w  # 7.05

    def verify_all(self) -> dict[str, dict[str, float | bool]]:
        checks: dict[str, dict[str, float | bool]] = {}

        # 1. Vertical PCB & Card-Guide Rail radial & cone clearances inside Ø61 mm cavity
        r_cav = self.cap_bot_cavity_dia / 2.0
        pcb_corner_r = math.hypot(self.pcb_w / 2.0, abs(self.pcb_y_back))
        rail_outer_x = self.pcb_w / 2.0 + 0.2 + self.pcb_rail_wall
        rail_outer_y = abs(self.pcb_y_back) + 0.2 + self.pcb_rail_wall
        rail_outer_r = math.hypot(rail_outer_x, rail_outer_y)
        cone_slope = self.cap_bot_taper_h / r_cav
        z_cone_at_pcb_top = self.z_cap_bot_cavity_taper_start + cone_slope * (r_cav - pcb_corner_r)
        pcb_top_cone_clr = z_cone_at_pcb_top - self.z_pcb_top_edge
        # Mated J2/J3 at X = ±8.9, Y = pcb_y_front + 9.8, Z_top = z_pcb_center + 19.2 + 2.9
        r_jst_top = math.hypot(5.2 + 3.7, self.pcb_y_front + self.pcb_jst_mated_h)
        z_jst_top = self.z_pcb_center + 19.2 + 2.9
        z_cone_at_jst = self.z_cap_bot_cavity_taper_start + cone_slope * (r_cav - r_jst_top)
        jst_cone_clr = z_cone_at_jst - z_jst_top
        cone_overhang_deg = math.degrees(math.atan2(r_cav, self.cap_bot_taper_h))
        checks["pcb_radial_clearance_mm"] = {"value": round(r_cav - pcb_corner_r, 3), "min": 5.0, "pass": (r_cav - pcb_corner_r) >= 5.0}
        checks["pcb_rail_radial_clearance_mm"] = {"value": round(r_cav - rail_outer_r, 3), "min": 3.0, "pass": (r_cav - rail_outer_r) >= 3.0}
        checks["pcb_top_to_cone_clearance_mm"] = {"value": round(pcb_top_cone_clr, 3), "min": 0.5, "max": 3.0, "pass": 0.5 <= pcb_top_cone_clr <= 3.0}
        checks["pcb_jst_cone_headroom_mm"] = {"value": round(jst_cone_clr, 3), "min": 5.0, "pass": jst_cone_clr >= 5.0}
        checks["cavity_cone_overhang_deg"] = {"value": round(cone_overhang_deg, 2), "max": 45.0, "pass": cone_overhang_deg <= 45.0}

        # 2. Bulkhead thermal isolation thickness
        checks["bulkhead_thickness_mm"] = {"value": self.bulkhead_thick, "min": 5.0, "pass": self.bulkhead_thick >= 5.0}

        # 3. Bottom-entry USB-C direct-mate & Ø20.2 x 2.5 mm grommet clearances on MECH-LID-BOT
        z_plug_tip = self.pcb_z_j1_mouth + self.usbc_mating_depth_mm
        z_overmold_top = z_plug_tip - self.usbc_specified_barrel_mm
        usbc_barrel_exposed_mm = abs(self.pcb_z_j1_mouth - z_overmold_top)
        overmold_above_lid_mm = z_overmold_top - self.z_lid_bot_end
        grommet_to_g3_r = self.bot_oring_r_in - (abs(self.y_usbc) + self.grommet_back_relief_dia / 2.0)
        grommet_to_sw1_web = (self.sw1_y - self.sw1_body_w_y / 2.0) - (self.y_usbc + self.grommet_back_relief_dia / 2.0)
        grommet_lip_to_sw1_boot = (self.sw1_y - self.sw1_boot_od / 2.0) - (self.y_usbc + 12.2)
        checks["grommet_panel_thick_mm"] = {"value": self.grommet_panel_thick, "min": 2.0, "max": 3.2, "pass": 2.0 <= self.grommet_panel_thick <= 3.2}
        checks["usbc_direct_mate_barrel_mm"] = {"value": round(usbc_barrel_exposed_mm, 3), "min": 1.0, "max": 3.0, "pass": 1.0 <= usbc_barrel_exposed_mm <= 3.0}
        checks["usbc_overmold_above_lid_mm"] = {"value": round(overmold_above_lid_mm, 3), "min": 1.0, "pass": overmold_above_lid_mm >= 1.0}
        checks["grommet_to_gasket3_wall_mm"] = {"value": round(grommet_to_g3_r, 3), "min": 5.0, "pass": grommet_to_g3_r >= 5.0}
        checks["grommet_to_sw1_lid_web_mm"] = {"value": round(grommet_to_sw1_web, 3), "min": 3.0, "pass": grommet_to_sw1_web >= 3.0}
        checks["grommet_lip_to_sw1_boot_mm"] = {"value": round(grommet_lip_to_sw1_boot, 3), "min": 2.0, "pass": grommet_lip_to_sw1_boot >= 2.0}

        # 4. Bottom-mounted SW1 & MECH-BASE-RING stand guard clearances
        sw1_to_j4_y = (self.sw1_y - self.sw1_body_w_y / 2.0) - (self.pcb_y_front + self.pcb_jst_mated_h)
        sw1_corner_r = math.hypot(self.sw1_body_w_x / 2.0, self.sw1_y + self.sw1_body_w_y / 2.0)
        sw1_boot_ground_clr = self.base_ring_h - self.sw1_boot_protrude_z
        sw1_boot_to_ring_r = (self.base_ring_id / 2.0) - (self.sw1_y + self.sw1_boot_od / 2.0)
        base_ring_inner_wall = (self.lid_bot_bolt_r - self.base_ring_cb_dia / 2.0) - (self.base_ring_id / 2.0)
        base_ring_outer_wall = (self.base_ring_od / 2.0) - (self.lid_bot_bolt_r + self.base_ring_cb_dia / 2.0)
        checks["sw1_panel_thick_mm"] = {"value": self.sw1_wall_thick, "min": 2.0, "max": 3.5, "pass": 2.0 <= self.sw1_wall_thick <= 3.5}
        checks["sw1_clear_of_j4_mated_mm"] = {"value": round(sw1_to_j4_y, 3), "min": 5.0, "pass": sw1_to_j4_y >= 5.0}
        checks["sw1_radial_in_cavity_mm"] = {"value": round(r_cav - sw1_corner_r, 3), "min": 5.0, "pass": (r_cav - sw1_corner_r) >= 5.0}
        checks["sw1_boot_above_ground_mm"] = {"value": round(sw1_boot_ground_clr, 3), "min": 3.0, "pass": sw1_boot_ground_clr >= 3.0}
        checks["sw1_boot_radial_access_mm"] = {"value": round(sw1_boot_to_ring_r, 3), "min": 10.0, "pass": sw1_boot_to_ring_r >= 10.0}
        checks["base_ring_cb_inner_wall_mm"] = {"value": round(base_ring_inner_wall, 3), "min": self.min_wall, "pass": base_ring_inner_wall >= self.min_wall}
        checks["base_ring_cb_outer_wall_mm"] = {"value": round(base_ring_outer_wall, 3), "min": self.min_wall, "pass": base_ring_outer_wall >= self.min_wall}

        # 5. Radial clearances inside worst-case UVT PMMA shroud (ID_min = 68.0 mm) + star spacing
        r_glass_min = self.glass_id_min / 2.0
        r_pilot = self.glass_pilot_od / 2.0
        r_core_max_corner = math.hypot(self.core_w_max / 2.0, self.core_w_max / 2.0)
        r_led_vis_max = self.core_w_nom / 2.0 + self.star_tim_thick + self.star_thick + self.led_vis_max_h
        r_m3_head_max = self.core_w_nom / 2.0 + self.star_tim_thick + self.star_thick + self.m3_pan_plus_washer_h
        star_gap_z = (self.z_led_uv - self.star_dia / 2.0) - (self.z_led_vis + self.star_dia / 2.0)
        checks["pilot_to_shroud_id_min_mm"] = {"value": round(r_glass_min - r_pilot, 3), "min": 0.2, "pass": (r_glass_min - r_pilot) >= 0.2}
        checks["skirt_to_shroud_od_max_mm"] = {"value": round(self.glass_skirt_id_top / 2.0 - self.glass_od_max / 2.0, 3), "min": 0.2, "pass": (self.glass_skirt_id_top / 2.0 - self.glass_od_max / 2.0) >= 0.2}
        checks["core_corner_to_shroud_id_min_mm"] = {"value": round(r_glass_min - r_core_max_corner, 3), "min": 1.0, "pass": r_glass_min - r_core_max_corner >= 1.0}
        checks["led_vis_to_shroud_id_min_mm"] = {"value": round(r_glass_min - r_led_vis_max, 3), "min": 1.0, "pass": r_glass_min - r_led_vis_max >= 1.0}
        checks["m3_head_to_shroud_id_min_mm"] = {"value": round(r_glass_min - r_m3_head_max, 3), "min": 1.0, "pass": r_glass_min - r_m3_head_max >= 1.0}
        checks["uv_to_vis_star_gap_mm"] = {"value": round(star_gap_z, 3), "min": 10.0, "pass": star_gap_z >= 10.0}

        # 6. Structural wall thicknesses (>= 2.5 mm everywhere, incl. seamless cap_bot shell & captive M3 nut slots!)
        r_bolt = self.m3_clearance_dia / 2.0
        bot_cav_to_g3_wall = self.bot_oring_r_in - r_cav
        bot_g3_to_bolt_wall = (self.lid_bot_bolt_r - r_bolt) - self.bot_oring_r_out
        bot_nut_to_g3_z = (self.z_lid_bot_end + 5.0) - self.bot_oring_roof_z_max
        bot_bolt_outer_wall = (self.cap_bot_od / 2.0 - self.cap_chamfer) - (self.lid_bot_bolt_r + r_bolt)
        cap_bot_mid_wall = (self.cap_bot_mid_od / 2.0) - r_cav
        cap_bot_waist_to_slot = (self.cap_bot_waist_od / 2.0) - (self.core_pocket_w / 2.0 + self.core_wire_slot_d)
        skirt_wall = self.cap_top_od / 2.0 - self.glass_skirt_id_top / 2.0
        pilot_corner_wall = self.glass_pilot_od / 2.0 - math.hypot(self.core_pocket_w / 2.0, self.core_pocket_w / 2.0)
        z_top_lock = self.z_cap_top_top - self.cap_top_lock_z_from_top
        g2_roof_z = self.z_glass_top + self.glass_oring_depth
        top_lock_above_g2 = (z_top_lock - r_bolt) - g2_roof_z
        checks["bot_cav_to_gasket3_wall_mm"] = {"value": round(bot_cav_to_g3_wall, 3), "min": self.min_wall, "pass": bot_cav_to_g3_wall >= self.min_wall}
        checks["bot_gasket3_to_bolt_wall_mm"] = {"value": round(bot_g3_to_bolt_wall, 3), "min": self.min_wall, "pass": bot_g3_to_bolt_wall >= self.min_wall}
        checks["bot_nut_slot_above_g3_mm"] = {"value": round(bot_nut_to_g3_z, 3), "min": self.min_wall, "pass": bot_nut_to_g3_z >= self.min_wall}
        checks["bot_bolt_to_chamfer_wall_mm"] = {"value": round(bot_bolt_outer_wall, 3), "min": self.min_wall, "pass": bot_bolt_outer_wall >= self.min_wall}
        checks["cap_bot_mid_shell_wall_mm"] = {"value": round(cap_bot_mid_wall, 3), "min": 4.0, "pass": cap_bot_mid_wall >= 4.0}
        checks["cap_bot_waist_to_slot_wall_mm"] = {"value": round(cap_bot_waist_to_slot, 3), "min": 4.0, "pass": cap_bot_waist_to_slot >= 4.0}
        checks["shroud_skirt_min_wall_mm"] = {"value": round(skirt_wall, 3), "min": self.min_wall, "pass": skirt_wall >= self.min_wall}
        checks["pilot_corner_min_wall_mm"] = {"value": round(pilot_corner_wall, 3), "min": self.min_wall, "pass": pilot_corner_wall >= self.min_wall}
        checks["top_lock_above_gasket2_mm"] = {"value": round(top_lock_above_g2, 3), "min": self.min_wall, "pass": top_lock_above_g2 >= self.min_wall}

        # 7. Protruding core, top rain plug & integral drip-brim clearances
        hang_to_plug_clr = (self.z_core_top - self.plug_top_insert_h) - (self.z_hang_hole + self.core_hang_hole_dia / 2.0)
        brim_overhang_cap = 0.5 * (self.cap_top_brim_od - self.cap_bot_od)
        checks["core_protrusion_mm"] = {"value": round(self.core_protrusion_mm, 3), "min": 60.0, "max": 100.0, "pass": 60.0 <= self.core_protrusion_mm <= 100.0}
        checks["hang_hole_to_top_plug_mm"] = {"value": round(hang_to_plug_clr, 3), "min": 3.0, "pass": hang_to_plug_clr >= 3.0}
        checks["cap_top_brim_overhang_mm"] = {"value": round(brim_overhang_cap, 3), "min": 10.0, "pass": brim_overhang_cap >= 10.0}

        # 8. Shroud length tolerance O-ring squeeze & gland fill (149.0 .. 151.0 mm)
        squeeze_nom = (self.glass_oring_cs - self.glass_oring_depth) / self.glass_oring_cs
        squeeze_min = (self.glass_oring_cs - (self.glass_oring_depth + 0.5 * self.glass_length_tol)) / self.glass_oring_cs
        squeeze_max = (self.glass_oring_cs - (self.glass_oring_depth - 0.5 * self.glass_length_tol)) / self.glass_oring_cs
        groove_w = 0.5 * (self.glass_oring_od - self.glass_oring_id)
        oring_area = math.pi * (0.5 * self.glass_oring_cs) ** 2
        gland_h_at_151 = self.glass_oring_depth - 0.5 * self.glass_length_tol
        gland_fill_at_151 = oring_area / (groove_w * gland_h_at_151)
        checks["shroud_oring_squeeze_min_pct"] = {"value": round(100.0 * squeeze_min, 1), "min": 10.0, "pass": squeeze_min >= 0.10}
        checks["shroud_oring_squeeze_nom_pct"] = {"value": round(100.0 * squeeze_nom, 1), "min": 20.0, "max": 35.0, "pass": 0.20 <= squeeze_nom <= 0.35}
        checks["shroud_oring_squeeze_max_pct"] = {"value": round(100.0 * squeeze_max, 1), "max": 45.0, "pass": squeeze_max <= 0.45}
        checks["gland_fill_at_151"] = {"value": round(gland_fill_at_151, 4), "max": 0.92, "pass": gland_fill_at_151 <= 0.92}

        return checks

    def to_dict(self) -> dict:
        d = asdict(self)
        d["derived"] = {
            "z_base_ring_bot": self.z_base_ring_bot,
            "z_lid_bot_end": self.z_lid_bot_end,
            "pcb_y_back": self.pcb_y_back,
            "y_usbc": self.y_usbc,
            "z_pcb_bot_edge": self.z_pcb_bot_edge,
            "z_pcb_center": self.z_pcb_center,
            "z_pcb_top_edge": self.z_pcb_top_edge,
            "z_cap_bot_cavity_taper_start": self.z_cap_bot_cavity_taper_start,
            "z_cap_bot_bulkhead_start": self.z_cap_bot_bulkhead_start,
            "z_glass_bot": self.z_glass_bot,
            "z_core_bot": self.z_core_bot,
            "z_cap_bot_top": self.z_cap_bot_top,
            "z_glass_top": self.z_glass_top,
            "z_cap_top_bot": self.z_cap_top_bot,
            "z_cap_top_top": self.z_cap_top_top,
            "z_core_top": self.z_core_top,
            "core_protrusion_mm": self.core_protrusion_mm,
            "z_hang_hole": self.z_hang_hole,
            "z_plug_top_end": self.z_plug_top_end,
            "total_height_mm": self.total_height_mm,
            "exposed_glass_window_mm": self.exposed_glass_window,
            "z_optical_center": self.z_optical_center,
            "z_led_uv": self.z_led_uv,
            "z_led_vis": self.z_led_vis,
            "axial_uv_to_top_mm": self.axial_uv_to_top_mm,
            "axial_uv_to_vis_mm": self.axial_uv_to_vis_mm,
            "axial_vis_to_bot_mm": self.axial_vis_to_bot_mm,
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
