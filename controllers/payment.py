# -*- coding: utf-8 -*-
business= "sandboxgextiendas@gestionexperta.com"
@auth.requires_login()
def index():
	from invoices import Fiscal, Order, Orderlist
	from shops import Product, PricePlan
	Fiscal(db), Product(db), PricePlan(db), Order(db), Orderlist(db)
	fiscal=db(db.fiscals.user==auth.user_id).select().first()
	order=None
	orderlist=None
	if fiscal:
		order=db((db.orders.user==auth.user_id) & (db.orders.status=="Creando")).select().first()
		if order:
			orderlist=db(db.orderlist.g_order==order.id).select()
			flatrate=False
			for item in orderlist:
				if item.product.plan:
					if item.product.plan.paymode=="flatrate":
						flatrate=True
		else:
			redirect(URL(c='account',f='index'))

	else:
		redirect(URL('myaccount', 'fiscal', vars=dict(wizard=True)))

	form=FORM(	INPUT(_type='radio', _name='paypal', _id='paypal', _value='paypal', value='yes').xml(),
				INPUT(_type='radio', _name='bank', _id='bank', _value='bank', value='no').xml(),
				INPUT(_name="confirm", _type='submit', _class="btn btn-grove-two btn-xlg"), _action=URL('confirm_order') )

	return dict(form=form, fiscal=fiscal, orderlist=orderlist, order=order, flatrate=flatrate)


@auth.requires_login()
def code():
	#Esto es para realizar el pago o cambiar de modo de pago. Se accede a esta función desde la url que viene en el aviso enviado por mail para recordar que se acerca la fecha
	#de caducidad del servicio cuya forma de pago es por transferencia

	# redirect()
	# https://devel.gextiendas.es/account/viewinvoice/20141000101

	return dict()


@auth.requires_login()
def bankcheckout():
	from queuemail import Queuemail
	from invoices import Order, Orderlist
	from adminsettings import Adminsettings
	Order(db), Orderlist(db), Adminsettings(db)
	settings = db(db.adminsettings.id>0).select(db.adminsettings.ALL).first()
	logger.debug(settings)
	queue=Queuemail(db)
	
	try:
		queuedata=[]		
		order=db((db.orders.user==auth.user_id) & (db.orders.status=="Creando")).select().first()

		if order!=None:
			
		 	db((db.orders.user==auth.user_id) & (db.orders.status=="Creando")).update(status='Pendiente pago', ordered_at=datetime.datetime.now(), payment_method="Transferencia")
		 	queuedata.append({'to': '%s'%auth.user.email,
					'subject':'[gextiendas] Confirmación pedido',
					'message':'Estimado %s,\nen cuanto realice su transferencia, en un plazo de 24/72 horas (según el tiempo de gestíón entre entidades bancarias) podremos verificarla y el servicio se activará. Es muy importante que no olvide detallar como concepto en la transferencia la referencia %s.\n\nSi tiene cualquier duda, le rogamos se ponga en contacto con nosotros. Muchas gracias por confiar en nuestro equipo.\n\nReciba un cordial saludo.\n--\nGextiendas' % (auth.user.first_name,order.payment_code.code)
					})
		 	
			#y ahora notificación a cada uno de los administradores
			logger.debug(db(db.auth_membership.group_id== db(db.auth_group.role=="administradores").select().first()['id'])._select(db.auth_membership.ALL, db.auth_user.ALL, left=db.auth_user.on(db.auth_membership.user_id==db.auth_user.id)))			
			mails=db(db.auth_membership.group_id==db((db.auth_group.role=="administradores") | (db.auth_group.role=="superadministradores") ).select().first()['id']).select(db.auth_membership.ALL, db.auth_user.ALL, left=db.auth_user.on(db.auth_membership.user_id==db.auth_user.id))
			
			for m in mails:
			
				url = "%(scheme)s://%(host)s%(urlrequest)s" % {	'scheme':request.env.wsgi_url_scheme,
																'host':request.env.http_host,
																'urlrequest':URL(	request.application, 
																					'administrator', 
																					'orders', 
																					vars=dict(id=order.id))}
			
				queuedata.append({'to':'%s' % m.auth_user.email,
								'subject':'Aviso de pago mediante transferencia para %s'%order.payment_code.code,
								'message':'El usuario %s ha solicitado pagar mediante transferencia bancaria los servicios . Desde el momento que el cliente haga la misma, tendrá entre 24/48 horas para verificar la recepción de la misma:\n\n %s\n\n' % (auth.user.email, url)
								})
			
				queue.queuemessage(queuedata)
			

			
			db.commit()
			
			session.flash="Pedido confirmado. Le hemos enviado un correo electrónico"
			return dict(bank_account=settings.bank_account, beneficiary=settings.beneficiary, bank=settings.bank, ref=order.payment_code.code, total="%.2f" % (float(order.total) + float(order.totaltax)), redirect=False)
		else:
			return dict(redirect=True)

	except Exception as ex:
		session.flash="Ocurrió un error al hacer el pedido. Inténtelo de nuevo"
		db.rollback()
		
		return dict(bank_account=settings.bank_account, beneficiary=settings.beneficiary, bank=settings.bank, ref=order.payment_code, total="%.2f" % (float(order.total) + float(order.totaltax)), redirect=False)

