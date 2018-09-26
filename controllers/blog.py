# coding: utf8

def index(): 
	from pagination import Pagination
	from blog import Blog, Images
	from comments import Comments
	from adminsettings import Adminsettings, Cifrar
	Adminsettings(db)
	Blog(db,ckeditor), Images(db)
	Comments(db)
	settings = db(db.adminsettings.id>0).select(db.adminsettings.ALL).first()
	session.publishing=False
	session.preview=False
	records=db(db.blog.id>0).count()
	items_per_page=settings.blogitems
	pag=Pagination(records, items_per_page)
	posts = db(db.blog.public==True).select(db.blog.ALL, orderby=~db.blog.id, limitby=pag.limitby(), cache=(cache.ram, 5), cacheable=True)
	lastposts = db(db.blog.public==True).select(db.blog.ALL, orderby=~db.blog.id, limitby=(0,10), cache=(cache.ram, 150), cacheable=True)
	
	return dict(posts=posts, pagination=pag, records=records, items_per_page=items_per_page, lastposts=lastposts)

def show():
	session.publishing=False
	from blog import Blog, Images
	from regnews import Regnews
	from comments import Comments

	from gluon.tools import Recaptcha

	Blog(db,ckeditor), Images(db)
	Regnews(db)	
	Comments(db)
	images=None
	if auth.has_membership('administradores') or auth.has_membership('superadministradores'):
		#logger.debug(session.preview)
		if not request.args(0):
			redirect(URL('blog','index'))			
		if session.preview:
			from blog import Draft
			Draft(db,ckeditor)
			if request.args(0).isdigit():

				post=db.draft(db.draft.id==request.args(0)) or redirect(URL('blog','index'))
			else:
				post=db.draft(db.draft.urlfriendly==request.args(0)) or redirect(URL('blog','index'))
		else:
			if request.args(0).isdigit():			
				post=db.blog(db.blog.id==request.args(0)) or redirect(URL('blog','index'))	
			else:
				post=db.blog(db.blog.urlfriendly==request.args(0)) or redirect(URL('blog','index'))	
	else:
		if not request.args(0):
			redirect(URL('blog','index'))
		if request.args(0).isdigit():			
			post=db.blog((db.blog.id==request.args(0)) & (db.blog.public==True) ) or redirect(URL('blog','index'))
		else:
			post=db.blog((db.blog.urlfriendly==request.args(0)) & (db.blog.public==True) ) or redirect(URL('blog','index'))
	if post.image!=None:
		images=db.images(post.image)
		#logger.debug(images)

	comment = Field('comment', 'text', label="Comentario",notnull=True, requires=IS_NOT_EMPTY(error_message="Debes escribir un comentario"))

	if auth.is_logged_in():
		form = SQLFORM.factory(comment, submit_button = 'Comentar', formstyle='bootstrap')
	else:
		name = Field('name', 'string', label="Nombre", length=50, requires=IS_NOT_EMPTY(error_message="Debe identificarse con un nombre"))
		email = Field('email', 'string', length=128, requires=IS_EMAIL(error_message="email incorrecto"))
		website = Field('website','string', length=128, widget=lambda field,value: SQLFORM.widgets.string.widget(field, value, _placeholder='Opcional'))
		rnews = Field('rnews', 'bool', default=True) 
		captcha = Recaptcha(request, '6Lf849gSAAAAAD2YgjNJxrelMp7-hPnTNZyyf4pD', '6Lf849gSAAAAAOgabgN9kc5YO1hhEws_un0btbbf',use_ssl=True, error_message='Inválido', label='Verificar:', options='theme:"clean", lang:"es"')
		# antispam= Field("anti_spam", widget=recaptcha, default='')		
		form = SQLFORM.factory(name, rnews, email, website, comment,  submit_button = 'Comentar')

		form[0].append(captcha)

	if form.errors.has_key('captcha'):
		response.flash='Captcha inválido'

	elif form.validate(keepvalues=False):
		data=form.vars

		try:
			if auth.is_logged_in():
				if request.args(0).isdigit():
					db.comments.insert(comment=data.comment, user=auth.user.id, blog=request.args(0))
				else:
					db.comments.insert(comment=data.comment, user=auth.user.id, blog=db(db.blog.urlfriendly==request.args(0)).select().first()["id"] )
			else:
				reg=db(db.regnews.email==data.email).select()
				if len(reg)==0:
					id=db.regnews.insert(email=data.email, name=data.name, news=data.rnews, website=data.website)
					if request.args(0).isdigit():
						db.comments.insert(comment=data.comment, blog=request.args(0), regnews=id)
					else:
						db.comments.insert(comment=data.comment, blog=db(db.blog.urlfriendly==request.args(0)).select().first()["id"], regnews=id)
				else: 
					if request.args(0).isdigit():
						db.comments.insert(comment=data.comment, blog=request.args(0), regnews=reg[0].id)
					else:
						db.comments.insert(comment=data.comment, blog=db(db.blog.urlfriendly==request.args(0)).select().first()["id"], regnews=reg[0].id)

			db.commit()
			response.flash = "Comentario publicado"
			
			#redirect(URL('blog','show', args=request.args(0)))
		except Exception, ex:
			logger.debug(ex)
			db.rollback()
			response.flash="Su comentario no se pudo enviar. Inténtelo de nuevo"
			
		# redirect(URL(request.application,'blog','list'))	
	elif form.errors:
		response.flash = 'Hay algunos errores'
	lastposts = db(db.blog.public==True).select(db.blog.ALL, orderby=~db.blog.id, limitby=(0,10), cache=(cache.ram, 150), cacheable=True)
	return dict(post=post, form=form, images=images, lastposts=lastposts)

