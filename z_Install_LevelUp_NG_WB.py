#!/usr/bin/env python3
"""Install or remove the LevelUp 737NG Tablet and FMS W&B hooks."""

from __future__ import annotations

import argparse
import hashlib
import math
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


TABLET_LUA_FILE = Path("B738.tablet.lua")
TABLET_BACKUP_FILE = Path("B738.tablet.lua.levelupngwb.backup")
LEGACY_BACKUP_FILE = Path("B738.tablet.lua.levelup700wb.backup")
FMS_LUA_FILE = Path("../B738.a_fms/B738.a_fms.lua")
FMS_BACKUP_FILE = Path("../B738.a_fms/B738.a_fms.lua.levelupngwb.backup")
MANIFEST_FILE = Path("levelup-ng-wb-package-manifest.txt")
PACKAGE_ID = "levelup-737ng-weight-balance-test-balloon"


def make_acf_contract(
    version: str,
    name: str,
    empty_mass: float,
    cg_z: float,
    cg_fwd: float,
    cg_aft: float,
    mac: float,
    max_mass: float,
    fuel_mass: float,
    station_names: tuple[str, ...],
    station_arms: tuple[float, ...],
    station_maxima: tuple[float, ...],
    tank_empty_arms: tuple[float, ...],
    tank_full_arms: tuple[float, ...],
    tank_names: tuple[str, str, str] = ("Left Main", "Center Wing", "Right Main"),
) -> dict[str, object]:
    text_fields = {
        "acf/_tank_name/0": tank_names[0],
        "acf/_tank_name/1": tank_names[1],
        "acf/_tank_name/2": tank_names[2],
    }
    number_fields = {
        "acf/_m_empty": empty_mass,
        "acf/_cgZ": cg_z,
        "acf/_cgZ_fwd": cg_fwd,
        "acf/_cgZ_aft": cg_aft,
        "acf/_average_mac_acf": mac,
        "acf/_m_max": max_mass,
        "acf/_m_fuel_max_tot": fuel_mass,
        "acf/_fixed_max/count": 9,
        "acf/_fixed_name/count": 9,
        "acf/_fixed_ref/i_count": 9,
        "acf/_fixed_ref/j_count": 3,
        "acf/_fixed_role/count": 9,
        "acf/_tank_name/count": 9,
        "acf/_tank_rat/count": 9,
        "acf/_tank_xyz/i_count": 9,
        "acf/_tank_xyz/j_count": 3,
        "acf/_tank_xyz_full/i_count": 9,
        "acf/_tank_xyz_full/j_count": 3,
    }
    tank_ratios = (0.187000006, 0.625999987, 0.187000006, 0, 0, 0, 0, 0, 0)
    all_tank_empty_arms = (*tank_empty_arms, 0, 0, 0, 0, 0, 0)
    all_tank_full_arms = (*tank_full_arms, 0, 0, 0, 0, 0, 0)
    for index in range(9):
        text_fields[f"acf/_fixed_name/{index}"] = station_names[index]
        number_fields[f"acf/_fixed_ref/{index},2"] = station_arms[index]
        number_fields[f"acf/_fixed_max/{index}"] = station_maxima[index]
        number_fields[f"acf/_tank_rat/{index}"] = tank_ratios[index]
        number_fields[f"acf/_tank_xyz/{index},2"] = all_tank_empty_arms[index]
        number_fields[f"acf/_tank_xyz_full/{index},2"] = all_tank_full_arms[index]
    return {"version": version, "name": name, "text": text_fields, "number": number_fields}


