import os
import math
import drawing
from game_queue import GameQueue

LEVEL_FILE = 'lastlevel.txt'
SAVE_FILE = 'savegame.txt'


class Game:
    def __init__(self, grid):
        self.grid = grid
        self.active = False
        self.stars_total = 0
        self.stars_found = 0
        self.teleport_destination = None
        if os.path.isfile(LEVEL_FILE):
            with open(LEVEL_FILE) as f:
                self.level = int(f.read())
        else:
            self.level = 1

        self.game_queue = GameQueue(self.grid)
        self.speed_list = []  # Keep track of moving (lethal) objects
        self.monsters = []  # List of all monsters in the level
        self.level_buttons = drawing.level_buttons(grid, self.level)

    def start_level(self, level=-1):
        self.level = level if level > -1 else self.level
        self.load_level(level)
        self.init_level()

    def load_level(self, level):
        self.grid.auto_update = False
        self.grid.load(f'levels/level{self.level}.txt')
        self.grid.auto_update = True
        self.grid.redraw()
        with open(LEVEL_FILE, 'w') as f:
            f.write(str(self.level))

    def init_level(self):
        self.stars_total = 0
        self.stars_found = 0
        self.teleport_destination = None
        self.monsters = []
        self.monsters_can_move = False  # Monsters can only move after a player move
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
                elif self.grid[x, y] in ('M', 'S'):  # Monster or baby monster
                    self.monsters += [(x, y)]
                elif self.grid[x, y] == 'C':
                    # Time Capsule. Not implemented.
                    self.grid[x, y] = ' '
        self.update_sidebar()
        self.game_queue.reset()
        self.active = True

    def move_hero(self, movement):

        self.speed_list = []
        if not self.active:
            return  # No moving by dead hero's

        dx, dy = movement
        target = self.grid[self.hero_x + dx, self.hero_y + dy]

        def abs_move(x, y):
            self.game_queue.insert((x, y))  # Set previous hero position as 'dirty'
            self.fill_queue(self.hero_x, self.hero_y)
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
            self.update_sidebar()

        # boulder of balloon en opzij en niks achter bolder/balloon -> move bolder/balloon en zelf
        elif target == 'O' and dy == 0:
            if dx == -1 and self.grid[self.hero_x - 2, self.hero_y] == ' ':
                self.grid[self.hero_x - 2, self.hero_y] = target
                self.game_queue.push((self.hero_x - 2, self.hero_y))
                rel_move(dx, dy)
            elif dx == 1 and self.grid[self.hero_x + 2, self.hero_y] == ' ':
                self.grid[self.hero_x + 2, self.hero_y] = target
                self.game_queue.push((self.hero_x + 2, self.hero_y))
                rel_move(dx, dy)

        # arrow en omhoog/laag en niks achter arrow -> move arrow en zelf
        elif target in ('<', '>') and dx == 0:
            if dy == -1 and self.grid[self.hero_x, self.hero_y - 2] == ' ':
                self.grid[self.hero_x, self.hero_y - 2] = target
                self.game_queue.push((self.hero_x, self.hero_y - 2))
                rel_move(dx, dy)
            elif dy == 1 and self.grid[self.hero_x, self.hero_y + 2] == ' ':
                self.grid[self.hero_x, self.hero_y + 2] = target
                self.game_queue.push((self.hero_x, self.hero_y + 2))
                rel_move(dx, dy)

        # teleport -> teleport
        elif target == 'T':
            rel_move(dx, dy)
            abs_move(*self.teleport_destination)

        # bomb -> dead
        elif target == '!':
            self.die('Killed by an exploding bomb.')

        # monster -> dead
        elif target == 'M':
            self.die('Killed by walking into a monster.')

        # Exit
        elif target == 'X' and self.stars_found == self.stars_total:
            rel_move(dx, dy)
            self.win()

        self.monsters_can_move = True

    def move_monsters(self):
        def at_dir(dir):
            return self.grid[x + directions[dir][0], y + directions[dir][1]]

        # Monsters
        for index, monster in enumerate(self.monsters):
            x, y = monster
            monster_type = self.grid[x, y]
            if monster_type == 'M':  # Full grown monster
                best_dist_to_hero = math.sqrt((self.hero_x - x) ** 2 + (self.hero_y - y) ** 2)
                best_direction = None
                for direction in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
                    dx, dy = direction
                    newx, newy = x + dx, y + dy
                    if not self.grid[newx, newy] in (' ', '@'):
                        continue  # No space in that direction
                    dist_to_hero = math.sqrt((self.hero_x - newx) ** 2 + (self.hero_y - newy) ** 2)
                    if dist_to_hero < best_dist_to_hero:  # Direction found that brings the monster closer to the hero
                        best_dist_to_hero = dist_to_hero
                        best_direction = direction
            else:  # Baby monster
                directions = [(-1, 0), (-1, -1), (0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1)]
                passable = (' ', '@', '+')
                dir = 0
                # zoek de muur
                a = at_dir(dir)
                while at_dir(dir) in passable:
                    dir += 1
                    a = at_dir(dir)
                # ga langs de muur
                while at_dir(dir) not in passable:
                    dir = (dir + 1) % 8
                    b = at_dir(dir)
                if dir % 2 == 1:
                    dir = (dir + 1) % 8
                best_direction = directions[dir]
            # Move monster
            if best_direction:
                dx, dy = best_direction
                newx, newy = x + dx, y + dy
                target = self.grid[newx, newy]
                if target == '@':
                    baby = 'baby ' if monster_type == 'S' else ''
                    self.die(f'Killed by a {baby}monster.')
                elif target == '+':
                    # Monster was captured
                    self.monsters.remove((x, y))
                    self.grid[x, y] = ' '  # remove the monster
                    self.grid[newx, newy] = ' '  # remove the cage
                else:
                    self.grid[newx, newy] = monster_type  # Move the monster
                    self.grid[x, y] = ' '
                    self.monsters[index] = (newx, newy)
                    # self.fill_queue(x, y)
                    # self.fill_queue(newx, newy)
        self.monsters_can_move = False

    def timer_step(self):
        def try_move(x, y, dx, dy):
            source = self.grid[x, y]
            target = self.grid[x + dx, y + dy]

            if (x, y) in self.speed_list:
                if target == '@':
                    # Uh, oh. speeding object hits the hero.
                    source_name = 'a falling boulder' if source == 'O' else 'a speeding arrow'
                    self.die(f'Killed by {source_name}.')
                    return True
                elif target == 'M':  # Kill monster
                    self.monsters.remove((x + dx, y + dy))
                    target = ' '

            if target == ' ':
                self.grid[x + dx, y + dy] = self.grid[x, y]
                self.grid[x, y] = ' '
                self.game_queue.insert((x, y))
                self.game_queue.insert(
                    (x + dx, y + dy)
                )  # Put new square in the beginning of list for further fall or flight
                self.fill_queue(x, y)  # Stir up old square
                self.speed_list += [(x + dx, y + dy)]
                return True
            return False

        if not self.active:
            return

        while self.game_queue:  # Loop until interesting symbol found in the queue or queue is empty
            coo = self.game_queue.get()
            x, y = coo
            symbol = self.grid[x, y]
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

        if self.monsters_can_move and not self.game_queue:  # Player has moved and all reactions are done
            self.move_monsters()  # Now move the monsters

    def fill_queue(self, x, y):
        # Boulders fall if one of the following . positions get's emptied:
        #
        #   . O .
        #   . . .
        #   . . .
        #
        # Arrows fly if one of the following . positions get's emptied:
        #
        #   . . .    . . .
        #   > . .    . . <
        #   . . .    . . .
        #
        # So always next to or one or two levels under the boulder
        # and next to or one or two levels in front of the arrow.

        for dy in range(-2, 3):
            for dx in [0, -1, 1, -2, 2]:  # More priority from the middele out
                c = self.grid[x + dx, y + dy]
                if (
                    (c == '<' and dx >= 0 and -2 < dy < 2)
                    or (c == '>' and dx <= 0 and -2 < dy < 2)
                    or (c == 'O' and dy <= 0 and -2 < dx < 2)
                    or (c == '^' and dy >= 0 and -2 < dx < 2)
                ):
                    self.game_queue.push((x + dx, y + dy))

    def update_sidebar(self):
        text = f'Level {self.level}                 {self.stars_found}/{self.stars_total} gold found'
        drawing.sidebar_message(self.grid, (2, 15), text)
        drawing.show_levels(self.grid, self.level_buttons, self.level)

    def die(self, message):
        drawing.full_screen_message(self.grid, drawing.RED, message)
        self.active = False

    def win(self):
        drawing.full_screen_message(self.grid, drawing.GREEN, 'Level complete!')
        self.level += 1
        self.active = False

    def save_state(self):
        if not self.active:
            return
        self.grid.save(SAVE_FILE)

    def load_state(self):
        if not os.path.isfile(SAVE_FILE):
            return
        self.grid.auto_update = False
        self.grid.load(SAVE_FILE)
        self.grid.auto_update = True
        self.init_level()
        self.grid.redraw()
