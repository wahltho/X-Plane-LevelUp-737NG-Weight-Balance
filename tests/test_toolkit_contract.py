#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path


REPOSITORY = Path(__file__).resolve().parents[1]
MODULE_MANIFEST = REPOSITORY / "toolkit/weight-and-balance-module.json"
ACF_CONTRACT = REPOSITORY / "contracts/levelup-ng-wb-acf-v0.3.3.json"
TABLET_LOADER_PATCH = REPOSITORY / "patches/B738.tablet.loader.json"
TABLET_PATCH = REPOSITORY / "patches/B738.tablet.lua.json"
FMS_PATCH = REPOSITORY / "patches/B738.a_fms.lua.json"
INSTALLER = REPOSITORY / "z_Install_LevelUp_NG_WB.py"
BASELINE = Path(
    "/Users/wahltho/dev/Zibo Mod/Original/Zibo Mod Original/"
    "B738X_XP12_4_05_35/plugins/xlua/scripts/B738.tablet/B738.tablet.lua"
)
FMS_BASELINE = Path(
    "/Users/wahltho/dev/Zibo Mod/Original/Zibo Mod Original/"
    "B738X_XP12_4_05_35/plugins/xlua/scripts/B738.a_fms/B738.a_fms.lua"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def apply_exact_replacements(source: str, payload: dict[str, object]) -> str:
    lines = source.replace("\r\n", "\n").replace("\r", "\n").splitlines()
    for replacement in payload["replacements"]:
        old = replacement["oldLines"]
        new = replacement["newLines"]
        matches = [
            index
            for index in range(len(lines) - len(old) + 1)
            if lines[index:index + len(old)] == old
        ]
        assert len(matches) == 1, (replacement["name"], matches)
        index = matches[0]
        lines[index:index + len(old)] = new
    return "\n".join(lines) + "\n"


def apply_marked_insertion(source: str, payload: dict[str, object]) -> str:
    lines = source.replace("\r\n", "\n").replace("\r", "\n").splitlines()
    block = [payload["beginMarker"], *payload["contentLines"], payload["endMarker"]]
    block_matches = [
        index for index in range(len(lines) - len(block) + 1)
        if lines[index:index + len(block)] == block
    ]
    if len(block_matches) == 1:
        return "\n".join(lines) + "\n"
    assert not block_matches
    assert payload["beginMarker"] not in lines
    assert payload["endMarker"] not in lines
    anchor = payload["anchorLines"]
    matches = [
        index for index in range(len(lines) - len(anchor) + 1)
        if lines[index:index + len(anchor)] == anchor
    ]
    assert len(matches) == 1, matches
    index = matches[0] + len(anchor)
    lines[index:index] = block
    return "\n".join(lines) + "\n"


manifest = json.loads(MODULE_MANIFEST.read_text(encoding="utf-8"))
assert manifest["schemaVersion"] == 1
assert manifest["manifestType"] == "levelup-compatibility-module-source"
assert manifest["moduleId"] == "weight-and-balance"
assert manifest["moduleVersion"] == "0.3.3"
assert manifest["toolkitIntegration"]["directCatalogEntry"] is False
assert [entry["variantId"] for entry in manifest["supportedVariants"]] == [2, 0, 1, 4]

payloads = {entry["path"]: entry for entry in manifest["payloads"]}
for relative_path, metadata in payloads.items():
    path = REPOSITORY / relative_path
    assert path.is_file(), relative_path
    assert path.stat().st_size == metadata["size"], relative_path
    assert sha256(path) == metadata["sha256"], relative_path

copy_targets = [target for target in manifest["targets"] if target["operation"] == "copy-file-v1"]
assert len(copy_targets) == 3
for target in copy_targets:
    assert target["resultSha256"] == payloads[target["payload"]]["sha256"]

loader_patch = json.loads(TABLET_LOADER_PATCH.read_text(encoding="utf-8"))
assert loader_patch["format"] == "insert-marked-block-v1"
patch = json.loads(TABLET_PATCH.read_text(encoding="utf-8"))
assert patch["format"] == "exact-text-replacements-v1"
assert len(patch["replacements"]) == 4
patched = apply_exact_replacements(
    apply_marked_insertion(BASELINE.read_text(encoding="utf-8"), loader_patch),
    patch,
)
assert patched.count("BEGIN LEVELUP_NG_WB") == 5
assert patched.count('dofile("B738.tablet_levelup_ng_wb_adapter.lua")') == 1
assert patched.index("BEGIN LEVELUP_NG_WB INSTALL") > patched.index("function after_physics()")

other_loader = (
    "-- BEGIN UPSTREAM_TABLET_PERF_CALC DOFILE\n"
    'dofile("B738.tablet_perf_adapter.lua")\n'
    "-- END UPSTREAM_TABLET_PERF_CALC DOFILE"
)
with_other_loader = BASELINE.read_text(encoding="utf-8").replace(
    "jit.off()", "jit.off()\n" + other_loader, 1
)
combined = apply_exact_replacements(
    apply_marked_insertion(with_other_loader, loader_patch),
    patch,
)
assert combined.count("BEGIN UPSTREAM_TABLET_PERF_CALC DOFILE") == 1
assert combined.count("BEGIN LEVELUP_NG_WB DOFILE") == 1

fms_patch = json.loads(FMS_PATCH.read_text(encoding="utf-8"))
assert fms_patch["format"] == "exact-text-replacements-v1"
assert len(fms_patch["replacements"]) == 2
fms_patched = apply_exact_replacements(FMS_BASELINE.read_text(encoding="utf-8"), fms_patch)
assert fms_patched.count("BEGIN LEVELUP_NG_WB FMS_EMPTY_WEIGHT") == 1
assert fms_patched.count("BEGIN LEVELUP_NG_WB FMS_ZFW_OWNER") == 1
assert "for station_index = 0, 8 do" in fms_patched
assert "zfw_real = simDR_levelup_ng_acf_m_empty + station_payload_weight" in fms_patched
assert "B738DR_b737_variant == 4" in fms_patched

spec = importlib.util.spec_from_file_location("levelup_ng_wb_installer", INSTALLER)
assert spec is not None and spec.loader is not None
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)
contract = json.loads(ACF_CONTRACT.read_text(encoding="utf-8"))
assert contract["schemaVersion"] == 1
assert contract["packageVersion"] == "0.3.3"
json_contracts = {entry["name"]: entry for entry in contract["variants"]}
installer_contracts = {entry["name"]: entry for entry in installer.ACF_CONTRACTS}
assert set(json_contracts) == set(installer_contracts)
for name, expected in installer_contracts.items():
    actual = json_contracts[name]
    assert actual["version"] == expected["version"]
    assert actual["text"] == expected["text"]
    assert actual["number"] == expected["number"]

print("PASS: Toolkit module payloads, structural Tablet/FMS patches and semantic ACF contract")