ACF_CONTRACTS = (
    make_acf_contract(
        "levelup600-wb-v2", "737_60NG.acf",
        80199.78, 45.979999542, 44.229999542, 47.700000763, 14.878139496,
        124499.8, 46062.01,
        ("Cargo1", "Cargo2", "Zone 1", "Zone 2", "Zone 3", "Zone 4", "Zone 5", "Galley F", "Galley A"),
        (24, 62, 20, 32, 46, 58, 70, 15, 76.199996948),
        (4200, 6900, 8000, 8000, 8000, 8000, 8000, 3000, 3000),
        (49, 43, 49),
        (49, 43, 49),
        ("Left Main", "Center Wing", "Right Wing"),
    ),
    make_acf_contract(
        "levelup700-wb-v1", "737_70NG.acf",
        82999.61, 49.029998779, 47.189998627, 50.939998627, 14.992128372,
        154499.9, 46062.008,
        ("Cargo1", "Cargo2", "Zone 1", "Zone 2", "Zone 3", "Zone 4", "Zone 5", "Galley F", "Galley R"),
        (29, 69, 22, 34, 46, 58, 70, 15, 80),
        (4200, 6900, 8000, 8000, 8000, 8000, 8000, 3000, 3000),
        (52.650001526, 46, 52.650001526),
        (52.650001526, 46, 52.650001526),
    ),
    make_acf_contract(
        "levelup800-wb-v2", "737_80NG.acf",
        91514.04, 59.889999390, 57.869998932, 61.840000153, 14.992127419,
        174700.0, 46062.01,
        ("Cargo1", "Cargo2", "Zone 1", "Zone 2", "Zone 3", "Zone 4", "Zone 5", "Galley F", "Galley A"),
        (37, 85, 33.5, 46.5, 58.5, 70.5, 82.5, 15, 99),
        (7848, 10690, 10000, 10000, 10000, 10000, 10000, 3000, 3000),
        (64, 56.5, 64),
        (64, 56.5, 64),
    ),
    make_acf_contract(
        "levelup900-wb-v2", "737_90NG.acf",
        94580.0, 64.650001526, 63.380001068, 67.129997253, 14.993530273,
        174700.0, 46062.008,
        ("Cargo1", "Cargo2", "Zone 1", "Zone 2", "Zone 3", "Zone 4", "Zone 5", "Galley F", "Galley A"),
        (45, 89, 34, 47.5, 65, 77, 91, 15, 108),
        (7848, 10690, 10000, 10000, 10000, 10000, 10000, 3000, 3000),
        (69, 62, 69),
        (69, 62, 69),
    ),
    make_acf_contract(
        "levelup900er-wb-v2", "737_9ENG.acf",
        98495.0, 65.389999390, 64.879997253, 67.879997253, 14.993530273,
        187699.31, 52512.31,
        ("Cargo1", "Cargo2", "Zone 1", "Zone 2", "Zone 3", "Zone 4", "Zone 5", "Galley F", "Galley A"),
        (45, 89, 34, 47.5, 65, 77, 91, 15, 108),
        (7848, 10500, 10000, 10000, 10000, 10000, 10000, 3000, 3000),
        (69, 62, 69),
        (69, 62, 69),
    ),
)

PAYLOADS = (
    Path("B738.tablet_levelup_ng_wb_data.lua"),
    Path("B738.tablet_levelup_ng_wb_core.lua"),
    Path("B738.tablet_levelup_ng_wb_adapter.lua"),
)
FRAGMENTS = (
    Path("Add_levelup_ng_wb_dofile.txt"),
    Path("Add_levelup_ng_wb_install_hook.txt"),
    Path("Replace_external_payload_gate.txt"),
    Path("Replace_internal_payload_gate.txt"),
    Path("Replace_total_payload_scalar_gate.txt"),
    Path("Add_levelup_ng_wb_fms_empty_weight.txt"),
    Path("Replace_levelup_ng_wb_fms_zfw_owner.txt"),
)

DOFILE_BEGIN = "-- BEGIN LEVELUP_NG_WB DOFILE"
DOFILE_END = "-- END LEVELUP_NG_WB DOFILE"
INSTALL_BEGIN = "-- BEGIN LEVELUP_NG_WB INSTALL"
INSTALL_END = "-- END LEVELUP_NG_WB INSTALL"
EXTERNAL_BEGIN = "-- BEGIN LEVELUP_NG_WB EXTERNAL_PAYLOAD_GATE"
EXTERNAL_END = "-- END LEVELUP_NG_WB EXTERNAL_PAYLOAD_GATE"
INTERNAL_BEGIN = "-- BEGIN LEVELUP_NG_WB INTERNAL_PAYLOAD_GATE"
INTERNAL_END = "-- END LEVELUP_NG_WB INTERNAL_PAYLOAD_GATE"
TOTAL_BEGIN = "-- BEGIN LEVELUP_NG_WB TOTAL_PAYLOAD_SCALAR_GATE"
TOTAL_END = "-- END LEVELUP_NG_WB TOTAL_PAYLOAD_SCALAR_GATE"
FMS_EMPTY_BEGIN = "-- BEGIN LEVELUP_NG_WB FMS_EMPTY_WEIGHT"
FMS_EMPTY_END = "-- END LEVELUP_NG_WB FMS_EMPTY_WEIGHT"
FMS_ZFW_BEGIN = "-- BEGIN LEVELUP_NG_WB FMS_ZFW_OWNER"
FMS_ZFW_END = "-- END LEVELUP_NG_WB FMS_ZFW_OWNER"

