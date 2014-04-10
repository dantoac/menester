#encode: utf8


def _open_task(project_uuid):
    dataset = db((project_uuid == db.project.uuid)
                 & (db.project.uuid == db.task.project_uuid)
                 & (db.task.closed == False)
             ).select(#db.project.uuid, 
                      db.task.id.count(), 
                      #groupby=db.project.uuid
             ).first()[db.task.id.count()]
    
    return dataset


def _get_task_info(task_uuid):
    '''
    Para obtener info de una tarea usando sólo su uuid
    '''
    dataset = db(db.task.uuid == task_uuid).select().first()
    return Storage(dataset)


#def _get_task_info_parent


def total_progress(project):
    """
    Calcula el porcentaje de progreso total de tareas de un
    proyecto dado por el uuid string: 'project', sin
    considerar las tareas anuladas (task.nullify=True)
    Retorna el número del porcentaje como string.
    """

    session.forget(response)

    if project:
        query = ((db.task.project_uuid == project) &
                 (db.task.nullify == False)
        )
    else:
        query = ((db.task.id>0) &
                 (db.task.project_uuid == db.project.uuid) &
                 (db.project.close == False) &
                 (db.task.nullify == False)
        )

    task_count =  db.task.id.count()
    percentage_sum = db.task.progress.sum()

    data = db(query).select(percentage_sum, task_count, 
                            cacheable = True,
                            ).first()
   
    total_progress = 0

    if data[percentage_sum]:
        total_progress = round(float(data[percentage_sum]) / float(data[task_count]),1)

    return total_progress


def numfmt(value, places=0, curr='$', sep='.', dp='',
             pos='', neg='-', trailneg=''):
    """Convert Decimal to a money formatted string.

    places:  required number of places after the decimal point
    curr:    optional currency symbol before the sign (may be blank)
    sep:     optional grouping separator (comma, period, space, or blank)
    dp:      decimal point indicator (comma or period)
             only specify as blank when places is zero
    pos:     optional sign for positive numbers: '+', space or blank
    neg:     optional sign for negative numbers: '-', '(', space or blank
    trailneg:optional trailing minus indicator:  '-', ')', space or blank

    >>> d = Decimal('-1234567.8901')
    >>> moneyfmt(d, curr='$')
    '-$1,234,567.89'
    >>> moneyfmt(d, places=0, sep='.', dp='', neg='', trailneg='-')
    '1.234.568-'
    >>> moneyfmt(d, curr='$', neg='(', trailneg=')')
    '($1,234,567.89)'
    >>> moneyfmt(Decimal(123456789), sep=' ')
    '123 456 789.00'
    >>> moneyfmt(Decimal('-0.02'), neg='<', trailneg='>')
    '<0.02>'

    """
    from decimal import Decimal
    value = str(value)
    value = Decimal(value)
    q = Decimal(10) ** -places      # 2 places --> '0.01'
    sign, digits, exp = value.quantize(q).as_tuple()
    result = []
    digits = map(str, digits)
    build, next = result.append, digits.pop
    if sign:
        build(trailneg)
    for i in range(places):
        build(next() if digits else '0')
    build(dp)
    if not digits:
        build('0')
    i = 0
    while digits:
        build(next())
        i += 1
        if i == 3 and digits:
            i = 0
            build(sep)
    build(curr)
    build(neg if sign else pos)
    return ''.join(reversed(result))


