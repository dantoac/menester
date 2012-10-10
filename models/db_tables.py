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
         Field('aim', 'string', length=120),
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
         Field('project_uuid', 'string', requires=IS_IN_DB(db, 'project.uuid'),
               writable=False),
         Field('project_name'),
         Field('name', 'string', required=True, requires=IS_NOT_EMPTY()),
         Field('tag','list:string'),
         Field('description', 'text'),
         Field('state', 'reference state', default=1),
         Field('priority', 'string',
               requires=IS_EMPTY_OR(IS_IN_SET([1,2,3,4,5])),
               default='3',widget=SQLFORM.widgets.options.widget),
         Field('created', 'datetime', compute=lambda r:request.now),
         Field('finish', 'datetime'),
         Field('nullify', 'boolean', default=False),
         Field('author','string', writable=False),
         Field('task_parent'),
         Field('task_child'),
         format = '%(name)s'
         )


db.task.task_parent.requires=IS_IN_DB(
    db((db.task.project_uuid == request.vars.puuid) & ~(db.task.id==request.args(0))
       ), 'task.uuid', '%(name)s')

db.task.task_child.requires=IS_IN_DB(
    db((db.task.project_uuid == request.vars.puuid) & ~(db.task.id==request.args(0))
       ), 'task.uuid', '%(name)s')

deftable('comment_task',
         Field('uuid', 'string', length=64, default=uuid.uuid4(),
               writable=False, readable=False),
         Field('task_uuid', 'string', requires=IS_IN_DB(db, 'task.uuid'),
               writable=False, readable=False),
         Field('body', 'text', required=True, 
               requires=IS_LENGTH(minsize=4)),
         Field('author','string', writable=False, readable=False),
         Field('created_on','datetime', default=request.now,
               writable=False, readable=False)
         )
         
