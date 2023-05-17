# SiriRemote-Linux

This project allows the usage of an Apple TV 4th Siri Remote with Linux.

Do you have an old remote lying around and would like to control your linux machine with it? Then this is for you. This
python program connects to and intercepts the data from a SiriRemote over bluetooth and does something useful with it,
like change the volume or control media. Even the touchpad is working and if you know a bit of python, you can basically
do anything with it.

## Usage

### Preparations (only once)

Pair the remote with you machine:

```commandline
bluetoothctl
power on
scan on
```

Press `MENU` and `+` for few seconds and the remote will show up in bluetoothctl. The mac address should start
with `48:A9:1C:`.

```commandline
pair <mac-address>
disconnect <mac-address>
exit
```

Install the python dependencies:

```commandline
pip install bluepy evdev
```

### Media control

This will connect to the remote and simulate an input device for your machine.

Run the main program (`<mac-address>` being the remote mac address)

```commandline
sudo python ./main.py <mac-address>
```

Press any button on the remote, and you should now be able to control the volume, media and the mouse cursor (menu /
airplay = prev. / next song). The remote will disconnect after a while of inactivity but as soon as you press any button
it will reconnect.

### Custom

This repo provides a [SiriRemote](remote/remote.py) class which you can use to easily interface with the remote and
receive button and touchpad events. You can see a simple example for it in [echo_test.py](echo_test.py).

# Internal working of the SiriRemote

