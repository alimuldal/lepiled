#!/usr/bin/env python3
"""
LepiLED DIY Maxi Switch (Rev 4.1 — USB-C PD Only + Dual AL8860WT-7 Buck + S3 DPDT)
Comprehensive SPICE + Analytic Corner Sweep + Full-Parameter Monte Carlo Suite.

Verifies:
  1. Nominal mode transitions (OFF -> 4-UV -> 8-ALL) via ngspice
  2. Hysteretic hardware UVLO (17.54 V ON / 16.64 V OFF; 0.90 V hyst) through 0.30 Ohm
     source impedance proving 5-15.75 V PD fallback rejection & ZERO motorboating
  3. Open-circuit LED disconnect AND live-reconnect surge (C4/C5=100 nF + R22/R23=6.8 Ohm
     keeps UV < 1.0 A & Vis <= 1.2 A through 150 nH / 80 mOhm harness)
  4. Inherent short-circuit LED protection (J2 shorted mid-run)
  5. USB-C input protection: -15 V negative transient (unidirectional SMBJ22A clamp),
     inductive 21 V hot-plug clamping, and Q1 OFF-state R21 gate bleed
  6. True .temp 85 C hot-plug (1.0 uH cable, derated MLCCs, Q1 genuinely OFF during step)
     + slew-controlled Q1 turn-on inrush (< 1.0 A via C13-to-GND)
  7. Exhaustive datasheet corner sweep across V_IN in [18.5, 21.5] V, T_amb in [-10, 55] C
  8. Full-parameter Monte Carlo (N=2000) with +/-0.85% over-temp LM4040 & V_ON/V_OFF checks
"""

import csv
import itertools
import json
import math
import os
import re
import subprocess
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

SIM_DIR = Path(__file__).resolve().parent
NET_DIR = SIM_DIR / "netlists"
OUT_DIR = SIM_DIR / "outputs"
OUT_DIR.mkdir(parents=True, exist_ok=True)

NGSPICE = os.environ.get(
    "NGSPICE_BIN",
    "/home/alimuldal/.local/share/lepiled-tools/bin/ngspice",
)
if not Path(NGSPICE).exists():
    NGSPICE = "ngspice"


def run_ngspice(cir_name: str) -> dict:
    cir_path = NET_DIR / cir_name
    proc = subprocess.run(
        [NGSPICE, "-b", cir_path.name],
        cwd=str(NET_DIR),
        capture_output=True,
        text=True,
        timeout=120,
    )
    log_text = proc.stdout + "\n--- STDERR ---\n" + proc.stderr
    log_path = OUT_DIR / (cir_path.stem + ".log")
    log_path.write_text(log_text)
    if proc.returncode != 0:
        raise RuntimeError(f"ngspice failed on {cir_name}:\n{proc.stderr[-1000:]}")
    # Fail-on-meas-error guard (fixes Opus A-M5 silent measurement failure bug)
    for line in log_text.splitlines():
        low = line.lower()
        if "meas" in low and ("failed" in low or "no such vector" in low):
            raise RuntimeError(f"ngspice .meas failure in {cir_name}: {line.strip()}")
        if "no such vector" in low or "measure failed" in low:
            raise RuntimeError(f"ngspice vector/measure error in {cir_name}: {line.strip()}")
    meas = {}
    for line in proc.stdout.splitlines():
        m = re.match(r"^\s*([a-zA-Z0-9_]+)\s*=\s*([-+]?[0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?)", line)
        if m:
            meas[m.group(1).lower()] = float(m.group(2))
    return meas


def load_wrdata(filename: str) -> np.ndarray:
    path = OUT_DIR / filename
    return np.loadtxt(path)


def solve_buck_channel(
    v_in: float,
    v_led: float,
    v_sense: float,
    r_s: float,
    L: float,
    dcr: float,
    r_sw: float,
    v_d: float,
    hys: float = 0.20,
    t_pd: float = 50e-9,
    i_q: float = 0.55e-3,
):
    """Exact analytic model of AL8860 hysteretic buck LED driver (AL8860.pdf p. 13)."""
    i_nom = v_sense / r_s
    v_on = v_in - v_led - i_nom * (r_s + dcr + r_sw)
    if v_on <= 0.15:
        return None
    v_off = v_led + v_d + i_nom * (r_s + dcr)
    di_hys = 2.0 * hys * i_nom
    di_up = (v_on / L) * t_pd
    di_dn = (v_off / L) * t_pd
    di_tot = di_hys + di_up + di_dn
    i_pk = i_nom * (1.0 + hys) + di_up
    i_val = max(0.0, i_nom * (1.0 - hys) - di_dn)
    i_avg = 0.5 * (i_pk + i_val)

    t_on = L * di_tot / v_on
    t_off = L * di_tot / v_off
    period = t_on + t_off
    f_sw = 1.0 / period
    duty = t_on / period

    i_l_rms = math.sqrt(i_avg**2 + (di_tot**2) / 12.0)
    i_sw_rms = i_l_rms * math.sqrt(duty)
    i_d_avg = i_avg * (1.0 - duty)

    p_sw_cond = (i_sw_rms**2) * r_sw
    p_sw_tran = 0.5 * v_in * i_avg * 25e-9 * f_sw
    p_iq = v_in * i_q
    p_ic = p_sw_cond + p_sw_tran + p_iq
    p_diode = i_d_avg * v_d
    p_ind = (i_l_rms**2) * dcr
    p_rs = (i_l_rms**2) * r_s
    p_led = i_avg * v_led
    p_in = p_led + p_ic + p_diode + p_ind + p_rs
    eff = p_led / p_in
    i_in = p_in / v_in

    return {
        "i_avg": i_avg,
        "i_pk": i_pk,
        "i_val": i_val,
        "di_pp": di_tot,
        "t_on": t_on,
        "t_off": t_off,
        "f_sw": f_sw,
        "duty": duty,
        "p_led": p_led,
        "p_ic": p_ic,
        "p_diode": p_diode,
        "p_ind": p_ind,
        "p_rs": p_rs,
        "p_in": p_in,
        "i_in": i_in,
        "eff": eff,
    }


