# coding: utf8


def index(): 

    menu = UL([A(t, _href=URL(args=t)) for t in db.tables])

    admin = SQLFORM.smartgrid(db[request.args(0) or 'auth_user'])

    return {'menu': menu,'admin': admin}

