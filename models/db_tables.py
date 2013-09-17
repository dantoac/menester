#coding: utf8

import uuid

dt = db.define_table

dt('project',
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
   Field('close', 'boolean', default=False),
   Field('email_contact', 'list:string', requires=IS_EMAIL()),
   Field('team', 'list:reference auth_user'),
   Field('value','double',default=0),
   Field('estimated_cost','double',default=0,label='Costo Estimado' ),
   auth.signature,
   format = '%(name)s'
)


dt('project_setting',
   auth.signature,
   Field('project_uuid'),
)

dt('project_relation',
   Field('project')
)

dt('state',
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


dt('task',
    Field('uuid','string',length=64, default=uuid.uuid4(),
          writable=False),
    Field('project_uuid', 'string', requires=IS_IN_DB(db, 'project.uuid'),
          writable=False),
    Field('project_name'),
    Field('name', 'string', required=True, requires=IS_NOT_EMPTY()),
    Field('tag','list:string'),
    Field('description', 'text'),
    Field('progress', 
          requires=IS_IN_SET([(0,'Nuevo'),
                              (10,'10%'),
                              (25,'25%'),
                              (55,'55%'),
                              (75,'75%'),
                              (90,'90%'),
                              (100,'Terminado')], zero=None),
          label='Estado/Progreso'),
    Field('priority', 'string', requires=IS_EMPTY_OR(IS_IN_SET([1,2,3,4,5])),
          label=T('Prioridad'),default='3'),
    Field('created', 'datetime', default=request.now, readable=False,writable=False),
    Field('updated', 'datetime', compute=lambda r:request.now),
    Field('start', 'datetime'),
    Field('finish', 'datetime'),
    Field('closed', 'boolean', default=False,
          compute=(lambda c: True if c['progress']=='100' or c['nullify']==True else False)),
    Field('nullify', 'boolean', default=False),
    Field('author','string', writable=False),
    Field('task_parent'),
    Field('task_child'),
    format = '%(name)s'
    )

dt('comment',
    Field('uuid', 'string', length=64, default=uuid.uuid4(),
          writable=False, readable=False),
    Field('target_uuid', 'string',
          writable=False, readable=False),
    Field('body', 'text', required=True, 
          requires=IS_LENGTH(minsize=4,maxsize=1024)),
    Field('author','string', writable=False, readable=False),
    Field('created_on','datetime', default=request.now,
          writable=False, readable=False)
    )



pago_metadata = db.Table(db,'pago_metadata',
                         Field('amount','double'),
                         Field('subject'),
                         Field('due_date','date'),
                         Field('done','boolean',default=True),
                     )

dt('income',    
   Field('uuid', 'string', length=64, default=uuid.uuid4(),
         writable=False, readable=False),
   Field('project_uuid'),
   Field('type','reference income_type'),
   pago_metadata,
   auth.signature
)
    
dt('expense',
   Field('uuid', 'string', length=64, default=uuid.uuid4(),
         writable=False, readable=False),
   Field('project_uuid'),
   Field('type','reference expense_type'),
   pago_metadata,
   auth.signature
)


dt('income_type',
   Field('name'),
   format = '%(name)s'
   )

dt('expense_type',
   Field('name'),
   format = '%(name)s'
   )

db.income.project_uuid.requires=IS_EMPTY_OR(IS_IN_DB(db, 'project.uuid','%(name)s'))
db.expense.project_uuid.requires=IS_EMPTY_OR(IS_IN_DB(db, 'project.uuid','%(name)s'))


if db.income_type.isempty():
    db.income_type.bulk_insert([
        {'name':'Cliente Producto'},
        {'name':'Cliente Servicio'},
        {'name':'Otro...'},
    ])



if db.expense_type.isempty():
    db.expense_type.bulk_insert([
        {'name':'Bencina'},
        {'name':'Pasaje'},
        {'name':'Comida'},
        {'name':'Reunión'},
        {'name':'Gastos Generales'},
        {'name':'Otro...'},
    ])


