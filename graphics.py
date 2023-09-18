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


def process_system(minor_height, delta_t):
    file_suffix = str(minor_height) + "_0"
    with open('outputs/output_' + file_suffix + '.txt', 'r') as file:
        lines = file.readlines()

    current_time = 0
    main_force = 0
    minor_force = 0

    main_pressures = []
    minor_pressures = []
    times = []
    max_step = int(lines[-2].split()[1])

    for step in range(max_step):
        first_line = step * (constants["n"] + 4)
        time = float(lines[first_line + 1].split()[1])
        first_object_colliding = int(lines[first_line + 2].split()[1])
        second_object_colliding = str(lines[first_line + 2].split()[2])

        if time > current_time + delta_t or step == max_step - 1:
            main_pressures.append(main_force / delta_t)
            minor_pressures.append(minor_force / delta_t)
            times.append(time + delta_t / 2)
            main_force = 0
            minor_force = 0
            current_time = time

        if second_object_colliding.startswith('P'):
            vx = float(lines[first_line + 3 + first_object_colliding].split()[2])
            vy = float(lines[first_line + 3 + first_object_colliding].split()[3])
            main_force, minor_force = add_force(minor_height, main_force, minor_force, vx, vy,
                                                second_object_colliding)

    return times[:-1], main_pressures[:-1], minor_pressures[:-1]


def graph_pressure_vs_time(minor_height, times, main_pressures, minor_pressures):
    # Graph main_pressures and minor_pressures in the same graph, having pressure in y-axis and time in x-axis
    plt.figure(figsize=(10, 6))
    plt.plot(times, main_pressures, label="Recinto fijo")
    plt.plot(times, minor_pressures, label="Recinto variable")
    plt.xlabel('Tiempo (s)')
    plt.ylabel('Presión ($\\frac{N}{m}$)')

    plt.grid()
    plt.legend(loc='upper right')
    plt.savefig("images/pressureVsTime_" + str(minor_height) + ".png")
    print("Saved pressureVsTime_" + str(minor_height) + ".png")
    plt.close()


def f(x, a, b):
    return a * x + b


def squared_residuals(x, y, b, a):
    return np.sum((y - f(x, a, b)) ** 2)


def adjust_pressure_vs_at(pressures, areas_inverse):
    a_initial = (pressures[-1] - pressures[0]) / (areas_inverse[-1] - areas_inverse[0])
    b_initial = pressures[0] - a_initial * areas_inverse[0]
    # Bounds for 'a' within 50% of the initial values
    a_bounds = (a_initial - 0.2 * a_initial, a_initial + 0.2 * a_initial)

    # Create a range of values for 'a'
    num_points = 100
    a_values = np.linspace(a_bounds[0], a_bounds[1], num_points)

    # Calculate the squared residuals for each combination of 'a'
    error_curve = np.array([0.0] * num_points)
    for i in range(num_points):
        error_curve[i] = squared_residuals(areas_inverse, pressures, b_initial, a_values[i])

    # Find the minimum of the error surface using minimize
    initial_guess = np.array([a_initial])
    result = minimize(lambda coeffs: squared_residuals(areas_inverse, pressures, b_initial, *coeffs), x0=initial_guess)

    # Get the best-fitting coefficients
    best_a = result.x[0]
    best_error = squared_residuals(areas_inverse, pressures, b_initial, best_a)

    plt.figure(figsize=(10, 6))
    plt.plot(a_values, error_curve, 'b-')
    plt.xlabel('a')
    plt.ylabel('E(a)')

    print("best_a: " + str(best_a))
    print("best_error: " + str(best_error))

    plt.scatter(best_a, squared_residuals(areas_inverse, pressures, b_initial, best_a), c='black', s=50, label='Mejor a')
    plt.axvline(x=best_a,  color='gray', linestyle='--')  # Vertical line to x-axis
    plt.axhline(y=best_error, color='gray', linestyle='--')  # Horizontal line to y-axis

    # Add ticks and labels for the lines
    plt.text(best_a, best_error + 2, f'{best_a:.3f}', ha='center', va='center')
    plt.text(0.18, best_error + 1, f'{best_error:.3f}', ha='center', va='center')

    plt.legend(loc='upper right')
    plt.grid()
    plt.savefig("images/adjust_pressureVsAt.png")
    print("Saved adjust_pressureVsAt.png")
    plt.close()

    return best_a, b_initial


def graph_pressure_vs_at(all_main_pressures, all_minor_pressures, minor_heights):
    pressures = []
    areas_inverse = []

    for i, minor_height in enumerate(minor_heights):
        start_stationary_index = int(
            0.4 * len(all_main_pressures[i]))  # Stationary state after 40% of the function approx.
        pressures.append(np.mean([x + y for x, y in zip(all_main_pressures[i][start_stationary_index:],
                                                        all_minor_pressures[i][start_stationary_index:])]))
        areas_inverse.append(
            1 / (constants["main_height"] * constants["main_width"] + minor_height * constants["minor_width"]))

    pressures = np.array(pressures)
    areas_inverse = np.array(areas_inverse)

    best_a, best_b = adjust_pressure_vs_at(pressures, areas_inverse)
    fitted_xs = np.arange(areas_inverse[-1], areas_inverse[0], step=1)
    fitted_pressures = f(fitted_xs, best_a, best_b)

    # Grafica los datos originales y la curva de ajuste con el valor óptimo de c
    plt.figure(figsize=(10, 6))
    plt.plot(areas_inverse, pressures, marker='o', linestyle='', label='Datos Originales')
    plt.plot(fitted_xs, fitted_pressures, label='Curva de Ajuste Lineal')
    plt.xlabel('$Área^{-1} (\\frac{1}{m^2}$)')
    plt.ylabel('Presión ($\\frac{N}{m}$)')
    plt.grid()
    plt.legend(loc='upper left')
    plt.savefig("images/pressureVsAt.png")
    print("Saved pressureVsAt.png")
    plt.close()


