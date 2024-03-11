#! /usr/bin/python3

###############################
### Serveur de jeu "cluedo"
###
###
### Version 0.2
###
###
### Gaétan Richard 2023
###############################


import socket
import sys
import random


######################
## Variables globales
######################

N=2 # Nombre de joueurs
lieux=[ i for i in range(N+1)]
armes=[ N+i+1 for i in range(N+1)]
personnages = [ 2*N+i+2 for i in range(N+1)]

BUF=20 # Taille maximale de la ligne

LIMITE=N*N*N # Limite du nombre de tour

#socket.setdefaulttimeout(10) # Délai maximal de réponse


###################
## Données serveur 
###################

# Liste des joueurs
# Un joueur est décrit par l’enregistrement
# nom et conn
joueurs = [ None for i in range(N)] 
gains = [ 0 for i in range(N)]

########################
## Données de la partie
########################

secret=None # Le secret à deviner
actifs = [True for i in range(N)] # Les joueurs actifs


#####################
## Code
#####################

# Exception 
class ServerError(Exception):
    def __init__(self,code,j) :
        self.code = code
        self.j = j

    def __str__(self) :
        return "Erreur serveur de "+str(self.j)+" ["+str(self.code)+"]"



# Prépare un message à envoyer
def message(commande,args) :

    msg=commande+" "+" ".join([str(arg) for arg in args])+"\n"

    return msg.encode()

# Décode un message, renvoie la commande et les arguments
def decode(data) :

    info = data.decode().split(" ") 

    return (info[0], [ int(s) for s in info[1:]])

# Vérifie que la liste contient trois cartes 
def verifie_cartes(l,j) :
    if ( len(l) != 3 ) :
        raise(ServerError(201,j))
    c=sorted(l)
    M=N+1
    if ( 0 <= c[0] < M and
         M <= c[1] < 2*M and
         2*M <= c[2] < 3*M ) :
        return # OK
    raise(ServerError(201,j))


# Envoie un message à tous les joueurs sauf j
# Si j est None, on envoi à tous
def broadcast(msg,j) :
    for i in range(N) :
        if (i == j) :
            continue
        joueurs[i]["conn"].send(msg)


def voisins(j,cartes) :

    for k in range(j+1,j+N) : # On parcours tous les autres voisins en partant de j
        i = k % N
        main = joueurs[i]["cartes"]
        if cartes[0] in main or cartes[1] in main or cartes[2] in main :
            # le joueur possède au moins une carte en main
            
            joueurs[i]["conn"].send(message("C",[])) # On demande le choix au joueur
            try :
                (com,args)=decode(joueurs[i]["conn"].recv(BUF)) # On reçoit sa réponse
            except Exception :
                raise(ServerError(122,i))

            if (com != "M" or not args[0] in cartes or not args[0] in main) :
                raise(ServerError(121,i))

            return (i,args[0])
        else :
            broadcast(message("P",[i]),None) # On previens tout le monde que i passe 

    return (None,None) # Cas particulier, aucun joueur (hors j) n’a de carte de la demande

def lancer_serveur (port) :

    # On crée la socket
    s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("localhost", port))
    s.listen()

    # On récupère les connections des joueurs
    for i in range(N) :
        conn, addr = s.accept()
        conn.send(message("B",[i,N])) # Envoie du bonjour
        
        try :
            nom=conn.recv(BUF).decode().split(" ") # Réception du nom
        except Exception :
            raise(ServerError(103,i))
        
        if (len(nom)!=2 or nom[0] != "B"):
            raise(ServerError(103,i))


        joueurs[i]= { "nom" : nom[1] , "conn" : conn , "cartes" : None} # Ajout du joueur


def init_partie() :
    global secret,actifs
    
    # On mélange les trois piles
    random.shuffle(lieux)
    random.shuffle(armes)
    random.shuffle(personnages)

    # On met le secret
    secret=[lieux[0],armes[0],personnages[0]]
    print(secret)
    # On remet actif tous les joueurs
    actifs = [True for i in range(N)]

    # On attribue les cartes restantes
    pile = lieux[1:]+armes[1:]+personnages[1:]
    random.shuffle(pile)
    for i in range(N) :
        joueurs[i]["cartes"] = pile[3*i:3*i+3]
        joueurs[i]["conn"].send(message("C",pile[3*i:3*i+3]))

def partie () :

    init_partie()

    t=-1 # Tour en cours

    while True:
        t+=1

        if t > LIMITE :
            raise(ServerError(104,-1))
        j = t % N # joueur en cours

        if (not actifs[j]) : # Le joueur est éliminé
            continue 

        # On demande l’action au joueur
        joueurs[j]["conn"].send(message("T",[]))
        try :
            (com,args) = decode(joueurs[j]["conn"].recv(BUF))
        except Exception :
            raise(ServerError(112,i))
        
        if com == "A" :
            verifie_cartes(args,j) 
            if sorted(args)==secret :
                broadcast(message("F",[j]),None) # On envoie M à tous le monde
                return (j,t) # Le joueur j a gagné la partie
            else :
                actifs[j]=False # Le joueur 
        elif com == "H" :
            verifie_cartes(args,j)  
            broadcast(message(com,args),j) # On transmet l’hypothèse à tous
            (vois,rep)=voisins(j,args) # On va chercher parmis les voisins
            if vois is None :
                broadcast(message("M",[]),None) # On envoie M à tous le monde
            else :
                broadcast(message("M",[vois]),j) # On envoie M vois à tous les autres
                joueurs[j]["conn"].send(message("M",[vois,rep]))
        else :
            raise(ServerError(111,i))

    pass


if __name__ == "__main__":

    if (len(sys.argv) < 2) :
        print('Usage: Serveur.py <port> <nb_parties>', file=sys.stderr)
        
    lancer_serveur(int(sys.argv[1]))

    for i in range(int(sys.argv[2])) :
        try :
            (j,t)=partie()
            print("La partie",i,"a été gagnée par le joueur",j,"en",t,"tour")
            gains[j]+=1
        except ServerError as e:
            broadcast(message("E",[e.code]),None)
            print("Partie",i,": Erreur",e.code,"par",e.j)
            if e.j >0 :
                gains[e.j]-=1

    print(gains)

