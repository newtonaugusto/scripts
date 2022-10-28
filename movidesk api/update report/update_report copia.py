import pandas as pd
import requests
import json 
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import numpy as np
import io
import boto3
import botocore
import boto3.session

from time import sleep


# Classe que descreve o formato dos tickets vindos da requisição
class Tickets:
    def __init__(self, objs):
        self.obj_list = [Ticket(**item) for item in objs]
        
    @classmethod
    def obj_list(self):
        return self.__tickets

    def get(self):
        all_lines = []
        [all_lines.extend(item.get()) for item in self.obj_list]
        return all_lines       

class Ticket:
    class Action:
        class TimeAppointment:
            class CreatedBy(object):

                column = ("email", )
                def __init__(self, email, *args, **kwargs):
                    self.email = email
                
                def __str__(self):
                    return self.email

                def __repr__(self):
                    return self.__str__()

            column = ("time_appointment_id", "activity", "periodStart", "periodEnd", "workTime", "workTypeName", *CreatedBy.column)
            def __init__(self, id, activity, date, periodStart, periodEnd, workTime, workTypeName, createdBy, *args, **kwargs):
                self.id = id
                self.activity = activity
                self.date = datetime.strptime(date, "%Y-%m-%dT00:00:00")
                if periodStart is not None:
                    self.periodStart = datetime.strptime(f"{self.date.date()} {periodStart}", "%Y-%m-%d %H:%M:%S")
                    self.periodEnd = datetime.strptime(f"{self.date.date()} {periodEnd}", "%Y-%m-%d %H:%M:%S")
                else: 
                    work_time_list = workTime.split(":")
                    self.periodStart = self.date + timedelta(hours=8)
                    self.periodEnd = self.periodStart + timedelta(hours=int(work_time_list[0]), minutes=int(work_time_list[1]), seconds=int(work_time_list[2]))

                self.workTime = workTime
                self.workTypeName = workTypeName
                self.createdBy = self.CreatedBy(**createdBy)

            def get(self):
                return self.id, self.activity, self.periodStart, self.periodEnd, self.workTime, self.workTypeName, self.createdBy.email
            
        column = ("action_id", "justification", "status", *TimeAppointment.column)       
        def __init__(self, id, justification, status, timeAppointments, *args, **kwargs):
            self.id = id
            self.justification = justification
            self.status = status

            self.timeAppointments = [self.TimeAppointment(**item) for item in timeAppointments if item != [] or item is not None]

        def __str__(self):
            return f"{self.id} {self.justification} {self.status}"

        def __repr__(self):
            return self.__str__()

        def get(self):
            return [(self.id, self.justification, self.status, *item.get(), ) for item in self.timeAppointments]

    class Client:
        column = ("business_name", )
        class Organization:
            def __init__(self, id, businessName):
                self.businessName = businessName
                self.id = id

        def __init__(self, id, businessName, organization, *args, **kwargs):
            self.id = id
            self.organization = self.Organization(**organization) if organization is not None else None
            self.client_name = businessName if self.organization is not None else None
            self.business_name  = self.organization.businessName if self.client_name is not None else businessName

        def __str__(self):
            return f"Cliente {self.client_name} - {self.business_name} ||"

        def __repr__(self):
            return self.__str__()

        def get(self):
            return self.business_name

    column = ("ticket_id", "urgency", "status", "ownerTeam", "category", "subject", "createdDate", *Client.column, *Action.column)

    def __init__(self, id, urgency, status, ownerTeam, category, subject, createdDate, actions, clients, *args, **kwargs):
        self.id = id
        self.urgency = urgency
        self.status = status
        self.ownerTeam = ownerTeam
        self.category = category
        self.subject = subject
        self.createdDate = datetime.strptime(createdDate.split(".")[0], "%Y-%m-%dT%H:%M:%S")

        self.actions = [self.Action(**item) for item in actions]
        self.clients = [self.Client(**item) for item in clients]

        if len(self.clients) > 1:
            keys = list(dict.fromkeys([item.business_name for item in self.clients]))
            if len(keys) > 1:
                if all(x in keys for x in ["Infomach", "Infomach - Comercial"]) and len(keys) == 2:
                    keys.remove("Infomach - Comercial")
                else:
                    if "Infomach" in keys:
                        keys.remove("Infomach")
                    if "Infomach - Comercial" in keys:
                        keys.remove("Infomach - Comercial")
            clients_filtered = []
            for item in self.clients:
                if item.business_name in keys:
                    clients_filtered.append(item)
                    keys.remove(item.business_name)

            self.clients = clients_filtered

    def __str__(self):
        return f"{self.id}"

    def __repr__(self):
        return self.__str__()
    
    def get(self):
        all_lines = []
        [[[all_lines.append((self.id, self.urgency, self.status, self.ownerTeam, self.category, self.subject, self.createdDate, client.get(), *item,)) for item in action.get()] for action in self.actions] for client in self.clients]

        return all_lines