@auth.requires_login()	
def edit():
	# response.files.append(URL('static', 'js/calendar.js'))
	if auth.has_membership('administradores') or auth.has_membership('superadministradores'):
		id=None
		data=request.vars
		
		images=None

		if data.draft!="None":

			from blog import Draft, Blog, Images
			Draft(db,ckeditor), Blog(db,ckeditor), Images(db)
			id=data.draft

			dbpost=db(db.draft.id==data.draft).select().first() or redirect(URL('blog','index'))

			title = Field('title', 'string',label=T("Title"), length=128, notnull=True, default= dbpost.title, requires=IS_NOT_EMPTY(error_message="El título no puede estar vacío"))
			subtitle = Field('subtitle', 'string',label=T("Subtitle"), length=128, notnull=True, default= dbpost.subtitle, requires=IS_NOT_EMPTY(error_message="El título no puede estar vacío"))
			post = Field('post', 'text', widget=ckeditor.widget, default=dbpost.post, requires=IS_NOT_EMPTY(error_message="El campo no puede estar vacío"))
			tags = Field('tags', 'string', label=T("Tags"), length=255, notnull=False, default=dbpost.tags)

			
			if dbpost.image==None:
				imagenormal = Field('image', 'upload', uploadfield=True, label="Imagen 750x500", uploadfolder=os.path.join(request.folder,'uploads'))				
				form = SQLFORM.factory(title, subtitle, imagenormal, post, tags, submit_button = 'Guardar borrador', table_name='images')
			else:
				images=db.images(dbpost.image) 
				form = SQLFORM.factory(title, subtitle, post, tags, submit_button = 'Guardar borrador')
			form.element('input[name=title]')['_class']='form-control'
			form.element('input[name=subtitle]')['_class']='form-control'
			form.element('input', _type='submit')['_class']="btn btn-primary"
			form.element('input[name=tags]')['_class']='form-control'
			form.element('input[name=tags]')['_placeholder']="etiquetas separadas por comas"
			
			draft=True
			
			if form.validate(keepvalues=True):
				
				if session.publishing==False:
					if form.vars.image:

						form.vars.id = db(db.draft.id==id).update(title=form.vars.title,
														subtitle=form.vars.subtitle,
														post=form.vars.post,
														image=__save_dbimage(form.vars.image),
														user=auth.user_id,
														tags=form.vars.tags,
														urlfriendly=IS_SLUG()(form.vars.title)[0])

					else:

						form.vars.id = db(db.draft.id==id).update(title=form.vars.title,
												subtitle=form.vars.subtitle,
												post=form.vars.post,
												user=auth.user_id,
												tags=form.vars.tags,
												urlfriendly=IS_SLUG()(form.vars.title)[0])

					db.commit()
					dbpost=db(db.draft.id==data.draft).select().first()
					images=db.images(dbpost.image)
					if session.preview==True:
						redirect(URL(request.application, 'blog', 'show',args=id))
				else:
					
					try:

						from blog import Blog
						Blog(db,ckeditor)
						dbdraft=db.draft(id)
						if dbdraft.blog!=None:
							
							bid=dbdraft.blog
							if form.vars.image:
								
								db(db.blog.id==dbdraft.blog).update(title=form.vars.title,
														subtitle=form.vars.subtitle,
														post=form.vars.post,
														image=__save_dbimage(form.vars.image),
														user=auth.user_id,														
														tags=form.vars.tags,
														urlfriendly=IS_SLUG()(form.vars.title)[0])
							else:
								db(db.blog.id==dbdraft.blog).update(title=form.vars.title,
														subtitle=form.vars.subtitle,
														post=form.vars.post,
														image=dbdraft.image,
														user=auth.user_id,
														tags=form.vars.tags,
														urlfriendly=IS_SLUG()(form.vars.title)[0])
							db(db.draft.id==id).delete()
							db.commit()
						else:
							if form.vars.image:
								bid=db.blog.insert(title=form.vars.title,
													subtitle=form.vars.subtitle,
													image=__save_dbimage(form.vars.image),
													post=form.vars.post,
													user=auth.user_id,
													tags=form.vars.tags,
													urlfriendly=IS_SLUG()(form.vars.title)[0])
							else:
								bid=db.blog.insert(title=form.vars.title,
													subtitle=form.vars.subtitle,
													image=db.draft(id).image,
													post=form.vars.post,
													user=auth.user_id,
													tags=form.vars.tags,
													urlfriendly=IS_SLUG()(form.vars.title)[0])
							db(db.draft.id==id).delete()
							db.commit()
						redirect(URL(request.application, 'blog','show', args=bid))
					except Exception as ex:
						logger.debug("%s" % ex)
						db.rollback()
						pass

				response.flash = 'Modificaciones guardadas'
			elif form.errors:
				response.flash = 'Hay algunos errores'

		elif data.blog!="None":
			from blog import Blog, Images
			Blog(db,ckeditor), Images(db)

			id=data.blog
			draft=False
			dbpost = db.blog(id) or redirect(URL('blog','index'))
			title = Field('title', 'string',label=T("Title"), length=128, notnull=True, default= dbpost.title, requires=IS_NOT_EMPTY(error_message="El título no puede estar vacío"))
			subtitle = Field('subtitle', 'string',label=T("Subtitle"), length=128, notnull=True, default= dbpost.subtitle, requires=IS_NOT_EMPTY(error_message="El título no puede estar vacío"))
			post = Field('post', 'text', widget=ckeditor.widget, default=dbpost.post, requires=IS_NOT_EMPTY(error_message="El campo no puede estar vacío")) 
			tags = Field('tags', 'string', label=T("Tags"), length=255, notnull=False, default=dbpost.tags)
			if dbpost.image==None:
				imagenormal = Field('image', 'upload', uploadfield=True, label="Imagen 750x500", uploadfolder=os.path.join(request.folder,'uploads'))				
				form = SQLFORM.factory(title, subtitle, imagenormal, post, tags, submit_button = 'Guardar', table_name='images')
			else:
				images=db.images(dbpost.image)
				form = SQLFORM.factory(title, subtitle, post, tags, submit_button = 'Guardar')

			form = SQLFORM.factory(title, subtitle, post, tags, submit_button = 'Modificar')
			form.element('input[name=title]')['_class']='form-control'
			form.element('input[name=subtitle]')['_class']='form-control'
			form.element('input', _type='submit')['_class']="btn btn-primary"
			form.element('input[name=tags]')['_class']='form-control'
			form.element('input[name=tags]')['_placeholder']="etiquetas separadas por comas"
			if form.validate(keepvalues=True):
				if session.preview:
					from blog import Draft
					Draft(db,ckeditor)

					dbdraft=db(db.draft.blog==id).select().first()

					form.vars['blog']=id

					if dbdraft!=None:
						draftid=dbdraft.id
						if form.vars.image:
							db(db.draft.blog==id).update(**dict(form.vars))
							db(db.draft.blog==id).update(urlfriendly=IS_SLUG()(form.vars.title)[0])
						
					else:
						
						if form.vars.image:
							draftid=db.draft.insert(title=form.vars.title,
													subtitle=form.vars.subtitle,
													image=__save_dbimage(form.vars.image),
													post=form.vars.post,
													user=auth.user_id,
													tags=form.vars.tags,
													urlfriendly=IS_SLUG()(form.vars.title)[0])
						else:
							draftid=db.draft.insert(title=form.vars.title,
												subtitle=form.vars.subtitle,
												image=dbpost.image,
												post=form.vars.post,
												user=auth.user_id,
												tags=form.vars.tags,
												urlfriendly=IS_SLUG()(form.vars.title)[0])

					db.commit()
					session.flash="Vista previa"
					redirect(URL(request.application, 'blog','show', args=draftid))

				else:
					db(db.blog.id==id).update(**dict(form.vars))
					db(db.blog.id==id).update(urlfriendly=IS_SLUG()(form.vars.title)[0])
					db.commit()
				response.flash = 'Modificaciones guardadas'
			elif form.errors:
				response.flash = 'Hay algunos errores'
		return dict(form=form,id=id, draft=draft, images=images)
	else:
		redirect(URL(request.application,'blog','index'))

