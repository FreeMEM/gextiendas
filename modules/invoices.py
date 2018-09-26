# -*- coding: utf-8 -*-
from gluon import *
import logging, datetime
from settings import Settings
logger = logging.getLogger(" >>>> modules/shops >>>> Gextiendas: ")
logger.setLevel(logging.DEBUG)
from shops import Product 

class Invoice(object):
	
	def __init__(self,db):
		Product(db)
		self.db=db 
		try:
			Fiscal(db)
			self.define_tables()
		except:
			pass
	def define_tables(self):
		config=Settings()
		self.db.define_table('invoices',
			Field('user','reference auth_user'), #cliente cliente
			Field('subtotal', 'decimal(10,2)'),
			Field('discount', 'decimal(10,2)'),
			Field('total', 'decimal(10,2)'),
			Field('taxes', 'decimal(10,2)'),
			Field('tax', 'decimal(10,2)'),
			Field('created_at', 'date', default=datetime.date.today(), requires=IS_DATE()),
			Field('invoice_number', 'decimal(12,0)', unique=True, notnull=False),
			#Field('sent', 'boolean', default=False, notnull=True), #indica si ha sido enviada por email
			migrate=config.settings['migrate'])
	def makeinvoice(self, orderid, paid=None, manualinvoice=False): #manualinvoice hace que se generen (manualinvoice==False) las anotaciones de crédito o que no se generen (True)
		from adminsettings import Adminsettings
		db=self.db
		adminsettings = db(db.adminsettings.id>0).select(db.adminsettings.ALL).first()
		order=db(db.orders.id==orderid).select().first()
		if order.invoice==None:
			lastinvoice=db(db.invoices.id>0).select(orderby=~db.invoices.id).first() #last
			if lastinvoice:
				strinvoice=str(lastinvoice.invoice_number)
				if strinvoice.find(datetime.datetime.now().strftime('%Y'))>=0:
					invoice_number=int(strinvoice)+1
				else: #hemos cambiado de año
					invoice_number=int("%s%s"% (datetime.datetime.now().strftime('%Y'), adminsettings.serialinit))
			else:
				invoice_number=int("%s%s"% (datetime.datetime.now().strftime('%Y'), adminsettings.serialinit))	
				
			return self.__insertinvoice(order, invoice_number, paid, manualinvoice)
		else:
			return None


	#metodos privados!

	def __insertinvoice(self, order, invoice_number, paid, manualinvoice): #esto genera crédito y contratos
		from shops import ContractedProduct
		from adminsettings import Adminsettings
		db=self.db

		ContractedProduct(db), Orderlist(db), Adminsettings(db)
		settings = db(db.adminsettings.id>0).select(db.adminsettings.ALL).first()
		try:
			invoiceid=db.invoices.insert(	user=order.user,
											subtotal=order.total,
											discount="0.00",
											total="%.2f" % (float(order.total)+float(order.totaltax)),
											taxes=order.totaltax,
											tax=settings.tax,
											invoice_number=invoice_number)


			#fecha de confirmación del order y "Pagado"
			if paid!="Pendiente pago":
				db(db.orders.id==order.id).update(invoice=invoiceid, confirmed_at=datetime.datetime.now(), status="Pagado")
			else:
				db(db.orders.id==order.id).update(invoice=invoiceid, confirmed_at=datetime.datetime.now(), status=paid)


			#actualizar datos contratos sobre forma de pago
			success_annotation=True
			accountingentry=AccountingEntry(db)


			for orderlist in db(db.orderlist.g_order==order.id).select():
				db((db.contractedproducts.user==order.user) & (db.contractedproducts.product==orderlist.product)).update(paymentmethod=order.payment_method)
				if paid!="Pendiente pago" and not manualinvoice:
					#anotar accountingentry
					success_annotation=accountingentry.annotation(orderlist, order)

				if not success_annotation:
					break
			if success_annotation:
				db.commit()
				return invoiceid
			else:
				db.rollback()
				return None
			
			
		except db._adapter.driver.IntegrityError:
			db.rollback()
			logger.debug("ERROR IntegrityError en INSERTINVOICE : %s" % ex)

			self.makeinvoice(order.id)
		except Exception, ex:
			logger.debug("ERROR en INSERTINVOICE: %s" % ex)
			db.rollback()
			return None

