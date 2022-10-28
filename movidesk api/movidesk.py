# -*- coding: utf-8 -*-
#!/usr/bin/env python
#

import requests
import json 
from datetime import datetime, timedelta
import pandas as pd
import csv
 
#### declara as variaveis
now = datetime.now().strftime("%H")
titulo = datetime.now().strftime("%Y%m%d_%H%M")
arqsaida= r'fouad-{}.csv'.format(titulo)
arqsaida1=r'horas-{}.csv'.format(titulo)
arqentrada = 'fouad.json'

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
    actions($expand=timeAppointments($expand=createdBy))&$top=3""")

res = []
for q in query:
    print("index: {}".format(query.index(q)))
    res.append(requests.get(q))

tick = [] 
for r in res:
    tick.append(json.loads(r.text))

# with open(arqentrada, 'w') as f:
#  json.dump(json.loads(res.text), f, separators=(',', ':'), indent=4)
tickets = []
for t in tick:
    tickets.extend(t)
print(tickets)

#### prepara os dados para saida csv
table = []
for i, t in enumerate(tickets):
    if t['owner'] == None:
        pass
    clients = []
    for client in t['clients']:
        clients.append(client['businessName'])
    workTime = timedelta()
    for action in t['actions']:
        if not action['timeAppointments']:
            pass
        else:
            for time in action['timeAppointments']:
                auxTime = datetime.strptime(time['workTime'],"%H:%M:%S")
                hours = timedelta(hours=auxTime.hour, minutes=auxTime.minute, seconds=auxTime.second)
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

with open(arqsaida1, 'w') as f:
    table_out.insert(0, ["data","criador do ticket","clientes","qtde de tickets","tempo trabalhado"])
    pd.DataFrame(table_out).to_csv(arqsaida1, index=None, header=None, sep=';',encoding='utf-8')


print('break')

with open(arqsaida, 'w') as f:
    pd.DataFrame(table).to_csv(arqsaida, index=None, header=None, sep=';')

#### converte o arquivo json em dataframe e o transforma direto para CSV
# with open(arqsaida, 'w') as f:
#  a = pd.read_json(arqentrada).to_csv(f,index=None,sep=';')




