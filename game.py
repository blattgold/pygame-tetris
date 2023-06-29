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
pygame.mixer.init()

FONT_ARIAL_25 = pygame.font.Font(os.path.join("assets", "fonts", "Arialn.ttf"), 25)
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

KEYBINDS = {"MOVE_L": pygame.K_a,
            "MOVE_R": pygame.K_d,
            "ROTATE": pygame.K_SPACE,
            "DROP": pygame.K_s,
            "PAUSE": pygame.K_ESCAPE,
            "GUI_UP": pygame.K_w,
            "GUI_DOWN": pygame.K_s,
            "GUI_ACTION": pygame.K_RETURN}

SFX = {"DROP": pygame.mixer.Sound(os.path.join("assets", "sfx", "drop.wav")),
       "CLEAR1": pygame.mixer.Sound(os.path.join("assets", "sfx", "clear1.wav")),
       "CLEAR2": pygame.mixer.Sound(os.path.join("assets", "sfx", "clear2.wav")),
       "CLEAR3": pygame.mixer.Sound(os.path.join("assets", "sfx", "clear3.wav")),
       "CLEAR4": pygame.mixer.Sound(os.path.join("assets", "sfx", "clear4.wav"))}

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
    dropping = False

    def __init__(self
                 ,level
                 ,x=LEVEL_W//2
                 ,y=0
                 ,piece=all_pieces[random.randint(0,6)]
                 ,tpf=2):
        self.piece_w_rot = piece.copy()
        self.x = x
        self.y = y
        self.level = level
        self.color = random.randint(1,7)
        self.dropping = False
        self.rot_index = 0
        self.tpf = tpf
        self.tpf_adjusted = tpf * self.level.get_difficulty()
        self.dropping_tpf = tpf * self.level.get_difficulty() * 10 # how many ticks until update per frame if drop key is held
        self.current_tick = 0
        self.move_on_tick = 100 # block moves down on move_on_tick.

    def tick(self):
        '''
        increases current_tick by tpf on each call.
        returns True if current_tick reached move_on_tick and sets current_tick to 0. Otherwise False
        '''
        if self.current_tick >= self.move_on_tick:
            self.current_tick = 0
            return True
        elif self.dropping:
            self.current_tick += self.dropping_tpf 
            return False
        else:
            self.current_tick += self.tpf_adjusted
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

    def try_rotate(self):
        '''
        tries to rotate the piece, if doing so would cause it to occupy a space that is already occupied
        then it won't rotate
        '''
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

    def set_dropping(self, drop):
        self.dropping = drop

