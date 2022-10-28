############################
# Create by : Newton Miotto# 
############################


import pandas as pd
import urllib3
import json 
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import numpy as np
import io
import os
import boto3
import botocore
import boto3.session
from codeguru_profiler_agent import with_lambda_profiler


from time import sleep


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

                column = ("create_by_email", "create_by_name")
                def __init__(self, email, businessName, *args, **kwargs):
                    self.email = email
                    self.name = businessName
                
                def __str__(self):
                    return self.email, self.name

                def __repr__(self):
                    return self.__str__()

            column = ("time_appointment_id", "activity", "periodStart", "periodEnd", "workTime", "workTypeName", *CreatedBy.column)
            def __init__(self, id, activity, date, periodStart, periodEnd, workTime, workTypeName, createdBy, *args, **kwargs):
                self.id = id
                self.activity = activity
                self.date = datetime.strptime(date, "%Y-%m-%dT00:00:00")
                if periodStart is not None:
                    period_start = datetime.strptime(f"{self.date.date()} {periodStart}", "%Y-%m-%d %H:%M:%S")
                    period_end = datetime.strptime(f"{self.date.date()} {periodEnd}", "%Y-%m-%d %H:%M:%S")
                    if period_start.year == 2001:
                        period_start = period_start.replace(year = 2021)
                    if period_end.year == 2001:
                        period_end = period_end.replace(year = 2021)
                    self.periodStart = period_start
                    self.periodEnd = period_end
                else: 
                    work_time_list = workTime.split(":")
                    self.period_start = self.date + timedelta(hours=8)
                    self.period_end = self.period_start + timedelta(hours=int(work_time_list[0]), minutes=int(work_time_list[1]), seconds=int(work_time_list[2]))

                self.workTime = workTime
                self.workTypeName = workTypeName
                self.createdBy = self.CreatedBy(**createdBy)

            def get(self):
                return self.id, self.activity, self.periodStart, self.periodEnd, self.workTime, self.workTypeName, self.createdBy.email, self.createdBy.name
            
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
    
    class SlaSolutionChangedBy:
        column = ("sla_id", "sla_business_name", "sla_email", "sla_phone", "sla_person_type", "sla_profile_type",) 
        def __init__(self, id, businessName, email, phone, personType, profileType, *args, **kwargs):
            self.id = id
            self.business_name = businessName
            self.email = email
            self.phone = phone
            self.person_type = personType
            self.profile_type = profileType
            
        def __str__(self):
            return f"{self.sla_solution_changed_by_business_name}"

        def __repr__(self):
            return self.__str__()

        def get(self):
            return (self.sla_solution_changed_by_id, self.sla_solution_changed_by_business_name, 
            self.sla_solution_changed_by_email, self.sla_solution_changed_by_phone, 
            self.sla_solution_changed_by_person_type, self.sla_solution_changed_by_profile_type)

    class Owner:
        column = ("owner_name",) 
        def __init__(self, businessName, *args, **kwargs):
            self.owner_name = businessName

        def __str__(self):
            return f"{self.owner_name}"

        def __repr__(self):
            return self.__str__()

        def get(self):
            return self.owner_name

    class CreatedBy:
        column = ("created_by_name",) 
        def __init__(self, businessName, *args, **kwargs):
            self.created_by_name = businessName

        def __str__(self):
            return f"{self.created_by_name}"

        def __repr__(self):
            return self.__str__()

        def get(self):
            return self.created_by_name

    class Client:
        column = ("client_id", "business_name", )
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
            return (self.id, self.business_name)

    column = ("ticket_id", "urgency", "status", "owner_team", "category", "subject", "created_date", "service_first_level", "sla_agreement", "sla_agreement_rule", "sla_solution_time", "sla_response_time", "sla_solution_changed_by_user", "sla_solution_date", "sla_solution_date_is_paused", "sla_response_date", "sla_real_response_date", *Client.column, *SlaSolutionChangedBy.column, *Action.column, *Owner.column, *CreatedBy.column)

    def __init__(self, id, urgency, status, ownerTeam, category, subject, createdDate, serviceFirstLevel, slaAgreement, slaAgreementRule, slaSolutionTime, slaResponseTime, slaSolutionChangedByUser, slaSolutionDate, slaSolutionDateIsPaused, slaResponseDate, slaRealResponseDate, actions, slaSolutionChangedBy, clients, owner, createdBy, *args, **kwargs):
        self.id = id
        self.urgency = urgency
        self.status = status
        self.ownerTeam = ownerTeam
        self.category = category
        self.subject = subject
        self.createdDate = datetime.strptime(createdDate.split(".")[0], "%Y-%m-%dT%H:%M:%S")
        self.service_first_level = serviceFirstLevel
        self.sla_agreement = slaAgreement
        self.sla_agreement_rule = slaAgreementRule
        self.sla_solution_time = slaSolutionTime
        self.sla_response_time = slaResponseTime
        self.sla_solution_changed_by_user = slaSolutionChangedByUser
        self.sla_solution_date = slaSolutionDate
        self.sla_solution_date_is_paused = slaSolutionDateIsPaused
        self.sla_response_date = slaResponseDate
        self.sla_real_response_date = slaRealResponseDate
        self.actions = [self.Action(**item) for item in actions]
        self.clients = [self.Client(**item) for item in clients]
        
        if slaSolutionChangedBy is not None and slaSolutionChangedBy != []:
            self.sla_solution_changed_by = self.SlaSolutionChangedBy(**slaSolutionChangedBy) 
            self.sla_id = self.sla_solution_changed_by.id
            self.sla_business_name = self.sla_solution_changed_by.business_name
            self.sla_email = self.sla_solution_changed_by.email
            self.sla_phone = self.sla_solution_changed_by.phone
            self.sla_person_type = self.sla_solution_changed_by.person_type
            self.sla_profile_type = self.sla_solution_changed_by.profile_type
        else:
            self.sla_id = None
            self.sla_business_name = None
            self.sla_email = None
            self.sla_phone = None
            self.sla_person_type = None
            self.sla_profile_type = None

        if owner is not None and owner != []:
            self.owner = self.Owner(**owner) 
        else:
            self.owner = None

        if createdBy is not None and owner != []:
            self.created_by = self.CreatedBy(**createdBy)
        else:
            self.created_by = None

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
        [[[all_lines.append((self.id, self.urgency, self.status, self.ownerTeam, self.category, 
        self.subject, self.createdDate, self.service_first_level, self.sla_agreement, 
        self.sla_agreement_rule, self.sla_solution_time, self.sla_response_time, 
        self.sla_solution_changed_by_user, self.sla_solution_date, 
        self.sla_solution_date_is_paused, self.sla_response_date, self.sla_real_response_date, 
        *client.get(), self.sla_id, self.sla_business_name, self.sla_email, self.sla_phone, self.sla_person_type, self.sla_profile_type, *item, self.owner, self.created_by)) for item in action.get()] for action in self.actions] for client in self.clients]

        return all_lines

