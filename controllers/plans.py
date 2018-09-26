#-*- coding: utf-8 -*-
@auth.requires_login()
def index():
	from shops import Shop, DomainShop, PricePlan
	Shop(db), DomainShop(db), PricePlan(db)
	
	shop = db((db.shop.host==request.vars.host) & (db.shop.user==auth.user_id)).select().first()
	
	if shop:

		return dict(host=shop.host)
	else:
		session.flash="No podemos encontrar la tienda %s" % request.vars.host
		redirect(URL('index'))

@auth.requires_login()
def contractplan():
	from shops import ContractedProduct
	ContractedProduct(db) #este ya carga los objetos que le hacen falta
	plan=db(db.priceplans.id==request.vars.plan).select().first()
	shop = db((db.shop.host==request.vars.host) & (db.shop.user==auth.user_id)).select().first()
	
	if shop and plan:
		return dict(shop=shop, plan=plan)
	else:
		session.flash="Disculpe la molestias. No podemos encontrar la tienda %s o el plan solicitado." % request.vars.host
		redirect(URL('index'))


@auth.requires_login()
def payment():
	from invoices import Order, Orderlist
	from shops import Product, Shop, DomainShop, ContractedProduct
	from adminsettings import Adminsettings
	from auxiliartools import AuxiliarTools
	Adminsettings(db)
	settings = db(db.adminsettings.id>0).select(db.adminsettings.ALL).first()
	Shop(db), Order(db), Orderlist(db), Product(db), DomainShop(db), ContractedProduct(db)
	external=AuxiliarTools(db)

	host=request.vars.host
	plan=request.vars.plan
	cert=request.vars.cert
	if host and plan and cert:#hay que comprobar que viene por request un plan asignado a una tienda con el dato del cert
		try:	
			db((db.orders.status=='Creando') & (db.orders.user==auth.user_id)).delete() #sólo puede haber un pedido en estado de creación.
			plan=db(db.priceplans.id==request.vars.plan).select().first()
			shop = db((db.shop.host==request.vars.host) & (db.shop.user==auth.user_id)).select().first()
			if shop and plan: #comprobar que existe y es suyo (siempre por seguridad)
				profileplans=db(db.profileplans.priceplan==plan).select()
				total=float(0)
				for profileplan in profileplans:
					if profileplan.active:
						product=db(db.products.id==profileplan.product).select().first()

						if product.name.find("SSL")!=-1 and cert=="false":
							continue
						total=total + float(product.price)

				orderid=db.orders.insert(	user=auth.user_id,
											total=total,
											totaltax="%.2f" %float(((total * float(settings.tax))/100)),
											status="Creando",
											payment_code=db.paymentcodes.insert(code=external.generatecode()),
											payment_method=None)
				for profileplan in profileplans:
					if profileplan.active:
						product=db(db.products.id==profileplan.product).select().first()
						if product.name.find("SSL")!=-1 and cert=="false":
							continue
						orderlistid=db.orderlist.insert(product=product.id,
											g_order=orderid,
											quantity=1,
											price=product.price,
											price_wdto=product.price,
											tax=settings.tax)

						#NO SE PUEDE HACER EL INSERT DIRECTAMENTE. HAY QUE VER SI EL SHOP YA TIENE CONTRATADO EL PRODUCTO. SI NO TIENE se hace un INSERT, si no, no hace nada.
						#En realidad esta comprobación no hace falta porque no se va a dar este caso, pero sí en contracts.postcontracts por ser una generación de contratos manual .
						#Sólo se va a poder contratar una unidad y la recursividad y duración de la periodicidad harán el resto.
						
						contracted=db(	(db.contractedproducts.shop==shop.id) & 
										(db.contractedproducts.user==auth.user_id) & 
										(db.contractedproducts.product==product.id)).select().first()

						if not contracted:
							db.contractedproducts.insert(
											user=auth.user_id,
											product=product.id,
											period=product.min_period,
											autorenove=product.suscription,
											start=None, 
											renove=None, #fecha de la renovación.
											expiration=None,
											shop=shop.id,
											orderlist=orderlistid,
											paymentmethod=None)
						
				db.commit()
				return "OK"
		except Exception as ex:
			session.flash="Ocurrió un error al crear el pedido %s" % ex
			redirect(request.env.http_referer)

	else:
		session.flash="Disculpen la molestias. No podemos encontrar la información requerida"
		redirect(request.application, 'account', 'index')




######funciones privadas


	




	#crear el pedido

