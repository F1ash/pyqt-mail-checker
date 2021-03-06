# -*- coding: utf-8 -*-
#  Translator.py
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

from PyQt4.QtCore import QTranslator, QString
from Utils.Functions import lang as Lang
import os.path, sys

class Translator(QTranslator):
	def __init__(self, context = '', parent=None):
		QTranslator.__init__(self, parent)

		lang = Lang[0][:2]
		_Path = self.user_or_sys(lang + '.qm')
		#print 'Tr:' ,  lang, _Path
		self.load(QString(lang), QString(_Path), QString('qm'))
		self.context = context

	def user_or_sys(self, path_):
		return os.path.join(sys.path[0], 'misc', path_)

	def _translate(self, sourceText):
		res = self.translate(self.context, sourceText)
		#print res, 'tr:', self.context, sourceText
		if len(res) == 0:
			res = QString(sourceText)
		return res
