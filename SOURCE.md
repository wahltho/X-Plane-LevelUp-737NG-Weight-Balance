# Evidence and derivation

This test balloon covers `737_70NG.acf`/ID `2`, `737_80NG.acf`/ID `0`,
`737_90NG.acf`/ID `1` and `737_9ENG.acf`/ID `4`. No values are inferred for
the -600 or any MAX variant.

## Reference aircraft

| Field | 737-700 | 737-800 |
|---|---:|---:|
| Contract | `levelup700-wb-v1` | `levelup800-wb-v2` |
| Reference SHA-256 | `8cb0d7254e63cd1a2b4fe88071e706393504e6bfce7ab6af3cca417d22ea3c31` | `9315f4110ae8c2b5feb53872ae3d7a6bcc2ff380099b6c925c9734d2d65fbe16` |
| Empty mass | `82999.61 lb` | `91514.04 lb` |
| Reference CG | `49.029998779 ft` | `59.889999390 ft` |
| Fixed forward/aft | `47.189998627 / 50.939998627 ft` | `57.869998932 / 61.840000153 ft` |
| MAC | `14.992128372 ft` | `14.992127419 ft` |
| Maximum gross mass | `154499.9 lb` | `174700 lb` |
| Fuel capacity | `46062.008 lb` | `46062.01 lb` |
| Tank ratios | `0.187000006 / 0.625999987 / 0.187000006` | same |
| Tank arms | `52.650001526 / 46 / 52.650001526 ft` | `64 / 56.5 / 64 ft` |

| Field | 737-900 | 737-900ER |
|---|---:|---:|
| Contract | `levelup900-wb-v1` | `levelup900er-wb-v1` |
| Reference SHA-256 | `b736f745bf0f170e598ad896a8e055533107742478624e32239975194895d071` | `67256a2181435da50b0f31f2c0ebbf81732e530c7b3809de05967abf0930eec6` |
| Empty mass | `94580 lb` | `98495 lb` |
| Reference CG | `64.650001526 ft` | `65.389999390 ft` |
| Fixed forward/aft | `63.380001068 / 67.129997253 ft` | `64.879997253 / 67.879997253 ft` |
| MAC | `14.993530273 ft` | `14.993530273 ft` |
| Maximum gross mass | `174700 lb` | `187699.31 lb` |
| Fuel capacity | `46062.008 lb` | `52512.31 lb` |
| Tank ratios | `0.187000006 / 0.625999987 / 0.187000006` | same |
| Empty tank arms | `70 / 62 / 70 ft` | `70 / 62 / 70 ft` |
| Full tank arms | `70 / 62 / 70 ft` | `69 / 62 / 69 ft` |

The current references are
`/Users/wahltho/Downloads/Level Up/737_70NG.acf`, the retained -800 provenance,
and `/Users/wahltho/Downloads/Level Up/737_90NG.acf` plus `737_9ENG.acf`.
The SHA-256 values record evidence
provenance but are not installation requirements. The installer checks every
consumed mass, CG/MAC, station and tank field semantically and allows all
unrelated ACF changes.

## Payload stations

| Index | 737-700 name / arm / max | 737-800 name / arm / max | Role |
|---:|---|---|---|
| 0 | Cargo1 / `29 ft` / `4200 lb` | Cargo1 / `37 ft` / `7848 lb` | cargo |
| 1 | Cargo2 / `69 ft` / `6900 lb` | Cargo2 / `85 ft` / `10690 lb` | cargo |
| 2 | Zone 1 / `22 ft` / `8000 lb` | Zone 1 / `33.5 ft` / `10000 lb` | passenger |
| 3 | Zone 2 / `34 ft` / `8000 lb` | Zone 2 / `46.5 ft` / `10000 lb` | passenger |
| 4 | Zone 3 / `46 ft` / `8000 lb` | Zone 3 / `58.5 ft` / `10000 lb` | passenger |
| 5 | Zone 4 / `58 ft` / `8000 lb` | Zone 4 / `70.5 ft` / `10000 lb` | passenger |
| 6 | Zone 5 / `70 ft` / `8000 lb` | Zone 5 / `82.5 ft` / `10000 lb` | passenger |
| 7 | Galley F / `15 ft` / `3000 lb` | Galley F / `15 ft` / `3000 lb` | service/cabin crew |
| 8 | Galley R / `80 ft` / `3000 lb` | Galley A / `99 ft` / `3000 lb` | service/cabin crew |

The -900 and -900ER share these station arms: Cargo 1/2 `43/97 ft`, Zones
1-5 `35/48.5/66/79/92 ft`, and Galley F/A `15/108 ft`. Their maxima are
`7848/10690 lb` (-900) or `7848/10500 lb` (-900ER) for cargo, `10000 lb` for
each passenger zone and `3000 lb` for each service station. The -900 uses ACF
role `1` for cargo and service stations. Jochen confirmed that the current
-900ER service-station role `0` is an ACF oversight and that both Galley F/A
stations are cargo-role stations. The private overlay applies that intentional
fix immediately. The public installer deliberately does not gate on the role
category because the integration consumes station order, name, arm and
maximum—not X-Plane's UI category—so it accepts both the current input and the
announced corrected revision without weakening the physical W&B contract.

ACF masses are pounds and longitudinal coordinates are feet. X-Plane
`m_stations` and the Tablet payload state are kilograms; offset DataRefs are
metres. Conversion uses exact `0.45359237 kg/lb` and `0.3048 m/ft`.

