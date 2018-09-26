# coding: utf8
@auth.requires_login()
@page_allowed_ip
def printorder(): 
	import os, uuid, subprocess
	import gluon.contenttype, gluon.globals
	from appy.pod.renderer import Renderer 
	from invoices import Order, Orderlist
	from shops import Product
	from adminsettings import Adminsettings
	Adminsettings(db), Order(db), Orderlist(db), Product(db)
	settings = db(db.adminsettings.id>0).select(db.adminsettings.ALL).first()
	if auth.has_membership('superadministradores') or auth.has_membership('administradores'):

		order= db(db.orders.id==request.args(0)).select(db.orders.ALL, 
															db.auth_user.id,
															db.auth_user.first_name,
															db.auth_user.last_name,  
															db.auth_user.email,
															db.fiscals.ALL,
															left=[	db.auth_user.on(db.auth_user.id==db.orders.user),
																	db.fiscals.on(db.fiscals.user==db.auth_user.id)]).first()
		if order:
			ordernumber="%s"%order.orders.id
			orderdate="%s" % order.orders.ordered_at.strftime("%d-%m-%Y")
			customernumber= "%s" % order.auth_user.email
			customernif= "%s" % ("",order.fiscals.tax_identification)[order.fiscals.tax_identification!=None]
			nombre="%s" % ("%s %s" % (order.auth_user.first_name, order.auth_user.last_name),order.fiscals.fiscalname)[order.fiscals.fiscalname!=""]
			domicilio="%s" % ("",order.fiscals.address)[order.fiscals.address!=None]
			domicilio2="%s %s %s" % (("", order.fiscals.postal_code)[order.fiscals.postal_code!=None], ("", order.fiscals.city)[order.fiscals.city!=None], ("",order.fiscals.province)[order.fiscals.province!=None]) 
			telefono="%s" % order.fiscals.country
			fax="%s" % order.fiscals.phone
			
			iva="%.2f" % order.orders.tax
			totaliva="%.2f" % float(order.orders.totaltax)
			total="%.2f" % float(order.orders.total)
			totalorder="%.2f"% float(float(order.orders.total)+ float(order.orders.totaltax))  

			items = []

			for item in db(db.orderlist.g_order==order.orders.id).select(db.orderlist.ALL,
																			db.products.ALL,
																			left=[db.products.on(db.products.id==db.orderlist.product)]):

				tax_result="%.2f" % (((float(item.orderlist.price)* (float(item.orderlist.quantity) ))* float(item.orderlist.tax))/float(100))
				

				items.append(dict(	id="%s" % item.products.id,
									name="%s"%item.products.name,
									cant="%s" % item.orderlist.quantity,
									price="%.2f"%float(item.orderlist.price),
									percent="%.2f" % float(item.orderlist.tax), #se refiere al iva, pero en el .odt puse este nombre de variable por una ida de olla.
									total="%.2f" % (float(item.orderlist.quantity) * float(item.orderlist.price))
									)
							)
			
				
			try:

				# Report creation               
				template_file = os.path.join(request.folder, 'private', 'order.odt')
				# tmp_uuid = uuid.uuid4()
				output_file_odt = os.path.join(request.folder, 'private', 'tmp','%s_%s.odt' % ("pedido",order.orders.id ))
				output_file_pdf = os.path.join(request.folder, 'private', 'tmp','%s_%s.pdf' % ("pedido",order.orders.id ))
				
				#por si existiese de vez anterior
				for filepath in [output_file_odt, output_file_pdf]:
					if os.path.exists(filepath):
						os.remove(filepath)


				renderer = Renderer(template_file, locals(), output_file_odt)

				renderer.run()
				
				command= "unoconv --format pdf --output %s %s"%(os.path.join(request.folder, 'private', 'tmp'),output_file_odt )
				process = subprocess.Popen(command, shell=True)
				processcode = process.wait()

				response.headers['Content-Length'] = '%s'%os.path.getsize(output_file_pdf)
				response.headers['Content-Type'] = '%s' % gluon.contenttype.contenttype('.pdf')
				response.headers['Content-Disposition'] = 'attachment; filename=%s_%s.pdf' % ("pedido",order.orders.id )
				stream = open(output_file_pdf, 'rb')
				for filepath in [output_file_odt, output_file_pdf]:
					if os.path.exists(filepath):
						os.remove(filepath)
				return stream
				# response.stream(output_file_pdf, chunk_size=4096)
			
			except Exception as ex:

				for filepath in [output_file_odt, output_file_pdf]:
					if os.path.exists(filepath):
						os.remove(filepath)
				logger.debug("Error general al generar PDF: %s " % ex)
				pass
			except IOError, e: # Explicitly ignore IOError if it occurs.

				for filepath in [output_file_odt, output_file_pdf]:
					if os.path.exists(filepath):
						os.remove(filepath)
				logger.debug("Error IOerror al generar PDF: %s" % e)
				pass
		session.flash= 'No se pudo encontrar el pedido, inténtelo de nuevo'
		if auth.has_membership('superadministradores') or auth.has_membership('administradores'):
			redirect(URL(request.application, 'administrator', 'viewinvoice', args=request.args(0)))
		else:
			redirect(URL(request.application, 'account', 'billing', args=request.args(0)))
	else:
		redirect(URL(request.application, 'user','login'))


