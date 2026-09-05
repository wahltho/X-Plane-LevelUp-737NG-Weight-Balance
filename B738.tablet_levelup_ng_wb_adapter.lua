-- Adapter for the stock Zibo 4.05.35 B738.tablet.lua used by LevelUp.

dofile("B738.tablet_levelup_ng_wb_data.lua")
dofile("B738.tablet_levelup_ng_wb_core.lua")
local contracts = B738_levelup_ng_wb_data
local core = B738_levelup_ng_wb_core
local M = {}
local original = {}
local warned_station = nil
local cached_lemac_z_m = nil
local aircraft_key, metadata, frame_data, geometry_error = nil, nil, nil, nil
local warned_geometry = nil
simDR_levelup_ng_zfw_cg_offset_z = find_dataref("sim/flightmodel2/misc/zfw_cg_offset_z")
-- XLua scalar properties must be module-global, not local wrapper objects.
simDR_levelup_ng_acf_path = find_dataref("sim/aircraft/view/acf_relative_path")
simDR_levelup_ng_empty = find_dataref("sim/aircraft/weight/acf_m_empty")
simDR_levelup_ng_max = find_dataref("sim/aircraft/weight/acf_m_max")
simDR_levelup_ng_reference = find_dataref("sim/aircraft/weight/acf_cgZ_original")
simDR_levelup_ng_station_z = find_dataref("sim/aircraft/weight/acf_stations_ref_z")
simDR_levelup_ng_station_max = find_dataref("sim/aircraft/weight/acf_m_station_max")
simDR_levelup_ng_fuel_max = find_dataref("sim/aircraft/weight/acf_m_fuel_tot")
simDR_levelup_ng_tank_empty = find_dataref("sim/aircraft/overflow/acf_tank_Z")
simDR_levelup_ng_tank_full = find_dataref("sim/aircraft/overflow/acf_tank_Z_full")
simDR_levelup_ng_tank_rat = find_dataref("sim/aircraft/overflow/acf_tank_rat")

function M.reset_aircraft()
    -- Retire our last handoff on a supported -> unsupported transition too;
    -- do not clear a continuously stock-owned aircraft's publication.
    if aircraft_key ~= nil or contracts[B738DR_b737_variant] then B738DR_calc_to_cg = 0 end
    aircraft_key, metadata, frame_data, geometry_error = nil, nil, nil, nil
    cached_lemac_z_m, warned_station, warned_geometry = nil, nil, nil
end

local function read_aircraft(refresh)
    local policy = contracts[B738DR_b737_variant]
    if not policy then M.reset_aircraft(); return nil end
    local loaded = (simDR_levelup_ng_acf_path or ""):gsub("%z.*", ""):gsub("\\", "/")
    local root = (file_path or ""):gsub("%z.*", ""):gsub("\\", "/")
    local key = tostring(B738DR_b737_variant) .. "|" .. root .. "|" .. loaded
    if aircraft_key ~= key then
        M.reset_aircraft()
        aircraft_key = key
        if loaded:match("([^/]+)$") ~= policy.acf_name or root == "" then
            geometry_error = "loaded ACF path/variant mismatch"
        else
            local ok, result, reason = pcall(contracts.read_metadata,
                root:gsub("/+$", "") .. "/" .. policy.acf_name, policy)
            if ok then metadata, geometry_error = result, reason
            else geometry_error = "ACF metadata read failed: " .. tostring(result) end
        end
        refresh = true
    end
    if refresh then
        cached_lemac_z_m = nil
        frame_data = nil
        if metadata then
            local ok, result, reason = pcall(function()
                return contracts.snapshot(policy, metadata, {
                    empty_kg = simDR_levelup_ng_empty, max_kg = simDR_levelup_ng_max,
                    reference_ft = simDR_levelup_ng_reference, fuel_kg = simDR_levelup_ng_fuel_max,
                    station_z = simDR_levelup_ng_station_z, station_max = simDR_levelup_ng_station_max,
                    tank_empty = simDR_levelup_ng_tank_empty, tank_full = simDR_levelup_ng_tank_full,
                    tank_rat = simDR_levelup_ng_tank_rat,
                })
            end)
            if ok then frame_data, geometry_error = result, reason
            else geometry_error = "aircraft DataRefs unavailable: " .. tostring(result) end
        end
    end
    if not frame_data then
        B738DR_calc_to_cg = 0
        if warned_geometry ~= geometry_error then
            print("LevelUp W&B: " .. tostring(geometry_error) ..
                "; station writes/predicted CG inhibited (reload after correcting ACF metadata)")
            warned_geometry = geometry_error
        end
    else
        warned_geometry = nil
    end
    return frame_data
end

local function active_data()
    return read_aircraft(false)
end

local function current_stations()
    local masses = {}
    for index = 1, 9 do masses[index] = simDR_payload_stations[index - 1] or 0 end
    return masses
end

