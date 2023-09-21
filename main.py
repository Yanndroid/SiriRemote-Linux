import sys
from remote.remote import SiriRemote, RemoteListener
from hid_input import Input

hid_input = Input()


class Callback(RemoteListener):
    def event_battery(self, percent: int):
        print("Battery", percent)

    def event_power(self, charging: bool):
        print("Charging", charging)

    def event_button(self, button: int):
        handle_button_event(button)

    def event_touchpad(self, data):
        handle_touchpad_event(data)


prevXY = [None, None]


def handle_touchpad_event(data):
    sensi = 8
    x = data[0] * sensi
    y = data[1] * - sensi
    p = data[2]

    if prevXY[0] and prevXY[1]:
        hid_input.move_cursor(x - prevXY[0], y - prevXY[1])

    if p == 0:
        prevXY[0] = prevXY[1] = None
    else:
        prevXY[0] = x
        prevXY[1] = y


def handle_button_event(button):
    if button == SiriRemote.BUTTON_RELEASED:
        hid_input.release()
        return

    if button & SiriRemote.BUTTON_HOME:
        hid_input.add_key(Input.KEY_NEXTSONG)

    if button & SiriRemote.BUTTON_VOLUME_UP:
        hid_input.add_key(Input.KEY_VOLUMEUP)

    if button & SiriRemote.BUTTON_VOLUME_DOWN:
        hid_input.add_key(Input.KEY_VOLUMEDOWN)

    if button & SiriRemote.BUTTON_TOUCHPAD:
        hid_input.add_key(Input.BTN_LEFT)

    if button & SiriRemote.BUTTON_POWER:
        hid_input.add_key(Input.KEY_SCREENLOCK)

    if button & SiriRemote.BUTTON_SIRI:
        hid_input.add_key(Input.BTN_RIGHT)

    if button & SiriRemote.BUTTON_BACK:
        hid_input.add_key(Input.KEY_PREVIOUSSONG)

    if button & SiriRemote.BUTTON_MUTE:
        hid_input.add_key(Input.KEY_MUTE)

    if button & SiriRemote.BUTTON_PLAY_PAUSE:
        hid_input.add_key(Input.KEY_PLAYPAUSE)

    if button & SiriRemote.BUTTON_UP:
        hid_input.add_key(Input.KEY_UP)

    if button & SiriRemote.BUTTON_DOWN:
        hid_input.add_key(Input.KEY_DOWN)

    if button & SiriRemote.BUTTON_LEFT:
        hid_input.add_key(Input.KEY_LEFT)

    if button & SiriRemote.BUTTON_RIGHT:
        hid_input.add_key(Input.KEY_RIGHT)

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
