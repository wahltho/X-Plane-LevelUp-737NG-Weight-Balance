#!/usr/bin/env python3
"""Optional Lua 5.1 test runner: install lupa in a disposable Python venv."""
import argparse
from pathlib import Path
from lupa.lua51 import LuaRuntime

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument("--aircraft-root", type=Path)
parser.add_argument("--syntax", type=Path, action="append", default=[])
args = parser.parse_args()
tests = ["test_core.lua", "test_data.lua", "test_adapter.lua"]
if args.aircraft_root:
    tests.append("test_loaded_acf.lua")
for name in tests:
    path = ROOT / "tests" / name
    runtime = LuaRuntime(unpack_returned_tuples=True)
    runtime.globals().arg = runtime.table_from({
        0: str(path), 1: str(args.aircraft_root.resolve()) if args.aircraft_root else "",
    })
    runtime.execute("dofile(...)", str(path))
for path in [*ROOT.glob("B738.tablet_levelup_ng_wb_*.lua"), *args.syntax]:
    LuaRuntime().execute("assert(loadfile(...))", str(path.resolve()))
    print(f"PASS Lua 5.1 syntax: {path.name}", flush=True)
