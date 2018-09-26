# -*- coding: utf-8 -*-

def index():
    from blog import Blog, Images
    Blog(db,ckeditor), Images(db)
    response.files.append(URL('static', 'js/vendor/layerslider/jquery-easing-1.3.js'))
    response.files.append(URL('static', 'js/vendor/layerslider/jquery-transit-modified.js'))
    #LayerSlider from Kreatura Media with Transitions 
    response.files.append(URL('static', 'js/vendor/layerslider/layerslider.transitions.js'))
    response.files.append(URL('static', 'js/vendor/layerslider/layerslider.kreaturamedia.jquery.js'))
    #Grove Layerslider initiation script
    response.files.append(URL('static', 'js/grove-slider.js'))
    return dict()


def user():
    #mientras estamos de lanzamiento
    # redirect(URL('communications', 'prelaunch'))
    request.requires_https()

    #if settings.prelaunch==True and not (auth.has_membership('administradores') or auth.has_membership('superadministradores')) :
    #    redirect(URL(request.application, 'communications','prelaunch'))
    auth.settings.formstyle = 'bootstrap3_inline'
    # if request.args(0) == 'logout':
    #     redirect('http://%(host)s' % {'host':request.env.http_host})
    if request.args(0) == 'login' and auth.is_logged_in():
        redirect(URL('account','index'))
    if request.args(0) == 'register':
        redirect(URL('default','register'))

    return dict(form=auth())

def register(): 
    if auth.is_logged_in():
        redirect(URL('account','index'))

    #mientras estemos de lanzamiento
    redirect(URL('communications', 'prelaunch'))

    request.requires_https()
    for field in ['first_name', 'last_name' ]:
        db.auth_user[field].readable = db.auth_user[field].writable = False
    return dict(form=auth.register())

@cache.action()
def download():
    return response.download(request, db)

def sitemap():
    # Import Os and Regex
    import os
    from gluon.myregex import regex_expose

    # Finding You Controllers 
    ctldir = os.path.join(request.folder,"controllers")
    ctls=os.listdir(ctldir)
    
    # Excluding The appadmin.py and the Manage.py
    if 'appadmin.py' in ctls: ctls.remove('appadmin.py')
    if 'manage.py' in ctls: ctls.remove('manage.py')

    # Adding  Schemas for the site map

    sitemap=TAG.urlset(_xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")

    # Add The Pages That You Dont want in the XML Sitemap
    ExcludedPages = ['edit', 'saved','delete','new','setpublic','user', 'publishing', 'preview','deletedraft','verified', 'requestreset', 'newform', 'download','handle_error','sitemap','register','google0ac0168ea35fcffb','BingSiteAuth','successful','mailcheck' ]
    ExcludedCtrl = ['administrator', 'plugin_ckeditor', 'verifyprocess', 'payment', 'myaccount', 'account', 'plans','payment','products']

    # Define Your Domain
    # urldomain = '%(scheme)s://www.gextiendas.es' % {'scheme':request.env.wsgi_url_scheme}
    urldomain = '%(scheme)s://%(host)s' % {'scheme':request.env.wsgi_url_scheme,'host':request.env.http_host}

    for ctl in ctls:
            if ctl.endswith(".bak") == False:

                if ctl.replace(".py","") not in ExcludedCtrl:
                    filename = os.path.join(ctldir,ctl)
                    data = open(filename, 'r').read()
                    functions = regex_expose.findall(data)
                    ctl = ctl[:-3].replace("_"," ")

                    # Adding Statics URLs From Your Controllers 
                    for f in functions:
                        # Ignore the Pages from the list above (  ExcludedPages )
                        if f not in ExcludedPages:
                             sitemap.append(TAG.url(TAG.loc('%s/%s/%s' % (urldomain, ctl,f.replace("_"," ")))))


    #  Dynamic URLs From Tables  For ex ... >> www.domain.com/post/1
    from blog import Blog, Images
    try:
        Blog(db,ckeditor)
        Images(db)
    except:
        pass
    posts = db(db.blog.public==True).select(db.blog.ALL, orderby=~db.blog.created_on)
    for item in posts:
        #sitemap.append(TAG.url(TAG.loc('%s/%s/blog/show/%s' % (urldomain, request.application,item.id))))
        sitemap.append(TAG.url(TAG.loc('%s/blog/show/%s' % (urldomain, item.urlfriendly))))
    
    return '<?xml version="1.0" encoding="UTF-8"?>\n%s' % sitemap.xml()



def handle_error():
    """ Custom error handler that returns correct status codes."""
    

    code = request.vars.code
    request_url = request.vars.request_url
    ticket = request.vars.ticket
    rlink=""
    if request.vars.request_url.find("app_")>=0:
        response.layout_path = "layout_acme.html"
        rlink=A('al dashboard', _href=URL(request.application, 'app_dashboard','index'))
    else:

        response.layout_path = "layout_biz.html"
        rlink=A('página principal', _href=URL(request.application, 'default','index'))


    ticket_url = "<a href='%(scheme)s://%(host)s/admin/default/ticket/%(ticket)s' target='_blank'>%(ticket)s</a>" % {'scheme':request.env.wsgi_url_scheme,'host':request.env.http_host,'ticket':ticket}

    if code is not None and request_url != request.url: # Make sure error url is not current url to avoid infinite loop.
        response.status = int(code) # Assign the error status code to the current response. (Must be integer to work.)
    if code == '403':

        return dict(code=code, error="Not authorized", ticket_url=ticket_url,  rlink=rlink)
    elif code == '404':

        return dict(code=code, error="Not found", ticket_url=ticket_url,  rlink=rlink)
    elif code == '500':

        # Get ticket URL:
        
 
        # Email a notice, etc:

        if settings.production==True:
            mail.send(to=['franciscotapias@gextiendas.es'],
                        subject="New Error",
                        message="Error Ticket:  %s" % ticket_url)
        
        return dict(code=code, error="Server error", ticket_url=ticket_url, rlink=rlink)
    
    else:
        return dict(code=code, error="Other error", ticket_url=ticket_url, rlink=rlink)


def google0ac0168ea35fcffb():
    
    return dict(siteverification="google-site-verification: google0ac0168ea35fcffb.html")

def BingSiteAuth():
    response.headers['content-type'] = 'text/xml'
    xml = request.body.read()  # retrieve the raw POST data
    if len(xml) == 0:
        xml = '<?xml version="1.0" ?><users><user>D8352F56DB33E5D0F03FFC2A51CCBFD3</user></users>'
    return response.render(dict(xml=XML(xml)))