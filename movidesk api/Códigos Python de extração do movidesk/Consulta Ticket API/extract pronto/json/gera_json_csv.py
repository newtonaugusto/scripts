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
    def __init__(self, month, year):
        self.initial_date = datetime(year=year,month=month, day=1)
        self.final_date = self.initial_date + relativedelta(months=+1) - timedelta(days=1)
        if self.final_date > datetime.today():
            self.final_date = datetime.today()

    ### Função que faz a requisição e retorna os tickets da API do Movidesk
    def request_tickets(self):
        ### Repete a requisição para cada dia do mês, pois tem um limite de linhas na api
        query = []
        for i in range(1, self.final_date.day + 1):
            datefull = f'{self.initial_date.year}-{self.initial_date.month:02}-{i:02}'
            print (datefull)
            query.append("""https://api.movidesk.com/public/v1/tickets?token=&$select=id,subject,serviceFirstLevel,slaAgreement,slaAgreementRule,slaSolutionTime,slaResponseTime,slaSolutionChangedByUser,slaSolutionDate,slaSolutionDateIsPaused,slaResponseDate,slaRealResponseDate,createdDate,actionCount,category,justification,ownerTeam,createdBy,status,urgency&$expand=clients($select=id,businessName,personType,profileType),createdBy,owner,clients($expand=organization($select=id,businessName)),slaSolutionChangedBy($select=id,businessName,email,phone,personType,profileType),actions($select=origin,id,createdDate,description,createdBy,status,justification),actions($expand=timeAppointments($expand=createdBy))&$filter=actions/any(a:a/timeAppointments/any(t:t/date ge """ + datefull + """T00:00:00.00z and t/date le """ + datefull + """T23:59:59.00z))""")

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

initial_date = datetime(year=2020,month=6, day=1)
final_date = datetime(year=2021,month=9, day=28)
date_to_request = initial_date

while date_to_request < final_date:
    # tickets = Request(date_to_request.month, date_to_request.year).request_tickets()
    # with open(f'{date_to_request.month} - {date_to_request.year}.json', 'w') as f:
    #     json.dump(tickets, f)
    with open(f'{date_to_request.month} - {date_to_request.year}.json', 'r', encoding="utf8") as f:
        json_to_convert = json.load(f)
        tickets = Tickets(json_to_convert)
        dataframe = pd.DataFrame(tickets.get(), columns=Ticket.column)
        dataframe = dataframe.drop_duplicates(subset=["ticket_id", "action_id", "time_appointment_id"], keep="last")
        if date_to_request.month == 6 and date_to_request.year == 2020:
            pd.DataFrame(dataframe).to_csv(f'{date_to_request.month} - {date_to_request.year}.csv', index=False, header=dataframe.columns, sep=';', encoding="utf-8")
        else:
            pd.DataFrame(dataframe).to_csv(f'{date_to_request.month} - {date_to_request.year}.csv', index=False, header=False, sep=';', encoding="utf-8")


    date_to_request = date_to_request + relativedelta(months=1)