def f_c(x, a):
    return a * x


def squared_residuals_c(x, y, a):
    return np.sum((y - f_c(x, a)) ** 2)


def graph_difussion_coefficient(minor_heights, index_height=3, skip=100):  # 0.09

    file_suffix = str(minor_heights[index_height]) + "_0"
    with open('outputs/output_' + file_suffix + '.txt', 'r') as file:
        lines = file.readlines()

    max_step = int(lines[-2].split()[1])
    first_step = int(max_step * 0.07)
    first_particle_line_before = first_step * (constants["n"] + 4) + 3

    times = []
    msds_avg = []
    msds_std = []

    # from start_stationary_index to max_step with step skip
    for step in range(first_step, max_step, skip):
        times.append(float(lines[step * (constants["n"] + 4) + 1].split()[1]))
        first_particle_line_after = step * (constants["n"] + 4) + 3

        msds = []
        for i in range(constants["n"]):
            msds.append((float(lines[first_particle_line_after + i].split()[0]) - float(lines[first_particle_line_before + i].split()[0])) ** 2 \
                        + (float(lines[first_particle_line_after + i].split()[1]) - float(lines[first_particle_line_before + i].split()[1])) ** 2)

        msds_avg.append(np.mean(msds))
        msds_std.append(np.std(msds))

    times = np.array(times)
    msds_avg = np.array(msds_avg)
    msds_std = np.array(msds_std)

    num_points_to_fit = int(0.5 * len(times))
    times_fit = np.array(times[:num_points_to_fit])
    msds_avg_fit = np.array(msds_avg[:num_points_to_fit])

    print(msds_avg_fit)

    result = minimize(lambda coeffs: squared_residuals_c(times_fit, msds_avg_fit, *coeffs),
                      x0=np.array([3 * (10 ** (-5))]))
    best_a = result.x[0]

    adjust_difussion_coefficient(msds_avg_fit, times_fit, best_a)

    formatted_decimal = str(best_a)[0:4]
    best_a_exp = int(np.floor(np.log10(abs(best_a))))
    formatted_best_a = r'$10^{' + str(best_a_exp) + '}$'

    # Grafica los datos y el ajuste
    plt.figure(figsize=(10, 6))
    plt.errorbar(times, msds_avg, yerr=msds_std, label='Datos originales')
    plt.plot(times_fit, f_c(times_fit, best_a), label='Ajuste Lineal, D=' + formatted_decimal + "·" + formatted_best_a)
    plt.xlabel('Tiempo (s)')
    plt.ylabel('$<z^2> (m^2)$')
    plt.grid()

    # Agrega el valor de D como texto en el gráfico
    text_x = times_fit[int(num_points_to_fit / 2)] + 20  # Posición x para el texto
    text_y = f_c(text_x, best_a) + 20  # Posición y para el texto
    plt.text(text_x, text_y, f'D = {best_a}', fontsize=12, color='black')

    plt.legend(loc='upper left')
    plt.savefig("images/msd_" + str(minor_heights[index_height]) + ".png")
    print("Saved images/msd_" + str(minor_heights[index_height]) + ".png")
    plt.close()


def adjust_difussion_coefficient(msds_avg_fit, times_fit, a_initial):
    best_a = a_initial
    # Bounds for 'a' within 20% of the initial values
    a_bounds = (a_initial - 0.2 * a_initial, a_initial + 0.2 * a_initial)

    # Create a range of values for 'a'
    num_points = 100
    a_values = np.linspace(a_bounds[0], a_bounds[1], num_points)

    # Calculate the squared residuals for each combination of 'a'
    error_curve = np.array([0.0] * num_points)
    for i in range(num_points):
        error_curve[i] = squared_residuals_c(times_fit, msds_avg_fit, a_values[i])

    best_error = squared_residuals_c(times_fit, msds_avg_fit, a_initial)

    print(best_a)
    print(best_error)

    plt.figure(figsize=(10, 6))
    plt.plot(a_values, error_curve, 'b-')
    plt.xlabel('a')
    plt.ylabel('E(a)')

    plt.scatter(best_a, squared_residuals_c(times_fit, msds_avg_fit, best_a), c='black', s=50, label='Mejor a')
    plt.axvline(x=best_a,  color='gray', linestyle='--')  # Vertical line to x-axis
    plt.axhline(y=best_error, color='gray', linestyle='--')  # Horizontal line to y-axis


    formatted_decimal_best_a = str(best_a)[0:4]
    best_a_exp = int(np.floor(np.log10(abs(best_a))))
    formatted_best_a = r'$10^{' + str(best_a_exp) + '}$'

    formatted_decimal_error = str(best_error)[0:4]
    best_error_exp = int(np.floor(np.log10(abs(best_error))))
    formatted_error = r'$10^{' + str(best_error_exp) + '}$'

    # Add ticks and labels for the lines
    plt.text(best_a+0.05*10**-5, best_error+0.05*10**-5, f'{formatted_decimal_best_a + "·" + formatted_best_a}', ha='center', va='center')
    plt.text(best_a-0.6*10**-5, best_error+0.02*10**-5, f'{formatted_decimal_error + "·" + formatted_error}', ha='center', va='center')

    plt.legend(loc='upper right')
    plt.grid()
    plt.savefig("images/adjust_difussion_coefficient.png")
    print("Saved adjust_difussion_coefficient.png")
    plt.close()

    return best_a