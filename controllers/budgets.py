# coding: utf8
@auth.requires_login()
@page_allowed_ip
def printbudget(): 
	import os, uuid, subprocess
	import gluon.contenttype, gluon.globals
	from appy.pod.renderer import Renderer 
	from invoices import Budget, Budgetlist
	from shops import Product
	from adminsettings import Adminsettings
	Adminsettings(db), Budget(db), Budgetlist(db), Product(db)
	settings = db(db.adminsettings.id>0).select(db.adminsettings.ALL).first()
	if auth.has_membership('superadministradores') or auth.has_membership('administradores'):

		budget= db(db.budgets.id==request.args(0)).select(db.budgets.ALL, 
															db.auth_user.id,
															db.auth_user.first_name,
															db.auth_user.last_name,  
															db.auth_user.email,
															db.fiscals.ALL,
															left=[	db.auth_user.on(db.auth_user.id==db.budgets.user),
																	db.fiscals.on(db.fiscals.user==db.auth_user.id)]).first()
		if budget:
			budgetnumber="%s"%budget.budgets.id
			budgetdate="%s" % budget.budgets.created_at.strftime("%d-%m-%Y")
			customernumber= "%s" % budget.auth_user.email
			customernif= "%s" % ("",budget.fiscals.tax_identification)[budget.fiscals.tax_identification!=None]
			nombre="%s" % ("%s %s" % (budget.auth_user.first_name, budget.auth_user.last_name),budget.fiscals.fiscalname)[budget.fiscals.fiscalname!=""]
			domicilio="%s" % ("",budget.fiscals.address)[budget.fiscals.address!=None]
			domicilio2="%s %s %s" % (("", budget.fiscals.postal_code)[budget.fiscals.postal_code!=None], ("", budget.fiscals.city)[budget.fiscals.city!=None], ("",budget.fiscals.province)[budget.fiscals.province!=None]) 
			telefono="%s" % budget.fiscals.country
			fax="%s" % budget.fiscals.phone
			
			iva="%.2f" % budget.budgets.tax
			totaliva="%.2f" % float(budget.budgets.totaltax)
			total="%.2f" % float(budget.budgets.total)
			totalbudget="%.2f"% float(float(budget.budgets.total)+ float(budget.budgets.totaltax))  

			items = []

			for item in db(db.budgetlist.g_budget==budget.budgets.id).select(db.budgetlist.ALL,
																			db.products.ALL,
																			left=[db.products.on(db.products.id==db.budgetlist.product)]):

				tax_result="%.2f" % (((float(item.budgetlist.price)* (float(item.budgetlist.quantity) ))* float(item.budgetlist.tax))/float(100))
				

				items.append(dict(	id="%s" % item.products.id,
									name="%s"%item.products.name,
									cant="%s" % item.budgetlist.quantity,
									price="%.2f"%float(item.budgetlist.price),
									percent="%.2f" % float(item.budgetlist.tax), #se refiere al iva, pero en el .odt puse este nombre de variable por una ida de olla.
									total="%.2f" % (float(item.budgetlist.quantity) * float(item.budgetlist.price))
									)
							)
			
				
			try:

				# Report creation               
				template_file = os.path.join(request.folder, 'private', 'budget.odt')
				# tmp_uuid = uuid.uuid4()
				output_file_odt = os.path.join(request.folder, 'private', 'tmp','%s_%s.odt' % ("presupuesto",budget.budgets.id ))
				output_file_pdf = os.path.join(request.folder, 'private', 'tmp','%s_%s.pdf' % ("presupuesto",budget.budgets.id ))
				
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
				response.headers['Content-Disposition'] = 'attachment; filename=%s_%s.pdf' % ("presupuesto",budget.budgets.id )
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
		session.flash= 'No se pudo encontrar el presupuesto, inténtelo de nuevo'
		if auth.has_membership('superadministradores') or auth.has_membership('administradores'):
			redirect(URL(request.application, 'administrator', 'viewinvoice', args=request.args(0)))
		else:
			redirect(URL(request.application, 'account', 'billing', args=request.args(0)))
	else:
		redirect(URL(request.application, 'user','login'))


