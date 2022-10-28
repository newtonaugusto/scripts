# coding: utf-8

import requests
import json 
from datetime import datetime, timedelta
import pandas as pd
import csv

### Função que faz a requisição e retorna os tickets da API do Movidesk
def request_tickets(start_day_int, final_day_int, month_str, year_str):
    ### Repete a requisição para cada dia do mês, pois tem um limite de linhas na api
    query = []
    for i in range(start_day_int, final_day_int + 1):
        dia = (f'{i:02}')
        print(dia)
        mes = month_str
        ano = year_str
        datefull = str(ano) + '-' + str(mes) + '-' + str(dia)
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

### Para Testes
# tickets = json.loads(requests.get("https://api.movidesk.com/public/v1/tickets?token=&$select=id,subject,serviceFirstLevel,createdDate,actionCount,category,justification,ownerTeam,createdBy,status,urgency&$expand=clients($select=id,businessName,personType,profileType),createdBy,owner,clients($expand=organization($select=id,businessName)),actions($select=origin,id,createdDate,description,createdBy,status,justification),actions($expand=timeAppointments($expand=createdBy))&$filter=actions/any(a:a/timeAppointments/any(t:t/date ge 2021-03-01 and t/date le 2021-03-31))&$top=100").text)

### Arquivo de saída
now = datetime.now().strftime("%H")
mes_atual = '06'
initial_date_request = '01-' + mes_atual +'-2020'
final_date_request = '30-' + mes_atual +'-2020'
titulo = '2020-' + mes_atual
arqsaida= r'relatorio-{}.csv'.format(titulo)


### Define dia de inicio e de fim, o mês e o ano da query, e realiza a consulta
tickets = request_tickets(1, 31, mesAtual, '2021')

### Variáveis de controle
initial_date = datetime.strptime(initial_date_request, '%d-%m-%Y')
final_date = datetime.strptime(final_date_request, '%d-%m-%Y')

### Prepara os dados para saida csv
table = []
for i, t in enumerate(tickets):
    
    clients = []
    for client in t['clients']:
        if(client['organization'] == None):
            clients.append([client['id'], client['businessName']])
        else:
            clients.append([client['organization']['id'], client['organization']['businessName']])
    for action in t['actions']:
        activity = []
        current_date = datetime.strptime(action['createdDate'][:10], '%Y-%m-%d')
        if not (current_date >= initial_date and current_date <= final_date):
            pass
        else:
            if not action['timeAppointments']:
                pass
            else:
                workTime = timedelta()                    
                for time in action['timeAppointments']:
                    if time['periodStart']:
                        periodStart = time['periodStart']
                    if time['periodEnd']:
                        periodEnd = time['periodEnd']
                    if time['workTypeName']:
                        workTypeName = time['workTypeName']
                    if not (time['workTime'] == '00:00:00'):
                        if time['activity']:
                            activity.append(time['activity'])
                        current_date = datetime.strptime(time['date'][:10], '%Y-%m-%d')
                        if (current_date >= initial_date and current_date <= final_date):
                            date_text = time['workTime']
                            x = date_text.split(":")
                            hours = timedelta(hours=int(x[0]), minutes=int(x[1]), seconds=int(x[2]))
                            workTime+=hours
                controle = False
                for z in table:
                    if(z[6] == action['id'] and z[2] == t['id']):
                        controle = True
                        break
                if not controle:
                    if not t['justification']:
                        justification = '-'
                    else:
                        justification = t['justification']
                    if not t['owner']:
                        owner = "-"
                    else:
                        owner = t['owner']['businessName']
                    table.append([action['createdDate'][:10], t['subject'], t['id'], owner, clients, workTime, action['id'], t['urgency'], t['status'], t['ownerTeam'], justification, t['category'], t['actionCount'], action['status'], action['description'], activity,t['createdBy']['businessName'], periodStart, periodEnd, workTypeName, t['serviceFirstLevel']])

for x in table:
    days = x[5].days
    seconds = x[5].seconds
    hours = (seconds//3600) + days*24
    minutes = (seconds//60)%60
    x[5] = str(f'{hours:02}')+':'+str(f'{minutes:02}')
    for cont, c in enumerate(x[4]):
        aux = ""
        aux = str(c[1]).replace("'","")
        if(cont == 0):
            clients = aux
        else:
            if aux in clients:                
                clients = clients + ',' + aux
    x[4] = clients

with open(arqsaida, 'w') as f:
    # table.insert(0, ["data da action","assunto do ticket","id do ticket","owner criador", "clientes","tempo trabalhado","action id","urgency","status","ownerTeam", "justification", "category", "actionCount", "status", "description", "activity","solicitante","hora de início", "hora de fim", "tipo de hora", "serviço"])
    pd.DataFrame(table).to_csv(arqsaida, index=None, header=None, sep=';')