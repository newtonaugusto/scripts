import requests
import json 
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

class Request:
    def __init__(self, month, year):
        self.initial_date = datetime(year=year,month=month, day=1)
        self.final_date = self.initial_date + relativedelta(months=+1) - timedelta(days=1)

    ### Função que faz a requisição e retorna os tickets da API do Movidesk
    def request_tickets(self):
        ### Repete a requisição para cada dia do mês, pois tem um limite de linhas na api
        query = []
        for i in range(1, self.final_date.day + 1):
            datefull = f'{self.initial_date.year}-{self.initial_date.month:02}-{i:02}'
            print (datefull)
            query.append("""https://api.movidesk.com/public/v1/tickets?token=&$select=id,subject,serviceFirstLevel,createdDate,actionCount,category,justification,ownerTeam,createdBy,status,urgency&$expand=clients($select=id,businessName,personType,profileType),createdBy,owner,clients($expand=organization($select=id,businessName)),actions($select=origin,id,createdDate,description,createdBy,status,justification),actions($expand=timeAppointments($expand=createdBy))&$filter=actions/any(a:a/timeAppointments/any(t:t/date ge """ + datefull + """T00:00:00.00z and t/date le """ + datefull + """T23:59:59.00z))""")

        res = []
        for q in query:
            print("index: {}".format(query.index(q)))
            res.append(requests.get(q))

        tick = [] 
        for r in res:
            tick.append(json.loads(r.text))

        tickets = []
        for t in tick:
            tickets.extend(t)

        return tickets

date_to_request = datetime(year=2021,month=4, day=1)
tickets = Request(date_to_request.month, date_to_request.year).request_tickets()
with open(f'{date_to_request.month} - {date_to_request.year}.json', 'w') as f:
        json.dump(tickets, f)
