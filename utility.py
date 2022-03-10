from PyQt5.QtCore import *
from os.path import join, isfile
from paths import *
import os, pickle


def getOnlineTiles():
    file = open(ONLINE_TILES, 'r')
    tiles = {}
    for line in file:
        tiles[line.split('=')[0].strip()] = '"' + line.split('=')[1].strip() + '"'

    return tiles

def getTileInfo(tile, mode):
    if mode == 'Offline':
        zLevels = [int(z_l) for z_l in os.listdir(join(TILES_DIR, tile)) if z_l.isnumeric()]
        zLevels.sort()
        tilesPath = QUrl.fromLocalFile(join(TILES_DIR, tile)).toString()
        tilesPath = '"' + tilesPath + '/{z}/{x}/{y}.png"'
        return tilesPath, zLevels[0], zLevels[-1]
    else:
        tilesJson = getOnlineTiles()
        return tilesJson[tile], 2, 18


def loadConfigs():
    if not isfile(CONFIG_FILE):
        configs = {
            'systemFont': ['Segoe UI', 12],
            'tilesMode' : 'Offline',
            'currentTile': 'JAWG Matrix',
            'offlineTilesIndex': 0,
            'onlineTilesIndex': 0,
            'iranView': [[41.27780646738183, 70.26855468750001], 
                         [23.46324633155036, 36.82617187500001]],
            'lastBounds': [[0, 0], [0, 0]],
            'viewMode': 'no focus',
            'startupView': 'Iran',
            'viewType': 'static',
        }
        file = open(CONFIG_FILE, 'wb')
        pickle.dump(configs, file)
    else:
        file = open(CONFIG_FILE, 'rb')
        configs = pickle.load(file)

    return configs


def saveConfigs(configs):
    file = open(CONFIG_FILE, 'wb')
    pickle.dump(configs, file)
