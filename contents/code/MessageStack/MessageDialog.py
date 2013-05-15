# -*- coding: utf-8 -*-
#  MailViewDialog.py
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
						QHBoxLayout, QVBoxLayout, \
						QPushButton, QIcon, \
						QSizePolicy, QProgressBar
from PyQt4.QtCore import Qt, QEvent

class MessageDialog(QWidget):
	def __init__(self, mailList, jobID = '', sec = 0, parent = None):
		QWidget.__init__(self, parent)
		self.prnt = parent
		self.jobID = jobID
		self.frozen = False
		self.tr = self.prnt.prnt.tr
		self.setWindowTitle(self.tr._translate('M@il Checker : MailView Dialog'))
		self.setStyleSheet("QWidget {background: rgba(235,240,255,128);}")
		self.mailList = QLabel(mailList)
		self.layout = QVBoxLayout(self)
		self.buttonLayout = QHBoxLayout(self)
		
		self.ok = QPushButton(QIcon.fromTheme("dialog-ok"), "", self)
		self.cancel = QPushButton(QIcon.fromTheme("dialog-cancel"), "", self)
		self.freezMSG = QPushButton(QIcon.fromTheme("layer-visible-on"), '', self)
		self.freezMSG.setToolTip(self.tr._translate('Freez message'))
		self.ok.setMaximumHeight(15)
		self.freezMSG.setMaximumHeight(15)
		self.cancel.setMaximumHeight(15)
		self.ok.clicked.connect(self.accepted)
		self.freezMSG.clicked.connect(self.freez)
		self.cancel.clicked.connect(self.rejected)
		self.buttonLayout.addWidget(self.ok)
		self.buttonLayout.addWidget(self.freezMSG)
		self.buttonLayout.addWidget(self.cancel)

		self.layout.addWidget(self.mailList)
		if sec :
			self.lifetime = QProgressBar()
			self.lifetime.setOrientation(Qt.Horizontal)
			self.lifetime.setMinimum(0)
			self.lifetime.setMaximum(sec)
			self.lifetime.setValue(sec)
			self.lifetime.setMaximumHeight(7)
			self.layout.addWidget(self.lifetime)
			self.lifetimeID = self.startTimer(1000)
		self.layout.addItem(self.buttonLayout)

		self.setLayout(self.layout)
		self.setSizePolicy(QSizePolicy(QSizePolicy.PushButton))
		self.setMinimumWidth(100)

	def accepted(self):
		self.prnt.prnt.viewJob.emit(self.jobID)
		if self.prnt.prnt.SoundEnabled :
			self.prnt.prnt.sound.Accepted.play()
		self.close()

	def rejected(self, common = False):
		if self.prnt.prnt.SoundEnabled and not common :
			self.prnt.prnt.sound.Cleared.play()
		self.close()

	def freez(self, common = False):
		self.killTimer(self.lifetimeID)
		self.setStyleSheet("QWidget {background: rgba(100,175,255,25);}")
		self.frozen = True
		if self.prnt.prnt.SoundEnabled and not common :
			self.prnt.prnt.sound.Frozen.play()

	def timerEvent(self, ev):
		if ev.type()==QEvent.Timer :
			value = self.lifetime.value()
			#print ev.timerId(), value
			if value > self.lifetime.minimum() :
				self.lifetime.setValue(value-1)
			else :
				self.close()

	def closeEvent(self, ev):
		if ev.type()==QEvent.Close :
			self.killTimer(self.lifetimeID)
			self.prnt.checkEmpty.emit(self.jobID)
			self.prnt.prnt.clearJob.emit(self.jobID)
			ev.accept()
		else : ev.ignore()
