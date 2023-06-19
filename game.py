#!/usr/bin/python3

import pygame
import random
import sys
import os
import gui
from enum import Enum

GRID_SIZE = 40
LEVEL_W = GRID_SIZE * 10
LEVEL_H = GRID_SIZE * 20

pygame.font.init()
FONT_ARIAL = pygame.font.Font(os.path.join("assets", "fonts", "Arialn.ttf"), 40)
FONT_ARIAL_55 = pygame.font.Font(os.path.join("assets", "fonts", "Arialn.ttf"), 55)

IMG_BLOCK_BLUE = pygame.image.load(os.path.join("assets", "block_blue.png"))
IMG_BLOCK_CYAN = pygame.image.load(os.path.join("assets", "block_cyan.png"))
IMG_BLOCK_GREEN = pygame.image.load(os.path.join("assets", "block_green.png"))
IMG_BLOCK_ORANGE = pygame.image.load(os.path.join("assets", "block_orange.png"))
IMG_BLOCK_PURPLE = pygame.image.load(os.path.join("assets", "block_purple.png"))
IMG_BLOCK_RED = pygame.image.load(os.path.join("assets", "block_red.png"))
IMG_BLOCK_YELLOW = pygame.image.load(os.path.join("assets", "block_yellow.png"))

IMG_BACKGROUND = pygame.image.load(os.path.join("assets", "cathedral.jpg"))

BLOCK_IMGS = [False,
              IMG_BLOCK_BLUE,
              IMG_BLOCK_CYAN,
              IMG_BLOCK_GREEN,
              IMG_BLOCK_ORANGE,
              IMG_BLOCK_PURPLE,
              IMG_BLOCK_RED,
              IMG_BLOCK_YELLOW]

def get_rotations(piece):
    result = [piece]
    result.append(list (map(lambda x: (-x[1], x[0]),piece)))
    result.append(list (map(lambda x: (-x[0], -x[1]),piece)))
    result.append(list (map(lambda x: (x[1], -x[0]),piece)))
    return result

all_pieces = [[[(0,0), (-1,0), (1,0), (-2,0)],
              [(0,0), (0,-1), (0,2), (0,1)]], # I
              get_rotations([(0,0), (-1,0), (-1,-1), (1,0)]), # J
              get_rotations([(0,0), (-1,0), (1,0), (-1,1)]), # L
              [[(0,0), (0,1), (-1,0), (-1,1)]], # O
              [[(0,0), (-1,0), (-1,-1), (0,1)],
               [(0,0), (0,-1), (1, -1), (-1,0)]], # S
              [[(0,0), (-1,-1), (1,0), (0,-1)],
               [(0,0), (1,-1), (0, 1), (1,0)]], # Z
              get_rotations([(0,0), (0,-1), (1,0), (-1,0)])] # T

class Tet:
    x = LEVEL_W//2
    y = 0
    piece_w_rot = 0
    rot_index = 0
    ticks_per_frame = 3
    current_tick = 0
    move_on_tick = 100 # block moves down on move_on_tick.
    level = 0
    color = 1

    def __init__(self
                 ,level
                 ,x=LEVEL_W//2
                 ,y=0
                 ,piece=all_pieces[random.randint(0,6)]
                 ,tpf=5):
        self.piece_w_rot = piece.copy()
        self.x = x
        self.y = y
        self.ticks_per_frame = tpf
        self.level = level
        self.color = random.randint(1,7)
    # increases current_tick by ticks_per_frame on each call.
    # returns True if current_tick reached move_on_tick and sets current_tick to 0. Otherwise False
    def tick(self):
        if self.current_tick >= self.move_on_tick:
            self.current_tick = 0
            return True
        else:
            self.current_tick += self.ticks_per_frame
            return False

    def update(self):
        if self.tick():
            if self.level.occupied(0, 1): # would collide on move
                self.level.assimilate()
                return
            self.y += GRID_SIZE

    def move_r(self):
        if not self.level.occupied(1):
            self.x += GRID_SIZE

    def move_l(self):
        if not self.level.occupied(-1):
            self.x -= GRID_SIZE

    def rotate(self):
        if self.rot_index < len(self.piece_w_rot) - 1:
            self.rot_index += 1
        else:
            self.rot_index = 0
    # tries to rotate the piece, if doing so would cause it to occupy a space that is already occupied
    # then it won't rotate
    def try_rotate(self):
        before_rot = self.rot_index
        self.rotate()
        if self.level.occupied():
            self.rot_index = before_rot

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    def set_x(self, x):
        self.x = x

    def set_y(self, y):
        self.y = y

    def getPiece(self):
        return self.piece_w_rot.copy()

    def setPiece(self, piece):
        self.piece_w_rot = piece

    def getRotIndex(self):
        return self.rot_index

    def setRotIndex(self, index):
        self.rot_index = index

    def get_color(self):
        return self.color

