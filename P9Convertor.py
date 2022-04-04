global scriptFormat

# template de script care va fi trimis catre Mace4

scriptFormat = '''clear(print_models).
set(arithmetic).
assign(max_seconds, 1).
assign(max_models, 1).
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


# Clasa raspunzatoare pentru convertirea si enuntarea teoremelor de rationare
# in legatura cu pozitia minelor pe tabla de joc intr-un limbaj
# pe care Mace4 il accepta!
class P9Convertor:
    def __init__(self, matrix):
        self.matrix = matrix
        self.size = len(matrix)
        global scriptFormat
        self.scriptFormat = scriptFormat

    def setMatrix(self, matrix):
        self.matrix = matrix
        self.size = len(matrix)

    # Locul 2 in script,
    # returneaza scriptul pentru functiile succesor si predecesor!
    def _getP9SuccPred(self):
        succFormat = "s({0})={1}."
        predFormat = "p({0})={1}."
        n = self.size + 2
        succPredScript = ""
        for i in range(n):
            succPredScript += succFormat.format(i, (i + 1) % n)
        succPredScript += "\n"
        for i in range(n):
            succPredScript += predFormat.format(i, n - 1 if i == 0 else i - 1)
        return succPredScript

    # Locul 6 in script,
    # returneaza scriptul cu functia de pondere pentru fiecare pozitie de pe tabla de joc
    def _getP9Map(self):
        cellFormat = "f({0},{1})={2}."
        mapScript = ""
        n = self.size + 2

        # bordura de joc
        for i in range(n):
            mapScript += cellFormat.format(i, 0, 0)
            mapScript += cellFormat.format(i, n - 1, 0)
            if i == 0 or i == n - 1: continue
            mapScript += cellFormat.format(0, i, 0)
            mapScript += cellFormat.format(n - 1, i, 0)

        # tabla de joc propriu-zisa
        mapScript += "\n"
        for i in range(self.size):
            mapScript += "\n"
            line = self.matrix[i]
            for j in range(len(line)):
                discovered, code = line[j]
                mapScript += cellFormat.format(i + 1, j + 1, code if discovered else 0)

        return mapScript

    # Locul 4 in script,
    # returneaza pozitiile cu mine regaiste deja de agent
    def _getP9MineMap(self):
        strFormat = "mine({0},{1})=1."
        mineMapScript = ""
        for i in range(self.size):
            line = self.matrix[i]
            for j in range(len(line)):
                discovered, code = line[j]
                if not discovered and code == -2:
                    mineMapScript += strFormat.format(i + 1, j + 1)
        return mineMapScript

    # Locul 3 in script,
    # returneaza harta minelor care au ponderea zero si sunt celule descoperite deja
    def _getP9SafeMap(self):
        strFormat = "mine({0},{1})=0."
        mineMapScript = ""

        n = self.size + 2

        # pe borduri
        for i in range(n):
            mineMapScript += strFormat.format(i, 0)
            mineMapScript += strFormat.format(i, n - 1)
            if i == 0 or i == n - 1: continue
            mineMapScript += strFormat.format(0, i)
            mineMapScript += strFormat.format(n - 1, i)
        mineMapScript += "\n"

        # inauntru
        for i in range(self.size):
            line = self.matrix[i]
            for j in range(len(line)):
                discovered, nbOfMines = line[j]
                if discovered and nbOfMines == 0:
                    mineMapScript += strFormat.format(i + 1, j + 1)
        return mineMapScript

    # generarea scriptului final, care primeste ca parametru o tupla (i, j, value)
    # unde (i, j) reprezinta pozitia la care nu vreau (value = 1) sau vreau (value = 0)
    # sa demonstrez ca exista mina
    def generateScript(self, to_prove):
        n = self.size + 2
        theorem = ""
        if to_prove is not None:
            i, j, value = to_prove
            theorem = "mine({0},{1})={2}.".format(i + 1, j + 1, value)
        return self.scriptFormat.format(n, n - 1, self._getP9SuccPred(), self._getP9SafeMap(), self._getP9MineMap(),
                                        theorem, self._getP9Map())
