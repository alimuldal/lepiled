#!/usr/bin/env python3
"""
Export the canonical LepiLED Rev 4.0 (Option 2: 20 V USB-C PD + Dual AL8860 Buck)
schematic directly from the native KiCad 9.0.8 schematic (`pcb_design/driver_pcb/driver_pcb.kicad_sch`)
into `circuit_design/schematic.{pdf,svg,png}` and verify 0 ERC violations.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCH_PATH = REPO_ROOT / "pcb_design" / "driver_pcb" / "driver_pcb.kicad_sch"
OUT_DIR = REPO_ROOT / "circuit_design"
KCLI = "/usr/bin/kicad-cli"


def main() -> None:
    if not SCH_PATH.exists():
        raise FileNotFoundError(f"Missing native KiCad schematic: {SCH_PATH}. Run pcb_design/driver_pcb/build_driver_pcb.py first.")

    subprocess.run(
        [KCLI, "sch", "erc", "--severity-all", "--exit-code-violations",
         "-o", str(SCH_PATH.with_name("erc_report.rpt")), str(SCH_PATH)],
        check=True,
    )
    subprocess.run([KCLI, "sch", "export", "pdf", "-o", str(OUT_DIR / "schematic.pdf"), str(SCH_PATH)], check=True)
    subprocess.run([KCLI, "sch", "export", "svg", "-o", str(OUT_DIR), str(SCH_PATH)], check=True)
    svg_gen = OUT_DIR / "driver_pcb.svg"
    if svg_gen.exists():
        shutil.move(str(svg_gen), str(OUT_DIR / "schematic.svg"))
    subprocess.run(
        ["pdftoppm", "-png", "-r", "180", "-singlefile",
         str(OUT_DIR / "schematic.pdf"), str(OUT_DIR / "schematic")],
        check=True,
    )
    print(f"Exported native KiCad 9.0.8 schematic to {OUT_DIR / 'schematic.pdf'}, .svg, .png (0 ERC violations).")


if __name__ == "__main__":
    main()
