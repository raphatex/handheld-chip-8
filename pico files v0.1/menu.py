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

test=XglcdFont('fonts/Unispace12x24.c', 12, 24)
Wendy = XglcdFont('fonts/Wendy7x8.c', 7, 8)

 
def afficher(début,fin):
    x=0
    y=0
    display.clear()
    for lignes in menu[début:fin:]:
        display.draw_text(x,y,lignes,bally,False)
        y=y+10
    
def launch(filename):
    """ Launch the Python script <filename> """
    # clear the screen
    display.fill_rectangle(0,0,width,height,1)
    display.present()
    nb=1
    tps=0.125
    sleep(0.05)
    i1=False
    i2=True
    t=True
    while nb<120:
        display.draw_hline(3,50, nb, invert=False)
        nb=nb+1
        display.present()
        sleep(tps)
        tps=tps+0.005
        tps=tps*0.6
    
    sleep(0.60)
    chip8 = Emulator()
    chip8.readProg("/sd/games/"+filename)
    chip8.mainLoop()
    
def changement_ligne(x,y,menu,i):
    display.fill_rectangle(x,y, 121, 9, invert=False)
    display.draw_text(x,y,menu[i],bally,invert=True)
    display.present()



bally=XglcdFont('fonts/Bally7x9.c', 7, 9)



menu = []
fichiers_jeux=[]
for file in uos.listdir("/sd/games"):
    if file[len(file)-1]=="8":
        fichiers_jeux.append(file)
        if len(file)>20:
            menu.append(file[:15:]+"...")
        else:
            menu.append(file[:len(file)-4:])
menu_sans_emplacements=[]
for o in menu:
    menu_sans_emplacements.append(o)
for i in range(200):
    menu.append(" ")





delai = 1000
y = 0
for lignes in menu[0:6:]:
    x = 0
    for char in lignes:
        for i in range (7):
            random = chr(randint(97,122))
            display.draw_letter(x, y, random, bally)
            display.present()
            
            display.fill_rectangle(x,y,7,9, invert = True)
            display.present()
            sleep_us(delai)
        display.draw_letter(x, y, char, bally)
        x += 8
        display.present()
    delai = int(delai*0.70)
    y += 10

x=0
y=0
i=0
début=0
fin=6
while True:
            if y>=60:
                i=i-6
                y=0
                display.fill_rectangle(x,50, 121, 9, invert=True)
                display.draw_text(x,50,menu[i+5],bally,invert=False)
                display.present()
            elif menu[i]==" ":
                x=0
                display.fill_rectangle(x,50, 121, 9, invert=True)
                display.draw_text(x,50,menu[i],bally,invert=False)
                display.present()
                i=début
                y=0
            changement_ligne(x,y,menu,i)
            
            touche = lecture_touche()
            if touche == None:
                booleen_touche = 1
            
            if touche=="A" and booleen_touche == 1:
                launch(fichiers_jeux[i])
                booleen_touche = 0
            elif touche=="haut" and y==0 and booleen_touche == 1:
                i=i+5    
                y=50
                display.fill_rectangle(x,0, 121, 9, invert=True)
                display.draw_text(x,0,menu[i-5],bally,invert=False)
                display.present()
                booleen_touche = 0
            elif touche=="haut" and y!=0 and booleen_touche == 1:
                y=y-10
                i=i-1
                display.fill_rectangle(x,y+10, 121, 9, invert=True)
                display.draw_text(x,y+10,menu[i+1],bally,invert=False)
                display.present()
                booleen_touche = 0
            elif lecture_touche()=="bas" and booleen_touche == 1:
                y=y+10
                i=i+1
                display.fill_rectangle(x,y-10, 121, 9, invert=True)
                display.draw_text(x,y-10,menu[i-1],bally,invert=False)
                display.present()
                booleen_touche = 0
            elif touche=="droite" and len(menu_sans_emplacements)>=7 and booleen_touche == 1 and menu[i+7]!=" ":
                x=0
                début=début+7
                fin=fin+7
                afficher(début,fin)
                i=début
                y=0
                booleen_touche = 0
            elif touche=="gauche" and len(menu_sans_emplacements)>=7 and début!=0 and booleen_touche == 1:
                début=début-7
                fin=fin-7
                afficher(début,fin)
                i=début
                y=0
                booleen_touche = 0

