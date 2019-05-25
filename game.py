from typing import List
import drawing
from game_queue import GameQueue
from gridworld.grid import log


class Game:
    def __init__(self, grid):
        self.grid = grid
        self.level = 1
        self.active = False
        self.stars_total = 0
        self.stars_found = 0
        self.teleport_destination = None

        self.game_queue = GameQueue(self.grid)
        self.speed_list = []  # Keep track of moving (lethal) objects
        self.level_buttons = drawing.level_buttons(grid)

    def start_level(self, level=-1):
        log('stat_level')
        self.level = level if level > -1 else self.level
        self.grid.auto_update = False
        self.grid.load(f'levels/level{self.level}.txt')
        self.grid.auto_update = True
        self.grid.redraw()

        self.stars_total = 0
        self.stars_found = 0
        self.teleport_destination = None
        # Scan the newly loaded level and set game state accordingly
        for y in range(self.grid.height):
            for x in range(self.grid.width):
                if self.grid[x, y] == '@':
                    self.hero_x = x
                    self.hero_y = y
                elif self.grid[x, y] == '*':
                    self.stars_total += 1
                elif self.grid[x, y] == 'A':
                    self.teleport_destination = (x, y)
                elif self.grid[x,y] == 'C':
                    # Time Capsule. Not implemented.
                    self.grid[x,y] = ' '
        self.update_statusbar()
        self.game_queue.reset()
        self.active = True

    def move(self, movement):

        self.speed_list = []
        if not self.active:
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
            self.stars_found += 1
            self.update_statusbar()

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

        # bomb -> dead
        elif target == '!':
            self.die('Killed by an exploding bomb.')

        # Exit
        elif target == 'X' and self.stars_found==self.stars_total:
            rel_move(dx, dy)
            self.win()

    log('end game.move')

    def step(self):
        def try_move(x, y, dx, dy):
            source = self.grid[x, y]
            target = self.grid[x + dx, y + dy]

            if (x, y) in self.speed_list and target == '@':
                # Uh, oh. speeding object hits the hero.
                source_name = 'a falling boulder' if source == 'O' else 'a speeding arrow'
                self.die(f'Killed by {source_name}.')
                return True

            if target == ' ':
                self.grid[x + dx, y + dy] = self.grid[x, y]
                self.grid[x, y] = ' '
                self.fill_queue(x, y)
                self.fill_queue(x + dx, y + dy)
                self.speed_list += [(x + dx, y + dy)]
                return True
            return False

        # log('game.step', len(self.game_queue))
        while self.game_queue:  # Loop until interesting symbol found in the queue or queue is empty
            coo = self.game_queue.get()
            x, y = coo
            symbol = self.grid[x, y]
            log('game action', x, y, symbol)
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

        # log('end game.step')

    def fill_queue(self, x, y):
        # Check for items that might move
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                if self.grid[x + dx, y + dy] != ' ':
                    self.game_queue.put((x + dx, y + dy))

    def update_statusbar(self):
        text = f'Level {self.level}                 {self.stars_found}/{self.stars_total} gold found'
        drawing.status_bar_message(self.grid, (2, 15), text)
        drawing.show_levels(self.grid, self.level_buttons)

    def die(self, message):
        drawing.full_screen_message(self.grid, drawing.RED, message)
        self.active = False

    def win(self):
        drawing.full_screen_message(self.grid, drawing.GREEN, 'Level complete!')
        self.level += 1
        self.active = False
