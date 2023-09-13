import ctypes
import socket
import threading


class _HCISocketAddress(ctypes.Structure):
    _fields_ = [
        ("sin_family", ctypes.c_ushort),
        ("hci_dev", ctypes.c_ushort),
        ("hci_channel", ctypes.c_ushort),
    ]


class HCISocket:

    def __init__(self, listener):
        self._listener = listener

        sa_pointer = ctypes.POINTER(_HCISocketAddress)
        ctypes.cdll.LoadLibrary("libc.so.6")
        libc = ctypes.CDLL("libc.so.6")

        c_socket = libc.socket
        c_socket.argtypes = (ctypes.c_int, ctypes.c_int, ctypes.c_int)
        c_socket.restype = ctypes.c_int

        c_bind = libc.bind
        c_bind.argtypes = (ctypes.c_int, ctypes.POINTER(_HCISocketAddress), ctypes.c_int)
        c_bind.restype = ctypes.c_int

        s = c_socket(31, 3, 1)  # (AF_BLUETOOTH, SOCK_RAW, HCI_CHANNEL_USER)
        if s < 0: raise Exception("Unable to open AF_BLUETOOTH socket")

        sa = _HCISocketAddress()
        sa.sin_family = 31  # AF_BLUETOOTH
        sa.hci_dev = 0  # adapter index
        sa.hci_channel = 1  # HCI_USER_CHANNEL

        r = c_bind(s, sa_pointer(sa), ctypes.sizeof(sa))
        if r != 0: raise Exception("Unable to bind")

        self._socket = socket.fromfd(s, 31, 3, 1)

    def _data_listener(self):
        while True:
            self._listener(self._socket.recv(1024))

    def open(self):
        # self._socket.bind((0,))
        threading.Thread(target=self._data_listener, daemon=True).start()

    def close(self):
        # TODO: stop thread? (is daemon anyway)
        self._socket.close()

    def send(self, data):
        print("Send:", data.hex())
        self._socket.send(data)
