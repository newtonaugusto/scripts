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

    

    query.append("""https://api.movidesk.com/public/v1/tickets?token=\
    &$select=id,subject,createdDate&$expand=clients($select=id,businessName),clients($expand=organization($select=id,businessName)),\
    owner,actions($select=origin,id,createdDate),actions($expand=timeAppointments($expand=createdBy))\
    &$filter=actions/any(a:a/timeAppointments/any(t:t/date ge """ + datefull + """T00:00:00.00z and t/date le """ + datefull + """T23:59:59.00z))""")

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
# tickets = json.loads(requests.get("https://api.movidesk.com/public/v1/tickets?token=&$select=id,subject,createdDate&$expand=clients($select=id,businessName),clients($expand=organization($select=id,businessName)),owner,actions($select=origin,id, createdDate),actions($expand=timeAppointments($expand=createdBy))&$filter=actions/any(a:a/timeAppointments/any(t:t/date ge 2021-03-01 and t/date le 2021-03-31))&$top=100").text)
# Teste, gerando json
print('início')
# def escrever_json(lista):
#     with open('tickets_mar.json', 'w') as f:
#         json.dump(lista, f)

# escrever_json(tickets)

### Fim das requisições
initial_date = datetime.strptime("01-03-2021", '%d-%m-%Y')
final_date = datetime.strptime("31-03-2021", '%d-%m-%Y')
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
        current_date = datetime.strptime(action['createdDate'][:10], '%Y-%m-%d')
        if not (current_date >= initial_date and current_date <= final_date):
            pass
        else:
            if not action['timeAppointments']:
                pass
            else:
                workTime = timedelta()                    
                for time in action['timeAppointments']:
                    if not (time['workTime'] == '00:00:00'):
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
                    if not t['owner']:
                        owner = "-"
                    else:
                        owner = t['owner']['businessName']
                    table.append([action['createdDate'][:10], t['subject'], t['id'], owner, clients, workTime, action['id']])

table_out = []
for e in table:
    workTime = e[5]
    if not table_out:
        table_out.append([e[0], e[3], e[4], 1, workTime])
    else:
        #verifica se o cliente está na tabela de saida, se sim vai contar mais 1 registro e somar o workTime
        iterou = False
        for i, el in enumerate(table_out):
            if e[4][0] == el[2][0]:
                table_out[i][3]+=1
                table_out[i][4]+=workTime
                iterou = True
                pass
        if not iterou:
            table_out.append([e[0], e[3], e[4], 1, workTime])

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
        
        


    # for cont, i in enumerate(x[0]):
    #     if(type(i) == str):
    #         print(i)
    #     else:
    #         x[0][cont] = i.strftime('%d-%m-%Y')
        
for y in table_out:
    days = y[4].days
    seconds = y[4].seconds
    hours = (seconds//3600) + days*24
    minutes = (seconds//60)%60
    y[4] = str(f'{hours:02}')+':'+str(f'{minutes:02}')
    for cont, c in enumerate(y[2]):
        aux = ""
        aux = str(c[1]).replace("'","")
        if(cont == 0):
            clients = aux
        else:
            if aux in clients:
                clients = clients + ',' + aux
    y[2] = clients
    del y[0]
    del y[0]


with open(arqsaida1, 'w') as f:
    # table_out.insert(0, ["data do ticket pai","criador do ticket","clientes","qtde de actions","tempo trabalhado"])
    table_out.insert(0, ["clientes","qtde de actions","tempo trabalhado"])
    pd.DataFrame(table_out).to_csv(arqsaida1, index=None, header=None, sep=';',encoding='utf-8')


# [date_register, t['subject'], t['id'], t['owner']['businessName'], clients, workTime]
with open(arqsaida, 'w') as f:
    table.insert(0, ["data do ticket pai","assunto do ticket","id do ticket","owner criador", "clientes","tempo trabalhado","action id"])
    pd.DataFrame(table).to_csv(arqsaida, index=None, header=None, sep=';')

print('fim')