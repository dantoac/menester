# coding: utf8




def task():
    # comentar una tarea
    task_uuid = request.vars.tuuid
    
    if task_uuid:
        db.comment.object_uuid.default = task_uuid
        db.comment.author.default = db.auth_user[auth.user_id].email

    form = crud.create(db.comment)

    query = (db.comment.object_uuid.contains(task_uuid))

    tasklist_dataset = db(query).select(db.comment.body,
                                        db.comment.author,
                                        db.comment.created_on,
                                        db.comment.id,
                                        orderby=~db.comment.id)
    
    return dict(form=form, comments=tasklist_dataset)


