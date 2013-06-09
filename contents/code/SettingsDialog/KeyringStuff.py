# -*- coding: utf-8 -*-
#  KeyringStuff.py
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

import os
import string
import ConfigParser
import base64
from os.path import join, expanduser, isfile
from Utils.Functions import randomString

KEYRING_SETTING = 'keyring-setting'
CRYPTED_PASSWORD = 'crypted-password'
BLOCK_SIZE = 32
PADDING = '\0'

try:
	import gnomekeyring as G
except ImportError:
	pass

try:
	from PyKDE4.kdeui import KWallet
except ImportError:
	kwallet_support = False
else:
	kwallet_support = True

def to_unicode(obj):
	if not isinstance(obj, basestring) and hasattr(obj, 'toUtf8') :
		return obj.toUtf8().data()
	elif not isinstance(obj, basestring) and hasattr(obj, 'toLocal8Bit') :
		return obj.toLocal8Bit().data()
	return obj

class PasswordSetError(Exception):
	"""Raised when the password can't be set.
	"""

class CryptedFileKeyring():
	"""PyCrypto File Keyring"""
	filename = 'crypted_pass.cfg'
	crypted_password = None
	def __init__(self, parent = None):
		self.name = 'CryptedFileKeyring'
		self.appletName = 'pyqt-mail-checker'
		self.file_path = join(expanduser("~/.config"), self.appletName, self.filename)
		self.prnt = parent
		self.password = None

	def open_Keyring(self):
		allowed = None
		try :
			if self.supported()>=0 :
				allowed = True if self._auth() else self.repeatAuth(allowed)
			if not allowed : self.close_Keyring()
		except Exception, err :
			print "[ In CryptedFileKeyring.open_Keyring() ]: ", err
		finally : pass
		return allowed

	def repeatAuth(self, allowed, count = 0):
		if not allowed and count < 3 :
			self.password = None
			result = self._check_file()
			allowed = self.repeatAuth(result, count+1)
		return allowed

	def create_Keyring(self, _password = None):
		self.password = to_unicode(_password)
		# hash the password
		import crypt
		self.crypted_password = crypt.crypt(self.password, self.password)

		# write down the initialization
		config = ConfigParser.RawConfigParser()
		config.add_section(KEYRING_SETTING)
		config.set(KEYRING_SETTING, CRYPTED_PASSWORD, self.crypted_password)

		config_file = open(self.file_path,'w')
		config.write(config_file)

		if config_file:
			config_file.close()

	def close_Keyring(self):
		if self.password :
			count = len(self.password)
			self.password = randomString(count)
			del self.password
			self.password = None

	def supported(self):
		"""Applicable for all platforms, but not recommend"""
		try:
			from Crypto.Cipher import AES
			status = 0
		except ImportError:
			status = -1
		return status

	def has_entry(self, key, _folder = None):
		folder = to_unicode(_folder) if _folder else self.appletName
		config = ConfigParser.RawConfigParser()
		config.read(self.file_path)
		return config.has_option(to_unicode(key), folder)

	def get_password(self, key, _folder = None):
		#get_password(self, service, username):
		"""Read the password from the file.
		"""
		folder = to_unicode(_folder) if _folder else self.appletName
		service = to_unicode(key)
		username = folder

		# load the passwords from the file
		config = ConfigParser.RawConfigParser()
		if os.path.exists(self.file_path):
			config.read(self.file_path)

		# fetch the password
		try:
			password_base64 = config.get(service, username).encode()
			# decode with base64
			password_encrypted = base64.decodestring(password_base64)
			# decrypted the password
			password = self.decrypt(password_encrypted).decode('utf-8')
		except (ConfigParser.NoOptionError, ConfigParser.NoSectionError):
			password = None
		finally : pass
		return password

	def set_password(self, key, _password, _folder = None):
		#set_password(self, service, username, password):
		"""Write the password in the file.
		"""
		password = to_unicode(_password)
		folder = to_unicode(_folder) if _folder else self.appletName
		service = to_unicode(key)
		username = folder

		# encrypt the password
		password_encrypted = self.encrypt(password.encode('utf-8'))
		# load the password from the disk
		config = ConfigParser.RawConfigParser()
		if os.path.exists(self.file_path):
			config.read(self.file_path)

		# encode with base64
		password_base64 = base64.encodestring(password_encrypted).decode()
		# write the modification
		if not config.has_section(service):
			config.add_section(service)
		config.set(service, username, password_base64)
		config_file = open(self.file_path,'w')
		config.write(config_file)

		if config_file:
			config_file.close()

	def _check_file(self):
		"""Check if the password file has been init properly.
		"""
		result = None
		if isfile(self.file_path):
			config = ConfigParser.RawConfigParser()
			config.read(self.file_path)
			try:
				self.crypted_password = config.get(KEYRING_SETTING,
													CRYPTED_PASSWORD)

			except (ConfigParser.NoSectionError, ConfigParser.NoOptionError), err:
				print "[ In CryptedFileKeyring._check_file() ]: ", err
			finally : pass
			if self.crypted_password.strip() != '' :
				if self.password is None :
					self.prnt.getKeyringPassword()
			else :
				self.prnt.createKeyring("%s: %s not inited"%(self.name, self.appletName))
		else :
			self.prnt.createKeyring("%s: %s not inited"%(self.name, self.appletName))
		result = self._auth()
		return result

	def _auth(self):
		"""Return if the password can open the keyring.
		"""
		if self.password and self.crypted_password :
			import crypt
			return crypt.crypt(self.password, self.password) == self.crypted_password
		return None

	def _init_crypter(self):
		"""Init the crypter(using the password of the keyring).
		"""
		# init the cipher with the password
		from Crypto.Cipher import AES
		# pad to BLOCK_SIZE bytes
		password = self.passwordComplete(self.password)
		# https://bugs.launchpad.net/pycrypto/+bug/997464/comments/2
		return AES.new(password, AES.MODE_CFB, "\0"*16, segment_size=128)

	def passwordComplete(self, password):
		return password + (BLOCK_SIZE - len(password) % BLOCK_SIZE) * PADDING

	def encrypt(self, _password):
		"""Encrypt the given password using the pycryto.
		"""
		password = to_unicode(_password)
		crypter = self._init_crypter()
		return crypter.encrypt(self.passwordComplete(password))

	def decrypt(self, _password_encrypted):
		"""Decrypt the given password using the pycryto.
		"""
		password_encrypted = to_unicode(_password_encrypted)
		crypter = self._init_crypter()
		password = crypter.decrypt(password_encrypted)
		while password.endswith(PADDING) : password = password[:-1]
		return password

