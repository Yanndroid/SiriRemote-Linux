from remote import SiriRemote, RemoteListener

f = open("../test/frames.txt", "w")


class Callback(RemoteListener):
    last_audio_frame = 0

    def event_battery(self, percent: int):
        print("Battery", percent)

    def event_power(self, charging: bool):
        print("Charging", charging)

    def event_button(self, button: int):
        print("Button", button)

    def event_touchpad(self, data, pressed: bool):
        print("Touch", data, pressed)

    def event_audio(self, frame_number, data):
        # print("Audio", data.hex())

        if frame_number == 0: self.last_audio_frame = 0

        for i in range(self.last_audio_frame, frame_number-1):
            f.write("00" + "\n")

        f.write(data.hex() + "\n")

        self.last_audio_frame = frame_number


if __name__ == '__main__':
    SiriRemote("48:A9:1C:8A:13:65", Callback())
