# LevelUp 737NG W&B v0.5.3

Adds silent ACF compatibility checks to the public Lua patch. Tablet and FMS
only take W&B ownership when the loaded aircraft has the supported nine-station
layout and valid ACF W&B inputs. Old, missing or incompatible ACFs retain the
upstream behavior without W&B warnings, payload intervention or CG clearing.
Reloading an aircraft or changing variant/path re-evaluates compatibility.

Valid aircraft retain dynamic geometry, the v0.5.2 station-coordinate fix,
external payload ownership and existing runtime numeric safety guards. No ACF,
airfoil, flight-model, trim-table or private C++ changes are included.

The FMS uses the same ACF predicate in its own XLua state, avoiding dependence
on Tablet/FMS callback order. Toolkit exact-text anchors are now unambiguous.
No additional Toolkit ACF-specific validation logic is required for this
runtime protection. This release supplies the module; it does not publish the
separate consolidated Maintenance Toolkit package.

## Install / update

Close X-Plane. Extract the complete ZIP into
`plugins/xlua/scripts/B738.tablet/`, replacing the previous patch files. Run
`py z_Install_LevelUp_NG_WB.py` on Windows or
`python3 z_Install_LevelUp_NG_WB.py` on macOS/Linux, then restart X-Plane.

Unlike 0.5.1-to-0.5.2, this update changes marked hook contents and adds the
FMS reload hook: extract the full package AND rerun the installer. Existing
backups and co-installed supported performance/VNAV patches are preserved.
The standalone installer still refuses incompatible ACFs before editing Lua;
the new runtime protection also covers a later ACF replacement or a Toolkit
installation path.

Automated validation is documented in `VALIDATION_0.5.3.md`. In-simulator
acceptance across all five variants remains pending, including old/new ACF
reloads, external loading, the reported -600 100-PAX case and FMC CG/trim.
