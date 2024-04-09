##################################################################
#                                                                #
# ---------------- émulateur CHIP-8 MicroPython ---------------- #
# ------------------------ par Raphatex ------------------------ #
#                                                                #
##################################################################
#                                                                #
# ---------- basé sur l'émulateur Pygame de AlpacaMax ---------- #
# https://github.com/AlpacaMax/Python-CHIP8-Emulator/tree/master #
#                                                                #
# modifications:                                                 #
# - adaptation pour Raspberry pi PICO                            #
# - adaptation à un écran 128*64 ssd1309                         #
# - ajout du son à partir d'un buzzer                            #
# - ajout d'une fonction de sauvegarde de l'état du jeu          #
# - possibilité de configurer les touches pour chaque jeu        #
# - possibilité de mettre pause                                  #
#                                                                #
##################################################################

import random
from utime import ticks_ms, ticks_us
from machine import Pin, SPI, PWM
from ssd1309 import Display
from xglcd_font import XglcdFont
from buttons import lecture_touche
import sys
import pinout
from time import sleep

if pinout.SD_READER:
    root = "/sd/"
else:
    root = ""

buzzer = PWM(pinout.PIN_BUZZ)
buzzer.freq(500)

liste_bouton = [0,0,0,0,0,0]

#pin_gauche = Pin(9, mode=Pin.IN, pull=Pin.PULL_UP)
#pin_droite = Pin(5, mode=Pin.IN, pull=Pin.PULL_UP)
#pin_bas = Pin(4, mode=Pin.IN, pull=Pin.PULL_UP)
#pin_haut = Pin(12, mode=Pin.IN, pull=Pin.PULL_UP)
#pin_A = Pin(14, mode=Pin.IN, pull=Pin.PULL_UP)
#pin_B = Pin(15, mode=Pin.IN, pull=Pin.PULL_UP)

def A_isr(pin):
    global liste_bouton
    liste_bouton[4]=1

def B_isr(pin):
    global liste_bouton
    liste_bouton[5]=1

def haut_isr(pin):
    global liste_bouton
    liste_bouton[3]=1

def droite_isr(pin):
    global liste_bouton
    liste_bouton[2]=1

def bas_isr(pin):
    global liste_bouton
    liste_bouton[1]=1

def gauche_isr(pin):
    global liste_bouton
    liste_bouton[0]=1
  
#pin_gauche.irq(trigger=Pin.IRQ_FALLING,handler=gauche_isr)
#pin_droite.irq(trigger=Pin.IRQ_FALLING,handler=droite_isr)
#pin_haut.irq(trigger=Pin.IRQ_FALLING,handler=haut_isr)
#pin_bas.irq(trigger=Pin.IRQ_FALLING,handler=bas_isr)
#pin_A.irq(trigger=Pin.IRQ_FALLING,handler=A_isr)
#pin_B.irq(trigger=Pin.IRQ_FALLING,handler=B_isr)

spi_display = SPI(pinout.SPI_ID, baudrate=10000000, sck=pinout.PIN_D0, mosi=pinout.PIN_D1)
display = Display(spi_display, dc=pinout.PIN_A0, cs=pinout.PIN_CS, rst=pinout.PIN_RST)

class Register:
    def __init__(self, bits):
        self.value = 0
        self.bits = bits

    def checkCarry(self):
        hexValue = hex(self.value)[2:]

        if len(hexValue) > self.bits / 4:
            self.value = int(hexValue[-int(self.bits / 4):], 16)
            return 1
        
        return 0
    
    def checkBorrow(self):
        if self.value < 0:
            self.value = abs(self.value)
            return 0
        
        return 1
    
    def readValue(self):
        return hex(self.value)
    
    def readSave(self):
        return self.value
    
    def setValue(self, value):
        self.value = value

