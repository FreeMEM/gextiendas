# coding: utf8
@auth.requires_login()
@page_allowed_ip
def createcontracts():
	if auth.has_membership('superadministradores') or auth.has_membership('administradores'):
		from shops import ContractedProduct, Product, Shop
		from invoices import Order, Orderlist
		Product(db), ContractedProduct(db), Order(db), Orderlist(db), Shop(db)
		if not request.vars.invoice=='None' and not request.vars.invoice==None:
			g_order=db(db.orders.invoice==request.vars.invoice).select().first()["id"]
		else:
			g_order=request.vars.order

		if not request.vars.shop:
			shop=db(db.shop.user==request.args(0)).select()
		else:
			shopid=request.vars.shop

		if not shop:
			redirect(URL('contracts','createmanualshop', args=request.args(0), vars=dict(invoice=request.vars.invoice, order=request.vars.order)))
		else:
			shopid=shop[0].id

		contractedproducts=db(	(db.orderlist.g_order==g_order) & 
								(db.orders.user==request.args(0)) &
								(	(db.contractedproducts.shop==shopid) | 
									(db.contractedproducts.shop==None))).select(	
																				db.orders.ALL,
																				db.orderlist.ALL,
																				db.contractedproducts.ALL,
																				db.products.ALL,
																				left=[	db.orderlist.on(db.orders.id==db.orderlist.g_order),
																						db.products.on(db.products.id==db.orderlist.product),
																						db.contractedproducts.on(db.contractedproducts.product==db.products.id)
																					],

																				groupby=db.orderlist.id)

		session.usercontract=request.args(0)
		return dict(contractedproducts=contractedproducts, shop=shop, shopid=shopid)
	else:
		redirect(URL(request.application,'default','user/login'))

@auth.requires_login()
@page_allowed_ip
def createmanualshop():
	if auth.has_membership('superadministradores') or auth.has_membership('administradores'):
		from shops import Shop
		from gluon.contrib.pysimplesoap.client import SoapClient
		import time
		Shop(db)
		if request.args(0):
			firstname=Field('first_name','string', length=128, notnull=True, requires= IS_NOT_EMPTY(error_message='Para configurar en la aplicación del Host el nombre del administrador'))
			lastname=Field('last_name','string', length=128, notnull=True, requires= IS_NOT_EMPTY(error_message='Para configurar en la aplicación del Host el nombre del administrador'))
			applicationtitle=Field('name', 'string', length=80,  notnull=True, unique=True, requires=[IS_NOT_EMPTY(error_message='Nombre de la web o tienda'), IS_NOT_IN_DB(db,'shop.name', error_message="Este nombre ya está siendo usado")])
			hostname=Field('host', 'string', length=45,  notnull=True, unique=True, requires=[IS_MATCH('^\w+$', 'Sólo letras y números, ni espacios ni caracteres especiales'), IS_NOT_EMPTY(error_message='Más adelante podrás poner tu propio dominio, pero ahora es importante este dato'), IS_NOT_IN_DB(db, 'shop.host', error_message="Este nombre ya está siendo usado")])
			form = SQLFORM.factory(firstname, lastname, applicationtitle, hostname, submit_button = 'Crear Tienda')
			if form.validate(keepvalues=True):
				try:
					#almacena los datos
					dbdata="%s" %str(time.time()).replace('.','')
					shopid=db.shop.insert(	user=request.args(0),
											host=form.vars.host,
											db_name="gex%s"%dbdata,
											db_user="gex%s"%dbdata,
											name=form.vars.name,
											email=auth.user.email,
											first_name=form.vars.first_name,
											last_name=form.vars.last_name,
											country='es',
											language='es',
										)
					user=db.auth_user(request.args(0))
					if not user.first_name or not user.last_name:
						user.update_record(first_name=form.vars.first_name, last_name=form.vars.last_name)
					client = SoapClient(wsdl="http://localhost:8000/internalgexcommerce/default/call/soap?WSDL=None")
					if client.addShopSite(request.args(0), shopid)['result']=="0":
						db(db.shop.id==shopid).update(status="enabled")
						db.commit()
					else:
						db.rollback()
						response.flash="Ocurrió un error al generar la tienda."	
					
				except Exception as ex:
					logger.debug(ex)
					db.rollback()
					response.flash="Ocurrió un error al generar la tienda."
				
			elif form.errors:
				response.flash = 'Revise los campos erróneos'

			return dict(form=form)

		else:

			redirect(URL(request.application, 'administrator','users'))
	else:
		redirect(URL(request.application,'default','user/login'))

