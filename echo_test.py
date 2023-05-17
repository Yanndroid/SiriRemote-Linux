import sys

from remote.remote import SiriRemote, RemoteListener


class Callback(RemoteListener):
    def event_battery(self, percent: int):
        print("Battery", percent)

    def event_power(self, charging: bool):
        print("Charging", charging)

    def event_button(self, button: int):
        print("Button", button)

    def event_touchpad(self, data, pressed: bool):
        print("Touch", data, pressed)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        mac = sys.argv[1]
        SiriRemote(mac, Callback())
    else:
        print("error: no mac address")