@auth.requires_login()	
def preview():
	if auth.has_membership('administradores') or auth.has_membership('superadministradores'):
		session.publishing=False
		session.preview=True
		return "OK"
@auth.requires_login()	
def publishing():
	if auth.has_membership('administradores') or auth.has_membership('superadministradores'):
		session.publishing=True
		session.preview=False
		return "OK"

@auth.requires_login()
def delete():
	if auth.has_membership('administradores') or auth.has_membership('superadministradores'):
		from blog import Blog
		Blog(db,ckeditor)
		
		try:
			db(db.blog.id==request.args(0)).delete()
			session.flash="Publicación borrada"
			return "OK"
		except:
			return "FAIL"
	else:
		redirect(URL(request.application,'blog','index'))
@auth.requires_login()
def deletedraft():
	if auth.has_membership('administradores') or auth.has_membership('superadministradores'):
		from blog import Draft
		Draft(db,ckeditor)
		
		try:
			db(db.draft.id==request.args(0)).delete()
			session.flash="Borrador eliminado"
			return "OK"
		except:
			return "FAIL"
	else:
		redirect(URL(request.application,'blog','index'))

@auth.requires_login()
def new(): 

	session.imageid=None
	from blog import Draft, Images
	session.preview=False
	if auth.has_membership('administradores') or auth.has_membership('superadministradores'):


		Images(db)
		draft=Draft(db,ckeditor)
		
		title = Field('title', 'string',label=T("Title"), length=128, notnull=True, requires=IS_NOT_EMPTY(error_message="El campo no puede estar vacío"))
		subtitle = Field('subtitle', 'string',label=T("Subtitle"), length=128, notnull=True, requires=IS_NOT_EMPTY(error_message="El campo no puede estar vacío"))
		post = Field('post', 'text', widget=ckeditor.widget, requires=IS_NOT_EMPTY(error_message="El campo no puede estar vacío"))
		tags = Field('tags', 'string', label=T("Tags"), length=255, notnull=False)
		imagenormal = Field('image', 'upload', uploadfield=True, label="Imagen 750x500", uploadfolder=os.path.join(request.folder,'uploads'))
		

		form = SQLFORM.factory(title, subtitle, imagenormal, post, tags, submit_button = 'Guardar borrador', table_name='images')

		form.element('input[name=title]')['_class']='form-control'
		form.element('input[name=subtitle]')['_class']='form-control'
		form.element('input[name=tags]')['_class']='form-control'
		form.element('input[name=tags]')['_placeholder']="etiquetas separadas por comas"
		
		form.element('input', _type='submit')['_class']="btn btn-primary"
		# if form.accepts(request.vars, session, keepvalues=True, onvalidation=__form_insert_processing):
		if form.validate(keepvalues=False):
			if form.vars.image:
				#form.vars.id = db.draft.insert(**dict(form.vars))
				
				form.vars.id = db.draft.insert(title=form.vars.title,
												subtitle=form.vars.subtitle,
												post=form.vars.post,
												image=__save_dbimage(form.vars.image),
												user=auth.user_id,
												tags=form.vars.tags,
												urlfriendly=IS_SLUG()(form.vars.title)[0])
			else:
				form.vars.id = db.draft.insert(title=form.vars.title,
											subtitle=form.vars.subtitle,
											post=form.vars.post,
											user=auth.user_id,
											tags=form.vars.tags,
											urlfriendly=IS_SLUG()(form.vars.title)[0])
			db.commit()
			session.flash = 'Publicación creada'
			redirect(URL('blog','edit', vars=dict(draft=form.vars.id, blog=None)))
			# redirect(URL(request.application,'blog','list'))	
		elif form.errors:
			response.flash = 'Hay algunos errores'
		return dict(form=form)
	else:
		redirect(URL(request.application,'blog','index'))



