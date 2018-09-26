# -*- coding: utf-8 -*-
from gluon import *
from gluon.globals import current
import logging, datetime, os, subprocess, simplejson
from applications.gextiendas.modules.settings import Settings
logger = logging.getLogger(" >>>> modules/queuemail >>>> Gextiendas: ")
logger.setLevel(logging.DEBUG)

class Queuemail(object):

	def __init__(self, db):
		self.db=db
		self.request = current.request

		try:
			self.define_tables()
		except Exception as ex:
			logger.debug(ex)
			pass
		
	def define_tables(self):
		config=Settings()
		self.db.define_table('queuemail',
			Field('status', 'boolean', notnull=True, default=False),
			Field('email', 'string', length=180),
			Field('subject', 'string', length=180),
			Field('message', 'text'),
			Field('html','text'),
			Field('unsubscribe', 'string', length=255),
			Field('template','string', length=255),
			Field('title','string', length=255),
			Field('created_on','datetime',default=datetime.datetime.now()),
			migrate=config.settings['migrate'])

	def queuemessage(self, queuedata):
		logger.debug(queuedata)
		for data in queuedata:

			
			self.db.queuemail.insert(status=False, 
									email=data['to'],
									subject=data['subject'],
									message=data['message'],
									html=(None,data.get("html"))[data.get("html")!=None],
									unsubscribe=(None,data.get("unsubscribe"))[data.get("unsubscribe")!=None],
									template=(None,data.get("template"))[data.get("template")!=None],
									title=(None,data.get("title"))[data.get("title")!=None]
									)
			
			
	def sendmessages(self):

		#http://web2py.com/examples/static/epydoc/web2py.gluon.tools.Mail-class.html
		from gluon.tools import Auth
		from applications.gextiendas.modules.settings import Settings
		from applications.gextiendas.modules.adminsettings import Adminsettings, Cifrar
		from applications.gextiendas.modules.regnews import Regnews


		config=Settings()
		auth = Auth(self.db)
		
		asettings=Adminsettings(self.db)
		try:
			asettings.define_tables()
		except:
			pass
		reg=Regnews(self.db)
		datasettings=self.db().select(self.db.adminsettings.ALL).first()

		mail=auth.settings.mailer
		if datasettings:
			mail.settings.server=datasettings.mailserver    # your SMTP server
			mail.settings.sender=datasettings.emailfrom         # your email
			mail.settings.login="%s:%s"%(datasettings.username, datasettings.password)      # your credentials or None

		fname=os.path.join(self.request.folder,'private',"queue_running.lock")
		
		try:
			if os.path.exists(fname):
				#os.utime(fname, None)

				stinfo= os.stat(fname)
				current_time = datetime.datetime.now()
				unix_timestamp = datetime.datetime.fromtimestamp(stinfo.st_mtime)
				minutos=datetime.timedelta(minutes=15)
				diferencia= current_time - unix_timestamp
				if diferencia>=minutos:
					logger.debug("Se ha superado el tiempo de envío de esta tarea. Se procede a quitar el bloqueo y cancelar la tarea, para que pueda lanzarse la tarea en el proximo cron")
					f = open(fname,'r')
					command = "kill -s 2 %s" % f.readline().replace('\n', '')
					logger.debug(command)
					f.close()
					kill = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
					(out, err) = kill.communicate()
					logger.debug(kill.wait())
					os.remove(fname)
				else:
					logger.debug("Se están enviando correos. A dormir y mirar queue en siguiente cron")
			else:
				logger.debug("Proceso para envío iniciado %s" % datetime.datetime.now())
				#se crea el fichero
				text_file=open(fname,'w')
				text_file.write("%s"%os.getpid())
				text_file.close()
				queuemsg = self.db(self.db.queuemail.status==False).select(self.db.queuemail.ALL)
				for q in queuemsg:
					#hago esta búsqueda redundante para evitar solapamientos con otros hilos y enviar el mismo email varias veces
					queue=self.db.queuemail(q.id)
					if queue.status==True:
						continue
					#fin de la búsqueda redundante
					if queue.html:
						context =dict(data_html=queue.html, title=queue.title, unsubscribe=queue.unsubscribe)
						logger.debug(context)
						msghtml= current.response.render(queue.template,context)
						message=(queue.message, msghtml)

					else:
						message=queue.message
					
					if mail.send(to='%s' % queue.email,
								subject='%s' % queue.subject,
								message=message):
						logger.debug("email enviado a %s" % queue.email)
						self.db(self.db.queuemail.id==queue.id).update(status=True)
						self.db.commit()
					else:

						if (simplejson.dumps(mail.error[0]).find('550') or simplejson.dumps(mail.error[0]).find('450')):
							self.db(self.db.regnews.email==queue.email).delete()
							self.db(self.db.queuemail.email==queue.email).delete()
						

				#procesados todos los msg del queumail, se borra el fichero de bloqueo
				os.remove(fname)
		except Exception as ex:
			logger.debug("Ocurrió el siguiente error en Queuemail.sendmessages: %s" % ex)
			if os.path.exists(fname):
				os.remove(fname)




# for persona in db(db.persona).select():
#     context = dict(persona=persona)
#     mensaje = response.render('mensaje.html', context)
#     mail.send(to=['quien@example.com'],
#               subject='None',
#               message=mensaje)
