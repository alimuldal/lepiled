#!/usr/bin/env python3
"""
Headless PyVista 3D CAD Renderer for LepiLED DIY Maxi Switch (Rev 4.5 — Compact, Horizontal PCB, Radial O-Rings & M20 Split Gland).
Must be run under `xvfb-run -a /home/alimuldal/.local/share/lepiled-cad-venv/bin/python render_cad.py`.
"""

from __future__ import annotations

from pathlib import Path
import pyvista as pv


PART_STYLES = {
    "base_ring":      dict(color="#9c4514", opacity=1.0),  # Protective standing ring & switch/gland guard
    "lid_bot":        dict(color="#c25a1e", opacity=1.0),  # Bottom lid w/ radial O-ring spigot
    "cap_bot":        dict(color="#d96b27", opacity=1.0),  # Seamless shell w/ horizontal PCB standoffs
    "cap_top":        dict(color="#d96b27", opacity=1.0),  # 15-deg sloped conical Ø88 mm rain roof
    "plug_top":       dict(color="#c25a1e", opacity=1.0),
    "pcb_assy":       dict(color="#1f6f3b", opacity=1.0),  # Horizontal driver_pcb + all 57 SMDs
    "hs_core":        dict(color="#b8c0c8", opacity=1.0),  # Bare 30x30x3x200 mm Al 6063-T6
    "fasteners_m3":   dict(color="#dbe2ea", opacity=1.0),  # M3 + M2.5 screws
    "glass_tube":     dict(color="#c8ebff", opacity=0.28), # Clear extruded XT PMMA Ø60x54x115 mm
    "dtp_stars":      dict(color="#c87533", opacity=1.0),  # 8x 20 mm Copper DTP stars
    "sw1_assy":       dict(color="#b03030", opacity=1.0),  # Bottom-mounted C&K 7211 DPDT + boot
    "gland_usbc":     dict(color="#333840", opacity=1.0),  # M20 IP68 split waterproof cable gland
    "usbc_plug_assy": dict(color="#55606e", opacity=1.0),  # Compact 90-deg USB-C PD plug
}


def load_parts(parts_dir: Path) -> dict[str, pv.PolyData]:
    return {k: pv.read(str(parts_dir / f"{k}.stl")) for k in PART_STYLES}


def render_assembly_iso(parts: dict[str, pv.PolyData], out_path: Path) -> None:
    pl = pv.Plotter(off_screen=True, window_size=(1200, 1600))
    pl.set_background("white")
    for k, mesh in parts.items():
        st = PART_STYLES[k]
        pl.add_mesh(mesh, color=st["color"], opacity=st["opacity"], smooth_shading=True, split_sharp_edges=True)
    pl.camera_position = [(420, -450, 240), (0, 0, 118), (0, 0, 1)]
    pl.add_title("LepiLED Rev 4.5 (30x30x3 Core, Horizontal PCB, Radial O-Rings & M20 Split Gland)", font_size=11, color="black")
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
    pl.add_title(title, font_size=11, color="black")
    pl.add_axes()
    pl.screenshot(str(out_path))
    pl.close()


def render_cap_detail(stl_path: Path, title: str, z_mid: float, out_path: Path, color: str = "#d96b27") -> None:
    mesh = pv.read(str(stl_path))
    pl = pv.Plotter(off_screen=True, shape=(1, 2), window_size=(1600, 800))
    pl.set_background("white")

    pl.subplot(0, 0)
    pl.add_mesh(mesh, color=color, smooth_shading=True, split_sharp_edges=True)
    pl.camera_position = [(130, -130, z_mid + 110), (0, 0, z_mid), (0, 0, 1)]
    pl.add_text(f"{title} — Top Isometric", font_size=11, color="black")

    pl.subplot(0, 1)
    pl.add_mesh(mesh, color=color, smooth_shading=True, split_sharp_edges=True)
    pl.camera_position = [(145, -145, z_mid - 125), (0, 0, z_mid), (0, 0, 1)]
    pl.add_text(f"{title} — Bottom Isometric", font_size=11, color="black")

    pl.screenshot(str(out_path))
    pl.close()


def main() -> None:
    cad_dir = Path(__file__).resolve().parent
    parts = load_parts(cad_dir / "parts_stl")

    render_assembly_iso(parts, cad_dir / "assembly_iso.png")
    render_section(
        parts,
        bounds=(-100, 100, 0, 100, -35, 275),
        title="Section XZ (Y = 0) — Rev 4.5 Radial O-Rings, Direct Core Lock & 25-deg Rain Roof",
        cam_pos=[(0, -680, 118), (0, 0, 118), (0, 0, 1)],
        out_path=cad_dir / "assembly_section_xz.png",
    )
    render_section(
        parts,
        bounds=(-100, 0, -100, 100, -35, 275),
        title="Section YZ (X = 0) — Rev 4.5 Horizontal PCB, 90-deg USB-C, M20 Split Gland & SW1",
        cam_pos=[(680, 0, 118), (0, 0, 118), (0, 0, 1)],
        out_path=cad_dir / "assembly_section_yz.png",
    )
    render_cap_detail(cad_dir / "mech_lid_bot.stl", "MECH-LID-BOT (Radial Spigot + M20 Gland + SW1 + Vent + D12)", 6.0, cad_dir / "lid_bot_detail.png", color="#c25a1e")
    render_cap_detail(cad_dir / "mech_cap_bot.stl", "MECH-CAP-BOT (Horizontal PCB Standoffs + 9x7.5mm Wire Slots)", 38.0, cad_dir / "cap_bot_detail.png")
    render_cap_detail(cad_dir / "mech_cap_top.stl", "MECH-CAP-TOP (25-deg Sloped Conical Ø88mm Rain Roof)", 182.0, cad_dir / "cap_top_detail.png")
    print("Rendered all 6 Rev 4.5 CAD PNGs cleanly.")


if __name__ == "__main__":
    main()
