from emulator import Emulator
from buttons import lecture_touche
import machine
import sdcard
import uos
from time import sleep_us, sleep
from machine import Pin, SPI
from xglcd_font import XglcdFont
from ssd1309 import Display
from random import randint
import buttons
 
# Assign chip select (CS) pin (and start it high)
cs = machine.Pin(17, machine.Pin.OUT)
 
# Intialize SPI peripheral (start with 1 MHz)
spi = machine.SPI(0,
                  baudrate=1000000,
                  polarity=0,
                  phase=0,
                  bits=8,
                  firstbit=machine.SPI.MSB,
                  sck=machine.Pin(18),
                  mosi=machine.Pin(19),
                  miso=machine.Pin(16))
 
spi_display = SPI(1, baudrate=10000000, sck=Pin(14), mosi=Pin(11))
display = Display(spi_display, dc=Pin(22), cs=Pin(28), rst=Pin(27))

# Initialize SD card
sd = sdcard.SDCard(spi, cs)
 
# Mount filesystem
vfs = uos.VfsFat(sd)
uos.mount(vfs, "/sd")

width = 128
height = 64
line = 1 
highlight = 1
shift = 0
list_length = 0
total_lines = 6
booleen_touche = 1

bally = XglcdFont('fonts/Bally7x9.c', 7, 9)


display.fill_rectangle(0,0, 128, 64, invert=False)#bas gauche
display.present()


