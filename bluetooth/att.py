import struct
from hci_user import HCISocket
from parser import *


class ATTDeviceListener:
    def on_connected(self, device):
        pass

    def on_disconnected(self, device):
        pass

    def on_att_data(self, device, handle, value):
        pass


class ATTFragmentMerger:
    def __init__(self, size):
        self.size = size
        self.value = bytearray()

    def append(self, data):
        self.value.extend(bytearray(data))
        return bytes(self.value) if len(self.value) >= self.size else None


class ATTDevice:

    def __init__(self, mac, listener: ATTDeviceListener):
        self._mac = mac
        self._listener = listener

        self._hci_socket = HCISocket(self._hci_callback)
        self._hci_socket.open()

        self._connection_handle = 0

        self._att_merger = None

    def connect(self):
        mac_bytes = list(reversed(bytearray.fromhex(self._mac.replace(':', ''))))

        # wtl = struct.pack("<BH8B", 0x01, 0x2011, 0x07, 0x00, *mac_bytes)
        # self._hci_socket.send(wtl)

        cmd = struct.pack("<BHBHH9B6H",
                          0x01, 0x200d, 0x19, 0x0060, 0x0060, 0x00, 0x00,
                          *mac_bytes,
                          0x00, 0x0018, 0x0028, 0x0000, 0x002a, 0x0000, 0x0000)
        self._hci_socket.send(cmd)

    def start_encryption(self):
        cmd = struct.pack(f"<BHBH8B2B16B",
                          0x01, 0x2019, 0x1c, 0x0007,
                          0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                          0x00, 0x00,
                          0x9d, 0x0d, 0x14, 0x4a, 0x07, 0xcc, 0x7e, 0xc3,
                          0xd6, 0x07, 0xb4, 0x4b, 0xfa, 0x20, 0x03, 0xb6)
        self._hci_socket.send(cmd)

    # def request_mtu(self, value):
    #     cmd = struct.pack(f"<B4HBH",
    #                       0x02,
    #                       self._connection_handle,
    #                       0x07, 0x03, 0x0004, 0x02,
    #                       value)
    #     self._hci_socket.send(cmd)

    # def read_characteristic(self, handle, command=True):
    #     method = 0x0a + (0x40 if command else 0x00)
    #     att_data = [method, *int_to_bytes(handle)]
    #     att_data_len = len(att_data)
    #     cmd = struct.pack(f"<B4H{att_data_len}B",
    #                       0x02,
    #                       self._connection_handle,
    #                       att_data_len + 4,
    #                       att_data_len,
    #                       0x0004,
    #                       *att_data)
    #     self._hci_socket.send(cmd)

    def write_characteristic(self, handle, value, command=True):
        method = 0x12 + (0x40 if command else 0x00)
        att_data = [method, *int_to_bytes(handle), *value]
        att_data_len = len(att_data)
        cmd = struct.pack(f"<B4H{att_data_len}B",
                          0x02,
                          self._connection_handle,
                          att_data_len + 4,
                          att_data_len,
                          0x0004,
                          *att_data)
        self._hci_socket.send(cmd)

    def enable_notifications(self, handle):
        self.write_characteristic(handle, b'\x01\x00')

    def _hci_callback(self, data):
        hci_packet = HCIPacket(data)
        if hci_packet.type == HCIPacket.TYPE_EVENT_PACKET:
            self._handle_hci_event(hci_packet.content)
        elif hci_packet.type == HCIPacket.TYPE_ACL_DATA_PACKET:
            self._handle_hci_acl_data(hci_packet.content)

    def _handle_hci_event(self, data):
        hci_event = HCIEventPacket(data)
        if hci_event.is_connection_event:
            mac = hci_event.content[6:12]
            print("Connect Event:", mac.hex())
            # TODO mac check
            self._connection_handle = hci_event.get_connection_handle()
            self._listener.on_connected(self)
        elif hci_event.is_disconnect_event:
            if hci_event.get_connection_handle() == self._connection_handle:
                self._listener.on_disconnected(self)

    def _handle_hci_acl_data(self, data):
        hci_acl_data = HCIACLDataPacket(data)

        # TODO testing (enable)
        # if hci_acl_data.handle != self._connection_handle:
        #     return

        if hci_acl_data.is_fragment:
            self._handle_hci_acl_frame(hci_acl_data)
        else:
            att_packet = ATTPacket(hci_acl_data.content)
            if att_packet.handle and att_packet.value:
                self._listener.on_att_data(self, att_packet.handle, att_packet.value)

    def _handle_hci_acl_frame(self, hci_acl_data):
        if hci_acl_data.is_first:
            self._att_merger = ATTFragmentMerger(hci_acl_data.length + 4)

        if self._att_merger:
            merged = self._att_merger.append(hci_acl_data.content)
            if merged:
                att_packet = ATTPacket(merged)
                self._listener.on_att_data(self, att_packet.handle, att_packet.value)
                self._att_merger = None
