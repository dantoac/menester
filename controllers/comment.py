# coding: utf8

@auth.requires_login()
def new():
    # comentar una tarea
    uuid = request.vars.uuid
    
    if uuid:
        db.comment.target_uuid.default = uuid
        db.comment.author.default = db.auth_user[auth.user_id].email

    form = SQLFORM(db.comment)

    if form.process().accepted:
        
        ds = db((db.task.uuid == uuid)
                & (db.task.project_uuid == db.project.uuid)
                ).select(db.task.id,
                         db.task.uuid,
                         db.task.name,
                         db.project.name,
                         db.project.email_contact,
                         db.project.uuid,
                         limitby=(0,1)
                         ).first()

        mail.send(
            to=ds.project.email_contact,
            subject='Comentario en Proyecto %s' % ds.project.name.upper(),
            message='\nTarea #%(taskid)s: %(taskname)s\nURL: %(url)s\nComentario de %(author)s:\n"%(comment)s"\n' % \
                dict(taskid=ds.task.id,
                     taskname=ds.task.name,
                     url=URL(c='t',f='view.html',
                             args=ds.task.id,
                             vars={'puuid':ds.project.uuid},
                             host=True),
                     author=db.auth_user[auth.user_id].email,
                     comment=form.vars.body)
            )


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

