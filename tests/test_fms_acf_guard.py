#!/usr/bin/env python3
"""Focused, unrun-until-approved Lua 5.1 regression for the actual FMS fragments."""
import argparse
import json
import tempfile
from pathlib import Path
from lupa.lua51 import LuaRuntime

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument("--legacy-aircraft-root", type=Path, action="append", default=[])
args = parser.parse_args()
fixtures = json.loads((ROOT / "contracts/levelup-ng-wb-acf-v0.4.1.json").read_text())["variants"]
data_source = (ROOT / "B738.tablet_levelup_ng_wb_data.lua").read_text()
binding = (ROOT / "Add_levelup_ng_wb_fms_empty_weight.txt").read_text()
formula = (ROOT / "Replace_levelup_ng_wb_fms_zfw_owner.txt").read_text()
reset = (ROOT / "Add_levelup_ng_wb_fms_reset.txt").read_text()

with tempfile.TemporaryDirectory() as temporary:
    root = Path(temporary)
    lua = LuaRuntime(unpack_returned_tuples=True)
    messages = []
    lua.globals().print = lambda *items: messages.append(items)
    def load_data(name):
        assert name == "../B738.tablet/B738.tablet_levelup_ng_wb_data.lua"
        lua.execute(data_source)  # XLua discards the loaded chunk's return value.
    lua.globals().dofile = load_data
    lua.execute("""
        function find_dataref(name)
            if name == "sim/aircraft/weight/acf_m_empty" then return 40000 end
            return ""
        end
        B738DR_oew_kg, simDR_payload_weight, full_crew_weight = 40500, 9000, 1024
        simDR_payload_stations = {[0]=100,[1]=200,[2]=300,[3]=400,[4]=500,
            [5]=600,[6]=700,[7]=800,[8]=900}
    """)
    # The local reader stays private, exactly as in the patched upstream chunk.
    calculate, reload = lua.execute(binding + "\nreturn function()\n" + formula +
        "\nreturn zfw_real end, function()\n" + reset + "\nend")
    lua.globals().file_path2 = str(root) + "/"
    for row in fixtures:
        fields = {**row["text"], **row["number"]}
        path = root / row["name"]
        def write(values):
            path.write_text("I\n1200 Version\n" + "".join(
                f"P {key} {value}\n" for key, value in values.items()))
        lua.globals().B738DR_b737_variant = row["variantId"]
        lua.globals().simDR_levelup_ng_wb_acf_path = "Aircraft/LU/" + row["name"]
        write(fields)
        reload()
        assert calculate() == 44500  # independent physical-station total 4500
        for changes in ({"acf/_fixed_name/0": "Pax Fwd"},
                        {"acf/_fixed_max/8": 0},
                        {"acf/_fixed_ref/7,2": "missing"}):
            write({**fields, **changes})
            reload()
            assert calculate() == 48476  # original OEW + scalar payload - crew
        path.unlink()
        reload()
        assert calculate() == 48476
        write(fields)
        reload()
        assert calculate() == 44500
        lua.globals().simDR_levelup_ng_wb_acf_path = "Aircraft/LU/wrong.acf"
        assert calculate() == 48476
    for legacy in args.legacy_aircraft_root:
        lua.globals().file_path2 = str(legacy) + "/"
        for row in fixtures:
            assert (legacy / row["name"]).is_file()
            lua.globals().B738DR_b737_variant = row["variantId"]
            lua.globals().simDR_levelup_ng_wb_acf_path = "Aircraft/LU/" + row["name"]
            reload()
            assert calculate() == 48476, (legacy, row["name"])
    assert not messages, "ACF rejection must not emit W&B warnings"
    lua.globals().B738DR_b737_variant = -1
    assert calculate() == 48476
print("PASS: FMS old/missing/malformed ACF delegation, valid five-variant ownership and reload")