@auth.requires_login()
def paypalcheckout():
	from paypalcrypto import PaypalCrypto
	import time
	from queuemail import Queuemail
	from invoices import Order, Orderlist
	from shops import ContractedProduct, PricePlan
	from adminsettings import Adminsettings
	from auxiliartools import AuxiliarTools	
	
	Order(db), Orderlist(db), Adminsettings(db), ContractedProduct(db), PricePlan(db)
	settings = db(db.adminsettings.id>0).select(db.adminsettings.ALL).first()
	external=AuxiliarTools(db)

	order=db((db.orders.user==auth.user_id) & (db.orders.status=="Creando")).select().first()
	
	
	try:
		if order!=None:
			
			code=external.generatecode()
			if not order.payment_code:
				order.update_record(payment_code=db.paymentcodes.insert(code=code))
				db.commit()
			order.update_record(payment_method="Paypal")
			#custom="código pedido %s %s %s"%(order.user*100, order.id*100, str(long(time.mktime(order.ordered_at.timetuple())*1e3)))
			
			logger.debug("FLATRATE: %s %s %s" % (request.vars.flatrate, request.vars.flatrate==True, type(request.vars.flatrate)))
			attributes=None
			if request.vars.flatrate=='False':

				attributes= {
					"cert_id":"UPWJKQGJHDE4S",
					"cmd":"_xclick",
					#"cmd":"_cart",
					"amount":"%.2f" % (float(order.total) + float(order.totaltax)),
					"currency_code":"EUR",
					"custom":order.payment_code.code,
					"item_name":"[Gextiendas] Servicios de ecommerce",
					#"business":"K6VY4N9UQQLNQ", #sandboxgextiendas@gestionexperta.com
					"business":"sandboxgextiendas@gestionexperta.com",
					#"business":"payments@gextiendas.es",
					"paymentaction":"sale",
					"notify_url":"%(scheme)s://%(host)s%(urlrequest)s" % {'scheme':request.env.wsgi_url_scheme,'host':request.env.http_host,'urlrequest':URL(request.application,'payment','ipn_handler')},
					"return":"%(scheme)s://%(host)s%(urlrequest)s" % {'scheme':request.env.wsgi_url_scheme,'host':request.env.http_host,'urlrequest':URL(request.application, 'payment','receipt_page')}
				}
			else:
				attributes= {
					"cert_id":"UPWJKQGJHDE4S",
					"cmd":"_xclick-subscriptions",
					#"amount":"%.2f" % (float(order.total) + float(order.totaltax)),
					"a3":"%.2f" % (float(order.total) + float(order.totaltax)),
					"p3":"1",
					"t3":"M",
					"src":"1",
					"sra":"1",
					"1c":"ES",
					"no_shipping":"1",
					"currency_code":"EUR",
					"custom":order.payment_code.code,
					"item_name":"Servicios Gextiendas",
					#"business":"K6VY4N9UQQLNQ", #sandboxgextiendas@gestionexperta.com
					"business": business,
					#"business":"payments@gextiendas.es",
					"paymentaction":"sale",
					"notify_url":"%(scheme)s://%(host)s%(urlrequest)s" % {'scheme':request.env.wsgi_url_scheme,'host':request.env.http_host,'urlrequest':URL(request.application,'payment','ipn_handler')},
					"return":"%(scheme)s://%(host)s%(urlrequest)s" % {'scheme':request.env.wsgi_url_scheme,'host':request.env.http_host,'urlrequest':URL(request.application, 'account','index')}
				}

			logger.debug("ATTRIBUTESSS %s" % attributes)
	except Exception as ex:
		db.rollback()
		logger.debug("Paypalcheck error: %s" % ex)
		session.flash="Ocurrió un error, inténtelo de nuevo"
		redirect('payment','index')

	pc=PaypalCrypto(attributes)
	encattrs=pc.paypalencrypt()
	logger.debug("encattrs: %s" % encattrs)

	

	return dict(encattrs=encattrs, order=db(db.orders.id==order.id).select(	db.orders.ALL,
												db.contractedproducts.ALL,
												left=[	db.orderlist.on(db.orderlist.g_order==db.orders.id),
														db.contractedproducts.on(db.contractedproducts.orderlist==db.orderlist.id)]
												).first())


