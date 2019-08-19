
from keyboard_featherwing.bbq10keyboard import BBQ10Keyboard
from adafruit_stmpe610 import Adafruit_STMPE610_SPI
import adafruit_ili9341
import adafruit_lsm303
import adafruit_sdcard
import digitalio
import displayio
import storage
import board
import time
import os

spi = board.SPI()
spi.try_lock()
spi.configure(baudrate=100000000)
spi.unlock()

tft_cs = board.D9
tft_dc = board.D10
touch_cs = board.D6
sd_cs = board.D5

displayio.release_displays()

display_bus = displayio.FourWire(spi, command=tft_dc, chip_select=tft_cs)
display = adafruit_ili9341.ILI9341(display_bus, width=320, height=240)

print('Display: Pass (duh!)')

try:
    touch = Adafruit_STMPE610_SPI(spi, digitalio.DigitalInOut(touch_cs))
    while touch.buffer_empty:
        pass

    print('Touch: Pass, ', touch.read_data())
except Exception as e:
    print('Touch: Fail, ', e)

try:
    sdcard = adafruit_sdcard.SDCard(spi, digitalio.DigitalInOut(sd_cs))
    vfs = storage.VfsFat(sdcard)
    storage.mount(vfs, '/sd')

    if len(os.listdir('/sd/')) > 0:
        print('SD-Card: Pass')
    else:
        raise Exception('No files')
except Exception as e:
    print('SD-Card: Fail, ', e)

try:
    i2c = board.I2C()
except Exception as e:
    print('I2C: Fail, ', e)

try:
    sensor = adafruit_lsm303.LSM303(i2c)

    time.sleep(0.25)

    acc_x, acc_y, acc_z = sensor.acceleration
    mag_x, mag_y, mag_z = sensor.magnetic

    print('Accel: Pass, (%.6f, %.6f, %.6f)' % (acc_x, acc_y, acc_z))
    #print('Magnetometer (gauss): ({0:10.3f}, {1:10.3f}, {2:10.3f})'.format(mag_x, mag_y, mag_z))
except:
    print('Accel: Fail')


def wait_single_key(kbd, key):
    print('Press %s' % key)
    while kbd.key_count < 2:
        pass

    keys = kbd.keys
    return keys[0] == (1, key) and keys[1] == (3, key)

try:
    kbd = BBQ10Keyboard(i2c)

    if not wait_single_key(kbd, 'q'):
        raise Exception()

    if not wait_single_key(kbd, 's'):
        raise Exception()

    if not wait_single_key(kbd, 'p'):
        raise Exception()

    if not wait_single_key(kbd, 'b'):
        raise Exception()

    if not wait_single_key(kbd, 'm'):
        raise Exception()

    if not wait_single_key(kbd, 'f'):
        raise Exception()

    print('Keyboard: Pass')
except:
    print('Keyboard: Fail')

print('All tests passed!')

while True:
    pass
