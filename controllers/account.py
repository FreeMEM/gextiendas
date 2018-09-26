# -*- coding: utf-8 -*-
@auth.requires_login()
def index():
	from shops import Shop
	from gluon.contrib.pysimplesoap.client import SoapClient
	import time
	Shop(db)
	shops=db((db.shop.id>0) & (db.shop.user==auth.user_id)).select()
	form=None

	if not shops:	
		from queuemail import Queuemail
		Queuemail(db)
		firstname=Field('first_name','string', length=128, notnull=True, requires= IS_NOT_EMPTY(error_message='Para dirigirnos a usted y para los clientes en su tienda'))
		lastname=Field('last_name','string', length=128, notnull=True, requires= IS_NOT_EMPTY(error_message='Para dirigirnos a usted y para los clientes en su tienda'))
		shopname=Field('name', 'string', length=80,  notnull=True, unique=True, requires=[IS_NOT_EMPTY(error_message='No olvide decirnos el nombre de su tienda'), IS_NOT_IN_DB(db,'shop.name', error_message="Este nombre ya está siendo usado")])
		hostname=Field('host', 'string', length=45,  notnull=True, unique=True, requires=[IS_MATCH('^\w+$', 'Sólo letras y números, ni espacios ni caracteres especiales'), IS_NOT_EMPTY(error_message='Más adelante podrás poner tu propio dominio, pero ahora es importante este dato'), IS_NOT_IN_DB(db, 'shop.host', error_message="Este nombre ya está siendo usado")])
		form = SQLFORM.factory(firstname, lastname, shopname, hostname, submit_button = 'Crear Tienda')
		if form.validate():
			try:
				#almacena los datos
				dbdata="%s" %str(time.time()).replace('.','')
				shopid=db.shop.insert(	user=auth.user_id,
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
				db(db.auth_user.id==auth.user).update(first_name=form.vars.first_name, last_name=form.vars.last_name)
		
				client = SoapClient(wsdl="http://localhost:8000/internalgexcommerce/default/call/soap?WSDL=None")
				if client.addShopSite(auth.user_id, shopid)['result']=="0":
					db(db.shop.id==shopid).update(status="enabled")
					db.commit()

				else:
					db.rollback()
					session.flash="Ocurrió un error al generar la tienda."	
					redirect(URL('index'))

			except Exception as ex:
				logger.debug(ex)
				db.rollback()
				session.flash="Ocurrió un error al generar la tienda."
				redirect(URL('index'))



			session.flash="En unos minutos recibirá un correo con los datos de su nueva tienda"
			redirect(URL('index'))
		elif form.errors:
			response.flash = 'Revise los campos erróneos'


	return dict(shops=shops, form=form)


@auth.requires_login()
def newshop():
	# if settings.prelaunch==True and not (auth.has_membership('administradores') or auth.has_membership('superadministradores')):
	# 	redirect(URL(request.application, 'communications','prelaunch'))

	from shops import Shop, DomainShop
	from gluon.contrib.pysimplesoap.client import SoapClient
	import time
	Shop(db), DomainShop(db)
	lenshops=db( (db.shop.id > 0) & (db.shop.user==auth.user_id) ).count()
	count=db.domainshops.id.count()
	countsdomainshops=int(db((db.shop.id>0) & (db.shop.user==auth.user_id) & (db.domainshops.shop==db.shop.id)).select(count, left=[db.domainshops.on(db.domainshops.shop==db.shop.id)]).first()['COUNT(domainshops.id)'])
	shopid=None
	if lenshops <= 10+countsdomainshops:
		form=None
		from queuemail import Queuemail
		Queuemail(db)
		firstname=Field('first_name','string', length=128, notnull=True, requires= IS_NOT_EMPTY(error_message='Para dirigirnos a usted y para los clientes en su tienda'))
		lastname=Field('last_name','string', length=128, notnull=True, requires= IS_NOT_EMPTY(error_message='Para dirigirnos a usted y para los clientes en su tienda'))
		shopname=Field('name', 'string', length=80,  notnull=True, unique=True, requires=[IS_NOT_EMPTY(error_message='No olvide decirnos el nombre de su tienda'), IS_NOT_IN_DB(db,'shop.name', error_message="Este nombre ya está siendo usado")])
		hostname=Field('host', 'string', length=45,  notnull=True, unique=True, requires=[IS_MATCH('^\w+$', 'Sólo letras y números, ni espacios ni caracteres especiales'), IS_NOT_EMPTY(error_message='Más adelante podrás poner tu propio dominio, pero ahora es importante este dato'), IS_NOT_IN_DB(db, 'shop.host', error_message="Este nombre ya está siendo usado")])
		form = SQLFORM.factory(firstname, lastname, shopname, hostname, submit_button = T('Create new store'))
		if form.validate():
			try:
				#almacena los datos
				dbdata="%s" %str(time.time()).replace('.','')
				shopid= db.shop.insert(	user=auth.user_id,
								host=form.vars.host,
								db_name="gex%s"%dbdata,
								db_user="gex%s"%dbdata,
								name=form.vars.name,
								email=auth.user.email,
								first_name=form.vars.first_name,
								last_name=form.vars.last_name,
								country='es',
								language='es',
								ip=__get_ip_address('wlan0'),
								)
				
				client = SoapClient(wsdl="http://localhost:8000/internalgexcommerce/default/call/soap?WSDL=None")
				if client.addShopSite(auth.user_id, shopid)['result']=="0":
					db(db.shop.id==shopid).update(status="enabled")
					db.commit()
				else:
					db.rollback()
					response.flash="Ocurrió un error al generar la tienda."	
				
				session.shopname=form.vars.host
			except Exception as ex:
				logger.debug(ex)
				db.rollback()
				response.flash="Ocurrió un error al generar la tienda."
			
			

			session.flash="En unos minutos recibirá un correo con los datos de su nueva instancia de tienda"
			redirect(URL('account', 'index'))
			# if request.vars.priceplan:
			# 	plan=db.priceplans(request.vars.priceplan)
			# 	if plan.paymode=='free':
			# 		redirect(URL('index'))
			# 	else:	
			# 		redirect(URL('setdomain', vars=dict(plan=request.vars.priceplan, shop=shopid)))
			# else:
			# 	redirect(URL('plans'))
		elif form.errors:
			response.flash = 'Revise los campos erróneos'
	else:
		session.flash = "Ńo puede crear más tiendas. Contrate alguno de los planes de pago"

	return dict(form=form, domainshops=countsdomainshops)


@auth.requires_login() #esto ssirve para habilitar un domain en una shop
def enabledomain():
	from shops import Shop, DomainShop, PricePlan, ContractedProduct, Product
	Shop(db), DomainShop(db), PricePlan(db), ContractedProduct(db), Product(db)
	
	shop = db((db.shop.host==request.vars.host) & (db.shop.user==auth.user_id)).select().first()
	
	if shop:
		if shop.priceplan.paymode=='free':
			#hay que pasar por caja, pero antes comprobar si hay algún pedido en planes distintos a free para esta tienda pendiente de ser aprobado
			pending=db(	(db.contractedproducts.shop==shop.id) & 
						(db.contractedproducts.user==auth.user_id) &
						(db.contractedproducts.start==None) & 
						(	(db.priceplans.paymode!=None) & 
							(db.priceplans.paymode!='free') )).select(	db.contractedproducts.id, 
																		join=[	db.products.on(db.products.id==db.contractedproducts.product),
																				db.priceplans.on(db.priceplans.id==db.products.plan)]
																	).first()
			logger.debug(db(	(db.contractedproducts.shop==shop.id) & 
								(db.contractedproducts.user==auth.user_id) &
								(db.contractedproducts.start==None) & 
								(	(db.priceplans.paymode!=None) & 
									(db.priceplans.paymode!='free') ))._select(	db.contractedproducts.id, 
																				join=[	db.products.on(db.products.id==db.contractedproducts.product),
																						db.priceplans.on(db.priceplans.id==db.products.plan)]
																			))


			if pending==None:
				if request.vars.host:
					redirect(URL(request.application, 'plans','index', vars=dict(host=request.vars.host)))
			else:
				session.flash="Este pedido para cambiar de plan, estaba pendiente de confirmación pago"
				redirect(URL('payment','index'))
				

		else: 
			#este dominio está en shop con un priceplan de pago, así que se puede llamar al api de internalgexcommerce para configurar el apache
			logger.debug("de pagoooo")
	else:
		session.flash="No podemos encontrar la tienda %s" % request.vars.host
		redirect(URL('index'))

@auth.requires_login()
def setdomain():
	from shops import Shop, DomainShop, PricePlan
	from auxiliartools import IS_NOT_IN_DB_OR_OWNERSHOP
	Shop(db), DomainShop(db), PricePlan(db)

	shophost=request.vars.shop
	shop=db((db.shop.host==request.vars.shop) & (db.shop.user==auth.user_id)).select(db.shop.ALL, db.priceplans.ALL, join=[db.priceplans.on(db.priceplans.id==db.shop.priceplan)]).first()

	redirection=False
	ip=shop.shop.ip
	if shop:
		domain=Field('domain', 'string', length=45,  notnull=True, requires=[IS_NOT_EMPTY(error_message='¿olvidaste decirnos el dominio?'), IS_NOT_IN_DB_OR_OWNERSHOP(db, shop.shop.id, error_message="Este dominio ya está siendo usado. Contacta con nosotros si crees que es un error por nuestra parte."), IS_URL(error_message="ejemplo de formato: gextiendas.es")])
		host=Field('host', 'string', length=45, notnull=False, requires=[IS_MATCH('^\w+$', 'Sólo letras y números')])
		form=SQLFORM.factory(domain, host, submit_button = 'establecer dominio')
		if form.validate():
			try:
				if ((db((db.domainshops.host==form.vars.host) & (db.domainshops.domain==form.vars.domain.replace("http://",""))).select().first()==None) and (form.vars.domain.replace("http://","")  not in ["gextiendas.es","gextiendas.com", "gestionexperta.com", "gestionexperta.es"])):
					if shop.priceplans.paymode=='ifselling' or shop.priceplans.paymode=='flatrate':
						db.domainshops.insert(shop=shop.shop.id, host=form.vars.host, domain=form.vars.domain.replace("http://",""), active="enabling")
					elif shop.priceplans.paymode=='free':
						db.domainshops.insert(shop=shop.shop.id, host=form.vars.host, domain=form.vars.domain.replace("http://",""), active="disabled")
					db.commit()
				else:
					session.flash="%s.%s ya está siendo utilizado" %(form.vars.host, form.vars.domain.replace("http://",""))
				redirection=True
			except Exception as ex:
				logger.debug("Error en account/setdomain %s" % ex)
				db.rollback()
				response.flash="Ocurrió un error al establecer el nombre de dominio."
		elif form.errors:
			response.flash="Ocurrió algún error"
		if redirection:
			redirect(URL('index'))
		return dict(form=form, ip=ip)
	else:
		redirect(URL('index'))

@auth.requires_login()
def storeboard():
	session.shopname=request.vars.host
	return dict(host=request.vars.host)

@auth.requires_login()
def datashop():
	from shops import Shop, DomainShop, ContractedProduct, Product
	from invoices import Order
	Shop(db), DomainShop(db), ContractedProduct(db), Product(db), Order(db)
	#store=db((db.shop.user==auth.user_id) & (db.shop.host==request.vars.host)).select()
	stores=db(	(db.shop.host==request.vars.host) & 
				(db.shop.user==auth.user_id)).select(	db.shop.ALL, 
														db.domainshops.ALL,
														db.priceplans.ALL,
														left=[	db.domainshops.on(db.domainshops.shop==db.shop.id),
																db.priceplans.on(db.priceplans.id==db.shop.priceplan)])
	
	contractedproducts= db( (db.contractedproducts.user==auth.user_id) &
							(db.contractedproducts.shop==stores[0].shop) &
							(db.contractedproducts.expiration<=datetime.datetime.now())).select(db.contractedproducts.ALL,
																								db.products.ALL,																								
																								left=[db.products.on(db.products.id==db.contractedproducts.product)])
	return dict(stores=stores, host=stores[0].shop.host, ip=stores[0].shop.ip, contractedproducts=contractedproducts)



@auth.requires_login()
def modifydomain():
	from shops import Shop, DomainShop, PricePlan
	Shop(db), DomainShop(db), PricePlan(db)
	shophost=request.vars.host
	shop=db((db.shop.host==request.vars.host) & (db.shop.user==auth.user_id)).select().first()
	redirection=False
	ip=shop.ip
	if shop:
		try:
			db( (db.domainshops.shop==shop.id) &
				(db.domainshops.host==request.vars.o_hostname) &
				(db.domainshops.domain==request.vars.o_domain)).update(domain=request.vars.domain, host=request.vars.hostname, active='modifying')
			db.commit()
			session.flash="Modificación realizada con éxito"
			return "ok"
		except Exception as ex:
			return ex
	else:
		session.flash="No podemos encontrar la tienda %s" % request.vars.host
		redirect(URL('index'))
	

@auth.requires_login()
def deletedomain():
	from shops import Shop, DomainShop, PricePlan
	Shop(db), DomainShop(db), PricePlan(db)
	shophost=request.vars.host
	shop=db((db.shop.host==request.vars.host) & (db.shop.user==auth.user_id)).select().first()
	redirection=False
	ip=shop.ip
	if shop:
		try:
			db( (db.domainshops.shop==shop.id) &
				(db.domainshops.host==request.vars.hostname) &
				(db.domainshops.domain==request.vars.domain)).delete()
			
			session.flash="Dominio borrado con éxito"
			return "ok"
		except Exception as ex:
			return ex
	else:
		session.flash="No podemos encontrar la tienda %s" % request.vars.host
		redirect(URL('index'))



@auth.requires_login()
def myservices():
	from shops import ContractedProduct, Product, Shop
	from invoices import Order, Orderlist
	from pagination import Pagination
	from adminsettings import Adminsettings
	Adminsettings(db)
	ContractedProduct(db), Product(db), Shop(db), Order(db), Orderlist(db)
	settings = db(db.adminsettings.id>0).select(db.adminsettings.ALL).first()
	records=db((db.contractedproducts.id>0) & (db.contractedproducts.user==auth.user_id)).count()
	items_per_page=settings.orderlistitems
	pag=Pagination(records, items_per_page)
	contractedproducts = db((db.contractedproducts.id>0) & (db.contractedproducts.user==auth.user_id)).select(
								db.contractedproducts.ALL, 
								db.products.ALL, 
								db.shop.ALL,
								db.auth_user.ALL,
								db.fiscals.ALL,
								left=[	db.products.on(db.products.id==db.contractedproducts.product),
										db.shop.on(db.shop.id==db.contractedproducts.shop),
										db.auth_user.on(db.auth_user.id==db.contractedproducts.user),
										db.fiscals.on(db.fiscals.user==db.auth_user.id)],
								orderby=~db.contractedproducts.expiration, limitby=pag.limitby())

	return dict(contractedproducts=contractedproducts, pagination=pag, records=records, items_per_page=items_per_page)	



@auth.requires_login()
def myaccount():
	from invoices import Fiscal
	from cities import Cities
	from province import Province
	Fiscal(db),	Province(db), Cities(db), 
	
	customer=db(db.auth_user.id==auth.user_id).select(	db.auth_user.id,
														db.auth_user.first_name,
														db.auth_user.last_name,
														db.auth_user.email,
														db.fiscals.ALL,
														left=[db.fiscals.on(db.fiscals.user==db.auth_user.id)]).first()

	wpoblacion = SQLFORM.widgets.autocomplete(request, db.cities.poblacion, limitby=(0,10), min_length=2)
	wprovincia = SQLFORM.widgets.autocomplete(request, db.province.provincia, limitby=(0,10), min_length=2)


	if customer!=None:

		first_name= Field('first_name', 'string', label=XML("<strong>Nombre</strong>"), length=128, notnull=True, default=customer.auth_user.first_name, requires=IS_NOT_EMPTY(error_message="No olvide esta dato"))
		last_name= Field('last_name', 'string', label=XML("<strong>Apellidos</strong>"), length=128, notnull=True, default=customer.auth_user.last_name, requires=IS_NOT_EMPTY(error_message="No olvide esta dato"))
		email=Field('email',  label=XML('<strong>Email</strong>'), length=128,  writable=False, notnull=True, default=customer.auth_user.email, requires=[IS_NOT_EMPTY(), IS_EMAIL(error_message='No puede estar vacío.')])
		tax_identification = Field('tax_identification', 'string', label=XML("<strong>NIF/CIF/NIE</strong> <span class='glyphicon glyphicon-question-sign'></span>"),length=45, notnull=True, default=customer.fiscals.tax_identification, requires=IS_NOT_EMPTY(error_message="No olvide esta dato"))
		fiscalname=Field('fiscalname', 'string', label=XML("<strong>Nombre empresa</strong>") ,length =128, notnull=False, default=customer.fiscals.fiscalname)
		address=Field('address', 'string', label=XML("<strong>Dirección</strong>"), length =196, notnull=True, default=customer.fiscals.address, requires=IS_NOT_EMPTY(error_message="no olvide este dato"))
		city= Field('city', 'string',   label=XML("<strong>Ciudad/Población</strong>"), length=45, notnull=True, default=customer.fiscals.city, requires=IS_NOT_EMPTY(error_message="no olvide este dato"), widget=wpoblacion)
		province = Field('province', 'string',   label=XML("<strong>Provincia</strong>"), length=45, notnull=True, default=customer.fiscals.province, requires=IS_NOT_EMPTY(error_message="no olvide este dato"), widget=wprovincia)
		country=Field('country', 'string', label=XML("<strong>Pais</strong>"), length =45, notnull=True, default=customer.fiscals.country, requires=IS_NOT_EMPTY(error_message="no olvide este dato"))
		postalcode=Field('postal_code', 'string', label=XML("<strong>Código postal</strong>"), length=10, notnull=False, default=customer.fiscals.postal_code)
		phone=Field('phone', 'string', label=XML("<strong>Teléfono</strong>"), length=20, notnull=False, default=customer.fiscals.phone)

		form = SQLFORM.factory(first_name, last_name, email, tax_identification, fiscalname, address, city, province, country, postalcode, phone, submit_button = 'modificar datos', formstyle='bootstrap3_inline')

		if form.validate(keepvalues=True):

			try:
				db(db.auth_user.id==customer.auth_user.id).update(first_name=form.vars.first_name,
																  last_name=form.vars.last_name)
				db(db.fiscals.id==customer.fiscals.id).update(tax_identification=form.vars.tax_identification, 
													fiscalname=form.vars.fiscalname,
													address=form.vars.address, 
													city=form.vars.city,
													province=form.vars.province,
													country=form.vars.country, 
													postal_code=form.vars.postal_code,
													phone=form.vars.phone)
				db.commit()
			except Exception, ex:
				logger.debug("No se pudo modificar los datos del usuario/fiscal: %s" % ex)
				db.rollback()
				response.flash = 'Hubo un error: %s' % ex				
			response.flash="Datos modificados correctamente"
		elif form.errors:
			response.flash = 'Hay errores'
		else:
			response.flash = 'Por favor completa los campos'
		
		form.element('input[name=city]')['_class']='form-control'
		form.element('input[name=province]')['_class']='form-control'

		form.element('input[name=city]')['_class']='form-control'
		form.element('input[name=province]')['_class']='form-control'
		form.element('div#no_table_first_name__row div.col-sm-9')['_class']='col-sm-4'
		form.element('div#no_table_last_name__row div.col-sm-9')['_class']='col-sm-4'
		form.element('div#no_table_tax_identification__row div.col-sm-9')['_class']='col-sm-3'
		form.element('div#no_table_fiscalname__row div.col-sm-9')['_class']='col-sm-4'
		form.element('div#no_table_city__row div.col-sm-9')['_class']='col-sm-4'
		form.element('div#no_table_province__row div.col-sm-9')['_class']='col-sm-3'
		form.element('div#no_table_country__row div.col-sm-9')['_class']='col-sm-2'
		form.element('div#no_table_postal_code__row div.col-sm-9')['_class']='col-sm-2'
		form.element('div#no_table_phone__row div.col-sm-9')['_class']='col-sm-4'
		form.element('label#no_table_first_name__label')['_class']='col-sm-2 control-label'
		form.element('label#no_table_last_name__label')['_class']='col-sm-2 control-label'
		form.element('label#no_table_email__label')['_class']='col-sm-2 control-label'
		form.element('label#no_table_fiscalname__label')['_class']='col-sm-2 control-label'
		form.element('label#no_table_tax_identification__label')['_class']='col-sm-2 control-label'
		form.element('label#no_table_address__label')['_class']='col-sm-2 control-label'
		form.element('label#no_table_city__label')['_class']='col-sm-2 control-label'
		form.element('label#no_table_province__label')['_class']='col-sm-2 control-label'
		form.element('label#no_table_country__label')['_class']='col-sm-2 control-label'
		form.element('label#no_table_postal_code__label')['_class']='col-sm-2 control-label'
		form.element('label#no_table_phone__label')['_class']='col-sm-2 control-label'
		form.element('div#submit_record__row div.col-sm-9')['_class']='col-sm-9 col-sm-offset-2'
		return dict(form=form, userid=customer.auth_user.id)











@auth.requires_login()
def mycredit():
	from invoices import CreditAccount, AccountingEntry, Order, Orderlist 
	Order(db), CreditAccount(db), AccountingEntry(db), Orderlist(db)
	creditaccount=db(db.creditaccounts.user==auth.user_id).select().first()
	accountingentries=None
	if creditaccount:
		accountingentries=db(	(db.accountingentries.creditaccount==creditaccount.id) &
								(db.accountingentries.active==True) ).select(	db.accountingentries.ALL, 
																				db.orders.ALL,
																				db.invoices.ALL,
																				db.products.name,
																				join=[	db.orderlist.on(db.accountingentries.orderlist==db.orderlist.id),
																						db.products.on(db.products.id==db.orderlist.product),
																						db.orders.on(db.orders.id==db.orderlist.g_order),
																						db.invoices.on(db.invoices.id==db.orders.invoice)],
																				orderby=~db.accountingentries.id)

	return dict(creditaccount=creditaccount, accountingentries=accountingentries, invoices=db(db.invoices.user==auth.user_id).select())

@auth.requires_login()
def viewinvoice():
	from invoices import Invoice, Order, Orderlist, Budget, AccountingEntry, CreditAccount
	Invoice(db), Order(db), Orderlist(db), Budget(db), AccountingEntry(db), CreditAccount(db)
	invoice= db((db.invoices.invoice_number==request.args(0)) & (db.invoices.user==auth.user_id)).select(db.invoices.ALL, 
																	db.auth_user.id,
																	db.auth_user.first_name,
																	db.auth_user.last_name,  
																	db.fiscals.ALL,
																	left=[	db.auth_user.on(db.auth_user.id==db.invoices.user),
																			db.fiscals.on(db.fiscals.user==db.auth_user.id)]).first()


	orderlist= db(db.orders.invoice==invoice.invoices.id).select(	db.orders.ALL, 
																	db.orderlist.ALL,
																	db.products.ALL,
																	left=[	db.orderlist.on(db.orderlist.g_order==db.orders.id),
																			db.products.on(db.products.id==db.orderlist.product)])

	order=db(db.orders.invoice==invoice.invoices.id).select(db.orders.ALL).first()

	return dict(invoice=invoice, orderlist=orderlist, order=order)
	



################ private functions

def __get_ip_address(ifname):
	import socket
	import fcntl
	import struct
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	# info = fcntl.ioctl(s.fileno(), 0x8927, struct.pack)
	return socket.inet_ntoa(fcntl.ioctl(
		s.fileno(),
		0x8915, #SIOCGIFADDR
		struct.pack('256s', ifname[:15])
	)[20:24])