class Request:
    def __init__(self, date_to_request):
        self.date_to_request = date_to_request

    ### Função que faz a requisição e retorna os tickets da API do Movidesk
    def request_tickets(self):
        ### Repete a requisição para cada dia do mês, pois tem um limite de linhas na api
        datefull =  f'{self.date_to_request.year}-{self.date_to_request.month:02}-{self.date_to_request.day:02}'
        print(datefull)
        query = """https://api.movidesk.com/public/v1/tickets?token=&$select=id,subject,serviceFirstLevel,createdDate,actionCount,category,justification,ownerTeam,createdBy,status,urgency&$expand=clients($select=id,businessName,personType,profileType),createdBy,owner,clients($expand=organization($select=id,businessName)),actions($select=origin,id,createdDate,description,createdBy,status,justification),actions($expand=timeAppointments($expand=createdBy))&$filter=actions/any(a:a/timeAppointments/any(t:t/date ge """ + datefull + """T00:00:00.00z and t/date le """ + datefull + """T23:59:59.00z))"""
        resposta = requests.get(query)
        tickets = None
        if resposta.status_code == 200:
            tickets = json.loads(resposta.text)
        return tickets

def alert_error_sns(client, text, is_failed):
    # Se der erro manda publica mensagem no SNS
    if is_failed:
        response = client.publish(
            TopicArn="arn:aws:sns:us-east-1:900397181019:movidash-sns",
            Message=text,
            Subject='Erro de atualização',
        )
    else:
        response = client.publish(
            TopicArn="arn:aws:sns:us-east-1:900397181019:movidash-sns",
            Message=text,
            Subject='Sucesso na atualização.',
        )

def lambda_handler(event, context): 
    # Inicia sessão na aws
    aws_access_key_id = ""
    aws_secret_access_key = ""
    aws_region = "us-east-1"   
    s3 = boto3.client('s3',
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=aws_region)
    s3.download_file('streamlitmovidesk', 'relatorio.csv', 'relatorio.csv')

    sns = boto3.client('sns',
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=aws_region) 

    # Caminho do relatório a ser atualizado
    URL = r"relatorio.csv"
    cont_attempts = 0
    while True:
        cont_attempts += 1
        try:
            update_report(s3, URL)
            is_failed = False
            break
        except:
            is_failed = True
            sleep(5)
        if cont_attempts > 5:
            break
    
    if is_failed:
        alert_error_sns(sns, f"Erro ao dar load no relatorio do Movidash. Dia de referencia: {datetime.today() - timedelta(days=1)}", is_failed)
    else:
        alert_error_sns(sns, f"Sucesso na atualização do relatório.. Dia de referencia: {datetime.today() - timedelta(days=1)}", is_failed)
    return 0

def update_report(s3, URL):

    dayli_buffer = io.BytesIO()
    date_request = datetime.today() - timedelta(days=1)
    dayli_buffer.write(json.dumps(Request(date_request).request_tickets()).encode())
    dayli_buffer.seek(0)
    arquivo = json.load(dayli_buffer)
    dayli_buffer.close()
    tickets = Tickets(arquivo)
    dataframe = pd.DataFrame(tickets.get(), columns=Ticket.column)
    dayli_buffer = io.BytesIO()  
    pd.DataFrame(dataframe).to_csv(dayli_buffer, index=False, header=dataframe.columns, sep=';', encoding="utf-8")
    dayli_buffer.seek(0)
    with open(URL, 'r'):
        df1 = pd.read_csv(URL, delimiter=";")

    df2 = pd.read_csv(dayli_buffer, delimiter=";")
    dayli_buffer.close()
    df = pd.concat([df1, df2], ignore_index=True)
    df = df.drop_duplicates(subset=["ticket_id", "action_id", "time_appointment_id"], keep="last")
    csv_buffer=io.StringIO()
    df.to_csv(csv_buffer, index=False, header=df.columns, sep=';', encoding="utf-8")
    content = csv_buffer.getvalue()
    csv_buffer.close()
    s3.put_object(Bucket='streamlitmovidesk', Body=content, Key=URL)

lambda_handler(context="", event="")