# -*- coding: utf-8 -*-

## your http://google.com/analytics id
#response.google_analytics_id = "UA-51208654-1"
response.google_analytics_id = "UA-53108489-1"
response.title = settings.title
response.subtitle = settings.subtitle
response.meta.author = '%(author)s <%(author_email)s>' % settings
response.meta.keywords = settings.keywords
response.meta.description = settings.description

item_landingpage=[]

item_landingpage.append(('Inicio', request.controller == 'default', URL(request.application,'default','index'), []))
item_landingpage.append(('Blog', request.controller == 'blog', URL(request.application,'blog','index'), []))
item_landingpage.append(('Consigue tu tienda', request.controller == 'communications', URL(request.application,'communications','prelaunch'), []))
item_landingpage.append(('Precios', request.controller == 'prices', URL(request.application,'prices','index'), []))
item_landingpage.append(('Nosotros', request.controller == 'about', URL(request.application,'about','index'), []))
if auth.has_membership('administradores') or auth.has_membership('superadministradores'):
  item_landingpage.append(('Administrar', request.controller == 'administrator', URL(request.application,'administrator','bloglist'), []))
if auth.is_logged_in():
  item_landingpage.append(('Mi cuenta', request.controller == 'account', URL(request.application,'account','index'), []))
if auth.is_logged_in():
  item_landingpage.append(('Salir', request.controller == 'default', URL(request.application,'default','user/logout'), []))
#else:
#  item_landingpage.append(('Entra en tu cuenta', request.controller == 'default/user', URL(request.application,'default','user'), []))


if auth.has_membership('administradores') or auth.has_membership('superadministradores'):
  itemsadmin=[]
  itemsadmin.append(('Publicaciones del Blog', request.function == 'bloglist', URL(request.application,'administrator','bloglist'), []))
  itemsadmin.append(('Pedidos', request.function == 'orders', URL(request.application,'administrator','orders'), []))
  itemsadmin.append(('Contratos', request.function == 'contractedproducts', URL(request.application,'administrator','contractedproducts'), []))
  itemsadmin.append(('Productos/Tarifas', (request.function == 'products' or request.function=='priceplans' or request.function=='editproduct' or request.function=='editpriceplan'), URL(request.application,'administrator','products'), []))
  itemsadmin.append(('Facturación', request.function == 'billing' , URL(request.application,'administrator','billing'), []))
  itemsadmin.append(('Usuarios',(request.function == 'newinvoice') or (request.function == 'newbudget') or (request.function == 'neworder') or (request.function == 'viewbudget') or (request.function == 'vieworder') or (request.function == 'users') or (request.function=='editcustomer') or (request.function=='createcustomer') or (request.function=='viewinvoice')  , URL(request.application,'administrator','users'), []))
  # itemsadmin.append(('Consultas', request.function == 'clientqueries', URL(request.application,'administrator','clientqueries'), []))
  # itemsadmin.append(('Colas de emails', request.function == 'queuemails', URL(request.application,'administrator','queuemails'), []))
  itemsadmin.append(('Suscripciones', request.function == 'subscriptions', URL(request.application,'administrator','subscriptions'), []))
  itemsadmin.append(('Mensajes', request.function == 'emailbox', URL(request.application,'administrator','emailbox'), []))
  # itemsadmin.append(('Comunicaciones', request.function == 'communications', URL(request.application,'administrator','communications'), []))
  
  itemsadmin.append(('Configuración', request.function == 'settings', URL(request.application,'administrator','settings'), []))

  response.menuadmin=itemsadmin
  response.menu_landingpage = item_landingpage

  items_products=[]
  items_products.append(('Productos', request.function == 'products', URL(request.application,'administrator','products'), []))
  items_products.append(('Planes de precios', request.function == 'priceplans', URL(request.application,'administrator','priceplans'), []))
  items_products.append(('Perfiles de planes', request.function == 'profileplans', URL(request.application,'administrator','profileplans'), []))
  response.menu_products=items_products

  

if auth.has_membership('clientes') or auth.has_membership('administradores') or auth.has_membership('superadministradores'):
  item_account=[]
  item_account.append(('Tiendas', ((request.function == 'index') or (request.function == 'newshop')), URL(request.application,'account','index'), []))
  #item_account.append(('Seguridad', request.function == 'security', URL(request.application,'account','security'), []))
  #item_account.append(('Campañas', request.function == 'campaign', URL(request.application,'account','campaign'), []))
  #item_account.append(('LOPD/LSSICE', request.function == 'laws', URL(request.application,'account','laws'), []))
  item_account.append(('Mis datos', request.function == 'myaccount', URL(request.application,'account', 'myaccount'), []))
  item_account.append(('Mis servicios', request.function == 'myservices', URL(request.application,'account', 'myservices'), []))
  item_account.append(('Mi crédito/Facturas', (request.function == 'mycredit')  or (request.function == 'viewinvoice'), URL(request.application,'account', 'mycredit'), []))
  #item_account.append(('Preferencias', request.function == 'preferences', URL(request.application,'account','preferences'), []))
  #item_account.append(('Administrador de archivos', request.function == 'filemanager', URL(request.application,'account','filemanager'), []))
  response.menuaccount= item_account


response.menu_landingpage=item_landingpage