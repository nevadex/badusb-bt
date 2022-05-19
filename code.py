import usb_hid
from adafruit_hid.mouse import Mouse
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS as KeyboardLayout
from adafruit_hid.keycode import Keycode
import supervisor
import time
import digitalio
from board import *
import busio

# =======================
# original by dbisu
# =======================

# config

BAUDRATE = 9600  # default 9600
# check your board's UART compatible pins
TX_PIN = GP12    # rx pin on bt module
RX_PIN = GP13    # tx pin on bt module
EN_PIN = GP11    # not used

duckyCommands = {
    'WINDOWS': Keycode.WINDOWS, 'GUI': Keycode.GUI, 'CMD': Keycode.GUI,
    'APP': Keycode.APPLICATION, 'MENU': Keycode.APPLICATION, 'SHIFT': Keycode.SHIFT,
    'ALT': Keycode.ALT, 'CONTROL': Keycode.CONTROL, 'CTRL': Keycode.CONTROL,
    'DOWNARROW': Keycode.DOWN_ARROW, 'DOWN': Keycode.DOWN_ARROW, 'LEFTARROW': Keycode.LEFT_ARROW,
    'LEFT': Keycode.LEFT_ARROW, 'RIGHTARROW': Keycode.RIGHT_ARROW, 'RIGHT': Keycode.RIGHT_ARROW,
    'UPARROW': Keycode.UP_ARROW, 'UP': Keycode.UP_ARROW, 'BREAK': Keycode.PAUSE,
    'PAUSE': Keycode.PAUSE, 'CAPSLOCK': Keycode.CAPS_LOCK, 'DELETE': Keycode.DELETE,
    'END': Keycode.END, 'ESC': Keycode.ESCAPE, 'ESCAPE': Keycode.ESCAPE, 'HOME': Keycode.HOME,
    'INSERT': Keycode.INSERT, 'NUMLOCK': Keycode.KEYPAD_NUMLOCK, 'PAGEUP': Keycode.PAGE_UP,
    'PAGEDOWN': Keycode.PAGE_DOWN, 'PRINTSCREEN': Keycode.PRINT_SCREEN, 'ENTER': Keycode.ENTER,
    'SCROLLLOCK': Keycode.SCROLL_LOCK, 'SPACE': Keycode.SPACE, 'TAB': Keycode.TAB,
    'BACKSPACE': Keycode.BACKSPACE,
    'A': Keycode.A, 'B': Keycode.B, 'C': Keycode.C, 'D': Keycode.D, 'E': Keycode.E,
    'F': Keycode.F, 'G': Keycode.G, 'H': Keycode.H, 'I': Keycode.I, 'J': Keycode.J,
    'K': Keycode.K, 'L': Keycode.L, 'M': Keycode.M, 'N': Keycode.N, 'O': Keycode.O,
    'P': Keycode.P, 'Q': Keycode.Q, 'R': Keycode.R, 'S': Keycode.S, 'T': Keycode.T,
    'U': Keycode.U, 'V': Keycode.V, 'W': Keycode.W, 'X': Keycode.X, 'Y': Keycode.Y,
    'Z': Keycode.Z, 'F1': Keycode.F1, 'F2': Keycode.F2, 'F3': Keycode.F3,
    'F4': Keycode.F4, 'F5': Keycode.F5, 'F6': Keycode.F6, 'F7': Keycode.F7,
    'F8': Keycode.F8, 'F9': Keycode.F9, 'F10': Keycode.F10, 'F11': Keycode.F11,
    'F12': Keycode.F12,
    '.': Keycode.PERIOD, ',': Keycode.COMMA, '/': Keycode.FORWARD_SLASH, '\\': Keycode.BACKSLASH,
    '1': Keycode.ONE, '2': Keycode.TWO, '3': Keycode.THREE, '4': Keycode.FOUR, '5': Keycode.FIVE,
    '6': Keycode.SIX, '7': Keycode.SEVEN, '8': Keycode.EIGHT, '9': Keycode.NINE, '0': Keycode.ZERO,
}


def convertLine(line):
    newline = []
    # loop on each key - the filter removes empty values
    for key in filter(None, line.split(" ")):
        key = key.upper()
        # find the keycode for the command in the list
        command_keycode = duckyCommands.get(key, None)
        if command_keycode is not None:
            # if it exists in the list, use it
            newline.append(command_keycode)
        elif hasattr(Keycode, key):
            # if it's in the Keycode module, use it (allows any valid keycode)
            newline.append(getattr(Keycode, key))
        else:
            # if it's not a known key name, show the error for diagnosis
            print(f"[DD] Unknown key: <{key}>")
            BTuart.write(createBTStatus('error', key, 'ERROR: UNKNOWN KEY'))
    return newline


def runScriptLine(line):
    for k in line:
        kbd.press(k)
    kbd.release_all()


def sendString(line):
    layout.write(line)


def parseLine(line):
    global defaultDelay
    if line[0:3].upper() == "REM":
        # ignore ducky script comments
        pass
    elif line[0:5].upper() == "DELAY":
        time.sleep(float(line[6:]) / 1000)
    elif line[0:6].upper() == "STRING":
        sendString(line[7:])
    elif line[0:5].upper() == "PRINT":
        print("[DD-SCRIPT]: " + line[6:])
        BTuart.write(createBTStatus('print', line[6:], 'OK', exec='dd-scpt'))
    elif line[0:6].upper() == "IMPORT":
        # runScript(line[7:])
        # disabled
        BTuart.write(createBTStatus('error', 'IMPORT', 'ERROR: IMPORT DISABLED'))
        pass
    elif line[0:13].upper() == "DEFAULT_DELAY":
        defaultDelay = int(line[14:]) * 10
    elif line[0:12].upper() == "DEFAULTDELAY":
        defaultDelay = int(line[13:]) * 10
    elif line[0:3].upper() == "LED":
        # led.value = not led.value
        pass
    else:
        newScriptLine = convertLine(line)
        runScriptLine(newScriptLine)