FMS_EMPTY_STOCK = [
    'simDR_payload_stations\t\t= find_dataref("sim/flightmodel/weight/m_stations")',
]
FMS_ZFW_STOCK = [
    "\tzfw_real = B738DR_oew_kg + simDR_payload_weight - full_crew_weight",
]

LEGACY_MARKERS = (
    ("-- BEGIN LEVELUP_700_WB DOFILE", "-- END LEVELUP_700_WB DOFILE", DOFILE_BEGIN, DOFILE_END),
    ("-- BEGIN LEVELUP_700_WB INSTALL", "-- END LEVELUP_700_WB INSTALL", INSTALL_BEGIN, INSTALL_END),
    ("-- BEGIN LEVELUP_700_WB EXTERNAL_PAYLOAD_GATE", "-- END LEVELUP_700_WB EXTERNAL_PAYLOAD_GATE", EXTERNAL_BEGIN, EXTERNAL_END),
    ("-- BEGIN LEVELUP_700_WB INTERNAL_PAYLOAD_GATE", "-- END LEVELUP_700_WB INTERNAL_PAYLOAD_GATE", INTERNAL_BEGIN, INTERNAL_END),
    ("-- BEGIN LEVELUP_700_WB TOTAL_PAYLOAD_SCALAR_GATE", "-- END LEVELUP_700_WB TOTAL_PAYLOAD_SCALAR_GATE", TOTAL_BEGIN, TOTAL_END),
)


def detect_eol(data: bytes) -> str:
    crlf = data.count(b"\r\n")
    lf_only = data.count(b"\n") - crlf
    return "\r\n" if crlf > lf_only else "\n"


def split_lines(data: bytes) -> tuple[list[str], str, bool]:
    eol = detect_eol(data)
    final_eol = data.endswith((b"\n", b"\r"))
    text = data.decode("utf-8", errors="strict")
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    if final_eol and lines and lines[-1] == "":
        lines.pop()
    return lines, eol, final_eol


def encode_lines(lines: list[str], eol: str, final_eol: bool) -> bytes:
    text = eol.join(lines)
    if final_eol:
        text += eol
    return text.encode("utf-8")


def read_fragment(path: Path) -> list[str]:
    lines, _, _ = split_lines(path.read_bytes())
    while lines and lines[-1] == "":
        lines.pop()
    return lines


def require(path: Path) -> None:
    if not path.is_file():
        print(f"ERROR: {path} not found.", file=sys.stderr)
        raise SystemExit(2)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_package() -> str:
    require(MANIFEST_FILE)
    package_id = ""
    version = ""
    payloads: dict[str, tuple[int, str]] = {}
    for line in MANIFEST_FILE.read_text(encoding="utf-8").splitlines():
        fields = line.split("|")
        if len(fields) == 3 and fields[:2] == ["package", "id"]:
            package_id = fields[2]
        elif len(fields) == 3 and fields[:2] == ["package", "version"]:
            version = fields[2]
        elif len(fields) == 7 and fields[0] == "payload" and fields[3] == "size" and fields[5] == "sha256":
            payloads[fields[2]] = (int(fields[4]), fields[6])

    if package_id != PACKAGE_ID or not version:
        print(f"ERROR: invalid or incompatible {MANIFEST_FILE}.", file=sys.stderr)
        raise SystemExit(2)

    required = (*PAYLOADS, *FRAGMENTS, Path("z_Install_LevelUp_NG_WB.py"))
    for path in required:
        require(path)
        expected = payloads.get(path.name)
        if expected is None or len(path.read_bytes()) != expected[0] or sha256(path) != expected[1]:
            print(f"ERROR: {path.name} does not match package {version}.", file=sys.stderr)
            raise SystemExit(2)
    print(f"Verified package payload: {version}")
    return version


def default_aircraft_root() -> Path:
    try:
        return Path.cwd().parents[3]
    except IndexError:
        return Path.cwd()


