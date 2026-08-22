local package_root = arg[0]:match("^(.*)/tests/") or "."
local core = dofile(package_root .. "/B738.tablet_levelup_ng_wb_core.lua")
local contracts = dofile(package_root .. "/B738.tablet_levelup_ng_wb_data.lua")

local function near(actual, expected, tolerance, label)
    assert(math.abs(actual - expected) <= tolerance,
        string.format("%s: %.12f != %.12f", label, actual, expected))
end

local zones = {
    { 10, 2, 1 }, { 12, 1, 0 }, { 14, 0, 1 }, { 3, 0, 0 }, { 9, 1, 1 },
}
local targets = core.payload_targets(zones, { 84, 35, 10 }, 1000, 500, 450, 100, 125)
local expected_targets = { 1000, 500, 920, 1043, 1186, 252, 801, 325, 350 }
for i = 1, 9 do near(targets[i], expected_targets[i], 1e-12, "target " .. i) end

local station_masses = { 1000, 500, 2000, 1800, 1600, 300, 1200, 200, 250 }
local fuel_masses = { 3000, 5000, 3000 }

local data700 = contracts[2]
local z700, mass700, moment700 = core.cg_z(
    data700.empty_mass_kg, data700.empty_cg_z_m, station_masses, data700.stations, fuel_masses, data700.tanks
)
-- Independent kg-m control results, calculated outside the production core.
near(mass700, 57497.989808975704, 1e-9, "700 gross mass")
near(moment700, 840784.9793934701, 1e-6, "700 gross moment")
near(z700, 14.62285868056938, 1e-12, "700 cg z")

local data800 = contracts[0]
local z800, mass800, moment800 = core.cg_z(
    data800.empty_mass_kg, data800.empty_cg_z_m, station_masses, data800.stations, fuel_masses, data800.tanks
)
near(mass800, 61360.0702918748, 1e-9, "800 gross mass")
near(moment800, 1104667.7681431761, 1e-6, "800 gross moment")
near(z800, 18.003039482982054, 1e-12, "800 cg z")

local data900 = contracts[1]
local z900, mass900, moment900 = core.cg_z(
    data900.empty_mass_kg, data900.empty_cg_z_m, station_masses, data900.stations, fuel_masses, data900.tanks
)
near(mass900, 62750.766354600004, 1e-9, "900 gross mass")
near(moment900, 1225916.149216837, 1e-6, "900 gross moment")
near(z900, 19.53627374507706, 1e-12, "900 cg z")

local data900er = contracts[4]
local z900er, mass900er, moment900er = core.cg_z(
    data900er.empty_mass_kg, data900er.empty_cg_z_m, station_masses, data900er.stations,
    fuel_masses, data900er.tanks
)
near(mass900er, 64526.58048315, 1e-9, "900ER gross mass")
near(moment900er, 1269754.2588752897, 1e-6, "900ER gross moment")
near(z900er, 19.678003225459374, 1e-12, "900ER cg z")
near(core.tank_arm(data900er.tanks[1], data900er.tanks[1].max_kg * 0.5),
    69.5 * 0.3048, 1e-12, "900ER half-full main arm")

-- X-Plane's cg_offset_z values share an offset datum with each other, but not
-- the ACF's absolute station coordinates. Derive an ACF-space LEMAC through
-- the current ZFW state before converting predictions or fixed limits.
local zfw_mac = core.zfw_mac_from_offsets(20.0, 0.12, 0.006079854442879007, data700.mac_m)
near(zfw_mac, 17.50700001283644, 1e-12, "700 X-Plane ZFW %MAC")
local lemac700, derived_zfw_mac = core.derive_lemac(
    14.7, 20.0, 0.12, 0.006079854442879007, data700.mac_m
)
near(lemac700, 13.9, 1e-12, "700 derived ACF-space LEMAC")
near(derived_zfw_mac, zfw_mac, 1e-12, "700 derived ZFW %MAC")

