'''
Object classes for characters in explorer

created 2019-03-19 by NGnius'''

import random

NEXT_INT = 0
MAX_LEVEL = 42

class Person():
    def __init__(self, name, dungeon, spawn=True):
        self.basespeed = 1
        self.basedamage = 1
        self.basehealth = 1
        self.speed = 1
        self.damage = 1
        self.health = 1
        self.level = 1
        self.experience = 0
        self.name = name
        self.friendly = None # passive
        self.char = '@'
        self.max_level = MAX_LEVEL
        self.dungeon = dungeon
        if spawn:
            self.teleport(dungeon)

    def move_or_attack(self):
        target = self.get_target()
        if target is not None:
            # print(self.name, 'is attacking', target[0].name)
            self.attack(target=target)
        else:
            self.move()

    def get_target(self):
        if self.health <= 0:
            return
        my_loc = self.dungeon.find_person(self.name)
        # \/ vars below \/: (Person obj, co-ords)
        up = (self.dungeon.get_person((my_loc[0], my_loc[1]+1)), (my_loc[0], my_loc[1]+1))
        down = (self.dungeon.get_person((my_loc[0], my_loc[1]-1)), (my_loc[0], my_loc[1]-1))
        right = (self.dungeon.get_person((my_loc[0]+1, my_loc[1])), (my_loc[0]+1, my_loc[1]))
        left = (self.dungeon.get_person((my_loc[0]-1, my_loc[1])), (my_loc[0]-1, my_loc[1]))
        enemies = list()
        # attack neighbouring enemies
        if up[0] is not None and not up[0].friendly:
            enemies.append(up)
        if down[0] is not None and not down[0].friendly:
            enemies.append(down)
        if right[0] is not None and not right[0].friendly:
            enemies.append(right)
        if left[0] is not None and not left[0].friendly:
            enemies.append(left)
        if len(enemies) == 0:
            return  # no enemies to attack
        return random.choice(enemies)

    def attack(self, target=None):
        if target is not None:
            my_loc = self.dungeon.find_person(self.name)
            target[0].take_damage(self.damage)
            self.dungeon.animate(my_loc, target[1])

    def move(self):
        # locations are (x,y) co-ords
        player_loc = self.dungeon.find_person('you')
        if player_loc is None:
            return
        my_loc = self.dungeon.find_person(self.name)
        # move toward player
        if player_loc[0]>my_loc[0]:
            x_move=1
        elif player_loc[0]<my_loc[0]:
            x_move=-1
        else:
            x_move=0
        if player_loc[1]>my_loc[1]:
            y_move=1
        elif player_loc[1]<my_loc[1]:
            y_move=-1
        else:
            y_move=0
        new_loc = (my_loc[0]+x_move, my_loc[1]+y_move)
        if self.dungeon.get_person(new_loc) is None:
            # print(self.name, my_loc, '->', new_loc)
            self.dungeon.move_swap(my_loc, new_loc)

    def teleport(self, dungeon):
        if self.dungeon is not None:
            cur_loc = self.dungeon.find_person(self.name)
            if cur_loc is not None:
                self.dungeon.move_place(None, cur_loc)
        self.dungeon = dungeon
        coords = self.dungeon.find_random_location()
        self.dungeon.move_place(self, coords)
        self.level_to(self.level) # reset status changes

    def level_to(self, lvl):
        if lvl > self.max_level:
            lvl = self.max_level
        elif lvl < 1:
            lvl = 1
        self.health = self.basehealth*lvl
        self.damage = self.basedamage*lvl
        self.speed = self.basespeed*lvl
        self.level = lvl

    def take_damage(self, dmg):
        # print(self.name, 'health reduced by', dmg)
        if self.health > dmg:
            self.health -= dmg
        else:
            self.health = 0
            self.dungeon.move_place(None, self.dungeon.find_person(self.name))

class Companion(Person):
    def __init__(self, name, dungeon, **kwargs):
        super().__init__(name, dungeon, **kwargs)
        self.friendly = True # friendly
        self.level_to(self.level + 1)

class Enemy(Person):
    def __init__(self, dungeon, name=None):
        global NEXT_INT
        if name is None:
            name = str(NEXT_INT)
            NEXT_INT += 1
        super().__init__(name, dungeon)
        self.friendly = False # hostile
        self.level_to(dungeon.level + random.choice([-1, 0]))

