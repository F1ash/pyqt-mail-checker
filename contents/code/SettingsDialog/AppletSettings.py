#  AppletSettings.py
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

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from Translator import Translator
#from AkonadiMod import AkonadiModuleExist
# CHOP:
AkonadiModuleExist = False

class AppletSettings(QWidget):
	def __init__(self, obj = None, parent= None):
		QWidget.__init__(self, parent)

		self.Parent = obj
		self.prnt = parent
		self.tr = Translator('AppletSettings')
		self.Settings = self.Parent.Settings
		self.checkAccess = self.Parent.checkAccess

		timeOut = self.initValue('TimeOut', '600')
		AutoRun = self.initValue('AutoRun', '0')
		soundEnabled = self.Settings.value('Sound', False).toBool()
		countProbe = self.initValue('CountProbe', '3')
		lifeTime = self.initValue('MsgLifeTime', '30')
		showError = self.initValue('ShowError', '1')
		waitThread = self.initValue('WaitThread', '120')
		stayDebLog = self.initValue('stayDebLog', '5')
		showVersion = self.initValue('ShowVersion', '1')
		maxShowedMail = self.initValue('MaxShowedMail', '1024')
		mailsInGroup = self.initValue('MailsInGroup', '5')

		self.layout = QGridLayout()

		self.timeOutLabel = QLabel(self.tr._translate("Timeout checking (sec.):"))
		self.layout.addWidget(self.timeOutLabel, 0, 0)
		self.timeOutBox = QSpinBox(self)
		self.timeOutBox.setMinimum(10)
		self.timeOutBox.setMaximum(7200)
		self.timeOutBox.setSingleStep(1)
		self.timeOutBox.setValue(int(timeOut))
		self.timeOutBox.setMaximumWidth(75)
		self.layout.addWidget(self.timeOutBox, 0, 5)

		self.autoRunLabel = QLabel(self.tr._translate("Autorun mail checking :"))
		self.layout.addWidget(self.autoRunLabel, 1, 0)
		self.AutoRunBox = QCheckBox()
		if int(AutoRun) > 0 :
			self.AutoRunBox.setCheckState(Qt.Checked)
		self.layout.addWidget(self.AutoRunBox, 1, 5)

		self.countProbe = QLabel(self.tr._translate("Count of connect probe\nto mail server:"))
		self.layout.addWidget(self.countProbe, 2, 0)
		self.countProbeBox = QSpinBox(self)
		self.countProbeBox.setMinimum(1)
		self.countProbeBox.setMaximum(10)
		self.countProbeBox.setSingleStep(1)
		self.countProbeBox.setValue(int(countProbe))
		self.layout.addWidget(self.countProbeBox, 2, 5)

		self.msgTimeLife = QLabel(self.tr._translate("Message`s timelife:"))
		self.layout.addWidget(self.msgTimeLife, 3, 0)
		self.msgTimeLifeBox = QSpinBox(self)
		self.msgTimeLifeBox.setMinimum(0)
		self.msgTimeLifeBox.setMaximum(600)
		self.msgTimeLifeBox.setSingleStep(1)
		self.msgTimeLifeBox.setValue(int(lifeTime))
		self.layout.addWidget(self.msgTimeLifeBox, 3, 5)

		self.showError = QLabel(self.tr._translate("Show error messages :"))
		self.layout.addWidget(self.showError, 4, 0)
		self.showErrorBox = QCheckBox()
		if int(showError) > 0 :
			self.showErrorBox.setCheckState(Qt.Checked)
		self.layout.addWidget(self.showErrorBox, 4, 5)

		self.waitThreadLabel = QLabel(self.tr._translate("Autoexit of connect (sec.):"))
		self.layout.addWidget(self.waitThreadLabel, 5, 0)
		self.waitThreadBox = QSpinBox(self)
		self.waitThreadBox.setMinimum(3)
		self.waitThreadBox.setMaximum(7200)
		self.waitThreadBox.setSingleStep(1)
		self.waitThreadBox.setValue(int(waitThread))
		self.layout.addWidget(self.waitThreadBox, 5, 5)

		self.stayDebLogLabel = QLabel(self.tr._translate("Stay Debug output Log :"))
		self.layout.addWidget(self.stayDebLogLabel, 6, 0)
		self.stayDebLogBox = QSpinBox(self)
		self.stayDebLogBox.setMinimum(1)
		self.stayDebLogBox.setMaximum(50)
		self.stayDebLogBox.setSingleStep(1)
		self.stayDebLogBox.setValue(int(stayDebLog))
		self.stayDebLogBox.setMaximumWidth(75)
		self.layout.addWidget(self.stayDebLogBox, 6, 5)

		self.showVersion = QLabel(self.tr._translate("Show Version :"))
		self.layout.addWidget(self.showVersion, 7, 0)
		self.showVersionBox = QCheckBox()
		if int(showVersion) > 0 :
			self.showVersionBox.setCheckState(Qt.Checked)
		self.layout.addWidget(self.showVersionBox, 7, 5)

		self.maxMailLabel = QLabel(self.tr._translate("Max Count of Showed Mail :"))
		self.layout.addWidget(self.maxMailLabel, 8, 0)
		self.maxMailBox = QSpinBox(self)
		self.maxMailBox.setMinimum(1)
		self.maxMailBox.setMaximum(1024)
		self.maxMailBox.setSingleStep(1)
		self.maxMailBox.setValue(int(maxShowedMail))
		self.maxMailBox.setMaximumWidth(75)
		self.maxMailBox.valueChanged[int].connect(self.showMailGroupping)
		self.layout.addWidget(self.maxMailBox, 8, 5)

		self.mailInGroupLabel = QLabel('\t' + self.tr._translate("Count of Mail in Group for account:"))
		self.mailInGroupLabel.setEnabled(False)
		self.layout.addWidget(self.mailInGroupLabel, 9, 0)
		self.mailInGroupBox = QSpinBox(self)
		self.mailInGroupBox.setMinimum(1)
		self.mailInGroupBox.setMaximum(10)
		self.mailInGroupBox.setSingleStep(1)
		self.mailInGroupBox.setValue(int(mailsInGroup))
		self.mailInGroupBox.setMaximumWidth(75)
		self.mailInGroupBox.setEnabled(False)
		self.layout.addWidget(self.mailInGroupBox, 9, 5)

		self.soundLabel = QLabel(self.tr._translate("Sound Enable :"))
		self.layout.addWidget(self.soundLabel, 10, 0)
		self.soundBox = QCheckBox()
		if soundEnabled :
			self.soundBox.setCheckState(Qt.Checked)
		self.layout.addWidget(self.soundBox, 10, 5)

		self.setLayout(self.layout)
		self.maxMailBox.valueChanged.emit(int(maxShowedMail))

	def initValue(self, key_, default = '0'):
		if self.Settings.contains(key_) :
			#print dateStamp() ,  key_, self.Settings.value(key_).toString()
			return self.Settings.value(key_).toString()
		else :
			self.Settings.setValue(key_, QVariant(default))
			#print dateStamp() ,  key_, self.Settings.value(key_).toString()
			return default

	def stateChanged(self, state):
		self.mailInGroupLabel.setEnabled(state)
		self.mailInGroupBox.setEnabled(state)

	def showMailGroupping(self, i):
		if i > self.mailInGroupBox.value() :
			self.stateChanged(True)
		else :
			self.stateChanged(False)

	def refreshSettings(self):
		if not self.checkAccess() : return None
		self.Settings.setValue('TimeOut', str(self.timeOutBox.value()))
		self.Settings.setValue('CountProbe', str(self.countProbeBox.value()))
		self.Settings.setValue('MsgLifeTime', str(self.msgTimeLifeBox.value()))
		self.Settings.setValue('WaitThread', str(self.waitThreadBox.value()))
		self.Settings.setValue('stayDebLog', str(self.stayDebLogBox.value()))
		self.Settings.setValue('MaxShowedMail', str(self.maxMailBox.value()))
		self.Settings.setValue('MailsInGroup', str(self.mailInGroupBox.value()))
		if self.AutoRunBox.isChecked() :
			self.Settings.setValue('AutoRun', '1')
		else:
			self.Settings.setValue('AutoRun', '0')
		if self.showErrorBox.isChecked() :
			self.Settings.setValue('ShowError', '1')
		else:
			self.Settings.setValue('ShowError', '0')
		if self.showVersionBox.isChecked() :
			self.Settings.setValue('ShowVersion', '1')
		else:
			self.Settings.setValue('ShowVersion', '0')
		value = self.soundBox.isChecked()
		self.Settings.setValue('Sound', value)

		self.Settings.sync()

	def eventClose(self, event):
		self.prnt.done(0)
