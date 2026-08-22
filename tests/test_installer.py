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
BASELINE = Path(
    "/Users/wahltho/dev/Zibo Mod/Original/Zibo Mod Original/"
    "B738X_XP12_4_05_35/plugins/xlua/scripts/B738.tablet/B738.tablet.lua"
)
INSTALLER = PACKAGE / "z_Install_LevelUp_NG_WB.py"
V020_ARCHIVE = PACKAGE / "remote_release/levelup-737ng-weight-balance-v0.2.0.zip"
V021_ARCHIVE = PACKAGE / "remote_release/levelup-737ng-weight-balance-v0.2.1.zip"
V022_ARCHIVE = PACKAGE / "remote_release/levelup-737ng-weight-balance-v0.2.2.zip"
FILES = (
    "B738.tablet_levelup_ng_wb_data.lua",
    "B738.tablet_levelup_ng_wb_core.lua",
    "B738.tablet_levelup_ng_wb_adapter.lua",
    "Add_levelup_ng_wb_dofile.txt",
    "Add_levelup_ng_wb_install_hook.txt",
    "Replace_external_payload_gate.txt",
    "Replace_internal_payload_gate.txt",
    "Replace_total_payload_scalar_gate.txt",
    "levelup-ng-wb-package-manifest.txt",
    "z_Install_LevelUp_NG_WB.py",
)

spec = importlib.util.spec_from_file_location("levelup_ng_installer", INSTALLER)
assert spec is not None and spec.loader is not None
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_contract_acf(path: Path, contract: dict[str, object]) -> None:
    fields = {**dict(contract["text"]), **dict(contract["number"])}
    roles = (1, 1, 0, 0, 0, 0, 0, 1, 1)
    for index, role in enumerate(roles):
        fields[f"acf/_fixed_role/{index}"] = role
    lines = ["I", "1200 Version"]
    for key in sorted(fields):
        lines.append(f"P {key} {fields[key]}")
    lines.append("P acf/_elev1_cratR 0.180000000")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def setup(line_ending: bytes = b"\n", performance_blocks: bool = False) -> tuple[tempfile.TemporaryDirectory, Path]:
    temporary = tempfile.TemporaryDirectory()
    aircraft = Path(temporary.name) / "LU 737NG Series"
    folder = aircraft / "plugins/xlua/scripts/B738.tablet"
    folder.mkdir(parents=True)
    for name in FILES:
        shutil.copy2(PACKAGE / name, folder / name)
    for contract in installer.ACF_CONTRACTS:
        write_contract_acf(aircraft / str(contract["name"]), contract)

    text = BASELINE.read_text(encoding="utf-8")
    if performance_blocks:
        perf_dofile = (
            "-- BEGIN UPSTREAM_TABLET_PERF_CALC DOFILE\n"
            'dofile("B738.tablet_perf_adapter.lua")\n'
            "-- END UPSTREAM_TABLET_PERF_CALC DOFILE"
        )
        perf_hook = (
            "-- BEGIN UPSTREAM_TABLET_PERF_CALC HOOKS\n"
            "B738_upstream_perf_adapter.install()\n"
            "-- END UPSTREAM_TABLET_PERF_CALC HOOKS"
        )
        text = text.replace("jit.off()", "jit.off()\n" + perf_dofile, 1)
        text = text.replace("function page_app_rating()", perf_hook + "\nfunction page_app_rating()", 1)
    (folder / "B738.tablet.lua").write_bytes(text.encode("utf-8").replace(b"\n", line_ending))
    return temporary, folder


def run(folder: Path, *args: str, expected: int = 0) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        ["python3", "z_Install_LevelUp_NG_WB.py", *args],
        cwd=folder, capture_output=True, text=True, check=False,
    )
    if completed.returncode != expected:
        raise AssertionError(
            f"installer returned {completed.returncode}, expected {expected}\n"
            f"stdout:\n{completed.stdout}\nstderr:\n{completed.stderr}"
        )
    return completed


