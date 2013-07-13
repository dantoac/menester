#encode: utf8

def index():
    p = request.vars.p
    project_name = ''
    if p:

        project_name = 'en '+db(db.project.uuid == p).select(db.project.name, limitby=(0,1)).first()['name']
        
        db.income.project_uuid.default = p
        db.income.project_uuid.writable = False
        db.income.project_uuid.readable = False
        query = (db.income.project_uuid == p) & (db.income.project_uuid == db.project.uuid)
    else:
        query = db.income.id>0
    form = crud.update(db.income,request.args(0))

    dataset = db(query).select(
        db.income.id,
        db.income.project_uuid,
        db.income.amount,
        db.income.due_date,
        db.income.done,
        db.project.ALL,
        left=db.project.on(db.income.project_uuid == db.project.uuid)
    )
    

    
    chart_dataset = db(query).select(db.income.amount.sum(),db.income.due_date,groupby=db.income.due_date)
    data = [(str(i.income.due_date),i['SUM(income.amount)']) for i in chart_dataset]
    meta_data_x = [d[0] for d in data]
    data_x = "["
    for m in meta_data_x:  data_x += '"%s",' % m
    data_x+= "]"
    data_y = [int(d[1]) for d in data]
    chart_data = [data_x, data_y]



    return {'form':form,'dataset':dataset, 'project_name':project_name, 'chart_data':chart_data}















