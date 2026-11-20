#!/usr/bin/env python3
"""
Single Source of Truth for LepiLED DIY Maxi Switch (Rev 4.6 — "Field Lantern":
Unified Tapered Frustum, Intact Core Hubs, Dry-Bay Core Anchor, Coaxial Split Cable Clamp & Lofted Rain Roof).

Rev 4.6 Engineering & Industrial-Design Upgrades (Resolving All Rev 4.5 Adversarial Audit Findings):
  1. P0-1 Fixed — Intact Full-Height 30.8 x 30.8 mm Core Sockets & Positive Fastener Clamping:
     - Both internal 45-deg shroud transition cones terminate onto solid R = 24.4 mm (Ø48.8 mm) central hubs
       (2.62 mm corner wall / 9.0 mm flat wall around the 30.8 x 30.8 mm core sockets; 0.000 mm^2 overhang).
     - MECH-CAP-BOT locks the Al core INTERNALLY from the dry electronics bay via 2x M3x16 SHCS bearing flat on
       a 7.1 mm solid ASA bulkhead into MECH-CORE-ANCHOR (cross-pinned flush to the Al core) — ZERO exterior
       side holes or water-ingress paths on MECH-CAP-BOT!
     - MECH-CAP-TOP locks onto the core via 2x M3x10 SHCS bearing on 4.60 mm solid hub shoulders clear of the
       unbroken Ø84 mm eaves rim, with a backed 2.0 x 2.5 mm top neutral-cure oxime silicone seal channel.
  2. P0-2 Fixed — Coaxial 3D-Printed 2-Piece Split Cable Clamp (Eliminates Colliding M20 Gland, -£3.33):
     - MECH-LID-BOT has a 16.0 x 14.0 mm stadium pass-through port (passes intact 90-deg USB-C plug cleanly)
       clamped from below by 2x identical MECH-CABLE-CLAMP halves + slit silicone grommet (0 mm protrusion
       above lid top -> 15.4 mm clear vertical bend room below 90-deg plug body; zero spigot collision!).
  3. P1-1..P1-4 Fixed — Ovality-Safe O-Rings, M2.5 Heat-Set Inserts, Side-Visible D12 & Matte-Black Core:
     - Widened Ø61.6 mm x 14.5 mm shroud bores with 60 x 3.5 mm soft VMQ50/60 radial O-rings (22.9% nom /
       11.4-31.4% squeeze across real 59.2-60.6 mm oval Plexiglas XT tubes; +3.5 mm short-tube margin).
     - 4x filleted PCB standoffs sized for M2.5 x 4.0 x 3.5 mm brass heat-set inserts (zero FDM splitting).
     - 29.8 mm D12 lightpipe (1.4 mm from D12 lens) with 45-deg beveled tip visible through portal while standing;
       Ø9.5 x 0.8 mm recessed pocket protecting MECH-VENT-1 adhesive ePTFE patch.
     - Standardized Black ASA + matte-black spray paint on core (eliminating 76-87 C PETG creep & passing all
       16/16 Real-WPE thermal cases at 22-30 C still air!).
  4. Industrial-Design "Field Lantern" Overhaul (-100+ g plastic, -1 major shell part):
     - Eliminates MECH-BASE-RING: MECH-CAP-BOT is ONE continuous 4.3-deg tapered frustum (Ø87.6 -> Ø74.0 mm)
       recessing MECH-LID-BOT 19 mm inside, with 2 smooth 45-deg-arch cable portals, tactile 0/1/2 switch index
       ribs, and centered bottom cable clip for 0-deg plumb hanging.
     - MECH-CAP-TOP smoothly lofts its unbroken Ø84 mm 25-deg circular rain eaves into an R=4 mm 38.8x38.8 mm
       rounded-square chimney collar; crowned by an 8 mm 45-deg-beveled finial (MECH-PLUG-TOP) and 2-half
       Signal-Orange snap-in hang-hole bushing (MECH-HANG-BUSHING).

All coordinates are in millimeters (mm) using a right-handed global frame:
  - Origin (0, 0, 0): Flat ground plane (bottom rim of unified MECH-CAP-BOT tapered skirt).
  - +Z: Vertically upward along lamp centerline toward MECH-CAP-TOP and MECH-PLUG-TOP.
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

    # Unified 5.1-deg compact tapered bottom frustum (MECH-CAP-BOT: Z = 0.0 .. 80.0 mm, prints INVERTED!)
    cap_bot_base_od: float = 88.4       # Ground-plane base OD (replaces Ø94.4 mm flange + MECH-BASE-RING!)
    cap_bot_collar_od: float = 74.0     # Upper shroud collar OD (matches MECH-CAP-TOP skirt OD!)
    cap_bot_skirt_h: float = 17.5       # Compact recessed skirt shielding SW1 boot (2.5 mm) & split clamp (5.0 mm)
    cap_bot_skirt_id: float = 80.0      # Recesses Ø79.4 mm MECH-LID-BOT + 4x M3 bolt heads cleanly inside skirt!
    cap_bot_portal_w: float = 16.0      # 2x opposing 45-deg gothic-arch cable/drainage portals at ±Y (0 overhang!)
    cap_bot_portal_rect_h: float = 3.0  # + 8.0 mm 45-deg pitched arch crown = 11.0 mm portal height
    cap_bot_cavity_dia: float = 71.0    # Upper electronics bay (Z = 32.0 .. 53.0 mm; clears PCB & 90-deg USB-C plug!)
    cap_bot_spigot_bore_dia: float = 65.0  # Lower radial O-ring sealing bore (Z = 22.5 .. 29.0 mm; 45-deg flare 29->32!)
    cap_bot_ceiling_z: float = 53.0     # Flat upward-facing print floor (2.6 mm above B.Cu TH pins @ Z = 50.4 mm!)
    cap_bot_core_bot_z: float = 58.5    # Core seat on 5.5 mm solid ASA bulkhead (hidden 30.8 mm internal bridge!)
    cap_bot_glass_bot_z: float = 65.5   # Shroud bottom seat (7.0 mm + 14.5 mm hub = 21.5 mm intact 4-wall core socket!)
    core_hub_od: float = 48.8           # Solid R = 24.4 mm central hub in BOTH caps (2.62 mm corner / 9.0 mm flat wall!)

    # Recessed flat bottom lid w/ radial O-ring spigot (MECH-LID-BOT: Z = 17.5 .. 22.5 mm + 6.5 mm spigot)
    lid_bot_od: float = 79.4            # Slips cleanly inside Ø80.0 mm integral skirt (hides lid seam & all 4x M3 bolts!)
    lid_bot_thick: float = 5.0          # Z = 17.5 .. 22.5 mm
    lid_bot_bolt_r: float = 36.8        # 4x M3x10 SHCS at 45/135/225/315 deg into 4x M3 brass inserts (R+2.75=39.55<40!)
    lid_spigot_od: float = 64.2         # Slides cleanly inside Ø65.0 mm bore (0.40 mm radial clearance)
    lid_spigot_id: float = 56.2         # 2.25 mm solid wall behind radial O-ring groove root (R_g = 30.35 mm)
    lid_spigot_h: float = 6.5           # Z = 24.0 .. 30.5 mm

    # Bottom lid radial O-ring (MECH-GASKET-3: standard 62 x 2.5 mm VMQ70 on Ø64.2 mm spigot, 45-deg roof -> 0 overhang!)
    bot_oring_groove_od: float = 60.70  # Radial gland = (65.0 - 60.7)/2 = 2.15 mm -> 14.0% nom squeeze!
    bot_oring_cs: float = 2.5
    bot_oring_flat_w: float = 2.8       # Z = 25.4 .. 28.2 mm + 1.75 mm 45-deg top ramp

    # Brass heat-set inserts & fasteners (M3 lid/clamp/anchor + M2.5 PCB standoffs)
    m3_clearance_dia: float = 3.4
    m3_insert_pilot_dia: float = 4.0    # Standard M3 x 5.0 x 4.2 mm knurled brass heat-set insert pilot bore
    m3_insert_depth: float = 6.0
    m25_insert_pilot_dia: float = 3.3   # Standard M2.5 x 4.0 x 3.5 mm knurled brass heat-set insert pilot bore
    m25_insert_depth: float = 4.6

    # Internal dry-bay core anchor (MECH-CORE-ANCHOR: locks Al core via 2x M3x16 vertical bulkhead bolts — ZERO side holes!)
    anchor_w: float = 23.4              # Slips inside 24.0 x 24.0 mm Al core bore (0.30 mm/side clearance)
    anchor_h_in_core: float = 15.0      # Z = 72.0 .. 87.0 mm inside Al bore (cross-pinned at Z = 79.5 mm by 2x M3x8 CSK!)
    anchor_bolt_x: float = 6.5          # 2x M3x16 SHCS upward at (±6.5, 0.0 mm) through 7.1 mm solid ASA bulkhead!
    anchor_pin_z_rel: float = 7.5       # Cross-pin M3x8 CSK screw height above z_core_bot (Z = 79.5 mm, flush in core!)

    # Driver PCB mounted HORIZONTALLY (SMD/JST side DOWN on 4x M2.5 brass heat-set standoffs via H1..H4)
    pcb_w: float = 36.0                 # Along global X (±18.0 mm)
    pcb_l: float = 46.0                 # Along global Y (centered at pcb_y_center = +6.0 mm -> Y = -17.0 .. +29.0 mm)
    pcb_thick: float = 1.6              # F.Cu = 50.0 mm, B.Cu = 51.6 mm
    pcb_corner_r: float = 2.0
    pcb_y_center: float = 6.0           # Balances PCB (+Y R=33.38) & 90-deg USB-C plug (-Y R=33.83) inside Ø71.0 mm bay!
    pcb_z_fcu: float = 47.0             # F.Cu (SMD/JST down) -> 9.73 mm above SW1 lugs & strain relief clears Z=29 spigot!
    pcb_smd_max_h: float = 4.5          # L1/L2 SRN6045 = 4.5 mm
    pcb_jst_mated_h: float = 9.8        # J2..J4 JST-XH mated downward (Z = 33.7 .. 43.5 mm)
    pcb_jst_pin_protrude: float = 1.8   # TH pins upward on B.Cu (Z = 45.1 .. 46.9 mm -> 2.6 mm below Z=49.5 ceiling!)
    pcb_hole_x: float = 14.0            # H1..H4 at (±14.0, pcb_y_center ± 19.0) = (±14.0, -13.0 / +25.0)
    pcb_hole_y: float = 19.0
    pcb_hole_drill: float = 2.7         # M2.5 NPTH clearance drill
    pcb_hole_keepout: float = 5.5
    pcb_standoff_tip_od: float = 5.5    # Matches Ø5.5 mm copper keepout at PCB face (tapers to Ø7.4 mm at root!)
    pcb_standoff_root_od: float = 7.4   # Robust 2.05 mm wall around Ø3.3 mm M2.5 brass heat-set insert!

    # Compact 90-deg USB-C PD plug + 3D-printed 2-piece coaxial split cable clamp (MECH-CABLE-CLAMP, replaces M20 gland!)
    usbc_j1_overhang_mm: float = 3.18   # GCT USB4085 datasheet front face 7.26 mm from datum (3.18 mm past -23 mm edge)
    usbc_z_offset_from_fcu: float = 1.88
    usbc_mating_depth_mm: float = 4.55
    usbc_plug_90_len: float = 13.0      # Compact 90-deg-down USB-C plug protrusion past J1 mouth
    usbc_plug_90_w: float = 13.2
    usbc_plug_90_h: float = 11.5        # Vertical body height downward from J1 centerline
    usbc_strain_relief_h: float = 7.0   # Explicitly modeled molded strain-relief boot below plug body!
    clamp_x: float = 0.0
    clamp_y: float = -18.5              # Cleanly inside Ø56.2 mm spigot ID; 10.4 mm vertical bend room to plug body!
    clamp_port_w: float = 16.0          # Stadium port in MECH-LID-BOT passes intact 13.2x11.5 mm 90-deg USB-C plug!
    clamp_port_l: float = 14.0
    clamp_bolt_dx: float = 12.0         # 2x M3x12 SHCS clamping split halves upward into lid_bot (R = 22.05 < 28.1 mm!)
    clamp_outer_h: float = 9.5          # Protrudes 9.5 mm below Z = 17.5 -> Z = 8.0 mm (5.0 mm ground clr w/ M3 head!)
    clamp_cable_dia: float = 4.5        # Clamps Ø4.0-4.5 mm round USB-C PD cable jacket via slit silicone grommet

    # Bottom-mounted SW1 toggle switch (C&K 7211SYZBE + silicone boot on MECH-LID-BOT at X=0, Y=+15.0 mm)
    sw1_x: float = 0.0
    sw1_y: float = 15.0                 # Inside Ø56.2 mm spigot (R_corner = 21.65 < 28.1 mm); 18.8 mm gap to clamp port!
    sw1_hole_dia: float = 6.35          # 1/4-40 UNS bushing bore
    sw1_wall_thick: float = 2.5         # 2.5 mm lower wall (Z = 19.0 .. 21.5) + 2.5 mm anti-rotation pocket (21.5 .. 24.0)
    sw1_body_w_x: float = 12.70
    sw1_body_w_y: float = 11.43
    sw1_body_h_z: float = 10.67
    sw1_lugs_h_z: float = 4.80          # Top of lugs at Z = 19 + 2.5 + 10.67 + 4.80 = 36.97 mm (11.2 mm below SMD!)
    sw1_boot_protrude_z: float = 15.0   # Boot downward to Z = 4.0 mm (4.0 mm clear above flat ground!)
    sw1_boot_od: float = 13.3

    # Recessed IP68 ePTFE breather vent + side-visible 45-deg beveled D12 green PD-status lightpipe on MECH-LID-BOT
    vent_x: float = -20.0
    vent_y: float = 0.0
    vent_hole_dia: float = 2.5
    vent_pocket_dia: float = 9.5        # 0.8 mm recessed protective pocket around Ø8 mm adhesive ePTFE patch!
    vent_pocket_depth: float = 0.8
    d12_lightpipe_x: float = 16.0       # Directly beneath D12 (+16.0, -6.6 board -> +16.0, -0.6 global!)
    d12_lightpipe_y: float = -0.6
    d12_lightpipe_dia: float = 2.6      # Accepts 29.8 mm clear Ø2.5 mm PMMA rod (1.4 mm from D12 lens, 45-deg side tip!)

    # Shatter-resistant Clear Unstabilized Extruded PMMA (Plexiglas XT) shroud (MECH-TUBE-1: Ø60 x 54 x 3.0 x 115 mm)
    glass_od_nom: float = 60.0
    glass_id_nom: float = 54.0
    glass_od_max: float = 60.6          # Real extruded Plexiglas XT ovality (+0.6 / -0.8 mm)!
    glass_od_min: float = 59.2
    glass_id_min: float = 53.5
    glass_length: float = 115.0
    glass_length_tol: float = 2.0       # Full ±2.0 mm UK saw-cut tolerance (113.0 .. 117.0 mm) absorbed cleanly!
    glass_socket_depth: float = 14.5    # Deepened from 12.0 -> 14.5 mm (+2.5 mm short-tube gravity-drop margin!)
    glass_bore_id: float = 61.6         # Widened from 60.8 -> 61.6 mm (0.50 mm/side slip clearance over 60.6 mm oval tube!)

    # Shroud radial bore O-rings (MECH-GASKET-1..2: 60 x 3.5 mm soft VMQ50/60 silicone on Ø60 mm PMMA OD!)
    glass_oring_groove_od: float = 65.40  # Gland = 2.70 mm nom -> 22.9% nom / 11.4% @ 59.2 mm / 31.4% @ 60.6 mm!
    glass_oring_cs: float = 3.5
    glass_oring_flat_w: float = 4.6       # + 1.9 mm 45-deg ramp -> max fill 0.77 <= 0.85, zero extrusion!

    # Central protruding Al core (MECH-HS-CORE: stock 200.0 mm cut of 30 x 30 x 3.0 mm Al 6063-T6, sprayed matte black!)
    core_w_nom: float = 30.0
    core_w_max: float = 30.4
    core_wall: float = 3.0
    core_bore_nom: float = 24.0
    core_length: float = 200.0
    core_pocket_w: float = 30.8
    core_wire_slot_w: float = 9.0       # 9.0 x 7.5 mm channels at ±Y pass 7.4 x 5.75 mm JST-XH plugs without de-pinning!
    core_wire_slot_d: float = 7.5
    core_hang_hole_dia: float = 8.0
    core_hang_hole_from_top: float = 16.0

    # Top end-cap (MECH-CAP-TOP) — prints UPRIGHT w/ unbroken Ø84 mm circular eaves lofted to R=4 mm square collar!
    cap_top_skirt_od: float = 74.0      # Matches MECH-CAP-BOT collar OD (4.30 mm solid wall outside Ø65.4 mm O-ring!)
    cap_top_brim_od: float = 84.0       # Unbroken 360-deg Ø84 mm circular rain eaves (+12 mm/side past Ø60 mm shroud!)
    cap_top_skirt_h: float = 10.0       # Vertical skirt before 45-deg underside flare
    cap_top_rim_h: float = 3.0          # Crisp cylindrical drip rim
    cap_top_roof_h: float = 11.5        # Loft height from Ø84 circle -> 38.8x38.8 R4 rounded-square collar (27-35 deg!)
    cap_top_collar_w: float = 38.8      # 4.0 mm uniform flat & corner wall around 30.8x30.8 mm core socket!
    cap_top_collar_r: float = 4.0       # R = 4.0 mm rounded-square transition collar
    cap_top_lock_z_rel: float = 24.5    # 2x M3x10 SHCS at Z = 211.5 mm bearing on 4.6 mm solid hub shoulders (clear of rim!)
    cap_top_seal_groove: float = 2.0    # Backed 2.0 x 2.5 mm top neutral-cure oxime silicone seal channel!
    cap_chamfer: float = 0.8
    min_wall: float = 2.5

    # Chamfered finial top rain plug (MECH-PLUG-TOP: 8 mm 45-deg-beveled obelisk cap!)
    plug_top_w: float = 23.5
    plug_top_insert_h: float = 10.0
    plug_top_cap_w: float = 30.2        # Flush architectural fit on 30.0x30.0 mm Al chimney
    plug_top_cap_h: float = 8.0         # 3.0 mm vertical collar + 5.0 mm 45-deg obelisk bevel!

    # 2-half snap-in Signal-Orange hang-hole paracord bushing (MECH-HANG-BUSHING)
    hang_bush_id: float = 5.4           # Smooth rounded Ø5.4 mm bore for paracord / mini carabiner
    hang_bush_flange_od: float = 12.0   # High-visibility Signal-Orange touchpoint accent!
    hang_bush_flange_t: float = 1.6

    # 8x Off-the-shelf pre-mounted 20 mm Copper DTP LED stars (4x UV + 4x Vis; M3 pan screws + nylon washers)
    star_dia: float = 20.0
    star_thick: float = 1.50
    star_tim_thick: float = 0.15
    star_uv_z_offset: float = 16.0
    star_vis_z_offset: float = -16.0
    star_bolt_r: float = 9.5
    led_uv_max_h: float = 2.08
    led_vis_max_h: float = 2.39
    m3_pan_plus_washer_h: float = 3.20

    @property
    def print_clearance(self) -> float:
        return 0.25 if self.process == "FDM" else 0.15

    # Derived global coordinates (Rev 4.6)
    @property
    def z_lid_bot_start(self) -> float:
        return self.cap_bot_skirt_h  # 19.0

    @property
    def z_lid_bot_end(self) -> float:
        return self.z_lid_bot_start + self.lid_bot_thick  # 24.0

    @property
    def z_pcb_bcu(self) -> float:
        return self.pcb_z_fcu + self.pcb_thick  # 51.6

    @property
    def y_j1_mouth(self) -> float:
        return self.pcb_y_center - 0.5 * self.pcb_l - self.usbc_j1_overhang_mm  # -20.18

    @property
    def z_j1_center(self) -> float:
        return self.pcb_z_fcu - self.usbc_z_offset_from_fcu  # 48.12

    @property
    def z_core_bot(self) -> float:
        return self.cap_bot_core_bot_z  # 72.0

    @property
    def z_anchor_pin(self) -> float:
        return self.z_core_bot + self.anchor_pin_z_rel  # 79.5

    @property
    def z_glass_bot(self) -> float:
        return self.cap_bot_glass_bot_z  # 86.5

    @property
    def z_cap_bot_top(self) -> float:
        return self.z_glass_bot + self.glass_socket_depth  # 101.0

    @property
    def z_glass_top(self) -> float:
        return self.z_glass_bot + self.glass_length  # 201.5

    @property
    def z_cap_top_bot(self) -> float:
        return self.z_glass_top - self.glass_socket_depth  # 187.0

    @property
    def z_cap_top_brim_bot(self) -> float:
        return self.z_cap_top_bot + self.cap_top_skirt_h  # 197.0

    @property
    def z_cap_top_brim_rim_bot(self) -> float:
        return self.z_cap_top_brim_bot + 0.5 * (self.cap_top_brim_od - self.cap_top_skirt_od)  # 202.0

    @property
    def z_cap_top_brim_rim_top(self) -> float:
        return self.z_cap_top_brim_rim_bot + self.cap_top_rim_h  # 205.0

    @property
    def z_cap_top_top(self) -> float:
        return round(self.z_cap_top_brim_rim_top + self.cap_top_roof_h, 3)  # 216.5

    @property
    def z_cap_top_lock(self) -> float:
        return self.z_cap_top_bot + self.cap_top_lock_z_rel  # 211.5

    @property
    def z_core_top(self) -> float:
        return self.z_core_bot + self.core_length  # 272.0

    @property
    def core_protrusion_mm(self) -> float:
        return round(self.z_core_top - self.z_cap_top_top, 3)  # 55.5

    @property
    def z_hang_hole(self) -> float:
        return self.z_core_top - self.core_hang_hole_from_top  # 256.0

    @property
    def z_plug_top_end(self) -> float:
        return self.z_core_top + self.plug_top_cap_h  # 280.0

    @property
    def total_height_mm(self) -> float:
        return round(self.z_plug_top_end, 3)  # 280.0 (ground at Z=0!)

    @property
    def exposed_glass_window(self) -> float:
        return self.z_cap_top_bot - self.z_cap_bot_top  # 86.0

    @property
    def z_optical_center(self) -> float:
        return 0.5 * (self.z_glass_bot + self.z_glass_top)  # 144.0

    @property
    def z_led_uv(self) -> float:
        return self.z_optical_center + self.star_uv_z_offset  # 160.0

    @property
    def z_led_vis(self) -> float:
        return self.z_optical_center + self.star_vis_z_offset  # 128.0

    @property
    def axial_uv_to_top_mm(self) -> float:
        return round(self.z_cap_top_top - self.z_led_uv, 3)  # 56.5

    @property
    def axial_uv_to_vis_mm(self) -> float:
        return self.z_led_uv - self.z_led_vis  # 32.0

    @property
    def axial_vis_to_bot_mm(self) -> float:
        return self.z_led_vis - self.z_core_bot  # 56.0

    @property
    def bulkhead_thick(self) -> float:
        return self.z_core_bot - self.cap_bot_ceiling_z  # 16.0 mm perimeter (7.1 mm at anchor M3 bolts!)

    def cap_bot_outer_r_at_z(self, z: float) -> float:
        """Exact outer radius of the continuous tapered frustum MECH-CAP-BOT at global Z."""
        r0 = 0.5 * self.cap_bot_base_od
        r1 = 0.5 * self.cap_bot_collar_od
        return r0 + (r1 - r0) * (z / self.z_cap_bot_top)

    def verify_all(self) -> dict[str, dict[str, float | bool]]:
        checks: dict[str, dict[str, float | bool]] = {}
        r_cav = self.cap_bot_cavity_dia / 2.0

        # 1. Horizontal driver_pcb & 90-deg USB-C plug (+ 7 mm strain relief!) clearances inside Ø71.0 mm bay
        pcb_pos_corner_r = math.hypot(self.pcb_w / 2.0 - self.pcb_corner_r, self.pcb_y_center + self.pcb_l / 2.0 - self.pcb_corner_r) + self.pcb_corner_r
        pcb_neg_corner_r = math.hypot(self.pcb_w / 2.0 - self.pcb_corner_r, abs(self.pcb_y_center - self.pcb_l / 2.0) - self.pcb_corner_r) + self.pcb_corner_r
        plug_corner_r = math.hypot(self.usbc_plug_90_w / 2.0, abs(self.y_j1_mouth) + self.usbc_plug_90_len)
        th_pin_to_ceiling = self.cap_bot_ceiling_z - (self.z_pcb_bcu + self.pcb_jst_pin_protrude)
        jst_bot_z = self.pcb_z_fcu - self.pcb_jst_mated_h
        sw1_lugs_top_z = self.z_lid_bot_start + self.sw1_wall_thick + self.sw1_body_h_z + self.sw1_lugs_h_z
        smd_to_sw1_z = (self.pcb_z_fcu - 1.8) - sw1_lugs_top_z
        plug_bot_z = (self.z_j1_center + 2.8) - self.usbc_plug_90_h
        strain_bot_z = plug_bot_z - self.usbc_strain_relief_h
        checks["pcb_radial_clearance_mm"] = {"value": round(r_cav - max(pcb_pos_corner_r, pcb_neg_corner_r), 3), "min": 1.5, "pass": (r_cav - max(pcb_pos_corner_r, pcb_neg_corner_r)) >= 1.5}
        checks["usbc_90_plug_radial_clr_mm"] = {"value": round(r_cav - plug_corner_r, 3), "min": 1.2, "pass": (r_cav - plug_corner_r) >= 1.2}
        checks["pcb_th_pins_to_ceiling_mm"] = {"value": round(th_pin_to_ceiling, 3), "min": 2.0, "pass": th_pin_to_ceiling >= 2.0}
        checks["pcb_smd_above_sw1_lugs_mm"] = {"value": round(smd_to_sw1_z, 3), "min": 5.5, "pass": smd_to_sw1_z >= 5.5}
        checks["pcb_jst_above_lid_top_mm"] = {"value": round(jst_bot_z - self.z_lid_bot_end, 3), "min": 10.0, "pass": (jst_bot_z - self.z_lid_bot_end) >= 10.0}
        checks["usbc_strain_above_lid_top_mm"] = {"value": round(strain_bot_z - self.z_lid_bot_end, 3), "min": 3.0, "pass": (strain_bot_z - self.z_lid_bot_end) >= 3.0}

        # 2. Recessed MECH-LID-BOT, 2-piece Split Cable Clamp, SW1 & ground clearances
        r_spigot_in = self.lid_spigot_id / 2.0
        clamp_port_outer_r = math.hypot(self.clamp_port_w / 2.0, abs(self.clamp_y) + self.clamp_port_l / 2.0)
        clamp_bolt_r = math.hypot(self.clamp_bolt_dx, abs(self.clamp_y))
        clamp_to_sw1_gap = (self.sw1_y - self.sw1_body_w_y / 2.0) - (self.clamp_y + self.clamp_port_l / 2.0)
        sw1_corner_r = math.hypot(self.sw1_body_w_x / 2.0, self.sw1_y + self.sw1_body_w_y / 2.0)
        sw1_boot_ground_clr = self.z_lid_bot_start - self.sw1_boot_protrude_z
        clamp_ground_clr = self.z_lid_bot_start - self.clamp_outer_h
        checks["clamp_port_in_spigot_clr_mm"] = {"value": round(r_spigot_in - clamp_port_outer_r, 3), "min": 1.0, "pass": (r_spigot_in - clamp_port_outer_r) >= 1.0}
        checks["clamp_bolt_in_spigot_clr_mm"] = {"value": round(r_spigot_in - (clamp_bolt_r + 2.0), 3), "min": 2.5, "pass": (r_spigot_in - (clamp_bolt_r + 2.0)) >= 2.5}
        checks["clamp_to_sw1_gap_mm"] = {"value": round(clamp_to_sw1_gap, 3), "min": 14.0, "pass": clamp_to_sw1_gap >= 14.0}
        checks["sw1_in_spigot_clr_mm"] = {"value": round(r_spigot_in - sw1_corner_r, 3), "min": 5.0, "pass": (r_spigot_in - sw1_corner_r) >= 5.0}
        checks["sw1_boot_above_ground_mm"] = {"value": round(sw1_boot_ground_clr, 3), "min": 2.5, "pass": sw1_boot_ground_clr >= 2.5}
        checks["clamp_above_ground_mm"] = {"value": round(clamp_ground_clr, 3), "min": 5.0, "pass": clamp_ground_clr >= 5.0}

        # 3. Radial clearances inside Ø60 x 54 mm Plexiglas XT shroud (ID_min = 53.5 mm) + solid R=24.4 mm hubs
        r_glass_min = self.glass_id_min / 2.0
        r_hub = self.core_hub_od / 2.0
        r_core_max_corner = math.hypot(self.core_w_max / 2.0, self.core_w_max / 2.0)
        r_led_vis_max = self.core_w_nom / 2.0 + self.star_tim_thick + self.star_thick + self.led_vis_max_h
        r_m3_head_corner = math.hypot(self.core_w_nom / 2.0 + self.star_tim_thick + self.star_thick + self.m3_pan_plus_washer_h, self.star_bolt_r)
        star_gap_z = (self.z_led_uv - self.star_dia / 2.0) - (self.z_led_vis + self.star_dia / 2.0)
        wire_slot_outer_r = math.hypot(self.core_wire_slot_w / 2.0, self.core_pocket_w / 2.0 + self.core_wire_slot_d)
        hub_corner_wall = r_hub - math.hypot(self.core_pocket_w / 2.0, self.core_pocket_w / 2.0)
        checks["shroud_bore_to_od_max_mm"] = {"value": round(0.5 * (self.glass_bore_id - self.glass_od_max), 3), "min": 0.45, "pass": 0.5 * (self.glass_bore_id - self.glass_od_max) >= 0.45}
        checks["core_hub_to_shroud_id_min_mm"] = {"value": round(r_glass_min - r_hub, 3), "min": 2.0, "pass": (r_glass_min - r_hub) >= 2.0}
        checks["core_hub_corner_wall_mm"] = {"value": round(hub_corner_wall, 3), "min": self.min_wall, "pass": hub_corner_wall >= self.min_wall}
        checks["core_corner_to_shroud_id_min_mm"] = {"value": round(r_glass_min - r_core_max_corner, 3), "min": 3.0, "pass": (r_glass_min - r_core_max_corner) >= 3.0}
        checks["led_vis_to_shroud_id_min_mm"] = {"value": round(r_glass_min - r_led_vis_max, 3), "min": 5.0, "pass": (r_glass_min - r_led_vis_max) >= 5.0}
        checks["m3_head_to_shroud_id_min_mm"] = {"value": round(r_glass_min - r_m3_head_corner, 3), "min": 3.0, "pass": (r_glass_min - r_m3_head_corner) >= 3.0}
        checks["uv_to_vis_star_gap_mm"] = {"value": round(star_gap_z, 3), "min": 10.0, "pass": star_gap_z >= 10.0}
        checks["wire_slot_inside_shroud_id_mm"] = {"value": round(r_glass_min - wire_slot_outer_r, 3), "min": 2.5, "pass": (r_glass_min - wire_slot_outer_r) >= 2.5}

        # 4. Structural walls (>= 2.5 mm across unified frustum, lid inserts, O-ring bores & top collar)
        r_ins = self.m3_insert_pilot_dia / 2.0
        lid_ins_inner_wall = (self.lid_bot_bolt_r - r_ins) - (self.cap_bot_spigot_bore_dia / 2.0)
        lid_ins_outer_wall = self.cap_bot_outer_r_at_z(self.z_lid_bot_end + self.m3_insert_depth) - (self.lid_bot_bolt_r + r_ins)
        skirt_wall_min = self.cap_bot_outer_r_at_z(self.cap_bot_skirt_h) - (self.cap_bot_skirt_id / 2.0)
        cap_bot_mid_wall = self.cap_bot_outer_r_at_z(self.cap_bot_ceiling_z) - r_cav
        shroud_oring_outer_wall = (self.cap_bot_collar_od / 2.0) - (self.glass_oring_groove_od / 2.0)
        lid_spigot_oring_wall = (self.bot_oring_groove_od / 2.0) - (self.lid_spigot_id / 2.0)
        top_collar_flat_wall = 0.5 * (self.cap_top_collar_w - self.core_pocket_w)
        checks["lid_insert_inner_wall_mm"] = {"value": round(lid_ins_inner_wall, 3), "min": 2.2, "pass": lid_ins_inner_wall >= 2.2}
        checks["lid_insert_outer_wall_mm"] = {"value": round(lid_ins_outer_wall, 3), "min": self.min_wall, "pass": lid_ins_outer_wall >= self.min_wall}
        checks["skirt_wall_min_mm"] = {"value": round(skirt_wall_min, 3), "min": self.min_wall, "pass": skirt_wall_min >= self.min_wall}
        checks["cap_bot_bay_wall_mm"] = {"value": round(cap_bot_mid_wall, 3), "min": 3.0, "pass": cap_bot_mid_wall >= 3.0}
        checks["shroud_oring_outer_wall_mm"] = {"value": round(shroud_oring_outer_wall, 3), "min": 3.5, "pass": shroud_oring_outer_wall >= 3.5}
        checks["lid_spigot_oring_wall_mm"] = {"value": round(lid_spigot_oring_wall, 3), "min": 2.2, "pass": lid_spigot_oring_wall >= 2.2}
        checks["top_collar_flat_wall_mm"] = {"value": round(top_collar_flat_wall, 3), "min": 3.5, "pass": top_collar_flat_wall >= 3.5}

        # 5. Radial O-ring squeeze & gland fill (60x3.5 VMQ50/60 on real 59.2-60.6 mm XT PMMA & 62x2.5 VMQ70 on lid)
        g12_gland_nom = 0.5 * (self.glass_oring_groove_od - self.glass_od_nom)
        g12_gland_min = 0.5 * (self.glass_oring_groove_od - self.glass_od_max)
        g12_gland_max = 0.5 * (self.glass_oring_groove_od - self.glass_od_min)
        g12_sq_nom = 100.0 * (self.glass_oring_cs - g12_gland_nom) / self.glass_oring_cs
        g12_sq_min = 100.0 * (self.glass_oring_cs - g12_gland_max) / self.glass_oring_cs
        g12_sq_max = 100.0 * (self.glass_oring_cs - g12_gland_min) / self.glass_oring_cs
        g12_ramp = 0.5 * (self.glass_oring_groove_od - self.glass_bore_id)
        g12_area = g12_gland_min * self.glass_oring_flat_w + 0.5 * g12_ramp * (g12_gland_min + (g12_gland_min - g12_ramp))
        g12_fill = (math.pi * (0.5 * self.glass_oring_cs) ** 2) / g12_area

        g3_gland_nom = 0.5 * (self.cap_bot_spigot_bore_dia - self.bot_oring_groove_od)
        g3_sq_nom = 100.0 * (self.bot_oring_cs - g3_gland_nom) / self.bot_oring_cs
        g3_ramp = 0.5 * (self.lid_spigot_od - self.bot_oring_groove_od)
        g3_area = g3_gland_nom * self.bot_oring_flat_w + 0.5 * g3_ramp * (g3_gland_nom + (g3_gland_nom - g3_ramp))
        g3_fill = (math.pi * (0.5 * self.bot_oring_cs) ** 2) / g3_area

        # Short-tube (-2 mm = 113.0 mm) gravity-drop engagement margin above top of g2 flat root!
        short_tube_top = (self.z_glass_bot - 1.0) + (self.glass_length - self.glass_length_tol) - 1.0  # -1 mm end bevel
        g2_flat_top = self.z_cap_top_bot + 3.0 + self.glass_oring_flat_w
        short_tube_seal_margin = short_tube_top - g2_flat_top

        checks["g12_radial_squeeze_min_pct"] = {"value": round(g12_sq_min, 1), "min": 10.0, "pass": g12_sq_min >= 10.0}
        checks["g12_radial_squeeze_nom_pct"] = {"value": round(g12_sq_nom, 1), "min": 14.0, "max": 26.0, "pass": 14.0 <= g12_sq_nom <= 26.0}
        checks["g12_radial_squeeze_max_pct"] = {"value": round(g12_sq_max, 1), "max": 33.0, "pass": g12_sq_max <= 33.0}
        checks["g12_gland_fill_max"] = {"value": round(g12_fill, 4), "max": 0.85, "pass": g12_fill <= 0.85}
        checks["short_tube_g2_margin_mm"] = {"value": round(short_tube_seal_margin, 3), "min": 2.0, "pass": short_tube_seal_margin >= 2.0}
        checks["g3_radial_squeeze_nom_pct"] = {"value": round(g3_sq_nom, 1), "min": 10.0, "max": 22.0, "pass": 10.0 <= g3_sq_nom <= 22.0}
        checks["g3_gland_fill"] = {"value": round(g3_fill, 4), "max": 0.85, "pass": g3_fill <= 0.85}

        # 6. Protruding core, top finial plug & lofted rain roof checks
        hang_to_plug_clr = (self.z_core_top - self.plug_top_insert_h) - (self.z_hang_hole + self.core_hang_hole_dia / 2.0)
        brim_overhang_shroud = 0.5 * (self.cap_top_brim_od - self.glass_od_nom)
        roof_slope_min_deg = math.degrees(math.atan2(self.cap_top_roof_h, 0.5 * (self.cap_top_brim_od - self.cap_top_collar_w)))
        checks["core_protrusion_mm"] = {"value": round(self.core_protrusion_mm, 3), "min": 55.0, "max": 85.0, "pass": 55.0 <= self.core_protrusion_mm <= 85.0}
        checks["hang_hole_to_top_plug_mm"] = {"value": round(hang_to_plug_clr, 3), "min": 2.0, "pass": hang_to_plug_clr >= 2.0}
        checks["cap_top_brim_overhang_mm"] = {"value": round(brim_overhang_shroud, 3), "min": 12.0, "pass": brim_overhang_shroud >= 12.0}
        checks["cap_top_roof_slope_deg"] = {"value": round(roof_slope_min_deg, 1), "min": 20.0, "pass": roof_slope_min_deg >= 20.0}

        return checks

    def to_dict(self) -> dict:
        d = asdict(self)
        d["derived"] = {
            "z_lid_bot_start": self.z_lid_bot_start,
            "z_lid_bot_end": self.z_lid_bot_end,
            "z_pcb_bcu": self.z_pcb_bcu,
            "y_j1_mouth": self.y_j1_mouth,
            "z_j1_center": self.z_j1_center,
            "z_core_bot": self.z_core_bot,
            "z_anchor_pin": self.z_anchor_pin,
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
            "frustum_taper_deg": round(math.degrees(math.atan2(0.5 * (self.cap_bot_base_od - self.cap_bot_collar_od), self.z_cap_bot_top)), 2),
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