def read_acf_fields(path: Path) -> dict[str, str]:
    fields: dict[str, str] = {}
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as error:
        print(f"ERROR: cannot read {path}: {error}", file=sys.stderr)
        raise SystemExit(2)
    for line in lines:
        if not line.startswith("P acf/"):
            continue
        key, separator, value = line[2:].partition(" ")
        if not separator or key in fields:
            print(f"ERROR: malformed or duplicate ACF field {key!r} in {path}.", file=sys.stderr)
            raise SystemExit(2)
        fields[key] = value
    return fields


def acf_contract_error(path: Path, version: str, key: str, actual: str | None, expected: object) -> None:
    print(
        f"ERROR: {path} violates {version}: {key} is {actual!r}; expected {expected!r}.",
        file=sys.stderr,
    )
    raise SystemExit(2)


def verify_acf(path: Path, contract: dict[str, object]) -> None:
    require(path)
    fields = read_acf_fields(path)
    version = str(contract["version"])
    for key, expected in dict(contract["text"]).items():
        actual = fields.get(key)
        if actual != expected:
            acf_contract_error(path, version, key, actual, expected)
    for key, expected in dict(contract["number"]).items():
        serialized = fields.get(key)
        try:
            actual = float(serialized) if serialized is not None else None
        except ValueError:
            actual = None
        if actual is None or not math.isclose(actual, float(expected), rel_tol=1e-9, abs_tol=1e-6):
            acf_contract_error(path, version, key, serialized, expected)
    print(f"Verified {version}: {path} (unrelated ACF changes allowed)")


def matches(lines: list[str], needle: str) -> list[int]:
    return [index for index, line in enumerate(lines) if needle in line]


def find_block(lines: list[str], begin: str, end: str) -> tuple[int, int] | None:
    starts = matches(lines, begin)
    ends = matches(lines, end)
    if not starts and not ends:
        return None
    if len(starts) != 1 or len(ends) != 1 or ends[0] < starts[0]:
        print(f"ERROR: malformed or duplicate marked block {begin!r}.", file=sys.stderr)
        raise SystemExit(1)
    return starts[0], ends[0] + 1


def active_anchor(lines: list[str], needle: str) -> int:
    found = [i for i, line in enumerate(lines) if needle in line and not line.lstrip().startswith("--")]
    if len(found) != 1:
        print(f"ERROR: expected one active anchor {needle!r}, found {len(found)}.", file=sys.stderr)
        raise SystemExit(1)
    return found[0]


def migrate_block(lines: list[str], old_begin: str, old_end: str, new_begin: str, new_end: str, fragment: list[str]) -> bool:
    old = find_block(lines, old_begin, old_end)
    new = find_block(lines, new_begin, new_end)
    if old and new:
        print(f"ERROR: both legacy and current W&B blocks are installed for {new_begin!r}.", file=sys.stderr)
        raise SystemExit(1)
    if not old:
        return False
    lines[old[0]:old[1]] = fragment
    return True


def install_insert(lines: list[str], begin: str, end: str, fragment: list[str], anchor: str, before: bool) -> bool:
    block = find_block(lines, begin, end)
    if block:
        if lines[block[0]:block[1]] == fragment:
            return False
        lines[block[0]:block[1]] = fragment
        return True
    index = active_anchor(lines, anchor)
    lines[index if before else index + 1:index if before else index + 1] = fragment
    return True


def install_at_end(lines: list[str], begin: str, end: str, fragment: list[str]) -> bool:
    block = find_block(lines, begin, end)
    if block and block[1] == len(lines) and lines[block[0]:block[1]] == fragment:
        return False
    if block:
        del lines[block[0]:block[1]]
    lines.extend(fragment)
    return True


def locate_sequence(lines: list[str], sequence: list[str]) -> int:
    found = [i for i in range(0, len(lines) - len(sequence) + 1) if lines[i:i + len(sequence)] == sequence]
    if len(found) != 1:
        print(f"ERROR: expected one exact stock payload gate, found {len(found)}.", file=sys.stderr)
        raise SystemExit(1)
    return found[0]


def install_replacement(
    lines: list[str], begin: str, end: str, fragment: list[str], stock_sequence: list[str]
) -> bool:
    block = find_block(lines, begin, end)
    if block:
        if lines[block[0]:block[1]] == fragment:
            return False
        lines[block[0]:block[1]] = fragment
        return True
    index = locate_sequence(lines, stock_sequence)
    lines[index:index + len(stock_sequence)] = fragment
    return True


def remove_block(lines: list[str], begin: str, end: str, replacement: list[str] | None = None) -> bool:
    block = find_block(lines, begin, end)
    if not block:
        return False
    lines[block[0]:block[1]] = replacement or []
    return True


