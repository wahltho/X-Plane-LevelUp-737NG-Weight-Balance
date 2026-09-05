# Loaded-aircraft W&B contract — 0.5.0 source

Status: 0.5.0 source and automated regression/package checks complete.
No aircraft deploy or simulator-runtime test. See `VALIDATION_0.5.0.md`.

## Scope and invariant

Intentional maintenance improvement: valid aircraft-author W&B geometry is
read from the loaded aircraft instead of copied into a versioned Lua table.
It is not an adoption or validation of alternate ACF/airfoils/aerodynamic
proposals. No ACF or private C++ source is changed.

Every CG forecast and envelope conversion in a Tablet callback uses one
geometry snapshot. LEMAC calibration happens before stock graph consumers
and before station writes. Missing/invalid inputs suppress predicted CG and
FMC takeoff-CG publication, but never restore stock scalar payload writers
for supported LevelUp IDs.

## Inputs, provenance and units

| Input | Source | Conversion/use |
|---|---|---|
| Empty mass, max gross | `sim/aircraft/weight/acf_m_empty`, `acf_m_max` | runtime kg |
| Reference CG | `sim/aircraft/weight/acf_cgZ_original` | ft × 0.3048 = absolute m |
| Station longitudinal arms | `sim/aircraft/weight/acf_stations_ref_z[0..8]` | absolute m |
| Station maxima | `sim/aircraft/weight/acf_m_station_max[0..8]` | kg |
| Total fuel capacity | `sim/aircraft/weight/acf_m_fuel_tot` | runtime kg, NOT lb |
| Tank capacity fractions | `sim/aircraft/overflow/acf_tank_rat[0..8]` | dimensionless |
| Tank endpoints | `sim/aircraft/overflow/acf_tank_Z`, `acf_tank_Z_full` | offset m + reference CG in m |
| MAC length | loaded ACF `acf/_average_mac_acf` | ft × 0.3048 |
| Fixed limits | loaded ACF `acf/_cgZ_fwd`, `acf/_cgZ_aft` | ft × 0.3048 |
| Names/dimensions | loaded ACF fixed/tank arrays | supported semantic order |
| Current CG | `sim/flightmodel2/misc/cg_offset_z_mac` | %MAC; read-only |
| Current/ZFW offsets | `sim/flightmodel2/misc/cg_offset_z`, `zfw_cg_offset_z` | m, positive aft |

Tank units/interpolation are based on the native X-Plane 12.4.3-r2 sweep of
2026-08-20, with aircraft plugins excluded. Runtime total fuel was
20893.378906 kg despite the stale local DataRefs.txt lb label. At half-full,
the left main centroid was 62.730002873 ft versus the independent linear
expectation 62.730002493 ft. Maximum residual across 18 nonzero samples:
7.2726e-7 m. This establishes the simulator primitive, not real-aircraft tank
accuracy or acceptance of this new Lua path.

No globally usable MAC-length or station-name DataRef was identified. Reading
these few fields from the ACF avoids substituting wing-element MAC for aircraft
MAC. Fixed CG limits also come from ACF because overflow-limit DataRef units
are not sufficiently established. The file is read using upstream
`file_path` (`zibomod/Aircraft_Path`) after checking the loaded filename in
`sim/aircraft/view/acf_relative_path` against the variant ID.

## Formula checks

All moments below are kg m in the same absolute, positive-aft datum:

```text
tankCapacity = totalFuelKg × tankRatio
tankArm = referenceM + emptyOffsetM
          + (fullOffsetM − emptyOffsetM) × clamp(fuelKg/tankCapacity, 0, 1)
CG = (emptyKg × referenceM + Σ stationKg × stationArmM + Σ fuelKg × tankArm) / totalKg
ZFW_MAC = currentMAC + (zfwOffsetM − currentOffsetM) / MAC_M × 100
LEMAC_M = modeledCurrentZfwCG_M − ZFW_MAC/100 × MAC_M
predictedMAC = (predictedCG_M − LEMAC_M) / MAC_M × 100
```

Independent existing -600 control: total mass 56228.0082836786 kg,
moment 771543.5328944295 kg m, CG 13.721694159997247 m. These
literal expectations remain unchanged in the core regression.

