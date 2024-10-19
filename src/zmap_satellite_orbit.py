import krpc
import time
import math
import json

# To be used with the Zmap Satellite rocket found in the stock ksp library

conn = krpc.connect('zmap')
vessel = conn.space_center.active_vessel

def launch():
    vessel.auto_pilot.target_pitch_and_heading(90, 90)
    vessel.auto_pilot.engage()
    vessel.control.throttle = 0.35
    vessel.control.activate_next_stage() # engines
    vessel.control.activate_next_stage() # clamps
    print('Launch')

def handle_solid_booster_separation():
    # Booster separations
    fuel_amount = conn.get_call(vessel.resources.amount, 'SolidFuel')
    expr = conn.krpc.Expression.less_than(
        conn.krpc.Expression.call(fuel_amount),
        conn.krpc.Expression.constant_float(0.1))
    booster_separation_event = conn.krpc.add_event(expr)
    with booster_separation_event.condition:
        booster_separation_event.wait()
    vessel.control.activate_next_stage() # separate boosters
    vessel.control.throttle = 0.75 # pump up main engine
    print('Booster separation')

def perform_gravity_turn():
    # Perform gravity turn at 10k
    mean_altitude = conn.get_call(getattr, vessel.flight(), 'mean_altitude')
    expr = conn.krpc.Expression.greater_than(
        conn.krpc.Expression.call(mean_altitude),
        conn.krpc.Expression.constant_double(10000))
    gravity_turn_event = conn.krpc.add_event(expr)
    with gravity_turn_event.condition:
        gravity_turn_event.wait()
    vessel.auto_pilot.target_pitch_and_heading(60, 90)
    vessel.control.throttle = 0.85
    print('Gravity turn')

def cut_at_apo_reached():
    # Cut engines at desired apoapsis height of 78km
    # We go a little higher than 75km because our weight changes after separation
    apoapsis_altitude = conn.get_call(getattr, vessel.orbit, 'apoapsis_altitude')
    expr = conn.krpc.Expression.greater_than(
        conn.krpc.Expression.call(apoapsis_altitude),
        conn.krpc.Expression.constant_double(78000))
    apoapsis_reached_event = conn.krpc.add_event(expr)
    with apoapsis_reached_event.condition:
        apoapsis_reached_event.wait()
    vessel.control.throttle = 0

def separate_main_booster():
    print('Separating main booster')
    vessel.control.activate_next_stage()
    time.sleep(1)
    vessel.control.activate_next_stage()
    time.sleep(3)
    vessel.auto_pilot.target_pitch_and_heading(0, 90)


def perform_orbital_burn():
    # Perform orbital burn at 75km
    mean_altitude = conn.get_call(getattr, vessel.flight(), 'mean_altitude')
    expr = conn.krpc.Expression.greater_than(
        conn.krpc.Expression.call(mean_altitude),
        conn.krpc.Expression.constant_double(75000))
    orbital_burn_event = conn.krpc.add_event(expr)
    with orbital_burn_event.condition:
        orbital_burn_event.wait()
        
    print('Orbital burn!')
    vessel.auto_pilot.target_pitch_and_heading(0, 90)
    vessel.control.throttle = 1
    vessel.control.activate_next_stage()


def plan_circularization_burn():
    # Plan circularization burn (using vis-viva equation)
    print('Planning circularization burn')
    mu = vessel.orbit.body.gravitational_parameter
    r = vessel.orbit.apoapsis
    a1 = vessel.orbit.semi_major_axis
    a2 = r
    v1 = math.sqrt(mu*((2./r)-(1./a1)))
    v2 = math.sqrt(mu*((2./r)-(1./a2)))
    delta_v = v2 - v1
    print(mu, r, a1, v1, v2, delta_v)

    # Calculate burn time (using rocket equation)
    F = vessel.available_thrust
    Isp = vessel.specific_impulse * 9.82
    m0 = vessel.mass
    m1 = m0 / math.exp(delta_v/Isp)
    flow_rate = F / Isp
    burn_time = (m0 - m1) / flow_rate

    print('Rocket Equation Results:')
    print(json.dumps({
        'Standard gravitational parameter (mu)': mu,
        'Apoapsis (r)': r,
        'Semimajor axis (a1)': a1,
        'Apoapsis (a2)': a2,
        'v1': v1,
        'v2': v2,
        'delta_v': delta_v,
        'Available thrust (F)': F,
        'Specific impulse (Isp)': Isp,
        'Mass (m0)': m0,
        'm1': m1,
        'Flow rate': flow_rate,
        'Burn time': burn_time,
    }, indent=2))

    print(f'Burning for {burn_time} seconds')
    return burn_time


# Main
launch()

handle_solid_booster_separation()

perform_gravity_turn()

cut_at_apo_reached()

separate_main_booster()

perform_orbital_burn()

burn_time = plan_circularization_burn()

time.sleep(burn_time - 0.1)

# Set final controls before returning to manual control
vessel.control.throttle = 0
vessel.control.sas = True
vessel.control.rcs = True
print('Orbit reached')