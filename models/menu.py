# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## Customize your APP title, subtitle and menus here
#########################################################################

response.title = ' '.join(word.capitalize() for word in request.application.split('_'))
response.subtitle = T('Gestor simple de Tareas y Proyectos')

## read more at http://dev.w3.org/html5/markup/meta.name.html
response.meta.author = 'contacto@nim.io'
response.meta.description = 'fast task and project manager'
response.meta.keywords = 'tracker, web2py'
response.meta.generator = 'Web2py Web Framework'

## your http://google.com/analytics id
response.google_analytics_id = None

#########################################################################
## this is the main application menu add/remove items as required
#########################################################################

if auth.has_membership('admin'):
    response.menu = [
        (T('Proyectos'), False, URL('p','index'), []),
        (T('Tareas'), False, URL('t','index'), []),
        (T('Flujo Caja'), None, None, [
            (T('Entradas'), False, URL('i','index'), []),
            (T('Salidas'), False, URL('e','index'), []),
            (T('Proyectadas'), False, URL('due','index'), [])
        ]),
        ]

elif auth.has_membership('cdo'):
    response.menu = [(T('Tareas'), False, URL('t','index'), []),]
