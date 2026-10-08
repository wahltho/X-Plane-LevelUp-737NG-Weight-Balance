# Installation guide

Version **0.5.3**. Automated regression and packaged-installation checks pass;
in-simulator acceptance remains pending. See `VALIDATION_0.5.3.md`.

## Requirements

- LevelUp 737NG Series using upstream Zibo 4.05.35 Tablet Lua and the
  unmodified upstream `zibomod.xpl`.
- All five LevelUp ACFs with the supported nine-station layout and valid
  numeric geometry; three fuel tanks with equal wing capacities.
  Pilot mass remains in empty mass, cabin crew/catering remain separate.
  See `DYNAMIC_AIRCRAFT_DATA.md`.
- Python 3. No compiler or plugin build is required.

The reference ACF SHA-256 values are recorded in `SOURCE.md`. They establish
provenance only; installation is controlled by the station/tank structure and numeric
sanity, not exact arms/masses or the whole-file hash. The role category is intentionally excluded
from the gate so that the current -900ER ACF and Jochen's announced correction
of its Galley F/A roles are both accepted.

## Install or upgrade

Close X-Plane and extract the complete ZIP outside the aircraft directory.
Do not pre-copy the Lua modules into the Tablet folder. From the package, run:

```text
python3 z_Install_LevelUp_NG_WB.py --aircraft-root "/path/to/LevelUp aircraft"
```

On Windows use `py -3`. Python 3.10 or newer is required. The installer checks
package hashes, all five aircraft contracts and the affected Lua layout before
changing files. It saves originals and its own installation receipt. Repeat the
command to update an installation that has this receipt, then restart X-Plane.

Older standalone installs without a receipt must first be removed with their
original installer and backups. Do not copy new runtime files over them or
delete their backup files to bypass the check. Manual installs and installations
owned by MTK are not automatically adopted.

Other correctly installed patches and unrelated Lua edits are preserved. Mixed
line endings, unknown W&B blocks or changed payloads block the operation.

## Capacity boundary

The figures below describe historical author ACFs; in 0.5.3 the loaded
DataRef maxima determine actual boundaries, including after author updates.

The ACF station maxima are authoritative. Rounded stock Tablet cargo values
are normalized to the exact active ACF maximum before any station or CG write:

- -700 Cargo 1/2 differ from the stock Tablet ceiling by `21.912 / 42.213 kg`.
- -600 Cargo 1/2 have the same exact maxima and margins as the -700.
- -800 and -900 Cargo 1/2 differ by `0.207 / 1.098 kg`.
- -900ER Cargo 1/2 differ by `0.207 / 87.280 kg`.
- -800 Galley F/A combined with half the cabin crew can exceed the `3000-lb`
  ACF station maximum by `24.823 / 72.823 kg` at the extreme Tablet entries.

Cargo normalization preserves the requested total whenever the two cargo
stations have enough combined capacity. A service-station excess invalidates
the complete target instead of silently dropping cabin crew or catering mass.

## Remove

Close X-Plane and run from the extracted package:

```text
python3 z_Install_LevelUp_NG_WB.py --aircraft-root "/path/to/LevelUp aircraft" --uninstall
```

This removes the recorded Tablet/FMS W&B hooks, restores the payload gates and
ZFW formula, and restores or removes companion files according to their original
state. Other patches are preserved. Keep the receipt and backups if removal is
blocked; do not delete them by hand.

## First simulator evidence

Follow `RUNTIME_TEST_PLAN.md`. At minimum record all nine `m_stations`,
`m_fixed`, three fuel tanks, X-Plane current/ZFW offsets and `%MAC`, EFB
current/ZFW/TOW/LW CG, `calc_to_cg`, FMC CG and takeoff trim. Matching displays
alone are not proof that station and fuel ownership agree.

## Installation ownership

MTK and the standalone installer remain separate supported installation methods.
Use the same owner for updates and removal. To switch, uninstall through the
current owner first, then install through the other. Neither installer adopts
already patched files on the strength of matching hashes alone.

Keep the complete extracted package, including `standalone_guard.py` and
`standalone-ownership.json`. The standalone installer checks its recorded
original backups and stops if MTK owns this patch or a shared target file.
Unknown, duplicate or incomplete patch blocks and unowned companion files also
block the operation. Other correctly installed patches are preserved.

A failed operation restores the bytes it changed. If the process is interrupted,
keep the `.patch-ownership` receipt, transaction journal and lock, together with
any older patch backup/state directory. Do not delete them to retry. Ask for
support before changing those files.

Older standalone installs without a complete receipt are not automatically
migrated. Remove them using the installer and original backups that created
them. This source change affects installation checks only; runtime payloads and
patch versions are unchanged. Installer and recovery tests cover these checks.
