#!/usr/bin/env python3
"""The fixed independent data test must reject missing/reversed/double datum.

Only temporary copies are mutated; release source and aircraft stay untouched.
"""
from pathlib import Path
import shutil
import tempfile
from lupa.lua51 import LuaRuntime, LuaError

ROOT = Path(__file__).resolve().parents[1]
NAME = "B738.tablet_levelup_ng_wb_data.lua"
source = (ROOT / NAME).read_text()
needle = "arm = data.empty_cg_z_m + arm"
assert source.count(needle) == 1
for label, replacement in (
    ("missing reference (0.5.0/0.5.1 defect)", "arm = arm"),
    ("wrong sign", "arm = arm - data.empty_cg_z_m"),
    ("double reference", "arm = 2 * data.empty_cg_z_m + arm"),
):
    with tempfile.TemporaryDirectory(prefix="wb-datum-mutant-") as directory:
        temp = Path(directory)
        (temp / "tests").mkdir()
        test = temp / "tests/test_data.lua"
        shutil.copy2(ROOT / "tests/test_data.lua", test)
        shutil.copy2(ROOT / "B738.tablet_levelup_ng_wb_core.lua", temp)
        (temp / NAME).write_text(source.replace(needle, replacement))
        lua = LuaRuntime()
        lua.globals().arg = lua.table_from({0: str(test)})
        try:
            lua.execute("dofile(...)", str(test))
        except LuaError as error:
            # Require the independent numeric comparison to fail, not syntax
            # or a missing fixture: the historical test oracle stays intact.
            assert " != 634340" in str(error), str(error)
        else:
            raise AssertionError(f"undetected datum mutant: {label}")
    print(f"PASS: independent mass/moment oracle rejects {label}")
