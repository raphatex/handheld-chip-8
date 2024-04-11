from time import sleep_us, sleep
from machine import Pin, SPI
from xglcd_font import XglcdFont
from ssd1309 import Display
from random import randint
import pinout

texte = ["mastermind", "tetris", "pong", "Brick"]

spi_display = SPI(pinout.SPI_ID, baudrate=10000000, sck=pinout.PIN_D0, mosi=pinout.PIN_D1)
display = Display(spi_display, dc=pinout.PIN_A0, cs=pinout.PIN_CS, rst=pinout.PIN_RST)

print("Loading fonts.  Please wait.")
bally = XglcdFont('fonts/Bally7x9.c', 7, 9)

delai = 3000
y = 0
for lignes in texte:
    x = 0
    for char in lignes:
        for i in range (10):
            random = chr(randint(97,122))
            display.draw_letter(x, y, random, bally)
            display.present()
            
            sleep_us(delai)
            display.fill_rectangle(x,y,7,9, invert = True)
            display.present()
        display.draw_letter(x, y, char, bally)
        x += 8
        display.present()
    delai = int(delai*0.85)
    y += 10
    
sleep(2)

delai = 1000
y = (len(texte)-1)*10
for lignes in reversed(texte):
    x = (len(lignes)-1)*8
    for char in reversed(lignes):
        for k in range (10):
            display.fill_rectangle(x,y,7,9, invert = True)
            display.present()

            sleep_us(delai)
            
            random = chr(randint(97,122))
            display.draw_letter(x, y, random, bally)
            display.present()
            
        display.fill_rectangle(x,y,7,9, invert = True)
        x -= 8
        display.present()
    y -= 10





