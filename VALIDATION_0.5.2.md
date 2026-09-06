# v0.5.2 validation — 2026-09-06

Scope: public Lua runtime station-datum correction, not aerodynamic tuning.
No author ACF, overlay, Toolkit repository or simulator install is modified.

## Root cause and independent evidence

The native DRT screenshot has original CG 60.34 ft and first station offset
-7.412736 m. Absolute station position = 60.34 * 0.3048 - 7.412736 =
10.978896 m = 36.02 ft. All nine screenshot offsets match the independently
stored Zibo ACF positions after this conversion (within 2 micrometres of
rounded values). The local DataRefs.txt origin description is inconsistent
with this measured getter behavior.

Versions 0.5.0/0.5.1 treated those offsets as absolute positions. Their test
inputs repeated that mistake. Dynamic current-ZFW calibration could conceal
it for the current load but corrupted forecasts with different payload mass.
Only input fixtures change; independent absolute positions and kg-m/lb-ft
mass/moment oracles remain unchanged.

The separate upstream partial replay executes the original .35 payload-entry,
loading publication and CG-graph functions with the real adapter and a modeled
X-Plane mass/moment boundary. For its synthetic 100-PAX / 0 service / 0 center
case: current CG 24.064907%, TO 23.983102%, OEW 22.000000%. Six fuel/service
combinations and settled one-frame lag agree within 1e-9 %MAC. These are
independent synthetic control values, not the reporter's actual flight values.
Full extraction details and original failing datum experiment are recorded in
`tests/PAYLOAD_GRAPH_REPLAY_2026_09_06.md` in the source repository.

## Automated acceptance

Status: all automated acceptance rows below PASS; simulator and consolidated
Toolkit rollout remain separate, unperformed layers.

| Check | Required coverage |
|---|---|
| Lua 5.1 syntax/core/data/adapter | five variants; independent moments; native offsets; nine measured values; reference change; owner/delegation/lifecycle |
| Datum mutation checks | independent unchanged 634340 kg-m oracle rejects missing, reversed and doubled reference additions |
| Actual ACF input checks | previous five ACFs, revised -600/-700 with previous -800/-900/-900ER; independent lb-ft oracle |
| Partial upstream replay | 100 PAX loading, graph, TO/OEW/ZFW; center 0/100/500 kg; service 0/675 kg; one-frame lag |
| Name and numeric guards | 65 old/new/invalid name cases; invalid layout/numeric rejection |
| Installer | LF/CRLF; historical upgrades through 0.5.1; idempotence/uninstall; Windows temporary file and Lua 5.4 rejection |
| Coexistence | Tablet performance and FMS VNAV blocks preserved; .0/.1 upgrade hooks byte-identical |
| Toolkit module | exact payload hashes/sizes, targets, unchanged operation schemas and aliases |
| Release ZIP | exact contents, checksums/source parity, fresh install, Lua 5.1 syntax; synthetic/previous/current inputs |
| Simulator acceptance | NOT RUN; required after release |
| Consolidated Toolkit release | separate owner; NOT performed here |

Original .35 Lua and unchanged author ACF paths/hashes are documented in
`tests/PAYLOAD_GRAPH_REPLAY_2026_09_06.md` and `VALIDATION_0.5.1.md` (repository).
The historical private-overlay snapshot audit is outside this public module's
acceptance scope; it is not silently included in the green result.

## Reproduce

Use Python with Lupa 2.8 (`lupa.lua51`, actual Lua 5.1). Historical ZIPs and
original .35 Lua are read-only local inputs for installer migration checks.

```text
python tools/test_lua51.py --aircraft-root "/path/to/previous-five-ACFs"
python tools/test_lua51.py --aircraft-root "/path/to/previous-five-ACFs" --updated-aircraft-root "/path/to/new-600-and-700"
python tests/test_upstream_payload_graph.py --acf "/path/to/737_60NG.acf"
python tests/test_station_datum_mutations.py
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

## Runtime follow-up

Repeat the -600 engines-running, 100-PAX, page-3 graph report, then all five
variants through internal/external load changes, crew/galley, taxi/destination
fuel and aircraft reload. Record current CG in %MAC (`real_cg_mac`), not the
metre-valued `real_cg`; compare calculated TO CG, explicitly accepted FMC CG
and trim. Current/planned states may differ during loading; OEW includes
service mass. No new trim offset or automatic override of pilot-entered CG.
The full matrix is `RUNTIME_TEST_PLAN.md`; release is not runtime closure.
