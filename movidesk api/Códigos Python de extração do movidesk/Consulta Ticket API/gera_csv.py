import pandas as pd
import urllib3
import json 
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import numpy as np

from time import time


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
        query = """https://api.movidesk.com/public/v1/tickets?token=&$select=id,subject,serviceFirstLevel, slaAgreement, slaAgreementRule, slaSolutionTime, slaResponseTime, slaSolutionChangedByUser, slaSolutionDate, slaSolutionDateIsPaused, slaResponseDate, slaRealResponseDate, createdDate,actionCount,category,justification,ownerTeam,createdBy,status,urgency&$expand=clients($select=id,businessName,personType,profileType),createdBy,owner,clients($expand=organization($select=id,businessName)),slaSolutionChangedBy($select=id,businessName,email,phone,personType,profileType),actions($select=origin,id,createdDate,description,createdBy,status,justification),actions($expand=timeAppointments($expand=createdBy))&$filter=actions/any(a:a/timeAppointments/any(t:t/date ge """ + datefull + """T00:00:00.00z and t/date le """ + datefull + """T23:59:59.00z))"""
        ##resposta = requests.get(query)
        http = urllib3.PoolManager()
        resposta = http.request('GET', query)
        tickets = None
        if resposta.status == 200:
            tickets = json.loads(resposta.data.decode('utf-8'))
            # if tickets != [] and tickets != None:
            #     with open(f"{datefull}.json", "w") as f:
            #         f.write(json.dumps(tickets))
            
        return tickets

def generate_json(initial_date_request, final_date_request, url_json):
    initial_date_request = initial_date_request
    final_date_request = final_date_request

    date_to_request = initial_date_request
    tickets_json = []
    while date_to_request <= final_date_request:
        end_of_month = (date_to_request + relativedelta(months=1) - timedelta(days=1))
        if end_of_month > final_date_request:
            end_of_month = final_date_request
        print(f"date_to_request {date_to_request} - end_of_month {end_of_month}")
        while date_to_request <= end_of_month:
            result_request = Request(date_to_request).request_tickets()
            if result_request is not None and result_request != []:
                for item in result_request:
                    tickets_json.append(item)
            date_to_request = date_to_request + timedelta(days=1)
        
        date_to_request = end_of_month + timedelta(days=1)
        
    with open(url_json, "w") as f:
        f.write(json.dumps(tickets_json))

def convert_json_to_csv(url_json, url_csv):
    with open(url_json, 'r') as f:
        json_to_convert = json.load(f)
        tickets = Tickets(json_to_convert)
        print(tickets.get())
        dataframe = pd.DataFrame(tickets.get(), columns=Ticket.column)
        dataframe = dataframe.drop_duplicates(subset=["ticket_id", "action_id", "time_appointment_id"], keep="last")
        pd.DataFrame(dataframe).to_csv(url_csv, index=False, header=dataframe.columns, sep=';', encoding="utf-8")


def main():

    inicio = time()
    
    initial_date = datetime(2021, 10, 1)
    final_date = datetime(2021, 10, 31)
    url_json = "tickets_outubro2021.json"
    url_csv = "tickets_outubro2021.csv"
    generate_json(initial_date_request=initial_date, final_date_request=final_date, url_json=url_json)
    convert_json_to_csv(url_json=url_json, url_csv=url_csv)

    fim = time()
    print(fim - inicio)
    

if __name__ == "__main__":
    main()