import matplotlib.pyplot as plt
import numpy as np
from constants import constants
from scipy.optimize import minimize
import matplotlib as mtl


def add_force(minor_height, main_force, minor_force, vx, vy, second_object_colliding):
    if second_object_colliding == 'P0':
        main_force += (abs(vx) * 2 / constants["main_height"])
    elif second_object_colliding == 'P2' or second_object_colliding == 'P6':
        main_force += (abs(vx) * 2 / (constants["main_height"] - minor_height) / 2)
    elif second_object_colliding == 'P1' or second_object_colliding == 'P7':
        main_force += (abs(vy) * 2 / constants["main_width"])
    elif second_object_colliding == 'P4':
        minor_force += (abs(vx) * 2 / minor_height)
    elif second_object_colliding == 'P3' or second_object_colliding == 'P5':
        minor_force += (abs(vy) * 2 / constants["minor_width"])

    return main_force, minor_force


def process_system(minor_height, reps, delta_t):
    all_main_pressures = []
    all_minor_pressures = []
    avg_collision_amounts = []
    times = []

    for rep in range(reps):
        file_suffix = str(minor_height) + "_" + str(rep)
        with open('outputs/output_' + file_suffix + '.txt', 'r') as file:
            lines = file.readlines()

        current_time = 0
        main_force = 0
        minor_force = 0
        collision_amount = 0

        main_pressures = []
        minor_pressures = []
        collision_amounts = []
        times = []

        for step in range(constants["max_step"]):
            first_line = step * (constants["n"] + 4)
            time = float(lines[first_line + 1].split()[1])
            first_object_colliding = int(lines[first_line + 2].split()[1])
            second_object_colliding = str(lines[first_line + 2].split()[2])

            if time > current_time + delta_t or step == constants["max_step"] - 1:
                main_pressures.append(main_force / delta_t)
                minor_pressures.append(minor_force / delta_t)
                collision_amounts.append(collision_amount)
                times.append(time + delta_t / 2)
                collision_amount = 0
                main_force = 0
                minor_force = 0
                current_time = time

            collision_amount += 1

            if second_object_colliding.startswith('P'):
                vx = float(lines[first_line + first_object_colliding + 3].split()[
                               2])  # + 3 because of the first 3 lines (step, time, collision)
                vy = float(lines[first_line + first_object_colliding + 3].split()[3])
                main_force, minor_force = add_force(minor_height, main_force, minor_force, vx, vy,
                                                    second_object_colliding)

        all_main_pressures.append(main_pressures[:-1])
        all_minor_pressures.append(minor_pressures[:-1])
        avg_collision_amounts.append(np.mean(collision_amounts))

    avg_collision_amount = np.mean(avg_collision_amounts)
    avg_main_pressures = np.mean(all_main_pressures, axis=0)
    avg_minor_pressures = np.mean(all_minor_pressures, axis=0)

    return times[:-1], avg_main_pressures, avg_minor_pressures, avg_collision_amount


def graph_pressure_vs_time(minor_height, times, avg_main_pressures, avg_minor_pressures):
    file_suffix = str(minor_height)
    # Graph main_pressures and minor_pressures in the same graph, having pressure in y-axis and time in x-axis
    plt.figure(figsize=(10, 6))
    plt.plot(times, avg_main_pressures, label="Recinto fijo")
    plt.plot(times, avg_minor_pressures, label="Recinto variable")
    plt.xlabel('Tiempo (s)')
    plt.ylabel('Presión (N/m)')
    plt.grid()
    plt.legend(loc='upper right')
    plt.savefig("images/pressureVsTime_" + file_suffix + ".png")
    print("Saved pressureVsTime_" + file_suffix + ".png")
    plt.close()


def f(x, a, b):
    return a * x + b


def squared_residuals(x, y, a, b):
    return np.sum((y - f(x, a, b)) ** 2)


def adjust_pressure_vs_at(pressures, areas_inverse):
    a_initial = (pressures[1] - pressures[0]) / (areas_inverse[1] - areas_inverse[0])
    b_initial = pressures[0] - a_initial * areas_inverse[0]

    # Bounds for 'a' and 'b' within 20% of the initial values
    a_bounds = (a_initial - 0.1 * a_initial, a_initial + 0.1 * a_initial)
    if b_initial >= 0:
        b_bounds = (b_initial - 0.1 * b_initial, b_initial + 0.1 * b_initial)
    else:
        b_bounds = (b_initial + 0.1 * b_initial, b_initial - 0.1 * b_initial)

    # Create a grid of 'a' and 'b' values
    num_points = 100
    a_values = np.linspace(a_bounds[0], a_bounds[1], num_points)
    b_values = np.linspace(b_bounds[0], b_bounds[1], num_points)
    A, B = np.meshgrid(a_values, b_values)

    # Calculate the squared residuals for each combination of 'a' and 'b'
    error_surface = np.zeros_like(A)
    for i in range(num_points):
        for j in range(num_points):
            error_surface[i, j] = squared_residuals(areas_inverse, pressures, A[i, j], B[i, j])

    # Find the minimum of the error surface using minimize
    initial_guess = np.array([a_initial, b_initial])
    result = minimize(lambda coeffs: squared_residuals(areas_inverse, pressures, *coeffs), initial_guess,
                      bounds=[a_bounds, b_bounds])

    # Get the best-fitting coefficients
    best_a, best_b = result.x

    # Plot the 3D error surface
    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')
    surf = ax.plot_surface(A, B, error_surface, cmap='viridis')  # Plot the error surface
    ax.set_xlabel('a')
    ax.set_ylabel('b')
    ax.set_zlabel('Error')

    # Plot the point corresponding to the minimum
    ax.scatter(best_a, best_b, squared_residuals(areas_inverse, pressures, best_a, best_b), color='black', s=50,
               label='Minimum')
    ax.view_init(elev=20)
    plt.legend()
    plt.savefig("images/adjust_pressureVsAt.png")
    print("Saved adjust_pressureVsAt.png")
    plt.close()

    return best_a, best_b


def graph_pressure_vs_At(all_main_pressures, all_minor_pressures, minor_heights):
    pressures = []
    areas_inverse = []

    for i, minor_height in enumerate(minor_heights):
        pressures.append(np.mean([x + y for x, y in zip(all_main_pressures[i], all_minor_pressures[
            i])]))  # TODO: luego del estado estacionario
        areas_inverse.append(
            1 / (constants["main_height"] * constants["main_width"] + minor_height * constants["minor_width"]))

        print("area: " + str((constants["main_height"] * constants["main_width"] + minor_height * constants["minor_width"])))
    pressures = np.array(pressures)
    areas_inverse = np.array(areas_inverse)

    best_a, best_b = adjust_pressure_vs_at(pressures, areas_inverse)
    fitted_xs = np.arange(areas_inverse[-1], areas_inverse[0], step=0.1)
    fitted_pressures = f(fitted_xs, best_a, best_b)

    # Grafica los datos originales y la curva de ajuste con el valor óptimo de c
    plt.figure(figsize=(10, 6))
    plt.plot(areas_inverse, pressures, 'ro', label='Datos Originales')
    plt.plot(fitted_xs, fitted_pressures, 'b-', label='Curva de Ajuste Lineal')
    plt.xlabel('1/Área (1/m)')
    plt.ylabel('Presión (N/m)')
    plt.grid()
    plt.legend(loc='upper left')
    plt.savefig("images/pressureVsAt.png")
    print("Saved pressureVsAt.png")
    plt.close()
