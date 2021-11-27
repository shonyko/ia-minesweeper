import os
import subprocess

if False:
    from lib.Processing3 import *

di = [-1, 1, 0, 0, -1, 1, -1, 1]
dj = [0, 0, -1, 1, -1, -1, 1, 1]


def calculatePonders(matrix, dimension):
    for i in range(dimension):
        for j in range(dimension):
            if matrix[i][j][1] != -1:
                nbBombs = 0
                for v in range(len(di)):
                    (vi, vj) = (i + di[v], j + dj[v])
                    if 0 <= vi < dimension and 0 <= vj < dimension and matrix[vi][vj][1] == -1:
                        nbBombs = nbBombs + 1
                matrix[i][j] = (False, nbBombs)


def readFromFile(filePath, dimension):
    matrix = []
    with open(filePath) as f:
        lines = f.readlines()
        for i in range(dimension):
            matrix.append([])
            line = lines[i]
            for j in range(dimension):
                if line[j] == '*':
                    matrix[i].append((False, 0))
                else:
                    matrix[i].append((False, -1))
    return matrix


global unused


class Grid:
    def __init__(self, dimension, mapFilePath, bombImage):
        self.dimension = dimension
        self.matrix = readFromFile(mapFilePath, dimension)
        calculatePonders(self.matrix, dimension)

        self.widthRate = width / self.dimension
        self.heightRate = height / self.dimension

        self.bombImage = bombImage

    def draw(self):
        for i in range(self.dimension):
            for j in range(self.dimension):
                strokeWeight(3)
                discovered, code = self.matrix[i][j]
                
                if not discovered:
                    if code == -2:
                        fill(255, 0, 0)
                    else:
                        fill(80, 80, 80)
                else:
                    fill(110, 110, 110)

                rect(j * self.widthRate, i * self.heightRate, self.widthRate, self.heightRate)

                if discovered:
                    if code >= 0:
                        fill(250, 250, 250)
                        textWidth("20")
                        text(str(code), j * self.widthRate + self.widthRate / 2,
                             i * self.heightRate + self.heightRate / 2)
                    else:
                        image(self.bombImage, j * self.widthRate, i * self.heightRate, self.widthRate, self.heightRate)

    def _inside(self, i, j, mousex, mousey):
        return j * self.widthRate <= mousex < (j + 1) * self.widthRate and i * self.heightRate <= mousey < (
                i + 1) * self.heightRate

    def handleMousePressed(self, mousex, mousey):
        global unused
        unused = [[True for j in range(self.dimension)] for i in range(self.dimension)]

        for i in range(self.dimension):
            for j in range(self.dimension):
                if self._inside(i, j, mousex, mousey):
                    if self.matrix[i][j] >= 0 and not self.matrix[i][j][0]:
                        unused[i][j] = False
                        self.matrix[i][j] = (True, self.matrix[i][j][1])
                        if self.matrix[i][j][1] == 0:
                            setZeroToTrue(self.matrix, (i, j), self.dimension)
                        break

    def __str__(self):
        result = ""
        for i in range(self.dimension):
            for j in range(self.dimension):
                result += str(self.matrix[i][j][1]) + "  "
            result += "\n"
        return result


def setZeroToTrue(matrix, start, n):
    (x, y) = start
    for v in range(len(di)):
        (vi, vj) = (x + di[v], y + dj[v])
        if 0 <= vi < n and 0 <= vj < n and unused[vi][vj] and not matrix[vi][vj][0]:
            unused[vi][vj] = False
            if matrix[vi][vj][1] == 0:
                matrix[vi][vj] = (True, 0)
                setZeroToTrue(matrix, (vi, vj), n)
            elif matrix[vi][vj][1] > 0:
                matrix[vi][vj] = (True, matrix[vi][vj][1])


