# LevelUp 737-900/-900ER ACF reconcile — 2026-08-23

Status: source reconcile and automatic dry verification only. No simulator
runtime acceptance is claimed.

| Variant | Aircraft-author input SHA-256 | Reconciled private overlay SHA-256 |
|---|---|---|
| 737-900 / ID 1 | `4b4ec0617e7aa1786be362e9cfe1ab60d92ba1b097e8145e896d31f835f842e9` | `0134a4d8537ab3f65a79e2eea7f8a0335a0622350bc217ad03a308b025ee8faa` |
| 737-900ER / ID 4 | `c2c0db2907904fb50fbd281f96d46c90e1191f002ed360bcaed778ba106cfed2` | `db05c59bf4892be62240b9fcb5ae5a338870d255ae72606c8f2088b4827fe9fb` |

## Aircraft-author changes accepted

- Both variants move Cargo 1/2 from `43/97` to `45/89 ft`.
- Both variants move Zones 1-5 from `35/48.5/66/79/92` to
  `34/47.5/65/77/91 ft`.
- Both variants use `69/62/69 ft` for empty and full tank positions. The prior
  900ER `70 -> 69 ft` main-tank interpolation is no longer part of the ACF
  contract.
- The new wing geometry, incidence values, elevator control rates and version
  metadata are accepted as aircraft-author flightmodel ownership.
- Empty mass, reference CG, fixed limits, MAC, maximum mass, fuel capacity,
  tank ratios, station names and maxima remain unchanged.

## Private deltas retained

The reconcile preserves the complete private 42-object table, removal of
`jdcopilot.obj`, particle object, Collins WXR objects, Shadow NAV and EFB/SYS
wiring, and transformed cockpit/default view. The incoming 900ER still marks
Galley A as passenger role `0`; the overlay retains cargo role `1` as the
previously confirmed aircraft-author correction. The public Lua contract does
not consume or gate X-Plane's UI role category.

## Contract consequence

The public compatibility module advances only the 900 and 900ER semantic
contracts to `levelup900-wb-v2` and `levelup900er-wb-v2`. The private C++ port
uses the same refined station/tank geometry. Independent control cases use
literal mass-and-moment sums rather than either production implementation.

No plugin build, deploy, commit, tag, push, release or simulator runtime test
was performed by this reconcile.
