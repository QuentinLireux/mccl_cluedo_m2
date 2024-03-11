import os
from threading import Thread
import subprocess
import sys
import platform

path = os.path.abspath(".")


def server(port, tour):
    server = sys.executable + " " + path + "/src/server.py " + port + " " + tour
    print(server)
    os.system(server)

def j1(port, type):
    bot = sys.executable + " " + path + "/src/"+type+".py " + port
    os.system(bot)

def j2(port, type):
    bot = sys.executable + " " + path + "/src/"+type+".py " + port
    print(platform.system())
    if platform.system() == "Windows":
        # Ouvrir un terminal Windows
        subprocess.Popen(["start", "cmd", "/k", bot], shell=True)
    elif platform.system() == "Linux":
        # Ouvrir un terminal Linux (utilisation de x-terminal-emulator, ajustez-le en fonction de votre système)
        subprocess.Popen(["x-terminal-emulator", "-e", bot])
    elif platform.system() == "Darwin":
        # Ouvrir un terminal macOS
        subprocess.Popen(["open", "-a", "Terminal", bot])
    else:
        print("Plate-forme non prise en charge : impossible d'ouvrir un terminal.")


if __name__ == "__main__":
    print(len(sys.argv))
    if (len(sys.argv) < 5) :
        print('Usage: bot1VSbot1.py <port> <nb_parties> <type_j1> <type_j2>', file=sys.stderr)
        exit()

    port = sys.argv[1]
    tour = sys.argv[2]
    type_j1 = sys.argv[3]
    type_j2 = sys.argv[4]

    chemin = path+"/src/"+type_j1+".py"
    if not os.path.exists(chemin):
        print('Usage: Vous devez écrire le nom exacte du type de joueur (bot1/bot2/joueur)')
        exit()
    chemin = path+"/src/"+type_j2+".py"
    if not os.path.exists(chemin):
        print('Usage: Vous devez écrire le nom exacte du type de joueur (bot1/bot2/joueur)')
        exit()

    print(port, tour, type_j1, type_j2)
    server = Thread(target=server, args=(port, tour))
    server.start()

    #for i in range(0,2):
    bot2 = Thread(target=j1, args=(port, type_j1))
    bot2.start()

    bot3 = Thread(target=j2, args=(port, type_j2))
    bot3.start()