def ipn_handler():
	import urllib2, datetime

	logger.debug(request.vars)



	#queryid=request.vars['custom']

	
	url="%(scheme)s://%(host)s?cmd=_notify-validate&%(urlrequest)s" % {'scheme':request.env.wsgi_url_scheme,'host':'www.sandbox.paypal.com/cgi-bin/webscr','urlrequest':URL(vars=request.vars)}
	#url="%(scheme)s://%(host)s?cmd=_notify-validate&%(urlrequest)s" % {'scheme':request.env.wsgi_url_scheme,'host':'www.paypal.com/cgi-bin/webscr','urlrequest':URL(vars=request.vars)}

	url=url.replace("/payment/ipn_handler?","")
	#logger.debug("llego4 %s" % url)

	result=""
	while True:
	 	try:
	 		req = urllib2.Request(url)
	 		output = urllib2.urlopen(req)
	 		result=output.read()
	 		break
		except Exception as ex:
				logger.debug("Error %s"% ex)

	

	#IPN datos relevante: custom, subscr_id, txn_type, txn_id, ipn_track_id, payment_status,
	# PayPal will then send one single-word message, VERIFIED, if the message is valid; otherwise, it will send another single-word message, INVALID.

	# Important: After you have authenticated an IPN message (that is, received a VERIFIED response from PayPal), you must perform these important checks before you can assume that the IPN is both legitimate and has not already been processed:

	# Check that the payment_status is Completed.
	# If the payment_status is Completed, check the txn_id against the previous PayPal transaction that you processed to ensure the IPN message is not a duplicate.
	# Check that the receiver_email is an email address registered in your PayPal account.
	# Check that the price (carried in mc_gross) and the currency (carried in mc_currency) are correct for the item (carried in item_name or item_number).
	# Once you have completed these checks, IPN authentication is complete. Now, you can update your database with the information provided and initiate any back-end processing that's appropriate.
		
	#IPN nornal

	#<Storage {'protection_eligibility': 'Eligible', 'last_name': 'Buyer', 'txn_id': '3DE20514FP4266159', 'receiver_email': 'sandboxgextiendas@gestionexperta.com', 'payment_status': 'Completed', 'payment_gross': '', 'tax': '0.00', 'residence_country': 'ES', 'address_state': 'Albacete', 'payer_status': 'verified', 'txn_type': 'web_accept', 'address_country': 'Spain', 'handling_amount': '0.00', 'payment_date': '03:40:08 Nov 04, 2014 PST', 'first_name': 'Test', 'item_name': '[Gextiendas] Servicios de ecommerce', 'address_street': 'calle Vilamar\\xc3\\xad 76993- 17469', 'charset': 'windows-1252', 'custom': '0113679HUQ', 'notify_version': '3.8', 'address_name': 'Test Buyer', 'test_ipn': '1', 'item_number': '', 'receiver_id': 'K6VY4N9UQQLNQ', 'transaction_subject': '0113679HUQ', 'business': 'sandboxgextiendas@gestionexperta.com', 'payer_id': 'RNH2WS7RX3LV8', 'verify_sign': 'AwD4sJJmdrzDKNGw7KMAMuZSx1AHAUFXw7K0K.MTc4yFwx3f-ME79PYb', 'address_zip': '02001', 'payment_fee': '', 'address_country_code': 'ES', 'address_city': 'Albacete', 'address_status': 'unconfirmed', 'mc_fee': '2.61', 'mc_currency': 'EUR', 'shipping': '0.00', 'payer_email': 'paypal-buyer@gestionexperta.com', 'payment_type': 'instant', 'mc_gross': '66.55', 'ipn_track_id': '70c4750d34201', 'quantity': '1'}> 
	#<Storage {'protection_eligibility': 'Eligible', 'last_name': 'Buyer', 'txn_id': '3DE20514FP4266159', 'receiver_email': 'sandboxgextiendas@gestionexperta.com', 'payment_status': 'Completed', 'payment_gross': '', 'tax': '0.00', 'residence_country': 'ES', 'address_state': 'Albacete', 'payer_status': 'verified', 'txn_type': 'web_accept', 'address_country': 'Spain', 'handling_amount': '0.00', 'payment_date': '03:40:08 Nov 04, 2014 PST', 'first_name': 'Test', 'item_name': '[Gextiendas] Servicios de ecommerce', 'address_street': 'calle Vilamar\\xc3\\x83\\xc2\\xad 76993- 17469', 'charset': 'UTF-8', 'custom': '0113679HUQ', 'notify_version': '3.8', 'address_name': 'Test Buyer', 'test_ipn': '1', 'item_number': '', 'receiver_id': 'K6VY4N9UQQLNQ', 'transaction_subject': '0113679HUQ', 'business': 'sandboxgextiendas@gestionexperta.com', 'payer_id': 'RNH2WS7RX3LV8', 'auth': 'A5I9nNJn6BAC5e2tgl00VrEPDi978J0G7DckCMvTJ2Wus4RGjw67pD3EaztVX2b2cU4WjXEM43QIgv9obAMATIA', 'verify_sign': 'AFcWxV21C7fd0v3bYYYRCpSSRl31Af8nlEsXeJR3qYq0oRp.V6axDaRc', 'address_zip': '02001', 'payment_fee': '', 'address_country_code': 'ES', 'address_city': 'Albacete', 'address_status': 'unconfirmed', 'mc_fee': '2.61', 'mc_currency': 'EUR', 'shipping': '0.00', 'payer_email': 'paypal-buyer@gestionexperta.com', 'payment_type': 'instant', 'mc_gross': '66.55', 'quantity': '1'}> [] 
	#<Storage {'protection_eligibility': 'Eligible', 'last_name': 'Buyer', 'txn_id': '3DE20514FP4266159', 'receiver_email': 'sandboxgextiendas@gestionexperta.com', 'payment_status': 'Completed', 'payment_gross': '', 'tax': '0.00', 'residence_country': 'ES', 'address_state': 'Albacete', 'payer_status': 'verified', 'txn_type': 'web_accept', 'address_country': 'Spain', 'handling_amount': '0.00', 'payment_date': '03:40:08 Nov 04, 2014 PST', 'first_name': 'Test', 'item_name': '[Gextiendas] Servicios de ecommerce', 'address_street': 'calle Vilamar\\xc3\\xad 76993- 17469', 'charset': 'windows-1252', 'custom': '0113679HUQ', 'notify_version': '3.8', 'address_name': 'Test Buyer', 'test_ipn': '1', 'item_number': '', 'receiver_id': 'K6VY4N9UQQLNQ', 'transaction_subject': '0113679HUQ', 'business': 'sandboxgextiendas@gestionexperta.com', 'payer_id': 'RNH2WS7RX3LV8', 'verify_sign': 'AwD4sJJmdrzDKNGw7KMAMuZSx1AHAUFXw7K0K.MTc4yFwx3f-ME79PYb', 'address_zip': '02001', 'payment_fee': '', 'address_country_code': 'ES', 'address_city': 'Albacete', 'address_status': 'unconfirmed', 'mc_fee': '2.61', 'mc_currency': 'EUR', 'shipping': '0.00', 'payer_email': 'paypal-buyer@gestionexperta.com', 'payment_type': 'instant', 'mc_gross': '66.55', 'ipn_track_id': '70c4750d34201', 'quantity': '1'}> 
	#<Storage {'protection_eligibility': 'Eligible', 'last_name': 'Buyer', 'txn_id': '3DE20514FP4266159', 'receiver_email': 'sandboxgextiendas@gestionexperta.com', 'payment_status': 'Completed', 'payment_gross': '', 'tax': '0.00', 'residence_country': 'ES', 'address_state': 'Albacete', 'payer_status': 'verified', 'txn_type': 'web_accept', 'address_country': 'Spain', 'handling_amount': '0.00', 'payment_date': '03:40:08 Nov 04, 2014 PST', 'first_name': 'Test', 'item_name': '[Gextiendas] Servicios de ecommerce', 'address_street': 'calle Vilamar\\xc3\\xad 76993- 17469', 'charset': 'windows-1252', 'custom': '0113679HUQ', 'notify_version': '3.8', 'address_name': 'Test Buyer', 'test_ipn': '1', 'item_number': '', 'receiver_id': 'K6VY4N9UQQLNQ', 'transaction_subject': '0113679HUQ', 'business': 'sandboxgextiendas@gestionexperta.com', 'payer_id': 'RNH2WS7RX3LV8', 'verify_sign': 'AwD4sJJmdrzDKNGw7KMAMuZSx1AHAUFXw7K0K.MTc4yFwx3f-ME79PYb', 'address_zip': '02001', 'payment_fee': '', 'address_country_code': 'ES', 'address_city': 'Albacete', 'address_status': 'unconfirmed', 'mc_fee': '2.61', 'mc_currency': 'EUR', 'shipping': '0.00', 'payer_email': 'paypal-buyer@gestionexperta.com', 'payment_type': 'instant', 'mc_gross': '66.55', 'ipn_track_id': '70c4750d34201', 'quantity': '1'}> 
	

	#IPN recurrent  
	#primera notificación. Alta de suscripción. Notiicado por mi cuenta.	
	#<Storage {'last_name': 'Buyer', 'receiver_email': 'sandboxgextiendas@gestionexperta.com', 'residence_country': 'ES', 'payer_status': 'verified', 'txn_type': 'subscr_signup', 'first_name': 'Test', 'item_name': 'Servicios Gextiendas', 'charset': 'windows-1252', 'custom': '202545T4H4', 'notify_version': '3.8', 'recurring': '1', 'test_ipn': '1', 'business': 'sandboxgextiendas@gestionexperta.com', 'payer_id': 'RNH2WS7RX3LV8', 'period3': '1 M', 'verify_sign': 'AX6PBnkcJ7jJrr5pDIO.z1RmrMaaAGgNGrGxSeVNwJzNXXwYvajPnm4-', 'subscr_id': 'I-BWW79X6683EA', 'mc_amount3': '21.78', 'mc_currency': 'EUR', 'subscr_date': '05:12:14 Nov 03, 2014 PST', 'payer_email': 'paypal-buyer@gestionexperta.com', 'ipn_track_id': '6eb738f99ad8', 'reattempt': '1'}>

	#segunda. Notificación de pago por parte de la cuenta del cliente
	#<Storage {'protection_eligibility': 'Ineligible', 'last_name': 'Buyer', 'txn_id': '69G69974FM486513Y', 'receiver_email': 'sandboxgextiendas@gestionexperta.com', 'payment_status': 'Completed', 'payment_gross': '', 'residence_country': 'ES', 'payer_status': 'verified', 'txn_type': 'subscr_payment', 'payment_date': '05:12:15 Nov 03, 2014 PST', 'first_name': 'Test', 'item_name': 'Servicios Gextiendas', 'charset': 'windows-1252', 'custom': '202545T4H4', 'notify_version': '3.8', 'transaction_subject': 'Servicios Gextiendas', 'test_ipn': '1', 'receiver_id': 'K6VY4N9UQQLNQ', 'business': 'sandboxgextiendas@gestionexperta.com', 'payer_id': 'RNH2WS7RX3LV8', 'verify_sign': 'AaS.4COnBP7ShIMRTtOpCSbO2eC3AXffHkIB5NNBcAMHHtS-KslOaLMS', 'subscr_id': 'I-BWW79X6683EA', 'payment_fee': '', 'mc_fee': '1.09', 'mc_currency': 'EUR', 'payer_email': 'paypal-buyer@gestionexperta.com', 'payment_type': 'instant', 'mc_gross': '21.78', 'ipn_track_id': '6eb738f99ad8'}> 

	# ==> /var/log/apache2/gextiendas_443.com-error.log <== 
	
	
	#baja
	#notificacion baja de suscripción desde mi cuenta por el payer
	#<Storage {'last_name': 'Buyer', 'receiver_email': 'sandboxgextiendas@gestionexperta.com', 'residence_country': 'ES', 'payer_status': 'verified', 'txn_type': 'subscr_cancel', 'first_name': 'Test', 'item_name': 'Servicios Gextiendas', 'charset': 'windows-1252', 'custom': '202545T4H4', 'notify_version': '3.8', 'recurring': '1', 'test_ipn': '1', 'business': 'sandboxgextiendas@gestionexperta.com', 'payer_id': 'RNH2WS7RX3LV8', 'period3': '1 M', 'verify_sign': 'Aey6maswQ4YaVSn6P5pFEGe747AEAsoWZDTnZcoJRVJim0KtLpzDZghw', 'subscr_id': 'I-BWW79X6683EA', 'mc_amount3': '21.78', 'mc_currency': 'EUR', 'subscr_date': '05:16:43 Nov 03, 2014 PST', 'payer_email': 'paypal-buyer@gestionexperta.com', 'ipn_track_id': 'd58261bd67c86', 'reattempt': '1'}> 
	

	if result.replace("\n","")=="VERIFIED":
		#guardar datos en paypalrecord
		from invoices import Paypalrecord, Paymentcode, Order
		Paypalrecord(db), Order(db)
		if request.vars['txn_id']:
			paypalrecord=db(db.paypalrecords.txn_id==request.vars['txn_id']).select(db.paypalrecords.ALL,
																					db.paymentcodes.ALL,
																					join=[db.paymentcodes.on(db.paymentcodes.id==db.paypalrecords.payment_code)])
			
			order=db(db.paymentcodes.code==request.vars['custom']).select(	db.orders.ALL,
																			db.payments.id,
																			join=[db.paymentcodes.id==db.orders.payment_code])

			if request.vars['payment_status']=='Completed':
				if not paypalrecord:
					if 	request.vars['receiver_email']==business and request.vars['mc_gross']== (order.orders.total + order.orders.totaltax) and request.vars['mc_currency']=="EUR": #para evitar spoofing IPN
						db.paypalrecord.insert(	
												payment_code = db(db.paymentcodes.code==request.vars['custom']).select(db.paymentcodes.id).first()['id'],
												subscr_id = request.vars['subscr_id'],
												payer_id = request.vars['payer_id'],
												txn_type = request.vars['txn_type'],
												txn_id = request.vars['txn_id'],
												ipn_track_id = request.vars['ipn_track_id'],
												payment_status = request.vars['payment_status'],
												payment_date = request.vars['payment_date'])

	elif result.replace("\n","")=="INVALID":
		#email a administradores para investigar. Sospechoso de fraude.
		pass

	# 	from shops import ContractedProduct, Product, Shop
	# 	from invoices import Order, Orderlist, Invoice, CreditAccount, AccountingEntry, Paymentcode
	# 	from gluon.contrib.pysimplesoap.client import SoapClient
	# 	ContractedProduct(db), Product(db), Shop(db), Order(db), Orderlist(db),  AccountingEntry(db), Paymentcode(db)

	# 	mcontracts=db(	((db.contractedproducts.expiration == None) | (db.contractedproducts.expiration >= datetime.datetime.now())) &
	# 						(	(db.profileplans.active==True) &
	# 							(db.priceplans.planname!="free") & 
	# 							(db.contractedproducts.active==True)
	# 						) &
	# 						db.paymentcodes.code==queryid
	# 					).select(db.contractedproducts.ALL,
	# 							 db.products.plan,
	# 							 db.products.price,
	# 							 db.products.suscription,
	# 							 db.products.name,
	# 							 db.priceplans.planname,
	# 							 db.priceplans.id,
	# 							 db.profileplans.ALL,
	# 							 db.orders.ALL,
	# 							 db.paymentcodes.ALL,
	# 							 left=[	db.products.on(db.products.id==db.contractedproducts.product),
	# 							 		db.profileplans.on(db.profileplans.product==db.products.id),
	# 							 		db.priceplans.on(db.priceplans.id==db.profileplans.priceplan),
	# 							 		db.orderlist.on(db.orderlist.id==db.contractedproducts.orderlist),
	# 							 		db.orders.on(db.orders.id==db.orderlist.g_order)])


	# 	queue=Queuemail(db)
		
	# 	order=db(db.paymentcodes.code==queryid).select(	db.paymentcodes.ALL,
	# 													db.orders.ALL,
	# 													join=[db.orders.on(db.orders.payment_code==db.paymentcodes.id)])
		
	# 	# order=db.orders(orderid)
	# 	try:
	# 		if order:
	# 			#crear factura
	# 			invoice=Invoice(db)
	# 			invoiceid=invoice.makeinvoice(order.id) #aquí se hace además la anotación positiva en creditaccount
	# 			if invoiceid!=None:
	# 				# notificar recepción del pago
	# 				subject="[gextiendas] Factura Nº %s" % db.invoices(invoiceid).invoice_number
	# 				queuedata=[]

	# 				urlinvoice= '%(scheme)s://%(host)s%(url)s' % {'scheme':request.env.wsgi_url_scheme,'host':request.env.http_host, 'url':URL('payment','code',args=[order.payment_code.code])}
	# 				data={	"now": datetime.datetime.now().strftime("%d-%m-%Y %H:%M"),
	# 								"name": order.user.first_name, 
	# 								"code": order.payment_code.code,
	# 								"url": urlinvoice,
	# 					}
	# 				plaintext="""
	# 						\t\t\t\t Fuengirola (Málaga), a %(now)s \n
	# 						Estimado %(name)s, hemos recibido un pago mediante transferencia correspondiente a la referencia de pago: %(code)s \n
	# 						Puede descargarse la factura siguiendo este enlace:\n
	# 						%(url)s \n
	# 						El equipo de GEXtiendas.\n

	# 							""" % data	
	# 				html="""
	# 						<p>Fuengirola (Málaga), a %(now)s</p>
	# 						<p>Estimado %(name)s, hemos recibido un pago mediante transferencia correspondiente a la referencia de pago: %(code)s</p>
	# 						<p>Puede descargarse la factura siguiendo este enlace:</p>
	# 						<p><a href='%(url)s'>%(url)s</a></p>
	# 						<p>El equipo de GEXtiendas.</p>
	# 					""" % data


	# 				queuedata.append({	'to': '%s'%order.user.email,
	# 									'subject':subject,
	# 									'message':plaintext,
	# 									'html':XML(html),
	# 									'template':'communications/paymentreceived_template.html',
	# 									'title':'Pago recibido: %s' % subject,
	# 									'unsubscribe':''
	# 								})
	# 				queue.queuemessage(queuedata)

	# 				#
	# 				# client = SoapClient(wsdl="http://localhost:8000/internalgexcommerce/default/call/soap?WSDL=None")
	# 				# logger.debug(client.enableDomainShop())
	# 				# buscar si hay dominios que estén esperando ser habilitados en una tienda del productocontratado en la lista de ese pedido
	# 				# activar dominio
	# 				# anotar accountinentry negativo
	# 				# actualizar crédito

	# 				session.flash="Operación realizada con éxito"
	# 			else:
	# 				session.flash="Hubo un error y no se pudo aprobar el pedido"
	# 		else:
	# 			session.flash="Hubo un error. No se pudo aprobar el pedido"

	# 	except Exception as ex:

	# 		logger.debug(ex)
	# 		session.flash="Ocurrió un error %s " % ex

	#	redirect(URL('administrator','orders'))




