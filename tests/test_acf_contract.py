#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
import math
import os
import re
from pathlib import Path


PACKAGE = Path(__file__).resolve().parents[1]
REPO = Path(os.environ.get("ZIBO_MOD_REPOSITORY", "/Users/wahltho/Documents/Projects/Zibo Mod"))
OVERLAY = REPO / "overlay/LU 737NG Series"
DATA = PACKAGE / "B738.tablet_levelup_ng_wb_data.lua"
INSTALLER = PACKAGE / "z_Install_LevelUp_NG_WB.py"

EXPECTED = {
    "737_70NG.acf": {
        "variant": 2, "version": "levelup700-wb-v1",
        "reference_hash": "8cb0d7254e63cd1a2b4fe88071e706393504e6bfce7ab6af3cca417d22ea3c31",
        "overlay_hash": "a5d2cdd9e7dec57ec42d22a0937f3c08ee56e1adbd7334b87bbfd38fb9a811f2",
        "mass": (82999.61, 49.029998779, 47.189998627, 50.939998627, 14.992128372, 154499.9, 46062.008),
        "names": ("Cargo1", "Cargo2", "Zone 1", "Zone 2", "Zone 3", "Zone 4", "Zone 5", "Galley F", "Galley R"),
        "arms": (29, 69, 22, 34, 46, 58, 70, 15, 80),
        "maxima": (4200, 6900, 8000, 8000, 8000, 8000, 8000, 3000, 3000),
        "roles": (1, 1, 0, 0, 0, 0, 0, 1, 1),
        "tank_empty": (52.650001526, 46, 52.650001526), "tank_full": (52.650001526, 46, 52.650001526),
    },
    "737_80NG.acf": {
        "variant": 0, "version": "levelup800-wb-v2",
        "reference_hash": "9315f4110ae8c2b5feb53872ae3d7a6bcc2ff380099b6c925c9734d2d65fbe16",
        "overlay_hash": "e3bb89129fc2400581fec27e8b2c2947a99b06e0aefc24cb3d40a833fc0f5c1c",
        "mass": (91514.04, 59.889999390, 57.869998932, 61.840000153, 14.992127419, 174700.0, 46062.01),
        "names": ("Cargo1", "Cargo2", "Zone 1", "Zone 2", "Zone 3", "Zone 4", "Zone 5", "Galley F", "Galley A"),
        "arms": (37, 85, 33.5, 46.5, 58.5, 70.5, 82.5, 15, 99),
        "maxima": (7848, 10690, 10000, 10000, 10000, 10000, 10000, 3000, 3000),
        "roles": (1, 1, 0, 0, 0, 0, 0, 1, 1),
        "tank_empty": (64, 56.5, 64), "tank_full": (64, 56.5, 64),
    },
    "737_90NG.acf": {
        "variant": 1, "version": "levelup900-wb-v2",
        "reference_hash": "4b4ec0617e7aa1786be362e9cfe1ab60d92ba1b097e8145e896d31f835f842e9",
        "overlay_hash": "0134a4d8537ab3f65a79e2eea7f8a0335a0622350bc217ad03a308b025ee8faa",
        "mass": (94580, 64.650001526, 63.380001068, 67.129997253, 14.993530273, 174700, 46062.008),
        "names": ("Cargo1", "Cargo2", "Zone 1", "Zone 2", "Zone 3", "Zone 4", "Zone 5", "Galley F", "Galley A"),
        "arms": (45, 89, 34, 47.5, 65, 77, 91, 15, 108),
        "maxima": (7848, 10690, 10000, 10000, 10000, 10000, 10000, 3000, 3000),
        "roles": (1, 1, 0, 0, 0, 0, 0, 1, 1),
        "tank_empty": (69, 62, 69), "tank_full": (69, 62, 69),
    },
    "737_9ENG.acf": {
        "variant": 4, "version": "levelup900er-wb-v2",
        "reference_hash": "c2c0db2907904fb50fbd281f96d46c90e1191f002ed360bcaed778ba106cfed2",
        "overlay_hash": "db05c59bf4892be62240b9fcb5ae5a338870d255ae72606c8f2088b4827fe9fb",
        "mass": (98495, 65.389999390, 64.879997253, 67.879997253, 14.993530273, 187699.31, 52512.31),
        "names": ("Cargo1", "Cargo2", "Zone 1", "Zone 2", "Zone 3", "Zone 4", "Zone 5", "Galley F", "Galley A"),
        "arms": (45, 89, 34, 47.5, 65, 77, 91, 15, 108),
        "maxima": (7848, 10500, 10000, 10000, 10000, 10000, 10000, 3000, 3000),
        "roles": (1, 1, 0, 0, 0, 0, 0, 1, 1),
        "tank_empty": (69, 62, 69), "tank_full": (69, 62, 69),
    },
}


def values(path: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("P acf/"):
            key, value = line[2:].split(" ", 1)
            assert key not in result, key
            result[key] = value
    return result


spec = importlib.util.spec_from_file_location("levelup_ng_installer", INSTALLER)
assert spec is not None and spec.loader is not None
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)
contracts = {str(contract["name"]): contract for contract in installer.ACF_CONTRACTS}
assert set(contracts) == set(EXPECTED)

ratios = (0.187000006, 0.625999987, 0.187000006, 0, 0, 0, 0, 0, 0)
mass_keys = ("acf/_m_empty", "acf/_cgZ", "acf/_cgZ_fwd", "acf/_cgZ_aft", "acf/_average_mac_acf", "acf/_m_max", "acf/_m_fuel_max_tot")
for name, expected in EXPECTED.items():
    path = OVERLAY / name
    assert hashlib.sha256(path.read_bytes()).hexdigest() == expected["overlay_hash"]
    acf = values(path)
    contract = contracts[name]
    assert contract["version"] == expected["version"]
    text = dict(contract["text"])
    numbers = dict(contract["number"])
    assert [numbers[key] for key in mass_keys] == list(expected["mass"])
    for key, wanted in text.items():
        assert acf[key] == wanted, (name, key)
    for key, wanted in numbers.items():
        assert math.isclose(float(acf[key]), float(wanted), rel_tol=1e-9, abs_tol=1e-6), (name, key)
    for index in range(9):
        assert int(float(acf[f"acf/_fixed_role/{index}"])) == expected["roles"][index]
        assert f"acf/_fixed_role/{index}" not in numbers
        assert numbers[f"acf/_tank_rat/{index}"] == ratios[index]

source = DATA.read_text(encoding="utf-8")
for expected in EXPECTED.values():
    assert expected["version"] in source
    assert expected["reference_hash"] in source
station_rows = re.findall(r'\{ name = "([^\"]+)",\s+arm_m = ([0-9.]+) \* FT_TO_M, max_kg = ([0-9.]+) \* LB_TO_KG \}', source)
assert len(station_rows) == 36
for offset, variant in enumerate((0, 1, 2, 4)):
    expected = next(item for item in EXPECTED.values() if item["variant"] == variant)
    rows = station_rows[offset * 9:(offset + 1) * 9]
    assert tuple(row[0] for row in rows) == expected["names"]
    assert tuple(float(row[1]) for row in rows) == expected["arms"]
    assert tuple(float(row[2]) for row in rows) == expected["maxima"]

print("PASS: exact -700/-800/-900/-900ER overlay fields, Lua provenance and installer contracts")
