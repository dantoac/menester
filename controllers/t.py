# coding: utf8

@auth.requires_login()
def index():
    session.forget(response)
    project_id = project_uuid = None
    response.title = 'Tareas'
    response.subtitle = 'Todos los Proyectos'
    progress=''

    if request.vars.p:
        project = db(db.project.slug == request.vars.p
                        ).select(
                            db.project.id, 
                            db.project.uuid,
                            limitby=(0,1)
                            ).first()
                            
        project_slug = str(request.vars.p).upper()
        
        if project:    
            project_uuid = project.uuid
            progress = total_progress(project_uuid)
            response.title = 'Tareas en '+project_slug
            response.subtitle = project_uuid
            request.vars.puuid = project_uuid
    
        else:
            response.flash = 'No existe Proyecto "'+project_slug+'"'


    new_task = LOAD(f='new.load', args=request.args, vars=request.vars,
                    target='new_task_container',
                    _class='container-fluid', ajax=True, 
                    content=XML('Cargando Tareas... (Si no carga haga %s)' %
                    A('clic aquí', _href=URL(f='new.html, vars=request.vars'))))
      


    return dict(progress=progress,new_task=new_task)


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
        
    data = db(query & query_task_state).select(db.task.ALL,
        orderby=(db.task.created and ~db.task.priority)
                                               )

    return dict(data=data)

@auth.requires_login()
def new():
    
    if request.vars.puuid:
        db.task.project_uuid.default = request.vars.puuid
        db.task.project_uuid.writable = False
        db.task.project_name.default = request.vars.p

    db.task.author.default = db.auth_user[auth.user_id].email

    form = SQLFORM(db.task, request.args(0))
    
    if form.process().accepted:
        if request.args:
            session.flash = 'Tarea modificada'
            if request.vars.p:
                redirect(URL(c='t',f='index',vars={'p':request.vars.p}))
            else:
                redirect(URL(c='t',f='index'))
        else:
            response.flash = 'Tarea '+str(form.vars.id)+' agregada exitosamente'
    elif form.errors:
        response.flash = 'Hubo errores al crear la Tarea. Revise formulario.'
        response.js = 'jQuery(document).ready(function(){jQuery("#new_task").show();});'
    
        
    task_list = LOAD(f='list.load', args=request.args, vars=request.vars,
                    target='task_list_container', ajax=False,
                    _class='')
    
    return dict(form=form, task_list=task_list)

