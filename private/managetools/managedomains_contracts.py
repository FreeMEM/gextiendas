# -*- coding: utf-8 -*-

#crontab 
#*/1 * * * * cd /home/gextiendas/web2py && /usr/bin/python web2py.py -S gextiendas -M -R applications/gextiendas/private/managetools/managedomains_contracts.py >> /tmp/manage_domains_contracts.out 2>&1


#este cron busca dominios para activar/desactivar en tiendas


# client = SoapClient(wsdl="http://localhost:8000/internalgexcommerce/default/call/soap?WSDL=None")

# client = SoapClient(wsdl="http://localhost:8000/internalgexcommerce/default/call/soap?WSDL=None")
# logger.debug(client.addShopSite(auth.user_id))

#buscar contratos cuya fecha de expiración sea NULL o >= CURRENT_DATE() y plan distinto de NULL o free

from gluon import *
from shops import ContractedProduct, Product, PricePlan, Shop
from invoices import Order, Orderlist
contract=ContractedProduct(db)
Product(db), PricePlan(db), Shop(db), Orderlist(db), Order(db)

mcontracts=db(	((db.contractedproducts.expiration == None) | (db.contractedproducts.expiration >= datetime.datetime.now())) &
				(	(db.profileplans.active==True) &
					(db.priceplans.planname!="free") & 
					(db.contractedproducts.active==True)
				)
			).select(db.contractedproducts.ALL,
					 db.products.plan,
					 db.products.price,
					 db.products.suscription,
					 db.products.name,
					 db.priceplans.planname,
					 db.priceplans.id,
					 db.profileplans.ALL,
					 db.orders.ALL,
					 left=[	db.products.on(db.products.id==db.contractedproducts.product),
					 		db.profileplans.on(db.profileplans.product==db.products.id),
					 		db.priceplans.on(db.priceplans.id==db.profileplans.priceplan),
					 		db.orderlist.on(db.orderlist.id==db.contractedproducts.orderlist),
					 		db.orders.on(db.orders.id==db.orderlist.g_order)])
logger.debug(db(	((db.contractedproducts.expiration == None) | (db.contractedproducts.expiration >= datetime.datetime.now())) &
				(	(db.profileplans.active==True) &
					(db.priceplans.planname!="free") & 
					(db.contractedproducts.active==True)
				)
			)._select(db.contractedproducts.id,
					 db.products.plan,
					 db.products.name,
					 db.priceplans.planname,
					 db.priceplans.id,
					 db.profileplans.id,
					 db.orders.id,
					 left=[	db.products.on(db.products.id==db.contractedproducts.product),
					 		db.profileplans.on(db.profileplans.product==db.products.id),
					 		db.priceplans.on(db.priceplans.id==db.profileplans.id),
					 		db.orderlist.on(db.orderlist.id==db.contractedproducts.orderlist),
					 		db.orders.on(db.orders.id==db.orderlist.g_order)]))

for cont in mcontracts:
	contract.managecontract(cont)