def replace_acf_field(path: Path, key: str, value: str) -> None:
    prefix = f"P {key} "
    lines = path.read_text(encoding="utf-8").splitlines()
    matches = [index for index, line in enumerate(lines) if line.startswith(prefix)]
    assert len(matches) == 1, (key, matches)
    lines[matches[0]] = prefix + value
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def exercise_windows_luac_temporary_file_contract() -> None:
    payload = b"function flight_start()\nend\n"
    fake_path = Path(tempfile.mkdtemp()) / "windows-locked.lua"

    class WindowsLockedTemporary:
        def __init__(self) -> None:
            self.name = str(fake_path)
            self.stream = fake_path.open("wb")
            self.closed = False

        def __enter__(self) -> "WindowsLockedTemporary":
            return self

        def write(self, data: bytes) -> int:
            return self.stream.write(data)

        def flush(self) -> None:
            self.stream.flush()

        def __exit__(self, *_: object) -> None:
            self.stream.close()
            self.closed = True

    temporary: WindowsLockedTemporary | None = None

    def named_temporary_file(*, suffix: str, delete: bool) -> WindowsLockedTemporary:
        nonlocal temporary
        assert suffix == ".lua"
        assert delete is False
        temporary = WindowsLockedTemporary()
        return temporary

    def run_luac(arguments: list[str], **_: object) -> subprocess.CompletedProcess[str]:
        assert temporary is not None and temporary.closed
        assert arguments == ["C:/Lua/luac.exe", "-p", str(fake_path)]
        assert fake_path.read_bytes() == payload
        return subprocess.CompletedProcess(arguments, 0, "", "")

    original_which = installer.shutil.which
    original_named_temporary_file = installer.tempfile.NamedTemporaryFile
    original_run = installer.subprocess.run
    try:
        installer.shutil.which = lambda _: "C:/Lua/luac.exe"
        installer.tempfile.NamedTemporaryFile = named_temporary_file
        installer.subprocess.run = run_luac
        installer.validate_lua(payload)
        assert not fake_path.exists()
    finally:
        installer.shutil.which = original_which
        installer.tempfile.NamedTemporaryFile = original_named_temporary_file
        installer.subprocess.run = original_run
        if fake_path.exists():
            fake_path.unlink()
        fake_path.parent.rmdir()


def exercise(line_ending: bytes, performance_blocks: bool) -> None:
    temporary, folder = setup(line_ending, performance_blocks)
    try:
        target = folder / "B738.tablet.lua"
        original = target.read_bytes()
        acf_hashes = {path.name: digest(path) for path in folder.parents[3].glob("737_*NG.acf")}
        first = run(folder)
        assert "Installed v0.3.0" in first.stdout
        assert "Verified package payload: v0.3.0" in first.stdout
        assert "Verified levelup700-wb-v1" in first.stdout
        assert "Verified levelup800-wb-v2" in first.stdout
        assert "Verified levelup900-wb-v1" in first.stdout
        assert "Verified levelup900er-wb-v1" in first.stdout
        installed = target.read_bytes()
        assert (folder / "B738.tablet.lua.levelupngwb.backup").read_bytes() == original
        for marker in (
            b"BEGIN LEVELUP_NG_WB DOFILE", b"BEGIN LEVELUP_NG_WB INSTALL",
            b"BEGIN LEVELUP_NG_WB EXTERNAL_PAYLOAD_GATE",
            b"BEGIN LEVELUP_NG_WB INTERNAL_PAYLOAD_GATE",
            b"BEGIN LEVELUP_NG_WB TOTAL_PAYLOAD_SCALAR_GATE",
        ):
            assert installed.count(marker) == 1
        assert b"LEVELUP_700_WB" not in installed
        if line_ending == b"\r\n":
            assert installed.count(b"\n") == installed.count(b"\r\n")
        if performance_blocks:
            assert installed.count(b"BEGIN UPSTREAM_TABLET_PERF_CALC DOFILE") == 1
            assert installed.count(b"BEGIN UPSTREAM_TABLET_PERF_CALC HOOKS") == 1
        installed_text = installed.decode("utf-8").replace("\r\n", "\n")
        assert installed_text.count('dofile("B738.tablet_levelup_ng_wb_adapter.lua")') == 1
        assert installed_text.index("BEGIN LEVELUP_NG_WB INSTALL") > installed_text.index("function after_physics()")
        assert installed_text.rstrip().endswith("-- END LEVELUP_NG_WB INSTALL")
        assert "\n\telseif B738DR_ext_payload == 0 then\n\t\tsam_tick = 0\n" in installed_text
        assert "\n\tif B738DR_ext_payload == 0 and not B738_levelup_ng_wb_adapter.owns_payload() then\n" in installed_text
        assert "\n\t\t\tif not B738_levelup_ng_wb_adapter.owns_payload() then\n\t\t\t\tsimDR_payload_weight = full_crew_weight\n\t\t\tend\n" in installed_text

        installed_hash = digest(target)
        run(folder)
        assert digest(target) == installed_hash
        assert {path.name: digest(path) for path in folder.parents[3].glob("737_*NG.acf")} == acf_hashes

        run(folder, "--uninstall")
        assert target.read_bytes() == original
        run(folder, "--uninstall")
        assert target.read_bytes() == original
    finally:
        temporary.cleanup()


