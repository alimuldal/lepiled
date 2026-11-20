#!/usr/bin/env python3
"""
Headless PyVista 3D CAD Renderer for LepiLED DIY Maxi Switch (Rev 4.6 — "Field Lantern":
Matte-Black ASA + Matte-Black Al Chimney + Warm Copper Stars + Signal-Orange Hang-Hole Touchpoint).
Renders true orthographic cross-sections with exact parametric mm dimensions & approximate mass badges.
Must be run under `xvfb-run -a /home/alimuldal/.local/share/lepiled-cad-venv/bin/python render_cad.py`.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pyvista as pv

from params import LepiLEDParams


# Intentional Field-Instrument CMF palette (Matte Charcoal/Black ASA + Matte-Black Chimney + Copper Stars + Signal Orange)
PART_STYLES = {
    "lid_bot":        dict(color="#363b42", opacity=1.0),  # Recessed matte charcoal ASA lid
    "cap_bot":        dict(color="#25292e", opacity=1.0),  # Unified 4.3-deg matte-black ASA tapered frustum
    "cap_top":        dict(color="#25292e", opacity=1.0),  # Lofted square-to-round matte-black ASA rain roof
    "plug_top":       dict(color="#30353c", opacity=1.0),  # 8 mm chamfered obelisk finial
    "core_anchor":    dict(color="#4a515a", opacity=1.0),  # Internal dry-bay core anchor block
    "cable_clamp":    dict(color="#3d434b", opacity=1.0),  # 2-piece coaxial split cable clamp
    "hang_bushing":   dict(color="#ff5a1f", opacity=1.0),  # Signal-Orange RAL 2009 hang-hole touchpoint!
    "pcb_assy":       dict(color="#1f6f3b", opacity=1.0),  # Horizontal driver_pcb + all 57 SMDs
    "hs_core":        dict(color="#1e2126", opacity=1.0),  # Matte-black sprayed 30x30x3x200 mm Al 6063-T6 core
    "fasteners_m3":   dict(color="#adb6c2", opacity=1.0),  # M3 + M2.5 fasteners
    "glass_tube":     dict(color="#d8f0ff", opacity=0.24), # Clear extruded Plexiglas XT Ø60x54x115 mm
    "dtp_stars":      dict(color="#d47a34", opacity=1.0),  # 8x warm Copper 20 mm DTP LED stars
    "sw1_assy":       dict(color="#c4342d", opacity=1.0),  # Bottom-mounted SW1 + waterproof boot
    "usbc_plug_assy": dict(color="#5b6675", opacity=1.0),  # Compact 90-deg USB-C PD plug + 7 mm strain relief
    "d12_rod":        dict(color="#4ef57b", opacity=0.85), # 29.8 mm D12 green PD-status lightpipe
}


def load_parts(parts_dir: Path) -> dict[str, pv.PolyData]:
    return {k: pv.read(str(parts_dir / f"{k}.stl")) for k in PART_STYLES}


def render_assembly_iso(parts: dict[str, pv.PolyData], out_path: Path) -> None:
    pl = pv.Plotter(off_screen=True, window_size=(1200, 1600))
    pl.set_background("#f4f6f8")
    for k, mesh in parts.items():
        st = PART_STYLES[k]
        pl.add_mesh(mesh, color=st["color"], opacity=st["opacity"], smooth_shading=True, split_sharp_edges=True)
    pl.camera_position = [(430, -450, 250), (0, 0, 140), (0, 0, 1)]
    pl.add_title("LepiLED Rev 4.6 'Field Lantern' (Matte-Black ASA + Tapered Frustum + Lofted Roof + Copper Stars)", font_size=10, color="black")
    pl.add_axes()
    pl.screenshot(str(out_path))
    pl.close()


def _draw_vdim(ax: plt.Axes, x_dim: float, z0: float, z1: float, label: str,
               x_ref0: float | None = None, x_ref1: float | None = None,
               color: str = "#1c2430", fontsize: float = 9.0, text_dx: float = -3.5, ha: str = "right") -> None:
    """Draw a clean vertical engineering dimension with extension lines and double-headed arrow."""
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
    """Draw a clean horizontal engineering dimension with extension lines and double-headed arrow."""
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
    """Draw a subtle leader-line annotation callout."""
    ax.annotate(
        label,
        xy=xy_target,
        xytext=xy_text,
        ha=ha,
        va="center",
        fontsize=8.2,
        color=color,
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
    """Render an exact parallel-projection orthographic section and overlay true-to-scale mm dimensions & weight."""
    win_w, win_h = 1350, 1600
    z_center = 136.0
    par_scale = 175.0  # Exact world mm half-height -> Z ∈ [-39, +311] mm!
    half_x = par_scale * (win_w / win_h)  # 147.66 mm -> X/Y ∈ [-147.7, +147.7] mm!

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

    # Subtle vertical centerline
    ax.plot([0.0, 0.0], [-10.0, p.z_plug_top_end + 12.0], color="#8a96a3", lw=0.65, ls="-.", alpha=0.55)

    # Title banner
    ax.text(
        0.0, z_center + par_scale - 6.0, title,
        ha="center", va="top", fontsize=11.0, fontweight="bold", color="#111820",
    )

    # Shared key outer dimensions (true orthographic mm!)
    r_base = 0.5 * p.cap_bot_base_od        # 44.2
    r_col = 0.5 * p.cap_bot_collar_od       # 37.0
    r_brim = 0.5 * p.cap_top_brim_od        # 42.0
    r_shroud = 0.5 * p.glass_od_nom         # 30.0
    r_core = 0.5 * p.core_w_nom             # 15.0

    # Left outer total height dimension (281.5 mm)
    _draw_vdim(ax, -108.0, 0.0, p.total_height_mm, f"{p.total_height_mm:.1f} mm\ntotal", x_ref0=-r_base, x_ref1=-10.0, text_dx=-3.5, ha="right")

    # Bottom base OD & top eaves OD
    _draw_hdim(ax, -18.0, -r_base, r_base, f"Ø{p.cap_bot_base_od:.1f} mm base", z_ref0=0.0, z_ref1=0.0, text_dz=-3.5, va="top")
    _draw_hdim(ax, p.z_plug_top_end + 14.0, -r_core, r_core, f"{p.core_w_nom:.0f} mm Al core", z_ref0=p.z_core_top, z_ref1=p.z_core_top, text_dz=3.2, va="bottom")

    if plane == "YZ":
        # Inner-left vertical breakdown: Base (76.5), Optical Window (86.0), Chimney (63.0)
        _draw_vdim(ax, -66.0, 0.0, p.z_cap_bot_top, f"{p.z_cap_bot_top:.1f} mm\nbase", x_ref0=-r_base, x_ref1=-r_col, text_dx=-3.0, ha="right", fontsize=8.4)
        _draw_vdim(ax, -66.0, p.z_cap_bot_top, p.z_cap_top_bot, f"{p.exposed_glass_window:.1f} mm\nwindow", x_ref0=-r_col, x_ref1=-r_col, text_dx=-3.0, ha="right", fontsize=8.4)
        _draw_vdim(ax, -66.0, p.z_cap_top_top, p.z_core_top, f"{p.core_protrusion_mm:.1f} mm\nchimney", x_ref0=-19.4, x_ref1=-r_core, text_dx=-3.0, ha="right", fontsize=8.4)

        # Right side horizontal diameters & key internal callouts
        _draw_hdim(ax, p.z_cap_top_top + 7.5, -r_brim, r_brim, f"Ø{p.cap_top_brim_od:.0f} mm rain eaves", z_ref0=p.z_cap_top_brim_rim_top, z_ref1=p.z_cap_top_brim_rim_top, text_dz=3.2, va="bottom", fontsize=8.5)
        _draw_vdim(ax, 66.0, p.z_glass_bot, p.z_glass_top, f"{p.glass_length:.0f} mm\nXT PMMA\n(Ø{p.glass_od_nom:.0f}×{p.glass_id_nom:.0f})", x_ref0=r_shroud, x_ref1=r_shroud, text_dx=3.5, ha="left", fontsize=8.3)
        _draw_vdim(ax, 66.0, 0.0, p.z_lid_bot_start, f"{p.z_lid_bot_start:.1f} mm skirt", x_ref0=r_base, x_ref1=42.0, text_dx=3.5, ha="left", fontsize=8.3)

        _draw_callout(ax, (15.0, p.z_hang_hole), (56.0, p.z_hang_hole - 6.0), "Ø8 mm hang hole\n+ Signal-Orange bushing")
        _draw_callout(ax, (26.0, p.pcb_z_fcu), (56.0, p.pcb_z_fcu + 8.0), "Driver PCB (36×46 mm)\non M2.5 brass inserts")
        _draw_callout(ax, (15.0, 11.0), (56.0, 30.0), "SW1 toggle + boot\n(2.5 mm ground clr)")
        _draw_callout(ax, (-18.5, 12.0), (-56.0, -10.0), "2-piece split clamp\n+ 90° USB-C plug", ha="right")
    else:
        # XZ plane: show Al core 200 mm length, 32 mm LED star pitch, solid hub & anchor/lock screws
        _draw_vdim(ax, -66.0, p.z_core_bot, p.z_core_top, f"{p.core_length:.0f} mm\nstock Al tube", x_ref0=-r_core, x_ref1=-r_core, text_dx=-3.0, ha="right", fontsize=8.5)
        _draw_vdim(ax, 66.0, p.z_led_vis, p.z_led_uv, f"{p.axial_uv_to_vis_mm:.0f} mm\nstar pitch", x_ref0=20.0, x_ref1=20.0, text_dx=3.5, ha="left", fontsize=8.5)
        _draw_hdim(ax, p.z_cap_top_top + 7.5, -r_brim, r_brim, f"Ø{p.cap_top_brim_od:.0f} mm eaves / Ø{p.cap_top_skirt_od:.0f} mm collar", z_ref0=p.z_cap_top_brim_rim_top, z_ref1=p.z_cap_top_brim_rim_top, text_dz=3.2, va="bottom", fontsize=8.4)

        _draw_callout(ax, (15.0, p.z_hang_hole), (56.0, p.z_hang_hole - 6.0), "Ø8 mm hang hole\n+ 8 mm finial cap")
        _draw_callout(ax, (22.0, p.z_cap_top_lock), (56.0, p.z_cap_top_lock - 6.0), "2× M3×10 top lock\n(4.6 mm solid shoulder)")
        _draw_callout(ax, (18.0, p.z_led_uv), (56.0, p.z_led_uv + 16.0), "8× 20 mm Cu DTP stars\n(4 UV + 4 Vis)")
        _draw_callout(ax, (26.5, p.z_glass_bot + 7.5), (56.0, p.z_glass_bot + 10.0), "Solid R=24.4 mm hub\n+ 60×3.5 VMQ50 O-ring")
        _draw_callout(ax, (6.5, p.cap_bot_ceiling_z + 3.0), (56.0, p.cap_bot_ceiling_z + 2.0), "2× M3×12 dry-bay anchor\n(5.5 mm bulkhead, 0 side holes)")
        d12_len = round((p.pcb_z_fcu - 0.80 - 1.40) - (p.z_lid_bot_start - 1.0), 1)
        _draw_callout(ax, (16.0, 28.0), (56.0, 26.0), f"{d12_len:.1f} mm D12 lightpipe\n(45° side-visible tip)")

    # Crisp specification & approximate weight card (top-right corner)
    mass_text = (
        f"Approx. Weight: ~{mass['total_fdm_g']:.0f} g\n"
        f"  • Black ASA (FDM):  ~{mass['asa_fdm_62pct_g']:.0f} g\n"
        f"  • 30×30×3 Al core:   {mass['al_core_3mm_g']:.0f} g\n"
        f"  • XT PMMA shroud:     {mass['uvt_pmma_shroud_g']:.0f} g\n"
        f"  • Stars / PCB / HW:  {mass['elec_stars_hardware_g']:.0f} g\n"
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
        bounds=(-100, 100, 0, 100, -10, 275),
        title="Section XZ (Y = 0) — Rev 4.6 Compact Base, Solid Hubs, Dry-Bay Anchor & Lofted Roof",
        cam_pos=[(0, -690, 136), (0, 0, 136), (0, 0, 1)],
        plane="XZ",
        out_path=cad_dir / "assembly_section_xz.png",
    )
    render_section_annotated(
        parts, p, mass,
        bounds=(-100, 0, -100, 100, -10, 275),
        title="Section YZ (X = 0) — Rev 4.6 Compact Base, Horizontal PCB, Split Clamp & SW1",
        cam_pos=[(690, 0, 136), (0, 0, 136), (0, 0, 1)],
        plane="YZ",
        out_path=cad_dir / "assembly_section_yz.png",
    )
    render_cap_detail(cad_dir / "mech_lid_bot.stl", "MECH-LID-BOT (Recessed Ø79.4 + Split Port + Interior Vent + D12)", 22.0, cad_dir / "lid_bot_detail.png")
    render_cap_detail(cad_dir / "mech_cap_bot.stl", "MECH-CAP-BOT (Compact 80.0 mm Tapered Frustum + Intact Hub + M2.5 Standoffs)", 40.0, cad_dir / "cap_bot_detail.png")
    render_cap_detail(cad_dir / "mech_cap_top.stl", "MECH-CAP-TOP (Lofted Square-to-Round Roof + Solid R=24.4 Hub)", 177.0, cad_dir / "cap_top_detail.png")
    print("Rendered all 6 Rev 4.6 CAD PNGs with orthographic dimensions & weight badges cleanly.")


if __name__ == "__main__":
    main()
