# -*- coding: utf-8 -*-
from gluon import *
import logging, datetime
from settings import Settings
logger = logging.getLogger(" >>>> modules/shops >>>> Gextiendas: ")
logger.setLevel(logging.DEBUG)

# -*- coding: utf-8 -*-

class Shop(object):

	def __init__(self, db):
		self.db=db
		try:
			self.define_tables()
		except:
			pass
		
	def define_tables(self):
		config=Settings()
		self.db.define_table('shop',
			Field('user', 'reference auth_user'),
			Field('host','string', length=45, notnull=True, unique=True, requires=[IS_MATCH('^\w+$', 'Sólo letras y números'), IS_NOT_EMPTY(error_message='Más adelante podrás poner tu propio dominio, pero ahora es importante este dato')]), #este host es correspondiente a host.gextiendas.es
			#Field('domain','string', length=128, notnull=False, unique=True, requires=[IS_MATCH('^\w+$', 'Sólo letras y números'), IS_NOT_EMPTY(error_message='Olvidaste poner el dominio')]),
			Field('db_name', 'string', length=30,  notnull=True, unique=True), 
			Field('db_user', 'string', length=16, notnull=True, unique=True),
			Field('name', 'string', length=80, notnull=True),
			Field('email', 'string', length=96, requires = IS_EMAIL(error_message='Email inválido')),
			Field('first_name','string', length=128, notnull=True, requires= IS_NOT_EMPTY(error_message='No puede estar vacío')),
			Field('last_name','string', length=128, notnull=True, requires= IS_NOT_EMPTY(error_message='No puede estar vacío')),
			Field('country','string', length=16, notnull=True, default="es"),
			Field('language','string', length=16, notnull=True, default="es"),
			Field('status','string', length=16, default='generating', notnull=False, requires=IS_IN_SET('generating','enabled','disabled')),
			Field('priceplan', 'reference priceplans', default=1, notnull=True, requires=[IS_IN_DB(self.db,self.db.priceplans.id,'%(planname)s', error_message="Debe escoger un plan", zero=None)]),
			Field('ip','string', length=20, notnull=False),
			Field('type','string', length=30, notnull=True, default='Prestashop', requires=IS_IN_SET('Prestashop','Wordpress','Woocommerce', 'Magento', 'Web2Py')),
			migrate=config.settings['migrate'])
			#domain, db_name, db_user, name, email, first_name, last_name, country, language, 

class DomainShop(object):
	def __init__(self, db):
		self.db=db
		PricePlan(db)
		Shop(db)
		try:

			self.define_tables()
		except:
			pass
	def define_tables(self):
		config=Settings()
		self.db.define_table('domainshops',
			Field('shop', 'reference shop'),
			Field('domain', 'string', length=128, notnull=True, requires=[IS_NOT_EMPTY(error_message='olvidaste decirnos el dominio')]),
			Field('host','string', length=128, notnull=False, requires=[IS_MATCH('^\w+$', 'Sólo letras y números')]), #este host corresponde al del dominio que el cliente establece
			Field('email', 'string', length=128, notnull=True, requires=[IS_EMAIL(error_message='Email inválido'), IS_NOT_EMPTY(error_message='Debes facilitarnos un email del mismo dominio')]),			
			#Field('redirect301', 'reference shop', notnull=False),
			Field('active', 'string', default="disabled", notnull=True, requires=IS_IN_SET('enabling','enabled','disabled', 'modifying', 'deleting')),
			#enabling pendiente de aprobación
			#
			migrate=config.settings['migrate'])

	def enable(self):
		return None

	def modify(self):
		return None

	def delete(self):
		return None

class Product(object):
	def __init__(self, db):
		self.db=db
		PricePlan(db)
		try:
			self.define_tables()
		except:
			pass
	def define_tables(self):
		config=Settings()

		self.db.define_table('products',
			Field('name', 'string', length=128, notnull=True, unique=True, requires=[IS_NOT_EMPTY()]),
			Field('price', 'decimal(10,2)',notnull=True, requires=[IS_NOT_EMPTY(error_message='el precio es obligatorio')]), #no incluye tax
			Field('description', 'text', notnull=False),
			Field('active', 'boolean', default=True),
			Field('suscription', 'boolean', default=True),
			Field('min_period', 'string', length='16', notnull=False, default=None, requires=IS_EMPTY_OR(IS_IN_SET(['hours','days','week','month','year'], error_message="Elija un estado"))),
			Field('plan', 'reference priceplans', notnull=False, default=None, requires=IS_EMPTY_OR(IS_IN_DB(self.db, self.db.priceplans.id,'%(planname)s', error_message="Debe escoger un plan"))),
			Field('builtin','boolean', notnull=True, default=False), #esto es para saber que es un servicio funciona en el sistema y que si es True se podrá crear contratos que generarán anotaciones, es decir que modificarán el saldo.
			migrate=config.settings['migrate'])


