# -*- coding: utf-8 -*-
from gluon.storage import Storage
from applications.gextiendas.modules.settings import Settings
config=Settings()
import logging
logger = logging.getLogger(" >>>> GestionExperta: ")
logger.setLevel(logging.DEBUG)

session.secure() #la deshabilito provisionalmente hasta que Auth(db,secure=True)
T.force('es-es')
settings = Storage()




settings.migrate = config.settings['migrate']
settings.data_migrate = config.settings['data_migrate']
settings.title = config.settings['title']
settings.subtitle = config.settings['subtitle']
settings.author = config.settings['author']
settings.author_email = config.settings['author_email']
settings.keywords = config.settings['keywords']
settings.description = config.settings['description']
settings.mysql_uri = config.settings['mysql_uri']

settings.email_server = config.settings['email_server']
settings.email_sender = config.settings['email_sender']
settings.email_login  = config.settings['email_login']
settings.login_method = config.settings['login_method']
settings.login_config = config.settings['login_config']
settings.plugins = config.settings['plugins']
settings.prelaunch=True

if request.is_local:
	from gluon.custom_import import track_changes; track_changes(True)
import datetime

response.generic_patterns = ['*'] if request.is_local else []
## (optional) optimize handling of static files
#response.optimize_css = 'concat,minify,inline'
#response.optimize_js = 'concat,minify,inline'
response.optimize_css = 'concat,minify'
response.optimize_js = 'concat,minify'
#response.static_version = '0.0.1'
#response.static_version

import sys, os
from gluon.fileutils import abspath


#85.56.86.237  ip nueva de jose
#85.52.166.224 camaleon3
import IPy #please include IPy in site packages folder
SERVICE_ALLOWED_IPS = ['127.0.0.1','192.168.1.0/24','85.52.166.224', '85.56.86.237' ]
PAGE_ALLOWED_IPS =  ['127.0.0.1','192.168.1.0/24','85.52.166.224', '85.56.86.237']
service_allowed_ips = [IPy.IP(i) for i in SERVICE_ALLOWED_IPS]
page_allowed_ips = [IPy.IP(i) for i in PAGE_ALLOWED_IPS]

def NOT_ALLOWED(*anything):
	return (False,'Error! Your IP ADDRESS is not allowed!')# you could just return False


def service_allowed_ip(f,ips=service_allowed_ips):
	allowed = False
	client_ip = request.client
	for x in ips:
		if client_ip in x: allowed = True
	if allowed == True:
		return f
	else:
		f_name = f.__name__
		f = NOT_ALLOWED # this could be done with a lambda too
		f.__name__ = f_name
		return f

def page_allowed_ip(f,ips=page_allowed_ips):
	allowed = False
	client_ip = request.client
	for x in ips:
		if client_ip in x: allowed = True
	if allowed == True:
		return f
	else:
		redirect(URL(request.application,'default','user/login'))

periodicity={'hours':'horas','days':'diaria','week':'semanal','month':'mensual','year':'anual', None:'-'}