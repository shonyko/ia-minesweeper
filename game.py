from Grid import Grid
from Grid import P9Convertor
from Grid import EAGame

import time

if False:
    from lib.Processing3 import *

global grid
global convertor
global game

def setup():
    size(600, 600)
    # fullScreen()

    global grid
    bomb = loadImage("img/bomb.png")

    grid = Grid(9, "maps/map.txt", bomb)
    print(grid)

    global convertor
    convertor = P9Convertor(grid.matrix)

    global game
    game = EAGame(grid.matrix, convertor)

def draw():
    grid.draw()
    game.move()
    time.sleep(1)
    print(game.isWin())
    
    


def mousePressed():
    grid.handleMousePressed(mouseX, mouseY)