# TODO : MateKeyring

class GnomeKeyring():
	def __init__(self, parent = None):
		self.name = 'GnomeKeyring'
		self.appletName = 'pyqt-mail-checker'
		self.prnt = parent

	def open_Keyring(self):
		allowed = False
		if self.supported()>=0 and G.is_available() :
			_gnome_keyrings = G.list_keyring_names_sync()
			allowed = True
			try :
				if self.appletName not in _gnome_keyrings :
					self.prnt.createKeyring("%s: %s doesn`t exist"%(self.name, self.appletName))
					return False
				self.KEYRING_NAME = self.appletName
			except Exception, err :
				allowed = False
			finally : pass
		return allowed

	def create_Keyring(self, password = None):
		try :
			G.create_sync(self.appletName, to_unicode(password))
		except Exception, err :
			print "[ In GnomeKeyring.create_Keyring() ]: ", err
		finally : pass

	def close_Keyring(self):
		if G.is_available() : G.lock_sync(self.appletName)

	def supported(self):
		try:
			import gnomekeyring as G
		except ImportError:
			return -1
		else:
			if ("GNOME_KEYRING_CONTROL" in os.environ and
				"DISPLAY" in os.environ and
				"DBUS_SESSION_BUS_ADDRESS" in os.environ):
				return 1
			else:
				return 0

	def has_entry(self, key, _folder = None):
		folder = _folder if _folder else self.appletName
		item_list = G.list_item_ids_sync(self.appletName)
		found = False
		for item in item_list :
			attr = G.item_get_attributes_sync(self.appletName, item)
			keyIn = 'user' in attr and 'domain' in attr
			if keyIn and attr['user']==to_unicode(key) and attr['domain']==folder :
				found = True
				break
		return found

	def get_password(self, key, _folder = None):
		if not G.is_available() : return None
		folder = _folder if _folder else self.appletName
		item_list = G.list_item_ids_sync(self.appletName)
		password = None
		# ♿ ☟ GnomeKeyring is glitch at find_network_password_sync
		i = 0
		_items = None
		while i < 10 :
			try :
				_items = G.find_network_password_sync(to_unicode(key), folder)
				break
			except G.CancelledError :
				i+=1
			except G.NoMatchError :
				i+=1
			finally : pass
		# ♿ ☝ GnomeKeyring is glitch at find_network_password_sync
		if _items :
			for item in _items :
				if item['keyring']==self.appletName :
					password = item['password']
					break
		return password

	def set_password(self, key, password, _folder = None):
		if not G.is_available() :
			self.prnt.Parent.eventNotification("%s not available." % self.name)
			return None
		folder = _folder if _folder else self.appletName
		try:
			G.item_create_sync(
				self.KEYRING_NAME, G.ITEM_NETWORK_PASSWORD,
				"Password for '%s' in '%s'" % (to_unicode(key), folder),
				{'user': to_unicode(key), 'domain': folder},
				to_unicode(password), True)
		except G.CancelledError:
			raise PasswordSetError("cancelled by user")
		finally : pass

