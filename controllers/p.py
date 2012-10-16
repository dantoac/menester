# coding: utf8
# This is the controller for "Projects".

@auth.requires_login()
def index():
    return dict()


def list():
        
    #query proyectos en cualquier estado
    if request.vars.state == 'any':
        query_project_state = (db.project.id > 0)
    else:
        query_project_state = ((db.project.close == None) | (db.project.close != True))
                                   
    data = db(query_project_state).select()

    project_list = TABLE(TR(
            TH(''),
            TH('NOMBRE'),
            TH('PROGRESO'),
            TH('INICIO'),
            TH('FIN'),
            TH(),
            ),_class='table table-bordered table-condensed table-striped')

    for n,p in enumerate(data):
        project_list.append(TR(
                TD(A(TAG.i(_class='icon-white icon-tasks'),  
                     _href=URL(c='t', f='index.html', vars=dict(p=p.slug)), 
                     _class='btn btn-mini btn-primary' )),
                TD(STRONG(p.name.title())),
                TD(DIV(DIV(_class="bar", 
                           _style="width: %s%%;" % total_progress(p.uuid)),
                       _class="progress progress-success")),

                TD(CAT(p.start.date(),BR(),
                       TAG.SMALL(prettydate(p.start), _class='')) \
                       if p.start else  SPAN('Indefinido',_class='muted')),

                TD(p.end.date() if p.end else  SPAN('Indefinido',_class='muted')),

                # Actualizar projecto
                TD(A(TAG.i(_class='icon-edit icon-white'),  
                     _href=URL(c='p', f='new.load', args=p.id),
                     _class='btn btn-mini btn-inverse',
                     cid="new_project"),
                   ),
                
                ))


    return dict(project_list=project_list)


#@auth.requires_login()
def new():
    #form = crud.update(db.project, request.args(0))
    form = SQLFORM(db.project, request.args(0))

    if form.process().accepted:
        response.flash = "Projecto registrado"
        
        project_aim = form.vars.aim or ''
        project_name = form.vars.name or ''
        project_start = form.vars.start.date() if form.vars.start else ''
        project_end = form.vars.end.date() if form.vars.end else ''

        #notificando por email
        p_contact = db(db.project.id==form.vars.id).select(
            db.project.email_contact, limitby=(0,1)).first().email_contact
        
        slug = IS_SLUG()(form.vars.name)[0]

        mail_msg = str(CAT(
            'PROYECTO: ', project_name, '\n',
            'OBJETIVO: ', project_aim, '\n',
            'INICIA: ', project_start, '\n',
            'TERMINA: ', project_end, '\n',
            'ENLACE ', URL(c='t',f='index.html', vars={'p':slug}, host=True),'\n',
            ))

        if p_contact:
            mail.send(
                to=p_contact,
                subject='Proyecto [%s]' % project_name,
                message=mail_msg
                )

        if not request.ajax: redirect(URL(c='t',f='index.html',vars={'p':project_name}))
    elif form.errors:
        response.flash = "Hubo errores. Revise mensaje en formulario"
        response.js = 'jQuery(document).ready(function(){jQuery("#new_project").show();});'

    return dict(form=form)