def validate_lua(payload: bytes, label: str = "Lua file") -> None:
    compiler = shutil.which("luac")
    if compiler is None:
        print("Lua syntax check skipped: luac not found.")
        return
    temporary_path: Path | None = None
    try:
        # Windows prevents luac.exe from reopening a NamedTemporaryFile while
        # Python still owns its default exclusive handle. Keep the generated
        # name, but close the file before starting the external compiler.
        with tempfile.NamedTemporaryFile(suffix=".lua", delete=False) as temporary:
            temporary_path = Path(temporary.name)
            temporary.write(payload)
            temporary.flush()
        completed = subprocess.run(
            [compiler, "-p", str(temporary_path)], capture_output=True, text=True, check=False
        )
    finally:
        if temporary_path is not None:
            try:
                temporary_path.unlink()
            except FileNotFoundError:
                pass
    if completed.returncode:
        print(f"ERROR: modified {label} failed luac: {completed.stderr.strip()}", file=sys.stderr)
        raise SystemExit(1)
    print(f"Lua syntax check passed: {label}")


def patch_tablet(lines: list[str], uninstall: bool, fragments: dict[str, list[str]]) -> bool:
    changed = False
    if uninstall:
        changed |= remove_block(lines, DOFILE_BEGIN, DOFILE_END)
        changed |= remove_block(lines, INSTALL_BEGIN, INSTALL_END)
        changed |= remove_block(lines, EXTERNAL_BEGIN, EXTERNAL_END, ["\tif B738DR_ext_payload == 0 then", "\t\tsam_tick = 0"])
        changed |= remove_block(lines, INTERNAL_BEGIN, INTERNAL_END, ["\tif B738DR_ext_payload == 0 then"])
        changed |= remove_block(lines, TOTAL_BEGIN, TOTAL_END, ["\t\t\t\tsimDR_payload_weight = full_crew_weight"])
        for old_begin, old_end, _, _ in LEGACY_MARKERS:
            replacement = None
            if "EXTERNAL" in old_begin:
                replacement = ["\tif B738DR_ext_payload == 0 then", "\t\tsam_tick = 0"]
            elif "INTERNAL" in old_begin:
                replacement = ["\tif B738DR_ext_payload == 0 then"]
            elif "TOTAL" in old_begin:
                replacement = ["\t\t\t\tsimDR_payload_weight = full_crew_weight"]
            changed |= remove_block(lines, old_begin, old_end, replacement)
    else:
        for old_begin, old_end, new_begin, new_end in LEGACY_MARKERS:
            changed |= migrate_block(lines, old_begin, old_end, new_begin, new_end, fragments[new_begin])

        changed |= install_insert(lines, DOFILE_BEGIN, DOFILE_END, fragments[DOFILE_BEGIN], "jit.off()", False)
        changed |= install_at_end(lines, INSTALL_BEGIN, INSTALL_END, fragments[INSTALL_BEGIN])
        changed |= install_replacement(
            lines, EXTERNAL_BEGIN, EXTERNAL_END, fragments[EXTERNAL_BEGIN],
            ["\tif B738DR_ext_payload == 0 then", "\t\tsam_tick = 0"],
        )
        changed |= install_replacement(
            lines, INTERNAL_BEGIN, INTERNAL_END, fragments[INTERNAL_BEGIN],
            ["\tif B738DR_ext_payload == 0 then", "\t\tlocal add_weight = 0"],
        )
        internal_block = find_block(lines, INTERNAL_BEGIN, INTERNAL_END)
        assert internal_block is not None
        if internal_block[1] >= len(lines) or lines[internal_block[1]] != "\t\tlocal add_weight = 0":
            lines.insert(internal_block[1], "\t\tlocal add_weight = 0")
            changed = True
        changed |= install_replacement(
            lines, TOTAL_BEGIN, TOTAL_END, fragments[TOTAL_BEGIN],
            ["\t\t\t\tsimDR_payload_weight = full_crew_weight"],
        )
    return changed


