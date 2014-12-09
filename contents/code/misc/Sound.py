# -*- coding: utf-8 -*-
#  Sound.py
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

from PyQt4.phonon import Phonon

class Sound():
	def __init__(self, parent = None):
		#print Phonon.BackendCapabilities.availableAudioOutputDevices()
		self.AppletStarted = Phonon.createPlayer(Phonon.NotificationCategory, \
				Phonon.MediaSource("/usr/share/sounds/freedesktop/stereo/device-added.oga"))

		self.AppletClosed  = Phonon.createPlayer(Phonon.NotificationCategory, \
				Phonon.MediaSource("/usr/share/sounds/freedesktop/stereo/device-removed.oga"))

		self.Accepted      = Phonon.createPlayer(Phonon.NotificationCategory, \
				Phonon.MediaSource("/usr/share/sounds/freedesktop/stereo/camera-shutter.oga"))

		self.Frozen        = Phonon.createPlayer(Phonon.NotificationCategory, \
				Phonon.MediaSource("/usr/share/pyqt-mail-checker/misc/frozen.ogg"))

		self.Cleared       = Phonon.createPlayer(Phonon.NotificationCategory, \
				Phonon.MediaSource("/usr/share/sounds/freedesktop/stereo/trash-empty.oga"))

		self.Complete      = Phonon.createPlayer(Phonon.NotificationCategory, \
				Phonon.MediaSource("/usr/share/sounds/freedesktop/stereo/complete.oga"))

		self.Failed        = Phonon.createPlayer(Phonon.NotificationCategory, \
				Phonon.MediaSource("/usr/share/sounds/freedesktop/stereo/dialog-error.oga"))

		self.NewMessage    = Phonon.createPlayer(Phonon.NotificationCategory, \
				Phonon.MediaSource("/usr/share/sounds/freedesktop/stereo/bell.oga"))

		self.Attention     = Phonon.createPlayer(Phonon.NotificationCategory, \
				Phonon.MediaSource("/usr/share/sounds/freedesktop/stereo/dialog-warning.oga"))
