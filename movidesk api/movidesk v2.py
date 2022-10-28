# -*- coding: utf-8 -*-
#!/usr/bin/env python
#

import requests
import json 
from datetime import datetime, timedelta
import pandas as pd
import csv

### declara as variaveis
now = datetime.now().strftime("%H")
titulo = datetime.now().strftime("%Y%m%d_%H%M")
arqsaida= r'fouad-{}.csv'.format(titulo)
arqsaida1=r'horas-{}.csv'.format(titulo)
arqentrada = 'fouad.json'

### Repete a requisição para cada dia do mês, pois tem um limite de linhas na api
query = []
for i in range(1,32):
    dia=(f'{i:02}')
    print(dia)
    mes='03'
    ano='2021'
    datefull = str(ano) + '-' + str(mes) + '-' + str(dia)

    query.append("""https://api.movidesk.com/public/v1/tickets/?token=\
    &$select=id,subject,createdDate&$filter=createdDate ge """ + datefull + """T00:00:00.00z and createdDate le """ + datefull + """T23:59:59.99z\
    &$expand=clients($select=id, businessName),clients($expand=organization($select=id, businessName)),owner,actions($select=origin,id),\
    actions($expand=timeAppointments($expand=createdBy))""")

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

### Para Testes
# tickets = json.loads(requests.get("https://api.movidesk.com/public/v1/tickets?token=&$select=id,subject,createdDate&$filter=createdDate ge 2021-03-01T00:00:00.00z and createdDate le 2021-03-31T00:00:00.00z&$expand=clients($select=id, businessName),clients($expand=organization($select=id, businessName)),owner,actions($select=origin,id),actions($expand=timeAppointments($expand=createdBy))&$top=100").text)

### Fim das requisições

### Prepara os dados para saida csv
table = []
for i, t in enumerate(tickets):
    if t['owner'] == None:
        pass
    clients = []
    for client in t['clients']:
        if(client['organization'] == None):
            clients.append([client['id'], client['businessName']])
        else:
            clients.append([client['organization']['id'], client['organization']['businessName']])
    workTime = timedelta()
    for action in t['actions']:
        if not action['timeAppointments']:
            pass
        else:
            for time in action['timeAppointments']:
                date_text = time['workTime']
                x = date_text.split(":")
                hours = timedelta(hours=int(x[0]), minutes=int(x[1]), seconds=int(x[2]))
                workTime+=hours
    if t['owner'] == None:
        pass
        # table.append([t['createdDate'], t['subject'], t['id'], 'Nulo', clients, workTime])
    else:
        table.append([datetime.strptime(t['createdDate'][:10], '%Y-%m-%d'), t['subject'], t['id'], t['owner']['businessName'], clients, workTime])

table_out = []
for e in table:
    workTime = e[5]
    if not table_out:
        table_out.append([e[0].strftime('%d/%m/%Y'), e[3], e[4], 1, workTime])
    else:
        #verifica se o cliente está na tabela de saida, se sim vai contar mais 1 registro e somar o workTime
        iterou = False
        for i, el in enumerate(table_out):
            if e[4][0] == el[2][0]:
                table_out[i][3]+=1
                table_out[i][4]+=workTime
                iterou = True
        if not iterou:
            table_out.append([e[0].strftime('%d/%m/%Y'), e[3], e[4], 1, workTime])

for x in table:
    days = x[5].days
    seconds = x[5].seconds
    hours = (seconds//3600) + days*24
    minutes = (seconds//60)%60
    x[5] = str(hours)+':'+str(minutes)
for y in table_out:
    days = y[4].days
    seconds = y[4].seconds
    hours = (seconds//3600) + days*24
    minutes = (seconds//60)%60
    y[4] = str(hours)+':'+str(minutes)


with open(arqsaida1, 'w') as f:
    table_out.insert(0, ["data","criador do ticket","clientes","qtde de tickets","tempo trabalhado"])
    pd.DataFrame(table_out).to_csv(arqsaida1, index=None, header=None, sep=';',encoding='utf-8')


print('break')

with open(arqsaida, 'w') as f:
    pd.DataFrame(table).to_csv(arqsaida, index=None, header=None, sep=';')