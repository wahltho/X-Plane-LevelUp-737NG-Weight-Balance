#!/usr/bin/env python3
"""Partial upstream replay: real input/graph functions, independent simulated XP.

Not a full flight loop or engines-running simulator test. Deliberate feedback
mutations are hypotheses, never evidence that XP actually returns those values.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path
from lupa.lua51 import LuaRuntime

ROOT = Path(__file__).resolve().parents[1]
BASELINE = Path('/Users/wahltho/dev/Zibo Mod/Original/Zibo Mod Original/B738X_XP12_4_05_35/plugins/xlua/scripts/B738.tablet/B738.tablet.lua')
parser = argparse.ArgumentParser()
parser.add_argument('--acf', type=Path, default=Path('/Users/wahltho/Downloads/737_60NG.acf'))
args = parser.parse_args()
source = BASELINE.read_text()
fields = dict(re.findall(r'^P (\S+) (.*)$', args.acf.read_text(), re.M))
def acf(name):
    return float(fields['acf/' + name])

def body(name):
    match = re.search(r'^function ' + re.escape(name) + r'\(.*?(?=^function |\Z)', source, re.M | re.S)
    assert match, name
    return match.group()

FUNCTIONS = ('update_payload', 'total_payload_entry', 'fill_zone_weight_req',
             'B738_numpad_enter_CMDhandler', 'activate_numpad', 'cmd_fuel_cg',
             'num_pages', 'page_fuel_cg', 'calc_mac_DR', 'calc_mac',
             'calc_zfw_mac', 'calc_oew_mac', 'calc_des_mac', 'calc_gw_cg_shift',
             'check_tow', 'check_gw', 'check_zfw', 'check_lw')
stock = '\n'.join(body(name) for name in FUNCTIONS)
after = body('after_physics')
start = after.index('\tif cor_time > 3 then')
end = after.index('\tcor_time = cor_time + 1', start) + len('\tcor_time = cor_time + 1')
publication = after[start:end]
LB, FT = 0.45359237, 0.3048
empty, ref, mac = acf('_m_empty') * LB, acf('_cgZ') * FT, acf('_average_mac_acf') * FT
# Synthetic independent datum, NOT an asserted real -600 LEMAC.
lemac = ref - 0.22 * mac
arms = [acf(f'_fixed_ref/{i},2') * FT for i in range(9)]
caps = [acf('_m_fuel_max_tot') * LB * acf(f'_tank_rat/{i}') for i in range(3)]
tank_empty = [acf(f'_tank_xyz/{i},2') * FT for i in range(3)]
tank_full = [acf(f'_tank_xyz_full/{i},2') * FT for i in range(3)]

def centroid(stations, fuel):
    mass = empty + sum(stations) + sum(fuel)
    moment = empty * ref + sum(w * z for w, z in zip(stations, arms))
    for i, w in enumerate(fuel):
        moment += w * (tank_empty[i] + (tank_full[i] - tank_empty[i]) * w / caps[i])
    return moment / mass

def percent(z):
    return (z - lemac) / mac * 100

def run(case, center=0, service=0):
    lua = LuaRuntime(unpack_returned_tuples=True)
    g = lua.globals()
    def table(values):
        return lua.table_from(dict(enumerate(values)))
    g.package_root = str(ROOT)
    g.file_path = str(args.acf.parent)
    live = {
        'sim/aircraft/view/acf_relative_path': str(args.acf),
        'sim/aircraft/weight/acf_m_empty': empty,
        'sim/aircraft/weight/acf_m_max': acf('_m_max') * LB,
        'sim/aircraft/weight/acf_cgZ_original': acf('_cgZ'),
        'sim/aircraft/weight/acf_m_fuel_tot': acf('_m_fuel_max_tot') * LB,
        'sim/aircraft/weight/acf_stations_ref_z': table([
            z if case == 'absolute_station_arms' else (z - ref) / FT if case == 'feet_station_arms' else z - ref
            for z in arms]),
        'sim/aircraft/weight/acf_m_station_max': table([acf(f'_fixed_max/{i}') * LB for i in range(9)]),
        'sim/aircraft/overflow/acf_tank_rat': table([acf(f'_tank_rat/{i}') for i in range(9)]),
        'sim/aircraft/overflow/acf_tank_Z': table([z - ref for z in tank_empty]),
        'sim/aircraft/overflow/acf_tank_Z_full': table([z - ref for z in tank_full]),
        'sim/flightmodel2/misc/zfw_cg_offset_z': 0,
    }
    # Actual wrapper-vs-module-global semantics, not numeric find_dataref stubs.
    g.read_live = lambda name: live[name]
    lua.execute('''
local properties = {}
setmetatable(_G, {
 __newindex = function(t,k,v)
  if type(v) == "table" and v.__dref then properties[k] = v.__dref
  else rawset(t,k,v) end
 end,
 __index = function(t,k) if properties[k] then return read_live(properties[k]) end end
})
function find_dataref(name) return {__dref=name} end
local real_dofile = dofile
function dofile(path)
 if path:match("^B738%.tablet_levelup_ng_wb_") then real_dofile(package_root .. "/" .. path)
 else real_dofile(path) end
end
B738DR_b737_variant=3; B738DR_ext_payload=0; B738DR_fmc_units=0
B738DR_req_fuel=0; B738DR_dest_fuel=-1; B738DR_dev_tune=0
B738DR_oew_cg=0; B738DR_calc_to_cg=0; B738DR_auto_flight=0
B738DR_pax_layout=4; B738DR_73x=0; B738DR_autogate_nearest=0
B738DR_std_pax_num={[0]=24,30,24,30,30}
B738DR_std_pax_weight={[0]=84,75,35}
B738DR_fa_fwd_kg=0; B738DR_fa_aft_kg=0
B738DR_galley_fwd_kg=0; B738DR_galley_aft_kg=0
B738DR_tab_line_manip={}; B738DR_tab_perf_manip={}; B738DR_zone_arm={}
zone1_pax={0,0,0}; zone2_pax={0,0,0}; zone3_pax={0,0,0}
zone4_pax={0,0,0}; zone5_pax={0,0,0}; zone_weight_req={0,0,0,0,0}
zone_cargo1=0; zone_cargo2=0; full_crew_weight=0
full_crew_weight_f=0; full_crew_weight_r=0; req_payload_weight=0
simDR_payload_stations={[0]=0,0,0,0,0,0,0,0,0}
line={}; line_c={}; line_s={}; line_g={}; line_a={}
page=1; max_page=4; gw_tow_state=1; cor_time=0
KGS_LBS=2.2046226218487757; SIM_PERIOD=0.1
temp_wing_tank_kg=3907; temp_max_fuel_kg=20876
B738CMD_change_payload={once=function() error("stock scalar writer called") end}
function flight_start() end -- startup systems outside this partial replay
''')
    lua.execute(stock)
    # Unmodified stock CG publisher + page consumer; unrelated after_physics
    # systems deliberately excluded and listed in the fidelity boundary.
    lua.execute('function after_physics()\n' + publication + '\ncalc_mac_DR()\npage_fuel_cg()\nend')
    lua.execute('dofile("B738.tablet_levelup_ng_wb_adapter.lua"); B738_levelup_ng_wb_adapter.install()')
    fuel = [3000, center, 3000]
    g.simDR_fuel_tank_weight_kg = table(fuel)
    g.B738DR_fa_fwd_kg = service / 2
    g.B738DR_fa_aft_kg = service / 2
    g.B738DR_oew_kg = empty
    history = []
    for tick in range(360):
        masses = [g.simDR_payload_stations[i] for i in range(9)]
        gross_z, zfw_z = centroid(masses, fuel), centroid(masses, [0,0,0])
        feedback = (percent(gross_z), gross_z - ref, zfw_z - ref)
        history.append(feedback)
        delivered = history[-2] if case == 'one_frame_lag' and tick else feedback
        g.simDR_cg_z_mac, g.simDR_cg_xp12 = delivered[:2]
        live['sim/flightmodel2/misc/zfw_cg_offset_z'] = (
            0 if case == 'zero_zfw_offset' else delivered[2])
        g.simDR_payload_weight = sum(masses)
        if tick == 30:
            g.cmd_fuel_cg(1)
            g.cmd_fuel_cg(18)
            # Value presented to the actual Enter handler by the Pax button.
            g.tab_numpad_val = 'P100'
            g.B738DR_tab_numpad_spec1 = 0
            g.B738_numpad_enter_CMDhandler(0, 0)
            assert sum(g[f'zone{i}_pax'][1] for i in range(1,6)) == 100
            assert [g[f'zone{i}_pax'][1] for i in range(1,6)] == [18,22,18,22,20]
            g.page = 1 # return/navigation control outside partial replay
        if tick == 270:
            g.cmd_fuel_cg(7)
            assert g.page == 3
        g.after_physics()
    masses = [g.simDR_payload_stations[i] for i in range(9)]
    assert masses == [0,0,1512,1848,1512,1848,1680,service/2,service/2]
    # Independent taxi mass subtraction; no production helper used as oracle.
    forecast_fuel = list(fuel)
    remaining = 226.8
    burnt = min(center, remaining)
    forecast_fuel[1] -= burnt
    remaining -= burnt
    forecast_fuel[0] -= remaining / 2
    forecast_fuel[2] -= remaining / 2
    expected_to = percent(centroid(masses, forecast_fuel))
    expected_oew = percent(centroid([0]*7 + [service/2, service/2], [0,0,0]))
    expected_zfw = percent(centroid(masses, [0,0,0]))
    result = dict(case=case, center_kg=center, service_kg=service,
        gw=g.simDR_cg_z_mac, to=g.B738DR_calc_to_cg, oew=g.B738DR_oew_cg,
        expected_to=expected_to, expected_oew=expected_oew,
        zfw_unclamped=g.calc_zfw_mac(), expected_zfw=expected_zfw)
    if case in ('consistent', 'one_frame_lag'):
        for actual, expected in ((result['to'], expected_to), (result['oew'], expected_oew),
                                 (result['zfw_unclamped'], expected_zfw)):
            assert abs(actual - expected) < 1e-9, result
    return result

print(json.dumps({'fidelity': 'partial upstream replay; simulated XP, no actual engines-running startup',
                  'upstream_sha256': hashlib.sha256(BASELINE.read_bytes()).hexdigest(),
                  'acf_sha256': hashlib.sha256(args.acf.read_bytes()).hexdigest()}))
for center in (0, 100, 500):
    for service in (0, 675):
        print(json.dumps(run('consistent', center, service)))
for case in ('one_frame_lag', 'absolute_station_arms', 'feet_station_arms', 'zero_zfw_offset'):
    print(json.dumps(run(case)))
print('PASS: six settled baseline cases plus one-frame lag; mutations are diagnostic only')
