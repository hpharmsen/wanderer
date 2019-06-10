import os
import math
from collections import defaultdict
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
        self.babymonsters = []  # List of all monsters in the level
        self.babymonster_walldirection = defaultdict(lambda: -1)

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
        self.babymonsters = []
        self.monsters_can_move = False  # Monsters can only move after a player move
        # Scan the newly loaded level and set game state accordingly
        for y in range(self.grid.height):
            for x in range(self.grid.width):
                if self.grid[x, y] == '@':
                    self.hero_x = x
                    self.hero_y = y
                elif self.grid[x, y] in ('*', '+'):  # Cage turns to gold when captured baby monster
                    self.stars_total += 1
                elif self.grid[x, y] == 'A':
                    self.teleport_destination = (x, y)
                elif self.grid[x, y] == 'M':  # Monster or baby monster
                    self.monsters += [(x, y)]
                elif self.grid[x, y] == 'S':  # Monster or baby monster
                    self.babymonsters += [(x, y)]
                elif self.grid[x, y] == 'C':
                    # Time Capsule. Not implemented.
                    self.grid.clear((x, y))
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
            self.grid.clear((self.hero_x, self.hero_y))
            self.hero_x = x
            self.hero_y = y
            self.grid[x, y] = '@'

        def rel_move(dx, dy):
            abs_move(self.hero_x + dx, self.hero_y + dy)

        # empty or earth -> move
        if target in (None, ':'):
            rel_move(dx, dy)

        # money -> increase points and move
        elif target == '*':
            rel_move(dx, dy)
            self.stars_found += 1
            self.update_sidebar()

        # pushing a boulder or balloon sideways
        elif target in ('O', '^') and dy == 0:
            if dx == -1 and self.grid[self.hero_x - 2, self.hero_y] == None:
                self.grid[self.hero_x - 2, self.hero_y] = target
                self.game_queue.push((self.hero_x - 2, self.hero_y))
                rel_move(dx, dy)
            elif dx == 1 and self.grid[self.hero_x + 2, self.hero_y] == None:
                self.grid[self.hero_x + 2, self.hero_y] = target
                self.game_queue.push((self.hero_x + 2, self.hero_y))
                rel_move(dx, dy)

        # pushing an arrow up or down
        elif target in ('<', '>') and dx == 0:
            if dy == -1 and self.grid[self.hero_x, self.hero_y - 2] == None:
                self.grid[self.hero_x, self.hero_y - 2] = target
                self.game_queue.push((self.hero_x, self.hero_y - 2))
                rel_move(dx, dy)
            elif dy == 1 and self.grid[self.hero_x, self.hero_y + 2] == None:
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

        # exit
        elif target == 'X' and self.stars_found == self.stars_total:
            rel_move(dx, dy)
            self.win()

        self.monsters_can_move = True

    def move_monsters(self):
        def at_dir(dir):
            a = self.grid[x + directions[dir][0], y + directions[dir][1]]  # !!
            return self.grid[x + directions[dir][0], y + directions[dir][1]]

        # Monsters
        for index, monster in enumerate(self.monsters):
            x, y = monster
            best_dist_to_hero = math.sqrt((self.hero_x - x) ** 2 + (self.hero_y - y) ** 2)
            best_direction = None
            for direction in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
                dx, dy = direction
                newx, newy = x + dx, y + dy
                if not self.grid[newx, newy] in (None, '@'):
                    continue  # No space in that direction
                dist_to_hero = math.sqrt((self.hero_x - newx) ** 2 + (self.hero_y - newy) ** 2)
                if dist_to_hero < best_dist_to_hero:  # Direction found that brings the monster closer to the hero
                    best_dist_to_hero = dist_to_hero
                    best_direction = direction

            # Move monster
            if best_direction:
                dx, dy = best_direction
                newx, newy = x + dx, y + dy
                target = self.grid[newx, newy]
                if target == '@':
                    self.die(f'Killed by a monster.')
                else:
                    self.grid[newx, newy] = 'M'  # Move the monster
                    self.grid[x, y] = None
                    self.monsters[index] = (newx, newy)

        # Baby monsters
        for index, monster in enumerate(self.babymonsters):
            x, y = monster
            directions = [(-1, 0), (-1, -1), (0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1)]
            passable = (None, '@', '+', ':', 'S')
            wall = self.babymonster_walldirection[index]  # Direction of the wall this monster was following

            if wall == -1:
                # Monster is not following a wall yet, find a wall first
                for i in [0, 2, 4, 6, 1, 3, 5, 7]:  # Maybe add 1,3,5,7 otherwise use: range
                    if at_dir(i) not in passable:
                        wall = i
                        break
                else:
                    print('No wall found!')
                    for i in [0, 2, 4, 6]:  # Maybe add 1,3,5,7 otherwise use: range
                        print(at_dir(i))
                    continue  # Next monster

            # Now find a place to go
            for i in [2, 4, 6]:
                dir = (wall + i) % 8
                if dir % 2 == 1:
                    dir -= 1
                if at_dir(dir) in passable:
                    break
            else:
                continue  # No where to go, continue with next monster

            best_direction = directions[dir]
            # Move monster
            dx, dy = best_direction
            newx, newy = x + dx, y + dy
            target = self.grid[newx, newy]
            if target == '@':
                self.die(f'Killed by a baby monster.')
            elif target == '+':
                # baby monster was captured
                del self.babymonsters[index]
                del self.babymonster_walldirection[index]
                self.grid[x, y] = None  # remove the monster
                self.grid[newx, newy] = '*'  # Replace the cage buy gold
            else:
                self.grid.push((newx, newy), 'S')  # Move the monster
                self.grid.pop((x, y))
                self.babymonsters[index] = (newx, newy)
                if at_dir(dir - 1) in passable:  # cell at left is passable. Turn left.
                    newwall = dir - 4
                else:
                    newwall = dir - 2
                newwall %= 8
                # set the position of the wall the monster is following. This is needed for the next step
                self.babymonster_walldirection[index] = newwall

        self.monsters_can_move = False

    def timer_step(self):
        def try_move(x, y, dx, dy):
            source = self.grid[x, y]
            target = self.grid[x + dx, y + dy]

            if (
                (x, y) in self.speed_list and source != '^' and dx * dy == 0
            ):  # Balloons and diagonal moving objects are not lethal
                if target == '@':
                    # Uh, oh. speeding object which is no balloon hits the hero.
                    source_name = 'a falling boulder' if source == 'O' else 'a speeding arrow'
                    self.die(f'Killed by {source_name}.')
                    return True
                elif target == 'M':  # Kill monster
                    self.monsters.remove((x + dx, y + dy))
                    target = None
                elif target == 'S':  # Kill baby monster
                    for index, monster_coo in reversed(list(enumerate(self.monsters))):
                        if monster_coo == (x + dx, y + dy):
                            del self.babymonsters[index]
                            del self.babymonster_walldirection[index]
                    target = None
                elif source in ('>', '<') and target == '^':
                    target = None  # Balloon is popped by an arrow

            if target == None:
                self.grid[x + dx, y + dy] = self.grid[x, y]
                self.grid.clear((x, y))
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
                if self.grid[x, y + 1] in ('O', '/') and self.grid[x - 1, y] == None and try_move(x, y, -1, +1):
                    break  # down-left
                if self.grid[x, y + 1] in ('O', '\\') and self.grid[x + 1, y] == None and try_move(x, y, +1, +1):
                    break  # down-right
            elif symbol == '<':
                if try_move(x, y, -1, 0):  # left
                    break
                if self.grid[x - 1, y] in ('O', '\\') and self.grid[x, y - 1] == None and try_move(x, y, -1, -1):
                    break  # left-up
                if self.grid[x - 1, y] in ('O', '/') and self.grid[x, y + 1] == None and try_move(x, y, -1, +1):
                    break  # left-down
            elif symbol == '>':
                if try_move(x, y, +1, 0):  # right
                    break
                if self.grid[x + 1, y] in ('O', '/') and self.grid[x, y - 1] == None and try_move(x, y, +1, -1):
                    break  # right-up
                if self.grid[x + 1, y] in ('O', '\\') and self.grid[x, y + 1] == None and try_move(x, y, +1, +1):
                    break  # right-down
            elif symbol == '^':
                if try_move(x, y, 0, -1):  # up
                    break
                if self.grid[x, y - 1] in ('O', '/') and self.grid[x + 1, y] == None and try_move(x, y, +1, -1):
                    break  # up-left
                if self.grid[x, y - 1] in ('O', '\\') and self.grid[x - 1, y] == None and try_move(x, y, -1, -1):
                    break  # up-right

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
        # Balloons rise if one of the following . positions get's emptied:
        #
        #   . . .
        #   . . .
        #   . ^ .
        #
        # So always next to or one or two levels under the boulder, above the balloon
        # or next to or one or two levels in front of the arrow.

        for dy in range(-2, 3, +1):  # Toch +1 ipv -1 omdat boulders voor arrows moeten gaan
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
        self.level_buttons = drawing.show_levels(self.grid, self.level)

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
