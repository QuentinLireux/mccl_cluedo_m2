import socket
import random
import sys



liste_hypo = []

#Contient l'accusation en chaine de caractère
accusation = ""

nbjoueur = 0
c = []
HOST_NAME = "localhost"
host_port = 0 
buffer = 1024
notre_nom = None

current_hypo = []

def ajoute_hypo(j,c1, c2=None, c3=None, boolean=True):
    hypo = {}

    hypo["joueur"] = j
    hypo["bool"] = boolean
    hypo["c1"] = c1
    hypo["c2"] = c2
    hypo["c3"] = c3

    supprime_hypos(hypo)
    liste_hypo.append(hypo)



def supprime_hypos(hypo):
    for i in liste_hypo:
        if hypo["c3"] == None:
            if hypo["c2"] == None:
                if hypo["bool"]:
                    if hypo["joueur"] != i["joueur"] and hypo["c1"] == i["c1"]:
                        liste_hypo.remove(hypo)
                        ajoute_hypo(i["joueur"],i["c1"],boolean=False)
                else :
                    pass
            else:
                if hypo["joueur"] != i["joueur"] and (hypo["c1"] == i["c1"] or hypo["c2"] == i["c2"]):
                    liste_hypo.remove(hypo)
       
        else:
            pass 

def choisir_hypo():
    # Trouver trois cartes que le bot n'a pas vues
    cartes_non_vues = []
    for carte in range(nbjoueur * 3 + 3):
        if carte not in current_hypo:
            cartes_non_vues.append(carte)

    if len(cartes_non_vues) >= 3:
        # Choisissez trois cartes non vues au hasard
        choix_hypo = random.sample(cartes_non_vues, 3)
        print(choix_hypo)
        return (choix_hypo[0], choix_hypo[1], choix_hypo[2])
    else:
        # Le bot a vu toutes les cartes, il peut faire une accusation
        return None


def choisie_une_carte(hypo):
    for carte in hypo:
        if carte in c:
            return carte

def recup_cards(msg):
    return (int(msg.split(" ")[1]),int(msg.split(" ")[2]),int(msg.split(" ")[3]))

def traiter(msg):
    global  nbjoueur, notre_nom, accusation,c
    #La ligne est B -> on dit bonjour
    if msg.split(" ")[0] == "B":
        nous = msg.split(" ")[0] +" "+ msg.split(" ")[1]
        connexion_serveur.send(nous.encode())
        
        print("Bonjour je suis ", msg)
        notre_nom = int(msg.split(" ")[1])
        nbjoueur = int(msg.split(" ")[2])

    #La ligne est H -> un joueur fait l'hypothèse H X X X
    elif msg.split(" ")[0] == "H" :
        current_hypo.append(int(msg.split(" ")[1]))
        current_hypo.append(int(msg.split(" ")[2]))
        current_hypo.append(int(msg.split(" ")[3]))

    #La ligne est C -> on doit montrer une carte qui est dans l'hypothèse
    elif msg.split(" ")[0] == "C" and len(msg) <= 2:
        carte_choisie = choisie_une_carte(current_hypo)
        cst = "M " + str(carte_choisie)
        print("Je donne la carte ",cst)
        connexion_serveur.send(cst.encode())

    #La ligne est C c c c -> on nous donne nos cartes
    elif msg.split(" ")[0] == "C" and len(msg) > 2:
        cards = recup_cards(msg)
        ajoute_hypo(notre_nom, cards[0],cards[1],cards[2])
        for i in cards:
            c.append(i)
            for j in range (nbjoueur):
                if j != notre_nom :
                    ajoute_hypo(j,i,boolean=False)
        print(liste_hypo)

    #La ligne est M -> personne n'a les cartes de l'hypothèse
    elif msg.split(" ")[0] == "M" and len(msg) == 1:
        accusation = "A "+ str(current_hypo[0]) +" "+ str(current_hypo[1]) + " " + str(current_hypo[2])
        #ajoute_hypo(current_hypo[0],current_hypo[1],current_hypo[2])
        
    #La ligne est M X -> X a une des cartes de l'hypothèse
    elif msg.split(" ")[0] == "M" and len(msg) == 3:
        ajoute_hypo(msg.split(" ")[1], str(current_hypo[0]), str(current_hypo[1]), str(current_hypo[2]))

    
    #La ligne est M X c -> X a la carte c
    elif msg.split(" ")[0] == "M" and len(msg) == 5:
        ajoute_hypo(msg.split(" ")[1], msg.split(" ")[2])

    #La ligne est T -> c'est notre tour on doit choisir hypothèse ou accusation
    elif msg.split(" ")[0] == "T":
        if accusation != "":
            print("J'accuse ! ",accusation)
            connexion_serveur.send(accusation.encode())
        else:
            c1,c2,c3 = choisir_hypo()
            cst = "H "+ str(c1) +" "+ str(c2) + " " + str(c3)
            print(cst)
            connexion_serveur.send(cst.encode())
        #----A complété



    #La ligne est P X -> X n'a aucune carte de l'hypothèse
    elif msg.split(" ")[0] == "P":
        for c in current_hypo:
            ajoute_hypo(msg.split(" ")[1], c, boolean=False)

    #La ligne est F -> la partie est finie
    elif msg.split(" ")[0] == "F":
        print("Le jeu est fini.")
        connexion_serveur.close()
        quit()

    else:
        pass
        #print("On a pas traité ce message.")




if (len(sys.argv) < 1):
    print('Usage: bot0.py <port> ', file=sys.stderr)
host_port = int(sys.argv[1])


connexion_serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connexion_serveur.connect((HOST_NAME,host_port))

while(True):
    liste_hypo = []
    msg = connexion_serveur.recv(buffer).decode()
    if msg != "":
        print(msg)
        
        for msg in msg.split("\n") :
            traiter(msg)
        