@auth.requires_login()
@page_allowed_ip
def neworder(): 
	
	from shops import Product
	from invoices import Fiscal, Order, Orderlist, Budgetlist
	from adminsettings import Adminsettings
	Adminsettings(db), Product(db), Fiscal(db), Order(db), Orderlist(db), Budgetlist(db)
	settings = db(db.adminsettings.id>0).select(db.adminsettings.ALL).first()

	if auth.has_membership('superadministradores') or auth.has_membership('administradores'):
		if request.args(0):
			products=db( db.products.active==True ).select()
			if request.vars.budget:
				order=db(	(db.orders.user==request.args(0)) & 
							(db.orders.status=="CreandoAdmin") &
							(db.orders.budget==request.vars.budget)).select().first()
				if not order:
					orderid=db.orders.insert(	status="CreandoAdmin", 
												user=request.args(0),
												budget=request.vars.budget,
												tax=settings.tax,
												payment_method='Transferencia',
												manual_operation=True
												)
					order=db.orders(orderid)
					for row in db(db.budgetlist.g_budget==request.vars.budget).select():
						db.orderlist.insert(product=row.product,
											g_order=orderid,
											quantity=row.quantity,
											price=row.price,
											price_wdto=row.price_wdto,
											tax=row.tax,
											dto=row.dto,
											dto_percentage=row.dto_percentage)


			else:

				if request.args(1):
					order=db( (db.orders.user==request.args(0)) &
								(db.orders.id==request.args(1))).select().first()
				else:
					order=db(	(db.orders.user==request.args(0)) & 
								(db.orders.status=="CreandoAdmin")).select().first()


				if not order:
					orderid=db.orders.insert(	status="CreandoAdmin",
										tax=settings.tax,
										user=request.args(0),
										payment_method='Transferencia',
										manual_operation=True)
					order=db.orders(orderid)
			
			
			customer=db(db.auth_user.id==request.args(0)).select(	db.auth_user.id,
																	db.auth_user.first_name,
																	db.auth_user.last_name,
																	db.auth_user.email,
																	db.fiscals.ALL,
																	left=[db.fiscals.on(db.fiscals.user==db.auth_user.id)]).first()

			db.commit()

			return dict(products=products, customer=customer, tax=order.tax, order=order)
		else:
			redirect(URL(request.application, 'administrator','users'))
	else:
		redirect(URL(request.application,'default','user/login'))


@auth.requires_login()
@page_allowed_ip
def cancelorder(): 
	from invoices import Order
	Order(db)
	if auth.has_membership('superadministradores') or auth.has_membership('administradores'):
		try:
			db(	(db.orders.user==request.vars.customer) & (db.orders.id==request.vars.orderid)).delete()
			
		except Exception as ex:
			logger.debug("OCurrió un error al borrar una orden de pedido desde billing: %s" % ex)
			response.flash="Ocurrió un error: %s" % ex

		redirect(URL(request.application, 'administrator','editcustomer', args=request.vars.customer))
		return dict()