class ContractedProduct(object):
	
	def __init__(self, db):
		from invoices import Order, Invoice
		self.db=db
		Product(db), Order(db), Invoice(db), Shop(db)
		try:
			self.define_tables()
		except:
			pass
	#Si un contrato expira y no se renueva se cambia active=False
	#Pasados unos días sin renovar, se borra.
	def define_tables(self):
		config=Settings()
		self.db.define_table('contractedproducts',
			Field('user', 'reference auth_user'),
			Field('product', 'reference products', requires=[IS_IN_DB(self.db,self.db.products.id,'%(name)s', error_message="Debe escoger un producto", zero=None)]),
			Field('quantity', 'integer', notnull=False, default=1), 
			Field('period', 'string', length='16', default='month', requires=[IS_IN_SET('hours','days','week','month','year',None)]),
			Field('autorenove', 'boolean', default=True), #si false preguntar si renovar
			Field('start', 'datetime', default=datetime.datetime.now()), ##fecha de inicio/contratación del servicio por primera vez
			Field('renove', 'datetime'), #fecha última renovación
			Field('expiration', 'datetime'), #fecha de expiración
			Field('shop', 'reference shop'),
			Field('orderlist', 'reference orderlist'),
			Field('paymentmethod', 'string', length=32, default='paypal', requires=[IS_IN_SET('paypal','transferencia','domiciliación')]),
			Field('automatics_action', 'boolean', default=True), #si es True puede activar/desactivar servicios automáticamente. Se puede poner a False si se maneja el contrato desde administrator
			Field('notifications', 'boolean', default=True), #si es True notifica por email los eventos
			Field('active', 'boolean', default=True, notnull=True),
			Field('managed', 'boolean', default=False, notnull=True), #cuando ya se han realizado acciones (actualizado saldo, cambios en apache, etc) se cambia a true.
			Field('credit_annotation','boolean', default=True, notnull=True), #pensado para contratos manuales. En un contrato manual
			Field('invoice','reference invoices'), #lo he añadido a última hora para saber si el contrato ya tiene asignado factura y así saber si incrementar fecha de expiración al trabajar con contratos manuales en contracts.postcontract
			migrate=config.settings['migrate'])

	def managecontract(self, contract):
		# Atención, esta función es altamente complicada porque se concentran casi todos los objetos, situaciones y operaciones del sistema.
		# Dolor de cabeza que te cagas llena de condiciones. De todo menos KISS. ALGUNA VEZ SIMPLIFICARE SEMEJANTE MIERDA!
		from shops import PricePlan, Shop
		from invoices import CreditAccount, AccountingEntry
		from adminsettings import Adminsettings
		from dateutil.relativedelta import relativedelta
		from gluon.contrib.pysimplesoap.client import SoapClient
		db=self.db
		CreditAccount(db), Shop(db), Adminsettings(db)
		accounting=AccountingEntry(db)
		adm=db.adminsettings(1)
		logger.debug(contract)
		#comprueba si active
		if contract.contractedproducts.active:
			total=((contract.products.price * adm.tax)/100) + contract.products.price
			credit=0
			c=db(db.creditaccounts.user==contract.contractedproducts.user).select().first()
			if c!=None:
				credit=c.balance	
			try:
				now=datetime.datetime.now()
				if contract.contractedproducts.period=='hours': #no usado por ahora
					inc=datetime.timedelta(hours=contract.contractedproducts.quantity)
				elif contract.contractedproducts.period=='days': #no usado por ahora
					inc=datetime.timedelta(days=contract.contractedproducts.quantity)
				elif contract.contractedproducts.period=='week': #no usado por ahora
					inc=datetime.timedelta(weeks=contract.contractedproducts.quantity)
				elif contract.contractedproducts.period=='month': 
					inc=relativedelta(months=contract.contractedproducts.quantity)
					horizon_date=15 #15 días
				elif contract.contractedproducts.period=='year': 
					inc=relativedelta(years=contract.contractedproducts.quantity)
					horizon_date=30*11 #días. No tengo en cuenta febreros ni bisiestos porque es sólo para hacer algo en 11 meses aprox.
				else:
					inc=datetime.timedelta(hours=0)
				
				#si autorenove, 
				if contract.contractedproducts.autorenove:
					#si expiration is None:
					if contract.contractedproducts.expiration==None:
						# cambiar status y plan del shop si contract.order.status=="Pagado"
						if contract.orders.status=='Pagado':
							#comprueba si saldo 
							if credit>=total:
								#activar servicios
								if contract.contractedproducts.automatics_action:
									client = SoapClient(wsdl="http://localhost:8000/internalgexcommerce/default/call/soap?WSDL=None")
									if client.enableDomainShop(contract.contractedproducts.user, contract.contractedproducts.shop)['result']=="0":									
										db(db.shop.id==contract.contractedproducts.shop).update(priceplan=contract.priceplans.id)
										# cambiar de contractedproducts fecha de start y expiration
										db(db.contractedproducts.id==contract.contractedproducts.id).update(start=now, expiration= now+inc, managed=True)
										#quitar saldo
										if contract.contractedproducts.credit_annotation:
											accounting.annotation(contract.contractedproducts.orderlist, db.orders(contract.orders.id), positive=False)
										db.commit() 
									else:
										raise Exception("Imposible habilitar dominio userid: %s shopid: %s status:%s priceplan:%s" % (contract.contractedproducts.user, contract.contractedproducts.shop, 'enabled', contract.priceplans.id))
								else:
										db(db.shop.id==contract.contractedproducts.shop).update(priceplan=contract.priceplans.id)
										# cambiar de contractedproducts fecha de start y expiration
										db(db.contractedproducts.id==contract.contractedproducts.id).update(start=now, expiration= now+inc, managed=True)
										#quitar saldo
										if contract.contractedproducts.credit_annotation:
											accounting.annotation(contract.contractedproducts.orderlist, db.orders(contract.orders.id), positive=False)
										db.commit() 
					else:
						#comprobar método de pago. 
						#Si método de pago es una transferencia, 
						if contract.contractedproducts.paymentmethod=='Transferencia':
							# no ha expirado, managed==True y pedido tiene más de horizon días
							logger.debug("llego1")
							if contract.orders.manual_operation ==True:
								logger.debug("llego2")
								order_date=contract.orders.confirmed_at
							else:
								logger.debug("llego3")
								order_date=contract.orders.ordered_at
							


							if 	(contract.contractedproducts.managed==True) and (contract.contractedproducts.expiration>=datetime.datetime.now()) and ((datetime.datetime.now() - order_date).days>=horizon_date):
								# si es un pedido "pagado" en fechas anteriores:
								logger.debug("llego4.1")
								if contract.orders.status=='Pagado':
									logger.debug("llego5")
									# - generar pedido nuevo pendiente de pago a partir del producto y heredando datos del pedido
									orderid=db.orders.insert(	user=contract.contractedproducts.user,
																total=contract.products.price,
																totaltax=(contract.products.price * adm.tax)/100,
																ordered_at=datetime.datetime.now(),
																status='Pendiente pago',
																payment_method=contract.orders.payment_method,
																payment_code=contract.orders.payment_code,
																manual_operation=contract.orders.manual_operation,
																tax=adm.tax
															)
									logger.debug("llego6")
									orderlistid=db.orderlist.insert(
															product=contract.contractedproducts.product,
															g_order=orderid,
															quantity=contract.contractedproducts.quantity,
															price=contract.products.price,
															price_wdto=contract.products.price,
															tax=adm.tax,
														)
									logger.debug("llego7")
									# - encolar correo aviso expiration date, para que paguen teniendo en cuenta que las transferencias pueden demorarse entre 4-5 días
									#si es un plan
									if contract.contractedproducts.notifications: #and not contract.orders.manual_operation: #MEJOR DESACTIVO "and not contract.orders.manual_operation" PARA TENER EN CUENTA QUE SEA DOMICILIACION EN CUYO CASO EL MENSAJE DEL MAIL CAMBIARÁ
										if contract.products.plan!=None:
											logger.debug("LLEGO8")
											urlpayment = '%(scheme)s://%(host)s%(url)s' % {'scheme':'https','host':'www.gextiendas.es', 'url':URL('payment','code',args=[contract.orders.payment_code.code])}
											html = """
													<p>Fuengirola (Málaga), a %(now)s</p>
													<p>Estimado %(name)s, el próximo %(date)s caduca el servicio contratado: </p>
													<p>%(product)s para su tienda %(shop_name)s (%(shop_hostname)s)</p>
													<p>La modalidad de pago mediante transferencia bancaria suele demorarse de 1 a 5 días aproximadamente. Rogamos tenga en cuenta esta circunstancia y programe con tiempo la transferencia desde su banco, ya que todos nuestros sistemas están automatizados y si ocurriese que no llegase el pago a tiempo, se desactivará el servicio.</p>
													<p>Si lo desea puede realizar el pago mediante paypal o cambiar la forma de pago siguiendo este enlace:</p>
													<p><a href="%(url)s">%(url)s</a></p>
													<p>El equipo de GEXtiendas.</p>
												""" % 	{	"now": datetime.datetime.now().strftime("%d-%m-%Y %H:%M"),
															"name": contract.contractedproducts.user.first_name, 
															"date": contract.contractedproducts.expiration, 
															"product": contract.products.name,
															"shop_hostname":contract.contractedproducts.shop.host, 
															"shop_name":contract.contractedproducts.shop.name,
															"url": urlpayment,
														}
											subject="[GEXtiendas] seguimiento de servicios"
											logger.debug("LLEGO9")
											plaintext="""
													www.gestionexperta.com/www.gextiendas.es\n
													\n
													\n
													\t\t\t\t  Fuengirola (Málaga), a %(now)s \n
													Estimado %(name)s, el próximo %(date)s caduca el servicio contratado:\n\n
													%(product)s para su tienda %(shop_name)s (%(shop_hostname)s)\n\n
													La modalidad de pago mediante transferencia bancaria suele demorarse de 1 a 5 días aproximadamente. Rogamos tenga en cuenta esta circunstancia y programe con tiempo la transferencia desde su banco, ya que todos nuestros sistemas están automatizados y si ocurriese que no llegase el pago a tiempo, se desactivará el servicio.\n
													Si lo desea puede realizar el pago mediante paypal o cambiar la forma de pago siguiendo este enlace:\n\n
													%(url)s \n\n\n
													El equipo de gextiendas
													""" % 	{	"now": datetime.datetime.now().strftime("%d-%m-%Y %H:%M"),
															"name": contract.contractedproducts.user.first_name, 
															"date": contract.contractedproducts.expiration, 
															"product": contract.products.name,
															"shop_hostname":contract.contractedproducts.shop.host, 
															"shop_name":contract.contractedproducts.shop.name,
															"url": urlpayment,
														}
										#si no es un plan (por ejemplo LOPD)
										#else:
										#cambiar el mensaje html. PENDIENTE. Es posible que si no es un plan no sea autorenove. Estudiar
										logger.debug("LLEGO10")
										self.__expirationwarningmail(contract.contractedproducts.user, html, subject, plaintext)
										logger.debug("LLEGO11")
										# - actualizar orderlist de contract
										# - actualizar managed a False
									db(db.contractedproducts.id==contract.contractedproducts.id).update(orderlist=orderlistid, managed=False)
									logger.debug("LLEGO12")
									logger.debug("Transferencia Pagada  no ha expirado, managed==True y pedido tiene más de horizon días")

									db.commit()
									logger.debug("LLEGO13")
								# si es pendiente de pago
								elif contract.orders.status=='Pendiente pago' and contract.contractedproducts.notifications==True:# and not contract.orders.manual_operation: #DESACTIVO MANUAL_OPERATION PORQUE EN MANODO MANUAL CONTROLO SI SE LE ENVIA O NO MAIL
									logger.debug("LLEGO14")
									# encolar mail recordatorio de que ha hecho un pedido y está pendiente de pago
									if contract.contractedproducts.notifications:
										logger.debug("LLEGO15")
										urlpayment = '%(scheme)s://%(host)s%(url)s' % {'scheme':'https','host':'www.gextiendas.es', 'url':URL('payment','code',args=[contract.orders.payment_code.code])}
										html = """
												<p>Fuengirola (Málaga), a %(ordered_at)s</p>
												<p>Estimado %(name)s, el pasado %(date)s realizó un pedido de este producto: </p>
												<p>%(product)s para su tienda %(shop_name)s (%(shop_hostname)s)</p>
												<p>pero no tenemos constancia de su transferencia bancaria. Si cree que es un error, puede enviarnos por correo electrónico el justificante del banco por fax al 912692914 o por correo electrónico a <a href="mailto:administracion@gextiendas.es">administracion@gextiendas.es</a> indicándonos su cuenta de usuario (email con el que accede al sistema).</p>
												<p>Si lo desea puede realizar el pago mediante paypal o cambiar la forma de pago siguiendo este enlace:</p>
												<p><a href="%(url)s">%(url)s</a></p>
												<p>El equipo de GEXtiendas.</p>
											""" % 	{	"ordered_at": contract.orders.ordered_at.strftime("%d-%m-%Y %H:%M"),
														"name": contract.contractedproducts.user.first_name, 
														"date": contract.contractedproducts.expiration, 
														"product": contract.products.name,
														"shop_hostname":contract.contractedproducts.shop.host, 
														"shop_name":contract.contractedproducts.shop.name,
														"url": urlpayment,
													}
										logger.debug("LLEGO16")
										subject="[GEXtiendas] seguimiento de servicios"
										plaintext="""
												www.gestionexperta.com/www.gextiendas.es\n
												\n
												\n
												\t\t\t\t  Fuengirola (Málaga), a %(ordered_at)s \n
												Estimado %(name)s, el próximo %(date)s caduca el servicio contratado:\n\n
												%(product)s para su tienda %(shop_name)s (%(shop_hostname)s)\n\n
												pero no tenemos constancia de su transferencia bancaria. Si cree que es un error, puede enviarnos por correo electrónico el justificante del banco por fax al 912692914 o por correo electrónico a <a href="mailto:administracion@gextiendas.es">administracion@gextiendas.es</a> indicándonos su cuenta de usuario (email con el que accede al sistema).\n
												Si lo desea puede realizar el pago mediante paypal o cambiar la forma de pago siguiendo este enlace:\n\n
												%(url)s \n\n\n
												El equipo de gextiendas
												""" % 	{	
															"ordered_at": contract.orders.ordered_at.strftime("%d-%m-%Y %H:%M"),
															"name": contract.contractedproducts.user.first_name, 
															"date": contract.contractedproducts.expiration, 
															"product": contract.products.name,
															"shop_hostname":contract.contractedproducts.shop.host, 
															"shop_name":contract.contractedproducts.shop.name,
															"url": urlpayment,
														}
										logger.debug("LLEGO17")
										self.__expirationwarningmail(contract.contractedproducts.user, html, subject, plaintext)
										logger.debug("LLEGO18")
									logger.debug("LLEGO19")
									logger.debug("Transferencia Pendiente pago,  no ha expirado, managed==True y pedido tiene más de horizon días")

							# managed==False y status=="Pagado"
							elif (contract.contractedproducts.managed==False) and (contract.orders.status=="Pagado"):
								logger.debug("LLEGO20")
								#comprobar que realmente hay saldo, 
								if credit>=total:
									logger.debug("LLEGO21")
									# actualizar fechas de renove y expiration
									# actualizar managed=True
									db(db.contractedproducts.id==contract.contractedproducts.id).update(renove=now, expiration= contract.contractedproducts.expiration + inc, managed=True)
									#quitar saldo
									logger.debug("LLEGO22")
									if contract.contractedproducts.credit_annotation:
										accounting.annotation(contract.contractedproducts.orderlist, db.orders(contract.orders.id), positive=False)
										logger.debug("LLEGO23")
									logger.debug("Transferencia Pagada  no ha expirado, managed==False y pedido tiene más de horizon días")
									logger.debug("LLEGO24")
									
									db.commit()
							#si expirado margen de 2 día, desactivar servicios
							elif contract.contractedproducts.expiration < (datetime.datetime.now() + datetime.timedelta(days=2)):
								logger.debug("LLEGO25")
								if contract.contractedproducts.automatics_action:
									logger.debug("LLEGO26")
									client = SoapClient(wsdl="http://localhost:8000/internalgexcommerce/default/call/soap?WSDL=None")
									logger.debug("LLEGO27")
									if client.disableDomainShop(contract.contractedproducts.user, contract.contractedproducts.shop)['result']=="0":
										logger.debug("LLEGO28")
										db(db.shop.id==contract.contractedproducts.shop).update(status='enabled', priceplan=db(db.priceplans.paymode=="free").select().first()["id"])
										logger.debug("LLEGO29")
									else:
										raise Exception("Imposible deshabilitar dominio userid: %s shopid: %s priceplan:%s" % (contract.contractedproducts.user, contract.contractedproducts.shop, db(db.priceplans.paymode=="free").select().first()["id"]))

								else:
									db(db.shop.id==contract.contractedproducts.shop).update(status='enabled', priceplan=db(db.priceplans.paymode=="free").select().first()["id"])
									logger.debug("LLEGO30")
								db.commit()
							#si expirado margen de 7 día, desactivar servicios	y borrar contrato
							elif contract.contractedproducts.expiration< (datetime.datetime.now() + datetime.timedelta(days=7)):
								if contract.contractedproducts.automatics_action:
									client = SoapClient(wsdl="http://localhost:8000/internalgexcommerce/default/call/soap?WSDL=None")
									if client.disableDomainShop(contract.contractedproducts.user, contract.contractedproducts.shop)['result']=="0":
										db(db.shop.id==contract.contractedproducts.shop).update(status='enabled', priceplan=db(db.priceplans.paymode=="free").select().first()["id"])
										logger.debug("LLEGO31")
									else:
										raise Exception("Imposible deshabilitar dominio userid: %s shopid: %s priceplan:%s" % (contract.contractedproducts.user, contract.contractedproducts.shop, db(db.priceplans.paymode=="free").select().first()["id"]))
								else:
									db(db.shop.id==contract.contractedproducts.shop).update(status='enabled', priceplan=db(db.priceplans.paymode=="free").select().first()["id"])
									logger.debug("LLEGO32")

								db.commit(db)
							logger.debug("LLEGO34")
						# Si es paypal no hacer nada, que lo haga IPN
							#db(db.contractedproducts.id==contract.contractedproducts.id).update(renove=now, expiration= contract.contractedproducts.expiration+inc)
							#update fecha de renove a now y suma tiempo a expiration

				#si no autorenove, dos casos, que sean ifselling o comprobar que el producto no sea de suscripción, si no, pasados 7 días borrar contrato, cambiar a plan gratuito y desactivar servicios si no lo estuviesen ya.
				else:
					
					if contract.products.plan=='ifselling' or contract.products.suscription==False:
						logger.debug("LLEGO33")
						if contract.contractedproducts.start==None:
							logger.debug("LLEGO34")
							# cambiar status y plan del shop si contract.order.status=="Pagado"
							if contract.orders.status=='Pagado':
								logger.debug("LLEGO35")
								#comprueba si saldo 
								if credit>=total:
									#activar servicios 
									logger.debug("LLEGO36")
									if contract.contractedproducts.automatics_action:
										logger.debug("LLEGO37")
										client = SoapClient(wsdl="http://localhost:8000/internalgexcommerce/default/call/soap?WSDL=None")
										logger.debug("LLEGO38")
										if client.enableDomainShop(contract.contractedproducts.user, contract.contractedproducts.shop)['result']=="0":
											logger.debug("LLEGO39")
											db(db.shop.id==contract.contractedproducts.shop).update(status='enabled', priceplan=contract.priceplans.id)
											logger.debug("LLEGO40")
											# cambiar de contractedproducts fecha de start y expiration
											db(db.contractedproducts.id==contract.contractedproducts.id).update(start=now, expiration= now+inc)
											logger.debug("LLEGO41")
											#quitar saldo
											if contract.contractedproducts.credit_annotation:
												logger.debug("LLEGO42")
												accounting.annotation(contract.contractedproducts.orderlist, db.orders(contract.orders.id), positive=False)
												logger.debug("LLEGO43")
											db.commit()
											logger.debug("LLEGO44")
										else:
											raise Exception("Imposible habilitar dominio userid: %s shopid: %s status:%s priceplan:%s" % (contract.contractedproducts.user, contract.contractedproducts.shop, 'enabled', contract.priceplans.id))
									else:
										logger.debug("LLEGO45")
										db(db.shop.id==contract.contractedproducts.shop).update(status='enabled', priceplan=contract.priceplans.id)
										logger.debug("LLEGO46")
										# cambiar de contractedproducts fecha de start y expiration
										db(db.contractedproducts.id==contract.contractedproducts.id).update(start=now, expiration= now+inc)
										logger.debug("LLEGO47")
										#quitar saldo
										if contract.contractedproducts.credit_annotation:
											logger.debug("LLEGO48")
											accounting.annotation(contract.contractedproducts.orderlist, db.orders(contract.orders.id), positive=False)
											logger.debug("LLEGO49")
										db.commit()
										logger.debug("LLEGO50")
					
					#pasados 7 días borrar contrato, cambiar a plan gratuito y desactivar servicios si no lo estuviesen ya.				
					
					elif contract.contractedproducts.expiration< (datetime.datetime.now() + datetime.timedelta(days=7)):	
						logger.debug("LLEGO51")
						client = SoapClient(wsdl="http://localhost:8000/internalgexcommerce/default/call/soap?WSDL=None")
						logger.debug("LLEGO52")
						if client.disableDomainShop(contract.contractedproducts.user, contract.contractedproducts.shop)['result']=="0":
							logger.debug("LLEGO53")
							db(db.shop.id==contract.contractedproducts.shop).update(status='enabled', priceplan=db(db.priceplans.paymode=="free").select().first()["id"])
							logger.debug("LLEGO54")
							db.commit()
						else:
							raise Exception("Imposible habilitar dominio userid: %s shopid: %s status:%s priceplan:%s" % (contract.contractedproducts.user, contract.contractedproducts.shop, 'enabled', db(db.priceplans.paymode=="free").select().first()["id"]))




			except Exception as ex:
						db.rollback()
						logger.debug("Error manage_plans_and_status %s" % ex)


	def __expirationwarningmail(self, user, html,subject, plaintext):

		from queuemail import Queuemail
		#encolar correo aviso expiration date, para que recordar pago, teniendo en cuenta que las transferencias pueden demorarse entre 4-5 días
		db=self.db
		queue=Queuemail(db)
		queuedata=[]
		queuedata.append({	'to': '%s'%db.auth_user(user).email,
							'subject':subject,
							'message':plaintext,
							'html':XML(html),
							'template':'communications/mail_template.html',
							'title':'Aviso: %s' % subject,
							'unsubscribe':''
						})
		queue.queuemessage(queuedata)