def exercise_non_wb_acf_change() -> None:
    temporary, folder = setup()
    try:
        acf = folder.parents[3] / "737_80NG.acf"
        replace_acf_field(acf, "acf/_elev1_cratR", "0.190000000")
        with acf.open("ab") as stream:
            stream.write(b"# unrelated FM tuning remains allowed\n")
        result = run(folder)
        assert "Verified levelup700-wb-v1" in result.stdout
        assert "Verified levelup800-wb-v2" in result.stdout
    finally:
        temporary.cleanup()


def exercise_station_role_tolerance() -> None:
    temporary, folder = setup()
    try:
        acf = folder.parents[3] / "737_9ENG.acf"
        replace_acf_field(acf, "acf/_fixed_role/7", "0")
        replace_acf_field(acf, "acf/_fixed_role/8", "0")
        result = run(folder)
        assert "Verified levelup900er-wb-v1" in result.stdout
    finally:
        temporary.cleanup()


def exercise_wrong_acf(name: str, version: str) -> None:
    temporary, folder = setup()
    try:
        target = folder / "B738.tablet.lua"
        original_hash = digest(target)
        replace_acf_field(folder.parents[3] / name, "acf/_fixed_ref/4,2", "47.000000000")
        result = run(folder, expected=2)
        assert f"violates {version}" in result.stderr
        assert "acf/_fixed_ref/4,2" in result.stderr
        assert digest(target) == original_hash
        assert not (folder / "B738.tablet.lua.levelupngwb.backup").exists()
    finally:
        temporary.cleanup()


def legacy_v014_source(original: str) -> str:
    old_dofile = (
        "-- BEGIN LEVELUP_700_WB DOFILE\n"
        'dofile("B738.tablet_levelup700_wb_adapter.lua")\n'
        "-- END LEVELUP_700_WB DOFILE"
    )
    old_install = (
        "-- BEGIN LEVELUP_700_WB INSTALL\n"
        "B738_levelup700_wb_adapter.install()\n"
        "-- END LEVELUP_700_WB INSTALL"
    )
    old_external = (
        "\t-- BEGIN LEVELUP_700_WB EXTERNAL_PAYLOAD_GATE\n"
        "\tif B738_levelup700_wb_adapter.owns_payload() then\n"
        "\t\tsam_tick = 0\n"
        "\telseif B738DR_ext_payload == 0 then\n"
        "\t\tsam_tick = 0\n"
        "\t-- END LEVELUP_700_WB EXTERNAL_PAYLOAD_GATE"
    )
    old_internal = (
        "\t-- BEGIN LEVELUP_700_WB INTERNAL_PAYLOAD_GATE\n"
        "\tif B738DR_ext_payload == 0 and not B738_levelup700_wb_adapter.owns_payload() then\n"
        "\t-- END LEVELUP_700_WB INTERNAL_PAYLOAD_GATE"
    )
    old_total = (
        "\t\t\t-- BEGIN LEVELUP_700_WB TOTAL_PAYLOAD_SCALAR_GATE\n"
        "\t\t\tif not B738_levelup700_wb_adapter.owns_payload() then\n"
        "\t\t\t\tsimDR_payload_weight = full_crew_weight\n"
        "\t\t\tend\n"
        "\t\t\t-- END LEVELUP_700_WB TOTAL_PAYLOAD_SCALAR_GATE"
    )
    text = original.replace("jit.off()", "jit.off()\n" + old_dofile, 1)
    text = text.rstrip() + "\n" + old_install + "\n"
    text = text.replace("\tif B738DR_ext_payload == 0 then\n\t\tsam_tick = 0", old_external, 1)
    text = text.replace("\tif B738DR_ext_payload == 0 then\n\t\tlocal add_weight = 0", old_internal + "\n\t\tlocal add_weight = 0", 1)
    text = text.replace("\t\t\t\tsimDR_payload_weight = full_crew_weight", old_total, 1)
    return text


