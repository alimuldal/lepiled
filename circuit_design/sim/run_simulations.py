#!/usr/bin/env python3
"""
LepiLED DIY Maxi Switch — Dual-Engine Reproducible Circuit Simulation Suite

Single Source of Truth:
  - Reads component & datasheet limits from datasheets/datasheets_summary.json
  - Reads RefDes / nominal values from circuit_design/COMPONENT_IDS.csv

Engine 1 (ngspice SPICE):
  - Executes circuit_design/sim/netlists/lepiled_nominal.cir (9.5 ms: OFF -> 4-UV -> 8-ALL -> 4-UV)
  - Executes circuit_design/sim/netlists/lepiled_fault_open_led.cir (worst-case BZT52C18 19.1V open-load OVP)
  - Executes circuit_design/sim/netlists/lepiled_fault_input_prot.cir (IC=0 cold plug, -12V rev, +12V stiff & 4A-limited, 5->12V step)
  - Parses logs & wrdata traces, verifies assertions, saves ngspice_transient_modes.png

Engine 2 (Python / SciPy):
  - Switched-averaged state-space ODE (scipy.integrate.solve_ivp) across 9.5 ms (OFF -> 4-UV -> 8-ALL -> 4-UV)
    with 2.0 ms DIM2 discharge tau (R6+R7) and LM3410 soft-start/ICL clamp
  - Exhaustive worst-case corner sweep across datasheet & OOS tolerances including explicit Tj <= 125 C gate (T_PCB = 55 C)
  - Input-path droop verification (V_USB = 4.75 V full-path droop & V_IC = 4.50 V direct droop vs F1 I_hold)
  - N = 2000 seeded (seed=42) Monte-Carlo sampling full [4.5, 5.5] V and [0.17, 0.33] Ohm ranges
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
        raise RuntimeError("ngspice binary not found")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    results = {"status": "executed", "binary": str(ngspice), "runs": {}}

    for name, netlist in [
        ("nominal", NETLIST_DIR / "lepiled_nominal.cir"),
        ("fault_open_led", NETLIST_DIR / "lepiled_fault_open_led.cir"),
        ("fault_input_prot", NETLIST_DIR / "lepiled_fault_input_prot.cir"),
        ("fault_ovp_sweep", NETLIST_DIR / "lepiled_fault_ovp_sweep.cir"),
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

    # Verify ngspice pass/fail invariants
    nom_m = results["runs"]["nominal"]["measurements"]
    assert nom_m["dim2_end"] < 0.4, f"U2 DIM2_NET failed to discharge < 0.4V: {nom_m['dim2_end']}"
    assert abs(nom_m["il2_end_avg"]) < 1e-3, f"U2 L2 DC current did not stop: {nom_m['il2_end_avg']}"
    assert nom_m["i_vis_backfeed"] < 1e-6, f"4-UV steady backfeed >= 1uA: {nom_m['i_vis_backfeed']}"
    assert nom_m["i_vis_end"] < 1.5e-3, f"U2 C5 passive tail did not decay below 1.5 mA by 9.5ms: {nom_m['i_vis_end']}"

    ovp_m = results["runs"]["fault_open_led"]["measurements"]
    assert ovp_m["vout1_open_peak"] < 24.0, f"Open-load OVP VOUT1 exceeded 24V: {ovp_m['vout1_open_peak']}"
    assert ovp_m["vsw_open_peak"] < 24.0, f"Open-load OVP VSW exceeded 24V: {ovp_m['vsw_open_peak']}"

    prot_m = results["runs"]["fault_input_prot"]["measurements"]
    assert prot_m["cold_iin_pk"] < 3.0, f"Cold hot-plug I_in_pk >= 3A: {prot_m['cold_iin_pk']}"
    assert prot_m["cold_il1_pk"] < 3.0, f"Cold hot-plug I_L1_pk >= 3A Isat: {prot_m['cold_il1_pk']}"
    assert prot_m["cold_il2_pk"] < 3.0, f"Cold hot-plug I_L2_pk >= 3A Isat: {prot_m['cold_il2_pk']}"
    assert abs(prot_m["rev12_iin_ss"]) < 1e-3, f"-12V reverse current >= 1mA: {prot_m['rev12_iin_ss']}"
    assert abs(prot_m["rev16_iin_ss"]) < 1e-3, f"-16V reverse current >= 1mA: {prot_m['rev16_iin_ss']}"
    assert prot_m["ov12_stiff_vin_pk"] < 7.0, f"+12V stiff VIN_PROT >= 7V: {prot_m['ov12_stiff_vin_pk']}"
    assert prot_m["ov12_4a_vin_pk"] < 7.0, f"+12V 4A-limited VIN_PROT >= 7V: {prot_m['ov12_4a_vin_pk']}"
    assert prot_m["ov16_stiff_vin_pk"] < 7.0, f"+16V stiff VIN_PROT >= 7V: {prot_m['ov16_stiff_vin_pk']}"
    for r_key in ["ov16_pr12_w", "ov16_pr13_w", "ov16_pr14_w", "ov16_pr15_w", "ov16_pr16_w", "ov16_pr17_w", "ov16_pr19_w"]:
        assert prot_m[r_key] <= 0.050, f"+16V resistor {r_key} exceeded 50 mW: {prot_m[r_key]}"

    swp_m = results["runs"]["fault_ovp_sweep"]["measurements"]
    assert swp_m["hold55_85c_vin_ss"] > 5.0, f"5.5V @ 85C hold ON failed: {swp_m['hold55_85c_vin_ss']}"
    for v_tag in ["60", "62", "64", "66", "67", "68", "69", "70", "12", "15", "16"]:
        assert swp_m[f"sw{v_tag}_vp_pk"] < 7.0, f"OVP sweep {v_tag} VIN_PROT >= 7V: {swp_m[f'sw{v_tag}_vp_pk']}"
        assert swp_m[f"sw{v_tag}_pd11_pk"] < 0.050, f"OVP sweep {v_tag} P(D11) >= 50mW: {swp_m[f'sw{v_tag}_pd11_pk']}"
    assert swp_m["step_5to12_vin_pk"] < 7.0, f"5.5->12V step VIN_PROT >= 7V: {swp_m['step_5to12_vin_pk']}"
    assert swp_m["step_5to12_vin_ss"] < 1e-3, f"5.5->12V step failed to cut off: {swp_m['step_5to12_vin_ss']}"
    assert swp_m["step_5to12_vgs_min"] > -8.0, f"5.5->12V Vgs exceeded -8V: {swp_m['step_5to12_vgs_min']}"
    assert swp_m["step_5to16_vin_pk"] < 7.0, f"5.5->16V step VIN_PROT >= 7V: {swp_m['step_5to16_vin_pk']}"
    assert swp_m["step_5to16_vin_ss"] < 1e-3, f"5.5->16V step failed to cut off: {swp_m['step_5to16_vin_ss']}"
    assert swp_m["step_5to16_vgs_min"] > -8.0, f"5.5->16V Vgs exceeded -8V: {swp_m['step_5to16_vgs_min']}"

    # Plot ngspice nominal trace
    trace_path = OUT_DIR / "ngspice_nominal_trace.txt"
    if trace_path.exists():
        data = np.loadtxt(trace_path, skiprows=1)
        t_ms = data[:, 0] * 1e3
        step = max(1, len(t_ms) // 5000)
        td = t_ms[::step]

        fig, axes = plt.subplots(3, 1, figsize=(10.5, 8.0), sharex=True)
        axes[0].plot(td, data[::step, 2], label="EN1_NET (U1.DIM)", color="#047857", lw=1.3)
        axes[0].plot(td, data[::step, 3], label="DIM2_NET (U2.DIM, tau_dis=2.0ms)", color="#2563EB", lw=1.3)
        axes[0].axhline(1.8, color="#64748B", ls="--", lw=0.9, label="VDIM_H = 1.8 V")
        axes[0].axhline(0.4, color="#94A3B8", ls=":", lw=0.9, label="VDIM_L = 0.4 V")
        axes[0].set_ylabel("Enable (V)")
        axes[0].set_title("ngspice 45.2 Cycle-by-Cycle Transient (9.5 ms): OFF -> 4-UV -> 8-ALL -> 4-UV")
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
    """Solve steady-state CCM/DCM boost converter equations per TI LM3410 SNVS541H with exact energy conservation."""
    i_led = vfb / r_sense
    v_str = vstr_at_350mA + (i_led - 0.350) * rdyn_str
    v_out = v_str + vfb

    p_led = v_str * i_led
    p_rsense = (i_led**2) * r_sense
    p_diode = vd * i_led
    p_q = vin_ic * iq

    d = (v_out + vd - vin_ic) / (v_out + vd)
    i_l_avg = i_led / max(1.0 - d, 0.04)

    for _ in range(40):
        v_drop = i_l_avg * (dcr + d * rds)
        d = min(max((v_out + vd - vin_ic + v_drop) / (v_out + vd), 0.05), 0.95)
        di_l_pp = max((vin_ic - i_l_avg * (dcr + rds)) * d / (L * fsw), 0.0)
        i_l_rms = math.sqrt(i_l_avg**2 + (di_l_pp**2) / 12.0)
        i_sw_rms = math.sqrt(d) * i_l_rms
        p_cond = (i_sw_rms**2) * rds
        p_ind = (i_l_rms**2) * dcr
        p_sw = 0.5 * v_out * i_l_avg * fsw * ((tr_ns + tf_ns) * 1e-9)
        p_stage = p_led + p_rsense + p_diode + p_ind + p_cond + p_sw
        i_l_avg_new = p_stage / vin_ic
        if abs(i_l_avg_new - i_l_avg) < 1e-12:
            i_l_avg = i_l_avg_new
            break
        i_l_avg = 0.5 * i_l_avg + 0.5 * i_l_avg_new

    di_l_pp = (vin_ic - i_l_avg * (dcr + rds)) * d / (L * fsw)
    i_l_pk = i_l_avg + 0.5 * di_l_pp
    i_l_min = i_l_avg - 0.5 * di_l_pp
    is_ccm = i_l_min > 0.0

    # Exact power-conserving RMS & loss breakdown (TI Sec. 10.3.3 Eqs. 40-50)
    i_l_rms = math.sqrt(i_l_avg**2 + (di_l_pp**2) / 12.0)
    i_sw_rms = math.sqrt(d) * i_l_rms
    p_cond = (i_sw_rms**2) * rds
    p_sw = 0.5 * v_out * i_l_avg * fsw * ((tr_ns + tf_ns) * 1e-9)
    p_ic = p_cond + p_sw + p_q
    p_ind = (i_l_rms**2) * dcr
    p_in_ch = p_led + p_rsense + p_ic + p_diode + p_ind
    i_in_avg = p_in_ch / vin_ic
    eta = p_led / p_in_ch

    # Output ripple voltage: capacitor charge/discharge + peak inductor current * ESR
    dv_out_pp = (i_led * d) / (c_out_eff * fsw) + i_l_pk * esr_out

    return {
        "i_led_A": i_led,
        "v_str_V": v_str,
        "v_out_V": v_out,
        "duty": d,
        "ccm": is_ccm,
        "i_in_avg_A": i_in_avg,
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
    """State-space averaged transient ODE across 9.5 ms: OFF -> 4-UV -> 8-ALL -> 4-UV."""
    ic = ds["boost_ic"]["LM3410XMY/NOPB"]
    ind = ds["inductor"]["SRN6045-100M"]
    cap_out = ds["capacitors"]["CL32B106KBJNFNE"]
    res_s = ds["resistors"]["CRL1206-FW-R560ELF"]
    uv = ds["leds"]["SST-10-UV-A130-G365-00"]
    rb = ds["leds"]["XPEBRY-L1-0000-00S02"]
    gr = ds["leds"]["XPEBGR-L1-0000-00K01"]
    cw = ds["leds"]["XPEBWT-L1-0000-00H51"]
    mos = ds["protection_and_input"]["DMG2305UX-7"]
    ptc = ds["protection_and_input"]["MF-LSMF500/16X"]
    usb = ds["protection_and_input"]["USB4085-GF-A"]

    L = ind["L_H"]
    dcr = ind["dcr_typ_ohm"]
    c_out = cap_out["effective_capacitance_at_16V_F"]
    r_s = res_s["resistance_ohm"]
    vfb = ic["vfb_V"]["typ"]
    rds = ic["rds_on_ohm"]["typ_25C"]
    vd = ds["schottky_diode"]["B340A-13-F"]["vf_V"]["at_1A_25C_typ"]
    icl_typ = ic["icl_A"]["typ"]

    # Input path impedance: 18 AWG 1m cable (0.022) + J1 (0.040) + F1 MF-LSMF500/16X (0.015) + Q1A+Q1B (0.080)
    r_in_path = (
        0.022
        + usb["contact_resistance_mohm"]["initial"] * 1e-3
        + 0.015
        + 2.0 * mos["rds_on_ohm"]["at_4V5_typ"]
    )
    v_usb = 5.0

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
        dv = v_out - v_th
        return 0.15 * np.logaddexp(0.0, dv / 0.15) / r_dyn

    def switch_mode(t: float) -> tuple[float, float]:
        # OFF (0..0.2ms) -> 4-UV (0.2..1.5ms) -> 8-ALL (1.5..3.5ms) -> 4-UV (3.5..9.5ms)
        if t < 0.2e-3:
            return 0.0, 0.0
        elif t < 1.5e-3:
            return 1.0, 0.0
        elif t < 3.5e-3:
            return 1.0, 1.0
        else:
            return 1.0, 0.0

    # State: [i_L1, v_C4, d1_int, ss1, i_L2, v_C5, d2_int, ss2, v_dim2]
    tau_chg = 10e3 * 100e-9   # R7 * C6 = 1.0 ms (when SW1 drives EN2_NET)
    tau_dis = 20e3 * 100e-9   # (R7 + R6) * C6 = 2.0 ms (when SW1 opens EN2_NET)

    def rhs(t: float, y: np.ndarray) -> np.ndarray:
        i_l1, v_c4, d1, ss1, i_l2, v_c5, d2, ss2, v_dim2 = y
        sw_uv, sw_all = switch_mode(t)

        i_in_est = max(i_l1, 0.0) + max(i_l2, 0.0)
        vin_prot = v_usb - i_in_est * r_in_path
        v_en1 = vin_prot - 0.65 if (sw_uv > 0.5 or sw_all > 0.5) else 0.0
        v_en2_src = vin_prot if sw_all > 0.5 else 0.0

        # Exact R7/C6/R6 charge (tau=1.0 ms) and open-switch discharge (tau=2.0 ms)
        dv_dim2 = (v_en2_src - v_dim2) / tau_chg if sw_all > 0.5 else -(v_dim2 / tau_dis)

        en1 = 1.0 if v_en1 >= ic["vdim_high_min_V"] else 0.0
        en2 = 1.0 if v_dim2 >= ic["vdim_high_min_V"] else 0.0

        # Soft-start ramp (0..1 over ~0.15 ms) limiting peak cycle current below ICL_typ
        dss1 = (1.0 - ss1) / 1.0e-4 if en1 > 0.5 else -ss1 / 1.0e-5
        dss2 = (1.0 - ss2) / 1.0e-4 if en2 > 0.5 else -ss2 / 1.0e-5
        icl_eff1 = max(0.35, ss1 * icl_typ)
        icl_eff2 = max(0.35, ss2 * icl_typ)

        i_led1 = led_current(v_c4, v_th_uv, r_dyn_uv)
        i_led2 = led_current(v_c5, v_th_vis, r_dyn_vis)

        v_fb1 = i_led1 * r_s
        v_fb2 = i_led2 * r_s

        # Outer loop with soft-start / ICL duty limit (prevents unphysical current spike)
        d_raw1 = np.clip(d1 + 2.0 * (vfb - v_fb1), 0.05, ic["dmax"]["typ"]) if en1 > 0.5 else 0.0
        d_raw2 = np.clip(d2 + 2.0 * (vfb - v_fb2), 0.05, ic["dmax"]["typ"]) if en2 > 0.5 else 0.0
        d_cmd1 = d_raw1 * (1.0 / (1.0 + math.exp(25.0 * (i_l1 - icl_eff1 * 0.85)))) if en1 > 0.5 else 0.0
        d_cmd2 = d_raw2 * (1.0 / (1.0 + math.exp(25.0 * (i_l2 - icl_eff2 * 0.85)))) if en2 > 0.5 else 0.0

        dd1 = 12000.0 * (vfb - v_fb1) if (en1 > 0.5 and i_l1 < icl_eff1 * 0.85) else (-15000.0 * d1 if en1 < 0.5 else 0.0)
        dd2 = 12000.0 * (vfb - v_fb2) if (en2 > 0.5 and i_l2 < icl_eff2 * 0.85) else (-15000.0 * d2 if en2 < 0.5 else 0.0)

        if en1 > 0.5:
            di_l1 = (vin_prot - i_l1 * (dcr + d_cmd1 * rds) - (1.0 - d_cmd1) * (v_c4 + vd)) / L
            i_out1 = (1.0 - d_cmd1) * i_l1
        else:
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

        return np.array([di_l1, dv_c4, dd1, dss1, di_l2, dv_c5, dd2, dss2, dv_dim2])

    y0 = np.array([0.0, 4.7, 0.0, 0.0, 0.0, 4.7, 0.0, 0.0, 0.0])
    t_eval = np.linspace(0.0, 9.5e-3, 9501)
    sol = solve_ivp(rhs, (0.0, 9.5e-3), y0, method="Radau", t_eval=t_eval, rtol=1e-6, atol=1e-8)
    assert sol.success, f"ODE solver failed: {sol.message}"

    t = sol.t
    i_l1, v_c4, _, _, i_l2, v_c5, _, _, v_dim2 = sol.y
    i_led1 = np.array([led_current(v, v_th_uv, r_dyn_uv) for v in v_c4])
    i_led2 = np.array([led_current(v, v_th_vis, r_dyn_vis) for v in v_c5])
    i_in_tot = np.maximum(i_l1, 0.0) + np.maximum(i_l2, 0.0)

    m_4uv = (t >= 1.1e-3) & (t <= 1.45e-3)
    m_8all = (t >= 3.1e-3) & (t <= 3.45e-3)
    m_end = (t >= 9.0e-3) & (t <= 9.5e-3)

    dim2_end = float(np.mean(v_dim2[m_end]))
    i_vis_end_mA = float(np.min(i_led2[m_end]) * 1e3)
    i_vis_backfeed_mA = float(np.max(i_led2[m_4uv]) * 1e3)
    assert dim2_end < 0.4, f"SciPy DIM2_NET failed to discharge < 0.4V: {dim2_end}"
    assert i_vis_backfeed_mA < 1e-3, f"SciPy 4-UV backfeed >= 1uA: {i_vis_backfeed_mA} mA"
    assert i_vis_end_mA < 1.0, f"SciPy I_VIS C5 tail did not decay < 1 mA by 9.5ms: {i_vis_end_mA} mA"

    # Plot SciPy transient ODE
    fig, axes = plt.subplots(3, 1, figsize=(10.5, 8.0), sharex=True)
    axes[0].plot(t * 1e3, v_dim2, label="DIM2_NET (tau_chg=1.0ms, tau_dis=2.0ms)", color="#2563EB", lw=1.5)
    axes[0].axhline(1.8, color="#64748B", ls="--", lw=0.9, label="VDIM_H = 1.8 V")
    axes[0].axhline(0.4, color="#94A3B8", ls=":", lw=0.9, label="VDIM_L = 0.4 V")
    axes[0].set_ylabel("DIM2 (V)")
    axes[0].set_title("SciPy Radau State-Space Transient ODE (9.5 ms): OFF -> 4-UV -> 8-ALL -> 4-UV")
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
        "iin_peak_A": float(np.max(i_in_tot)),
        "dim2_cross_1p8V_ms": float(t[np.argmax(v_dim2 >= 1.8)] * 1e3),
        "dim2_end_V": dim2_end,
        "i_vis_end_mA": i_vis_end_mA,
    }


def solve_usb_path_droop(
    v_usb: float,
    r_cable: float,
    r_j1: float,
    r_f1: float,
    r_q1_pair: float,
    ds: dict,
    worst_boost: bool = False,
    worst_leds: bool = False,
) -> dict:
    """Self-consistent 8-ALL input-path droop & F1 hold-current verification."""
    ic = ds["boost_ic"]["LM3410XMY/NOPB"]
    ind = ds["inductor"]["SRN6045-100M"]
    sch = ds["schottky_diode"]["B340A-13-F"]
    res_s = ds["resistors"]["CRL1206-FW-R560ELF"]
    cap_out = ds["capacitors"]["CL32B106KBJNFNE"]
    uv = ds["leds"]["SST-10-UV-A130-G365-00"]
    rb = ds["leds"]["XPEBRY-L1-0000-00S02"]
    gr = ds["leds"]["XPEBGR-L1-0000-00K01"]
    cw = ds["leds"]["XPEBWT-L1-0000-00H51"]

    r_path = r_cable + r_j1 + r_f1 + r_q1_pair
    L = ind["L_min_H"] if worst_boost else ind["L_H"]
    dcr = ind["dcr_max_ohm"] * 1.30 if worst_boost else ind["dcr_typ_ohm"]
    rds = ic["rds_on_ohm"]["max"] if worst_boost else ic["rds_on_ohm"]["typ_25C"]
    vd = sch["vf_V"]["at_3A_25C_max"] if worst_boost else sch["vf_V"]["at_1A_25C_typ"]
    vfb = ic["vfb_V"]["max"] if worst_boost else ic["vfb_V"]["typ"]
    fsw_loss = ic["fsw_Hz"]["max"] if worst_boost else ic["fsw_Hz"]["typ"]
    fsw_pk = ic["fsw_Hz"]["min"] if worst_boost else ic["fsw_Hz"]["typ"]
    iq = ic["iq_switching_mA"]["max"] * 1e-3 if worst_boost else ic["iq_switching_mA"]["typ"] * 1e-3
    r_sense = res_s["resistance_ohm"] * (0.99 if worst_boost else 1.0)
    vstr_uv = 16.0 if worst_leds else 4.0 * uv["vf_at_350mA_25C_V"]["typ"]
    vstr_vis = 13.5 if worst_leds else (2.0 * rb["vf_at_350mA_25C_V"]["typ"] + gr["vf_at_350mA_25C_V"]["typ"] + cw["vf_at_350mA_25C_V"]["typ"])
    rdyn_uv = 4.0 * uv["rdyn_ohm_per_led"]
    rdyn_vis = 2.0 * rb["rdyn_ohm_per_led"] + gr["rdyn_ohm_per_led"] + cw["rdyn_ohm_per_led"]

    vin_prot = v_usb - 0.25
    for _ in range(40):
        c1 = solve_steady_boost(
            vin_prot, L, r_sense, vstr_uv, rdyn_uv, vfb, fsw_loss, rds, dcr, vd,
            cap_out["effective_capacitance_at_16V_F"], cap_out["esr_ohm"],
            iq, ic["t_rise_ns"], ic["t_fall_ns"],
        )
        c2 = solve_steady_boost(
            vin_prot, L, r_sense, vstr_vis, rdyn_vis, vfb, fsw_loss, rds, dcr, vd,
            cap_out["effective_capacitance_at_16V_F"], cap_out["esr_ohm"],
            iq, ic["t_rise_ns"], ic["t_fall_ns"],
        )
        i_in = c1["i_in_avg_A"] + c2["i_in_avg_A"]
        vin_prot = v_usb - i_in * r_path

    # Evaluate worst-case peak inductor current at fsw_pk
    c1_pk = solve_steady_boost(
        vin_prot, L, r_sense, vstr_uv, rdyn_uv, vfb, fsw_pk, rds, dcr, vd,
        cap_out["effective_capacitance_at_16V_F"], cap_out["esr_ohm"],
        iq, ic["t_rise_ns"], ic["t_fall_ns"],
    )
    c2_pk = solve_steady_boost(
        vin_prot, L, r_sense, vstr_vis, rdyn_vis, vfb, fsw_pk, rds, dcr, vd,
        cap_out["effective_capacitance_at_16V_F"], cap_out["esr_ohm"],
        iq, ic["t_rise_ns"], ic["t_fall_ns"],
    )

    return {
        "v_usb_V": v_usb,
        "r_path_ohm": round(r_path, 4),
        "vin_prot_V": round(vin_prot, 3),
        "i_usb_A": round(i_in, 3),
        "p_usb_total_W": round(v_usb * i_in, 3),
        "ch1_ipk_A": round(c1_pk["i_l_pk_A"], 3),
        "ch2_ipk_A": round(c2_pk["i_l_pk_A"], 3),
        "ch1_tj_55C_C": round(55.0 + c1["p_ic_W"] * ic["r_theta_ja_C_per_W"], 2),
        "p_f1_W": round((i_in**2) * r_f1, 3),
        "p_q1_pair_W": round((i_in**2) * r_q1_pair, 3),
        "p_pcb_passives_W": round((i_in**2) * (r_f1 + r_q1_pair) + c1["p_rsense_W"] + c2["p_rsense_W"], 3),
    }


def run_corners_and_mc(ds: dict) -> tuple[dict, list[dict]]:
    ic = ds["boost_ic"]["LM3410XMY/NOPB"]
    ind = ds["inductor"]["SRN6045-100M"]
    sch = ds["schottky_diode"]["B340A-13-F"]
    res_s = ds["resistors"]["CRL1206-FW-R560ELF"]
    cap_out = ds["capacitors"]["CL32B106KBJNFNE"]
    uv = ds["leds"]["SST-10-UV-A130-G365-00"]
    rb = ds["leds"]["XPEBRY-L1-0000-00S02"]
    gr = ds["leds"]["XPEBGR-L1-0000-00K01"]
    cw = ds["leds"]["XPEBWT-L1-0000-00H51"]
    ptc = ds["protection_and_input"]["MF-LSMF500/16X"]
    mos = ds["protection_and_input"]["DMG2305UX-7"]
    usb = ds["protection_and_input"]["USB4085-GF-A"]

    L_nom = ind["L_H"]
    L_tol = ind["tolerance_fraction"]
    r_nom = res_s["resistance_ohm"]
    vfb_nom = ic["vfb_V"]["typ"]
    c_out_eff = cap_out["effective_capacitance_at_16V_F"]
    esr = cap_out["esr_ohm"]
    tr, tf = ic["t_rise_ns"], ic["t_fall_ns"]
    t_pcb_max_C = 55.0

    # Nominal steady-state at typ 5.0 V USB (18 AWG 1.0 m cable + J1 + F1 + Q1A/Q1B -> R_path = 0.157 Ohm)
    nom_droop = solve_usb_path_droop(
        5.0, 0.022, usb["contact_resistance_mohm"]["initial"] * 1e-3,
        0.015, 2.0 * mos["rds_on_ohm"]["at_4V5_typ"], ds, worst_boost=False, worst_leds=False,
    )
    vin_ic_nom = nom_droop["vin_prot_V"]

    vstr_uv_nom = 4.0 * uv["vf_at_350mA_25C_V"]["typ"]
    vstr_vis_nom = 2.0 * rb["vf_at_350mA_25C_V"]["typ"] + gr["vf_at_350mA_25C_V"]["typ"] + cw["vf_at_350mA_25C_V"]["typ"]
    rdyn_uv = 4.0 * uv["rdyn_ohm_per_led"]
    rdyn_vis = 2.0 * rb["rdyn_ohm_per_led"] + gr["rdyn_ohm_per_led"] + cw["rdyn_ohm_per_led"]

    nom_ch1 = solve_steady_boost(
        vin_ic=vin_ic_nom, L=L_nom, r_sense=r_nom, vstr_at_350mA=vstr_uv_nom, rdyn_str=rdyn_uv,
        vfb=vfb_nom, fsw=ic["fsw_Hz"]["typ"], rds=ic["rds_on_ohm"]["typ_25C"],
        dcr=ind["dcr_typ_ohm"], vd=sch["vf_V"]["at_1A_25C_typ"],
        c_out_eff=c_out_eff, esr_out=esr, iq=ic["iq_switching_mA"]["typ"] * 1e-3,
        tr_ns=tr, tf_ns=tf,
    )
    nom_ch2 = solve_steady_boost(
        vin_ic=vin_ic_nom, L=L_nom, r_sense=r_nom, vstr_at_350mA=vstr_vis_nom, rdyn_str=rdyn_vis,
        vfb=vfb_nom, fsw=ic["fsw_Hz"]["typ"], rds=ic["rds_on_ohm"]["typ_25C"],
        dcr=ind["dcr_typ_ohm"], vd=sch["vf_V"]["at_1A_25C_typ"],
        c_out_eff=c_out_eff, esr_out=esr, iq=ic["iq_switching_mA"]["typ"] * 1e-3,
        tr_ns=tr, tf_ns=tf,
    )

    # Reconciled input-path droop scenarios (8-ALL mode) — zero uncovered V_IC gap
    droop_checks = {
        "usb_5p0V_typ_18AWG_1m_usbc": solve_usb_path_droop(5.0, 0.022, 0.040, 0.015, 0.080, ds, worst_boost=False, worst_leds=False),
        "usb_4p85V_ds_worst_18AWG_1m_captive": solve_usb_path_droop(4.85, 0.022, 0.0, ptc["r_1max_ohm"], 2.0 * mos["rds_on_ohm"]["at_4V5_max"], ds, worst_boost=True, worst_leds=True),
        "usb_4p90V_ds_worst_18AWG_0p8m_usbc": solve_usb_path_droop(4.90, 0.018, 0.050, ptc["r_1max_ohm"], 2.0 * mos["rds_on_ohm"]["at_4V5_max"], ds, worst_boost=True, worst_leds=True),
        "usb_4p75V_typLED_20AWG_1m_usbc": solve_usb_path_droop(4.75, 0.040, 0.050, ptc["r_1max_ohm"], 2.0 * mos["rds_on_ohm"]["at_4V5_max"], ds, worst_boost=True, worst_leds=False),
        "vic_4p25V_ds_worst_direct": solve_usb_path_droop(4.25, 0.0, 0.0, 0.0, 0.0, ds, worst_boost=True, worst_leds=True),
    }
    for d_key in ["usb_4p85V_ds_worst_18AWG_1m_captive", "usb_4p90V_ds_worst_18AWG_0p8m_usbc", "usb_4p75V_typLED_20AWG_1m_usbc"]:
        dc = droop_checks[d_key]
        assert dc["i_usb_A"] < ptc["ihold_55C_A"], f"{d_key} exceeds F1 Ihold@55C ({ptc['ihold_55C_A']}A): {dc}"
        assert dc["i_usb_A"] < ptc["ihold_60C_A"], f"{d_key} exceeds F1 Ihold@60C ({ptc['ihold_60C_A']}A): {dc}"
        assert dc["ch1_ipk_A"] < ic["icl_A"]["min"], f"{d_key} exceeds ICL_min: {dc}"
        assert dc["ch1_tj_55C_C"] <= ic["tj_recommended_max_C"], f"{d_key} exceeds Tj 125C: {dc}"
    assert droop_checks["vic_4p25V_ds_worst_direct"]["ch1_ipk_A"] < ic["icl_A"]["min"]
    assert droop_checks["vic_4p25V_ds_worst_direct"]["ch1_tj_55C_C"] <= ic["tj_recommended_max_C"]

    # Exhaustive corner sweep across 3 scenarios (datasheet_spec explicitly includes V_IC_min = 4.25 V & 4.38 V!)
    scenarios = [
        ("datasheet_spec", [4.25, 4.38, 4.50, 5.00, 5.50], [ic["vfb_V"]["min"], vfb_nom, ic["vfb_V"]["max"]], [r_nom * 0.99, r_nom, r_nom * 1.01], ic["tj_recommended_max_C"]),
        ("oos_vfb_10pct_r_5pct", [4.50, 5.00, 5.50], [vfb_nom * 0.90, vfb_nom, vfb_nom * 1.10], [r_nom * 0.95, r_nom, r_nom * 1.05], ic["tj_recommended_max_C"]),
        ("oos_vfb_15pct_r_5pct", [4.50, 5.00, 5.50], [vfb_nom * 0.85, vfb_nom, vfb_nom * 1.15], [r_nom * 0.95, r_nom, r_nom * 1.05], ic["tj_abs_max_C"]),
    ]

    corner_rows: list[dict] = []
    corner_summary: dict = {}

    for scen_name, vin_vals, vfb_vals, r_vals, tj_gate_C in scenarios:
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
                vin_vals,
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
                    vin == min(vin_vals)
                    and L == L_nom * (1.0 - L_tol)
                    and r_s == min(r_vals)
                    and vstr == max(vstr_vals)
                    and vfb == max(vfb_vals)
                    and fsw in (ic["fsw_Hz"]["min"], ic["fsw_Hz"]["max"])
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
                        "p_ind_mW": round(res["p_ind_W"] * 1e3, 1),
                        "p_diode_mW": round(res["p_diode_W"] * 1e3, 1),
                        "p_rsense_mW": round(res["p_rsense_W"] * 1e3, 1),
                        "tj_ic_at_55C": round(t_pcb_max_C + res["p_ic_W"] * ic["r_theta_ja_C_per_W"], 2),
                        "ccm": res["ccm"],
                    })

            max_tj_55C = t_pcb_max_C + max_pic * ic["r_theta_ja_C_per_W"]
            max_tj_60C = 60.0 + max_pic * ic["r_theta_ja_C_per_W"]
            key = f"{scen_name}__{ch_name}"
            corner_summary[key] = {
                "total_corners": tot,
                "vin_min_V": min(vin_vals),
                "dcm_corners": dcm_count,
                "max_i_l_pk_A": round(max_ipk, 4),
                "margin_vs_icl_min_A": round(ic["icl_A"]["min"] - max_ipk, 4),
                "max_duty": round(max_d, 4),
                "margin_vs_dmax_min": round(ic["dmax"]["min"] - max_d, 4),
                "max_i_led_mA": round(max_iled * 1e3, 2),
                "max_v_out_V": round(max_vout, 3),
                "max_p_ic_mW": round(max_pic * 1e3, 1),
                "max_tj_ic_55C_amb": round(max_tj_55C, 2),
                "max_tj_ic_60C_amb": round(max_tj_60C, 2),
                "tj_limit_C": tj_gate_C,
                "max_tpcb_for_125C_C": round(125.0 - max_pic * ic["r_theta_ja_C_per_W"], 2),
                "all_limits_pass": bool(
                    max_ipk < ic["icl_A"]["min"]
                    and max_d < ic["dmax"]["min"]
                    and max_iled < if_max
                    and max_vout < ic["vsw_recommended_V"]["max"]
                    and max_tj_55C <= tj_gate_C
                ),
            }

    # Seeded N = 2000 Monte-Carlo sampling FULL [4.25, 5.50] V and [0.17, 0.33] Ohm ranges, T_PCB in [25, 55] C
    rng = np.random.default_rng(42)
    N = 2000
    mc_ipk_ch1 = np.zeros(N)
    mc_ipk_ch2 = np.zeros(N)
    mc_iled_ch1 = np.zeros(N)
    mc_vout_ch1 = np.zeros(N)
    mc_tj_ic1 = np.zeros(N)

    for i in range(N):
        vin = rng.uniform(4.25, 5.50)
        L1 = np.clip(rng.normal(L_nom, L_nom * L_tol / 2.5), L_nom * 0.78, L_nom * 1.22)
        L2 = np.clip(rng.normal(L_nom, L_nom * L_tol / 2.5), L_nom * 0.78, L_nom * 1.22)
        r1 = rng.normal(r_nom, r_nom * 0.015)
        r2 = rng.normal(r_nom, r_nom * 0.015)
        vfb1 = np.clip(rng.normal(vfb_nom, vfb_nom * 0.045), 0.1615, 0.2185)
        vfb2 = np.clip(rng.normal(vfb_nom, vfb_nom * 0.045), 0.1615, 0.2185)
        fsw1 = np.clip(rng.normal(1.6e6, 0.12e6), 1.2e6, 2.0e6)
        fsw2 = np.clip(rng.normal(1.6e6, 0.12e6), 1.2e6, 2.0e6)
        vstr1 = rng.uniform(11.4, 16.0)
        vstr2 = rng.uniform(10.2, 13.5)
        rds1 = rng.uniform(0.17, 0.33)
        rds2 = rng.uniform(0.17, 0.33)
        vd = rng.uniform(0.30, 0.50)
        t_pcb = rng.uniform(25.0, t_pcb_max_C)

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
    axes[2].set_title("U1 LM3410XMY Tj (T_pcb 25-55C)")
    axes[2].set_xlabel("Tj (C)")
    axes[2].legend(fontsize=8)
    axes[2].grid(True, alpha=0.25)

    fig.tight_layout()
    fig.savefig(OUT_DIR / "monte_carlo_margins.png", dpi=180)
    plt.close(fig)

    summary = {
        "nominal_analytic": {"vin_ic_V": vin_ic_nom, "ch1_uv": nom_ch1, "ch2_vis": nom_ch2},
        "input_droop_checks": droop_checks,
        "corners": corner_summary,
        "monte_carlo_N2000": {
            "seed": 42,
            "vin_range_V": [4.25, 5.50],
            "rds_range_ohm": [0.17, 0.33],
            "t_pcb_range_C": [25.0, t_pcb_max_C],
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

    print("1/3 Running ngspice SPICE simulations (nominal 9.5ms, open-load OVP, input-prot faults)...")
    ngspice_res = run_ngspice_suite()

    print("2/3 Running SciPy state-space transient ODE (9.5ms, tau_dis=2.0ms)...")
    ode_res = run_scipy_transient_ode(ds)

    print("3/3 Running exhaustive corner sweeps, droop checks & N=2000 Monte-Carlo...")
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
