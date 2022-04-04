import random

BOMB_SYMBOL = 'B'
EMPTY_SYMBOL = '*'


class ActionType:
    DISCOVER = 0
    MARK = 1


di = [-1, -1, -1, 0, 1, 1, 1, 0]
dj = [-1, 0, 1, 1, 1, 0, -1, -1]

# Clasa raspunzatoare cu logica de joc, citirea din fisier, generare random de matrice cu bombe
# si calcularea ponderilor!
class MinesweeperState:
    def __init__(self, path=None, n=None):
        self.initialized = False

        self.path = path

        self._initializeGameVariables()

        if path is not None:
            self._readFromFile()
        else:
            if n is not None:
                self._generateRandomMatrix(n)
            else:
                print("configuratie incorecta!")

        self._computeCodes()
        self.lose = False

        self.copyMatrix = self._matrixCopy()
        self.markedCount = 0

        self.unused = [[True for j in range(self.sizeX)] for i in range(self.sizeY)]

    # avem nevoie de copie a matricei initiale
    # pentru atunci cand userul vrea sa dea unflag,
    # revenind astfel la o stare trecuta a harti de joc
    def _matrixCopy(self):
        return [[self.matrix[i][j] for j in range(self.sizeX)] for i in range(self.sizeY)]

    #generarea aleatoare a unei harti cu intre 12%-17% din diminesiunea ei
    # fiind reprezentate de bombe
    def _generateRandomMatrix(self, n):
        size = n * n
        nbBombs = random.randrange(int(size * 0.12), int(size * 0.17))
        self.noBombs = nbBombs

        self.matrix = [[(False, 0) for i in range(n)] for j in range(n)]

        while nbBombs:
            i, j = random.randrange(0, n), random.randrange(0, n)
            (_, code) = self.matrix[i][j]
            if code == 0:
                self.matrix[i][j] = (False, -1)
                nbBombs = nbBombs - 1

        self.sizeX = self.sizeY = n
        self._buildBorderdMatrix()

    def _initializeGameVariables(self):
        if self.initialized: return

        self.sizeX = self.sizeY = 0
        self.noBombs = self.noDiscoveredBombs = 0

        self.initialized = True

    # citirea din fisier a unei harti, care poate sa aiba dimensiuni diferite
    # (nu doar matrice patratica)
    def _readFromFile(self):
        matrix = []

        with open(self.path) as f:
            lines = f.readlines()

        if lines is None or len(lines) <= 0:
            print("ERROR: An error occured while reading the map from file.")

        self.sizeY = len(lines)
        for char in lines[0]:
            if char.isspace(): continue
            self.sizeX += 1

        for line in lines:
            matrixLine = []
            for char in line:
                if char.isspace(): continue

                if char == EMPTY_SYMBOL:
                    matrixLine.append((False, 0))
                elif char == BOMB_SYMBOL:
                    matrixLine.append((False, -1))
                    self.noBombs += 1
                else:
                    print("WARNING: Unknown character in map.")

            matrix.append(matrixLine)

        self.matrix = matrix
        self._buildBorderdMatrix()

    #matricea bordata, care ajuta a simplificarea logicii de joc
    def _buildBorderdMatrix(self):
        if not hasattr(self, "_verticalBorder"):
            self._verticalBorder = []
            for i in range(self.sizeX + 2):
                self._verticalBorder.append((False, 0))

        self.borderedMatrix = []
        self.borderedMatrix.append(self._verticalBorder)

        for line in self.matrix:
            self.borderedMatrix.append([(False, 0)] + line + [(False, 0)])

        self.borderedMatrix.append(self._verticalBorder)

    #calcularea ponderilor
    def _computeCodes(self):
        for i in range(1, self.sizeY + 1):
            for j in range(1, self.sizeX + 1):
                if self.matrix[i - 1][j - 1][1] == -1: continue

                nbBombs = 0
                for v in range(len(di)):
                    (vi, vj) = (i + di[v], j + dj[v])
                    nbBombs = nbBombs + (self.borderedMatrix[vi][vj][1] == -1)

                self.matrix[i - 1][j - 1] = (False, nbBombs)

        self._buildBorderdMatrix()

    def _inside(self, pos):
        i, j = pos
        return 0 <= i < self.sizeY and 0 <= j < self.sizeX

    def _discoverCell(self, pos):
        i, j = pos

        if not self.unused[i][j]: return

        _, code = self.matrix[i][j]
        self.unused[i][j] = False
        self.matrix[i][j] = (True, code)

        if code == -1:
            self.lose = True

        if code == 0:
            for v in range(len(di)):
                vi, vj = i + di[v], j + dj[v]
                if not self._inside((vi, vj)): continue
                self._discoverCell((vi, vj))

        self._buildBorderdMatrix()

    def _markCell(self, pos):
        i, j = pos
        discovered, code = self.matrix[i][j]

        if discovered:
            return

        bypass = False
        newValue = (False, -2)
        if code == -2:
            newValue = self.copyMatrix[i][j]
            self.noDiscoveredBombs -= self.copyMatrix[i][j] == -1
            self.markedCount -= code == -2
            bypass = True

        if not bypass and self.markedCount >= self.noBombs:
            return

        self.matrix[i][j] = newValue
        self.markedCount += int(code != -2)
        self.noDiscoveredBombs += int(code == -1)

    def handleMove(self, type, pos):
        if type == ActionType.DISCOVER:
            self._discoverCell(pos)
        elif type == ActionType.MARK:
            self._markCell(pos)
        else:
            # raise TypeError('nu anteleg')
            print("WARNING: Unknown move type: " + str(type) + ".")

    def isLose(self):
        return self.lose
        # lines = self.matrix
        # for line in lines:
        #     if len(list(filter(lambda tuple: tuple[0] and tuple[1] == -1, line))) > 0:
        #         return True
        # return False

    def isWin(self):
        return self.noBombs == self.noDiscoveredBombs

    def __str__(self):
        result = ""
        for i in range(self.sizeY):
            for j in range(self.sizeX):
                result += str(self.matrix[i][j][1]) + "  "
            result += "\n"
        return result
