# import graph function from animation.py
import graphics
from animation import animate
from graphics import *

minor_heights = [0.03, 0.05, 0.07, 0.09]

times = []
all_main_pressures = []
all_minor_pressures = []

#for minor_height in minor_heights:
    # animate(minor_height, 100)

    #times, main_pressures, minor_pressures = graphics.process_system(minor_height=minor_height, delta_t=3)
    # graphics.graph_pressure_vs_time(minor_height, times, main_pressures, minor_pressures)
    #all_main_pressures.append(main_pressures)
    #all_minor_pressures.append(minor_pressures)

# graphics.graph_pressure_vs_at(all_main_pressures, all_minor_pressures, minor_heights)
graphics.graph_difussion_coefficient(minor_heights, index_height=3, skip=10000)
