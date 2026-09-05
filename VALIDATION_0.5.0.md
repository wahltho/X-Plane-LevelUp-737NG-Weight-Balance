# v0.5.0 validation — 2026-09-05

Scope: public LevelUp W&B patch for upstream Zibo 4.05.35 Lua/plugin.
No author ACFs changed, copied into the overlay, or included in the ZIP.
No private C++ source, Toolkit repository or simulator installation changed.

## Results

| Check | Result |
|---|---|
| Lua 5.1 syntax, three payload modules | PASS |
| Frozen independent mass/moment regressions (five variants) | PASS |
| Dynamic units, capacities, endpoints and invalid inputs | PASS |
| Adapter: internal/external owners, current/forecast CG, reload/MAC change, delegation | PASS |
| Five current author ACFs: actual Lua metadata parser + independent lb-ft/kg-m calculation | PASS |
| Installer ACF layout/numeric mutation cases | PASS |
| Installer LF/CRLF, idempotence, migration and uninstall | PASS |
| Windows luac handoff and rejection of incompatible Lua 5.4 compiler | PASS |
| Tablet performance / FMS VNAV patch coexistence | PASS |
| Toolkit payload hashes, operations and layout contract | PASS |
| ZIP contents/checksum/source identity and fresh installation | PASS |
| Fresh ZIP installation using all five current full author ACFs | PASS |
| Full patched upstream Tablet/FMS syntax under Lua 5.1 | PASS |
| Historical private-overlay hash audit | FAIL — outside this public patch's acceptance scope |
| X-Plane runtime / flight validation | NOT RUN |

The historical `tests/test_overlay_reconcile.py` stops at its old private ACF
hash assertion. Neither its expectations nor the overlay were changed to make
it green. It is not a required geometry baseline for this dynamic public patch.

Lua checks used `lupa.lua51` from Lupa 2.8 in a disposable Python environment:
actual Lua 5.1, not the installed system Lua 5.4. XLua property and discarded
dofile-return behavior are simulated in the adapter regression; these dry
checks do not substitute for the real X-Plane/XLua flight loop.

## Current author inputs

Read-only source directory: `/Users/wahltho/Downloads/Level Up`.

| ACF | SHA-256 |
|---|---|
| 737_60NG.acf | c808d3536fd938bb76c51e0acf7256bd65bed2a7380eabbec496ccde90a518d4 |
| 737_70NG.acf | 8cb0d7254e63cd1a2b4fe88071e706393504e6bfce7ab6af3cca417d22ea3c31 |
| 737_80NG.acf | 0ada8a33da3a479b51cc6f08a372f9ebfcdaf85bb2b92c59a58941c33510083e |
| 737_90NG.acf | ffdff69b3693667ffdb85369aaa2fbe8ed0bc08874ef763aeb16c8ce021f891a |
| 737_9ENG.acf | c2c0db2907904fb50fbd281f96d46c90e1191f002ed360bcaed778ba106cfed2 |

## Reproduce (maintainer environment)

Use a disposable Python environment with `lupa==2.8` for the Lua runner.
The installer tests additionally use locally available original .35 Lua
and historical release fixtures. Run from the repository root:

```text
python tools/test_lua51.py --aircraft-root "/path/to/Level Up"
python tests/test_acf_contract.py
python tests/test_installer.py
python tests/test_toolkit_contract.py
python tools/build_release.py
python tests/test_release.py --lua51-syntax
python tests/test_release.py --lua51-syntax --aircraft-root "/path/to/Level Up"
git diff --check
```

Remaining simulator acceptance is defined in `RUNTIME_TEST_PLAN.md`.
No claim of complete in-flight/aircraft-realism validation is made.
