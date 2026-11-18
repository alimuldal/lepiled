#!/usr/bin/env python3
"""
Reproducible Coupled First-Principles 2D/3D Thermal Analysis for LepiLED DIY Maxi Switch (M3).

Reconciled directly to the exact CAD dimensions in `mechanical_design/cad/params.py`,
M1 electrical dissipation budgets in `circuit_design/INTERFACE_CONTRACT.md` §2.1,
and M2 PCB layouts (`pcb_design/led_mcpcb/build_led_mcpcb.py` & `pcb_design/driver_pcb/build_driver_pcb.py`).

Physics modeled:
  1. Genuine 2D Finite-Volume (FVM) PDE solver on exact M2 MCPCB thermal copper polygons
     (1.30 x 3.25 mm pinched-neck thermal pad, 1.30 mm 1 oz Cu neck, 100 um 1.0 W/(m*K) dielectric):
     dynamically solves R_diel_UV_avg = 15.29 K/W (max 17.54 K/W) and R_diel_Vis_avg = 18.89 K/W.
  2. Genuine 3D 3-layer FVM PDE solver on exact M2 Driver PCB (36 x 46 x 1.6 mm FR4, F.Cu pours,
     B.Cu GND plane with SW1/SW2 keepouts, 32x GND vias [6x U1 DAP + 6x U2 DAP + 20x stitching], 4x H1..H4
     plated holes, 25 um soldermask, 0.5 mm TG-A6200 gap pad with J1/TP1/TP2/J2/J3/J4/H1..H4 cutouts,
     and MECH-ADAPT-BOT Ø90x3 + Ø59x5 mm Al 6061 pedestal with 1.8 mm milled pockets):
     computes R_eff_bot_avg, T_pcb_bot_avg, T_pcb_top_avg, T_j,U1 (3D via-coupled & JEDEC), and T_j,Q1 (max of Q1A/Q1B).
  3. Non-linear natural convection (Bar-Cohen/Rohsenow Elenbaas radial-fin channel choking,
     Churchill-Chu external cylinder/vertical plate, McAdams horizontal up/down plates)
     + Stefan-Boltzmann radiation for MECH-HS-EXT-TOP (Fischer SK 578/50 SA, Ø60x50 mm) and
     MECH-HS-EXT-BOT (Fischer SK LED R 80 SA, Ø80x70 mm, catalog 1.35 K/W).
  4. Parallel internal borosilicate 3.3 tube heat path (exposed window = 126.0 mm, eps_core = 0.88
     via MECH-COAT-1 matte-black coating; bare Al eps = 0.34 also evaluated in sensitivity).
  5. First-principles parallel bulkhead thermal decoupling (6.0 mm PETG/PA12 bulkhead + outer wall +
     2x M4 SS DIN 7991 CSK bulkhead bolts w/ nylon CSK insulating washers + internal cavity radiation -> R_bulkhead ~ 11.2 K/W)
     and first-principles top butt-joint spreading (core TIM + 3 mm radial Al + hub TIM -> 0.284 K/W).
"""

from __future__ import annotations

import csv
import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
from matplotlib.path import Path as MplPath
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import fsolve
from scipy.sparse import lil_matrix
from scipy.sparse.linalg import spsolve

# Import exact CAD geometry
CAD_DIR = Path(__file__).resolve().parent.parent / "cad"
sys.path.insert(0, str(CAD_DIR))
from params import LepiLEDParams  # noqa: E402

SIGMA = 5.670374419e-8


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
# 1. Genuine 2D FVM MCPCB Pinched-Neck Thermal Spreading Solver
# ---------------------------------------------------------------------------

def _uv_mcpcb_polygon() -> list[tuple[float, float]]:
    """Exact M2 D_UV thermal copper polygon from pcb_design/led_mcpcb/build_led_mcpcb.py."""
    pts = [
        (-0.65, -2.35), (-7.20, -2.35), (-7.20, -17.00), (+7.20, -17.00), (+7.20, -2.35), (+0.65, -2.35),
        (+0.65, +2.35), (+9.20, +2.35), (+9.20, +20.60), (+8.40, +21.30), (+3.60, +21.30),
    ]
    for deg in range(0, -181, -15):
        rad = math.radians(deg)
        pts.append((3.60 * math.cos(rad), 14.0 + 3.60 * math.sin(rad)))
    pts.extend([(-3.60, +21.30), (-8.40, +21.30), (-9.20, +20.60), (-9.20, +2.35), (-0.65, +2.35)])
    return pts


def _vis_mcpcb_polygon() -> list[tuple[float, float]]:
    """Exact M2 D_VIS thermal copper polygon from pcb_design/led_mcpcb/build_led_mcpcb.py."""
    return [
        (-0.65, -1.65), (+0.65, -1.65), (+0.65, +2.35), (+2.30, +2.35), (+2.30, -1.65),
        (+3.40, -1.65), (+3.40, -4.40), (+7.20, -4.40), (+7.20, +17.20), (-7.20, +17.20),
        (-7.20, -4.40), (-3.40, -4.40), (-3.40, -1.65), (-2.30, -1.65), (-2.30, +2.35), (-0.65, +2.35),
    ]


def solve_mcpcb_2d_r_diel(
    poly_pts: list[tuple[float, float]] | None,
    pad_w_mm: float,
    pad_h_mm: float,
    dx_mm: float = 0.10,
    t_cu_um: float = 35.0,
    k_cu: float = 385.0,
    t_diel_um: float = 100.0,
    k_diel: float = 1.0,
) -> dict[str, float]:
    """Solve 2D steady-state FVM PDE on exact MCPCB Cu geometry over dielectric."""
    xs = np.arange(-9.5 + dx_mm / 2.0, 9.5, dx_mm)
    ys = np.arange(-17.5 + dx_mm / 2.0, 22.0, dx_mm)
    XX, YY = np.meshgrid(xs, ys, indexing="ij")
    pad_mask = (np.abs(XX) <= pad_w_mm / 2.0) & (np.abs(YY) <= pad_h_mm / 2.0)
    if poly_pts is None:
        mask = pad_mask
    else:
        poly = MplPath(poly_pts)
        pts_grid = np.column_stack([XX.ravel(), YY.ravel()])
        inside = poly.contains_points(pts_grid).reshape(XX.shape)
        mask = inside | pad_mask

    coords = np.argwhere(mask)
    n = len(coords)
    idx_map = -np.ones(XX.shape, dtype=int)
    for k, (i, j) in enumerate(coords):
        idx_map[i, j] = k

    cell_a = (dx_mm * 1e-3) ** 2
    g_diel = (k_diel / (t_diel_um * 1e-6)) * cell_a
    g_cu = k_cu * (t_cu_um * 1e-6)

    A = lil_matrix((n, n))
    b = np.zeros(n)
    q_cell = 1.0 / float(np.sum(pad_mask))
    for k, (i, j) in enumerate(coords):
        diag = g_diel
        if pad_mask[i, j]:
            b[k] = q_cell
        for di, dj in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            ni, nj = i + di, j + dj
            if 0 <= ni < XX.shape[0] and 0 <= nj < XX.shape[1] and mask[ni, nj]:
                diag += g_cu
                A[k, idx_map[ni, nj]] = -g_cu
        A[k, k] = diag

    T = spsolve(A.tocsr(), b)
    T_pad = T[idx_map[pad_mask]]
    return {
        "R_diel_avg_KW": float(T_pad.mean()),
        "R_diel_max_KW": float(T_pad.max()),
        "cu_area_mm2": float(n * dx_mm * dx_mm),
    }


# ---------------------------------------------------------------------------
# 2. Genuine 3D 3-Layer FVM Driver PCB + TG-A6200 + MECH-ADAPT-BOT Solver
# ---------------------------------------------------------------------------

