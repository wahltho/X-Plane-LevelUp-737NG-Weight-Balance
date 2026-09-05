# Changelog

## 0.5.0 - 2026-09-05

- Replaces fixed numeric variant tables with loaded-aircraft DataRef snapshots.
  MAC, CG limits and station/tank names are read from the current ACF per load.
- Uses one frame's geometry and pre-write datum for OEW/ZFW/TOW/LW, graph
  checks and the existing FMC CG handoff. Resets on aircraft load/path/variant.
- Inhibits writes/predictions for invalid supported inputs without returning
  payload ownership to stock scalar writers. External stations stay read-only.
- Replaces exact numeric ACF gates with layout and numeric sanity checks.
- Retains the existing dofile/install positions, Tablet/FMS marked hooks,
  payload/fuel policies and trim tables. No aircraft or private-port changes.
- Lua 5.1, math/adapter/dynamic-input regressions, five current author ACFs,
  installer/migration/coexistence, Toolkit and packaged-installation checks pass.
  No new simulator-runtime validation; see `VALIDATION_0.5.0.md`.

## 0.4.2 - 2026-08-30

- Restricts the optional whole-file Lua syntax check to a Lua 5.1-compatible
  `luac`, matching X-Plane XLua/LuaJIT semantics.
- Skips incompatible system compilers such as Lua 5.4, which reject an
  assignment to the upstream Zibo FMS `for ii` control variable even though
  the same Lua is valid under XLua.
- Keeps validation transactional and leaves all W&B contracts, Tablet/FMS
  hooks and runtime behavior unchanged.

## 0.4.1 - 2026-08-27

- Updates the 737-600 semantic contract to `levelup600-wb-v2` for the refined
  `24/62/20/32/46/58/70/15/76.199996948 ft` station arms.
- Retains the existing -600 empty mass, reference CG, CG limits, MAC, station
  names and maxima, service-load ownership and constant fuel-tank geometry.
- Reconciles only those five changed W&B arms into the private overlay and
  intentionally excludes the accompanying elevator, flap and generated
  geometry changes from the private aerodynamic baseline.
- Updates the independent moment oracle, semantic installer gate and Toolkit
  module contract. FMC trim and VREF logic remain unchanged.

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
