# coding: utf8
# This is the controller for "Projects".

@auth.requires_login()
def index():
    projects = LOAD(f='new.load', ajax=True)
    return dict(projects=projects)


@auth.requires_login()
def new():
    form = crud.update(db.project, request.args(0))

    data = db(db.project).select()

    result = TABLE(TR(
        TH('Nombre'),
        TH('Avance'),
        TH('Finaliza'),
        ),_class='table table-striped')

    for p in data:
        result.append(TR(
            TD(A(TAG.i(_class='icon-list icon-white'), ' %s' % p.name.title(), 
                 _href=URL(c='t', f='index.html', vars=dict(p=p.slug)), 
                 _class='btn btn-primary' ), A(TAG.i(_class='icon-edit'), 
                                           _href=URL(c='p', f='new.html', 
                                                     args=p.id), _class='btn')
               ),
            TD(),
            TD(p.finish),
            ))


    return dict(form=form, result=result)
