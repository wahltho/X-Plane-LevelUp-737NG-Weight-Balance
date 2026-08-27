# 737-600 ACF reconcile - 2026-08-27

## Inputs

| Item | Value |
|---|---|
| New aircraft-author input | `/Users/wahltho/Downloads/737_60NG.acf` |
| Input SHA-256 | `c808d3536fd938bb76c51e0acf7256bd65bed2a7380eabbec496ccde90a518d4` |
| Previous author input | `/Users/wahltho/Downloads/Level Up/737_60NG.acf` |
| Previous SHA-256 | `362f1e5ca26186f527e4924f4e43328dcb3b2e87945b462b8125f237b73da123` |
| Reconciled private overlay SHA-256 | `02e39a193298f86828d74c9752ae3cf768ebb940c36d462540dff71b05ccf861` |
| Public semantic contract | `levelup600-wb-v2`, Variant ID `3` |

## Accepted W&B revision

The new input changes five longitudinal station arms. These values are accepted
as one indivisible 737-600 W&B contract revision:

| Station | Previous | Refined |
|---|---:|---:|
| Cargo1 | 25 ft | 24 ft |
| Cargo2 | 63 ft | 62 ft |
| Zone 2 | 33 ft | 32 ft |
| Zone 4 | 59 ft | 58 ft |
| Zone 5 | 72 ft | 70 ft |

Zone 1, Zone 3, Galley F and Galley A remain unchanged. Empty mass, reference
CG, forward/aft limits, MAC, maximum mass, station names, station maxima and
fuel-tank geometry also remain unchanged.

For an independent control load of 1,000 lb at every station, the revised arms
reduce ZFW moment by 6,000 lb-ft. With the contracted empty mass and MAC this is
approximately -0.4521 %MAC relative to the previous station geometry.

## Intentional private-overlay boundary

The author input also changes elevator control ratios, flap coefficients and
their generated Plane Maker geometry. Those changes are not part of the public
semantic W&B contract and are not imported into the private overlay. The
overlay continues to use its documented v2.S1.50C aerodynamic baseline while
retaining private object slots, Collins WXR integration, transformed cockpit
view and normalized Galley F/A cargo/service roles.

The public installer intentionally accepts unrelated ACF changes. It verifies
only the fields consumed by the W&B owner chain.