local function selected_stations()
    local data = active_data()
    local cargo1 = zone_cargo1
    local cargo2 = zone_cargo2
    if data then
        cargo1, cargo2 = core.normalize_cargo(cargo1, cargo2, data.stations)
        if cargo1 ~= zone_cargo1 then
            zone_cargo1 = cargo1
            if B738DR_zone_cargo1_payload ~= nil then B738DR_zone_cargo1_payload = cargo1 end
        end
        if cargo2 ~= zone_cargo2 then
            zone_cargo2 = cargo2
            if B738DR_zone_cargo2_payload ~= nil then B738DR_zone_cargo2_payload = cargo2 end
        end
    end
    local zones = { zone1_pax, zone2_pax, zone3_pax, zone4_pax, zone5_pax }
    local passenger_weights = {
        B738DR_std_pax_weight[0], B738DR_std_pax_weight[1], B738DR_std_pax_weight[2]
    }
    local cabin_crew = B738DR_fa_fwd_kg + B738DR_fa_aft_kg
    return core.payload_targets(
        zones, passenger_weights, cargo1, cargo2, cabin_crew,
        B738DR_galley_fwd_kg, B738DR_galley_aft_kg
    )
end

local function prediction_stations()
    if B738DR_ext_payload ~= 0 then return current_stations() end
    return selected_stations()
end

local function refresh_reference_lemac(data)
    local current_model_zfw = core.cg_z(
        data.empty_mass_kg, data.empty_cg_z_m, current_stations(), data.stations, nil, data.tanks
    )
    local zfw_offset = simDR_levelup_ng_zfw_cg_offset_z
    if not current_model_zfw or not zfw_offset then
        cached_lemac_z_m = nil
        return nil
    end
    cached_lemac_z_m = core.derive_lemac(
        current_model_zfw, simDR_cg_z_mac or 0, simDR_cg_xp12 or 0, zfw_offset, data.mac_m
    )
    return cached_lemac_z_m
end

local function reference_lemac(data)
    -- Never recalibrate after writing stations against a pre-write XP offset.
    return cached_lemac_z_m
end

local function mac_for(data, stations, fuel)
    if B738DR_ext_payload == 0 and not core.validate_station_masses(stations, data.stations) then
        return 0
    end
    local cg_z = core.cg_z(
        data.empty_mass_kg, data.empty_cg_z_m, stations, data.stations, fuel, data.tanks
    )
    if not cg_z then return 0 end
    local lemac_z_m = reference_lemac(data)
    if not lemac_z_m then return 0 end
    local mac = core.mac_from_lemac(cg_z, lemac_z_m, data.mac_m)
    if not mac or mac < 0 or mac > 100 then return 0 end
    return mac
end

local function actual_fuel()
    return {
        simDR_fuel_tank_weight_kg[0] or 0,
        simDR_fuel_tank_weight_kg[1] or 0,
        simDR_fuel_tank_weight_kg[2] or 0,
    }
end

local function refresh_weight_contract(data, stations)
    local service_mass = stations[8] + stations[9]
    full_crew_weight_f = stations[8]
    full_crew_weight_r = stations[9]
    full_crew_weight = service_mass
    crew_weight_f_req = stations[8]
    crew_weight_r_req = stations[9]
    cargo1_weight_req = stations[1]
    cargo2_weight_req = stations[2]
    for zone = 1, 5 do zone_weight_req[zone] = stations[zone + 2] end
    B738DR_oew_kg = data.empty_mass_kg + service_mass
    req_payload_weight = core.total_mass(stations)
end

local function validate_or_warn(data, stations)
    local valid, index, reason = core.validate_station_masses(stations, data.stations)
    if valid then
        warned_station = nil
        return true
    end
    if warned_station ~= index then
        print(string.format(
            "LevelUp %s W&B: %s (%s); payload station writes inhibited",
            data.label, data.stations[index].name, reason
        ))
        warned_station = index
    end
    return false
end

function M.owns_payload()
    -- An invalid supported aircraft must NOT fall back to stock scalar writers.
    return contracts[B738DR_b737_variant] ~= nil
end

function M.data_for_variant(variant_id)
    if variant_id == B738DR_b737_variant then return active_data() end
    return nil
end

function M.begin_frame()
    local data = read_aircraft(true)
    if data then refresh_reference_lemac(data) end
end

function M.frame_update(prepared)
    if not prepared then M.begin_frame() end
    local data = active_data()
    if not data then return end

    local stations = prediction_stations()
    refresh_weight_contract(data, stations)

    if B738DR_ext_payload == 0 then
        local targets = selected_stations()
        refresh_weight_contract(data, targets)
        if validate_or_warn(data, targets) then
            local step = math.max(0, SIM_PERIOD or 0) * data.station_rate_kg_s
            for index = 1, 9 do
                simDR_payload_stations[index - 1] = core.move_toward(
                    simDR_payload_stations[index - 1] or 0, targets[index], step
                )
            end
        else
            B738DR_calc_to_cg = 0
            return
        end
    end

    local takeoff_mac = M.calc_mac(1)
    if takeoff_mac >= 6 and takeoff_mac <= 36 then
        B738DR_calc_to_cg = takeoff_mac
    else
        B738DR_calc_to_cg = 0
    end