@auth.requires_login()
def setpublic():

	if auth.has_membership('administradores') or auth.has_membership('superadministradores'):
		from blog import Blog
		Blog(db,ckeditor)

		data=request.vars
		try:
			db(db.blog.id==data.id).update(public=data.public)
			return "true"
		except:
			return "false"
	else:
		redirect(URL(request.application,'blog','index'))


@cache.action()
def download():
	from blog import Draft, Blog, Images
	Draft(db,ckeditor), Blog(db,ckeditor), Images(db)

	return response.download(request, db)

def __save_dbimage(fname):
	from PIL import Image
	import re
	#creamos los nombres de los ficheros
	immobile_fname=re.sub(".image.",".imagemobile.",fname) 
	immini_fname=re.sub(".image.",".imagemini.",fname) 

	#y comenzamos
	im=Image.open(os.path.join(os.path.join(request.folder,'uploads'),fname)) #750x370
	immobile=Image.open(os.path.join(os.path.join(request.folder,'uploads'),fname)) #470x232
	immini=Image.open(os.path.join(os.path.join(request.folder,'uploads'),fname)) #263x179
	if im.format!="JPEG" and im.format!="PNG":
		response.flash="El fichero debe ser un jpeg o un png"
	if im.size[0]!=750:
		im=im.resize((750,int((im.size[1]*750)/im.size[0])))
		
	if immobile.size[0]!=470:
	 	immobile=immobile.resize((470,int((immobile.size[1]*470)/immobile.size[0])))
	 	
	if immini.size[0]!=263:
		immini=immini.resize((263,int((immini.size[1]*263)/immini.size[0])))
		
	im.save(os.path.join(os.path.join(request.folder,'uploads'),fname), "JPEG", quality=80, optimize=True, progressive=True )
	immobile.save(os.path.join(os.path.join(request.folder,'uploads'),immobile_fname), "JPEG", quality=80, optimize=True, progressive=True)
	immini.save(os.path.join(os.path.join(request.folder,'uploads'),immini_fname), "JPEG", quality=80, optimize=True, progressive=True)

	#guardamos en la bbdd los nombres de fichero
	return db.images.insert(image=fname, imagemobile=immobile_fname, imagemini=immini_fname)