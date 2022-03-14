from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PyQt5.uic import loadUi
from mapSettings import MapSettings
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from utility import *
import sys, json


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        loadUi(MAIN_WINDOW_UI, self)
        self.configs = loadConfigs()
        font = QFont(self.configs['systemFont'][0], self.configs['systemFont'][1])
        self.setFont(font)
        self.browser = QWebEngineView()
        self.browser.setPage(WebEnginePage())
        url = QUrl.fromLocalFile(HTML_FILE)
        self.browser.load(url)
        self.browser.loadFinished.connect(self.onMapLoad)
        self.mapLayout.addWidget(self.browser)
        self.mapSettingsWin = None
        self.initTimers()
        self.initButtons()
        self.initActions()
        file = open(DEMO_COORDINATES)
        json_array = json.load(file)
        self.coordinates = json_array['features'][0]['geometry']['coordinates']
    
    def initTimers(self):
        self.index = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.updateMarker)    

    def initActions(self):
        self.actionFonts.triggered.connect(self.openFontDialog)
        self.actionMap.triggered.connect(self.openMapSettings)

    def initButtons(self):
        self.btnStart.clicked.connect(lambda: self.timer.start(100))
        self.btnStop.clicked.connect(self.timer.stop)

    def onMapLoad(self):
        initLatLng = [42.354558431366236, -104.16602050552856]
        initZoomlevel = 2

        self.browser.page().runJavaScript(f"createMap({initLatLng[0]}, {initLatLng[1]}, {initZoomlevel})")

        viewType = '"' + self.configs['viewType'] + '"'
        if self.configs['startupView'] == 'Iran':
            bounds = self.configs['iranView']
        else:
            bounds = self.configs['lastBounds']

        self.browser.page().runJavaScript(f"initBounds({bounds}, {viewType})")

        self.initTiles()
        self.initRadioButtons()

    def initTiles(self):
        if isfile(ONLINE_TILES):
            try:
                onlineTiles = getOnlineTiles()    
                self.cmbOnlineTiles.insertItems(0, onlineTiles.keys())
            except Exception:
                self.cmbOnlineTiles.insertItems(0, [])

        offlineTiles = [tile for tile in os.listdir(TILES_DIR) if tile != '.gitignore']
        if 'OnlineTiles.txt' in offlineTiles:
            offlineTiles.remove('OnlineTiles.txt')

        self.cmbOfflineTiles.insertItems(0, offlineTiles)

        if 0 <= self.configs['onlineTilesIndex'] < self.cmbOnlineTiles.count():
            self.cmbOnlineTiles.setCurrentIndex(self.configs['onlineTilesIndex'])

        if 0 <= self.configs['offlineTilesIndex'] < self.cmbOfflineTiles.count():
            self.cmbOfflineTiles.setCurrentIndex(self.configs['offlineTilesIndex'])

        self.cmbOnlineTiles.currentTextChanged.connect(self.changeTile)
        self.cmbOfflineTiles.currentTextChanged.connect(self.changeTile)

    def initRadioButtons(self):
        self.rdbNoFocus.setChecked(True)

        self.rdbOfflineTiles.toggled.connect(self.setTilesMode)
        self.rdbOnlineTiles.toggled.connect(self.setTilesMode)
        self.rdbFocus.toggled.connect(self.setViewMode)
        self.rdbNoFocus.toggled.connect(self.setViewMode)

        if self.configs['tilesMode'] == 'Offline':
            self.rdbOfflineTiles.setChecked(True)
        else:
            self.rdbOnlineTiles.setChecked(True)

        if self.configs['viewMode'] == 'focus':
            self.rdbFocus.setChecked(True)
        else:
            self.rdbNoFocus.setChecked(True)

        if self.cmbOnlineTiles.count() == 0:
            self.rdbOnlineTiles.setEnabled(False)
            self.cmbOnlineTiles.setEnabled(False)

        if self.cmbOfflineTiles.count() == 0:
            self.rdbOfflineTiles.setEnabled(False)
            self.cmbOfflineTiles.setEnabled(False)

    def setTilesMode(self):
        if self.rdbOfflineTiles.isChecked():
            self.cmbOfflineTiles.setEnabled(True)
            self.cmbOnlineTiles.setEnabled(False)
            self.configs['tilesMode'] = 'Offline'
            self.changeTile(self.cmbOfflineTiles.currentText())
        else:
            self.cmbOfflineTiles.setEnabled(False)
            self.cmbOnlineTiles.setEnabled(True)
            self.configs['tilesMode'] = 'Online'
            self.changeTile(self.cmbOnlineTiles.currentText())

        saveConfigs(self.configs)

    def setViewMode(self):
        if self.rdbFocus.isChecked():
            self.configs['viewMode'] = 'focus'
        else:
            self.configs['viewMode'] = 'no focus'
        
        saveConfigs(self.configs)

    def changeTile(self, tile):
        mode = 'Offline' if self.rdbOfflineTiles.isChecked() else 'Online'
        offCondition = mode == 'Offline' and self.cmbOfflineTiles.count() != 0
        onCondition = mode == 'Online' and self.cmbOnlineTiles.count() != 0
        if onCondition or offCondition:
            tilesPath , min, max = getTileInfo(tile, mode)
            self.browser.page().runJavaScript(
                f"createTileLayer({tilesPath}, {min}, {max})"
            )
            self.configs['currentTile'] = tile
            self.configs['offlineTilesIndex'] = self.cmbOfflineTiles.currentIndex()
            self.configs['onlineTilesIndex'] = self.cmbOnlineTiles.currentIndex()
            saveConfigs(self.configs)

    def updateMarker(self):
        mode = "'no focus'" if self.rdbNoFocus.isChecked() else "'focus'"
        self.browser.page().runJavaScript(
            f"updateMarker({self.coordinates[self.index][1]}, {self.coordinates[self.index][0]}, {mode})"
        )
        if self.index == len(self.coordinates) - 1:
            self.index = 0
        self.index += 1

    def openMapSettings(self):
        if self.mapSettingsWin is None:
            self.mapSettingsWin = MapSettings(self, Qt.WindowCloseButtonHint)

        self.mapSettingsWin.show()

    def openFontDialog(self):
        font, ok = QFontDialog.getFont(self.font())
        if ok:
            self.setFont(font)
            if self.mapSettingsWin:
                self.mapSettingsWin.setFont(font)
            self.configs['systemFont'] = [font.family(), font.pointSize()]
            saveConfigs(self.configs)
            self.update()
            self.repaint()  

    def closeEvent(self, a0: QCloseEvent) -> None:
        self.timer.stop()
        self.browser.page().runJavaScript(
            "map.getBounds()", self.saveBounds
        )

    def saveBounds(self, bounds):
        try:
            bounds = [
                [bounds['_northEast']['lat'] ,bounds['_northEast']['lng']], 
                [bounds['_southWest']['lat'] ,bounds['_southWest']['lng']]
            ]
            self.configs['lastBounds'] = bounds
            saveConfigs(self.configs)
        except Exception:
            pass
            

class WebEnginePage(QWebEnginePage):
    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
        print(f"[JS Message] Line-{lineNumber}:",message)


def main():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.showMaximized()
    return app.exec_()


if __name__ == '__main__':
    sys.exit(main())