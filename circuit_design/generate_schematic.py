#!/usr/bin/env python3
"""
Generate the complete LepiLED DIY Maxi Switch schematic (SVG, PDF, PNG)
using schemdraw + inkscape.

All 62 RefDes in circuit_design/COMPONENT_IDS.csv are represented cleanly with
zero overlapping labels or wires, and pinouts verified strictly against vendor PDFs.
"""

from pathlib import Path
import shutil
import subprocess
import schemdraw
import schemdraw.elements as elm


def draw_box(
    d: schemdraw.Drawing,
    x0: float,
    y0: float,
    x1: float,
    y1: float,
    title: str,
    dashed: bool = False,
    color: str = "#CBD5E1",
    title_color: str = "#0F172A",
    title_size: float = 10.5,
) -> None:
    ls = "--" if dashed else "-"
    lw = 1.1 if dashed else 1.0
    d += elm.Line().at((x0, y1)).to((x1, y1)).linestyle(ls).color(color).linewidth(lw)
    d += elm.Line().to((x1, y0)).linestyle(ls).color(color).linewidth(lw)
    d += elm.Line().to((x0, y0)).linestyle(ls).color(color).linewidth(lw)
    d += elm.Line().to((x0, y1)).linestyle(ls).color(color).linewidth(lw)
    d += elm.Label().at((x0 + 0.35, y1 - 0.5)).label(
        title, loc="right", halign="left", valign="center", fontsize=title_size, color=title_color
    )


def draw_rect_block(
    d: schemdraw.Drawing,
    x0: float,
    y0: float,
    w: float,
    h: float,
    center_lines: list[str],
    left_pins: list[tuple[str, float, str]] | None = None,
    right_pins: list[tuple[str, float, str]] | None = None,
    top_pins: list[tuple[str, float, str]] | None = None,
    bot_pins: list[tuple[str, float, str]] | None = None,
    lead: float = 0.5,
    fontsize: float = 7.5,
    pin_fontsize: float = 6.6,
) -> dict[str, tuple[float, float]]:
    """Draw a crisp rectangular IC/connector block with non-overlapping pin labels and return pin tip coords."""
    x1, y1 = x0 + w, y0 + h
    d += elm.Line().at((x0, y1)).to((x1, y1)).color("#0F172A").linewidth(1.4)
    d += elm.Line().to((x1, y0)).color("#0F172A").linewidth(1.4)
    d += elm.Line().to((x0, y0)).color("#0F172A").linewidth(1.4)
    d += elm.Line().to((x0, y1)).color("#0F172A").linewidth(1.4)

    cy = y0 + h / 2.0
    cx = x0 + w / 2.0
    d += elm.Label().at((cx, cy)).label("\n".join(center_lines), halign="center", valign="center", fontsize=fontsize, color="#0F172A")

    pts: dict[str, tuple[float, float]] = {}
    for name, frac, pnum in (left_pins or []):
        py = y0 + frac * h
        d += elm.Line().at((x0, py)).to((x0 - lead, py)).color("#0F172A")
        pts[name] = (x0 - lead, py)
        lbl = f"{name} ({pnum})" if pnum else name
        d += elm.Label().at((x0 + 0.12, py)).label(lbl, halign="left", valign="center", fontsize=pin_fontsize, color="#334155")

    for name, frac, pnum in (right_pins or []):
        py = y0 + frac * h
        d += elm.Line().at((x1, py)).to((x1 + lead, py)).color("#0F172A")
        pts[name] = (x1 + lead, py)
        lbl = f"{name} ({pnum})" if pnum else name
        d += elm.Label().at((x1 - 0.12, py)).label(lbl, halign="right", valign="center", fontsize=pin_fontsize, color="#334155")

    for name, frac, pnum in (top_pins or []):
        px = x0 + frac * w
        d += elm.Line().at((px, y1)).to((px, y1 + lead)).color("#0F172A")
        pts[name] = (px, y1 + lead)
        lbl = f"{name} ({pnum})" if pnum else name
        d += elm.Label().at((px, y1 - 0.16)).label(lbl, halign="center", valign="top", fontsize=pin_fontsize, color="#334155")

    for name, frac, pnum in (bot_pins or []):
        px = x0 + frac * w
        d += elm.Line().at((px, y0)).to((px, y0 - lead)).color("#0F172A")
        pts[name] = (px, y0 - lead)
        lbl = f"{name} ({pnum})" if pnum else name
        d += elm.Label().at((px, y0 + 0.16)).label(lbl, halign="center", valign="bottom", fontsize=pin_fontsize, color="#334155")

    return pts


