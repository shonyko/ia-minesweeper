import os
import random
import subprocess

from Map import ActionType


class AgentType:
    AI = 0
    HUMAN = 1


# rezultatul pe care-l intoarce Mace4 corespondent cu FALS-ul din metoda reducerii
# la absurd
FALS = "Exiting with failure."


# Clasa care se ocupa cu comunicarea scriptului catre Mace4 si executarea
# miscarilor in functie de rezultatul primit de la teorema enuntata!
class AIAgent:
    def __init__(self, map, convertor, agentType=AgentType.AI):
        self.map = map
        self.convertor = convertor
        self.DEVNULL = open(os.devnull, 'wb')

        self.type = agentType

    # trimite scriptul cu teorema catre Mace4 care o executa si
    # care intoarce un rezultat.
    # metoda returneaza true daca teorema a fost demonstrata
    def verifyTheorem(self, script):
        path = "./temps/script.in"

        if os.path.exists(path):
            os.remove(path)

        with open(path, "w") as f:
            f.write(script)

        temp = subprocess.Popen(["mace4", "-f", path], stdout=subprocess.PIPE, stderr=self.DEVNULL)
        output, errors = temp.communicate()

        return FALS in output.decode('utf-8')
    
    #itereaza peste harta si se opreste la prima celula desecoperita
    # in care poate demonstra ca fie este o mina, fie ca e libera
    # daca ajunge la final si nu poate demonstra nimic, alege random o pozitie
    # pe care o descopera
    def move(self):
        chestie_bombastica_cu_titirez_cu_propulsie_nucleara_automata = []

        for i in range(self.map.sizeY):
            for j in range(self.map.sizeX):
                if not self.map.unused[i][j]: continue

                discovered, code = self.map.matrix[i][j]
                if not discovered and code != -2:
                    chestie_bombastica_cu_titirez_cu_propulsie_nucleara_automata.append((i, j))
                    # verificam daca nu e mina
                    script = self.convertor.generateScript((i, j, 1))
                    if self.verifyTheorem(script):
                        self.map.handleMove(ActionType.DISCOVER, (i, j))
                        return
                    # verificam daca e mina
                    script = self.convertor.generateScript((i, j, 0))
                    if self.verifyTheorem(script):
                        if self.map.matrix[i][j][1] != -1:
                            print("Hahah n-ai ales mina fraiere")
                        self.map.handleMove(ActionType.MARK, (i, j))
                        return

        lgth = len(chestie_bombastica_cu_titirez_cu_propulsie_nucleara_automata)
        if lgth != 0:
            idx = random.randrange(0, lgth)
            i, j = chestie_bombastica_cu_titirez_cu_propulsie_nucleara_automata[idx]
            self.map.handleMove(ActionType.DISCOVER, (i, j))