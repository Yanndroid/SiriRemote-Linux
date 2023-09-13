import time
from bluepy.btle import BTLEDisconnectError
from . import bt


class RemoteListener:
    def event_battery(self, percent: int):
        pass

    def event_power(self, charging: bool):
        pass

    def event_button(self, button: int):
        pass

    def event_touchpad(self, data, pressed: bool):
        pass


class SiriRemote:
    __HANDLE_INPUT = 35
    __HANDLE_BATTERY = 40
    __HANDLE_POWER = 43
    __TOUCH_EVENT = 50

    __POWER_CHARGING = 171
    __POWER_DISCHARGING = 175
    __POWER_PLUGGED_IN = 187

    BUTTON_RELEASED = 0
    BUTTON_AIRPLAY = 1
    BUTTON_VOLUME_UP = 2
    BUTTON_VOLUME_DOWN = 4
    BUTTON_PLAY_PAUSE = 8
    BUTTON_SIRI = 16
    BUTTON_MENU = 32
    BUTTON_TOUCHPAD_2 = 64  # custom: 2 finger click
    BUTTON_TOUCHPAD = 128

    __lastButton = 0

    def __init__(self, mac, listener: RemoteListener):
        self.__device = bt.Device(mac)
        self.__listener = listener
        self.__setup()

    def __setup(self):
        try:
            self.__device.connect()
            self.__device.set_mtu(104)
            self.__device.set_listener(self.__handle_notification)
            self.__device.enable_notifications(0x002f)  # battery service
            self.__device.enable_notifications(0x0032)  # power service
            self.__device.enable_notifications(0x0036)  # hid service
            self.__device.enable_notifications(0x003a)  # hid service
            self.__device.enable_notifications(0x003e)  # hid service
            self.__device.enable_notifications(0x0042)  # hid service
            self.__device.enable_notifications(0x0046)  # hid service
            self.__device.enable_notifications(0x004a)  # hid service
            self.__device.write_characteristic(0x004d, b'\xF0\x00')  # "magic" byte
            self.__device.loop()
        except BTLEDisconnectError:
            self.__listener.event_button(0)  # release all keys
            time.sleep(0.5)
            self.__setup()

    def __handle_notification(self, handle, data):
        if handle == self.__HANDLE_BATTERY:
            self.__handle_battery(data)
        elif handle == self.__HANDLE_POWER:
            self.__handle_power(data)
        elif handle == self.__HANDLE_INPUT:
            self.__handle_input(data)

    def __handle_battery(self, data):
        self.__listener.event_battery(data[0])

    def __handle_power(self, data):
        if data[0] == self.__POWER_CHARGING:
            self.__listener.event_power(True)
        elif data[0] == self.__POWER_DISCHARGING:
            self.__listener.event_power(False)

    def __handle_input(self, data):
        button = data[1]
        if data[0] == 2 and button & self.BUTTON_TOUCHPAD:
            button += self.BUTTON_TOUCHPAD_2 - self.BUTTON_TOUCHPAD

        if button != self.__lastButton:
            self.__lastButton = button
            self.__listener.event_button(button)

        if len(data) >= 3 and data[2] == self.__TOUCH_EVENT:
            self.__handle_touchpad(data)

    def __handle_touchpad(self, data):
        pressed = data[1] & self.BUTTON_TOUCHPAD
        if len(data) == 13:
            self.__listener.event_touchpad([self.__decode_finger(data[6:13])], pressed)
        elif len(data) == 20:
            self.__listener.event_touchpad([self.__decode_finger(data[6:13]),
                                            self.__decode_finger(data[13:20])], pressed)

    @staticmethod
    def __decode_finger(data):
        x = int((data[0] + 255 * (data[1] & 7) - 230) / 15)
        y = (data[2] if data[2] & 128 else data[2] + 255) - 188
        p = data[5]
        return x, y, p