@auth.requires_login()
@page_allowed_ip
def postcontracts():
	import simplejson
	from dateutil.relativedelta import relativedelta
	if auth.has_membership('superadministradores') or auth.has_membership('administradores'):
		from shops import ContractedProduct, Product, Shop
		from invoices import Order, Orderlist, CreditAccount, AccountingEntry
		Order(db), Orderlist(db), Product(db), ContractedProduct(db), Shop(db)
		accounting=AccountingEntry(db)
		logger.debug(request.post_vars)
		data=simplejson.loads(request.post_vars.datacontracts)
		shopid=request.post_vars.shopid
		try:
			for d in data:
				#NO SE PUEDE HACER EL INSERT DIRECTAMENTE. HAY QUE VER SI EL SHOP YA TIENE CONTRATADO EL PRODUCTO. SI NO TIENE se hace un INSERT, si no, no hace nada.
				#Sólo se va a poder contratar una unidad y la recursividad y duración de la periodicidad  harán el resto.
				orderlist=db(db.orderlist.id==int(d['orderlist'])).select(	db.orderlist.ALL,
																			db.products.ALL,
																			db.orders.ALL,
																			join=[	db.products.on(db.products.id==db.orderlist.product),
																					db.orders.on(db.orders.id==db.orderlist.g_order)]).first()
						

				
				contracted=db(	(db.contractedproducts.shop==shopid) & 
								(db.contractedproducts.user==session.usercontract) & 
								(db.contractedproducts.product==orderlist.orderlist.product)).select().first()

				
				if not contracted:
					db.contractedproducts.insert(	user=session.usercontract,
													product=orderlist.orderlist.product,
													period=orderlist.products.min_period,#optimizar para evitar más consultas
													autorenove=d['autorenove'],
													shop=shopid,
													orderlist=orderlist.orderlist.id,
													paymentmethod=orderlist.orders.payment_method,
													automatics_action=d['automatics_action'],
													notifications=d['notifications'],
													credit_annotation=d['credit_annotation'],
													invoice=request.vars.invoice)
					
				else:
					contracted.update_record(	autorenove=d['autorenove'],
												automatics_action=d['automatics_action'],
												notifications=d['notifications'],
												credit_annotation=d['credit_annotation'],
												)

				logger.debug("LLegoogoo1")
				#anotar crédito si orders pagado y si credit_annotation==True y si not in accountingentries
				if orderlist.orders.status=="Pagado" and d['credit_annotation']:
					if not db((db.accountingentries.orderlist==orderlist.orderlist.id) & 
								(db.accountingentries.active==True)	).select().first():
						logger.debug("LLegoogoo2")
						if not accounting.annotation(db.orderlist(orderlist.orderlist.id), db.orders(orderlist.orders.id), positive=True):
							raise Exception("Ocurrió un error al hacer la anotación en postcontracts")
						logger.debug("LLegoogoo3")
						if contracted:	
							if request.vars.invoice and contracted.invoice:
								if int(request.vars.invoice)>int(contracted.invoice):
									expiration=contracted.expiration
									if contracted.period=='hours': #no usado por ahora
										inc=datetime.timedelta(hours=contracted.quantity)
									elif contracted.period=='days': #no usado por ahora
										inc=datetime.timedelta(days=contracted.quantity)
									elif contracted.period=='week': #no usado por ahora
										inc=datetime.timedelta(weeks=contracted.quantity)
									elif contracted.period=='month': 
										inc=relativedelta(months=contracted.quantity)
										horizon_date=15 #15 días
									elif contracted.period=='year': 
										inc=relativedelta(years=contracted.quantity)
										horizon_date=30*11 #días. No tengo en cuenta febreros ni bisiestos porque es sólo para hacer algo en 11 meses aprox.
									else:
										inc=datetime.timedelta(hours=0)
									if not accounting.annotation(db.orderlist(orderlist.orderlist.id), db.orders(orderlist.orders.id), positive=False):
										raise Exception("Ocurrió un error al hacer la anotación en postcontracts")
									contracted.update_record(expiration=expiration+inc, invoice=request.vars.invoice)
									
			db.commit()
			session.flash="Contratos creados correctamente"
		except Exception as ex:
			logger.debug("Se produjo un error en postcontracts %s" % ex)
			db.rollback()
			raise HTTP(500,ex)

			
		session.usercontract=None
		return "ok"
	else:
		return "no authorized"
