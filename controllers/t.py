# coding: utf8


def index():
    
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
                    _class='container', ajax=True, 
                    content=XML('Cargando Tareas... (Si no carga haga %s)' %
                    A('clic aquí', _href=URL(f='new.html'))))
    
    return dict(new_task=new_task)



def list():
    project_id = None
    project = db(db.project.slug == request.vars.p
                    ).select(db.project.id,limitby=(0,1)).first() 
    
    if project:
        project_id = project.id
        query = (db.task.project == project_id)
        
    else:
        query = (db.task)

    data = db(query).select(orderby=~db.task.priority)

    result = TABLE(THEAD(TR(TH('TID'),
        TH('Nombre'),
        TH('Estado'),
        TH('Prioridad'),
        TH('Termina'),
        TH('Creado'),
        )), _class='table table-bordered')

    for n,task in enumerate(data):
        n+=1
        fgcolor="none;"
        if task.priority==10:
            bgcolor="#a40000;"
            fgcolor="#fff"
        elif task.priority==9:
            bgcolor = "#cc0000;"
            fgcolor="#fff"
        elif task.priority==8:
            bgcolor = "#ef2929;"
            fgcolor="#fff"
        elif task.priority==7:
            bgcolor = "#ce5c00;"
            fgcolor="#fff"
        elif task.priority==6:
            bgcolor="#f57900;"
            fgcolor="#fff"
        elif task.priority==5:
            bgcolor="#c4a000;"
   
        elif task.priority==4:
            bgcolor="#fcaf3e;"
   
        elif task.priority==3:
            bgcolor="#edd400;"
        elif task.priority==2:
            bgcolor="#fce94f;"
        elif task.priority==1:
            bgcolor="#ffff00;"
        elif task.priority==0:
            bgcolor="#eeeeec;"
        else:
            bgcolor="transparent;"
            fgcolor="#000;"
            
        result.append(TR(TD(A(task.id, _href=URL(f='new.html', args=task.id), 
                            _class='btn btn-inverse')),
                TD(SPAN(TAG.sub(task.project.name),BR(),task.name)),
                TD(SPAN(task.state.name,_class='label')),
                TD(task.priority),
                TD(task.finish),
                TD(prettydate(task.created)),
                _style='background:'+bgcolor+'color:'+fgcolor))
    return dict(result=result)


def new():
    
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
                    _class='center')
    
    return dict(form=form, task_list=task_list)
