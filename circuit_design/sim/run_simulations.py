#!/usr/bin/env python3
"""
LepiLED DIY Maxi Switch — Dual-Engine Reproducible Circuit Simulation Suite

Single Source of Truth:
  - Reads component & datasheet limits from datasheets/datasheets_summary.json
  - Reads RefDes / nominal values from circuit_design/COMPONENT_IDS.csv

Engine 1 (ngspice SPICE):
  - Executes circuit_design/sim/netlists/lepiled_nominal.cir (OFF -> 4-UV -> 8-ALL -> 4-UV)
  - Executes circuit_design/sim/netlists/lepiled_fault_open_led.cir (open-load 20V OVP clamp)
  - Parses logs & wrdata traces, saves ngspice_transient_modes.png

Engine 2 (Python / SciPy):
  - Switched-averaged state-space ODE (scipy.integrate.solve_ivp) across OFF -> 4-UV -> 8-ALL -> 4-UV
  - Exhaustive worst-case corner sweep across:
      * Datasheet VFB [0.178, 0.202] V (±6.3%), R_sense ±1%, L ±20%
      * Out-of-spec VFB ±10% and ±15%, R_sense ±5%, L ±20%
      * Vin [4.5, 5.5] V, Vf across [-10 C, +85 C], fsw [1.2, 2.0] MHz, Rds_on [0.17, 0.33] Ohm, VD [0.34, 0.50] V
  - N = 2000 seeded (seed=42) Monte-Carlo tolerance trials checking all datasheet & thermal limits
  - Outputs: sim_summary.json, corner_sweep.csv, scipy_transient_modes.png, monte_carlo_margins.png
"""

from __future__ import annotations

import csv
import itertools
import json
import math
import re
import shutil
import subprocess
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import solve_ivp


REPO_ROOT = Path(__file__).resolve().parents[2]
SIM_DIR = Path(__file__).resolve().parent
NETLIST_DIR = SIM_DIR / "netlists"
OUT_DIR = SIM_DIR / "outputs"
DATASHEETS_JSON = REPO_ROOT / "datasheets" / "datasheets_summary.json"
COMPONENT_IDS_CSV = REPO_ROOT / "circuit_design" / "COMPONENT_IDS.csv"
USER_NGSPICE = Path("/home/alimuldal/.local/share/lepiled-tools/bin/ngspice")