class Level:
    map = [[0 for i in range(10)] for j in range(20)]
    tet = 0
    game = False

    def __init__(self, game):
        self.map = [[0 for i in range(10)] for j in range(20)]
        self.game = game
        self.difficulty = 1 # increases over time
        self.difficulty_stage = 0 # current stage until difficulty increase
        self.difficulty_increase_on_stage = 20 # difficulty increases upon reaching this number
        self.score_rewards = (1   * self.difficulty, 
                              100 * self.difficulty,
                              300 * self.difficulty, 
                              500 * self.difficulty, 
                              800 * self.difficulty) # reward for: placed block, 1 line cleared, 2 lines cleared... 4 lines cleared
        self.tet = Tet(self)

    def get_map(self):
        return self.map.copy()

    def get_tet(self):
        return self.tet

    def get_difficulty(self):
        return self.difficulty

    def set_difficulty(self, difficulty):
        self.difficulty = difficulty

    def update(self):
        self.tet.update()

    def assimilate(self):
        for pr in self.tet.getPiece()[self.tet.getRotIndex()]:
            self.map[self.tet.get_y() // GRID_SIZE + pr[1]][self.tet.get_x() // GRID_SIZE + pr[0]] = self.tet.get_color()
        self.clear_lines()
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

        self.game.update_score(self.score_rewards[lines_cleared])

        self.difficulty_stage += lines_cleared # add 1 to difficulty stage per line cleared
        '''
        Play sound based on amount of lines cleared
        '''
        for element in SFX.values():
            if lines_cleared == 0:
                pygame.mixer.Sound.play(element)
                break
            else:
                lines_cleared -= 1


    def push_lines(self, row_index):
        del self.map[row_index]
        self.map.insert(0, [0 for i in range(10)])

    def check_game_over(self):
        return any(map(lambda x: x != 0, self.map[0]))

class FileHandler():
    path = ""
    data = [] # list contains tuples containing (name (str), score (int))

    def __init__(self, path="scores"):
        self.path = path + ".txt"
        self.data = []
        self.parse_file_data()

    def add_score_to_data(self, name, score):
        '''
        assumes data to be sorted
        inserts score at sorted position
        '''
        added = False
        for index, element in enumerate(self.data):
            if element[1] <= score:
                self.data.insert(index, (name, score))
                added = True
                break
        
        if not added:
            self.data.append((name, score))

        return self

    def get_data(self):
        return self.data.copy()

    def parse_file_data(self):
        '''
        check if file exists, if it does, parse data from file
        and save as tuples in data member variable
        '''
        if os.path.exists(self.path):
            file = open(self.path, "r")
            for line in file:
                if line[0] == "#":
                    continue
                parsed = line.split(':', 1)
                name = parsed[0]
                score = parsed[1].strip('\n')
                if not score.isnumeric():
                    score = 0
                self.data.append((name, int(score))) 
                print(f"added '{name}: {score}' from file to data")

    def write_data_to_file(self):
        '''
        open file and erase all data in it.
        then write on each line "name:score"
        '''
        file = open(self.path, "a")
        file.truncate(0)
        print("file has been cleared")

        file.write("# this file is assumed to be sorted from highest to lowest.\n")

        for element in self.data:
            file.write(f"{element[0]}:{element[1]}\n")
            print(f"written '{element[0]}:{element[1]}' to file")
        file.close()
        return self
            

class Game:
    game_states = Enum("game_states", ["menu", "pause", "playing", "gameover"])
    game_state = game_states.menu
    file_handler = FileHandler()
    score = 0
    level = False
    quit = False

    def __init__(self, gui):
        self.gui = gui
        self.init_state_menu()
        self.held_keys = []

    def loop(self):
        if self.game_state == self.game_states.menu:
            pass
        elif self.game_state == self.game_states.pause:
            pass
        elif self.game_state == self.game_states.playing:
            self.level.update()
            if self.level.check_game_over():
                self.init_state_gameover()

        self.handle_input()

        return self.quit

    def handle_input(self):
        events = pygame.event.get()

        for event in events:
            if event.type == pygame.QUIT:
                self.quit = True
            '''
            GUI Input
            '''
            for element in self.gui.values():
                element.input(event=event, 
                              key_gui_up=KEYBINDS["GUI_UP"],
                              key_gui_down=KEYBINDS["GUI_DOWN"],
                              key_gui_action=KEYBINDS["GUI_ACTION"])
            '''
            Gameplay Input
            '''
            if self.game_state == self.game_states.playing:
                tet = self.level.get_tet()
                '''
                if key is pressed
                '''
                if event.type == pygame.KEYDOWN:
                    if event.key == KEYBINDS["ROTATE"]:
                        tet.try_rotate()
                    if event.key == KEYBINDS["MOVE_L"]:
                        tet.move_l()
                    elif event.key == KEYBINDS["MOVE_R"]:
                        tet.move_r()
                    if event.key == KEYBINDS["PAUSE"]:
                        self.init_state_pause()
                    if event.key == KEYBINDS["DROP"]:
                        if KEYBINDS["DROP"] not in self.held_keys:
                            self.level.get_tet().set_dropping(True)
                            self.held_keys.append(KEYBINDS["DROP"])
                '''
                if key has been released
                '''
                if event.type == pygame.KEYUP:
                    if event.key == KEYBINDS["DROP"]:
                        if KEYBINDS["DROP"] in self.held_keys:
                            self.level.get_tet().set_dropping(False)
                            self.held_keys.remove(KEYBINDS["DROP"])

            elif self.game_state == self.game_states.pause:
                if event.type == pygame.KEYDOWN:
                    if event.key == KEYBINDS["PAUSE"]:
                        self.init_state_playing()

    def init_state_menu(self):
        '''
        Main Menu
        '''
        self.gui.clear()
        self.gui["main_menu"] = gui.Container(LEVEL_W // 2,
                                              LEVEL_H // 2)
        self.gui["main_menu"].add_child(gui.Text("pygame-tetris", FONT_ARIAL_55))
        self.gui["main_menu"].add_child(gui.Button(gui.Text("Start Game", FONT_ARIAL)) \
        .set_on_click(self,self.init_state_playing, []))
        self.gui["main_menu"].add_child(gui.Button(gui.Text("High Scores", FONT_ARIAL)) \
        .set_on_click(self,self.init_state_score, []))
        self.gui["main_menu"].add_child(gui.Button(gui.Text("Quit", FONT_ARIAL)) \
        .set_on_click(self,self.set_quit, []))

    def init_state_playing(self):
        '''
        Playing
        '''
        self.gui.clear()

        if self.level == False:
            self.level = Level(self)

        self.update_score_gui()

        self.game_state = self.game_states.playing

    def init_state_pause(self):
        '''
        Pause Menu
        '''
        self.gui["pause_menu"] = gui.Container(LEVEL_W // 2, 
                                               LEVEL_H // 2) \
        .add_child(gui.Text("Game Paused", FONT_ARIAL_55)) \
        .add_child(gui.Text("Rewards", FONT_ARIAL)) \
        .add_child(gui.Text("---------------", FONT_ARIAL)) \
        .add_child(gui.Text(f"block placed: {self.score_rewards[0]}", FONT_ARIAL)) \
        .add_child(gui.Text(f"1 line cleared: {self.score_rewards[1]}", FONT_ARIAL)) \
        .add_child(gui.Text(f"2 lines cleared: {self.score_rewards[2]}", FONT_ARIAL)) \
        .add_child(gui.Text(f"3 lines cleared: {self.score_rewards[3]}", FONT_ARIAL)) \
        .add_child(gui.Text(f"4 lines cleared: {self.score_rewards[4]}", FONT_ARIAL)) \

        self.game_state = self.game_states.pause

    def init_state_gameover(self):
        '''
        Game Over Screen
        '''
        self.gui.clear()

        self.gui["gameover_enter"] = gui.Container(LEVEL_W // 2,
                                                   LEVEL_H // 2) \
        .add_child(gui.Text("Game Over", FONT_ARIAL_55)) \
        .add_child(gui.Text(f"score: {self.score}", FONT_ARIAL)) \
        .add_child(gui.Text("Please enter your name", FONT_ARIAL)) \
        .add_child(gui.TextInput(gui.Text("", FONT_ARIAL)) \
                   .set_on_action(self, 
                                  self.init_state_score, 
                                  [self.score]))

        self.level = False
        self.score = 0
        self.game_state = self.game_states.gameover

    def init_state_score(self, score=0):
        '''
        View score and add score if game over
        '''
        if "gameover_enter" in self.gui.keys():
            self.file_handler.add_score_to_data(self.gui["gameover_enter"].get_child(3).get_input_text().get_content(),
                                                score)
            self.file_handler.write_data_to_file()

        self.gui.clear()


        self.gui["score_screen"] = gui.Container(LEVEL_W // 2,
                                                 LEVEL_H // 2) \
        .add_child(gui.Text("High Scores", FONT_ARIAL_55)) \
        .add_child(gui.Text("-------------", FONT_ARIAL_55)) \

        for index, score in enumerate(self.file_handler.get_data()):
            if index > 10:
                break
            self.gui["score_screen"] \
            .add_child(gui.Text(f"{score[0]}: {score[1]}", FONT_ARIAL))
        self.gui["score_screen"].add_child(gui.Button(gui.Text("Back to Title", FONT_ARIAL)).set_on_click(self, self.init_state_menu, [])) \



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
        screen.blit(BLOCK_IMGS[piece.get_color()], 
                    (piece.get_x() + actual[0] * GRID_SIZE, 
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
