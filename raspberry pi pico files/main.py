from machine import Pin, SPI
from ssd1309 import Display
import pinout
from buttons import lecture_touche
import uos
from time import sleep_us, sleep
from utime import ticks_ms
from random import randint

spi_display = SPI(pinout.SPI_ID, baudrate=10000000, sck=pinout.PIN_D0, mosi=pinout.PIN_D1)
display = Display(spi_display, dc=pinout.PIN_A0, cs=pinout.PIN_CS, rst=pinout.PIN_RST)

display.fill_rectangle(0, 0, 127, 63)
display.present()
from xglcd_font import XglcdFont
bally = XglcdFont('fonts/Bally7x9.c', 7, 9)
from emulator import Emulator
from beatmaker import BeatMaker


if pinout.SD_READER:
    import sdcard
    
    # Assign chip select (CS) pin (and start it high)
    cs = Pin(pinout.SD_CS, Pin.OUT)
     
    # Intialize SPI peripheral (start with 1 MHz)
    spi = SPI(1,baudrate=1000000,polarity=0,phase=0,bits=8,firstbit=SPI.MSB,sck=pinout.SD_SCLK,mosi=pinout.SD_MOSI,miso=pinout.SD_MISO)
    
    # Initialize SD card
    sd = sdcard.SDCard(spi, cs)
    
    # Mount filesystem
    vfs = uos.VfsFat(sd)
    uos.mount(vfs, "/sd")
    root = "/sd/"
    
else:
    root = ""

class Fichiers:
    def __init__(self):
        self.width = 128
        self.height = 64
        self.line = 1 
        self.highlight = 1
        self.shift = 0
        self.list_length = 0
        self.total_lines = 6
        self.booleen_touche = 1
        self.bally=XglcdFont('fonts/Bally7x9.c', 7, 9)

    def afficher(self, début,fin):
        y = 0
        display.clear()
        for lignes in menu[début:fin:]:
            display.draw_text(0,y,lignes,bally,False)
            y += 10
    
    def launch(self, filename, folder):
        display.clear()
        display.draw_bitmap("images/" "polytech" ".mono", 0, 0, 128, 50, invert=False)
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
            
        display.present()
        chip8 = Emulator()
        chip8.readProg(root+folder+"/"+filename)
        chip8.mainLoop()
    
    def changement_ligne(self,x,y,menu,i):
        display.fill_rectangle(x,y, 127, 9, invert=False)
        display.draw_text(x,y,menu[i],self.bally,invert=True)
        display.present()


    def loop(self, folder, app):
        menu = []
        fichiers_jeux=[]
        if app == 1:
            # chip 8
            ext = "ch8"
        elif app == 2:
            # beatmaker
            ext = "mp7"
            menu.append("nouveau son")
            fichiers_jeux.append("nouveau fichier")
        elif app == 3:
            ext = "py"

            
        for file in uos.listdir(root+folder):
            if file[-len(ext):]==ext:
                fichiers_jeux.append(file)
                if len(file)>21:
                    menu.append(file[:17:]+"..")
                else:
                    menu.append(file[:len(file)-len(ext)-1:])
        
        menu_sans_emplacements=[]
        for o in menu:
            menu_sans_emplacements.append(o)
        for i in range(200):
            menu.append(" ")


        delai = 500
        y = 0
        for lignes in menu[0:6:]:
            if lignes != " ":
                x = 0
                for char in lignes:
                    for i in range (7):
                        random = chr(randint(97,122))
                        display.draw_letter(int(x), y, random, self.bally)
                        display.present()
                        
                        display.fill_rectangle(int(x),y,7,9, invert = True)
                        display.present()
                        sleep_us(delai)
                    display.draw_letter(int(x), y, char, self.bally)
                    x += 6.5
                    display.present()
                delai = int(delai*0.70)
                y += 10

        x=0
        y=0
        i=0
        début=0
        fin=6
        
        execution = 1
        booleen_touche = 1
        while execution:
            if y>=60:
                i=i-6
                y=0
                display.fill_rectangle(0,50, 127, 9, invert=True)
                display.draw_text(0,50,menu[i+5],self.bally,invert=False)
                display.present()
            elif menu[i]==" ":
                x=0
                display.fill_rectangle(0,50, 127, 9, invert=True)
                display.draw_text(0,50,menu[i],self.bally,invert=False)
                display.present()
                i=début
                y=0
            self.changement_ligne(x,y,menu,i)
            
            touche = lecture_touche()
            if touche == None:
                booleen_touche = 1
            
            elif (touche == "home" or touche == "B") and booleen_touche == 1:
                execution = 0
            
            elif touche=="A" and booleen_touche == 1:
                if app == 1:
                    self.launch(fichiers_jeux[i], folder)
                elif app == 2:
                    beatmaker = BeatMaker()
                    if fichiers_jeux[i] != "nouveau fichier":
                        beatmaker.read(root+folder+"/"+fichiers_jeux[i])
                    beatmaker.mainloop()
                
                display.clear()
                display.present()
                delai = 500
                y = 0
                for lignes in menu[0:6:]:
                    if lignes != " ":
                        x = 0
                        for char in lignes:
                            for i in range (7):
                                random = chr(randint(97,122))
                                display.draw_letter(int(x), y, random, self.bally)
                                display.present()
                                
                                display.fill_rectangle(int(x),y,7,9, invert = True)
                                display.present()
                                sleep_us(delai)
                            display.draw_letter(int(x), y, char, self.bally)
                            x += 6.5
                            display.present()
                        delai = int(delai*0.70)
                        y += 10

                x=0
                y=0
                i=0
                début=0
                fin=6
                booleen_touche = 0
                
            elif touche=="haut" and y==0 and booleen_touche == 1:
                i=i+5    
                y=50
                display.fill_rectangle(0,0, 127, 9, invert=True)
                display.draw_text(0,0,menu[i-5],self.bally,invert=False)
                display.present()
                booleen_touche = 0
            elif touche=="haut" and y!=0 and booleen_touche == 1:
                y=y-10
                i=i-1
                display.fill_rectangle(0,y+10, 127, 9, invert=True)
                display.draw_text(0,y+10,menu[i+1],self.bally,invert=False)
                display.present()
                booleen_touche = 0
            elif lecture_touche()=="bas" and booleen_touche == 1:
                y=y+10
                i=i+1
                display.fill_rectangle(0,y-10, 127, 9, invert=True)
                display.draw_text(0,y-10,menu[i-1],self.bally,invert=False)
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
                


