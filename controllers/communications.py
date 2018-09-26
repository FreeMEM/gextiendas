# -*- coding: utf-8 -*-
@cache.action(time_expire=6000, cache_model=cache.ram, session=True, vars=True, public=True)
def prelaunch(): 
    request.requires_https()
    from regnews import Regnews
    from mailboxing import Mailboxing
    from queuemail import Queuemail
    from auxiliartools import AuxiliarTools
    auxiliar = AuxiliarTools(db)
    Regnews(db)
    Mailboxing(db)
    queue=Queuemail(db)
    
    email = Field('email', 'string', length=128, requires=[IS_NOT_EMPTY(error_message="Un email es requerido"), IS_EMAIL(error_message="email incorrecto")], widget=lambda field,value: SQLFORM.widgets.string.widget(field, value, _placeholder='ejemplo: mail@dominio.com'))
    form = SQLFORM.factory(email)
    form.element('input',_name='email')['_class']="form-control input-lg"
    form.element('input',_name='email')['_placeholder']="email"
    form.element('input',_type='submit')['_class']="btn btn-grove-one btn-lg btn-bold btn-block"
    form.element('input',_type='submit')['_value']="Quiero mi tienda"
    queuedata=[]

    if form.validate(keepvalues=True):

        data=form.vars
        try:
            reg=db(db.regnews.email==data.email).select()
            verification_code=auxiliar.generatecode()
            if len(reg)==0:
                db.regnews.insert(email=data.email, news=False, verification_code=verification_code, ip=request.client )
            else:
                db(db.regnews.email==data.email).update(news=False, verification_code=verification_code, ip=request.client)
            #primero encolamos el mail al usuario que ha hecho la petición de contacto
            urlconfirm = '%(scheme)s://%(host)s%(url)s' % {'scheme':request.env.wsgi_url_scheme,'host':request.env.http_host, 'url':URL('communications','mailcheck',args=['confirm',verification_code])}
            urlrefuse = '%(scheme)s://%(host)s%(url)s' % {'scheme':request.env.wsgi_url_scheme,'host':request.env.http_host, 'url':URL('communications','mailcheck',args=['refuse',verification_code])}
            
            html=   """
                    <p>Gracias por apuntarte al prelanzamiento de GEXtiendas.</p>
                    <p>Por favor, confirma tu petición clickando en el siguiente enlace:</p>
                    <p><a href='%(urlconfirm)s'>%(urlconfirm)s</a></p>
                    <p>o si por error, no eres el destinatario de este email, clicka en este otro para borrarte de nuestra lista:</p>
                    <p><a href='%(urlrefuse)s'>%(urlrefuse)s</a></p>
                    <h3>Estamos de prelanzamiento</h3>
                    <p>Como ya sabes, estamos a punto de poner en marcha nuestro sistema de gestión de tiendas electrónicas. Podrás crear y mantener gratuitamente cuantas tiendas electrónicas quieras. Si más adelante necesitas servicios profesionales, cuenta con nosotros a precios más ventajosos por el simple hecho de haber formado parte del proceso de prelanzamiento.</p>

                    <p>Esperamos que con nosotros, ganes mucho.</p>
                    """ % {"urlconfirm":urlconfirm, "urlrefuse":urlrefuse}

            queuedata.append({'to': '%s'%data.email,
                    'subject':'Confirmación de registro de email en Gextiendas',
                    'message':'Gracias por enviarnos tu dirección de correo electrónico.\nPor favor, confirma tu petición clickando en el siguiente enlace:\n%s\no si por error, no eres el destinatario de este email, clicka en este otro\n%s\n para borrarte de nuestra lista.\nComo ya sabes, estamos de prelanzamiento y estamos a punto de poner en marcha nuestro sistema de gestión de tiendas electrónicas. Podrás crear y mantener gratuitamente cuantas tiendas electrónicas quieras. Si más adelante necesitas servicios profesionales, cuenta con nosotros a precios más ventajosos por el simple hecho de haber formado parte del proceso de prelanzamiento.\n\nEsperamos que con nosotros, ganes mucho.\n--\nGextiendas' %(urlconfirm,urlrefuse),
                    'html':XML(html),
                    'unsubscribe':urlrefuse
                    })
            #y ahora notificación a cada uno de los administradores
            mails=db(db.auth_membership.group_id==1).select(db.auth_membership.ALL, db.auth_user.ALL, left=db.auth_user.on(db.auth_membership.user_id==db.auth_user.id))
            for m in mails:
                queuedata.append({'to':'%s' % m.auth_user.email,
                                'subject':'Tienes nuevos leads para la campaña de prelanzamiento: %s' % data.email,
                                'message':'Míralo en: %s' % "https://www.gextiendas.es/administrator/subscriptions"
                                })                          
            try:
                queue.queuemessage(queuedata)
            except Exception, ex:
                db.rollback()
                logger.debug("error al almacenar la cola de mensajes %s" % ex)
                response.flash='No hemos podido registrar tu email. Inténtalo de nuevo.'
                return dict(form=form)

            db.commit()
            session.flash = 'Su petición ha sido registrada'


        except Exception as ex:
            logger.debug("Error en Communication Prelaunch %s" %ex)
            db.rollback()
            response.flash='No hemos podido registrar tu email. Inténtalo de nuevo.'
        
        redirect(URL('successful'))        
    elif form.errors:
        logger.debug("lllllegggoooo33")
        response.flash = 'Revise los campos erróneos'
    else:
        logger.debug("lllllegggoooo33 %s" % form.vars)

    return dict(form=form)


def successful():
    return dict()


def mailcheck():
    request.requires_https()
    from regnews import Regnews
    Regnews(db)
    if request.args:
        if len(request.args)==2:
            datenow=datetime.datetime.now()
            if request.args[0]=="confirm":

                db(db.regnews.verification_code==request.args[1]).update(news=True, suscribed_on=datenow, verified_on=datenow)
            elif request.args[0]=="refuse":
                db(db.regnews.verification_code==request.args[1]).update(news=False, unsuscribed_on=datenow)

            db.commit()

            return dict(action=request.args[0])
        else:
            return dict(action="error")    
    else:
        return dict(action="error")
