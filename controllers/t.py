# coding: utf8

@auth.requires_login()
def index():
    session.forget(response)
    project_id = None
    response.title = 'Tareas'
    response.subtitle = 'Todos los Proyectos'
    
    if request.vars.p:
        project = db(db.project.slug == request.vars.p
                        ).select(
                            db.project.id, 
                            limitby=(0,1)
                            ).first()
                            
        project_slug = str(request.vars.p).upper()
        
        if project:    
            project_id = project.id
    
            response.title = 'Proyecto '+project_slug
            response.subtitle = 'Tareas relacionadas'
    
        else:
            response.flash = 'No existe Proyecto "'+project_slug+'"'

    new_task = LOAD(f='new.load', vars={'p':project_id}, 
                    args=request.args, target='new_task_container',
                    _class='container-fluid', ajax=True, 
                    content=XML('Cargando Tareas... (Si no carga haga %s)' %
                    A('clic aquí', _href=URL(f='new.html'))))
    
    return dict(new_task=new_task)


@auth.requires_login()
def list():
    
    project_id = None
    project = db(db.project.slug == request.vars.p
                    ).select(db.project.id,limitby=(0,1)).first() 
    
    if project:
        project_id = project.id
        query = (db.task.project == project_id)
        
    else:
        query = (db.task)

    data = db(query).select(orderby=(db.task.created and ~db.task.priority),
                            )

    result = TABLE(THEAD(TR(TH('TID'),
        TH('Nombre'),
        #TH('Prior'),
        TH('Termina'),
        TH('Creado'),
        )), _class='table table-bordered')

    for task in data:
        
        fgcolor="none;"
        
        if task.priority=="5":
            bgcolor="#ef2929;"
        elif task.priority=="4":
            bgcolor="#fcaf3f;"
        elif task.priority=="3":
            bgcolor="#fce94f;"
        elif task.priority=="2":
            bgcolor="#d3d7cf;"
        elif task.priority=="1":
            bgcolor="#eeeeec;"       
        else:
            bgcolor="transparent;"
            
        result.append(TR(
                TD(A(task.id, _href=URL(f='new.html', args=task.id), 
                            _class='btn btn-inverse')),
                TD(TAG.sub(task.project.name),BR(),
                    A(task.name, _class='task_name', _rel='popover', 
                        **{'_data-original-title': task.name,
                            '_data-content': task.description}
                        ),BR(),
                        SPAN(task.state.name, _class='label')
                        ),
                #TD(),
                #TD(task.priority),
                TD(task.finish),
                TD(prettydate(task.created),BR(),'by '+str(task.author)),
                _style='background:'+bgcolor+'color:'+fgcolor)
                )
                
    return dict(result=result)

@auth.requires_login()
def new():

    db.task.author.default=db.auth_user[auth.user_id].email
    db.task.author.update=db.auth_user[auth.user_id].email
    
    if request.vars.p:
            db.task.project.default = request.vars.p
    
    form = SQLFORM(db.task, request.args(0))
    
    if form.process().accepted:
        if request.args:
            session.flash = 'Tarea modificada exitosamente'
            redirect(URL(c='t',f='index'))
        else:
            response.flash = 'Tarea '+str(form.vars.id)+' agregada exitosamente'
    elif form.errors:
        response.flash = 'Hubo errores al crear la Tarea. Revise formulario.'
    
        
    task_list = LOAD(f='list.load', args=request.args, vars=request.vars,
                    target='task_list_container', ajax=False,
                    _class='')
    
    return dict(form=form, task_list=task_list)