def solve_driver_pcb_3d(
    params: LepiLEDParams,
    mode_scale: str = "DS-100%",
    pad_thick_mm: float = 0.5,
    pad_k: float = 6.2,
    bcu_oz: float = 1.0,
    mask_um: float = 25.0,
    dx_mm: float = 0.25,
) -> dict[str, float]:
    """
    Solve 3D 3-layer (F.Cu / B.Cu / MECH-ADAPT-BOT) FVM PDE on exact M2 Driver PCB geometry.
    Models explicit isolated F.Cu copper pours (U1/U2 DAPs, VOUT1, VOUT2, SW1_NODE, SW2_NODE,
    VBUS_FUSED, V_MID) with 15% signal trace fill elsewhere and FR4-only lateral coupling across
    isolation gaps, plus full coupling between B.Cu and Layer 2 (MECH-ADAPT-BOT).
    Returns temperature rises above MECH-ADAPT-BOT sink hub (T_hs_b) and effective R_eff_bot_avg.
    """
    nx = int(round(params.pcb_w / dx_mm))
    ny = int(round(params.pcb_l / dx_mm))
    xs = -0.5 * params.pcb_w + (np.arange(nx) + 0.5) * dx_mm
    ys = -0.5 * params.pcb_l + (np.arange(ny) + 0.5) * dx_mm
    XX, YY = np.meshgrid(xs, ys, indexing="ij")
    N = nx * ny

    t_cu = 0.035e-3 * bcu_oz
    k_cu = 385.0
    k_fr4_z = 0.30
    k_fr4_xy = 0.35
    t_fr4 = params.pcb_thick * 1e-3
    k_al = 167.0
    cell_a = (dx_mm * 1e-3) ** 2

    g_fr4_lat = k_fr4_xy * (t_fr4 * 0.5)
    g_fcu_pour = k_cu * t_cu * 1.00 + g_fr4_lat
    g_fcu_sig = k_cu * t_cu * 0.15 + g_fr4_lat
    g_bcu_lat = k_cu * t_cu * 0.95 + g_fr4_lat

    # Explicit isolated F.Cu copper pour regions (build_driver_pcb.py:1490-1555)
    # 0 = 15% signal/trace fill; 1..8 = isolated solid copper pours separated by FR4 isolation gaps
    fcu_reg = np.zeros((nx, ny), dtype=int)
    pts_flat = np.column_stack([XX.ravel(), YY.ravel()])

    # 3: VOUT1 pour & 4: VOUT2 pour (priority 3 zones; cover D9.1 (-5.6, +10.3) and D10.1 (+13.4, +10.3))
    vout1_poly = MplPath([(-17.5, 14.9), (-11.2, 14.9), (-8.2, 12.2), (-6.8, 8.4), (-0.5, 8.4), (-0.5, 22.5), (-17.5, 22.5)])
    vout2_poly = MplPath([(0.5, 14.9), (7.8, 14.9), (11.0, 12.2), (12.2, 8.4), (17.5, 8.4), (17.5, 22.5), (0.5, 22.5)])
    m_vout1 = vout1_poly.contains_points(pts_flat).reshape(nx, ny)
    m_vout2 = vout2_poly.contains_points(pts_flat).reshape(nx, ny)
    fcu_reg[m_vout1] = 3
    fcu_reg[m_vout2] = 4

    # 5: SW1_NODE & 6: SW2_NODE (exact pads L1.2/L2.2, D9.2/D10.2, U1.7/U2.7 + 1.00 mm bridge, ~13.53 mm^2 each)
    m_sw1 = (
        (((XX >= -12.50) & (XX <= -10.70) & (YY >= 9.30) & (YY <= 14.30))
         | ((XX >= -10.40) & (XX <= -8.80) & (YY >= 9.45) & (YY <= 11.15))
         | ((XX >= -10.535) & (XX <= -10.115) & (YY >= 6.90) & (YY <= 8.30))
         | ((XX >= -10.825) & (XX <= -9.825) & (YY >= 7.60) & (YY <= 10.80))
         | ((XX >= -11.60) & (XX <= -9.60) & (YY >= 9.80) & (YY <= 10.80)))
        & (~m_vout1)
    )
    m_sw2 = (
        (((XX >= 6.50) & (XX <= 8.30) & (YY >= 9.30) & (YY <= 14.30))
         | ((XX >= 8.60) & (XX <= 10.20) & (YY >= 9.45) & (YY <= 11.15))
         | ((XX >= 8.465) & (XX <= 8.885) & (YY >= 6.90) & (YY <= 8.30))
         | ((XX >= 8.175) & (XX <= 9.175) & (YY >= 7.60) & (YY <= 10.80))
         | ((XX >= 7.40) & (XX <= 9.40) & (YY >= 9.80) & (YY <= 10.80)))
        & (~m_vout2)
    )
    fcu_reg[m_sw1] = 5
    fcu_reg[m_sw2] = 6

    # 1: U1 DAP (-10.00, +5.40) & 2: U2 DAP (+9.00, +5.40) — 90-deg rotated 3.0 x 2.0 mm DAPs
    m_u1_dap = (np.abs(XX - (-10.00)) <= 1.50) & (np.abs(YY - 5.40) <= 1.00)
    m_u2_dap = (np.abs(XX - 9.00) <= 1.50) & (np.abs(YY - 5.40) <= 1.00)
    fcu_reg[m_u1_dap] = 1
    fcu_reg[m_u2_dap] = 2

    # 7: VBUS_FUSED & 8: V_MID (exact build_driver_pcb.py:1501-1504 pours)
    m_vbus_fused = (XX >= -17.0) & (XX <= -13.6) & (YY >= -14.8) & (YY <= -7.0)
    m_v_mid = (XX >= -13.8) & (XX <= -10.6) & (YY >= -7.6) & (YY <= -5.6)
    fcu_reg[m_vbus_fused] = 7
    fcu_reg[m_v_mid] = 8

    # Exact B.Cu keepouts under SW1_NODE & SW2_NODE (build_driver_pcb.py:1526-1531, Y >= +6.65)
    bcu_ko = (
        ((XX >= -12.90) & (XX <= -8.25) & (YY >= 8.80) & (YY <= 14.70))
        | ((XX >= -11.15) & (XX <= -9.60) & (YY >= 6.65) & (YY <= 9.00))
        | ((XX >= 6.10) & (XX <= 10.75) & (YY >= 8.80) & (YY <= 14.70))
        | ((XX >= 7.85) & (XX <= 9.40) & (YY >= 6.65) & (YY <= 9.00))
    )

    # TG-A6200 active area after subtracting J2/J3, J4, J1+TP1/TP2, and H1..H4 cutouts
    in_tim = (np.abs(XX) <= 0.5 * params.tim_pcb_w) & (np.abs(YY) <= 0.5 * params.tim_pcb_l)
    cut_j23 = (
        (np.abs(XX - params.adapt_bot_j23_pocket_x) <= 0.5 * params.adapt_bot_j23_pocket_w)
        & (np.abs(YY - params.adapt_bot_j23_pocket_y) <= 0.5 * params.adapt_bot_j23_pocket_l)
    )
    cut_j4 = (
        (np.abs(XX - params.adapt_bot_j4_pocket_x) <= 0.5 * params.adapt_bot_j4_pocket_w)
        & (np.abs(YY - params.adapt_bot_j4_pocket_y) <= 0.5 * params.adapt_bot_j4_pocket_l)
    )
    cut_j1tp = (
        (np.abs(XX - params.adapt_bot_j1tp_pocket_x) <= 0.5 * params.adapt_bot_j1tp_pocket_w)
        & (np.abs(YY - params.adapt_bot_j1tp_pocket_y) <= 0.5 * params.adapt_bot_j1tp_pocket_l)
    )
    cut_holes = np.zeros_like(XX, dtype=bool)
    for hx in (-params.pcb_hole_x, params.pcb_hole_x):
        for hy in (-params.pcb_hole_y, params.pcb_hole_y):
            cut_holes |= ((XX - hx) ** 2 + (YY - hy) ** 2) <= (0.5 * params.pcb_hole_keepout) ** 2

    pad_active = in_tim & (~cut_j23) & (~cut_j4) & (~cut_j1tp) & (~cut_holes)
    pocket_active = cut_j23 | cut_j4 | cut_j1tp

    g_fr4_z = (k_fr4_z / t_fr4) * cell_a
    g_via_03 = k_cu * (math.pi * (0.15e-3 ** 2 - 0.13e-3 ** 2)) / t_fr4
    g_via_h = k_cu * (math.pi * (1.35e-3 ** 2 - 1.325e-3 ** 2)) / t_fr4

    # TG-A6200 catalog thermal impedance: bulk t/k + 1.27 K*cm^2/W contact (matches 2.88 K*cm^2/W @ 1.0mm, 6.2 W/mK)
    r_pad_cm2 = (pad_thick_mm * 0.1 / (pad_k * 0.01)) + 1.27
    r_mask_cm2 = (mask_um * 1e-4) / (0.20 * 0.01)
    g_tim_cell = cell_a / ((r_pad_cm2 + r_mask_cm2) * 1e-4)
    g_air_cell = cell_a / ((pad_thick_mm * 1e-3 / 0.026) + (mask_um * 1e-6 / 0.20))

    # MECH-ADAPT-BOT thickness (3.0 mm plate + 5.0 mm pedestal = 8.0 mm; minus 1.8 mm in milled pockets)
    t_al_full = (params.adapt_bot_thick + params.adapt_bot_pedestal_h) * 1e-3
    t_al_pocket = t_al_full - params.adapt_bot_pin_pocket_depth * 1e-3
    adapt_t_grid = np.where(pocket_active, t_al_pocket, t_al_full)

    # Component heat sources synced 1:1 to M2 driver_pcb_cpl.csv (U1/U2, D9/D10, L1/L2, F1, Q1A/Q1B, R3/R4)
    # Note: all 32 GND vias (incl. 6x U1 DAP + 6x U2 DAP) are placed at exact driver_pcb.kicad_pcb coords below.
    if mode_scale == "DS-100%":
        sources = [
            (-10.00, 5.40, 3.0, 2.0, 1.290),   # U1 (rot 90, 3.0x2.0 mm DAP)
            (9.00, 5.40, 3.0, 2.0, 0.839),     # U2 (rot 90, 3.0x2.0 mm DAP)
            (-7.60, 10.30, 4.5, 2.6, 0.182),   # D9 (SMA rot 180)
            (11.40, 10.30, 4.5, 2.6, 0.182),   # D10 (SMA rot 180)
            (-13.80, 11.80, 6.0, 6.0, 0.243),  # L1 (SRN6045 rot 0)
            (5.20, 11.80, 6.0, 6.0, 0.159),    # L2 (SRN6045 rot 0)
            (-12.80, -13.20, 7.3, 5.1, 0.262), # F1 (2920 rot 180)
            (-14.20, -7.80, 2.5, 3.0, 0.545),  # Q1A (SOT-23 rot 90)
            (-10.20, -5.80, 2.5, 3.0, 0.545),  # Q1B (SOT-23 rot 270)
            (-2.40, 5.20, 1.6, 3.2, 0.0735),   # R3 (1206 rot 270)
            (16.40, 5.20, 1.6, 3.2, 0.0735),   # R4 (1206 rot 270)
        ]
    elif mode_scale == "8-ALL Nom":
        sources = [
            (-10.00, 5.40, 3.0, 2.0, 0.404),
            (9.00, 5.40, 3.0, 2.0, 0.255),
            (-7.60, 10.30, 4.5, 2.6, 0.129),
            (11.40, 10.30, 4.5, 2.6, 0.129),
            (-13.80, 11.80, 6.0, 6.0, 0.070),
            (5.20, 11.80, 6.0, 6.0, 0.044),
            (-12.80, -13.20, 7.3, 5.1, 0.105),
            (-14.20, -7.80, 2.5, 3.0, 0.200),
            (-10.20, -5.80, 2.5, 3.0, 0.200),
            (-2.40, 5.20, 1.6, 3.2, 0.032),
            (16.40, 5.20, 1.6, 3.2, 0.032),
        ]
    else:  # 4-UV Nom (0.80 W)
        sources = [
            (-10.00, 5.40, 3.0, 2.0, 0.404),
            (-7.60, 10.30, 4.5, 2.6, 0.129),
            (-13.80, 11.80, 6.0, 6.0, 0.070),
            (-12.80, -13.20, 7.3, 5.1, 0.045),
            (-14.20, -7.80, 2.5, 3.0, 0.060),
            (-10.20, -5.80, 2.5, 3.0, 0.060),
            (-2.40, 5.20, 1.6, 3.2, 0.032),
        ]

    q_grid = np.zeros((nx, ny))
    via_grid = np.zeros((nx, ny))
    for sx, sy, sw, sh, pq in sources:
        m = (np.abs(XX - sx) <= 0.5 * sw) & (np.abs(YY - sy) <= 0.5 * sh)
        q_grid[m] += pq / float(np.sum(m))

    # Exact 32 GND vias extracted 1:1 from pcb_design/driver_pcb/driver_pcb.kicad_pcb
    # (6x inside U1 DAP + 6x inside U2 DAP + 20x stitching vias)
    gnd_via_locs = [
        # U1 DAP (6x)
        (-10.65, 4.90), (-10.65, 5.90), (-10.00, 4.90), (-10.00, 5.90), (-9.35, 4.90), (-9.35, 5.90),
        # U2 DAP (6x)
        (8.35, 4.90), (8.35, 5.90), (9.00, 4.90), (9.00, 5.90), (9.65, 4.90), (9.65, 5.90),
        # Stitching GND vias (20x)
        (-16.54, -1.60), (-13.60, 6.725), (-12.00, 1.85), (-7.40, -2.00), (-7.00, 5.70),
        (-4.60, -13.20), (-3.475, 13.70), (-2.65, -9.20), (-2.65, -7.70), (-2.575, -13.20),
        (0.625, -13.20), (4.40, -12.20), (5.525, -3.20), (6.40, 6.725), (7.10, 1.85),
        (10.60, -11.15), (11.675, -3.25), (12.00, 5.70), (15.125, 13.70), (15.75, -1.40),
    ]
    for vx, vy in gnd_via_locs:
        i = int(np.clip((vx + 0.5 * params.pcb_w) / dx_mm, 0, nx - 1))
        j = int(np.clip((vy + 0.5 * params.pcb_l) / dx_mm, 0, ny - 1))
        via_grid[i, j] += g_via_03
    for hx in (-params.pcb_hole_x, params.pcb_hole_x):
        for hy in (-params.pcb_hole_y, params.pcb_hole_y):
            m_h = ((XX - hx) ** 2 + (YY - hy) ** 2) <= (2.5 ** 2)
            via_grid[m_h] += g_via_h / float(np.sum(m_h))

    in_hub = np.hypot(XX, YY) <= (0.5 * params.hs_ext_bot_core_dia)
    hub_area = float(np.sum(in_hub)) * cell_a
    # Bottom TIM-2 + core interface (~0.08 K/W across Ø34 mm SK LED R 80 SA core)
    g_hub_cell = (cell_a / hub_area) / 0.08

    # Vectorized sparse FVM assembly over 3 layers (0: F.Cu, 1: B.Cu, 2: MECH-ADAPT-BOT)
    gf_b = g_fr4_z + via_grid
    gb_a = np.where(pad_active, g_tim_cell, g_air_cell)
    ga_s = np.where(in_hub, g_hub_cell, 0.0)

    k0 = np.arange(N).reshape(nx, ny)
    k1 = k0 + N
    k2 = k0 + 2 * N

    rows_i: list[np.ndarray] = []
    cols_j: list[np.ndarray] = []
    vals: list[np.ndarray] = []

    def add_coupling(ka: np.ndarray, kb: np.ndarray, g: np.ndarray) -> None:
        kf = ka.ravel()
        kt = kb.ravel()
        gf = g.ravel()
        rows_i.extend([kf, kt, kf, kt])
        cols_j.extend([kf, kt, kt, kf])
        vals.extend([gf, gf, -gf, -gf])

    # Vertical inter-layer couplings: F.Cu <-> B.Cu, B.Cu <-> MECH-ADAPT-BOT, and MECH-ADAPT-BOT -> Sink
    add_coupling(k0, k1, gf_b)
    add_coupling(k1, k2, gb_a)
    rows_i.append(k2.ravel())
    cols_j.append(k2.ravel())
    vals.append(ga_s.ravel())

    # Lateral in-plane couplings (+X and +Y edges)
    for sl_a, sl_b in [((slice(0, -1), slice(None)), (slice(1, None), slice(None))),
                       ((slice(None), slice(0, -1)), (slice(None), slice(1, None)))]:
        ra, rb = fcu_reg[sl_a], fcu_reg[sl_b]
        g0 = np.where(ra != rb, g_fr4_lat, np.where(ra > 0, g_fcu_pour, g_fcu_sig))
        add_coupling(k0[sl_a], k0[sl_b], g0)

        g1 = np.where(bcu_ko[sl_a] | bcu_ko[sl_b], g_fr4_lat, g_bcu_lat)
        add_coupling(k1[sl_a], k1[sl_b], g1)

        g2 = k_al * np.minimum(adapt_t_grid[sl_a], adapt_t_grid[sl_b])
        add_coupling(k2[sl_a], k2[sl_b], g2)

    from scipy.sparse import coo_matrix
    A = coo_matrix((np.concatenate(vals), (np.concatenate(rows_i), np.concatenate(cols_j))), shape=(3 * N, 3 * N)).tocsr()
    b = np.zeros(3 * N)
    b[:N] = q_grid.ravel()

    T = spsolve(A, b)
    T0, T1, T2 = T[:N].reshape(nx, ny), T[N:2 * N].reshape(nx, ny), T[2 * N:].reshape(nx, ny)
    q_tot = float(np.sum(q_grid))
    u1_mask = (np.abs(XX - (-10.00)) <= 1.50) & (np.abs(YY - 5.40) <= 1.00)
    q1a_mask = (np.abs(XX - (-14.20)) <= 1.25) & (np.abs(YY - (-7.80)) <= 1.50)
    q1b_mask = (np.abs(XX - (-10.20)) <= 1.25) & (np.abs(YY - (-5.80)) <= 1.50)
    dt_q1a = float(T0[q1a_mask].mean())
    dt_q1b = float(T0[q1b_mask].mean())
    return {
        "A_pad_cm2": round(float(np.sum(pad_active) * dx_mm * dx_mm / 100.0), 2),
        "Q_pcb_W": round(q_tot, 3),
        "R_eff_bot_avg_KW": float(T1.mean() / q_tot),
        "dT_adapt_bot_avg_C": float(T2.mean()),
        "dT_pcb_bot_avg_C": float(T1.mean()),
        "dT_pcb_top_avg_C": float(T0.mean()),
        "dT_U1_BCu_C": float(T1[u1_mask].mean()),
        "dT_U1_top_C": float(T0[u1_mask].mean()),
        "dT_Q1A_top_C": dt_q1a,
        "dT_Q1B_top_C": dt_q1b,
        "dT_Q1_top_C": max(dt_q1a, dt_q1b),
    }


