local package_root = arg[0]:match("^(.*)/tests/") or "."

B738DR_b737_variant = 3
B738DR_ext_payload = 0
B738DR_std_pax_weight = { [0] = 84, [1] = 35, [2] = 10 }
B738DR_fa_fwd_kg = 120
B738DR_fa_aft_kg = 330
B738DR_galley_fwd_kg = 100
B738DR_galley_aft_kg = 125
B738DR_req_fuel = 10000
B738DR_calc_to_cg = 0
B738DR_oew_kg = 0
SIM_PERIOD = 0.1

zone1_pax = { 10, 2, 1 }
zone2_pax = { 12, 1, 0 }
zone3_pax = { 14, 0, 1 }
zone4_pax = { 3, 0, 0 }
zone5_pax = { 9, 1, 1 }
zone_cargo1 = 1000
zone_cargo2 = 500
zone_weight_req = { 0, 0, 0, 0, 0 }

simDR_payload_stations = { [0] = 0, [1] = 0, [2] = 0, [3] = 0, [4] = 0, [5] = 0, [6] = 0, [7] = 0, [8] = 0 }
simDR_fuel_tank_weight_kg = { [0] = 3000, [1] = 5000, [2] = 3000 }
simDR_cg_xp12 = 0.12

local LB_TO_KG = 0.45359237
local FT_TO_M = 0.3048
local literal = {
    [0] = {
        empty_mass = 91514.04 * LB_TO_KG,
        empty_arm = 59.889999390 * FT_TO_M,
        mac = 14.992127419 * FT_TO_M,
        lemac = 17.4,
        fwd = 57.869998932 * FT_TO_M,
        aft = 61.840000153 * FT_TO_M,
        station_arms = { 37, 85, 33.5, 46.5, 58.5, 70.5, 82.5, 15, 99 },
        fuel_total = 46062.01,
        tank_empty = { 64, 56.5, 64 },
        tank_full = { 64, 56.5, 64 },
        takeoff_fuel = { 3907.0614902557695, 1959.077019488461, 3907.0614902557695 },
    },
    [1] = {
        empty_mass = 94580 * LB_TO_KG,
        empty_arm = 64.650001526 * FT_TO_M,
        mac = 14.993530273 * FT_TO_M,
        lemac = 18.4,
        fwd = 63.380001068 * FT_TO_M,
        aft = 67.129997253 * FT_TO_M,
        station_arms = { 45, 89, 34, 47.5, 65, 77, 91, 15, 108 },
        fuel_total = 46062.008,
        tank_empty = { 69, 62, 69 },
        tank_full = { 69, 62, 69 },
        takeoff_fuel = { 3907.061320612218, 1959.077358775564, 3907.061320612218 },
    },
    [2] = {
        empty_mass = 82999.61 * LB_TO_KG,
        empty_arm = 49.029998779 * FT_TO_M,
        mac = 14.992128372 * FT_TO_M,
        lemac = 13.9,
        fwd = 47.189998627 * FT_TO_M,
        aft = 50.939998627 * FT_TO_M,
        station_arms = { 29, 69, 22, 34, 46, 58, 70, 15, 80 },
        fuel_total = 46062.008,
        tank_empty = { 52.650001526, 46, 52.650001526 },
        tank_full = { 52.650001526, 46, 52.650001526 },
        takeoff_fuel = { 3907.0613206122184, 1959.077358775563, 3907.0613206122184 },
    },
    [4] = {
        empty_mass = 98495 * LB_TO_KG,
        empty_arm = 65.389999390 * FT_TO_M,
        mac = 14.993530273 * FT_TO_M,
        lemac = 18.6,
        fwd = 64.879997253 * FT_TO_M,
        aft = 67.879997253 * FT_TO_M,
        station_arms = { 45, 89, 34, 47.5, 65, 77, 91, 15, 108 },
        fuel_total = 52512.31,
        tank_empty = { 69, 62, 69 },
        tank_full = { 69, 62, 69 },
        takeoff_fuel = { 4454.187391418068, 864.8252171638644, 4454.187391418068 },
    },
}

local function independent_cg(variant, stations, fuel)
    local ref = literal[variant]
    local mass = ref.empty_mass
    local moment = ref.empty_mass * ref.empty_arm
    for index = 1, 9 do
        mass = mass + stations[index]
        moment = moment + stations[index] * ref.station_arms[index] * FT_TO_M
    end
    if fuel then
        for index = 1, 3 do
            mass = mass + fuel[index]
            local capacity = ref.fuel_total * ({ 0.187000006, 0.625999987, 0.187000006 })[index] * LB_TO_KG
            local arm = ref.tank_empty[index] +
                (ref.tank_full[index] - ref.tank_empty[index]) * fuel[index] / capacity
            moment = moment + fuel[index] * arm * FT_TO_M
        end
    end
    return moment / mass