local distributed700 = core.fuel_from_total(10000, data700.tanks)
near(distributed700[1], 3907.0613206122184, 1e-9, "700 left fuel")
near(distributed700[2], 2185.877358775563, 1e-9, "700 center fuel")
near(distributed700[3], 3907.0613206122184, 1e-9, "700 right fuel")
local distributed800 = core.fuel_from_total(10000, data800.tanks)
near(distributed800[1], 3907.0614902557695, 1e-9, "800 left fuel")
near(distributed800[2], 2185.877019488461, 1e-9, "800 center fuel")
near(distributed800[3], 3907.0614902557695, 1e-9, "800 right fuel")
local distributed900er = core.fuel_from_total(10000, data900er.tanks)
near(distributed900er[1], 4454.187391418068, 1e-9, "900ER left fuel")
near(distributed900er[2], 1091.6252171638644, 1e-9, "900ER center fuel")
near(distributed900er[3], 4454.187391418068, 1e-9, "900ER right fuel")

local zfw800 = core.cg_z(
    data800.empty_mass_kg, data800.empty_cg_z_m, station_masses, data800.stations, nil, data800.tanks
)
local takeoff800 = core.after_taxi(core.fuel_from_total(12000, data800.tanks), data800.taxi_fuel_kg)
local tow800 = core.cg_z(
    data800.empty_mass_kg, data800.empty_cg_z_m, station_masses, data800.stations, takeoff800, data800.tanks
)
local landing800 = core.cg_z(
    data800.empty_mass_kg, data800.empty_cg_z_m, station_masses, data800.stations,
    { 1500, 0, 1500 }, data800.tanks
)
near((tow800 - zfw800) / data800.mac_m * 100, 3.470749546785, 1e-12, "800 takeoff fuel shift")
near((landing800 - zfw800) / data800.mac_m * 100, 1.975618204414, 1e-12, "800 landing fuel shift")

local after_taxi = core.after_taxi({ 3000, 500, 3000 }, 226.8)
near(after_taxi[1], 3000, 1e-12, "taxi left")
near(after_taxi[2], 273.2, 1e-12, "taxi center")
near(after_taxi[3], 3000, 1e-12, "taxi right")

assert(core.validate_station_masses(expected_targets, data700.stations))
assert(core.validate_station_masses(expected_targets, data800.stations))
local invalid700, index700 = core.validate_station_masses({ 1927, 0, 0, 0, 0, 0, 0, 0, 0 }, data700.stations)
assert(not invalid700 and index700 == 1, "700 ACF cargo maximum must remain authoritative")
local invalid800, index800 = core.validate_station_masses({ 3560, 0, 0, 0, 0, 0, 0, 0, 0 }, data800.stations)
assert(not invalid800 and index800 == 1, "800 rounded ACF cargo maximum must remain authoritative")
local invalid_galley, galley_index = core.validate_station_masses({ 0, 0, 0, 0, 0, 0, 0, 1385.6, 0 }, data800.stations)
assert(not invalid_galley and galley_index == 8, "800 combined galley/crew maximum must remain authoritative")
local normalized1, normalized2 = core.normalize_cargo(3560, 4850, data900er.stations)
near(normalized1, 3559.79291976, 1e-9, "900ER cargo1 normalization")
near(normalized2, 4762.719885, 1e-9, "900ER cargo2 normalization")
local redistributed1, redistributed2 = core.normalize_cargo(3000, 4850, data900er.stations)
near(redistributed1 + redistributed2, 7850, 1e-9, "900ER normalization preserves feasible total")
near(redistributed2, 4762.719885, 1e-9, "900ER normalization respects aft maximum")

local fwd700, aft700 = core.fixed_limit_macs(data700, lemac700)
near(fwd700, 10.581046579618961, 1e-12, "700 fixed forward limit")
near(aft700, 35.59417284795903, 1e-12, "700 fixed aft limit")
assert(core.within_fixed_envelope(60000, 12, data700, lemac700))
assert(not core.within_fixed_envelope(60000, 36, data700, lemac700))

local fwd800, aft800 = core.fixed_limit_macs(data800, 17.4)
near(fwd800, 5.225307502248546, 1e-12, "800 fixed forward limit")
near(aft800, 31.705880339220826, 1e-12, "800 fixed aft limit")
assert(core.within_fixed_envelope(70000, 20, data800, 17.4))
assert(not core.within_fixed_envelope(80000, 20, data800, 17.4))

print("PASS: 700/800/900/900ER stations, independent mass/moment, variable fuel arms, taxi and fixed envelopes")