end

function M.update_payload()
    local data = active_data()
    if not M.owns_payload() then return original.update_payload() end
    if not data then return end
    local targets = prediction_stations()
    refresh_weight_contract(data, targets)
    validate_or_warn(data, targets)
end

function M.total_payload_entry(in_entry)
    local data = active_data()
    if not M.owns_payload() then return original.total_payload_entry(in_entry) end
    if not data or B738DR_ext_payload ~= 0 then return end
    original.total_payload_entry(in_entry)
    local targets = selected_stations()
    refresh_weight_contract(data, targets)
    validate_or_warn(data, targets)
end

function M.calc_mac(in_gw_tow)
    local data = active_data()
    if not M.owns_payload() then return original.calc_mac(in_gw_tow) end
    if in_gw_tow == 0 then
        local mac = simDR_cg_z_mac or 0
        return mac, core.clamp(mac, 0, 100)
    end
    if not data then return 0, 0 end
    local fuel
    if B738DR_req_fuel and B738DR_req_fuel > 0 then
        fuel = core.fuel_from_total(B738DR_req_fuel, data.tanks)
    else
        fuel = actual_fuel()
    end
    fuel = core.after_taxi(fuel, data.taxi_fuel_kg)
    local mac = mac_for(data, prediction_stations(), fuel)
    return mac, core.clamp(mac, 0, 100)
end

function M.calc_zfw_mac()
    local data = active_data()
    if not M.owns_payload() then return original.calc_zfw_mac() end
    if not data then return 0 end
    return mac_for(data, prediction_stations(), nil)
end

function M.calc_oew_mac()
    local data = active_data()
    if not M.owns_payload() then return original.calc_oew_mac() end
    if not data then return 0 end
    local source = prediction_stations()
    local service_only = { 0, 0, 0, 0, 0, 0, 0, source[8], source[9] }
    return mac_for(data, service_only, nil)
end

function M.calc_des_mac(fuel_input)
    local data = active_data()
    if not M.owns_payload() then return original.calc_des_mac(fuel_input) end
    if not data then return 0 end
    local fuel = core.fuel_from_total(fuel_input or 0, data.tanks)
    return mac_for(data, prediction_stations(), fuel)
end

function M.calc_gw_cg_shift()
    if not M.owns_payload() then return original.calc_gw_cg_shift() end
    local mac = simDR_cg_z_mac or 0
    return mac, core.clamp(mac, 0, 100)
end

local function fixed_check(original_function, weight_kg, mac)
    local data = active_data()
    if not M.owns_payload() then return original_function(weight_kg, mac) end
    if not data then return false end
    local lemac_z_m = reference_lemac(data)
    if not lemac_z_m then return false end
    return core.within_fixed_envelope(weight_kg, mac, data, lemac_z_m)
end

function M.check_tow(weight_kg, mac) return fixed_check(original.check_tow, weight_kg, mac) end
function M.check_gw(weight_kg, mac) return fixed_check(original.check_gw, weight_kg, mac) end
function M.check_zfw(weight_kg, mac) return fixed_check(original.check_zfw, weight_kg, mac) end
function M.check_lw(weight_kg, mac) return fixed_check(original.check_lw, weight_kg, mac) end

function M.install()
    original.update_payload = update_payload
    original.total_payload_entry = total_payload_entry
    original.calc_mac = calc_mac
    original.calc_zfw_mac = calc_zfw_mac
    original.calc_oew_mac = calc_oew_mac
    original.calc_des_mac = calc_des_mac
    original.calc_gw_cg_shift = calc_gw_cg_shift
    original.check_tow = check_tow
    original.check_gw = check_gw
    original.check_zfw = check_zfw
    original.check_lw = check_lw
    original.after_physics = after_physics
    original.flight_start = flight_start
    original.change_payload_command = B738CMD_change_payload

    update_payload = M.update_payload
    total_payload_entry = M.total_payload_entry
    calc_mac = M.calc_mac
    calc_zfw_mac = M.calc_zfw_mac
    calc_oew_mac = M.calc_oew_mac
    calc_des_mac = M.calc_des_mac
    calc_gw_cg_shift = M.calc_gw_cg_shift
    check_tow = M.check_tow
    check_gw = M.check_gw
    check_zfw = M.check_zfw
    check_lw = M.check_lw
    B738CMD_change_payload = {
        once = function()
            if not M.owns_payload() then original.change_payload_command:once() end
        end,
    }
    after_physics = function()
        -- Read/calibrate before stock graph consumers AND before our writes.
        M.begin_frame()
        original.after_physics()
        M.frame_update(true)
    end
    flight_start = function()
        M.reset_aircraft()
        if original.flight_start then original.flight_start() end
    end
end

M.core = core
M.contracts = contracts
B738_levelup_ng_wb_adapter = M
return M
