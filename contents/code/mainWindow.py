# -*- coding: utf-8 -*-
#  mainWindow.py
#  
#  Copyright 2012 Flash <kaperang07@gmail.com>
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

try :
	from PyQt4.QtCore import *
	from PyQt4.QtGui import *
	import string, time, os.path, sys
	
	from misc.Sound import Sound
	from Utils.Functions import *
	from SettingsDialog.Filter import Filters
	from SettingsDialog.Proxy import ProxySettings
	from SettingsDialog.Examples import Examples
	from SettingsDialog.EditAccounts import EditAccounts
	from SettingsDialog.AppletSettings import AppletSettings
	from SettingsDialog.FontNColor import Font_n_Colour
	from SettingsDialog.Passwd import *
	from SettingsDialog.PageDialog import PageDialog
	from Threads.IdleMailing import IdleMailing
	from Threads.WaitIdle import WaitIdle
	from Threads.CheckMailThread import ThreadCheckMail
	from MessageStack.MessageStackWidget import MessageStackWidget
	from MailProgExec import MailProgExec
	from Translator import Translator
	#sys.stderr = open('/dev/shm/errorMailChecker' + str(time.time()) + '.log','w')
	sys.stdout = open('/tmp/outMailChecker' + time.strftime("_%Y_%m_%d_%H:%M:%S", time.localtime()) + '.log','w')
except Exception, err :
	print "Exception: ", err
finally:
	'O`key'
	pass

