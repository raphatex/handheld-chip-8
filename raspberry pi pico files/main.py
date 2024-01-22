from emulator import Emulator
from buttons import lecture_touche

print("lancement du jeu")

while lecture_touche() != 'D':
    print("")

chip8 = Emulator()
chip8.readProg("games/mastermind.ch8")
chip8.mainLoop()

print("de retour à l'OS")