New analytical station-arm check: moving an occupied station aft by 1 m adds
exactly its mass to the moment. With 920 kg in that station, the expected CG
change is 920/totalMass m. The adapter regression checks ZFW, TOW and LW using
their different independent mass denominators, not production CG functions
as the expected-value generator.

## Owner / closure delta

| Surface | Source contract | Verification still required |
|---|---|---|
| Variant + loaded file | IDs 3/2/0/1/4 and exact corresponding basename | all five; wrong path/variant rejection |
| Metadata lifecycle | read once per flight_start/path/variant; disk edits require reload | same-ID reload, two copies, Windows paths |
| Numeric geometry | refresh before each after_physics callback; shared snapshot | runtime units/float precision on supported XP versions |
| Internal payload | selected zones; cargo capacity normalization; nine slow writes | save/load, SimBrief, loading, transition tests |
| External payload | physical stations; no station/aggregate writes or entry normalization | changes to every station while paused and in flight |
| Actual/current CG | X-Plane only, still available if forecast geometry invalid | continuous in-flight logging |
| OEW | empty plus forward/aft service mass/moments | graph vs crew/galley settings; OEW need not equal empty CG |
| Forecast fuel | existing equal-wing-first allocation, center-first taxi burn, 226.8 kg taxi | planned vs actual ramp fuel and destination fuel |
| Tank moment | live capacity plus empty/full linear centroid | variable endpoint cases, all five |
| EFB forecasts/limits | same geometry + pre-write derived LEMAC | no post-write recalibration or stale CHECK state |
| FMC ZFW/GW | existing marked FMS physical-station formula unchanged | compare physical vs planned mass during loading |
| FMC CG/trim | existing calc_to_cg handoff and upstream acceptance/tables | manual acceptance/cache remains upstream-owned |
| Invalid supported input | no stock fallback; no station writes; predicted CG 0 / CHECK | missing arrays, NaN, zero capacities, recovery |
| Unsupported IDs/Zibo | original handlers | delegation regression |
| Installer + Toolkit | schema-1 names/counts; standalone numeric sanity; runtime guard in both | migration, coexistence, integrity, bundled install |

The Toolkit contract retains its existing schema and operations. Its numeric
list now covers array dimensions and inactive tanks, not exact geometry.
Standalone installation additionally checks finite numeric inputs and symmetry.
Both install paths receive the same runtime semantic/numeric guard. No Toolkit
repository/catalog is modified; the Toolkit owner must import this release.

## Deliberately unchanged constraints

- Nine stations: cargo 0/1, passenger zones 2–6, service 7/8. Existing per-variant
  names (including Galley R/A and Right Main/Wing) are retained. Role categories
  are not a mass/moment input and remain outside the gate.
- Pilots belong to empty mass; cabin crew are split 50/50, with the respective
  forward/aft galley selections added. The aircraft author must preserve that
  meaning; it cannot be inferred from station order.
- Three active tanks, left/center/right; equal wing capacities; ratios sum to
  one. New tank layouts or new fuel-distribution policies require separate work.
- Fixed ACF limits remain a feasibility envelope, not a certified envelope.
- Stock selection ceilings, taxi allowance, loading rate and FMC trim tables
  are unchanged. A larger ACF capacity does not expand the stock EFB input UI.
- Calibrating LEMAC from current X-Plane ZFW cannot diagnose an unrelated
  plugin moving the datum. Controlled native/loaded-aircraft comparison remains
  required; matching displayed values alone is not real-aircraft validation.

## Regression and release gates

Passed: frozen v0.4.1 mass/moment fixtures, dynamic-arm forecasts,
simulated invalid/recovery, same-ID/MAC reload, external entry ownership, layout
and numeric mutation cases, installer coexistence and updated package contracts.
All five current author ACFs also pass the actual Lua metadata reader and
independent lb-ft versus kg-m mass/moment comparison. The historical
`test_overlay_reconcile.py` is a separate private-aircraft snapshot audit,
not a required numeric baseline for this dynamic public implementation.

Lua 5.1 syntax/core/adapter and dynamic-input tests, Python installer/ACF/Toolkit
tests and fresh ZIP installation/syntax checks passed under the user's approval.
Later runtime matrix: all five LevelUp variants plus stock Zibo, current/forecast
CG through loading/flight/reload/external tools, FMC mass/CG acceptance and
unchanged trim consumers. Do not call the feature runtime-complete before that.
