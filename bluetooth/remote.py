from signal import pause

import att


class RemoteListener:
    def event_battery(self, percent: int):
        pass

    def event_power(self, charging: bool):
        pass

    def event_button(self, button: int):
        pass

    def event_touchpad(self, data, pressed: bool):
        pass

    def event_audio(self, frame_number, data):
        pass


class SiriRemote(att.ATTDeviceListener):
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
        self.__listener = listener
        self.__device = att.ATTDevice(mac, self)
        # self.__device.connect() # TODO testing (enable)

        pause()

    def on_connected(self, device):
        print("Connected", device._connection_handle)  # TODO testing (remove)

        # TODO testing (enable)
        # device.enable_notifications(0x0029)
        # device.enable_notifications(0x002c)
        # device.enable_notifications(0x0024)
        # device.write_characteristic(0x001d, b'\xAF', False)

    def on_disconnected(self, device):
        print("Disconnected")
        self.__device.connect()

    def on_att_data(self, device, handle, value):
        if handle == self.__HANDLE_BATTERY:
            self._handle_battery(value)
        elif handle == self.__HANDLE_POWER:
            self._handle_power(value)
        elif handle == self.__HANDLE_INPUT:
            self._handle_input(value)

    def _handle_battery(self, data):
        self.__listener.event_battery(data[0])

    def _handle_power(self, data):
        if data[0] == self.__POWER_CHARGING:
            self.__listener.event_power(True)
        elif data[0] == self.__POWER_DISCHARGING:
            self.__listener.event_power(False)

    def _handle_input(self, data):
        button = data[1]
        if data[0] == 2 and button & self.BUTTON_TOUCHPAD:
            button += self.BUTTON_TOUCHPAD_2 - self.BUTTON_TOUCHPAD

        if button != self.__lastButton:
            self.__lastButton = button
            self.__listener.event_button(button)

        if len(data) >= 3 and data[2] == self.__TOUCH_EVENT:
            self._handle_touchpad(data)

        if len(data) == 101:
            self._handle_audio(data)

    def _handle_touchpad(self, data):
        pressed = data[1] & self.BUTTON_TOUCHPAD
        if len(data) == 13:
            self.__listener.event_touchpad([self._decode_finger(data[6:13])], pressed)
        elif len(data) == 20:
            self.__listener.event_touchpad([self._decode_finger(data[6:13]),
                                            self._decode_finger(data[13:20])], pressed)

    def _handle_audio(self, data):
        frame_number = data[4] + (data[5] << 8)
        print(frame_number)  # TODO testing (remove)
        self.__listener.event_audio(frame_number, data[6:])

    def _decode_finger(self, data):
        x = int((data[0] + 255 * (data[1] & 7) - 230) / 15)
        y = (data[2] if data[2] & 128 else data[2] + 255) - 188
        p = data[5]
        return x, y, p
