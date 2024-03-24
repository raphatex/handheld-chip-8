from machine import Pin
from time import sleep

broches_boutons = [7,9,4,5,12,13,14,15]
label_bouton = ["start","gauche","bas","droite","haut","home","A","B"]

for x in range(0,8):
    broches_boutons[x] = Pin(broches_boutons[x], Pin.IN, Pin.PULL_UP)
    
def lecture_touche():
    for x in range(0,8):
        if broches_boutons[x].value() == 0:
            return label_bouton[x]