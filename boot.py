from board import *
import digitalio
import usb_hid
import storage

# =======================
# original by dbisu
# =======================

print("BadUSB-BT v2 by nevadex\nOriginal BadUSB by dbisu\n")
print("SRC: https://github.com/nevadex/badusb-bt")

usb_hid.enable((usb_hid.Device.MOUSE, usb_hid.Device.CONSUMER_CONTROL, usb_hid.Device.KEYBOARD))

noStorageStatus = False
noStoragePin = digitalio.DigitalInOut(GP15)
noStoragePin.switch_to_input(pull=digitalio.Pull.UP)
noStorageStatus = noStoragePin.value  # usb normally off

# prog/safe mode kinda useless
progStatusPin = digitalio.DigitalInOut(GP0)
progStatusPin.switch_to_input(pull=digitalio.Pull.UP)
progStatus = not progStatusPin.value  # safe normally off

if noStorageStatus and not progStatus:
    # don't show USB drive to host PC
    storage.disable_usb_drive()
    print("[BOOT] USB drive disabled")
    storage.remount("/", False)
else:
    # edit boot
    print("[BOOT] USB drive enabled")
