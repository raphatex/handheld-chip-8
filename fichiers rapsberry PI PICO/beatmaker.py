from machine import Pin, PWM, SPI
from time import sleep
from ssd1309 import Display
from xglcd_font import XglcdFont
from buttons import lecture_touche
import pinout

spi_display = SPI(pinout.SPI_ID, baudrate=10000000, sck=pinout.PIN_D0, mosi=pinout.PIN_D1)
display = Display(spi_display, dc=pinout.PIN_A0, cs=pinout.PIN_CS, rst=pinout.PIN_RST)

buzzer = PWM(pinout.PIN_BUZZ)

if pinout.SD_READER:
    root = "/sd/"
    
else:
    root = ""

class BeatMaker:
    def __init__(self):
        self.bally = XglcdFont('fonts/Bally7x9.c', 7, 9)
        
        self.vitesse = 9
        self.liste_note = [110, 116, 123, 131, 139, 147, 155, 165, 175, 185, 196, 208, 220, 233, 247, 262, 277, 294, 311, 330, 349, 370, 392, 415, 440, 466, 494, 523, 554, 587, 622, 659]

        self.x = 10
        self.y = 30

        self.map = []
        for i in range(32):
            line = []
            for j in range(60):
                line.append(0)
            self.map.append(line)

        display.fill_rectangle(self.x, self.y, 2, 2, invert=False)
        display.draw_hline(8, self.y, self.x-9)
        display.present()
        
        
    def play_notes(self, note_to_play):
        i = len(note_to_play)-1
        while note_to_play[i] == None:
            note_to_play.pop(i)
            i -= 1
        
        bool_touche = 1
        loop = True
        while loop:
            x_ligne = 8
            display.fill_rectangle(x_ligne, 0, 1, 63, invert=False)
            display.present()
            
            for note in note_to_play:
                touche = lecture_touche()
                if touche == None:
                    bool_touche = 0
                elif touche == "start" and bool_touche == 0:
                    loop = False
                    break
                
                display.fill_rectangle(x_ligne, 0, 1, 63, invert=True)
                x_ligne += 2
                display.fill_rectangle(x_ligne, 0, 1, 63, invert=False)
                display.present()
                if note != None:
                    buzzer.freq(note)
                    buzzer.duty_u16(1000)
                    sleep(1/self.vitesse)
                    buzzer.duty_u16(0)
                else:
                    sleep(1/self.vitesse)
            display.fill_rectangle(x_ligne, 0, 1, 63, invert=True)

    def initScreen(self):
        liste = [0,1,0,0,1,0,1,0,0,1,0,1,0,1,0,0,1,0,1,0,0,1,0,1,0,1,0,0,1,0,1,0]        
        display.fill_rectangle(0, 0, 8, 63, invert=False)
        y = 0
        for i in liste:
            if i == 1:
                display.fill_rectangle(3, y, 4, 2, invert=True)
            y += 2
        display.present()


    def reload_screen(self):
        display.fill_rectangle(9, 0, 120, 63, invert=False)
        for i in range(60):
            for j in range(32):
                display.fill_rectangle(2*i+8, 2*j, 2, 2, invert=not(self.map[j][i]))
        display.draw_hline(8, self.y, self.x-9)
        display.fill_rectangle(self.x, self.y, 2, 2, invert=False)
        display.present()

    def read(self, path):
        i = 0
        j = 0
        with open(path, 'rb') as f:
            wholeSong = f.read()
            for note in wholeSong:
                self.map[j][i] = note
                i += 1
                if i == 60:
                    i = 0
                    j += 1
                    
    def save(self):
        display.clear()
        x = 3
        y = 16
        n = 0
        display.draw_text(0, 0, "Choisir emplacement", self.bally, invert=False)
        for i in range(5):
            display.draw_rectangle(x, y, 20, 20, invert=False)
            display.draw_letter(x+6, y+5, str(n), self.bally)
            x += 25
            n += 1
        y += 25
        x = 3
        
        for i in range(5):
            display.draw_rectangle(x, y, 20, 20, invert=False)
            display.draw_letter(x+6, y+5, str(n), self.bally)
            x += 25
            n += 1
            
        n = 0
        x = 3
        y = 16
        display.fill_rectangle(x, y, 20, 20, invert=False)
        display.draw_letter(x+6, y+5, str(n), self.bally, invert=True)
        display.present()
        
        bool_touche = 1
        execution = 1
        while execution:
            touche = lecture_touche()
            
            if touche == None:
                bool_touche = 0
                
            elif touche == "haut" and bool_touche == 0 and n >= 5:
                display.fill_rectangle(x, y, 20, 20, invert=True)
                display.draw_rectangle(x, y, 20, 20, invert=False)
                display.draw_letter(x+6, y+5, str(n), self.bally)
                
                y -= 25
                n -= 5
                display.fill_rectangle(x, y, 20, 20, invert=False)
                display.draw_letter(x+6, y+5, str(n), self.bally, invert=True)
                display.present()
                
                bool_touche = 1
                
            elif touche == "bas" and bool_touche == 0 and n <= 4:
                display.fill_rectangle(x, y, 20, 20, invert=True)
                display.draw_rectangle(x, y, 20, 20, invert=False)
                display.draw_letter(x+6, y+5, str(n), self.bally)
                
                y += 25
                n += 5
                display.fill_rectangle(x, y, 20, 20, invert=False)
                display.draw_letter(x+6, y+5, str(n), self.bally, invert=True)
                display.present()
                
                bool_touche = 1
                
            elif touche == "gauche" and bool_touche == 0 and n != 0 and n != 5:
                display.fill_rectangle(x, y, 20, 20, invert=True)
                display.draw_rectangle(x, y, 20, 20, invert=False)
                display.draw_letter(x+6, y+5, str(n), self.bally)
                
                x -= 25
                n -= 1
                display.fill_rectangle(x, y, 20, 20, invert=False)
                display.draw_letter(x+6, y+5, str(n), self.bally, invert=True)
                display.present()
                
                bool_touche = 1
                
            elif touche == "droite" and bool_touche == 0 and n != 4 and n != 9:
                display.fill_rectangle(x, y, 20, 20, invert=True)
                display.draw_rectangle(x, y, 20, 20, invert=False)
                display.draw_letter(x+6, y+5, str(n), self.bally)
                
                x += 25
                n += 1
                display.fill_rectangle(x, y, 20, 20, invert=False)
                display.draw_letter(x+6, y+5, str(n), self.bally, invert=True)
                display.present()
                
                bool_touche = 1
            
            elif touche == "A" and bool_touche == 0:
                execution = 0
        
        
        with open(root+"/music/son "+str(n)+".mp7", 'w') as s:
            for i in range(len(self.map)):
                s.write(bytearray(self.map[i]))

    def mainloop(self):
        self.initScreen()
        self.reload_screen()
        bool_touche = 1
        execution = 1

        while execution:
            touche = lecture_touche()
            
            if touche == "home" and bool_touche == 0:
                execution = 0
                with open(root+"/music/autosave.mp7", 'w') as s:
                    for i in range(len(self.map)):
                        s.write(bytearray(self.map[i]))
            
            if touche == "gauche" and bool_touche == 0:
                bool_touche = 1
                if self.x >= 10:
                    display.draw_hline(self.x-3, self.y, 2, invert=True)
                    display.fill_rectangle(self.x, self.y, 2, 2, invert=not(self.map[(self.y//2)][(self.x-8)//2]))
                    self.x -= 2
                    display.fill_rectangle(self.x, self.y, 2, 2, invert=False)
                    sleep(0.2)
                
            elif touche == "droite" and bool_touche == 0:
                bool_touche = 1
                if self.x <= 125:
                    display.fill_rectangle(self.x, self.y, 2, 2, invert=not(self.map[(self.y//2)][(self.x-8)//2]))
                    self.x += 2
                    display.draw_hline(self.x-3, self.y, 2)
                    display.fill_rectangle(self.x, self.y, 2, 2, invert=False)
                    sleep(0.2)
                
            elif touche == "bas" and bool_touche == 0:
                bool_touche = 1
                if self.y <= 61:
                    display.draw_hline(8, self.y, self.x-9, invert = True)
                    display.fill_rectangle(self.x, self.y, 2, 2, invert=not(self.map[(self.y//2)][(self.x-8)//2]))
                    j = self.y//2
                    for i in range(60):
                        if self.map[j][i] == 1:
                            display.draw_hline(8+i*2, self.y, 2)
                    self.y += 2
                    display.draw_hline(8, self.y, self.x-9)
                    display.fill_rectangle(self.x, self.y, 2, 2, invert=False)
                    sleep(0.2)
                
            elif touche == "haut" and bool_touche == 0:
                bool_touche = 1
                if self.y >= 2:
                    display.draw_hline(8, self.y, self.x-9, invert = True)
                    display.fill_rectangle(self.x, self.y, 2, 2, invert=not(self.map[(self.y//2)][(self.x-8)//2]))
                    j = self.y//2
                    for i in range(60):
                        if self.map[j][i] == 1:
                            display.draw_hline(8+i*2, self.y, 2)
                    self.y -= 2
                    display.draw_hline(8, self.y, self.x-9)
                    display.fill_rectangle(self.x, self.y, 2, 2, invert=False)
                    sleep(0.2)
                    
            elif touche == "A" and bool_touche == 0:
                bool_touche = 1
                self.map[(self.y//2)][(self.x-8)//2] = not(self.map[(self.y//2)][(self.x-8)//2])
                
                
            elif touche == "B" and bool_touche == 0:
                bool_touche = 1
                display.fill_rectangle(14, 10, 107, 43, invert=True)
                display.draw_rectangle(14, 10, 107, 43, invert=False)
                display.fill_rectangle(26, 14, 80, 11, invert=False)
                display.draw_text(27, 15, "vitesse", self.bally, invert=True)
                display.draw_text(84, 15, str(self.vitesse), self.bally, invert=True)
                display.draw_text(27, 35, "Sauvegarder", self.bally, invert=False)
                display.present()
                choix = 0
                echap = True
                sleep(0.2)
                
                while echap:
                    touche = lecture_touche()
                    if touche == None:
                        bool_touche = 0
                    elif touche == "B" and bool_touche == 0:
                        echap = 0
                    
                    elif touche == "bas" and bool_touche == 0:
                        bool_touche = 1
                        if choix == 0:
                            choix = 1
                            display.fill_rectangle(15, 11, 105, 41, invert=True)
                            display.draw_text(27, 15, "vitesse", self.bally, invert=False)
                            display.draw_text(84, 15, str(self.vitesse), self.bally, invert=False)
                            display.fill_rectangle(26, 34, 80, 11, invert=False)
                            display.draw_text(27, 35, "Sauvegarder", self.bally, invert=True)
                            display.present()
                            
                    elif touche == "haut" and bool_touche == 0:
                        bool_touche = 1
                        if choix == 1:
                            choix = 0
                            display.fill_rectangle(15, 11, 105, 41, invert=True)
                            display.fill_rectangle(26, 14, 80, 11, invert=False)
                            display.draw_text(27, 15, "vitesse", self.bally, invert=True)
                            display.draw_text(84, 15, str(self.vitesse), self.bally, invert=True)
                            display.draw_text(27, 35, "Sauvegarder", self.bally, invert=False)
                            display.present()
                        
                    elif touche == "A" and bool_touche == 0 and choix == 1:
                        self.save()
                        self.initScreen()
                        echap = 0
                        
                    elif touche == "droite" and bool_touche == 0 and choix == 0:
                        bool_touche = 1
                        self.vitesse += 1
                        display.fill_rectangle(26, 14, 80, 11, invert=False)
                        display.draw_text(27, 15, "vitesse", self.bally, invert=True)
                        display.draw_text(84, 15, str(self.vitesse), self.bally, invert=True)
                        display.present()
                        
                    elif touche == "gauche" and bool_touche == 0 and choix == 0:
                        bool_touche = 1
                        if self.vitesse >= 2:
                            self.vitesse -= 1
                            display.fill_rectangle(26, 14, 80, 11, invert=False)
                            display.draw_text(27, 15, "vitesse", self.bally, invert=True)
                            display.draw_text(84, 15, str(self.vitesse), self.bally, invert=True)
                            display.present()
                    
                self.reload_screen()
            
            elif touche == "start" and bool_touche == 0:
                # lancer la lecture de la musique
                bool_touche = 1
                note_to_play = []
                for i in range (60):
                    note = 0
                    for j in range(32):
                        if self.map[j][i] == 1:
                            note_to_play.append(self.liste_note[j])
                            note = 1
                            break
                    if note == 0:
                        note_to_play.append(None)
                        
                display.fill_rectangle(self.x, self.y, 2, 2, invert=False)
                self.play_notes(note_to_play)
                self.reload_screen()
            
            elif touche == None:
                bool_touche = 0

            display.present()

