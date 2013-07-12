
def total_progress(project):
    """
    Calcula el porcentaje de progreso total de tareas de un
    proyecto dado por el parámetro integer: 'project', sin
    considerar las tareas anuladas (task.nullify=True)
    Retorna el número del porcentaje como string.
    """

    session.forget(response)

    query = ((db.task.project_uuid == project) &
             (db.task.nullify == False)
             )

    task_count =  db.task.id.count()
    percentage_sum = db.task.progress.sum()

    data = db(query).select(percentage_sum, task_count, 
                            cacheable = True,
                            ).first()
   
    total_progress = None

    if data[percentage_sum]:
        total_progress = data[percentage_sum] / data[task_count]

    return total_progress
