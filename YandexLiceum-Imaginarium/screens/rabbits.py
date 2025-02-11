from screens.MyManager import MyPygameGUIManager
from screens.screens_manager import BaseWindow
import pygame
import pygame_gui
import CONSTANTS
import db.local_api
import os
import sys
import random


def load_image(name, colorkey=None):
    fullname = os.path.join('source', name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


class RabbitsWindow(BaseWindow):
    def __init__(self, screen, name="rabbits"):
        super(RabbitsWindow, self).__init__(screen, name=name)
        self.table = Table(self.screen)
        self.players = UserTable(self.screen)
        self.pole = Pole(self.screen)
        self.rabs = []
        self.screen = screen
        self.add_screen_object(self.table)
        self.add_screen_object(self.pole)
        self.add_screen_object(self.players)
        self.first_table = True
        self.manager = MyPygameGUIManager(CONSTANTS.SIZE)
        ready_button_size = (CONSTANTS.SIZE_X // 4, CONSTANTS.SIZE_Y // 10)
        ready_button_koor = ((CONSTANTS.SIZE_X - ready_button_size[0]) // 2,
                             CONSTANTS.SIZE_Y * 6 // 7)
        self.ready_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(ready_button_koor, ready_button_size),
            text="Я готов",
            manager=self.manager)
        self.button_clicked = False
        self.add_screen_object(self.manager)

    def update(self, events, time_delta, user_data):
            print(colors)
            count = 0
            for id in self.dict_of_players:
                self.rabs.append(Rabbits(self.screen, id, self.dict_of_players[id]['score'], colors[count]))
                self.add_screen_object(self.rabs[-1])
        for event in events:
            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == self.ready_button:
                        if not self.button_clicked:
                            count_1 = db.local_api.DataBaseManager.get_ready_count_and_add(user_data["room_id"])
                            count_2 = db.local_api.DataBaseManager.get_q_of_players(user_data["room_id"])
                            if count_1 == count_2:
                                next_screen = 'round_window'
                            self.button_clicked = True
            self.manager.process_events(event)
        self.manager.update(time_delta)
        self.players.update(events, time_delta, user_data)
        for i in self.rabs:
            i.update(events, time_delta, user_data)
        return next_screen, user_data


class Table:

    def __init__(self, screen):
        self.screen = screen
        self.image = load_image("table.png")
        self.image = pygame.transform.scale(self.image, (896, 600))
        self.rect = self.image.get_rect()
        self.rect.x = 270
        self.rect.y = 35

    def draw(self, screen):
        self.screen.blit(self.image, (self.rect.x, self.rect.y))

    def collide(self, position):
        if self.rect.x <= position[0] <= self.rect.x + 896 and \
                self.rect.y <= position[1] <= self.rect.y + 600:
            if not 468 <= position[0] <= 468 + 500 or not \
                    50 <= position[1] <= 50 + 500:
                return True
            return False
        return False


class UserTable:
    def __init__(self, screen):
        self.screen = screen
        self.frame_counter = 0
        self.dict_of_players = False

    def update(self, events, time_delta, user_data):
        if self.frame_counter % (60 * 3) == 0:
            print(user_data)
            self.dict_of_players = db.local_api.DataBaseManager.players_by_room_id(user_data["room_id"])
            self.frame_counter = 0
        self.frame_counter += 1

    def draw(self, screen):
        dict_of_players = self.dict_of_players
        pygame.draw.rect(self.screen, CONSTANTS.LIGHT_BLUE,
                         (35, 35, 200, 375))
        count = 0
        my_font = pygame.font.SysFont('arialblack', 11)
        for id in dict_of_players:
            name = dict_of_players[id]["name"]
            score = str(dict_of_players[id]['score'])
            self.text_surface = my_font.render(name + ': ' + score, False, CONSTANTS.BLACK)
            self.screen.blit(self.text_surface, (35, 35 + 75 + 50 * count))
            count += 1
        my_font_2 = pygame.font.SysFont('arialblack', 17)
        self.text_surface_2 = my_font_2.render('Игроки:', False, CONSTANTS.BLACK)
        self.screen.blit(self.text_surface_2, (35, 35))


class Pole:
    def __init__(self, screen):
        self.screen = screen
        self.image = load_image("pole.png")

        self.rect = self.image.get_rect()
        self.rect.x = 468
        self.rect.y = 50

    def draw(self, screen):
        self.screen.blit(self.image, (self.rect.x, self.rect.y))


class Rabbits:
    def __init__(self, screen, id_user, score_user, color):
        self.screen = screen
        self.user = id_user
        self.color = color
        self.score = score_user
        self.kinds = ['sit', 'jump']
        self.count_kinds = 0
        self.coords = (CONSTANTS.STAND[0])
        print(self.coords)
        self.image = load_image(f'bunny_{color}_sit.png', -1)
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.rect = self.image.get_rect()
        self.rect.x = self.coords[0]
        self.rect.y = self.coords[1]

    def update(self, events, time_delta, user_data):
        print(user_data)
        if self.coords != CONSTANTS.STAND[self.score]:
            self.coords = CONSTANTS.STEPS[CONSTANTS.STEPS.index(self.coords) + 1]
            print(self.coords)
            self.count_kinds = (self.count_kinds + 1) % 2
            self.image = load_image(f'bunny_{self.color}_{self.kinds[self.count_kinds]}.png', -1)
            if self.count_kinds == 0:
                self.image = pygame.transform.scale(self.image, (50, 50))
            self.rect = self.image.get_rect()
            self.rect.x = self.coords[0]
            self.rect.y = self.coords[1]
        self.draw(self.screen)

    def draw(self, screen):
        print(self.coords, '!!!!')
        self.screen.blit(self.image, (self.rect.x, self.rect.y))

