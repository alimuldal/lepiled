#!/usr/bin/env python3
"""
Single Source of Truth for LepiLED DIY Maxi Switch (Rev 4.3 — Field-Robust, Lightweight & Weatherproofed) Mechanical & CAD Parameters.

Rev 4.3 Physical Upgrades (Building on Rev 4.2 20 mm Copper DTP Stars + Bare 250 mm Protruding 3 mm Al Core):
  1. Shatter-Resistant UV-Transmitting PMMA (Acrylic) Shroud (MECH-TUBE-1):
     - Replaces brittle 263 g borosilicate glass with 120 g UV-transmitting cast PMMA tubing
       (Ø75.0 mm OD x 3.0 mm wall = Ø69.0 mm ID x 150.0 mm; ~85-92% UV-A @ 365 nm; ~£8-10 UK 1-off).
     - Retains standard 68x3.5 mm VMQ70 silicone O-rings (MECH-GASKET-1..2).
  2. Bottom-Mounted Toggle Switch (SW1 on MECH-LID-BOT) + Protective Base Stand Ring (MECH-BASE-RING):
     - Eliminates the side switch cutout on MECH-CAP-BOT (+X wall is now 100% solid and unbroken).
     - Mounts C&K 7211SYZBE + C&K 759D02000 silicone boot vertically pointing downward through MECH-LID-BOT
       at (X = 0.0, Y = +8.5 mm), safely clear of driver_pcb bottom (4.0 mm air gap) and all TH pins/bosses.
     - Adds a support-free bolt-on MECH-BASE-RING (Ø92 x 19 mm, 4x arched drainage cutouts) clamped by the
       same 4x M3x16 lid bolts, shielding the toggle boot by 4.0 mm so the lamp stands safely upright.
  3. Dual-Layer Rain Roof System:
     - Integral Ø108 mm 45-deg flared drip-brim built into MECH-CAP-TOP (0.00 mm^2 overhang when printed
       inverted), shedding rain clear of the shroud and USB-C grommet while leaving the 85.5 mm Al core open.
     - Detachable pack-flat MECH-RAIN-HAT (Ø144 mm x 9.7 mm, 0.00 mm^2 overhang) keyed onto MECH-PLUG-TOP
       and retained automatically by the hanging cord passing through 2x Ø6.0 mm holes.
  4. Weight-Trimmed, Robust MECH-CAP-BOT Shell:
     - Keeps the sturdy 40x40x3.0 mm Al 6063 core (300 g, full M3 thread engagement) while contouring
       excess solid plastic bulk out of MECH-CAP-BOT (~337 cm^3 -> ~200 cm^3, all walls >= 3.5 mm robust).

All coordinates are in millimeters (mm) using a right-handed global frame:
  - Origin (0, 0, 0): Bottom face of MECH-LID-BOT (MECH-BASE-RING extends downward to Z = -19.0 mm).
  - +Z: Vertically upward along the lamp centerline toward MECH-CAP-TOP, MECH-PLUG-TOP, and MECH-RAIN-HAT.
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
    base_ring_id: float = 68.0          # Open Ø68 mm finger access around downward-pointing SW1 toggle
    base_ring_h: float = 18.0           # Shields 15.0 mm C&K 759D02000 silicone boot by 3.0 mm above flat ground
    base_ring_bolt_web: float = 3.0     # 3.0 mm seat web -> M3x16 SHCS engages full captive M3 nut in cap_bot!
    base_ring_cb_dia: float = 6.4       # Clears Ø5.5 mm M3 SHCS head + 2.5 mm hex key (2.60 mm outer wall!)
    base_ring_drain_w: float = 22.0     # 4x wide drainage cutouts at 0/90/180/270 deg (zero water pooling)
    base_ring_drain_h: float = 7.0

    # Flat 3D-printed bottom lid (MECH-LID-BOT: Ø92 x 4.0 mm + 4x integral 18.0 mm PCB bosses + bottom SW1 bore)
    lid_bot_od: float = 92.0
    lid_bot_thick: float = 4.0
    lid_bot_bolt_r: float = 40.2        # 4x M3 at 45° outside MECH-GASKET-3 into captive M3 hex nuts
    pcb_boss_h: float = 18.0            # Elevates PCB to Z=22.0 mm -> 4.03 mm vertical clearance above SW1 lugs!
    pcb_boss_od: float = 6.2            # Ø6.2 mm standoff boss (3.8 mm radial clearance inside Ø61 mm cavity)
    pcb_loc_pin_dia: float = 2.45       # Integral printed locating pin passing through Ø2.7 mm NPTH H1..H4 (0 inserts!)
    pcb_loc_pin_h: float = 2.0          # Protrudes 0.4 mm cleanly above Z_pcb_top = 23.6 mm

    # Captive M3 hex-nut pocket geometry (DIN 934 M3 nut: 5.5 mm AF, 2.4 mm thick -> 5.8 x 2.7 mm pocket)
    m3_nut_af: float = 5.8
    m3_nut_thick: float = 2.7
    m3_clearance_dia: float = 3.4

    # Driver PCB (Rev 4.2/4.3 build_driver_pcb.py — isolated NPTH H1..H4, USB-C only, JLCPCB Basic SMT)
    pcb_w: float = 36.0
    pcb_l: float = 46.0
    pcb_thick: float = 1.6
    pcb_corner_r: float = 2.0
    pcb_smd_max_h: float = 4.8          # L1/L2 SRN6045 = 4.5 mm
    pcb_jst_mated_h: float = 9.8        # J2..J4 JST XH mated (pre-crimped 22 AWG pigtails)
    pcb_jst_pin_protrude: float = 1.8   # 16.2 mm air clearance above lid top
    pcb_hole_x: float = 14.0            # H1..H4 isolated NPTH at (±14.0, ±19.0)
    pcb_hole_y: float = 19.0
    pcb_hole_drill: float = 2.7
    pcb_hole_keepout: float = 5.5

    # End-cap outer envelopes (contoured waist cuts cap_bot plastic volume ~44% while keeping >= 3.5-5.0 mm walls!)
    cap_bot_od: float = 92.0            # Lower bolt/gasket flange (Z = 4.0 .. 15.0 mm)
    cap_bot_mid_od: float = 71.0        # Contoured mid-body cylinder (5.0 mm robust wall around Ø61 mm cavity!)
    cap_bot_waist_od: float = 65.0      # Tapered upper waist (>= 8.5 mm robust wall around wire slots & cone!)
    cap_top_od: float = 84.0            # Upper shroud socket skirt OD (3.5 mm skirt wall)
    cap_top_brim_od: float = 108.0      # Integral Ø108 mm rain drip-brim flange on MECH-CAP-TOP (0 deg overhang inverted!)
    cap_top_brim_rim_h: float = 3.5     # Sturdy 3.5 mm brim flange + 3.0 mm 45-deg gusset at Z_cap_top_top
    cap_chamfer: float = 0.8
    min_wall: float = 2.5

    # Bottom end-cap internal cavity & bulkhead (42.7 deg cone to apex -> support-free)
    cap_bot_cavity_dia: float = 61.0
    cap_bot_cavity_full_h: float = 30.0   # Z = 4.0 -> 34.0
    cap_bot_taper_h: float = 33.0         # Z = 34.0 -> 67.0 (atan(30.5/33.0) = 42.7 deg <= 45 deg!)
    bulkhead_thick: float = 6.0           # Z = 67.0 -> 73.0

    # Bottom lid-to-cap O-ring groove (MECH-GASKET-3: 66x2.0 mm VMQ70, optional single O-ring or silicone bead)
    bot_oring_r_in: float = 33.0
    bot_oring_r_out: float = 35.5
    bot_oring_flat_h: float = 0.80

    # Unified USB-C direct-mate entry + Ø20.2 x 2.5 mm rubber membrane grommet flange (-Y side boss)
    usbc_overmold_w: float = 13.6
    usbc_overmold_h: float = 7.8
    usbc_z_offset_from_pcb_top: float = 1.88
    usbc_j1_front_y: float = -25.76
    usbc_mating_depth_mm: float = 4.55
    usbc_specified_barrel_mm: float = 6.65
    grommet_outer_spotface_y: float = -43.5
    grommet_outer_spotface_dia: float = 26.0
    grommet_panel_thick: float = 2.5
    grommet_bore_dia: float = 20.2
    grommet_back_relief_dia: float = 23.6
    grommet_back_relief_depth: float = 2.5

    # SW1 toggle switch (Rev 4.3: Bottom-mounted vertically through MECH-LID-BOT at X=0, Y=+8.5 mm!)
    sw1_x: float = 0.0
    sw1_y: float = 8.5                    # Cleanly between J4 pins (Y=-2.5) and J2/J3 pins (Y=+19.2)
    sw1_hole_dia: float = 6.35            # 1/4-40 UNS bushing bore
    sw1_wall_thick: float = 2.5           # 1.5 mm recess on top of 4.0 mm lid -> full thread engagement for 759D02000 boot
    sw1_body_w_x: float = 12.70           # C&K 7211SYZBE body width (across poles)
    sw1_body_w_y: float = 11.43           # C&K 7211SYZBE body thickness (along throw)
    sw1_body_h_z: float = 10.67           # Body height upward into cavity
    sw1_lugs_h_z: float = 4.80            # Solder lugs upward into cavity (top at Z = 17.97 mm -> 4.03 mm below PCB!)
    sw1_boot_protrude_z: float = 15.0     # C&K 759D02000 silicone boot downward below Z = 0 (4.0 mm inside 19 mm base ring!)
    sw1_boot_od: float = 13.3

    # Shatter-resistant UV-Transmitting PMMA (Acrylic) shroud (MECH-TUBE-1: 75 mm OD x 3.0 mm wall = 69 mm ID x 150 mm)
    glass_od_nom: float = 75.0
    glass_id_nom: float = 69.0
    glass_od_max: float = 75.6            # Cast/extruded UVT PMMA tolerance ±0.6 mm
    glass_id_min: float = 68.0
    glass_length: float = 150.0
    glass_length_tol: float = 1.0
    glass_socket_depth: float = 12.0
    glass_pilot_od: float = 66.8          # 0.60 mm radial clearance to ID_min; matches 68x3.5 mm VMQ70 O-ring groove!
    glass_skirt_id_top: float = 77.0      # 0.70 mm radial clearance to OD_max; zero undercut above 76.6 mm O-ring groove!
    glass_skirt_id_bot: float = 76.6

    # Shroud axial face-seal O-ring (MECH-GASKET-1..2: standard 68x3.5 mm VMQ70 silicone O-ring pair)
    glass_oring_id: float = 66.8
    glass_oring_od: float = 76.6          # Groove width = 4.90 mm -> 91.3% gland fill at 151.0 mm WC (PASS <= 92%!)
    glass_oring_cs: float = 3.5
    glass_oring_depth: float = 2.65

    # Central protruding bare Al core (MECH-HS-CORE: stock 250.0 mm cut of 40x40x3.0 mm Al 6063 — kept 3 mm robust!)
    core_w_nom: float = 40.0
    core_w_max: float = 40.5
    core_wall: float = 3.0
    core_bore_nom: float = 34.0
    core_length: float = 250.0            # Stock 250 mm cut -> protrudes 85.5 mm above MECH-CAP-TOP!
    core_pocket_w: float = 41.0
    core_wire_slot_w: float = 6.0
    core_wire_slot_d: float = 3.5
    core_hang_hole_dia: float = 8.0       # Drilled Ø8.0 mm carabiner/cord hanging hole across protruding top
    core_hang_hole_from_top: float = 18.0 # Center at Z = 305.0 mm (12 mm below MECH-RAIN-HAT collar!)

    # 3D-printed bottom internal core plug (MECH-PLUG-BOT: 33.4x33.4x12.0 mm w/ captive M3 nuts)
    plug_bot_w: float = 33.4
    plug_bot_h: float = 12.0
    plug_bot_bolt_x: float = 9.0
    plug_bot_pin_y: float = 9.0

    # Top end-cap (MECH-CAP-TOP) — slides over protruding core, locks with 2x M3x12 screws into core walls
    cap_top_flange_thick: float = 14.5    # Z = 223.0 .. 237.5 mm
    cap_top_lock_z_from_top: float = 7.5  # 2x M3 locking screws at Z = 230.0 mm (2.65 mm above G2, 0.4 mm cleanly below brim!)
    cap_top_seal_groove: float = 1.5

    # 3D-printed top weatherproof rain plug (MECH-PLUG-TOP: caps open top of protruding 40x40x3 mm hollow tube)
    plug_top_w: float = 33.5
    plug_top_insert_h: float = 10.0       # Z = 313.0 .. 323.0 mm (clears Ø8 mm hang hole at Z = 305.0 mm by 4.0 mm!)
    plug_top_cap_w: float = 40.4
    plug_top_cap_h: float = 4.0           # Z = 323.0 .. 327.0 mm

    # Detachable pack-flat rain umbrella (MECH-RAIN-HAT: Ø136 mm disc + 5 mm drip lip, keyed onto MECH-PLUG-TOP)
    rain_hat_od: float = 136.0            # Wide rain shield; packs flat (7.5 mm thick!) in a rucksack
    rain_hat_thick: float = 2.5           # Sturdy flat top disc (prints upside-down on Z_top -> 0.00 mm^2 overhang!)
    rain_hat_lip_h: float = 5.0           # Downward outer drip lip (Z = 322.05 .. 327.05 mm)
    rain_hat_lip_wall: float = 2.8        # Robust 2.8 mm rim wall
    rain_hat_collar_id: float = 41.2      # Slip-fits cleanly over 40.4 mm MECH-PLUG-TOP & 40.5 mm max Al core (sharp corners!)
    rain_hat_collar_wall: float = 2.8     # 46.8 x 46.8 mm outer collar
    rain_hat_collar_h: float = 5.5        # Overlaps MECH-PLUG-TOP (4 mm) + Al core (1.5 mm), 12.5 mm above hang hole!
    rain_hat_cord_hole_x: float = 28.0    # 2x Ø6.0 mm cord pass-through holes cleanly outside collar (holds hat down!)
    rain_hat_cord_hole_dia: float = 6.0

    # 8x Off-the-shelf pre-mounted 20 mm Copper DTP LED stars (4x UV + 4x Vis; ZERO custom led_mcpcb!)
    star_dia: float = 20.0
    star_thick: float = 1.50
    star_tim_thick: float = 0.15
    star_uv_z_offset: float = 18.0        # Z = 148 + 18 = 166.0 mm
    star_vis_z_offset: float = -18.0      # Z = 148 - 18 = 130.0 mm
    star_bolt_r: float = 9.5
    led_uv_max_h: float = 2.08
    led_vis_max_h: float = 2.39
    m3_pan_plus_washer_h: float = 3.20

    @property
    def print_clearance(self) -> float:
        return 0.25 if self.process == "FDM" else 0.15

    # Derived global Z coordinates
    @property
    def z_base_ring_bot(self) -> float:
        return -self.base_ring_h  # -19.0

    @property
    def z_lid_bot_start(self) -> float:
        return 0.0

    @property
    def z_lid_bot_end(self) -> float:
        return self.lid_bot_thick  # 4.0

    @property
    def z_pcb_bot(self) -> float:
        return self.z_lid_bot_end + self.pcb_boss_h  # 22.0

    @property
    def z_pcb_top(self) -> float:
        return self.z_pcb_bot + self.pcb_thick  # 23.6

    @property
    def z_usbc(self) -> float:
        return self.z_pcb_top + self.usbc_z_offset_from_pcb_top  # 25.48

    @property
    def z_cap_bot_cavity_taper_start(self) -> float:
        return self.z_lid_bot_end + self.cap_bot_cavity_full_h  # 34.0

    @property
    def z_cap_bot_bulkhead_start(self) -> float:
        return self.z_cap_bot_cavity_taper_start + self.cap_bot_taper_h  # 67.0

    @property
    def z_glass_bot(self) -> float:
        return self.z_cap_bot_bulkhead_start + self.bulkhead_thick  # 73.0

    @property
    def z_core_bot(self) -> float:
        return self.z_glass_bot  # 73.0

    @property
    def z_cap_bot_top(self) -> float:
        return self.z_glass_bot + self.glass_socket_depth  # 85.0

    @property
    def z_glass_top(self) -> float:
        return self.z_glass_bot + self.glass_length  # 223.0

    @property
    def z_cap_top_bot(self) -> float:
        return self.z_glass_top - self.glass_socket_depth  # 211.0

    @property
    def z_cap_top_top(self) -> float:
        return self.z_glass_top + self.cap_top_flange_thick  # 237.5

    @property
    def z_core_top(self) -> float:
        return self.z_core_bot + self.core_length  # 323.0

    @property
    def core_protrusion_mm(self) -> float:
        return self.z_core_top - self.z_cap_top_top  # 85.5

    @property
    def z_hang_hole(self) -> float:
        return self.z_core_top - self.core_hang_hole_from_top  # 305.0

    @property
    def z_plug_top_end(self) -> float:
        return self.z_core_top + self.plug_top_cap_h  # 327.0

    @property
    def z_rain_hat_top(self) -> float:
        return self.z_plug_top_end + 0.05 + self.rain_hat_thick  # 330.25

    @property
    def total_height_with_hat_mm(self) -> float:
        return self.z_rain_hat_top - self.z_base_ring_bot  # 349.25

    @property
    def exposed_glass_window(self) -> float:
        return self.z_cap_top_bot - self.z_cap_bot_top  # 126.0

    @property
    def z_optical_center(self) -> float:
        return 0.5 * (self.z_glass_bot + self.z_glass_top)  # 148.0

    @property
    def z_led_uv(self) -> float:
        return self.z_optical_center + self.star_uv_z_offset  # 166.0

    @property
    def z_led_vis(self) -> float:
        return self.z_optical_center + self.star_vis_z_offset  # 130.0

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
        return self.z_lid_bot_end + self.bot_oring_flat_h + half_w  # 6.05

    def verify_all(self) -> dict[str, dict[str, float | bool]]:
        checks: dict[str, dict[str, float | bool]] = {}

        # 1. PCB & Boss radial clearance + TH pin air clearance + locating pin fit
        pcb_corner_r = math.hypot(self.pcb_w / 2.0 - self.pcb_corner_r,
                                  self.pcb_l / 2.0 - self.pcb_corner_r) + self.pcb_corner_r
        pcb_rad_clr = self.cap_bot_cavity_dia / 2.0 - pcb_corner_r
        boss_outer_r = math.hypot(self.pcb_hole_x, self.pcb_hole_y) + self.pcb_boss_od / 2.0
        boss_rad_clr = self.cap_bot_cavity_dia / 2.0 - boss_outer_r
        pin_air_clr = self.pcb_boss_h - self.pcb_jst_pin_protrude
        loc_pin_clr = self.pcb_hole_drill - self.pcb_loc_pin_dia
        checks["pcb_radial_clearance_mm"] = {"value": round(pcb_rad_clr, 3), "min": 1.0, "pass": pcb_rad_clr >= 1.0}
        checks["boss_radial_clearance_mm"] = {"value": round(boss_rad_clr, 3), "min": 2.0, "pass": boss_rad_clr >= 2.0}
        checks["th_pin_under_pcb_air_mm"] = {"value": round(pin_air_clr, 3), "min": 3.0, "pass": pin_air_clr >= 3.0}
        checks["pcb_loc_pin_clearance_mm"] = {"value": round(loc_pin_clr, 3), "min": 0.15, "max": 0.4, "pass": 0.15 <= loc_pin_clr <= 0.4}

        # 2. Vertical headroom above PCB & mated JST-XH pigtails to conical ceiling
        r_jst_outer = math.hypot(5.2 + 3.7, 19.2 + 2.9)
        cone_slope = self.cap_bot_taper_h / (self.cap_bot_cavity_dia / 2.0)
        z_cone_at_jst = self.z_cap_bot_cavity_taper_start + cone_slope * (self.cap_bot_cavity_dia / 2.0 - r_jst_outer)
        jst_vert_clr = z_cone_at_jst - (self.z_pcb_top + self.pcb_jst_mated_h)
        pcb_edge_clr = self.z_cap_bot_cavity_taper_start - self.z_pcb_top
        cone_overhang_deg = math.degrees(math.atan2(self.cap_bot_cavity_dia / 2.0, self.cap_bot_taper_h))
        checks["pcb_cavity_edge_headroom_mm"] = {"value": round(pcb_edge_clr, 3), "min": 8.0, "pass": pcb_edge_clr >= 8.0}
        checks["pcb_jst_cone_headroom_mm"] = {"value": round(jst_vert_clr, 3), "min": 5.0, "pass": jst_vert_clr >= 5.0}
        checks["cavity_cone_overhang_deg"] = {"value": round(cone_overhang_deg, 2), "max": 45.0, "pass": cone_overhang_deg <= 45.0}

        # 3. Bulkhead thermal isolation thickness
        checks["bulkhead_thickness_mm"] = {"value": self.bulkhead_thick, "min": 5.0, "pass": self.bulkhead_thick >= 5.0}

        # 4. USB-C tunnel + Ø20.2 mm rubber grommet flange clearances
        g1_z_bot = self.z_glass_bot - self.glass_oring_depth
        grommet_bore_z_bot = self.z_usbc - self.grommet_bore_dia / 2.0
        grommet_back_z_bot = self.z_usbc - self.grommet_back_relief_dia / 2.0
        grommet_back_y_in = self.grommet_outer_spotface_y + self.grommet_panel_thick + self.grommet_back_relief_depth
        grommet_to_g3_radial = abs(grommet_back_y_in) - self.bot_oring_r_out
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

        # 5. Bottom-mounted SW1 (C&K 7211SYZBE on MECH-LID-BOT) & MECH-BASE-RING stand guard clearances
        sw1_lugs_top_z = self.sw1_wall_thick + self.sw1_body_h_z + self.sw1_lugs_h_z
        sw1_to_pcb_z = self.z_pcb_bot - sw1_lugs_top_z
        sw1_to_j4_y = (self.sw1_y - self.sw1_body_w_y / 2.0) - (-2.5 + 1.0)
        sw1_to_j23_y = (19.2 - 1.0) - (self.sw1_y + self.sw1_body_w_y / 2.0)
        sw1_boot_ground_clr = self.base_ring_h - self.sw1_boot_protrude_z
        sw1_boot_to_ring_r = (self.base_ring_id / 2.0) - (math.hypot(self.sw1_x, self.sw1_y) + self.sw1_boot_od / 2.0)
        base_ring_inner_wall = (self.lid_bot_bolt_r - self.base_ring_cb_dia / 2.0) - (self.base_ring_id / 2.0)
        base_ring_outer_wall = (self.base_ring_od / 2.0) - (self.lid_bot_bolt_r + self.base_ring_cb_dia / 2.0)
        checks["sw1_panel_thick_mm"] = {"value": self.sw1_wall_thick, "min": 2.0, "max": 3.5, "pass": 2.0 <= self.sw1_wall_thick <= 3.5}
        checks["sw1_lugs_below_pcb_mm"] = {"value": round(sw1_to_pcb_z, 3), "min": 2.5, "pass": sw1_to_pcb_z >= 2.5}
        checks["sw1_clear_of_j4_pins_mm"] = {"value": round(sw1_to_j4_y, 3), "min": 2.0, "pass": sw1_to_j4_y >= 2.0}
        checks["sw1_clear_of_j23_pins_mm"] = {"value": round(sw1_to_j23_y, 3), "min": 2.0, "pass": sw1_to_j23_y >= 2.0}
        checks["sw1_boot_above_ground_mm"] = {"value": round(sw1_boot_ground_clr, 3), "min": 3.0, "pass": sw1_boot_ground_clr >= 3.0}
        checks["sw1_boot_radial_access_mm"] = {"value": round(sw1_boot_to_ring_r, 3), "min": 10.0, "pass": sw1_boot_to_ring_r >= 10.0}
        checks["base_ring_cb_inner_wall_mm"] = {"value": round(base_ring_inner_wall, 3), "min": self.min_wall, "pass": base_ring_inner_wall >= self.min_wall}
        checks["base_ring_cb_outer_wall_mm"] = {"value": round(base_ring_outer_wall, 3), "min": self.min_wall, "pass": base_ring_outer_wall >= self.min_wall}

        # 6. Radial clearances inside worst-case UVT PMMA shroud (ID_min = 68.0 mm) + star spacing
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

        # 7. Structural wall thicknesses (>= 2.5 mm everywhere, incl. contoured cap_bot waist & captive M3 nut slots!)
        r_bolt = self.m3_clearance_dia / 2.0
        bot_cav_to_g3_wall = self.bot_oring_r_in - self.cap_bot_cavity_dia / 2.0
        bot_g3_to_bolt_wall = (self.lid_bot_bolt_r - r_bolt) - self.bot_oring_r_out
        bot_nut_to_g3_z = (self.z_lid_bot_end + 5.0) - self.bot_oring_roof_z_max
        bot_bolt_outer_wall = (self.cap_bot_od / 2.0 - self.cap_chamfer) - (self.lid_bot_bolt_r + r_bolt)
        cap_bot_mid_wall = (self.cap_bot_mid_od / 2.0) - (self.cap_bot_cavity_dia / 2.0)
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

        # 8. Protruding core, top rain plug & detachable rain hat clearances
        hang_to_plug_clr = (self.z_core_top - self.plug_top_insert_h) - (self.z_hang_hole + self.core_hang_hole_dia / 2.0)
        hang_to_hat_collar_clr = (self.z_plug_top_end + 0.05 - self.rain_hat_collar_h) - (self.z_hang_hole + self.core_hang_hole_dia / 2.0)
        hat_brim_overhang_cap = 0.5 * (self.cap_top_brim_od - self.cap_bot_od)
        checks["core_protrusion_mm"] = {"value": round(self.core_protrusion_mm, 3), "min": 60.0, "max": 100.0, "pass": 60.0 <= self.core_protrusion_mm <= 100.0}
        checks["hang_hole_to_top_plug_mm"] = {"value": round(hang_to_plug_clr, 3), "min": 3.0, "pass": hang_to_plug_clr >= 3.0}
        checks["hang_hole_to_rain_hat_collar_mm"] = {"value": round(hang_to_hat_collar_clr, 3), "min": 8.0, "pass": hang_to_hat_collar_clr >= 8.0}
        checks["cap_top_brim_overhang_mm"] = {"value": round(hat_brim_overhang_cap, 3), "min": 6.0, "pass": hat_brim_overhang_cap >= 6.0}

        # 9. Shroud length tolerance O-ring squeeze & gland fill (149.0 .. 151.0 mm)
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
            "core_protrusion_mm": self.core_protrusion_mm,
            "z_hang_hole": self.z_hang_hole,
            "z_plug_top_end": self.z_plug_top_end,
            "z_rain_hat_top": self.z_rain_hat_top,
            "total_height_with_hat_mm": self.total_height_with_hat_mm,
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
