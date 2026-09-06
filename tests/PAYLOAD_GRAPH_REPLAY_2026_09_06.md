# -600 payload/graph partial replay — 2026-09-06

Public v0.5.1 source baseline: b1c6e1f7c59773f7a3de3c9eb8240d53d2d429a9.
Initial analysis made no Production, ACF, overlay, installer or release changes.
The original experiment below is preserved as historical evidence; see the
confirmed datum and 0.5.2 follow-up at the end.

## Fidelity and boundaries

`test_upstream_payload_graph.py` extracts original upstream 4.05.35 functions
verbatim: the complete Enter handler, total_payload_entry, fill_zone_weight_req,
update_payload, cmd_fuel_cg, activate_numpad, num_pages, page_fuel_cg, calc_mac_DR
and CG/check functions captured/replaced by the production adapter. It executes
the unmodified upstream periodic CG publication block inside an explicitly
restricted after_physics wrapper. The production adapter then wraps that loop.

The Pax-button result `P100` is supplied to the real Enter handler. The five
zone counts are independently asserted as 18/22/18/22/20 for the explicitly
selected 24/30/24/30/30 seat layout. The test advances 360 continuous 0.1-second
ticks, enters P100 at tick 30, returns to page 1, and selects the actual graph
command at tick 270. Production slow-loading writes every station; the last
90 ticks verify the settled graph state. No station completion is injected.

This is NOT the complete original after_physics, initial engines-running
startup, numpad key-click/navigation dispatcher, FMC consumer/trim computation,
or an actual XLua/X-Plane runtime. No other compatibility modules execute here.
Simulator mass and CG feedback is independently modeled in Python from the
actual ACF. The reference datum gives the empty aircraft a **synthetic 22%MAC**;
it is not a real-aircraft LEMAC claim. Pax weights and service selections are
explicit synthetic inputs, not a claim about the reporter's saved settings.

The Lua environment models module-global DataRef property resolution and the
discarded dofile return. It does not silently default unknown globals to zero.
One initial run exposed a missing modeled OEW initialization; the test now
initializes OEW to ACF empty mass. No Production behavior was changed for that.

## Inputs

- `/Users/wahltho/Downloads/737_60NG.acf`
  SHA256 `aede06487ef0080af2769bdbc69f01015e107d26c1fb8a44eea5a5932624a915`
- Original 4.05.35 `B738.tablet.lua`
  SHA256 `7c9e445a2a002f1ef81a0b738ad3c3b791a63c2c313d44d993517e260cd32141`
- 84 kg male passengers; 100 PAX; zero cargo; service 0 or 675 kg.
- 3000 kg in each main; center fuel 0/100/500 kg; requested fuel zero.
- No fuel burn during the loading replay. Forecast taxi burn is 226.8 kg.

## Results (%MAC)

| Feedback / geometry model | Current GW | TO | OEW | Expected TO | Expected OEW |
|---|---:|---:|---:|---:|---:|
| Consistent, 0 center, 0 service | 24.064907 | 23.983102 | 22.000000 | 23.983102 | 22.000000 |
| Consistent, 0 center, 675 service | 24.004311 | 23.923317 | 21.953472 | 23.923317 | 21.953472 |
| Consistent, 100 center, 0 service | 24.021481 | 24.019262 | 22.000000 | 24.019262 | 22.000000 |
| Consistent, 100 center, 675 service | 23.961572 | 23.959117 | 21.953472 | 23.959117 | 21.953472 |
| Consistent, 500 center, 0 service | 23.849471 | 23.946670 | 22.000000 | 23.946670 | 22.000000 |
| Consistent, 500 center, 675 service | 23.792257 | 23.887937 | 21.953472 | 23.887937 | 21.953472 |
| One-frame-delayed feedback, settled | 24.064907 | 23.983102 | 22.000000 | 23.983102 | 22.000000 |
| CG-relative station arms treated as absolute | 24.064907 | 30.604046 | 79.974211 | 23.983102 | 22.000000 |
| Feet station arms treated as metres | 24.064907 | 8.980319 | 0 (guard) | 23.983102 | 22.000000 |
| ZFW offset stuck at zero | 24.064907 | 24.361359 | 22.378257 | 23.983102 | 22.000000 |

Six baseline cases and settled one-frame lag agree with independent mass/moment
oracles within 1e-9 %MAC. The three mutations are **sensitivity experiments**,
not assertions about actual X-Plane behavior or exact reproduction of the
reporter's values. The relative-arm experiment reproduces the distinctive
direction and scale of the two reported anomalies simultaneously.

## Interpretation and falsification

The local DataRefs.txt documents `acf_stations_ref_z` as metres to the aircraft
origin. The current production snapshot therefore uses it as an absolute arm.
If the actual runtime instead returns an arm relative to reference CG, the
modeled loaded ZFW position becomes wrong. Dynamic LEMAC calibration can hide
that error for the current ZFW (21.621743% remains matched in this experiment),
but it transfers a false reference into the differently loaded OEW and TOW.
Thus matching current/ZFW alone does not validate the geometry interpretation.

No existing native station-reference capture was found in the focused local
evidence search. The official X-Plane load-station article confirms station
mass -> resulting CG ownership, but does not settle this getter's coordinate
origin: https://developer.x-plane.com/article/weightbalance-and-load-stations/

Decisive runtime evidence, read-only in DRT:

- `sim/aircraft/weight/acf_stations_ref_z` (all nine entries)
- `sim/aircraft/weight/acf_cgZ_original`

For this exact ACF, Cargo1 is at 24 ft and reference CG at 45.979999542 ft.
The competing predictions for array index 0 are:

- Absolute metres: 24 * 0.3048 = **7.3152 m**.
- CG-relative metres: (24 - 45.979999542) * 0.3048 = **-6.6995038604 m**.

A runtime value near the former rejects the relative-arm hypothesis; do not
add the reference CG blindly. A value near the latter supports it, but all
nine entries and reload/reference behavior still need checking before a fix.
Then inspect current/ZFW offsets, station masses and actual/requested fuel if
the station-coordinate hypothesis fails. No physical constants or CG offsets
should be tuned to fit this report.

## Reproduce

```text
/tmp/lu-wb-051-tests/bin/python tests/test_upstream_payload_graph.py
```

Requires Lupa 2.8 / Lua 5.1 and the named read-only original Lua and ACF inputs.
The initial result was a test-source handoff, not runtime closure.

## Native capture and 0.5.2 follow-up

The supplied `Screenshot 2026-09-06 081529.png` shows original CG 60.34 ft
and all nine native station offsets:

```text
[-7.412736, 6.1996326, -10.823448, -6.5044317, -0.91744804,
 4.1635685, 9.369553, -14.633448, 14.322552]
```

Adding 60.34 * 0.3048 metres reconstructs the Zibo ACF positions
36.02/80.68/24.83/39/57.33/74/91.08/12.33/107.33 ft to within 2 micrometres
of their rounded values. This resolves the station getter's datum in the
observed native runtime; it is not a new capture from the reporter's -600.

0.5.2 normalizes that datum at the snapshot boundary. The normal replay now
feeds actual CG-relative offsets, not absolute arms. The six settled cases
and one-frame-lag case reproduce the original independent expected TO/OEW/ZFW
values above within 1e-9 %MAC. The new absolute-arm and feet mutations are
deliberately invalid inputs; their results are not runtime claims.
The original negative result explains why matching current/ZFW CG alone
was insufficient. The remaining partial-replay boundaries still apply.
