#!/usr/bin/env python3
"""
Headless PyVista 3D CAD Renderer for LepiLED DIY Maxi Switch (M3).
Must be run under `xvfb-run -a /home/alimuldal/.local/share/lepiled-cad-venv/bin/python render_cad.py`.

Generates:
  - assembly_iso.png
  - assembly_section_xz.png
  - assembly_section_yz.png
  - cap_bot_detail.png
  - cap_top_detail.png
  - cap_bot_usbc_detail.png
"""

from __future__ import annotations

from pathlib import Path
import pyvista as pv


PART_STYLES = {
    "hs_bot":            dict(color="#22252a", opacity=1.0),
    "hs_top":            dict(color="#22252a", opacity=1.0),
    "adapt_bot":         dict(color="#b8c0c8", opacity=1.0),
    "adapt_top":         dict(color="#b8c0c8", opacity=1.0),
    "spacer_washers":    dict(color="#e2e8f0", opacity=1.0),
    "tim_pcb":           dict(color="#5599cc", opacity=1.0),
    "pcb_assy":          dict(color="#1f6f3b", opacity=1.0),
    "cap_bot":           dict(color="#d96b27", opacity=1.0),
    "cap_top":           dict(color="#d96b27", opacity=1.0),
    "hs_core":           dict(color="#30343b", opacity=1.0),
    "anchor_bot":        dict(color="#9aa5b1", opacity=1.0),
    "anchor_top":        dict(color="#a8b2bc", opacity=1.0),
    "fasteners_anchors": dict(color="#dbe2ea", opacity=1.0),
    "eye_bolt":          dict(color="#cfd6de", opacity=1.0),
    "glass_tube":        dict(color="#bfe6ff", opacity=0.28),
    "mcpcbs":            dict(color="#e5e7eb", opacity=1.0),
    "sw1_assy":          dict(color="#b03030", opacity=1.0),
    "m16_assy":          dict(color="#4a5058", opacity=1.0),
}


def load_parts(parts_dir: Path) -> dict[str, pv.PolyData]:
    return {k: pv.read(str(parts_dir / f"{k}.stl")) for k in PART_STYLES}


def render_assembly_iso(parts: dict[str, pv.PolyData], out_path: Path) -> None:
    pl = pv.Plotter(off_screen=True, window_size=(1200, 1600))
    pl.set_background("white")
    for k, mesh in parts.items():
        st = PART_STYLES[k]
        pl.add_mesh(mesh, color=st["color"], opacity=st["opacity"], smooth_shading=True, split_sharp_edges=True)
    # Aim slightly above mid-Z with extra distance so top title sits cleanly above MECH-EYE-1
    pl.camera_position = [(540, -560, 355), (0, 0, 205), (0, 0, 1)]
    pl.add_title("LepiLED DIY Maxi Switch (M3) — Full Assembly", font_size=13, color="black")
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
    pl.add_title(title, font_size=13, color="black")
    pl.add_axes()
    pl.screenshot(str(out_path))
    pl.close()


def render_cap_detail(stl_path: Path, title: str, z_mid: float, out_path: Path) -> None:
    mesh = pv.read(str(stl_path))
    pl = pv.Plotter(off_screen=True, shape=(1, 2), window_size=(1600, 800))
    pl.set_background("white")

    # Top-isometric view (tilted slightly toward -Y/+X cutouts)
    pl.subplot(0, 0)
    pl.add_mesh(mesh, color="#d96b27", smooth_shading=True, split_sharp_edges=True)
    pl.camera_position = [(130, -130, z_mid + 115), (0, 0, z_mid), (0, 0, 1)]
    pl.add_text(f"{title} — Top Isometric", font_size=11, color="black")

    # Bottom-isometric view
    pl.subplot(0, 1)
    pl.add_mesh(mesh, color="#d96b27", smooth_shading=True, split_sharp_edges=True)
    pl.camera_position = [(155, -155, z_mid - 135), (0, 0, z_mid), (0, 0, 1)]
    pl.add_text(f"{title} — Bottom Isometric", font_size=11, color="black")

    pl.screenshot(str(out_path))
    pl.close()


def main() -> None:
    cad_dir = Path(__file__).resolve().parent
    parts = load_parts(cad_dir / "parts_stl")

    render_assembly_iso(parts, cad_dir / "assembly_iso.png")
    render_section(
        parts,
        bounds=(-100, 100, 0, 100, -10, 420),  # keep Y >= 0 half, looking from -Y
        title="Section XZ (Y = 0) — Decoupled Dual Heatsink, Anchors & SW1",
        cam_pos=[(0, -820, 200), (0, 0, 200), (0, 0, 1)],
        out_path=cad_dir / "assembly_section_xz.png",
    )
    render_section(
        parts,
        bounds=(-100, 0, -100, 100, -10, 420),  # keep X <= 0 half, looking from +X
        title="Section YZ (X = 0) — Captive M16 Hex, J1/TP1/TP2 Pocket & Core",
        cam_pos=[(820, 0, 200), (0, 0, 200), (0, 0, 1)],
        out_path=cad_dir / "assembly_section_yz.png",
    )
    render_cap_detail(cad_dir / "mech_cap_bot.stl", "MECH-CAP-BOT (M16)", 108.5, cad_dir / "cap_bot_detail.png")
    render_cap_detail(cad_dir / "mech_cap_top.stl", "MECH-CAP-TOP (Flat)", 283.25, cad_dir / "cap_top_detail.png")
    render_cap_detail(cad_dir / "mech_cap_bot_usbc.stl", "MECH-CAP-BOT-USBC", 108.5, cad_dir / "cap_bot_usbc_detail.png")
    print("Rendered all 6 CAD PNGs cleanly.")


if __name__ == "__main__":
    main()
