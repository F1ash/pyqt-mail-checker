#!/usr/bin/python 
# -*- coding: utf-8 -*-

import sys, os.path
app_dir = os.path.join("/usr/share", "pyqt-mail-checker")
sys.path.insert(0, app_dir)
from PyQt4.QtGui import QApplication
from mainWindow import MainWindow

app = QApplication(sys.argv)
d = app.desktop()
main = MainWindow(d)
sys.exit(app.exec_())

