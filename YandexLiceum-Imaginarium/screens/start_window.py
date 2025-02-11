import db.local_api
from screens.screens_manager import BaseWindow
import pygame
import pygame_gui
import CONSTANTS
from screens.MyManager import MyPygameGUIManager


class StartWindow(BaseWindow):
    def __init__(self, screen, name="start_window"):
        super(StartWindow, self).__init__(screen, name=name)
        self.manager = MyPygameGUIManager(CONSTANTS.SIZE)
        rect_size = (CONSTANTS.SIZE_X // 5, CONSTANTS.SIZE_Y // 10)
        rect_koor = ((CONSTANTS.SIZE_X - rect_size[0]) // 2,
                     (CONSTANTS.SIZE_Y - rect_size[1]) // 2)
        self.text_input = pygame_gui.elements.ui_text_entry_line.UITextEntryLine(
            relative_rect=pygame.Rect(rect_koor[0],
                                      rect_koor[1],
                                      rect_size[0],
                                      rect_size[1]),
            manager=self.manager)
        self.entered_text = ""
        self.add_screen_object(self.manager)

    def update(self, events, time_delta, user_data):
        next_screen = self.name
        for event in events:
            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_TEXT_ENTRY_FINISHED:
                    if event.ui_element == self.text_input and event.text != self.entered_text:
                        self.search_screen_button = pygame_gui.elements.UIButton(
                            relative_rect=pygame.Rect((350, 275), (100, 50)),
                            text="Найти комнату",
                            manager=self.manager)
                        self.creating_screen_button = pygame_gui.elements.UIButton(
                            relative_rect=pygame.Rect((100, 275), (100, 50)),
                            text="Создать комнату",
                            manager=self.manager)
                        self.entered_text = event.text
                        user_data["user_name"] = self.entered_text
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == self.search_screen_button:
                        self.user_id = db.local_api.DataBaseManager.add_user(self.entered_text)
                        user_data["user_id"] = self.user_id
                        print("search")
                        next_screen = "search_window"
                    if event.ui_element == self.creating_screen_button:
                        print("creating")
                        self.user_id = db.local_api.DataBaseManager.add_user(self.entered_text)
                        user_data["user_id"] = self.user_id
                        self.room_id, session_id = db.local_api.DataBaseManager.create_room_with_owner(self.user_id)
                        user_data["room_id"] = self.room_id
                        user_data["session_id"] = session_id
                        user_data["is_owner"] = True
                        user_data["room_owner"] = self.user_id
                        next_screen = "group_creating_window"
            self.manager.process_events(event)
        self.manager.update(time_delta)
        return next_screen, user_data
