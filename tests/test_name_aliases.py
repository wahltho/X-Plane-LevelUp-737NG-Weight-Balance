#!/usr/bin/env python3
"""Independent old/new-label matrix through installer AND actual Lua 5.1 parser."""
import contextlib
import importlib.util
import io
import json
import tempfile
from pathlib import Path
import sys
from lupa.lua51 import LuaRuntime

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
spec = importlib.util.spec_from_file_location("installer", ROOT / "z_Install_LevelUp_NG_WB.py")
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)
runtime = LuaRuntime(unpack_returned_tuples=True)
data = runtime.execute("return dofile(...)", str(ROOT / "B738.tablet_levelup_ng_wb_data.lua"))
# Never generate the expectation from the current production policy.
fixtures = json.loads((ROOT / "contracts/levelup-ng-wb-acf-v0.4.1.json").read_text())["variants"]
cases = 0

def check(contract, fields, accepted):
    global cases
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / contract["name"]
        path.write_text("I\n1200 Version\n" + "".join(f"P {k} {v}\n" for k, v in fields.items()))
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            try:
                installer.verify_acf(path, contract)
                installed = True
            except SystemExit as error:
                assert error.code == 2
                installed = False
        result = data.read_metadata(str(path), data[contract["variantId"]])
        metadata = result[0] if isinstance(result, tuple) else result
        assert installed == accepted, (contract["name"], "installer", fields)
        assert bool(metadata) == accepted, (contract["name"], "Lua", fields)
        cases += 1

for contract in installer.ACF_CONTRACTS:
    fixture = next(row for row in fixtures if row["name"] == contract["name"])
    baseline = {**fixture["text"], **fixture["number"]}
    check(contract, baseline, True)
    for aft in ("Galley A", "Galley R"):
        for right in ("Right Main", "Right Wing"):
            expected = (aft == "Galley A" or contract["variantId"] == 2) and (
                right == "Right Main" or contract["variantId"] == 3)
            check(contract, {**baseline, "acf/_fixed_name/8": aft, "acf/_tank_name/2": right}, expected)
    for key, wrong in (("acf/_fixed_name/7", "Galley R"),
                       ("acf/_tank_name/0", "Right Wing"),
                       ("acf/_fixed_name/8", "Galley X"),
                       ("acf/_tank_name/2", "Right Unknown")):
        check(contract, {**baseline, key: wrong}, False)
    for a, b in (("acf/_fixed_name/7", "acf/_fixed_name/8"),
                 ("acf/_tank_name/0", "acf/_tank_name/2")):
        check(contract, {**baseline, a: baseline[b], b: baseline[a]}, False)
    for key in ("acf/_fixed_name/8", "acf/_tank_name/2"):
        missing = dict(baseline)
        del missing[key]
        check(contract, missing, False)

print(f"PASS: {cases} independent name cases, installer/Lua agreement across all five variants")
