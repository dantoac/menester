#encode: utf8

def index():
    response.flash = 'Aún es necesario recargar manualmente el gráfico luego de registrar Ingresos.'
    p = request.vars.p
    project_name = ''
    if p:
        project_name = 'en '+db(db.project.uuid == p).select(db.project.name, limitby=(0,1)).first()['name']
        query = (db.income.project_uuid == p) & (db.income.project_uuid == db.project.uuid)
    else:
        query = db.income.id>0

    dataset = db(query).select(db.income.amount.sum(),db.income.due_date,groupby=db.income.due_date)
    data = [(str(i.income.due_date),i['SUM(income.amount)']) for i in dataset]
    meta_data_x = [d[0] for d in data]
    data_x = "["
    for m in meta_data_x:  data_x += '"%s",' % m
    data_x+= "]"
    data_y = [int(d[1]) for d in data]
    chart_data = [data_x, data_y]



    return {'chart_data':chart_data,'project_name':project_name,'dataset':dataset}



def new():
        
    project_name = ''
    if request.vars.p and len(request.vars.p.strip()):

        project_name_dataset = db(db.project.uuid == request.vars.p).select(db.project.name, limitby=(0,1))
        if project_name_dataset: project_name = 'en '+project_name_dataset.first()['name']
        
        
        db.income.project_uuid.default = request.vars.p
        db.income.project_uuid.writable = False
        db.income.project_uuid.readable = False
        query = (db.income.project_uuid == request.vars.p) & (db.income.project_uuid == db.project.uuid)
    else:
        query = db.income.id>0
    form = SQLFORM(db.income,request.args(0))

    if form.process().accepted:
        if request.args(0):
            session.flash = 'Ingreso actualizado exitosamente'
            redirect(URL(f='new.load',vars=request.vars))
        else:
            response.flash = 'Ingreso registrado exitosamente'
    elif form.errors:
        response.flash = 'Error registrando el Ingreso. Revise el formulario'

    dataset = db(query).select(
        db.income.id,
        db.income.project_uuid,
        db.income.amount,
        db.income.due_date,
        db.income.done,
        db.project.ALL,
        left=db.project.on(db.income.project_uuid == db.project.uuid)
    )
    
    return {'form':form, 'dataset':dataset}














