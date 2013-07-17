#encode: utf8

@auth.requires_login()
def index():
    
    request.vars.p

    if request.vars.p:

        query = (db.expense.project_uuid == request.vars.p) & (db.expense.project_uuid == db.project.uuid)
    else:
        query = db.expense.id>0

    dataset = db(query).select(db.expense.amount.sum(),
                               db.expense.due_date,
                               groupby=db.expense.due_date,
                               )

    # data = [(str(i.expense.due_date),i['SUM(expense.amount)']) for i in dataset]
    # meta_data_x = [d[0] for d in data]
    # data_x = "["
    # for m in meta_data_x:  data_x += '"%s",' % m
    # data_x+= "]"
    # data_y = [int(d[1]) for d in data]
    # chart_data = [data_x, data_y]



    return {#'chart_data':chart_data,
            'dataset':dataset}



@auth.requires_login()
def new():
        
    project_metadata = ''
    if request.vars.p and len(request.vars.p.strip()):

        project_metadata = db(db.project.uuid == request.vars.p).select(limitby=(0,1))     
        db.expense.project_uuid.default = request.vars.p
        db.expense.project_uuid.writable = False
        db.expense.project_uuid.readable = False
        query = (db.expense.project_uuid == request.vars.p) & (db.expense.project_uuid == db.project.uuid)
        select_fields = [db.expense.due_date,db.expense.amount, db.expense.subject, db.expense.done]
    else:
        query = (db.expense.id>0)
        db.expense.project_uuid.represent = lambda id,row: db(db.project.uuid == row.project_uuid).select(db.project.name, cacheable=True, limitby=(0,1)).first()['name']
        select_fields = [db.expense.project_uuid,db.expense.due_date,db.expense.amount, db.expense.subject, db.expense.done]

    """
    form = SQLFORM(db.expense,request.args(0))

    if form.process().accepted:
        if request.args(0):
            session.flash = 'Ingreso actualizado exitosamente'
            redirect(URL(f='new.load',vars=request.vars))
        else:
            response.flash = 'Ingreso registrado exitosamente'
    elif form.errors:
        response.flash = 'Error registrando el Ingreso. Revise el formulario'
    """

    form = SQLFORM.grid(query,
                        orderby=db.expense.due_date,
                        fields = select_fields,
                        details=False,
                        field_id = db.expense.id
    )

    #dataset = db(query).select(db.expense.amount, db.expense.due_date)
    

    dataset = db(query).select(db.expense.amount.sum(),
                               db.expense.due_date,
                               groupby=db.expense.due_date,
    )


    return {'form':form, 'dataset':dataset, 'project_metadata':project_metadata}








