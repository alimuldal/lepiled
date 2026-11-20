#!/usr/bin/env python3
"""
Headless PyVista 3D CAD Renderer for LepiLED DIY Maxi Switch (Rev 4.6 — "Field Lantern":
Matte-Black ASA + Matte-Black Al Chimney + Warm Copper Stars + Signal-Orange Hang-Hole Touchpoint).
Must be run under `xvfb-run -a /home/alimuldal/.local/share/lepiled-cad-venv/bin/python render_cad.py`.
"""

from __future__ import annotations

from pathlib import Path
import pyvista as pv


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


def render_section(parts: dict[str, pv.PolyData], bounds: tuple[float, float, float, float, float, float],
                   title: str, cam_pos: list, out_path: Path) -> None:
    pl = pv.Plotter(off_screen=True, window_size=(1200, 1600))
    pl.set_background("#f4f6f8")
    for k, mesh in parts.items():
        st = PART_STYLES[k]
        clipped = mesh.clip_box(bounds=bounds, invert=False)
        if clipped.n_cells > 0:
            op = 0.32 if k == "glass_tube" else 1.0
            pl.add_mesh(clipped, color=st["color"], opacity=op, smooth_shading=False, show_edges=False)
    pl.camera_position = cam_pos
    pl.add_title(title, font_size=10, color="black")
    pl.add_axes()
    pl.screenshot(str(out_path))
    pl.close()


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
    parts = load_parts(cad_dir / "parts_stl")

    render_assembly_iso(parts, cad_dir / "assembly_iso.png")
    render_section(
        parts,
        bounds=(-100, 100, 0, 100, -10, 290),
        title="Section XZ (Y = 0) — Rev 4.6 Intact R=24.4 Hubs, Dry-Bay Core Anchor & Lofted Roof",
        cam_pos=[(0, -690, 140), (0, 0, 140), (0, 0, 1)],
        out_path=cad_dir / "assembly_section_xz.png",
    )
    render_section(
        parts,
        bounds=(-100, 0, -100, 100, -10, 290),
        title="Section YZ (X = 0) — Rev 4.6 Horizontal PCB, 90-deg USB-C + Strain Relief, Split Clamp & SW1",
        cam_pos=[(690, 0, 140), (0, 0, 140), (0, 0, 1)],
        out_path=cad_dir / "assembly_section_yz.png",
    )
    render_cap_detail(cad_dir / "mech_lid_bot.stl", "MECH-LID-BOT (Recessed Ø78.6 + Split Port + Recessed Vent + D12)", 24.0, cad_dir / "lid_bot_detail.png")
    render_cap_detail(cad_dir / "mech_cap_bot.stl", "MECH-CAP-BOT (Unified Tapered Frustum + Intact Core Hub + M2.5 Standoffs)", 50.0, cad_dir / "cap_bot_detail.png")
    render_cap_detail(cad_dir / "mech_cap_top.stl", "MECH-CAP-TOP (Lofted Square-to-Round Roof + Solid R=24.4 Hub)", 202.0, cad_dir / "cap_top_detail.png")
    print("Rendered all 6 Rev 4.6 CAD PNGs cleanly.")


if __name__ == "__main__":
    main()
