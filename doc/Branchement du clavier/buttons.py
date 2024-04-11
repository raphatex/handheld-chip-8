from machine import Pin

# les lignes du clavier sont branchées aux broches
# GP1, GP2, GP3, GP4 du pico
broches_lignes = [0,1,2,3]

# les colonnes du clavier sont branchées aux broches
# GP4, GP5, GP6, GP7 du pico
broches_colonnes = [4,5,6,7]

# matrice définissant chaque touche du clavier
clavier = [["1","2","3","A"],
           ["4","5","6","B"],
           ["7","8","9","C"],
           ["*","0","#","D"]]

# les lignes sont réglées en sorties, niveau logique haut
for x in range(0,4):
    broches_lignes[x]=Pin(broches_lignes[x], Pin.OUT)
    broches_lignes[x].value(1)
    
# les colonnes réglées en entrée
for x in range(0,4):
    broches_colonnes[x] = Pin(broches_colonnes[x], Pin.IN, Pin.PULL_UP)

# routine qui identifie la touche enfoncée:
def lecture_touche (cols = broches_colonnes,lignes = broches_lignes):
    for i in lignes: # une ligne à la fois
        i.value(0)  # on met la ligne au niveau logique bas
        # on mesure chaque colonne de cette ligne
        resultat=[cols[0].value(),cols[1].value(),cols[2].value(),cols[3].value()]
        if min(resultat)==0:
            reponse = clavier[int(lignes.index(i))][int(resultat.index(0))]
            i.value(1) # au cas où une touche est maintenue enfoncée
            return(reponse)
        i.value(1) # retour au niveau logique haut