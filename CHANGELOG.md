# Changelog

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
