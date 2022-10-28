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

    column = ("ticket_id", "urgency", "status", "ownerTeam", "subject", "createdDate", *Client.column, *Action.column)

    def __init__(self, id, urgency, status, ownerTeam, subject, createdDate, actions, clients, *args, **kwargs):
        self.id = id
        self.urgency = urgency
        self.status = status
        self.ownerTeam = ownerTeam
        self.subject = subject
        self.createdDate = datetime.strptime(createdDate.split(".")[0], "%Y-%m-%dT%H:%M:%S")

        self.actions = [self.Action(**item) for item in actions]

        self.clients = [self.Client(**item) for item in clients]

        if len(self.clients) > 1:
            self.clients = list(filter(lambda item: item.business_name != "Infomach", self.clients ))

    def __str__(self):
        return f"{self.id}"

    def __repr__(self):
        return self.__str__()
    
    def get(self):
        all_lines = []
        [[[all_lines.append((self.id, self.urgency, self.status, self.ownerTeam, self.subject, self.createdDate, *client.get(), *item,)) for item in action.get()] for action in self.actions] for client in self.clients]

        return all_lines


if __name__ == "__main__":
    with open("4 - 2021.json", "rb") as file:

        arquivo = json.load(file)
        tickets = Tickets(arquivo)

        dataframe = pd.DataFrame(tickets.get(), columns=Ticket.column)
        now = datetime.now()

        last_7_days = now - timedelta(days=30)
        teste = dataframe.loc[
            (dataframe['periodEnd'] > last_7_days) & 
            (dataframe['ownerTeam'] == "Cloud & Desenvolvimento")]

        print(last_7_days)
        print(teste)

        