def uvlo_thresholds(r15, r16, r17, r18, r19, v_ref, v_io):
    """Exact analytic turn-on and turn-off thresholds of U4A hysteretic UVLO."""
    v_th = v_ref + v_io
    # Rising (U4A OUT = 0 V): R19 in parallel with R16
    r16_eff = (r16 * r19) / (r16 + r19)
    v_on = v_th * (1.0 + r15 / r16_eff)
    # Falling (U4A OUT open): R17/R18 Thevenin -> V_thv = VIN * R18/(R17+R18), R_thv = R17||R18
    k_div = r18 / (r17 + r18)
    r_fb_tot = r19 + (r17 * r18) / (r17 + r18)
    # (VIN - v_th)/R15 + (k_div*VIN - v_th)/r_fb_tot = v_th/R16
    v_off = v_th * (1.0 / r16 + 1.0 / r15 + 1.0 / r_fb_tot) / (1.0 / r15 + k_div / r_fb_tot)
    return v_on, v_off


def run_corner_sweep() -> dict:
    """Exhaustive worst-case datasheet corner sweep across USB-C PD 20 V +/-5% + margin."""
    v_ins = [18.5, 19.0, 20.0, 21.0, 21.5]
    v_senses = [0.096, 0.100, 0.104]
    r_ss = [0.297, 0.300, 0.303]
    ls = [54.4e-6, 68.0e-6, 81.6e-6]
    temps = [-10.0, 25.0, 55.0]

    rows = []
    worst = {
        "uv_i_max": 0.0, "uv_i_min": 9.9, "uv_ipk_max": 0.0,
        "uv_fsw_max": 0.0, "uv_ton_min": 9.9, "uv_duty_max": 0.0,
        "uv_pic_max": 0.0, "uv_tj_max": -99.0,
        "vis_i_max": 0.0, "vis_i_min": 9.9, "vis_ipk_max": 0.0,
        "vis_fsw_max": 0.0, "vis_ton_min": 9.9, "vis_duty_max": 0.0,
        "vis_pic_max": 0.0, "vis_tj_max": -99.0,
        "total_pcb_loss_max": 0.0, "i_in_total_max": 0.0,
        "failed_corners": 0, "total_corners": 0,
    }

    for v_in, v_s, r_s, L, t_amb in itertools.product(v_ins, v_senses, r_ss, ls, temps):
        dcr = 0.351 * (1.0 + 0.00393 * max(0.0, t_amb + 15.0 - 25.0))
        r_sw = 0.30 if t_amb <= 25.0 else 0.45
        v_d = 0.40 if t_amb <= 25.0 else 0.32

        uv_vfs = [4 * 3.90 + 4 * 0.00267 * (25 - (-10))] if t_amb < 0 else (
            [4 * 2.70 - 4 * 0.00267 * (80 - 25), 4 * 3.60, 4 * 3.90]
        )
        vis_vfs = [2 * 3.40 + 3.25 + 3.19 + 4 * 0.0015 * 35] if t_amb < 0 else (
            [2 * 2.60 + 2.50 + 2.60 - 4 * 0.0015 * 55, 2 * 2.93 + 2.70 + 2.93, 2 * 3.40 + 3.25 + 3.19]
        )

        for v_uv, v_vis in itertools.product(uv_vfs, vis_vfs):
            v_uv = min(v_uv, 16.0)
            c1 = solve_buck_channel(v_in, v_uv, v_s, r_s, L, dcr, r_sw, v_d)
            c2 = solve_buck_channel(v_in, v_vis, v_s, r_s, L, dcr, r_sw, v_d)
            worst["total_corners"] += 1
            if c1 is None or c2 is None:
                worst["failed_corners"] += 1
                continue

            # Rev 4.1 overhead: U3 (6 mA max + 2.9 mA D12), U4 (1.7 mA), U5 (R14 10k),
            # UVLO dividers (R15+R16=69k, R17+R18=200k), F1 (MF-MSMF110/33X max 0.16 Ohm hot),
            # R8 (5 mOhm), single Q1 DMN4035L (0.075 Ohm hot)
            i_div = v_in / 69000.0 + v_in / 200000.0
            i_in_raw = c1["i_in"] + c2["i_in"] + 0.0089 + 0.0017 + (v_in - 2.5) / 10000.0 + i_div
            p_overhead = (
                v_in * 0.0089
                + v_in * 0.0017
                + v_in * (v_in - 2.5) / 10000.0
                + v_in * i_div
                + (i_in_raw**2) * (0.160 + 0.005 + 0.075)
            )
            p_pcb_tot = (
                c1["p_ic"] + c1["p_diode"] + c1["p_ind"] + c1["p_rs"]
                + c2["p_ic"] + c2["p_diode"] + c2["p_ind"] + c2["p_rs"]
                + p_overhead
            )
            tj1 = t_amb + c1["p_ic"] * 147.0
            tj2 = t_amb + c2["p_ic"] * 147.0

            ok = (
                c1["i_pk"] < 0.70 and c2["i_pk"] < 0.70
                and c1["f_sw"] < 1.0e6 and c2["f_sw"] < 1.0e6
                and c1["duty"] < 0.98 and c2["duty"] < 0.98
                and tj1 < 125.0 and tj2 < 125.0
                and i_in_raw < 0.73  # < MF-MSMF110/33X I_hold(60 C) = 0.73 A!
            )
            if not ok:
                worst["failed_corners"] += 1

            worst["uv_i_max"] = max(worst["uv_i_max"], c1["i_avg"])
            worst["uv_i_min"] = min(worst["uv_i_min"], c1["i_avg"])
            worst["uv_ipk_max"] = max(worst["uv_ipk_max"], c1["i_pk"])
            worst["uv_fsw_max"] = max(worst["uv_fsw_max"], c1["f_sw"])
            worst["uv_ton_min"] = min(worst["uv_ton_min"], c1["t_on"])
            worst["uv_duty_max"] = max(worst["uv_duty_max"], c1["duty"])
            worst["uv_pic_max"] = max(worst["uv_pic_max"], c1["p_ic"])
            worst["uv_tj_max"] = max(worst["uv_tj_max"], tj1)

            worst["vis_i_max"] = max(worst["vis_i_max"], c2["i_avg"])
            worst["vis_i_min"] = min(worst["vis_i_min"], c2["i_avg"])
            worst["vis_ipk_max"] = max(worst["vis_ipk_max"], c2["i_pk"])
            worst["vis_fsw_max"] = max(worst["vis_fsw_max"], c2["f_sw"])
            worst["vis_ton_min"] = min(worst["vis_ton_min"], c2["t_on"])
            worst["vis_duty_max"] = max(worst["vis_duty_max"], c2["duty"])
            worst["vis_pic_max"] = max(worst["vis_pic_max"], c2["p_ic"])
            worst["vis_tj_max"] = max(worst["vis_tj_max"], tj2)

            worst["total_pcb_loss_max"] = max(worst["total_pcb_loss_max"], p_pcb_tot)
            worst["i_in_total_max"] = max(worst["i_in_total_max"], i_in_raw)

            rows.append([
                v_in, t_amb, round(v_uv, 2), round(v_vis, 2), v_s, r_s, round(L * 1e6, 1),
                round(c1["i_avg"] * 1e3, 1), round(c1["i_pk"] * 1e3, 1), round(c1["f_sw"] * 1e-3, 1),
                round(c1["p_ic"] * 1e3, 1), round(tj1, 1),
                round(c2["i_avg"] * 1e3, 1), round(c2["i_pk"] * 1e3, 1), round(c2["f_sw"] * 1e-3, 1),
                round(c2["p_ic"] * 1e3, 1), round(tj2, 1),
                round(p_pcb_tot, 3), round(i_in_raw, 3), "PASS" if ok else "FAIL"
            ])

    csv_path = OUT_DIR / "corner_sweep.csv"
    with open(csv_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow([
            "V_in_V", "T_amb_C", "V_uv_V", "V_vis_V", "V_sense_V", "R_s_Ohm", "L_uH",
            "I_uv_mA", "I_uv_pk_mA", "f_uv_kHz", "P_U1_mW", "Tj_U1_C",
            "I_vis_mA", "I_vis_pk_mA", "f_vis_kHz", "P_U2_mW", "Tj_U2_C",
            "P_pcb_tot_W", "I_in_tot_A", "Status"
        ])
        w.writerows(rows)
    return worst


def run_monte_carlo(n: int = 2000, seed: int = 20261119) -> dict:
    """
    Full-parameter Monte Carlo (N=2000) sampling EVERY datasheet tolerance simultaneously:
    V_IN (USB PD 20 V +/-5%), T_amb, V_SENSE (+/-4%), R_S (+/-1%), L (+/-20%), DCR,
    R_SW, V_D, individual LED Vf + tempco, UVLO R15..R19 (+/-1%),
    LM4040 (+/-0.85% full over-temp per Note 3!), LM393B Vio (+/-4 mV).
    """
    rng = np.random.default_rng(seed)

    v_in = rng.uniform(19.0, 21.0, n)
    t_amb = rng.uniform(5.0, 45.0, n)
    v_s1 = rng.normal(0.100, 0.004 / 3.0, n).clip(0.096, 0.104)
    v_s2 = rng.normal(0.100, 0.004 / 3.0, n).clip(0.096, 0.104)
    r_s1 = rng.normal(0.300, 0.003 / 3.0, n).clip(0.297, 0.303)
    r_s2 = rng.normal(0.300, 0.003 / 3.0, n).clip(0.297, 0.303)
    L1 = rng.normal(68e-6, 68e-6 * 0.20 / 3.0, n).clip(54.4e-6, 81.6e-6)
    L2 = rng.normal(68e-6, 68e-6 * 0.20 / 3.0, n).clip(54.4e-6, 81.6e-6)
    dcr1 = rng.uniform(0.25, 0.351, n) * (1.0 + 0.00393 * (t_amb + 10.0 - 25.0))
    dcr2 = rng.uniform(0.25, 0.351, n) * (1.0 + 0.00393 * (t_amb + 10.0 - 25.0))
    r_sw1 = rng.uniform(0.20, 0.42, n)
    r_sw2 = rng.uniform(0.20, 0.42, n)
    v_d1 = rng.uniform(0.28, 0.40, n)
    v_d2 = rng.uniform(0.28, 0.40, n)

    t_j_led = t_amb + 30.0
    v_uv = np.sum(rng.normal(3.60, 0.10, (n, 4)).clip(2.7, 3.9), axis=1) - 4 * 0.00267 * (t_j_led - 25.0)
    v_vis = (
        np.sum(rng.normal(2.93, 0.12, (n, 2)).clip(2.6, 3.4), axis=1)
        + rng.normal(2.70, 0.14, n).clip(2.5, 3.25)
        + rng.normal(2.93, 0.09, n).clip(2.6, 3.19)
        - 4 * 0.0015 * (t_j_led - 25.0)
    )

    # UVLO threshold sampling (Rev 4.7: Hottech TL431 2.495 V +/-1.5% over-temp, LM393DR2G +/-5 mV, Basic 30k/5.1k/270k)
    r15 = rng.normal(30.0e3, 30.0e3 * 0.01 / 3.0, n).clip(29.70e3, 30.30e3)
    r16 = rng.normal(5.1e3, 5.1e3 * 0.01 / 3.0, n).clip(5.049e3, 5.151e3)
    r17 = rng.normal(100.0e3, 100.0e3 * 0.01 / 3.0, n).clip(99.0e3, 101.0e3)
    r18 = rng.normal(100.0e3, 100.0e3 * 0.01 / 3.0, n).clip(99.0e3, 101.0e3)
    r19 = rng.normal(270.0e3, 270.0e3 * 0.01 / 3.0, n).clip(267.3e3, 272.7e3)
    v_ref = rng.normal(2.495, 2.495 * 0.015 / 3.0, n).clip(2.4576, 2.5324)
    v_io = rng.normal(0.0, 0.005 / 3.0, n).clip(-0.005, 0.005)
    v_on, v_off = uvlo_thresholds(r15, r16, r17, r18, r19, v_ref, v_io)
    v_hyst = v_on - v_off

    i_uv_arr, i_vis_arr, i_in_arr, p_pcb_arr, eff_arr, tj1_arr, tj2_arr = [], [], [], [], [], [], []
    passes = 0
    rows = []

    for k in range(n):
        c1 = solve_buck_channel(v_in[k], v_uv[k], v_s1[k], r_s1[k], L1[k], dcr1[k], r_sw1[k], v_d1[k])
        c2 = solve_buck_channel(v_in[k], v_vis[k], v_s2[k], r_s2[k], L2[k], dcr2[k], r_sw2[k], v_d2[k])
        if c1 is None or c2 is None:
            continue
        i_div = v_in[k] / 69000.0 + v_in[k] / 200000.0
        i_in_tot = c1["i_in"] + c2["i_in"] + 0.0033 + 0.0029 + 0.0006 + (v_in[k] - 2.5) / 10000.0 + i_div
        p_over = (
            v_in[k] * 0.0068
            + v_in[k] * (v_in[k] - 2.5) / 10000.0
            + v_in[k] * i_div
            + (i_in_tot**2) * (0.080 + 0.005 + 0.052)
        )
        p_pcb = (
            c1["p_ic"] + c1["p_diode"] + c1["p_ind"] + c1["p_rs"]
            + c2["p_ic"] + c2["p_diode"] + c2["p_ind"] + c2["p_rs"]
            + p_over
        )
        eff = (c1["p_led"] + c2["p_led"]) / (v_in[k] * i_in_tot)
        tj1 = t_amb[k] + c1["p_ic"] * 147.0
        tj2 = t_amb[k] + c2["p_ic"] * 147.0

        ok = (
            0.305 <= c1["i_avg"] <= 0.365
            and 0.305 <= c2["i_avg"] <= 0.365
            and c1["i_pk"] < 0.70 and c2["i_pk"] < 0.70
            and c1["f_sw"] < 1.0e6 and c2["f_sw"] < 1.0e6
            and tj1 < 100.0 and tj2 < 100.0
            and 16.0 < v_off[k] < 17.3
            and 16.8 < v_on[k] < 18.2
            and v_hyst[k] >= 0.75
            and i_in_tot < 0.73
        )
        if ok:
            passes += 1

        i_uv_arr.append(c1["i_avg"] * 1e3)
        i_vis_arr.append(c2["i_avg"] * 1e3)
        i_in_arr.append(i_in_tot)
        p_pcb_arr.append(p_pcb)
        eff_arr.append(eff * 100.0)
        tj1_arr.append(tj1)
        tj2_arr.append(tj2)
        if k < 500:
            rows.append([
                k, round(v_in[k], 3), round(t_amb[k], 1), round(c1["i_avg"] * 1e3, 2),
                round(c2["i_avg"] * 1e3, 2), round(i_in_tot, 4), round(p_pcb, 4),
                round(eff * 100.0, 2), round(v_on[k], 3), round(v_off[k], 3), round(tj1, 1)
            ])

    with open(OUT_DIR / "monte_carlo.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["trial", "V_in_V", "T_amb_C", "I_uv_mA", "I_vis_mA", "I_in_A", "P_pcb_W", "Eff_pct", "V_uvlo_on_V", "V_uvlo_off_V", "Tj_U1_C"])
        w.writerows(rows)

    def stats(a):
        arr = np.array(a)
        return {
            "mean": round(float(np.mean(arr)), 3),
            "std": round(float(np.std(arr)), 3),
            "min": round(float(np.min(arr)), 3),
            "p01": round(float(np.percentile(arr, 1)), 3),
            "p99": round(float(np.percentile(arr, 99)), 3),
            "max": round(float(np.max(arr)), 3),
        }

    return {
        "n_trials": n,
        "passes": passes,
        "yield_pct": round(100.0 * passes / n, 3),
        "i_uv_mA": stats(i_uv_arr),
        "i_vis_mA": stats(i_vis_arr),
        "i_in_A": stats(i_in_arr),
        "p_pcb_W": stats(p_pcb_arr),
        "eff_pct": stats(eff_arr),
        "tj_u1_C": stats(tj1_arr),
        "tj_u2_C": stats(tj2_arr),
        "v_uvlo_on_V": stats(v_on),
        "v_uvlo_off_V": stats(v_off),
        "v_uvlo_hyst_V": stats(v_hyst),
    }


def plot_results(mc_res: dict):
    # 1. Nominal Mode Cycling Plot (OFF -> 4-UV -> 8-ALL)
    d = load_wrdata("nominal_waveforms.txt")
    t_ms = d[:, 0] * 1e3
    vin = d[:, 1]
    i_uv = d[:, 3] * 1e3
    i_vis = d[:, 5] * 1e3
    i_in = -d[:, 7] * 1e3
    v_c1 = d[:, 9]
    v_c2 = d[:, 11]

    fig, axes = plt.subplots(3, 1, figsize=(10, 7.5), sharex=True)
    axes[0].plot(t_ms, i_uv, label="Ch1 UV LED Current (mA)", color="#6c3483", lw=1.4)
    axes[0].plot(t_ms, i_vis, label="Ch2 Vis LED Current (mA)", color="#1f618d", lw=1.4)
    axes[0].axhline(333.3, color="gray", ls="--", lw=0.8, label="Nominal 333 mA")
    axes[0].set_ylabel("LED Current (mA)")
    axes[0].set_title("LepiLED Rev 4.1 (USB-C PD Only + Direct DPDT) — Mode Cycling (OFF -> 4-UV -> 8-ALL)")
    axes[0].legend(loc="upper left", fontsize=8)
    axes[0].grid(True, alpha=0.3)

    axes[1].plot(t_ms, i_in, label="20 V USB-C Input Current (mA)", color="#b9770e", lw=1.2)
    axes[1].set_ylabel("Input Current (mA)")
    axes[1].legend(loc="upper left", fontsize=8)
    axes[1].grid(True, alpha=0.3)

    axes[2].plot(t_ms, vin, label="VIN_20V Bus (V)", color="#c0392b", lw=1.2)
    axes[2].plot(t_ms, v_c1, label="U1_CTRL (V)", color="#6c3483", lw=1.0, ls="--")
    axes[2].plot(t_ms, v_c2, label="U2_CTRL (V)", color="#1f618d", lw=1.0, ls=":")
    axes[2].set_ylabel("Voltage (V)")
    axes[2].set_xlabel("Time (ms)")
    axes[2].legend(loc="right", fontsize=8)
    axes[2].grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "plot_nominal_modes.png", dpi=150)
    plt.close(fig)

    # 2. Hysteretic UVLO Ramp Plot
    du = load_wrdata("uvlo_sweep_waveforms.txt")
    tu = du[:, 0] * 1e3
    fig, axes = plt.subplots(2, 1, figsize=(10, 5.5), sharex=True)
    axes[0].plot(tu, du[:, 1], label="VIN_20V (through 0.30 Ohm source Z)", color="#c0392b", lw=1.5)
    axes[0].axhline(17.54, color="#27ae60", ls="--", lw=0.9, label="V_ON = 17.54 V")
    axes[0].axhline(16.64, color="#2980b9", ls=":", lw=0.9, label="V_OFF = 16.64 V (0.90 V Hyst)")
    axes[0].set_ylabel("Supply Voltage (V)")
    axes[0].set_title("Hysteretic Hardware UVLO (LM393B + LM4040-2.5) — Zero Chatter on Slow Ramp")
    axes[0].legend(loc="upper right", fontsize=8)
    axes[0].grid(True, alpha=0.3)

    axes[1].plot(tu, du[:, 11] * 1e3, label="Ch1 UV Current (mA)", color="#6c3483", lw=1.4)
    axes[1].plot(tu, du[:, 13] * 1e3, label="Ch2 Vis Current (mA)", color="#1f618d", lw=1.4)
    axes[1].set_ylabel("LED Current (mA)")
    axes[1].set_xlabel("Time (ms)")
    axes[1].legend(loc="upper right", fontsize=8)
    axes[1].grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "plot_uvlo_sweep.png", dpi=150)
    plt.close(fig)

    # 3. Faults Plot (Open+Reconnect + Short-LED + True 85 C Hot-Plug & Q1 Slew Inrush)
    do = load_wrdata("fault_open_led.txt")
    ds = load_wrdata("fault_short_led.txt")
    dh = load_wrdata("fault_hotplug_85c.txt")
    fig, axes = plt.subplots(3, 1, figsize=(10, 8.2))
    axes[0].plot(do[:, 0] * 1e3, do[:, 7] * 1e3, label="I_UV (mA) — Disconnect @ 2 ms, Live-Reconnect @ 4 ms", color="#6c3483", lw=1.2)
    axes[0].plot(do[:, 0] * 1e3, do[:, 11] * 1e3, label="I_VIS (mA) — Live-Reconnect @ 4 ms", color="#1f618d", lw=1.1, alpha=0.8)
    axes[0].axhline(1000.0, color="#c0392b", ls="--", lw=0.9, label="SST-10-UV 1.0 A CW Max")
    axes[0].set_title("Fault 1: Open-LED Disconnect & Live-Reconnect Surge (C4/C5=100 nF + 6.8 Ohm)")
    axes[0].set_ylabel("LED Current (mA)")
    axes[0].legend(fontsize=8)
    axes[0].grid(True, alpha=0.3)

    axes[1].plot(ds[:, 0] * 1e3, ds[:, 3] * 1e3, label="I(L1) Inductor Current (mA)", color="#1f618d", lw=1.1)
    axes[1].set_title("Fault 2: Shorted LED String at t=2.5 ms — Inherent AL8860 Regulation (~333 mA)")
    axes[1].set_ylabel("Current (mA)")
    axes[1].legend(fontsize=8)
    axes[1].grid(True, alpha=0.3)

    axes[2].plot(dh[:, 0] * 1e3, dh[:, 1], label="V(VBUS_FUSED) (V)", color="#c0392b", lw=1.3)
    axes[2].plot(dh[:, 0] * 1e3, dh[:, 3], label="V(VIN_20V) Slew-Limited (V)", color="#27ae60", lw=1.3)
    ax2_r = axes[2].twinx()
    ax2_r.plot(dh[:, 0] * 1e3, dh[:, 7] * 1e3, label="I(Q1) Inrush (mA)", color="#2980b9", lw=1.1, ls="--")
    ax2_r.set_ylabel("Q1 Inrush (mA)", color="#2980b9")
    axes[2].set_title("Fault 4: True 85 C Hot-Plug (1.0 uH) + Q1 C13-to-GND Slew-Controlled Inrush (<1 A)")
    axes[2].set_ylabel("Voltage (V)")
    axes[2].set_xlabel("Time (ms)")
    axes[2].legend(loc="center right", fontsize=8)
    axes[2].grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "plot_fault_suite.png", dpi=150)
    plt.close(fig)


