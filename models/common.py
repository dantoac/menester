
def total_progress(project):
    """
    Calcula el porcentaje de progreso total de tareas de un
    proyecto dado por el parámetro integer: 'project', sin
    considerar las tareas rechazadas (por defecto state.id '6')
    Retorna el número del porcentaje como string.
    """

    session.forget(response)

    query = ((db.task.project == project) &
             (db.task.state == db.state.id) &
             (db.state.id <> 6)
             )

    task_count =  db.state.id.count()
    percentage_sum = db.state.percentage.sum()

    data = db(query).select(percentage_sum, task_count,
                       cacheable = True).first()
   
    total_progress = None

    if data[percentage_sum]:
        total_progress = data[percentage_sum] / data[task_count] 

    return str(total_progress)
