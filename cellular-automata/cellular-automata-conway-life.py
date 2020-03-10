#! /usr/bin/env python3

import pygame
import numpy as np
import sys


def get_neighbors(cell, state):
    # torus-like

    neighbors = 0

    r_x = cell[0] == len(state) - 1
    d_y = cell[1] == len(state[0]) - 1

    # negatives are fair game (thanks python!)
    neighbors += (state[cell[0] - 1, cell[1]] == 1)
    neighbors += (state[cell[0], cell[1] - 1] == 1)

    neighbors += (state[cell[0] - 1, cell[1] - 1] == 1)

    if not r_x:
        neighbors += (state[cell[0] + 1, cell[1]] == 1)
        neighbors += (state[cell[0] + 1, cell[1] - 1] == 1)
    else:
        neighbors += (state[0, cell[1]] == 1)
        neighbors += (state[0, cell[1] - 1] == 1)

    if not d_y:
        neighbors += (state[cell[0], cell[1] + 1] == 1)
        neighbors += (state[cell[0] - 1, cell[1] + 1] == 1)
    else:
        neighbors += (state[cell[0], 0] == 1)
        neighbors += (state[cell[0] - 1, 0] == 1)

    if not r_x and not d_y:
        neighbors += (state[cell[0] + 1, cell[1] + 1] == 1)
    else:
        neighbors += (state[0, 0] == 1)

    return neighbors


def update_cells(cells):
    updated = cells.copy()

    for i, row in enumerate(cells):
        for j, cell in enumerate(row):
            n = get_neighbors((i, j), cells)
            if n < 2 or n > 3:
                updated[i, j] = 0
            if n == 3:
                updated[i, j] = 1

    return updated


if __name__ == '__main__':

    width = 800
    height = 600
    factor = 10

    pygame.init()
    surface = pygame.display.set_mode((width, height))
    pygame.display.set_caption('Conway\'s Game of Life')

    if '--file' in sys.argv:
        import os

        idx = sys.argv.index('--file')
        filename = sys.argv[idx + 1]
        filename = os.path.join('.', filename)
        with open(filename, 'r') as f:
            cells = np.array([[int(y) for y in x.strip()]
                              for x in f.readlines()]).T

        pad_w_l = (width // factor - cells.shape[0]) // 2
        pad_w_r = width // factor - cells.shape[0] - pad_w_l

        pad_h_u = (height // factor - cells.shape[1]) // 2
        pad_h_d = height // factor - cells.shape[1] - pad_h_u

        cells = np.pad(cells,
                       [(pad_w_l, pad_w_r),
                        (pad_h_u, pad_h_d)
                        ])

    else:
        # generate initial config
        cells = np.random.choice([0, 0, 0, 0, 0, 1],
                                 (width // factor, height // factor))

    while True:
        cells = update_cells(cells)

        # draw cells, going from 0-1 to 0-255 in a blue color field
        blit_cells = cells * 255
        blit_cells = np.stack([blit_cells,
                               blit_cells,
                               blit_cells],
                              axis=-1)

        surface.fill(pygame.Color(0, 0, 0))

        pygame.surfarray.blit_array(surface,
                                    blit_cells.repeat(factor, axis=0)
                                              .repeat(factor, axis=1))

        # pygame.time.delay(30)

        for event in pygame.event.get():
            if (event.type == pygame.QUIT or
                (event.type == pygame.KEYDOWN
                 and event.key == pygame.K_q)):
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                # cells = update_cells(cells)
                pass

        pygame.display.flip()
