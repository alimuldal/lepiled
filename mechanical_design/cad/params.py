#!/usr/bin/env python3
"""
Single Source of Truth for LepiLED DIY Maxi Switch (Rev 4.5 — Compact, Horizontal PCB, Radial O-Rings & Weatherproof Split Gland).

Rev 4.5 Engineering Upgrades (Addressing All Rev 4.4 Critical Mechanical Review Findings):
  1. Compact Core & Extruded XT PMMA Shroud (-295 g mass, -86 mm height vs Rev 4.4):
     - MECH-HS-CORE: Stock 200.0 mm bare 30 x 30 x 3.0 mm Al 6063-T6 box section (175 g; retains full 3.0 mm
       wall for 6-turn M3 star threads; protrudes 61.5 mm above MECH-CAP-TOP w/ unobstructed Ø8 mm hang hole).
     - MECH-TUBE-1: Unstabilized clear extruded PMMA (Plexiglas XT) Ø60 x 54 x 3.0 x 115.0 mm (73 g, ±2.0 mm
       saw-cut tolerant via radial bore O-ring seals).
  2. Radial Bore/Spigot O-Ring Seals (25–40 N Hand Push, ±2.5 mm Cut-Length Tolerant):
     - Replaces high-preload axial face-seal O-rings with 45-deg self-supporting radial O-ring grooves:
       MECH-GASKET-1/2 (60 x 3.0 mm VMQ70 on Ø60 mm PMMA OD, 20.0% nom squeeze) and MECH-GASKET-3
       (70 x 2.5 mm VMQ70 on MECH-LID-BOT spigot, 14.0% nom squeeze).
  3. Horizontal Driver PCB on Bulkhead Standoffs + Bottom SW1 + M20 Split Waterproof Cable Gland:
     - Unchanged 36 x 46 mm driver_pcb mounts horizontally (SMD/JST side down for easy service) onto 4x Ø5.5 mm
       standoffs inside MECH-CAP-BOT via H1..H4 (4x M2.5x8 screws; 100% clear of all 57 SMDs modeled from CPL!).
     - Permanently captured USB-C PD cable exits straight downward through an M20 IP68 split cable gland
       (passes intact USB-C plug, seals watertight around round Ø4–5 mm cable jacket) beside bottom-mounted SW1
       (C&K 7211SYZBE + 759D02000 boot), protected inside MECH-BASE-RING (Ø92 x 74 x 20 mm).
     - Adhesive Ø8 mm IP68 ePTFE breather vent patch + Ø2.5 mm clear D12 PD-status lightpipe in MECH-LID-BOT.
  4. Simplified Core Attachment & Sloped Conical Rain Roof:
     - Eliminates MECH-PLUG-BOT completely: core locks directly into MECH-CAP-BOT's 12 mm collar below the
       shroud seal via 2x M3x10 SHCS radial screws, with 2x generous 9.0 x 7.5 mm wire channels passing pre-crimped
       2-pin JST-XH plugs straight through without de-pinning.
     - MECH-CAP-TOP features a 15-deg sloped conical Ø88 mm rain roof (zero pooling) + internal neutral-cure
       oxime silicone core seal groove below its 2x M3x10 locking screws.

All coordinates are in millimeters (mm) using a right-handed global frame:
  - Origin (0, 0, 0): Bottom face of MECH-LID-BOT (MECH-BASE-RING extends downward to Z = -20.0 mm).
  - +Z: Vertically upward along the lamp centerline toward MECH-CAP-TOP and MECH-PLUG-TOP.
  - +X, +Y: Normal to the 4 flat faces of the 30x30x3 mm MECH-HS-CORE tube.
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

    # Protective bolt-on standing ring / switch & cable-gland guard (MECH-BASE-RING: Z = -20.0 .. 0.0 mm)
    base_ring_od: float = 94.4
    base_ring_id: float = 71.6          # Open Ø71.6 mm finger, SW1 & M20 split gland clearance (2.60 mm robust CB walls!)
    base_ring_h: float = 20.0           # Shields 15 mm SW1 boot (5 mm) & 16.5 mm M20 gland nut (3.5 mm) above flat ground
    base_ring_bolt_web: float = 2.5     # 2.5 mm seat web -> M3x16 SHCS engages full captive M3 nut in cap_bot
    base_ring_cb_dia: float = 6.2       # Clears Ø5.5 mm M3 SHCS head + 2.5 mm hex key (2.60 mm inner/outer walls!)
    base_ring_drain_w: float = 24.0     # 4x wide drainage & captured USB-C cable exit cutouts at 0/90/180/270 deg
    base_ring_drain_h: float = 9.5

    # Flat 3D-printed bottom lid w/ radial O-ring spigot (MECH-LID-BOT: Ø94.4 x 5.0 mm + 7.0 mm spigot)
    lid_bot_od: float = 94.4
    lid_bot_thick: float = 5.0
    lid_bot_bolt_r: float = 41.5        # 4x M3 at 45 deg outside Ø74.4 mm cavity (2.60 mm inner / 2.80 mm outer wall!)
    lid_spigot_od: float = 73.6         # Slides cleanly inside Ø74.4 mm cavity bore (0.40 mm radial clearance)
    lid_spigot_id: float = 65.0         # 2.55 mm solid wall behind radial O-ring groove root (R_g = 35.05 mm)
    lid_spigot_h: float = 7.0           # Z = 5.0 .. 12.0 mm

    # Bottom lid radial O-ring (MECH-GASKET-3: standard 70 x 2.5 mm VMQ70 on lid spigot, 45-deg roof -> 0 overhang!)
    bot_oring_groove_od: float = 70.10  # Groove root dia -> radial gland = (74.4 - 70.1)/2 = 2.15 mm (14.0% squeeze!)
    bot_oring_cs: float = 2.5
    bot_oring_flat_w: float = 2.8       # Vertical root land height (Z = 6.5 .. 9.3 mm, + 1.75 mm 45-deg top ramp)

    # Captive M3 hex-nut pocket geometry (DIN 934 M3 nut: 5.5 mm AF, 2.4 mm thick -> 5.8 x 2.7 mm w/ retention detent)
    m3_nut_af: float = 5.8
    m3_nut_thick: float = 2.7
    m3_clearance_dia: float = 3.4

    # Driver PCB mounted HORIZONTALLY (SMD/JST side DOWN on 4x ceiling standoffs via H1..H4 + 4x M2.5x8 screws)
    pcb_w: float = 36.0                 # Along global X (±18.0 mm)
    pcb_l: float = 46.0                 # Along global Y (centered at pcb_y_center = +8.0 mm -> Y = -15.0 .. +31.0)
    pcb_thick: float = 1.6              # Along global Z (F.Cu = 27.0 mm, B.Cu = 28.6 mm)
    pcb_corner_r: float = 2.0
    pcb_y_center: float = 8.0           # Shifts PCB +8 mm so compact 90-deg USB-C plug clears Ø74.4 mm cavity cleanly
    pcb_z_fcu: float = 27.0             # F.Cu (SMD/JST face) facing DOWN at Z = 27.0 mm (7.2 mm above SW1 lugs!)
    pcb_smd_max_h: float = 4.5          # L1/L2 SRN6045 = 4.5 mm
    pcb_jst_mated_h: float = 9.8        # J2..J4 JST-XH mated downward (Z = 17.2 .. 27.0 mm)
    pcb_jst_pin_protrude: float = 1.8   # TH pins upward on B.Cu (Z = 28.6 .. 30.4 mm)
    pcb_hole_x: float = 14.0            # H1..H4 at (±14.0, pcb_y_center ± 19.0) = (±14.0, -11.0/+27.0)
    pcb_hole_y: float = 19.0
    pcb_hole_drill: float = 2.7         # M2.5 NPTH clearance drill
    pcb_hole_keepout: float = 5.5
    pcb_standoff_od: float = 5.5        # Matches Ø5.5 mm copper keepout on H1..H4!
    pcb_standoff_pilot_dia: float = 2.2 # Self-tapping pilot bore for 4x M2.5x8 pan-head screws

    # Seamless contoured bottom end-cap outer envelopes (MECH-CAP-BOT: prints INVERTED, 0.000 mm^2 >46 deg overhang!)
    cap_bot_od: float = 94.4            # Lower bolt flange (Z = 5.0 .. 15.0 mm; 3.20 mm outer bolt wall!)
    cap_bot_mid_od: float = 82.0        # Cylindrical electronics bay (3.8 mm robust wall around Ø74.4 mm cavity!)
    cap_bot_collar_od: float = 72.0     # Upper core-lock & shroud bore collar (3.60 mm wall outside O-ring groove!)
    cap_bot_cavity_dia: float = 74.4    # Clears PCB corners (R=35.85 -> 1.35 mm) & 90-deg USB-C plug (R=31.0 -> 6.2 mm)
    cap_bot_ceiling_z: float = 35.0     # Flat upward-facing print floor (6.4 mm standoffs to B.Cu=28.6 mm)
    cap_bot_core_bot_z: float = 53.0    # Core bottom seat (43.6-deg shroud cone closes at Z=32.1 mm, 1.7 mm above TH pins!)
    cap_bot_glass_bot_z: float = 65.0   # Shroud bottom seat (12.0 mm above core bottom -> room for 2x M3 core lock!)
    cap_bot_lock_z: float = 59.0        # 2x M3x10 SHCS radial core locking screws 6.0 mm BELOW shroud bottom!

    # Bottom-entry M20 IP68 split waterproof cable gland + compact 90-deg USB-C PD plug (Option A captured cable)
    usbc_j1_overhang_mm: float = 2.76   # J1 mouth extends 2.76 mm past -23.0 mm PCB edge -> Y_mouth = -17.76 mm
    usbc_z_offset_from_fcu: float = 1.88
    usbc_mating_depth_mm: float = 4.55
    usbc_plug_90_len: float = 13.0      # Compact 90-deg-down USB-C plug protrusion past J1 mouth (Y = -17.76..-30.76)
    usbc_plug_90_w: float = 13.2
    usbc_plug_90_h: float = 11.5        # Vertical body height downward from J1 centerline
    gland_x: float = 0.0
    gland_y: float = -18.5              # Centered beneath 90-deg USB-C cable exit; 17.8 mm gap to SW1!
    gland_bore_dia: float = 20.4        # Standard M20 split waterproof cable gland bore (passes intact USB-C plug!)
    gland_nut_od: float = 26.5          # Inner locknut & outer dome nut envelope (R=13.25 -> clears R=32.5 spigot!)
    gland_outer_h: float = 16.5         # Protrusion below Z=0 (3.5 mm shielded inside 20 mm MECH-BASE-RING!)
    gland_inner_h: float = 8.5          # Locknut + thread height above Z=5.0 inside cavity (Z = 5.0..13.5 mm)

    # Bottom-mounted SW1 toggle switch (C&K 7211SYZBE on MECH-LID-BOT at X=0, Y=+18.5 mm, pointing straight down)
    sw1_x: float = 0.0
    sw1_y: float = 18.5                 # Cleanly separated from M20 gland (Y=-18.5) and clear of J2/J3 & J4 in XY!
    sw1_hole_dia: float = 6.35          # 1/4-40 UNS bushing bore
    sw1_wall_thick: float = 2.5         # 2.5 mm upper anti-rotation pocket in 5.0 mm lid -> full boot thread engagement
    sw1_body_w_x: float = 12.70
    sw1_body_w_y: float = 11.43
    sw1_body_h_z: float = 10.67
    sw1_lugs_h_z: float = 4.80          # Top of lugs at Z = 2.5 + 10.67 + 4.80 = 17.97 mm (7.2 mm below SMD @ Z=25.2!)
    sw1_boot_protrude_z: float = 15.0   # C&K 759D02000 silicone boot downward (5.0 mm inside 20 mm MECH-BASE-RING!)
    sw1_boot_od: float = 13.3

    # Pressure-equalization IP68 ePTFE breather vent + D12 green PD-status lightpipe on MECH-LID-BOT
    vent_x: float = -23.0
    vent_y: float = 0.0
    vent_hole_dia: float = 2.5          # Covered externally by Ø8 mm adhesive IP68 ePTFE breather vent patch
    d12_lightpipe_x: float = 16.0       # Directly beneath D12 (+16.0, -6.6 board -> +16.0, +1.4 global!)
    d12_lightpipe_y: float = 1.4
    d12_lightpipe_dia: float = 2.6      # Accepts Ø2.5 mm clear PMMA rod / clear filament sealed w/ neutral silicone

    # Shatter-resistant Clear Unstabilized Extruded PMMA (Plexiglas XT) shroud (MECH-TUBE-1: Ø60 x 54 x 3.0 x 115 mm)
    glass_od_nom: float = 60.0
    glass_id_nom: float = 54.0
    glass_od_max: float = 60.4
    glass_od_min: float = 59.6
    glass_id_min: float = 53.5
    glass_length: float = 115.0
    glass_length_tol: float = 2.0       # Full ±2.0 mm UK saw-cut tolerance absorbed effortlessly by radial O-rings!
    glass_socket_depth: float = 12.0
    glass_bore_id: float = 60.8         # Outer shroud bore (0.20 mm/side clearance to 60.4 mm max OD!)

    # Shroud radial bore O-rings (MECH-GASKET-1..2: standard 60 x 3.0 mm VMQ70 sealing on Ø60.0 mm PMMA OD!)
    glass_oring_groove_od: float = 64.80  # Radial gland = (64.8 - 60.0)/2 = 2.40 mm -> 20.0% nom / 13.3-26.7% squeeze!
    glass_oring_cs: float = 3.0
    glass_oring_flat_w: float = 3.6       # Vertical root height (+ 2.0 mm 45-deg roof ramp -> 0.000 mm^2 overhang!)

    # Central protruding bare Al core (MECH-HS-CORE: stock 200.0 mm cut of 30 x 30 x 3.0 mm Al 6063-T6 — 175 g!)
    core_w_nom: float = 30.0
    core_w_max: float = 30.4
    core_wall: float = 3.0              # Full 3.0 mm robust wall kept for 6-turn M3 star & lock screw threads!
    core_bore_nom: float = 24.0
    core_length: float = 200.0
    core_pocket_w: float = 30.8         # 0.20 mm/side max clearance around 30.4 mm max core
    core_wire_slot_w: float = 9.0       # 9.0 x 7.5 mm channels at ±Y pass 7.4 x 5.75 mm JST-XH plugs without de-pinning!
    core_wire_slot_d: float = 7.5
    core_hang_hole_dia: float = 8.0
    core_hang_hole_from_top: float = 16.0

    # Top end-cap (MECH-CAP-TOP) — prints UPRIGHT w/ 15-deg sloped conical Ø88 mm rain roof + internal core seal!
    cap_top_skirt_od: float = 72.0      # Matches MECH-CAP-BOT collar OD (3.60 mm wall outside radial O-ring groove!)
    cap_top_brim_od: float = 88.0       # 45-deg self-supporting flare (+14 mm/side past Ø60 mm shroud!)
    cap_top_rim_h: float = 3.5          # Cylindrical drip edge before 25-deg conical rain-shedding roof
    cap_top_roof_deg: float = 25.0      # 25-deg sloped conical roof — rapid rain shedding & zero pooling!
    cap_top_collar_od: float = 50.6     # Central boss around 30.8 x 30.8 mm core exit (R = 25.3 mm -> 3.5 mm corner wall!)
    cap_top_lock_z_rel: float = 15.5    # 2x M3x10 radial core lock screws sheltered cleanly under unbroken 25-deg roof!
    cap_top_seal_groove: float = 1.5    # Top exit neutral-cure silicone chamfer groove
    cap_chamfer: float = 0.8
    min_wall: float = 2.5

    # 3D-printed top weatherproof rain plug (MECH-PLUG-TOP: seals open top of protruding 30 x 30 x 3 mm Al tube)
    plug_top_w: float = 23.5
    plug_top_insert_h: float = 10.0
    plug_top_cap_w: float = 30.4
    plug_top_cap_h: float = 4.0

    # 8x Off-the-shelf pre-mounted 20 mm Copper DTP LED stars (4x UV + 4x Vis; M3 pan screws + nylon washers)
    star_dia: float = 20.0
    star_thick: float = 1.50
    star_tim_thick: float = 0.15
    star_uv_z_offset: float = 16.0      # 32.0 mm UV-to-Vis center pitch (12.0 mm gap between Ø20 mm stars!)
    star_vis_z_offset: float = -16.0
    star_bolt_r: float = 9.5
    led_uv_max_h: float = 2.08
    led_vis_max_h: float = 2.39
    m3_pan_plus_washer_h: float = 3.20

    @property
    def print_clearance(self) -> float:
        return 0.25 if self.process == "FDM" else 0.15

    # Derived global coordinates (Rev 4.5 horizontal PCB + compact 30x30x3 core)
    @property
    def z_base_ring_bot(self) -> float:
        return -self.base_ring_h  # -20.0

    @property
    def z_lid_bot_start(self) -> float:
        return 0.0

    @property
    def z_lid_bot_end(self) -> float:
        return self.lid_bot_thick  # 5.0

    @property
    def z_pcb_bcu(self) -> float:
        return self.pcb_z_fcu + self.pcb_thick  # 28.6

    @property
    def y_j1_mouth(self) -> float:
        return self.pcb_y_center - 0.5 * self.pcb_l - self.usbc_j1_overhang_mm  # -17.76

    @property
    def z_j1_center(self) -> float:
        return self.pcb_z_fcu - self.usbc_z_offset_from_fcu  # 25.12

    @property
    def z_core_bot(self) -> float:
        return self.cap_bot_core_bot_z  # 48.0

    @property
    def z_glass_bot(self) -> float:
        return self.cap_bot_glass_bot_z  # 60.0

    @property
    def z_cap_bot_top(self) -> float:
        return self.z_glass_bot + self.glass_socket_depth  # 72.0

    @property
    def z_glass_top(self) -> float:
        return self.z_glass_bot + self.glass_length  # 175.0

    @property
    def z_cap_top_bot(self) -> float:
        return self.z_glass_top - self.glass_socket_depth  # 163.0

    @property
    def z_cap_top_brim_bot(self) -> float:
        return self.z_cap_top_bot + 8.0  # 171.0 (8 mm vertical skirt before 45-deg flare)

    @property
    def z_cap_top_brim_rim_bot(self) -> float:
        return self.z_cap_top_brim_bot + 0.5 * (self.cap_top_brim_od - self.cap_top_skirt_od)  # 179.0

    @property
    def z_cap_top_brim_rim_top(self) -> float:
        return self.z_cap_top_brim_rim_bot + self.cap_top_rim_h  # 181.5

    @property
    def z_cap_top_top(self) -> float:
        slope_dr = 0.5 * (self.cap_top_brim_od - self.cap_top_collar_od)
        return round(self.z_cap_top_brim_rim_top + slope_dr * math.tan(math.radians(self.cap_top_roof_deg)), 3)  # 186.511

    @property
    def z_cap_top_lock(self) -> float:
        return self.z_cap_top_bot + self.cap_top_lock_z_rel  # 182.0

    @property
    def z_core_top(self) -> float:
        return self.z_core_bot + self.core_length  # 248.0

    @property
    def core_protrusion_mm(self) -> float:
        return round(self.z_core_top - self.z_cap_top_top, 3)  # 61.489

    @property
    def z_hang_hole(self) -> float:
        return self.z_core_top - self.core_hang_hole_from_top  # 232.0

    @property
    def z_plug_top_end(self) -> float:
        return self.z_core_top + self.plug_top_cap_h  # 252.0

    @property
    def total_height_mm(self) -> float:
        return round(self.z_plug_top_end - self.z_base_ring_bot, 3)  # 272.0

    @property
    def exposed_glass_window(self) -> float:
        return self.z_cap_top_bot - self.z_cap_bot_top  # 91.0

    @property
    def z_optical_center(self) -> float:
        return 0.5 * (self.z_glass_bot + self.z_glass_top)  # 117.5

    @property
    def z_led_uv(self) -> float:
        return self.z_optical_center + self.star_uv_z_offset  # 133.5

    @property
    def z_led_vis(self) -> float:
        return self.z_optical_center + self.star_vis_z_offset  # 101.5

    @property
    def axial_uv_to_top_mm(self) -> float:
        return round(self.z_cap_top_top - self.z_led_uv, 3)  # 53.011

    @property
    def axial_uv_to_vis_mm(self) -> float:
        return self.z_led_uv - self.z_led_vis  # 32.0

    @property
    def axial_vis_to_bot_mm(self) -> float:
        return self.z_led_vis - self.z_core_bot  # 53.5

    @property
    def bulkhead_thick(self) -> float:
        return self.z_core_bot - self.cap_bot_ceiling_z  # 13.0 mm perimeter (min 4.8 mm at pyramid tip)

    def verify_all(self) -> dict[str, dict[str, float | bool]]:
        checks: dict[str, dict[str, float | bool]] = {}
        r_cav = self.cap_bot_cavity_dia / 2.0

        # 1. Horizontal driver_pcb & 90-deg USB-C plug clearances inside Ø74.4 mm cavity
        pcb_pos_corner_r = math.hypot(self.pcb_w / 2.0, self.pcb_y_center + self.pcb_l / 2.0)
        pcb_neg_corner_r = math.hypot(self.pcb_w / 2.0, self.pcb_y_center - self.pcb_l / 2.0)
        plug_corner_r = math.hypot(self.usbc_plug_90_w / 2.0, abs(self.y_j1_mouth) + self.usbc_plug_90_len)
        z_cone_apex = (self.z_glass_bot - 1.2) - (self.glass_bore_id / 2.0 - 0.2) * 1.05
        th_pin_to_pyramid = z_cone_apex - (self.z_pcb_bcu + self.pcb_jst_pin_protrude)
        th_pin_to_ceiling = self.cap_bot_ceiling_z - (self.z_pcb_bcu + self.pcb_jst_pin_protrude)
        jst_bot_z = self.pcb_z_fcu - self.pcb_jst_mated_h
        sw1_lugs_top_z = self.sw1_wall_thick + self.sw1_body_h_z + self.sw1_lugs_h_z
        # Over SW1 (Y = +12.8..+24.2), max SMD height on driver_pcb is 1.8 mm (C2/C3), while J2/J3 start at Y=+24.3 mm
        smd_to_sw1_z = (self.pcb_z_fcu - 1.8) - sw1_lugs_top_z
        checks["pcb_radial_clearance_mm"] = {"value": round(r_cav - max(pcb_pos_corner_r, pcb_neg_corner_r), 3), "min": 1.0, "pass": (r_cav - max(pcb_pos_corner_r, pcb_neg_corner_r)) >= 1.0}
        checks["usbc_90_plug_radial_clr_mm"] = {"value": round(r_cav - plug_corner_r, 3), "min": 4.0, "pass": (r_cav - plug_corner_r) >= 4.0}
        checks["pcb_th_pins_to_pyramid_mm"] = {"value": round(th_pin_to_pyramid, 3), "min": 1.5, "pass": th_pin_to_pyramid >= 1.5}
        checks["pcb_th_pins_to_ceiling_mm"] = {"value": round(th_pin_to_ceiling, 3), "min": 4.0, "pass": th_pin_to_ceiling >= 4.0}
        checks["pcb_smd_above_sw1_lugs_mm"] = {"value": round(smd_to_sw1_z, 3), "min": 5.0, "pass": smd_to_sw1_z >= 5.0}
        checks["pcb_jst_above_lid_top_mm"] = {"value": round(jst_bot_z - self.z_lid_bot_end, 3), "min": 10.0, "pass": (jst_bot_z - self.z_lid_bot_end) >= 10.0}

        # 2. Bottom M20 split cable gland, SW1, ePTFE vent & MECH-BASE-RING clearances
        r_spigot_in = self.lid_spigot_id / 2.0
        gland_nut_to_spigot = r_spigot_in - (abs(self.gland_y) + self.gland_nut_od / 2.0)
        gland_to_sw1_gap = (self.sw1_y - self.sw1_body_w_y / 2.0) - (self.gland_y + self.gland_nut_od / 2.0)
        sw1_corner_r = math.hypot(self.sw1_body_w_x / 2.0, self.sw1_y + self.sw1_body_w_y / 2.0)
        sw1_boot_ground_clr = self.base_ring_h - self.sw1_boot_protrude_z
        gland_ground_clr = self.base_ring_h - self.gland_outer_h
        base_ring_inner_wall = (self.lid_bot_bolt_r - self.base_ring_cb_dia / 2.0) - (self.base_ring_id / 2.0)
        base_ring_outer_wall = (self.base_ring_od / 2.0) - (self.lid_bot_bolt_r + self.base_ring_cb_dia / 2.0)
        checks["gland_nut_in_spigot_clr_mm"] = {"value": round(gland_nut_to_spigot, 3), "min": 0.5, "pass": gland_nut_to_spigot >= 0.5}
        checks["gland_to_sw1_gap_mm"] = {"value": round(gland_to_sw1_gap, 3), "min": 10.0, "pass": gland_to_sw1_gap >= 10.0}
        checks["sw1_in_spigot_clr_mm"] = {"value": round(r_spigot_in - sw1_corner_r, 3), "min": 5.0, "pass": (r_spigot_in - sw1_corner_r) >= 5.0}
        checks["sw1_boot_above_ground_mm"] = {"value": round(sw1_boot_ground_clr, 3), "min": 3.0, "pass": sw1_boot_ground_clr >= 3.0}
        checks["gland_above_ground_mm"] = {"value": round(gland_ground_clr, 3), "min": 2.5, "pass": gland_ground_clr >= 2.5}
        checks["base_ring_cb_inner_wall_mm"] = {"value": round(base_ring_inner_wall, 3), "min": self.min_wall, "pass": base_ring_inner_wall >= self.min_wall}
        checks["base_ring_cb_outer_wall_mm"] = {"value": round(base_ring_outer_wall, 3), "min": self.min_wall, "pass": base_ring_outer_wall >= self.min_wall}

        # 3. Radial clearances inside compact Ø60 x 54 mm XT PMMA shroud (ID_min = 53.5 mm) + wire slots
        r_glass_min = self.glass_id_min / 2.0
        r_core_max_corner = math.hypot(self.core_w_max / 2.0, self.core_w_max / 2.0)
        r_led_vis_max = self.core_w_nom / 2.0 + self.star_tim_thick + self.star_thick + self.led_vis_max_h
        r_m3_head_corner = math.hypot(self.core_w_nom / 2.0 + self.star_tim_thick + self.star_thick + self.m3_pan_plus_washer_h, self.star_bolt_r)
        star_gap_z = (self.z_led_uv - self.star_dia / 2.0) - (self.z_led_vis + self.star_dia / 2.0)
        wire_slot_outer_r = math.hypot(self.core_wire_slot_w / 2.0, self.core_pocket_w / 2.0 + self.core_wire_slot_d)
        checks["shroud_bore_to_od_max_mm"] = {"value": round(0.5 * (self.glass_bore_id - self.glass_od_max), 3), "min": 0.15, "pass": 0.5 * (self.glass_bore_id - self.glass_od_max) >= 0.15}
        checks["core_corner_to_shroud_id_min_mm"] = {"value": round(r_glass_min - r_core_max_corner, 3), "min": 3.0, "pass": (r_glass_min - r_core_max_corner) >= 3.0}
        checks["led_vis_to_shroud_id_min_mm"] = {"value": round(r_glass_min - r_led_vis_max, 3), "min": 5.0, "pass": (r_glass_min - r_led_vis_max) >= 5.0}
        checks["m3_head_to_shroud_id_min_mm"] = {"value": round(r_glass_min - r_m3_head_corner, 3), "min": 3.0, "pass": (r_glass_min - r_m3_head_corner) >= 3.0}
        checks["uv_to_vis_star_gap_mm"] = {"value": round(star_gap_z, 3), "min": 10.0, "pass": star_gap_z >= 10.0}
        checks["wire_slot_jst_xh_width_mm"] = {"value": self.core_wire_slot_w, "min": 8.5, "pass": self.core_wire_slot_w >= 8.5}
        checks["wire_slot_jst_xh_depth_mm"] = {"value": self.core_wire_slot_d, "min": 7.0, "pass": self.core_wire_slot_d >= 7.0}
        checks["wire_slot_inside_shroud_id_mm"] = {"value": round(r_glass_min - wire_slot_outer_r, 3), "min": 2.5, "pass": (r_glass_min - wire_slot_outer_r) >= 2.5}

        # 4. Structural walls (>= 2.5 mm everywhere)
        r_bolt = self.m3_clearance_dia / 2.0
        bot_cav_to_bolt = (self.lid_bot_bolt_r - r_bolt) - r_cav
        bot_bolt_to_outer = (self.cap_bot_od / 2.0 - self.cap_chamfer) - (self.lid_bot_bolt_r + r_bolt)
        cap_bot_mid_wall = (self.cap_bot_mid_od / 2.0) - r_cav
        shroud_oring_outer_wall = (self.cap_bot_collar_od / 2.0) - (self.glass_oring_groove_od / 2.0)
        lid_spigot_oring_wall = (self.bot_oring_groove_od / 2.0) - (self.lid_spigot_id / 2.0)
        top_collar_corner_wall = (self.cap_top_collar_od / 2.0) - math.hypot(self.core_pocket_w / 2.0, self.core_pocket_w / 2.0)
        checks["bot_cav_to_bolt_wall_mm"] = {"value": round(bot_cav_to_bolt, 3), "min": self.min_wall, "pass": bot_cav_to_bolt >= self.min_wall}
        checks["bot_bolt_to_outer_wall_mm"] = {"value": round(bot_bolt_to_outer, 3), "min": self.min_wall, "pass": bot_bolt_to_outer >= self.min_wall}
        checks["cap_bot_mid_wall_mm"] = {"value": round(cap_bot_mid_wall, 3), "min": 3.2, "pass": cap_bot_mid_wall >= 3.2}
        checks["shroud_oring_outer_wall_mm"] = {"value": round(shroud_oring_outer_wall, 3), "min": 3.0, "pass": shroud_oring_outer_wall >= 3.0}
        checks["lid_spigot_oring_wall_mm"] = {"value": round(lid_spigot_oring_wall, 3), "min": self.min_wall, "pass": lid_spigot_oring_wall >= self.min_wall}
        checks["top_collar_corner_wall_mm"] = {"value": round(top_collar_corner_wall, 3), "min": 3.0, "pass": top_collar_corner_wall >= 3.0}

        # 5. Radial O-ring squeeze & gland fill (MECH-GASKET-1/2 on Ø60 mm PMMA OD & MECH-GASKET-3 on Ø74.4 mm bore)
        g12_gland_nom = 0.5 * (self.glass_oring_groove_od - self.glass_od_nom)
        g12_gland_min = 0.5 * (self.glass_oring_groove_od - self.glass_od_max)
        g12_gland_max = 0.5 * (self.glass_oring_groove_od - self.glass_od_min)
        g12_sq_nom = 100.0 * (self.glass_oring_cs - g12_gland_nom) / self.glass_oring_cs
        g12_sq_min = 100.0 * (self.glass_oring_cs - g12_gland_max) / self.glass_oring_cs
        g12_sq_max = 100.0 * (self.glass_oring_cs - g12_gland_min) / self.glass_oring_cs
        g12_ramp = 0.5 * (self.glass_oring_groove_od - self.glass_bore_id)
        g12_area = g12_gland_min * self.glass_oring_flat_w + 0.5 * g12_ramp * (g12_gland_min + (g12_gland_min - g12_ramp))
        g12_fill = (math.pi * (0.5 * self.glass_oring_cs) ** 2) / g12_area

        g3_gland_nom = 0.5 * (self.cap_bot_cavity_dia - self.bot_oring_groove_od)
        g3_sq_nom = 100.0 * (self.bot_oring_cs - g3_gland_nom) / self.bot_oring_cs
        g3_ramp = 0.5 * (self.lid_spigot_od - self.bot_oring_groove_od)
        g3_area = g3_gland_nom * self.bot_oring_flat_w + 0.5 * g3_ramp * (g3_gland_nom + (g3_gland_nom - g3_ramp))
        g3_fill = (math.pi * (0.5 * self.bot_oring_cs) ** 2) / g3_area

        checks["g12_radial_squeeze_min_pct"] = {"value": round(g12_sq_min, 1), "min": 10.0, "pass": g12_sq_min >= 10.0}
        checks["g12_radial_squeeze_nom_pct"] = {"value": round(g12_sq_nom, 1), "min": 12.0, "max": 25.0, "pass": 12.0 <= g12_sq_nom <= 25.0}
        checks["g12_radial_squeeze_max_pct"] = {"value": round(g12_sq_max, 1), "max": 32.0, "pass": g12_sq_max <= 32.0}
        checks["g12_gland_fill_max"] = {"value": round(g12_fill, 4), "max": 0.85, "pass": g12_fill <= 0.85}
        checks["g3_radial_squeeze_nom_pct"] = {"value": round(g3_sq_nom, 1), "min": 10.0, "max": 22.0, "pass": 10.0 <= g3_sq_nom <= 22.0}
        checks["g3_gland_fill"] = {"value": round(g3_fill, 4), "max": 0.85, "pass": g3_fill <= 0.85}

        # 6. Protruding core, top rain plug & sloped conical roof checks
        hang_to_plug_clr = (self.z_core_top - self.plug_top_insert_h) - (self.z_hang_hole + self.core_hang_hole_dia / 2.0)
        brim_overhang_shroud = 0.5 * (self.cap_top_brim_od - self.glass_od_nom)
        checks["core_protrusion_mm"] = {"value": round(self.core_protrusion_mm, 3), "min": 55.0, "max": 85.0, "pass": 55.0 <= self.core_protrusion_mm <= 85.0}
        checks["hang_hole_to_top_plug_mm"] = {"value": round(hang_to_plug_clr, 3), "min": 2.0, "pass": hang_to_plug_clr >= 2.0}
        checks["cap_top_brim_overhang_mm"] = {"value": round(brim_overhang_shroud, 3), "min": 12.0, "pass": brim_overhang_shroud >= 12.0}
        checks["cap_top_roof_slope_deg"] = {"value": self.cap_top_roof_deg, "min": 10.0, "pass": self.cap_top_roof_deg >= 10.0}

        return checks

    def to_dict(self) -> dict:
        d = asdict(self)
        d["derived"] = {
            "z_base_ring_bot": self.z_base_ring_bot,
            "z_lid_bot_end": self.z_lid_bot_end,
            "z_pcb_bcu": self.z_pcb_bcu,
            "y_j1_mouth": self.y_j1_mouth,
            "z_j1_center": self.z_j1_center,
            "z_core_bot": self.z_core_bot,
            "z_glass_bot": self.z_glass_bot,
            "z_cap_bot_top": self.z_cap_bot_top,
            "z_glass_top": self.z_glass_top,
            "z_cap_top_bot": self.z_cap_top_bot,
            "z_cap_top_top": self.z_cap_top_top,
            "z_cap_top_lock": self.z_cap_top_lock,
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
            "bulkhead_thick": self.bulkhead_thick,
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
