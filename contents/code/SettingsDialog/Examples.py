# -*- coding: utf-8 -*-

from PyQt4.QtCore import QString
from PyQt4.QtGui import QWidget, QTextEdit, QGridLayout
from EXAMPLES import EXAMPLES

class Examples(QWidget):
	def __init__(self, obj, parent = None):
		QWidget.__init__(self, parent)

		browseText = QTextEdit()
		browseText.setReadOnly(True)

		examples = QString.fromUtf8(EXAMPLES)
		browseText.setText(examples)

		form = QGridLayout()
		form.addWidget(browseText,0,0)
		self.setLayout(form)

	def closeEvent(self, event):
		event.ignore()
		self.done(0)
