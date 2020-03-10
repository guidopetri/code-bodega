#! /usr/bin/env python3

import pygame
import numpy as np
import sys
import noise


width = 800
height = 600
factor = 4

pygame.init()
surface = pygame.display.set_mode((width, height))
pygame.display.set_caption('Waves in Cellular Automata')

cells = np.zeros((width // factor, height // factor))

# generate initial config (using perlin noise)
np.random.seed(0)
cells = np.array([noise.snoise2(x, y, octaves=1, persistence=5, lacunarity=10)
                  for x in range(cells.shape[0])
                  for y in range(cells.shape[1])]).reshape(cells.shape[0], -1)
cells /= 3
updated_cells = cells.copy()

while True:
    # update cells

    # subtract a proportion of the cell value (0-1.5x)
    vert_diffs = np.random.random(cells.shape)
    vert_diffs *= updated_cells
    horz_diffs = np.random.random(cells.shape)
    horz_diffs *= updated_cells

    # move that proportion to the cells left/above the current cell, weighted
    updated_cells = updated_cells - vert_diffs
    updated_cells[:, :-1] += vert_diffs[:, 1:] * 1.05

    updated_cells = updated_cells - horz_diffs
    updated_cells[:-1, :] += horz_diffs[1:, :] * 0.75 * 1.05

    waves_generated = np.random.randint(cells.shape[0] // 10,
                                        cells.shape[0] // 5)

    # generate new initialization cells
    new_cells = zip(np.random.randint(0,
                                      cells.shape[0],
                                      max(waves_generated, 1)),
                    np.random.randint(0,
                                      cells.shape[1],
                                      max(waves_generated, 1)),
                    )

    for cell in new_cells:
        updated_cells[cell[0], cell[1]] += 0.75

    updated_cells = np.clip(updated_cells, 0, 1)

    # draw cells, going from 0-1 to 0-255 in a blue color field
    blit_cells = np.around(updated_cells * 255)
    blit_cells = np.stack([blit_cells,
                           blit_cells,
                           np.ones(updated_cells.shape) * 255],
                          axis=-1)

    surface.fill(pygame.Color(0, 0, 0))

    pygame.surfarray.blit_array(surface,
                                blit_cells.repeat(factor, axis=0)
                                          .repeat(factor, axis=1))

    pygame.time.delay(100)

    for event in pygame.event.get():
        if (event.type == pygame.QUIT or
            (event.type == pygame.KEYDOWN
             and event.key == pygame.K_q)):
            pygame.quit()
            sys.exit()

    pygame.display.flip()