class P9Convertor:
    def __init__(self, matrix):
        self.matrix = matrix
        self.size = len(matrix)
        self.scriptFormat = '''
clear(print_models).
set(arithmetic).
assign(max_models, -1).
%domain size
assign(domain_size, {0}). 

formulas(rules_minesweeper).
%s si p
{2} 

mine(x, y) = 1 | mine(x, y) = 0.
f(x, y) != 0 -> mine(x, y) = 0.

f(x, y) != 0 -> mine(p(x),p(y)) + mine(p(x),y) + mine(p(x),s(y)) + mine(x,p(y)) +
   mine(x,s(y)) + mine(s(x),p(y)) + mine(s(x),y) + mine(s(x),s(y)) = f(x,y).

all y mine(0, y) = 0.
all y mine({1}, y) = 0.
all x mine(x, 0) = 0.
all x mine(x, {1}) = 0.

%nu-s mine unde e zero
{3} 
%unde sunt mine?
{4} 
%teorema
{5}
end_of_list.
formulas(map_minesweeper).
%harta
{6}
end_of_list.
        '''

    # 2
    def _getP9SuccPred(self):
        succFormat = "s({0})={1}."
        predFormat = "p({0})={1}."

        n = self.size + 2

        str = ""
        for i in range(n):
            str += succFormat.format(i, (i + 1) % n)
        
        str += "\n"

        for i in range(n):
            str += predFormat.format(i, n - 1 if i == 0 else i - 1)

        return str

    # 6
    def _getP9Map(self):
        cellFormat = "f({0},{1})={2}."
        map = ""

        n = self.size + 2

        # bordura frate
        for i in range(n):
            map += cellFormat.format(i, 0, 0)
            map += cellFormat.format(i, n - 1, 0)

            if i == 0 or i == n - 1: continue

            map += cellFormat.format(0, i, 0)
            map += cellFormat.format(n - 1, i, 0)

        # restu
        map += "\n"
        for i in range(self.size):
            map += "\n"
            line = self.matrix[i]
            for j in range(len(line)):
                discovered, code = line[j]
                map += cellFormat.format(i + 1, j + 1, code if discovered else 0)

        return map

    # 4
    def _getP9MineMap(self):
        strFormat = "mine({0},{1})=1."
        str = ""

        for i in range(self.size):
            line = self.matrix[i]
            for j in range(len(line)):
                discovered, code = line[j]
                if not discovered and code == -2:
                    str += strFormat.format(i + 1, j + 1)

        return str

    # 3
    def _getP9SafeMap(self):
        strFormat = "mine({0},{1})=0."
        str = ""

        for i in range(self.size):
            line = self.matrix[i]
            for j in range(len(line)):
                discovered, nbOfMines = line[j]
                if discovered and nbOfMines == 0:
                    str += strFormat.format(i + 1, j + 1)

        return str

    def getP9Script(self):
        pass

    def generateScript(self, to_prove):
        n = self.size + 2

        theorem = ""
        if to_prove is not None:
            i, j, value = to_prove
            theorem = "mine({0},{1})={2}.".format(i + 1, j + 1, value)
        
        return self.scriptFormat.format(n, n - 1, self._getP9SuccPred(), self._getP9SafeMap(), self._getP9MineMap(), theorem, self._getP9Map())
    
class EAGame:
    def __init__(self, matrix, convertor):
        self.matrix = matrix
        self.convertor = convertor

    def verifyTheorem(self, script):
        path = "./temps/script.txt"
        print("brrrr")
        if os.path.exists(path):
            print("brrrr2")
            os.remove(path)

        print("brrrr3")
        with open(path, "w") as f:
            f.write(script)

        result = subprocess.check_output(["mace4", "-f", path])
        print(result)
        return "Exiting with failure." in result

    def isLose(self):
        lines = self.matrix
        for line in lines:
            if(len(list(filter(lambda tuple: tuple[0] and tuple[1] == -1, line)))):
                return True
        
        return False

    def isWin(self):
        lines = self.matrix
        for line in lines:
            if(len(list(filter(lambda tuple: tuple[1] == -1, line)))):
                return False
        
        return True

    def move(self):
        chestie_bombastica_cu_titirez_cu_propulsie_nucleara_automata = []
        n = len(self.matrix)
        for i in range(n):
            for j in range(n):
                discovered, code = self.matrix[i][j]

                if not discovered and code != -2:
                    chestie_bombastica_cu_titirez_cu_propulsie_nucleara_automata.append((i, j))

                    # verificam daca nu e mina
                    script = self.convertor.generateScript((i, j, 1))
                    if self.verifyTheorem(script):
                        self.matrix[i][j] = (True, self.matrix[i][j][1])
                        return

                    # verificam daca e mina
                    script = self.convertor.generateScript((i, j, 0))
                    if self.verifyTheorem(script):
                        if self.matrix[i][j][1] != -1:
                            print("Hahah n-ai ales mina fraiere")

                        self.matrix[i][j] = (False, -2)
                        return
            
            import random
            idx = random.randrange(0, len(chestie_bombastica_cu_titirez_cu_propulsie_nucleara_automata))
            i, j = chestie_bombastica_cu_titirez_cu_propulsie_nucleara_automata[idx]
            _, code = self.matrix[i][j]
            self.matrix[i][j] = (True, code)
            

                    
