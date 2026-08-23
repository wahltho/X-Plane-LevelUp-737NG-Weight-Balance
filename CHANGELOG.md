# Changelog

## 0.3.1 - 2026-08-23

- Updates the 737-900 and 737-900ER semantic contracts to Jochen Heiden's
  refined 2026-08-22 station geometry.
- Moves the shared Cargo 1/2 and five passenger-zone arms to
  `45/89/34/47.5/65/77/91 ft` while retaining the two `15/108 ft` galley
  stations and existing station maxima.
- Uses the new constant `69/62/69 ft` tank geometry for both variants and
  removes the previous -900ER empty/full main-tank interpolation.
- Updates independent mass-and-moment oracles, overlay provenance, installer
  gates and the Toolkit semantic contract.

## 0.3.0 - 2026-08-22

- Established the standalone canonical repository for the public LevelUp W&B
  compatibility patch.
- Supports the 737-700, 737-800, 737-900 and 737-900ER variants.
- Uses X-Plane payload stations as the physical payload owner in internal mode
  and remains read-only toward stations in external-payload mode.
- Publishes current and predicted CG through the existing EFB/FMC handoff while
  retaining the existing FMC takeoff-trim tables.
- Includes semantic ACF contracts that allow unrelated flight-model tuning.
- Adds a machine-readable Toolkit module handoff without creating a separate
  end-user Toolkit action.
- Retains the Windows `luac.exe` temporary-file lifecycle fix from 0.2.3.
