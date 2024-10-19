import krpc
import time
import math
import json

# To be used with the Orbiter A1 stock KSP craft.
# Trying to hop to island

conn = krpc.connect('kerbal_x')
vessel = conn.space_center.active_vessel

def launch():
    vessel.auto_pilot.target_pitch_and_heading(90, 90)
    vessel.auto_pilot.engage()
    vessel.control.throttle = 1 # must go faster
    vessel.control.activate_next_stage() # engines
    print('Launch')

def handle_booster_separations():
    # Booster separations
    active_engines = len([e for e in vessel.parts.engines if e.active and e.thrust > 0])
    while active_engines > 1:
        for engine in vessel.parts.engines:
            if engine.has_fuel == False:
                vessel.control.activate_next_stage()
                active_engines -= 2 # We're cutting 2 engines at a time
                print('Booster separation')
                break

def until_altitude_reached(alt: int, comparison = 'greater_than'):
    mean_altitude = conn.get_call(getattr, vessel.flight(), 'mean_altitude')
    krpc_expr_comparison = conn.krpc.Expression.greater_than if comparison == 'greater_than' else conn.krpc.Expression.less_than
    expr = krpc_expr_comparison(
        conn.krpc.Expression.call(mean_altitude),
        conn.krpc.Expression.constant_double(alt))
    altitude_reached_event = conn.krpc.add_event(expr)
    with altitude_reached_event.condition:
        altitude_reached_event.wait()

def course_correct_towards_island_at_altitude():
    until_altitude_reached(20000, 'greater_than')
    print('Altitude reached')
    vessel.control.throttle = 1
    vessel.auto_pilot.target_pitch_and_heading(0, 120)
    time.sleep(12)
    vessel.control.throttle = 0
    


def landing_sequence():
    altitude = 45000
    throttle = 1
    engine_engaged = False
    parachute = vessel.parts.parachutes.pop()
    while True:
        # TODO: Figure out how to keep in retrograde
        # Always keep in retrograde
        retrograde = conn.get_call(getattr, vessel.flight(), 'retrograde')
        vessel.auto_pilot.target_direction = retrograde.arguments
        vessel.auto_pilot.tar
        mean_altitude = conn.get_call(getattr, vessel.flight(), 'mean_altitude')
        if mean_altitude < altitude: # if below target altitude
            if throttle <= 0.1: # break loop at 0.1 throttle and deploy parachutes
                parachute.deploy()
                vessel.control.sas = True
                break
            
            if not engine_engaged:
                vessel.control.throttle = throttle
                continue
            
            altitude -= 1000
            throttle -= 0.0227
            vessel.control.throttle = throttle
    

launch()
handle_booster_separations()
course_correct_towards_island_at_altitude()
landing_sequence()
