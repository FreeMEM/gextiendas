# coding: utf8
from adminsettings import Adminsettings
Adminsettings(db)
@auth.requires_login()
@page_allowed_ip
def bloglist():
	if auth.has_membership('administradores') or auth.has_membership('superadministradores'):
		from pagination import Pagination
		from blog import Blog, Draft, Images
		settings = db(db.adminsettings.id>0).select(db.adminsettings.ALL).first()
		blog=Blog(db,ckeditor)
		draft=Draft(db,ckeditor)
		Images(db)
		brecords=db(db.blog.id>0).count()
		drecords=db(db.draft.id>0).count()
		records = int(brecords) + int(drecords)
		items_per_page=settings.bloglistitems
		pag=Pagination(records, items_per_page)
		drafts =db().select(db.draft.ALL, orderby=~db.draft.id, limitby=pag.limitby())
		posts = db().select(db.blog.ALL, orderby=~db.blog.id, limitby=pag.limitby())
		return dict(posts=posts, drafts=drafts, pagination=pag, records=records, items_per_page=items_per_page)
	else:
		redirect(URL(request.application,'blog','index'))



@auth.requires_login()
@page_allowed_ip
def emailbox():
	if auth.has_membership('administradores') or auth.has_membership('superadministradores'):
		settings = db(db.adminsettings.id>0).select(db.adminsettings.ALL).first()
		from pagination import Pagination
		from mailboxing import Mailboxing
		Mailboxing(db)
		records=db(db.mailbox.id>0).count()
		notreads=db(db.mailbox.messread==False).count()
		items_per_page=settings.messageitems
		pag=Pagination(records, items_per_page)
		messages = db().select(db.mailbox.ALL, orderby=~db.mailbox.id, limitby=pag.limitby())
		return dict(messages=messages, pagination=pag, records=records, items_per_page=items_per_page, notreads=notreads)
	else:
		redirect(URL(request.application,'default','user/login'))



@auth.requires_login()
@page_allowed_ip
def subscriptions():
	if auth.has_membership('administradores') or auth.has_membership('superadministradores'):
		from pagination import Pagination
		from regnews import Regnews
		settings = db(db.adminsettings.id>0).select(db.adminsettings.ALL).first()
		try:
			reg=Regnews(db)
			reg.define_tables()
		except:
			pass
		records=db(db.regnews.id>0).count()
		items_per_page=settings.subscriptionitems
		pag=Pagination(records, items_per_page)
		subscriptions = db().select(db.regnews.ALL, orderby=~db.regnews.id, limitby=pag.limitby())
		return dict(subscriptions=subscriptions, pagination=pag, records=records, items_per_page=items_per_page, actives=db(db.regnews.news==True).count())
	else:
		redirect(URL(request.application,'default','user/login'))

@auth.requires_login()
@page_allowed_ip
def setread():
	if auth.has_membership('administradores') or auth.has_membership('superadministradores'):
		from mailboxing import Mailboxing

		Mailboxing(db)

		data=request.vars
		try:
			db(db.mailbox.id==data.id).update(messread=data.read)
			return "true"
		except:
			return "false"
	else:
		redirect(URL(request.application,'default','user/login'))



@auth.requires_login()
@page_allowed_ip
def users():
	if auth.has_membership('administradores') or auth.has_membership('superadministradores'):
		return dict(users=db(db.auth_user).select())
	else:
		redirect(URL(request.application,'default','user/login'))

@auth.requires_login()
@page_allowed_ip
def setgroupid():
	if auth.has_membership('administradores') or auth.has_membership('superadministradores'):
		data = request.vars
		try:
			if data.user_id!= auth.user.id:
				db(db.auth_membership.user_id==data.user_id).delete()
				auth.add_membership(data.group_id, data.user_id)
				db.commit()
				return "true"
			else:
				return "false"
		except:
			return "false"

	else:
		redirect(URL(request.application,'default','user/login'))


@auth.requires_login()
@page_allowed_ip
def orders():
	if auth.has_membership('administradores') or auth.has_membership('superadministradores'):
		from shops import Shop, ContractedProduct
		from invoices import Order, Orderlist
		from pagination import Pagination
		Order(db), Orderlist(db), Shop(db), ContractedProduct(db)
		settings = db(db.adminsettings.id>0).select(db.adminsettings.ALL).first()
		records=db(db.orders.status!="CreandoAdmin").count()
		items_per_page=settings.orderlistitems
		pag=Pagination(records, items_per_page)
		#orders = db(db.orders.status!="CreandoAdmin").select(db.orders.ALL, orderby=~db.orders.id, limitby=pag.limitby())

		orders=db(db.orders.status!="CreandoAdmin").select(db.orders.ALL, 
													
													db.shop.host,
													left=[	db.orderlist.on(db.orderlist.g_order==db.orders.id),
															db.contractedproducts.on(db.contractedproducts.orderlist==db.orderlist.id),
															db.shop.on(db.shop.id==db.contractedproducts.shop)],
													orderby=~db.orders.id,
													groupby=db.orders.id, 
													limitby=pag.limitby())




		return dict(orders=orders, pagination=pag, records=records, items_per_page=items_per_page)

	else:
		redirect(URL(request.application,'default','user/login'))


