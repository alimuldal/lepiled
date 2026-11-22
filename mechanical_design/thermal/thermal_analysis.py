#!/usr/bin/env python3
"""
Coupled First-Principles 8-Node Thermal Analysis for LepiLED DIY Maxi Switch.

Reads exact CAD geometry from `mechanical_design/cad/cad_params.json` and electrical power
budgets from `circuit_design/sim/outputs/sim_summary.json`.

8 Coupled Steady-State Nodes:
  1. T_c_uv    : Al core at UV star tier (Z = 94.0 mm)
  2. T_c_vis   : Al core at visible star tier (Z = 60.0 mm)
  3. T_c_bay   : Al core passing through top electronics bay
  4. T_hs_t    : Protruding bare mill Al upper chimney (with plume preheating)
  5. T_baffle  : PCB-facing surface of 2.0 mm plastic thermal baffle (radiates/conducts to B.Cu)
  6. T_bay_air : Top electronics bay air temperature
  7. T_bell_in : Inner wall temperature of white PETG/ASA umbrella bell
  8. T_pcb_avg : Vertically mounted 36 x 46 mm 2L FR4 driver_pcb (F.Cu conv + bell radiation + wire conduction)

Key physical fidelity improvements:
  - Open-chimney internal natural-draft square-duct solver (buoyancy = Poiseuille friction + mesh/inlet drag K_eff)
    coupled directly to core bore dimensions (`26 x 26 mm` inside `30 x 30 x 2.0 mm` Al tube).
  - First-principles vertical PCB heat transfer (no hardcoded R_pcb = 9.5 K/W), explicit baffle-to-B.Cu node,
    25%-infill thick-wall conduction penalty, fresh bare mill Al emissivity (eps = 0.10), and chimney plume penalty.
  - Explicit pass gates checking BOTH electronics (`T_pcb_avg <= 70 C` for commercial U4 LM393DR2G)
    AND polymer HDT on ALL core-contacting plastic nodes (`max(T_c_vis, T_c_uv, T_c_bay, T_pcb_avg)` <= 70 C PETG / 95 C ASA).
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
CAD_PARAMS_JSON = REPO_ROOT / "mechanical_design" / "cad" / "cad_params.json"
SIM_SUMMARY_JSON = REPO_ROOT / "circuit_design" / "sim" / "outputs" / "sim_summary.json"
SIGMA = 5.670374419e-8


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
    dT = max(0.05, T_s - T_amb)
    p = air_props(0.5 * (T_s + T_amb))
    Ra = 9.81 * p["beta"] * dT * (L ** 3) / (p["nu"] * p["alpha"])
    Nu = (0.825 + (0.387 * Ra ** (1.0 / 6.0)) / (1.0 + (0.492 / p["Pr"]) ** (9.0 / 16.0)) ** (8.0 / 27.0)) ** 2
    return Nu * p["k"] / L


def churchill_chu_horiz_cyl_h(T_s: float, T_amb: float, D: float) -> float:
    dT = max(0.05, T_s - T_amb)
    p = air_props(0.5 * (T_s + T_amb))
    Ra = 9.81 * p["beta"] * dT * (D ** 3) / (p["nu"] * p["alpha"])
    Nu = (0.60 + (0.387 * Ra ** (1.0 / 6.0)) / (1.0 + (0.559 / p["Pr"]) ** (9.0 / 16.0)) ** (8.0 / 27.0)) ** 2
    return Nu * p["k"] / D


@dataclass(frozen=True)
class ChimneyConfig:
    name: str
    open_chimney: bool
    chimney_eps: float
    core_inner_eps: float
    k_minor_mesh: float = 8.0   # Conservative minor-loss K for 2x 1 mm stainless mesh + inlet/exhaust turns
    pcb_bridge_rth_KW: float | None = None  # Captive 15x15 mm B.Cu->Al core silicone-pad + brass-shim bridge (None = no bridge)


def compute_chimney_ambient_view_factor(L_chim_mm: float, core_w_mm: float, bell_od_mm: float, collar_h_mm: float) -> float:
    w_shelf = max(0.0, 0.5 * (bell_od_mm - core_w_mm))
    ys = np.linspace(0.5, L_chim_mm, 60)
    h_eff = ys + collar_h_mm
    f_to_eave = float(np.mean(0.5 * (1.0 - h_eff / np.sqrt(h_eff ** 2 + w_shelf ** 2))))
    return round(1.0 - f_to_eave, 4)


def protruding_core_Q(
    T_s: float,
    T_amb: float,
    core_w_mm: float,
    L_mm: float,
    eps: float,
    orientation: str = "vertical",
    f_rad_amb: float = 0.84,
    rth_penalty_factor: float = 1.0,
) -> float:
    """Natural convection (with +2 K rising head-plume preheating) + view-factor-corrected radiation."""
    W = core_w_mm * 1e-3
    L = L_mm * 1e-3
    A_sides = 4.0 * W * L
    T_plume = T_amb + (2.0 if orientation == "vertical" else 0.0)
    dT_c = max(0.05, T_s - T_plume)
    dT_r = max(0.05, T_s - T_amb)
    if orientation == "vertical":
        h_c = churchill_chu_vertical_plate_h(T_s, T_plume, L)
    else:
        h_c = churchill_chu_horiz_cyl_h(T_s, T_plume, 4.0 * W / math.pi)
    Q_conv = h_c * A_sides * dT_c
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
    k_minor_mesh: float = 3.0,
    orientation: str = "vertical",
    rth_penalty_factor: float = 1.0,
) -> tuple[float, float]:
    """
    First-principles buoyancy-driven natural draft inside open unobstructed vertical square Al duct
    with bottom inlet contraction and top rain-finial exhaust turn loss.
    Returns (Q_bore_W, mean_air_velocity_m_s).
    """
    dT = T_wall - T_amb
    if dT <= 0.1:
        return 0.0, 0.0
    b = bore_mm * 1e-3
    L = L_duct_mm * 1e-3
    A_duct = b * b
    A_in = max(1e-6, (inlet_w_mm * 1e-3) ** 2 - (4.0 - math.pi) * (0.003 ** 2))
    area_ratio = A_duct / min(A_duct, A_in)
    K_eff = k_minor_mesh + 1.5 * max(0.0, area_ratio ** 2 - 1.0)
    p = air_props(0.5 * (T_wall + T_amb))

    if orientation != "vertical":
        # Horizontal orientation loses stack buoyancy -> gentle open-end convective exchange (~20% of vertical)
        h_h = 0.25 * churchill_chu_horiz_cyl_h(T_wall, T_amb, b)
        return (h_h * (4.0 * b * L) * dT * 0.25) / rth_penalty_factor, 0.02

    V = 0.14
    eff = 0.7
    for _ in range(35):
        mdot = p["rho"] * V * A_duct
        Re = V * b / p["nu"]
        Gz = (b / L) * Re * p["Pr"]
        Nu_g = 3.66 + (0.0668 * Gz) / (1.0 + 0.04 * (Gz ** (2.0 / 3.0)))
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
    return float(Q_tot), float(V)


def shroud_annular_path_Q(
    T_core: float,
    T_amb: float,
    D_in_mm: float,
    D_out_mm: float,
    L_shroud_mm: float,
    D_core_eq_mm: float,
    eps_core: float,
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
            Nu_d = max(1.0, 0.42 * (Ra_d ** 0.25) * (p["Pr"] ** 0.012) * ((L / delta) ** (-0.3)))
        else:
            D_c, D_o = 2.0 * r_1, 2.0 * r_2
            F_cyl = ((math.log(D_o / D_c)) ** 4) / ((delta ** 3) * (D_c ** (-0.6) + D_o ** (-0.6)) ** 5)
            Ra_c = F_cyl * Ra_d
            k_eff_k = max(1.0, 0.386 * (p["Pr"] / (0.861 + p["Pr"])) ** 0.25 * (Ra_c ** 0.25))
            Nu_d = k_eff_k * delta / (r_1 * math.log(r_2 / r_1))
        h_gap_c = Nu_d * p["k"] / delta
        Q_gap_c = h_gap_c * A_1 * dT_gap
        denom = (1.0 / eps_core) + (A_1 / A_2) * (1.0 / eps_shroud - 1.0)
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

    T_gi, T_go = fsolve(resid, [0.5 * (T_core + T_amb), 0.3 * T_core + 0.7 * T_amb])
    Q_from_core = float((T_gi - T_go) / R_wall - 0.5 * Q_opt_wall_W)
    return Q_from_core, float(T_gi), float(T_go)


def solve_system(
    cad: dict,
    Q_uv_elec_heat: float,
    Q_vis_elec_heat: float,
    Q_opt_reabs_tot: float,
    Q_pcb: float,
    p_u1: float,
    T_amb: float,
    cfg: ChimneyConfig,
    f_rad_amb: float,
    r_sub_led: float = 0.50,
    r_tim_led: float = 0.30,
    orientation: str = "vertical",
    rth_penalty_factor: float = 1.0,
) -> dict[str, float]:
    """Solve coupled 8-node steady-state thermal network with explicit baffle, bell wall, and open-chimney physics."""
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

    # Top-head exterior & interior bay areas (including realistic 25%-infill wall conduction)
    D_bell = cad["cap_top_bell_od"] * 1e-3
    D_eaves = cad["cap_top_eaves_od"] * 1e-3
    D_port = cad["top_base_port_od"] * 1e-3
    A_ring = math.pi * D_port * (cad["top_base_port_h"] * 1e-3)
    A_eaves = math.pi * D_eaves * (cad["cap_top_eaves_h"] * 1e-3) + 0.5 * math.pi * (D_eaves ** 2 - D_bell ** 2)
    A_bell = math.pi * D_bell * ((cad["cap_top_roof_bot_z"] - der["z_cap_top_eaves_top"]) * 1e-3)
    roof_run = max(1e-4, 0.5 * (D_bell - cad["cap_top_collar_w"] * 1e-3))
    roof_slope_rad = math.atan2(cad["cap_top_roof_h"] * 1e-3, roof_run)
    A_roof = 0.25 * math.pi * (D_bell ** 2 - (cad["cap_top_collar_w"] * 1e-3) ** 2) / math.cos(roof_slope_rad)
    A_ext = A_ring + A_eaves + A_bell + A_roof
    A_int = 0.0255  # True interior Ø85/Ø78 bay wall + ceiling + floor surface area
    # Area-weighted wall conduction: 45% thin solid bell (3.1 mm, k=0.20) + 55% thicker 25%-infill port/eaves/roof (8.5 mm, k_eff=0.11)
    R_wall = 1.0 / (0.45 * A_int * (0.20 / 0.0031) + 0.55 * A_int * (0.11 / 0.0085))

    A_core_3 = 3.0 * W * L_bay
    A_core_1 = 1.0 * W * L_bay
    A_pcb_1 = (cad["pcb_w"] * cad["pcb_l"]) * 1e-6  # 0.001656 m^2 per face
    eps_pcb = 0.85
    eps_baffle = 0.90
    G_pcb_wires = 0.008  # Conservative conduction through USB-C copper/shield + M3 stanchions
    G_pcb_bridge = (1.0 / cfg.pcb_bridge_rth_KW) if cfg.pcb_bridge_rth_KW else 0.0

    Q_uv_tot = Q_uv_elec_heat + 0.25 * Q_opt_reabs_tot
    Q_vis_tot = Q_vis_elec_heat + 0.25 * Q_opt_reabs_tot
    Q_opt_wall = 0.50 * Q_opt_reabs_tot
    d_core_eq = 4.0 * cad["core_w_nom"] / math.pi

    def resid(x: list[float]) -> list[float]:
        T_c_uv, T_c_vis, T_c_bay, T_hs_t, T_baf, T_bay_air, T_bell_in, T_pcb = x
        T_c_avg = 0.5 * (T_c_uv + T_c_vis)
        Q_shroud, _, _ = shroud_annular_path_Q(
            T_c_avg, T_amb,
            D_in_mm=cad["glass_id_nom"], D_out_mm=cad["glass_od_nom"],
            L_shroud_mm=der["exposed_glass_window_mm"], D_core_eq_mm=d_core_eq,
            eps_core=cfg.core_inner_eps, eps_shroud=0.93, k_wall=0.19,
            Q_opt_wall_W=Q_opt_wall, orientation=orientation,
        )
        if cfg.open_chimney:
            T_bore_avg = 0.35 * T_c_vis + 0.35 * T_c_uv + 0.30 * T_c_bay
            Q_bore, _ = open_chimney_bore_Q(
                T_bore_avg, T_amb, b_mm, cad["cap_bot_inlet_w"], cad["core_length"] - 15.0,
                k_minor_mesh=cfg.k_minor_mesh, orientation=orientation, rth_penalty_factor=rth_penalty_factor,
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
        Q_c3_rad = cfg.core_inner_eps * SIGMA * A_core_3 * ((T_c_bay + 273.15) ** 4 - (T_bell_in + 273.15) ** 4)
        Q_sock = 0.025 * (T_c_bay - T_bell_in)

        # Core -> 2.0 mm baffle (0.55 mm air + 2.0 mm PETG/ASA)
        R_core_baf = (0.00055 / 0.028 + (cad["core_sleeve_wall"] * 1e-3) / 0.21) / A_core_1
        Q_core_baf = (T_c_bay - T_baf) / R_core_baf

        # Baffle <-> B.Cu of PCB (air gap conduction + radiation) & optional captive 15x15 mm silicone-pad/brass-shim bridge to Al core
        gap_bp = (cad["pcb_x_bcu"] - (0.5 * cad["core_pocket_w"] + cad["core_sleeve_wall"])) * 1e-3
        A_bridge = (0.015 * 0.015) if G_pcb_bridge > 0.0 else 0.0
        A_pcb_air = max(1e-6, A_pcb_1 - A_bridge)
        A_baf_rest = max(0.0, A_core_1 - A_pcb_1)
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

        # Bay air -> bell inner wall -> outer bell wall -> ambient
        h_bay_wall = max(2.5, churchill_chu_vertical_plate_h(T_bay_air, T_bell_in, 0.085) * 0.70)
        Q_air_wall = h_bay_wall * A_int * (T_bay_air - T_bell_in)

        T_out_est = 0.5 * (T_bell_in + T_amb)
        h_ext_c = churchill_chu_vertical_plate_h(T_out_est, T_amb, 0.095)
        h_ext_r = 0.90 * 4.0 * SIGMA * ((0.5 * (T_out_est + T_amb) + 273.15) ** 3)
        R_bell_tot = (R_wall + 1.0 / ((h_ext_c + h_ext_r) * A_ext)) * rth_penalty_factor
        Q_bell_amb = (T_bell_in - T_amb) / R_bell_tot

        return [
            Q_uv_tot - 0.5 * Q_shroud - Q_uv_vis - Q_uv_bay - 0.35 * Q_bore,
            Q_vis_tot + Q_uv_vis - 0.5 * Q_shroud - 0.35 * Q_bore,
            Q_uv_bay - Q_bay_top - Q_c3_conv - Q_c3_rad - Q_sock - Q_core_baf - Q_pad_core - 0.30 * Q_bore,
            Q_bay_top - Q_top,
            Q_core_baf - Q_baf_pcb - Q_baf_rest_conv - Q_baf_rest_rad,
            Q_c3_conv + Q_baf_rest_conv + Q_pcb_conv - Q_air_wall,
            Q_air_wall + Q_c3_rad + Q_sock + Q_baf_rest_rad + Q_pcb_rad + Q_pcb_wire - Q_bell_amb,
            Q_pcb + Q_baf_pcb + Q_pad_core - Q_pcb_conv - Q_pcb_rad - Q_pcb_wire,
        ]

    x0 = [T_amb + 25.0, T_amb + 25.0, T_amb + 20.0, T_amb + 18.0, T_amb + 19.0, T_amb + 14.0, T_amb + 10.0, T_amb + 24.0]
    T_c_uv, T_c_vis, T_c_bay, T_hs_t, T_baf, T_bay_air, T_bell_in, T_pcb_avg = [float(v) for v in fsolve(resid, x0)]
    T_c_avg = 0.5 * (T_c_uv + T_c_vis)
    Q_shroud_core, T_gi, T_go = shroud_annular_path_Q(
        T_c_avg, T_amb,
        D_in_mm=cad["glass_id_nom"], D_out_mm=cad["glass_od_nom"],
        L_shroud_mm=der["exposed_glass_window_mm"], D_core_eq_mm=d_core_eq,
        eps_core=cfg.core_inner_eps, eps_shroud=0.93, k_wall=0.19,
        Q_opt_wall_W=Q_opt_wall, orientation=orientation,
    )
    if cfg.open_chimney:
        Q_bore_val, V_chim = open_chimney_bore_Q(
            0.35 * T_c_vis + 0.35 * T_c_uv + 0.30 * T_c_bay, T_amb, b_mm, cad["cap_bot_inlet_w"],
            cad["core_length"] - 15.0, k_minor_mesh=cfg.k_minor_mesh, orientation=orientation,
            rth_penalty_factor=rth_penalty_factor,
        )
    else:
        Q_bore_val, V_chim = 0.0, 0.0

    q_uv_single = Q_uv_elec_heat / 4.0
    T_j_uv = T_c_uv + q_uv_single * (1.4 + r_sub_led + 0.10 + r_tim_led)
    if Q_vis_elec_heat <= 0.0:
        T_j_vis = T_c_vis
    else:
        q_green_single = 0.270 * Q_vis_elec_heat
        T_j_vis = T_c_vis + q_green_single * (4.9 + r_sub_led + 0.10 + r_tim_led)

    T_pcb_hotspot = T_pcb_avg + 3.5 * Q_pcb
    T_j_u1_jedec = T_pcb_avg + p_u1 * 147.0
    # Worst-case temperature of ANY polymer surface contacting the Al core (cap_bot, top_base, cap_top) or PCB stanchions
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
        T_pcb_hotspot=T_pcb_hotspot,
        T_plastic_max=T_plastic_max,
        T_j_uv=T_j_uv,
        T_j_vis=T_j_vis,
        T_j_u1_jedec=T_j_u1_jedec,
        T_shroud_in=T_gi,
        T_shroud_out=T_go,
        Q_shroud_total=Q_shroud_core + Q_opt_wall,
        Q_bore=Q_bore_val,
        V_chimney_ms=V_chim,
        Q_top=protruding_core_Q(T_hs_t, T_amb, cad["core_w_nom"], l_chim_mm, cfg.chimney_eps, orientation, f_rad_amb, rth_penalty_factor),
        margin_uv_100C=100.0 - T_j_uv,
        margin_vis_150C=150.0 - T_j_vis,
        margin_pmma_75C=75.0 - T_gi,
        margin_petg_70C=70.0 - T_plastic_max,
        margin_asa_95C=95.0 - T_plastic_max,
        margin_u1_125C=125.0 - T_j_u1_jedec,
        margin_ic_comm_70C=70.0 - T_pcb_avg,
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
    p_pcb_4uv_nom = round(ch1["p_ic"] + ch1["p_diode"] + ch1["p_ind"] + ch1["p_rs"] + an["p_overhead_W"], 3)
    p_u1_nom = round(max(an["ch1_uv"]["p_ic"], an["ch2_vis"]["p_ic"]), 4)
    p_u1_wc = round(max(cs["uv_pic_max"], cs["vis_pic_max"]), 4)
    p_led_uv_nom = float(te["p_led_uv_nom_W"])
    p_led_vis_nom = float(te["p_led_vis_nom_W"])

    modes = [
        ("4-UV Nom (40%WPE)",     round(0.60 * p_led_uv_nom, 3), 0.000, round(0.14 * 0.40 * p_led_uv_nom, 3), p_pcb_4uv_nom, round(an["ch1_uv"]["p_ic"], 4)),
        ("8-ALL Nom (49%UV WPE)", round(0.51 * p_led_uv_nom, 3), round(0.60 * p_led_vis_nom, 3), round(0.14 * (0.49 * p_led_uv_nom + 0.40 * p_led_vis_nom), 3), p_pcb_8all_nom, p_u1_nom),
        ("8-ALL Nom (40%UV WPE)", round(0.60 * p_led_uv_nom, 3), round(0.60 * p_led_vis_nom, 3), round(0.14 * (0.40 * p_led_uv_nom + 0.40 * p_led_vis_nom), 3), p_pcb_8all_nom, p_u1_nom),
        ("8-ALL DS-RealWPE",      3.650, 2.950, 0.450, p_pcb_wc, p_u1_wc),
        ("8-ALL DS-100% (NoOpt)", 5.620, 4.750, 0.000, p_pcb_wc, p_u1_wc),
    ]

    l_chim = float(cad["derived"]["core_protrusion_mm"])
    f_rad_amb = compute_chimney_ambient_view_factor(
        l_chim, cad["core_w_nom"], cad["cap_top_bell_od"], cad["cap_top_collar_h"],
    )

    configs = [
        ChimneyConfig("Config 0: Open Chimney + Bare Mill Al (eps=0.10) + PCB Thermal Bridge", True, 0.10, 0.10, k_minor_mesh=3.0, pcb_bridge_rth_KW=8.5),
        ChimneyConfig("Config 1: Open Chimney + Anodized/Painted Al (eps=0.82) + PCB Thermal Bridge", True, 0.82, 0.82, k_minor_mesh=3.0, pcb_bridge_rth_KW=8.5),
        ChimneyConfig("Config 2: Open Chimney + Bare Mill Al (eps=0.10), No PCB Bridge", True, 0.10, 0.10, k_minor_mesh=3.0, pcb_bridge_rth_KW=None),
        ChimneyConfig("Config 3: Closed Bore + Bare Mill Al (eps=0.10), No PCB Bridge", False, 0.10, 0.10, pcb_bridge_rth_KW=None),
    ]

    rows = []
    for cfg in configs:
        t_list = [15.0, 22.0, 30.0, 35.0] if cfg.name.startswith("Config 0:") else [22.0, 30.0]
        for T_amb in t_list:
            for orient in ("vertical", "horizontal"):
                for m_name, q_uv, q_vis, q_opt, q_pcb, p_u1 in modes:
                    r = solve_system(
                        cad, q_uv, q_vis, q_opt, q_pcb, p_u1, T_amb,
                        cfg=cfg, f_rad_amb=f_rad_amb, orientation=orient,
                    )
                    passed_petg = (
                        r["margin_uv_100C"] > 0.0
                        and r["margin_vis_150C"] > 0.0
                        and r["margin_pmma_75C"] > 0.0
                        and r["margin_petg_70C"] >= 0.0
                        and r["margin_u1_125C"] >= 0.0
                        and r["margin_ic_comm_70C"] >= 0.0
                    )
                    passed_asa = (
                        r["margin_uv_100C"] > 0.0
                        and r["margin_vis_150C"] > 0.0
                        and r["margin_pmma_75C"] > 0.0
                        and r["margin_asa_95C"] >= 0.0
                        and r["margin_u1_125C"] >= 0.0
                        and r["margin_ic_comm_70C"] >= 0.0
                    )
                    rows.append({
                        "config": cfg.name,
                        "T_amb_C": T_amb,
                        "orientation": orient,
                        "mode": m_name,
                        "Q_uv_W": q_uv,
                        "Q_vis_W": q_vis,
                        "Q_opt_reabs_W": q_opt,
                        "Q_pcb_W": q_pcb,
                        "P_u1_W": p_u1,
                        **{k: round(v, 3) for k, v in r.items()},
                        "pass_all_limits_petg": passed_petg,
                        "pass_all_limits_asa": passed_asa,
                    })

    csv_path = out_dir / "thermal_results.csv"
    with csv_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    t_ambs = np.linspace(10.0, 40.0, 31)
    sweep_modes = ["4-UV Nom (40%WPE)", "8-ALL Nom (40%UV WPE)", "8-ALL DS-RealWPE", "8-ALL DS-100% (NoOpt)"]
    sweep_data: dict[str, list[dict[str, float]]] = {m: [] for m in sweep_modes}
    for m_name, q_uv, q_vis, q_opt, q_pcb, p_u1 in modes:
        if m_name not in sweep_modes:
            continue
        for Ta in t_ambs:
            r = solve_system(cad, q_uv, q_vis, q_opt, q_pcb, p_u1, float(Ta), configs[0], f_rad_amb, orientation="vertical")
            sweep_data[m_name].append({"T_amb": float(Ta), **{k: round(v, 3) for k, v in r.items()}})

    cfg0_rows = [r for r in rows if r["config"].startswith("Config 0:")]
    cfg0_vert_22_real = [r for r in cfg0_rows if r["orientation"] == "vertical" and r["T_amb_C"] <= 22.0 and "DS-100%" not in r["mode"]]
    cfg0_vert_30_nom = [r for r in cfg0_rows if r["orientation"] == "vertical" and r["T_amb_C"] <= 30.0 and "Nom" in r["mode"]]
    cfg0_vert_30_real_petg = [r for r in cfg0_rows if r["orientation"] == "vertical" and r["T_amb_C"] <= 30.0 and "DS-100%" not in r["mode"]]

    cfg0_vert_35_real = [r for r in cfg0_rows if r["orientation"] == "vertical" and r["T_amb_C"] <= 35.0 and "DS-100%" not in r["mode"]]

    # Plot 1: thermal_margins.png
    fig, axes = plt.subplots(1, 3, figsize=(14.5, 4.8), dpi=150)
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
    ax.bar(x + w, get_vals("T_j_uv", 22.0, "horizontal"), w, label="22°C Horiz", color="#c44e52")
    ax.axhline(100.0, color="red", ls="--", lw=1.5, label="Limit 100°C")
    ax.axhline(80.0, color="gray", ls=":", lw=1.2, label="Nom Target 80°C")
    ax.set_title("UV LED Junction $T_{j,\\mathrm{UV}}$ (Cu DTP Star)")
    ax.set_ylabel("Temperature (°C)")
    ax.set_xticks(x, ["4-UV\nNom", "8-ALL\nNom", "8-ALL\nDS-Real", "8-ALL\nDS-100%"], fontsize=8.5)
    ax.set_ylim(0, 118)
    ax.grid(axis="y", alpha=0.3)
    ax.legend(fontsize=7.2, loc="upper left")

    ax = axes[1]
    ax.bar(x - w, get_vals("T_c_vis", 22.0, "vertical"), w, label="22°C Vert Core", color="#4c72b0")
    ax.bar(x, get_vals("T_c_vis", 30.0, "vertical"), w, label="30°C Vert Core", color="#dd8452")
    ax.bar(x + w, get_vals("T_shroud_in", 30.0, "vertical"), w, label="30°C XT PMMA Wall", color="#55a868")
    ax.axhline(70.0, color="red", ls="--", lw=1.5, label="PETG HDT 70°C")
    ax.axhline(95.0, color="purple", ls=":", lw=1.2, label="ASA HDT 95°C")
    ax.set_title("Core Contact & XT PMMA Shroud")
    ax.set_xticks(x, ["4-UV\nNom", "8-ALL\nNom", "8-ALL\nDS-Real", "8-ALL\nDS-100%"], fontsize=8.5)
    ax.set_ylim(0, 105)
    ax.grid(axis="y", alpha=0.3)
    ax.legend(fontsize=7.2, loc="upper left")

    ax = axes[2]
    ax.bar(x - w, get_vals("T_pcb_avg", 22.0, "vertical"), w, label="22°C Vert PCB", color="#4c72b0")
    ax.bar(x, get_vals("T_pcb_avg", 30.0, "vertical"), w, label="30°C Vert PCB", color="#dd8452")
    ax.bar(x + w, get_vals("T_bay_air", 30.0, "vertical"), w, label="30°C Bay Air", color="#55a868")
    ax.axhline(70.0, color="orange", ls="--", lw=1.5, label="U4 LM393 / PETG 70°C")
    ax.set_title("Vertical Driver PCB & Top Bay Air")
    ax.set_xticks(x, ["4-UV\nNom", "8-ALL\nNom", "8-ALL\nDS-Real", "8-ALL\nDS-100%"], fontsize=8.5)
    ax.set_ylim(0, 95)
    ax.grid(axis="y", alpha=0.3)
    ax.legend(fontsize=7.2, loc="upper left")

    fig.suptitle("LepiLED Steady-State Thermal Margins (Open 26 mm Chimney, Bare Mill Al + 15 × 15 mm PCB Bridge)", fontweight="bold")
    fig.tight_layout()
    fig.savefig(out_dir / "thermal_margins.png")
    plt.close(fig)

    # Plot 2: thermal_ambient_sweep.png
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.2, 4.8), dpi=150)
    colors = {
        "4-UV Nom (40%WPE)": "#2ca02c",
        "8-ALL Nom (40%UV WPE)": "#1f77b4",
        "8-ALL DS-RealWPE": "#ff7f0e",
        "8-ALL DS-100% (NoOpt)": "#d62728",
    }
    for m in sweep_modes:
        pts = sweep_data[m]
        ta = [pt["T_amb"] for pt in pts]
        ax1.plot(ta, [pt["T_j_uv"] for pt in pts], lw=2.0, color=colors[m], label=m)
        ax2.plot(ta, [pt["T_c_vis"] for pt in pts], lw=1.8, color=colors[m], label=f"{m} (Core)")
        ax2.plot(ta, [pt["T_pcb_avg"] for pt in pts], lw=1.4, ls="--", color=colors[m], label=f"{m} (PCB)")
    ax1.axhline(100.0, color="red", ls="--", lw=1.4, label="UV Limit 100°C")
    ax1.axvline(22.0, color="green", ls=":", lw=1.2, label="UK Night 22°C")
    ax1.axvline(30.0, color="gray", ls=":", lw=1.2, label="Warm Night 30°C")
    ax1.axvline(35.0, color="darkorange", ls=":", lw=1.2, label="Heatwave 35°C")
    ax1.set_title("UV LED $T_{j,\\mathrm{UV}}$ vs Ambient (Vertical Hanging)")
    ax1.set_xlabel("Ambient Temperature $T_{\\mathrm{amb}}$ (°C)")
    ax1.set_ylabel("Temperature (°C)")
    ax1.grid(alpha=0.3)
    ax1.legend(fontsize=7.2)

    ax2.axhline(70.0, color="red", ls="--", lw=1.4, label="PETG HDT / LM393 70°C")
    ax2.axhline(95.0, color="purple", ls=":", lw=1.2, label="ASA HDT 95°C")
    ax2.axvline(22.0, color="green", ls=":", lw=1.2)
    ax2.axvline(30.0, color="gray", ls=":", lw=1.2)
    ax2.axvline(35.0, color="darkorange", ls=":", lw=1.2)
    ax2.set_title("Core Contact & Vertical PCB Temperature vs Ambient")
    ax2.set_xlabel("Ambient Temperature $T_{\\mathrm{amb}}$ (°C)")
    ax2.set_ylabel("Temperature (°C)")
    ax2.grid(alpha=0.3)
    ax2.legend(fontsize=6.5, ncol=2)

    fig.suptitle("Ambient Temperature Sweep (10–40 °C, Open 26 mm Chimney, Bare Mill Al + PCB Bridge)", fontweight="bold")
    fig.tight_layout()
    fig.savefig(out_dir / "thermal_ambient_sweep.png")
    plt.close(fig)

    # Plot 3: thermal_network_comparison.png (side-by-side UV junction + Driver PCB at 30 C)
    fig, (ax_uv, ax_pcb) = plt.subplots(1, 2, figsize=(13.2, 4.9), dpi=150)
    cfg_labels = [
        "Open Chimney\nBare Mill Al\n+ PCB Bridge\n(Baseline)",
        "Open Chimney\nAnod./Painted\n+ PCB Bridge\n(Optional)",
        "Open Chimney\nBare Mill Al\n(No Bridge)",
        "Closed Bore\nBare Mill Al\n(No Bridge)",
    ]
    cfg_prefixes = ["Config 0:", "Config 1:", "Config 2:", "Config 3:"]
    x_c = np.arange(len(cfg_labels))
    for ax_p, metric, ylabel, ylim, lim_val, lim_lbl, title_p in [
        (ax_uv, "T_j_uv", "UV LED Junction $T_{j,\\mathrm{UV}}$ (°C)", 110, 100.0, "SST-10-UV Limit 100°C", "UV LED Junction ($T_{\\mathrm{amb}}=30^\\circ\\mathrm{C}$)"),
        (ax_pcb, "T_pcb_avg", "Driver PCB Average $T_{\\mathrm{pcb}}$ (°C)", 92, 70.0, "LM393 / PETG Limit 70°C", "Driver PCB Temperature ($T_{\\mathrm{amb}}=30^\\circ\\mathrm{C}$)"),
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
            ax_p.text(i - 0.18, vn + 1.5, f"{vn:.1f}°C", ha="center", fontsize=8.2, fontweight="bold")
            ax_p.text(i + 0.18, vd + 1.5, f"{vd:.1f}°C", ha="center", fontsize=8.2, fontweight="bold")
        ax_p.set_xticks(x_c, cfg_labels, fontsize=8.5)
        ax_p.set_ylabel(ylabel)
        ax_p.set_ylim(0, ylim)
        ax_p.set_title(title_p)
        ax_p.grid(axis="y", alpha=0.3)
        ax_p.legend(fontsize=8.0, loc="upper left")
    fig.suptitle("Thermal Configuration Comparison ($T_{\\mathrm{amb}}=30^\\circ\\mathrm{C}$, Vertical Still Air)", fontweight="bold")
    fig.tight_layout()
    fig.savefig(out_dir / "thermal_network_comparison.png")
    plt.close(fig)

    summary = {
        "revision": "6.0",
        "architecture": "Open-Chimney Funnel Lantern (30x30x2.0x300 mm Bare Mill-Finish Al Core eps=0.10, Open 26 mm Chimney, Epoxy Cu DTP Stars, +X Vertical PCB w/ 15x15 mm Silicone-Pad/Brass-Shim Bridge)",
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
        "ssot_inputs": {
            "core_section_mm": f"{cad['core_w_nom']:.0f}x{cad['core_w_nom']:.0f}x{cad['core_wall']:.1f}",
            "core_bore_mm": cad["core_bore_nom"],
            "core_length_mm": cad["core_length"],
            "core_protrusion_mm": l_chim,
            "chimney_rad_view_factor_F_amb": f_rad_amb,
            "exposed_shroud_window_mm": cad["derived"]["exposed_glass_window_mm"],
            "core_finish": "mill",
            "core_emissivity": configs[0].chimney_eps,
            "pcb_thermal_bridge_rth_KW": configs[0].pcb_bridge_rth_KW,
            "chimney_minor_loss_K": configs[0].k_minor_mesh,
            "p_pcb_4uv_nom_W": p_pcb_4uv_nom,
            "p_pcb_8all_nom_W": p_pcb_8all_nom,
            "p_pcb_wc_W": p_pcb_wc,
        },
        "vert_uk_night_22C_real_petg_all_pass": all(r["pass_all_limits_petg"] for r in cfg0_vert_22_real),
        "vert_15_30C_nom_petg_all_pass": all(r["pass_all_limits_petg"] for r in cfg0_vert_30_nom),
        "vert_15_30C_real_petg_all_pass": all(r["pass_all_limits_petg"] for r in cfg0_vert_30_real_petg),
        "vert_15_35C_real_petg_all_pass": all(r["pass_all_limits_petg"] for r in cfg0_vert_35_real),
        "vert_15_30C_real_asa_all_pass": all(r["pass_all_limits_asa"] for r in cfg0_vert_30_real_petg),
        "vert_15_35C_real_asa_all_pass": all(r["pass_all_limits_asa"] for r in cfg0_vert_35_real),
        "baseline_results": cfg0_rows,
        "config_comparison_30C_vert": [
            r for r in rows if r["T_amb_C"] == 30.0 and r["orientation"] == "vertical" and r["mode"] in ("8-ALL Nom (40%UV WPE)", "8-ALL DS-RealWPE")
        ],
        "ambient_sweep_vert": sweep_data,
    }
    json_path = out_dir / "thermal_summary.json"
    json_path.write_text(json.dumps(summary, indent=2) + "\n")

    print("=== Coupled 8-Node Thermal Analysis (Open 26 mm Chimney, Bare Mill 30x30x2 Al eps=0.10, 15x15 mm PCB Bridge R=8.5 K/W) ===")
    for r in cfg0_rows:
        if r["T_amb_C"] in (22.0, 30.0, 35.0) and r["orientation"] == "vertical" and r["mode"] in ("4-UV Nom (40%WPE)", "8-ALL Nom (40%UV WPE)", "8-ALL DS-RealWPE"):
            print(
                f"  Tamb={r['T_amb_C']:2.0f}C vert | {r['mode']:21s} | "
                f"TjUV={r['T_j_uv']:5.1f}C TcVis={r['T_c_vis']:4.1f}C Tbay={r['T_bay_air']:4.1f}C "
                f"Tpcb={r['T_pcb_avg']:4.1f}C Qbore={r['Q_bore']:.2f}W | PETG={r['pass_all_limits_petg']} ASA={r['pass_all_limits_asa']}"
            )
    print(f"Vertical <=22 C Real-WPE (PETG + LM393) PASS: {sum(r['pass_all_limits_petg'] for r in cfg0_vert_22_real)}/{len(cfg0_vert_22_real)}")
    print(f"Vertical 15-30 C Real-WPE (PETG + LM393) PASS: {sum(r['pass_all_limits_petg'] for r in cfg0_vert_30_real_petg)}/{len(cfg0_vert_30_real_petg)}")
    print(f"Vertical 15-35 C Real-WPE (ASA + LM393) PASS: {sum(r['pass_all_limits_asa'] for r in cfg0_vert_35_real)}/{len(cfg0_vert_35_real)}")

    print(f"Saved: {csv_path}, {json_path}, and 3 PNG plots in {out_dir}")


if __name__ == "__main__":
    main()
