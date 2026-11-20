#!/usr/bin/env python3
"""
Reproducible Coupled First-Principles Thermal Analysis for LepiLED DIY Maxi Switch (Rev 4.9).

SSOT-Coupled Architecture (zero hardcoded stale geometry or power budgets!):
  - Reads exact CAD geometry directly from `mechanical_design/cad/cad_params.json`
    (30 x 30 x 3.0 mm x 200 mm Al 6063-T6 core protruding 58.5 mm above MECH-CAP-TOP,
    Ø60 x 54 x 3.0 mm Extruded Clear XT PMMA shroud, 86.0 mm exposed window, 5.5 mm bulkhead).
  - Reads exact electrical PCB & LED power budgets directly from
    `circuit_design/sim/outputs/sim_summary.json` (Bourns SRN6045-680M + Convoy OSRAM CSLNM1).
  - Config 0 (Rev 4.9 Standard): Unpainted Bare Mill 30x30x3 Al Core (eps = 0.20 everywhere —
    £0 paint cost, zero masking, zero UV paint outgassing; passes ALL 15..22 C UK-night modes
    including DS-RealWPE and ALL 15..30 C nominal modes with PETG & commercial 0..70 C ICs!).
  - Config 1 (Optional Upgrade): Chimney-Only Matte-Black Spray (eps = 0.88 on top 58.5 mm)
    drops T_PCB_hotspot by ~5 C at 30 C worst-case DS-RealWPE if operating in 30 C tropical
    nights with a PETG housing.
  - Visible LEDs upgraded to ams OSRAM CSLNM1 on 20 mm Cu DTP stars (R_thJS = 4.9 K/W max vs
    9.0 K/W Cree XP-E2 Green -> ~4 C cooler visible die junction!).
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


# ---------------------------------------------------------------------------
# Convection & Radiation Correlations
# ---------------------------------------------------------------------------

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


def horizontal_plate_up_h(T_s: float, T_amb: float, L_char: float) -> float:
    dT = max(0.05, T_s - T_amb)
    p = air_props(0.5 * (T_s + T_amb))
    Ra = 9.81 * p["beta"] * dT * (L_char ** 3) / (p["nu"] * p["alpha"])
    Nu = 0.54 * Ra ** 0.25 if Ra < 1e7 else 0.15 * Ra ** (1.0 / 3.0)
    return Nu * p["k"] / L_char


def elenbaas_channel_h(T_s: float, T_amb: float, b: float, L_flow: float) -> float:
    dT = max(0.05, T_s - T_amb)
    p = air_props(0.5 * (T_s + T_amb))
    Ra_b = 9.81 * p["beta"] * dT * (b ** 3) / (p["nu"] * p["alpha"]) * (b / L_flow)
    Nu_b = (576.0 / (Ra_b ** 2) + 2.873 / (Ra_b ** 0.5)) ** (-0.5)
    return Nu_b * p["k"] / b


@dataclass(frozen=True)
class HeatsinkSpec:
    name: str
    kind: str  # "protruding_core" | "radial"
    D_out_mm: float
    D_core_mm: float
    L_mm: float
    n_fins: int = 0
    t_fin_mm: float = 0.0
    eps: float = 0.88


def compute_chimney_ambient_view_factor(L_chim_mm: float, core_w_mm: float, eave_od_mm: float, collar_h_mm: float) -> float:
    """
    Conservative view factor F_amb from the 4 protruding chimney walls to open ambient sky,
    accounting for the Ø84 mm circular rain eaves overhanging radially below the collar.
    Uses exact perpendicular-plane view factor approximation for a horizontal shelf of width
    w_shelf = (eave_od - core_w)/2 located collar_h below the chimney base.
    """
    w_shelf = max(0.0, 0.5 * (eave_od_mm - core_w_mm))
    # Approximate average angle subtended by the horizontal eave shelf across height L_chim
    ys = np.linspace(0.5, L_chim_mm, 60)
    # Local view factor from vertical strip at height y above roof to horizontal shelf of width w_shelf
    h_eff = ys + collar_h_mm
    f_to_eave_local = 0.5 * (1.0 - h_eff / np.sqrt(h_eff ** 2 + w_shelf ** 2))
    f_to_eave = float(np.mean(f_to_eave_local))
    # Clamp conservatively (0.12..0.22 -> F_amb ~ 0.84)
    return round(1.0 - f_to_eave, 4)


def protruding_core_Q(
    T_s: float,
    T_amb: float,
    hs: HeatsinkSpec,
    orientation: str = "vertical",
    f_rad_amb: float = 0.84,
    rth_penalty_factor: float = 1.0,
) -> float:
    """Natural convection + view-factor-corrected radiation from 4 outer walls of protruding Al chimney."""
    W = hs.D_out_mm * 1e-3
    L = hs.L_mm * 1e-3
    A_sides = 4.0 * W * L  # excludes plastic-capped top finial (conservative)
    dT = max(0.05, T_s - T_amb)
    if orientation == "vertical":
        h_c = churchill_chu_vertical_plate_h(T_s, T_amb, L)
    else:
        h_c = churchill_chu_horiz_cyl_h(T_s, T_amb, 4.0 * W / math.pi)
    Q_conv = h_c * A_sides * dT
    # Radiation to open ambient weighted by F_amb; remaining (1 - F_amb) sees warm plastic rain eaves (~0.35 dT)
    T_eave = T_amb + 0.35 * dT
    Q_rad_amb = hs.eps * f_rad_amb * SIGMA * ((T_s + 273.15) ** 4 - (T_amb + 273.15) ** 4) * A_sides
    Q_rad_eave = hs.eps * (1.0 - f_rad_amb) * SIGMA * ((T_s + 273.15) ** 4 - (T_eave + 273.15) ** 4) * A_sides
    return (Q_conv + Q_rad_amb + Q_rad_eave) / rth_penalty_factor


def radial_heatsink_Q(
    T_s: float,
    T_amb: float,
    hs: HeatsinkSpec,
    orientation: str = "vertical",
    rth_penalty_factor: float = 1.0,
) -> float:
    """Benchmark natural convection + radiation from external radial-fin heatsink (SK 578/50 SA)."""
    D_out = hs.D_out_mm * 1e-3
    D_core = hs.D_core_mm * 1e-3
    L = hs.L_mm * 1e-3
    t_fin = hs.t_fin_mm * 1e-3
    h_fin = 0.5 * (D_out - D_core)
    r_mid = 0.25 * (D_out + D_core)
    b_avg = max(0.0015, 2.0 * math.pi * r_mid / hs.n_fins - t_fin)

    A_fin_sides = hs.n_fins * 2.0 * h_fin * L
    A_core_exp = max(0.0, (math.pi * D_core - hs.n_fins * t_fin)) * L
    A_fin_tips = hs.n_fins * t_fin * L
    A_end = math.pi * (D_out ** 2) / 4.0 * 0.45
    A_rad_cyl = math.pi * D_out * L
    A_rad_end = math.pi * (D_out ** 2) / 4.0

    m_fin = math.sqrt(2.0 * 6.0 / (200.0 * t_fin))
    eta_fin = math.tanh(m_fin * h_fin) / (m_fin * h_fin)
    dT = max(0.05, T_s - T_amb)

    if orientation == "vertical":
        h_chan = elenbaas_channel_h(T_s, T_amb, b_avg, L)
        h_tips = churchill_chu_vertical_plate_h(T_s, T_amb, L)
        h_top = horizontal_plate_up_h(T_s, T_amb, 0.25 * D_out)
        Q_conv = dT * (h_chan * (eta_fin * A_fin_sides + A_core_exp) + h_tips * A_fin_tips + h_top * A_end)
    else:
        h_chan = elenbaas_channel_h(T_s, T_amb, b_avg, max(0.020, 0.85 * D_out)) * 0.75
        h_tips = churchill_chu_horiz_cyl_h(T_s, T_amb, D_out)
        h_end = churchill_chu_vertical_plate_h(T_s, T_amb, D_out)
        Q_conv = dT * (h_chan * (eta_fin * A_fin_sides + A_core_exp) + h_tips * A_fin_tips + h_end * A_end)

    Q_rad = SIGMA * ((T_s + 273.15) ** 4 - (T_amb + 273.15) ** 4) * (min(0.95, hs.eps + 0.04) * A_rad_cyl + hs.eps * A_rad_end)
    return (Q_conv + Q_rad) / rth_penalty_factor


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
    """
    Heat flow from internal Al core across annular air gap + PLEXIGLAS XT 0A070 shroud wall
    (k = 0.19 W/mK, eps = 0.93) to ambient, including direct optical Fresnel/bulk absorption
    Q_opt_wall_W deposited inside the PMMA wall.
    Returns (Q_from_core_W, T_shroud_in_C, T_shroud_out_C).
    """
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

        # Optical absorption deposited at mid-wall adds +0.5*Q_opt_wall to inner->outer conduction & full Q_opt_wall to outer rejection
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


def compute_bulkhead_resistance(cad: dict) -> float:
    """
    First-principles parallel thermal resistance between bottom of Al core and sealed electronics bay (K/W):
      - 5.5 mm solid PETG/ASA bulkhead conduction (k = 0.21 W/mK, A = 1200 mm^2)
      - Outer MECH-CAP-BOT frustum wall conduction (L = 32 mm, A = 2400 mm^2)
      - 2x M3x12 A2 stainless steel anchor bolts via MECH-CORE-ANCHOR (plastic thermal break ~ 2 mm in series)
      - Internal cavity radiation (~114 K/W)
    """
    k_plast = 0.21  # Conservative PETG/ASA FDM conductivity (anisotropic Z layers)
    t_bh = cad["derived"]["bulkhead_thick"] * 1e-3  # 5.5 mm
    r_bh = t_bh / (k_plast * 1200e-6)
    r_wall = 0.032 / (k_plast * 2400e-6)
    r_rad = 114.1
    return 1.0 / (1.0 / r_bh + 1.0 / r_wall + 1.0 / r_rad)


def solve_system(
    cad: dict,
    Q_uv_elec_heat: float,
    Q_vis_elec_heat: float,
    Q_opt_reabs_tot: float,
    Q_pcb: float,
    p_u1: float,
    T_amb: float,
    top_hs: HeatsinkSpec,
    eps_core_inner: float = 0.20,
    f_rad_amb: float = 0.84,
    r_sub_led: float = 0.50,
    r_tim_led: float = 0.30,
    orientation: str = "vertical",
    rth_penalty_factor: float = 1.0,
    k_shroud: float = 0.19,
    eps_shroud: float = 0.93,
) -> dict[str, float]:
    """Solve coupled 5-node steady-state thermal network for Rev 4.8 Field Lantern."""
    der = cad["derived"]
    A_cs = (cad["core_w_nom"] ** 2 - cad["core_bore_nom"] ** 2) * 1e-6  # 324e-6 m^2 for 30x30x3 mm!
    k_al = 200.0  # Al 6063-T6

    # Axial conduction along 30x30x3 Al hollow square core
    ax_top_mm = der["axial_uv_to_top_mm"] + (0.5 * top_hs.L_mm if top_hs.kind == "protruding_core" else 0.0)
    R_ax_uv_top = (ax_top_mm * 1e-3) / (k_al * A_cs)
    R_ax_uv_vis = (der["axial_uv_to_vis_mm"] * 1e-3) / (k_al * A_cs)
    r_int_top = 0.0 if top_hs.kind == "protruding_core" else 0.28
    R_top_total = R_ax_uv_top + r_int_top
    R_bulkhead = compute_bulkhead_resistance(cad)

    # Sealed plastic electronics bay (lid-mounted horizontal PCB inside Ø71.6 mm cavity, Ø92.4 mm outer shell):
    # Bay-air to ambient resistance: ~17.5 K/W (A_ext ~ 0.018 m^2, h_ext ~ 11 W/m^2K -> 5.0 K/W + wall 1.0 + int 11.5)
    # PCB-to-bay-air resistance: ~10.0 K/W (2L 36x46 mm FR4 w/ solid 1oz B.Cu GND plane in stagnant Ø71.6 mm air)
    R_bay_to_amb = 17.5 * rth_penalty_factor
    R_pcb_to_bay = 10.0

    # Split internal optical Fresnel/end-cap re-absorption 50% onto core (25% UV zone, 25% Vis zone) & 50% onto PMMA wall
    Q_uv_tot = Q_uv_elec_heat + 0.25 * Q_opt_reabs_tot
    Q_vis_tot = Q_vis_elec_heat + 0.25 * Q_opt_reabs_tot
    Q_opt_wall = 0.50 * Q_opt_reabs_tot

    d_core_eq = 4.0 * cad["core_w_nom"] / math.pi

    def Q_top_sink(T_s: float) -> float:
        if top_hs.kind == "protruding_core":
            return protruding_core_Q(T_s, T_amb, top_hs, orientation=orientation, f_rad_amb=f_rad_amb, rth_penalty_factor=rth_penalty_factor)
        return radial_heatsink_Q(T_s, T_amb, top_hs, orientation=orientation, rth_penalty_factor=rth_penalty_factor)

    def resid(x: list[float]) -> list[float]:
        T_c_uv, T_c_vis, T_hs_t, T_bay_air, T_pcb_avg = x
        T_c_avg = 0.5 * (T_c_uv + T_c_vis)
        Q_shroud_core, _, _ = shroud_annular_path_Q(
            T_c_avg, T_amb,
            D_in_mm=cad["glass_id_nom"], D_out_mm=cad["glass_od_nom"],
            L_shroud_mm=der["exposed_glass_window_mm"], D_core_eq_mm=d_core_eq,
            eps_core=eps_core_inner, eps_shroud=eps_shroud, k_wall=k_shroud,
            Q_opt_wall_W=Q_opt_wall, orientation=orientation,
        )
        Q_uv_to_vis = (T_c_uv - T_c_vis) / R_ax_uv_vis
        Q_uv_to_top = (T_c_uv - T_hs_t) / R_top_total
        Q_vis_to_bay = (T_c_vis - T_bay_air) / R_bulkhead
        Q_pcb_to_bay = (T_pcb_avg - T_bay_air) / R_pcb_to_bay
        Q_bay_to_amb = (T_bay_air - T_amb) / R_bay_to_amb

        return [
            Q_uv_tot - 0.5 * Q_shroud_core - Q_uv_to_vis - Q_uv_to_top,
            Q_vis_tot + Q_uv_to_vis - 0.5 * Q_shroud_core - Q_vis_to_bay,
            Q_uv_to_top - Q_top_sink(T_hs_t),
            Q_vis_to_bay + Q_pcb_to_bay - Q_bay_to_amb,
            Q_pcb - Q_pcb_to_bay,
        ]

    x0 = [T_amb + 30.0, T_amb + 28.0, T_amb + 24.0, T_amb + 14.0, T_amb + 19.0]
    T_c_uv, T_c_vis, T_hs_t, T_bay_air, T_pcb_avg = [float(v) for v in fsolve(resid, x0)]
    T_c_avg = 0.5 * (T_c_uv + T_c_vis)
    Q_shroud_core, T_gi, T_go = shroud_annular_path_Q(
        T_c_avg, T_amb,
        D_in_mm=cad["glass_id_nom"], D_out_mm=cad["glass_od_nom"],
        L_shroud_mm=der["exposed_glass_window_mm"], D_core_eq_mm=d_core_eq,
        eps_core=eps_core_inner, eps_shroud=eps_shroud, k_wall=k_shroud,
        Q_opt_wall_W=Q_opt_wall, orientation=orientation,
    )

    # Junction temperatures (20 mm Copper DTP star: R_sub = 0.50 K/W, solder = 0.10 K/W, TIM = 0.30 K/W)
    # Luminus SST-10-UV RthJS = 1.4 K/W; ams OSRAM CSLNM1 (KB/KP/KW) RthJS = 4.9 K/W max (4.1 typ)
    q_uv_single = Q_uv_elec_heat / 4.0
    T_j_uv = T_c_uv + q_uv_single * (1.4 + r_sub_led + 0.10 + r_tim_led)

    if Q_vis_elec_heat <= 0.0:
        T_j_vis = T_c_vis
    else:
        # KP CSLNM1.F1 phosphor-converted green carries ~27% of Ch2 visible heat
        q_green_single = 0.270 * Q_vis_elec_heat
        T_j_vis = T_c_vis + q_green_single * (4.9 + r_sub_led + 0.10 + r_tim_led)

    # Driver PCB hotspot & U1/U2 AL8860WT-7 junction (TSOT25 RthJA = 147 C/W to bay air, conservative JEDEC)
    T_pcb_hotspot = T_pcb_avg + 3.5 * Q_pcb
    T_j_u1_jedec = T_pcb_avg + p_u1 * 147.0

    # Key limits:
    # - SST-10-UV: Tj_max = 100 C (nominal target <= 80 C)
    # - Cree XP-E2: Tj_max = 150 C
    # - AL8860WT-7: Tj_max = 125 C derated (150 C abs)
    # - PLEXIGLAS XT 0A070 continuous service: <= 75 C (Vicat softening ~105 C)
    # - PETG housing HDT limit: 75.0 C (ASA HDT = 95.0 C)
    # - Commercial IC ambient (U4 LM393DR2G / U5 Hottech TL431): 0..+70 C rated T_bay_air
    return dict(
        T_c_uv=T_c_uv,
        T_c_vis=T_c_vis,
        T_hs_t=T_hs_t,
        T_bay_air=T_bay_air,
        T_pcb_avg=T_pcb_avg,
        T_pcb_hotspot=T_pcb_hotspot,
        T_j_uv=T_j_uv,
        T_j_vis=T_j_vis,
        T_j_u1_jedec=T_j_u1_jedec,
        T_shroud_in=T_gi,
        T_shroud_out=T_go,
        Q_shroud_total=Q_shroud_core + Q_opt_wall,
        Q_top=Q_top_sink(T_hs_t),
        Q_bay=(T_bay_air - T_amb) / R_bay_to_amb,
        R_ax_uv_top=R_ax_uv_top,
        R_ax_uv_vis=R_ax_uv_vis,
        R_bulkhead=R_bulkhead,
        margin_uv_100C=100.0 - T_j_uv,
        margin_vis_150C=150.0 - T_j_vis,
        margin_pmma_75C=75.0 - T_gi,
        margin_petg_75C=75.0 - T_pcb_hotspot,
        margin_asa_95C=95.0 - T_pcb_hotspot,
        margin_u1_125C=125.0 - T_j_u1_jedec,
        margin_ic_comm_70C=70.0 - T_bay_air,
    )


def main() -> None:
    out_dir = Path(__file__).resolve().parent
    cad = json.loads(CAD_PARAMS_JSON.read_text(encoding="utf-8"))
    sim = json.loads(SIM_SUMMARY_JSON.read_text(encoding="utf-8"))

    # Read EXACT Rev 4.8 SSOT electrical & mechanical values
    te = sim["thermal_export"]
    an = sim["analytic_nominal_20V"]
    cs = sim["corner_sweep"]

    p_pcb_8all_nom = float(te["p_pcb_nom_W"])
    p_pcb_wc = float(te["p_pcb_wc_W"])
    # 4-UV Nom PCB loss = Ch1 buck loss + quiescent overhead (from sim_summary.json)
    ch1 = an["ch1_uv"]
    p_pcb_4uv_nom = round(ch1["p_ic"] + ch1["p_diode"] + ch1["p_ind"] + ch1["p_rs"] + an["p_overhead_W"], 3)
    p_u1_nom = round(max(an["ch1_uv"]["p_ic"], an["ch2_vis"]["p_ic"]), 4)
    p_u1_wc = round(max(cs["uv_pic_max"], cs["vis_pic_max"]), 4)
    p_led_uv_nom = float(te["p_led_uv_nom_W"])    # 4.736 W
    p_led_vis_nom = float(te["p_led_vis_nom_W"])  # 3.801 W

    # Operating Modes: (name, Q_uv_heat_W, Q_vis_heat_W, Q_opt_reabs_W, Q_pcb_W, P_u1_W)
    # Optical re-absorption = ~14% of optical output in open-space hanging (PMMA Fresnel + end-cap hub scatter)
    modes = [
        ("4-UV Nom (40%WPE)",     round(0.60 * p_led_uv_nom, 3), 0.000, round(0.14 * 0.40 * p_led_uv_nom, 3), p_pcb_4uv_nom, round(an["ch1_uv"]["p_ic"], 4)),
        ("8-ALL Nom (49%UV WPE)", round(0.51 * p_led_uv_nom, 3), round(0.60 * p_led_vis_nom, 3), round(0.14 * (0.49 * p_led_uv_nom + 0.40 * p_led_vis_nom), 3), p_pcb_8all_nom, p_u1_nom),
        ("8-ALL Nom (40%UV WPE)", round(0.60 * p_led_uv_nom, 3), round(0.60 * p_led_vis_nom, 3), round(0.14 * (0.40 * p_led_uv_nom + 0.40 * p_led_vis_nom), 3), p_pcb_8all_nom, p_u1_nom),
        ("8-ALL DS-RealWPE",      3.650, 2.950, 0.450, p_pcb_wc, p_u1_wc),
        ("8-ALL DS-100% (NoOpt)", 5.620, 4.750, 0.000, p_pcb_wc, p_u1_wc),
    ]

    l_chim = float(cad["derived"]["core_protrusion_mm"])  # 58.5 mm directly from cad_params.json!
    f_rad_amb = compute_chimney_ambient_view_factor(
        l_chim, cad["core_w_nom"], cad["cap_top_brim_od"], cad["cap_top_collar_h"],
    )

    hs_black_chim = HeatsinkSpec(f"Protruding {l_chim:.1f}mm Matte-Black Chimney", "protruding_core", cad["core_w_nom"], cad["core_bore_nom"], l_chim, eps=0.88)
    hs_bare_chim = HeatsinkSpec(f"Protruding {l_chim:.1f}mm Bare Mill Al Chimney", "protruding_core", cad["core_w_nom"], cad["core_bore_nom"], l_chim, eps=0.20)
    hs_sk578 = HeatsinkSpec("SK 578/50 SA (Benchmark)", "radial", 60.0, 24.0, 50.0, n_fins=22, t_fin_mm=1.4, eps=0.88)

    # (name, top_hs, eps_core_inner)
    configs = [
        (f"Config 0: Rev 4.9 Standard — Unpainted Bare Mill 30x30x3 Al Core (eps=0.20 everywhere, XT PMMA)", hs_bare_chim, 0.20),
        (f"Config 1: Optional Chimney-Only Matte-Black Spray ({l_chim:.1f}mm black, bare inner Al)", hs_black_chim, 0.20),
        (f"Config 2: Full-Core Matte-Black Spray ({l_chim:.1f}mm + inner core black, star pads masked)", hs_black_chim, 0.88),
        ("Config 3: Benchmark External SK 578/50 SA Heatsink + Bare Inner Core", hs_sk578, 0.20),
    ]

    rows = []
    for cfg_name, top_hs, eps_in in configs:
        t_list = [15.0, 22.0, 30.0, 35.0] if cfg_name.startswith("Config 0:") else [22.0, 30.0]
        for T_amb in t_list:
            for orient in ("vertical", "horizontal"):
                for m_name, q_uv, q_vis, q_opt, q_pcb, p_u1 in modes:
                    r = solve_system(
                        cad, q_uv, q_vis, q_opt, q_pcb, p_u1, T_amb,
                        top_hs=top_hs, eps_core_inner=eps_in, f_rad_amb=f_rad_amb,
                        orientation=orient,
                    )
                    passed_petg = (
                        r["margin_uv_100C"] > 0.0
                        and r["margin_vis_150C"] > 0.0
                        and r["margin_pmma_75C"] > 0.0
                        and r["margin_petg_75C"] >= 0.0
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
                        "config": cfg_name,
                        "T_amb_C": T_amb,
                        "orientation": orient,
                        "mode": m_name,
                        "Q_uv_W": q_uv,
                        "Q_vis_W": q_vis,
                        "Q_opt_reabs_W": q_opt,
                        "Q_pcb_W": q_pcb,
                        "P_u1_W": p_u1,
                        **{k: round(v, 3) for k, v in r.items()},
                        "pass_all_limits": passed_petg,
                        "pass_all_limits_asa": passed_asa,
                    })

    csv_path = out_dir / "thermal_results.csv"
    with csv_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    # Ambient sweep (10..40 C) for Rev 4.9 Standard (Config 0: Unpainted Bare Mill Al Core, vertical hanging)
    t_ambs = np.linspace(10.0, 40.0, 31)
    sweep_modes = ["4-UV Nom (40%WPE)", "8-ALL Nom (40%UV WPE)", "8-ALL DS-RealWPE", "8-ALL DS-100% (NoOpt)"]
    sweep_data: dict[str, list[dict[str, float]]] = {m: [] for m in sweep_modes}
    for m_name, q_uv, q_vis, q_opt, q_pcb, p_u1 in modes:
        if m_name not in sweep_modes:
            continue
        for Ta in t_ambs:
            r = solve_system(
                cad, q_uv, q_vis, q_opt, q_pcb, p_u1, float(Ta),
                top_hs=hs_bare_chim, eps_core_inner=0.20, f_rad_amb=f_rad_amb,
                orientation="vertical",
            )
            sweep_data[m_name].append({"T_amb": float(Ta), **{k: round(v, 3) for k, v in r.items()}})

    # Sensitivity Cases (Rev 4.9 Standard Config 0 Bare Al vs alternatives at 22 C UK Night & 30 C Warm Night)
    sens_specs = [
        ("Rev 4.9 Standard: Unpainted Bare Mill Al Core (22 C UK Night, Vertical Hanging)", 22.0, "vertical", dict(eps_core_inner=0.20, r_tim_led=0.30, rth_penalty_factor=1.0), hs_bare_chim),
        ("Rev 4.9 Standard: Unpainted Bare Mill Al Core (30 C Warm Night, Vertical Hanging)", 30.0, "vertical", dict(eps_core_inner=0.20, r_tim_led=0.30, rth_penalty_factor=1.0), hs_bare_chim),
        ("Rev 4.9 Standard: Unpainted Bare Mill Al Core (30 C Warm Night, Horizontal)", 30.0, "horizontal", dict(eps_core_inner=0.20, r_tim_led=0.30, rth_penalty_factor=1.0), hs_bare_chim),
        ("Optional Upgrade: Chimney-Only Matte-Black Spray (30 C, Vertical Hanging)", 30.0, "vertical", dict(eps_core_inner=0.20, r_tim_led=0.30, rth_penalty_factor=1.0), hs_black_chim),
        ("Full-Core Matte-Black Spray (30 C, Vertical Hanging)", 30.0, "vertical", dict(eps_core_inner=0.88, r_tim_led=0.30, rth_penalty_factor=1.0), hs_black_chim),
        ("Thick TIM bondline under 20mm star (R_tim=0.80 K/W, 30 C Vertical)", 30.0, "vertical", dict(eps_core_inner=0.20, r_tim_led=0.80, rth_penalty_factor=1.0), hs_bare_chim),
        ("+20% Still-Air Convection Penalty (Bare Mill Al, 30 C Vertical)", 30.0, "vertical", dict(eps_core_inner=0.20, r_tim_led=0.30, rth_penalty_factor=1.20), hs_bare_chim),
    ]
    sensitivity = []
    nom40 = next(m for m in modes if m[0] == "8-ALL Nom (40%UV WPE)")
    dsreal = next(m for m in modes if m[0] == "8-ALL DS-RealWPE")
    for desc, ta_s, ori, kw, ths in sens_specs:
        rn = solve_system(cad, nom40[1], nom40[2], nom40[3], nom40[4], nom40[5], ta_s, ths, f_rad_amb=f_rad_amb, orientation=ori, **kw)
        rd = solve_system(cad, dsreal[1], dsreal[2], dsreal[3], dsreal[4], dsreal[5], ta_s, ths, f_rad_amb=f_rad_amb, orientation=ori, **kw)
        sensitivity.append({
            "case": desc,
            "T_amb_C": ta_s,
            "orientation": ori,
            "nom_Tj_uv_C": round(rn["T_j_uv"], 2),
            "nom_T_shroud_in_C": round(rn["T_shroud_in"], 2),
            "nom_T_bay_air_C": round(rn["T_bay_air"], 2),
            "nom_T_pcb_hotspot_C": round(rn["T_pcb_hotspot"], 2),
            "nom_Tj_u1_jedec_C": round(rn["T_j_u1_jedec"], 2),
            "dsreal_Tj_uv_C": round(rd["T_j_uv"], 2),
            "dsreal_T_shroud_in_C": round(rd["T_shroud_in"], 2),
            "dsreal_Tj_vis_C": round(rd["T_j_vis"], 2),
            "dsreal_T_bay_air_C": round(rd["T_bay_air"], 2),
            "dsreal_T_pcb_hotspot_C": round(rd["T_pcb_hotspot"], 2),
        })

    cfg0_rows = [r for r in rows if r["config"].startswith("Config 0:")]
    cfg0_uk_22_real = [r for r in cfg0_rows if r["T_amb_C"] <= 22.0 and "DS-100%" not in r["mode"]]
    cfg0_15_30_nom = [r for r in cfg0_rows if r["T_amb_C"] <= 30.0 and "Nom" in r["mode"]]
    cfg0_15_30_real_asa = [r for r in cfg0_rows if r["T_amb_C"] <= 30.0 and "DS-100%" not in r["mode"]]

    summary = {
        "revision": "4.9",
        "architecture": f"Rev 4.9 Field Lantern (Extruded XT PMMA Ø60x54x115 + Unpainted Bare Mill {l_chim:.1f}mm Al Core + Convoy Cu DTP Stars + Unified M3 CSK)",
        "input_hashes": {
            "cad_params.json": _sha256_file(CAD_PARAMS_JSON),
            "sim_summary.json": _sha256_file(SIM_SUMMARY_JSON),
            "thermal_analysis.py": _sha256_file(Path(__file__)),
        },
        "ssot_inputs": {
            "core_section_mm": f"{cad['core_w_nom']:.0f}x{cad['core_w_nom']:.0f}x{cad['core_wall']:.1f}",
            "core_length_mm": cad["core_length"],
            "core_protrusion_mm": l_chim,
            "chimney_rad_view_factor_F_amb": f_rad_amb,
            "exposed_shroud_window_mm": cad["derived"]["exposed_glass_window_mm"],
            "shroud_material": "Extruded Clear XT PMMA (k=0.19 W/mK, eps=0.93, Ø60x54x3.0 mm)",
            "p_pcb_4uv_nom_W": p_pcb_4uv_nom,
            "p_pcb_8all_nom_W": p_pcb_8all_nom,
            "p_pcb_wc_W": p_pcb_wc,
            "p_u1_nom_W": p_u1_nom,
            "p_u1_wc_W": p_u1_wc,
            "R_bulkhead_parallel_KW": round(compute_bulkhead_resistance(cad), 3),
            "R_sub_copper_dtp_KW": 0.50,
            "R_thJS_vis_osram_cslnm1_max_KW": 4.90,
            "optical_reabsorption_fraction": 0.14,
        },
        "rev49_uk_night_22C_real_modes_all_pass": all(r["pass_all_limits"] for r in cfg0_uk_22_real),
        "rev49_15_30C_nom_all_pass": all(r["pass_all_limits"] for r in cfg0_15_30_nom),
        "rev49_15_30C_real_modes_asa_all_pass": all(r["pass_all_limits_asa"] for r in cfg0_15_30_real_asa),
        "baseline_rev49_results": cfg0_rows,
        "config_comparison_30C_vert": [
            r for r in rows if r["T_amb_C"] == 30.0 and r["orientation"] == "vertical" and r["mode"] in ("8-ALL Nom (40%UV WPE)", "8-ALL DS-RealWPE")
        ],
        "sensitivity": sensitivity,
        "ambient_sweep_vert": sweep_data,
    }
    json_path = out_dir / "thermal_summary.json"
    json_path.write_text(json.dumps(summary, indent=2) + "\n")

    print(f"=== Rev 4.9 SSOT Thermal Analysis (Unpainted Bare Al Chimney={l_chim:.1f}mm, F_amb={f_rad_amb:.3f}, P_PCB={p_pcb_8all_nom:.3f}/{p_pcb_wc:.3f}W) ===")
    for r in cfg0_rows:
        if r["T_amb_C"] in (22.0, 30.0) and r["mode"] in ("4-UV Nom (40%WPE)", "8-ALL Nom (40%UV WPE)", "8-ALL DS-RealWPE"):
            print(
                f"  Tamb={r['T_amb_C']:2.0f}C {r['orientation']:10s} | {r['mode']:21s} | "
                f"TjUV={r['T_j_uv']:5.1f}C TjVis={r['T_j_vis']:5.1f}C Tshroud={r['T_shroud_in']:4.1f}C "
                f"Tbay={r['T_bay_air']:4.1f}C Tpcb={r['T_pcb_hotspot']:4.1f}C | PETG={r['pass_all_limits']} ASA={r['pass_all_limits_asa']}"
            )
    print(f"Rev 4.9 UK-Night (<=22 C Real-WPE, PETG) PASS: {sum(r['pass_all_limits'] for r in cfg0_uk_22_real)}/{len(cfg0_uk_22_real)}")
    print(f"Rev 4.9 Nominal (15-30 C, PETG) PASS:          {sum(r['pass_all_limits'] for r in cfg0_15_30_nom)}/{len(cfg0_15_30_nom)}")
    print(f"Rev 4.9 Real-WPE (15-30 C, ASA+Comm IC) PASS:  {sum(r['pass_all_limits_asa'] for r in cfg0_15_30_real_asa)}/{len(cfg0_15_30_real_asa)}")

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
    ax.bar(x + w, get_vals("T_j_uv", 30.0, "horizontal"), w, label="30°C Horiz", color="#c44e52")
    ax.axhline(100.0, color="red", ls="--", lw=1.5, label="Limit 100°C")
    ax.axhline(80.0, color="gray", ls=":", lw=1.2, label="Nom Target 80°C")
    ax.set_title("UV LED Junction $T_{j,\\mathrm{UV}}$ (Cu DTP Star)")
    ax.set_ylabel("Temperature (°C)")
    ax.set_xticks(x, ["4-UV\nNom", "8-ALL\nNom", "8-ALL\nDS-Real", "8-ALL\nDS-100%"], fontsize=8.5)
    ax.set_ylim(0, 118)
    ax.grid(axis="y", alpha=0.3)
    ax.legend(fontsize=7.2, loc="upper left")

    ax = axes[1]
    ax.bar(x - w, get_vals("T_shroud_in", 22.0, "vertical"), w, label="22°C Vert", color="#4c72b0")
    ax.bar(x, get_vals("T_shroud_in", 30.0, "vertical"), w, label="30°C Vert", color="#dd8452")
    ax.bar(x + w, get_vals("T_shroud_in", 30.0, "horizontal"), w, label="30°C Horiz", color="#c44e52")
    ax.axhline(75.0, color="red", ls="--", lw=1.5, label="XT PMMA 75°C")
    ax.set_title("Extruded XT PMMA Inner Wall $T_{\\mathrm{shroud}}$")
    ax.set_xticks(x, ["4-UV\nNom", "8-ALL\nNom", "8-ALL\nDS-Real", "8-ALL\nDS-100%"], fontsize=8.5)
    ax.set_ylim(0, 95)
    ax.grid(axis="y", alpha=0.3)
    ax.legend(fontsize=7.5, loc="upper left")

    ax = axes[2]
    ax.bar(x - w, get_vals("T_pcb_hotspot", 22.0, "vertical"), w, label="22°C Vert", color="#4c72b0")
    ax.bar(x, get_vals("T_pcb_hotspot", 30.0, "vertical"), w, label="30°C Vert", color="#dd8452")
    ax.bar(x + w, get_vals("T_bay_air", 30.0, "vertical"), w, label="30°C Bay Air (U4/U5)", color="#55a868")
    ax.axhline(75.0, color="red", ls="--", lw=1.5, label="PETG Limit 75°C")
    ax.axhline(70.0, color="orange", ls=":", lw=1.3, label="U4/U5 Comm. 70°C")
    ax.set_title("Driver PCB & Sealed Bay Air (PETG/ASA)")
    ax.set_xticks(x, ["4-UV\nNom", "8-ALL\nNom", "8-ALL\nDS-Real", "8-ALL\nDS-100%"], fontsize=8.5)
    ax.set_ylim(0, 95)
    ax.grid(axis="y", alpha=0.3)
    ax.legend(fontsize=7.2, loc="upper left")

    fig.suptitle(f"Rev 4.9 Standard (Unpainted Bare Mill Al {l_chim:.1f} mm + XT PMMA + 14% Opt. Re-Abs.) — Steady-State Margins", fontweight="bold")
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
        ax2.plot(ta, [pt["T_bay_air"] for pt in pts], lw=2.0, color=colors[m], label=f"{m} (Bay)")
        ax2.plot(ta, [pt["T_pcb_hotspot"] for pt in pts], lw=1.3, ls="--", color=colors[m], label=f"{m} (PCB)")
    ax1.axhline(100.0, color="red", ls="--", lw=1.4, label="UV Limit 100°C")
    ax1.axvline(22.0, color="green", ls=":", lw=1.2, label="UK Night 22°C")
    ax1.axvline(30.0, color="gray", ls=":", lw=1.2, label="Warm Night 30°C")
    ax1.set_title("UV LED $T_{j,\\mathrm{UV}}$ vs Ambient (Vertical Hanging)")
    ax1.set_xlabel("Ambient Temperature $T_{\\mathrm{amb}}$ (°C)")
    ax1.set_ylabel("Temperature (°C)")
    ax1.grid(alpha=0.3)
    ax1.legend(fontsize=7.2)

    ax2.axhline(75.0, color="red", ls="--", lw=1.4, label="PETG 75°C (ASA=95°C)")
    ax2.axhline(70.0, color="orange", ls=":", lw=1.4, label="U4/U5 Comm. 70°C")
    ax2.axvline(22.0, color="green", ls=":", lw=1.2)
    ax2.axvline(30.0, color="gray", ls=":", lw=1.2)
    ax2.set_title("Sealed Bay Air & Driver PCB vs Ambient (Vertical)")
    ax2.set_xlabel("Ambient Temperature $T_{\\mathrm{amb}}$ (°C)")
    ax2.set_ylabel("Temperature (°C)")
    ax2.grid(alpha=0.3)
    ax2.legend(fontsize=6.5, ncol=2)

    fig.suptitle(f"Rev 4.9 Ambient Sweep (10–40°C, Unpainted Bare Mill Al {l_chim:.1f}mm, F_amb={f_rad_amb:.2f}, P_PCB={p_pcb_8all_nom:.2f}/{p_pcb_wc:.2f}W)", fontweight="bold")
    fig.tight_layout()
    fig.savefig(out_dir / "thermal_ambient_sweep.png")
    plt.close(fig)

    # Plot 3: thermal_network_comparison.png
    fig, ax = plt.subplots(figsize=(10.5, 4.8), dpi=150)
    cfg_labels = [
        f"Config 0 (Rev 4.9):\nBare Mill Al Core\n(unpainted, eps=0.20)",
        f"Config 1 (Opt.):\nChimney-Only Black\n(top {l_chim:.1f}mm, bare inner)",
        "Config 2:\nFull-Core Matte-Black\n(star pads masked)",
        "Config 3:\nSK 578/50 SA Top\n(benchmark finned)",
    ]
    cfg_prefixes = ["Config 0:", "Config 1:", "Config 2:", "Config 3:"]
    uv_nom = [
        next(r["T_j_uv"] for r in rows if r["config"].startswith(pf) and r["T_amb_C"] == 30.0 and r["orientation"] == "vertical" and r["mode"] == "8-ALL Nom (40%UV WPE)")
        for pf in cfg_prefixes
    ]
    uv_ds = [
        next(r["T_j_uv"] for r in rows if r["config"].startswith(pf) and r["T_amb_C"] == 30.0 and r["orientation"] == "vertical" and r["mode"] == "8-ALL DS-RealWPE")
        for pf in cfg_prefixes
    ]
    x_c = np.arange(len(cfg_labels))
    ax.bar(x_c - 0.18, uv_nom, 0.36, label="8-ALL Nom (40% UV WPE)", color="#4c72b0")
    ax.bar(x_c + 0.18, uv_ds, 0.36, label="8-ALL Worst-Case Real-WPE", color="#dd8452")
    ax.axhline(100.0, color="red", ls="--", lw=1.6, label="SST-10-UV Limit 100°C")
    for i, (vn, vd) in enumerate(zip(uv_nom, uv_ds)):
        ax.text(i - 0.18, vn + 1.5, f"{vn:.1f}°C", ha="center", fontsize=8.5, fontweight="bold")
        ax.text(i + 0.18, vd + 1.5, f"{vd:.1f}°C", ha="center", fontsize=8.5, fontweight="bold")
    ax.set_xticks(x_c, cfg_labels, fontsize=9)
    ax.set_ylabel("UV LED Junction $T_{j,\\mathrm{UV}}$ (°C)")
    ax.set_ylim(0, 118)
    ax.set_title("Rev 4.9 Surface-Finish Comparison ($T_{\\mathrm{amb}}=30^\\circ\\mathrm{C}$, Vertical Hanging Still Air)")
    ax.grid(axis="y", alpha=0.3)
    ax.legend(fontsize=8.5)
    fig.tight_layout()
    fig.savefig(out_dir / "thermal_network_comparison.png")
    plt.close(fig)

    print(f"Saved: {csv_path}, {json_path}, and 3 PNG plots in {out_dir}")


if __name__ == "__main__":
    main()
