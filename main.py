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

    times, main_pressures, minor_pressures = graphics.calculatePressure(minor_height=minor_height, reps=reps, deltaT=0.5)
    all_main_pressures.append(main_pressures)
    all_minor_pressures.append(minor_pressures)

    # graphics.graphPressureVsTime(minor_height, times, main_pressures, minor_pressures)

graphics.graphPressureVsAt(all_main_pressures, all_minor_pressures, minor_heights)