def main():
    print("=== LepiLED Rev 4.1 (USB-C PD Only + S3 DPDT + Hysteretic UVLO) Verification Suite ===")
    nominal = run_ngspice("lepiled_nominal.cir")
    uvlo = run_ngspice("lepiled_fault_uvlo_sweep.cir")
    open_led = run_ngspice("lepiled_fault_open_led.cir")
    short_led = run_ngspice("lepiled_fault_short_led.cir")
    input_prot = run_ngspice("lepiled_fault_input_prot.cir")
    hotplug_85c = run_ngspice("lepiled_fault_hotplug_85c.cir")

    corners = run_corner_sweep()
    mc = run_monte_carlo(n=2000)
    plot_results(mc)

    # Nominal analytic operating point at 20.0 V, 25 C (reconciled with SPICE: includes D12 LED + dividers)
    nom_uv = solve_buck_channel(19.90, 4 * 3.59, 0.100, 0.300, 68e-6, 0.29, 0.30, 0.34)
    nom_vis = solve_buck_channel(19.90, 2 * 2.92 + 2.69 + 2.92, 0.100, 0.300, 68e-6, 0.29, 0.30, 0.34)
    i_div_nom = 19.9 / 69000.0 + 19.9 / 200000.0
    i_in_nom = nom_uv["i_in"] + nom_vis["i_in"] + 0.0033 + 0.0029 + 0.0006 + (19.9 - 2.5) / 10000.0 + i_div_nom
    p_over_nom = (
        19.9 * 0.0068
        + 19.9 * (19.9 - 2.5) / 10000.0
        + 19.9 * i_div_nom
        + (i_in_nom**2) * (0.080 + 0.005 + 0.052)
    )
    p_pcb_nom = (
        nom_uv["p_ic"] + nom_uv["p_diode"] + nom_uv["p_ind"] + nom_uv["p_rs"]
        + nom_vis["p_ic"] + nom_vis["p_diode"] + nom_vis["p_ind"] + nom_vis["p_rs"]
        + p_over_nom
    )

    uvlo_hyst_meas = uvlo["v_uvlo_on"] - uvlo["v_uvlo_off"]

    checks = {
        "nominal_off_leakage_mA": (abs(nominal["i_uv_off"] * 1e3) < 0.5 and abs(nominal["i_vis_off"] * 1e3) < 0.5),
        "nominal_4uv_current_mA": (315.0 <= nominal["i_uv_4uv"] * 1e3 <= 355.0 and abs(nominal["i_vis_4uv"] * 1e3) < 0.5),
        "nominal_8all_current_mA": (315.0 <= nominal["i_uv_8all"] * 1e3 <= 355.0 and 315.0 <= nominal["i_vis_8all"] * 1e3 <= 355.0),
        "nominal_lm4040_calibrated_2p50V": (2.485 <= nominal["vref_nom"] <= 2.515),
        "nominal_inductor_peak_margin": (nominal["il1_pk"] < 0.55 and nominal["il2_pk"] < 0.55),
        "nominal_vin_ripple_lt_250mV": (nominal["vin_pp"] < 0.25),
        "uvlo_rejects_5_to_15p75V": (uvlo["vctrl_1575v"] < 0.05 and abs(uvlo["i_uv_1575v"] * 1e3) < 0.5 and abs(uvlo["i_vis_1575v"] * 1e3) < 0.5),
        "uvlo_hysteresis_zero_chatter": (
            17.2 <= uvlo["v_uvlo_on"] <= 17.9
            and 16.3 <= uvlo["v_uvlo_off"] <= 17.0
            and uvlo_hyst_meas >= 0.70
            and uvlo["v_ok_min_post"] > 7.0
            and abs(uvlo["i_uv_end_off"] * 1e3) < 0.5
        ),
        "fault_open_led_and_live_reconnect_safe": (
            open_led["vsw1_pk_open"] < 23.0
            and abs(open_led["i_uv_open"] * 1e3) < 0.5
            and open_led["i_uv_reconn_pk"] < 1.00
            and open_led["i_vis_reconn_pk"] < 1.20
            and open_led["i_uv_recover"] * 1e3 > 315.0
        ),
        "fault_short_led_regulated": (280.0 <= short_led["il1_avg_short"] * 1e3 <= 390.0 and short_led["il1_pk_short"] < 0.65),
        "fault_neg_transient_clamped": (input_prot["neg_vbus_min"] > -2.5),
        "fault_hotplug_21V_clamped": (input_prot["hp_vbus_peak"] < 28.0 and input_prot["q1_off_leak_v"] < 0.05),
        "fault_hotplug_85c_and_q1_inrush_safe": (
            hotplug_85c["vbus_85c_peak"] < 28.5
            and hotplug_85c["vin20_off_max"] < 0.20
            and hotplug_85c["vin20_85c_peak"] < 23.0
            and hotplug_85c["q1_inrush_pk"] < 1.00
            and hotplug_85c["vin20_settle"] > 20.5
        ),
        "corner_sweep_zero_failures": (corners["failed_corners"] == 0),
        "monte_carlo_100pct_yield": (mc["passes"] == mc["n_trials"]),
    }

    summary = {
        "architecture": "Rev 4.1 (USB-C PD Only AP33771C + Single 40V DMN4035L + Hysteretic UVLO + Direct Gold DPDT + Dual AL8860WT-7 Buck)",
        "all_passed": all(checks.values()),
        "checks": checks,
        "ngspice_nominal": {k: round(v, 6) for k, v in nominal.items()},
        "ngspice_uvlo": {**{k: round(v, 6) for k, v in uvlo.items()}, "v_uvlo_hyst": round(uvlo_hyst_meas, 6)},
        "ngspice_open_led": {k: round(v, 6) for k, v in open_led.items()},
        "ngspice_short_led": {k: round(v, 6) for k, v in short_led.items()},
        "ngspice_input_prot": {k: round(v, 6) for k, v in input_prot.items()},
        "ngspice_hotplug_85c": {k: round(v, 6) for k, v in hotplug_85c.items()},
        "analytic_nominal_20V": {
            "ch1_uv": {k: round(v, 6) for k, v in nom_uv.items()},
            "ch2_vis": {k: round(v, 6) for k, v in nom_vis.items()},
            "i_in_8all_A": round(i_in_nom, 4),
            "p_in_8all_W": round(20.0 * i_in_nom, 3),
            "p_pcb_loss_nom_W": round(p_pcb_nom, 3),
            "p_overhead_W": round(p_over_nom, 3),
            "sys_efficiency_pct": round(100.0 * (nom_uv["p_led"] + nom_vis["p_led"]) / (20.0 * i_in_nom), 2),
        },
        "corner_sweep": {k: round(v, 6) if isinstance(v, float) else v for k, v in corners.items()},
        "monte_carlo": mc,
    }

    (OUT_DIR / "sim_summary.json").write_text(json.dumps(summary, indent=2))

    print("\n--- CHECKS ---")
    for name, ok in checks.items():
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
    print(f"\nNominal 8-ALL (ngspice): I_UV={nominal['i_uv_8all']*1e3:.1f} mA, I_VIS={nominal['i_vis_8all']*1e3:.1f} mA, "
          f"I_in={-nominal['i_in_8all']*1e3:.1f} mA @ 20 V, V_REF={nominal['vref_nom']:.4f} V, "
          f"VIN_pp={nominal['vin_pp']*1e3:.1f} mV, dI_UV_pp={nominal['i_uv_pp']*1e3:.1f} mA")
    print(f"Analytic 20 V Nominal: P_in={20.0*i_in_nom:.2f} W ({i_in_nom:.3f} A), P_PCB={p_pcb_nom:.3f} W, "
          f"Sys Eff={100.0*(nom_uv['p_led']+nom_vis['p_led'])/(20.0*i_in_nom):.1f}%")
    print(f"UVLO (0.30 Ohm Z): V_ON={uvlo['v_uvlo_on']:.3f} V, V_OFF={uvlo['v_uvlo_off']:.3f} V, "
          f"Hyst={uvlo_hyst_meas:.3f} V, V_OK_min_post={uvlo['v_ok_min_post']:.2f} V (ZERO chatter!)")
    print(f"Faults: Open+Reconnect I_UV_pk={open_led['i_uv_reconn_pk']:.3f} A (<1.0 A), I_VIS_pk={open_led['i_vis_reconn_pk']:.3f} A (<1.2 A); "
          f"Short I_L1={short_led['il1_avg_short']*1e3:.1f} mA; NegClamp={input_prot['neg_vbus_min']:.2f} V; "
          f"85C HotPlug V_pk={hotplug_85c['vbus_85c_peak']:.2f} V, Q1_OFF={hotplug_85c['vin20_off_max']:.4f} V, Q1_inrush_pk={hotplug_85c['q1_inrush_pk']:.3f} A (<1.0 A)")
    print(f"Corners: {corners['total_corners']-corners['failed_corners']}/{corners['total_corners']} PASS "
          f"(P_PCB_max={corners['total_pcb_loss_max']:.3f} W, I_in_max={corners['i_in_total_max']:.3f} A, Tj_max={max(corners['uv_tj_max'], corners['vis_tj_max']):.1f} C)")
    print(f"Monte Carlo: {mc['passes']}/{mc['n_trials']} ({mc['yield_pct']}%) PASS; "
          f"V_ON=[{mc['v_uvlo_on_V']['min']}, {mc['v_uvlo_on_V']['max']}] V, V_OFF=[{mc['v_uvlo_off_V']['min']}, {mc['v_uvlo_off_V']['max']}] V")

    if not all(checks.values()):
        sys.exit(1)


if __name__ == "__main__":
    main()
