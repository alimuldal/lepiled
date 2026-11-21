#!/usr/bin/env python3
"""
Parametric Mechanical Specification & Clearance Audit — LepiLED DIY Maxi Switch.

Single source of truth for all mechanical dimensions, tolerances, drill coordinates,
O-ring gland calculations, and clearance assertions. Written to cad_params.json.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
import math
from pathlib import Path
from typing import Literal


@dataclass(frozen=True)
class LepiLEDParams:
    process: Literal["FDM", "SLS"] = "FDM"

    # 1. Bottom Tapered Funnel Nosecone (MECH-CAP-BOT: Z = 0.0 .. 34.0 mm, open screened chimney inlet)
    cap_bot_tip_od: float = 40.0         # Bottom nosecone tip OD (4.01 mm corner wall at Z = 6.0 mm)
    cap_bot_collar_od: float = 71.0      # Upper shroud collar OD (2.80 mm solid wall behind 60x3.5 O-ring)
    cap_bot_cone_h: float = 15.5         # Exact 45.0-deg self-supporting frustum Z = 0.0 .. 15.5 mm
    cap_bot_core_bot_z: float = 6.0      # Core seat ledge around 22 x 22 mm screened chimney air inlet
    cap_bot_inlet_w: float = 22.0        # Open rounded-square chimney inlet at nosecone tip (R = 3 mm)
    cap_bot_bolt_z: float = 12.5         # Single M4 x 50 mm A2 stainless cross-bolt (6.5 mm from core bottom)
    cap_bot_glass_bot_z: float = 19.5    # Bottom shroud seat (14.5 mm socket -> exposed window starts at Z = 34.0 mm)
    core_hub_od: float = 49.0            # Solid R = 24.5 mm central hub in both shroud sockets

    # 2. Extruded Clear XT PMMA Shroud (MECH-TUBE-1: Ø60 x 54 x 3.0 x 115 mm)
    glass_od_nom: float = 60.0
    glass_id_nom: float = 54.0
    glass_od_max: float = 60.6           # Extruded XT PMMA ovality (+0.6 / -0.8 mm)
    glass_od_min: float = 59.2
    glass_id_min: float = 53.5
    glass_length: float = 115.0
    glass_length_tol: float = 2.0        # +/-2.0 mm cut tolerance (113.0 .. 117.0 mm)
    glass_socket_depth: float = 14.5
    glass_bore_id: float = 61.6          # 0.50 mm/side slip clearance over 60.6 mm oval tube

    # Shroud radial bore O-rings (MECH-GASKET-1..2: 60 x 3.5 mm soft VMQ50/60)
    glass_oring_groove_od: float = 65.40 # Gland = 2.70 mm nom -> 22.9% nom / 11.4-31.4% squeeze across ovality
    glass_oring_cs: float = 3.5
    glass_oring_flat_w: float = 4.6

    # 3. Central Open-Chimney Bare Mill Al Core (MECH-HS-CORE: 30 x 30 x 2.0 mm x 300.0 mm 6063-T6)
    core_w_nom: float = 30.0
    core_w_max: float = 30.4
    core_wall: float = 2.0               # 2.0 mm wall -> 26 x 26 mm open chimney bore, 181 g mass, zero tapping
    core_bore_nom: float = 26.0
    core_length: float = 300.0           # Standard UK 300 mm stock cut (zero sawing)
    core_pocket_w: float = 31.1          # +0.35 mm/side slip clearance over 30.4 mm max Al tube
    core_wire_slot_w: float = 9.0        # 9.0 x 7.5 mm channels at +/-Y passing pre-crimped JST-XH plugs
    core_wire_slot_d: float = 7.5
    core_bolt_hole_dia: float = 4.5      # 4x plain Ø4.5 mm clearance holes (2x bottom Z_rel=6.5, 2x top Z_rel=284.0)
    core_hang_hole_from_top: float = 16.0

    # 4. Top-Head Electronics Chassis (MECH-TOP-BASE: Z = 120.0 .. 220.5 mm, prints upright)
    top_base_collar_od: float = 71.0     # Lower shroud collar OD matching MECH-CAP-BOT
    top_base_flare_bot_z: float = 133.5  # Flare starts 4.0 mm above MECH-GASKET-2 groove
    top_base_port_od: float = 94.0       # Side-port ring OD (R = 47.0 mm; 45-deg flare Z = 133.5 .. 145.0 mm)
    top_base_port_h: float = 26.0        # Z = 145.0 .. 171.0 mm (accommodates 18-20 mm 90-deg USB-C plugs & draining cove)
    top_base_port_id: float = 78.0       # R = 39.0 mm dry bay (8.0 mm port wall -> >= 4.0 mm behind blind clamp inserts)
    top_base_deck_od: float = 98.0       # 2.0 mm 45-deg top lip (R = 49.0 mm) backing axial O-ring groove
    top_base_ear_r: float = 51.0         # 4x diagonal 45-deg gusseted bolt ears for M3 x 12 CSK
    top_base_ear_boss_r: float = 5.5     # 2.25 mm solid rim around Ø6.5 mm CSK seat (R_max = 56.5 mm)
    top_base_ear_h: float = 8.0          # Z = 163.0 .. 171.0 mm

    # Axial face O-ring groove on Z = 171.0 mm deck (MECH-GASKET-3: 88 x 2.5 mm soft VMQ50)
    top_oring_id: float = 88.0           # Standard 88 x 2.5 mm VMQ50 (mean dia 90.5 mm vs groove mean 90.6 mm)
    top_oring_cs: float = 2.5
    top_oring_groove_r_in: float = 43.6  # Groove R = 43.6 .. 47.0 mm (width = 3.4 mm)
    top_oring_groove_w: float = 3.4
    top_oring_groove_depth: float = 1.88 # 24.8% axial squeeze, 76.8% gland fill

    # 5. Committed Ordered Driver PCB (36.0 x 46.0 x 1.6 mm) Mounted Vertically on +X Core Face
    #    Board local (bx, by, bz_from_fcu) -> Global (X = pcb_x_fcu + bz, Y = bx, Z = pcb_z_center + by)
    #    Captive M3 hex nuts in ±Y stanchions set a 5.5 mm B.Cu->Al core gap (5.3 mm WC) with a
    #    15.6 x 15.6 mm captive thermal-bridge chute behind U1/U2 (1.0 mm silicone pads + 15x15x0.5 mm brass shims)!
    pcb_w: float = 36.0                  # Along global Y (-18.0 .. +18.0 mm)
    pcb_l: float = 46.0                  # Along global Z (Z = 174.5 .. 220.5 mm, center = 197.5 mm)
    pcb_thick: float = 1.6
    pcb_corner_r: float = 2.0
    pcb_x_bcu: float = 20.5              # B.Cu face (5.50 mm nom / 5.30 mm WC from anodized Al core)
    pcb_z_center: float = 197.5          # Bottom edge Z = 174.5 (above deck 171.0 -> open-air J1 mating), top Z = 220.5
    pcb_smd_max_h: float = 4.5           # L1/L2 SRN6045 outward along +X
    pcb_jst_mated_h: float = 9.8         # J2..J4 JST-XH mated outward along +X (X = 22.1 .. 31.9 mm)
    pcb_jst_pin_protrude: float = 1.8    # TH pins inward along -X behind B.Cu (X = 18.7 .. 20.5 -> 1.65 mm clear of baffle)
    pcb_hole_y: float = 14.0             # H1..H4 at Y = ±14.0 mm, Z = pcb_z_center ± 19.0 mm (178.5 & 216.5 mm)
    pcb_hole_z: float = 19.0
    pcb_hole_drill: float = 3.2          # M3 NPTH clearance drill on ordered board
    pcb_hole_keepout: float = 6.2
    pcb_standoff_tip_od: float = 6.0     # 0.6 mm stepped landing pad inside Ø6.2 mm B.Cu keepout
    pcb_standoff_body_od: float = 9.0    # Stanchion width along Y housing side-entry captive M3 hex nut pockets
    pcb_nut_af: float = 5.5              # Standard DIN 934 M3 hex nut across flats (pocket height 5.80 mm)
    pcb_nut_thick: float = 2.4           # Standard DIN 934 M3 hex nut thickness (pocket width 2.60 mm at X = 16.55..19.15)
    pcb_thermal_win_w: float = 15.6      # Captive chute width along ±Y for 15 x 15 x 0.5 mm brass shims + 1 mm silicone pads
    pcb_thermal_win_z_bot: float = 199.0 # Captive chute bottom shelf (3.0 mm above J4 pins, centered under U1/U2 at Z=207.4)
    pcb_thermal_win_h: float = 15.4      # Straight chute side walls Z = 199.0 .. 214.4 mm + 45-deg roof to Z = 222.2 mm
    core_sleeve_wall: float = 1.5        # Solid 1.5 mm insulating barrier at X = 15.55 .. 17.05 mm behind J1 & J4 TH pins

    # 6. Standard Left/Right 90-deg USB-C Plug & Fixed Compressing Split Cable Clamp (+Y port)
    usbc_j1_overhang_mm: float = 3.18    # GCT USB4085 mouth below bottom PCB edge (Z_mouth = 171.32 mm)
    usbc_x_offset_from_fcu: float = 1.88 # J1 center X = 25.6 + 1.88 = +27.48 mm
    usbc_mating_depth_mm: float = 4.55
    usbc_exposed_tongue_mm: float = 2.10 # Real GCT USB4085 exposed plug tongue below J1 mouth
    usbc_plug_90_len: float = 18.0       # Realistic 18.0 mm commercial left/right 90-deg plug below J1 mouth
    usbc_plug_90_thick_x: float = 8.5    # Along X
    usbc_plug_90_w_y: float = 13.2       # Along Y (exits along +Y)
    usbc_strain_relief_h: float = 7.0    # Molded boot extending along +Y
    clamp_z: float = 156.5               # Aligned with 90-deg plug cable exit inside Z = 145.0 .. 171.0 ring
    clamp_port_w: float = 16.0           # Along X: passes intact straight charger-end USB-C plug outward cleanly
    clamp_port_h: float = 17.0           # 45-deg pitched gable roof Z = 148.0 .. 165.0 mm
    clamp_bolt_dx: float = 13.0          # 2x M3 x 14 pan-head screws in X-slotted flange into blind M3x5 inserts
    clamp_standoff_y: float = 1.2        # 1.2 mm axial standoff so 45-deg wedges actually drive radial compression
    clamp_flange_t: float = 6.0          # Outer face at Y = 47.0 + 1.2 + 6.0 = 54.2 mm (4.8 mm inside R = 59 eaves)
    clamp_grommet_len: float = 10.5      # Full cylindrical chamber fitting 10.0 mm slit Ø8 x Ø4 silicone sleeve
    clamp_grommet_id: float = 7.4        # Compresses Ø8.0 mm silicone sleeve radially onto Ø4.0-4.5 mm cable
    clamp_cable_dia: float = 4.5

    # 7. Side-Mounted Recessed SW1 Toggle Switch (-X draining cove, sheltered inside -X visor brow)
    sw1_z: float = 155.5                 # Centered in widened 32 mm, 18-deg outward-draining -X cove
    sw1_recess_x: float = 5.5            # Recessed 5.5 mm inward from R = 47.0 ring -> face at X = -41.5 mm
    sw1_cove_w: float = 32.0             # Gloved-finger access width along ±Y
    sw1_cove_slope_deg: float = 18.0     # Outward-downward cove floor slope preventing water pooling
    sw1_hole_dia: float = 6.50           # True round Ø6.50 mm bore (360-deg flat sealing land for 759D02000 boot)
    sw1_wall_thick: float = 2.5          # Solid wall X = -41.5 .. -39.0 mm + keyed internal anti-rotation pocket
    sw1_body_w_y: float = 12.70          # Along Y = 3-terminal toggle throw axis
    sw1_body_h_z: float = 11.43          # Along Z = 2-pole width
    sw1_body_d_x: float = 10.67          # Inward along +X (-39.0 .. -28.33 mm)
    sw1_lugs_d_x: float = 4.80           # Lugs reach X = -23.53 mm (8.33 mm clear of worst-case 30.4 mm Al core)
    sw1_boot_protrude_x: float = 18.6    # Conservative envelope for C&K 759D02000 (16.7 mm nominal)
    sw1_boot_od: float = 13.3
    cap_top_sw_visor_x: float = 63.5     # Matching -X rain-hood visor brow (+4.5 mm past R = 59.0 eaves)

    # 8. Downward-Facing Sheltered IP68 ePTFE Breather Vent (-Y bay floor through 45-deg flare underside)
    vent_floor_y: float = -33.8          # Flat horizontal dry-bay floor mount (0.45 mm inside R=39 wall) for Ø8 mm ePTFE patch
    vent_hole_dia: float = 3.5           # 35-deg downward-outward gravity-draining bore (exits flare underside at Z=136.9)
    vent_pocket_dia: float = 9.5
    vent_pocket_depth: float = 0.8

    # 9. Unbroken White Umbrella Rain Bell (MECH-CAP-TOP: Z = 171.0 .. 257.0 mm, prints upright)
    cap_top_bore_id: float = 85.0        # R = 42.5 mm straight bore (>= 6.7 mm behind J2/J3 for silicone wire bends)
    cap_top_bell_od: float = 91.2        # R = 45.6 mm vertical bell OD (3.1 mm solid wall)
    cap_top_eaves_od: float = 118.0      # R = 59.0 mm overhanging rain eaves (12.0 mm porch over R_port = 47.0)
    cap_top_eaves_h: float = 10.0        # Z = 171.0 .. 181.0 mm (4x M3x5 inserts, 1.4 mm drip kerf, +Y C-clip)
    cap_top_eaves_taper_h: float = 13.4  # Exact 45.0-deg top slope R = 59.0 -> 45.6 mm (Z = 181.0 .. 194.4 mm)
    cap_top_ceil_cone_z: float = 219.0   # Internal <=44-deg self-supporting Circle->Square ceiling loft
    cap_top_roof_bot_z: float = 232.0    # Outer rain roof start (Ø91.2 mm)
    cap_top_roof_h: float = 15.0         # Loft height Ø91.2 -> 40.4 x 40.4 R4 collar (Z = 232.0 .. 247.0, 30.6 deg)
    cap_top_collar_h: float = 10.0       # Vertical 40.4 x 40.4 R4 chimney collar (Z = 247.0 .. 257.0, zero side holes)
    cap_top_collar_w: float = 40.4       # 4.65 mm uniform flat wall around 31.1 x 31.1 mm core socket
    cap_top_collar_r: float = 4.0
    cap_top_seal_groove: float = 2.5     # Backed 2.5 x 3.0 mm top neutral-sealant V-groove (chamfered top lip)
    cap_top_seal_depth: float = 3.0
    d12_local_bx: float = 16.0           # Exact KiCad D12 position on driver_pcb for translucent 0.6 mm internal dimple
    d12_local_by: float = -6.6
    d12_skin_thick: float = 0.60         # Unbroken outer white skin thickness opposite D12 (red 20 V PD glow)
    min_wall: float = 2.5

    # 10. M3 Brass Inserts & Fasteners (10x identical M3 x 5.0 inserts, 10x M3 screws, 2x M4 x 50 SS bolts)
    m3_clearance_dia: float = 3.4
    m3_insert_pilot_dia: float = 4.0
    m3_insert_depth: float = 6.5         # 5.0 mm insert + 1.5 mm ooze pocket
    m3_insert_blind_depth: float = 6.2   # In 8.0 mm +Y port wall (>= 4.0 mm solid dry-bay wall at X = ±13)
    m4_bolt_len: float = 50.0            # 2x identical M4 x 50 mm A2 stainless bolts + nyloc nuts (bottom & top)

    # 11. Open-Chimney Ventilated Rain Finial (MECH-PLUG-TOP: Z = 285.0 .. 324.0 mm, prints inverted)
    plug_top_leg_w: float = 25.4         # 4 corner legs slipping inside 26.0 x 26.0 mm Al bore (0.30 mm/side clearance)
    plug_top_insert_h: float = 21.0      # Z = 285.0 .. 306.0 mm, cross-pinned at Z = 290.0 mm by top M4 x 50 bolt
    plug_top_vent_h: float = 9.0         # 4x open side exhaust windows Z = 306.0 .. 315.0 mm (5.18 cm^2 open area)
    plug_top_hood_w: float = 38.0        # Overhanging 38 x 38 mm rain hood (6.0 mm overhang over 26 mm bore)
    plug_top_hood_h: float = 9.0         # Z = 315.0 .. 324.0 mm (45-deg pitched roof 38 -> 26 mm)

    # 12. 8x Convoy 20 mm Cu DTP LED Stars (bonded with 2-part thermal epoxy -> zero core holes in optical zone)
    star_dia: float = 20.0
    star_thick: float = 1.50
    star_tim_thick: float = 0.10         # 2-part thermal epoxy bondline (Arctic Alumina / MG 8329TFS)
    star_uv_z_offset: float = 17.0       # 34.0 mm UV-to-Vis pitch
    star_vis_z_offset: float = -17.0
    led_uv_max_h: float = 2.08
    led_vis_max_h: float = 0.85

    @property
    def print_clearance(self) -> float:
        return 0.25 if self.process == "FDM" else 0.15

    # Derived Global Z & Coordinate Datums
    @property
    def z_core_bot(self) -> float:
        return self.cap_bot_core_bot_z  # 6.0

    @property
    def z_bot_bolt(self) -> float:
        return self.cap_bot_bolt_z  # 12.5 (Z_rel = 6.5 mm from core bottom)

    @property
    def z_glass_bot(self) -> float:
        return self.cap_bot_glass_bot_z  # 19.5

    @property
    def z_cap_bot_top(self) -> float:
        return self.z_glass_bot + self.glass_socket_depth  # 34.0

    @property
    def z_glass_top(self) -> float:
        return self.z_glass_bot + self.glass_length  # 134.5

    @property
    def z_top_base_bot(self) -> float:
        return self.z_glass_top - self.glass_socket_depth  # 120.0

    @property
    def top_base_flare_h(self) -> float:
        return 0.5 * (self.top_base_port_od - self.top_base_collar_od)  # 11.5 (exact 45-deg flare)

    @property
    def z_top_base_port_bot(self) -> float:
        return self.top_base_flare_bot_z + self.top_base_flare_h  # 145.0

    @property
    def z_top_base_deck_top(self) -> float:
        return self.z_top_base_port_bot + self.top_base_port_h  # 171.0

    @property
    def pcb_x_fcu(self) -> float:
        return round(self.pcb_x_bcu + self.pcb_thick, 3)  # 25.6

    @property
    def z_pcb_bot(self) -> float:
        return self.pcb_z_center - 0.5 * self.pcb_l  # 174.5

    @property
    def z_pcb_top(self) -> float:
        return self.pcb_z_center + 0.5 * self.pcb_l  # 220.5

    @property
    def z_j1_mouth(self) -> float:
        return round(self.z_pcb_bot - self.usbc_j1_overhang_mm, 3)  # 171.32

    @property
    def x_j1_center(self) -> float:
        return round(self.pcb_x_fcu + self.usbc_x_offset_from_fcu, 3)  # 27.48

    @property
    def z_d12(self) -> float:
        return round(self.pcb_z_center + self.d12_local_by, 3)  # 190.9

    @property
    def z_cap_top_bot(self) -> float:
        return self.z_top_base_deck_top  # 171.0

    @property
    def z_cap_top_eaves_top(self) -> float:
        return self.z_cap_top_bot + self.cap_top_eaves_h  # 181.0

    @property
    def z_cap_top_collar_bot(self) -> float:
        return self.cap_top_roof_bot_z + self.cap_top_roof_h  # 247.0

    @property
    def z_cap_top_top(self) -> float:
        return self.z_cap_top_collar_bot + self.cap_top_collar_h  # 257.0

    @property
    def z_core_top(self) -> float:
        return self.z_core_bot + self.core_length  # 306.0

    @property
    def core_protrusion_mm(self) -> float:
        return self.z_core_top - self.z_cap_top_top  # 49.0

    @property
    def z_hang_hole(self) -> float:
        return self.z_core_top - self.core_hang_hole_from_top  # 290.0

    @property
    def z_plug_top_end(self) -> float:
        return self.z_core_top + self.plug_top_vent_h + self.plug_top_hood_h  # 324.0

    @property
    def total_height_mm(self) -> float:
        return self.z_plug_top_end  # 324.0

    @property
    def exposed_glass_window(self) -> float:
        return self.z_top_base_bot - self.z_cap_bot_top  # 86.0

    @property
    def z_optical_center(self) -> float:
        return 0.5 * (self.z_cap_bot_top + self.z_top_base_bot)  # 77.0

    @property
    def z_led_uv(self) -> float:
        return self.z_optical_center + self.star_uv_z_offset  # 94.0

    @property
    def z_led_vis(self) -> float:
        return self.z_optical_center + self.star_vis_z_offset  # 60.0

    @property
    def axial_uv_to_top_mm(self) -> float:
        return self.z_cap_top_top - self.z_led_uv  # 163.0

    @property
    def axial_uv_to_vis_mm(self) -> float:
        return self.z_led_uv - self.z_led_vis  # 34.0

    @property
    def drill_guide_from_core_bot_mm(self) -> dict[str, float]:
        """Al-core drill coordinates measured from core ends (only 4 plain Ø4.5 mm holes total, zero tapping)."""
        zb = self.z_core_bot
        return {
            "bottom_m4_bolt_from_bot_mm": round(self.z_bot_bolt - zb, 2),             # 6.5
            "vis_star_center_from_bot_mm": round(self.z_led_vis - zb, 2),             # 54.0 (epoxy alignment mark)
            "uv_star_center_from_bot_mm": round(self.z_led_uv - zb, 2),               # 88.0 (epoxy alignment mark)
            "top_m4_hang_bolt_from_bot_mm": round(self.z_hang_hole - zb, 2),          # 284.0
            "top_m4_hang_bolt_from_top_mm": round(self.core_hang_hole_from_top, 2),   # 16.0
        }

    def verify_all(self) -> dict[str, dict]:
        checks: dict[str, dict] = {}

        # 1. Compact open-chimney bottom nosecone checks
        cone_angle_deg = math.degrees(math.atan2(0.5 * (self.cap_bot_collar_od - self.cap_bot_tip_od), self.cap_bot_cone_h))
        nose_r_at_core = 0.5 * self.cap_bot_tip_od + self.z_core_bot * math.tan(math.radians(cone_angle_deg))
        nose_core_corner_wall = nose_r_at_core - 0.5 * self.core_pocket_w * math.sqrt(2.0)
        collar_oring_wall = 0.5 * (self.cap_bot_collar_od - self.glass_oring_groove_od)
        bot_bolt_al_edge = (self.z_bot_bolt - self.z_core_bot) - 0.5 * self.core_bolt_hole_dia
        inlet_area_cm2 = (self.cap_bot_inlet_w ** 2 - (4.0 - math.pi) * 3.0 ** 2) / 100.0
        checks["funnel_bot_height_le_35mm"] = {"value": round(self.z_cap_bot_top, 2), "max": 35.0, "pass": self.z_cap_bot_top <= 35.0}
        checks["funnel_bot_tip_od_le_42mm"] = {"value": round(self.cap_bot_tip_od, 2), "max": 42.0, "pass": self.cap_bot_tip_od <= 42.0}
        checks["funnel_bot_cone_angle_le_46deg"] = {"value": round(cone_angle_deg, 2), "max": 46.0, "pass": cone_angle_deg <= 46.0}
        checks["nose_core_corner_wall_mm"] = {"value": round(nose_core_corner_wall, 3), "min": 2.5, "pass": nose_core_corner_wall >= 2.5}
        checks["shroud_collar_oring_wall_mm"] = {"value": round(collar_oring_wall, 3), "min": 2.5, "pass": collar_oring_wall >= 2.5}
        checks["bot_m4_bolt_al_edge_mm"] = {"value": round(bot_bolt_al_edge, 3), "min": 4.0, "pass": bot_bolt_al_edge >= 4.0}
        checks["chimney_inlet_area_cm2"] = {"value": round(inlet_area_cm2, 2), "min": 4.0, "pass": inlet_area_cm2 >= 4.0}
        checks["vis_star_height_from_tip_mm"] = {"value": round(self.z_led_vis, 2), "max": 65.0, "pass": self.z_led_vis <= 65.0}

        # 2. Vertical driver_pcb (+X face) & top-bay clearances inside Ø85.0 mm MECH-CAP-TOP bell
        r_bell = 0.5 * self.cap_top_bore_id  # 42.5 mm
        pcb_fcu_r = math.hypot(self.pcb_x_fcu, 0.5 * self.pcb_w)
        l12_r = math.hypot(self.pcb_x_fcu + self.pcb_smd_max_h, 16.6)
        jst_corner_r = math.hypot(self.pcb_x_fcu + self.pcb_jst_mated_h, 8.9)
        jst_wire_r = math.hypot(self.pcb_x_fcu + self.pcb_jst_mated_h, 5.2)
        core_sleeve_x = 0.5 * self.core_pocket_w + self.core_sleeve_wall  # 17.05
        th_pin_x = self.pcb_x_bcu - self.pcb_jst_pin_protrude            # 18.70
        pcb_air_gap_to_core = th_pin_x - core_sleeve_x                   # 1.65 mm to plastic barrier (3.50 mm to WC Al)
        pcb_nut_back_wall = 1.00                                         # X = 15.55 .. 16.55 mm behind captive M3 nut
        pcb_nut_front_wall = self.pcb_x_bcu - (0.5 * self.core_pocket_w + pcb_nut_back_wall + 2.60)  # 1.35 mm front wall
        pcb_thermal_gap_wc = self.pcb_x_bcu - 0.5 * self.core_w_max      # 5.30 mm WC (5.50 mm nom)
        usbc_plug_to_baffle = (self.x_j1_center - 0.5 * self.usbc_plug_90_thick_x) - core_sleeve_x   # 2.68 mm
        j23_top_z = self.pcb_z_center + 19.2 + 2.9                       # 219.6 mm
        cone_z_at_jst = self.cap_top_ceil_cone_z + (r_bell - jst_corner_r)
        cone_z_at_pcb = self.cap_top_ceil_cone_z + (r_bell - pcb_fcu_r)

        checks["pcb_fcu_radial_clr_mm"] = {"value": round(r_bell - pcb_fcu_r, 3), "min": 8.0, "pass": (r_bell - pcb_fcu_r) >= 8.0}
        checks["pcb_l12_radial_clr_mm"] = {"value": round(r_bell - l12_r, 3), "min": 6.0, "pass": (r_bell - l12_r) >= 6.0}
        checks["pcb_jst_wire_bend_clr_mm"] = {"value": round(r_bell - jst_wire_r, 3), "min": 6.5, "pass": (r_bell - jst_wire_r) >= 6.5}
        checks["pcb_th_pins_air_gap_to_baffle_mm"] = {"value": round(pcb_air_gap_to_core, 3), "min": 1.2, "pass": pcb_air_gap_to_core >= 1.2}
        checks["pcb_nut_back_wall_mm"] = {"value": round(pcb_nut_back_wall, 3), "min": 0.8, "pass": pcb_nut_back_wall >= 0.8}
        checks["pcb_nut_front_wall_mm"] = {"value": round(pcb_nut_front_wall, 3), "min": 1.2, "pass": pcb_nut_front_wall >= 1.2}
        checks["pcb_thermal_bridge_gap_wc_mm"] = {"value": round(pcb_thermal_gap_wc, 3), "min": 4.5, "max": 6.0, "pass": 4.5 <= pcb_thermal_gap_wc <= 6.0}
        checks["usbc_plug_to_baffle_clr_mm"] = {"value": round(usbc_plug_to_baffle, 3), "min": 1.5, "pass": usbc_plug_to_baffle >= 1.5}
        checks["jst_below_ceil_cone_mm"] = {"value": round(cone_z_at_jst - j23_top_z, 3), "min": 4.0, "pass": (cone_z_at_jst - j23_top_z) >= 4.0}
        checks["pcb_top_below_ceil_cone_mm"] = {"value": round(cone_z_at_pcb - self.z_pcb_top, 3), "min": 6.0, "pass": (cone_z_at_pcb - self.z_pcb_top) >= 6.0}

        # 3. Side-port ring: 18 mm 90-deg USB-C plug, compressing +Y clamp, -X SW1 cove, -Y vent & eaves
        plug_bot_z = self.z_j1_mouth - self.usbc_plug_90_len
        port_floor_z = self.z_top_base_port_bot
        r_port_out = 0.5 * self.top_base_port_od  # 47.0
        r_port_in = 0.5 * self.top_base_port_id   # 39.0
        clamp_blind_wall = (r_port_out - self.m3_insert_blind_depth) - math.sqrt(r_port_in ** 2 - self.clamp_bolt_dx ** 2)
        clamp_outer_y = r_port_out + self.clamp_standoff_y + self.clamp_flange_t  # 54.2 mm
        eaves_overhang_clamp = 0.5 * self.cap_top_eaves_od - clamp_outer_y        # 4.8 mm
        clamp_top_to_eaves = self.z_top_base_deck_top - (self.clamp_z + 10.0)     # 4.5 mm
        sw1_face_x = -(r_port_out - self.sw1_recess_x)                            # -41.5 mm
        sw1_lugs_x = sw1_face_x + self.sw1_wall_thick + self.sw1_body_d_x + self.sw1_lugs_d_x  # -23.53 mm
        sw1_clr_to_core = abs(sw1_lugs_x) - 0.5 * self.core_w_max                 # 8.33 mm
        sw1_boot_tip_x = abs(sw1_face_x) + self.sw1_boot_protrude_x               # 60.1 mm WC (58.2 nom)
        sw1_visor_shelter = self.cap_top_sw_visor_x - sw1_boot_tip_x              # 3.4 mm WC (5.3 nom)
        sw1_z_margin = min(self.sw1_z - port_floor_z, self.z_top_base_deck_top - self.sw1_z) - 0.5 * self.sw1_body_h_z
        g3_r_out = self.top_oring_groove_r_in + self.top_oring_groove_w           # 47.0 mm
        eave_ins_to_g3 = (self.top_base_ear_r - 0.5 * self.m3_insert_pilot_dia) - g3_r_out  # 2.0 mm
        eave_ins_outer = 0.5 * self.cap_top_eaves_od - (self.top_base_ear_r + 0.5 * self.m3_insert_pilot_dia)  # 6.0 mm
        ear_csk_rim = self.top_base_ear_boss_r - 3.25                             # 2.25 mm

        checks["usbc_plug_18mm_above_floor_mm"] = {"value": round(plug_bot_z - port_floor_z, 3), "min": 6.0, "pass": (plug_bot_z - port_floor_z) >= 6.0}
        checks["clamp_insert_blind_wall_mm"] = {"value": round(clamp_blind_wall, 3), "min": 2.5, "pass": clamp_blind_wall >= 2.5}
        checks["clamp_standoff_travel_mm"] = {"value": round(self.clamp_standoff_y, 3), "min": 1.0, "pass": self.clamp_standoff_y >= 1.0}
        checks["clamp_grommet_len_ge_10mm"] = {"value": round(self.clamp_grommet_len, 2), "min": 10.0, "pass": self.clamp_grommet_len >= 10.0}
        checks["clamp_sheltered_inside_eaves_mm"] = {"value": round(eaves_overhang_clamp, 3), "min": 3.5, "pass": eaves_overhang_clamp >= 3.5}
        checks["clamp_top_below_eaves_mm"] = {"value": round(clamp_top_to_eaves, 3), "min": 4.0, "pass": clamp_top_to_eaves >= 4.0}
        checks["sw1_lugs_clr_to_core_mm"] = {"value": round(sw1_clr_to_core, 3), "min": 7.0, "pass": sw1_clr_to_core >= 7.0}
        checks["sw1_boot_inside_visor_mm"] = {"value": round(sw1_visor_shelter, 3), "min": 2.5, "pass": sw1_visor_shelter >= 2.5}
        checks["sw1_port_ring_z_wall_mm"] = {"value": round(sw1_z_margin, 3), "min": 3.0, "pass": sw1_z_margin >= 3.0}
        checks["eave_insert_to_g3_wall_mm"] = {"value": round(eave_ins_to_g3, 3), "min": 1.8, "pass": eave_ins_to_g3 >= 1.8}
        checks["eave_insert_outer_wall_mm"] = {"value": round(eave_ins_outer, 3), "min": 4.0, "pass": eave_ins_outer >= 4.0}
        checks["ear_csk_outer_rim_mm"] = {"value": round(ear_csk_rim, 3), "min": 2.0, "pass": ear_csk_rim >= 2.0}

        # 4. Core hub, collar & epoxy-bonded LED star optical chamber clearances
        hub_corner_wall = 0.5 * self.core_hub_od - (0.5 * self.core_pocket_w) * math.sqrt(2.0)
        cap_top_collar_wall = 0.5 * (self.cap_top_collar_w - self.core_pocket_w)
        core_corner_r = (0.5 * self.core_w_max) * math.sqrt(2.0)
        led_r = 0.5 * self.core_w_max + self.star_tim_thick + self.star_thick + self.led_uv_max_h
        slot_corner_r = math.hypot(0.5 * self.core_wire_slot_w, 0.5 * self.core_pocket_w + self.core_wire_slot_d)
        r_glass_min = 0.5 * self.glass_id_min
        uv_top_rim_clr = self.z_top_base_bot - (self.z_led_uv + 0.5 * self.star_dia)
        vis_bot_rim_clr = (self.z_led_vis - 0.5 * self.star_dia) - self.z_cap_bot_top
        uv_vis_star_gap = self.axial_uv_to_vis_mm - self.star_dia

        checks["core_hub_corner_wall_mm"] = {"value": round(hub_corner_wall, 3), "min": 2.2, "pass": hub_corner_wall >= 2.2}
        checks["cap_top_collar_wall_mm"] = {"value": round(cap_top_collar_wall, 3), "min": 4.0, "pass": cap_top_collar_wall >= 4.0}
        checks["core_corner_to_glass_id_mm"] = {"value": round(r_glass_min - core_corner_r, 3), "min": 5.0, "pass": (r_glass_min - core_corner_r) >= 5.0}
        checks["led_to_glass_id_mm"] = {"value": round(r_glass_min - led_r, 3), "min": 7.0, "pass": (r_glass_min - led_r) >= 7.0}
        checks["wire_slot_to_glass_id_mm"] = {"value": round(r_glass_min - slot_corner_r, 3), "min": 2.5, "pass": (r_glass_min - slot_corner_r) >= 2.5}
        checks["star_uv_vis_edge_gap_mm"] = {"value": round(uv_vis_star_gap, 3), "min": 10.0, "pass": uv_vis_star_gap >= 10.0}
        checks["uv_star_below_top_rim_mm"] = {"value": round(uv_top_rim_clr, 3), "min": 12.0, "pass": uv_top_rim_clr >= 12.0}
        checks["vis_star_above_bot_rim_mm"] = {"value": round(vis_bot_rim_clr, 3), "min": 12.0, "pass": vis_bot_rim_clr >= 12.0}

        # 5. Shroud radial O-rings (60 x 3.5 mm VMQ50) & top-bell axial face O-ring (88 x 2.5 mm VMQ50)
        g12_gland_nom = 0.5 * (self.glass_oring_groove_od - self.glass_od_nom)
        g12_gland_min = 0.5 * (self.glass_oring_groove_od - self.glass_od_max)
        g12_gland_max = 0.5 * (self.glass_oring_groove_od - self.glass_od_min)
        g12_sq_nom = 100.0 * (self.glass_oring_cs - g12_gland_nom) / self.glass_oring_cs
        g12_sq_max = 100.0 * (self.glass_oring_cs - g12_gland_min) / self.glass_oring_cs
        g12_sq_min = 100.0 * (self.glass_oring_cs - g12_gland_max) / self.glass_oring_cs
        g12_ramp = 0.5 * (self.glass_oring_groove_od - self.glass_bore_id)
        g12_area_min = g12_gland_min * self.glass_oring_flat_w + 0.5 * g12_ramp * (g12_gland_min + (g12_gland_min - g12_ramp))
        g12_fill = (math.pi * (0.5 * self.glass_oring_cs) ** 2) / g12_area_min

        g3_sq_pct = 100.0 * (self.top_oring_cs - self.top_oring_groove_depth) / self.top_oring_cs
        g3_fill = (math.pi * (0.5 * self.top_oring_cs) ** 2) / (self.top_oring_groove_w * self.top_oring_groove_depth)

        short_tube_top = (self.z_glass_bot - 1.0) + (self.glass_length - self.glass_length_tol) - 1.0
        g2_flat_top = self.z_top_base_bot + 3.0 + self.glass_oring_flat_w
        short_tube_seal_margin = short_tube_top - g2_flat_top

        checks["g12_radial_squeeze_min_pct"] = {"value": round(g12_sq_min, 1), "min": 10.0, "pass": g12_sq_min >= 10.0}
        checks["g12_radial_squeeze_nom_pct"] = {"value": round(g12_sq_nom, 1), "min": 14.0, "max": 26.0, "pass": 14.0 <= g12_sq_nom <= 26.0}
        checks["g12_radial_squeeze_max_pct"] = {"value": round(g12_sq_max, 1), "max": 33.0, "pass": g12_sq_max <= 33.0}
        checks["g12_gland_fill_max"] = {"value": round(g12_fill, 4), "max": 0.85, "pass": g12_fill <= 0.85}
        checks["short_tube_g2_margin_mm"] = {"value": round(short_tube_seal_margin, 3), "min": 2.0, "pass": short_tube_seal_margin >= 2.0}
        checks["g3_axial_squeeze_pct"] = {"value": round(g3_sq_pct, 1), "min": 18.0, "max": 30.0, "pass": 18.0 <= g3_sq_pct <= 30.0}
        checks["g3_axial_gland_fill"] = {"value": round(g3_fill, 4), "max": 0.85, "pass": g3_fill <= 0.85}

        # 6. Open chimney, ventilated finial & top M4 hanging bolt checks
        roof_slope_deg = math.degrees(math.atan2(self.cap_top_roof_h, 0.5 * (self.cap_top_bell_od - self.cap_top_collar_w)))
        exhaust_area_cm2 = 4.0 * (self.plug_top_leg_w - 2.0 * 5.5) * self.plug_top_vent_h / 100.0
        hood_overhang_mm = 0.5 * (self.plug_top_hood_w - self.core_bore_nom)
        top_bolt_edge_mm = self.core_hang_hole_from_top - 0.5 * self.core_bolt_hole_dia

        checks["core_protrusion_mm"] = {"value": round(self.core_protrusion_mm, 3), "min": 45.0, "max": 75.0, "pass": 45.0 <= self.core_protrusion_mm <= 75.0}
        checks["cap_top_roof_slope_deg"] = {"value": round(roof_slope_deg, 1), "min": 24.0, "pass": roof_slope_deg >= 24.0}
        checks["finial_exhaust_area_cm2"] = {"value": round(exhaust_area_cm2, 2), "min": 4.5, "pass": exhaust_area_cm2 >= 4.5}
        checks["finial_hood_overhang_mm"] = {"value": round(hood_overhang_mm, 2), "min": 5.0, "pass": hood_overhang_mm >= 5.0}
        checks["top_m4_bolt_al_edge_mm"] = {"value": round(top_bolt_edge_mm, 2), "min": 10.0, "pass": top_bolt_edge_mm >= 10.0}

        return checks

    def to_dict(self) -> dict:
        d = asdict(self)
        d["derived"] = {
            "z_core_bot": self.z_core_bot,
            "z_bot_bolt": self.z_bot_bolt,
            "z_glass_bot": self.z_glass_bot,
            "z_cap_bot_top": self.z_cap_bot_top,
            "z_glass_top": self.z_glass_top,
            "z_top_base_bot": self.z_top_base_bot,
            "top_base_flare_h": self.top_base_flare_h,
            "z_top_base_port_bot": self.z_top_base_port_bot,
            "z_top_base_deck_top": self.z_top_base_deck_top,
            "pcb_x_bcu": self.pcb_x_bcu,
            "pcb_x_fcu": self.pcb_x_fcu,
            "z_pcb_bot": self.z_pcb_bot,
            "z_pcb_top": self.z_pcb_top,
            "z_j1_mouth": self.z_j1_mouth,
            "x_j1_center": self.x_j1_center,
            "z_d12": self.z_d12,
            "z_cap_top_bot": self.z_cap_top_bot,
            "z_cap_top_eaves_top": self.z_cap_top_eaves_top,
            "z_cap_top_collar_bot": self.z_cap_top_collar_bot,
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
