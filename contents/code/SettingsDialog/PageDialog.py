# -*- coding: utf-8 -*-
#  PageDialog.py
#  
#  Copyright 2013 Flash <kaperang07@gmail.com>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#

from PyQt4.QtGui import QDialog, QTabWidget, \
						QHBoxLayout, QVBoxLayout, \
						QPushButton, QIcon, \
						QSizePolicy
from PyQt4.QtCore import Qt, QString, QEvent, pyqtSignal, QTimer
from Translator import Translator

class PageDialog(QDialog):
	okClicked = pyqtSignal()
	cancelClicked = pyqtSignal()
	settingsCancelled = pyqtSignal()
	def __init__(self, parent = None):
		QDialog.__init__(self, parent)
		self.prnt = parent
		self.tr = Translator()
		self.setWindowTitle(self.tr._translate('M@il Checker : Settings'))
		self.tabWidget = QTabWidget(self)
		self.tabWidget.setTabPosition(QTabWidget.North)
		self.layout = QVBoxLayout()
		self.buttonLayout = QHBoxLayout()
		self.ok = QPushButton(QIcon.fromTheme("dialog-ok"), "", self)
		self.cancel = QPushButton(QIcon.fromTheme("dialog-cancel"), "", self)

		self.buttonLayout.addWidget(self.ok)
		self.buttonLayout.addWidget(self.cancel)
		self.layout.addWidget(self.tabWidget)
		self.layout.addItem(self.buttonLayout)
		self.setLayout(self.layout)
		self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
		self.setMinimumWidth(100)
		self.ok.clicked.connect(self.accepted)
		self.cancel.clicked.connect(self.rejected)
		QTimer.singleShot(100, self._restoreGeometry)

	def _restoreGeometry(self):
		self.restoreGeometry(self.prnt.Settings.value('SettingsGeometry').toByteArray())

	def addPage(self, wdg, wdgName):
		self.tabWidget.addTab(wdg, wdgName)

	def accepted(self): self.okClicked.emit()
	def rejected(self):
		self.settingsCancelled.emit()
		self.cancelClicked.emit()

	def closeEvent(self, ev):
		ev.ignore()
		self.rejected()

	def _close(self):
		self.prnt.Settings.setValue('SettingsGeometry', self.saveGeometry())
		if not self.prnt.isVisible() :
			self.prnt.show()
			self.prnt.autoHide(3)
		if self.prnt.isMinimized() :
			self.prnt.showNormal()
		self.done(0)
