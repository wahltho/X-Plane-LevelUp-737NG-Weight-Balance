# LevelUp 737NG weight-and-balance compatibility patch

This repository is the canonical source for the unofficial patch that integrates
Jochen Heiden's LevelUp
`737_60NG.acf`, `737_70NG.acf`, `737_80NG.acf`, `737_90NG.acf` and `737_9ENG.acf` with the
unmodified upstream Zibo 4.05.35 `zibomod.xpl`, Tablet Lua and FMS Lua. Release `v0.4.1`
supports Variant-IDs `3/2/0/1/4` (`737-600/-700/-800/-900/-900ER`) from one package.
Every MAX variant and stock Zibo delegate to the original Tablet
functions.

The initial standalone repository import is derived from the committed
`Documentation/levelup_ng_wb_patch` state through Zibo Mod commit `4f2ff389`.
Future public LevelUp W&B patch development belongs here; the private C++ port
remains owned by the Zibo Mod repository.

`v0.4.1` supersedes the -700-only `v0.1.4` and common
`v0.2.0`/`v0.2.1`/`v0.2.2`/`v0.2.3`
packages. The installer migrates the five old `LEVELUP_700_WB` blocks in place,
preserves the original v0.1.x backup and installs the common adapter only after
all stock Tablet functions are defined. Existing v0.2.x hooks remain valid;
v0.2.2 synchronized provenance with Jochen's final 700/800 V2.S1.51 inputs.
Release v0.2.3 fixed the Windows `luac.exe` temporary-file handoff. Release
v0.3.0 added Jochen's first -900/-900ER contracts and exact per-variant cargo
normalization. v0.3.1 follows the refined 2026-08-22 -900/-900ER station and
tank geometry; both variants now use fixed `69 / 62 / 69 ft` tank arms. The loader remains directly
after `jit.off()`; it never assigns the discarded XLua `dofile()` return value.
Release v0.3.2 additionally closed the LevelUp FMC ZFW/GW owner mismatch. For
supported IDs, FMS ZFW uses ACF empty mass plus the nine physical
`m_stations` values and no longer subtracts Zibo's inherited `524 kg` pilots a
second time. Stock Zibo and unsupported variants retain the upstream formula.
Release v0.4.0 added Jochen's first V2.S1.51 -600 contract to that complete owner chain.
Release v0.4.1 follows the refined -600 station geometry by moving Cargo1,
Cargo2, Zone 2, Zone 4 and Zone 5 forward while leaving all other W&B fields
and unrelated flight-model tuning outside the semantic contract.

## Owner contract

- Internal payload mode: the Tablet selection owns nine X-Plane
  `m_stations[0..8]` values for each supported variant. Each station moves at
  `222 kg/s`. The patch never writes aggregate `m_fixed`.
- External payload mode: the patch and stock Tablet are read-only toward
  payload. The current X-Plane station values are the prediction input.
- Current/in-flight CG: X-Plane's `cg_offset_z_mac` is the sole owner and EFB
  source.
- ZFW/TOW/LW CG: the common mass-and-moment core uses the active ACF contract,
  calibrates its coordinate system from X-Plane's current ZFW offset, and uses
  the same derived LEMAC for predictions and fixed limits.
- EFB/FMC: existing Tablet DataRefs consume the replacement calculations;
  takeoff CG is continuously published through `calc_to_cg`. FMC ZFW/GW uses
  the same physical station owner for supported LevelUp variants. Existing FMC
  CG acceptance and trim tables remain unchanged.
- Lifecycle: save/load, SimBrief and slow loading keep the stock Tablet zone
  state. Variant changes invalidate the calibrated LEMAC and warning state
  before the new aircraft contract can own any result.

## ACF contracts

The installer verifies only the W&B fields consumed by the integration. It
accepts unrelated flight-model tuning and does not require a whole-file
checksum.

| Variant | ID | ACF contract | Empty / max mass | MAC |
|---|---:|---|---:|---:|
| 737-600 | 3 | `levelup600-wb-v2` | `80199.78 / 124499.8 lb` | `14.878139496 ft` |
| 737-700 | 2 | `levelup700-wb-v1` | `82999.61 / 154499.9 lb` | `14.992128372 ft` |
| 737-800 | 0 | `levelup800-wb-v2` | `91514.04 / 174700 lb` | `14.992127419 ft` |
| 737-900 | 1 | `levelup900-wb-v2` | `94580 / 174700 lb` | `14.993530273 ft` |
| 737-900ER | 4 | `levelup900er-wb-v2` | `98495 / 187699.31 lb` | `14.993530273 ft` |

All five contracts contain two cargo stations, five passenger zones and two
service/cabin-crew stations. The refined -900 and -900ER contracts both use
`69 / 62 / 69 ft` constant tank arms.

The ACF remains authoritative at capacity boundaries. Rounded stock Tablet
cargo selections are normalized to the exact active ACF maxima before the EFB,
station writer and FMC prediction consume them. See `SOURCE.md` for the exact
margins.

## Installation

See `INSTALLATION.md`. Versioned distributable archives and their SHA-256
checksum files are published on the repository's GitHub Releases page:

- `LevelUp-737NG-Weight-Balance-v0.4.1.zip`
- `LevelUp-737NG-Weight-Balance-v0.4.1.zip.sha256`

Extract the archive directly into `plugins/xlua/scripts/B738.tablet/`, then
run:

```text
python3 z_Install_LevelUp_NG_WB.py
```

The archive contains the Lua modules, installer, source evidence, owner matrix
and runtime guide. It does not contain the aircraft ACFs; those are aircraft
package inputs verified in their normal LevelUp root.

## Acceptance boundary

The -700 station/current-CG path was observed at `22.63 %MAC` with v0.1.3.
The v0.1.3 planned-CG failure was traced to an XLua local property binding and
fixed in v0.1.4. The new -600 and revised -800/-900/-900ER contracts have no simulator
acceptance evidence yet. Dry tests prove deterministic math, owner delegation,
variant cache invalidation, installer migration and archive integrity; they do
not prove X-Plane runtime behavior.

## Repository dry verification

The maintainer tests use local reference paths and are not included in the
end-user archive. In this source directory run:

```text
luac -p B738.tablet_levelup_ng_wb_*.lua
lua tests/test_core.lua
lua tests/test_adapter.lua
python3 tests/test_acf_contract.py
python3 tests/test_overlay_reconcile.py
python3 tests/test_installer.py
python3 tests/test_release.py
python3 tests/test_toolkit_contract.py
```

No plugin build or modified binary is involved.

## Maintenance Toolkit contract

This repository owns the W&B module and its independent version history. It
does not define a separate end-user action in the Maintenance Toolkit. The
Toolkit's consolidated LevelUp compatibility package imports a pinned release
of this module together with the other LevelUp compatibility modules.

The source handoff is machine-readable:

- `patches/B738.tablet.lua.json` contains the five structural Tablet changes;
- `patches/B738.a_fms.lua.json` contains the two structural FMS changes;
- `contracts/levelup-ng-wb-acf-v0.4.1.json` contains the semantic ACF fields
  required by the five supported variants;
- `toolkit/weight-and-balance-module.json` binds payload hashes, target paths,
  variant IDs and the intended schema-3 operations.

The module contract is deliberately not advertised as a standalone Toolkit
catalog entry. The Toolkit must add semantic ACF-contract validation before
the consolidated package can enable this module; whole-file ACF checksums
would incorrectly reject unrelated flight-model tuning.
