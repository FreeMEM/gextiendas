# -*- coding: utf-8 -*-
from gluon import *
import logging, datetime
from settings import Settings
logger = logging.getLogger(" >>>> modules/cities >>>> GestionExperta: ")
logger.setLevel(logging.DEBUG)

class Cities(object):

	def __init__(self, db):
		self.db=db
		try:
			self.define_tables()
		except:
			pass
	def define_tables(self):
		config=Settings()		
		self.db.define_table('cities',
			Field('province', 'reference province'),
			Field('poblacion', 'string', length=45,  notnull=True),
			Field('provinciaseo', 'string', length=255,  notnull=True, unique=True),
			Field('postal', 'integer', default=None),
			Field('latitud', 'float', default=None),
			Field('longitud', 'float', default=None),
			migrate=config.settings['migrate'])
