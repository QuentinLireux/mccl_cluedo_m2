import socket
import random
import sys


nbjoueur = 0
HOST_NAME = "localhost"
host_port = 0 
buffer = 1024

notre_nom = None
joueur_actuelle = 0
current_hypo = []
secret = {"c1":None,"c2":None,"c3":None}
connaissance_j = {}
tour = 0
limite = 0


class ServerError(Exception):
    def __init__(self,code,j) :
        self.code = code
        self.j = j

    def __str__(self) :
        return "Erreur client de "+str(self.j)+" ["+str(self.code)+"]"

def initialise_base():
    dico_carte1 = {}
    dico_carte2 = {}
    dico_carte3 = {}
    for i in range (0,((nbjoueur+1)*3)):
        if i < ((nbjoueur+1)*3)/3:
            dico_carte1.update({i:None})
        elif i >= ((nbjoueur+1)*3)/3 and i < ((nbjoueur+1)*3)*2/3:
            dico_carte2.update({i:None})
        elif i >= ((nbjoueur+1)*3)*2/3:
            dico_carte3.update({i:None})
    for j in range (0,nbjoueur):
        connaissance_j.update({j:{"c1":dico_carte1.copy(),"c2":dico_carte2.copy(),"c3":dico_carte3.copy()}})

def ajoute_hypo(joueur, c, bool):
    cat = ""
    if c < ((nbjoueur+1)*3)/3:
        cat = "c1"
    if c >= ((nbjoueur+1)*3)/3 and c < ((nbjoueur+1)*3)*2/3:
        cat = "c2"
    if c >= ((nbjoueur+1)*3)*2/3:
        cat = "c3"
    connaissance_j[joueur][cat][c] = bool
    maj(joueur,cat,c,bool)

def maj(joueur,cat,c, bool):
    for i in range (0,nbjoueur):
        if joueur == notre_nom: # a revérifier
            if i != joueur:
                connaissance_j[i][cat][c] = not(bool)
        else:
            connaissance_j[i][cat][c] = bool # a retirer
            connaissance_j[notre_nom][cat][c] = not(bool)


def un_gagnant():
    somme_secret_c1 = []
    somme_secret_c2 = []
    somme_secret_c3 = []
    for c_key, c_value in connaissance_j[notre_nom].items():
        for j_key,j_value in connaissance_j[notre_nom][c_key].items():
            if j_value == None:
                if j_key < ((nbjoueur+1)*3)/3:
                    somme_secret_c1.append(j_key)
                if j_key >= ((nbjoueur+1)*3)/3 and j_key < ((nbjoueur+1)*3)*2/3:
                    somme_secret_c2.append(j_key)
                if j_key >= ((nbjoueur+1)*3)*2/3:
                    somme_secret_c3.append(j_key)

    if len(somme_secret_c1) == 1:
        secret["c1"] = somme_secret_c1[0]
    if len(somme_secret_c2) == 1:
        secret["c2"] = somme_secret_c2[0]
    if len(somme_secret_c3) == 1:
        secret["c3"] = somme_secret_c3[0]
    #print("Le secret :",secret)


def formuler_hypothese():
    hypothese = {"c1": None, "c2": None, "c3": None}
    for type_carte in connaissance_j[notre_nom]:
        hypothese_type_carte = []
        for numero_carte in connaissance_j[notre_nom][type_carte]:
            if connaissance_j[notre_nom][type_carte][numero_carte] == None:
                hypothese_type_carte.append(numero_carte)
        if hypothese_type_carte:
            hypothese[type_carte] = random.choice(hypothese_type_carte)
    return hypothese


def choisie_une_carte(hypo):
    cartes = []
    for i in range (0,((nbjoueur+1)*3)):
        if i in hypo:
            if i < ((nbjoueur+1)*3)/3:
                if connaissance_j[notre_nom]["c1"][i] != None:
                    cartes.append(i)
            elif i >= ((nbjoueur+1)*3)/3 and i < ((nbjoueur+1)*3)*2/3:
                if connaissance_j[notre_nom]["c2"][i] != None:
                    cartes.append(i)
            elif i >= ((nbjoueur+1)*3)*2/3:
                if connaissance_j[notre_nom]["c3"][i] != None:
                    cartes.append(i)
    return random.choice(cartes)

def recup_cards(msg):
    return (int(msg.split(" ")[1]),int(msg.split(" ")[2]),int(msg.split(" ")[3]))

