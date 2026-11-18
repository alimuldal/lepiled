# Project Blockers & Environment Notes

This file tracks external access blockers, missing system-level software requiring administrator (`sudo`) privileges, and user-space workarounds implemented so autonomous development can continue without interactive pauses.

---

## 1. Hard External Blockers (Action Required by User)

### B1. Private Reference Google Sheet (`HTTP 401` / Login-Gated)
- **Resource URL:** `https://docs.google.com/spreadsheets/d/1VNcXHNNrZ-xlLQjyCB3U-OSda4Kfq_rMDRMXmeiYSrs/edit?usp=sharing`
- **Observed Behaviour:** Verified across 5 endpoints (`/edit`, `/export?format=csv`, `/export?format=xlsx`, `/gviz/tq`, `/htmlview`) on 2026-11-18: returns `HTTP/2 401` or `HTTP/2 302` redirect to `https://accounts.google.com/ServiceLogin`.
- **Impact:** Any earlier part links, prices, or notes stored exclusively inside that spreadsheet are inaccessible to autonomous tooling.
- **Mitigation:** All active, passive, emitter, and electro-mechanical component selections have been independently grounded directly from primary vendor PDF datasheets and live UK distributor searches (`digikey.co.uk`, `mouser.co.uk`, `uk.farnell.com`, `uk.rs-online.com`). If the user shares the sheet publicly ("Anyone with the link can view") or exports a CSV into `docs/`, those notes can be cross-checked in a follow-up pass.

---

## 2. Missing System Software

*(None currently blocking — all required EDA, schematic, simulation, and Gerber tools are provisioned in user-space without `sudo`; see Section 3.)*

---

## 3. Resolved / Mitigated Tooling (No Blocker)

### M1. Open-Source SPICE Simulator (`ngspice 45.2+ds-1`) — **NOT BLOCKED**
- **Status:** System `/usr/bin/ngspice` is not installed (`sudo` unavailable), **but `ngspice 45.2+ds-1` with full XSPICE codemodels is provisioned and verified in user-space** without root privileges.
- **Location:** `/home/alimuldal/.local/share/lepiled-tools/bin/ngspice` (extracted from Ubuntu `ngspice_45.2+ds-1_amd64.deb` with `spinit` codemodel paths patched and `SPICE_SCRIPTS` wrapper).
- **Python Environment:** `/home/alimuldal/.local/share/lepiled-venv` (`Python 3.14.4`, `numpy 2.5.5`, `scipy 1.18.1`, `matplotlib 3.11.2`, `schemdraw 0.23`, `cairosvg 2.9.1`).
- **Verification:** `ngspice -v` and batch netlist runs (`ngspice -b`) execute with exit code 0 and zero warnings/errors.

### B2 / M2. Open-Source PCB EDA & Gerber Viewer (`KiCad 9.0.8` + `gerbv 2.10.0`) — **RESOLVED IN USER-SPACE (NO BLOCKER)**
- **Status:** System `/usr/bin/kicad`, `/usr/bin/kicad-cli`, and `/usr/bin/gerbv` are not installed (`sudo` unavailable), **but KiCad `9.0.8+dfsg-1` (`kicad-cli`, Python `pcbnew` 9.0.8), `kicad-symbols 9.0.7-1`, `kicad-footprints 9.0.7-1`, and `gerbv 2.10.0-2build1` are provisioned and verified in user-space** without root privileges.
- **Location & Wrappers:**
  - Extracted packages: `/home/alimuldal/.local/share/lepiled-kicad/` (downloaded via `https://mirrors.edge.kernel.org/ubuntu/` with `sha512sum` verification against `apt-get download --print-uris`).
  - `/home/alimuldal/.local/share/lepiled-tools/bin/kicad-cli` (`bwrap --ro-overlay /usr/share` + `LD_LIBRARY_PATH` + `XDG_CONFIG_HOME` isolation).
  - `/home/alimuldal/.local/share/lepiled-tools/bin/kicad-python` (`bwrap --ro-overlay /usr/share` + `PYTHONPATH` exposing `pcbnew` 9.0.8 inside `/home/alimuldal/.local/share/lepiled-venv/bin/python`).
  - `/home/alimuldal/.local/share/lepiled-tools/bin/gerbv` (`LD_LIBRARY_PATH` wrapper for `/home/alimuldal/.local/share/lepiled-kicad/usr/bin/gerbv`).
- **Verification:**
  - `kicad-cli --version` -> `9.0.8` (exit code `0`).
  - `kicad-python -c "import pcbnew; print(pcbnew.Version())"` -> `9.0.8` (exit code `0`).
  - `gerbv --version` -> `gerbv version` (exit code `0`).

### B3 / M3. Parametric 3D CAD & FVM Thermal Toolchain (`build123d 0.13.0` + `lepiled-cad-venv`) — **RESOLVED IN USER-SPACE (NO BLOCKER)**
- **Status:** System-wide CAD/mesh/rendering packages are not installed (`sudo` unavailable), **but a complete Python `3.14.4` CAD, B-Rep, mesh, and offscreen rendering environment is provisioned and verified in user-space** without root privileges.
- **Location:** `/home/alimuldal/.local/share/lepiled-cad-venv/bin/python` (`Python 3.14.4`), paired with `/usr/bin/xvfb-run` for headless offscreen rendering.
- **Installed Key Packages:** `build123d 0.13.0`, `cadquery-ocp-novtk 8.0.1.1.0`, `trimesh 5.2.1`, `manifold3d 3.5.5`, `pyvista 0.49.2`, `vtk 9.7.2`, `numpy-stl 4.1.4`, `numpy 2.5.5`, `scipy 1.18.1`, `matplotlib 3.11.2`.
- **Verification:**
  - `/home/alimuldal/.local/share/lepiled-cad-venv/bin/python mechanical_design/cad/params.py` -> `34/34` parametric checks `PASS` (exit code `0`).
  - `/home/alimuldal/.local/share/lepiled-cad-venv/bin/python mechanical_design/cad/generate_cad.py` -> `0/612` all-pairs B-Rep overlaps, `84/84` insertion checks pass (exit code `0`).
  - `xvfb-run -a /home/alimuldal/.local/share/lepiled-cad-venv/bin/python mechanical_design/cad/render_cad.py` -> renders 6 CAD PNGs (exit code `0`).
