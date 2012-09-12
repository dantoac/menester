# coding: utf8

db.define_table('project',
    Field('name', 'string', label='Nombre'),
    Field('slug', compute=lambda n: IS_SLUG()(n['name'])[0]),
    Field('start', 'datetime', default=request.now,
            label='Fecha Inicio'),
    Field('finish', 'datetime', label='Fecha Término'),
    format = '%(name)s'
    )

db.define_table('state',
                Field('name', ),
                Field('closed', 'boolean', default=False),
                Field('percentage', 'integer', default=0,
                      requires=IS_INT_IN_RANGE(0,101),
                      ),
                format = '%(name)s %(percentage)s%%'
                )

if db(db.state).isempty():
    db.state.bulk_insert([
        dict(name='Nuevo',percentage=0),
        dict(name='Concepto',percentage=10),
        dict(name='Iniciado', percentage=25),
        dict(name='Bosquejo', percentage=55),
        dict(name='Prototipo', percentage=75),
        dict(name='Funcional', percentage=90),
        dict(name='Terminado', percentage=100)
        ])

db.define_table('task',
    Field('project', 'reference project'),
    Field('name', 'string', required=True, requires=IS_NOT_EMPTY()),
    Field('description', 'text'),
    Field('state', 'reference state', default=1),
    Field('priority', 'string', requires=IS_EMPTY_OR(IS_IN_SET([1,2,3,4,5])),
        default='3',widget=SQLFORM.widgets.options.widget),
    Field('created', 'datetime', default=request.now),
    Field('updated', 'datetime', update=request.now),
    Field('finish', 'datetime'),
    Field('active', 'boolean'),
    Field('author','string', writable=False),
    format = '%(name)s'
   )
