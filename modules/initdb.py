# -*- coding: utf-8 -*-
from gluon import *
import logging
logger = logging.getLogger(" >>>> modules/initDB >>>> GestionExperta: ")
logger.setLevel(logging.DEBUG)

class InitDB(object):
	def __init__(self, db, auth):
		self.db=db
		self.auth=auth

	def basicGroups(self):
		if self.db(self.db.auth_group).isempty():
			self.db.auth_group.insert(role="superadministradores", description="superadministrador del sistema, por el momento sólo exite uno")
			self.db.auth_group.insert(role="administradores", description="administradores del sistema")
			self.db.auth_group.insert(role="profesionales", description="Colaboradores legales, diseñadores externos, programadores externos")
			self.db.auth_group.insert(role="comerciales", description="Comerciales")
			self.db.auth_group.insert(role="clientes", description="Usuarios de las tiendas")
			self.db.commit()
	def basicUsers(self):
		if self.db(self.db.auth_user).isempty():
			id=self.db.auth_user.insert(first_name='First Name', last_name='Last Name', email='email@email.com', password='password')
			self.db.auth_membership.insert(user_id=id, group_id=self.db(self.db.auth_group.role=='superadministradores').select(self.db.auth_group.id)[0].id)
			self.db.commit()
	def basicPricePlans(self):
		from shops import PricePlan
		db=self.db
		PricePlan(db)
		if db(db.priceplans).isempty():
			db.priceplans.insert(planname='Gratuito', paymode='free')
			db.priceplans.insert(planname='Paga si vendes', 
								paymode='ifselling', 
								explanation=XML('<p>El plan <strong> "Paga si vendes" </strong> te permite usar el servicio de tienda con <strong>tus propios dominios habilitados para disfrutar de la multitienda, sin pagar ninguna cuota de suscripción mensual</strong>. Sólo te cobraremos si vendes, a razón de 2€ por venta y un límite de gasto mensual de 40€. Estas cantidades las iremos descontando de tu cuenta de crédito, que a continuación deberás cargar mediante tarjeta, transferencia bancaria o domiciliación bancaria (estos últimos dos métodos sólo para Europa). Si en algún momento deseas cambiar de plan podrás utilizar tu crédito restante.</p><p>Si tu cuenta se queda a cero, podrás seguir usando el servicio hasta el fin de los 30 días del periodo correspondiente. A partir de ese momento, si no dispones de crédito, el servicio volverá al plan "gratuíto" sin perder ningún dato de tu tienda, ni productos, ventas, clientes, ni aspecto, todo seguirá igual, salvo que tendrás que volver a habilitar tu dominio recargando crédito o contratando cualquier plan de tarifa plana.</p><p>De forma opcional, aunque altamente recomendable, deberías tener un certificado digital SSL para asegurar las comunicaciones, las transacciones y dar confianza a tus clientes. Nosotros te lo podemos gestionar y mantener anualmente por 10€, para que no tengas que preocuparte. Si te pasas a algún plan de tarifa plana, te lo reembolsaremos. Si quieres instalarte y gestionar por tu cuenta el certificado, también podrás hacerlo, te daremos las herramientas y la interfaz para hacerlo.</p><p>Los precios aquí detallados <strong>no incluyen IVA</strong></p>')
								)
			db.priceplans.insert(planname='Tarifa plana',
								explanation=XML('<p>El plan <strong> "Tarifa plana" </strong> te permite usar el servicio de tienda online<strong> sin ningún tipo de comisiones de venta.</strong> Sólo te cobraremos una suscripción mensual de 28,90€. Este servicio te permite habilitar tus propios dominios para disfrutar del sistema multitienda. Si en algún momento deseas cambiarte a un plan superior, te descontaremos del nuevo precio el mes que ya estás disfrutando. Podrás deshabilitar el dominio o darte de baja definitivamente del servicio en cuyo caso se borrarán los contenidos y bases de datos de tu tienda, cuando termines de disfrutar el tiempo contratado.</p><p>Si decides cambiar a un plan inferior, como "Paga si vendes", se descontará la parte proporcional de lo disfrutado y se te abonará al precio del nuevo plan. Si decides cambiarte al plan "Gratuíto", podrás disfrutar del antiguo plan hasta que terminen los días contratados. Te cambies al plan que te cambies no perderás datos de tu tienda, ni productos, ventas, clientes, ni aspecto, todo seguirá igual, salvo la posibilidad o no de usar el dominio.</p><p>De forma opcional, vamos a regalarte un certificado digital SSL y su gestión mientras mantengas la suscripción. Es opcional, porque quizá quieras gestionarlo tú mismo y contratar la firma de una Autoridad Certificadora de tu confianza; a tu elección. En cualquier caso te daremos las herramientas y la interfaz para gestionar e instalar los certificados por tí mismo.</p><p>Los precios aquí detallados <strong>no incluyen IVA</strong></p>'))
			db.priceplans.insert(planname='Seguro')
			db.priceplans.insert(planname='Asistido')
			db.priceplans.insert(planname='Posicionado')
			db.priceplans.insert(planname='Difusión')
	def basicProducts(self):
		from shops import Product, PricePlan, ProfilePlan
		db=self.db
		Product(db), PricePlan(db), ProfilePlan(db)
		if db(db.products).isempty():
			db.products.insert(	name="Tarifa plana", 
								price="18.00", 
								plan=3,
								min_period="month",
								description="Vende lo que quieras y paga siempre lo mismo. Con certificado SSL incluído.")
			db.products.insert(	name="Carga crédito mínimo 'Paga si vendes'",
								price="40.00",
								plan=2,
								suscription=False,
								description="Para que si se disparan tus ventas, controles tu gasto con un límite de 40€")									
			db.products.insert(	name="Plan Asistido", 
								price="199.00", 
								plan=4,
								min_period="month",
								description="Con asistencia telefónica y Comunity Management Básico incluído todos los meses")
			db.products.insert(	name="Plan Difusión", 
								price="399.00", 
								plan=6,
								min_period="month",
								description="Community Management Avanzado mes a mes")
			db.products.insert(	name="Certificado SSL",
								min_period="year",
								price="15.00")
			db.products.insert( name="Certificado SSL (Planes por Suscripción)",
								min_period="year",
								price="0.00")
			db.products.insert(	name="Pack iniciación", 
								price="450.00",
								suscription=False,
								description="incluye la modificación de la plantilla para la inserción de logotipos y de imágenes de productos en Slider de presentación, compuesto por tres imágenes completamente montadas para promoción de tres artículos o servicios.")			
			db.products.insert(	name="Asistencia telefónica bono 5h", 
								price="210.00",
								suscription=False,
								description="Por si necesitas algo más, que la asistencia incluída en tu plan")
			db.products.insert(	name="Asistencia telefónica bono 10h", 
								price="380.00",
								suscription=False,
								description="Por si necesitas algo más, que la asistencia incluída en tu plan")
			db.products.insert(	name="Asistencia telefónica bono 15h", 
								price="480.00",
								suscription=False,
								description="Por si necesitas algo más, que la asistencia incluída en tu plan")
			db.products.insert(	name="Pack video corporativo",
								suscription=False,
								price="150.00",
								description="Filmación profesional en vídeo del negocio físico o productos para la creación de un video corporativo de aproximadamente 50 segundos una vez editado, asi como sesión de fotos profesional de artículos (de 10 a 15 tomas)")
			db.products.insert(	name="Community Management Básico", 
								price="200.00",
								description="Creación de identidad digital y un mes de difusión/discusión semanal en Facebook y twitter sobre productos y servicios.")
			db.products.insert(	name="Community Management Avanzado",
								price="300.00",
								description="Creación de identidad digital  y un mes de difusión/discusión semanal en Facebook, Twitter, Google+ y blog de empresa, sobre productos y servicios.")
			db.products.insert(	name="Facebook Social Management",
								price="60.00",
								description="Dos entradas semanales en Facebook")
			db.products.insert(	name="Twitter Social Management",
								price="60.00",
								description="Dos tweets semanales")
			db.products.insert(	name="Blog Social Management",
								price="80.00",
								description="Una entrada semanal en Blog")
			db.products.insert(	name="Google+ Social Management",
								price="60.00",
								description="Dos entradas semanales en tu comunidad Google+")
			db.products.insert(	name="Campaña SEO", 
								price="250.00",
								suscription=False,
								description="Análisis, adecuación de la tienda y puesta en marcha de estrategia.")
			db.products.insert(	name="SEM en Google adwords express", 
								price="130.00",
								active=False,
								suscription=False,
								description="Colocación y monitorización del anuncio y creación del Landing Page")
			db.products.insert(	name="SEM en Google adwords", 
								price="130.00",
								active=False,
								suscription=False,
								description="Colocación y monitorización del anuncio y creación del Landing Page")
			db.products.insert(	name="Ads en Facebook", 
								price="130.00",
								active=False,
								suscription=False,
								description="Colocación y monitorización del anuncio y creación del Landing Page")
			db.products.insert(	name="SEM en Bing", 
								price="130.00",
								active=False,
								suscription=False,
								description="Colocación y monitorización del anuncio y creación del Landing Page")
			db.products.insert(	name="Servicio de introducción de productos en tu catálogo", 
								price="28.00",
								suscription=False,
								description="Añadimos los productos que desees y su información relacionada: SEO, categoría, asociaciones, atributos y valores, marca del producto, ilustración del producto, marca de agua, 3 imágenes por artículo, existencias, administrar proveedor, tags.")

			db.products.insert(	name="Adecuación LOPD", 
								price="140.00",
								suscription=False,
								active=False,
								description="Para que cumplas con la Ley Orgánica de protección de datos, adecuamos tu tienda, desarrollamos el documento de seguridad, los contratos de acceso a datos por parte de terceros (asesorías, seguros, informáticos), te facilitamos toda la documentación relacionada y registramos los ficheros de datos personales en la Agencia de Protección de Datos. Además te damos un año de consultoría legal sobre LOPD totalmente gratis")
			
			db.products.insert(	name="Adecuación LSSICE", 
								price="60.00",
								suscription=False,
								active=False,
								description="Adaptamos su tienda para que cumpla la Ley de Servicios de la Sociedad de la Información y Comercio Electrónico, de obligado cumplimiento.")

			db.profileplans.insert(	product=db(db.products.name=="Carga crédito mínimo 'Paga si vendes'").select().first()['id'],
									priceplan=db(db.priceplans.planname=="Paga si vendes").select().first()['id'])

			db.profileplans.insert(	product=db(db.products.name=="Certificado SSL").select().first()['id'],
									priceplan=db(db.priceplans.planname=="Paga si vendes").select().first()['id'])

			db.profileplans.insert(	product=db(db.products.name=="Tarifa Plana").select().first()['id'],
									priceplan=db(db.priceplans.planname=="Tarifa plana").select().first()['id'])

			db.profileplans.insert(	product=db(db.products.name=="Certificado SSL (Planes por Suscripción)").select().first()['id'],
									priceplan=db(db.priceplans.planname=="Tarifa plana").select().first()['id'])
