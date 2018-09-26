# -*- coding: utf-8 -*-
from gluon import *
import logging, datetime
from settings import Settings
logger = logging.getLogger(" >>>> modules/province >>>> GestionExperta: ")
logger.setLevel(logging.DEBUG)

class Province(object):

	def __init__(self, db):
		self.db=db
		try:
			self.define_tables()
		except:
			pass
		
	def define_tables(self):
		config=Settings()
		self.db.define_table('province',
			Field('provincia', 'string', length=45,  notnull=True),
			Field('provinciaseo', 'string', length=45,  notnull=True, unique=True),
			Field('provincia3', 'string', length=45,  notnull=True),
			migrate=config.settings['migrate'])