@auth.requires_login()
@page_allowed_ip
def contractedproducts():
	if auth.has_membership('administradores') or auth.has_membership('superadministradores'):

		from shops import ContractedProduct, Product, Shop
		from invoices import Order, Orderlist
		from pagination import Pagination
		ContractedProduct(db), Product(db), Shop(db), Order(db), Orderlist(db)
		settings = db(db.adminsettings.id>0).select(db.adminsettings.ALL).first()
		records=db(db.contractedproducts.id>0).count()
		items_per_page=settings.orderlistitems
		pag=Pagination(records, items_per_page)
		contractedproducts = db(db.contractedproducts.id>0).select(	db.contractedproducts.ALL,
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

	else:
		redirect(URL(request.application,'default','user/login'))

@auth.requires_login()
@page_allowed_ip
def settings():
	if auth.has_membership('administradores') or auth.has_membership('superadministradores'):

		settings = db(db.adminsettings.id>0).select(db.adminsettings.ALL).first()

		if settings:
			servername = Field('mailserver', 'string',label="Servidor de correo", length=128, notnull=True, default = settings.mailserver, requires=IS_NOT_EMPTY(error_message="No puede estar vacío"), widget=lambda field,value: SQLFORM.widgets.string.widget(field, value, _placeholder='ejemplo: smtp.dominio.com'))
			username = Field('username', 'string', label="Nombre de usuario", default=settings.username, length=128, requires=IS_NOT_EMPTY(error_message="No puede estar vacío"))
			password = Field('password', 'string', label = "Contraseña", length=64, readable=False)
			emailfrom = Field('emailfrom', 'string', length=128, default=settings.emailfrom, label="Contestar a", requires=IS_EMAIL(error_message="Formato de email incorrecto"), widget=lambda field,value: SQLFORM.widgets.string.widget(field, value, _placeholder='nombre de usuario o cuenta de email'))
			blogitems = Field('blogitems', 'integer', length=4, default=settings.blogitems, label="Blog items/pág")
			queryitems = Field('queryitems', 'integer', default=(15, settings.queryitems)[settings.queryitems!=None], label="Consultas items/pag.")
			messageitems = Field('messageitems', 'integer', length=4,default=settings.messageitems, label="Adm. Mensajes items/pag.")
			bloglistitems = Field('bloglistitems', 'integer', length=4, default=settings.bloglistitems, label="Adm. Blog items/pag.")
			orderlistitems = Field('orderlistitems', 'integer', length=4, default=settings.orderlistitems, label="Adm. Pedidos items/pag.")
			productitems = Field('productitems', 'integer', length=4, default=settings.productitems, label="Adm. Productos items/pag.")
			useritems = Field('useritems', 'integer', length=4, default=settings.useritems, label="Adm. Usuarios items/pag.")
			subscriptionitems =Field('subscriptionitems', 'integer', default=settings.subscriptionitems, label="Adm. Suscriptores items/pag.")
			querylistitems = Field('querylistitems', 'integer', default=(15, settings.querylistitems)[settings.querylistitems!=None], label="Adm. Consultas items/pag.")
			invoiceitems =Field('invoiceitems', 'integer', default=settings.invoiceitems, label="Adm. Facturas items/pag.")
			tax=Field('tax', 'decimal(10,2)', default=settings.tax, label="IVA general")
			bank_account=Field('bank_account', 'string', length="30", label="Cuenta bancaria", default=settings.bank_account)
			beneficiary=Field('beneficiary', 'string', length="120", label="Beneficiario", default=settings.beneficiary)
			bank=Field('bank', 'string', length="120", label="Entidad bancaria", default=settings.bank)
			serialinit=Field('serialinit', 'integer', length=11, label="Inicio serie facturación", default=settings.serialinit)
			form = SQLFORM.factory(servername, username, password, emailfrom, blogitems, queryitems, messageitems, bloglistitems, orderlistitems, productitems, useritems, subscriptionitems, querylistitems, invoiceitems, tax, bank_account, beneficiary, bank, serialinit, submit_button = 'Guardar', formstyle='bootstrap3_inline')

			if form.validate():
				if form.vars.password!="" and form.vars.password!=None:
					db(db.adminsettings.id==settings.id).update(**dict(form.vars))
				else:
					db(db.adminsettings.id==settings.id).update(
						mailserver=form.vars.mailserver,
						username=form.vars.username,
						emailfrom=form.vars.emailfrom,
						blogitems=form.vars.blogitems,
						queryitems=form.vars.queryitems,
						messageitems=form.vars.messageitems,
						bloglistitems=form.vars.bloglistitems,
						orderlistitems=form.vars.orderlistitems,
						productitems=form.vars.productitems,
						useritems=form.vars.useritems,
						subscriptionitems=form.vars.subscriptionitems,
						querylistitems=form.vars.querylistitems,
						invoiceitems=form.vars.invoiceitems,
						tax=form.vars.tax,
						bank_account=form.vars.bank_account,
						beneficiary=form.vars.beneficiary,
						bank=form.vars.bank,
						serialinit=form.vars.serialinit,
						)
				# settings.update(**dict(form.vars))
				db.commit()
				session.flash = 'Modificaciones guardadas'
				redirect(URL('administrator','settings'))
			elif form.errors:

				response.flash = 'Hay algunos errores'
			else:
				response.flash = 'Por favor completa los campos'


		else:
			servername = Field('mailserver', 'string',label="Servidor de correo", length=128, notnull=True, requires=IS_NOT_EMPTY(error_message="No puede estar vacío"), widget=lambda field,value: SQLFORM.widgets.string.widget(field, value, _placeholder='ejemplo: smtp.dominio.com'))
			username = Field('username', 'string', label="Nombre de usuario", length=128, requires=IS_NOT_EMPTY(error_message="No puede estar vacío"))
			password = Field('password', 'string', label = "Contraseña", length=64, readable=False)
			emailfrom = Field('emailfrom', 'string', length=128,  label="Contestar a", requires=IS_EMAIL(error_message="Formato de email incorrecto"), widget=lambda field,value: SQLFORM.widgets.string.widget(field, value, _placeholder='nombre de usuario o cuenta de email'))
			blogitems = Field('blogitems', 'integer', length=4, default=20, label="Blog items/pág")
			queryitems = Field('queryitems', 'integer', default=15, label="Consultas items/pag.")
			messageitems = Field('messageitems', 'integer', length=4,default=15, label="Adm. Mensajes items/pag.")
			bloglistitems = Field('bloglistitems', 'integer', length=4, default=15, label="Adm. Blog items/pág")
			orderlistitems = Field('orderlistitems', 'integer', length=4, default=15, label="Adm. Pedidos items/pag.")
			productitems = Field('productitems', 'integer', length=4, default=15, label="Adm. Productos items/pag.")
			useritems = Field('useritems', 'integer', length=4, default=15, label="Adm. Usuarios items/pág")
			subscriptionitems =Field('subscriptionitems', 'integer', default=15, label="Adm. Suscriptores items/pág")
			invoiceitems =Field('invoiceitems', 'integer', default=15, label="Adm. Facturas items/pag.")
			querylistitems = Field('querylistitems', 'integer', default=15, label="Adm. Consultas items/pag.")
			tax=Field('tax', 'decimal(10,2)', default=21, label="IVA general")
			bank_account=Field('bank_account', 'string', length="30", label="Cuenta bancaria", default="")
			beneficiary=Field('beneficiary', 'string', length="120", label="Beneficiario", default="")
			bank=Field('bank', 'string', length="120", label="Entidad bancaria", default="")
			serialinit=Field('serialinit', 'integer', length=11, label="Inicio serie facturación", default="1000101")
			form = SQLFORM.factory(servername, username, password, emailfrom, blogitems, queryitems, messageitems, bloglistitems, useritems, subscriptionitems, querylistitems,invoiceitems, bank_account, beneficiary, bank, tax, submit_button = 'Guardar', formstyle='bootstrap3_inline')

			if form.validate():
				db.adminsettings.insert(**dict(form.vars))
				session.flash = 'Configuración guardada'
				redirect(URL('administrator','settings'))
			elif form.errors:
				response.flash = 'Hay errores'
			else:
				response.flash = 'Por favor completa los campos'

		return dict(form=form)


	else:
		redirect(URL(request.application,'default','user/login'))


@auth.requires_login()
@page_allowed_ip
def order_approving():
	if auth.has_membership('administradores') or auth.has_membership('superadministradores'):
		from shops import ContractedProduct, Product, Shop
		from invoices import Order, Orderlist, Invoice, CreditAccount, AccountingEntry
		from queuemail import Queuemail
		from gluon.contrib.pysimplesoap.client import SoapClient
		queue=Queuemail(db)
		ContractedProduct(db), Product(db), Shop(db), Order(db), Orderlist(db),  AccountingEntry(db)
		order=db.orders(request.vars.order)
		
		# order=db.orders(orderid)
		try:
			if order:
				#crear factura
				invoice=Invoice(db)
				invoiceid=invoice.makeinvoice(order.id) #aquí se hace además la anotación positiva en creditaccount
				if invoiceid!=None:
					# notificar recepción del pago
					subject="[gextiendas] Factura Nº %s" % db.invoices(invoiceid).invoice_number
					queuedata=[]

					urlinvoice= '%(scheme)s://%(host)s%(url)s' % {'scheme':request.env.wsgi_url_scheme,'host':request.env.http_host, 'url':URL('payment','code',args=[order.payment_code.code])}
					data={	"now": datetime.datetime.now().strftime("%d-%m-%Y %H:%M"),
									"name": order.user.first_name, 
									"code": order.payment_code.code,
									"url": urlinvoice,
						}
					plaintext="""
							\t\t\t\t Fuengirola (Málaga), a %(now)s \n
							Estimado %(name)s, hemos recibido un pago mediante transferencia correspondiente a la referencia de pago: %(code)s \n
							Puede descargarse la factura siguiendo este enlace:\n
							%(url)s \n
							El equipo de GEXtiendas.\n

								""" % data	
					html="""
							<p>Fuengirola (Málaga), a %(now)s</p>
							<p>Estimado %(name)s, hemos recibido un pago mediante transferencia correspondiente a la referencia de pago: %(code)s</p>
							<p>Puede descargarse la factura siguiendo este enlace:</p>
							<p><a href='%(url)s'>%(url)s</a></p>
							<p>El equipo de GEXtiendas.</p>
						""" % data


					queuedata.append({	'to': '%s'%order.user.email,
										'subject':subject,
										'message':plaintext,
										'html':XML(html),
										'template':'communications/paymentreceived_template.html',
										'title':'Pago recibido: %s' % subject,
										'unsubscribe':''
									})
					queue.queuemessage(queuedata)

					#
					# client = SoapClient(wsdl="http://localhost:8000/internalgexcommerce/default/call/soap?WSDL=None")
					# logger.debug(client.enableDomainShop())
					# buscar si hay dominios que estén esperando ser habilitados en una tienda del productocontratado en la lista de ese pedido
					# activar dominio
					# anotar accountinentry negativo
					# actualizar crédito

					session.flash="Operación realizada con éxito"
				else:
					session.flash="Hubo un error y no se pudo aprobar el pedido"
			else:
				session.flash="Hubo un error. No se pudo aprobar el pedido"

		except Exception as ex:

			logger.debug(ex)
			session.flash="Ocurrió un error %s " % ex

		redirect(URL('administrator','orders'))
	else:

		redirect(URL(request.application,'default','user/login'))

@auth.requires_login()
@page_allowed_ip
def products():
	if auth.has_membership('administradores') or auth.has_membership('superadministradores'):
		from shops import Product, PricePlan
		from pagination import Pagination
		Product(db), PricePlan(db)

		settings = db(db.adminsettings.id>0).select(db.adminsettings.ALL).first()
		records=db(db.products.id>0).count()
		items_per_page=settings.productitems
		pag=Pagination(records, items_per_page)
		products=db(db.products.id>0).select(db.products.ALL, db.priceplans.planname, left=[db.priceplans.on(db.priceplans.id==db.products.plan)], orderby=db.products.id, limitby=pag.limitby())
		return dict(products=products, pagination=pag, records=records, items_per_page=items_per_page)
	else:
		redirect(URL(request.application,'default','user/login'))

@auth.requires_login()
@page_allowed_ip
def priceplans():
	if auth.has_membership('administradores') or auth.has_membership('superadministradores'):
		from shops import PricePlan
		from pagination import Pagination
		PricePlan(db)
		
		priceplans=db(db.priceplans.id>0).select()
		records=db(db.priceplans.id>0).count()
		return dict(priceplans=priceplans, records=records)
	else:
		redirect(URL(request.application,'default','user/login'))

@auth.requires_login()
@page_allowed_ip
def editproduct():
	if auth.has_membership('administradores') or auth.has_membership('superadministradores'):
		from shops import Product, PricePlan
		from pagination import Pagination
		Product(db), PricePlan(db)

		if request.vars.productid:
			product=db(db.products.id==request.vars.productid).select(db.products.ALL, db.priceplans.planname, left=[db.priceplans.on(db.priceplans.id==db.products.plan)]).first()
			name= Field('name', 'string', length=128, default=product.products.name, notnull=True, unique=True, requires=IS_NOT_EMPTY())
			price=Field('price', 'decimal(10,2)', default=product.products.price, notnull=True, requires=[IS_NOT_EMPTY(error_message='el precio es obligatorio'),IS_DECIMAL_IN_RANGE(minimum=0, maximum=10000, error_message='el precio debe ser entre 0.00 y 10000.00')])
			description=Field('description', 'text', default=product.products.description, notnull=False)
			active=Field('active', 'boolean', default=product.products.active)
			subscription=Field('suscription', 'boolean', default=product.products.suscription)
			min_period=Field('min_period', 'string', length='16', notnull=False, default=product.products.min_period, requires=IS_EMPTY_OR(IS_IN_SET(['hours','days','week','month','year'], error_message="Elija un estado")))
			plan=Field('plan', 'reference priceplans', default=product.products.plan, notnull=False, requires=IS_EMPTY_OR(IS_IN_DB(db, db.priceplans.id,'%(planname)s', error_message="Debe escoger un plan")))
			builtin=Field('builtin', 'boolean', default=product.products.builtin)
			form = SQLFORM.factory(name, price, description, active, subscription, min_period,  plan, builtin, submit_button = 'Guardar', formstyle='bootstrap3_inline')
			if form.validate():
				db(db.products.id==product.products.id).update(**dict(form.vars))
				session.flash = 'Producto editado'
				redirect(URL('administrator','products'))
			elif form.errors:
				response.flash = 'Hay errores'
			else:
				response.flash = 'Por favor completa los campos'

			return dict(form=form)
		else:
			redirect(URL(request.application,'administrator','newproduct'))

	else:
		redirect(URL(request.application,'default','user/login'))



@auth.requires_login()
@page_allowed_ip
def newproduct():
	if auth.has_membership('administradores') or auth.has_membership('superadministradores'):
		from shops import Product, PricePlan
		from pagination import Pagination
		Product(db), PricePlan(db)
		name= Field('name', 'string', label="Nombre", length=128, notnull=True, unique=True, requires=IS_NOT_EMPTY())
		price=Field('price', 'decimal(10,2)', label="Precio", notnull=True, requires=[IS_NOT_EMPTY(error_message='el precio es obligatorio'),IS_DECIMAL_IN_RANGE(minimum=0, maximum=10000, error_message='el precio debe ser entre 0.00 y 10000.00')])
		description=Field('description', 'text', label="Descripción",notnull=True, requires=IS_NOT_EMPTY(error_message='se necesita una descripción'))
		active=Field('active', 'boolean', default=True)
		subscription=Field('suscription', 'boolean', default=True)
		min_period=Field('min_period', 'string', length='16', notnull=False, default='month', requires=IS_EMPTY_OR(IS_IN_SET(['hours','days','week','month','year'], error_message="Elija un estado")))
		plan=Field('plan', 'reference priceplans', default=None, notnull=False, requires=IS_EMPTY_OR(IS_IN_DB(db, db.priceplans.id,'%(planname)s', error_message="Debe escoger un plan")))
		builtin=Field('builtin', 'boolean', default=False)
		form = SQLFORM.factory(name, price, description, active, subscription, min_period, plan, builtin, submit_button = 'Guardar', formstyle='bootstrap3_inline')

		if form.validate():
			db.products.insert(**dict(form.vars))
			session.flash = 'Producto creado'
			redirect(URL('administrator','products'))
		elif form.errors:
			response.flash = 'Hay errores'
		else:
			response.flash = 'Por favor completa los campos'

		return dict(form=form)


@auth.requires_login()
@page_allowed_ip
def editpriceplan():
	if auth.has_membership('administradores') or auth.has_membership('superadministradores'):
		from shops import PricePlan
		from pagination import Pagination
		PricePlan(db)

		if request.vars.priceplanid:
			priceplan=db(db.priceplans.id==request.vars.priceplanid).select().first()
			name = Field('planname', 'string', label="Nombre del plan", length=128, default=priceplan.planname, notnull=True, unique=True, requires=IS_NOT_EMPTY())
			paymode = Field('paymode', 'string', default=priceplan.paymode, length=16, requires=IS_IN_SET(['free','ifselling','flatrate'], error_message="Elija opción", zero=None))
			explanation = Field('explanation', 'text', default=priceplan.explanation, notnull=False)
			
			form = SQLFORM.factory(name, paymode, explanation, submit_button = 'Guardar', formstyle='bootstrap3_inline')
			if form.validate():
				db(db.priceplans.id==priceplan.id).update(**dict(form.vars))
				session.flash = 'datos guardados'
				redirect(URL('administrator','priceplans'))
			elif form.errors:
				response.flash = 'Hay errores'
			else:
				response.flash = 'Por favor completa los campos'

			return dict(form=form)
		else:
			redirect(URL(request.application,'administrator','newpriceplan'))

	else:
		redirect(URL(request.application,'default','user/login'))


@auth.requires_login()
@page_allowed_ip
def newpriceplan():
	if auth.has_membership('administradores') or auth.has_membership('superadministradores'):
		from shops import PricePlan
		from pagination import Pagination
		PricePlan(db)

		name = Field('planname', 'string', label="Nombre del plan", length=128, notnull=True, unique=True, requires=IS_NOT_EMPTY(error_message="No olvide el nombre del plan"))
		paymode = Field('paymode', 'string', length=16, requires=IS_IN_SET(['free','ifselling','flatrate'], error_message="Elija opción", zero=None))
		explanation = Field('explanation', 'text',  notnull=False)
		
		form = SQLFORM.factory(name, paymode, explanation, submit_button = 'Guardar', formstyle='bootstrap3_inline')
		if form.validate():
			db.priceplans.insert(**dict(form.vars))
			session.flash = 'plan creado'
			redirect(URL('administrator','priceplans'))
		elif form.errors:
			response.flash = 'Hay errores'
		else:
			response.flash = 'Por favor completa los campos'

		return dict(form=form)

	else:
		redirect(URL(request.application,'default','user/login'))


@auth.requires_login()
@page_allowed_ip
def profileplans():
	if auth.has_membership('administradores') or auth.has_membership('superadministradores'):
		from shops import Product, PricePlan, ProfilePlan
		from pagination import Pagination
		Product(db), PricePlan(db), ProfilePlan(db)
		prod=request.vars.product
		pricep=request.vars.priceplan

		if (prod!=None) and (pricep!=None):
			try:
				db.profileplans.insert(priceplan=pricep, product=prod)
			except Exception as ex:
				db.rollback()
				logger.debug("ocurrió un error al crear un perfil de plan")
				response.flash="ocurrió un error al crear un perfil de plan"
				
		profileplans=db(db.profileplans.id>0).select(	db.profileplans.ALL,
														db.priceplans.planname,
														db.products.name,
														join=[	db.priceplans.on(db.priceplans.id==db.profileplans.priceplan),
																db.products.on(db.products.id==db.profileplans.product)],
														orderby=db.profileplans.priceplan)
		return dict(profileplans=profileplans, 
					records=db(db.profileplans.id>0).count(), 
					priceplans=db(db.priceplans.id>0).select(), 
					products=db(db.products.id>0).select())
	else:
		redirect(URL(request.application,'default','user/login'))


@auth.requires_login()
@page_allowed_ip
def del_profileplans():
	if auth.has_membership('administradores') or auth.has_membership('superadministradores'):
		from shops import Product, PricePlan, ProfilePlan
		from pagination import Pagination
		Product(db), PricePlan(db), ProfilePlan(db)
		try:
			if db(db.profileplans.id==request.vars.deleteid).delete():
				return "OK"
			else:
				return "Fail"
		except Exception, ex:
			logger.debug('hubo un error al borrar el profileplans id: %    error: %' % (request.vars.deleteid, ex))
			return "Fail"

	else:
		redirect(URL(request.application,'default','user/login'))







@auth.requires_login()
@page_allowed_ip
def newcustomer():
	if auth.has_membership('administradores') or auth.has_membership('superadministradores'):

		from invoices import Fiscal
		from cities import Cities
		from province import Province
		Fiscal(db),	Province(db), Cities(db)

		wpoblacion = SQLFORM.widgets.autocomplete(request, db.cities.poblacion, limitby=(0,10), min_length=2)
		wprovincia = SQLFORM.widgets.autocomplete(request, db.province.provincia, limitby=(0,10), min_length=2)
		first_name = Field('first_name', 'string', label=XML("<strong>Nombre</strong>"), length=128, notnull=True, requires=IS_NOT_EMPTY(error_message="No olvide esta dato"))
		last_name = Field('last_name', 'string', label=XML("<strong>Apellidos</strong>"), length=128, notnull=True, requires=IS_NOT_EMPTY(error_message="No olvide esta dato"))
		password = Field('password', label = XML("<strong>Contraseña</strong>"), requires=[IS_NOT_EMPTY(error_message="No olvide esta dato")])
		email = Field('email',  label=XML('<strong>Email</strong>'), length=128,  notnull=True, requires=[IS_NOT_EMPTY(), IS_EMAIL(error_message='No puede estar vacío.'), IS_NOT_IN_DB(db,'auth_user.email')])
		tax_identification = Field('tax_identification', 'string', label=XML("<strong>NIF/CIF/NIE</strong> <span class='glyphicon glyphicon-question-sign'></span>"),length=45, notnull=False)
		fiscalname = Field('fiscalname', 'string', label=XML("<strong>Nombre empresa</strong>") ,length =128, notnull=False)
		address = Field('address', 'string', label=XML("<strong>Dirección</strong>"), length =196, notnull=False)
		city = Field('city', 'string',   label=XML("<strong>Ciudad/Población</strong>"), length=45, notnull=False, widget=wpoblacion)
		province = Field('province', 'string',   label=XML("<strong>Provincia</strong>"), length=45, notnull=False, widget=wprovincia)
		country = Field('country', 'string', label=XML("<strong>Pais</strong>"), length =45, notnull=False)
		postalcode = Field('postal_code', 'string', label=XML("<strong>Código postal</strong>"), length=10, notnull=False)
		phone = Field('phone', 'string', label=XML("<strong>Teléfono</strong>"), length=20, notnull=False)

		form = SQLFORM.factory(first_name, last_name, password, email, tax_identification, fiscalname, address, city, province, country, postalcode, phone, submit_button = 'enviar datos', formstyle='bootstrap3_inline')



		if form.validate(keepvalues=True):

			try:
				userid=db.auth_user.insert(first_name=form.vars.first_name,
									last_name=form.vars.last_name,
									password=CRYPT(key=Auth.get_or_create_key(), digest_alg='pbkdf2(1000,20,sha512)', salt=True)(form.vars.password)[0],
									email=form.vars.email)
				if userid:
					db.fiscals.insert(	user=userid, 
										tax_identification=form.vars.tax_identification, 
										fiscalname=form.vars.fiscalname,
										address=form.vars.address, 
										city=form.vars.city,
										province=form.vars.province,
										country=form.vars.country, 
										postal_code=form.vars.postal_code,
										phone=form.vars.phone)
					auth.add_membership(db(db.auth_group.role=="clientes").select().first()["id"], userid)
					db.commit()
				else:
					response.flash="no se ha creado al usario"

			except Exception, ex:
				logger.debug("No se pudo crear al nuevo cliente: %s" % ex)
				db.rollback()
				response.flash = 'Hubo un error: %s' % ex
			redirect(URL('administrator','editcustomer', args=userid))
		elif form.errors:
			response.flash = 'Hay errores'
		else:
			response.flash = 'Por favor completa los campos'
		
		form.element('input[name=city]')['_class']='form-control'
		form.element('input[name=province]')['_class']='form-control'
		
		return dict(form=form)
	else:
		redirect(URL(request.application,'default','user/login'))





@auth.requires_login()
@page_allowed_ip
def editcustomer():
	if auth.has_membership('administradores') or auth.has_membership('superadministradores'):
		if request.args(0):
			from invoices import Fiscal, Order, Orderlist, Invoice, Budget, AccountingEntry, CreditAccount
			from shops import ContractedProduct, Product, Shop
			from cities import Cities
			from province import Province
			Fiscal(db),	Province(db), Cities(db), ContractedProduct(db), Product(db), Shop(db), Order(db), Orderlist(db), AccountingEntry(db), CreditAccount(db),  Invoice(db), Budget(db)
			
			customer=db(db.auth_user.id==request.args(0)).select(	db.auth_user.id,
																	db.auth_user.first_name,
																	db.auth_user.last_name,
																	db.auth_user.email,
																	db.fiscals.ALL,
																	left=[db.fiscals.on(db.fiscals.user==db.auth_user.id)]).first()
			
			wpoblacion = SQLFORM.widgets.autocomplete(request, db.cities.poblacion, limitby=(0,10), min_length=2)
			wprovincia = SQLFORM.widgets.autocomplete(request, db.province.provincia, limitby=(0,10), min_length=2)


			inc=datetime.timedelta(days=30)
			
			contractedproducts = db((db.contractedproducts.user==request.args(0)) & 
									(	(db.contractedproducts.expiration+inc>=datetime.datetime.now()) | 
										(db.contractedproducts.expiration==None)	)).select(	db.contractedproducts.ALL,
																							db.products.ALL,
																							db.shop.ALL,
																							db.auth_user.ALL,
																							db.fiscals.ALL,
																							left=[	db.products.on(db.products.id==db.contractedproducts.product),
																									db.shop.on(db.shop.id==db.contractedproducts.shop),
																									db.auth_user.on(db.auth_user.id==db.contractedproducts.user),
																									db.fiscals.on(db.fiscals.user==db.auth_user.id)],
																							orderby=~db.contractedproducts.expiration)

			invoices = db( db.invoices.user==request.args(0)).select(db.invoices.ALL,
																	db.orders.id,
																	db.orders.status,
																	left=[  db.orders.on(db.orders.invoice==db.invoices.id)],
																	orderby=~db.invoices.id,
																	groupby=db.orders.id
																	)
			

			budgets = db((db.budgets.user==request.args(0)) & (db.budgets.status!="Creando")).select(db.budgets.ALL, orderby=~db.budgets.id)

			orders= db((db.orders.invoice==None) & (db.orders.user==request.args(0))).select(orderby=~db.orders.id)

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

				form = SQLFORM.factory(first_name, last_name, email, tax_identification, fiscalname, address, city, province, country, postalcode, phone, submit_button = 'enviar datos', formstyle='bootstrap3_inline')



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
					response.flash="Datos enviados correctamente"
				elif form.errors:
					response.flash = 'Hay errores'

				
				form.element('input[name=city]')['_class']='form-control'
				form.element('input[name=province]')['_class']='form-control'


				creditaccount=db(db.creditaccounts.user==customer.auth_user.id).select().first()
				accountingentries=None

				if creditaccount:
					accountingentries = db(	(db.accountingentries.creditaccount==creditaccount.id) &
											(db.accountingentries.active==True) ).select(	db.accountingentries.ALL, 
																							db.orders.ALL,
																							db.invoices.ALL,
																							db.products.name,
																							join=[	db.orderlist.on(db.accountingentries.orderlist==db.orderlist.id),
																									db.products.on(db.products.id==db.orderlist.product),
																									db.orders.on(db.orders.id==db.orderlist.g_order),
																									db.invoices.on(db.invoices.id==db.orders.invoice)],
																							orderby=~db.accountingentries.id)




				return dict(form=form, contractedproducts=contractedproducts, invoices=invoices, budgets=budgets, orders=orders, userid=customer.auth_user.id, accountingentries=accountingentries, creditaccount=creditaccount)

			else:
				redirect(URL('administrator','newcustomer'))
		else:
			redirect(URL('administrator','users'))


	else:
		redirect(URL(request.application,'default','user/login'))


@auth.requires_login()
@page_allowed_ip
def billing():
	
	if auth.has_membership('administradores') or auth.has_membership('superadministradores'):
		from invoices import Fiscal, Invoice,Order
		from pagination import Pagination
		Fiscal(db), Invoice(db), Order(db)
		settings = db(db.adminsettings.id>0).select(db.adminsettings.ALL).first()
		count=db.invoices.id.count()
		records=db((db.invoices.id>0)).select(count,
											left=[	db.auth_user.on(db.auth_user.id==db.invoices.user),
													db.fiscals.on(db.fiscals.user==db.auth_user.id)],
											orderby=~db.invoices.id).first()
		items_per_page=settings.invoiceitems
		pag=Pagination(int(records[count]), items_per_page)
		invoices= db((db.invoices.id>0)).select(db.orders.status,
												db.orders.invoice,
												db.invoices.ALL, 
												db.auth_user.id,
												db.auth_user.first_name,
												db.auth_user.last_name,  
												db.fiscals.fiscalname,

												left=[	db.orders.on(db.orders.invoice==db.invoices.id),
														db.auth_user.on(db.auth_user.id==db.invoices.user),
														db.fiscals.on(db.fiscals.user==db.auth_user.id),
														],
												orderby=~db.invoices.id,
												limitby=pag.limitby())
		
		total=0
		totaltaxes=0
		for invoice in db(db.invoices.created_at>=datetime.date(datetime.datetime.today().year,1,1)).select():
			total=total+ invoice.total
			totaltaxes= totaltaxes + invoice.taxes

		return dict(invoices=invoices, pagination=pag, records=records[count], items_per_page=items_per_page, total=total, totaltaxes=totaltaxes)

	else:
		redirect(URL(request.application,'default','user/login'))

@auth.requires_login()
@page_allowed_ip
def viewinvoice():

	if auth.has_membership('administradores') or auth.has_membership('superadministradores'):
		from invoices import Invoice, Order, Orderlist, Budget, AccountingEntry, CreditAccount
		Invoice(db), Order(db), Orderlist(db), Budget(db), AccountingEntry(db), CreditAccount(db)
		invoice= db(db.invoices.id==request.args(0)).select(db.invoices.ALL, 
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
	else:
		redirect(URL(request.application,'default','user/login'))


@auth.requires_login()
@page_allowed_ip
def delete_accountingentry():
	if auth.has_membership('administradores') or auth.has_membership('superadministradores'):
		from invoices import Orderlist, AccountingEntry, CreditAccount
		Orderlist(db), AccountingEntry(db), CreditAccount(db)
		#comprobar que el AccountingEntry que se va a borrar es correcto
		try:
			accountingentry=db.accountingentries(request.vars.accountingentries)
			creditaccount=db.creditaccounts(accountingentry.creditaccount)
			balance=None
			if creditaccount.user==int(request.vars.customer):
				#buscar el primer accountingentry con ese orderlist y a partir de ese, la lista de accountingsentry con ese user hasta el final.
				accountingentries=db(db.accountingentries.id>=db((db.accountingentries.orderlist==accountingentry.orderlist) & (db.accountingentries.active==True)).select().first()['id']).select()
				#recorrer la lista
				for ae in accountingentries:
					#si coincide orderlist, quedarse con total*(-1), desactivar accountingentry
					if ae.orderlist==accountingentry.orderlist:
						if float(ae.total)>=0:
							total=float(ae.total)*(-1)
						else:
							total=0
						#desactivar 
						db(db.accountingentries.id==ae.id).update(active=False, deactivated_by=auth.user_id, deactivated_at=datetime.datetime.now())

					#si no, sumarr a balance el total*(-1)	
					else:			
						aentry=db.accountingentries(ae.id)

						balance=float(aentry.balance)+total
						logger.debug("%s %s %s  %s + %s = %s" % (aentry.id, total, aentry.balance,  aentry.balance, total, balance))

						aentry.update_record(balance=balance)
				#modificar balance de CreditAccount
				if balance!=None:
					db(db.creditaccounts.id==accountingentry.creditaccount).update(balance=balance)
				db.commit()
				return "ok"
			else:
				return "fail"
		except Exception as ex:
			db.rollback()
			logger.debug("Error delete_accountingentry %s" % ex)
			raise HTTP(500, ex)
	else:
		return "fail"