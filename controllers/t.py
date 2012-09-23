# coding: utf8

@auth.requires_login()
def index():
    session.forget(response)
    project_id = None
    response.title = 'Tareas'
    response.subtitle = 'Todos los Proyectos'
    progress=''

    if request.vars.p:
        project = db(db.project.slug == request.vars.p
                        ).select(
                            db.project.id, 
                            limitby=(0,1)
                            ).first()
                            
        project_slug = str(request.vars.p).upper()
        
        if project:    
            project_id = project.id
            progress = total_progress(project_id)
            response.title = 'Proyecto '+project_slug
            response.subtitle = 'Tareas relacionadas'
    
        else:
            response.flash = 'No existe Proyecto "'+project_slug+'"'

    new_task = LOAD(f='new.load', args=request.args, vars={'pid':project_id},
                    target='new_task_container',
                    _class='container-fluid', ajax=True, 
                    content=XML('Cargando Tareas... (Si no carga haga %s)' %
                    A('clic aquí', _href=URL(f='new.html, vars=request.vars'))))
    


    return dict(progress=progress,new_task=new_task)


@auth.requires_login()
def list():
    
    project_id = None

    project = db(db.project.slug == request.vars.p
                 ).select(db.project.id,limitby=(0,1)).first()
        
    #query Tareas en cualquier estado
    if request.vars.showstate == 'any':
        query_task_state = (db.task.state != None)
    else:
        query_task_state = (db.task.state <> 5)
    
    if project:
        project_id = project.id
        query = (db.task.project == project_id)
        
    else:
        query = (db.task.id > 0)

    data = db(query & query_task_state).select(
        orderby=(db.task.created and ~db.task.priority))

    result = TABLE(THEAD(TR(TH('#'),
        TH('Nombre'),
        TH('Progreso'),
        TH('Autor'),
        )), _class='table table-bordered table-condensed')

    for task in data:
        
        fgcolor="none;"
        
        if task.priority=="5":
            bgcolor="#ef2929;"
            priority_class = "error"
        elif task.priority=="4":
            bgcolor="#fcaf3f;"
            priority_class = "warning"
        elif task.priority=="3":
            bgcolor="#fce94f;"
            priority_class = "success"
        elif task.priority=="2":
            bgcolor="#d3d7cf;"
            priority_class = "info"
        elif task.priority=="1":
            bgcolor="#eeeeec;"  
            priority_class = ""
        else:
            bgcolor="transparent;"
            priority_class = ""


        taskname = task.name

        if task.state == 6:
            state_class = ""
            progress_css_class = ""
            taskname = TAG.DEL(task.name, _class="muted")
        elif task.state == 5:
            state_class = "label-inverted"
            progress_css_class = "progress  progress-striped"
        elif task.state == 4:
            state_class = "label-success"
            progress_css_class = "progress progress-success progress-striped"
        elif task.state == 3:
            state_class = "label-warning"
            progress_css_class = "progress progress-warning  progress-striped"
        elif task.state == 2:
            state_class = "label-info"
            progress_css_class = "progress progress-info  progress-striped"
        else:
            state_class = "label-important"
            progress_css_class = "progress progress-danger  progress-striped"
        
            


        result.append(TR(
                ## TID
                TD(A(task.id, _href=URL(f='new.html', args=task.id,
                                        vars=request.vars), 
                     _class='btn btn-mini')),

                ## TNAME
                TD(A(taskname, _class='task_name',
                     _rel='popover', **{'_data-original-title': '%s %s%%' % \
                                            (task.name,task.state.percentage),
                                        '_data-content': task.description}),
                   BR(), SPAN(task.state.name, _class='label %s' % state_class),
                   ),
  
                ## TPROGRESS
                TD(
                    DIV(DIV(_class='bar', 
                            _style='width:%s%%;' % task.state.percentage),
                        _class=' %s active' % progress_css_class)),
                
                ## TAUTHOR
                TD(str(task.author),BR(),prettydate(task.created)),
                #_style='background:'+bgcolor+'color:'+fgcolor)
                _class = priority_class)
                      )
                
    return dict(result=result)

@auth.requires_login()
def new():

    db.task.author.default=db.auth_user[auth.user_id].email
    db.task.author.update=db.auth_user[auth.user_id].email
    
    if request.vars.pid:
            db.task.project.default = request.vars.pid
    
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
    
        
    task_list = LOAD(f='list.load', args=request.args, vars=request.vars,
                    target='task_list_container', ajax=False,
                    _class='')
    
    return dict(form=form, task_list=task_list)

