# coding: utf8

@auth.requires_login()
def index():

    project_id = project_uuid = None
    project_slug = request.vars.p


    response.title = 'Tareas'
    response.subtitle = 'Todos los Proyectos'
    progress=''

    if request.vars.p:
        project = db(db.project.slug == project_slug
                        ).select(
                            db.project.id, 
                            db.project.name,
                            db.project.uuid,
                            db.project.aim,
                            limitby=(0,1)
                            ).first()
                            
        project_slug = str(request.vars.p).upper()
        
        if project:    
            project_uuid = project.uuid
            progress = total_progress(project_uuid)
            project_aim = project.aim
            project_name = project.name

            response.title += ' '+project_name
            response.subtitle = project_aim
            request.vars.puuid = project_uuid
    
        else:
            response.flash = 'No existe Proyecto "'+project_slug+'"'


    task_new = LOAD(f='new.load', args=request.args, 
                    vars=dict(p=request.vars.p,
                              puuid=request.vars.puuid),
                    target='task_new_container',
                    _class='container-fluid', ajax=True, 
                    content=XML('Cargando Tareas... (Si no carga haz %s)' %
                                A('clic aquí', _href=URL(f='list.html', 
                                                         vars=request.vars))),
                    )
      


    return dict(progress=progress,task_new=task_new)



def view():
    tid =  request.args(0)
    if not tid: return
    task = db.task[tid]
    if task: return dict(task=task)



@auth.requires_login()
def list():
    
    project_uuid = None

    project = db(db.project.slug == request.vars.p
                 ).select(db.project.uuid,limitby=(0,1)).first()
        
    #query Tareas en cualquier estado
    if request.vars.showstate == 'any':
        query_task_state = (db.task.id > 0)
    else:
        query_task_state = ((db.task.state <> 6) & 
                            (db.task.nullify == False))
    
    if project:
        project_uuid = project.uuid
        query = (db.task.project_uuid == project_uuid)
        
    else:
        query = (db.task.id > 0)
        
    data = db(query & query_task_state).select(
        db.task.id,
        db.task.name,
        db.task.progress,
        db.task.priority,
        db.task.created,
        db.task.author,
        db.task.nullify,
        db.task.tag,
        db.task.description,
        orderby=(db.task.created and ~db.task.priority))
    return dict(data=data)

@auth.requires_login()
def new():

    
    tid = request.args(0)

    if tid and db((db.task.id == tid) & (db.task.nullify==False)).isempty(): return
    
    if request.vars.puuid:
        db.task.project_uuid.default = request.vars.puuid
        db.task.project_name.default = request.vars.p
        

    db.task.author.default = db.auth_user[auth.user_id].email

    
    active_task = db((db.task.project_uuid == request.vars.puuid) 
                     & ~(db.task.id==tid)
                     & (db.task.nullify==False)
                     & (db.task.state != 6)
                     )
                     
    # listando sólo las tareas del respectivo proyecto
    ## parents
    db.task.task_parent.requires=IS_EMPTY_OR(IS_IN_DB(active_task, 
                                                      'task.uuid', '%(name)s'))

    ## childs
    db.task.task_child.requires=IS_EMPTY_OR(IS_IN_DB(active_task,
                                                     'task.uuid', '%(name)s'))
    
    form = SQLFORM(db.task, tid)
    
    if form.process().accepted:

        project_uuid = request.post_vars.project_uuid

        project_mail = db(db.project.uuid==project_uuid).select(
            db.project.email_contact, 
            db.project.name,
            limitby=(0,1)
            ).first()
          

        #notificando por email        
        if request.post_vars.notify:
            task_data = db(db.task.id==form.vars.id).select(
                db.task.progress, limitby=(0,1)).first()

            
            mail_subject = '[%(project_name)s #%(task_id)s] %(task_progress)s%% "%(task_name)s"' \
                % dict(project_name=project_mail.name,
                       task_name = form.vars.name,
                       task_progress = task_data.progress,
                       task_id = form.vars.id
                       )
            
            mail_msg = str(CAT(
                    'Enlace: ',URL('t','view.html',args=form.vars.id,
                                   vars={'p':project_mail.name},host=True),'\n',
                    'Tarea: ',form.vars.name,'\n',
                    'Prioridad: %s/5' % form.vars.priority,'\n',
                    'Tags: ', ','.join(form.vars.tag),'\n',
                    'Descripción: ', form.vars.description
                    ))
            
            if project_mail.email_contact:
                mail.send(
                    to=project_mail.email_contact,
                    subject=mail_subject,
                    message=mail_msg
                    )
    



        if request.vars.p:
            redirect(URL(c='t',f='index.html',vars={'p':request.vars.p}))
        else:
            redirect(URL(c='t',f='index'))

    elif form.errors:
        response.flash = 'Hubo errores al crear la Tarea. Revise formulario.'
        response.js = 'jQuery(document).ready(function(){jQuery("#task_new").show();});'
    
        
    task_list = LOAD(f='list.load', 
                     vars=dict(p=request.vars.p,
                               puuid=request.vars.puuid),
                     target='task_list_container', ajax=True,
                     )
    
    return dict(form=form, task_list=task_list)

