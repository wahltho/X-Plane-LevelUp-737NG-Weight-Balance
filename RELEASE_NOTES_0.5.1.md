# LevelUp 737NG W&B v0.5.1

Compatibility update for the corrected ACF labels:

- 737-600 right tank: `Right Main` or legacy `Right Wing`.
- 737-700 aft service station: `Galley A` or legacy `Galley R`.

Both old and new ACFs work with the standalone installer and runtime guard.
Aliases are limited to the respective variant and original array index.
All other station/tank layout and numeric safety checks remain active.

This release does not change CG/trim calculations, fuel or loading policies,
upstream Tablet/FMS hooks, or any ACF/flight-model/airfoil files. The newly
reported GW/TO/OEW CG discrepancies are not claimed fixed by this update.

## Installation

Close X-Plane, back up the aircraft, and extract the complete ZIP into
`plugins/xlua/scripts/B738.tablet/`. Run `py z_Install_LevelUp_NG_WB.py` on
Windows or `python3 z_Install_LevelUp_NG_WB.py` on macOS/Linux, then reload
the aircraft. Do not replace the upstream Tablet/FMS Lua manually.
See `INSTALLATION.md` for complete instructions.

## Toolkit integration

The versioned module and hashes are included for the consolidated package owner.
`contracts/levelup-ng-wb-acf-v0.5.1.json` uses canonical names in `text` and
optional field-scoped legacy alternatives in `textAlternatives`. Validators
supporting alternatives must accept exact canonical equality OR membership
in that field's alternatives; never ignore the name check altogether.
Canonical-only validators accept the corrected ACFs, not the legacy names.
This module release does not itself publish a consolidated Toolkit update.

Automated regression/package validation is recorded in `VALIDATION_0.5.1.md`.
No local upstream-Lua X-Plane runtime test was performed; tester feedback is
still required for simulator acceptance.
