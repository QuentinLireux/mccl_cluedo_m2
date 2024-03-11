import socket
import random
import sys


nbjoueur = 0
HOST_NAME = "localhost"
host_port = 0 
buffer = 1024

def gen_deck():
    l1 = []
    l2 = []
    l3 = []
    for i in range(0,nbjoueur+1):
        l1.append(i)
    for j in range(nbjoueur+1, (nbjoueur*2)+2):
        l2.append(j)
    for k in range((nbjoueur*2)+2, (nbjoueur*3)+3):
        l3.append(k)
    deck.append(l1)
    deck.append(l2)
    deck.append(l3)

def supprime_pos(i):
    deck[i//(nbjoueur+1)][i%(nbjoueur+1)] = -1

def choisie_une_carte(hypo):
    intersection = []
    for i in hypo:
        if i in c:
            intersection.append(i)
    if len(intersection) != 0:
        return random.choice(intersection)
    else:
        return None

def recup_cards(msg):
    return (int(msg.split(" ")[1]),int(msg.split(" ")[2]),int(msg.split(" ")[3]))

def random_cards():
    deck_1 = []
    deck_2 = []
    deck_3 = []
 
    for i in deck[0]:
        if i != -1:
            deck_1.append(i)
    for i in deck[1]:
        if i != -1:
            deck_2.append(i)
    for i in deck[2]:
        if i != -1:
            deck_3.append(i)

    while True:
        c1 = random.choice(deck_1)
        c2 = random.choice(deck_2)
        c3 = random.choice(deck_3)
        if [c1, c2, c3] not in list_hypo:
            list_hypo.append([c1,c2,c3])
            return (c1,c2,c3)



def traiter(msg):
    #La ligne est B -> on dit bonjour
    if msg.split(" ")[0] == "B":
        pass
    #La ligne est H -> un joueur fait l'hypothèse H X X X, on ne fait rien
    elif msg.split(" ")[0] == "H" :
        pass

    #La ligne est C -> on doit montrer une carte qui est dans l'hypothèse
    elif msg.split(" ")[0] == "C" and len(msg) <= 2:
        pass

     #La ligne est C c c c -> on nous donne nos cartes
    elif msg.split(" ")[0] == "C" and len(msg) > 2:
        pass


    #La ligne est M -> personne n'a les cartes de l'hypothèse
    elif msg.split(" ")[0] == "M" and len(msg) == 1:
        pass
    
    #La ligne est M X -> X a une des cartes de l'hypothèse
    elif msg.split(" ")[0] == "M" and len(msg) == 3:
        pass
    
    #La ligne est M X c -> X a la carte c
    elif msg.split(" ")[0] == "M" and len(msg) == 5:
        supprime_pos(int(msg.split(" ")[-1]))

    #La ligne est T -> c'est notre tour on doit choisir hypothèse ou accusation
    elif msg.split(" ")[0] == "T":
        print("DECK-> ", deck)
        rep = on_est_pas_gagnant()
        print(rep)
        #On a un jeu gagnant -> on emet une accusation  
        if (rep != 0):
            cst = "A "+ str(rep[0]) +" "+ str(rep[1]) + " " + str(rep[2])
            print("J'accuse ! ",cst)
            connexion_serveur.send(cst.encode())
        
        #Aucun jeu n'est gagnant on emet une hypothèse
        else: 
            c1,c2,c3 = random_cards()
            cst = "H "+ str(c1) +" "+ str(c2) + " " + str(c3)
            print("Mon hypothèse est ",cst)
            connexion_serveur.send(cst.encode())
    
    #La ligne est P X -> X n'a aucune carte de l'hypothèse
    elif msg.split(" ")[0] == "P":
        pass

    #La ligne est F -> la partie est finie
    elif msg.split(" ")[0] == "F":
        print("Le jeu est fini.")
        connexion_serveur.close()
        quit()
    else:
        pass#print("On a pas traité ce message.")

    


if (len(sys.argv) < 1):
    print('Usage: bot0.py <port> ', file=sys.stderr)
host_port = int(sys.argv[1])


connexion_serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connexion_serveur.connect((HOST_NAME,host_port))

while(True):

    msg = connexion_serveur.recv(buffer).decode()
    if msg != "":
        print(msg)
        
        for msg in msg.split("\n") :
            traiter(msg)
        