class ProfilePlan(object):
	def __init__(self, db):
		self.db=db
		PricePlan(db)
		Product(db)
		try:
			self.define_tables()
		except:
			pass
	def define_tables(self):
		config=Settings()
		self.db.define_table('profileplans',
			Field('priceplan', 'reference priceplans', requires=[IS_IN_DB(self.db,self.db.priceplans.id,'%(planname)s', error_message="Debe escoger un plan", zero=None)]),
			Field('product', 'reference products', requires=[IS_IN_DB(self.db,self.db.products.id,'%(name)s', error_message="Debe escoger un producto", zero=None)]),
			Field('active', 'boolean', default=True),
			migrate=config.settings['migrate'])


class PricePlan(object):
	def __init__(self, db):
		self.db=db
		try:
			self.define_tables()
		except:
			pass
	def define_tables(self):
		config=Settings()
		self.db.define_table('priceplans',
			Field('planname', 'string', length=128, notnull=True, unique=True, requires=IS_NOT_EMPTY()),
			Field('paymode', 'string', default='flatrate', length=16, requires=IS_IN_SET(['free','ifselling','flatrate'])),
			Field('explanation', 'text', notnull=False),
			migrate=config.settings['migrate'])


class CustomerAgreement(object):
	def __init__(self, db):
		self.db=db
		Agreement(db)
		try:
			self.define_tables()
		except:
			pass
	def define_tables(self):
		config=Settings()
		self.db.define_table('customeragreements',
			Field('user', 'reference auth_user'),
			Field('agreement', 'reference agreements', requires=IS_IN_DB(self.db,self.db.agreements.id,'%(agreemem)s', error_message="Debe escoger un tipo de contrato", zero=None)),
			migrate=config.settings['migrate'])


class Agreement(object):
	def __init__(self, db):
		self.db=db
		try:
			self.define_tables()
		except:
			pass
	def define_tables(self):
		config=Settings()
		self.db.define_table('agreements',
			Field('agreement', 'string', length=128), 
			Field('filename', 'string', length=128, notnull=True, unique=True, requires=[IS_NOT_EMPTY()]),
			migrate=config.settings['migrate'])


# class MethodPayments(object):
# 	def __init__(self, db):
# 		self.db=db 
# 		try:
# 			self.define_tables()
# 		except:
# 			pass
# 	def
 

