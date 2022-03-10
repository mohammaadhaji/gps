from PyQt5.QtWidgets import QDialog, QApplication
from PyQt5.uic import loadUi    
from paths import *
from utility import *


class MapSettings(QDialog):
    def __init__(self, *args, **kwargs):
        super(MapSettings, self).__init__(*args, **kwargs)
        loadUi(MAP_SETTINGS_UI, self)
        self.setFont(self.parent().font())
        self.setWidgets()
        self.buttonBox.clicked.connect(self.finish)
        

    def setWidgets(self):
        if self.parent().configs['viewType'] == 'static':
            self.rdbStatic.setChecked(True)
        else:
            self.rdbFly.setChecked(True)

        if self.parent().configs['startupView'] == 'Iran':
            self.rdbViewIran.setChecked(True)
        else:
            self.rdbLastView.setChecked(True)

    
    def finish(self, btn):
        if btn.text() == 'OK':
            if self.rdbStatic.isChecked():
                self.parent().configs['viewType'] = 'static'
            else:
                self.parent().configs['viewType'] = 'fly'

            if self.rdbViewIran.isChecked():
                self.parent().configs['startupView'] = 'Iran'
            else:
                self.parent().configs['startupView'] = 'lastView'

            saveConfigs(self.parent().configs)
        else:
            self.setWidgets()

        QApplication.processEvents()
        self.close()
