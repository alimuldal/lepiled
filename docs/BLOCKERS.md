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

## 2. Missing System Software (Required for Milestone M2)

### B2. Missing `kicad` / `kicad-cli` / `gerbv`
- **Status:** Not installed on host (`command -v kicad kicad-cli gerbv` returns non-zero); installing system packages requires `sudo`.
- **Impact:**
  - **Milestone M1 (Current):** **Not blocked.** Schematic capture (`schemdraw` + `inkscape` vector PDF/PNG export) and SPICE/tolerance circuit simulation (`ngspice` + `scipy`) run completely in user-space.
  - **Milestone M2 (PCB Design & Manufacturing Outputs):** Automated Electrical Rules Check (`kicad-cli sch erc`), Design Rules Check (`kicad-cli pcb drc`), Gerber/Excellon export (`kicad-cli pcb export gerbers/drill`), and Gerber visual inspection (`gerbv`) require KiCad and `gerbv` (or a user-space AppImage/extracted package if viable).
- **Resolution Command (requires `sudo`):**
  ```bash
  sudo apt update && sudo apt install -y kicad gerbv
  ```

---

## 3. Resolved / Mitigated Tooling (No Blocker)

### M1. Open-Source SPICE Simulator (`ngspice 45.2+ds-1`) — **NOT BLOCKED**
- **Status:** System `/usr/bin/ngspice` is not installed (`sudo` unavailable), **but `ngspice 45.2+ds-1` with full XSPICE codemodels is provisioned and verified in user-space** without root privileges.
- **Location:** `/home/alimuldal/.local/share/lepiled-tools/bin/ngspice` (extracted from Ubuntu `ngspice_45.2+ds-1_amd64.deb` with `spinit` codemodel paths patched and `SPICE_SCRIPTS` wrapper).
- **Python Environment:** `/home/alimuldal/.local/share/lepiled-venv` (`Python 3.14.4`, `numpy 2.5.5`, `scipy 1.18.1`, `matplotlib 3.11.2`, `schemdraw 0.23`, `cairosvg 2.9.1`).
- **Verification:** `ngspice -v` and batch netlist runs (`ngspice -b`) execute with exit code 0 and zero warnings/errors.
