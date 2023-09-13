import socket
import struct
import threading


class HCISocket:

    def __init__(self, listener):
        self._listener = listener
        self._socket = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_RAW, socket.BTPROTO_HCI)
        self._socket.setsockopt(socket.SOL_HCI, socket.HCI_DATA_DIR, 1)
        self._socket.setsockopt(socket.SOL_HCI, socket.HCI_TIME_STAMP, 1)
        self._socket.setsockopt(socket.SOL_HCI, socket.HCI_FILTER,
                                struct.pack("IIIh2x", 0xffffffff, 0xffffffff, 0xffffffff, 0))

    def _data_listener(self):
        while True:
            self._listener(self._socket.recv(1024))

    def open(self):
        self._socket.bind((0,))
        threading.Thread(target=self._data_listener, daemon=True).start()

    def close(self):
        # TODO: stop thread? (is daemon anyway)
        self._socket.close()

    def send(self, data):
        print("Send:", data.hex())
        self._socket.send(data)