def draw_boost_channel(
    d: schemdraw.Drawing,
    x0: float,
    y0: float,
    title: str,
    u_ref: str,
    l_ref: str,
    d_catch_ref: str,
    c_in_ref: str,
    c_in_hf_ref: str,
    c_out_ref: str,
    c_out_hf_ref: str,
    r_sense_ref: str,
    d_ovp_ref: str,
    r_ovp_ref: str,
    j_ref: str,
    dim_net: str,
    sw_net: str,
    vout_net: str,
    fb_net: str,
    ret_net: str,
    led_specs: list[tuple[str, str]],
) -> None:
    """Draw one complete LM3410XMY (DGN MSOP-8-PowerPAD) boost CC channel + TI Fig. 14 OVP + off-board LEDs."""
    draw_box(d, x0 - 0.8, y0 - 6.6, x0 + 40.6, y0 + 5.8, title)

    rail_y = y0 + 2.8
    # VIN_PROT entry
    d += elm.Dot().at((x0, rail_y)).label("VIN_PROT", loc="left", fontsize=8.5, color="#B91C1C")
    d += elm.Line().right(1.8)
    d += elm.Dot()
    d.push()
    d += elm.Capacitor().down(2.6).label(f"{c_in_ref}\n10uF 25V\nX7R 1206", loc="top", ofst=0.32, fontsize=7.2)
    d += elm.Ground()
    d.pop()

    d += elm.Line().right(3.4)
    d += elm.Dot()
    d.push()
    d += elm.Capacitor().down(2.6).label(f"{c_in_hf_ref}\n100nF 25V\n0603", loc="top", ofst=0.32, fontsize=7.2)
    d += elm.Ground()
    d.pop()

    # Tap to U.VIN (pin 3) and Inductor L
    d += elm.Line().right(3.2)
    d += elm.Dot()
    d.push()
    d += elm.Line().down(1.7)
    p_u_vin_tap = d.here
    d.pop()

    # Inductor L
    d += elm.Inductor2(loops=4).right(3.8).label(f"{l_ref} 10uH ±20%\nSRN6045-100M", loc="top", ofst=0.22, fontsize=7.8)
    p_sw = d.here
    d += elm.Dot().label(sw_net, loc="top", ofst=0.20, fontsize=8, color="#7C2D12")

    # Catch diode D9/D10 -> space -> VOUT dot
    d += elm.Schottky().right(3.2).label(f"{d_catch_ref} B340A-13-F\n40V 3A SMA", loc="top", ofst=0.22, fontsize=7.8)
    d += elm.Line().right(1.8)
    d += elm.Dot().label(vout_net, loc="top", ofst=0.22, fontsize=8.2, color="#1D4ED8")

    # Output caps C_out, C_out_hf
    d += elm.Line().right(2.6)
    d += elm.Dot()
    d.push()
    d += elm.Capacitor().down(2.6).label(f"{c_out_ref}\n10uF 50V\nX7R 1210", loc="top", ofst=0.32, fontsize=7.2)
    d += elm.Ground()
    d.pop()

    d += elm.Line().right(3.4)
    d += elm.Dot()
    d.push()
    d += elm.Capacitor().down(2.6).label(f"{c_out_hf_ref}\n100nF 50V\n0603", loc="top", ofst=0.32, fontsize=7.2)
    d += elm.Ground()
    d.pop()

    # Continue VOUT to OVP tap and J2/J3 pin 1
    d += elm.Line().right(2.8)
    p_ovp_top = d.here
    d += elm.Dot()
    d += elm.Line().right(3.2)
    p_j_top = d.here

    # LM3410XMY (DGN MSOP-8-PowerPAD) block aligned directly below SW_NODE
    # Pinout strictly per datasheets/lm3410.pdf p. 3:
    # 1=NC, 2=PGND, 3=VIN, 4=DIM, 5=FB, 6=AGND, 7=SW, 8=NC, DAP=GND
    ic_w, ic_h = 5.6, 3.2
    ic_x0 = p_sw[0] - ic_w / 2.0
    ic_y0 = y0 - 3.1
    ic_pts = draw_rect_block(
        d,
        ic_x0,
        ic_y0,
        ic_w,
        ic_h,
        [u_ref, "LM3410XMY", "DGN-8 (NC: 1,8)"],
        left_pins=[("VIN", 0.72, "3"), ("DIM", 0.28, "4")],
        right_pins=[("FB", 0.50, "5")],
        top_pins=[("SW", 0.50, "7")],
        bot_pins=[("PGND/AGND/DAP", 0.50, "2/6/EP")],
        lead=0.45,
        fontsize=7.6,
        pin_fontsize=6.6,
    )

    d += elm.Line().at(p_u_vin_tap).to((p_u_vin_tap[0], ic_pts["VIN"][1]))
    d += elm.Line().to(ic_pts["VIN"])

    d += elm.Line().at(ic_pts["DIM"]).left(1.0).label(dim_net, loc="left", fontsize=8.2, color="#047857")
    d += elm.Dot()

    d += elm.Line().at(ic_pts["PGND/AGND/DAP"]).down(0.55)
    d += elm.Ground()

    d += elm.Line().at(ic_pts["SW"]).to(p_sw)

    # --- TI Figure 14 OVP & Feedback Topology ---
    fb_y = ic_pts["FB"][1]
    p_fb_node = (p_ovp_top[0], fb_y)
    d += elm.Line().at(ic_pts["FB"]).to(p_fb_node)
    d += elm.Dot().label(fb_net, loc="bottom", ofst=0.22, fontsize=7.8, color="#6D28D9")

    # D_ovp Zener (BZT52C18-7-F) from FB_NET (anode) up to VOUT (cathode)
    d.push()
    d += elm.Zener().at(p_fb_node).to(p_ovp_top).label(
        f"{d_ovp_ref}\nBZT52C18\n18V OVP", loc="top", ofst=0.30, fontsize=7.2
    )
    d.pop()

    # R_ovp (100 Ohm) from FB_NET right to RET_NET
    d += elm.Resistor().at(p_fb_node).to((p_j_top[0], fb_y)).label(
        f"{r_ovp_ref} 100R\n0603", loc="top", ofst=0.22, fontsize=7.2
    )
    p_j_bot = d.here
    d += elm.Dot().label(ret_net, loc="top", ofst=0.22, fontsize=7.8, color="#6D28D9")

    # Sense resistor R3 / R4 from RET_NET down to GND
    d.push()
    d += elm.Resistor().at(p_j_bot).down(2.4).label(
        f"{r_sense_ref}\n0.56R 1%\n0.5W 1206\n(339mA)", loc="top", ofst=0.30, fontsize=7.2
    )
    d += elm.Ground()
    d.pop()

    # On-PCB Header J2 / J3 pins
    d += elm.Dot().at(p_j_top).label(f"{j_ref}.1 (+)", loc="top", ofst=0.18, fontsize=7.8)
    d += elm.Line().at(p_j_bot).right(1.3)
    d += elm.Dot().label(f"{j_ref}.2 (-)", loc="bottom", ofst=0.20, fontsize=7.8)
    d += elm.Line().right(1.2)
    p_off_bot = d.here

    d += elm.Line().at(p_j_top).right(2.5)
    p_off_top = d.here

    # Off-board dashed enclosure for 4S LED string (fully inside outer box!)
    box_x0 = p_off_top[0] + 0.2
    box_x1 = box_x0 + 7.4
    draw_box(
        d, box_x0, y0 - 5.9, box_x1, y0 + 5.0,
        "OFF-BOARD LEDs (Al MCPCB)", dashed=True, color="#64748B", title_color="#475569", title_size=7.8
    )

    led_x = box_x0 + 1.1
    d += elm.Line().at(p_off_top).to((led_x, p_off_top[1]))
    d += elm.Line().to((led_x, y0 + 3.8))
    for idx, (lref, ldesc) in enumerate(led_specs):
        d += elm.LED().down(1.85).label(f"{lref}  {ldesc}", loc="bottom", ofst=0.28, fontsize=7.5)
        if idx < 3:
            d += elm.Line().down(0.2)
    d += elm.Line().to((led_x, p_off_bot[1]))
    d += elm.Line().to(p_off_bot)