# ---------------------------------------------------------------------------
# 3. Convection & Radiation Correlations
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


def horizontal_plate_down_h(T_s: float, T_amb: float, L_char: float) -> float:
    dT = max(0.05, T_s - T_amb)
    p = air_props(0.5 * (T_s + T_amb))
    Ra = 9.81 * p["beta"] * dT * (L_char ** 3) / (p["nu"] * p["alpha"])
    Nu = 0.27 * Ra ** 0.25
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
    kind: str  # "radial", "flat_disc", "plastic_pocket"
    D_out_mm: float
    D_core_mm: float = 24.0
    L_mm: float = 50.0
    n_fins: int = 22
    t_fin_mm: float = 1.4
    eps: float = 0.88


SK577_50 = HeatsinkSpec("SK 577/50 SA", "radial", 50.0, 20.0, 50.0, 20, 1.3)
SK578_50 = HeatsinkSpec("SK 578/50 SA", "radial", 60.0, 24.0, 50.0, 22, 1.4)
SK80_70 = HeatsinkSpec("SK LED R 80 SA", "radial", 80.0, 34.0, 70.0, 22, 1.2)
DISC_72 = HeatsinkSpec("Flat Al Disc 72x4", "flat_disc", 72.0, 0.0, 4.0, 0, 0.0)
PLASTIC_POCKET = HeatsinkSpec("Sealed PETG/PA12 Pocket", "plastic_pocket", 92.0, 0.0, 40.0, 0, 0.0)