@auth.requires_login()
@page_allowed_ip
def confirmorder(): 
	from invoices import Order, Orderlist
	from adminsettings import Adminsettings
	Adminsettings(db), Order(db), Orderlist(db)
	settings = db(db.adminsettings.id>0).select(db.adminsettings.ALL).first()
	if auth.has_membership('superadministradores') or auth.has_membership('administradores'):
		try:
			order= db((db.orders.user==request.vars.customer) & (db.orders.id==request.vars.orderid)).select().first()
			
			total=float(0)
			totaltax=float(0)
			orderlist=db(db.orderlist.g_order==order.id).select()
			
			if orderlist:
				for row in orderlist:
					total=total + (float(row.quantity) * float(row.price))

				totaltax=(total*float(settings.tax))/100
				if request.args(0)=="onlycreate":
					db(db.orders.id==order.id).update(	total="%.2f"%total,
														totaltax="%.2f"%totaltax,
														status="Pendiente pago")

				else:
					db(db.orders.id==order.id).update(	total="%.2f"%total,
														totaltax="%.2f"%totaltax,
														status="Pendiente pago",
														confirmed_at=datetime.datetime.now(),
														confirmed_by=auth_user)


				db.commit()

		except Exception as ex:
			db.rollback()
			logger.debug("Ocurrió un error al generar la factura %s" % ex)
			session.flash="Se produjo un error al generar la factura: %s" %ex
			redirect(URL('order','neworder',args=order.id))

		redirect(URL(request.application, 'orders', 'vieworder', args=order.id))
		return dict()


@auth.requires_login()
@page_allowed_ip
def call():
	return service()


@auth.requires_login()
@service_allowed_ip
@service.json
def item():
	if auth.has_membership('superadministradores') or auth.has_membership('administradores'):
		
		from shops import Product
		from invoices import Order, Orderlist
		from adminsettings import Adminsettings
		Adminsettings(db), Order(db), Orderlist(db), Product(db)
		settings = db(db.adminsettings.id>0).select(db.adminsettings.ALL).first()
		#entrada: data: { 'product': int, 'quantity': int, 'rate': int, 'operation': ['add','del','set'] }
		#salida: (json)sales
		#begin
		#comprobar si tiene un order abierta y si no crearla
		if request.vars.orderid:
			order =db(	(db.orders.user==request.vars.customer) & 
						(db.orders.id==request.vars.orderid)).select().first()
		else:
			order=db(	(db.orders.user==request.vars.customer) & 
					(db.orders.status=="CreandoAdmin")).select().first()
		if not order and request.vars.operation=="add":
			orderid=db.orders.insert(status="CreandoAdmin", 
									user=request.vars.customer, 
									payment_method='Transferencia',
									tax=settings.tax,
									manual_operation=True)
			order=db.orders(orderid)
		
		orderlist_id=None
		try:	
			#add/del product y quantity.
			row=db((db.orderlist.product==request.vars.product) & (db.orderlist.g_order==order.id)).select().first()

			if row:
				orderlist_id=row.id

				if request.vars.operation=="add":
					db(db.orderlist.id==orderlist_id).update(quantity=int(row.quantity)+int(request.vars.quantity))

				elif request.vars.operation=="set":

					db(db.orderlist.id==orderlist_id).update(quantity=int(request.vars.quantity))
				db.commit()
			else:
				product=db(db.products.id==request.vars.product).select().first()
				#valor iva, para conservar el valor en caso de variar en el futuro
				#el precio para conservar en caso de variar en el futuro.
				orderlist_id= db.orderlist.insert(	product=request.vars.product, 
													g_order=order.id, 
													quantity=request.vars.quantity, 
													price=product.price, 
													price_wdto=product.price,
													tax="%.2f" % settings.tax)
				db.commit()

				
		except Exception as ex:
			logger.debug("ALGO SALIO MAL en item %s" % ex)
			db.rollback()
		#retorna json del pedido
		
		data = db((db.orderlist.g_order==order.id)).select(db.orderlist.ALL, db.products.name, join=[db.products.on(db.products.id==db.orderlist.product)]).as_list()
		return data
	else:
		return dict()



