-- Read-only integration check against author ACFs. No aircraft modification.
local root = arg[0]:match("^(.*)/tests/") or "."
local aircraft_root = assert(arg[1], "pass the directory containing all five author ACFs")
local data = dofile(root .. "/B738.tablet_levelup_ng_wb_data.lua")
local core = dofile(root .. "/B738.tablet_levelup_ng_wb_core.lua")
for _, variant in ipairs({3, 2, 0, 1, 4}) do
    local policy = data[variant]
    local path = aircraft_root .. "/" .. policy.acf_name
    local metadata = assert(data.read_metadata(path, policy))
    local numbers = {}
    for line in io.lines(path) do
        local key, value = line:match("^P (acf/[^%s]+) (.*)")
        if key then numbers[key] = tonumber(value) end
    end
    local function n(key) return assert(numbers["acf/" .. key], key) end
    -- Simulated native DataRef units, independently derived from the actual
    -- disk input. This is not a running-X-Plane DataRef observation.
    local input = {
        empty_kg = n("_m_empty") * 0.45359237, max_kg = n("_m_max") * 0.45359237,
        reference_ft = n("_cgZ"), fuel_kg = n("_m_fuel_max_tot") * 0.45359237,
        station_z = {}, station_max = {}, tank_rat = {}, tank_empty = {}, tank_full = {},
    }
    for i = 0, 8 do
        input.station_z[i] = n("_fixed_ref/" .. i .. ",2") * 0.3048
        input.station_max[i] = n("_fixed_max/" .. i) * 0.45359237
        input.tank_rat[i] = n("_tank_rat/" .. i)
        input.tank_empty[i] = (n("_tank_xyz/" .. i .. ",2") - input.reference_ft) * 0.3048
        input.tank_full[i] = (n("_tank_xyz_full/" .. i .. ",2") - input.reference_ft) * 0.3048
    end
    local snapshot = assert(data.snapshot(policy, metadata, input))
    local stations, fuel = {}, {}
    -- Oracle entirely in ACF lb/ft, converted only at the final comparison.
    local mass_lb, moment_lbft = n("_m_empty"), n("_m_empty") * n("_cgZ")
    for i = 0, 8 do
        local load_lb = n("_fixed_max/" .. i) * (i + 1) / 20
        stations[i + 1] = load_lb * 0.45359237
        mass_lb = mass_lb + load_lb
        moment_lbft = moment_lbft + load_lb * n("_fixed_ref/" .. i .. ",2")
    end
    for i = 0, 2 do
        local fraction = (i + 1) / 4
        local load_lb = n("_m_fuel_max_tot") * n("_tank_rat/" .. i) * fraction
        local arm_ft = n("_tank_xyz/" .. i .. ",2") +
            (n("_tank_xyz_full/" .. i .. ",2") - n("_tank_xyz/" .. i .. ",2")) * fraction
        fuel[i + 1] = load_lb * 0.45359237
        mass_lb = mass_lb + load_lb
        moment_lbft = moment_lbft + load_lb * arm_ft
    end
    local cg, mass, moment = core.cg_z(snapshot.empty_mass_kg, snapshot.empty_cg_z_m,
        stations, snapshot.stations, fuel, snapshot.tanks)
    assert(math.abs(mass - mass_lb * 0.45359237) < 1e-8)
    assert(math.abs(moment - moment_lbft * 0.45359237 * 0.3048) < 1e-7)
    assert(math.abs(cg - moment_lbft / mass_lb * 0.3048) < 1e-10)
    print("PASS loaded ACF metadata/units/independent moment: " .. policy.acf_name)
end
