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

import getpass
import os
import sys
import ConfigParser
import base64

from keyring.util.escape import escape as escape_for_ini
from keyring.util import properties

try:
	from abc import ABCMeta, abstractmethod, abstractproperty
except ImportError:
	# to keep compatible with older Python versions.
	class ABCMeta(type):
		pass

	def abstractmethod(funcobj):
		return funcobj

	def abstractproperty(funcobj):
		return property(funcobj)

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

_KEYRING_SETTING = 'keyring-setting'
_CRYPTED_PASSWORD = 'crypted-password'
_BLOCK_SIZE = 32
_PADDING = '0'

def to_unicode(obj):
	if not isinstance(obj, basestring) and hasattr(obj, 'toLocal8Bit') :
		return obj.toLocal8Bit().data()
	elif not isinstance(obj, basestring) and hasattr(obj, 'toUtf8') :
		return obj.toUtf8().data()
	return obj

class PasswordSetError(Exception):
	"""Raised when the password can't be set.
	"""

class KeyringBackend(object):
	"""The abstract base class of the keyring, every backend must implement
	this interface.
	"""
	__metaclass__ = ABCMeta

	@abstractmethod
	def supported(self):
		"""Return if this keyring supports current environment:
		-1: not applicable
		 0: suitable
		 1: recommended
		"""
		return -1

	@abstractmethod
	def get_password(self, service, username):
		"""Get password of the username for the service
		"""
		return None

	@abstractmethod
	def set_password(self, service, username, password):
		"""Set password for the username of the service
		"""
		raise PasswordSetError("reason")

	def get_password(self, service, username):
		"""Override the get_password() in KeyringBackend.
		"""
		try:
			password = self.keyring_impl.password_get(service, username)
		except OSError:
			password = None
		return password

	def set_password(self, service, username, password):
		"""Override the set_password() in KeyringBackend.
		"""
		try:
			self.keyring_impl.password_set(service, username, password)
		except OSError, e:
			raise PasswordSetError(e.message)

class BasicFileKeyring(KeyringBackend):
	"""BasicFileKeyring is a file-based implementation of keyring.

	It stores the password directly in the file, and supports the
	encryption and decryption. The encrypted password is stored in base64
	format.
	"""

	@properties.NonDataProperty
	def file_path(self):
		"""
		The path to the file where passwords are stored.
		"""
		return os.path.join(os.path.expanduser('~'), self.filename)

	@abstractproperty
	def filename(self):
		"""The filename used to store the passwords.
		"""
		pass

	@abstractmethod
	def encrypt(self, password):
		"""Encrypt the password.
		"""
		pass

	@abstractmethod
	def decrypt(self, password_encrypted):
		"""Decrypt the password.
		"""
		pass

	def get_password(self, service, username):
		"""Read the password from the file.
		"""
		service = escape_for_ini(service)
		username = escape_for_ini(username)

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
		return password

	def set_password(self, service, username, password):
		"""Write the password in the file.
		"""
		service = escape_for_ini(service)
		username = escape_for_ini(username)

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

class CryptedFileKeyring(BasicFileKeyring):
	"""PyCrypto File Keyring"""
	filename = 'crypted_pass.cfg'
	crypted_password = None
	def __init__(self, parent = None):
		self.name = 'CryptedFileKeyring'
		self.appletName = 'pyqt-mail-checker'
		self.prnt = parent

	def open_Keyring(self): pass

	def close_Keyring(self): pass

	def supported(self):
		"""Applicable for all platforms, but not recommend"
		"""
		try:
			from Crypto.Cipher import AES
			status = 0
		except ImportError:
			status = -1
		return status

	def has_entry(self, key, _folder = None): pass

	def get_password(self, key, _folder = None): pass

	def set_password(self, key, password, _folder = None): pass

	def _getpass(self, *args, **kwargs):
		"""Wrap getpass.getpass(), so that we can override it when testing.
		"""

		return getpass.getpass(*args, **kwargs)

	def _init_file(self):
		"""Init the password file, set the password for it.
		"""

		password = None
		while 1:
			if not password:
				password = self._getpass("Please set a password for your new keyring")
				password2 = self._getpass('Password (again): ')
				if password != password2:
					sys.stderr.write("Error: Your passwords didn't match\n")
					password = None
					continue
			if '' == password.strip():
				# forbid the blank password
				sys.stderr.write("Error: blank passwords aren't allowed.\n")
				password = None
				continue
			if len(password) > _BLOCK_SIZE:
				# block size of AES is less than 32
				sys.stderr.write("Error: password can't be longer than 32.\n")
				password = None
				continue
			break

		# hash the password
		import crypt
		self.crypted_password = crypt.crypt(password, password)

		# write down the initialization
		config = ConfigParser.RawConfigParser()
		config.add_section(_KEYRING_SETTING)
		config.set(_KEYRING_SETTING, _CRYPTED_PASSWORD, self.crypted_password)

		config_file = open(self.file_path,'w')
		config.write(config_file)

		if config_file:
			config_file.close()

	def _check_file(self):
		"""Check if the password file has been init properly.
		"""
		if os.path.exists(self.file_path):
			config = ConfigParser.RawConfigParser()
			config.read(self.file_path)
			try:
				self.crypted_password = config.get(_KEYRING_SETTING,
													_CRYPTED_PASSWORD)
				return self.crypted_password.strip() != ''
			except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
				pass
		return False

	def _auth(self, password):
		"""Return if the password can open the keyring.
		"""
		import crypt
		return crypt.crypt(password, password) == self.crypted_password

	def _init_crypter(self):
		"""Init the crypter(using the password of the keyring).
		"""
		# check the password file
		if not self._check_file():
			self._init_file()

		password = self._getpass("Please input your password for the keyring")

		if not self._auth(password):
			sys.stderr.write("Wrong password for the keyring.\n")
			raise ValueError("Wrong password")

		# init the cipher with the password
		from Crypto.Cipher import AES
		# pad to _BLOCK_SIZE bytes
		password = password + (_BLOCK_SIZE - len(password) % _BLOCK_SIZE) * \
																	_PADDING
		return AES.new(password, AES.MODE_CFB)

	def encrypt(self, password):
		"""Encrypt the given password using the pycryto.
		"""
		crypter = self._init_crypter()
		return crypter.encrypt(password)

	def decrypt(self, password_encrypted):
		"""Decrypt the given password using the pycryto.
		"""
		crypter = self._init_crypter()
		return crypter.decrypt(password_encrypted)

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
					self.prnt.createKeyring("GnomeKeyring: %s doesn`t exist"%self.appletName)
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
			print "[ In Keyring.create_Keyring() ]: ", err
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
