# -*- coding: utf-8 -*-

## if SSL/HTTPS is properly configured and you want all HTTP requests to
## be redirected to HTTPS, uncomment the line below:
# request.requires_https()

db = DAL(settings.mysql_uri,pool_size=10)

db = DAL(settings.mysql_uri,pool_size=10)
from auxiliartools import AuxiliarTools
auxiliartools=AuxiliarTools(db)

## by default give a view/generic.extension to all actions from localhost
## none otherwise. a pattern can be 'controller/function.extension'
response.generic_patterns = ['*'] if request.is_local else []
## (optional) optimize handling of static files

from gluon.tools import Auth, Crud, Service, PluginManager, prettydate, Mail
from seo import Seo

auth = Auth(db, hmac_key=Auth.get_or_create_key(), secure=True) #Fuerza https todo el sitio
#auth = Auth(db)
#crud, service, plugins = Crud(db), Service(), PluginManager()
service = Service()


metas=Seo(db)


## create all tables needed by auth if not custom tables
auth.define_tables(username=False, signature=False)

## configure email

if auth.is_logged_in():
	request.requires_https()
## after defining tables, uncomment below to enable auditing
# auth.enable_record_versioning(db)
mail=Mail(globals())
mail.settings.server = settings.email_server
mail.settings.sender = settings.email_sender
mail.settings.login = settings.email_login
auth.settings.mailer = mail

auth.settings.actions_disabled.append('profile')
auth.settings.formstyle='bootstrap3_inline'

#desactivo la creación de grupos automática
auth.settings.create_user_groups = False

if settings.data_migrate==True:
	from initdb import InitDB
	initdb=InitDB(db, auth)
	initdb.basicGroups()
	initdb.basicUsers()
	initdb.basicPricePlans()
	initdb.basicProducts()

## configure auth policy
#Auth. Configuración para registro, reset password y reset user.
auth.settings.remember_me_form = True
auth.messages.label_remember_me="Recuérdame"
auth.settings.long_expiration = 3600*24*365 # one year. Ha dejado de funcionar. Uso expiration en vez de long_expiration.
#auth.settings.expiration = 3600*24*365 # one year



auth.settings.register_onaccept.append(lambda form:mail.send(to=settings.author_email, subject='[gextiendas] Un nuevo usuario se ha registrado', message="La nueva cuenta de correo es %s" % form.vars.email))

auth.settings.registration_requires_verification = True
auth.settings.login_after_registration = True
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True



auth.messages.verify_email = auxiliartools.render_verifymail(request.vars.email, request.vars.first_name)
auth.messages.reset_password = auxiliartools.render_resetmail(request.vars.email)
auth.settings.register_onaccept = auxiliartools.set_membership(auth, 'clientes')


auth.messages.verify_email_subject = '[gextiendas.es] Verificación de email'
auth.messages.reset_password_subject = '[gextiendas.es] Password reset'
auth.messages.reset_password_log = '[gextiendas.es] User %(id)s Password reset'
auth.messages.label_reset_password_key = '[gextiendas.es] Reset Password key'

if auth.has_membership('administradores') or auth.has_membership('superadministradores'):
	auth.settings.login_next = URL(c='administrator', f='bloglist')
else:
	auth.settings.login_next = URL(c='account', f='index')
# auth.settings.login_next = URL('index')
auth.settings.logout_next = URL(c='default', f='index')
# auth.settings.profile_next = URL('index')
auth.settings.register_next = URL(c='verifyprocess', f='index')
# auth.settings.retrieve_username_next = URL('user', args='login')
auth.settings.retrieve_password_next = URL('index')
auth.settings.change_password_next = URL('index')
auth.settings.request_reset_password_next = URL(c='verifyprocess', f='requestreset')
auth.settings.reset_password_next = URL(c='app_dashboard', f='index')
auth.settings.verify_email_next = URL('verifyprocess', 'verified')
auth.messages.email_sent = 'Un email ha sido enviado a su cuenta'
auth.messages.password_changed = 'Su password ha sido modificado'

# auth.settings.register_onvalidation = set_membership(auth, 'profesionales')


from plugin_ckeditor import CKEditor
ckeditor = CKEditor(db)