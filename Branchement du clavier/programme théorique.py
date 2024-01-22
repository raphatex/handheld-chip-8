from machine import Pin
import utime 

# les lignes du clavier sont branchées aux broches
# GP1, GP2, GP3, GP4 du pico
broches_lignes = [1,2,3,4]

# les colonnes du clavier sont branchées aux broches
# GP5, GP6, GP7, GP8 du pico
broches_colonnes = [5,6,7,8]

# matrice définissant chaque touche du clavier
clavier = [["1","2","3","A"],["4","5","6","B"],\
         ["7","8","9","C"],["*","0","#","D"]]


# routine qui identifie la touche enfoncée:
def lecture_touche (cols,lignes):
  for i in lignes: # une ligne à la fois
    i.value(0)  # on met la ligne au niveau logique bas
    # on mesure chaque colonne de cette ligne
    resultat=[cols[0].value(),cols[1].value(),cols[2].value(),cols[3].value()]
    if min(resultat)==0:
      reponse = clavier[int(lignes.index(i))][int(resultat.index(0))]
      i.value(1) # au cas où une touche est maintenue enfoncée
      return(reponse)
    i.value(1) # retour au niveau logique haut    

mots = ''

def ajout(touche) :
    mots = mots + touche
    return mots


for x in range(0,4):
    broches_lignes[x]=Pin(broches_lignes[x], Pin.OUT)
    broches_lignes[x].value(1)

# les colonnes réglées en entrée
# les lignes sont réglées en sorties, niveau logique haut
for x in range(0,4):
    broches_lignes[x]=Pin(broches_lignes[x], Pin.OUT)
    broches_lignes[x].value(1)
    
for x in range(0,4):
    broches_colonnes[x] = Pin(broches_colonnes[x], Pin.IN, Pin.PULL_UP)
    
# les colonnes réglées en entrée
for x in range(0,4):
    broches_colonnes[x] = Pin(broches_colonnes[x], Pin.IN, Pin.PULL_UP)

def write() :
    touche = lecture_touche(broches_colonnes,broches_lignes)
    if touche != None :
        if touche == '#' :
            print(mots)
        else :
            mot = mot + touche
            print(touche,end ='') #Simplifier avec fonctions si ça marche
            time.sleep(0.3)
            write()
        
        
