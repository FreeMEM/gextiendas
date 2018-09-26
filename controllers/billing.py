# coding: utf8

@auth.requires_login()
def printinvoice(): 
	import os, uuid, subprocess
	import gluon.contenttype, gluon.globals
	from appy.pod.renderer import Renderer 
	from invoices import Invoice, Order, Orderlist, Product
	from adminsettings import Adminsettings
	Adminsettings(db), Invoice(db), Order(db), Orderlist(db), Product(db)
	settings = db(db.adminsettings.id>0).select(db.adminsettings.ALL).first()
	if auth.has_membership('superadministradores') or auth.has_membership('administradores'):

		invoice= db(db.invoices.id==request.args(0)).select(db.invoices.ALL, 
															db.auth_user.id,
															db.auth_user.first_name,
															db.auth_user.last_name,  
															db.auth_user.email,
															db.fiscals.ALL,
															left=[	db.auth_user.on(db.auth_user.id==db.invoices.user),
																	db.fiscals.on(db.fiscals.user==db.auth_user.id)]).first()
	else:

		invoice= db((db.invoices.id==request.args(0)) & (db.invoices.user==auth.user_id)).select(db.invoices.ALL, 
															db.auth_user.id,
															db.auth_user.first_name,
															db.auth_user.last_name,
															db.auth_user.email,
															db.fiscals.ALL,
															left=[	db.auth_user.on(db.auth_user.id==db.invoices.user),
																	db.fiscals.on(db.fiscals.user==db.auth_user.id)]).first()
	if invoice:
		invoicenumber="%s"%invoice.invoices.invoice_number
		invoicedate="%s" % invoice.invoices.created_at.strftime("%d-%m-%Y")
		customernumber= "%s" % invoice.auth_user.email
		customernif= "%s" % invoice.fiscals.tax_identification
		nombre="%s" % ("%s %s" % (invoice.auth_user.first_name, invoice.auth_user.last_name),invoice.fiscals.fiscalname)[invoice.fiscals.fiscalname!=""]
		domicilio="%s" % invoice.fiscals.address
		domicilio2="%s %s %s" % (invoice.fiscals.postal_code, invoice.fiscals.city, invoice.fiscals.province) 
		telefono="%s" % invoice.fiscals.country
		fax="%s" % invoice.fiscals.phone
		subtotal="%.2f"% float(invoice.invoices.subtotal)
		totaldto="%.2f" % float(invoice.invoices.discount)
		totaliva="%.2f" % float(invoice.invoices.taxes)
		total="%.2f"% float(invoice.invoices.subtotal)
		totalinvoice="%.2f"% float(invoice.invoices.total)
		iva="%.2f" % float(invoice.invoices.tax)
		totaliva="%.2f" % float(invoice.invoices.taxes)
		items = []
		subtotal_no_dto = 0
		for item in db(db.orders.invoice==invoice.invoices.id).select(	db.orders.ALL, 
																		db.orderlist.ALL,
																		db.products.ALL,
																		left=[	db.orderlist.on(db.orderlist.g_order==db.orders.id),
																				db.products.on(db.products.id==db.orderlist.product)]):

			tax_result="%.2f" % (((float(item.orderlist.price)* (float(item.orderlist.quantity) ))* float(item.orderlist.tax))/float(100))
			

			subtotal_no_dto += item.orderlist.price * item.orderlist.quantity
			items.append(dict(	id="%s" % item.products.id,
								name="%s"%item.products.name,
								cant="%s" % item.orderlist.quantity,
								price="%.2f"%float(item.orderlist.price),
								percent="%.2f" % float(item.orderlist.tax), #se refiere al iva, pero en el .odt puse este nombre de variable por una ida de olla.
								dto="%.2f"%float(item.orderlist.dto_percentage)+"%",
								total="%.2f" % (float(item.orderlist.quantity) * float(item.orderlist.price))
								)
						)
		
			
		try:

			# Report creation               
			template_file = os.path.join(request.folder, 'private', 'factura.odt')
			# tmp_uuid = uuid.uuid4()
			output_file_odt = os.path.join(request.folder, 'private', 'tmp','%s_%s.odt' % ("factura",invoice.invoices.id ))
			output_file_pdf = os.path.join(request.folder, 'private', 'tmp','%s_%s.pdf' % ("factura",invoice.invoices.id ))
			
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
			response.headers['Content-Disposition'] = 'attachment; filename=%s_%s.pdf' % ("factura",invoice.invoices.invoice_number )
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
	session.flash= 'No se pudo encontrar la factura, inténtelo de nuevo'
	if auth.has_membership('superadministradores') or auth.has_membership('administradores'):
		redirect(URL(request.application, 'administrator', 'viewinvoice', args=request.args(0)))
	else:
		redirect(URL(request.application, 'account', 'billing', args=request.args(0)))



