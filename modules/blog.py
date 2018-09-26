# -*- coding: utf-8 -*-
from gluon import *
import logging, datetime
from settings import Settings
logger = logging.getLogger(" >>>> modules/blog >>>> Gxtiendas: ")
logger.setLevel(logging.DEBUG)

class Blog(object):

	def __init__(self, db, ckeditor):
		self.db=db
		self.ckeditor=ckeditor
		try:
			self.define_tables()
		except:
			pass
	def define_tables(self):
		config=Settings()	
		self.db.define_table('blog',
			Field('title', 'string', length=255),
			Field('subtitle', 'string', length=255),
			Field('urlfriendly','string', length=255),
			Field('image','reference images'),
			Field('public', 'boolean', default=True),
			Field('post', 'text', widget=self.ckeditor.widget),
			Field('created_on','datetime',default=datetime.datetime.now()),
			Field('user', 'reference auth_user'),
			Field('tags','string', length=255),
			migrate=config.settings['migrate'])
		self.db.blog.urlfriendly.compute=lambda row:IS_SLUG()(row.title)[0]
		self.db.blog.urlfriendly.requires = IS_NOT_EMPTY()
		self.db.blog.title.requires = IS_NOT_EMPTY()                
		self.db.blog.post.requires = IS_NOT_EMPTY()

class Draft(object):
	def __init__(self, db, ckeditor):
		self.db=db
		self.ckeditor=ckeditor
		try:
			self.define_tables()
		except:
			pass		
	def define_tables(self):
		config=Settings()
		self.db.define_table('draft',
			Field('title', 'string', length=255, notnull=True),
			Field('subtitle', 'string', length=255),
			Field('urlfriendly','string', length=255),
			Field('image','reference images'),
			Field('blog', 'reference blog'),
			Field('post', 'text', widget=self.ckeditor.widget),
			Field('created_on','datetime',default=datetime.datetime.now()),
			Field('user', 'reference auth_user'),
			Field('tags','string', length=255),
			migrate=config.settings['migrate'])
		self.db.draft.urlfriendly.compute=lambda row:IS_SLUG()(row.title)[0]
		self.db.draft.urlfriendly.requires = IS_NOT_EMPTY()
		self.db.draft.title.requires = IS_NOT_EMPTY()
		self.db.draft.post.requires = IS_NOT_EMPTY()


class Images(object):
	import os
	from gluon.globals import current

	def __init__(self, db):
		self.request = current.request
		self.db=db
		try:
			self.define_tables()
		except Exception as ex:
			logger.debug("error %s" % ex)
			pass
	def define_tables(self):
		config=Settings()
		self.db.define_table('images',
			Field('alt', 'string', length=255),
			Field('title', 'string', length=255),
			Field('cita_url', 'string',length=255),
			Field('image', 'upload', autodelete=True),
			Field('imagemobile', 'upload', autodelete=True),
			Field('imagemini', 'upload', autodelete=True),
			migrate=config.settings['migrate'])

