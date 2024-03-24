from machine import Pin
from time import sleep

broches_boutons = [0,1,2,3,4,5,6,7]
label_bouton = ["B","gauche","bas","droite","haut","A","home","start"]

for x in range(0,8):
    broches_boutons[x] = Pin(broches_boutons[x], Pin.IN, Pin.PULL_UP)
    
def lecture_touche():
    for x in range(0,8):
        if broches_boutons[x].value() == 0:
            return label_bouton[x]
        