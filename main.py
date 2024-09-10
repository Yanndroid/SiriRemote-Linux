import sys
from remote.remote import SiriRemote, RemoteListener
from input.hid_input import Input

hid_input = Input()


class Callback(RemoteListener):
    def event_battery(self, percent: int):
        print("Battery", percent)

    def event_power(self, charging: bool):
        print("Charging", charging)

    def event_button(self, button: int):
        handle_button_event(button)

    def event_touchpad(self, data, pressed: bool):
        if len(data) == 2 and data[0][2] == 0:  # "ghost" finger with pressure 0
            handle_touchpad_event(data[1], pressed)
        else:
            handle_touchpad_event(data[0], pressed)


def handle_touchpad_event(data, pressed: bool):
    if not pressed:
        hid_input.release()
        return

    x = data[0]
    y = data[1]

    if abs(y - 54) > abs(x - 54):
        button = Input.KEY_UP if y > 54 else Input.KEY_DOWN
    else:
        button = Input.KEY_RIGHT if x > 54 else Input.KEY_LEFT

    if 30 < y < 78 and 30 < x < 78:
        button = Input.KEY_ENTER

    hid_input.add_key(button)
    hid_input.press()


def handle_button_event(button):
    if button & SiriRemote.BUTTON_TOUCHPAD_2 or button & SiriRemote.BUTTON_TOUCHPAD:
        return

    if button == SiriRemote.BUTTON_RELEASED:
        hid_input.release()
        return

    if button & SiriRemote.BUTTON_AIRPLAY:
        hid_input.add_key(Input.KEY_BACK)

    if button & SiriRemote.BUTTON_VOLUME_UP:
        hid_input.add_key(Input.KEY_VOLUMEUP)

    if button & SiriRemote.BUTTON_VOLUME_DOWN:
        hid_input.add_key(Input.KEY_VOLUMEDOWN)

    if button & SiriRemote.BUTTON_PLAY_PAUSE:
        hid_input.add_key(Input.KEY_PLAYPAUSE)

    # if button & SiriRemote.BUTTON_SIRI:
    #     print("Siri")

    if button & SiriRemote.BUTTON_MENU:
        hid_input.add_key(Input.KEY_MENU)

    hid_input.press()


if __name__ == '__main__':
    try:
        if len(sys.argv) > 1:
            mac = sys.argv[1]
            SiriRemote(mac, Callback())
        else:
            print("error: no mac address")
    except KeyboardInterrupt:
        hid_input.close()
        exit()
