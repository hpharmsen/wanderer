# https://csijh.github.io/wanderer/javascript/index.html

# TODO:
# √ Split into Gridworld and Wanderer projects
# √ All on GitHub
# √ Dead by arrows en boulders
# √ Persistent statusbar
# √ Message by kill
# - Win when exit and all money
# - Level chooser
# - center screen in full screen mode

# √ Switch between update and flip
# - Readme.md with dependencies and usage
# - implement balloons
# - implement monsters
# - implement time capsule and maximum moves

# GRIDWORLD TODO:
# - README met voorbeelden en uitleg per functie
# - Borders ook mogelijk maken naast vakjes (PacMan, Kamertje verhuren)
# - Properties met underscore plus getters/setters waar nodig

import sys
from functools import partial

# pip3 install git+https://github.com/hpharmsen/gridworld
from gridworld.grid import Grid, draw_character_cell, TOP, log
import pygame
import drawing
from game import Game


def key_action(key, game):
    log('key action', key)
    if key == pygame.K_q:
        sys.exit()
    elif key == pygame.K_r or not game.active:
        game.start_level()
    else:
        moves = {pygame.K_LEFT: (-1, 0), pygame.K_RIGHT: (1, 0), pygame.K_UP: (0, -1), pygame.K_DOWN: (0, 1)}
        movement = moves.get(key)
        if movement:
            game.move(movement)


def game_step(game):
    game.step()


def setup_grid():
    grid = Grid(
        42,
        18,
        33,
        33,
        title='test',
        margin=0,
        margincolor=drawing.GRAY,
        itemfont='/Library/Fonts/Arial.ttf',
        framerate=60,
        statusbar_position=TOP,
        statusbar_size=34,
        full_screen=False,
    )
    grid.update_fullscreen = False  # Only update the changed bits
    grid.set_drawaction('#', partial(drawing.draw_ground, color=(60, 60, 60)))
    grid.set_drawaction('=', partial(drawing.draw_ground, color=(70, 70, 70)))
    grid.set_drawaction(':', partial(drawing.draw_ground, color=(140, 120, 80)))
    grid.set_drawaction('\\', drawing.draw_down_line)
    grid.set_drawaction('O', drawing.draw_boulder)
    grid.set_drawaction('/', drawing.draw_up_line)
    grid.set_drawaction('!', drawing.draw_bomb)
    grid.set_drawaction('*', drawing.draw_money)
    grid.set_drawaction('<', partial(draw_character_cell, character='←'))
    grid.set_drawaction('>', partial(draw_character_cell, character='→'))

    return grid


if __name__ == '__main__':
    # gridworld.grid.logging = True
    current_level = 0

    grid = setup_grid()
    game = Game(grid)

    grid.frame_action = partial(game_step, game=game)
    grid.key_action = partial(key_action, game=game)
    grid.update_statusbar = game.update_statusbar

    game.start_level(0)
    grid.run()
