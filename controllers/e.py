#encode: utf8

def index():
    p = request.vars.p
    project_name = ''
    if p:

        project_name = 'en '+db(db.project.uuid == p).select(db.project.name, limitby=(0,1)).first()['name']

        db.expense.project_uuid.default = p
        db.expense.project_uuid.writable = False
        db.expense.project_uuid.readable = False
        query = (db.expense.project_uuid == p) & (db.expense.project_uuid == db.project.uuid)
    else:
        query = db.expense.id>0
    form = crud.update(db.expense,request.args(0))

    dataset = db(query).select(
        db.expense.id,
        db.expense.project_uuid,
        db.expense.amount,
        db.expense.due_date,
        db.expense.done,
        db.project.ALL,
        left=db.project.on(db.expense.project_uuid == db.project.uuid)
    )
    

    

    chart_dataset = db(query).select(db.expense.amount.sum(),db.expense.due_date,groupby=db.expense.due_date)
    data = [(str(i.expense.due_date),i['SUM(expense.amount)']) for i in chart_dataset]
    meta_data_x = [d[0] for d in data]
    data_x = "["
    for m in meta_data_x:  data_x += '"%s",' % m
    data_x+= "]"
    data_y = [int(d[1]) for d in data]
    chartdata = [data_x, data_y]

    return {'form':form,'dataset':dataset, 'project_name':project_name, 'chartdata':chartdata}















