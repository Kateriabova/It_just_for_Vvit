import CONSTANTS
import pygame
import db.local_api
import screens.MyManager as MyManager
import pygame_gui
import screens.screens_manager


class Round(screens.screens_manager.BaseWindow):
    def __init__(self, screen, name="round_window"):
        super(Round, self).__init__(screen, name)
        self.first_update = True

        self.hand = Hand((CONSTANTS.SIZE_X // 7, CONSTANTS.SIZE_Y // 3))
        self.add_screen_object(self.hand)
        self.colode = Colode(CONSTANTS.BACKSIDE_IMAGE_PATH, self.hand)
        self.add_screen_object(self.colode)
        self.table_of_cards = TableCards((30, 30),
                                         (CONSTANTS.SIZE_X * 6 // 7 - 30, CONSTANTS.SIZE_Y * 6 // 7),
                                         CONSTANTS.BACKSIDE_IMAGE_PATH)
        self.add_screen_object(self.table_of_cards)

        self.show_manager = MyManager.MyPygameGUIManager(CONSTANTS.SIZE)
        self.show_button_text = {0: "Показать", 1: "Скрыть"}
        self.show_button_count = 0
        show_cards_button_size = (CONSTANTS.SIZE_X // 12, CONSTANTS.SIZE_Y // 15)
        show_cards_button_position = ((CONSTANTS.SIZE_X - show_cards_button_size[0]) // 2,
                                      CONSTANTS.SIZE_Y - show_cards_button_size[1] - CONSTANTS.SIZE_Y // 7)
        self.show_cards_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(show_cards_button_position, show_cards_button_size),
            text=self.show_button_text[self.show_button_count],
            manager=self.show_manager)
        self.add_screen_object(self.show_manager)

        self.round_stage = "association"
        self.frame_counter = 0
        self.input_association_manager = MyManager.MyPygameGUIManager(CONSTANTS.SIZE)
        self.input_line_edit = pygame_gui.elements.ui_text_entry_line.UITextEntryLine(
            relative_rect=pygame.Rect(CONSTANTS.SIZE_X * 6 // 7 - 100,
                                      CONSTANTS.SIZE_Y * 6 // 7 - 50,
                                      100,
                                      50), manager=self.input_association_manager)
        self.gm = False
        self.entered_text = ""
        self.gm_font = pygame.font.SysFont('arialblack', 17)
        self.card_played = False
        self.association = False
        self.cd_seconds = 0

    def draw(self, screen):
        screen.blit(self.gm_surface, (CONSTANTS.SIZE_X * 5 // 7 + 50, CONSTANTS.SIZE_Y // 2))
        if self.round_stage != "association" and not self.first_ass_upd:
            screen.blit(self.association_surface, (CONSTANTS.SIZE_X // 3, 50))
            self.first_ass_upd = False
        if self.round_stage == "association":
            self.input_association_manager.draw(screen)
        super(Round, self).draw(screen)

    def update(self, events, time_delta, user_data):
        next_screen = self.name
        if user_data["first_update"]:
            user_data["round_id"] = db.local_api.DataBaseManager.get_round(user_data["room_id"])
            self.gm = db.local_api.DataBaseManager.get_gm(user_data["round_id"])
            self.gm_name = db.local_api.DataBaseManager.get_user_name_by_session(self.gm)
            if self.gm == user_data["session_id"]:
                self.gm_surface = self.gm_font.render(f"Ведущий: Вы", False, CONSTANTS.BLACK)
            else:
                self.gm_surface = self.gm_font.render(f"Ведущий: {self.gm_name}", False, CONSTANTS.BLACK)
            self.table_of_cards.change_round_id(user_data["round_id"])
            user_data["first_update"] = False
            self.was_voted = False
            self.cd_seconds = 0
            self.round_stage = "association"
            print(user_data)
            self.first_update = False
            self.colode.get_user_id(user_data["user_id"])
            for card_id in user_data["cards"]:
                if card_id not in self.hand.cards:
                    img_path = db.local_api.DataBaseManager.get_img_path_by_card_id(card_id)
                    new_card = CardOnHand((CONSTANTS.SIZE_X - CONSTANTS.SIZE_X // 7, 0),
                                          card_id,
                                          img_path,
                                          CONSTANTS.BACKSIDE_IMAGE_PATH,
                                          user_data)
                    print(self.hand.default_position)
                    new_pos = self.hand.default_position
                    new_card.move_to_pos(new_pos[0],
                                         new_pos[1])
                    self.hand.add_card(new_card)
            print(self.hand.cards)
        else:
            if self.frame_counter % 60 == 0:
                new_round_stage = db.local_api.DataBaseManager.get_round_status(user_data["round_id"])
                if self.round_stage == "association" and new_round_stage == "playing":
                    self.association = db.local_api.DataBaseManager.get_association_by_round_id(user_data["round_id"])
                    self.round_stage = "playing"
                if new_round_stage == "vouting" and self.round_stage == "playing":
                    self.table_of_cards.show_cards()
                    self.round_stage = "vouting"
                if new_round_stage == "results" and self.round_stage == "vouting":
                    self.table_of_cards.show_authors()
                    self.round_stage = "results"
                elif self.round_stage == "vouting":
                    self.cd_seconds += 1
                if self.cd_seconds == 5:
                    user_data["first_update"] = True
                    next_screen = "rabbits"
                self.frame_counter = 0
            if self.round_stage == "playing":
                self.table_of_cards.update(user_data)
            if self.round_stage == "playing":
                self.association_surface = self.gm_font.render(f"Ассоциация: {self.association}", False,
                                                               CONSTANTS.BLACK)
            for event in events:
                if event.type == pygame.USEREVENT:
                    if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                        if event.ui_element == self.show_cards_button:
                            if self.hand.showed:
                                self.hand.hide_cards()
                            else:
                                self.hand.show_cards()
                    if self.round_stage == "association" and self.gm == user_data["session_id"]:
                        if event.user_type == pygame_gui.UI_TEXT_ENTRY_FINISHED \
                                and event.ui_element == self.input_line_edit \
                                and event.text != self.entered_text \
                                and self.card_played:
                            print("ввод", self.entered_text, event.text)
                            if self.entered_text == "":
                                self.entered_text = event.text
                                self.association = self.entered_text
                                db.local_api.DataBaseManager.add_association(self.entered_text,
                                                                             self.card_played.get_id(),
                                                                             user_data["round_id"])
                                self.first_ass_upd = True
                                self.round_stage = "playing"
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.round_stage == "association" and self.gm == user_data["session_id"]\
                            and not self.card_played:
                        collide_hand = self.hand.collide_any(event.pos[0], event.pos[1])
                        if collide_hand:
                            card = self.hand.play_card(collide_hand)
                            print(card.get_id())
                            self.card_played = card
                            self.hand.hide_cards()
                            self.colode.get_card(user_data["round_id"], user_data)
                            self.table_of_cards.add_card(self.card_played)
                            db.local_api.DataBaseManager.play_card_by_round_id(self.card_played.get_id(),
                                                                               user_data["session_id"],
                                                                               user_data["round_id"])
                            # запрос чтобы сыгарть карту
                    if self.round_stage == "playing" and self.gm != user_data["session_id"]:
                        collide_hand = self.hand.collide_any(event.pos[0], event.pos[1])
                        if collide_hand and not self.card_played:
                            card = self.hand.play_card(collide_hand)
                            self.card_played = card
                            self.table_of_cards.add_card(self.card_played)
                            db.local_api.DataBaseManager.play_card_by_round_id(self.card_played.get_id(),
                                                                               user_data["session_id"],
                                                                               user_data["round_id"])
                            self.colode.get_card(user_data["round_id"], user_data)
                    if self.round_stage == "vouting" and user_data["session_id"] != self.gm:
                        collide_table_cards = self.table_of_cards.collide_any((event.pos[0], event.pos[1]))
                        if collide_table_cards and not self.was_voted:
                            db.local_api.DataBaseManager.add_voute(user_data["session_id"],
                                                                   collide_table_cards,
                                                                   user_data["round_id"])
                            self.was_voted = True
                self.show_manager.process_events(event)
                self.input_association_manager.process_events(event)
            self.show_manager.update(time_delta)
            self.input_association_manager.update(time_delta)
            self.table_of_cards.update(user_data)
            self.frame_counter += 1
        return next_screen, user_data


class CardOnHand():
    def __init__(self, pos, id, img_path, backside_img_path, user_data):
        self.id = id
        self.author_id = user_data["session_id"]
        self.texture = "side"
        self.dict_of_textures = {"side": img_path, "backside": backside_img_path}
        self.move = False
        self.converting = False
        self.frame_count_move = 0
        self.frame_count_convert = 0
        self.position = list(pos)
        self.rect_size = [CONSTANTS.SIZE_X // 7, CONSTANTS.SIZE_Y // 3]
        self.start_pos = [CONSTANTS.SIZE_X // 2, CONSTANTS.SIZE_Y]
        self.frames_to_move = 120

    def convert_to_size(self, new_size, animation_frames):
        self.convert_to_x = new_size[0]
        self.convert_to_y = new_size[1]
        self.frames_to_convert = animation_frames
        self.x_convert_delta = (self.rect_size[0] - self.convert_to_x) // self.frames_to_convert
        self.y_convert_delta = (self.rect_size[1] - self.convert_to_y) // self.frames_to_convert
        self.converting = True

    def move_to_pos(self, pos_x, pos_y):
        self.move_to_x = pos_x
        self.move_to_y = pos_y
        self.x_move_delta = (self.move_to_x - self.position[0]) // (self.frames_to_move // 3)
        self.y_move_delta = (self.move_to_y - self.position[1]) // (self.frames_to_move // 3)
        self.move = True

    def draw(self, screen):
        if self.move:
            if self.frame_count_move % 3 == 0:
                self.position[0] += self.x_move_delta
                self.position[1] += self.y_move_delta
            if self.frame_count_move == self.frames_to_move:
                self.move = False
                self.frame_count_move = -1
            self.frame_count_move += 1
        if self.converting:
            self.rect_size[0] += self.x_convert_delta
            self.rect_size[1] += self.y_convert_delta
            if self.frame_count_convert == self.frames_to_convert:
                self.converting = False
                self.frames_to_convert = -1
            self.frame_count_convert += 1
        pygame.draw.rect(screen, CONSTANTS.LIGHT_BLUE, pygame.Rect(self.position[0],
                                                                   self.position[1],
                                                                   self.rect_size[0],
                                                                   self.rect_size[1]))

    def collide(self, pos_x, pos_y):
        if self.position[0] <= pos_x <= self.position[0] + self.rect_size[0] \
                and self.position[1] <= pos_y <= self.position[1] + self.rect_size[1]:
            return True
        return False

    def change_side(self):
        if self.texture == "side":
            self.texture = "backside"
        else:
            self.texture = "side"

    def get_id(self):
        return self.id

    def get_size(self):
        return self.rect_size

    def get_author_id(self):
        return self.author_id


class Hand:
    def __init__(self, card_size):
        self.cards = {}
        self.showed = False
        self.card_size = card_size
        self.default_position = ((CONSTANTS.SIZE_X - card_size[0]) // 2,
                                 CONSTANTS.SIZE_Y - CONSTANTS.SIZE_Y // 14)

    def add_card(self, card: CardOnHand):
        card.change_side()
        self.cards[card.get_id()] = card

    def play_card(self, card_id):
        card = self.cards.pop(card_id)
        card.change_side()
        return card

    def show_cards(self):
        card_start_posistion_x = CONSTANTS.SIZE_X // 7
        card_posistion_y = CONSTANTS.SIZE_Y // 6
        for key in self.cards:
            self.cards[key].move_to_pos(card_start_posistion_x, card_posistion_y)
            card_size = self.cards[key].get_size()
            self.cards[key].change_side()
            card_start_posistion_x += card_size[0] + CONSTANTS.SIZE_X // 21
        self.showed = True

    def collide_any(self, pos_x, pos_y):
        if self.showed:
            for key in self.cards:
                result = self.cards[key].collide(pos_x, pos_y)
                if result:
                    return key
        return False

    def hide_cards(self):
        for key in self.cards:
            self.cards[key].change_side()
            self.cards[key].move_to_pos(self.default_position[0],
                                        self.default_position[1])
        self.showed = False

    def draw(self, screen):
        for card_id in self.cards:
            self.cards[card_id].draw(screen)


class Colode:
    def __init__(self, backside_img_path, hand: Hand):
        self.colode_pos = (CONSTANTS.SIZE_X - CONSTANTS.SIZE_X // 7, 0)
        self.backside_path = backside_img_path
        self.hand = hand

    def get_user_id(self, user_id):
        self.user_id = user_id

    def get_card(self, round_id, user_data):
        card_id, card_path = db.local_api.DataBaseManager.give_card_to_user(self.user_id, user_data["room_id"])
        new_card = CardOnHand(self.colode_pos, card_id, card_path, self.backside_path, user_data)
        new_card.move_to_pos(self.hand.default_position[0], self.hand.default_position[1])
        self.hand.add_card(new_card)

    def draw(self, screen):
        pygame.draw.rect(screen, CONSTANTS.LIGHT_BLUE, pygame.Rect(self.colode_pos[0],
                                                                   self.colode_pos[1],
                                                                   CONSTANTS.SIZE_X // 7,
                                                                   CONSTANTS.SIZE_Y // 3))


class TableCards:
    def __init__(self, start_position, size, backsize_img_path):
        self.backside_img_path = backsize_img_path
        self.start_position = start_position
        self.size = size
        self.card_position = (self.start_position[0] + (self.size[0] - 100) // 2,
                              self.start_position[1] + self.size[1] // 3)
        self.card_size_x = self.size[0] * 36 // (41 * 7)
        self.showed = False
        self.authors_showed = False
        self.cards = {}
        self.frame_counter = 0
        self.authors_font = pygame.font.SysFont('arialblack', 11)

    def add_card(self, card: CardOnHand):
        size = card.get_size()
        card.convert_to_size((self.card_size_x, int(self.card_size_x * (size[1] / size[0]))), 30)
        card.move_to_pos(self.card_position[0], self.card_position[1])
        self.cards[card.get_id()] = card

    def show_cards(self):
        start_card_x_position = self.start_position[0] + self.size[0] // 14
        y_position = self.start_position[1] + self.size[1] // 3
        for card_id in self.cards:
            self.cards[card_id].change_side()
            self.cards[card_id].move_to_pos(start_card_x_position, y_position)
            start_card_x_position += (self.card_size_x * 7 // 6)
        self.showed = True

    def show_authors(self):
        self.authors_showed = True

    def update(self, user_data):
        if self.frame_counter % 120 == 0:
            cards, result = db.local_api.DataBaseManager.get_played_cards(user_data["round_id"])
            for card_id in cards:
                if card_id not in self.cards:
                    self.cards[card_id] = CardOnHand(self.start_position,
                                                     card_id,
                                                     db.local_api.DataBaseManager.get_img_path_by_card_id(card_id),
                                                     self.backside_img_path,
                                                     user_data)
            if result == "ok":
                self.show_cards()

    def draw(self, screen):
        for card_id in self.cards:
            if self.authors_showed:
                author_name = db.local_api.DataBaseManager.get_user_name_by_id(self.cards[card_id].get_author_id())
                author_surface = self.authors_font.render(author_name,
                                                          False,
                                                          CONSTANTS.BLACK)
                screen.blit(author_surface, (self.cards[card_id].position[0], self.cards[card_id].position[1] - 50))
                number_of_votes = db.local_api.DataBaseManager.get_number_of_votes(self.round_id, card_id)
                if number_of_votes != 0:
                    voute_surface = self.authors_font.render(str(number_of_votes),
                                                             False,
                                                             CONSTANTS.BLACK)
                    screen.blit(voute_surface, (self.cards[card_id].position[0],
                                                self.cards[card_id].position[1] + self.cards[card_id].get_size[1] + 50))
            self.cards[card_id].draw(screen)

    def change_round_id(self, round_id):
        self.round_id = round_id

    def collide_any(self, position):
        for card_id in self.cards:
            if self.cards[card_id].collide(position[0], position[1]):
                return card_id
        return False
