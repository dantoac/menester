# coding: utf8
# This is the controller for "Projects".

@auth.requires_login()
def index():
    session.forget(response)
    new_project = LOAD(c='p', f='new.load', ajax=True, target='new_project')
    return dict(new_project=new_project)


def list():
        
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
            TD(DIV(DIV(_class="bar", 
                       _style="width: %s%%;" % total_progress(p.id)),
                   _class="progress progress-striped")),
            TD(p.finish or SPAN('Indefinido',_class='muted')),
            ))

    return dict(result=result)


#@auth.requires_login()
def new():
    #form = crud.update(db.project, request.args(0))
    form = SQLFORM(db.project)

    if form.process().accepted:
        response.flash = "Projecto registrado"
    elif form.errors:
        response.flash = "Hubo errores"
    else:
        response.flash = "Lista de Proyectos"

    project_list = LOAD(f='list.load', ajax=True)

    return dict(form=form, project_list=project_list)