class MainWindow(QWidget):
	idleThreadMessage = pyqtSignal(dict)
	idleingStopped = pyqtSignal()
	viewJob = pyqtSignal(str)
	clearJob = pyqtSignal(str)
	def __init__(self, desktop, parent = None):
		QWidget.__init__(self,parent)

		self.initStat = False
		self.closeFlag = True
		self.checkResult = []
		self.idleMailingList = []
		self.ErrorMsg = ''
		self.desktop = desktop

		self.listNewMail = []
		self.connectIconsFlag = False
		self.appletName = 'pyqt-mail-checker'
		self.lockFile = os.path.join("/tmp", self.appletName + '.lock')
		self.tr = Translator()
		self.setWindowTitle(self.tr._translate('M@il Checker'))
		self.Settings = QSettings(self.appletName, self.appletName)
		self.GeneralLOCK = QMutex()
		self.someFunctions = Required(self)
		self.sound = Sound(self)
		self.initPrefixAndSuffix()
		self.initWorkParameters()
		self.init()

	def lock(self):
		if not self.isLocked() :
			with open(self.lockFile, 'w') as f :
				f.write( str(os.getpid()) )
			return True
		return False

	def unlock(self):
		if self.isLocked() :
			os.remove(self.lockFile)

	def isLocked(self):
		return os.path.exists(self.lockFile)

	def init(self):
		self.T = ThreadCheckMail(self)
		self.Timer = QTimer()

		self.initMainWindow()
		self.setMinimumSize(150.0,75.0)

		self.connect(self, SIGNAL('destroyed()'), self.eventClose)
		self.connect(self, SIGNAL('refresh'), self.refreshData)
		self.connect(self, SIGNAL('access'), self.processInit)
		self.connect(self, SIGNAL('killThread'), self.killMailCheckerThread)
		self.idleThreadMessage.connect(self.idleMessage)
		self.idleingStopped.connect(self.idleingStoppedEvent)
		self.Timer.timeout.connect(self._refreshData)
		self.viewJob.connect(self.mailViewJobUp)
		self.clearJob.connect(self.mailViewJobClean)

		self.locked = self.lock()
		if not self.locked : self.eventClose()
		else :
			AutoRun = self.initValue('AutoRun')
			if AutoRun != '0' :
				#QApplication.postEvent(self, QEvent(QEvent.User))
				self.Timer1 = QTimer()
				self.Timer1.setSingleShot(True)
				self.Timer1.timeout.connect(self.enterPassword)
				self.Timer1.start(2000)
			if self.SoundEnabled :
				self.sound.AppletStarted.play()

	def initMainWindow(self):
		self.initMainWindowLayout()
		self.initTitle()
		self.initMessageStackWidget()
		self.createDialogWidget()
		self.initSysTrayIcon()
		self.restoreAppGeometry()

		self.setLayout(self.layout)
		self.updateGeometry()

	def initMainWindowLayout(self):
		self.layout = QGridLayout()
		self.layout.setContentsMargins(1, 1, 1, 1)
		self.layout.setSpacing(0)

	def initMessageStackWidget(self):
		self.MailProgExecList = {}
		self.MessageStackWidget = MessageStackWidget(self)
		self.MessageStackWidget.hide()

	def initTitle(self):
		self.VERSION = '~'
		fileName = self.user_or_sys('VERSION')
		if os.path.exists(fileName) :
			with open(fileName) as f :
				self.VERSION = f.read()
		#print dateStamp() , "VERSION : ", self.VERSION
		self.version = self.initValue('ShowVersion', '1')

		self.titleLayout = QHBoxLayout()

		self.icon = QPushButton()
		self.icon.setMaximumSize(36,36)
		self.icon.setIconSize(self.getIconActualSize("mailChecker"))
		self.icon.setIcon(QIcon.fromTheme("mailChecker"))
		self.icon.setToolTip(self.headerPref + \
							self.tr._translate('Click for Start\Stop') + \
							self.headerSuff)
		self.connectIconsFlag = self.connect(self.icon, SIGNAL('clicked()'), self._enterPassword)

		self.TitleDialog = QLabel()
		if int(self.version) > 0 :
			self.title = self.tr._translate('M@il Checker') + '\n' + self.VERSION + ' ' + lang[0][:2]
		else :
			self.title = self.tr._translate('M@il Checker')
		self.TitleDialog.setText(self.headerPref + self.title + self.headerSuff)
		self.TitleDialog.setStyleSheet(self.headerColourStyle)
		
		self.titleLayout.addWidget(self.TitleDialog)
		self.titleLayout.addWidget(self.icon)
		self.layout.addItem(self.titleLayout)

	def initColourAndFont(self):
		self.headerFontVar = self.initValue('headerFont', ' ')
		self.headerSizeVar = self.initValue('headerSize')
		self.headerBoldVar = self.initValue('headerBold')
		self.headerItalVar = self.initValue('headerItal')
		self.headerColourVar = self.initValue('headerColour')

		self.accountFontVar = self.initValue('accountFont', ' ')
		self.accountSizeVar = self.initValue('accountSize')
		self.accountBoldVar = self.initValue('accountBold')
		self.accountItalVar = self.initValue('accountItal')
		self.accountColourVar = self.initValue('accountColour')
		self.accountSFontVar = self.initValue('accountSFont', ' ')
		self.accountSSizeVar = self.initValue('accountSSize')
		self.accountSBoldVar = self.initValue('accountSBold')
		self.accountSItalVar = self.initValue('accountSItal')
		self.accountSColourVar = self.initValue('accountSColour')

		self.accountToolTipFontVar = self.initValue('accountToolTipFont', ' ')
		self.accountToolTipSizeVar = self.initValue('accountToolTipSize')
		self.accountToolTipBoldVar = self.initValue('accountToolTipBold')
		self.accountToolTipItalVar = self.initValue('accountToolTipItal')
		self.accountToolTipColourVar = self.initValue('accountToolTipColour')
		self.accountToolTipSFontVar = self.initValue('accountToolTipSFont', ' ')
		self.accountToolTipSSizeVar = self.initValue('accountToolTipSSize')
		self.accountToolTipSBoldVar = self.initValue('accountToolTipSBold')
		self.accountToolTipSItalVar = self.initValue('accountToolTipSItal')
		self.accountToolTipSColourVar = self.initValue('accountToolTipSColour')

		self.countFontVar = self.initValue('countFont', ' ')
		self.countSizeVar = self.initValue('countSize')
		self.countBoldVar = self.initValue('countBold')
		self.countItalVar = self.initValue('countItal')
		self.countColourVar = self.initValue('countColour')
		self.countSFontVar = self.initValue('countSFont', ' ')
		self.countSSizeVar = self.initValue('countSSize')
		self.countSBoldVar = self.initValue('countSBold')
		self.countSItalVar = self.initValue('countSItal')
		self.countSColourVar = self.initValue('countSColour')

		self.countToolTipFontVar = self.initValue('countToolTipFont', ' ')
		self.countToolTipSizeVar = self.initValue('countToolTipSize')
		self.countToolTipBoldVar = self.initValue('countToolTipBold')
		self.countToolTipItalVar = self.initValue('countToolTipItal')
		self.countToolTipColourVar = self.initValue('countToolTipColour')
		self.countToolTipSFontVar = self.initValue('countToolTipSFont', ' ')
		self.countToolTipSSizeVar = self.initValue('countToolTipSSize')
		self.countToolTipSBoldVar = self.initValue('countToolTipSBold')
		self.countToolTipSItalVar = self.initValue('countToolTipSItal')
		self.countToolTipSColourVar = self.initValue('countToolTipSColour')

		self.fieldBoxFontVar = self.initValue('fieldBoxFont', ' ')
		self.fieldBoxSizeVar = self.initValue('fieldBoxSize')
		self.fieldBoxBoldVar = self.initValue('fieldBoxBold')
		self.fieldBoxItalVar = self.initValue('fieldBoxItal')
		self.fieldBoxColourVar = self.initValue('fieldBoxColour')

		self.fieldFromFontVar = self.initValue('fieldFromFont', ' ')
		self.fieldFromSizeVar = self.initValue('fieldFromSize')
		self.fieldFromBoldVar = self.initValue('fieldFromBold')
		self.fieldFromItalVar = self.initValue('fieldFromItal')
		self.fieldFromColourVar = self.initValue('fieldFromColour')

		self.fieldSubjFontVar = self.initValue('fieldSubjFont', ' ')
		self.fieldSubjSizeVar = self.initValue('fieldSubjSize')
		self.fieldSubjBoldVar = self.initValue('fieldSubjBold')
		self.fieldSubjItalVar = self.initValue('fieldSubjItal')
		self.fieldSubjColourVar = self.initValue('fieldSubjColour')

		self.fieldDateFontVar = self.initValue('fieldDateFont', ' ')
		self.fieldDateSizeVar = self.initValue('fieldDateSize')
		self.fieldDateBoldVar = self.initValue('fieldDateBold')
		self.fieldDateItalVar = self.initValue('fieldDateItal')
		self.fieldDateColourVar = self.initValue('fieldDateColour')

		self.headerColourStyle = self.getRGBaStyle(QString(self.headerColourVar).toUInt())
		self.accountColourStyle = self.getRGBaStyle(QString(self.accountColourVar).toUInt())
		self.accountSColourStyle = self.getRGBaStyle(QString(self.accountSColourVar).toUInt())
		self.accountToolTipColourStyle = self.getRGBaStyle(QString(self.accountToolTipColourVar).toUInt())
		self.accountToolTipSColourStyle = self.getRGBaStyle(QString(self.accountToolTipSColourVar).toUInt())
		self.countColourStyle = self.getRGBaStyle(QString(self.countColourVar).toUInt())
		self.countSColourStyle = self.getRGBaStyle(QString(self.countSColourVar).toUInt())
		self.countToolTipColourStyle = self.getRGBaStyle(QString(self.countToolTipColourVar).toUInt())
		self.countToolTipSColourStyle = self.getRGBaStyle(QString(self.countToolTipSColourVar).toUInt())

	def getRGBaStyle(self, (colour, yes)):
		if yes :
			style = 'QLabel { color: rgba' + str(QColor().fromRgba(colour).getRgb()) + ';} '
		else :
			style = 'QLabel { color: rgba' + self.getSystemColor() + ';} '
		return style

	def initValue(self, key_, defaultValue = ''):
		if self.Settings.contains(key_) :
			#print dateStamp() ,  key_, self.Settings.value(key_).toString()
			return self.Settings.value(key_).toString()
		else :
			if defaultValue == '' :
				defaultValue = self.getSystemColor('int')
			self.Settings.setValue(key_, QVariant(defaultValue))
			#print dateStamp() ,  key_, self.Settings.value(key_).toString()
			return defaultValue

	def getSystemColor(self, key_ = ''):
		currentBrush = QPalette().windowText()
		colour = currentBrush.color()
		if key_ == 'int' :
			#print dateStamp() ,  colour.rgba()
			return str(colour.rgba())
		else :
			#print dateStamp() ,  str(colour.getRgb())
			return str(colour.getRgb())

	def cursive_n_bold(self, bold, italic):
		pref = ''
		suff = ''
		if bold == '1' :
			pref += '<b>'; suff += '</b>'
		if italic == '1' :
			pref = '<i>' + pref; suff += '</i>'
		return pref, suff

	def getPrefixAndSuffix(self, b, i, font, tooltip = False, colour = 0):
		pref, suff = self.cursive_n_bold(b, i)
		prefix = '<font face="' + font
		if tooltip :
			colourHTML = str( QColor(QString(colour).toUInt()[0]).name() )
			prefix += '" color="' + colourHTML
		prefix += '" >' + pref
		suffix = suff + '</font>'
		return prefix, suffix

	def initWorkParameters(self):
		self.checkTimeOut = self.initValue('TimeOut', '600')
		self.msgLifeTime = int(self.initValue('MsgLifeTime', '30'))
		self.waitThread = self.initValue('WaitThread', '120')
		self.maxShowedMail = int(self.initValue('MaxShowedMail', '1024'))
		self.mailsInGroup = int(self.initValue('MailsInGroup', '5'))
		self.KeyringName = self.initValue('Keyring', '')
		self.SoundEnabled = self.Settings.value('Sound', False).toBool()

		self.passwordManipulate = PasswordManipulate(self)
		if hasattr(self.passwordManipulate, 'Keyring') :
			self.Keyring = self.passwordManipulate.Keyring
		else : self.Keyring = None
		
		self.Settings.sync()
		self.accountList = self.Settings.value('Accounts').toString().split(';')
		self.accountCommand = {}
		for accountName in self.accountList :
			self.Settings.beginGroup(accountName)
			self.accountCommand[accountName] = self.initValue('CommandLine', ' ')
			self.Settings.endGroup()

	def initPrefixAndSuffix(self):
		self.initColourAndFont()
		self.headerPref, self.headerSuff = self.getPrefixAndSuffix( \
							self.headerBoldVar, self.headerItalVar, \
							self.headerFontVar)
		self.accPref, self.accSuff = self.getPrefixAndSuffix( \
							self.accountBoldVar, self.accountItalVar, \
							self.accountFontVar)
		self.accSPref, self.accSSuff = self.getPrefixAndSuffix( \
							self.accountSBoldVar, self.accountSItalVar, \
							self.accountSFontVar)
		self.accTTPref, self.accTTSuff = self.getPrefixAndSuffix( \
							self.accountToolTipBoldVar, self.accountToolTipItalVar, \
							self.accountToolTipFontVar, True, self.accountToolTipColourVar)
		self.accTTSPref, self.accTTSSuff = self.getPrefixAndSuffix( \
							self.accountToolTipSBoldVar, self.accountToolTipSItalVar, \
							self.accountToolTipSFontVar, True, self.accountToolTipSColourVar)
		self.countPref, self.countSuff = self.getPrefixAndSuffix( \
							self.countBoldVar, self.countItalVar, \
							self.countFontVar)
		self.countSPref, self.countSSuff = self.getPrefixAndSuffix( \
							self.countSBoldVar, self.countSItalVar, \
							self.countFontVar)
		self.countTTPref, self.countTTSuff = self.getPrefixAndSuffix( \
							self.countToolTipBoldVar, self.countToolTipItalVar, \
							self.countToolTipFontVar, True, self.countToolTipColourVar)
		self.countTTSPref, self.countTTSSuff = self.getPrefixAndSuffix( \
							self.countToolTipSBoldVar, self.countToolTipSItalVar, \
							self.countToolTipSFontVar, True, self.countToolTipSColourVar)
		self.fieldBoxPref, self.fieldBoxSuff = self.getPrefixAndSuffix( \
							self.fieldBoxBoldVar, self.fieldBoxItalVar, \
							self.fieldBoxFontVar, True, self.fieldBoxColourVar)
		self.fieldFromPref, self.fieldFromSuff = self.getPrefixAndSuffix( \
							self.fieldFromBoldVar, self.fieldFromItalVar, \
							self.fieldFromFontVar, True, self.fieldFromColourVar)
		self.fieldSubjPref, self.fieldSubjSuff = self.getPrefixAndSuffix( \
							self.fieldSubjBoldVar, self.fieldSubjItalVar, \
							self.fieldSubjFontVar, True, self.fieldSubjColourVar)
		self.fieldDatePref, self.fieldDateSuff = self.getPrefixAndSuffix( \
							self.fieldDateBoldVar, self.fieldDateItalVar, \
							self.fieldDateFontVar, True, self.fieldDateColourVar)
		self.mailAttrColor = ((self.fieldFromPref, self.fieldFromSuff), \
								(self.fieldSubjPref, self.fieldSubjSuff), \
								(self.fieldDatePref, self.fieldDateSuff))

	def customEvent(self, event):
		if event.type() == QEvent.User :
			self.enterPassword()
		elif event.type() == 1011 :
			self._refreshData()
		elif event.type() == 1010 :
			self.emit(SIGNAL('killThread'))

	def user_or_sys(self, path_):
		return os.path.join(sys.path[0], path_)

	def createDialogItem(self, i):
		self.label.append('')
		self.countList.append('')

		self.label[i] = QLabel()
		self.countList[i] = QLabel()
		self.label[i].setStyleSheet(self.accountColourStyle)
		self.countList[i].setStyleSheet(self.countColourStyle)
		self.Dialog.addWidget(self.label[i],i,0)
		self.Dialog.addWidget(self.countList[i],i,1)

	def createMailBoxDialog(self):
		if hasattr(self, 'Dialog') :
			while self.Dialog.count() :
				child = self.Dialog.takeAt(0)
				del child
			del self.Dialog
			del self.label
			del self.countList
		self.Dialog = QGridLayout()
		i = 0
		self.label = []
		self.countList = []
		for accountName in self.Settings.value('Accounts').toString().split(';') :
			#print accountName.toLocal8Bit().data()
			self.createDialogItem(i)
			self.label[i].setToolTip(self.accTTPref + self.tr._translate('Account') + \
													self.accTTSuff + ' ' + accountName)
			i += 1
		if hasattr(self, 'scrolled') : del self.scrolled
		self.scrolled = QWidget()
		self.scrolled.setLayout(self.Dialog)
		self.scroller.setWidget(self.scrolled)

	def createDialogWidget(self):
		self.scroller = QScrollArea()
		self.scroller.setWidgetResizable(True)
		self.createMailBoxDialog()
		self.labelStat = QLabel()
		self.labelStat.setText("<font color=red><b>" + self.tr._translate('..stopped..') + "</b></font>")
		self.layout.addWidget(self.scroller)
		self.layout.addWidget(self.labelStat)

	def initSysTrayIcon(self):
		if not hasattr(self, 'trayIcon') :
			self.trayIcon = QSystemTrayIcon()
			self.trayIcon.setToolTip(self.tr._translate('M@il Checker'))
			self.trayIcon.setIcon(QIcon.fromTheme("mailChecker"))
			self.connect(self.trayIcon, SIGNAL("activated(QSystemTrayIcon::ActivationReason)"), \
										self.trayIconClicked)

			self.trayIconMenu = QMenu(self)
			self.trayVisiblityAction = QAction("", self)
			self.trayVisiblityAction.setIcon(QIcon.fromTheme("arrow-up"))
			self.trayIconMenu.addAction(self.trayVisiblityAction)
			self.trayMessagesAction = QAction("", self)
			self.trayMessagesAction.setIcon(QIcon.fromTheme("arrow-up"))
			self.trayIconMenu.addAction(self.trayMessagesAction)
			self.trayIconMenu.addSeparator()
			self.trayReloadAction = QAction(self.tr._translate("Reload"), self)
			self.trayReloadAction.setIcon(QIcon.fromTheme("view-refresh"))
			self.trayIconMenu.addAction(self.trayReloadAction)
			self.trayIconMenu.addSeparator()
			self.traySettingsAction = QAction(self.tr._translate("Settings"), self)
			self.traySettingsAction.setIcon(QIcon.fromTheme("configure"))
			self.trayIconMenu.addAction(self.traySettingsAction)
			self.trayIconMenu.addSeparator()
			self.trayExitAction = QAction(self.tr._translate("Exit"), self)
			self.trayExitAction.setIcon(QIcon.fromTheme("application-exit"))
			self.trayIconMenu.addAction(self.trayExitAction)
			
			self.trayVisiblityAction.triggered.connect(self.show_n_hide)
			self.trayMessagesAction.triggered.connect(self.show_n_hide_messages)
			self.trayReloadAction.triggered.connect(self.reloadApp)
			self.traySettingsAction.triggered.connect(self.showConfigurationInterface)
			self.trayExitAction.triggered.connect(self.eventClose)
			
			self.trayIcon.setContextMenu(self.trayIconMenu)
			self.trayIcon.show()

	def restoreAppGeometry(self):
		self.currentGeometry = self.Settings.value('Geometry').toByteArray()
		self.restoreGeometry(self.currentGeometry)

		if self.Settings.value('RunInTray', 'False') == 'True' : self.show()
		else : self.hide()
		self.setTrayVisibilityActionIcon(self.trayVisiblityAction)
		self.setTrayVisibilityActionIcon(self.trayMessagesAction)

	def getIconActualSize(self, theme=''):
		icon = QIcon.fromTheme(theme)
		return icon.actualSize(QSize(36, 36))

	def autoHide(self, i = 0):
		if i : QTimer.singleShot(1000*i, self.hide)

	def show_n_hide(self):
		if self.isVisible() : self.hide()
		else : self.show()
		self.setTrayVisibilityActionIcon(self.trayVisiblityAction)

	def show_n_hide_messages(self):
		if self.MessageStackWidget.isVisible() :
			self.MessageStackWidget.hide()
		else :
			self.MessageStackWidget.show()
			self.MessageStackWidget.move(self.mapToGlobal(self.trayIconMenu.pos()))
		self.setTrayVisibilityActionIcon(self.trayMessagesAction)

	def setTrayVisibilityActionIcon(self, obj = None):
		if obj :
			if obj == self.trayVisiblityAction :
				window = "Main Window"
				control = self
			else :
				window = "Messages"
				control = self.MessageStackWidget
			if control.isVisible() :
				icon = QIcon.fromTheme("arrow-down")
				text = self.tr._translate("Hide %s" % window)
			else :
				icon = QIcon.fromTheme("arrow-up")
				text = self.tr._translate("Show %s" % window)
			
			obj.setIcon(icon)
			obj.setText(text)

	def trayIconClicked(self, reason):
		if reason == QSystemTrayIcon.Trigger :
			self.show_n_hide()
		elif reason == QSystemTrayIcon.MiddleClick :
			self.show_n_hide_messages()

	def processInit(self):
		self.initStat = True
		self.someFunctions.initPOP3Cache()

		self.Timer.start(int(self.checkTimeOut) * 1000)
		print dateStamp() ,  'processInit'
		QApplication.postEvent(self, QEvent(1011))

	def eventNotification(self, str_ = '', id_of_new_Items = {}, command = ''):
		jobID = randomString(12)
		if len(id_of_new_Items) :
			self.MailProgExecList[jobID] = MailProgExec(self, id_of_new_Items, command, self)
		self.MessageStackWidget.newMessage(str_, jobID, self.msgLifeTime)
		if not self.MessageStackWidget.isVisible() :
			self.MessageStackWidget._show()
			self.MessageStackWidget.move(self.mapToGlobal(self.trayIconMenu.pos()))

	def mailViewJobUp(self, key = ''):
		_key = str(key)
		if _key in self.MailProgExecList.iterkeys() :
			if not self.MailProgExecList[_key].isFinished() and \
				not self.MailProgExecList[_key].isRunning() :
					self.MailProgExecList[_key].start()

	def mailViewJobClean(self, key = ''):
		to_Delete = []
		for _key in self.MailProgExecList.iterkeys() :
			if self.MailProgExecList[_key].isFinished() or _key == key :
				to_Delete.append(_key)
		for _key in to_Delete :
			del self.MailProgExecList[_key]

	def disableIconClick(self):
		if self.connectIconsFlag and self.initStat :
			self.connectIconsFlag = not ( self.disconnect(self.icon, \
				SIGNAL('clicked()'), self._enterPassword) )

	def _refreshData(self):
		print dateStamp() , '_refresh'
		if self.initStat :
			self.labelStat.setText("<font color=green><b>" + self.tr._translate('..running..') + "</b></font>")
			self.icon.setIconSize(self.getIconActualSize("mailChecker_web"))
			self.icon.setIcon(QIcon.fromTheme("mailChecker_web"))
			self.icon.setToolTip(self.headerPref + self.tr._translate('Mail\nChecking') +  self.headerSuff)
			self.trayIcon.setIcon(QIcon.fromTheme("mailChecker_web"))
			self.disableIconClick()
		else:
			self.labelStat.setText("<font color=red><b>" + self.tr._translate('..stopped..') + "</b></font>")
			self.icon.setIconSize(self.getIconActualSize("mailChecker_stop"))
			self.icon.setIcon(QIcon.fromTheme("mailChecker_stop"))
			self.trayIcon.setIcon(QIcon.fromTheme("mailChecker_stop"))
			return None

		if self.checkAccess() :
			if not self.T.isRunning() :
				#print dateStamp() ,  'start'
				accData = []
				for accountName in self.Settings.value('Accounts').toString().split(';') :
					self.Settings.beginGroup(accountName)
					enabled = self.Settings.value('Enabled').toString()
					connectMethod = self.Settings.value('connectMethod').toString()
					self.Settings.endGroup()
					#print dateStamp() , accountName.toLocal8Bit().data(), connectMethod, enabled
					if str(enabled) == '1' :
						pswd = self.Keyring.get_password(accountName)
						data = (accountName, pswd)
						if connectMethod == 'imap\idle' :
							exist = False
							for item in self.idleMailingList :
								if accountName == item.name :
									exist = True
									break
							if not exist :
								self.idleMailingList.append(IdleMailing(data, self))
							accData.append(('', ''))
						else :
							accData.append(data)
					else :
						# delete the disabled accounts within idle mode
						exist = False
						for item in self.idleMailingList :
							if accountName == item.name :
								item.stop()
								exist = item
								break
						#print exist, accountName.toLocal8Bit().data()
						if exist : self.idleMailingList.remove(exist)
						accData.append(('', ''))
				self.T = ThreadCheckMail(self, accData, self.waitThread)
				print dateStamp() ,  'time for wait thread : ', self.waitThread
				self.T.start()
				#print dateStamp() , ' starting idles mail:', self.idleMailingList
				for item in self.idleMailingList :
					try :
						if not item.runned :
							item.start()
							state = ' started'
						else :
							state = ' runned'
						#print item.name, state
					except Exception, err :
						print dateStamp(), err, 'in', item.name.toLocal8Bit().data()
					finally : pass
			else :
				#print dateStamp() ,  'isRunning : send signal to kill...'
				#self.emit(SIGNAL('killThread'))
				pass
		else:
			self.emit(SIGNAL('refresh'))
			# print dateStamp() ,  'false start'

	def refreshData(self):
		#print dateStamp() ,  'refresh', self.initStat
		self.GeneralLOCK.lock()

		if self.initStat :
			noCheck = False
			self.labelStat.setText("<font color=green><b>" + self.tr._translate('..running..') + "</b></font>")
			self.icon.setIconSize(self.getIconActualSize("mailChecker"))
			self.icon.setIcon(QIcon.fromTheme("mailChecker"))
			self.icon.setToolTip(self.headerPref + self.tr._translate('Click for Start\Stop') + \
																				self.headerSuff)
			self.trayIcon.setIcon(QIcon.fromTheme("mailChecker"))
		else :
			noCheck = True
			self.labelStat.setText("<font color=red><b>" + self.tr._translate('..stopped..') + "</b></font>")
			self.icon.setIconSize(self.getIconActualSize("mailChecker_stop"))
			self.icon.setIcon(QIcon.fromTheme("mailChecker_stop"))
			self.icon.setToolTip(self.headerPref + self.tr._translate('Click for Start\Stop') + \
																				self.headerSuff)
			self.trayIcon.setIcon(QIcon.fromTheme("mailChecker_stop"))

		#print dateStamp() ,  self.checkResult, '  received Result\n', path_, self.labelStat.text()
		i = 0
		newMailExist = False
		self.listNewMail = ''
		x = ''
		if not hasattr(self, 'accountList') : self.accountList = QStringList()
		#for item in self.accountList : print item.toLocal8Bit().data(), 'accList'
		count = len(self.label) - 1
		for accountName in self.accountList :
			self.Settings.beginGroup(accountName)
			enabled = self.Settings.value('Enabled').toString()
			connectMethod = self.Settings.value('connectMethod').toString()
			self.Settings.endGroup()
			IDLE = True if connectMethod == 'imap\idle' else False
			DISABLED = True if enabled != '1' else False
			try :
				if DISABLED :
					if hasattr(self, 'label') and i>= count : self.createDialogItem(i)
					accountName_ = self.accPref + accountName + self.accSuff
					accountTT = self.accTTPref + self.tr._translate('Account') + \
								self.accTTSuff + ' ' + accountName + \
								self.tr._translate(' disabled')
					text_1 = self.countPref + self.tr._translate('disabled') + \
							 self.countSuff
					text_2 = self.countTTPref + '<pre>' + \
							 self.tr._translate('disabled') + \
							 '</pre>' + self.countTTSuff
				elif int(self.checkResult[i][2]) > 0 and not IDLE :
					self.listNewMail += '<pre>' + accountName + '&#09;' + \
										 str(self.checkResult[i][2]) + ' | ' + \
										 str(self.checkResult[i][6]) + '</pre>'
					newMailExist = True
					if hasattr(self, 'label') :
						self.label[i].setStyleSheet(self.accountSColourStyle)
						self.countList[i].setStyleSheet(self.countSColourStyle)
					accountName_ = self.accSPref + accountName + self.accSSuff
					accountTT = self.accTTSPref + self.tr._translate('Account') + \
												self.accTTSSuff + ' ' + accountName
					text_1 = self.countSPref + str(self.checkResult[i][1]) + ' | ' + \
							 str(self.checkResult[i][6]) + self.countSSuff
					text_2 = self.countTTSPref + '<pre>' + self.tr._translate('New : ') + \
							 str(self.checkResult[i][2]) + '</pre><pre>' + self.tr._translate('UnRead : ') + \
							 str(self.checkResult[i][6]) + '</pre>' + self.countTTSSuff
				elif int(self.checkResult[i][2]) < 1 and not IDLE :
					if hasattr(self, 'label') :
						self.label[i].setStyleSheet(self.accountColourStyle)
						self.countList[i].setStyleSheet(self.countColourStyle)
					accountName_ = self.accPref + accountName + self.accSuff
					accountTT = self.accTTPref + self.tr._translate('Account') + \
												self.accTTSuff + ' ' + accountName
					text_1 = self.countPref + str(self.checkResult[i][1]) + ' | ' + \
							 str(self.checkResult[i][6]) + self.countSuff
					text_2 = self.countTTPref + '<pre>' + self.tr._translate('New : ') + \
							 str(self.checkResult[i][2]) + '</pre><pre>' + self.tr._translate('UnRead : ') + \
							 str(self.checkResult[i][6]) + '</pre>' + self.countTTSuff

				if not IDLE or DISABLED :
					self.label[i].setText(accountName_)
					self.label[i].setToolTip(accountTT)
					self.countList[i].setText(text_1)
					self.countList[i].setToolTip(text_2)

			except Exception, x :
				print dateStamp() ,  x, '  refresh_1'
			finally:
				pass
			i += 1

		countOfNodes = len(self.checkResult)
		matched = True if countOfNodes == len(self.accountList) else False
		#print dateStamp() ,  newMailExist and not noCheck and matched, countOfNodes
		if newMailExist and not noCheck and matched :
			''' detect count of new mail '''
			countOfAllNewMail = 0
			overLoad = False
			i = 0
			while i < countOfNodes :
				countOfAllNewMail += int(self.checkResult[i][2])
				i += 1
			if self.maxShowedMail < countOfAllNewMail :
				overLoad = True
				self.eventNotification('<b>' + self.tr._translate('There are more then') + '<br></br>' + \
										'&#09;' + str(self.maxShowedMail) + \
										' (' + str(countOfAllNewMail) + ') ' + \
										self.tr._translate('messages.') + '</b>', \
										{0 : 0}, '' )
			i = 0
			while i < countOfNodes and not overLoad :
				""" collected mail headers for each account """
				str_ = self.checkResult[i][4]
				encoding = self.checkResult[i][5].split('\n')
				STR_ = ''
				numbers = self.checkResult[i][7].split()
				numbers.reverse()
				if str_ not in ['', ' ', '0'] :
					#print dateStamp() ,  str_
					j = 0
					k = 0
					groups = 0
					msgAttributes = str_.split('\r\n\r\n')
					msgAttributes.reverse()
					for _str in msgAttributes :
						if _str not in ['', ' ', '\n', '\t', '\r', '\r\n'] :
							mailAttrStr = self.someFunctions.mailAttrToSTR(_str, encoding[j])
							_str_raw = htmlWrapper(mailAttrStr, self.mailAttrColor)
							## None is means deprecated mail header
							if _str_raw is None :
								j += 1
								continue
							''' grouping mail '''
							STR_ += '<br>' + self.tr._translate('In ') + \
									self.fieldBoxPref + self.accountList[i] + \
									self.fieldBoxSuff + ':</br><br>' + _str_raw
							k += 1
							if k == self.mailsInGroup :
								''' mail group notification '''
								l = groups * k
								m = l + k
								#print [numbers[l:m]], (l, m)
								self.eventNotification('<b><u>' + \
										self.tr._translate('New Mail :') + \
										'</u></b>' + STR_, \
										{self.accountList[i] : string.join(numbers[l:m], ' ')}, \
										self.accountCommand[ self.accountList[i] ])
								k = 0
								groups += 1
								STR_ = ''
						j += 1
				''' tail of mail group notification '''
				if STR_ != '' :
					l = groups * self.mailsInGroup
					#print [numbers[l:]]
					self.eventNotification('<b><u>' + \
										self.tr._translate('New Mail :') + \
										'</u></b>' + STR_, \
										{self.accountList[i] : string.join(numbers[l:], ' ')}, \
										self.accountCommand[ self.accountList[i] ])
				i += 1

		if self.listNewMail == '' :
			self.listNewMail = self.tr._translate("No new mail")
		self.trayIcon.setToolTip( "<b><u>" + \
								self.tr._translate('M@il Checker') + \
								"</u></b><br>" + \
								self.headerPref + self.listNewMail + self.headerSuff)

		i = 0
		while i < countOfNodes :
			if self.checkResult[i][3] not in ['', ' ', '0', '\n'] :
				self.ErrorMsg += self.checkResult[i][3]
			i += 1
		if self.ErrorMsg not in ['', ' ', '0', '\n'] :
			if self.Settings.value('ShowError').toString() != '0' and not noCheck :
				self.eventNotification( QString().fromUtf8(self.ErrorMsg) )

		if not self.connectIconsFlag :
			self.connectIconsFlag = self.connect(self.icon, SIGNAL('clicked()'), self._enterPassword)
		#print 'connect :', self.connectIconsFlag

		self.GeneralLOCK.unlock()
		#print dateStamp() ,  'refresh out'

	def createConfigurationInterface(self, parent):
		self.editAccounts = EditAccounts(self, parent)
		parent.addPage(self.editAccounts, self.tr._translate("Accounts"))
		self.appletSettings = AppletSettings(self, parent)
		parent.addPage(self.appletSettings, self.tr._translate("Settings"))
		#self.passwordManipulate = PasswordManipulate(self, parent)
		parent.addPage(self.passwordManipulate, self.tr._translate("Password Manipulation"))
		self.fontsNcolour = Font_n_Colour(self, parent)
		parent.addPage(self.fontsNcolour, self.tr._translate("Font and Colour"))
		self.filters = Filters(self, parent)
		parent.addPage(self.filters, self.tr._translate("Filters"))
		self.proxy = ProxySettings(self, parent)
		parent.addPage(self.proxy, self.tr._translate("Proxy"))
		self.examples = Examples(self, parent)
		parent.addPage(self.examples, self.tr._translate("EXAMPLES"))
		self.connect(parent, SIGNAL("okClicked()"), self.configAccepted)
		self.connect(parent, SIGNAL("cancelClicked()"), self.configDenied)
		self.connect(self.dialog, SIGNAL('settingsCancelled()'), self.passwordManipulate.initKeyring)

	def showConfigurationInterface(self, key = False):
		if not hasattr(self, 'dialog') or self.dialog is None :
			self.dialog = PageDialog(self)
			self.createConfigurationInterface(self.dialog)
		if not key :
			self.dialog.exec_()
		else :
			self.dialog.showNormal()

	def settingsChangeComplete(self):
		if self.editAccounts.StateChanged :
			self.sound.Attention.play()
			answer = QMessageBox.question (self.dialog, \
					 self.tr._translate('Accounts'), \
					 self.tr._translate('Accounts:\nChanges was not completed.'), \
					 self.tr._translate('Save'), \
					 self.tr._translate('Cancel'))
			if not answer : self.editAccounts.parameters.saveAccountData()
		self.appletSettings.refreshSettings()
		self.fontsNcolour.refreshSettings()
		if self.filters.StateChanged[0] or self.filters.StateChanged[1] :
			self.sound.Attention.play()
			answer = QMessageBox.question (self.dialog, \
					 self.tr._translate('Filters'), \
					 self.tr._translate('Filters:\nChanges was not completed.'), \
					 self.tr._translate('Save'), \
					 self.tr._translate('Cancel'))
			if not answer :
				if self.filters.StateChanged[0] : self.filters.saveFilter(0)
				if self.filters.StateChanged[1] : self.filters.saveFilter(1)
		if self.proxy.StateChanged :
			self.sound.Attention.play()
			answer = QMessageBox.question (self.dialog, \
					 self.tr._translate('Proxy'), \
					 self.tr._translate('Proxy:\nChanges was not completed.'), \
					 self.tr._translate('Save'), \
					 self.tr._translate('Cancel'))
			if not answer : self.proxy.saveData()
		self.Settings.setValue('UseProxy', 'True' if self.proxy.enableProxy.checkState()==Qt.Checked else 'False')
		if self.passwordManipulate.StateChanged :
			self.sound.Attention.play()
			answer = QMessageBox.question (self.dialog, \
					 self.tr._translate('Password Manipulation'), \
					 self.tr._translate('Password Manipulation:\nChanges was not completed.'), \
					 self.tr._translate('Save'), \
					 self.tr._translate('Cancel'))
			if not answer : self.passwordManipulate.saveData()
			else : self.passwordManipulate.rejectChanges()
		self.Settings.sync()

	def checkAccess(self):
		if self.Keyring :
			if self.Keyring.open_Keyring() : return True
			else :
				self.eventNotification(self.tr._translate("Warning :\nAccess denied!"))
		else :
			self.eventNotification(self.tr._translate(\
				"Warning :\nSecurity service for password restore\ndon`t choiced!"))
			if hasattr(self, 'dialog') and self.dialog is not None :
				self.dialog.tabWidget.setCurrentWidget(self.passwordManipulate)
			else :
				self.showConfigurationInterface(True)
				self.dialog.tabWidget.setCurrentWidget(self.passwordManipulate)
				self.dialog.exec_()
		return False

	def configAccepted(self):
		self.disconnect(self, SIGNAL('refresh'), self.refreshData)
		if self.Keyring is None and self.passwordManipulate.StateChanged \
				and self.passwordManipulate.getProposedKeyring() is not None :
			self.continueReset()
		elif self.Keyring is not None and self.checkAccess() :
			self.continueReset()
		else :
			self.configHide()

	def continueReset(self):
		self.settingsChangeComplete()
		self.disableIconClick()
		self.Timer.stop()
		self.configHide()
		self.connect(self, SIGNAL('refresh'), self.refreshData)
		self.emit(SIGNAL('killThread'))

	@pyqtSlot(name='configHide')
	def configDenied(self):
		if hasattr(self, 'dialog') and self.dialog is not None :
			self.disconnect(self.dialog, SIGNAL("okClicked()"), self.configAccepted)
			self.disconnect(self.dialog, SIGNAL("cancelClicked()"), self.configDenied)
			self.disconnect(self.dialog, SIGNAL('settingsCancelled()'), self.passwordManipulate.initKeyring)
			self.dialog._close()
			del self.dialog
			self.dialog = None

	def _enterPassword(self):
		if not self.initStat :
			if self.checkAccess() :
				#print dateStamp() ,  '_eP'
				self.enterPassword()
			else :
				#print dateStamp() ,  '_eP_1'
				return None
		else :
			self.disableIconClick()
			x = ''
			try:
				self.Timer.stop()
			except Exception, x :
				print dateStamp() ,  x, '  _entP'
			finally:
				pass
			self.emit(SIGNAL('killThread'))
			print dateStamp() ,  'stop_eP'

	def enterPassword(self):
		if self.checkAccess() :
			#print dateStamp() ,  'eP'
			self.emit(SIGNAL('access'))
		else :
			#print dateStamp() ,  'eP_1'
			self.initStat = False

	def eventClose(self):
		self.initStat = False
		if self.closeFlag :
			print dateStamp() ,  '  eventCloseMethod'
			self.disconnect(self, SIGNAL('refresh'), self.refreshData)
			self.disconnect(self, SIGNAL('access'), self.processInit)
			self.disconnect(self, SIGNAL('destroyed()'), self.eventClose)
			self.disconnect(self, SIGNAL('killThread'), self.killMailCheckerThread)
			self.idleThreadMessage.disconnect(self.idleMessage)
			self.idleingStopped.disconnect(self.idleingStoppedEvent)
			self.disableIconClick()
			self.configHide()
			self.MessageStackWidget.close()
			self.Timer.stop()
			if self.Keyring : self.Keyring.close_Keyring()
			try :
				self.someFunctions.savePOP3Cache()
			except IOError, x :
				print dateStamp() ,x, '  eventClose_2'
			finally : pass
			self.updateGeometry()
			self.Settings.setValue('Geometry', self.saveGeometry())
			self.killMailCheckerThread()
			self.GeneralLOCK.unlock()
			count = self.initValue('stayDebLog', '5')
			cleanDebugOutputLogFiles(int(count))
			self.Settings.sync()
			if self.locked : self.unlock()
			print dateStamp() , "MailChecker destroyed manually."
			if self.SoundEnabled :
				#self.sound.AppletClosed.finished.connect(self.close)
				self.sound.AppletClosed.play()
		self.closeFlag = False
		self.closeEvent(QEvent(QEvent.Close))

	def closeEvent(self, ev):
		if self.closeFlag :
			self.eventClose()
			ev.accept()
		#sys.stderr.close()
		sys.stdout.close()
		self.close()

	def killMailCheckerThread(self):
		if hasattr(self, 'T') :
			#print dateStamp() ,'   killMetod Up'
			if self.T.isRunning() : self.T._terminate()
		# stopping idles mail
		for item in self.idleMailingList :
			try :
				item.stop()
			except Exception, err :
				print dateStamp(), err
			finally : pass
		''' wait for idle terminate '''
		i = WaitIdle(self)
		i.start()
		print dateStamp() , "Processes are killed."

	def idleingStoppedEvent(self):
		print dateStamp() , 'idleingStoppedEvent'
		self.someFunctions.savePOP3Cache()
		self.initStat = False
		
		# refresh color & font Variables
		self.initPrefixAndSuffix()
		
		self.initWorkParameters()
		
		# refresh plasmoid Header
		self.TitleDialog.setText(self.headerPref + self.title + self.headerSuff)
		self.TitleDialog.setStyleSheet(self.headerColourStyle)

		# refresh MailBox Dialog
		self.createMailBoxDialog()
		self.setLayout(self.layout)

		self.emit(SIGNAL('refresh'))
		print dateStamp() , 'idleingStoppedEvent_1'

	def mouseDoubleClickEvent(self, ev):
		self.showConfigurationInterface()

	def reloadApp(self): self.enterPassword()

	def __del__(self): self.eventClose()

	def idleMessage(self, d):
		# print d
		# stopping emitted idle mail
		if d['state'] == SIGNSTOP :
			itm = None
			for item in self.idleMailingList :
				if item.name == d['acc'] : itm = item
			#print self.idleMailingList, '<--|'
			i = 0
			if not hasattr(self, 'accountList' ) : self.accountList = QStringList()
			#for item in self.accountList : print item.toLocal8Bit().data(), 'accList_IDLE'
			for accountName in self.accountList :
				try :
					if d['acc'] == accountName :
						if hasattr(self, 'label') :
							self.label[i].setStyleSheet(self.accountColourStyle)
							self.countList[i].setStyleSheet(self.countColourStyle)
						accountName_ = self.accPref + accountName + self.accSuff
						accountTT = self.accTTPref + self.tr._translate('Account') + \
									self.accTTSuff + ' ' + accountName + '<br>(IDLE stopped)'

						self.label[i].setText(accountName_)
						self.label[i].setToolTip(accountTT)
						break
					i += 1
				except Exception, err :
					print dateStamp(), err, 'idle_stop'
				finally : pass
			if itm is not None :
				self.eventNotification( itm.name + self.tr._translate(' is not active.' ))
				self.idleMailingList.remove(itm)
			#print self.idleMailingList, '<--'
			return None
		#
		# show error notify from emitted idle mail
		if d['state'] == SIGNERRO :
			self.eventNotification( "In %s error: %s"%(d['acc'], \
									str([QString(s).toLocal8Bit().data() for s in d['msg']])) )
			return None
		#
		# show init or new mail data and notify
		i = 0
		self.listNewMail = ''
		if not hasattr(self, 'accountList' ) : self.accountList = QStringList()
		#for item in self.accountList : print item.toLocal8Bit().data(), 'accList_IDLE1'
		for accountName in self.accountList :
			try :
				if d['acc'] == accountName :
					self.listNewMail += accountName + '(IDLE)\t' + \
											str(d['msg'][1]) + ' | ' + \
											str(d['msg'][2])
					newMailExist = True
					if hasattr(self, 'label') :
						self.label[i].setStyleSheet(self.accountSColourStyle)
						self.countList[i].setStyleSheet(self.countSColourStyle)
					accountName_ = self.accSPref + accountName + self.accSSuff
					accountTT = self.accTTSPref + self.tr._translate('Account') + \
								self.accTTSSuff + ' ' + accountName + '<br>(IDLE)'
					text_1 = self.countSPref + str(d['msg'][0]) + ' | ' + \
							str(d['msg'][2]) + self.countSSuff
					text_2 = self.countTTSPref + '<pre>' + self.tr._translate('New : ') + \
							str(d['msg'][1]) + '</pre><pre>' + self.tr._translate('UnRead : ') + \
							str(d['msg'][2]) + '</pre>' + self.countTTSSuff

					self.label[i].setText(accountName_)
					self.label[i].setToolTip(accountTT)
					self.countList[i].setText(text_1)
					self.countList[i].setToolTip(text_2)
				i += 1
			except Exception, err :
				print dateStamp(), err, 'idle_newMail'
			finally : pass
		if d['state'] == SIGNDATA :
			self.trayIcon.showMessage ( self.tr._translate('M@il Checker'), \
								self.listNewMail, \
								QSystemTrayIcon.Information, 5000 )
			''' detect count of new mail '''
			countOfAllNewMail = d['msg'][1]
			overLoad = False
			if self.maxShowedMail < countOfAllNewMail :
				overLoad = True
				self.eventNotification('<b>' + self.tr._translate('There are more then') + '<br></br>' + \
										'&#09;' + str(self.maxShowedMail) + \
										' (' + str(countOfAllNewMail) + ') ' + \
										self.tr._translate('messages.') + '</b>', \
										{0 : 0}, '' )
			if not overLoad :
				j = 0
				STR_ = ''
				k = 0
				groups = 0
				numbers = d['msg'][4].split()
				numbers.reverse()
				msgAttributes = string.split(d['msg'][3], '\r\n\r\n')
				msgAttributes.reverse()
				for _str in msgAttributes :
					if _str not in ['', ' ', '\n', '\t', '\r', '\r\n'] :
						mailAttrStr = self.someFunctions.mailAttrToSTR(_str)
						_str_raw = htmlWrapper(mailAttrStr, self.mailAttrColor)
						## None is means deprecated mail header
						if _str_raw is None :
							j += 1
							continue
						STR_ += '<br>' + self.tr._translate('In ') + \
								self.fieldBoxPref + d['acc'] + self.fieldBoxSuff + ':</br><br>' + \
								_str_raw
						k += 1
						if k == self.mailsInGroup :
							''' mail group notification '''
							l = groups * k
							m = l + k
							self.eventNotification('<b><u>' + \
									self.tr._translate('New Mail :') + \
									'</u></b>' + STR_, \
									{d['acc'] : string.join(numbers[l:m], ' ')}, \
									self.accountCommand[ d['acc'] ])
							k = 0
							groups += 1
							STR_ = ''
					j += 1
				if STR_ != '' :
					l = groups * self.mailsInGroup
					msg = '<b><u>' + self.tr._translate('New Mail :') + '</u></b>' + STR_
					self.eventNotification( msg, \
											{d['acc'] : string.join(numbers[l:], ' ')}, \
											self.accountCommand[ d['acc'] ])