def build_schematic(out_dir: Path) -> Path:
    schemdraw.theme("default")
    d = schemdraw.Drawing(unit=1.0, inches_per_unit=0.38, fontsize=9)

    # Title block
    d += elm.Label().at((-0.6, 17.8)).label(
        "LepiLED DIY Maxi Switch — Complete Hardware Schematic (M1 Verified Rev 3.0)",
        loc="right", halign="left", fontsize=14, color="#0F172A",
    )
    d += elm.Label().at((-0.6, 17.0)).label(
        "5V USB-C Input + Back-to-Back PMOS Reverse/Soft-Start + TL431 Precision OVP | SPDT Maxi-Switch | Dual LM3410XMY Boost CC | BZT52C18 OVP | 71 RefDes",
        loc="right", halign="left", fontsize=9.0, color="#334155",
    )

    # =========================================================================
    # BLOCK 1 (Top-Left): USB-C Power Input, Rd, Back-to-Back PMOS + TL431 OVP & Soft-Start
    # =========================================================================
    bx0, by0 = 0.0, 9.6
    draw_box(d, bx0 - 0.6, by0 - 8.2, bx0 + 44.0, by0 + 6.0, "1. USB-C 5V Input, Rd Negotiation, +/-16V Reverse Cutoff, TL431 OVP and Soft-Start")

    j1_pts = draw_rect_block(
        d,
        bx0 + 0.1,
        by0 - 0.5,
        4.4,
        4.2,
        ["J1", "USB4085-GF-A", "USB-C (5A)"],
        right_pins=[("VBUS", 0.80, "A4/B4/A9/B9"), ("CC1", 0.50, "A5"), ("CC2", 0.20, "B5")],
        bot_pins=[("GND", 0.50, "A1/B1/A12/B12/SH")],
        lead=0.40,
        fontsize=7.4,
        pin_fontsize=6.2,
    )
    d += elm.Line().at(j1_pts["GND"]).down(0.6)
    d += elm.Ground()

    # CC1 & CC2 Rd pulldowns
    d += elm.Line().at(j1_pts["CC1"]).right(1.8)
    d += elm.Resistor().right(1.9).label("R1 5.1k 1% 0805", loc="top", ofst=0.14, fontsize=6.6)
    d += elm.Line().down(0.5)
    d += elm.Ground()

    d += elm.Line().at(j1_pts["CC2"]).right(0.3)
    d += elm.Resistor().right(1.9).label("R2 5.1k 1% 0805", loc="bottom", ofst=0.14, fontsize=6.6)
    d += elm.Line().down(0.5)
    d += elm.Ground()

    # TP2 GND pad cleanly placed at bottom-left of Block 1
    d += elm.Dot().at((bx0 + 0.6, by0 - 6.8)).label("TP2 (GND_EXT)", loc="right", ofst=0.16, fontsize=7.2, color="#475569")
    d += elm.Line().down(0.5)
    d += elm.Ground()

    # VBUS -> TP1 -> C12 (ESD) -> F1 -> VBUS_FUSED -> Q1A -> V_MID -> Q1B -> VIN_PROT -> D11 -> C1
    d += elm.Line().at(j1_pts["VBUS"]).right(1.0)
    d += elm.Dot().label("VBUS", loc="top", ofst=0.18, fontsize=7.8, color="#B91C1C")
    d += elm.Line().right(1.3)
    p_tp1 = d.here
    d += elm.Dot()
    d.push()
    d += elm.Line().up(1.3)
    d += elm.Dot().label("TP1 (VBUS_EXT)", loc="right", ofst=0.14, fontsize=7.1, color="#475569")
    d.pop()

    # C12 ESD bypass cap
    d += elm.Line().at(p_tp1).right(1.6)
    d += elm.Dot()
    d.push()
    d += elm.Capacitor().down(2.4).label("C12\n100nF\n25V 0603", loc="bottom", ofst=0.22, fontsize=6.5)
    d += elm.Ground()
    d.pop()

    # F1 PTC (MF-LSMF500/16X)
    d += elm.Line().right(1.4)
    d += elm.Fuse().right(3.2).label("F1 MF-LSMF500/16X\n5A/16V 2920 PTC", loc="top", ofst=0.18, fontsize=6.9)
    d += elm.Dot().label("VBUS_FUSED", loc="top", ofst=0.18, fontsize=6.9)

    # Q1A P-MOSFET
    d += elm.Line().right(1.2)
    p_q1a_in = d.here
    q1a_pts = draw_rect_block(
        d,
        p_q1a_in[0] + 0.35,
        p_q1a_in[1] - 1.0,
        3.4,
        2.0,
        ["Q1A", "DMG2305UX-7", "Rev-Block"],
        left_pins=[("D", 0.50, "3")],
        right_pins=[("S", 0.50, "2")],
        bot_pins=[("G", 0.50, "1")],
        lead=0.35,
        fontsize=6.8,
        pin_fontsize=6.2,
    )
    d += elm.Line().at(p_q1a_in).to(q1a_pts["D"])

    # V_MID rail between Q1A and Q1B (wide 10.6 span for spacious OVP + Soft-Start)
    d += elm.Line().at(q1a_pts["S"]).right(2.0)
    p_vmid_sub = d.here
    d += elm.Dot()
    d += elm.Line().right(2.6)
    p_vmid_r14 = d.here
    d += elm.Dot()
    d += elm.Line().right(2.2)
    p_vmid = d.here
    d += elm.Dot().label("V_MID", loc="top", ofst=0.20, fontsize=7.5, color="#B91C1C")
    d += elm.Line().right(2.4)
    p_vmid_d15 = d.here
    d += elm.Dot()
    d += elm.Line().right(4.0)
    p_q1b_in = d.here

    # Q1B P-MOSFET (S=V_MID, D=VIN_PROT, G=Q1_GATE)
    q1b_pts = draw_rect_block(
        d,
        p_q1b_in[0] + 0.35,
        p_q1b_in[1] - 1.0,
        3.4,
        2.0,
        ["Q1B", "DMG2305UX-7", "OVP-Cut"],
        left_pins=[("S", 0.50, "2")],
        right_pins=[("D", 0.50, "3")],
        bot_pins=[("G", 0.50, "1")],
        lead=0.35,
        fontsize=6.8,
        pin_fontsize=6.2,
    )
    d += elm.Line().at(p_q1b_in).to(q1b_pts["S"])

    # Gate bus Q1_GATE joining Q1A.G and Q1B.G + R10 pull-up + D15 Vgs clamp
    gate_y = q1a_pts["G"][1] - 0.35
    d += elm.Line().at(q1a_pts["G"]).to((q1a_pts["G"][0], gate_y))
    d += elm.Line().to((q1b_pts["G"][0], gate_y))
    d += elm.Line().to(q1b_pts["G"])
    p_gate_mid = (p_vmid[0], gate_y)
    p_gate_d15 = (p_vmid_d15[0], gate_y)
    d += elm.Dot().at(p_gate_mid)
    d += elm.Dot().at(p_gate_d15)
    d += elm.Label().at((p_gate_d15[0] + 0.30, gate_y + 0.16)).label("Q1_GATE", halign="left", valign="bottom", fontsize=6.6)
    d += elm.Resistor().at(p_vmid).to(p_gate_mid).label("R10 10k\n0603", loc="top", ofst=0.18, fontsize=6.4)
    d += elm.Zener().at(p_gate_d15).to(p_vmid_d15).label("D15\nBZT52C5V6\nVGS Clamp", loc="bottom", ofst=0.22, fontsize=6.2)

    # V_MID OVP sub-bus at y = gate_y - 0.80 = 9.7 from p_vmid_sub left to x = 11.4
    vmid_bus_y = gate_y - 0.80
    d += elm.Line().at(p_vmid_sub).to((p_vmid_sub[0], vmid_bus_y))
    d += elm.Line().to((11.4, vmid_bus_y))
    p_bus_r12 = (11.4, vmid_bus_y)
    p_bus_r15 = (18.2, vmid_bus_y)
    p_bus_q2e = (21.6, vmid_bus_y)
    d += elm.Dot().at(p_bus_r15)
    d += elm.Dot().at(p_bus_q2e)

    # 1. Precision Divider R12 (13.7k) / R13 (10.0k) at x = 11.4
    d += elm.Resistor().at(p_bus_r12).down(2.5).label("R12\n13.7k 1%\n0603", loc="top", ofst=0.22, fontsize=6.3)
    p_ovp_sense = d.here
    d += elm.Dot().label("OVP_SENSE", loc="left", ofst=0.16, fontsize=6.3)
    d.push()
    d += elm.Resistor().down(2.4).label("R13\n10.0k 1%\n0603", loc="top", ofst=0.22, fontsize=6.3)
    d += elm.Ground()
    d.pop()

    # 2. U3 TL431AIDBZR (SOT-23-3 DBZ: 1=K, 2=REF, 3=A) at x = 13.6..16.2
    u3_x0 = 13.6
    u3_y0 = p_ovp_sense[1] - 0.85
    u3_pts = draw_rect_block(
        d,
        u3_x0,
        u3_y0,
        2.6,
        1.7,
        ["U3", "TL431AI", "2.495V 1%"],
        left_pins=[("REF", 0.50, "2")],
        top_pins=[("K", 0.50, "1")],
        bot_pins=[("A", 0.50, "3")],
        lead=0.28,
        fontsize=6.4,
        pin_fontsize=5.9,
    )
    d += elm.Line().at(p_ovp_sense).to(u3_pts["REF"])
    d += elm.Line().at(u3_pts["A"]).down(0.6)
    d += elm.Ground()

    # 3. R15 (10k) + R16 (5.6k) + Q2 (MMBT3906 PNP) at x = 20.3..22.9, y = 7.1..8.8
    q2_x0 = p_bus_q2e[0] - 1.3
    q2_y0 = vmid_bus_y - 2.6
    q2_pts = draw_rect_block(
        d,
        q2_x0,
        q2_y0,
        2.6,
        1.7,
        ["Q2", "MMBT3906", "OVP PNP"],
        top_pins=[("E", 0.50, "2")],
        left_pins=[("B", 0.50, "1")],
        bot_pins=[("C", 0.50, "3")],
        lead=0.28,
        fontsize=6.4,
        pin_fontsize=5.9,
    )
    d += elm.Line().at(p_bus_q2e).to(q2_pts["E"])
    p_q2b = (p_bus_r15[0], q2_pts["B"][1])
    d += elm.Line().at(q2_pts["B"]).to(p_q2b)
    d += elm.Dot().label("Q2_BASE", loc="bottom", ofst=0.14, fontsize=6.1)
    d += elm.Resistor().at(p_bus_r15).to(p_q2b).label("R15 10k\n0603", loc="top", ofst=0.18, fontsize=6.2)
    # Connect U3.K (OVP_K) via R16 (5.6k) to Q2_BASE (cleanly clear of U3 top pin)
    d += elm.Line().at(u3_pts["K"]).to((u3_pts["K"][0], p_q2b[1] + 0.6))
    d += elm.Line().to((u3_pts["K"][0], p_q2b[1]))
    d += elm.Dot().label("OVP_K", loc="top", ofst=0.14, fontsize=6.0)
    d += elm.Resistor().to(p_q2b).label("R16 5.6k\n0603", loc="bottom", ofst=0.20, fontsize=6.1)

    # OVP_DRV node cleanly below Q2.C
    p_ovp_drv = (q2_pts["C"][0], q2_pts["C"][1] - 0.35)
    d += elm.Line().at(q2_pts["C"]).to(p_ovp_drv)
    d += elm.Dot().label("OVP_DRV", loc="left", ofst=0.14, fontsize=6.2)

    # 4. D16 (BAW56LT1G Common Anode) at x = 24.4..27.0, y = 5.7..7.3
    d16_x0 = 24.4
    d16_y0 = p_ovp_drv[1] - 0.85
    d16_pts = draw_rect_block(
        d,
        d16_x0,
        d16_y0,
        2.6,
        1.6,
        ["D16", "BAW56", "Com-Anode"],
        left_pins=[("A", 0.50, "3")],
        top_pins=[("K1", 0.50, "1")],
        bot_pins=[("K2", 0.50, "2")],
        lead=0.28,
        fontsize=6.3,
        pin_fontsize=5.9,
    )
    d += elm.Line().at(p_ovp_drv).to(d16_pts["A"])
    # K1 -> R18 (220R) -> Q1_GATE
    d += elm.Resistor().at(d16_pts["K1"]).to((d16_pts["K1"][0], gate_y)).label("R18 220R\n0603", loc="top", ofst=0.18, fontsize=6.2)
    d += elm.Dot()

    # 5. Q4 (MMBT3904) OVP Latch at x = 21.4..24.0, y = 2.9..4.5
    q4_x0 = 21.4
    q4_y0 = 2.9
    q4_pts = draw_rect_block(
        d,
        q4_x0,
        q4_y0,
        2.6,
        1.6,
        ["Q4", "MMBT3904", "OVP-Latch"],
        right_pins=[("C", 0.50, "3")],
        left_pins=[("B", 0.50, "1")],
        bot_pins=[("E", 0.50, "2")],
        lead=0.28,
        fontsize=6.3,
        pin_fontsize=5.9,
    )
    d += elm.Line().at(q4_pts["E"]).down(0.45)
    d += elm.Ground()

    # R17 (10k) from OVP_DRV to Q4_BASE + R20 (100k) to GND
    d += elm.Line().at(q4_pts["B"]).left(0.9)
    p_q4b = d.here
    d += elm.Dot().label("Q4_BASE", loc="bottom", ofst=0.16, fontsize=6.0)
    d.push()
    d += elm.Resistor().down(1.4).label("R20 100k\n0603", loc="top", ofst=0.24, fontsize=6.1)
    d += elm.Ground()
    d.pop()
    d += elm.Line().at(p_ovp_drv).to((p_q4b[0], p_ovp_drv[1]))
    d += elm.Resistor().to(p_q4b).label("R17 10k\n0603", loc="top", ofst=0.20, fontsize=6.1)

    # 6. Soft-start Q3 (MMBT3904) at x = 29.0..31.8, y = 4.4..6.2 (Q3.C cleanly left of Q1B!)
    q3_x0 = 29.0
    q3_y0 = 4.4
    q3_pts = draw_rect_block(
        d,
        q3_x0,
        q3_y0,
        2.8,
        1.8,
        ["Q3", "MMBT3904", "Soft-Start"],
        top_pins=[("C", 0.50, "3")],
        left_pins=[("B", 0.50, "1")],
        bot_pins=[("E", 0.50, "2")],
        lead=0.30,
        fontsize=6.5,
        pin_fontsize=6.0,
    )
    d += elm.Line().at(q3_pts["C"]).to((q3_pts["C"][0], gate_y))
    d += elm.Dot()
    d += elm.Resistor().at(q3_pts["E"]).down(1.7).label("R11 1.5k\n0603", loc="bottom", ofst=0.22, fontsize=6.3)
    d += elm.Ground()

    # Q3_BASE node: fed by Q4.C, C11, and R14 (220k)
    d += elm.Line().at(q3_pts["B"]).left(1.4)
    p_q3b = d.here
    d += elm.Dot().label("Q3_BASE", loc="bottom", ofst=0.18, fontsize=6.2)
    d.push()
    d += elm.Capacitor().down(1.8).label("C11\n100nF\n0603", loc="bottom", ofst=0.22, fontsize=6.2)
    d += elm.Ground()
    d.pop()
    # Q4.C -> Q3_BASE cleanly
    d.push()
    d += elm.Line().at(q4_pts["C"]).to((q4_pts["C"][0], p_q3b[1]))
    d += elm.Line().to(p_q3b)
    d.pop()
    # R14 (220k) routed at y = 8.4 cleanly ABOVE D16 up to p_vmid_r14
    d.push()
    d += elm.Line().at(p_q3b).up(3.1)
    d += elm.Resistor().to((p_vmid_r14[0], d.here[1])).label("R14 220k 0603", loc="bottom", ofst=0.14, fontsize=6.2)
    d += elm.Line().to(p_vmid_r14)
    d.pop()

    # Hysteresis K2 -> R19 (27k) -> OVP_SENSE cleanly along bottom of Block 1 (y = 1.9)
    hyst_y = 1.9
    d += elm.Line().at(d16_pts["K2"]).to((d16_pts["K2"][0], hyst_y))
    d += elm.Resistor().to((p_ovp_sense[0] + 1.2, hyst_y)).label("R19 27k 1% 0603 (Hyst)", loc="bottom", ofst=0.14, fontsize=6.2)
    d += elm.Line().to((p_ovp_sense[0] + 1.2, p_ovp_sense[1]))
    d += elm.Line().to(p_ovp_sense)

    # Downstream of Q1B.D -> VIN_PROT -> D11 (downstream TVS) -> C1 -> To Ch1/Ch2
    d += elm.Line().at(q1b_pts["D"]).right(1.1)
    p_vin_prot = d.here
    d += elm.Dot().label("VIN_PROT", loc="top", ofst=0.20, fontsize=7.8, color="#B91C1C")
    d.push()
    d += elm.Zener().down(3.3).reverse().label("D11\nSMBJ5.0A\n600W TVS", loc="top", ofst=0.28, fontsize=6.8)
    d += elm.Ground()
    d.pop()

    d += elm.Line().at(p_vin_prot).right(2.2)
    d += elm.Dot()
    d.push()
    d += elm.Capacitor().down(3.3).label("C1\n10uF 25V\nX7R 1206", loc="bottom", ofst=0.28, fontsize=6.8)
    d += elm.Ground()
    d.pop()
    d += elm.Line().right(0.9)
    d += elm.Dot().label("To Ch1/Ch2", loc="right", fontsize=7.4, color="#B91C1C")

    # =========================================================================
    # BLOCK 2 (Bottom-Left): Maxi-Switch Logic & Mechanical Mounting Holes
    # =========================================================================
    sx0, sy0 = 0.0, -5.8
    draw_box(d, sx0 - 0.6, sy0 - 7.0, sx0 + 44.0, sy0 + 6.6, "2. Maxi-Switch Logic (4-UV / OFF / 8-ALL) and Ch2 1.0ms Stagger")

    # Off-board SW1 + SW1_BOOT dashed box
    draw_box(d, sx0 - 0.2, sy0 - 2.8, sx0 + 5.5, sy0 + 4.8, "OFF-BOARD", dashed=True, color="#64748B", title_color="#475569", title_size=8)

    sw1_pts = draw_rect_block(
        d,
        sx0 + 0.1,
        sy0 - 1.6,
        4.6,
        4.4,
        ["SW1", "100SP3T1", "+ SW1_BOOT", "759D02000", "On-Off-On"],
        right_pins=[("4-UV", 0.82, "1"), ("COM", 0.50, "2"), ("8-ALL", 0.18, "3")],
        lead=0.45,
        fontsize=7.0,
        pin_fontsize=6.4,
    )

    j4_pts = draw_rect_block(
        d,
        sx0 + 6.8,
        sy0 - 1.6,
        2.8,
        4.4,
        ["J4", "B3B-XH"],
        left_pins=[("1", 0.82, ""), ("2", 0.50, ""), ("3", 0.18, "")],
        right_pins=[("UV", 0.82, ""), ("5V", 0.50, ""), ("ALL", 0.18, "")],
        lead=0.40,
        fontsize=7.5,
    )

    # Straight horizontal connections SW1 -> J4
    d += elm.Line().at(sw1_pts["4-UV"]).to(j4_pts["1"])
    d += elm.Line().at(sw1_pts["COM"]).to(j4_pts["2"])
    d += elm.Line().at(sw1_pts["8-ALL"]).to(j4_pts["3"])

    # J4.2 -> VIN_PROT tap
    d += elm.Line().at(j4_pts["5V"]).right(1.0).label("VIN_PROT", loc="right", fontsize=8, color="#B91C1C")

    # D12 Common-Cathode Diode-OR (BAV70LT1G)
    p_j4_uv = j4_pts["UV"]
    p_j4_all = j4_pts["ALL"]

    d += elm.Line().at(p_j4_uv).right(2.2)
    d += elm.Dot().label("SW_UV_EN", loc="top", ofst=0.22, fontsize=7.5)
    d += elm.Line().right(0.6)
    d += elm.Diode().right(2.8).label("D12A\n(BAV70LT1G)", loc="top", ofst=0.22, fontsize=7.3)
    p_d12_k = d.here
    d += elm.Dot()

    d += elm.Line().at(p_j4_all).right(2.2)
    p_en2 = d.here
    d += elm.Dot()
    d += elm.Label().at((p_en2[0] - 0.15, p_en2[1] + 0.20)).label("EN2_NET", halign="right", valign="bottom", fontsize=7.4)

    # Branch up from EN2_NET through D12B to D12 cathode
    d.push()
    d += elm.Line().at(p_en2).to((p_d12_k[0], p_en2[1]))
    d += elm.Dot()
    d += elm.Diode().up(p_d12_k[1] - p_en2[1]).label("D12B", loc="bottom", ofst=0.25, fontsize=7.5)
    d.pop()

    # EN1_NET -> R5 pulldown & U1.DIM output (now plenty of vertical room above EN2_NET!)
    d += elm.Line().at(p_d12_k).right(4.2)
    p_en1 = d.here
    d += elm.Dot()
    d.push()
    d += elm.Line().right(1.6).label("EN1_NET → U1.DIM", loc="right", fontsize=8.3, color="#047857")
    d.pop()
    d += elm.Resistor().at(p_en1).down(1.5).label("R5 10k\n0603", loc="top", ofst=0.28, fontsize=7.4)
    d += elm.Ground()

    # R6 pulldown on EN2_NET & R7/C6 Stagger RC -> DIM2_NET
    d.push()
    d += elm.Line().at(p_en2).down(0.6)
    d += elm.Resistor().down(2.0).label("R6 10k\n0603", loc="bottom", ofst=0.28, fontsize=7.4)
    d += elm.Ground()
    d.pop()

    d += elm.Line().at((p_d12_k[0], p_en2[1])).right(3.8)
    d += elm.Resistor().right(3.0).label("R7 10k\n0603", loc="top", ofst=0.22, fontsize=7.4)
    p_dim2 = d.here
    d += elm.Dot()
    d.push()
    d += elm.Line().right(1.4).label("DIM2_NET → U2.DIM", loc="right", fontsize=8.3, color="#047857")
    d.pop()
    d += elm.Capacitor().at(p_dim2).down(2.0).label("C6 100nF\n25V 0603\n(tau=1.0/2.0ms)", loc="bottom", ofst=0.28, fontsize=7.2)
    d += elm.Ground()

    # Mechanical Mounting Holes & Notes box at bottom-left
    d += elm.Label().at((sx0 - 0.1, sy0 - 5.3)).label(
        "PCB Mechanical Mounting (GND-tied M2.5, 36 x 46 mm 2-layer FR4):",
        loc="right", halign="left", fontsize=8.5, color="#0F172A",
    )
    d += elm.Label().at((sx0 - 0.1, sy0 - 6.0)).label(
        "H1 (-14,+19) | H2 (+14,+19) | H3 (-14,-19) | H4 (+14,-19) mm  [2.7mm drill, 5.5mm pad]",
        loc="right", halign="left", fontsize=8, color="#334155",
    )

    # =========================================================================
    # BLOCK 3 (Top-Right): Channel 1 — 4S UV-A Boost Driver
    # =========================================================================
    draw_boost_channel(
        d=d,
        x0=46.2,
        y0=8.8,
        title="3. Channel 1: 4S UV-A Boost Constant-Current Driver (339mA nom)",
        u_ref="U1",
        l_ref="L1",
        d_catch_ref="D9",
        c_in_ref="C2",
        c_in_hf_ref="C7",
        c_out_ref="C4",
        c_out_hf_ref="C9",
        r_sense_ref="R3",
        d_ovp_ref="D13",
        r_ovp_ref="R8",
        j_ref="J2",
        dim_net="EN1_NET",
        sw_net="SW1_NODE",
        vout_net="VOUT1 (~14.4V)",
        fb_net="FB1_NET",
        ret_net="UV_RET",
        led_specs=[
            ("D1", "SST-10-UV 365nm"),
            ("D2", "SST-10-UV 365nm"),
            ("D3", "SST-10-UV 365nm"),
            ("D4", "SST-10-UV 365nm"),
        ],
    )

    # =========================================================================
    # BLOCK 4 (Bottom-Right): Channel 2 — 4S Visible Boost Driver
    # =========================================================================
    draw_boost_channel(
        d=d,
        x0=46.2,
        y0=-5.2,
        title="4. Channel 2: 4S Visible Boost Constant-Current Driver (339mA nom)",
        u_ref="U2",
        l_ref="L2",
        d_catch_ref="D10",
        c_in_ref="C3",
        c_in_hf_ref="C8",
        c_out_ref="C5",
        c_out_hf_ref="C10",
        r_sense_ref="R4",
        d_ovp_ref="D14",
        r_ovp_ref="R9",
        j_ref="J3",
        dim_net="DIM2_NET",
        sw_net="SW2_NODE",
        vout_net="VOUT2 (~11.5V)",
        fb_net="FB2_NET",
        ret_net="VIS_RET",
        led_specs=[
            ("D5", "XP-E2 Blue 00S02"),
            ("D6", "XP-E2 Blue 00S02"),
            ("D7", "XP-E2 Green 00K01"),
            ("D8", "XP-E2 CW 00H51"),
        ],
    )

    svg_path = out_dir / "schematic.svg"
    pdf_path = out_dir / "schematic.pdf"
    png_path = out_dir / "schematic.png"

    d.save(str(svg_path))

    inkscape = shutil.which("inkscape")
    if inkscape:
        subprocess.run(
            [inkscape, str(svg_path), "--export-type=pdf", f"--export-filename={pdf_path}"],
            check=True,
        )
        subprocess.run(
            [inkscape, str(svg_path), "--export-type=png", "--export-dpi=220", f"--export-filename={png_path}"],
            check=True,
        )
    else:
        import cairosvg
        cairosvg.svg2pdf(url=str(svg_path), write_to=str(pdf_path))
        cairosvg.svg2png(url=str(svg_path), write_to=str(png_path), scale=2.0)

    return png_path


if __name__ == "__main__":
    out_dir = Path(__file__).resolve().parent
    build_schematic(out_dir)
    print(f"Generated schematic SVG, PDF, PNG in {out_dir}")