@auth.requires_login()
@page_allowed_ip
def newbudget(): 
	
	from shops import Product
	from invoices import Fiscal, Budget
	from adminsettings import Adminsettings
	Adminsettings(db), Product(db), Fiscal(db), Budget(db)
	settings = db(db.adminsettings.id>0).select(db.adminsettings.ALL).first()
	
	if auth.has_membership('superadministradores') or auth.has_membership('administradores'):
		if request.args(0):
			products=db( db.products.active==True ).select()
		
			if request.args(1):
				budget=db( (db.budgets.user==request.args(0)) &
							(db.budgets.id==request.args(1))).select().first()
			else:
				budget=db(	(db.budgets.user==request.args(0)) & 
							(db.budgets.status=="Creando")).select().first()


			if not budget:
				budgetid=db.budgets.insert(	status="Creando",
									tax=settings.tax,
									user=request.args(0))
				budget=db.budgets(budgetid)
			
			
			customer=db(db.auth_user.id==request.args(0)).select(	db.auth_user.id,
																	db.auth_user.first_name,
																	db.auth_user.last_name,
																	db.auth_user.email,
																	db.fiscals.ALL,
																	left=[db.fiscals.on(db.fiscals.user==db.auth_user.id)]).first()

			db.commit()

			return dict(products=products, customer=customer, tax=budget.tax, budgetid=budget.id)
		else:
			redirect(URL(request.application, 'administrator','users'))
	else:
		redirect(URL(request.application,'default','user/login'))


@auth.requires_login()
@page_allowed_ip
def cancelbudget(): 
	from invoices import Budget
	Budget(db)
	if auth.has_membership('superadministradores') or auth.has_membership('administradores'):
		try:
			db(	(db.budgets.user==request.vars.customer) & (db.budgets.id==request.vars.budgetid)).delete()
			
		except Exception as ex:
			logger.debug("OCurrió un error al borrar una orden de pedido desde billing: %s" % ex)
			response.flash="Ocurrió un error: %s" % ex

		redirect(URL(request.application, 'administrator','editcustomer', args=request.vars.customer))
		return dict()


@auth.requires_login()
@page_allowed_ip
def confirmbudget(): 
	from invoices import Budget, Budgetlist
	from adminsettings import Adminsettings
	Adminsettings(db), Budget(db), Budgetlist(db)
	settings = db(db.adminsettings.id>0).select(db.adminsettings.ALL).first()
	if auth.has_membership('superadministradores') or auth.has_membership('administradores'):
		try:
			budget= db((db.budgets.user==request.vars.customer) & (db.budgets.id==request.vars.budgetid)).select().first()
			
			total=float(0)
			totaltax=float(0)
			budgetlist=db(db.budgetlist.g_budget==budget.id).select()
			
			if budgetlist:
				for row in budgetlist:
					total=total + (float(row.quantity) * float(row.price))

				totaltax=(total*float(settings.tax))/100

				db(db.budgets.id==budget.id).update(total="%.2f"%total,
													totaltax="%.2f"%totaltax,
													status="Creado",
													confirmed_at=datetime.datetime.now())

				db.commit()
		except Exception as ex:
			db.rollback()
			logger.debug("Ocurrió un error al generar la factura %s" % ex)
			session.flash="Se produjo un error al generar la factura: %s" %ex
			redirect(URL('budget','newbudget',args=budget.id))

		redirect(URL(request.application, 'administrator', 'editcustomer', args=request.vars.customer))
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
		from invoices import Budget, Budgetlist
		from adminsettings import Adminsettings
		Adminsettings(db), Budget(db), Budgetlist(db), Product(db)
		settings = db(db.adminsettings.id>0).select(db.adminsettings.ALL).first()
		#entrada: data: { 'product': int, 'quantity': int, 'rate': int, 'operation': ['add','del','set'] }
		#salida: (json)sales
		#begin
		#comprobar si tiene un budget abierta y si no crearla
		if request.vars.budgetid:
			budget =db(	(db.budgets.user==request.vars.customer) & 
						(db.budgets.id==request.vars.budgetid)).select().first()
		else:
			budget=db(	(db.budgets.user==request.vars.customer) & 
					(db.budgets.status=="Creando")).select().first()
		if not budget and request.vars.operation=="add":
			budgetid=db.budgets.insert(	status="Creando", 
										user=request.vars.customer, 
										tax=settings.tax)
			budget=db.budgets(budgetid)
		
		budgetlist_id=None
		try:	
			#add/del product y quantity.
			row=db((db.budgetlist.product==request.vars.product) & (db.budgetlist.g_budget==budget.id)).select().first()

			if row:
				budgetlist_id=row.id

				if request.vars.operation=="add":
					db(db.budgetlist.id==budgetlist_id).update(quantity=int(row.quantity)+int(request.vars.quantity))

				elif request.vars.operation=="set":

					db(db.budgetlist.id==budgetlist_id).update(quantity=int(request.vars.quantity))
				db.commit()
			else:
				product=db(db.products.id==request.vars.product).select().first()
				#valor iva, para conservar el valor en caso de variar en el futuro
				#el precio para conservar en caso de variar en el futuro.
				budgetlist_id= db.budgetlist.insert(product=request.vars.product, 
													g_budget=budget.id, 
													quantity=request.vars.quantity, 
													price=product.price, 
													price_wdto=product.price,
													tax="%.2f" % settings.tax)
				db.commit()

				
		except Exception as ex:
			logger.debug("ALGO SALIO MAL en item %s" % ex)
			db.rollback()
		#retorna json del pedido
		
		data = db((db.budgetlist.g_budget==budget.id)).select(db.budgetlist.ALL, db.products.name, join=[db.products.on(db.products.id==db.budgetlist.product)]).as_list()
		return data
	else:
		return dict()



