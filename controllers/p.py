# coding: utf8
# This is the controller for "Projects".

@auth.requires_login()
def index():
    session.forget(response)
    new_project = LOAD(c='p', f='new.load', ajax=True, target='new_project_container')
    return dict(new_project=new_project)


def list():
        
    data = db(db.project).select()

    project_list = TABLE(TR(
            TH('Nombre'),
            TH('Avance'),
            TH('Finaliza'),
            ),_class='table table-striped')
    
    for p in data:
        project_list.append(TR(
                TD(A(TAG.i(_class='icon-list icon-white'), ' %s' % p.name.title(), 
                     _href=URL(c='t', f='index.html', vars=dict(p=p.slug)), 
                     _class='btn btn-primary' ), A(TAG.i(_class='icon-edit'), 
                                                   _href=URL(c='p', f='new.html', 
                                                             args=p.id), _class='btn')
                   ),
                TD(DIV(DIV(_class="bar", 
                           _style="width: %s%%;" % total_progress(p.uuid)),
                       _class="progress")),
                TD(p.finish or SPAN('Indefinido',_class='muted')),
                ))

    return dict(project_list=project_list)


#@auth.requires_login()
def new():
    form = crud.update(db.project, request.args(0))
    #form = SQLFORM(db.project, request.args(0))

    if form.process().accepted:
        response.flash = "Projecto registrado"
        if not request.ajax: redirect(URL(c='p',f='index'))
    elif form.errors:
        response.flash = "Hubo errores. Revise mensaje en formulario"
        response.js = 'jQuery(document).ready(function(){jQuery("#new_project").show();});'
 
    project_list = LOAD(f='list.load', ajax=True)

    return dict(form=form, project_list=project_list)
