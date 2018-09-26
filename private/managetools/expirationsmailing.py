# -*- coding: utf-8 -*-

#crontab 
#*/1 * * * * cd /home/gextiendas/web2py && /usr/bin/python web2py.py -S gextiendas -M -R applications/gextiendas/private/managedomains_contracts.py >> /tmp/manage_domains_contracts.out 2>&1

#Este cron busca dominios para activar/desactivar


client = SoapClient(wsdl="http://localhost:8000/internalgexcommerce/default/call/soap?WSDL=None")
# logger.debug(client.addShopSite(auth.user_id, ))

# la llamada al soap lo voy a trasladar al script que se llama desde el cron
# client = SoapClient(wsdl="http://localhost:8000/internalgexcommerce/default/call/soap?WSDL=None")
# logger.debug(client.addShopSite(auth.user_id))
#session.flash="En unos minutos recibirá un correo con los datos de su nueva instancia de tienda"