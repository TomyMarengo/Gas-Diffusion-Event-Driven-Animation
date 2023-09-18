import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
from constants import constants

##### Graphics #####
img_plot = None
ax2d = None
minor_height = 0
lines = []
n = constants["n"]
radius = constants["radius"]
mass = constants["mass"]
init_velocity = constants["init_velocity"]
main_width = constants["main_width"]
main_height = constants["main_height"]
minor_width = constants["minor_width"]

####################

def update(frame, skip):
    global img_plot, ax2d, minor_height, lines

    ax2d.clear()

    first_line = skip * frame * (n + 4)  # 4 -> step + time + firstObjectColliding + secondObjectColliding
    step = int(lines[first_line].split()[1])
    time = float(lines[first_line + 1].split()[1])
    firstObjectColliding = int(lines[first_line + 2].split()[1])
    secondObjectColliding = str(lines[first_line + 2].split()[2])

    # Initialize array particles, each line of the file contain posX posY velX velY of each particle
    particles = np.zeros((n, 4))
    for i in range(n):
        particles[i] = lines[first_line + 3 + i].split()

    img_plot = ax2d.scatter(particles[:, 0], particles[:, 1], s=50, c='b')

    ax2d.plot([0, 0], [-main_height, 0], color='b')  # 0
    # line from (0, 0) to (main_width, 0)
    ax2d.plot([0, main_width], [0, 0], color='b')  # 1
    # line from (main_width, 0) to (main_width, -(main_height - minor_height) / 2
    ax2d.plot([main_width, main_width], [0, -(main_height - minor_height) / 2], color='b')  # 2
    # line from (main_width, -(main_height - minor_height) / 2) to (main_width + minor_width, -(main_height - minor_height) / 2)
    ax2d.plot([main_width, main_width + minor_width],
              [-(main_height - minor_height) / 2, -(main_height - minor_height) / 2], color='b')  # 3
    # line from (main_width + minor_width, -(main_height - minor_height) / 2) to (main_width + minor_width, -(main_height - minor_height) / 2 - minor_height)
    ax2d.plot([main_width + minor_width, main_width + minor_width],
              [-(main_height - minor_height) / 2, -(main_height - minor_height) / 2 - minor_height], color='b')  # 4
    # line from (main_width + minor_width, -(main_height - minor_height) / 2 - minor_height) to (main_width, -(main_height - minor_height) / 2 - minor_height)
    ax2d.plot([main_width + minor_width, main_width],
              [-(main_height - minor_height) / 2 - minor_height, -(main_height - minor_height) / 2 - minor_height],
              color='b')  # 5
    # line from (main_width, -(main_height - minor_height) / 2 - minor_height) to (main_width, -main_height)
    ax2d.plot([main_width, main_width], [-(main_height - minor_height) / 2 - minor_height, -main_height],
              color='b')  # 6
    # line from (main_width, -main_height) to (0, -main_height)
    ax2d.plot([main_width, 0], [-main_height, -main_height], color='b')  # 7

    if secondObjectColliding == 'P0':
        ax2d.plot([0, 0], [-main_height, 0], color='r')  # 0
    elif secondObjectColliding == 'P1':
        ax2d.plot([0, main_width], [0, 0], color='r')  # 1
    elif secondObjectColliding == 'P2':
        ax2d.plot([main_width, main_width], [0, -(main_height - minor_height) / 2], color='r')  # 2
    elif secondObjectColliding == 'P3':
        ax2d.plot([main_width, main_width + minor_width],
                  [-(main_height - minor_height) / 2, -(main_height - minor_height) / 2], color='r')  # 3
    elif secondObjectColliding == 'P4':
        ax2d.plot([main_width + minor_width, main_width + minor_width],
                  [-(main_height - minor_height) / 2, -(main_height - minor_height) / 2 - minor_height], color='r')  # 4
    elif secondObjectColliding == 'P5':
        ax2d.plot([main_width + minor_width, main_width],
                  [-(main_height - minor_height) / 2 - minor_height, -(main_height - minor_height) / 2 - minor_height],
                  color='r')  # 5
    elif secondObjectColliding == 'P6':
        ax2d.plot([main_width, main_width], [-(main_height - minor_height) / 2 - minor_height, -main_height],
                  color='r')  # 6
    elif secondObjectColliding == 'P7':
        ax2d.plot([main_width, 0], [-main_height, -main_height], color='r')  # 7
    else:
        if secondObjectColliding != '-1':
            ax2d.scatter(particles[int(secondObjectColliding), 0], particles[int(secondObjectColliding), 1], s=75,
                         c='r')

    if firstObjectColliding != -1:
        ax2d.scatter(particles[int(firstObjectColliding), 0], particles[int(firstObjectColliding), 1], s=75, c='r')

    plt.xticks([])
    plt.yticks([])

    ax2d.set_xticks([])
    ax2d.set_yticks([])

    return [img_plot]


def animate(height, skip=100):
    global img_plot, ax2d, minor_height, lines
    fig, ax2d = plt.subplots(figsize=(10, 10))
    ax2d.set_aspect('equal', adjustable='box')
    fig.canvas.manager.set_window_title('Gas Diffusion')

    minor_height = height
    file_suffix = str(height) + "_0"

    with open('outputs/output_' + file_suffix + '.txt', 'r') as file:
        lines = file.readlines()

    max_step = int(len(lines)/(constants["n"] + 4))
    cant_frames = int(max_step/skip)

    ani = FuncAnimation(fig, frames=cant_frames, func=update, fargs=(skip,), interval=100)
    plt.tight_layout()
    ani.save('gifs/animation_' + file_suffix + '.gif')
    print('Gif ' + file_suffix + ' creado')
    return ani
