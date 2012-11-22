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
            TH('INICIO/FIN'),
            TH(),
            ),_class='table table-bordered table-condensed table-striped')

    for n,p in enumerate(data):

        # contando cantidad de tareas abiertas en el proyecto
        total_task = db((db.task.project_uuid==p.uuid)
                        &(db.task.closed==False)).count()
        
        project_list.append(TR(
                TD(A(TAG.i(_class='icon-white icon-tasks'),  
                     _href=URL(c='t', f='index.html', vars=dict(p=p.slug)), 
                     _class='btn btn-mini btn-primary' )),
                TD(STRONG(p.name.title()),BR(),T('Pendiente: '),SPAN(total_task, _class='badge badge-warning') if total_task else '--'),
                TD(DIV(DIV(_class="bar", 
                           _style="width: %s%%;" % total_progress(p.uuid)),
                       _class="progress progress-success")),

                TD(CAT(SPAN(p.start.date() if p.start else SPAN('Ø'),
                           _class='label label-info'),' ',
                       SPAN(p.end.date() if p.end else  SPAN('Ø'),
                           _class='label label-important')) \
                       ),

                

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
        project_closed = form.vars.close or ''

        #notificando por email
        p_contact = db(db.project.id==form.vars.id).select(
            db.project.email_contact, limitby=(0,1)).first().email_contact
        
        slug = IS_SLUG()(form.vars.name)[0]

        mail_msg = str(CAT(
            'PROYECTO: ', project_name, '\n',
            'OBJETIVO: ', project_aim or '---','\n',
            'INICIA: ', project_start or '---','\n',
            'TERMINA: ', project_end or '---','\n',
            'ENLACE: ', URL(c='t',f='index.html', vars={'p':slug}, host=True),'\n',
            ))

        
        project_closed_msg = '\b'
        if project_closed == True:
            project_closed_msg = '(CERRADO)'

        if p_contact:
            mail.send(
                to=p_contact,
                subject='%s Proyecto [%s]' % (project_closed_msg,project_name),
                message=mail_msg
                )

        if not request.ajax: redirect(URL(c='t',f='index.html',vars={'p':project_name}))
    elif form.errors:
        response.flash = "Hubo errores. Revise mensaje en formulario"
        response.js = 'jQuery(document).ready(function(){jQuery("#new_project").show();});'

    return dict(form=form)
