-- Pure mass-and-moment model.  No X-Plane or Tablet globals are used here.

local M = {}

local function finite(value)
    return type(value) == "number" and value == value and value > -math.huge and value < math.huge
end

function M.clamp(value, low, high)
    if value < low then return low end
    if value > high then return high end
    return value
end

function M.move_toward(current, target, maximum_step)
    if target > current then
        return math.min(target, current + maximum_step)
    end
    return math.max(target, current - maximum_step)
end

function M.payload_targets(zone_counts, passenger_weights, cargo1_kg, cargo2_kg,
                           cabin_crew_kg, galley_fwd_kg, galley_aft_kg)
    local result = { cargo1_kg, cargo2_kg, 0, 0, 0, 0, 0, 0, 0 }
    for zone = 1, 5 do
        local mass = 0
        for category = 1, 3 do
            mass = mass + (zone_counts[zone][category] or 0) * (passenger_weights[category] or 0)
        end
        result[zone + 2] = mass
    end
    local cabin_half = cabin_crew_kg * 0.5
    result[8] = cabin_half + galley_fwd_kg
    result[9] = cabin_half + galley_aft_kg
    return result
end

function M.validate_station_masses(masses, stations)
    for index = 1, #stations do
        local mass = masses[index]
        if not finite(mass) or mass < 0 then
            return false, index, "invalid mass"
        end
        if mass > stations[index].max_kg + 0.001 then
            return false, index, "station maximum exceeded"
        end
    end
    return true
end

function M.total_mass(masses)
    local total = 0
    for index = 1, #masses do total = total + masses[index] end
    return total
end

function M.normalize_cargo(cargo1_kg, cargo2_kg, stations)
    local requested_total = math.max(0, cargo1_kg or 0) + math.max(0, cargo2_kg or 0)
    local total = math.min(requested_total, stations[1].max_kg + stations[2].max_kg)
    local cargo1 = M.clamp(cargo1_kg or 0, 0, stations[1].max_kg)
    local cargo2 = total - cargo1
    if cargo2 > stations[2].max_kg then
        cargo2 = stations[2].max_kg
        cargo1 = total - cargo2
    end
    return cargo1, cargo2
end

function M.tank_arm(tank, mass_kg)
    local empty_arm = tank.empty_arm_m or tank.arm_m
    local full_arm = tank.full_arm_m or tank.arm_m
    if not finite(empty_arm) or not finite(full_arm) or not finite(tank.max_kg) or tank.max_kg <= 0 then
        return nil
    end
    local fraction = M.clamp((mass_kg or 0) / tank.max_kg, 0, 1)
    return empty_arm + (full_arm - empty_arm) * fraction
end

function M.cg_z(empty_mass_kg, empty_cg_z_m, station_masses, stations, fuel_masses, tanks)
    if not finite(empty_mass_kg) or empty_mass_kg <= 0 or not finite(empty_cg_z_m) then return nil end
    for index = 1, 9 do
        if not finite(station_masses[index]) or station_masses[index] < 0 or
            not stations[index] or not finite(stations[index].arm_m) then return nil end
    end
    if fuel_masses then
        for index = 1, 3 do
            if not finite(fuel_masses[index]) or fuel_masses[index] < 0 then return nil end
        end
    end
    local mass = empty_mass_kg
    local moment = empty_mass_kg * empty_cg_z_m
    for index = 1, #stations do
        mass = mass + station_masses[index]
        moment = moment + station_masses[index] * stations[index].arm_m
    end
    if fuel_masses then
        for index = 1, #tanks do
            local arm_m = M.tank_arm(tanks[index], fuel_masses[index])
            if not arm_m then return nil end
            mass = mass + fuel_masses[index]
            moment = moment + fuel_masses[index] * arm_m
        end
    end
    if mass <= 0 then return nil end
    return moment / mass, mass, moment
end

function M.z_to_mac(cg_z_m, anchor_z_m, anchor_mac, mac_m)
    if not finite(cg_z_m) or not finite(anchor_z_m) or not finite(anchor_mac) or mac_m <= 0 then
        return nil
    end
    return anchor_mac + ((cg_z_m - anchor_z_m) / mac_m) * 100.0
end

function M.zfw_mac_from_offsets(current_mac, current_offset_m, zfw_offset_m, mac_m)
    if not finite(current_mac) or not finite(current_offset_m) or not finite(zfw_offset_m) or mac_m <= 0 then
        return nil
    end
    local zfw_mac = current_mac + ((zfw_offset_m - current_offset_m) / mac_m) * 100.0
    if current_mac <= 0 or current_mac > 100 or zfw_mac < 0 or zfw_mac > 100 then return nil end
    return zfw_mac
end

function M.derive_lemac(current_model_zfw_m, current_mac, current_offset_m, zfw_offset_m, mac_m)
    if not finite(current_model_zfw_m) then return nil, nil end
    local zfw_mac = M.zfw_mac_from_offsets(current_mac, current_offset_m, zfw_offset_m, mac_m)
    if not zfw_mac then return nil, nil end
    return current_model_zfw_m - (zfw_mac / 100.0) * mac_m, zfw_mac
end

function M.mac_from_lemac(cg_z_m, lemac_z_m, mac_m)
    if not finite(cg_z_m) or not finite(lemac_z_m) or mac_m <= 0 then return nil end
    return ((cg_z_m - lemac_z_m) / mac_m) * 100.0
end

function M.fuel_from_total(total_kg, tanks)
    local fuel = { 0, 0, 0 }
    local remaining = math.max(0, total_kg or 0)
    local wing_total = tanks[1].max_kg + tanks[3].max_kg
    local wing_fuel = math.min(remaining, wing_total)
    fuel[1] = wing_fuel * 0.5
    fuel[3] = wing_fuel * 0.5
    remaining = remaining - wing_fuel
    fuel[2] = math.min(remaining, tanks[2].max_kg)
    return fuel
end

function M.after_taxi(fuel, taxi_kg)
    local result = { math.max(0, fuel[1] or 0), math.max(0, fuel[2] or 0), math.max(0, fuel[3] or 0) }
    local remaining = math.max(0, taxi_kg or 0)
    local center_burn = math.min(result[2], remaining)
    result[2] = result[2] - center_burn
    remaining = remaining - center_burn
    if remaining > 0 then
        local half = remaining * 0.5
        local left_burn = math.min(result[1], half)
        local right_burn = math.min(result[3], half)
        result[1] = result[1] - left_burn
        result[3] = result[3] - right_burn
        remaining = remaining - left_burn - right_burn
        if remaining > 0 then
            local extra_left = math.min(result[1], remaining)
            result[1] = result[1] - extra_left
            remaining = remaining - extra_left
        end
        if remaining > 0 then
            result[3] = math.max(0, result[3] - remaining)
        end
    end
    return result
end

function M.fixed_limit_macs(data, lemac_z_m)
    local fwd = M.mac_from_lemac(data.cg_fwd_z_m, lemac_z_m, data.mac_m)
    local aft = M.mac_from_lemac(data.cg_aft_z_m, lemac_z_m, data.mac_m)
    if not fwd or not aft then return nil, nil end
    return math.min(fwd, aft), math.max(fwd, aft)
end

function M.within_fixed_envelope(weight_kg, mac, data, lemac_z_m)
    local fwd, aft = M.fixed_limit_macs(data, lemac_z_m)
    if not fwd or not finite(weight_kg) or not finite(mac) then return false end
    return weight_kg > 0 and weight_kg <= data.max_gross_mass_kg and mac >= fwd and mac <= aft
end

B738_levelup_ng_wb_core = M
return M
