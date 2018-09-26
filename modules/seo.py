# -*- coding: utf-8 -*-
from gluon import *
from gluon.globals import current
from gluon import *
import logging, datetime
from settings import Settings
from blog import Blog

class Seo(object):
	logger = logging.getLogger(" >>>> modules/seo >>>> Gextiendas: ")
	

	def __init__(self,db):
		self.db=db
		self.logger.setLevel(logging.DEBUG)
		self.define_tables()

	def define_tables(self):
		config=Settings()	
		
		self.db.define_table('seo',
			Field('controller','string', length=96, notnull=False, default=None),
			Field('function', 'string', length=96, notnull=False, default=None),
			Field('meta_key','string', length=64, notnull=False, default=None),
			Field('meta_value','string', length=255, notnull=False, default=None),
			migrate=config.settings['migrate'])

	def printMetaProperties(self):
		import string
		
		from gluon import META
		config=Settings()	
		request = current.request
		metas=[]
		db=self.db
		#si es un post de blog, extraer metadatos de la entrada
		if (request.controller=='blog') and (request.function=='show'):
			from blog import Blog, Images
			from plugin_ckeditor import CKEditor
			ckeditor = CKEditor(db)
			Blog(db,ckeditor), Images(db)



			if request.args(0).isdigit():		
				post=db(db.blog.id==request.args(0)).select(db.blog.ALL, db.images.image, join=[db.images.on(db.images.id==db.blog.image)]).first()
			else:
				post=db(db.blog.urlfriendly==request.args(0)).select(db.blog.ALL, db.images.image, join=[db.images.on(db.images.id==db.blog.image)]).first()

			if post!=None:
				self.logger.debug(post.blog.title)
				metas.append(META(_property="og:title", _content=post.blog.title))
				#metas.append(META(_property="og:description", _content=post.description)) #hace falta un field description
				
				metas.append(META(_property="og:image", _content=URL('blog', 'download', args=post.images.image, host=True)))
				metas.append(META(_property="og:type", _content="article"))
				
				if post.blog.tags!=None:
					for tag in post.blog.tags.split(','):
						if tag!="":
							metas.append(META(_property="article:tag", _content=tag.strip()))

				metas.append(META(_property="url", _content=URL('blog','show',request.args(0), host=True)))
				metas.append(META(_property="article:published_time", _content=post.blog.created_on))
				
				metas.append(META(_name="twitter:image:src", _content=URL('blog', 'download', args=post.images.image, host=True)))
				metas.append(META(_name="twitter:card", _content="summary_large_image"))
				metas.append(META(_name="twitter:site", _content="@gextiendas"))
				metas.append(META(_name="twitter:domain", _content="Tu plataforma experta para la gestión de tiendas online"))
				metas.append(META(_name="twitter:creator", _content="@gestionexperta"))
				metas.append(META(_property="article:publisher", _content="http://www.facebook.com/gextiendas"))
		
		#puede ocurrir que un controller/function tengan meta_keys y meta_values definidos en seo table
		elif request.controller!='blog' and request.controller!='administrator' and request.controller!='account':
			metas.append(META(_property="og:title", _content=config.settings['title']))
			metas.append(META(_property="og:description", _content=config.settings['description']))
			metas.append(META(_property="og:type", _content='website'))
			metas.append(META(_property="og:site_name", _content=config.settings['title']))
			metas.append(META(_property="og:image", _content="http://www.gextiendas.es/gextiendas/static/img/slides/up-sales.png"))
			metas.append(META(_name="twitter:image:src", _content="http://www.gextiendas.es/gextiendas/static/img/slides/up-sales.png"))
			metas.append(META(_name="twitter:card", _content="summary_large_image"))
			metas.append(META(_name="twitter:site", _content="@gextiendas"))
			metas.append(META(_name="twitter:domain", _content="Tu plataforma experta para la gestión de tiendas online"))
			metas.append(META(_name="twitter:creator", _content="@gestionexperta"))
			metas.append(META(_property="article:publisher", _content="http://www.facebook.com/gextiendas"))
			for seovalues in db( (db.seo.controller==request.controller) & (db.seo.function==request.function)).select(db.seo.meta_key, db.seo.meta_key):
				metas.append(META(_property=seovalues.meta_key, _content=seovalues.meta_value))

		#y si ninguna de las anteriores, entonces metas por defecto
		else:
			metas.append(META(_property="og:title", _content=config.settings['title']))
			metas.append(META(_property="og:description", _content=config.settings['description']))
			metas.append(META(_property="og:type", _content='website'))
			metas.append(META(_property="og:site_name", _content=config.settings['title']))
			metas.append(META(_property="og:image", _content="http://www.gextiendas.es/gextiendas/static/img/slides/up-sales.png"))
			metas.append(META(_name="twitter:image:src", _content="http://www.gextiendas.es/gextiendas/static/img/slides/up-sales.png"))
		
		return metas





