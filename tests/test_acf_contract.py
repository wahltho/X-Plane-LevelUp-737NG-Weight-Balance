#!/usr/bin/env python3
"""Layout gate plus numeric changes, independently frozen author fixtures."""
import contextlib
import importlib.util
import io
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("wb_installer", ROOT / "z_Install_LevelUp_NG_WB.py")
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)
fixtures = json.loads((ROOT / "contracts/levelup-ng-wb-acf-v0.4.1.json").read_text())["variants"]

def check(contract, fields, accepted):
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / contract["name"]
        path.write_text("I\n1200 Version\n" + "".join(f"P {k} {v}\n" for k, v in fields.items()))
        try:
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                installer.verify_acf(path, contract)
        except SystemExit as error:
            assert not accepted and error.code == 2
        else:
            assert accepted

for contract in installer.ACF_CONTRACTS:
    fixture = next(row for row in fixtures if row["name"] == contract["name"])
    baseline = {**fixture["text"], **fixture["number"]}
    check(contract, baseline, True)
    # Each numeric change is intentional test input, NOT a new aircraft baseline.
    for key, value in {
        "acf/_fixed_ref/2,2": 26.5, "acf/_fixed_max/0": 4300,
        "acf/_m_empty": 81000, "acf/_cgZ": 46,
        "acf/_average_mac_acf": 15.1, "acf/_cgZ_fwd": 44,
        "acf/_cgZ_aft": 68, "acf/_m_max": 190000,
        "acf/_m_fuel_max_tot": 53000, "acf/_tank_xyz/0,2": 60,
        "acf/_tank_xyz_full/0,2": 66, "acf/_fixed_role/7": 0,
    }.items():
        check(contract, {**baseline, key: value}, True)
    for key, value in {
        "acf/_fixed_name/2": "Cargo1", "acf/_fixed_max/count": 8,
        "acf/_fixed_max/0": 0, "acf/_fixed_ref/4,2": "nan",
        "acf/_average_mac_acf": 0, "acf/_m_empty": -1,
        "acf/_m_max": 1, "acf/_cgZ_fwd": 100,
        "acf/_tank_rat/3": 0.01, "acf/_tank_rat/0": 0.2,
        "acf/_tank_xyz_full/1,2": "inf", "acf/_tank_name/0": "Center Wing",
    }.items():
        check(contract, {**baseline, key: value}, False)
    for key in ("acf/_m_empty", "acf/_average_mac_acf", "acf/_fixed_ref/0,2"):
        missing = dict(baseline)
        del missing[key]
        check(contract, missing, False)

print("PASS: all five author fixtures, dynamic W&B geometry accepted, malformed/layout changes rejected")