@auth.requires_login()
@page_allowed_ip
def newinvoice(): 
	from invoices import Invoice, Order, Orderlist, Budget, Budgetlist
	from shops import Product
	from adminsettings import Adminsettings
	Adminsettings(db), Invoice(db), Order(db), Orderlist(db), Product(db), Budget(db), Budgetlist(db)
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
												payment_method='Transferencia',
												tax=settings.tax,
												manual_operation=True)
					for row in db(db.budgetlist.g_budget==request.vars.budget).select():
						db.orderlist.insert(product=row.product,
											g_order=orderid,
											quantity=row.quantity,
											price=row.price,
											price_wdto=row.price_wdto,
											tax=row.tax,
											dto=row.dto,
											dto_percentage=row.dto_percentage)
					db.commit()
				else:
					orderid=order.id
			elif request.vars.order:
				order=db(	(db.orders.user==request.args(0)) & 
							(db.orders.id==request.vars.order)).select().first()
				if order:
					orderid=order.id
				else:
					response.flash="Error"

			else:
				order=db(	(db.orders.user==request.args(0)) & 
							(db.orders.status=="CreandoAdmin") & 
							(db.orders.budget==None)).select().first()

				if not order:
					orderid=db.orders.insert(	status="CreandoAdmin", 
												user=request.args(0),
												tax=settings.tax, 
												payment_method='Transferencia',
												manual_operation=True)
					db.commit()
				else:
					orderid=order.id	
				

			customer=db(db.auth_user.id==request.args(0)).select(	db.auth_user.id,
																		db.auth_user.first_name,
																		db.auth_user.last_name,
																		db.auth_user.email,
																		db.fiscals.ALL,
																		left=[db.fiscals.on(db.fiscals.user==db.auth_user.id)]).first()

			paymentmethod=db.orders(orderid).payment_method

			return dict(products=products, customer=customer, tax=settings.tax, paymentmethod=paymentmethod)
		else:
			redirect(URL(request.application, 'administrator','users'))
	else:
		redirect(URL(request.application,'default','user/login'))



@auth.requires_login()
@page_allowed_ip
def cancelinvoice(): 
	from invoices import Order
	Order(db)
	if auth.has_membership('superadministradores') or auth.has_membership('administradores'):
		try:
			if request.vars.budget!='None' and request.vars.budget!=None:
				db((db.orders.user==request.vars.customer) & (db.orders.status=="CreandoAdmin") & (db.orders.budget==request.vars.budget)).delete()
			else:
				db(	(db.orders.user==request.vars.customer) & (db.orders.status=="CreandoAdmin")).delete()
			
		except Exception as ex:
			logger.debug("Ocurrió un error al borrar una orden de pedido desde billing: %s" % ex)
			response.flash="Ocurrió un error: %s" % ex

		redirect(URL(request.application, 'administrator','editcustomer', args=request.vars.customer))
		return dict()


