# -*- coding: utf-8 -*-
from gluon import *
from gluon.dal import SQLCustomType
import logging, datetime, m2secret, hashlib
from applications.gextiendas.modules.settings import Settings
logger = logging.getLogger(" >>>> modules/adminsettings >>>> Gextiendas: ")
logger.setLevel(logging.DEBUG)


class Cifrar:

	def __init__(self):
		self.key= hashlib.sha256("fAdfg234f'wHfdh50ui34jkerjkerjkjfrwcwlmc-EE0Awvtasdfa").digest()
	def __call__(self,value):
		secret = m2secret.Secret()
		secret.encrypt(value, self.key)
		return secret.serialize()
	def formatter(self,value):
		secret = m2secret.Secret()
		secret.deserialize(value)
		return (secret.decrypt(self.key), None)


class Adminsettings(object):

	def __init__(self, db):
		self.db=db
		try:
			self.define_tables()
		except Exception as ex:
			logger.debug(ex)
			pass

	def define_tables(self):
		config=Settings()	
		data= Cifrar()
		cryp = SQLCustomType(type ='text', native ='longtext', encoder =(lambda x: data(x)), decoder = (lambda x: data.formatter(x)[0] ))
		self.db.define_table('adminsettings',
			Field('mailserver', 'string'),
			Field('username', 'string', length=128, requires=IS_NOT_EMPTY(error_message="No puede estar vacío")),
			Field('password', type=cryp, length=256, readable=False, label='Password'),
			Field('emailfrom', 'string', length=128, requires=IS_EMAIL(error_message="Formato de email incorrecto")),
			Field('blogitems', 'integer', default=20),
			Field('messageitems', 'integer', default=15),
			Field('bloglistitems', 'integer', default=15),
			Field('orderlistitems', 'integer', default=15),
			Field('useritems', 'integer', default=15),
			Field('subscriptionitems', 'integer', default=15),
			Field('productitems', 'integer', default=50),
			Field('queryitems', 'integer', default=15),
			Field('querylistitems', 'integer', default=15),
			Field('invoiceitems', 'integer', default=15),
			Field('tax', 'decimal(10,2)'),
			Field('bank_account', 'string', length="30", notnull=False),
			Field('beneficiary', 'string', length="120", label="Beneficiario"),
			Field('bank', 'string', length="120", label="Entidad bancaria"),
			Field('serialinit','integer',default=1000101),
			migrate=config.settings['migrate'])
		if config.settings['data_migrate']:
			if self.db(self.db.adminsettings).isempty():
				self.db.adminsettings.insert(mailserver="mail.server", 
											username="email@dominio.com", 
											password="password",
											emailfrom="email@dominio.com",
											tax="21.00",
											bank_account="bank account",
											beneficiary="beneficiario",
											bank="banco")
