from typing import List
import drawing
from game_queue import GameQueue
import pygame  # TODO: remove dependency on pygame from game.py
from gridworld.grid import log


class Game:
    def __init__(self, grid):
        self.grid = grid
        self.level = 1
        self.active = False
        self.stars_to_go = 0
        self.teleport_destination = None
        self.dead = False

        self.game_queue = GameQueue(self.grid)
        self.speed_list = []  # Keep track of moving (lethal) objects

    def start_level(self, level=-1):
        log('stat_level')
        self.level = level if level > -1 else 1
        self.grid.auto_update = False
        self.grid.load(f'levels/level{self.level}.txt')
        self.grid.auto_update = True
        self.grid.redraw()

        # Scan the newly loaded level and set game state accordingly
        for y in range(self.grid.height):
            for x in range(self.grid.width):
                if self.grid[x, y] == '@':
                    self.hero_x = x
                    self.hero_y = y
                elif self.grid[x, y] == '*':
                    self.stars_to_go += 1
                elif self.grid[x, y] == 'T':
                    self.teleport_destination = (x, y)
        self.game_queue.reset()
        self.active = True

    def move(self, movement):

        self.speed_list = []
        if self.dead:
            return  # No moving by dead hero's

        log('game.move')

        dx, dy = movement
        target = self.grid[self.hero_x + dx, self.hero_y + dy]

        def abs_move(x, y):
            self.fill_queue(self.hero_x, self.hero_y)
            self.fill_queue(x, y)
            self.grid[self.hero_x, self.hero_y] = ' '
            self.hero_x = x
            self.hero_y = y
            self.grid[x, y] = '@'

        def rel_move(dx, dy):
            abs_move(self.hero_x + dx, self.hero_y + dy)

        # leeg, earth -> move
        if target in (' ', ':'):
            rel_move(dx, dy)

        # geld -> punten omhoog en move
        elif target == '*':
            rel_move(dx, dy)
            self.stars_to_go -= 1
            sx, sy, sw, sh = self.grid.get_statusbar_dimensions()
            self.grid.clear_statusbar(drawing.DARKGRAY)
            text = f'{self.stars_to_go} bags to go'
            font = pygame.font.Font(self.grid.itemfont, 30)
            rendered = font.render(text, True, drawing.WHITE)
            # text_rect = text.get_rect()
            # text_rect.center = (x + w * pos[0] // 100, y + h * pos[1] // 100)
            self.grid.screen.blit(rendered, (sx, sy))

        # boulder of balloon en opzij en niks achter bolder/balloon -> move bolder/balloon en zelf
        elif target == 'O' and dy == 0:
            if dx == -1 and self.grid[self.hero_x - 2, self.hero_y] == ' ':
                self.grid[self.hero_x - 2, self.hero_y] = target
                rel_move(dx, dy)
            elif dx == 1 and self.grid[self.hero_x + 2, self.hero_y] == ' ':
                self.grid[self.hero_x + 2, self.hero_y] = target
                rel_move(dx, dy)

        # arrow en omhoog/laag en niks achter arrow -> move arrow en zelf
        elif target in ('<', '>') and dx == 0:
            if dy == -1 and self.grid[self.hero_x, self.hero_y - 2] == ' ':
                self.grid[self.hero_x, self.hero_y - 2] = target
                rel_move(dx, dy)
            elif dy == 1 and self.grid[self.hero_x, self.hero_y + 2] == ' ':
                self.grid[self.hero_x, self.hero_y + 2] = target
                rel_move(dx, dy)

        # teleport -> teleport
        elif target == 'T':
            rel_move(dx, dy)
            abs_move(*self.teleport_destination)

        # bom -> dood
        elif target == '!':
            self.die('Hit by bomb')

    log('end game.move')

    def step(self):
        def try_move(x, y, dx, dy):
            source = self.grid[x, y]
            target = self.grid[x + dx, y + dy]

            if (x, y) in self.speed_list and target == '@':
                # Uh, oh. speeding object hits the hero.
                self.die(f'Hit by {source}')
                return True

            if target == ' ':
                self.grid[x + dx, y + dy] = self.grid[x, y]
                self.grid[x, y] = ' '
                self.fill_queue(x, y)
                self.fill_queue(x + dx, y + dy)
                self.speed_list += [(x + dx, y + dy)]
                return True
            return False

        #log('game.step', len(self.game_queue))
        while self.game_queue:  # Loop until interesting symbol found in the queue or queue is empty
            coo = self.game_queue.get()
            x, y = coo
            symbol = self.grid[x, y]
            log( 'game action', x,y, symbol )
            if symbol == 'O':
                if try_move(x, y, 0, +1):  # down
                    break
                if self.grid[x, y + 1] in ('O', '/') and self.grid[x - 1, y] == ' ' and try_move(x, y, -1, +1):
                    break  # down-left
                if self.grid[x, y + 1] in ('O', '\\') and self.grid[x + 1, y] == ' ' and try_move(x, y, +1, +1):
                    break  # down-right
            elif symbol == '<':
                if try_move(x, y, -1, 0):  # left
                    break
                if self.grid[x - 1, y] in ('O', '\\') and self.grid[x, y - 1] == ' ' and try_move(x, y, -1, -1):
                    break  # left-up
                if self.grid[x - 1, y] in ('O', '/') and self.grid[x, y + 1] == ' ' and try_move(x, y, -1, +1):
                    break  # left-down
            elif symbol == '>':
                if try_move(x, y, +1, 0):  # right
                    break
                if self.grid[x + 1, y] in ('O', '/') and self.grid[x, y - 1] == ' ' and try_move(x, y, +1, -1):
                    break  # right-up
                if self.grid[x + 1, y] in ('O', '\\') and self.grid[x, y + 1] == ' ' and try_move(x, y, +1, +1):
                    break  # right-down

        #log('end game.step')


    def fill_queue(self, x, y):
        # Check for items that might move
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                if self.grid[x + dx, y + dy] != ' ':
                    self.game_queue.put((x + dx, y + dy))

    def die(self, message):
        self.grid.screen.fill(drawing.RED)
        pygame.display.flip()
        self.dead = True