class Order(object):
	def __init__(self, db):
		self.db=db 
		Invoice(db)
		Budget(db)
		Paymentcode(db)
		try:
			self.define_tables()
		except:
			pass
	def define_tables(self):
		config= Settings()
		self.db.define_table('orders',
			Field('user','reference auth_user'),
			Field('invoice', 'reference invoices'),
			Field('budget','reference budgets', unique=True),
			Field('total', 'decimal(10,2)', default=0),#without taxes
			Field('totaltax','decimal(10,2)', default=0),
			Field('tax', 'decimal(10,2)',default=0),
			Field('ordered_at', 'datetime', default=datetime.datetime.now(), requires=IS_DATETIME()),
			Field('confirmed_at', 'datetime', requires=IS_DATETIME()), #fecha de pago confirmado o aprobado por administrador
			Field('confirmed_ip', 'string', notnull=False, length=32), #ip desde donde se ha realizado la confirmación
			Field('confirmed_by', 'reference auth_user'), #ip desde donde se ha realizado la confirmación			
			Field('request_send', 'datetime', requires=IS_DATETIME()), #fecha de envío de la petición de una confirmación de pedido
			Field('confirm_request', 'datetime', requires=IS_DATETIME()), #fecha de confirmación de un pedido
			Field('status', default="Creando", requires=IS_IN_SET(['Pagado', 'Pendiente pago', 'Creando', 'CreandoAdmin'], zero=None)),			
			Field('payment_method', default="Paypal", requires=IS_IN_SET(['Paypal', 'Transferencia', 'Domiciliación', 'Tarjeta'])),
			Field('payment_code','reference paymentcodes'),
			Field('note', 'text', notnull=False),
			Field('manual_operation', 'boolean', default=False),#indica que este pedido se ha realizado de forma manual desde el panel de administrador
			migrate=config.settings['migrate'])


class Orderlist(object):
	def __init__(self, db):
		
		self.db=db
		Order(db)	
		try:
			self.define_tables()
		except Exception as ex:
			logger.debug(ex)
			pass
	def define_tables(self):
		config=Settings()
		self.db.define_table('orderlist',
			Field('product','reference products'),
			Field('g_order', 'reference orders'),
			Field('quantity', 'integer', default=0, notnull=True),
			Field('price', 'decimal(10,2)'), #no incluye impuestos
			Field('price_wdto', 'decimal(10,2)'),
			Field('tax', 'decimal(10,2)'), #corresponde al 21% u otros.
			Field('dto', 'decimal(10,2)', default='0.00'),
			Field('dto_percentage', 'decimal(10,2)', default='0.00'),
			migrate=config.settings['migrate'])

class Budget(object):
	def __init__(self, db):
		self.db=db 
		Invoice(db)
		try:
			self.define_tables()
		except:
			pass
	def define_tables(self):
		config= Settings()
		self.db.define_table('budgets',
			Field('user','reference auth_user'),
			Field('invoice', 'reference invoices'),
			Field('total', 'decimal(10,2)'),#without taxes
			Field('totaltax','decimal(10,2)'),
			Field('tax', 'decimal(10,2)'),
			Field('created_at', 'datetime', default=datetime.datetime.now(), requires=IS_DATETIME()),
			Field('status', default="Creando", requires=IS_IN_SET(['Creando', 'Creado','Confirmado'], zero=None)),
			Field('confirmed_at', 'datetime', requires=IS_DATETIME()), #fecha de paso a factura
			Field('note', 'text', notnull=False),
			migrate=config.settings['migrate'])

class Budgetlist(object):
	def __init__(self, db):
		
		self.db=db
		Order(db)
		try:
			self.define_tables()
		except Exception as ex:
			logger.debug(ex)
			pass
	def define_tables(self):
		config=Settings()
		self.db.define_table('budgetlist',
			Field('product','reference products'),
			Field('g_budget', 'reference budgets'),
			Field('quantity', 'integer', default=0, notnull=True),
			Field('price', 'decimal(10,2)'), #no incluye impuestos
			Field('price_wdto', 'decimal(10,2)'),
			Field('tax', 'decimal(10,2)'), #corresponde al 21% u otros.
			Field('dto', 'decimal(10,2)', default='0.00'),
			Field('dto_percentage', 'decimal(10,2)', default='0.00'),
			migrate=config.settings['migrate'])

class Fiscal(object):

	def __init__(self, db):
		self.db=db
		try:
			self.define_tables()
		except Exception as ex:
			logger.debug(ex)
			pass
	def define_tables(self):
		config=Settings()
		self.db.define_table('fiscals',
			Field('user', 'reference auth_user'),
			Field('commercial', 'reference auth_user'),
			Field('tax_identification', 'string', length=45, notnull=True, requires=IS_NOT_EMPTY(error_message="es obligatorio CIF/NIF/NIE")),
			Field('fiscalname', 'string', length =128, notnull=False),
			Field('address', 'string', length =250, notnull=True, requires=IS_NOT_EMPTY()),
			Field('city', 'string', length =45, notnull=False),
			Field('province', 'string', length =45, notnull=False),
			Field('country', 'string', length =45, notnull=True, requires=IS_NOT_EMPTY()),
			Field('postal_code', 'string', length =10, notnull=False),
			Field('phone', 'string', length=20, notnull=False),
			migrate=config.settings['migrate'])


