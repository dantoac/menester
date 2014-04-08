# coding: utf8
# This is the controller for "Projects".



@cache.action(time_expire=300, cache_model=cache.ram, session=True, vars=True, public=True)
def progress():
    '''
    Esta función esta disponible como API para mostrar al Cliente el
    porcentaje de avance en el proyecto.
    '''

    project = db(db.project.uuid == request.vars.p).select().first()
    
    #if not project: raise HTTP(404)
    
    progress = total_progress(project.uuid if project else None)

    open_tasks = _open_task(request.vars.p)
    
    response.headers['Access-Control-Allow-Origin'] = '*'

    return {
        'progress':progress, 
        'name': project.name if project else None,
        'open_task_count': open_tasks
    }



@auth.requires_membership('admin')
def index():
    return dict()

@auth.requires_membership('admin')
def aoeu():
            
    dataset = db.project

    open_task_dataset = db((db.task.project_uuid==db.project.uuid)
                           & (db.task.closed==False)
                       ).select(db.project.uuid, 
                                db.task.id.count(), 
                                groupby=db.project.uuid)
    
    open_task = Storage({t.project.uuid:t['COUNT(task.id)'] for t in open_task_dataset})


    db.project.name.represent = lambda name,r: CAT(A(r.name, 
                                                     _href=URL(args=['edit','project',r.id], user_signature=True),
                                                     _class='btn btn-large btn-block {0}'.format('btn-success' if r.close else 'btn-danger')),

                                                   DIV(
                                                       A(TAG.i(_class='icon icon-arrow-down'),
                                                                   T('Ingresos'),
                                                                   _href= URL(c='i',f='index',vars={'p':r.uuid}),
                                                                   _class='btn'),
                                                       A(TAG.i(_class='icon icon-arrow-up'),
                                                                   T('Egresos'),
                                                                   _href= URL(c='e',f='index',vars={'p':r.uuid}),
                                                                   _class='btn'),
                                                       A(TAG.i(_class='icon icon-tasks'),
                                                                   T('Tareas'),
                                                                   _href= URL(c='t',f='index',vars={'p':r.uuid}),
                                                                   _class='btn'),
                                                       _class='btn-group'),
                                                   DIV(
                                                       DIV('Comienza: ', prettydate(r.start)),
                                                       DIV('Finaliza: ', prettydate(r.end)),
                                                       _class='well well-small'
                                                   )
                                               )

    db.project.start.readable = False
    db.project.end.readable = False
    db.project.close.readable = False


    grid = SQLFORM.grid(dataset, orderby=db.project.close|~db.project.created_on|~db.project.modified_on,
                        fields = [db.project.name,
                                  db.project.uuid,
                                  db.project.start,
                                  db.project.end,
                                  db.project.close,
                                  ], 
                        details=False, deletable=True, editable=True,
                        paginate = 10,
                        links = [
                            lambda r: XML('''
                            <div id="project-chart-%(id)s"></div>
                            <script>
                            new Morris.Line({
                            element: 'project-chart-%(id)s',
                            data: %(data)s,
                            xkey: 'y',
                            ykeys: ['a','b','c'],
                            labels: ['Ingresos','Egresos','Utilidades'],
                            lineColors: ['#007bcc','#d64b46','#4e9a06']
                            });
                            </script>
                            ''' % {'id':r.id, 'data':flux(r.uuid)})
                        ]
    )
   
    return {'projects': grid}


@auth.requires_membership('admin')
def list():
        
    #query proyectos en cualquier estado
    if request.vars.state == 'any':
        query_project_state = (db.project.id > 0)
    else:
        query_project_state = ((db.project.close == None) | (db.project.close != True))
                                   
    dataset = db(query_project_state).select(orderby=~db.project.modified_on)

           
    income_dataset = db((db.income.project_uuid == db.project.uuid)
                        & (db.income.done == True)).select(
                            db.project.uuid, 
                            db.income.amount.sum(),
                            groupby=db.project.uuid
                        )

    expense_dataset = db((db.expense.project_uuid == db.project.uuid)
                         & (db.expense.done==True)
                     ).select(
                         db.project.uuid, 
                         db.expense.amount.sum(),
                         groupby=db.project.uuid
                     )

    project_income = Storage({i.project.uuid:i['SUM(income.amount)'] for i in income_dataset})
    project_expense = Storage({i.project.uuid:i['SUM(expense.amount)'] for i in expense_dataset})
   
    return {'dataset':dataset, 
            'project_income':project_income,
            'project_expense':project_expense,
    }

@auth.requires_membership('admin')
def new():
    #form = crud.update(db.project, request.args(0))

    db.project.uuid.readable = True
    form = SQLFORM(db.project, request.args(0))

    if form.process().accepted:
        response.flash = "Projecto registrado"
        
        project_aim = form.vars.aim or ''
        project_name = form.vars.name or ''
        project_start = form.vars.start.date() if form.vars.start else ''
        project_end = form.vars.end.date() if form.vars.end else ''
        project_closed = form.vars.close or ''

        #notificando por email
        
        mail_msg = str(CAT(
            'Objetivo: %s\n' % project_aim or '---',
            'Finaliza: {0} ({1})\n'.format(project_end or '---', prettydate(project_end) or '---'),
            'Tareas: %s\n' % URL(c='t',f='index.html', vars={'p':request.post_vars.uuid}, host=True),
            ))

        
        project_closed_msg = '\b' #retrocede el cursor
        if project_closed == True:
            project_closed_msg = '<CERRADO>'

        if form.vars.email_contact:
            mail.send(
                to=form.vars.email_contact,
                subject='[MENESTER] %s [%s%%] %s' % (project_name, 
                                                      total_progress(request.post_vars.uuid),
                                                      project_closed_msg),
                message=mail_msg
                )

        if request.ajax: 
            redirect(URL(c='p',f='list.load'))
    elif form.errors:
        response.flash = "Hubo errores. Revise mensaje en formulario"
        response.js = 'jQuery(document).ready(function(){jQuery("#new_project").show();});'

    return dict(form=form)
