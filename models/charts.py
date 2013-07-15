# coding: utf8

def CHART_income_expense_total():
    
    dataset_income = db(db.income).select(db.income.amount.sum(),db.income.due_date,groupby=db.income.due_date)
    dataset_expense = db(db.expense).select(db.expense.amount.sum(),db.expense.due_date,groupby=db.expense.due_date)

    dataset = db((db.income.project_uuid == db.project.uuid)
                 & (db.expense.project_uuid == db.project.uuid)
                 ).select()

    #dataset_full = dataset_income & dataset_expense

    data_income = [(str(i.income.due_date),i['SUM(income.amount)']) for i in dataset_income]
    data_expense = [(str(i.expense.due_date),i['SUM(expense.amount)']) for i in dataset_expense]



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
Histórico de <span class="label label-info">Ingresos</span> y <span class="label label-important">Egresos</span>
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
           'Y2':chart_data[2]
    }


    return XML(html)
