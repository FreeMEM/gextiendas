# -*- coding: utf-8 -*-
from gluon import *
from gluon import current
import logging
from gluon.template import render #no es lo mismo que response.render
from gluon.fileutils import abspath
from shops import Shop, DomainShop
from applications.gextiendas.modules.settings import Settings
logger = logging.getLogger(" >>>> modules/AuxiliarTools >>>> GestionExperta: ")
logger.setLevel(logging.DEBUG)


class AuxiliarTools(object):

	def __init__(self,db):
		self.db=db

	def render_verifymail(self,email,name):
		path = abspath('applications', current.request.application, 'views')
		url = "%(scheme)s://%(host)s%(urlrequest)s" % {'scheme':current.request.env.wsgi_url_scheme,'host':current.request.env.http_host,'urlrequest':URL(current.request.application, 'default', 'user', args=['verify_email'])+'/%(key)s'}
		return render(filename=path+'/verify_mail.html', context=dict(text=url, email=email, name=name ))


	def render_resetmail(self,email):
		path = abspath('applications', current.request.application, 'views')
		return render(filename=path+'/reset_mail.html' , context=dict(text='https://' + current.request.env.http_host + URL(r=current.request,c='default',f='user',args=['reset_password']) + '/%(key)s', email=email))

	def set_membership(self,auth, group):
		if auth.is_logged_in():
			from regnews import Regnews
			Regnews(self.db)
			if self.db(self.db.regnews.email==auth.user.email).count()==0:
				self.db.regnews.insert(email=auth.user.email, name="%s %s"%(auth.user.first_name, auth.user.last_name), news=True)	
		auth.add_membership(auth.id_group(group), auth.user_id)

	def generatecode(self):
		import random, string, time
		char_set = string.ascii_uppercase + string.digits
		letters=''.join(random.sample(char_set*6, 6))
		n=str(int(time.time()))
		number= n[len(n)-5:len(n)]
		payment_code= "%s%s" %(number,letters) 	#Es el código identificador de los pagos mediante transferencia bancaria provenientes del cliente o 
		return payment_code



class IS_NOT_IN_DB_OR_OWNERSHOP(object):
	def __init__(self, db, shopid, error_message="Este dominio ya está siendo usado en otra tienda"):
		self.error_message=error_message
		self.shopid=shopid
		self.db=db
		Shop(self.db), DomainShop(self.db)

	def __call__(self,value): #value es el valor que entra desde el form con el Field
		db=self.db
		domainshop=db(db.domainshops.domain==value).select(	db.domainshops.ALL, 
															db.shop.ALL,
															join=[db.shop.on(db.shop.id==db.domainshops.shop)]).first()
		shop=db.shop(self.shopid)
		if domainshop:
			if domainshop.shop.user==shop.user:
				return (value,None)
			else:
				return (value, self.error_message)
		else:
			return (value,None)