@auth.requires_login()
def index():
	return dict()

@auth.requires_login()
def fiscal():
	from invoices import Fiscal
	from cities import Cities
	from province import Province
	Fiscal(db),	Province(db), Cities(db)
	
	fiscal=db(db.fiscals.user==auth.user_id).select().first()
	logger.debug(fiscal)
	wpoblacion = SQLFORM.widgets.autocomplete(request, db.cities.poblacion, limitby=(0,10), min_length=2)
	wprovincia = SQLFORM.widgets.autocomplete(request, db.province.provincia, limitby=(0,10), min_length=2)
	if request.vars.wizard:
		wizard=request.vars.wizard
	else:
		wizard=False
	if fiscal:
		tax_identification = Field('tax_identification', 'string', label=XML("<strong>NIF/CIF/NIE</strong> <span class='glyphicon glyphicon-question-sign'></span>"), default=fiscal.tax_identification,length=45, notnull=True, requires=IS_NOT_EMPTY(error_message="No olvide esta dato"))
		fiscalname=Field('fiscalname', 'string', label=XML("<strong>Nombre empresa</strong>"),default=fiscal.fiscalname,length =128, notnull=False)
		address=Field('address', 'string', label=XML("<strong>Dirección</strong>"), default=fiscal.address, length =250, notnull=True, requires=IS_NOT_EMPTY(error_message="no olvide este dato"))
		city= Field('city', 'string', label=XML("<strong>Ciudad/Población</strong>"), default=fiscal.city, length=45, notnull=True, requires=IS_NOT_EMPTY(error_message="no olvide este dato"), widget=wpoblacion)
		province = Field('province', 'string', label=XML("<strong>Provincia</strong>"), default=fiscal.province, notnull=False, widget=wprovincia)
		country=Field('country', 'string', label=XML("<strong>Pais</strong>"), length =45, default=fiscal.country, notnull=True, requires=IS_NOT_EMPTY(error_message="no olvide este dato"))
		postalcode=Field('postal_code', 'string', label=XML("<strong>Código postal</strong>"), default=fiscal.postal_code, length =10, notnull=True, requires=IS_NOT_EMPTY(error_message="no olvide este dato"))
		phone=Field('phone', 'string', label=XML("<strong>Teléfono de contacto</strong>"), length=20, default=fiscal.phone, notnull=False)
	else:
		tax_identification = Field('tax_identification', 'string', label=XML("<strong>NIF/CIF/NIE</strong> <span class='glyphicon glyphicon-question-sign'></span>"),length=45, notnull=True, requires=IS_NOT_EMPTY(error_message="No olvide esta dato"))
		fiscalname=Field('fiscalname', 'string', label=XML("<strong>Nombre empresa</strong>") ,length =128, notnull=False)
		address=Field('address', 'string', label=XML("<strong>Dirección</strong>"), length =196, notnull=True, requires=IS_NOT_EMPTY(error_message="no olvide este dato"))
		city= Field('city', 'string',   label=XML("<strong>Ciudad/Población</strong>"), length=45, notnull=True, requires=IS_NOT_EMPTY(error_message="no olvide este dato"), widget=wpoblacion)
		province = Field('province', 'string',   label=XML("<strong>Provincia</strong>"), length=45, notnull=False, widget=wprovincia)
		country=Field('country', 'string', label=XML("<strong>Pais</strong>"), length =45, notnull=True, requires=IS_NOT_EMPTY(error_message="no olvide este dato"))
		postalcode=Field('postal_code', 'string', label=XML("<strong>Código postal</strong>"), length=10, notnull=True, requires=IS_NOT_EMPTY(error_message="no olvide este dato"))
		phone=Field('phone', 'string', label=XML("<strong>Teléfono de contacto</strong>"), length=20, notnull=False)




	form = SQLFORM.factory(tax_identification, fiscalname, address, city, province, country, postalcode, phone, submit_button = ('enviar datos','siguiente')[wizard==True], formstyle='bootstrap3_inline')



	if form.validate(keepvalues=True):
		if fiscal: #update
			db(db.fiscals.id==fiscal.id).update(tax_identification=form.vars.tax_identification, 
												fiscalname=form.vars.fiscalname,
												address=form.vars.address, 
												city=form.vars.city,
												province=form.vars.province,
												country=form.vars.country, 
												postal_code=form.vars.postal_code,
												phone=form.vars.phone)
		else: #insert
			db.fiscals.insert(	user=auth.user_id,
								tax_identification=form.vars.tax_identification, 
								fiscalname=form.vars.fiscalname,
								address=form.vars.address, 
								city=form.vars.city,
								province=form.vars.province,
								country=form.vars.country, 
								postal_code=form.vars.postal_code,
								phone=form.vars.phone)
		session.flash="Datos enviados correctamente"
		if wizard:
			redirect(URL(request.application,'payment', 'index'))
		else:
			redirect(URL('account')) 

		

	elif form.errors:
		response.flash = 'Hay errores'

	form.element('input[name=city]')['_class']='form-control'
	form.element('input[name=province]')['_class']='form-control'
	form.element('div#no_table_tax_identification__row div.col-sm-9')['_class']='col-sm-3'
	form.element('div#no_table_fiscalname__row div.col-sm-9')['_class']='col-sm-4'
	form.element('div#no_table_city__row div.col-sm-9')['_class']='col-sm-4'
	form.element('div#no_table_province__row div.col-sm-9')['_class']='col-sm-3'
	form.element('div#no_table_country__row div.col-sm-9')['_class']='col-sm-2'
	form.element('div#no_table_postal_code__row div.col-sm-9')['_class']='col-sm-2'
	form.element('div#no_table_phone__row div.col-sm-9')['_class']='col-sm-4'
	# form.element('label.col-lg-2')['_class']='col-lg-3 control-label'
	# form.element('label.col-lg-2')['_class']='col-lg-3 control-label'
	# form.element('label.col-lg-2')['_class']='col-lg-3 control-label'
	# form.element('label.col-lg-2')['_class']='col-lg-3 control-label'
	# form.element('label.col-lg-2')['_class']='col-lg-3 control-label'
	# form.element('label.col-lg-2')['_class']='col-lg-3 control-label'
	# form.element('label.col-lg-2')['_class']='col-lg-3 control-label'
	# form.element('label.col-lg-2')['_class']='col-lg-3 control-label'


	return dict(form=form)
