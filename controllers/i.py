#encode: utf8

@auth.requires_membership('admin')
def index():
    
    request.vars.p

    if request.vars.p:

        query = (db.income.project_uuid == request.vars.p) & (db.income.project_uuid == db.project.uuid)
    else:
        query = db.income.id>0

    dataset = db(query).select(db.income.amount.sum(),
                               db.income.due_date,
                               groupby=db.income.due_date,
                               )

    # data = [(str(i.income.due_date),i['SUM(income.amount)']) for i in dataset]
    # meta_data_x = [d[0] for d in data]
    # data_x = "["
    # for m in meta_data_x:  data_x += '"%s",' % m
    # data_x+= "]"
    # data_y = [int(d[1]) for d in data]
    # chart_data = [data_x, data_y]



    return {#'chart_data':chart_data,
            'dataset':dataset}



@auth.requires_membership('admin')
def new():
        
    project_metadata = ''
    if request.vars.p and len(request.vars.p.strip()):

        project_metadata = db(db.project.uuid == request.vars.p).select(limitby=(0,1))     
        db.income.project_uuid.default = request.vars.p
        db.income.project_uuid.writable = False
        db.income.project_uuid.readable = False
        query = (db.income.project_uuid == request.vars.p) & (db.income.project_uuid == db.project.uuid)
        select_fields = [db.income.due_date,db.income.amount, db.income.subject, db.income.done]
    else:
        query = (db.income.id>0)
        db.income.project_uuid.represent = lambda id,row: db(db.project.uuid == row.project_uuid).select(db.project.name, cacheable=True, limitby=(0,1)).first()['name']
        select_fields = [db.income.project_uuid,db.income.due_date,db.income.amount, db.income.subject, db.income.done]

    """
    form = SQLFORM(db.income,request.args(0))

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
                        orderby=~db.income.due_date,
                        fields = select_fields,
                        details=False,
                        field_id = db.income.id
    )

    #dataset = db(query).select(db.income.amount, db.income.due_date)
    

    dataset = db(query).select(db.income.amount.sum(),
                               db.income.due_date,
                               groupby=db.income.due_date,
    )


    return {'form':form, 'dataset':dataset, 'project_metadata':project_metadata}








