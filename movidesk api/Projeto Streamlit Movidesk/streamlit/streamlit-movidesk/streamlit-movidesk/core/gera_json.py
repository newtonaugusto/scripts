import requests
import json 
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

class Request:
    def __init__(self, month, year):
        self.initial_date = datetime(year=year,month=month, day=1)
        self.final_date = self.initial_date + relativedelta(months=+1) - timedelta(days=1)
        self.min_date = datetime(year=2020,month=6, day=16)

    ### Função que faz a requisição e retorna os tickets da API do Movidesk
    def request_tickets(self):
        ### Repete a requisição para cada dia do mês, pois tem um limite de linhas na api
        if self.initial_date < self.min_date:
            self.initial_date = self.min_date
        if self.final_date > datetime.today():
            self.final_date = datetime.today()
        query = []
        for i in range(self.initial_date.day, self.final_date.day + 1):
            datefull = f'{self.initial_date.year}-{self.initial_date.month:02}-{i:02}'
            print (datefull)
            query.append("""https://api.movidesk.com/public/v1/tickets?token=&$select=id,subject,serviceFirstLevel,createdDate,actionCount,category,justification,ownerTeam,createdBy,status,urgency&$expand=clients($select=id,businessName,personType,profileType),createdBy,owner,clients($expand=organization($select=id,businessName)),actions($select=origin,id,createdDate,description,createdBy,status,justification),actions($expand=timeAppointments($expand=createdBy))&$filter=actions/any(a:a/timeAppointments/any(t:t/date ge """ + datefull + """T00:00:00.00z and t/date le """ + datefull + """T23:59:59.00z))""")

        res = []
        for q in query:
            print("index: {}".format(query.index(q)))
            resposta = requests.get(q)
            if resposta.status_code == 200:
                res.append(resposta)
            else:
                print(f'Resposta.text: {resposta.text}')
                print(f"Query: {q}")
                i = 0
                while i < 3 or resposta.status_code == 200:
                    resposta = requests.get(q)
                    i+=1
                    
                    print(f'Status Code: {resposta.status_code}')
            
        tick = [] 
        for r in res:
            tick.append(json.loads(r.text))

        tickets = []
        for t in tick:
            tickets.extend(t)

        return tickets

# Para requisições all time
start_date_request = datetime(year=2020,month=6, day=1)
end_date_request = datetime(year=2021,month=6, day=1)
tickets = []
while start_date_request <= end_date_request:
    monthly_ticket = Request(start_date_request.month, start_date_request.year).request_tickets()
    start_date_request = start_date_request + relativedelta(months=+1)
    tickets.extend(monthly_ticket)
with open('062020-062021-tickets.json', 'w') as f:
        json.dump(tickets, f)


# Para requisições de meses específicos
# date_to_request = datetime(year=2021,month=5, day=1)
# tickets = Request(date_to_request.month, date_to_request.year).request_tickets()
# with open(f'{date_to_request.month} - {date_to_request.year}.json', 'w') as f:
#         json.dump(tickets, f)
