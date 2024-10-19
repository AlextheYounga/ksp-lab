import krpc
import time
import math
import json

# To be used with the Orbiter A1 stock KSP craft

conn = krpc.connect('kerbal_x')
vessel = conn.space_center.active_vessel

def launch():
    vessel.auto_pilot.target_pitch_and_heading(90, 90)
    vessel.auto_pilot.engage()
    vessel.control.throttle = 1 # must go faster
    vessel.control.activate_next_stage() # engines
    print('Launch')

    

launch()

retrograde = conn.get_call(getattr, vessel.flight(), 'retrograde')
import pdb; pdb.set_trace()