class DelayTimer:
    def __init__(self):
        self.timer = 0
    
    def countDown(self):
        if self.timer > 0:
            self.timer -= 1

    def setTimer(self, value):
        self.timer = value
    
    def readTimer(self):
        return self.timer

class SoundTimer(DelayTimer):
    def __init__(self):
        DelayTimer.__init__(self)

    def beep(self):
        if self.timer > 1:
            buzzer.duty_u16(1000)
        else :
            buzzer.duty_u16(0)

class Stack:
    def __init__(self):
        self.stack = []
    
    def push(self, value):
        self.stack.append(value)
    
    def pop(self):
        return self.stack.pop()
    
    def get(self):
        return self.stack

    def load(self, stack_save):
        self.stack = stack_save

class Emulator:
    def __init__(self):
        self.SOUND = 1
        try:
            with open(root+"/settings.cfg", 'r') as s:
                file = s.read()
        except:
            pass
        else:
            with open(root+"/settings.cfg", 'r') as s:
                file = s.read()
                print(file[18])
                if file[18] == '0':
                    self.SOUND = 0
        
        self.Memory = []
        for i in range(0, 4096):
            self.Memory.append(0x0)

        fonts = [ 
        0xF0, 0x90, 0x90, 0x90, 0xF0, # 0
        0x20, 0x60, 0x20, 0x20, 0x70, # 1
        0xF0, 0x10, 0xF0, 0x80, 0xF0, # 2
        0xF0, 0x10, 0xF0, 0x10, 0xF0, # 3
        0x90, 0x90, 0xF0, 0x10, 0x10, # 4
        0xF0, 0x80, 0xF0, 0x10, 0xF0, # 5
        0xF0, 0x80, 0xF0, 0x90, 0xF0, # 6
        0xF0, 0x10, 0x20, 0x40, 0x40, # 7
        0xF0, 0x90, 0xF0, 0x90, 0xF0, # 8
        0xF0, 0x90, 0xF0, 0x10, 0xF0, # 9
        0xF0, 0x90, 0xF0, 0x90, 0x90, # A
        0xE0, 0x90, 0xE0, 0x90, 0xE0, # B
        0xF0, 0x80, 0x80, 0x80, 0xF0, # C
        0xE0, 0x90, 0x90, 0x90, 0xE0, # D
        0xF0, 0x80, 0xF0, 0x80, 0xF0, # E
        0xF0, 0x80, 0xF0, 0x80, 0x80  # F
        ]
        for i in range(len(fonts)):
            self.Memory[i] = fonts[i]

        self.Registers = []
        for i in range(16):
            self.Registers.append(Register(8))
        
        self.IRegister = Register(16)
        self.ProgramCounter = 0x200

        self.stack = Stack()
        self.playing = 1
        self.pause = 0

        self.delayTimer = DelayTimer()
        self.soundTimer = SoundTimer()
        
        self.lastime = ticks_us()
        
        self.label_bouton = ["gauche","bas","droite","haut","A","B"]
        
        self.lastKey = 'A'
        self.keys = []
        for i in range(0, 16):
            self.keys.append(False)
        self.keyDict = {
            'haut' : 2,
            'gauche' : 4,
            'A' : 5,
            'droite' : 6,
            'bas' : 8,
            'B' : 0xf
        }

        self.grid = []
        for i in range(32):
            line = []
            for j in range(64):
                line.append(0)
            self.grid.append(line)

        self.size = 2
        width = 64
        height = 32
        
    def execOpcode(self, opcode):
        #print(opcode)

        if opcode[0] == '0':

            if opcode[1] != '0':
                #0NNN

                print("ROM attempts to run RCA 1802 program at <0x" + opcode[1:] + '>')

            else:
                if opcode == '00e0':
                    #00E0
                    #disp_clear()
                    
                    self.clear()

                elif opcode == '00ee':
                    #00EE
                    #return;
                    try:
                        self.ProgramCounter = self.stack.pop()
                    except:
                        self.playing = 0
                        print("stop playing")

        
        elif opcode[0] == '1':
            #1NNN
            #goto NNN;

            self.ProgramCounter = int(opcode[1:], 16) - 2
        
        elif opcode[0] == '2':
            #2NNN
            #*(0xNNN)()

            self.stack.push(self.ProgramCounter)
            self.ProgramCounter = int(opcode[1:], 16) - 2
        
        elif opcode[0] == '3':
            #3XNN
            #if(Vx==NN)

            vNum = int(opcode[1], 16)
            targetNum = int(opcode[2:], 16)

            if self.Registers[vNum].value == targetNum:
                self.ProgramCounter += 2

        elif opcode[0] == '4':
            #4XNN
            #if(Vx!=NN)

            vNum = int(opcode[1], 16)
            targetNum = int(opcode[2:], 16)

            if self.Registers[vNum].value != targetNum:
                self.ProgramCounter += 2

        elif opcode[0] == '5':
            #5XY0
            #if(Vx==Vy)

            v1 = int(opcode[1], 16)
            v2 = int(opcode[2], 16)

            if self.Registers[v1].value == self.Registers[v2].value:
                self.ProgramCounter += 2

        elif opcode[0] == '6':
            #6XNN
            #Vx = NN

            vNum = int(opcode[1], 16)
            targetNum = int(opcode[2:], 16)

            self.Registers[vNum].value = targetNum
        
        elif opcode[0] == '7':
            #7XNN
            #Vx += NN

            vNum = int(opcode[1], 16)
            targetNum = int(opcode[2:], 16)

            self.Registers[vNum].value += targetNum
            self.Registers[vNum].checkCarry()
        
        elif opcode[0] == '8':
            if opcode[3] == '0':
                #8XY0
                #Vx=Vy

                v1 = int(opcode[1], 16)
                v2 = int(opcode[2], 16)

                self.Registers[v1].value = self.Registers[v2].value
            
            elif opcode[3] == '1':
                #8XY1
                #Vx=Vx|Vy

                v1 = int(opcode[1], 16)
                v2 = int(opcode[2], 16)

                self.Registers[v1].value = self.Registers[v1].value | self.Registers[v2].value
            
            elif opcode[3] == '2':
                #8XY2
                #Vx=Vx&Vy

                v1 = int(opcode[1], 16)
                v2 = int(opcode[2], 16)

                self.Registers[v1].value = self.Registers[v1].value & self.Registers[v2].value
            
            elif opcode[3] == '3':
                #8XY3
                #Vx=Vx^Vy

                v1 = int(opcode[1], 16)
                v2 = int(opcode[2], 16)

                self.Registers[v1].value = self.Registers[v1].value ^ self.Registers[v2].value
            
            elif opcode[3] == '4':
                #8XY4
                #Vx += Vy

                v1 = int(opcode[1], 16)
                v2 = int(opcode[2], 16)

                self.Registers[v1].value += self.Registers[v2].value

                self.Registers[0xf].value = self.Registers[v1].checkCarry()
            
            elif opcode[3] == '5':
                #8XY5
                #Vx -= Vy

                v1 = int(opcode[1], 16)
                v2 = int(opcode[2], 16)

                self.Registers[v1].value -= self.Registers[v2].value

                self.Registers[0xf].value = self.Registers[v1].checkBorrow()
            
            elif opcode[3] == '6':
                #8XY6
                #Vx>>1

                v1 = int(opcode[1], 16)
                leastBit = int(bin(self.Registers[v1].value)[-1])

                self.Registers[v1].value = self.Registers[v1].value >> 1
                self.Registers[0xf].value = leastBit
            
            elif opcode[3] == '7':
                #8XY7
                #Vx=Vy-Vx

                v1 = int(opcode[1], 16)
                v2 = int(opcode[2], 16)

                self.Registers[v1].value = self.Registers[v2].value - self.Registers[v1].value
                self.Registers[0xf].value = self.Registers[v1].checkBorrow()
            
            elif opcode[3] == 'e':
                #8XYE
                #Vx<<=1

                v1 = int(opcode[1], 16)
                mostBit = int(bin(self.Registers[v1].value)[2])

                self.Registers[v1].value = self.Registers[v1].value << 1
                self.Registers[0xf].value = mostBit
        
        elif opcode[0] == '9':
            #9XY0
            #if(Vx!=Vy)

            v1 = int(opcode[1], 16)
            v2 = int(opcode[2], 16)

            if self.Registers[v1].value != self.Registers[v2].value:
                self.ProgramCounter += 2
        
        elif opcode[0] == 'a':
            #ANNN
            #I = NNN

            addr = int(opcode[1:], 16)

            self.IRegister.value = addr
        
        elif opcode[0] == 'b':
            #BNNN
            #PC=V0+NNN

            addr = int(opcode[1:], 16)

            self.ProgramCounter = self.Registers[0].value + addr - 2
        
        elif opcode[0] == 'c':
            #CXNN
            #Vx=rand()&NN

            vNum = int(opcode[1], 16)
            targetNum = int(opcode[2:], 16)

            rand = random.randint(0, 255)

            self.Registers[vNum].value = targetNum & rand
        
        elif opcode[0] == 'd':
            #DXYN
            #draw(Vx,Vy,N)
            
            Vx = int(opcode[1], 16)
            Vy = int(opcode[2], 16)
            N  = int(opcode[3], 16)

            addr = self.IRegister.value
            sprite = self.Memory[addr: addr + N]

            for i in range(len(sprite)):
                if type(sprite[i]) == str:
                     sprite[i] = int(sprite[i], 16)

            if self.draw(self.Registers[Vx].value, self.Registers[Vy].value, sprite):
                self.Registers[0xf].value = 1
            else:
                self.Registers[0xf].value = 0
        
        elif opcode[0] == 'e':
            if opcode[2:] == '9e':
                #EX9E
                #if(key()==Vx)

                Vx = int(opcode[1], 16)
                key = self.Registers[Vx].value
                if self.keys[key]:
                    self.ProgramCounter += 2

            elif opcode[2:] == 'a1':
                #EXA1
                #if(key()!=Vx)

                Vx = int(opcode[1], 16)
                key = self.Registers[Vx].value
                if not self.keys[key]:
                    self.ProgramCounter += 2
        
        elif opcode[0] == 'f':
            if opcode[2:] == '07':
                #FX07
                #delay_timer(Vx)

                Vx = int(opcode[1], 16)
                self.Registers[Vx].value = self.delayTimer.readTimer()

            elif opcode[2:] == '0a':
                #FX0A
                #Vx = get_key()

                Vx = int(opcode[1], 16)
                key = None

                while True:
                    self.keyHandler()
                    isKeyDown = False

                    for i in range(len(self.keys)):
                        if self.keys[i]:
                            key = i
                            isKeyDown = True
                    
                    if isKeyDown:
                        break
                
                self.Registers[Vx].value = key
            
            elif opcode[2:] == '15':
                #FX15
                #delay_timer(Vx)

                Vx = int(opcode[1], 16)
                value = self.Registers[Vx].value

                self.delayTimer.setTimer(value)
            
            elif opcode[2:] == '18':
                #FX18
                #sound_timer(Vx)

                Vx = int(opcode[1], 16)
                value = self.Registers[Vx].value

                self.soundTimer.setTimer(value)
            
            elif opcode[2:] == '1e':
                #FX1E
                #I += Vx

                Vx = int(opcode[1], 16)
                self.IRegister.value += self.Registers[Vx].value
            
            elif opcode[2:] == '29':
                #FX29
                #I = sprite_addr[Vx]

                Vx = int(opcode[1], 16)
                value = self.Registers[Vx].value

                self.IRegister.value = value * 5
            
            elif opcode[2:] == '33':
                #FX33
                '''
                set_BCD(Vx);
                *(I+0)=BCD(3);
                *(I+1)=BCD(2);
                *(I+2)=BCD(1);
                '''

                Vx = int(opcode[1], 16)
                value = str(self.Registers[Vx].value)

                fillNum = 3 - len(value)
                value = '0' * fillNum + value

                for i in range(len(value)):
                    self.Memory[self.IRegister.value + i] = int(value[i])
            
            elif opcode[2:] == '55':
                #FX55
                #reg_dump(Vx, &I)

                Vx = int(opcode[1], 16)
                for i in range(0, Vx + 1):
                    self.Memory[self.IRegister.value + i] = self.Registers[i].value

            elif opcode[2:] == '65':
                #FX65
                #reg_load(Vx, &I)

                Vx = int(opcode[1], 16)
                for i in range(0, Vx + 1):
                    self.Registers[i].value = self.Memory[self.IRegister.value + i]

        self.ProgramCounter += 2

    def execution(self):
        index = self.ProgramCounter
        high = self.hexHandler(self.Memory[index])
        low = self.hexHandler(self.Memory[index + 1])

        opcode = high + low

        self.execOpcode(opcode)

    def draw(self, Vx, Vy, sprite):
        collision = False

        spriteBits = []
        for i in sprite:
            binary = bin(i)
            line = list(binary[2:])
            fillNum = 8 - len(line)
            line = ['0'] * fillNum + line

            spriteBits.append(line)

        for i in range(len(spriteBits)):
            for j in range(8):
                try:
                    inversion = False
                    if self.grid[Vy + i][Vx + j] == 1 and int(spriteBits[i][j]) == 1:
                        collision = True
                        inversion = True
                        
                    if int(spriteBits[i][j]) == 1:
                        display.fill_rectangle((Vx + j) * self.size, (Vy + i) * self.size, self.size, self.size, invert=inversion)

                    self.grid[Vy + i][Vx + j] = self.grid[Vy + i][Vx + j] ^ int(spriteBits[i][j])
                except:
                    continue

                
        display.present()
        return collision
    
    def clear(self):
        display.clear()
        display.present()
        
        for i in range(len(self.grid)):
            for j in range(len(self.grid[0])):
                self.grid[i][j] = 0


    def loadSave(self):
        bool_bouton = 0
        bally = XglcdFont('fonts/Bally7x9.c', 7, 9)
        display.draw_text(0, 20, "charger sauvegarde", bally)
        display.fill_rectangle(19,40,25,11, invert = False)
        display.draw_text(20, 40, "oui", bally, invert = True)
        display.draw_text(80, 40, "non", bally)
        choix = 1
        display.present()
        while lecture_touche()!= "A" and lecture_touche() != "start":
            if lecture_touche() == "gauche" and bool_bouton == 0:
                display.fill_rectangle(79,40,25,11, invert = True)
                display.draw_text(80, 40, "non", bally, invert = False)
                display.fill_rectangle(19,40,25,11, invert = False)
                display.draw_text(20, 40, "oui", bally, invert = True)
                display.present()
                choix = 1
                bool_bouton = 1
                
            elif lecture_touche() == "droite" and bool_bouton == 0:
                display.fill_rectangle(19,40,25,11, invert = True)
                display.draw_text(20, 40, "oui", bally, invert = False)
                display.fill_rectangle(79,40,25,11, invert = False)
                display.draw_text(80, 40, "non", bally, invert = True)
                display.present()
                choix = 0
                bool_bouton = 1
            
            if lecture_touche() == None:
                bool_bouton = 0
                
        display.clear()
        display.present()
            
        return choix

    def Convert(self, i):
        if i <= 57:
            i -= 48
        else:
            i -= 87
        return i
    

    def readProg(self, filename):
        
        self.filename = filename
        begin = 6
        if pinout.SD_READER:
            begin = 10
            
        self.saveName = root + "Saves/" + self.filename[begin:len(self.filename)-3]+"sav"
        self.keyFile = root + "Games/" + self.filename[begin:len(self.filename)-4]
        print(self.keyFile)
        self.loadKeys()
        
        try:
            f = open(self.saveName)
        except:
            print("pas de sauvegarde")
            rom = self.convertProg(filename)
            
            offset = int('0x200', 16)
            for i in rom:
                self.Memory[offset] = i
                offset += 1
            
        else:
            if self.loadSave():
                with open(self.saveName, 'rb') as f:
                    wholeProgram = f.read()
                    bit = 0
                    reg = 0
                    pc = 0
                    multpc = 16**3
                    multI = 16**3
                    multStack = 16**3
                    indexStack = 0
                    stack_byte = 0
                    delay_byte = 0
                    x = 0
                    y = 0
                    stack = []
                    offset = 0
                    for i in wholeProgram:
                        
                        # ram
                        if offset <= 4095:
                            self.Memory[offset] = i
                            offset += 1
                            
                        # 16 registres 8-bit
                        elif offset >= 4096 and offset <= 4127:
                            if bit == 0:
                                highBits = self.Convert(i)
                                bit = 1
                            
                            elif bit == 1:
                                lowBits = self.Convert(i)
                                self.Registers[reg].setValue(highBits*16+lowBits)
                                reg += 1
                                bit = 0
                                
                            offset += 1
                        
                        # registre I (16-bit)
                        elif offset >= 4128 and offset <= 4131:
                            i = self.Convert(i)
                            self.IRegister.setValue(self.IRegister.readSave() + i*multI)
                            multI = multI//16
                            offset += 1

                        # PC (16-bit)
                        elif offset >= 4132 and offset <= 4135:
                            i = self.Convert(i)
                            pc += i*multpc
                            multpc = multpc//16
                            offset += 1
                        
                        # Timer (8-bit)
                        elif offset == 4136 or offset == 4137:
                            i = self.Convert(i)
                                
                            if delay_byte == 0:
                                delay_byte = 1
                                timer = i*16
                            else:
                                timer += i
                                self.delayTimer.setTimer(timer)
                           
                            offset += 1
                        
                        # ecran
                        elif offset >= 4138 and offset <= 6185:
                            self.grid[y][x] = i
                            
                            x += 1
                            if x == 64:
                                x = 0
                                y += 1
                            
                            offset += 1
                            
                        # stack (16-bit)
                        else:
                            i = self.Convert(i)
                            
                            stack_byte += i*multStack
                            multStack = multStack//16
                            indexStack += 1
                            
                            if indexStack == 4:
                                stack.append(stack_byte)
                                indexStack = 0
                                stack_byte = 0
                                multStack = 16**3
                                
                            offset += 1
                            
                            
                self.stack.load(stack)
                
                self.ProgramCounter = pc
                
                for y in range(0, len(self.grid)):
                    for x in range(0, len(self.grid[0])):
                        if self.grid[y][x] == 1:
                            display.fill_rectangle(x * self.size, y * self.size, self.size, self.size)
                        
                display.present()
                print("sauvegarde chargée")
                
                
            else:
                rom = self.convertProg(filename)
            
                offset = int('0x200', 16)
                for i in rom:
                    self.Memory[offset] = i
                    offset += 1
        
    
    def convertProg(self, filename):
        rom = []

        with open(filename, 'rb') as f:
            wholeProgram = f.read()

            for i in wholeProgram:
                opcode = i
                rom.append(opcode)
        
        return rom
    
    def loadKeys(self):
        try:
            KEYS = __import__(self.keyFile)
        except:
            print("pas de configuration")
        else:
            KEYS = __import__(self.keyFile)
            list_keys = KEYS.keyDict.keys()
            for x in list_keys:
                print(str(KEYS.keyDict[x]) + " : " + x)
                self.keyDict[x] = KEYS.keyDict[x]
            print("configuration chargée")
    
    def hexHandler(self, Num):
        newHex = hex(Num)[2:]
        if len(newHex) == 1:
            newHex = '0' + newHex
        
        return newHex

    def keyHandler(self):
        global liste_bouton
        
        if ticks_us() - self.lastime >= (16670):
            self.lastime = ticks_us()
            self.delayTimer.countDown()
            self.soundTimer.countDown()
        
        self.pin_value = lecture_touche()
        
        if self.pin_value == "start" and self.bool_start == 0:
            self.pause = 1
            display.fill_rectangle(50, 18, 28, 28, invert = True)
            display.fill_rectangle(54, 22, 8, 20)
            display.fill_rectangle(66, 22, 8, 20)
            display.present()
            self.bool_start = 1
            
        if self.pin_value == None:
            self.bool_start = 0
        
        if self.pin_value != "start" and self.pin_value != "home":
            if self.lastKey != self.pin_value:
                targetKey = self.keyDict[self.lastKey]
                self.keys[targetKey] = False
                
            if self.pin_value != None:
                targetKey = self.keyDict[self.pin_value]
                self.keys[targetKey] = True
                self.lastKey = self.pin_value
        
        #for i in range(len(self.label_bouton)):
            #targetKey = self.keyDict[self.label_bouton[i]]
            #if liste_bouton[i] == 1:
                #print(self.label_bouton[i])
                #self.keys[targetKey] = True
                #liste_bouton[i] = 0
                
            #else:
                #self.keys[targetKey] = False
                

    def fillZero(self, data, s):
        if self.IRegister.readSave() <= 0xf:
            s.write("0")
        if self.IRegister.readSave() <= 0xff:
            s.write("0")
        if self.IRegister.readSave() <= 0xfff:
            s.write("0")

    def mainLoop(self):
        while lecture_touche() != "home" and self.playing == 1:
            if self.pause == 0:
                self.keyHandler()
                if self.SOUND:
                    self.soundTimer.beep()
                self.execution()
            else:
                if lecture_touche() == "start" and self.bool_start == 0:
                    self.pause = 0
                    
                    # on réimprime l'écran
                    display.clear()
                    for y in range(0, len(self.grid)):
                        for x in range(0, len(self.grid[0])):
                            if self.grid[y][x] == 1:
                                display.fill_rectangle(x * self.size, y * self.size, self.size, self.size)
                    display.present()
                            
                    self.bool_start = 1
                elif lecture_touche() == None:
                    self.bool_start = 0
        
        buzzer.duty_u16(0)
        with open(self.saveName, 'w') as s:
            # on sauvegarde la memoire ram
            s.write(bytearray(self.Memory))
            
            # on sauvegarde les 16 registres 8-bit
            for i in range(0,16):
                if self.Registers[i].readSave() <= 0xf:
                    s.write("0")
                s.write(str(self.Registers[i].readValue())[2:])
                
            # on sauvegarde le registre I de 16-bit
            self.fillZero(self.IRegister.readSave(), s)
            s.write(str(self.IRegister.readValue())[2:])
            
            # on sauvegarde le PC de 16-bit
            self.fillZero(self.ProgramCounter, s)
            s.write(str(hex(self.ProgramCounter))[2:])
            
            # on sauvegarde le delayTimer de 8-bit
            if self.delayTimer.readTimer() <= 0xf:
                    s.write("0")
            s.write(str(hex(self.delayTimer.readTimer()))[2:])
            
            # on sauvegarde l'écran (chaque pixel prend 8bit)*128*64
            for i in range(len(self.grid)):
                s.write(bytearray(self.grid[i]))
            
            # on sauvegarde le stack (16 valeur max) de 16-bit
            stack = self.stack.get()
            for element in stack:
                self.fillZero(element, s)
                s.write(str(hex(element))[2:])
    
            
        display.clear()
        display.present()
