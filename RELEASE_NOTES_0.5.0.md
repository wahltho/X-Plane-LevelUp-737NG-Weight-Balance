# LevelUp 737NG Weight & Balance v0.5.0

For LevelUp using the unmodified upstream Zibo 4.05.35 plugin and Lua.
Supports the -600, -700, -800, -900 and -900ER in one package.

## Changes

- Reads W&B masses, station geometry/capacities and tank geometry from the
  loaded aircraft's DataRefs instead of fixed per-variant numeric tables.
- Reads MAC, fixed CG limits and station/tank layout from the active ACF.
- Uses shared geometry for OEW/ZFW/TOW/LW CG and the existing FMC CG handoff.
- Refreshes metadata on aircraft reload/change and retains strict payload
  ownership, including read-only external payload and invalid-data protection.
- Valid numeric W&B edits no longer require a new patch. Supported station
  order, names and tank layout are still checked.

No ACFs, airfoils, flight-model tuning or trim-table changes are included.
The existing loader positions and compatibility hooks remain unchanged.

## Install / upgrade

1. Close X-Plane and back up the LevelUp aircraft.
2. Download **LevelUp-737NG-Weight-Balance-v0.5.0.zip** (not Source code).
3. Extract all contents, including subdirectories, directly into
   `plugins/xlua/scripts/B738.tablet/`.
4. Run `py z_Install_LevelUp_NG_WB.py` on Windows, or
   `python3 z_Install_LevelUp_NG_WB.py` on macOS/Linux.
5. Restart X-Plane. Do not uninstall the previous version first.

The ZIP includes the installer, Lua modules and instructions, but no ACF files.
The Maintenance Toolkit module contract is included; availability through its
consolidated update depends on the Toolkit importing this release.

## Verification

Automated Lua 5.1/math/ownership/reload regressions, all five current author
ACFs, installer/migration/patch-coexistence, Toolkit integrity and fresh ZIP
installation checks pass, including full patched Tablet/FMS Lua syntax.
No new simulator-runtime validation was performed. Detailed evidence and
remaining runtime checks are included in the ZIP.
