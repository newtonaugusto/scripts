import json
import time
from datetime import datetime, timedelta
import numpy as np
import pandas as pd

class Tickets:
    def __init__(self, objs):
        self.obj_list = [Ticket(**item) for item in objs]
        print(Ticket.column)
        
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
        column = ("client_name", "business_name", )
        # column = ("business_name", )
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
            return self.client_name, self.business_name

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
        [[[all_lines.append((self.id, self.urgency, self.status, self.ownerTeam, self.category, self.subject, self.createdDate, *client.get(), *item,)) for item in action.get()] for action in self.actions] for client in self.clients]

        return all_lines


if __name__ == "__main__":
    with open("062020-062021-tickets.json", "rb") as file:
        arquivo = json.load(file)
        # with open('5e6-2021-tickets.json', 'rb') as file2:
        #     arquivo2 = json.load(file2)
        #     with open('4e5-2021-tickets.json', 'rb') as file3:
        #         arquivo3 = json.load(file3)
        tickets = Tickets(arquivo)
        concat_json_tickets = tickets.get()
        # concat_json_tickets.extend(Tickets(arquivo2).get())
        # concat_json_tickets.extend(Tickets(arquivo3).get())
        # columns = ["ticket_id", "urgency", "status", "ownerTeam", "subject", "createdDate", "client_name", "business_name","action_id", "justification", "status","time_appointment_id", "activity", "periodStart", "periodEnd", "workTime", "workTypeName","email"]
        dataframe = pd.DataFrame(concat_json_tickets, columns=Ticket.column)
        # print(len(np.unique(dataframe[["ticket_id", "action_id", "time_appointment_id"]].values, axis=0)))
        with open("relatorio.csv", "wb") as file:
            # print(dataframe.drop_duplicates(subset=["ticket_id", "action_id", "time_appointment_id"], keep="last"))
            dataframe = dataframe.drop_duplicates(subset=["ticket_id", "action_id", "time_appointment_id"], keep="last")
            dataframe = dataframe.drop('client_name', 1)
            pd.DataFrame(dataframe).to_csv('relatorio.csv', index=False, header=dataframe.columns, sep=';', encoding="utf-8")
    
        # dataframe = dataframe.drop(columns=['client_name'])
        # # dataframe = dataframe.drop('client_name')

        
        # dataframe.drop_duplicates(inplace=True)


        # now = datetime.now()
        # with open('relatorio.csv', 'w') as f:
        #     # table.insert(0, ["data da action","assunto do ticket","id do ticket","owner criador", "clientes","tempo trabalhado","action id","urgency","status","ownerTeam", "justification", "category", "actionCount", "status", "description", "activity","solicitante","hora de início", "hora de fim", "tipo de hora", "serviço"])
        #     pd.DataFrame(dataframe).to_csv('relatorio.csv', index=False, header=dataframe.columns, sep=';', encoding="utf-8")   
        # print(dataframe.columns)
        # last_7_days = now - timedelta(days=30)
        # teste = dataframe.loc[
        #     (dataframe['periodEnd'] > last_7_days) & 
        #     (dataframe['ownerTeam'] == "Cloud & Desenvolvimento")]


        

