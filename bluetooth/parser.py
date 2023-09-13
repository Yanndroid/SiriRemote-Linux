def bytes_to_int(a, b):
    return a + (b << 8)


def int_to_bytes(i):
    return i & 0xff, i >> 8


class HCIPacket:
    TYPE_ACL_DATA_PACKET = 0x02
    TYPE_EVENT_PACKET = 0x04

    def __init__(self, data):
        self.type = data[0]
        self.content = data[1:]


class HCIEventPacket:
    _CODE_META_LE = 0x3e
    _CODE_DISCONNECTED = 0x05
    _SUB_EVENT_CONNECTION = 0x0a

    def __init__(self, data):
        code = data[0]
        self.content = data[2:]
        self.is_connection_event = (code == self._CODE_META_LE and self.content[0] == self._SUB_EVENT_CONNECTION)
        self.is_disconnect_event = (code == self._CODE_DISCONNECTED)

    def get_connection_handle(self):
        offset = 1 if self.is_connection_event else 0
        return bytes_to_int(self.content[1 + offset], self.content[2 + offset])


class HCIACLDataPacket:
    # L2CAP_CID_ATT = 0x0004

    def __init__(self, data):
        header = bytes_to_int(data[0], data[1])
        self.handle = header & 0x0fff
        self.length = bytes_to_int(data[4], data[5])
        self.content = data[4:]

        self.is_first = bool(header & 0x2000)
        self.is_fragment = self.length != len(self.content) - 4
        # self.is_att = (self.is_fragment or bytes_to_int(self.content[2], self.content[3]) == self.L2CAP_CID_ATT)


class ATTPacket:
    def __init__(self, data):
        self.length = bytes_to_int(data[0], data[1])
        self.method = data[4]
        self.handle = bytes_to_int(data[5], data[6]) if len(data) > 6 else None
        self.value = data[7:] if len(data) > 7 else None
