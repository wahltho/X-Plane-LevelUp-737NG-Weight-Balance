local root = arg[0]:match("^(.*)/tests/") or "."
local data = dofile(root .. "/B738.tablet_levelup_ng_wb_data.lua")
local core = dofile(root .. "/B738.tablet_levelup_ng_wb_core.lua")

-- Synthetic independent dimensional fixture, not aircraft reference data.
local function inputs()
    local input = { empty_kg = 40000, max_kg = 70000, reference_ft = 50, fuel_kg = 20000,
        station_z = {}, station_max = {}, tank_rat = {}, tank_empty = {}, tank_full = {} }
    for i = 0, 8 do
        input.station_z[i], input.station_max[i], input.tank_rat[i] = 10 + i, 2000, 0
    end
    input.tank_rat[0], input.tank_rat[1], input.tank_rat[2] = 0.2, 0.6, 0.2
    input.tank_empty[0], input.tank_empty[1], input.tank_empty[2] = -1, -2, -1
    input.tank_full[0], input.tank_full[1], input.tank_full[2] = 1, -2, 1
    return input
end
local meta = { mac_m = 4.5, cg_fwd_z_m = 14, cg_aft_z_m = 17 }
local function near(actual, expected)
    assert(math.abs(actual - expected) < 1e-10, tostring(actual) .. " != " .. tostring(expected))
end
for _, variant in ipairs({3, 2, 0, 1, 4}) do
    local input = inputs()
    local snapshot = assert(data.snapshot(data[variant], meta, input))
    near(snapshot.empty_mass_kg, 40000)
    near(snapshot.empty_cg_z_m, 15.24)
    near(snapshot.tanks[1].max_kg, 4000)
    near(snapshot.tanks[2].max_kg, 12000)
    near(snapshot.tanks[1].empty_arm_m, 14.24)
    near(snapshot.tanks[1].full_arm_m, 16.24)
    near(core.tank_arm(snapshot.tanks[1], 1000), 14.74)
    near(core.tank_arm(snapshot.tanks[1], 2000), 15.24)
    local cg, mass, moment = core.cg_z(40000, 15.24,
        {1000, 0, 0, 0, 0, 0, 0, 0, 0}, snapshot.stations, {1000, 0, 0}, snapshot.tanks)
    near(mass, 42000)
    near(moment, 634340) -- 40000*15.24 + 1000*10 + 1000*14.74
    near(cg, 634340/42000)

    input.station_z[0] = 13
    input.station_max[0] = 2500
    input.empty_kg = 41000
    input.reference_ft = 51
    input.max_kg = 72000
    input.fuel_kg = 22000
    local changed = assert(data.snapshot(data[variant], meta, input))
    near(changed.stations[1].arm_m, 13)
    near(changed.stations[1].max_kg, 2500)
    near(changed.empty_mass_kg, 41000)
    near(changed.empty_cg_z_m, 15.5448)
    near(changed.max_gross_mass_kg, 72000)
    near(changed.tanks[1].max_kg, 4400)
    near(changed.tanks[1].empty_arm_m, 14.5448)
    near(snapshot.stations[1].arm_m, 10) -- old snapshot cannot mutate
    near(snapshot.tanks[1].max_kg, 4000)
    for _, bad in ipairs({0, -1, math.huge}) do
        input.station_max[0] = bad
        assert(not data.snapshot(data[variant], meta, input))
    end
    input = inputs()
    input.station_z[1] = 0/0
    assert(not data.snapshot(data[variant], meta, input))
    input = inputs()
    input.tank_rat[3] = 0.01
    assert(not data.snapshot(data[variant], meta, input))
    input = inputs()
    input.tank_rat[0], input.tank_rat[2] = 0.1, 0.3
    assert(not data.snapshot(data[variant], meta, input))
    input = inputs()
    input.tank_full[0] = nil
    assert(not data.snapshot(data[variant], meta, input))
end
assert(data[6] == nil and data[-1] == nil)
print("PASS: dynamic runtime units, kg/m moments, endpoints, independent snapshots and input rejection")