def exercise_v014_upgrade() -> None:
    temporary, folder = setup()
    try:
        target = folder / "B738.tablet.lua"
        target.write_text(legacy_v014_source(target.read_text(encoding="utf-8")), encoding="utf-8", newline="\n")
        backup_marker = b"original v0.1.4 backup must remain untouched\n"
        (folder / "B738.tablet.lua.levelup700wb.backup").write_bytes(backup_marker)

        result = run(folder)
        assert "Installed v0.3.0" in result.stdout
        upgraded = target.read_text(encoding="utf-8")
        assert "LEVELUP_700_WB" not in upgraded
        assert upgraded.count('dofile("B738.tablet_levelup_ng_wb_adapter.lua")') == 1
        assert upgraded.index("BEGIN LEVELUP_NG_WB INSTALL") > upgraded.index("function after_physics()")
        assert upgraded.rstrip().endswith("-- END LEVELUP_NG_WB INSTALL")
        assert (folder / "B738.tablet.lua.levelup700wb.backup").read_bytes() == backup_marker
        assert not (folder / "B738.tablet.lua.levelupngwb.backup").exists()
    finally:
        temporary.cleanup()


def exercise_v020_upgrade() -> None:
    temporary, folder = setup()
    try:
        old_arms = {
            "acf/_fixed_ref/0,2": "36",
            "acf/_fixed_ref/2,2": "31",
            "acf/_fixed_ref/3,2": "44",
            "acf/_fixed_ref/4,2": "56",
            "acf/_fixed_ref/5,2": "68",
            "acf/_fixed_ref/6,2": "80",
            "acf/_tank_xyz/0,2": "63.950000763",
            "acf/_tank_xyz/1,2": "55.5",
            "acf/_tank_xyz/2,2": "63.950000763",
            "acf/_tank_xyz_full/0,2": "63.950000763",
            "acf/_tank_xyz_full/1,2": "55.5",
            "acf/_tank_xyz_full/2,2": "63.950000763",
        }
        new_arms = dict(installer.ACF_CONTRACTS[1]["number"])
        acf = folder.parents[3] / "737_80NG.acf"
        for key, value in old_arms.items():
            replace_acf_field(acf, key, value)

        with zipfile.ZipFile(V020_ARCHIVE) as archive:
            archive.extractall(folder)
        old_result = run(folder)
        assert "Installed v0.2.0" in old_result.stdout
        target = folder / "B738.tablet.lua"
        installed_v020 = target.read_bytes()
        backup_v020 = (folder / "B738.tablet.lua.levelupngwb.backup").read_bytes()

        for key in old_arms:
            replace_acf_field(acf, key, str(new_arms[key]))
        for name in FILES:
            shutil.copy2(PACKAGE / name, folder / name)

        result = run(folder)
        assert "Verified package payload: v0.3.0" in result.stdout
        assert "Verified levelup800-wb-v2" in result.stdout
        assert "already in the requested state" in result.stdout
        assert target.read_bytes() == installed_v020
        assert (folder / "B738.tablet.lua.levelupngwb.backup").read_bytes() == backup_v020
        assert digest(folder / "B738.tablet_levelup_ng_wb_data.lua") == digest(
            PACKAGE / "B738.tablet_levelup_ng_wb_data.lua"
        )
    finally:
        temporary.cleanup()


