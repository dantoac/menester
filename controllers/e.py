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
    

    return {'form':form,'dataset':dataset, 'project_name':project_name}















