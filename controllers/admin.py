# coding: utf8

@auth.requires_login()
def index(): 
    if not auth.user_id == 1: redirect(URL(f='error'))
    menu = UL([A(t, _href=URL(args=t)) for t in db.tables])


    db.auth_user.registration_key.writable = True

    admin = SQLFORM.smartgrid(db[request.args(0) or 'auth_user'])

    return {'menu': menu,'admin': admin}