def radial_heatsink_Q(
    T_s: float,
    T_amb: float,
    hs: HeatsinkSpec,
    orientation: str = "vertical",
    top_exposed: bool = True,
    bot_exposed: bool = False,
    adapt_plate_od_mm: float = 0.0,
    adapt_plate_t_mm: float = 0.0,
    rth_penalty_factor: float = 1.0,
) -> tuple[float, float, float, float]:
    """Heat dissipation Q [W] from radial-fin heatsink (+ optional exposed adapter rim)."""
    D_out = hs.D_out_mm * 1e-3
    D_core = hs.D_core_mm * 1e-3
    L = hs.L_mm * 1e-3
    t_fin = hs.t_fin_mm * 1e-3
    h_fin = 0.5 * (D_out - D_core)
    r_mid = 0.25 * (D_out + D_core)
    pitch_mid = 2.0 * math.pi * r_mid / hs.n_fins
    b_avg = max(0.0015, pitch_mid - t_fin)

    A_fin_sides = hs.n_fins * 2.0 * h_fin * L
    A_core_exposed = max(0.0, (math.pi * D_core - hs.n_fins * t_fin)) * L
    A_fin_tips = hs.n_fins * t_fin * L
    A_end = math.pi * (D_out ** 2) / 4.0 * 0.45

    A_rad_cyl = math.pi * D_out * L
    A_rad_end = (math.pi * D_out ** 2 / 4.0) * ((1.0 if top_exposed else 0.0) + (1.0 if bot_exposed else 0.0))

    A_adapt_rim = 0.0
    A_adapt_annulus = 0.0
    if adapt_plate_od_mm > hs.D_out_mm and adapt_plate_t_mm > 0.0:
        D_ad = adapt_plate_od_mm * 1e-3
        t_ad = adapt_plate_t_mm * 1e-3
        A_adapt_rim = math.pi * D_ad * t_ad
        A_adapt_annulus = 0.25 * math.pi * (D_ad ** 2 - D_out ** 2)

    h_est = 6.0
    m_fin = math.sqrt(2.0 * h_est / (200.0 * t_fin))
    eta_fin = math.tanh(m_fin * h_fin) / (m_fin * h_fin)

    dT = max(0.05, T_s - T_amb)
    if orientation == "vertical":
        h_chan = elenbaas_channel_h(T_s, T_amb, b_avg, L)
        h_tips = churchill_chu_vertical_plate_h(T_s, T_amb, L)
        h_top = horizontal_plate_up_h(T_s, T_amb, 0.25 * D_out) if top_exposed else 0.0
        h_bot = horizontal_plate_down_h(T_s, T_amb, 0.25 * D_out) if bot_exposed else 0.0
        Q_adapt = dT * (h_bot * A_adapt_annulus + h_tips * A_adapt_rim) if A_adapt_rim > 0 else 0.0
        Q_conv = dT * (
            h_chan * (eta_fin * A_fin_sides + A_core_exposed)
            + h_tips * A_fin_tips
            + h_top * A_end
            + h_bot * A_end
        ) + Q_adapt
    else:
        L_flow_horiz = max(0.020, 0.85 * D_out)
        h_chan_h = elenbaas_channel_h(T_s, T_amb, b_avg, L_flow_horiz) * 0.75
        h_tips_h = churchill_chu_horiz_cyl_h(T_s, T_amb, D_out)
        h_end_v = churchill_chu_vertical_plate_h(T_s, T_amb, D_out)
        Q_adapt = dT * (h_end_v * A_adapt_annulus + h_tips_h * A_adapt_rim) if A_adapt_rim > 0 else 0.0
        Q_conv = dT * (
            h_chan_h * (eta_fin * A_fin_sides + A_core_exposed)
            + h_tips_h * A_fin_tips
            + h_end_v * A_end * ((1.0 if top_exposed else 0.0) + (1.0 if bot_exposed else 0.0))
        ) + Q_adapt

    eps_eff = min(0.95, hs.eps + 0.04)
    T_s_K = T_s + 273.15
    T_a_K = T_amb + 273.15
    eps_adapt = 0.20
    Q_rad = SIGMA * (T_s_K ** 4 - T_a_K ** 4) * (
        eps_eff * A_rad_cyl + hs.eps * A_rad_end + eps_adapt * (A_adapt_rim + A_adapt_annulus)
    )
    Q_tot = (Q_conv + Q_rad) / rth_penalty_factor
    return Q_tot, Q_conv / rth_penalty_factor, Q_rad / rth_penalty_factor, eta_fin


def flat_disc_Q(T_s: float, T_amb: float, D_mm: float = 72.0, t_mm: float = 4.0,
                eps: float = 0.88, orientation: str = "vertical") -> float:
    D = D_mm * 1e-3
    t = t_mm * 1e-3
    A_face = math.pi * D ** 2 / 4.0
    A_rim = math.pi * D * t
    dT = max(0.05, T_s - T_amb)
    if orientation == "vertical":
        h_face = horizontal_plate_down_h(T_s, T_amb, 0.25 * D)
        h_rim = churchill_chu_vertical_plate_h(T_s, T_amb, t)
    else:
        h_face = churchill_chu_vertical_plate_h(T_s, T_amb, 0.8 * D)
        h_rim = churchill_chu_vertical_plate_h(T_s, T_amb, D)
    Q_conv = dT * (h_face * A_face + h_rim * A_rim)
    Q_rad = eps * SIGMA * ((T_s + 273.15) ** 4 - (T_amb + 273.15) ** 4) * (A_face + A_rim)
    return Q_conv + Q_rad


def borosilicate_path_Q(
    T_core: float,
    T_amb: float,
    D_in_mm: float = 68.0,
    D_out_mm: float = 75.0,
    L_glass_mm: float = 126.0,
    D_core_eq_mm: float = 50.93,
    eps_core: float = 0.88,
    eps_glass: float = 0.90,
    orientation: str = "vertical",
) -> tuple[float, float, float]:
    """Heat flow through annular air gap + 3.5 mm borosilicate wall + outer natural conv/rad."""
    if T_core <= T_amb + 0.05:
        return 0.0, T_amb, T_amb
    r_1 = 0.5 * D_core_eq_mm * 1e-3
    r_2 = 0.5 * D_in_mm * 1e-3
    r_3 = 0.5 * D_out_mm * 1e-3
    L = L_glass_mm * 1e-3
    A_1 = 2.0 * math.pi * r_1 * L
    A_2 = 2.0 * math.pi * r_2 * L
    A_3 = 2.0 * math.pi * r_3 * L
    R_wall = math.log(r_3 / r_2) / (2.0 * math.pi * 1.14 * L)
    delta = r_2 - r_1

    def resid(vars_: list[float]) -> list[float]:
        T_gi, T_go = vars_
        dT_gap = max(0.01, T_core - T_gi)
        p = air_props(0.5 * (T_core + T_gi))
        Ra_d = 9.81 * p["beta"] * dT_gap * (delta ** 3) / (p["nu"] * p["alpha"])
        if orientation == "vertical":
            Nu_d = max(1.0, 0.42 * (Ra_d ** 0.25) * (p["Pr"] ** 0.012) * ((L / delta) ** (-0.3)))
        else:
            D_c = 2.0 * r_1
            D_o = 2.0 * r_2
            F_cyl = ((math.log(D_o / D_c)) ** 4) / ((delta ** 3) * (D_c ** (-0.6) + D_o ** (-0.6)) ** 5)
            Ra_c = F_cyl * Ra_d
            k_eff_k = max(1.0, 0.386 * (p["Pr"] / (0.861 + p["Pr"])) ** 0.25 * (Ra_c ** 0.25))
            Nu_d = k_eff_k * delta / (r_1 * math.log(r_2 / r_1))
        h_gap_c = Nu_d * p["k"] / delta
        Q_gap_c = h_gap_c * A_1 * (T_core - T_gi)

        denom = (1.0 / eps_core) + (A_1 / A_2) * (1.0 / eps_glass - 1.0)
        Q_gap_r = SIGMA * A_1 * ((T_core + 273.15) ** 4 - (T_gi + 273.15) ** 4) / denom
        Q_gap = Q_gap_c + Q_gap_r

        Q_wall = (T_gi - T_go) / R_wall
        h_out_c = (
            churchill_chu_vertical_plate_h(T_go, T_amb, L)
            if orientation == "vertical"
            else churchill_chu_horiz_cyl_h(T_go, T_amb, 2.0 * r_3)
        )
        Q_out_c = h_out_c * A_3 * (T_go - T_amb)
        Q_out_r = eps_glass * SIGMA * A_3 * ((T_go + 273.15) ** 4 - (T_amb + 273.15) ** 4)
        Q_out = Q_out_c + Q_out_r
        return [Q_gap - Q_wall, Q_wall - Q_out]

    T_gi, T_go = fsolve(resid, [0.5 * (T_core + T_amb), 0.3 * T_core + 0.7 * T_amb])
    Q_wall = float((T_gi - T_go) / R_wall)
    return Q_wall, float(T_gi), float(T_go)


