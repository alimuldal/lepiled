# LepiLED Repository Engineering Rules

These rules apply unconditionally to all edits, simulations, CAD rebuilds, figures, BOM updates, and documentation changes in this repository.

## 1. Frozen Ordered Hardware
- **Do not modify `driver_pcb` fabrication outputs** (`pcb_design/`) or SPICE circuit netlists (`circuit_design/sim/netlists/`) unless the user explicitly asks to revise the PCB/circuit. The `36.0 × 46.0 mm` 2-Reel Hybrid Lead-Free HASL `driver_pcb` has already been ordered from JLCPCB.

## 2. Single-Source-of-Truth (SSOT) & Figure Freshness (Mandatory)
Every generated figure, plot, render, and summary JSON in this repository **must** stay 100% synchronized with the current BOM, CAD geometry, circuit simulation, and thermal model:
- **Circuit Simulation (`circuit_design/sim/`):** Any edit to `COMPONENT_IDS.csv`, `models.lib`, `*.cir`, or `run_simulations.py` requires re-running `run_simulations.py` (regenerating `sim_summary.json` and all 3 `plot_*.png` figures with fresh SHA-256 `output_figure_hashes`), followed by re-running `thermal_analysis.py`.
- **Mechanical CAD & Renders (`mechanical_design/cad/`):** Any edit to `params.py`, `generate_cad.py`, or `render_cad.py` requires re-running `generate_cad.py` (regenerating STEP/STL exports, `cad_params.json`, and `cad_verification.json`), `xvfb-run -a render_cad.py` (regenerating all 6 CAD PNGs and `cad_render_manifest.json`), and `thermal_analysis.py`.
- **Thermal Model & BOM Material/Finish Parity (`mechanical_design/thermal/`, `bom/`):** Any change to core finish/emissivity (e.g., bare mill vs anodized/painted), chimney geometry, shroud material, PCB thermal bridge, or power dissipation requires updating `thermal_analysis.py`, regenerating `thermal_results.csv`, `thermal_summary.json`, and all 3 thermal PNGs (`thermal_margins.png`, `thermal_ambient_sweep.png`, `thermal_network_comparison.png`), and updating all affected tables/text in `README.md` and `mechanical_design/MECHANICAL_DESIGN.md`.
- **No Hardcoded Plot Annotations:** Derive plot reference lines, legends, geometry parameters, and material/finish titles dynamically from live simulation outputs and SSOT JSONs (`cad_params.json`, `sim_summary.json`, `thermal_summary.json`) rather than hardcoding stale thresholds or finishes in plotting scripts.
- **Visual Inspection:** After regenerating any PNG figure (SPICE, CAD, or thermal), visually inspect the updated image(s) to confirm titles, legends, annotations, and curves accurately reflect the latest design choices.

## 3. Automated Pre-Commit Verification Gate
- Before committing or reporting a design/BOM/simulation change as complete, run:
  ```bash
  /tmp/lepiled-venv/bin/python verify_all.py --check
  ```
- Every gate — PCB/Gerber audit, SPICE & figure hashes, CAD & render manifest hashes, Thermal & figure hashes, BOM ↔ Thermal core-finish parity, BOM 1:1 parity, and doc numeric/stale-token parity — **must pass**.

## 4. Documentation Style Hygiene
- Keep active project documentation (`README.md`, `bom/BOM.md`, `docs/ASSEMBLY_GUIDE.md`, `docs/BLOCKERS.md`, `docs/CHANGE_CHECKLIST.md`, `mechanical_design/*.md`) in calm, neutral, factual technical prose: zero exclamation marks (`!`, excluding Markdown image syntax `![...]`) and zero historical `Rev N` comparison prose (revision history belongs strictly in `docs/DESIGN_DECISIONS.md`).