''' Non-abstract classes '''

# enemies

class Polite(Enemy):
    def get_target(self):
        pass # does not attack

    def attack(self, target=None):
        pass # does not attack

class Outside(Enemy):
    def attack(self, target = None):
        if target is None:
            return
        my_loc = self.dungeon.find_person(self.name)
        target[0].take_damage(self.damage)
        self.dungeon.animate(my_loc, target[1])
        # shoots beam

    def get_target(self):
        if self.health <= 0:
            return
        my_loc = self.dungeon.find_person(self.name)
        potential_targets = list()
        # find friendlies with same x
        blocked = {'up': False, 'down': False}
        for y in range(1, self.dungeon.size-1):
            # up
            if not blocked['up'] and my_loc[1]+y < self.dungeon.size:
                person = self.dungeon.get_person((my_loc[0], my_loc[1]+y))
                if person is not None:
                    if person.friendly:
                        potential_targets.append([y, (person, (my_loc[0], my_loc[1]+y))])
                    else:
                        blocked['up'] = True
            # down
            if not blocked['down'] and my_loc[1]-y >= 0:
                person = self.dungeon.get_person((my_loc[0], my_loc[1]-y))
                if person is not None:
                    if person.friendly:
                        potential_targets.append([y, (person, (my_loc[0], my_loc[1]-y))])
                    else:
                        blocked['down'] = True
        # find friendlies with same y
        blocked = {'right': False, 'left': False}
        for x in range(1, self.dungeon.WIDTH-1):
            # right
            if not blocked['right'] and my_loc[0]+x < self.dungeon.WIDTH:
                person = self.dungeon.get_person((my_loc[0]+x, my_loc[1]))
                if person is not None:
                    if person.friendly:
                        potential_targets.append([x, (person, (my_loc[0]+x, my_loc[1]))])
                    blocked['right'] = True
            # left
            if not blocked['left'] and my_loc[0]-x >= 0:
                person = self.dungeon.get_person((my_loc[0]-x, my_loc[1]))
                if person is not None:
                    if person.friendly:
                        potential_targets.append([x, (person, (my_loc[0]-x, my_loc[1]))])
                    blocked['left'] = True
        if len(potential_targets) == 0:
            return
        potential_targets.sort()
        return potential_targets[0][1]

# friendlies

class Toxic(Companion):
    def __init__(self, dungeon=None):
        super().__init__('cixot', dungeon, spawn=False)
        self.char = 'c'
        self.basehealth = 2
        if dungeon is not None:
            self.level_to(self.dungeon.level)

class Internet(Companion):
    def __init__(self, dungeon=None):
        super().__init__('tenretni', dungeon, spawn=False)
        self.char = 't'
        self.basehealth = 2
        if dungeon is not None:
            self.level_to(self.dungeon.level)

class Player(Person):
    def __init__(self, dungeon=None):
        super().__init__('you', dungeon, spawn=False)
        self.friendly = True
        self.char = 'x'
        self.basehealth = 2
        if dungeon is not None:
            self.level_to(self.dungeon.level)
        self.inventory = list()

    def attack(self, using=1, target=None):
        if len(self.inventory) > using:
            self.damage += self.inventory[using]['damage']
            super().attack(target=target)
            self.damage -= self.inventory[using]['damage']
        else:
            super().attack(target=target)

    def move_or_attack(self):
        # this is handled by user, not by algorithm
        pass

    def move(self, x=0, y=0):
        my_loc = self.dungeon.find_person(self.name)
        new_loc = (my_loc[0]+x, my_loc[1]+y)
        person_at_new_loc = self.dungeon.get_person(new_loc)
        # move into empty spot or swap spots with friendly person
        if person_at_new_loc is None or person_at_new_loc.friendly:
            # print(self.name, my_loc, '->', new_loc)
            self.dungeon.move_swap(my_loc, new_loc)

    def move_up(self):
        self.move(y=1)

    def move_down(self):
        self.move(y=-1)

    def move_left(self):
        self.move(x=-1)

    def move_right(self):
        self.move(x=1)

    def teleport(self, *args, **kwargs):
        super().teleport(*args, **kwargs)
        self.level_to(self.dungeon.level)