class CreditAccount(object):
	def __init__(self, db):
		self.db=db 
		try:
			self.define_tables()
		except Exception as ex:
			logger.debug(ex)
			pass
	def define_tables(self):
		config=Settings()
		db=self.db 
		db.define_table('creditaccounts',
			Field('user', 'reference auth_user'),
			Field('balance', 'decimal(10,2)'), #sin impuestos
			Field('modified_at', 'datetime', default=datetime.datetime.now(), requires=IS_DATETIME()),
			migrate=config.settings['migrate'])


class AccountingEntry(object):
	def __init__(self, db):
		self.db=db
		CreditAccount(db)
		Order(db)
		Orderlist(db)
		try:
			self.define_tables()
		except Exception as ex:
			logger.debug("AccountingEntry >>>> %s"%ex)
			pass
	def define_tables(self):
		config=Settings()
		self.db.define_table('accountingentries',
			Field('creditaccount', 'reference creditaccounts'),
			Field('orderlist', 'reference orderlist'),
			Field('total', 'decimal(10,2)'),
			Field('balance', 'decimal(10,2)'), #la última entrada debe coincidir con el balance de CreditAccount
			Field('annotated_at', 'datetime', default=datetime.datetime.now(), requires=IS_DATETIME()),
			Field('active', 'boolean', notnull=True, default=True),
			Field('deactivated_by', 'reference auth_user', notnull=False),
			Field('deactivated_at', 'datetime', notnull=False),
			migrate=config.settings['migrate'])

	def annotation(self, orderlist, order, positive=True):
		#anotar accountingentry
		#actualizar crédito
		db=self.db
		CreditAccount(db)
		try:
			
			creditaccount=db(db.creditaccounts.user==order.user).select().first()

			if not creditaccount:
				creditaccount_id=db.creditaccounts.insert(user=order.user, balance="0.00")
			else:
				creditaccount_id=creditaccount.id
			lastentry = db((db.accountingentries.creditaccount==creditaccount_id) &
							(db.accountingentries.active==True)).select(orderby=~db.accountingentries.id).first() #last
			total="%.2f" % float((-1,1)[positive] * (((orderlist.price_wdto * orderlist.tax)/100) + orderlist.price_wdto))
			if lastentry:
				balance="%.2f" % (float(lastentry.balance) + float(total))
			else:
				balance=total
			
			db.accountingentries.insert(creditaccount=creditaccount_id,
										orderlist=orderlist.id,
										total=total,
										balance=balance)
			db(db.creditaccounts.id==creditaccount_id).update(balance=balance, modified_at=datetime.datetime.now())
			db.commit()
			return True
		except Exception as ex:
			db.rollback()
			logger.debug("Annotation ERROR %s" %ex)
			return False

class Paymentcode(object):
	def __init__(self,db):
		self.db=db
		
		try:
			self.define_tables()
		except:
			pass
	def define_tables(self):
		config=Settings()
		self.db.define_table('paymentcodes',
		Field('code', 'string', unique=True, length=10),	#Es el código identificador de los pagos mediante transferencia bancaria provenientes del cliente
		migrate=config.settings['migrate'])

	#def loggingdata(self, data):


class Paypalrecord(object):
	def __init__(self,db):
		self.db=db
		Paymentcode(db)
		try:
			self.define_tables()
		except:
			pass
	def define_tables(self):
		
		#custom, corresponde a payment_code
		#subscr_id, este el id del suscriptor
		#payer_id
		#txn_type, "web_accept", "subscr_signup", "subscr_payment" 
		#txn_id, identificador de la operación
		#ipn_track_id, identificador IPN
		#payment_status, Completed
		
		config= Settings()
		self.db.define_table('paypalrecords',
			Field('payment_code', 'reference paymentcodes'), #custom
			Field('subscr_id', 'string', length=128, notnull=False),
			Field('payer_id', 'string', length=128, notnull=False),
			Field('txn_type', 'string', length=128, notnull=False),
			Field('txn_id', 'string', unique=True, length=128, notnull=False),
			Field('ipn_track_id', 'string', length=128, notnull=False),
			Field('payment_status', 'string', length=128, notnull=False),
			Field('payment_date', 'string', length=64),
			Field('created_at', 'datetime', notnull=True, default=datetime.datetime.now()),
			migrate=config.settings['migrate'])


