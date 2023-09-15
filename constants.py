# constants.py

def initialize_constants():
    with open("outputs/data.txt", 'r') as data_file:
        data_lines = data_file.readlines()

    n = int(data_lines[0].split()[1])
    max_step = int(data_lines[1].split()[1])
    radius = float(data_lines[2].split()[1])
    mass = float(data_lines[3].split()[1])
    init_velocity = float(data_lines[4].split()[1])
    main_width = float(data_lines[5].split()[1])
    main_height = float(data_lines[6].split()[1])
    minor_width = float(data_lines[7].split()[1])

    constants = {
        "n": n,
        "max_step": max_step,
        "radius": radius,
        "mass": mass,
        "init_velocity": init_velocity,
        "main_width": main_width,
        "main_height": main_height,
        "minor_width": minor_width,
    }

    return constants


# Llama a initialize_constants una sola vez al importar este módulo
constants = initialize_constants()
