#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import zipfile
from pathlib import Path


REPOSITORY = Path(__file__).resolve().parents[1]
VERSION = "v0.3.0"
ARCHIVE_NAME = f"LevelUp-737NG-Weight-Balance-{VERSION}.zip"
RELEASE_FILES = (
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
    "patches/B738.tablet.lua.json",
    "contracts/levelup-ng-wb-acf-v0.3.0.json",
    "toolkit/weight-and-balance-module.json",
    "README.md",
    "INSTALLATION.md",
    "SOURCE.md",
    "OWNER_CLOSURE.md",
    "RUNTIME_TEST_PLAN.md",
    "ACF_RECONCILE_2026_08_22.md",
    "CHANGELOG.md",
    "LICENSE",
)
ZIP_TIMESTAMP = (2026, 8, 22, 0, 0, 0)


def main() -> int:
    manifest = (REPOSITORY / "levelup-ng-wb-package-manifest.txt").read_text(encoding="utf-8")
    if f"package|version|{VERSION}" not in manifest:
        raise RuntimeError(f"Package manifest does not declare {VERSION}.")

    destination = REPOSITORY / "dist"
    destination.mkdir(exist_ok=True)
    archive_path = destination / ARCHIVE_NAME
    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for relative in RELEASE_FILES:
            path = REPOSITORY / relative
            if not path.is_file():
                raise FileNotFoundError(path)
            info = zipfile.ZipInfo(relative, date_time=ZIP_TIMESTAMP)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (0o100644 & 0xFFFF) << 16
            archive.writestr(info, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)

    digest = hashlib.sha256(archive_path.read_bytes()).hexdigest()
    checksum_path = archive_path.with_suffix(archive_path.suffix + ".sha256")
    checksum_path.write_text(f"{digest}  {archive_path.name}\n", encoding="ascii", newline="\n")
    print(archive_path)
    print(checksum_path)
    print(digest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
