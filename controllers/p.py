# coding: utf8
# This is the controller for "Projects".

@auth.requires_login()
def index():
    new_project = LOAD(c='p', f='new.load', args=request.args, ajax=True, target='new_project_container')
    return dict(new_project=new_project)


def list():
        
    data = db(db.project).select()

    project_list = TABLE(TR(
            TH('Nombre'),
            TH('Avance'),
            TH('Finaliza'),
            ),_class='table table-striped')

    for p in data:
        project_list.append(TR(
                TD(A(TAG.i(_class='icon-list icon-white'), ' %s' % p.name.title(), 
                     _href=URL(c='t', f='index.html', vars=dict(p=p.slug)), 
                     _class='btn btn-primary' ), A(TAG.i(_class='icon-edit'), 
                                                   _href=URL(c='p', f='new.html', 
                                                             args=p.id), _class='btn',
                                                   )
                   ),
                TD(DIV(DIV(_class="bar", 
                           _style="width: %s%%;" % total_progress(p.uuid)),
                       _class="progress")),
                TD(p.end or SPAN('Indefinido',_class='muted')),
                ))


    return dict(project_list=project_list)


#@auth.requires_login()
def new():
    #form = crud.update(db.project, request.args(0))
    form = SQLFORM(db.project, request.args(0))

    if form.process().accepted:
        response.flash = "Projecto registrado"
        
        #notificando por email
        p_contact = db(db.project.id==form.vars.id).select(
            db.project.email_contact, limitby=(0,1)).first().email_contact
        
        slug = IS_SLUG()(form.vars.name)[0]

        mail_msg = str(CAT(
            'PROYECTO: ', form.vars.name, '\n',
            'OBJETIVO: ', form.vars.aim, '\n',
            'INICIA: ', form.vars.start.date(), '\n',
            'TERMINA: ', form.vars.start.date(), '\n',
            'ENLACE ', URL(c='t',f='index.html', vars={'p':slug}, host=True),'\n',
            ))

        if p_contact:
            mail.send(
                to=p_contact,
                subject='Proyecto [%s]' % form.vars.name,
                message=mail_msg
                )

        if not request.ajax: redirect(URL(c='p',f='index'))
    elif form.errors:
        response.flash = "Hubo errores. Revise mensaje en formulario"
        response.js = 'jQuery(document).ready(function(){jQuery("#new_project").show();});'
 
    project_list = LOAD(f='list.load', ajax=True, target='project_list_container')

    return dict(form=form, project_list=project_list)