@auth.requires_login()
@auth.requires(auth.has_membership('superadministradores') or auth.has_membership('administradores') or auth.has_membership('directores') or auth.has_membership('gerente') or auth.has_membership('responsables'))
@service.json
def delitem():
	if auth.has_membership('superadministradores') or auth.has_membership('administradores'):
		from invoices import Invoice, Order, Orderlist
		from shops import Product
		from adminsettings import Adminsettings
		Adminsettings(db), Invoice(db), Order(db), Orderlist(db), Product(db)
		settings = db(db.adminsettings.id>0).select(db.adminsettings.ALL).first()

		order=db(	(db.orders.user==request.vars.customer) & 
					(db.orders.id==request.vars.orderid)).select().first()
		try:
			db((db.orderlist.id==request.vars.id) & (db.orderlist.g_order==order.id)).delete()
			db.commit()
		except:
			db.rollback()
		
		return db((db.orderlist.g_order==order.id)).select(	db.orderlist.ALL, 
															db.products.name, 
															db.products.id,
															join=[db.products.on(db.products.id==db.orderlist.product)]).as_list()
	else:
		return dict()



@auth.requires_login()
@service_allowed_ip
@service.json
def items():
	if auth.has_membership('superadministradores') or auth.has_membership('administradores'):
		from invoices import Invoice, Order, Orderlist
		from shops import Product
		from adminsettings import Adminsettings
		Adminsettings(db), Invoice(db), Order(db), Orderlist(db), Product(db)
		settings = db(db.adminsettings.id>0).select(db.adminsettings.ALL).first()
		#entrada: data: { 'product': int, 'quantity': int, 'rate': int, 'operation': ['add','del','set'] }
		#salida: (json)sales
		#begin
		#comprobar si tiene un order abierta y si no crearla
		order=db(	(db.orders.user==request.vars.customer) & 
					(db.orders.id==request.vars.orderid)).select().first()

		try:
			if not order:
				orderid=db.orders.insert(status="CreandoAdmin", 
										user=request.vars.customer, 
										payment_method='Transferencia',
										tax=settings.tax,
										manual_operation=True)
				order=db.orders(orderid)
			
			return db((db.orderlist.g_order==order.id)).select(	db.orderlist.ALL, 
																db.products.name, 
																db.products.id,
																join=[db.products.on(db.products.id==db.orderlist.product)]).as_list()
			 
		except Exception as ex:
			logger.debug(ex)
			db.rollback()
	else:
		return dict()


@auth.requires_login()
@service_allowed_ip
@service.json
def updating_paymethod():
	if auth.has_membership('superadministradores') or auth.has_membership('administradores'):
		from invoices import Order
		Order(db)
		try:
			db(	(db.orders.user==request.vars.customer) & 
				(db.orders.id==request.vars.orderid)).update(payment_method=request.vars.paymentmethod)
			db.commit()
			return dict(callback="OK")
		except Exception as ex:
			db.rollback()
			logger.debug("Ocurrió un error al modificar el método de pago %s" % ex)
			return dict(callback="Fail")


@auth.requires_login()
@page_allowed_ip
def vieworder():
	if auth.has_membership('administradores') or auth.has_membership('superadministradores'):
		from invoices import Order, Orderlist
		from shops import Product
		Order(db), Orderlist(db), Product(db)
		order= db(db.orders.id==request.args(0)).select(db.orders.ALL, 
															db.auth_user.id,
															db.auth_user.first_name,
															db.auth_user.last_name,  
															db.fiscals.ALL,
															left=[	db.auth_user.on(db.auth_user.id==db.orders.user),
																	db.fiscals.on(db.fiscals.user==db.auth_user.id)]).first()


		if order:
			orderlist= db(db.orderlist.g_order==order.orders.id).select(db.orderlist.ALL,
																		db.products.ALL,
																		left=[	db.products.on(db.products.id==db.orderlist.product)])

			return dict(order=order, orderlist=orderlist)
		else:
			redirect(URL(request.application, 'administrator','users'))			
	else:
		redirect(URL(request.application,'default','user/login'))


@auth.requires_login()
@page_allowed_ip
def confirm_payment():
	if auth.has_membership('administradores') or auth.has_membership('superadministradores'):
		from invoices import Order
		Order(db)
		db((db.orders.invoice==request.vars.invoice) & (db.orders.user==request.args(0))).update(status="Pagado")
		db.commit()
		session.flash="La factura se ha marcado como pagada"
		redirect(URL('administrator','viewinvoice', args=[request.vars.invoice]))
		return dict()
	else:
		redirect(URL(request.application,'default','user/login'))
