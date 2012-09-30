# coding: utf8




def task():
    # comentar una tarea
    task_uuid = request.vars.tuuid
    
    if task_uuid:
        db.comment_task.task_uuid.default = task_uuid
        db.comment_task.author.default = db.auth_user[auth.user_id].email

    form = crud.create(db.comment_task)

    query = (db.comment_task.task_uuid.contains(task_uuid))

    tasklist_dataset = db(query).select(db.comment_task.body,
                                        db.comment_task.author,
                                        db.comment_task.created_on,
                                        db.comment_task.id,
                                        orderby=~db.comment_task.id)
    
    return dict(form=form, comments=tasklist_dataset)


def task_list():
    # lista los comentarios en una tarea

    return locals()

