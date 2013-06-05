# -*- coding: utf-8 -*-
#  PasswordEnter.py
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

from PyQt4.QtGui import QDialog, QLabel, \
						QVBoxLayout, QHBoxLayout, \
						QPushButton, QIcon, QLineEdit, \
						QMessageBox
from PyQt4.QtCore import QStringList, Qt, QTimer
from KeyringStuff import *

class PasswordEnter(QDialog):
	def __init__(self, title = '', parent = None, mode = 1):
		QDialog.__init__(self, parent)
		self.prnt = parent
		self.mode = mode
		self.tr = self.prnt.tr
		self.Sound = self.prnt.Parent.sound
		self.Keyring = self.prnt.Keyring
		self.title = QLabel(self.tr._translate(title))
		self.title.setAlignment(Qt.AlignHCenter)
		self.passwrd = QLineEdit()
		self.passwrd.setMaxLength(BLOCK_SIZE)
		self.passwrd.setPlaceholderText(self.tr._translate("Enter Password"))
		self.passwrd.setEchoMode(QLineEdit.Password)
		self.passwrd.setToolTip(self.tr._translate("Enter Password"))
		if self.mode :
			self.confirm = QLineEdit()
			self.confirm.setMaxLength(BLOCK_SIZE)
			self.confirm.setPlaceholderText(self.tr._translate("Confirm Password"))
			self.confirm.setEchoMode(QLineEdit.Password)
			self.confirm.setToolTip(self.tr._translate("Confirm it"))

		self._layout = QVBoxLayout()
		self._layout.addWidget(self.title)
		self._layout.addWidget(self.passwrd)
		if self.mode :
			self._layout.addWidget(self.confirm)
		self.ok = QPushButton(QIcon.fromTheme("dialog-ok"), "", self)
		self.cancel = QPushButton(QIcon.fromTheme("dialog-cancel"), "", self)
		self.buttonLayout = QHBoxLayout()
		self.buttonLayout.addWidget(self.ok)
		self.buttonLayout.addWidget(self.cancel)
		self._layout.addItem(self.buttonLayout)
		self.setLayout(self._layout)
		if self.mode :
			self.ok.clicked.connect(self.checkCorrectOfPassword)
		else :
			self.ok.clicked.connect(self.returnPassword)
		self.cancel.clicked.connect(self.clearEnterFields)
		self.parentVisibilityState = \
			(self.prnt.Parent.isVisible(), \
			self.prnt.Parent.isMinimized(), \
			self.prnt.Parent.isMaximized())
		QTimer.singleShot(100, self.moveToTrayIcon)

	def moveToTrayIcon(self):
		self.move(self.prnt.Parent.mapToGlobal(self.prnt.Parent.trayIconMenu.pos()))

	def checkCorrectOfPassword(self):
		if self.confirm.text() == self.passwrd.text() and \
				not self.confirm.text().isEmpty() :
			self.Keyring.create_Keyring(self.passwrd.text())
			self.Sound.Complete.play()
			QMessageBox.information(self, \
					self.tr._translate("Create Keyring"), \
					self.tr._translate("Keyring created."), \
					1)
			self.clearEnterFields()
			self.prnt.saveData()
			self.done(0)
		else :
			self.Sound.Attention.play()
			QMessageBox.information(self, \
					self.tr._translate("Create Keyring"), \
					self.tr._translate("Passwords mismatch or empty"), \
					1)
			self.clearEnterFields()

	def clearEnterFields(self):
		self.passwrd.clear()
		if self.mode :
			self.confirm.clear()

	def returnPassword(self):
		if not self.passwrd.text().isEmpty() :
			self.prnt.Keyring.password = to_unicode(self.passwrd.text())
			self.clearEnterFields()
			self.close()
		else :
			self.Sound.Attention.play()
			QMessageBox.information(self, \
					self.tr._translate("Enter Password"), \
					self.tr._translate("Passwords empty"), \
					1)

	def closeEvent(self, ev):
		#self.prnt.Parent.show()
		ev.ignore()
		if not self.parentVisibilityState[0] :
			self.prnt.Parent.autoHide(3)
		elif not self.parentVisibilityState[1] and not self.parentVisibilityState[2] :
			self.prnt.Parent.showNormal()
		elif self.parentVisibilityState[1] : self.prnt.Parent.showMinimized()
		else : self.prnt.Parent.showMaximized()
		self.done(0)
