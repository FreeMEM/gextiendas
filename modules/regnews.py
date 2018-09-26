# -*- coding: utf-8 -*-
from gluon import *
import logging, datetime
from settings import Settings
logger = logging.getLogger(" >>>> modules/regnews >>>> GestionExperta: ")
logger.setLevel(logging.DEBUG)

class Regnews(object):

	def __init__(self, db):
		self.db=db
		try:
			self.define_tables()
		except:
			pass
		
	def define_tables(self):
		config=Settings()
		self.db.define_table('regnews',
			Field('email', 'string', length=128, notnull=True, requires=[IS_EMAIL(error_message="email incorrecto"), IS_NOT_EMPTY(error_message="Debes poner tu correo electrónico")]),
			Field('user', 'reference auth_user', notnull=False),
			Field('name', 'string', length=50, notnull=False),
			Field('website', 'string', length=128, notnull=False),
			Field('phone', 'string', length=18, notnull=False),
			Field('city', 'string', length=40, notnull=False),
			Field('province', 'string', length=40, notnull=False),
			Field('news', 'boolean', default=True),
			Field('verification_code', 'string', length=64, notnull=False),
			Field('verified_on', 'datetime', default=None, notnull=False),
			Field('created_on','datetime',default=datetime.datetime.now()),
			Field('suscribed_on', 'datetime', default=None, notnull=False),
			Field('unsuscribed_on', 'datetime', default=None, notnull=False),
			Field('ip', 'string', length=20, notnull=False), #almacena ip del cliente en la creación del registro
			migrate=config.settings['migrate'])

		self.db.executesql('CREATE INDEX IF NOT EXISTS verification_code_idx ON regnews (verification_code);')

		# self.db.regnews.city.widget = SQLFORM.widgets.autocomplete(request, db.cities.poblacion, limitby=(0,10), min_length=2)
		# self.db.regnews.province.widget = SQLFORM.widgets.autocomplete(request, db.province.provincia, limitby=(0,10), min_length=2)