end

local function independent_mac(variant, stations, fuel)
    local ref = literal[variant]
    return ((independent_cg(variant, stations, fuel) - ref.lemac) / ref.mac) * 100
end

local zfw_offset_value = 0
local function establish_xplane_reference(variant, stations)
    local actual_fuel = { 3000, 5000, 3000 }
    local current_zfw_m = independent_cg(variant, stations, nil)
    local current_gross_m = independent_cg(variant, stations, actual_fuel)
    simDR_cg_z_mac = ((current_gross_m - literal[variant].lemac) / literal[variant].mac) * 100
    zfw_offset_value = simDR_cg_xp12 + current_zfw_m - current_gross_m
end

-- Reproduce XLua scalar-property resolution. A local find_dataref result stays
-- a wrapper table; a module-global assignment resolves to the numeric value.
local xlua_properties = {}
setmetatable(_G, {
    __newindex = function(environment, key, value)
        if type(value) == "table" and type(value.__get) == "function" then
            xlua_properties[key] = value
        else
            rawset(environment, key, value)
        end
    end,
    __index = function(_, key)
        local property = xlua_properties[key]
        if property then return property.__get(property) end
        return nil
    end,
})

function find_dataref(name)
    assert(name == "sim/flightmodel2/misc/zfw_cg_offset_z")
    return {
        __get = function() return zfw_offset_value end,
        __set = function(_, value) zfw_offset_value = value end,
        dref = name,
    }
end

local stock_calls = 0
update_payload = function() stock_calls = stock_calls + 1 end
calc_mac = function() return 31, 31 end
calc_zfw_mac = function() return 32 end
calc_oew_mac = function() return 33 end
calc_des_mac = function() return 34 end
calc_gw_cg_shift = function() return 35, 35 end
check_tow = function() return "stock_tow" end
check_gw = function() return "stock_gw" end
check_zfw = function() return "stock_zfw" end
check_lw = function() return "stock_lw" end
after_physics = function() stock_calls = stock_calls + 10 end
B738CMD_change_payload = { once = function() stock_calls = stock_calls + 100 end }
total_payload_entry = function() stock_calls = stock_calls + 1000 end

-- XLua 1.3 discards dofile() return values. Both nested modules and the
-- adapter must therefore self-register through explicit globals.
local standard_dofile = dofile
dofile = function(path)
    if path:match("^B738%.tablet_levelup_ng_wb_") then
        standard_dofile(package_root .. "/" .. path)
    else
        standard_dofile(path)
    end
    return nil
end
dofile("B738.tablet_levelup_ng_wb_adapter.lua")
assert(B738_levelup_ng_wb_adapter ~= nil, "adapter must self-register under XLua")
assert(B738_levelup_ng_wb_core ~= nil, "core must self-register under XLua")
assert(B738_levelup_ng_wb_data ~= nil, "data must self-register under XLua")
assert(xlua_properties.simDR_levelup_ng_zfw_cg_offset_z ~= nil,
    "ZFW offset must be bound as an XLua module-global property")
dofile = standard_dofile
local adapter = B738_levelup_ng_wb_adapter
adapter.install()

update_payload()
assert(stock_calls == 1, "unsupported LevelUp variant must delegate update_payload")
assert(calc_zfw_mac() == 32, "unsupported LevelUp variant must preserve stock CG")
B738CMD_change_payload:once()
assert(stock_calls == 101, "unsupported LevelUp command must delegate")

local selected = { 1000, 500, 920, 1043, 1186, 252, 801, 325, 350 }
local service_only = { 0, 0, 0, 0, 0, 0, 0, 325, 350 }
local empty_stations = { 0, 0, 0, 0, 0, 0, 0, 0, 0 }

