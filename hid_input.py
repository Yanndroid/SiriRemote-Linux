from evdev import UInput, ecodes as e


class Input:
    KEY_VOLUMEUP = e.KEY_VOLUMEUP
    KEY_VOLUMEDOWN = e.KEY_VOLUMEDOWN
    KEY_MUTE = e.KEY_MUTE

    KEY_PLAYPAUSE = e.KEY_PLAYPAUSE
    KEY_NEXTSONG = e.KEY_NEXTSONG
    KEY_PREVIOUSSONG = e.KEY_PREVIOUSSONG

    KEY_UP = e.KEY_UP
    KEY_DOWN = e.KEY_DOWN
    KEY_LEFT = e.KEY_LEFT
    KEY_RIGHT = e.KEY_RIGHT

    KEY_SCREENLOCK = e.KEY_SCREENLOCK

    BTN_LEFT = e.BTN_LEFT
    BTN_RIGHT = e.BTN_RIGHT

    def __init__(self):
        cap = {e.EV_KEY: [self.KEY_VOLUMEUP, self.KEY_VOLUMEDOWN, self.KEY_MUTE,
                          self.KEY_PLAYPAUSE, self.KEY_NEXTSONG, self.KEY_PREVIOUSSONG,
                          self.KEY_UP, self.KEY_DOWN, self.KEY_LEFT, self.KEY_RIGHT,
                          self.KEY_SCREENLOCK,
                          self.BTN_LEFT, self.BTN_RIGHT],
               e.EV_REL: [e.REL_X, e.REL_Y]}
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

    def move_cursor(self, x, y):
        self.__ui.write(e.EV_REL, e.REL_X, x)
        self.__ui.write(e.EV_REL, e.REL_Y, y)
        self.__ui.syn()

    def close(self):
        self.__ui.close()