class KDEKWallet():
	def __init__(self, parent = None):
		self.name = 'KDEKWallet'
		self.appletName = 'pyqt-mail-checker'

	def open_Keyring(self):
		if self.supported()<0 : return False
		self.wallet = KWallet.Wallet.openWallet(KWallet.Wallet.LocalWallet(), 0)
		if self.wallet is None : return False
		return True

	def create_Keyring(self, password = None):
		print "Incorrect request"

	def close_Keyring(self): 
		if hasattr(self, 'wallet') and not(self.wallet is None) :
			self.wallet.closeWallet(self.wallet.walletName(), True)

	def supported(self):
		if kwallet_support and os.environ.has_key('KDE_SESSION_UID'):
			return 1
		elif kwallet_support :
			return 0
		else:
			return -1

	def setFolder(self, folder):
		if not self.wallet.hasFolder(folder) :
			self.wallet.createFolder(folder)
		self.wallet.setFolder(folder)

	def has_entry(self, key, _folder = None):
		folder = _folder if _folder else self.appletName
		if hasattr(self, 'wallet') and not(self.wallet is None) :
			return not self.wallet.keyDoesNotExist(KWallet.Wallet.LocalWallet(), folder, key)
		return False

	def get_password(self, key, _folder = None):
		folder = _folder if _folder else self.appletName
		if hasattr(self, 'wallet') and not(self.wallet is None) :
			if self.wallet.keyDoesNotExist(KWallet.Wallet.LocalWallet(), folder, key):
				return None
			self.setFolder(folder)
			result = self.wallet.readPassword(key)[1]
			return result

	def set_password(self, key, password = None, folder = None):
		if hasattr(self, 'wallet') and not(self.wallet is None) :
			if key :
				self.setFolder(folder if folder else self.appletName)
				self.wallet.writePassword(key, password)

_all_keyring = None

KEYRING = {}

def get_all_keyring(obj):
	global _all_keyring
	global KEYRING
	KEYRING[0] = CryptedFileKeyring(obj)
	KEYRING[1] = GnomeKeyring(obj)
	KEYRING[2] = KDEKWallet(obj)
	if _all_keyring is None:
		_all_keyring = [ KEYRING[0], KEYRING[1], KEYRING[2] ]
	return _all_keyring