def patch_fms(lines: list[str], uninstall: bool, fragments: dict[str, list[str]]) -> bool:
    changed = False
    if uninstall:
        changed |= remove_block(lines, FMS_EMPTY_BEGIN, FMS_EMPTY_END)
        changed |= remove_block(lines, FMS_ZFW_BEGIN, FMS_ZFW_END, FMS_ZFW_STOCK)
    else:
        changed |= install_insert(
            lines, FMS_EMPTY_BEGIN, FMS_EMPTY_END, fragments[FMS_EMPTY_BEGIN],
            FMS_EMPTY_STOCK[0], False,
        )
        changed |= install_replacement(
            lines, FMS_ZFW_BEGIN, FMS_ZFW_END, fragments[FMS_ZFW_BEGIN], FMS_ZFW_STOCK,
        )
    return changed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--uninstall", action="store_true")
    parser.add_argument("--aircraft-root", type=Path, help="LevelUp aircraft root containing the supported ACFs")
    args = parser.parse_args()

    require(TABLET_LUA_FILE)
    require(FMS_LUA_FILE)
    version = ""
    if not args.uninstall:
        version = verify_package()
        aircraft_root = args.aircraft_root or default_aircraft_root()
        for contract in ACF_CONTRACTS:
            verify_acf(aircraft_root / str(contract["name"]), contract)

    tablet_original = TABLET_LUA_FILE.read_bytes()
    tablet_lines, tablet_eol, tablet_final_eol = split_lines(tablet_original)
    fms_original = FMS_LUA_FILE.read_bytes()
    fms_lines, fms_eol, fms_final_eol = split_lines(fms_original)
    fragments = {
        DOFILE_BEGIN: read_fragment(Path("Add_levelup_ng_wb_dofile.txt")),
        INSTALL_BEGIN: read_fragment(Path("Add_levelup_ng_wb_install_hook.txt")),
        EXTERNAL_BEGIN: read_fragment(Path("Replace_external_payload_gate.txt")),
        INTERNAL_BEGIN: read_fragment(Path("Replace_internal_payload_gate.txt")),
        TOTAL_BEGIN: read_fragment(Path("Replace_total_payload_scalar_gate.txt")),
        FMS_EMPTY_BEGIN: read_fragment(Path("Add_levelup_ng_wb_fms_empty_weight.txt")),
        FMS_ZFW_BEGIN: read_fragment(Path("Replace_levelup_ng_wb_fms_zfw_owner.txt")),
    }

    tablet_changed = patch_tablet(tablet_lines, args.uninstall, fragments)
    fms_changed = patch_fms(fms_lines, args.uninstall, fragments)

    if not tablet_changed and not fms_changed:
        print("LevelUp 737NG W&B hooks are already in the requested state.")
        return 0

    tablet_modified = encode_lines(tablet_lines, tablet_eol, tablet_final_eol)
    fms_modified = encode_lines(fms_lines, fms_eol, fms_final_eol)
    if tablet_changed:
        validate_lua(tablet_modified, TABLET_LUA_FILE.name)
    if fms_changed:
        validate_lua(fms_modified, FMS_LUA_FILE.name)

    if not args.uninstall:
        if tablet_changed:
            tablet_backup = LEGACY_BACKUP_FILE if LEGACY_BACKUP_FILE.exists() else TABLET_BACKUP_FILE
            if not tablet_backup.exists():
                shutil.copy2(TABLET_LUA_FILE, tablet_backup)
                print(f"Backup created: {tablet_backup}")
            else:
                print(f"Backup already exists, not overwritten: {tablet_backup}")
        if fms_changed:
            if not FMS_BACKUP_FILE.exists():
                shutil.copy2(FMS_LUA_FILE, FMS_BACKUP_FILE)
                print(f"Backup created: {FMS_BACKUP_FILE}")
            else:
                print(f"Backup already exists, not overwritten: {FMS_BACKUP_FILE}")

    written: list[tuple[Path, bytes]] = []
    try:
        if tablet_changed:
            TABLET_LUA_FILE.write_bytes(tablet_modified)
            written.append((TABLET_LUA_FILE, tablet_original))
        if fms_changed:
            FMS_LUA_FILE.write_bytes(fms_modified)
            written.append((FMS_LUA_FILE, fms_original))
    except OSError as error:
        for path, original in reversed(written):
            path.write_bytes(original)
        print(f"ERROR: W&B installation rolled back after write failure: {error}", file=sys.stderr)
        raise SystemExit(1)

    action = "Removed" if args.uninstall else f"Installed {version}"
    targets = [str(path) for path, changed in ((TABLET_LUA_FILE, tablet_changed), (FMS_LUA_FILE, fms_changed)) if changed]
    print(f"{action} LevelUp 737NG W&B hooks in {', '.join(targets)}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
