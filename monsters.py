import math

self.mini_monster_wall_direction = defaultdict(lambda: -1)


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
            wall = self.mini_monster_wall_direction[monster]  # Direction of the wall this monster was following

            if wall == -1:
                # Monster is not following a wall yet, find a wall first
                for i in [0, 2, 4, 6]:  # Maybe add 1,3,5,7 otherwise use: range
                    if at_dir(i) not in passable:
                        wall = i
                        break
                else:
                    print('No wall found!')
                    continue  # Next monster

            # Now find a place to go
            for i in [2, 4, 6]:
                dir = (wall + i) % 8
                if at_dir(dir) in passable:
                    break
            else:
                continue  # No where to go, continue with next monster

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
                # Mini monster was captured
                self.monsters.remove((x, y))
                self.grid[x, y] = ' '  # remove the monster
                self.grid[newx, newy] = '*'  # Replace the cage buy gold
            else:
                self.grid[newx, newy] = monster_type  # Move the monster
                self.grid[x, y] = ' '
                self.monsters[index] = (newx, newy)
                if monster_type == 'S':
                    if at_dir(dir - 1) in passable:  # cell at left is passable. Turn left.
                        newwall = dir - 4
                    else:
                        newwall = dir - 2
                    newwall %= 8
                    # set the position of the wall the monster is following. This is needed for the next step
                    del self.mini_monster_wall_direction[monster]
                    self.mini_monster_wall_direction[(newx, newy)] = newwall
                # self.fill_queue(x, y)
                # self.fill_queue(newx, newy)
    self.monsters_can_move = False
