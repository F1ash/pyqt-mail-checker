# -*- coding: utf-8 -*-

from PyQt4.QtGui import QWidget, QScrollArea, QVBoxLayout, \
						QPushButton, QIcon, QHBoxLayout
from PyQt4.QtCore import Qt, QEvent, pyqtSignal, QMutex
from MessageDialog import MessageDialog

class MessageStackWidget(QWidget):
	checkEmpty = pyqtSignal(str)
	def __init__(self, obj, parent = None):
		QWidget.__init__(self, parent)
		self.prnt = obj
		self.setWindowTitle(self.prnt.tr._translate('M@il Checker : Stack'))
		self.mutex = QMutex()
		self.parentVisibilityState = \
		(self.prnt.isVisible(), self.prnt.isMinimized(), self.prnt.isMaximized())

		self.stack = QWidget()
		self.scroll = QScrollArea()
		self.scroll.setWidgetResizable(True)
		self.scroll.setWidget(self.stack)

		self.scrolledLayout = QVBoxLayout()
		self.buttonLayout = QHBoxLayout()
		self.stackLayout = QVBoxLayout()
		self.stackLayout.setSpacing(3)

		self.freezAllMSG = QPushButton(QIcon.fromTheme("layer-visible-on"), '')
		self.freezAllMSG.setToolTip(self.prnt.tr._translate('Freez all messages'))
		self.freezAllMSG.clicked.connect(self.freezAllMessages)
		self.clearAllMSG = QPushButton(QIcon.fromTheme("edit-clear"), '')
		self.clearAllMSG.setToolTip(self.prnt.tr._translate('Clear all messages'))
		self.clearAllMSG.clicked.connect(self.clearAllMessages)

		self.buttonLayout.addWidget(self.freezAllMSG)
		self.buttonLayout.addWidget(self.clearAllMSG)
		self.scrolledLayout.addItem(self.buttonLayout)
		self.scrolledLayout.addWidget(self.scroll)
		self.scrolledLayout.setSpacing(3)
		self.setLayout(self.scrolledLayout)

		self.setMinimumHeight(self.prnt.desktop.height()/5)
		self.setMinimumWidth(self.prnt.desktop.width()/3)
		self.stack.setStyleSheet("QWidget {background: rgba(235,240,255,0);}")
		self.MessageStack = {}
		self.checkEmpty.connect(self.checkStackContent)

	def newMessage(self, str_, jobID, lifetime = 0):
		self.MessageStack[jobID] = MessageDialog(str_, jobID, lifetime, self)
		self.stackLayout.insertWidget(0, self.MessageStack[jobID])
		self.stack.setLayout(self.stackLayout)
		self.setLayout(self.scrolledLayout)
		if self.prnt.SoundEnabled :
			self.prnt.sound.NewMessage.play()

	def freezAllMessages(self):
		self.mutex.lock()
		for jobID in self.MessageStack.iterkeys() :
			self.MessageStack[jobID].freez(common = True)
		self.mutex.unlock()
		if self.prnt.SoundEnabled :
			self.prnt.sound.Frozen.play()

	def clearAllMessages(self):
		self.clearAllMSG.setEnabled(False)
		self.mutex.lock()
		to_Delete = []
		for jobID in self.MessageStack.iterkeys() :
			to_Delete.append(jobID)
		for jobID in to_Delete :
			self.MessageStack[jobID].rejected(common = True)
		self.mutex.unlock()
		self.clearAllMSG.setEnabled(True)
		if self.prnt.SoundEnabled :
			self.prnt.sound.Cleared.play()

	def checkStackContent(self, key = ''):
		_key = str(key)
		self.stackLayout.removeWidget(self.MessageStack[_key])
		if _key in self.MessageStack.iterkeys() : del self.MessageStack[_key]
		#print "MessageStack least:", [item for item in self.MessageStack.iterkeys()]
		count = self.stackLayout.count()
		if not count :
			#self.prnt.clearJob.emit("***ALL***")
			self.parentVisibilityState = \
			(self.prnt.isVisible(), self.prnt.isMinimized(), self.prnt.isMaximized())
			if not self.parentVisibilityState[0] : self.prnt.showMinimized()
			self.close()

	def _show(self):
		self.stack.show()
		self.show()

	def closeEvent(self, ev):
		self.hide()
		ev.ignore()
		if not self.parentVisibilityState[0] :
			self.prnt.autoHide(3)
		elif not self.parentVisibilityState[1] and not self.parentVisibilityState[2] :
			self.prnt.showNormal()
		elif self.parentVisibilityState[1] : self.prnt.showMinimized()
		else : self.prnt.showMaximized()
