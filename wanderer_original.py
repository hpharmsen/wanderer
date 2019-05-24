# https://csijh.github.io/wanderer/javascript/index.html

# TODO:
# √ Split into Gridworld and Wanderer projects
# √ All on GitHub
# √ Dead by arrows en boulders
# - Persistent statusbar
# - Message by kill
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


import sys
from functools import partial

# pip3 install git+https://github.com/hpharmsen/gridworld
from gridworld.grid import Grid, draw_character_cell, TOP, log
import pygame

import drawing
from hero import Hero
from game_queue import GameQueue

game_active = False


def key_action(grid, key):
    global direction_map, current_level, hero, game_queue, game_active
    if key == pygame.K_q:
        sys.exit()
    elif key == pygame.K_r or not game_active:
        start_level(grid, current_level)
    else:
        move = {pygame.K_LEFT: (-1, 0), pygame.K_RIGHT: (1, 0), pygame.K_UP: (0, -1), pygame.K_DOWN: (0, 1)}.get(key)
        if move:
            dirty_cells = hero.move(move)
            if hero.dead:
                game_active = False
            else:
                for cell in dirty_cells:
                    game_queue.fill(*cell)
        log('hero moved')


def start_level(grid, level):
    global game_active

    grid.auto_update = False
    grid.load(f'levels/level{level}.txt')
    grid.auto_update = True
    grid.redraw()
    if not hero:
        hero = Hero(grid)
    else:
        hero.__init__(grid)
    print(hero.dead)
    game_queue = GameQueue(grid)
    game_active = True
    return hero, game_queue


def game_logic(grid):
    global hero, game_active
    if game_active:
        message = game_queue.process()
        if message:
            game_active = False
            hero.die(message)


if __name__ == '__main__':
    logging = True
    current_level = 0
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

    hero, game_queue = start_level(grid, current_level)

    grid.frame_action = game_logic
    grid.key_action = key_action
    grid.run()
