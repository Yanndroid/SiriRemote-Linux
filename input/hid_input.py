from evdev import UInput, ecodes as e


class Input:
    KEY_VOLUMEUP = e.KEY_VOLUMEUP
    KEY_VOLUMEDOWN = e.KEY_VOLUMEDOWN

    KEY_PLAYPAUSE = e.KEY_PLAYPAUSE

    KEY_MENU = e.KEY_M
    KEY_BACK = e.KEY_BACKSPACE
    KEY_ENTER = e.KEY_ENTER

    KEY_LEFT = e.KEY_LEFT
    KEY_UP = e.KEY_UP
    KEY_RIGHT = e.KEY_RIGHT
    KEY_DOWN = e.KEY_DOWN

    def __init__(self):
        cap = {e.EV_KEY: [self.KEY_VOLUMEUP, self.KEY_VOLUMEDOWN,
                          self.KEY_PLAYPAUSE,
                          self.KEY_MENU, self.KEY_BACK, self.KEY_ENTER,
                          self.KEY_LEFT, self.KEY_UP, self.KEY_RIGHT, self.KEY_DOWN]}
        self.__ui = UInput(cap, name='Siri Remote Wrapper')

        self.__new_keys = []
        self.__pressed_keys = []

    def add_key(self, key):
        if key not in self.__new_keys:
            self.__new_keys.append(key)

    def press(self):
        for key in self.__pressed_keys:
            if key not in self.__new_keys:
                self.__ui.write(e.EV_KEY, key, 0)

        for key in self.__new_keys:
            self.__ui.write(e.EV_KEY, key, 1)

        self.__ui.syn()

        self.__pressed_keys.clear()
        self.__pressed_keys.extend(self.__new_keys)
        self.__new_keys.clear()

    def release(self):
        for key in self.__pressed_keys:
            self.__ui.write(e.EV_KEY, key, 0)
        self.__ui.syn()

    def close(self):
        self.__ui.close()
