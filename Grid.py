from Map import ActionType

if False:
    from lib.Processing3 import *


# Clasa care se ocupa cu desenarea pe ecran
# a tablei de joc in diferitele ei stari
class Grid:
    def __init__(self, map, bombImage, flag):
        self.bombImage = bombImage
        self.flag = flag

        self.map = None
        self.widthRate = None
        self.heightRate = None

        self.setMap(map)

    def setMap(self, map):
        self.map = map
        self.widthRate = width / self.map.sizeX
        self.heightRate = height / self.map.sizeY

    # deseneaza tabla de joc!
    def draw(self):
        for i in range(self.map.sizeY):
            for j in range(self.map.sizeX):
                strokeWeight(3)
                discovered, code = self.map.matrix[i][j]

                if code == -2:
                    fill(255, 0, 0)
                    image(self.flag, j * self.widthRate, i * self.heightRate, self.widthRate, self.heightRate)
                else:
                    if not discovered:
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

    # testeaza daca mouse-ul este in interiorul unei celule de la pozitia (i, j)
    def _inside(self, i, j, mousex, mousey):
        return j * self.widthRate <= mousex < (j + 1) * self.widthRate and i * self.heightRate <= mousey < (
                i + 1) * self.heightRate

    # metoda care executa miscarea de descoperire unor celule
    # sau de macare declansata de mouse
    def handleMousePressed(self, mousex, mousey, mouseButton):
        for i in range(self.map.sizeY):
            for j in range(self.map.sizeX):
                if self._inside(i, j, mousex, mousey):
                    if mouseButton == LEFT:
                        self.map.handleMove(ActionType.DISCOVER, (i, j))
                    else:
                        self.map.handleMove(ActionType.MARK, (i, j))

    def __str__(self):
        result = ""
        for i in range(self.map.sizeY):
            for j in range(self.map.sizeX):
                result += str(self.map.matrix[i][j][1]) + "  "
            result += "\n"
        return result