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

from PyQt4.QtGui import QComboBox, QWidget
from Translator import Translator
from PasswordEnter import *

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
		i = 0
		for item in get_all_keyring(self) :
			state = item.supported()
			if state :
				icon = QIcon.fromTheme("dialog-ok-apply")
				info = self.tr._translate("Available / Recommended")
			elif state==0 :
				icon = QIcon.fromTheme("dialog-ok")
				info = self.tr._translate("Available")
			else :
				icon = QIcon.fromTheme("dialog-cancel")
				info = self.tr._translate("Not Available")
			self.currentKeyring.addItem(icon, item.name)
			i += 1
			self.currentKeyring.setItemData(i, info)
		self.currentKeyring.setToolTip(self.tr._translate("Current Keyring"))
		self.currentKeyring.currentIndexChanged[int].connect(self.stateChanged)
		self.keyringInfo = QLabel()

		self.VBLayout = QVBoxLayout()
		self.VBLayout.addWidget(self.currentKeyring)
		self.VBLayout.addWidget(self.keyringInfo)

		self.setLayout(self.VBLayout)
		self.initKeyring()

	def initKeyring(self):
		keyringName = self.Settings.value("Keyring", "").toString()
		i = self.currentKeyring.findText(keyringName)
		if i>=0 : self.currentKeyring.setCurrentIndex(i)
		self.Keyring = None if i<1 else KEYRING[i-1]
		self.StateChanged = False

	def stateChanged(self, i=0):
		self.StateChanged = True
		self.keyringInfo.setText("INFO: %s" % self.currentKeyring.itemData(i).toString())
		self.Keyring = None if i<1 else KEYRING[i-1]

	def saveData(self):
		self.Settings.setValue("Keyring", self.currentKeyring.currentText())
		self.StateChanged = False

	def rejectChanges(self):
		self.initKeyring()

	def createKeyring(self, msg = ''):
		self.StateChanged = True
		self.Parent.eventNotification(msg)
		#
		self.enterPassword = PasswordEnter('Create Keyring', self)
		self.enterPassword.exec_()
		del self.enterPassword
		self.enterPassword = None

	def getKeyringPassword(self):
		self.enterPassword = PasswordEnter(self.Keyring.name, self, 0)
		self.enterPassword.exec_()
		del self.enterPassword
		self.enterPassword = None