local function exercise_variant(variant)
    B738DR_b737_variant = variant
    B738DR_ext_payload = 0
    for index = 0, 8 do simDR_payload_stations[index] = 0 end
    establish_xplane_reference(variant, empty_stations)
    update_payload()
    B738CMD_change_payload:once()
    assert(math.abs(full_crew_weight - 675) < 1e-12, "must not add stock 524 kg")
    assert(math.abs(full_crew_weight_f - 325) < 1e-12)
    assert(math.abs(full_crew_weight_r - 350) < 1e-12)
    assert(math.abs(B738DR_oew_kg - (literal[variant].empty_mass + 675)) < 1e-9)

    local before = stock_calls
    after_physics()
    assert(stock_calls == before + 10, "wrapped stock after_physics must still run")
    for index = 0, 8 do
        assert(math.abs(simDR_payload_stations[index] - 22.2) < 1e-9,
            "internal stations must slow-load independently: " .. variant .. "/" .. index)
    end
    assert(B738DR_calc_to_cg >= 6 and B738DR_calc_to_cg <= 36, "takeoff CG must feed FMC handoff")

    local takeoff_mac = calc_mac(1)
    local expected_takeoff_mac = independent_mac(variant, selected, literal[variant].takeoff_fuel)
    assert(math.abs(takeoff_mac - expected_takeoff_mac) < 1e-9, "TOW CG must use active ACF contract")
    local expected_zfw_mac = independent_mac(variant, selected, nil)
    assert(math.abs(calc_zfw_mac() - expected_zfw_mac) < 1e-9, "ZFW CG must use active ACF contract")
    assert(math.abs(calc_oew_mac() - independent_mac(variant, service_only, nil)) < 1e-9,
        "OEW CG must use active ACF contract")
    local destination_fuel = { 1000, 0, 1000 }
    local expected_lw_mac = independent_mac(variant, selected, destination_fuel)
    assert(math.abs(calc_des_mac(2000) - expected_lw_mac) < 1e-9, "LW CG must use active ACF contract")
    local tow_cg = independent_cg(variant, selected, literal[variant].takeoff_fuel)
    local zfw_cg = independent_cg(variant, selected, nil)
    assert(check_tow(50000, takeoff_mac) ==
        (tow_cg >= literal[variant].fwd and tow_cg <= literal[variant].aft),
        "TOW fixed-envelope result must follow ACF coordinates")
    assert(check_zfw(44000, expected_zfw_mac) ==
        (zfw_cg >= literal[variant].fwd and zfw_cg <= literal[variant].aft),
        "ZFW fixed-envelope result must follow ACF coordinates")

    B738DR_ext_payload = 1
    local external = { 100, 200, 300, 400, 300, 200, 100, 50, 60 }
    for index = 0, 8 do simDR_payload_stations[index] = external[index + 1] end
    establish_xplane_reference(variant, external)
    adapter.frame_update()
    for index = 0, 8 do
        assert(simDR_payload_stations[index] == external[index + 1], "external mode must be read-only")
    end
    assert(math.abs(req_payload_weight - 1710) < 1e-12)
    assert(math.abs(full_crew_weight - 110) < 1e-12)
    local current_mac, current_pos = calc_gw_cg_shift()
    assert(current_mac == simDR_cg_z_mac and current_pos == simDR_cg_z_mac,
        "current CG must come from X-Plane")
end

exercise_variant(2)
exercise_variant(0)
exercise_variant(1)
exercise_variant(4)

-- Rounded upstream Tablet cargo limits are normalized to the exact ACF
-- station capacities before any physical write or FMC handoff.
B738DR_b737_variant = 4
B738DR_ext_payload = 0
zone_cargo1 = 3560
zone_cargo2 = 4850
zone1_pax = { 1, 0, 0 }
zone2_pax = { 1, 0, 0 }
zone3_pax = { 1, 0, 0 }
zone4_pax = { 1, 0, 0 }
zone5_pax = { 42, 0, 0 }
B738DR_galley_fwd_kg = 1
B738DR_galley_aft_kg = 1000
for index = 0, 8 do simDR_payload_stations[index] = 0 end
establish_xplane_reference(4, empty_stations)
adapter.frame_update()
assert(math.abs(zone_cargo1 - 7848 * LB_TO_KG) < 1e-9, "cargo1 must use exact ACF maximum")
assert(math.abs(zone_cargo2 - 10500 * LB_TO_KG) < 1e-9, "900ER cargo2 must use exact ACF maximum")
assert(B738DR_calc_to_cg == 0,
    "normalized but out-of-range extreme load must not publish a stale FMC CG")
for index = 0, 8 do assert(simDR_payload_stations[index] > 0, "normalized targets must slow-load") end
zone_cargo1 = 1000
zone_cargo2 = 500
zone1_pax = { 10, 2, 1 }
zone2_pax = { 12, 1, 0 }
zone3_pax = { 14, 0, 1 }
zone4_pax = { 3, 0, 0 }
zone5_pax = { 9, 1, 1 }
B738DR_galley_fwd_kg = 100
B738DR_galley_aft_kg = 125

zfw_offset_value = 100
adapter.frame_update()
assert(B738DR_calc_to_cg == 0, "invalid X-Plane datum must suppress FMC CG instead of publishing a guess")

B738DR_b737_variant = 3
assert(check_tow(1, 1) == "stock_tow", "variant switch must relinquish envelope ownership")
print("PASS: -700/-800/-900/-900ER owners, ACF tank arms, exact cargo limits, external read-only and delegation")
