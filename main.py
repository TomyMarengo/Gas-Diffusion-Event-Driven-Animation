# import graph function from animation.py
import graphics
from animation import animate
from graphics import *

reps = 1
minor_heights = [0.03, 0.05, 0.07, 0.09]

times = []
all_main_pressures = []
all_minor_pressures = []

for minor_height in minor_heights:
    # animate(minor_height, 100)

    times, avg_main_pressures, avg_minor_pressures, avg_collision_amount = graphics.process_system(minor_height=minor_height, reps=reps, delta_t=1.8)
    all_main_pressures.append(avg_main_pressures)
    all_minor_pressures.append(avg_minor_pressures)

    # graphics.graph_pressure_vs_time(minor_height, times, avg_main_pressures, avg_minor_pressures)

graphics.graph_pressure_vs_At(all_main_pressures, all_minor_pressures, minor_heights)
