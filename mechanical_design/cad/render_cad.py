#!/usr/bin/env python3
"""
Headless PyVista 3D CAD Renderer for LepiLED DIY Maxi Switch (Rev 4.3 — Field-Robust, Lightweight & Weatherproofed).
Must be run under `xvfb-run -a /home/alimuldal/.local/share/lepiled-cad-venv/bin/python render_cad.py`.
"""

from __future__ import annotations

from pathlib import Path
import pyvista as pv


PART_STYLES = {
    "base_ring":      dict(color="#9c4514", opacity=1.0),  # Protective standing ring & switch guard
    "lid_bot":        dict(color="#c25a1e", opacity=1.0),
    "cap_bot":        dict(color="#d96b27", opacity=1.0),  # Contoured lightweight shell
    "cap_top":        dict(color="#d96b27", opacity=1.0),  # Integral Ø108 mm drip-brim
    "plug_top":       dict(color="#c25a1e", opacity=1.0),
    "rain_hat":       dict(color="#9c4514", opacity=1.0),  # Detachable pack-flat Ø144 mm rain hat
    "plug_bot":       dict(color="#e08040", opacity=1.0),
    "pcb_assy":       dict(color="#1f6f3b", opacity=1.0),
    "hs_core":        dict(color="#b8c0c8", opacity=1.0),  # Bare mill-finish 3 mm Al 6063
    "fasteners_m3":   dict(color="#dbe2ea", opacity=1.0),
    "glass_tube":     dict(color="#c8ebff", opacity=0.28), # Shatter-resistant UVT PMMA acrylic shroud
    "dtp_stars":      dict(color="#c87533", opacity=1.0),  # 8x 20 mm Copper DTP stars
    "sw1_assy":       dict(color="#b03030", opacity=1.0),  # Bottom-mounted C&K 7211 DPDT + boot
    "grommet_usbc":   dict(color="#333840", opacity=1.0),
    "usbc_plug_assy": dict(color="#55606e", opacity=1.0),
}


def load_parts(parts_dir: Path) -> dict[str, pv.PolyData]:
    return {k: pv.read(str(parts_dir / f"{k}.stl")) for k in PART_STYLES}


def render_assembly_iso(parts: dict[str, pv.PolyData], out_path: Path) -> None:
    pl = pv.Plotter(off_screen=True, window_size=(1200, 1600))
    pl.set_background("white")
    for k, mesh in parts.items():
        st = PART_STYLES[k]
        pl.add_mesh(mesh, color=st["color"], opacity=st["opacity"], smooth_shading=True, split_sharp_edges=True)
    pl.camera_position = [(520, -550, 310), (0, 0, 160), (0, 0, 1)]
    pl.add_title("LepiLED Rev 4.3 (UVT PMMA Shroud + Bottom SW1 + Dual Rain Roof)", font_size=12, color="black")
    pl.add_axes()
    pl.screenshot(str(out_path))
    pl.close()


def render_section(parts: dict[str, pv.PolyData], bounds: tuple[float, float, float, float, float, float],
                   title: str, cam_pos: list, out_path: Path) -> None:
    pl = pv.Plotter(off_screen=True, window_size=(1200, 1600))
    pl.set_background("white")
    for k, mesh in parts.items():
        st = PART_STYLES[k]
        clipped = mesh.clip_box(bounds=bounds, invert=False)
        if clipped.n_cells > 0:
            op = 0.35 if k == "glass_tube" else 1.0
            pl.add_mesh(clipped, color=st["color"], opacity=op, smooth_shading=False, show_edges=False)
    pl.camera_position = cam_pos
    pl.add_title(title, font_size=12, color="black")
    pl.add_axes()
    pl.screenshot(str(out_path))
    pl.close()


def render_cap_detail(stl_path: Path, title: str, z_mid: float, out_path: Path, color: str = "#d96b27") -> None:
    mesh = pv.read(str(stl_path))
    pl = pv.Plotter(off_screen=True, shape=(1, 2), window_size=(1600, 800))
    pl.set_background("white")

    pl.subplot(0, 0)
    pl.add_mesh(mesh, color=color, smooth_shading=True, split_sharp_edges=True)
    pl.camera_position = [(140, -140, z_mid + 120), (0, 0, z_mid), (0, 0, 1)]
    pl.add_text(f"{title} — Top Isometric", font_size=11, color="black")

    pl.subplot(0, 1)
    pl.add_mesh(mesh, color=color, smooth_shading=True, split_sharp_edges=True)
    pl.camera_position = [(160, -160, z_mid - 140), (0, 0, z_mid), (0, 0, 1)]
    pl.add_text(f"{title} — Bottom Isometric", font_size=11, color="black")

    pl.screenshot(str(out_path))
    pl.close()


def main() -> None:
    cad_dir = Path(__file__).resolve().parent
    parts = load_parts(cad_dir / "parts_stl")

    render_assembly_iso(parts, cad_dir / "assembly_iso.png")
    render_section(
        parts,
        bounds=(-120, 120, 0, 120, -30, 360),
        title="Section XZ (Y = 0) — Rev 4.3 Dual Rain Roof, Solid +X Wall & Base Stand Ring",
        cam_pos=[(0, -820, 160), (0, 0, 160), (0, 0, 1)],
        out_path=cad_dir / "assembly_section_xz.png",
    )
    render_section(
        parts,
        bounds=(-120, 0, -120, 120, -30, 360),
        title="Section YZ (X = 0) — Rev 4.3 Bottom SW1, Contoured Shell, Grommet & Rain Hat",
        cam_pos=[(820, 0, 160), (0, 0, 160), (0, 0, 1)],
        out_path=cad_dir / "assembly_section_yz.png",
    )
    render_cap_detail(cad_dir / "mech_lid_bot.stl", "MECH-LID-BOT (Bottom SW1 + PCB Pins)", 10.0, cad_dir / "lid_bot_detail.png", color="#c25a1e")
    render_cap_detail(cad_dir / "mech_cap_bot.stl", "MECH-CAP-BOT (Contoured Lightweight Shell)", 45.0, cad_dir / "cap_bot_detail.png")
    render_cap_detail(cad_dir / "mech_cap_top.stl", "MECH-CAP-TOP (Integral Ø108mm Drip-Brim)", 224.0, cad_dir / "cap_top_detail.png")
    print("Rendered all 6 Rev 4.3 CAD PNGs cleanly.")


if __name__ == "__main__":
    main()