Huge thanks to [Jack-R1](https://github.com/Jack-R1). Without his previous work, I wouldn't have made it this far.

The remote communicates with HID over GATT, but since it's an Apple product you need to do some additional stuff, just
to
receive data. And even then it doesn't work on its own.

## GATT Layout

```
Service: "Generic Access" | UUID: 00001800-0000-1000-8000-00805f9b34fb | Handle: 0x1
  Char: "Device Name" | UUID: 00002a00-0000-1000-8000-00805f9b34fb | Handle: 0x2 | Value Handle: 0x3
  Char: "Appearance" | UUID: 00002a01-0000-1000-8000-00805f9b34fb | Handle: 0x4 | Value Handle: 0x5
Service: "Generic Attribute" | UUID: 00001801-0000-1000-8000-00805f9b34fb | Handle: 0x6
  Char: "Service Changed" | UUID: 00002a05-0000-1000-8000-00805f9b34fb | Handle: 0x7 | Value Handle: 0x8
    Desc: "Client Characteristic Configuration" | UUID: 00002902-0000-1000-8000-00805f9b34fb | Handle: 0x9
Service: "Device Information" | UUID: 0000180a-0000-1000-8000-00805f9b34fb | Handle: 0xa
  Char: "Serial Number String" | UUID: 00002a25-0000-1000-8000-00805f9b34fb | Handle: 0xb | Value Handle: 0xc
  Char: "Hardware Revision String" | UUID: 00002a27-0000-1000-8000-00805f9b34fb | Handle: 0xd | Value Handle: 0xe
  Char: "Firmware Revision String" | UUID: 00002a26-0000-1000-8000-00805f9b34fb | Handle: 0xf | Value Handle: 0x10
  Char: "Manufacturer Name String" | UUID: 00002a29-0000-1000-8000-00805f9b34fb | Handle: 0x11 | Value Handle: 0x12
  Char: "PnP ID" | UUID: 00002a50-0000-1000-8000-00805f9b34fb | Handle: 0x13 | Value Handle: 0x14
Service: "Human Interface Device" | UUID: 00001812-0000-1000-8000-00805f9b34fb | Handle: 0x15
  Char: "HID Information" | UUID: 00002a4a-0000-1000-8000-00805f9b34fb | Handle: 0x16 | Value Handle: 0x17
  Char: "Report Map" | UUID: 00002a4b-0000-1000-8000-00805f9b34fb | Handle: 0x18 | Value Handle: 0x19
  Char: "HID Control Point" | UUID: 00002a4c-0000-1000-8000-00805f9b34fb | Handle: 0x1a | Value Handle: 0x1b
  Char: "Report" | UUID: 00002a4d-0000-1000-8000-00805f9b34fb | Handle: 0x1c | Value Handle: 0x1d
    Desc: "Report Reference" | UUID: 00002908-0000-1000-8000-00805f9b34fb | Handle: 0x1e
  Char: "Report" | UUID: 00002a4d-0000-1000-8000-00805f9b34fb | Handle: 0x1f | Value Handle: 0x20
    Desc: "Report Reference" | UUID: 00002908-0000-1000-8000-00805f9b34fb | Handle: 0x21
  Char: "Report" | UUID: 00002a4d-0000-1000-8000-00805f9b34fb | Handle: 0x22 | Value Handle: 0x23
    Desc: "Client Characteristic Configuration" | UUID: 00002902-0000-1000-8000-00805f9b34fb | Handle: 0x24
    Desc: "Report Reference" | UUID: 00002908-0000-1000-8000-00805f9b34fb | Handle: 0x25
Service: "Battery Service" | UUID: 0000180f-0000-1000-8000-00805f9b34fb | Handle: 0x26
  Char: "Battery Level" | UUID: 00002a19-0000-1000-8000-00805f9b34fb | Handle: 0x27 | Value Handle: 0x28
    Desc: "Client Characteristic Configuration" | UUID: 00002902-0000-1000-8000-00805f9b34fb | Handle: 0x29
  Char: "2a1a" | UUID: 00002a1a-0000-1000-8000-00805f9b34fb | Handle: 0x2a | Value Handle: 0x2b
    Desc: "Client Characteristic Configuration" | UUID: 00002902-0000-1000-8000-00805f9b34fb | Handle: 0x2c
Service: "Bond Management" | UUID: 0000181e-0000-1000-8000-00805f9b34fb | Handle: 0x2d
  Char: "Bond Management Control Point" | UUID: 00002aa4-0000-1000-8000-00805f9b34fb | Handle: 0x2e | Value Handle: 0x2f
  Char: "Bond Management Feature" | UUID: 00002aa5-0000-1000-8000-00805f9b34fb | Handle: 0x30 | Value Handle: 0x31
Service: "8341f2b4-c013-4f04-8197-c4cdb42e26dc" | UUID: 8341f2b4-c013-4f04-8197-c4cdb42e26dc | Handle: 0x32
  Char: "9fbf120d-6301-42d9-8c58-25e699a21dbd" | UUID: 9fbf120d-6301-42d9-8c58-25e699a21dbd | Handle: 0x33 | Value Handle: 0x34
  Char: "2bdcaebe-8746-45df-a841-96b840980fb7" | UUID: 2bdcaebe-8746-45df-a841-96b840980fb7 | Handle: 0x35 | Value Handle: 0x36
  Char: "2bdcaebe-8746-45df-a841-96b840980fb8" | UUID: 2bdcaebe-8746-45df-a841-96b840980fb8 | Handle: 0x37 | Value Handle: 0x38
  Char: "30e69638-3752-4feb-a3aa-3226bcd05ace" | UUID: 30e69638-3752-4feb-a3aa-3226bcd05ace | Handle: 0x39 | Value Handle: 0x3a
    Desc: "Client Characteristic Configuration" | UUID: 00002902-0000-1000-8000-00805f9b34fb | Handle: 0x3b
```

## Battery information

### Battery level

Enable notifications on handle `0x0027`, by writing `0x01 0x00` to `0x0029`. You'll then receive values from `0x0028`
ranging from `0x00` to `0x64`, which are 0 to 100 as integer and represent the battery percentage.

### Charging state

Enable notifications on handle `0x002a`, by writing `0x01 0x00` to `0x002c`. Possible values you'll receive
from `0x002b` are:

- `0xAB` charging
- `0xAF` discharging
- `0xBB` plugged in

## Enable input

To receive input data from the remote we need to send `0xAF` to the handle `0x001d` and also enable notifications
on handle `0x0022`, by writing `0x01 0x00` to `0x0024`. You'll then receive byte arrays from `0x0023` with a length of
either 2, 13, 20 or 101[^audio].

### Buttons

Button presses are sent with the second byte and are encoded bitwise, so it also supports multiple presses:

- `0x00` All released
- `0x01` AirPlay
- `0x02` Volume up
- `0x04` Volume down
- `0x08` Play/Pause
- `0x10` Siri
- `0x20` Menu
- `0x80` Touchpad

### Touch

Touch events are sent with a 13 byte array (or 20 with two fingers). The first 6 are general information and the
following 7 are the data of the touch position.

| Index | Content                       |
|-------|-------------------------------|
| 0     | Finger count                  |
| 1     | [Pressed buttons](#Buttons)   |
| 2     | always 50                     |
| 3     | ?                             |
| 4     | ?                             |
| 5     | ? (increases over time)       |
|       |                               |
| 6     | [X coordinate](#X-coordinate) |
| 7     | [X coordinate](#X-coordinate) |
| 8     | [Y coordinate](#Y-coordinate) |
| 9     | ? (0 when released)           |
| 10    | ? (0 when released)           |
| 11    | pressure                      |
| 12    | ?                             |
|       |                               |
| 13-19 | see 6-12 (second finger)      |

#### X coordinate

The X coordinate consists of two bytes at the indices 6 and 7. However only the first 3 bits of the byte at index 7 are
required. The SiriRemote's touchpad has the weird property of having 8 vertical "zones" and the byte at index 6 only
gives us the location in such a "zone". The byte at index 7 gives us the remaining information for the "zone" index.

`x = data[6] + 255 * (data[7] & 7)`

#### Y coordinate

The Y coordinate is pretty strait forward. The value (bottom to top) goes from 188 to 255 and then from 0 to 38. I
assume it's a signed bytes which would explain this behaviour.

The resolution is pretty low compared to the X coordinate, so there might be something else that contributes to the Y
coordinate, that I haven't found yet.

### Audio/Siri

Unfortunately I wasn't able to test the data we receive from the microphone, because of a linux limitation[^audio].

All I know for now is that you're supposed to get 101 bytes of which the majority is opus encoded audio data. You can
check out [Jack-R1](https://github.com/Jack-R1)'s repos for more information about this.

[^audio]: 101 bytes are received when Siri/Audio is used, but bluez somehow can't handle more than 20 bytes. The bytes
do however appear in wireshark.