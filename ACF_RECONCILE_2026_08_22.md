# LevelUp 737-900/-900ER ACF reconcile — 2026-08-22

## Inputs and provenance

| Variant | Aircraft-author input | Input SHA-256 | Reconciled overlay SHA-256 |
|---|---|---|---|
| 737-900 / ID 1 | `/Users/wahltho/Downloads/Level Up/737_90NG.acf` | `b736f745bf0f170e598ad896a8e055533107742478624e32239975194895d071` | `2ac3fa0c5cc6c5002675712989f3a0ef4c9fdb9cf7c62e54c7819129a295e5cc` |
| 737-900ER / ID 4 | `/Users/wahltho/Downloads/Level Up/737_9ENG.acf` | `67256a2181435da50b0f31f2c0ebbf81732e530c7b3809de05967abf0930eec6` | `06f5357b46ad6fa242464e11c64b988ec4a31cb5da0c7aaaa9d37af2d61c383e` |

The input ACFs supply the flight-model and W&B values. They are evidence
inputs, not deploy targets and not whole-file replacements for the private
overlay.

## Three-way ownership decision

- Incoming aircraft-author values win for flight-model, empty/max mass,
  reference/forward/aft CG, MAC, station names/arms/maxima, fuel capacity,
  tank ratios and empty/full tank geometry.
- The private overlay retains its complete object table, removal of
  `jdcopilot.obj`, particle and Collins WXR object slots, Shadow NAV and
  landing-nav-kind wiring, EFB/SYS wiring, and transformed cockpit/default
  views.
- The 900ER input's Galley F/A role `0` is corrected to cargo role `1` in the
  private overlay. Jochen identified role `0` as an oversight on 2026-08-22 and
  announced the same correction for his next ACF revision. This is an explicit
  `intentional-fix`; it does not change station arms, maxima or moments.
- The public Lua installer does not validate individual station-role fields.
  Its physical contract is station count, order, name, arm and maximum, so it
  works with both the current author input and the announced role-only update.

## Confirmed service and trim baseline

The aircraft author confirmed that pilots are included in empty weight and
that cabin crew plus catering are split evenly between the forward and aft
service stations. The ACF forward/aft CG values are the initial fixed envelope.
The current upstream FMC takeoff-trim calculation remains the baseline; no trim
logic or table is changed by W&B package v0.3.0.

## Evidence boundary

Static reconcile and mass/moment tests cover both variants. No plugin build,
deploy, commit or simulator runtime test was performed in this reconcile.
