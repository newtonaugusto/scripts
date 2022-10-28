import requests
import json 
import pandas as pd
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta

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
    def __init__(self, month, year):
        self.initial_date = datetime(year=year,month=month, day=1)
        self.final_date = self.initial_date + relativedelta(months=+1) - timedelta(days=1)
        if self.final_date < datetime.today():
            self.final_date = date_to_request.today()

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

initial_date = datetime(year=2021,month=9, day=1)
final_date = datetime(year=2021,month=9, day=8)
date_to_request = initial_date

while date_to_request < final_date:
    tickets = Request(date_to_request.month, date_to_request.year).request_tickets()
    with open(f'{date_to_request.month} - {date_to_request.year}.json', 'w') as f:
        json.dump(tickets, f)
    with open(f'{date_to_request.month} - {date_to_request.year}.json', 'r') as f:
        json_to_convert = json.load(f)
        tickets = Tickets(json_to_convert)
        dataframe = pd.DataFrame(tickets.get(), columns=Ticket.column)
        dataframe = dataframe.drop_duplicates(subset=["ticket_id", "action_id", "time_appointment_id"], keep="last")
        pd.DataFrame(dataframe).to_csv(f'{date_to_request.month} - {date_to_request.year}.csv', index=False, header=dataframe.columns, sep=';', encoding="utf-8")


    date_to_request = date_to_request + relativedelta(months=1)