def compute_bulkhead_resistance(params: LepiLEDParams) -> float:
    """
    First-principles parallel thermal resistance of MECH-CAP-BOT bulkhead (K/W):
      - Plastic bulkhead conduction (k=0.23 W/mK, A_mean ~ 1400 mm^2, t=6.0 mm)
      - Outer cap wall conduction (t_wall ~ 38 mm, A_wall ~ 2800 mm^2)
      - 2x M4 SS DIN 7991 CSK bulkhead bolts (k=15 W/mK, L=11.5 mm, A_s=17.56 mm^2) w/ 1.0 mm nylon CSK finishing/insulating washers (k=0.25, A=35 mm^2 ea)
      - Internal cavity radiation (~114 K/W)
    """
    k_petg = 0.23
    r_bh_plastic = (params.bulkhead_thick * 1e-3) / (k_petg * 1400e-6)  # 18.63 K/W
    r_wall = 0.038 / (k_petg * 2800e-6)                                # 59.01 K/W
    r_bolts = (0.0115 / (15.0 * 17.56e-6)) + (0.001 / (0.25 * 70e-6))  # 100.80 K/W
    r_rad = 114.1
    return 1.0 / (1.0 / r_bh_plastic + 1.0 / r_wall + 1.0 / r_bolts + 1.0 / r_rad)


def compute_top_joint_resistance(params: LepiLEDParams) -> float:
    """
    First-principles top core-to-heatsink interface resistance (K/W):
      - Core-to-adapt_top TIM1 (0.05 mm @ 8.5 W/mK over 444 mm^2 -> 0.013 + 0.055 contact = 0.068 K/W)
      - Radial conduction in 3.0 mm Al 6061 adapt_top from core r_eq=18.5 mm to SK578/50 hub r=12.0 mm (0.138 K/W)
      - Hub-to-heatsink TIM2 (0.078 K/W)
    """
    r_core_tim = 0.068
    r_radial_al = math.log(18.5 / 12.0) / (2.0 * math.pi * 167.0 * (params.adapt_top_thick * 1e-3))
    r_hub_tim = 0.078
    return r_core_tim + r_radial_al + r_hub_tim


def solve_system(
    params: LepiLEDParams,
    Q_uv_tot: float,
    Q_vis_tot: float,
    Q_pcb: float,
    p_u1: float,
    T_amb: float,
    top_hs: HeatsinkSpec,
    bot_hs: HeatsinkSpec,
    pcb_3d: dict[str, float],
    r_diel_uv: float,
    r_diel_vis: float,
    orientation: str = "vertical",
    coupled_core_to_bot: bool = False,
    eps_core: float = 0.88,
    r_tim_led: float = 0.15,
    r_int_top: float | None = None,
    r_bulkhead: float | None = None,
    rth_penalty_factor: float = 1.0,
) -> dict[str, float]:
    """Solve coupled 5-node steady-state thermal network with 2D/3D FVM inputs."""
    if r_int_top is None:
        r_int_top = compute_top_joint_resistance(params)
    if r_bulkhead is None:
        r_bulkhead = compute_bulkhead_resistance(params)

    A_cs = (params.core_w_nom ** 2 - params.core_bore_nom ** 2) * 1e-6  # 444e-6 m^2
    k_al = 200.0
    R_ax_uv_top = (params.axial_uv_to_top_mm * 1e-3) / (k_al * A_cs)
    R_ax_uv_vis = (params.axial_uv_to_vis_mm * 1e-3) / (k_al * A_cs)
    R_ax_vis_bot = (params.axial_vis_to_bot_mm * 1e-3) / (k_al * A_cs)

    R_top_total = R_ax_uv_top + r_int_top
    R_core_bot = (R_ax_vis_bot + 0.25) if coupled_core_to_bot else r_bulkhead
    plastic_pocket = bot_hs.kind == "plastic_pocket"
    r_tim_pcb = 10.0 if plastic_pocket else pcb_3d["R_eff_bot_avg_KW"]

    def Q_top_sink(T_s: float) -> float:
        return radial_heatsink_Q(
            T_s, T_amb, top_hs, orientation=orientation,
            top_exposed=True, bot_exposed=False,
            adapt_plate_od_mm=params.adapt_top_od, adapt_plate_t_mm=params.adapt_top_thick,
            rth_penalty_factor=rth_penalty_factor,
        )[0]

    def Q_bot_sink(T_s: float) -> float:
        if plastic_pocket:
            return max(0.0, T_s - T_amb) / 21.0
        if bot_hs.kind == "flat_disc":
            return flat_disc_Q(T_s, T_amb, bot_hs.D_out_mm, bot_hs.L_mm, orientation=orientation)
        return radial_heatsink_Q(
            T_s, T_amb, bot_hs, orientation=orientation,
            top_exposed=False, bot_exposed=True,
            adapt_plate_od_mm=params.adapt_bot_od, adapt_plate_t_mm=params.adapt_bot_thick,
            rth_penalty_factor=rth_penalty_factor,
        )[0]

    def resid(x: list[float]) -> list[float]:
        T_c_uv, T_c_vis, T_hs_t, T_hs_b, T_pcb_bot = x
        T_c_avg = 0.5 * (T_c_uv + T_c_vis)
        Q_glass, _, _ = borosilicate_path_Q(
            T_c_avg, T_amb,
            D_in_mm=params.glass_id_nom,
            D_out_mm=params.glass_od_nom,
            L_glass_mm=params.exposed_glass_window,
            eps_core=eps_core,
            orientation=orientation,
        )
        Q_uv_to_vis = (T_c_uv - T_c_vis) / R_ax_uv_vis
        Q_uv_to_top = (T_c_uv - T_hs_t) / R_top_total
        Q_vis_to_bot = (T_c_vis - T_hs_b) / R_core_bot
        Q_pcb_to_bot = (T_pcb_bot - T_hs_b) / r_tim_pcb

        eq1 = Q_uv_tot - 0.5 * Q_glass - Q_uv_to_vis - Q_uv_to_top
        eq2 = Q_vis_tot + Q_uv_to_vis - 0.5 * Q_glass - Q_vis_to_bot
        eq3 = Q_uv_to_top - Q_top_sink(T_hs_t)
        eq4 = Q_vis_to_bot + Q_pcb_to_bot - Q_bot_sink(T_hs_b)
        eq5 = Q_pcb - Q_pcb_to_bot
        return [eq1, eq2, eq3, eq4, eq5]

    x0 = [T_amb + 25.0, T_amb + 25.0, T_amb + 20.0, T_amb + 15.0, T_amb + 18.0]
    T_c_uv, T_c_vis, T_hs_t, T_hs_b, T_pcb_bot = [float(v) for v in fsolve(resid, x0)]
    T_c_avg = 0.5 * (T_c_uv + T_c_vis)
    Q_glass, T_gi, T_go = borosilicate_path_Q(
        T_c_avg, T_amb,
        D_in_mm=params.glass_id_nom,
        D_out_mm=params.glass_od_nom,
        L_glass_mm=params.exposed_glass_window,
        eps_core=eps_core,
        orientation=orientation,
    )

    q_uv = Q_uv_tot / 4.0
    T_j_uv = T_c_uv + q_uv * (1.4 + r_diel_uv + 0.10 + r_tim_led)

    if Q_vis_tot == 0.0:
        T_j_vis = T_c_vis
    else:
        q_green = 0.66 * (Q_vis_tot / 2.30) if Q_vis_tot < 3.5 else 1.19 * (Q_vis_tot / 4.93)
        T_j_vis = T_c_vis + q_green * (9.0 + r_diel_vis + 0.10 + r_tim_led)

    if plastic_pocket:
        T_pcb_top_avg = T_pcb_bot + 10.0 * (Q_pcb / 4.39)
        T_u1_top = T_pcb_bot + 40.0 * (p_u1 / 1.29)
        T_q1_top = T_pcb_bot + 45.0 * (Q_pcb / 4.39)
    else:
        T_pcb_top_avg = T_hs_b + pcb_3d["dT_pcb_top_avg_C"]
        T_u1_top = T_hs_b + pcb_3d["dT_U1_top_C"]
        T_q1_top = T_hs_b + pcb_3d["dT_Q1_top_C"]

    # U1 junction: 3D via-coupled (T_U1_F.Cu + P_u1 * R_theta_JC_bot 6.8 C/W) AND conservative JEDEC above T_pcb_bot
    T_j_u1_3d = T_u1_top + p_u1 * 6.8
    T_j_u1_jedec = T_pcb_bot + p_u1 * 53.7
    # Q1A/Q1B DMG2305UX-7 (Tj_max = 150 C, 0.545 W ea DS / ~0.20 W ea Nom)
    p_q1_each = 0.545 if Q_pcb > 3.0 else (0.200 if Q_pcb > 1.0 else 0.060)
    T_j_q1 = T_q1_top + p_q1_each * 25.0

    return dict(
        T_c_uv=T_c_uv,
        T_c_vis=T_c_vis,
        T_hs_t=T_hs_t,
        T_hs_b=T_hs_b,
        T_pcb_bot=T_pcb_bot,
        T_pcb_top_avg=T_pcb_top_avg,
        T_j_uv=T_j_uv,
        T_j_vis=T_j_vis,
        T_j_u1_3d=T_j_u1_3d,
        T_j_u1_jedec=T_j_u1_jedec,
        T_q1_pad=T_q1_top,
        T_j_q1=T_j_q1,
        T_glass_in=T_gi,
        T_glass_out=T_go,
        Q_glass=Q_glass,
        Q_top=Q_top_sink(T_hs_t),
        Q_bot=Q_bot_sink(T_hs_b),
        R_ax_uv_top=R_ax_uv_top,
        R_ax_uv_vis=R_ax_uv_vis,
        R_diel_uv=r_diel_uv,
        R_diel_vis=r_diel_vis,
        R_bulkhead=R_core_bot,
        R_int_top=r_int_top,
        R_eff_bot_pcb=r_tim_pcb,
        margin_uv=100.0 - T_j_uv,
        margin_vis=150.0 - T_j_vis,
        margin_pcb_bot=55.0 - T_pcb_bot,
        margin_pcb_top=55.0 - T_pcb_top_avg,
        margin_u1_3d=125.0 - T_j_u1_3d,
        margin_u1_jedec=125.0 - T_j_u1_jedec,
        margin_q1=150.0 - T_j_q1,
    )


