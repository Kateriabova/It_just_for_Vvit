import pygame_gui


class MyPygameGUIManager(pygame_gui.UIManager):
    def draw(self, screen):
        self.draw_ui(screen)
