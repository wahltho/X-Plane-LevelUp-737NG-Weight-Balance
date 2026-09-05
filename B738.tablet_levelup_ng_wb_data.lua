-- BEGIN CUSTOM: loaded-aircraft W&B input contract.
-- Policy only: no variant geometry, mass, or capacity is hard-coded here.
local M = {}
for id, row in pairs({
    [3] = { "737-600", "737_60NG.acf", "Galley A", "Right Wing" },
    [2] = { "737-700", "737_70NG.acf", "Galley R", "Right Main" },
    [0] = { "737-800", "737_80NG.acf", "Galley A", "Right Main" },
    [1] = { "737-900", "737_90NG.acf", "Galley A", "Right Main" },
    [4] = { "737-900ER", "737_9ENG.acf", "Galley A", "Right Main" },
}) do
    M[id] = {
        variant_id = id, label = row[1], acf_name = row[2],
        station_names = { "Cargo1", "Cargo2", "Zone 1", "Zone 2", "Zone 3",
            "Zone 4", "Zone 5", "Galley F", row[3] },
        tank_names = { "Left Main", "Center Wing", row[4] },
        -- Existing loading/fuel policies, not values inferred from geometry.
        taxi_fuel_kg = 226.8, station_rate_kg_s = 222,
    }
end

local function finite(value)
    return type(value) == "number" and value == value and math.abs(value) < math.huge
end
M.finite = finite

-- Only metadata not exposed as a usable global DataRef is read from disk.
-- Parse once per aircraft load/path/variant, never in the per-frame loop.
function M.read_metadata(path, policy)
    local file = io.open(path, "r")
    if not file then return nil, "cannot read loaded ACF metadata" end
    local fields = {}
    for line in file:lines() do
        local key, value = line:match("^P (acf/[^%s]+) (.*)")
        if key then
            if fields[key] then file:close(); return nil, "duplicate ACF field: " .. key end
            fields[key] = value:gsub("%s+$", "")
        end
    end
    file:close()
    for key, count in pairs({
        ["_fixed_max/count"] = 9, ["_fixed_name/count"] = 9,
        ["_fixed_ref/i_count"] = 9, ["_fixed_ref/j_count"] = 3,
        ["_fixed_role/count"] = 9, ["_tank_name/count"] = 9,
        ["_tank_rat/count"] = 9, ["_tank_xyz/i_count"] = 9,
        ["_tank_xyz/j_count"] = 3, ["_tank_xyz_full/i_count"] = 9,
        ["_tank_xyz_full/j_count"] = 3,
    }) do
        if tonumber(fields["acf/" .. key]) ~= count then return nil, "unsupported ACF array: " .. key end
    end
    for i = 1, 9 do
        if fields["acf/_fixed_name/" .. (i - 1)] ~= policy.station_names[i] then
            return nil, "station order/name mismatch at index " .. (i - 1)
        end
    end
    for i = 1, 3 do
        if fields["acf/_tank_name/" .. (i - 1)] ~= policy.tank_names[i] then
            return nil, "tank order/name mismatch at index " .. (i - 1)
        end
    end
    local mac = tonumber(fields["acf/_average_mac_acf"])
    local fwd = tonumber(fields["acf/_cgZ_fwd"])
    local aft = tonumber(fields["acf/_cgZ_aft"])
    if not finite(mac) or mac <= 0 or not finite(fwd) or not finite(aft) or fwd >= aft then
        return nil, "invalid MAC or fixed CG limits"
    end
    return { mac_m = mac * 0.3048, cg_fwd_z_m = fwd * 0.3048, cg_aft_z_m = aft * 0.3048 }
end

-- A complete immutable-for-the-frame snapshot. Runtime masses are kg,
-- original CG is ft, station arms are absolute m, tank endpoints are offset m.
-- Tank units verified by the native X-Plane 12.4.3-r2 sweep (2026-08-20).
function M.snapshot(policy, metadata, input)
    if not metadata then return nil, "ACF metadata unavailable" end
    for _, key in ipairs({ "empty_kg", "max_kg", "reference_ft", "fuel_kg" }) do
        if not finite(input[key]) then return nil, "invalid DataRef: " .. key end
    end
    if input.empty_kg <= 0 or input.max_kg <= input.empty_kg or input.fuel_kg <= 0 then
        return nil, "invalid aircraft mass/capacity"
    end
    local data = {
        label = policy.label, variant_id = policy.variant_id,
        mac_m = metadata.mac_m, cg_fwd_z_m = metadata.cg_fwd_z_m,
        cg_aft_z_m = metadata.cg_aft_z_m, empty_mass_kg = input.empty_kg,
        empty_cg_z_m = input.reference_ft * 0.3048, max_gross_mass_kg = input.max_kg,
        taxi_fuel_kg = policy.taxi_fuel_kg, station_rate_kg_s = policy.station_rate_kg_s,
        stations = {}, tanks = {},
    }
    local total_ratio = 0
    for i = 0, 8 do
        local arm, maximum, ratio = input.station_z[i], input.station_max[i], input.tank_rat[i]
        if not finite(arm) or not finite(maximum) or maximum <= 0 then
            return nil, "invalid station geometry/capacity at index " .. i
        end
        if not finite(ratio) or ratio < 0 or (i < 3 and ratio <= 0) or (i >= 3 and ratio ~= 0) then
            return nil, "unsupported tank layout at index " .. i
        end
        data.stations[i + 1] = { name = policy.station_names[i + 1], arm_m = arm, max_kg = maximum }
        total_ratio = total_ratio + ratio
        if i < 3 then
            local empty, full = input.tank_empty[i], input.tank_full[i]
            if not finite(empty) or not finite(full) then return nil, "invalid tank endpoints" end
            data.tanks[i + 1] = { name = policy.tank_names[i + 1],
                empty_arm_m = data.empty_cg_z_m + empty,
                full_arm_m = data.empty_cg_z_m + full, max_kg = input.fuel_kg * ratio }
        end
    end
    -- Existing prediction policy needs symmetric wing capacities.
    if math.abs(total_ratio - 1) > 0.000001 or
        math.abs(input.tank_rat[0] - input.tank_rat[2]) > 0.00000001 then
        return nil, "unsupported fuel capacity ratios"
    end
    return data
end

B738_levelup_ng_wb_data = M
return M
-- END CUSTOM