class Menu:
    def __init__(self):
        self.fichiers = Fichiers()
        self.choix = 1
        self.icons = ["engrenage", "C8", "musique", "PY"]
        self.texte = ["parametres", 28, "jeux CHIP-8", 25, "BeatMaker", 31, "fichiers python", 12]

    def petitRect(self,x_rect, y_rect, size_rect):
        display.fill_rectangle(x_rect,y_rect,size_rect,size_rect, invert=False)
        display.fill_rectangle(x_rect+2,y_rect+2,size_rect-4,size_rect-4, invert=True)
        display.draw_pixel(x_rect, y_rect, invert=True)
        display.draw_pixel(size_rect+x_rect-1, y_rect, invert=True)
        display.draw_pixel(x_rect, size_rect+y_rect-1, invert=True)
        display.draw_pixel(size_rect+x_rect-1, size_rect+y_rect-1, invert=True)
        if size_rect >= 8:
            display.draw_pixel(x_rect+2, y_rect+2, invert=False)
            display.draw_pixel(size_rect+x_rect-3, y_rect+2, invert=False)
            display.draw_pixel(x_rect+2, y_rect+size_rect-3, invert=False)
            display.draw_pixel(size_rect+x_rect-3, y_rect+size_rect-3, invert=False)
        display.fill_circle((size_rect)//2+x_rect, (size_rect)//2+y_rect, size_rect//4, invert=False)

    def loadChoix(self,choix, droite):
        x_rect = 3
        y_rect = 12
        size_rect = 21
        x_rect2 = 100
        x_rect_milieu = 41
        y_rect_milieu = 1
        size_rect_milieu = 42
        
        display.clear()
        self.petitRect(x_rect_milieu, y_rect_milieu, size_rect_milieu)
        display.present()
        if droite:
            for i in range(20):
                display.fill_rectangle(x_rect+2*i-2,y_rect-(i-1)//2,size_rect+i-1,size_rect+i-1, invert=True) # efface rectangle gauche
                display.fill_rectangle(x_rect_milieu+3*i-3,y_rect_milieu+(i-1)//2,size_rect_milieu-i+3,size_rect_milieu-i+1, invert=True) # efface rectangle milieu
                display.fill_rectangle(x_rect2,y_rect,size_rect-i+1,size_rect-i//2+1, invert=True) # efface rectangle droite
                
                self.petitRect(x_rect, y_rect+(size_rect-i)//2-1, i+2) # nouveau rectangle à gauche
                self.petitRect(x_rect+2*i, y_rect-i//2, size_rect+i) # rectangle à gauche
                self.petitRect(x_rect_milieu+3*i, y_rect_milieu+i//2+2, size_rect_milieu-i-2) # rectangle du milieu
                if i != 19:
                    self.petitRect(x_rect2, y_rect+i//2, size_rect-i) # rectangle à droite
                display.present()
        
        else:
            for i in range(20):
                display.fill_rectangle(x_rect+i-1,y_rect+(i-1)//2,size_rect-i+1,size_rect-i+1, invert=True) # efface rectangle gauche
                display.fill_rectangle(x_rect_milieu-2*i+3,y_rect_milieu+(i-1)//2,size_rect_milieu-i+3,size_rect_milieu-i+1, invert=True) # efface rectangle milieu
                display.fill_rectangle(x_rect2-3*i+3,y_rect-(i+1)//2,size_rect+i+1,size_rect+i+1, invert=True) # efface rectangle droite
                
                self.petitRect(x_rect2, y_rect+(size_rect-i)//2-1, i+2) # nouveau rectangle à droite
                self.petitRect(x_rect2-3*i, y_rect-i//2, size_rect+i) # rectangle à droite
                if i != 19:
                    self.petitRect(x_rect+i, y_rect+i//2, size_rect-i) # rectangle à gauche
                self.petitRect(x_rect_milieu-2*i, y_rect_milieu+i//2+2, size_rect_milieu-i-2) # rectangle du milieu
                display.present()

        
        display.draw_text(self.texte[2*self.choix+1], 50, self.texte[2*self.choix], bally)
        display.draw_bitmap("images/" + self.icons[self.choix] + ".mono", 41, 2, 42, 42, invert=False)
        display.present()
        
        
    def DrawTriangles(self, size_triangle, inversion):
        x_triangle = 31
        x_triangle_2 = 122-x_triangle
        y_triangle = 23
        
        display.draw_line(x_triangle-size_triangle//2, y_triangle, x_triangle+size_triangle//2, y_triangle-size_triangle, invert=inversion)
        display.draw_line(x_triangle-size_triangle//2, y_triangle, x_triangle+size_triangle//2, y_triangle+size_triangle, invert=inversion)
        display.draw_line(x_triangle+size_triangle//2, y_triangle-size_triangle, x_triangle+size_triangle//2, y_triangle+size_triangle, invert=inversion)
        
        display.draw_line(x_triangle_2-size_triangle//2, y_triangle+size_triangle, x_triangle_2+size_triangle//2, y_triangle, invert=inversion)
        display.draw_line(x_triangle_2-size_triangle//2, y_triangle-size_triangle, x_triangle_2+size_triangle//2, y_triangle, invert=inversion)
        display.draw_line(x_triangle_2-size_triangle//2, y_triangle-size_triangle, x_triangle_2-size_triangle//2, y_triangle+size_triangle, invert=inversion)
        
        
    
    def loop(self):
        lastime = ticks_ms()
        x_rect = 3
        y_rect = 13
        size_triangle = 8
        size_rect = 21
        self.petitRect(x_rect, y_rect, size_rect)
        x_rect2 = 100
        self.petitRect(x_rect2, y_rect, size_rect)
        display.draw_text(self.texte[2*self.choix+1], 50, self.texte[2*self.choix], bally)
        display.draw_bitmap("images/" + self.icons[self.choix] + ".mono", 41, 2, 42, 42, invert=False)
        self.DrawTriangles(size_triangle, 0)
        display.present()
        bool_bouton = 1
        bool_triangle = 1

        while True:
            if ticks_ms() - lastime >= 140:
                lastime = ticks_ms()
                self.DrawTriangles(size_triangle, 1)
                
                if bool_triangle == 1:
                    if size_triangle != 4:
                        size_triangle -= 2
                    else:
                        size_triangle = 2
                        bool_triangle = 0
                else:
                    if size_triangle != 6:
                        size_triangle += 2
                    else:
                        size_triangle = 8
                        bool_triangle = 1
                    
                self.DrawTriangles(size_triangle, 0)
                display.present()
            
            touche = lecture_touche()
            if touche == "gauche" and bool_bouton == 0:
                bool_bouton = 1
                if self.choix <= 2:
                    self.choix += 1
                else:
                    self.choix = 0
                self.DrawTriangles(size_triangle, 1)
                self.loadChoix(self.choix, 1)
                    
            elif touche == "droite" and bool_bouton == 0:
                bool_bouton = 1
                if self.choix >= 1:
                    self.choix -= 1
                else:
                    self.choix = 3
                self.DrawTriangles(size_triangle, 1)
                self.loadChoix(self.choix, 0)
                
            elif touche == "A" and bool_bouton == 0:
                bool_bouton = 1
                display.clear()
                display.present()
                # 0 : paramètres
                # 1 : CHIP-8
                # 2 : BeatMaker
                # 3 : Python
                
                if self.choix == 0:
                    self.settings()
                elif self.choix == 1:
                    self.fichiers.loop("games",self.choix)
                elif self.choix == 2:
                    self.fichiers.loop("music",self.choix)
                elif self.choix == 3:
                    self.fichiers.loop("python",self.choix)
                
                
                display.clear()
                x_rect = 3
                y_rect = 13
                size_rect = 21
                self.petitRect(x_rect, y_rect, size_rect)
                x_rect2 = 100
                self.petitRect(x_rect2, y_rect, size_rect)
                display.draw_text(self.texte[2*self.choix+1], 50, self.texte[2*self.choix], bally)
                display.draw_bitmap("images/" + self.icons[self.choix] + ".mono", 41, 2, 42, 42, invert=False)
                self.DrawTriangles(size_triangle, 0)
                display.present()
            
            elif touche == None:
                bool_bouton = 0

    def settings(self):
        display.clear()
        bool_touche = 1
        display.draw_rectangle(0, 0, 127, 63, invert=False)
        display.fill_rectangle(26, 14, 70, 11, invert=False)
        display.draw_rectangle(10, 14, 11, 11, invert=False)
        display.draw_line(12, 16, 18, 22)
        display.draw_line(12, 22, 18, 16)
        display.draw_text(27, 15, "animations", bally, invert=True)
        display.draw_text(27, 35, "retour", bally, invert=False)
        display.present()
        choix = 0
        echap = True
        animation = 1
        
        while echap:
            touche = lecture_touche()
            if touche == None:
                bool_touche = 0
            
            elif touche == "bas" and bool_touche == 0:
                bool_touche = 1
                if choix == 0:
                    choix = 1
                    display.fill_rectangle(26, 11, 70, 41, invert=True)
                    display.draw_text(27, 15, "animations", bally, invert=False)
                    display.fill_rectangle(26, 34, 70, 11, invert=False)
                    display.draw_text(27, 35, "retour", bally, invert=True)
                    display.present()
                    
            elif touche == "haut" and bool_touche == 0:
                bool_touche = 1
                if choix == 1:
                    choix = 0
                    display.fill_rectangle(26, 11, 70, 41, invert=True)
                    display.fill_rectangle(26, 14, 70, 11, invert=False)
                    display.draw_text(27, 15, "animations", bally, invert=True)
                    display.draw_text(27, 35, "retour", bally, invert=False)
                    display.present()
                
            elif touche == "A" and bool_touche == 0:
                bool_touche = 1
                if choix == 1:
                    echap = 0
                else:
                    animation = not(animation)
                    if animation:
                        display.draw_line(12, 16, 18, 22)
                        display.draw_line(12, 22, 18, 16)
                        display.present()
                    else:
                        display.fill_rectangle(11, 15, 9, 9, invert=True)
                        display.present()
                
                with open(root+"/settings.cfg", 'w') as s:
                    s.write("animation:" + str(animation))
                sleep(0.1)
            
                
            elif (touche == "home" or touche =="B") and bool_touche == 0:
                echap = 0


test=XglcdFont('fonts/Unispace12x24.c', 12, 24)
Wendy = XglcdFont('fonts/Wendy7x8.c', 7, 8)

display.fill_rectangle(0,0, 128, 64, invert=False)
delai = 1000
y=10
x = 10
for char in "GAMECHEAP":
    for i in range (7):
        random = chr(randint(97,122))
        display.draw_letter(x, y, random, test,invert=True)
        display.present()
            
        display.fill_rectangle(x,y,12,24, invert=False)
        display.present()
        sleep_us(delai)
    display.draw_letter(x, y, char, test,invert=True)
    x += 12
    display.present()
delai = int(delai*0.70)
sleep(0.3)
y=55
x = 15
for char in "Polytech inc.":
    for i in range (7):
        random = chr(randint(97,122))
        display.draw_letter(x, y, random, Wendy,invert=True)
        display.present()
            
        display.fill_rectangle(x,y,7,8, invert=False)
        display.present()
        sleep_us(delai)
    display.draw_letter(x, y, char, Wendy,invert=True)
    x += 8
    display.present()
delai = int(delai*0.70)

Robotron = XglcdFont('fonts/Robotron7x11.c', 7, 11)

main_menu = Menu()

display.clear()
display.fill_rectangle(0,0, 128, 64, invert=True)
display.draw_text(10,10,"GAMECHEAP",test)
display.present()
sleep(0.3)


delai = 1000
y=50
x = 20
for char in "Press start":
    for i in range (7):
        random = chr(randint(97,122))
        display.draw_letter(x, y, random, Robotron)
        display.present()
            
        display.fill_rectangle(x,y,7,11, invert = True)
        display.present()
        sleep_us(delai)
    display.draw_letter(x, y, char, Robotron)
    x += 8
    display.present()
delai = int(delai*0.70)
display.present()

def prettyText():
    # "press start" qui bouge
    while lecture_touche()!="start":
        y = 50
        x = 20
        mot = "press start"
        for i in range(0, len(mot)):
            if i >= 1:
                display.fill_rectangle(x-8,y,7,11, invert = True)
                display.draw_letter(x-8, y-1, mot[i-1], Robotron)
            
            if i <= len(mot)-2:
                display.fill_rectangle(x+8,y,7,11, invert = True)
                display.draw_letter(x+8, y-1, mot[i+1], Robotron)
            
            display.fill_rectangle(x,y,7,11, invert = True)
            display.draw_letter(x, y-2, mot[i], Robotron)
            display.present()
            
            lastime = ticks_ms()
            while ticks_ms() - lastime <= 70:
                if lecture_touche() == "start":
                    return 1
                
            display.fill_rectangle(x,y-2,7,11, invert = True)
            if i == len(mot)-1:
                display.draw_letter(x, y, mot[i], Robotron)
            else:
                display.draw_letter(x, y-1, mot[i], Robotron)
            
            if i >= 1:
                display.fill_rectangle(x-8,y-1,7,11, invert = True)
                display.draw_letter(x-8, y, mot[i-1], Robotron)
            
            if i <= len(mot)-2:
                display.fill_rectangle(x+8,y-1,7,11, invert = True)
                display.draw_letter(x+8, y, mot[i+1], Robotron)
                
            display.present()
            x += 8
        sleep(0.15)
    return 1

prettyText()
display.clear()
sleep(0.1)

main_menu.loop()