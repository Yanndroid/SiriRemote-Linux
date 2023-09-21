from bluepy.btle import Peripheral, DefaultDelegate


class Device(DefaultDelegate):
    def __init__(self, mac):
        super().__init__()
        self.mac = mac
        self.__peripheral = None
        self.__listener = None

    def connect(self):
        self.__peripheral = Peripheral(self.mac)
        self.__peripheral.withDelegate(self)

    def loop(self):
        while True:
            self.__peripheral.waitForNotifications(0)

    def set_listener(self, listener):
        self.__listener = listener

    def write_characteristic(self, handle, value):
        self.__peripheral.writeCharacteristic(handle, value, True)

    def enable_notifications(self, handle):
        self.__peripheral.writeCharacteristic(handle, b'\x01\x00')

    def set_mtu(self, value):
        self.__peripheral.setMTU(value)

    def handleNotification(self, handle, data):
        # print(hex(handle), data.hex())  # TODO: testing

        if self.__listener:
            self.__listener(handle, data)