@auth.requires_login()
@auth.requires(auth.has_membership('superadministradores') or auth.has_membership('administradores') or auth.has_membership('directores') or auth.has_membership('gerente') or auth.has_membership('responsables'))
@service.json
def delitem():
	if auth.has_membership('superadministradores') or auth.has_membership('administradores'):
		from invoices import Invoice, Budget, Budgetlist
		from shops import Product
		from adminsettings import Adminsettings
		Adminsettings(db), Invoice(db), Budget(db), Budgetlist(db), Product(db)
		settings = db(db.adminsettings.id>0).select(db.adminsettings.ALL).first()

		budget=db(	(db.budgets.user==request.vars.customer) & 
					(db.budgets.id==request.vars.budgetid)).select().first()
		try:
			db((db.budgetlist.id==request.vars.id) & (db.budgetlist.g_budget==budget.id)).delete()
			db.commit()
		except:
			db.rollback()
		
		return db((db.budgetlist.g_budget==budget.id)).select(	db.budgetlist.ALL, 
															db.products.name, 
															db.products.id,
															join=[db.products.on(db.products.id==db.budgetlist.product)]).as_list()
	else:
		return dict()



@auth.requires_login()
@service_allowed_ip
@service.json
def items():
	if auth.has_membership('superadministradores') or auth.has_membership('administradores'):
		from invoices import Invoice, Budget, Budgetlist
		from shops import Product
		from adminsettings import Adminsettings
		Adminsettings(db), Invoice(db), Budget(db), Budgetlist(db), Product(db)
		settings = db(db.adminsettings.id>0).select(db.adminsettings.ALL).first()
		#entrada: data: { 'product': int, 'quantity': int, 'rate': int, 'operation': ['add','del','set'] }
		#salida: (json)sales
		#begin
		#comprobar si tiene un budget abierta y si no crearla
		budget=db(	(db.budgets.user==request.vars.customer) & 
					(db.budgets.id==request.vars.budgetid)).select().first()

		try:
			if not budget:
				budgetid=db.budgets.insert(	status="Creando", 
											user=request.vars.customer, 
											tax=settings.tax )
				budget=db.budgets(budgetid)
			
			return db((db.budgetlist.g_budget==budget.id)).select(	db.budgetlist.ALL, 
																db.products.name, 
																db.products.id,
																join=[db.products.on(db.products.id==db.budgetlist.product)]).as_list()
			 
		except Exception as ex:
			logger.debug(ex)
			db.rollback()
	else:
		return dict()





@auth.requires_login()
@page_allowed_ip
def viewbudget():
	if auth.has_membership('administradores') or auth.has_membership('superadministradores'):
		from invoices import Budget, Budgetlist
		from shops import Product
		Budget(db), Budgetlist(db), Product(db)
		budget= db(db.budgets.id==request.args(0)).select(db.budgets.ALL, 
															db.auth_user.id,
															db.auth_user.first_name,
															db.auth_user.last_name,  
															db.fiscals.ALL,
															left=[	db.auth_user.on(db.auth_user.id==db.budgets.user),
																	db.fiscals.on(db.fiscals.user==db.auth_user.id)]).first()

		if budget:

			budgetlist= db(db.budgetlist.g_budget==budget.budgets.id).select(db.budgetlist.ALL,
																		db.products.ALL,
																		left=[	db.products.on(db.products.id==db.budgetlist.product)])

			return dict(budget=budget, budgetlist=budgetlist)
		else:
			redirect(URL(request.application, 'administrator','users'))
	else:
		redirect(URL(request.application,'default','user/login'))
