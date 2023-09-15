import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
from constants import constants
from scipy.optimize import minimize


def add_force(minor_height, main_force, minor_force, vx, vy, second_object_colliding):
    if second_object_colliding == 'P0':
        main_force += vx * 2 / constants["main_height"]
    elif second_object_colliding == 'P2' or second_object_colliding == 'P6':
        main_force += vx * 2 / (constants["main_height"] - minor_height) / 2
    elif second_object_colliding == 'P1' or second_object_colliding == 'P7':
        main_force += vy * 2 / constants["main_width"]
    elif second_object_colliding == 'P4':
        minor_force += vx * 2 / minor_height
    elif second_object_colliding == 'P3' or second_object_colliding == 'P5':
        minor_force += vy * 2 / constants["minor_width"]

    return main_force, minor_force


def calculate_pressure(minor_height, reps, deltaT=0.5):
    all_main_pressures = []
    all_minor_pressures = []

    for rep in range(reps):
        file_suffix = str(minor_height) + "_" + str(rep)
        with open('outputs/output_' + file_suffix + '.txt', 'r') as file:
            lines = file.readlines()

        currentTime = 0
        main_force = 0
        minor_force = 0

        main_pressures = []
        minor_pressures = []
        times = []

        for step in range(constants["max_step"]):
            first_line = step * (constants["n"] + 4)
            time = float(lines[first_line + 1].split()[1])
            first_object_colliding = int(lines[first_line + 2].split()[1])
            second_object_colliding = str(lines[first_line + 2].split()[2])

            if time > currentTime + deltaT or step == constants["max_step"] - 1:
                main_pressures.append(main_force / deltaT)
                minor_pressures.append(minor_force / deltaT)
                times.append(time + deltaT / 2)
                main_force = 0
                minor_force = 0
                currentTime = time

            if second_object_colliding.startswith('P'):
                vx = float(lines[first_line + first_object_colliding + 3].split()[
                               2])  # + 3 because of the first 3 lines (step, time, collision)
                vy = float(lines[first_line + first_object_colliding + 3].split()[3])
                main_force, minor_force = add_force(minor_height, main_force, minor_force, vx, vy,
                                                    second_object_colliding)

        all_main_pressures.append(main_pressures)
        all_minor_pressures.append(minor_pressures)

        avg_main_pressures = np.mean(all_main_pressures, axis=0)
        avg_minor_pressures = np.mean(all_minor_pressures, axis=0)

        return times, avg_main_pressures, avg_minor_pressures


def graph_pressure_vs_time(minor_height, times, main_pressures, minor_pressures):
    file_suffix = str(minor_height)
    # Graph main_pressures and minor_pressures in the same graph, having pressure in y-axis and time in x-axis
    plt.figure(figsize=(10, 6))
    plt.plot(times, main_pressures, label="Perímetro fijo")
    plt.plot(times, minor_pressures, label="Perímetro variable")
    plt.xlabel('Tiempo (s)')
    plt.ylabel('Presión (N/m)')
    plt.grid()
    plt.legend(loc='upper right')
    plt.savefig("images/pressureVsTime_" + file_suffix + ".png")
    print("Saved pressureVsTime_" + file_suffix + ".png")
    plt.close()


def f(x, a, b, c):
    return a ** (x - b) + c


def squared_residuals(x, y, a, b, c):
    return np.sum((y - f(x, a, b, c)) ** 2)


def graph_pressure_vs_At(all_main_pressures, all_minor_pressures, minor_heights):
    pressures = []
    areas_inverse = []

    for i, minor_height in enumerate(minor_heights):
        pressures.append(np.mean([x + y for x, y in zip(all_main_pressures[i], all_minor_pressures[
            i])]))  # TODO: luego del estado estacionario
        areas_inverse.append(
            1 / (constants["main_height"] * constants["main_width"] + minor_height * constants["minor_width"]))
    pressures = np.array(pressures)
    areas_inverse = np.array(areas_inverse)

    b = areas_inverse[-1]
    c = pressures[0]
    print("b:" + str(b))
    print("c:" + str(c))
    bounds = [(0.1, 0.9), (b - b*0.1, b + b*0.1)]
    if c >= 0:
        bounds.append((c - c*0.2, c + c*0.2))
    else:
        bounds.append((c + c*0.2, c - c*0.2))
    print(bounds)

    initial_guess = np.array([0.5, b, c])
    result = minimize(lambda coeffs: squared_residuals(areas_inverse, pressures, *coeffs), initial_guess, bounds=bounds)
    print(result)
    fitted_pressures = f(np.arange(areas_inverse[0], areas_inverse[-1], step=1), result.x[0], result.x[1], result.x[2])
    print(fitted_pressures)

    # Grafica los datos originales y la curva de ajuste con el valor óptimo de c
    plt.figure(figsize=(10, 6))
    plt.plot(areas_inverse, pressures, 'ro', label='Datos Originales')
    plt.plot(areas_inverse, fitted_pressures, 'b-', label='Curva de Ajuste Exponencial (c óptimo)')
    plt.xlabel('1/Área (1/m)')
    plt.ylabel('Presión (N/m)')
    plt.grid()
    plt.legend(loc='upper right')
    plt.savefig("images/pressureVsAt.png")
    print("Saved pressureVsAt.png")
    plt.close()
