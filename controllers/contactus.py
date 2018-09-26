# -*- coding: utf-8 -*-
def index(): 
	from regnews import Regnews
	from mailboxing import Mailboxing
	from cities import Cities
	from province import Province
	from queuemail import Queuemail
	Province(db)
	Cities(db)
	Regnews(db)
	Mailboxing(db)
	Queuemail(db)
	

	wpoblacion = SQLFORM.widgets.autocomplete(request, db.cities.poblacion, limitby=(0,10), min_length=2)
	wprovincia = SQLFORM.widgets.autocomplete(request, db.province.provincia, limitby=(0,10), min_length=2)

	name = Field('name', 'string', label="Nombre", length=50, requires=IS_NOT_EMPTY(error_message="Debe identificarse con un nombre"), widget=lambda field,value: SQLFORM.widgets.string.widget(field, value, _placeholder='Nombre y apellidos'))
	email = Field('email', 'string', length=128, requires=[IS_NOT_EMPTY(error_message="Un email es requerido"), IS_EMAIL(error_message="email incorrecto")], widget=lambda field,value: SQLFORM.widgets.string.widget(field, value, _placeholder='ejemplo: mail@dominio.com'))
	phone = Field('phone', 'string', length=18, notnull=False)
	poblacion= Field('city', 'string', length=40, notnull=False, widget=wpoblacion)
	provincia= Field('province', 'string', length=40, notnull=False, widget=wprovincia)
	rnews = Field('rnews', 'boolean', default=True)
	message = Field('message', 'text', notnull=True, requires=IS_NOT_EMPTY(error_message="Por favor, díganos por qué quiere contactar con nosotros."))
	form = SQLFORM.factory(name, rnews, email, phone, poblacion, provincia, message, submit_button = 'contactar', formstyle='bootstrap')


	queuedata=[]
	if form.validate(keepvalues=False):
		data=form.vars
		try:

			reg=db(db.regnews.email==data.email).select()
			if len(reg)==0:
				id=db.regnews.insert(email=data.email, name=data.name, news=data.rnews, phone=data.phone, city=data.city, province=data.province)	
				db.mailbox.insert(regnews=id, message=data.message)
			else: 
				db.mailbox.insert(regnews=reg[0].id, message=data.message)
			db.commit()
		except:
			db.rollback()
			response.flash='Su petición de contacto no pudo registrarse. Inténtelo de nuevo.'
		#primero encolamos el mail al usuario que ha hecho la petición de contacto
		queuedata.append({'to': '%s'%data.email,
						'subject':'Confirmación de petición de contacto',
						'message':'Estimado %s,\n hemos recibido una petición de contacto por parte suya desde el formulario de contacto de Despacho Cifrado.\n\n Muchas gracias por su interés. Le responderemos en breve.\n\n Reciba un cordial saludo.\n--\nDespacho Cifrado' % data.name
						})
		#y ahora notificación a cada uno de los administradores
		mails=db(db.auth_membership.group_id==1).select(db.auth_membership.ALL, db.auth_user.ALL, left=db.auth_user.on(db.auth_membership.user_id==db.auth_user.id))
		for m in mails:
			queuedata.append({'to':'%s' % m.auth_user.email,
							'subject':'Tienes una solicitud de contacto',
							'message':'%s con mail: %s y teléfono: %s  te ha enviado el siguiente mensaje: \n %s ' %(data.name, data.email, data.phone, data.message)
							})							
		try:
			logger.debug(queuedata)
			queue.queuemessage(queuedata)
		except Exception, ex:
			logger.debug("error al almacenar la cola de mensajes %s" % ex)
			pass
		session.flash = 'Su petición ha sido registrada'
		redirect(URL(request.application,'default','index'))
		
	elif form.errors:

		response.flash = 'Revise los campos erróneos'

	return dict(form=form)