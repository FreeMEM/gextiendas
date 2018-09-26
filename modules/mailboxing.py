# -*- coding: utf-8 -*-
from gluon import *
from gluon.globals import current
from regnews import Regnews
import logging, datetime
from settings import Settings
logger = logging.getLogger(" >>>> modules/Mailbox >>>> GestionExperta: ")
logger.setLevel(logging.DEBUG)

class Mailboxing(object):
	def __init__(self, db):
		Regnews(db)
		self.db=db
		self.T = current.T
		try:
			self.define_tables()
		except Exception as ex:
			pass


	def define_tables(self):
		config=Settings()
		self.db.define_table('mailbox',
			Field('regnews', 'reference regnews'),
			Field('message', 'text', notnull=True, requires=IS_NOT_EMPTY(error_message=self.T("Please tell me why you want to contact me"))),
			Field('comment', 'text', notnull=False),
			Field('messread', 'boolean', default=False),
			Field('created_on','datetime',default=datetime.datetime.now()),
			migrate=config.settings['migrate'])