MODES = [
    ("4-UV Nom", "4-UV Nom", 2.96, 0.00, 0.80, 0.404),
    ("8-ALL Nom (typUV)", "8-ALL Nom", 2.53, 2.30, 1.60, 0.404),
    ("8-ALL Nom (40%UV)", "8-ALL Nom", 2.96, 2.30, 1.60, 0.404),
    ("8-ALL DS-RealWPE", "DS-100%", 3.80, 3.05, 4.39, 1.290),
    ("8-ALL DS-100%", "DS-100%", 5.85, 4.93, 4.39, 1.290),
]

CONFIGS = [
    ("Config 0: Sealed Plastic Pocket (SK 578/50 Top only)", SK578_50, PLASTIC_POCKET, False),
    ("Config 1: SK 578/50 Top + Flat 72mm Al Disc Bot (Decoupled)", SK578_50, DISC_72, False),
    ("Config 4: Coupled Dual SK 578/50 SA (Bridged Core)", SK578_50, SK578_50, True),
    ("Config C: Decoupled Dual SK 578/50 SA (R1 Baseline)", SK578_50, SK578_50, False),
    ("Config A: Decoupled SK 578/50 Top + SK LED R 80 SA Bot", SK578_50, SK80_70, False),
]


def main() -> None:
    out_dir = Path(__file__).resolve().parent
    params = LepiLEDParams()

    # 1. Solve genuine 2D MCPCB FVM PDEs
    mcpcb_uv_1oz = solve_mcpcb_2d_r_diel(_uv_mcpcb_polygon(), 1.30, 3.25, dx_mm=0.10, t_cu_um=35.0)
    mcpcb_vis_1oz = solve_mcpcb_2d_r_diel(_vis_mcpcb_polygon(), 1.30, 3.30, dx_mm=0.10, t_cu_um=35.0)
    mcpcb_uv_2oz = solve_mcpcb_2d_r_diel(_uv_mcpcb_polygon(), 1.30, 3.25, dx_mm=0.10, t_cu_um=70.0)
    mcpcb_uv_none = solve_mcpcb_2d_r_diel(None, 1.30, 3.25, dx_mm=0.10, t_cu_um=35.0)

    r_diel_uv = mcpcb_uv_1oz["R_diel_avg_KW"]
    r_diel_vis = mcpcb_vis_1oz["R_diel_avg_KW"]

    # 2. Solve genuine 3D Driver PCB FVM PDEs across all modes + sensitivity variants
    pcb_3d_base = {
        k: solve_driver_pcb_3d(params, mode_scale=k, pad_thick_mm=params.tim_pcb_thick, pad_k=6.2)
        for k in ("4-UV Nom", "8-ALL Nom", "DS-100%")
    }
    pcb_3d_1mm = solve_driver_pcb_3d(params, mode_scale="DS-100%", pad_thick_mm=1.0, pad_k=6.2)
    pcb_3d_3wm = solve_driver_pcb_3d(params, mode_scale="DS-100%", pad_thick_mm=0.5, pad_k=3.0)
    pcb_3d_nom_3wm = solve_driver_pcb_3d(params, mode_scale="8-ALL Nom", pad_thick_mm=0.5, pad_k=3.0)

    r_bh_nom = compute_bulkhead_resistance(params)
    r_top_nom = compute_top_joint_resistance(params)

    rows = []
    for cfg_name, top_hs, bot_hs, coupled in CONFIGS:
        for T_amb in [22.0, 30.0]:
            for orient in ["vertical", "horizontal"]:
                for m_name, m_scale, q_uv, q_vis, q_pcb, p_u1 in MODES:
                    r = solve_system(
                        params, q_uv, q_vis, q_pcb, p_u1, T_amb,
                        top_hs, bot_hs, pcb_3d_base[m_scale],
                        r_diel_uv=r_diel_uv, r_diel_vis=r_diel_vis,
                        orientation=orient, coupled_core_to_bot=coupled,
                        r_int_top=r_top_nom, r_bulkhead=r_bh_nom,
                    )
                    passed = (
                        r["margin_uv"] > 0.0
                        and r["margin_vis"] > 0.0
                        and r["margin_pcb_bot"] >= 0.0
                        and r["margin_pcb_top"] >= 0.0
                        and r["margin_u1_3d"] >= 0.0
                        and r["margin_u1_jedec"] >= 0.0
                        and r["margin_q1"] >= 0.0
                    )
                    rows.append({
                        "config": cfg_name,
                        "T_amb_C": T_amb,
                        "orientation": orient,
                        "mode": m_name,
                        "Q_uv_W": q_uv,
                        "Q_vis_W": q_vis,
                        "Q_pcb_W": q_pcb,
                        "P_u1_W": p_u1,
                        **{k: round(v, 3) for k, v in r.items()},
                        "pass_all_limits": passed,
                    })

    csv_path = out_dir / "thermal_results.csv"
    with csv_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    # Ambient sweep (15..40 C) for Config A (horizontal)
    t_ambs = np.linspace(15.0, 40.0, 26)
    sweep_modes = ["4-UV Nom", "8-ALL Nom (40%UV)", "8-ALL DS-RealWPE", "8-ALL DS-100%"]
    sweep_data: dict[str, list[dict[str, float]]] = {m: [] for m in sweep_modes}
    for m_name, m_scale, q_uv, q_vis, q_pcb, p_u1 in MODES:
        if m_name not in sweep_modes:
            continue
        for Ta in t_ambs:
            r = solve_system(
                params, q_uv, q_vis, q_pcb, p_u1, float(Ta),
                SK578_50, SK80_70, pcb_3d_base[m_scale],
                r_diel_uv=r_diel_uv, r_diel_vis=r_diel_vis,
                orientation="horizontal", coupled_core_to_bot=False,
                r_int_top=r_top_nom, r_bulkhead=r_bh_nom,
            )
            sweep_data[m_name].append({"T_amb": float(Ta), **{k: round(v, 3) for k, v in r.items()}})

    # Adversarial Sensitivity & Robustness Cases (30 C Horizontal unless noted)
    sens_specs = [
        ("Baseline Config A (SK LED R 80 Bot, 0.5mm TG-A6200, eps=0.88)", 30.0, dict(eps_core=0.88, r_tim_led=0.15, rth_penalty_factor=1.0), pcb_3d_base["8-ALL Nom"], pcb_3d_base["DS-100%"]),
        ("1.0 mm TG-A6200 PCB pad (instead of 0.5 mm)", 30.0, dict(eps_core=0.88, r_tim_led=0.15, rth_penalty_factor=1.0), pcb_3d_base["8-ALL Nom"], pcb_3d_1mm),
        ("Cheaper 3.0 W/mK 0.5 mm PCB gap pad", 30.0, dict(eps_core=0.88, r_tim_led=0.15, rth_penalty_factor=1.0), pcb_3d_nom_3wm, pcb_3d_3wm),
        ("Bare mill-finish core (eps=0.34, omitted MECH-COAT-1)", 30.0, dict(eps_core=0.34, r_tim_led=0.15, rth_penalty_factor=1.0), pcb_3d_base["8-ALL Nom"], pcb_3d_base["DS-100%"]),
        ("Thick 0.25 mm TIM-1/2 bondline (R_tim_led=0.50 K/W)", 30.0, dict(eps_core=0.88, r_tim_led=0.50, rth_penalty_factor=1.0), pcb_3d_base["8-ALL Nom"], pcb_3d_base["DS-100%"]),
        ("Worst-case +20% R_th still-air heatsink penalty", 30.0, dict(eps_core=0.88, r_tim_led=0.15, rth_penalty_factor=1.20), pcb_3d_base["8-ALL Nom"], pcb_3d_base["DS-100%"]),
        ("Hot summer ambient T_amb = 35 C (Horizontal)", 35.0, dict(eps_core=0.88, r_tim_led=0.15, rth_penalty_factor=1.0), pcb_3d_base["8-ALL Nom"], pcb_3d_base["DS-100%"]),
    ]
    sensitivity = []
    for desc, ta_s, kw, pcb_nom, pcb_ds in sens_specs:
        rn = solve_system(params, 2.96, 2.30, 1.60, 0.404, ta_s, SK578_50, SK80_70, pcb_nom, r_diel_uv=r_diel_uv, r_diel_vis=r_diel_vis, orientation="horizontal", **kw)
        rd = solve_system(params, 5.85, 4.93, 4.39, 1.290, ta_s, SK578_50, SK80_70, pcb_ds, r_diel_uv=r_diel_uv, r_diel_vis=r_diel_vis, orientation="horizontal", **kw)
        sensitivity.append({
            "case": desc,
            "T_amb_C": ta_s,
            "nom_Tj_uv_C": round(rn["T_j_uv"], 2),
            "nom_T_pcb_bot_C": round(rn["T_pcb_bot"], 2),
            "nom_T_pcb_top_C": round(rn["T_pcb_top_avg"], 2),
            "ds100_Tj_uv_C": round(rd["T_j_uv"], 2),
            "ds100_Tj_vis_C": round(rd["T_j_vis"], 2),
            "ds100_T_pcb_bot_C": round(rd["T_pcb_bot"], 2),
            "ds100_T_pcb_top_C": round(rd["T_pcb_top_avg"], 2),
            "ds100_Tj_u1_3d_C": round(rd["T_j_u1_3d"], 2),
            "ds100_Tj_u1_jedec_C": round(rd["T_j_u1_jedec"], 2),
            "ds100_Tj_q1_C": round(rd["T_j_q1"], 2),
        })

    cfg_a_rows = [r for r in rows if r["config"].startswith("Config A:")]
    cfg_a_pass = all(r["pass_all_limits"] for r in cfg_a_rows)
    summary = {
        "cad_reconciliation": {
            "core_length_mm": params.core_length,
            "exposed_glass_window_mm": params.exposed_glass_window,
            "axial_uv_to_top_mm": params.axial_uv_to_top_mm,
            "axial_uv_to_vis_mm": params.axial_uv_to_vis_mm,
            "axial_vis_to_bot_mm": params.axial_vis_to_bot_mm,
            "bulkhead_thick_mm": params.bulkhead_thick,
            "R_ax_uv_top_KW": round(cfg_a_rows[0]["R_ax_uv_top"], 4),
            "R_ax_uv_vis_KW": round(cfg_a_rows[0]["R_ax_uv_vis"], 4),
            "R_bulkhead_parallel_KW": round(r_bh_nom, 3),
            "R_int_top_spreading_KW": round(r_top_nom, 3),
        },
        "mcpcb_2d_fvm": {
            "uv_1oz_100um": {k: round(v, 3) for k, v in mcpcb_uv_1oz.items()},
            "vis_1oz_100um": {k: round(v, 3) for k, v in mcpcb_vis_1oz.items()},
            "uv_2oz_100um": {k: round(v, 3) for k, v in mcpcb_uv_2oz.items()},
            "uv_bare_pad_no_island": {k: round(v, 3) for k, v in mcpcb_uv_none.items()},
        },
        "driver_pcb_3d_fvm": {
            "DS-100%_0.5mm_TG-A6200": {k: round(v, 3) for k, v in pcb_3d_base["DS-100%"].items()},
            "DS-100%_1.0mm_TG-A6200": {k: round(v, 3) for k, v in pcb_3d_1mm.items()},
            "8-ALL_Nom_0.5mm_TG-A6200": {k: round(v, 3) for k, v in pcb_3d_base["8-ALL Nom"].items()},
            "4-UV_Nom_0.5mm_TG-A6200": {k: round(v, 3) for k, v in pcb_3d_base["4-UV Nom"].items()},
        },
        "config_a_all_pass": cfg_a_pass,
        "config_a_results": cfg_a_rows,
        "config_comparison_30C_horiz": [
            r for r in rows if r["T_amb_C"] == 30.0 and r["orientation"] == "horizontal" and r["mode"] in ("8-ALL Nom (40%UV)", "8-ALL DS-100%")
        ],
        "sensitivity_horiz": sensitivity,
        "ambient_sweep_horiz": sweep_data,
        "caveat_enclosed_trap_box": (
            "All calculations assume stagnant open ambient air (T_amb <= 30 C; T_pcb_bot <= 55 C holds up to ~39 C "
            "even in DS-100%, and T_pcb_top_avg <= 55 C up to ~31 C DS-100% / ~40 C Nom). Inside an unventilated "
            "enclosed moth-trap funnel box where trapped air exceeds 31 C under sustained DS-100% droop, add trap ventilation."
        ),
    }
    json_path = out_dir / "thermal_summary.json"
    json_path.write_text(json.dumps(summary, indent=2))

    print(f"2D FVM MCPCB: UV R_diel={r_diel_uv:.3f} K/W (max {mcpcb_uv_1oz['R_diel_max_KW']:.3f}), VIS R_diel={r_diel_vis:.3f} K/W")
    print(f"3D FVM PCB (DS-100%, 0.5mm TG-A6200, A_pad={pcb_3d_base['DS-100%']['A_pad_cm2']} cm2): "
          f"R_eff_bot={pcb_3d_base['DS-100%']['R_eff_bot_avg_KW']:.3f} K/W, dT_bot={pcb_3d_base['DS-100%']['dT_pcb_bot_avg_C']:.2f}C, "
          f"dT_top={pcb_3d_base['DS-100%']['dT_pcb_top_avg_C']:.2f}C, dT_U1_top={pcb_3d_base['DS-100%']['dT_U1_top_C']:.2f}C")
    print(f"First-principles R_bulkhead={r_bh_nom:.2f} K/W, R_int_top={r_top_nom:.3f} K/W")
    print("=== Config A (Decoupled SK 578/50 Top + SK LED R 80 SA Bot) ===")
    for r in cfg_a_rows:
        print(
            f"  Tamb={r['T_amb_C']:2.0f}C {r['orientation']:10s} | {r['mode']:18s} | "
            f"TjUV={r['T_j_uv']:5.1f}C TjVis={r['T_j_vis']:5.1f}C "
            f"TpcbB={r['T_pcb_bot']:5.1f}C TpcbT={r['T_pcb_top_avg']:5.1f}C "
            f"Tu1_3D={r['T_j_u1_3d']:5.1f}C Tu1_J={r['T_j_u1_jedec']:5.1f}C | PASS={r['pass_all_limits']}"
        )
    print(f"Config A all pass: {cfg_a_pass}")

    # Plot 1: thermal_margins.png
    fig, axes = plt.subplots(1, 3, figsize=(14.5, 4.8), dpi=150)
    sel_modes = ["4-UV Nom", "8-ALL Nom (40%UV)", "8-ALL DS-RealWPE", "8-ALL DS-100%"]
    x = np.arange(len(sel_modes))
    w = 0.25

    def get_vals(metric: str, ta: float, orient: str) -> list[float]:
        return [
            next(r[metric] for r in cfg_a_rows if r["mode"] == m and r["T_amb_C"] == ta and r["orientation"] == orient)
            for m in sel_modes
        ]

    ax = axes[0]
    ax.bar(x - w, get_vals("T_j_uv", 22.0, "vertical"), w, label="22°C Vert", color="#4c72b0")
    ax.bar(x, get_vals("T_j_uv", 30.0, "vertical"), w, label="30°C Vert", color="#dd8452")
    ax.bar(x + w, get_vals("T_j_uv", 30.0, "horizontal"), w, label="30°C Horiz", color="#c44e52")
    ax.axhline(100.0, color="red", ls="--", lw=1.5, label="Limit 100°C")
    ax.axhline(80.0, color="gray", ls=":", lw=1.2, label="Nom Target 80°C")
    ax.set_title("UV LED Junction $T_{j,\\mathrm{UV}}$ (2D FVM)")
    ax.set_ylabel("Temperature (°C)")
    ax.set_xticks(x, ["4-UV\nNom", "8-ALL\nNom", "8-ALL\nDS-Real", "8-ALL\nDS-100%"], fontsize=8.5)
    ax.set_ylim(0, 115)
    ax.grid(axis="y", alpha=0.3)
    ax.legend(fontsize=7.5, loc="upper left")

    ax = axes[1]
    ax.bar(x - w, get_vals("T_j_vis", 22.0, "vertical"), w, label="22°C Vert", color="#4c72b0")
    ax.bar(x, get_vals("T_j_vis", 30.0, "vertical"), w, label="30°C Vert", color="#dd8452")
    ax.bar(x + w, get_vals("T_j_vis", 30.0, "horizontal"), w, label="30°C Horiz", color="#c44e52")
    ax.axhline(150.0, color="red", ls="--", lw=1.5, label="Limit 150°C")
    ax.axhline(85.0, color="gray", ls=":", lw=1.2, label="Nom Target 85°C")
    ax.set_title("Visible Green LED $T_{j,\\mathrm{Vis}}$ (2D FVM)")
    ax.set_xticks(x, ["4-UV\nNom", "8-ALL\nNom", "8-ALL\nDS-Real", "8-ALL\nDS-100%"], fontsize=8.5)
    ax.set_ylim(0, 165)
    ax.grid(axis="y", alpha=0.3)
    ax.legend(fontsize=7.5, loc="upper left")

    ax = axes[2]
    ax.bar(x - w, get_vals("T_pcb_bot", 22.0, "vertical"), w, label="22°C Vert (B.Cu)", color="#4c72b0")
    ax.bar(x, get_vals("T_pcb_top_avg", 30.0, "vertical"), w, label="30°C Vert (F.Cu avg)", color="#dd8452")
    ax.bar(x + w, get_vals("T_pcb_top_avg", 30.0, "horizontal"), w, label="30°C Horiz (F.Cu avg)", color="#c44e52")
    ax.axhline(55.0, color="red", ls="--", lw=1.5, label="PCB Limit 55°C")
    ax.set_title("Driver PCB $T_{\\mathrm{PCB,top\\_avg}}$ & $T_{\\mathrm{PCB,bot}}$ (3D)")
    ax.set_xticks(x, ["4-UV\nNom", "8-ALL\nNom", "8-ALL\nDS-Real", "8-ALL\nDS-100%"], fontsize=8.5)
    ax.set_ylim(0, 70)
    ax.grid(axis="y", alpha=0.3)
    ax.legend(fontsize=7.0, loc="upper left")

    fig.suptitle("Config A (SK 578/50 Top + SK LED R 80 SA Bot) — 2D/3D FVM Steady-State Margins", fontweight="bold")
    fig.tight_layout()
    fig.savefig(out_dir / "thermal_margins.png")
    plt.close(fig)

    # Plot 2: thermal_ambient_sweep.png
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.0, 4.8), dpi=150)
    colors = {
        "4-UV Nom": "#2ca02c",
        "8-ALL Nom (40%UV)": "#1f77b4",
        "8-ALL DS-RealWPE": "#ff7f0e",
        "8-ALL DS-100%": "#d62728",
    }
    for m in sweep_modes:
        pts = sweep_data[m]
        ta = [p["T_amb"] for p in pts]
        ax1.plot(ta, [p["T_j_uv"] for p in pts], lw=2.0, color=colors[m], label=m)
        ax2.plot(ta, [p["T_pcb_bot"] for p in pts], lw=2.0, color=colors[m], label=f"{m} (B.Cu)")
        ax2.plot(ta, [p["T_pcb_top_avg"] for p in pts], lw=1.4, ls="--", color=colors[m], label=f"{m} (F.Cu)")
    ax1.axhline(100.0, color="red", ls="--", lw=1.4, label="UV Limit 100°C")
    ax1.axvline(30.0, color="gray", ls=":", lw=1.2, label="Design Tamb 30°C")
    ax1.set_title("UV LED $T_{j,\\mathrm{UV}}$ vs Ambient (Horizontal)")
    ax1.set_xlabel("Ambient Temperature $T_{\\mathrm{amb}}$ (°C)")
    ax1.set_ylabel("Temperature (°C)")
    ax1.grid(alpha=0.3)
    ax1.legend(fontsize=8)

    ax2.axhline(55.0, color="red", ls="--", lw=1.4, label="PCB Limit 55°C")
    ax2.axvline(30.0, color="gray", ls=":", lw=1.2, label="Design Tamb 30°C")
    ax2.set_title("Driver PCB $T_{\\mathrm{PCB,bot}}$ & $T_{\\mathrm{PCB,top}}$ vs Ambient (Horiz)")
    ax2.set_xlabel("Ambient Temperature $T_{\\mathrm{amb}}$ (°C)")
    ax2.set_ylabel("Temperature (°C)")
    ax2.grid(alpha=0.3)
    ax2.legend(fontsize=6.5, ncol=2)

    fig.suptitle("Ambient Temperature Sweep (15–40°C, Stagnant Horizontal Air, 2D/3D FVM)", fontweight="bold")
    fig.tight_layout()
    fig.savefig(out_dir / "thermal_ambient_sweep.png")
    plt.close(fig)

    # Plot 3: thermal_network_comparison.png
    fig, ax = plt.subplots(figsize=(11.0, 4.8), dpi=150)
    cfg_labels = [
        "Config 0:\nSealed Plastic\nPocket",
        "Config 1:\nFlat 72mm\nAl Disc Bot",
        "Config 4:\nCoupled Dual\nSK 578/50",
        "Config C:\nDecoupled Dual\nSK 578/50 (R1)",
        "Config A:\nDecoupled\nSK LED R 80 Bot",
    ]
    cfg_prefixes = ["Config 0:", "Config 1:", "Config 4:", "Config C:", "Config A:"]
    pcb_nom = [
        next(r["T_pcb_top_avg"] for r in rows if r["config"].startswith(p) and r["T_amb_C"] == 30.0 and r["orientation"] == "horizontal" and r["mode"] == "8-ALL Nom (40%UV)")
        for p in cfg_prefixes
    ]
    pcb_ds = [
        next(r["T_pcb_top_avg"] for r in rows if r["config"].startswith(p) and r["T_amb_C"] == 30.0 and r["orientation"] == "horizontal" and r["mode"] == "8-ALL DS-100%")
        for p in cfg_prefixes
    ]
    x_c = np.arange(len(cfg_labels))
    ax.bar(x_c - 0.18, pcb_nom, 0.36, label="8-ALL Nom (1.60 W PCB, F.Cu avg)", color="#4c72b0")
    ax.bar(x_c + 0.18, pcb_ds, 0.36, label="8-ALL DS-100% (4.39 W PCB, F.Cu avg)", color="#dd8452")
    ax.axhline(55.0, color="red", ls="--", lw=1.6, label="PCB Limit 55°C")
    for i, (vn, vd) in enumerate(zip(pcb_nom, pcb_ds)):
        ax.text(i - 0.18, vn + 2.0, f"{vn:.1f}°C", ha="center", fontsize=8.5, fontweight="bold")
        ax.text(i + 0.18, vd + 2.0, f"{vd:.1f}°C", ha="center", fontsize=8.5, fontweight="bold")
    ax.set_xticks(x_c, cfg_labels, fontsize=9)
    ax.set_ylabel("Driver PCB $T_{\\mathrm{PCB,top\\_avg}}$ (°C)")
    ax.set_ylim(0, 175)
    ax.set_title("Driver PCB Cooling Architecture Comparison ($T_{\\mathrm{amb}}=30^\\circ\\mathrm{C}$, Horizontal, 3D FVM)")
    ax.grid(axis="y", alpha=0.3)
    ax.legend(fontsize=8.5)
    fig.tight_layout()
    fig.savefig(out_dir / "thermal_network_comparison.png")
    plt.close(fig)

    print(f"Saved: {csv_path}, {json_path}, and 3 PNG plots in {out_dir}")


if __name__ == "__main__":
    main()