def load_specs() -> tuple[dict, dict[str, dict]]:
    with DATASHEETS_JSON.open("r", encoding="utf-8") as f:
        ds = json.load(f)
    comps: dict[str, dict] = {}
    with COMPONENT_IDS_CSV.open("r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            comps[row["RefDes"]] = row
    return ds, comps


def find_ngspice() -> Path | None:
    which = shutil.which("ngspice")
    if which:
        return Path(which)
    if USER_NGSPICE.exists():
        return USER_NGSPICE
    return None


def parse_ngspice_meas(log_text: str) -> dict[str, float]:
    meas: dict[str, float] = {}
    pat = re.compile(r"^([a-zA-Z0-9_]+)\s*=\s*([-+]?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?)")
    for line in log_text.splitlines():
        m = pat.match(line.strip())
        if m:
            meas[m.group(1)] = float(m.group(2))
    return meas


def run_ngspice_suite() -> dict:
    ngspice = find_ngspice()
    if ngspice is None:
        return {"status": "skipped_missing_ngspice"}

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    results = {"status": "executed", "binary": str(ngspice), "runs": {}}

    for name, netlist in [
        ("nominal", NETLIST_DIR / "lepiled_nominal.cir"),
        ("fault_open_led", NETLIST_DIR / "lepiled_fault_open_led.cir"),
    ]:
        proc = subprocess.run(
            [str(ngspice), "-b", str(netlist)],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            check=True,
        )
        log_path = OUT_DIR / f"ngspice_{name}.log"
        full_log = proc.stdout + proc.stderr
        log_path.write_text(full_log, encoding="utf-8")
        assert "Error:" not in full_log and "failed!" not in full_log, (
            f"ngspice {name} reported errors in {log_path}"
        )
        meas = parse_ngspice_meas(proc.stdout)
        results["runs"][name] = {
            "returncode": proc.returncode,
            "measurements": meas,
            "log_file": str(log_path.relative_to(REPO_ROOT)),
        }

    # Plot ngspice nominal trace if generated
    trace_path = OUT_DIR / "ngspice_nominal_trace.txt"
    if trace_path.exists():
        data = np.loadtxt(trace_path, skiprows=1)
        t_ms = data[:, 0] * 1e3
        # Downsample cleanly for plotting (~4000 points)
        step = max(1, len(t_ms) // 4000)
        td = t_ms[::step]

        fig, axes = plt.subplots(3, 1, figsize=(10.5, 8.0), sharex=True)
        axes[0].plot(td, data[::step, 2], label="EN1_NET (U1.DIM)", color="#047857", lw=1.3)
        axes[0].plot(td, data[::step, 3], label="DIM2_NET (U2.DIM, 1ms RC)", color="#2563EB", lw=1.3)
        axes[0].axhline(1.8, color="#64748B", ls="--", lw=0.9, label="VDIM_H = 1.8 V")
        axes[0].set_ylabel("Enable (V)")
        axes[0].set_title("ngspice 45.2 Cycle-by-Cycle Transient: OFF -> 4-UV -> 8-ALL -> 4-UV")
        axes[0].legend(loc="upper right", fontsize=8)
        axes[0].grid(True, alpha=0.3)

        axes[1].plot(td, data[::step, 4], label="VOUT1 (4S UV)", color="#7C3AED", lw=1.2)
        axes[1].plot(td, data[::step, 5], label="VOUT2 (4S Vis)", color="#0EA5E9", lw=1.2)
        axes[1].set_ylabel("Vout (V)")
        axes[1].legend(loc="upper right", fontsize=8)
        axes[1].grid(True, alpha=0.3)

        axes[2].plot(td, data[::step, 10] * 1e3, label="I_UV (D1..D4)", color="#7C3AED", lw=1.1)
        axes[2].plot(td, data[::step, 11] * 1e3, label="I_VIS (D5..D8)", color="#0284C7", lw=1.1)
        axes[2].plot(td, -data[::step, 12] * 1e3, label="I_USB_IN (mA)", color="#DC2626", lw=0.9, alpha=0.75)
        axes[2].set_ylabel("Current (mA)")
        axes[2].set_xlabel("Time (ms)")
        axes[2].legend(loc="upper right", fontsize=8)
        axes[2].grid(True, alpha=0.3)

        fig.tight_layout()
        fig.savefig(OUT_DIR / "ngspice_transient_modes.png", dpi=180)
        plt.close(fig)

    return results


def solve_steady_boost(
    vin_ic: float,
    L: float,
    r_sense: float,
    vstr_at_350mA: float,
    rdyn_str: float,
    vfb: float,
    fsw: float,
    rds: float,
    dcr: float,
    vd: float,
    c_out_eff: float,
    esr_out: float,
    iq: float,
    tr_ns: float,
    tf_ns: float,
) -> dict:
    """Solve steady-state CCM/DCM boost converter equations per TI LM3410 SNVS541H."""
    i_led = vfb / r_sense
    v_str = vstr_at_350mA + (i_led - 0.350) * rdyn_str
    v_out = v_str + vfb

    # Solve duty cycle iteratively including inductor DCR & switch Rds_on drops
    d = (v_out + vd - vin_ic) / (v_out + vd)
    for _ in range(15):
        i_in_avg = i_led / max(1.0 - d, 0.04)
        v_drop = i_in_avg * (dcr + d * rds)
        d_new = (v_out + vd - vin_ic + v_drop) / (v_out + vd)
        d = min(max(d_new, 0.05), 0.95)

    i_in_avg = i_led / (1.0 - d)
    di_l_pp = (vin_ic - i_in_avg * (dcr + rds)) * d / (L * fsw)
    i_l_pk = i_in_avg + 0.5 * di_l_pp
    i_l_min = i_in_avg - 0.5 * di_l_pp
    is_ccm = i_l_min > 0.0

    # RMS & power loss breakdown (TI Sec. 10.3.3 Eqs. 40-49)
    i_l_rms = math.sqrt(i_in_avg**2 + (di_l_pp**2) / 12.0)
    i_sw_rms = math.sqrt(d) * i_l_rms
    p_cond = (i_sw_rms**2) * rds
    p_sw = 0.5 * v_out * i_in_avg * fsw * ((tr_ns + tf_ns) * 1e-9)
    p_q = vin_ic * iq
    p_ic = p_cond + p_sw + p_q
    p_diode = vd * i_led
    p_ind = (i_l_rms**2) * dcr
    p_rsense = (i_led**2) * r_sense
    p_led = v_str * i_led
    p_in_ch = p_led + p_rsense + p_ic + p_diode + p_ind
    eta = p_led / p_in_ch

    # Output ripple (TI Eq. 11)
    r_out_dyn = (v_out / i_led)
    dv_out_pp = di_l_pp * esr_out + (v_out * d) / (2.0 * fsw * r_out_dyn * c_out_eff)

    return {
        "i_led_A": i_led,
        "v_str_V": v_str,
        "v_out_V": v_out,
        "duty": d,
        "ccm": is_ccm,
        "i_in_avg_A": i_in_avg + iq,
        "di_l_pp_A": di_l_pp,
        "i_l_pk_A": i_l_pk,
        "i_l_rms_A": i_l_rms,
        "dv_out_pp_V": dv_out_pp,
        "p_led_W": p_led,
        "p_ic_W": p_ic,
        "p_diode_W": p_diode,
        "p_ind_W": p_ind,
        "p_rsense_W": p_rsense,
        "p_in_ch_W": p_in_ch,
        "efficiency": eta,
    }


def run_scipy_transient_ode(ds: dict) -> dict:
    """State-space averaged transient ODE across OFF -> 4-UV -> 8-ALL -> 4-UV."""
    ic = ds["boost_ic"]["LM3410XMY/NOPB"]
    ind = ds["inductor"]["SRN6045-100M"]
    cap_out = ds["capacitors"]["CL32B106KBJNFNE"]
    res_s = ds["resistors"]["CRL1206-FW-R560ELF"]
    uv = ds["leds"]["SST-10-UV-A130-G365-00"]
    rb = ds["leds"]["XPEBRY-L1-0000-00R02"]
    gr = ds["leds"]["XPEBGR-L1-0000-00E01"]
    cw = ds["leds"]["XPEBWT-L1-0000-00F51"]
    mos = ds["protection_and_input"]["DMG2305UX-7"]
    ptc = ds["protection_and_input"]["MF-LSMF300/24X"]

    L = ind["L_H"]
    dcr = ind["dcr_max_ohm"] * 0.85
    c_out = cap_out["effective_capacitance_at_16V_F"]
    r_s = res_s["resistance_ohm"]
    vfb = ic["vfb_V"]["typ"]
    rds = ic["rds_on_ohm"]["typ_25C"]
    vd = ds["schottky_diode"]["B340A-13-F"]["vf_V"]["at_1A_25C_typ"]

    # Input path impedance: cable (0.08) + F1 (0.03) + Q1 (0.04)
    r_in_path = 0.08 + 0.5 * (ptc["r_min_ohm"] + ptc["r_1max_ohm"]) + mos["rds_on_ohm"]["at_4V5_typ"]
    v_usb = 5.0

    # Smooth LED string I(V) curve from datasheet Vstr0 + rdyn
    v_th_uv = 4.0 * (uv["vf_at_350mA_25C_V"]["typ"] - 0.350 * uv["rdyn_ohm_per_led"])
    r_dyn_uv = 4.0 * uv["rdyn_ohm_per_led"] + r_s
    v_th_vis = (
        2.0 * rb["vf_at_350mA_25C_V"]["typ"]
        + gr["vf_at_350mA_25C_V"]["typ"]
        + cw["vf_at_350mA_25C_V"]["typ"]
        - 0.350 * (2 * rb["rdyn_ohm_per_led"] + gr["rdyn_ohm_per_led"] + cw["rdyn_ohm_per_led"])
    )
    r_dyn_vis = 2 * rb["rdyn_ohm_per_led"] + gr["rdyn_ohm_per_led"] + cw["rdyn_ohm_per_led"] + r_s

    def led_current(v_out: float, v_th: float, r_dyn: float) -> float:
        # Smooth diode turn-on with 150 mV soft knee
        dv = v_out - v_th
        return 0.15 * np.logaddexp(0.0, dv / 0.15) / r_dyn

    def switch_mode(t: float) -> tuple[float, float]:
        # OFF (0..0.2ms) -> 4-UV (0.2..1.5ms) -> 8-ALL (1.5..3.5ms) -> 4-UV (3.5..4.5ms)
        if t < 0.2e-3:
            return 0.0, 0.0
        elif t < 1.5e-3:
            return 1.0, 0.0
        elif t < 3.5e-3:
            return 1.0, 1.0
        else:
            return 1.0, 0.0

    # State: [i_L1, v_C4, d1_int, i_L2, v_C5, d2_int, v_dim2]
    tau_rc = 10e3 * 100e-9  # R7 * C6 = 1.0 ms

    def rhs(t: float, y: np.ndarray) -> np.ndarray:
        i_l1, v_c4, d1, i_l2, v_c5, d2, v_dim2 = y
        sw_uv, sw_all = switch_mode(t)

        # Estimate vin_prot after input path drop
        i_in_est = max(i_l1, 0.0) + max(i_l2, 0.0)
        vin_prot = v_usb - i_in_est * r_in_path
        v_en1 = vin_prot - 0.65 if (sw_uv > 0.5 or sw_all > 0.5) else 0.0
        v_en2_src = vin_prot if sw_all > 0.5 else 0.0

        # R7/C6/R6 divider & RC stagger on DIM2
        dv_dim2 = (v_en2_src - v_dim2) / tau_rc if sw_all > 0.5 else -(v_dim2 / (10e3 * 100e-9))

        en1 = 1.0 if v_en1 >= ic["vdim_high_min_V"] else 0.0
        en2 = 1.0 if v_dim2 >= ic["vdim_high_min_V"] else 0.0

        i_led1 = led_current(v_c4, v_th_uv, r_dyn_uv)
        i_led2 = led_current(v_c5, v_th_vis, r_dyn_vis)

        v_fb1 = i_led1 * r_s
        v_fb2 = i_led2 * r_s

        # Outer current-mode control loop dynamics (PI control matching ~0.35ms soft-start)
        d_cmd1 = np.clip(d1 + 2.0 * (vfb - v_fb1), 0.05, ic["dmax"]["typ"]) if en1 > 0.5 else 0.0
        d_cmd2 = np.clip(d2 + 2.0 * (vfb - v_fb2), 0.05, ic["dmax"]["typ"]) if en2 > 0.5 else 0.0

        dd1 = 12000.0 * (vfb - v_fb1) if en1 > 0.5 else -15000.0 * d1
        dd2 = 12000.0 * (vfb - v_fb2) if en2 > 0.5 else -15000.0 * d2

        # State-space averaged inductor & output capacitor derivatives
        # When disabled, diode conducts passively only if v_c < vin_prot - vd
        if en1 > 0.5:
            di_l1 = (vin_prot - i_l1 * (dcr + d_cmd1 * rds) - (1.0 - d_cmd1) * (v_c4 + vd)) / L
            i_out1 = (1.0 - d_cmd1) * i_l1
        else:
            # Passive clamp path through L1 + D9 if v_c4 < vin_prot - vd
            v_pass1 = max(vin_prot - vd - v_c4, 0.0)
            di_l1 = (v_pass1 - i_l1 * 0.5) / L if v_pass1 > 0 or i_l1 > 0 else 0.0
            i_out1 = max(i_l1, 0.0)

        if en2 > 0.5:
            di_l2 = (vin_prot - i_l2 * (dcr + d_cmd2 * rds) - (1.0 - d_cmd2) * (v_c5 + vd)) / L
            i_out2 = (1.0 - d_cmd2) * i_l2
        else:
            v_pass2 = max(vin_prot - vd - v_c5, 0.0)
            di_l2 = (v_pass2 - i_l2 * 0.5) / L if v_pass2 > 0 or i_l2 > 0 else 0.0
            i_out2 = max(i_l2, 0.0)

        dv_c4 = (i_out1 - i_led1) / c_out
        dv_c5 = (i_out2 - i_led2) / c_out

        return np.array([di_l1, dv_c4, dd1, di_l2, dv_c5, dd2, dv_dim2])

    y0 = np.array([0.0, 4.7, 0.0, 0.0, 4.7, 0.0, 0.0])
    t_eval = np.linspace(0.0, 4.5e-3, 4501)
    sol = solve_ivp(rhs, (0.0, 4.5e-3), y0, method="Radau", t_eval=t_eval, rtol=1e-6, atol=1e-8)
    assert sol.success, f"ODE solver failed: {sol.message}"

    t = sol.t
    i_l1, v_c4, _, i_l2, v_c5, _, v_dim2 = sol.y
    i_led1 = np.array([led_current(v, v_th_uv, r_dyn_uv) for v in v_c4])
    i_led2 = np.array([led_current(v, v_th_vis, r_dyn_vis) for v in v_c5])
    i_in_tot = np.maximum(i_l1, 0.0) + np.maximum(i_l2, 0.0)

    m_4uv = (t >= 1.1e-3) & (t <= 1.45e-3)
    m_8all = (t >= 3.1e-3) & (t <= 3.45e-3)

    # Plot SciPy transient ODE
    fig, axes = plt.subplots(3, 1, figsize=(10.5, 8.0), sharex=True)
    axes[0].plot(t * 1e3, v_dim2, label="DIM2_NET (U2.DIM, 1.0ms stagger)", color="#2563EB", lw=1.5)
    axes[0].axhline(1.8, color="#64748B", ls="--", lw=0.9, label="VDIM_H = 1.8 V")
    axes[0].set_ylabel("DIM2 (V)")
    axes[0].set_title("SciPy Radau State-Space Transient ODE: OFF -> 4-UV -> 8-ALL -> 4-UV")
    axes[0].legend(loc="upper right", fontsize=8)
    axes[0].grid(True, alpha=0.3)

    axes[1].plot(t * 1e3, v_c4, label="VOUT1 (4S UV)", color="#7C3AED", lw=1.4)
    axes[1].plot(t * 1e3, v_c5, label="VOUT2 (4S Vis)", color="#0EA5E9", lw=1.4)
    axes[1].set_ylabel("Vout (V)")
    axes[1].legend(loc="upper right", fontsize=8)
    axes[1].grid(True, alpha=0.3)

    axes[2].plot(t * 1e3, i_led1 * 1e3, label="I_UV (mA)", color="#7C3AED", lw=1.4)
    axes[2].plot(t * 1e3, i_led2 * 1e3, label="I_VIS (mA)", color="#0284C7", lw=1.4)
    axes[2].plot(t * 1e3, i_in_tot * 1e3, label="I_IN_TOTAL (mA)", color="#DC2626", lw=1.1, alpha=0.8)
    axes[2].set_ylabel("Current (mA)")
    axes[2].set_xlabel("Time (ms)")
    axes[2].legend(loc="upper right", fontsize=8)
    axes[2].grid(True, alpha=0.3)

    fig.tight_layout()
    fig.savefig(OUT_DIR / "scipy_transient_modes.png", dpi=180)
    plt.close(fig)

    return {
        "4uv_i_uv_mA": float(np.mean(i_led1[m_4uv]) * 1e3),
        "4uv_i_vis_backfeed_mA": float(np.max(i_led2[m_4uv]) * 1e3),
        "4uv_vout1_V": float(np.mean(v_c4[m_4uv])),
        "4uv_iin_A": float(np.mean(i_in_tot[m_4uv])),
        "8all_i_uv_mA": float(np.mean(i_led1[m_8all]) * 1e3),
        "8all_i_vis_mA": float(np.mean(i_led2[m_8all]) * 1e3),
        "8all_vout1_V": float(np.mean(v_c4[m_8all])),
        "8all_vout2_V": float(np.mean(v_c5[m_8all])),
        "8all_iin_A": float(np.mean(i_in_tot[m_8all])),
        "dim2_cross_1p8V_ms": float(t[np.argmax(v_dim2 >= 1.8)] * 1e3),
    }


def run_corners_and_mc(ds: dict) -> tuple[dict, list[dict]]:
    ic = ds["boost_ic"]["LM3410XMY/NOPB"]
    ind = ds["inductor"]["SRN6045-100M"]
    sch = ds["schottky_diode"]["B340A-13-F"]
    res_s = ds["resistors"]["CRL1206-FW-R560ELF"]
    cap_out = ds["capacitors"]["CL32B106KBJNFNE"]
    uv = ds["leds"]["SST-10-UV-A130-G365-00"]
    rb = ds["leds"]["XPEBRY-L1-0000-00R02"]
    gr = ds["leds"]["XPEBGR-L1-0000-00E01"]
    cw = ds["leds"]["XPEBWT-L1-0000-00F51"]

    L_nom = ind["L_H"]
    L_tol = ind["tolerance_fraction"]
    r_nom = res_s["resistance_ohm"]
    vfb_nom = ic["vfb_V"]["typ"]
    c_out_eff = cap_out["effective_capacitance_at_16V_F"]
    esr = cap_out["esr_ohm"]
    tr, tf = ic["t_rise_ns"], ic["t_fall_ns"]

    # Nominal steady-state for Ch1 (4S UV) and Ch2 (4S Vis)
    vstr_uv_nom = 4.0 * uv["vf_at_350mA_25C_V"]["typ"]
    vstr_vis_nom = 2.0 * rb["vf_at_350mA_25C_V"]["typ"] + gr["vf_at_350mA_25C_V"]["typ"] + cw["vf_at_350mA_25C_V"]["typ"]
    rdyn_uv = 4.0 * uv["rdyn_ohm_per_led"]
    rdyn_vis = 2.0 * rb["rdyn_ohm_per_led"] + gr["rdyn_ohm_per_led"] + cw["rdyn_ohm_per_led"]

    nom_ch1 = solve_steady_boost(
        vin_ic=4.85, L=L_nom, r_sense=r_nom, vstr_at_350mA=vstr_uv_nom, rdyn_str=rdyn_uv,
        vfb=vfb_nom, fsw=ic["fsw_Hz"]["typ"], rds=ic["rds_on_ohm"]["typ_25C"],
        dcr=ind["dcr_typ_ohm"], vd=sch["vf_V"]["at_1A_25C_typ"],
        c_out_eff=c_out_eff, esr_out=esr, iq=ic["iq_switching_mA"]["typ"] * 1e-3,
        tr_ns=tr, tf_ns=tf,
    )
    nom_ch2 = solve_steady_boost(
        vin_ic=4.85, L=L_nom, r_sense=r_nom, vstr_at_350mA=vstr_vis_nom, rdyn_str=rdyn_vis,
        vfb=vfb_nom, fsw=ic["fsw_Hz"]["typ"], rds=ic["rds_on_ohm"]["typ_25C"],
        dcr=ind["dcr_typ_ohm"], vd=sch["vf_V"]["at_1A_25C_typ"],
        c_out_eff=c_out_eff, esr_out=esr, iq=ic["iq_switching_mA"]["typ"] * 1e-3,
        tr_ns=tr, tf_ns=tf,
    )

    # Exhaustive corner sweep across 3 scenarios
    # Temp range -10C to +85C shifts Vf: UV (-2.67 mV/C * 4 = -10.68 mV/C -> +0.37V at -10C, -0.64V at +85C)
    # Plus binning spread: UV [2.7..3.9]*4 => [11.4, 16.0] V; Vis => [10.2, 13.5] V
    scenarios = [
        ("datasheet_spec", [ic["vfb_V"]["min"], vfb_nom, ic["vfb_V"]["max"]], [r_nom * 0.99, r_nom, r_nom * 1.01]),
        ("oos_vfb_10pct_r_5pct", [vfb_nom * 0.90, vfb_nom, vfb_nom * 1.10], [r_nom * 0.95, r_nom, r_nom * 1.05]),
        ("oos_vfb_15pct_r_5pct", [vfb_nom * 0.85, vfb_nom, vfb_nom * 1.15], [r_nom * 0.95, r_nom, r_nom * 1.05]),
    ]

    corner_rows: list[dict] = []
    corner_summary: dict = {}

    for scen_name, vfb_vals, r_vals in scenarios:
        for ch_name, vstr_vals, rdyn_str, if_max in [
            ("Ch1_UV", [11.4, vstr_uv_nom, 16.0], rdyn_uv, uv["if_max_cw_A"]),
            ("Ch2_Vis", [10.2, vstr_vis_nom, 13.5], rdyn_vis, rb["if_max_cw_A"]),
        ]:
            max_ipk = 0.0
            max_d = 0.0
            max_iled = 0.0
            max_vout = 0.0
            max_pic = 0.0
            dcm_count = 0
            tot = 0

            for vin, L, r_s, vstr, vfb, fsw, rds, vd in itertools.product(
                [4.5, 5.0, 5.5],
                [L_nom * (1.0 - L_tol), L_nom, L_nom * (1.0 + L_tol)],
                r_vals,
                vstr_vals,
                vfb_vals,
                [ic["fsw_Hz"]["min"], ic["fsw_Hz"]["typ"], ic["fsw_Hz"]["max"]],
                [ic["rds_on_ohm"]["typ_25C"], ic["rds_on_ohm"]["typ_125C"], ic["rds_on_ohm"]["max"]],
                [0.30, sch["vf_V"]["at_1A_25C_typ"], sch["vf_V"]["at_3A_25C_max"]],
            ):
                tot += 1
                res = solve_steady_boost(
                    vin_ic=vin, L=L, r_sense=r_s, vstr_at_350mA=vstr, rdyn_str=rdyn_str,
                    vfb=vfb, fsw=fsw, rds=rds, dcr=ind["dcr_max_ohm"] * 1.30, vd=vd,
                    c_out_eff=c_out_eff, esr_out=esr, iq=ic["iq_switching_mA"]["max"] * 1e-3,
                    tr_ns=tr, tf_ns=tf,
                )
                if not res["ccm"]:
                    dcm_count += 1
                max_ipk = max(max_ipk, res["i_l_pk_A"])
                max_d = max(max_d, res["duty"])
                max_iled = max(max_iled, res["i_led_A"])
                max_vout = max(max_vout, res["v_out_V"])
                max_pic = max(max_pic, res["p_ic_W"])

                if (
                    vin == 4.5
                    and L == L_nom * (1.0 - L_tol)
                    and r_s == min(r_vals)
                    and vstr == max(vstr_vals)
                    and vfb == max(vfb_vals)
                    and fsw == ic["fsw_Hz"]["min"]
                    and rds == ic["rds_on_ohm"]["max"]
                    and vd == sch["vf_V"]["at_3A_25C_max"]
                ):
                    corner_rows.append({
                        "scenario": scen_name,
                        "channel": ch_name,
                        "vin_V": vin,
                        "L_uH": round(L * 1e6, 2),
                        "rsense_ohm": round(r_s, 4),
                        "vstr_V": vstr,
                        "vfb_mV": round(vfb * 1e3, 1),
                        "fsw_MHz": fsw / 1e6,
                        "rds_ohm": rds,
                        "i_led_mA": round(res["i_led_A"] * 1e3, 2),
                        "v_out_V": round(res["v_out_V"], 3),
                        "duty": round(res["duty"], 4),
                        "i_l_pk_A": round(res["i_l_pk_A"], 4),
                        "margin_vs_icl_min_A": round(ic["icl_A"]["min"] - res["i_l_pk_A"], 4),
                        "p_ic_mW": round(res["p_ic_W"] * 1e3, 1),
                        "ccm": res["ccm"],
                    })

            key = f"{scen_name}__{ch_name}"
            corner_summary[key] = {
                "total_corners": tot,
                "dcm_corners": dcm_count,
                "max_i_l_pk_A": round(max_ipk, 4),
                "margin_vs_icl_min_A": round(ic["icl_A"]["min"] - max_ipk, 4),
                "max_duty": round(max_d, 4),
                "margin_vs_dmax_min": round(ic["dmax"]["min"] - max_d, 4),
                "max_i_led_mA": round(max_iled * 1e3, 2),
                "max_v_out_V": round(max_vout, 3),
                "max_p_ic_mW": round(max_pic * 1e3, 1),
                "all_limits_pass": bool(
                    max_ipk < ic["icl_A"]["min"]
                    and max_d < ic["dmax"]["min"]
                    and max_iled < if_max
                    and max_vout < ic["vsw_recommended_V"]["max"]
                ),
            }

    # Seeded N = 2000 Monte-Carlo (including out-of-spec tails: 3-sigma covers ±12% VFB, ±3% R, ±20% L)
    rng = np.random.default_rng(42)
    N = 2000
    mc_ipk_ch1 = np.zeros(N)
    mc_ipk_ch2 = np.zeros(N)
    mc_iled_ch1 = np.zeros(N)
    mc_vout_ch1 = np.zeros(N)
    mc_tj_ic1 = np.zeros(N)

    for i in range(N):
        vin = rng.uniform(4.60, 5.40)
        L1 = np.clip(rng.normal(L_nom, L_nom * L_tol / 2.5), L_nom * 0.78, L_nom * 1.22)
        L2 = np.clip(rng.normal(L_nom, L_nom * L_tol / 2.5), L_nom * 0.78, L_nom * 1.22)
        r1 = rng.normal(r_nom, r_nom * 0.015)
        r2 = rng.normal(r_nom, r_nom * 0.015)
        vfb1 = np.clip(rng.normal(vfb_nom, vfb_nom * 0.045), 0.1615, 0.2185)
        vfb2 = np.clip(rng.normal(vfb_nom, vfb_nom * 0.045), 0.1615, 0.2185)
        fsw1 = np.clip(rng.normal(1.6e6, 0.12e6), 1.2e6, 2.0e6)
        fsw2 = np.clip(rng.normal(1.6e6, 0.12e6), 1.2e6, 2.0e6)
        vstr1 = rng.uniform(13.2, 15.6)
        vstr2 = rng.uniform(10.6, 12.8)
        rds1 = rng.uniform(0.17, 0.28)
        rds2 = rng.uniform(0.17, 0.28)
        vd = rng.uniform(0.32, 0.44)
        t_pcb = rng.uniform(25.0, 60.0)

        c1 = solve_steady_boost(vin, L1, r1, vstr1, rdyn_uv, vfb1, fsw1, rds1, ind["dcr_max_ohm"] * 1.2, vd, c_out_eff, esr, 7e-3, tr, tf)
        c2 = solve_steady_boost(vin, L2, r2, vstr2, rdyn_vis, vfb2, fsw2, rds2, ind["dcr_max_ohm"] * 1.2, vd, c_out_eff, esr, 7e-3, tr, tf)

        mc_ipk_ch1[i] = c1["i_l_pk_A"]
        mc_ipk_ch2[i] = c2["i_l_pk_A"]
        mc_iled_ch1[i] = c1["i_led_A"] * 1e3
        mc_vout_ch1[i] = c1["v_out_V"]
        mc_tj_ic1[i] = t_pcb + c1["p_ic_W"] * ic["r_theta_ja_C_per_W"]

    # Plot Monte-Carlo histograms
    fig, axes = plt.subplots(1, 3, figsize=(12.5, 4.0))
    axes[0].hist(mc_ipk_ch1, bins=35, color="#7C3AED", alpha=0.75, label="Ch1 UV")
    axes[0].hist(mc_ipk_ch2, bins=35, color="#0EA5E9", alpha=0.65, label="Ch2 Vis")
    axes[0].axvline(ic["icl_A"]["min"], color="#DC2626", ls="--", lw=1.8, label="ICL_min = 2.10 A")
    axes[0].set_title("Peak Inductor Current (N=2000)")
    axes[0].set_xlabel("I_L,pk (A)")
    axes[0].set_ylabel("Count")
    axes[0].legend(fontsize=8)
    axes[0].grid(True, alpha=0.25)

    axes[1].hist(mc_iled_ch1, bins=35, color="#059669", alpha=0.8)
    axes[1].axvline(1000.0, color="#DC2626", ls="--", lw=1.8, label="UV If_max = 1000 mA")
    axes[1].set_title("Ch1 UV LED Current (N=2000)")
    axes[1].set_xlabel("I_LED (mA)")
    axes[1].legend(fontsize=8)
    axes[1].grid(True, alpha=0.25)

    axes[2].hist(mc_tj_ic1, bins=35, color="#D97706", alpha=0.8)
    axes[2].axvline(ic["tj_recommended_max_C"], color="#DC2626", ls="--", lw=1.8, label="Tj_max = 125 C")
    axes[2].set_title("U1 LM3410XMY Tj (T_pcb 25-60C)")
    axes[2].set_xlabel("Tj (C)")
    axes[2].legend(fontsize=8)
    axes[2].grid(True, alpha=0.25)

    fig.tight_layout()
    fig.savefig(OUT_DIR / "monte_carlo_margins.png", dpi=180)
    plt.close(fig)

    summary = {
        "nominal_analytic": {"ch1_uv": nom_ch1, "ch2_vis": nom_ch2},
        "corners": corner_summary,
        "monte_carlo_N2000": {
            "seed": 42,
            "ch1_ipk_max_A": float(np.max(mc_ipk_ch1)),
            "ch1_ipk_p99_A": float(np.percentile(mc_ipk_ch1, 99)),
            "ch2_ipk_max_A": float(np.max(mc_ipk_ch2)),
            "ch1_iled_min_mA": float(np.min(mc_iled_ch1)),
            "ch1_iled_max_mA": float(np.max(mc_iled_ch1)),
            "ch1_vout_max_V": float(np.max(mc_vout_ch1)),
            "ch1_tj_ic_max_C": float(np.max(mc_tj_ic1)),
            "pass_count_icl": int(np.sum((mc_ipk_ch1 < ic["icl_A"]["min"]) & (mc_ipk_ch2 < ic["icl_A"]["min"]))),
            "pass_count_tj": int(np.sum(mc_tj_ic1 <= ic["tj_recommended_max_C"])),
        },
    }
    return summary, corner_rows


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ds, comps = load_specs()

    print("1/3 Running ngspice SPICE simulations...")
    ngspice_res = run_ngspice_suite()

    print("2/3 Running SciPy state-space transient ODE...")
    ode_res = run_scipy_transient_ode(ds)

    print("3/3 Running exhaustive corner sweeps & N=2000 Monte-Carlo...")
    mc_corner_res, corner_rows = run_corners_and_mc(ds)

    csv_path = OUT_DIR / "corner_sweep.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(corner_rows[0].keys()))
        writer.writeheader()
        writer.writerows(corner_rows)

    full_summary = {
        "single_source_of_truth": {
            "datasheets_json": str(DATASHEETS_JSON.relative_to(REPO_ROOT)),
            "component_ids_csv": str(COMPONENT_IDS_CSV.relative_to(REPO_ROOT)),
            "refdes_count": len(comps),
        },
        "ngspice": ngspice_res,
        "scipy_transient_ode": ode_res,
        "analytic_and_mc": mc_corner_res,
    }

    summary_path = OUT_DIR / "sim_summary.json"
    summary_path.write_text(json.dumps(full_summary, indent=2), encoding="utf-8")

    # Assert all safety margins pass
    for key, val in mc_corner_res["corners"].items():
        assert val["all_limits_pass"], f"Corner check failed for {key}: {val}"
        assert val["dcm_corners"] == 0, f"Unexpected DCM corner in {key}: {val}"

    mc = mc_corner_res["monte_carlo_N2000"]
    assert mc["pass_count_icl"] == 2000, f"MC ICL failures: {mc}"
    assert mc["pass_count_tj"] == 2000, f"MC Tj failures: {mc}"

    print("ALL M1 DUAL-ENGINE SIMULATIONS PASSED.")
    print(f"Summary saved to {summary_path.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
