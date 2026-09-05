# v0.5.1 validation — 2026-09-05

Scope: alias-only public upstream Lua compatibility release. No author ACF,
overlay, private C++ source, Toolkit repository or simulator install modified.

Status: public-module automated regression and packaged-installation checks PASS.

| Check | Result |
|---|---|
| 65 independent name cases through installer and real Lua 5.1 parser | PASS |
| Old/new aliases, all five variants, missing/unknown/swapped names | PASS |
| Lua 5.1 syntax, core independent mass/moment and dynamic-data regressions | PASS |
| Adapter owners, external read-only, lifecycle and FMC handoff | PASS |
| Alias-only reload preserves GW/ZFW/TO/OEW/LW CG and FMC handoff | PASS |
| Five previous full author ACFs: metadata, units, independent lb-ft moments | PASS |
| New -600/-700 plus previous -800/-900/-900ER full ACFs | PASS |
| ACF numeric/layout mutation regression | PASS |
| Installer LF/CRLF, migrations, idempotence, uninstall | PASS |
| 0.5.0 upgrade with new names; Tablet/FMS hooks byte-identical | PASS |
| Windows luac handoff / Lua 5.4 compiler rejection | PASS |
| Tablet performance / VNAV FMS patch coexistence | PASS |
| Toolkit module hashes, operations, canonical names and alias metadata | PASS |
| ZIP contents/hash/source parity, full fresh install and Lua 5.1 syntax | PASS |
| Packaged installs with synthetic, previous and new author inputs | PASS |
| git diff --check | PASS |
| Consolidated Toolkit import/release | Separate owner; not performed |
| X-Plane upstream XLua runtime/flight validation | NOT RUN |

Two intermediate test failures were fixture/assertion defects, not production
fixes: historical upgrades initially inherited new canonical names from the
current policy; their input now remains the frozen old author fixture. The
0.5.0 upgrade initially expected an `Installed` message, but unchanged hooks
correctly report `already in the requested state`. The final test requires
verified v0.5.1 payload, unchanged hook hashes, updated module, idempotence,
unchanged ACF hashes and preservation of co-installed patch blocks.

Author inputs: previous five ACFs in `Downloads/Level Up`; revised -600 and
-700 in `Downloads`. Full source files are read-only test inputs, not payloads.
Their W&B numeric fields are unchanged; the -600 also contains unrelated
flight-model edits, which are neither incorporated nor validated here.

Revised input SHA-256:

- 737_60NG.acf: `aede06487ef0080af2769bdbc69f01015e107d26c1fb8a44eea5a5932624a915`
- 737_70NG.acf: `74d5ccb24cfff5444993d67a148cf6fa923c7d39e299219c58186f90d8b44750`

Previous input hashes are in `VALIDATION_0.5.0.md` in the repository history.

## Reproduce

Use Python with `lupa==2.8` (actual Lua 5.1). Installer migration tests require
the locally archived historical release ZIPs and original upstream .35 Lua.

```text
python tools/test_lua51.py --aircraft-root "/path/to/previous-five-ACFs"
python tools/test_lua51.py --aircraft-root "/path/to/previous-five-ACFs" --updated-aircraft-root "/path/to/new-600-and-700"
python tests/test_name_aliases.py
python tests/test_acf_contract.py
python tests/test_installer.py
python tests/test_toolkit_contract.py
python tools/build_release.py
python tests/test_release.py --lua51-syntax
python tests/test_release.py --lua51-syntax --aircraft-root "/path/to/previous-five-ACFs"
python tests/test_release.py --lua51-syntax --aircraft-root "/path/to/previous-five-ACFs" --updated-aircraft-root "/path/to/new-600-and-700"
git diff --check
```

The historical private-overlay audit is outside this public module's acceptance
scope and remains unchanged. No X-Plane/XLua runtime validation is claimed.
