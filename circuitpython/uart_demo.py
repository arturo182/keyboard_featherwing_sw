from bbq10keyboard import BBQ10Keyboard, STATE_PRESS, STATE_RELEASE, STATE_LONG_PRESS
from adafruit_display_text.label import Label
from adafruit_display_shapes.rect import Rect
import adafruit_ili9341
import terminalio
import displayio
import neopixel
import board
import busio
import time
import gc

# ui dimensions
header = 32
margin = 8
border = 1

# Release any resources currently in use for the displays
displayio.release_displays()

spi = board.SPI()
tft_cs = board.D9
tft_dc = board.D10

display_bus = displayio.FourWire(spi, command=tft_dc, chip_select=tft_cs)
display = adafruit_ili9341.ILI9341(display_bus, width=320, height=240)

uart = busio.UART(board.TX, board.RX, baudrate=115200, receiver_buffer_size=128)

i2c = board.I2C()
kbd = BBQ10Keyboard(i2c)

splash = displayio.Group(max_size=25)
display.show(splash)

# background
def bg_stripe(x, color):
    width = display.width // 8
    color_bitmap = displayio.Bitmap(width, 240, 1)
    color_palette = displayio.Palette(1)
    color_palette[0] = color
    bg_sprite = displayio.TileGrid(color_bitmap, x=x*width, y=0, pixel_shader=color_palette)
    splash.append(bg_sprite)

bg_stripe(0, 0x000000)
bg_stripe(1, 0x784F17)
bg_stripe(2, 0xFF0018)
bg_stripe(3, 0xFFA52C)
bg_stripe(4, 0xFFFF41)
bg_stripe(5, 0x008018)
bg_stripe(6, 0x0000F9)
bg_stripe(7, 0x86007D)

# output rect
output_rect = Rect(margin, margin, display.width-margin*2, display.height-margin*2-header-margin, fill=0xFFFFFF, outline=0x666666)
splash.append(output_rect)

# output header
header_rect = Rect(margin + border, margin+border, display.width-(margin+border)*2, header, fill=0xCCCCCC)
splash.append(header_rect)

header_text = Label(terminalio.FONT, text="UART Demo", x=margin*2+border, y=int(margin+border+header/2), color=0x000000)
splash.append(header_text)

# output text
p = displayio.Palette(2)
p.make_transparent(0)
p[1] = 0x000000

w, h = terminalio.FONT.get_bounding_box()
tilegrid = displayio.TileGrid(terminalio.FONT.bitmap, pixel_shader=p, x=margin*2+border, y=int(margin+border+header+margin/2), width=48, height=10, tile_width=w, tile_height=h)
term = terminalio.Terminal(tilegrid, terminalio.FONT)
splash.append(tilegrid)

# input textarea
input_rect = Rect(margin, display.height-margin-header, display.width-margin*2, header, fill=0xFFFFFF, outline=0x666666)
splash.append(input_rect)

# input text
input_text = Label(terminalio.FONT, text='', x=margin*2+border, y=int(display.height-margin-border-header*0.7), color=0x000000, max_glyphs=50)
splash.append(input_text)

# carret
carret = Rect(input_text.x + input_text.bounding_box[2] + 1, int(display.height-margin-header/2-header/4), 1, header//2, fill=0x000000)
splash.append(carret)

carret_blink_time = time.monotonic()
carret_blink_state = True

while True:
    # Carret blink animation
    if time.monotonic() - carret_blink_time >= 0.5:
        if carret_blink_state:
            splash.remove(carret)
        else:
            splash.append(carret)

        carret_blink_state = not carret_blink_state
        carret_blink_time = time.monotonic()

    # Get UART incoming data and print to terminal on screen
    if uart.in_waiting > 0:
        uart_in = uart.read(uart.in_waiting)

        print(uart_in)
        term.write(uart_in)

    # Process keyboard
    if kbd.key_count > 0:
        k = kbd.key
        if k[0] == STATE_RELEASE:
            if k[1] == '\x08': # Backspace
                if len(input_text.text) > 0:
                    input_text.text = input_text.text[:-1]
            elif k[1] == '\n': # Enter, send over UART
                text =  input_text.text + '\n'
                uart.write(text.encode('utf-8'))

                input_text.text = ''
            else: # Anything else, we add to the text field
                input_text.text += k[1]

            carret.x = input_text.x + input_text.bounding_box[2] + 1


