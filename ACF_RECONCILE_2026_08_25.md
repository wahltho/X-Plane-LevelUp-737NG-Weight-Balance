# LevelUp 737-600 ACF reconcile — 2026-08-25

Status: source reconcile and automatic dry verification only. No simulator
runtime acceptance is claimed.

## Provenance

| Role | Value |
|---|---|
| Aircraft-author input | `/Users/wahltho/Downloads/Level Up/737_60NG.acf` |
| Input SHA-256 | `362f1e5ca26186f527e4924f4e43328dcb3b2e87945b462b8125f237b73da123` |
| Version | `XP12 V2.S1.51 (20260824 200 SAO)` |
| Reconciled private overlay SHA-256 | `b06555077f214263cc146c6c8519b7469937cf19889458e979eacf2d96549dce` |
| Public semantic contract | `levelup600-wb-v1`, Variant ID `3` |

The aircraft author described the -600 load-station geometry as an initial
test-balloon/WAG. It is authoritative for compatibility with this ACF, but is
not presented as independently validated real-aircraft geometry.

## Aircraft-author state accepted

- Empty mass `80199.78 lb`, maximum mass `124499.8 lb` and fuel capacity
  `46062.01 lb`.
- Reference CG `45.979999542 ft`, fixed forward/aft positions
  `44.229999542 / 47.700000763 ft` and MAC `14.878139496 ft`.
- Cargo 1/2 at `25/63 ft`, five zones at `20/33/46/59/72 ft`, and Galley F/A
  at `15/76.199996948 ft`, with the supplied station maxima.
- Constant empty/full tank positions `49/43/49 ft` and ACF tank ratios.
- The complete incoming V2.S1.51 flightmodel, including wing, flap and control
  changes, remains aircraft-author owned.

## Private deltas retained

The reconcile preserves the complete private 42-object domain, removal of
`jdcopilot.obj`, particle object, Collins WXR objects and the transformed
cockpit/default view. Galley F/A roles are normalized to service/cargo role
`1` under the already confirmed common LevelUp service-load contract. The
public Lua installer does not gate on the X-Plane UI role category.

## Owner consequence

The public package and private C++ port both add Variant ID `3` to the existing
nine-station owner. Internal mode writes only `m_stations`; external mode is
read-only. Current CG stays X-Plane-owned, while ZFW/TOW/LW predictions and
FMC ZFW/GW consume the same station snapshot. Existing FMC trim tables remain
the consumer baseline and VREF logic is outside this change.

No plugin build, deploy, commit, tag, push, release or simulator runtime test
was performed by this reconcile.
