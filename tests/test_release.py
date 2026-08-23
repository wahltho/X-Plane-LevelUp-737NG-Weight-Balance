#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path


PACKAGE = Path(__file__).resolve().parents[1]
ARCHIVE = PACKAGE / "dist/LevelUp-737NG-Weight-Balance-v0.3.1.zip"
CHECKSUM = ARCHIVE.with_suffix(ARCHIVE.suffix + ".sha256")
BASELINE = Path(
    "/Users/wahltho/dev/Zibo Mod/Original/Zibo Mod Original/"
    "B738X_XP12_4_05_35/plugins/xlua/scripts/B738.tablet/B738.tablet.lua"
)
EXPECTED = {
    "B738.tablet_levelup_ng_wb_data.lua",
    "B738.tablet_levelup_ng_wb_core.lua",
    "B738.tablet_levelup_ng_wb_adapter.lua",
    "Add_levelup_ng_wb_dofile.txt",
    "Add_levelup_ng_wb_install_hook.txt",
    "Replace_external_payload_gate.txt",
    "Replace_internal_payload_gate.txt",
    "Replace_total_payload_scalar_gate.txt",
    "z_Install_LevelUp_NG_WB.py",
    "levelup-ng-wb-package-manifest.txt",
    "README.md",
    "INSTALLATION.md",
    "SOURCE.md",
    "OWNER_CLOSURE.md",
    "RUNTIME_TEST_PLAN.md",
    "ACF_RECONCILE_2026_08_22.md",
    "ACF_RECONCILE_2026_08_23.md",
    "CHANGELOG.md",
    "LICENSE",
    "patches/B738.tablet.lua.json",
    "contracts/levelup-ng-wb-acf-v0.3.1.json",
    "toolkit/weight-and-balance-module.json",
}

spec = importlib.util.spec_from_file_location("levelup_ng_installer", PACKAGE / "z_Install_LevelUp_NG_WB.py")
assert spec is not None and spec.loader is not None
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)


def write_contract_acf(path: Path, contract: dict[str, object]) -> None:
    fields = {**dict(contract["text"]), **dict(contract["number"])}
    roles = (1, 1, 0, 0, 0, 0, 0, 1, 1)
    for index, role in enumerate(roles):
        fields[f"acf/_fixed_role/{index}"] = role
    lines = ["I", "1200 Version"]
    lines.extend(f"P {key} {fields[key]}" for key in sorted(fields))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


assert ARCHIVE.is_file(), ARCHIVE
actual_hash = hashlib.sha256(ARCHIVE.read_bytes()).hexdigest()
expected_hash, expected_name = CHECKSUM.read_text(encoding="ascii").split()
assert expected_name == ARCHIVE.name
assert actual_hash == expected_hash

with zipfile.ZipFile(ARCHIVE) as archive:
    assert set(archive.namelist()) == EXPECTED
    assert all(not name.startswith(("/", "../")) and "/../" not in name for name in archive.namelist())
    for name in EXPECTED:
        assert archive.read(name) == (PACKAGE / name).read_bytes(), name

    with tempfile.TemporaryDirectory() as temporary:
        aircraft = Path(temporary) / "LU 737NG Series"
        tablet = aircraft / "plugins/xlua/scripts/B738.tablet"
        tablet.mkdir(parents=True)
        archive.extractall(tablet)
        shutil.copy2(BASELINE, tablet / "B738.tablet.lua")
        for contract in installer.ACF_CONTRACTS:
            write_contract_acf(aircraft / str(contract["name"]), contract)
        completed = subprocess.run(
            ["python3", "z_Install_LevelUp_NG_WB.py"], cwd=tablet,
            capture_output=True, text=True, check=False,
        )
        assert completed.returncode == 0, completed.stdout + completed.stderr
        assert "Verified levelup700-wb-v1" in completed.stdout
        assert "Verified levelup800-wb-v2" in completed.stdout
        assert "Verified levelup900-wb-v2" in completed.stdout
        assert "Verified levelup900er-wb-v2" in completed.stdout
        installed = (tablet / "B738.tablet.lua").read_bytes()
        assert installed.count(b"BEGIN LEVELUP_NG_WB") == 5
        assert b"BEGIN LEVELUP_700_WB" not in installed

print("PASS: v0.3.1 entries, checksum, source identity and fresh four-contract installation")
