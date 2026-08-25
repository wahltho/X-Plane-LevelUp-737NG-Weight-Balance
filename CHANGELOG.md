# Changelog

## 0.4.0 - 2026-08-25

- Adds Jochen Heiden's V2.S1.51 737-600 ACF as `levelup600-wb-v1`
  (Variant ID `3`) to the common station, CG, FMC-ZFW and trim-handoff owner.
- Uses the supplied two cargo, five passenger-zone and two service stations,
  fixed ACF CG limits and constant `49 / 43 / 49 ft` tank arms.
- Reconciles the private -600 overlay while preserving its object table,
  Collins WXR integration and transformed cockpit/default view.
- Extends semantic ACF gates, independent mass-and-moment oracles, lifecycle,
  external-payload and Toolkit-source tests to all five NG variants.
- Leaves FMC trim tables and VREF performance logic unchanged.

## 0.3.3 - 2026-08-24

- Split the shared Tablet loader into an independent
  `insert-marked-block-v1` operation.
- Keep W&B hook replacements separate so other marked Tablet loaders can be
  installed and removed independently.
- Add standalone package-coexistence coverage for the performance-calculator
  loader.

## 0.3.2 - 2026-08-24

- Fixes the approximately `1.155 klb` LevelUp FMC ZFW/GW deficit caused by
  subtracting Zibo's inherited `524 kg` pilots although LevelUp ACF empty mass
  already includes them.
- Uses ACF empty mass plus `m_stations[0..8]` as the FMC ZFW owner for Variant
  IDs `2/0/1/4`; stock Zibo and unsupported variants keep the upstream formula.
- Adds structural, marked FMS changes without another FMS `dofile()`, preserving
  existing VNAV descent-table patches in either installation order.
- Extends installer rollback, backup, uninstall, LF/CRLF, migration, archive and
  Toolkit tests across both Tablet and FMS targets.
- Leaves takeoff trim tables unchanged pending new RealBench evidence.

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
