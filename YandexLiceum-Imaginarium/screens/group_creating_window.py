from screens.MyManager import MyPygameGUIManager
import pygame_gui
import pygame
import CONSTANTS
from screens.screens_manager import BaseWindow
import db.local_api


class GroupCreatingWindow(BaseWindow):
    def __init__(self, screen, name="group_creating_window"):
        super(GroupCreatingWindow, self).__init__(screen, name)
        self.manager = MyPygameGUIManager(CONSTANTS.SIZE)
        self.colode_button_count = 0
        self.colode_button_text = {0: "Колоды", 1: "Участники"}
        colode_button_size = (CONSTANTS.SIZE_X // 12, CONSTANTS.SIZE_Y // 15)
        colode_button_position = ((CONSTANTS.SIZE_X - colode_button_size[0]) // 2,
                                  CONSTANTS.SIZE_Y - colode_button_size[1] - CONSTANTS.SIZE_Y // 7)
        self.colode_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(colode_button_position, colode_button_size),
            text=self.colode_button_text[self.colode_button_count],
            manager=self.manager
        )
        self.user_table = UserTable(screen)
        self.object_to_draw_manager = ObjectToDraw(self.user_table,
                                                   ((CONSTANTS.SIZE_X - 100) // 2,
                                                    CONSTANTS.SIZE_Y // 7))
        self.colode_table = ColodeTable(screen, self.manager)
        self.object_to_draw_manager.dict_of_objects_to_draw[1] = self.colode_table
        self.add_screen_object(self.object_to_draw_manager)
        self.add_screen_object(self.manager)
        self.frame_counter = 0
        pos_x = CONSTANTS.SIZE_X // 7 - 100
        pos_y = CONSTANTS.SIZE_Y // 7 - 50
        self.ready_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(pos_x, pos_y, 100, 50),
            text="Начать",
            manager=self.manager)

    def update(self, events, time_delta, user_data):
        next_screen = self.name
        self.frame_counter += 1
        if self.frame_counter // 60:
            game_status = db.local_api.DataBaseManager.get_game_status(user_data["room_id"], user_data["user_id"])
            if game_status:
                next_screen = "rabbits"
                user_data["cards"] = []
                for card_id in game_status:
                    user_data["cards"].append(card_id)
                return next_screen, user_data
        self.object_to_draw_manager.update(events, time_delta, user_data)
        for event in events:
            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == self.colode_button:
                        self.colode_button_count += 1
                        self.object_to_draw_manager.change_widget(self.colode_button_count % 2)
                        self.colode_button.set_text(self.colode_button_text[self.colode_button_count % 2])
                    if event.ui_element == self.ready_button and user_data["is_owner"]:
                        db.local_api.DataBaseManager.start_game(user_data["room_id"])
                        result = db.local_api.DataBaseManager.get_users_cards(user_data["session_id"])
                        print(result)
                        if result:
                            user_data["cards"] = []
                            for card_id in result:
                                user_data["cards"].append(card_id)
                            print("rabbits")
                            # Обработать начало партии
                            next_screen = "rabbits"
                    elif event.ui_element == self.ready_button:
                        print("Вы не владелей этой комнаты")
                    button_answer = self.colode_table.get_colode_info_by_button(event.ui_element)
                    if button_answer and user_data["is_owner"]:
                        db.local_api.DataBaseManager.change_colode_in_room_by_room_id(user_data["room_id"],
                                                                                      button_answer)
                    elif not user_data["is_owner"]:
                        print("Вы не владелец этой комнаты")
            self.manager.process_events(event)
        self.manager.update(time_delta)
        return next_screen, user_data


class ObjectToDraw:
    def __init__(self, obj, start_pos):
        self.dict_of_objects_to_draw = {0: obj}
        self.id = 0
        self.start_pos = start_pos

    def update(self, events, time_delta, user_data):
        if self.id in self.dict_of_objects_to_draw:
            self.dict_of_objects_to_draw[self.id].update(events, time_delta, user_data)
        else:
            print("widget not found")

    def change_widget(self, id):
        self.id = id

    def draw(self, screen):
        if self.id in self.dict_of_objects_to_draw:
            self.dict_of_objects_to_draw[self.id].draw(screen, self.start_pos[0], self.start_pos[1])
        else:
            print("widget not found")


class ColodeTable:
    def __init__(self, screen, manager):
        self.screen = screen
        self.frame_counter = 0
        self.dict_of_players = False
        self.start_colode = 0
        self.manager = MyPygameGUIManager(CONSTANTS.SIZE)
        self.dict_of_colodes = db.local_api.DataBaseManager.colode_names()
        self.frame_count = 0

    def draw(self, screen, start_pos_x, start_pos_y):
        if self.frame_count == 0:
            if self.dict_of_colodes:
                dict_of_colodes = self.dict_of_colodes
                colode_button_size_y = CONSTANTS.SIZE_Y // 5 * 3 // 6
                colode_button_size_x = 100
                colode_button_koor_x = start_pos_x
                start_colode_buttons_y = start_pos_y
                count_colode = 0
                keys = dict_of_colodes.keys()
                print(dict_of_colodes)
                for id in keys:
                    colode = dict_of_colodes[id]["name"]
                    if self.start_colode + 6 > count_colode >= self.start_colode:
                        self.dict_of_colodes[id]["button"] = pygame_gui.elements.UIButton(
                            relative_rect=pygame.Rect((colode_button_koor_x, start_colode_buttons_y),
                                                      (colode_button_size_x, colode_button_size_y)),
                            text=colode,
                            manager=self.manager
                        )
                        start_colode_buttons_y += colode_button_size_y
                    count_colode += 1
                print(dict_of_colodes)
            self.frame_count = 1
        self.manager.draw(screen)

    def update(self, events, time_delta, user_data):
        for event in events:
            self.manager.process_events(event)
        self.manager.update(time_delta)

    def get_colode_info_by_button(self, button):
        for id in self.dict_of_colodes:
            if "button" in self.dict_of_colodes[id]:
                if self.dict_of_colodes[id]["button"] == button:
                    return id
        print("Такой колоды не нашлось")
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

    def draw(self, screen, start_pos_x, start_pos_y):
        if self.dict_of_players:
            dict_of_players = self.dict_of_players
            pygame.draw.rect(self.screen, CONSTANTS.LIGHT_BLUE,
                             (start_pos_x, start_pos_y, 100, 375))
            count = 0
            my_font = pygame.font.SysFont('arialblack', 11)
            for id in dict_of_players:
                name = dict_of_players[id]["name"]
                score = str(dict_of_players[id]['score'])
                self.text_surface = my_font.render(name + ': ' + score, False, CONSTANTS.BLACK)
                self.screen.blit(self.text_surface, (start_pos_x + 5, start_pos_y + 5 + 75 + 50 * count))
                count += 1
            my_font_2 = pygame.font.SysFont('arialblack', 17)
            self.text_surface_2 = my_font_2.render('Игроки:', False, CONSTANTS.BLACK)
            self.screen.blit(self.text_surface_2, (start_pos_x + 5, start_pos_y + 5))
