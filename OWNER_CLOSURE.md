# Owner and closure matrix

| Chain element | Owner for IDs 3/2/0/1/4 | Input / unit | Consumer | Dry evidence | Runtime status |
|---|---|---|---|---|---|
| Aircraft reference | active versioned ACF contract | lb, ft -> kg, m | data table | five semantic gates and reconciled overlay fields | not run |
| Variant selection | `zibomod/b737_variant` | ID 3, 2, 0, 1 or 4 | contract selector | five-way switch/delegation harness | not run |
| EFB payload selection | stock Tablet zones/cargo/crew | pax counts, kg | target builder | mapping test | -700 only observed |
| Internal station state | common adapter | nine targets, kg | `m_stations[0..8]` | independent rate/owner tests for all five | -700 v0.1.3 positive |
| External station state | external tool/X-Plane | nine masses, kg | read-only prediction input | no-write tests for all five | not run |
| Aggregate payload | X-Plane | station sum, kg | `m_fixed` readback | all known stock scalar writers and command gated | not run |
| Empty/service mass | ACF plus service stations | kg | `oew_kg`, EFB weights | no-524-kg tests; author contract confirmed | not run |
| FMC ZFW/GW | upstream FMS with LevelUp owner gate | ACF empty kg + nine physical stations | PERF INIT and downstream GW | exact .35 structural patch; independent 524-kg oracle | RealBench root cause confirmed; v0.3.2 pending |
| Actual fuel | X-Plane | `m_fuel[0..2]`, kg | current GW/CG | read-only path | not run |
| Requested TOW fuel | Tablet | total kg | per-contract tanks, taxi state | independent ACF-arm fuel tests | not run |
| Destination fuel | Tablet/FMC | total kg | LW prediction | independent fuel tests | not run |
| Current/in-flight CG | X-Plane | `cg_offset_z_mac`, %MAC | EFB graph/current CG | owner tests | -700 v0.1.3: 22.63% |
| ZFW CG | moment core | empty + planned/current stations | EFB ZFW | independent kg-m tests for all five | -600 runtime pending |
| TOW CG | moment core | stations + fuel - 226.8 kg | EFB, `calc_to_cg`, FMC | all five plus handoff | -600 runtime pending |
| LW CG | moment core | stations + destination fuel | EFB LW | all five | -600 runtime pending |
| Datum transform | X-Plane offsets + modeled current ZFW | m, %MAC, ACF MAC | one derived LEMAC | XLua property/datum tests | v0.1.3 failure fixed; pending |
| Envelope | active ACF contract fixed positions | anchored %MAC | EFB checks | boundary tests for all five | pending |
| FMC CG | upstream FMC | `calc_to_cg`, %MAC | TAKEOFF REF / `fmc_cg` | producer handoff | pending |
| Takeoff trim | upstream table | FMC CG, flaps | trim display | unchanged consumer | pending |
| Save/load/SimBrief | stock Tablet | zone/cargo state | regenerated targets | owner design | pending |
| Aircraft reload/change | common adapter | variant ID | cache invalidation/delegation | 2 -> 0 -> unsupported harness | pending |
| Installer lifecycle | common installer | stock .35 + five ACF contracts | five Tablet + two FMS blocks | LF/CRLF, idempotence, uninstall | not runtime |
| v0.1.4-v0.3.1 migration | common installer | legacy/current blocks and backups | v0.3.2 contract | migration/idempotence harness | not runtime |
| Patch coexistence | independent marked blocks | stock Tablet/FMS | performance and VNAV patches retained | both install orders represented | pending runtime |
| Unsupported MAX IDs/Zibo | stock implementation | original state | original consumers | delegation tests | pending runtime |

## Open closure items

- The complete -600/-700/-800/-900/-900ER chain still requires simulator evidence.
- Cargo is capacity-normalized; an extreme service entry above an ACF maximum
  is deliberately rejected because dropping crew/catering mass would violate
  closure.
- The fixed envelopes and ACF tank geometry are supplied-ACF feasibility
  contracts, not independently validated real-aircraft curves. The current
  -900/-900ER ACFs use constant `69 ft` main-tank arms.
- Existing FMC trim tables are preserved and must be checked as consumers;
  they have not been revalidated aerodynamically.
- Display agreement alone is insufficient: stations, fuel, current/ZFW/TOW/LW
  CG, FMC handoff and trim must close in the same captured state.
