class BaseWindow:
    def __init__(self, screen, name="basewindow"):
        self.screen_objects = []
        self.name = name
        self.screen = screen

    def add_screen_object(self, new_screen_object):
        self.screen_objects.append(new_screen_object)

    def draw(self, screen):
        for screen_object in self.screen_objects:
            screen_object.draw(screen)

    def update(self, events, time_delta, user_data):
        return self.name, user_data

    def get_name(self):
        return self.name


class WindowManager:
    def __init__(self, screen):
        self.screen = screen
        self.windows = {}
        self.window_now = None
        self.user_data = {"first_update": True}

    def add_window(self, window):
        window_name = window.get_name()
        self.windows[window_name] = window

    def change_window(self, window_name):
        if window_name in self.windows:
            self.window_now = window_name
        else:
            print(f"Error: {window_name} window not found.")

    def draw(self):
        if not self.user_data["first_update"]:
            window = self.windows[self.window_now]
            window.draw(self.screen)

    def update(self, events, time_delta):
        window = self.windows[self.window_now]
        next_window, user_data = window.update(events, time_delta, self.user_data)
        self.user_data = user_data
        if next_window != window.get_name():
            self.user_data["first_update"] = True
        else:
            self.user_data["first_update"] = False
        self.change_window(next_window)

    def add_user_data(self, key, value):
        self.user_data[key] = value
