# -*- coding: utf-8 -*-
from gluon import *
import logging, datetime
from settings import Settings
logger = logging.getLogger(" >>>> modules/comments >>>> GestionExperta: ")
logger.setLevel(logging.DEBUG)

class Comments(object):

	def __init__(self, db):
		self.db=db
		try:
			self.define_tables()
		except:
			pass
	def define_tables(self):
		config=Settings()
		self.db.define_table('comments',
			Field('user', 'reference auth_user'),
			Field('regnews', 'reference regnews'),
			Field('blog', 'reference blog'),
			Field('public', 'boolean', default=True),
			Field('comment', 'text', notnull=True, requires=IS_NOT_EMPTY(error_message="Debes escribir un comentario")),
			Field('created_on','datetime',default=datetime.datetime.now()),
			migrate=config.settings['migrate'])
