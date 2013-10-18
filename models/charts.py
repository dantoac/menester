# coding: utf8

def flux(project_uuid=None):
    '''
    Gráficos de incomes y expenses 
    usando Morris.js: http://www.oesmith.co.uk/morris.js/

    Permite gráficos de barra, línea y área por cada
    proyecto en específico y todos en general.
    '''

    from datetime import datetime
    
    # si pasamos el uuid de un proyecto, construye query para filtrar
    #sólo incomes y expenses de éste.
    if project_uuid:
        query_income = db.income.project_uuid == project_uuid
        query_expense = db.expense.project_uuid == project_uuid

    else:
        query_income = db.income.id>0
        query_expense = db.expense.id>0

    # datasets según query creadas anteriormente.
    #Obtiene las sumas totales agrupadas por AÑO-MES

    #incomes
    i_dataset = db((query_income) & (db.income.done == True)).select(
        db.income.due_date, 
        db.income.amount.sum(), 
        groupby=(db.income.due_date.year(), db.income.due_date.month()),
        cacheable=True
    )
    
    #expenses
    e_dataset = db((query_expense) & (db.expense.done == True)).select(
        db.expense.due_date, 
        db.expense.amount.sum(), 
        groupby=(db.expense.due_date.year(),db.expense.due_date.month()),
        cacheable=True
    )
    
    # crea objeto útil pero parcializado para usar en morris.
    #Uno para incomes
    report_i = [{'y': datetime.strftime(income.income.due_date,'%Y-%m'), 
                 'a':income['SUM(income.amount)'], 
             } for income in i_dataset]

    #Otro para expenses
    report_e = [{'y':datetime.strftime(expense.expense.due_date,'%Y-%m'), 
                 'b':expense['SUM(expense.amount)']} for expense in e_dataset]

    
    #"FIRME PERO FEO" BEGINS HERE!
    if len(report_i) >= len(report_e):
        most_registry = report_i[:]
        less_registry = report_e[:]
    else:
        most_registry = report_e[:]
        less_registry = report_i[:]

    
    
    # crea el objeto final para generar el gráfico.
    #TODO: resolver por qué quedan items repetidos (no perjudican 
    #gráfico final)
    
    for mr in most_registry:
        for ls in less_registry:
            if ls['y'] == mr['y']: #in mr.values():
                mr.update(ls)
                ls.update(mr)
            else:
                if not most_registry.count(ls):
                    most_registry.append(ls)
                #if not most_registry.count(mr):
                #    most_registry.append(mr)
               
    
    # elimina hashes repetidos en la lista
    #http://stackoverflow.com/questions/9427163/remove-duplicate-dict-in-list-in-python
    most_registry = [dict(t) for t in set([tuple(d.items()) for d in most_registry])]
    
    # ordena por fecha
    report_data = sorted(most_registry, key=lambda registry: registry['y'])

    return response.json(report_data)



def CHART_data_sum(dataset,xfield,ykeys):
    '''
    MORRIS.JS 
    
    data: [
    { y: '2009', a: 100, b: 90},
    { y: '2007', a: 75,  b: 65 },
    { y: '2013.', a: 50,  b: 40 },
    { y: '2006', a: 75,  b: 65 },
    { y: '2010', a: 50,  b: 40 },
    { y: '2011', a: 75,  b: 65 },
    { y: '2012', a: 100, b: 90 }
    ]
    '''
   

    #data = [{'y%s' % n: str(d[field]) for n,field in enumerate(dataset.colnames)} for d in dataset]

    colnames = dataset.colnames
    colnames.remove(xfield)

    data = []
    for d in dataset:
        col = {}
        for n,k in enumerate(dataset.colnames):
            col['%s%s' % (ykeys,n)] = str(d[k])
            col['x'] = d[xfield] or '2013'
        data.append(col)
            
    return data



def __CHART_data_sum(datasets,ykeys):
    '''
    data: [
    { y: '2009', a: 100, b: 90},
    { y: '2007', a: 75,  b: 65 },
    { y: '2013.', a: 50,  b: 40 },
    { y: '2006', a: 75,  b: 65 },
    { y: '2010', a: 50,  b: 40 },
    { y: '2011', a: 75,  b: 65 },
    { y: '2012', a: 100, b: 90 }
    ]
    '''
   
    from datetime import datetime, date


    #data = [{'y%s' % n: str(d[field]) for n,field in enumerate(dataset.colnames)} for d in dataset]

    data = []
    for n,dataset in enumerate(datasets):

        


        colnames = dataset.colnames
        
        #if xfield in colnames: colnames.remove(xfield)

        for d in dataset:

            
            for colname in dataset.colnames:
                
                if isinstance(d[colname],(date,datetime)):
                    xkey = colname 
                    colnames.remove(xkey)
                else:
                    xkey=None
                
            
            col = {}

            for k in colnames:
                col['%s%s' % (ykeys,n)] = str(d[k])
                try:
                    col['x'] = d[xkey]
                except:
                    col['x'] = '2012'

            data.append(col)
            
    return data





def _CHART_income_expense_total():
    '''jqcharts'''


    dataset_income = db(db.income).select(db.income.amount.sum(),db.income.due_date,groupby=db.income.due_date)
    dataset_expense = db(db.expense).select(db.expense.amount.sum(),db.expense.due_date,groupby=db.expense.due_date)

    dataset = db((db.income.project_uuid == db.project.uuid)
                 & (db.expense.project_uuid == db.project.uuid)
                 ).select()

    #dataset_full = dataset_income & dataset_expense

    data_income = [(str(i.income.due_date),i['SUM(income.amount)']) for i in dataset_income]
    data_expense = [(str(i.expense.due_date),i['SUM(expense.amount)']) for i in dataset_expense]

    total_incomes = sum([i['SUM(income.amount)'] for i  in dataset_income])
    total_expenses = sum([i['SUM(expense.amount)'] for i  in dataset_expense])

    #meta_data_x = [d[0] for d in data_expense]
    meta_data_x = [d[0] for d in data_expense]

    #meta_data_x.extend([d[0] for d in data_income])

    data_x = "["
    for m in meta_data_x:  data_x += '"%s",' % m
    data_x+= "]"

    data_y = [int(d[1]) for d in data_income]
    data_y2 = [int(d[1]) for d in data_expense]

    chart_data = [data_x, data_y, data_y2]

    html = '''
    
    
    <div class="row" style="width:960px;margin:1em auto;text-align:center;">

    
<div class="">Total <span class="label label-info">Ingresos</span> %(incomes)s <span class="label label-important">Egresos</span> %(expenses)s</div>
  <canvas id="chart" width="960" height="200" style="margin:auto;"></canvas>
</div>
<script>
  //Get the context of the canvas element we want to select
  var ctx = document.getElementById("chart").getContext("2d");


  var data = {
  labels : %(X)s, 
  datasets : [

  {
  fillColor : "rgba(151,187,205,0.5)",
  strokeColor : "rgba(151,187,205,1)",
  pointColor : "rgba(151,187,205,1)",
  pointStrokeColor : "#fff",
  data : %(Y1)s
  },

  {
  fillColor : "rgba(205,151,187,0.5)",
  strokeColor : "rgba(151,187,205,1)",
  pointColor : "rgba(151,187,205,1)",
  pointStrokeColor : "#fff",
  data : %(Y2)s
  }


  ]
  }

  var myNewChart = new Chart(ctx).Line(data);
</script>
    ''' % {'X':chart_data[0],
           'Y1':chart_data[1],
           'Y2':chart_data[2],
           'incomes':numfmt(total_incomes),
           'expenses':numfmt(total_expenses)
    }


    return XML(html)
