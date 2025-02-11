from screens import screens_manager, start_window, rabbits, search_window, group_creating_window, round
import pygame
import CONSTANTS
from CONSTANTS import SIZE, GAME_NAME, FPS


def main():
    pygame.init()
    screen = pygame.display.set_mode(SIZE)
    pygame.display.set_caption(GAME_NAME)
    clock = pygame.time.Clock()
    running = True
    window_manager = screens_manager.WindowManager(screen)

    '''Пример использования window_manager'''
    example_window = screens_manager.BaseWindow(screen, name="example_window")  # инициализирцем окно
    window_manager.add_window(example_window)  # добавляем его в window_manager
    # window_manager.change_window(example_window.get_name()) так надо будет задать начальное окно

    start = start_window.StartWindow(screen)
    window_manager.add_window(start)

    rabbits_window = rabbits.RabbitsWindow(screen)
    window_manager.add_window(rabbits_window)

    search = search_window.SearchWindow(screen)
    window_manager.add_window(search)

    creating_window = group_creating_window.GroupCreatingWindow(screen)
    window_manager.add_window(creating_window)

    round_window = round.Round(screen)
    window_manager.add_window(round_window)

    window_manager.change_window(start.get_name())
    while running:
        screen.fill((100, 0, 0))
        time_delta = clock.tick(FPS) / 1000.0
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False
        window_manager.update(events, time_delta)
        window_manager.draw()
        pygame.display.flip()
    pygame.quit()


if __name__ == '__main__':
    main()
