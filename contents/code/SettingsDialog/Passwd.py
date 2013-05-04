# -*- coding: utf-8 -*-
#  Passwd.py
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

from PyQt4.QtGui import QComboBox, QWidget, QLabel, \
						QVBoxLayout, QHBoxLayout, \
						QPushButton, QIcon, QLineEdit, \
						QMessageBox
from PyQt4.QtCore import QStringList, Qt
from Translator import Translator
from KeyringStuff import *

class PasswordManipulate(QWidget):
	def __init__(self, obj = None, parent = None):
		QWidget.__init__(self)

		self.Parent = obj
		#self.prnt = parent
		self.tr = Translator('PasswordManipulate')
		self.Settings = self.Parent.Settings
		self.checkAccess = self.Parent.checkAccess
		self.currentKeyring = QComboBox()
		self.currentKeyring.addItem("")
		for item in get_all_keyring(self) :
			state = item.supported()
			if state : icon = QIcon.fromTheme("dialog-ok-apply")
			elif state==0 : icon = QIcon.fromTheme("dialog-ok")
			else : icon = QIcon.fromTheme("dialog-cancel")
			self.currentKeyring.addItem(icon, item.name)
		self.currentKeyring.setToolTip(self.tr._translate("Current Keyring"))
		keyringName = self.Settings.value("Keyring", "").toString()
		i = self.currentKeyring.findText(keyringName)
		if i>=0 : self.currentKeyring.setCurrentIndex(i)
		self.currentKeyring.currentIndexChanged[int].connect(self.stateChanged)
		info = "???????"
		self.keyringInfo = QLabel()
		#self.keyringInfo.setPixmap(QIcon.fromTheme("task-attention").pixmap(32, 32))
		self.keyringInfo.setText("INFO: %s" % info)

		self.VBLayout = QVBoxLayout()
		self.VBLayout.addWidget(self.currentKeyring)
		self.VBLayout.addWidget(self.keyringInfo)
		self.setLayout(self.VBLayout)
		self.StateChanged = False
		self.Keyring = None if i<1 else KEYRING[i-1]

	def stateChanged(self, i=0):
		self.StateChanged = True
		# change keyring info

	def saveData(self):
		self.StateChanged = False
		self.Settings.setValue("Keyring", self.currentKeyring.currentText())

	def eventNotification(self, msg = ''):
		self.Parent.eventNotification(msg)
		self.title = QLabel(self.tr._translate("Create Keyring"))
		self.title.setAlignment(Qt.AlignHCenter)
		self.passwrd = QLineEdit()
		self.passwrd.setEchoMode(QLineEdit.Password)
		self.passwrd.setToolTip(self.tr._translate("Enter Password"))
		self.confirm = QLineEdit()
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
		self.keyringCreation = QWidget()
		self.keyringCreation.setLayout(self._layout)
		self.VBLayout.addWidget(self.keyringCreation)
		self.setLayout(self.VBLayout)
		self.ok.clicked.connect(self.checkCorrectOfPassword)
		self.cancel.clicked.connect(self.clearKeyringCreation)
		self.Parent.showConfigurationInterface()
		self.Parent.dialog.tabWidget.setCurrentWidget(self)

	def checkCorrectOfPassword(self):
		if self.confirm.text().toLocal8Bit().data() == \
				self.passwrd.text().toLocal8Bit().data() :
			self.Keyring.create_Keyring(self.passwrd.text().toLocal8Bit().data())
			QMessageBox.information(self, \
					self.tr._translate("Create Keyring"), \
					self.tr._translate("Keyring created."), \
					1)
			self.clearKeyringCreation()
			self.deleteKeyringCreation()
		else :
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
		self.VBLayout.removeWidget(self.keyringCreation)
		del self.keyringCreation

	#def eventClose(self, event):
	#	self.prnt.done(0)
