#! /usr/bin/env python3

import pygame
import numpy as np
import sys


def get_neighbors(cell, state):

    neighbors = 0

    if cell[0] != 0:
        neighbors += (state[cell[0] - 1, cell[1]] == 1)
    if cell[0] < (len(state) - 1):
        neighbors += (state[cell[0] + 1, cell[1]] == 1)
    if cell[1] != 0:
        neighbors += (state[cell[0], cell[1] - 1] == 1)
    if cell[1] < (len(state[0]) - 1):
        neighbors += (state[cell[0], cell[1] + 1] == 1)

    return neighbors


def generate_new_sprite(surface):
    color = 1.0

    state = np.random.choice([0.0, color], (4, 8))

    for _ in range(2):
        old_state = state.copy()

        for i, row in enumerate(state):
            for j, cell in enumerate(row):
                n = get_neighbors((i, j), old_state)

                state[i, j] = color * ((cell == 0 and n in (0, 1))
                                       or (cell > 0 and n in (2, 3))
                                       )

    state = np.vstack([np.zeros(state.shape[1]).reshape(1, -1), state])

    state = np.hstack([np.zeros(state.shape[0]).reshape(-1, 1),
                       state,
                       np.zeros(state.shape[0]).reshape(-1, 1)],
                      )

    for i, row in enumerate(state):
        for j, cell in enumerate(row):
            if cell:
                pass
            elif get_neighbors((i, j), state):
                state[i, j] = 0.5

    # draw cells, going from 0-1 to 0-255
    blit_cells = np.around(state * 255)
    blit_cells = np.stack([blit_cells,
                           blit_cells,
                           blit_cells],
                          axis=-1)
    color = np.random.random(3)
    blit_cells = blit_cells * color
    blit_cells = np.around(blit_cells)
    blit_cells = np.vstack([blit_cells,
                            np.flip(blit_cells, axis=0)])

    ratio_w = surface.get_width() // blit_cells.shape[0]
    ratio_h = surface.get_height() // blit_cells.shape[1]

    blit_cells = blit_cells.repeat(ratio_w, axis=0).repeat(ratio_h, axis=1)

    pad_w_l = (surface.get_width() - blit_cells.shape[0]) // 2
    pad_w_r = surface.get_width() - blit_cells.shape[0] - pad_w_l

    pad_h_u = (surface.get_height() - blit_cells.shape[1]) // 2
    pad_h_d = surface.get_height() - blit_cells.shape[1] - pad_h_u

    blit_cells = np.pad(blit_cells,
                        [(pad_w_l, pad_w_r),
                         (pad_h_u, pad_h_d),
                         (0, 0)
                         ])

    pygame.surfarray.blit_array(surface, blit_cells)

    return surface


if __name__ == '__main__':

    width = 600
    height = 600

    pygame.init()
    surface = pygame.display.set_mode((width, height))
    pygame.display.set_caption('Sprites in Cellular Automata')

    sprite_sheet = []
    size = 60

    for _ in range(width // size):
        for _ in range(height // size):
            sprite_surf = pygame.Surface((size, size))
            sprite_surf.set_colorkey(pygame.Color(0, 0, 0))
            sprite_surf = generate_new_sprite(sprite_surf)
            sprite_sheet.append(sprite_surf)

    while True:

        surface.fill(pygame.Color(255, 255, 255))

        for i, sprite in enumerate(sprite_sheet):
            loc = sprite.get_rect(topleft=((size * i) % width,
                                           size * (i // (height // size))))
            surface.blit(sprite, loc)

        for event in pygame.event.get():
            if (event.type == pygame.QUIT or
                (event.type == pygame.KEYDOWN
                 and event.key == pygame.K_q)):
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                for i, sprite_surf in enumerate(sprite_sheet):
                    sprite_surf = generate_new_sprite(sprite_surf)
                    sprite_sheet.pop(i)
                    sprite_sheet.append(sprite_surf)

        pygame.display.flip()
