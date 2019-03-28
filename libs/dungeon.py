'''
Dungeon object class

created 2019-03-19 by NGnius '''
# import math
import random

DEFAULT_SIZE = 16
WIDTH = 42
ANIMATION_CHAR = '*'
BLANK_CHAR = '.'
PORTAL_CHAR = '0'

class Dungeon():
    def __init__(self, size=DEFAULT_SIZE, level=1):
        self.WIDTH = WIDTH
        self.size = size
        self.level = level
        # make board
        self._board = self._make_board()  # list of list; size^2
        self._animated_board = self._make_board()
        # 2 randomly placed portals
        self.portals = (self.find_random_location(), self.find_random_location())

    def animate(self, fr, to, _char=ANIMATION_CHAR):
        vector = (to[0]-fr[0], to[1]-fr[1])
        n = (vector[0]**2 + vector[1]**2)**(0.5)
        uvector = (vector[0]/n, vector[1]/n)
        # print(uvector, 'is your vector, Victor')
        for i in range(1, max(abs(vector[0]), abs(vector[1]))):
            self._animated_board[fr[0]+round(i*uvector[0])][fr[1]+round(i*uvector[1])] = _char
        self._animated_board[to[0]][to[1]] = _char  # just in case it's missed by vector drawing

    def move_place(self, obj, coords):
        if self._verify_coords(coords):
            self._board[coords[0]][coords[1]] = obj

    def move_swap(self, coords1, coords2):
        if self._verify_coords(coords1) and self._verify_coords(coords2):
            self._board[coords1[0]][coords1[1]], self._board[coords2[0]][coords2[1]] = self._board[coords2[0]][coords2[1]], self._board[coords1[0]][coords1[1]]

    def _make_board(self, fill=None):
        board = list()
        for x in range(WIDTH):
            board.append(list())
            for y in range(self.size):
                board[x].append(fill)
        return board

    def draw_board(self, blank=BLANK_CHAR):
        board_str = ''
        for y in range(self.size):
            row_str = ''
            for x in range(WIDTH):
                if self._animated_board[x][y] is not None:
                    row_str += self._animated_board[x][y]
                    self._animated_board[x][y] = None  # reset animations as we go
                elif (x,y) in self.portals:
                    row_str += PORTAL_CHAR
                elif self._board[x][y] is not None:
                    row_str += self._board[x][y].char
                else:
                    row_str += blank
            board_str = '\n' + row_str + board_str
        return board_str

    def do_turn(self):
        done_turn = list()
        # do move or attack for people on board
        for x in range(WIDTH):
            for y in range(self.size):
                person = self._board[x][y]
                if person is not None and person.name not in done_turn:
                    # print('Move/Attacking', person.name)
                    person.move_or_attack()
                    done_turn.append(person.name)

    def get_person(self, coords):
        if coords[0] >= WIDTH or coords[1] >= self.size:
            return
        return self._board[coords[0]][coords[1]]

    def find_person(self, name):
        for x in range(WIDTH):
            for y in range(self.size):
                person = self._board[x][y]
                if person is not None:
                    if person.name == name:
                        return (x,y)

    def find_random_location(self):
        person_at = not None  # legit
        while person_at is not None:
            coords = (random.randrange(0, self.size), random.randrange(0, self.size))
            person_at = self.get_person(coords)
        return coords

    def _verify_coords(self, coords):
        if coords[0] >= WIDTH or coords[0] < 0:
            return False
        if coords[1] >= self.size or coords[1] < 0:
            return False
        return True
