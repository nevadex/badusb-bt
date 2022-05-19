# BadUSB-BT
## Bluetooth controlled rubber ducky device
> Designed and tested on raspberry pi pico

[*Original by dbisu*](https://github.com/dbisu/pico-ducky/)

---
**Requirements:**
- A board that supports circuit python, USB, and UART (rpi pico)
- A bluetooth module, such as HC-05, HC-06, etc. that have UART output (hc-05)
- A device and application to control it (I have provided a basic android app)

# Pre-setup
1. Configure your bluetooth module using AT firmware or other.  
2. Wire your BT module's VCC, GND, TX, and RX pins to the board. Remember TX from module goes to RX on the board, and vice versa.  
3. Install circuit python for your board  

# Setup
1. Download `adafruit-circuitpython-bundle-7.x-mpy-YYYYMMDD.zip` [here](https://github.com/adafruit/Adafruit_CircuitPython_Bundle/releases/latest) and extract it outside the drive.
2. Navigate to `lib` in the recently extracted folder and copy `adafruit_hid` to the `lib` folder in your `CIRCUITPY` drive.
3. From the repo, download [boot.py](https://github.com/nevadex/badusb-bt/blob/main/boot.py) to the `CIRCUITPY` drive and download [code.py](https://github.com/nevadex/badusb-bt/blob/main/code.py) to a location outside of the drive.
4. Edit `code.py` at config section (line 17) and change the values to ones specific to your bt module and how it is connected to your board.
5. Copy `code.py` to the `CIRCUITPY` drive, then unplug the device from your computer.

# Safe Mode and USB Enable Mode  
By default, the script will run when connected to a computer, and the `CIRCUITPY` drive will not appear. In order to access the drive in the future, there are two ways.
1. [Safe mode (Setup on original)](https://github.com/dbisu/pico-ducky/#setup-mode): **Connect PIN1`GP0` to PIN3`GND`**<br>This will prevent the BT script from running.
2. [USB Enable mode](https://github.com/dbisu/pico-ducky/#usb-enabledisable-mode): **Connect PIN18`GND` to PIN20`GP15`**<br>This will enable the USB drive so it can be accessed from a computer. Do not write to the payload via app or use DS command when this is enabled.

In case of neither above methods working, or a bricked installation, some boards like RPi Pico have a BOOTSEL button that resets on-board memory so you can fix any weird issues.

# My Control App  
I created an MIT App Inventor app for using the device. You can create your own too, the bluetooth documentation is below.  
To use my app, either:
- Download and install the prebuilt apk from [here](https://github.com/nevadex/badusb-bt/blob/main/badusb_btc.apk)
- Build from source using the aia file [here](https://github.com/nevadex/badusb-bt/blob/main/badusb_btcv2_android.aia)

The app is extremely basic, and will automatically connect to the first device in your paired device list, so theres that :/

# Bluetooth Serial Documentation  
The bluetooth serial can be used by any app, as long as you send the right syntax.  
**SYNTAX: CMD+DATA  
EXAMPLE: MS+1 (mouse scroll up)**  
## List of all commands  

| Name             | Command | Description                                  | Example            | Accepted Data                                                                                                   |
|------------------|---------|----------------------------------------------|--------------------|-----------------------------------------------------------------------------------------------------------------|
| Ducky Keyboard   | DK      | Runs a one line duckyscript command          | DK+A               | Duckyscript                                                                                                     |
| Ducky Entry      | DE      | Runs a one line duckyscript command          | DK+CTRL ALT DELETE | Duckyscript                                                                                                     |
| Mouse Button     | MB      | Clicks(press and release) a mouse button     | MB+right           | ["left", "right", "middle"]                                                                                     |
| Mouse Press      | MP      | Presses and holds a mouse button             | MP+left            | ["left", "right", "middle"]                                                                                     |
| Mouse Release    | MR      | Releases a mouse button                      | MR+left            | ["left", "right", "middle"]                                                                                     |
| Mouse Scroll     | MS      | Scroll wheel                                 | MS+-1              | [-1, 0, 1]                                                                                                      |
| Mouse Movement   | MM      | Move mouse in terms of X, Y, and scroll(w)   | MM+100,100,0       | x and y: integer<br>scroll(w): [-1, 0, 1]<br>format: "x,y,w"                                                    |
| Consumer Control | CC      | Runs a consumer control keycode              | CC+205             | Integer defined in [consumer control standards](https://www.usb.org/sites/default/files/hut1_21_0.pdf#page=118) |
| Ducky Payload    | DP      | Run duckyscript file "payload.dd" on device  | DP+                | None                                                                                                            |
| Ducky Save       | DS      | Save duckyscript to "payload.dd" on device   | DS+CTRL ALT DELETE | Duckyscript                                                                                                     |
| Ducky Read       | DR      | Read duckyscript file "payload.dd" on device | DR+                | None                                                                                                            |

All commands return a response except Mouse Movement.  
All responses follow a common scheme: `<exec>type[data] ... status`  
Example: `<dd-exec>key[a] ... OK`  
These can be parsed and processed if needed.  
Ducky Read returns two responses:
- `<dd-exec>ddread[payload.dd] ... OK` which contains no data
- `<data>ddread[DATA] ... OK`, where `DATA` is the duckyscript read from the file

---

> nevadex (c) 2022 via [GNU-GPL v2](https://github.com/nevadex/badusb-bt/blob/main/LICENSE)
