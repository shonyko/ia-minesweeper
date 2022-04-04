if False:
    from lib.Processing3 import *


# Clasa pentru desenarea butonului si interactionarea lui cu mouse-ul
class Button:
    def __init__(self, x, y, rateX, rateY, color, txt):
        self.x = x
        self.y = y
        self.rateX = rateX
        self.rateY = rateY
        self.color = color
        self.txt = txt
        self.selected = False

    def draw(self):
        fill(self.color) if not self.selected else fill(self.color + 40)
        rect(self.x, self.y, width * self.rateX, height * self.rateY, 20)
        textSize(10)
        fill(0)
        text(self.txt, self.x - 20 + (width * self.rateX) / 2, self.y + (height * self.rateY) / 2)

    def inside(self, x, y):
        return self.x <= x <= self.x + width * self.rateX and self.y <= y <= self.y + height * self.rateY

    def selectIfInside(self, x, y):
        if self.inside(x, y):
            self.selected = True
        else:
            self.selected = False


# Clasa container pentru buttoane cu titlu
class Menu:
    def __init__(self, txt, textX, textY):
        self.txt = txt
        self.textX, self.textY = textX, textY
        self.state = None
        self.buttons = []

    def draw(self):
        textSize(30)
        text(self.txt, self.textX - 32, self.textY)
        for button in self.buttons:
            button.draw()

    def addButton(self, button):
        self.buttons.append(button)

    def mouseEnteredButton(self, x, y):
        for button in self.buttons:
            button.selectIfInside(x, y)

    def handleMousePressed(self, x, y):
        for i in range(len(self.buttons)):
            if self.buttons[i].inside(x, y):
                clb = self.state[i]
                clb()
                return

    def addConstraint(self, state):
        self.state = state


# Clasa care ajuta la construirea unui meniu mai usor
class MenuBuilder:
    def __init__(self, txt, x, y):
        self.menu = Menu(txt, x, y)

    def withButton(self, button):
        self.menu.addButton(button)
        return self

    def addConstraint(self, state):
        self.menu.addConstraint(state)
        return self

    def construct(self):
        return self.menu

    @staticmethod
    def createMenu(txt, x, y):
        return MenuBuilder(txt, x, y)