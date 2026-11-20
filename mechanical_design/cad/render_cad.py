#!/usr/bin/env python3
"""
Headless PyVista 3D CAD Renderer for LepiLED DIY Maxi Switch (Rev 4.8 — "Field Lantern":
PETG/ASA Shell + Chimney-Only Matte-Black Al Core + Copper Stars + Signal-Orange Hang Bushing).
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
    "lid_bot":        dict(color="#363b42", opacity=1.0),  # Recessed lid + 4x integral M2.5 PCB standoffs
    "cap_bot":        dict(color="#25292e", opacity=1.0),  # Unified matte PETG/ASA base shell
    "cap_top":        dict(color="#25292e", opacity=1.0),  # Lofted rain roof + 9.5 mm vertical collar
    "plug_top":       dict(color="#30353c", opacity=1.0),  # 8 mm chamfered obelisk finial
    "core_anchor":    dict(color="#4a515a", opacity=1.0),  # Staggered internal dry-bay core anchor
    "cable_clamp":    dict(color="#3d434b", opacity=1.0),  # Blind-bolted conical radial-compression clamp
    "hang_bushing":   dict(color="#ff5a1f", opacity=1.0),  # Signal-Orange snap-fit hang-hole pivot bushing
    "hang_bail":      dict(color="#c4cdd6", opacity=1.0),  # DIY C-shaped steel wire hanging bail (coat-hanger wire)
    "pcb_assy":       dict(color="#1f6f3b", opacity=1.0),  # Serviceable lid-mounted driver_pcb (SMD/JST UP)
    "hs_core":        dict(color="#8d96a0", opacity=1.0),  # Bare mill Al core interior (chimney top sprayed matte black)
    "inserts_brass":  dict(color="#d4a73c", opacity=1.0),  # 14x modeled brass heat-set inserts
    "fasteners_m3":   dict(color="#adb6c2", opacity=1.0),  # Full-length M3 + M2.5 nylon fasteners
    "glass_tube":     dict(color="#d8f0ff", opacity=0.24), # PLEXIGLAS XT Clear 0A070 (Ø60x54x115 mm)
    "dtp_stars":      dict(color="#d47a34", opacity=1.0),  # 8x 20 mm LED stars + Ø7 nylon edge-clamping washers
    "sw1_assy":       dict(color="#c4342d", opacity=1.0),  # Bottom-mounted SW1 + realistic 18.6 mm boot
    "usbc_plug_assy": dict(color="#5b6675", opacity=1.0),  # Realistic 15 mm 90-deg USB-C plug + 7 mm strain relief
}


def load_parts(parts_dir: Path) -> dict[str, pv.PolyData]:
    return {k: pv.read(str(parts_dir / f"{k}.stl")) for k in PART_STYLES}


def render_assembly_iso(parts: dict[str, pv.PolyData], out_path: Path) -> None:
    pl = pv.Plotter(off_screen=True, window_size=(1200, 1600))
    pl.set_background("#f4f6f8")
    for k, mesh in parts.items():
        st = PART_STYLES[k]
        pl.add_mesh(mesh, color=st["color"], opacity=st["opacity"], smooth_shading=True, split_sharp_edges=True)
    pl.camera_position = [(490, -510, 290), (0, 0, 158), (0, 0, 1)]
    pl.add_title("LepiLED Rev 4.8 — Wire Bail, Lid-PCB, Sealed Collar & 0A070 PMMA", font_size=10, color="black")
    pl.add_axes()
    pl.screenshot(str(out_path))
    pl.close()


def _draw_vdim(ax: plt.Axes, x_dim: float, z0: float, z1: float, label: str,
               x_ref0: float | None = None, x_ref1: float | None = None,
               color: str = "#1c2430", fontsize: float = 9.0, text_dx: float = -3.5, ha: str = "right") -> None:
    ext_color = "#6b7785"
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
        bbox=dict(boxstyle="round,pad=0.18", fc="#f4f6f8", ec="none", alpha=0.88),
    )


def _draw_hdim(ax: plt.Axes, z_dim: float, x0: float, x1: float, label: str,
               z_ref0: float | None = None, z_ref1: float | None = None,
               color: str = "#1c2430", fontsize: float = 9.0, text_dz: float = -4.0, va: str = "top") -> None:
    ext_color = "#6b7785"
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
        bbox=dict(boxstyle="round,pad=0.18", fc="#f4f6f8", ec="none", alpha=0.88),
    )


def _draw_callout(ax: plt.Axes, xy_target: tuple[float, float], xy_text: tuple[float, float],
                  label: str, ha: str = "left", color: str = "#22303c") -> None:
    ax.annotate(
        label, xy=xy_target, xytext=xy_text, ha=ha, va="center", fontsize=8.2, color=color,
        bbox=dict(boxstyle="round,pad=0.22", fc="white", ec="#c5ced6", lw=0.7, alpha=0.92),
        arrowprops=dict(arrowstyle="-|>", color="#5a6875", lw=0.85, mutation_scale=8, shrinkA=2, shrinkB=2),
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
    win_w, win_h = 1350, 1600
    z_center = 152.0
    par_scale = 194.0
    half_x = par_scale * (win_w / win_h)

    pl = pv.Plotter(off_screen=True, window_size=(win_w, win_h))
    pl.set_background("#f4f6f8")
    for k, mesh in parts.items():
        st = PART_STYLES[k]
        clipped = mesh.clip_box(bounds=bounds, invert=False)
        if clipped.n_cells > 0:
            op = 0.32 if k == "glass_tube" else 1.0
            pl.add_mesh(clipped, color=st["color"], opacity=op, smooth_shading=False, show_edges=False)
    pl.camera_position = cam_pos
    pl.enable_parallel_projection()
    pl.camera.parallel_scale = par_scale
    img = pl.screenshot(return_img=True)
    pl.close()

    fig, ax = plt.subplots(figsize=(9.0, 10.67), dpi=150)
    fig.patch.set_facecolor("#f4f6f8")
    ax.set_facecolor("#f4f6f8")
    ax.imshow(img, extent=[-half_x, half_x, z_center - par_scale, z_center + par_scale], aspect="equal")
    ax.set_xlim(-half_x, half_x)
    ax.set_ylim(z_center - par_scale, z_center + par_scale)
    ax.axis("off")

    ax.plot([0.0, 0.0], [-10.0, p.total_height_with_bail_mm + 12.0], color="#8a96a3", lw=0.65, ls="-.", alpha=0.55)
    ax.text(0.0, z_center + par_scale - 6.0, title, ha="center", va="top", fontsize=10.4, fontweight="bold", color="#111820")

    r_base = 0.5 * p.cap_bot_base_od
    r_col = 0.5 * p.cap_bot_collar_od
    r_brim = 0.5 * p.cap_top_brim_od
    r_shroud = 0.5 * p.glass_od_nom
    r_core = 0.5 * p.core_w_nom

    _draw_vdim(ax, -108.0, 0.0, p.total_height_mm, f"{p.total_height_mm:.1f} mm\nbody", x_ref0=-r_base, x_ref1=-15.0, text_dx=-3.5, ha="right")
    _draw_hdim(ax, -18.0, -r_base, r_base, f"Ø{p.cap_bot_base_od:.1f} mm base", z_ref0=0.0, z_ref1=0.0, text_dz=-3.5, va="top")
    if plane == "XZ":
        _draw_hdim(ax, p.total_height_with_bail_mm + 8.0, -p.bail_half_w, p.bail_half_w, f"{2.0 * p.bail_half_w:.0f} mm C-clip wire bail", z_ref0=p.z_hang_hole + p.bail_leg_h, z_ref1=p.z_hang_hole + p.bail_leg_h, text_dz=3.0, va="bottom")
    else:
        _draw_hdim(ax, p.total_height_with_bail_mm + 8.0, -r_core, r_core, f"{p.core_w_nom:.0f} mm Al core", z_ref0=p.z_core_top, z_ref1=p.z_core_top, text_dz=3.0, va="bottom")

    if plane == "YZ":
        _draw_vdim(ax, -66.0, 0.0, p.z_cap_bot_top, f"{p.z_cap_bot_top:.1f} mm\nbase", x_ref0=-r_base, x_ref1=-r_col, text_dx=-3.0, ha="right", fontsize=8.4)
        _draw_vdim(ax, -66.0, p.z_cap_bot_top, p.z_cap_top_bot, f"{p.exposed_glass_window:.1f} mm\nwindow", x_ref0=-r_col, x_ref1=-r_col, text_dx=-3.0, ha="right", fontsize=8.4)
        _draw_vdim(ax, -66.0, p.z_cap_top_top, p.z_core_top, f"{p.core_protrusion_mm:.1f} mm\nchimney", x_ref0=-20.2, x_ref1=-r_core, text_dx=-3.0, ha="right", fontsize=8.4)

        _draw_hdim(ax, p.z_cap_top_top + 7.5, -r_brim, r_brim, f"Ø{p.cap_top_brim_od:.0f} mm rain eaves", z_ref0=p.z_cap_top_brim_rim_top, z_ref1=p.z_cap_top_brim_rim_top, text_dz=3.2, va="bottom", fontsize=8.5)
        _draw_vdim(ax, 66.0, p.z_glass_bot, p.z_glass_top, f"{p.glass_length:.0f} mm\n0A070 PMMA\n(Ø{p.glass_od_nom:.0f}×{p.glass_id_nom:.0f})", x_ref0=r_shroud, x_ref1=r_shroud, text_dx=3.5, ha="left", fontsize=8.3)
        _draw_vdim(ax, 66.0, 0.0, p.z_lid_bot_start, f"{p.z_lid_bot_start:.1f} mm skirt", x_ref0=r_base, x_ref1=43.0, text_dx=3.5, ha="left", fontsize=8.3)

        _draw_callout(ax, (-1.5, p.z_bail_top_center - 6.0), (-56.0, p.z_bail_top_center - 12.0), f"DIY C-clip wire bail\n({p.bail_clearance_above_finial_mm:.0f} mm hook clr; £0)", ha="right")
        _draw_callout(ax, (15.0, p.z_hang_hole), (56.0, p.z_hang_hole - 6.0), "Ø8→4.0 mm snap-fit\nwire-bail pivot bushing")
        _draw_callout(ax, (26.0, p.pcb_z_fcu), (56.0, p.pcb_z_fcu + 10.0), "Lid-mounted PCB (SMD UP)\non M2.5 lid standoffs")
        _draw_callout(ax, (15.0, 12.0), (56.0, 32.0), "SW1 + real 18.6 mm boot\n(3.4 mm recessed in skirt)")
        _draw_callout(ax, (-20.5, 16.0), (-56.0, -8.0), "Blind-bolted conical\nsplit clamp + 15 mm USB-C", ha="right")
    else:
        _draw_vdim(ax, -66.0, p.z_core_bot, p.z_core_top, f"{p.core_length:.0f} mm\nstock Al tube", x_ref0=-r_core, x_ref1=-r_core, text_dx=-3.0, ha="right", fontsize=8.5)
        _draw_vdim(ax, 66.0, p.z_led_vis, p.z_led_uv, f"{p.axial_uv_to_vis_mm:.0f} mm\nstar pitch", x_ref0=20.0, x_ref1=20.0, text_dx=3.5, ha="left", fontsize=8.5)
        _draw_hdim(ax, p.z_cap_top_top + 7.5, -r_brim, r_brim, f"Ø{p.cap_top_brim_od:.0f} mm eaves / 40.4 mm collar", z_ref0=p.z_cap_top_brim_rim_top, z_ref1=p.z_cap_top_brim_rim_top, text_dz=3.2, va="bottom", fontsize=8.4)

        _draw_callout(ax, (-16.0, p.z_bail_top_center - 16.0), (-56.0, p.z_bail_top_center - 14.0), "DIY C-clip wire bail\n(~175 mm coat hanger; self-clamps!)", ha="right")
        _draw_callout(ax, (15.0, p.z_hang_hole), (56.0, p.z_hang_hole - 6.0), "Chimney-only matte black\n+ Ø4.0 mm snap bushings")
        _draw_callout(ax, (21.0, p.z_cap_top_lock), (56.0, p.z_cap_top_lock - 6.0), "2× M3×10 top lock\n(4.65 mm collar wall, 0 holes)")
        _draw_callout(ax, (18.0, p.z_led_uv), (56.0, p.z_led_uv + 16.0), "8× 20 mm stars edge-clamped\n(R=11.7 mm + Ø7 nylon washer)")
        _draw_callout(ax, (26.5, p.z_glass_bot + 7.5), (56.0, p.z_glass_bot + 10.0), "Solid R=24.5 mm hub\n+ 60×3.5 VMQ50 O-ring")
        _draw_callout(ax, (11.0, p.z_anchor_pin), (56.0, p.z_anchor_pin - 20.0), "Staggered core anchor\n(±Y bolts / ±X CSK pins)")

    mass_text = (
        f"Approx. Weight: ~{mass['total_fdm_petg_g']:.0f} g PETG\n"
        f"  (~{mass['total_fdm_asa_g']:.0f} g ASA)\n"
        f"  • Printed shell:    {mass['petg_fdm_62pct_g']:.0f} g\n"
        f"  • 30×30×3 Al core:  {mass['al_core_3mm_g']:.0f} g\n"
        f"  • 0A070 PMMA tube:   {mass['uvt_pmma_shroud_g']:.0f} g\n"
        f"  • Stars / PCB / HW: {mass['elec_stars_hardware_g']:.0f} g\n"
        f"Envelope: {p.total_height_mm:.1f} × Ø{p.cap_bot_base_od:.1f} mm"
    )
    ax.text(
        half_x - 6.0, z_center + par_scale - 18.0, mass_text,
        ha="right", va="top", fontsize=7.9, family="monospace", color="#18222c",
        bbox=dict(boxstyle="round,pad=0.45", fc="white", ec="#9aa6b2", lw=0.95, alpha=0.96),
    )

    fig.tight_layout(pad=0.2)
    fig.savefig(str(out_path), dpi=150, facecolor="#f4f6f8")
    plt.close(fig)


def render_cap_detail(stl_path: Path, title: str, z_mid: float, out_path: Path, color: str = "#383e47") -> None:
    mesh = pv.read(str(stl_path))
    pl = pv.Plotter(off_screen=True, shape=(1, 2), window_size=(1600, 800))
    pl.set_background("#f4f6f8")

    pl.subplot(0, 0)
    pl.add_mesh(mesh, color=color, smooth_shading=True, split_sharp_edges=True)
    pl.camera_position = [(140, -140, z_mid + 120), (0, 0, z_mid), (0, 0, 1)]
    pl.add_text(f"{title} — Top Isometric", font_size=10, color="black")

    pl.subplot(0, 1)
    pl.add_mesh(mesh, color=color, smooth_shading=True, split_sharp_edges=True)
    pl.camera_position = [(150, -150, z_mid - 135), (0, 0, z_mid), (0, 0, 1)]
    pl.add_text(f"{title} — Bottom Isometric", font_size=10, color="black")

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
        bounds=(-100, 100, 0, 100, -10, 330),
        title="Section XZ (Y = 0) — Rev 4.8 C-Clip Wire Bail, Sealed Collar & Edge-Clamped Stars",
        cam_pos=[(0, -760, 152), (0, 0, 152), (0, 0, 1)],
        plane="XZ",
        out_path=cad_dir / "assembly_section_xz.png",
    )
    render_section_annotated(
        parts, p, mass,
        bounds=(-100, 0, -100, 100, -10, 330),
        title="Section YZ (X = 0) — Rev 4.8 Wire Bail, Lid-Mounted PCB, Blind Clamp & Real SW1 Boot",
        cam_pos=[(760, 0, 152), (0, 0, 152), (0, 0, 1)],
        plane="YZ",
        out_path=cad_dir / "assembly_section_yz.png",
    )
    render_cap_detail(cad_dir / "mech_lid_bot.stl", "MECH-LID-BOT (4x M2.5 Standoffs + Blind Clamp + Recessed Vent)", 32.0, cad_dir / "lid_bot_detail.png")
    render_cap_detail(cad_dir / "mech_cap_bot.stl", "MECH-CAP-BOT (22 mm Skirt + Straight Ø71.6 Bore + Intact Ribs)", 44.0, cad_dir / "cap_bot_detail.png")
    render_cap_detail(cad_dir / "mech_cap_top.stl", "MECH-CAP-TOP (Lofted Roof + 9.5 mm Solid Collar — 0 Roof Holes!)", 192.0, cad_dir / "cap_top_detail.png")
    print("Rendered all 6 Rev 4.8 CAD PNGs cleanly.")


if __name__ == "__main__":
    main()
