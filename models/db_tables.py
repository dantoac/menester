# coding: utf8

import uuid

deftable = db.define_table

deftable('project',
         Field('uuid', 'string', length=64, default=uuid.uuid4(),
               writable=False, readable=False, unique=True, 
               required=True),
         Field('name', 'string', label='Nombre', required=True, 
               unique=True, requires=[IS_NOT_EMPTY(),
                                      IS_NOT_IN_DB(db,'project.name')
                                      ]),
         Field('slug', compute=lambda n: IS_SLUG()(n['name'])[0]),
         Field('start', 'datetime', default=request.now,
               label='Fecha Inicio'),
         Field('end', 'datetime', label='Fecha Término'),
         Field('finished', 'boolean'),
         format = '%(name)s'
         )

deftable('state',
         Field('name', 'string', required=True, unique=True,
               requires=[IS_NOT_EMPTY(), IS_NOT_IN_DB(db,'state.name')]),
         Field('closed', 'boolean', default=False),
         Field('percentage', 'integer', default=0,
               requires=IS_INT_IN_RANGE(0,101),
               ),
         format = '%(percentage)s%% %(name)s'
         )

if db(db.state).isempty():
    db.state.bulk_insert([
            dict(name='Nuevo',percentage=0),
            dict(name='Concepto',percentage=10),       
            dict(name='Iniciado',percentage=25),
            dict(name='Prototipo', percentage=55),
            dict(name='Pruebas', percentage=75),
            dict(name='Finalizado', percentage=100, closed=True)
            ])
    
    

deftable('task',
         Field('uuid','string',length=64, default=uuid.uuid4(),
               writable=False),
         Field('project_uuid', 'string', IS_IN_DB(db, 'project.uuid'),
               writable=False),
         Field('project_name'),
         Field('name', 'string', required=True, requires=IS_NOT_EMPTY()),
         Field('description', 'text'),
         Field('state', 'reference state', default=1),
         Field('priority', 'string', 
               requires=IS_EMPTY_OR(IS_IN_SET([1,2,3,4,5])),
               default='3',widget=SQLFORM.widgets.options.widget),
         Field('created', 'datetime', compute=lambda r:request.now),
         Field('finish', 'datetime'),
         Field('nullify', 'boolean', default=False),
         Field('author','string', writable=False),
         format = '%(name)s'
         )


