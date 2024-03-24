from emulator import Emulator
from buttons import lecture_touche

while True:
    if lecture_touche() == "start":
        print("lancement du jeu")

        chip8 = Emulator()
        chip8.readProg("games/Tetris [Raphatex, 2024].ch8")
        chip8.mainLoop()

        print("de retour à l'OS")

