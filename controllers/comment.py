# coding: utf8

def new():
    # comentar una tarea
    uuid = request.vars.uuid
    
    if uuid:
        db.comment.target_uuid.default = uuid
        db.comment.author.default = db.auth_user[auth.user_id].email

    form = crud.create(db.comment)

    query = (db.comment.target_uuid == uuid)

    dataset = db(query).select(db.comment.body,
                               db.comment.author,
                               db.comment.created_on,
                               db.comment.id,
                               orderby=~db.comment.id)
    
    return dict(form=form, comments=dataset)


def _delete():
    comment_id = request.args(0)
    delete = db(db.comment.id == comment_id).delete()
    if delete:
        response.flash = 'Comentario eliminado'
    else:
        response.flash = 'omgwtf'
