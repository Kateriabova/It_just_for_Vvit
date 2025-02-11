from screens.MyManager import MyPygameGUIManager
import pygame_gui
import pygame
import CONSTANTS
from screens.screens_manager import BaseWindow
import db.local_api


class SearchWindow(BaseWindow):
    def __init__(self, screen, name="search_window"):
        super(SearchWindow, self).__init__(screen, name=name)
        self.manager = MyPygameGUIManager(CONSTANTS.SIZE)
        update_button_size = (CONSTANTS.SIZE_X // 12, CONSTANTS.SIZE_Y // 15)
        update_button_koor = (CONSTANTS.SIZE_X - update_button_size[0] * 2,
                              update_button_size[1])
        self.update_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(update_button_koor, update_button_size),
            text="Обновить",
            manager=self.manager)
        self.add_screen_object(self.manager)
        self.start_room = 0
        self.show_table_of_rooms()

    def show_table_of_rooms(self):
        self.dict_of_rooms = db.local_api.DataBaseManager.room_info()
        room_button_size_y = CONSTANTS.SIZE_Y // 5 * 3 // 6
        room_button_size_x = CONSTANTS.SIZE_X // 5 * 3
        room_button_koor_x = CONSTANTS.SIZE_X // 7
        start_rooms_buttons_y = CONSTANTS.SIZE_Y // 7
        count_rooms = 0
        keys = self.dict_of_rooms.keys()
        for id in keys:
            colode, owner, count, active, = self.dict_of_rooms[id]["colode"], \
                                            self.dict_of_rooms[id]["owner"], \
                                            self.dict_of_rooms[id]["count"], \
                                            self.dict_of_rooms[id]["active"]
            if active == 1:
                if self.start_room + 6 > count_rooms >= self.start_room:
                    self.dict_of_rooms[id]["button"] = pygame_gui.elements.UIButton(
                        relative_rect=pygame.Rect((room_button_koor_x, start_rooms_buttons_y),
                                                  (room_button_size_x, room_button_size_y)),
                        text=f"Хозяин: {owner}, {colode}, {count}/6",
                        manager=self.manager
                    )
                    start_rooms_buttons_y += room_button_size_y
                count_rooms += 1

    def get_room_info_by_button(self, button):
        for id in self.dict_of_rooms:
            print(self.dict_of_rooms[id], button)
            if "button" in self.dict_of_rooms[id]:
                if self.dict_of_rooms[id]["button"] == button:
                    return id
        print("Такой комнаты не нашлось")
        return False

    def update(self, events, time_delta, user_data):
        next_screeen = self.name
        for event in events:
            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == self.update_button:
                        self.show_table_of_rooms()
                    else:
                        if "user_id" in user_data:
                            room_id = self.get_room_info_by_button(event.ui_element)
                            room_info = self.dict_of_rooms[room_id]
                            session_id = db.local_api.DataBaseManager.add_user_to_room(room_id, user_data["user_id"])
                            print(session_id)
                            if session_id:
                                user_data["session_id"] = session_id
                                next_screeen = "group_creating_window"
                                colode, owner, count, active, = room_info["colode"], \
                                                                room_info["owner"], \
                                                                room_info["count"], \
                                                                room_info["active"]
                                user_data["room_owner"] = owner
                                user_data["is_owner"] = False
                                user_data["room_id"] = room_id
                        else:
                            print("не найдено поля id в user_data")
            self.manager.process_events(event)
        self.manager.update(time_delta)
        return next_screeen, user_data
