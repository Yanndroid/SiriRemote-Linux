import time
from signal import pause

import att


class DeviceListener(att.ATTDeviceListener):
    def on_connected(self, device):
        print("Connected", device._connection_handle)

        device.start_encryption()

        device.enable_notifications(0x0029)
        device.enable_notifications(0x002c)
        device.enable_notifications(0x0024)
        device.write_characteristic(0x001d, b'\xAF', False)

    def on_disconnected(self, device):
        print("Disconnected")

    def on_att_data(self, device, handle, value):
        # if len(value) == 101:
        #     n = value[4] + (value[5] << 8)
        #     print(f"{n:<3}", value.hex())
        # else:
        #     print(value.hex())
        print("Recv:", handle, value.hex())


if __name__ == '__main__':
    device = att.ATTDevice("48:A9:1C:8A:13:65", DeviceListener())
    device.connect()
    pause()
