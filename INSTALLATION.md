# Installation guide

## Requirements

- LevelUp 737NG Series using upstream Zibo 4.05.35 Tablet Lua and the
  unmodified upstream `zibomod.xpl`.
- `737_60NG.acf`, `737_70NG.acf`, `737_80NG.acf`, `737_90NG.acf` and `737_9ENG.acf` matching
  `levelup600-wb-v2`, `levelup700-wb-v1`, `levelup800-wb-v2`, `levelup900-wb-v2` and
  `levelup900er-wb-v2`. Unrelated flight-model changes are allowed.
- Python 3. No compiler or plugin build is required.

The reference ACF SHA-256 values are recorded in `SOURCE.md`. They establish
provenance only; installation is controlled by the individual consumed W&B
fields, not the whole-file hash. The role category is intentionally excluded
from the gate so that the current -900ER ACF and Jochen's announced correction
of its Galley F/A roles are both accepted.

## Install or upgrade

1. Close X-Plane.
2. Back up the LevelUp test aircraft.
3. Open `plugins/xlua/scripts/B738.tablet/` in the LevelUp aircraft folder.
4. Extract every file from
   `LevelUp-737NG-Weight-Balance-v0.4.2.zip` directly into that folder. Do not
   create another subfolder.
5. Run one of:

   ```text
   py z_Install_LevelUp_NG_WB.py
   python z_Install_LevelUp_NG_WB.py
   python3 z_Install_LevelUp_NG_WB.py
   ```

The installer must report:

- package payload `v0.4.2` verified;
- all five ACF contracts verified;
- Lua syntax passed when a Lua 5.1-compatible `luac` is available, or skipped
  with an informational message for incompatible system compilers;
- LevelUp 737NG W&B hooks installed.

For an aircraft root outside the normal four-parent layout, use:

```text
python3 z_Install_LevelUp_NG_WB.py --aircraft-root "/path/to/LU 737NG Series"
```

A fresh install creates `B738.tablet.lua.levelupngwb.backup` and sibling
`B738.a_fms.lua.levelupngwb.backup` files once. An upgrade
from the -700-only v0.1.x package keeps
`B738.tablet.lua.levelup700wb.backup` unchanged and migrates the old five
marked blocks. Do not uninstall v0.1.4 first. A full X-Plane restart is
required after installing or upgrading.

For an existing v0.2.0 through v0.4.1 installation, extract v0.4.2 over
the same Tablet folder and run the installer normally. Do not uninstall first.
The five common Tablet hooks are unchanged. The installer adds two marked
blocks to the sibling `B738.a_fms/B738.a_fms.lua` and verifies all five current
ACF contracts. Existing marked VNAV descent-table and Tablet performance
patches are preserved.

The v0.2.3 Windows `luac.exe` temporary-file fix remains included.

Release v0.4.2 additionally ignores Lua 5.2 through 5.4 system compilers for
whole-file validation because the embedded Zibo Lua targets XLua/LuaJIT 5.1
semantics. Patch anchors and ACF contracts are still validated normally.

The installer tolerates other marked compatibility patches and both LF and
CRLF line endings. It refuses an unsupported stock Tablet structure or a
changed W&B field rather than guessing a source edit.

## Capacity boundary

The ACF station maxima are authoritative. Rounded stock Tablet cargo values
are normalized to the exact active ACF maximum before any station or CG write:

- -700 Cargo 1/2 differ from the stock Tablet ceiling by `21.912 / 42.213 kg`.
- -600 Cargo 1/2 have the same exact maxima and margins as the -700.
- -800 and -900 Cargo 1/2 differ by `0.207 / 1.098 kg`.
- -900ER Cargo 1/2 differ by `0.207 / 87.280 kg`.
- -800 Galley F/A combined with half the cabin crew can exceed the `3000-lb`
  ACF station maximum by `24.823 / 72.823 kg` at the extreme Tablet entries.

Cargo normalization preserves the requested total whenever the two cargo
stations have enough combined capacity. A service-station excess invalidates
the complete target instead of silently dropping cabin crew or catering mass.

## Remove

Close X-Plane and run from the same Tablet folder:

```text
python3 z_Install_LevelUp_NG_WB.py --uninstall
```

This removes only the five common Tablet W&B blocks and the two FMS W&B blocks,
then restores the stock payload gates and stock FMS ZFW formula. It preserves
other compatibility patches and all backup files. Package files can then be
deleted manually.

## First simulator evidence

Follow `RUNTIME_TEST_PLAN.md`. At minimum record all nine `m_stations`,
`m_fixed`, three fuel tanks, X-Plane current/ZFW offsets and `%MAC`, EFB
current/ZFW/TOW/LW CG, `calc_to_cg`, FMC CG and takeoff trim. Matching displays
alone are not proof that station and fuel ownership agree.
