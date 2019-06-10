# TODO:
# √ Reimplement fill_queue
# √ Readme.md with dependencies and usage
# - implement mini monsters
# √ S to save level progress
# - implement balloons
# - implement time capsule and maximum moves

# GRIDWORLD TODO:
# - Borders ook mogelijk maken naast vakjes (PacMan, Kamertje verhuren)
# √ Properties with underscore plus getters/setters where needed
# - Setting background color and item color for individual cells - or not...

import sys
from functools import partial

# pip3 install git+https://github.com/hpharmsen/gridworld
from grid import Grid, TOP
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


def setup_grid():
    grid = Grid(
        42,
        18,
        33,
        33,
        title='Wanderer',
        cellcolor=drawing.LIGHT_GRAY,
        margin=0,
        font='/Library/Fonts/Arial.ttf',
        framerate=60,
        sidebar_position=TOP,
        sidebar_size=34,
        full_screen=False,
    )
    grid.update_fullscreen = False  # Only update the changed bits
    grid.set_drawaction('#', partial(grid.draw_background, color=(60, 60, 60)))
    grid.set_drawaction('=', partial(grid.draw_background, color=(70, 70, 70)))
    grid.set_drawaction(':', partial(grid.draw_background, color=(140, 120, 80)))
    grid.set_drawaction('\\', drawing.draw_down_line)
    grid.set_drawaction('O', drawing.draw_boulder)
    grid.set_drawaction('/', drawing.draw_up_line)
    grid.set_drawaction('!', drawing.draw_bomb)
    grid.set_drawaction('*', drawing.draw_money)
    grid.set_drawaction('^', drawing.draw_balloon)
    grid.set_drawaction('@', drawing.draw_hero)
    grid.set_drawaction('M', drawing.draw_monster)
    grid.set_drawaction('S', drawing.draw_baby_monster)
    grid.set_drawaction('+', drawing.draw_cage)
    grid.set_drawaction('<', partial(grid.draw_character_cell, character='←'))
    grid.set_drawaction('>', partial(grid.draw_character_cell, character='→'))

    return grid


if __name__ == '__main__':
    grid = setup_grid()
    game = Game(grid)

    grid.set_timer_action(partial(game.timer_step))
    grid.set_key_action(partial(key_action, game=game))
    grid.set_mouse_click_action(partial(mouse_click, game=game))
    grid.set_update_sidebar_action(game.update_sidebar)
    pygame.key.set_repeat(100, 60)
    game.start_level()
    grid.run()