kbd = Keyboard(usb_hid.devices)
layout = KeyboardLayout(kbd)

ms = Mouse(usb_hid.devices)
cc = ConsumerControl(usb_hid.devices)

# turn off automatically reloading when files are written to the pico
supervisor.disable_autoreload()

# sleep at the start to allow the device to be recognized by the host computer
time.sleep(.5)


def createBTStatus(type, value, status, exec='dd-exec'):
    text = '<' + exec + '>' + type + '[' + value + '] ... ' + status + '\r\n'
    return bytes(text, 'utf-8')


def getProgrammingStatus():
    # check GP0 for safe mode
    progStatusPin = digitalio.DigitalInOut(GP0)
    progStatusPin.switch_to_input(pull=digitalio.Pull.UP)
    progStatus = not progStatusPin.value
    return progStatus


defaultDelay = 0


def runScript(file):
    global defaultDelay

    duckyScriptPath = file
    try:
        f = open(duckyScriptPath, "r", encoding='utf-8')
        previousLine = ""
        for line in f:
            line = line.rstrip()
            if line[0:6] == "REPEAT":
                for i in range(int(line[7:])):
                    # repeat the last command
                    parseLine(previousLine)
                    time.sleep(float(defaultDelay) / 1000)
            else:
                parseLine(line)
                previousLine = line
            time.sleep(float(defaultDelay) / 1000)
        f.close()
    except OSError as e:
        print("[DD] Unable to open file ", file)


def selectPayload():
    return "payload.dd"


progStatus = False
progStatus = getProgrammingStatus()

# en/key on GP11 (kinda useless)
BTuart = busio.UART(tx=TX_PIN, rx=RX_PIN, baudrate=BAUDRATE)

if not progStatus:
    print("[BB] Loaded program, entering bluetooth mode")

    try:
        # main loop
        while True:
            if BTuart.in_waiting > 0:
                raw = BTuart.readline()

                if raw is not None:
                    raw = raw.decode("utf-8")
                    raw = raw.replace("\r\n", "")
                    print(raw)
                    command = raw[0:2]
                    data = raw[3:]

                    if command == "DK":  # ducky keyboard
                        parseLine(data)
                        write = '<dd-exec>[' + data + ']\r\n'
                        BTuart.write(createBTStatus('key', data, 'OK'))
                    elif command == "DE":  # ducky entry
                        parseLine(data)
                        write = '<dd-exec>[' + data + ']\r\n'
                        BTuart.write(createBTStatus('ddentry', data, 'OK'))
                    elif command == "MB":  # mouse button
                        if data == "left":
                            ms.click(Mouse.LEFT_BUTTON)
                        elif data == "middle":
                            ms.click(Mouse.MIDDLE_BUTTON)
                        elif data == "right":
                            ms.click(Mouse.RIGHT_BUTTON)
                        BTuart.write(createBTStatus('msbtn', data, 'OK'))
                    elif command == "MP":  # mouse press
                        if data == "left":
                            ms.press(Mouse.LEFT_BUTTON)
                        elif data == "middle":
                            ms.press(Mouse.MIDDLE_BUTTON)
                        elif data == "right":
                            ms.press(Mouse.RIGHT_BUTTON)
                        BTuart.write(createBTStatus('mspress', data, 'OK'))
                    elif command == "MR":  # mouse release
                        if data == "left":
                            ms.release(Mouse.LEFT_BUTTON)
                        elif data == "middle":
                            ms.release(Mouse.MIDDLE_BUTTON)
                        elif data == "right":
                            ms.release(Mouse.RIGHT_BUTTON)
                        BTuart.write(createBTStatus('msrelease', data, 'OK'))
                    elif command == "MS":  # mouse scroll
                        ms.move(x=0, y=0, wheel=int(data))
                        BTuart.write(createBTStatus('scroll', data, 'OK'))
                    elif command == "MM":  # mouse movement
                        values = data.split(",")  # 0=x, 1=y, 2=w
                        ms.move(x=int(values[0]), y=int(values[1]), wheel=int(values[2]))
                        # no response due to high send rate
                    elif command == "CC":  # consumer control
                        cc.send(int(data))
                        BTuart.write(createBTStatus('cc', data, 'OK'))
                    elif command == "DP":  # ducky payload
                        runScript(selectPayload())
                        BTuart.write(createBTStatus('ddpayload', selectPayload(), 'OK'))
                    elif command == "DS":  # ducky save
                        f = open(selectPayload(), "w", encoding='utf-8')
                        dd = data.replace("<NEWLINE>", "\n")
                        f.write(dd)
                        f.close()
                        BTuart.write(createBTStatus('ddsave', selectPayload(), 'OK'))
                    elif command == "DR":  # ducky read
                        f = open(selectPayload(), "r", encoding='utf-8')
                        dd = f.read()
                        f.close()
                        dd = dd.replace("\n", "<NEWLINE>")
                        BTuart.write(createBTStatus('ddread', dd, 'OK', exec='data'))
                        BTuart.write(createBTStatus('ddread', selectPayload(), 'OK'))
    except KeyboardInterrupt:
        print("[BB] Keyboard Interrupt. Exiting")

    except Exception as ex:
        print("[BB] Encountered an error.\n=====" + str(ex) + "=====\nRestarting")
        supervisor.reload()
else:
    print("[BB] Safe mode, program not active")
