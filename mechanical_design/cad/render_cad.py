#!/usr/bin/env python3
"""
Headless PyVista 3D CAD Renderer for LepiLED DIY Maxi Switch.
Run under: xvfb-run -a /tmp/lepiled-venv/bin/python mechanical_design/cad/render_cad.py
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pyvista as pv

from params import LepiLEDParams


PART_STYLES = {
    "cap_bot":        dict(color="#f4f6f9", opacity=1.0),
    "top_base":       dict(color="#e4eaf0", opacity=1.0),
    "cap_top":        dict(color="#f7f9fb", opacity=1.0),
    "plug_top":       dict(color="#ebeef2", opacity=1.0),
    "cable_clamp":    dict(color="#d6dee6", opacity=1.0),
    "hang_loop":      dict(color="#d96b27", opacity=1.0),
    "pcb_assy":       dict(color="#1d703b", opacity=1.0),
    "thermal_bridge": dict(color="#5498c9", opacity=1.0),
    "hs_core":        dict(color="#aeb7c2", opacity=1.0),
    "inserts_brass":  dict(color="#d4a73c", opacity=1.0),
    "fasteners_m3":   dict(color="#8d97a4", opacity=1.0),
    "glass_tube":     dict(color="#bfe8ff", opacity=0.26),
    "dtp_stars":      dict(color="#d47a34", opacity=1.0),
    "sw1_assy":       dict(color="#c8322b", opacity=1.0),
    "usbc_plug_assy": dict(color="#4a5564", opacity=1.0),
    "usbc_cable":     dict(color="#262c34", opacity=1.0),
}

BG_COLOR = "#dce4ec"


def load_parts(parts_dir: Path) -> dict[str, pv.PolyData]:
    return {k: pv.read(str(parts_dir / f"{k}.stl")) for k in PART_STYLES}


def render_assembly_iso(parts: dict[str, pv.PolyData], out_path: Path) -> None:
    pl = pv.Plotter(off_screen=True, shape=(1, 2), window_size=(1800, 1400))
    pl.set_background(BG_COLOR)

    # Left panel: +Y/+X isometric — shows +Y cable clamp, drip loop, eaves C-clip, and bottom nosecone
    pl.subplot(0, 0)
    for k, mesh in parts.items():
        st = PART_STYLES[k]
        pl.add_mesh(mesh, color=st["color"], opacity=st["opacity"], smooth_shading=True, split_sharp_edges=True)
    pl.camera_position = [(540, 565, 320), (0, 10, 180), (0, 0, 1)]
    pl.add_text("Isometric View (+Y Cable Side)", font_size=10, color="#141c24")
    pl.add_axes()

    # Right panel: -X/-Y isometric — shows -X switch cove, visor, tactile ribs, and -Y breather underside
    pl.subplot(0, 1)
    for k, mesh in parts.items():
        st = PART_STYLES[k]
        pl.add_mesh(mesh, color=st["color"], opacity=st["opacity"], smooth_shading=True, split_sharp_edges=True)
    pl.camera_position = [(-565, -520, 315), (-8, -6, 180), (0, 0, 1)]
    pl.add_text("Isometric View (-X Switch Side)", font_size=10, color="#141c24")
    pl.add_axes()

    pl.screenshot(str(out_path))
    pl.close()


def _draw_vdim(ax: plt.Axes, x_dim: float, z0: float, z1: float, label: str,
               x_ref0: float | None = None, x_ref1: float | None = None,
               color: str = "#16202a", fontsize: float = 8.6, text_dx: float = -3.5, ha: str = "right") -> None:
    ext_color = "#5c6b7a"
    if x_ref0 is not None:
        gap = 2.5 if x_dim < x_ref0 else -2.5
        ov = -3.0 if x_dim < x_ref0 else 3.0
        ax.plot([x_ref0 - gap, x_dim + ov], [z0, z0], color=ext_color, lw=0.75, ls="-")
    if x_ref1 is not None:
        gap = 2.5 if x_dim < x_ref1 else -2.5
        ov = -3.0 if x_dim < x_ref1 else 3.0
        ax.plot([x_ref1 - gap, x_dim + ov], [z1, z1], color=ext_color, lw=0.75, ls="-")
    ax.annotate(
        "", xy=(x_dim, z1), xytext=(x_dim, z0),
        arrowprops=dict(arrowstyle="<|-|>", color=color, lw=1.05, mutation_scale=10, shrinkA=0, shrinkB=0),
    )
    ax.text(
        x_dim + text_dx, 0.5 * (z0 + z1), label,
        color=color, fontsize=fontsize, fontweight="bold", ha=ha, va="center",
        bbox=dict(boxstyle="round,pad=0.18", fc=BG_COLOR, ec="none", alpha=0.90),
    )


def _draw_hdim(ax: plt.Axes, z_dim: float, x0: float, x1: float, label: str,
               z_ref0: float | None = None, z_ref1: float | None = None,
               color: str = "#16202a", fontsize: float = 8.6, text_dz: float = -4.0, va: str = "top") -> None:
    ext_color = "#5c6b7a"
    if z_ref0 is not None:
        gap = 2.0 if z_dim < z_ref0 else -2.0
        ov = -3.0 if z_dim < z_ref0 else 3.0
        ax.plot([x0, x0], [z_ref0 - gap, z_dim + ov], color=ext_color, lw=0.75, ls="-")
    if z_ref1 is not None:
        gap = 2.0 if z_dim < z_ref1 else -2.0
        ov = -3.0 if z_dim < z_ref1 else 3.0
        ax.plot([x1, x1], [z_ref1 - gap, z_dim + ov], color=ext_color, lw=0.75, ls="-")
    ax.annotate(
        "", xy=(x1, z_dim), xytext=(x0, z_dim),
        arrowprops=dict(arrowstyle="<|-|>", color=color, lw=1.05, mutation_scale=10, shrinkA=0, shrinkB=0),
    )
    ax.text(
        0.5 * (x0 + x1), z_dim + text_dz, label,
        color=color, fontsize=fontsize, fontweight="bold", ha="center", va=va,
        bbox=dict(boxstyle="round,pad=0.18", fc=BG_COLOR, ec="none", alpha=0.90),
    )


def _draw_callout(ax: plt.Axes, xy_target: tuple[float, float], xy_text: tuple[float, float],
                  label: str, ha: str = "left", color: str = "#1a2633") -> None:
    ax.annotate(
        label, xy=xy_target, xytext=xy_text, ha=ha, va="center", fontsize=8.0, color=color,
        bbox=dict(boxstyle="round,pad=0.22", fc="white", ec="#a8b6c4", lw=0.75, alpha=0.95),
        arrowprops=dict(arrowstyle="-|>", color="#455565", lw=0.9, mutation_scale=8, shrinkA=2, shrinkB=2),
    )


def render_section_annotated(
    parts: dict[str, pv.PolyData],
    p: LepiLEDParams,
    mass: dict[str, float],
    bounds: tuple[float, float, float, float, float, float],
    title: str,
    cam_pos: list,
    plane: str,
    out_path: Path,
) -> None:
    win_w, win_h = 1400, 1650
    z_center = 178.0
    par_scale = 216.0
    half_x = par_scale * (win_w / win_h)

    pl = pv.Plotter(off_screen=True, window_size=(win_w, win_h))
    pl.set_background(BG_COLOR)
    for k, mesh in parts.items():
        if plane == "XZ" and k == "usbc_cable":
            continue
        st = PART_STYLES[k]
        clipped = mesh.clip_box(bounds=bounds, invert=False)
        if clipped.n_cells > 0:
            op = 0.34 if k == "glass_tube" else 1.0
            pl.add_mesh(clipped, color=st["color"], opacity=op, smooth_shading=False, show_edges=False)
    pl.camera_position = cam_pos
    pl.enable_parallel_projection()
    pl.camera.parallel_scale = par_scale
    img = pl.screenshot(return_img=True)
    pl.close()

    fig, ax = plt.subplots(figsize=(9.33, 11.0), dpi=150)
    fig.patch.set_facecolor(BG_COLOR)
    ax.set_facecolor(BG_COLOR)
    ax.imshow(img, extent=[-half_x, half_x, z_center - par_scale, z_center + par_scale], aspect="equal")
    ax.set_xlim(-half_x, half_x)
    ax.set_ylim(z_center - par_scale, z_center + par_scale)
    ax.axis("off")

    z_top_loop = p.z_plug_top_end + 42.0
    ax.plot([0.0, 0.0], [-12.0, z_top_loop + 10.0], color="#6c7d8e", lw=0.65, ls="-.", alpha=0.55)
    ax.text(0.0, z_center + par_scale - 6.0, title, ha="center", va="top", fontsize=10.2, fontweight="bold", color="#101820")

    r_tip = 0.5 * p.cap_bot_tip_od
    r_col = 0.5 * p.cap_bot_collar_od
    r_eaves = 0.5 * p.cap_top_eaves_od
    r_shroud = 0.5 * p.glass_od_nom
    r_core = 0.5 * p.core_w_nom

    _draw_vdim(ax, -126.0, 0.0, p.total_height_mm, f"{p.total_height_mm:.1f} mm\nbody", x_ref0=-r_tip, x_ref1=-19.0, text_dx=-3.5, ha="right")
    _draw_hdim(ax, -18.0, -r_tip, r_tip, f"Ø{p.cap_bot_tip_od:.0f} mm tip (22 mm chimney inlet)", z_ref0=0.0, z_ref1=0.0, text_dz=-3.5, va="top")

    if plane == "XZ":
        _draw_hdim(ax, p.z_plug_top_end + 44.0, -21.0, 21.0, "M4 × 50 mm hang bolt", z_ref0=p.z_plug_top_end + 12.0, z_ref1=p.z_plug_top_end + 12.0, text_dz=3.0, va="bottom")
        _draw_vdim(ax, -82.0, p.z_core_bot, p.z_core_top, f"{p.core_length:.0f} mm\nopen chimney", x_ref0=-r_core, x_ref1=-r_core, text_dx=-3.0, ha="right", fontsize=8.4)
        _draw_vdim(ax, 82.0, p.z_led_vis, p.z_led_uv, f"{p.axial_uv_to_vis_mm:.0f} mm\nstar pitch", x_ref0=20.0, x_ref1=20.0, text_dx=3.5, ha="left", fontsize=8.4)
        _draw_vdim(ax, 82.0, 0.0, p.z_cap_bot_top, f"{p.z_cap_bot_top:.1f} mm\nnosecone", x_ref0=r_tip, x_ref1=r_col, text_dx=3.5, ha="left", fontsize=8.4)
        _draw_hdim(ax, p.z_cap_top_top + 7.5, -r_eaves, r_eaves, f"Ø{p.cap_top_eaves_od:.0f} mm rain eaves", z_ref0=p.z_cap_top_eaves_top, z_ref1=p.z_cap_top_eaves_top, text_dz=3.0, va="bottom", fontsize=8.3)

        _draw_callout(ax, (-15.0, p.z_core_top + 8.0), (-64.0, p.z_plug_top_end + 4.0), "Ventilated rain finial\n(4 exhaust ports + mesh)", ha="right")
        _draw_callout(ax, (20.0, p.z_hang_hole), (66.0, p.z_hang_hole - 2.0), "M4 × 50 mm stainless\nhanging cross-bolt")
        _draw_callout(ax, (26.0, p.pcb_z_center + 4.0), (68.0, 232.0), "Driver PCB (36 × 46 mm)\n+X face, captive 15×15 mm pad/shims")
        _draw_callout(ax, (-52.0, p.sw1_z), (-68.0, 214.0), "SW1 toggle + silicone boot\n(-X draining cove + visor)", ha="right")
        _draw_callout(ax, (18.0, p.z_led_uv), (66.0, 128.0), "8× 20 mm Cu DTP stars\n(2-part thermal epoxy)")
        _draw_callout(ax, (20.0, p.z_bot_bolt), (66.0, 52.0), "M4 × 50 mm nosecone bolt\n+ bottom stainless mesh")
    else:
        _draw_hdim(ax, p.z_plug_top_end + 44.0, -r_core, r_core, f"{p.core_w_nom:.0f} × {p.core_wall:.0f} mm Al core", z_ref0=p.z_core_top, z_ref1=p.z_core_top, text_dz=3.0, va="bottom")
        _draw_vdim(ax, -82.0, 0.0, p.z_cap_bot_top, f"{p.z_cap_bot_top:.1f} mm\nnosecone", x_ref0=-r_tip, x_ref1=-r_col, text_dx=-3.0, ha="right", fontsize=8.3)
        _draw_vdim(ax, -82.0, p.z_cap_bot_top, p.z_top_base_bot, f"{p.exposed_glass_window:.1f} mm\nwindow", x_ref0=-r_col, x_ref1=-r_col, text_dx=-3.0, ha="right", fontsize=8.3)
        _draw_vdim(ax, -82.0, p.z_cap_top_top, p.z_core_top, f"{p.core_protrusion_mm:.1f} mm\nchimney", x_ref0=-20.2, x_ref1=-r_core, text_dx=-3.0, ha="right", fontsize=8.3)
        _draw_vdim(ax, 82.0, p.z_glass_bot, p.z_glass_top, f"{p.glass_length:.0f} mm\nXT PMMA", x_ref0=r_shroud, x_ref1=r_shroud, text_dx=3.5, ha="left", fontsize=8.3)

        _draw_callout(ax, (28.0, 300.0), (70.0, 296.0), "USB-C power cable\n(2.0 m, routed upward)")
        _draw_callout(ax, (45.0, p.z_top_base_deck_top), (72.0, 232.0), "88 × 2.5 mm axial face O-ring\n+ 1.4 mm eaves drip kerf")
        _draw_callout(ax, (60.5, 176.0), (76.0, 190.0), "+Y flexible eaves C-clip\n+ zip-tie slot")
        _draw_callout(ax, (66.5, 137.0), (76.0, 146.0), "20 mm drip loop\n+ compressing clamp")
        _draw_callout(ax, (-36.0, 142.0), (-60.0, 224.0), "-Y downward breather vent\n(flat bay-floor patch)", ha="right")
        _draw_callout(ax, (-19.0, 130.0), (-60.0, 190.0), "±Y 9.0 × 7.5 mm wire slots\n(uncrossed to J2/J3)", ha="right")
        _draw_callout(ax, (-28.0, 16.0), (-58.0, 52.0), "45° tapered nosecone\n(open chimney inlet)", ha="right")

    mass_text = (
        f"Mass Summary\n"
        f"Total: ~{mass['total_fdm_petg_g']:.0f} g PETG\n"
        f"       ~{mass['total_fdm_asa_g']:.0f} g ASA\n"
        f"  Printed parts:   {mass['petg_fdm_62pct_g']:.0f} g\n"
        f"  300 mm Al core:  {mass['al_core_2mm_g']:.0f} g\n"
        f"  XT PMMA shroud:  {mass['uvt_pmma_shroud_g']:.0f} g\n"
        f"  LEDs / PCB / HW: {mass['elec_stars_hardware_g']:.0f} g\n"
        f"Tip: Ø{p.cap_bot_tip_od:.0f} × {p.z_cap_bot_top:.1f} mm"
    )
    ax.text(
        half_x - 6.0, z_center + par_scale - 18.0, mass_text,
        ha="right", va="top", fontsize=7.8, family="monospace", color="#141e28",
        bbox=dict(boxstyle="round,pad=0.45", fc="white", ec="#9aa6b2", lw=0.95, alpha=0.96),
    )

    fig.tight_layout(pad=0.2)
    fig.savefig(str(out_path), dpi=150, facecolor=BG_COLOR)
    plt.close(fig)


def render_part_detail(stl_path: Path, title: str, z_mid: float, out_path: Path, color: str = "#f3f6f9") -> None:
    mesh = pv.read(str(stl_path))
    pl = pv.Plotter(off_screen=True, shape=(1, 2), window_size=(1600, 800))
    pl.set_background(BG_COLOR)

    pl.subplot(0, 0)
    pl.add_mesh(mesh, color=color, smooth_shading=True, split_sharp_edges=True)
    pl.camera_position = [(165, 165, z_mid + 130), (0, 0, z_mid), (0, 0, 1)]
    pl.add_text(f"{title} — Top Isometric (+X/+Y)", font_size=10, color="#141c24")

    pl.subplot(0, 1)
    pl.add_mesh(mesh, color=color, smooth_shading=True, split_sharp_edges=True)
    pl.camera_position = [(-165, -165, z_mid - 130), (0, 0, z_mid), (0, 0, 1)]
    pl.add_text(f"{title} — Bottom Isometric (-X/-Y)", font_size=10, color="#141c24")

    pl.screenshot(str(out_path))
    pl.close()


def main() -> None:
    cad_dir = Path(__file__).resolve().parent
    p = LepiLEDParams(process="FDM")
    verif = json.loads((cad_dir / "cad_verification.json").read_text(encoding="utf-8"))
    mass = verif["mass_budget_g"]
    parts = load_parts(cad_dir / "parts_stl")

    render_assembly_iso(parts, cad_dir / "assembly_iso.png")
    render_section_annotated(
        parts, p, mass,
        bounds=(-100, 100, 0, 100, -10, 380),
        title="Section XZ (Y = 0) — Open Chimney, Vertical PCB & Switch Cove",
        cam_pos=[(0, -820, 178), (0, 0, 178), (0, 0, 1)],
        plane="XZ",
        out_path=cad_dir / "assembly_section_xz.png",
    )
    render_section_annotated(
        parts, p, mass,
        bounds=(-100, 0, -100, 100, -10, 380),
        title="Section YZ (X = 0) — Cable Routing, Breather Vent & Axial Seal",
        cam_pos=[(820, 0, 178), (0, 0, 178), (0, 0, 1)],
        plane="YZ",
        out_path=cad_dir / "assembly_section_yz.png",
    )
    render_part_detail(cad_dir / "mech_cap_bot.stl", "MECH-CAP-BOT — Open-Chimney Bottom Nosecone", 17.0, cad_dir / "cap_bot_detail.png")
    render_part_detail(cad_dir / "mech_top_base.stl", "MECH-TOP-BASE — Top Electronics Chassis", 170.0, cad_dir / "top_base_detail.png")
    render_part_detail(cad_dir / "mech_cap_top.stl", "MECH-CAP-TOP — Top Weatherproof Rain Bell", 214.0, cad_dir / "cap_top_detail.png")
    print("Rendered all 6 CAD PNGs cleanly.")


if __name__ == "__main__":
    main()
