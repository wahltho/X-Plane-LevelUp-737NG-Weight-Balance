# LevelUp 737NG W&B v0.5.2

Fixes a coordinate-conversion error introduced with the dynamic geometry
in 0.5.0: native payload-station positions are CG-relative metres, not absolute
arms. The patch now adds the original reference CG once before calculating
moments. This addresses implausible OEW/TO CG after payload changes and also
corrects the shared landing-CG prediction inputs.

The existing takeoff-CG handoff to the FMC was already present. It receives
the corrected calculation; no FMC trim tables or accepted manual CG are changed.
ACFs, flight models, fuel/loading policies and upstream hook placement remain
unchanged. Both corrected and legacy -600/-700 station/tank labels still work.

## Install / update

Close X-Plane and back up the aircraft. Extract the **complete ZIP** into
`plugins/xlua/scripts/B738.tablet/`, replacing the old patch files. Run
`py z_Install_LevelUp_NG_WB.py` on Windows or
`python3 z_Install_LevelUp_NG_WB.py` on macOS/Linux. Restart X-Plane.

For 0.5.0/0.5.1 upgrades, verified v0.5.2 payload plus “hooks are already in
the requested state” is success. Do not replace the upstream Tablet/FMS Lua
manually. Existing supported performance/VNAV patch blocks are preserved.
See `INSTALLATION.md` for details.

Automated Lua 5.1, independent mass/moment, all-five-variant, partial upstream
replay, installer/coexistence and ZIP checks are documented in
`VALIDATION_0.5.2.md`. In-simulator retesting is still required, particularly
the reported -600 100-PAX case, OEW graph and FMC CG acceptance.

Toolkit module metadata and hashes are included. Publishing this module does
not itself update the separate consolidated Maintenance Toolkit package.