def exercise_performance_installed_second() -> None:
    temporary, folder = setup()
    try:
        target = folder / "B738.tablet.lua"
        original = target.read_text(encoding="utf-8")
        run(folder)
        text = target.read_text(encoding="utf-8")
        perf_dofile = (
            "-- BEGIN UPSTREAM_TABLET_PERF_CALC DOFILE\n"
            'dofile("B738.tablet_perf_adapter.lua")\n'
            "-- END UPSTREAM_TABLET_PERF_CALC DOFILE"
        )
        perf_hook = (
            "-- BEGIN UPSTREAM_TABLET_PERF_CALC HOOKS\n"
            "B738_upstream_perf_adapter.install()\n"
            "-- END UPSTREAM_TABLET_PERF_CALC HOOKS"
        )
        text = text.replace("jit.off()", "jit.off()\n" + perf_dofile, 1)
        text = text.replace("function page_app_rating()", perf_hook + "\nfunction page_app_rating()", 1)
        target.write_text(text, encoding="utf-8", newline="\n")
        coexist_hash = digest(target)
        run(folder)
        assert digest(target) == coexist_hash
        run(folder, "--uninstall")
        remaining = target.read_text(encoding="utf-8")
        expected = original.replace("jit.off()", "jit.off()\n" + perf_dofile, 1)
        expected = expected.replace("function page_app_rating()", perf_hook + "\nfunction page_app_rating()", 1)
        assert remaining == expected
    finally:
        temporary.cleanup()


def exercise_v021_upgrade() -> None:
    temporary, folder = setup()
    try:
        with zipfile.ZipFile(V021_ARCHIVE) as archive:
            archive.extractall(folder)
        old_result = run(folder)
        assert "Installed v0.2.1" in old_result.stdout
        target = folder / "B738.tablet.lua"
        installed_v021 = target.read_bytes()
        backup_v021 = (folder / "B738.tablet.lua.levelupngwb.backup").read_bytes()

        for name in FILES:
            shutil.copy2(PACKAGE / name, folder / name)

        result = run(folder)
        assert "Verified package payload: v0.3.0" in result.stdout
        assert "Verified levelup700-wb-v1" in result.stdout
        assert "Verified levelup800-wb-v2" in result.stdout
        assert "already in the requested state" in result.stdout
        assert target.read_bytes() == installed_v021
        assert (folder / "B738.tablet.lua.levelupngwb.backup").read_bytes() == backup_v021
        assert digest(folder / "B738.tablet_levelup_ng_wb_data.lua") == digest(
            PACKAGE / "B738.tablet_levelup_ng_wb_data.lua"
        )
    finally:
        temporary.cleanup()


def exercise_v022_upgrade() -> None:
    temporary, folder = setup()
    try:
        with zipfile.ZipFile(V022_ARCHIVE) as archive:
            archive.extractall(folder)
        old_result = run(folder)
        assert "Installed v0.2.2" in old_result.stdout
        target = folder / "B738.tablet.lua"
        installed_v022 = target.read_bytes()
        backup_v022 = (folder / "B738.tablet.lua.levelupngwb.backup").read_bytes()

        for name in FILES:
            shutil.copy2(PACKAGE / name, folder / name)

        result = run(folder)
        assert "Verified package payload: v0.3.0" in result.stdout
        assert "Verified levelup700-wb-v1" in result.stdout
        assert "Verified levelup800-wb-v2" in result.stdout
        assert "already in the requested state" in result.stdout
        assert target.read_bytes() == installed_v022
        assert (folder / "B738.tablet.lua.levelupngwb.backup").read_bytes() == backup_v022
    finally:
        temporary.cleanup()


assert BASELINE.is_file(), BASELINE
exercise_windows_luac_temporary_file_contract()
exercise(b"\n", False)
exercise(b"\r\n", False)
exercise(b"\n", True)
exercise_v014_upgrade()
exercise_v020_upgrade()
exercise_v021_upgrade()
exercise_v022_upgrade()
exercise_performance_installed_second()
exercise_non_wb_acf_change()
exercise_station_role_tolerance()
exercise_wrong_acf("737_70NG.acf", "levelup700-wb-v1")
exercise_wrong_acf("737_80NG.acf", "levelup800-wb-v2")
exercise_wrong_acf("737_90NG.acf", "levelup900-wb-v1")
exercise_wrong_acf("737_9ENG.acf", "levelup900er-wb-v1")
print("PASS: Windows luac handoff, .35 anchors, legacy migration, four ACF contracts, LF/CRLF, idempotence, uninstall and coexistence")
