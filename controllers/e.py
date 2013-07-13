#encode: utf8

def index():
    response.flash = 'Aún es necesario recargar manualmente el gráfico luego de registrar Ingresos.'
    request.vars.p

    if request.vars.p:

        query = (db.expense.project_uuid == request.vars.p) & (db.expense.project_uuid == db.project.uuid)
    else:
        query = db.expense.id>0

    dataset = db(query).select(db.expense.amount.sum(),db.expense.due_date,groupby=db.expense.due_date)
    data = [(str(i.expense.due_date),i['SUM(expense.amount)']) for i in dataset]
    meta_data_x = [d[0] for d in data]
    data_x = "["
    for m in meta_data_x:  data_x += '"%s",' % m
    data_x+= "]"
    data_y = [int(d[1]) for d in data]
    chart_data = [data_x, data_y]



    return {'chart_data':chart_data,
            'dataset':dataset}



def new():
        
    project_metadata = ''
    if request.vars.p and len(request.vars.p.strip()):

        project_metadata = db(db.project.uuid == request.vars.p).select(limitby=(0,1))     
        db.expense.project_uuid.default = request.vars.p
        db.expense.project_uuid.writable = False
        db.expense.project_uuid.readable = False
        query = (db.expense.project_uuid == request.vars.p) & (db.expense.project_uuid == db.project.uuid) #& (db.expense.done == True)
    else:
        query = db.expense.id>0
    form = SQLFORM(db.expense,request.args(0))

    if form.process().accepted:
        if request.args(0):
            session.flash = 'Egreso actualizado exitosamente'
            redirect(URL(f='new.load',vars=request.vars))
        else:
            response.flash = 'Egreso registrado exitosamente'
    elif form.errors:
        response.flash = 'Error registrando el Egreso. Revise el formulario'

    dataset = db(query).select(
        db.expense.id,
        db.expense.project_uuid,
        db.expense.amount,
        db.expense.due_date,
        db.expense.done,
        db.project.ALL,
        left=db.project.on(db.expense.project_uuid == db.project.uuid)
    )
    
    return {'form':form, 'dataset':dataset, 'project_metadata':project_metadata}














