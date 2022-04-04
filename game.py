import time

from AIAgent import AIAgent
from GUI import MenuBuilder, Button
from Grid import Grid
from MinesweeperState import MinesweeperState
from P9Convertor import P9Convertor

if False:
    from lib.Processing3 import *

# logics stuff
global gameMap, grid, convertor, agent

# state staff
global currentState, currentMenu

# gui for state
global playerMenu, mapMenu, winMenu, loseMenu


# callbacks from GUI

def initPlayerState():
    global agent, gameMap, convertor
    agent = AIAgent(gameMap, convertor)
    global currentState
    currentState = GameState.PLAY
    drawBackground()


def aiPlayer():
    initPlayerState()


def humanPlayer():
    global currentState, currentMenu, agent
    agent = None
    currentMenu = None
    currentState = GameState.PLAY
    drawBackground()


def initMapState(n):
    global gameMap, convertor, grid
    gameMap = MinesweeperState(None, n) if n is not None else MinesweeperState("maps/map.txt")
    grid.setMap(gameMap)
    convertor.setMatrix(gameMap.matrix)

    global currentState, currentMenu, playerMenu
    currentState = GameState.SELECT_PLAYER
    currentMenu = playerMenu
    drawBackground()


def nineXnine():
    initMapState(9)


def twelveXtwelve():
    initMapState(12)


def sixteenXsixteen():
    initMapState(16)


def win():
    global currentState, currentMenu, winMenu
    currentState = GameState.WIN
    currentMenu = winMenu


def lose():
    global currentState, currentMenu, loseMenu
    currentState = GameState.LOSE
    currentMenu = loseMenu


def fromFile():
    initMapState(None)


def restart():
    global currentState, currentMenu, mapMenu
    currentState = GameState.SELECT_MAP
    currentMenu = mapMenu
    drawBackground()


class GameState:
    subGameState = {
        "aiPlayerFun": aiPlayer,
        "humanPlayerFun": humanPlayer,
        "9x9Fun": nineXnine,
        "12x12Fun": twelveXtwelve,
        "16x16Fun": sixteenXsixteen,
        "fromFileFun": fromFile,
        "restartFun": restart
    }

    SELECT_PLAYER = [subGameState.get("aiPlayerFun"), subGameState.get("humanPlayerFun")]
    SELECT_MAP = [subGameState.get("9x9Fun"), subGameState.get("12x12Fun"), subGameState.get("16x16Fun"),
                  subGameState.get("fromFileFun")]
    LOSE = [subGameState.get("restartFun")]
    WIN = [subGameState.get("restartFun")]
    PLAY = []


global backgroundImage


def setup():
    size(600, 600)
    # fullScreen()
    bomb = loadImage("img/bomb.png")
    flag = loadImage("img/flag.png")

    global backgroundImage
    backgroundImage = loadImage("img/grid.png")

    initGameLogic(bomb, flag)

    drawBackground()
    initGUI()

    # setarea starii initiale impreuna cu meniu-ul aferent
    global currentState, currentMenu
    currentState = GameState.SELECT_MAP
    currentMenu = mapMenu


def drawBackground():
    global backgroundImage

    image(backgroundImage, 0, 0, width, height)
    fill(155, 170)
    rect(0, 0, width, height)


def initGameLogic(bomb, flag):
    global gameMap
    gameMap = MinesweeperState("maps/map.txt")
    global grid
    grid = Grid(gameMap, bomb, flag)
    global convertor
    convertor = P9Convertor(gameMap.matrix)
    global agent
    agent = AIAgent(gameMap, convertor)


def initGUI():
    global playerMenu
    clr = color(82, 26, 102)
    playerMenu = MenuBuilder.createMenu("Choose player", width / 2.4, 40).withButton(
        Button(width / 4.5, height / 4.5, 0.5, 0.199, clr, "AI PLAYER")).withButton(
        Button(width / 4.5, height / 2.4, 0.5, 0.199, clr, "HUMAN PLAYER")).addConstraint(
        GameState.SELECT_PLAYER).construct()

    global mapMenu
    mapMenu = MenuBuilder.createMenu("Choose a grid", width / 2.4, 40).withButton(
        Button(width / 4.5, height / 4.5, 0.22, 0.18, clr, "9x9")).withButton(
        Button(width / 4.5, 2 * height / 4.5, 0.22, 0.18, clr, "12x12")).withButton(
        Button(2 * width / 4.5, height / 4.5, 0.22, 0.18, clr, "16x16")).withButton(
        Button(2 * width / 4.5, 2 * height / 4.5, 0.22, 0.18, clr, "From File")).addConstraint(
        GameState.SELECT_MAP).construct()

    global winMenu
    winMenu = MenuBuilder.createMenu("You won!", width / 2.5, 40).withButton(
        Button(width / 2.7, height / 3, 0.25, 0.199, clr, "Restart")
    ).addConstraint(GameState.WIN).construct()

    global loseMenu
    loseMenu = MenuBuilder.createMenu("You lose!", width / 2.5, 40).withButton(
        Button(width / 2.7, height / 3, 0.25, 0.199, clr, "Restart")
    ).addConstraint(GameState.LOSE).construct()


def draw():
    global currentMenu, currentState
    if currentMenu is not None:
        currentMenu.draw()

    if currentState == GameState.PLAY:

        grid.draw()

        if gameMap.isLose():
            fill(255, 192, 203, 70)
            rect(0, 0, width, height)
            lose()
        elif gameMap.isWin():
            fill(255, 192, 203, 70)
            rect(0, 0, width, height)
            win()
        elif agent is not None:
            agent.move()
            time.sleep(1)


def mousePressed():
    global currentMenu
    if currentMenu is not None:
        currentMenu.handleMousePressed(mouseX, mouseY)
    elif currentState == GameState.PLAY and agent is None:
        grid.handleMousePressed(mouseX, mouseY, mouseButton)


def mouseMoved():
    global currentMenu
    if currentMenu is not None:
        currentMenu.mouseEnteredButton(mouseX, mouseY)
