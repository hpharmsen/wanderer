# https://csijh.github.io/wanderer/javascript/index.html

# TODO:
# √ Reimplement fill_queue
# √ Readme.md with dependencies and usage
# - implement mini monsters
# √ S to save level progress
# - implement balloons
# - implement time capsule and maximum moves

# GRIDWORLD TODO:
# - Borders ook mogelijk maken naast vakjes (PacMan, Kamertje verhuren)
# - Properties with underscore plus getters/setters where needed

import sys
from functools import partial

# pip3 install git+https://github.com/hpharmsen/gridworld
from gridworld.grid import Grid, draw_character_cell, TOP
import pygame
import drawing
from game_logic import Game


def key_action(key, game):
    if key == pygame.K_q:
        sys.exit()
    elif key == pygame.K_s:
        game.save_state()
    elif key == pygame.K_l:
        game.load_state()
    elif key == pygame.K_r or not game.active:
        game.start_level()
    else:
        moves = {
            pygame.K_LEFT: (-1, 0),
            pygame.K_RIGHT: (1, 0),
            pygame.K_UP: (0, -1),
            pygame.K_DOWN: (0, 1),
            pygame.K_SPACE: (0, 0),
        }
        movement = moves.get(key)
        if movement:
            game.move_hero(movement)


def mouse_click(pos, game):
    for button in game.level_buttons:
        if button.rect.collidepoint(*pos):
            game.start_level(button.level)


def timer_step(game):
    game.timer_step()


def setup_grid():
    grid = Grid(
        42,
        18,
        33,
        33,
        title='Wanderer',
        cellcolor=drawing.LIGHT_GRAY,
        margin=0,
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
    grid.set_drawaction('@', drawing.draw_hero)
    grid.set_drawaction('M', drawing.draw_monster)
    grid.set_drawaction('<', partial(draw_character_cell, character='←'))
    grid.set_drawaction('>', partial(draw_character_cell, character='→'))

    return grid


if __name__ == '__main__':
    grid = setup_grid()
    game = Game(grid)

    grid.frame_action = partial(timer_step, game=game)
    grid.key_action = partial(key_action, game=game)
    grid.mouse_click_action = partial(mouse_click, game=game)
    grid.update_statusbar = game.update_statusbar
    pygame.key.set_repeat(100, 60)
    game.start_level()
    grid.run()
