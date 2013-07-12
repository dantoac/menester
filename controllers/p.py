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
                                   
    dataset = db(query_project_state).select(orderby=~db.project.id)
           
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

    open_task_dataset = db((db.task.project_uuid==db.project.uuid)
                    & (db.task.closed==False)
                ).select(db.project.uuid, 
                         db.task.id.count(), 
                         groupby=db.project.uuid)
        
    open_task = Storage({t.project.uuid:t['COUNT(task.id)'] for t in open_task_dataset})
   
    return {'dataset':dataset, 
            'project_income':project_income,
            'project_expense':project_expense,
            'open_task':open_task
    }

@auth.requires_login()
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

        if request.ajax: redirect(URL(c='p',f='new.load',args=form.vars.id))
    elif form.errors:
        response.flash = "Hubo errores. Revise mensaje en formulario"
        response.js = 'jQuery(document).ready(function(){jQuery("#new_project").show();});'

    return dict(form=form)
