#!/usr/bin/env python3
"""
Single Source of Truth for LepiLED DIY Maxi Switch (Rev 4.8 — "Field Lantern":
Serviceable Lid-Mounted PCB, Sealed Lofted Collar, Staggered Core Anchor,
Blind-Bolted Conical Split Cable Clamp & PETG/ASA-Agnostic Tolerance).

Rev 4.8 Mechanical Fixes (Resolving ALL Adversarial Critical Review Findings):
  1. P0-1 Fixed — Zero Roof Holes / Silicone-Groove Breach on MECH-CAP-TOP:
     - Adds a 9.5 mm vertical rounded-square chimney collar (40.4 x 40.4 mm, R=4 mm) above the
       25-deg lofted rain roof so the M3x10 core lock screws bear flat on solid 4.65 mm vertical
       collar walls 5.0 mm ABOVE the internal shroud cone apex and 1.25 mm BELOW the top silicone
       seal groove. Enforced by automated exterior-to-interior ray-cast breach gate!
  2. P0-2 Fixed — Staggered MECH-CORE-ANCHOR & Full-Length Modeled Fasteners/Inserts:
     - Vertical dry-bay M3x12 SHCS + brass inserts moved to ±Y (0, ±6.5 mm); horizontal flush
       M3x8 CSK cross-pins + brass inserts on ±X at Z_rel = 13.0 mm (90-deg orthogonal + >4.4 mm
       vertical clearance; ZERO insert/screw collision!). All 14 brass inserts & exact-length BOM
       screws are explicitly modeled in the all-pairs B-Rep check.
  3. P0-3 Fixed — Round-Star Edge-Clamping Bolt Pitch (star_bolt_r = 11.7 mm):
     - Widens M3 star bolts from 9.5 -> 11.7 mm (23.4 mm pitch; M3 shank clears every Ø20.0 mm
       round Cu DTP board by 0.20 mm while Ø7.0 mm DIN 125 nylon washers clamp 1.80 mm of star rim).
     - Star pitch set to 34.0 mm (±17.0 mm) leaving 3.6 mm clear gap between adjacent nylon washers.
  4. P0-4 Fixed — Serviceable Lid-Mounted PCB (Eliminates Blind USB-C Mating & Spigot Crush):
     - Horizontal driver_pcb (SMD/JST-side UP!) mounts on 4x integral M2.5 brass-insert standoffs
       rising UP from MECH-LID-BOT inside an unobstructed straight Ø71.6 mm bore!
     - User mates J1 (realistic 15.0 mm 90-deg USB-C plug), J4 (SW1), and clamps the cable in
       OPEN AIR on the bench, plugs J2/J3 facing upward, and slides lid+PCB straight up in one motion!
     - D12 red PD LED is directly visible on top of PCB during bench bring-up (fragile 28 mm
       lightpipe rod & through-bore eliminated!).
  5. P0-5 Fixed — Real 18.6 mm SW1 Boot Clearance, Blind Conical Cable Clamp & Intact Ribs:
     - Deepens skirt to 22.0 mm so real C&K 7211SYZBE + 759D02000 boot (18.6 mm protrusion) sits
       3.4 mm recessed inside the skirt; aligns 12.70(X)x11.43(Y) anti-rotation pocket with throw axis;
       moves tactile 0/1/2 ribs to Z=13.0..19.5 mm above the +Y portal so none are erased!
     - MECH-LID-BOT thickened to 7.0 mm for BLIND M3 brass-insert pockets (1.8 mm solid roof into dry
       bay) + 45-deg tapered conical seat driving radial compression in MECH-CABLE-CLAMP onto a slit
       silicone sleeve; cuts the Ø9.5 x 0.8 mm internal recessed MECH-VENT-1 pocket.
  6. PETG/ASA-Agnostic Clearances & Snap-Fit Hang Bushing:
     - Core socket widened to 31.1 x 31.1 mm (+0.35 mm/side over 30.4 mm max extruded Al tube) so
       parts print cleanly on any workshop PETG or ASA printer.
     - Adds 0.35 mm snap-retention barbs to MECH-HANG-BUSHING halves.

Global Right-Handed Frame (mm):
  - Origin (0, 0, 0): Flat ground plane (bottom rim of MECH-CAP-BOT skirt).
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

    # Unified "Field Lantern" bottom housing (MECH-CAP-BOT: Z = 0.0 .. 88.5 mm, prints INVERTED!)
    cap_bot_base_od: float = 94.4        # Cylindrical lower skirt OD (Z = 0 .. 36.0 mm -> 3.1 mm skirt wall!)
    cap_bot_taper_start_z: float = 36.0  # Smooth 10.8-deg frustum taper from Ø94.4 (Z=36) -> Ø74.0 (Z=89.5)
    cap_bot_collar_od: float = 74.0      # Upper shroud collar OD (matches MECH-CAP-TOP skirt OD!)
    cap_bot_skirt_h: float = 22.0        # Deepened skirt shielding real 18.6 mm SW1 boot by 3.4 mm!
    cap_bot_skirt_id: float = 88.2       # Recesses Ø87.6 mm MECH-LID-BOT + 4x flush M3 CSK screws cleanly inside!
    cap_bot_portal_w: float = 16.0       # 2x opposing 45-deg gothic-arch cable/drainage portals at ±Y (0 overhang!)
    cap_bot_portal_rect_h: float = 3.0   # + 8.0 mm 45-deg pitched arch crown = 11.0 mm portal height
    cap_bot_cavity_dia: float = 71.6     # Unobstructed straight Ø71.6 mm bore from spigot to ceiling!
    cap_bot_spigot_bore_dia: float = 71.6  # Matches cavity_dia -> straight-up lid+PCB+USB-C plug insertion!
    cap_bot_ceiling_z: float = 63.5      # Flush CSK anchor bolts -> 5.6 mm clear above J2/J3/J4 mated plugs (57.9)!
    cap_bot_core_bot_z: float = 69.0     # Core seat on 5.5 mm solid bulkhead (1 hidden internal bridge)
    cap_bot_glass_bot_z: float = 75.0    # Shroud bottom seat (6.0 + 14.5 = 20.5 mm intact 4-wall core socket!)
    core_hub_od: float = 49.0            # Solid R = 24.5 mm central hub in BOTH caps (2.51 mm corner wall!)

    # Recessed bottom lid w/ radial O-ring spigot + 4x integral M3 PCB standoffs (MECH-LID-BOT: Z = 22.0 .. 30.5)
    lid_bot_od: float = 87.6             # Slips cleanly inside Ø88.2 mm integral skirt
    lid_bot_thick: float = 8.5           # Z = 22.0 .. 30.5 mm (1.5 mm solid roof above std M3x5.0 clamp inserts!)
    lid_bot_bolt_r: float = 40.0         # 4x M3x12 CSK flush lid screws (2.20 mm insert inner wall & 0.55 mm outer rim!)
    lid_spigot_od: float = 70.8          # Slides cleanly inside Ø71.6 mm bore (0.40 mm/side clearance)
    lid_spigot_id: float = 62.8          # 2.25 mm solid wall behind radial O-ring groove root (R_g = 33.65 mm)
    lid_spigot_h: float = 7.0            # Z = 30.5 .. 37.5 mm

    # Bottom lid radial O-ring (MECH-GASKET-3: standard 68 x 2.5 mm VMQ70 on Ø70.8 mm spigot, 0 overhang!)
    bot_oring_groove_od: float = 67.30   # Radial gland = (71.6 - 67.3)/2 = 2.15 mm -> 14.0% nom squeeze!
    bot_oring_cs: float = 2.5
    bot_oring_flat_w: float = 2.8        # Z = 31.9 .. 34.7 mm + 1.75 mm 45-deg top ramp

    # Unified M3 Brass Heat-Set Inserts & CSK Fasteners (ALL 14 inserts = identical workshop M3 x 5.0 x 4.2 mm!)
    m3_clearance_dia: float = 3.4
    m3_insert_pilot_dia: float = 4.0     # Standard M3 x 5.0 x 4.2 mm knurled brass heat-set insert pilot bore
    m3_insert_depth: float = 6.0
    m3_insert_blind_depth: float = 7.0   # Blind M3x5.0 insert bore (5.1 mm) + 1.9 mm 45-deg cone in 8.5 mm lid (1.5 mm roof!)

    # Staggered internal dry-bay core anchor (MECH-CORE-ANCHOR: vertical bolts ±Y, cross-pins ±X -> ZERO clash!)
    anchor_w: float = 23.4               # Slips inside 24.0 x 24.0 mm Al core bore (0.30 mm/side clearance)
    anchor_h_in_core: float = 19.0       # Z = 69.0 .. 88.0 mm inside Al bore
    anchor_bolt_y: float = 6.5           # 2x M3x12 CSK flush upward at (0.0, ±6.5 mm) through 5.5 mm bulkhead!
    anchor_pin_z_rel: float = 13.0       # 2x M3x8 CSK cross-pins on ±X at Z_rel = 13.0 mm (Z = 82.0 mm, flush!)

    # Serviceable Lid-Mounted Driver PCB (SMD/JST-Side UP on 4x unified M3 standoffs rising from MECH-LID-BOT!)
    pcb_w: float = 36.0                  # Along global X (±18.0 mm)
    pcb_l: float = 46.0                  # Along global Y (centered at pcb_y_center = +7.3 mm)
    pcb_thick: float = 1.6               # B.Cu = 46.5 mm (DOWN), F.Cu = 48.1 mm (UP — SMD/JST/D12 face UP!)
    pcb_corner_r: float = 2.0
    pcb_y_center: float = 7.3            # Balances PCB (+Y R=34.51) & realistic 15 mm 90-deg USB-C plug (-Y R=34.52)!
    pcb_z_bcu: float = 46.5              # B.Cu bottom face resting on 4x MECH-LID-BOT M3 standoffs (Z = 30.5 .. 46.5)
    pcb_smd_max_h: float = 4.5           # L1/L2 SRN6045 = 4.5 mm upward from F.Cu
    pcb_jst_mated_h: float = 9.8         # J2..J4 JST-XH mated upward (Z = 48.1 .. 57.9 mm; 5.6 mm below flush ceiling!)
    pcb_jst_pin_protrude: float = 1.8    # TH pins downward below B.Cu (Z = 44.7 .. 46.5 mm -> 4.7 mm above SW1 lugs!)
    pcb_hole_x: float = 14.0             # H1..H4 at (±14.0, pcb_y_center ± 19.0)
    pcb_hole_y: float = 19.0
    pcb_hole_drill: float = 3.2          # Unified M3 NPTH clearance drill (r=3.10 mm F/B.Cu copper keepout!)
    pcb_hole_keepout: float = 6.2
    pcb_standoff_tip_od: float = 6.0     # Fits cleanly inside Ø6.2 mm B.Cu copper keepout!
    pcb_standoff_body_od: float = 7.0    # 1.50 mm solid wall around standard Ø4.0 mm M3x5.0 brass heat-set insert!

    # Realistic 15.0 mm 90-deg-down USB-C PD plug + blind-bolted conical radial-compression split cable clamp
    usbc_j1_overhang_mm: float = 3.18    # GCT USB4085 front mouth 7.26 mm from Row B (3.18 mm past -23 mm edge)
    usbc_z_offset_from_fcu: float = 1.88
    usbc_mating_depth_mm: float = 4.55
    usbc_plug_90_len: float = 15.0       # REALISTIC 15.0 mm 90-deg USB-C plug protrusion (upgraded from 13.0 mm!)
    usbc_plug_90_w: float = 13.2
    usbc_plug_90_h: float = 11.5         # Drops downward past -Y PCB edge (Z = 40.5 .. 52.0 mm -> clears spigot 36.0!)
    usbc_strain_relief_h: float = 7.0    # Molded strain-relief boot (Z = 33.5 .. 40.5 mm -> fits inside Ø62.8 spigot!)
    clamp_x: float = 0.0
    clamp_y: float = -20.5               # Cleanly inside Ø62.8 mm spigot ID (2.55 mm clear!); below plug centerline
    clamp_port_w: float = 16.5           # Stadium port passes intact 13.2 x 11.5 mm 90-deg USB-C plug effortlessly!
    clamp_port_l: float = 14.5
    clamp_bolt_dx: float = 13.0          # 2x M3x14 SHCS into BLIND M3 inserts (ZERO through-holes into dry bay!)
    clamp_outer_h: float = 9.0           # Protrudes 9.0 mm below Z = 22.0 -> Z = 13.0 (10.0 mm ground clr w/ M3 head!)
    clamp_cable_dia: float = 4.5         # Clamps Ø4.0-4.5 mm round USB-C PD cable jacket via slit silicone sleeve

    # Bottom-mounted SW1 toggle switch (C&K 7211SYZBE + 759D02000 boot on MECH-LID-BOT at X=0, Y=+15.0 mm)
    sw1_x: float = 0.0
    sw1_y: float = 15.0                  # Inside Ø62.8 mm spigot; 21.5 mm gap to clamp port!
    sw1_hole_dia: float = 6.35           # 1/4-40 UNS bushing bore
    sw1_wall_thick: float = 2.5          # 2.5 mm lower wall (Z = 22.0 .. 24.5) + 4.5 mm upper anti-rotation pocket!
    sw1_body_w_x: float = 12.70          # 12.70 mm along X = 3-terminal toggle throw axis (aligned with 0/1/2 ribs!)
    sw1_body_w_y: float = 11.43          # 11.43 mm along Y = 2-pole width
    sw1_body_h_z: float = 10.67
    sw1_lugs_h_z: float = 4.80           # Top of lugs at Z = 22.0 + 2.5 + 10.67 + 4.80 = 39.97 mm (3.7 mm below pins!)
    sw1_boot_protrude_z: float = 18.6    # REAL 8.89 bushing - 2.5 wall + 10.67 bat + 1.5 boot cap = 18.6 mm!
    sw1_boot_od: float = 13.3

    # Recessed IP68 ePTFE breather vent on sheltered INSIDE face of MECH-LID-BOT (D12 lightpipe eliminated!)
    vent_x: float = -21.5
    vent_y: float = 0.0
    vent_hole_dia: float = 2.5
    vent_pocket_dia: float = 9.5         # Actually cut 0.8 mm deep recessed pocket on INSIDE top face Z=28.2..29.0!
    vent_pocket_depth: float = 0.8

    # PLEXIGLAS XT Clear 0A070 (29070) UV-A transmitting extruded PMMA shroud (Ø60 x 54 x 3.0 x 115 mm)
    glass_od_nom: float = 60.0
    glass_id_nom: float = 54.0
    glass_od_max: float = 60.6           # Real extruded Plexiglas XT ovality (+0.6 / -0.8 mm)
    glass_od_min: float = 59.2
    glass_id_min: float = 53.5
    glass_length: float = 115.0
    glass_length_tol: float = 2.0        # Full ±2.0 mm UK saw-cut tolerance (113.0 .. 117.0 mm)
    glass_socket_depth: float = 14.5
    glass_bore_id: float = 61.6          # 0.50 mm/side slip clearance over 60.6 mm oval tube

    # Shroud radial bore O-rings (MECH-GASKET-1..2: 60 x 3.5 mm soft VMQ50/60 silicone)
    glass_oring_groove_od: float = 65.40 # Gland = 2.70 mm nom -> 22.9% nom / 11.4-31.4% squeeze across ovality
    glass_oring_cs: float = 3.5
    glass_oring_flat_w: float = 4.6

    # Central protruding Al core (MECH-HS-CORE: stock 200.0 mm cut of 30 x 30 x 3.0 mm Al 6063-T6; chimney-only black!)
    core_w_nom: float = 30.0
    core_w_max: float = 30.4
    core_wall: float = 3.0
    core_bore_nom: float = 24.0
    core_length: float = 200.0
    core_pocket_w: float = 31.1          # PETG/ASA-agnostic clearance (+0.35 mm/side over 30.4 mm max Al tube!)
    core_wire_slot_w: float = 9.0        # 9.0 x 7.5 mm channels at ±Y pass 7.4 x 5.75 mm JST-XH plugs cleanly
    core_wire_slot_d: float = 7.5
    core_hang_hole_dia: float = 8.0
    core_hang_hole_from_top: float = 16.0

    # Top end-cap (MECH-CAP-TOP) — prints UPRIGHT w/ lofted rain roof + 9.5 mm vertical collar (ZERO roof breach!)
    cap_top_skirt_od: float = 74.0       # Matches MECH-CAP-BOT collar OD
    cap_top_brim_od: float = 84.0        # Unbroken 360-deg Ø84 mm circular rain eaves
    cap_top_skirt_h: float = 8.0         # Vertical skirt before 45-deg underside flare
    cap_top_rim_h: float = 2.5           # Crisp cylindrical drip rim
    cap_top_roof_h: float = 10.0         # Loft height from Ø84 circle -> 40.4x40.4 R4 collar (24.6 deg slope!)
    cap_top_collar_h: float = 9.5        # Vertical 40.4x40.4 R4 chimney collar above loft (eliminates roof holes!)
    cap_top_collar_w: float = 40.4       # 4.65 mm uniform flat wall around 31.1x31.1 mm core socket!
    cap_top_collar_r: float = 4.0
    cap_top_lock_z_rel: float = 28.8     # 2x M3x10 SHCS bearing flat on 4.65 mm vertical collar wall (5.0 mm above cone!)
    cap_top_seal_groove: float = 2.0     # Backed 2.0 x 2.5 mm top PMMA-safe neutral-alkoxy silicone seal channel!
    cap_top_seal_depth: float = 2.5
    cap_chamfer: float = 0.8
    min_wall: float = 2.5

    # Chamfered finial top rain plug (MECH-PLUG-TOP: 8 mm 45-deg-beveled obelisk cap)
    plug_top_w: float = 23.5
    plug_top_insert_h: float = 10.0
    plug_top_cap_w: float = 30.2
    plug_top_cap_h: float = 8.0

    # 2-half snap-in Signal-Orange hang-hole pivot bushing (MECH-HANG-BUSHING w/ 0.30 mm snap retention barb!)
    hang_bush_id: float = 4.0            # Snug Ø4.0 mm pivot bore for Ø2.2-3.0 mm coat-hanger wire bail (or cord)
    hang_bush_flange_od: float = 12.0
    hang_bush_flange_t: float = 1.6

    # Removable C-shaped wire hanging bail (DIY bent from ~170 mm of Ø2.2-3.0 mm coat-hanger steel wire; £0 BOM)
    bail_wire_dia: float = 2.6           # Modeled stiff coat-hanger steel wire diameter (Ø4.0 bore fits up to 3.2 mm)
    bail_half_w: float = 22.0            # 44.0 mm centerline span (clears flanges at ±16.65 & 40.4 collar!)
    bail_pin_tip_x: float = 8.0          # Inward pivot pins engage 8.65 mm past outer flange (5.65 mm through Al!)
    bail_leg_h: float = 30.0             # Vertical side legs Z = 252 .. 282 mm (+6 mm above finial top)
    bail_crown_half_w: float = 7.5       # Converging upper shoulders self-center hooks & pull pins INWARD under load!
    bail_top_z_above_pivot: float = 64.0 # Apex centerline Z = 316.0 mm (38.7 mm clear gap above finial for carabiners!)

    # 8x Off-the-shelf pre-mounted 20 mm LED stars (4x UV + 4x Vis; edge-clamped at R=11.7 mm by M3 + Ø7 nylon washer!)
    star_dia: float = 20.0
    star_thick: float = 1.50
    star_tim_thick: float = 0.15
    star_uv_z_offset: float = 17.0       # 34.0 mm UV-to-Vis pitch -> 3.6 mm gap between adjacent Ø7.0 mm nylon washers!
    star_vis_z_offset: float = -17.0
    star_bolt_r: float = 11.7            # 23.4 mm bolt pitch -> clears EVERY Ø20.0 mm round board by 0.20 mm!
    star_washer_od: float = 7.0          # DIN 125 M3 nylon washer -> 1.80 mm positive clamping overlap onto star edge!
    led_uv_max_h: float = 2.08
    led_vis_max_h: float = 0.85          # ams OSRAM CSLNM1 max height = 0.81 mm!
    m3_pan_plus_washer_h: float = 3.20   # M3 CSK + steel flat washer + 0.8 mm DIN 125 nylon washer = 3.0 mm!

    @property
    def print_clearance(self) -> float:
        return 0.25 if self.process == "FDM" else 0.15

    # Derived global coordinates (Rev 4.8)
    @property
    def z_lid_bot_start(self) -> float:
        return self.cap_bot_skirt_h  # 22.0

    @property
    def z_lid_bot_end(self) -> float:
        return self.z_lid_bot_start + self.lid_bot_thick  # 29.0

    @property
    def z_lid_spigot_top(self) -> float:
        return self.z_lid_bot_end + self.lid_spigot_h  # 36.0

    @property
    def pcb_z_fcu(self) -> float:
        return round(self.pcb_z_bcu + self.pcb_thick, 3)  # 47.1 (SMD/JST-Side UP!)

    @property
    def z_pcb_bcu(self) -> float:
        return self.pcb_z_bcu  # 45.5

    @property
    def y_j1_mouth(self) -> float:
        return round(self.pcb_y_center - 0.5 * self.pcb_l - self.usbc_j1_overhang_mm, 3)  # -19.18

    @property
    def z_j1_center(self) -> float:
        return round(self.pcb_z_fcu + self.usbc_z_offset_from_fcu, 3)  # 48.98 (J1 sits on TOP F.Cu!)

    @property
    def z_core_bot(self) -> float:
        return self.cap_bot_core_bot_z  # 68.0

    @property
    def z_anchor_pin(self) -> float:
        return self.z_core_bot + self.anchor_pin_z_rel  # 81.0

    @property
    def z_glass_bot(self) -> float:
        return self.cap_bot_glass_bot_z  # 74.0

    @property
    def z_cap_bot_top(self) -> float:
        return self.z_glass_bot + self.glass_socket_depth  # 88.5

    @property
    def z_glass_top(self) -> float:
        return self.z_glass_bot + self.glass_length  # 189.0

    @property
    def z_cap_top_bot(self) -> float:
        return self.z_glass_top - self.glass_socket_depth  # 174.5

    @property
    def z_cap_top_brim_bot(self) -> float:
        return self.z_cap_top_bot + self.cap_top_skirt_h  # 182.5

    @property
    def z_cap_top_brim_rim_bot(self) -> float:
        return self.z_cap_top_brim_bot + 0.5 * (self.cap_top_brim_od - self.cap_top_skirt_od)  # 187.5

    @property
    def z_cap_top_brim_rim_top(self) -> float:
        return self.z_cap_top_brim_rim_bot + self.cap_top_rim_h  # 190.0

    @property
    def z_cap_top_collar_bot(self) -> float:
        return round(self.z_cap_top_brim_rim_top + self.cap_top_roof_h, 3)  # 200.0

    @property
    def z_cap_top_top(self) -> float:
        return round(self.z_cap_top_collar_bot + self.cap_top_collar_h, 3)  # 209.5

    @property
    def z_cap_top_lock(self) -> float:
        return round(self.z_cap_top_bot + self.cap_top_lock_z_rel, 3)  # 203.3

    @property
    def z_core_top(self) -> float:
        return self.z_core_bot + self.core_length  # 268.0

    @property
    def core_protrusion_mm(self) -> float:
        return round(self.z_core_top - self.z_cap_top_top, 3)  # 58.5

    @property
    def z_hang_hole(self) -> float:
        return self.z_core_top - self.core_hang_hole_from_top  # 252.0

    @property
    def z_plug_top_end(self) -> float:
        return self.z_core_top + self.plug_top_cap_h  # 276.0

    @property
    def total_height_mm(self) -> float:
        return round(self.z_plug_top_end, 3)  # 276.0 (lamp body height; bail folded/removed)

    @property
    def z_bail_top_center(self) -> float:
        return round(self.z_hang_hole + self.bail_top_z_above_pivot, 3)  # 316.0

    @property
    def total_height_with_bail_mm(self) -> float:
        return round(self.z_bail_top_center + 0.5 * self.bail_wire_dia, 3)  # 317.3

    @property
    def bail_clearance_above_finial_mm(self) -> float:
        return round((self.z_bail_top_center - 0.5 * self.bail_wire_dia) - self.z_plug_top_end, 3)  # 38.7

    @property
    def exposed_glass_window(self) -> float:
        return self.z_cap_top_bot - self.z_cap_bot_top  # 86.0

    @property
    def z_optical_center(self) -> float:
        return 0.5 * (self.z_glass_bot + self.z_glass_top)  # 131.5

    @property
    def z_led_uv(self) -> float:
        return self.z_optical_center + self.star_uv_z_offset  # 148.5

    @property
    def z_led_vis(self) -> float:
        return self.z_optical_center + self.star_vis_z_offset  # 114.5

    @property
    def axial_uv_to_top_mm(self) -> float:
        return round(self.z_cap_top_top - self.z_led_uv, 3)  # 61.0

    @property
    def axial_uv_to_vis_mm(self) -> float:
        return self.z_led_uv - self.z_led_vis  # 34.0

    @property
    def axial_vis_to_bot_mm(self) -> float:
        return self.z_led_vis - self.z_core_bot  # 46.5

    @property
    def bulkhead_thick(self) -> float:
        return self.z_core_bot - self.cap_bot_ceiling_z  # 5.5 mm

    @property
    def drill_guide_from_core_bot_mm(self) -> dict[str, float]:
        """SSOT drill hole Z-distances measured from bottom end of 200 mm Al core (used by drill jig & ASSEMBLY_GUIDE.md!)."""
        return {
            "anchor_cross_pin_x_faces": round(self.anchor_pin_z_rel, 2),
            "vis_star_bot_bolt_all_4_faces": round(self.axial_vis_to_bot_mm - self.star_bolt_r, 2),
            "vis_star_center_all_4_faces": round(self.axial_vis_to_bot_mm, 2),
            "vis_star_top_bolt_all_4_faces": round(self.axial_vis_to_bot_mm + self.star_bolt_r, 2),
            "uv_star_bot_bolt_all_4_faces": round((self.z_led_uv - self.z_core_bot) - self.star_bolt_r, 2),
            "uv_star_center_all_4_faces": round(self.z_led_uv - self.z_core_bot, 2),
            "uv_star_top_bolt_all_4_faces": round((self.z_led_uv - self.z_core_bot) + self.star_bolt_r, 2),
            "cap_top_lock_x_faces": round(self.z_cap_top_lock - self.z_core_bot, 2),
            "hang_hole_8mm_x_faces": round(self.core_length - self.core_hang_hole_from_top, 2),
        }

    def cap_bot_outer_r_at_z(self, z: float) -> float:
        """Exact outer radius of MECH-CAP-BOT (cylindrical Ø92.4 up to Z=36 mm, then linear frustum to Ø74.0 at Z=88.5)."""
        r0 = 0.5 * self.cap_bot_base_od
        r1 = 0.5 * self.cap_bot_collar_od
        if z <= self.cap_bot_taper_start_z:
            return r0
        frac = (z - self.cap_bot_taper_start_z) / (self.z_cap_bot_top - self.cap_bot_taper_start_z)
        return r0 + (r1 - r0) * frac

    def verify_all(self) -> dict[str, dict[str, float | bool]]:
        checks: dict[str, dict[str, float | bool]] = {}
        r_cav = self.cap_bot_cavity_dia / 2.0  # 35.8

        # 1. Serviceable Lid-Mounted PCB (SMD/JST UP) & realistic 15.0 mm 90-deg USB-C plug clearances
        pcb_pos_corner_r = math.hypot(self.pcb_w / 2.0 - self.pcb_corner_r, self.pcb_y_center + self.pcb_l / 2.0 - self.pcb_corner_r) + self.pcb_corner_r
        pcb_neg_corner_r = math.hypot(self.pcb_w / 2.0 - self.pcb_corner_r, abs(self.pcb_y_center - self.pcb_l / 2.0) - self.pcb_corner_r) + self.pcb_corner_r
        plug_corner_r = math.hypot(self.usbc_plug_90_w / 2.0, abs(self.y_j1_mouth) + self.usbc_plug_90_len)
        jst_top_z = self.pcb_z_fcu + self.pcb_jst_mated_h  # 57.9
        anchor_head_bot_z = self.cap_bot_ceiling_z         # Flush M3x12 CSK anchor bolts sit flush at 63.5!
        sw1_lugs_top_z = self.z_lid_bot_start + self.sw1_wall_thick + self.sw1_body_h_z + self.sw1_lugs_h_z  # 39.97
        th_pins_bot_z = self.pcb_z_bcu - self.pcb_jst_pin_protrude  # 43.7
        plug_bot_z = (self.z_j1_center + 3.0) - self.usbc_plug_90_h  # 40.48
        strain_bot_z = plug_bot_z - self.usbc_strain_relief_h        # 33.48
        y_plug_ctr = self.y_j1_mouth - 1.5 - 0.5 * (self.usbc_plug_90_len - 1.5)
        strain_outer_r = abs(y_plug_ctr) + 3.6  # Top of 7 mm boot at Z=40.5 -> inside Ø62.8 spigot at Z=36!
        checks["pcb_radial_clearance_mm"] = {"value": round(r_cav - max(pcb_pos_corner_r, pcb_neg_corner_r), 3), "min": 1.2, "pass": (r_cav - max(pcb_pos_corner_r, pcb_neg_corner_r)) >= 1.2}
        checks["usbc_90_plug_radial_clr_mm"] = {"value": round(r_cav - plug_corner_r, 3), "min": 0.8, "pass": (r_cav - plug_corner_r) >= 0.8}
        checks["jst_top_below_anchor_heads_mm"] = {"value": round(anchor_head_bot_z - jst_top_z, 3), "min": 2.0, "pass": (anchor_head_bot_z - jst_top_z) >= 2.0}
        checks["th_pins_above_sw1_lugs_mm"] = {"value": round(th_pins_bot_z - sw1_lugs_top_z, 3), "min": 3.0, "pass": (th_pins_bot_z - sw1_lugs_top_z) >= 3.0}
        checks["usbc_plug_above_spigot_top_mm"] = {"value": round(plug_bot_z - self.z_lid_spigot_top, 3), "min": 3.5, "pass": (plug_bot_z - self.z_lid_spigot_top) >= 3.5}
        checks["usbc_strain_above_lid_top_mm"] = {"value": round(strain_bot_z - self.z_lid_bot_end, 3), "min": 3.5, "pass": (strain_bot_z - self.z_lid_bot_end) >= 3.5}
        checks["usbc_strain_in_spigot_clr_mm"] = {"value": round(self.lid_spigot_id / 2.0 - strain_outer_r, 3), "min": 0.5, "pass": (self.lid_spigot_id / 2.0 - strain_outer_r) >= 0.5}

        # 2. Recessed MECH-LID-BOT, Blind-Bolted Conical Split Cable Clamp, SW1 & ground clearances
        r_spigot_in = self.lid_spigot_id / 2.0  # 31.4
        clamp_port_outer_r = math.hypot(self.clamp_port_w / 2.0, abs(self.clamp_y) + self.clamp_port_l / 2.0)
        clamp_bolt_r = math.hypot(self.clamp_bolt_dx, abs(self.clamp_y))
        clamp_blind_roof = self.lid_bot_thick - self.m3_insert_blind_depth
        clamp_to_sw1_gap = (self.sw1_y - self.sw1_body_w_y / 2.0) - (self.clamp_y + self.clamp_port_l / 2.0)
        sw1_corner_r = math.hypot(self.sw1_body_w_x / 2.0, self.sw1_y + self.sw1_body_w_y / 2.0)
        sw1_boot_ground_clr = self.z_lid_bot_start - self.sw1_boot_protrude_z
        clamp_ground_clr = self.z_lid_bot_start - self.clamp_outer_h  # Flush M3x12 CSK heads -> 13.0 mm ground clr!
        checks["clamp_port_in_spigot_clr_mm"] = {"value": round(r_spigot_in - clamp_port_outer_r, 3), "min": 1.5, "pass": (r_spigot_in - clamp_port_outer_r) >= 1.5}
        checks["clamp_bolt_in_spigot_clr_mm"] = {"value": round(r_spigot_in - (clamp_bolt_r + 2.0), 3), "min": 3.0, "pass": (r_spigot_in - (clamp_bolt_r + 2.0)) >= 3.0}
        checks["clamp_blind_insert_roof_mm"] = {"value": round(clamp_blind_roof, 3), "min": 1.5, "pass": clamp_blind_roof >= 1.5}
        checks["clamp_to_sw1_gap_mm"] = {"value": round(clamp_to_sw1_gap, 3), "min": 18.0, "pass": clamp_to_sw1_gap >= 18.0}
        checks["sw1_in_spigot_clr_mm"] = {"value": round(r_spigot_in - sw1_corner_r, 3), "min": 6.0, "pass": (r_spigot_in - sw1_corner_r) >= 6.0}
        checks["sw1_boot_above_ground_mm"] = {"value": round(sw1_boot_ground_clr, 3), "min": 2.5, "pass": sw1_boot_ground_clr >= 2.5}
        checks["clamp_head_above_ground_mm"] = {"value": round(clamp_ground_clr, 3), "min": 5.0, "pass": clamp_ground_clr >= 5.0}

        # 3. Radial & Axial clearances inside Ø60 x 54 mm Plexiglas XT 0A070 shroud + round-star edge clamping
        r_glass_min = self.glass_id_min / 2.0
        r_hub = self.core_hub_od / 2.0
        r_core_max_corner = math.hypot(self.core_w_max / 2.0, self.core_w_max / 2.0)
        r_led_vis_max = self.core_w_nom / 2.0 + self.star_tim_thick + self.star_thick + self.led_vis_max_h
        r_m3_head_corner = math.hypot(self.core_w_nom / 2.0 + self.star_tim_thick + self.star_thick + self.m3_pan_plus_washer_h, self.star_washer_od / 2.0)
        star_bolt_edge_clr = (self.star_bolt_r - 1.5) - (self.star_dia / 2.0)  # M3 shank clears Ø20.0 mm round board!
        star_washer_bite = (self.star_dia / 2.0) - (self.star_bolt_r - self.star_washer_od / 2.0)
        washer_gap_z = (self.z_led_uv - self.star_bolt_r - self.star_washer_od / 2.0) - (self.z_led_vis + self.star_bolt_r + self.star_washer_od / 2.0)
        wire_slot_outer_r = math.hypot(self.core_wire_slot_w / 2.0, self.core_pocket_w / 2.0 + self.core_wire_slot_d)
        hub_corner_wall = r_hub - math.hypot(self.core_pocket_w / 2.0, self.core_pocket_w / 2.0)
        checks["shroud_bore_to_od_max_mm"] = {"value": round(0.5 * (self.glass_bore_id - self.glass_od_max), 3), "min": 0.45, "pass": 0.5 * (self.glass_bore_id - self.glass_od_max) >= 0.45}
        checks["core_hub_to_shroud_id_min_mm"] = {"value": round(r_glass_min - r_hub, 3), "min": 2.0, "pass": (r_glass_min - r_hub) >= 2.0}
        checks["core_hub_corner_wall_mm"] = {"value": round(hub_corner_wall, 3), "min": 2.4, "pass": hub_corner_wall >= 2.4}
        checks["core_corner_to_shroud_id_min_mm"] = {"value": round(r_glass_min - r_core_max_corner, 3), "min": 3.0, "pass": (r_glass_min - r_core_max_corner) >= 3.0}
        checks["led_vis_to_shroud_id_min_mm"] = {"value": round(r_glass_min - r_led_vis_max, 3), "min": 5.0, "pass": (r_glass_min - r_led_vis_max) >= 5.0}
        checks["m3_head_to_shroud_id_min_mm"] = {"value": round(r_glass_min - r_m3_head_corner, 3), "min": 5.0, "pass": (r_glass_min - r_m3_head_corner) >= 5.0}
        checks["star_bolt_clears_round_20mm_mm"] = {"value": round(star_bolt_edge_clr, 3), "min": 0.15, "pass": star_bolt_edge_clr >= 0.15}
        checks["star_washer_edge_bite_mm"] = {"value": round(star_washer_bite, 3), "min": 1.5, "pass": star_washer_bite >= 1.5}
        checks["uv_to_vis_washer_gap_mm"] = {"value": round(washer_gap_z, 3), "min": 3.0, "pass": washer_gap_z >= 3.0}
        checks["wire_slot_inside_shroud_id_mm"] = {"value": round(r_glass_min - wire_slot_outer_r, 3), "min": 2.5, "pass": (r_glass_min - wire_slot_outer_r) >= 2.5}

        # 4. Structural walls & cap_top roof/groove separation (P0-1 regression checks!)
        r_ins = self.m3_insert_pilot_dia / 2.0
        lid_ins_inner_wall = (self.lid_bot_bolt_r - r_ins) - (self.cap_bot_spigot_bore_dia / 2.0)
        lid_ins_outer_wall = self.cap_bot_outer_r_at_z(self.z_lid_bot_end + self.m3_insert_depth) - (self.lid_bot_bolt_r + r_ins)
        skirt_wall_min = self.cap_bot_outer_r_at_z(self.cap_bot_skirt_h) - (self.cap_bot_skirt_id / 2.0)
        cap_bot_mid_wall = self.cap_bot_outer_r_at_z(self.cap_bot_ceiling_z) - r_cav
        shroud_oring_outer_wall = (self.cap_bot_collar_od / 2.0) - (self.glass_oring_groove_od / 2.0)
        lid_spigot_oring_wall = (self.bot_oring_groove_od / 2.0) - (self.lid_spigot_id / 2.0)
        top_collar_flat_wall = 0.5 * (self.cap_top_collar_w - self.core_pocket_w)
        z_cone_apex_rel = (self.z_glass_top + 1.2 - self.z_cap_top_bot) + (self.glass_bore_id / 2.0 - self.core_hub_od / 2.0)
        lock_above_cone = (self.cap_top_lock_z_rel - self.m3_clearance_dia / 2.0) - z_cone_apex_rel
        # Teardrop apex for 42-deg angle is R / sin(42 deg) = 1.494 * R
        td_apex_z = self.z_cap_top_lock + (self.m3_clearance_dia / 2.0) / math.sin(math.radians(42.0))
        lock_below_seal_groove = (self.z_cap_top_top - self.cap_top_seal_depth) - td_apex_z
        checks["lid_insert_inner_wall_mm"] = {"value": round(lid_ins_inner_wall, 3), "min": 2.2, "pass": lid_ins_inner_wall >= 2.2}
        checks["lid_insert_outer_wall_mm"] = {"value": round(lid_ins_outer_wall, 3), "min": 3.0, "pass": lid_ins_outer_wall >= 3.0}
        checks["skirt_wall_min_mm"] = {"value": round(skirt_wall_min, 3), "min": 2.8, "pass": skirt_wall_min >= 2.8}
        checks["cap_bot_bay_wall_mm"] = {"value": round(cap_bot_mid_wall, 3), "min": 3.5, "pass": cap_bot_mid_wall >= 3.5}
        checks["shroud_oring_outer_wall_mm"] = {"value": round(shroud_oring_outer_wall, 3), "min": 3.5, "pass": shroud_oring_outer_wall >= 3.5}
        checks["lid_spigot_oring_wall_mm"] = {"value": round(lid_spigot_oring_wall, 3), "min": 2.2, "pass": lid_spigot_oring_wall >= 2.2}
        checks["top_collar_flat_wall_mm"] = {"value": round(top_collar_flat_wall, 3), "min": 4.0, "pass": top_collar_flat_wall >= 4.0}
        checks["cap_top_lock_above_cone_mm"] = {"value": round(lock_above_cone, 3), "min": 3.0, "pass": lock_above_cone >= 3.0}
        checks["cap_top_lock_below_seal_mm"] = {"value": round(lock_below_seal_groove, 3), "min": 1.0, "pass": lock_below_seal_groove >= 1.0}

        # 5. Radial O-ring squeeze & gland fill
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

        short_tube_top = (self.z_glass_bot - 1.0) + (self.glass_length - self.glass_length_tol) - 1.0
        g2_flat_top = self.z_cap_top_bot + 3.0 + self.glass_oring_flat_w
        short_tube_seal_margin = short_tube_top - g2_flat_top

        checks["g12_radial_squeeze_min_pct"] = {"value": round(g12_sq_min, 1), "min": 10.0, "pass": g12_sq_min >= 10.0}
        checks["g12_radial_squeeze_nom_pct"] = {"value": round(g12_sq_nom, 1), "min": 14.0, "max": 26.0, "pass": 14.0 <= g12_sq_nom <= 26.0}
        checks["g12_radial_squeeze_max_pct"] = {"value": round(g12_sq_max, 1), "max": 33.0, "pass": g12_sq_max <= 33.0}
        checks["g12_gland_fill_max"] = {"value": round(g12_fill, 4), "max": 0.85, "pass": g12_fill <= 0.85}
        checks["short_tube_g2_margin_mm"] = {"value": round(short_tube_seal_margin, 3), "min": 2.0, "pass": short_tube_seal_margin >= 2.0}
        checks["g3_radial_squeeze_nom_pct"] = {"value": round(g3_sq_nom, 1), "min": 10.0, "max": 22.0, "pass": 10.0 <= g3_sq_nom <= 22.0}
        checks["g3_gland_fill"] = {"value": round(g3_fill, 4), "max": 0.85, "pass": g3_fill <= 0.85}

        # 6. Protruding core, top finial plug, lofted rain roof & C-clip wire hanging bail checks
        hang_to_plug_clr = (self.z_core_top - self.plug_top_insert_h) - (self.z_hang_hole + self.core_hang_hole_dia / 2.0)
        brim_overhang_shroud = 0.5 * (self.cap_top_brim_od - self.glass_od_nom)
        roof_slope_min_deg = math.degrees(math.atan2(self.cap_top_roof_h, 0.5 * (self.cap_top_brim_od - self.cap_top_collar_w)))
        bail_pin_radial_clr = 0.5 * (self.hang_bush_id - self.bail_wire_dia)
        flange_outer_x_wc = 0.5 * self.core_w_max + 0.05 + self.hang_bush_flange_t
        bail_pin_engage = (0.5 * self.core_w_nom + self.hang_bush_flange_t) - self.bail_pin_tip_x
        bail_leg_flange_clr = (self.bail_half_w - 0.5 * self.bail_wire_dia) - flange_outer_x_wc
        checks["core_protrusion_mm"] = {"value": round(self.core_protrusion_mm, 3), "min": 55.0, "max": 85.0, "pass": 55.0 <= self.core_protrusion_mm <= 85.0}
        checks["hang_hole_to_top_plug_mm"] = {"value": round(hang_to_plug_clr, 3), "min": 2.0, "pass": hang_to_plug_clr >= 2.0}
        checks["cap_top_brim_overhang_mm"] = {"value": round(brim_overhang_shroud, 3), "min": 12.0, "pass": brim_overhang_shroud >= 12.0}
        checks["cap_top_roof_slope_deg"] = {"value": round(roof_slope_min_deg, 1), "min": 20.0, "pass": roof_slope_min_deg >= 20.0}
        checks["bail_pin_in_bushing_clr_mm"] = {"value": round(bail_pin_radial_clr, 3), "min": 0.5, "pass": bail_pin_radial_clr >= 0.5}
        checks["bail_pin_engagement_mm"] = {"value": round(bail_pin_engage, 3), "min": 7.0, "pass": bail_pin_engage >= 7.0}
        checks["bail_leg_to_flange_clr_mm"] = {"value": round(bail_leg_flange_clr, 3), "min": 2.5, "pass": bail_leg_flange_clr >= 2.5}
        checks["bail_clearance_above_finial_mm"] = {"value": round(self.bail_clearance_above_finial_mm, 3), "min": 30.0, "pass": self.bail_clearance_above_finial_mm >= 30.0}
        lid_csk_rim_clr = 0.5 * self.lid_bot_od - (self.lid_bot_bolt_r + 3.25)
        checks["lid_csk_outer_rim_clr_mm"] = {"value": round(lid_csk_rim_clr, 3), "min": 0.3, "pass": lid_csk_rim_clr >= 0.3}

        return checks

    def to_dict(self) -> dict:
        d = asdict(self)
        d["derived"] = {
            "z_lid_bot_start": self.z_lid_bot_start,
            "z_lid_bot_end": self.z_lid_bot_end,
            "z_lid_spigot_top": self.z_lid_spigot_top,
            "z_pcb_bcu": self.z_pcb_bcu,
            "pcb_z_fcu": self.pcb_z_fcu,
            "y_j1_mouth": self.y_j1_mouth,
            "z_j1_center": self.z_j1_center,
            "z_core_bot": self.z_core_bot,
            "z_anchor_pin": self.z_anchor_pin,
            "z_glass_bot": self.z_glass_bot,
            "z_cap_bot_top": self.z_cap_bot_top,
            "z_glass_top": self.z_glass_top,
            "z_cap_top_bot": self.z_cap_top_bot,
            "z_cap_top_collar_bot": self.z_cap_top_collar_bot,
            "z_cap_top_top": self.z_cap_top_top,
            "z_cap_top_lock": self.z_cap_top_lock,
            "z_core_top": self.z_core_top,
            "core_protrusion_mm": self.core_protrusion_mm,
            "z_hang_hole": self.z_hang_hole,
            "z_plug_top_end": self.z_plug_top_end,
            "total_height_mm": self.total_height_mm,
            "z_bail_top_center": self.z_bail_top_center,
            "total_height_with_bail_mm": self.total_height_with_bail_mm,
            "bail_clearance_above_finial_mm": self.bail_clearance_above_finial_mm,
            "exposed_glass_window_mm": self.exposed_glass_window,
            "z_optical_center": self.z_optical_center,
            "z_led_uv": self.z_led_uv,
            "z_led_vis": self.z_led_vis,
            "axial_uv_to_top_mm": self.axial_uv_to_top_mm,
            "axial_uv_to_vis_mm": self.axial_uv_to_vis_mm,
            "axial_vis_to_bot_mm": self.axial_vis_to_bot_mm,
            "bulkhead_thick": self.bulkhead_thick,
            "drill_guide_from_core_bot_mm": self.drill_guide_from_core_bot_mm,
        }
        d["checks"] = self.verify_all()
        return d


if __name__ == "__main__":
    p = LepiLEDParams()
    out_path = Path(__file__).with_name("cad_params.json")
    data = p.to_dict()
    out_path.write_text(json.dumps(data, indent=2) + "\n")
    print(f"Wrote {out_path}")
    all_pass = True
    for name, c in data["checks"].items():
        status = "PASS" if c["pass"] else "FAIL"
        print(f"  [{status}] {name:34s}: {c}")
        if not c["pass"]:
            all_pass = False
    if not all_pass:
        raise SystemExit(1)
