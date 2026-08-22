#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path


REPO = Path(os.environ.get("ZIBO_MOD_REPOSITORY", "/Users/wahltho/Documents/Projects/Zibo Mod"))
OVERLAY = REPO / "overlay/LU 737NG Series"
MANIFEST = REPO / "overlay/LU 737NG Series manifest.json"

EXPECTED = {
    "737_70NG.acf": {
        "sha256": "a5d2cdd9e7dec57ec42d22a0937f3c08ee56e1adbd7334b87bbfd38fb9a811f2",
        "version": "XP12 2.S1.51 (20260819 2130 SAO)", "object_count": 42,
        "view": (-1.627290078, 2.344606488, 9.095732005, -2.988779),
        "cg_mac": (49.029998779, 47.189998627, 50.939998627, 14.992128372),
        "arms": (29, 69, 22, 34, 46, 58, 70, 15, 80),
    },
    "737_80NG.acf": {
        "sha256": "e3bb89129fc2400581fec27e8b2c2947a99b06e0aefc24cb3d40a833fc0f5c1c",
        "version": "XP12 FM V2.S1.51 (20260819 1920 SAO)", "object_count": 41,
        "view": (-1.626870131, 2.342401763, 9.099929059, -2.988779),
        "cg_mac": (59.889999390, 57.869998932, 61.840000153, 14.992127419),
        "arms": (37, 85, 33.5, 46.5, 58.5, 70.5, 82.5, 15, 99),
    },
    "737_90NG.acf": {
        "sha256": "2ac3fa0c5cc6c5002675712989f3a0ef4c9fdb9cf7c62e54c7819129a295e5cc",
        "version": "XP12 V2.S1.51 (20260821 1900 SAO)", "object_count": 42,
        "view": (-1.627290078, 2.344606488, 9.095732005, -2.988779),
        "cg_mac": (64.650001526, 63.380001068, 67.129997253, 14.993530273),
        "arms": (43, 97, 35, 48.5, 66, 79, 92, 15, 108),
    },
    "737_9ENG.acf": {
        "sha256": "06f5357b46ad6fa242464e11c64b988ec4a31cb5da0c7aaaa9d37af2d61c383e",
        "version": "XP12 FM V2.S1.51 SFP (20260821 2310 SAO)", "object_count": 42,
        "view": (-1.626870131, 2.342401763, 9.099929059, -2.988779),
        "cg_mac": (65.389999390, 64.879997253, 67.879997253, 14.993530273),
        "arms": (43, 97, 35, 48.5, 66, 79, 92, 15, 108),
        "roles": (1, 1, 0, 0, 0, 0, 0, 1, 1),
        "flaps": (0.075000003, 0.730000019, -0.699999988),
    },
}


def properties(path: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("P "):
            _, key, value = line.split(" ", 2)
            assert key not in result, key
            result[key] = value
    return result


manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
entries = {
    entry["target"]: entry
    for section in ("source_only_entries", "entries")
    for entry in manifest.get(section, [])
    if entry.get("target") in EXPECTED
}
assert set(entries) == set(EXPECTED)

for filename, expected in EXPECTED.items():
    path = OVERLAY / filename
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    assert digest == expected["sha256"]
    assert entries[filename]["source_sha256"] == digest
    fields = properties(path)
    assert fields["acf/_version"] == expected["version"]
    assert int(fields["_obja/count"]) == expected["object_count"]
    objects = [value for key, value in fields.items() if key.startswith("_obja/")]
    assert "jdcopilot.obj" not in objects
    assert "particles/particles.obj" in objects
    assert "wxr_collins_knobs.obj" in objects
    assert "wxr_collins_panel.obj" in objects
    view = tuple(float(fields[f"acf/_pe_xyz/{index}"]) for index in range(3)) + (float(fields["acf/_ang_offset/0,1"]),)
    assert all(math.isclose(actual, wanted, abs_tol=1e-9) for actual, wanted in zip(view, expected["view"]))
    cg_mac = tuple(float(fields[key]) for key in ("acf/_cgZ", "acf/_cgZ_fwd", "acf/_cgZ_aft", "acf/_average_mac_acf"))
    assert all(math.isclose(actual, wanted, abs_tol=1e-9) for actual, wanted in zip(cg_mac, expected["cg_mac"]))
    assert int(fields["acf/_fixed_max/count"]) == 9
    arms = tuple(float(fields[f"acf/_fixed_ref/{index},2"]) for index in range(9))
    assert arms == expected["arms"]
    if "roles" in expected:
        assert tuple(int(float(fields[f"acf/_fixed_role/{index}"])) for index in range(9)) == expected["roles"]
    if "flaps" in expected:
        assert tuple(float(fields[key]) for key in ("acf/_flap1_cd", "acf/_flap1_cl", "acf/_flap1_cm")) == expected["flaps"]

print("PASS: reconciled V2.S1.51 700/800/900/900ER W&B, flightmodel, private objects and cockpit views")