class Request:
    def __init__(self, date_to_request):
        self.date_to_request = date_to_request

    ### Função que faz a requisição e retorna os tickets da API do Movidesk
    def request_tickets(self):
        ### Repete a requisição para cada dia do mês, pois tem um limite de linhas na api
        datefull =  f'{self.date_to_request.year}-{self.date_to_request.month:02}-{self.date_to_request.day:02}'
        print(datefull)
        query = """https://api.movidesk.com/public/v1/tickets?token=&$select=id,subject,serviceFirstLevel,slaAgreement,slaAgreementRule,slaSolutionTime,slaResponseTime,slaSolutionChangedByUser,slaSolutionDate,slaSolutionDateIsPaused,slaResponseDate,slaRealResponseDate,createdDate,actionCount,category,justification,ownerTeam,createdBy,status,urgency&$expand=clients($select=id,businessName,personType,profileType),createdBy,owner,clients($expand=organization($select=id,businessName)),slaSolutionChangedBy($select=id,businessName,email,phone,personType,profileType),actions($select=origin,id,createdDate,description,createdBy,status,justification),actions($expand=timeAppointments($expand=createdBy))&$filter=actions/any(a:a/timeAppointments/any(t:t/date ge """ + datefull + """T00:00:00.00z and t/date le """ + datefull + """T23:59:59.00z))"""
        ##resposta = requests.get(query)
        http = urllib3.PoolManager()
        resposta = http.request('GET', query)
        tickets = None
        if resposta.status == 200:
            tickets = json.loads(resposta.data.decode('utf-8'))
           
        return tickets

def alert_error_sns(client, text, is_failed):
    # Se der erro manda publica mensagem no SNS
    if is_failed:
        response = client.publish(
            TopicArn="arn:aws:sns:us-east-2:686836150544:dados-movidesk-topic",
            Message=text,
            Subject='Erro de atualização',
        )
    else:
        response = client.publish(
            TopicArn="arn:aws:sns:us-east-2:686836150544:dados-movidesk-topic",
            Message=text,
            Subject='Sucesso na atualização.',
        )
        
@with_lambda_profiler(profiling_group_name="aws-lambda-dados-movidesk")
def lambda_handler(event, context): 
    # Inicia sessão na aws
    # aws_secret_access_key = os.environ['SECRET']
    # aws_access_key_id = os.environ['ACCESS']
    buffer_report = io.BytesIO()
    aws_region = "us-east-2"   
    s3 = boto3.client('s3', region_name=aws_region)
  #       aws_access_key_id=aws_access_key_id,
  #      aws_secret_access_key=aws_secret_access_key,
      
    s3.download_fileobj('dados.datalake.movidesk', 'ticket-api/relatorio.csv', buffer_report)
    # s3.download_file('streamlitmovidesk', 'relatorio.csv', r'\tmp\relatorio.csv')

    sns = boto3.client('sns',   region_name=aws_region) 
     #   aws_access_key_id=aws_access_key_id,
     #  aws_secret_access_key=aws_secret_access_key,
      

    # Caminho do relatório a ser atualizado
    cont_attempts = 0
    is_failed = False
    while True:
        cont_attempts += 1
        try:
            buffer_report.seek(0)
            update_report(s3, buffer_report)
            break
        except:
            if cont_attempts > 5:
                is_failed = True
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
    df1 = pd.read_csv(URL, delimiter=";")
    
    df2 = pd.read_csv(dayli_buffer, delimiter=";")
    dayli_buffer.close()
    df = pd.concat([df1, df2], ignore_index=True)
    df = df.drop_duplicates(subset=["ticket_id", "action_id", "time_appointment_id"], keep="last")
    csv_buffer=io.StringIO()
    df.to_csv(csv_buffer, index=False, header=df.columns, sep=';', encoding="utf-8")
    content = csv_buffer.getvalue()
    csv_buffer.close()
    s3.put_object(Bucket='dados.datalake.movidesk', Body=content, Key="ticket-api/relatorio.csv")

# lambda_handler(event="", context="")
#  123