def fin_tour():
    global joueur_actuelle,nbjoueur,tour
    if joueur_actuelle == nbjoueur-1:
        joueur_actuelle = 0
    else:
        joueur_actuelle += 1
    tour += 1
    print("\n\nTour :" ,tour, ", Joueur :",joueur_actuelle)
    print(connaissance_j)
    un_gagnant()


def traiter(msg):
    global notre_nom, nbjoueur,connaissance_j, secret,joueur_actuelle,current_hypo,limite
    #La ligne est B -> on dit bonjour
    if msg.split(" ")[0] == "B":
        nous = msg.split(" ")[0] +" "+ msg.split(" ")[1]
        connexion_serveur.send(nous.encode())
        
        print("Bonjour je suis ", msg)
        notre_nom = int(msg.split(" ")[1])
        nbjoueur = int(msg.split(" ")[2])
        limite = nbjoueur * nbjoueur * nbjoueur
        initialise_base()
        
    #La ligne est H -> un joueur fait l'hypothèse H X X X
    elif msg.split(" ")[0] == "H" :
        fin_tour()
        current_hypo = [] # a retirer
        current_hypo.append(int(msg.split(" ")[1]))
        current_hypo.append(int(msg.split(" ")[2]))
        current_hypo.append(int(msg.split(" ")[3]))
        print("l'hypo :",current_hypo)
        #fin_tour()
    #La ligne est C -> on doit montrer une carte qui est dans l'hypothèse
    elif msg.split(" ")[0] == "C" and len(msg) <= 2:
        carte_choisie = choisie_une_carte(current_hypo)
        cst = "M " + str(carte_choisie)
        print("Je donne la carte ",cst)
        connexion_serveur.send(cst.encode())
        #fin_tour()

    #La ligne est C c c c -> on nous donne nos cartes
    elif msg.split(" ")[0] == "C" and len(msg) > 2:
        cards = recup_cards(msg)
        print("Voici nos cartes : ",cards)
        for i in cards:
            ajoute_hypo(int(notre_nom),int(i),True)

    #La ligne est M -> personne n'a les cartes de l'hypothèse
    elif msg.split(" ")[0] == "M" and len(msg) == 1:
        print("Il n'a aucune carte")
        for i in current_hypo:
            ajoute_hypo(joueur_actuelle,i,True) # A revoir je crois que c'est false
        
    #La ligne est M X -> X a une des cartes de l'hypothèse
    elif msg.split(" ")[0] == "M" and len(msg) == 3:
        print("Il a l'une des cartes ", msg.split(" ")[1])

        #fin_tour()
    
    #La ligne est M X c -> X a la carte c
    elif msg.split(" ")[0] == "M" and len(msg) == 5:
        print((msg.split(" ")[1])," a la carte " ,int(msg.split(" ")[2]))
        ajoute_hypo(int(msg.split(" ")[1]), int(msg.split(" ")[2]), True)
        #fin_tour()

    #La ligne est T -> c'est notre tour on doit choisir hypothèse ou accusation
    elif msg.split(" ")[0] == "T":
        fin_tour()

        if secret["c1"] != None and secret["c2"] != None and secret["c3"] != None :
            cst = "A "+ str(secret["c1"]) +" "+ str(secret["c2"]) + " " + str(secret["c3"])
            print("J'accuse ! ",cst)
            connexion_serveur.send(cst.encode())
        else:
            hypo = formuler_hypothese()
            cst = "H "+ str(hypo["c1"]) +" "+ str(hypo["c2"]) + " " + str(hypo["c3"])
            print("Mon hypothèse est ",cst)
            connexion_serveur.send(cst.encode())
        
        

    #La ligne est P X -> X n'a aucune carte de l'hypothèse
    elif msg.split(" ")[0] == "P":
        print("Il n'a pas de carte")
        #fin_tour()
        

    #La ligne est F -> la partie est finie
    elif msg.split(" ")[0] == "F":
        print("Le jeu est fini.")
        connexion_serveur.close()
        quit()

    else:
        pass
        #print("On a pas traité ce message.")



if (len(sys.argv) < 1):
    print('Usage: bot1.py <port> ', file=sys.stderr)
host_port = int(sys.argv[1])


connexion_serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connexion_serveur.connect((HOST_NAME,host_port))



while(True):
    if tour > limite :
            raise(ServerError(104,-1))
    
    msg = connexion_serveur.recv(buffer).decode()
    if msg != "":
        #print(msg)
        
        for msg in msg.split("\n") :
            traiter(msg)
    
        