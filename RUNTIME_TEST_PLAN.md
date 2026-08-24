# Later simulator test matrix

Run only after explicit deploy/runtime approval and after preserving the exact
baseline aircraft and Lua files.

## Instrumentation

Capture for every case:

- Variant-ID and aircraft filename;
- `m_stations[0..8]`, `m_fixed`, `m_fuel[0..2]`;
- `cg_offset_z`, `zfw_cg_offset_z`, `cg_offset_z_mac`;
- EFB current/ZFW/TOW/LW CG and graph status;
- requested ramp/destination fuel and taxi allowance;
- `calc_to_cg`, FMC CG and takeoff trim.

## Per-variant matrix

Run the following with `737_70NG.acf`/ID 2, `737_80NG.acf`/ID 0,
`737_90NG.acf`/ID 1 and `737_9ENG.acf`/ID 4:

1. Confirm all four ACF contracts pass the v0.3.3 installer. A whole-file hash may
   differ after unrelated flight-model tuning.
2. Empty/internal: verify no unexplained 524-kg addition. EFB current CG must
   equal X-Plane `cg_offset_z_mac` within 0.5 percentage points; populated CG
   rows must not show `CHECK`.
3. Internal asymmetric load: all nine stations must ramp independently at the
   expected rate, `m_fixed` must equal X-Plane's aggregate, and CG must move in
   the direction independently predicted from the ACF arms.
4. Save/load, SimBrief import, slow loading and aircraft reload: selected zones
   must reconstruct the same targets without a scalar payload owner taking
   over.
5. Requested ramp/TOW fuel: compare captured tank allocation after 226.8-kg
   taxi fuel, independent mass/moment, EFB TOW CG and `calc_to_cg`.
6. FMC transfer: accept the produced CG on TAKEOFF REF and record the existing
   trim-table result for the same flaps and CG. Confirm PERF INIT ZFW equals
   ACF empty mass plus all nine stations within display rounding, and that FMC
   GW equals that ZFW plus actual fuel.
7. Destination fuel/LW: compare the three modeled tank values, independent
   landing moment and EFB LW CG.
8. External payload: change every station with an external tool. Tablet and
   patch must write neither station nor `m_fixed`; EFB current CG must follow
   X-Plane and predictions must use the external snapshot.
9. External-to-internal transition: ownership must change once and stations
   must converge from the external state to current Tablet targets.
10. Exact capacity: verify cargo normalization preserves total cargo without
    exceeding either ACF maximum. A service-station value above its maximum
    must inhibit all station writes and set no FMC takeoff-CG handoff.
11. Forward/aft and maximum-mass limits: EFB checks must change consistently at
    the contract boundary without stale state from the other variant.

## Variant/lifecycle regressions

1. Exercise direct transitions `2 -> 0 -> 1 -> 4 -> 2`. Before publication,
   the prior calibrated LEMAC must be invalidated and predictions must converge
   to the newly selected contract.
2. On the -900 and -900ER, compare empty, half-full and full main tanks. Verify
   the captured moment follows the ACF's constant `69 ft` main-tank arms and
   that TOW/LW predictions use the same arm rule.
3. Load a LevelUp ID 3 aircraft. The patch must relinquish all payload, CG and
   envelope ownership and preserve stock behavior.
4. Load stock Zibo 737-800. Confirm no LevelUp station writer, current-CG
   override or FMC handoff is active.
5. Repeat representative cases with the performance patch installed before
   and after this W&B package.
6. Upgrade an aircraft with -700 v0.1.4 installed. Verify the original backup
   remains unchanged, only five common Tablet v0.3.3 blocks plus two FMS blocks
   remain, and all four
   supported variants load.
7. Upgrade an aircraft with v0.2.0 installed and Jochen's revised 800 ACF.
   Verify the common hooks remain singletons, the 800 v2 contract is active,
   and no old arm values survive in the installed runtime data.
8. Repeat one representative case with the VNAV descent-table patch installed
   before W&B and once with it installed after W&B. Verify both FMS marked
   blocks remain singletons and uninstalling W&B preserves the VNAV block.

## Known regression reproducer

For the -700 reproduce approximately `34309 lb` payload, `119682 lb` ZFW,
`13717 lb` ramp fuel and `132900 lb` TOW. Current CG should remain near the
previously observed `22.63 %MAC`; ZFW/TOW CG and `calc_to_cg` must be nonzero,
inside the fixed envelope and not show `CHECK`.

For each of the -800/-900/-900ER record at least empty, balanced
full-passenger, forward-cargo, aft-cargo and Airside-service loads. Compare all
outcomes against independent mass/moment calculations using that variant's
station and tank arms in `SOURCE.md`.

A passing display alone is not closure. The producer state, X-Plane physical
state, EFB prediction, FMC CG and trim consumer must agree for one captured
state before that variant is accepted.
