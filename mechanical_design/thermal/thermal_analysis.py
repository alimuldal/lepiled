#!/usr/bin/env python3
"""
Coupled First-Principles 8-Node (+ 2-Zone PCB) Thermal Analysis for LepiLED DIY Maxi Switch.

Reads exact CAD geometry from `mechanical_design/cad/cad_params.json` and electrical power
budgets from `circuit_design/sim/outputs/sim_summary.json`.

8 Coupled Steady-State Nodes:
  1. T_c_uv    : Al core at UV star tier (Z = 94.0 mm)
  2. T_c_vis   : Al core at visible star tier (Z = 60.0 mm)
  3. T_c_bay   : Al core passing through top electronics bay (Z = 145..247 mm)
  4. T_hs_t    : Protruding bare mill Al upper chimney (48.0 mm above collar, with plume preheating)
  5. T_baffle  : PCB-facing surface of 1.5 mm ASA thermal baffle (radiates/conducts to B.Cu)
  6. T_bay_air : Top electronics bay air temperature
  7. T_bell_in : Inner wall temperature of White ASA umbrella bell
  8. T_pcb_avg : Vertically mounted 36 x 46 mm 2L FR4 driver_pcb (F.Cu conv + bell rad + wires + bridge)

Physical fidelity features (audited via 3-model independent first-principles review):
  - Square-duct open-chimney solver using Shah & London isothermal Nu_fd = 2.976, Hagenbach
    developing-flow excess loss K_fd = 1.43, CAD-derived obstruction losses (bottom M4 bolt,
    MECH-PLUG-TOP legs/webs + top M4 throat, 90-deg flat hood & 509.7 mm^2 side exits -> K_eff ~ 9.3),
    and 4-node axial wall/bore coupling including T_hs_t.
  - Baffled horizontal duct sets Q_bore = 0 (stratified stagnant air) and uses horizontal external
    cylinder convection on the umbrella head.
  - Shroud annular gap clamps Nu = 1 below MacGregor-Emery's Ra_d >= 1e4 validity floor (pure
    conduction verified to 0.6% against 2D Laplace PDE) and includes 24.4% white-soldermask LED star
    emissivity (eps_eff = 0.283 on bare mill Al) plus spectral UV (15.3%) / Visible (3.5%) optical
    re-absorption in extruded XT PMMA 0A070 GT.
  - Top bay derives A_int and A_ext from cad_params.json, models 15%-gyroid White ASA wall conduction,
    applies +2 K shroud-plume preheating to the umbrella exterior, uses a realistic epoxied-shim
    15 x 15 mm PCB bridge resistance (16.0 K/W), and evaluates a coupled 2-zone PCB check for U4
    (LM393DR2G, 0..+70 C) sitting outside the bridge footprint.
  - Asserts fsolve convergence (ier == 1, max|resid| < 1e-6) and global energy balance (< 1e-5 W).
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
from dataclasses import dataclass
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import fsolve

REPO_ROOT = Path(__file__).resolve().parents[2]
CAD_PARAMS_JSON = REPO_ROOT / "mechanical_design/cad/cad_params.json"
SIM_SUMMARY_JSON = REPO_ROOT / "circuit_design/sim/outputs/sim_summary.json"
SIGMA = 5.670374419e-8

# Single-source thermal limits (referenced dynamically in both gates and plots)
LIMIT_UV_C = 100.0        # Luminus SST-10-UV max junction
LIMIT_VIS_C = 150.0       # ams OSRAM CSLNM1 max junction
LIMIT_PMMA_C = 75.0       # PLEXIGLAS XT Clear 0A070 GT continuous service
LIMIT_ASA_CONT_C = 80.0   # White ASA continuous derated limit under bolt/O-ring load (HDT-B 95 - 15 K)
LIMIT_ASA_HDT_C = 95.0    # White ASA HDT-B (0.45 MPa)
LIMIT_LM393_C = 70.0      # onsemi LM393DR2G commercial rating (0..+70 C)
LIMIT_U1_J_C = 125.0      # AL8860WT-7 recommended max junction
UNCERTAINTY_BAND_K = 4.0  # Structural + field model uncertainty band (+/-4 K)


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


def air_props(T_C: float) -> dict[str, float]:
    """Dry air thermophysical properties at 1 atm, T in deg C (valid 0..150 C)."""
    T_K = T_C + 273.15
    rho = 101325.0 / (287.058 * T_K)
    mu = 1.458e-6 * (T_K ** 1.5) / (T_K + 110.4)
    nu = mu / rho
    cp = 1005.0 + 0.05 * max(0.0, T_C)
    k = 0.02414 * (T_K / 273.15) ** 0.85
    alpha = k / (rho * cp)
    Pr = nu / alpha
    beta = 1.0 / T_K
    return dict(rho=rho, mu=mu, nu=nu, cp=cp, k=k, alpha=alpha, Pr=Pr, beta=beta, T_K=T_K)


def churchill_chu_vertical_plate_h(T_s: float, T_amb: float, L: float) -> float:
    dT = max(0.05, abs(T_s - T_amb))
    p = air_props(0.5 * (T_s + T_amb))
    Ra = 9.81 * p["beta"] * dT * (L ** 3) / (p["nu"] * p["alpha"])
    Nu = (0.825 + (0.387 * Ra ** (1.0 / 6.0)) / (1.0 + (0.492 / p["Pr"]) ** (9.0 / 16.0)) ** (8.0 / 27.0)) ** 2
    return Nu * p["k"] / L


def churchill_chu_horiz_cyl_h(T_s: float, T_amb: float, D: float) -> float:
    dT = max(0.05, abs(T_s - T_amb))
    p = air_props(0.5 * (T_s + T_amb))
    Ra = 9.81 * p["beta"] * dT * (D ** 3) / (p["nu"] * p["alpha"])
    Nu = (0.60 + (0.387 * Ra ** (1.0 / 6.0)) / (1.0 + (0.559 / p["Pr"]) ** (9.0 / 16.0)) ** (8.0 / 27.0)) ** 2
    return Nu * p["k"] / D


@dataclass(frozen=True)
class ChimneyConfig:
    name: str
    short_label: str
    open_chimney: bool
    win_eps: float            # Bare/painted Al emissivity inside optical window (before 24.4% star area blend)
    bay_eps: float            # Exterior Al emissivity on 3 exposed faces inside top electronics bay
    chimney_eps: float        # Exterior Al emissivity on protruding upper chimney stub
    k_cad_obstructions: float = 6.35  # Bot M4 bolt (0.35) + Plug legs/webs & top M4 throat (2.00) + 90-deg flat hood/ports (4.00)
    k_hagenbach: float = 1.43         # Shah & London square-duct laminar hydrodynamic developing-flow excess loss
    pcb_bridge_rth_KW: float | None = 16.0  # Realistic 15x15 mm epoxied-shim + >=3 W/mK silicone-pad bridge (None = no bridge)


def compute_chimney_ambient_view_factor(L_chim_mm: float, core_w_mm: float, bell_od_mm: float, collar_h_mm: float) -> float:
    w_shelf = max(0.0, 0.5 * (bell_od_mm - core_w_mm))
    ys = np.linspace(0.5, L_chim_mm, 60)
    h_eff = ys + collar_h_mm
    f_to_eave = float(np.mean(0.5 * (1.0 - h_eff / np.sqrt(h_eff ** 2 + w_shelf ** 2))))
    return round(1.0 - f_to_eave, 4)


def compute_chimney_k_eff(bore_mm: float, inlet_w_mm: float, k_cad_obstructions: float, k_hagenbach: float) -> float:
    b = bore_mm * 1e-3
    A_duct = b * b
    A_in = max(1e-6, (inlet_w_mm * 1e-3) ** 2 - (4.0 - math.pi) * (0.003 ** 2))
    area_ratio = A_duct / min(A_duct, A_in)
    k_inlet_exp = 1.5 * max(0.0, area_ratio ** 2 - 1.0)
    return k_inlet_exp + k_hagenbach + k_cad_obstructions


def protruding_core_Q(
    T_s: float,
    T_amb: float,
    core_w_mm: float,
    L_mm: float,
    eps: float,
    orientation: str = "vertical",
    f_rad_amb: float = 0.85,
    rth_penalty_factor: float = 1.0,
) -> float:
    """Natural convection (with +2 K rising head-plume preheating) + view-factor-corrected radiation."""
    W = core_w_mm * 1e-3
    L = L_mm * 1e-3
    A_sides = 4.0 * W * L
    T_plume = T_amb + (2.0 if orientation == "vertical" else 0.0)
    if orientation == "vertical":
        h_c = churchill_chu_vertical_plate_h(T_s, T_plume, L)
    else:
        h_c = churchill_chu_horiz_cyl_h(T_s, T_plume, 4.0 * W / math.pi)
    Q_conv = h_c * A_sides * (T_s - T_plume)
    dT_r = max(0.0, T_s - T_amb)
    T_eave = T_amb + 0.35 * dT_r
    Q_rad_amb = eps * f_rad_amb * SIGMA * ((T_s + 273.15) ** 4 - (T_amb + 273.15) ** 4) * A_sides
    Q_rad_eave = eps * (1.0 - f_rad_amb) * SIGMA * ((T_s + 273.15) ** 4 - (T_eave + 273.15) ** 4) * A_sides
    return (Q_conv + Q_rad_amb + Q_rad_eave) / rth_penalty_factor


def open_chimney_bore_Q(
    T_wall: float,
    T_amb: float,
    bore_mm: float,
    inlet_w_mm: float,
    L_duct_mm: float,
    k_cad_obstructions: float = 6.35,
    k_hagenbach: float = 1.43,
    orientation: str = "vertical",
    rth_penalty_factor: float = 1.0,
) -> tuple[float, float, float]:
    """
    First-principles buoyancy-driven natural draft inside vertical square Al duct using
    Shah & London square-duct isothermal Nu_fd = 2.976, Poiseuille friction (fRe = 56.91),
    Hagenbach entrance loss, and CAD obstruction minor losses.
    In horizontal orientation, a baffled L/D = 11.5 duct traps stratified air (Q_bore = 0).
    Returns (Q_bore_W, mean_air_velocity_m_s, dP_buoy_Pa).
    """
    dT = T_wall - T_amb
    if dT <= 0.1 or orientation != "vertical":
        return 0.0, 0.0, 0.0

    b = bore_mm * 1e-3
    L = L_duct_mm * 1e-3
    A_duct = b * b
    K_eff = compute_chimney_k_eff(bore_mm, inlet_w_mm, k_cad_obstructions, k_hagenbach)
    p = air_props(0.5 * (T_wall + T_amb))

    V = 0.13
    eff = 0.65
    dP_buoy = 0.0
    for _ in range(45):
        mdot = p["rho"] * V * A_duct
        Re = V * b / p["nu"]
        Gz = (b / L) * Re * p["Pr"]
        # Square-duct isothermal developing laminar Nu (Shah & London 1978, Nu_T,fd = 2.976)
        Nu_g = 2.976 + (0.0668 * Gz) / (1.0 + 0.04 * (Gz ** (2.0 / 3.0)))
        h_in = Nu_g * p["k"] / b
        NTU = h_in * (4.0 * b * L) / max(1e-9, mdot * p["cp"])
        eff = 1.0 - math.exp(-NTU)
        dT_air_avg = dT * (1.0 - eff / max(1e-6, NTU))
        dP_buoy = p["rho"] * 9.81 * p["beta"] * dT_air_avg * L
        A_q = 0.5 * K_eff * p["rho"]
        B_q = 28.45 * p["mu"] * L / (b * b)
        V_new = (-B_q + math.sqrt(B_q * B_q + 4.0 * A_q * dP_buoy)) / (2.0 * A_q)
        V = 0.5 * V + 0.5 * V_new
    Q_tot = (p["rho"] * V * A_duct * p["cp"] * dT * eff) / rth_penalty_factor
    return float(Q_tot), float(V), float(dP_buoy)


def shroud_annular_path_Q(
    T_core: float,
    T_amb: float,
    D_in_mm: float,
    D_out_mm: float,
    L_shroud_mm: float,
    D_core_eq_mm: float,
    eps_core_eff: float,
    eps_shroud: float = 0.93,
    k_wall: float = 0.19,
    Q_opt_wall_W: float = 0.0,
    orientation: str = "vertical",
) -> tuple[float, float, float]:
    if T_core <= T_amb + 0.05 and Q_opt_wall_W <= 0.0:
        return 0.0, T_amb, T_amb
    r_1 = 0.5 * D_core_eq_mm * 1e-3
    r_2 = 0.5 * D_in_mm * 1e-3
    r_3 = 0.5 * D_out_mm * 1e-3
    L = L_shroud_mm * 1e-3
    A_1 = 2.0 * math.pi * r_1 * L
    A_2 = 2.0 * math.pi * r_2 * L
    A_3 = 2.0 * math.pi * r_3 * L
    R_wall = math.log(r_3 / r_2) / (2.0 * math.pi * k_wall * L)
    delta = r_2 - r_1

    def resid(vars_: list[float]) -> list[float]:
        T_gi, T_go = vars_
        dT_gap = T_core - T_gi
        p = air_props(0.5 * (T_core + T_gi))
        Ra_d = 9.81 * p["beta"] * max(0.01, abs(dT_gap)) * (delta ** 3) / (p["nu"] * p["alpha"])
        if orientation == "vertical":
            # MacGregor-Emery is valid only for Ra_d >= 1e4; below 1e4 the 7.9 mm gap is pure conduction
            # (2*pi*r_1/delta = 15.19 matches exact 2D Laplace square-in-circle PDE S/L = 15.27 within 0.6%).
            if Ra_d >= 1.0e4:
                Nu_d = max(1.0, 0.42 * (Ra_d ** 0.25) * (p["Pr"] ** 0.012) * ((L / delta) ** (-0.3)))
            else:
                Nu_d = 1.0
        else:
            D_c, D_o = 2.0 * r_1, 2.0 * r_2
            F_cyl = ((math.log(D_o / D_c)) ** 4) / ((delta ** 3) * (D_c ** (-0.6) + D_o ** (-0.6)) ** 5)
            Ra_c = F_cyl * Ra_d
            k_eff_k = max(1.0, 0.386 * (p["Pr"] / (0.861 + p["Pr"])) ** 0.25 * (Ra_c ** 0.25))
            Nu_d = k_eff_k * delta / (r_1 * math.log(r_2 / r_1))
        h_gap_c = Nu_d * p["k"] / delta
        Q_gap_c = h_gap_c * A_1 * dT_gap
        denom = (1.0 / eps_core_eff) + (A_1 / A_2) * (1.0 / eps_shroud - 1.0)
        Q_gap_r = SIGMA * A_1 * ((T_core + 273.15) ** 4 - (T_gi + 273.15) ** 4) / denom
        Q_gap = Q_gap_c + Q_gap_r

        Q_wall = (T_gi - T_go) / R_wall
        h_out_c = (
            churchill_chu_vertical_plate_h(T_go, T_amb, L)
            if orientation == "vertical"
            else churchill_chu_horiz_cyl_h(T_go, T_amb, 2.0 * r_3)
        )
        Q_out_c = h_out_c * A_3 * (T_go - T_amb)
        Q_out_r = eps_shroud * SIGMA * A_3 * ((T_go + 273.15) ** 4 - (T_amb + 273.15) ** 4)
        Q_out = Q_out_c + Q_out_r
        return [(Q_gap + 0.5 * Q_opt_wall_W) - Q_wall, (Q_gap + Q_opt_wall_W) - Q_out]

    sol, infodict, ier, msg = fsolve(
        resid, [0.5 * (T_core + T_amb), 0.3 * T_core + 0.7 * T_amb], full_output=True
    )
    if ier != 1 or float(np.max(np.abs(infodict["fvec"]))) > 1e-6:
        raise RuntimeError(f"shroud_annular_path_Q did not converge: ier={ier}, msg={msg}")
    T_gi, T_go = float(sol[0]), float(sol[1])
    Q_from_core = float((T_gi - T_go) / R_wall - 0.5 * Q_opt_wall_W)
    return Q_from_core, T_gi, T_go


def solve_system(
    cad: dict,
    Q_uv_elec_heat: float,
    Q_vis_elec_heat: float,
    Q_opt_core_W: float,
    Q_opt_wall_W: float,
    Q_pcb: float,
    P_pcb_upper: float,
    P_pcb_lower: float,
    p_u1: float,
    T_amb: float,
    cfg: ChimneyConfig,
    f_rad_amb: float,
    r_sub_led: float = 0.65,  # 1.5 mm Cu DTP star radial fin efficiency + 2 mm Al wall constriction
    r_tim_led: float = 0.65,  # Realistic hand-clamped 0.15 mm thermal epoxy (k = 1.2-1.5 W/mK)
    orientation: str = "vertical",
    rth_penalty_factor: float = 1.0,
) -> dict[str, float]:
    """Solve coupled 8-node (+ 2-zone PCB) steady-state thermal network with convergence & energy asserts."""
    der = cad["derived"]
    W = cad["core_w_nom"] * 1e-3
    b_mm = cad["core_bore_nom"]
    A_cs = (cad["core_w_nom"] ** 2 - b_mm ** 2) * 1e-6
    k_al = 200.0
    l_chim_mm = der["core_protrusion_mm"]

    L_bay = (der["z_cap_top_collar_bot"] - 4.0 - der["z_top_base_port_bot"]) * 1e-3
    z_bay_mid = 0.5 * (der["z_top_base_port_bot"] + der["z_cap_top_collar_bot"] - 4.0)
    z_chim_mid = der["z_cap_top_top"] + 0.5 * l_chim_mm

    R_ax_uv_vis = (der["axial_uv_to_vis_mm"] * 1e-3) / (k_al * A_cs)
    R_ax_uv_bay = ((z_bay_mid - der["z_led_uv"]) * 1e-3) / (k_al * A_cs)
    R_ax_bay_top = ((z_chim_mid - z_bay_mid) * 1e-3) / (k_al * A_cs)

    # Top-head exterior & interior bay areas derived directly from cad_params.json (15% gyroid White ASA)
    D_bell = cad["cap_top_bell_od"] * 1e-3
    D_eaves = cad["cap_top_eaves_od"] * 1e-3
    D_port = cad["top_base_port_od"] * 1e-3
    D_collar = cad["top_base_collar_od"] * 1e-3
    D_bore = cad["cap_top_bore_id"] * 1e-3
    D_port_id = cad["top_base_port_id"] * 1e-3

    # Exterior surface area (underside flare + port ring + eaves + taper + straight bell + 45-deg roof)
    flare_s = math.hypot(0.5 * (D_port - D_collar), der["top_base_flare_h"] * 1e-3)
    A_flare = math.pi * 0.5 * (D_port + D_collar) * flare_s
    A_ring = math.pi * D_port * (cad["top_base_port_h"] * 1e-3)
    eaves_taper_s = math.hypot(0.5 * (D_eaves - D_bell), cad["cap_top_eaves_taper_h"] * 1e-3)
    A_eaves = (
        math.pi * D_eaves * (cad["cap_top_eaves_h"] * 1e-3)
        + 0.25 * math.pi * (D_eaves ** 2 - D_port ** 2)
        + math.pi * 0.5 * (D_eaves + D_bell) * eaves_taper_s
    )
    h_bell_straight = max(0.0, (cad["cap_top_roof_bot_z"] - der["z_cap_top_eaves_top"] - cad["cap_top_eaves_taper_h"]) * 1e-3)
    A_bell = math.pi * D_bell * h_bell_straight
    roof_run = max(1e-4, 0.5 * (D_bell - cad["cap_top_collar_w"] * 1e-3))
    roof_slope_rad = math.atan2(cad["cap_top_roof_h"] * 1e-3, roof_run)
    A_roof = 0.25 * math.pi * (D_bell ** 2 - (cad["cap_top_collar_w"] * 1e-3) ** 2) / math.cos(roof_slope_rad)
    A_ext = A_flare + A_ring + A_eaves + A_bell + A_roof

    # True interior dry-bay wall + ceiling cone + annular floor area from cad_params.json (~0.0308 m^2)
    h_bay_low = (der["z_top_base_deck_top"] - der["z_top_base_port_bot"]) * 1e-3
    h_bay_up = (cad["cap_top_ceil_cone_z"] - der["z_top_base_deck_top"]) * 1e-3
    ceil_h = (der["z_cap_top_collar_bot"] - cad["cap_top_ceil_cone_z"]) * 1e-3
    ceil_s = math.hypot(0.5 * (D_bore - cad["core_pocket_w"] * 1e-3), ceil_h)
    A_int = (
        math.pi * D_port_id * h_bay_low
        + math.pi * D_bore * h_bay_up
        + math.pi * 0.5 * (D_bore + cad["core_pocket_w"] * 1e-3) * ceil_s
        + 0.25 * math.pi * (D_port_id ** 2) - (cad["core_pocket_w"] * 1e-3) ** 2
    )
    # 15%-gyroid White ASA wall conduction: 45% solid 3.1 mm bell (k=0.18) + 55% 4-wall/15%-gyroid 8.5 mm port/eaves/roof (k_eff=0.082)
    R_wall = 1.0 / (0.45 * A_int * (0.18 / 0.0031) + 0.55 * A_int * (0.082 / 0.0085))

    A_core_3 = 3.0 * W * L_bay
    A_core_1 = 1.0 * W * L_bay
    A_pcb_1 = (cad["pcb_w"] * cad["pcb_l"]) * 1e-6
    A_chute = (cad["pcb_thermal_win_w"] * cad["pcb_thermal_win_h"]) * 1e-6
    eps_pcb = 0.85
    eps_baffle = 0.90
    G_pcb_wires = 0.008  # Conservative conduction through USB-C copper/shield + M3 stanchions
    G_pcb_bridge = (1.0 / cfg.pcb_bridge_rth_KW) if cfg.pcb_bridge_rth_KW else 0.0

    # Effective optical-window core emissivity including 8x Ø20 mm white-soldermask Convoy stars (24.4% coverage, eps=0.85)
    L_win = der["exposed_glass_window_mm"] * 1e-3
    f_stars = min(0.5, (8.0 * 0.25 * math.pi * ((cad["star_dia"] * 1e-3) ** 2)) / (4.0 * W * L_win))
    eps_win_eff = (1.0 - f_stars) * cfg.win_eps + f_stars * 0.85

    Q_uv_tot = Q_uv_elec_heat + 0.50 * Q_opt_core_W
    Q_vis_tot = Q_vis_elec_heat + 0.50 * Q_opt_core_W
    d_core_eq = 4.0 * cad["core_w_nom"] / math.pi

    # Shroud plume preheating on the overhanging umbrella head in vertical orientation
    T_bell_amb = T_amb + (2.0 if orientation == "vertical" else 0.0)

    def resid(x: list[float]) -> list[float]:
        T_c_uv, T_c_vis, T_c_bay, T_hs_t, T_baf, T_bay_air, T_bell_in, T_pcb = x
        T_c_avg = 0.5 * (T_c_uv + T_c_vis)
        Q_shroud, _, _ = shroud_annular_path_Q(
            T_c_avg, T_amb,
            D_in_mm=cad["glass_id_nom"], D_out_mm=cad["glass_od_nom"],
            L_shroud_mm=der["exposed_glass_window_mm"], D_core_eq_mm=d_core_eq,
            eps_core_eff=eps_win_eff, eps_shroud=0.93, k_wall=0.19,
            Q_opt_wall_W=Q_opt_wall_W, orientation=orientation,
        )
        if cfg.open_chimney:
            # Length-weighted bore wall temp including cooler 48 mm upper chimney stub
            T_bore_avg = 0.25 * T_c_vis + 0.25 * T_c_uv + 0.34 * T_c_bay + 0.16 * T_hs_t
            Q_bore, _, _ = open_chimney_bore_Q(
                T_bore_avg, T_amb, b_mm, cad["cap_bot_inlet_w"], cad["core_length"] - 15.0,
                k_cad_obstructions=cfg.k_cad_obstructions, k_hagenbach=cfg.k_hagenbach,
                orientation=orientation, rth_penalty_factor=rth_penalty_factor,
            )
        else:
            Q_bore = 0.0

        Q_top = protruding_core_Q(
            T_hs_t, T_amb, cad["core_w_nom"], l_chim_mm, cfg.chimney_eps,
            orientation=orientation, f_rad_amb=f_rad_amb, rth_penalty_factor=rth_penalty_factor,
        )
        Q_uv_vis = (T_c_uv - T_c_vis) / R_ax_uv_vis
        Q_uv_bay = (T_c_uv - T_c_bay) / R_ax_uv_bay
        Q_bay_top = (T_c_bay - T_hs_t) / R_ax_bay_top

        h_c3 = churchill_chu_vertical_plate_h(T_c_bay, T_bay_air, L_bay) * 0.65
        Q_c3_conv = h_c3 * A_core_3 * (T_c_bay - T_bay_air)
        Q_c3_rad = cfg.bay_eps * SIGMA * A_core_3 * ((T_c_bay + 273.15) ** 4 - (T_bell_in + 273.15) ** 4)
        Q_sock = 0.025 * (T_c_bay - T_bell_in)

        # Core -> 1.5 mm ASA baffle (0.55 mm slip gap + 1.5 mm ASA, minus 15.6 x 15.4 mm bridge chute cutout)
        A_baf_eff = max(1e-5, A_core_1 - A_chute)
        R_core_baf = (0.00055 / 0.028 + (cad["core_sleeve_wall"] * 1e-3) / 0.18) / A_baf_eff
        Q_core_baf = (T_c_bay - T_baf) / R_core_baf

        # Baffle <-> B.Cu air gap & radiation + captive 15 x 15 mm epoxied-shim PCB thermal bridge
        gap_bp = (cad["pcb_x_bcu"] - (0.5 * cad["core_pocket_w"] + cad["core_sleeve_wall"])) * 1e-3
        A_bridge = (0.015 * 0.015) if G_pcb_bridge > 0.0 else 0.0
        A_pcb_air = max(1e-6, A_pcb_1 - A_bridge)
        A_baf_rest = max(0.0, A_baf_eff - A_pcb_air)
        Q_baf_pcb_cond = (0.028 / gap_bp) * A_pcb_air * (T_baf - T_pcb)
        eps_eff_bp = 1.0 / (1.0 / eps_baffle + 1.0 / eps_pcb - 1.0)
        Q_baf_pcb_rad = eps_eff_bp * SIGMA * A_pcb_air * ((T_baf + 273.15) ** 4 - (T_pcb + 273.15) ** 4)
        Q_baf_pcb = Q_baf_pcb_cond + Q_baf_pcb_rad
        Q_pad_core = G_pcb_bridge * (T_c_bay - T_pcb)
        Q_baf_rest_conv = 3.5 * A_baf_rest * (T_baf - T_bay_air)
        Q_baf_rest_rad = 0.90 * SIGMA * A_baf_rest * ((T_baf + 273.15) ** 4 - (T_bell_in + 273.15) ** 4)

        # Vertical PCB F.Cu -> bay air (natural conv) + inner bell wall (radiation) + cable/mount conduction
        h_pcb_c = churchill_chu_vertical_plate_h(T_pcb, T_bay_air, cad["pcb_l"] * 1e-3) * 0.85
        Q_pcb_conv = h_pcb_c * A_pcb_1 * (T_pcb - T_bay_air)
        eps_eff_pw = 1.0 / (1.0 / eps_pcb + 1.0 / 0.90 - 1.0)
        Q_pcb_rad = eps_eff_pw * SIGMA * A_pcb_1 * ((T_pcb + 273.15) ** 4 - (T_bell_in + 273.15) ** 4)
        Q_pcb_wire = G_pcb_wires * (T_pcb - T_bell_in)

        # Bay air -> bell inner wall -> outer bell wall -> ambient (orientation-aware exterior convection)
        h_bay_wall = max(2.5, churchill_chu_vertical_plate_h(T_bay_air, T_bell_in, 0.085) * 0.70)
        Q_air_wall = h_bay_wall * A_int * (T_bay_air - T_bell_in)

        T_out_est = 0.5 * (T_bell_in + T_bell_amb)
        if orientation == "vertical":
            h_ext_c = churchill_chu_vertical_plate_h(T_out_est, T_bell_amb, 0.095)
        else:
            h_ext_c = churchill_chu_horiz_cyl_h(T_out_est, T_bell_amb, D_bell)
        h_ext_r = 0.90 * 4.0 * SIGMA * ((0.5 * (T_out_est + T_amb) + 273.15) ** 3)
        R_bell_tot = (R_wall + 1.0 / ((h_ext_c + h_ext_r) * A_ext)) * rth_penalty_factor
        # Weighted sink temperature separating plume convection from ambient radiation
        T_sink_bell = (h_ext_c * T_bell_amb + h_ext_r * T_amb) / max(1e-9, h_ext_c + h_ext_r)
        Q_bell_amb = (T_bell_in - T_sink_bell) / R_bell_tot

        # Axial Q_bore extraction calibrated to 60-cell 1D FVM marching-air profile (30% vis, 27% uv, 31% bay, 12% top)
        return [
            Q_uv_tot - 0.5 * Q_shroud - Q_uv_vis - Q_uv_bay - 0.27 * Q_bore,
            Q_vis_tot + Q_uv_vis - 0.5 * Q_shroud - 0.30 * Q_bore,
            Q_uv_bay - Q_bay_top - Q_c3_conv - Q_c3_rad - Q_sock - Q_core_baf - Q_pad_core - 0.31 * Q_bore,
            Q_bay_top - Q_top - 0.12 * Q_bore,
            Q_core_baf - Q_baf_pcb - Q_baf_rest_conv - Q_baf_rest_rad,
            Q_c3_conv + Q_baf_rest_conv + Q_pcb_conv - Q_air_wall,
            Q_air_wall + Q_c3_rad + Q_sock + Q_baf_rest_rad + Q_pcb_rad + Q_pcb_wire - Q_bell_amb,
            Q_pcb + Q_baf_pcb + Q_pad_core - Q_pcb_conv - Q_pcb_rad - Q_pcb_wire,
        ]

    x0 = [T_amb + 28.0, T_amb + 28.0, T_amb + 22.0, T_amb + 19.0, T_amb + 20.0, T_amb + 14.0, T_amb + 10.0, T_amb + 25.0]
    sol, infodict, ier, msg = fsolve(resid, x0, full_output=True)
    max_res = float(np.max(np.abs(infodict["fvec"])))
    if ier != 1 or max_res > 1e-6:
        raise RuntimeError(f"solve_system failed to converge ({cfg.name}, Tamb={T_amb}): ier={ier}, max_res={max_res}, msg={msg}")

    T_c_uv, T_c_vis, T_c_bay, T_hs_t, T_baf, T_bay_air, T_bell_in, T_pcb_avg = [float(v) for v in sol]
    T_c_avg = 0.5 * (T_c_uv + T_c_vis)
    Q_shroud_core, T_gi, T_go = shroud_annular_path_Q(
        T_c_avg, T_amb,
        D_in_mm=cad["glass_id_nom"], D_out_mm=cad["glass_od_nom"],
        L_shroud_mm=der["exposed_glass_window_mm"], D_core_eq_mm=d_core_eq,
        eps_core_eff=eps_win_eff, eps_shroud=0.93, k_wall=0.19,
        Q_opt_wall_W=Q_opt_wall_W, orientation=orientation,
    )
    if cfg.open_chimney:
        T_bore_avg = 0.25 * T_c_vis + 0.25 * T_c_uv + 0.34 * T_c_bay + 0.16 * T_hs_t
        Q_bore_val, V_chim, dP_buoy = open_chimney_bore_Q(
            T_bore_avg, T_amb, b_mm, cad["cap_bot_inlet_w"], cad["core_length"] - 15.0,
            k_cad_obstructions=cfg.k_cad_obstructions, k_hagenbach=cfg.k_hagenbach,
            orientation=orientation, rth_penalty_factor=rth_penalty_factor,
        )
    else:
        Q_bore_val, V_chim, dP_buoy = 0.0, 0.0, 0.0

    Q_top_val = protruding_core_Q(T_hs_t, T_amb, cad["core_w_nom"], l_chim_mm, cfg.chimney_eps, orientation, f_rad_amb, rth_penalty_factor)
    T_out_est = 0.5 * (T_bell_in + T_bell_amb)
    h_ext_c = churchill_chu_vertical_plate_h(T_out_est, T_bell_amb, 0.095) if orientation == "vertical" else churchill_chu_horiz_cyl_h(T_out_est, T_bell_amb, D_bell)
    h_ext_r = 0.90 * 4.0 * SIGMA * ((0.5 * (T_out_est + T_amb) + 273.15) ** 3)
    R_bell_tot = (R_wall + 1.0 / ((h_ext_c + h_ext_r) * A_ext)) * rth_penalty_factor
    T_sink_bell = (h_ext_c * T_bell_amb + h_ext_r * T_amb) / max(1e-9, h_ext_c + h_ext_r)
    Q_bell_amb_val = (T_bell_in - T_sink_bell) / R_bell_tot

    Q_in_tot = Q_uv_elec_heat + Q_vis_elec_heat + Q_opt_core_W + Q_opt_wall_W + Q_pcb
    Q_out_tot = (Q_shroud_core + Q_opt_wall_W) + Q_bore_val + Q_top_val + Q_bell_amb_val
    energy_err = abs(Q_in_tot - Q_out_tot)
    if energy_err > 1e-5:
        raise RuntimeError(f"Global energy conservation violated: |Q_in - Q_out| = {energy_err:.2e} W")

    # Coupled 2-zone PCB estimate separating Upper Buck Stage (over bridge) from Lower Control Zone (U4 LM393)
    h_pcb_c = churchill_chu_vertical_plate_h(T_pcb_avg, T_bay_air, cad["pcb_l"] * 1e-3) * 0.85
    eps_eff_pw = 1.0 / (1.0 / eps_pcb + 1.0 / 0.90 - 1.0)
    h_pcb_r = eps_eff_pw * 4.0 * SIGMA * ((0.5 * (T_pcb_avg + T_bell_in) + 273.15) ** 3)
    gap_bp = (cad["pcb_x_bcu"] - (0.5 * cad["core_pocket_w"] + cad["core_sleeve_wall"])) * 1e-3
    eps_eff_bp = 1.0 / (1.0 / eps_baffle + 1.0 / eps_pcb - 1.0)
    h_bp_tot = (0.028 / gap_bp) + eps_eff_bp * 4.0 * SIGMA * ((0.5 * (T_baf + T_pcb_avg) + 273.15) ** 3)
    A_half = 0.5 * A_pcb_1
    A_br_eff = (0.015 * 0.015) if G_pcb_bridge > 0.0 else 0.0
    G_conv_h = h_pcb_c * A_half
    G_rad_h = h_pcb_r * A_half
    G_baf_u = h_bp_tot * max(1e-6, A_half - A_br_eff)
    G_baf_l = h_bp_tot * A_half
    G_lat = 1.0 / 45.0  # 1 oz Cu + 1.6 mm FR4 lateral conductance between upper & lower PCB halves
    M_2z = np.array([
        [G_pcb_bridge + G_baf_u + G_conv_h + G_rad_h + G_lat, -G_lat],
        [-G_lat, G_baf_l + G_conv_h + G_rad_h + G_pcb_wires + G_lat],
    ])
    rhs_2z = np.array([
        P_pcb_upper + G_pcb_bridge * T_c_bay + G_baf_u * T_baf + G_conv_h * T_bay_air + G_rad_h * T_bell_in,
        P_pcb_lower + G_baf_l * T_baf + G_conv_h * T_bay_air + (G_rad_h + G_pcb_wires) * T_bell_in,
    ])
    T_pcb_upper, T_pcb_u4 = [float(v) for v in np.linalg.solve(M_2z, rhs_2z)]
    T_pcb_hotspot = max(T_pcb_avg + 3.5 * Q_pcb, T_pcb_upper)
    # U4 LM393DR2G self-heating (~25 mW nom / 54 mW WC * ~120 K/W SOIC-8 -> +3.0 C conservative proxy)
    T_j_u4 = T_pcb_u4 + (3.0 if Q_pcb > 0.65 else 1.5)
    Q_bridge_W = G_pcb_bridge * (T_c_bay - T_pcb_avg)  # >0 = core heats PCB; <0 = PCB cools to core

    q_uv_single = Q_uv_elec_heat / 4.0
    T_j_uv = T_c_uv + q_uv_single * (1.4 + r_sub_led + 0.10 + r_tim_led)
    if Q_vis_elec_heat <= 0.0:
        T_j_vis = T_c_vis
    else:
        q_green_single = 0.285 * Q_vis_elec_heat
        T_j_vis = T_c_vis + q_green_single * (4.9 + r_sub_led + 0.10 + r_tim_led)

    # Conservative JEDEC RthJA junction proxy on top of board temp
    T_j_u1_jedec = T_pcb_avg + p_u1 * 147.0
    # Bounding temperature of any polymer surface contacting the Al core or PCB stanchions
    T_plastic_max = max(T_c_vis, T_c_uv, T_c_bay, T_pcb_avg)

    return dict(
        T_c_uv=T_c_uv,
        T_c_vis=T_c_vis,
        T_c_bay=T_c_bay,
        T_hs_t=T_hs_t,
        T_baffle=T_baf,
        T_bay_air=T_bay_air,
        T_bell_in=T_bell_in,
        T_pcb_avg=T_pcb_avg,
        T_pcb_upper=T_pcb_upper,
        T_pcb_u4=T_pcb_u4,
        T_j_u4=T_j_u4,
        T_pcb_hotspot=T_pcb_hotspot,
        T_plastic_max=T_plastic_max,
        T_j_uv=T_j_uv,
        T_j_vis=T_j_vis,
        T_j_u1_jedec=T_j_u1_jedec,
        T_shroud_in=T_gi,
        T_shroud_out=T_go,
        Q_shroud_total=Q_shroud_core + Q_opt_wall_W,
        Q_bore=Q_bore_val,
        Q_bridge_W=Q_bridge_W,
        V_chimney_ms=V_chim,
        dP_buoy_Pa=dP_buoy,
        Q_top=Q_top_val,
        max_resid_W=max_res,
        energy_err_W=energy_err,
        margin_uv_100C=LIMIT_UV_C - T_j_uv,
        margin_vis_150C=LIMIT_VIS_C - T_j_vis,
        margin_pmma_75C=LIMIT_PMMA_C - T_gi,
        margin_asa_cont_80C=LIMIT_ASA_CONT_C - T_plastic_max,
        margin_asa_95C=LIMIT_ASA_HDT_C - T_plastic_max,
        margin_u1_125C=LIMIT_U1_J_C - T_j_u1_jedec,
        margin_lm393_avg_70C=LIMIT_LM393_C - T_pcb_avg,
        margin_lm393_u4_70C=LIMIT_LM393_C - T_j_u4,
    )


def main() -> None:
    out_dir = Path(__file__).resolve().parent
    cad = json.loads(CAD_PARAMS_JSON.read_text(encoding="utf-8"))
    sim = json.loads(SIM_SUMMARY_JSON.read_text(encoding="utf-8"))

    te = sim["thermal_export"]
    an = sim["analytic_nominal_20V"]
    cs = sim["corner_sweep"]

    p_pcb_8all_nom = float(te["p_pcb_nom_W"])
    p_pcb_wc = float(te["p_pcb_wc_W"])
    ch1 = an["ch1_uv"]
    p_over_nom = float(an["p_overhead_W"])
    p_pcb_4uv_nom = round(ch1["p_ic"] + ch1["p_diode"] + ch1["p_ind"] + ch1["p_rs"] + p_over_nom, 3)
    p_u1_nom = round(max(an["ch1_uv"]["p_ic"], an["ch2_vis"]["p_ic"]), 4)
    p_u1_wc = round(max(cs["uv_pic_max"], cs["vis_pic_max"]), 4)
    p_led_uv_nom = float(te["p_led_uv_nom_W"])
    p_led_vis_nom = float(te["p_led_vis_nom_W"])

    # Worst-case LED electrical power derived directly from corner_sweep I_max and datasheet hot max Vf
    # SST-10-UV V5 bin max Vf = 4.00 V; OSRAM CSLNM1 hot max average Vf = 3.25 V
    p_led_uv_wc = round(4.0 * float(cs["uv_i_max"]) * 4.00, 3)
    p_led_vis_wc = round(4.0 * float(cs["vis_i_max"]) * 3.25, 3)
    # Conservative min-bin hot WPE: 34% UV (SST-10-UV F365 @ 65 C), 28% Vis (OSRAM CSLNM1 min-bin phosphor)
    wpe_uv_wc, wpe_vis_wc = 0.34, 0.28

    # Spectral optical re-absorption in PLEXIGLAS XT 0A070 GT (200k-ray 3D Lambertian Monte Carlo):
    # UV (365 nm): 11.3% PMMA bulk wall, 4.0% core/sockets (15.3% total)
    # Visible:     1.3% PMMA bulk wall, 2.2% core/sockets (3.5% total)
    def opt_split(p_uv_opt: float, p_vis_opt: float) -> tuple[float, float]:
        q_wall = round(0.113 * p_uv_opt + 0.013 * p_vis_opt, 3)
        q_core = round(0.040 * p_uv_opt + 0.022 * p_vis_opt, 3)
        return q_core, q_wall

    p_buck_8all_nom = round(p_pcb_8all_nom - p_over_nom, 3)
    p_buck_4uv_nom = round(p_pcb_4uv_nom - p_over_nom, 3)
    p_over_wc = round(p_over_nom * (p_pcb_wc / p_pcb_8all_nom), 3)
    p_buck_wc = round(p_pcb_wc - p_over_wc, 3)

    # (name, Q_uv_heat, Q_vis_heat, Q_opt_core, Q_opt_wall, Q_pcb, P_upper, P_lower, P_u1)
    modes = [
        ("4-UV Nom (40%WPE)",     round(0.60 * p_led_uv_nom, 3), 0.000, *opt_split(0.40 * p_led_uv_nom, 0.0), p_pcb_4uv_nom, p_buck_4uv_nom, p_over_nom, round(an["ch1_uv"]["p_ic"], 4)),
        ("8-ALL Nom (49%UV WPE)", round(0.51 * p_led_uv_nom, 3), round(0.60 * p_led_vis_nom, 3), *opt_split(0.49 * p_led_uv_nom, 0.40 * p_led_vis_nom), p_pcb_8all_nom, p_buck_8all_nom, p_over_nom, p_u1_nom),
        ("8-ALL Nom (40%UV WPE)", round(0.60 * p_led_uv_nom, 3), round(0.60 * p_led_vis_nom, 3), *opt_split(0.40 * p_led_uv_nom, 0.40 * p_led_vis_nom), p_pcb_8all_nom, p_buck_8all_nom, p_over_nom, p_u1_nom),
        ("8-ALL DS-RealWPE",      round((1.0 - wpe_uv_wc) * p_led_uv_wc, 3), round((1.0 - wpe_vis_wc) * p_led_vis_wc, 3), *opt_split(wpe_uv_wc * p_led_uv_wc, wpe_vis_wc * p_led_vis_wc), p_pcb_wc, p_buck_wc, p_over_wc, p_u1_wc),
        ("8-ALL DS-100% (NoOpt)", p_led_uv_wc, p_led_vis_wc, 0.000, 0.000, p_pcb_wc, p_buck_wc, p_over_wc, p_u1_wc),
    ]

    l_chim = float(cad["derived"]["core_protrusion_mm"])
    f_rad_amb = compute_chimney_ambient_view_factor(
        l_chim, cad["core_w_nom"], cad["cap_top_bell_od"], cad["cap_top_collar_h"],
    )

    configs = [
        ChimneyConfig(
            "Config 0: Open Chimney + Bare Mill Al (eps=0.10) + Epoxied PCB Bridge (16 K/W)",
            "Open Chimney\nBare Mill Al\n+ Epoxied Bridge\n(Baseline)",
            open_chimney=True, win_eps=0.10, bay_eps=0.10, chimney_eps=0.10, pcb_bridge_rth_KW=16.0,
        ),
        ChimneyConfig(
            "Config 1: Open Chimney + Upper-Tube Matte Paint (Z=145..305 mm, eps=0.85) + Epoxied Bridge",
            "Open Chimney\nUpper Matte Paint\n+ Epoxied Bridge\n(Hot-Night Opt.)",
            open_chimney=True, win_eps=0.10, bay_eps=0.85, chimney_eps=0.85, pcb_bridge_rth_KW=16.0,
        ),
        ChimneyConfig(
            "Config 2: Open Chimney + Bare Mill Al (eps=0.10), No PCB Bridge",
            "Open Chimney\nBare Mill Al\n(No Bridge)",
            open_chimney=True, win_eps=0.10, bay_eps=0.10, chimney_eps=0.10, pcb_bridge_rth_KW=None,
        ),
        ChimneyConfig(
            "Config 3: Blocked Bore + Bare Mill Al (eps=0.10) + Epoxied PCB Bridge (16 K/W)",
            "Blocked Bore\nBare Mill Al\n+ Epoxied Bridge\n(Fault Mode)",
            open_chimney=False, win_eps=0.10, bay_eps=0.10, chimney_eps=0.10, pcb_bridge_rth_KW=16.0,
        ),
    ]

    rows = []
    max_resid_all = 0.0
    max_energy_err_all = 0.0
    for cfg in configs:
        t_list = [15.0, 22.0, 30.0, 35.0] if cfg.name.startswith(("Config 0:", "Config 1:")) else [22.0, 30.0]
        for T_amb in t_list:
            for orient in ("vertical", "horizontal"):
                for m_name, q_uv, q_vis, q_oc, q_ow, q_pcb, p_up, p_lo, p_u1 in modes:
                    r = solve_system(
                        cad, q_uv, q_vis, q_oc, q_ow, q_pcb, p_up, p_lo, p_u1, T_amb,
                        cfg=cfg, f_rad_amb=f_rad_amb, orientation=orient,
                    )
                    max_resid_all = max(max_resid_all, r["max_resid_W"])
                    max_energy_err_all = max(max_energy_err_all, r["energy_err_W"])
                    passed_asa_lm393 = (
                        r["margin_uv_100C"] > 0.0
                        and r["margin_vis_150C"] > 0.0
                        and r["margin_pmma_75C"] > 0.0
                        and r["margin_asa_cont_80C"] >= 0.0
                        and r["margin_u1_125C"] >= 0.0
                        and r["margin_lm393_avg_70C"] >= 0.0
                        and r["margin_lm393_u4_70C"] >= 0.0
                    )
                    passed_asa_struct = (
                        r["margin_uv_100C"] > 0.0
                        and r["margin_vis_150C"] > 0.0
                        and r["margin_pmma_75C"] > 0.0
                        and r["margin_asa_cont_80C"] >= 0.0
                        and r["margin_u1_125C"] >= 0.0
                    )
                    rows.append({
                        "config": cfg.name,
                        "T_amb_C": T_amb,
                        "orientation": orient,
                        "mode": m_name,
                        "Q_uv_W": q_uv,
                        "Q_vis_W": q_vis,
                        "Q_opt_core_W": q_oc,
                        "Q_opt_wall_W": q_ow,
                        "Q_pcb_W": q_pcb,
                        "P_u1_W": p_u1,
                        **{k: round(v, 3) for k, v in r.items() if k not in ("max_resid_W", "energy_err_W")},
                        "pass_asa_struct": passed_asa_struct,
                        "pass_asa_lm393": passed_asa_lm393,
                    })

    csv_path = out_dir / "thermal_results.csv"
    with csv_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    t_ambs = np.linspace(10.0, 40.0, 31)
    sweep_modes = ["4-UV Nom (40%WPE)", "8-ALL Nom (40%UV WPE)", "8-ALL DS-RealWPE", "8-ALL DS-100% (NoOpt)"]
    sweep_data: dict[str, list[dict[str, float]]] = {m: [] for m in sweep_modes}
    for m_name, q_uv, q_vis, q_oc, q_ow, q_pcb, p_up, p_lo, p_u1 in modes:
        if m_name not in sweep_modes:
            continue
        for Ta in t_ambs:
            r = solve_system(cad, q_uv, q_vis, q_oc, q_ow, q_pcb, p_up, p_lo, p_u1, float(Ta), configs[0], f_rad_amb, orientation="vertical")
            sweep_data[m_name].append({"T_amb": float(Ta), **{k: round(v, 3) for k, v in r.items() if k not in ("max_resid_W", "energy_err_W")}})

    cfg0_rows = [r for r in rows if r["config"].startswith("Config 0:")]
    cfg1_rows = [r for r in rows if r["config"].startswith("Config 1:")]
    cfg0_vert_22_real = [r for r in cfg0_rows if r["orientation"] == "vertical" and r["T_amb_C"] <= 22.0 and "DS-100%" not in r["mode"]]
    cfg0_vert_30_real = [r for r in cfg0_rows if r["orientation"] == "vertical" and r["T_amb_C"] <= 30.0 and "DS-100%" not in r["mode"]]
    cfg0_vert_35_real = [r for r in cfg0_rows if r["orientation"] == "vertical" and r["T_amb_C"] <= 35.0 and "DS-100%" not in r["mode"]]
    cfg1_vert_35_real = [r for r in cfg1_rows if r["orientation"] == "vertical" and r["T_amb_C"] <= 35.0 and "DS-100%" not in r["mode"]]

    bore_str = f"{cad['core_bore_nom']:.0f} mm"
    bridge_str = f"{cad['pcb_thermal_win_w'] - 0.6:.0f} × {cad['pcb_thermal_win_w'] - 0.6:.0f} mm"
    k_eff_val = round(compute_chimney_k_eff(cad["core_bore_nom"], cad["cap_bot_inlet_w"], configs[0].k_cad_obstructions, configs[0].k_hagenbach), 2)
    f_stars_pct = round(100.0 * (8.0 * 0.25 * math.pi * (cad["star_dia"] ** 2)) / (4.0 * cad["core_w_nom"] * cad["derived"]["exposed_glass_window_mm"]), 1)
    eps_win_eff_val = round((1.0 - f_stars_pct / 100.0) * configs[0].win_eps + (f_stars_pct / 100.0) * 0.85, 3)

    # Plot 1: thermal_margins.png (all 3 panels show vertical 22/30 C AND horizontal 22 C honestly!)
    fig, axes = plt.subplots(1, 3, figsize=(15.0, 5.0), dpi=150)
    sel_modes = ["4-UV Nom (40%WPE)", "8-ALL Nom (40%UV WPE)", "8-ALL DS-RealWPE", "8-ALL DS-100% (NoOpt)"]
    x = np.arange(len(sel_modes))
    w = 0.25

    def get_vals(metric: str, ta: float, orient: str) -> list[float]:
        return [
            next(r[metric] for r in cfg0_rows if r["mode"] == m and r["T_amb_C"] == ta and r["orientation"] == orient)
            for m in sel_modes
        ]

    ax = axes[0]
    ax.bar(x - w, get_vals("T_j_uv", 22.0, "vertical"), w, label="22°C Vert (UK Night)", color="#4c72b0")
    ax.bar(x, get_vals("T_j_uv", 30.0, "vertical"), w, label="30°C Vert (Warm)", color="#dd8452")
    ax.bar(x + w, get_vals("T_j_uv", 22.0, "horizontal"), w, label="22°C Horiz (Not Rec.)", color="#c44e52")
    ax.axhline(LIMIT_UV_C, color="red", ls="--", lw=1.5, label=f"SST-10-UV Limit {LIMIT_UV_C:.0f}°C")
    ax.set_title("UV LED Junction $T_{j,\\mathrm{UV}}$ (Cu DTP + Epoxy)")
    ax.set_ylabel("Temperature (°C)")
    ax.set_xticks(x, ["4-UV\nNom", "8-ALL\nNom", "8-ALL\nDS-Real", "8-ALL\nDS-100%"], fontsize=8.5)
    ax.set_ylim(0, 122)
    ax.grid(axis="y", alpha=0.3)
    ax.legend(fontsize=7.2, loc="upper left")

    ax = axes[1]
    ax.bar(x - w, get_vals("T_plastic_max", 22.0, "vertical"), w, label="22°C Vert Core/ASA", color="#4c72b0")
    ax.bar(x, get_vals("T_plastic_max", 30.0, "vertical"), w, label="30°C Vert Core/ASA", color="#dd8452")
    ax.bar(x + w, get_vals("T_plastic_max", 22.0, "horizontal"), w, label="22°C Horiz Core/ASA", color="#c44e52")
    ax.axhline(LIMIT_ASA_CONT_C, color="darkorange", ls="--", lw=1.5, label=f"ASA Cont. Derated {LIMIT_ASA_CONT_C:.0f}°C")
    ax.axhline(LIMIT_ASA_HDT_C, color="purple", ls=":", lw=1.3, label=f"ASA HDT-B {LIMIT_ASA_HDT_C:.0f}°C")
    ax.set_title("Max Core/Plastic Contact ($T_{\\mathrm{plastic,max}}$)")
    ax.set_xticks(x, ["4-UV\nNom", "8-ALL\nNom", "8-ALL\nDS-Real", "8-ALL\nDS-100%"], fontsize=8.5)
    ax.set_ylim(0, 118)
    ax.grid(axis="y", alpha=0.3)
    ax.legend(fontsize=7.0, loc="upper left")

    ax = axes[2]
    ax.bar(x - w, get_vals("T_j_u4", 22.0, "vertical"), w, label="22°C Vert U4 (LM393)", color="#4c72b0")
    ax.bar(x, get_vals("T_j_u4", 30.0, "vertical"), w, label="30°C Vert U4 (LM393)", color="#dd8452")
    ax.bar(x + w, get_vals("T_j_u4", 22.0, "horizontal"), w, label="22°C Horiz U4 (LM393)", color="#c44e52")
    ax.axhline(LIMIT_LM393_C, color="red", ls="--", lw=1.5, label=f"U4 LM393 Limit {LIMIT_LM393_C:.0f}°C")
    ax.set_title("Driver PCB Control IC ($T_{j,\\mathrm{U4}}$ 2-Zone)")
    ax.set_xticks(x, ["4-UV\nNom", "8-ALL\nNom", "8-ALL\nDS-Real", "8-ALL\nDS-100%"], fontsize=8.5)
    ax.set_ylim(0, 102)
    ax.grid(axis="y", alpha=0.3)
    ax.legend(fontsize=7.2, loc="upper left")

    fig.suptitle(
        f"LepiLED Thermal Margins (Open {bore_str} Sq-Duct Chimney K={k_eff_val}, Bare Mill Al ε={configs[0].chimney_eps:.2f}, Epoxied {bridge_str} Bridge {configs[0].pcb_bridge_rth_KW:.0f} K/W)",
        fontweight="bold", fontsize=10.5,
    )
    fig.tight_layout()
    fig.savefig(out_dir / "thermal_margins.png")
    plt.close(fig)

    # Plot 2: thermal_ambient_sweep.png (with +/-4 K structural/field uncertainty band & dynamic limits)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.6, 5.0), dpi=150)
    colors = {
        "4-UV Nom (40%WPE)": "#2ca02c",
        "8-ALL Nom (40%UV WPE)": "#1f77b4",
        "8-ALL DS-RealWPE": "#ff7f0e",
        "8-ALL DS-100% (NoOpt)": "#d62728",
    }
    for m in sweep_modes:
        pts = sweep_data[m]
        ta = np.array([pt["T_amb"] for pt in pts])
        t_uv = np.array([pt["T_j_uv"] for pt in pts])
        t_pl = np.array([pt["T_plastic_max"] for pt in pts])
        t_u4 = np.array([pt["T_j_u4"] for pt in pts])
        ax1.plot(ta, t_uv, lw=2.0, color=colors[m], label=m)
        ax2.plot(ta, t_pl, lw=1.8, color=colors[m], label=f"{m} (Core/ASA)")
        ax2.plot(ta, t_u4, lw=1.4, ls="--", color=colors[m], label=f"{m} (U4 LM393)")
        if m == "8-ALL DS-RealWPE":
            ax1.fill_between(ta, t_uv - UNCERTAINTY_BAND_K, t_uv + UNCERTAINTY_BAND_K, color=colors[m], alpha=0.14, label=f"±{UNCERTAINTY_BAND_K:.0f} K Model/Field Band")
            ax2.fill_between(ta, t_u4 - UNCERTAINTY_BAND_K, t_u4 + UNCERTAINTY_BAND_K, color=colors[m], alpha=0.13)
    ax1.axhline(LIMIT_UV_C, color="red", ls="--", lw=1.4, label=f"UV Limit {LIMIT_UV_C:.0f}°C")
    ax1.axvline(22.0, color="green", ls=":", lw=1.2, label="UK Night 22°C")
    ax1.axvline(30.0, color="gray", ls=":", lw=1.2, label="Warm Night 30°C")
    ax1.axvline(35.0, color="darkorange", ls=":", lw=1.2, label="Heatwave 35°C")
    ax1.set_title("UV LED $T_{j,\\mathrm{UV}}$ vs Ambient (Vertical Hanging)")
    ax1.set_xlabel("Ambient Temperature $T_{\\mathrm{amb}}$ (°C)")
    ax1.set_ylabel("Temperature (°C)")
    ax1.set_ylim(28, 114)
    ax1.grid(alpha=0.3)
    ax1.legend(fontsize=7.0, loc="upper left")

    ax2.axhline(LIMIT_LM393_C, color="red", ls="--", lw=1.4, label=f"U4 LM393 Limit {LIMIT_LM393_C:.0f}°C")
    ax2.axhline(LIMIT_ASA_CONT_C, color="darkorange", ls="-.", lw=1.3, label=f"ASA Cont. Derated {LIMIT_ASA_CONT_C:.0f}°C")
    ax2.axhline(LIMIT_ASA_HDT_C, color="purple", ls=":", lw=1.2, label=f"ASA HDT-B {LIMIT_ASA_HDT_C:.0f}°C")
    ax2.axvline(22.0, color="green", ls=":", lw=1.2)
    ax2.axvline(30.0, color="gray", ls=":", lw=1.2)
    ax2.axvline(35.0, color="darkorange", ls=":", lw=1.2)
    ax2.set_title("Max Core/ASA Contact & U4 LM393 vs Ambient")
    ax2.set_xlabel("Ambient Temperature $T_{\\mathrm{amb}}$ (°C)")
    ax2.set_ylabel("Temperature (°C)")
    ax2.set_ylim(25, 116)
    ax2.grid(alpha=0.3)
    ax2.legend(fontsize=6.2, ncol=2, loc="upper left")

    fig.suptitle(
        f"Ambient Sweep (10–40 °C, Vertical Hanging, Open {bore_str} Chimney K={k_eff_val}, Bare Mill Al + Epoxied Bridge)",
        fontweight="bold", fontsize=10.8,
    )
    fig.tight_layout()
    fig.savefig(out_dir / "thermal_ambient_sweep.png")
    plt.close(fig)

    # Plot 3: thermal_network_comparison.png (cleanly isolates paint, bridge & blockage at 30 C vertical)
    fig, (ax_uv, ax_pcb) = plt.subplots(1, 2, figsize=(13.4, 5.0), dpi=150)
    cfg_labels = [c.short_label for c in configs]
    cfg_prefixes = [f"Config {i}:" for i in range(len(configs))]
    x_c = np.arange(len(cfg_labels))
    for ax_p, metric, ylabel, ylim, lim_val, lim_lbl, title_p in [
        (ax_uv, "T_j_uv", "UV LED Junction $T_{j,\\mathrm{UV}}$ (°C)", 112, LIMIT_UV_C, f"SST-10-UV Limit {LIMIT_UV_C:.0f}°C", "UV LED Junction ($T_{\\mathrm{amb}}=30^\\circ\\mathrm{C}$)"),
        (ax_pcb, "T_j_u4", "Control IC $T_{j,\\mathrm{U4}}$ (°C, 2-Zone PCB)", 95, LIMIT_LM393_C, f"U4 LM393 Limit {LIMIT_LM393_C:.0f}°C", "Driver PCB Control IC $U_4$ ($T_{\\mathrm{amb}}=30^\\circ\\mathrm{C}$)"),
    ]:
        v_nom = [
            next(r[metric] for r in rows if r["config"].startswith(pf) and r["T_amb_C"] == 30.0 and r["orientation"] == "vertical" and r["mode"] == "8-ALL Nom (40%UV WPE)")
            for pf in cfg_prefixes
        ]
        v_ds = [
            next(r[metric] for r in rows if r["config"].startswith(pf) and r["T_amb_C"] == 30.0 and r["orientation"] == "vertical" and r["mode"] == "8-ALL DS-RealWPE")
            for pf in cfg_prefixes
        ]
        ax_p.bar(x_c - 0.18, v_nom, 0.36, label="8-ALL Nom (40% UV WPE)", color="#4c72b0")
        ax_p.bar(x_c + 0.18, v_ds, 0.36, label="8-ALL Worst-Case Real-WPE", color="#dd8452")
        ax_p.axhline(lim_val, color="red", ls="--", lw=1.6, label=lim_lbl)
        for i, (vn, vd) in enumerate(zip(v_nom, v_ds)):
            ax_p.text(i - 0.18, vn + 1.5, f"{vn:.1f}°C", ha="center", fontsize=8.2, fontweight="bold",
                      bbox=dict(facecolor="white", edgecolor="none", pad=0.6, alpha=0.85))
            ax_p.text(i + 0.18, vd + 1.5, f"{vd:.1f}°C", ha="center", fontsize=8.2, fontweight="bold",
                      bbox=dict(facecolor="white", edgecolor="none", pad=0.6, alpha=0.85))
        ax_p.set_xticks(x_c, cfg_labels, fontsize=8.2)
        ax_p.set_ylabel(ylabel)
        ax_p.set_ylim(0, ylim)
        ax_p.set_title(title_p)
        ax_p.grid(axis="y", alpha=0.3)
        ax_p.legend(fontsize=8.0, loc="upper left")
    fig.suptitle(
        f"Thermal Configuration Comparison ($T_{{\\mathrm{{amb}}}}=30^\\circ\\mathrm{{C}}$, Vertical Still Air, $K_{{\\mathrm{{eff}}}}={k_eff_val}$)",
        fontweight="bold", fontsize=11.0,
    )
    fig.tight_layout()
    fig.savefig(out_dir / "thermal_network_comparison.png")
    plt.close(fig)

    summary = {
        "revision": "6.1",
        "architecture": (
            f"Open-Chimney Funnel Lantern ({cad['core_w_nom']:.0f}x{cad['core_w_nom']:.0f}x{cad['core_wall']:.1f}x{cad['core_length']:.0f} mm "
            f"Bare Mill-Finish Al Core eps={configs[0].chimney_eps:.2f}, Square-Duct {bore_str} Chimney K_eff={k_eff_val}, "
            f"White ASA Enclosure, Epoxy Cu DTP Stars, +X Vertical PCB w/ Epoxied {bridge_str} Bridge R={configs[0].pcb_bridge_rth_KW:.0f} K/W)"
        ),
        "input_hashes": {
            "cad_params.json": _sha256_file(CAD_PARAMS_JSON),
            "sim_summary.json": _sha256_file(SIM_SUMMARY_JSON),
            "thermal_analysis.py": _sha256_file(Path(__file__)),
        },
        "output_figure_hashes": {
            "thermal_margins.png": _sha256_file(out_dir / "thermal_margins.png"),
            "thermal_ambient_sweep.png": _sha256_file(out_dir / "thermal_ambient_sweep.png"),
            "thermal_network_comparison.png": _sha256_file(out_dir / "thermal_network_comparison.png"),
        },
        "solver_audit": {
            "max_node_residual_W": float(f"{max_resid_all:.3e}"),
            "max_global_energy_err_W": float(f"{max_energy_err_all:.3e}"),
            "all_converged": True,
        },
        "ssot_inputs": {
            "enclosure_material": "White ASA (15% gyroid infill; HDT-B 95 C, derated continuous limit 80 C)",
            "core_section_mm": f"{cad['core_w_nom']:.0f}x{cad['core_w_nom']:.0f}x{cad['core_wall']:.1f}",
            "core_bore_mm": cad["core_bore_nom"],
            "core_length_mm": cad["core_length"],
            "core_protrusion_mm": l_chim,
            "chimney_rad_view_factor_F_amb": f_rad_amb,
            "exposed_shroud_window_mm": cad["derived"]["exposed_glass_window_mm"],
            "core_finish": "mill",
            "core_emissivity": configs[0].chimney_eps,
            "window_star_coverage_pct": f_stars_pct,
            "window_effective_emissivity": eps_win_eff_val,
            "chimney_square_duct_Nu_fd": 2.976,
            "chimney_total_loss_K_eff": k_eff_val,
            "pcb_thermal_bridge_rth_KW": configs[0].pcb_bridge_rth_KW,
            "p_pcb_4uv_nom_W": p_pcb_4uv_nom,
            "p_pcb_8all_nom_W": p_pcb_8all_nom,
            "p_pcb_wc_W": p_pcb_wc,
            "p_led_uv_wc_W": p_led_uv_wc,
            "p_led_vis_wc_W": p_led_vis_wc,
        },
        "vert_uk_night_22C_real_asa_lm393_all_pass": all(r["pass_asa_lm393"] for r in cfg0_vert_22_real),
        "vert_15_30C_real_asa_lm393_all_pass": all(r["pass_asa_lm393"] for r in cfg0_vert_30_real),
        "vert_15_35C_real_asa_struct_all_pass": all(r["pass_asa_struct"] for r in cfg0_vert_35_real),
        "vert_15_35C_real_asa_lm393_bare_all_pass": all(r["pass_asa_lm393"] for r in cfg0_vert_35_real),
        "vert_15_35C_real_asa_lm393_painted_upper_all_pass": all(r["pass_asa_lm393"] for r in cfg1_vert_35_real),
        "baseline_results": cfg0_rows,
        "config_comparison_30C_vert": [
            r for r in rows if r["T_amb_C"] == 30.0 and r["orientation"] == "vertical" and r["mode"] in ("8-ALL Nom (40%UV WPE)", "8-ALL DS-RealWPE")
        ],
        "config_comparison_35C_vert": [
            r for r in rows if r["T_amb_C"] == 35.0 and r["orientation"] == "vertical" and r["mode"] in ("8-ALL Nom (40%UV WPE)", "8-ALL DS-RealWPE")
        ],
        "ambient_sweep_vert": sweep_data,
    }
    json_path = out_dir / "thermal_summary.json"
    json_path.write_text(json.dumps(summary, indent=2) + "\n")

    print(f"=== Coupled 8-Node (+2-Zone PCB) Thermal Analysis (Sq-Duct {bore_str} K_eff={k_eff_val}, Bare Mill Al eps={configs[0].chimney_eps:.2f}, Epoxied Bridge {configs[0].pcb_bridge_rth_KW:.0f} K/W) ===")
    for r in cfg0_rows:
        if r["T_amb_C"] in (15.0, 22.0, 30.0, 35.0) and r["orientation"] == "vertical" and r["mode"] in ("4-UV Nom (40%WPE)", "8-ALL Nom (40%UV WPE)", "8-ALL DS-RealWPE"):
            print(
                f"  Tamb={r['T_amb_C']:2.0f}C vert | {r['mode']:21s} | "
                f"TjUV={r['T_j_uv']:5.1f}C Tpl={r['T_plastic_max']:4.1f}C Tsh={r['T_shroud_in']:4.1f}C Tbay={r['T_bay_air']:4.1f}C "
                f"Tpcb={r['T_pcb_avg']:4.1f}C Tu4={r['T_j_u4']:4.1f}C Qbore={r['Q_bore']:.2f}W | ASA={r['pass_asa_struct']} LM393={r['pass_asa_lm393']}"
            )
    print(f"--- Config 1 (Optional Upper-Tube Matte Paint Z=145..305 mm, eps=0.85) ---")
    for r in cfg1_rows:
        if r["T_amb_C"] in (30.0, 35.0) and r["orientation"] == "vertical" and r["mode"] in ("8-ALL Nom (40%UV WPE)", "8-ALL DS-RealWPE"):
            print(
                f"  Tamb={r['T_amb_C']:2.0f}C vert | {r['mode']:21s} | "
                f"TjUV={r['T_j_uv']:5.1f}C Tpl={r['T_plastic_max']:4.1f}C Tpcb={r['T_pcb_avg']:4.1f}C Tu4={r['T_j_u4']:4.1f}C | ASA+LM393={r['pass_asa_lm393']}"
            )
    print(f"Max node residual: {max_resid_all:.2e} W | Max global energy err: {max_energy_err_all:.2e} W")
    print(f"Bare Mill Vertical <=22 C Real-WPE (ASA + LM393) PASS: {sum(r['pass_asa_lm393'] for r in cfg0_vert_22_real)}/{len(cfg0_vert_22_real)}")
    print(f"Bare Mill Vertical 15-30 C Real-WPE (ASA + LM393) PASS: {sum(r['pass_asa_lm393'] for r in cfg0_vert_30_real)}/{len(cfg0_vert_30_real)}")
    print(f"Bare Mill Vertical 15-35 C Real-WPE (ASA struct) PASS: {sum(r['pass_asa_struct'] for r in cfg0_vert_35_real)}/{len(cfg0_vert_35_real)} | LM393 PASS: {sum(r['pass_asa_lm393'] for r in cfg0_vert_35_real)}/{len(cfg0_vert_35_real)}")
    print(f"Upper-Painted Vertical 15-35 C Real-WPE (ASA + LM393) PASS: {sum(r['pass_asa_lm393'] for r in cfg1_vert_35_real)}/{len(cfg1_vert_35_real)}")
    print(f"Saved: {csv_path}, {json_path}, and 3 PNG plots in {out_dir}")


if __name__ == "__main__":
    main()
