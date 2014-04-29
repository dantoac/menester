# coding: utf8

@auth.requires(auth.has_membership('cdo') or auth.has_membership('admin'))
def index():

    project_id = project_uuid = None
    project_slug = request.vars.name
    project_uuid = request.vars.p

    progress=''

    if request.vars.p:
        project = db((db.project.uuid == project_uuid)
                     #| (db.project.slug == project_slug)
                        ).select(
                            db.project.id, 
                            db.project.name,
                            db.project.uuid,
                            db.project.aim,
                            db.project.close,
                            limitby=(0,1)
                            ).first()
                            
        project_slug = str(request.vars.name).upper()
        
        if project:    
            project_uuid = project.uuid
            
            project_aim = project.aim
            project_name = project.name

            response.title += ' '+project_name
            response.subtitle = project_aim
            request.vars.puuid = project_uuid

            if project.close:
                response.flash = 'Atención: este Proyecto está actualmente CERRADO '
    
        else:
            response.flash = 'No existe Proyecto "'+project_slug+'"'
     
    return {}


@auth.requires(auth.has_membership('cdo') or auth.has_membership('admin'))
def view():
    task = db.task(request.args(0)) or redirect(URL(c='t', f='index.html'))
    return dict(task=task)



@auth.requires(auth.has_membership('cdo') or auth.has_membership('admin'))
def list():

    this_week = week_dates()
    
    project_id = project_uuid = None
    project_slug = request.vars.name
    project_uuid = request.vars.p
    
    # para obtener el nombre del proyecto según slug (!)
    project = db((db.project.uuid == project_uuid)
                 #| (db.project.slug == project_slug)
                 ).select(db.project.uuid,
                          db.project.name,
                          limitby=(0,1)).first()
        
    #query Tareas en cualquier estado
    if request.get_vars.state == 'any':
        query_task_state = (db.task.id > 0)

    elif request.get_vars.state == 'active':

        query_task_state = ((db.task.progress != 100) & 
                    (db.task.closed != True) &
                    (db.task.nullify != True)                            
                    )

    # es lo mismo que un "else", pero mejor explícito a implícito...
    elif not request.get_vars.state or request.get_vars.state in ['week', 'None']:

        query_task_state = ((db.task.progress != 100) & 
                            (db.task.closed != True) &
                            (db.task.nullify != True) &
                            (db.task.finish >= this_week[0]) &
                            (db.task.finish <= this_week[-1])
                            )

    

    session.task_state = request.get_vars.state

    #project_uuid = None
    if project:
        project_uuid = project.uuid
        query_project = ((db.task.project_uuid == db.project.uuid) 
                         & (db.task.project_uuid == project_uuid))
        
    else:
        query_project = (db.task.project_uuid == db.project.uuid)
        

    #creando el dataset
    data = db((query_project)
              & (db.project.close == False)
              & (query_task_state) 
              ).select(
        db.task.ALL,
        db.project.name,
        db.project.uuid,
        db.project.slug,
        #db.comment.id.count(),
        #left=db.comment.on(db.task.uuid == db.comment.target_uuid),
        orderby=~db.task.priority|~db.task.progress|db.task.closed|db.task.nullify,
        groupby=db.task.id
        )


    data2 = db((query_project)
              & (query_task_state) 
              )._select(
        db.task.ALL,
        db.project.name,
        db.project.uuid,
        db.project.slug,
        #db.comment.id.count(),
        #left=db.comment.on(db.task.uuid == db.comment.target_uuid),
        orderby=~db.task.priority|~db.task.progress|db.task.closed|db.task.nullify,
        groupby=db.task.id
        )

    print(data2)

    return dict(data=data, this_week=this_week)

@auth.requires(auth.has_membership('cdo') or auth.has_membership('admin'))
def new():
    
    tid = request.args(0)

    if request.ajax: response.js = '$("#task_new_container").slideDown();'

    if tid and db((db.task.id == tid) & (db.task.nullify==False)).isempty(): return
       

    db.task.author.default = db.auth_user[auth.user_id].email

    
    active_task = ((db.task.project_uuid == request.vars.p) 
                     & ~(db.task.id==tid)
                     & (db.task.nullify==False)
                     & (db.task.progress < 100) #asi por retrocompatibilidad; debería ser task.closed==False;
                     )
                     
    # listando sólo las tareas del respectivo proyecto
    ## parents
    db.task.task_parent.requires=IS_EMPTY_OR(IS_IN_DB(db(active_task), 
                                                      'task.uuid', '%(name)s'))

    ## childs
    #db.task.task_child.requires=IS_EMPTY_OR(IS_IN_DB(db(active_task), 'task.uuid', '%(name)s'))
    
    form = SQLFORM(db.task, tid)

    form.vars.project_uuid = request.vars.p
    
    if form.process().accepted:

        project_data = db((db.project.uuid==form.vars.project_uuid)
                      ).select(
                          db.project.email_contact, 
                          db.project.name,
                          db.project.uuid,
                          limitby=(0,1)
                      ).first()
          

        #notificando por email        
        if request.post_vars.notify:
            
            
            task_progress = '[%s%%]' % form.vars.progress if int(form.vars.progress) < 100 else '[LOGRADO]'

            tags = form.vars.tag
            
            if not isinstance(form.vars.tag, basestring):
                tags = ', '.join(form.vars.tag)                

            mail_subject = '[MENESTER] #%(task_id)s: %(task_name)s' \
                % dict(task_id = form.vars.id,
                       task_name = form.vars.name,
                   )

            mail_msg = str(CAT(
                '\nProgreso: %s\n' % task_progress,
                'Termina: %s (%s)\n' % (form.vars.finish or '---', prettydate(form.vars.finish) or 'n/a'),
                'Prioridad: %s/5\n' % form.vars.priority,
                'Etiquetas: %s\n' % tags,
                'Enlace: %s\n' % URL('t','index.html',anchor=form.vars.id,vars={'p':project_data.uuid},host=True),
                'Proyecto: %s (%s%%)\n' % (project_data.name, total_progress(project_data.uuid)),
                '\nDescripción: \n%s\n' % form.vars.description or '---',
            ))
            
            if project_data.email_contact:
                mail.send(
                    to=project_data.email_contact,
                    subject=mail_subject,
                    message=mail_msg
                    )
    


        js_hideform = 'jQuery(document).ready(function(){jQuery("#task_new_container").slideUp();});'

        #if request.vars.p:
        response.js = 'web2py_component("%s", "task_list_container"); %s' % (URL(c='t',f='list.load',vars={'p': request.get_vars.p,'state': request.get_vars.state}),
                             js_hideform)

        #else:
        #    response.js = 'web2py_component("%s", "task_list_container");' % URL(c='t',f='list.load')
        
    elif form.errors:
        response.flash = 'Hubo errores al crear la Tarea. Revise formulario.'
        response.js = 'jQuery(document).ready(function(){jQuery("#task_new_container").show();});'



    return dict(form=form)