# <!-- Notificación solo para el Administrador: esta página no muestra una meta descripción porque no tiene una. Haz una de estas dos cosas: escribe una específicamente para esta página o ve a el menú SEO -> Titles y configura una plantilla. -->
# <link rel="canonical" href="http://blog.tapiasbravo.com/gestion-experta-crm-en-github/">
# <link rel="publisher" href="https://plus.google.com/+FranciscoTapias">
# <meta property="og:locale" content="es_ES">
# <meta property="og:type" content="article">
# <meta property="og:title" content="Gestión Experta CRM en GitHub">
# <meta property="og:description" content="Ayer por la noche generé mi primer proyecto en gitHub:https://github.com/FreeMEM/gestionexpertacrm">
# <meta property="og:url" content="http://blog.tapiasbravo.com/gestion-experta-crm-en-github/">
# <meta property="og:site_name" content="La bitácora de FreeMEM - tapiasbravo punto com">
# <meta property="article:tag" content="crm">
# <meta property="article:tag" content="gestion experta">
# <meta property="article:tag" content="github">
# <meta property="article:section" content="programación">
# <meta property="article:published_time" content="2012-12-04T13:54:01+00:00">
# <meta property="article:modified_time" content="2014-05-15T17:33:41+00:00">
# <meta property="og:updated_time" content="2014-05-15T17:33:41+00:00">
# <meta property="og:image" content="http://blog.tapiasbravo.com/wp-content/uploads/2012/12/github.jpg">
# <meta property="og:image" content="http://a248.e.akamai.net/assets.github.com/images/modules/dashboard/bootcamp/octocat_setup.png?01fc92e0">
# <meta name="twitter:card" content="summary_large_image">
# <meta name="twitter:site" content="@gestionexperta">
# <meta name="twitter:domain" content="La bitácora de FreeMEM - tapiasbravo punto com">
# <meta name="twitter:creator" content="@gestionexperta">
# <meta name="twitter:image:src" content="http://blog.tapiasbravo.com/wp-content/uploads/2012/12/github.jpg">


# <!-- This site is optimized with the Yoast WordPress SEO plugin v1.5.2.8 - https://yoast.com/wordpress/plugins/seo/ -->
# <link rel="canonical" href="http://www.neoteo.com/">
# <link rel="next" href="http://www.neoteo.com/page/2/">
# <meta property="og:locale" content="es_ES">
# <meta property="og:type" content="website">
# <meta property="og:title" content="Neoteo - Tecnología, todos los días.">
# <meta property="og:url" content="http://www.neoteo.com/">
# <meta property="og:site_name" content="Neoteo">
# <meta property="article:publisher" content="http://www.facebook.com/neoteo">
# <meta property="fb:admins" content="580366759">
# <meta name="msvalidate.01" content="FE44E19D4E977A12C6344E8850CD4C77">
# <meta name="google-site-verification" content="BC3o1-kg3bOGZWOSUdwRsjIRw-2y4zRmrVGlu001_x0">
# <!-- / Yoast WordPress SEO plugin. -->