The -700/-800/-900 empty/full longitudinal tank positions are identical. The
-900ER mains move from `70 ft` empty to `69 ft` full. Planned and actual fuel
moments therefore interpolate the -900ER main arm by `tank_mass/tank_capacity`.
This is an ACF physics contract, not an independently validated real-aircraft
fuel-moment curve.

## Aircraft-author owner contract

Jochen confirmed for the supported aircraft that pilot weights are already in
ACF empty mass. Cabin crew and catering are split 50/50 between the forward
and aft service stations. Consequently the stock Tablet's fixed `524 kg` crew
addition is removed only while a supported contract owns payload. The ACF CG
limits and existing FMC trim tables remain the agreed feasibility baseline.

## Formula and coordinate closure

Every modeled CG is calculated in ACF coordinates:

`z = sum(mass_kg * arm_m) / sum(mass_kg)`

X-Plane's current ZFW %MAC is derived only from values sharing X-Plane's
offset datum:

`xplane_zfw_mac = current_mac + (zfw_offset - current_offset) / MAC * 100`

The current ACF-space ZFW moment is independently calculated from empty mass
and the actual station snapshot. That common state calibrates ACF-space LEMAC:

`lemac_acf = current_model_zfw - xplane_zfw_mac / 100 * MAC`

All predicted states and fixed limits then use:

`predicted_mac = (predicted_z - lemac_acf) / MAC * 100`

Calibration runs before slow-loading writes so X-Plane's ZFW offset and the
station snapshot describe the same completed physics frame. Current/in-flight
CG is never reconstructed: it remains X-Plane's `cg_offset_z_mac`.

Numeric XLua DataRefs must be assigned to a module-global property. The
v0.1.3 local binding failure is covered by a harness that discards `dofile()`
returns and resolves only global properties.

## Independent control examples

The dry test uses a literal ACF model independent of the production core. One
control case has station masses
`1000/500/2000/1800/1600/300/1200/200/250 kg` and tank masses
`3000/5000/3000 kg`. Direct summation gives:

- gross mass: `61360.0702918748 kg`;
- gross moment: `1104667.7681431761 kg m`;
- longitudinal CG: `18.003039482982054 m`.

Using the same explicit `8850 kg` station snapshot with `12000 kg` requested
ramp fuel and the fixed `226.8 kg` taxi allowance, the takeoff state is
`3907.061490 / 3959.077019 / 3907.061490 kg` and shifts CG by
`+3.470750 percentage points MAC` relative to ZFW. A `3000 kg` destination
state split between the mains shifts it by `+1.975618 points`. Absolute %MAC
still requires the runtime-derived LEMAC.

For the -900ER, the same explicit station snapshot and `3000/5000/3000 kg`
tank state gives `64526.58048315 kg`, `1269754.25887529 kg m` and
`19.678003225459374 m`. The expected value independently interpolates each
main-tank arm from the ACF empty/full pair; it is not generated by the Lua or
C++ production function.

## Fuel convention

Requested/destination total fuel fills both mains first and then the center,
matching the upstream `.35` prediction convention. Taxi fuel is removed
center-first and then symmetrically from the mains. Actual current fuel always
comes from X-Plane's three tank values. A later validated operational model may
replace this convention as an intentional fix.

## Capacity boundaries

The ACF is authoritative. Release v0.3.0 normalizes rounded internal Tablet
cargo selections to the exact station maxima before any station or CG write:

- -700 Cargo 1/2 ACF maxima are `1905.088 / 3129.787 kg`, below the stock
  Tablet's `1927 / 3172 kg` by `21.912 / 42.213 kg`.
- -800 Cargo 1/2 ACF maxima are `3559.793 / 4848.902 kg`, below the Tablet's
  `3560 / 4850 kg` by `0.207 / 1.098 kg`.
- -900 uses the same exact cargo maxima as -800.
- -900ER Cargo 1/2 maxima are `3559.793 / 4762.720 kg`; the stock Cargo 2
  ceiling exceeds the ACF by `87.280 kg`.
- Each -800 service station allows `1360.777 kg`. Maximum Galley F plus half
  cabin crew can reach `1385.6 kg`; Galley A can reach `1433.6 kg`. The
  extreme excesses are `24.823 / 72.823 kg`.
- The -800 passenger-zone maximum of `4535.924 kg` remains above the largest
  stock -800 zone target (`42 * 87 = 3654 kg`).

Service-station excess still invalidates the complete target rather than
silently discarding crew or catering weight. These are documented acceptance
boundaries, not guessed ACF changes.

## Scope of the reconciled ACFs

Compared with the first 800 contract, Jochen's 2026-08-20 file moves Cargo 1
from `36` to `37 ft`, moves all five passenger zones aft by `2.5 ft`, moves
the main tank arms from `63.950000763` to `64 ft`, and the center arm from
`55.5` to `56.5 ft`. Names, order, roles, maxima, empty mass, reference CG,
limits, MAC, maximum mass, fuel capacity and tank ratios remain unchanged.
The complete textual delta also contains extensive wing-geometry, incidence
and flap tuning. This compatibility package consumes only the enforced W&B
fields and does not interpret, reproduce or overwrite that flight-model work.

Jochen's 2026-08-21 -900/-900ER inputs replace the disabled three-passenger/
two-cargo definitions with nine active stations. The -900ER input also changes
fuel capacity, empty/full main-tank geometry and flap coefficients. Overlay
reconcile takes those aircraft-owner fields while retaining the private object
table, Collins WXR objects and transformed cockpit/default view. Whole-file
replacement is deliberately not used.
