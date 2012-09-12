# coding: utf8
# This is the controller for "Projects".

@auth.requires_login()
def index():
    projects = LOAD(f='new.load', ajax=True)
    return dict(projects=projects)


@auth.requires_login()
def new():
    form = SQLFORM(db.project, request.args(0), _class='')

    if form.process().accepted:
        response.flash = 'Proyecto agregado'
    elif form.errors:
        response.flash = 'errores!'

    data = db(db.project).select()

    result = TABLE(TR(
        TH('Nombre'),
        TH('Finaliza'),
        TH('')
        ),_class='table table-striped')

    for p in data:
        result.append(TR(
            TD(EM(p.name.title())),
            TD(prettydate(p.finish)),
            #TD(A('Tareas', _href=URL(c='t', vars={'p':p.id}), _class='btn', ))
            TD(A('Tareas', _href=URL(c='t', f='index.html', vars=dict(p=p.slug)), _class='btn', ))
            ))


    return dict(form=form, result=result)
