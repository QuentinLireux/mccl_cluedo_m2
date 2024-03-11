import socket
import random
import sys


nbjoueur = 0

HOST_NAME = "localhost"
host_port = 0 
buffer = 1024



def traiter(msg,connexion_serveur):
    """#La ligne est B -> on dit bonjour
    if msg.split(" ")[0] == "B":
        nous = msg.split(" ")[0] +" "+ msg.split(" ")[1]
        connexion_serveur.send(nous.encode())
        
        print("Bonjour je suis ", msg)
        nbjoueur = int(msg.split(" ")[2])
    """ 
    #La ligne est H -> un joueur fait l'hypothèse H X X X, on ne fait rien
    if msg.split(" ")[0] == "H" :
        print("Un joueur a fait l'hypothése : ", msg)

    #La ligne est C -> on doit montrer une carte qui est dans l'hypothèse
    if msg.split(" ")[0] == "C" and len(msg) <= 2:
        print("Tu dois donner une carte qui est dans l'hypothèse")
        print("A toi de répondre")
        rep = input()
        connexion_serveur.send(rep.encode())

     #La ligne est C c c c -> on nous donne nos cartes
    if msg.split(" ")[0] == "C" and len(msg) > 2:
        print("Nos cartes sont ", msg)

    #La ligne est M -> personne n'a les cartes de l'hypothèse
    if msg.split(" ")[0] == "M" and len(msg) == 1:
        print("Personne n'a les cartes de l'hypothèse")
    
    #La ligne est M X -> X a une des cartes de l'hypothèse
    if msg.split(" ")[0] == "M" and len(msg) == 3:
        print("Quelqu'un a l'une des cartes de l'hypothèse")
        print
    #La ligne est M X c -> X a la carte c
    if msg.split(" ")[0] == "M" and len(msg) == 5:
        print("Il a la carte ", msg)
    #La ligne est T -> c'est notre tour on doit choisir hypothèse ou accusation
    if msg.split(" ")[0] == "T":
        print("A toi de répondre")
        rep = input()
        connexion_serveur.send(rep.encode())
    
    #La ligne est P X -> X n'a aucune carte de l'hypothèse
    if msg.split(" ")[0] == "P":
        print("Aucune carte de l'hypothèse")

    #La ligne est F -> la partie est finie
    if msg.split(" ")[0] == "F":
        print("Le jeu est fini.")
        connexion_serveur.close()
        quit()
    else:
        pass#print("On a pas traité ce message.")

    


if (len(sys.argv) < 1):
    print('Usage: joueur.py <port> ', file=sys.stderr)
host_port = int(sys.argv[1])

connexion_serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connexion_serveur.connect((HOST_NAME,host_port))

while(True):

    msg = connexion_serveur.recv(buffer).decode()
    if msg != "":
        #print(msg)
   
        if msg.split(" ")[0] == "B":
            nous = msg.split(" ")[0] +" "+ msg.split(" ")[1]
            connexion_serveur.send(nous.encode())
            print("Bonjour je suis ", msg)
            nbjoueur = int(msg.split(" ")[2])
        else:
            for msg in msg.split("\n") :
                traiter(msg,connexion_serveur)
        #connexion_serveur.send(rep.encode())
        