class Level:
    map = [[0 for i in range(10)] for j in range(20)]
    tet = 0
    game = False

    def __init__(self, game):
        self.map = [[0 for i in range(10)] for j in range(20)]
        self.tet = Tet(self)
        self.game = game

    def get_map(self):
        return self.map.copy()

    def get_tet(self):
        return self.tet

    def update(self):
        self.tet.update()

    def assimilate(self):
        for pr in self.tet.getPiece()[self.tet.getRotIndex()]:
            self.map[self.tet.get_y() // GRID_SIZE + pr[1]][self.tet.get_x() // GRID_SIZE + pr[0]] = self.tet.get_color()
        self.clear_lines()
        self.game.update_score(1)
        self.tet = Tet(self, LEVEL_W // 2, 0, all_pieces[random.randint(0,6)])

    def occupied(self, x_off=0, y_off=0):
        for pr in self.tet.getPiece()[self.tet.getRotIndex()]:
            y = self.tet.get_y() // GRID_SIZE + pr[1] + y_off
            x = self.tet.get_x() // GRID_SIZE + pr[0] + x_off
            if y >= 20 or x >= 10 or x < 0:
                return True
            if self.map[y][x] != 0:
                return True
        return False

    def clear_lines(self):
        lines_cleared = 0
        for row_index, row in enumerate(self.map):
            filled = True
            for element in row:
                if element == 0:
                    filled = False
            if filled:
                for element_index, element in enumerate(self.map[row_index]):
                    self.map[row_index][element_index] = 0
                self.push_lines(row_index)
                lines_cleared += 1
        self.game.update_score(10 * lines_cleared)

    def push_lines(self, row_index):
        del self.map[row_index]
        self.map.insert(0, [0 for i in range(10)])

    def check_game_over(self):
        return any(map(lambda x: x != 0, self.map[0]))

class Game:
    game_states = Enum("game_states", ["menu", "pause", "playing", "gameover"])
    game_state = game_states.menu
    score = 0
    level = False
    gui = []
    quit = False

    def __init__(self, gui):
        self.gui = gui
        self.init_state_menu()

    def loop(self):
        if self.game_state == self.game_states.menu:
            pass
        elif self.game_state == self.game_states.pause:
            pass
        elif self.game_state == self.game_states.playing:
            self.level.update()
            if self.level.check_game_over():
                self.change_state(self.game_states.gameover)

        self.handle_input()

        return self.quit

    def handle_input(self):
        events = pygame.event.get()

        for event in events:
            if event.type == pygame.QUIT:
                self.quit = True

            if self.game_state == self.game_states.playing:
                tet = self.level.get_tet()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        tet.try_rotate()
                    if event.key == pygame.K_a:
                        tet.move_l()
                    elif event.key == pygame.K_d:
                        tet.move_r()
                    if event.key == pygame.K_ESCAPE:
                        self.init_state_pause()

            elif self.game_state == self.game_states.pause:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.init_state_playing()

            elif self.game_state == self.game_states.menu:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_w:
                        self.gui["main_menu"].update_selected(-1)
                    if event.key == pygame.K_s:
                        self.gui["main_menu"].update_selected(1)
                    if event.key == pygame.K_SPACE:
                        if self.gui["main_menu"].get_selected() != False:
                            self.gui["main_menu"].get_selected()[1].on_click()

    def init_state_menu(self):
        self.gui.clear()
        self.gui["main_menu"] = gui.Container(LEVEL_W // 2,
                                              LEVEL_H // 2) \
        .set_border_w(3) \
        .set_border_color((160,160,160)) \
        .set_color((200,200,200)) \
        .set_corner_roundness(10) \
        .set_padding((10,10,10,10)) \
        .set_child_spacing(5) 
        self.gui["main_menu"].add_child(gui.Text("pygame-tetris", FONT_ARIAL_55))
        self.gui["main_menu"].add_child(gui.Button(gui.Text("Start Game", FONT_ARIAL)) \
        .set_border_w(3) \
        .set_border_color((0,0,0)) \
        .set_color_deselected((100,100,100)) \
        .set_color_selected((100,200,100)) \
        .set_padding((5,10,5,10)) \
        .set_on_click(self,self.init_state_playing, []))
        self.gui["main_menu"].add_child(gui.Button(gui.Text("Quit", FONT_ARIAL)) \
        .set_border_w(3) \
        .set_border_color((0,0,0)) \
        .set_color_deselected((100,100,100)) \
        .set_color_selected((100,200,100)) \
        .set_padding((5,10,5,10)) \
        .set_on_click(self,self.set_quit, []))

    def init_state_playing(self):
        self.gui.clear()

        if self.level == False:
            self.level = Level(self)

        self.update_score_gui()

        self.game_state = self.game_states.playing

    def init_state_pause(self):
        self.gui["pause_menu"] = gui.Container(LEVEL_W // 2, 
                                               LEVEL_H // 2) \
        .set_border_w(3) \
        .set_border_color((160,160,160)) \
        .set_color((200,200,200)) \
        .set_corner_roundness(10) \
        .set_padding((10,10,10,10)) \
        .set_child_spacing(0) \
        .add_child(gui.Text("Game Paused", FONT_ARIAL_55)) \
        .add_child(gui.Text("Test", FONT_ARIAL))

        self.game_state = self.game_states.pause

    def init_state_gameover(self):
        self.gui.clear()

        self.game_state = self.game_states.gameover
        self.level = False
        self.score = 0

    def update_score_gui(self):
        self.gui["score_gui"] = gui.Text("Score: " + str(self.score), FONT_ARIAL)

    def update_score(self, score):
        self.score += score
        self.update_score_gui()

    def get_level(self):
        return self.level

    def set_quit(self):
        self.quit = True

def drawTet(screen, piece):
    for actual in (piece.getPiece())[piece.getRotIndex()]:
        pygame.draw.rect(screen, (100, 100, 0), pygame.Rect(piece.get_x() + actual[0] * GRID_SIZE,
                                                            piece.get_y() + actual[1] * GRID_SIZE,
                                                            GRID_SIZE,
                                                            GRID_SIZE))
        screen.blit(BLOCK_IMGS[piece.get_color()], (piece.get_x() + actual[0] * GRID_SIZE,
                          piece.get_y() + actual[1] * GRID_SIZE))

def drawLevel(screen, level):
    for row_index, row  in enumerate(level.get_map()):
        for column_index, column in enumerate(row):
            if column != 0:
                screen.blit(BLOCK_IMGS[column], (column_index * GRID_SIZE, row_index * GRID_SIZE))
def main():
    pygame.init()
    screen = pygame.display.set_mode((LEVEL_W, LEVEL_H))
    clock = pygame.time.Clock()
    running = True

    gui = {}

    game = Game(gui)

    def draw_before_gui():
        screen.blit(IMG_BACKGROUND, (0, 0))
        if not game.get_level() == False:
            drawTet(screen, game.get_level().get_tet())
            drawLevel(screen, game.get_level())

    while running:
        clock.tick(60)

        running = not game.loop()

        draw_before_gui()
        for element in gui.values():
            element.update()
            element.draw(screen)
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