@auth.requires_login()
@page_allowed_ip
def confirminvoice(): 
	from invoices import Order, Invoice, Orderlist, CreditAccount, AccountingEntry
	from adminsettings import Adminsettings
	Adminsettings(db), Order(db), Invoice(db), Orderlist(db)
	accounting=AccountingEntry(db)
	from auxiliartools import AuxiliarTools	
	external=AuxiliarTools(db)
	settings = db(db.adminsettings.id>0).select(db.adminsettings.ALL).first()
	if auth.has_membership('superadministradores') or auth.has_membership('administradores'):
		try:	
			if request.vars.budget!='None' and request.vars.budget!=None:
				order= db((db.orders.user==request.vars.customer) & (db.orders.budget==request.vars.budget)).select().first()
			elif request.vars.order!='None' and request.vars.order!=None:
				order= db((db.orders.user==request.vars.customer) & (db.orders.id==request.vars.order)).select().first()
			else:
				order= db((db.orders.user==request.vars.customer) & (db.orders.status=="CreandoAdmin")).select().first()
			if not order.invoice:
					

				total=float(0)
				totaltax=float(0)
				orderlist=db(db.orderlist.g_order==order.id).select()
				fail=True
				if orderlist:
					fail=False
					for row in orderlist:
						total=total + (float(row.quantity) * float(row.price))

						totaltax=(total*float(settings.tax))/100
					if request.vars.paid=='False':
						status="Pendiente pago"
					else:
						status="Pagado"
					payment_code=None
					if order.payment_method=="Transferencia":
						payment_code=db.paymentcodes.insert(code=external.generatecode())


					db(db.orders.id==order.id).update(	total="%.2f"%total,
														totaltax="%.2f"%totaltax,
														status=status,
														payment_code=payment_code,
														confirmed_at=datetime.datetime.now(),
														confirmed_ip=request.client,
														confirmed_by=auth.user_id)

					if request.vars.paid!='False':
						invoiceid=Invoice(db).makeinvoice(order.id, None, True) #Factura pagada
					elif request.vars.paid=='False':
						invoiceid=Invoice(db).makeinvoice(order.id, "Pendiente pago", True) #Pendiente de pago 
					if request.vars.budget!='None' and request.vars.budget!=None:
						db(db.budgets.id==request.vars.budget).update(invoice=invoiceid)
					db.commit()

					# Al ser una factura manual, hay que buscar si hay contratos esperando de ser tratados tras el pago
					# buscar los contratos que pertenezcan a cada uno de los orderlist y si no están ya en accountingentries
					# hacer las anotaciones que se tengan que hacer si credit_annotation==True
					for row in orderlist:
						contract=db(db.contractedproducts.orderlist==row.id).select().first()
						if contract:
							#anotar crédito si orders pagado y si credit_annotation==True y si not in accountingentries
							if contract.credit_annotation==True:
								if not db(	(db.accountingentries.orderlist==row.id) &
											(db.accountingentries.active==True)).select().first():
									if not accounting.annotation(row, order, positive=True):
										raise Exception('Ocurrió un error al hacer la anotación en billing.confirminvoice')



				else:
					redirect(URL(request.application, 'administrator', 'viewinvoice', args=invoiceid))
					return dict()

		except Exception as ex:
			db.rollback()
			logger.debug("Ocurrió un error al generar la factura %s" % ex)
			session.flash="Se produjo un error al generar la factura: %s" %ex
			redirect(URL('billing','newinvoice',args=auth.user_id))
			return dict()
		if fail:
			redirect(URL(request.application, 'administrator', 'editcustomer', args=request.vars.customer))
			return dict()
		else:
			redirect(URL(request.application, 'administrator', 'viewinvoice', args=invoiceid))
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
		from invoices import Invoice, Order, Orderlist
		from shops import Product
		from adminsettings import Adminsettings
		from auxiliartools import AuxiliarTools	
		external=AuxiliarTools(db)
		Adminsettings(db), Invoice(db), Order(db), Orderlist(db), Product(db)
		settings = db(db.adminsettings.id>0).select(db.adminsettings.ALL).first()
		#entrada: data: { 'product': int, 'quantity': int, 'rate': int, 'operation': ['add','del','set'] }
		#salida: (json)sales
		#begin
		#comprobar si tiene un order abierta y si no crearla
		if request.vars.budget!='None' and request.vars.budget!=None:
			order=db(	(db.orders.user==request.vars.customer) & 
						(db.orders.status=="CreandoAdmin") &
						(db.orders.budget==request.vars.budget)).select().first()

		else:
			order=db(	(db.orders.user==request.vars.customer) & 
						(db.orders.status=="CreandoAdmin")).select().first()

		if not order and request.vars.operation=="add":
			orderid=db.orders.insert(status="CreandoAdmin", 
									user=request.vars.customer, 
									payment_method='Transferencia', 
									tax=settings.tax,
									budget=(None,request.vars.budget)[request.vars.budget!='None'],
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
		if request.vars.budget!='None' and request.vars.budget!=None:
			order=db(	(db.orders.user==request.vars.customer) & 
						(db.orders.status=="CreandoAdmin") &
						(db.orders.budget==request.vars.budget)).select().first()

		else:
			order=db(	(db.orders.user==request.vars.customer) & 
						(db.orders.status=="CreandoAdmin")).select().first()
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
		from auxiliartools import AuxiliarTools	
		external=AuxiliarTools(db)
		Adminsettings(db), Invoice(db), Order(db), Orderlist(db), Product(db)
		settings = db(db.adminsettings.id>0).select(db.adminsettings.ALL).first()
		#entrada: data: { 'product': int, 'quantity': int, 'rate': int, 'operation': ['add','del','set'] }
		#salida: (json)sales
		#begin
		#comprobar si tiene un order abierta y si no crearla

		if request.vars.budget!='None' and request.vars.budget!=None:

			order=db(	(db.orders.user==request.vars.customer) & 
						(db.orders.status=="CreandoAdmin") &
						(db.orders.budget==request.vars.budget)).select().first()
		elif request.vars.order!='None' and request.vars.order!=None:
			order=db(	(db.orders.user==request.vars.customer) & 
						(db.orders.id==request.vars.order)).select().first()

		else:
			
			order=db(	(db.orders.user==request.vars.customer) & 
						(db.orders.status=="CreandoAdmin")).select().first()
			
		try:
			if not order:
				orderid=db.orders.insert(status="CreandoAdmin", 
										user=request.vars.customer, 
										payment_method='Domiciliación',
										tax=settings.tax,
										budget=(None,request.vars.budget)[request.vars.budget!='None'],
										manual_operation=True)
				order=db.orders(orderid).first()
			
			orderlist = db((db.orderlist.g_order==order.id)).select(	db.orderlist.ALL, 
																db.products.name, 
																db.products.id,
																join=[db.products.on(db.products.id==db.orderlist.product)]).as_list()
			
			return orderlist

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
			if request.vars.budget!='None' and request.vars.budget!=None:
				db(	(db.orders.user==request.vars.customer) & 
					(db.orders.status=="CreandoAdmin") &
					(db.orders.budget==request.vars.budget)).update(payment_method=request.vars.paymentmethod)
			else:
				db(	(db.orders.user==request.vars.customer) & 
					(db.orders.status=="CreandoAdmin")).update(payment_method=request.vars.paymentmethod)
			db.commit()
			return dict(callback="OK")
		except Exception as ex:
			db.rollback()
			logger.debug("Ocurrió un error al modificar el método de pago %s" % ex)
			return dict(callback="Fail")




@auth.requires_login()
@service_allowed_ip
@service.json
def newcontract():
	return dict()