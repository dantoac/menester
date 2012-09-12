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
                Field('finished', 'boolean', default=False),
                Field('percentage', 'integer', default=0,
                      requires=IS_IN_SET([0,10,35,55,75,90,100]),
                      ),
                format = "%(name)s-%(percentage)s"
                )
    
db.define_table('task',
    Field('project', 'reference project'),
    Field('name', 'string', required=True, requires=IS_NOT_EMPTY()),
    Field('description', 'text'),
    Field('state', 'reference state', default=1),
    Field('priority', 'integer', requires=IS_EMPTY_OR(IS_INT_IN_RANGE(0,11))),
    Field('created', 'datetime', default=request.now),
    Field('updated', 'datetime', update=request.now),
    Field('finish', 'datetime'),
    Field('active', 'boolean'),
    format = '%(name)s'
   )
