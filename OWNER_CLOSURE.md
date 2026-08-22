# Owner and closure matrix

| Chain element | Owner for IDs 2/0/1/4 | Input / unit | Consumer | Dry evidence | Runtime status |
|---|---|---|---|---|---|
| Aircraft reference | active versioned ACF contract | lb, ft -> kg, m | data table | four semantic gates and reconciled overlay fields | not run |
| Variant selection | `zibomod/b737_variant` | ID 2, 0, 1 or 4 | contract selector | four-way switch/delegation harness | not run |
| EFB payload selection | stock Tablet zones/cargo/crew | pax counts, kg | target builder | mapping test | -700 only observed |
| Internal station state | common adapter | nine targets, kg | `m_stations[0..8]` | independent rate/owner tests for all four | -700 v0.1.3 positive |
| External station state | external tool/X-Plane | nine masses, kg | read-only prediction input | no-write tests for all four | not run |
| Aggregate payload | X-Plane | station sum, kg | `m_fixed` readback | all known stock scalar writers and command gated | not run |
| Empty/service mass | ACF plus service stations | kg | `oew_kg`, EFB weights | no-524-kg tests; author contract confirmed | not run |
| Actual fuel | X-Plane | `m_fuel[0..2]`, kg | current GW/CG | read-only path | not run |
| Requested TOW fuel | Tablet | total kg | per-contract tanks, taxi state | fixed and variable-arm independent fuel tests | not run |
| Destination fuel | Tablet/FMC | total kg | LW prediction | independent fuel tests | not run |
| Current/in-flight CG | X-Plane | `cg_offset_z_mac`, %MAC | EFB graph/current CG | owner tests | -700 v0.1.3: 22.63% |
| ZFW CG | moment core | empty + planned/current stations | EFB ZFW | independent kg-m tests for all four | v0.3.0 not run |
| TOW CG | moment core | stations + fuel - 226.8 kg | EFB, `calc_to_cg`, FMC | all four plus handoff | v0.3.0 not run |
| LW CG | moment core | stations + destination fuel | EFB LW | all four | v0.3.0 not run |
| Datum transform | X-Plane offsets + modeled current ZFW | m, %MAC, ACF MAC | one derived LEMAC | XLua property/datum tests | v0.1.3 failure fixed; pending |
| Envelope | active ACF contract fixed positions | anchored %MAC | EFB checks | boundary tests for all four | pending |
| FMC CG | upstream FMC | `calc_to_cg`, %MAC | TAKEOFF REF / `fmc_cg` | producer handoff | pending |
| Takeoff trim | upstream table | FMC CG, flaps | trim display | unchanged consumer | pending |
| Save/load/SimBrief | stock Tablet | zone/cargo state | regenerated targets | owner design | pending |
| Aircraft reload/change | common adapter | variant ID | cache invalidation/delegation | 2 -> 0 -> unsupported harness | pending |
| Installer lifecycle | common installer | stock .35 + four ACF contracts | five marked blocks | LF/CRLF, idempotence, uninstall | not runtime |
| v0.1.4/v0.2.x migration | common installer | legacy/current five blocks and backup | v0.3.0 contract | migration/idempotence harness | not runtime |
| Patch coexistence | independent marked blocks | stock Tablet | performance patch retained | both install orders represented | pending runtime |
| Unsupported ID 3/Zibo | stock implementation | original state | original consumers | delegation tests | pending runtime |

## Open closure items

- The complete -700/-800/-900/-900ER chain still requires simulator evidence.
- Cargo is capacity-normalized; an extreme service entry above an ACF maximum
  is deliberately rejected because dropping crew/catering mass would violate
  closure.
- The fixed envelopes and ACF tank geometry are supplied-ACF feasibility
  contracts, not independently validated real-aircraft curves. The -900ER
  main-tank arm varies linearly between the ACF empty and full positions.
- Existing FMC trim tables are preserved and must be checked as consumers;
  they have not been revalidated aerodynamically.
- ID 3 (-600) remains delegated until a sourced ACF contract exists.
- Display agreement alone is insufficient: stations, fuel, current/ZFW/TOW/LW
  CG, FMC handoff and trim must close in the same captured state.
