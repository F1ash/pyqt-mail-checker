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

from PyQt4.QtGui import QWidget, QLabel, \
						QVBoxLayout, QHBoxLayout, \
						QPushButton, QIcon, QLineEdit, \
						QMessageBox
from PyQt4.QtCore import QStringList, Qt

class PasswordEnter(QWidget):
	def __init__(self, title = '', parent = None):
		QWidget.__init__(self, parent)
		self.prnt = parent
		self.tr = self.prnt.tr
		self.Sound = self.prnt.Parent.sound
		self.Keyring = self.prnt.Keyring
		self.title = QLabel(self.tr._translate(title))
		self.title.setAlignment(Qt.AlignHCenter)
		self.passwrd = QLineEdit()
		self.passwrd.setPlaceholderText(self.tr._translate("Enter Password"))
		self.passwrd.setEchoMode(QLineEdit.Password)
		self.passwrd.setToolTip(self.tr._translate("Enter Password"))
		self.confirm = QLineEdit()
		self.confirm.setPlaceholderText(self.tr._translate("Confirm Password"))
		self.confirm.setEchoMode(QLineEdit.Password)
		self.confirm.setToolTip(self.tr._translate("Confirm it"))

		self._layout = QVBoxLayout()
		self._layout.addWidget(self.title)
		self._layout.addWidget(self.passwrd)
		self._layout.addWidget(self.confirm)
		self.ok = QPushButton(QIcon.fromTheme("dialog-ok"), "", self)
		self.cancel = QPushButton(QIcon.fromTheme("dialog-cancel"), "", self)
		self.buttonLayout = QHBoxLayout()
		self.buttonLayout.addWidget(self.ok)
		self.buttonLayout.addWidget(self.cancel)
		self._layout.addItem(self.buttonLayout)
		self.setLayout(self._layout)
		self.ok.clicked.connect(self.checkCorrectOfPassword)
		self.cancel.clicked.connect(self.clearKeyringCreation)

	def checkCorrectOfPassword(self):
		if self.confirm.text() == self.passwrd.text() :
			self.Keyring.create_Keyring(self.passwrd.text())
			self.Sound.Complete.play()
			QMessageBox.information(self, \
					self.tr._translate("Create Keyring"), \
					self.tr._translate("Keyring created."), \
					1)
			self.clearKeyringCreation()
			self.deleteKeyringCreation()
		else :
			self.Sound.Attention.play()
			QMessageBox.information(self, \
					self.tr._translate("Create Keyring"), \
					self.tr._translate("Passwords mismatch"), \
					1)
			self.clearKeyringCreation()

	def clearKeyringCreation(self):
		self.passwrd.clear()
		self.confirm.clear()

	def deleteKeyringCreation(self):
		#while (item = self._layout.takeAt(0)) \
		#			and item not in (0, None) :
		#	del item
		self.prnt.VBLayout.removeWidget(self)
		self.close()

	#def eventClose(self, event):
	#	self.prnt.done(0)