def receipt_page():
	logger.debug("RECEIPT PAGE %s %s" % (request.vars, request.args))


	#RECEIPT PAGE <Storage {'protection_eligibility': 'Eligible', 'last_name': 'Buyer', 'txn_id': '6W703032M08998407', 'receiver_email': 'sandboxgextiendas@gestionexperta.com', 'payment_status': 'Completed', 'payment_gross': '', 'tax': '0.00', 'residence_country': 'ES', 'address_state': 'Albacete', 'payer_status': 'verified', 'txn_type': 'web_accept', 'address_country': 'Spain', 'handling_amount': '0.00', 'payment_date': '09:19:48 Oct 30, 2014 PDT', 'first_name': 'Test', 'item_name': '[Gextiendas] Servicios de ecommerce', 'address_street': 'calle Vilamar\\xc3\\x83\\xc2\\xad 76993- 17469', 'charset': 'UTF-8', 'custom': '78305R8YUP', 'notify_version': '3.8', 'address_name': 'Test Buyer', 'test_ipn': '1', 'item_number': '', 'receiver_id': 'K6VY4N9UQQLNQ', 'transaction_subject': '78305R8YUP', 'business': 'sandboxgextiendas@gestionexperta.com', 'payer_id': 'RNH2WS7RX3LV8', 'auth': 'AcKFLdoPf283IlmPw6cKhCB0xT62NlgwpcVmFmB8wxYh9A09gHcfZlGUVmvP5h6MwJnB4ayyThOJs0AMNRwvxig', 'verify_sign': 'AKWrfKn9abdlJmJ8qdzlhG7K2kFPAmIWCNycE99.QpOu.PVZ8CscUNch', 'address_zip': '02001', 'payment_fee': '', 'address_country_code': 'ES', 'address_city': 'Albacete', 'address_status': 'unconfirmed', 'mc_fee': '1.09', 'mc_currency': 'EUR', 'shipping': '0.00', 'payer_email': 'paypal-buyer@gestionexperta.com', 'payment_type': 'instant', 'mc_gross': '21.78', 'quantity': '1'}> [] 

	return dict(output=request.vars, output_args=request.args )




	#otro ejemplo recurrent. El primer IPN no tiene txn_id
	# <Storage {'last_name': 'Buyer', 'receiver_email': 'sandboxgextiendas@gestionexperta.com', 'residence_country': 'ES', 'payer_status': 'verified', 'txn_type': 'subscr_signup', 'first_name': 'Test', 'item_name': 'Servicios Gextiendas', 'charset': 'windows-1252', 'custom': '95572USWOY', 'notify_version': '3.8', 'recurring': '1', 'test_ipn': '1', 'business': 'sandboxgextiendas@gestionexperta.com', 'payer_id': 'RNH2WS7RX3LV8', 'period3': '1 M', 'verify_sign': 'A6EWPBZEuDT.99y2h87vt.owPq2GAXmqDzqwlLGFFxSeAWKQ9RbGhM3W', 'subscr_id': 'I-RJ9CRP2WVNFB', 'mc_amount3': '21.78', 'mc_currency': 'EUR', 'subscr_date': '05:54:41 Nov 05, 2014 PST', 'payer_email': 'paypal-buyer@gestionexperta.com', 'ipn_track_id': '112eff333e81d', 'reattempt': '1'}> 
	# <Storage {'protection_eligibility': 'Ineligible', 'last_name': 'Buyer', 'txn_id': '0PC23572KE118343C', 'receiver_email': 'sandboxgextiendas@gestionexperta.com', 'payment_status': 'Completed', 'payment_gross': '', 'residence_country': 'ES', 'payer_status': 'verified', 'txn_type': 'subscr_payment', 'payment_date': '05:54:42 Nov 05, 2014 PST', 'first_name': 'Test', 'item_name': 'Servicios Gextiendas', 'charset': 'windows-1252', 'custom': '95572USWOY', 'notify_version': '3.8', 'transaction_subject': 'Servicios Gextiendas', 'test_ipn': '1', 'receiver_id': 'K6VY4N9UQQLNQ', 'business': 'sandboxgextiendas@gestionexperta.com', 'payer_id': 'RNH2WS7RX3LV8', 'verify_sign': 'A9Mb5bB7cYUoXgjRHF2-VHQRPoGvAPUHDi5XtvsV-5Yaemm2YvChqGe1', 'subscr_id': 'I-RJ9CRP2WVNFB', 'payment_fee': '', 'mc_fee': '1.09', 'mc_currency': 'EUR', 'payer_email': 'paypal-buyer@gestionexperta.com', 'payment_type': 'instant', 'mc_gross': '21.78', 'ipn_track_id': '112eff333e81d'}> 
