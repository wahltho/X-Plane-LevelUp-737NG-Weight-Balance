# v0.5.3 validation — 2026-09-07

Scope: public Lua activation hardening and matching installer/package metadata.
No aircraft, private overlay, Toolkit application or simulator install changed.
Runtime numerical calculations and independent moment oracles are preserved.

## Automated evidence

Validation uses Python 3.14 with Lupa 2.8 / actual Lua 5.1.

| Check | Result / coverage |
|---|---|
| Lua core/data/adapter and payload syntax | PASS; five variants, independent moments, external owner and reload |
| Silent Tablet fallback | PASS; each variant with wrong station name, zero capacity or missing numeric value; upstream callbacks preserved, no W&B CG/OEW/station writes or warnings |
| FMS real patch fragments | PASS; five valid fixtures, malformed/missing ACFs, same-ID reload recovery, path mismatch and stock delegation; independent physical/scalar weight oracles |
| Archived old ACFs | PASS; all five V2.S1 and all five V2.S1.50A files leave FMS on the upstream formula without warnings |
| Full current author ACF inputs | PASS; five inputs plus revised -600/-700, actual Lua metadata reader and independent lb-ft/kg-m moments |
| ACF/layout/numeric guards | PASS; unsupported structure rejected, valid dynamic numeric changes accepted |
| Name aliases | PASS; 65 independent installer/Lua cases |
| Datum mutations | PASS; unchanged 634340 kg-m oracle rejects missing, reversed and doubled reference addition |
| Partial upstream payload/graph replay | PASS; six settled fuel/service cases and one-frame lag; simulated XP boundary, not full runtime |
| Installer | PASS; LF/CRLF, historical upgrades through 0.5.2, idempotence/uninstall, backups, unchanged ACFs, performance/VNAV coexistence, Windows temporary-file handling and Lua 5.4 compiler rejection |
| Toolkit definitions | PASS; actual handler ambiguity rule, fresh application and idempotence, complete patched upstream Tablet/FMS Lua 5.1 syntax |
| Release archive | PASS; exact entries, SHA-256/source parity, fresh installs with synthetic/previous/revised ACF inputs, complete patched Tablet/FMS and payload Lua 5.1 syntax |
| Simulator acceptance / consolidated Toolkit rollout | NOT RUN; separate proof layers |

Two pre-existing Toolkit exact-text payloads retained their entire old sequence
inside the replacement. Applying the actual handler ambiguity rule exposed this
rejection. Scoped comments now distinguish the installed anchors; both install
paths preserve the upstream statements and removal restores the originals.
An installer assertion was updated only for that comment; its payload-owner
condition and expected upstream statement remain unchanged.

The first replay attempt used a removed historical default ACF path. The passing
run explicitly uses `Downloads/Randomuser/737_60NG.acf`. No aircraft data was
changed to pass a check.

## Input provenance

The five `Downloads/Level Up` ACFs match the hashes in `VALIDATION_0.5.0.md`.
The revised -600/-700 in `Downloads/Randomuser` match `VALIDATION_0.5.1.md`:
`aede06487ef0080af2769bdbc69f01015e107d26c1fb8a44eea5a5932624a915` and
`74d5ccb24cfff5444993d67a148cf6fa923c7d39e299219c58186f90d8b44750`.
Old inputs are the read-only archived `737NG Series_V2.S1` and
`737NG Series_V2.S1.50A` aircraft directories. No ACF is included in the ZIP.

## Reproduce

```text
python tools/test_lua51.py --aircraft-root "/path/to/five-ACFs" --updated-aircraft-root "/path/to/revised-600-and-700"
python tests/test_fms_acf_guard.py --legacy-aircraft-root "/path/to/737NG Series_V2.S1" --legacy-aircraft-root "/path/to/737NG Series_V2.S1.50A"
python tests/test_acf_contract.py
python tests/test_name_aliases.py
python tests/test_station_datum_mutations.py
python tests/test_upstream_payload_graph.py --acf "/path/to/revised-600/737_60NG.acf"
python tests/test_installer.py
python tests/test_toolkit_contract.py
python tools/build_release.py
python tests/test_release.py --lua51-syntax
python tests/test_release.py --lua51-syntax --aircraft-root "/path/to/five-ACFs" --updated-aircraft-root "/path/to/revised-600-and-700"
git diff --check
```

Installer migration checks require the archived release ZIPs through 0.5.2 and
original upstream 4.05.35 Lua. The old private-overlay snapshot test remains
outside this public dynamic-geometry release and is not counted as green.

## Runtime acceptance remains open

Follow `RUNTIME_TEST_PLAN.md` for five-variant physical stations/current and
planned CG, old/new ACF transitions, save/load, external payload, loading,
FMC handoff and unchanged trim consumers. Full X-Plane/XLua callback timing,
Windows/macOS sibling dofile loading and aircraft behavior are not established
by the automated harness or full-file syntax checks.
