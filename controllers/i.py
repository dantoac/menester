#encode: utf8

def index():
    p = request.vars.p

    if p:
        db.income.project_uuid.default = p
        #db.income.project_uuid.writable = False
        #db.income.project_uuid.readable = False
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
    

    return {'form':form,'dataset':dataset}















