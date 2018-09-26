# -*- coding: utf-8 -*- 
from gluon import *

class Settings(object):

	def __init__(self):

		self.settings=	{ 
							'migrate':True,
							'data_migrate':True,
							'production':False,
							'title':'Tiendas virtuales gratuitas en Prestashop | Tu plataforma experta para la gestión de tiendas online',
							'subtitle':'Conectamos personas, descubrimos clientes juntos.',
							'author':'Gestión Experta de Sistemas Computacionales S.L.',
							'author_email':'francisco.antonio@tapiasbravo.com',
							'keywords': 'tiendas online, gratis, prestashop, seo, community manager, socialmedia, ingenieria software, software a medida',
							'description':'GEXtiendas es una plataforma para ayudarte a crear y gestionar multitud de tiendas online con pocos clicks',
							#'mongodb_uri':'mongodb://user:pass@localhost/despachocifrado',
							'mysql_uri':'mysql://user:pass@localhost/gextiendas',
							'security_key':'x9b17e50-x2e8-xba0-x5c3-xf05fca09adc',
							'email_server':'mail.server',
							'email_sender':'comunicacion@mail.server',
							'email_login':'comunicacion@mail.server:pass',
							'login_method':'local',
							'login_config':'',
							'plugins':[]
						}
